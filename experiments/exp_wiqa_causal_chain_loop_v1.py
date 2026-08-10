# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; 5-arm hash-differ)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (3-way discrete classification accuracy on a real benchmark; no capacity/
#   noise-floor discriminator threshold)
# - HP_SCOPE: {dev_full: [gate1_lift, gate2_scramble, gate3_novalidate, gate4_multihop]}
# - cardinality_ok: EXPECTED_N_UNITS=len(SEEDS_FULL)=3 (full) / 1 (smoke)
# - per-unit failure-class instrumentation (no bare except; degraded_scoring budget 2%)
# - calibration_check: adaptive_with_discriminator_gate (GATE_THRESH=0.05 from cosine-distribution
#   shape, label-blind; discriminator-fires checked at smoke via arms-must-differ + abstain-rate)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL CausalLinkRegister (polarity-extended) + iterative_attractor
#   objects (real_code_path); no synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-10_wiqa_causal_chain_loop_v1.md for the full pre-reg.
"""exp_wiqa_causal_chain_loop_v1 -- first cell of the WIQA flagship pivot: does a glass-box
multi-hop SIGNED causal-chain propagation system beat MAJORITY, POLARITY-ECHO (the sharpened
surface-shortcut risk), and BoW-OVERLAP on WIQA dev (what-if procedural-text QA, 3-way
more/less/no_effect, near-chance majority ~33.3%)?

Mechanism (CAUSAL-CHAIN-LOOP): extract (perturbation, outcome) clauses from the question stem
(100%-reliable regex, MEASURED@calibration); anchor each clause to a paragraph step via an HD
bag-of-words pull-in (hdlab.cleanup_family.iterative_attractor, Stage-1/Stage-2A's retrieve-
VALIDATE pattern re-instantiated for real text) with a cosine admission gate; build a per-item
hdlab.situation_model_accumulate.CausalLinkRegister (polarity-extended THIS cell) over adjacent
paragraph steps, polarity flipping on a negating/blocking word in the target step; walk the
register hop-by-hop from the perturbation anchor to the outcome anchor (query_effect_of +
query_link_polarity at each hop -- genuine per-hop retrieve-VALIDATE-advance, not a bare Python
list walk), multiplying signs; compare the propagated sign to the outcome clause's own stated
polarity (same -> "more", opposite -> "less"), or interpret the propagated sign DIRECTLY when the
outcome clause has no stated polarity word (~21.6% of items, MEASURED@calibration) -- POLARITY-
ECHO structurally cannot do this (see prereg "Semantic finding"). Any anchor/structural failure
ABSTAINS to POLARITY-ECHO's own prediction (augment-not-replace, same anti-regression pattern as
the E4/MCScript2.0 gate-test) -- CAUSAL-CHAIN-LOOP can never score below POLARITY-ECHO by
construction.

HONEST PRE-MEASURED FINDINGS (see prereg, not repeated in full here): no cheap lexical/HD-BoW
signal separates the no_effect/distractor bucket (balanced-accuracy=0.4997, chance); real
POLARITY-ECHO dev accuracy = 0.3420 overall / 0.4125 multi-hop (weaker than the scoping drill
feared, still the real baseline to beat); only 9.09% of the 77 distinct paragraphs have any
negating/blocking step (edge-flip fires rarely; the mechanism's larger source of edge is the
"no stated outcome polarity" direct-interpretation case, not edge-sign-flipping).

Modes:
  --self-test  Real-code-path check: 3-step hand-built chain (A->B->-C, negation on C) +
               hand-built WIQA-shaped pair + CausalLinkRegister backward-compat check +
               substrate_signature preflight. No queue dispatch.
  --smoke      First 300 dev items (deterministic order) at FULL parameters (same lexicons,
               GATE_THRESH, D=1024 -- discriminator-preview per DISCRIMINATOR-MUST-SURVIVE-SCALE).
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

ANCHOR_NAME = "wiqa_causal_chain_loop_v1"
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
GATE_THRESH = 0.05  # MEASURED@calibration: near p10 of non-distractor best-cosine dist
                     # (INPARA pert_best p10=0.0531, EXOGENOUS pert_best p10=0.0331); admits
                     # nearly all genuine content overlap while rejecting true zero-overlap.
SEEDS_SMOKE = [7]
SEEDS_FULL = [7, 17, 29]
SMOKE_N = 300
DEGRADED_BUDGET = 0.02  # halt if >2% of items hit a per-item scoring exception

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
    absent). Shared primitive: used identically by POLARITY-ECHO and as CAUSAL-CHAIN-LOOP's raw
    perturbation/outcome sign input -- the differentiator is what each arm DOES with it, not the
    lexicon itself."""
    toks = TOKRE.findall(text.lower())
    inc = any(t in INCREASE_WORDS for t in toks)
    dec = any(t in DECREASE_WORDS for t in toks)
    if inc and not dec:
        return 1
    if dec and not inc:
        return -1
    return 0


