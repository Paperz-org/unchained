# Unchained Documentation

!!! tip "Modern API Framework"
    Unchained is a lightweight wrapper around [Django](https://www.djangoproject.com/) that simplifies API development using [Django Ninja](https://django-ninja.dev/).

## Core Features

- :material-bolt: **Dependency Injection**: Using Python type annotations
- :material-database: **Automatic CRUD Operations**: Generate API endpoints for your models

## Quick Example

=== "Basic Usage"

    ```python
    from typing import Annotated
    
    from models import User
    from unchained import Depends, Unchained
    
    app = Unchained()
    
    
    def other_dependency() -> str:
        return "world"
    
    
    def dependency(other_dependency: Annotated[str, Depends(other_dependency)]) -> str:
        return other_dependency
    
    
    @app.get("/hello/{a}")
    def hello(request, a: str, b: Annotated[str, Depends(dependency)]):
        return {"message": f"Hello {a} {b} !"}
    
    
    app.crud(User)
    ```

=== "With CRUD Operations"

    ```python
    from django.db import models
    from unchained import Unchained
    from unchained.models.base import BaseModel
    
    class User(BaseModel):
        name = models.CharField(max_length=255)
        email = models.EmailField(unique=True)
    
    app = Unchained()
    app.crud(User)  # Automatically generates CRUD endpoints
    ```

## Documentation Sections

- [:material-power-plug: Dependency Injection](dependency-injection/intro.md)
- [:material-database: CRUD Operations](crud/customizing.md)
- [:material-cog: Advanced Topics](advanced/custom-responses.md)

## Official Documentation

- [:fontawesome-brands-python: Django Documentation](https://docs.djangoproject.com/en/stable/)
- [:material-api: Django Ninja Documentation](https://django-ninja.dev/) 