from functools import cached_property
from typing import TYPE_CHECKING, List, Type

from ninja import NinjaAPI

from .settings import DEFAULT as DEFAULT_SETTINGS

if TYPE_CHECKING:
    from .models.base import BaseModel


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


class Unchained(NinjaAPI, metaclass=UnchainedMeta):
    # Initialize all_models as empty, we'll populate it after Django setup
    all_models: List[Type] = []
    APP_NAME = "unchained.app"

    def __init__(self):
        from django.urls import path

        self._path = path

        # from ninja import NinjaAPI

        # self.api = NinjaAPI()

        self.app_config_class: Type | None = None
        self.models: list[Type] = []

        super().__init__()

    @cached_property
    def app(self):
        from django.core.asgi import get_asgi_application

        return get_asgi_application()

    def crud(self, model: "BaseModel"):
        from ninja_crud import CRUDRouter

        router = CRUDRouter(model)

        self.add_router(router.path, router.router)

    def __call__(self, *args, **kwargs):
        self.urlpatterns.append(self._path("api/", self.urls))
        return self.app
