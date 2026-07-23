import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.security.authorization import get_token_payload, require_staff


@pytest.fixture
def rbac_app() -> FastAPI:
    app = FastAPI()

    @app.get("/staff-only")
    async def staff_only(_: dict = Depends(require_staff)) -> dict:
        return {"ok": True}

    return app


def test_require_staff_allows_admin(rbac_app: FastAPI) -> None:
    rbac_app.dependency_overrides[get_token_payload] = lambda: {"sub": "1", "roles": ["admin"]}
    client = TestClient(rbac_app)
    response = client.get("/staff-only")
    assert response.status_code == 200


def test_require_staff_allows_staff(rbac_app: FastAPI) -> None:
    rbac_app.dependency_overrides[get_token_payload] = lambda: {"sub": "1", "roles": ["staff"]}
    client = TestClient(rbac_app)
    response = client.get("/staff-only")
    assert response.status_code == 200


def test_require_staff_blocks_customer(rbac_app: FastAPI) -> None:
    rbac_app.dependency_overrides[get_token_payload] = lambda: {"sub": "1", "roles": ["customer"]}
    client = TestClient(rbac_app)
    response = client.get("/staff-only")
    assert response.status_code == 403
