import logging

from celery import Celery

from app.core.config.settings import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "ecommerce",
    broker=settings.celery_broker_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
)


@celery_app.task(name="send_email")
def send_email_task(to: str, subject: str, body: str) -> dict:
    logger.info("Sending email to %s: %s", to, subject)
    return {"status": "sent", "to": to}


@celery_app.task(name="process_domain_event")
def process_domain_event_task(event_name: str, aggregate_id: str, payload: dict) -> dict:
    logger.info("Processing event %s for %s", event_name, aggregate_id)
    return {"event": event_name, "aggregate_id": aggregate_id, "payload": payload}
