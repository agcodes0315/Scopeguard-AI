# What would stop this project winning?

## Must complete before submitting

1. **Reliable demo:** ensure `python -m pytest -q` runs inside `.venv`, `docker compose -f compose.graph.yml ps` shows FalkorDB up, and Ollama contains `gemma3:4b`.
2. **One complete story:** agreement → message → Gemma + evidence → manual quote → client decision → related graph memory.
3. **Independent outcome:** run a timed pilot; record both successful and unsuccessful outputs; report pilot sample size and method.
4. **Graph necessity:** demonstrate a decision changes on a repeated exact request but *doesn't* transfer to another request/agreement version. If the graph is unavailable, graph features should not quietly pretend to succeed.
5. **Live link honesty:** Render currently hosts a static showcase, *not* an end-to-end hosted AI API. Make this unmistakable in README and submission.
6. **Eligibility honesty:** earlier ScopeGuard work predates the Hacktoberfest Week 2 window; new commits do not reset the original development timeline. Submit only where rules allow this provenance.

## Product weaknesses / strongest next changes

| Weakness | Quick measurable fix | Longer-term product fix |
| --- | --- | --- |
| Non-technical users see raw graph JSON | Show an evidence sentence beside the path; capture 5-user comprehension checks | Interactive explainable decision timeline |
| Model responses sometimes slow | Add loading state and record p50/p95 latency from real calls | Streaming updates and caching |
| `needs_review` blocks quotation | Explicit clarification template; measure safe false-positive rate | Structured review workflow and customer questions |
| First-time user must navigate several pages | One click demo fixture and guided journey | Unified single-page task UI |
| No proven willingness to pay | Interview 5 freelancers; document verbatim consented feedback | Pilot with actual usage and paid conversion |
| Public API lacks customer identity controls | Keep all local/project demo data synthetic | Auth, tenant isolation, expiring invitations, security review |

## Judges' hard questions, with defensible answers

**Why not paste into ChatGPT?** The product ties agreement evidence, manually decided rates, client review and saved graph decisions into one repeatable workflow. The advantage is workflow reliability, not that Gemma is inherently more accurate than every cloud model.

**Where is the graph indispensable?** Persistent relationships linking agreement versions, requests, confirmed decisions, and scope-limited exceptions affect later repeat-request outcomes. A decision without graph memory has different behavior.

**Why is a `needs_review` answer useful?** It avoids falsely billing ambiguous work; the user can ask for clarification instead of quoting an unsupported amount.

**What is the current business proof?** Technical MVP only unless actual independent users have tested it. Pilot results and interviews are the next evidence needed.

**What is deployed?** Render static showcase, full inference and FalkorDB demonstrated on a local workstation.

**Will you guarantee a prize?** No; quality and independent judging are outside the project's control.
