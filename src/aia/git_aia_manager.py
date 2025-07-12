"""Git AI assistant manager implementation.

Provides AI assistant workflow management across different Git providers.
Implements Strategy pattern for extensible provider support.
"""

# Standard lib imports
from abc import ABCMeta, abstractmethod
from enum import Enum
import json
import subprocess

# Third party imports

# Local imports
from aia import abk_common
from aia.models import Issue, WorkflowConfig, GitOperation, WorkflowStatus


# -----------------------------------------------------------------------------
# Local Constants
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Git Branch Type
# -----------------------------------------------------------------------------
class GitBranchType(Enum):
    """Git branch type enumeration.

    Defines branch prefixes: B (bug), D (docs), F (feature), R (research), T (test).
    """

    BUG = "B"
    DOCUMENTATION = "D"
    FEATURE = "F"
    RESEARCH = "R"
    TEST = "T"


# -----------------------------------------------------------------------------
# AI assistant type
# -----------------------------------------------------------------------------
class AiaType(Enum):
    """AI assistant type enumeration.

    Defines available AI assistant types in the workflow.
    """

    AI_CODER = "ai-coder"
    AI_MARKETEER = "ai-marketeer"
    AI_REVIEWER = "ai-reviewer"
    AI_RESEARCHER = "ai-researcher"
    AI_TESTER = "ai-tester"


# -----------------------------------------------------------------------------
# git AI assistant manager base
# -----------------------------------------------------------------------------
class AiaManagerBase(metaclass=ABCMeta):
    """Abstract base class for AI assistant managers.

    Args:
        aia_type: AI assistant type
        config: Workflow configuration
    """

    def __init__(self, aia_type: AiaType, config: WorkflowConfig) -> None:
        """Initialize the AI assistant manager."""
        self.aia_type = aia_type
        self.config = config

    def generate_branch_name(self, issue: Issue) -> str:
        """Generate standardized branch name: {prefix}/{issue_number}/{short_name}.

        Args:
            issue: Issue object containing labels and metadata

        Returns:
            Formatted branch name (e.g., "F/123/add-user-auth")
        """
        # Determine branch type based on issue labels
        branch_type = self._get_branch_type_from_labels(issue.labels)
        short_name = issue.get_short_name()
        return f"{branch_type.value}/{issue.number}/{short_name}"

    def _get_branch_type_from_labels(self, labels: list[str]) -> GitBranchType:
        """Determine branch type from issue labels using set intersection.

        Args:
            labels: List of issue labels

        Returns:
            Branch type, defaults to FEATURE if no type labels found
        """
        type_labels = {"bug", "documentation", "feature", "research", "test"}
        labels_set = set(labels)

        # Find intersection - should contain exactly one type label
        found_types = type_labels.intersection(labels_set)

        if found_types:
            # Get the single type label (since there should only be one)
            type_label = found_types.pop()
            match type_label:
                case "bug":
                    return GitBranchType.BUG
                case "documentation":
                    return GitBranchType.DOCUMENTATION
                case "feature":
                    return GitBranchType.FEATURE
                case "research":
                    return GitBranchType.RESEARCH
                case "test":
                    return GitBranchType.TEST

        # Default to feature if no type label found
        return GitBranchType.FEATURE

    @abstractmethod
    def get_issues(self, status: WorkflowStatus | None = None) -> list[Issue]:
        """Get issues from the repository."""
        raise NotImplementedError

    @abstractmethod
    def get_issue(self, issue_number: int) -> Issue | None:
        """Get a specific issue by number."""
        raise NotImplementedError

    @abstractmethod
    def update_issue_status(self, issue: Issue, new_status: WorkflowStatus) -> GitOperation:
        """Update issue status in project board."""
        raise NotImplementedError

    @abstractmethod
    def add_label_to_issue(self, issue: Issue, label: str) -> GitOperation:
        """Add label to issue."""
        raise NotImplementedError

    @abstractmethod
    def remove_label_from_issue(self, issue: Issue, label: str) -> GitOperation:
        """Remove label from issue."""
        raise NotImplementedError

    @abstractmethod
    def create_branch(self, issue: Issue) -> GitOperation:
        """Create branch for issue."""
        raise NotImplementedError

    @abstractmethod
    def create_commit(self, branch: str, files: list[str], message: str):
        """Abstract method - should not be implemented. Interface purpose."""
        raise NotImplementedError

    @abstractmethod
    def push_commit(self, branch: str, files, message):
        """Abstract method - should not be implemented. Interface purpose."""
        raise NotImplementedError

    @abstractmethod
    def create_pr(self, title: str, body: str, head, base):
        """Abstract method - should not be implemented. Interface purpose."""
        raise NotImplementedError

    @abstractmethod
    def comment_on_pr(self, repo, pr_number, message):
        """Abstract method - should not be implemented. Interface purpose."""
        raise NotImplementedError

    @abstractmethod
    def assign_to_ai(self, issue: Issue, ai_type: AiaType) -> GitOperation:
        """Assign issue to AI assistant."""
        raise NotImplementedError

    @abstractmethod
    def get_assigned_issues(self) -> list[Issue]:
        """Get issues assigned to this AI assistant."""
        raise NotImplementedError


