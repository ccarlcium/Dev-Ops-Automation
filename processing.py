"""CSV processing module for the midterm project.

Functions:
- process_csv(input_csv, output_csv, log_csv=None) -> (processed_count, errors_count)

The function reads `input_csv`, performs simple validation, writes valid rows to `output_csv`,
and records validation errors and processing history using `pipeline_logging` helpers.
"""
from __future__ import annotations
import csv
import os
import time
from typing import Tuple, List, Dict, Any, Iterable

from create_pipeline_log import create_pipeline_log
from log_validation_errors import log_validation_errors
from track_file_processing_history import track_file_processing_history
from log_execution_time import log_execution_time
from generate_audit_trail import generate_audit_trail
from error_logging import log_error, log_batch_errors


def _now_iso() -> str:
    import datetime
    return datetime.datetime.utcnow().isoformat() + 'Z'


def _validate_row(row: Dict[str, str], required_columns: Iterable[str]) -> List[Dict[str, Any]]:
    errors: List[Dict[str, Any]] = []
    # ensure required columns present
    for c in required_columns:
        if c not in row:
            errors.append({'file_path': '', 'details': f'missing column: {c}', 'function_name': 'process_csv'})
            return errors
    # check non-empty values for required columns
    for c in required_columns:
        if (row.get(c) or '').strip() == '':
            errors.append({'file_path': '', 'details': f'empty value in column: {c}', 'function_name': 'process_csv'})
    # example numeric check for column named 'id' or 'value'
    if 'id' in row and row.get('id'):
        try:
            int(row['id'])
        except Exception:
            errors.append({'file_path': '', 'details': 'id not integer', 'function_name': 'process_csv'})
    return errors


def process_csv(input_csv: str, output_csv: str, log_csv: str | None = None, required_columns: Iterable[str] | None = None) -> Tuple[int, int]:
    """Process `input_csv`, write valid rows to `output_csv`.

    - Automatically detects CSV columns if `required_columns` is None.
    - Records file processing history to `log_csv`.
    - Logs validation errors via `log_validation_errors`.
    - Captures and logs runtime errors to error_logs directory.

    Returns (processed_count, errors_count).
    """
    if log_csv is None:
        log_csv = os.path.join(os.path.dirname(os.path.abspath(input_csv)), 'pipeline_log.csv')

    processed = 0
    errors: List[Dict[str, Any]] = []
    
    try:
        # Check if input file exists
        if not os.path.isfile(input_csv):
            error_msg = f"Input file not found: {input_csv}"
            log_error(
                error_type='file_error',
                message=error_msg,
                file_path=input_csv,
                function_name='process_csv',
            )
            return 0, 1

        create_pipeline_log(log_csv)

        start_ts = _now_iso()
        track_file_processing_history(log_csv, input_csv, 'started', details=f'started_at={start_ts}')

        @log_execution_time(log_csv)
        def _run():
            nonlocal processed, errors, required_columns

            try:
                with open(input_csv, newline='', encoding='utf-8') as inf, \
                     open(output_csv, 'w', newline='', encoding='utf-8') as outf:

                    reader = csv.DictReader(inf)
                    fieldnames = reader.fieldnames or []

                    # Check if file is empty
                    if not fieldnames:
                        error_msg = "Input file has no headers or is empty"
                        log_error(
                            error_type='parsing_error',
                            message=error_msg,
                            file_path=input_csv,
                            function_name='process_csv',
                        )
                        return

                    # 🔥 AUTO-DETECT COLUMNS
                    if required_columns is None:
                        required_columns = fieldnames

                    writer = csv.DictWriter(outf, fieldnames=fieldnames)
                    writer.writeheader()

                    row_num = 0
                    for row in reader:
                        row_num += 1
                        try:
                            row_errors = _validate_row(row, required_columns)
                            if row_errors:
                                for e in row_errors:
                                    e['file_path'] = input_csv
                                    e['details'] = f"Row {row_num}: {e.get('details', '')}"
                                errors.extend(row_errors)
                            else:
                                writer.writerow(row)
                                processed += 1
                        except Exception as row_err:
                            error_msg = f"Error processing row {row_num}: {str(row_err)}"
                            log_error(
                                error_type='row_processing_error',
                                message=error_msg,
                                file_path=input_csv,
                                function_name='_run',
                                exception=row_err,
                            )
                            errors.append({
                                'file_path': input_csv,
                                'details': error_msg,
                                'function_name': 'process_csv',
                                'type': 'row_processing_error',
                            })

            except UnicodeDecodeError as ue:
                error_msg = f"Unicode decode error while reading {input_csv}: {str(ue)}"
                log_error(
                    error_type='encoding_error',
                    message=error_msg,
                    file_path=input_csv,
                    function_name='_run',
                    exception=ue,
                )
                errors.append({
                    'file_path': input_csv,
                    'message': error_msg,
                    'type': 'encoding_error',
                })

            except PermissionError as pe:
                error_msg = f"Permission denied accessing {input_csv}: {str(pe)}"
                log_error(
                    error_type='permission_error',
                    message=error_msg,
                    file_path=input_csv,
                    function_name='_run',
                    exception=pe,
                )
                raise

            except csv.Error as ce:
                error_msg = f"CSV parsing error in {input_csv}: {str(ce)}"
                log_error(
                    error_type='csv_parse_error',
                    message=error_msg,
                    file_path=input_csv,
                    function_name='_run',
                    exception=ce,
                )
                errors.append({
                    'file_path': input_csv,
                    'message': error_msg,
                    'type': 'csv_parse_error',
                })

            except Exception as e:
                error_msg = f"Unexpected error in _run: {str(e)}"
                log_error(
                    error_type='unexpected_error',
                    message=error_msg,
                    file_path=input_csv,
                    function_name='_run',
                    exception=e,
                )
                raise

        _run()

        if errors:
            log_validation_errors(log_csv, errors)
            # Also log to error_logs directory
            log_batch_errors(errors, file_path=input_csv)

        track_file_processing_history(log_csv, input_csv, 'completed', details=f'processed={processed},errors={len(errors)}')

        try:
            generate_audit_trail(log_csv)
        except Exception as audit_err:
            log_error(
                error_type='audit_trail_error',
                message=f"Error generating audit trail: {str(audit_err)}",
                function_name='generate_audit_trail',
                exception=audit_err,
            )

        return processed, len(errors)

    except PermissionError as pe:
        error_msg = f"Permission denied accessing files: {str(pe)}"
        log_error(
            error_type='permission_error',
            message=error_msg,
            file_path=input_csv,
            function_name='process_csv',
            exception=pe,
        )
        return 0, 1

    except FileNotFoundError as fnfe:
        error_msg = f"File not found: {str(fnfe)}"
        log_error(
            error_type='file_not_found_error',
            message=error_msg,
            file_path=input_csv,
            function_name='process_csv',
            exception=fnfe,
        )
        return 0, 1

    except Exception as e:
        error_msg = f"Unexpected error in process_csv: {str(e)}"
        log_error(
            error_type='critical_error',
            message=error_msg,
            file_path=input_csv,
            function_name='process_csv',
            exception=e,
        )
        try:
            track_file_processing_history(log_csv, input_csv, 'failed', details=f'error={error_msg}')
        except Exception:
            pass
        return 0, 1