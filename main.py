from typing import Annotated

from fast_depends import Depends

from models import User
from unchained import Unchained

# Create API instance and set up Django
app = Unchained()


def other_dependency() -> str:
    return "other dependency"


def dependency(other_dependency: Annotated[str, Depends(other_dependency)]) -> str:
    return other_dependency


# Define your endpoints


@app.get("/hello")
def hello(request, a: Annotated[str, Depends(dependency)]):
    return {"message": f"Hello {a}!"}


@app.get("/add/{a}/{b}")
def add(request, a: int, b: int, c: Annotated[str, Depends(dependency)]):
    return {"result": a + b, "c": c}


app.crud(User)
