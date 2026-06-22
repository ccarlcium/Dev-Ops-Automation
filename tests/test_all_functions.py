"""Comprehensive pytest test suite for all functions in the pipeline."""
import csv
import os
import sys
import tempfile
import time
import pytest
from pathlib import Path

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from create_pipeline_log import create_pipeline_log
from log_execution_time import log_execution_time
from log_validation_errors import log_validation_errors
from track_file_processing_history import track_file_processing_history
from generate_audit_trail import generate_audit_trail
from logging_utils import _ensure_dir_exists, _write_row, _now_ts, DEFAULT_HEADERS
from processing import process_csv, _validate_row, _now_iso
from process_inputs import _validate_file


# ============================================================================
# Tests for create_pipeline_log
# ============================================================================

class TestCreatePipelineLog:
    """Test suite for create_pipeline_log function."""
    
    def test_create_pipeline_log_basic(self, tmp_path):
        """Test creating pipeline log with default path."""
        log_file = tmp_path / 'pipeline_log.csv'
        result = create_pipeline_log(str(log_file))
        
        assert os.path.isfile(result)
        assert result == os.path.abspath(str(log_file))
        
    def test_create_pipeline_log_with_headers(self, tmp_path):
        """Test that created log has correct headers."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            assert reader.fieldnames == DEFAULT_HEADERS
            
    def test_create_pipeline_log_overwrites_existing(self, tmp_path):
        """Test that creating log overwrites existing file."""
        log_file = tmp_path / 'pipeline_log.csv'
        log_file.write_text('garbage content\n')
        
        create_pipeline_log(str(log_file))
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()
        assert len(lines) == 1  # only header
        assert 'timestamp' in lines[0]
        
    def test_create_pipeline_log_creates_nested_dirs(self, tmp_path):
        """Test that nested directories are created."""
        log_file = tmp_path / 'deep' / 'nested' / 'dirs' / 'pipeline_log.csv'
        result = create_pipeline_log(str(log_file))
        
        assert os.path.isfile(result)
        assert log_file.exists()


# ============================================================================
# Tests for log_execution_time decorator
# ============================================================================

class TestLogExecutionTime:
    """Test suite for log_execution_time decorator."""
    
    def test_decorator_basic(self, tmp_path):
        """Test that decorator logs function execution."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        @log_execution_time(str(log_file))
        def add(a, b):
            return a + b
        
        result = add(2, 3)
        assert result == 5
        
        # Check log has entry
        with open(log_file, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()
        assert len(lines) == 2  # header + 1 entry
        
    def test_decorator_records_function_name(self, tmp_path):
        """Test that decorator records correct function name."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        @log_execution_time(str(log_file))
        def test_function():
            pass
        
        test_function()
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                assert row['function_name'] == 'test_function'
                assert row['event'] == 'execution'
                
    def test_decorator_records_duration(self, tmp_path):
        """Test that decorator records execution duration."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        @log_execution_time(str(log_file))
        def sleepy():
            time.sleep(0.05)
        
        sleepy()
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                duration = int(row['duration_ms'])
                assert duration >= 40  # at least 40ms (accounting for overhead)
                
    def test_decorator_success_level(self, tmp_path):
        """Test that successful execution records INFO level."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        @log_execution_time(str(log_file))
        def successful():
            return "ok"
        
        successful()
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                assert row['level'] == 'INFO'
                assert row['details'] == ''
                
    def test_decorator_exception_level(self, tmp_path):
        """Test that exception execution records ERROR level."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        @log_execution_time(str(log_file))
        def failing():
            raise ValueError("test error")
        
        with pytest.raises(ValueError):
            failing()
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                assert row['level'] == 'ERROR'
                assert row['details'] == 'exception'


# ============================================================================
# Tests for log_validation_errors
# ============================================================================

class TestLogValidationErrors:
    """Test suite for log_validation_errors function."""
    
    def test_log_validation_errors_basic(self, tmp_path):
        """Test logging a single validation error."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        errors = [
            {'file_path': 'test.csv', 'details': 'bad value', 'function_name': 'validate'}
        ]
        log_validation_errors(str(log_file), errors)
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()
        assert len(lines) == 2  # header + 1 error
        
    def test_log_validation_errors_multiple(self, tmp_path):
        """Test logging multiple validation errors."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        errors = [
            {'file_path': 'test.csv', 'details': 'error 1', 'function_name': 'validate'},
            {'file_path': 'test.csv', 'details': 'error 2', 'function_name': 'validate'},
            {'file_path': 'test.csv', 'details': 'error 3', 'function_name': 'validate'},
        ]
        log_validation_errors(str(log_file), errors)
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()
        assert len(lines) == 4  # header + 3 errors
        
    def test_log_validation_errors_empty(self, tmp_path):
        """Test that empty error list does nothing."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        log_validation_errors(str(log_file), [])
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()
        assert len(lines) == 1  # only header
        
    def test_log_validation_errors_none(self, tmp_path):
        """Test that None error list does nothing."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        log_validation_errors(str(log_file), None)
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()
        assert len(lines) == 1  # only header
        
    def test_log_validation_errors_event_type(self, tmp_path):
        """Test that validation errors have correct event type."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        errors = [{'file_path': 'test.csv', 'details': 'error', 'function_name': 'validate'}]
        log_validation_errors(str(log_file), errors)
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                assert row['event'] == 'validation_error'
                assert row['level'] == 'ERROR'


# ============================================================================
# Tests for track_file_processing_history
# ============================================================================

class TestTrackFileProcessingHistory:
    """Test suite for track_file_processing_history function."""
    
    def test_track_file_started(self, tmp_path):
        """Test tracking file processing start."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        track_file_processing_history(str(log_file), 'test.csv', 'started')
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                assert row['status'] == 'started'
                assert row['file_path'] == 'test.csv'
                assert row['event'] == 'file_processing'
                
    def test_track_file_completed(self, tmp_path):
        """Test tracking file processing completion."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        track_file_processing_history(str(log_file), 'test.csv', 'completed', details='processed=10')
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                assert row['status'] == 'completed'
                assert row['details'] == 'processed=10'
                
    def test_track_file_failed(self, tmp_path):
        """Test tracking file processing failure."""
        log_file = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log_file))
        
        track_file_processing_history(str(log_file), 'test.csv', 'failed', details='reason=error')
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                assert row['status'] == 'failed'
                assert row['level'] == 'INFO'


# ============================================================================
# Tests for generate_audit_trail
# ============================================================================

class TestGenerateAuditTrail:
    """Test suite for generate_audit_trail function."""
    
    def test_generate_audit_trail_basic(self, tmp_path):
        """Test generating basic audit trail."""
        log_file = tmp_path / 'pipeline_log.csv'
        
        # Create a fake pipeline log
        with open(log_file, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=DEFAULT_HEADERS)
            writer.writeheader()
            writer.writerow({
                'timestamp': '2026-01-01T00:00:00Z',
                'level': 'INFO',
                'event': 'execution',
                'function_name': 'test_func',
                'duration_ms': '100',
                'file_path': '',
                'status': '',
                'details': ''
            })
        
        audit_file = generate_audit_trail(str(log_file))
        
        assert os.path.isfile(audit_file)
        assert 'audit' in audit_file
        
    def test_generate_audit_trail_custom_output(self, tmp_path):
        """Test generating audit trail with custom output path."""
        log_file = tmp_path / 'pipeline_log.csv'
        output_file = tmp_path / 'custom_audit.csv'
        
        with open(log_file, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=DEFAULT_HEADERS)
            writer.writeheader()
        
        result = generate_audit_trail(str(log_file), str(output_file))
        
        assert result == os.path.abspath(str(output_file))
        assert os.path.isfile(output_file)
        
    def test_generate_audit_trail_aggregates_stats(self, tmp_path):
        """Test that audit trail aggregates function statistics."""
        log_file = tmp_path / 'pipeline_log.csv'
        
        with open(log_file, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=DEFAULT_HEADERS)
            writer.writeheader()
            writer.writerow({
                'timestamp': '2026-01-01T00:00:00Z',
                'level': 'INFO',
                'event': 'execution',
                'function_name': 'func_a',
                'duration_ms': '100',
                'file_path': '',
                'status': '',
                'details': ''
            })
            writer.writerow({
                'timestamp': '2026-01-01T00:00:00Z',
                'level': 'INFO',
                'event': 'execution',
                'function_name': 'func_a',
                'duration_ms': '200',
                'file_path': '',
                'status': '',
                'details': ''
            })
        
        audit_file = generate_audit_trail(str(log_file))
        
        with open(audit_file, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if row['function_name'] == 'func_a':
                    assert int(row['count']) == 2
                    assert int(row['total_duration_ms']) == 300
                    
    def test_generate_audit_trail_missing_file(self, tmp_path):
        """Test error handling when log file doesn't exist."""
        log_file = tmp_path / 'nonexistent.csv'
        
        with pytest.raises(FileNotFoundError):
            generate_audit_trail(str(log_file))


