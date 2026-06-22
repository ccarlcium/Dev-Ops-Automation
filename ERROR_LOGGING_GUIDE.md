# Error Logging System - Complete Guide

## Overview

Your pipeline system now has a comprehensive error detection and logging system that captures, stores, and analyzes all errors that occur during processing. All errors are logged to a dedicated `error_logs/` folder for easy access and troubleshooting.

## Key Features

✅ **Automatic Error Detection**
- File I/O errors (missing files, permission issues)
- CSV parsing errors (encoding issues, malformed CSV)
- Validation errors (empty values, invalid data types)
- Processing errors (unexpected exceptions)
- Runtime errors with full stack traces

✅ **Multiple Error Log Formats**
- CSV format for spreadsheet analysis (`error_logs/error_log.csv`)
- JSON format for detailed analysis (`error_logs/error_*.json`)

✅ **Error Tracking**
- Timestamp for each error
- Error type classification
- File path being processed
- Function name where error occurred
- Detailed error message
- Full traceback for debugging

✅ **Error Monitoring**
- View errors in summary, table, or JSON format
- Filter errors by type
- Get real-time error statistics
- Identify problematic files

## File Structure

```
error_logs/                    # New error logging directory
├── error_log.csv             # Central error log (CSV format)
├── error_20260324T120530.json # Individual error snapshots
├── error_20260324T120531.json
└── ...
```

## How It Works

### 1. Automatic Error Capture

All errors are now captured automatically during pipeline execution:

```python
# When process_inputs.py runs:
python process_inputs.py

# Errors are logged to:
# - error_logs/error_log.csv (all errors)
# - error_logs/error_*.json (individual error details)
# - output/pipeline_log.csv (pipeline history)
```

### 2. Error Types Detected

| Error Type | Description | Example |
|-----------|-------------|---------|
| `file_error` | File doesn't exist or can't be accessed | Missing input file |
| `file_not_found_error` | Specific file not found exception | FileNotFoundError |
| `permission_error` | No permission to read/write file | PermissionError |
| `encoding_error` | Unicode/encoding issue in file | UnicodeDecodeError |
| `csv_parse_error` | Malformed CSV structure | Invalid CSV format |
| `parsing_error` | File is empty or has no headers | Empty CSV |
| `validation_error` | Data validation failed | Empty required field |
| `row_processing_error` | Error processing individual row | Row parsing issue |
| `processing_error` | General processing error | Unexpected exception |
| `unexpected_error` | Unhandled exception | Runtime error |
| `critical_error` | Critical system error | Fatal failure |

## Using the Error Logging System

### View Error Summary

```powershell
python view_errors.py
```

Shows:
- Total number of errors
- Errors grouped by type
- List of files with errors

### View Errors in Table Format

```powershell
python view_errors.py --format table
```

Shows errors in a readable table with timestamps, types, messages, and files.

### View Errors as JSON

```powershell
python view_errors.py --format json
```

Shows all error details in JSON format for programmatic analysis.

### View Recent Errors

```powershell
python view_errors.py --format recent --recent 20
```

Shows the last 20 errors (customizable with `--recent N`).

### View List of Error Files

```powershell
python view_errors.py --format files
```

Lists all individual error JSON snapshots for detailed inspection.

### Filter Errors by Type

```powershell
python view_errors.py --type validation_error
```

Shows only errors of a specific type.

## Integration Points

### process_inputs.py (One-Shot Processing)

```bash
python process_inputs.py
```

- Processes all CSVs in `input/` directory once
- Logs all errors to `error_logs/`
- Displays summary with error count
- Shows which files had errors

### watch_input.py (Continuous Processing)

```bash
python watch_input.py --input-dir input --log output/pipeline_log.csv
```

- Continuously watches for new files
- Catches and logs errors without stopping
- Exits after 10 consecutive errors (prevents infinite failure loops)
- Reports file move/processing errors

### processing.py (Core Processing)

The core `process_csv()` function now:
- Validates input file exists
- Catches encoding errors
- Catches CSV parsing errors
- Logs each row-level error with context
- Captures audit trail generation errors
- Returns gracefully with error counts

## Error Log Format

### CSV Format (error_logs/error_log.csv)

```
timestamp,error_type,message,file_path,function_name,details,traceback
2026-03-24T12:05:30.123456Z,validation_error,Empty value in column: id,input/sample.csv,process_csv,Column validation failed,
2026-03-24T12:05:31.234567Z,file_error,Input file not found: input/missing.csv,input/missing.csv,process_csv,,
```

