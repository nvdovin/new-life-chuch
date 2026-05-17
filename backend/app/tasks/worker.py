from arq import cron
from arq.connections import RedisSettings

from app.core.config import settings


async def send_deadline_reminders(ctx: dict) -> None:
    _ = ctx


async def notify_prayer_status(ctx: dict, prayer_id: str) -> None:
    _ = (ctx, prayer_id)


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_dsn)
    functions = [send_deadline_reminders, notify_prayer_status]
    cron_jobs = [
        cron(send_deadline_reminders, minute=0),
    ]
