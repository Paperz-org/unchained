# Minimal Django Ninja API

This is a minimal Django application using Django Ninja that runs from a single file. No project setup or app creation required!

## Setup

1. Install the requirements:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The server will start at http://127.0.0.1:8000 with hot-reload enabled.

## Available Endpoints

- GET `/api/hello?name=YourName` - Returns a greeting message
  - Optional query parameter: `name` (default: "World")
  - Example response: `{"message": "Hello YourName!"}`

- GET `/api/add?a=5&b=3` - Adds two numbers
  - Required query parameters: `a` and `b` (integers)
  - Example response: `{"result": 8}`

## Features

- Single file Django application
- Fast API development with Django Ninja
- ASGI server with hot-reload
- No project/app setup required
- Type hints and automatic OpenAPI documentation
