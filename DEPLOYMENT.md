# AI Assistant Workflow - Multi-Repository Deployment Guide

This guide explains how to deploy the AI assistant workflow to any GitHub repository.

## Quick Deployment

### Option 1: Git Submodule (Recommended)

Add `aia` as a submodule to any repository:

```bash
# Navigate to your target repository
cd /path/to/your/repo

# Add aia as a submodule
git submodule add https://github.com/alexbigkid/aia.git .aia

# Initialize and update the submodule
git submodule update --init --recursive

# Run the setup script
python .aia/scripts/setup_repo_workflow.py

# Add aia to your PATH (or use full path)
export PATH="$PATH:$(pwd)/.aia/src"

# Validate setup
python -m aia validate
```

### Option 2: Direct Clone

Clone `aia` directly into your repository:

```bash
# Navigate to your target repository
cd /path/to/your/repo

# Clone aia
git clone https://github.com/alexbigkid/aia.git .aia

# Run setup
python .aia/scripts/setup_repo_workflow.py

# Install dependencies
cd .aia && pip install -e . && cd ..

# Use the workflow
python .aia/src/aia/cli.py status
```

### Option 3: System-wide Installation

Install `aia` globally and use in any repository:

```bash
# Clone and install globally
git clone https://github.com/alexbigkid/aia.git
cd aia
pip install -e .

# Now use in any repository
cd /path/to/any/repo
aia setup
```

## Multi-Repository Workflow

### 1. Repository Structure

Each repository gets its own configuration:

```
your-repo/
├── .aia_config.json      # Repository-specific config
├── .github_app/              # GitHub App credentials (optional)
├── .aia/                 # AI workflow system (submodule/clone)
└── your-project-files...
```

### 2. Configuration Management

Each repository maintains its own `.aia_config.json`:

```json
{
  "repo_owner": "your-username",
  "repo_name": "current-repo-name",
  "project_number": 123,
  "default_base_branch": "main",
  "workflow_columns": ["🔍 Triage", "📋 ToDo", "🔄 Doing", "👀 Review", "🧪 Testing", "✅ Done"],
  "ai_types": ["ai-coder", "ai-reviewer", "ai-tester", "ai-researcher", "ai-marketeer"]
}
```

### 3. GitHub App Setup (Optional)

For advanced features, set up a GitHub App once and reuse across repositories:

```bash
# Set up GitHub App in any repository
aia setup

# Copy credentials to other repositories
cp .github_app/config.json /path/to/other/repo/.github_app/
```

## Usage Patterns

### Pattern 1: Dedicated AI Repository

Keep `aia` in a dedicated repository and reference it:

```bash
# In your main development directory
git clone https://github.com/alexbigkid/aia.git

# Create alias for easy access
alias aia='python /path/to/aia/src/aia/cli.py'

# Use in any repository
cd /path/to/project1 && aia setup
cd /path/to/project2 && aia setup
```

### Pattern 2: Per-Project Integration

Each project includes its own copy of the AI workflow:

```bash
# Add to each project as needed
cd project1 && git submodule add https://github.com/alexbigkid/aia.git .aia
cd project2 && git submodule add https://github.com/alexbigkid/aia.git .aia
```

### Pattern 3: Organization-wide Deployment

Deploy across all repositories in an organization:

```bash
#!/bin/bash
# deploy_ai_workflow.sh

REPOS=("repo1" "repo2" "repo3")
ORG="your-org"

for repo in "${REPOS[@]}"; do
    echo "Setting up AI workflow for $ORG/$repo"
    git clone "https://github.com/$ORG/$repo.git"
    cd "$repo"

    # Add as submodule
    git submodule add https://github.com/alexbigkid/aia.git .aia

    # Run setup
    python .aia/scripts/setup_repo_workflow.py

    # Commit changes
    git add .
    git commit -m "Add AI assistant workflow"
    git push

    cd ..
done
```

## Repository-Specific Features

### Automatic Repository Detection

The system automatically detects the current repository:

```bash
cd /path/to/any/repo
aia status  # Automatically works with current repo
```

### Cross-Repository Issue Management

Work with issues across multiple repositories:

```bash
# Set environment variables for specific repo
export GITHUB_REPO_OWNER=other-user
export GITHUB_REPO_NAME=other-repo
aia status  # Now works with other-user/other-repo
```

### Project Board Sharing

Share project boards across related repositories:

```json
{
  "repo_owner": "team",
  "repo_name": "frontend",
  "project_number": 42,  // Same project board for multiple repos
  "default_base_branch": "develop"
}
```

## Best Practices

### 1. Repository Isolation

- Keep configurations separate per repository
- Use `.gitignore` to exclude sensitive credentials
- Use project-specific GitHub Apps when needed

### 2. Team Collaboration

- Share project board numbers across team members
- Use consistent branch naming conventions
- Document AI workflow usage in repository READMEs

### 3. Credential Management

```bash
# Use environment variables for CI/CD
export GITHUB_REPO_OWNER=org
export GITHUB_REPO_NAME=repo
export GITHUB_PROJECT_NUMBER=123

# Or use repository-specific config files
cp .aia_config.template.json .aia_config.json
# Edit with repository-specific values
```

### 4. Updating Across Repositories

```bash
# Update all submodules
find . -name ".aia" -type d -exec git -C {} pull origin main \\;

# Or use git submodule update
git submodule update --remote --recursive
```

## Example Multi-Repo Setup

```bash
# Your development directory structure
~/dev/
├── aia/                 # Main AI workflow repository
├── project-frontend/
│   ├── .aia/           # Submodule pointing to aia
│   └── .aia_config.json # Frontend-specific config
├── project-backend/
│   ├── .aia/           # Submodule pointing to aia
│   └── .aia_config.json # Backend-specific config
└── project-mobile/
    ├── .aia/           # Submodule pointing to aia
    └── .aia_config.json # Mobile-specific config
```

## Troubleshooting

### Issue: Command not found
```bash
# Add to PATH or use full path
export PATH="$PATH:/path/to/aia/src"
# Or
python /path/to/aia/src/aia/cli.py status
```

### Issue: Wrong repository detected
```bash
# Override with environment variables
export GITHUB_REPO_OWNER=correct-owner
export GITHUB_REPO_NAME=correct-repo
aia status
```

### Issue: Project board access
```bash
# Validate permissions
aia validate
# Re-run setup if needed
python .aia/scripts/setup_repo_workflow.py
```

## Migration Guide

### From Single Repo to Multi-Repo

1. **Export current configuration**:
   ```bash
   cp .aia_config.json aia_template.json
   ```

2. **Deploy to new repositories**:
   ```bash
   cd /path/to/new/repo
   cp /path/to/aia_template.json .aia_config.json
   # Edit repo_owner and repo_name
   ```

3. **Update project boards** as needed for each repository.

The AI assistant workflow is now ready to work across all your GitHub repositories! 🚀
