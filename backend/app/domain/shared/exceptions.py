class DomainError(Exception):
    """Raised when a domain invariant or business rule is violated."""

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code or "DOMAIN_ERROR"
        super().__init__(message)
