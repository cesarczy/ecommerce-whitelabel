from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.domain_event import DomainEvent
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewSubmittedEvent(DomainEvent):
    product_id: str
    rating: int


@dataclass
class Review(AggregateRoot):
    id: EntityId
    product_id: EntityId
    customer_id: EntityId
    order_id: EntityId | None
    rating: int
    title: str
    comment: str
    created_at: datetime

    def __post_init__(self) -> None:
        super().__init__()

    @classmethod
    def create(
        cls,
        *,
        product_id: EntityId,
        customer_id: EntityId,
        rating: int,
        title: str,
        comment: str,
        order_id: EntityId | None = None,
    ) -> Review:
        if rating < 1 or rating > 5:
            raise DomainError("Rating must be between 1 and 5", code="INVALID_REVIEW")
        title_clean = title.strip()
        comment_clean = comment.strip()
        if not comment_clean:
            raise DomainError("Review comment is required", code="INVALID_REVIEW")
        review = cls(
            id=EntityId.generate(),
            product_id=product_id,
            customer_id=customer_id,
            order_id=order_id,
            rating=rating,
            title=title_clean,
            comment=comment_clean,
            created_at=datetime.now(UTC),
        )
        review._record_event(
            ReviewSubmittedEvent(
                aggregate_id=review.id.value,
                product_id=str(product_id.value),
                rating=rating,
            )
        )
        return review

    @classmethod
    def reconstitute(
        cls,
        *,
        review_id: EntityId,
        product_id: EntityId,
        customer_id: EntityId,
        order_id: EntityId | None,
        rating: int,
        title: str,
        comment: str,
        created_at: datetime,
    ) -> Review:
        return cls(
            id=review_id,
            product_id=product_id,
            customer_id=customer_id,
            order_id=order_id,
            rating=rating,
            title=title,
            comment=comment,
            created_at=created_at,
        )
