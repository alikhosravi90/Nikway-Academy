# LE-05 independent QA

Date: 2026-11-25. Baseline: `3ff3f5df28d3f39968e42ba583b61e2a1dcf1b1b`.
Reviewer: separate AI QA agent, not an independent human approver.

**PARTIAL — local structure and bounded offline behavior verified. Human/content rights, scientific approval, actual delivery and educational effectiveness remain unproven.** No merge, deployment, recruitment, participant collection or permission issuance is authorized by this report.

## Findings and regression evidence

1. **CI false-positive delivery denial (material).** The initial workflow accepted any nonzero exit from `engine.cli ... --delivery`, including import errors, crashes or a missing interpreter. That did not demonstrate a rights/review denial. Required correction: require exit 1, valid structured JSON with status FAIL and both rights/review categories, rejecting malformed output and unrelated failure.
2. **CI empty-dataset claim not asserted (material).** The initial workflow merely executed the analyzer. A successful process producing a fabricated effect would pass. Required correction: assert NO_DATA, zero participant and paired counts, null paired effect and expected exit.
3. **Integration not initially covered by CI.** Core unittest discovery does not include `missions/LE-03/test_bridge.py`; a separate pinned-source job is needed. Local execution establishes only local evidence.

Initial core suite: 77/77 PASS. Five additional mission regressions: full suite 82/82 PASS. Added two CI-helper regressions and observed RED (two failures for absent helper; other five mission tests PASS) before the implementation. Final retest status is recorded below after fixes.

## Reviewed proof boundaries

- **LE-01:** all 29 dossiers retain `rightsClearedForIntendedUse=false`. Conditional reuse labels are accompanied by scope, attribution, exceptions and owner-decision requirements. Source copyright/permission does not grant rights to an independently generated lesson; generated material is also not thereby approved. No legal correctness determination or fresh remote terms audit was performed by this QA agent.
- **LE-02:** review receipt explicitly identifies AI reviewer, `humanApproval=null`, proposed revisions not applied. All recorded source-file hashes matched current files in the independent regression. Scientific and bilingual recommendations remain proposals; no psychometric evidence or human approval is established.
- **LE-03:** seven initial local real-module tests passed, including altered digest/rendition rejection, objective-binding failure and Academy shape/checksum rejection. `promotionAllowed=false`, draft lifecycle and blockers remain in the receipt. This flag is a report statement, not trusted enforcement at Academy admission. New synthetic learner text is authored by the adapter; the source record is not an approved instructional source. CF transaction/database gates, Academy authenticated admission and publish paths are outside coverage. A checksum detects accidental alteration against a manifest, not trusted authorship or rights.
- **LE-04:** strict known fields, complete four-criterion scores, integer 0..2, duplicate participant/phase rejection and explicitly null unpaired effect were exercised. Empty data produce NO_DATA. Additional malformed row/phase/score shapes are rejected. Transfer count is not transfer success. Declared observed/deidentified status never proves consent, identity, source authenticity or human review. No pilot observations were collected. Resource-exhaustion behavior and arbitrary-size input are not claimed tested.
- **Workflow:** workflow definition review is not evidence of a hosted run. Current-SHA remote CI must be separately checked by the parent; this report does not mark GitHub CI PASS.

## Final retest

After the CI-helper and integration hardening changes:

- `python3 -m unittest discover -s tests -v`: **84/84 PASS**, including seven independent mission QA regressions.
- `missions/LE-03/.venv/bin/python -m unittest discover -s missions/LE-03 -p 'test_bridge.py' -v`: **10/10 PASS**. New cases cover validly re-digested unsupported source rejection, execution-time provenance and fresh-destination snapshot export.
- `python3 missions/LE-05/ci_gates.py`: **PASS**, explicitly verified expected delivery denial and absent learner data.
- Reviewed helper rejects crashes, malformed JSON, empty or nonstring errors, missing rights/review categories, nonzero analyzer exit and fabricated empty-dataset effects. Workflow now invokes this helper. Findings 1 and 2 are locally resolved.
- Finding 3 remains pending the parent adding/verifying the separate remote integration job; no hosted run is claimed here.

These commands ran against the shared uncommitted mission changes on 2026-11-25. The exact committed SHA and hosted result are a separate parent receipt. No human sign-off is substituted by automated tests or this independent AI review.
