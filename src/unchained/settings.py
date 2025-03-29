import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT = {
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
    "STATIC_ROOT": os.path.join(_BASE_DIR, "unchained/static"),
    "JAZZMIN_SETTINGS": {
        "site_title": "Unchained",
        "site_header": "Unchained",
        "site_brand": "Unchained App",
        "show_ui_builder": True,
        "dark_mode_theme": "darkly"
    }
}
