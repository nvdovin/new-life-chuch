# New Life Church Platform

Production-oriented monorepo for church operations, content management, prayer moderation, ministry planning, and role-based administration.

## Stack
- Backend: FastAPI, Pydantic v2, SQLAlchemy async, Alembic, ARQ
- Frontend: Next.js 14 (App Router), TypeScript strict, TailwindCSS, Zustand, React Query-ready
- Data: PostgreSQL 15, ClickHouse, Redis
- Storage: MinIO (S3-compatible)
- Infra: Docker Compose, Nginx, GitHub Actions

## Run
```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- API: `http://localhost:8000/api/v1`
- OpenAPI: `http://localhost:8000/api/v1/openapi.json`
- MinIO Console: `http://localhost:9001`

## Backend Highlights
- JWT access/refresh auth
- Argon2id password hashing (`pwdlib`)
- AES-256-GCM encryption helper for sensitive PII
- RBAC middleware pattern (`users/roles/permissions/...`)
- Domain modules: sermons, news (+birthdays), prayer requests, ministries/tasks, knowledge base
- ARQ worker for notifications and deadline reminders

## Security Baseline
- Input validation via Pydantic
- Security headers in Nginx: CSP, HSTS, XFO, XCTO
- Ready for rate limit middleware (`slowapi`)
- Design target: OWASP Top 10 protections

## Docs
- `docs/architecture.md`
- `docs/api-contracts.md`
- `docs/data-model.md`
- `docs/ops-backup.md`
