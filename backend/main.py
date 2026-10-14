"""ScopeGuard AI MVP — locally hosted FastAPI + open-weight Gemma via Ollama."""
import json
import secrets
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from backend.documents import extract_document

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

@app.post("/api/documents/extract")
async def upload_agreement(file: UploadFile = File(...)):
    """Text-only extraction; no uploaded document is written to disk."""
    contents = await file.read(3 * 1024 * 1024 + 1)
    try:
        return extract_document(file.filename or "", contents)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


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
    elif any(k in words for k in ('heading', 'text correction', 'text update', 'description text', 'portfolio description', 'spelling', 'typo')):
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


def _tentative_request(text: str) -> bool:
    """Conservative: discussion of future possibilities isn't an approved change.

    Detect exploratory phrasing, without downgrading direct explicit instructions.
    This is a heuristic, NOT a calibrated model confidence score.
    """
    t = " ".join(text.lower().split())
    return bool(re.search(
        r"\b(?:may|might|maybe|perhaps|possibly|potentially)\b"
        r"|\b(?:would|could)\s+(?:a|an|the|adding|we|you|it)\b"
        r"|\b(?:consider|thinking about|wondering if)\b"
        r"|\b(?:be a good idea|later|someday)\b", t,
    ))


def _explicit_extra_policy(label: str, request_quote: str, agreement: str) -> str:
    """Return an exact contract clause only when a definite extra matches a policy.

    This is a constrained evidence check, NOT a general classifier. Absence of
    a clear contract rule or unclear intent must fall back to needs_review.
    """
    if not request_quote or _tentative_request(request_quote):
        return ""
    r = request_quote.lower()
    a = agreement.lower()
    clauses = _sentences(agreement)

    # Contract explicitly prices additional pages separately. Only treat an
    # affirmative request for a genuinely NEW page as a possible extra.
    # Never treat edits to Home/About/Services/etc as additional pages.
    new_page = bool(re.search(
        r"\b(?:add|create|build|develop|include|make)\b.{0,75}\b(?:new |extra |additional )?(?:[a-z][a-z -]{0,30} )?pages?\b", r
    ))
    if new_page:
        # A request for an existing named page is not evidence of a new page.
        match = re.search(r"\b(?:add|create|build|develop|include|make)\b.{0,75}?\b(?:a|an|the|new|extra|additional)\s+([a-z][a-z -]{0,30}?)\s+pages?\b", r)
        requested_name = match.group(1).strip() if match else ""
        if requested_name and re.search(r"\b(?:home|about|services|portfolio|contact)\b", requested_name):
            return ""
        for clause in clauses:
            low = clause.lower()
            if re.search(r"\b(?:additional|extra|new)\s+pages?\b", low) and re.search(r"\b(?:separate|additional)\s+(?:approval|pricing|cost|charge)|\b(?:out of scope|not included)\b", low):
                return clause

    # Exceeding an explicitly contracted revision limit is a potential extra.
    round_match = re.search(r"\b(?:third|3rd|fourth|4th|fifth|5th|sixth|6th|[3-9](?:th)?)(?:\s+revision|\s+round)|\brevision\s+(?:round\s+)?(?:three|four|five|six|[3-9])\b", r)
    if round_match and re.search(r"\b(?:two|2)\s+(?:rounds?\s+of\s+revisions?|revision\s+rounds?)\b", a):
        for clause in clauses:
            low = clause.lower()
            if 'revision' in low and (re.search(r"\b(?:third|3rd|additional|extra)\b", low) and re.search(r"\b(?:approval|pricing|charge|cost|bill)\b", low)):
                return clause
    return ""


def _known_included(label: str, agreement: str, request_text: str) -> bool:
    """Confirm only narrow, explicit included work and named revision rounds.

    Unknown terms, vague requests, and missing contract language remain for review.
    """
    a, label, r = agreement.lower(), label.lower(), request_text.lower()
    if not re.search(r"\b(?:first|second|1st|2nd|round\s*[12])\s+revision\b|\brevision\s*(?:round\s*)?(?:one|two|1|2)\b", r):
        return False
    if not re.search(r"\b(?:two|2)\s+(?:rounds?\s+of\s+revisions?|revision\s+rounds?)\b", a):
        return False
    if _tentative_request(request_text):
        return False
    if re.search(r"\b(?:phone|contact\s+(?:number|email|information)|email address)\b", label):
        return "contact information updates" in a
    if re.search(r"\b(?:color|colour|background)\b", label):
        return "color changes" in a or "colour changes" in a or "color adjustments" in a
    if re.search(r"\b(?:heading|headline|description|text|typo|spelling)\b", label):
        return "text corrections" in a or "text updates" in a
    return False

