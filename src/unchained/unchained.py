from contextlib import asynccontextmanager, contextmanager
from functools import cached_property, wraps
from typing import TYPE_CHECKING, Any, Callable

from django.db.models import QuerySet
from django.urls import URLPattern, URLResolver, include, path
from ninja import NinjaAPI


from unchained.admin import UnchainedAdmin
from unchained.meta import URLPatterns, UnchainedMeta
from unchained.lifespan import Lifespan
import inspect


if TYPE_CHECKING:
    from .models.base import BaseModel
 
class Unchained(NinjaAPI, metaclass=UnchainedMeta):
    APP_NAME = "unchained.app"
    urlpatterns = URLPatterns()

    def __init__(
        self,
        admin: UnchainedAdmin | None = None,
        lifespan: Callable | None = None,
        **kwargs,
    ):
        from django.urls import path

        self._path = path
        self.admin = admin or UnchainedAdmin()
        self._lifespan = self._wrap_lifespan(lifespan) if lifespan else None    

        # Call parent init
        super().__init__(**kwargs)

    
    def lifespan(self, func: Callable):
        if self._lifespan:
            raise ValueError("Lifespan already set")

        self._lifespan = self._wrap_lifespan(func)
    
        return func
    
    @staticmethod
    def _wrap_lifespan(func: Callable):
        if inspect.isgeneratorfunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                sync_cm = contextmanager(func)
                with sync_cm(*args, **kwargs) as value:
                    yield value
            
            return asynccontextmanager(async_wrapper)

        elif inspect.isasyncgenfunction(func):
            # For async generator functions
            return asynccontextmanager(func)
    
        else:
            raise ValueError("Lifespan function must be a generator function")

    @property
    def app(self):
        """Return the ASGI application wrapped with lifespan middleware."""
        from django.core.asgi import get_asgi_application
        
        # Get the Django ASGI application
        django_app = get_asgi_application()
        
        return Lifespan(django_app, self._lifespan)

    def crud(
        self,
        model: "BaseModel",
        create_schema: Any | None = None,
        read_schema: Any | None = None,
        update_schema: Any | None = None,
        filter_schema: Any | None = None,
        path: str | None = None,
        tags: list[str] | None = None,
        queryset: QuerySet | None = None,
        operations: str = "CRUD",
    ):
        from ninja_crud import CRUDRouter  # type: ignore

        router = CRUDRouter(
            model,
            create_schema=create_schema,
            read_schema=read_schema,
            update_schema=update_schema,
            filter_schema=filter_schema,
            path=path,
            tags=tags,
            queryset=queryset,
            operations=operations,
        )    

    def __call__(self, *args, **kwargs):
        from django.conf import settings
        from django.conf.urls.static import static
        from django.contrib import admin

        self.urlpatterns.add(self._path("api/", self.urls))
        self.urlpatterns.add(self._path("admin/", admin.site.urls))
        if settings.DEBUG:
            self.urlpatterns.add(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
        return self.app
    

    @staticmethod
    def is_generator_function(func):
        """Check if the function is a generator function (uses yield)."""
        return inspect.isasyncgenfunction(func)
    