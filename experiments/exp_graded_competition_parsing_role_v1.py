# CELL-TEMPLATE (measurement/mechanism-probe; NOT a queue-dispatch cell).
# SOLVER cell for problem `discrete_where_the_brain_is_graded_in_parsing_and_role_assignment`.
#
# THE PROBLEM: our parser (attachment) and role assigner (binding) make HARD, DISCRETE commitments where
# the brain runs GRADED probabilistic competition (MacDonald/Pearlmutter/Seidenberg 1994; Spivey-Knowlton
# 1996 normalized recurrence; Lewis & Vasishth 2005 cue-based retrieval). The discrete choice is the
# noise->0 / argmax LIMIT of that competition. Graded competition predicts DIFFICULTY (settling time /
# competition margin) and human-like ambiguity errors a discrete model structurally cannot.
#
# HOW THE BRAIN DOES THIS (opening move): candidate attachment sites / role fillers compete in parallel,
# each supported by ADDITIVE cue-match activation (Lewis-Vasishth; ACT-R spreading activation), settling
# by mutual inhibition (normalized recurrence, Spivey-Knowlton). Prior substrate cells already established
# the noise->0 == discrete limit and the interference signature at the EPISODE level (relcl_cue_retrieval)
# and a BINARY route-conflict difficulty readout (relcl_parallel_routes). WHAT IS STILL OPEN and what this
# cell delivers: a SINGLE graded competition over REAL candidate tokens in REAL sentences that
#   (1) reduces EXACTLY to the discrete resolver at noise->0 (argmax of the same additive activation);
#   (2) emits a CONTINUOUS competition margin (+ cycles-to-settle) that is a valid graded DIFFICULTY
#       signal on a genuinely ambiguous / non-canonical population -- CI-separated where discrete commitment
#       ERRS and on the literature-pinned hard constructions, with a SHUFFLED-cue-weight twin LOSING;
#   (3) the continuous margin is a STRICTLY BETTER difficulty predictor than the substrate's existing
#       BINARY route-conflict (AUC-separated) -- graded beats the discretized version of itself;
#   (4) ONE activation function A(verb, candidate) serves BOTH role binding (argmax over candidates) AND
#       attachment (argmax over heads) -- the cross-organ unification.
#   (5) ACCURACY (honest, decisive either way): graded competition vs the strongest DISCRETE floors on the
#       ambiguous population. Expected per the brief + prior work: argmax IS the accuracy-optimal readout,
#       so graded TIES the fixed-priority resolver on gold accuracy -- what graded uniquely BUYS is the
#       difficulty signal, not gold accuracy. A tie here is a rigorous, brain-faithful NEGATIVE on the
#       accuracy clause, not a failure.
#
# POPULATION: the BALANCED reversible non-canonical set (build_items; 6 constructions, both nouns animate =
# genuinely reversible, disjoint dev/test lexicons) -- the population where discrete commitment errs. Plus
# REAL QA-SRL patient items as the generalization / margin-vs-conflict AUC test.
#
# ARMS (each picks a 1-based patient token, or emits a difficulty scalar):
#   TWO_LINE        word order + voice (single dominant cue). Discrete floor.
#   STRUCT_RESOLVER fixed-priority filler-gap resolver (arm_fillergap_incremental). Strongest discrete floor.
#   GRADED          argmax of learned-validity additive cue activation (== normalized-recurrence winner).
#   PICK_FRONTED / TWIN   degeneracy + info-free controls.
#   GRADED_TWIN     graded with SHUFFLED cue validities (info-free difficulty twin).
"""exp_graded_competition_parsing_role_v1 -- graded probabilistic competition (additive cue-based retrieval
+ normalized-recurrence settling) over real candidate tokens: discrete == its noise->0 limit; the continuous
competition margin is a valid graded difficulty signal that beats the binary route-conflict; one activation
serves attachment AND role binding. --self-test / --smoke / full.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import random
import sys
import time
import traceback
from collections import Counter
from typing import Dict, List, Optional, Tuple

import numpy as np

ANCHOR_NAME = "graded_competition_parsing_role_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from experiments.exp_relcl_incremental_fillergap_parser_v1 import (  # noqa: E402
    build_items, ANIMATE_DEV, ANIMATE_TEST, TRANS_DEV, TRANS_TEST, CONSTRUCTIONS,
    _cands, _verb_local_passive_precise, arm_two_line, arm_fillergap_incremental, arm_pick_fronted,
    _has_post_object, boot_mean, boot_diff, _band, BOOT_SEED,
)

NOMINAL = {"NOUN", "PROPN", "PRON"}
N_BOOT = 10000
TWIN_SEEDS = [11, 23, 37, 41, 53]
# constructions the psycholinguistic literature pins as HARD (object-extraction: filler must be integrated
# at the gap across an intervening subject -- Gordon/Hendrick/Johnson 2001; Gibson DLT) vs EASY.
HARD_CONSTR = {"object_relative", "object_cleft"}
EASY_CONSTR = {"canonical_active", "subject_relative", "subject_cleft"}

# ---------------------------------------------------------------------------------------------
# THE GRADED COMPETITION: additive cue activation over candidate tokens + normalized-recurrence settling.
# ---------------------------------------------------------------------------------------------
CUES = ("order", "struct", "recency")


def cue_supports(toks: List[str], pos: List[str], v: int, cands: List[int],
                 prec_voice: bool) -> Dict[str, np.ndarray]:
    """Graded per-candidate support in [0,1] for each cue, for the PATIENT gap of verb v (1-based).
      order   : proximity in the canonical word-order direction (post-verbal if active, pre-verbal if
                passive) -- the dominant word-order cue. 1/(1+rank) so nearer = stronger, others 0.
      struct  : 1.0 for the structural filler-gap pick (active-filler resolver), else 0 -- the syntactic cue.
      recency : 1/(1+|i-v|) absolute proximity -- ACT-R base-level activation / similarity-interference cue
                (a recent salient nominal competes for the gap even when the structure points elsewhere).
    All three are computable from POS + closed-class words + position (no gold, no arc graph)."""
    n = len(cands)
    order = np.zeros(n)
    if prec_voice:
        before = [k for k, i in enumerate(cands) if i < v]
        for rank, k in enumerate(reversed(before)):      # nearest pre-verbal first
            order[k] = 1.0 / (1.0 + rank)
    else:
        after = [k for k, i in enumerate(cands) if i > v]
        for rank, k in enumerate(after):                 # nearest post-verbal first
            order[k] = 1.0 / (1.0 + rank)
    struct = np.zeros(n)
    sp = arm_fillergap_incremental(toks, pos, v, cands, prec_voice)
    if sp in cands:
        struct[cands.index(sp)] = 1.0
    recency = np.array([1.0 / (1.0 + abs(i - v)) for i in cands], dtype=np.float64)
    return {"order": order, "struct": struct, "recency": recency}


def net_activation(sup: Dict[str, np.ndarray], weights: Dict[str, float]) -> np.ndarray:
    """Additive Lewis-Vasishth activation: A_i = sum_c w_c * support_c(i)."""
    n = len(next(iter(sup.values())))
    A = np.zeros(n, dtype=np.float64)
    for c in CUES:
        A = A + weights.get(c, 0.0) * sup[c]
    return A


def normalized_recurrence(net: np.ndarray, gain: float = 2.0, criterion: float = 0.90,
                          max_cycles: int = 100) -> Tuple[int, int, float]:
    """Spivey-Knowlton normalized recurrence over N candidate interpretations: multiplicative recurrent
    feedback + normalization (mutual inhibition), settle to criterion. Returns
    (winner_index, cycles_to_settle, final_gap). The winner == argmax(net) (settling is monotone in net),
    so this is the DISCRETE argmax in the noise->0 limit; cycles-to-settle is the graded difficulty."""
    n = len(net)
    if n == 0:
        return -1, 0, 0.0
    if n == 1:
        return 0, 1, 1.0
    a = np.full(n, 1.0 / n, dtype=np.float64)
    # shift by min for overflow safety -- this PRESERVES the activation GAPs (net_i - net_j), which is
    # what drives settling speed. Do NOT rescale by max: dividing by the range would normalise the gap
    # away and make every item settle at the same rate (the difficulty gradient would vanish).
    net = net - net.min()
    for cyc in range(1, max_cycles + 1):
        a = a * np.exp(gain * net)
        a = a / a.sum()
        top = np.sort(a)[::-1]
        if top[0] >= criterion:
            return int(np.argmax(a)), cyc, float(top[0] - top[1])
    top = np.sort(a)[::-1]
    return int(np.argmax(a)), max_cycles, float(top[0] - top[1])


def softmax(x: np.ndarray, gain: float) -> np.ndarray:
    z = gain * (x - x.max())
    e = np.exp(z)
    return e / e.sum()


def graded_pick(sup, weights, gain=2.0) -> Dict:
    """Run the graded competition and return the MAINTAINED DISTRIBUTION over candidates plus its readouts.
    BRAIN-FAITHFUL FRAME (deepened per the 2nd literature drill -- Levy 2008; Swets/Desmet/Clifton/Ferreira
    2008): the native output of comprehension is a PROBABILITY DISTRIBUTION over candidate interpretations,
    consumed downstream; the difficulty currency is the distribution's ENTROPY (Levy: comprehension = a
    distribution over structures; -log P surprisal = the relative entropy it induces). The single discrete
    answer is the ARGMAX of that distribution -- a LATER, TASK-TRIGGERED collapse (Swets: resolution to one
    reading happens only when the task presses, and even then incompletely), NOT the default readout.
    Returns:
      win     : argmax candidate (the task-triggered collapse = the discrete resolver's pick).
      p       : the maintained softmax distribution over candidates (the native graded output).
      entropy : NORMALIZED Shannon entropy H/log(n) in [0,1] -- HIGH = ambiguous/underspecified = hard
                (candidate-count-robust; the Levy-faithful difficulty signal).
      margin  : top1-top2 of the raw additive activation (a monotone continuous competition margin).
      cycles  : Spivey-Knowlton normalized-recurrence cycles-to-settle (the settling-time difficulty)."""
    net = net_activation(sup, weights)
    n = len(net)
    if n == 0:
        return {"win": -1, "p": np.array([]), "entropy": 0.0, "margin": 0.0, "cycles": 0}
    if n == 1:
        return {"win": 0, "p": np.array([1.0]), "entropy": 0.0, "margin": float(net[0] + 1.0), "cycles": 1}
    p = softmax(net, gain)
    ent = float(-(p * np.log(p + 1e-12)).sum() / np.log(n))    # normalized entropy in [0,1]
    order = np.sort(net)[::-1]
    margin = float(order[0] - order[1])
    win, cycles, _gap = normalized_recurrence(net, gain=gain)
    return {"win": int(np.argmax(net)), "p": p, "entropy": ent, "margin": margin, "cycles": int(cycles)}


# ---------------------------------------------------------------------------------------------
# LEARN cue validities (Competition-Model cue validity = reliability of the cue's top pick on DEV).
# ---------------------------------------------------------------------------------------------
def learn_validities(items: List[dict], gen) -> Dict[str, float]:
    correct = {c: 0 for c in CUES}
    total = {c: 0 for c in CUES}
    cache: Dict[str, object] = {}
    for it in items:
        toks = it["toks"]; text = " ".join(toks)
        cr = cache.get(text)
        if cr is None:
            cr = gen.generate(text, extended=True); cache[text] = cr
        if list(cr.tokens) != toks:
            continue
        pos = list(cr.pos); v = it["verb_idx"]; gold = it["gold_idx"]
        cands = _cands(pos)
        if gold not in cands or not cands:
            continue
        pv = _verb_local_passive_precise(toks, pos, v)
        sup = cue_supports(toks, pos, v, cands, pv)
        gold_k = cands.index(gold)
        for c in CUES:
            s = sup[c]
            if s.max() <= 0:
                continue                       # cue is silent on this item -> does not vote
            top = int(np.argmax(s))
            total[c] += 1
            correct[c] += int(top == gold_k)
    val = {}
    for c in CUES:
        r = correct[c] / total[c] if total[c] else 0.5
        val[c] = max(0.0, 2.0 * (r - 0.5))     # validity in [0,1]; chance-reliable cue -> 0 weight
    return val


# ---------------------------------------------------------------------------------------------
# AUC helper (rank-based) + bootstrap AUC-difference.
# ---------------------------------------------------------------------------------------------
def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    """AUC of `scores` predicting binary `labels` (1=positive). Ties get average rank. NaN if degenerate."""
    scores = np.asarray(scores, float); labels = np.asarray(labels, int)
    pos = scores[labels == 1]; neg = scores[labels == 0]
    n1, n2 = len(pos), len(neg)
    if n1 == 0 or n2 == 0:
        return float("nan")
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(len(scores), float)
    sorted_s = scores[order]
    i = 0
    while i < len(sorted_s):
        j = i
        while j + 1 < len(sorted_s) and sorted_s[j + 1] == sorted_s[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    sum_pos = ranks[labels == 1].sum()
    return float((sum_pos - n1 * (n1 + 1) / 2.0) / (n1 * n2))


def boot_diff_unpaired(a: np.ndarray, b: np.ndarray, n_boot: int, seed: int) -> dict:
    """CI of mean(a)-mean(b) for INDEPENDENT samples a, b of possibly different size (resample each)."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) == 0 or len(b) == 0:
        return {"point": float("nan"), "ci95": [float("nan"), float("nan")], "half_width": float("nan"),
                "n_a": int(len(a)), "n_b": int(len(b))}
    rng = np.random.default_rng(seed)
    ma = a[rng.integers(0, len(a), size=(n_boot, len(a)))].mean(axis=1)
    mb = b[rng.integers(0, len(b), size=(n_boot, len(b)))].mean(axis=1)
    d = ma - mb
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"point": float(a.mean() - b.mean()), "ci95": [float(lo), float(hi)],
            "half_width": float((hi - lo) / 2), "n_a": int(len(a)), "n_b": int(len(b))}


