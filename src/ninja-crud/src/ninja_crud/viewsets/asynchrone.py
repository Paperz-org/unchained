"""Asynchrone implementation of the ViewSet."""

from collections.abc import Coroutine
from typing import Any, Callable, cast

from django.db import DatabaseError
from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import Query
from ninja.pagination import paginate
from pydantic import ValidationError

from ..decorators import async_rename_parameter as rename
from ..exceptions import BadRequest, EntryNotFound
from ..types import (
    CreateSchemaType,
    FilterSchemaType,
    ModelType,
    PKType,
    ReadSchemaType,
    UpdateSchemaType,
)
from .base import BaseViewSet

ListItemsReturnType = Callable[[HttpRequest, Query], QuerySet[ModelType]]
GetItemReturnType = Callable[[HttpRequest, PKType], Coroutine[Any, Any, ModelType]]
CreateItemReturnType = Callable[[HttpRequest, CreateSchemaType], Coroutine[Any, Any, Any]]
UpdateItemReturnType = Callable[[HttpRequest, PKType, UpdateSchemaType], Coroutine[Any, Any, Any]]
DeleteItemReturnType = Callable[[HttpRequest, PKType], Coroutine[Any, Any, tuple[int, None]]]


class AsyncViewSet(
    BaseViewSet[ModelType, CreateSchemaType, ReadSchemaType, UpdateSchemaType, FilterSchemaType, PKType]
):
    """Async implementation of the ViewSet."""

    async def _get_object(self, id: PKType) -> ModelType:  # noqa: A002
        """Get object by ID asynchronously."""
        return cast(ModelType, await self.queryset.aget(pk=id))

    async def _save_object(self, obj: ModelType) -> None:
        """Save object asynchronously."""
        await obj.asave()

    async def _delete_object(self, obj: ModelType) -> None:  # type: ignore[override]
        """Delete object asynchronously."""
        await obj.adelete()

    async def _apply_updates(self, obj: ModelType, payload: UpdateSchemaType) -> None:  # type: ignore[override]
        """Apply updates to object asynchronously."""
        data = await self._handle_foreign_keys(payload.dict(exclude_unset=True))
        for attr, value in data.items():
            setattr(obj, attr, value)

    @property
    def list_items(self) -> ListItemsReturnType:
        """List items."""

        @paginate
        def _list_items(request: HttpRequest, filters: self.filter_schema = Query(...)) -> QuerySet[ModelType]:  # noqa: B008
            return cast(QuerySet[ModelType], filters.filter(self.queryset))

        return _list_items

    @property
    def get_item(self) -> GetItemReturnType:
        """Get item."""

        @rename(pk_name=self.pk_name)
        async def _get_item(request: HttpRequest, pk_name: self.pk_type) -> ModelType:
            try:
                return await self._get_object(pk_name)
            except self.model.DoesNotExist as e:
                raise EntryNotFound(self.model, pk_name) from e

        return _get_item

    @property
    def create_item(self) -> CreateItemReturnType:
        """Create item."""

        async def _create_item(request: HttpRequest, payload: self.create_schema) -> self.read_schema:  # type: ignore[E0611]
            try:
                data = payload.dict()

                # Handle foreign keys for remaining fields
                data = await self._handle_foreign_keys(data)

                # Create the object without M2M fields
                obj = await self.model.objects.acreate(**data)

            except (ValidationError, DatabaseError, ValueError) as e:
                raise BadRequest(self._format_error_message("creating", e)) from e
            else:
                return obj

        return _create_item

    @property
    def update_item(self) -> UpdateItemReturnType:
        """Update item."""

        @rename(pk_name=self.pk_name)
        async def _update_item(
            request: HttpRequest, pk_name: self.pk_type, payload: self.update_schema
        ) -> self.read_schema:  # type: ignore[E0611]
            try:
                obj = await self._get_object(pk_name)

                data = payload.dict(exclude_unset=True)

                # Handle foreign keys for remaining fields
                data = await self._handle_foreign_keys(data)

                # Update regular fields
                for attr, value in data.items():
                    setattr(obj, attr, value)

                await self._save_object(obj)

            except self.model.DoesNotExist:
                raise EntryNotFound(self.model, pk_name) from None
            except BadRequest:
                raise
            except Exception as e:
                raise BadRequest(self._format_error_message("updating", e)) from e
            else:
                return obj

        return _update_item

    @property
    def delete_item(self) -> DeleteItemReturnType:
        """Delete item."""

        @rename(pk_name=self.pk_name)
        async def _delete_item(request: HttpRequest, pk_name: self.pk_type) -> tuple[int, None]:
            try:
                obj = await self._get_object(pk_name)
                await self._delete_object(obj)

            except self.model.DoesNotExist as e:
                raise EntryNotFound(self.model, pk_name) from e

            except (ValueError, DatabaseError) as e:
                raise BadRequest(self._format_error_message("deleting", e)) from e

            else:
                return 204, None

        return _delete_item

    async def _handle_foreign_keys(self, data: dict) -> dict:
        """Handle foreign key relations by converting IDs to model instances (async version)."""
        for field in self.model._meta.get_fields():
            if (
                field.is_relation
                and not field.auto_created
                and field.concrete
                and not field.many_to_many
                and field.name in data
                and data[field.name] is not None
            ):
                related_model = cast(type[ModelType], field.related_model)
                fk_id = data[field.name]
                try:
                    data[field.name] = await related_model.objects.aget(pk=fk_id)
                except related_model.DoesNotExist as e:
                    msg = f"{related_model.__name__} with id {fk_id} not found"
                    raise BadRequest(msg) from e
        return data
