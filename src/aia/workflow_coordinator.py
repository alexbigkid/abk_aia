"""Workflow coordinator for AI assistant collaboration.

Orchestrates the AI assistant workflow, managing transitions between
different AI types and workflow states in the kanban process.
"""

import logging

from aia.git_aia_manager import AiaManagerBase, AiaType, AiaManagerFactory
from aia.models import Issue, WorkflowConfig, WorkflowStatus, GitOperation
from aia import abk_common


class WorkflowCoordinator:
    """Coordinates workflow between different AI assistants.

    Manages the complete AI assistant workflow from issue assignment
    through code implementation, review, testing, and PR creation.

    Args:
        provider: Git provider name ("github", "gitlab", "bitbucket")
        config: Workflow configuration with repository settings
    """

    def __init__(self, config: WorkflowConfig, provider: str = "github"):
        """Initialize workflow coordinator with managers for all AI types."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Create managers for each AI type
        self.managers: dict[AiaType, AiaManagerBase] = {}
        for ai_type in AiaType:
            self.managers[ai_type] = AiaManagerFactory.create_manager(provider, ai_type, config)

    @abk_common.function_trace
    def get_manager(self, ai_type: AiaType) -> AiaManagerBase:
        """Get manager for specific AI type.

        Args:
            ai_type: AI assistant type

        Returns:
            Manager instance for the AI type
        """
        return self.managers[ai_type]

    @abk_common.function_trace
    def start_coder_workflow(self, issue_number: int) -> GitOperation:
        """Start ai-coder workflow: ToDo → Doing, assign to ai-coder, create branch.

        Args:
            issue_number: Issue number to start workflow for

        Returns:
            GitOperation with branch name in output if successful
        """
        coder_manager = self.get_manager(AiaType.AI_CODER)

        # Get the issue
        issue = coder_manager.get_issue(issue_number)
        if not issue:
            return GitOperation(success=False, message=f"Issue {issue_number} not found")

        # Check if issue is in ToDo status
        if issue.project_status != WorkflowStatus.TODO:
            return GitOperation(success=False, message=f"Issue {issue_number} is not in ToDo status")

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
        self.logger.info(f"Started coder workflow for issue {issue_number} on branch {branch_name}")

        return GitOperation(success=True, message=f"Started coder workflow for issue {issue_number}", output=branch_name)

    @abk_common.function_trace
    def complete_coder_workflow(self, issue_number: int) -> GitOperation:
        """Complete ai-coder workflow: Doing → Review, assign to ai-reviewer.

        Args:
            issue_number: Issue number to complete workflow for

        Returns:
            GitOperation with success/failure details
        """
        coder_manager = self.get_manager(AiaType.AI_CODER)

        # Get the issue
        issue = coder_manager.get_issue(issue_number)
        if not issue:
            return GitOperation(success=False, message=f"Issue {issue_number} not found")

        # Check if assigned to ai-coder
        if issue.get_assigned_ai() != AiaType.AI_CODER.value:
            return GitOperation(success=False, message=f"Issue {issue_number} is not assigned to ai-coder")

        # Move to Review status
        result = coder_manager.update_issue_status(issue, WorkflowStatus.REVIEW)
        if not result.success:
            return result

        # Assign to ai-reviewer
        result = coder_manager.assign_to_ai(issue, AiaType.AI_REVIEWER)
        if not result.success:
            return result

        self.logger.info(f"Completed coder workflow for issue {issue_number}, assigned to reviewer")

        return GitOperation(success=True, message=f"Completed coder workflow for issue {issue_number}")

    @abk_common.function_trace
    def complete_reviewer_workflow(self, issue_number: int) -> GitOperation:
        """Complete ai-reviewer workflow: Review → Testing, assign to ai-tester.

        Args:
            issue_number: Issue number to complete workflow for

        Returns:
            GitOperation with success/failure details
        """
        reviewer_manager = self.get_manager(AiaType.AI_REVIEWER)

        # Get the issue
        issue = reviewer_manager.get_issue(issue_number)
        if not issue:
            return GitOperation(success=False, message=f"Issue {issue_number} not found")

        # Check if assigned to ai-reviewer
        if issue.get_assigned_ai() != AiaType.AI_REVIEWER.value:
            return GitOperation(success=False, message=f"Issue {issue_number} is not assigned to ai-reviewer")

        # Move to Testing status
        result = reviewer_manager.update_issue_status(issue, WorkflowStatus.TESTING)
        if not result.success:
            return result

        # Assign to ai-tester
        result = reviewer_manager.assign_to_ai(issue, AiaType.AI_TESTER)
        if not result.success:
            return result

        self.logger.info(f"Completed reviewer workflow for issue {issue_number}, assigned to tester")

        return GitOperation(success=True, message=f"Completed reviewer workflow for issue {issue_number}")

    @abk_common.function_trace
    def complete_tester_workflow(self, issue_number: int, pr_title: str, pr_body: str) -> GitOperation:
        """Complete ai-tester workflow: Testing → Done, create PR, unassign AI.

        Args:
            issue_number: Issue number to complete workflow for
            pr_title: Pull request title
            pr_body: Pull request body

        Returns:
            GitOperation with success/failure details
        """
        tester_manager = self.get_manager(AiaType.AI_TESTER)

        # Get the issue
        issue = tester_manager.get_issue(issue_number)
        if not issue:
            return GitOperation(success=False, message=f"Issue {issue_number} not found")

        # Check if assigned to ai-tester
        if issue.get_assigned_ai() != AiaType.AI_TESTER.value:
            return GitOperation(success=False, message=f"Issue {issue_number} is not assigned to ai-tester")

        # Generate branch name for PR
        branch_name = tester_manager.generate_branch_name(issue)

        # Create PR
        result = tester_manager.create_pr(pr_title, pr_body, branch_name, self.config.default_base_branch)
        if not result.success:
            return result

        # Move to Done status
        result = tester_manager.update_issue_status(issue, WorkflowStatus.DONE)
        if not result.success:
            return result

        # Remove AI assignment (ready for human review)
        result = tester_manager.remove_label_from_issue(issue, f"assigned:{AiaType.AI_TESTER.value}")
        if not result.success:
            return result

        self.logger.info(f"Completed tester workflow for issue {issue_number}, PR created")

        return GitOperation(success=True, message=f"Completed tester workflow for issue {issue_number}, PR created")

    @abk_common.function_trace
    def get_issues_for_ai(self, ai_type: AiaType, status: WorkflowStatus | None = None) -> list[Issue]:
        """Get issues assigned to specific AI type, optionally filtered by status.

        Args:
            ai_type: AI assistant type
            status: Optional workflow status filter

        Returns:
            List of issues assigned to the AI type
        """
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
        """Get unassigned issues in ToDo status ready for ai-coder.

        Returns:
            List of issues in ToDo status not assigned to any AI
        """
        coder_manager = self.get_manager(AiaType.AI_CODER)
        todo_issues = coder_manager.get_issues(WorkflowStatus.TODO)

        # Filter out issues already assigned to any AI
        return [issue for issue in todo_issues if not issue.is_assigned_to_ai()]

    @abk_common.function_trace
    def get_workflow_status(self) -> dict[WorkflowStatus, int]:
        """Get count of issues by workflow status.

        Returns:
            Dictionary mapping workflow status to issue count
        """
        coder_manager = self.get_manager(AiaType.AI_CODER)
        all_issues = coder_manager.get_issues()

        status_counts = {status: 0 for status in WorkflowStatus}

        for issue in all_issues:
            if issue.project_status:
                status_counts[issue.project_status] += 1

        return status_counts

    @abk_common.function_trace
    def assign_researcher_to_issue(self, issue_number: int) -> GitOperation:
        """Assign ai-researcher to an issue for research phase.

        Args:
            issue_number: Issue number to assign researcher to

        Returns:
            GitOperation with success/failure details
        """
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

        return GitOperation(success=True, message=f"Assigned ai-researcher to issue {issue_number}")

    @abk_common.function_trace
    def complete_research_workflow(self, issue_number: int) -> GitOperation:
        """Complete research workflow and unassign ai-researcher.

        Args:
            issue_number: Issue number to complete research for

        Returns:
            GitOperation with success/failure details
        """
        researcher_manager = self.get_manager(AiaType.AI_RESEARCHER)

        # Get the issue
        issue = researcher_manager.get_issue(issue_number)
        if not issue:
            return GitOperation(success=False, message=f"Issue {issue_number} not found")

        # Check if assigned to ai-researcher
        if issue.get_assigned_ai() != AiaType.AI_RESEARCHER.value:
            return GitOperation(success=False, message=f"Issue {issue_number} is not assigned to ai-researcher")

        # Remove researcher assignment
        result = researcher_manager.remove_label_from_issue(issue, f"assigned:{AiaType.AI_RESEARCHER.value}")
        if not result.success:
            return result

        self.logger.info(f"Completed research workflow for issue {issue_number}")

        return GitOperation(success=True, message=f"Completed research workflow for issue {issue_number}")

    @abk_common.function_trace
    def trigger_ai_coder(self) -> GitOperation:
        """Trigger ai-coder to pick up the highest priority ToDo issue.

        Returns:
            GitOperation with workflow start details
        """
        coder_manager = self.get_manager(AiaType.AI_CODER)

        # Get the top priority ToDo issue
        top_issue = coder_manager.get_top_priority_todo_issue()
        if not top_issue:
            return GitOperation(success=False, message="No ToDo issues available for ai-coder")

        # Start the coder workflow
        result = self.start_coder_workflow(top_issue.number)
        if not result.success:
            return result

        self.logger.info(f"ai-coder triggered for issue #{top_issue.number}: {top_issue.title}")

        return GitOperation(
            success=True, message=f"ai-coder started working on issue #{top_issue.number}: {top_issue.title}", output=result.output
        )

    @abk_common.function_trace
    def trigger_ai_reviewer(self) -> GitOperation:
        """Trigger ai-reviewer to review issues in Review column.

        Returns:
            GitOperation with review workflow details
        """
        reviewer_manager = self.get_manager(AiaType.AI_REVIEWER)

        # Get issues in Review column
        review_issues = reviewer_manager.get_issues_in_column(WorkflowStatus.REVIEW)
        if not review_issues:
            return GitOperation(success=False, message="No issues in Review column for ai-reviewer")

        # Process the first review issue
        issue = review_issues[0]

        # Comment on the issue with review start notification
        comment_result = reviewer_manager.comment_on_pr(
            self.config.repo_full_name, issue.number, "🔍 ai-reviewer started reviewing this issue..."
        )

        if not comment_result.success:
            self.logger.warning(f"Could not add review comment: {comment_result.message}")

        self.logger.info(f"ai-reviewer triggered for issue #{issue.number}: {issue.title}")

        return GitOperation(
            success=True, message=f"ai-reviewer started reviewing issue #{issue.number}: {issue.title}", output=f"issue_{issue.number}"
        )

    @abk_common.function_trace
    def trigger_ai_tester(self) -> GitOperation:
        """Trigger ai-tester to test issues in Testing column.

        Returns:
            GitOperation with testing workflow details
        """
        tester_manager = self.get_manager(AiaType.AI_TESTER)

        # Get issues in Testing column
        testing_issues = tester_manager.get_issues_in_column(WorkflowStatus.TESTING)
        if not testing_issues:
            return GitOperation(success=False, message="No issues in Testing column for ai-tester")

        # Process the first testing issue
        issue = testing_issues[0]

        # Comment on the issue with testing start notification
        comment_result = tester_manager.comment_on_pr(
            self.config.repo_full_name, issue.number, "🧪 ai-tester started testing this issue..."
        )

        if not comment_result.success:
            self.logger.warning(f"Could not add testing comment: {comment_result.message}")

        self.logger.info(f"ai-tester triggered for issue #{issue.number}: {issue.title}")

        return GitOperation(
            success=True, message=f"ai-tester started testing issue #{issue.number}: {issue.title}", output=f"issue_{issue.number}"
        )

    @abk_common.function_trace
    def simulate_complete_workflow(self, issue_number: int) -> GitOperation:
        """Simulate a complete AI workflow for testing purposes.

        Args:
            issue_number: Issue number to run workflow for

        Returns:
            GitOperation with complete workflow simulation results
        """
        results = []

        # Step 1: Start coder workflow
        coder_result = self.start_coder_workflow(issue_number)
        if not coder_result.success:
            return coder_result
        results.append(f"✅ ai-coder: {coder_result.message}")

        # Step 2: Complete coder workflow
        complete_coder_result = self.complete_coder_workflow(issue_number)
        if not complete_coder_result.success:
            return complete_coder_result
        results.append(f"✅ ai-coder → ai-reviewer: {complete_coder_result.message}")

        # Step 3: Complete reviewer workflow
        complete_reviewer_result = self.complete_reviewer_workflow(issue_number)
        if not complete_reviewer_result.success:
            return complete_reviewer_result
        results.append(f"✅ ai-reviewer → ai-tester: {complete_reviewer_result.message}")

        # Step 4: Complete tester workflow
        pr_title = f"Implement issue #{issue_number}"
        pr_body = f"This PR implements the changes for issue #{issue_number}."
        complete_tester_result = self.complete_tester_workflow(issue_number, pr_title, pr_body)
        if not complete_tester_result.success:
            return complete_tester_result
        results.append(f"✅ ai-tester → Done: {complete_tester_result.message}")

        return GitOperation(
            success=True, message=f"Complete workflow simulation completed for issue #{issue_number}", output="\n".join(results)
        )
