# Standards Compliance Matrix

**Document ID:** ARC-12  
**Document revision:** 0.2-draft  
**Review status:** Proposed  
**Owner role:** Architecture lead (assignment pending)  
**Dependencies:** [Architecture index](README.md) and [documentation standard](../../governance/documentation-standard.md).

Version: 0.2.0-draft | Target architecture proposed | Local prototype evidence appended; target not fully implemented or verified

All references are candidates; applicability and edition must be verified. Status N/A here means not assessed, not exemption.

| Reference | Requirement area | Evidence | Owner | Status |
|---|---|---|---|---|
| ISO 42010 | Architecture description | Viewpoint review | Architect | Not assessed |
| ISO 25964 / SKOS | Vocabulary | Validation | Knowledge lead | Not assessed |
| ISO 30401 | Knowledge management | Process review | Knowledge lead | Not assessed |
| ISO 9241-210 | Human-centered design | User research | UX lead | Not assessed |
| WCAG 2.2 AA | Accessibility | Audit | UX lead | Not assessed |
| ISO 21001 / 29993 | Learning quality | Service review | Learning lead | Not assessed |
| xAPI / cmi5 / SCORM | Learning records/content | Interop tests | Integration lead | Not assessed |
| LTI 1.3 / QTI / CASE | Tool, assessment, competency exchange | Contract tests | Integration lead | Not assessed |
| Open Badges 3.0 | Credentials | Verification tests | Learning lead | Not assessed |
| ISO 25010 | Software quality | Quality report | Engineering lead | Not assessed |
| ISO 27001 / 27701 / OWASP ASVS | Security/privacy | Audit | Security lead | Not assessed |
| ISO 42001 / 23894 | AI governance/risk | Risk register and evaluations | AI lead | Not assessed |

## Governance

Track control ID, applicable edition, requirement reference, implementation, evidence URI, reviewer, status and review date. Statuses: proposed, applicable, implemented, verified, failed, justified exclusion. No certification asserted. Role assignments are proposed, not staffed.

## Phase 1–2 evidence update — 2026-11-25

### Evidence is not standards validation

The local build, 24 Vitest tests and 12 Playwright tests provide bounded implementation evidence. Responsive/keyboard/dialog behavior is relevant to accessibility review, and functional tests to software quality, but none establishes compliance with the standards above. Keep every standards assessment status unchanged until applicability, edition, control mapping and independent review are completed.

[Implementation package and decision reconciliation](implementation/phase-1-2/README.md) · [Acceptance evidence](implementation/phase-1-2/ACCEPTANCE.md).
