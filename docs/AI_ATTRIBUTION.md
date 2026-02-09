# AI Attribution Log

## Overview

SolShield is an AI-native project. This document transparently logs all AI usage in compliance with hackathon rules.

## AI Systems Used

### 1. Claude (Anthropic) — Runtime Risk Analysis
- **Model**: Claude 3.5 Sonnet (`claude-sonnet-4-20250514`)
- **Purpose**: Real-time DeFi position risk analysis and rebalancing strategy recommendation
- **Integration**: Direct API calls via `anthropic` Python SDK
- **Decision Logging**: Every AI decision is:
  - Logged with full reasoning trace
  - SHA-256 hashed for integrity
  - Recorded on-chain in `RebalanceRecord` accounts
  - Stored in tamper-evident activity log

### 2. Claude — Code Generation Assistance
- **Purpose**: Assisted in generating boilerplate code, tests, and documentation
- **Human Review**: All generated code was reviewed and modified for correctness
- **Scope**: Smart contract scaffolding, protocol adapter templates, test structures

## Transparency Measures

1. **On-Chain Attestation**: Every rebalance records `ai_reasoning_hash` on Solana
2. **Hash Chain Log**: `agent/logs/` contains append-only JSONL with SHA-256 chain
3. **Verifiable**: Run `python -c "from activity_logger import ActivityLogger; ..."` to verify integrity
4. **Open Source**: All AI prompts are visible in `agent/analyzer.py`

## AI Decision Framework

The AI operates within strict guardrails:
- **Conservative bias**: Only acts when confidence ≥ 70%
- **Fallback rules**: If AI fails, rule-based system takes over
- **Cooldown**: Minimum 60 seconds between rebalances
- **Emergency override**: Users can pause monitoring at any time
- **Transparency**: Full reasoning is logged, never a black box

## Ethical Considerations

- Users explicitly opt-in to monitoring
- AI cannot access user funds without registration
- All actions are auditable and reversible
- Emergency pause is always available
- No hidden data collection or tracking
