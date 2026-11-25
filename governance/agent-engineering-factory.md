# Agent Engineering Factory

Status: proposed; tooling availability, licenses and performance not verified.

## Candidate tools (20)

| Tool | Purpose |
|---|---|
| Superpowers | Engineering workflow |
| Spec Kit | Specifications and plans |
| GitHub MCP | Repository operations |
| Context7 | Current technical documentation |
| Playwright | Browser tests |
| Figma MCP | UI design |
| Product Design | Product experience |
| Poka-Yoke | Mistake prevention |
| Docker | Isolated runtime |
| Semgrep | Static analysis |
| Trivy | Dependency security |
| Renovate | Dependency updates |
| Temporal | Durable orchestration |
| OpenHands | Complementary coding agent |
| LiteLLM | Model routing |
| Ollama | Local inference |
| Git worktree | Parallel isolated changes |
| uv | Python environment |
| pnpm | JavaScript dependencies |
| BuildKit | Container build cache |

## Acceleration methods (12)

Parallel execution, dependency graph scheduling, model routing, context caching, incremental testing, build caching, code reuse, automated preliminary review, checkpointing, dynamic agent allocation, bottleneck management and batch execution. Full release tests and independent acceptance remain mandatory.

## Organization

16 proposed roles: commander (1), architect (1), researchers (2), developers (4), integrators (2), infrastructure (2), independent validators (3), security (1). Roles are not necessarily simultaneous agent instances.

## Concurrency scenarios

2 economical, 4 balanced (initial proposal), 8 fast, 16 maximum experimental. Measure hardware capacity and provider limits before starting; reduce concurrency on contention or rework. Use isolated worktrees, shared contract ownership, dependency gates and least privilege. No unauthorized spending, plugin installation, secrets disclosure or public deployment.

## Validation

Benchmark 2 versus 4 workers on comparable scoped tasks; record wall time, throughput, token cost, CPU/RAM, blocked time, rework and accepted quality. Scale only when measured benefit outweighs coordination overhead. Verify tool availability and compatibility in the actual Codex workspace; install only necessary approved tools. No acceleration claim, installation, merge or deployment is implied by this record.
