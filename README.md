# AI Assistant Interface

A standardized AI assistant interface for Git workflow management supporting GitHub, GitLab, and Bitbucket repositories. Deploy to any repository for automated AI-driven development workflows.

## Key Features

- **🔄 Multi-repository support**: Use across unlimited GitHub repositories
- **🌐 Multi-provider support**: GitHub (fully implemented), GitLab and Bitbucket (interfaces defined)
- **📋 Standardized branch naming**: [B|D|F|R|T] + / + issue number + / + short name
- **🤖 AI assistant coordination**: ai-coder, ai-reviewer, ai-tester, ai-researcher, ai-marketeer
- **⚡ Automated kanban workflow**: Triage → ToDo → Doing → Review → Testing → Done
- **📊 GitHub project integration**: Seamless project board management
- **🔧 Issue and pull request management**: Complete workflow automation

## Quick Start

### Installation

```bash
# Clone and install globally
git clone https://github.com/alexbigkid/aia.git
cd aia
./install.sh

# Or install manually
pip install -e .
```

### Deploy to Any Repository

```bash
# Navigate to your target repository
cd /path/to/your/repo

# Set up AI workflow (interactive)
aia setup

# Validate setup
aia validate

# Check status
aia status
```

### Basic Usage

```bash
# Show current repository context
aia info

# Create new issue
aia create-issue --title "Add user authentication"

# Trigger AI agents
aia trigger ai-coder      # Pick up ToDo issue → Doing
aia trigger ai-reviewer   # Review code → Testing
aia trigger ai-tester     # Test implementation → Done + PR
```

## Multi-Repository Deployment

### Option 1: Global Installation (Recommended)

Install once, use everywhere:

```bash
# Install globally
git clone https://github.com/alexbigkid/aia.git
cd aia && ./install.sh

# Use in any repository
cd /path/to/project1 && aia setup
cd /path/to/project2 && aia setup
```

### Option 2: Git Submodule

Add to specific repositories:

```bash
# Add as submodule
cd your-repo
git submodule add https://github.com/alexbigkid/aia.git .aia

# Setup workflow
python .aia/scripts/setup_repo_workflow.py
```

### Option 3: Direct Clone

```bash
cd your-repo
git clone https://github.com/alexbigkid/aia.git .aia
python .aia/scripts/setup_repo_workflow.py
```

## CLI Commands

```bash
aia setup                    # Interactive repository setup
aia info                     # Show repository context
aia status                   # Project board status
aia validate                 # Validate configuration
aia create-issue             # Create new issue
aia trigger ai-coder         # Trigger AI coder workflow
aia trigger ai-reviewer      # Trigger AI reviewer workflow
aia trigger ai-tester        # Trigger AI tester workflow
aia --help                   # Show all commands
```

## Workflow Process

1. **Create Issue**: Manual or `aia create-issue` → **Triage**
2. **Triage**: Review and move to **ToDo** with priority
3. **AI Implementation**: `aia trigger ai-coder` → **Doing** → **Review**
4. **AI Code Review**: Automatic → **Testing**
5. **AI Testing**: Automatic → **Done** + **Pull Request**
6. **Human Review**: Review and merge PR

## Repository Context

The system automatically detects your current repository context:

- **Environment Variables**: `GITHUB_REPO_OWNER`, `GITHUB_REPO_NAME`, `GITHUB_PROJECT_NUMBER`
- **Config File**: `.aia_config.json` in repository root
- **Git Remote**: Auto-detection from `git remote get-url origin`

Use `aia info` to see your current context.

## Configuration

Each repository gets its own configuration:

```json
{
  "repo_owner": "your-username",
  "repo_name": "your-repo",
  "project_number": 123,
  "default_base_branch": "main"
}
```

## Architecture

### Core Components

- **`models.py`** - Data models (Issue, PullRequest, WorkflowConfig, etc.)
- **`git_aia_manager.py`** - Strategy pattern implementation for different Git providers
- **`workflow_coordinator.py`** - Orchestrates AI assistant collaboration
- **`cli.py`** - Command-line interface for all operations

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

Kanban workflow: 🔍 Triage → 📋 ToDo → 🔄 Doing → 👀 Review → 🧪 Testing → ✅ Done

## Development Commands

### Code Quality and Testing

```bash
# Run code formatting and linting
uv run ruff check
uv run ruff format

# Run pytest unit tests (includes coverage by default)
uv run pytest                            # Run tests with coverage
uv run pytest -v                         # Verbose output with coverage
uv run pytest --no-cov                   # Run tests without coverage

# Coverage testing with different options
uv run pytest --cov --cov-report=xml     # Generate XML coverage report
uv run pytest --cov --cov-report=html    # Generate HTML coverage report
uv run pytest --cov --cov-report=term    # Terminal coverage report only

# Run comprehensive test suite
uv run python run_tests.py
```

### Building and Running

```bash
# Build the package
python -m build

# Run the main application
aia
# or
python -m aia
```

## Key Dependencies

- **colorama** - Terminal color output support
- **ruff** - Modern Python linter and formatter (dev dependency)
- **coverage** - Test coverage reporting (dev dependency)
- **parameterized** - Test parameterization support (dev dependency)
- **pytest** - Testing framework (dev dependency)
- **pytest-mock** - Mock support for pytest (dev dependency)

## Development Notes

- The project uses `hatchling` as the build backend
- Requires Python 3.13 or higher
- Uses `ruff` for both linting and formatting (replaces black/flake8)
- GitHub CLI (`gh`) is required for GitHub operations
- See `examples/usage_example.py` for comprehensive usage examples
- Run `python run_tests.py` for comprehensive test suite execution
- Test coverage: 99% with 96 passing unit tests (using pytest-cov)

## Documentation

- **CLAUDE.md** - Complete development and usage guide
- **DEPLOYMENT.md** - Multi-repository deployment patterns
- **examples/usage_example.py** - Code examples and patterns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `uv run pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
