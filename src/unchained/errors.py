from unchained.ninja.errors import HttpError as NinjaHTTPError
from unchained.ninja.errors import ValidationError as NinjaValidationError


class UnchainedBaseException(Exception):
    pass


class UnchainedError(UnchainedBaseException):
    pass


class ValidationError(UnchainedBaseException, NinjaValidationError):
    pass


class HTTPError(UnchainedBaseException, NinjaHTTPError):
    pass
