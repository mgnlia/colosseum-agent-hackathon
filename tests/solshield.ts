import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { Solshield } from "../target/types/solshield";
import { expect } from "chai";
import { Keypair, PublicKey, SystemProgram } from "@solana/web3.js";

describe("solshield", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.Solshield as Program<Solshield>;
  const authority = provider.wallet;
  const agentKeypair = Keypair.generate();
  const userKeypair = Keypair.generate();

  let protocolStatePda: PublicKey;
  let protocolStateBump: number;

  before(async () => {
    // Derive protocol state PDA
    [protocolStatePda, protocolStateBump] = PublicKey.findProgramAddressSync(
      [Buffer.from("protocol-state")],
      program.programId
    );

    // Airdrop SOL to test accounts
    const airdropAgent = await provider.connection.requestAirdrop(
      agentKeypair.publicKey,
      2 * anchor.web3.LAMPORTS_PER_SOL
    );
    await provider.connection.confirmTransaction(airdropAgent);

    const airdropUser = await provider.connection.requestAirdrop(
      userKeypair.publicKey,
      2 * anchor.web3.LAMPORTS_PER_SOL
    );
    await provider.connection.confirmTransaction(airdropUser);
  });

  it("initializes the protocol", async () => {
    const config = {
      agentAuthority: agentKeypair.publicKey,
      defaultWarnThreshold: new anchor.BN(15000), // 1.5x
      defaultCriticalThreshold: new anchor.BN(12000), // 1.2x
      maxPositionsPerUser: 10,
      rebalanceFeeBps: 50, // 0.5%
    };

    await program.methods
      .initialize(config)
      .accounts({
        protocolState: protocolStatePda,
        authority: authority.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .rpc();

    const state = await program.account.protocolState.fetch(protocolStatePda);
    expect(state.authority.toString()).to.equal(authority.publicKey.toString());
    expect(state.agentAuthority.toString()).to.equal(
      agentKeypair.publicKey.toString()
    );
    expect(state.defaultWarnThreshold.toNumber()).to.equal(15000);
    expect(state.defaultCriticalThreshold.toNumber()).to.equal(12000);
    expect(state.totalPositions.toNumber()).to.equal(0);
    expect(state.totalRebalances.toNumber()).to.equal(0);
  });

  it("registers a position for monitoring", async () => {
    const obligationKey = Keypair.generate().publicKey;

    const [positionPda] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("position"),
        userKeypair.publicKey.toBuffer(),
        obligationKey.toBuffer(),
      ],
      program.programId
    );

    await program.methods
      .registerPosition(
        { kamino: {} }, // DeFiProtocol::Kamino
        obligationKey,
        new anchor.BN(15000), // warn threshold
        new anchor.BN(12000) // critical threshold
      )
      .accounts({
        protocolState: protocolStatePda,
        position: positionPda,
        owner: userKeypair.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([userKeypair])
      .rpc();

    const position = await program.account.monitoredPosition.fetch(positionPda);
    expect(position.owner.toString()).to.equal(
      userKeypair.publicKey.toString()
    );
    expect(position.obligationKey.toString()).to.equal(
      obligationKey.toString()
    );
    expect(position.warnThreshold.toNumber()).to.equal(15000);
    expect(position.criticalThreshold.toNumber()).to.equal(12000);
    expect(position.healthFactor.toNumber()).to.equal(0);
    expect(position.rebalanceCount).to.equal(0);

    // Verify protocol state updated
    const state = await program.account.protocolState.fetch(protocolStatePda);
    expect(state.totalPositions.toNumber()).to.equal(1);
  });

  it("updates health factor (agent only)", async () => {
    const obligationKey = Keypair.generate().publicKey;

    const [positionPda] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("position"),
        userKeypair.publicKey.toBuffer(),
        obligationKey.toBuffer(),
      ],
      program.programId
    );

    // First register the position
    await program.methods
      .registerPosition(
        { kamino: {} },
        obligationKey,
        new anchor.BN(15000),
        new anchor.BN(12000)
      )
      .accounts({
        protocolState: protocolStatePda,
        position: positionPda,
        owner: userKeypair.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([userKeypair])
      .rpc();

    // Update health as the agent
    await program.methods
      .updateHealth(
        new anchor.BN(18000), // health factor 1.8x
        new anchor.BN(50000_000000), // $50,000 collateral
        new anchor.BN(20000_000000) // $20,000 debt
      )
      .accounts({
        protocolState: protocolStatePda,
        position: positionPda,
        agent: agentKeypair.publicKey,
      })
      .signers([agentKeypair])
      .rpc();

    const position = await program.account.monitoredPosition.fetch(positionPda);
    expect(position.healthFactor.toNumber()).to.equal(18000);
    expect(position.totalCollateralUsd.toNumber()).to.equal(50000_000000);
    expect(position.totalDebtUsd.toNumber()).to.equal(20000_000000);
  });

  it("rejects health update from non-agent", async () => {
    const obligationKey = Keypair.generate().publicKey;
    const randomSigner = Keypair.generate();

    const airdrop = await provider.connection.requestAirdrop(
      randomSigner.publicKey,
      anchor.web3.LAMPORTS_PER_SOL
    );
    await provider.connection.confirmTransaction(airdrop);

    const [positionPda] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("position"),
        userKeypair.publicKey.toBuffer(),
        obligationKey.toBuffer(),
      ],
      program.programId
    );

    await program.methods
      .registerPosition(
        { marginFi: {} },
        obligationKey,
        new anchor.BN(15000),
        new anchor.BN(12000)
      )
      .accounts({
        protocolState: protocolStatePda,
        position: positionPda,
        owner: userKeypair.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([userKeypair])
      .rpc();

    try {
      await program.methods
        .updateHealth(
          new anchor.BN(10000),
          new anchor.BN(10000_000000),
          new anchor.BN(10000_000000)
        )
        .accounts({
          protocolState: protocolStatePda,
          position: positionPda,
          agent: randomSigner.publicKey,
        })
        .signers([randomSigner])
        .rpc();
      expect.fail("Should have thrown UnauthorizedAgent error");
    } catch (err: any) {
      expect(err.toString()).to.include("UnauthorizedAgent");
    }
  });

  it("pauses and resumes a position", async () => {
    const obligationKey = Keypair.generate().publicKey;

    const [positionPda] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("position"),
        userKeypair.publicKey.toBuffer(),
        obligationKey.toBuffer(),
      ],
      program.programId
    );

    await program.methods
      .registerPosition(
        { solend: {} },
        obligationKey,
        new anchor.BN(15000),
        new anchor.BN(12000)
      )
      .accounts({
        protocolState: protocolStatePda,
        position: positionPda,
        owner: userKeypair.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .signers([userKeypair])
      .rpc();

    // Pause
    await program.methods
      .pausePosition()
      .accounts({
        position: positionPda,
        owner: userKeypair.publicKey,
      })
      .signers([userKeypair])
      .rpc();

    let position = await program.account.monitoredPosition.fetch(positionPda);
    expect(JSON.stringify(position.status)).to.include("paused");

    // Resume
    await program.methods
      .resumePosition()
      .accounts({
        position: positionPda,
        owner: userKeypair.publicKey,
      })
      .signers([userKeypair])
      .rpc();

    position = await program.account.monitoredPosition.fetch(positionPda);
    expect(JSON.stringify(position.status)).to.include("active");
  });
});
