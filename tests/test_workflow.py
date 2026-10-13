import os
import tempfile
from fastapi.testclient import TestClient
from backend.main import app
import backend.workflow as workflow

def test_proposal_lifecycle(tmp_path,monkeypatch):
    monkeypatch.setattr(workflow,'DB',tmp_path/'test.db')
    c=TestClient(app)
    with workflow.connection() as db:
        db.execute("INSERT INTO analyses(id, items_json) VALUES(?, ?)", ('testing-analysis-12345', '[{"request":"New page","classification":"potential_extra","agreement_evidence":"Five pages included","request_evidence":"Add a new page"}]'))
    resp=c.post('/api/proposals',json={'title':'Client site revision','currency':'INR','hourly_rate':850,'analysis_id':'testing-analysis-12345','item_indices':[0],'items':[{'description':'New page','hours':2,'evidence':'Add a new page'}]})
    assert resp.status_code==201
    token=resp.json()['token']
    data=c.get('/api/proposals/'+token).json()
    assert data['total']==1700
    assert data['status']=='pending'
    pdf=c.get('/api/proposals/'+token+'/pdf')
    assert pdf.status_code==200 and pdf.content.startswith(b'%PDF')
    decision=c.post('/api/proposals/'+token+'/decision',json={'decision':'approved','note':'Looks good'})
    assert decision.status_code==200
    assert decision.json()['status']=='approved'
    assert c.post('/api/proposals/'+token+'/decision',json={'decision':'rejected'}).status_code==409

def test_reject_invalid_prices(tmp_path,monkeypatch):
    monkeypatch.setattr(workflow,'DB',tmp_path/'test2.db')
    c=TestClient(app)
    assert c.post('/api/proposals',json={'title':'Test contract','hourly_rate':-2,'items':[{'description':'Change','hours':2}]}).status_code==422
    assert c.get('/api/proposals/not-a-valid-token').status_code==404
