# Portable package → Moodle pilot adapter

Operator-only CLI for the isolated Moodle 5.3.1 pilot. No production, external publication, authoring UI, or Academy/Moodle completion/grade synchronization is implied.

`content-import.py` imports the existing strict Python validator before any Docker call or archive write. It preserves the original UTF-8 bytes in an operator-selected private archive named by SHA-256; Moodle receives derived escaped text, not an alternative canonical package. Export the preserved archive file to recover the exact original. Do not use a Moodle course backup as a portable-package export.

After infrastructure installation and explicit coordination:

```sh
python3 infra/moodle/content-import.py content/examples/agent-engineering-basics.fa.json \
  --archive infra/runtime/moodle-content-originals \
  --container EXPLICIT_ISOLATED_MOODLE_CONTAINER \
  --learner 00000000-0000-4000-8000-000000000001 \
  --reviewer 00000000-0000-4000-8000-000000000003
```

The synthetic accounts must already exist through the coordinated identity bootstrap/login. The adapter does not create accounts or grant site administration. Explicit learner enrolment uses the core student role; reviewer uses non-editing teacher. Moodle usernames are the immutable OIDC subject UUIDs. Only tenant-A learner subject `00000000-0000-4000-8000-000000000001` can receive student enrolment and only tenant-A reviewer subject `00000000-0000-4000-8000-000000000003` can receive teacher enrolment. Cross-role assignment, old display usernames, and tenant-B subject ending `002` are rejected in both wrapper and PHP before course mutation. This is a bounded pilot identity mapping, not an arbitrary federated identity policy.

A package/version gets one course idnumber. An advisory lock and delegated DB transaction guard concurrent imports. Matching original bytes reuse the course and idempotently enrol requested identities. Different bytes under the same package/version fail closed; existing activity/grading changes are never overwritten. Operators must inspect a drifted Moodle course separately; matching import receipts do not claim ongoing content reconciliation.

Native content: three Page activities containing lesson text, mapped objectives, and practice instructions; one online-text Assignment; native ready human rubric with all criterion anchors. Plain package text is escaped before HTML rendering. Manual lesson completion and Moodle assignment states remain Moodle-native. The portable character-count minimum/maximum are displayed guidance only, because Moodle's native word limit is not equivalent. Portable passScore is not asserted as an automatically enforced threshold. There is no automatic grading or status transfer to Academy.

Implementation uses Moodle core `create_course`, `course_create_sections_if_missing`, `add_moduleinfo`, `enrol_manual::enrol_user`, and grading manager/rubric controller APIs. API references verified against official MOODLE_503_STABLE sources:

- https://github.com/moodle/moodle/blob/MOODLE_503_STABLE/public/course/modlib.php
- https://github.com/moodle/moodle/blob/MOODLE_503_STABLE/public/grade/grading/form/rubric/lib.php
- https://github.com/moodle/moodle/blob/MOODLE_503_STABLE/public/grade/grading/form/rubric/tests/generator/rubric.php
- https://github.com/moodle/moodle/blob/MOODLE_503_STABLE/public/grade/grading/tests/generator/lib.php

The PHP CLI is a privileged internal adapter, not an untrusted admission endpoint. Invoke only through the validator wrapper; no web route is installed. Runtime import, idempotency and browser learner/reviewer validation remain required before claiming operational PASS.

Provider binding is rechecked immediately before every enrolment: auth `oidc`, exact local `mnethostid`, exact `keycloak:academy:<sub>` idnumber, matching username, and neither deleted nor suspended. Pure PHP fixture tests reject each mismatched field independently; read-only runtime validation confirms both configured synthetic identities satisfy the guard.
