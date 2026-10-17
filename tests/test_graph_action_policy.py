from backend.graph_action_policy import choose_next_action
import pytest


def test_verified_extra_selects_proposal_draft():
    result = choose_next_action({'state': 'no_applicable_exception', 'evidence_path': [{'via': 'HAS_AGREEMENT'}], 'agreement_version': 1}, 'potential_extra', verified_evidence=True)
    assert result['action'] == 'prepare_change_proposal_draft'
    assert result['can_create_charge'] is False
    assert result['evidence_path'][0]['via'] == 'HAS_AGREEMENT'


def test_matching_exception_requires_verification():
    result = choose_next_action({'state': 'applicable_customer_approved_exception', 'agreement_version': 1}, 'potential_extra', verified_evidence=True)
    assert result['action'] == 'verify_existing_exception'
    assert result['requires_human_review']


def test_stale_history_blocks_proposal():
    result = choose_next_action({'state': 'no_applicable_exception', 'stale_exceptions': [{'agreement_version': 1}], 'agreement_version': 2}, 'potential_extra', verified_evidence=True)
    assert result['action'] == 'prepare_clarification_draft'


def test_conflict_blocks_proposal():
    assert choose_next_action({'state': 'conflict'}, 'potential_extra', verified_evidence=True)['action'] == 'prepare_clarification_draft'


def test_unverified_extra_blocks_proposal():
    assert choose_next_action({'state': 'no_applicable_exception'}, 'potential_extra')['action'] == 'prepare_clarification_draft'


def test_included_never_charged():
    result = choose_next_action({'state': 'no_applicable_exception'}, 'included')
    assert result['action'] == 'prepare_in_scope_reply'
    assert not result['can_create_charge']


def test_unknown_state_fails_closed():
    assert choose_next_action({'state': 'surprise'}, 'potential_extra', verified_evidence=True)['action'] == 'prepare_clarification_draft'


def test_invalid_classification_rejected():
    with pytest.raises(ValueError):
        choose_next_action({}, 'auto_charge')

