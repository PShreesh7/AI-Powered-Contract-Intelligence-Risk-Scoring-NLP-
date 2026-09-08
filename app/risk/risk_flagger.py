from __future__ import annotations

import re

from typing import List

from app.models.schemas import (
    ClauseSegment,
    RiskFlag,
)


RISK_RULES = [
    {
        "pattern": re.compile(
            r"\bsole discretion\b",
            re.IGNORECASE,
        ),
        "clause_types": {
            "termination",
            "termination for convenience",
            "payment terms",
        },
        "risk_level": "medium",
        "reason": "Grants one-sided discretionary power.",
        "suggestion": "Require mutual written consent or specify objective, defined criteria instead of unilateral discretion.",
    },
    {
        "pattern": re.compile(
            r"\bunlimited liability\b|\bwithout limitation\b|\bno limitation of liability\b",
            re.IGNORECASE,
        ),
        "clause_types": {
            "limitation of liability",
            "cap on liability",
            "uncapped liability",
            "indemnification",
        },
        "risk_level": "high",
        "reason": "No clear cap on liability exposure.",
        "suggestion": "Negotiate an aggregate liability cap (e.g., total fees paid in preceding 12 months) and express consequential damages exclusion.",
    },
    {
        "pattern": re.compile(
            r"\bimmediately\b.*\bterminate\b|\bterminate\b.*\bimmediately\b",
            re.IGNORECASE,
        ),
        "clause_types": {
            "termination",
            "termination for convenience",
        },
        "risk_level": "medium",
        "reason": "Termination may occur without standard notice.",
        "suggestion": "Add a standard advance notice requirement (e.g., 30 days) and a cure period for remediable breaches.",
    },
    {
        "pattern": re.compile(
            r"\bperpetual\b|\bindefinite(ly)?\b",
            re.IGNORECASE,
        ),
        "clause_types": {
            "confidentiality",
            "non-compete",
        },
        "risk_level": "medium",
        "reason": "Open-ended duration may create ongoing legal risk.",
        "suggestion": "Limit the duration of obligations to a definite time frame (e.g., 2 to 5 years following termination).",
    },
    {
        "pattern": re.compile(
            r"\bautomatic(ally)?\s+(renew(al|s)?|extend(ed|s)?)\b",
            re.IGNORECASE,
        ),
        "clause_types": {
            "termination",
            "termination for convenience",
            "payment terms",
        },
        "risk_level": "medium",
        "reason": "Automatic renewal clause may cause unintended contract rollover.",
        "suggestion": "Require written notice at least 30 to 60 days prior to the expiration date to prevent automatic renewal.",
    },
    {
        "pattern": re.compile(
            r"\bindemnif(y|ies|ication)\b.*\b(hold\s+harmless|defend)\b",
            re.IGNORECASE,
        ),
        "clause_types": {
            "indemnification",
        },
        "risk_level": "high",
        "reason": "Broad indemnity obligation creates high financial exposure.",
        "suggestion": "Exclude indirect/consequential damages, cap indemnity obligation, and limit scope to direct third-party claims.",
    },
    {
        "pattern": re.compile(
            r"\bnon-compete\b|\bshall not compete\b|\bnon-solicitation\b",
            re.IGNORECASE,
        ),
        "clause_types": {
            "non-compete",
        },
        "risk_level": "high",
        "reason": "Restrictive covenant may unduly limit future business or employment opportunities.",
        "suggestion": "Ensure restrictive covenants are narrowly tailored in duration, industry scope, and geographic reach.",
    },
]


def rule_based_flags(
    clause: ClauseSegment,
) -> List[RiskFlag]:

    flags = []

    for rule in RISK_RULES:

        if (
            clause.clause_type in rule["clause_types"]
            and rule["pattern"].search(clause.text)
        ):

            flags.append(
                RiskFlag(
                    clause_id=clause.clause_id,
                    risk_level=rule["risk_level"],
                    reason=rule["reason"],
                    suggestion=rule.get("suggestion"),
                )
            )

    return flags


def flag_risks(
    clauses,
):

    all_flags = []

    for clause in clauses:

        all_flags.extend(
            rule_based_flags(
                clause
            )
        )

    return all_flags