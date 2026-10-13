# ScopeGuard AI — Next steps after the approved PDF

## What is verified
- Gemma analysis ran on your Windows laptop.
- You created a three-item INR 8,500 proposal.
- Customer approval was recorded.
- PDF opened and shows APPROVED, correct items and amount.

## What was incorrect in the old PDF
The Careers page cited the third-revision request. The PDF reflects the original stored proposal; this does NOT change retroactively.

## Using the 1.1 package
1. Keep a copy of your old project as a backup, especially `data/scopeguard.db`.
2. Extract this ZIP to a **new** directory, such as `C:\Users\Lenovo\ScopeGuard-AI-v1-1`.
3. VS Code > File > Open Folder > select the extracted project folder (the folder containing `start.ps1`).
4. In VS Code PowerShell run: `powershell -ExecutionPolicy Bypass -File .\start.ps1`
5. Use the URL printed in the terminal. The launcher picks an available port from 8001–8005.
6. Load demo example > Analyze scope with Gemma. Confirm that Careers is not citing the third-revision request.
7. Enter hours 3, 3, 2.5 and rate 1000. Create a new proposal and review the generated approval link; approve the new proposal and download its PDF.
8. Run tests: `.\.venv\Scripts\python.exe -m pytest -q`.

## Current boundaries
- Use synthetic demo data only: share token alone enables approval/rejection; no account identity verification.
- Full PDF contract upload, automatic contract clause linking, hosted model inference, Sentry instrumentation and production-scale tenancy are NOT implemented.
- This is an MVP and does not determine whether charges are legally enforceable.
- Don't enter an old approval token into a public website.

## Judge-facing next priorities
1. Record a short demo including the corrected evidence and both roles.
2. Measure 20+ labeled test scenarios, report failures honestly.
3. Have a real freelancer try it with synthetic data and note feedback.
4. Publish a DEV article with the repository, video link, and measured outcomes, without inventing partner integrations.
