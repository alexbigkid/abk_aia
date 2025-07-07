"""Test configuration and shared fixtures."""

import pytest
from datetime import datetime
from unittest.mock import Mock

from abk_aia.models import Issue, WorkflowConfig, WorkflowStatus, IssueState


@pytest.fixture
def sample_config():
    """Create a sample WorkflowConfig for testing."""
    return WorkflowConfig(repo_owner="test-owner", repo_name="test-repo", project_number=1, default_base_branch="main")


@pytest.fixture
def sample_issue():
    """Create a sample Issue for testing."""
    return Issue(
        number=123,
        title="Test issue title",
        body="Test issue body",
        state=IssueState.OPEN,
        labels=["feature", "priority:high"],
        assignees=["test-user"],
        created_at=datetime(2025, 1, 1, 12, 0, 0),
        updated_at=datetime(2025, 1, 1, 12, 30, 0),
        url="https://github.com/test-owner/test-repo/issues/123",
        project_status=WorkflowStatus.TODO,
    )


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for testing."""
    mock = Mock()
    mock.stdout = ""
    mock.stderr = ""
    mock.returncode = 0
    return mock
