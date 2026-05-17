import boto3

from app.core.config import settings


def _client():
    return boto3.client(
        's3',
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )


def presigned_upload_url(object_key: str, expires: int = 600) -> str:
    return _client().generate_presigned_url(
        ClientMethod='put_object',
        Params={'Bucket': settings.s3_bucket, 'Key': object_key},
        ExpiresIn=expires,
    )


def presigned_download_url(object_key: str, expires: int = 600) -> str:
    return _client().generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': settings.s3_bucket, 'Key': object_key},
        ExpiresIn=expires,
    )
