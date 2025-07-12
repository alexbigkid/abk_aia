#!/usr/bin/env python3
"""Setup script for deploying AI assistant workflow to any GitHub repository.

This script allows you to clone aia into any repository and quickly configure
the AI assistant workflow for that specific repository.
"""

import json
import subprocess
import sys
from pathlib import Path


def get_current_repo_info() -> tuple[str, str]:
    """Get current repository owner and name from git remote."""
    try:
        # Get remote URL
        result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True)

        remote_url = result.stdout.strip()

        # Parse GitHub URL - handle both HTTPS and SSH
        if remote_url.startswith("https://github.com/"):
            # https://github.com/owner/repo.git
            repo_part = remote_url.replace("https://github.com/", "").replace(".git", "")
        elif remote_url.startswith("git@github.com:"):
            # git@github.com:owner/repo.git
            repo_part = remote_url.replace("git@github.com:", "").replace(".git", "")
        else:
            raise ValueError(f"Unsupported remote URL format: {remote_url}")

        owner, repo_name = repo_part.split("/")
        return owner, repo_name

    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting git remote: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error parsing repository info: {e}")
        sys.exit(1)


def check_github_cli() -> bool:
    """Check if GitHub CLI is installed and authenticated."""
    try:
        subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_project_boards(owner: str, repo: str) -> list[dict]:
    """Get available project boards for the repository."""
    try:
        # List organization/user projects
        cmd = ["gh", "project", "list", "--owner", owner, "--format", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        projects = json.loads(result.stdout)
        return projects

    except subprocess.CalledProcessError:
        return []


def create_project_board(owner: str, repo: str) -> int | None:
    """Create a new project board for AI workflow."""
    print("🔧 Creating new project board for AI workflow...")

    try:
        # Create project
        cmd = ["gh", "project", "create", "--owner", owner, "--title", f"{repo} - AI Assistant Workflow", "--format", "json"]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        project_data = json.loads(result.stdout)
        project_number = project_data["number"]

        print(f"✅ Created project board #{project_number}")
        return project_number

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create project board: {e.stderr}")
        return None


def setup_repository_workflow():
    """Main setup function for repository AI workflow."""
    print("🚀 Setting up AI Assistant Workflow for Repository")
    print("=" * 50)

    # Check prerequisites
    if not check_github_cli():
        print("❌ GitHub CLI not installed or not authenticated")
        print("Please run: gh auth login")
        sys.exit(1)

    print("✅ GitHub CLI authenticated")

    # Get current repository info
    try:
        owner, repo_name = get_current_repo_info()
        print(f"📁 Repository: {owner}/{repo_name}")
    except Exception:
        # Fallback to manual input
        print("Could not auto-detect repository. Please enter manually:")
        owner = input("Repository owner: ").strip()
        repo_name = input("Repository name: ").strip()

    if not owner or not repo_name:
        print("❌ Repository owner and name are required")
        sys.exit(1)

    # Check if repository exists and we have access
    try:
        cmd = ["gh", "repo", "view", f"{owner}/{repo_name}"]
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✅ Repository access confirmed: {owner}/{repo_name}")
    except subprocess.CalledProcessError:
        print(f"❌ Cannot access repository {owner}/{repo_name}")
        print("Please check repository name and permissions")
        sys.exit(1)

    # Get or create project board
    print("\n🔍 Checking for existing project boards...")
    projects = get_project_boards(owner, repo_name)

    project_number = None

    if projects:
        print(f"Found {len(projects)} existing project boards:")
        for i, project in enumerate(projects):
            print(f"  {i + 1}. {project['title']} (#{project['number']})")

        print(f"  {len(projects) + 1}. Create new project board")

        while True:
            try:
                choice = input(f"\\nSelect project board (1-{len(projects) + 1}): ").strip()
                choice_num = int(choice)

                if 1 <= choice_num <= len(projects):
                    project_number = projects[choice_num - 1]["number"]
                    print(f"✅ Using existing project #{project_number}")
                    break
                elif choice_num == len(projects) + 1:
                    project_number = create_project_board(owner, repo_name)
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
    else:
        print("No existing project boards found.")
        create_new = input("Create new project board? (y/n): ").strip().lower()
        if create_new in ["y", "yes"]:
            project_number = create_project_board(owner, repo_name)
        else:
            print("⚠️  Continuing without project board (limited functionality)")

    # Create configuration
    config_data = {
        "repo_owner": owner,
        "repo_name": repo_name,
        "project_number": project_number,
        "default_base_branch": "main",
        "workflow_columns": ["🔍 Triage", "📋 ToDo", "🔄 Doing", "👀 Review", "🧪 Testing", "✅ Done"],
        "ai_types": ["ai-coder", "ai-reviewer", "ai-tester", "ai-researcher", "ai-marketeer"],
    }

    # Save configuration
    config_path = Path(".aia_config.json")
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)

    print(f"\\n✅ Configuration saved to {config_path}")

    # Create required labels
    print("\\n🏷️  Setting up repository labels...")
    required_labels = [
        ("bug", "d73a4a", "Something isn't working"),
        ("documentation", "0075ca", "Improvements or additions to documentation"),
        ("feature", "a2eeef", "New feature or request"),
        ("research", "d4c5f9", "Research task"),
        ("test", "c5def5", "Testing related"),
        ("assigned:ai-coder", "bfd4f2", "Assigned to AI coder"),
        ("assigned:ai-reviewer", "fef2c0", "Assigned to AI reviewer"),
        ("assigned:ai-tester", "f9c2ff", "Assigned to AI tester"),
        ("assigned:ai-researcher", "c2e0c6", "Assigned to AI researcher"),
        ("assigned:ai-marketeer", "ff9aa2", "Assigned to AI marketeer"),
    ]

    created_count = 0
    for label_name, color, description in required_labels:
        try:
            cmd = ["gh", "label", "create", label_name, "--repo", f"{owner}/{repo_name}", "--color", color, "--description", description]
            subprocess.run(cmd, capture_output=True, check=True)
            created_count += 1
        except subprocess.CalledProcessError:
            # Label probably already exists
            pass

    print(f"✅ Repository labels configured ({created_count} new labels created)")

    # Create .gitignore entry for aia if needed
    gitignore_path = Path(".gitignore")
    gitignore_entry = "# AI Assistant Workflow\\n.aia_config.json\\n.github_app/\\n"

    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if ".aia_config.json" not in content:
            with open(gitignore_path, "a") as f:
                f.write(f"\\n{gitignore_entry}")
            print("✅ Updated .gitignore")
    else:
        gitignore_path.write_text(gitignore_entry)
        print("✅ Created .gitignore")

    # Final instructions
    print("\\n🎉 AI Assistant Workflow Setup Complete!")
    print("=" * 50)
    print("\\n📋 Next Steps:")
    print("1. Validate setup: aia validate")
    print("2. Check status: aia status")
    print("3. Create test issue: aia create-issue")
    print("4. Trigger AI coder: aia trigger ai-coder")
    print("\\n📚 Documentation:")
    print("- View commands: aia --help")
    print("- Read CLAUDE.md for detailed usage")

    if project_number:
        print(f"\\n🔗 Project Board: https://github.com/users/{owner}/projects/{project_number}")


if __name__ == "__main__":
    setup_repository_workflow()
