# Security Architecture

Version: 0.2.0-draft | Target architecture proposed | Local prototype evidence appended; target not fully implemented or verified

## Trust boundaries
Browser, API, identity provider, external engines, storage, model providers and operators. Treat all external content and model output as untrusted.
## Controls
OIDC authorization code with PKCE; server-side authorization; scoped RBAC; tenant isolation; TLS; secret manager; signed short-lived media URLs; upload limits and scanning; audit trail; rate limits.
## Threats
| Threat | Mitigation |
|---|---|
| Cross-tenant access | Scoped queries and negative tests |
| Account takeover | MFA for privileged roles, session revocation |
| Malicious upload | Type validation, quarantine |
| Prompt injection | Tool allowlists and approval gates |
| Supply chain | Dependency scanning and pinned versions |
| Data loss | Encrypted backup and restore drill |
## Privacy
Consent for recordings, minimal collection, retention and deletion workflows; no secrets or personal records in public GitHub. Legal jurisdiction and age policies require review.
## Acceptance
Threat model review, access matrix tests, vulnerability scan and recovery evidence. No compliance claim.

## Phase 1–2 evidence update — 2026-11-25

### Observed local controls and limits
Implemented: Zod validation, React text rendering, bounded tutor prompts, validated backup import, transactional local writes, reset confirmation and dependency lockfile. The dated npm audit reported zero known vulnerabilities. No server authorization, OIDC, tenant isolation, encryption-at-rest guarantee, secret manager, upload malware scanning or security certification is claimed. Published evidence excludes local absolute paths and screenshots containing profile labels.

[Implementation package and decision reconciliation](implementation/phase-1-2/README.md) · [Acceptance evidence](implementation/phase-1-2/ACCEPTANCE.md).
