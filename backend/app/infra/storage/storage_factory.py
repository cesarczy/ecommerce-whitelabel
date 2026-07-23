import io
import logging

import boto3
from botocore.client import Config

from app.application.interfaces.ports import StoragePort
from app.core.config.settings import settings

logger = logging.getLogger(__name__)


class R2StorageAdapter(StoragePort):
    """Cloudflare R2 via S3-compatible API."""

    def __init__(self) -> None:
        endpoint = settings.r2_endpoint or f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )
        self._bucket = settings.r2_bucket

    async def upload(self, *, key: str, data: bytes, content_type: str) -> str:
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=io.BytesIO(data),
            ContentType=content_type,
        )
        return key

    async def get_presigned_url(self, *, key: str, expires_seconds: int = 3600) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_seconds,
        )

    async def delete(self, *, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)


def get_storage_adapter() -> StoragePort:
    from app.infra.storage.minio_adapter import InMemoryStorageAdapter, MinIOStorageAdapter

    provider = settings.storage_provider.lower()
    if provider == "r2" and settings.r2_access_key_id:
        try:
            return R2StorageAdapter()
        except Exception as exc:
            logger.warning("R2 adapter failed, falling back: %s", exc)
    if provider != "memory":
        try:
            return MinIOStorageAdapter()
        except Exception as exc:
            logger.warning("MinIO adapter failed, falling back: %s", exc)
    return InMemoryStorageAdapter()
