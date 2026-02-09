# SolShield Architecture

## System Overview

SolShield is a three-layer system:

### Layer 1: On-Chain (Anchor Programs)
- **SolShield Program** — Position registry, health tracking, rebalance records
- Stores all monitored positions as PDAs
- Records every rebalance with AI reasoning hash for auditability
- Access-controlled: only the registered agent authority can update positions

### Layer 2: AI Agent (Python)
- **Position Monitor** — Queries Kamino, MarginFi, Solend via RPC
- **Claude Analyzer** — Risk assessment using Claude 3.5 Sonnet
- **Rebalance Executor** — Jupiter swaps + protocol interactions
- **Activity Logger** — Cryptographic hash-chain audit trail

### Layer 3: Dashboard (Next.js)
- Real-time position visualization
- Risk alerts and history
- Agent activity feed

## Data Flow

```
1. Monitor polls Solana RPC every 30s
2. Fetches obligation/margin accounts from lending protocols
3. Calculates health factors
4. If health < threshold → sends to Claude for analysis
5. Claude returns strategy + reasoning
6. Executor builds and signs transaction via AgentWallet
7. Records rebalance on-chain with reasoning hash
8. Activity logger maintains tamper-evident audit trail
```

## Security Model

- Agent authority is a separate keypair from user wallets
- Users explicitly register positions for monitoring
- All AI decisions are hashed and stored on-chain
- Activity log uses SHA-256 hash chain for integrity
- Emergency pause allows users to stop monitoring instantly

## Protocol Integration Details

### Kamino (KLend)
- Program: `KLend2g3cP87ber41GRRLYPqxQ1p57Y5MR8D68Lds`
- Obligation accounts: 1300 bytes, owner at offset 8
- Health factor: weighted collateral / total debt

### MarginFi
- Program: `MFv2hWf31Z9kbCa1snEPYctwafyhdJnV4QSdzCrRKg`
- Margin accounts: authority at offset 40
- Uses bank-based lending with shares model

### Solend
- Program: `So1endDq2YkqhipRh3WViPa8hFMqRV1JimkXg5H2RGD`
- Obligation accounts: 916 bytes, owner at offset 2
- u128 deposited/borrowed values at offset 66

### Jupiter (Swaps)
- Quote API: `https://quote-api.jup.ag/v6/quote`
- Swap API: `https://quote-api.jup.ag/v6/swap`
- Used for collateral rebalancing operations
