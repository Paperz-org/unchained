# Unchained Framework

A modern, type-safe Python web framework built on top of Django with dependency injection.

## Installation

```bash
pip install unchained
```

## Quickstart

```python
# app.py
from unchained import Unchained
from django.db import models
from unchained.models.base import BaseModel

# Define your application
app = Unchained()

# Define a model
class Task(BaseModel):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

# Generate CRUD endpoints for Task model
app.crud(Task)

# Custom endpoint
@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello {name}!"}

# Dependency injection example
@app.get("/tasks/completed")
def completed_tasks():
    return Task.objects.filter(completed=True).all()

# Run your application with:
# uvicorn app:app
```

To get started:

1. Install Unchained: `pip install unchained`
2. Create app.py with the code above
3. Set up the database: `unchained migrate`
4. Run the server: `uvicorn app:app`
5. Visit http://127.0.0.1:8000/docs to view your API documentation

**[See our detailed quickstart guide for a full example →](quickstart.md)**

## Key Features

- **Django Integration** - Leverage Django's powerful ORM and admin
- **FastAPI-like Routing** - Modern, intuitive API endpoints
- **CRUD Generator** - Automatic endpoints for your models
- **Type Safety** - Full static type checking
- **Dependency Injection** - Clean, modular code architecture
- **Admin Interface** - Customizable admin dashboard

## Documentation

- [Routing](core/routing.md)
- [Models & CRUD](core/models.md)
- [Dependency Injection](core/dependency-injection.md)
- [State Management](core/state.md)
- [Admin Interface](core/admin.md)

## Examples

Check out the quickstart guide for complete examples of:

- Basic API setup
- CRUD applications
- Dependency injection implementation

## Need Help?

[GitHub Issues](https://github.com/yourusername/unchained/issues)
