# Moodle local integration

Issue: [#17](https://github.com/alikhosravi90/Nikway-Academy/issues/17). Candidate only; no merge or release approval.

Moodle: http://localhost:18701/ · Academy: http://localhost:18501/.
Use **Log in with NIKWAY SSO** and the existing private synthetic Academy credentials. The dedicated Moodle administrator credential is in ignored `infra/moodle/runtime/credentials.json`; never paste it into GitHub. Only the two explicitly mapped tenant-A subjects can use this pilot. Moodle is not a shared multi-tenant LMS here.

## Existing installation

Run from this checkout:

```sh
scripts/moodle-compose.sh ps
scripts/moodle-compose.sh stop
scripts/moodle-compose.sh start
scripts/moodle-compose.sh restart
```

The commands affect only project `nikway-academy-moodle`. Do not remove its volumes. The existing baseline project remains separate. In the current workspace, ignored `infra/moodle/runtime` links to the original private runtime in the sibling `moodle-infra` worktree; preserve that worktree until an explicit migration is completed.

## Reproduce in an empty local environment

Prerequisites: Docker Compose, Python 3 with the repository backend dependencies (including jsonschema), curl, GnuPG for recovery, and the separately installed Academy candidate with its private `.env`, synthetic realm and `nikway-academy-content_default` network. Ports 18701/18702 and subnets 10.253.243.0/28 (live) and 10.253.243.16/28 (restore probe) must be available. Do not run a fresh initialization over the existing installation.

```sh
python3 scripts/moodle-init.py
scripts/moodle-compose.sh build
scripts/moodle-compose.sh up -d db moodle
python3 scripts/moodle-install.py
scripts/moodle-connect.sh
scripts/moodle-compose.sh up -d cron
backend/.venv/bin/python infra/moodle/content-import.py \
  content/examples/agent-engineering-basics.fa.json \
  --archive infra/moodle/runtime/imports \
  --container nikway-academy-moodle-moodle-1 \
  --learner 00000000-0000-4000-8000-000000000001 \
  --reviewer 00000000-0000-4000-8000-000000000003
```

The connect step checks or creates only the dedicated OIDC client, connects the Moodle web service to the candidate network, permits the exact current Keycloak private IP through Moodle's outbound policy, and provisions the two subject-bound accounts. Unexpected client/policy drift fails closed. A Keycloak IP change requires reviewing and replacing the old exception; do not globally disable the outbound guard. See [identity boundaries](moodle-auth-decision.md).

To display the Academy launch link, set the following in the private Academy `infra/runtime/.env`, preserving all other values, then run `scripts/local-compose.sh up -d --no-build --no-deps api`:

```dotenv
MOODLE_URL=http://localhost:18701
MOODLE_TENANT_ID=10000000-0000-4000-8000-000000000001
```

## Backup and verification

```sh
scripts/moodle-backup.sh
python3 scripts/moodle-restore-verify.py infra/moodle/runtime/backups/TIMESTAMP
python3 scripts/moodle-restore-probe.py infra/moodle/runtime/backups/TIMESTAMP
```

Keep the private backup passphrase separately. The probe restores database and files to disposable volumes at port 18702, checks data digests and application HTTP, then removes only its own probe resources. It does not replace the live site or certify restored OIDC login. Preserve the original portable JSON archive separately too.

## Scope and acceptance limits

- Academy launch, OIDC login and native Moodle course delivery are operational integration surfaces. Grades, progress, account suspension and Academy membership revocation are **not synchronized**.
- Lesson completion is manual. The dashboard percentage reflects tracked lesson activities; it is not proof of passing the assessment. The sample grade/feedback is an explicitly synthetic integration fixture, not a human educational assessment or certification.
- Original portable package bytes are archived with SHA-256. Derived Moodle pages/assignment/rubric do not replace that source. Character limits are guidance and portable passScore is not automatically enforced.
- HTTP is restricted to loopback and trusted local Docker networks. The selected OIDC plugin's independent JWT signature/issuer/audience validation limitation remains a production gate. No claim of production security or public readiness is made.
- Trivy results cover discovered OS/dependency packages, not a complete Moodle/PHP/plugin advisory or penetration audit. Local tests and hosted Academy CI have distinct scopes.

See `evidence/moodle/`, `evidence/moodle-auth-http.json`, and `infra/moodle/content-*-evidence.json` for execution receipts.
