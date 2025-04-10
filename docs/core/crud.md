# CRUD Operations

!!! info "Automatic CRUD Generation"
    Unchained provides automatic CRUD endpoint generation for your Django models with minimal setup.

## Basic CRUD

=== "Simple Setup"
    ```python
    app.crud(User)  # Generates all CRUD endpoints
    ```

=== "Customized CRUD"
    ```python
    app.crud(
        User,
        operations="CRUD",  # Create, Read, Update, Delete
        path="/users",      # Custom path
        tags=["Users"]      # API tags
    )
    ```

=== "Partial CRUD"
    ```python
    app.crud(
        User,
        operations="CR",    # Only Create and Read
        path="/users"
    )
    ```

## Operations Parameter

The `operations` parameter allows you to control which CRUD operations are generated for your model. Each letter in the string represents a specific operation:

- **C**: Create - POST endpoint to create new records
- **R**: Read - GET endpoints to retrieve individual records and lists of records
- **U**: Update - PUT/PATCH endpoints to modify existing records
- **D**: Delete - DELETE endpoint to remove records

### Examples

```python
# Full CRUD (default if not specified)
app.crud(User, operations="CRUD")

# Read-only API
app.crud(User, operations="R")

# Create and Read only (no updates or deletes)
app.crud(User, operations="CR")

# Create, Read, and Update (no delete capability)
app.crud(User, operations="CRU")
```

### Generated Endpoints

For a model with `operations="CRUD"` and `path="/users"`, the following endpoints would be generated:

| Method | Endpoint | Operation | Description |
|--------|----------|-----------|-------------|
| POST | /users/ | Create | Create a new user |
| GET | /users/ | Read | List all users (with pagination) |
| GET | /users/{id} | Read | Get a specific user by ID |
| PUT | /users/{id} | Update | Update a specific user (full update) |
| PATCH | /users/{id} | Update | Update a specific user (partial update) |
| DELETE | /users/{id} | Delete | Delete a specific user |

You can combine any subset of "CRUD" to generate only the endpoints you need for your application.

## Custom Schemas

Customize the input and output data models for your CRUD operations using Pydantic schemas.

=== "Input Schema"
    ```python
    from pydantic import BaseModel

    class UserCreate(BaseModel):
        name: str
        email: str
        password: str

    app.crud(
        User,
        create_schema=UserCreate
    )
    ```

=== "Output Schema"
    ```python
    class UserRead(BaseModel):
        id: int
        name: str
        email: str
        is_active: bool

    app.crud(
        User,
        read_schema=UserRead
    )
    ```

## Filtering and Pagination

Control which records are returned and how they're organized.

=== "Filter Schema"
    ```python
    class UserFilter(BaseModel):
        name: str | None = None
        email: str | None = None
        is_active: bool | None = None

    app.crud(
        User,
        filter_schema=UserFilter
    )
    ```

=== "Custom QuerySet"
    ```python
    app.crud(
        User,
        queryset=User.objects.filter(is_active=True)
    )
    ```

## Best Practices

1. **Type Safety**: Always use type hints in schemas for better documentation and validation
2. **Validation**: Use Pydantic models for input validation with appropriate field constraints
5. **Consistency**: Follow a consistent naming scheme for your schemas and endpoints

## Advanced Configuration

### Response Models

Control what fields are returned in responses:

```python
app.crud(
    User,
    read_schema=UserRead,
    list_schema=UserList  # Different schema for list endpoint
)
```

### Authentication and Permissions

Add authentication and permission requirements:

```python
from unchained.auth import jwt_required

app.crud(
    User,
    auth=[jwt_required],
    permissions=["admin"]
)
```

### Custom Endpoints

Add additional custom endpoints alongside standard CRUD:

```python
user_crud = app.crud(User)

@user_crud.router.get("/me")
def get_current_user():
    # Custom endpoint logic
    pass
```

## Complete Example

```python
from django.db import models
from pydantic import BaseModel, EmailStr, Field
from unchained.models.base import BaseModel as UnchainedModel

# Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool

class UserFilter(BaseModel):
    name: str | None = None
    email: str | None = None
    is_active: bool | None = None

# Model
class User(UnchainedModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-id"]

# CRUD Setup
app.crud(
    User,
    create_schema=UserCreate,
    read_schema=UserRead,
    filter_schema=UserFilter,
    operations="CRUD",
    path="/users",
    tags=["Users"]
)
```

For information about model definition and database migrations, see the [Models documentation](./models.md). 