# Tasks and acceptance

The canonical task list, dependencies, owners and acceptance criteria are in ../../missions/local-mvp/manifest.json. No task is accepted by creating this document. Each implementation must add evidence and receive independent review before its mission is accepted.

Run `python3 scripts/validate_missions.py` for structural and acceptance gates. Run `python3 scripts/validate_missions.py --self-test` for deliberate negative fixtures. Runtime security and user journey tests remain separate gates.
