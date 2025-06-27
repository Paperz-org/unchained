from typing import Annotated, List, Optional

from unchained import Unchained
from unchained.dependencies import QueryParams
from unchained.dependencies.depends import Depends

app = Unchained()


def test(q: Annotated[str, QueryParams()]):
    return {
        "query": q,
        # "tags": tags,
    }


@app.get("/search/")
def search(
    # test: Annotated[dict, Depends(test)],
    page_size: Annotated[int, QueryParams(default=10)],
    tags: Annotated[list[str], QueryParams()],
):
    return {
        "test": test,
        "tags": tags,
    }
