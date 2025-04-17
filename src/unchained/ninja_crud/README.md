# Ninja CRUD

A utility library for Django Ninja that simplifies creating CRUD (Create, Read, Update, Delete) API endpoints from Django models.

## Features

- Automatic generation of CRUD endpoints for Django models
- Support for both synchronous and asynchronous viewsets
- Automatic schema generation based on model fields
- Customizable endpoints and operations
- Support for filtering and pagination
- Proper handling of foreign keys and many-to-many relationships

## Installation

```bash
pip install ninja-crud
```

## Quick Start

```python
from django.contrib.auth.models import User
from unchained.ninja import NinjaAPI
from unchained.ninja_crud import CRUDRouter

api = NinjaAPI()

# Create a CRUD router for the User model
users_router = CRUDRouter(User, path="users")

# Register the router with the API
api.add_router("", users_router.router)
```

This will create the following endpoints:

- `POST /users/` - Create a new user
- `GET /users/` - List all users
- `GET /users/{id}/` - Get a user by ID
- `PUT /users/{id}/` - Update a user
- `DELETE /users/{id}/` - Delete a user

## Customization

### Custom Schemas

You can define custom schemas for different operations:

```python
from pydantic import BaseModel
from unchained.ninja import Schema

class UserCreate(Schema):
    username: str
    email: str
    password: str

class UserRead(Schema):
    id: int
    username: str
    email: str

class UserUpdate(Schema):
    email: str = None
    first_name: str = None
    last_name: str = None

users_router = CRUDRouter(
    User,
    create_schema=UserCreate,
    read_schema=UserRead,
    update_schema=UserUpdate,
    path="users"
)
```

### Custom Operations

You can specify which CRUD operations to enable:

```python
# Only enable Read and Update operations
users_router = CRUDRouter(User, operations="RU", path="users")
```

### Custom QuerySet

You can provide a custom queryset to filter the objects:

```python
# Only active users
queryset = User.objects.filter(is_active=True)
users_router = CRUDRouter(User, queryset=queryset, path="users")
```

## Advanced Usage

### Filtering

You can define a custom filter schema:

```python
from unchained.ninja import FilterSchema

class UserFilter(FilterSchema):
    username: str = None
    is_active: bool = None

users_router = CRUDRouter(
    User,
    filter_schema=UserFilter,
    path="users"
)
```

### Handling Complex Relationships

The library automatically detects models with complex relationships (many-to-many) and uses the appropriate viewset:

- `SyncViewSet` - Used for models with complex relationships
- `AsyncViewSet` - Used for models with simple relationships for better performance

## License

MIT 