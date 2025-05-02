from django.db import models

from .meta import MainAppModelMeta


class BaseModel(models.Model, metaclass=MainAppModelMeta):
    """
    Base model class that automatically sets app_label to 'app'
    All models should inherit from this class instead of models.Model
    """

    class Meta:
        abstract = True

