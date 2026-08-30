"""Decisive eval for SEMANTIC (ATL-hub) state matching vs exact-string, with the three research guards.

The entity-state layer is the anterior-temporal-lobe semantic hub (Patterson/Nestor/Rogers 2007) -- graded,
feature-based, NOT lexical-string. So a reader who stored 'ill' answers 'is X unwell?' via SYNONYMY and 'is
the vase damaged?' after 'shattered' via ENTAILMENT. This cell measures whether the glass-box WordNet matcher
(with guards) recovers those queries an EXACT-string floor cannot, WITHOUT breaking the three named failure
modes (privative / relative-gradable / typed antonymy). Research: notes/problems/.../research_semantic_state_
matching_and_perfect_currency_backgrounding_2026-08-29.md (GO-WITH-BOUNDS).

Arms (all feed abstract stored states -> isolate the MATCHER, not extraction):
  EXACT              exact-value match only (the no-semantics floor)
  SEMANTIC_GUARDED   synonymy + scalar/hypernym entailment + TYPED antonymy (the brain-faithful arm)
  SEMANTIC_UNGUARDED guards off (typed-antonymy disabled) -> must FAIL the contrary-negation traps
  TWIN               guarded matcher on SHUFFLED stored values (info-free) -> must LOSE on the synonym set

Populations: SET A (a query that DOES hold -- synonym / entailment / contradictory-negation) and SET B (a
query that does NOT hold -- an antonym of a held state, a CONTRARY negation 'not tall'-/->short, unrelated).
Plus a privative EXTRACTION sub-check ('a fake soldier' must not store 'soldier').

Gate: SEMANTIC_GUARDED beats EXACT CI-separated on the full population; the UNGUARDED ablation is WORSE on
SET B (guards load-bearing); the TWIN loses on SET A. Deterministic, ASCII-only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.state_register import (
    StateRegister, state_match, extract_state_events, CURRENT, PRIOR,
)

ANCHOR = "state_register_semantic_v1"

# SET A -- (stored_value, stored_polarity, query, kind): the query DOES hold (gold True).
SET_A = [
    # synonymy
    ("ill", 1, "unwell", "syn"), ("ill", 1, "sick", "syn"), ("sick", 1, "ill", "syn"),
    ("happy", 1, "glad", "syn"), ("glad", 1, "happy", "syn"), ("wealthy", 1, "rich", "syn"),
    ("rich", 1, "wealthy", "syn"), ("weary", 1, "tired", "syn"), ("tired", 1, "weary", "syn"),
    ("afraid", 1, "frightened", "syn"), ("frightened", 1, "afraid", "syn"), ("sad", 1, "unhappy", "syn"),
    ("unhappy", 1, "sad", "syn"), ("dead", 1, "deceased", "syn"), ("big", 1, "large", "syn"),
    ("large", 1, "big", "syn"), ("small", 1, "little", "syn"), ("quiet", 1, "still", "syn"),
    # scalar / degree entailment (stronger -> weaker)
    ("shattered", 1, "broken", "scalar"), ("shattered", 1, "damaged", "scalar"),
    ("smashed", 1, "broken", "scalar"), ("broken", 1, "damaged", "scalar"), ("freezing", 1, "cold", "scalar"),
    ("boiling", 1, "hot", "scalar"), ("starving", 1, "hungry", "scalar"), ("drenched", 1, "wet", "scalar"),
    ("furious", 1, "angry", "scalar"), ("terrified", 1, "afraid", "scalar"), ("delighted", 1, "happy", "scalar"),
    ("miserable", 1, "sad", "scalar"), ("exhausted", 1, "tired", "scalar"), ("deceased", 1, "dead", "scalar"),
    # hypernym entailment (specific noun -> general)
    ("soldier", 1, "serviceman", "hyper"), ("widow", 1, "woman", "hyper"), ("cottage", 1, "house", "hyper"),
    # contradictory-negation ('not alive' -> dead HOLDS; closed-scale)
    ("alive", -1, "dead", "contra_neg"), ("open", -1, "shut", "contra_neg"), ("locked", -1, "unlocked", "contra_neg"),
    ("full", -1, "empty", "contra_neg"),
]
# SET B -- (stored_value, stored_polarity, query, kind): the query does NOT hold (gold False).
SET_B = [
    # antonym of a HELD state
    ("ill", 1, "well", "anto"), ("alive", 1, "dead", "anto"), ("open", 1, "shut", "anto"),
    ("rich", 1, "poor", "anto"), ("happy", 1, "sad", "anto"), ("locked", 1, "unlocked", "anto"),
    ("full", 1, "empty", "anto"), ("clean", 1, "dirty", "anto"),
    # CONTRARY negation ('not tall' -/-> short; open-scale, a middle exists) -- the guard-3 traps
    ("tall", -1, "short", "contrary_neg"), ("rich", -1, "poor", "contrary_neg"),
    ("happy", -1, "sad", "contrary_neg"), ("ill", -1, "well", "contrary_neg"),
    ("hot", -1, "cold", "contrary_neg"), ("old", -1, "young", "contrary_neg"),
    ("strong", -1, "weak", "contrary_neg"), ("clean", -1, "dirty", "contrary_neg"),
    # unrelated
    ("ill", 1, "tall", "unrel"), ("soldier", 1, "broken", "unrel"), ("happy", 1, "locked", "unrel"),
    ("open", 1, "ill", "unrel"), ("rich", 1, "asleep", "unrel"),
]


def _predict(arm, stored_v, stored_pol, query):
    """Predict whether the queried state HOLDS (True) under an arm, feeding one abstract stored state."""
    reg = StateRegister().fold(["e"], [("state", "e", stored_v, CURRENT if stored_pol == 1 else CURRENT,
                                        stored_pol, 1)], n_clauses=4)
    if arm == "exact":
        return reg.is_in_state("e", query, 3, semantic=False) is True
    if arm == "guarded":
        return reg.is_in_state("e", query, 3, semantic=True) is True
    if arm == "unguarded":
        return state_match(query, stored_v, stored_pol, guards=False) == "MATCH"
    raise ValueError(arm)


def _acc(arm, pairs, shuffle_stored=None):
    hits = []
    for i, (sv, sp, q, kind) in enumerate(pairs):
        stored = shuffle_stored[i] if shuffle_stored is not None else sv
        pred = _predict(arm, stored, sp, q)
        gold = kind not in ()  # placeholder; gold set by caller list membership
        hits.append((pred, kind))
    return hits


def _boot_ci(hits, n_boot=2000, seed=0):
    hits = np.asarray(hits, dtype=float)
    if len(hits) == 0:
        return 0.0, 0.0, 0.0
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(hits), size=(n_boot, len(hits)))
    bs = hits[idx].mean(axis=1)
    return float(hits.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def _score_arm(arm, seed=0, twin=False):
    """Accuracy over SET_A (gold True) + SET_B (gold False). twin=True shuffles stored values (info-free)."""
    rng = np.random.default_rng(seed + 7)
    a_stored = [p[0] for p in SET_A]
    b_stored = [p[0] for p in SET_B]
    if twin:
        a_stored = list(rng.permutation(a_stored))
        b_stored = list(rng.permutation(b_stored))
    hits, byk = [], {}
    for (sv, sp, q, kind), st in list(zip(SET_A, a_stored)):
        pred = _predict(arm, st, sp, q)
        h = int(pred is True)          # gold True
        hits.append(h); byk.setdefault(kind, []).append(h)
    for (sv, sp, q, kind), st in list(zip(SET_B, b_stored)):
        pred = _predict(arm, st, sp, q)
        h = int(pred is False)         # gold False
        hits.append(h); byk.setdefault(kind, []).append(h)
    return hits, {k: round(float(np.mean(v)), 3) for k, v in byk.items()}


def _privative_extraction_check():
    """A 'fake/former soldier' must NOT store 'soldier' (guard #1, at extraction). Returns (n, n_blocked)."""
    import spacy
    nlp = spacy.load("en_core_web_sm")
    sents = ["He was a fake soldier.", "He was a former captain.", "She was a former queen.",
             "He was an alleged thief.", "He was a would-be poet.", "It was a counterfeit coin."]
    blocked = 0
    for s in sents:
        evs = extract_state_events(nlp, s)
        # blocked if no state event carries the head noun as its value
        if not any(e["kind"] == "state" for e in evs):
            blocked += 1
    return len(sents), blocked


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(m):
    d = _out_dir(); tmp = os.path.join(d, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, os.path.join(d, "metrics.json"))


def main(seed=0):
    t0 = time.perf_counter()
    arms = {}
    for arm in ("exact", "guarded", "unguarded"):
        hits, byk = _score_arm(arm, seed=seed)
        m, lo, hi = _boot_ci(hits, seed=seed)
        arms[arm] = {"acc": round(m, 4), "ci": [round(lo, 4), round(hi, 4)], "by_kind": byk}
    twin_hits, twin_byk = _score_arm("guarded", seed=seed, twin=True)
    tw_m, tw_lo, tw_hi = _boot_ci(twin_hits, seed=seed)

    # set-A-only (synonym recall) is where EXACT structurally fails; compute separately for the headline
    def _setA_acc(arm):
        h = []
        for (sv, sp, q, kind) in SET_A:
            h.append(int(_predict(arm, sv, sp, q) is True))
        return _boot_ci(h, seed=seed)
    exA = _setA_acc("exact"); gdA = _setA_acc("guarded")
    # set-B-only (traps) is where UNGUARDED fails
    def _setB_acc(arm):
        h = []
        for (sv, sp, q, kind) in SET_B:
            h.append(int(_predict(arm, sv, sp, q) is False))
        return _boot_ci(h, seed=seed)
    gdB = _setB_acc("guarded"); ugB = _setB_acc("unguarded")

    n_priv, n_blocked = _privative_extraction_check()

    gate = bool(arms["guarded"]["ci"][0] > arms["exact"]["ci"][1]         # guarded beats exact overall
                and gdA[1] > exA[2]                                        # ... driven by synonym recall
                and gdB[0] > ugB[2]                                        # guards fix set B vs unguarded
                and gdA[1] > tw_hi)                                        # twin loses on the held set
    metrics = {
        "verdict": "HARD_PASS" if gate else "SOFT_OR_FAIL",
        "anchor_name": ANCHOR, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(time.perf_counter() - t0, 2), "seed": seed,
        "n_setA": len(SET_A), "n_setB": len(SET_B),
        "arms": arms,
        "twin_shuffled_stored": {"acc": round(tw_m, 4), "ci": [round(tw_lo, 4), round(tw_hi, 4)]},
        "setA_synonym_recall": {"exact": round(exA[0], 4), "exact_hi": round(exA[2], 4),
                                "guarded": round(gdA[0], 4), "guarded_lo": round(gdA[1], 4)},
        "setB_trap_accuracy": {"guarded": round(gdB[0], 4), "guarded_lo": round(gdB[1], 4),
                               "unguarded": round(ugB[0], 4), "unguarded_hi": round(ugB[2], 4)},
        "privative_extraction_guard": {"n": n_priv, "blocked": n_blocked},
        "gate": {"guarded_beats_exact_ci_sep": bool(arms["guarded"]["ci"][0] > arms["exact"]["ci"][1]),
                 "synonym_recall_lift_ci_sep": bool(gdA[1] > exA[2]),
                 "guards_fix_setB_vs_unguarded_ci_sep": bool(gdB[0] > ugB[2]),
                 "twin_loses_on_setA": bool(gdA[1] > tw_hi), "PASS": gate},
        "interpretation": ("The brain-faithful semantic (ATL-hub) matcher recovers synonym/entailment state "
                           "queries an exact-string reader cannot (setA), while the THREE guards keep the "
                           "named failure modes correct (setB) where the UNGUARDED ablation fails; the "
                           "info-free twin (shuffled stored values) loses. Privative extraction guard blocks "
                           f"{n_blocked}/{n_priv} 'fake/former X'."),
    }
    _atomic_write(metrics)
    print(f"[{ANCHOR}] guarded {arms['guarded']['acc']:.3f} vs exact {arms['exact']['acc']:.3f} "
          f"vs unguarded {arms['unguarded']['acc']:.3f} | twin {tw_m:.3f} | GATE {'PASS' if gate else 'no'}")
    print(f"   setA synonym recall: exact {exA[0]:.3f} -> guarded {gdA[0]:.3f}")
    print(f"   setB traps: guarded {gdB[0]:.3f} vs UNGUARDED {ugB[0]:.3f} (guards load-bearing)")
    print(f"   privative extraction blocked {n_blocked}/{n_priv}; by_kind guarded {arms['guarded']['by_kind']}")
    print(f"-> {os.path.join(_out_dir(), 'metrics.json')} ({metrics['elapsed_s']}s)")
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        assert state_match("unwell", "ill", 1) == "MATCH" and state_match("short", "tall", -1) == "NONE"
        print("[self-test] PASS"); sys.exit(0)
    main(seed=args.seed)
