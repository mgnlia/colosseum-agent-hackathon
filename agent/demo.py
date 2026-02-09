"""SolShield Demo — Simulated liquidation prevention scenario

This demo simulates:
1. A user with positions on Kamino, MarginFi, and Solend
2. Market crash causing health factors to drop
3. Claude AI analyzing the risk and recommending strategies
4. Autonomous rebalancing execution
"""
import asyncio
import json
import time
from dataclasses import dataclass

from protocols.base import (
    PositionData, CollateralPosition, DebtPosition,
    Protocol, RiskLevel,
)
from analyzer import ClaudeAnalyzer, RebalanceStrategy
from activity_logger import ActivityLogger


def create_demo_positions() -> list[PositionData]:
    """Create realistic demo positions across protocols"""
    return [
        # Kamino: Healthy position
        PositionData(
            protocol=Protocol.KAMINO,
            owner="DemoWallet111111111111111111111111111111111",
            obligation_key="KaminoObligation1111111111111111111111111",
            health_factor=2.1,
            total_collateral_usd=50000.0,
            total_debt_usd=20000.0,
            net_value_usd=30000.0,
            risk_level=RiskLevel.HEALTHY,
            collaterals=[
                CollateralPosition(
                    mint="So11111111111111111111111111111111111111112",
                    symbol="SOL",
                    amount=250.0,
                    value_usd=37500.0,
                    ltv=0.75,
                    liquidation_threshold=0.85,
                ),
                CollateralPosition(
                    mint="mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
                    symbol="mSOL",
                    amount=75.0,
                    value_usd=12500.0,
                    ltv=0.70,
                    liquidation_threshold=0.80,
                ),
            ],
            debts=[
                DebtPosition(
                    mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                    symbol="USDC",
                    amount=20000.0,
                    value_usd=20000.0,
                    borrow_rate_apy=0.045,
                ),
            ],
        ),
        # MarginFi: WARNING — needs attention
        PositionData(
            protocol=Protocol.MARGINFI,
            owner="DemoWallet111111111111111111111111111111111",
            obligation_key="MarginFiAccount1111111111111111111111111",
            health_factor=1.35,
            total_collateral_usd=30000.0,
            total_debt_usd=19000.0,
            net_value_usd=11000.0,
            risk_level=RiskLevel.WARNING,
            collaterals=[
                CollateralPosition(
                    mint="So11111111111111111111111111111111111111112",
                    symbol="SOL",
                    amount=200.0,
                    value_usd=30000.0,
                    ltv=0.80,
                    liquidation_threshold=0.85,
                ),
            ],
            debts=[
                DebtPosition(
                    mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                    symbol="USDC",
                    amount=19000.0,
                    value_usd=19000.0,
                    borrow_rate_apy=0.052,
                ),
            ],
        ),
        # Solend: CRITICAL — immediate action needed
        PositionData(
            protocol=Protocol.SOLEND,
            owner="DemoWallet111111111111111111111111111111111",
            obligation_key="SolendObligation111111111111111111111111",
            health_factor=1.08,
            total_collateral_usd=25000.0,
            total_debt_usd=19700.0,
            net_value_usd=5300.0,
            risk_level=RiskLevel.CRITICAL,
            collaterals=[
                CollateralPosition(
                    mint="So11111111111111111111111111111111111111112",
                    symbol="SOL",
                    amount=166.7,
                    value_usd=25000.0,
                    ltv=0.75,
                    liquidation_threshold=0.85,
                ),
            ],
            debts=[
                DebtPosition(
                    mint="Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
                    symbol="USDT",
                    amount=19700.0,
                    value_usd=19700.0,
                    borrow_rate_apy=0.068,
                ),
            ],
        ),
    ]


