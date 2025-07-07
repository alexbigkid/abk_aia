"""Unit tests for abk_common module."""

from unittest.mock import Mock, patch

from abk_aia.abk_common import function_trace, PerformanceTimer


class TestFunctionTrace:
    """Test function_trace decorator."""

    @patch("abk_aia.abk_common.logging.getLogger")
    def test_function_trace_decorator(self, mock_get_logger):
        """Test function_trace decorator functionality."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @function_trace
        def test_function(x, y):
            return x + y

        result = test_function(1, 2)

        assert result == 3
        assert mock_logger.info.call_count == 2  # Entry and exit

        # Check log messages
        calls = mock_logger.info.call_args_list
        assert "Entering test_function" in str(calls[0])
        assert "Exiting test_function" in str(calls[1])


class TestPerformanceTimer:
    """Test PerformanceTimer context manager."""

    def test_performance_timer_with_default_logger(self):
        """Test PerformanceTimer with default logger."""
        with patch("abk_aia.abk_common.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            timer = PerformanceTimer("test_operation")
            assert timer._timer_name == "test_operation"
            assert timer._logger == mock_logger

    def test_performance_timer_with_custom_logger(self):
        """Test PerformanceTimer with custom logger."""
        custom_logger = Mock()
        timer = PerformanceTimer("test_operation", custom_logger)

        assert timer._timer_name == "test_operation"
        assert timer._logger == custom_logger

    def test_performance_timer_context_manager(self):
        """Test PerformanceTimer as context manager."""
        mock_logger = Mock()

        with patch("abk_aia.abk_common.timeit.default_timer", side_effect=[1.0, 1.1]), PerformanceTimer("test_operation", mock_logger):
            # Simulate some work
            pass

        # Check that logger.info was called with timing information
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "Executing test_operation took" in call_args
        assert "ms" in call_args

    def test_performance_timer_timing_calculation(self):
        """Test accurate timing calculation."""
        mock_logger = Mock()

        # Mock timer to return specific values
        with patch("abk_aia.abk_common.timeit.default_timer", side_effect=[1.0, 1.05]), PerformanceTimer("test_operation", mock_logger):
            pass

        # Should log 50ms (0.05 seconds * 1000)
        call_args = mock_logger.info.call_args[0][0]
        assert "50." in call_args and "ms" in call_args
