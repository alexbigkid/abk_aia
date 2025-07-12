#!/bin/bash
# AI Assistant Workflow - Installation Script
# This script installs the AI workflow system for use across multiple repositories

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo -e "${BLUE}"
echo "🚀 AI Assistant Workflow - Installation"
echo "=========================================="
echo -e "${NC}"

# Check if we're in the aia repository
if [[ ! -f "src/aia/__init__.py" ]]; then
    print_error "This script must be run from the aia repository root"
    exit 1
fi

print_info "Installing AI Assistant Workflow..."

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.13"

if [[ $(echo "$python_version >= $required_version" | bc -l) -eq 1 ]]; then
    print_status "Python $python_version detected (>= $required_version required)"
else
    print_error "Python $required_version or higher required. Found: $python_version"
    exit 1
fi

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    print_status "GitHub CLI (gh) is installed"
    
    # Check if authenticated
    if gh auth status &> /dev/null; then
        print_status "GitHub CLI is authenticated"
    else
        print_warning "GitHub CLI is not authenticated. Run 'gh auth login' after installation"
    fi
else
    print_warning "GitHub CLI (gh) not found. Install from: https://cli.github.com/"
fi

# Install package in development mode
print_info "Installing package in development mode..."
if pip install -e .; then
    print_status "Package installed successfully"
else
    print_error "Package installation failed"
    exit 1
fi

# Install development dependencies (optional)
read -p "Install development dependencies? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Installing development dependencies..."
    if pip install -e ".[dev]"; then
        print_status "Development dependencies installed"
    else
        print_warning "Development dependencies installation failed (continuing anyway)"
    fi
fi

# Create global alias (optional)
echo
print_info "Creating global alias for easy access..."
shell_rc=""
if [[ -f "$HOME/.bashrc" ]]; then
    shell_rc="$HOME/.bashrc"
elif [[ -f "$HOME/.zshrc" ]]; then
    shell_rc="$HOME/.zshrc"
fi

if [[ -n "$shell_rc" ]]; then
    # Check if alias already exists
    if ! grep -q "alias aia=" "$shell_rc"; then
        echo "alias aia='python -m aia'" >> "$shell_rc"
        print_status "Added 'aia' alias to $shell_rc"
        print_info "Run 'source $shell_rc' or restart your terminal to use the alias"
    else
        print_status "Alias already exists in $shell_rc"
    fi
else
    print_warning "Could not find shell configuration file to add alias"
fi

# Make setup script executable
chmod +x scripts/setup_repo_workflow.py
print_status "Made setup script executable"

# Run tests to verify installation
echo
print_info "Running tests to verify installation..."
if python -m pytest --no-cov -q; then
    print_status "All tests passed - installation verified"
else
    print_warning "Some tests failed, but installation should still work"
fi

# Show next steps
echo
echo -e "${GREEN}🎉 Installation Complete!${NC}"
echo
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Navigate to any GitHub repository:"
echo "   cd /path/to/your/repo"
echo
echo "2. Set up AI workflow for that repository:"
echo "   aia setup"
echo "   # or python -m aia setup"
echo
echo "3. Validate the setup:"
echo "   aia validate"
echo
echo "4. Check repository status:"
echo "   aia info"
echo "   aia status"
echo
echo -e "${BLUE}Multi-Repository Usage:${NC}"
echo "• Each repository gets its own configuration"
echo "• Use 'aia info' to see current repository context"
echo "• Read DEPLOYMENT.md for advanced deployment patterns"
echo
echo -e "${BLUE}Documentation:${NC}"
echo "• Commands: aia --help"
echo "• Usage: cat CLAUDE.md"
echo "• Deployment: cat DEPLOYMENT.md"
echo
echo -e "${YELLOW}Note: If you don't have the alias, use 'python -m aia' instead of 'aia'${NC}"