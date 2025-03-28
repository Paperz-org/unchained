from models import User
from unchained import Unchained

# Create API instance and set up Django
app = Unchained()

# Define your endpoints
@app.get("/hello")
def hello(request, name: str = "World"):
    return {"message": f"Hello {name}!"}


@app.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}


# @app.get("/users")
# def get_users(request):
#     return {"users": list(User.objects.all())}

app.crud(User)