# NIKWAY Academy Security Architecture — Defense in Depth

**Document ID:** ARC-22  
**Document revision:** 0.2-draft  
**Review status:** Proposed  
**Owner role:** Architecture lead (assignment pending)  
**Dependencies:** [Architecture index](README.md) and [documentation standard](../../governance/documentation-standard.md).

Status: proposed extension to ARC-10; not implemented, audited or certified.

| Layer | Candidate controls and tools |
|---|---|
| Network | WireGuard, private networks |
| Edge | ArvanCloud CDN/WAF/DDoS protection |
| Identity | Keycloak, WebAuthn/TOTP MFA |
| Authorization | RBAC, ABAC, Open Policy Agent |
| Tenant isolation | PostgreSQL RLS and scoped application authorization |
| Secrets | OpenBao |
| Transport | TLS, Let's Encrypt |
| API | Traefik, rate limits |
| Uploads | ClamAV, quarantine and validation |
| Code and containers | CodeQL, Trivy, Gitleaks |
| Supply chain | Sigstore/Cosign, CycloneDX SBOM |
| Runtime | Falco where supported, Wazuh |
| AI and MCP | Scoped tools, approval gates, injection defenses |
| Recovery | Restic, pgBackRest |

## Architecture
Zero Trust, defense in depth and DevSecOps. Enforce authorization at each trust boundary, including external engines, distributed cells, storage, search and agent memory. CDN must not expose private tenant content. Separate credentials per environment and cell. Apply least privilege, audit privileged operations, rotate secrets and protect logs from sensitive data leakage.

## References
ISO/IEC 27001, 27701, 27017, 27018; ISO 22301; NIST CSF 2.0 and SP 800-207; OWASP ASVS, API Security and LLM Top 10; SLSA. Verify editions and applicability; no compliance claim.

## Acceptance gates
Threat model and access matrix; negative cross-tenant tests; MFA and revocation tests; secret, dependency and container scans; signed artifact verification; upload quarantine tests; AI prompt-injection and tool authorization tests; backup restore and incident response exercise. Runtime monitoring and penetration testing before production. Benchmark, licensing, resource sizing and provider capability verification remain pending. Install controls incrementally; no merge or deployment authorized.
