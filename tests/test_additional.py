import os
import sys
import csv
import time

# Add parent directory to path so imports work from tests/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from create_pipeline_log import create_pipeline_log
from log_execution_time import log_execution_time
from log_validation_errors import log_validation_errors
from generate_audit_trail import generate_audit_trail
from processing import process_csv


def test_create_pipeline_log_overwrites(tmp_path):
    p = tmp_path / 'pl.csv'
    # create a file with content
    p.write_text('garbage')
    import os
    import csv
    import time
    from create_pipeline_log import create_pipeline_log
    from log_execution_time import log_execution_time
    from log_validation_errors import log_validation_errors
    from generate_audit_trail import generate_audit_trail
    from processing import process_csv


    def test_create_pipeline_log_overwrites(tmp_path):
        p = tmp_path / 'pl.csv'
        # create a file with content
        p.write_text('garbage')
        create_pipeline_log(str(p))
        content = p.read_text()
        assert 'timestamp' in content


    def test_log_execution_time_records_duration(tmp_path):
        log = tmp_path / 'pl.csv'
        create_pipeline_log(str(log))

        @log_execution_time(str(log))
        def sleepy():
            time.sleep(0.02)

        sleepy()
        # read last row
        with open(str(log), 'r', encoding='utf-8') as fh:
            lines = fh.read().splitlines()
        last = lines[-1].split(',')
        # duration_ms is at index 4 in header
        assert int(last[4]) >= 10


    def test_log_validation_errors_no_errors(tmp_path):
        log = tmp_path / 'pl.csv'
        create_pipeline_log(str(log))
        # calling with None should do nothing (no exceptions)
        log_validation_errors(str(log), None)
        # only header exists
        with open(str(log), 'r', encoding='utf-8') as fh:
            lines = fh.read().splitlines()
        assert len(lines) == 1


    def test_generate_audit_trail_counts(tmp_path):
        log = tmp_path / 'pl.csv'
        # create a fake pipeline log with multiple entries
        with open(str(log), 'w', newline='', encoding='utf-8') as fh:
            fh.write('timestamp,level,event,function_name,duration_ms,file_path,status,details\n')
            fh.write('t,INFO,execution,foo,100,,,\n')
            fh.write('t,ERROR,execution,foo,0,,,\n')
            fh.write('t,INFO,execution,bar,200,,,\n')
            fh.write('t,ERROR,validation_error,bar,,,file.csv,missing\n')
        audit = generate_audit_trail(str(log))
        with open(audit, 'r', encoding='utf-8') as fh:
            content = fh.read()
        assert 'foo' in content and 'bar' in content


    def test_process_csv_missing_column(tmp_path):
        inp = tmp_path / 'in.csv'
        out = tmp_path / 'out.csv'
        log = tmp_path / 'pipeline_log.csv'
        # missing 'value' column
        with open(inp, 'w', newline='', encoding='utf-8') as fh:
            w = csv.writer(fh)
            w.writerow(['id','other'])
            w.writerow([1,'x'])
        processed, errors = process_csv(str(inp), str(out), str(log), required_columns=('id','value'))
        assert processed == 0
        assert errors >= 1