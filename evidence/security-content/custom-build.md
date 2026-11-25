# Locally maintained Keycloak remediation candidate

**Candidate image scan: PASS0High/0Critical. Production/vendor support: not established.** Frozen official baseline unchanged. This candidate is a locally maintained source/dependency build, not an official Keycloak release.

- Image tag `nikway-keycloak-custom:26.8.2-guava33.7.2`; image/manifestID `sha256:c03a8747a16c11dcba0ecdc04ecd8c87e1ae5a7342b1ee4e10f8db70292182da`.
- Source: official26.8.2 archive, SHA256`686c4cf4d9cf5fe0b516fd5c7b8f74cdb980990ee5181e944560df4296e3037f`.
- Builder: Maven image digest`308cba8b638ed7e4658cea3f8399066219466211c805f6d5728c3c9c7614661b`, isolated3GiB/2CPU.
- Change: rootPOM dependencyManagement selects upstreamGuava33.7.2-jre. Quarkus regenerates its application, then official distribution assembly creates the complete archive. No prebuiltJAR was swapped into the official image.
- Runtime: Temurin21.0.13.1+2 Alpine digest`5d7689f47d670aca766b9503a70bccc2d73b4eb9221ae8f714ae958313c4ce70`, Bash5.3.9-r1. NSS/sqlite RHEL packages are absent because the runtime distribution is replaced, not because scanner metadata was deleted.
- Mavenserver+dist result: BUILD SUCCESS,7m57s reported, within600s external limit. Upstream tests explicitly skipped; security/browser acceptance is a separate gate.
- Maven warned about Quarkusdevelopment dependencies. The official image also contains the same named health/openapi/assistant developmentJARs; this warning alone is not newly introduced exposure. Full image scan includes deployedJARs.
- Actual full scan: `keycloak-custom-scan.json`; original6findings absent, no ignores/suppressions. ScanDB freshness and scope described in root-cause report.

Two reproducible routes are provided:

1. `./infra/identity/build-custom-keycloak.sh`: tested source compilation and subsequent packaging sequence, with local ignored Mavencache. This is the route used for the evaluated image.
2. `docker build -f infra/identity/Dockerfile.keycloak-source -t nikway-keycloak-custom:26.8.2-guava33.7.2 infra/identity`: self-contained multistage recipe with source checksum and pinned builder/runtime. This equivalent consolidated recipe has not been separately rebuilt end-to-end; it does not depend on committed binary artifacts.

The original official image plus patchedJRE-only experiment is recorded separately:1High/0Critical, Guava still affected, and byte-equivalence proof for entire`/opt/keycloak`. Its three-user signed-token/PKCE probe passed. It must not be substituted for the fully rebuilt image.

No baseline Compose change or database migration performed by this agent. Root owns content-project-only switch after logical backup, full Academy authorization/browser/content regression, final backup/restore and image identity verification. Keep the original184xx baseline untouched. No production approval follows from a clean scanner result.

First-start defect and remediation: the assembled archive did not precreate`/opt/keycloak/data`; binding the import file caused Docker to create a root-owned parent, and the nonroot process hit`AccessDeniedException: /opt/keycloak/data/h2`. Both customDockerfiles now explicitly create`data/import` and set ownership1000:1000 before switchingUSER. The affected disposable container was removed and the final image rebuilt/rescanned. This was isolated from all Academy databases. The original intermediateimage9f8dcfe is superseded.

Final corrected image acceptance: all3synthetic users passed real S256 authorization-code login and RS256 signature/issuer/audience/fixedUUID validation; wrong-verifier and missing-PKCE requests rejected. UID1000 and writabledata observed. Exact rootCompose Bash`/dev/tcp/localhost/9000` readiness probe passed. Idle memory547.6MiB under1536MiB limit. These are H2 isolated checks; root must still run PostgreSQL-backed Academy regression. Receipt:`keycloak-custom-pkce.json`.
