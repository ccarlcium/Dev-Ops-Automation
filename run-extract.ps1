# Run extraction script for the midterm PDF
# Usage: open PowerShell in this folder and run: .\run-extract.ps1
$python = "python"
$script = Join-Path $PSScriptRoot "extract_midterm.py"
if (-not (Test-Path $script)) {
    Write-Error "extract_midterm.py not found in $PSScriptRoot"
    exit 1
}
& $python $script
if ($LASTEXITCODE -ne 0) { Write-Error "Extraction failed with exit code $LASTEXITCODE" }
else { Write-Output "Extraction completed." }
