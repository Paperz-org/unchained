# Unchained Framework

!!! tip "Modern API Framework"
    Unchained is a powerful Python web framework built on top of Django. It provides a modern, type-safe, and dependency-injection based approach to building web applications.

## :material-bolt: Quick Start

=== "Installation"
    ```bash
    pip install unchained
    ```

=== "Basic Application"
    ```python
    from unchained import Unchained

    app = Unchained()

    @app.get("/hello/{name}")
    def hello(name: str):
        return {"message": f"Hello {name}!"}
    ```

=== "With Models"
    ```python
    from django.db import models
    from unchained.models.base import BaseModel

    class User(BaseModel):
        name = models.CharField(max_length=255)
        email = models.EmailField(unique=True)

    app.crud(User)  # Automatically generates CRUD endpoints
    ```

## :material-feature-search-outline: Features

| Feature | Description |
|---------|-------------|
| :material-database: Django Integration | Seamless integration with Django's ORM and admin interface |
| :material-api: FastAPI-like Routing | Modern routing system with dependency injection |
| :material-cog: CRUD Operations | Built-in support for CRUD operations on models |
| :material-code-braces: Type Safety | Full type hints support throughout the framework |
| :material-power-plug: Dependency Injection | Powerful dependency injection system using FastDepends |
| :material-view-dashboard: Admin Interface | Customizable admin interface for models |
| :material-timer: Lifespan Management | Support for application startup and shutdown events |
| :material-state-machine: State Management | Application-wide state management |

## :material-book-open-page-variant: Documentation

### Getting Started

- [:material-api: Routing](core/routing.md)
- [:material-power-plug: Dependency Injection](core/dependency-injection.md)
- [:material-timer: Lifespan Management](core/lifespan.md)
- [:material-state-machine: State Management](core/state.md)
- [:material-database: Models & CRUD](core/models.md)
- [:material-view-dashboard: Admin Interface](core/admin.md)

### Advanced Topics

- [:material-cog: Settings](advanced/settings.md)
- [:material-code-braces: Type Safety](advanced/type-safety.md)
- [:material-shield-check: Security](advanced/security.md)

### Examples

- [:material-code-tags: Basic API](examples/basic-api.md)
- [:material-database: CRUD Example](examples/crud.md)
- [:material-power-plug: Dependency Injection](examples/dependency-injection.md)
- [:material-state-machine: State Management](examples/state.md)

## :material-help-circle: Getting Help

- :material-github: [GitHub Issues](https://github.com/yourusername/unchained/issues)
- :material-discord: [Discord Community](https://discord.gg/your-discord)
- :material-email: [Email Support](mailto:support@example.com)

## :material-book-open-variant: Related Documentation

- [:fontawesome-brands-python: Django Documentation](https://docs.djangoproject.com/en/stable/)
- [:material-api: Django Ninja Documentation](https://django-ninja.dev/)
- [:material-power-plug: FastDepends Documentation](https://fast-depends.readthedocs.io/) 