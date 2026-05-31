"""Comparison harness: substrate-with-tools vs LLM-only.

Drives the Tier 2b comparison per the user-revised plan
(notes/session_kickoff_testbed_v1.md Tier 2):

  Substrate-with-tools  : LLM has access to the 6 substrate tools; the
                          harness maintains the tool-call loop until the
                          LLM emits a final text answer.

  LLM-only              : LLM gets the synthetic corpus pasted into the
                          system prompt and answers from context. No
                          tools.

Both conditions get the SAME question set (hdlab_service/baselines/
questions.py) and the SAME synthetic corpus. The harness reports per-
condition + per-question metrics:

  - exact_match: did the answer text match the ground-truth expected_answer?
  - partial_match: did the expected_answer string appear in the response?
  - tokens_in / tokens_out / total_tokens
  - n_tool_calls (substrate-with-tools only)
  - latency_ms

Aggregate metrics: accuracy %, mean tokens, mean latency per condition.

The harness is LLM-client agnostic. Pass any client satisfying the
LLMClient protocol (real or mock). Tests use MockLLMClient so the wiring
+ metric math run without API credentials.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Sequence

from fastapi.testclient import TestClient

from hdlab_service.baselines.llm_client import (
    LLMClient,
    LLMMessage,
    LLMResponse,
)
from hdlab_service.baselines.questions import TestQuestion
from hdlab_service.corpora.synthetic_corpus import (
    Corpus,
    corpus_as_context_string,
)


_SYSTEM_PROMPT_SUBSTRATE = (
    "You answer questions by calling substrate tools. The substrate stores "
    "facts as (key, value) pairs; the user will tell you which keys to look "
    "up via a 'KEYS:' line. Call substrate_retrieve_fact once per key, then "
    "compose a final answer. If a tool returns no_match, report it as "
    "'(not_found)'.\n\n"
    "OUTPUT FORMAT (strict): Respond with ONLY the value(s). If one key, "
    "respond with only that value. If multiple keys, join values with "
    "exactly ' | ' (space-pipe-space). No preamble, no labels, no markdown, "
    "no bolding, no quotation marks, no key names, no explanatory text. "
    "Example: a question with KEYS p_00, p_01 where the values are 'Quinn' "
    "and 'engineer' must produce exactly:\n"
    "Quinn | engineer\n"
    "Not 'The values are: Quinn | engineer' or '**Quinn** | **engineer**' "
    "or 'p_00=Quinn | p_01=engineer'."
)

_SYSTEM_PROMPT_LLM_ONLY = (
    "You answer questions strictly from the fact corpus provided below. The "
    "user will give a question with a 'KEYS:' line indicating which keys to "
    "look up.\n\n"
    "OUTPUT FORMAT (strict): Respond with ONLY the value(s). If one key, "
    "respond with only that value. If multiple keys, join values with "
    "exactly ' | ' (space-pipe-space). No preamble, no labels, no markdown, "
    "no bolding, no quotation marks, no key names, no explanatory text. "
    "If a key is absent, return '(not_found)' verbatim. Do not fabricate. "
    "Example: a question with KEYS p_00, p_01 where the corpus contains "
    "'p_00__name = Quinn' and 'p_01__role = engineer' must produce exactly:\n"
    "Quinn | engineer\n"
    "Not 'p_00__name = Quinn | p_01__role = engineer' (do not echo the key "
    "or the assignment syntax).\n\n"
    "{corpus_dump}"
)


@dataclass
class QuestionResult:
    """One question's outcome under one condition."""
    qid: str
    category: str
    condition: str
    answer: str
    expected: str
    exact_match: bool
    partial_match: bool
    tokens_in: int
    tokens_out: int
    latency_ms: float
    n_tool_calls: int = 0
    error: str | None = None


@dataclass
class ConditionAggregate:
    """Aggregate metrics for one condition across the full question set."""
    condition: str
    n_total: int
    n_exact: int
    n_partial: int
    accuracy_exact: float       # n_exact / n_total
    accuracy_partial: float     # n_partial / n_total
    mean_tokens_in: float
    mean_tokens_out: float
    mean_total_tokens: float
    mean_latency_ms: float
    mean_tool_calls: float
    per_category_accuracy: dict[str, float] = field(default_factory=dict)