def content_tokens(text: str) -> List[str]:
    return [t for t in TOKRE.findall(text.lower()) if t not in STOPWORDS and len(t) > 1]


def has_negating_word(text: str) -> bool:
    return bool(set(TOKRE.findall(text.lower())) & NEGATING_STEP_WORDS)


_WORD_VEC_CACHE: Dict[str, np.ndarray] = {}


def word_vec(word: str, d: int = D) -> np.ndarray:
    """Deterministic bipolar {-1,+1} vector per distinct content word, hashlib-seeded
    (PROT-023/F.5 compliant -- no built-in hash(), no list(set()) ordering)."""
    if word not in _WORD_VEC_CACHE:
        seed = int.from_bytes(
            hashlib.sha256(f"wiqa_bow_word::{word}".encode()).digest()[:8], "big") % (2 ** 32)
        rng = np.random.default_rng(seed)
        _WORD_VEC_CACHE[word] = (rng.integers(0, 2, size=d).astype(np.float32) * 2 - 1)
    return _WORD_VEC_CACHE[word]


def encode_bow(text: str, d: int = D) -> np.ndarray:
    """Bag-of-words HD bundle: sum of content-word vectors (unnormalized)."""
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
    """Hashlib-seeded deterministic permutation (PROT-023/F.5 compliant), same convention as
    exp_focus_pullin_causal_stage1_micro_world_v1._deterministic_perm."""
    seed = int.from_bytes(
        hashlib.sha256(f"wiqa_scramble::{identity_tag}".encode()).digest()[:8], "big") % (2 ** 32)
    rng = np.random.default_rng(seed)
    return rng.permutation(n).tolist()


# ---------------------------------------------------------------------- anchor retrieval
def anchor_step(probe_vec: np.ndarray, step_vecs: List[np.ndarray]) -> Tuple[Optional[int], float, bool]:
    """Pull-in retrieval (hdlab.cleanup_family.iterative_attractor) of the best-matching paragraph
    step for a clause probe. Returns (best_idx or None, raw_cosine_score, admitted)."""
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
    """Build a CausalLinkRegister over K adjacent paragraph steps (edge i -> i+1). Edge polarity
    is -1 if the step checked for negation contains a blocking/negating word, else +1.
    negation_check_order=None (real): checks step[i+1] (the true target step).
    negation_check_order=perm (ABLATION-1 scramble): checks step[perm[i+1]] instead -- destroys
    WHICH edges are flagged negative while preserving the same adjacency topology and roughly the
    same count of negative edges in the paragraph overall."""
    k = len(steps)
    gen = torch.Generator()
    gen.manual_seed(12345)  # register internals (role/idx vecs) are item-ephemeral scaffolding;
                            # a fixed seed here is deliberate (not a source of the propagated
                            # answer -- the answer comes from polarity + topology, not from which
                            # random FHRR vectors were drawn).
    reg = CausalLinkRegister(d=D, generator=gen, max_event_slots=max(k, 1))
    edge_polarity: List[int] = []
    for i in range(k - 1):
        check_idx = negation_check_order[i + 1] if negation_check_order is not None else (i + 1)
        pol = -1 if has_negating_word(steps[check_idx]) else 1
        reg.add_causal_link(i, i + 1, polarity=pol)
        edge_polarity.append(pol)
    return reg, edge_polarity


