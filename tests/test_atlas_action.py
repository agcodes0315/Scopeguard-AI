"""Deterministic integration tests without Docker or Ollama."""
from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from backend.atlas_action import ActionRequest, next_action


class FakeGraph:
    def __init__(self, state='none', source='graph_agreement_plus_gemma', classification='potential_extra'):
        self.state, self.source, self.classification = state, source, classification
        self.queries = []

    def ro_query(self, query, params=None):
        self.queries.append((query, params))
        if 'RETURN a.id,a.version,a.body' in query:
            return SimpleNamespace(result_set=[['a1', 1, 'Five pages. Extra pages require approval.']])
        if 'RETURN a.id,a.version,e.id' in query:
            if self.state == 'exception':
                return SimpleNamespace(result_set=[['a1', 1, 'e1', 'Add Testimonials page', None, 'included', 'Waived once', True, 'confirmed_by_reviewer']])
            if self.state == 'stale':
                return SimpleNamespace(result_set=[['old', 0, 'e1', 'Add Testimonials page', None, 'included', 'Older waiver', True, 'confirmed_by_reviewer']])
            return SimpleNamespace(result_set=[])
        if 'RETURN a.id, a.body, a.version' in query:
            return SimpleNamespace(result_set=[['a1', 'Five pages. Extra pages require approval.', 1]])
        if 'RETURN c.id,c.text' in query:
            return SimpleNamespace(result_set=[['c1', 'Extra pages require approval.']])
        if 'RETURN r.id,r.text,d.classification' in query:
            if self.source == 'graph_memory':
                return SimpleNamespace(result_set=[['r-old', 'Add Testimonials page', self.classification, 'Previously reviewed', 'confirmed']])
            return SimpleNamespace(result_set=[])
        raise AssertionError('Unexpected query '+query)

    def query(self, query, params=None):
        self.queries.append((query, params))
        return SimpleNamespace(result_set=[])


def analyzer(agreement, request):
    return SimpleNamespace(items=[SimpleNamespace(
        classification='potential_extra', reasoning='New page outside scope',
        agreement_evidence='Extra pages require approval.',
        request_evidence='Add Testimonials page')])


def test_verified_new_extra_selects_proposal_draft():
    output = next_action(ActionRequest(project_id='p1', request_text='Add Testimonials page'),
                         graph=FakeGraph(), analyzer=analyzer)
    assert output['action'] == 'prepare_change_proposal_draft'
    assert output['verified_evidence'] is True
    assert output['can_create_charge'] is False
    assert output['billing_authorized'] is False


def test_matching_customer_exception_requires_verification():
    output = next_action(ActionRequest(project_id='p1', request_text='Add Testimonials page'),
                         graph=FakeGraph(state='exception'), analyzer=analyzer)
    assert output['action'] == 'verify_existing_exception'
    assert not output['customer_consent_verified']


def test_stale_exception_requires_clarification():
    output = next_action(ActionRequest(project_id='p1', request_text='Add Testimonials page'),
                         graph=FakeGraph(state='stale'), analyzer=analyzer)
    assert output['action'] == 'prepare_clarification_draft'


def test_old_graph_memory_keeps_review_not_consent():
    output = next_action(ActionRequest(project_id='p1', request_text='Add Testimonials page'),
                         graph=FakeGraph(source='graph_memory'), analyzer=analyzer)
    assert output['action'] == 'verify_existing_exception'
    assert output['analysis_source'] == 'graph_memory'


def test_graph_unavailable_fails_closed():
    class DownGraph:
        def ro_query(self, *args, **kwargs):
            raise HTTPException(503, 'FalkorDB unavailable')
    with pytest.raises(HTTPException) as exc:
        next_action(ActionRequest(project_id='p1', request_text='Add Testimonials page'),
                    graph=DownGraph(), analyzer=analyzer)
    assert exc.value.status_code == 503
