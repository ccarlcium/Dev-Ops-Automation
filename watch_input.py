"""Simple CSV input directory watcher.

Usage:
  python watch_input.py --input-dir <dir> [--interval 2] [--log <log_csv>]

This script polls `--input-dir` for new .csv files, calls `process_csv` on each
new file, writes a `processed_<name>.csv` output next to the input, and moves
the original file to an internal `processed/` subdirectory with a timestamp
to avoid re-processing.

All errors are logged to the error_logs directory for easy troubleshooting.
"""
from __future__ import annotations
import argparse
import os
import shutil
import time
import datetime
from typing import Optional

from processing import process_csv
from error_logging import log_error


def _now_ts() -> str:
    return datetime.datetime.now().strftime('%Y%m%dT%H%M%S')


def watch_input_dir(input_dir: str, poll_interval: float = 2.0, log_csv: Optional[str] = None) -> None:
    try:
        os.makedirs(input_dir, exist_ok=True)
        processed_dir = os.path.join(input_dir, 'processed')
        os.makedirs(processed_dir, exist_ok=True)
    except Exception as e:
        error_msg = f"Failed to create directories: {str(e)}"
        log_error(
            error_type='directory_creation_error',
            message=error_msg,
            function_name='watch_input_dir',
            exception=e,
        )
        raise

    seen = set()
    consecutive_errors = 0
    max_consecutive_errors = 10

    while True:
        try:
            entries = [p for p in os.listdir(input_dir) if p.lower().endswith('.csv')]
            for fname in entries:
                try:
                    # skip files in processed subdir and temporary files
                    full = os.path.join(input_dir, fname)
                    if os.path.isdir(full):
                        continue
                    if os.path.dirname(full) == processed_dir:
                        continue
                    if fname.startswith('processed_'):
                        continue

                    # If we've seen and attempted this file recently, skip until change
                    mtime = os.path.getmtime(full)
                    key = (fname, int(mtime))
                    if key in seen:
                        continue

                    print(f"Detected CSV: {full}")

                    out_name = f"processed_{fname}"
                    out_path = os.path.join(input_dir, out_name)

                    try:
                        processed_count, errors_count = process_csv(full, out_path, log_csv=log_csv)
                        print(f"Processed {fname}: {processed_count} rows, {errors_count} errors")
                        consecutive_errors = 0

                        # move original file to processed/ with timestamp suffix
                        target_name = f"{os.path.splitext(fname)[0]}_{_now_ts()}.csv"
                        target_path = os.path.join(processed_dir, target_name)
                        try:
                            shutil.move(full, target_path)
                            print(f"Moved input to {target_path}")
                        except Exception as move_err:
                            error_msg = f"Failed to move {full} to {target_path}: {str(move_err)}"
                            log_error(
                                error_type='file_move_error',
                                message=error_msg,
                                file_path=full,
                                function_name='watch_input_dir',
                                exception=move_err,
                            )
                            print(f"Warning: {error_msg}")

                    except PermissionError as pe:
                        error_msg = f"Permission denied processing {full}: {str(pe)}"
                        log_error(
                            error_type='permission_error',
                            message=error_msg,
                            file_path=full,
                            function_name='watch_input_dir',
                            exception=pe,
                        )
                        print(f"Error: {error_msg}")
                        consecutive_errors += 1

                    except FileNotFoundError as fnfe:
                        error_msg = f"File not found: {str(fnfe)}"
                        log_error(
                            error_type='file_not_found_error',
                            message=error_msg,
                            file_path=full,
                            function_name='watch_input_dir',
                            exception=fnfe,
                        )
                        print(f"Error: {error_msg}")
                        consecutive_errors += 1

                    except Exception as e:
                        error_msg = f"Error processing {full}: {str(e)}"
                        log_error(
                            error_type='processing_error',
                            message=error_msg,
                            file_path=full,
                            function_name='watch_input_dir',
                            exception=e,
                        )
                        print(f"Error: {error_msg}")
                        consecutive_errors += 1

                    seen.add(key)

                except Exception as inner_err:
                    error_msg = f"Unexpected error processing file {fname}: {str(inner_err)}"
                    log_error(
                        error_type='unexpected_file_error',
                        message=error_msg,
                        file_path=fname,
                        function_name='watch_input_dir',
                        exception=inner_err,
                    )
                    print(f"Error: {error_msg}")

            # Check if too many consecutive errors
            if consecutive_errors >= max_consecutive_errors:
                error_msg = f"Too many consecutive errors ({consecutive_errors}), exiting watcher"
                log_error(
                    error_type='watcher_abort',
                    message=error_msg,
                    function_name='watch_input_dir',
                )
                print(f"Error: {error_msg}")
                return

        except KeyboardInterrupt:
            print("Watcher interrupted by user, exiting")
            log_error(
                error_type='watcher_interrupt',
                message='Watcher interrupted by user',
                function_name='watch_input_dir',
            )
            return

        except Exception as e:
            error_msg = f"Watcher error: {str(e)}"
            log_error(
                error_type='watcher_error',
                message=error_msg,
                function_name='watch_input_dir',
                exception=e,
            )
            print(f"Error: {error_msg}")
            consecutive_errors += 1

            if consecutive_errors >= max_consecutive_errors:
                print(f"Too many consecutive errors, exiting watcher")
                return

        time.sleep(poll_interval)


def main() -> None:
    p = argparse.ArgumentParser(description='Watch an input directory for CSV files and process them.')
    p.add_argument('--input-dir', '-i', required=True, help='Directory to watch for CSV files')
    p.add_argument('--interval', '-t', type=float, default=2.0, help='Polling interval seconds')
    p.add_argument('--log', '-l', dest='log_csv', default=None, help='Path to pipeline log CSV')
    args = p.parse_args()

    watch_input_dir(args.input_dir, poll_interval=args.interval, log_csv=args.log_csv)


if __name__ == '__main__':
    main()
