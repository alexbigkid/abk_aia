"""Unit tests for git_aia_manager module."""

import pytest
from unittest.mock import Mock, patch
import json
import subprocess

from abk_aia.git_aia_manager import GitBranchType, AiaType, AiaManagerBase, GitHubAiaManager, AiaManagerFactory
from abk_aia.models import Issue, WorkflowStatus, GitOperation, IssueState, WorkflowConfig


class TestGitBranchType:
    """Test GitBranchType enum."""

    def test_branch_type_values(self):
        """Test branch type enum values."""
        assert GitBranchType.BUG.value == "B"
        assert GitBranchType.DOCUMENTATION.value == "D"
        assert GitBranchType.FEATURE.value == "F"
        assert GitBranchType.RESEARCH.value == "R"
        assert GitBranchType.TEST.value == "T"


class TestAiaType:
    """Test AiaType enum."""

    def test_aia_type_values(self):
        """Test AI assistant type enum values."""
        assert AiaType.AI_CODER.value == "ai-coder"
        assert AiaType.AI_MARKETEER.value == "ai-marketeer"
        assert AiaType.AI_REVIEWER.value == "ai-reviewer"
        assert AiaType.AI_RESEARCHER.value == "ai-researcher"
        assert AiaType.AI_TESTER.value == "ai-tester"


class TestAiaManagerBase:
    """Test AiaManagerBase abstract class."""

    def test_init(self, sample_config):
        """Test manager initialization."""

        # Create a concrete implementation for testing
        class TestManager(AiaManagerBase):
            def get_issues(self, status=None):
                return []

            def get_issue(self, issue_number):
                return None

            def update_issue_status(self, issue, new_status):
                return GitOperation(True, "")

            def add_label_to_issue(self, issue, label):
                return GitOperation(True, "")

            def remove_label_from_issue(self, issue, label):
                return GitOperation(True, "")

            def create_branch(self, issue):
                return GitOperation(True, "")

            def create_commit(self, branch, files, message):
                return GitOperation(True, "")

            def push_commit(self, branch, files, message):
                return GitOperation(True, "")

            def create_pr(self, title, body, head, base):
                return GitOperation(True, "")

            def comment_on_pr(self, repo, pr_number, message):
                return GitOperation(True, "")

            def assign_to_ai(self, issue, ai_type):
                return GitOperation(True, "")

            def get_assigned_issues(self):
                return []

        manager = TestManager(AiaType.AI_CODER, sample_config)
        assert manager.aia_type == AiaType.AI_CODER
        assert manager.config == sample_config

    def test_generate_branch_name(self, sample_config, sample_issue):
        """Test branch name generation."""

        class TestManager(AiaManagerBase):
            def get_issues(self, status=None):
                return []

            def get_issue(self, issue_number):
                return None

            def update_issue_status(self, issue, new_status):
                return GitOperation(True, "")

            def add_label_to_issue(self, issue, label):
                return GitOperation(True, "")

            def remove_label_from_issue(self, issue, label):
                return GitOperation(True, "")

            def create_branch(self, issue):
                return GitOperation(True, "")

            def create_commit(self, branch, files, message):
                return GitOperation(True, "")

            def push_commit(self, branch, files, message):
                return GitOperation(True, "")

            def create_pr(self, title, body, head, base):
                return GitOperation(True, "")

            def comment_on_pr(self, repo, pr_number, message):
                return GitOperation(True, "")

            def assign_to_ai(self, issue, ai_type):
                return GitOperation(True, "")

            def get_assigned_issues(self):
                return []

        manager = TestManager(AiaType.AI_CODER, sample_config)
        branch_name = manager.generate_branch_name(sample_issue)
        assert branch_name == "F/123/test-issue-title"

    def test_get_branch_type_from_labels_feature(self, sample_config):
        """Test branch type detection for feature labels."""

        class TestManager(AiaManagerBase):
            def get_issues(self, status=None):
                return []

            def get_issue(self, issue_number):
                return None

            def update_issue_status(self, issue, new_status):
                return GitOperation(True, "")

            def add_label_to_issue(self, issue, label):
                return GitOperation(True, "")

            def remove_label_from_issue(self, issue, label):
                return GitOperation(True, "")

            def create_branch(self, issue):
                return GitOperation(True, "")

            def create_commit(self, branch, files, message):
                return GitOperation(True, "")

            def push_commit(self, branch, files, message):
                return GitOperation(True, "")

            def create_pr(self, title, body, head, base):
                return GitOperation(True, "")

            def comment_on_pr(self, repo, pr_number, message):
                return GitOperation(True, "")

            def assign_to_ai(self, issue, ai_type):
                return GitOperation(True, "")

            def get_assigned_issues(self):
                return []

        manager = TestManager(AiaType.AI_CODER, sample_config)

        # Test different label types
        assert manager._get_branch_type_from_labels(["feature"]) == GitBranchType.FEATURE
        assert manager._get_branch_type_from_labels(["bug"]) == GitBranchType.BUG
        assert manager._get_branch_type_from_labels(["documentation"]) == GitBranchType.DOCUMENTATION
        assert manager._get_branch_type_from_labels(["research"]) == GitBranchType.RESEARCH
        assert manager._get_branch_type_from_labels(["test"]) == GitBranchType.TEST

        # Test default fallback
        assert manager._get_branch_type_from_labels(["priority:high"]) == GitBranchType.FEATURE

        # Test with multiple labels including type label
        assert manager._get_branch_type_from_labels(["bug", "priority:high", "assigned:ai-coder"]) == GitBranchType.BUG


