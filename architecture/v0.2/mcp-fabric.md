# NIKWAY MCP Fabric

Proposed, not implemented. Domain tool groups: learning, community, knowledge, workshop, assessment, competency, media, practice, competition, tenant, engineering, governance, analytics. Grouping does not require thirteen separate deployments.

Candidate stack: FastMCP, OpenAI Agents SDK, IBM ContextForge gateway, Streamable HTTP or local stdio, Keycloak, OAuth authorization as applicable to transport, OPA, JSON Schema, OpenTelemetry, OpenBao, Temporal. MCP connects agents to tools/resources; A2A is a separate agent communication candidate.

Registry records tool identity, version, schemas, scopes, tenant context, side effects, timeout and approval policy. Separate read/write tools; enforce authorization at backend, not merely gateway. Validate inputs/outputs, prevent token passthrough and cross-tenant access, audit actions without secrets. Require scoped human approval for sensitive writes. Benchmark gateway, SDK and protocol compatibility; test unauthorized calls, injection, replay, tenant isolation and failure recovery.