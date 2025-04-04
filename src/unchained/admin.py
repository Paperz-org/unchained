from typing import TYPE_CHECKING, Iterable

from django.contrib import admin
from django.contrib.admin import ModelAdmin

if TYPE_CHECKING:
    from unchained.models.base import BaseModel


class UnchainedAdmin:
    def register(
        self,
        model_or_iterable: type["BaseModel"] | Iterable[type["BaseModel"]],
        admin_class: type[ModelAdmin] | None = None,
        **options,
    ):
        admin.site.register(model_or_iterable, admin_class, **options)

    def unregister(self, model):
        admin.site.unregister(model)

    def get_urls(self):
        return admin.site.get_urls()
