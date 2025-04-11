"""Http exceptions for automatically generated CRUD operations."""

from typing import Any

from ninja.errors import HttpError

from .types import ModelType


class EntryNotFound(HttpError):  # noqa: N818
    """Exception raised when an entry is not found."""

    def __init__(self, model: type[ModelType], id_: Any) -> None:
        """Initialize the exception."""
        message = f"{model._meta.verbose_name} with id {id_} not found"
        super().__init__(404, message)


class BadRequest(HttpError):  # noqa: N818
    """Exception raised for bad request errors."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        super().__init__(400, message)
