from typing import Annotated

from pydantic import BaseModel

from admin import ProductAdmin, UserAdmin
from models import Product, User
from unchained import Depends, Request, Unchained


class Headers(BaseModel):
    x_api_key: str | None = None


app = Unchained()

app.admin.register(User, UserAdmin)
app.admin.register(Product, ProductAdmin)


def other_dependency() -> str:
    print("other_dependency")
    return "world"


def dependency(request: Request, other_dependency: Annotated[str, Depends(other_dependency)]) -> str:
    print(request)
    return other_dependency


def dep(
    request: Request,
    dependency: Annotated[str, Depends(dependency)],
    other_dependency: Annotated[str, Depends(other_dependency)],
):
    print(request)
    print(dependency)
    print(other_dependency)
    return "hello"


@app.get("/hello/{a}")
def hello(request: Request, a: str, b: Annotated[str, Depends(dep)]):
    return {"message": f"Hello {a} {b} !"}


app.crud(User, operations="CRUD")
