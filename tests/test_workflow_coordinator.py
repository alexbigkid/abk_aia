"""Unit tests for workflow_coordinator module."""

from unittest.mock import Mock, patch
import logging

from aia.workflow_coordinator import WorkflowCoordinator
from aia.git_aia_manager import AiaType
from aia.models import Issue, WorkflowStatus, GitOperation, IssueState


class TestWorkflowCoordinator:
    """Test WorkflowCoordinator class."""

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_init(self, mock_factory, sample_config):
        """Test WorkflowCoordinator initialization."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        coordinator = WorkflowCoordinator(sample_config, "github")

        assert coordinator.provider == "github"
        assert coordinator.config == sample_config
        assert isinstance(coordinator.logger, logging.Logger)

        # Should create managers for all AI types
        assert mock_factory.create_manager.call_count == len(AiaType)

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_get_manager(self, mock_factory, sample_config):
        """Test getting specific manager."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        coordinator = WorkflowCoordinator(sample_config, "github")
        manager = coordinator.get_manager(AiaType.AI_CODER)

        assert manager == mock_manager

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_start_coder_workflow_success(self, mock_factory, sample_config, sample_issue):
        """Test successful coder workflow start."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        # Mock manager methods
        mock_manager.get_issue.return_value = sample_issue
        mock_manager.update_issue_status.return_value = GitOperation(True, "Status updated")
        mock_manager.assign_to_ai.return_value = GitOperation(True, "Assigned")
        mock_manager.create_branch.return_value = GitOperation(True, "Branch created", "F/123/test-branch")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.start_coder_workflow(123)

        assert result.success is True
        assert "Started coder workflow" in result.message
        assert result.output == "F/123/test-branch"

        # Verify method calls
        mock_manager.get_issue.assert_called_once_with(123)
        mock_manager.update_issue_status.assert_called_once_with(sample_issue, WorkflowStatus.DOING)
        mock_manager.assign_to_ai.assert_called_once_with(sample_issue, AiaType.AI_CODER)
        mock_manager.create_branch.assert_called_once_with(sample_issue)

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_start_coder_workflow_issue_not_found(self, mock_factory, sample_config):
        """Test coder workflow start when issue not found."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager
        mock_manager.get_issue.return_value = None

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.start_coder_workflow(999)

        assert result.success is False
        assert "Issue 999 not found" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_start_coder_workflow_wrong_status(self, mock_factory, sample_config):
        """Test coder workflow start when issue not in ToDo status."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        # Create issue in wrong status
        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=[],
            assignees=[],
            created_at=sample_config.created_at if hasattr(sample_config, "created_at") else None,
            updated_at=sample_config.updated_at if hasattr(sample_config, "updated_at") else None,
            url="",
            project_status=WorkflowStatus.DOING,  # Wrong status
        )
        mock_manager.get_issue.return_value = issue

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.start_coder_workflow(123)

        assert result.success is False
        assert "not in ToDo status" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_coder_workflow_success(self, mock_factory, sample_config):
        """Test successful coder workflow completion."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        # Create issue assigned to ai-coder
        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-coder"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue
        mock_manager.update_issue_status.return_value = GitOperation(True, "Status updated")
        mock_manager.assign_to_ai.return_value = GitOperation(True, "Assigned to reviewer")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_coder_workflow(123)

        assert result.success is True
        assert "Completed coder workflow" in result.message

        # Verify transitions
        mock_manager.update_issue_status.assert_called_once_with(issue, WorkflowStatus.REVIEW)
        mock_manager.assign_to_ai.assert_called_once_with(issue, AiaType.AI_REVIEWER)

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_reviewer_workflow_success(self, mock_factory, sample_config):
        """Test successful reviewer workflow completion."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        # Create issue assigned to ai-reviewer
        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-reviewer"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue
        mock_manager.update_issue_status.return_value = GitOperation(True, "Status updated")
        mock_manager.assign_to_ai.return_value = GitOperation(True, "Assigned to tester")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_reviewer_workflow(123)

        assert result.success is True
        assert "Completed reviewer workflow" in result.message

        # Verify transitions
        mock_manager.update_issue_status.assert_called_once_with(issue, WorkflowStatus.TESTING)
        mock_manager.assign_to_ai.assert_called_once_with(issue, AiaType.AI_TESTER)

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_tester_workflow_success(self, mock_factory, sample_config):
        """Test successful tester workflow completion."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        # Create issue assigned to ai-tester
        issue = Issue(
            number=123,
            title="Test issue",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-tester", "feature"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue
        mock_manager.generate_branch_name.return_value = "F/123/test-issue"
        mock_manager.create_pr.return_value = GitOperation(True, "PR created")
        mock_manager.update_issue_status.return_value = GitOperation(True, "Status updated")
        mock_manager.remove_label_from_issue.return_value = GitOperation(True, "Label removed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_tester_workflow(123, "Fix: Test issue", "Fixes #123")

        assert result.success is True
        assert "PR created" in result.message

        # Verify all operations
        mock_manager.create_pr.assert_called_once_with("Fix: Test issue", "Fixes #123", "F/123/test-issue", "main")
        mock_manager.update_issue_status.assert_called_once_with(issue, WorkflowStatus.DONE)
        mock_manager.remove_label_from_issue.assert_called_once_with(issue, "assigned:ai-tester")

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_assign_researcher_to_issue(self, mock_factory, sample_config, sample_issue):
        """Test assigning researcher to issue."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        mock_manager.get_issue.return_value = sample_issue
        mock_manager.assign_to_ai.return_value = GitOperation(True, "Assigned to researcher")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.assign_researcher_to_issue(123)

        assert result.success is True
        assert "Assigned ai-researcher" in result.message

        mock_manager.assign_to_ai.assert_called_once_with(sample_issue, AiaType.AI_RESEARCHER)

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_research_workflow(self, mock_factory, sample_config):
        """Test completing research workflow."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        # Create issue assigned to ai-researcher
        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-researcher"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue
        mock_manager.remove_label_from_issue.return_value = GitOperation(True, "Label removed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_research_workflow(123)

        assert result.success is True
        assert "Completed research workflow" in result.message

        mock_manager.remove_label_from_issue.assert_called_once_with(issue, "assigned:ai-researcher")

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_get_issues_for_ai(self, mock_factory, sample_config, sample_issue):
        """Test getting issues for specific AI type."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        # Test with status filter
        mock_manager.get_issues.return_value = [sample_issue]

        coordinator = WorkflowCoordinator(sample_config, "github")

        # Mock the assigned AI check
        with patch.object(sample_issue, "get_assigned_ai", return_value="ai-coder"):
            issues = coordinator.get_issues_for_ai(AiaType.AI_CODER, WorkflowStatus.DOING)

        assert len(issues) == 1
        assert issues[0] == sample_issue
        mock_manager.get_issues.assert_called_once_with(WorkflowStatus.DOING)

        # Test without status filter
        mock_manager.get_assigned_issues.return_value = [sample_issue]

        issues = coordinator.get_issues_for_ai(AiaType.AI_CODER)
        assert len(issues) == 1
        mock_manager.get_assigned_issues.assert_called_once()

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_get_todo_issues(self, mock_factory, sample_config):
        """Test getting unassigned ToDo issues."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        # Create mix of assigned and unassigned issues
        unassigned_issue = Issue(
            number=123,
            title="Unassigned",
            body="",
            state=IssueState.OPEN,
            labels=["feature"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
            project_status=WorkflowStatus.TODO,
        )

        assigned_issue = Issue(
            number=124,
            title="Assigned",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-coder", "feature"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
            project_status=WorkflowStatus.TODO,
        )

        mock_manager.get_issues.return_value = [unassigned_issue, assigned_issue]

        coordinator = WorkflowCoordinator(sample_config, "github")
        todo_issues = coordinator.get_todo_issues()

        # Should only return unassigned issue
        assert len(todo_issues) == 1
        assert todo_issues[0].number == 123

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_get_workflow_status(self, mock_factory, sample_config):
        """Test getting workflow status counts."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        # Create issues in different statuses
        issues = [
            Issue(123, "Test1", "", IssueState.OPEN, [], [], None, None, "", WorkflowStatus.TODO),
            Issue(124, "Test2", "", IssueState.OPEN, [], [], None, None, "", WorkflowStatus.TODO),
            Issue(125, "Test3", "", IssueState.OPEN, [], [], None, None, "", WorkflowStatus.DOING),
            Issue(126, "Test4", "", IssueState.OPEN, [], [], None, None, "", WorkflowStatus.DONE),
        ]

        mock_manager.get_issues.return_value = issues

        coordinator = WorkflowCoordinator(sample_config, "github")
        status_counts = coordinator.get_workflow_status()

        assert status_counts[WorkflowStatus.TODO] == 2
        assert status_counts[WorkflowStatus.DOING] == 1
        assert status_counts[WorkflowStatus.REVIEW] == 0
        assert status_counts[WorkflowStatus.TESTING] == 0
        assert status_counts[WorkflowStatus.DONE] == 1


class TestWorkflowCoordinatorErrorHandling:
    """Test error handling in WorkflowCoordinator."""

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_start_coder_workflow_update_status_failure(self, mock_factory, sample_config, sample_issue):
        """Test start_coder_workflow when update_issue_status fails."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        mock_manager.get_issue.return_value = sample_issue
        mock_manager.update_issue_status.return_value = GitOperation(False, "Update failed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.start_coder_workflow(123)

        assert result.success is False
        assert "Update failed" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_start_coder_workflow_assign_failure(self, mock_factory, sample_config, sample_issue):
        """Test start_coder_workflow when assign_to_ai fails."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        mock_manager.get_issue.return_value = sample_issue
        mock_manager.update_issue_status.return_value = GitOperation(True, "Updated")
        mock_manager.assign_to_ai.return_value = GitOperation(False, "Assignment failed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.start_coder_workflow(123)

        assert result.success is False
        assert "Assignment failed" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_start_coder_workflow_create_branch_failure(self, mock_factory, sample_config, sample_issue):
        """Test start_coder_workflow when create_branch fails."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        mock_manager.get_issue.return_value = sample_issue
        mock_manager.update_issue_status.return_value = GitOperation(True, "Updated")
        mock_manager.assign_to_ai.return_value = GitOperation(True, "Assigned")
        mock_manager.create_branch.return_value = GitOperation(False, "Branch creation failed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.start_coder_workflow(123)

        assert result.success is False
        assert "Branch creation failed" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_coder_workflow_not_assigned(self, mock_factory, sample_config):
        """Test complete_coder_workflow when issue not assigned to ai-coder."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-reviewer"],  # Wrong assignment
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_coder_workflow(123)

        assert result.success is False
        assert "not assigned to ai-coder" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_reviewer_workflow_not_assigned(self, mock_factory, sample_config):
        """Test complete_reviewer_workflow when issue not assigned to ai-reviewer."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-coder"],  # Wrong assignment
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_reviewer_workflow(123)

        assert result.success is False
        assert "not assigned to ai-reviewer" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_tester_workflow_not_assigned(self, mock_factory, sample_config):
        """Test complete_tester_workflow when issue not assigned to ai-tester."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-coder"],  # Wrong assignment
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_tester_workflow(123, "PR Title", "PR Body")

        assert result.success is False
        assert "not assigned to ai-tester" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_tester_workflow_pr_creation_failure(self, mock_factory, sample_config):
        """Test complete_tester_workflow when PR creation fails."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-tester", "feature"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue
        mock_manager.generate_branch_name.return_value = "F/123/test"
        mock_manager.create_pr.return_value = GitOperation(False, "PR creation failed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_tester_workflow(123, "PR Title", "PR Body")

        assert result.success is False
        assert "PR creation failed" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_tester_workflow_status_update_failure(self, mock_factory, sample_config):
        """Test complete_tester_workflow when status update fails."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-tester", "feature"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue
        mock_manager.generate_branch_name.return_value = "F/123/test"
        mock_manager.create_pr.return_value = GitOperation(True, "PR created")
        mock_manager.update_issue_status.return_value = GitOperation(False, "Status update failed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_tester_workflow(123, "PR Title", "PR Body")

        assert result.success is False
        assert "Status update failed" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_research_workflow_not_assigned(self, mock_factory, sample_config):
        """Test complete_research_workflow when issue not assigned to ai-researcher."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-coder"],  # Wrong assignment
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_research_workflow(123)

        assert result.success is False
        assert "not assigned to ai-researcher" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_coder_workflow_issue_not_found(self, mock_factory, sample_config):
        """Test complete_coder_workflow when issue not found."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager
        mock_manager.get_issue.return_value = None

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_coder_workflow(123)

        assert result.success is False
        assert "Issue 123 not found" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_coder_workflow_status_update_failure(self, mock_factory, sample_config):
        """Test complete_coder_workflow when status update fails."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-coder"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue
        mock_manager.update_issue_status.return_value = GitOperation(False, "Status update failed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_coder_workflow(123)

        assert result.success is False
        assert "Status update failed" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_coder_workflow_assignment_failure(self, mock_factory, sample_config):
        """Test complete_coder_workflow when assignment to reviewer fails."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-coder"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue
        mock_manager.update_issue_status.return_value = GitOperation(True, "Status updated")
        mock_manager.assign_to_ai.return_value = GitOperation(False, "Assignment failed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_coder_workflow(123)

        assert result.success is False
        assert "Assignment failed" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_reviewer_workflow_issue_not_found(self, mock_factory, sample_config):
        """Test complete_reviewer_workflow when issue not found."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager
        mock_manager.get_issue.return_value = None

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_reviewer_workflow(123)

        assert result.success is False
        assert "Issue 123 not found" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_reviewer_workflow_status_update_failure(self, mock_factory, sample_config):
        """Test complete_reviewer_workflow when status update fails."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-reviewer"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue
        mock_manager.update_issue_status.return_value = GitOperation(False, "Status update failed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_reviewer_workflow(123)

        assert result.success is False
        assert "Status update failed" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_reviewer_workflow_assignment_failure(self, mock_factory, sample_config):
        """Test complete_reviewer_workflow when assignment to tester fails."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-reviewer"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue
        mock_manager.update_issue_status.return_value = GitOperation(True, "Status updated")
        mock_manager.assign_to_ai.return_value = GitOperation(False, "Assignment failed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_reviewer_workflow(123)

        assert result.success is False
        assert "Assignment failed" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_tester_workflow_issue_not_found(self, mock_factory, sample_config):
        """Test complete_tester_workflow when issue not found."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager
        mock_manager.get_issue.return_value = None

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_tester_workflow(123, "PR Title", "PR Body")

        assert result.success is False
        assert "Issue 123 not found" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_tester_workflow_label_removal_failure(self, mock_factory, sample_config):
        """Test complete_tester_workflow when label removal fails."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-tester", "feature"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue
        mock_manager.generate_branch_name.return_value = "F/123/test"
        mock_manager.create_pr.return_value = GitOperation(True, "PR created")
        mock_manager.update_issue_status.return_value = GitOperation(True, "Status updated")
        mock_manager.remove_label_from_issue.return_value = GitOperation(False, "Label removal failed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_tester_workflow(123, "PR Title", "PR Body")

        assert result.success is False
        assert "Label removal failed" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_assign_researcher_to_issue_not_found(self, mock_factory, sample_config):
        """Test assign_researcher_to_issue when issue not found."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager
        mock_manager.get_issue.return_value = None

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.assign_researcher_to_issue(123)

        assert result.success is False
        assert "Issue 123 not found" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_assign_researcher_to_issue_assignment_failure(self, mock_factory, sample_config, sample_issue):
        """Test assign_researcher_to_issue when assignment fails."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager
        mock_manager.get_issue.return_value = sample_issue
        mock_manager.assign_to_ai.return_value = GitOperation(False, "Assignment failed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.assign_researcher_to_issue(123)

        assert result.success is False
        assert "Assignment failed" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_research_workflow_issue_not_found(self, mock_factory, sample_config):
        """Test complete_research_workflow when issue not found."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager
        mock_manager.get_issue.return_value = None

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_research_workflow(123)

        assert result.success is False
        assert "Issue 123 not found" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_complete_research_workflow_label_removal_failure(self, mock_factory, sample_config):
        """Test complete_research_workflow when label removal fails."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        issue = Issue(
            number=123,
            title="Test",
            body="",
            state=IssueState.OPEN,
            labels=["assigned:ai-researcher"],
            assignees=[],
            created_at=None,
            updated_at=None,
            url="",
        )

        mock_manager.get_issue.return_value = issue
        mock_manager.remove_label_from_issue.return_value = GitOperation(False, "Label removal failed")

        coordinator = WorkflowCoordinator(sample_config, "github")
        result = coordinator.complete_research_workflow(123)

        assert result.success is False
        assert "Label removal failed" in result.message

    @patch("aia.workflow_coordinator.AiaManagerFactory")
    def test_get_workflow_status_with_none_project_status(self, mock_factory, sample_config):
        """Test get_workflow_status with issues that have None project_status."""
        mock_manager = Mock()
        mock_factory.create_manager.return_value = mock_manager

        # Create issues with mixed project_status including None
        issues = [
            Issue(123, "Test1", "", IssueState.OPEN, [], [], None, None, "", WorkflowStatus.TODO),
            Issue(124, "Test2", "", IssueState.OPEN, [], [], None, None, "", None),  # None status
            Issue(125, "Test3", "", IssueState.OPEN, [], [], None, None, "", WorkflowStatus.DOING),
        ]

        mock_manager.get_issues.return_value = issues

        coordinator = WorkflowCoordinator(sample_config, "github")
        status_counts = coordinator.get_workflow_status()

        assert status_counts[WorkflowStatus.TODO] == 1
        assert status_counts[WorkflowStatus.DOING] == 1
        assert status_counts[WorkflowStatus.REVIEW] == 0
        assert status_counts[WorkflowStatus.TESTING] == 0
        assert status_counts[WorkflowStatus.DONE] == 0
