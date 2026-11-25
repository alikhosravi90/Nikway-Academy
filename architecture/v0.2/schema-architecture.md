# NIKWAY Unified Schema Architecture

Proposed schema-first, ontology-first and contract-first design. References: https://schema.org/ ; https://github.com/openedx/edx-platform ; https://github.com/moodle/moodle ; https://github.com/frappe/frappe ; https://github.com/directus/directus ; https://github.com/backstage/backstage ; https://github.com/Apicurio/apicurio-registry ; https://www.1edtech.org/ ; https://www.w3.org/TR/shacl/ . Qualitative benchmark only.

| Layer | Selection |
|---|---|
| Semantic | RDF, OWL, SKOS, SHACL |
| Canonical and agent contracts | JSON Schema |
| Database | PostgreSQL |
| API | OpenAPI |
| Events | AsyncAPI |
| UI | JSON Forms |
| Learning | xAPI, QTI, CASE, LRMI |
| Tools | MCP |
| Workflow | BPMN |
| Web metadata | Schema.org |
| Registry | Apicurio |
| Migrations | Alembic |
| Validation | Pydantic, pySHACL |
| Contract testing | Pact |

Domain schemas: identity, tenancy, catalog, learning, community, knowledge, media, workshop, practice, competition, assessment, competency, credentials, intelligence, billing, integration, audit. Domain schemas do not replace tenant isolation. Canonical domain concepts map explicitly to database, API, event, UI and learning models; do not assume automatic lossless conversion. Version contracts, enforce backward compatibility, validate migrations and tenant boundaries, and test producer/consumer compatibility. GitHub is baseline source of truth; registry adoption requires feasibility review. No implementation or merge claimed.
