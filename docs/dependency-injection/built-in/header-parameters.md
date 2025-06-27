---
title: Header Parameters
---

# Header Parameters (`Header`)

Extract request headers using `unchained.dependencies.Header` with `typing.Annotated`.

-   **Header Name**: The header name is typically inferred from the parameter name by converting underscores to hyphens (e.g., `user_agent` -> `user-agent`). You can explicitly specify the header name using `Header("X-Custom-Header")`.
-   **Case-Insensitivity**: Header name lookup is case-insensitive.
-   **Required vs. Optional**: Similar to `QueryParams`, use function signature defaults or `Header(default=...)` for optional headers. Missing required headers result in an HTTP 422 response.
-   **Type Conversion**: Basic type conversion can be applied via type hints if needed, although headers are typically strings.

```python
from typing import Annotated, Optional
from unchained import Unchained
from unchained.dependencies import Header

app = Unchained()

@app.get("/header-info")
def header_info(
    # Infer header name 'user-agent' from parameter name
    user_agent: Annotated[Optional[str], Header()] = None,
    # Explicitly specify header name 'X-API-Key' (required)
    api_key: Annotated[str, Header("X-API-Key")],
    # Optional, explicit name, with default
    x_request_id: Annotated[Optional[str], Header("X-Request-ID", default="N/A")]
):
    return {
        "ua": user_agent,
        "key": api_key,
        "req_id": x_request_id,
    }

# Example Request (with headers):
# GET /header-info
# User-Agent: MyClient/1.0
# X-API-Key: secret123
# -> 200 OK {"ua": "MyClient/1.0", "key": "secret123", "req_id": "N/A"}

# Example Request (missing required header):
# GET /header-info
# User-Agent: MyClient/1.0
# -> 422 Validation Error (detail: missing required header 'X-API-Key')

# Example Request (providing optional header):
# GET /header-info
# User-Agent: MyClient/1.0
# X-API-Key: secret123
# x-request-id: abc-789 # Case-insensitive match
# -> 200 OK {"ua": "MyClient/1.0", "key": "secret123", "req_id": "abc-789"}
```

!!! info "Header Name Conversion"
    Remember the automatic conversion: `parameter_name` becomes `parameter-name` when looking for the header. 