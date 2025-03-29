# CRUD Operations

!!! success "Rapid Development"
    Unchained provides automatic CRUD (Create, Read, Update, Delete) operations through the `app.crud()` method, enabling you to build REST APIs with minimal code.

## Basic Usage

With just a single line of code, you can generate complete CRUD endpoints for your models:

```python
from unchained import Unchained
from unchained.models.base import BaseModel
from django.db import models

class User(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

app = Unchained()
app.crud(User)  # Generates all CRUD endpoints for User model
```

!!! note "Generated Endpoints"
    The `app.crud(User)` method generates the following endpoints:
    
    - `GET /api/users` - List all users
    - `GET /api/users/{id}` - Get a specific user by ID
    - `POST /api/users` - Create a new user
    - `PUT /api/users/{id}` - Update a user
    - `DELETE /api/users/{id}` - Delete a user

## Example Usage

=== "Model Definition"
    ```python
    from django.db import models
    from unchained.models.base import BaseModel
    
    class Product(BaseModel):
        name = models.CharField(max_length=255)
        price = models.DecimalField(max_digits=10, decimal_places=2)
        description = models.TextField(blank=True)
    ```

=== "API Setup"
    ```python
    from unchained import Unchained
    from .models import Product
    
    app = Unchained()
    app.crud(Product)
    ```

=== "API Usage"
    ```bash
    # List all products
    GET /api/products
    
    # Get a specific product
    GET /api/products/1
    
    # Create a new product
    POST /api/products
    {
      "name": "New Product",
      "price": 99.99,
      "description": "A fantastic new product"
    }
    ```

## Further Reading

For more information on the underlying technologies:

- :material-api: [Django Ninja documentation](https://django-ninja.dev/)
- :material-database: [Django ORM documentation](https://docs.djangoproject.com/en/stable/topics/db/) 