"""Edit-quality metrics following MEMIT (Meng et al 2023) conventions.

Four metrics:
  efficacy           Did the edit take? P(target_new | prompt) > P(target_true | prompt).
                     SCAFFOLD: query(prompt) == expected substrate row index for target_new.
  specificity        Are neighborhood facts preserved? Average over neighborhood_prompts:
                     no shift in the method's answer on facts that share entities but not
                     the edited (subject, relation).
  paraphrase         Do paraphrases of the prompt also retrieve target_new?
                     Average over paraphrase_prompts.
  sequential_count   How many sequential edits can the method absorb before efficacy
                     falls below threshold (default 0.5)? Stream-level metric.

Each metric returns a float in [0, 1] for a single case, or `None` if not applicable
(e.g. no paraphrase prompts). sequential_count is a stream-level metric and is
emitted as None for single cases; the harness aggregator will use the stream variant
in Phase-2.

For the SCAFFOLD, metrics are intentionally cheap: they compare the method's
`query(prompt)` output to the method's `query(key_text(triple))` output. This is
faithful for the substrate (where key_text deterministically maps to a row),
and is a stand-in for the upstream LLM-token-probability metric until Phase-2
swaps in real probability head readers.

ASCII-only per CLAUDE.md.
"""
from __future__ import annotations

from typing import Any, Optional

from experiments.llm_benchmarks.edit_benchmark_harness import EditMethod, EditTriple


def _expected_target_token(method: EditMethod, triple: EditTriple) -> Optional[str]:
    """SCAFFOLD: the substrate hashes target_new -> a row idx; we use that as
    the "expected token". Real LLM impls compare logits over target_new tokens.
    """
    fn = getattr(method, "_val_vec", None)
    if fn is None:
        return None
    try:
        _vec, idx = fn(triple.target_new)
        return str(idx)
    except Exception:
        return None


def score_efficacy(method: EditMethod, triple: EditTriple) -> Optional[float]:
    """1.0 if method.query(prompt) returns the target_new token, else 0.0."""
    expected = _expected_target_token(method, triple)
    if expected is None:
        return None
    prompt = triple.prompt or f"{triple.subject}|||{triple.relation}"
    got = method.query(prompt)
    return 1.0 if got == expected else 0.0


def score_specificity(method: EditMethod, triple: EditTriple) -> Optional[float]:
    """Average non-overlap with target_new across neighborhood_prompts.

    SCAFFOLD: we measure the fraction of neighborhood prompts whose retrieved
    token differs from the edited target. Higher = more isolation = better.
    """
    if not triple.neighborhood_prompts:
        return None
    expected_target = _expected_target_token(method, triple)
    if expected_target is None:
        return None
    differing = 0
    for nprompt in triple.neighborhood_prompts:
        if method.query(nprompt) != expected_target:
            differing += 1
    return differing / float(len(triple.neighborhood_prompts))


def score_paraphrase(method: EditMethod, triple: EditTriple) -> Optional[float]:
    """Fraction of paraphrase_prompts that retrieve target_new."""
    if not triple.paraphrase_prompts:
        return None
    expected = _expected_target_token(method, triple)
    if expected is None:
        return None
    hits = 0
    for pprompt in triple.paraphrase_prompts:
        if method.query(pprompt) == expected:
            hits += 1
    return hits / float(len(triple.paraphrase_prompts))


def score_sequential_count(method: EditMethod, triple: EditTriple) -> Optional[float]:
    """Stream-level metric; per-case value is None (aggregator computes the stream).

    Phase-2: replaced by a stream walker that finds max prefix length with
    aggregate efficacy >= 0.5. See notes/llm_benchmark_harness_2026-05-29.md.
    """
    return None
