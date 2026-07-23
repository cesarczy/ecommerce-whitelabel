from datetime import UTC, datetime

import pytest

from app.domain.review.entities.review import Review
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError


class TestReview:
    def test_create_review_records_event(self) -> None:
        review = Review.create(
            product_id=EntityId.generate(),
            customer_id=EntityId.generate(),
            rating=5,
            title="Great",
            comment="Excellent product",
        )
        assert review.rating == 5
        events = review.collect_events()
        assert len(events) == 1
        assert events[0].event_name == "ReviewSubmittedEvent"

    def test_rejects_invalid_rating(self) -> None:
        with pytest.raises(DomainError):
            Review.create(
                product_id=EntityId.generate(),
                customer_id=EntityId.generate(),
                rating=0,
                title="Bad",
                comment="Invalid",
            )

    def test_rejects_empty_comment(self) -> None:
        with pytest.raises(DomainError):
            Review.create(
                product_id=EntityId.generate(),
                customer_id=EntityId.generate(),
                rating=3,
                title="Ok",
                comment="   ",
            )

    def test_reconstitute(self) -> None:
        pid = EntityId.generate()
        cid = EntityId.generate()
        rid = EntityId.generate()
        now = datetime.now(UTC)
        review = Review.reconstitute(
            review_id=rid,
            product_id=pid,
            customer_id=cid,
            order_id=None,
            rating=4,
            title="Good",
            comment="Nice",
            created_at=now,
        )
        assert review.id == rid
        assert review.comment == "Nice"
