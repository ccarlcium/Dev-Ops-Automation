"""Error log viewer and analyzer utility.

Usage:
  python view_errors.py [--format {table|json|summary}]

This script provides easy access to all logged errors with multiple
viewing formats and statistics.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
from typing import List, Dict, Any
from error_logging import ERROR_LOGS_DIR, get_error_summary


def view_errors_summary() -> None:
    """Display a summary of all errors."""
    summary = get_error_summary()
    
    print("\n" + "="*70)
    print("ERROR SUMMARY")
    print("="*70)
    print(f"Total errors: {summary['total_errors']}")
    
    if summary['errors_by_type']:
        print(f"\nErrors by type:")
        for error_type, count in sorted(summary['errors_by_type'].items()):
            print(f"  • {error_type:<30} {count:>5} error(s)")
    else:
        print("No errors logged yet.")
    
    if summary['files_with_errors']:
        print(f"\nFiles with errors ({len(summary['files_with_errors'])}):")
        for file_path in sorted(summary['files_with_errors']):
            print(f"  • {file_path}")
    
    print("="*70 + "\n")


def view_errors_table() -> None:
    """Display errors in a table format."""
    error_log = os.path.join(ERROR_LOGS_DIR, 'error_log.csv')
    
    if not os.path.isfile(error_log):
        print("No error log found.")
        return
    
    print("\n" + "="*130)
    print("ERROR LOG (TABLE VIEW)")
    print("="*130)
    
    try:
        with open(error_log, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                print("No errors logged yet.")
                return
            
            # Print header
            print(f"{'Timestamp':<28} {'Type':<25} {'Message':<50} {'File':<15}")
            print("-"*130)
            
            for row in rows:
                timestamp = row.get('timestamp', '')[:19]  # Truncate to date+time
                error_type = row.get('error_type', '')[:25]
                message = row.get('message', '')[:50]
                file_path = row.get('file_path', '')
                if file_path:
                    file_path = os.path.basename(file_path)[:15]
                
                print(f"{timestamp:<28} {error_type:<25} {message:<50} {file_path:<15}")
        
        print("="*130 + "\n")
    except Exception as e:
        print(f"Error reading log file: {str(e)}")


def view_errors_json() -> None:
    """Display errors in JSON format."""
    error_log = os.path.join(ERROR_LOGS_DIR, 'error_log.csv')
    
    if not os.path.isfile(error_log):
        print("No error log found.")
        return
    
    try:
        errors = []
        with open(error_log, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse details if it's a JSON string
                if row.get('details'):
                    try:
                        row['details'] = json.loads(row['details'])
                    except json.JSONDecodeError:
                        pass
                errors.append(row)
        
        print(json.dumps(errors, indent=2))
    except Exception as e:
        print(f"Error reading log file: {str(e)}")


def view_recent_errors(count: int = 10) -> None:
    """Display the most recent errors."""
    error_log = os.path.join(ERROR_LOGS_DIR, 'error_log.csv')
    
    if not os.path.isfile(error_log):
        print("No error log found.")
        return
    
    print("\n" + "="*130)
    print(f"RECENT ERRORS (Last {count})")
    print("="*130)
    
    try:
        with open(error_log, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                print("No errors logged yet.")
                return
            
            # Get last N rows
            recent = rows[-count:] if len(rows) > count else rows
            
            # Print header
            print(f"{'#':<3} {'Timestamp':<28} {'Type':<20} {'Message':<60}")
            print("-"*130)
            
            for idx, row in enumerate(recent, 1):
                timestamp = row.get('timestamp', '')[:19]
                error_type = row.get('error_type', '')[:20]
                message = row.get('message', '')[:60]
                
                print(f"{idx:<3} {timestamp:<28} {error_type:<20} {message:<60}")
        
        print("="*130 + "\n")
    except Exception as e:
        print(f"Error reading log file: {str(e)}")


def view_errors_by_type(error_type: str) -> None:
    """Display errors of a specific type."""
    error_log = os.path.join(ERROR_LOGS_DIR, 'error_log.csv')
    
    if not os.path.isfile(error_log):
        print("No error log found.")
        return
    
    print("\n" + "="*130)
    print(f"ERRORS OF TYPE: {error_type}")
    print("="*130)
    
    try:
        with open(error_log, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader if row.get('error_type') == error_type]
            
            if not rows:
                print(f"No errors of type '{error_type}' found.")
                return
            
            print(f"Found {len(rows)} error(s)\n")
            
            # Print header
            print(f"{'Timestamp':<28} {'File':<30} {'Message':<60}")
            print("-"*130)
            
            for row in rows:
                timestamp = row.get('timestamp', '')[:19]
                file_path = row.get('file_path', '')
                if file_path:
                    file_path = os.path.basename(file_path)[:30]
                message = row.get('message', '')[:60]
                
                print(f"{timestamp:<28} {file_path:<30} {message:<60}")
        
        print("="*130 + "\n")
    except Exception as e:
        print(f"Error reading log file: {str(e)}")


def list_error_files() -> None:
    """List all error JSON files."""
    if not os.path.isdir(ERROR_LOGS_DIR):
        print("No error_logs directory found.")
        return
    
    json_files = [f for f in os.listdir(ERROR_LOGS_DIR) if f.endswith('.json')]
    
    if not json_files:
        print("No individual error files found.")
        return
    
    print(f"\n{'='*70}")
    print(f"Individual error files ({len(json_files)})")
    print(f"{'='*70}")
    
    for fname in sorted(json_files, reverse=True)[:20]:  # Show most recent 20
        fpath = os.path.join(ERROR_LOGS_DIR, fname)
        size = os.path.getsize(fpath)
        print(f"  • {fname:<40} {size:>8} bytes")
    
    if len(json_files) > 20:
        print(f"  ... and {len(json_files) - 20} more files")
    
    print(f"{'='*70}\n")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='View and analyze error logs from the pipeline system.'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json', 'summary', 'recent', 'files'],
        default='summary',
        help='Output format (default: summary)'
    )
    parser.add_argument(
        '--type',
        help='Filter errors by type'
    )
    parser.add_argument(
        '--recent',
        type=int,
        default=10,
        help='Number of recent errors to show (default: 10)'
    )
    
    args = parser.parse_args()
    
    if args.format == 'summary':
        view_errors_summary()
    elif args.format == 'table':
        view_errors_table()
    elif args.format == 'json':
        view_errors_json()
    elif args.format == 'recent':
        view_recent_errors(args.recent)
    elif args.format == 'files':
        list_error_files()
    
    if args.type:
        view_errors_by_type(args.type)


if __name__ == '__main__':
    main()