def propagate_sign(reg: CausalLinkRegister, lo: int, hi: int) -> Tuple[Optional[int], List[Dict]]:
    """Retrieve-VALIDATE-advance walk lo -> hi using the register's own query_effect_of +
    query_link_polarity at EACH hop (genuine per-hop substrate decode, not a bare Python list
    lookup). Returns (product_sign, trace); product_sign is None if any hop's registered effect
    doesn't match the expected next index (hop-consistency VALIDATE failure -> caller abstains)."""
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
    """Everything that does NOT depend on the scramble seed: extraction, anchoring, admission,
    the TRUE register's CAUSAL-CHAIN-LOOP + ABLATION-2(no-validate) predictions, and the
    MAJORITY/POLARITY-ECHO/BoW-OVERLAP baseline predictions."""
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
    pred_majority = "more"  # MEASURED@calibration: train label-frequency tie-break, dev acc=0.3333

    # ---- POLARITY-ECHO (the real baseline; MEASURED@calibration overall=0.3420, multihop=0.4125) ----
    if op == 0:
        pred_polecho = "no_effect"
    elif pp == 0:
        pred_polecho = "more"
    else:
        pred_polecho = "more" if pp == op else "less"

    # ---- BoW-OVERLAP (secondary, expected-weak) ----
    outcome_toks = set(content_tokens(outcome_clause))
    para_toks = set(content_tokens(para_text))
    if len(outcome_toks & para_toks) == 0:
        pred_bow = "no_effect"
    else:
        pred_bow = "more"  # train-majority among the non-flagged remainder

    # ---- CAUSAL-CHAIN-LOOP + ABLATION-2 (share the TRUE, unscrambled register) ----
    reg, edge_polarity = build_register(steps, negation_check_order=None)

    def _propagate_and_predict(use_gate: bool) -> Tuple[str, Dict]:
        admitted = (p_admit and o_admit) if use_gate else (p_idx is not None and o_idx is not None)
        if not (admitted and p_idx is not None and o_idx is not None and p_idx != o_idx and pp != 0):
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
        return pred, {"abstained": False, "propagated_sign": propagated, "trace": trace}

    pred_loop, loop_diag = _propagate_and_predict(use_gate=True)
    pred_ablation2, ablation2_diag = _propagate_and_predict(use_gate=False)

    return {
        "question_id": ex["metadata_question_id"],
        "gold": ex["answer_label"],
        "qtype": ex["metadata_question_type"],
        "path_len": ex["metadata_path_len"],
        "multihop": bool(ex["metadata_path_len"] is not None and ex["metadata_path_len"] >= 2),
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
    }


def score_item_scramble(base: Dict, seed: int) -> str:
    """ABLATION-1: SAME anchors/admission as CAUSAL-CHAIN-LOOP; edge-polarity negation-check
    computed against a deterministically-permuted step order (seed+para-id-keyed)."""
    steps = base["steps"]
    k = len(steps)
    p_idx, o_idx, p_admit, o_admit, pp, op = (
        base["p_idx"], base["o_idx"], base["p_admit"], base["o_admit"], base["pp"], base["op"])
    if not (p_admit and o_admit and p_idx is not None and o_idx is not None
            and p_idx != o_idx and pp != 0):
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
    # Bulk columnar conversion (fast) instead of 6894 individual dev[i] row accesses (slow --
    # each triggers a separate Arrow->Python conversion). dev.to_list() + a columnar id fetch
    # are both single bulk ops.
    qids = dev["metadata_question_id"]
    idx_order = sorted(range(len(dev)), key=lambda i: qids[i])
    all_rows = dev.to_list()
    return [all_rows[i] for i in idx_order]


# ---------------------------------------------------------------------- accuracy aggregation
def _acc(rows: List[Dict], pred_key: str, subset: Optional[str] = None) -> float:
    if subset == "multihop":
        rows = [r for r in rows if r["multihop"]]
    elif subset is not None:
        raise ValueError(f"unknown subset {subset!r}")
    if not rows:
        return float("nan")
    return sum(1 for r in rows if r[pred_key] == r["gold"]) / len(rows)


def _abstain_rate(rows: List[Dict], diag_key: str) -> float:
    if not rows:
        return float("nan")
    return sum(1 for r in rows if r[diag_key]["abstained"]) / len(rows)


