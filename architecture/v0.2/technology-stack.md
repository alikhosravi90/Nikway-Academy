# NIKWAY Academy Technology Stack v1.0

**Document ID:** ARC-23  
**Document revision:** 0.2-draft  
**Review status:** Proposed  
**Owner role:** Architecture lead (assignment pending)  
**Dependencies:** [Architecture index](README.md) and [documentation standard](../../governance/documentation-standard.md).

Status: selected design baseline, pending feasibility, licensing, cost and capacity validation. Not an installation manifest.

| Responsibility | Selection |
|---|---|
| Frontend | React + TypeScript + Vite |
| Design | Tailwind + shadcn/ui |
| Mobile | PWA |
| Offline | Dexie |
| Backend | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migration | Alembic |
| Identity | Keycloak |
| LMS | Moodle |
| Community | Discourse |
| Workshop | BigBlueButton |
| Whiteboard | Excalidraw |
| Collaboration | Yjs |
| Interactive content | H5P |
| Knowledge | Wiki.js |
| CMS | Strapi |
| Video | PeerTube |
| Podcast | Castopod |
| Competition | NIKWAY Core |
| Competency | NIKWAY Core |
| Learning records | xAPI + Learning Locker |
| Analytics | Metabase |
| Agent SDK | OpenAI Agents SDK |
| Model gateway | LiteLLM |
| RAG | Onyx |
| Vector storage | pgvector |
| Tools | MCP |
| Local LLM | Ollama |
| Workflow | Temporal |
| Cache | Redis |
| Object storage | S3-compatible |
| Reverse proxy | Traefik |
| Containers | Docker |
| Orchestration | Docker Compose |
| IaC | OpenTofu |
| Metrics | Prometheus |
| Monitoring | Grafana |
| Logs | Loki |
| Telemetry | OpenTelemetry |
| Cloud | ArvanCloud |
| Repository | GitHub |
| Specification | Spec Kit |
| Engineering agent | Codex |
| CI/CD | GitHub Actions |
| Unit tests | pytest + Vitest |
| E2E | Playwright |
| Security | Trivy + CodeQL |

## Decisions

Retain existing React/Vite/Dexie prototype rather than migrate to Next.js. Moodle preferred over Open edX. Modular monolith core, Docker Compose before Kubernetes, local-first and cloud-ready, replaceable model providers. Integrate via versioned APIs, OIDC and events. External services may require their own supported databases and deployment topology; shared PostgreSQL is not mandated for them.

## Adoption gates

Pin versions, review licenses and dependencies, verify identity and API compatibility, measure resource and operating costs, run local smoke and recovery tests, then approve ADRs. Install incrementally, not all at once. No fork, merge or deployment authorized by this record.
