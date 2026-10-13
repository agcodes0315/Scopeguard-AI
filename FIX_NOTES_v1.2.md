# ScopeGuard AI v1.2 — Billing safety patch

## Fixes
- Explicitly included first-round phone, color and heading edits now classify as `included` for the supplied test agreement.
- Pricing UI only displays findings classified as `potential_extra` with a verified agreement excerpt and client request quote. If none qualify, the proposal button is disabled and extra total remains 0.
- Server requires an actual saved analysis ID and exact item indices for every new proposal. The server independently rejects included, unverified, mismatched or forged items (HTTP 422), regardless of frontend changes.
- Seven automated tests pass, including the original incorrectly billed ₹8,500 scenario.

## Important limitations
- This is a narrow deterministic safeguard, **not** a general legal-contract reasoner. Unfamiliar wording, conflicting clauses, or model mistakes can still occur. All AI classifications need human review.
- This patch improves quote relevance but does **not** establish semantic entailment for every contract clause.
- Shared tokens are bearer links; there is no user authentication or expiration. Use synthetic demo data only, not sensitive real customer agreements.
- Existing previously approved proposals and PDFs remain unchanged. Create a **new analysis and new proposal** after updating.
- PDF/DOCX upload, 20+ independent Gemma evaluation runs, Render deployment, and Sentry tracing are not included in this patch.

## Install safely (Windows PowerShell)
1. Back up your existing scopeguard-ai folder, including its `data` directory if you need the proposal history.
2. Extract this ZIP into a separate folder, for example `C:\Users\Lenovo\scopeguard-ai-v1.2`.
3. Open that folder in VS Code; do not copy the old `data` or `.venv` folder unless intentionally migrating.
4. In PowerShell, run: `powershell -ExecutionPolicy Bypass -File .\start.ps1`.
5. Open the localhost URL printed by the launcher (it selects an available port).
6. In another terminal, run `python -m pytest -q` after activating `.venv`.
7. Rerun the in-scope agreement + first-round changes. The analysis should show `INCLUDED`, no eligible billable extras, and total INR 0.
8. Also rerun the additional-pages demo and check it still flags potential extra work. Human review is required.

This version is a local hackathon MVP. It must not be used as a production billing or approval system.
