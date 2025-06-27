---
title: Path Parameters
---

# Path Parameters

Path parameters defined in your route's path string (e.g., `/items/{item_id}`) are automatically available for injection into your route handler or its dependencies.

-   **Matching**: Injection occurs by matching the parameter name in the function signature with the name defined in the route path.
-   **Type Conversion**: The value extracted from the path (which is always initially a string) is automatically parsed and converted based on the parameter's type hint (e.g., `int`, `float`).
-   **Validation**: If the path parameter cannot be converted to the specified type (e.g., providing "abc" for an `int` parameter), Unchained automatically returns an HTTP 422 Unprocessable Entity response detailing the validation error.

```python
from unchained import Unchained
from typing import Annotated
from unchained import Depends
from unchained.errors import HTTPError

app = Unchained()

items_db = {1: "Item One", 2: "Item Two"}

# --- Injection into Route Handler ---

@app.get("/items/{item_id}")
def get_item(item_id: int): # Matches {item_id} in path
    # item_id is automatically converted to an integer.
    # If the path was /items/abc, a 422 error would be returned.
    if item_id not in items_db:
        raise HTTPError(404, f"Item with ID {item_id} not found.")
    return {"item_id": item_id, "name": items_db[item_id]}

# --- Injection into Dependency ---

def get_item_from_db(item_id: int):
    print(f"Dependency fetching item: {item_id}")
    # item_id is injected here too
    if item_id not in items_db:
        raise HTTPError(404, f"Dependency: Item {item_id} not found.")
    return items_db[item_id]

@app.get("/items-dep/{item_id}")
def get_item_via_dep(item_name: Annotated[str, Depends(get_item_from_db)]):
    return {"name_from_dep": item_name}
``` 