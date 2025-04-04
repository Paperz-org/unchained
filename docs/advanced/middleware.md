# Middleware

!!! info "Django Middleware"
    Unchained configures Django with standard middleware for handling requests and responses. Learn more about [Django middleware](https://docs.djangoproject.com/en/stable/topics/http/middleware/).

## Default Configuration

Unchained includes the following Django middleware components as defined in `settings.py`:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # Required for admin
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Required for admin
    "django.contrib.messages.middleware.MessageMiddleware",  # Required for admin
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

## Middleware Functions

Each middleware component serves a specific purpose:

| Middleware | Purpose | Documentation |
| ---------- | ------- | ------------- |
| :material-shield-lock: SecurityMiddleware | Handles security-related HTTP headers | [Docs](https://docs.djangoproject.com/en/stable/ref/middleware/#module-django.middleware.security) |
| :material-cookie-settings: SessionMiddleware | Enables session support (required for admin) | [Docs](https://docs.djangoproject.com/en/stable/topics/http/sessions/) |
| :material-application-brackets: CommonMiddleware | Handles common request processing | [Docs](https://docs.djangoproject.com/en/stable/ref/middleware/#module-django.middleware.common) |
| :material-shield-account: CsrfViewMiddleware | Provides CSRF protection | [Docs](https://docs.djangoproject.com/en/stable/ref/csrf/) |
| :material-account-key: AuthenticationMiddleware | Associates users with requests (required for admin) | [Docs](https://docs.djangoproject.com/en/stable/ref/middleware/#django.contrib.auth.middleware.AuthenticationMiddleware) |
| :material-message-text: MessageMiddleware | Enables temporary message storage (required for admin) | [Docs](https://docs.djangoproject.com/en/stable/ref/contrib/messages/) |
| :material-security: XFrameOptionsMiddleware | Clickjacking protection | [Docs](https://docs.djangoproject.com/en/stable/ref/clickjacking/) |

!!! tip "Request Flow"
    Middleware components are processed in order for each request, and in reverse order for each response. See [Django's middleware processing](https://docs.djangoproject.com/en/stable/topics/http/middleware/#middleware-order-and-layering) documentation for details.

## Further Reading

For more detailed information about Django middleware and web request handling:

- :fontawesome-brands-python: [Django Middleware Documentation](https://docs.djangoproject.com/en/stable/topics/http/middleware/)
- :material-api: [Django Ninja Request Handling](https://django-ninja.dev/guides/requests/)
