# Operating Model

## Agent responsibilities

| Agent | Responsibility | Output |
|---|---|---|
| Portfolio Router | Scope requests and coordinate product agents | Project selection, dependencies and task plan |
| Project Agent (11) | Product-specific domain context | Repository-aware plan and acceptance criteria |
| Repository Auditor | Inspect GitHub metadata and source evidence | Verified baseline, gaps and blockers |
| Competitor Analyst | Compare evidence-backed product capabilities | Source-linked parity matrix |
| Implementer | Produce bounded code changes in an isolated worker | Feature branch and patch evidence (Phase 2) |
| Independent Reviewer | Review security, correctness and tenant isolation | Blocking/non-blocking findings |
| Release Coordinator | Track PR dependencies and main-branch integration | Merge readiness and commit evidence (Phase 3) |

## Execution state machine

REQUESTED -> SCOPED -> AUDITED -> PLANNED -> IMPLEMENTING -> REVIEWING -> PR_READY -> MERGED

A task may transition to BLOCKED at any stage. A plan is not an implementation. A PR is not a merge. A merged commit is not a production deployment.

## Merge policy

- Inspect the latest main before creating a feature branch.
- Do not overwrite or force-push existing work.
- Keep each product's changes in its own repository.
- Preserve stacked PR dependencies and merge in dependency order.
- The owner has requested CI workflows be skipped. This does not mean tests can be falsely marked as passed: report tests as not run and retain local/static review evidence.
- Do not merge if a change has unresolved security findings, data-loss risk, broken dependency ordering or unverified destructive migrations.
- Record PR URL, head SHA, merge SHA and actual merge result.

## Security boundaries

- Start with a fine-grained read-only GitHub token.
- Never pass credentials or tenant database URLs to the LLM.
- Do not ingest patient data, financial account data, Aadhaar/PAN or production records.
- Isolate each worker in a disposable checkout/container with CPU, memory, time and filesystem limits.
- Restrict writes to the exact allowlisted repository and task branch.
- Require human-controlled configuration for production deployment and live payment operations.
