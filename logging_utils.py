"""Shared helpers for CSV-based pipeline logging modules."""
from __future__ import annotations
import csv
import os
import datetime
from typing import Any, Dict

DEFAULT_HEADERS = [
    "timestamp",
    "level",
    "event",
    "function_name",
    "duration_ms",
    "file_path",
    "status",
    "details",
]


def _ensure_dir_exists(path: str) -> None:
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def _write_row(csv_file: str, row: Dict[str, Any]) -> None:
    _ensure_dir_exists(csv_file)
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, "a", newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=DEFAULT_HEADERS)
        if not file_exists:
            writer.writeheader()
        out = {k: '' for k in DEFAULT_HEADERS}
        for k, v in row.items():
            out[k] = v if v is not None else ''
        writer.writerow(out)


def _now_ts() -> str:
    return datetime.datetime.utcnow().isoformat() + 'Z'
