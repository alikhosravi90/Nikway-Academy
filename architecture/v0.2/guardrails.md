# NIKWAY Unified Guardrail Architecture

Status: proposed; not implemented or verified.

## Scope
Architecture, engineering, security, tenant isolation, AI inputs/outputs, agent permissions, data validation, financial budgets, infrastructure quotas, learning quality, compliance and release gates.

## Candidate stack
Open Policy Agent (policy as code); NeMo Guardrails and Guardrails AI (model interaction/output controls, subject to overlap review); Pydantic (schema validation); LiteLLM (model quotas); PostgreSQL RLS (data isolation); GitHub Rulesets and Actions (engineering controls); Temporal (workflow limits); OpenTelemetry (audit and monitoring).

## Enforcement lifecycle
Request → authenticate → policy/permission check → risk and budget check → allow, deny or require human approval → execute within scope → validate output → record evidence. Recheck authorization at execution; approval is scoped and expires. Output validation cannot undo irreversible side effects.

## Principles
Deny by default, least privilege, fail closed for sensitive operations, human approval for consequential actions, bounded retries, hard budget limits, kill switch, auditability and policy versioning. Model guardrails do not replace deterministic authorization. Never trust tool output as instructions. Protect logs from secrets and private tenant data.

## Acceptance gates
Test unauthorized actions, cross-tenant leakage, prompt injection, malformed output, budget exhaustion, policy-service outage, approval replay, retry limits, kill switch and blocked release. Record policy version, decision, reason and correlation ID. Benchmark and feasibility remain pending; no merge, installation or deployment authorized.