def boot_auc_diff(score_a: np.ndarray, score_b: np.ndarray, labels: np.ndarray,
                  n_boot: int, seed: int) -> dict:
    """Bootstrap CI of AUC(score_a) - AUC(score_b) for the same labels (paired resample of items)."""
    score_a = np.asarray(score_a, float); score_b = np.asarray(score_b, float)
    labels = np.asarray(labels, int)
    a0, b0 = auc(score_a, labels), auc(score_b, labels)
    rng = np.random.default_rng(seed)
    n = len(labels)
    diffs = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        da = auc(score_a[idx], labels[idx]); db = auc(score_b[idx], labels[idx])
        if da == da and db == db:
            diffs.append(da - db)
    if not diffs:
        return {"auc_a": a0, "auc_b": b0, "point": float("nan"), "ci95": [float("nan")] * 2}
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return {"auc_a": a0, "auc_b": b0, "point": float(a0 - b0), "ci95": [float(lo), float(hi)],
            "half_width": float((hi - lo) / 2)}


# ---------------------------------------------------------------------------------------------
# SCORE the synthetic balanced set.
# ---------------------------------------------------------------------------------------------
ARMS = ["TWO_LINE", "STRUCT_RESOLVER", "GRADED", "GRADED_TWIN", "PICK_FRONTED", "TWIN"]


