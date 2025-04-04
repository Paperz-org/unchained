import asyncio
import copy
import functools
from typing import Callable, get_args

from fast_depends import inject
from fast_depends.dependencies import model

from unchained.dependencies.header import BaseCustom
from unchained.signature import Signature, SignatureUpdater


class UnchainedBaseMeta(type):
    @staticmethod
    def _create_http_method(http_method_name: str, type_: type) -> Callable:
        """Factory to create HTTP method handlers with proper signature."""
        # TODO: we have a perfomance issue: we are creating partial functions for each reference to a dependency.
        # We should use only one partial function per dependency that need it.
        _with_request_dependency = []

        def method(self, *args, **kwargs):
            def _create_injected_decorator(http_method):
                def decorator(*decorator_args, **decorator_kwargs):
                    def wrapper(api_func):
                        if hasattr(api_func, "_original_api_func"):
                            api_func = api_func._original_api_func

                        
                        # Get the signature of the API function
                        api_func_signature = Signature.from_callable(api_func)
                        # TODO msut work but ????????????????????????????????????
                        # _original_signature = Signature.from_callable(api_func)
                        _original_signature = copy.deepcopy(api_func_signature)

                        for param_name, param in api_func_signature.parameters.items():
                            if Signature.param_is_annotated(param):
                                # If the parameter is Annotated, we need to extract the type and instance
                                # We use this to add the type in the CustomField.
                                # Because FastDepends don't inject the type in the CustomField.
                                # type_ is the type of the parameter
                                # instance is the instance of the parameter
                                # Exemple: a: Annotated[int, CustomField(dependency)]
                                # type_ is int
                                # instance is CustomField(dependency)
                                type_, instance = get_args(param.annotation)
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
                                    _with_request_dependency.extend(updater.partialised_dependencies)
                        
                        injected = inject(api_func)

                        # Update function signature with new parameters
                        # We remove the annotated parameters from the signature to allow Django Ninja to correctly parse the parameters
                        api_func.__signature__ = api_func_signature.new_signature_without_annotated()

                        def _prepare_execution(func_args, func_kwargs):
                            api_func.__signature__ = api_func_signature
                            # Get the request parameter
                            request = func_args[0]

                            # If the API function doesn't have a request parameter, we remove it from the arguments
                            if not api_func_signature.has_request_object:
                                func_args = func_args[1:]
                            # Inject the request parameter in all the partials function that have a request parameter
                            for dep in _with_request_dependency:
                                dep.dependency.keywords["request"] = request


                            return func_args, func_kwargs

                        # Here is the sync last decorator
                        @functools.wraps(api_func)
                        def decorated(*func_args, **func_kwargs):
                            func_args, func_kwargs = _prepare_execution(func_args, func_kwargs)
                            # This is the API result:
                            return injected(*func_args, **func_kwargs)

                        # Here is the async last decorator
                        @functools.wraps(api_func)
                        async def adecorated(*func_args, **func_kwargs):
                            func_args, func_kwargs = _prepare_execution(func_args, func_kwargs)
                            # This is the API result:
                            res = await injected(*func_args, **func_kwargs)
                            return res
    
                        result = http_method(*decorator_args, **decorator_kwargs)(
                            adecorated if asyncio.iscoroutinefunction(api_func) else decorated
                        )
                        api_func.__signature__ = _original_signature
                        result._original_api_func = api_func
                        return result

                    return wrapper

                return decorator

            original_method = getattr(super(type_, self), http_method_name)
            return _create_injected_decorator(original_method)(*args, **kwargs)

        method.__name__ = http_method_name
        method.__qualname__ = f"Unchained.{http_method_name}"

        return method


class UnchainedRouterMeta(UnchainedBaseMeta):
    urlpatterns: list[str]

    def __new__(cls, name, bases, attrs):
        # Create HTTP method decorators dynamically before class creation
        new_cls = super().__new__(cls, name, bases, attrs)
        for http_method in ["get", "post", "put", "patch", "delete"]:
            setattr(new_cls, http_method, cls._create_http_method(http_method, new_cls))
        return new_cls


class UnchainedMeta(UnchainedBaseMeta):
    urlpatterns: list[str]

    def __new__(cls, name, bases, attrs):
        from django import setup as django_setup
        from django.conf import settings as django_settings

        from unchained.settings import settings

        new_cls = super().__new__(cls, name, bases, attrs)

        # Create HTTP method decorators dynamically before class creation
        for http_method in ["get", "post", "put", "patch", "delete"]:
            setattr(new_cls, http_method, cls._create_http_method(http_method, new_cls))

        django_settings.configure(**settings.django.model_dump(), ROOT_URLCONF=new_cls)
        django_setup()

        new_cls.urlpatterns = []

        return new_cls
        return new_cls
