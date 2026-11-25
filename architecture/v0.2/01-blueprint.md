# Architecture Blueprint

Version: 0.2.0-draft | Target architecture proposed | Local prototype evidence appended; target not fully implemented or verified

## Scope
Learners, facilitators, experts and organizations share a portal for courses, articles, media, community, live workshops, practice, competitions and competency development.
## Logical architecture
```mermaid
graph TD
 U[Portal PWA] --> C[FastAPI Core]
 U --> I[OIDC Identity]
 C --> D[PostgreSQL]
 C --> A[Adapter Layer]
 A --> M[Moodle]
 A --> B[BigBlueButton]
 A --> F[Discourse]
 C --> G[Model Gateway]
 C --> S[Object Storage]
```
## Decisions
- Core owns navigation, catalog, enrollment orchestration and competency evidence. Engines own native execution records.
- MVP uses modular monolith and background worker; no mandatory microservices.
- React/TypeScript/Vite, FastAPI, PostgreSQL, Keycloak and S3-compatible storage are proposed baseline. Moodle, BBB and Discourse are integrated incrementally; H5P for interactive content. Open edX is an alternative, not concurrent requirement.
- Optional adapters: Strapi, Wiki.js, PeerTube, Castopod, Onyx, Temporal, Metabase.
## Deployment
Local Docker Compose first; separate media workloads; cloud deployment only after capacity and connectivity tests. No fixed sizing until measured.
## Gates
G1 identity and catalog; G2 learning journey; G3 workshop and evidence; G4 community and challenges; G5 AI evaluation. Each requires reproducible tests and rollback instructions.

## Phase 1–2 evidence update — 2026-11-25

### Local implementation boundary
The six-module React/TypeScript + Vite application is implemented and locally tested. Tailwind CSS, shadcn/ui, React Router, Zod and Dexie are used. This is a frontend prototype; the React/Vite + FastAPI/PostgreSQL target diagram above remains a proposed target, not the deployed implementation. See the decision reconciliation and actual component diagram in the linked package.

[Implementation package and decision reconciliation](implementation/phase-1-2/README.md) · [Acceptance evidence](implementation/phase-1-2/ACCEPTANCE.md).

Frontend reconciliation: [ADR-001](../../decisions/ADR-001-frontend-baseline.md), proposed for review.
