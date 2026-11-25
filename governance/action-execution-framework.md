# NIKWAY Action Execution Framework

Status: proposed; not operationally validated or enforced. Extends Unified Agentic SDLC and release lifecycle.

## Reference patterns

- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow): branches, review, merge.
- [Spec Kit](https://github.com/github/spec-kit): specifications, plans, tasks.
- [Moodle](https://docs.moodle.org/dev/Process): separation of development, review, integration and testing.
- [Kubernetes](https://github.com/kubernetes/community): ownership and release coordination.
- [Kanban](https://kanbanguides.org/): flow and WIP limits.
- [ITIL](https://www.peoplecert.org/): change and service operations.
- [BPMN](https://www.omg.org/spec/BPMN/): process modeling.
- [Temporal](https://github.com/temporalio/temporal): durable execution and recovery; optional, subject to feasibility.

## Hierarchy

Portfolio → Product → Roadmap → Target Release → Milestone → Epic → Feature → Issue → Task → Action. Intermediate layers may be omitted for small work.

## Action lifecycle

Requested → Dependency Check → Ready → Assigned → Executing → Verification → Accepted → Evidence Recorded → Closed. Failed verification returns to correction; blocked work escalates; cancellation records reason. Evidence must be available before acceptance; the evidence-recording step finalizes the audit record.

## Action contract

Required: action_id, parent_issue, objective, inputs, outputs, owner, dependencies, tools, permissions, timeout, cost_limit, acceptance_criteria, evidence_refs, status. Record attempt count, timestamps and correlation ID. Never store secrets in public records.

## Execution controls

Definition of Ready: scope, inputs, dependencies, owner, authority and acceptance criteria confirmed. Definition of Done: output verified, evidence linked, review completed and residual risks recorded. Apply WIP limits, bounded retry with idempotency, timeout, escalation, checkpoints and audit trail. Compensate reversible side effects when safe; irreversible actions require approval. Do not retry authorization failures automatically.

## Responsibility

Product owner defines goals; coordinator assigns work; executor implements; independent verifier validates; maintainer approves merge; release manager controls release; operator deploys only with authorization.

## Validation

Pilot one issue with dependent actions, a retryable failure, a blocked action and independent acceptance. Measure cycle time, WIP, failure rate and evidence completeness. This is a qualitative benchmark, not a measured comparison. No installation, merge or deployment is authorized by this document.
