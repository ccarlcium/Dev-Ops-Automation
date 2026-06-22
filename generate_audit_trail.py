"""Generate a simple audit trail summary from a pipeline CSV log."""
from __future__ import annotations
import csv
import os
from typing import Optional, Dict, Any
from logging_utils import _ensure_dir_exists


def generate_audit_trail(csv_file: str, output_file: Optional[str] = None) -> str:
    """Read `csv_file` and write a summary CSV with per-function stats.

    Returns the path to `output_file`.
    """
    if not os.path.isfile(csv_file):
        raise FileNotFoundError(csv_file)
    if output_file is None:
        output_file = os.path.splitext(csv_file)[0] + '_audit.csv'

    stats: Dict[str, Dict[str, Any]] = {}
    with open(csv_file, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            fn = r.get('function_name') or '<root>'
            rec = stats.setdefault(fn, {'count': 0, 'total_ms': 0, 'errors': 0})
            rec['count'] += 1
            try:
                rec['total_ms'] += int(r.get('duration_ms') or 0)
            except Exception:
                pass
            if (r.get('level') or '').upper() == 'ERROR' or r.get('event') == 'validation_error':
                rec['errors'] += 1

    _ensure_dir_exists(output_file)
    with open(output_file, 'w', newline='', encoding='utf-8') as fh:
        fieldnames = ['function_name', 'count', 'total_duration_ms', 'avg_duration_ms', 'errors']
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for fn, rec in sorted(stats.items(), key=lambda kv: kv[0]):
            avg = int(rec['total_ms'] / rec['count']) if rec['count'] else 0
            writer.writerow({
                'function_name': fn,
                'count': rec['count'],
                'total_duration_ms': rec['total_ms'],
                'avg_duration_ms': avg,
                'errors': rec['errors']
            })
    return os.path.abspath(output_file)
