# Header Dependency

The `Header` dependency allows you to extract values from request headers. It automatically try to extract the header using the parameter name as the header name. It automatically converts header names to lowercase and converts underscores to dashes like so:

```python
# Header name: X-Api-Key
# Converted to: x_api_key
```

You can also specify a custom header name using the first `name` argument as follows:

```python
header: Annotated[str, Header("X-Custom-Header")]
```

If the header name is not found, the dependency will raise a `ValidationError` exception, but you can make it optional by specifying it's type as `Optional` like so:

```python
header: Annotated[str | None, Header("X-Custom-Header")] = None
```







```python
from typing import Annotated
from unchained import Unchained, Request
from unchained.dependencies import Header

app = Unchained()

@app.get("/items/")
async def read_items(
    user_agent: Annotated[str, Header()],
    header: Annotated[str, Header("X-Custom-Header")],
):
    ...

# Example using Header within a custom dependency function:
async def verify_api_key(api_key: Annotated[str | None, Header("X-API-Key")] = None) -> str:
    """
    A dependency function to verify an API key provided in the X-API-Key header.
    """
    if not api_key:
        raise BadRequest("X-API-Key header is missing")
    if api_key != "SECRET_KEY":
        raise BadRequest("Invalid API Key")
    return api_key

@app.get("/secure-data")
async def get_secure_data(
    request: Request,
    verified_key: Annotated[str, Depends(verify_api_key)] # Use the dependency
):
    """
    Endpoint protected by API key verification.
    """
    return {"data": "sensitive information", "api_key_used": verified_key}

```
