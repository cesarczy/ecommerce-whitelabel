import pyotp

from app.application.interfaces.ports import MfaService


class TotpMfaService(MfaService):
    def generate_secret(self) -> str:
        return pyotp.random_base32()

    def get_provisioning_uri(self, *, secret: str, email: str) -> str:
        return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name="EcommerceWhitelabel")

    def verify_code(self, *, secret: str, code: str) -> bool:
        return pyotp.TOTP(secret).verify(code, valid_window=1)
