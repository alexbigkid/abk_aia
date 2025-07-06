"""Workflow coordinator for AI assistant collaboration."""

import logging

from abk_aia.git_aia_manager import AiaManagerBase, AiaType, AiaManagerFactory
from abk_aia.models import Issue, WorkflowConfig, WorkflowStatus, GitOperation
from abk_aia import abk_common


class WorkflowCoordinator:
    """Coordinates workflow between different AI assistants."""

    def __init__(self, provider: str, config: WorkflowConfig):
        """Initialize workflow coordinator."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Create managers for each AI type
        self.managers: dict[AiaType, AiaManagerBase] = {}
        for ai_type in AiaType:
            self.managers[ai_type] = AiaManagerFactory.create_manager(provider, ai_type, config)

    @abk_common.function_trace
    def get_manager(self, ai_type: AiaType) -> AiaManagerBase:
        """Get manager for specific AI type."""
        return self.managers[ai_type]

    @abk_common.function_trace
    def start_coder_workflow(self, issue_number: int) -> GitOperation:
        """Start the ai-coder workflow for an issue."""
        coder_manager = self.get_manager(AiaType.AI_CODER)

        # Get the issue
        issue = coder_manager.get_issue(issue_number)
        if not issue:
            return GitOperation(success=False, message=f"Issue {issue_number} not found")

        # Check if issue is in ToDo status
        if issue.project_status != WorkflowStatus.TODO:
            return GitOperation(
                success=False, message=f"Issue {issue_number} is not in ToDo status"
            )

        # Move to Doing status
        result = coder_manager.update_issue_status(issue, WorkflowStatus.DOING)
        if not result.success:
            return result

        # Assign to ai-coder
        result = coder_manager.assign_to_ai(issue, AiaType.AI_CODER)
        if not result.success:
            return result

        # Create branch
        result = coder_manager.create_branch(issue)
        if not result.success:
            return result

        branch_name = result.output
        self.logger.info(
            f"Started coder workflow for issue {issue_number} on branch {branch_name}"
        )

        return GitOperation(
            success=True,
            message=f"Started coder workflow for issue {issue_number}",
            output=branch_name,
        )

    @abk_common.function_trace
    def complete_coder_workflow(self, issue_number: int) -> GitOperation:
        """Complete the ai-coder workflow and transition to reviewer."""
        coder_manager = self.get_manager(AiaType.AI_CODER)

        # Get the issue
        issue = coder_manager.get_issue(issue_number)
        if not issue:
            return GitOperation(success=False, message=f"Issue {issue_number} not found")

        # Check if assigned to ai-coder
        if issue.get_assigned_ai() != AiaType.AI_CODER.value:
            return GitOperation(
                success=False, message=f"Issue {issue_number} is not assigned to ai-coder"
            )

        # Move to Review status
        result = coder_manager.update_issue_status(issue, WorkflowStatus.REVIEW)
        if not result.success:
            return result

        # Assign to ai-reviewer
        result = coder_manager.assign_to_ai(issue, AiaType.AI_REVIEWER)
        if not result.success:
            return result

        self.logger.info(
            f"Completed coder workflow for issue {issue_number}, assigned to reviewer"
        )

        return GitOperation(
            success=True, message=f"Completed coder workflow for issue {issue_number}"
        )

    @abk_common.function_trace
    def complete_reviewer_workflow(self, issue_number: int) -> GitOperation:
        """Complete the ai-reviewer workflow and transition to tester."""
        reviewer_manager = self.get_manager(AiaType.AI_REVIEWER)

        # Get the issue
        issue = reviewer_manager.get_issue(issue_number)
        if not issue:
            return GitOperation(success=False, message=f"Issue {issue_number} not found")

        # Check if assigned to ai-reviewer
        if issue.get_assigned_ai() != AiaType.AI_REVIEWER.value:
            return GitOperation(
                success=False, message=f"Issue {issue_number} is not assigned to ai-reviewer"
            )

        # Move to Testing status
        result = reviewer_manager.update_issue_status(issue, WorkflowStatus.TESTING)
        if not result.success:
            return result

        # Assign to ai-tester
        result = reviewer_manager.assign_to_ai(issue, AiaType.AI_TESTER)
        if not result.success:
            return result

        self.logger.info(
            f"Completed reviewer workflow for issue {issue_number}, assigned to tester"
        )

        return GitOperation(
            success=True, message=f"Completed reviewer workflow for issue {issue_number}"
        )

    @abk_common.function_trace
    def complete_tester_workflow(
        self, issue_number: int, pr_title: str, pr_body: str
    ) -> GitOperation:
        """Complete the ai-tester workflow and create PR."""
        tester_manager = self.get_manager(AiaType.AI_TESTER)

        # Get the issue
        issue = tester_manager.get_issue(issue_number)
        if not issue:
            return GitOperation(success=False, message=f"Issue {issue_number} not found")

        # Check if assigned to ai-tester
        if issue.get_assigned_ai() != AiaType.AI_TESTER.value:
            return GitOperation(
                success=False, message=f"Issue {issue_number} is not assigned to ai-tester"
            )

        # Generate branch name for PR
        branch_name = tester_manager.generate_branch_name(issue)

        # Create PR
        result = tester_manager.create_pr(
            pr_title, pr_body, branch_name, self.config.default_base_branch
        )
        if not result.success:
            return result

        # Move to Done status
        result = tester_manager.update_issue_status(issue, WorkflowStatus.DONE)
        if not result.success:
            return result

        # Remove AI assignment (ready for human review)
        result = tester_manager.remove_label_from_issue(
            issue, f"assigned:{AiaType.AI_TESTER.value}"
        )
        if not result.success:
            return result

        self.logger.info(f"Completed tester workflow for issue {issue_number}, PR created")

        return GitOperation(
            success=True,
            message=f"Completed tester workflow for issue {issue_number}, PR created",
        )

    @abk_common.function_trace
    def get_issues_for_ai(
        self, ai_type: AiaType, status: WorkflowStatus | None = None
    ) -> list[Issue]:
        """Get issues assigned to specific AI type."""
        manager = self.get_manager(ai_type)

        if status:
            # Get issues with specific status
            all_issues = manager.get_issues(status)
            # Filter by AI assignment
            return [issue for issue in all_issues if issue.get_assigned_ai() == ai_type.value]
        else:
            # Get all issues assigned to this AI
            return manager.get_assigned_issues()

    @abk_common.function_trace
    def get_todo_issues(self) -> list[Issue]:
        """Get issues in ToDo status ready for ai-coder."""
        coder_manager = self.get_manager(AiaType.AI_CODER)
        todo_issues = coder_manager.get_issues(WorkflowStatus.TODO)

        # Filter out issues already assigned to any AI
        return [issue for issue in todo_issues if not issue.is_assigned_to_ai()]

    @abk_common.function_trace
    def get_workflow_status(self) -> dict[WorkflowStatus, int]:
        """Get count of issues by workflow status."""
        coder_manager = self.get_manager(AiaType.AI_CODER)
        all_issues = coder_manager.get_issues()

        status_counts = {status: 0 for status in WorkflowStatus}

        for issue in all_issues:
            if issue.project_status:
                status_counts[issue.project_status] += 1

        return status_counts

    @abk_common.function_trace
    def assign_researcher_to_issue(self, issue_number: int) -> GitOperation:
        """Assign ai-researcher to an issue for research phase."""
        researcher_manager = self.get_manager(AiaType.AI_RESEARCHER)

        # Get the issue
        issue = researcher_manager.get_issue(issue_number)
        if not issue:
            return GitOperation(success=False, message=f"Issue {issue_number} not found")

        # Assign to ai-researcher
        result = researcher_manager.assign_to_ai(issue, AiaType.AI_RESEARCHER)
        if not result.success:
            return result

        self.logger.info(f"Assigned ai-researcher to issue {issue_number}")

        return GitOperation(
            success=True, message=f"Assigned ai-researcher to issue {issue_number}"
        )

    @abk_common.function_trace
    def complete_research_workflow(self, issue_number: int) -> GitOperation:
        """Complete research workflow and prepare for coder."""
        researcher_manager = self.get_manager(AiaType.AI_RESEARCHER)

        # Get the issue
        issue = researcher_manager.get_issue(issue_number)
        if not issue:
            return GitOperation(success=False, message=f"Issue {issue_number} not found")

        # Check if assigned to ai-researcher
        if issue.get_assigned_ai() != AiaType.AI_RESEARCHER.value:
            return GitOperation(
                success=False, message=f"Issue {issue_number} is not assigned to ai-researcher"
            )

        # Remove researcher assignment
        result = researcher_manager.remove_label_from_issue(
            issue, f"assigned:{AiaType.AI_RESEARCHER.value}"
        )
        if not result.success:
            return result

        self.logger.info(f"Completed research workflow for issue {issue_number}")

        return GitOperation(
            success=True, message=f"Completed research workflow for issue {issue_number}"
        )