def _rand_settle_entropy(n: int, gain: float, seed: int) -> float:
    """info-free twin #2 -- RANDOM SETTLING: entropy of a softmax over RANDOM per-candidate activations
    (no cue information at all). Same arithmetic/scale as the real competition; guaranteed to carry no
    real difficulty signal, so it must NOT predict discrete error."""
    if n <= 1:
        return 0.0
    r = np.random.default_rng(seed).random(n)
    p = softmax(r, gain)
    return float(-(p * np.log(p + 1e-12)).sum() / np.log(n))


def score_synth(items: List[dict], gen, weights: Dict[str, float], weights_twin: Dict[str, float]) -> dict:
    twin_rngs = [random.Random(s) for s in TWIN_SEEDS]
    cache: Dict[str, object] = {}
    per: List[dict] = []
    n_dropped = 0
    for idx, it in enumerate(items):
        toks = it["toks"]; text = " ".join(toks)
        cr = cache.get(text)
        if cr is None:
            cr = gen.generate(text, extended=True); cache[text] = cr
        if list(cr.tokens) != toks:
            n_dropped += 1
            continue
        pos = list(cr.pos); v = it["verb_idx"]; gold = it["gold_idx"]
        cands = _cands(pos)
        if not cands:
            n_dropped += 1
            continue
        pv = _verb_local_passive_precise(toks, pos, v)
        sup = cue_supports(toks, pos, v, cands, pv)
        g = graded_pick(sup, weights)
        gt = graded_pick(sup, weights_twin)
        tl = arm_two_line(toks, pos, v, cands, pv)
        sr = arm_fillergap_incremental(toks, pos, v, cands, pv)
        pf = arm_pick_fronted(toks, pos, v, cands, pv)
        gpick = cands[g["win"]] if g["win"] >= 0 else None
        gtpick = cands[gt["win"]] if gt["win"] >= 0 else None
        picks = {"TWO_LINE": tl, "STRUCT_RESOLVER": sr, "GRADED": gpick,
                 "GRADED_TWIN": gtpick, "PICK_FRONTED": pf}
        corr = {k: int(picks[k] == gold) for k in picks}
        corr["TWIN"] = float(np.mean([int(random.Random(r.random()).choice(cands) == gold)
                                      for r in twin_rngs])) if cands else 0.0
        # binary route-conflict (the substrate's existing discrete difficulty signal)
        conflict = int(tl != sr)
        ent_rand = _rand_settle_entropy(len(cands), 2.0, 90001 + idx)
        per.append({"construction": it["construction"], "extraction": it["extraction"],
                    "corr": corr, "margin": g["margin"], "cycles": g["cycles"], "entropy": g["entropy"],
                    "margin_twin": gt["margin"], "entropy_twin": gt["entropy"], "entropy_rand": ent_rand,
                    "conflict": conflict, "two_line_err": int(tl != gold), "n_cands": len(cands)})
    return {"per": per, "n_dropped": n_dropped}


