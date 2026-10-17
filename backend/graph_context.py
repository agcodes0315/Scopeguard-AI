"""FalkorDB-backed, human-confirmed scope decision memory.

This is intentionally separate from the original Gemma billing/proposal flow:
Graph data is indispensable to these endpoints; no SQLite fallback exists.
Only synthetic/public data belongs in the unauthenticated hackathon demo.
"""
from __future__ import annotations

import hashlib
import os
import re
import secrets
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix='/api/graph', tags=['FalkorDB Context'])
GRAPH_NAME = os.getenv('FALKORDB_GRAPH', 'scopeguard_demo')


def get_graph():
    try:
        from falkordb import FalkorDB
        db = FalkorDB(host=os.getenv('FALKORDB_HOST', '127.0.0.1'),
                      port=int(os.getenv('FALKORDB_PORT', '6379')),
                      password=os.getenv('FALKORDB_PASSWORD') or None,
                      socket_timeout=5)
        graph = db.select_graph(GRAPH_NAME)
        graph.query('RETURN 1')  # Fail closed: no alternate backing store.
        return graph
    except Exception as exc:
        raise HTTPException(503, 'FalkorDB context unavailable; graph-backed decisions are disabled.') from exc


def _key(text: str) -> str:
    return hashlib.sha256(' '.join(text.lower().split()).encode()).hexdigest()


def _clauses(agreement: str) -> list[str]:
    return [line.strip() for line in re.split(r'(?<=[.!?])\s+|\n+', agreement) if line.strip()][:60]


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    agreement: str = Field(min_length=20, max_length=30000)
    owner: str = Field(default='Demo Freelancer', max_length=100)


class GraphAnalyze(BaseModel):
    project_id: str
    request: str = Field(min_length=5, max_length=15000)


class ConfirmDecision(BaseModel):
    project_id: str
    request_id: str
    classification: Literal['included', 'potential_extra', 'needs_review']
    reviewer_note: str = Field(min_length=3, max_length=400)


def create_project(payload: ProjectCreate, graph=None):
    graph = graph or get_graph()
    pid = secrets.token_hex(12)
    version = secrets.token_hex(8)
    graph.query('''MERGE (p:Project {id:$pid}) SET p.name=$name, p.owner=$owner
        CREATE (a:Agreement {id:$version, body:$body, version:1})
        CREATE (p)-[:HAS_AGREEMENT]->(a)''',
        {'pid':pid,'name':payload.name,'owner':payload.owner,'version':version,'body':payload.agreement})
    for idx, clause in enumerate(_clauses(payload.agreement)):
        graph.query('''MATCH (a:Agreement {id:$version})
            CREATE (c:Clause {id:$cid, text:$text, position:$idx})
            CREATE (a)-[:CONTAINS]->(c)''',
            {'version':version,'cid':f'{version}:{idx}','text':clause,'idx':idx})
    return {'project_id':pid,'agreement_id':version,'clause_count':len(_clauses(payload.agreement))}


def classify_graph_context(request: str, agreement: str, confirmed_rows: list, clauses: list):
    """Context decision tool. Human approvals win ONLY for same request+same contract version.

    Everything else is advisory and intentionally conservative. The original
    evidence-guarded Gemma analyzer still handles first-time scope analysis.
    """
    request_hash = _key(request)
    for req_id, stored_text, category, note, status in confirmed_rows:
        if status == 'confirmed' and _key(stored_text) == request_hash:
            return category, 'Prior HUMAN-CONFIRMED decision for the same request and agreement version: '+note, req_id
    return None, '', None