@dataclass
class HarnessReport:
    """Top-level result: per-question rows + per-condition aggregates."""
    n_questions: int
    n_conditions: int
    rows: list[QuestionResult] = field(default_factory=list)
    aggregates: list[ConditionAggregate] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_comparison(
    client: TestClient,
    corpus: Corpus,
    questions: Sequence[TestQuestion],
    llm: LLMClient,
    conditions: Sequence[str] = ("substrate_with_tools", "llm_only"),
    tools: Sequence[dict] | None = None,
    max_tool_loop_iters: int = 6,
    key_to_atom: dict[str, str] | None = None,
) -> HarnessReport:
    """Run the full question set across the requested conditions.

    Args:
        client: FastAPI TestClient bound to the substrate service. Each
            condition gets a fresh substrate state (caller seeds the corpus
            via _store_corpus before invoking this function, OR the
            convenience wrapper run_comparison_full_setup handles that).
        corpus: synthetic corpus for the LLM-only context dump.
        questions: TestQuestion sequence.
        llm: LLM client (real or mock).
        conditions: which conditions to run (intersection with
            {"substrate_with_tools", "llm_only"}).
        tools: tool definitions to pass to the LLM in the substrate
            condition. Defaults to the full SUBSTRATE_TOOLS_ANTHROPIC list.
        max_tool_loop_iters: safety cap; mock LLM uses 1-3 in practice,
            real LLMs may try more.

    Returns:
        HarnessReport with per-row results + per-condition aggregates.
    """
    if tools is None:
        from hdlab_service.tool_definitions import SUBSTRATE_TOOLS_ANTHROPIC
        tools = SUBSTRATE_TOOLS_ANTHROPIC

    rows: list[QuestionResult] = []
    for q in questions:
        # Optional pre-question setup (edits, etc.). Applied to BOTH the
        # substrate state AND the in-memory corpus so the two conditions
        # see the same post-edit state.
        if q.requires_edit_setup:
            _apply_edit_setup(client, q.requires_edit_setup, corpus, key_to_atom)

        for cond in conditions:
            if cond == "substrate_with_tools":
                r = _run_substrate_with_tools(
                    client, q, llm, tools, max_tool_loop_iters
                )
            elif cond == "llm_only":
                r = _run_llm_only(client, q, corpus, llm)
            else:
                r = QuestionResult(
                    qid=q.qid, category=q.category, condition=cond,
                    answer="", expected=q.expected_answer,
                    exact_match=False, partial_match=False,
                    tokens_in=0, tokens_out=0, latency_ms=0.0,
                    error=f"unknown condition {cond!r}",
                )
            rows.append(r)

    aggregates = _aggregate(rows, conditions)
    return HarnessReport(
        n_questions=len(questions),
        n_conditions=len(conditions),
        rows=rows,
        aggregates=aggregates,
    )


# Convenience: stores the corpus then runs comparison.
def run_comparison_full_setup(
    client: TestClient,
    corpus: Corpus,
    questions: Sequence[TestQuestion],
    llm: LLMClient,
    **kwargs,
) -> tuple[HarnessReport, dict[str, str]]:
    """Store the corpus then run the comparison.

    Returns (report, key_to_atom_id_map) so the caller can inspect or
    apply additional edits between runs. Threads the key_to_atom mapping
    into run_comparison so per-question edit setups can actually apply.
    """
    key_to_atom = _store_corpus(client, corpus)
    report = run_comparison(client, corpus, questions, llm,
                            key_to_atom=key_to_atom, **kwargs)
    return report, key_to_atom


# ---------------------------------------------------------------------------
# Per-condition runners
# ---------------------------------------------------------------------------

