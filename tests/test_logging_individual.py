import os
import sys
import csv
import tempfile
import time

# Add parent directory to path so imports work from tests/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from create_pipeline_log import create_pipeline_log
from log_execution_time import log_execution_time
from log_validation_errors import log_validation_errors
from track_file_processing_history import track_file_processing_history
from generate_audit_trail import generate_audit_trail


def test_create_pipeline_log(tmp_path):
    p = tmp_path / 'pl.csv'
    p2 = create_pipeline_log(str(p))
    assert os.path.isfile(p2)
    with open(p2, 'r', encoding='utf-8') as fh:
        header = fh.readline().strip()
        assert 'timestamp' in header


def test_log_execution_time_decorator(tmp_path):
    log = tmp_path / 'pl.csv'
    create_pipeline_log(str(log))

    @log_execution_time(str(log))
    def add(a, b):
        return a + b

    assert add(2, 3) == 5
    # ensure a row was appended
    with open(str(log), 'r', encoding='utf-8') as fh:
        lines = fh.read().splitlines()
        assert len(lines) >= 2
        assert 'execution' in lines[-1]


def test_log_validation_errors_and_history_and_audit(tmp_path):
    log = tmp_path / 'pl.csv'
    create_pipeline_log(str(log))
    errors = [
        {'file_path': 'inp.csv', 'details': 'bad row', 'function_name': 'validate'},
    ]
    log_validation_errors(str(log), errors)
    track_file_processing_history(str(log), 'inp.csv', 'failed', 'reason=x')

    # generate audit
    audit = generate_audit_trail(str(log))
    assert os.path.isfile(audit)
    with open(audit, 'r', encoding='utf-8') as fh:
        content = fh.read()
        assert 'validate' in content or '<root>' in content
