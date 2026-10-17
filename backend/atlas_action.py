"""Graph-gated next action for ScopeGuard Atlas.

No irreversible actions. All requests rely on FalkorDB data from the current
agreement; the response is advice rather than authorization to charge.
"""
from __future__ import annotations

from fastapi import APIRouter
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
