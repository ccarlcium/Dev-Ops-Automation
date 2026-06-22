"""Append validation errors to a CSV pipeline log."""
from __future__ import annotations
from typing import Iterable, Dict, Any, Optional
from logging_utils import _write_row, _now_ts


def log_validation_errors(csv_file: str, errors: Optional[Iterable[Dict[str, Any]]] = None) -> None:
    """Append validation errors to `csv_file`.

    Each error should be a dict with optional keys: file_path, details, function_name.
    """
    if not errors:
        return
    for e in errors:
        row = {
            'timestamp': _now_ts(),
            'level': 'ERROR',
            'event': 'validation_error',
            'function_name': e.get('function_name') if isinstance(e, dict) else '',
            'details': e.get('details') if isinstance(e, dict) else str(e),
            'file_path': e.get('file_path') if isinstance(e, dict) else '',
            'status': ''
        }
        _write_row(csv_file, row)
