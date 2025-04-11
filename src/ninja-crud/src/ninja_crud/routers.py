"""Main class to create CRUD operations for a Django model."""

import functools
from typing import Callable, Generic, cast, get_type_hints

from django.db.models import QuerySet
from ninja import FilterSchema, Router, Schema
from ninja.orm import create_schema as generate_schema
from ninja.orm.fields import TYPES as NINJA_TYPES_MAP
from pydantic import Field, create_model

from .types import (
    CreateSchemaType,
    FilterSchemaType,
    ModelType,
    ReadSchemaType,
    UpdateSchemaType,
)
from .viewsets import AsyncViewSet, SyncViewSet


class CRUDRouter(Generic[ModelType, CreateSchemaType, ReadSchemaType, UpdateSchemaType, FilterSchemaType]):
    """
    Generic class to create CRUD operations for a Django model.

    This router automatically generates endpoint handlers for Create, Read, Update, and Delete
    operations on the specified Django model. It uses Django Ninja for API creation and can
    work with both synchronous and asynchronous viewsets.

    Args:
        model: The Django model to create CRUD operations for
        create_schema: Optional schema for validating create operations. Auto-generated if None.
        read_schema: Optional schema for serializing model instances. Auto-generated if None.
        update_schema: Optional schema for validating update operations. Auto-generated if None.
        path: The URL path prefix for all endpoints. Defaults to the model's plural verbose name in lowercase.
        tags: Tags for API documentation grouping. Defaults to the model's verbose name.
        queryset: Optional custom queryset to use as the base for all operations.
        operations: String containing any combination of "C", "R", "U", "D" to specify
                   which operations to enable. Defaults to "CRUD" (all operations).
    """

    def __init__(
        self,
        model: type[ModelType],
        *,
        create_schema: type[CreateSchemaType] | None = None,
        read_schema: type[ReadSchemaType] | None = None,
        update_schema: type[UpdateSchemaType] | None = None,
        filter_schema: type[FilterSchemaType] | None = None,
        path: str | None = None,
        tags: list[str] | None = None,
        queryset: QuerySet | None = None,
        operations: str = "CRUD",
    ) -> None:
        self._model = model
        self._operations = operations
        self._queryset = queryset or model.objects.all()

        self._create_schema = create_schema or self._generate_create_schema()
        self._read_schema = read_schema or self._generate_read_schema()
        self._update_schema = update_schema or self._generate_update_schema()
        self._filter_schema = filter_schema or self._generate_filter_schema()
        self._model_pk_python_type = NINJA_TYPES_MAP.get(model._meta.pk.get_internal_type(), int)
        self._pk_name = model._meta.pk.name
        self._swagger_description_model = str(model.__name__)

        self._tags = tags or cast(list[str], [model._meta.verbose_name])

        model_name = cast(
            str,
            (model._meta.model_name if model._meta.verbose_name_plural is None else model._meta.verbose_name_plural),
        )
        if not path and not model_name:
            msg = "Unable to find model name, please provide a path"
            raise ValueError(msg)

        self.path = path or model_name.replace(" ", "-").lower()
        self.router = Router(tags=self._tags)

        # Register CRUD routes
        self._register_routes()

    def _register_routes(self) -> None:
        """
        Register all CRUD routes based on the operations setting.

        Selects the appropriate viewset (sync or async) based on model relationship complexity
        and registers only the endpoints specified in the operations parameter.
        """
        # Choose the appropriate viewset based on relationship types
        viewset: SyncViewSet | AsyncViewSet
        if self._has_complex_relationships():
            viewset = SyncViewSet(
                self._model,
                self._create_schema,
                self._read_schema,
                self._update_schema,
                self._filter_schema,
                self._queryset,
                self._model_pk_python_type,
                self._pk_name,
            )
        else:
            viewset = AsyncViewSet(
                self._model,
                self._create_schema,
                self._read_schema,
                self._update_schema,
                self._filter_schema,
                self._queryset,
                self._model_pk_python_type,
                self._pk_name,
            )
        # Register the router with the API
        if "C" in self._operations:
            self._register_create_item(viewset.create_item)
        if "R" in self._operations:
            self._register_list_items(viewset.list_items)
            self._register_get_item(viewset.get_item)
        if "U" in self._operations:
            self._register_update_item(viewset.update_item)
        if "D" in self._operations:
            self._register_delete_item(viewset.delete_item)

    def _generate_create_schema(self) -> type[Schema]:
        """
        Generate a schema for create operations.

        Automatically excludes auto-created and auto-updated fields.
        """
        return generate_schema(self._model, name=f"{self._model.__name__}Create", exclude=self._autogenerated_fields)

    def _generate_filter_schema(self) -> type[FilterSchemaType]:
        """
        Generate a schema for filter operations.
        """
        model = generate_schema(self._model, name="TmpFilter", base_class=FilterSchema, optional_fields="__all__")
        field_types = get_type_hints(model)
        filter_schema: type[FilterSchemaType] = create_model(
            f"{self._model.__name__}Filter",
            __base__=FilterSchema,
            **{field_name: (field_types[field_name], Field(default=None)) for field_name in model.model_fields},
        )  # type: ignore
        return filter_schema

    def _generate_update_schema(self) -> type[Schema]:
        """
        Generate a schema for update operations.

        Makes all fields optional and excludes auto-created and auto-updated fields.
        """
        return generate_schema(
            self._model,
            name=f"{self._model.__name__}Update",
            exclude=self._autogenerated_fields,
            optional_fields="__all__",  # type: ignore
        )

    def _generate_read_schema(self) -> type[Schema]:
        """
        Generate a schema for read operations.

        Includes all model fields for serialization.
        """
        return generate_schema(self._model, name=f"{self._model.__name__}Read")

    @functools.cached_property
    def _autogenerated_fields(self) -> list[str]:
        """
        Identify fields that are automatically generated or updated by Django.

        Returns:
            List of field names that should be excluded from user input.
        """
        return [
            field.name
            for field in self._model._meta.get_fields()
            if field.concrete
            and (
                getattr(field, "auto_created", False)
                or getattr(field, "auto_now", False)
                or getattr(field, "auto_now_add", False)
            )
        ]

    def _has_complex_relationships(self) -> bool:
        """
        Check if the model has complex relationships that may benefit from asynchronous handling.

        Looks for many-to-many relationships or reverse foreign keys (one-to-many).

        Returns:
            bool: True if complex relationships exist, False otherwise.
        """
        return any(field.many_to_many for field in self._model._meta.get_fields())

    def _register_create_item(self, function: Callable) -> None:
        """
        Register the create endpoint (POST /).

        Args:
            function: The handler function for creating items.
        """
        self.router.add_api_operation(
            "/",
            ["POST"],
            function,
            response={201: self._read_schema},
            operation_id=f"create_{self._model._meta.model_name}",
            summary=f"Create {self._swagger_description_model}",
        )

    def _register_list_items(self, function: Callable) -> None:
        """
        Register the list endpoint (GET /).

        Args:
            function: The handler function for listing items.
        """
        self.router.add_api_operation(
            "/",
            ["GET"],
            function,
            response=list[self._read_schema],  # type: ignore
            operation_id=f"list_{self._model._meta.model_name}",
            summary=f"List {self._swagger_description_model}",
        )

    def _register_get_item(self, function: Callable) -> None:
        """
        Register the detail endpoint (GET /{id}).

        Args:
            function: The handler function for retrieving a specific item.
        """
        self.router.add_api_operation(
            f"/{{{self._pk_name}}}",
            ["GET"],
            function,
            response=self._read_schema,
            operation_id=f"get_{self._model._meta.model_name}",
            summary=f"Get {self._swagger_description_model}",
        )

    def _register_update_item(self, function: Callable) -> None:
        """
        Register the update endpoint (PATCH /{id}).

        Args:
            function: The handler function for updating a specific item.
        """
        self.router.add_api_operation(
            f"/{{{self._pk_name}}}",
            ["PATCH"],
            function,
            response=self._read_schema,
            operation_id=f"update_{self._model._meta.model_name}",
            summary=f"Update {self._swagger_description_model}",
        )

    def _register_delete_item(self, function: Callable) -> None:
        """
        Register the delete endpoint (DELETE /{id}).

        Args:
            function: The handler function for deleting a specific item.
        """
        self.router.add_api_operation(
            f"/{{{self._pk_name}}}",
            ["DELETE"],
            function,
            response={204: None},
            operation_id=f"delete_{self._model._meta.model_name}",
            summary=f"Delete {self._swagger_description_model}",
        )
