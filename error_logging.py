"""Comprehensive error logging module for the pipeline system.

This module provides enhanced error detection and logging capabilities,
storing all errors in a dedicated error_logs/ directory and the main
pipeline log.
"""
from __future__ import annotations
import csv
import os
import datetime
import json
import traceback
from typing import Any, Dict, Optional, List


ERROR_LOGS_DIR = 'error_logs'


def _ensure_error_dir() -> str:
    """Ensure error_logs directory exists and return its path."""
    os.makedirs(ERROR_LOGS_DIR, exist_ok=True)
    return ERROR_LOGS_DIR


def _now_ts() -> str:
    """Return current timestamp in ISO format with Z suffix."""
    return datetime.datetime.utcnow().isoformat() + 'Z'


def _now_filename_ts() -> str:
    """Return current timestamp suitable for filenames."""
    return datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')


def log_error(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    file_path: Optional[str] = None,
    function_name: Optional[str] = None,
    exception: Optional[Exception] = None,
    error_log_csv: Optional[str] = None,
) -> None:
    """Log an error to both the error_logs folder and pipeline log.
    
    Args:
        error_type: Type of error (e.g., 'validation_error', 'file_error', 'parsing_error')
        message: Error message
        details: Additional details dict
        file_path: Path to the file being processed
        function_name: Name of function where error occurred
        exception: Exception object if available
        error_log_csv: Path to error log CSV (defaults to error_logs/error_log.csv)
    """
    error_dir = _ensure_error_dir()
    
    if error_log_csv is None:
        error_log_csv = os.path.join(error_dir, 'error_log.csv')
    
    # Build error record
    error_record = {
        'timestamp': _now_ts(),
        'error_type': error_type,
        'message': message,
        'file_path': file_path or '',
        'function_name': function_name or '',
        'details': json.dumps(details) if details else '',
    }
    
    # Add traceback if exception provided
    if exception:
        error_record['traceback'] = traceback.format_exc()
    else:
        error_record['traceback'] = ''
    
    # Write to error log CSV
    _write_error_csv(error_log_csv, error_record)
    
    # Also write individual error file for easy access
    error_filename = f"error_{_now_filename_ts()}.json"
    error_filepath = os.path.join(error_dir, error_filename)
    _write_error_json(error_filepath, error_record)


def log_batch_errors(
    errors: List[Dict[str, Any]],
    file_path: Optional[str] = None,
    error_log_csv: Optional[str] = None,
) -> None:
    """Log multiple errors at once.
    
    Args:
        errors: List of error dicts (each should have 'type', 'message', and optional 'details')
        file_path: Path to file being processed
        error_log_csv: Path to error log CSV
    """
    error_dir = _ensure_error_dir()
    
    if error_log_csv is None:
        error_log_csv = os.path.join(error_dir, 'error_log.csv')
    
    for error in errors:
        # Handle both old format (details key) and new format (message key)
        message = error.get('message', error.get('details', ''))
        
        record = {
            'timestamp': _now_ts(),
            'error_type': error.get('type', 'validation_error'),
            'message': message,
            'file_path': file_path or error.get('file_path', ''),
            'function_name': error.get('function_name', ''),
            'details': json.dumps(error.get('details')) if error.get('details') and error.get('type') else '',
            'traceback': '',
        }
        _write_error_csv(error_log_csv, record)


def _write_error_csv(csv_file: str, record: Dict[str, str]) -> None:
    """Write error record to CSV file."""
    os.makedirs(os.path.dirname(os.path.abspath(csv_file)), exist_ok=True)
    
    headers = [
        'timestamp',
        'error_type',
        'message',
        'file_path',
        'function_name',
        'details',
        'traceback',
    ]
    
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        
        # Ensure all fields present
        row = {k: '' for k in headers}
        for k, v in record.items():
            if k in headers:
                row[k] = str(v) if v is not None else ''
        writer.writerow(row)


def _write_error_json(json_file: str, record: Dict[str, Any]) -> None:
    """Write error record to JSON file."""
    os.makedirs(os.path.dirname(os.path.abspath(json_file)), exist_ok=True)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2)


