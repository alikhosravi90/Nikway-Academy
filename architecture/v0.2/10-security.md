# Security Architecture

Version: 0.2.0-draft | Proposed architecture | Not implemented or verified

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
