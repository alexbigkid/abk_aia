"""Notification system for AI assistant workflow tracking.

Provides notifications and status updates for AI assistant workflows,
including issue comments, progress tracking, and workflow state changes.
"""

import json
import logging
from datetime import datetime
from typing import Any

from aia.models import Issue, WorkflowStatus, GitOperation
from aia.git_aia_manager import AiaType, AiaManagerBase


class WorkflowNotifications:
    """Handles notifications and status tracking for AI workflows."""

    def __init__(self, manager: AiaManagerBase):
        """Initialize notification system.

        Args:
            manager: AI assistant manager for GitHub operations
        """
        self.manager = manager
        self.logger = logging.getLogger(__name__)

    def notify_workflow_start(self, issue: Issue, ai_type: AiaType, branch_name: str) -> GitOperation:
        """Notify that an AI workflow has started.

        Args:
            issue: Issue being worked on
            ai_type: AI assistant type starting the workflow
            branch_name: Branch created for the work

        Returns:
            GitOperation result of notification
        """
        timestamp = datetime.now().isoformat()

        message = f"""🚀 **{ai_type.value} workflow started**

**Issue:** #{issue.number} - {issue.title}
**Branch:** `{branch_name}`
**Started:** {timestamp}

{ai_type.value} is now working on this issue. Progress updates will be posted here.
"""

        return self.manager.comment_on_pr(self.manager.config.repo_full_name, issue.number, message)

    def notify_workflow_progress(self, issue: Issue, ai_type: AiaType, progress_message: str) -> GitOperation:
        """Notify workflow progress update.

        Args:
            issue: Issue being worked on
            ai_type: AI assistant type providing the update
            progress_message: Progress update message

        Returns:
            GitOperation result of notification
        """
        timestamp = datetime.now().isoformat()

        message = f"""⚡ **{ai_type.value} progress update**

{progress_message}

**Updated:** {timestamp}
"""

        return self.manager.comment_on_pr(self.manager.config.repo_full_name, issue.number, message)

    def notify_workflow_transition(
        self, issue: Issue, from_status: WorkflowStatus, to_status: WorkflowStatus, next_ai: AiaType
    ) -> GitOperation:
        """Notify workflow transition between AI assistants.

        Args:
            issue: Issue being transitioned
            from_status: Previous workflow status
            to_status: New workflow status
            next_ai: Next AI assistant taking over

        Returns:
            GitOperation result of notification
        """
        timestamp = datetime.now().isoformat()

        message = f"""🔄 **Workflow transition**

**Issue:** #{issue.number} - {issue.title}
**From:** {from_status.value}
**To:** {to_status.value}
**Next AI:** {next_ai.value}
**Transitioned:** {timestamp}

{next_ai.value} will now take over this issue.
"""

        return self.manager.comment_on_pr(self.manager.config.repo_full_name, issue.number, message)

    def notify_workflow_complete(self, issue: Issue, ai_type: AiaType, pr_url: str | None = None) -> GitOperation:
        """Notify that an AI workflow has completed.

        Args:
            issue: Issue that was completed
            ai_type: AI assistant type that completed the work
            pr_url: Optional pull request URL if created

        Returns:
            GitOperation result of notification
        """
        timestamp = datetime.now().isoformat()

        message = f"""✅ **{ai_type.value} workflow completed**

**Issue:** #{issue.number} - {issue.title}
**Completed:** {timestamp}
"""

        if pr_url:
            message += f"**Pull Request:** {pr_url}\n"

        message += f"\n{ai_type.value} has completed work on this issue. Ready for human review!"

        return self.manager.comment_on_pr(self.manager.config.repo_full_name, issue.number, message)

    def notify_workflow_error(self, issue: Issue, ai_type: AiaType, error_message: str) -> GitOperation:
        """Notify workflow error that requires human intervention.

        Args:
            issue: Issue where error occurred
            ai_type: AI assistant type that encountered the error
            error_message: Error description

        Returns:
            GitOperation result of notification
        """
        timestamp = datetime.now().isoformat()

        message = f"""❌ **{ai_type.value} workflow error**

**Issue:** #{issue.number} - {issue.title}
**Error:** {error_message}
**Occurred:** {timestamp}

Human intervention required. Please review and resolve the error.
"""

        return self.manager.comment_on_pr(self.manager.config.repo_full_name, issue.number, message)

    def create_workflow_summary(self, issue: Issue) -> dict[str, Any]:
        """Create a summary of workflow activities for an issue.

        Args:
            issue: Issue to summarize

        Returns:
            Dictionary containing workflow summary
        """
        return {
            "issue_number": issue.number,
            "issue_title": issue.title,
            "current_status": issue.project_status.value if issue.project_status else "Unknown",
            "assigned_ai": issue.get_assigned_ai(),
            "labels": issue.labels,
            "created_at": issue.created_at.isoformat(),
            "updated_at": issue.updated_at.isoformat(),
            "url": issue.url,
        }

    def generate_status_report(self, issues: list[Issue]) -> str:
        """Generate a formatted status report for multiple issues.

        Args:
            issues: List of issues to include in report

        Returns:
            Formatted status report string
        """
        if not issues:
            return "No issues to report."

        report = []
        report.append("📊 **AI Workflow Status Report**")
        report.append("=" * 40)
        report.append("")

        # Group issues by status
        status_groups = {}
        for issue in issues:
            status = issue.project_status.value if issue.project_status else "Unknown"
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(issue)

        # Report each status group
        for status, status_issues in status_groups.items():
            report.append(f"**{status}** ({len(status_issues)} issues)")
            for issue in status_issues:
                assigned_ai = issue.get_assigned_ai()
                ai_info = f" [{assigned_ai}]" if assigned_ai else ""
                report.append(f"  • #{issue.number}: {issue.title}{ai_info}")
            report.append("")

        return "\n".join(report)

    def log_workflow_event(self, event_type: str, issue: Issue, ai_type: AiaType, details: dict[str, Any]) -> None:
        """Log workflow event for debugging and tracking.

        Args:
            event_type: Type of event (start, progress, transition, complete, error)
            issue: Issue involved in the event
            ai_type: AI assistant type
            details: Additional event details
        """
        event_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "issue_number": issue.number,
            "issue_title": issue.title,
            "ai_type": ai_type.value,
            "status": issue.project_status.value if issue.project_status else None,
            "details": details,
        }

        self.logger.info(f"Workflow event: {json.dumps(event_data, indent=2)}")


