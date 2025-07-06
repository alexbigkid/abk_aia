# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based AI assistant interface project called `abk_aia`. It's built as a modern Python package using the `hatchling` build system and follows Python 3.13+ standards.

## Development Commands

### Installation and Setup
```bash
# Install the package in development mode
pip install -e .

# Install development dependencies
pip install -e .[dev]
```

### Code Quality and Testing
```bash
# Run code formatting and linting
ruff check
ruff format

# Run tests with coverage
coverage run -m pytest
coverage report
```

### Building and Running
```bash
# Build the package
python -m build

# Run the main application
abk_aia
# or
python -m abk_aia
```

## Architecture

This is a standardized AI assistant interface for Git workflow management. The project follows a modular architecture:

### Core Components

- **`models.py`** - Data models (Issue, PullRequest, WorkflowConfig, etc.)
- **`git_aia_manager.py`** - Strategy pattern implementation for different Git providers
- **`workflow_coordinator.py`** - Orchestrates AI assistant collaboration
- **`abk_common.py`** - Common utilities and decorators

### AI Assistant Types

- **ai-coder** - Implements features, fixes bugs, creates documentation
- **ai-researcher** - Conducts research before implementation
- **ai-tester** - Creates and runs tests
- **ai-marketeer** - Market research and promotion strategies
- **ai-reviewer** - Reviews PRs and provides feedback

### Branch Naming Convention

- **B** - Bug fixes (B/{issue_number}/{short-issue-name})
- **D** - Documentation (D/{issue_number}/{short-issue-name})
- **F** - Features (F/{issue_number}/{short-issue-name})
- **R** - Research (R/{issue_number}/{short-issue-name})
- **T** - Tests (T/{issue_number}/{short-issue-name})

### Workflow States

Kanban workflow: 📋 ToDo → 🔄 Doing → 👀 Review → 🧪 Testing → ✅ Done

### Git Provider Support

- **GitHub** - Fully implemented with GitHub CLI integration
- **GitLab** - Interface defined, implementation pending
- **Bitbucket** - Interface defined, implementation pending

## Key Dependencies

- **colorama** - Terminal color output support
- **ruff** - Modern Python linter and formatter (dev dependency)
- **coverage** - Test coverage reporting (dev dependency)
- **parameterized** - Test parameterization support (dev dependency)

## Development Notes

- The project uses `hatchling` as the build backend
- Requires Python 3.13 or higher
- Uses `ruff` for both linting and formatting (replaces black/flake8)
- GitHub CLI (`gh`) is required for GitHub operations
- See `examples/usage_example.py` for comprehensive usage examples