def get_error_summary(error_log_csv: Optional[str] = None) -> Dict[str, Any]:
    """Get a summary of all errors logged.
    
    Args:
        error_log_csv: Path to error log CSV
        
    Returns:
        Dict with error counts by type and total errors
    """
    error_dir = _ensure_error_dir()
    
    if error_log_csv is None:
        error_log_csv = os.path.join(error_dir, 'error_log.csv')
    
    if not os.path.isfile(error_log_csv):
        return {
            'total_errors': 0,
            'errors_by_type': {},
            'files_with_errors': set(),
        }
    
    summary = {
        'total_errors': 0,
        'errors_by_type': {},
        'files_with_errors': set(),
    }
    
    try:
        with open(error_log_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                summary['total_errors'] += 1
                error_type = row.get('error_type', 'unknown')
                summary['errors_by_type'][error_type] = summary['errors_by_type'].get(error_type, 0) + 1
                if row.get('file_path'):
                    summary['files_with_errors'].add(row['file_path'])
    except Exception:
        pass
    
    summary['files_with_errors'] = list(summary['files_with_errors'])
    return summary


def save_processing_summary(
    total_files: int,
    processed_count: int,
    failed_count: int,
    pipeline_log: str,
    summary_file: Optional[str] = None,
) -> None:
    """Save processing run summary to a file in error_logs/.
    
    Args:
        total_files: Total number of files processed
        processed_count: Number of successfully processed files
        failed_count: Number of failed files
        pipeline_log: Path to pipeline log
        summary_file: Path to save summary (defaults to error_logs/processing_summary.json)
    """
    error_dir = _ensure_error_dir()
    
    if summary_file is None:
        summary_file = os.path.join(error_dir, 'processing_summary.json')
    
    # Get current error summary
    error_summary = get_error_summary()
    
    # Convert sets to lists for JSON serialization
    files_with_errors = error_summary.get('files_with_errors', [])
    if isinstance(files_with_errors, set):
        files_with_errors = list(files_with_errors)
    
    summary_data = {
        'timestamp': _now_ts(),
        'processing': {
            'total_files': total_files,
            'successfully_processed': processed_count,
            'failed': failed_count,
            'success_rate': round((processed_count / total_files * 100), 2) if total_files > 0 else 0,
        },
        'logs': {
            'pipeline_log': pipeline_log,
            'error_log': os.path.join(error_dir, 'error_log.csv'),
            'error_logs_directory': error_dir,
        },
        'errors': {
            'total_errors': error_summary.get('total_errors', 0),
            'errors_by_type': error_summary.get('errors_by_type', {}),
            'files_with_errors': files_with_errors,
        },
    }
    
    os.makedirs(os.path.dirname(os.path.abspath(summary_file)), exist_ok=True)
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2)


def save_processing_run_log(
    total_files: int,
    processed_count: int,
    failed_count: int,
    pipeline_log: str,
    run_log_csv: Optional[str] = None,
) -> None:
    """Append processing run to a CSV log for historical tracking.
    
    Args:
        total_files: Total number of files processed
        processed_count: Number of successfully processed files
        failed_count: Number of failed files
        pipeline_log: Path to pipeline log
        run_log_csv: Path to run log CSV (defaults to error_logs/processing_runs.csv)
    """
    error_dir = _ensure_error_dir()
    
    if run_log_csv is None:
        run_log_csv = os.path.join(error_dir, 'processing_runs.csv')
    
    file_exists = os.path.isfile(run_log_csv)
    
    headers = [
        'timestamp',
        'total_files',
        'successfully_processed',
        'failed',
        'success_rate',
        'total_errors',
        'pipeline_log',
    ]
    
    error_summary = get_error_summary()
    
    row = {
        'timestamp': _now_ts(),
        'total_files': total_files,
        'successfully_processed': processed_count,
        'failed': failed_count,
        'success_rate': round((processed_count / total_files * 100), 2) if total_files > 0 else 0,
        'total_errors': error_summary['total_errors'],
        'pipeline_log': pipeline_log,
    }
    
    os.makedirs(os.path.dirname(os.path.abspath(run_log_csv)), exist_ok=True)
    
    with open(run_log_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
