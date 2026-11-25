# NIKWAY Learning Experience Intelligence

**Document ID:** ARC-24  
**Document revision:** 0.2-draft  
**Review status:** Proposed  
**Owner role:** Architecture lead (assignment pending)  
**Dependencies:** [Architecture index](README.md) and [documentation standard](../../governance/documentation-standard.md).

Proposed xAPI architecture; no LRS installed or conformance verified. Record learning experiences from courses, articles, videos, workshops, exercises, competitions, projects, assessments, community and AI mentoring using Actor–Verb–Object statements with context, result and timestamp where appropriate.

Candidate stack: xAPI / IEEE 9274.1.1, Learning Locker, cmi5, xAPI Profiles, NATS JetStream, FastAPI adapter, Metabase, Dexie offline queue, Keycloak, CASE competency mappings. Source activities emit validated statements through adapter to LRS; authorized analytics consume records. Participation is not proof of competency. Minimize personal data, scope records to tenant, use stable statement IDs and deduplicate retries; enforce authorization on ingestion and query. Verify supported xAPI versions, profile semantics, offline replay, isolation, retention and correction procedures before adoption.