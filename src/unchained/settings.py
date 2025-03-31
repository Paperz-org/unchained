import importlib
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import Field, field_validator
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

UNCHAINED_SETTINGS_MODULE = os.environ.get("UNCHAINED_SETTINGS_MODULE")

_BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FIXED_STATIC_ROOT = os.path.join(_BASE_DIR, "unchained/static")

# Original Django settings dictionary
DEFAULT: Dict[str, Any] = {
    "DEBUG": True,
    "SECRET_KEY": "your-secret-key-here",
    "ALLOWED_HOSTS": ["*"],
    "MIDDLEWARE": [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",  # Required for admin
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",  # Required for admin
        "django.contrib.messages.middleware.MessageMiddleware",  # Required for admin
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ],
    "INSTALLED_APPS": [
        "jazzmin",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",  # Added staticfiles app
        "unchained.app",
    ],
    "MIGRATION_MODULES": {
        # ????? It makes no sense as app should be unchained.app and if not migration
        # is supposed to be kind of local... But it works........
        "app": "migrations",
    },
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    },
    "TEMPLATES": [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",  # Required for admin
                    "django.contrib.messages.context_processors.messages",  # Required for admin
                ],
            },
        },
    ],
    # Added static files configuration
    "STATIC_URL": "/static/",
    "STATIC_ROOT": FIXED_STATIC_ROOT,
    "JAZZMIN_SETTINGS": {
        "site_title": "Unchained",
        "site_header": "Unchained",
        "site_brand": "Unchained App",
        "show_ui_builder": True,
        "dark_mode_theme": "darkly",
    },
}


class DjangoSettingsSource(PydanticBaseSettingsSource):
    """
    A settings source for Pydantic that reads values from a Django settings module.
    """

    def __init__(self, settings_module: Optional[str] = None):
        """
        Initialize the settings source.

        Args:
            settings_module: The path to the settings module. If None, will try to read
                             from UNCHAINED_SETTINGS_MODULE environment variable.
        """
        self.settings_module = settings_module
        self._settings_cache = None

    def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Load settings from the Django settings module.

        Returns:
            Dictionary with the settings values from the Django settings module.
        """
        django_settings = self._get_django_settings()

        # Extract all uppercase attributes (following Django's convention)
        values = {}
        for key in dir(django_settings):
            if key.isupper():
                # Skip STATIC_ROOT since it must not be changed
                if key == "STATIC_ROOT":
                    continue
                values[key] = getattr(django_settings, key)

        return values

    def _get_django_settings(self) -> ModuleType:
        """Load the Django settings module."""
        if self.settings_module is None:
            self.settings_module = os.environ.get("UNCHAINED_SETTINGS_MODULE") or os.environ.get(
                "DJANGO_SETTINGS_MODULE"
            )

        if not self.settings_module:
            raise ValueError(
                "Settings module not specified. Set UNCHAINED_SETTINGS_MODULE "
                "environment variable or pass settings_module to DjangoSettingsSource."
            )

        try:
            return self._import_settings_module(self.settings_module)
        except ImportError as e:
            raise ImportError(f"Could not import settings '{self.settings_module}': {e}")

    def _import_settings_module(self, module_path: str) -> ModuleType:
        """
        Import the settings module.

        Args:
            module_path: The path to the module.

        Returns:
            The imported module.
        """
        # Add the current directory to sys.path if it's not already there
        original_sys_path = sys.path.copy()
        if "" not in sys.path:
            sys.path.insert(0, "")

        try:
            return importlib.import_module(module_path)
        finally:
            # Restore the original sys.path
            sys.path = original_sys_path

    def get_field_value(self, field: FieldInfo, field_name: str) -> Tuple[Any, str, bool]:
        """
        Get value for a field from Django settings.

        Args:
            field: The field info from Pydantic.
            field_name: The name of the field.

        Returns:
            Tuple of (value, source, found) where found is a boolean indicating if the value was found.
        """
        # For STATIC_ROOT, always return the fixed value
        if field_name == "STATIC_ROOT":
            return FIXED_STATIC_ROOT, "fixed_config", True

        django_settings = self._get_django_settings()

        # Check if the field exists in Django settings
        if hasattr(django_settings, field_name):
            return getattr(django_settings, field_name), f"settings:{self.settings_module}", True

        return None, "", False


class UnchainedSettings(BaseSettings):
    DEBUG: bool = DEFAULT["DEBUG"]
    SECRET_KEY: str = DEFAULT["SECRET_KEY"]
    ALLOWED_HOSTS: List[str] = DEFAULT["ALLOWED_HOSTS"]
    MIDDLEWARE: List[str] = DEFAULT["MIDDLEWARE"]
    INSTALLED_APPS: List[str] = DEFAULT["INSTALLED_APPS"]
    MIGRATION_MODULES: Dict[str, str] = DEFAULT["MIGRATION_MODULES"]
    DATABASES: Dict[str, Dict[str, Any]] = DEFAULT["DATABASES"]
    TEMPLATES: List[Dict[str, Any]] = DEFAULT["TEMPLATES"]
    STATIC_URL: str = DEFAULT["STATIC_URL"]
    # Set a frozen value for STATIC_ROOT that cannot be overridden
    STATIC_ROOT: str = Field(default=FIXED_STATIC_ROOT, frozen=True)
    JAZZMIN_SETTINGS: Dict[str, Any] = DEFAULT["JAZZMIN_SETTINGS"]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
        env_prefix="UNCHAINED_",
        env_nested_delimiter="__",
        case_sensitive=True,
    )

    @field_validator("INSTALLED_APPS")
    def validate_unchained_settings_module(cls, v: List[str]) -> List[str]:
        if "unchained.app" not in v:
            v.append("unchained.app")
        return v

    @field_validator("MIGRATION_MODULES")
    def validate_migration_modules(cls, v: Dict[str, str]) -> Dict[str, str]:
        if "app" not in v:
            v["app"] = "migrations"
        return v

    # Force STATIC_ROOT to always have the fixed value
    @field_validator("STATIC_ROOT")
    def validate_static_root(cls, v: str) -> str:
        # Always return the fixed value regardless of what was set
        return FIXED_STATIC_ROOT

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        # The order determines priority - later sources override earlier ones
        sources = (init_settings, env_settings, dotenv_settings)

        #  Here we should check on pyproject.toml too
        if os.environ.get("UNCHAINED_SETTINGS_MODULE") or os.environ.get("DJANGO_SETTINGS_MODULE"):
            return (DjangoSettingsSource(), *sources)

        return sources

    def as_django_dict(self) -> Dict[str, Any]:
        """Convert settings to a dictionary suitable for Django configuration."""
        # Return the settings as a dictionary for Django
        return self.model_dump()


settings = UnchainedSettings()
