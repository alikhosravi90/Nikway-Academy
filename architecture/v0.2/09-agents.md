# AI Agent Architecture

Version: 0.2.0-draft | Proposed architecture | Not implemented or verified

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
