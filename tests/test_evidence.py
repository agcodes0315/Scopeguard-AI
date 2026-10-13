from fastapi.testclient import TestClient
from backend.main import app, _ground_quote
import backend.main as main

AGREEMENT = 'The client commissions five pages: Home, About, Services, Portfolio, Contact. The price includes two rounds of revisions.'
REQUESTS = 'Please add a Testimonials page and a Careers page to the site. We also need a third revision round to redo the home page.'

def test_mismatched_quote_is_replaced_with_relevant_exact_quote():
    bad = 'We also need a third revision round to redo the home page.'
    correct = _ground_quote('Add Careers page', bad, REQUESTS, client_request=True)
    assert 'Careers page' in correct
    assert 'third revision' not in correct
    assert correct in REQUESTS

def test_no_unrelated_evidence_when_no_supporting_text():
    assert _ground_quote('Add payment gateway', 'third revision round', REQUESTS, client_request=True) == ''

def test_analysis_end_to_end_misquoted_model(monkeypatch):
    import json
    def fake_model(_):
        return json.dumps({'summary':'Possible extras', 'items':[
            {'request':'Add Careers page','classification':'potential_extra','agreement_evidence':'','request_evidence':'We also need a third revision round to redo the home page.','reasoning':'new page'},
            {'request':'Third revision round','classification':'potential_extra','agreement_evidence':'The price includes two rounds of revisions.','request_evidence':'We also need a third revision round to redo the home page.','reasoning':'extra round'}]})
    monkeypatch.setattr(main,'call_ollama',fake_model)
    resp=TestClient(app).post('/api/analyze',json={'agreement':AGREEMENT,'requests':REQUESTS})
    assert resp.status_code == 200
    a,b=resp.json()['items']
    assert 'Careers page' in a['request_evidence']
    assert 'third revision' not in a['request_evidence']
    assert a['classification']=='potential_extra'
    assert b['agreement_evidence'] in AGREEMENT
    assert b['request_evidence'] in REQUESTS
