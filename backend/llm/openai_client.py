"""
OpenAI gpt-4o-mini client wrapper for the v1 demo.

Cost (Jan 2026 pricing): $0.150 / 1M input tokens, $0.600 / 1M output tokens
Demo budget envelope: ~$30-50/month for typical demo traffic
"""
from __future__ import annotations
import logging
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# gpt-4o-mini per-token pricing (USD)
INPUT_COST_PER_1M = 0.150
OUTPUT_COST_PER_1M = 0.600


@dataclass
class LLMResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    finish_reason: Optional[str] = None


def _client(api_key: Optional[str] = None):
    """Lazy OpenAI client init. Reads OPENAI_API_KEY from env if not passed."""
    if OpenAI is None:
        raise RuntimeError("openai SDK not installed; pip install openai")
    import os
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY not set. Create one at https://platform.openai.com/api-keys "
            "and paste it into .env.local as OPENAI_API_KEY=sk-..."
        )
    return OpenAI(api_key=key)


def chat(
    prompt: str,
    model: str = "gpt-4o-mini",
    system: Optional[str] = None,
    max_tokens: int = 512,
    temperature: float = 0.3,
    api_key: Optional[str] = None,
) -> LLMResponse:
    """Single-turn chat completion. Returns LLMResponse with cost + latency."""
    client = _client(api_key)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    latency_ms = (time.perf_counter() - t0) * 1000

    text = resp.choices[0].message.content or ""
    usage = resp.usage
    cost = (
        (usage.prompt_tokens * INPUT_COST_PER_1M / 1_000_000)
        + (usage.completion_tokens * OUTPUT_COST_PER_1M / 1_000_000)
    )

    return LLMResponse(
        text=text.strip(),
        model=model,
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens,
        cost_usd=cost,
        latency_ms=latency_ms,
        finish_reason=resp.choices[0].finish_reason,
    )


def ask_bare(question: str, system: Optional[str] = None, **kwargs) -> LLMResponse:
    """Ask the LLM directly with no substrate context (the 'bare' panel of the demo)."""
    default_system = (
        "You are a helpful assistant. Answer the user's question directly and concisely. "
        "If you do not know, say 'I don't know' rather than guessing."
    )
    return chat(prompt=question, system=system or default_system, **kwargs)


def ask_with_context(
    question: str,
    context_facts: list[str],
    audit_chain_summary: Optional[str] = None,
    system: Optional[str] = None,
    **kwargs,
) -> LLMResponse:
    """Ask the LLM with substrate-retrieved facts as context (the 'substrate-enhanced' panel)."""
    default_system = (
        "You are a substrate-augmented assistant. The user's question is answered using "
        "facts retrieved by an external substrate memory. Quote facts verbatim when relevant. "
        "If the facts don't cover the question, say so honestly."
    )
    facts_block = "\n".join(f"- {f}" for f in context_facts) if context_facts else "(no facts retrieved)"
    full_prompt = f"""Retrieved facts from substrate:
{facts_block}

{'Audit chain: ' + audit_chain_summary if audit_chain_summary else ''}

User question: {question}

Answer:"""
    return chat(prompt=full_prompt, system=system or default_system, **kwargs)


def health_check(api_key: Optional[str] = None) -> dict:
    """Quick test that the API key + model are reachable. Costs <$0.0001."""
    try:
        resp = chat(
            prompt="Reply with the single word: ok",
            max_tokens=5,
            temperature=0.0,
            api_key=api_key,
        )
        return {
            "ok": True,
            "model": resp.model,
            "response_text": resp.text,
            "cost_usd": resp.cost_usd,
            "latency_ms": resp.latency_ms,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    print(health_check())
