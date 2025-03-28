from unchained import Unchained

# Create API instance and set up Django
api = Unchained()

# from models import User

# Register models explicitly
# api.register_model(User)


# Define your endpoints
@api.get("/hello")
def hello(request, name: str = "World"):
    return {"message": f"Hello {name}!"}


@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}
