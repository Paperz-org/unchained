# Contributing to Unchained

!!! quote "Community Driven"
    We welcome contributions to Unchained! This guide will help you get started with contributing to the project.

## Development Setup

=== "Step 1: Clone the repository"
    ```bash
    git clone git@github.com:yourusername/unchained.git
    cd unchained
    ```

=== "Step 2: Create a virtual environment"
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

=== "Step 3: Install dependencies"
    ```bash
    pip install -e ".[dev]"
    ```

!!! tip "Virtual Environment"
    Always use a virtual environment to avoid conflicts with other projects or system-wide Python packages.

## Running Tests

Use pytest to verify that your changes don't break existing functionality:

```bash
pytest
```

## Code Style

Unchained uses `ruff` for code formatting and linting:

| Command | Description |
| ------- | ----------- |
| `ruff format src tests` | Format code according to project style |
| `ruff check src tests` | Check code for style and error issues |

## Contribution Workflow

:material-git: **Step 1**: Create a new branch
```bash
git checkout -b feature/your-feature-name
```

:material-code-tags: **Step 2**: Make your changes
```bash
# Write your code and tests
```

:material-source-commit: **Step 3**: Commit your changes
```bash
git add .
git commit -m "Add your feature or fix description"
```

:material-upload: **Step 4**: Push your changes
```bash
git push origin feature/your-feature-name
```

:material-source-pull: **Step 5**: Create a pull request on GitHub

!!! success "Good Pull Requests"
    - Have a clear purpose and description
    - Include tests for new functionality
    - Update documentation as needed
    - Follow the code style guidelines
    - Address one concern or feature at a time

## Documentation

When making documentation changes:

1. Edit markdown files in the `docs/` directory
2. Run the documentation server to preview changes:
   ```bash
   mkdocs serve
   ```
3. Visit http://127.0.0.1:8000 in your browser

## Getting Help

If you have questions or need help:

- :octicons-issue-opened-16: Open an issue on GitHub
- :fontawesome-brands-github: Check existing issues and discussions

---

<div class="grid cards" markdown>

-   :fontawesome-solid-bug:{ .lg .middle } __Report a Bug__

    ---

    Found a bug? Report it on GitHub Issues.

-   :material-lightbulb:{ .lg .middle } __Feature Request__

    ---

    Have an idea for a new feature? Let us know!

-   :material-file-document:{ .lg .middle } __Improve Docs__

    ---

    Documentation improvements are always welcome.

</div> 