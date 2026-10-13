# Submission checklist — only claim verified work

## Before publishing
- [ ] Verify 18 tests locally and run the 24-case live Gemma evaluation.
- [ ] Manually inspect mistakes and improve the worst failure cases.
- [ ] Push a public repository with code and LICENSE. Don't push secrets, `.env`, `.venv`, `data/` or real customer agreements.
- [ ] Record a 90–150 second demo: sample agreement -> Vault -> Scope Inbox -> Gemma -> approved price -> customer decision -> PDF -> editable reply.
- [ ] Collect one actual freelancer's feedback (optional). Never invent testimonials or revenue.
- [ ] Publish DEV post using required challenge tags and original event submission template.
- [ ] Submit to the contest and double-check published URLs and eligibility.

## Open Source Mini Challenge form shown in your screenshots (verify it's the correct event)
- **Contribution URL:** link to a real commit or PR showing the code change.
- **Project repository URL:** real public GitHub repo link.
- **GitHub username:** your actual GitHub username.
- **Description:** what was built, how it works, why it matters. See DEV_SUBMISSION_DRAFT.md; adjust with real benchmark data.
- **Feature request:** improve secure client invitation, robust clause evidence, calibrated uncertainty. Give priority honestly.
- **Friction log:** publish a markdown issue/doc with real encountered errors (Windows port conflict, wrong evidence, false charges, missing database table), steps, mitigation, and requested improvements; paste public URL if required.
- **Testing link:** a real deployed public URL (localhost is NOT a public test link). If optional and unavailable, leave blank.
- **Tool experience:** Gemma/Ollama, Python/FastAPI, SQLite, pytest, PyMuPDF/python-docx, ReportLab, Git/GitHub; list only those actually used.
- **AI tools used:** Gemma 3 4B through Ollama plus any coding assistants actually used.
- **Declarations:** only confirm factual eligibility and age criteria.

## Partner tech claims
- Gemma: **YES**, local inference via Ollama in backend/main.py.
- Render: **NO**, app is not deployed there.
- Sentry: **NO**, agent tracing not integrated.
- GitHub Copilot: **ONLY IF actually used/documented**; Git alone is insufficient.
- Chroma/Qdrant, LangChain, Gmail, Slack, Stripe: **NOT yet implemented**.

## Customer safety notes
Don't claim confidentiality against all threats: local AI prevents sending prompts to a third-party LLM API in the default configuration, but a publicly exposed or compromised device/server can still leak data. Local demo share links are bearer tokens; approvals are records, not authenticated digital signatures.
