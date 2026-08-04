from contextvars import ContextVar
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from unchained.base import BaseUnchained

app: ContextVar[Optional["BaseUnchained"]] = ContextVar("app", default=None)