class TestGitHubAiaManager:
    """Test GitHubAiaManager implementation."""

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_get_issues_success(self, mock_run, sample_config):
        """Test successful get_issues call."""
        # Mock successful subprocess response
        mock_result = Mock()
        mock_result.stdout = json.dumps(
            [
                {
                    "number": 123,
                    "title": "Test issue",
                    "body": "Test body",
                    "state": "open",
                    "labels": [{"name": "feature"}],
                    "assignees": [],
                    "createdAt": "2025-01-01T12:00:00Z",
                    "updatedAt": "2025-01-01T12:30:00Z",
                    "url": "https://github.com/test/repo/issues/123",
                }
            ]
        )
        mock_run.return_value = mock_result

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        issues = manager.get_issues()

        assert len(issues) == 1
        assert issues[0].number == 123
        assert issues[0].title == "Test issue"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_get_issues_failure(self, mock_run, sample_config):
        """Test get_issues with subprocess failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="Error")

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        issues = manager.get_issues()

        assert issues == []

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_get_issue_success(self, mock_run, sample_config):
        """Test successful get_issue call."""
        mock_result = Mock()
        mock_result.stdout = json.dumps(
            {
                "number": 123,
                "title": "Test issue",
                "body": "Test body",
                "state": "open",
                "labels": [{"name": "feature"}],
                "assignees": [],
                "createdAt": "2025-01-01T12:00:00Z",
                "updatedAt": "2025-01-01T12:30:00Z",
                "url": "https://github.com/test/repo/issues/123",
            }
        )
        mock_run.return_value = mock_result

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        issue = manager.get_issue(123)

        assert issue is not None
        assert issue.number == 123
        assert issue.title == "Test issue"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_update_issue_status_success(self, mock_run, sample_config, sample_issue):
        """Test successful issue status update."""
        mock_result = Mock()
        mock_run.return_value = mock_result

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.update_issue_status(sample_issue, WorkflowStatus.DOING)

        assert result.success is True
        assert "Updated issue 123 status" in result.message

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_add_label_success(self, mock_run, sample_config, sample_issue):
        """Test successful label addition."""
        mock_result = Mock()
        mock_run.return_value = mock_result

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.add_label_to_issue(sample_issue, "priority:high")

        assert result.success is True
        assert "Added label 'priority:high'" in result.message

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_create_branch_success(self, mock_run, sample_config, sample_issue):
        """Test successful branch creation."""
        mock_result = Mock()
        mock_run.return_value = mock_result

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.create_branch(sample_issue)

        assert result.success is True
        assert "Created branch" in result.message
        assert result.output == "F/123/test-issue-title"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_create_commit_success(self, mock_run, sample_config):
        """Test successful commit creation."""
        mock_result = Mock()
        mock_result.stdout = "Commit created successfully"
        mock_run.return_value = mock_result

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.create_commit("feature-branch", ["file1.py", "file2.py"], "Add new features")

        assert result.success is True
        assert "Created commit on branch 'feature-branch'" in result.message
        assert result.output == "Commit created successfully"

        # Should call git add for each file, then git commit
        assert mock_run.call_count == 3  # 2 git add calls + 1 git commit call

        # Verify git add calls
        add_calls = mock_run.call_args_list[:2]
        assert add_calls[0][0][0] == ["git", "add", "file1.py"]
        assert add_calls[1][0][0] == ["git", "add", "file2.py"]

        # Verify git commit call
        commit_call = mock_run.call_args_list[2]
        assert commit_call[0][0] == ["git", "commit", "-m", "Add new features"]

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_create_commit_single_file(self, mock_run, sample_config):
        """Test commit creation with single file."""
        mock_result = Mock()
        mock_result.stdout = "Single file committed"
        mock_run.return_value = mock_result

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.create_commit("bugfix-branch", ["README.md"], "Update documentation")

        assert result.success is True
        assert "Created commit on branch 'bugfix-branch'" in result.message
        assert result.output == "Single file committed"

        # Should call git add once, then git commit
        assert mock_run.call_count == 2

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_create_commit_add_file_error(self, mock_run, sample_config):
        """Test create_commit when git add fails."""
        # First git add call fails
        mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr="File not found")

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.create_commit("test-branch", ["nonexistent.py"], "Test commit")

        assert result.success is False
        assert "Error creating commit" in result.message
        assert result.error == "File not found"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_create_commit_commit_error(self, mock_run, sample_config):
        """Test create_commit when git commit fails."""

        def side_effect(*args, **kwargs):
            cmd = args[0]
            if cmd[0:2] == ["git", "add"]:
                # git add succeeds
                return Mock()
            elif cmd[0:2] == ["git", "commit"]:
                # git commit fails
                raise subprocess.CalledProcessError(1, "git", stderr="Nothing to commit")

        mock_run.side_effect = side_effect

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.create_commit("test-branch", ["file.py"], "Empty commit")

        assert result.success is False
        assert "Error creating commit" in result.message
        assert result.error == "Nothing to commit"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_assign_to_ai(self, mock_run, sample_config):
        """Test AI assignment with label management."""
        from datetime import datetime

        mock_result = Mock()
        mock_run.return_value = mock_result

        # Create issue with existing AI assignment
        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-researcher", "feature"],
            assignees=[],
            created_at=datetime(2025, 1, 1),
            updated_at=datetime(2025, 1, 1),
            url="test-url",
        )

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.assign_to_ai(issue, AiaType.AI_CODER)

        # Should call subprocess twice: remove old label, add new label
        assert mock_run.call_count == 2
        assert result.success is True

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_get_assigned_issues_success(self, mock_run, sample_config):
        """Test getting issues assigned to specific AI type."""
        # Mock successful subprocess response with mixed assignments
        mock_result = Mock()
        mock_result.stdout = json.dumps(
            [
                {
                    "number": 123,
                    "title": "Assigned to ai-coder",
                    "body": "Test body",
                    "state": "open",
                    "labels": [{"name": "assigned:ai-coder"}, {"name": "feature"}],
                    "assignees": [],
                    "createdAt": "2025-01-01T12:00:00Z",
                    "updatedAt": "2025-01-01T12:30:00Z",
                    "url": "https://github.com/test/repo/issues/123",
                },
                {
                    "number": 124,
                    "title": "Assigned to ai-reviewer",
                    "body": "Test body",
                    "state": "open",
                    "labels": [{"name": "assigned:ai-reviewer"}, {"name": "bug"}],
                    "assignees": [],
                    "createdAt": "2025-01-01T12:00:00Z",
                    "updatedAt": "2025-01-01T12:30:00Z",
                    "url": "https://github.com/test/repo/issues/124",
                },
                {
                    "number": 125,
                    "title": "Unassigned issue",
                    "body": "Test body",
                    "state": "open",
                    "labels": [{"name": "feature"}],
                    "assignees": [],
                    "createdAt": "2025-01-01T12:00:00Z",
                    "updatedAt": "2025-01-01T12:30:00Z",
                    "url": "https://github.com/test/repo/issues/125",
                },
            ]
        )
        mock_run.return_value = mock_result

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        assigned_issues = manager.get_assigned_issues()

        # Should only return issues assigned to ai-coder
        assert len(assigned_issues) == 1
        assert assigned_issues[0].number == 123
        assert assigned_issues[0].title == "Assigned to ai-coder"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_get_assigned_issues_none_assigned(self, mock_run, sample_config):
        """Test getting assigned issues when none are assigned to this AI type."""
        mock_result = Mock()
        mock_result.stdout = json.dumps(
            [
                {
                    "number": 124,
                    "title": "Assigned to different AI",
                    "body": "Test body",
                    "state": "open",
                    "labels": [{"name": "assigned:ai-reviewer"}, {"name": "bug"}],
                    "assignees": [],
                    "createdAt": "2025-01-01T12:00:00Z",
                    "updatedAt": "2025-01-01T12:30:00Z",
                    "url": "https://github.com/test/repo/issues/124",
                }
            ]
        )
        mock_run.return_value = mock_result

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        assigned_issues = manager.get_assigned_issues()

        assert len(assigned_issues) == 0

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_get_assigned_issues_failure(self, mock_run, sample_config):
        """Test get_assigned_issues when get_issues fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="API Error")

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        assigned_issues = manager.get_assigned_issues()

        # Should return empty list when get_issues fails
        assert assigned_issues == []


