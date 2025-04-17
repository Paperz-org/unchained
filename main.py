from unchained import Unchained

app = Unchained()

@app.get("/")
def index():
    return "Hello, World!"