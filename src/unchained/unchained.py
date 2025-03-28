from functools import cached_property
from typing import List, Type

from .settings import DEFAULT as DEFAULT_SETTINGS


class UnchainedMeta(type):
    urlpatterns: list[str]

    def __new__(cls, name, bases, attrs):
        from django import setup as django_setup
        from django.conf import settings as django_settings

        new_cls = super().__new__(cls, name, bases, attrs)
        django_settings.configure(**DEFAULT_SETTINGS, ROOT_URLCONF=new_cls)
        django_setup()
        new_cls.urlpatterns = []
        return new_cls


class Unchained(metaclass=UnchainedMeta):
    # Initialize all_models as empty, we'll populate it after Django setup
    all_models: List[Type] = []
    APP_NAME = "unchained.app"

    def __init__(self):
        from django.urls import path

        self._path = path

        from ninja import NinjaAPI

        self.api = NinjaAPI()

        self.app_config_class: Type | None = None
        self.models: list[Type] = []

    @cached_property
    def app(self):
        from django.core.asgi import get_asgi_application

        return get_asgi_application()

    def __getattr__(self, item):
        attr = getattr(self.api, item, None)
        if attr:
            return attr

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{item}'"
        )

    def __call__(self, *args, **kwargs):
        self.urlpatterns.append(self._path("api/", self.api.urls))
        return self.app
