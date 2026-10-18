"""Graph-gated next action for ScopeGuard Atlas.

No irreversible actions. All requests rely on FalkorDB data from the current
agreement; the response is advice rather than authorization to charge.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
import secrets
from pydantic import BaseModel, Field

from backend.atlas import PreviewRequest, preview
from backend.graph_action_policy import choose_next_action
from backend.graph_context import GraphAnalyze, analyze_project, get_graph

router = APIRouter(prefix='/api/atlas', tags=['Graph-informed next action'])


class ActionRequest(BaseModel):
    project_id: str = Field(min_length=1)
    request_text: str = Field(min_length=5, max_length=15000)


def next_action(payload: ActionRequest, graph=None, analyzer=None):
    """Read graph history, analyze with graph-selected agreement, choose next step.

    analyzer injection is for deterministic tests. Actual requests use the
    configured Gemma analyzer in graph_context.analyze_project.
    """
    graph = graph if graph is not None else get_graph()
    p = preview(PreviewRequest(project_id=payload.project_id,
                               request_text=payload.request_text), graph=graph)
    # Graph-guided analysis records a pending decision; never confirms it.
    analysis = analyze_project(GraphAnalyze(project_id=payload.project_id,
                                             request=payload.request_text),
                               graph=graph, analyzer=analyzer)
    state = p['state']
    verified = bool(analysis.get('verified_evidence', False))
    classification = analysis['classification']
    # The older graph workflow stores confirmed Request->Decision relations,
    # whereas Atlas records agreement-bound Exception entities. Treat either
    # as decision memory; do not assume customer consent.
    if analysis['source'] == 'graph_memory' and state == 'no_applicable_exception':
        state = 'matching_prior_graph_decision'
    # Contradictory memory sources must not silently select an action.
    if (p['state'] == 'applicable_customer_approved_exception' and
            analysis['source'] == 'graph_memory' and
            classification != p['recommendation']):
        state = 'conflict'
    graph_input = {**p, 'state': state}
    action = choose_next_action(graph_input, classification,
                                verified_evidence=verified)
    if state == 'matching_prior_graph_decision':
        action['action'] = 'verify_existing_exception'
        action['reason'] = ('A reviewed decision was retrieved from a matching '
                            'request under the active agreement. Verify conditions '
                            'and actual client consent independently.')
    # Provide the actual read/query traversal, never fake a graph connection.
    return {
        **action,
        'project_id': payload.project_id,
        'request_id': analysis['request_id'],
        'agreement_id': analysis['agreement_id'],
        'classification': classification,
        'analysis_source': analysis['source'],
        'graph_state': state,
        'verified_evidence': verified,
        'evidence_path': p.get('evidence_path', []) + analysis.get('evidence_path', []),
        'billing_authorized': False,
        'customer_consent_verified': False,
        'agent_executed_external_action': False,
    }


@router.post('/next-action')
def next_action_route(payload: ActionRequest):
    return next_action(payload)


class ExecuteDraftRequest(ActionRequest):
    # Only internal reversible drafting.
    client_label: str = Field(default='Client', max_length=120)


def create_safe_draft(payload: ExecuteDraftRequest, graph=None, analyzer=None):
    graph = graph if graph is not None else get_graph()
    decision = next_action(ActionRequest(project_id=payload.project_id,
                                         request_text=payload.request_text),
                           graph=graph, analyzer=analyzer)
    action = decision['action']
    if action not in {'prepare_change_proposal_draft', 'prepare_clarification_draft',
                      'verify_existing_exception', 'prepare_in_scope_reply'}:
        raise HTTPException(422, 'Unsupported action; no draft created.')
    templates = {
        'prepare_change_proposal_draft': (
            'Proposed scope change',
            'Your request may be outside the agreed scope. I can prepare a separate estimate after confirming the deliverables, timeline, hours and rate. This draft is not a charge or approval.'),
        'prepare_clarification_draft': (
            'Clarification needed before proceeding',
            'Before proceeding, could we clarify the requested deliverables and check them against the current agreement? No additional work or charges are approved.'),
        'verify_existing_exception': (
            'Please verify the earlier exception',
            'A matching prior decision was retrieved for the active agreement. Please verify its exact terms and independently confirm customer consent before relying on it.'),
        'prepare_in_scope_reply': (
            'Review of requested work',
            'The request appears to be within the existing agreement, subject to human review. This draft does not approve additional charges.'),
    }
    subject, paragraph = templates[action]
    # The request is untrusted source text, not an instruction to the executor.
    safe_request = ' '.join(payload.request_text.split())[:350]
    body = (f'Hello {payload.client_label},\n\nRegarding your request: '
            f'{safe_request}\n\n{paragraph}\n\nBest regards')
    # The artifact is attached to the actual graph request, not a local-only mock.
    draft_id = secrets.token_hex(12)
    graph.query('''MATCH (p:Project {id:$pid})-[:RECEIVED]->(r:Request {id:$rid})
        -[:BASED_ON]->(a:Agreement {id:$aid})
        CREATE (d:ActionDraft {id:$did, action:$action, subject:$subject,
          body:$body, status:'draft_only', agreement_version:$ver})
        CREATE (r)-[:GENERATED_DRAFT]->(d)
        CREATE (d)-[:BASED_ON_AGREEMENT]->(a)''', {
        'pid': payload.project_id, 'rid': decision['request_id'],
        'aid': decision['agreement_id'], 'did': draft_id, 'action': action,
        'subject': subject, 'body': body, 'ver': decision['agreement_version']})
    return {**decision, 'draft_id': draft_id, 'draft': {'subject': subject, 'body': body,
        'editable': True, 'status': 'draft_only'}, 'agent_executed_internal_action': True,
        'agent_executed_external_action': False, 'sent': False, 'payment_created': False,
        'approval_created': False}


@router.post('/execute-safe-action')
def execute_safe_action_route(payload: ExecuteDraftRequest):
    return create_safe_draft(payload)
