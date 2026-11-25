# Identity security investigation — 2026-11-25

**Frozen official baseline: NO-GO remains. Vendor-supported zero-High/Critical replacement: not established. A locally maintained source-build candidate now scans0High/0Critical; see `custom-build.md` and its separate acceptance receipts.** Baseline `3c59b6e3453530988fb44f425ddeb277b0c47921` and its running services/databases were preserved. No vulnerability suppressions, metadata deletion, JAR substitution, signup, purchase, or release occurred.

## Six findings in the official Keycloak image

Image `quay.io/keycloak/keycloak@sha256:7e66a96e4739239070aeaf72e4c5decf0f7f682cfc725b9f7ea2b336eaba38b3` contains Keycloak26.8.2. Full OS/JAR scan reproduced6High/0Critical. Exact package identifiers and advisory sources are in `keycloak-scan.json`. The long CVE identifiers are genuine vendor/upstream records; length is not grounds to dismiss them.

| Finding | Root cause and observed evidence | Supported fix / present boundary |
|---|---|---|
| CVE-2026-91403 | Java certificate distrust issue. Red Hat OpenJDK uses system trust rather than shipping an independent trust store. Current RPM21.0.13.1.2 and ca-certificates2026.2.92_v9.0.319-90.3.el9_8. | Red Hat tracks complete root removal under CVE-2026-114406/114820, rather than an OpenJDKRPM fix for91403. Public `keytool -list -v -cacerts` showed neither Comodo AAA Services nor emSign ECC RootCA-G3 subjects. This is evidence of distrust, **not a scanner exception or claim that the6finding gate passed**. |
| CVE-2026-119373 | SQLite FTS5 prefix doclist merge/detail=none handling with negative rowids. Installed sqlite-libs3.34.1-11.el9_8. | Upstream fixed3.54.0. No fixed RHEL9 package reported by current scanner. |
| CVE-2026-119374 | SQLite FTS5 secure-delete reads crafted corrupt footer offsets. | Upstream fixed3.54.0; same unresolved RHEL9 package. |
| CVE-2026-119379 | SQLite session changeset apply mishandles crafted repeated table with larger column count. | Upstream fixed3.54.0; same unresolved RHEL9 package. |
| CVE-2026-119586 | SQLite CLI `.recover` output piped into a second CLI can execute malicious dotcommands. Upstream explicitly distinguishes this from a core library bug. `/usr/bin/sqlite3` absent in image. | CLI applicability differs from package-level detection. No waiver applied; raw finding retained. |
| CVE-2026-102554 | Guava33.6.0-jre native Java deserialization eagerly allocates attacker-requested capacity in affected collection classes. | Upstream fixes33.7.2. Official latestKeycloak26.8.2 still bundles33.6.0. No vendor-issued compatible fixed Keycloak release found. Normal OIDC JSON is not itself proof of a Java serialization exploit path. |

SQLite is a real transitive dependency of `nss-softokn` (NSS), so deleting its library or package metadata is not a justified repair. PostgreSQL is Academy's application/identity database, but that fact alone does not prove every NSS/SQLite path unreachable. No exploit reachability proof is claimed.

The current OpenJDK reports21.0.13.1, the fixed version for the separate Java4ShellCVE-2026-114938. Keycloak's official November19 update says image26.8.2-3 carries this fix. It does not fix the Guava finding. Container tag alone is insufficient; this investigation checked actual Java runtime output.

## Official source receipts

Read2026-11-25; summaries above are paraphrases.

