from typing import Annotated, Optional

from unchained import Unchained
from unchained.dependencies import QueryParams

app = Unchained()

@app.get("/search/")
def search(
    q: Annotated[str, QueryParams()],
    tags: Annotated[list[str], QueryParams()],
    page_size: Annotated[int, QueryParams(default=10)],
    page: Annotated[int, QueryParams()] = 1,
    include_details: Annotated[Optional[bool], QueryParams()] = None,
):
    return {
        "query": q,
        "page": page,
        "size": page_size,
        "details": include_details,
        "tags": tags or [],
    }