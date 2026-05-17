# Architecture

## Logical Components
1. Next.js frontend (admin + editor + member UX)
2. FastAPI backend (REST API + RBAC + audit)
3. PostgreSQL (transactional domain data)
4. ClickHouse (analytics: page visits, task performance, login history)
5. Redis (cache, queue, rate limit state)
6. ARQ workers (async notifications, reminders)
7. MinIO/S3 (media storage + presigned URLs)

## RBAC
Tables:
- users
- roles
- permissions
- role_permissions
- user_roles

Permission checks are enforced in route dependencies (middleware-style gate).

## Auditability
All important mutations are intended to be mirrored into `audit_logs` with actor, entity, payload diff.

## Deployment
Nginx serves as reverse proxy for API and frontend with security headers.
