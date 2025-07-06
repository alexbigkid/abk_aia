"""Data models for AI assistant Git workflow."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class IssueState(Enum):
    """GitHub issue state."""

    OPEN = "open"
    CLOSED = "closed"


class WorkflowStatus(Enum):
    """Kanban workflow status."""

    TODO = "📋 ToDo"
    DOING = "🔄 Doing"
    REVIEW = "👀 Review"
    TESTING = "🧪 Testing"
    DONE = "✅ Done"


class PullRequestState(Enum):
    """GitHub pull request state."""

    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


@dataclass
class Issue:
    """GitHub issue representation."""

    number: int
    title: str
    body: str
    state: IssueState
    labels: list[str]
    assignees: list[str]
    created_at: datetime
    updated_at: datetime
    url: str
    project_status: WorkflowStatus | None = None

    def get_short_name(self) -> str:
        """Generate short name for branch naming from issue title."""
        # Remove special characters and convert to lowercase
        short_name = "".join(c for c in self.title if c.isalnum() or c.isspace())
        # Replace spaces with hyphens and limit length
        short_name = short_name.replace(" ", "-").lower()
        # Limit to 30 characters
        if len(short_name) > 30:
            short_name = short_name[:30].rstrip("-")
        return short_name

    def has_label(self, label: str) -> bool:
        """Check if issue has a specific label."""
        return label in self.labels

    def is_assigned_to_ai(self) -> bool:
        """Check if issue is assigned to any AI assistant."""
        return any(label.startswith("assigned:ai-") for label in self.labels)

    def get_assigned_ai(self) -> str | None:
        """Get the AI assistant assigned to this issue."""
        for label in self.labels:
            if label.startswith("assigned:ai-"):
                return label.split(":", 1)[1]
        return None


@dataclass
class PullRequest:
    """GitHub pull request representation."""

    number: int
    title: str
    body: str
    state: PullRequestState
    head_branch: str
    base_branch: str
    labels: list[str]
    assignees: list[str]
    created_at: datetime
    updated_at: datetime
    url: str
    mergeable: bool
    draft: bool

    def is_ready_for_review(self) -> bool:
        """Check if PR is ready for review."""
        return not self.draft and self.state == PullRequestState.OPEN


@dataclass
class WorkflowConfig:
    """Configuration for AI assistant workflow."""

    repo_owner: str
    repo_name: str
    project_number: int | None = None
    default_base_branch: str = "main"

    @property
    def repo_full_name(self) -> str:
        """Get full repository name."""
        return f"{self.repo_owner}/{self.repo_name}"


@dataclass
class GitOperation:
    """Represents a Git operation result."""

    success: bool
    message: str
    output: str | None = None
    error: str | None = None
