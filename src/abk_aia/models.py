"""Data models for AI assistant Git workflow.

Defines data structures for issues, pull requests, workflow configuration,
and Git operations used throughout the AI assistant workflow system.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class IssueState(Enum):
    """GitHub issue state enumeration."""

    OPEN = "open"
    CLOSED = "closed"


class WorkflowStatus(Enum):
    """Kanban workflow status enumeration.
    
    Defines the workflow states: ToDo → Doing → Review → Testing → Done
    """

    TODO = "📋 ToDo"
    DOING = "🔄 Doing"
    REVIEW = "👀 Review"
    TESTING = "🧪 Testing"
    DONE = "✅ Done"


class PullRequestState(Enum):
    """GitHub pull request state enumeration."""

    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


@dataclass
class Issue:
    """GitHub issue data model.
    
    Attributes:
        number: Issue number
        title: Issue title
        body: Issue description
        state: Issue state (open/closed)
        labels: List of label strings
        assignees: List of assignee usernames
        created_at: Creation timestamp
        updated_at: Last update timestamp
        url: Issue URL
        project_status: Optional workflow status
    """

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
        """Generate short name for branch naming from issue title.
        
        Returns:
            Lowercase, hyphenated name limited to 30 characters
        """
        # Remove special characters and convert to lowercase
        short_name = "".join(c for c in self.title if c.isalnum() or c.isspace())
        # Replace spaces with hyphens and limit length
        short_name = short_name.replace(" ", "-").lower()
        # Limit to 30 characters
        if len(short_name) > 30:
            short_name = short_name[:30].rstrip("-")
        return short_name

    def has_label(self, label: str) -> bool:
        """Check if issue has a specific label.
        
        Args:
            label: Label string to check for
            
        Returns:
            True if label is present
        """
        return label in self.labels

    def is_assigned_to_ai(self) -> bool:
        """Check if issue is assigned to any AI assistant.
        
        Returns:
            True if issue has any "assigned:ai-*" label
        """
        return any(label.startswith("assigned:ai-") for label in self.labels)

    def get_assigned_ai(self) -> str | None:
        """Get the AI assistant assigned to this issue.
        
        Returns:
            AI assistant type string (e.g., "ai-coder") or None
        """
        for label in self.labels:
            if label.startswith("assigned:ai-"):
                return label.split(":", 1)[1]
        return None


@dataclass
class PullRequest:
    """GitHub pull request data model.
    
    Attributes:
        number: PR number
        title: PR title
        body: PR description
        state: PR state (open/closed/merged)
        head_branch: Source branch
        base_branch: Target branch
        labels: List of label strings
        assignees: List of assignee usernames
        created_at: Creation timestamp
        updated_at: Last update timestamp
        url: PR URL
        mergeable: Whether PR can be merged
        draft: Whether PR is in draft state
    """

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
        """Check if PR is ready for review.
        
        Returns:
            True if PR is open and not a draft
        """
        return not self.draft and self.state == PullRequestState.OPEN


@dataclass
class WorkflowConfig:
    """Configuration for AI assistant workflow.
    
    Attributes:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        project_number: Optional GitHub project number
        default_base_branch: Default base branch for PRs
    """

    repo_owner: str
    repo_name: str
    project_number: int | None = None
    default_base_branch: str = "main"

    @property
    def repo_full_name(self) -> str:
        """Get full repository name.
        
        Returns:
            Repository name in "owner/repo" format
        """
        return f"{self.repo_owner}/{self.repo_name}"


@dataclass
class GitOperation:
    """Git operation result data model.
    
    Attributes:
        success: Whether operation succeeded
        message: Result message
        output: Optional output data
        error: Optional error message
    """

    success: bool
    message: str
    output: str | None = None
    error: str | None = None
