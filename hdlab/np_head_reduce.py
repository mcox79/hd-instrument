"""np_head_reduce -- the glass-box NP-HEAD reducer (Stage A of who-did-what role assignment).

Landed 2026-09-03 from the owner-DONE `the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning`
(SOLVED, EXCELLENT, witness test_whodidwhat_nphead_case.py 45/45). THE high-value structural fix: the reader's
role assigners pick the WRONG word inside a noun phrase ("the undertaker's shop" -> undertaker; "iron gate" ->
iron) on ~1/3 of clean 19c clauses -- 96% of the LANDED assigners' misses are exactly this. Reducing each
candidate to its NP HEAD before the role pick lifts EVERY consumer (resolve_patient / hybrid_role_patient /
competition_pick / route_predicate_arguments) +0.20 first-hand (0.683 -> 0.888), and the full drop-in stack takes
the live reader 0.629 -> 0.981 end-to-end -- ALL CI-separated, info-free twin (shuffled reduction) LOSES.

PINNED (constituent-head identification is a real comprehension stage): the NP head is found by the Right-hand
Head Rule for compounds (Williams 1981 -- the head of [N N] is the rightmost noun) and the DP-head rule for
genitives (Abney 1987 -- the head of [NP 's N] is the possessed N, not the possessor); bracket-closure / phrase
composition is neurally real (Nelson 2017 ECoG; Ding 2016; Pallier 2011). So: DROP a candidate that is a compound
MODIFIER (immediately followed by a NOUN/PROPN) or a genitive POSSESSOR (immediately followed by 's); KEEP the head.

Byte-exact to the validated reference `experiments/exp_whodidwhat_full_fix_v1._np_head_reduce_pairs` (index form).
Glass-box, stdlib-only, deterministic. NO spaCy / NO LLM. ASCII.
"""
from __future__ import annotations

from typing import List, Sequence

# genitive markers (straight + curly apostrophe) -- from the validated cell (exp_whodidwhat_nphead_case_v1.POSS)
POSS = frozenset({"'s", "'", "s'", "’s", "’"})

# a candidate immediately followed by one of these POS tags is a compound MODIFIER, not the head (RHR)
_HEAD_BLOCKING_NEXT_POS = ("NOUN", "PROPN")


def is_np_head(toks: Sequence[str], pos: Sequence[str], ix: int) -> bool:
    """True iff the token at index `ix` is (plausibly) the HEAD of its NP: it is NOT a compound modifier
    (immediately followed by NOUN/PROPN) and NOT a genitive possessor (immediately followed by 's)."""
    nxt_pos = pos[ix + 1] if ix + 1 < len(pos) else "X"
    nxt_tok = toks[ix + 1].lower() if ix + 1 < len(toks) else ""
    return not ((nxt_pos in _HEAD_BLOCKING_NEXT_POS) or (nxt_tok in POSS))


def np_head_reduce(toks: Sequence[str], pos: Sequence[str], cand_indices: Sequence[int]) -> List[int]:
    """Reduce a list of candidate token INDICES to their NP heads (drop compound modifiers + genitive
    possessors, Right-hand Head Rule + DP-head). Falls back to the input if the reduction empties it
    (never returns []). Byte-exact to exp_whodidwhat_full_fix_v1._np_head_reduce_pairs on the index of each pair."""
    out = [ix for ix in cand_indices if is_np_head(toks, pos, ix)]
    return out or list(cand_indices)


def np_head_reduce_pairs(toks: Sequence[str], pos: Sequence[str], cand_pairs):
    """Pair form `[(head_string, idx), ...] -> [(head_string, idx), ...]` -- byte-identical to the validated
    reference reducer, for callers that carry (head, idx) pairs (e.g. graded candidate lists)."""
    out = [(h, ix) for h, ix in cand_pairs if is_np_head(toks, pos, ix)]
    return out or list(cand_pairs)


__all__ = ["np_head_reduce", "np_head_reduce_pairs", "is_np_head", "POSS"]
