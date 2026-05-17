# Data Model

## Core Domain
- `sermons`: title, body, media URLs, external links, transcript, tags, author, preached_on
- `news`: title, body, media, priority, publish_at, birthday fields
- `prayer_requests`: author/anonymous, category, content, status, moderation flag
- `ministries`: ministry dictionary
- `ministry_tasks`: hierarchy (depth <= 3), status, priority, deadline
- `knowledge_articles`: nested markdown docs with version

## Access Control
- `roles`, `permissions`, `role_permissions`, `user_roles`

## Security & Sessions
- `refresh_tokens`
- encrypted fields in `users` (phone, 2FA secret)

## Compliance Hooks
User anonymization/delete should scrub or hash PII while preserving non-PII referential records when needed.
