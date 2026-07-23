import pytest

from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.address import Address
from app.domain.shared.value_objects.cep import CEP
from app.domain.shared.value_objects.sku import SKU


class TestAddress:
    def test_create_with_formatted_cep(self) -> None:
        address = Address.create(
            street="Rua das Flores",
            number="123",
            neighborhood="Centro",
            city="São Paulo",
            state="sp",
            cep="01310-100",
        )
        assert address.state == "SP"
        assert str(address.cep) == "01310-100"

    def test_rejects_invalid_state(self) -> None:
        with pytest.raises(DomainError):
            Address.create(
                street="Rua A",
                number="1",
                neighborhood="Bairro",
                city="Cidade",
                state="SAO",
                cep="01310100",
            )


class TestCEP:
    def test_create_strips_non_digits(self) -> None:
        assert str(CEP.create("01310-100")) == "01310-100"


class TestSKU:
    def test_create_uppercases(self) -> None:
        assert str(SKU.create("abc-123")) == "ABC-123"

    def test_rejects_short_sku(self) -> None:
        with pytest.raises(DomainError):
            SKU.create("AB")
