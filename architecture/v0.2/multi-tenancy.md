# NIKWAY Academy — Hybrid Multi-Tenancy

Status: proposed; isolation, licensing and runtime compatibility not verified.

## Benchmark
- [AWS SaaS Lens](https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/saas-lens.html): pool, bridge and silo isolation patterns.
- [Moodle Workplace](https://moodle.com/products/workplace/): commercial multi-tenancy capability; standard Moodle LMS must not be assumed to provide equivalent isolation.
- [Open edX](https://github.com/openedx/edx-platform): multisite capabilities are not proof of tenant isolation.

## Selected architecture
NIKWAY Core owns tenant registry, membership, provisioning and policy. Pool: shared core and PostgreSQL with tenant_id and RLS. Bridge: dedicated database or resources. Silo: dedicated instance. On-premise: independent deployment. Public content is explicitly classified; anonymous access does not grant tenant access. Model selection depends on verified requirements and cost, not customer size alone.

## Controls
Derive tenant context from authenticated membership, not untrusted request fields. Enforce scoped authorization and RLS with non-bypass application roles; tenant-scoped constraints, storage policies, cache keys, search indexes, agent memory, model quotas, workflow identifiers, logs and reports. External engines require verified isolation or separate instances. Keycloak identity, FastAPI authorization, PostgreSQL RLS, S3 policies, Redis namespaces, LiteLLM quotas, Temporal workflows and OpenTofu provisioning are proposed components, not proof of isolation.

## Tenant lifecycle
Register → provision → activate → operate → migrate/suspend → export → offboard. Support branding, billing, quotas, backup/restore, controlled federation and audited migration. Define retention and deletion policy before launch.

## Acceptance gates
Negative cross-tenant tests for APIs, DB, files, cache, search, AI retrieval, reports and background jobs; verify privileged access and tenant switching; test tenant-specific restore, migration and offboarding; verify Moodle, Discourse, BBB and other adapter isolation independently. Measure costs and noisy-neighbor effects. No production data or secrets in public repository. No deployment or merge authorized.