- [Red Hat CVE-2026-91403](https://access.redhat.com/security/cve/cve-2026-91403): system-CA integration and follow-up remediation distinction.
- [Red Hat certificate distrust bulletin](https://access.redhat.com/security/vulnerabilities/RHSB-2026-012): affected roots and trust-store remediation.
- [SQLite upstream CVE catalogue](https://www.sqlite.org/cves.html): exact119373/119374/119379 fixes and119586 CLI-only explanation.
- [Google Guava advisory](https://github.com/google/guava/security/advisories/GHSA-xxph-c9ww-hj94): affected classes and fixed33.7.2.
- [Google Guava release33.7.2](https://github.com/google/guava/releases/tag/v33.7.2): upstream code-fix release.
- [Keycloak downloads](https://www.keycloak.org/downloads): current stable26.8.2.
- [Keycloak supported configurations](https://www.keycloak.org/server/supported-configurations): supportedJava runtime constraints.
- [Keycloak Java4Shell bulletin](https://www.keycloak.org/2026/11/java4shell-vulnerability-cve-2026-114938): updated image/runtime and effective-runtime verification requirements.
- [Official container customizations](https://www.keycloak.org/server/containers): customization is possible, but does not make a hand-patched dependency a vendor-released fix.

Red Hat JSON API requests returnedHTTP403 (separate receipt); browser-readable primary advisories were available. API failures are not interpreted as absence of a vulnerability. Scanner DB timestamp is2026-11-25T07:11:44.18325427Z; JavaDB timestamp2026-11-25T00:58:20Z. Scan used the existing verified official Trivy0.76.2 binary/cache, `--skip-db-update --skip-java-db-update`, full OS/language analysis, no ignore-unfixed or severity exclusions before receipt extraction.

## Alternatives investigated

1. **New official Keycloak patch:** no newer stable release found. Replacing only Java/base packages leaves Guava unresolved. Native serialization filtering could mitigate affected classes but is not a fixed dependency and can affect compatibility; not presented as a repair. Unsupported JAR surgery was rejected.
2. **Chainguard-maintained Keycloak distribution:** anonymous manifest fetch of `cgr.dev/chainguard/keycloak:latest` returnedFORBIDDEN. [Registry documentation](https://www.chainguard.dev/docs/chainguard/containers/registry) distinguishes public images from authenticated catalogue access. Not operationally tested, no account/purchase/contact made; therefore UNKNOWN compatibility/security and no recommended migration.
3. **Dex official2.46.1 operational benchmark:** image digest and exact scan are recorded. Disposable256MiB/0.5CPU container, loopback18680, explicit isolated10.253.243.0/28, memory storage, random synthetic password. S256 authorization-code exchange succeeded; wrong verifier and missingPKCE were rejected. JWTaccess-token audience=`academy-web`, subject is notUUID, so it fails Academy's current API identity contract. Observed idle8.145MiB, one login414.16ms; this is not throughput/load evidence. Scan found28High/0Critical across OS andGo packages, so adoption worsens the current gate. No persistent storage/recovery/account-management benchmark claimed. Container and network removed afterward.

[Dex local connector](https://dexidp.io/docs/connectors/local/), [Dex configuration source at tested tag](https://github.com/dexidp/dex/blob/v2.46.1/config.yaml.dist), and [Dex official image](https://github.com/dexidp/dex/pkgs/container/dex) support reproducibility. Dex migration would require a trusted issuer+subject mapping instead of fixedUUID assumptions, deliberate API audience configuration, identity/password migration, persistent storage/backups, session/logout review, and complete authorization/browser regression. It is not a drop-in replacement. Existing memberships must never be reassigned merely from matching username/email.

## Decision and next action

Follow-up custom-build experiment: exact official26.8.2 source was rebuilt with fixedGuava33.7.2-jre and packaged on patchedTemurin21.0.13.1 Alpine. Fullimage scan reports0High/0Critical without suppressions. This is locally maintained, not vendor-supported; full Academy regression and content-project switch are parent-owned gates. The frozen official baseline status does not change.


Keep the frozen local baseline classifiedNO-GO for release. A supportedKeycloak build containing fixedGuava plus repaired/removed-by-vendor SQLite exposure is the lowest migration-cost path. Re-evaluate exact immutable image with fresh full scannerDB, PKCE negative tests, tenant/role/self-review regression, backup/restore, and browser logout before switching any runtime. If no such build is available, maintaining a patched-source distribution requires explicit ownership and regression scope; this investigation does not silently assume that responsibility or claim completion.