### JSON Format (error_logs/error_*.json)

```json
{
  "timestamp": "2026-03-24T12:05:30.123456Z",
  "error_type": "validation_error",
  "message": "Empty value in column: id",
  "file_path": "input/sample.csv",
  "function_name": "process_csv",
  "details": "{\"row\": 5, \"column\": \"id\"}",
  "traceback": "Traceback (most recent call last):\n  ..."
}
```

## Example Usage Workflows

### Workflow 1: Process Inputs with Error Report

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Process all files
python process_inputs.py

# View what went wrong
python view_errors.py

# View detailed errors by type
python view_errors.py --type validation_error

# See most recent errors
python view_errors.py --format recent --recent 5
```

### Workflow 2: Watch For Files with Error Alerts

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Start watching (will log all errors)
python watch_input.py --input-dir input --log output/pipeline_log.csv

# In another terminal:
# View errors in real-time
python view_errors.py --format recent --recent 5
```

### Workflow 3: Debug a Problematic File

```powershell
# Check the error summary
python view_errors.py

# Find which files have errors
python view_errors.py --type validation_error

# View all details for investigation
python view_errors.py --format json | python -m json.tool

# Check individual error JSON files
# error_logs/error_*.json files contain full stacktraces
```

## Advanced Usage

### Programmatic Error Access

```python
from error_logging import get_error_summary, log_error

# Get error statistics
summary = get_error_summary()
print(f"Total errors: {summary['total_errors']}")
print(f"Errors by type: {summary['errors_by_type']}")
print(f"Affected files: {summary['files_with_errors']}")

# Log custom errors
log_error(
    error_type='custom_error',
    message='Something went wrong',
    file_path='input/problematic.csv',
    function_name='my_function'
)
```

### Custom Error Logging

```python
from error_logging import log_error
import traceback

try:
    # Your processing code
    process_something()
except Exception as e:
    log_error(
        error_type='processing_error',
        message=f'Failed to process: {str(e)}',
        file_path='input/file.csv',
        function_name='my_function',
        exception=e  # Automatically includes traceback
    )
```

## Error Log Cleanup

To archive old errors or clear the logs:

```powershell
# View current error logs size
Get-ChildItem error_logs/ | Measure-Object -Property Length -Sum

# Archive old error logs (Windows)
Compress-Archive error_logs/ error_logs_backup_20260324.zip

# Clear error logs (backup first!)
Remove-Item error_logs/*.csv, error_logs/*.json
```

## Troubleshooting

### No errors appearing in error_logs/

1. **Check if errors actually occurred:**
   ```powershell
   python view_errors.py
   ```

2. **Verify error_logs directory exists:**
   ```powershell
   Test-Path error_logs
   ```

3. **Check file permissions:**
   ```powershell
   Get-Acl error_logs
   ```

### Can't access error files

1. **Ensure proper permissions:**
   ```powershell
   icacls error_logs /grant "%USERNAME%":F
   ```

2. **Close any locked files:**
   - Some programs may lock CSV/JSON files

3. **Use JSON format:**
   ```powershell
   python view_errors.py --format json
   ```

### Too many errors

1. **Get summary of errors:**
   ```powershell
   python view_errors.py
   ```

2. **Filter by problematic file:**
   ```powershell
   python view_errors.py --format table
   ```

3. **Review input data quality:**
   - Check CSV formatting
   - Verify required columns
   - Validate data types

## Best Practices

✅ **DO:**
- Check errors after processing with `python view_errors.py`
- Archive error logs periodically for auditing
- Use error types to categorize issues
- Fix data quality issues at the source
- Monitor error trends over time

❌ **DON'T:**
- Ignore critical errors
- Manually edit error_log.csv
- Delete error_logs without backup
- Process known-bad files repeatedly
- Skip validation errors

## Summary

Your pipeline now has robust error detection and logging:

- ✅ All errors automatically captured
- ✅ Stored in `error_logs/` folder
- ✅ Multiple viewing formats available
- ✅ Full stack traces for debugging
- ✅ Error summary and statistics
- ✅ Integration with all processing scripts
- ✅ Easy troubleshooting tools

**To get started:**
```powershell
# 1. Run your normal processing
python process_inputs.py

# 2. Check for errors
python view_errors.py

# 3. Investigate if needed
python view_errors.py --format json
```

That's it! Your errors are now being detected and stored systematically.
