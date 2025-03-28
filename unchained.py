import importlib
import importlib.machinery
import importlib.util
import os
import sys
import types
from functools import cached_property
from typing import TYPE_CHECKING, List, Type

if TYPE_CHECKING:
    from django.contrib import admin
    from ninja import NinjaAPI


DEFAULT_SETTINGS = {
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
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "_unchained_app",
    ],
    "MIGRATION_MODULES": {
        "_unchained_app": "migrations",
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
}


class Unchained:
    # Initialize all_models as empty, we'll populate it after Django setup
    all_models: List[Type] = []
    _NinjaAPI: Type["NinjaAPI"]
    APP_NAME = "_unchained_app"

    def __init__(self, settings_path: str | None = None):
        self.urlpatterns: list[str] = []
        self.settings_path = settings_path
        self.app_config_class: Type | None = None
        self.models: list[Type] = []

        # Configure settings first
        self.configure_settings()

        # Setup Django - this needs to happen before model detection
        self._setup_django()

        # Now that Django is set up, we can import MainAppModelMeta and detect models
        # self._detect_and_register_models()

        # Then setup the app and other components
        self._setup_imports()
        self._configure_api()

    def _import_module(self, module_path, attribute=None):
        """
        Dynamically import a module and optionally get a specific attribute.

        Args:
            module_path (str): Dotted path to the module
            attribute (str, optional): Specific attribute to import from the module
        """
        module = importlib.import_module(module_path)
        return getattr(module, attribute) if attribute else module

    def _setup_imports(self):
        """
        Configure all necessary imports in the correct order.
        This method is called after Django setup to ensure proper initialization.
        """
        self._path = self._import_module("django.urls", "path")
        self._NinjaAPI = self._import_module("ninja", "NinjaAPI")

    def _configure_api(self):
        """Configure the API and URL patterns"""
        self.api = self._NinjaAPI()

    @cached_property
    def app(self):
        get_asgi_application = self._import_module(
            "django.core.asgi", "get_asgi_application"
        )
        return get_asgi_application()

    def _setup_django(self):
        django = self._import_module("django")
        django.setup()

    def configure_settings(self):
        settings = self._import_module("django.conf", "settings")
        if not self.settings_path:
            settings.configure(**DEFAULT_SETTINGS, ROOT_URLCONF=self)

    def __getattr__(self, item):
        attr = getattr(self.api, item, None)
        if attr:
            return attr

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{item}'"
        )

    def __call__(self, *args, **kwargs):
        self._register_api()
        return self.app

    def register_model(self, model_class):
        """
        Register a model with the main app

        Args:
            model_class (Type[models.Model]): The model class to register
        Returns:
            Type[models.Model]: The registered model class
        """
        # Set app_label for the model if not already set or if it's incorrect
        # if (
        #     not hasattr(model_class._meta, "app_label")
        #     or model_class._meta.app_label != self.APP_NAME
        # ):
        #     model_class._meta.app_label = self.APP_NAME

        # # Make sure the model knows its module
        # model_module = f"{self.APP_NAME}.models"
        # if model_class.__module__ != model_module:
        #     model_class.__module__ = model_module

        # # Add model to the models module
        # models_module = sys.modules[model_module]
        model_name = model_class.__name__
        # if not hasattr(models_module, model_name):
        #     setattr(models_module, model_name, model_class)

        # # Add model to our internal registry
        # if model_class not in self.models:
        #     self.models.append(model_class)

        # Force Django to recognize model changes
        try:
            # Make sure Django's connection is ready
            connection = self._import_module("django.db", "connection")
            if hasattr(connection, "prepare_database"):
                connection.prepare_database()

            # Force Django to re-scan models
            apps = self._import_module("django.apps", "apps")

            # Update the app's model registry
            app_config = apps.get_app_config(self.APP_NAME)
            if model_name not in app_config.models:
                app_config.models[model_name.lower()] = model_class

            # Clear Django's cache to ensure models are re-detected
            apps.clear_cache()

            print(f"Model {model_name} registered with app {self.APP_NAME}")
        except Exception as e:
            print(f"Warning: Error registering model {model_name}: {e}")

        return model_class

    def _detect_and_register_models(self):
        """Detect and register all models with MainAppModelMeta after Django is set up"""
        try:
            # Import MainAppModelMeta to access the model registry
            from models_base import MainAppModelMeta

            # Get all models from the global registry
            models = MainAppModelMeta.models_registry
            print(models)

            if models:
                print(f"Detected {len(models)} models from MODEL_REGISTRY")
                for model in models:
                    # Make sure the model has the correct app_label
                    if (
                        hasattr(model._meta, "app_label")
                        and model._meta.app_label != self.APP_NAME
                    ):
                        model._meta.app_label = self.APP_NAME

                    # Register the model with our app
                    self.register_model(model)
            else:
                print("No models found in MODEL_REGISTRY")
        except ImportError as e:
            print(f"Warning: Could not import model registry: {e}")
        except Exception as e:
            print(f"Error detecting models: {e}")

    def _register_api(self):
        self.urlpatterns.append(self._path("api/", self.api.urls))
