import sys

# Import Django modules (now safe after initialization)
from django.core.management import execute_from_command_line

# TODO: make it dynamic
from main import api

# Initialize Django with a virtual app to avoid circular imports


def makemigrations():
    """Create new migrations based on models changes."""
    sys.argv = ["manage.py", "makemigrations", "app"]
    execute_from_command_line(sys.argv)


def migrate():
    """Apply migrations to the database."""
    sys.argv = ["manage.py", "migrate"]
    execute_from_command_line(sys.argv)


def showmigrations():
    """Show all migrations."""
    sys.argv = ["manage.py", "showmigrations"]
    execute_from_command_line(sys.argv)


def startapp():
    """Start a new app."""
    sys.argv = ["manage.py", "startapp", "app_name"]
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python db_commands.py [makemigrations|migrate]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "makemigrations":
        makemigrations()
    elif command == "migrate":
        migrate()
    elif command == "showmigrations":
        showmigrations()
    elif command == "startapp":
        startapp()
    else:
        print("Unknown command. Use 'makemigrations' or 'migrate'")
        sys.exit(1)
