"""Example usage of the AI assistant workflow interface."""

import logging
from abk_aia.workflow_coordinator import WorkflowCoordinator
from abk_aia.models import WorkflowConfig, WorkflowStatus
from abk_aia.git_aia_manager import AiaType


def setup_logging():
    """Setup logging for the example."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def main():
    """Example usage of the AI assistant workflow."""
    setup_logging()

    # Configuration for your GitHub repository
    config = WorkflowConfig(
        repo_owner="your-username",
        repo_name="your-repo",
        project_number=1,  # Your GitHub project number
        default_base_branch="main",
    )

    # Initialize workflow coordinator for GitHub
    coordinator = WorkflowCoordinator("github", config)

    print("=== AI Assistant Workflow Example ===")

    # Example 1: Get workflow status overview
    print("\n1. Getting workflow status overview...")
    status_counts = coordinator.get_workflow_status()
    for status, count in status_counts.items():
        print(f"   {status.value}: {count} issues")

    # Example 2: Get issues ready for ai-coder
    print("\n2. Getting issues ready for ai-coder...")
    todo_issues = coordinator.get_todo_issues()
    print(f"   Found {len(todo_issues)} issues in ToDo status")
    for issue in todo_issues[:3]:  # Show first 3
        print(f"   - #{issue.number}: {issue.title}")

    # Example 3: Start ai-coder workflow (if there are todo issues)
    if todo_issues:
        issue_number = todo_issues[0].number
        print(f"\n3. Starting ai-coder workflow for issue #{issue_number}...")

        result = coordinator.start_coder_workflow(issue_number)
        if result.success:
            print(f"   ✓ {result.message}")
            print(f"   Branch: {result.output}")
        else:
            print(f"   ✗ {result.message}")

    # Example 4: Get issues assigned to ai-coder
    print("\n4. Getting issues assigned to ai-coder...")
    coder_issues = coordinator.get_issues_for_ai(AiaType.AI_CODER, WorkflowStatus.DOING)
    print(f"   Found {len(coder_issues)} issues assigned to ai-coder")
    for issue in coder_issues[:3]:  # Show first 3
        print(f"   - #{issue.number}: {issue.title}")

    # Example 5: Complete ai-coder workflow and transition to reviewer
    if coder_issues:
        issue_number = coder_issues[0].number
        print(f"\n5. Completing ai-coder workflow for issue #{issue_number}...")

        result = coordinator.complete_coder_workflow(issue_number)
        if result.success:
            print(f"   ✓ {result.message}")
        else:
            print(f"   ✗ {result.message}")

    # Example 6: Get issues assigned to ai-reviewer
    print("\n6. Getting issues assigned to ai-reviewer...")
    reviewer_issues = coordinator.get_issues_for_ai(AiaType.AI_REVIEWER, WorkflowStatus.REVIEW)
    print(f"   Found {len(reviewer_issues)} issues assigned to ai-reviewer")
    for issue in reviewer_issues[:3]:  # Show first 3
        print(f"   - #{issue.number}: {issue.title}")

    # Example 7: Complete ai-reviewer workflow and transition to tester
    if reviewer_issues:
        issue_number = reviewer_issues[0].number
        print(f"\n7. Completing ai-reviewer workflow for issue #{issue_number}...")

        result = coordinator.complete_reviewer_workflow(issue_number)
        if result.success:
            print(f"   ✓ {result.message}")
        else:
            print(f"   ✗ {result.message}")

    # Example 8: Get issues assigned to ai-tester
    print("\n8. Getting issues assigned to ai-tester...")
    tester_issues = coordinator.get_issues_for_ai(AiaType.AI_TESTER, WorkflowStatus.TESTING)
    print(f"   Found {len(tester_issues)} issues assigned to ai-tester")
    for issue in tester_issues[:3]:  # Show first 3
        print(f"   - #{issue.number}: {issue.title}")

    # Example 9: Complete ai-tester workflow and create PR
    if tester_issues:
        issue_number = tester_issues[0].number
        issue = tester_issues[0]
        print(f"\n9. Completing ai-tester workflow for issue #{issue_number}...")

        pr_title = f"Fix: {issue.title}"
        pr_body = f"Fixes #{issue_number}\\n\\nThis PR implements the solution for {issue.title}"

        result = coordinator.complete_tester_workflow(issue_number, pr_title, pr_body)
        if result.success:
            print(f"   ✓ {result.message}")
        else:
            print(f"   ✗ {result.message}")

    # Example 10: Research workflow
    print("\n10. Research workflow example...")
    if todo_issues:
        issue_number = todo_issues[0].number
        print(f"   Assigning ai-researcher to issue #{issue_number}...")

        result = coordinator.assign_researcher_to_issue(issue_number)
        if result.success:
            print(f"   ✓ {result.message}")

            # Complete research
            print(f"   Completing research for issue #{issue_number}...")
            result = coordinator.complete_research_workflow(issue_number)
            if result.success:
                print(f"   ✓ {result.message}")
            else:
                print(f"   ✗ {result.message}")
        else:
            print(f"   ✗ {result.message}")

    print("\n=== Example completed ===")


if __name__ == "__main__":
    main()
