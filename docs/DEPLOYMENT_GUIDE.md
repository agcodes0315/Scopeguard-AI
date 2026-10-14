# Deployment plan — Hacktoberfest + Graph Hacks

## Working demo immediately: local Docker deployment

- FalkorDB: `docker compose -f compose.graph.yml up -d` (persistent Docker volume).
- Gemma: local Ollama `gemma3:4b`.
- Backend/frontend: `powershell -ExecutionPolicy Bypass -File .\start.ps1`.
- Graph workspace: `http://127.0.0.1:<printed-port>/graph.html`.
- Demo: screen-record a project being created, first decision, human confirmation, second decision using graph memory, and inspect FalkorDB Browser.

This satisfies the **local setup alternative** in the Graph Hacks rules. Record the deployment, do not claim it is publicly hosted.

## Public deployment path (requires additional work)

1. Choose a hosting provider with adequate RAM/CPU for Ollama+Gemma and a persistent FalkorDB volume, **or** use authenticated FalkorDB Cloud plus a securely hosted Ollama-compatible inference endpoint. A small free web service does *not* run a 3.4 GB quantized model reliably.
2. Apply authentication and project authorization to **all** APIs (`/api/analyze`, `/api/graph/*`, workspace, proposals, approval links, uploads); encrypt sensitive records, rate-limit, cap request payloads, and prevent arbitrary remote access. **Do not expose the current unauthenticated version publicly.**
3. Protect FalkorDB ports; expose only HTTPS through a reverse proxy. Use a generated DB password, TLS on external connections, backups, and isolated graph-per-tenant or mandatory tenant-scoped queries.
4. Configure `FALKORDB_HOST`, `FALKORDB_PORT`, `FALKORDB_PASSWORD`, and `FALKORDB_GRAPH`; configure `OLLAMA_URL` and `OLLAMA_MODEL` for reachable inference. Never expose plain Ollama over the internet.
5. Deploy with persistent state; validate all 24 local Gemma cases and graph memory across app restarts before sharing a demo URL.

**Render consideration:** Render web-service filesystems are ephemeral by default, so any on-disk SQLite and FalkorDB storage would need persistent infrastructure; persistent disks generally require paid services. Render deployment is not provided as a working cloud URL in this ZIP. A `Dockerfile` builds the existing app but it does not provision FalkorDB or Gemma. Do not deploy it alone and claim a functioning Graph Hacks system.

## Hacktoberfest 2026 entry

Preserve original ScopeGuard AI/Gemma: `/`, `/api/analyze`, approval workflow, versioned agreements, evaluation suite, human-entered hours, customer approval flow. Continue with DEV article + demo and honest 24/24 *scenario* evaluation reporting (not universal model accuracy). See original README and `DEV_SUBMISSION_DRAFT.md`.

## Graph Hacks 2026 entry

Create a separate README section identifying graph additions and the primary Track 01. Submit a public repository, `GRAPH_HACKS_README.md`, the Cypher model/queries, reproducible local setup, a graph-reasoning and cross-session-memory demo video, and an accurate statement on whether a live URL actually exists.
