import csv
import os
import sys

# Add parent directory to path so imports work from tests/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing import process_csv


def create_csv(path, header, rows):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def test_process_valid(tmp_path):
    inp = tmp_path / 'in_valid.csv'
    out = tmp_path / 'out_valid.csv'
    log = tmp_path / 'pipeline_log.csv'
    header = ['id', 'value']
    rows = [[1, 'a'], [2, 'b'], [3, 'c']]
    create_csv(inp, header, rows)

    processed, errors = process_csv(str(inp), str(out), str(log), required_columns=('id', 'value'))
    assert processed == 3
    assert errors == 0
    assert out.exists()


def test_process_invalid(tmp_path):
    inp = tmp_path / 'in_invalid.csv'
    out = tmp_path / 'out_invalid.csv'
    log = tmp_path / 'pipeline_log.csv'
    header = ['id', 'value']
    rows = [[1, 'a'], ['', 'b'], ['x', 'c']]
    create_csv(inp, header, rows)

    processed, errors = process_csv(str(inp), str(out), str(log), required_columns=('id', 'value'))
    # first row valid, second has empty id, third id not integer -> 1 processed, 2 errors
    assert processed == 1
    assert errors == 2
    assert out.exists()
