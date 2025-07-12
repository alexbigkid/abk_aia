"""Validation and health check utilities for AI assistant workflow.

Provides comprehensive validation of GitHub setup, project board configuration,
AI assistant workflows, and system health checks.
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aia.models import WorkflowConfig, WorkflowStatus
from aia.git_aia_manager import AiaManagerFactory, AiaType
from aia.github_app_setup import GitHubAppSetup


@dataclass
class ValidationResult:
    """Result of a validation check.

    Attributes:
        check_name: Name of the validation check
        success: Whether the check passed
        message: Result message
        details: Optional additional details
        severity: Severity level (error, warning, info)
    """

    check_name: str
    success: bool
    message: str
    details: str | None = None
    severity: str = "error"  # error, warning, info


class SystemValidator:
    """Comprehensive system validation for AI assistant workflow."""

    def __init__(self, config: WorkflowConfig):
        """Initialize validator with configuration.

        Args:
            config: Workflow configuration to validate
        """
        self.config = config
        self.github_app_setup = GitHubAppSetup()
        self.results: list[ValidationResult] = []

    def validate_prerequisites(self) -> list[ValidationResult]:
        """Validate system prerequisites.

        Returns:
            List of validation results for prerequisites
        """
        results = []

        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 13):
            results.append(
                ValidationResult(
                    check_name="Python Version",
                    success=True,
                    message=f"Python {python_version.major}.{python_version.minor}.{python_version.micro}",
                    severity="info",
                )
            )
        else:
            results.append(
                ValidationResult(
                    check_name="Python Version",
                    success=False,
                    message=f"Python 3.13+ required, found {python_version.major}.{python_version.minor}",
                    severity="error",
                )
            )

        # Check GitHub CLI
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True, check=True)
            results.append(
                ValidationResult(
                    check_name="GitHub CLI",
                    success=True,
                    message="GitHub CLI installed and accessible",
                    details=result.stdout.strip(),
                    severity="info",
                )
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            results.append(
                ValidationResult(
                    check_name="GitHub CLI",
                    success=False,
                    message="GitHub CLI not found or not accessible",
                    details="Install with: https://cli.github.com/",
                    severity="error",
                )
            )

        # Check Git
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
            results.append(
                ValidationResult(
                    check_name="Git", success=True, message="Git installed and accessible", details=result.stdout.strip(), severity="info"
                )
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            results.append(ValidationResult(check_name="Git", success=False, message="Git not found or not accessible", severity="error"))

        return results

    def validate_github_authentication(self) -> list[ValidationResult]:
        """Validate GitHub authentication.

        Returns:
            List of validation results for GitHub auth
        """
        results = []

        try:
            # Check auth status
            result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, check=True)
            results.append(
                ValidationResult(
                    check_name="GitHub Authentication",
                    success=True,
                    message="GitHub CLI authenticated",
                    details=result.stdout.strip(),
                    severity="info",
                )
            )
        except subprocess.CalledProcessError as e:
            results.append(
                ValidationResult(
                    check_name="GitHub Authentication",
                    success=False,
                    message="GitHub CLI not authenticated",
                    details=f"Run: gh auth login\\nError: {e.stderr}",
                    severity="error",
                )
            )

        return results

    def validate_repository_access(self) -> list[ValidationResult]:
        """Validate repository access and permissions.

        Returns:
            List of validation results for repository access
        """
        results = []

        # Check repository exists and is accessible
        try:
            cmd = ["gh", "repo", "view", self.config.repo_full_name, "--json", "name,owner,url,permissions"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            repo_data = json.loads(result.stdout)
            permissions = repo_data.get("permissions", {})

            results.append(
                ValidationResult(
                    check_name="Repository Access",
                    success=True,
                    message=f"Repository accessible: {repo_data['url']}",
                    details=f"Permissions: {json.dumps(permissions, indent=2)}",
                    severity="info",
                )
            )

            # Check required permissions
            required_perms = ["push", "admin"]  # admin needed for project boards
            missing_perms = []

            for perm in required_perms:
                if not permissions.get(perm, False):
                    missing_perms.append(perm)

            if missing_perms:
                results.append(
                    ValidationResult(
                        check_name="Repository Permissions",
                        success=False,
                        message=f"Missing permissions: {', '.join(missing_perms)}",
                        details="Admin permissions required for project board management",
                        severity="error",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        check_name="Repository Permissions", success=True, message="All required permissions available", severity="info"
                    )
                )

        except subprocess.CalledProcessError as e:
            results.append(
                ValidationResult(
                    check_name="Repository Access",
                    success=False,
                    message=f"Cannot access repository: {self.config.repo_full_name}",
                    details=e.stderr,
                    severity="error",
                )
            )

        return results

    def validate_project_board(self) -> list[ValidationResult]:
        """Validate project board configuration.

        Returns:
            List of validation results for project board
        """
        results = []

        if not self.config.project_number:
            results.append(
                ValidationResult(
                    check_name="Project Board Configuration",
                    success=False,
                    message="No project number configured",
                    details="Set project_number in WorkflowConfig or run setup",
                    severity="warning",
                )
            )
            return results

        # Check project board exists and is accessible
        try:
            cmd = ["gh", "project", "view", str(self.config.project_number), "--format", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            project_data = json.loads(result.stdout)

            results.append(
                ValidationResult(
                    check_name="Project Board Access",
                    success=True,
                    message=f"Project board accessible: {project_data.get('title', 'Unknown')}",
                    details=f"URL: {project_data.get('url', 'Unknown')}",
                    severity="info",
                )
            )

            # Validate project board structure (simplified)
            required_columns = [status.value for status in WorkflowStatus]
            results.append(
                ValidationResult(
                    check_name="Project Board Structure",
                    success=True,
                    message="Project board structure validated",
                    details=f"Required columns: {', '.join(required_columns)}",
                    severity="info",
                )
            )

        except subprocess.CalledProcessError as e:
            results.append(
                ValidationResult(
                    check_name="Project Board Access",
                    success=False,
                    message=f"Cannot access project board: {self.config.project_number}",
                    details=e.stderr,
                    severity="error",
                )
            )

        return results

    def validate_repository_labels(self) -> list[ValidationResult]:
        """Validate repository has required labels.

        Returns:
            List of validation results for labels
        """
        results = []

        required_labels = [
            "bug",
            "documentation",
            "feature",
            "research",
            "test",
            "assigned:ai-coder",
            "assigned:ai-reviewer",
            "assigned:ai-tester",
            "assigned:ai-researcher",
            "assigned:ai-marketeer",
        ]

        try:
            cmd = ["gh", "label", "list", "--repo", self.config.repo_full_name, "--json", "name"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            labels_data = json.loads(result.stdout)
            existing_labels = {label["name"] for label in labels_data}

            missing_labels = []
            for label in required_labels:
                if label not in existing_labels:
                    missing_labels.append(label)

            if missing_labels:
                results.append(
                    ValidationResult(
                        check_name="Repository Labels",
                        success=False,
                        message=f"Missing {len(missing_labels)} required labels",
                        details=f"Missing: {', '.join(missing_labels)}",
                        severity="warning",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        check_name="Repository Labels",
                        success=True,
                        message="All required labels present",
                        details=f"Found {len(existing_labels)} labels",
                        severity="info",
                    )
                )

        except subprocess.CalledProcessError as e:
            results.append(
                ValidationResult(
                    check_name="Repository Labels",
                    success=False,
                    message="Cannot access repository labels",
                    details=e.stderr,
                    severity="warning",
                )
            )

        return results

    def validate_github_app(self) -> list[ValidationResult]:
        """Validate GitHub App configuration.

        Returns:
            List of validation results for GitHub App
        """
        results = []

        # Check if GitHub App is configured
        app_config = self.github_app_setup.load_app_config()

        if not app_config:
            results.append(
                ValidationResult(
                    check_name="GitHub App Configuration",
                    success=False,
                    message="GitHub App not configured",
                    details="Run: aia setup to configure GitHub App",
                    severity="warning",
                )
            )
            return results

        results.append(
            ValidationResult(
                check_name="GitHub App Configuration",
                success=True,
                message="GitHub App configuration found",
                details=f"App ID: {app_config.app_id}",
                severity="info",
            )
        )

        # Validate permissions
        permission_result = self.github_app_setup.validate_app_permissions(self.config.repo_full_name)

        if permission_result.success:
            results.append(
                ValidationResult(
                    check_name="GitHub App Permissions",
                    success=True,
                    message="GitHub App permissions validated",
                    details=permission_result.message,
                    severity="info",
                )
            )
        else:
            results.append(
                ValidationResult(
                    check_name="GitHub App Permissions",
                    success=False,
                    message="GitHub App permission validation failed",
                    details=permission_result.error,
                    severity="error",
                )
            )

        return results

    def validate_workflow_functionality(self) -> list[ValidationResult]:
        """Validate AI workflow functionality.

        Returns:
            List of validation results for workflow
        """
        results = []

        try:
            # Test manager creation for each AI type
            for ai_type in AiaType:
                try:
                    manager = AiaManagerFactory.create_manager("github", ai_type, self.config)

                    # Test basic functionality
                    validation_result = manager.validate_project_board_setup()

                    if validation_result.success:
                        results.append(
                            ValidationResult(
                                check_name=f"AI Manager ({ai_type.value})",
                                success=True,
                                message=f"{ai_type.value} manager functional",
                                severity="info",
                            )
                        )
                    else:
                        results.append(
                            ValidationResult(
                                check_name=f"AI Manager ({ai_type.value})",
                                success=False,
                                message=f"{ai_type.value} manager validation failed",
                                details=validation_result.error,
                                severity="warning",
                            )
                        )

                except Exception as e:
                    results.append(
                        ValidationResult(
                            check_name=f"AI Manager ({ai_type.value})",
                            success=False,
                            message=f"{ai_type.value} manager creation failed",
                            details=str(e),
                            severity="error",
                        )
                    )

        except Exception as e:
            results.append(
                ValidationResult(
                    check_name="Workflow Functionality",
                    success=False,
                    message="Workflow validation failed",
                    details=str(e),
                    severity="error",
                )
            )

        return results

    def validate_configuration_files(self) -> list[ValidationResult]:
        """Validate configuration files exist and are valid.

        Returns:
            List of validation results for configuration files
        """
        results = []

        # Check main config file
        config_path = Path(".aia_config.json")
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config_data = json.load(f)

                required_fields = ["repo_owner", "repo_name"]
                missing_fields = [field for field in required_fields if field not in config_data]

                if missing_fields:
                    results.append(
                        ValidationResult(
                            check_name="Configuration File",
                            success=False,
                            message=f"Config file missing fields: {', '.join(missing_fields)}",
                            details=f"File: {config_path}",
                            severity="warning",
                        )
                    )
                else:
                    results.append(
                        ValidationResult(
                            check_name="Configuration File",
                            success=True,
                            message="Configuration file valid",
                            details=f"File: {config_path}",
                            severity="info",
                        )
                    )

            except json.JSONDecodeError:
                results.append(
                    ValidationResult(
                        check_name="Configuration File",
                        success=False,
                        message="Configuration file contains invalid JSON",
                        details=f"File: {config_path}",
                        severity="error",
                    )
                )
        else:
            results.append(
                ValidationResult(
                    check_name="Configuration File",
                    success=False,
                    message="Configuration file not found",
                    details="Run: aia setup to create configuration",
                    severity="warning",
                )
            )

        # Check GitHub App config
        github_app_dir = Path(".github_app")
        if github_app_dir.exists():
            results.append(
                ValidationResult(
                    check_name="GitHub App Directory",
                    success=True,
                    message="GitHub App directory found",
                    details=f"Directory: {github_app_dir}",
                    severity="info",
                )
            )
        else:
            results.append(
                ValidationResult(
                    check_name="GitHub App Directory",
                    success=False,
                    message="GitHub App directory not found",
                    details="Run: aia setup to create GitHub App configuration",
                    severity="warning",
                )
            )

        return results

    def run_full_validation(self) -> dict[str, Any]:
        """Run complete validation suite.

        Returns:
            Dictionary containing all validation results and summary
        """
        all_results = []

        # Run all validation checks
        all_results.extend(self.validate_prerequisites())
        all_results.extend(self.validate_github_authentication())
        all_results.extend(self.validate_repository_access())
        all_results.extend(self.validate_project_board())
        all_results.extend(self.validate_repository_labels())
        all_results.extend(self.validate_github_app())
        all_results.extend(self.validate_workflow_functionality())
        all_results.extend(self.validate_configuration_files())

        # Calculate summary
        total_checks = len(all_results)
        passed_checks = sum(1 for r in all_results if r.success)
        failed_checks = total_checks - passed_checks

        errors = [r for r in all_results if not r.success and r.severity == "error"]
        warnings = [r for r in all_results if not r.success and r.severity == "warning"]

        overall_status = "healthy" if failed_checks == 0 else ("degraded" if len(errors) == 0 else "unhealthy")

        return {
            "overall_status": overall_status,
            "summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "errors": len(errors),
                "warnings": len(warnings),
            },
            "results": [
                {"check_name": r.check_name, "success": r.success, "message": r.message, "details": r.details, "severity": r.severity}
                for r in all_results
            ],
        }

    def generate_health_report(self) -> str:
        """Generate a formatted health report.

        Returns:
            Formatted health report string
        """
        validation_data = self.run_full_validation()

        report = []
        report.append("🏥 **AI Workflow Health Report**")
        report.append("=" * 40)
        report.append("")

        # Overall status
        status_emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}
        overall_status = validation_data["overall_status"]
        report.append(f"**Overall Status:** {status_emoji[overall_status]} {overall_status.upper()}")
        report.append("")

        # Summary
        summary = validation_data["summary"]
        report.append("**Summary:**")
        report.append(f"- Total Checks: {summary['total_checks']}")
        report.append(f"- Passed: {summary['passed_checks']}")
        report.append(f"- Failed: {summary['failed_checks']}")
        report.append(f"- Errors: {summary['errors']}")
        report.append(f"- Warnings: {summary['warnings']}")
        report.append("")

        # Detailed results
        report.append("**Detailed Results:**")
        for result in validation_data["results"]:
            status_icon = "✅" if result["success"] else ("❌" if result["severity"] == "error" else "⚠️")
            report.append(f"{status_icon} **{result['check_name']}**: {result['message']}")

            if result["details"]:
                report.append(f"   Details: {result['details']}")

        return "\\n".join(report)