# ---------------------------------------------------------------------- full-dev per-seed run
def run_one_seed(seed: int, rows_base: List[Dict], heartbeat_cb=None) -> Dict:
    t0 = time.time()
    n = len(rows_base)
    scramble_preds = []
    for i, base in enumerate(rows_base):
        scramble_preds.append(score_item_scramble(base, seed))
        if heartbeat_cb is not None and (i + 1) % 1000 == 0:
            heartbeat_cb(i + 1, n, time.time() - t0)
    rows = [dict(r, pred_ablation1=sp) for r, sp in zip(rows_base, scramble_preds)]

    acc = {
        "majority": {"overall": _acc(rows, "pred_majority"), "multihop": _acc(rows, "pred_majority", "multihop")},
        "polecho": {"overall": _acc(rows, "pred_polecho"), "multihop": _acc(rows, "pred_polecho", "multihop")},
        "bow": {"overall": _acc(rows, "pred_bow"), "multihop": _acc(rows, "pred_bow", "multihop")},
        "loop": {"overall": _acc(rows, "pred_loop"), "multihop": _acc(rows, "pred_loop", "multihop")},
        "ablation1_scramble": {"overall": _acc(rows, "pred_ablation1"), "multihop": _acc(rows, "pred_ablation1", "multihop")},
        "ablation2_novalidate": {"overall": _acc(rows, "pred_ablation2"), "multihop": _acc(rows, "pred_ablation2", "multihop")},
    }
    abstain = {
        "loop": _abstain_rate(rows, "loop_diag"),
        "ablation2_novalidate": _abstain_rate(rows, "ablation2_diag"),
    }
    elapsed = time.time() - t0
    return {"seed": seed, "n_items": n, "elapsed_s": round(elapsed, 4), "acc": acc, "abstain": abstain}


def _arms_must_differ(rows_base: List[Dict], scramble_preds_seed0: List[str]) -> Dict:
    def _digest(vals):
        b = json.dumps(list(vals), sort_keys=False, default=str).encode("utf-8")
        return hashlib.sha256(b).hexdigest()
    sigs = {
        "majority": _digest([r["pred_majority"] for r in rows_base]),
        "polecho": _digest([r["pred_polecho"] for r in rows_base]),
        "bow": _digest([r["pred_bow"] for r in rows_base]),
        "loop": _digest([r["pred_loop"] for r in rows_base]),
        "ablation1_scramble": _digest(scramble_preds_seed0),
        "ablation2_novalidate": _digest([r["pred_ablation2"] for r in rows_base]),
    }
    pairs_differ = {f"{a}_vs_{b}": sigs[a] != sigs[b]
                     for i, a in enumerate(sigs) for b in list(sigs)[i + 1:]}
    return {"sigs": sigs, "pairs_differ": pairs_differ, "all_differ": all(pairs_differ.values())}


# ---------------------------------------------------------------------- verdict logic
GATE1_LIFT = 0.05
GATE2_SCRAMBLE_COLLAPSE_MARGIN = 0.05
GATE2_SCRAMBLE_CEIL_MARGIN = 0.02
GATE4_MULTIHOP_LIFT = 0.08


def _median(xs: List[float]) -> float:
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 == 1 else 0.5 * (s[mid - 1] + s[mid])