class WorkflowTracker:
    """Tracks workflow progress and generates analytics."""

    def __init__(self):
        """Initialize workflow tracker."""
        self.events = []
        self.logger = logging.getLogger(__name__)

    def track_event(
        self, event_type: str, issue_number: int, ai_type: AiaType, duration: float | None = None, success: bool = True
    ) -> None:
        """Track a workflow event.

        Args:
            event_type: Type of event
            issue_number: Issue number
            ai_type: AI assistant type
            duration: Optional duration in seconds
            success: Whether the event was successful
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "issue_number": issue_number,
            "ai_type": ai_type.value,
            "duration": duration,
            "success": success,
        }

        self.events.append(event)
        self.logger.info(f"Tracked event: {json.dumps(event)}")

    def get_workflow_metrics(self) -> dict[str, Any]:
        """Get workflow performance metrics.

        Returns:
            Dictionary containing workflow metrics
        """
        if not self.events:
            return {"total_events": 0, "message": "No events tracked yet"}

        total_events = len(self.events)
        successful_events = sum(1 for e in self.events if e["success"])
        success_rate = (successful_events / total_events) * 100

        # Calculate average duration for events that have duration
        durations = [e["duration"] for e in self.events if e["duration"] is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Count events by AI type
        ai_counts = {}
        for event in self.events:
            ai_type = event["ai_type"]
            ai_counts[ai_type] = ai_counts.get(ai_type, 0) + 1

        return {
            "total_events": total_events,
            "successful_events": successful_events,
            "success_rate": round(success_rate, 2),
            "average_duration": round(avg_duration, 2),
            "ai_type_distribution": ai_counts,
            "latest_event": self.events[-1] if self.events else None,
        }

    def export_events(self, filename: str) -> bool:
        """Export tracked events to JSON file.

        Args:
            filename: Output filename

        Returns:
            True if export succeeded
        """
        try:
            with open(filename, "w") as f:
                json.dump(self.events, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to export events: {e}")
            return False
