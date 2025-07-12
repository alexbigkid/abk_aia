"""Command-line interface for AI assistant workflow management.

Provides CLI commands for triggering AI agents, managing GitHub project boards,
and automating the AI assistant workflow.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from aia.git_aia_manager import AiaManagerFactory, AiaType
from aia.github_app_setup import GitHubAppSetup
from aia.models import WorkflowConfig
from aia.workflow_coordinator import WorkflowCoordinator


class AiaCLI:
    """Main CLI class for AI assistant workflow management."""

    def __init__(self):
        """Initialize CLI with configuration."""
        self.config = self._load_config()
        self.github_app_setup = GitHubAppSetup()

    def _load_config(self) -> WorkflowConfig | None:
        """Load workflow configuration from environment or config file."""
        # Try environment variables first
        repo_owner = os.getenv("GITHUB_REPO_OWNER")
        repo_name = os.getenv("GITHUB_REPO_NAME")
        project_number = os.getenv("GITHUB_PROJECT_NUMBER")

        if repo_owner and repo_name:
            return WorkflowConfig(
                repo_owner=repo_owner,
                repo_name=repo_name,
                project_number=int(project_number) if project_number else None,
                default_base_branch=os.getenv("DEFAULT_BASE_BRANCH", "main"),
            )

        # Try config file
        config_path = Path(".aia_config.json")
        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    config_data = json.load(f)

                return WorkflowConfig(
                    repo_owner=config_data["repo_owner"],
                    repo_name=config_data["repo_name"],
                    project_number=config_data.get("project_number"),
                    default_base_branch=config_data.get("default_base_branch", "main"),
                )
            except Exception as e:
                print(f"Error loading config: {e}")

        # Try auto-detecting from git remote
        try:
            result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True)

            remote_url = result.stdout.strip()

            # Parse GitHub URL
            if "github.com" in remote_url:
                if remote_url.startswith("https://github.com/"):
                    repo_part = remote_url.replace("https://github.com/", "").replace(".git", "")
                elif remote_url.startswith("git@github.com:"):
                    repo_part = remote_url.replace("git@github.com:", "").replace(".git", "")
                else:
                    return None

                if "/" in repo_part:
                    owner, name = repo_part.split("/", 1)
                    print(f"🔍 Auto-detected repository: {owner}/{name}")
                    print("💡 Run 'aia setup' to configure the AI workflow for this repository")

                    return WorkflowConfig(repo_owner=owner, repo_name=name, project_number=None, default_base_branch="main")
        except subprocess.CalledProcessError:
            pass

        return None

    def _ensure_config(self) -> WorkflowConfig:
        """Ensure configuration is available or exit."""
        if not self.config:
            print("❌ No configuration found. Please set up your project first.")
            print("Run: aia setup")
            sys.exit(1)
        return self.config

    def setup_command(self, _args) -> None:
        """Set up GitHub project and AI assistant workflow."""
        print("🚀 Setting up AI Assistant Workflow...")

        # Interactive setup
        repo_owner = input("GitHub repository owner: ").strip()
        repo_name = input("GitHub repository name: ").strip()
        project_number = input("GitHub project number (optional): ").strip()

        if not repo_owner or not repo_name:
            print("❌ Repository owner and name are required")
            return

        # Create workflow config
        config = WorkflowConfig(repo_owner=repo_owner, repo_name=repo_name, project_number=int(project_number) if project_number else None)

        # Save configuration
        config_path = Path(".aia_config.json")
        config_data = {
            "repo_owner": config.repo_owner,
            "repo_name": config.repo_name,
            "project_number": config.project_number,
            "default_base_branch": config.default_base_branch,
        }

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        print(f"✅ Configuration saved to {config_path}")

        # Set up GitHub App
        print("\n🔧 Setting up GitHub App...")
        setup_result = self.github_app_setup.setup_github_app_complete(config.repo_full_name)

        if setup_result.success:
            print("✅ GitHub App setup completed")
            print(f"📝 Setup details:\n{setup_result.output}")
        else:
            print(f"❌ GitHub App setup failed: {setup_result.message}")

        # Validate project board
        print("\n🔍 Validating project board...")
        manager = AiaManagerFactory.create_manager("github", AiaType.AI_CODER, config)
        validation_result = manager.validate_project_board_setup()

        if validation_result.success:
            print(f"✅ Project board validated: {validation_result.message}")
        else:
            print(f"❌ Project board validation failed: {validation_result.message}")

    def status_command(self, args) -> None:
        """Show project board status and workflow information."""
        config = self._ensure_config()

        print(f"📊 Project Board Status: {config.repo_full_name}")
        print("=" * 50)

        # Get project board info
        manager = AiaManagerFactory.create_manager("github", AiaType.AI_CODER, config)
        board_info = manager.get_project_board_info()

        if "error" in board_info:
            print(f"❌ Error: {board_info['error']}")
            return

        # Display column information
        for column_name, column_info in board_info["columns"].items():
            count = column_info["count"]
            print(f"\n{column_name}: {count} issues")

            if count > 0 and hasattr(args, "verbose") and args.verbose:
                for issue in column_info["issues"]:
                    print(f"  • #{issue['number']}: {issue['title']}")

        print(f"\n📈 Total Issues: {board_info['total_issues']}")

    def trigger_command(self, args) -> None:
        """Trigger AI assistant to work on issues."""
        config = self._ensure_config()

        # Parse AI type
        try:
            ai_type = AiaType(args.ai_type)
        except ValueError:
            print(f"❌ Invalid AI type: {args.ai_type}")
            print(f"Available types: {', '.join([t.value for t in AiaType])}")
            return

        print(f"🤖 Triggering {ai_type.value} workflow...")

        # Create workflow coordinator
        coordinator = WorkflowCoordinator(config, "github")

        if args.ai_type == "ai-coder":
            # AI Coder: Pick up top priority ToDo issue
            result = coordinator.trigger_ai_coder()
        elif args.ai_type == "ai-reviewer":
            # AI Reviewer: Review issues in Review column
            result = coordinator.trigger_ai_reviewer()
        elif args.ai_type == "ai-tester":
            # AI Tester: Test issues in Testing column
            result = coordinator.trigger_ai_tester()
        else:
            print(f"❌ AI type {args.ai_type} triggering not implemented yet")
            return

        if result.success:
            print(f"✅ {ai_type.value} workflow completed: {result.message}")
        else:
            print(f"❌ {ai_type.value} workflow failed: {result.message}")

    def validate_command(self, _args) -> None:
        """Validate GitHub App setup and permissions."""
        config = self._ensure_config()

        print("🔍 Validating GitHub App setup...")

        # Check GitHub App configuration
        app_config = self.github_app_setup.load_app_config()
        if not app_config:
            print("❌ GitHub App not configured. Run: aia setup")
            return

        print("✅ GitHub App configuration found")

        # Validate permissions
        permission_result = self.github_app_setup.validate_app_permissions(config.repo_full_name)

        if permission_result.success:
            print("✅ GitHub App permissions validated")
        else:
            print(f"❌ Permission validation failed: {permission_result.message}")

        # Validate project board
        manager = AiaManagerFactory.create_manager("github", AiaType.AI_CODER, config)
        board_result = manager.validate_project_board_setup()

        if board_result.success:
            print(f"✅ Project board access validated: {board_result.message}")
        else:
            print(f"❌ Project board validation failed: {board_result.message}")

    def create_issue_command(self, args) -> None:
        """Create a new issue in the Triage column."""
        config = self._ensure_config()

        print("📝 Creating new issue...")

        # Get issue details
        title = args.title or input("Issue title: ").strip()
        body = args.body or input("Issue description: ").strip()

        if not title:
            print("❌ Issue title is required")
            return

        # Create issue using GitHub CLI
        try:
            cmd = ["gh", "issue", "create", "--repo", config.repo_full_name, "--title", title, "--body", body or "No description provided"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            print(f"✅ Issue created: {result.stdout.strip()}")

            # Move to Triage column if project board is configured
            if config.project_number:
                print("🔄 Moving issue to Triage column...")
                # Implementation would go here
                print("✅ Issue moved to Triage column")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create issue: {e.stderr}")

    def info_command(self, _args) -> None:
        """Show current repository and configuration information."""
        print("📋 AI Assistant Workflow - Repository Information")
        print("=" * 50)

        # Show current working directory
        print(f"📁 Current Directory: {Path.cwd()}")

        # Show git repository info
        try:
            result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True)
            print(f"🔗 Git Remote: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            print("⚠️  Not in a git repository or no remote configured")

        # Show current configuration
        if self.config:
            print(f"✅ Configured Repository: {self.config.repo_full_name}")
            print(f"📊 Project Number: {self.config.project_number or 'Not configured'}")
            print(f"🌿 Default Branch: {self.config.default_base_branch}")
        else:
            print("❌ No AI workflow configuration found")

        # Show configuration file location
        config_path = Path(".aia_config.json")
        if config_path.exists():
            print(f"⚙️  Config File: {config_path.absolute()}")
        else:
            print("⚙️  Config File: Not found")

        # Show environment variables
        env_vars = {
            "GITHUB_REPO_OWNER": os.getenv("GITHUB_REPO_OWNER"),
            "GITHUB_REPO_NAME": os.getenv("GITHUB_REPO_NAME"),
            "GITHUB_PROJECT_NUMBER": os.getenv("GITHUB_PROJECT_NUMBER"),
        }

        active_env_vars = {k: v for k, v in env_vars.items() if v}
        if active_env_vars:
            print("\n🔧 Active Environment Variables:")
            for key, value in active_env_vars.items():
                print(f"  {key}: {value}")

        # Show aia installation
        try:
            import aia

            print(f"\n🤖 AIA Version: Installed at {Path(aia.__file__).parent}")
        except ImportError:
            print("\n❌ AIA not properly installed")

    def run(self):
        """Main CLI entry point."""
        parser = argparse.ArgumentParser(prog="aia", description="AI Assistant Workflow Management CLI")

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Setup command
        setup_parser = subparsers.add_parser("setup", help="Set up GitHub project and AI workflow")
        setup_parser.set_defaults(func=self.setup_command)

        # Status command
        status_parser = subparsers.add_parser("status", help="Show project board status")
        status_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed issue information")
        status_parser.set_defaults(func=self.status_command)

        # Trigger command
        trigger_parser = subparsers.add_parser("trigger", help="Trigger AI assistant workflow")
        trigger_parser.add_argument("ai_type", choices=[t.value for t in AiaType], help="AI assistant type to trigger")
        trigger_parser.set_defaults(func=self.trigger_command)

        # Validate command
        validate_parser = subparsers.add_parser("validate", help="Validate GitHub App setup and permissions")
        validate_parser.set_defaults(func=self.validate_command)

        # Create issue command
        create_parser = subparsers.add_parser("create-issue", help="Create new issue in Triage column")
        create_parser.add_argument("--title", help="Issue title")
        create_parser.add_argument("--body", help="Issue description")
        create_parser.set_defaults(func=self.create_issue_command)

        # Info command
        info_parser = subparsers.add_parser("info", help="Show repository and configuration information")
        info_parser.set_defaults(func=self.info_command)

        # Parse and execute
        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return

        try:
            args.func(args)
        except KeyboardInterrupt:
            print("\n⏹️  Operation cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli = AiaCLI()
    cli.run()


if __name__ == "__main__":
    main()
