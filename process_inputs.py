import glob, os
import csv
from processing import process_csv, _validate_row
from error_logging import log_error, get_error_summary, save_processing_summary, save_processing_run_log

def _validate_file(file_path, required_columns=None, auto_detect=False):
    """Validate file structure before processing.

    By default (when `auto_detect` is False) the function keeps the test-suite
    expectation of requiring ('id','value') when `required_columns` is not
    provided. When `auto_detect` is True the function will accept whatever
    headers are present in the file (useful for the CLI/script run).
    """
    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Must have headers
            if not reader.fieldnames:
                return False, "Empty file or no headers"

            # Decide required columns. Preserve test-suite expectation that
            # omitting `required_columns` requires ('id','value'), but allow
            # callers to request auto-detection by setting `auto_detect=True`.
            if required_columns is None:
                if auto_detect:
                    required_columns = reader.fieldnames
                else:
                    required_columns = ('id', 'value')

            # Check for missing columns
            missing = [col for col in required_columns if col not in reader.fieldnames]
            if missing:
                return False, f"Missing columns: {', '.join(missing)}"

            # Check at least one row
            try:
                next(reader)
            except StopIteration:
                return False, "File has headers but no data rows"

            return True, "Valid"

    except UnicodeDecodeError as ue:
        return False, f"Encoding error: {str(ue)}"
    except PermissionError as pe:
        return False, f"Permission denied: {str(pe)}"
    except FileNotFoundError as fnfe:
        return False, f"File not found: {str(fnfe)}"
    except Exception as e:
        return False, str(e)

def main():
    """Process all CSV files in input directory with comprehensive error logging."""
    try:
        os.makedirs('output', exist_ok=True)
        log = 'output/pipeline_log.csv'
        
        # Get all CSV files in input directory
        input_files = glob.glob('input/*.csv')
        
        if not input_files:
            print("No CSV files found in input/ directory")
            return
        
        print(f"Found {len(input_files)} CSV file(s) to process")
        
        processed_count = 0
        failed_count = 0
        
        for f in input_files:
            try:
                out = os.path.join('output', 'processed_' + os.path.basename(f))
                print(f"\nProcessing {f} -> {out}")
                
                # Validate file before processing
                is_valid, msg = _validate_file(f, auto_detect=True)
                if not is_valid:
                    error_msg = f"Validation error: {msg}"
                    print(f"  ❌ {error_msg}")
                    log_error(
                        error_type='file_validation_error',
                        message=error_msg,
                        file_path=f,
                        function_name='main',
                    )
                    failed_count += 1
                    continue
                
                # Process the CSV file
                try:
                    rows_processed, errors_count = process_csv(f, out, log_csv=log)
                    print(f"  ✓ Processed: {rows_processed} rows, {errors_count} error(s)")
                    processed_count += 1
                    
                except PermissionError as pe:
                    error_msg = f"Permission denied: {str(pe)}"
                    print(f"  ❌ {error_msg}")
                    log_error(
                        error_type='permission_error',
                        message=error_msg,
                        file_path=f,
                        function_name='main',
                        exception=pe,
                    )
                    failed_count += 1
                    
                except FileNotFoundError as fnfe:
                    error_msg = f"File not found: {str(fnfe)}"
                    print(f"  ❌ {error_msg}")
                    log_error(
                        error_type='file_not_found_error',
                        message=error_msg,
                        file_path=f,
                        function_name='main',
                        exception=fnfe,
                    )
                    failed_count += 1
                    
                except Exception as pe:
                    error_msg = f"Error processing file: {str(pe)}"
                    print(f"  ❌ {error_msg}")
                    log_error(
                        error_type='processing_error',
                        message=error_msg,
                        file_path=f,
                        function_name='main',
                        exception=pe,
                    )
                    failed_count += 1
                    
            except Exception as f_err:
                error_msg = f"Unexpected error with file {f}: {str(f_err)}"
                print(f"  ❌ {error_msg}")
                log_error(
                    error_type='unexpected_error',
                    message=error_msg,
                    file_path=f,
                    function_name='main',
                    exception=f_err,
                )
                failed_count += 1
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total files: {len(input_files)}")
        print(f"Successfully processed: {processed_count}")
        print(f"Failed: {failed_count}")
        print(f"Pipeline log: {log}")
        print(f"Error logs: error_logs/")
        
        # Get and display error summary
        try:
            summary = get_error_summary()
            if summary['total_errors'] > 0:
                print(f"\n{'='*60}")
                print(f"ERROR SUMMARY")
                print(f"{'='*60}")
                print(f"Total errors logged: {summary['total_errors']}")
                if summary['errors_by_type']:
                    print(f"Errors by type:")
                    for error_type, count in summary['errors_by_type'].items():
                        print(f"  - {error_type}: {count}")
                if summary['files_with_errors']:
                    print(f"Files with errors: {len(summary['files_with_errors'])}")
                    for file_path in summary['files_with_errors']:
                        print(f"  - {file_path}")
        except Exception as e:
            print(f"Warning: Could not generate error summary: {str(e)}")
        
        print(f"{'='*60}\n")
        
        # Save processing summary to error_logs/ (NEW!)
        try:
            save_processing_summary(
                total_files=len(input_files),
                processed_count=processed_count,
                failed_count=failed_count,
                pipeline_log=log,
            )
            save_processing_run_log(
                total_files=len(input_files),
                processed_count=processed_count,
                failed_count=failed_count,
                pipeline_log=log,
            )
            print(f"✓ Processing summary saved to: error_logs/processing_summary.json")
            print(f"✓ Processing run log saved to: error_logs/processing_runs.csv\n")
        except Exception as e:
            print(f"Warning: Could not save processing summary: {str(e)}\n")
        
    except Exception as e:
        error_msg = f"Critical error in main: {str(e)}"
        print(f"❌ {error_msg}")
        log_error(
            error_type='critical_error',
            message=error_msg,
            function_name='main',
            exception=e,
        )
        raise

if __name__ == '__main__':
    main()
