# Mobile Cloud Deployment (Free Tier)

This deploys the mobile dashboard and its API to Cloudflare Workers. The app is a PWA and can be added to the Android home screen.

## What the free setup includes

- Cloudflare Workers Free for the API and static dashboard.
- Cloudflare D1 Free for run history and login-rate-limit state.
- Cloudflare Workers AI with DeepSeek R1 Distill Qwen 32B, using the included free daily allocation.
- GitHub fine-grained personal access tokens for read-only repository metadata and open pull requests.
- No paid DeepSeek API key and no cloud VM.

Cloudflare Workers Free currently documents 100,000 requests/day. Workers AI documents 10,000 Neurons/day at no charge on the Free plan. AI calls stop when the free allocation is exhausted; do not upgrade to a paid plan if the hard ₹0 budget must be maintained. The selected DeepSeek R1 distilled model is listed in the Cloudflare AI catalog and does not show the paid-access-required restriction applied to newer V4 models. Check current Cloudflare quotas before relying on them.

## One-time Cloudflare setup

1. Sign in to Cloudflare and remain on the Free plan. Do not add a paid Workers plan or prepaid AI credits.
2. Open **Workers & Pages → D1 SQL Database → Create**. Name it `erp-super-agent`.
3. Copy the D1 database ID. In this repository's `wrangler.toml`, replace `REPLACE_AFTER_CREATING_D1` with that ID.
4. Connect the GitHub repository `senthilsrinivasanmuthaiyan/TaskManager` to **Workers Builds**. Set the production branch to `feature/mobile-cloud-control-plane` for initial preview, or deploy the merged main branch later. Use the repository root as the project root and `npm run deploy` as the deploy command.
5. Before deployment, configure these Worker secrets in the Cloudflare dashboard:
   - `ADMIN_PASSWORD`: a unique strong password for the mobile dashboard.
   - `SESSION_SECRET`: a random secret with at least 32 bytes of entropy.
   - `GITHUB_TOKEN_PRIMARY`: fine-grained PAT for `senthilsrinivasanmuthaiyan`.
   - `GITHUB_TOKEN_SECONDARY`: fine-grained PAT for `senthilsrinivasanmuthaiyan1`.
6. Each GitHub token should be limited to the 11 target repositories owned by that account, with repository **Metadata: Read-only** and **Pull requests: Read-only**. Do not grant Contents: write, Actions: write, Administration, or other write permissions. Keep the tokens in Cloudflare Secrets only; never commit them to Git or enter them in the dashboard.
7. Deploy the Worker.
8. Apply the D1 migrations from a terminal with Wrangler authenticated to the same Cloudflare account:
   `npx wrangler d1 migrations apply erp-super-agent --remote`
   Or execute the SQL files in order using the D1 SQL console: `cloudflare/migrations/0001_initial.sql`, then `cloudflare/migrations/0002_login_rate_limit.sql`.
9. Verify `/api/health` reports `status: ok`, then open the Worker URL and sign in.

## Install on Android

1. Open the deployed HTTPS Worker URL in Chrome on Android.
2. Sign in.
3. Open Chrome's three-dot menu and choose **Install app** or **Add to Home screen**.
4. Launch ERP Super Agent from the home screen.

The PWA caches the static app shell only. API calls and repository data require an internet connection.

## Security

- Sessions are signed, HttpOnly, Secure and SameSite=Strict cookies with a seven-day expiry.
- Login attempts are rate-limited by a hashed client IP.
- The dashboard API requires authentication.
- GitHub access is read-only. The app cannot push commits, create branches, merge pull requests or modify product repositories.
- Do not use patient information, production data, database credentials or payment secrets in agent prompts.
- Use a strong unique admin password and a random session secret. Rotate tokens immediately if exposed.

## Current functional scope

The cloud worker can list the 11 configured repositories, inspect default branch/open PR/branch metadata, store audit history in D1 and request an AI-generated project plan. It is not yet a code-writing or merge agent. AI usage is bounded by Cloudflare Workers AI's Free-plan daily allocation; once exhausted, AI requests may fail until the quota resets.

## Free-tier caveats

Cloudflare can change free quotas and model availability. The free Workers plan has request and CPU limits. Workers AI free usage is quota-limited. This is suitable for a lightweight personal control plane, not a production SLA or continuously running coding worker. Keep a copy of configuration and migration files in Git.
