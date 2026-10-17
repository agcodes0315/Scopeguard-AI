# ScopeGuard Atlas graph-gated next-action integration

## What changes
- Adds `POST /api/atlas/next-action`, choosing a **draft next action** based on the live graph preview and active-agreement graph-guided analysis.
- Adds `verified_evidence` to the existing graph analysis output, derived **on the server** using exact quote containment (not a semantic guarantee).
- Reuses the deterministic action policy. All actions require human review, and **none authorize charges, sending, or customer consent**.
- Returns both evidence paths; a developer can format them in Atlas after backend verification.

## On Windows
1. Extract ZIP anywhere; keep the folder structure inside it.
2. From VS Code repository PowerShell: `& .\.venv\Scripts\python.exe 'C:\path\to\extracted\install_in_project.py'`
3. If a root policy already exists in `backend/`, installer backs the prior policy up under the Windows temp folder and replaces it with a valid tested policy.
4. The policy handles matching, reviewer-only, conflicting, and stale graph states conservatively.
5. `& .\.venv\Scripts\python.exe -m pytest tests/test_atlas_action.py -q`
6. `& .\.venv\Scripts\python.exe -m pytest -q`
7. Only if all pass: stage **only** `backend/atlas_action.py backend/graph_action_policy.py backend/graph_context.py backend/main.py tests/test_atlas_action.py` and the existing action-policy tests. Do not stage temporary installers or private data.

## API usage (LOCAL ONLY)
`POST http://127.0.0.1:<running-port>/api/atlas/next-action`
`{"project_id":"<actual graph project id>","request_text":"Please add a Testimonials page."}`

Real action change follows the graph: matching saved exception -> verify; no exception plus verified new extra -> prepare a proposal **draft**; stale exception -> clarification. Unrelated requests cannot inherit exact-hash exceptions. Clients must not supply or override the server-computed verified_evidence flag.

## Important
The existing graph and Atlas endpoints are **unauthenticated**. Do NOT deploy this endpoint publicly; use localhost and fictional test data. End-to-end Gemma/FalkorDB performance and behavior are not verified by these isolated tests. The action policy is a rules engine informed by a graph, not an autonomous tool planner or a guarantee of prize eligibility.
