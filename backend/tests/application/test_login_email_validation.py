import pytest
from pydantic import ValidationError

from app.application.dto.schemas import LoginUserInput


def test_login_accepts_dev_admin_email() -> None:
    payload = LoginUserInput(email="admin@ecommerce.local", password="Admin123!")
    assert payload.email == "admin@ecommerce.local"


def test_login_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        LoginUserInput(email="not-an-email", password="Admin123!")
