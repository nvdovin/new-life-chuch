# API Contracts (v1)

Base URL: `/api/v1`

## Auth & Profile
- `POST /auth/register`
- `POST /auth/login`
- `GET /users/me`
- `POST /users/me/2fa/enable`
- `DELETE /users/{user_id}` (anonymization, permission: `users.delete`)

## Media
- `POST /media/presign` -> upload/download presigned URLs for S3-compatible storage

## Sermons
- `GET /sermons?q=&tag=`
- `GET /sermons/{sermon_id}`
- `POST /sermons` (permission: `sermons.write`)
- `PATCH /sermons/{sermon_id}` (permission: `sermons.write`)
- `DELETE /sermons/{sermon_id}` (permission: `sermons.write`)

## News
- `GET /news?q=`
- `POST /news` (permission: `news.write`)
- `PATCH /news/{news_id}` (permission: `news.write`)
- `DELETE /news/{news_id}` (permission: `news.write`)

## Prayer Requests
- `GET /prayers?status=` (permission: `prayers.read`)
- `POST /prayers`
- `PATCH /prayers/{prayer_id}` (permission: `prayers.moderate`)

## Ministries & Tasks
- `GET /ministries`
- `POST /ministries` (permission: `ministries.write`)
- `PATCH /ministries/{ministry_id}` (permission: `ministries.write`)
- `DELETE /ministries/{ministry_id}` (permission: `ministries.write`)
- `GET /tasks?ministry_id=&status=`
- `POST /tasks` (permission: `tasks.write`)
- `PATCH /tasks/{task_id}` (permission: `tasks.write`)
- `DELETE /tasks/{task_id}` (permission: `tasks.write`)

## Knowledge Base
- `GET /knowledge?q=`
- `POST /knowledge` (permission: `knowledge.write`)
- `PATCH /knowledge/{article_id}` (permission: `knowledge.write`)
- `DELETE /knowledge/{article_id}` (permission: `knowledge.write`)

## Admin
- `GET /audit-logs?limit=` (permission: `audit.read`)

OpenAPI: `/api/v1/openapi.json`
