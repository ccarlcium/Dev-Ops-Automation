#!/usr/bin/env bash
# Script to verify CI/CD error logging configuration
# Run this locally to check if everything is set up correctly

echo "=========================================="
echo "CI/CD Error Logging Setup Verification"
echo "=========================================="
echo

# Check if CI workflow file exists
if [ -f .github/workflows/ci.yml ]; then
    echo "✓ GitHub Actions workflow found: .github/workflows/ci.yml"
else
    echo "✗ GitHub Actions workflow NOT found"
    exit 1
fi

echo

# Check for error_logging.py
if [ -f error_logging.py ]; then
    echo "✓ error_logging.py module exists"
else
    echo "✗ error_logging.py module NOT found"
    exit 1
fi

# Check for view_errors.py
if [ -f view_errors.py ]; then
    echo "✓ view_errors.py utility exists"
else
    echo "✗ view_errors.py utility NOT found"
    exit 1
fi

# Check for process_inputs.py
if [ -f process_inputs.py ]; then
    echo "✓ process_inputs.py script exists"
else
    echo "✗ process_inputs.py script NOT found"
    exit 1
fi

echo

# Check if error_logs directory exists
if [ -d error_logs ]; then
    error_count=$(find error_logs -type f | wc -l)
    echo "✓ error_logs directory exists ($error_count files)"
else
    echo "✓ error_logs directory will be created on first error"
fi

echo

# Check required imports in process_inputs.py
if grep -q "from error_logging import" process_inputs.py; then
    echo "✓ process_inputs.py imports error_logging"
else
    echo "✗ process_inputs.py does NOT import error_logging"
    exit 1
fi

# Check if processing.py has error_logging import
if grep -q "from error_logging import" processing.py; then
    echo "✓ processing.py imports error_logging"
else
    echo "✗ processing.py does NOT import error_logging"
    exit 1
fi

echo

# Check CI workflow has process_inputs.py
if grep -q "python process_inputs.py" .github/workflows/ci.yml; then
    echo "✓ CI workflow runs process_inputs.py"
else
    echo "✗ CI workflow does NOT run process_inputs.py"
    exit 1
fi

# Check CI workflow has error logging display
if grep -q "view_errors.py" .github/workflows/ci.yml; then
    echo "✓ CI workflow displays error summary"
else
    echo "✗ CI workflow does NOT display error summary"
    exit 1
fi

# Check CI workflow uploads artifacts
if grep -q "upload-artifact" .github/workflows/ci.yml; then
    echo "✓ CI workflow uploads error artifacts"
else
    echo "✗ CI workflow does NOT upload artifacts"
    exit 1
fi

echo

echo "=========================================="
echo "All checks passed! ✓"
echo "=========================================="
echo

echo "Next steps:"
echo "1. Push your changes to GitHub"
echo "2. Check Actions tab for the workflow run"
echo "3. View error summary in the run output"
echo "4. Download error-logs artifact if needed"
echo

echo "Local testing:"
echo "  python process_inputs.py     # Process files locally"
echo "  python view_errors.py         # View errors locally"
echo
