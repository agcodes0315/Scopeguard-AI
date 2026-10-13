import json
from fastapi.testclient import TestClient
from backend.main import app
import backend.main as main
import backend.workflow as workflow

AGREEMENT = ('The client commissions a five-page website for INR 30,000. '
'The website includes Home, About, Services, Portfolio, and Contact pages. '
'The agreement includes two rounds of revisions. '
'Text corrections, color changes, and contact information updates are included within these revision rounds. '
'Additional pages or revisions beyond two rounds require separate approval and pricing.')
REQUESTS = ('Please correct the phone number on the Contact page. '
'Change the background color of the Services page. '
'Update the heading text on the Home page. '
'This is our first revision round.')

def test_included_requests_cannot_be_billed(tmp_path,monkeypatch):
    monkeypatch.setattr(workflow,'DB',tmp_path/'safety.db')
    def model(_):
        return json.dumps({'summary':'Wrongly claimed outside scope','items':[
            {'request':'Correct phone number on Contact page','classification':'potential_extra','request_evidence':'Please correct the phone number on the Contact page.','agreement_evidence':'','reasoning':'needs extra payment'},
            {'request':'Change background color of Services page','classification':'potential_extra','request_evidence':'Change the background color of the Services page.','agreement_evidence':'','reasoning':'needs extra payment'},
            {'request':'Update heading text on Home page','classification':'potential_extra','request_evidence':'Update the heading text on the Home page.','agreement_evidence':'','reasoning':'needs extra payment'},
        ]})
    monkeypatch.setattr(main,'call_ollama',model)
    c=TestClient(app)
    response=c.post('/api/analyze',json={'agreement':AGREEMENT,'requests':REQUESTS})
    assert response.status_code==200
    analysis=response.json()
    assert [x['classification'] for x in analysis['items']]==['included']*3
    assert 'No extra charges' in analysis['summary']
    assert all(x['agreement_evidence'] in AGREEMENT for x in analysis['items'])
    result=c.post('/api/proposals',json={'title':'Wrong extra charge','currency':'INR','hourly_rate':1000,
        'analysis_id':analysis['analysis_id'],'item_indices':[0],
        'items':[{'description':analysis['items'][0]['request'],'hours':3,'evidence':analysis['items'][0]['request_evidence']}]})
    assert result.status_code==422

def test_cannot_forge_analyzed_evidence_or_bypass_review(tmp_path,monkeypatch):
    monkeypatch.setattr(workflow,'DB',tmp_path/'checks.db')
    with workflow.connection() as db:
        assert db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analyses'").fetchone() is not None
        db.execute('INSERT INTO analyses(id,items_json) VALUES(?,?)',('analysis-123456',json.dumps([
            {'request':'Uncertain work','classification':'needs_review','agreement_evidence':'a','request_evidence':'b'},
            {'request':'New page','classification':'potential_extra','agreement_evidence':'five pages','request_evidence':'Add new page'}])))
    c=TestClient(app)
    payload={'title':'Proposal test','currency':'INR','hourly_rate':1000,'analysis_id':'analysis-123456','item_indices':[0],
       'items':[{'description':'Uncertain work','hours':3,'evidence':'b'}]}
    assert c.post('/api/proposals',json=payload).status_code==422
    payload['item_indices']=[1];payload['items']=[{'description':'New page','hours':3,'evidence':'fake'}]
    assert c.post('/api/proposals',json=payload).status_code==422
    payload['items'][0]['evidence']='Add new page'
    assert c.post('/api/proposals',json=payload).status_code==201
