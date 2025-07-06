"""Init of abk_aia module."""

from abk_aia.workflow_coordinator import WorkflowCoordinator
from abk_aia.git_aia_manager import AiaType, GitBranchType, AiaManagerFactory
from abk_aia.models import WorkflowConfig, WorkflowStatus, Issue, GitOperation


def main() -> None:
    """Main entry point for the AI assistant interface."""
    print("ABK AI Assistant Interface")
    print("=========================")
    print()
    print("This is a standardized interface for AI assistant Git workflow management.")
    print("It supports GitHub, GitLab, and Bitbucket repositories.")
    print()
    print("Key features:")
    print("- Automated kanban workflow (ToDo → Doing → Review → Testing → Done)")
    print(
        "- AI assistant coordination (ai-coder, ai-reviewer, ai-tester, ai-researcher, ai-marketeer)"
    )
    print("- Standardized branch naming (B/, D/, F/, R/, T/ + issue number + short name)")
    print("- GitHub CLI integration for seamless operations")
    print()
    print("For usage examples, see: examples/usage_example.py")
    print("For documentation, see: CLAUDE.md")


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
