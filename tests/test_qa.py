import os
import pytest
from app.qa.contract_qa import (
    QAUnavailableError,
    ask_question,
    build_context,
    build_prompt,
)


def test_build_context():
    clauses = [
        "1. Termination. 30 days notice.",
        "2. Governing Law. Delaware.",
    ]
    context = build_context(clauses)
    assert "1. Termination" in context
    assert "2. Governing Law" in context
    assert "---" in context


def test_build_context_truncation():
    clauses = ["Long clause " * 500 for _ in range(10)]
    context = build_context(clauses)
    assert len(context) <= 13000
    assert "[...document truncated for length...]" in context


def test_build_prompt():
    prompt = build_prompt("Context contract text", "What is the notice period?")
    assert "Context contract text" in prompt
    assert "What is the notice period?" in prompt
    assert "CONTRACT TEXT:" in prompt


def test_ask_question_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(QAUnavailableError) as exc_info:
        ask_question(["Clause text"], "What is the fee?")
    assert "No GOOGLE_API_KEY" in str(exc_info.value)
