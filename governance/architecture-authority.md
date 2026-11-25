# Architecture authority and conflict register

Status: proposed. Core ARC-01–12 define scope; extensions refine their own responsibility. Approved ADRs resolve conflicts; no draft silently overrides another.

| Concern | Primary reference | Related |
|---|---|---|
| Frontend | ARC-23 + proposed ADR-001 | ARC-01,05,13 |
| Tenant isolation | ARC-20 | ARC-08,10,17,22 |
| Security | ARC-10,22 | ARC-17 |
| Integration | ARC-11,18 | ARC-15,19,21 |
| Data contracts | ARC-15 | ARC-08,21 |
| Learning records | ARC-24 | ARC-06,08 |
| Infrastructure | ARC-16 | ARC-14,20,23 |
| Agent tools | ARC-19 | ARC-09,17 |

## Open decisions

- Confirm Vite baseline and SEO/PWA needs (ADR-001 pending).
- Decide minimum MVP services versus optional candidates; avoid deploying overlapping CMS, knowledge and media systems without use cases.
- Verify Moodle and LRS tenant isolation and protocol versions.
- Decide whether Camel, n8n, Temporal and NATS are needed for each integration path.
- Resolve overlapping AI guardrail libraries after evaluation.
- Verify licenses, provider capability, costs and standards editions.

Cross-references are navigation, not evidence of semantic consistency. Independent review and CI remain pending. No merge authorized.
