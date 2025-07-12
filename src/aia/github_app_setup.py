"""GitHub App setup and configuration for AI assistant workflow.

Provides utilities for creating and configuring GitHub Apps with required permissions
for AI assistant automation, including project board management and issue handling.
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aia.models import GitOperation


@dataclass
class GitHubAppConfig:
    """Configuration for GitHub App.

    Attributes:
        app_id: GitHub App ID
        private_key_path: Path to private key file
        installation_id: Installation ID for the repository
        webhook_secret: Webhook secret for validation
    """

    app_id: str
    private_key_path: str
    installation_id: str
    webhook_secret: str


class GitHubAppSetup:
    """GitHub App setup and configuration manager."""

    def __init__(self, config_dir: str = ".github_app"):
        """Initialize GitHub App setup.

        Args:
            config_dir: Directory to store GitHub App configuration
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

    def generate_app_manifest(self) -> dict[str, Any]:
        """Generate GitHub App manifest with required permissions.

        Returns:
            GitHub App manifest dictionary
        """
        return {
            "name": "AI Assistant Workflow Bot",
            "description": "Automated AI assistant workflow management for GitHub projects",
            "url": "https://github.com/your-org/aia",
            "hook_attributes": {"url": "https://your-domain.com/webhook"},
            "redirect_url": "https://your-domain.com/auth/callback",
            "public": False,
            "default_permissions": {
                # Repository permissions
                "issues": "write",
                "pull_requests": "write",
                "contents": "write",
                "metadata": "read",
                # Project permissions
                "projects": "write",
                # Organization permissions (if needed)
                "organization_projects": "write",
            },
            "default_events": ["issues", "pull_request", "project_card", "project_column", "push"],
        }

    def create_app_manifest_file(self) -> GitOperation:
        """Create GitHub App manifest file.

        Returns:
            GitOperation result
        """
        try:
            manifest = self.generate_app_manifest()
            manifest_path = self.config_dir / "app_manifest.json"

            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)

            return GitOperation(success=True, message=f"GitHub App manifest created: {manifest_path}", output=str(manifest_path))
        except Exception as e:
            return GitOperation(success=False, message=f"Failed to create app manifest: {str(e)}", error=str(e))

    def create_github_app_from_manifest(self, manifest_path: str) -> GitOperation:
        """Create GitHub App from manifest file using GitHub CLI.

        Args:
            manifest_path: Path to manifest file

        Returns:
            GitOperation result with app creation details
        """
        try:
            # Use GitHub CLI to create app from manifest
            cmd = ["gh", "app", "create", "--from-manifest", manifest_path]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            return GitOperation(success=True, message="GitHub App created successfully", output=result.stdout)
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Failed to create GitHub App: {e.stderr}", error=e.stderr)

    def save_app_config(self, app_config: GitHubAppConfig) -> GitOperation:
        """Save GitHub App configuration to file.

        Args:
            app_config: GitHub App configuration

        Returns:
            GitOperation result
        """
        try:
            config_path = self.config_dir / "config.json"

            config_data = {
                "app_id": app_config.app_id,
                "private_key_path": app_config.private_key_path,
                "installation_id": app_config.installation_id,
                "webhook_secret": app_config.webhook_secret,
            }

            with open(config_path, "w") as f:
                json.dump(config_data, f, indent=2)

            return GitOperation(success=True, message=f"GitHub App config saved: {config_path}", output=str(config_path))
        except Exception as e:
            return GitOperation(success=False, message=f"Failed to save app config: {str(e)}", error=str(e))

    def load_app_config(self) -> GitHubAppConfig | None:
        """Load GitHub App configuration from file.

        Returns:
            GitHubAppConfig if exists, None otherwise
        """
        try:
            config_path = self.config_dir / "config.json"

            if not config_path.exists():
                return None

            with open(config_path) as f:
                config_data = json.load(f)

            return GitHubAppConfig(
                app_id=config_data["app_id"],
                private_key_path=config_data["private_key_path"],
                installation_id=config_data["installation_id"],
                webhook_secret=config_data["webhook_secret"],
            )
        except Exception:
            return None

    def validate_app_permissions(self, repo_full_name: str) -> GitOperation:
        """Validate GitHub App has required permissions for repository.

        Args:
            repo_full_name: Repository name in "owner/repo" format

        Returns:
            GitOperation result
        """
        try:
            # Check if app has access to repository
            cmd = ["gh", "api", f"/repos/{repo_full_name}/installation", "--jq", ".permissions"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            permissions = json.loads(result.stdout)

            required_permissions = {"issues": "write", "pull_requests": "write", "contents": "write", "projects": "write"}

            missing_permissions = []
            for perm, level in required_permissions.items():
                if perm not in permissions or permissions[perm] != level:
                    missing_permissions.append(f"{perm}:{level}")

            if missing_permissions:
                return GitOperation(
                    success=False, message=f"Missing permissions: {', '.join(missing_permissions)}", error="Insufficient permissions"
                )

            return GitOperation(success=True, message="All required permissions validated", output=result.stdout)
        except subprocess.CalledProcessError as e:
            return GitOperation(success=False, message=f"Permission validation failed: {e.stderr}", error=e.stderr)

    def create_environment_template(self) -> GitOperation:
        """Create .env template file with required environment variables.

        Returns:
            GitOperation result
        """
        try:
            env_template = """# GitHub App Configuration
# Copy this file to .env and fill in your values

# GitHub App ID (from GitHub App settings)
GITHUB_APP_ID=

# Path to GitHub App private key file
GITHUB_APP_PRIVATE_KEY_PATH=

# Installation ID for your repository
GITHUB_APP_INSTALLATION_ID=

# Webhook secret for validating webhooks
GITHUB_APP_WEBHOOK_SECRET=

# Repository configuration
GITHUB_REPO_OWNER=
GITHUB_REPO_NAME=
GITHUB_PROJECT_NUMBER=

# Default branch for pull requests
DEFAULT_BASE_BRANCH=main
"""

            env_path = self.config_dir / ".env.template"

            with open(env_path, "w") as f:
                f.write(env_template)

            return GitOperation(success=True, message=f"Environment template created: {env_path}", output=str(env_path))
        except Exception as e:
            return GitOperation(success=False, message=f"Failed to create environment template: {str(e)}", error=str(e))

    def setup_github_app_complete(self, repo_full_name: str) -> GitOperation:
        """Complete GitHub App setup process.

        Args:
            repo_full_name: Repository name in "owner/repo" format

        Returns:
            GitOperation result with setup summary
        """
        try:
            results = []

            # Step 1: Create app manifest
            manifest_result = self.create_app_manifest_file()
            results.append(f"✓ Manifest: {manifest_result.message}")

            # Step 2: Create environment template
            env_result = self.create_environment_template()
            results.append(f"✓ Environment template: {env_result.message}")

            # Step 3: Create setup instructions
            instructions = self._create_setup_instructions()
            results.append(f"✓ Setup instructions: {instructions}")

            return GitOperation(success=True, message="GitHub App setup completed", output="\n".join(results))
        except Exception as e:
            return GitOperation(success=False, message=f"GitHub App setup failed: {str(e)}", error=str(e))

    def _create_setup_instructions(self) -> str:
        """Create setup instructions file."""
        instructions = """# GitHub App Setup Instructions

## 1. Create GitHub App

1. Go to your GitHub repository or organization settings
2. Navigate to "Developer settings" > "GitHub Apps"
3. Click "New GitHub App"
4. Use the manifest file generated in `.github_app/app_manifest.json`
5. Or manually configure with these settings:
   - Name: AI Assistant Workflow Bot
   - Permissions: Issues (write), Pull Requests (write), Contents (write), Projects (write)
   - Events: issues, pull_request, project_card, project_column, push

## 2. Configure Environment Variables

1. Copy `.github_app/.env.template` to `.env`
2. Fill in your GitHub App credentials:
   - GITHUB_APP_ID: From GitHub App settings
   - GITHUB_APP_PRIVATE_KEY_PATH: Download private key from GitHub App settings
   - GITHUB_APP_INSTALLATION_ID: Install app to your repository and get ID
   - GITHUB_APP_WEBHOOK_SECRET: Set webhook secret in GitHub App settings

## 3. Install GitHub App

1. Go to your GitHub App settings
2. Click "Install App"
3. Choose your repository
4. Note the installation ID from URL

## 4. Validate Setup

Run: `aia validate-github-app`

This will check permissions and connectivity.
"""

        instructions_path = self.config_dir / "SETUP_INSTRUCTIONS.md"

        with open(instructions_path, "w") as f:
            f.write(instructions)

        return str(instructions_path)
