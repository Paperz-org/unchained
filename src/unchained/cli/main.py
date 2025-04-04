from typing import Optional, Tuple, Any

from typer import Argument, Option, Typer, echo

from unchained.cli.db import app as db_app

# Enhanced help text for the main app
app = Typer(name="unchained", help="Unchained CLI tool - A modern web framework for building Python web applications")
app.add_typer(db_app, name="migrations", help="Database migration commands for managing your application's schema")


def _load_app(app_path: Optional[str] = None) -> Tuple[str, Any, Any]:
    """
    Load the application from the given path or detect it automatically.
    
    Returns:
        Tuple containing:
        - app_path_str: The string representation of the app path
        - module: The imported module
        - instance: The app instance from the module
    """
    from unchained.cli.utils import get_app_path_arg, load_app_module
    
    path = get_app_path_arg(app_path)
    module, instance = load_app_module(path)
    
    return path, module, instance


@app.command(name="start")
def runserver(
    app_path: Optional[str] = Argument(None, help="Path to the app module and instance in the format module:instance"),
    host: str = Option("127.0.0.1", "--host", "-h", help="Host to bind the server to (default: 127.0.0.1)"),
    port: int = Option(8000, "--port", "-p", help="Port to bind the server to (default: 8000)"),
    reload: bool = Option(True, "--reload/--no-reload", help="Enable auto-reload for development (default: enabled)"),
):
    """
    Run the development server using uvicorn.

    Launches a local development server with the specified application.
    If app_path is not provided, it will be detected automatically from:
    1. UNCHAINED_APP_PATH environment variable
    2. pyproject.toml [tool.unchained] settings
    3. Common app patterns in current directory
    """
    path, _, _ = _load_app(app_path)

    # Only import uvicorn when needed
    import uvicorn

    uvicorn.run(path, host=host, port=port, reload=reload, factory=True)


@app.command(name="collectstatic")
def collectstatic():
    """
    Collect static files.
    """
    from django.core.management import call_command

    call_command("collectstatic", interactive=False, clear=True, link=True)

    
# Add a helper command that doesn't require Django loading
@app.command()
def version():
    """
    Show the current version of Unchained.

    Displays the installed version of the Unchained framework.
    This command is useful for debugging and when reporting issues.
    """
    from importlib.metadata import version as get_version

    try:
        v = get_version("unchained")
        echo(f"Unchained version: {v}")
    except Exception:
        echo("Unchained version: development")


@app.command(name="createsuperuser")
def createsuperuser(
    app_path: Optional[str] = Argument(None, help="Path to the app module and instance in the format module:instance"),
    username: Optional[str] = Argument(None, help="Superuser username (optional, will prompt if not provided)"),
    email: Optional[str] = Argument(None, help="Superuser email (optional, will prompt if not provided)"),
    noinput: bool = Argument(False, help="Run without user input, using provided username and email"),
):
    """
    Create a superuser account for the admin interface.

    Creates an administrator account with full permissions to manage
    your application through the Django admin interface. Will prompt
    for username, email, and password unless provided as arguments.

    Examples:
      unchained migrations createsuperuser                  # Interactive creation
      unchained migrations createsuperuser admin admin@example.com  # With username and email
    """
    _load_app(app_path)

    from django.conf import settings

    # Settings should already be configured by the Unchained instance
    # If not configured, this will raise an exception
    if not settings.configured:
        echo("Error: Django settings are not configured. Ensure your app properly configures settings.")
        return

    from django.core.management import call_command

    args: list[str] = []
    kwargs: dict[str, object] = {}

    if username:
        kwargs["username"] = username
    if email:
        kwargs["email"] = email
    if noinput:
        kwargs["interactive"] = not noinput

    call_command("createsuperuser", *args, **kwargs)

@app.command(name="shell")
def shell(
    app_path: Optional[str] = Argument(None, help="Path to the app module and instance in the format module:instance"),
):
    """
    Start the Django shell.
    """
    _load_app(app_path)

    from django.conf import settings

    # Settings should already be configured by the Unchained instance
    # If not configured, this will raise an exception
    if not settings.configured:
        echo("Error: Django settings are not configured. Ensure your app properly configures settings.")
        return

    from django.core.management import call_command

    call_command("shell")

def main():
    app(prog_name="unchained")


if __name__ == "__main__":
    main()
