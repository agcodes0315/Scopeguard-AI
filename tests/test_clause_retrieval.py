from backend.main import _agreement_clause, _known_included
from test_billing_safety import AGREEMENT, REQUESTS

def test_specific_included_clauses_not_generic_website():
    for label, fragment in [("Correct phone number on Contact page", "contact information updates"), ("Change background color of Services page", "color changes"), ("Update heading text on Home page", "Text corrections")]:
        assert _known_included(label, AGREEMENT, REQUESTS)
        assert fragment.lower() in _agreement_clause(label, AGREEMENT).lower()

def test_included_requires_explicit_revision_round():
    label = "Correct phone number on Contact page"
    assert not _known_included(label, AGREEMENT, "Please correct the phone number, this is revision round 3.")
