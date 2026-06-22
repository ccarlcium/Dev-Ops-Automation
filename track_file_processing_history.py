"""Record file processing events to a CSV pipeline log."""
from __future__ import annotations
from typing import Optional, Any, Dict
from logging_utils import _write_row, _now_ts


def track_file_processing_history(csv_file: str, file_path: str, status: str, details: Optional[str] = None) -> None:
    """Append a file processing event to `csv_file`.

    `status` examples: 'started', 'completed', 'failed'.
    """
    row: Dict[str, Any] = {
        'timestamp': _now_ts(),
        'level': 'INFO',
        'event': 'file_processing',
        'function_name': '',
        'duration_ms': '',
        'file_path': file_path,
        'status': status,
        'details': details or ''
    }
    _write_row(csv_file, row)
