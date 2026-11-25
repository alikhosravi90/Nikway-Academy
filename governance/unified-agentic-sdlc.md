# NIKWAY Unified Agentic SDLC

Status: proposed hybrid methodology; not empirically validated or enforced.

| Model | Responsibility |
|---|---|
| Release-driven | Version scope and release gates |
| Specification-driven | Requirements and acceptance criteria |
| Issue-driven | Traceable work |
| Domain-driven | Domain boundaries |
| Test-driven | Implementation quality |
| Evidence-based | Acceptance evidence |
| GitHub Flow | Branch and PR workflow |
| Stage-Gate | Approval controls |
| DevSecOps | Secure delivery |
| Agentic development | Scoped agent execution |
| PDCA | Continuous improvement |

## Workflow

Roadmap → Target Release → Milestone → Epic → Feature → Specification → Issue → Task → Agent assignment → Branch → Implement/Test → Commit/Push → PR → Validate/Review → Merge → Release Gate → Release/Deploy → Measure/Improve.

A target release is a planning object, not an already published release. Epics and tasks may be represented as issues or sub-issues. Small changes may omit intermediate planning layers but retain traceability, acceptance criteria and required checks. Multiple issues may share a PR only with explicit scope and acceptance mapping.

## Gates

- Issue: scope, owner, dependencies and acceptance criteria.
- PR: linked issues, test evidence, risk and rollback notes.
- Merge: required checks pass and independent review approves.
- Release: required milestone issues accepted, integrated tests pass, version and release notes prepared.
- Deployment: authorized environment, rollback and monitoring ready.

## Adoption

Complements implementation-methodology.md; does not replace its controls. Validate on one pilot feature before enforcing repository-wide. No merge or release is authorized by this document.
