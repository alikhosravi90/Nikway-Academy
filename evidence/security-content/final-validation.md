# Final candidate validation — 2026-11-25

**PASS for the bounded local checks below; scanner evidence has mixed scopes.** Project`nikway-academy-content`, API18600, UI18501, identity18580. Frozen baseline184xx container IDs, image IDs, and start timestamps stayed unchanged. No baseline restart, database mount, or switch occurred.

## Persistence and encrypted recovery

- Stop/start readiness26.284s; restart readiness17.793s. Every Academy table(12) and9 stable Keycloak identity/configuration tables retained identical canonical row counts andSHA256 values across both transitions.
- Keycloak volatile session/lock tables were excluded only from lifecycle equality. Full encrypted backup/restore covered **every table**: Academy12tables/234rows and Keycloak101tables/1732rows.
- Both AES256-encrypted dumps restored into newly named disposable databases; per-table sortedCOPY data counts/hashes matched the decrypted archives. Disposable databases were dropped by the verifier. Plaintext remained in process memory; passwords, tokens, and database rows were not committed.
- Existing container start was used instead of `local-start.sh --build`, to preserve the exact runtime under test. Independent source-build validation belongs to CI; this lifecycle test does not claim a second clean rebuild.
- First guard check halted before mutations because earlier task text saidAPI18500; current `.env` and Docker mapping both confirmed18600. The explicit guard was corrected and the full test then passed.

## Read samples and resources

50 serial authenticated course reads through nginx:0errors, median7.125ms, p958.224ms, maximum115.453ms.50 health reads:0errors, median2.433ms, p953.265ms. These are local serial samples, not concurrency, throughput, capacity, or learning-quality measurements. Individual container resource samples and exact IDs appear in `final-content-runtime-validation.json`.

## Security evidence boundary

| Running service | Evidence | High / Critical |
|---|---|---|
| API`cbd16a202d4c...` | Exact immutable image scan | 0 / 0 |
| Custom Keycloak`c03a8747a16c...` | Exact immutable image scan | 0 / 0 |
| Frontend`45fd84fa320e...` | Running filesystem export scan | 0 / 0 |
| PostgreSQL`38134cd212d8...` | Running filesystem export scan | 0 / 0 |

**Do not describe this as four exact-image scans.** Docker could no longer inspect the historical frontend/PostgreSQL imageIDs used by the running containers. Their current local tags pointed elsewhere (frontend`ec038f19...`, PostgreSQL`e7bc399b...`). The coordinator chose to preserve the already-tested running containers. No newer tag was substituted as scan evidence. Cause of tag replacement/historical image unavailability is not established by this investigation; labels identify the frontend tag as contentCompose, but do not identify the actor.

For the two fallback scans, `docker export` captured running filesystems without mounted data volumes. Extraction included regular files and directories, did not follow symlinks/devices, and retained package metadata. Trivy scanned OS/language vulnerabilities with no suppressions. Container/image/start identities were identical before and after export. These scans do not cover image-layer provenance, unavailable manifests, mounted database contents, or application logic. Exact receipts: `final-content-images.json` and `final-content-rootfs.json`.

Trivy0.76.2 used the recorded2026-11-25 database snapshot. ZeroHigh/Critical does not prove absence of unknown vulnerabilities or future advisories. Keycloak remains a **locally maintained source/dependency build, not vendor-supported**; upstream integration tests were skipped. See `custom-maintenance-licenses.md` for changed-component license provenance. Parent-owned Academy/browser/content acceptance and CI are distinct gates; no production or merge approval is implied here.
