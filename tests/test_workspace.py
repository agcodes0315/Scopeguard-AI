from fastapi.testclient import TestClient
from backend.main import app
from backend import workspace

def test_projects_vault_inbox_and_versions(tmp_path,monkeypatch):
    monkeypatch.setattr(workspace,'DB',tmp_path/'workspace.db')
    c=TestClient(app)
    r=c.post('/api/workspace/projects',json={'name':'Website','client_label':'Demo Client'})
    assert r.status_code==201
    pid=r.json()['id']
    text='The project includes five pages. Extra pages require written approval.'
    a=c.post(f'/api/workspace/projects/{pid}/agreements',json={'text':text})
    assert a.status_code==201 and a.json()['version']==1
    assert a.json()['clauses'][0]['quote'] in text
    b=c.post(f'/api/workspace/projects/{pid}/agreements',json={'text':text+' Final date October 20.'})
    assert b.json()['version']==2
    latest=c.get(f'/api/workspace/projects/{pid}/agreements/latest').json()
    assert latest['version']==2 and 'sha256' in latest
    msg=c.post(f'/api/workspace/projects/{pid}/messages',json={'message':'Add two new pages'})
    assert msg.status_code==201
    assert len(c.get(f'/api/workspace/projects/{pid}/messages').json()['messages'])==1
    assert c.patch('/api/workspace/messages/'+msg.json()['id']+'/reviewed').json()['reviewed']

def test_drafts_do_not_invent_costs(tmp_path,monkeypatch):
    c=TestClient(app)
    payload={'client_label':'Sample Client','project_title':'Website','currency':'INR','extra_total':0,'items':[]}
    r=c.post('/api/workspace/draft-reply',json=payload)
    assert r.status_code==200 and 'clarify' in r.json()['body'].lower()
    payload.update(extra_total=2500,items=['Third revision round'])
    r=c.post('/api/workspace/draft-reply',json=payload)
    assert '2,500.00' in r.json()['body'] and 'Third revision round' in r.json()['body']

def test_unknown_project_rejected(tmp_path,monkeypatch):
    monkeypatch.setattr(workspace,'DB',tmp_path/'workspace.db')
    c=TestClient(app)
    assert c.get('/api/workspace/projects/not-real/agreements/latest').status_code==404
