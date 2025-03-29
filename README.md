![Unchained](assets/logo.png)

# Unchained - Modern Single-File Django Framework

Unchained is a lightweight framework that lets you build complete Django applications in a **single file**, without the traditional project and app structure. Write modern Python web apps with minimal boilerplate.

## Key Features

### Single-File Application

Build production-ready Django applications in a single file, similar to modern frameworks like Flask or FastAPI:

```python
from unchained import Unchained
from unchained.models.base import BaseModel
from django.db import models

class User(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

app = Unchained()

@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello {name}!"}

app.crud(User)  # Auto-generate CRUD endpoints
```

### Automatic CRUD Operations

Generate complete REST API endpoints for your models with a single line of code:

```python
app.crud(User)  # Creates GET, POST, PUT, DELETE endpoints
```

This creates:
- `GET /api/users` - List all users
- `GET /api/users/{id}` - Get a specific user
- `POST /api/users` - Create a new user
- `PUT /api/users/{id}` - Update a user
- `DELETE /api/users/{id}` - Delete a user

### Powerful Dependency Injection

Use Python type annotations for clean, testable dependencies:

```python
from typing import Annotated
from unchained import Depends

def get_current_user() -> User:
    # Logic to get user
    return user

@app.get("/profile")
def profile(user: Annotated[User, Depends(get_current_user)]):
    return {"user": user}
```

### Built-in CLI Tool

Manage your application with a powerful command-line interface:

```bash
# Start the server
unchained start main:app

# Database migrations
unchained migrations create
unchained migrations apply

# Create admin user
unchained createsuperuser
```

## Why Unchained?

### The Django Project/App Pain

Traditional Django development requires a rigid structure:

```
myproject/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── myapp/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations/
    ├── models.py
    ├── tests.py
    └── views.py
```

This approach comes with significant overhead:
- Running multiple commands to set up a project (`django-admin startproject`, `python manage.py startapp`)
- Manually connecting apps, updating settings files, and configuring URLs
- Working across many files for even simple features
- Constant switching between files for models, views, and URLs

### The Unchained Solution

**All of Django's power, none of the structure overhead.**

```python
# One file. That's it.
from unchained import Unchained
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

app = Unchained()

@app.get("/posts")
def list_posts():
    return Post.objects.all()

# No manage.py, no settings.py, no urls.py, no apps.py
```

## Installation

```bash
pip install unchained
```

## Admin Interface

Unchained includes Django's powerful admin interface out of the box with a modern UI theme ([Django Jazzmin](https://github.com/farridav/django-jazzmin)). The admin interface is automatically available at `/admin/` and lets you manage your models with a user-friendly UI.

### Registering Models

You can easily register your models with the admin interface:

```python
from unchained import Unchained
from unchained.models.base import BaseModel
from django.db import models
from django.contrib.admin import ModelAdmin

# Define your model
class Product(BaseModel):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

# Create custom admin class (optional)
class ProductAdmin(ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

# Create application
app = Unchained()

# Register model with the admin
app.admin.register(Product, ProductAdmin)
```

With this setup, you can log in to `/admin/` and manage your models through a clean, intuitive interface.

### Default Features

The admin interface provides:
- A modern dark/light theme with customizable UI
- CRUD operations for your models
- Search, filtering, and sorting
- User authentication and permissions
- Easy customization with ModelAdmin classes

## Simplifying CLI Commands

To avoid specifying `main:app` in every CLI command, you can configure Unchained to automatically detect your application:

### Using Environment Variables

Set the `UNCHAINED_APP_PATH` environment variable:

```bash
# Unix/Linux/MacOS
export UNCHAINED_APP_PATH=main:app

# Windows
set UNCHAINED_APP_PATH=main:app
```

After setting this, you can use CLI commands without specifying the app path:

```bash
unchained start
unchained migrations apply
```

### Using pyproject.toml

Add an `[tool.unchained]` section to your `pyproject.toml` file:

```toml
[tool.unchained]
app_path = "main:app"
```

With this configuration, Unchained will automatically detect your app path, allowing you to run commands like:

```bash
unchained start
unchained migrations create
```

## All Features

- **Single-file Django applications** - No project setup or app creation required
- **Fast API development** with Django Ninja and automatic OpenAPI documentation
- **Built-in CLI tool** for managing your application
- **Dependency Injection** using Python type annotations
- **Automatic CRUD operations** for your models
- **Modern Admin interface** with beautiful UI
- **ASGI server** with hot-reload for development

## Complete Quickstart Example

1. Create a file named `main.py`:

```python
from typing import Annotated

from unchained import Depends, Unchained
from unchained.models.base import BaseModel
from django.db import models
from django.contrib.admin import ModelAdmin

# Define your models
class User(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

# Custom admin class
class UserAdmin(ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')

# Create your application
app = Unchained()

# Register model with admin
app.admin.register(User, UserAdmin)

# Define dependencies
def get_greeting() -> str:
    return "Hello"

# Create API endpoints
@app.get("/hello/{name}")
def hello(name: str, greeting: Annotated[str, Depends(get_greeting)]):
    return {"message": f"{greeting} {name}!"}

# Generate CRUD endpoints automatically
app.crud(User)
```

2. Run the development server:

```bash
unchained start main:app
```

3. Access your application:
   - API: http://127.0.0.1:8000/api/
   - API docs: http://127.0.0.1:8000/api/docs
   - Admin interface: http://127.0.0.1:8000/admin/

## CLI Commands

Unchained comes with a powerful CLI tool to help manage your application:

### Starting the Server

```bash
# Basic usage
unchained start main:app

# Custom host and port
unchained start main:app --host 0.0.0.0 --port 5000

# Disable auto-reload
unchained start main:app --no-reload
```

### Database Migrations

```bash
# Create migrations
unchained migrations create main:app [name]

# Apply migrations
unchained migrations apply main:app [app_label] [migration_name]

# Show migration status
unchained migrations show main:app [app_label]
```

### User Management

```bash
# Create a superuser for admin access
unchained createsuperuser main:app [username] [email]
```

### Utilities

```bash
# Check version
unchained version
```

## API Documentation

Once your server is running, you can access the auto-generated API documentation at:
- Swagger UI: http://127.0.0.1:8000/api/docs
- ReDoc: http://127.0.0.1:8000/api/redoc

## Configuration

Unchained can be configured through:

1. Environment variables (e.g., `UNCHAINED_APP_PATH`)
2. A `pyproject.toml` file with `[tool.unchained]` section
3. Command-line arguments

## Learn More

For more information, check out the documentation:

- Django: https://docs.djangoproject.com/
- Django Ninja: https://django-ninja.dev/
- FastDepends: https://lancetnik.github.io/FastDepends/