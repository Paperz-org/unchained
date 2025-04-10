# Unchained Framework Documentation

Unchained is a powerful Python web framework built on top of Django, Django Ninja, and FastDepends. It provides a modern, type-safe, and dependency-injection based approach to building web applications.

## Features

- **Django Integration**: Seamlessly integrates with Django's ORM and admin interface
- **FastAPI-like Routing**: Modern routing system with dependency injection
- **CRUD Operations**: Built-in support for CRUD operations on models
- **Type Safety**: Full type hints support throughout the framework
- **Dependency Injection**: Powerful dependency injection system using FastDepends
- **Admin Interface**: Customizable admin interface for models
- **Lifespan Management**: Support for application startup and shutdown events
- **State Management**: Application-wide state management

## Quick Start

1. Install the framework:
```bash
pip install unchained
```

2. Create a new application:
```python
from unchained import Unchained
from unchained.states import BaseState

class State(BaseState):
    app_name: str

app = Unchained(state=State())
```

3. Define your models:
```python
from django.db import models
from unchained.models.base import BaseModel

class User(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
```

4. Set up the admin interface:
```python
from django.contrib import admin

class UserAdmin(admin.ModelAdmin):
    model = User

app.admin.register(User, UserAdmin)
```

5. Define routes:
```python
@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello {name}!"}
```

6. Add CRUD operations:
```python
app.crud(User, operations="CRUD")
```

## Core Concepts

### Application State

The framework provides a state management system through the `BaseState` class:

```python
class State(BaseState):
    app_name: str
    api_key: str

app = Unchained(state=State())
```

### Dependency Injection

Unchained uses FastDepends for dependency injection:

```python
from typing import Annotated
from unchained import Depends, Request

def get_user(request: Request):
    return request.user

@app.get("/profile")
def profile(user: Annotated[User, Depends(get_user)]):
    return {"user": user}
```

### Lifespan Management

Handle application startup and shutdown:

```python
@app.lifespan
async def startup(app: Unchained):
    app.state.api_key = "secret"
    yield
    print("Shutting down...")
```

### Custom Settings

Extend the default settings:

```python
from unchained.settings import UnchainedSettings

class Settings(UnchainedSettings):
    API_KEY: str = "default"
    DEBUG: bool = True
```

### Router Configuration

Create modular routers:

```python
from unchained.routers import Router

router = Router()

@router.get("/items")
def get_items():
    return {"items": []}

app.add_router("/api", router)
```

## Advanced Features

### Custom Dependencies

Create reusable dependencies:

```python
from unchained.dependencies.header import Header

def get_api_key(x_api_key: Annotated[str, Header()]) -> str:
    return x_api_key
```

### Model CRUD Operations

Automatically generate CRUD endpoints:

```python
app.crud(
    User,
    create_schema=UserCreate,
    read_schema=UserRead,
    update_schema=UserUpdate,
    operations="CRUD"
)
```

### Admin Customization

Customize the admin interface:

```python
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']
    search_fields = ['name', 'email']
```

## Best Practices

1. **Type Safety**: Always use type hints for better IDE support and runtime safety
2. **Dependency Injection**: Use the dependency injection system for better testability
3. **Modular Design**: Split your application into routers for better organization
4. **State Management**: Use the state system for application-wide variables
5. **Error Handling**: Implement proper error handling in your routes

## Examples

See the `test_app` directory for complete examples of:
- Basic routing
- Dependency injection
- CRUD operations
- Admin interface
- State management
- Custom settings

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 