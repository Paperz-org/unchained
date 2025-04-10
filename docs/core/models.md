# Models & Migrations

!!! info "Django Models"
    Unchained provides seamless integration with Django's ORM for model definition and database management.

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

## Common Model Patterns

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

## Database Migrations

Unchained uses Django's migration system to manage database schema changes. After defining or modifying your models, you'll need to create and apply migrations.

### Creating Migrations

To create new migrations based on model changes:

```bash
unchained migrations create [name]
```

Where `[name]` is an optional name for the migration (e.g., "add_user_model").

### Applying Migrations

To apply migrations and update your database schema:

```bash
unchained migrations apply
```

### Viewing Migration Status

To see which migrations have been applied:

```bash
unchained migrations show
```

For detailed information about migration commands and options, see the [CLI documentation](../cli/commands.md#database-migration-commands).

## Best Practices

1. **Use abstract models** for common fields and behavior
2. **Add Meta options** for ordering, indexes, and constraints
3. **Create migrations early** to catch model issues
4. **Keep migrations small** to make deployments safer
5. **Test migrations** on a copy of production data when possible

For information about generating CRUD endpoints from your models, see the [CRUD documentation](./crud.md). 