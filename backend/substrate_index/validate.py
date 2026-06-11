"""LLM comparison harness for the substrate self-index.

Per Research Refinement 2 (SELF_INDEX_RESCOPE_ENDORSED 2026-06-11):
- LLM-as-judge is DISQUALIFIED (circular evaluation).
- Both substrate AND LLM are SYSTEMS UNDER TEST.
- Both score against externally-verified benchmark ground truth
  (TestQuery.expected_atom_ids).
- 5-axis pre-registered harness with CLUTRR / SME / MIRB benchmark anchors
  (Day 2-3 hook; current scope: Research's 5 disclosed queries Q1-Q5).

LLMs receive the candidate atom vocabulary in the prompt and return ranked
atom-id picks; we score those picks against ground truth using the same
metrics layer as substrate.

Output: a SystemDiagnostic per system, plus a comparative SystemDiagnostic
that records substrate-vs-LLM head-to-head NDCG.
"""
from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Optional, Protocol

from backend.substrate_index.metrics import (
    QueryScore,
    SystemDiagnostic,
    diagnose,
    score_query,
)
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.retrieve import Retriever
from backend.substrate_index.schema import (
    QueryResult,
    TestQuery,
)

logger = logging.getLogger(__name__)


# ============================================================
# LLM client protocol
# ============================================================


class LLMClient(Protocol):
    """Minimal interface; supply your own (Anthropic / OpenAI / local).

    The client is given a prompt and returns the model's text response.
    Implementations should set temperature=0 for stability.
    """

    def complete(self, system_prompt: str, user_prompt: str) -> str: ...

    @property
    def name(self) -> str: ...


# ============================================================
# Prompt builder
# ============================================================


_SYSTEM_PROMPT = (
    "You are an expert in vector-symbolic architectures, hyperdimensional "
    "computing, and the mathematics of substrate self-improvement (FHRR, "
    "HMM decoding, global discrete optimization, etc.).\n"
    "\n"
    "You will be given a vocabulary of atom ids each labeled with a name "
    "and one-line description, and a single question. Return the top-K most "
    "relevant atom ids as a strict JSON array of strings -- nothing else. "
    "If fewer than K atoms are relevant, return fewer. Do not invent atom ids "
    "not in the vocabulary."
)


def build_llm_prompt(
    query_text: str,
    pstore: PartitionedStore,
    top_k: int,
    vocab_filter_corpus: Optional[str] = None,
) -> tuple[str, str]:
    """Compose (system_prompt, user_prompt) for the LLM head-to-head call.

    vocab_filter_corpus: optionally restrict the vocabulary the LLM sees
    (e.g., only math atoms for math-only queries).
    """
    atoms = pstore.all_atoms()
    if vocab_filter_corpus:
        atoms = [a for a in atoms if a.corpus.value == vocab_filter_corpus]
    # Render each atom compactly: qualified_id | name | first sentence
    vocab_lines = []
    for a in atoms:
        first_sentence = a.description.split(". ")[0].strip()
        if len(first_sentence) > 180:
            first_sentence = first_sentence[:180] + "..."
        vocab_lines.append(f"- {a.qualified_id} | {a.name} | {first_sentence}")
    vocab_text = "\n".join(vocab_lines)

    user_prompt = (
        f"VOCABULARY ({len(atoms)} atoms):\n"
        f"{vocab_text}\n\n"
        f"QUESTION: {query_text}\n\n"
        f"Return the top {top_k} most relevant atom ids as a JSON array of strings, "
        f"e.g. [\"math::T2/fhrr_bind\", \"math::T2/fhrr_unbind\"]. Nothing else."
    )
    return _SYSTEM_PROMPT, user_prompt


# ============================================================
# Response parser
# ============================================================


_JSON_ARRAY_PATTERN = re.compile(r'\[[^\]]*\]', re.DOTALL)


def parse_llm_response(text: str, known_atom_ids: set[str]) -> list[str]:
    """Extract a list of atom ids from the LLM response.

    Tolerant to:
    - JSON array wrapping with surrounding chatter
    - Atom ids appearing inline as bullet lists
    - Filters to only return atom ids that exist in the corpus (drops
      hallucinated ids).
    """
    # Try JSON parse first
    matches = _JSON_ARRAY_PATTERN.findall(text)
    for m in matches:
        try:
            parsed = json.loads(m)
            if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
                return [x for x in parsed if x in known_atom_ids]
        except json.JSONDecodeError:
            continue
    # Fallback: pick known atom ids out of the text body
    found = []
    for aid in known_atom_ids:
        if aid in text:
            found.append(aid)
    return found[:10]


# ============================================================
# Head-to-head run
# ============================================================


@dataclass(frozen=True)
class HeadToHeadResult:
    """Output of a full benchmark run."""
    substrate_diagnostic: SystemDiagnostic
    llm_diagnostic: SystemDiagnostic
    substrate_scores: tuple[QueryScore, ...]
    llm_scores: tuple[QueryScore, ...]
    llm_name: str

    def to_dict(self) -> dict:
        return {
            "substrate_diagnostic": self.substrate_diagnostic.to_dict(),
            "llm_diagnostic": self.llm_diagnostic.to_dict(),
            "substrate_scores": [s.to_dict() for s in self.substrate_scores],
            "llm_scores": [s.to_dict() for s in self.llm_scores],
            "llm_name": self.llm_name,
        }


