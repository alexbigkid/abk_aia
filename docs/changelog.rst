Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------

[0.1.0] - 2025-07-06
---------------------

Added
^^^^^

- Initial release of ABK AIA (AI Assistant Git Workflow Interface)
- **Multi-provider support**: GitHub implementation (GitLab and Bitbucket placeholders)
- **Standardized branch naming**: [B|D|F|R|T] + / + issue number + / + short name convention
- **AI assistant coordination**: Support for ai-coder, ai-reviewer, ai-tester, ai-researcher, ai-marketeer
- **Automated kanban workflow**: ToDo → Doing → Review → Testing → Done state management
- **GitHub CLI integration**: Complete GitHub operations using gh CLI
- **Issue management**: Get, update, assign, and label issues
- **Branch operations**: Automated branch creation with standardized naming
- **Pull request management**: Create PRs and manage workflow completion
- **Project board integration**: Update issue status in GitHub project boards
- **Workflow coordination**: Complete AI assistant workflow orchestration
- **Data models**: Comprehensive models for issues, PRs, configurations, and operations
- **Factory pattern**: Extensible manager creation for different Git providers
- **Type safety**: Full type hints and validation throughout
- **Documentation**: Complete Sphinx documentation with RTD theme
- **Examples**: Comprehensive usage examples and workflow demonstrations

Technical Details
^^^^^^^^^^^^^^^^^^

- **Python 3.13+ support**: Built with modern Python features
- **GitHub CLI dependency**: Uses gh CLI for all GitHub operations  
- **Set intersection optimization**: Efficient label matching using set operations
- **Strategy pattern**: Extensible architecture for multiple Git providers
- **Comprehensive error handling**: Detailed error reporting and validation
- **Dataclass models**: Clean, typed data structures throughout
- **Abstract base classes**: Well-defined interfaces for extensibility

Dependencies
^^^^^^^^^^^^

- **colorama**: Cross-platform colored terminal text
- **GitHub CLI (gh)**: Required for GitHub operations
- **Git**: Required for local Git operations

Development Dependencies
^^^^^^^^^^^^^^^^^^^^^^^

- **ruff**: Code linting and formatting
- **coverage**: Test coverage reporting  
- **parameterized**: Parameterized test support
- **sphinx**: Documentation generation
- **sphinx-rtd-theme**: Read the Docs theme for documentation