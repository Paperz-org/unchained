# Quickstart Guide

This guide will help you create a fully functional application with Unchained in minutes.

## Installation

```bash
pip install unchained
```

## Complete Example

Below is a single-file application that demonstrates the key features of Unchained:

```python
# app.py
from unchained import Unchained, Depends
from django.db import models
from unchained.models.base import BaseModel
from typing import List, Optional

# Create your application
app = Unchained()

# Define models
class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Task(BaseModel):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="tasks", null=True)
    
    def __str__(self):
        return self.title

# Generate CRUD endpoints for both models
app.crud(Category)
app.crud(Task)

# Define a dependency
def get_task_by_id(task_id: int):
    try:
        return Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return {"error": "Task not found"}

# Basic route
@app.get("/")
def home():
    return {"message": "Welcome to the Task Manager API"}

# Path parameter example
@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello {name}!"}

# Query parameter example
@app.get("/tasks/filter")
def filter_tasks(completed: Optional[bool] = None, category: Optional[str] = None):
    query = Task.objects.all()
    
    if completed is not None:
        query = query.filter(completed=completed)
    
    if category:
        query = query.filter(category__name=category)
    
    return list(query.values())

# Dependency injection example
@app.get("/tasks/{task_id}/details")
def task_details(task = Depends(get_task_by_id)):
    return task

# POST request with body
@app.post("/tasks/create")
def create_task(task_data: dict):
    category = None
    if task_data.get("category_id"):
        try:
            category = Category.objects.get(id=task_data["category_id"])
        except Category.DoesNotExist:
            pass
    
    task = Task(
        title=task_data["title"],
        description=task_data.get("description", ""),
        completed=task_data.get("completed", False),
        due_date=task_data.get("due_date"),
        category=category
    )
    task.save()
    return task

# Application state (middleware)
@app.before_request
def log_request():
    print("Request received")

@app.after_request
def log_response():
    print("Response sent")
```

## Running Your Application

1. Save the code above as `app.py`
2. Run database migrations:
   ```bash
   unchained migrations create
   unchained migrations apply
   ```
3. Start the server:
   ```bash
   unchained start app:app
   ```
4. Open your browser to `http://127.0.0.1:8000/docs` to see the interactive API documentation

## Key Features Demonstrated

- **Models** - Django models with relationships
- **CRUD Operations** - Automatic API endpoints
- **Routing** - Path and query parameters
- **Dependency Injection** - Clean separation of concerns
- **Request Handling** - Working with request body
- **Middleware** - Request/response hooks
- **API Documentation** - Automatic OpenAPI docs

## Next Steps

- Learn about authentication and security features
- Explore advanced models in the documentation
- Set up custom admin pages 