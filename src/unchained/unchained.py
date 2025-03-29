import functools
import inspect
from functools import cached_property
from typing import TYPE_CHECKING, Annotated, Any, Callable, get_origin

from django.db.models import QuerySet
from fast_depends import inject
from ninja import NinjaAPI

from .admin import UnchainedAdmin
from .settings import DEFAULT as DEFAULT_SETTINGS

if TYPE_CHECKING:
    from .models.base import BaseModel


class UnchainedMeta(type):
    urlpatterns: list[str]

    def __new__(cls, name, bases, attrs):
        from django import setup as django_setup
        from django.conf import settings as django_settings

        # Create HTTP method decorators dynamically before class creation
        for http_method in ["get", "post", "put", "patch", "delete"]:
            attrs[http_method] = cls._create_http_method(http_method)

        new_cls = super().__new__(cls, name, bases, attrs)

        django_settings.configure(**DEFAULT_SETTINGS, ROOT_URLCONF=new_cls)
        django_setup()

        new_cls.urlpatterns = []

        return new_cls

    @staticmethod
    def _create_http_method(http_method_name: str) -> Callable:
        """Factory to create HTTP method handlers with proper signature."""

        def method(self, *args, **kwargs):
            def _create_injected_decorator(http_method):
                def decorator(*decorator_args, **decorator_kwargs):
                    def wrapper(func):
                        func_signature = inspect.signature(func)
                        # Remove Annotated from parameter annotations
                        parameters = []
                        for _, param in func_signature.parameters.items():
                            annotation = param.annotation
                            if not (hasattr(annotation, "__origin__") and get_origin(annotation) is Annotated):
                                parameters.append(param)

                        # Update function signature with new parameters
                        func.__signature__ = inspect.Signature(parameters)

                        @functools.wraps(func)
                        def decorated(*func_args, **func_kwargs):
                            func.__signature__ = func_signature
                            injected = inject(func)
                            return injected(*func_args, **func_kwargs)

                        return http_method(*decorator_args, **decorator_kwargs)(decorated)

                    return wrapper

                return decorator

            original_method = getattr(super(Unchained, self), http_method_name)
            return _create_injected_decorator(original_method)(*args, **kwargs)

        method.__name__ = http_method_name
        method.__qualname__ = f"Unchained.{http_method_name}"

        return method


class Unchained(NinjaAPI, metaclass=UnchainedMeta):
    APP_NAME = "unchained.app"

    def __init__(
        self,
        admin: UnchainedAdmin | None = None,
        **kwargs,
    ):
        from django.urls import path

        self._path = path
        self.admin = admin or UnchainedAdmin()

        # Call parent init
        super().__init__(**kwargs)

    @cached_property
    def app(self):
        from django.core.asgi import get_asgi_application

        return get_asgi_application()

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

        self.add_router(router.path, router.router)

    def __call__(self, *args, **kwargs):
        from django.conf import settings
        from django.conf.urls.static import static
        from django.contrib import admin

        self.urlpatterns.append(self._path("api/", self.urls))
        self.urlpatterns.append(self._path("admin/", admin.site.urls))
        if settings.DEBUG:
            self.urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        return self.app
