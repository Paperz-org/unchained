from django.http import HttpRequest as DjangoHttpRequest
from fast_depends import Depends

from . import app, models
from .unchained import Unchained

Request = DjangoHttpRequest

__all__ = ["Unchained", "models", "Depends", "Request"]
