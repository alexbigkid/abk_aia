"""Unit tests for main module entry point."""

from unittest.mock import patch

from aia import main


class TestMain:
    """Test main entry point."""

    @patch("aia.cli.AiaCLI.run")
    def test_main_function(self, mock_cli_run):
        """Test main function calls CLI."""
        main()
        mock_cli_run.assert_called_once()

    @patch("sys.argv", ["aia", "--help"])
    @patch("aia.cli.AiaCLI.run")
    def test_main_with_help(self, mock_cli_run):
        """Test main function with help argument."""
        main()
        mock_cli_run.assert_called_once()
