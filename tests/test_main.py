"""Unit tests for main module entry point."""

from unittest.mock import patch
from io import StringIO

from abk_aia import main


class TestMain:
    """Test main entry point."""

    @patch("sys.stdout", new_callable=StringIO)
    def test_main_function(self, mock_stdout):
        """Test main function prints expected output."""
        main()

        output = mock_stdout.getvalue()
        assert "ABK AI Assistant Interface" in output
        assert "Key features:" in output
        assert "Standardized branch naming" in output
        assert "GitHub CLI integration" in output
        assert "examples/usage_example.py" in output
        assert "CLAUDE.md" in output