async def run_demo():
    """Run the full demo scenario"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🛡️  SolShield Demo — AI Liquidation Prevention             ║
║                                                              ║
║   Simulating: Market crash → Position risk → AI analysis     ║
║   Protocols:  Kamino | MarginFi | Solend                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

    logger = ActivityLogger(log_dir="agent/logs", agent_name="demo")

    # Create demo positions
    positions = create_demo_positions()

    print("=" * 60)
    print("📊 STEP 1: Position Discovery")
    print("=" * 60)

    for pos in positions:
        risk_emoji = {
            RiskLevel.HEALTHY: "✅",
            RiskLevel.WARNING: "⚠️",
            RiskLevel.CRITICAL: "🔴",
            RiskLevel.EMERGENCY: "🚨",
        }[pos.risk_level]

        print(f"\n{risk_emoji} {pos.protocol.value.upper()} Position:")
        print(f"   Health Factor: {pos.health_factor:.2f}")
        print(f"   Collateral:    ${pos.total_collateral_usd:,.2f}")
        print(f"   Debt:          ${pos.total_debt_usd:,.2f}")
        print(f"   Net Value:     ${pos.net_value_usd:,.2f}")
        print(f"   Risk Level:    {pos.risk_level.value.upper()}")

        await logger.log_activity("position_discovered", {
            "protocol": pos.protocol.value,
            "health_factor": pos.health_factor,
            "risk_level": pos.risk_level.value,
            "collateral_usd": pos.total_collateral_usd,
            "debt_usd": pos.total_debt_usd,
        })

    print("\n" + "=" * 60)
    print("🤖 STEP 2: Claude AI Risk Analysis")
    print("=" * 60)

    # Check if we have an API key for real analysis
    import os
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    at_risk = [p for p in positions if p.risk_level != RiskLevel.HEALTHY]

    for pos in at_risk:
        print(f"\n🔍 Analyzing {pos.protocol.value.upper()} position (HF: {pos.health_factor:.2f})...")

        if api_key and api_key != "your_anthropic_api_key":
            # Real Claude analysis
            analyzer = ClaudeAnalyzer(api_key=api_key)
            analysis = await analyzer.analyze_position(pos)
        else:
            # Fallback demo analysis
            analyzer = ClaudeAnalyzer(api_key="demo")
            analysis = analyzer._fallback_analysis(pos)

        print(f"\n   📋 AI Recommendation:")
        print(f"   Strategy:    {analysis.strategy.value}")
        print(f"   Confidence:  {analysis.confidence:.0%}")
        print(f"   Urgency:     {analysis.urgency_score:.0%}")
        print(f"   Amount:      ${analysis.suggested_amount_usd:,.2f}")
        print(f"   Reasoning:   {analysis.reasoning[:200]}")
        print(f"   Hash:        {analysis.reasoning_hash[:32]}...")

        await logger.log_activity("ai_analysis", analysis.to_dict())

    print("\n" + "=" * 60)
    print("⚡ STEP 3: Autonomous Rebalancing (Dry Run)")
    print("=" * 60)

    for pos in at_risk:
        analyzer = ClaudeAnalyzer(api_key="demo")
        analysis = analyzer._fallback_analysis(pos)

        if analysis.needs_action:
            print(f"\n🔄 Executing {analysis.strategy.value} on {pos.protocol.value.upper()}:")
            print(f"   Amount: ${analysis.suggested_amount_usd:,.2f}")
            print(f"   Status: ✅ DRY RUN SUCCESS")
            print(f"   TX:     DRY_RUN_{'x' * 32}")

            await logger.log_activity("rebalance_executed", {
                "protocol": pos.protocol.value,
                "strategy": analysis.strategy.value,
                "amount_usd": analysis.suggested_amount_usd,
                "dry_run": True,
            })

    print("\n" + "=" * 60)
    print("📊 STEP 4: Results Summary")
    print("=" * 60)

    summary = await logger.get_summary()
    print(f"\n   Total Actions:        {summary['total_entries']}")
    print(f"   Integrity Valid:      {'✅' if summary['integrity_valid'] else '❌'}")
    print(f"   Activity Breakdown:   {json.dumps(summary['actions'], indent=6)}")
    print(f"   Chain Hash:           {summary['last_hash'][:32]}...")

    total_protected = sum(p.total_collateral_usd for p in at_risk)
    print(f"\n   💰 Total Value Protected: ${total_protected:,.2f}")
    print(f"   🛡️  Liquidations Prevented: {len(at_risk)}")

    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ✅ Demo Complete!                                          ║
║                                                              ║
║   SolShield successfully:                                    ║
║   • Discovered positions across 3 Solana DeFi protocols      ║
║   • Identified 2 at-risk positions                           ║
║   • Generated AI-powered rebalancing strategies              ║
║   • Executed autonomous rebalancing (dry run)                ║
║   • Maintained cryptographic audit trail                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    asyncio.run(run_demo())
