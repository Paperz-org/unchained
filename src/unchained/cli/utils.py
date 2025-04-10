from typing import Optional


def find_app_path():
    """
    Find the app path automatically in this order:
    1. From UNCHAINED_APP_PATH environment variable
    2. From pyproject.toml [tool.unchained] app_path setting
    3. From .unchained file in the current directory
    4. By searching common patterns in current directory
    """
    import os

    # Check environment variable first
    if "UNCHAINED_APP_PATH" in os.environ:
        return os.environ["UNCHAINED_APP_PATH"]

    # Check pyproject.toml

    from pathlib import Path

    import tomli

    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            pyproject = tomli.load(f)
            if "tool" in pyproject and "unchained" in pyproject["tool"]:
                if "app_path" in pyproject["tool"]["unchained"]:
                    return pyproject["tool"]["unchained"]["app_path"]

    return None


def get_app_path_arg(value: Optional[str]):
    """Helper function to get app path with automatic detection"""
    from typer import Exit, echo

    if value is None:
        detected_path = find_app_path()
        if detected_path is None:
            echo("Error: Couldn't detect app path automatically. Please specify it as an argument.")
            echo("Example: unchained start main:app")
            raise Exit(1)
        return detected_path
    return value


def load_app_module(app_path: str):
    """Load the app module and get the Unchained instance"""
    # Ensure the current directory is in the Python path
    import importlib
    import sys

    from typer import echo

    if "" not in sys.path:
        sys.path.insert(0, "")

    # Parse the app_path
    module_path, app_instance = app_path.split(":", 1)

    # Check if module exists
    try:
        # Just try to import to verify it exists
        if module_path.endswith(".py"):
            # If it's a .py file, remove the extension
            module_path = module_path[:-3]
        module = importlib.import_module(module_path)
        return module, getattr(module, app_instance)
    except ImportError:
        echo(f"Error: Could not import module '{module_path}'")
        sys.exit(1)
    except AttributeError:
        echo(f"Error: Could not find '{app_instance}' in module '{module_path}'")


class AppHandler:
    """
    A class that encapsulates app path finding and module loading functionality.
    Provides the same functionality as the standalone functions but in an OOP approach.
    """

    @staticmethod
    def find_app_path():
        """
        Find the app path automatically in this order:
        1. From UNCHAINED_APP_PATH environment variable
        2. From pyproject.toml [tool.unchained] app_path setting
        3. From .unchained file in the current directory
        4. By searching common patterns in current directory
        """
        import os

        # Check environment variable first
        if "UNCHAINED_APP_PATH" in os.environ:
            return os.environ["UNCHAINED_APP_PATH"]

        # Check pyproject.toml
        from pathlib import Path
        import tomli

        pyproject_path = Path("pyproject.toml")
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                pyproject = tomli.load(f)
                if "tool" in pyproject and "unchained" in pyproject["tool"]:
                    if "app_path" in pyproject["tool"]["unchained"]:
                        return pyproject["tool"]["unchained"]["app_path"]

        return None

    @staticmethod
    def get_app_path_arg(value: Optional[str]):
        """Helper method to get app path with automatic detection"""
        from typer import Exit, echo

        if value is None:
            detected_path = AppHandler.find_app_path()
            if detected_path is None:
                echo("Error: Couldn't detect app path automatically. Please specify it as an argument.")
                echo("Example: unchained start main:app")
                raise Exit(1)
            return detected_path
        return value

    @staticmethod
    def load_app_module(app_path: str):
        """Load the app module and get the Unchained instance"""
        # Ensure the current directory is in the Python path
        import importlib
        import sys
        from typer import echo

        if "" not in sys.path:
            sys.path.insert(0, "")

        # Parse the app_path
        module_path, app_instance = app_path.split(":", 1)

        # Check if module exists
        try:
            # Just try to import to verify it exists
            if module_path.endswith(".py"):
                # If it's a .py file, remove the extension
                module_path = module_path[:-3]
            module = importlib.import_module(module_path)
            return module, getattr(module, app_instance)
        except ImportError:
            echo(f"Error: Could not import module '{module_path}'")
            sys.exit(1)
        except AttributeError:
            echo(f"Error: Could not find '{app_instance}' in module '{module_path}'")

    def __init__(self, app_path: Optional[str] = None):
        """
        Initialize the app handler with an optional app path.
        If app_path is None, automatic detection will be attempted.
        """
        self.app_path = self.get_app_path_arg(app_path)
        self.module = None
        self.app_instance = None

    def load(self):
        """Load the application module and return the module and app instance"""
        self.module, self.app_instance = self.load_app_module(self.app_path)
        return self.module, self.app_instance
