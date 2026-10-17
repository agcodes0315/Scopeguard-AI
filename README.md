# 🛡️ ScopeGuard AI

### From a client’s “one small change” to an evidence-backed decision.

**A local-first scope-change and client-approval assistant for freelance web developers, powered by Gemma 3 4B and FalkorDB.**

[![Live showcase](https://img.shields.io/badge/Live_Showcase-Render-46cbb9?style=for-the-badge)](https://scopeguard-ai-508d.onrender.com/) [![Source code](https://img.shields.io/badge/GitHub-Source_Code-181717?style=for-the-badge&logo=github)](https://github.com/agcodes0315/Scopeguard-AI) [![Tests](https://img.shields.io/badge/Local_Tests-67_Passing-279b65?style=for-the-badge)](#testing-and-evaluation) [![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

> **Live-site clarification:** The Render link is a public *showcase*, not a publicly hosted Gemma/FalkorDB application. The full working prototype runs locally. Do not upload real customer contracts to a publicly accessible unauthenticated instance.

## The problem: a small change can become an expensive disagreement

A freelancer sells a five-page website for a fixed price. The agreement includes Home, About, Services, Portfolio and Contact, plus two revision rounds. After work begins, the client messages: **“Please add a Testimonials page.”** Soon there is a request for a third revision or a checkout system.

The difficulty is not simply building another page. It is answering five questions quickly, fairly and with evidence:

1. What did the original agreement promise?
2. Has this exact change already been discussed or waived?
3. Is the new request included, potentially additional, or too ambiguous to judge?
4. What would an appropriate *human-estimated* change proposal look like?
5. Did the customer explicitly accept the proposed change?

Without a connected record, the freelancer searches chat threads, rereads the agreement, drafts an uncomfortable pricing message and risks performing unapproved work. Clients can also be surprised by charges they never reviewed. **ScopeGuard helps both parties reach a documented decision before extra work starts.**

### Evidence that the problem is real

- Project Management Institute's *Pulse of the Profession 2024* reports an **average scope-creep rate of 30%** in its 2023 survey data (versus 23% among its highest-performing quartile and 37% among its lowest-performing quartile). This is broad **project-management evidence**, not a measured freelancer-specific prevalence rate. [PMI report](https://www.pmi.org/-/media/pmi/documents/public/pdf/learning/thought-leadership/pmi-pulse-of-the-profession-2024-report.pdf).
- PMI's *Scope Patrol* article reported that its **2018** research found scope creep or uncontrolled scope changes in **52% of projects**, up from 43% five years earlier. This is historical context, not a current 2026 estimate. [PMI article](https://www.pmi.org/learning/library/scope-creep-rising-11308).
- A 2026 survey of **1,060** freelancers and self-employed workers by The Accountancy Partnership reported that **10.9%** selected late/non-payment as the biggest threat in their industry. Payment problems and unapproved scope work are related concerns, **not identical outcomes**. [Industry Frustration Report](https://www.theaccountancy.co.uk/business-news/the-industry-frustration-report-335854.html).

**Research gap:** We have not yet measured how many *freelance website projects* experience charge disputes or what fraction ScopeGuard could prevent. That requires direct customer interviews and a documented pilot.

## Who we build for

| | Primary persona | Secondary persona |
|---|---|---|
| **User** | Solo web developer or small creative agency | Small-business owner commissioning a website |
| **Typical context** | Fixed-scope projects, scattered client messages, limited administrative time | Limited technical vocabulary, wants predictable cost and delivery |
| **Job to be done** | Respond to a new request with evidence and an appropriate next step | Understand exactly what they are approving or questioning |
| **Main frustration** | Re-reading agreements, awkward pricing conversations, lost decision history | Unexpected charges or unclear scope boundaries |
| **Desired outcome** | A reviewed, usable response and recorded decision | Clear proposal and explicit approve / reject / clarify options |

**Initial niche:** Independent website developers delivering five-to-ten-page business websites. This is intentionally narrower than “all freelancers”; it makes contracts, revision policies and change types easier to evaluate and demo.

## What the product does

**In one sentence:** Paste the agreement and the client's request; ScopeGuard identifies the relevant terms, offers conservative AI guidance, lets the freelancer control pricing, and records a customer decision.

### End-to-end customer journey

| Step | User action | Product response | Friction removed |
|---|---|---|---|
| 1. Establish scope | Paste or upload a PDF, DOCX or TXT agreement; optionally save a version in Agreement Vault | Agreement text is extracted for review; versions can be saved locally | Repeated searching for the current agreement |
| 2. Capture request | Paste the message or load it from Scope Inbox | Client request is available for analysis | Copying context between scattered tools |
| 3. Understand change | Select **Analyze scope with Gemma** | `included`, `potential_extra`, or `needs_review`, with agreement/request evidence | First-pass interpretation and drafting effort |
| 4. Review fairly | Inspect evidence; enter **your own** hours and hourly rate only for eligible extra items | Deterministic amount calculation; no AI-generated rate | Hidden or invented pricing |
| 5. Seek consent | Create an approval proposal; open the bearer-token customer link in the local demo | Client can approve, reject or request clarification; PDF proposal available | Verbal approval without a clear decision record |
| 6. Reuse context | In the Atlas graph workspace, confirm a human-reviewed classification and ask the same request again | FalkorDB retrieves the prior confirmed decision for the same normalized request and agreement version | Repeating old investigations and losing institutional memory |

**Safety boundary:** Analysis and graph memory do not constitute customer approval, legal advice or authorization to invoice. New/ambiguous requests require human judgment.

## Two complementary workflows, one project

### A. ScopeGuard — agreement to client approval

- **Agreement Vault:** versioned local project agreements with hashes and source labels.
- **Scope Inbox:** manually captured client messages per local project.
- **Gemma analyzer:** evidence-aware classification and conservative fallback to review.
- **Proposal builder:** freelancer-controlled hours/rates; deterministic totals.
- **Customer response:** approve, reject or request clarification; one final proposal decision.
- **Exports:** JSON findings, editable client reply drafts and proposal PDF.

### B. ScopeGuard Atlas — decisions with graph context

- **FalkorDB** stores connected projects, agreement versions, clauses, requests and reviewer decisions.
- The agent fetches the **active agreement** and related clauses from the graph before interpreting a new request.
- A **human-confirmed decision** is reused only for a matching normalized request against the same agreement version; other requests return to analysis/review.
- Graph results expose an **evidence path**, including which agreement and prior decision informed the response.
- The graph endpoints intentionally return an error when FalkorDB is unavailable; they do **not** silently fall back to an unrelated store.

This is **scoped decision memory**, not an autonomous multi-agent planning system or a general-purpose knowledge graph.

## Why FalkorDB actually matters

A standard text classifier sees an isolated message. Atlas adds relationships and history:

```text
(Project)-[:HAS_AGREEMENT]->(Agreement)-[:CONTAINS]->(Clause)
    |                              ^
    +--[:RECEIVED]-->(Request)-[:BASED_ON]--+
                            |
                            +--[:HAS_DECISION]->(Decision)

(Agreement)-[:HAS_EXCEPTION]->(Exception)
(Project)-[:RECORDED_EXCEPTION]->(Exception)
```

The extension includes recorded exceptions, with their agreement version and customer-approval status. A reviewer-recorded waiver alone does **not** establish customer consent.

**Actual Cypher used to select the current agreement** (from `backend/graph_context.py`):

```cypher
MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement)
RETURN a.id, a.body, a.version
ORDER BY a.version DESC LIMIT 1
```

**Actual Cypher used to find relevant human-reviewed history:**

```cypher
MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement {id:$aid})
      <-[:BASED_ON]-(r:Request)-[:HAS_DECISION]->(d:Decision)
RETURN r.id,r.text,d.classification,d.reviewer_note,d.status
```

**Actual Cypher used by Atlas to inspect agreement exceptions** (see `docs/ATLAS_GRAPH_MODEL.md`):

```cypher
MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement)-[:HAS_EXCEPTION]->(e:Exception)
RETURN a.id,a.version,e.id,e.request_text,e.request_hash,e.effect,e.reason,e.customer_approved,e.status
ORDER BY a.version DESC
```

Queries are parameterized; the full executable code is in [`backend/graph_context.py`](backend/graph_context.py) and [`backend/atlas.py`](backend/atlas.py). See [graph model documentation](docs/ATLAS_GRAPH_MODEL.md).

### Falsifiable graph demonstration

1. Create a **synthetic** website agreement with five pages and two revision rounds.
2. Analyze: `Please add a Testimonials page to the website.`
3. Inspect the graph-based agreement/evidence path.
4. Confirm a human-reviewed classification and note; **do not mark it as customer-approved without an independent approval record**.
5. Analyze the **identical** request again. The source can now be `graph_memory`, referencing the previous reviewed decision.
6. Change the request to `Please add an online store with checkout and payments.` The Testimonials decision must **not** be blindly applied.
7. Stop FalkorDB and retry a graph operation: the graph-dependent endpoint should fail closed rather than pretend history is available.

That last step distinguishes an essential context layer from a decorative visualization.

## Architecture

```text
Browser: vanilla HTML / CSS / JavaScript
    |
    v
FastAPI application (validation and workflow safety)
    |-------------------------> Ollama -> Gemma 3 4B (analysis only)
    |-------------------------> SQLite (local projects/proposals/decisions)
    |-------------------------> ReportLab (proposal PDF)
    |
    +---- Atlas graph endpoints -> FalkorDB
                                   Project / Agreement / Clause /
                                   Request / Decision / Exception

Render Static Site -> public documentation/showcase only
```

**Design choices:** A local model makes inference possible without sending agreement text to a proprietary inference API. The deterministic proposal engine avoids AI pricing hallucinations. FalkorDB persists connections across sessions in the graph-enabled workflow. Human approval gates reduce the risk of treating a recommendation as a commitment.

## Run locally (Windows / VS Code)

**Requirements:** Python 3.11+, Docker Desktop (for FalkorDB), [Ollama](https://ollama.com/download), enough memory/disk to run `gemma3:4b`.

```powershell
# Clone
 git clone https://github.com/agcodes0315/Scopeguard-AI.git
 cd Scopeguard-AI

# Python environment
 py -3.12 -m venv .venv
 .\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Download model (only needed once)
 ollama pull gemma3:4b

# Start graph storage
 docker compose -f compose.graph.yml up -d

# Start app; follow the URL printed by the script
 powershell -ExecutionPolicy Bypass -File .\start.ps1
```

If Python 3.12 is unavailable, use `py -3 -m venv .venv`. Ollama must be running; Docker must be running for graph features.

Open the URL printed by `start.ps1` (typically `http://127.0.0.1:8001`; the port may differ). Try the original ScopeGuard UI, then `/graph.html` and `/atlas.html` on **that same local port**. Check `http://127.0.0.1:8001/api/graph/health` only if the application is actually on port 8001.

For additional setup details, see [`docs/setup/START_HERE.md`](docs/setup/START_HERE.md) and [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md).

### Health check and tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q

docker compose -f compose.graph.yml ps
ollama list
```

**Last user-reported local verification (October 17, 2026):** `67 passed, 1 warning`. Docker showed a running FalkorDB container, and `ollama list` included `gemma3:4b`. The warning concerned Starlette's deprecated TestClient dependency; it did not fail that test run. This does **not** mean 62 live-model or end-to-end browser tests were performed.

### Optional live Gemma scenario evaluation

Start the FastAPI app first; then set `SCOPEGUARD_URL` to the **actual printed port** and run:

```powershell
$env:SCOPEGUARD_URL = 'http://127.0.0.1:8001'
.\.venv\Scripts\python.exe evaluation\run_evaluation.py
```

The repository contains **24 labeled synthetic scenarios**. On October 17, 2026 the user ran `evaluation/run_evaluation.py` locally with Gemma and reported 24/24 PASS; results were saved to `evaluation/results.json`. This is a reported local run, not an independently audited claim. Outcomes can vary with model behavior and versions. **Scenario success is not a statistically representative accuracy, precision or recall measure.**

## Evaluation, impact and product decisions

### What is verified and what is not

| Metric | Current evidence | Interpretation |
|---|---|---|
| Automated regression tests | **67 passed** in a reported local `.venv` run | Functional and safety checks pass in that environment |
| Synthetic scenarios | **24/24 predefined live synthetic scenarios passed** in the reported October 17, 2026 local run | Reproducible evaluation inputs, not 24 real users |
| Cross-session graph memory | Demonstrated with `graph_memory` and graph evidence paths | Qualitative demo, not a large-scale benchmark |
| Client approval | Synthetic ₹4,000 proposal and approval demonstrated | Fictional workflow, not recovered revenue |
| Public deployment | Render static showcase live | Not full-cloud Gemma inference or client-facing SaaS |
| First paying user / willingness to pay | **Not yet validated** | Open commercial hypothesis |
| Median time to usable reviewed reply | **Not yet measured** | Primary benchmark still needed |

### North-star metric

**Time from receiving a client request to a reviewed, usable client response.**

Supporting metrics: agreement-evidence validity, false billable-flag rate, human-edit distance to a usable reply, approval completion rate, and users willing to repeat the workflow.

**Target (not measured):** a reviewed, usable first draft in **under two minutes**, excluding initial model installation and agreement onboarding. Track median and P90 across repeated trials.

### Example cost of the problem — illustrative, not observed savings

If a freelancer spends **30 minutes** reconciling and responding to a scope dispute, values their time at **₹1,000/hour**, and handles **eight such requests/month**, the administrative opportunity cost is:

`0.5 hours × ₹1,000 × 8 = ₹4,000/month`.

This is an **assumption-based example**, not market size, revenue lost, or an amount ScopeGuard has demonstrated it can save. A measured before/after pilot is required to make real savings claims.

### Positioning and potential business model

**Sector:** freelance professional services / creative-agency operations, with a niche in website-development change control. **Alternatives:** manual email, chat searches, spreadsheets, contract templates and general-purpose AI drafting. ScopeGuard's **proposed** differentiator is the combination of local open-weight analysis, evidence-bound decisions, human-entered pricing, customer approval and exact-match version-aware graph memory in a single flow.

**Revenue hypothesis (unvalidated):** local open-source core with optional paid hosted convenience, team collaboration or managed onboarding. No paying-user, retention or pricing experiment has yet established demand.

## Before vs after: the honest claim

| Step | Without a dedicated workflow | With ScopeGuard (demonstrated capability) |
|---|---|---|
| Find agreement context | Search files/chat manually | Paste/load current agreement and stored versions |
| Interpret the request | Manual clause comparison | Gemma analysis with cited excerpts and `needs_review` fallback |
| Explain price | Draft a calculation manually | Freelancer enters hours/rate; amount is computed |
| Obtain decision | Informal chat reply | Explicit approve/reject/clarify customer view |
| Remember last exception | Search old messages | Version-aware, human-reviewed graph memory |

**Do not claim “13 hours → 3 hours” or “₹20,000 → ₹3,000” until identical tasks have been benchmarked.** A clear before/after screen recording and a timed pilot are next steps.

## Privacy, safety and limitations

This is a **hackathon MVP, not a production-secure multi-tenant service**.

- Use synthetic, public or permissioned demo material; never upload sensitive private contracts to an unauthenticated public demo.
- The public Render deployment is a static showcase. It does not run Ollama/Gemma or the graph API.
- Customer review links act as bearer tokens: anyone with the token can access the proposal. They are not verified identities or legally binding e-signatures.
- Local-first does not imply end-to-end encryption, access controls, or compliance certification.
- AI output is advisory. Exact quote matching does not establish that the legal interpretation is correct. `needs_review` and `included` should not be silently billed.
- The PDF is a **proposal**, not a tax invoice. Client approval is not payment.
- SQLite and the current unauthenticated API are not suitable for an Internet-facing multi-tenant rollout.
- FalkorDB graph memory uses conservative exact normalized matching; paraphrase-aware reuse, tenant isolation and consent verification need further engineering.
- In production, add authentication, authorization, tenant separation, expiring scoped links, audit logging, secure data deletion, rate limiting, durable storage, actual deployed model infrastructure and security testing.

## Product roadmap

**Before judging/submission:**

1. Publish a short working demo showing **first graph lookup → human confirmation → `graph_memory` reuse → unrelated request not reused**.
2. Publish the real scenario evaluation output, including failed cases and inference latency on the test machine.
3. Conduct 3–5 permitted user interviews and one timed usability session; quote feedback only with permission.
4. Link the demo from both the GitHub README and Render showcase.
5. Document meaningful original work completed within each contest's eligible window. Do **not** reset commit dates or misrepresent an existing project as newly created.

**After the hackathon:** improve graph versioning UI, smarter-but-safe evidence retrieval, project onboarding, secure identity/approval, model performance and a proper hosted architecture.

## Graph Hacks 2026 development provenance

ScopeGuard began as a local-first scope-management and customer-approval prototype **before** Graph Hacks. The competition-specific contribution focuses on FalkorDB-backed agreement relationships, version-aware exception context, human-reviewed decision memory, and the Atlas Decision Desk. The earlier local workflow is supporting infrastructure, not work claimed to have been created for the first time during the event.

**Eligibility evidence:** The repository intentionally preserves original commit timestamps and history. To verify precisely which graph files and features were implemented during the October 15–18, 2026 event period, inspect commit timestamps, pull requests, and file diffs rather than relying on this description alone. Only work demonstrably completed within the official window should be claimed as event work. Organizers determine eligibility.

```powershell
# From the cloned repository: inspect actual timestamped commits
# (this does not rewrite any history)
git log --all --since="2026-10-15T00:00:00+05:30" --until="2026-10-18T23:59:59+05:30" --date=iso-strict --pretty=format:"%h | %ad | %s"
git log --all --date=iso-strict -- backend/graph_context.py backend/atlas.py frontend/atlas.html docs/ATLAS_GRAPH_MODEL.md
```

The graph features cannot be considered eligible merely because a README or a new commit was added within the event window. No historical commits are reset, redated, or concealed.

## Hackathon context and transparency

**Graph Hacks — FalkorDB:** The graph-supported Atlas workflow is the relevant entry: FalkorDB is a required runtime dependency for graph decisions, and history influences later analysis. The strongest proposed track is **Agents That Act on Connected Data**; memory is also relevant, but this prototype does not yet demonstrate multiple cooperating agents.

**Hacktoberfest 2026, Week 2 — Side Hustle:** The local Gemma workflow fits the business/theme concept. However, Week 2 official rules require a **brand-new project built during the contest entry period**. This repository contains earlier development history, so acceptance/eligibility for the same existing project must **not be assumed**. Newly pushed commits do not change when original work was created. [Official Week 2 rules](https://dev.to/page/hacktoberfest-week2-2026-10-12-contest-rules).

AI coding assistance was used during development; the contributor must review, test, understand and accurately disclose AI-assisted work as required by contest rules.

## Documentation

| Resource | Path |
|---|---|
| Graph data model and Cypher | [`docs/ATLAS_GRAPH_MODEL.md`](docs/ATLAS_GRAPH_MODEL.md) |
| Graph Hacks overview | [`docs/GRAPH_HACKS_README.md`](docs/GRAPH_HACKS_README.md) |
| Product pitch and metrics | [`docs/PITCH_AND_METRICS.md`](docs/PITCH_AND_METRICS.md) |
| Deployment notes | [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md) |
| Windows/local getting started | [`docs/setup/START_HERE.md`](docs/setup/START_HERE.md) |
| DEV article draft | [`docs/DEV_SUBMISSION_DRAFT.md`](docs/DEV_SUBMISSION_DRAFT.md) |
| Graph context backend | [`backend/graph_context.py`](backend/graph_context.py) |
| Atlas decision backend | [`backend/atlas.py`](backend/atlas.py) |
| Evaluation scenarios | [`evaluation/`](evaluation/) |

## Open source and author

**MIT License** — see [`LICENSE`](LICENSE). Source and issue tracker: [agcodes0315/Scopeguard-AI](https://github.com/agcodes0315/Scopeguard-AI).

Built as a practical investigation into a simple principle: **an AI recommendation should lead to a transparent human decision, and the next decision should remember the evidence behind the last one.**
## Graph Hacks 2026 Development

ScopeGuard began as a local-first freelancer scope-management prototype before the event.

During Graph Hacks, the project was extended with FalkorDB-backed agreement and decision-memory workflows, including connected evidence retrieval, human-reviewed exceptions, agreement-version context, and the Atlas Decision Desk.

The earlier application provided the supporting scope-analysis and customer-approval workflow. The Graph Hacks contribution focuses on making previous decisions retrievable, traceable, and relevant to future client requests.

The repository preserves its original development history. Event-specific contributions should be verified against the actual Git commits and implementation files.

### Why FalkorDB matters

- Connects projects, agreements, clauses, requests, and decisions.
- Retrieves reviewed decisions for matching requests.
- Preserves agreement-version context.
- Avoids reusing an unrelated request's previous decision.
- Exposes the relationship path supporting the result.

**Transparency:** The local application existed before Graph Hacks. The graph-specific enhancements are the competition contribution.