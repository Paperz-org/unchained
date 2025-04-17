from unchained import Unchained

app = Unchained()

@app.get("/")
def index():
    return {"message": "Hello, World!"}