def analyze_project(payload: GraphAnalyze, graph=None, analyzer=None):
    graph = graph or get_graph()
    # Graph is the ONLY authority for project agreement/version.
    rows = graph.ro_query('''MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement)
        RETURN a.id, a.body, a.version ORDER BY a.version DESC LIMIT 1''',
        {'pid':payload.project_id}).result_set
    if not rows:
        raise HTTPException(404, 'Project not found in FalkorDB.')
    aid, agreement, version = rows[0]
    clauses = graph.ro_query('''MATCH (a:Agreement {id:$aid})-[:CONTAINS]->(c:Clause)
        RETURN c.id,c.text ORDER BY c.position''', {'aid':aid}).result_set
    previous = graph.ro_query('''MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement {id:$aid})
        <-[:BASED_ON]-(r:Request)-[:HAS_DECISION]->(d:Decision)
        RETURN r.id,r.text,d.classification,d.reviewer_note,d.status''',
        {'pid':payload.project_id,'aid':aid}).result_set
    remembered, memo, prior_id = classify_graph_context(payload.request, agreement, previous, clauses)
    request_id = secrets.token_hex(12)
    graph.query('''MATCH (p:Project {id:$pid})-[:HAS_AGREEMENT]->(a:Agreement {id:$aid})
        CREATE (r:Request {id:$rid, text:$text, hash:$hash})
        CREATE (p)-[:RECEIVED]->(r)
        CREATE (r)-[:BASED_ON]->(a)''',
        {'pid':payload.project_id,'aid':aid,'rid':request_id,'text':payload.request,'hash':_key(payload.request)})
    verified_evidence = False
    if remembered:
        category, explanation = remembered, memo
        source = 'graph_memory'
        evidence = [{'from':'Project:'+payload.project_id,'via':'HAS_AGREEMENT','to':'Agreement:'+aid},
                    {'from':'Request:'+prior_id,'via':'HAS_DECISION','to':'ConfirmedDecision'},
                    {'from':'Request:'+request_id,'via':'MATCHED_PRIOR_REQUEST','to':'Request:'+prior_id}]
    else:
        # The original analyzer runs only after graph context has selected the agreement.
        if analyzer is None:
            from backend.main import AnalyzeRequest, analyze
            analyzer = lambda a, r: analyze(AnalyzeRequest(agreement=a, requests=r))
        result = analyzer(agreement, payload.request)
        items = result.items
        # Exact text checks are a prerequisite, NOT proof of semantic correctness.
        verified_evidence = (
            len(items) == 1 and
            items[0].classification == 'potential_extra' and
            bool(items[0].agreement_evidence) and
            bool(getattr(items[0], 'request_evidence', '')) and
            str(items[0].agreement_evidence) in str(agreement) and
            str(items[0].request_evidence) in str(payload.request) and
            any(str(items[0].agreement_evidence) in str(row[1]) for row in clauses)
        )
        category = items[0].classification if len(items)==1 else 'needs_review'
        explanation = items[0].reasoning if len(items)==1 else 'Multiple findings: manual review required.'
        source = 'graph_agreement_plus_gemma'
        matching = [(str(cid),str(text)) for cid,text in clauses if len(items)==1 and items[0].agreement_evidence and items[0].agreement_evidence in text]
        evidence = [{'from':'Project:'+payload.project_id,'via':'HAS_AGREEMENT','to':'Agreement:'+aid}]
        evidence += [{'from':'Agreement:'+aid,'via':'CONTAINS','to':'Clause:'+cid,'quote':text} for cid,text in matching]
        # Preserve original evidence-guarded classification. Never make automatic billing/approval.
    graph.query('''MATCH (r:Request {id:$rid})
        CREATE (d:Decision {id:$did, classification:$category, status:'pending',
                            reviewer_note:'', source:$source})
        CREATE (r)-[:HAS_DECISION]->(d)''',
        {'rid':request_id,'did':secrets.token_hex(12),'category':category,'source':source})
    return {'project_id':payload.project_id,'request_id':request_id,'agreement_id':aid,
            'classification':category,'source':source,'reasoning':explanation,
            'evidence_path':evidence,'prior_decisions_considered':len(previous),
            'verified_evidence':verified_evidence,
            'requires_human_confirmation':True,
            'disclaimer':'Advisory only; no pricing, invoice, or client approval is performed.'}


def confirm(payload: ConfirmDecision, graph=None):
    graph = graph or get_graph()
    rows = graph.ro_query('''MATCH (p:Project {id:$pid})-[:RECEIVED]->(r:Request {id:$rid})
        -[:HAS_DECISION]->(d:Decision) RETURN d.status''',
        {'pid':payload.project_id,'rid':payload.request_id}).result_set
    if not rows:
        raise HTTPException(404, 'Decision not found for project.')
    if rows[0][0] != 'pending':
        raise HTTPException(409, 'This decision was already confirmed.')
    graph.query('''MATCH (p:Project {id:$pid})-[:RECEIVED]->(r:Request {id:$rid})
        -[:HAS_DECISION]->(d:Decision)
        SET d.classification=$category,d.status='confirmed',d.reviewer_note=$note''',
        {'pid':payload.project_id,'rid':payload.request_id,
         'category':payload.classification,'note':payload.reviewer_note})
    return {'status':'confirmed','request_id':payload.request_id,'classification':payload.classification}


@router.get('/health')
def graph_health():
    graph = get_graph()
    return {'status':'ok','graph':GRAPH_NAME,'connected':bool(graph)}


@router.post('/projects')
def graph_project(payload: ProjectCreate):
    return create_project(payload)


@router.post('/analyze')
def graph_analyze(payload: GraphAnalyze):
    return analyze_project(payload)


@router.post('/confirm')
def graph_confirm(payload: ConfirmDecision):
    return confirm(payload)
