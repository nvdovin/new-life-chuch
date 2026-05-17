from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'New Life Church API'
    env: str = 'dev'
    api_prefix: str = '/api/v1'

    postgres_dsn: str = Field(default='postgresql+asyncpg://postgres:postgres@postgres:5432/newlife')
    redis_dsn: str = Field(default='redis://redis:6379/0')
    clickhouse_dsn: str = Field(default='http://clickhouse:8123')

    jwt_secret: str = Field(default='change-me')
    jwt_algorithm: str = 'HS256'
    access_token_minutes: int = 15
    refresh_token_days: int = 14

    aes_key_b64: str = Field(default='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=')

    s3_endpoint: str = 'http://minio:9000'
    s3_access_key: str = 'minioadmin'
    s3_secret_key: str = 'minioadmin'
    s3_bucket: str = 'newlife-media'

    bootstrap_admin_email: str = 'admin@local'
    bootstrap_admin_password: str = 'ChangeMe123!'
    bootstrap_admin_full_name: str = 'Church Administrator'


settings = Settings()
