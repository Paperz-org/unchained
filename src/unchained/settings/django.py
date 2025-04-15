import os
from pathlib import Path
from enum import StrEnum
from typing import Any, Dict

_BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FIXED_STATIC_ROOT = os.path.join(_BASE_DIR, "static")


class MergeStrategy(StrEnum):
    MERGE = "merge"
    OVERRIDE = "override"


class MandatoryDjangoSettings:
    INSTALLED_APPS = [
        "unchained.app",
    ]

    MIGRATION_MODULES = {
        # ????? It makes no sense as app should be unchained.app and if not migration
        # is supposed to be kind of local... But it works........
        "app": "migrations",
    }
    STATIC_URL = "/static/"

    STATIC_ROOT = FIXED_STATIC_ROOT

    merge_strategy = MergeStrategy.MERGE

    @classmethod
    def as_django_settings(cls) -> Dict[str, Any]:
        settings = {}
        for key, value in cls.__dict__.items():
            if not key.isupper() or key.startswith("_"):
                continue
            settings[key] = value

        return settings
    

    def app_migration_module(self) -> str:
        return self.MIGRATION_MODULES["app"]

    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        """
        Get the final settings dictionary based on the merge strategy.
        - If MERGE: Combine settings from base class and subclass.
        - If OVERRIDE: Use only subclass settings but ensure mandatory fields.
        """
        if cls is MandatoryDjangoSettings:
            return cls.to_dict()

        if cls.merge_strategy == MergeStrategy.MERGE:
            final_settings = cls._handle_merge_strategy()
        else:
            final_settings = cls._handle_override_strategy()

        # Ensure mandatory settings
        if "unchained.app" not in final_settings.get("INSTALLED_APPS", []):
            if "INSTALLED_APPS" not in final_settings:
                final_settings["INSTALLED_APPS"] = []
            final_settings["INSTALLED_APPS"].append("unchained.app")

        if "app" not in final_settings.get("MIGRATION_MODULES", {}):
            if "MIGRATION_MODULES" not in final_settings:
                final_settings["MIGRATION_MODULES"] = {}
            final_settings["MIGRATION_MODULES"]["app"] = "migrations"

        if "STATIC_URL" not in final_settings:
            final_settings["STATIC_URL"] = "/static/"

        if "STATIC_ROOT" not in final_settings:
            final_settings["STATIC_ROOT"] = FIXED_STATIC_ROOT

        return final_settings

    @classmethod
    def _handle_merge_strategy(cls) -> Dict[str, Any]:
        base_settings = BaseDjangoSettings.as_django_settings()
        # Merge settings, with subclass taking precedence

        final_settings = base_settings.copy()

        for key, value in cls.as_django_settings().items():
            if key in final_settings and isinstance(value, list) and isinstance(final_settings[key], list):
                # Special handling for lists (like INSTALLED_APPS) to avoid duplicates
                combined = final_settings[key].copy()
                for item in value:
                    if item not in combined:
                        combined.append(item)
                final_settings[key] = combined
            elif key in final_settings and isinstance(value, dict) and isinstance(final_settings[key], dict):
                # Merge dictionaries
                merged_dict = final_settings[key].copy()
                merged_dict.update(value)
                final_settings[key] = merged_dict
            else:
                # Override or add new setting
                final_settings[key] = value

        return final_settings

    @classmethod
    def _handle_override_strategy(cls) -> Dict[str, Any]:
        return cls.as_django_settings()


class DefaultDjangoSettings(MandatoryDjangoSettings):
    merge_strategy = MergeStrategy.MERGE

    DEBUG = True
    SECRET_KEY = "your-secret-key-here"
    ALLOWED_HOSTS = ["*"]
    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",  # Required for admin
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",  # Required for admin
        "django.contrib.messages.middleware.MessageMiddleware",  # Required for admin
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]
    INSTALLED_APPS = [
        "jazzmin",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.staticfiles",
    ]

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    }
    TEMPLATES = [
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
    ]
    JAZZMIN_SETTINGS = {
        "site_title": "Unchained",
        "site_header": "Unchained",
        "site_brand": "Unchained App",
        "show_ui_builder": True,
        "dark_mode_theme": "darkly",
    }


class BaseDjangoSettings(MandatoryDjangoSettings):
    merge_strategy = MergeStrategy.OVERRIDE
    ...
