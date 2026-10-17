'''ScopeGuard Atlas: explicit, agreement-version-bound graph exceptions.

Every decision remains advisory. This extension never creates an invoice or
claims that freelancer confirmation is equivalent to customer consent.
Graph storage is mandatory; no fallback to SQLite is implemented.
'''
from __future__ import annotation

import hashlib
import secrets
from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.graph_context import get_graph

router = APIRouter(prefix="/api/atlas", tags=["ScopeGuard Atlas"])


def fingerprint(text: str) -> str:
    return hashlib.sha256(" ".join(text.casefold().split()).encode("utf-8")).hexdigest()


class RecordException(BaseModel):
    project_id: str = Field(min_length=1)
    request_text: str = Field(min_length=5, max_length=15000)
    effect: Literal["included", "potential_extra", "needs_review"]
    reason: str = Field(min_length=12, max_length=1000)
    reviewer: str = Field(min_length=2, max_length=100)
    customer_approved: bool = False


class PreviewRequest(BaseModel):
    project_id: str = Field(min_length=1)
    request_text: str = Field(min_length=5, max_length=15000)


def _current(graph, pid: str):
    rows = graph.ro_query('''MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement)
        RETURN a.id,a.version,a.body ORDER BY a.version DESC LIMIT 1''', {"pid": pid}).result_set
    if not rows:
        raise HTTPException(404, "Project not found in FalkorDB")
    return str(rows[0][0]), int(rows[0][1]), str(rows[0][2])


def record_exception(payload: RecordException, graph=None):
    '''Write a reviewer-acknowledged exception; customer consent stays explicit.'''
    graph = graph if graph is not None else get_graph()
    aid, version, _ = _current(graph, payload.project_id)
    eid = secrets.token_hex(12)
    graph.query('''MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement {id:$aid})
        CREATE (e:Exception {id:$eid, request_text:$txt, request_hash:$h,
          effect:$effect, reason:$reason, reviewer:$reviewer,
          customer_approved:$approved, status:'confirmed_by_reviewer', agreement_version:$ver})
        CREATE (a)-[:HAS_EXCEPTION]->(e)
        CREATE (p)-[:RECORDED_EXCEPTION]->(e)''', {
        "pid":payload.project_id,"aid":aid,"eid":eid,"txt":payload.request_text,
        "h":fingerprint(payload.request_text),"effect":payload.effect,
        "reason":payload.reason,"reviewer":payload.reviewer,
        "approved":payload.customer_approved,"ver":version,
    })
    return {"exception_id":eid,"agreement_id":aid,"agreement_version":version,
            "status":"confirmed_by_reviewer","customer_approved":payload.customer_approved,
            "note":"Reviewer confirmation alone does not establish client approval or authorize billing."}


def preview(payload: PreviewRequest, graph=None):
    '''Trace matching exceptions for the active agreement; never silently apply stale ones.

    Deliberately exact-normalized matching: semantically related requests cannot
    inherit an exception without an independent human applicability judgment.
    '''
    graph = graph if graph is not None else get_graph()
    aid, version, agreement = _current(graph, payload.project_id)
    rows = graph.ro_query('''MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement)
        -[:HAS_EXCEPTION]->(e:Exception)
        RETURN a.id,a.version,e.id,e.request_text,e.request_hash,e.effect,
               e.reason,e.customer_approved,e.status ORDER BY a.version DESC''',
        {"pid":payload.project_id}).result_set
    h = fingerprint(payload.request_text)
    matching=[]
    older=[]
    for agreement_id, v, eid, text, saved_hash, effect, reason, approved, status in rows:
        # Derive hash from stored text if historical data lacks it.
        if (saved_hash or fingerprint(str(text))) != h or status != 'confirmed_by_reviewer':
            continue
        entry={"exception_id":str(eid),"agreement_id":str(agreement_id),
               "agreement_version":int(v),"effect":str(effect),
               "reason":str(reason),"customer_approved":bool(approved)}
        if str(agreement_id)==aid and int(v)==version:
            matching.append(entry)
        else:
            older.append(entry)
    effects=set(x['effect'] for x in matching)
    if len(effects)>1:
        state="conflict"
        recommendation="needs_review"
        message="Conflicting human decisions exist for this exact request and active agreement. Clarify before acting."
    elif matching and all(x['customer_approved'] for x in matching):
        state="applicable_customer_approved_exception"
        recommendation=matching[0]['effect']
        message="Matching exception on the active agreement has an explicit customer-approved flag; verify its supporting consent record before acting."
    elif matching:
        state="reviewer_confirmed_only"
        recommendation="needs_review"
        message="Reviewer-confirmed exception found, but customer approval is not established."
    elif older:
        state="stale_exception"
        recommendation="needs_review"
        message="A matching historical exception belongs to an older agreement and cannot be reused automatically."
    else:
        state="no_applicable_exception"
        recommendation="needs_review"
        message="No exact applicable exception found. Run the standard Gemma analysis and review evidence."
    return {"project_id":payload.project_id,"agreement_id":aid,"agreement_version":version,
        "request_text":payload.request_text,"state":state,"recommendation":recommendation,
        "explanation":message,"applicable_exceptions":matching,"stale_exceptions":older,
        "evidence_path":[{"node":"Project","id":payload.project_id},
                         {"node":"Agreement","id":aid,"version":version}]+
                        [{"node":"Exception","id":x['exception_id'],"effect":x['effect'],"approved":x['customer_approved']} for x in matching],
        "requires_human_review":True,"billing_authorized":False,
        "disclaimer":"Advisory memory lookup only. No money is charged, no automatic approval is made."}


@router.post('/exceptions')
def record_route(payload: RecordException):
    return record_exception(payload)


@router.post('/preview')
def preview_route(payload: PreviewRequest):
    return preview(payload)
