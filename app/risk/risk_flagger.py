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
            (
                "termination "
                "for convenience"
            ),
            "payment terms",
        },
        "risk_level": (
            "medium"
        ),
        "reason": (
            "Grants one-sided "
            "discretionary power."
        ),
    },
    {
        "pattern": re.compile(
            (
                r"\bunlimited liability\b"
                r"|\bwithout limitation\b"
            ),
            re.IGNORECASE,
        ),
        "clause_types": {
            (
                "limitation "
                "of liability"
            ),
            "cap on liability",
            "uncapped liability",
            "indemnification",
        },
        "risk_level": (
            "high"
        ),
        "reason": (
            "No clear cap on "
            "liability exposure."
        ),
    },
    {
        "pattern": re.compile(
            (
                r"\bimmediately\b"
                r".*\bterminate\b"
            ),
            re.IGNORECASE,
        ),
        "clause_types": {
            "termination",
            (
                "termination "
                "for convenience"
            ),
        },
        "risk_level": (
            "medium"
        ),
        "reason": (
            "Termination may occur "
            "without standard notice."
        ),
    },
    {
        "pattern": re.compile(
            (
                r"\bperpetual\b"
                r"|\bindefinite(ly)?\b"
            ),
            re.IGNORECASE,
        ),
        "clause_types": {
            "confidentiality",
            "non-compete",
        },
        "risk_level": (
            "medium"
        ),
        "reason": (
            "Open-ended duration "
            "may create legal risk."
        ),
    },
]


def rule_based_flags(
    clause: ClauseSegment,
) -> List[RiskFlag]:

    flags = []

    for rule in RISK_RULES:

        if (
            clause.clause_type
            in rule[
                "clause_types"
            ]
            and rule[
                "pattern"
            ].search(
                clause.text
            )
        ):

            flags.append(
                RiskFlag(
                    clause_id=(
                        clause.clause_id
                    ),
                    risk_level=(
                        rule[
                            "risk_level"
                        ]
                    ),
                    reason=(
                        rule[
                            "reason"
                        ]
                    ),
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