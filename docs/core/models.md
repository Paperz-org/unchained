# Models & CRUD Operations

!!! info "Django Models with CRUD"
    Unchained provides seamless integration with Django's ORM and automatic CRUD endpoint generation.

## Basic Models

=== "Define a Model"
    ```python
    from django.db import models
    from unchained.models.base import BaseModel

    class User(BaseModel):
        name = models.CharField(max_length=255)
        email = models.EmailField(unique=True)
        is_active = models.BooleanField(default=True)
    ```

=== "Model Relationships"
    ```python
    class Post(BaseModel):
        title = models.CharField(max_length=255)
        content = models.TextField()
        author = models.ForeignKey(User, on_delete=models.CASCADE)
        tags = models.ManyToManyField(Tag)
    ```

## CRUD Operations

=== "Basic CRUD"
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

## Custom Schemas

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

1. **Type Safety**: Always use type hints in schemas
2. **Validation**: Use Pydantic models for input validation
3. **Security**: Be careful with sensitive fields
4. **Performance**: Use select_related/prefetch_related for relationships

## Common Patterns

### Soft Delete

```python
class SoftDeleteModel(BaseModel):
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

class User(SoftDeleteModel):
    name = models.CharField(max_length=255)
```

### Timestamps

```python
class TimestampModel(BaseModel):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Post(TimestampModel):
    title = models.CharField(max_length=255)
```

### Custom Manager

```python
class ActiveUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class User(BaseModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active = ActiveUserManager()
```

## Example: Complete Model Setup

```python
from django.db import models
from pydantic import BaseModel
from unchained.models.base import BaseModel as UnchainedModel

# Schemas
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserRead(BaseModel):
    id: int
    name: str
    email: str
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