def run_substrate(
    pstore: PartitionedStore,
    retriever: Retriever,
    queries: list[TestQuery],
    top_k: int = 10,
) -> tuple[list[QueryScore], list[QueryResult]]:
    """Run all queries against substrate retriever; return scores + raw results."""
    known_ids = pstore.all_qualified_ids()
    scores: list[QueryScore] = []
    raws: list[QueryResult] = []
    for q in queries:
        t0 = time.perf_counter()
        cands = retriever.semantic(q.query_text, top_k=top_k)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        # Also pull structural neighbors if expected_relations are non-empty
        # (best-effort; relation graph may be sparse)
        result = retriever.as_query_result(q.qid, cands, latency_ms=elapsed_ms)
        # Structural: try to add the typed-edge endpoints
        from backend.substrate_index.schema import RelationType
        struct_results = []
        for atom_cand in cands[:3]:
            for rt in RelationType:
                for n in pstore.out_neighbors(atom_cand.atom_id, rt):
                    struct_results.append((atom_cand.atom_id, rt.value, n))
        # Just take a handful for evidence
        from dataclasses import replace
        result = QueryResult(
            qid=result.qid,
            returned_atom_ids=result.returned_atom_ids,
            returned_relations=tuple(struct_results[:10]),
            latency_ms=result.latency_ms,
            raw_scores=result.raw_scores,
        )
        scores.append(score_query(q, result, known_ids))
        raws.append(result)
    return scores, raws


def run_llm(
    pstore: PartitionedStore,
    queries: list[TestQuery],
    llm: LLMClient,
    top_k: int = 10,
    vocab_filter_corpus: Optional[str] = None,
) -> tuple[list[QueryScore], list[QueryResult]]:
    """Run all queries against the LLM head-to-head. NOT LLM-as-judge --
    LLM is itself a SYSTEM UNDER TEST, scored against the same ground truth.
    """
    known_ids = pstore.all_qualified_ids()
    scores: list[QueryScore] = []
    raws: list[QueryResult] = []
    for q in queries:
        sys_p, user_p = build_llm_prompt(q.query_text, pstore, top_k, vocab_filter_corpus)
        t0 = time.perf_counter()
        try:
            response = llm.complete(sys_p, user_p)
        except Exception as e:
            logger.exception("LLM call failed on qid=%s: %s", q.qid, e)
            response = "[]"
        elapsed_ms = (time.perf_counter() - t0) * 1000
        picked = parse_llm_response(response, known_ids)
        result = QueryResult(
            qid=q.qid,
            returned_atom_ids=tuple(picked),
            returned_relations=(),
            latency_ms=elapsed_ms,
            raw_scores=tuple(),
        )
        scores.append(score_query(q, result, known_ids))
        raws.append(result)
    return scores, raws


def head_to_head(
    pstore: PartitionedStore,
    retriever: Retriever,
    queries: list[TestQuery],
    llm: LLMClient,
    top_k: int = 10,
    vocab_filter_corpus: Optional[str] = None,
) -> HeadToHeadResult:
    """Full benchmark: substrate + LLM, scored against ground truth, comparative
    diagnostic with substrate-vs-LLM win/loss/tie by NDCG."""
    sub_scores, _ = run_substrate(pstore, retriever, queries, top_k=top_k)
    llm_scores, _ = run_llm(pstore, queries, llm, top_k=top_k, vocab_filter_corpus=vocab_filter_corpus)
    sub_diag = diagnose(sub_scores, llm_scores=llm_scores)
    llm_diag = diagnose(llm_scores)
    return HeadToHeadResult(
        substrate_diagnostic=sub_diag,
        llm_diagnostic=llm_diag,
        substrate_scores=tuple(sub_scores),
        llm_scores=tuple(llm_scores),
        llm_name=llm.name,
    )


# ============================================================
# Minimal LLM client adapters
# ============================================================


class AnthropicClient:
    """Lightweight Anthropic wrapper. Requires ANTHROPIC_API_KEY env var."""

    def __init__(self, model: str = "claude-opus-4-7"):
        import os
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise RuntimeError("pip install anthropic to use AnthropicClient") from e
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("set ANTHROPIC_API_KEY env var")
        self._client = Anthropic(api_key=api_key)
        self._model = model

    @property
    def name(self) -> str:
        return f"anthropic/{self._model}"

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=2048,
            temperature=0.0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return resp.content[0].text


class OpenAIClient:
    """Lightweight OpenAI wrapper. Requires OPENAI_API_KEY env var."""

    def __init__(self, model: str = "gpt-4o-mini"):
        import os
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError("pip install openai to use OpenAIClient") from e
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("set OPENAI_API_KEY env var")
        self._client = OpenAI(api_key=api_key)
        self._model = model

    @property
    def name(self) -> str:
        return f"openai/{self._model}"

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or ""
