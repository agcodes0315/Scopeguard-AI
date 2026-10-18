from types import SimpleNamespace
from unittest.mock import patch
import pytest
from backend.atlas_action import ExecuteDraftRequest, create_safe_draft
from backend.atlas import AgreementVersionRequest, new_agreement_version


class FakeGraph:
    def __init__(self): self.writes = []
    def query(self, query, params=None): self.writes.append((query,params))
    def ro_query(self, query, params=None):
        return SimpleNamespace(result_set=[['agreement-1',1,'The site includes five pages. Additional pages require pricing.']])


@pytest.mark.parametrize('state,classification,verified,expected', [
    ('no_applicable_exception','potential_extra',True,'prepare_change_proposal_draft'),
    ('no_applicable_exception','needs_review',False,'prepare_clarification_draft'),
    ('applicable_customer_approved_exception','included',False,'verify_existing_exception'),
    ('stale_exception','potential_extra',True,'prepare_clarification_draft'),
])
def test_internal_execution_is_graph_linked_and_never_sends(state,classification,verified,expected):
    graph=FakeGraph()
    prev={'state':state,'recommendation':'included','agreement_id':'agreement-1','agreement_version':1,
          'evidence_path':[{'node':'Project','id':'p'},{'node':'Agreement','id':'agreement-1'}],
          'stale_exceptions': [{'exception_id':'old'}] if state=='stale_exception' else []}
    analysis={'request_id':'req-1','agreement_id':'agreement-1','classification':classification,
              'source':'graph_agreement_plus_gemma','verified_evidence':verified,'evidence_path':[]}
    with patch('backend.atlas_action.preview',return_value=prev), patch('backend.atlas_action.analyze_project',return_value=analysis):
        result=create_safe_draft(ExecuteDraftRequest(project_id='p',request_text='Please add a Testimonials page.'),graph=graph)
    assert result['action']==expected
    assert result['agent_executed_internal_action'] is True
    assert result['sent'] is False and result['payment_created'] is False
    assert result['can_create_charge'] is False
    assert result['draft']['editable'] is True
    assert len(graph.writes)==1
    cypher,values=graph.writes[0]
    assert 'GENERATED_DRAFT' in cypher and 'BASED_ON_AGREEMENT' in cypher
    assert values['aid']=='agreement-1' and values['rid']=='req-1'


def test_version_update_retains_older_exception():
    graph=FakeGraph()
    result=new_agreement_version(AgreementVersionRequest(project_id='p',agreement='New agreement: extra pages must be quoted and signed.'),graph=graph)
    assert result['agreement_version']==2
    assert result['old_exceptions_auto_reused'] is False
    assert len(graph.writes)>1
    assert 'HAS_AGREEMENT' in graph.writes[0][0]
    assert 'HAS_EXCEPTION' not in graph.writes[0][0]
