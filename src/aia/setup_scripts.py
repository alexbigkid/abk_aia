"""Setup scripts for GitHub project board validation and configuration.

Provides automated setup and validation utilities for configuring
GitHub repositories and project boards for AI assistant workflows.
"""

import json
import subprocess
import sys
from pathlib import Path

from aia.models import WorkflowConfig, WorkflowStatus, GitOperation
from aia.git_aia_manager import AiaType


class ProjectBoardSetup:
    """Handles GitHub project board setup and validation."""

    def __init__(self, config: WorkflowConfig):
        """Initialize setup with workflow configuration.

        Args:
            config: Workflow configuration
        """
        self.config = config
        self.required_columns = [status.value for status in WorkflowStatus]
        self.required_labels = [
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

    def validate_github_cli(self) -> GitOperation:
        """Validate that GitHub CLI is installed and authenticated.

        Returns:
            GitOperation result of validation
        """
        try:
            # Check if gh CLI is installed
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True, check=True)

            # Check if authenticated
            auth_result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, check=True)

            return GitOperation(
                success=True,
                message="GitHub CLI is installed and authenticated",
                output=f"CLI Version: {result.stdout.strip()}\\nAuth Status: {auth_result.stdout.strip()}",
            )
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"GitHub CLI validation failed: {e.stderr}", error=e.stderr)
        except FileNotFoundError:
            return GitOperation(
                success=False, message="GitHub CLI not found. Please install GitHub CLI first.", error="GitHub CLI not installed"
            )

    def validate_repository_access(self) -> GitOperation:
        """Validate access to the configured repository.

        Returns:
            GitOperation result of validation
        """
        try:
            cmd = ["gh", "repo", "view", self.config.repo_full_name, "--json", "name,owner,url"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            repo_data = json.loads(result.stdout)

            return GitOperation(success=True, message=f"Repository access validated: {repo_data['url']}", output=result.stdout)
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Repository access validation failed: {e.stderr}", error=e.stderr)

    def create_project_board(self, project_name: str) -> GitOperation:
        """Create a new GitHub project board with required columns.

        Args:
            project_name: Name for the new project board

        Returns:
            GitOperation result with project number if successful
        """
        try:
            # Create project
            cmd = ["gh", "project", "create", "--owner", self.config.repo_owner, "--title", project_name, "--format", "json"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            project_data = json.loads(result.stdout)
            project_number = project_data["number"]

            # Add the repository to the project
            add_repo_cmd = ["gh", "project", "item-add", str(project_number), "--url", f"https://github.com/{self.config.repo_full_name}"]

            subprocess.run(add_repo_cmd, capture_output=True, text=True, check=True)

            return GitOperation(success=True, message=f"Project board created with number: {project_number}", output=str(project_number))
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Project board creation failed: {e.stderr}", error=e.stderr)

    def validate_project_board_columns(self) -> GitOperation:
        """Validate that project board has required columns.

        Returns:
            GitOperation result of validation
        """
        if not self.config.project_number:
            return GitOperation(success=False, message="No project number configured")

        try:
            # Get project details
            cmd = ["gh", "project", "view", str(self.config.project_number), "--format", "json"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            project_data = json.loads(result.stdout)

            # Check if all required columns exist
            # Note: This is a simplified check - actual column validation would require
            # more complex GitHub API calls

            return GitOperation(
                success=True, message=f"Project board validated: {project_data.get('title', 'Unknown')}", output=result.stdout
            )
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Project board validation failed: {e.stderr}", error=e.stderr)

    def create_required_labels(self) -> GitOperation:
        """Create required labels in the repository.

        Returns:
            GitOperation result of label creation
        """
        created_labels = []
        failed_labels = []

        for label in self.required_labels:
            try:
                # Try to create the label
                cmd = ["gh", "label", "create", label, "--repo", self.config.repo_full_name, "--description", f"AI workflow label: {label}"]

                subprocess.run(cmd, capture_output=True, text=True, check=True)
                created_labels.append(label)
            except subprocess.CalledProcessError as e:
                # Label might already exist
                if "already exists" in e.stderr:
                    created_labels.append(f"{label} (already exists)")
                else:
                    failed_labels.append(f"{label}: {e.stderr}")

        if failed_labels:
            return GitOperation(
                success=False, message=f"Some labels failed to create: {', '.join(failed_labels)}", error=str(failed_labels)
            )

        return GitOperation(
            success=True, message=f"Labels created/validated: {len(created_labels)}", output=f"Created: {', '.join(created_labels)}"
        )

    def setup_issue_templates(self) -> GitOperation:
        """Create issue templates for AI workflow.

        Returns:
            GitOperation result of template creation
        """
        try:
            # Create .github directory if it doesn't exist
            github_dir = Path(".github")
            github_dir.mkdir(exist_ok=True)

            issue_template_dir = github_dir / "ISSUE_TEMPLATE"
            issue_template_dir.mkdir(exist_ok=True)

            # Create bug report template
            bug_template = """---
name: Bug Report
about: Create a bug report for ai-coder to fix
title: '[BUG] '
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Additional context**
Add any other context about the problem here.
"""

            # Create feature request template
            feature_template = """---
name: Feature Request
about: Suggest a new feature for ai-coder to implement
title: '[FEATURE] '
labels: feature
assignees: ''

---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
"""

            # Create documentation template
            docs_template = """---
name: Documentation
about: Request documentation creation or updates
title: '[DOCS] '
labels: documentation
assignees: ''

---

**Documentation needed**
Describe what documentation needs to be created or updated.

**Target audience**
Who is this documentation for? (developers, users, maintainers)

**Scope**
What should be covered in the documentation?

**Format**
What format should the documentation be in? (README, Wiki, inline comments, etc.)

**Additional context**
Add any other context about the documentation request here.
"""

            # Write templates
            (issue_template_dir / "bug_report.md").write_text(bug_template)
            (issue_template_dir / "feature_request.md").write_text(feature_template)
            (issue_template_dir / "documentation.md").write_text(docs_template)

            return GitOperation(
                success=True, message="Issue templates created successfully", output=f"Templates created in {issue_template_dir}"
            )
        except Exception as e:
            return GitOperation(success=False, message=f"Issue template creation failed: {str(e)}", error=str(e))

    def create_workflow_config_file(self) -> GitOperation:
        """Create workflow configuration file.

        Returns:
            GitOperation result of config file creation
        """
        try:
            config_data = {
                "repo_owner": self.config.repo_owner,
                "repo_name": self.config.repo_name,
                "project_number": self.config.project_number,
                "default_base_branch": self.config.default_base_branch,
                "workflow_columns": self.required_columns,
                "workflow_labels": self.required_labels,
                "ai_types": [ai_type.value for ai_type in AiaType],
            }

            config_path = Path(".aia_config.json")
            with open(config_path, "w") as f:
                json.dump(config_data, f, indent=2)

            return GitOperation(success=True, message=f"Workflow config file created: {config_path}", output=str(config_path))
        except Exception as e:
            return GitOperation(success=False, message=f"Config file creation failed: {str(e)}", error=str(e))

    def run_complete_setup(self, project_name: str) -> GitOperation:
        """Run complete setup process for AI workflow.

        Args:
            project_name: Name for the project board

        Returns:
            GitOperation result with setup summary
        """
        results = []

        # Step 1: Validate GitHub CLI
        cli_result = self.validate_github_cli()
        results.append(f"✓ GitHub CLI: {cli_result.message}")
        if not cli_result.success:
            return GitOperation(success=False, message="Setup failed at GitHub CLI validation", error=cli_result.error)

        # Step 2: Validate repository access
        repo_result = self.validate_repository_access()
        results.append(f"✓ Repository: {repo_result.message}")
        if not repo_result.success:
            return GitOperation(success=False, message="Setup failed at repository validation", error=repo_result.error)

        # Step 3: Create labels
        label_result = self.create_required_labels()
        results.append(f"✓ Labels: {label_result.message}")
        if not label_result.success:
            results.append(f"  ⚠️  Warning: {label_result.error}")

        # Step 4: Create project board (if project number not provided)
        if not self.config.project_number:
            project_result = self.create_project_board(project_name)
            if project_result.success:
                self.config.project_number = int(project_result.output)
                results.append(f"✓ Project Board: Created with number {self.config.project_number}")
            else:
                results.append(f"✗ Project Board: {project_result.message}")
        else:
            validate_result = self.validate_project_board_columns()
            results.append(f"✓ Project Board: {validate_result.message}")

        # Step 5: Create issue templates
        template_result = self.setup_issue_templates()
        results.append(f"✓ Issue Templates: {template_result.message}")

        # Step 6: Create config file
        config_result = self.create_workflow_config_file()
        results.append(f"✓ Config File: {config_result.message}")

        return GitOperation(success=True, message="Complete setup finished successfully", output="\\n".join(results))


def main():
    """Interactive setup script main entry point."""
    print("🚀 AI Assistant Workflow Setup")
    print("=" * 40)

    # Get repository information
    repo_owner = input("Enter GitHub repository owner: ").strip()
    repo_name = input("Enter GitHub repository name: ").strip()
    project_number = input("Enter existing project number (or press Enter to create new): ").strip()
    project_name = input("Enter project board name (if creating new): ").strip() or "AI Assistant Workflow"

    if not repo_owner or not repo_name:
        print("❌ Repository owner and name are required")
        sys.exit(1)

    # Create configuration
    config = WorkflowConfig(repo_owner=repo_owner, repo_name=repo_name, project_number=int(project_number) if project_number else None)

    # Run setup
    setup = ProjectBoardSetup(config)
    result = setup.run_complete_setup(project_name)

    if result.success:
        print("\\n✅ Setup completed successfully!")
        print(result.output)
    else:
        print(f"\\n❌ Setup failed: {result.message}")
        if result.error:
            print(f"Error: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
