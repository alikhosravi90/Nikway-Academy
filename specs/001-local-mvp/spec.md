# Local operational Academy MVP

A learner signs in, uses the single active tenant membership resolved by the API, enrolls in a course, completes ordered lessons, submits evidence and receives human rubric-based feedback. The local fixture provides a scheduled workshop with atomic capacity limits; workshop authoring and a facilitator role are deferred. Read-only tool invocation reports real capability availability.

API baseline: GET /api/me, GET /api/courses, POST /api/courses/{id}/enroll, POST /api/courses/{id}/lessons/{lesson_id}/complete, GET /api/progress, POST /api/courses/{id}/submissions, GET /api/submissions, POST /api/submissions/{id}/review, GET /api/workshops, POST /api/workshops/{id}/register, GET /api/capabilities, POST /api/tools/invoke.

JWT issuer, audience, signature and expiry are verified. Tenant context is derived from active membership; identity never comes from request payload. Tenant columns, scoped constraints and forced RLS protect server data. Application DB role must not bypass RLS. Reviewer cannot accept their own submission. The catalog is seeded and immutable through this API; each submission pins rubric_version=1 and retains its review revision. Catalog publishing/version management is deferred. Revision-requested follow-up is a new immutable submission, not a linked revision chain.

Write replay must not duplicate enrollment, completion or registration. Cross-tenant resources do not reveal private existence. Missing policy, invalid input, unavailable capability, unknown tool, timeout and exhausted budget fail closed. Browser demo data is not silently promoted into authenticated state.

No valid credential, live AI, MCP compatibility, videoconference integration, xAPI compliance or learning efficacy claim follows from this slice.
