"""Checks all 24 human-labelled scenarios against conservative evidence guardrails.

The Ollama response is deliberately mocked to stress post-processing. This
DOES NOT claim a 24/24 live Gemma result.
"""
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend import main, workflow

CASES = json.loads((Path(__file__).resolve().parents[1] / 'evaluation' / 'cases.json').read_text())


@pytest.mark.parametrize('case', CASES, ids=[c['id'] for c in CASES])
def test_policy_does_not_depend_on_model_guess(monkeypatch, tmp_path, case):
    monkeypatch.setattr(workflow, 'DB', tmp_path / 'test.db')
    # Simulates an overly conservative or excessively eager model.
    opposite = 'needs_review' if case['expected'] == 'potential_extra' else 'potential_extra'
    if case['expected'] == 'included':
        opposite = 'needs_review'
    mock = {'summary': 'Review scope', 'items': [{
        'request': case['requests'],
        'classification': opposite,
        'agreement_evidence': '',
        'request_evidence': case['requests'],
        'reasoning': 'Examine contract clauses.',
    }]}
    monkeypatch.setattr(main, 'call_ollama', lambda _: json.dumps(mock))
    resp = TestClient(main.app).post('/api/analyze', json={
        'agreement': case['agreement'], 'requests': case['requests']
    })
    assert resp.status_code == 200, resp.text
    items = resp.json()['items']
    assert items, case['id']
    assert items[0]['classification'] == case['expected'], (case['id'], items)
    if case['expected'] == 'potential_extra':
        assert items[0]['agreement_evidence'] in case['agreement']
        assert items[0]['request_evidence'] in case['requests']
    assert resp.json()['estimated_extra'] == 0
