"""Wiring tests for the comparison harness.

Uses the MockLLMClient so the test runs without API credentials. Verifies:
  - Harness drives both conditions end-to-end
  - Metric math (accuracy, tokens, latency) is internally consistent
  - Per-category accuracy buckets are populated
  - Reports are pretty-printable

These tests do NOT validate any claim about real LLM performance. They
validate that the harness IS WIRED UP correctly so the swap-in of a real
LLM client produces meaningful comparison data without further plumbing.
"""

from __future__ import annotations

import os
import shutil
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from hdlab_service.baselines.comparison_harness import (
    format_report,
    run_comparison_full_setup,
)
from hdlab_service.baselines.llm_client import MockLLMClient
from hdlab_service.baselines.questions import build_question_set
from hdlab_service.corpora.synthetic_corpus import small_corpus


@pytest.fixture()
def client(tmp_path) -> Iterator[TestClient]:
    state_dir = tmp_path / "state"
    keys_dir = state_dir / "keys"
    audit_path = state_dir / "audit_log.jsonl"
    os.environ["HDLAB_N"] = "256"
    os.environ["HDLAB_CODEBOOK"] = "BSC"
    os.environ["HDLAB_KEY_DIR"] = str(keys_dir)
    os.environ["HDLAB_AUDIT_PATH"] = str(audit_path)
    import importlib
    from hdlab_service import server as server_module
    importlib.reload(server_module)
    with TestClient(server_module.app) as c:
        yield c
    if state_dir.exists():
        shutil.rmtree(state_dir, ignore_errors=True)


def test_question_set_built_from_corpus() -> None:
    """The question set has both single-hop and multi-hop coverage."""
    corpus = small_corpus()
    qs = build_question_set(corpus)
    assert len(qs) >= 7
    categories = {q.category for q in qs}
    assert "single_hop" in categories
    assert "multi_hop" in categories
    # Every question has a non-empty expected_answer.
    for q in qs:
        assert q.expected_answer
        assert q.test_question


def test_harness_runs_both_conditions(client: TestClient) -> None:
    """End-to-end: store corpus + ask all questions in both conditions."""
    corpus = small_corpus()
    questions = build_question_set(corpus)
    llm = MockLLMClient()
    report, _key_to_atom = run_comparison_full_setup(
        client=client,
        corpus=corpus,
        questions=questions,
        llm=llm,
        conditions=("substrate_with_tools", "llm_only"),
    )
    assert report.n_questions == len(questions)
    assert report.n_conditions == 2
    # Each row pair (substrate, llm_only) per question
    assert len(report.rows) == len(questions) * 2
    # Both aggregates present
    aggs = {a.condition: a for a in report.aggregates}
    assert "substrate_with_tools" in aggs
    assert "llm_only" in aggs
    # Metric math sanity
    for a in report.aggregates:
        assert 0.0 <= a.accuracy_exact <= 1.0
        assert 0.0 <= a.accuracy_partial <= 1.0
        assert a.accuracy_partial >= a.accuracy_exact
        assert a.mean_total_tokens > 0
        # Mock LLM uses tool calls only in the substrate condition.
        if a.condition == "substrate_with_tools":
            assert a.mean_tool_calls > 0
        else:
            assert a.mean_tool_calls == 0


def test_harness_mock_llm_resolves_known_keys(client: TestClient) -> None:
    """Mock LLM + harness correctly answers single-hop questions in both conditions.

    Verifies the harness wiring delivers what the comparison is meant to
    measure: known-answer questions resolve through both paths.
    """
    corpus = small_corpus()
    questions = build_question_set(corpus)
    llm = MockLLMClient()
    report, _ = run_comparison_full_setup(
        client=client, corpus=corpus, questions=questions, llm=llm,
    )
    # Single-hop questions should resolve in both conditions with the mock.
    single_hop_rows = [r for r in report.rows if r.category == "single_hop"]
    assert len(single_hop_rows) >= 4
    sub_single = [r for r in single_hop_rows if r.condition == "substrate_with_tools"]
    llm_single = [r for r in single_hop_rows if r.condition == "llm_only"]
    # Both should hit >= 75% partial-match on single-hop with the mock.
    sub_acc = sum(1 for r in sub_single if r.partial_match) / len(sub_single)
    llm_acc = sum(1 for r in llm_single if r.partial_match) / len(llm_single)
    assert sub_acc >= 0.75, f"substrate single-hop partial accuracy {sub_acc:.2f} < 0.75"
    assert llm_acc >= 0.75, f"llm-only single-hop partial accuracy {llm_acc:.2f} < 0.75"


def test_harness_substrate_uses_tools(client: TestClient) -> None:
    """Substrate-with-tools rows have at least one tool call per question."""
    corpus = small_corpus()
    questions = build_question_set(corpus)
    llm = MockLLMClient()
    report, _ = run_comparison_full_setup(
        client=client, corpus=corpus, questions=questions, llm=llm,
    )
    sub_rows = [r for r in report.rows if r.condition == "substrate_with_tools"]
    assert sub_rows
    for r in sub_rows:
        if r.error:
            continue  # Skip errored rows; still required to count tool calls if any.
        assert r.n_tool_calls >= 1, (
            f"substrate row {r.qid} expected >=1 tool call; got {r.n_tool_calls}"
        )


def test_format_report_pretty_prints(client: TestClient) -> None:
    """format_report returns a non-empty multi-line string."""
    corpus = small_corpus()
    questions = build_question_set(corpus)[:3]  # Subset for speed
    llm = MockLLMClient()
    report, _ = run_comparison_full_setup(
        client=client, corpus=corpus, questions=questions, llm=llm,
    )
    text = format_report(report)
    assert "Pattern B comparison" in text
    assert "substrate_with_tools" in text
    assert "llm_only" in text
    assert "Exact" in text
