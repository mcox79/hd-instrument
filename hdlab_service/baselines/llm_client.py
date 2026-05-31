"""LLM client interface + mock implementation for the Tier 2b baseline harness.

This module defines the protocol the comparison harness uses to talk to an
LLM, plus a deterministic mock implementation that lets the harness +
tests run without API credentials.

When real API credentials arrive (separate from Lambda Cloud), drop in
either AnthropicLLMClient or OpenAILLMClient (stubs sketched below; one of
them gets fleshed out once a key is wired). The harness code stays the
same.

Two execution modes per the user-revised Tier 2 plan:

  Substrate-with-tools  : LLM has access to the 6 substrate tools defined
                          in hdlab_service/tool_definitions.py. Maintains
                          a tool-call loop until the LLM emits a final
                          text answer.

  LLM-only              : LLM gets the synthetic corpus pasted into the
                          system prompt and answers from context. No tool
                          calls.

The MockLLMClient is deterministic on the small synthetic corpus so the
harness wiring + comparison-metric math can be validated end-to-end
without spending real API budget.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Protocol, Sequence


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------

@dataclass
class LLMMessage:
    """One turn in the conversation. role: user | assistant | tool_result."""
    role: str
    content: str
    # Optional structured fields used by the tool-use loop.
    tool_use_id: str | None = None
    tool_name: str | None = None
    tool_input: dict | None = None


@dataclass
class ToolUseRequest:
    """Emitted when the LLM wants to call a tool."""
    tool_use_id: str
    tool_name: str
    tool_input: dict


@dataclass
class LLMResponse:
    """Result of one LLM call.

    Either:
      - `text` is non-empty (final answer; stop_reason == "end_turn"), OR
      - `tool_uses` is non-empty (LLM wants to call tools; stop_reason ==
        "tool_use"). The harness dispatches each tool, appends a
        tool_result message, and re-invokes the LLM.
    """
    stop_reason: str  # "end_turn" | "tool_use" | "max_tokens" | "error"
    text: str = ""
    tool_uses: list[ToolUseRequest] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    raw: dict | None = None


class LLMClient(Protocol):
    """Backend-agnostic LLM client used by the comparison harness."""

    name: str

    def call(
        self,
        system_prompt: str,
        messages: Sequence[LLMMessage],
        tools: Sequence[dict] | None = None,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        ...


# ---------------------------------------------------------------------------
# Mock client (deterministic; no API)
# ---------------------------------------------------------------------------

@dataclass
class MockLLMClient:
    """Deterministic LLM stand-in for harness wiring tests.

    Strategy:
      - In tool-use mode (tools is non-empty), looks at the last user
        question and emits a single substrate_retrieve_fact tool_use with
        the key parsed from the question. After the tool_result comes
        back, emits a final text answer from the tool result.
      - In LLM-only mode (tools is None or empty), scans the system_prompt
        for "<key> = <value>" lines and answers from the in-context corpus.
      - In multi-hop questions (questions containing the marker MULTIHOP:
        followed by space-separated keys to chase), iterates calls in
        sequence: one tool_use per hop.

    This is enough to validate the comparison harness wiring + metric
    math. Real LLMs replace it without changing the harness.
    """

    name: str = "mock"
    # Per-conversation hop counter so multi-hop chains advance one tool
    # call per LLM round-trip (mirrors real tool-use loops).
    _hop_state: dict[str, int] = field(default_factory=dict)

    # Tokens-per-character approximation; lets the comparison harness
    # report token consumption without burning real tokens.
    _CHARS_PER_TOKEN = 4

    def call(
        self,
        system_prompt: str,
        messages: Sequence[LLMMessage],
        tools: Sequence[dict] | None = None,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        if not messages:
            return LLMResponse(stop_reason="end_turn", text="(no input)")
        # Find the most recent user question (skip tool_results).
        user_q = ""
        for m in reversed(messages):
            if m.role == "user":
                user_q = m.content
                break
        tokens_in = (len(system_prompt) + sum(len(m.content) for m in messages)) // self._CHARS_PER_TOKEN

        # Tool-use path
        if tools:
            keys = _parse_keys_from_question(user_q)
            hop_key = f"{user_q!r}"
            hop = self._hop_state.get(hop_key, 0)

            # Count prior tool_result messages so we know how many hops
            # have actually completed (the harness appends one
            # tool_result per tool dispatch).
            results_seen = sum(1 for m in messages if m.role == "tool_result")

            if results_seen < len(keys):
                # Issue the next-hop tool call.
                tool_input = {"query": keys[results_seen], "min_confidence": 0.1}
                self._hop_state[hop_key] = hop + 1
                return LLMResponse(
                    stop_reason="tool_use",
                    tool_uses=[ToolUseRequest(
                        tool_use_id=f"toolu_mock_{hop+1}",
                        tool_name="substrate_retrieve_fact",
                        tool_input=tool_input,
                    )],
                    tokens_in=tokens_in,
                    tokens_out=20,
                )

            # All hops done: synthesize a final answer from the
            # accumulated tool results.
            tool_results = [m for m in messages if m.role == "tool_result"]
            final = _synthesize_answer_from_tool_results(tool_results)
            self._hop_state.pop(hop_key, None)
            return LLMResponse(
                stop_reason="end_turn",
                text=final,
                tokens_in=tokens_in,
                tokens_out=len(final) // self._CHARS_PER_TOKEN + 5,
            )

        # LLM-only path: extract from in-context corpus.
        keys = _parse_keys_from_question(user_q)
        if not keys:
            return LLMResponse(stop_reason="end_turn", text="(no key in question)")
        text = _answer_from_context(system_prompt, keys)
        return LLMResponse(
            stop_reason="end_turn",
            text=text,
            tokens_in=tokens_in,
            tokens_out=len(text) // self._CHARS_PER_TOKEN + 5,
        )


# ---------------------------------------------------------------------------
# Parsers + helpers
# ---------------------------------------------------------------------------

_KEY_LIST_RE = re.compile(r"KEYS:\s*([^\n]+)", re.IGNORECASE)


def _parse_keys_from_question(q: str) -> list[str]:
    """Pull the list of corpus keys to look up from a structured question.

    The harness wraps each test question with a `KEYS:` line listing the
    underscore-keyed corpus identifiers, e.g.
        Q: What was edited?
        KEYS: prod_03__name p_05__role

    The mock LLM consumes that line as its retrieval plan.
    """
    m = _KEY_LIST_RE.search(q or "")
    if not m:
        return []
    return [s for s in m.group(1).split() if s.strip()]


def _synthesize_answer_from_tool_results(tool_results: Sequence[LLMMessage]) -> str:
    """Compose a final answer from accumulated tool_result payloads."""
    fragments: list[str] = []
    for r in tool_results:
        body = _extract_fact_text(r.content)
        if body:
            fragments.append(body)
    if not fragments:
        return "no_answer"
    return " | ".join(fragments)


def _extract_fact_text(content: str) -> str:
    """Pull the fact_text field from a JSON-encoded retrieve response."""
    try:
        obj = json.loads(content)
    except json.JSONDecodeError:
        return content.strip()
    txt = obj.get("fact_text")
    if txt is None:
        return obj.get("text", "") or content[:80]
    return str(txt)


def _answer_from_context(system_prompt: str, keys: list[str]) -> str:
    """Scan the system prompt for `<key> = <value>` lines."""
    out: list[str] = []
    for k in keys:
        m = re.search(rf"^\s*{re.escape(k)}\s*=\s*(.+)$", system_prompt, re.MULTILINE)
        if m:
            out.append(m.group(1).strip())
        else:
            out.append("(not_found)")
    return " | ".join(out)


# ---------------------------------------------------------------------------
# Stubs for real backends (filled in once API creds arrive)
# ---------------------------------------------------------------------------

@dataclass
class AnthropicLLMClient:
    """Thin Anthropic wrapper. Stub until ANTHROPIC_API_KEY is wired.

    Implementation note for the next session:
      - Read ANTHROPIC_API_KEY from env
      - Use anthropic.Anthropic() client
      - Map LLMMessage list to Anthropic's messages format
      - Map LLMResponse.tool_uses from the response's `content` blocks
        where block.type == "tool_use"
      - tokens_in / tokens_out come from response.usage.input_tokens /
        output_tokens
    """
    name: str = "anthropic-claude"
    api_key: str | None = None
    model: str = "claude-sonnet-4-5-20250929"

    def call(
        self,
        system_prompt: str,
        messages: Sequence[LLMMessage],
        tools: Sequence[dict] | None = None,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        raise NotImplementedError(
            "AnthropicLLMClient.call is a stub. Wire ANTHROPIC_API_KEY and "
            "implement once Tier 2b credentials arrive."
        )


@dataclass
class OpenAILLMClient:
    """Thin OpenAI wrapper. Stub until OPENAI_API_KEY is wired."""
    name: str = "openai-gpt"
    api_key: str | None = None
    model: str = "gpt-4o"

    def call(
        self,
        system_prompt: str,
        messages: Sequence[LLMMessage],
        tools: Sequence[dict] | None = None,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        raise NotImplementedError(
            "OpenAILLMClient.call is a stub. Wire OPENAI_API_KEY and "
            "implement once Tier 2b credentials arrive."
        )
