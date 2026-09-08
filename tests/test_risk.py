from app.models.schemas import ClauseSegment
from app.risk.risk_flagger import flag_risks, rule_based_flags


def _make_clause(clause_id: str, text: str, clause_type: str) -> ClauseSegment:
    return ClauseSegment(
        clause_id=clause_id,
        text=text,
        clause_type=clause_type,
        confidence=0.95,
        start_char=0,
        end_char=len(text),
    )


def test_sole_discretion_risk():
    clause = _make_clause(
        "c1",
        "Company may terminate this agreement at its sole discretion.",
        "termination",
    )
    flags = rule_based_flags(clause)
    assert len(flags) == 1
    assert flags[0].risk_level == "medium"
    assert "discretionary power" in flags[0].reason
    assert flags[0].suggestion is not None
    assert "mutual written consent" in flags[0].suggestion


def test_unlimited_liability_risk():
    clause = _make_clause(
        "c2",
        "Vendor shall have unlimited liability for any direct or indirect damages.",
        "limitation of liability",
    )
    flags = rule_based_flags(clause)
    assert len(flags) == 1
    assert flags[0].risk_level == "high"
    assert "No clear cap" in flags[0].reason
    assert flags[0].suggestion is not None
    assert "liability cap" in flags[0].suggestion


def test_immediate_termination_risk():
    clause = _make_clause(
        "c3",
        "Either party may immediately terminate this agreement upon notice.",
        "termination",
    )
    flags = rule_based_flags(clause)
    assert len(flags) == 1
    assert flags[0].risk_level == "medium"
    assert "standard notice" in flags[0].reason
    assert flags[0].suggestion is not None


def test_perpetual_obligations_risk():
    clause = _make_clause(
        "c4",
        "Recipient shall keep all confidential information confidential in perpetual duration.",
        "confidentiality",
    )
    flags = rule_based_flags(clause)
    assert len(flags) == 1
    assert flags[0].risk_level == "medium"
    assert "Open-ended duration" in flags[0].reason
    assert flags[0].suggestion is not None


def test_auto_renewal_risk():
    clause = _make_clause(
        "c5",
        "This Agreement shall automatically renew for additional one-year periods.",
        "termination",
    )
    flags = rule_based_flags(clause)
    assert len(flags) == 1
    assert flags[0].risk_level == "medium"
    assert "Automatic renewal" in flags[0].reason
    assert "30 to 60 days" in flags[0].suggestion


def test_broad_indemnification_risk():
    clause = _make_clause(
        "c6",
        "Contractor agrees to indemnify and hold harmless the Company from any claims.",
        "indemnification",
    )
    flags = rule_based_flags(clause)
    assert len(flags) >= 1
    high_flags = [f for f in flags if f.risk_level == "high"]
    assert len(high_flags) >= 1
    assert any("indemnity" in f.reason.lower() for f in high_flags)


def test_non_compete_risk():
    clause = _make_clause(
        "c7",
        "Employee agrees to a strict non-compete clause for 5 years worldwide.",
        "non-compete",
    )
    flags = rule_based_flags(clause)
    assert len(flags) == 1
    assert flags[0].risk_level == "high"
    assert "Restrictive covenant" in flags[0].reason


def test_flag_risks_multiple():
    clauses = [
        _make_clause("c1", "Normal governing law clause.", "governing law"),
        _make_clause("c2", "Terminated at sole discretion.", "termination"),
    ]
    flags = flag_risks(clauses)
    assert len(flags) == 1
    assert flags[0].clause_id == "c2"
