import os
from pathlib import Path
from typing import Any, Dict, List, Self

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

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


class DjangoSettings(BaseSettings):
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
        extra="allow",
        case_sensitive=False,
        env_nested_delimiter="__",
    )

    @field_validator("INSTALLED_APPS")
    def validate_unchained_settings_module(cls, v: List[str]) -> List[str]:
        # Ensure unchained.app is in the list
        if "unchained.app" not in v:
            v.append("unchained.app")
        return v

    @field_validator("MIDDLEWARE")
    def validate_middleware(cls, v: List[str]) -> List[str]:
        # Merge with default middleware, ensuring no duplicates
        default_middleware = DEFAULT["MIDDLEWARE"]
        merged = list(v)  # Create a copy of the input list
        for middleware in default_middleware:
            if middleware not in merged:
                merged.append(middleware)
        return merged

    @field_validator("INSTALLED_APPS")
    def validate_installed_apps(cls, v: List[str]) -> List[str]:
        # Merge with default apps, ensuring no duplicates
        default_apps = DEFAULT["INSTALLED_APPS"]
        merged = list(v)  # Create a copy of the input list
        for app in default_apps:
            if app not in merged:
                merged.append(app)
        return merged

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

    def add_settings(self, settings: Self):
        for key, value in settings.model_dump().items():
            setattr(self, key, value)

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        return {key.upper(): value for key, value in super().model_dump(*args, **kwargs).items()}
