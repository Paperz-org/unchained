import functools
from functools import cached_property
from typing import TYPE_CHECKING, Annotated, Any, Callable, get_args, get_origin

from django.db.models import QuerySet
from fast_depends import inject
from fast_depends.dependencies import model
from ninja import NinjaAPI

from unchained.dependencies.header import BaseCustom  # type: ignore
from unchained.signature import Signature, SignatureUpdater  # type: ignore

from .admin import UnchainedAdmin
from .settings import DEFAULT as DEFAULT_SETTINGS

if TYPE_CHECKING:
    from .models.base import BaseModel


def _param_type_is_annotated(param_type: Any) -> bool:
    return hasattr(param_type, "__origin__") and get_origin(param_type) is Annotated


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
        _with_request_dependency = []

        def method(self, *args, **kwargs):
            def _create_injected_decorator(http_method):
                def decorator(*decorator_args, **decorator_kwargs):
                    def wrapper(api_func):
                        # Get the signature of the API function
                        api_func_signature = Signature.from_callable(api_func)

                        for param_name, param in api_func_signature.parameters.items():
                            param_type = param.annotation
                            if _param_type_is_annotated(param_type):
                                # If the parameter is Annotated, we need to extract the type and instance
                                # We use this to add the type in the CustomField.
                                # Because FastDepends don't inject the type in the CustomField.
                                # type_ is the type of the parameter
                                # instance is the instance of the parameter
                                # Exemple: a: Annotated[int, CustomField(dependency)]
                                # type_ is int
                                # instance is CustomField(dependency)
                                type_, instance = get_args(param_type)
                                if isinstance(instance, BaseCustom):
                                    # Add the type to the CustomField
                                    setattr(instance, "param_name", param_name)
                                    setattr(instance, "annotation_type", type_)
                                if isinstance(instance, model.Depends):
                                    # If the dependency has a request parameter, we need to remove it
                                    # because we will inject the request parameter later
                                    # We need to update the signature because FastDepends will create a model based on the signature.
                                    # This operation must be done recursively to update all the dependencies
                                    # See SignatureUpdater for more details

                                    updater = SignatureUpdater()
                                    updater.update_deep_dependencies(instance)
                                    _with_request_dependency.extend(
                                        updater.partialised_dependencies
                                    )

                        injected = inject(api_func)

                        # Update function signature with new parameters
                        # We remove the annotated parameters from the signature to allow Django Ninja to correctly parse the parameters
                        api_func.__signature__ = (
                            api_func_signature.new_signature_without_annotated()
                        )

                        @functools.wraps(api_func)
                        def decorated(*func_args, **func_kwargs):
                            api_func.__signature__ = api_func_signature
                            # Get the request parameter
                            request = func_args[0]

                            # If the API function doesn't have a request parameter, we remove it from the arguments
                            if not api_func_signature.has_request_object:
                                func_args = func_args[1:]

                            # Inject the request parameter in all the partials function that have a request parameter
                            for dep in _with_request_dependency:
                                dep.dependency.keywords["request"] = request

                            # This is the API result:
                            return injected(*func_args, **func_kwargs)

                        return http_method(*decorator_args, **decorator_kwargs)(
                            decorated
                        )

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
        task_workers: int = 2,
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

        # Start the task workers when the app is initialized
        # self.task_manager.start()

        original_app = get_asgi_application()

        # Wrap the ASGI app to handle cleanup on shutdown
        async def wrapped_app(scope, receive, send):
            return await original_app(scope, receive, send)

        return wrapped_app

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
            self.urlpatterns += static(
                settings.STATIC_URL, document_root=settings.STATIC_ROOT
            )
        return self.app
