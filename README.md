# Sales GPT Agent

AI copilot for the complete B2B sales cycle, combining SDR, Account Executive, and Sales Manager capabilities.

## Mission
Turn account signals, research, conversations, and opportunity data into the next best sales action across target account → qualified opportunity → closed deal → expansion.

## Agent modes
- **SDR Agent:** ICP/account research, trigger detection, persona mapping, prospect research, outreach, qualification, meeting prep, and AE handoff.
- **Account Executive Agent:** account planning, discovery, MEDDPICC, stakeholder mapping, solution/demo strategy, competitive positioning, ROI, Mutual Action Plans, objections, negotiation, deal risk, forecasting, and expansion.
- **Sales Manager Agent:** orchestrates the right skill based on stage, evidence, risk, and seller intent; challenges weak assumptions and recommends next actions.

## Architecture
```text
Sales-GPT-Agent/
├── agents/
├── skills/
│   ├── sdr/
│   ├── ae/
│   └── shared/
├── workflows/
├── memory/
├── knowledge/
└── examples/
```

## Design principles
1. Evidence before inference — distinguish facts, hypotheses, and unknowns.
2. Revenue outcomes over activity — optimize for meaningful opportunity progression.
3. One account context — SDR and AE agents share account, stakeholder, interaction, and opportunity state.
4. Next-best action — every analysis ends with prioritized recommendations.
5. Enterprise discipline — support multi-threading, MEDDPICC, business cases, procurement, security, legal, and executive alignment.
6. Human-controlled execution — external actions remain reviewable before sending.

## Milestone 1
Shared sales memory plus core SDR research/outreach and AE discovery/MEDDPICC/deal-strategy skills.
