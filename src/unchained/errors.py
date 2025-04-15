from ninja.errors import ValidationError as NinjaValidationError


class UnchainedBaseException(Exception):
    pass


class UnchainedError(UnchainedBaseException):
    pass


class ValidationError(UnchainedBaseException, NinjaValidationError):
    pass
