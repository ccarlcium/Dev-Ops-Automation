# Processing Summary Auto-Logging

## What Changed

Previously, when you ran `python process_inputs.py`, the summary output was only printed to the console and lost after the run ended.

**Now:** The summary is automatically saved to the `error_logs/` folder in **two formats**:

1. **processing_summary.json** - Latest run snapshot (JSON format)
2. **processing_runs.csv** - Historical log of all runs (CSV format)

## New Files in error_logs/

### processing_summary.json (Latest Run)
```json
{
  "timestamp": "2026-03-24T03:53:52.873575Z",
  "processing": {
    "total_files": 1,
    "successfully_processed": 1,
    "failed": 0,
    "success_rate": 100.0
  },
  "logs": {
    "pipeline_log": "output/pipeline_log.csv",
    "error_log": "error_logs/error_log.csv",
    "error_logs_directory": "error_logs"
  },
  "errors": {
    "total_errors": 0,
    "errors_by_type": {},
    "files_with_errors": []
  }
}
```

**Content:**
- Timestamp of run
- Total files processed
- Successfully processed count
- Failed count
- Success rate percentage
- Paths to logs
- Error summary (total, by type, affected files)

### processing_runs.csv (Historical Log)
```
timestamp,total_files,successfully_processed,failed,success_rate,total_errors,pipeline_log
2026-03-24T03:53:52.874519Z,1,1,0,100.0,0,output/pipeline_log.csv
2026-03-24T04:00:15.123456Z,4,4,0,100.0,6,output/pipeline_log.csv
2026-03-24T04:05:30.654321Z,2,1,1,50.0,12,output/pipeline_log.csv
```

**Content:**
- Each row = one run
- Timestamp
- Total files
- Successfully processed
- Failed count
- Success rate
- Total errors
- Pipeline log path

**Use case:** Track processing trends over time, see historical runs, analyze success rates.

## Usage

### View Latest Run Summary
```bash
# JSON format
type error_logs\processing_summary.json

# Pretty-print with Python
python -c "import json; print(json.dumps(json.load(open('error_logs/processing_summary.json')), indent=2))"
```

### View Historical Runs
```bash
# CSV format
type error_logs\processing_runs.csv

# Open in Excel
start error_logs\processing_runs.csv
```

### Check Success Rate Over Time
```bash
# With Python
python -c "
import csv
with open('error_logs/processing_runs.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f\"{row['timestamp']}: {row['success_rate']}% success\")
"
```

## What Gets Saved

When you run `python process_inputs.py`:

```
✓ processing_summary.json is created (or overwritten)
  └─ Latest run's complete summary
  
✓ processing_runs.csv is appended to (or created)
  └─ Each run adds a new row with stats
```

## What's Tracked

| Metric | Purpose |
|--------|---------|
| `total_files` | How many CSVs were found |
| `successfully_processed` | How many processed without failure |
| `failed` | How many processing attempts failed |
| `success_rate` | Percentage of successful processing |
| `total_errors` | Total validation/processing errors |
| `pipeline_log` | Reference to pipeline log file |
| `timestamp` | Exact date/time of run |

## Accessing From GitHub Actions

When the CI/CD pipeline runs, these files are:

1. **Created in error_logs/**
2. **Uploaded as artifacts** with name `error-logs` (30-day retention)
3. **Committed to repo** (if push event)

**Access:**
- GitHub Actions → Artifacts → error-logs
- Download and extract to see processing_summary.json and processing_runs.csv

## Error Tracking Details

Each processing run captures:

```
errors: {
  total_errors: <count>,
  errors_by_type: {
    validation_error: 5,
    file_error: 1,
    ...
  },
  files_with_errors: [
    "input/file1.csv",
    "input/file2.csv"
  ]
}
```

## Example Workflows

### Monitor Processing Success
```bash
# Run processing
python process_inputs.py

# Check latest summary
cat error_logs\processing_summary.json

# See if success_rate is 100%
```

### Track Quality Over Time
```bash
# After multiple runs, view historical data
# Each row in processing_runs.csv shows one run
# Look for trends or degradation
cat error_logs\processing_runs.csv
```

### Audit Trail
```bash
# For compliance/audit:
# - processing_runs.csv: Complete history of all runs
# - Each row has: timestamp, counts, error counts
# - error_log.csv: Detailed errors
# - pipeline_log.csv: Execution times
```

### Debug Failed Processing
```bash
# If success_rate < 100:
# 1. Check processing_summary.json for failed count
# 2. Check errors.files_with_errors list
# 3. Look at error_log.csv for details
# 4. Inspect specific file
```

## Files in error_logs/ Now

```
error_logs/
├── error_log.csv                    ← All errors (detailed)
├── error_*.json                     ← Individual error snapshots
├── processing_summary.json          ← Latest run (NEW)
└── processing_runs.csv              ← Historical log (NEW)
```

## Retention

| File | Retention | Purpose |
|------|-----------|---------|
| error_log.csv | Permanent (local) | Detailed error log |
| error_*.json | Permanent (local) | Error details |
| processing_summary.json | Permanent (local) | Latest run snapshot |
| processing_runs.csv | Permanent (local) | Historical all runs |
| error-logs artifact | 30 days (GitHub) | GitHub backup |

## Examples

### Example 1: Clean Run
```json
{
  "processing": {
    "total_files": 1,
    "successfully_processed": 1,
    "failed": 0,
    "success_rate": 100.0
  },
  "errors": {
    "total_errors": 0,
    "errors_by_type": {},
    "files_with_errors": []
  }
}
```

### Example 2: Run With Errors
```json
{
  "processing": {
    "total_files": 4,
    "successfully_processed": 3,
    "failed": 1,
    "success_rate": 75.0
  },
  "errors": {
    "total_errors": 15,
    "errors_by_type": {
      "validation_error": 12,
      "file_error": 3
    },
    "files_with_errors": [
      "input/complex_input.csv"
    ]
  }
}
```

## Implementation Details

### New Functions in error_logging.py

```python
save_processing_summary(
    total_files,
    processed_count,
    failed_count,
    pipeline_log
)
# Saves: error_logs/processing_summary.json

save_processing_run_log(
    total_files,
    processed_count,
    failed_count,
    pipeline_log
)
# Appends to: error_logs/processing_runs.csv
```

### Updated process_inputs.py

After printing summary to console, also calls:
```python
save_processing_summary(...)
save_processing_run_log(...)
```

Both automatically append to error_logs for persistent storage.

## Summary

✅ **Before:** Summary printed to console only (lost after run)

✅ **After:** Summary saved automatically in error_logs/:
- `processing_summary.json` - Latest run snapshot
- `processing_runs.csv` - Historical log of all runs

✅ **Accessible:**
- Local: View files in error_logs/
- GitHub: Download from artifacts
- Committed: Auto-committed to repo on push

✅ **Actionable:**
- Track success rates over time
- Identify problematic files
- Audit trail for compliance
- Spot quality trends

All automatic, no manual intervention needed! 🚀
