from pipeline_logging import (
    create_pipeline_log,
    log_execution_time,
    log_validation_errors,
    track_file_processing_history,
    generate_audit_trail,
)
import os
import tempfile

# Quick integration test
def run_test():
    tmpdir = tempfile.mkdtemp(prefix='pltest_')
    log = os.path.join(tmpdir, 'pipeline_test_log.csv')
    create_pipeline_log(log)

    @log_execution_time(log)
    def fast(a, b):
        return a + b

    @log_execution_time(log)
    def slow(n=1000000):
        s = 0
        for i in range(n):
            s += i
        return s

    fast(1,2)
    try:
        # call a function that raises to test error logging
        @log_execution_time(log)
        def bad():
            raise ValueError('boom')
        try:
            bad()
        except ValueError:
            pass
    except Exception:
        pass

    # validation errors
    errors = [
        {'file_path':'/data/file1.csv','details':'missing header','function_name':'validate_rows'},
        {'file_path':'/data/file2.csv','details':'invalid date','function_name':'validate_rows'},
    ]
    log_validation_errors(log, errors)

    # file processing history
    track_file_processing_history(log, '/data/file1.csv', 'completed', 'rows=100')
    track_file_processing_history(log, '/data/file2.csv', 'failed', 'reason=validation')

    audit = generate_audit_trail(log)
    print('Log:', log)
    print('Audit:', audit)
    with open(log, 'r', encoding='utf-8') as fh:
        print('\n--- LOG CONTENTS ---')
        print(fh.read())

    with open(audit, 'r', encoding='utf-8') as fh:
        print('\n--- AUDIT CONTENTS ---')
        print(fh.read())

if __name__ == '__main__':
    run_test()