# ============================================================================
# Tests for logging_utils
# ============================================================================

class TestLoggingUtils:
    """Test suite for logging_utils helper functions."""
    
    def test_ensure_dir_exists_new_dir(self, tmp_path):
        """Test creating new directory."""
        new_dir = tmp_path / 'new' / 'dir' / 'path' / 'file.csv'
        _ensure_dir_exists(str(new_dir))
        
        parent_dir = new_dir.parent
        assert parent_dir.exists()
        
    def test_ensure_dir_exists_existing_dir(self, tmp_path):
        """Test that existing directory doesn't raise error."""
        _ensure_dir_exists(str(tmp_path / 'file.csv'))
        assert tmp_path.exists()
        
    def test_write_row_creates_header(self, tmp_path):
        """Test that write_row creates header if file doesn't exist."""
        log_file = tmp_path / 'test.csv'
        
        _write_row(str(log_file), {
            'timestamp': '2026-01-01T00:00:00Z',
            'level': 'INFO',
            'event': 'test'
        })
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            assert reader.fieldnames == DEFAULT_HEADERS
            rows = list(reader)
            assert len(rows) == 1
            
    def test_write_row_appends_to_existing(self, tmp_path):
        """Test that write_row appends to existing file."""
        log_file = tmp_path / 'test.csv'
        create_pipeline_log(str(log_file))
        
        _write_row(str(log_file), {'timestamp': '2026-01-01T00:00:00Z', 'level': 'INFO'})
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()
        assert len(lines) == 2  # header + 1 row
        
    def test_write_row_empty_values_as_strings(self, tmp_path):
        """Test that None values are converted to empty strings."""
        log_file = tmp_path / 'test.csv'
        create_pipeline_log(str(log_file))
        
        _write_row(str(log_file), {
            'timestamp': '2026-01-01T00:00:00Z',
            'level': 'INFO',
            'duration_ms': None
        })
        
        with open(log_file, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                assert row['duration_ms'] == ''
                
    def test_now_ts_format(self):
        """Test that _now_ts returns correct ISO format."""
        ts = _now_ts()
        
        assert ts.endswith('Z')
        assert len(ts) > 20  # ISO format is at least 20 chars
        assert 'T' in ts


# ============================================================================
# Tests for processing._validate_row
# ============================================================================

class TestValidateRow:
    """Test suite for _validate_row function."""
    
    def test_validate_row_valid(self):
        """Test validation of valid row."""
        row = {'id': '1', 'value': 'test'}
        errors = _validate_row(row, ('id', 'value'))
        
        assert len(errors) == 0
        
    def test_validate_row_missing_column(self):
        """Test validation fails when column is missing."""
        row = {'id': '1'}
        errors = _validate_row(row, ('id', 'value'))
        
        assert len(errors) > 0
        assert 'missing column' in errors[0]['details']
        
    def test_validate_row_empty_required_column(self):
        """Test validation fails when required column is empty."""
        row = {'id': '', 'value': 'test'}
        errors = _validate_row(row, ('id', 'value'))
        
        assert len(errors) > 0
        assert 'empty value' in errors[0]['details']
        
    def test_validate_row_non_integer_id(self):
        """Test validation fails when id is not integer."""
        row = {'id': 'not_a_number', 'value': 'test'}
        errors = _validate_row(row, ('id', 'value'))
        
        assert len(errors) > 0
        assert 'id not integer' in errors[0]['details']
        
    def test_validate_row_whitespace_only(self):
        """Test validation fails when column has only whitespace."""
        row = {'id': '   ', 'value': 'test'}
        errors = _validate_row(row, ('id', 'value'))
        
        assert len(errors) > 0


# ============================================================================
# Tests for processing.process_csv
# ============================================================================

class TestProcessCSV:
    """Test suite for process_csv function."""
    
    def setup_method(self):
        """Setup test data."""
        self.header = ['id', 'value']
        
    def create_csv(self, path, rows):
        """Helper to create test CSV."""
        with open(path, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(self.header)
            for row in rows:
                writer.writerow(row)
                
    def test_process_csv_valid_rows(self, tmp_path):
        """Test processing valid rows."""
        inp = tmp_path / 'input.csv'
        out = tmp_path / 'output.csv'
        log = tmp_path / 'log.csv'
        
        self.create_csv(inp, [['1', 'a'], ['2', 'b'], ['3', 'c']])
        
        processed, errors = process_csv(str(inp), str(out), str(log))
        
        assert processed == 3
        assert errors == 0
        assert out.exists()
        
    def test_process_csv_invalid_rows(self, tmp_path):
        """Test processing with invalid rows."""
        inp = tmp_path / 'input.csv'
        out = tmp_path / 'output.csv'
        log = tmp_path / 'log.csv'
        
        self.create_csv(inp, [['1', 'a'], ['', 'b'], ['x', 'c']])
        
        processed, errors = process_csv(str(inp), str(out), str(log))
        
        assert processed == 1  # only first row valid
        assert errors == 2  # empty id, non-integer id
        
    def test_process_csv_missing_column(self, tmp_path):
        """Test processing with missing required column."""
        inp = tmp_path / 'input.csv'
        out = tmp_path / 'output.csv'
        log = tmp_path / 'log.csv'
        
        with open(inp, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(['id', 'other'])
            writer.writerow(['1', 'x'])
        
        processed, errors = process_csv(str(inp), str(out), str(log), required_columns=('id', 'value'))
        
        assert processed == 0
        assert errors >= 1
        
    def test_process_csv_creates_log(self, tmp_path):
        """Test that process_csv creates log file."""
        inp = tmp_path / 'input.csv'
        out = tmp_path / 'output.csv'
        log = tmp_path / 'log.csv'
        
        self.create_csv(inp, [['1', 'a']])
        
        process_csv(str(inp), str(out), str(log))
        
        assert log.exists()
        
    def test_process_csv_output_format(self, tmp_path):
        """Test that output CSV has correct format."""
        inp = tmp_path / 'input.csv'
        out = tmp_path / 'output.csv'
        log = tmp_path / 'log.csv'
        
        self.create_csv(inp, [['1', 'a'], ['2', 'b']])
        
        process_csv(str(inp), str(out), str(log))
        
        with open(out, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]['id'] == '1'
            assert rows[0]['value'] == 'a'


# ============================================================================
# Tests for process_inputs._validate_file
# ============================================================================

class TestValidateFile:
    """Test suite for _validate_file function."""
    
    def test_validate_file_valid_structure(self, tmp_path):
        """Test validation of file with valid structure."""
        csv_file = tmp_path / 'test.csv'
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(['id', 'value'])
            writer.writerow(['1', 'a'])
        
        is_valid, msg = _validate_file(str(csv_file))
        
        assert is_valid is True
        assert msg == 'Valid'
        
    def test_validate_file_missing_column(self, tmp_path):
        """Test validation fails when required column is missing."""
        csv_file = tmp_path / 'test.csv'
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(['id', 'other'])
        
        is_valid, msg = _validate_file(str(csv_file))
        
        assert is_valid is False
        assert 'Missing columns' in msg
        assert 'value' in msg
        
    def test_validate_file_empty(self, tmp_path):
        """Test validation fails for empty file."""
        csv_file = tmp_path / 'test.csv'
        csv_file.write_text('')
        
        is_valid, msg = _validate_file(str(csv_file))
        
        assert is_valid is False
        
    def test_validate_file_nonexistent(self, tmp_path):
        """Test validation fails for nonexistent file."""
        csv_file = tmp_path / 'nonexistent.csv'
        
        is_valid, msg = _validate_file(str(csv_file))
        
        assert is_valid is False
        
    def test_validate_file_custom_columns(self, tmp_path):
        """Test validation with custom required columns."""
        csv_file = tmp_path / 'test.csv'
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(['name', 'age'])
            writer.writerow(['John', '30'])
        
        is_valid, msg = _validate_file(str(csv_file), required_columns=('name', 'age'))
        
        assert is_valid is True


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple functions."""
    
    def test_full_pipeline(self, tmp_path):
        """Test complete pipeline from input to audit."""
        inp = tmp_path / 'input.csv'
        out = tmp_path / 'output.csv'
        log = tmp_path / 'pipeline_log.csv'
        
        # Create input CSV
        with open(inp, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(['id', 'value'])
            writer.writerow(['1', 'data1'])
            writer.writerow(['', 'data2'])
            writer.writerow(['3', 'data3'])
        
        # Process CSV
        processed, errors = process_csv(str(inp), str(out), str(log))
        
        # Generate audit
        audit = generate_audit_trail(str(log))
        
        assert processed == 2
        assert errors == 1
        assert log.exists()
        assert os.path.isfile(audit)
        assert out.exists()
        
    def test_multiple_files_with_logging(self, tmp_path):
        """Test processing multiple files with comprehensive logging."""
        log = tmp_path / 'pipeline_log.csv'
        create_pipeline_log(str(log))
        
        # Process multiple files
        for i in range(3):
            inp = tmp_path / f'input{i}.csv'
            out = tmp_path / f'output{i}.csv'
            
            with open(inp, 'w', newline='', encoding='utf-8') as fh:
                writer = csv.writer(fh)
                writer.writerow(['id', 'value'])
                writer.writerow([str(i), f'value{i}'])
            
            track_file_processing_history(str(log), str(inp), 'started')
            process_csv(str(inp), str(out), str(log))
            track_file_processing_history(str(log), str(inp), 'completed')
        
        # Verify audit trail
        audit = generate_audit_trail(str(log))
        assert os.path.isfile(audit)
        
        with open(audit, 'r', encoding='utf-8') as fh:
            content = fh.read()
        assert 'file_processing' in content or '<root>' in content
