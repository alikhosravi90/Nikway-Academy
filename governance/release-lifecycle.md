# NIKWAY development and release lifecycle

Status: proposed; not operationally validated. Extends Unified Agentic SDLC.

## Reference patterns

- [Moodle development process](https://docs.moodle.org/dev/Process): developer, peer reviewer, integrator and tester responsibilities.
- [Kubernetes release process](https://github.com/kubernetes/sig-release): release planning, stabilization, code freeze and prerelease gates.
- [GitHub Spec Kit](https://github.com/github/spec-kit): specification-driven work.

## Lifecycle

Research → Roadmap → Target Release → Specification → Issue → Branch → Implementation/Test → Commit/Push → PR → Review/CI → Merge → Integration Testing → Code Freeze → Stabilization → Alpha → Beta → Release Candidate → Release Gate → Release → Deploy → Monitor → Maintenance → Research.

## Nested cycles

Strategic: roadmap and feedback. Release: milestone, integration and stabilization. Development: issue, branch, PR and acceptance.

## Controls

- Merge requires passing required checks, evidence and independent review.
- Freeze prohibits new features; approved fixes only. Unready features are deferred.
- Alpha: internal validation; beta: controlled user feedback; RC: candidate for final acceptance. Stages may be combined for low-risk MVP with documented approval.
- Release gate: integrated tests, security review, release notes, version, rollback and operational readiness.
- Deployment requires explicit authorization and monitoring.
- Hotfix: issue, scoped branch, regression tests, review, merge, patch release and reconciliation with active development.
- Rollback: restore known-good artifact and compatible data state using tested procedure; record incident and follow-up.
- Maintenance: track supported versions, vulnerabilities, defects and deprecation.

## Validation

Run one pilot release and record traceability, CI, independent review, integration tests and recovery evidence. Benchmark is qualitative, not a source-code audit. No merge or deployment is authorized by this document.
