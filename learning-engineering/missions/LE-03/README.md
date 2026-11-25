# LE-03 — real-module integration, isolated draft

**PARTIAL.** The offline three-codebase path is executable and tested. It is not an authenticated, deployed three-service integration. No learner, service, database, account, secret, runtime directory or publication endpoint is used.

## Actual path

1. Learning Engineering `engine.exchange.build_package` validates the existing ten PDCA records and constructs a checksummed 0.1.0 envelope.
2. This mission's adapter authors an explicitly new original synthetic draft around that specification. Content Factory's actual `ComponentInput` validates it, and actual `cf.render.build_package` produces learner Markdown/HTML/quiz. The answer and explanation are absent from the learner quiz.
3. The adapter checks actual rendition checksums, maps the rendered Markdown and a proposed human rubric into Academy's portable draft package, and runs Academy's actual `content.validate_package.load_package`. No validator or engine implementation is copied into adapter logic or mocked.

These are selected real production-source functions, not the whole engines. CF Repository/database transaction gates and Academy authenticated admission/publish code are not invoked. Academy's concrete consumer implementation exists at `backend/app/content_api.py` in the pinned content-integration branch. Its `/api/content-packages` admission requires authenticated reviewer context and PostgreSQL; this harness stops before it.

## Exact code receipts

| Source | Pinned commit |
|---|---|
| Learning Engineering | `3ff3f5df28d3f39968e42ba583b61e2a1dcf1b1b` |
| Content Factory | `32423ee7963a213fc5ecd89457d42a1c63491385` |
| Academy content-integration | `7364427aee7e69ff2e872e66bafb8df129faeaad` |

`snapshot.py` exports only named tracked code/schema/record paths from these exact commits. `.snapshots/` and the local `.venv/` are ignored. `evidence/sources.json` records repository paths, observed heads, archive hashes and individual file hashes. Other Academy heads were inspected read-only: repository `c8b3a1513b011f94b7565abc43ffb0efb019a4d5`, release `7be59d794a7e73cdb32b7fd222f63473e83d815c`, integration `3c59b6e3453530988fb44f425ddeb277b0c47921`. The content-integration branch was selected because it has the actual portable-package consumer.

## Reproduce

From this directory, with Python 3.14 (the observed interpreter):

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-lock.txt
.venv/bin/python snapshot.py
.venv/bin/python -m unittest -v test_bridge
.venv/bin/python bridge.py
```

The current repository must contain all three pinned commits (they are branches of the same Git repository). `LE03_SOURCE_REPO` can override that repository path. Existing `.snapshots/` directories are refused; use a fresh mission checkout or explicitly remove only the generated mission snapshot directory before re-exporting. No source checkout path is hardcoded. Dependencies are installed only in the mission venv. Runtime tests do not access the network. `bridge.py` writes a nested evidence receipt, not an upload request. Keep the receipt and its blockers together; extracting its nested Academy draft does not authorize import or publication.

## Results and boundaries

Ten tests pass, including actual three-module traversal, LE digest mutation, CF rendition tampering, question/outcome mismatch, raw CF incompatibility and Academy checksum/unknown-field failures. TDD receipts preserve the initial missing-adapter failure and the demonstrated rendition-tamper failure before the checksum fix. The initial red test failed because the new module did not exist; later runtime contract errors were corrected by using lowercase package IDs and a SemVer revision string.

The bridge rejects any different source payload digest, even when the changed package is validly re-digested. It supports only the exact pinned PDCA package, not arbitrary source revisions. Academy `createdAt` records the actual UTC execution time, so the Academy package digest changes per run.

The LE envelope, CF component/ZIP and Academy JSON are incompatible wire contracts. This adapter is deliberately limited to the pinned PDCA draft; it is not a general semantic translator. It adds new, unreviewed instructional prose and a formative question, and retains original pending-rights records in the evidence receipt. It does not relabel those original records as approved or licensed.

| Remaining gap | Owner/action |
|---|---|
| LE original rights are pending; new draft isn't approved | Rights/content owner reviews source and derivative scope before use beyond local testing |
| Semantic mapping is proposed | Learning Engineering + CF + Academy owners approve a versioned mapping, especially competency IDs and immutable source references absent from Academy wire schema |
| LE 500-word bound differs from Academy character bounds | Assessment owner defines and verifies word-count behavior; current human review instruction only |
| Accessibility remains untested | Accessibility reviewer tests authored renditions; false booleans are not failures from an executed audit |
| Authenticated import and PostgreSQL gates untested | Separate isolated DB/service integration with trusted identities and rejection tests; do not reuse production data |
| No learner delivery or learning-effectiveness evidence | Authorized pilot with appropriate evidence and approvals |

`promotionAllowed=false` is an evidence statement in this offline tool, not an enforced authorization gate in Academy. No claim that an external caller cannot remove it is made. The existing Academy authorization checks remain outside this run's evidence boundary.

## CI recipe

Use checkout with full history, or fetch the pinned commits explicitly into the current repository. A fresh job has no `.snapshots/` directory. From repository root:

```sh
git fetch origin 3ff3f5df28d3f39968e42ba583b61e2a1dcf1b1b 32423ee7963a213fc5ecd89457d42a1c63491385 7364427aee7e69ff2e872e66bafb8df129faeaad
export LE03_SOURCE_REPO="$PWD"
cd learning-engineering/missions/LE-03
python3 -m venv .venv
.venv/bin/pip install -r requirements-lock.txt
.venv/bin/python snapshot.py
.venv/bin/python -m unittest -v test_bridge
.venv/bin/python bridge.py
```

No sibling worktree is required. Missing commits cause the snapshot step to fail rather than substitute another revision. Reusing a partial or stale snapshot directory also fails. CI should upload its generated receipt separately from the checked-in local evidence.
