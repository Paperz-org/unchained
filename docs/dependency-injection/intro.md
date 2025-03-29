# Dependency Injection

!!! abstract "Overview"
    Unchained uses the `Depends` function to implement dependency injection, allowing you to create reusable components in your API endpoints.

## Basic Usage

Dependency injection in Unchained is implemented using Python's `Annotated` type and the `Depends` function:

```python
from typing import Annotated
from unchained import Depends, Unchained

app = Unchained()

def dependency() -> str:
    return "world"

@app.get("/hello/{a}")
def hello(request, a: str, b: Annotated[str, Depends(dependency)]):
    return {"message": f"Hello {a} {b} !"}
```

!!! tip "How it works"
    When a request is made to `/hello/test`, the `dependency()` function is called automatically, and its return value (`"world"`) is injected as the value of parameter `b`.

## Nested Dependencies

You can also create dependencies that depend on other dependencies:

```python
from typing import Annotated
from unchained import Depends, Unchained

app = Unchained()

def first_dependency() -> str:
    return "world"

def second_dependency(value: Annotated[str, Depends(first_dependency)]) -> str:
    return f"wonderful {value}"

@app.get("/hello/{name}")
def hello(request, name: str, message: Annotated[str, Depends(second_dependency)]):
    return {"message": f"Hello {name}, {message}!"}
```

## Further Reading

For more information on the technologies used for dependency injection:

- :fontawesome-brands-python: [Python Annotated Type](https://docs.python.org/3/library/typing.html#typing.Annotated) 