def _run_substrate_with_tools(
    client: TestClient,
    q: TestQuestion,
    llm: LLMClient,
    tools: Sequence[dict],
    max_iters: int,
) -> QuestionResult:
    """Tool-use loop: LLM emits tool_use -> harness dispatches -> repeat."""
    messages: list[LLMMessage] = [LLMMessage(role="user", content=q.test_question)]
    tokens_in_total = 0
    tokens_out_total = 0
    n_tool_calls = 0
    t0 = time.perf_counter()
    final_text = ""
    error: str | None = None

    for _ in range(max_iters):
        resp: LLMResponse = llm.call(
            system_prompt=_SYSTEM_PROMPT_SUBSTRATE,
            messages=messages,
            tools=tools,
        )
        tokens_in_total += resp.tokens_in
        tokens_out_total += resp.tokens_out
        if resp.stop_reason == "tool_use" and resp.tool_uses:
            # Anthropic's API requires the assistant turn (with tool_use
            # blocks) to precede the tool_result user turn. Mock ignores
            # this field; real backends use it to reconstruct content.
            messages.append(LLMMessage(
                role="assistant",
                content=resp.text or "",
                tool_uses=list(resp.tool_uses),
            ))
            for tu in resp.tool_uses:
                tool_result = _dispatch_tool(client, tu.tool_name, tu.tool_input)
                n_tool_calls += 1
                messages.append(LLMMessage(
                    role="tool_result",
                    content=json.dumps(tool_result),
                    tool_use_id=tu.tool_use_id,
                ))
            continue
        if resp.stop_reason == "end_turn":
            final_text = resp.text
            break
        if resp.stop_reason == "error":
            error = "llm_error"
            break
    else:
        error = f"tool_loop_exceeded_{max_iters}_iters"

    latency_ms = (time.perf_counter() - t0) * 1000.0
    em, pm = _match(final_text, q.expected_answer)
    return QuestionResult(
        qid=q.qid, category=q.category, condition="substrate_with_tools",
        answer=final_text, expected=q.expected_answer,
        exact_match=em, partial_match=pm,
        tokens_in=tokens_in_total, tokens_out=tokens_out_total,
        latency_ms=round(latency_ms, 2),
        n_tool_calls=n_tool_calls,
        error=error,
    )


