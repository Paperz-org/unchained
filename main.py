import asyncio
from dataclasses import dataclass
from typing import Annotated

from ezq import EZQEvent, on_event, publish_event
from pydantic import BaseModel, ConfigDict

from admin import ProductAdmin, UserAdmin
from models import Product, User
from unchained import Depends, Request, Unchained
from unchained.dependencies.background_tasks import BackgroundTask
from unchained.dependencies.header import Header

# @dataclass
# class TestEvent(EZQEvent):
#     message: str


# @on_event
# async def test_event(event: TestEvent):
#     print("test_event", event)


class Headers(BaseModel):
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


def dependency(
    request: Request, other_dependency: Annotated[str, Depends(other_dependency)]
) -> str:
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
def hello(a: str, b: Annotated[str, Depends(dep)], x_api_key: Annotated[str, Header()]):
    print(x_api_key)
    return {"message": f"Hello {a} {b} !"}


def send_email(message: str) -> None:
    print("sending email", message)


@app.get("/task/{message}")
def task(message: str, background_task: Annotated[BackgroundTask, BackgroundTask(send_email)]):
    asyncio.run(background_task.start())
    return {"message": "Task published"}


app.crud(User, operations="CRUD")
