from typing import Annotated

from models import User
from unchained import Depends, Unchained

app = Unchained()


def other_dependency() -> str:
    return "world"


def dependency(other_dependency: Annotated[str, Depends(other_dependency)]) -> str:
    return other_dependency


@app.get("/hello/{a}")
def hello(request, a: str, b: Annotated[str, Depends(dependency)]):
    return {"message": f"Hello {a} {b} !"}


app.crud(User)
