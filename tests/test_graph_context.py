import pytest
from fastapi import HTTPException
from backend.graph_context import (
    _key, _clauses, classify_graph_context,
    ProjectCreate, GraphAnalyze, ConfirmDecision,
    create_project, analyze_project, confirm,
)

class FakeGraph:
    def __init__(self):
        self.calls=[]
        self.agreement=None
        self.clauses=[]
        self.previous=[]
        self.status='pending'
    def query(self, text, params=None):
        self.calls.append((text,params))
        if 'CREATE (a:Agreement' in text:
            self.agreement=(params['version'],params['body'],1)
        if 'CREATE (c:Clause' in text:
            self.clauses.append((params['cid'],params['text']))
        if "SET d.classification" in text:
            self.status='confirmed'
        return type('Result',(),{'result_set':[[1]]})()
    def ro_query(self, text, params=None):
        if 'RETURN a.id, a.body' in text:
            rows=[list(self.agreement)] if self.agreement else []
        elif 'RETURN c.id,c.text' in text:
            rows=[list(x) for x in self.clauses]
        elif 'RETURN r.id,r.text' in text:
            rows=self.previous
        elif 'RETURN d.status' in text:
            rows=[[self.status]]
        else:
            raise AssertionError(text)
        return type('Result',(),{'result_set':rows})()

def test_hash_normalization():
    assert _key('Please ADD a page')==_key(' please   add A page ')
    assert _key('Add a blog')!=_key('Add a shop')

def test_clauses_are_bounded():
    assert len(_clauses(('One clause. ')*80)) ==60

def test_prior_pending_is_not_memory():
    rows=[['prior','Add a Blog page','included','offered free','pending']]
    assert classify_graph_context('Add a Blog page','contract',rows,[])[0] is None

def test_approved_same_request_is_memory():
    rows=[['prior','Add a Blog page','included','one-time exception','confirmed']]
    assert classify_graph_context('add a blog  page','contract',rows,[])[0]=='included'

def test_different_request_not_reused():
    rows=[['prior','Add a Blog page','included','one-time exception','confirmed']]
    assert classify_graph_context('Add a Store page','contract',rows,[])[0] is None

def test_create_graph_structure():
    graph=FakeGraph()
    out=create_project(ProjectCreate(name='Demo',agreement='Five pages included. Extra pages require separate approval.'),graph)
    assert out['clause_count']==2
    assert len(graph.clauses)==2
    assert any('HAS_AGREEMENT' in text for text,_ in graph.calls)

def test_graph_required_for_analysis():
    with pytest.raises(HTTPException) as exc:
        analyze_project(GraphAnalyze(project_id='missing',request='Add a new page'),FakeGraph())
    assert exc.value.status_code==404

def test_live_graph_query_precedes_analyzer():
    graph=FakeGraph()
    created=create_project(ProjectCreate(name='Demo',agreement='Five pages included. Extra pages require separate approval.'),graph)
    class Item:
        classification='potential_extra'
        reasoning='New page exceeds the contract.'
        agreement_evidence='Extra pages require separate approval.'
    class Analysis:
        items=[Item()]
    calls=[]
    def analyzer(agreement,request):
        calls.append((agreement,request))
        return Analysis()
    out=analyze_project(GraphAnalyze(project_id=created['project_id'],request='Please add a Blog page'),graph,analyzer)
    assert out['source']=='graph_agreement_plus_gemma'
    assert out['classification']=='potential_extra'
    assert out['requires_human_confirmation']
    assert len(calls)==1 and calls[0][0].startswith('Five pages')
    assert any(x['via']=='CONTAINS' for x in out['evidence_path'])

def test_confirmed_graph_memory_skips_model():
    graph=FakeGraph()
    created=create_project(ProjectCreate(name='Demo',agreement='Five pages included. Extra pages require separate approval.'),graph)
    graph.previous=[['prior','Please add a Blog page','included','Approved free for this agreement','confirmed']]
    def must_not_run(*_):
        raise AssertionError('Gemma must not run when graph contains confirmed same-contract decision')
    out=analyze_project(GraphAnalyze(project_id=created['project_id'],request='Please add a Blog page'),graph,must_not_run)
    assert out['classification']=='included'
    assert out['source']=='graph_memory'
    assert any(x['via']=='MATCHED_PRIOR_REQUEST' for x in out['evidence_path'])

def test_confirm_is_human_action():
    graph=FakeGraph()
    out=confirm(ConfirmDecision(project_id='project',request_id='req',classification='needs_review',reviewer_note='Needs customer input'),graph)
    assert out['status']=='confirmed'
    with pytest.raises(HTTPException) as exc:
        confirm(ConfirmDecision(project_id='project',request_id='req',classification='needs_review',reviewer_note='Needs customer input'),graph)
    assert exc.value.status_code==409
