"""ScopeGuard AI MVP — locally hosted FastAPI + open-weight Gemma via Ollama."""
import json
import secrets
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
app = FastAPI(title="ScopeGuard AI", version="0.1.0")


class AnalyzeRequest(BaseModel):
    agreement: str = Field(min_length=20, max_length=30000)
    requests: str = Field(min_length=5, max_length=15000)
    hourly_rate: float = Field(default=500, ge=0, le=1000000)


class ScopeItem(BaseModel):
    request: str
    classification: Literal["included", "potential_extra", "needs_review"]
    agreement_evidence: str
    request_evidence: str
    reasoning: str
    estimated_hours: float | None = None


class AnalyzeResult(BaseModel):
    analysis_id: str
    summary: str
    items: list[ScopeItem]
    estimated_extra: float
    disclaimer: str
    model: str


def call_ollama(prompt: str) -> str:
    data = json.dumps({
        "model": MODEL,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": "You are an evidence-focused scope comparison assistant, not a lawyer. Output strictly JSON. Never invent contract terms or prices. Only quote exact excerpts from provided text. If uncertain label needs_review."},
            {"role": "user", "content": prompt},
        ],
        "options": {"temperature": 0.1},
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{OLLAMA_URL.rstrip('/')}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            payload = json.load(response)
        return payload["message"]["content"]
    except (urllib.error.URLError, TimeoutError, KeyError) as exc:
        raise HTTPException(status_code=503, detail=f"Ollama not reachable or model unavailable. Run 'ollama pull {MODEL}' and check Ollama is running. Details: {exc}") from exc


@app.get("/")
def homepage():
    return FileResponse(ROOT / "frontend" / "index.html")


@app.get("/style.css")
def stylesheet():
    return FileResponse(ROOT / "frontend" / "style.css", media_type="text/css")


@app.get("/app.js")
def javascript():
    return FileResponse(ROOT / "frontend" / "app.js", media_type="application/javascript")


@app.get("/proposal.html")
def proposal_page():
    return FileResponse(ROOT / "frontend" / "proposal.html")

@app.get("/proposal.js")
def proposal_script():
    return FileResponse(ROOT / "frontend" / "proposal.js", media_type="application/javascript")

@app.get("/api/health")
def health():
    return {"status": "ok", "model": MODEL, "runtime": OLLAMA_URL}


def _sentences(text: str) -> list[str]:
    """Split demo inputs into excerpts while retaining original substrings."""
    return [m.group(0).strip() for m in re.finditer(r"[^.!?\n]+(?:[.!?]+|$)", text) if m.group(0).strip()]


def _topic_terms(label: str) -> set[str]:
    stop = {"add", "new", "page", "pages", "the", "a", "an", "to", "for", "request", "change", "website", "site", "round", "rounds", "of", "extra", "additional", "do", "redo"}
    words = {w for w in re.findall(r"[a-z0-9]+", label.lower()) if len(w) > 2 and w not in stop}
    # Inflection differences for revision(s) and similar repeated words.
    return {w[:-1] if w.endswith('s') and len(w) > 4 else w for w in words}


def _matches_label(label: str, excerpt: str) -> bool:
    topics = _topic_terms(label)
    excerpt_words = _topic_terms(excerpt)
    return bool(topics and topics.intersection(excerpt_words))


def _ground_quote(label: str, proposed: str, source: str, *, client_request: bool) -> str:
    """Only accept a quote tied to this specific item, not merely present somewhere.

    If Gemma supplies a mismatched quote, look for a matching exact source
    sentence; if none exists, return empty rather than invent support.
    """
    proposed = proposed.strip()
    if proposed and proposed in source and _matches_label(label, proposed):
        return proposed
    if client_request:
        for sentence in _sentences(source):
            if _matches_label(label, sentence):
                return sentence[:1000]
    return ""


def _agreement_clause(label: str, agreement: str) -> str:
    """Find exact, topic-specific agreement text, never a generic page clause."""
    words = label.lower()
    clauses = _sentences(agreement)
    patterns = []
    # Specific item overrides generic words like "page" in every website task.
    if any(k in words for k in ('phone', 'contact information', 'contact number')):
        patterns = [('contact information', 'update'), ('phone',), ('contact', 'correction')]
    elif any(k in words for k in ('color', 'colour', 'background')):
        patterns = [('color', 'change'), ('colour', 'change')]
    elif any(k in words for k in ('heading', 'text correction', 'text update')):
        patterns = [('text', 'correction'), ('heading',)]
    elif any(k in words for k in ('revision', 'round')):
        patterns = [('revision',), ('round',)]
    elif any(k in words for k in ('page', 'testimonial', 'career')):
        patterns = [('website', 'includes'), ('page',)]
    for keywords in patterns:
        for clause in clauses:
            if all(keyword in clause.lower() for keyword in keywords):
                return clause
    return ''


def _known_included(label: str, agreement: str, requests: str) -> bool:
    """Narrow, fail-closed recognition of explicitly included edits within stated first revision."""
    a = agreement.lower(); label = label.lower(); r = requests.lower()
    if not any(x in r for x in ('first revision', '1st revision', 'revision round one', 'round 1')):
        return False
    if not any(x in a for x in ('two rounds of revisions','two revision rounds','2 rounds of revisions','2 revision rounds')):
        return False
    if ('phone' in label or 'contact number' in label) and 'contact information updates' in a:
        return True
    if any(x in label for x in ('color','colour','background')) and ('color changes' in a or 'colour changes' in a):
        return True
    if any(x in label for x in ('heading','text correction','text update')) and 'text corrections' in a:
        return True
    return False

@app.post("/api/analyze", response_model=AnalyzeResult)
def analyze(body: AnalyzeRequest):
    prompt = f"""Compare the original project agreement against later client requests.
Return an object with keys: summary (string) and items (array).
Each item needs: request (short string), classification (exactly one of included, potential_extra, needs_review), agreement_evidence (EXACT contiguous quote from agreement, or empty string), request_evidence (EXACT contiguous quote from client requests, or empty string), reasoning (short explanation), estimated_hours (numeric hours ONLY IF EXPLICITLY supplied in client request, otherwise null).
For missing evidence use an empty string, and lean needs_review for ambiguity. Do not estimate hours yourself. Do not manufacture monetary values.

AGREEMENT:\n{body.agreement}\n\nCLIENT REQUESTS:\n{body.requests}"""
    raw = call_ollama(prompt)
    try:
        parsed = json.loads(raw)
        summary = str(parsed.get("summary", "Review the identified requests."))[:1500]
        items = []
        for item in parsed.get("items", [])[:20]:
            if not isinstance(item, dict):
                continue
            ag_evidence = str(item.get("agreement_evidence", ""))
            req_evidence = str(item.get("request_evidence", ""))
            # Reject fabricated excerpts and downgrade unsupported conclusions.
            label = str(item.get("request", "Request"))[:200]
            verified_ag = _ground_quote(label, ag_evidence, body.agreement, client_request=False) or _agreement_clause(label, body.agreement)
            verified_req = _ground_quote(label, req_evidence, body.requests, client_request=True)
            category = item.get("classification", "needs_review")
            if category not in ("included", "potential_extra", "needs_review") or not verified_req:
                category = "needs_review"
            if _known_included(label, body.agreement, body.requests) and verified_req and verified_ag:
                category = "included"
            elif category == "potential_extra" and not verified_ag:
                category = "needs_review"
            # If the model's own reasoning says this is included, do not charge it.
            model_reason = str(item.get("reasoning", "")).lower()
            if category == "potential_extra" and any(term in model_reason for term in ('falls under the scope', 'included in the agreement', 'within the agreed scope', 'already included')):
                category = "needs_review"
            hours = item.get("estimated_hours")
            if not isinstance(hours, (int, float)) or hours < 0 or hours > 1000:
                hours = None
            # Hours are human-reviewed; do not accept LLM guesses in cost calculation.
            items.append(ScopeItem(
                request=label,
                classification=category,
                agreement_evidence=verified_ag,
                request_evidence=verified_req,
                reasoning=(str(item.get("reasoning", "Manual review recommended"))[:480] + (" Evidence requires human verification." if not verified_ag or not verified_req else "")),
                estimated_hours=None,
            ))
        # Persist the vetted output so proposals cannot forge classifications in the API.
        from backend.workflow import connection
        analysis_id = secrets.token_urlsafe(24)
        with connection() as db:
            db.execute('INSERT INTO analyses(id, items_json) VALUES(?, ?)',
                       (analysis_id, json.dumps([item.model_dump() for item in items])))
        if items and all(item.classification == 'included' for item in items):
            summary = 'All detected requests appear to be included in the stated agreement. No extra charges are suggested.'
        return AnalyzeResult(analysis_id=analysis_id, summary=summary, items=items, estimated_extra=0,
            disclaimer="Draft analysis, not legal advice. Confirm scope, estimates, rates and client approval before billing. Hour estimates must be entered by the freelancer.", model=MODEL)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=502, detail=f"Model returned invalid analysis; retry. Details: {exc}") from exc

from backend.workflow import router as workflow_router
app.include_router(workflow_router)
