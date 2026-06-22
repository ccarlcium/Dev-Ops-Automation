# GitHub Actions Automated Error Logging

## What's New

Your GitHub Actions CI/CD pipeline now automatically runs error logging whenever you push or pull to GitHub.

## How It Works

### Workflow Trigger Points

**On Push (Main Branch):**
1. Tests run with `pytest`
2. CSVs in `input/` are processed with error detection
3. Error logs are captured
4. Error summary is displayed in GitHub Actions
5. Error logs are committed back to repo (if errors found)
6. Processed files are committed to repo
7. Error logs are uploaded as artifacts (30-day retention)

**On Pull Request:**
1. Tests run with `pytest`
2. CSVs in `input/` are processed with error detection
3. Error logs are captured
4. Error summary is displayed in GitHub Actions
5. Error logs are uploaded as artifacts (30-day retention)

### Automated Error Logging Steps

```yaml
1. Process any CSVs in input/ with error logging
   └─> Runs: python process_inputs.py
       Creates: error_logs/error_log.csv (if errors occur)

2. Display error summary
   └─> Shows errors in: GitHub Actions > Run summary
       Formats:
       - ✅ No errors detected (if clean)
       - ⚠️ Errors Detected (if errors found)

3. Commit and push error logs
   └─> Automatically commits error_logs/ to repo (if errors)
   └─> Messages: "CI: Add error logs from run"

4. Upload error logs as artifact
   └─> Available in: GitHub Actions > Artifacts
       Name: error-logs
       Retention: 30 days

5. Upload processing logs as artifact
   └─> Available in: GitHub Actions > Artifacts
       Name: processing-logs
       Retention: 30 days
```

## Accessing Error Logs from GitHub

### Method 1: View in GitHub Actions Run Summary

1. Go to your repository
2. Click **Actions** tab
3. Select the workflow run
4. View the **Run summary** at bottom of page
5. See error summary displayed automatically

### Method 2: Download as Artifacts

1. Go to your repository
2. Click **Actions** tab
3. Select the workflow run
4. Scroll down to **Artifacts** section
5. Download:
   - `error-logs` (error_log.csv and error_*.json files)
   - `processing-logs` (pipeline_log.csv and processed CSVs)

### Method 3: Committed Error Logs

If errors are detected on push:
1. New commits are automatically created with error logs
2. Navigate to **error_logs/** folder in repo
3. View **error_log.csv** directly on GitHub
4. View individual **error_*.json** files for details

## Error Log Files

### error_log.csv
Central error database with columns:
- timestamp
- error_type
- message
- file_path
- function_name
- details
- traceback

### error_*.json
Individual error snapshots with complete details and stack traces.

## Example Workflow

### Scenario 1: Commit with CSV file containing errors

```bash
# You push a CSV with validation issues
git push origin main

# GitHub Actions:
# 1. Runs tests ✓
# 2. Processes CSV ✓
# 3. Detects 5 validation errors
# 4. Creates error_logs/error_log.csv
# 5. Displays error summary in run
# 6. Commits error_logs/ back to repo
# 7. Uploads artifacts for 30 days
```

### Scenario 2: Pull request with test files

```bash
# You create a PR
gh pr create --title "Add new test"

# GitHub Actions:
# 1. Runs tests ✓
# 2. Processes CSVs ✓
# 3. No errors found ✓
# 4. Shows: "✅ No errors detected"
# 5. Uploads artifacts as backup
```

## Configuration Details

### Error Detection Stages

**During CI:**
1. File validation (existence, permissions, encoding)
2. CSV parsing (headers, format)
3. Row-level validation (required fields, data types)
4. Processing errors (runtime issues)

### Error Types Captured

- `validation_error` - Data validation failed
- `file_error` - File access issues
- `permission_error` - Permission denied
- `encoding_error` - Character encoding issue
- `csv_parse_error` - Malformed CSV
- `parsing_error` - File parsing failed
- `processing_error` - General processing error
- `critical_error` - System critical error

### Artifact Retention

```yaml
error-logs artifact:
- Retained for 30 days
- Deleted automatically after 30 days
- Can be downloaded any time until expiration

processing-logs artifact:
- Retained for 30 days
- Deleted automatically after 30 days
- Can be downloaded any time until expiration
```

## Monitoring and Troubleshooting

### Check if CI ran successfully

1. Go to repository
2. Click **Actions** tab
3. Look for latest workflow run
4. Green checkmark ✓ = Success (no critical failures)
5. Red X ✗ = Failure (tests failed or critical error)

### Check for processing errors

1. Click the workflow run
2. Scroll to **Run summary** section
3. See error count and summary
4. Download `error-logs` artifact for details

### Debug a specific error

1. Download `error-logs` artifact
2. Open `error_log.csv` in spreadsheet or text editor
3. View individual `error_*.json` files for stack traces
4. Share with team for investigation

## Local Testing Before Push

Test locally to catch errors before pushing:

```powershell
# Process local files with error checking
python process_inputs.py

# View errors locally
python view_errors.py

# Fix issues, then push
git add .
git commit -m "Fix CSV validation errors"
git push origin main
```

## GitHub Actions Job Summary Example

When errors are detected, your job summary shows:

```
### ⚠️ Errors Detected During Processing

======================================================================
ERROR SUMMARY
======================================================================
Total errors: 6

Errors by type:
  • validation_error                   6 error(s)

Files with errors (2):
  • input\complex_input.csv
  • input\test.csv
======================================================================
```

When no errors are detected:

```
### ✅ No errors detected during processing
```

## Automatic Commits

When errors are detected during push, the workflow automatically:
1. Creates a commit with error logs
2. Commits to the same branch being pushed
3. Includes message: "CI: Add error logs from run"
4. Does NOT interfere with your changes

**Note:** If push fails, the workflow still uploads artifacts so you can access error logs.

## Integration with CI/CD Pipeline

The automated error logging is now part of your:
- ✅ Push workflow (all branches)
- ✅ Pull request workflow
- ✅ Automated testing pipeline
- ✅ Continuous processing pipeline
- ✅ Audit trail system

## Next Steps

1. **Make a test push** to see error logging in action
2. **Check GitHub Actions** for the error summary
3. **Download artifacts** to inspect error details
4. **View error-logs** folder in your repo (if errors occurred)

## Key Benefits

✅ Errors are always captured, even in CI  
✅ Error summary visible in GitHub Actions  
✅ Error logs automatically committed to repo  
✅ Artifacts uploaded for backup and investigation  
✅ 30-day retention for audit trail  
✅ No manual intervention needed  
✅ Complete error context preserved  
✅ Stack traces available for debugging  

---

**Your CI/CD pipeline now has automatic, comprehensive error logging! 🚀**
