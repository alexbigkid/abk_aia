#!/usr/bin/env python3
"""Test runner script for ABK AIA project."""

import subprocess
import sys


def run_command(command, description):
    """Run a command and print results."""
    print(f"\n🔧 {description}")
    print("=" * (len(description) + 4))

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def main():
    """Run all tests and checks."""
    print("🧪 ABK AIA Test Suite")
    print("=" * 20)

    commands = [
        ("uv run pytest -v --no-cov", "Running pytest unit tests"),
        ("uv run pytest --cov --cov-report=xml", "Running tests with coverage"),
        ("uv run ruff check src tests", "Running ruff linting"),
        ("uv run ruff format --check src tests", "Checking code formatting"),
    ]

    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1

    print(f"\n📊 Results: {success_count}/{len(commands)} checks passed")

    if success_count == len(commands):
        print("✅ All tests and checks passed!")
        return 0
    else:
        print("❌ Some tests or checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
