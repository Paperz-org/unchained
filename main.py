from typing import Annotated

from admin import ProductAdmin, UserAdmin
from models import Product, User
from unchained import Depends, Unchained

app = Unchained()

app.admin.register(User, UserAdmin)
app.admin.register(Product, ProductAdmin)


def other_dependency() -> str:
    return "world"


def dependency(other_dependency: Annotated[str, Depends(other_dependency)]) -> str:
    return other_dependency


@app.get("/hello/{a}")
def hello(request, a: str, b: Annotated[str, Depends(dependency)]):
    return {"message": f"Hello {a} {b} !"}


app.crud(User, operations="CRUD")
