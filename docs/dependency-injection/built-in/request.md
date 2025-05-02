# Request Object

Unchained automatically injects the `Request` object if you type-hint it in your route handler or dependency function signature. This object provides access to the raw request details.

```python
from unchained import Unchained, Request

app = Unchained()

@app.get("/request-details")
async def get_request_details(request: Request):
    """
    Demonstrates accessing details from the auto-injected Request object.
    """
    ...
```

It's also working within dependencies and nested dependencies.

```python
from unchained import Depends, Unchained, Request

app = Unchained()

async def get_request_method(request: Request) -> str:
    return request.method

@app.get("/request-details")
async def get_request_details(request_method: Annotated[str, Depends(get_request_method)]):
    ...
```


## Usage

Simply add `request: Request` as a parameter to your function signature. Unchained's dependency injection system recognizes this type hint and provides the current request instance.