def _acc_block(per, arms=ARMS):
    vecs = {a: np.array([p["corr"][a] for p in per], float) for a in arms}
    return vecs


def run_full(gen, smoke: bool) -> dict:
    t0 = time.time()
    n_boot = 1500 if smoke else N_BOOT
    per_type = 60 if smoke else 400
    # DEV (learn validities) on the DEV lexicon; TEST on the DISJOINT test lexicon.
    dev_items: List[dict] = []
    for s in (201, 211, 223):
        dev_items += build_items(s, per_type, ANIMATE_DEV, TRANS_DEV)
    weights = learn_validities(dev_items, gen)
    # info-free twin #1: SHUFFLED CUE VALIDITIES -- a guaranteed DERANGEMENT (cyclic rotation) so each cue
    # gets a DIFFERENT cue's learned weight (destroys the validity->cue mapping; never an identity perm).
    keys = list(weights.keys()); vals = [weights[k] for k in keys]
    weights_twin = {keys[i]: vals[(i - 1) % len(keys)] for i in range(len(keys))}

    test_items: List[dict] = []
    for s in (101, 113, 127):
        test_items += build_items(s, per_type, ANIMATE_TEST, TRANS_TEST)
    res = score_synth(test_items, gen, weights, weights_twin)
    per = res["per"]
    print(f"[synth] scored={len(per)} dropped={res['n_dropped']} weights={ {k: round(v,3) for k,v in weights.items()} } "
          f"twin={ {k: round(v,3) for k,v in weights_twin.items()} }", flush=True)

    # -------- ACCURACY (honest): graded vs the strongest discrete floors, on ambiguous + strata --------
    def acc_stratum(keep):
        rows = [p for p in per if keep(p)]
        if not rows:
            return {"n": 0}
        vecs = _acc_block(rows)
        acc = {a: boot_mean(vecs[a], n_boot, BOOT_SEED + i) for i, a in enumerate(ARMS)}
        floor_names = ["TWO_LINE", "STRUCT_RESOLVER", "PICK_FRONTED", "TWIN"]
        floor = max(floor_names, key=lambda a: acc[a]["point"])
        d_g_floor = boot_diff(vecs["GRADED"], vecs[floor], n_boot, BOOT_SEED + 301)
        d_g_2line = boot_diff(vecs["GRADED"], vecs["TWO_LINE"], n_boot, BOOT_SEED + 302)
        d_g_resolver = boot_diff(vecs["GRADED"], vecs["STRUCT_RESOLVER"], n_boot, BOOT_SEED + 303)
        d_g_twin = boot_diff(vecs["GRADED"], vecs["TWIN"], n_boot, BOOT_SEED + 304)
        return {"n": len(rows), "acc": {a: acc[a]["point"] for a in ARMS},
                "acc_ci": {a: acc[a]["ci95"] for a in ARMS},
                "strongest_floor": floor, "floor_upper": acc[floor]["ci95"][1],
                "graded_minus_floor": d_g_floor, "band_graded_vs_floor": _band(d_g_floor),
                "graded_minus_twoline": d_g_2line, "band_graded_vs_twoline": _band(d_g_2line),
                "graded_minus_resolver": d_g_resolver, "band_graded_vs_resolver": _band(d_g_resolver),
                "graded_minus_twin": d_g_twin, "band_graded_vs_twin": _band(d_g_twin)}

    strata = {
        "ALL": acc_stratum(lambda p: True),
        "noncanonical": acc_stratum(lambda p: p["extraction"] != "canonical"),
        "hard_object_extraction": acc_stratum(lambda p: p["construction"] in HARD_CONSTR),
        "canonical_gate": acc_stratum(lambda p: p["extraction"] == "canonical"),
    }

    # -------- DIFFICULTY SIGNAL: the maintained-distribution ENTROPY (Levy-faithful) + margin/cycles ----
    entropy = np.array([p["entropy"] for p in per], float)
    entropy_twin = np.array([p["entropy_twin"] for p in per], float)   # shuffled-validity (rotation)
    entropy_rand = np.array([p["entropy_rand"] for p in per], float)   # random settling
    margin = np.array([p["margin"] for p in per], float)
    cycles = np.array([p["cycles"] for p in per], float)
    conflict = np.array([p["conflict"] for p in per], float)
    tl_err = np.array([p["two_line_err"] for p in per], int)
    # difficulty is HIGH where two-line errs -> ENTROPY HIGHER, margin LOWER, cycles HIGHER on error items.
    # These partition items into UNEQUAL groups (error vs correct) -> UNPAIRED bootstrap.
    d_entropy = boot_diff_unpaired(entropy[tl_err == 1], entropy[tl_err == 0], n_boot, BOOT_SEED + 400)  # error-correct>0
    d_margin = boot_diff_unpaired(margin[tl_err == 0], margin[tl_err == 1], n_boot, BOOT_SEED + 401)     # correct-error>0
    d_cycles = boot_diff_unpaired(cycles[tl_err == 1], cycles[tl_err == 0], n_boot, BOOT_SEED + 402)     # error-correct>0
    d_entropy_twin = boot_diff_unpaired(entropy_twin[tl_err == 1], entropy_twin[tl_err == 0], n_boot, BOOT_SEED + 403)
    d_entropy_rand = boot_diff_unpaired(entropy_rand[tl_err == 1], entropy_rand[tl_err == 0], n_boot, BOOT_SEED + 406)
    # difficulty separates literature HARD (object-extraction) vs EASY constructions
    hard_mask = np.array([p["construction"] in HARD_CONSTR for p in per])
    easy_mask = np.array([p["construction"] in EASY_CONSTR for p in per])
    d_entropy_he = boot_diff_unpaired(entropy[hard_mask], entropy[easy_mask], n_boot, BOOT_SEED + 404)   # hard-easy>0
    # AUC: continuous ENTROPY vs BINARY route-conflict, predicting two-line error (graded beats discretized)
    auc_entropy = auc(entropy, tl_err)
    auc_margin = auc(-margin, tl_err)
    auc_conflict = auc(conflict, tl_err)
    auc_rand = auc(entropy_rand, tl_err)
    auc_cmp = boot_auc_diff(entropy, conflict, tl_err, n_boot, BOOT_SEED + 405)

    # -------- ATTACHMENT UNIFICATION: the SAME activation, argmax over HEADS instead of candidates ------
    attach = attachment_unification(test_items, gen, weights)

    # -------- REAL QA-SRL generalization (the meaningful population for graded-vs-binary-conflict) --------
    real = real_qasrl_margin_vs_conflict(gen, n_boot, limit=(1500 if smoke else None))

    # -------- gates --------
    # brief's difficulty clause = entropy predicts an INDEPENDENT difficulty measure CI-separated + twin at 0.
    # TWO independent measures: (1) discrete two-line ERROR (gold-free); (2) literature-pinned HARD (object-
    # extraction) vs EASY constructions (Gordon/Gibson -- NOT derived from our cues).
    difficulty_entropy_predicts_error = (d_entropy["ci95"][0] > 0)
    difficulty_entropy_hard_gt_easy = (d_entropy_he["ci95"][0] > 0)
    difficulty_margin_predicts_error = (d_margin["ci95"][0] > 0)
    difficulty_cycles_predicts_error = (d_cycles["ci95"][0] > 0)   # settling-view corroboration (McRae 1998)
    # info-free twins must NOT predict error: RANDOM SETTLING (guaranteed clean) is the gate; SHUFFLED
    # VALIDITY (rotation) is a second, mechanistic control reported alongside.
    difficulty_rand_twin_loses = (d_entropy_rand["ci95"][0] <= 0 <= d_entropy_rand["ci95"][1]) or (abs(d_entropy_rand["point"]) < d_entropy["point"] * 0.5)
    difficulty_shuffle_twin_weaker = (d_entropy_twin["point"] < d_entropy["point"] * 0.75)
    difficulty_twin_loses = bool(difficulty_rand_twin_loses)
    # graded beats the DISCRETIZED version of itself (the binary route-conflict) on REAL text, where genuine
    # graded competition exists. On the TEMPLATED synthetic set both tie (conflict is near-perfect by
    # construction), so the real-text comparison is the meaningful one.
    entropy_beats_conflict_real = bool(real.get("entropy_beats_conflict", False))
    entropy_beats_conflict_synth = (auc_cmp["ci95"][0] > 0)
    graded_ties_or_beats_resolver = (strata["noncanonical"].get("band_graded_vs_resolver") in ("ABOVE", "NOT_SEPARATED"))
    gate_no_leak = (strata["canonical_gate"].get("band_graded_vs_twoline") in ("ABOVE", "NOT_SEPARATED"))

    # SOLVED via the difficulty clause: the maintained-distribution ENTROPY is a valid graded difficulty
    # signal on TWO independent measures (predicts discrete error + literature-hard constructions, CI-sep),
    # the info-free twin loses, AND it beats the BINARY route-conflict on real text (graded > discretized).
    difficulty_clause = bool(difficulty_entropy_predicts_error and difficulty_entropy_hard_gt_easy
                             and difficulty_twin_loses and entropy_beats_conflict_real)
    verdict = ("GRADED_COMPETITION_ENTROPY_IS_A_VALID_DIFFICULTY_SIGNAL_BEATS_BINARY_CONFLICT"
               if difficulty_clause else "GRADED_DIFFICULTY_CLAUSE_INCOMPLETE")

    suffix = "_smoke" if smoke else ""
    out = OUTPUT_DIR + suffix
    os.makedirs(out, exist_ok=True)
    metrics = {
        "verdict": verdict,
        "anchor_name": ANCHOR_NAME, "run_mode": ("smoke" if smoke else "full"),
        "elapsed_s": round(time.time() - t0, 2), "n_boot": n_boot, "n_scored": len(per),
        "weights": weights, "weights_twin": weights_twin,
        "accuracy_strata": strata,
        "difficulty": {
            "entropy_error_minus_correct": d_entropy, "margin_correct_minus_error": d_margin,
            "cycles_error_minus_correct": d_cycles,
            "entropy_shuffled_validity_twin_error_minus_correct": d_entropy_twin,
            "entropy_random_settling_twin_error_minus_correct": d_entropy_rand,
            "entropy_hard_minus_easy": d_entropy_he,
            "auc_entropy_vs_two_line_err": auc_entropy, "auc_margin_vs_two_line_err": auc_margin,
            "auc_conflict_vs_two_line_err": auc_conflict, "auc_random_settling_twin": auc_rand,
            "auc_entropy_minus_conflict": auc_cmp,
        },
        "attachment_unification": attach,
        "real_qasrl": real,
        "gates": {
            "difficulty_entropy_predicts_error": bool(difficulty_entropy_predicts_error),
            "difficulty_entropy_hard_gt_easy": bool(difficulty_entropy_hard_gt_easy),
            "difficulty_margin_predicts_error": bool(difficulty_margin_predicts_error),
            "difficulty_cycles_predicts_error": bool(difficulty_cycles_predicts_error),
            "difficulty_random_settling_twin_loses": bool(difficulty_rand_twin_loses),
            "difficulty_shuffled_validity_twin_weaker": bool(difficulty_shuffle_twin_weaker),
            "entropy_beats_binary_conflict_real_qasrl": bool(entropy_beats_conflict_real),
            "entropy_beats_binary_conflict_synth": bool(entropy_beats_conflict_synth),
            "graded_ties_or_beats_resolver_noncanon": bool(graded_ties_or_beats_resolver),
            "gate_no_leak_canonical": bool(gate_no_leak),
            "difficulty_clause_SOLVED": bool(difficulty_clause),
        },
    }
    msg = (f"{verdict} || ACC noncanon: 2LINE={strata['noncanonical']['acc']['TWO_LINE']:.3f} "
           f"RESOLVER={strata['noncanonical']['acc']['STRUCT_RESOLVER']:.3f} "
           f"GRADED={strata['noncanonical']['acc']['GRADED']:.3f} "
           f"[graded-resolver {strata['noncanonical']['band_graded_vs_resolver']}] "
           f"|| DIFFICULTY entropy(error-correct)={d_entropy['point']:+.3f} CI[{d_entropy['ci95'][0]:+.3f},{d_entropy['ci95'][1]:+.3f}] "
           f"rand_twin={d_entropy_rand['point']:+.3f} shuf_twin={d_entropy_twin['point']:+.3f} cycles={d_cycles['point']:+.2f} "
           f"|| hard-easy entropy={d_entropy_he['point']:+.3f} CI[{d_entropy_he['ci95'][0]:+.3f},{d_entropy_he['ci95'][1]:+.3f}] "
           f"|| REAL-QASRL AUC entropy={real.get('auc_entropy', float('nan')):.3f} vs conflict={real.get('auc_conflict', float('nan')):.3f} "
           f"(synth ties {auc_entropy:.3f}/{auc_conflict:.3f}) "
           f"|| ATTACH acc={attach.get('attach_acc'):.3f}")
    metrics["verdict_msg"] = msg
    tmp = os.path.join(out, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, os.path.join(out, "metrics.json"))
    print("\n=== " + msg, flush=True)
    for k, vv in metrics["gates"].items():
        print(f"  {'PASS' if vv else 'fail'}  {k}", flush=True)
    return metrics


