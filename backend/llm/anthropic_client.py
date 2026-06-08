"""
Anthropic Claude Haiku client wrapper for the v1 demo (toggle path).

Cost (Jan 2026 pricing for Haiku 4.5): $1.00 / 1M input, $5.00 / 1M output.
Used as the "different LLM" toggle to show model-agnostic substrate value.
"""
from __future__ import annotations
import logging
import time
from dataclasses import dataclass
from typing import Optional

from backend.llm.openai_client import LLMResponse  # share the dataclass

logger = logging.getLogger(__name__)

try:
    import anthropic
except ImportError:
    anthropic = None


# Haiku 4.5 per-token pricing (USD)
INPUT_COST_PER_1M = 1.00
OUTPUT_COST_PER_1M = 5.00


def _client(api_key: Optional[str] = None):
    if anthropic is None:
        raise RuntimeError("anthropic SDK not installed; pip install anthropic")
    import os
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Create one at https://console.anthropic.com/settings/keys "
            "and paste it into .env.local as ANTHROPIC_API_KEY=sk-ant-..."
        )
    return anthropic.Anthropic(api_key=key)


def chat(
    prompt: str,
    model: str = "claude-haiku-4-5",
    system: Optional[str] = None,
    max_tokens: int = 512,
    temperature: float = 0.3,
    api_key: Optional[str] = None,
) -> LLMResponse:
    """Single-turn chat. Returns LLMResponse with cost + latency."""
    client = _client(api_key)
    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    t0 = time.perf_counter()
    resp = client.messages.create(**kwargs)
    latency_ms = (time.perf_counter() - t0) * 1000

    text = "".join(b.text for b in resp.content if hasattr(b, "text"))
    cost = (
        (resp.usage.input_tokens * INPUT_COST_PER_1M / 1_000_000)
        + (resp.usage.output_tokens * OUTPUT_COST_PER_1M / 1_000_000)
    )

    return LLMResponse(
        text=text.strip(),
        model=model,
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
        cost_usd=cost,
        latency_ms=latency_ms,
        finish_reason=getattr(resp, "stop_reason", None),
    )


def health_check(api_key: Optional[str] = None) -> dict:
    """Quick test that the API key + model are reachable. Costs <$0.001."""
    try:
        resp = chat(
            prompt="Reply with the single word: ok",
            max_tokens=10,
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
