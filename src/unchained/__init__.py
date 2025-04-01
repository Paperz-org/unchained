from django.http import HttpRequest as DjangoHttpRequest
from fast_depends import Depends

from . import app, models

# Need to be first ?
from .unchained import Unchained

Request = DjangoHttpRequest

__all__ = ["Unchained", "models", "Depends", "Request"]
