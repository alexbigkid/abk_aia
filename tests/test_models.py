"""Unit tests for models module."""

from datetime import datetime

from aia.models import Issue, IssueState, WorkflowConfig, WorkflowStatus, GitOperation, PullRequest, PullRequestState


class TestIssue:
    """Test Issue model."""

    def test_issue_creation(self, sample_issue):
        """Test creating an Issue instance."""
        assert sample_issue.number == 123
        assert sample_issue.title == "Test issue title"
        assert sample_issue.state == IssueState.OPEN
        assert "feature" in sample_issue.labels

    def test_get_short_name(self, sample_issue):
        """Test generating short name from title."""
        short_name = sample_issue.get_short_name()
        assert short_name == "test-issue-title"

    def test_get_short_name_with_special_chars(self):
        """Test short name generation with special characters."""
        issue = Issue(
            number=1,
            title="Fix: User Auth & Session Management!",
            body="",
            state=IssueState.OPEN,
            labels=[],
            assignees=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            url="",
        )
        short_name = issue.get_short_name()
        assert short_name == "fix-user-auth--session-managem"

    def test_has_label(self, sample_issue):
        """Test checking if issue has specific label."""
        assert sample_issue.has_label("feature") is True
        assert sample_issue.has_label("bug") is False

    def test_is_assigned_to_ai_false(self, sample_issue):
        """Test AI assignment check when not assigned."""
        assert sample_issue.is_assigned_to_ai() is False

    def test_is_assigned_to_ai_true(self):
        """Test AI assignment check when assigned."""
        issue = Issue(
            number=1,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-coder", "feature"],
            assignees=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            url="",
        )
        assert issue.is_assigned_to_ai() is True

    def test_get_assigned_ai(self):
        """Test getting assigned AI type."""
        issue = Issue(
            number=1,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-reviewer", "feature"],
            assignees=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            url="",
        )
        assert issue.get_assigned_ai() == "ai-reviewer"

    def test_get_assigned_ai_none(self, sample_issue):
        """Test getting assigned AI when none assigned."""
        assert sample_issue.get_assigned_ai() is None


class TestWorkflowConfig:
    """Test WorkflowConfig model."""

    def test_config_creation(self, sample_config):
        """Test creating WorkflowConfig instance."""
        assert sample_config.repo_owner == "test-owner"
        assert sample_config.repo_name == "test-repo"
        assert sample_config.project_number == 1
        assert sample_config.default_base_branch == "main"

    def test_repo_full_name(self, sample_config):
        """Test repo full name property."""
        assert sample_config.repo_full_name == "test-owner/test-repo"

    def test_config_defaults(self):
        """Test default values in config."""
        config = WorkflowConfig(repo_owner="owner", repo_name="repo")
        assert config.project_number is None
        assert config.default_base_branch == "main"


class TestGitOperation:
    """Test GitOperation model."""

    def test_successful_operation(self):
        """Test successful git operation."""
        op = GitOperation(success=True, message="Operation completed")
        assert op.success is True
        assert op.message == "Operation completed"
        assert op.output is None
        assert op.error is None

    def test_failed_operation(self):
        """Test failed git operation."""
        op = GitOperation(success=False, message="Operation failed", error="Command not found")
        assert op.success is False
        assert op.message == "Operation failed"
        assert op.error == "Command not found"

    def test_operation_with_output(self):
        """Test git operation with output."""
        op = GitOperation(success=True, message="Branch created", output="feature/123/new-feature")
        assert op.success is True
        assert op.output == "feature/123/new-feature"


class TestPullRequest:
    """Test PullRequest model."""

    def test_pr_creation(self):
        """Test creating PullRequest instance."""
        pr = PullRequest(
            number=42,
            title="Test PR",
            body="PR description",
            state=PullRequestState.OPEN,
            head_branch="feature/123/test",
            base_branch="main",
            labels=["feature"],
            assignees=["dev"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            url="https://github.com/owner/repo/pull/42",
            mergeable=True,
            draft=False,
        )
        assert pr.number == 42
        assert pr.title == "Test PR"
        assert pr.state == PullRequestState.OPEN

    def test_is_ready_for_review_true(self):
        """Test PR ready for review when open and not draft."""
        pr = PullRequest(
            number=1,
            title="Test",
            body="",
            state=PullRequestState.OPEN,
            head_branch="feature",
            base_branch="main",
            labels=[],
            assignees=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            url="",
            mergeable=True,
            draft=False,
        )
        assert pr.is_ready_for_review() is True

    def test_is_ready_for_review_false_draft(self):
        """Test PR not ready when it's a draft."""
        pr = PullRequest(
            number=1,
            title="Test",
            body="",
            state=PullRequestState.OPEN,
            head_branch="feature",
            base_branch="main",
            labels=[],
            assignees=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            url="",
            mergeable=True,
            draft=True,
        )
        assert pr.is_ready_for_review() is False


class TestEnums:
    """Test enum values."""

    def test_workflow_status_values(self):
        """Test workflow status enum values."""
        assert WorkflowStatus.TODO.value == "📋 ToDo"
        assert WorkflowStatus.DOING.value == "🔄 Doing"
        assert WorkflowStatus.REVIEW.value == "👀 Review"
        assert WorkflowStatus.TESTING.value == "🧪 Testing"
        assert WorkflowStatus.DONE.value == "✅ Done"

    def test_issue_state_values(self):
        """Test issue state enum values."""
        assert IssueState.OPEN.value == "open"
        assert IssueState.CLOSED.value == "closed"

    def test_pr_state_values(self):
        """Test pull request state enum values."""
        assert PullRequestState.OPEN.value == "open"
        assert PullRequestState.CLOSED.value == "closed"
        assert PullRequestState.MERGED.value == "merged"
