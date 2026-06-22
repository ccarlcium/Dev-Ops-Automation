"""Create pipeline log CSV file with headers."""
from __future__ import annotations
import os
import csv
from logging_utils import DEFAULT_HEADERS, _ensure_dir_exists


def create_pipeline_log(csv_file: str) -> str:
    """Create a CSV file at `csv_file` with the pipeline log headers and return absolute path."""
    _ensure_dir_exists(csv_file)
    with open(csv_file, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=DEFAULT_HEADERS)
        writer.writeheader()
    return os.path.abspath(csv_file)
