"""Common functionality."""

# Standard library imports
import logging
import timeit


# -----------------------------------------------------------------------------
# functions
# -----------------------------------------------------------------------------
def function_trace(original_function):
    """Decorator function to help to trace function call entry and exit.

    Args:
        original_function (_type_): function above which the decorator is defined
    """

    def function_wrapper(*args, **kwargs):
        _logger = logging.getLogger(original_function.__name__)
        _logger.info(f"Entering {original_function.__name__}")
        result = original_function(*args, **kwargs)
        _logger.info(f"Exiting {original_function.__name__}")
        return result

    return function_wrapper


class PerformanceTimer:
    """Performance Times class."""

    def __init__(self, timer_name: str, pt_logger: logging.Logger = None):
        """Init for performance timer."""
        self._timer_name = timer_name
        self._logger = pt_logger or logging.getLogger(__name__)

    def __enter__(self):
        """Enter for performance timer."""
        self.start = timeit.default_timer()

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit for performance timer."""
        time_took = (timeit.default_timer() - self.start) * 1000.0
        self._logger.info(f"Executing {self._timer_name} took {str(time_took)} ms")


if __name__ == "__main__":
    raise Exception(f"{__file__}: This module should not be executed directly. Only for imports")
