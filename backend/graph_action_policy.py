from typing import Any, Mapping
"""Conservative, deterministic next-action policy for an Atlas graph preview.

This is an integration component, NOT a graph query, AI inference, or payment service.
The caller must obtain a trusted preview from FalkorDB and a separately validated
classification. Never treats a saved exception as proof of customer consent.
"""


def choose_next_action(graph_preview: Mapping[str, Any], classification: str, *,
                       verified_evidence: bool = False) -> dict[str, Any]:
    """Return an explainable proposed action; never execute irreversible actions.

    graph_preview: existing Atlas preview response containing state, evidence_path,
    agreement_version, and optionally stale_exceptions/requires_human_review.
    classification: validated model result ('included', 'potential_extra', 'needs_review').
    verified_evidence: both request and agreement evidence have passed backend checks.
    """
    if classification not in {'included', 'potential_extra', 'needs_review'}:
        raise ValueError('Unrecognized classification: fail closed')
    state = str(graph_preview.get('state') or '').lower()
    path = graph_preview.get('evidence_path')
    if not isinstance(path, list):
        path = []
    version = graph_preview.get('agreement_version')
    stale = graph_preview.get('stale_exceptions') or []
    # Keep only an honest path passed back by the real graph service.
    result = {
        'action': 'prepare_clarification_draft',
        'requires_human_review': True,
        'can_create_charge': False,
        'agreement_version': version,
        'graph_state': state or 'unknown',
        'evidence_path': path,
        'reason': 'Insufficient verified context. Ask a human to review the request.',
    }
    if state in {'conflict', 'stale', 'stale_exception', 'agreement_changed'} or stale:
        result['reason'] = 'Conflicting or out-of-date graph history; request fresh human review.'
    elif state in {'applicable_customer_approved_exception', 'applicable_exception', 'matching_exception'}:
        result['action'] = 'verify_existing_exception'
        result['reason'] = 'Matching agreement-bound graph decision found; confirm scope and consent independently.'
    elif state in {'no_applicable_exception', 'no_match', 'new_request'}:
        if classification == 'included':
            result['action'] = 'prepare_in_scope_reply'
            result['reason'] = 'Current request appears included; confirm before responding. No extra charge.'
        elif classification == 'potential_extra' and verified_evidence:
            result['action'] = 'prepare_change_proposal_draft'
            result['reason'] = 'No applicable prior exception; verified potential extra. Freelancer must price and approve the proposal.'
        else:
            result['reason'] = 'No applicable history, but a chargeable change has not been verified.'
    return result
