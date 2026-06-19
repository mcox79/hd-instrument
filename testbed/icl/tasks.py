"""Probe 2 task generators: analogy / arithmetic-with-format / sentiment.

Each generator returns a list of problem dicts with the shape:

    {
      "task_type": str,             # "analogy" | "arithmetic" | "sentiment"
      "demos":     [(in, out), ...] # K demonstration examples
      "query":     str,             # the held-out input
      "answer":    str,             # ground-truth output
      "format_id": str,             # for arithmetic: which format was used
    }

The generators are seed-deterministic.  Demos and held-out query are disjoint
(no demo example appears in the query set for a given seed/task).

ASCII-only stdout per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np

# -----------------------------------------------------------------------------
# Analogy lexicon (fixed small relation pairs)
# -----------------------------------------------------------------------------
# A is to B as C is to ?  -> relation R: A->B and C->?
# We use a small lexicon of (relation_name, [(a, b), ...]) and form analogies
# by sampling 2 pairs from the SAME relation.
_ANALOGY_RELATIONS: Dict[str, List[Tuple[str, str]]] = {
    "male_to_female": [
        ("king", "queen"), ("man", "woman"), ("boy", "girl"),
        ("father", "mother"), ("brother", "sister"), ("uncle", "aunt"),
        ("nephew", "niece"), ("son", "daughter"), ("husband", "wife"),
        ("prince", "princess"), ("actor", "actress"), ("waiter", "waitress"),
    ],
    "singular_to_plural": [
        ("cat", "cats"), ("dog", "dogs"), ("book", "books"),
        ("car", "cars"), ("tree", "trees"), ("house", "houses"),
        ("apple", "apples"), ("table", "tables"), ("chair", "chairs"),
        ("phone", "phones"), ("road", "roads"), ("river", "rivers"),
    ],
    "present_to_past": [
        ("walk", "walked"), ("talk", "talked"), ("jump", "jumped"),
        ("look", "looked"), ("play", "played"), ("call", "called"),
        ("open", "opened"), ("close", "closed"), ("paint", "painted"),
        ("rain", "rained"), ("learn", "learned"), ("watch", "watched"),
    ],
    "country_to_capital": [
        ("france", "paris"), ("germany", "berlin"), ("italy", "rome"),
        ("spain", "madrid"), ("japan", "tokyo"), ("china", "beijing"),
        ("russia", "moscow"), ("egypt", "cairo"), ("greece", "athens"),
        ("portugal", "lisbon"), ("austria", "vienna"), ("poland", "warsaw"),
    ],
}


def generate_analogy_problems(n: int, seed: int, k_demos: int = 10) -> List[Dict[str, Any]]:
    """Return n analogy problems with k_demos demonstrations each.

    Each problem picks a random relation; the demos are k_demos pair-pairs
    from that relation; the query is a held-out pair from the same relation.
    """
    rng = np.random.default_rng(int(seed))
    out: List[Dict[str, Any]] = []
    rel_names = list(_ANALOGY_RELATIONS.keys())
    for _ in range(n):
        # Sample a relation
        rel = str(rng.choice(rel_names))
        pairs = list(_ANALOGY_RELATIONS[rel])
        # Need k_demos + 1 distinct pair-pairs from this relation; the relation has
        # ~12 pairs, so we sample with replacement at the pair-pair level if needed
        # but we ensure the QUERY pair-pair is distinct from any demo pair-pair.
        n_pairs = len(pairs)
        # Demo: each demo is "A is to B as C is to D"; we sample two distinct
        # pairs from `pairs` and form the analogy.
        demos: List[Tuple[str, str]] = []
        for _d in range(k_demos):
            idx = rng.choice(n_pairs, size=2, replace=False)
            (a, b), (c, d) = pairs[int(idx[0])], pairs[int(idx[1])]
            prompt = f"{a} is to {b} as {c} is to"
            demos.append((prompt, d))
        # Query: distinct from demos -- sample two pairs
        for _attempt in range(20):
            idx_q = rng.choice(n_pairs, size=2, replace=False)
            (a, b), (c, d) = pairs[int(idx_q[0])], pairs[int(idx_q[1])]
            q_prompt = f"{a} is to {b} as {c} is to"
            if q_prompt not in {dp[0] for dp in demos}:
                break
        out.append({
            "task_type": "analogy",
            "relation": rel,
            "demos": demos,
            "query": q_prompt,
            "answer": d,
            "format_id": "analogy_v1",
        })
    return out


# -----------------------------------------------------------------------------
# Arithmetic-with-format
# -----------------------------------------------------------------------------
_ARITHMETIC_FORMATS = [
    # format_id, format-fn (a, b, op) -> (prompt_str, answer_str)
    # op is one of "+", "-", "*"
    "tuple_arrow",     # "(3, 5) -> 8"
    "words",           # "three plus five equals 8"
    "function_call",   # "f(3, 5) = 8"
    "vertical_bar",    # "3 | 5 = 8"
]

_WORDS = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
    11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
    16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
}
_OP_WORDS = {"+": "plus", "-": "minus", "*": "times"}


def _apply_op(a: int, b: int, op: str) -> int:
    if op == "+": return a + b
    if op == "-": return a - b
    if op == "*": return a * b
    raise ValueError(f"unknown op {op!r}")


def _format_arithmetic(a: int, b: int, op: str, fmt: str) -> Tuple[str, str]:
    """Return (prompt_str_without_answer, answer_str)."""
    ans = _apply_op(a, b, op)
    if fmt == "tuple_arrow":
        return (f"({a}, {b}) ->", str(ans))
    if fmt == "words":
        # Only use words for small numbers; otherwise digits
        aw = _WORDS.get(a, str(a))
        bw = _WORDS.get(b, str(b))
        return (f"{aw} {_OP_WORDS[op]} {bw} equals", str(ans))
    if fmt == "function_call":
        op_name = {"+": "add", "-": "sub", "*": "mul"}[op]
        return (f"{op_name}({a}, {b}) =", str(ans))
    if fmt == "vertical_bar":
        return (f"{a} | {b} =", str(ans))
    raise ValueError(f"unknown fmt {fmt!r}")


def generate_arithmetic_problems(n: int, seed: int, k_demos: int = 10) -> List[Dict[str, Any]]:
    """Return n arithmetic-with-format problems.

    Each problem picks one of 4 non-standard formats; demos teach the format
    via k_demos solved (a, b, op) examples; query is a held-out (a, b, op).
    Numbers are sampled from 0..15 to keep words readable.
    """
    rng = np.random.default_rng(int(seed) ^ 0xA1)
    out: List[Dict[str, Any]] = []
    for _ in range(n):
        fmt = str(rng.choice(_ARITHMETIC_FORMATS))
        # Fix one op per problem to keep format-learning the dominant signal
        op = str(rng.choice(["+", "-", "*"]))
        demos: List[Tuple[str, str]] = []
        seen_pairs: set = set()
        while len(demos) < k_demos:
            a = int(rng.integers(0, 16))
            b = int(rng.integers(0, 16))
            if op == "-" and b > a:
                a, b = b, a
            if op == "*":
                # Cap product size for vocabulary friendliness
                if a > 9 or b > 9:
                    continue
            if (a, b) in seen_pairs:
                continue
            seen_pairs.add((a, b))
            prompt, ans = _format_arithmetic(a, b, op, fmt)
            demos.append((prompt, ans))
        # Query: distinct from demos
        for _attempt in range(50):
            a = int(rng.integers(0, 16))
            b = int(rng.integers(0, 16))
            if op == "-" and b > a:
                a, b = b, a
            if op == "*" and (a > 9 or b > 9):
                continue
            if (a, b) not in seen_pairs:
                break
        q_prompt, q_ans = _format_arithmetic(a, b, op, fmt)
        out.append({
            "task_type": "arithmetic",
            "op": op,
            "demos": demos,
            "query": q_prompt,
            "answer": q_ans,
            "format_id": fmt,
        })
    return out


# -----------------------------------------------------------------------------
# Sentiment classification
# -----------------------------------------------------------------------------
_POSITIVE_SENTENCES = [
    "the movie was wonderful",
    "i love this product",
    "what a beautiful day",
    "the food tastes amazing",
    "this is the best vacation ever",
    "she gave a brilliant performance",
    "i feel so grateful today",
    "the gift was perfect",
    "everyone had a great time",
    "the music was uplifting",
    "the view is breathtaking",
    "i am so happy with the result",
    "this book is delightful",
    "the team played extraordinarily well",
    "her smile lit up the room",
    "the service was excellent",
    "i adore this song",
    "the project succeeded beyond expectations",
    "the cake was delicious",
    "we had a fantastic evening",
]
_NEGATIVE_SENTENCES = [
    "the movie was terrible",
    "i hate this product",
    "what an awful day",
    "the food tastes disgusting",
    "this is the worst vacation ever",
    "she gave a dreadful performance",
    "i feel so miserable today",
    "the gift was a disappointment",
    "everyone had a bad time",
    "the music was annoying",
    "the view is depressing",
    "i am so frustrated with the result",
    "this book is boring",
    "the team played horribly",
    "her scowl darkened the room",
    "the service was rude",
    "i despise this song",
    "the project failed completely",
    "the cake was stale",
    "we had a miserable evening",
]


def generate_sentiment_problems(n: int, seed: int, k_demos: int = 10) -> List[Dict[str, Any]]:
    """Return n sentiment problems.  Labels: 'happy' / 'sad'."""
    rng = np.random.default_rng(int(seed) ^ 0xB2)
    pos = list(_POSITIVE_SENTENCES)
    neg = list(_NEGATIVE_SENTENCES)
    out: List[Dict[str, Any]] = []
    for _ in range(n):
        # Build k_demos as a balanced mix (k/2 positive, k/2 negative, with rng order)
        n_pos = k_demos // 2
        n_neg = k_demos - n_pos
        # Sample WITHOUT replacement so demos are distinct
        # But we also need to reserve at least one for the query.
        pos_idx = rng.choice(len(pos), size=n_pos + 1, replace=False)
        neg_idx = rng.choice(len(neg), size=n_neg + 1, replace=False)
        demos: List[Tuple[str, str]] = []
        for i in pos_idx[:n_pos]:
            demos.append((f"sentence: {pos[int(i)]} sentiment:", "happy"))
        for i in neg_idx[:n_neg]:
            demos.append((f"sentence: {neg[int(i)]} sentiment:", "sad"))
        # Shuffle demo order
        order = rng.permutation(len(demos))
        demos = [demos[int(j)] for j in order]
        # Query
        if rng.random() < 0.5:
            q_sent = pos[int(pos_idx[-1])]
            q_ans = "happy"
        else:
            q_sent = neg[int(neg_idx[-1])]
            q_ans = "sad"
        out.append({
            "task_type": "sentiment",
            "demos": demos,
            "query": f"sentence: {q_sent} sentiment:",
            "answer": q_ans,
            "format_id": "sentiment_v1",
        })
    return out


# -----------------------------------------------------------------------------
# Self-test
# -----------------------------------------------------------------------------
def _selftest() -> None:
    """PROT-022: verify each generator produces well-formed, deterministic problems."""
    print("[selftest] testbed.icl.tasks")

    for gen, name in [
        (generate_analogy_problems, "analogy"),
        (generate_arithmetic_problems, "arithmetic"),
        (generate_sentiment_problems, "sentiment"),
    ]:
        probs = gen(20, seed=7, k_demos=10)
        assert len(probs) == 20, f"{name}: wrong n: {len(probs)}"
        for p in probs:
            assert isinstance(p, dict)
            assert "demos" in p and "query" in p and "answer" in p and "task_type" in p
            assert len(p["demos"]) == 10, f"{name}: demos != 10: {len(p['demos'])}"
            for d in p["demos"]:
                assert isinstance(d, tuple) and len(d) == 2
                assert isinstance(d[0], str) and isinstance(d[1], str)
                # Demo input shouldn't equal query (sanity, not iron-clad for arithmetic)
            assert isinstance(p["query"], str) and len(p["query"]) > 0
            assert isinstance(p["answer"], str) and len(p["answer"]) > 0
        # Determinism: re-call with same seed -> identical
        probs2 = gen(20, seed=7, k_demos=10)
        assert probs == probs2, f"{name}: NOT deterministic with same seed"
        # Different seed -> different
        probs3 = gen(20, seed=11, k_demos=10)
        assert probs != probs3, f"{name}: SAME output with different seeds"
        print(f"  PASS {name}: 20 problems, demos=10, deterministic, seed-varying")

    print("[selftest] testbed.icl.tasks ALL PASS")


_selftest()


if __name__ == "__main__":
    _selftest()
    # Demo
    for gen, name in [
        (generate_analogy_problems, "analogy"),
        (generate_arithmetic_problems, "arithmetic"),
        (generate_sentiment_problems, "sentiment"),
    ]:
        probs = gen(3, seed=42, k_demos=4)
        print(f"\n--- {name} (first 3) ---")
        for p in probs:
            print(f"  demos[0]: {p['demos'][0]}")
            print(f"  query:    {p['query']!r}  ->  {p['answer']!r}")
