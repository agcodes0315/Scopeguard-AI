import pytest
from fastapi import HTTPException
from backend.atlas import fingerprint, RecordException, PreviewRequest, record_exception, preview

class Graph:
    def __init__(self,rows=None,version=1):
        self.rows=rows or []
        self.version=version
        self.writes=[]
    def ro_query(self,query,params):
        if 'RETURN a.id,a.version,a.body' in query:
            result=[['agreement-'+str(self.version),self.version,'Agreement text']]
        elif 'RETURN a.id,a.version,e.id' in query:
            result=self.rows
        else: raise AssertionError(query)
        return type('R',(),{'result_set':result})()
    def query(self,query,params):
        self.writes.append((query,params))

def row(v,text='Add a Blog page',effect='included',approved=True,id='exception-1'):
    return ['agreement-'+str(v),v,id,text,fingerprint(text),effect,'One time waived for this project',approved,'confirmed_by_reviewer']

def test_matching_consent_verified():
    result=preview(PreviewRequest(project_id='p',request_text='  add A blog page  '),Graph([row(1)]))
    assert result['state']=='applicable_customer_approved_exception'
    assert result['recommendation']=='included'
    assert not result['billing_authorized']
    assert any(n['node']=='Exception' for n in result['evidence_path'])

def test_without_customer_approval_requires_review():
    result=preview(PreviewRequest(project_id='p',request_text='Add a Blog page'),Graph([row(1,approved=False)]))
    assert result['state']=='reviewer_confirmed_only'
    assert result['recommendation']=='needs_review'

def test_old_agreement_exception_not_applied():
    result=preview(PreviewRequest(project_id='p',request_text='Add a Blog page'),Graph([row(1)],version=2))
    assert result['state']=='stale_exception'
    assert result['recommendation']=='needs_review'

def test_unrelated_change_not_reused():
    result=preview(PreviewRequest(project_id='p',request_text='Add a Store page'),Graph([row(1)]))
    assert result['state']=='no_applicable_exception'
    assert not result['applicable_exceptions']

def test_conflict_requires_manual_resolution():
    result=preview(PreviewRequest(project_id='p',request_text='Add a Blog page'),Graph([row(1),row(1,effect='potential_extra',id='exception-2')]))
    assert result['state']=='conflict' and result['recommendation']=='needs_review'

def test_write_provenance_and_contract_binding():
    graph=Graph()
    out=record_exception(RecordException(project_id='p',request_text='Add a Blog page',effect='included',reason='One time client-approved waiver',reviewer='Owner'),graph)
    assert out['agreement_version']==1
    assert graph.writes[0][1]['approved'] is False
    assert 'HAS_EXCEPTION' in graph.writes[0][0]

def test_case_and_whitespace_hash():
    assert fingerprint('A  NEW page')==fingerprint('a new page')