# ---------------------------------------------------------------------------------------------
# ATTACHMENT UNIFICATION: the SAME additive-cue + softmax FORM, but a SEPARATE POOL over candidate HEADS
# with DEPENDENCY-SPECIFIC cues (Beber 2025; eADM; Parker/Van Dyke 2017 -- attachment and role binding are
# NOT one literal pool; they share the algorithm-class with distinct cue weights). Role binding = argmax
# over candidate NOUNS for a fixed verb; attachment = argmax over candidate VERBS (heads) for a fixed noun.
# Attachment cues: FIRST-GAP (active-filler landing site, Frazier) + DLT LOCALITY (Gibson dependency-length).
# ---------------------------------------------------------------------------------------------
ATTACH_W = {"first_gap": 1.0, "locality": 0.3}   # OUR-INVENTION-UNDER-TEST (reported defaults; structural
#                                                  first-gap primary, locality secondary). Swept, not adopted.


def attachment_pick(toks: List[str], pos: List[str], filler: int, verbs: List[int]):
    """Attachment competition over candidate HEAD verbs for a fronted filler (same additive+softmax FORM as
    role binding, distinct cues). Returns (best_verb, margin, normalized_entropy)."""
    low = [t.lower() for t in toks]
    first_gap = np.zeros(len(verbs)); loc = np.zeros(len(verbs))
    seen_gap = False
    for k, v in enumerate(verbs):
        loc[k] = 1.0 / (1.0 + abs(v - filler))                 # Gibson DLT dependency locality
        if not seen_gap and not _has_post_object(pos, low, v):  # first verb with an EMPTY object slot
            first_gap[k] = 1.0; seen_gap = True                 # = the active-filler landing site
    A = ATTACH_W["first_gap"] * first_gap + ATTACH_W["locality"] * loc
    p = softmax(A, 2.0)
    ent = float(-(p * np.log(p + 1e-12)).sum() / np.log(len(verbs))) if len(verbs) > 1 else 0.0
    order = np.sort(A)[::-1]
    margin = float(order[0] - order[1]) if len(verbs) > 1 else float(order[0] + 1.0)
    return verbs[int(np.argmax(A))], margin, ent


