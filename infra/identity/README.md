# Isolated identity experiments

These are candidate evaluation tools, not a replacement for root Compose. All synthetic credentials stay in ignored `infra/runtime/`; no baseline database is mounted. Current outcome and limitations: `evidence/security-content/identity-root-cause.md`.

## Dex benchmark

Requires Python3 with bcrypt, Docker, and free loopback18680/subnet10.253.243.0/28. Verify the subnet against existing networks first. Run from repository root:

```sh
python3 infra/identity/dex-benchmark-setup.py
docker network create --subnet 10.253.243.0/28 nikway-identity-experiment
docker run -d --name nikway-dex-benchmark \
 --network nikway-identity-experiment --memory 256m --cpus 0.5 --pids-limit 100 \
 --security-opt no-new-privileges --cap-drop ALL -p 127.0.0.1:18680:5556 \
 -v "$PWD/infra/runtime/dex-benchmark/config.json:/etc/dex/config.json:ro" \
 ghcr.io/dexidp/dex@sha256:65b72ca0f4b0bf6d4ada84ec21da8851782563404ac7b8f926923d27ceced9ab \
 dex serve /etc/dex/config.json
python3 infra/identity/dex-benchmark.py
docker rm -f nikway-dex-benchmark
docker network rm nikway-identity-experiment
```

The probe performs real synthetic PKCE HTTP flows. It inspects token payload shape only; it does not claim signature-verification or backend authorization regression. First negative probe needed a redirect interceptor to observe OAuth error instead of following callback to an intentionally absent frontend; corrected probe passed. Memory storage loses all sessions/keys on stop, by design for this disposable benchmark.

## Custom Keycloak source-build feasibility

`./infra/identity/build-custom-keycloak.sh` downloads exact26.8.2 source (SHA256 checked), adds a dependencyManagement override for upstream fixedGuava33.7.2-jre, and runs bounded600s Mavenserver+dist package generation. Source/modules and Maven cache are ignored runtime files. Builder has3GiB/2CPU limits. Tests are skipped for compilation feasibility only. Maven rebuilding the distribution is distinct from substituting a JAR in an already assembled Quarkus application. This is a locally maintained fork, not vendor-supported remediation.

`Dockerfile.keycloak-custom` requires a build context containing the **successfully rebuilt and extracted** distribution at `keycloak/`; it must not be supplied the unmodified official distribution. Java21 base and Bash version are pinned. A successful compile would still require complete image scan, startup, PKCE negative tests, persistence/restore, and Academy security/browser tests before any runtime-switch proposal. Base-only scan does not pass the full-image gate.

The complete multistage source recipe is `Dockerfile.keycloak-source`; it pins the archive checksum and all container inputs. The evaluated image was produced by the bounded source-build and artifact-packaging sequence. The consolidated Dockerfile has not been separately run end-to-end. Both paths include the verified UID1000 writable-data fix.

`KEYCLOAK_EVALUATION_VARIANT=custom python3 infra/identity/keycloak-pkce-evaluation.py` verifies actualRS256 signatures, issuer, audience, fixed subjects for3synthetic identities, wrong-verifier rejection, and missing-PKCE rejection against18680. Generate its realm by copying `scripts/local-init.py` into an ignored isolatedroot (`infra/runtime/keycloak-evaluation/scripts/`), running that copy, and changing its realm redirect/web origin to18601. Start only the candidate container on a separately checked network/subnet, with its generated realm mounted read-only and `KC_HOSTNAME=http://localhost:18680`, `KC_HEALTH_ENABLED=true`. This H2 benchmark is not a PostgreSQL migration or production test.
