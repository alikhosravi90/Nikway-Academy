# Codex workspace operating model

GitHub is the versioned source of truth; existing local Codex workspace is the execution environment. Recover the actual workspace path before writing. Use separate Git worktrees for independent missions, scoped branches and explicit ownership; coordinate shared contracts before parallel changes.

Recommended directories: architecture/, governance/, contracts/, schemas/, templates/, missions/, evidence/, runtime/. Keep runtime secrets, credentials, databases and local configuration out of public Git. AGENTS.md should describe common instructions after checking existing instructions and obtaining review. Do not overwrite existing local assets. Use local-first, cloud-ready deployment; no purchases or public deployment.

Each mission uses the shared template, mission-specific specification, plan, tasks, acceptance, status, evidence and handover. Do not generate redundant empty files. This document does not create or access the actual local workspace.
