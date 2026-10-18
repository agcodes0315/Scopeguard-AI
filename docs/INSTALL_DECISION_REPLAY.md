# ScopeGuard Atlas — Safe graph-selected execution (local only)

## Install in your existing repository

The ZIP contains **replacement files** at their correct paths. Extract into `C:\Users\Lenovo\Desktop\scopeguard-ai`, overwriting the matching backend files. Do not replace or delete your other source files. Your public `showcase/index.html` remains unchanged; the new live replay screen is `/replay.html` in the local FastAPI application.

From VS Code PowerShell:

```powershell
cd C:\Users\Lenovo\Desktop\scopeguard-ai
.\.venv\Scripts\python.exe -m pytest tests\test_safe_executor.py -q
.\.venv\Scripts\python.exe -m pytest -q
# Ensure Docker Desktop, FalkorDB and Ollama/Gemma are running.
docker compose -f compose.graph.yml up -d
ollama list
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

Open **http://127.0.0.1:8001/replay.html**. If 8001 is in use, change the `--port` value and URL together.

**Recommended exact demo:** Create project → Run `Please add a Testimonials page to our cafe website.` → Record demo exception → Rerun same request → try online checkout → return to original Testimonials request → Create agreement version 2 → Run again. The graph-selected action and editable draft will change with the active graph history.

**Safety:** An internal `ActionDraft` node is created in FalkorDB linked to the actual Request and Agreement; no email, charge, invoice, or customer approval is executed. `customer_approved=true` is a *synthetic field* for the demo, not proof of a real consent document. Do not expose these unauthenticated endpoints publicly.

**Cypher additions:** `(Request)-[:GENERATED_DRAFT]->(ActionDraft)-[:BASED_ON_AGREEMENT]->(Agreement)`. New agreement versions are added through `Project-[:HAS_AGREEMENT]->Agreement`, while old `Exception` nodes remain attached to their original agreement. The graph preview chooses whether history is applicable or stale.

**Git push (after tests pass):**

```powershell
git status --short
git add backend/atlas.py backend/atlas_action.py backend/main.py frontend/replay.html tests/test_safe_executor.py docs/INSTALL_DECISION_REPLAY.md
# Inspect unrelated Dockerfile and LICENSE modifications separately.
git diff --cached --check
git commit -m "feat: execute safe graph-selected drafts and replay agreement versions"
git push origin main
```

The public Render **static site** only serves `showcase/` and will not execute these backend endpoints. Keep the live AI/graph workflow local until authentication and deployment infrastructure are implemented.
