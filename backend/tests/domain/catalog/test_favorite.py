from datetime import UTC, datetime

import pytest

from app.domain.catalog.entities.favorite import Favorite
from app.domain.shared.entity_id import EntityId


class TestFavorite:
    def test_create_favorite(self) -> None:
        user_id = EntityId.generate()
        product_id = EntityId.generate()
        favorite = Favorite.create(user_id=user_id, product_id=product_id)
        assert favorite.user_id == user_id
        assert favorite.product_id == product_id
