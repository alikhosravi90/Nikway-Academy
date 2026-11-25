# Local image security refresh

Status: **PARTIAL / release NO-GO**. Trivy 0.76.2, current downloaded vulnerability and Java databases; candidate image IDs, database timestamps, coverage and package findings are in `vulnerability-refresh.json`. Final running-container image IDs and matching rescan results are in `final-running-images.json` and the table below. Counts are package/vulnerability matches, not distinct CVEs. Zero HIGH/CRITICAL findings is bounded scanner evidence, not a security certification.

| Final running component | Image ID | HIGH | CRITICAL |
|---|---|---:|---:|
| API, Python 3.12 Alpine with pinned Kerberos patch | `f137537717f0949a5e64b55d5ed9432f83143703b1cd7bb53ed8818f65b26d52` | 0 | 0 |
| Frontend, refreshed nginx Alpine | `769f40a9729dcdc6beb409b55ec0203dd7cc7210b409db302f636937263978f1` | 0 | 0 |
| PostgreSQL 16 Alpine, patched libxml2 and distro su-exec | `dd44c4c2bfcb4cbcb4dccbc86070687701c5990d152f5a7a947b286bccef49a5` | 0 | 0 |
| Keycloak 26.8.2 | `7e66a96e4739239070aeaf72e4c5decf0f7f682cfc725b9f7ea2b336eaba38b3` | 6 | 0 |

The Keycloak scan includes OS packages and Java dependencies. One HIGH finding has a listed fixed version: Guava 33.6.0-jre → 33.7.2; five HIGH vendor findings have no listed fix. Keep local synthetic validation separate from release readiness; use a supported patched Keycloak image when available, then rescan and repeat identity tests. No unsupported JAR replacement or CVE suppression is included.

Initial cached-image findings were API 126 HIGH/6 CRITICAL, frontend 77/8, PostgreSQL 156/2, Keycloak 11/1. Refreshing same-version Debian tags left substantial findings. The selected Alpine Python runtime requires actual musl-wheel compatibility and backend tests; the PostgreSQL distribution change requires logical migration into a separate volume, never reusing raw Debian database files. The original database volume remains intact.

One initial PostgreSQL mitigation replaced gosu with a symlink but the layer scanner retained its old path findings. The final derived image removes both gosu and its alias, changes the entrypoint invocation directly to distro su-exec, and scans without HIGH/CRITICAL matches. No vulnerability exclusions are configured.
