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

=== "Path Parameters"
    ```python
    @app.get("/hello/{name}")
    def hello(name: str):
        return {"message": f"Hello, {name}!"}
    ```

=== "Query Parameters"
    ```python
    from typing import Annotated
    from unchained.dependencies.query import Query

    @app.get("/search")
    def search(q: Annotated[str, Query()]):
        return {"query": q}
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

## Query Parameters

=== "Required Parameters"
    ```python
    from typing import Annotated
    from unchained.dependencies.query import Query

    @app.get("/search")
    def search(q: Annotated[str, Query()]):
        return {"query": q}
    ```

=== "Optional Parameters"
    ```python
    @app.get("/items")
    def get_items(
        page: Annotated[int, Query(ge=1)] = 1,
        limit: Annotated[int, Query(le=100)] = 10
    ):
        return {"page": page, "limit": limit}
    ```

## Best Practices

1. **Type Safety**: Always use type hints for parameters
2. **Validation**: Use Pydantic models for request/response validation
3. **Modularity**: Split routes into logical routers
4. **Documentation**: Add docstrings to describe endpoint behavior

## Common Patterns

### Pagination

```python
from typing import Annotated
from pydantic import BaseModel
from unchained.dependencies.query import Query

class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 10

    @validator("page")
    def validate_page(cls, v):
        if v < 1:
            raise ValueError("Page must be positive")
        return v

    @validator("limit")
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError("Limit must be between 1 and 100")
        return v

@app.get("/items")
def get_items(pagination: Annotated[PaginationParams, Query()]):
    return {
        "items": [],
        "page": pagination.page,
        "limit": pagination.limit
    }
```

### Filtering

```python
from typing import Annotated
from pydantic import BaseModel
from unchained.dependencies.query import Query

class ItemFilter(BaseModel):
    category: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    in_stock: bool | None = None

@app.get("/items")
def get_items(filter: Annotated[ItemFilter, Query()]):
    return {
        "items": [],
        "filter": filter.dict(exclude_none=True)
    }
```

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