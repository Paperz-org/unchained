from django.http import HttpRequest as DjangoHttpRequest
from fast_depends import Depends

from . import app, models
from .settings import DEFAULT

# Need to be first ?
from .unchained import Unchained

Request = DjangoHttpRequest

__all__ = ["Unchained", "models", "DEFAULT", "Depends", "Request"]
