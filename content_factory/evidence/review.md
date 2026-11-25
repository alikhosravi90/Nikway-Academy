# Independent code review and disposition

2026-11-25. Read-only fresh reviewer `/root/content_factory_review`; no runtime/credential access or edits by reviewer. Reviewed current implementation against the approved architecture and implementation plan. Database tests were run by the implementer, not independently rerun by reviewer.

## Consequential finding fixed

P2: LocalConsumer.deliver did not bind fetched manifest.id to requested candidate ID. A routing mix-up could return a different consistent package. Regression `test_delivery_rejects_wrong_candidate_from_routing_mixup` reproduced the failure (`review-fix-red.log`); explicit ID check added. Final full suite: 24 passed (see tests.xml/full-suite.log).

## Deferred minors

- Snapshot/object tamper rejection branches in recovery are implemented but lack dedicated negative tests; do not claim those paths tested. Restore, missing objects, nonempty target and orphan reporting do have tests.
- Renderer attribution assumes synthetic authored material; document that limitation and keep real external corpus out of this MVP. Proper source-specific attribution is required before expanding scope.

## Reviewer declined-to-judge / executor rulings

Production federation, real Learning OS compatibility, licensing correctness, pedagogy/accessibility certification, operational backup durability/RPO/RTO and runtime results were outside the reviewer's read-only static evidence. Ruling: do not infer any of these from code review. Record local runtime evidence separately; keep human, external integration and production gates partial/open. Cost if wrong: inappropriate expansion of a local synthetic pilot; production remains NO-GO.

## Implementation rulings

- Reused existing isolated worktree and new branch; no additional checkout or merging. Cost if wrong: branch recovery complexity; original branch pointer is retained at c861651.
- Filesystem object adapter and opaque local credentials implement the bounded local profile. Cost: S3 durability/OIDC interoperability remain unproven and require separate integration work.
- Automated synthetic reviewer demonstrates controls only, never human content approval. Cost: human editorial work still required.
- Discovered shared uv cache corruption; reinstalled locked dependencies into this local venv using a task-local cache without altering shared cache contents. Cost: extra local disk usage only.
- Failure injection found cross-transaction pipeline state; made revision/candidate changes share the pipeline transaction. Adversarial package test found unbound rendition hashes; bound them into immutable candidate manifests. Both have failing-then-passing test evidence.