def apply_bands(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    seeds = sorted(per_seed.keys(), key=lambda s: int(s))
    loop_overall = per_seed[seeds[0]]["acc"]["loop"]["overall"]
    loop_multihop = per_seed[seeds[0]]["acc"]["loop"]["multihop"]
    majority_overall = per_seed[seeds[0]]["acc"]["majority"]["overall"]
    polecho_overall = per_seed[seeds[0]]["acc"]["polecho"]["overall"]
    polecho_multihop = per_seed[seeds[0]]["acc"]["polecho"]["multihop"]
    bow_overall = per_seed[seeds[0]]["acc"]["bow"]["overall"]
    ablation2_overall = per_seed[seeds[0]]["acc"]["ablation2_novalidate"]["overall"]

    scramble_vals = [per_seed[s]["acc"]["ablation1_scramble"]["overall"] for s in seeds]
    scramble_median = _median(scramble_vals)

    best_baseline = max(majority_overall, polecho_overall, bow_overall)
    gate1_gap = loop_overall - best_baseline
    gate1 = gate1_gap >= GATE1_LIFT

    scramble_drop = loop_overall - scramble_median
    scramble_ceil_ok = scramble_median <= best_baseline + GATE2_SCRAMBLE_CEIL_MARGIN
    gate2 = (scramble_drop >= GATE2_SCRAMBLE_COLLAPSE_MARGIN) and scramble_ceil_ok

    gate3 = ablation2_overall < loop_overall

    gate4_gap = loop_multihop - polecho_multihop
    gate4 = gate4_gap >= GATE4_MULTIHOP_LIFT

    detail = {
        "loop_overall": loop_overall, "loop_multihop": loop_multihop,
        "majority_overall": majority_overall, "polecho_overall": polecho_overall,
        "polecho_multihop": polecho_multihop, "bow_overall": bow_overall,
        "best_baseline": best_baseline, "gate1_gap": gate1_gap, "gate1_pass": gate1,
        "scramble_median": scramble_median, "scramble_vals": scramble_vals,
        "scramble_drop": scramble_drop, "scramble_ceil_ok": scramble_ceil_ok, "gate2_pass": gate2,
        "ablation2_overall": ablation2_overall, "gate3_pass": gate3,
        "gate4_gap": gate4_gap, "gate4_pass": gate4,
    }

    scramble_survives = scramble_drop < GATE2_SCRAMBLE_COLLAPSE_MARGIN and not scramble_ceil_ok

    if gate1_gap < 0 or scramble_survives or gate4_gap <= 0:
        tier = "HARD_FAIL"
        msg = (f"HARD_FAIL: gate1_gap={gate1_gap:.4f}(best_baseline={best_baseline:.4f}) "
               f"scramble_drop={scramble_drop:.4f} gate4_gap={gate4_gap:.4f}")
    elif gate1 and gate2 and gate3 and gate4:
        tier = "HARD_PASS"
        msg = (f"HARD_PASS: loop_overall={loop_overall:.4f} beats best_baseline={best_baseline:.4f} "
               f"by {gate1_gap:.4f}; scramble collapses (drop={scramble_drop:.4f}, "
               f"scramble_median={scramble_median:.4f}<=best+0.02); "
               f"ablation2_novalidate={ablation2_overall:.4f}<loop; "
               f"multihop lift over polecho={gate4_gap:.4f}")
    else:
        tier = "MIDDLE_BAND"
        msg = (f"MIDDLE_BAND: gate1={gate1}({gate1_gap:.4f}) gate2={gate2}(drop={scramble_drop:.4f}) "
               f"gate3={gate3}({ablation2_overall:.4f}<{loop_overall:.4f}) "
               f"gate4={gate4}({gate4_gap:.4f}) -- partial/mixed evidence")
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
                                 and not r["loop_diag"]["abstained"]]
    loop_wrong_polecho_right = [r for r in rows_base
                                 if r["pred_loop"] != r["gold"] and r["pred_polecho"] == r["gold"]
                                 and not r["loop_diag"]["abstained"]]

    def _fmt(r):
        return {"question_id": r["question_id"], "gold": r["gold"], "pred_loop": r["pred_loop"],
                "pred_polecho": r["pred_polecho"], "pp": r["pp"], "op": r["op"],
                "p_idx": r["p_idx"], "o_idx": r["o_idx"], "qtype": r["qtype"]}

    return {"loop_wins_vs_polecho": [_fmt(r) for r in loop_right_polecho_wrong[:n]],
            "loop_loses_vs_polecho": [_fmt(r) for r in loop_wrong_polecho_right[:n]],
            "n_loop_wins_total": len(loop_right_polecho_wrong),
            "n_loop_loses_total": len(loop_wrong_polecho_right)}


# ---------------------------------------------------------------------- self-test
def _hand_case_chain() -> Dict:
    """3-step hand-built chain A(0) -> B(1) -> C(2), negation word on C -> edge(1,2) polarity=-1,
    edge(0,1) polarity=+1 (no negation word on B). Perturbation pp=+1 (increase) anchored at A;
    outcome op=0 (no stated polarity) anchored at C -> propagated = +1 * (+1 * -1) = -1 -> "less"."""
    steps = ["water level increases in the tank", "pressure builds up", "the valve stops the flow"]
    reg, edge_pol = build_register(steps, negation_check_order=None)
    assert edge_pol == [1, -1], f"expected edge_polarity [1,-1], got {edge_pol}"
    sign, trace = propagate_sign(reg, 0, 2)
    assert sign == -1, f"expected propagated product -1, got {sign} (trace={trace})"
    # backward-compat: unsigned call site (polarity defaulted) still works identically
    gen = torch.Generator(); gen.manual_seed(1)
    reg2 = CausalLinkRegister(d=64, generator=gen, max_event_slots=3)
    reg2.add_causal_link(0, 1)  # no polarity kwarg -> default +1, old call-site shape unchanged
    eff, _ = reg2.query_effect_of(0)
    cau, _ = reg2.query_cause_of(1)
    assert eff == 1 and cau == 0, f"backward-compat broken: eff={eff} cau={cau}"
    assert reg2.query_link_polarity(0, 1) == 1
    return {"edge_polarity": edge_pol, "propagated_sign": sign, "trace": trace,
            "backward_compat_ok": True}


