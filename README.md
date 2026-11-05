# ERP Super Agent

DeepSeek-powered multi-agent control plane for the owner's 11 ERP repositories. This repository hosts the coordinator; product source code remains in each product repository.

## Current MVP capabilities

- 11-project registry with the verified GitHub repository names.
- DeepSeek Chat Completions integration using the OpenAI-compatible API.
- Router, repository auditor, competitor analyst, implementation planner and independent reviewer agent roles.
- Live GitHub metadata audit: default branch, open pull requests and branch inventory.
- Per-project task planning using current repository metadata.
- SQLite run history and FastAPI endpoints.
- GitHub writes disabled by default and repository allowlist enforcement helper.

The current MVP is a **read/audit/plan coordinator**, not yet an autonomous code-writing worker. It does not clone repositories, edit source files, run local tests, commit code, open PRs or merge branches. Those execution capabilities are the next phase and must be validated in an isolated worker runtime.

## Architecture

```text
Dashboard / API
      |
Portfolio Router (DeepSeek)
      |
      +-- Clinic Agent
      +-- School Agent
      +-- Jewel POS Agent
      +-- Universal POS Agent
      +-- Manufacturing Agent
      +-- Chit Fund Agent
      +-- OnePass Agent
      +-- SaaS Admin Agent
      +-- Travel Agent
      +-- Transport Fleet Agent
      +-- Retail Agent
      |
Shared specialist agents: Auditor | Competitor Analyst | Implementer | Reviewer
      |
GitHub metadata adapter --> SQLite audit history
```

## Setup

1. Use Python 3.11 or newer.
2. Create an isolated virtual environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`.
5. Set `DEEPSEEK_API_KEY` and a fine-grained `GITHUB_TOKEN` with read-only access to the 11 listed repositories.
6. Start: `uvicorn superagent.main:app --host 127.0.0.1 --port 8787`.
7. Open API docs at `http://127.0.0.1:8787/docs`.

## API

- `GET /health` — service and credential configuration status (never returns secrets).
- `GET /api/projects` — all 11 projects.
- `POST /api/audit` — live GitHub metadata audit across the portfolio.
- `POST /api/tasks` — plan a task for one project using a selected agent role.
- `GET /api/runs` — recent persisted runs.

Example task:

```json
{"project_key":"transport-fleet","role":"auditor","request":"Review pending fleet onboarding features and identify the safest next increment."}
```

## Security and operating rules

- Keep the API bound to localhost until authentication and deployment hardening are implemented.
- Never commit `.env`, API keys, GitHub tokens, patient data, Aadhaar/PAN, payment secrets or tenant database URLs.
- Use a fine-grained GitHub token limited to these repositories. Begin read-only.
- GitHub writes remain disabled by default. Do not enable them until a separate worker has path restrictions, branch protection awareness, audit logs and tests.
- No direct production database access is implemented.
- Do not auto-merge unreviewed code. The owner may choose to skip CI, but static checks, code review and explicit evidence must still be recorded.
- Competitor analysis requires source URLs or a configured research connector; the LLM must not invent competitor facts.

## Roadmap

1. **Foundation (this branch):** project registry, DeepSeek provider, GitHub read audit, specialist roles, API and audit history.
2. **Isolated coding workers:** shallow clone per task, branch creation, file-scoped patching, local test execution and immutable run logs.
3. **Review and PR automation:** independent review, draft PR creation, dependency-aware stacked PR handling and merge readiness.
4. **Portfolio dashboard:** live project health, open PRs, branch-to-main status, blockers and scheduled reporting.
5. **Production hardening:** authentication, RBAC, secrets manager, rate limits, worker sandbox, queue, backups and observability.

## Project registry

The 11 repositories are configured in `superagent/projects.py`. The Retail repository is the `senthilsrinivasanmuthaiyan1/retail` repository; Universal POS is `senthilsrinivasanmuthaiyan/universal-pos`; SaaS Admin is `senthilsrinivasanmuthaiyan/sassadmin`.
