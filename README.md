# ScopeGuard AI 🛡️

**Detect scope creep. Price it fairly. Get a clear decision before doing extra work.**

A local-first freelancer and client change-approval workflow powered by the open-weight **Gemma 3 4B** model through Ollama. Built as a new Hacktoberfest 2026 Week 2: Side Hustle project.

## Who it's for

Freelance developers, designers, creative studios, and their clients. A five-page website becomes seven pages and three rounds of revisions, but the agreement only covered five pages and two rounds. ScopeGuard identifies potential scope changes, asks the freelancer to set estimates, and lets the client approve or reject the proposal.

## Features implemented

- Local Gemma-powered agreement vs. request comparison
- Topic-matched exact request excerpts, conservative evidence rejection, and needs-review fallback
- Human-entered hours and rates; deterministic money calculations
- Tokenized customer review link (approve / reject / request clarification)
- Persisted decisions in SQLite; one final decision per proposal
- Downloadable proposal PDF (not a tax invoice)
- Export model findings as JSON
- FastAPI API with validation, pytest checks, and GitHub Actions CI
- Simple standalone frontend (no Node installation required)

## Windows setup (PowerShell in VS Code)

1. Install the latest [Ollama](https://ollama.com/download) and Python 3.11+.
2. Download the model:

```powershell
ollama pull gemma3:4b
```

3. Open this folder in VS Code and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

4. Visit **the URL printed in your terminal (normally http://127.0.0.1:8001)**, choose **Load demo example**, then **Analyze scope with Gemma**.
5. Enter hourly rate and nonzero estimated hours, choose **Create customer approval proposal**, and open the generated link in another browser tab. Make a decision as the customer; download the proposal PDF.

If `py` is not installed, use `python -m venv .venv` manually.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tests do not call Ollama and validate proposal creation, pricing, PDF generation, immutability of decisions, and invalid prices.

## How open innovation is essential

Gemma's open weights enable local analysis; a freelancer can keep sensitive raw agreements on their own machine when Ollama runs locally. The extraction model can be swapped without changing pricing rules. This is a powerful alternative to mandatory per-document closed API calls. **It does not mean the app is end-to-end encrypted or production-secure.**

## Architecture

`Browser → FastAPI → local Ollama/Gemma (only for analysis)`

`Browser → FastAPI → SQLite (proposals, approval states)`

`Browser → FastAPI → ReportLab (PDF export)`

## Amazon Leadership Principles as engineering inspiration

- **Customer Obsession:** Client and freelancer interfaces, fair pricing transparency.
- **Ownership:** Complete input-to-approval workflow.
- **Invent and Simplify:** Convert document language into scoped changes.
- **Highest Standards / Earn Trust:** Exact quotation checks, manual estimates, immutable final decisions.
- **Dive Deep:** Structured output validation, failure-mode testing.
- **Bias for Action / Deliver Results:** Small deployable MVP and demo-first workflow.
- **Frugality:** Local model, SQLite, no compulsory hosted API billing.

## Security and scaling limitations (important)

This is a **hackathon MVP, not a production multi-tenant SaaS**.

- Share tokens are bearer credentials: whoever gets the link can see and decide on the proposal. Use demo/synthetic agreements only. No authentication, role-based access control, or protected identity verification exists yet.
- SQLite is appropriate for local single-instance prototyping, not horizontally scaled deployments with ephemeral disks.
- For production, introduce authenticated accounts, expiring invitation links, role-based permissions, CSRF/rate limiting, encrypted storage, audit logs, consent, retention/deletion controls, and PostgreSQL with migrations.
- Avoid external deployment of private agreements until all these safeguards exist. A hosted FastAPI container **does not automatically include an Ollama model**. Configure an actual reachable Ollama service before enabling live hosted inference.
- Model classifications are advisory; excerpt checks only prove text inclusion, not semantic correctness. A human must review any outcome. No legal determination or automatic billing.
- Customer approval records are workflow signals, not enforceable signatures or evidence of payment.
- The PDF is a *proposal*, not a compliant tax invoice.

## Next steps before contest submission

- Evaluate with 20+ labeled synthetic cases and publish precision, recall, failure examples, and local latency.
- Add upload/extraction for common document types.
- Host a safe sandbox demo with *synthetic* data; do not claim live model inference unless a model runtime is actually connected.
- Run a genuine first-user test, obtain permission before quoting feedback.
- Add Sentry tracing only if properly redacted and configured; claim partner categories only for meaningful implemented uses.

## Sample DEV article structure

See [`DEV_SUBMISSION_DRAFT.md`](DEV_SUBMISSION_DRAFT.md). Fill in demonstration links and measured results rather than inventing them.

## License

MIT — see [`LICENSE`](LICENSE).

## 1.1 evidence correction and existing saved approvals

Previous versions allowed an exact quote for one change to appear as the supporting evidence for another (e.g. Careers page citing a third revision). Version 1.1 checks both quotation inclusion and whether the quote contains terms identifying the specific change. It may still reject valid indirect evidence, so review is always necessary.

**Previously generated proposals and PDFs are snapshots and do not update automatically.** To show corrected excerpts, re-run analysis, create a *new* proposal, and approve it again for the demo. Never rewrite historical approvals. The database lives under `data/scopeguard.db` in each project directory; back it up before changing installations.

On Windows the startup script now chooses the first free port between 8001 and 8005 rather than colliding with 8000. Use the exact URL printed in the terminal.


## v1.2 Billing Safety Patch

See [FIX_NOTES_v1.2.md](FIX_NOTES_v1.2.md) for upgrade instructions, safeguards, and limitations. New proposals require a recorded analysis ID and verified out-of-scope items; included work is not available for extra-charge proposals.

## October 2026: Competition upgrade (v1.3)

Upload selectable-text PDF, DOCX or UTF-8 TXT agreements directly in the left-hand agreement panel (up to 3 MB; max 25 PDF pages). Uploaded bytes are parsed in memory, and extracted text appears in the agreement textbox for review. The text is submitted only when the user clicks Analyze; the API does not retain uploaded files. This is not OCR.

Safety: `included` and `needs_review` items are excluded from automatic change proposals, and the backend independently checks analyzed classifications and evidence. This does not replace contract review, and the demo share-link design must not be exposed publicly without identity and access controls.

### Verify

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
# Separate VS Code terminal:
.\.venv\Scripts\python.exe -m pytest -q
# Use the actual port printed by start.ps1:
$env:SCOPEGUARD_URL='http://127.0.0.1:8001'
.\.venv\Scripts\python.exe evaluation\run_evaluation.py
```

This repository contains 24 human-labeled examples. Their existence is **not** an accuracy score; run the optional evaluator against your local Gemma model and review results.

For competition claims and Windows instructions, read `UPGRADE_GUIDE.md`.
