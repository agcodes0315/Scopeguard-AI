# ScopeGuard Graph — FalkorDB context extension

**Track 01: Agents That Act on Connected Data** and **Track 02: Agent Memory and Coordination (single-agent persistent memory prototype; multi-agent sharing not yet built)**.

**Core premise:** Client scope classifications must use a linked agreement version, clauses, requests, and prior human-confirmed decisions. The new `/api/graph/*` workflow **requires FalkorDB**. If the graph is down, it returns HTTP 503 and no graph decision. The original Hacktoberfest `POST /api/analyze` remains intact and Gemma-based. We don't claim the older endpoint depends on FalkorDB.

## Start on Windows

Requirements: Docker Desktop, Python 3.11+ and Ollama with `gemma3:4b`.

```powershell
cd C:\Users\Lenovo\Desktop\scopeguard-ai
docker compose -f compose.graph.yml up -d
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
ollama pull gemma3:4b
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Open the server URL (usually http://127.0.0.1:8001), then choose **Open the FalkorDB Graph Context Workspace**, or open `/graph.html` directly. FalkorDB Browser is at http://127.0.0.1:3000 (localhost-only).

1. Create a **synthetic demo** project and a contract. This writes `Project -> Agreement -> Clause` nodes.
2. Analyze a new request. Graph selects the current agreement and retrieves previous decisions *before* sending a first-time case to the existing evidence-guarded Gemma analyzer.
3. Inspect the `evidence_path` and classification (advisory only).
4. Human-confirm the review result. Only confirmed decisions become persistent graph memory.
5. Re-analyze the exact same request. A multi-hop graph query retrieves the prior confirmed decision under the same agreement version; classification source switches to `graph_memory`, and Gemma is *not* called.
6. Restart the app; graph memory survives due to Docker volume. Repeat step 5.

**Important limit:** Human-confirmed classifications are reusable only for the same normalized request and agreement version. This prototype deliberately does not generalize exceptional approvals to similar but different requests. It never creates invoices or automatically authorizes billing. There is no login/tenant isolation, so the demo must use **synthetic, public or self-owned non-sensitive data only**, never real customer contracts.

## Graph model

```text
(Project)-[:HAS_AGREEMENT]->(Agreement)-[:CONTAINS]->(Clause)
(Project)-[:RECEIVED]->(Request)-[:BASED_ON]->(Agreement)
(Request)-[:HAS_DECISION]->(Decision)
```

`Decision.status` is `pending` until explicit human confirmation; confirmed decisions carry `classification`, `reviewer_note`, and `source`. `Agreement.id` limits memory to the corresponding agreement version.

## Central Cypher queries

```cypher
// Find current contract for a project
MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement)
RETURN a.id,a.body,a.version ORDER BY a.version DESC LIMIT 1

// Trace exact clauses
MATCH (a:Agreement {id:$aid})-[:CONTAINS]->(c:Clause)
RETURN c.id,c.text ORDER BY c.position

// Retrieve linked prior human decisions (same agreement)
MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement {id:$aid})
<-[:BASED_ON]-(r:Request)-[:HAS_DECISION]->(d:Decision)
RETURN r.id,r.text,d.classification,d.reviewer_note,d.status
```

The project uses parameterized FalkorDB Python `graph.query` / `graph.ro_query` calls, never string-interpolated raw client inputs.

## Why FalkorDB is essential

The graph-powered endpoint has no stored agreement outside FalkorDB. Without its `Project->Agreement` traversal it cannot determine the source contract, and without its `Request->Decision` traversal it cannot recall a review. Removing FalkorDB makes `/api/graph/analyze` unusable; it returns HTTP 503. The existing `/api/analyze` endpoint is intentionally separate and remains available for the Hacktoberfest demo.

## Testing

```powershell
python -m pytest -q
$env:SCOPEGUARD_URL="http://127.0.0.1:8001"
python evaluation\run_evaluation.py
```

Regression tests under `tests/test_graph_context.py` cover graph-required execution, evidence trails, human confirmation, approved memory reuse, and refusal to reuse a different request. For full integration, also run Docker and demonstrate two sessions.

## Deployment and access control

See `DEPLOYMENT_GUIDE.md`. This is **not** a secured public SaaS app. APIs have no user authentication and are not suitable for public exposure. For a hackathon demo, use localhost + reproducible Docker setup and a screen recording, or add authentication and resource controls before hosting publicly.

## Track statement and AI use disclosure

Suggested primary track: **Agents That Act on Connected Data**. Secondary memory track only if demonstrable on the judges' deployment. ScopeGuard v2/Gemma analysis predates the Graph Hacks work; FalkorDB graph workflow is the event-specific addition. OpenAI ChatGPT assisted with source drafting, architecture ideas, and tests; participant must verify and explain them. No claim of multi-agent coordination, company-brain knowledge ingestion, or production security.