# -----------------------------------------------------------------------------
# GitHub AI assistant Manager
# -----------------------------------------------------------------------------
class GitHubAiaManager(AiaManagerBase):
    """GitHub AI assistant manager implementation.

    Uses GitHub CLI (gh) for all GitHub operations.
    Requires: gh CLI installed and authenticated.
    """

    @abk_common.function_trace
    def get_issues(self, status: WorkflowStatus | None = None) -> list[Issue]:
        """Get issues from GitHub repository."""
        try:
            cmd = [
                "gh",
                "issue",
                "list",
                "--repo",
                self.config.repo_full_name,
                "--json",
                "number,title,body,state,labels,assignees,createdAt,updatedAt,url",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            issues_data = json.loads(result.stdout)

            issues = []
            for issue_data in issues_data:
                issue = self._parse_issue_data(issue_data)
                if status is None or issue.project_status == status:
                    issues.append(issue)

            return issues
        except subprocess.CalledProcessError as e:
            print(f"Error getting issues: {e.stderr}")
            return []

    @abk_common.function_trace
    def get_issue(self, issue_number: int) -> Issue | None:
        """Get a specific issue by number."""
        try:
            cmd = [
                "gh",
                "issue",
                "view",
                str(issue_number),
                "--repo",
                self.config.repo_full_name,
                "--json",
                "number,title,body,state,labels,assignees,createdAt,updatedAt,url",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            issue_data = json.loads(result.stdout)

            return self._parse_issue_data(issue_data)
        except subprocess.CalledProcessError as e:
            print(f"Error getting issue {issue_number}: {e.stderr}")
            return None

    @abk_common.function_trace
    def update_issue_status(self, issue: Issue, new_status: WorkflowStatus) -> GitOperation:
        """Update issue status in GitHub project board."""
        try:
            if self.config.project_number:
                cmd = [
                    "gh",
                    "project",
                    "item-edit",
                    "--project-number",
                    str(self.config.project_number),
                    "--field",
                    "Status",
                    "--text",
                    new_status.value,
                    "--issue",
                    str(issue.number),
                ]

                subprocess.run(cmd, capture_output=True, text=True, check=True)
                return GitOperation(success=True, message=f"Updated issue {issue.number} status to {new_status.value}")
            else:
                return GitOperation(success=False, message="No project number configured")
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Error updating issue status: {e.stderr}", error=e.stderr)

    @abk_common.function_trace
    def add_label_to_issue(self, issue: Issue, label: str) -> GitOperation:
        """Add label to GitHub issue."""
        try:
            cmd = ["gh", "issue", "edit", str(issue.number), "--repo", self.config.repo_full_name, "--add-label", label]

            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return GitOperation(success=True, message=f"Added label '{label}' to issue {issue.number}")
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Error adding label: {e.stderr}", error=e.stderr)

    @abk_common.function_trace
    def remove_label_from_issue(self, issue: Issue, label: str) -> GitOperation:
        """Remove label from GitHub issue."""
        try:
            cmd = ["gh", "issue", "edit", str(issue.number), "--repo", self.config.repo_full_name, "--remove-label", label]

            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return GitOperation(success=True, message=f"Removed label '{label}' from issue {issue.number}")
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Error removing label: {e.stderr}", error=e.stderr)

    @abk_common.function_trace
    def create_branch(self, issue: Issue) -> GitOperation:
        """Create branch for GitHub issue."""
        try:
            branch_name = self.generate_branch_name(issue)

            # Create and checkout new branch
            cmd = ["git", "checkout", "-b", branch_name]
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            return GitOperation(success=True, message=f"Created branch '{branch_name}' for issue {issue.number}", output=branch_name)
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Error creating branch: {e.stderr}", error=e.stderr)

    @abk_common.function_trace
    def create_commit(self, branch: str, files: list[str], message: str) -> GitOperation:
        """Create commit with specified files."""
        try:
            # Add files to staging area
            for file in files:
                cmd = ["git", "add", file]
                subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Create commit
            cmd = ["git", "commit", "-m", message]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            return GitOperation(success=True, message=f"Created commit on branch '{branch}'", output=result.stdout)
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Error creating commit: {e.stderr}", error=e.stderr)

    @abk_common.function_trace
    def push_commit(self, branch: str, files: list[str], message: str) -> GitOperation:
        """Push branch to remote repository."""
        try:
            # Push branch to remote
            cmd = ["git", "push", "origin", branch]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            return GitOperation(success=True, message=f"Pushed branch '{branch}' to remote", output=result.stdout)
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Error pushing branch: {e.stderr}", error=e.stderr)

    @abk_common.function_trace
    def create_pr(self, title: str, body: str, head: str, base: str) -> GitOperation:
        """Create pull request on GitHub."""
        try:
            cmd = [
                "gh",
                "pr",
                "create",
                "--repo",
                self.config.repo_full_name,
                "--title",
                title,
                "--body",
                body,
                "--head",
                head,
                "--base",
                base,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            return GitOperation(success=True, message=f"Created PR: {title}", output=result.stdout)
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Error creating PR: {e.stderr}", error=e.stderr)

    @abk_common.function_trace
    def comment_on_pr(self, repo: str, pr_number: int, message: str) -> GitOperation:
        """Comment on GitHub pull request."""
        try:
            cmd = ["gh", "pr", "comment", str(pr_number), "--repo", repo, "--body", message]

            subprocess.run(cmd, capture_output=True, text=True, check=True)

            return GitOperation(success=True, message=f"Added comment to PR #{pr_number}")
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Error commenting on PR: {e.stderr}", error=e.stderr)

    @abk_common.function_trace
    def assign_to_ai(self, issue: Issue, ai_type: AiaType) -> GitOperation:
        """Assign issue to AI assistant."""
        # Remove existing AI assignment labels
        for label in issue.labels:
            if label.startswith("assigned:ai-"):
                self.remove_label_from_issue(issue, label)

        # Add new AI assignment label
        new_label = f"assigned:{ai_type.value}"
        return self.add_label_to_issue(issue, new_label)

    @abk_common.function_trace
    def get_assigned_issues(self) -> list[Issue]:
        """Get issues assigned to this AI assistant."""
        all_issues = self.get_issues()
        assigned_issues = []

        for issue in all_issues:
            if issue.get_assigned_ai() == self.aia_type.value:
                assigned_issues.append(issue)

        return assigned_issues

    @abk_common.function_trace
    def get_issues_in_column(self, column_status: WorkflowStatus) -> list[Issue]:
        """Get issues from a specific project board column."""
        return self.get_issues(status=column_status)

    @abk_common.function_trace
    def get_top_priority_todo_issue(self) -> Issue | None:
        """Get the highest priority issue from ToDo column.

        Returns:
            The first issue from ToDo column (assuming GitHub orders by priority)
        """
        todo_issues = self.get_issues_in_column(WorkflowStatus.TODO)
        if todo_issues:
            return todo_issues[0]  # First issue is highest priority
        return None

    @abk_common.function_trace
    def move_issue_to_column(self, issue: Issue, target_column: WorkflowStatus) -> GitOperation:
        """Move issue to a specific project board column.

        Args:
            issue: Issue to move
            target_column: Target column status

        Returns:
            GitOperation result
        """
        return self.update_issue_status(issue, target_column)

    @abk_common.function_trace
    def get_project_board_info(self) -> dict:
        """Get project board information including all columns and issue counts."""
        try:
            if not self.config.project_number:
                return {"error": "No project number configured"}

            # Get all issues and group by status
            all_issues = self.get_issues()
            column_counts = {}

            for status in WorkflowStatus:
                column_issues = [issue for issue in all_issues if issue.project_status == status]
                column_counts[status.value] = {
                    "count": len(column_issues),
                    "issues": [{"number": issue.number, "title": issue.title} for issue in column_issues],
                }

            return {
                "project_number": self.config.project_number,
                "repo": self.config.repo_full_name,
                "columns": column_counts,
                "total_issues": len(all_issues),
            }
        except Exception as e:
            return {"error": f"Failed to get project board info: {str(e)}"}

    @abk_common.function_trace
    def validate_project_board_setup(self) -> GitOperation:
        """Validate that the project board is properly configured."""
        try:
            if not self.config.project_number:
                return GitOperation(success=False, message="No project number configured in WorkflowConfig")

            # Test project board access
            cmd = ["gh", "project", "view", str(self.config.project_number), "--format", "json"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            project_data = json.loads(result.stdout)

            return GitOperation(
                success=True, message=f"Project board validated: {project_data.get('title', 'Unknown')}", output=result.stdout
            )

        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Project board validation failed: {e.stderr}", error=e.stderr)

    def _parse_issue_data(self, issue_data: dict) -> Issue:
        """Parse GitHub issue data into Issue object."""
        from datetime import datetime

        labels = [label["name"] for label in issue_data.get("labels", [])]
        assignees = [assignee["login"] for assignee in issue_data.get("assignees", [])]

        return Issue(
            number=issue_data["number"],
            title=issue_data["title"],
            body=issue_data.get("body", ""),
            state=issue_data["state"],
            labels=labels,
            assignees=assignees,
            created_at=datetime.fromisoformat(issue_data["createdAt"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(issue_data["updatedAt"].replace("Z", "+00:00")),
            url=issue_data["url"],
        )


# -----------------------------------------------------------------------------
# GitLab AI assistant Manager
# -----------------------------------------------------------------------------
class GitLabAiaManager(AiaManagerBase):
    """GitLab AI assistant manager (placeholder implementation)."""

    def get_issues(self, status: WorkflowStatus | None = None) -> list[Issue]:
        """GitLab implementation - not implemented yet."""
        raise NotImplementedError("GitLab implementation pending")

    def get_issue(self, issue_number: int) -> Issue | None:
        """GitLab implementation - not implemented yet."""
        raise NotImplementedError("GitLab implementation pending")

    def update_issue_status(self, issue: Issue, new_status: WorkflowStatus) -> GitOperation:
        """GitLab implementation - not implemented yet."""
        raise NotImplementedError("GitLab implementation pending")

    def add_label_to_issue(self, issue: Issue, label: str) -> GitOperation:
        """GitLab implementation - not implemented yet."""
        raise NotImplementedError("GitLab implementation pending")

    def remove_label_from_issue(self, issue: Issue, label: str) -> GitOperation:
        """GitLab implementation - not implemented yet."""
        raise NotImplementedError("GitLab implementation pending")

    def create_branch(self, issue: Issue) -> GitOperation:
        """GitLab implementation - not implemented yet."""
        raise NotImplementedError("GitLab implementation pending")

    def create_commit(self, branch: str, files: list[str], message: str) -> GitOperation:
        """GitLab implementation - not implemented yet."""
        raise NotImplementedError("GitLab implementation pending")

    def push_commit(self, branch: str, files: list[str], message: str) -> GitOperation:
        """GitLab implementation - not implemented yet."""
        raise NotImplementedError("GitLab implementation pending")

    def create_pr(self, title: str, body: str, head: str, base: str) -> GitOperation:
        """GitLab implementation - not implemented yet."""
        raise NotImplementedError("GitLab implementation pending")

    def comment_on_pr(self, repo: str, pr_number: int, message: str) -> GitOperation:
        """GitLab implementation - not implemented yet."""
        raise NotImplementedError("GitLab implementation pending")

    def assign_to_ai(self, issue: Issue, ai_type: AiaType) -> GitOperation:
        """GitLab implementation - not implemented yet."""
        raise NotImplementedError("GitLab implementation pending")

    def get_assigned_issues(self) -> list[Issue]:
        """GitLab implementation - not implemented yet."""
        raise NotImplementedError("GitLab implementation pending")


# -----------------------------------------------------------------------------
# Bitbucket AI assistant Manager
# -----------------------------------------------------------------------------
class BitbucketAiaManager(AiaManagerBase):
    """Bitbucket AI assistant manager (placeholder implementation)."""

    def get_issues(self, status: WorkflowStatus | None = None) -> list[Issue]:
        """Bitbucket implementation - not implemented yet."""
        raise NotImplementedError("Bitbucket implementation pending")

    def get_issue(self, issue_number: int) -> Issue | None:
        """Bitbucket implementation - not implemented yet."""
        raise NotImplementedError("Bitbucket implementation pending")

    def update_issue_status(self, issue: Issue, new_status: WorkflowStatus) -> GitOperation:
        """Bitbucket implementation - not implemented yet."""
        raise NotImplementedError("Bitbucket implementation pending")

    def add_label_to_issue(self, issue: Issue, label: str) -> GitOperation:
        """Bitbucket implementation - not implemented yet."""
        raise NotImplementedError("Bitbucket implementation pending")

    def remove_label_from_issue(self, issue: Issue, label: str) -> GitOperation:
        """Bitbucket implementation - not implemented yet."""
        raise NotImplementedError("Bitbucket implementation pending")

    def create_branch(self, issue: Issue) -> GitOperation:
        """Bitbucket implementation - not implemented yet."""
        raise NotImplementedError("Bitbucket implementation pending")

    def create_commit(self, branch: str, files: list[str], message: str) -> GitOperation:
        """Bitbucket implementation - not implemented yet."""
        raise NotImplementedError("Bitbucket implementation pending")

    def push_commit(self, branch: str, files: list[str], message: str) -> GitOperation:
        """Bitbucket implementation - not implemented yet."""
        raise NotImplementedError("Bitbucket implementation pending")

    def create_pr(self, title: str, body: str, head: str, base: str) -> GitOperation:
        """Bitbucket implementation - not implemented yet."""
        raise NotImplementedError("Bitbucket implementation pending")

    def comment_on_pr(self, repo: str, pr_number: int, message: str) -> GitOperation:
        """Bitbucket implementation - not implemented yet."""
        raise NotImplementedError("Bitbucket implementation pending")

    def assign_to_ai(self, issue: Issue, ai_type: AiaType) -> GitOperation:
        """Bitbucket implementation - not implemented yet."""
        raise NotImplementedError("Bitbucket implementation pending")

    def get_assigned_issues(self) -> list[Issue]:
        """Bitbucket implementation - not implemented yet."""
        raise NotImplementedError("Bitbucket implementation pending")


# -----------------------------------------------------------------------------
# Manager Factory
# -----------------------------------------------------------------------------
class AiaManagerFactory:
    """Factory for creating AI assistant managers.

    Supports: "github", "gitlab", "bitbucket"
    """

    @staticmethod
    def create_manager(provider: str, aia_type: AiaType, config: WorkflowConfig) -> AiaManagerBase:
        """Create manager for specified Git provider.

        Args:
            provider: Git provider ("github", "gitlab", "bitbucket")
            aia_type: AI assistant type
            config: Workflow configuration

        Returns:
            Manager instance for the provider

        Raises:
            ValueError: If provider is not supported
        """
        match provider.lower():
            case "github":
                return GitHubAiaManager(aia_type, config)
            case "gitlab":
                return GitLabAiaManager(aia_type, config)
            case "bitbucket":
                return BitbucketAiaManager(aia_type, config)
            case _:
                raise ValueError(f"Unsupported Git provider: {provider}")