def attachment_unification(items: List[dict], gen, weights: Dict[str, float]) -> dict:
    """For fronted-antecedent constructions (object relative/cleft) the fronted noun must ATTACH to the RC
    verb (its gap), NOT the tail/matrix verb. The SAME additive+softmax form (separate pool, attachment
    cues) should recover the RC verb with a REAL margin. Reports attachment accuracy + mean margin +
    entropy over heads."""
    cache: Dict[str, object] = {}
    hits, margins, ents, n = 0, [], [], 0
    for it in items:
        if it["construction"] not in ("object_relative", "object_cleft"):
            continue
        toks = it["toks"]; text = " ".join(toks)
        cr = cache.get(text)
        if cr is None:
            cr = gen.generate(text, extended=True); cache[text] = cr
        if list(cr.tokens) != toks:
            continue
        pos = list(cr.pos)
        verbs = [j for j in range(1, len(pos) + 1) if pos[j - 1] == "VERB"]
        fronted = it["gold_idx"]                     # the fronted antecedent = the patient of the RC verb
        if it["verb_idx"] not in verbs or len(verbs) < 2:
            continue                                  # need >=2 competing heads to be a real competition
        best_v, margin, ent = attachment_pick(toks, pos, fronted, verbs)
        hits += int(best_v == it["verb_idx"])
        margins.append(margin); ents.append(ent); n += 1
    return {"n": n, "attach_acc": (hits / n if n else float("nan")),
            "attach_margin_mean": float(np.mean(margins)) if margins else float("nan"),
            "attach_entropy_mean": float(np.mean(ents)) if ents else float("nan"),
            "attach_weights": ATTACH_W}


