import logging

from app.infra.workers.celery_app import send_email_task

logger = logging.getLogger(__name__)


def queue_email(*, to: str, subject: str, body: str) -> None:
    try:
        send_email_task.delay(to, subject, body)
    except Exception:
        logger.info("Email notification (offline): to=%s subject=%s body=%s", to, subject, body)
