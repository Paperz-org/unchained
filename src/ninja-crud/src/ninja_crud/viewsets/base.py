"""Base ViewSet for sync and async implementations."""

from abc import ABC, abstractmethod
from collections.abc import Coroutine
from typing import Any, Generic

from django.db.models import QuerySet

from ..types import (
    CreateSchemaType,
    FilterSchemaType,
    ModelType,
    PKType,
    ReadSchemaType,
    UpdateSchemaType,
)


class BaseViewSet(
    ABC, Generic[ModelType, CreateSchemaType, ReadSchemaType, UpdateSchemaType, FilterSchemaType, PKType]
):
    """Base class for ViewSets that implements common functionality shared between sync and async versions."""

    def __init__(
        self,
        model: type[ModelType],
        create_schema: type[CreateSchemaType],
        read_schema: type[ReadSchemaType],
        update_schema: type[UpdateSchemaType],
        filter_schema: type[FilterSchemaType],
        queryset: QuerySet,
        pk_type: PKType,
        pk_name: str,
    ) -> None:
        """Initialize the ViewSet."""
        self.model = model
        self.create_schema = create_schema
        self.read_schema = read_schema
        self.update_schema = update_schema
        self.filter_schema = filter_schema
        self.queryset = queryset
        self.pk_type = pk_type
        self.pk_name = pk_name

    @abstractmethod
    def _handle_foreign_keys(self, data: dict) -> dict | Coroutine[Any, Any, dict[Any, Any]]:
        """Handle foreign key relations by converting IDs to model instances (sync version)."""
        ...

    def _extract_m2m_fields(self, data: dict) -> tuple[dict, dict]:
        """Extract many-to-many fields from payload data."""
        m2m_fields = {field.name: data.pop(field.name) for field in self.model._meta.many_to_many if field.name in data}
        return data, m2m_fields

    def _format_error_message(self, operation: str, error: Exception) -> str:
        """Format error message for exception handling."""
        return f"Error {operation} {self.model.__name__}: {error!s}"

    @abstractmethod
    def _get_object(self, id: PKType) -> ModelType | Coroutine[Any, Any, ModelType]:  # noqa: A002
        """Abstract method to get an object by ID."""
        ...

    @abstractmethod
    def _save_object(self, obj: ModelType) -> None | Coroutine[Any, Any, None]:
        """Abstract method to save an object."""
        ...

    @abstractmethod
    def _delete_object(self, obj: ModelType) -> None:
        """Abstract method to delete an object."""
        ...

    @abstractmethod
    def _apply_updates(self, obj: ModelType, payload: UpdateSchemaType) -> None:
        """Abstract method to apply updates to an object."""
        ...
