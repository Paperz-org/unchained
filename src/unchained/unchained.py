import functools
import inspect
from functools import cached_property, partial
from typing import TYPE_CHECKING, Annotated, Any, Callable, get_args, get_origin

from django.db.models import QuerySet
from django.http import HttpRequest
from fast_depends import inject
from fast_depends.dependencies import model
from fast_depends.library import CustomField
from ninja import NinjaAPI

from .admin import UnchainedAdmin
from .settings import DEFAULT as DEFAULT_SETTINGS

if TYPE_CHECKING:
    from .models.base import BaseModel


def _has_request_in_signature(signature: inspect.Signature) -> bool:
    for _, param in signature.parameters.items():
        annotation = param.annotation
        if hasattr(annotation, "__origin__") and get_origin(annotation) is Annotated:
            continue
        if issubclass(annotation, HttpRequest):
            return True
    return False


def _has_request_in_signature_from_func(func: Callable) -> bool:
    signature = inspect.signature(func)
    return _has_request_in_signature(signature)


def _param_type_is_annotated(param_type: Any) -> bool:
    return hasattr(param_type, "__origin__") and get_origin(param_type) is Annotated


def _get_new_signature_without_request(signature: inspect.Signature) -> inspect.Signature:
    parameters = []
    for _, param in signature.parameters.items():
        annotation = param.annotation
        if hasattr(annotation, "__origin__") and get_origin(annotation) is Annotated:
            continue
        if issubclass(annotation, HttpRequest):
            continue
        parameters.append(param)

    return inspect.Signature(parameters)


def _get_new_signature_without_request_but_with_depends(signature: inspect.Signature) -> inspect.Signature:
    parameters = []
    for _, param in signature.parameters.items():
        annotation = param.annotation
        if hasattr(annotation, "__origin__") and get_origin(annotation) is Annotated:
            parameters.append(param)
            continue
        if issubclass(annotation, HttpRequest):
            continue
        parameters.append(param)

    return inspect.Signature(parameters)


def _get_depends_dependency(func: Callable) -> Callable:
    signature = inspect.signature(func)
    for _, param in signature.parameters.items():
        if not _param_type_is_annotated(param.annotation):
            continue
        else:
            type_, instance = get_args(param.annotation)
            if isinstance(instance, model.Depends):
                return instance.dependency
    return None


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

        def _register_deep_dependencies(signature: inspect.Signature):
            for _, param in signature.parameters.items():
                param_type = param.annotation
                if not _param_type_is_annotated(param_type):
                    continue
                type_, instance = get_args(param_type)

                if isinstance(instance, model.Depends):
                    # If the dependency has a request parameter, we need to remove it
                    # because we will inject the request parameter later
                    # We need to update the signature because FastDepends will create a model based on the signature.
                    dependency_signature = inspect.signature(instance.dependency)
                    _register_deep_dependencies(dependency_signature)
                    signature_without_request = _get_new_signature_without_request_but_with_depends(
                        dependency_signature
                    )
                    if _has_request_in_signature(dependency_signature):
                        instance.dependency = partial(instance.dependency, request=None)
                        instance.dependency.__signature__ = signature_without_request
                        # We need to store the signature without the request to inject it later
                        # because we will create a partial function with the request parameter
                        # and the signature of the partial function will be different
                        _with_request_dependency.append(instance)

        def method(self, *args, **kwargs):
            def _create_injected_decorator(http_method):
                def decorator(*decorator_args, **decorator_kwargs):
                    def wrapper(api_func):
                        # Get the signature of the API function
                        api_func_signature = inspect.signature(api_func)

                        # Check if the API function has a request parameter
                        # We do this to allow the api function to not have the request parameter if it's not necessary
                        # Based on this boolean, we will inject the request parameter or not.
                        api_func_has_request_param = _has_request_in_signature(api_func_signature)

                        # Remove Annotated from parameter annotations
                        without_annotated_parameters = []
                        for _, param in api_func_signature.parameters.items():
                            param_type = param.annotation
                            if not _param_type_is_annotated(param_type):
                                without_annotated_parameters.append(param)
                            else:
                                # If the parameter is Annotated, we need to extract the type and instance
                                # We use this to add the type in the CustomField.
                                # Because FastDepends don't inject the type in the CustomField.
                                # type_ is the type of the parameter
                                # instance is the instance of the parameter
                                # Exemple: a: Annotated[int, CustomField(dependency)]
                                # type_ is int
                                # instance is CustomField(dependency)
                                type_, instance = get_args(param_type)
                                if isinstance(instance, CustomField):
                                    # Add the type to the CustomField
                                    setattr(instance, "_annotation_types", type_)
                                if isinstance(instance, model.Depends) and not api_func_has_request_param:
                                    # If the dependency has a request parameter, we need to remove it
                                    # because we will inject the request parameter later
                                    # We need to update the signature because FastDepends will create a model based on the signature.
                                    dependency_signature = inspect.signature(instance.dependency)
                                    _register_deep_dependencies(dependency_signature)
                                    signature_without_request = _get_new_signature_without_request_but_with_depends(
                                        dependency_signature
                                    )
                                    if _has_request_in_signature(dependency_signature):
                                        instance.dependency = partial(instance.dependency, request=None)
                                        instance.dependency.__signature__ = signature_without_request
                                        # We need to store the signature without the request to inject it later
                                        # because we will create a partial function with the request parameter
                                        # and the signature of the partial function will be different
                                        _with_request_dependency.append(instance)

                        injected = inject(api_func)

                        # Update function signature with new parameters
                        # We remove the annotated parameters from the signature to allow Django Ninja to correctly parse the parameters
                        api_func.__signature__ = inspect.Signature(without_annotated_parameters)

                        @functools.wraps(api_func)
                        def decorated(*func_args, **func_kwargs):
                            if not api_func_has_request_param:
                                request = func_args[0]
                                func_args = func_args[1:]
                                for dep in _with_request_dependency:
                                    dep.dependency.keywords["request"] = request
                            # This is the API result:
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
