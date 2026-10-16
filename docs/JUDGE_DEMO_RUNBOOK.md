# Three-minute judge demo — ScopeGuard AI

**Prerequisites:** Ollama with `gemma3:4b`; Docker FalkorDB container; local FastAPI. Use fictional data. Pre-warm model before recording. Do not expose bearer approval tokens in public screencasts.

## 0:00 — 0:25: Who hurts?

> “A freelancer sells a five-page cafe website. The customer later asks for a sixth page. The hard part isn't writing code — it's remembering what was promised, proposing the price fairly, and obtaining agreement before work starts.”

## 0:25 — 1:05: Show actual ScopeGuard outcome

- Agreement: `Home, About, Services, Portfolio and Contact pages; two rounds of revisions included. Additional pages and a third revision require separate pricing and approval.`
- Request: `Please add a Testimonials page to the website.`
- Show Gemma reasoning and grounded agreement quote. If classification is `needs_review`, do not force a fake green result; explain the safety fallback.

## 1:05 — 1:45: Show graph is essential

- Open Atlas graph workspace, create a synthetic project and analyze the same request.
- Human-confirm the reviewed classification (this is *not* customer approval).
- Repeat the identical request with the same agreement version: expect `source: graph_memory` when a saved decision matches. Show the actual Project → Agreement / Request → Decision evidence path.
- Change the request to `Please add an online store with payments.` It must **not** reuse a Testimonials-specific waiver. State clearly that this is conservative exact-request memory, not semantic multi-hop reasoning.

## 1:45 — 2:30: Turn decision into action

- In the main workspace, enter human-estimated 4 hours at INR 1,000/hour: preview INR 4,000.
- Show client-facing proposal and synthetic approval. Explain that human review and client choice are separate.
- Download the proposal PDF; do not call it a tax invoice.

## 2:30 — 3:00: Proof / limits / ask

- Show `62 passed` (re-run before recording), FalkorDB running, live Render *showcase* link. Show the real pilot sample size **if available**.
- “The standalone local demo proves agreement comparison, consent workflow, and graph memory. It has not yet been validated for production handling of real contracts.”
- Ask judges to compare the two decision paths and the repeat-request memory behavior.

## Recording checks

- Clearly identify what is live locally vs what is deployed as a static showcase.
- Put repository, setup, graph model and Cypher query examples in README.
- Provide judge access to a public/unlisted video and full reproducible local setup.
- Mention use of AI coding assistance and preserve accurate build history.