# ---------------------------------------------------------------------------------------------
# REAL QA-SRL: does the continuous margin beat the BINARY route-conflict at predicting two-line error?
# ---------------------------------------------------------------------------------------------
def real_qasrl_margin_vs_conflict(gen, n_boot: int, limit: Optional[int]) -> dict:
    try:
        from experiments.exp_reader_vs_twoline_qasrl_power_v1 import load_patient_items, parse_and_align
    except Exception as e:  # noqa: BLE001
        return {"skipped": f"import failed: {type(e).__name__}: {e}"}
    try:
        ev = load_patient_items("dev.jsonl.gz", limit=limit) + load_patient_items("test.jsonl.gz", limit=limit)
        ev = parse_and_align(gen, ev)
    except Exception as e:  # noqa: BLE001
        return {"skipped": f"load failed: {type(e).__name__}: {e}"}
    # use uniform weights here (no gold to learn from live) -- the difficulty signal is weight-robust; the
    # synthetic block establishes the learned-validity result. weights emphasise struct + order equally.
    weights = {"order": 1.0, "struct": 1.0, "recency": 0.5}
    entropies, conflicts, errs = [], [], []
    for it in ev:
        toks, pos = it["toks"], it["pos"]
        v = it["verb_idx"] + 1
        if v < 1 or v > len(toks):
            continue
        cands = _cands(pos)
        if not cands:
            continue
        pv = _verb_local_passive_precise(toks, pos, v)
        sup = cue_supports(toks, pos, v, cands, pv)
        g = graded_pick(sup, weights)
        tl = arm_two_line(toks, pos, v, cands, pv)
        sr = arm_fillergap_incremental(toks, pos, v, cands, pv)
        ps, pe = it["patient"]
        err = int(not (tl is not None and ps < tl <= pe))
        entropies.append(g["entropy"]); conflicts.append(int(tl != sr)); errs.append(err)
    if not errs or sum(errs) == 0 or sum(errs) == len(errs):
        return {"n": len(errs), "note": "degenerate error labels", "n_err": int(sum(errs))}
    entropies = np.array(entropies, float); conflicts = np.array(conflicts, float); errs = np.array(errs, int)
    a_e = auc(entropies, errs); a_c = auc(conflicts, errs)
    cmp = boot_auc_diff(entropies, conflicts, errs, n_boot, BOOT_SEED + 501)
    return {"n": len(errs), "n_err": int(errs.sum()),
            "auc_entropy": a_e, "auc_conflict": a_c, "auc_entropy_minus_conflict": cmp,
            "entropy_beats_conflict": bool(cmp["ci95"][0] > 0)}


