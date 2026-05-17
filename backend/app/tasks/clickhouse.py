import httpx

from app.core.config import settings


async def push_event(event_name: str, payload: dict) -> None:
    query = "INSERT INTO events FORMAT JSONEachRow"
    row = {'event_name': event_name, 'payload': payload}
    async with httpx.AsyncClient(timeout=5) as client:
        await client.post(
            f"{settings.clickhouse_dsn}/?query={query}",
            content=(str(row).replace("'", '"') + '\n').encode('utf-8'),
        )
