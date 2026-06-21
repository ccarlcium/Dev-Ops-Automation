CSV Processing Project

Overview
- `processing.py`: main CSV orchestrator `process_csv`.
- Five logging modules (one per required function):
  - `create_pipeline_log.py`
  - `log_execution_time.py`
  - `log_validation_errors.py`
  - `track_file_processing_history.py`
  - `generate_audit_trail.py`
- `tests/`: pytest tests for modules and the orchestrator.

Quickstart (local)

1. Create a virtual environment and install dev deps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run tests:

```powershell
pytest -q
```

3. (Optional) drop any CSV files into an `input/` folder and process them:

```powershell
# watch input directory continuously
python watch_input.py -i input -l output/pipeline_log.csv
```

This will automatically produce `processed_<filename>.csv` files next to each
input and move the originals into `input/processed`.

Alternatively there is a one‑shot helper `process_inputs.py` that scans the
`input/` directory once (useful for CI runs):

```powershell
python process_inputs.py
```

Both scripts invoke `processing.process_csv()` under the hood and exercise all
five logging/audit functions.

Error Detection & Logging (NEW!)

The system now automatically detects and logs all errors to a dedicated `error_logs/` folder:

```powershell
# After running either script, view error summary
python view_errors.py

# View detailed errors in table format
python view_errors.py --format table

# View as JSON for analysis
python view_errors.py --format json

# View most recent errors
python view_errors.py --format recent --recent 10
```

**Error types captured:**
- File I/O errors (missing files, permission issues, encoding errors)
- CSV parsing errors (malformed CSV, missing headers)
- Validation errors (empty values, invalid data types)
- Processing errors (unexpected exceptions, runtime errors)

See [ERROR_LOGGING_GUIDE.md](ERROR_LOGGING_GUIDE.md) for complete documentation.

System workflow

The project is built around a simple, extensible CSV processing pipeline.  A high‑level view of the system looks like this:

1. **Input collection** – files are dropped into the `input/` directory.  
   - `watch_input.py` can run continuously and invoke `process_csv` for
     every new file.  
   - `process_inputs.py` performs a one‑shot scan of `input/` (useful in CI).
2. **Start logging** – the first thing `process_csv` does is create or open
   the pipeline log via `create_pipeline_log.create_pipeline_log`, writing
   headers if the file did not already exist.
3. **Record file history** – `track_file_processing_history` appends a
   "started" event for the current file, enabling a complete processing
   timeline.
4. **Process the CSV** – the core business logic lives in
   `processing.process_csv`.  The function is wrapped by the
   `log_execution_time.log_execution_time` decorator, which measures the
   duration of each step and writes elapsed times to the pipeline log.
5. **Validation and error reporting** – if the CSV contains invalid rows or
   other problems, `log_validation_errors.log_validation_errors` is called
   to append detailed error records to the log.
6. **Completion and audit** – after processing finishes (successfully or not)
   a "completed" event is written by `track_file_processing_history`, and
   finally `generate_audit_trail.generate_audit_trail` can be invoked to read
   the pipeline log and emit a summary audit CSV.
7. **Output** – processed files are written alongside the inputs and the
   originals are moved into `input/processed` by the helper scripts.  The
   audit trail and pipeline log live in `output/`.

The orchestrator (`processing.py`) ties these modules together in the order
above, fulfilling the requirement of one function per file plus a central
coordinator.

(see also the original "Orchestrator" section below for a quick listing of
the five helper functions.)

Tests (what CI runs)

- `tests/test_logging_individual.py` verifies each of the five modules independently.
- `tests/test_processing.py` verifies `processing.process_csv` with valid and invalid CSV inputs.

CI (GitHub Actions) - With Automated Error Logging

A workflow at `.github/workflows/ci.yml` installs dependencies and runs `pytest` on push and pull requests. **NEW:** The workflow now includes automated error detection and logging:

1. **Tests** – Runs full test suite with `pytest`
2. **Processing** – Processes any CSVs in `input/` folder with comprehensive error detection
3. **Error Logging** – All errors are automatically captured and logged
4. **Error Summary** – Error summary appears in GitHub Actions run summary
5. **Artifact Storage** – Error logs and processing outputs uploaded as artifacts (30-day retention)
6. **Auto-commit** – Error logs automatically committed to repository if errors occur

See [CI_CD_QUICK_GUIDE.md](CI_CD_QUICK_GUIDE.md) for details on accessing error logs from GitHub Actions.

Project structure (files)

- `create_pipeline_log.py` — creates pipeline CSV log file with headers.
- `log_execution_time.py` — decorator to log function execution duration into the pipeline log.
- `log_validation_errors.py` — append validation error records to the pipeline log.
- `track_file_processing_history.py` — record file start/completion events.
- `generate_audit_trail.py` — read pipeline log and produce an audit CSV summary.
- `processing.py` — orchestrator `process_csv(input_path, output_path, log_csv=None)` that uses the five modules above.
- `pipeline_logging.py` — compatibility wrapper re-exporting the five functions (kept for convenience).
- `error_logging.py` — comprehensive error detection and logging module (NEW!)
- `view_errors.py` — error log viewer and analyzer utility (NEW!)
- `tests/` — contains `test_logging_individual.py` and `test_processing.py` (PyTest).
- `.github/workflows/ci.yml` — GitHub Actions workflow that installs deps and runs `pytest` on push and PR.
- `output/` — processed CSV outputs and pipeline logs.
- `error_logs/` — error logs and detailed error snapshots (NEW!)

Functions implemented

- `create_pipeline_log.create_pipeline_log(csv_file)`
- `log_execution_time.log_execution_time(csv_file)` (decorator)
- `log_validation_errors.log_validation_errors(csv_file, errors)`
- `track_file_processing_history.track_file_processing_history(csv_file, file_path, status, details)`
- `generate_audit_trail.generate_audit_trail(csv_file)`

CI/CD workflow details

- Location: `.github/workflows/ci.yml`
- On events: `push`, `pull_request` (branches: `main`, `master`)
- Steps:
  1. Checkout repository
  2. Set up Python (matrix: 3.10, 3.11)
  3. Install dependencies from `requirements.txt`
  4. Run `pytest -q`

If any test fails, the workflow exits non-zero and the run is marked as failed — CI enforces correctness of the five-module architecture and the orchestrator.