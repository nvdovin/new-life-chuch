from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.routes import router as v1_router
from app.core.config import settings
from app.db.init_db import init_models

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title=settings.app_name, version='1.0.0', openapi_url=f"{settings.api_prefix}/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allow_headers=['Authorization', 'Content-Type'],
)

app.include_router(v1_router, prefix=settings.api_prefix)


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.on_event('startup')
async def startup_event() -> None:
    await init_models()
