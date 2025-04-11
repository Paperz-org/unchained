"""ninja-crud - Django Ninja utilities for creating CRUD APIs from django models."""

from .exceptions import BadRequest, EntryNotFound
from .routers import CRUDRouter
from .viewsets import AsyncViewSet, SyncViewSet
from .viewsets.base import BaseViewSet

__all__ = ["AsyncViewSet", "BadRequest", "BaseViewSet", "CRUDRouter", "EntryNotFound", "SyncViewSet"]

__version__ = "0.1.0"
