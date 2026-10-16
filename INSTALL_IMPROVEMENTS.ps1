$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
if (-not (Test-Path (Join-Path $root 'backend/main.py'))) { throw 'Run inside your ScopeGuard repo.' }
$source = Split-Path -Parent $MyInvocation.MyCommand.Path
foreach ($path in @('tools/impact_benchmark.py','tests/test_impact_benchmark.py','docs/PRODUCT_VALIDATION.md','docs/JUDGE_DEMO_RUNBOOK.md','docs/PRIORITY_FIXES.md','evaluation/pilot_results_TEMPLATE.csv')) {
    $target = Join-Path $root $path
    if (Test-Path $target) { throw "File already exists (safe stop): $path" }
    $folder = Split-Path -Parent $target
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
    Copy-Item (Join-Path $source $path) $target
    Write-Host "Added: $path"
}
Write-Host 'Install complete. Run .\.venv\Scripts\python.exe -m pytest -q' -ForegroundColor Green