class TestAiaManagerFactory:
    """Test AiaManagerFactory."""

    def test_create_github_manager(self, sample_config):
        """Test creating GitHub manager."""
        manager = AiaManagerFactory.create_manager("github", AiaType.AI_CODER, sample_config)
        assert isinstance(manager, GitHubAiaManager)
        assert manager.aia_type == AiaType.AI_CODER

    def test_create_gitlab_manager(self, sample_config):
        """Test creating GitLab manager (placeholder)."""
        manager = AiaManagerFactory.create_manager("gitlab", AiaType.AI_CODER, sample_config)
        assert manager.__class__.__name__ == "GitLabAiaManager"

    def test_create_bitbucket_manager(self, sample_config):
        """Test creating Bitbucket manager (placeholder)."""
        manager = AiaManagerFactory.create_manager("bitbucket", AiaType.AI_CODER, sample_config)
        assert manager.__class__.__name__ == "BitbucketAiaManager"

    def test_unsupported_provider(self, sample_config):
        """Test error for unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported Git provider"):
            AiaManagerFactory.create_manager("unsupported", AiaType.AI_CODER, sample_config)


class TestGitHubAiaManagerErrorHandling:
    """Test error handling in GitHubAiaManager."""

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_update_issue_status_no_project_number(self, mock_run, sample_issue):
        """Test update_issue_status when no project number configured."""
        config = WorkflowConfig(repo_owner="test", repo_name="repo")  # No project_number
        manager = GitHubAiaManager(AiaType.AI_CODER, config)

        result = manager.update_issue_status(sample_issue, WorkflowStatus.DOING)

        assert result.success is False
        assert "No project number configured" in result.message
        mock_run.assert_not_called()

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_update_issue_status_subprocess_error(self, mock_run, sample_config, sample_issue):
        """Test update_issue_status with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="API Error")

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.update_issue_status(sample_issue, WorkflowStatus.DOING)

        assert result.success is False
        assert "Error updating issue status" in result.message
        assert result.error == "API Error"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_add_label_subprocess_error(self, mock_run, sample_config, sample_issue):
        """Test add_label_to_issue with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="Label error")

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.add_label_to_issue(sample_issue, "test-label")

        assert result.success is False
        assert "Error adding label" in result.message
        assert result.error == "Label error"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_remove_label_subprocess_error(self, mock_run, sample_config, sample_issue):
        """Test remove_label_from_issue with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="Remove error")

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.remove_label_from_issue(sample_issue, "test-label")

        assert result.success is False
        assert "Error removing label" in result.message
        assert result.error == "Remove error"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_create_branch_subprocess_error(self, mock_run, sample_config, sample_issue):
        """Test create_branch with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr="Branch exists")

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.create_branch(sample_issue)

        assert result.success is False
        assert "Error creating branch" in result.message
        assert result.error == "Branch exists"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_create_commit_subprocess_error(self, mock_run, sample_config):
        """Test create_commit with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr="Commit failed")

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.create_commit("test-branch", ["file.py"], "Test commit")

        assert result.success is False
        assert "Error creating commit" in result.message
        assert result.error == "Commit failed"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_push_commit_subprocess_error(self, mock_run, sample_config):
        """Test push_commit with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr="Push failed")

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.push_commit("test-branch", ["file.py"], "Test commit")

        assert result.success is False
        assert "Error pushing branch" in result.message
        assert result.error == "Push failed"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_create_pr_subprocess_error(self, mock_run, sample_config):
        """Test create_pr with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="PR failed")

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.create_pr("Test PR", "Description", "feature", "main")

        assert result.success is False
        assert "Error creating PR" in result.message
        assert result.error == "PR failed"

    @patch("abk_aia.git_aia_manager.subprocess.run")
    def test_comment_on_pr_subprocess_error(self, mock_run, sample_config):
        """Test comment_on_pr with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="Comment failed")

        manager = GitHubAiaManager(AiaType.AI_CODER, sample_config)
        result = manager.comment_on_pr("owner/repo", 123, "Test comment")

        assert result.success is False
        assert "Error commenting on PR" in result.message
        assert result.error == "Comment failed"


class TestPlaceholderManagerMethods:
    """Test placeholder manager implementations."""

    def test_gitlab_manager_methods(self, sample_config):
        """Test GitLab manager placeholder methods."""
        from abk_aia.git_aia_manager import GitLabAiaManager

        manager = GitLabAiaManager(AiaType.AI_CODER, sample_config)

        with pytest.raises(NotImplementedError, match="GitLab implementation pending"):
            manager.get_issues()

        with pytest.raises(NotImplementedError, match="GitLab implementation pending"):
            manager.get_issue(123)

        with pytest.raises(NotImplementedError, match="GitLab implementation pending"):
            manager.update_issue_status(None, WorkflowStatus.DOING)

    def test_bitbucket_manager_methods(self, sample_config):
        """Test Bitbucket manager placeholder methods."""
        from abk_aia.git_aia_manager import BitbucketAiaManager

        manager = BitbucketAiaManager(AiaType.AI_CODER, sample_config)

        with pytest.raises(NotImplementedError, match="Bitbucket implementation pending"):
            manager.get_issues()

        with pytest.raises(NotImplementedError, match="Bitbucket implementation pending"):
            manager.get_issue(123)

        with pytest.raises(NotImplementedError, match="Bitbucket implementation pending"):
            manager.update_issue_status(None, WorkflowStatus.DOING)
