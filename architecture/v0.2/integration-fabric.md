# NIKWAY Unified Integration Fabric

**Document ID:** ARC-18  
**Document revision:** 0.2-draft  
**Review status:** Proposed  
**Owner role:** Architecture lead (assignment pending)  
**Dependencies:** [Architecture index](README.md) and [documentation standard](../../governance/documentation-standard.md).

Proposed extension to ARC-11. Qualitative benchmark: Kong/Traefik/APISIX; Kafka/RabbitMQ/NATS; Temporal/Camunda; Camel/Spring Integration; n8n/Node-RED; Airbyte/NiFi; Debezium/Maxwell; Apicurio/Confluent; Keycloak/authentik; Pact/Schemathesis; OPA/Cedar.

Selected candidates: Traefik, FastAPI/OpenAPI, NATS JetStream/AsyncAPI, Temporal, Apache Camel adapters, n8n automation, Airbyte batch data integration, Debezium CDC, Apicurio registry, Keycloak OIDC, MCP and A2A, Pact, OPA, OpenTelemetry, Pydantic. Learning interfaces: LTI, xAPI, QTI, CASE; semantic RDF/JSON-LD; WebSocket, WebRTC/HLS; versioned federation sync.

Core owns contracts; adapters isolate external engines. Apply tenant-aware authorization, idempotency, outbox, bounded retry, dead-letter handling, circuit breakers and versioning. Adopt incrementally: API first, events/workflows second, agent/contracts third, adapters/automation fourth, data/CDC/A2A fifth, federation sixth. Verify licenses, interoperability, resource cost and failure recovery before adoption. No installation or merge claimed.