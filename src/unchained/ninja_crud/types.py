"""Types for the library."""

from typing import TypeVar

from django.db import models

from unchained.ninja_crud.filter_schema import FilterSchema
from unchained.ninja_crud.schema import Schema

ModelType = TypeVar("ModelType", bound=models.Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=Schema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=Schema)
ReadSchemaType = TypeVar("ReadSchemaType", bound=Schema)
FilterSchemaType = TypeVar("FilterSchemaType", bound=FilterSchema)
PKType = TypeVar("PKType", bound=object)
