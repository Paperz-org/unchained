---
title: Request Object Dependency
---

Unchained automatically injects the `Request` object if you type-hint it in your route handler or dependency function signature. This object provides access to the raw request details.


```python
from unchained import Unchained, Request
from typing import Annotated
from unchained import Depends

app = Unchained()

@app.get("/request-info")
def get_request_info(request: Request):
    return {
        "method": request.method,
        "path": request.path,
        "client_host": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }
``` 