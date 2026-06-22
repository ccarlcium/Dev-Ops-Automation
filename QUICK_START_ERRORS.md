# Quick Reference - Error Logging System

## What's New

Your pipeline system now automatically detects and stores **ALL ERRORS** in a dedicated folder.

## 📁 Error Storage Location

```
error_logs/
├── error_log.csv          ← Central error database
└── error_*.json           ← Individual error snapshots (detailed logs)
```

## Quick Commands

### View All Errors (Summary)
```powershell
python view_errors.py
```
Shows:
- Total error count
- Errors grouped by type
- List of files with errors

### View Detailed Error Table  
```powershell
python view_errors.py --format table
```
Shows errors in a readable table format.

### View Recent Errors
```powershell
python view_errors.py --format recent --recent 10
```
Shows the last 10 errors (customize with `--recent N`).

### View Specific Error Type
```powershell
python view_errors.py --type validation_error
```
Shows only errors of a specific type.

### View as JSON (for analysis)
```powershell
python view_errors.py --format json
```
Returns errors in JSON format.

## Error Types Detected

| Type | What It Means | Example |
|------|---------------|---------|
| `validation_error` | Data validation failed | Empty required field |
| `file_error` | File access issue | File doesn't exist |
| `permission_error` | No read/write access | Permission denied |
| `encoding_error` | Character encoding issue | Invalid UTF-8 |
| `csv_parse_error` | Malformed CSV | Invalid format |
| `parsing_error` | File parsing failed | Empty/no headers |
| `processing_error` | General processing error | Unexpected exception |
| `critical_error` | System critical error | Fatal failure |

## Workflow Example

```powershell
# 1. Process your files
python process_inputs.py

# 2. Check if any errors occurred
python view_errors.py

# 3. If errors exist, view details
python view_errors.py --format table

# 4. Fix the problematic data and reprocess
python process_inputs.py
```

## Error Log Details

Each error contains:
- **timestamp** - Exact time error occurred
- **error_type** - Category of error
- **message** - What went wrong
- **file_path** - Which file had the error
- **function_name** - Where in code it failed
- **details** - Additional context
- **traceback** - Stack trace (for critical errors)

## Find Problematic Files

```powershell
# What file has the most errors?
python view_errors.py --format summary

# Then inspect that file to fix data quality issues
```

## Automated Error Handling

All of these now have built-in error handling:
- ✅ `process_inputs.py` - One-shot processing
- ✅ `watch_input.py` - Continuous watching  
- ✅ `processing.py` - Core processing engine

Errors are **automatically** logged - no extra setup needed!

## Full Documentation

For detailed information, see: [ERROR_LOGGING_GUIDE.md](ERROR_LOGGING_GUIDE.md)

## Key Benefits

✅ Never miss an error  
✅ Errors stored for audit trail  
✅ Multiple viewing formats  
✅ Easy troubleshooting  
✅ Error statistics and reporting  
✅ Full error context preserved  
✅ Automatic stack traces  

---

**That's it!** Your system now detects and stores errors automatically. 🎉