def _run_llm_only(
    client: TestClient,
    q: TestQuestion,
    corpus: Corpus,
    llm: LLMClient,
) -> QuestionResult:
    """LLM gets the corpus in the system prompt; no tool access."""
    # client is unused here but kept in the signature so future variants
    # (e.g. partial-context conditions that prune the corpus dump) can
    # consult substrate state for free.
    _ = client
    corpus_dump = corpus_as_context_string(corpus)
    system_prompt = _SYSTEM_PROMPT_LLM_ONLY.format(corpus_dump=corpus_dump)
    messages = [LLMMessage(role="user", content=q.test_question)]
    t0 = time.perf_counter()
    resp = llm.call(system_prompt=system_prompt, messages=messages, tools=None)
    latency_ms = (time.perf_counter() - t0) * 1000.0
    final_text = resp.text if resp.stop_reason == "end_turn" else ""
    em, pm = _match(final_text, q.expected_answer)
    return QuestionResult(
        qid=q.qid, category=q.category, condition="llm_only",
        answer=final_text, expected=q.expected_answer,
        exact_match=em, partial_match=pm,
        tokens_in=resp.tokens_in, tokens_out=resp.tokens_out,
        latency_ms=round(latency_ms, 2),
        n_tool_calls=0,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _store_corpus(client: TestClient, corpus: Corpus) -> dict[str, str]:
    """Store every fact; return key -> atom_id."""
    key_to_atom: dict[str, str] = {}
    for f in corpus.facts:
        resp = client.post("/store_fact", json={"key": f.key, "value": f.value})
        if resp.status_code != 200:
            raise RuntimeError(f"store_fact failed for {f.key}: {resp.text}")
        key_to_atom[f.key] = resp.json()["atom_id"]
    return key_to_atom


def _apply_edit_setup(
    client: TestClient,
    edits: dict,
    corpus: Corpus,
    key_to_atom: dict[str, str] | None,
) -> None:
    """Apply pre-question edits to BOTH the substrate AND the in-memory corpus.

    Substrate: POST /edit_fact with the atom_id (from the key_to_atom map
    built by _store_corpus) and the new value. The substrate's audit-chain
    handles versioning + post-edit retrieval semantics.

    Corpus: mutate the CorpusFact.value in-place so the next call to
    corpus_as_context_string (used by _run_llm_only) sees the edited value.
    Without this, the substrate condition gets the edit but the llm_only
    condition sees the original corpus dump -- which produces the same
    systematic miss we just diagnosed (Phase 1 first run, both conditions
    at 0pct exact on edit_aware while passing other categories).
    """
    if not edits:
        return
    if not key_to_atom:
        raise RuntimeError(
            "_apply_edit_setup needs key_to_atom mapping; pass through "
            "run_comparison_full_setup or supply explicitly to run_comparison."
        )
    for key, new_value in edits.items():
        atom_id = key_to_atom.get(key)
        if not atom_id:
            raise RuntimeError(f"no atom_id for edit key {key!r}")
        r = client.post(
            "/edit_fact",
            json={"atom_id": atom_id, "new_value": str(new_value)},
        )
        if r.status_code != 200:
            raise RuntimeError(f"edit_fact failed for {key}: {r.status_code} {r.text}")
        # Update the in-memory corpus so llm_only condition sees the edit too.
        for f in corpus.facts:
            if f.key == key:
                f.value = str(new_value)
                break


def _dispatch_tool(
    client: TestClient,
    tool_name: str,
    tool_input: dict,
) -> dict:
    """Map a tool name to the FastAPI endpoint + return the JSON body."""
    routes = {
        "substrate_retrieve_fact": ("POST", "/retrieve_fact"),
        "substrate_store_fact": ("POST", "/store_fact"),
        "substrate_edit_fact": ("POST", "/edit_fact"),
        "substrate_delete_fact": ("POST", "/delete_fact"),
        "substrate_compose_query": ("POST", "/compose_query"),
        "substrate_get_audit": ("GET", "/audit/{record_id}"),
    }
    if tool_name not in routes:
        return {"error": f"unknown_tool: {tool_name}"}
    method, path = routes[tool_name]
    if method == "GET":
        url = path.format(**tool_input)
        resp = client.get(url)
    else:
        resp = client.post(path, json=tool_input)
    if resp.status_code != 200:
        return {"error": f"http_{resp.status_code}", "body": resp.text}
    return resp.json()


def _match(actual: str, expected: str) -> tuple[bool, bool]:
    """Return (exact_match, partial_match) with normalization."""
    a = (actual or "").strip()
    e = (expected or "").strip()
    if not a:
        return False, False
    exact = a == e
    partial = exact or (e in a) or (a in e)
    return exact, partial


def _aggregate(
    rows: list[QuestionResult],
    conditions: Sequence[str],
) -> list[ConditionAggregate]:
    """Per-condition aggregate metrics."""
    out: list[ConditionAggregate] = []
    for cond in conditions:
        cond_rows = [r for r in rows if r.condition == cond]
        if not cond_rows:
            continue
        n = len(cond_rows)
        n_exact = sum(1 for r in cond_rows if r.exact_match)
        n_partial = sum(1 for r in cond_rows if r.partial_match)
        per_cat: dict[str, list[QuestionResult]] = {}
        for r in cond_rows:
            per_cat.setdefault(r.category, []).append(r)
        per_cat_acc = {
            cat: sum(1 for r in rs if r.exact_match) / len(rs)
            for cat, rs in per_cat.items()
        }
        out.append(ConditionAggregate(
            condition=cond,
            n_total=n,
            n_exact=n_exact,
            n_partial=n_partial,
            accuracy_exact=round(n_exact / n, 4),
            accuracy_partial=round(n_partial / n, 4),
            mean_tokens_in=round(sum(r.tokens_in for r in cond_rows) / n, 1),
            mean_tokens_out=round(sum(r.tokens_out for r in cond_rows) / n, 1),
            mean_total_tokens=round(
                sum(r.tokens_in + r.tokens_out for r in cond_rows) / n, 1
            ),
            mean_latency_ms=round(
                sum(r.latency_ms for r in cond_rows) / n, 2
            ),
            mean_tool_calls=round(
                sum(r.n_tool_calls for r in cond_rows) / n, 2
            ),
            per_category_accuracy={k: round(v, 4) for k, v in per_cat_acc.items()},
        ))
    return out


# ---------------------------------------------------------------------------
# Pretty-print
# ---------------------------------------------------------------------------

def format_report(report: HarnessReport) -> str:
    """Compact text-report for human review."""
    lines = []
    lines.append(f"Pattern B comparison: {report.n_questions} questions x "
                 f"{report.n_conditions} conditions")
    lines.append("")
    lines.append(f"{'Condition':<24} {'Exact':>6} {'Partial':>8} "
                 f"{'Tokens':>10} {'Latency_ms':>11} {'Tools/q':>8}")
    for a in report.aggregates:
        lines.append(
            f"{a.condition:<24} "
            f"{a.accuracy_exact*100:>5.1f}% "
            f"{a.accuracy_partial*100:>7.1f}% "
            f"{a.mean_total_tokens:>10.0f} "
            f"{a.mean_latency_ms:>11.1f} "
            f"{a.mean_tool_calls:>8.1f}"
        )
    lines.append("")
    lines.append("Per-category accuracy (exact):")
    for a in report.aggregates:
        cats = " ".join(f"{c}={v*100:.0f}%" for c, v in a.per_category_accuracy.items())
        lines.append(f"  {a.condition:<24} {cats}")
    return "\n".join(lines)
