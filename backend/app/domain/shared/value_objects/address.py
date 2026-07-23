from __future__ import annotations

from dataclasses import dataclass

from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.cep import CEP


@dataclass(frozen=True, slots=True)
class Address:
    street: str
    number: str
    complement: str | None
    neighborhood: str
    city: str
    state: str
    cep: CEP
    label: str = "Principal"

    @classmethod
    def create(
        cls,
        *,
        street: str,
        number: str,
        neighborhood: str,
        city: str,
        state: str,
        cep: str | CEP,
        complement: str | None = None,
        label: str = "Principal",
    ) -> Address:
        street_clean = street.strip()
        number_clean = number.strip()
        neighborhood_clean = neighborhood.strip()
        city_clean = city.strip()
        state_clean = state.strip().upper()
        label_clean = label.strip()

        if not all([street_clean, number_clean, neighborhood_clean, city_clean, state_clean]):
            raise DomainError("Address fields cannot be empty", code="INVALID_ADDRESS")
        if len(state_clean) != 2:
            raise DomainError("State must be a 2-letter code", code="INVALID_ADDRESS")

        cep_vo = cep if isinstance(cep, CEP) else CEP.create(cep)

        return cls(
            street=street_clean,
            number=number_clean,
            complement=complement.strip() if complement else None,
            neighborhood=neighborhood_clean,
            city=city_clean,
            state=state_clean,
            cep=cep_vo,
            label=label_clean or "Principal",
        )

    def equals(self, other: Address) -> bool:
        return (
            self.street == other.street
            and self.number == other.number
            and self.complement == other.complement
            and self.neighborhood == other.neighborhood
            and self.city == other.city
            and self.state == other.state
            and self.cep.equals(other.cep)
            and self.label == other.label
        )

    def __str__(self) -> str:
        complement = f", {self.complement}" if self.complement else ""
        return (
            f"{self.street}, {self.number}{complement} — "
            f"{self.neighborhood}, {self.city}/{self.state} — {self.cep}"
        )
