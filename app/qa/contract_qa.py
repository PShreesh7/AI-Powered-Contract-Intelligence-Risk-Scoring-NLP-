"""
Week 3 module: chat-with-contract.
Takes a plain-language question plus the contract's clause text, sends it to
an LLM, and returns a direct answer grounded in the actual document.

Uses Google Gemini (has a free tier, no credit card needed to start).

Setup:
1. Get a free API key at https://aistudio.google.com/app/apikey
2. pip install google-generativeai --break-system-packages   (Windows: just pip install google-generativeai)
3. Set your API key as an environment variable, don't hardcode it:
   Windows (PowerShell):  $env:GOOGLE_API_KEY="your-key-here"
   Mac/Linux:              export GOOGLE_API_KEY="your-key-here"
"""
from __future__ import annotations
import os
from typing import List

MAX_CONTEXT_CHARS = 12000  # keep prompts small -- most contracts easily fit


def build_context(clause_texts: List[str]) -> str:
    """Join clause texts into one context block, trimmed to a safe length."""
    joined = "\n\n---\n\n".join(clause_texts)
    if len(joined) > MAX_CONTEXT_CHARS:
        joined = joined[:MAX_CONTEXT_CHARS] + "\n\n[...document truncated for length...]"
    return joined


def build_prompt(context: str, question: str) -> str:
    return f"""You are a legal assistant helping someone understand a contract.
Answer the question using ONLY the contract text below. If the answer isn't
in the text, say so clearly instead of guessing.

CONTRACT TEXT:
{context}

QUESTION: {question}

Answer in 2-4 plain-language sentences. Quote the relevant clause briefly if useful."""


class QAUnavailableError(Exception):
    """Raised when no API key is configured -- lets the API return a clear error."""


def ask_question(clause_texts: List[str], question: str) -> str:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise QAUnavailableError(
            "No GOOGLE_API_KEY environment variable found. "
            "Get a free key at https://aistudio.google.com/app/apikey and set it "
            "to enable the contract Q&A feature."
        )

    try:
        import google.generativeai as genai
    except ImportError as e:
        raise QAUnavailableError(
            "The 'google-generativeai' package isn't installed. Run: "
            "pip install google-generativeai"
        ) from e

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")  # fast + free-tier friendly

    context = build_context(clause_texts)
    prompt = build_prompt(context, question)

    response = model.generate_content(prompt)
    return response.text.strip()


if __name__ == "__main__":
    sample_clauses = [
        "Either party may terminate this Agreement upon 30 days written notice.",
        "This Agreement shall be governed by the laws of Delaware.",
    ]
    print(ask_question(sample_clauses, "What's the notice period to terminate?"))