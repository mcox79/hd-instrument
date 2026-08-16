"""exp_synonym_substitution_metric_v1 -- IF A SYNONYM COUNTS AS SUCCESS, HOW MUCH OF OUR FAILURE
WAS THE METRIC?

THE TRIGGER (BOARD Q12, 2026-08-16, the owner describing their own word-finding, verbatim):
  "If I can't remember the word, i'll give up basically because it's not worth it - I'll use a word
   that means the same thing instead."
and Q10, on what a rejection checks:
  "words with the same meanings have different feelings to use -- 'think' versus 'contemplate' have
   very different feelings"
Q12 says HUMANS DO NOT HAVE TO FIND THE EXACT WORD. Q10 says the substitutes are NOT interchangeable
to the owner either. Both are design input and they pull in opposite directions; this cell measures
where between them our instrument actually sits.

THE PREMISE THAT SENT ME HERE, AND THE CORRECTION THAT CAME BACK
The brief states that every hit@1 number this programme has produced "scores an exact string match
against one gold word". READ OFF DISK, THAT IS NOT WHAT THE INSTRUMENT DOES.
experiments/exp_grounding_readout_known_answer_v1.gold_meaning_set(L) returns a SET -- every lemma
of every synset of L, plus hypernyms two levels up, plus sister terms, plus hyponyms -- and hit@1
counts a hit if the returned word is ANYWHERE in it. MEASURED on this exact pool by
scratch/syn_probe (and recomputed here as CRITERION_STRICTNESS): 55.383 words per item on average,
median 26. The meaning-equivalent criterion the owner describes is therefore ALREADY GRANTED, and
granted an order of magnitude more generously than synonymy.

So the question is not "swap exact for meaning-equivalent". It is A LADDER, and the deliverable is
where WE rise across it and where THE FLOORS rise:

  K0_EXACT_WORD             gold = {L}. Exactly ONE word is correct. "Name the word."
  K1_SUBSTITUTION_ALLOWED   gold = {L} + L's WordNet SYNSET co-lemmas. THE OWNER'S POLICY: the word,
                            or a word that means the same thing. MEASURED strictness ~3-4 words.
  K2_LANDED_CLOSURE         gold = {L} + the landed generous closure (adds hypernyms, sisters,
                            hyponyms, any POS). ~56 words. This is what every landed number used.
  K1_SYN_ONLY / K2_ONLY     the same two, with L MASKED OUT of the pool -- the landed instrument's
                            own eligibility, in which substitution is not merely allowed, it is
                            FORCED. K2_ONLY reproduces the landed 0.0481 / 0.0223 as a regression
                            gate.

THE JUDGE, AND WHY IT IS NOT CIRCULAR
WordNet 3.0 synsets, offline, static, read-only. It is NOT a meaning source for any arm: no arm's
score is computed from WordNet. Our read-out scores cosine in a bag-of-context space; the floors
score character trigrams, shared prefixes, log corpus count, and cosine to the mean anchor
direction. None of them can see the judge. Grading by our own embedding -- "close in our space
counts as close in meaning" -- would be the circularity the brief warns about and is not done
anywhere here. THE ONE HONEST QUALIFICATION, STATED RATHER THAN BURIED: WordNet also participates
in ITEM SELECTION (an item exists only if L has synsets), inherited from the landed harness. That
biases WHICH WORDS ARE TESTED, identically for every arm; it does not feed any arm's score.

NO NUMBER CROSSES A POOL, A CRITERION, OR A POPULATION
The criterion change MOVES THE POPULATION: 37.08% of items have NO synonym in the pool at all and
72.63% have no dominant-sense synonym, so a K1 number and a K2 number computed on "all items" would
be computed on different items. Every cross-criterion delta in this cell is therefore computed on
ONE COMMON ITEM SET, paired, with the SAME scores and the SAME eligibility, with ONLY the gold
matrix changing. That is the single-variable manipulation the question deserves.

POOL LADDER (tools/floor_battery.py, unmodified): OPEN, balanced_candidate_sets K=15 and K=49,
matched_candidate_sets K=15 (secondary; the prior cell's own matched pool failed its oracle check
and this one is re-checked, never inherited).

ABSTENTION WITH FALLBACK (Q12's second half). The owner does not merely tolerate a synonym, they
DECLINE and move on. Operationalised as selective prediction: sort items by the arm's own
confidence, keep the top r, measure accuracy on what is answered. Reported against a RANDOM-ABSTAIN
control at matched coverage (the discipline established by
experiments/exp_metacog_abstain_readout_signal_thresholding_v1, credited). A CONSTANT floor's
confidence is constant, so its curve is flat BY CONSTRUCTION -- a built-in negative control.
WHAT I DO NOT FAKE: "return the best meaning-equivalent instead of the argmax" is not
implementable without consulting the judge at run time, which would be an oracle and would also
violate the no-LLM/no-runtime-lookup rule in spirit. The substitution half of the policy IS the
criterion change; the declining half IS the curve. They are measured separately and labelled.

VALIDITY, READ BEFORE ANY TREATMENT NUMBER (standing rule)
  KA_QUERY_IS_GOLD_VECTOR   plants the answer -> near ceiling in every readable block
  NULL_SCRAMBLED_ANCHORS    permutes anchor->vector -> near THAT block's own chance
  They fail independently (one plants, one permutes; self-test T4 breaks one and leaves the other).
  SATURATION is checked: a loose criterion can push every arm to ceiling, at which point the metric
  separates nothing. Blocks whose treatment arms do not spread are marked unreadable.
  The CONSTANT/PROTOTYPE floor is RECOMPUTED HERE on this population with its own n under all three
  tie conventions. 0.1382 and 0.2070 are NOT imported; they are floors on other populations.

INSTRUMENTATION, NOT A COMPONENT MEASUREMENT. This cell measures a SUCCESS CRITERION. It makes no
neural-systems claim; the supporting biology is BEHAVIOURAL and marked so in the report.

ASCII-only. Nothing under hdlab/, data/foundation/ or any protected path is written or modified.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.floor_battery import (                                               # noqa: E402
    balanced_candidate_sets, constant_prototype_floor, hit_at_1_both_tie_conventions, margin,
    matched_candidate_sets, oracle_constant_scores,
)
# THE ENTIRE ARM SET, THE POOL AND THE SCORER ARE IMPORTED, NOT REBUILT. Same cache, same seeds,
# same code path -> the arms are bit-identical to the ones the landed numbers were computed on and
# the K2 blocks below act as a regression gate on that identity.
import experiments.exp_task_degeneracy_v1 as TD                                 # noqa: E402

ANCHOR_NAME = "exp_synonym_substitution_metric_v1"
OUT_DIR = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)

MASTER_SEED = 20260816          # SAME as TD, deliberately: the K2 blocks must reproduce.
N_BOOT = 10000
K_LIST = (15, 49)
COVERAGE_RATES = (0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 1.00)
KA_CEILING_MIN = TD.KA_CEILING_MIN
SAT_MIN_SPREAD = TD.SAT_MIN_SPREAD

FLOORS = ("F1_TRIGRAM_ONLY_orthographic", "F2_PREFIX_ONLY_orthographic",
          "F3_FREQUENCY_ONLY_constant", "F5_CONSTANT_PROTOTYPE_zero_query_information")
ABSTAIN_ARMS = ("R0_CTX_DENSE_our_read_out", "F1_TRIGRAM_ONLY_orthographic",
                "F2_PREFIX_ONLY_orthographic", "F3_FREQUENCY_ONLY_constant",
                "F5_CONSTANT_PROTOTYPE_zero_query_information", "NULL_SCRAMBLED_ANCHORS")


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1).encode("utf-8"))
    os.replace(tmp, path)


# =================================================================================================
# THE JUDGE -- WordNet, offline, static, read-only. Never consulted by any arm's scorer.
# =================================================================================================
def synset_colemmas(word: str, dominant_only: bool = False, strict: bool = True) -> set:
    """TRUE SYNONYMS: the other lemmas of the synsets `word` belongs to. Same synset means the two
    lemmas are substitutable in at least one sense, which is exactly the owner's 'a word that means
    the same thing'.

    MORPHOLOGY IS REMOVED, AND MORE AGGRESSIVELY THAN THE LANDED HARNESS DOES IT. The harness's own
    _is_variant caps the allowed length difference at 3, which MEASURED means it returns False for
    ('running','run') while returning True for ('runs','run'), ('ran','run'), ('bigger','big') and
    ('thought','think'). A 4-letter inflection could therefore be scored as a MEANING-EQUIVALENT
    SUBSTITUTION, which is precisely the artefact this cell exists to catch. `strict=True` adds a
    deliberately OVER-inclusive second guard; over-removal makes a synonym hit HARDER, so it is
    conservative for any claim that the loosened criterion helps us."""
    from nltk.corpus import wordnet as wn
    w = word.lower()
    ss = wn.synsets(w)
    if dominant_only:
        ss = ss[:1]                       # WordNet orders synsets by sense frequency
    g = set()
    for s in ss:
        for l in s.lemma_names():
            g.add(l.lower())
    g.discard(w)
    bad = _is_variant_strict if strict else _is_variant
    return {x for x in g if not bad(x, w)}


def _is_variant(tok: str, word: str) -> bool:
    import experiments.exp_grounding_readout_known_answer_v1 as C3
    return bool(C3._is_variant(tok, word))


_INFLECTIONS = ("ing", "ed", "es", "s", "er", "est", "ly", "ion", "ions", "ment", "ness", "ance")


def _is_variant_strict(tok: str, word: str) -> bool:
    """The harness's test, PLUS a shared-stem test that catches the 4+ character inflections it
    misses. Deliberately over-inclusive: it will also reject a handful of genuine synonyms that
    happen to share a stem, and that error direction is the safe one here."""
    if _is_variant(tok, word):
        return True
    a, b = (tok, word) if len(tok) <= len(word) else (word, tok)
    if len(a) >= 3 and b.startswith(a) and (len(b) - len(a)) <= 5:
        return True
    for suf in _INFLECTIONS:
        for x, y in ((tok, word), (word, tok)):
            if x.endswith(suf):
                stem = x[: -len(suf)]
                if len(stem) >= 3 and (y.startswith(stem) or stem.startswith(y)):
                    return True
    return False


def landed_closure(word: str) -> set:
    import experiments.exp_grounding_readout_known_answer_v1 as C3
    return set(C3.gold_meaning_set(word.lower()))


# =================================================================================================
# gold matrices
# =================================================================================================
def gold_matrix(index_lists: Sequence[np.ndarray], n_anchors: int, n_items: int,
                E: np.ndarray) -> np.ndarray:
    G = np.zeros((n_anchors, n_items), dtype=bool)
    for i, gi in enumerate(index_lists):
        if len(gi):
            G[gi, i] = True
    return G & E


def paired_criterion_delta(hit_a: np.ndarray, hit_b: np.ndarray, common: np.ndarray,
                           n_boot: int, seed: int) -> Dict:
    """PAIRED bootstrap of (criterion A - criterion B) on ONE COMMON ITEM SET. Same arm, same
    scores, same eligibility; only the gold matrix differs. This is the only comparison in this
    cell that crosses criteria, and it crosses nothing else."""
    idx = np.flatnonzero(common)
    nc = idx.size
    if nc < 30:
        return {"n": int(nc), "insufficient": True}
    rng = np.random.default_rng(seed)
    IDX = rng.integers(0, nc, size=(n_boot, nc))
    a = np.asarray(hit_a, dtype=np.float64)[idx][IDX].mean(axis=1)
    b = np.asarray(hit_b, dtype=np.float64)[idx][IDX].mean(axis=1)
    d = a - b
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    return {"n": int(nc),
            "acc_loose": round(float(np.asarray(hit_a, dtype=np.float64)[idx].mean()), 4),
            "acc_strict": round(float(np.asarray(hit_b, dtype=np.float64)[idx].mean()), 4),
            "rise": round(float(np.mean(d)), 4), "ci95": [round(lo, 4), round(hi, 4)],
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")}


# =================================================================================================
# ABSTENTION WITH FALLBACK -- selective prediction against a RANDOM-abstain control
# =================================================================================================
def confidence_signals(S: np.ndarray, E: np.ndarray) -> Dict[str, np.ndarray]:
    """top1 score and the top1-top2 MARGIN, over the eligible pool only. Both are computed from the
    arm's OWN scores -- no gold, no judge -- so they are usable at run time."""
    Sm = np.where(E, np.asarray(S, dtype=np.float32), -np.inf)
    n = Sm.shape[0]
    # partition, not sort: O(n) and it is all we need. With kth=n-2 every entry at or after n-2 is
    # >= the entry at n-2, so row n-1 is the max and row n-2 is the runner-up.
    part = np.partition(Sm, n - 2, axis=0)[n - 2:, :]
    second, top1 = part[0], part[1]
    marg = np.where(np.isfinite(second) & np.isfinite(top1), top1 - second, np.nan)
    return {"conf_top1": np.where(np.isfinite(top1), top1, np.nan), "conf_margin": marg}


