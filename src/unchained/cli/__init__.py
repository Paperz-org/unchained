from typing import Optional

import typer

from unchained.cli.db import app as db_app
from unchained.cli.utils import get_app_path_arg

# Use help for better documentation instead of callback
app = typer.Typer(name="unchained", help="Unchained CLI tool")
app.add_typer(db_app, name="migration", help="Database migration commands")


@app.command(name="start")
def runserver(
    app_path: Optional[str] = typer.Argument(None, help="Path to the app module and instance (module:instance)"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind the server to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind the server to"),
    reload: bool = typer.Option(True, "--reload/--no-reload", help="Enable auto-reload"),
):
    """Run the development server using uvicorn"""
    import importlib
    import sys

    app_path_str = get_app_path_arg(app_path)

    # Ensure the current directory is in the Python path
    if "" not in sys.path:
        sys.path.insert(0, "")

    # Parse the app_path
    module_path, app_instance = app_path_str.split(":", 1)

    # Check if module exists before running uvicorn
    try:
        # Just try to import to verify it exists
        if module_path.endswith(".py"):
            # If it's a .py file, remove the extension
            module_path = module_path[:-3]
        importlib.import_module(module_path)
    except ImportError:
        typer.echo(f"Error: Could not import module '{module_path}'")
        return

    # Only import uvicorn when needed
    import uvicorn

    uvicorn.run(app_path_str, host=host, port=port, reload=reload)


# Add a helper command that doesn't require Django loading
@app.command()
def version():
    """Show the current version of Unchained"""
    from importlib.metadata import version as get_version

    try:
        v = get_version("unchained")
        typer.echo(f"Unchained version: {v}")
    except Exception:
        typer.echo("Unchained version: development")


def main():
    app(prog_name="unchained")


if __name__ == "__main__":
    main()
