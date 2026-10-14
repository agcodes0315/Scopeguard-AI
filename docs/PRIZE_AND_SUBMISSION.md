# Hacktoberfest 2026 Submission Guide

## What is actually integrated?
- **Gemma (yes, prize-eligible):** The `gemma3:4b` open-weight model runs locally using Ollama and powers `POST /api/analyze`.
- **Render (no):** No live Render deployment. Dockerfile is not proof of deployment.
- **Sentry (no):** No Sentry SDK or agent tracing.
- **GitHub Copilot (unverified):** Do not enter this category unless you used a qualifying GitHub Copilot capability.
- **TabPFN, Tinker, DigitalOcean, MongoDB, Mastra, etc. (no):** Not integrated.

## Product story
Freelancers lose income through uncontrolled scope changes; clients lose trust through unexplained charges. ScopeGuard helps both parties review proposed additional work, inspect evidence, agree on freelancer-specified estimates, and record a decision. Under the hood, local Gemma gives a model-based comparison without a closed inference API.

## Proof to capture before publishing
1. Screenshot: agreement upload + extracted text.
2. Screenshot: explicit in-scope change marked included or needs_review, **not** billed.
3. Screenshot: a truly new page / third revision flagged potential_extra with matching agreement and request quotes.
4. Screenshot: customer approval of a new, priced proposal + generated PDF.
5. Terminal: passing automated tests. 24-scenario evaluation **actual score**, once completed.
6. Actual reviewer feedback: a freelancer's experience and requested changes, with consent to quote.

## DEV template structure
- What I Built: concrete two-sided pain point, target payer and commercial hypothesis.
- Demo: screen recording and/or deployed link; local-only demo requires video.
- Code: public repo link and license.
- How I Built It: Gemma through Ollama; FastAPI, JS, SQLite, deterministic guards, parsing and tests.
- Why Open Innovation Matters: model portability, local operation, privacy/control; do not claim every document stays private if you host inference remotely.
- My Agent Session: optional; include only a real session link.
- My First User: include only truthful actual experience; otherwise omit.
- Prize Categories: Best Use of Gemma, plus only others truly built.

## Separate Open Source Mini Challenge form
Screenshots show a separate form requiring contribution URL, project repo URL, GitHub username, project description, AI tool feedback, and optional friction-log/testing links. Make sure this form is associated with the competition you are actually submitting to; it is **not a substitute** for the DEV Week 2 post.

## Deployment reality
A lightweight host can run the UI and FastAPI API, but the 3.4GB Gemma model requires separate inference capacity. Do not advertise a live Render integration or local-private execution if routing user agreements to a hosted model without disclosing it.