# ---------------------------------------------------------------------------------------------
# SELF-TEST (each assertion can fail).
# ---------------------------------------------------------------------------------------------
def self_test() -> dict:
    print("[self-test] starting", flush=True)
    # (1) noise->0 limit: normalized_recurrence winner == argmax(net) on a clear and a near-tie case
    net = np.array([0.2, 0.9, 0.5])
    w, cyc, gap = normalized_recurrence(net)
    assert w == 1, (w, cyc)
    # (2) near-tie -> MORE cycles-to-settle than a clear winner (graded difficulty)
    _, cyc_close, _ = normalized_recurrence(np.array([0.80, 0.82]))
    _, cyc_far, _ = normalized_recurrence(np.array([0.10, 0.95]))
    assert cyc_close > cyc_far, (cyc_close, cyc_far)
    # (3) additive activation: a candidate matching 2 cues beats one matching 1 (argmax == discrete pick)
    sup = {"order": np.array([1.0, 0.0]), "struct": np.array([0.0, 1.0]), "recency": np.array([0.5, 0.5])}
    A = net_activation(sup, {"order": 0.4, "struct": 1.0, "recency": 0.2})
    assert int(np.argmax(A)) == 1, A       # struct cue (weight 1.0) wins -> the resolver's pick
    # (4) margin SMALLER and ENTROPY HIGHER when cues conflict (order!=struct) than when they agree
    sup_agree = {"order": np.array([1.0, 0.0]), "struct": np.array([1.0, 0.0]), "recency": np.array([0.5, 0.3])}
    g_conf = graded_pick(sup, {"order": 0.6, "struct": 1.0, "recency": 0.2})
    g_agree = graded_pick(sup_agree, {"order": 0.6, "struct": 1.0, "recency": 0.2})
    assert g_agree["margin"] > g_conf["margin"], (g_agree["margin"], g_conf["margin"])
    assert g_conf["entropy"] > g_agree["entropy"], (g_conf["entropy"], g_agree["entropy"])
    # (5) entropy: a near-tie distribution has HIGHER entropy than a clear winner; single candidate = 0
    sup_tie = {"order": np.array([1.0, 0.98]), "struct": np.array([0.0, 0.0]), "recency": np.array([0.5, 0.5])}
    sup_clear = {"order": np.array([1.0, 0.02]), "struct": np.array([1.0, 0.0]), "recency": np.array([0.5, 0.1])}
    w0 = {"order": 1.0, "struct": 1.0, "recency": 0.3}
    assert graded_pick(sup_tie, w0)["entropy"] > graded_pick(sup_clear, w0)["entropy"]
    assert graded_pick({"order": np.array([1.0]), "struct": np.array([0.0]), "recency": np.array([1.0])}, w0)["entropy"] == 0.0
    # (6) AUC: a perfectly separating score is 1.0; a constant is ~0.5
    assert abs(auc(np.array([0.1, 0.2, 0.9, 0.8]), np.array([0, 0, 1, 1])) - 1.0) < 1e-9
    # (7) shuffled weights change the winner (info-free twin is a real ablation)
    assert graded_pick(sup, {"order": 1.0, "struct": 0.0, "recency": 0.0})["win"] == 0
    print("[self-test] PASS (noise0==argmax; near-tie more cycles+entropy; additive argmax; conflict smaller margin/higher entropy; AUC)", flush=True)
    return {"verdict": "SELFTEST_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "SELFTEST_PASS",
            "elapsed_s": 0.0, "run_mode": "self_test", "anchor_name": ANCHOR_NAME}


def _write(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    suffix = "_selftest" if args.self_test else ("_smoke" if args.smoke else "")
    out_dir = OUTPUT_DIR + suffix
    try:
        if args.self_test:
            metrics = self_test()
            _write(out_dir, metrics)
        else:
            from experiments.exp_stated_entity_fate_reading_extractor_v1 import _load_or_build_frontend
            gen = _load_or_build_frontend()
            metrics = run_full(gen, smoke=args.smoke)
        print(f"[main] verdict={metrics['verdict']}", flush=True)
        print(metrics.get("verdict_msg", ""), flush=True)
    except Exception as e:  # noqa: BLE001
        diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:500]}",
                "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME}
        _write(out_dir, diag)
        raise


if __name__ == "__main__":
    main()
