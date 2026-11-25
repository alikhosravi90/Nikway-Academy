# NIKWAY Agent Resilience Framework

Status: proposed; qualitative benchmark, not runtime validated.

## Reference projects
Temporal (durable workflows), LangGraph (checkpointing), OpenHands (isolated execution), AutoGen (multi-agent coordination), Argo Workflows (dependency scheduling), Prefect (state and retries), Kubernetes (service recovery), LiteLLM (model fallback), Resilience4j (fault tolerance patterns).

## Controls
Checkpoint, retry with backoff, fallback, circuit breaker, bulkhead, dead-letter queue, watchdog, heartbeat, idempotency, compensation, graceful degradation, human escalation, state persistence, context recovery and resource throttling.

## Execution protocol
Persist mission ID, action ID, commit, worktree, dependencies, attempt count, status and evidence references. Resume from the last verified checkpoint after interruption. Retry transient errors at most three times with backoff; do not retry authorization failures automatically. Reconcile side effects before retrying. Escalate blocked missions and continue independent authorized work. Never bypass approval, budget or security controls. Keep secrets and private runtime state out of public Git.

## Initial implementation
Use Git worktrees, local persistent status files, checkpoints and a dependency-aware mission queue. Add Temporal or other orchestration engines only after measured need. Verify tool availability and licenses before installation.

## Acceptance
Test interrupted execution, restart, duplicate action, unavailable model, resource exhaustion, dependency failure and human approval boundaries. Measure recovery time, lost work, blocked time, retry rate and accepted throughput. No performance or recovery claim until tests pass. No merge or deployment authorized.
