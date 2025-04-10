# Routing

!!! info "URL Routing"
    Unchained provides a powerful routing system that allows you to define API endpoints with type safety and dependency injection.

## Basic Routing

=== "Simple Route"
    ```python
    @app.get("/hello")
    def hello():
        return {"message": "Hello, World!"}
    ```



## HTTP Methods

=== "GET"
    ```python
    @app.get("/items")
    def get_items():
        return {"items": []}
    ```

=== "POST"
    ```python
    @app.post("/items")
    def create_item(item: Item):
        return {"item": item}
    ```

=== "PUT"
    ```python
    @app.put("/items/{item_id}")
    def update_item(item_id: int, item: Item):
        return {"item_id": item_id, "item": item}
    ```

=== "DELETE"
    ```python
    @app.delete("/items/{item_id}")
    def delete_item(item_id: int):
        return {"deleted": item_id}
    ```

## Request Body

Unchained leverages Pydantic for powerful, automatic request body validation. Simply define your data structure as a Pydantic model and use it as a parameter in your route function.

=== "Basic Request Body"
    ```python
    from pydantic import BaseModel

    class Item(BaseModel):
        name: str
        price: float
        description: str = None
        tags: list[str] = []

    @app.post("/items")
    def create_item(item: Item):
        # The item parameter will automatically be populated from the request JSON body
        # Validation happens automatically based on the Pydantic model
        return {"item_id": 123, "item": item}
    ```

=== "Nested Models"
    ```python
    from pydantic import BaseModel

    class Image(BaseModel):
        url: str
        width: int
        height: int

    class Item(BaseModel):
        name: str
        price: float
        images: list[Image] = []

    @app.post("/items")
    def create_item(item: Item):
        # Nested objects are validated recursively
        return {"item": item}
    ```

=== "Field Validation"
    ```python
    from pydantic import BaseModel, Field, EmailStr

    class User(BaseModel):
        username: str = Field(..., min_length=3, max_length=50)
        email: EmailStr
        age: int = Field(..., ge=18, description="Age must be at least 18")
        
    @app.post("/users")
    def create_user(user: User):
        # Validation will ensure:
        # - username is between 3-50 characters
        # - email is a valid email format
        # - age is at least 18
        return {"user_id": 123, "user": user}
    ```

=== "Error Handling"
    When validation fails, Unchained automatically returns a 422 Unprocessable Entity response with details about the validation errors:
    
    ```json
    {
      "detail": [
        {
          "loc": ["body", "username"],
          "msg": "ensure this value has at least 3 characters",
          "type": "value_error.any_str.min_length"
        },
        {
          "loc": ["body", "age"],
          "msg": "ensure this value is greater than or equal to 18",
          "type": "value_error.number.not_ge"
        }
      ]
    }
    ```

## Request and Response

=== "Request Object"
    ```python
    from unchained import Request

    @app.get("/request")
    def get_request(request: Request):
        return {
            "method": request.method,
            "headers": dict(request.headers),
            "query_params": dict(request.query_params)
        }
    ```

=== "Response Object"
    ```python
    from unchained import Response

    @app.get("/custom-response")
    def custom_response():
        return Response(
            content={"message": "Custom response"},
            status_code=201,
            headers={"X-Custom": "value"}
        )
    ```

## Modular Routing

=== "Router Definition"
    ```python
    from unchained.routers import Router

    router = Router()

    @router.get("/items")
    def get_items():
        return {"items": []}
    ```

=== "Router Registration"
    ```python
    app.add_router("/api", router)
    # Routes will be available at /api/items
    ```

## Path Parameters

=== "Basic Types"
    ```python
    @app.get("/items/{item_id}")
    def get_item(item_id: int):
        return {"item_id": item_id}
    ```

=== "Custom Types"
    ```python
    from pydantic import BaseModel

    class ItemID(BaseModel):
        id: int

        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def validate(cls, v):
            if not isinstance(v, int):
                raise ValueError("Item ID must be an integer")
            if v < 1:
                raise ValueError("Item ID must be positive")
            return cls(id=v)

    @app.get("/items/{item_id}")
    def get_item(item_id: ItemID):
        return {"item_id": item_id.id}
    ```

## Headers

```python
from typing import Annotated
from unchained.dependencies.header import Header

@app.get("/items")
def get_items(user_agent: Annotated[str, Header()]):
    return {"user_agent": user_agent}
```

## Query Parameters

Access query parameters directly from the request object:

```python
@app.get("/items")
def get_items(request: Request):
    page = int(request.query_params.get("page", 1))
    limit = int(request.query_params.get("limit", 10))
    
    return {
        "items": [],
        "page": page,
        "limit": limit
    }
```

## Best Practices

1. **Type Safety**: Always use type hints for parameters
2. **Validation**: Use Pydantic models for request/response validation
3. **Modularity**: Split routes into logical routers
4. **Documentation**: Add docstrings to describe endpoint behavior

## Common Patterns

### Versioning

```python
from unchained.routers import Router

v1 = Router()
v2 = Router()

@v1.get("/items")
def get_items_v1():
    return {"version": "v1", "items": []}

@v2.get("/items")
def get_items_v2():
    return {"version": "v2", "items": []}

app.add_router("/api/v1", v1)
app.add_router("/api/v2", v2)
``` 