def abstention_curve(hit: np.ndarray, conf: np.ndarray, scored: np.ndarray,
                     rates: Sequence[float], n_boot: int, seed: int) -> Dict:
    """Accuracy against RESPONSE RATE. At response rate r the arm answers the r-fraction of items on
    which its own confidence is highest and declines the rest. The RANDOM-ABSTAIN control keeps a
    random subset of the same size; its expectation is the full-coverage accuracy, and its
    bootstrap band is what a curve must beat to mean anything."""
    idx = np.flatnonzero(scored & np.isfinite(conf))
    n = idx.size
    if n < 50:
        return {"n": int(n), "insufficient": True}
    h = np.asarray(hit, dtype=np.float64)[idx]
    c = np.asarray(conf, dtype=np.float64)[idx]
    rng = np.random.default_rng(seed)
    # TIES MUST BREAK AT RANDOM, NOT BY INDEX. Caught by self-test S4: with a CONSTANT confidence a
    # stable argsort returns the ITEMS IN POOL ORDER, so "the most confident r-fraction" silently
    # became "the first k anchors alphabetically" and the flat control spuriously beat its own
    # random band at 2 of 8 rates. This is the same class of defect as the tie-convention artefact
    # already on record for this instrument, in a new place.
    order = np.lexsort((rng.random(n), -c))
    hs = h[order]
    _u, _cnt = np.unique(c, return_counts=True)
    conf_tie_mass = float((_cnt[_cnt > 1].sum() - (_cnt > 1).sum()) / max(n, 1))
    base = float(h.mean())
    out = {"n_scored": int(n), "accuracy_at_full_response": round(base, 4),
           "confidence_tie_mass": round(conf_tie_mass, 4), "points": []}
    for r in rates:
        k = max(10, int(round(r * n)))
        k = min(k, n)
        acc = float(hs[:k].mean())
        draws = np.array([h[rng.choice(n, size=k, replace=False)].mean() for _ in range(200)])
        rlo, rhi = float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))
        out["points"].append({
            "response_rate": round(k / n, 4), "n_answered": int(k),
            "accuracy": round(acc, 4),
            "random_abstain_band95": [round(rlo, 4), round(rhi, 4)],
            "beats_random": bool(acc > rhi)})
    ranks = np.arange(1, n + 1, dtype=np.float64)
    out["AURC_mean_accuracy_over_all_response_rates"] = round(
        float((np.cumsum(hs) / ranks).mean()), 4)
    out["note"] = ("a CONSTANT floor has constant confidence, so its curve is flat by construction "
                   "and sits inside the random band at every rate -- the built-in negative control.")
    return out


