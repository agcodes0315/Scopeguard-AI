# ScopeGuard Atlas — pitch and product validation

## Customer
Indian independent website developers handling fixed-price client projects through messages and email. Clients use a no-login proposal flow. This is a **hypothesis**, not proven demand.

## One-sentence problem
Informal scope changes create mismatched expectations before anyone agrees on price, deliverables, or deadlines.

## Eight-slide pitch narrative
1. **Problem** — The client says “Please add another page.” Is that included? Who approved it?
2. **Evidence** — Upwork 2026 survey of U.S. knowledge workers: 38% freelance (https://www.upwork.com/press/releases/upworks-future-workforce-index-2026-how-ai-is-redefining-the-value-of-work-as-skilled-freelancing-accelerates); Leapers 2025 self-selected UK survey: 30.3% disputed contracts/payments (https://www.leapers.co/research/2025/report/); PMI 2018 cross-industry historical research: 52% of projects experienced scope creep (https://www.pmi.org/learning/library/scope-creep-rising-11308). These are distinct populations; never combine them into an India market estimate.
3. **Cost** — Illustrative only: 4 projects x 2 unpriced hours x ₹1,000/hour = ₹8,000/month of time value at risk. Not measured loss.
4. **Solution** — Create project once → paste request → view evidence and historic exceptions → draft fair proposal → get client confirmation.
5. **Before/after** — Test five independent developers using the same case, once manually and once with Atlas. Record task completion time, number of clicks and errors. Do NOT invent improvements.
6. **Graph engine** — Project → Agreement version → Exception. Show real Cypher, stale exception prevention, conflict detection, FalkorDB outage behavior.
7. **Business** — Open-source local foundation. Potential paid hosted convenience is a hypothesis, not existing revenue. Interview 5–8 freelancers about actual last disputes; test paid pilot intent.
8. **Why this team** — Explain personal contributions, real debugging of 24-case Gemma tests, test evidence, and disclose AI coding assistance.

## Product metrics and proposed targets (not results)
- Median time to produce a reviewed client-ready response: <2 minutes.
- Critical false-extra rate: 0 on held-out safety scenarios.
- Unsupported billing recommendations: 0.
- Correct agreement-version applicability: 100% on synthetic cross-version tests.
- Customer proposal completion without an account: >=80% in observed usability testing.
- Measured time savings = median(manual_seconds - assisted_seconds), with both raw times published.

## Honest limitations
The Atlas extension matches only the same whitespace-normalized request text, not semantically similar changes. A reviewer acknowledgement is not customer consent. A customer-approved flag must be independently verified; it is not cryptographic proof. The graph endpoints are unauthenticated and must not be deployed publicly with private information. No legal advice.
