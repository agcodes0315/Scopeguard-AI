"""Regression tests from the 21/24 local Gemma benchmark.
Mocks model output to test backend guardrails (not the live model's quality).
"""
import json
from fastapi.testclient import TestClient
from backend import main, workflow

AGREEMENT = (
    "The website consists of Home, About, Services, Portfolio and Contact pages. "
    "Two revision rounds are included. Text corrections, color changes and contact "
    "information updates during included rounds are covered. Additional pages and "
    "any third revision require separate approval and pricing."
)
def _evaluate(monkeypatch, tmp_path, user_request, items):
    monkeypatch.setattr(workflow, 'DB', tmp_path / 'classification.db')
    monkeypatch.setattr(main, 'call_ollama', lambda _: json.dumps({'summary': 'Test', 'items': items}))
    res = TestClient(main.app).post('/api/analyze', json={'agreement': AGREEMENT, 'requests': user_request})
    assert res.status_code == 200, res.text
    return res.json()


def test_portfolio_description_second_revision(monkeypatch, tmp_path):
    request = 'Please change the Portfolio description text in the second revision.'
    output = _evaluate(monkeypatch, tmp_path, request, [{
        'request': 'Change Portfolio description text', 'classification': 'needs_review',
        'request_evidence': request, 'agreement_evidence': '', 'reasoning': 'Unclear'
    }])
    assert [i['classification'] for i in output['items']] == ['included']
    assert 'Text corrections' in output['items'][0]['agreement_evidence']


def test_tentative_revision_does_not_become_extra(monkeypatch, tmp_path):
    request = 'We may need more revisions later.'
    output = _evaluate(monkeypatch, tmp_path, request, [{
        'request': 'More revisions', 'classification': 'potential_extra',
        'request_evidence': request, 'agreement_evidence': 'Two revision rounds are included.',
        'reasoning': 'Additional revision'
    }, {
        'request': 'Later revisions', 'classification': 'needs_review',
        'request_evidence': request, 'agreement_evidence': '', 'reasoning': 'Uncertain'
    }])
    assert [i['classification'] for i in output['items']] == ['needs_review']
    assert output['estimated_extra'] == 0


def test_exploratory_page_question_does_not_become_extra(monkeypatch, tmp_path):
    request = 'Would a Careers page be a good idea?'
    output = _evaluate(monkeypatch, tmp_path, request, [{
        'request': 'Add Careers page', 'classification': 'potential_extra',
        'request_evidence': request, 'agreement_evidence': 'Additional pages and any third revision require separate approval and pricing.',
        'reasoning': 'Potential new page'
    }])
    assert [i['classification'] for i in output['items']] == ['needs_review']
