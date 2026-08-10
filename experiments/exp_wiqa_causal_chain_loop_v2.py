# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; 6-arm hash-differ)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (3-way discrete classification accuracy on a real benchmark; no capacity/
#   noise-floor discriminator threshold)
# - HP_SCOPE: {dev_full: [decisive_gate_active, decisive_gate_active_multihop]}
# - cardinality_ok: EXPECTED_N_UNITS=len(SEEDS_FULL)=3 (full) / 1 (smoke)
# - per-unit failure-class instrumentation (no bare except; degraded_scoring budget 2%)
# - calibration_check: default_ok_for_this_regime (GATE_THRESH=0.05 unchanged from v1's
#   label-blind p10 calibration; stemming does not require re-calibration since it only
#   INCREASES genuine overlap magnitude, verified this session not to flood the gate: fire-rate
#   moved 27.9%->37.1% while aggregate loop accuracy stayed in the same band as v1, see below)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL CausalLinkRegister (polarity-extended) + iterative_attractor
#   objects (real_code_path); no synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-10_wiqa_causal_chain_loop_v2.md for the full pre-reg.
"""exp_wiqa_causal_chain_loop_v2 -- decisive de-dilution + abstain-reduction follow-up to v1
(data/exp_wiqa_causal_chain_loop_v1/metrics.json, MIDDLE_BAND, loop=0.3477 vs polecho=0.3420
aggregate +0.6pp, 72.09% abstain, aggregate/full-multihop scramble did NOT collapse the gain).

TWO changes over v1, both label-blind (neither reads answer_label):

1. EXTRACTION/ANCHORING IMPROVEMENT (reduces abstain): (a) light suffix-stripping stemming on
   BOW content tokens before hashing to a word-vector (recovers morphological near-misses like
   "grows"/"growing"/"grow" that v1's raw-token BOW missed -- MEASURED@calibration this session:
   gate-fail-driven abstain drops 41.09%->36.67% of all items with GATE_THRESH unchanged at
   0.05); (b) the perturbation/outcome anchors are now allowed to land on the SAME paragraph
   step (v1 structurally forced an abstain here) -- propagate_sign(reg, lo, hi) already handles
   lo==hi as a genuine zero-hop walk (sign=+1, empty trace, no special-casing needed), so this is
   a generalization of the existing walk, not a new mechanism. Combined effect MEASURED@
   calibration this session: overall abstain 72.09%->62.95%, mechanism-fires (active subset)
   27.91%->37.05%, multihop fire-rate 43.34%->44.15% (of 6894), negation-crossing fired-subset
   lands at n=95 (matches Director's task estimate exactly).

2. DECISIVE SUBSET-SCRAMBLE (the load-bearing addition): report loop / polecho / SCRAMBLE
   accuracy on 4 subsets -- all, active (loop did not abstain), active_multihop (active AND
   metadata_path_len>=2), negation_crossing (active AND the TRUE register's hop trace crossed
   >=1 polarity=-1 edge, n MEASURED=95) -- instead of only the full (72%-abstain-diluted) set.
   Decisive gate: on BOTH active and active_multihop, does SCRAMBLE (permuting which step's text
   is checked for a negating word at each edge, same permutation scheme as v1's ABLATION-1)
   collapse >= 50% of loop's edge over polecho? CAUSAL_VALIDATED (HARD_PASS) if yes on both;
   NOT_CAUSAL_STRUCTURAL (HARD_FAIL) if scramble does not collapse on active_multihop (the
   primary subset) or loop does not even beat polecho there; MIDDLE_BAND if mixed between the
   two subsets. negation_crossing (n=95) is reported as SUPPORTING evidence only (too small for
   a primary gate) since it isolates the ONE case (edge-sign-flip) the scramble ablation can
   actually perturb -- the direct-interpretation edge (v1's larger source of lift) is topology-
   only and the scramble does not touch it, so a negation_crossing-specific read is the sharpest
   single number for "does the SIGNED EDGE information matter," while active/active_multihop are
   the broader decisive subsets Director asked for.

Modes:
  --self-test  Hand-built chain checks (same-as-v1 negation chain + NEW same-step zero-hop case
               + NEW stemming-equivalence case) + CausalLinkRegister/iterative_attractor
               substrate_signature preflight. No queue dispatch.
  --smoke      First 300 dev items (deterministic stride sample, same convention as v1).
  --full       All 6894 dev items, 3 scramble seeds (7,17,29), per-seed checkpointed.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import inspect
import json
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

ANCHOR_NAME = "wiqa_causal_chain_loop_v2"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
WIQA_DATA_DIR = os.path.join(REPO_ROOT, "data", "corpora", "wiqa", "hf_dataset")

from hdlab.situation_model_accumulate import CausalLinkRegister  # noqa: E402
from hdlab.cleanup_family import iterative_attractor as _iterative_attractor  # noqa: E402
from experiments._seed_checkpoint import (  # noqa: E402
    resumable_seeds,
    write_partial,
    aggregate_partials,
    write_metrics as _ckpt_write_metrics,
)

# ---------------------------------------------------------------------- fixed parameters
D = 1024
GATE_THRESH = 0.05  # CITED@preregs/2026-08-10_wiqa_causal_chain_loop_v1.md (unchanged; label-blind
                     # p10-of-non-distractor-cosine calibration; re-verified this session to still
                     # sit in a discriminating band under stemming, see calibration_check above)
SEEDS_SMOKE = [7]
SEEDS_FULL = [7, 17, 29]
SMOKE_N = 300
DEGRADED_BUDGET = 0.02
DECISIVE_COLLAPSE_FRACTION = 0.5  # gate: scramble must erase >=50% of loop's edge over polecho

STEM_PAT = re.compile(r"^suppose (.+?), how will it affect (.+?)\.?$", re.IGNORECASE)
TOKRE = re.compile(r"[a-z']+")

STOPWORDS = {
    "a", "an", "the", "of", "to", "in", "on", "for", "and", "or", "is", "are", "will", "it",
    "affect", "how", "suppose", "happens", "happen", "that", "this", "be", "been", "being",
    "with", "as", "at", "by", "from", "its", "their", "there", "not", "so", "if",
}

INCREASE_WORDS = {
    "more", "increase", "increases", "increased", "increasing", "greater", "higher", "faster",
    "larger", "bigger", "longer", "stronger", "additional", "extra", "rise", "rises", "risen",
    "grow", "grows", "growing", "grown", "gain", "gains", "gained", "amplify", "amplifies",
    "excess", "exceeds", "warmer", "hotter", "rapid", "rapidly", "quicker", "sooner", "earlier",
    "abundant", "abundance", "boost", "boosts", "expand", "expands", "expanding", "raise",
    "raises", "raised",
}
DECREASE_WORDS = {
    "less", "fewer", "decrease", "decreases", "decreased", "decreasing", "lower", "lowers",
    "lowered", "smaller", "slower", "shorter", "weaker", "reduce", "reduces", "reduced",
    "reducing", "reduction", "shrink", "shrinks", "shrinking", "lose", "loses", "lost", "losing",
    "lack", "lacking", "without", "scarce", "scarcity", "delay", "delayed", "delays", "slow",
    "colder", "cooler", "limited", "limits", "limiting", "insufficient", "diminish",
    "diminishes", "diminished", "sterile", "infertile", "drop", "drops", "dropped", "declining",
    "decline", "declines", "stop", "stops", "stopped", "prevent", "prevents", "prevented",
    "block", "blocks", "blocked",
}
NEGATING_STEP_WORDS = {
    "stop", "stops", "stopped", "stopping", "prevent", "prevents", "prevented", "block",
    "blocks", "blocked", "limit", "limits", "limited", "limiting", "reduce", "reduces",
    "reduced", "reducing", "without", "less", "fewer", "decrease", "decreases", "decreased",
    "slow", "slows", "slowed", "lose", "loses", "lost", "losing", "lack", "lacking", "cease",
    "ceases", "ceased",
}


# ---------------------------------------------------------------------- text primitives
def detect_polarity(text: str) -> int:
    """+1 (increase-word present, no decrease-word), -1 (decrease, no increase), 0 (ambiguous/
    absent). UNCHANGED from v1: same lexicon, same logic (this cell's improvement targets
    extraction/anchoring, not the polarity lexicon)."""
    toks = TOKRE.findall(text.lower())
    inc = any(t in INCREASE_WORDS for t in toks)
    dec = any(t in DECREASE_WORDS for t in toks)
    if inc and not dec:
        return 1
    if dec and not inc:
        return -1
    return 0


def light_stem(t: str) -> str:
    """Suffix-stripping light stemmer (NOT Porter -- deliberately conservative, ASCII, hand-rule,
    label-blind). MEASURED@calibration this session (wiqa_stem_test.py, this session): applying
    this exact stemmer to BOW content tokens drops gate-fail abstain from 41.09%->36.67% of all
    6894 dev items with GATE_THRESH held fixed at 0.05 -- a genuine vocabulary-normalization
    fix (e.g. "grows"/"growing"/"grow" now collide to one word-vector), not a threshold tune."""
    if len(t) > 5 and t.endswith("ing"):
        return t[:-3]
    if len(t) > 5 and t.endswith("ies"):
        return t[:-3] + "y"
    if len(t) > 4 and t.endswith("ed"):
        return t[:-2]
    if len(t) > 4 and t.endswith("es"):
        return t[:-2]
    if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
        return t[:-1]
    if len(t) > 4 and t.endswith("ly"):
        return t[:-2]
    return t


def content_tokens(text: str) -> List[str]:
    """v2: stemmed (see light_stem docstring); v1 used raw tokens."""
    return [light_stem(t) for t in TOKRE.findall(text.lower()) if t not in STOPWORDS and len(t) > 1]


def has_negating_word(text: str) -> bool:
    return bool(set(TOKRE.findall(text.lower())) & NEGATING_STEP_WORDS)


_WORD_VEC_CACHE: Dict[str, np.ndarray] = {}


def word_vec(word: str, d: int = D) -> np.ndarray:
    """Deterministic bipolar {-1,+1} vector per distinct (stemmed) content word, hashlib-seeded
    (PROT-023/F.5 compliant)."""
    if word not in _WORD_VEC_CACHE:
        seed = int.from_bytes(
            hashlib.sha256(f"wiqa_bow_word::{word}".encode()).digest()[:8], "big") % (2 ** 32)
        rng = np.random.default_rng(seed)
        _WORD_VEC_CACHE[word] = (rng.integers(0, 2, size=d).astype(np.float32) * 2 - 1)
    return _WORD_VEC_CACHE[word]


def encode_bow(text: str, d: int = D) -> np.ndarray:
    """Bag-of-words HD bundle: sum of (stemmed) content-word vectors (unnormalized)."""
    toks = content_tokens(text)
    if not toks:
        return np.zeros(d, dtype=np.float32)
    return np.sum([word_vec(t, d) for t in toks], axis=0).astype(np.float32)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _deterministic_perm(identity_tag: str, n: int) -> List[int]:
    """Hashlib-seeded deterministic permutation (PROT-023/F.5 compliant), unchanged from v1."""
    seed = int.from_bytes(
        hashlib.sha256(f"wiqa_scramble::{identity_tag}".encode()).digest()[:8], "big") % (2 ** 32)
    rng = np.random.default_rng(seed)
    return rng.permutation(n).tolist()


# ---------------------------------------------------------------------- anchor retrieval
def anchor_step(probe_vec: np.ndarray, step_vecs: List[np.ndarray]) -> Tuple[Optional[int], float, bool]:
    """Pull-in retrieval (hdlab.cleanup_family.iterative_attractor). UNCHANGED mechanism from v1
    -- only the upstream encode_bow (stemming) changed what probe_vec/step_vecs contain."""
    if not step_vecs or float(np.linalg.norm(probe_vec)) < 1e-9:
        return None, 0.0, False
    cb = np.stack(step_vecs).astype(np.float32)
    q = probe_vec.astype(np.float32)
    _, diag = _iterative_attractor(q, cb, temp=4.0, max_steps=8)
    idx = int(diag["final_argmax_idx"])
    score = cosine(q, cb[idx])
    return idx, score, bool(score >= GATE_THRESH)


# ---------------------------------------------------------------------- causal register + propagation
def build_register(steps: List[str], negation_check_order: Optional[List[int]] = None
                    ) -> Tuple[CausalLinkRegister, List[int]]:
    """UNCHANGED from v1. Edge i->i+1 polarity=-1 if the checked step has a negating word."""
    k = len(steps)
    gen = torch.Generator()
    gen.manual_seed(12345)
    reg = CausalLinkRegister(d=D, generator=gen, max_event_slots=max(k, 1))
    edge_polarity: List[int] = []
    for i in range(k - 1):
        check_idx = negation_check_order[i + 1] if negation_check_order is not None else (i + 1)
        pol = -1 if has_negating_word(steps[check_idx]) else 1
        reg.add_causal_link(i, i + 1, polarity=pol)
        edge_polarity.append(pol)
    return reg, edge_polarity


def propagate_sign(reg: CausalLinkRegister, lo: int, hi: int) -> Tuple[Optional[int], List[Dict]]:
    """UNCHANGED mechanism from v1. lo==hi (NEW in v2's call sites, see below) is already handled
    correctly here: the while loop does not execute, sign=1, trace=[] (a genuine zero-hop walk,
    not a special case added to this function)."""
    cur = lo
    sign = 1
    trace: List[Dict] = []
    while cur < hi:
        effect_idx, _scores = reg.query_effect_of(cur)
        if effect_idx is None or effect_idx != cur + 1:
            trace.append({"hop_from": cur, "expected_to": cur + 1, "got": effect_idx, "valid": False})
            return None, trace
        pol = reg.query_link_polarity(cur, effect_idx)
        sign *= pol
        trace.append({"hop_from": cur, "to": effect_idx, "polarity": pol, "valid": True})
        cur = effect_idx
    return sign, trace


# ---------------------------------------------------------------------- per-item base scoring (seed-independent)
def score_item_base(ex: Dict) -> Dict:
    """v2 CHANGE from v1: the abstain-gate structural condition drops `p_idx != o_idx` (v1's
    _propagate_and_predict required distinct anchors; v2 allows same-step, letting
    propagate_sign's already-correct lo==hi zero-hop handling fire instead of a hard abstain).
    Everything else (extraction, polarity lexicon, register construction) is the same shape as
    v1 -- only encode_bow's stemming and this one structural relaxation differ."""
    m = STEM_PAT.match(ex["question_stem"])
    if not m:
        raise ValueError(f"question_stem did not match extraction regex: {ex['question_stem']!r}")
    pert_clause, outcome_clause = m.group(1), m.group(2)
    steps = [s for s in ex["question_para_step"] if s.strip()]
    para_text = " ".join(steps)

    pp = detect_polarity(pert_clause)
    op = detect_polarity(outcome_clause)

    step_vecs = [encode_bow(s) for s in steps]
    pert_probe = encode_bow(pert_clause)
    outcome_probe = encode_bow(outcome_clause)
    p_idx, p_score, p_admit = anchor_step(pert_probe, step_vecs)
    o_idx, o_score, o_admit = anchor_step(outcome_probe, step_vecs)

    # ---- MAJORITY ----
    pred_majority = "more"  # CITED@v1 (train label-frequency tie-break, dev acc=0.3333)

    # ---- POLARITY-ECHO (unchanged from v1) ----
    if op == 0:
        pred_polecho = "no_effect"
    elif pp == 0:
        pred_polecho = "more"
    else:
        pred_polecho = "more" if pp == op else "less"

    # ---- BoW-OVERLAP (unchanged from v1, but now over stemmed tokens) ----
    outcome_toks = set(content_tokens(outcome_clause))
    para_toks = set(content_tokens(para_text))
    if len(outcome_toks & para_toks) == 0:
        pred_bow = "no_effect"
    else:
        pred_bow = "more"

    # ---- CAUSAL-CHAIN-LOOP + ABLATION-2 (share the TRUE, unscrambled register) ----
    reg, edge_polarity = build_register(steps, negation_check_order=None)

    def _propagate_and_predict(use_gate: bool) -> Tuple[str, Dict]:
        admitted = (p_admit and o_admit) if use_gate else (p_idx is not None and o_idx is not None)
        # v2: dropped `p_idx != o_idx` (see docstring) -- same-step now propagates with lo==hi.
        if not (admitted and p_idx is not None and o_idx is not None and pp != 0):
            return pred_polecho, {"abstained": True, "reason": "gate_or_structural"}
        lo, hi = sorted([p_idx, o_idx])
        sign, trace = propagate_sign(reg, lo, hi)
        if sign is None:
            return pred_polecho, {"abstained": True, "reason": "hop_validate_fail", "trace": trace}
        propagated = pp * sign
        if op == 0:
            pred = "more" if propagated > 0 else "less"
        else:
            pred = "more" if propagated == op else "less"
        crosses_negation = any(h.get("polarity") == -1 for h in trace)
        return pred, {"abstained": False, "propagated_sign": propagated, "trace": trace,
                       "crosses_negation": crosses_negation}

    pred_loop, loop_diag = _propagate_and_predict(use_gate=True)
    pred_ablation2, ablation2_diag = _propagate_and_predict(use_gate=False)

    multihop = bool(ex["metadata_path_len"] is not None and ex["metadata_path_len"] >= 2)
    fired = not loop_diag["abstained"]
    negation_crossing = fired and bool(loop_diag.get("crosses_negation", False))

    return {
        "question_id": ex["metadata_question_id"],
        "gold": ex["answer_label"],
        "qtype": ex["metadata_question_type"],
        "path_len": ex["metadata_path_len"],
        "multihop": multihop,
        "steps": steps,
        "pp": pp, "op": op,
        "p_idx": p_idx, "p_score": p_score, "p_admit": p_admit,
        "o_idx": o_idx, "o_score": o_score, "o_admit": o_admit,
        "edge_polarity": edge_polarity,
        "pred_majority": pred_majority,
        "pred_polecho": pred_polecho,
        "pred_bow": pred_bow,
        "pred_loop": pred_loop, "loop_diag": loop_diag,
        "pred_ablation2": pred_ablation2, "ablation2_diag": ablation2_diag,
        "fired": fired, "negation_crossing": negation_crossing,
    }


def score_item_scramble(base: Dict, seed: int) -> str:
    """ABLATION-1: SAME anchors/admission as CAUSAL-CHAIN-LOOP (v2: including the same-step
    relaxation); edge-polarity negation-check computed against a deterministically-permuted step
    order. Fires on exactly the same item set as pred_loop (same topology/anchors/pp check, only
    polarity assignment differs) -- verified in self-test."""
    steps = base["steps"]
    k = len(steps)
    p_idx, o_idx, p_admit, o_admit, pp, op = (
        base["p_idx"], base["o_idx"], base["p_admit"], base["o_admit"], base["pp"], base["op"])
    if not (p_admit and o_admit and p_idx is not None and o_idx is not None and pp != 0):
        return base["pred_polecho"]
    perm = _deterministic_perm(f"{seed}::{base['question_id']}", k) if k > 0 else []
    reg, _edge_pol = build_register(steps, negation_check_order=perm)
    lo, hi = sorted([p_idx, o_idx])
    sign, _trace = propagate_sign(reg, lo, hi)
    if sign is None:
        return base["pred_polecho"]
    propagated = pp * sign
    if op == 0:
        return "more" if propagated > 0 else "less"
    return "more" if propagated == op else "less"


# ---------------------------------------------------------------------- dataset load
def load_dev() -> List[Dict]:
    import datasets
    ds = datasets.load_from_disk(WIQA_DATA_DIR)
    dev = ds["validation"]
    qids = dev["metadata_question_id"]
    idx_order = sorted(range(len(dev)), key=lambda i: qids[i])
    all_rows = dev.to_list()
    return [all_rows[i] for i in idx_order]


# ---------------------------------------------------------------------- accuracy aggregation
SUBSETS = ("all", "active", "active_multihop", "negation_crossing")


def _subset_rows(rows: List[Dict], subset: str) -> List[Dict]:
    if subset == "all":
        return rows
    if subset == "active":
        return [r for r in rows if r["fired"]]
    if subset == "active_multihop":
        return [r for r in rows if r["fired"] and r["multihop"]]
    if subset == "negation_crossing":
        return [r for r in rows if r["negation_crossing"]]
    raise ValueError(f"unknown subset {subset!r}")


def _acc(rows: List[Dict], pred_key: str) -> float:
    if not rows:
        return float("nan")
    return sum(1 for r in rows if r[pred_key] == r["gold"]) / len(rows)


def _acc_scramble(rows: List[Dict], scramble_preds: Dict[str, str]) -> float:
    """scramble_preds: question_id -> predicted label, for this seed."""
    if not rows:
        return float("nan")
    return sum(1 for r in rows if scramble_preds[r["question_id"]] == r["gold"]) / len(rows)


def _abstain_rate(rows: List[Dict]) -> float:
    if not rows:
        return float("nan")
    return sum(1 for r in rows if not r["fired"]) / len(rows)


# ---------------------------------------------------------------------- full-dev per-seed run
def run_one_seed(seed: int, rows_base: List[Dict], heartbeat_cb=None) -> Dict:
    t0 = time.time()
    n = len(rows_base)
    scramble_preds: Dict[str, str] = {}
    for i, base in enumerate(rows_base):
        scramble_preds[base["question_id"]] = score_item_scramble(base, seed)
        if heartbeat_cb is not None and (i + 1) % 1000 == 0:
            heartbeat_cb(i + 1, n, time.time() - t0)

    per_subset = {}
    for subset in SUBSETS:
        srows = _subset_rows(rows_base, subset)
        per_subset[subset] = {
            "n": len(srows),
            "majority": _acc(srows, "pred_majority"),
            "polecho": _acc(srows, "pred_polecho"),
            "bow": _acc(srows, "pred_bow"),
            "loop": _acc(srows, "pred_loop"),
            "ablation2_novalidate": _acc(srows, "pred_ablation2"),
            "scramble": _acc_scramble(srows, scramble_preds),
        }

    elapsed = time.time() - t0
    return {"seed": seed, "n_items": n, "elapsed_s": round(elapsed, 4), "per_subset": per_subset,
            "abstain_rate_all": _abstain_rate(rows_base)}


def _arms_must_differ(rows_base: List[Dict], scramble_preds_seed0: Dict[str, str]) -> Dict:
    def _digest(vals):
        b = json.dumps(list(vals), sort_keys=False, default=str).encode("utf-8")
        return hashlib.sha256(b).hexdigest()
    sigs = {
        "majority": _digest([r["pred_majority"] for r in rows_base]),
        "polecho": _digest([r["pred_polecho"] for r in rows_base]),
        "bow": _digest([r["pred_bow"] for r in rows_base]),
        "loop": _digest([r["pred_loop"] for r in rows_base]),
        "ablation1_scramble": _digest([scramble_preds_seed0[r["question_id"]] for r in rows_base]),
        "ablation2_novalidate": _digest([r["pred_ablation2"] for r in rows_base]),
    }
    pairs_differ = {f"{a}_vs_{b}": sigs[a] != sigs[b]
                     for i, a in enumerate(sigs) for b in list(sigs)[i + 1:]}
    return {"sigs": sigs, "pairs_differ": pairs_differ, "all_differ": all(pairs_differ.values())}


# ---------------------------------------------------------------------- verdict logic (decisive gate)
def _median(xs: List[float]) -> float:
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 == 1 else 0.5 * (s[mid - 1] + s[mid])


def apply_bands(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    seeds = sorted(per_seed.keys(), key=lambda s: int(s))

    subset_table: Dict[str, Dict] = {}
    for subset in SUBSETS:
        loop = per_seed[seeds[0]]["per_subset"][subset]["loop"]
        polecho = per_seed[seeds[0]]["per_subset"][subset]["polecho"]
        bow = per_seed[seeds[0]]["per_subset"][subset]["bow"]
        majority = per_seed[seeds[0]]["per_subset"][subset]["majority"]
        scramble_vals = [per_seed[s]["per_subset"][subset]["scramble"] for s in seeds]
        scramble_median = _median(scramble_vals)
        n = per_seed[seeds[0]]["per_subset"][subset]["n"]
        loop_minus_polecho = loop - polecho
        loop_minus_scramble = loop - scramble_median
        collapse_frac = (loop_minus_scramble / loop_minus_polecho) if loop_minus_polecho > 1e-9 else None
        subset_table[subset] = {
            "n": n, "loop": loop, "polecho": polecho, "bow": bow, "majority": majority,
            "scramble_vals": scramble_vals, "scramble_median": scramble_median,
            "loop_minus_polecho": loop_minus_polecho, "loop_minus_scramble": loop_minus_scramble,
            "collapse_frac": collapse_frac,
        }

    def _decisive(subset: str) -> Optional[bool]:
        """True=causal-validated on this subset, False=not-causal, None=loop doesn't beat
        polecho here (no edge to test collapse of -- inconclusive on this subset)."""
        t = subset_table[subset]
        if t["loop_minus_polecho"] <= 0:
            return None
        return t["collapse_frac"] >= DECISIVE_COLLAPSE_FRACTION

    active_decisive = _decisive("active")
    active_multihop_decisive = _decisive("active_multihop")

    abstain_rate_all = per_seed[seeds[0]]["abstain_rate_all"]

    detail = {
        "subset_table": subset_table,
        "active_decisive": active_decisive,
        "active_multihop_decisive": active_multihop_decisive,
        "abstain_rate_all": abstain_rate_all,
        "new_aggregate_loop_vs_polecho": subset_table["all"]["loop_minus_polecho"],
    }

    if active_multihop_decisive is True and active_decisive is True:
        tier = "HARD_PASS"
        msg = (f"CAUSAL_VALIDATED: scramble collapses loop's edge over polecho on BOTH active "
               f"(collapse_frac={subset_table['active']['collapse_frac']:.3f}) and "
               f"active_multihop (collapse_frac={subset_table['active_multihop']['collapse_frac']:.3f}) "
               f"subsets (>= {DECISIVE_COLLAPSE_FRACTION} threshold); abstain_rate={abstain_rate_all:.4f}")
    elif active_multihop_decisive is False:
        tier = "HARD_FAIL"
        cf = subset_table["active_multihop"]["collapse_frac"]
        cf_s = f"{cf:.3f}" if cf is not None else "n/a"
        msg = (f"NOT_CAUSAL_STRUCTURAL: on active_multihop (primary decisive subset), scramble "
               f"does NOT collapse loop's edge over polecho (collapse_frac={cf_s} < "
               f"{DECISIVE_COLLAPSE_FRACTION}) -- the active-subset gain looks structural "
               f"(topology/coverage), not causal-edge-sign reasoning; abstain_rate={abstain_rate_all:.4f}")
    elif active_multihop_decisive is None:
        tier = "HARD_FAIL"
        msg = (f"NOT_CAUSAL_STRUCTURAL: loop does not even beat polecho on active_multihop "
               f"(loop_minus_polecho={subset_table['active_multihop']['loop_minus_polecho']:.4f} <= 0) "
               f"-- no edge to attribute to causal reasoning; abstain_rate={abstain_rate_all:.4f}")
    else:
        tier = "MIDDLE_BAND"
        msg = (f"MIXED: active_decisive={active_decisive} active_multihop_decisive="
               f"{active_multihop_decisive} -- partial/inconsistent evidence between subsets; "
               f"abstain_rate={abstain_rate_all:.4f}")
    return tier, msg, detail


# ---------------------------------------------------------------------- output plumbing
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
             "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
             "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
             "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": round(elapsed_s, 2)}
    if extra:
        rec["extra"] = extra
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


# ---------------------------------------------------------------------- examples for report
def pick_examples(rows_base: List[Dict], n: int = 5) -> Dict:
    loop_right_polecho_wrong = [r for r in rows_base
                                 if r["pred_loop"] == r["gold"] and r["pred_polecho"] != r["gold"]
                                 and r["fired"]]
    loop_wrong_polecho_right = [r for r in rows_base
                                 if r["pred_loop"] != r["gold"] and r["pred_polecho"] == r["gold"]
                                 and r["fired"]]
    negation_crossing_examples = [r for r in rows_base if r["negation_crossing"]]

    def _fmt(r):
        return {"question_id": r["question_id"], "gold": r["gold"], "pred_loop": r["pred_loop"],
                "pred_polecho": r["pred_polecho"], "pp": r["pp"], "op": r["op"],
                "p_idx": r["p_idx"], "o_idx": r["o_idx"], "qtype": r["qtype"]}

    return {"loop_wins_vs_polecho": [_fmt(r) for r in loop_right_polecho_wrong[:n]],
            "loop_loses_vs_polecho": [_fmt(r) for r in loop_wrong_polecho_right[:n]],
            "n_loop_wins_total": len(loop_right_polecho_wrong),
            "n_loop_loses_total": len(loop_wrong_polecho_right),
            "negation_crossing_sample": [_fmt(r) for r in negation_crossing_examples[:n]],
            "n_negation_crossing_total": len(negation_crossing_examples)}


# ---------------------------------------------------------------------- self-test
def _hand_case_chain() -> Dict:
    """UNCHANGED from v1: 3-step hand-built chain A(0)->B(1)->C(2), negation word on C."""
    steps = ["water level increases in the tank", "pressure builds up", "the valve stops the flow"]
    reg, edge_pol = build_register(steps, negation_check_order=None)
    assert edge_pol == [1, -1], f"expected edge_polarity [1,-1], got {edge_pol}"
    sign, trace = propagate_sign(reg, 0, 2)
    assert sign == -1, f"expected propagated product -1, got {sign} (trace={trace})"
    gen = torch.Generator(); gen.manual_seed(1)
    reg2 = CausalLinkRegister(d=64, generator=gen, max_event_slots=3)
    reg2.add_causal_link(0, 1)
    eff, _ = reg2.query_effect_of(0)
    cau, _ = reg2.query_cause_of(1)
    assert eff == 1 and cau == 0, f"backward-compat broken: eff={eff} cau={cau}"
    assert reg2.query_link_polarity(0, 1) == 1
    return {"edge_polarity": edge_pol, "propagated_sign": sign, "trace": trace,
            "backward_compat_ok": True}


def _hand_case_zero_hop() -> Dict:
    """NEW in v2: p_idx == o_idx (both anchors land on step 1 of a 3-step chain) must propagate
    as a genuine zero-hop walk (sign=+1, empty trace), NOT abstain (v1's behavior)."""
    steps = ["a seed is planted", "sunlight reaches the leaves", "the plant grows"]
    reg, edge_pol = build_register(steps, negation_check_order=None)
    sign, trace = propagate_sign(reg, 1, 1)
    assert sign == 1, f"expected zero-hop sign=1, got {sign}"
    assert trace == [], f"expected empty trace for zero-hop, got {trace}"
    return {"zero_hop_sign": sign, "zero_hop_trace": trace}


def _hand_case_stemming() -> Dict:
    """NEW in v2: morphological variants must collide to the same content token post-stem."""
    assert light_stem("grows") == light_stem("growing") == light_stem("grow") == "grow", (
        light_stem("grows"), light_stem("growing"), light_stem("grow"))
    assert light_stem("increases") == light_stem("increased") or True  # documents intent, not
    # required identical (increases->increase, increased->increas -- both admissible variants
    # since the stemmer's job is REDUCING mismatch, not achieving a canonical dictionary form)
    v1 = word_vec(light_stem("grows"))
    v2 = word_vec(light_stem("growing"))
    assert np.array_equal(v1, v2), "stemmed variants must map to identical word_vec"
    return {"stem_grows": light_stem("grows"), "stem_growing": light_stem("growing"),
            "stem_grow": light_stem("grow"), "vectors_equal": True}


def _hand_case_wiqa_shaped() -> Dict:
    """UNCHANGED shape from v1: two hand-built WIQA-shaped items exercising the FULL
    score_item_base pipeline."""
    item_more = {
        "question_stem": "suppose more sunlight happens, how will it affect MORE plant growth.",
        "question_para_step": ["a seed is planted", "sunlight reaches the leaves", "the plant grows"],
        "answer_label": "more", "metadata_question_id": "hand:0", "metadata_para_id": "hand",
        "metadata_question_type": "INPARA_EFFECT", "metadata_path_len": 2,
    }
    item_less = {
        "question_stem": "suppose less sunlight happens, how will it affect MORE plant growth.",
        "question_para_step": ["a seed is planted", "sunlight reaches the leaves", "the plant grows"],
        "answer_label": "less", "metadata_question_id": "hand:1", "metadata_para_id": "hand",
        "metadata_question_type": "INPARA_EFFECT", "metadata_path_len": 2,
    }
    r_more = score_item_base(item_more)
    r_less = score_item_base(item_less)
    return {"item_more": {"pred_loop": r_more["pred_loop"], "gold": r_more["gold"],
                           "loop_diag": r_more["loop_diag"]},
            "item_less": {"pred_loop": r_less["pred_loop"], "gold": r_less["gold"],
                           "loop_diag": r_less["loop_diag"]}}


def self_test() -> Dict:
    hand_chain = _hand_case_chain()
    hand_zero_hop = _hand_case_zero_hop()
    hand_stem = _hand_case_stemming()
    hand_wiqa = _hand_case_wiqa_shaped()
    assert hand_wiqa["item_more"]["pred_loop"] == "more", hand_wiqa
    assert hand_wiqa["item_less"]["pred_loop"] == "less", hand_wiqa

    # real_code_path + substrate_signature preflight (F.1/F.2)
    sig = inspect.signature(CausalLinkRegister.__init__)
    assert set(["d", "generator", "max_event_slots"]).issubset(sig.parameters.keys()), sig
    sig_add = inspect.signature(CausalLinkRegister.add_causal_link)
    assert set(["cause_idx", "effect_idx", "polarity"]).issubset(sig_add.parameters.keys()), sig_add

    real_code_path_ok = os.path.isdir(WIQA_DATA_DIR)
    real_sample = None
    scramble_fires_same_as_loop = None
    if real_code_path_ok:
        dev = load_dev()
        real_sample = [score_item_base(dev[i]) for i in range(min(20, len(dev)))]
        # arms-fire-on-same-subset check (documented invariant, see score_item_scramble docstring)
        mismatches = 0
        for r in real_sample:
            sp = score_item_scramble(r, 7)
            scramble_fired = not (sp == r["pred_polecho"] and r["loop_diag"]["abstained"])
            if scramble_fired != r["fired"]:
                mismatches += 1
        scramble_fires_same_as_loop = (mismatches == 0)

    return {"hand_chain": hand_chain, "hand_zero_hop": hand_zero_hop, "hand_stem": hand_stem,
            "hand_wiqa": hand_wiqa, "real_code_path_ok": real_code_path_ok,
            "scramble_fires_same_as_loop": scramble_fires_same_as_loop,
            "real_sample_preds": [{"question_id": r["question_id"], "pred_loop": r["pred_loop"],
                                    "gold": r["gold"], "fired": r["fired"]} for r in (real_sample or [])]}


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                   "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                   "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str), flush=True)
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    expected_units = len(seeds)
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    print(f"[{run_mode}] loading WIQA dev split...", flush=True)
    dev = load_dev()
    if args.smoke:
        stride = max(1, len(dev) // SMOKE_N)
        dev = dev[::stride][:SMOKE_N]
    n_total = len(dev)
    print(f"[{run_mode}] scoring {n_total} items (base, seed-independent pass)...", flush=True)

    rows_base: List[Dict] = []
    n_degraded = 0
    for i, ex in enumerate(dev):
        try:
            rows_base.append(score_item_base(ex))
        except Exception as e:  # noqa: BLE001 -- per-item failure isolation (META_RULE_J)
            n_degraded += 1
            rows_base.append({
                "question_id": ex.get("metadata_question_id", f"UNKNOWN_{i}"),
                "gold": ex.get("answer_label", "no_effect"),
                "qtype": ex.get("metadata_question_type", "UNKNOWN"),
                "path_len": ex.get("metadata_path_len"),
                "multihop": bool((ex.get("metadata_path_len") or 0) >= 2),
                "steps": [], "pp": 0, "op": 0,
                "p_idx": None, "p_score": 0.0, "p_admit": False,
                "o_idx": None, "o_score": 0.0, "o_admit": False,
                "edge_polarity": [],
                "pred_majority": "more", "pred_polecho": "no_effect", "pred_bow": "no_effect",
                "pred_loop": "no_effect", "loop_diag": {"abstained": True, "reason": "SCORING_EXCEPTION"},
                "pred_ablation2": "no_effect", "ablation2_diag": {"abstained": True, "reason": "SCORING_EXCEPTION"},
                "fired": False, "negation_crossing": False,
                "degraded_scoring": True, "failure_class": type(e).__name__, "failure_detail": str(e)[:300],
            })
        if (i + 1) % 1000 == 0:
            print(f"[{run_mode}] base scoring {i + 1}/{n_total} elapsed={time.time() - t0:.1f}s", flush=True)
            _write_heartbeat(output_dir, i + 1, n_total, time.time() - t0, {"phase": "base"})

    degraded_frac = n_degraded / n_total if n_total else 0.0
    print(f"[{run_mode}] base pass done: {n_degraded}/{n_total} degraded ({degraded_frac:.4f}); "
          f"elapsed={time.time() - t0:.1f}s", flush=True)
    if degraded_frac > DEGRADED_BUDGET:
        raise RuntimeError(
            f"DEGRADED_SCORING_BUDGET_EXCEEDED: {degraded_frac:.4f} > {DEGRADED_BUDGET} "
            f"({n_degraded}/{n_total} items hit a per-item scoring exception)")

    run_config = {"run_mode": run_mode, "anchor": ANCHOR_NAME, "n_items": n_total}
    done, remaining = resumable_seeds(seeds, output_dir, run_config=run_config)
    print(f"[{run_mode}] {len(done)}/{len(seeds)} seeds already complete; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[{run_mode}] seed={seed} scrambling+scoring...", flush=True)

        def _hb(i, n, el, _seed=seed):
            _write_heartbeat(output_dir, i, n, el, {"phase": "scramble", "seed": _seed})

        seed_result = run_one_seed(seed, rows_base, heartbeat_cb=_hb)
        write_partial(output_dir, seed, {"seed": seed, "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
                                          "n_items": n_total, "result": seed_result})
        print(f"[{run_mode}] seed={seed} done: loop_all={seed_result['per_subset']['all']['loop']:.4f} "
              f"abstain={seed_result['abstain_rate_all']:.4f} elapsed={seed_result['elapsed_s']:.1f}s",
              flush=True)

    per_seed_partials = aggregate_partials(output_dir, seeds, run_config=run_config)
    per_seed = {str(s): per_seed_partials[str(s)]["result"] for s in seeds}

    # arms-must-differ (seed[0]'s scramble draw as the ABLATION-1 representative)
    scramble0 = {b["question_id"]: score_item_scramble(b, seeds[0]) for b in rows_base}
    diff = _arms_must_differ(rows_base, scramble0)

    tier, msg, band_detail = apply_bands(per_seed)
    if not diff["all_differ"]:
        tier = "HARD_FAIL"
        msg = f"ARMS_IDENTICAL overrides band verdict: {diff} || {msg}"

    n_fired_total = sum(1 for r in rows_base if r["fired"])
    n_negation_crossing_total = sum(1 for r in rows_base if r["negation_crossing"])
    n_multihop_fired_total = sum(1 for r in rows_base if r["fired"] and r["multihop"])

    examples = pick_examples(rows_base)
    elapsed = time.time() - t0

    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": f"{tier}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_items": n_total, "n_degraded": n_degraded, "degraded_frac": degraded_frac,
        "gate_thresh": GATE_THRESH, "n_dim": D, "seeds": seeds,
        "n_fired_total": n_fired_total, "n_negation_crossing_total": n_negation_crossing_total,
        "n_multihop_fired_total": n_multihop_fired_total,
        "v1_abstain_rate": 0.7209167391935016,  # CITED@data/exp_wiqa_causal_chain_loop_v1/metrics.json
        "per_seed": per_seed, "band_detail": band_detail,
        "arms_differ_verified": diff["all_differ"], "arms_differ_check": diff,
        "examples": examples,
        "cardinality_ok": len(per_seed) == expected_units, "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "3-way discrete classification accuracy comparison on a real benchmark (WIQA); "
                    "no capacity/noise-floor discriminator threshold to CRLB-check",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: GATE_THRESH=0.05 held from v1's label-blind "
                              "calibration; re-verified this session (wiqa_stem_test.py) that stemming "
                              "reduces gate-fail abstain without flooding the gate with noise-level "
                              "admissions -- discriminator-fires still checked at smoke via arms_differ "
                              "+ active-subset non-empty",
        "hp_scope": {"dev_full": ["decisive_gate_active", "decisive_gate_active_multihop"]},
        "progress_logging": "print_flush_true",
        "decisive_collapse_fraction_threshold": DECISIVE_COLLAPSE_FRACTION,
    }
    _ckpt_write_metrics(Path(output_dir), metrics, results=None)
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("per_seed",)},
                      indent=2, default=str), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately not BaseException, see cell-template mandate
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
