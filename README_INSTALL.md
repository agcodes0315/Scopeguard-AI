# ScopeGuard Atlas — Judge-friendly Decision Replay

This is an **additive frontend-only patch** that makes existing graph states understandable without changing the verified classification, billing, approval or graph backend. It is deliberately not a fabricated time-savings benchmark and does not claim new multi-hop graph reasoning.

## Install (Windows PowerShell)

1. Extract this ZIP somewhere outside the repository (e.g. Downloads).
2. In your actual project root, run:

```powershell
cd C:\Users\Lenovo\Desktop\scopeguard-ai
.\.venv\Scripts\python.exe "$env:USERPROFILE\Downloads\scopeguard-atlas-upgrade\install_upgrade.py"
.\.venv\Scripts\python.exe -m pytest -q
```

If you extracted to a different folder, replace the quoted installer path. No environment variables or tokens are required.

Optional: with Node installed, run `node "$env:USERPROFILE\Downloads\scopeguard-atlas-upgrade\tests\test_decision_replay.js"`.

## What changes

- Adds `frontend/decision-replay.js` to show clear, state-specific explanations: no matching exception, matching reviewed decision, unverified consent, stale exception, conflict, graph-memory reuse or fresh Gemma analysis.
- Modifies one `script` tag in `frontend/atlas.html`; original `atlas.js` and its behavior are unchanged.
- Moves raw JSON into an expandable **Technical evidence** panel for judges.
- Never promises customer approval or grants billing based on graph states.

## Verify in the browser

Start Docker, Ollama, and `start.ps1`. Visit the local `/atlas.html`. Use the existing synthetic agreement and an identical previously reviewed request, then an unrelated checkout request. Check that the new explanation changes and that Technical evidence retains the raw graph path. For a stale agreement, only claim version invalidation if it has been tested on a new actual agreement version.

**Note:** This package does not create new agreement-version editing endpoints. Backend version invalidation already has a unit test; an end-to-end version-change UI would be separate work.
