# Nexus AI - Deployment Guide

| Metadata | Details |
| :--- | :--- |
| **Document Purpose** | Comprehensive DevSecOps and Infrastructure Guide |
| **Document Owner** | Lead DevOps Engineer |
| **Status** | Approved |
| **Version** | 1.0.0 |
| **Date** | 2026-07-03 |

---

## 1. Development Environment
*   **Monorepo Tools:** `npm` / `turbo` for managing `apps/web` and `apps/api`.
*   **Frontend Local:** Node.js 20+, `npm run dev` running Next.js locally on Port `3000`.
*   **Backend Local:** Python 3.11+, Poetry for dependency management, `uvicorn main:app --reload` on Port `8000`.
*   **Database Local:** Native Supabase Local CLI spinning up isolated Postgres docker equivalents for database logic testing.

## 2. Production Environment
A strictly cloud-native, serverless/PaaS hybrid model ensuring zero reliance on internal bare-metal racking.
*   **Presentation Layer:** Vercel Global Edge Network.
*   **Orchestration Layer:** Render (Dockerized Web Services).
*   **Persistence & Auth:** Managed Supabase Cloud (AWS backend).

## 3. Environment Variables
Local development relies on `.env.local`; production relies on secure secrets management injected natively by Vercel and Render dashboards. Never commit `.env` files.

**Crucial Variables (Backend - Python/FastAPI):**
*   `GEMINI_API_KEY`: Google Generative AI authentication.
*   `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY`: Admin privileges for bypass logic where explicitly necessary.
*   `FRONTEND_CORS_ORIGIN`: Strict whitelisting `https://nexusai.vercel.app` to prevent API farming.

**Crucial Variables (Frontend - Next.js):**
*   `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Client-side DB initialization.
*   `NEXT_PUBLIC_FASTAPI_REST_URL`: Targeting Render production endpoints.

## 4. CI/CD (GitHub Actions)
Fully automated CI/CD pipeline blocking pushes that break build criteria.
1. **Push to `main`.**
2. **Action 1 (Format & Lint):** `black`, `flake8`, `eslint`, `prettier`.
3. **Action 2 (Testing):** Invokes `pytest` against logic models.
4. **Action 3 (Merge Check):** If successful, signals PaaS webhooks.

## 5. Docker
The `apps/api` (FastAPI + LangGraph) is securely containerized.
*   **Base Image:** `python:3.11-slim` ensures rapid pull times and reduced vulnerability surfaces.
*   **Execution:** Bootstraps Gunicorn managing Uvicorn workers `CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "gunicorn_conf.py", "main:app"]`.

## 6. Vercel (Frontend Delivery)
GitHub integration automatically pulls from the `apps/web` workspace block. Vercel compiles React Server Components natively, automatically attaching cached Next.js bundles to their global CDN edge, achieving near-zero visual load times regardless of geographic origin.

## 7. Render (Backend Execution)
Render automatically builds the Dockerfile upon a successful GitHub Actions merge. Connected directly to our private Supabase database VPC enabling ultra-low latency routing.

## 8. Supabase (Database/Auth)
Production environment tied specifically to an enterprise Supabase cluster handling concurrent scaling limits, daily archiving, and integrated WebHook capabilities to trigger downstream Analytics updates on ledger change.

## 9. Monitoring
*   **Vercel Analytics:** Web Vitals monitoring (LCP, FID) ensuring UI components render seamlessly.
*   **Sentry:** Deployed deeply into the FastAPI Python middleware to trap and instantly alert on unhandled LangGraph cyclical loops or critical Pydantic validation errors.
*   **LangSmith (Optional but Recommended):** Dashboard mapping exact token usage logic verifying prompt execution health.

## 10. Logging
Standard out `stdout` logging aggregated via Datadog. FastApi natively tags UUID traces to inbound requests tracing exactly which human actor queried which AI node payload for post-mortem forensics.

## 11. Backup
*   **Supabase Level:** Point in Time Recovery (PITR) enabling rollback in `<1s` intervals should a cascading failure corrupt core inventory data. Base automated archiving captures entire database clusters nightly.

## 12. Scaling
*   **API Pods (Render):** CPU-bound auto-scaling logic enabled. If `requests_per_second` spikes heavily, the internal load balancer spawns additional parallel FastAPI Docker containers instantly.
*   **Client Connections (Supabase):** PgBouncer pooling active, limiting idle connection drops guaranteeing database queries don't hang when the system surges scaling blocks.

## 13. Disaster Recovery
Should Render (Backend PaaS) suffer total zone failure, the Docker container allows instant manual replication and deployment to AWS ECS Fargate or Heroku with an adjustment of DNS paths and zero application re-writing required. Recovery Time Objective (RTO): < 15 minutes.
