# ADR-001 — Frontend baseline

Status: proposed for review. Owner role: architecture lead.

Context: local prototype uses React/TypeScript/Vite/Dexie; earlier target proposed Next.js. The selected stack retains Vite.

Decision: retain React/Vite as target frontend baseline; FastAPI remains proposed backend. Next.js is deferred unless measured SSR or other requirements justify migration.

Consequences: preserve existing frontend investment; validate PWA, routing, accessibility and SEO requirements. No backend implementation or production readiness implied.

Acceptance: review with owner, reproduce prototype build and document any unmet requirements. Supersedes only the earlier proposed Next.js selection upon approval.
