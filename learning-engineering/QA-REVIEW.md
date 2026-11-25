# Independent QA review — 2026-11-25

**PASS_LOCAL_STRUCTURE** for the bounded offline prototype after remediation.
**PARTIAL** for source, bilingual semantic and instructional validation.
**NO-GO** for production delivery, standards conformance, or educational-effectiveness claims.

Review scope: the seven preserved Learning Engineering baseline documents, implementation specification/plan, engine, record/package/semantic schemas, ontology/glossary, ten PDCA records, and 29-item research register. QA authored only this report and `tests/test_qa.py`; implementation fixes were made by the implementation agents. No commit, push, deployment, learner-data access, or permission change was performed by QA.

## Reproducible verification

From `learning-engineering/`, run `python3 -m unittest discover -s tests -v`.
Final independent run: **69 tests passed**, including **11 independent QA test methods**; no skips or expected-failure masks. This is a local working-tree result, not CI evidence or a deployed interoperability test. Subsequent changes require appropriate reruns.

The initial independent probes demonstrated real defects before fixes: cyclic supersession was accepted; assessment A could use a rubric only assessing objective B; explicit relations could contradict data references; NaN/Infinity rubric scores passed validation; replay returned a forged accepted receipt; record ID/version conflicts could enter through different packages; malformed stored entries raised uncontrolled key/type errors. All corresponding regression tests now pass. Final follow-up inspected `engine/review.py`, CLI review, local schema URN resolution, OPERATIONS.md and INTEGRATION-PROFILE.md. The declared review transition creates a new reviewed revision, preserves the original and pending rights, and never authenticates or approves delivery. Package objects now resolve the bundled record schema through an offline registry. These behaviors and the documented profile limits agree; no new concrete blocker was found.

The final suite also verifies strict nested shapes, bilingual required fields, version/digest/manifest rejection, immutable accumulation, pending-rights gates, vocabulary drift and Persian search normalization. The temporary pilot failure caused by assuming a direct content-to-assessment edge was resolved using shared objective alignment.

## Acceptance boundaries

| Area | Result and meaning |
|---|---|
| Record and graph validation | PASS locally for tested shapes, references, cycles and objective/rubric alignment; not proof that a claim is true or instruction is sound |
| Exchange integrity | PASS for tested corruption, replay, revision conflict and atomic-store cases; SHA-256 is integrity metadata, not a producer signature |
| Authorization | NOT IMPLEMENTED: caller-supplied local-fixture context is not authenticated identity, tenant authorization or consent |
| Delivery | Quarantine only; even a fixture claiming approved review and verified rights cannot obtain delivery authorization |
| Bilingual semantics | Structurally complete fa/en sample; translation accuracy, terminology equivalence, homonyms and instructional suitability need expert review |
| Contract completeness | Local v0.1 subset: no normative protocol conformance, media manifest delivery, learner-event transport, production rollback of scoring history, accessibility audit or live Content Factory/Learning OS integration established |
| Scientific evidence | No measured learner outcome, causal effect, assessor calibration or inter-rater reliability established |

## Source and rights review

The register contains 29 candidates: 22 marked verified **only for explicitly scoped identity/page facts**, seven still pending. All 29 have pending licensing; none has cleared reuse rights. QA did not independently reopen all 29 sources and does not promote the research agent's page observations to independent verification. Search-indexed facts where direct access failed, live pages without immutable revisions, unknown publication dates and unselected normative versions remain explicit limitations.

QA independently reopened the [ASQ PDCA page](https://asq.org/quality-resources/pdca-cycle) and [Deming Institute PDSA page](https://deming.org/explore/pdsa/) on 2026-11-25. The concise PDCA-stage paraphrase matches ASQ's procedure; the Deming page explicitly distinguishes PDSA from PDCA. Neither establishes this curriculum's effectiveness or reuse permission. The ASQ source record accurately leaves immutable edition and licensing unresolved. A verification label is not a license or scientific-quality rating.

The handover exercise's 12/100 and 5/100 values are synthetic: 12% and 5%, a seven-percentage-point decrease. The proposed 8/8 rubric threshold is unvalidated. Source citations support conceptual provenance, not the fictional scenario's empirical truth. Persian translation and the contextual alias مهندسی نظام آموزشی remain proposed.

G1 requires source/rights review; G2 requires bilingual domain review; G3 remains limited to this offline prototype until trusted adapters and real conformance evidence exist; G4 requires an approved evaluation design and actual evidence; G5 requires owner acceptance. No remaining observed blocker to local prototype use was found after remediation. These gates remain unresolved for operational adoption.
