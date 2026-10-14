# ScopeGuard AI v1.3 - Hacktoberfest Upgrade

## What is built
- Open-weight **Gemma 3 4B** scope comparison using local Ollama.
- Evidence-backed labels: included / potential_extra / needs_review. Unverified findings cannot automatically create charges.
- Freelancer-controlled pricing, one-time customer decisions, SQLite-backed history of proposals by token, and proposal PDF.
- **New:** text-based PDF, DOCX and TXT upload via local parsing (no upload retention).
- **New:** 24 human-labeled evaluation cases and an optional live-model runner.
- **New:** upload validation and regression tests.

## Windows setup
1. Extract this ZIP to a NEW folder. Keep previous folder and data as a backup.
2. Open the folder containing `start.ps1` in VS Code.
3. Update Ollama if necessary, then run `ollama pull gemma3:4b`.
4. Run `powershell -ExecutionPolicy Bypass -File .\start.ps1` and open the URL printed.
5. In a SECOND terminal, run `.\.venv\Scripts\python.exe -m pytest -q`.
6. To measure actual model behavior, with app running, run `$env:SCOPEGUARD_URL='http://127.0.0.1:PORT'; .\.venv\Scripts\python.exe evaluation\run_evaluation.py` replacing PORT.

## Prize eligibility: precise claims
- **Gemma:** Implemented as the core model; target Best Use of Gemma.
- **Render:** NOT implemented. A Dockerfile alone is not a deployed Render app; local Ollama is not reachable from Render automatically.
- **Sentry Agent Tracing:** NOT implemented.
- **Copilot:** Claim only if you actually used qualifying Copilot tooling, not merely because you have VS Code.
- TabPFN/Tinker/others: NOT implemented.

## Privacy/security limitations
- This is a local demo, not a production service: no user accounts, encryption-at-rest, invitation expiry, or authenticated customer identity. Do not expose directly to the public internet.
- Proposal links are bearer tokens: anyone possessing the link can read/decide. Don't share screenshots of real tokens.
- PDF parser works on PDFs containing selectable text; scanned PDFs need OCR.
- Clause matching is heuristic + Gemma; human review remains essential.
- The 24 cases are a dataset, not proof of model accuracy until you run and inspect the evaluation.

## Submission plan
1. Run tests and evaluation and keep factual scores.
2. Capture anonymized screenshots plus an end-to-end 2-minute demo.
3. Push public source with LICENSE, README, docs, and no private data.
4. Obtain real freelancer feedback (never fabricate user testimonials).
5. Submit the DEV article with #devchallenge and #hf26challenge; list **Best Use of Gemma**.
6. For a separate Open Source Mini Challenge form, use the actual repository/commit URL, your GitHub username, truthful tool feedback and a public friction-log link.
