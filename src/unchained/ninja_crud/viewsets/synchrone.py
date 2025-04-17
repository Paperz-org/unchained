"""Synchrone implementation of the ViewSet."""

from typing import Callable, cast

from django.db.models import QuerySet
from django.http import HttpRequest

from unchained.ninja import Query
from unchained.ninja.pagination import paginate

from ..decorators import rename_parameter as rename
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
GetItemReturnType = Callable[[HttpRequest, PKType], ModelType]
CreateItemReturnType = Callable[[HttpRequest, CreateSchemaType], ModelType]
UpdateItemReturnType = Callable[[HttpRequest, PKType, UpdateSchemaType], ModelType]
DeleteItemReturnType = Callable[[HttpRequest, PKType], tuple[int, None]]


class SyncViewSet(BaseViewSet[ModelType, CreateSchemaType, ReadSchemaType, UpdateSchemaType, FilterSchemaType, PKType]):
    """Sync implementation of the ViewSet."""

    def _get_object(self, id: PKType) -> ModelType:  # noqa: A002
        """Get object by ID synchronously."""
        return cast(ModelType, self.queryset.get(pk=id))

    def _save_object(self, obj: ModelType) -> None:
        """Save object synchronously."""
        obj.save()

    def _delete_object(self, obj: ModelType) -> None:
        """Delete object synchronously."""
        obj.delete()

    def _apply_updates(self, obj: ModelType, payload: UpdateSchemaType) -> None:
        """Apply updates to object synchronously."""
        data = self._handle_foreign_keys(payload.dict(exclude_unset=True))
        # Extract m2m fields to handle them separately
        regular_data, m2m_fields = self._extract_m2m_fields(data)

        # Update regular fields
        for attr, value in regular_data.items():
            setattr(obj, attr, value)

        # Save the object before handling m2m fields
        self._save_object(obj)

        # Handle m2m fields after saving the object
        for field_name, values in m2m_fields.items():
            if values is not None and hasattr(obj, field_name):
                field = getattr(obj, field_name)
                # Validate that all provided IDs exist
                if values:
                    qs = field.model.objects.filter(pk__in=values)
                    found_ids = set(qs.values_list("pk", flat=True))
                    provided_ids = set(values)

                    # Check for invalid IDs
                    invalid_ids = provided_ids - found_ids
                    if invalid_ids:
                        msg = f"Invalid IDs {list(invalid_ids)} for {field_name}. These objects do not exist."
                        raise BadRequest(msg) from None

                    field.set(qs)
                else:
                    field.clear()

    @property
    def list_items(self) -> ListItemsReturnType:
        """List items."""

        @paginate
        def _list_items(request: HttpRequest, filters: self.filter_schema = Query(...)) -> QuerySet[ModelType]:  # noqa: B008
            """List items."""
            return cast(QuerySet[ModelType], filters.filter(self.queryset))

        return _list_items

    @property
    def get_item(self) -> GetItemReturnType:
        """Get item."""

        @rename(pk_name=self.pk_name)
        def _get_item(request: HttpRequest, pk_name: self.pk_type) -> ModelType:
            try:
                return self._get_object(pk_name)
            except self.model.DoesNotExist as e:
                raise EntryNotFound(self.model, pk_name) from e

        return _get_item

    @property
    def create_item(self) -> CreateItemReturnType:
        """Create item."""

        def _create_item(request: HttpRequest, payload: self.create_schema) -> ModelType:  # type: ignore[E0611]
            """Create item."""
            try:
                data = payload.dict()
                data, m2m_fields = self._extract_m2m_fields(data)

                # Handle foreign keys for remaining fields
                data = self._handle_foreign_keys(data)

                # Create the object without M2M fields
                obj = self.model.objects.create(**data)

                # Set M2M fields after creation
                for field_name, values in m2m_fields.items():
                    if values is not None:
                        field = getattr(obj, field_name)
                        qs = field.model.objects.filter(pk__in=values)
                        field.set(qs)
            except Exception as e:
                raise BadRequest(self._format_error_message("creating", e)) from e
            else:
                return obj

        return _create_item

    @property
    def update_item(self) -> UpdateItemReturnType:
        """Update item."""

        @rename(pk_name=self.pk_name)
        def _update_item(request: HttpRequest, pk_name: self.pk_type, payload: self.update_schema) -> ModelType:  # type: ignore[E0611]
            """Update item."""
            try:
                obj = self._get_object(pk_name)

                data = payload.dict(exclude_unset=True)
                data, m2m_fields = self._extract_m2m_fields(data)

                # Handle foreign keys for remaining fields
                data = self._handle_foreign_keys(data)

                # Update regular fields
                for attr, value in data.items():
                    setattr(obj, attr, value)

                self._save_object(obj)

                # Set M2M fields after saving
                for field_name, values in m2m_fields.items():
                    if values is not None and hasattr(obj, field_name):
                        field = getattr(obj, field_name)
                        # Validate that all provided IDs exist
                        if values:
                            qs = field.model.objects.filter(pk__in=values)
                            found_ids = set(qs.values_list("pk", flat=True))
                            provided_ids = set(values)

                            # Check for invalid IDs
                            invalid_ids = provided_ids - found_ids
                            if invalid_ids:
                                msg = f"Invalid IDs {list(invalid_ids)} for {field_name}. These objects do not exist."
                                raise BadRequest(msg) from None  # noqa: TRY301

                            field.set(qs)
                        else:
                            field.clear()

            except self.model.DoesNotExist as e:
                raise EntryNotFound(self.model, pk_name) from e
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
        def _delete_item(request: HttpRequest, pk_name: self.pk_type) -> tuple[int, None]:
            """Delete item."""
            try:
                obj = self._get_object(pk_name)
                self._delete_object(obj)
            except self.model.DoesNotExist:
                raise EntryNotFound(self.model, pk_name) from None
            except Exception as e:
                raise BadRequest(self._format_error_message("deleting", e)) from e
            else:
                return 204, None

        return _delete_item

    def _handle_foreign_keys(self, data: dict) -> dict:
        """Handle foreign key relations by converting IDs to model instances (sync version)."""
        for field in self.model._meta.get_fields():
            if (
                field.is_relation
                and not field.auto_created
                and field.concrete
                and not field.many_to_many
                and (field.name in data and data[field.name] is not None)
            ):
                related_model = cast(type[ModelType], field.related_model)
                fk_id = data[field.name]
                try:
                    data[field.name] = related_model.objects.get(pk=fk_id)
                except related_model.DoesNotExist as e:
                    msg = f"{related_model.__name__} with id {fk_id} not found"
                    raise BadRequest(msg) from e
        return data