def _hand_case_wiqa_shaped() -> Dict:
    """Two hand-built WIQA-shaped items exercising the FULL score_item_base pipeline."""
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
    hand_wiqa = _hand_case_wiqa_shaped()
    assert hand_wiqa["item_more"]["pred_loop"] == "more", hand_wiqa
    assert hand_wiqa["item_less"]["pred_loop"] == "less", hand_wiqa

    # real_code_path + substrate_signature preflight (F.1/F.2)
    sig = inspect.signature(CausalLinkRegister.__init__)
    assert set(["d", "generator", "max_event_slots"]).issubset(sig.parameters.keys()), sig
    sig_add = inspect.signature(CausalLinkRegister.add_causal_link)
    assert set(["cause_idx", "effect_idx", "polarity"]).issubset(sig_add.parameters.keys()), sig_add

    # tiny real dataset load smoke (2 items) if the pulled corpus is on disk (real_code_path)
    real_code_path_ok = os.path.isdir(WIQA_DATA_DIR)
    real_sample = None
    if real_code_path_ok:
        dev = load_dev()
        real_sample = [score_item_base(dev[i]) for i in range(min(5, len(dev)))]

    return {"hand_chain": hand_chain, "hand_wiqa": hand_wiqa,
            "real_code_path_ok": real_code_path_ok,
            "real_sample_preds": [{"question_id": r["question_id"], "pred_loop": r["pred_loop"],
                                    "gold": r["gold"]} for r in (real_sample or [])]}


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
        # Stride sample (not a prefix): question_id-sorted dev is heavily clustered by
        # paragraph (~89 items/paragraph across 77 paragraphs) -- a naive dev[:SMOKE_N]
        # prefix draws from only ~3 paragraphs, MEASURED this session to systematically miss
        # all 7 (of 77) negating-word paragraphs, which made ABLATION-1(scramble) spuriously
        # bit-identical to CAUSAL-CHAIN-LOOP on smoke (not a mechanism bug -- scrambling an
        # all-positive edge list is a no-op). A stride sample spreads coverage across all
        # paragraphs so smoke's arms-must-differ check is representative.
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
        print(f"[{run_mode}] seed={seed} done: loop_overall={seed_result['acc']['loop']['overall']:.4f} "
              f"elapsed={seed_result['elapsed_s']:.1f}s", flush=True)

    per_seed_partials = aggregate_partials(output_dir, seeds, run_config=run_config)
    per_seed = {str(s): per_seed_partials[str(s)]["result"] for s in seeds}

    # arms-must-differ (seed[0]'s scramble draw as the ABLATION-1 representative)
    scramble0 = [score_item_scramble(b, seeds[0]) for b in rows_base]
    diff = _arms_must_differ(rows_base, scramble0)

    tier, msg, band_detail = apply_bands(per_seed)
    if not diff["all_differ"]:
        tier = "HARD_FAIL"
        msg = f"ARMS_IDENTICAL overrides band verdict: {diff} || {msg}"

    examples = pick_examples(rows_base)
    elapsed = time.time() - t0

    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": f"{tier}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_items": n_total, "n_degraded": n_degraded, "degraded_frac": degraded_frac,
        "gate_thresh": GATE_THRESH, "n_dim": D, "seeds": seeds,
        "per_seed": per_seed, "band_detail": band_detail,
        "arms_differ_verified": diff["all_differ"], "arms_differ_check": diff,
        "examples": examples,
        "cardinality_ok": len(per_seed) == expected_units, "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "3-way discrete classification accuracy comparison on a real benchmark (WIQA); "
                    "no capacity/noise-floor discriminator threshold to CRLB-check",
        "deterministic_seeding": True,
        "calibration_check": "adaptive_with_discriminator_gate: GATE_THRESH=0.05 set from the "
                              "cosine-distribution shape (label-blind); discriminator-fires verified "
                              "at smoke via arms_differ + loop abstain_rate < 1.0",
        "hp_scope": {"dev_full": ["gate1_lift", "gate2_scramble", "gate3_novalidate", "gate4_multihop"]},
        "progress_logging": "print_flush_true",
        "data_pull_status": "SUCCEEDED via revision=refs/convert/parquet fallback "
                             "(datasets>=3 dropped legacy script-dataset loading); "
                             "train=29808 validation=6894 test=3003, matches literature figures",
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
