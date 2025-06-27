---
title: Query Parameters
---

To extract parameters from the URL query string (e.g., `/search?q=term&limit=20`), you can use the `unchained.dependencies.QueryParams` built-in dependency.

-   **Required vs. Optional**: Required query parameters are declared simply with `Annotated[<type>, QueryParams()]`. Optional parameters can be defined either by providing a default value in the function signature (`param: Annotated[T, QueryParams()] = default`) or by using `QueryParams(default=...)`.
-   **Type Conversion**: Like path parameters, query parameters are converted based on the type hint (`int`, `bool`, `float`, etc.). `bool` conversion handles values like `True`, `true`, `1`, `yes` (case-insensitive) as true, and `False`, `false`, `0`, `no` as false.
-   **Validation**: Missing required parameters or type conversion failures result in an HTTP 422 response.
-   **Multi-Value Parameters**: To receive multiple query parameters with the same name (e.g., `/items?tag=a&tag=b`), use `typing.List[<type>]` or `list[<type>]` as the type hint.

```python
from typing import Annotated, List, Optional
from unchained import Unchained
from unchained.dependencies import QueryParams

app = Unchained()

@app.get("/search/")
def search(
    q: Annotated[str, QueryParams()],
    page: Annotated[int, QueryParams()] = 1,
    page_size: Annotated[int, QueryParams(default=10)],
    include_details: Annotated[bool | None, QueryParams()] = None,
    tags: Annotated[list[str] | None, QueryParams()] = None
):
    return {
        "query": q,
        "page": page,
        "size": page_size,
        "details": include_details,
        "tags": tags or [],
    }
```