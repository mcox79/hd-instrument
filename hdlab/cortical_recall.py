"""hdlab/cortical_recall.py -- ORGANS Q1/Q3, THE CORTICAL READ. Retrieval from CONSOLIDATED memory.

THE DEFECT THIS EXISTS TO FIX, MEASURED END TO END ON 2026-08-19.
`exp_substrate_end_to_end_readout_v1` v3 (3 seeds, 18 units): ablating consolidation to ZERO
provenance rows left the read-out IDENTICAL in 9 of 12 cells, and the EPISODIC route identical to
four decimals in all six. Ablating `definitions` cut grounding by a third and moved the read-out by
exactly 0.0000 in all twelve. The mechanism is a code fact: `recall_sentence()` addresses the
episodic DG codes and never touches `state.store`. THE CONSOLIDATED STORE IS WRITTEN AND NEVER READ.

BRAIN FRAME (Complementary Learning Systems; McClelland, McNaughton & O'Reilly 1995).
The hippocampus writes fast and sparse; replay transfers to neocortex; retrieval of CONSOLIDATED
knowledge is a CORTICAL read, and becomes progressively hippocampus-independent. We built the write
(D3) and the transfer (B3) and then answered every question out of the hippocampus. POSITION was
inverted -- consolidation sat downstream of retrieval where the brain puts it upstream. That is why
the substrate memorises almost perfectly (exact key 0.9333) and transfers nothing (held out
0.0044): a pure-hippocampal system recognises what it has seen and generalises nothing.

*** WHY THIS IS NOT BUILT ON THE FACT STORE'S OWN KEYS, WHICH WAS THE OBVIOUS DESIGN. ***
MEASURED (`scratch/probe_store_key_space_has_no_semantics.py`), because reading the code is not
evidence in this project: in `HDFactStore`'s `sr_key` space, semantically RELATED subject pairs
score 0.4850 and UNRELATED pairs 0.4717 -- a gap of +0.0133, with an identical-key positive control
at 1.0000. **The key space carries NO semantic similarity: `_sr_key` binds a per-symbol code, so
`dog` and `cat` get unrelated keys by construction.** The store is an EXACT-KEY hash-addressed
database. Cortical semantic memory is a DISTRIBUTED OVERLAPPING code in which similar concepts have
similar patterns, and pattern completion from a partial cue is only possible in such a code. That
is a SHAPE fidelity divergence, and it is the reason this organ retrieves in a SEMANTIC space and
uses the store only to say WHICH terms are consolidated and WHAT they were grounded to.

WHAT IS PINNED AND WHAT IS OURS.
  PINNED    consolidated knowledge is read from cortex, not from the hippocampus; the cortical
            store is a small distilled subset of what was experienced.
  PINNED    that subset is SPARSE relative to experience. Measured here: 2,883 episodic lemmas to
            68 consolidated facts, a 42x gap with the gate refusing ~88%. That is CLS behaving
            correctly and must NOT be "fixed" by loosening the gate.
  OURS      the SPACE the cortical read happens in (accumulated context, sensorimotor, or both)
            and the similarity rule over it. There is no pinned equation for cortical semantic
            retrieval. OUR-INVENTION-BEING-TESTED, and labelled so wherever it is scored.

*** SCOPE WARNING THAT MUST TRAVEL WITH THIS ORGAN. ***
It can only answer about terms that have been CONSOLIDATED. Measured before it was written
(`scratch/probe_cortical_route_feasibility.py`): on the cloze read-out task only 18 of 300
held-out targets (6.0%) have any entry in the store, which covers 2.4% of the candidate pool. **DO
NOT SCORE THIS ORGAN ON THAT TASK** -- it would read near zero from having no entry rather than
from being wrong, which is an unwinnable test, not a negative. Score it on an instrument built
around what was actually consolidated.

USAGE
  python -m hdlab.cortical_recall     # self-test
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

SPACES = ("context", "spoke", "both")


@dataclass(frozen=True)
class CorticalHit:
    """One retrieved consolidated concept. `meaning` is what the gate grounded the term TO."""
    term: str
    meaning: Optional[str]
    score: float


def _unit(v: np.ndarray) -> Optional[np.ndarray]:
    v = np.asarray(v, dtype=np.float64).reshape(-1)
    n = float(np.linalg.norm(v))
    return None if n < 1e-12 else v / n


def _spoke_vec(word: str) -> Optional[np.ndarray]:
    from hdlab.sensorimotor_spoke import profile
    return profile(word)


def build_cortical_index(consolidated: Dict[str, Optional[str]],
                         context_profiles: Dict[str, np.ndarray],
                         *, space: str = "context") -> Dict[str, np.ndarray]:
    """One unit vector per CONSOLIDATED term, in the requested semantic space.

    `consolidated` is term -> grounded meaning, i.e. exactly what the consolidation gate accepted.
    Terms with no representation in the chosen space are OMITTED rather than zero-filled, and the
    caller is expected to report how many that was: a retrieval set silently shrunk by coverage is
    the same defect as a control that excludes nothing.
    """
    if space not in SPACES:
        raise ValueError(f"unknown space {space!r}; known: {SPACES}")
    out: Dict[str, np.ndarray] = {}
    for term in sorted(consolidated):
        # A TERM MUST HAVE EVERY PART THE SPACE ASKS FOR, OR IT IS OMITTED.
        # BUG FOUND BY THE FIRST SMOKE OF exp_cortical_read_consolidated_v1 AND IT WAS MINE: this
        # loop used to append whatever parts existed, so under space="both" a term with only a
        # context profile produced a 256-dim vector while a term with both produced 268, and
        # `np.stack` raised "all input arrays must have the same shape". `cue_vector` ALREADY
        # refused a half-built vector; the index did not. The two sides of the same comparison
        # disagreed about what a vector in this space is.
        parts: List[Optional[np.ndarray]] = []
        if space in ("context", "both"):
            v = context_profiles.get(term)
            parts.append(_unit(v) if v is not None else None)
        if space in ("spoke", "both"):
            v = _spoke_vec(term)
            parts.append(_unit(v) if v is not None else None)
        if not parts or any(p is None for p in parts):
            continue
        # CONCATENATION, NOT SUMMATION, for space="both": the two spaces have different
        # dimensionalities and different meanings per axis, so adding them is not defined. Each
        # part is unit-normalised first so neither space dominates by scale alone. The relative
        # WEIGHTING of hub inputs is UNPINNED in the brain, so equal weight is our choice, stated.
        vec = np.concatenate(parts) if len(parts) > 1 else parts[0]
        u = _unit(vec)
        if u is not None:
            out[term] = u
    return out


def cue_vector(cue_words: Sequence[str], context_profiles: Dict[str, np.ndarray],
               *, space: str = "context", exclude: Sequence[str] = ()) -> Optional[np.ndarray]:
    """A cue built from CONTENT WORDS, in the same space as the index.

    `exclude` masks words out of their own cue. It is not a nicety: without it a cue containing the
    answer retrieves the answer by identity, which measures nothing.
    """
    drop = {w.lower() for w in exclude}
    words = [w.lower() for w in cue_words if w and w.lower() not in drop]
    if not words:
        return None
    parts: List[np.ndarray] = []
    if space in ("context", "both"):
        acc = [context_profiles[w] for w in words if w in context_profiles]
        u = _unit(np.sum(acc, axis=0)) if acc else None
        parts.append(u if u is not None else None)
    if space in ("spoke", "both"):
        acc = [v for v in (_spoke_vec(w) for w in words) if v is not None]
        u = _unit(np.sum(acc, axis=0)) if acc else None
        parts.append(u if u is not None else None)
    if any(p is None for p in parts):
        return None                      # a half-built cue is not comparable to a full index
    vec = np.concatenate(parts) if len(parts) > 1 else parts[0]
    return _unit(vec)


def cortical_recall(cue_words: Sequence[str],
                    consolidated: Dict[str, Optional[str]],
                    context_profiles: Dict[str, np.ndarray],
                    *, space: str = "context", top_k: int = 5,
                    exclude: Sequence[str] = (),
                    index: Optional[Dict[str, np.ndarray]] = None) -> List[CorticalHit]:
    """Retrieve CONSOLIDATED concepts by content similarity to a cue. THE CORTICAL READ.

    This is the route that did not exist. It differs from the episodic route in the two ways CLS
    says matter: it ranks ONLY over what was consolidated (not over everything experienced), and it
    returns the concept's GROUNDED MEANING rather than a raw lemma.
    """
    idx = index if index is not None else build_cortical_index(
        consolidated, context_profiles, space=space)
    if not idx:
        return []
    q = cue_vector(cue_words, context_profiles, space=space, exclude=exclude)
    if q is None:
        return []
    names = sorted(idx)
    M = np.stack([idx[n] for n in names])
    if M.shape[1] != q.shape[0]:
        return []
    sims = M @ q
    order = np.argsort(-sims)[:top_k]
    return [CorticalHit(term=names[i], meaning=consolidated.get(names[i]),
                        score=float(sims[i])) for i in order]


# -------------------------------------------------------------------------------------------
# SELF-TESTS. Each can fail.
# -------------------------------------------------------------------------------------------

def _fixture(seed: int = 7):
    """A tiny synthetic world: 6 consolidated terms with deliberately structured profiles."""
    rng = np.random.default_rng(seed)
    base = {name: rng.normal(size=32) for name in ("ANIMAL", "TOOL", "ABSTRACT")}
    terms = {"dog": "ANIMAL", "cat": "ANIMAL", "hammer": "TOOL", "axe": "TOOL",
             "justice": "ABSTRACT", "freedom": "ABSTRACT"}
    profiles = {w: base[fam] + 0.25 * rng.normal(size=32) for w, fam in terms.items()}
    # cue-only words, NOT consolidated, so the index and the cue vocabulary genuinely differ
    for w, fam in (("puppy", "ANIMAL"), ("chisel", "TOOL"), ("liberty", "ABSTRACT")):
        profiles[w] = base[fam] + 0.25 * rng.normal(size=32)
    consolidated = {w: ("creature" if f == "ANIMAL" else
                        "implement" if f == "TOOL" else "idea") for w, f in terms.items()}
    return consolidated, profiles


def _selftest_retrieves_the_right_family_from_a_partial_cue() -> dict:
    """POSITIVE CONTROL. A cue that never names the target must still retrieve its family.

    The target is masked out of its own cue -- without that the test measures identity lookup and
    could not fail.
    """
    consolidated, profiles = _fixture()
    hits = cortical_recall(["puppy"], consolidated, profiles, space="context", top_k=2)
    assert hits, "cortical_recall returned nothing on a well-formed cue"
    assert hits[0].term in ("dog", "cat"), f"expected an ANIMAL term first, got {hits[0].term}"
    assert hits[0].meaning == "creature", f"meaning not returned: {hits[0]}"
    tool = cortical_recall(["chisel"], consolidated, profiles, space="context", top_k=2)
    assert tool[0].term in ("hammer", "axe"), f"expected a TOOL term first, got {tool[0].term}"
    return {"animal_cue_top": hits[0].term, "animal_cue_meaning": hits[0].meaning,
            "tool_cue_top": tool[0].term, "animal_score": round(hits[0].score, 4)}


def _selftest_ranks_only_consolidated_terms() -> dict:
    """THE CLS DISTINCTION, ASSERTED. A term the gate never accepted must NEVER be returned.

    This is what separates a cortical read from the episodic one: the episodic route ranks over
    everything experienced, this ranks over the distilled subset only.
    """
    consolidated, profiles = _fixture()
    hits = cortical_recall(["puppy", "chisel", "liberty"], consolidated, profiles,
                           space="context", top_k=6)
    returned = {h.term for h in hits}
    leaked = returned - set(consolidated)
    assert not leaked, f"un-consolidated terms leaked into a cortical read: {sorted(leaked)}"
    assert returned, "nothing returned at all, so the check above is vacuous"
    return {"n_returned": len(returned), "index_size": len(consolidated),
            "profile_vocab": len(profiles)}


def _selftest_an_unrelated_cue_does_not_win() -> dict:
    """CAN-FAIL. An ABSTRACT cue must not rank an ANIMAL term above an ABSTRACT one.

    A retrieval that returns the same ordering for every cue is a constant wearing a route's name,
    which is the failure mode this project has shipped before.
    """
    consolidated, profiles = _fixture()
    animal = cortical_recall(["puppy"], consolidated, profiles, space="context", top_k=6)
    abstract = cortical_recall(["liberty"], consolidated, profiles, space="context", top_k=6)
    assert animal[0].term != abstract[0].term, (
        f"both cues returned the same top term ({animal[0].term}) -- the route is cue-independent")
    assert abstract[0].term in ("justice", "freedom"), (
        f"an abstract cue ranked {abstract[0].term} first")
    return {"animal_top": animal[0].term, "abstract_top": abstract[0].term,
            "orderings_differ": [h.term for h in animal] != [h.term for h in abstract]}


def _selftest_masking_actually_masks() -> dict:
    """A cue containing the answer must not retrieve it by identity once excluded."""
    consolidated, profiles = _fixture()
    unmasked = cortical_recall(["dog"], consolidated, profiles, space="context", top_k=1)
    masked = cortical_recall(["dog"], consolidated, profiles, space="context", top_k=1,
                             exclude=["dog"])
    assert unmasked and unmasked[0].term == "dog", (
        "POSITIVE CONTROL FAILED: an unmasked cue did not retrieve itself, so the masked "
        "comparison below proves nothing")
    assert not masked, f"exclusion did not empty a single-word cue: {masked}"
    return {"unmasked_top": unmasked[0].term, "masked_returned": len(masked)}


def _selftest_index_is_shape_homogeneous_under_partial_coverage() -> dict:
    """EVERY vector in an index must have the SAME length, even when coverage is ragged.

    *** THIS TEST EXISTS BECAUSE THE BUG SHIPPED. *** The first smoke of
    `exp_cortical_read_consolidated_v1` died with "all input arrays must have the same shape":
    under space="both" this module required BOTH parts for a CUE but accepted EITHER for the
    INDEX, so a term with only a context profile produced a 256-dim vector and a term with both
    produced 268. The two sides of the same comparison disagreed about what a vector is.

    The fixture is deliberately RAGGED -- real words that have sensorimotor norms mixed with a
    nonce that cannot -- because a fixture with uniform coverage could not have failed.
    """
    profiles = {w: np.ones(8) for w in ("dog", "cat", "zzqxvelmarathrom")}
    consolidated = {"dog": "creature", "cat": "creature", "zzqxvelmarathrom": "nonce"}
    out = {}
    for space in SPACES:
        idx = build_cortical_index(consolidated, profiles, space=space)
        shapes = sorted({tuple(v.shape) for v in idx.values()})
        assert len(shapes) <= 1, f"space={space!r} produced RAGGED index shapes: {shapes}"
        out[space] = {"n_terms": len(idx), "shape": shapes[0] if shapes else None}
        if idx:
            # And it must actually be usable, not merely uniform.
            hits = cortical_recall(["dog"], consolidated, profiles, space=space, top_k=1,
                                   exclude=["dog"], index=idx)
            out[space]["queryable"] = bool(hits) or len(idx) <= 1
    assert out["both"]["n_terms"] < out["context"]["n_terms"], (
        "POSITIVE CONTROL FAILED: the nonce was not dropped from the 'both' index, so this "
        f"fixture has uniform coverage and could not have caught the bug: {out}")
    return out


def run_selftests() -> dict:
    tests = [("index_is_shape_homogeneous_under_partial_coverage",
              _selftest_index_is_shape_homogeneous_under_partial_coverage),
             ("retrieves_the_right_family_from_a_partial_cue",
              _selftest_retrieves_the_right_family_from_a_partial_cue),
             ("ranks_only_consolidated_terms", _selftest_ranks_only_consolidated_terms),
             ("an_unrelated_cue_does_not_win", _selftest_an_unrelated_cue_does_not_win),
             ("masking_actually_masks", _selftest_masking_actually_masks)]
    out: dict = {"_failed": []}
    for name, fn in tests:
        try:
            out[name] = fn()
            out[name]["_ok"] = True
        except AssertionError as e:
            out[name] = {"_ok": False, "error": str(e)}
            out["_failed"].append(name)
    out["_overall"] = "PASS" if not out["_failed"] else "FAIL"
    return out


if __name__ == "__main__":
    import json
    r = run_selftests()
    print(json.dumps(r, indent=2, default=str))
    print("ALL SELF-TESTS PASSED" if r["_overall"] == "PASS" else "SELF-TESTS FAILED")
    raise SystemExit(0 if r["_overall"] == "PASS" else 1)
