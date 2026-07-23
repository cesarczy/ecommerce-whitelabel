class ApplicationError(Exception):
    def __init__(self, message: str, code: str = "APPLICATION_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(ApplicationError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, code="NOT_FOUND")


class ConflictError(ApplicationError):
    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message, code="CONFLICT")


class UnauthorizedError(ApplicationError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, code="UNAUTHORIZED")
