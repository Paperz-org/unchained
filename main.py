from typing import Annotated, Any

from django.contrib import admin

from admin import ProductAdmin, UserAdmin
from models import Product, User
from unchained import Depends, Unchained

app = Unchained()

admin.site.register(User, UserAdmin)
admin.site.register(Product, ProductAdmin)


class Toto:
    def __init__(self, a: str):
        self.a = a

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.a


def other_dependency() -> str:
    return "world"


def try_other_dependency(a: Annotated[str, Depends(other_dependency)]):
    return Toto(a)


def dependency(other_dependency: Annotated[str, Depends(other_dependency)]) -> str:
    return other_dependency


@app.get("/hello/{a}")
def hello(request, a: str, b: Annotated[str, Depends(dependency)]):
    return {"message": f"Hello {a} {b} !"}


app.crud(User)
