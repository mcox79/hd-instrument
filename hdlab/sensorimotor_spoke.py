"""hdlab/sensorimotor_spoke.py -- ORGAN B5. Modality-specific input feeding the hub.

WHAT THIS IS, IN ONE LINE: the substrate reads text, and text is one spoke. This is a second one.

BRAIN CLAIM, AND WHICH PARTS ARE PINNED (ORGAN_MAP B5, notes/PLAN.md 687-693):
  PINNED-BY-EVIDENCE  Modality-specific cortex feeds the anterior temporal hub. Concepts are not
                      built from linguistic co-occurrence alone.
  PINNED-BY-EVIDENCE  Text-only channels recover non-sensorimotor meaning well, SENSORY meaning
                      poorly, and MOTOR meaning minimally (Xu et al. 2025, Nat Hum Behav). This is
                      a published PREDICTION of exactly the ceiling this substrate measured on its
                      own co-occurrence channel, and it is why this organ exists.
  BOUNDING RESULT     A sensory-INDEPENDENT code for object colour exists in congenitally blind and
                      sighted alike (Wang, Men, Gao, Caramazza & Bi 2020, Neuron 107:383-393). So a
                      spoke is NOT the only route to modality knowledge. Do not over-claim it.
  UNPINNED            THE HUB-SPOKE COMBINATION RULE. There is no equation for how spoke evidence
                      combines with the hub's. Every weighting or selection rule here is
                      OUR-INVENTION-BEING-TESTED and is labelled as such. Not a fidelity claim.

WHAT IS SUPPLIED VERSUS LEARNED, STATED PLAINLY. The Lancaster norms are HUMAN RATINGS. They are
admissible under the owner's 2026-08-16 ruling -- a static, offline-built foundation asset with no
LLM at inference -- but the substrate does not GROW this spoke, it is handed one. That is SUPPLY,
not learning, and no result from this organ may be reported as the substrate having learned
perceptual structure.

WHY THIS FILE AND NOT A NEW NORM LOADER. `hdlab/grounded_similarity.py` already loads Lancaster +
Brysbaert, joins them on the single-token intersection and z-scores the 12 dimensions over that
population. This module CALLS it. Authoring a second loader would be islanding, and the
z-scoring is the part that is already right.

WHAT THIS FIXES, AND IT IS A METRIC FIX, NOT A NEW REPRESENTATION. ORGAN_MAP grades B5
RIGHT-OP-WRONG-METRIC, and its evidence is about NEAR pairs specifically: raw cosine reads
sofa/couch 0.968, happy/joyful 0.962, apple/orange 0.952, dog/cat 0.932 -- a synonym and a
same-category sibling land on top of each other. Cosine measures DIRECTION, and after z-scoring
the discriminating signal near the diagonal is largely MAGNITUDE: how strongly a concept loads on
touch, on hand-action, on interoception. Euclidean distance in z-space keeps that; cosine
discards it.

MEASURED, ON THE CONTRAST THAT MATTERS, AND THE FIRST VERSION OF THIS CLAIM WAS WRONG. Tested
across 10 synonym and 10 sibling pairs (scratch/probe_metric_synonym_vs_sibling.py): euclid
separates them by 1.348 pooled SDs, cosine by 0.511. But on CONCRETE-versus-ABSTRACT pairs cosine
wins decisively (ratio 22.8 to euclid's 3.2), and the self-test that first asserted otherwise
FAILED and is the reason this paragraph is precise. Both metrics are exposed and the scoring cell
SWEEPS them rather than adopting one, per "copy the computation, sweep the parameter".

USAGE
  python -m hdlab.sensorimotor_spoke        # self-test, including a can-fail shuffled-norms arm
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import random
import sys
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

METRICS = ("euclid", "cosine")

_cache: Dict[str, Optional[np.ndarray]] = {}


def profile(word: str) -> Optional[np.ndarray]:
    """z-scored 12-dim sensorimotor+concreteness profile, or None if the word has no norms.

    Delegates to grounded_similarity's table so there is exactly ONE join and ONE z-scoring in
    the codebase. Memoized per word because the scoring cell asks for the same words repeatedly.
    """
    w = (word or "").strip().lower()
    if not w:
        return None
    if w in _cache:
        return _cache[w]
    from hdlab.grounded_similarity import grounded_vector
    v = grounded_vector(w)
    out = None if v is None else np.asarray(v, dtype=np.float64)
    _cache[w] = out
    return out


def has_profile(word: str) -> bool:
    return profile(word) is not None


def coverage(words: Iterable[str]) -> dict:
    """How many of these words have norms. REPORTED, never assumed.

    Discipline 16's corollary: a control that excludes nothing is not a control, so any cell
    using this organ must state how many items the norm requirement removed.
    """
    ws = sorted(set((w or "").strip().lower() for w in words if w))
    have = [w for w in ws if has_profile(w)]
    return {"n_words": len(ws), "n_with_profile": len(have),
            "coverage": (len(have) / len(ws)) if ws else 0.0,
            "n_dropped": len(ws) - len(have)}


def distance(word_a: str, word_b: str, metric: str = "euclid") -> Optional[float]:
    """Distance between two words in sensorimotor space. LOWER IS MORE SIMILAR, both metrics.

    `cosine` is returned as 1 - cos so that both metrics order the same direction; that is a
    presentation choice and changes no ranking within a metric.
    """
    if metric not in METRICS:
        raise ValueError(f"unknown metric {metric!r}; known: {METRICS}")
    a, b = profile(word_a), profile(word_b)
    if a is None or b is None:
        return None
    if metric == "euclid":
        return float(np.linalg.norm(a - b))
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return None
    return float(1.0 - (a @ b) / (na * nb))


def nearest(target: str, candidates: Sequence[str], *, metric: str = "euclid",
            profiles: Optional[Dict[str, np.ndarray]] = None) -> Optional[str]:
    """The candidate whose sensorimotor profile is closest to the target's.

    THIS SELECTION RULE IS OUR-INVENTION-BEING-TESTED. The brain's hub-spoke combination rule is
    UNPINNED, so "nearest in spoke space" is a hypothesis about how spoke evidence picks a
    meaning, not a replication of a known computation. Ties break on the sorted candidate name so
    the result is deterministic across processes.

    `profiles` lets a caller supply a substituted table -- which is how the shuffled-norms
    control is built without this function knowing it is being controlled.
    """
    look = (lambda w: profiles.get(w)) if profiles is not None else profile
    t = look(target)
    if t is None:
        return None
    best, best_d = None, float("inf")
    for c in sorted(set(candidates)):
        if c == target:
            continue
        v = look(c)
        if v is None:
            continue
        if metric == "euclid":
            d = float(np.linalg.norm(t - v))
        else:
            nt, nv = float(np.linalg.norm(t)), float(np.linalg.norm(v))
            if nt < 1e-9 or nv < 1e-9:
                continue
            d = float(1.0 - (t @ v) / (nt * nv))
        if d < best_d:
            best, best_d = c, d
    return best


def shuffled_profiles(words: Sequence[str], seed: int) -> Dict[str, np.ndarray]:
    """Each word gets ANOTHER word's profile. The can-fail control for any result from this organ.

    If a sensorimotor arm scores the same with these substituted, the norms are not carrying the
    result and the arm is measuring something else -- the candidate pool, the coverage filter, or
    the marginal frequency of the answers. The MARGINALS are preserved exactly: this is a
    permutation of the profile assignment, not noise.
    """
    ws = [w for w in sorted(set(words)) if has_profile(w)]
    src = list(ws)
    random.Random(seed).shuffle(src)
    # A derangement is not enforced; with n in the thousands the expected number of fixed points
    # is 1, and forcing one would be a bias the real assignment does not have.
    return {w: profile(s) for w, s in zip(ws, src)}


# -------------------------------------------------------------------------------------------
# SELF-TESTS. Each can fail.
# -------------------------------------------------------------------------------------------

def _selftest_loads_and_covers() -> dict:
    cov = coverage(["dog", "cat", "justice", "hammer", "run", "zzqxvelmarathrom"])
    assert cov["n_with_profile"] >= 4, f"norms did not load: {cov}"
    assert not has_profile("zzqxvelmarathrom"), "a nonce word returned a profile"
    v = profile("dog")
    assert v is not None and v.shape == (12,), f"unexpected profile shape: {None if v is None else v.shape}"
    return cov


def _selftest_euclid_separates_synonym_from_sibling() -> dict:
    """The METRIC FIX, measured on the contrast ORGAN_MAP ACTUALLY NAMES.

    *** THE FIRST VERSION OF THIS TEST ASSERTED THE WRONG CONTRAST AND FAILED, WHICH IS WHY IT
    EXISTS. *** It compared dog/cat against dog/justice -- concrete versus abstract -- which BOTH
    metrics ace, and cosine won it (ratio 22.8 to euclid's 3.2). ORGAN_MAP's grade is about NEAR
    pairs only: "raw cosine cannot separate a synonym from a sibling -- sofa/couch 0.968,
    happy/joyful 0.962, apple/orange 0.952, dog/cat 0.932". Separating a synonym from a
    same-category sibling is what a meaning-selection organ has to get right; separating a dog
    from justice is not.

    MEASURED (scratch/probe_metric_synonym_vs_sibling.py, 10 synonym and 10 sibling pairs):
    euclid 1.348 pooled SDs, cosine 0.511. Both statements are true on their own axis -- cosine
    is the better separator far apart, euclid near -- which is precisely why the scoring cell
    SWEEPS both rather than adopting one.

    *** THIS IS A SANITY GATE, NOT EVIDENCE. *** The pairs are fixtures chosen by the author of
    this module, so they fail the "did the items predate the mechanism" test by construction. The
    evidence is the scoring cell against an independent gold, never this.
    """
    synonyms = [("sofa", "couch"), ("happy", "joyful"), ("rock", "stone"), ("car", "automobile"),
                ("boat", "ship"), ("hat", "cap"), ("rug", "carpet"), ("jail", "prison"),
                ("shop", "store"), ("road", "street")]
    siblings = [("apple", "orange"), ("dog", "cat"), ("chair", "table"), ("shirt", "trouser"),
                ("hammer", "screwdriver"), ("cow", "pig"), ("knife", "spoon"), ("bus", "train"),
                ("violin", "trumpet"), ("carrot", "potato")]
    out = {}
    for m in METRICS:
        syn = [d for d in (distance(a, b, metric=m) for a, b in synonyms) if d is not None]
        sib = [d for d in (distance(a, b, metric=m) for a, b in siblings) if d is not None]
        assert len(syn) >= 8 and len(sib) >= 8, (
            f"coverage too thin to judge the metric ({m}): {len(syn)} syn, {len(sib)} sib")
        sm, bm = float(np.mean(syn)), float(np.mean(sib))
        sd = float(np.sqrt((np.var(syn, ddof=1) + np.var(sib, ddof=1)) / 2.0))
        out[m] = {"synonym_mean": round(sm, 4), "sibling_mean": round(bm, 4),
                  "gap_over_pooled_sd": round((bm - sm) / sd, 3) if sd > 1e-12 else None,
                  "n_syn": len(syn), "n_sib": len(sib)}
    assert out["euclid"]["gap_over_pooled_sd"] > 0, (
        "euclidean put SIBLINGS closer than SYNONYMS -- the required direction is reversed")
    assert out["euclid"]["gap_over_pooled_sd"] > out["cosine"]["gap_over_pooled_sd"], (
        "euclidean did NOT separate synonym from sibling better than cosine, so the metric fix "
        f"is not supported and the module must drop that framing: {out}")
    return out


def _selftest_shuffled_norms_destroy_the_ordering() -> dict:
    """THE CAN-FAIL CONTROL FOR THE WHOLE ORGAN, and it is asserted BOTH WAYS.

    Real norms must pick a same-domain candidate for a clearly perceptual target more often than
    a permuted table does. A control that cannot move the number is the defect this project has
    already shipped twice (a no-op scramble, a rate-match that matched nothing).
    """
    targets = ["dog", "hammer", "apple", "chair", "shirt"]
    gold = {"dog": {"cat", "horse"}, "hammer": {"axe", "knife"}, "apple": {"pear", "peach"},
            "chair": {"bench", "sofa"}, "shirt": {"coat", "sock"}}
    distractors = ["justice", "theory", "freedom", "reason", "policy", "concept"]
    pool = sorted({c for s in gold.values() for c in s} | set(distractors))

    real = sum(int(nearest(t, pool, metric="euclid") in gold[t]) for t in targets)
    shuf_scores: List[int] = []
    for s in range(5):
        tbl = shuffled_profiles(pool + targets, seed=s)
        shuf_scores.append(sum(int(nearest(t, pool, metric="euclid", profiles=tbl) in gold[t])
                               for t in targets))
    assert real >= 3, (
        f"POSITIVE CONTROL FAILED: real norms picked a same-domain candidate only {real}/5, so "
        "this test could not have detected the shuffle either way")
    assert real > max(shuf_scores), (
        f"shuffled norms matched or beat real norms ({real} vs {shuf_scores}): the profiles are "
        "not carrying the selection")
    return {"real_hits_of_5": real, "shuffled_hits_of_5": shuf_scores}


def run_selftests() -> dict:
    tests = [("loads_and_covers", _selftest_loads_and_covers),
             ("euclid_separates_synonym_from_sibling",
              _selftest_euclid_separates_synonym_from_sibling),
             ("shuffled_norms_destroy_the_ordering",
              _selftest_shuffled_norms_destroy_the_ordering)]
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
