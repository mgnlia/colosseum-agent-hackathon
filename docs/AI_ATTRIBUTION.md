# AI Attribution Log — SolShield

## Overview

SolShield was built by an autonomous AI agent (Claude, by Anthropic) as part of the Colosseum Agent Hackathon 2026. This document provides full transparency on AI involvement.

## AI Usage

### Code Generation
- **Model:** Claude (Anthropic) via Claude Code CLI
- **Scope:** All source code, documentation, and configuration files
- **Human oversight:** Architecture direction and review by human operator

### Runtime AI (Agent Core)
- **Model:** Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- **Purpose:** Real-time DeFi position risk analysis and rebalancing strategy selection
- **Decision logging:** Every AI decision is logged with full reasoning traces in `agent/logs/`
- **Cryptographic verification:** Ed25519 signatures on all activity logs

## Build Timeline

| Date | Activity | AI Involvement |
|------|----------|---------------|
| Feb 2, 2026 | Hackathon start | - |
| Feb 7, 2026 | Initial architecture design | Claude: full code generation |
| Feb 8, 2026 | Protocol adapters (Kamino, MarginFi, Solend) | Claude: implementation |
| Feb 9, 2026 | Anchor programs + agent core | Claude: implementation |
| Feb 9, 2026 | Platform registration + submission | Claude: autonomous registration |
| Feb 9, 2026 | Forum engagement + community interaction | Claude: content generation |

## Decision Transparency

Every rebalancing decision made by SolShield includes:

1. **Input data:** On-chain position state (health factor, LTV, collateral, debt)
2. **Market context:** Token prices, volatility metrics, protocol utilization
3. **AI reasoning:** Full text explanation of why the action was chosen
4. **Confidence score:** 0.0-1.0 indicating model certainty
5. **Alternative strategies:** Other options considered and why they were rejected
6. **Cryptographic signature:** Ed25519 signature for tamper-proof audit trail

## Ethical Considerations

- SolShield operates in **dry-run mode by default** — no funds are moved without explicit opt-in
- All AI decisions are logged and auditable
- The agent cannot access user funds without explicit wallet delegation
- Emergency stop mechanism allows immediate agent shutdown
- Health factor thresholds are conservative to avoid unnecessary actions

## License

MIT — All code is open source and available for review.
