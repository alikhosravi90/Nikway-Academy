# NIKWAY Academy — Agentic Spec-Driven SDLC

Status: proposed baseline; not installed, approved or operationally validated.

## Benchmark

| Method | Application |
|---|---|
| Waterfall | High-level documentation |
| V-Model | Verification and validation |
| Spiral | Risk-driven iteration |
| Scrum | Iterative planning |
| Kanban | Agent work flow and WIP |
| XP | Engineering practices |
| DDD | Domain boundaries |
| TDD | Test-first development |
| BDD | Behavioral acceptance |
| SDD | Specification-first implementation |
| DevSecOps | Secure delivery |
| GitHub Flow | Branch and PR workflow |

References: [GitHub Spec Kit](https://github.com/github/spec-kit), [Moodle development process](https://docs.moodle.org/dev/Process). These are qualitative reference patterns, not verified comparative performance results.

## Proposed lifecycle

Constitution → Research → Specify → Plan → Issues/Tasks → Branch → Implement/Test → Commit/Push → PR → Validate → Independent Review → Gate → Merge → Release → Measure/Improve.

## Controls

- No implementation without scoped specification and acceptance criteria.
- No change without traceable issue, except explicitly authorized bootstrap.
- No acceptance without tests and evidence.
- No merge without passing required checks and independent review.
- No production deployment without approval and rollback plan.
- Failed gates return work to implementation; never bypass controls.

## Tooling

Spec Kit for specifications and tasks; GitHub Projects/Issues for coordination; GitHub Actions for checks; Codex and scoped sub-agents for implementation; ADRs for decisions; Playwright and pytest for tests.

## Adoption gates

Verify Spec Kit version and license; run a small local pilot; establish constitution and role authority; configure required CI and review rules; demonstrate traceability from specification to issue, PR, test evidence and release. Installation and enforcement remain pending.
