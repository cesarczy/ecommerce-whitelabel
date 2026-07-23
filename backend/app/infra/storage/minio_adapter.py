import io
import logging

from minio import Minio

from app.application.interfaces.ports import StoragePort
from app.core.config.settings import settings

logger = logging.getLogger(__name__)


class MinIOStorageAdapter(StoragePort):
    def __init__(self) -> None:
        self._client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self._bucket = settings.minio_bucket
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
        except Exception as exc:
            logger.warning("MinIO bucket check failed: %s", exc)

    async def upload(self, *, key: str, data: bytes, content_type: str) -> str:
        self._client.put_object(
            self._bucket,
            key,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        return key

    async def get_presigned_url(self, *, key: str, expires_seconds: int = 3600) -> str:
        from datetime import timedelta

        return self._client.presigned_get_object(
            self._bucket,
            key,
            expires=timedelta(seconds=expires_seconds),
        )

    async def delete(self, *, key: str) -> None:
        self._client.remove_object(self._bucket, key)


class InMemoryStorageAdapter(StoragePort):
    """Fallback when MinIO is unavailable."""

    _store: dict[str, bytes] = {}

    async def upload(self, *, key: str, data: bytes, content_type: str) -> str:
        self._store[key] = data
        return key

    async def get_presigned_url(self, *, key: str, expires_seconds: int = 3600) -> str:
        return f"/storage/{key}"

    async def delete(self, *, key: str) -> None:
        self._store.pop(key, None)
