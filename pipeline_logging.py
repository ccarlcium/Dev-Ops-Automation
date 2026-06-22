"""Compatibility wrapper re-exporting logging functions implemented in
separate modules (each function lives in its own file as required).
"""
from create_pipeline_log import create_pipeline_log
from log_execution_time import log_execution_time
from log_validation_errors import log_validation_errors
from track_file_processing_history import track_file_processing_history
from generate_audit_trail import generate_audit_trail

__all__ = [
    'create_pipeline_log',
    'log_execution_time',
    'log_validation_errors',
    'track_file_processing_history',
    'generate_audit_trail',
]
