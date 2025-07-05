from unchained import context
from typing import Callable, get_args

from fast_depends import inject

from unchained.dependencies.custom import BaseCustom
from unchained.signature import Signature
import functools
import copy
import asyncio

from unchained.signature.transformers import create_signature_with_auto_dependencies, create_signature_without_annotated


class UnchainedBaseMeta(type):
    @staticmethod
    def _create_http_method(http_method_name: str, type_: type) -> Callable:
        """Factory to create HTTP method handlers with proper signature."""

        def method(self, *args, **kwargs):
            def _create_injected_decorator(http_method):
                def decorator(*decorator_args, **decorator_kwargs):
                    def wrapper(api_func):

                        signature = Signature.from_callable(api_func)

                        for param_name, param in signature.parameters.items():
                            if param.is_custom_depends:
                                type_, instance = get_args(param.annotation)
                                if isinstance(instance, BaseCustom):
                                    setattr(instance, "param_name", param_name)
                                    setattr(instance, "annotation_type", type_)
                                    setattr(instance, "default", param.default)

                        signature_with_auto_dependencies = create_signature_with_auto_dependencies(signature)

                        api_func.__signature__ = signature_with_auto_dependencies

            
                        # Here is the sync last decorator
                        @functools.wraps(api_func)
                        def decorated(*func_args, **func_kwargs):
                            # This is the API result:
                            return api_func(*func_args, **func_kwargs)

                        # Here is the async last decorator
                        @functools.wraps(api_func)
                        async def adecorated(*func_args, **func_kwargs):
                            # This is the API result:
                            res = await api_func(*func_args, **func_kwargs)
                            return res

                        result = http_method(*decorator_args, **decorator_kwargs)(
                            adecorated if asyncio.iscoroutinefunction(api_func) else decorated
                        )

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


class URLPatterns(list):
    def add(self, value):
        if isinstance(value, list):
            self.extend(value)
        else:
            self.append(value)


class UnchainedMeta(UnchainedBaseMeta):
    urlpatterns = URLPatterns()

    def __new__(cls, name, bases, attrs):
        from django import setup as django_setup
        from django.conf import settings as django_settings

        from unchained.settings import settings

        new_cls = super().__new__(cls, name, bases, attrs)

        # Create HTTP method decorators dynamically before class creation
        for http_method in ["get", "post", "put", "patch", "delete"]:
            setattr(new_cls, http_method, cls._create_http_method(http_method, new_cls))

        django_settings.configure(**settings.django.get_settings(), ROOT_URLCONF=new_cls)
        django_setup()

        new_cls.settings = settings

        return new_cls
