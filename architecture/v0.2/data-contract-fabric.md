# NIKWAY Data Contract Fabric

Proposed, not implemented. Data contracts specify schema, semantics, producer/consumer ownership, quality, classification, access, tenant context, version, SLO, lineage, retention and compatibility.

Candidate stack: ODCS, Data Contract CLI, Apicurio, OpenMetadata, Soda Core, OpenLineage, JSON Schema/Pydantic, SHACL, OpenAPI, AsyncAPI, Pact, OPA and GitHub. Verify format and tooling compatibility; API/event/tool contracts remain distinct from dataset contracts and may reference them.

Contract catalog: tenant, identity, learning, xAPI, competency, assessment, agent memory, MCP tools, events and federation. Lifecycle: ontology → domain model → contract proposal → review/version → registry → producer validation → consumer verification → quality monitoring → evidence → revision. Require named owners, explicit compatibility policy, sample fixtures, negative tenant tests, quality thresholds and deprecation notice. GitHub is canonical versioned baseline; registry is distribution mechanism. Benchmark and runtime validation pending. No merge or deployment authorized.