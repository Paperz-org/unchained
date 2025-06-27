from typing import Annotated, List, Optional

from models import Product, User
from unchained import Unchained
from unchained.dependencies import Header, QueryParams
from unchained.dependencies.depends import Depends
from unchained.ninja_crud import CRUDRouter
from unchained.routers import Router
from admin import UserAdmin

print(UserAdmin)
# router = Router()


# @router.post("/users/")
# def create_user():
#     User.objects.create(name="John Doe", email="john.doe@example.com", password="password")
#     return {"message": "User created"}


# @router.get("/users/")
# async def get_users(
#     test_header: Annotated[str, Header()] = "default",
#     test_query: Annotated[str, QueryParams()] = "default",
# ):
#     return User.objects.all().values()


app = Unchained()
# app.include_router(router)

app.crud(User)

# def test(q: Annotated[str, QueryParams()]):
#     return {
#         "query": q,
#         # "tags": tags,
#     }


# @app.get("/search/")
# def search(
#     # test: Annotated[dict, Depends(test)],
#     page_size: Annotated[int, QueryParams(default=10)],
#     tags: Annotated[list[str], QueryParams()],
# ):
#     return {
#         "test": test,
#         "tags": tags,
#     }
