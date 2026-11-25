# AI Agent Architecture

**Document ID:** ARC-09  
**Document revision:** 0.2-draft  
**Review status:** Proposed  
**Owner role:** Architecture lead (assignment pending)  
**Dependencies:** [Architecture index](README.md) and [documentation standard](../../governance/documentation-standard.md).

Version: 0.2.0-draft | Target architecture proposed | Local prototype evidence appended; target not fully implemented or verified

## Roles
Tutor explains and quizzes; facilitator drafts workshop plans; knowledge agent retrieves authorized sources; feedback agent proposes rubric feedback; content agent drafts resources.
## Execution
Request → identity/scope → policy check → retrieval → model gateway → tool validation → response/evidence → audit. LiteLLM proposed gateway; SDK replaceable. No autonomous privileged writes.
## Tool contract
Each tool declares input schema, output schema, required scope, side effects, timeout and approval requirement. Tool outputs are untrusted data.
## Memory
Session context isolated by tenant and user; durable learning preferences opt-in; retrieval filtered by access. No private data used for training by default.
## Evaluation
Groundedness, citation validity, pedagogical correctness, injection resistance, leakage, cost and latency. Human approval for grading, publication and credential issuance.
## Acceptance
Adversarial tests, cross-tenant retrieval denial, budget limit, tool failure fallback and human override.

## Phase 1–2 evidence update — 2026-11-25

### Mock-only adapter boundary
TutorPort.reply(prompt, locale) is asynchronous and provider-independent. The current MockTutor returns prewritten answers for three topics and explicitly declines unsupported topics. Chat survives module navigation but is session-only. No model call, retrieval system, tools, durable AI memory or autonomous action exists. Text rendering and prompt bounds were checked; this is not adversarial evaluation of an LLM.

[Implementation package and decision reconciliation](implementation/phase-1-2/README.md) · [Acceptance evidence](implementation/phase-1-2/ACCEPTANCE.md).

## Related architecture authority
[ARC-19 — specialized design](./mcp-fabric.md) refines this document within its scope. Both remain proposed; unresolved conflicts require an ADR and review. Historical implementation evidence is not superseded by target design.
