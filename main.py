from typing import Annotated

from pydantic import BaseModel, ConfigDict

from admin import ProductAdmin, UserAdmin
from models import Product, User
from unchained import Depends, Request, Unchained
from unchained.dependencies.header import Header
from unchained.settings import UnchainedSettings, settings

print(settings.django)
print(settings.django.COUCOU)


class Headers(UnchainedSettings):
    x_api_key: str | None = None


app = Unchained()

app.admin.register(User, UserAdmin)
app.admin.register(Product, ProductAdmin)


class BaseHeader(BaseModel):
    model_config = ConfigDict(extra="allow")
    x_api_key: str


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
def hello(a: str, b: Annotated[str, Depends(dep)]):
    return {"message": f"Hello {a} {b} !"}


@app.get("/ahello/{a}")
async def ahello(a: str, b: Annotated[str, Depends(dep)]):
    return {"message": f"ASYNC Hello {a} {b} !"}



app.crud(User, operations="CRUD")
