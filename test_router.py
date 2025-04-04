from typing import Annotated

from fast_depends import Depends

from unchained import Request
from unchained.routers import Router

router = Router()


def other_dependency() -> str:
    print("other_dependency")
    return "world"


@router.get("/hello/{a}/{b}")
def hello(request: Request, a: str, b: str, other_dependency: Annotated[str, Depends(other_dependency)]):
    print("Hello from router")
    print(other_dependency)
    print(request)
    return {"message": f"Hello {a} {b} !"}
