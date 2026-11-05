# ERP Super Agent

DeepSeek-powered multi-agent control plane for the owner's 11 ERP repositories. This repository hosts the coordinator; product source code remains in each product repository.

## Current MVP capabilities

- 11-project registry with verified GitHub repository names.
- Local DeepSeek model support through Ollama and OpenAI-compatible model endpoints.
- Router, repository auditor, competitor analyst, implementation planner and independent reviewer agent roles.
- Live GitHub metadata audit: default branch, open pull requests and branch inventory.
- Per-project task planning using current repository metadata.
- SQLite run history and FastAPI endpoints.
- Dashboard for portfolio audit, project routing and task planning.
- GitHub writes disabled by default and repository allowlist enforcement helper.

## Zero-API-fee mode

The default configuration uses a local DeepSeek R1 model through Ollama. This avoids per-request API fees; it requires local disk, memory and compute.

1. Install Ollama: https://ollama.com
2. Pull the model: `ollama pull deepseek-r1:8b`
3. Keep the Ollama service running.
4. Copy `.env.example` to `.env`; local model settings are already the defaults.

Cloud DeepSeek API mode is optional and may incur usage charges. No paid API key is required for the local mode.

## Architecture

```text
Dashboard / API
      |
Portfolio Router (local DeepSeek model)
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
5. Install Ollama and pull `deepseek-r1:8b` (or configure another OpenAI-compatible model endpoint).
6. Set a fine-grained, read-only `GITHUB_TOKEN` limited to the 11 listed repositories.
7. Start: `uvicorn superagent.main:app --host 127.0.0.1 --port 8787`.
8. Open the dashboard at `http://127.0.0.1:8787` and API docs at `http://127.0.0.1:8787/docs`.

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

## Current implementation boundary

This is a read/audit/plan coordinator, not yet an autonomous code-writing worker. It does not clone repositories, edit product source files, run local tests, commit code, open product PRs or merge branches. Those execution capabilities are the next phase and must be validated in an isolated worker runtime.

## Roadmap

1. **Foundation:** project registry, local DeepSeek provider, GitHub read audit, specialist roles, dashboard and run history.
2. **Isolated coding workers:** shallow clone per task, branch creation, file-scoped patching, local test execution and immutable run logs.
3. **Review and PR automation:** independent review, draft PR creation, dependency-aware stacked PR handling and merge readiness.
4. **Portfolio dashboard:** live project health, open PRs, branch-to-main status, blockers and scheduled reporting.
5. **Production hardening:** authentication, RBAC, secrets manager, rate limits, worker sandbox, queue, backups and observability.

## Project registry

The 11 repositories are configured in `superagent/projects.py`. Retail is `senthilsrinivasanmuthaiyan1/retail`; Universal POS is `senthilsrinivasanmuthaiyan/universal-pos`; SaaS Admin is `senthilsrinivasanmuthaiyan/sassadmin`.


## Mobile cloud control plane (free-tier deployment)

A mobile-first installable PWA and Cloudflare Worker implementation is available on the `feature/mobile-cloud-control-plane` branch. It includes:
- Responsive Android dashboard and PWA manifest/service worker.
- Cloudflare Worker API with signed HttpOnly sessions and login rate limiting.
- D1 audit/run history and 11-repository read-only GitHub metadata audit.
- DeepSeek R1 Distill Qwen 32B through Cloudflare Workers AI, bounded by the Free-plan daily allocation.
- Deployment instructions in `docs/MOBILE_CLOUD_DEPLOYMENT.md`.

Cloud deployment requires the owner to create a Cloudflare D1 database, set the two GitHub read-only tokens and admin/session secrets, and deploy the Worker. No Cloudflare account credentials or GitHub tokens are stored in this repository. The app is not deployed yet. Keep Cloudflare on its Free plan to preserve the ₹0 monthly budget; AI calls can fail after the free daily allocation is exhausted.

The cloud control plane currently supports mobile login, repository metadata audits, run history and AI-generated plans. It does not yet write to product repositories or perform autonomous code changes/merges.
