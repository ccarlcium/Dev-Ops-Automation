"""Decorator to log execution time of functions into a CSV log."""
from __future__ import annotations
import time
import functools
from typing import Optional, Callable, Any
from logging_utils import _write_row, _now_ts
import os


def log_execution_time(csv_file: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory that logs function execution events to `csv_file`.

    Usage:
      @log_execution_time()  # logs to ./pipeline_log.csv
      @log_execution_time('logs.csv')
    """
    if csv_file is None:
        csv_file = os.path.join(os.getcwd(), 'pipeline_log.csv')

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_ts = _now_ts()
            start = time.perf_counter()
            success = True
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                end = time.perf_counter()
                duration_ms = int((end - start) * 1000)
                _write_row(csv_file, {
                    'timestamp': start_ts,
                    'level': 'INFO' if success else 'ERROR',
                    'event': 'execution',
                    'function_name': func.__name__,
                    'duration_ms': duration_ms,
                    'details': '' if success else 'exception',
                })
        return wrapper
    return decorator
