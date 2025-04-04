from functools import cached_property
from typing import TYPE_CHECKING, Any

from django.db.models import QuerySet
from django.urls import URLPattern, URLResolver, include, path
from ninja import NinjaAPI


from unchained.admin import UnchainedAdmin
from unchained.meta import URLPatterns, UnchainedMeta

if TYPE_CHECKING:
    from .models.base import BaseModel
 
class Unchained(NinjaAPI, metaclass=UnchainedMeta):
    APP_NAME = "unchained.app"
    urlpatterns = URLPatterns()

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

    def __call__(self, *args, **kwargs):
        from django.conf import settings
        from django.conf.urls.static import static
        from django.contrib import admin

        self.urlpatterns.add(self._path("api/", self.urls))
        self.urlpatterns.add(self._path("admin/", admin.site.urls))
        if settings.DEBUG:
            self.urlpatterns.add(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
        return self.app
    

