import importlib
import sys

from pydantic import Field, PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict

from unchained.settings.django import BaseDjangoSettings, DefaultDjangoSettings


class UnchainedSettings(BaseSettings):
    _django: BaseDjangoSettings = PrivateAttr()

    @property
    def django(self) -> BaseDjangoSettings:
        return self._django

    @django.setter
    def django(self, value: BaseDjangoSettings):
        self._django = value

    SETTINGS_MODULE: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
        case_sensitive=False,
        env_prefix="UNCHAINED_",
        env_nested_delimiter="__",
    )

    def add_settings(self, settings: BaseSettings):
        for key, value in settings.model_dump().items():
            setattr(self, key, value)


def load_settings() -> UnchainedSettings:
    _django_future_settings = {}
    unchained_settings = UnchainedSettings()

    unchained_settings_module = unchained_settings.SETTINGS_MODULE
    if not unchained_settings_module:
        unchained_settings.django = DefaultDjangoSettings()
        return unchained_settings

    original_sys_path = sys.path.copy()
    if "" not in sys.path:
        sys.path.insert(0, "")

    try:
        module = importlib.import_module(unchained_settings_module)

        for attr_name in dir(module):
            attr_value = getattr(module, attr_name)
            if attr_name.startswith("_"):
                continue
            if issubclass(attr_value, UnchainedSettings):
                unchained_settings.add_settings(attr_value())
            elif issubclass(attr_value, BaseDjangoSettings):
                unchained_settings.django = attr_value()
            elif attr_name.isupper() and not attr_name.startswith("_") and not attr_name.startswith("DJANGO_"):
                setattr(unchained_settings, attr_name, attr_value)
            elif attr_name.isupper() and not attr_name.startswith("_") and attr_name.startswith("DJANGO_"):
                _django_future_settings.update({attr_name[7:]: attr_value})

    finally:
        sys.path = original_sys_path

    if not hasattr(unchained_settings, "django"):
        unchained_settings.django = DefaultDjangoSettings()

    for key, value in _django_future_settings.items():
        setattr(unchained_settings.django, key, value)  # type: ignore

    return unchained_settings
