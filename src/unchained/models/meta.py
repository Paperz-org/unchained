import logging
from typing import Any, List, Type

from django.db import models


class MainAppModelMeta(models.base.ModelBase):
    """Metaclass that automatically sets app_label to 'app' for all models"""

    # Class variable to track all models created with this metaclass
    models_registry: List[Type] = []

    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> "MainAppModelMeta":
        # Set app_label in Meta if not already set
        if "Meta" not in attrs:
            attrs["Meta"] = type("Meta", (), {"app_label": "app"})
        elif not hasattr(attrs["Meta"], "app_label"):
            setattr(attrs["Meta"], "app_label", "app")

        # Create the model class
        model_class = super().__new__(cls, name, bases, attrs)
        # And register it
        cls.models_registry.append(model_class)
        logging.debug(cls.models_registry)
        return model_class
