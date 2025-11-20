# Tinty Development Justfile
# Run with: just <command>

# Show available commands
default:
    @just --list

# Development setup
# Development setup with Poetry
setup-poetry:
    poetry install --with dev
    poetry run pre-commit install

# Run tests
test:
    poetry run pytest

# Run tests with coverage
test-cov:
    poetry run pytest --cov=tinty --cov-report=html --cov-report=term

# Run type checking
typecheck:
    poetry run mypy src/

# Run linting and formatting
lint:
    poetry run ruff check --preview .

# Auto-fix linting issues
lint-fix:
    poetry run ruff check --preview --fix .

# Format code
format:
    poetry run ruff format --preview .

# Run all quality checks
check: lint typecheck test

# Run pre-commit hooks on all files
pre-commit:
    poetry run pre-commit run --all-files

# Clean build artifacts
clean:
    rm -rf build/ dist/ *.egg-info/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Build package with Poetry
build-poetry: clean
    poetry build

# Build and check package
build-check: build-poetry
    twine check dist/*



# Run example scripts
example script="quickstart":
    poetry run python examples/{{script}}.py

# Run CLI help
cli-help:
    poetry run tinty --help

# Test CLI functionality
cli-test:
    echo "hello world" | poetry run tinty 'l' red

# Create a new release (requires version bump)
release: check build-poetry
    @echo "Ready to release! Run: just publish-test or just publish"

# Publish to test PyPI
publish-test: build-poetry
    poetry publish --repository testpypi

# Publish to PyPI (PRODUCTION)
publish: build-poetry
    poetry publish

# Show package info
info:
    @echo "Package: tinty"
    @echo "Version: $(poetry run python -c 'import tinty; print(tinty.__version__)' 2>/dev/null || echo 'not installed')"
    @echo "Location: $(poetry run python -c 'import tinty; print(tinty.__file__)' 2>/dev/null || echo 'not found')"

# Show available colors demo
demo:
    poetry run python -c "from tinty import C, RED, GREEN, BLUE, BOLD; print(C('✅ Tinty works!') | GREEN | BOLD)"


# Generate screenshots for README (syncs examples, creates scripts, captures images)
screenshots:
    @echo "📸 Generating terminal screenshots for README..."
    @echo "🔄 Syncing examples between README and scripts..."
    @mkdir -p docs/images scripts
    poetry run python scripts/sync_examples.py
    chmod +x scripts/cli_examples.sh scripts/pipeline_demo.sh
    @echo "📸 Capturing screenshots with termshot..."
    @echo "Capturing basic colors example..."
    -termshot --filename docs/images/basic-colors.png --columns 80 poetry run python scripts/basic_colors.py
    @echo "Capturing CLI pattern highlighting examples..."
    -termshot --filename docs/images/cli-examples.png --columns 80 poetry run scripts/cli_examples.sh
    @echo "Capturing complex styling example..."
    -termshot --filename docs/images/complex-styling.png --columns 80 poetry run python scripts/complex_styling.py
    @echo "Capturing pattern highlighting example..."
    -termshot --filename docs/images/pattern-highlighting.png --columns 80 poetry run python scripts/pattern_highlighting.py
    @echo "Capturing nested groups example..."
    -termshot --filename docs/images/nested-groups.png --columns 80 poetry run python scripts/nested_groups.py
    @echo "Capturing channel isolation example..."
    -termshot --filename docs/images/channel-isolation.png --columns 80 poetry run python scripts/channel_isolation.py
    @echo "Capturing pipeline demo..."
    -termshot --filename docs/images/pipeline-demo.png --columns 80 poetry run scripts/pipeline_demo.sh
    @echo "Capturing both formats demo..."
    -termshot --filename docs/images/both-formats.png --columns 80 poetry run python scripts/both_formats.py
    @echo "✅ Screenshots generation complete (run in real terminal if termshot failed)"
    @echo "✅ README and scripts are synchronized"