@app.post("/api/analyze", response_model=AnalyzeResult)
def analyze(body: AnalyzeRequest):
    prompt = f"""Compare the original project agreement against later client requests.
Return an object with keys: summary (string) and items (array).
Each item needs: request (short string), classification (exactly one of included, potential_extra, needs_review), agreement_evidence (EXACT contiguous quote from agreement, or empty string), request_evidence (EXACT contiguous quote from client requests, or empty string), reasoning (short explanation), estimated_hours (numeric hours ONLY IF EXPLICITLY supplied in client request, otherwise null).
For missing evidence use an empty string, and lean needs_review for ambiguity. Exploratory questions, possible future changes, and tentative requests are needs_review, not potential_extra. Included work during the first or second agreed revision round is included. Do not estimate hours yourself. Do not manufacture monetary values.

AGREEMENT:\n{body.agreement}\n\nCLIENT REQUESTS:\n{body.requests}"""
    raw = call_ollama(prompt)
    try:
        parsed = json.loads(raw)
        summary = str(parsed.get("summary", "Review the identified requests."))[:1500]
        items = []
        # With a single exploratory request, collapse multiple invented sub-items.
        tentative_message = bool(_sentences(body.requests)) and all(_tentative_request(sentence) for sentence in _sentences(body.requests))
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
            # Confirm explicit, evidence-backed additional work even when the
            # model conservatively labels it needs_review. Never override
            # exploratory requests, missing client evidence, or unclear scope.
            policy_clause = _explicit_extra_policy(label, verified_req, body.agreement)
            if policy_clause and verified_req and not tentative_message:
                verified_ag = policy_clause
                category = "potential_extra"
            # Only narrow exact-scope edits may be overridden to included.
            if _known_included(label, body.agreement, body.requests) and verified_req and verified_ag:
                category = "included"
            elif category == "potential_extra" and not verified_ag:
                category = "needs_review"
            # Tentative requests are questions, never automatic billing authority.
            # For a single exploratory message, all model-split items inherit this safeguard.
            if tentative_message or _tentative_request(verified_req):
                category = "needs_review"
            # If the model's own reasoning says this is included, do not charge it.
            model_reason = str(item.get("reasoning", "")).lower()
            if category == "potential_extra" and any(term in model_reason for term in ('falls under the scope', 'included in the agreement', 'within the agreed scope', 'already included')):
                category = "needs_review"
            hours = item.get("estimated_hours")
            if not isinstance(hours, (int, float)) or hours < 0 or hours > 1000:
                hours = None
            # Hours are human-reviewed; do not accept LLM guesses in cost calculation.
            if tentative_message and items:
                # One exploratory message may be split into multiple imagined tasks.
                # Keep one review finding to avoid multiple misleading alerts.
                continue
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
        if items and not any(item.classification == 'potential_extra' for item in items):
            summary = 'No evidence-verified additional charges were found. Some findings may still require review.'
        if items and all(item.classification == 'included' for item in items):
            summary = 'All detected requests appear to be included in the stated agreement. No extra charges are suggested.'
        return AnalyzeResult(analysis_id=analysis_id, summary=summary, items=items, estimated_extra=0,
            disclaimer="Draft analysis, not legal advice. Confirm scope, estimates, rates and client approval before billing. Hour estimates must be entered by the freelancer.", model=MODEL)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=502, detail=f"Model returned invalid analysis; retry. Details: {exc}") from exc

from backend.workflow import router as workflow_router
app.include_router(workflow_router)

from backend.workspace import router as workspace_router
app.include_router(workspace_router)

@app.get("/workspace.js")
def workspace_script():
    return FileResponse(ROOT / "frontend" / "workspace.js", media_type="application/javascript")
