from fastapi import HTTPException as FastAPIHTTPException
from pydantic import ValidationError as PydanticValidationError


class UnchainedBaseException(Exception):
    pass


class UnchainedError(UnchainedBaseException):
    pass


class ValidationError(UnchainedBaseException, PydanticValidationError):
    pass


class HTTPError(UnchainedBaseException, FastAPIHTTPException):
    pass
