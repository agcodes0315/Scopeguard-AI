# ScopeGuard AI v2 — START HERE

## What you built
A local-first freelancer/client change-management assistant using **Gemma 3 4B** via Ollama. It compares agreement text against requests, checks supporting quotes, blocks unverified or included work from automatic extra billing, lets a freelancer estimate hours, and creates a tokenized customer approval proposal with PDF export.

**New in v2:**
- **Agreement Vault:** create demo projects, save numbered agreement versions with SHA-256 hashes, reload latest agreement, view source lines/clauses via API.
- **Scope Inbox:** save client messages locally under each project, retrieve them, and load a message into the analysis box. This is NOT connected to real email/Slack.
- **Client-ready reply drafting:** editable, deterministic clarification/change-order text. No email is automatically sent.
- **18 Python tests**, a separate **24-case Gemma evaluation dataset**, and GitHub Actions tests.

## Windows quickstart
1. Extract ZIP into a NEW folder (do not overwrite the working old folder or copy its `data/` automatically).
2. Open folder containing `start.ps1` in VS Code.
3. Ensure Ollama is running and `ollama pull gemma3:4b` succeeded.
4. Open PowerShell in this folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

5. Open the exact localhost URL in the terminal; leave the server terminal open.
6. Open a **second** terminal and run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Expected from packaged version: `18 passed` (a non-fatal Starlette warning may occur).

## Full UI demo in 9 actions
1. Create a new workspace project; enter a fictional client label.
2. Upload or paste a sample agreement.
3. Click **Save agreement version**; edit it later and save version 2.
4. Paste a client message; select **Save request to Inbox** and **View Inbox**.
5. Load the saved request; run **Analyze scope with Gemma**.
6. Check agreement evidence; do NOT bill `needs_review` or `included` findings.
7. Enter hours only against genuinely verified `potential_extra` findings.
8. Create a proposal, open its localhost customer link, decide, download PDF.
9. Click **Generate client response draft**. Review and edit before sending by your own means.

## Honest limitations
- The model can be wrong. Automated tests do **not** measure Gemma's actual accuracy. Run the evaluator and report observed outcomes.
- The workspace and proposal API have **no user authentication**. It is suitable for a **local demo with fictional data only**, NOT exposure on a public network or storage of private client contracts. Tokens are share links, not verified electronic signatures.
- Agreement "clauses" are exact numbered non-empty source lines, not guaranteed legal clause boundaries. Document uploads extract selectable text only (no OCR).
- No connected email/Slack inbox, payments, live notifications, embeddings database, contract marketplace, SaaS billing, Render deploy, Sentry instrumentation or Copilot-specific integration has been implemented.
- The UI's client-ready drafts are deterministic so they do not invent legal clauses or costs. Users must review all drafts.
- When finished recording the demo, keep `data/` out of git. Never commit `.env` or sensitive customer information.

## Gemma live benchmark
After starting the server in the first terminal, substitute its actual port below:

```powershell
$env:SCOPEGUARD_URL = 'http://127.0.0.1:8001'
.\.venv\Scripts\python.exe evaluation\run_evaluation.py
```

Review `evaluation/results.json`. Don't claim a performance score unless this run completes successfully and you review the predictions. 24 cases is a small exploratory evaluation, not a comprehensive benchmark.

## What to do for competition
See `PR_WORKFLOW.md`, `SUBMISSION_CHECKLIST.md`, `DEV_SUBMISSION_DRAFT.md`, and `PRIZE_AND_SUBMISSION.md`. The **Gemma partner category** is supported by actual code. Render/Sentry/GitHub Copilot partner claims require real qualifying implementation and evidence.
