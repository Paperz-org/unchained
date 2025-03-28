from models import User
from unchained import Unchained

# Create API instance and set up Django
api = Unchained()


# Define your endpoints
@api.get("/hello")
def hello(request, name: str = "World"):
    return {"message": f"Hello {name}!"}


@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}


@api.get("/users")
def get_users(request):
    return {"users": list(User.objects.all())}
