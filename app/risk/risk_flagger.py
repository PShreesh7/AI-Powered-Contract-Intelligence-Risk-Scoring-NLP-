"""
Day 4 module: anomaly / high-risk language detection.

Two-layer approach:
1. Rule-based heuristics -- fast, catches obvious red flags (unlimited liability,
   one-sided termination rights, missing caps, unusual notice periods).
2. LLM-based scoring -- sends the clause + its type to an LLM with a structured
   prompt asking for a risk_level and reason. This is where you plug in the
   Anthropic API (or any LLM) once you have API access set up for the team.

Keep the rule layer even after adding the LLM layer -- it's free, deterministic,
and useful as a fallback / sanity check.
"""
from __future__ import annotations
import re
from typing import List
from app.models.schemas import ClauseSegment, RiskFlag

# --- Layer 1: rule-based heuristics -----------------------------------------

RISK_RULES = [
    {
        "pattern": re.compile(r"\bsole discretion\b", re.IGNORECASE),
        "clause_types": {"termination", "payment terms"},
        "risk_level": "medium",
        "reason": "Grants one-sided discretionary power without objective criteria.",
    },
    {
        "pattern": re.compile(r"\bunlimited liability\b|\bwithout limitation\b", re.IGNORECASE),
        "clause_types": {"limitation of liability", "indemnification"},
        "risk_level": "high",
        "reason": "No cap on liability exposure -- unusual and high risk.",
    },
    {
        "pattern": re.compile(r"\bimmediately\b.*\bterminate\b", re.IGNORECASE),
        "clause_types": {"termination"},
        "risk_level": "medium",
        "reason": "Allows termination without a standard notice period.",
    },
    {
        "pattern": re.compile(r"\bperpetual\b|\bindefinite(ly)?\b", re.IGNORECASE),
        "clause_types": {"confidentiality", "non-compete"},
        "risk_level": "medium",
        "reason": "Open-ended duration with no expiry -- may be unenforceable or excessive.",
    },
]


def rule_based_flags(clause: ClauseSegment) -> List[RiskFlag]:
    flags = []
    for rule in RISK_RULES:
        if clause.clause_type in rule["clause_types"] and rule["pattern"].search(clause.text):
            flags.append(
                RiskFlag(
                    clause_id=clause.clause_id,
                    risk_level=rule["risk_level"],
                    reason=rule["reason"],
                )
            )
    return flags


# --- Layer 2: LLM-based scoring (stub -- wire up your API key) -------------

RISK_PROMPT_TEMPLATE = """You are a legal contract risk reviewer.

Clause type: {clause_type}
Clause text: "{clause_text}"

Assess this clause for unusual, one-sided, or high-risk language compared to
standard market practice. Respond ONLY with JSON in this exact shape:
{{"risk_level": "low|medium|high", "reason": "<one sentence>", "suggestion": "<one sentence or null>"}}
"""


def llm_based_flag(clause: ClauseSegment, call_llm_fn=None) -> RiskFlag | None:
    """
    call_llm_fn: a function(prompt: str) -> str that calls your LLM of choice
    (Anthropic API, OpenAI, local model, etc.) and returns raw text.
    Left pluggable so each team member can wire in whichever API key they have.
    """
    if call_llm_fn is None:
        return None  # no LLM configured yet -- rule-based layer still works standalone

    import json
    prompt = RISK_PROMPT_TEMPLATE.format(clause_type=clause.clause_type, clause_text=clause.text)
    raw_response = call_llm_fn(prompt)

    try:
        parsed = json.loads(raw_response)
        return RiskFlag(
            clause_id=clause.clause_id,
            risk_level=parsed["risk_level"],
            reason=parsed["reason"],
            suggestion=parsed.get("suggestion"),
        )
    except (json.JSONDecodeError, KeyError):
        return None


def flag_risks(clauses: List[ClauseSegment], call_llm_fn=None) -> List[RiskFlag]:
    all_flags: List[RiskFlag] = []
    for clause in clauses:
        all_flags.extend(rule_based_flags(clause))
        llm_flag = llm_based_flag(clause, call_llm_fn)
        if llm_flag:
            all_flags.append(llm_flag)
    return all_flags
