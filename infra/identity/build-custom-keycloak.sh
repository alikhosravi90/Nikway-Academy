#!/usr/bin/env bash
# Experimental locally maintained distribution; not an official Keycloak image.
set -euo pipefail
root=$(cd "$(dirname "$0")/../.." && pwd)
cd "$root"
mkdir -p infra/runtime/keycloak-source infra/runtime/maven-cache
python3 - <<'PY'
import pathlib,urllib.request,hashlib,tarfile
p=pathlib.Path('infra/runtime/keycloak-26.8.2.tar.gz')
if not p.exists():urllib.request.urlretrieve('https://github.com/keycloak/keycloak/archive/refs/tags/26.8.2.tar.gz',p)
assert hashlib.sha256(p.read_bytes()).hexdigest()=='686c4cf4d9cf5fe0b516fd5c7b8f74cdb980990ee5181e944560df4296e3037f'
source=pathlib.Path('infra/runtime/keycloak-source/keycloak-26.8.2')
if not source.exists():
 with tarfile.open(p) as t:t.extractall(source.parent,filter='data')
pom=source/'pom.xml';s=pom.read_text()
marker='<!-- Local maintained build: upstream Guava CVE-2026-102554 fixed release. -->'
if marker not in s:
 needle='<dependencyManagement>\n\n        <dependencies>'
 assert needle in s
 s=s.replace(needle,needle+'\n            '+marker+'\n            <dependency><groupId>com.google.guava</groupId><artifactId>guava</artifactId><version>33.7.2-jre</version></dependency>',1)
 pom.write_text(s)
PY
# Timeout bounds this feasibility run; stop only this named build container on exit.
trap 'docker stop -t 5 nikway-keycloak-source-build >/dev/null 2>&1 || true' EXIT
timeout 600 docker run --rm --name nikway-keycloak-source-build --memory 3g --cpus 2 --pids-limit 300 \
 -v "$root/infra/runtime/keycloak-source/keycloak-26.8.2:/src" \
 -v "$root/infra/runtime/maven-cache:/root/.m2" -w /src \
 maven@sha256:308cba8b638ed7e4658cea3f8399066219466211c805f6d5728c3c9c7614661b \
 mvn -B -ntp -pl quarkus/server,quarkus/dist -DskipTests -Dmaven.test.skip=true package
# Tests deliberately omitted from feasibility compilation; no release approval implied.
context=$(mktemp -d "$root/infra/runtime/keycloak-custom-context.XXXXXX")
mkdir "$context/keycloak"
tar -xzf "$root/infra/runtime/keycloak-source/keycloak-26.8.2/quarkus/dist/target/keycloak-26.8.2.tar.gz" -C "$context/keycloak" --strip-components=1
docker build -f "$root/infra/identity/Dockerfile.keycloak-custom" \
 -t nikway-keycloak-custom:26.8.2-guava33.7.2 "$context"
