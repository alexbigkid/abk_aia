"""AI Assistant Git Workflow Interface.

Standardized interface for AI assistant collaboration with Git repositories.
Supports structured workflows and multi-provider Git integration.

Features:
- Multi-provider support (GitHub, GitLab, Bitbucket)
- Standardized branch naming ([B|D|F|R|T] + / + issue number + / + short name)
- AI assistant coordination (ai-coder, ai-reviewer, ai-tester, ai-researcher, ai-marketeer)
- Automated kanban workflow (ToDo → Doing → Review → Testing → Done)
- GitHub project integration
- Issue and pull request management

Example:
    Basic usage::

        from aia import WorkflowCoordinator, WorkflowConfig

        config = WorkflowConfig(repo_owner="user", repo_name="repo", project_number=1)
        coordinator = WorkflowCoordinator("github", config)
        result = coordinator.start_coder_workflow(123)
"""

from aia.workflow_coordinator import WorkflowCoordinator
from aia.git_aia_manager import AiaType, GitBranchType, AiaManagerFactory
from aia.models import WorkflowConfig, WorkflowStatus, Issue, GitOperation


def main() -> None:
    """Main entry point for the CLI interface.

    Runs the full CLI interface for AI assistant workflow management.
    """
    from aia.cli import main as cli_main

    cli_main()


__all__ = [
    "WorkflowCoordinator",
    "AiaType",
    "GitBranchType",
    "AiaManagerFactory",
    "WorkflowConfig",
    "WorkflowStatus",
    "Issue",
    "GitOperation",
    "main",
]
