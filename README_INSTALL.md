# ScopeGuard quality + validation add-on (non-destructive)

The **existing repository is the project**. This pack adds a usable real-world pilot and judge proof. It does not overwrite `backend/main.py`, the frontend, or your existing README.

## Install on Windows

1. Extract ZIP to a temporary directory (e.g. Downloads\scopeguard-pack).
2. Open your VS Code PowerShell inside `C:\Users\Lenovo\Desktop\scopeguard-ai`.
3. Create a feature branch before copying files: `git switch main; git pull --ff-only origin main; git switch -c feat/pilot-proof-and-judge-demo`.
4. Run `powershell -ExecutionPolicy Bypass -File "C:\Users\Lenovo\Downloads\scopeguard-pack\INSTALL_IMPROVEMENTS.ps1"` (adjust path to extracted location).
5. Run ` .\.venv\Scripts\python.exe -m pytest -q`. In the previously reported repo the baseline was 62 tests; this pack adds 5 tests, so **67 pass would be expected** if the existing code is unchanged. This figure is a target, not a verified Windows result.
6. `git status; git add tools/impact_benchmark.py tests/test_impact_benchmark.py docs/PRODUCT_VALIDATION.md docs/JUDGE_DEMO_RUNBOOK.md docs/PRIORITY_FIXES.md evaluation/pilot_results_TEMPLATE.csv; git diff --cached --check; git commit -m "feat: add measured pilot benchmarking and demo evidence"; git push -u origin feat/pilot-proof-and-judge-demo`. Open a PR and review before merging.

## Run the actual study

Copy `evaluation/pilot_results_TEMPLATE.csv` to `evaluation/pilot_results.csv`. Gather **real paired results**, no placeholders. Then:

```powershell
.\.venv\Scripts\python.exe tools\impact_benchmark.py --input evaluation\pilot_results.csv
```

The benchmark **refuses empty data**. Avoid committing the raw pilot CSV if it contains any participant-identifying information. Share aggregated results only with consent.

## No unverified product claims

This pack improves **measurement, reproducibility, submission and product validation**. It does not claim to implement multi-hop graph algorithms, optimize model latency or fix unresolved model classifications. To safely change the backend, inspect and patch the current actual repo first.