def paired_selective_margin(hit_a: np.ndarray, conf_a: np.ndarray, hit_b: np.ndarray,
                            conf_b: np.ndarray, scored: np.ndarray, rate: float,
                            n_boot: int, seed: int) -> Dict:
    """Arm A vs arm B AT THE SAME RESPONSE RATE, each answering its own most-confident r-fraction.
    NOT paired item-wise (the two arms answer different items by design), so this is a bootstrap of
    the difference of two selective accuracies over the SAME underlying item population."""
    idx = np.flatnonzero(scored)
    n = idx.size
    if n < 50:
        return {"insufficient": True}
    ha, ca = np.asarray(hit_a, np.float64)[idx], np.asarray(conf_a, np.float64)[idx]
    hb, cb = np.asarray(hit_b, np.float64)[idx], np.asarray(conf_b, np.float64)[idx]
    k = max(10, int(round(rate * n)))
    rng = np.random.default_rng(seed)
    d = np.empty(n_boot // 10, dtype=np.float64)
    for t in range(d.size):
        s = rng.integers(0, n, size=n)
        # ties broken at random inside every resample, for the same reason as in abstention_curve
        oa = np.lexsort((rng.random(n), -np.nan_to_num(ca[s], nan=-np.inf)))[:k]
        ob = np.lexsort((rng.random(n), -np.nan_to_num(cb[s], nan=-np.inf)))[:k]
        d[t] = ha[s][oa].mean() - hb[s][ob].mean()
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    return {"response_rate": round(rate, 4), "n_answered": int(k),
            "point": round(float(np.mean(d)), 4), "ci95": [round(lo, 4), round(hi, 4)],
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> dict:
    res: dict = {"reused_selftest_exp_task_degeneracy_v1": "run below"}

    # S1 -- THE JUDGE fires where it must and not where it must not, and is STRICTLY TIGHTER than
    # the landed closure. If synonyms are not a subset of the landed gold, the ladder is not nested
    # and every delta below is meaningless.
    syn_dog = synset_colemmas("dog")
    land_dog = landed_closure("dog")
    assert "domestic_dog" in syn_dog or "canis_familiaris" in syn_dog, (
        "synset judge missed a true synonym of dog: %r" % sorted(syn_dog)[:20])
    assert "puppy" not in syn_dog, "synset judge leaked a HYPONYM into the synonym set"
    assert "canine" not in syn_dog, "synset judge leaked a HYPERNYM into the synonym set"
    assert "puppy" in land_dog and "canine" in land_dog, "landed closure changed under us"
    assert syn_dog <= land_dog, "the ladder is NOT nested: a synonym is not in the landed closure"
    assert "dog" not in syn_dog and "dogs" not in syn_dog, "judge returned the word itself"
    syn_big = synset_colemmas("big")
    assert "large" in syn_big, "synset judge missed big->large"
    dom = synset_colemmas("dog", dominant_only=True)
    assert dom <= syn_dog, "dominant-sense synonyms are not a subset of all-sense synonyms"
    res["S1_judge"] = {"n_syn_dog": len(syn_dog), "n_landed_dog": len(land_dog),
                       "nested": True, "n_dominant_dog": len(dom),
                       "sample_syn_dog": sorted(syn_dog)[:6]}

    # S2 -- MORPHOLOGY. The landed harness's guard is MEASURED here rather than assumed, because it
    # has a real hole, and the strict guard is asserted to close it without eating true synonymy.
    harness = {p: _is_variant(*p) for p in (("running", "run"), ("runs", "run"), ("ran", "run"),
                                            ("dogs", "dog"), ("bigger", "big"),
                                            ("thought", "think"), ("canine", "dog"),
                                            ("large", "big"))}
    assert harness[("running", "run")] is False, (
        "the landed harness's variant hole has been fixed elsewhere -- this cell's justification "
        "for a strict guard must be re-read before it is quoted")
    assert harness[("runs", "run")] and harness[("ran", "run")] and harness[("dogs", "dog")]
    assert not harness[("canine", "dog")] and not harness[("large", "big")]
    assert _is_variant_strict("running", "run"), "strict guard missed a 4-letter inflection"
    for good in (("large", "big"), ("canine", "dog"), ("contemplate", "think")):
        assert not _is_variant_strict(*good), "strict guard ate a true synonym: %r" % (good,)
    res["S2_variant_removal"] = {
        "landed_harness_results": {"|".join(k): v for k, v in harness.items()},
        "THE_HOLE": "the landed guard returns False for ('running','run') because its length-delta "
                    "rule caps at 3. Closed here by _is_variant_strict.",
        "strict_guard_closes_it_without_eating_true_synonymy": True}

    # S3 -- the criterion delta is PAIRED, is zero when the two criteria agree, and is positive and
    # CI-separated when the loose criterion genuinely admits more.
    rng = np.random.default_rng(4)
    strict = (rng.random(2000) < 0.05)
    loose = strict | (rng.random(2000) < 0.08)
    common = np.ones(2000, dtype=bool)
    d_same = paired_criterion_delta(strict, strict, common, 2000, 1)
    assert d_same["rise"] == 0.0 and d_same["band"] == "NOT_SEPARATED", (
        "identical criteria produced a delta: %r" % d_same)
    d_real = paired_criterion_delta(loose, strict, common, 2000, 1)
    assert d_real["band"] == "ABOVE" and d_real["rise"] > 0.05, "paired delta missed a real rise"
    res["S3_criterion_delta"] = {"identical_gives_zero": True, "real_rise_detected": d_real["rise"]}

    # S4 -- ABSTENTION. A curve driven by a signal that KNOWS must rise; a curve driven by a
    # CONSTANT must stay inside the random band at every rate. Both halves are required: a metric
    # that only ever goes up is not measuring selectivity.
    n = 3000
    truth = (rng.random(n) < 0.20)
    good_conf = truth.astype(np.float64) + 0.35 * rng.standard_normal(n)
    flat_conf = np.full(n, 0.5)
    sc = np.ones(n, dtype=bool)
    cg = abstention_curve(truth, good_conf, sc, COVERAGE_RATES, 2000, 3)
    cf = abstention_curve(truth, flat_conf, sc, COVERAGE_RATES, 2000, 3)
    assert cg["points"][0]["accuracy"] > 3.0 * cg["accuracy_at_full_response"], (
        "informative confidence did not lift selective accuracy: %r" % cg["points"][0])
    assert any(p["beats_random"] for p in cg["points"]), "informative curve never beat random"
    n_flat_beats = sum(p["beats_random"] for p in cf["points"])
    assert n_flat_beats <= 1, (
        "a CONSTANT confidence beat the random-abstain band at %d of %d rates -- the control is "
        "broken: %r" % (n_flat_beats, len(cf["points"]), cf))
    assert abs(cf["AURC_mean_accuracy_over_all_response_rates"]
               - cf["accuracy_at_full_response"]) < 0.03, (
        "a CONSTANT confidence produced a sloped curve: %r" % cf)
    assert cf["confidence_tie_mass"] > 0.99, "tie mass not detected on an all-ties signal"
    res["S4_abstention"] = {"informative_at_r0.05": cg["points"][0]["accuracy"],
                            "base": cg["accuracy_at_full_response"],
                            "flat_control_rates_beating_random": int(n_flat_beats),
                            "flat_control_AURC_vs_base": [
                                cf["AURC_mean_accuracy_over_all_response_rates"],
                                cf["accuracy_at_full_response"]]}

    # S5 -- confidence signals are computed over the ELIGIBLE pool only and the margin is the real
    # top1-top2 gap.
    S = np.array([[5.0, 1.0], [3.0, 9.0], [4.0, 2.0]], dtype=np.float32)
    E = np.array([[True, True], [False, True], [True, True]], dtype=bool)
    cs = confidence_signals(S, E)
    assert list(cs["conf_top1"]) == [5.0, 9.0], "top1 ignored the eligibility mask"
    assert list(cs["conf_margin"]) == [1.0, 7.0], "margin wrong: %r" % cs["conf_margin"]
    res["S5_confidence_signals"] = True

    # S6 -- gold_matrix respects eligibility (a masked anchor can never be a correct answer).
    G = gold_matrix([np.array([1]), np.array([0, 2])], 3, 2, E)
    assert not G[1, 0], "gold_matrix admitted an ineligible anchor"
    assert G[0, 1] and G[2, 1]
    res["S6_gold_matrix_respects_eligibility"] = True

    # S7 -- the imported harness's own suite, including its saturation guard and its independence
    # demonstration. Not restated here; run.
    res["reused_selftest_exp_task_degeneracy_v1"] = TD.self_test()

    print("[selftest] PASS " + json.dumps({k: v for k, v in res.items()
                                           if k != "reused_selftest_exp_task_degeneracy_v1"}),
          flush=True)
    return res


# =================================================================================================
# main run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid,
                 "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
                 "RULER_MODE_GATE": TD.ruler_mode_gate(),
                 "cache": TD.build_cache_if_missing()}
    C = TD.load_cache()
    aux = TD.load_aux(C)
    rep["aux_source"] = aux.get("source", "?")
    anchors, mat, mat_ok, keep = C["anchors"], C["mat"], C["mat_ok"], C["keep"]
    n_anchors, n_items = len(anchors), len(C["L_words"])
    C["qidx"] = np.array([C["pos"].get(w, 0) for w in C["L_words"]], dtype=np.int64)
    pos = C["pos"]
    print("[load] n_anchors=%d n_items=%d keep=%d  %.0fs"
          % (n_anchors, n_items, int(keep.sum()), time.time() - t0), flush=True)

    # ---- ELIGIBILITY: two variants -----------------------------------------------------------
    # E_EXCL is the LANDED instrument: L and its morphological variants are masked out, so the
    # system CANNOT name the word and substitution is FORCED.
    # E_SELF puts L back in the pool, which is the only way an EXACT-WORD criterion is scorable.
    E_EXCL = np.zeros((n_anchors, n_items), dtype=bool)
    for i in range(n_items):
        if keep[i]:
            E_EXCL[:, i] = mat_ok
            if len(C["excl"][i]):
                E_EXCL[C["excl"][i], i] = False
    E_SELF = np.zeros((n_anchors, n_items), dtype=bool)
    for i in range(n_items):
        if keep[i]:
            E_SELF[:, i] = mat_ok
    print("[pool] eligibility built  %.0fs" % (time.time() - t0), flush=True)

    # ---- THE CRITERION LADDER, built from the judge --------------------------------------------
    self_idx = np.full(n_items, -1, dtype=np.int64)
    g_syn: List[np.ndarray] = []
    g_dom: List[np.ndarray] = []
    g_land: List[np.ndarray] = []
    n_syn_raw, n_dom_raw, n_land_raw = [], [], []
    n_strict_removed_in_pool, ex_strict_removed = 0, []
    for i, w in enumerate(C["L_words"]):
        if not keep[i]:
            g_syn.append(np.zeros(0, np.int64)); g_dom.append(np.zeros(0, np.int64))
            g_land.append(np.zeros(0, np.int64))
            continue
        L = str(w).lower()
        self_idx[i] = pos.get(L, -1)
        s_all, s_dom, s_land = synset_colemmas(L), synset_colemmas(L, True), landed_closure(L)
        # MEASURE the strict guard's bite: co-lemmas that the LANDED guard would have let through
        # as "meaning-equivalent" and that are actually morphology.
        for extra in (synset_colemmas(L, strict=False) - s_all):
            if extra in pos:
                n_strict_removed_in_pool += 1
                if len(ex_strict_removed) < 25:
                    ex_strict_removed.append("%s~%s" % (L, extra))
        n_syn_raw.append(len(s_all)); n_dom_raw.append(len(s_dom)); n_land_raw.append(len(s_land))
        g_syn.append(np.array(sorted(pos[g] for g in s_all if g in pos), dtype=np.int64))
        g_dom.append(np.array(sorted(pos[g] for g in s_dom if g in pos), dtype=np.int64))
        g_land.append(np.array(sorted(pos[g] for g in s_land if g in pos), dtype=np.int64))
    print("[judge] criterion ladder built  %.0fs" % (time.time() - t0), flush=True)

    G_SYN_EXCL = gold_matrix(g_syn, n_anchors, n_items, E_EXCL)
    G_LAND_EXCL = gold_matrix(g_land, n_anchors, n_items, E_EXCL)
    G_DOM_EXCL = gold_matrix(g_dom, n_anchors, n_items, E_EXCL)

    SELFM = np.zeros((n_anchors, n_items), dtype=bool)
    for i in range(n_items):
        if keep[i] and self_idx[i] >= 0:
            SELFM[self_idx[i], i] = True
    SELFM &= E_SELF
    G_EXACT_SELF = SELFM.copy()
    G_SYN_SELF = (gold_matrix(g_syn, n_anchors, n_items, E_SELF) | SELFM)
    G_LAND_SELF = (gold_matrix(g_land, n_anchors, n_items, E_SELF) | SELFM)

    # POPULATIONS. Named, and never mixed.
    POP_ALL = keep & G_LAND_EXCL.any(axis=0)            # the landed population, n ~= 3994
    POP_SYN = POP_ALL & G_SYN_EXCL.any(axis=0)          # items that HAVE a synonym in the pool
    POP_DOM = POP_ALL & G_DOM_EXCL.any(axis=0)
    POP_SELF = keep & G_EXACT_SELF.any(axis=0)          # items whose own word is in the pool
    POP_SELF_SYN = POP_SELF & G_SYN_EXCL.any(axis=0)    # the COMMON set for the K0/K1/K2 ladder

    rep["CRITERION_STRICTNESS_how_many_words_count_as_correct_per_item"] = {
        "METHOD": "counted on THIS pool, over the anchors actually eligible -- a criterion is only "
                  "as loose as the words it can actually award.",
        "K0_EXACT_WORD": {"mean": 1.0, "median": 1.0,
                          "note": "one word by definition. Scorable only with L in the pool; "
                                  "MEASURED coverage below."},
        "K1_SUBSTITUTION_ALLOWED_self_plus_synonyms": {
            "mean_in_pool": round(float((G_SYN_SELF | SELFM).sum(axis=0)[POP_SELF].mean()), 3),
            "median_in_pool": float(np.median((G_SYN_SELF | SELFM).sum(axis=0)[POP_SELF])),
            "mean_raw_wordnet_before_pool_restriction": round(float(np.mean(n_syn_raw)), 3)},
        "K1_SYN_ONLY_synonyms_with_the_word_masked_out": {
            "mean_in_pool": round(float(G_SYN_EXCL.sum(axis=0)[POP_ALL].mean()), 3),
            "median_in_pool": float(np.median(G_SYN_EXCL.sum(axis=0)[POP_ALL])),
            "frac_items_with_NO_synonym_in_pool": round(
                float(1.0 - (G_SYN_EXCL.any(axis=0)[POP_ALL]).mean()), 4)},
        "K1_DOMINANT_SENSE_ONLY": {
            "mean_in_pool": round(float(G_DOM_EXCL.sum(axis=0)[POP_ALL].mean()), 3),
            "frac_items_with_NO_dominant_sense_synonym_in_pool": round(
                float(1.0 - (G_DOM_EXCL.any(axis=0)[POP_ALL]).mean()), 4),
            "note": "reported for completeness and NOT used as a primary criterion: it is unscorable "
                    "for most items, so it would silently change the population."},
        "K2_LANDED_CLOSURE": {
            "mean_in_pool": round(float(G_LAND_EXCL.sum(axis=0)[POP_ALL].mean()), 3),
            "median_in_pool": float(np.median(G_LAND_EXCL.sum(axis=0)[POP_ALL])),
            "mean_raw_wordnet_before_pool_restriction": round(float(np.mean(n_land_raw)), 3)},
        "MORPHOLOGY_GUARD_BITE": {
            "n_colemma_slots_in_pool_removed_by_the_STRICT_guard": int(n_strict_removed_in_pool),
            "examples_word_TILDE_rejected_colemma": ex_strict_removed,
            "why": "the landed harness's _is_variant caps the allowed length delta at 3 and so "
                   "MEASURED returns False for ('running','run'). Without the strict guard these "
                   "slots would have been scoreable as MEANING-EQUIVALENT SUBSTITUTIONS when they "
                   "are inflections. Over-removal makes a hit harder, so it is conservative."},
        "THE_READING": "the SYNONYM criterion is genuinely TIGHT. The LANDED criterion, which every "
                       "hit@1 in this programme has used, is the loose one -- by an order of "
                       "magnitude. Any claim that our numbers are low because the metric demands "
                       "one exact word has to survive this table first.",
        "POPULATIONS": {
            "POP_ALL_landed": int(POP_ALL.sum()), "POP_SYN": int(POP_SYN.sum()),
            "POP_DOM": int(POP_DOM.sum()), "POP_SELF": int(POP_SELF.sum()),
            "POP_SELF_SYN_the_common_set_for_the_ladder": int(POP_SELF_SYN.sum()),
            "why_this_matters": "the criterion change MOVES the population. Every cross-criterion "
                                "delta below is computed on ONE of these sets, named beside it."},
    }
    print("[judge] strictness: syn_in_pool_mean=%.3f landed_in_pool_mean=%.3f POP_SYN=%d POP_SELF_SYN=%d"
          % (G_SYN_EXCL.sum(axis=0)[POP_ALL].mean(), G_LAND_EXCL.sum(axis=0)[POP_ALL].mean(),
             POP_SYN.sum(), POP_SELF_SYN.sum()), flush=True)

    # ---- ARMS: imported wholesale, bit-identical to the landed run -----------------------------
    f5 = constant_prototype_floor(mat, mat_ok)
    from experiments import exp_meaning_lift_population_code_v1 as LIFT
    X, cov = TD.norms_for(anchors, TD.NORM_SEED)
    grd = LIFT.lift_kcap(X, 1024, TD.NORM_SEED, TD.GRD_FRAC, True, True).astype(np.float32)
    ST = TD.static_arms(C, aux, f5, grd)
    rep["grounded_channel_coverage"] = round(float(cov.mean()), 4)
    rep["CONSTANT_FLOOR_RECOMPUTED_HERE_not_imported"] = {
        "source": "tools.floor_battery.constant_prototype_floor(mat, mat_ok) on THIS population",
        "top_anchor_by_constant_score": anchors[int(np.argmax(np.where(np.isfinite(f5), f5,
                                                                       -np.inf)))],
        "note": "0.1382 and 0.2070 are floors on OTHER populations and are deliberately NOT "
                "imported. Every constant-floor number below is computed here with this "
                "population's own n, under all three tie conventions."}

    # ---- designated golds + de-biased pools, PER CRITERION -------------------------------------
    def designate(G: np.ndarray, km: np.ndarray, seed: int) -> np.ndarray:
        r = np.random.default_rng(seed)
        d = np.full(n_items, -1, dtype=np.int64)
        for i in np.flatnonzero(km):
            gi = np.flatnonzero(G[:, i])
            if gi.size:
                d[i] = int(gi[r.integers(0, gi.size)])
        return d

    # SAME SEED AS THE LANDED RUN for the K2 designation, so the K2 balanced blocks are a
    # regression gate rather than a fresh draw.
    des_land = designate(G_LAND_EXCL, POP_ALL, MASTER_SEED + 5)
    des_syn = designate(G_SYN_EXCL, POP_SYN, MASTER_SEED + 5)

    def _elig_from_cand(cand: np.ndarray, ok: np.ndarray, K: int) -> np.ndarray:
        E = np.zeros((n_anchors, n_items), dtype=bool)
        rows = cand[ok]
        cols = np.repeat(np.flatnonzero(ok)[:, None], K + 1, axis=1)
        E[rows.ravel(), cols.ravel()] = True
        return E

    blocks: Dict[str, Dict] = {}

    def add(name: str, E: np.ndarray, G: np.ndarray, km: np.ndarray, chance: float, rank: bool,
            des: np.ndarray, what: str) -> None:
        blocks[name] = {"E": E, "GOLD": G, "keep": km, "chance": float(chance), "rank": rank,
                        "designated": des, "what": what}

    n_el_excl = E_EXCL.sum(axis=0)
    ch_land = float(np.mean(G_LAND_EXCL[:, POP_ALL].sum(axis=0) / np.maximum(n_el_excl[POP_ALL], 1)))
    ch_syn = float(np.mean(G_SYN_EXCL[:, POP_SYN].sum(axis=0) / np.maximum(n_el_excl[POP_SYN], 1)))
    n_el_self = E_SELF.sum(axis=0)
    ch_ex = float(np.mean(G_EXACT_SELF[:, POP_SELF_SYN].sum(axis=0)
                          / np.maximum(n_el_self[POP_SELF_SYN], 1)))
    ch_s1 = float(np.mean(G_SYN_SELF[:, POP_SELF_SYN].sum(axis=0)
                          / np.maximum(n_el_self[POP_SELF_SYN], 1)))
    ch_s2 = float(np.mean(G_LAND_SELF[:, POP_SELF_SYN].sum(axis=0)
                          / np.maximum(n_el_self[POP_SELF_SYN], 1)))

    add("OPEN_K2_LANDED_selfExcluded_POPALL", E_EXCL, G_LAND_EXCL, POP_ALL, ch_land, True, des_land,
        "THE LANDED INSTRUMENT EXACTLY. Open pool, L masked out, generous WordNet closure. "
        "REGRESSION GATE: must reproduce 0.0481 exact-key / 0.0223 partial-cue.")
    add("OPEN_K1_SYNONLY_selfExcluded_POPSYN", E_EXCL, G_SYN_EXCL, POP_SYN, ch_syn, True, des_syn,
        "Open pool, L masked out, ONLY true synset synonyms count. Substitution is FORCED and the "
        "criterion is TIGHT. Population is the items that have a synonym in the pool.")
    # THE LADDER: identical pool (self-eligible), identical items, ONLY the gold changes.
    add("LADDER_K0_EXACT_WORD_selfEligible", E_SELF, G_EXACT_SELF, POP_SELF_SYN, ch_ex, True,
        designate(G_EXACT_SELF, POP_SELF_SYN, MASTER_SEED + 5),
        "THE LADDER, RUNG 1. L is IN the pool and ONLY L is correct: name the word. Analytically "
        "PINNED in EXACT_KEY (the query IS L's own stored vector) -- read PARTIAL_CUE only.")
    add("LADDER_K1_SUBSTITUTION_ALLOWED_selfEligible", E_SELF, G_SYN_SELF, POP_SELF_SYN, ch_s1,
        True, designate(G_SYN_SELF, POP_SELF_SYN, MASTER_SEED + 5),
        "THE LADDER, RUNG 2. THE OWNER'S POLICY: L or a word that means the same thing. Same pool, "
        "same items, same scores as rung 1 -- only the gold matrix changes.")
    add("LADDER_K2_LANDED_CLOSURE_selfEligible", E_SELF, G_LAND_SELF, POP_SELF_SYN, ch_s2, True,
        designate(G_LAND_SELF, POP_SELF_SYN, MASTER_SEED + 5),
        "THE LADDER, RUNG 3. L or anything in the landed generous closure. Same pool, same items.")

    ks = K_LIST if grid == "full" else K_LIST[:1]
    gl_land = [np.flatnonzero(G_LAND_EXCL[:, i]) for i in range(n_items)]
    gl_syn = [np.flatnonzero(G_SYN_EXCL[:, i]) for i in range(n_items)]
    for K in ks:
        cand, _g = balanced_candidate_sets(des_land, gl_land, C["excl"], POP_ALL, K,
                                           MASTER_SEED + 17 + K)
        ok = cand[:, 0] >= 0
        E_B = _elig_from_cand(cand, ok, K)
        assert int((E_B & G_LAND_EXCL).sum(axis=0)[ok].max()) == 1, "K2 balanced pool has 2 golds"
        add("BAL_K%d_K2_LANDED" % K, E_B, G_LAND_EXCL, ok, 1.0 / (K + 1), False, des_land,
            "DE-BIASED pool (no constant ranking can beat chance %.4f), LANDED criterion. Regression "
            "gate against the prior cell's de-biased numbers." % (1.0 / (K + 1)))
        cand2, _g2 = balanced_candidate_sets(des_syn, gl_syn, C["excl"], POP_SYN, K,
                                             MASTER_SEED + 17 + K)
        ok2 = cand2[:, 0] >= 0
        E_B2 = _elig_from_cand(cand2, ok2, K)
        assert int((E_B2 & G_SYN_EXCL).sum(axis=0)[ok2].max()) == 1, "K1 balanced pool has 2 golds"
        add("BAL_K%d_K1_SYNONLY" % K, E_B2, G_SYN_EXCL, ok2, 1.0 / (K + 1), False, des_syn,
            "DE-BIASED pool, SYNONYM criterion. THE DECIDING BLOCK: constants are dead by "
            "construction and only a true meaning-equivalent counts.")

    K_D = ks[0]
    cand_d, _gd, dmatch = matched_candidate_sets(des_syn, gl_syn, C["excl"], POP_SYN, K_D,
                                                 MASTER_SEED + 31,
                                                 ST["F1_TRIGRAM_ONLY_orthographic"])
    okd = cand_d[:, 0] >= 0
    E_D = _elig_from_cand(cand_d, okd, K_D)
    assert int((E_D & G_SYN_EXCL).sum(axis=0)[okd].max()) == 1, "matched pool has 2 golds"
    add("MATCHED_K%d_K1_SYNONLY" % K_D, E_D, G_SYN_EXCL, okd, 1.0 / (K_D + 1), False, des_syn,
        "SECONDARY, STRICTER: as balanced, plus distractors matched to the gold on trigram "
        "similarity. Its own ORACLE arm is re-read here, NEVER inherited -- the prior cell's "
        "matched pool failed exactly this check.")
    rep["matched_pool_match_diagnostics"] = dmatch
    print("[blocks] %d conditions built  %.0fs" % (len(blocks), time.time() - t0), flush=True)

    # ---- score every block in both regimes -----------------------------------------------------
    ORACLE, KAS, _ka_cache = {}, {}, {}
    for bname, cfg in blocks.items():
        kk = np.flatnonzero(cfg["keep"])
        restricted = bname.startswith(("BAL_", "MATCHED_"))
        ORACLE[bname] = TD.col(oracle_constant_scores(
            n_anchors, [np.flatnonzero(cfg["GOLD"][:, i]) for i in kk],
            ([np.flatnonzero(cfg["E"][:, i]) for i in kk] if restricted else None)))
        # KA depends ONLY on the designated-gold vector, and several blocks share a designation.
        # Deduplicated by the designation itself: 13 blocks would otherwise hold 13 dense
        # [n_anchors, n_items] matrices for an arm that is bit-identical across most of them.
        dkey = cfg["designated"].tobytes()
        if dkey not in _ka_cache:
            _ka_cache[dkey] = TD.known_answer_arm(C, cfg["designated"])
        KAS[bname] = _ka_cache[dkey]
    print("[oracle+KA] %d distinct known-answer arms for %d blocks  %.0fs"
          % (len(_ka_cache), len(blocks), time.time() - t0), flush=True)

    results: Dict[str, Dict] = {}
    hits_store: Dict[Tuple[str, str, str], np.ndarray] = {}     # (block, regime, arm) -> hit_exp
    scored_store: Dict[Tuple[str, str, str], np.ndarray] = {}
    conf_store: Dict[Tuple[str, str, str], Dict[str, np.ndarray]] = {}

    for regime in ("EXACT_KEY", "PARTIAL_CUE"):
        arms_base = TD.build_arms(C, ST, regime)
        for bname, cfg in blocks.items():
            arms = dict(arms_base)
            arms["KA_QUERY_IS_GOLD_VECTOR"] = KAS[bname]
            arms["ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor"] = ORACLE[bname]
            key = "%s|%s" % (bname, regime)
            results[key] = TD.score_condition(key, cfg["E"], cfg["GOLD"], cfg["keep"], arms,
                                              cfg["chance"], bool(cfg["rank"]), FLOORS)
            results[key]["condition_note"] = cfg["what"]
            results[key]["POPULATION"] = int(np.asarray(cfg["keep"]).sum())
            # CEILING / IDENTITY GUARD. The spread-based saturation check inherited from the prior
            # cell CANNOT catch this: on a self-eligible pool the lexical channels compare L to
            # ITSELF and score exactly 1.0000, while the constant floors stay near zero, so the
            # spread is enormous and the guard passes a block in which four "floors" are identity
            # lookups. Named explicitly here rather than left for a reader to notice.
            A = results[key]["hit_at_1_TIE_CORRECTED_primary"]
            pinned = sorted(k for k, v in A.items()
                            if v >= 0.99 and not k.startswith("KA_"))
            if pinned:
                results[key]["VOID_IDENTITY_LOOKUP_ARMS"] = pinned
                results[key]["NO_FLOOR_COMPARISON_MAY_BE_READ_FROM_THIS_BLOCK"] = (
                    "these arms sit at the instrument ceiling because L is IN the eligible pool and "
                    "their query is derived from L itself: the trigram channel matches L's own "
                    "spelling, the prefix channel matches L's own prefix, the grounded channel "
                    "matches L's own norms. They are not floors here, they are self-matches. Only "
                    "arms whose query is INDEPENDENT of L (the context read-out under PARTIAL_CUE) "
                    "carry information in this block.")
            if bname.startswith("LADDER_") and regime == "EXACT_KEY":
                results[key]["PINNED_NOT_READ"] = (
                    "in EXACT_KEY the query IS L's own stored vector and L is eligible, so the "
                    "argmax returns L by construction. Reported as a plumbing diagnostic; NO "
                    "criterion claim is taken from this block.")
            # retain per-item hit vectors for the criterion ladder and the abstention curves
            keep_arms = set(ABSTAIN_ARMS) | {"G_GROUNDED_KCAP_f0.100_lexical",
                                             "FUSE_ctx_SPELL", "FUSE_ctx_SPELL_GRD",
                                             "ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor"}
            for a in keep_arms:
                if a not in arms:
                    continue
                h = hit_at_1_both_tie_conventions(arms[a], cfg["E"], cfg["GOLD"])
                hits_store[(bname, regime, a)] = h["hit_exp"]
                scored_store[(bname, regime, a)] = h["scored"] & np.asarray(cfg["keep"], bool)
                if a in ABSTAIN_ARMS and regime == "PARTIAL_CUE" and bname in (
                        "OPEN_K2_LANDED_selfExcluded_POPALL", "OPEN_K1_SYNONLY_selfExcluded_POPSYN",
                        "LADDER_K0_EXACT_WORD_selfEligible",
                        "LADDER_K1_SUBSTITUTION_ALLOWED_selfEligible"):
                    conf_store[(bname, regime, a)] = confidence_signals(arms[a], cfg["E"])
            del arms
        del arms_base
    rep["RESULTS_BY_BLOCK"] = results
    print("[score] all blocks scored  %.0fs" % (time.time() - t0), flush=True)

    # ---- THE DELIVERABLE: how much do WE rise, and how much do THE FLOORS rise? -----------------
    ladder_arms = [a for a in ("R0_CTX_DENSE_our_read_out",) + tuple(FLOORS)
                   + ("G_GROUNDED_KCAP_f0.100_lexical", "FUSE_ctx_SPELL_GRD",
                      "ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", "NULL_SCRAMBLED_ANCHORS")]
    ladder: Dict[str, Dict] = {}
    common_ladder = POP_SELF_SYN.copy()
    for a in ladder_arms:
        k0 = ("LADDER_K0_EXACT_WORD_selfEligible", "PARTIAL_CUE", a)
        k1 = ("LADDER_K1_SUBSTITUTION_ALLOWED_selfEligible", "PARTIAL_CUE", a)
        k2 = ("LADDER_K2_LANDED_CLOSURE_selfEligible", "PARTIAL_CUE", a)
        if k0 not in hits_store:
            continue
        ladder[a] = {
            "K0_EXACT_WORD": round(float(hits_store[k0][common_ladder].mean()), 4),
            "K1_SUBSTITUTION_ALLOWED": round(float(hits_store[k1][common_ladder].mean()), 4),
            "K2_LANDED_CLOSURE": round(float(hits_store[k2][common_ladder].mean()), 4),
            "RISE_K1_minus_K0": paired_criterion_delta(hits_store[k1], hits_store[k0],
                                                       common_ladder, N_BOOT, MASTER_SEED + 41),
            "RISE_K2_minus_K1": paired_criterion_delta(hits_store[k2], hits_store[k1],
                                                       common_ladder, N_BOOT, MASTER_SEED + 42),
            "RISE_K2_minus_K0": paired_criterion_delta(hits_store[k2], hits_store[k0],
                                                       common_ladder, N_BOOT, MASTER_SEED + 43)}
    rep["LADDER_SELF_ELIGIBLE_DIAGNOSTIC_ONLY"] = {
        "REGIME": "PARTIAL_CUE (the real operating regime). EXACT_KEY is pinned on this pool.",
        "POPULATION": int(common_ladder.sum()),
        "WHAT_IS_HELD_FIXED": "identical items, identical eligibility (L in the pool), identical "
                              "scores. ONLY the gold matrix changes between rungs.",
        "WHY_THIS_IS_A_DIAGNOSTIC_AND_NOT_THE_DELIVERABLE": "putting L back in the pool -- the only "
            "way an EXACT-WORD criterion is scorable at all -- makes every LEXICAL channel a "
            "self-match: the trigram, prefix and grounded floors all score 1.0000 on all three "
            "rungs because their query is built from L and L is now a candidate. Their rise is "
            "exactly 0 for a degenerate reason. Only the CONTEXT read-out, whose query is a "
            "held-out sentence, carries information here. Read this table for OUR rise only, and "
            "take the floor comparison from the FORCED-SUBSTITUTION ladder below.",
        "per_arm": ladder}

    # ---- THE DELIVERABLE PROPER: the LANDED eligibility, criterion varied ----------------------
    # L is MASKED OUT, so the system cannot name the word and substitution is FORCED -- which is
    # also why the EXACT-WORD criterion is not merely strict on the landed instrument, it is
    # UNSATISFIABLE. The only non-degenerate criterion question is therefore WHAT THE SUBSTITUTE
    # MUST BE: a true synonym, or anything in the generous closure.
    forced: Dict[str, Dict] = {}
    common_forced = POP_SYN.copy()
    for a in ladder_arms:
        k1 = ("OPEN_K1_SYNONLY_selfExcluded_POPSYN", "PARTIAL_CUE", a)
        k2 = ("OPEN_K2_LANDED_selfExcluded_POPALL", "PARTIAL_CUE", a)
        k1e = ("OPEN_K1_SYNONLY_selfExcluded_POPSYN", "EXACT_KEY", a)
        k2e = ("OPEN_K2_LANDED_selfExcluded_POPALL", "EXACT_KEY", a)
        if k1 not in hits_store or k2 not in hits_store:
            continue
        forced[a] = {
            "PARTIAL_CUE": {
                "K1_TRUE_SYNONYM_ONLY": round(float(hits_store[k1][common_forced].mean()), 4),
                "K2_LANDED_GENEROUS_CLOSURE": round(float(hits_store[k2][common_forced].mean()), 4),
                "RISE_K2_minus_K1": paired_criterion_delta(hits_store[k2], hits_store[k1],
                                                           common_forced, N_BOOT,
                                                           MASTER_SEED + 51)},
            "EXACT_KEY": {
                "K1_TRUE_SYNONYM_ONLY": round(float(hits_store[k1e][common_forced].mean()), 4),
                "K2_LANDED_GENEROUS_CLOSURE": round(float(hits_store[k2e][common_forced].mean()), 4),
                "RISE_K2_minus_K1": paired_criterion_delta(hits_store[k2e], hits_store[k1e],
                                                           common_forced, N_BOOT,
                                                           MASTER_SEED + 52)}}
    rep["THE_DELIVERABLE_forced_substitution_criterion_rise_per_arm"] = {
        "POPULATION": int(common_forced.sum()),
        "WHAT_IS_HELD_FIXED": "identical items (POP_SYN: every item that HAS a synonym in the "
                              "pool), identical eligibility (the landed one -- L masked out), "
                              "identical scores. ONLY the gold matrix changes. Single variable.",
        "NOTE_ON_THE_LANDED_HEADLINE": "the landed 0.0223 was computed on POP_ALL (n=%d). The K2 "
                                       "column here is the SAME arm and the SAME criterion "
                                       "recomputed on POP_SYN (n=%d) so that it is commensurable "
                                       "with K1. The two K2 numbers are NOT the same number and "
                                       "neither is quoted for the other."
                                       % (int(POP_ALL.sum()), int(common_forced.sum())),
        "per_arm": forced,
        "HOW_TO_READ_IT": "if the floors rise as much as we do when the criterion is loosened, the "
                          "metric change buys nothing and that is the finding. If the floors rise "
                          "LESS than we do, our score depends more on the generosity than theirs "
                          "does -- which is worse, not better."}

    # ---- THE DECIDING QUESTION: does the read-out clear the floors under the loose criterion? ---
    def verdict_row(key: str) -> Dict:
        r = results.get(key)
        if r is None:
            return {}
        mm = r.get("ARM_BY_ARM_vs_EACH_FLOOR_tie_corrected", {}).get(
            "R0_CTX_DENSE_our_read_out", {})
        worst = None
        for f, m in mm.items():
            if worst is None or m["point"] < worst[1]["point"]:
                worst = (f, m)
        return {"n": r["n_common_scored"], "chance": r["chance_for_THIS_condition"],
                "R0_hit_tie_corrected": r["hit_at_1_TIE_CORRECTED_primary"].get(
                    "R0_CTX_DENSE_our_read_out"),
                "KA": r["VALIDITY"]["KNOWN_ANSWER_hit_at_1"],
                "NULL": r["VALIDITY"]["NULL_hit_at_1"],
                "READABLE": r["VALIDITY"]["CONDITION_READABLE"],
                "vs_each_floor": mm,
                "BINDING_FLOOR": worst[0] if worst else None,
                "MARGIN_vs_BINDING_FLOOR": worst[1] if worst else None,
                "CLEARS_ALL_FOUR_FLOORS_CI_SEPARATED": bool(
                    mm and all(m["band"] == "ABOVE" for m in mm.values()))}

    rep["THE_DECIDING_QUESTION"] = {
        "asked": "under the meaning-equivalent criterion, does the read-out clear "
                 "max(orthographic, frequency, scramble, constant) CI-separated where it did not "
                 "under exact match?",
        "rule": "each row is self-contained: its own pool, its own criterion, its own population, "
                "its own chance. NO ROW MAY BE COMPARED TO ANOTHER ROW'S ABSOLUTE NUMBER.",
        "rows": {k: verdict_row(k) for k in sorted(results)},
    }

    # ---- ABSTENTION WITH FALLBACK ---------------------------------------------------------------
    abst: Dict[str, Dict] = {}
    for bname in ("OPEN_K2_LANDED_selfExcluded_POPALL", "OPEN_K1_SYNONLY_selfExcluded_POPSYN",
                  "LADDER_K0_EXACT_WORD_selfEligible",
                  "LADDER_K1_SUBSTITUTION_ALLOWED_selfEligible"):
        per_arm = {}
        for a in ABSTAIN_ARMS:
            k = (bname, "PARTIAL_CUE", a)
            if k not in conf_store:
                continue
            sc = scored_store[k] & np.asarray(blocks[bname]["keep"], bool)
            per_arm[a] = {
                sig: abstention_curve(hits_store[k], conf_store[k][sig], sc, COVERAGE_RATES,
                                      N_BOOT, MASTER_SEED + 71)
                for sig in ("conf_top1", "conf_margin")}
        # the head-to-head that matters: US vs the SPELLING floor, each abstaining on its own signal
        head = {}
        kr = (bname, "PARTIAL_CUE", "R0_CTX_DENSE_our_read_out")
        kf = (bname, "PARTIAL_CUE", "F1_TRIGRAM_ONLY_orthographic")
        if kr in conf_store and kf in conf_store:
            sc = scored_store[kr] & scored_store[kf] & np.asarray(blocks[bname]["keep"], bool)
            for r in (0.10, 0.30, 0.50, 1.00):
                head["at_response_rate_%.2f" % r] = paired_selective_margin(
                    hits_store[kr], conf_store[kr]["conf_margin"],
                    hits_store[kf], conf_store[kf]["conf_margin"], sc, r, N_BOOT,
                    MASTER_SEED + 83)
        abst[bname] = {"per_arm": per_arm, "R0_minus_SPELLING_at_matched_response_rate": head}
    rep["ABSTENTION_WITH_FALLBACK"] = {
        "REGIME": "PARTIAL_CUE",
        "what_is_measured": "accuracy against RESPONSE RATE. At rate r the arm answers the "
                            "r-fraction of items on which its own confidence is highest.",
        "what_is_NOT_measured": "'return the best meaning-equivalent instead of the argmax' is not "
                                "implementable without consulting the judge at run time, which "
                                "would be an oracle. The SUBSTITUTION half of the owner's policy is "
                                "the criterion ladder; the DECLINING half is this curve.",
        "control": "RANDOM-ABSTAIN at matched coverage, 200 draws, 95% band. A curve that does not "
                   "exit that band is not selectivity. Method credited to "
                   "experiments/exp_metacog_abstain_readout_signal_thresholding_v1.",
        "blocks": abst}

    # ---- HEADLINE, computed from the measured numbers, not written in advance -------------------
    def _clears(key: str) -> Optional[bool]:
        row = rep["THE_DECIDING_QUESTION"]["rows"].get(key) or {}
        return row.get("CLEARS_ALL_FOUR_FLOORS_CI_SEPARATED")

    r0_rise = (forced.get("R0_CTX_DENSE_our_read_out", {})
               .get("PARTIAL_CUE", {}).get("RISE_K2_minus_K1", {}))
    f1_rise = (forced.get("F1_TRIGRAM_ONLY_orthographic", {})
               .get("PARTIAL_CUE", {}).get("RISE_K2_minus_K1", {}))
    clears_tight = _clears("BAL_K49_K1_SYNONLY|PARTIAL_CUE")
    if clears_tight is None:
        clears_tight = _clears("BAL_K15_K1_SYNONLY|PARTIAL_CUE")
    clears_loose = _clears("BAL_K49_K2_LANDED|PARTIAL_CUE")
    if clears_loose is None:
        clears_loose = _clears("BAL_K15_K2_LANDED|PARTIAL_CUE")
    rep["HEADLINE"] = {
        "PREMISE_CHECK": "the landed instrument does NOT demand one exact word. Its gold set "
                         "averages %.3f eligible words per item and it MASKS THE WORD ITSELF OUT of "
                         "the pool, so the exact-word criterion is not merely strict there, it is "
                         "UNSATISFIABLE. Meaning-equivalence was already granted."
                         % float(G_LAND_EXCL.sum(axis=0)[POP_ALL].mean()),
        "OUR_RISE_when_the_criterion_is_loosened_from_true_synonymy_to_the_landed_closure": r0_rise,
        "THE_SPELLING_FLOORS_RISE_on_the_same_items": f1_rise,
        "clears_all_four_floors_TIGHT_synonym_criterion_debiased_pool_partial_cue": clears_tight,
        "clears_all_four_floors_LANDED_criterion_debiased_pool_partial_cue": clears_loose,
        "CAVEAT_THAT_GOVERNS_EVERY_LINE_ABOVE": "a win obtained only by loosening the criterion is "
                                                "a statement about THE TASK, not about our "
                                                "capability, and is reported as such.",
    }
    rep["verdict"] = "SEE_HEADLINE_criterion_instrumentation_no_capability_claim"
    rep["verdict_msg"] = (
        "INSTRUMENTATION. Meaning-equivalence was ALREADY the landed criterion (%.1f eligible gold "
        "words per item, and the target word itself masked out of the pool). Loosening from true "
        "synonymy to the landed closure moves our read-out by %s and the spelling floor by %s on "
        "the SAME items (POP_SYN n=%d, PARTIAL_CUE, landed eligibility). NO capability claim is "
        "made and MEETS_BAR is not claimed."
        % (float(G_LAND_EXCL.sum(axis=0)[POP_ALL].mean()),
           str(r0_rise.get("rise")), str(f1_rise.get("rise")), int(common_forced.sum())))

    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", choices=["full", "reduced"], default="full")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    if a.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    with open(os.path.join(OUT_DIR, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    try:
        rep = run(a.grid)
        _atomic_json(os.path.join(OUT_DIR, "metrics.json"), rep)
        print("WROTE " + os.path.join(OUT_DIR, "metrics.json"), flush=True)
    except SystemExit:
        raise
    except Exception as exc:
        _atomic_json(os.path.join(OUT_DIR, "_crash_diagnostic.json"),
                     {"error": "%s: %s" % (type(exc).__name__, exc),
                      "traceback": traceback.format_exc(),
                      "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
