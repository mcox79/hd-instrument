"""exp_bound_key_crossitem_similarity_cost_v1 -- WHY DID ADDING A BOUND KEY MAKE THE REAL
READ-OUT WORSE WHILE ADDRESSING FACETS IN ISOLATION WENT FROM CHANCE TO 1.000?

THIS IS A DIAGNOSTIC CELL, NOT A GATED ONE. It has no pre-registered PASS/FAIL band because it
is not testing a capability claim; it is a one-variable discriminator between four standing
explanations of a reconciliation problem. It is a durable file (not scratch/) because a report
cites its numbers, and CLAUDE.md forbids a durable citation into a directory that gets wiped.

THE RECONCILIATION PROBLEM
--------------------------
Two landed results point opposite ways.
  IN ISOLATION  : addressing facets takes within-item facet recovery from chance (FLAT_SUM
                  0.2534, chance 0.25) to 1.000
                  (data/exp_hub_spoke_word_representation_v1/metrics.json)
  ON THE REAL   : adding a bound key made the live open-vocabulary read-out WORSE --
  READ-OUT        0.03675 vs 0.0480, CI [-0.0195,-0.0030], verdict STRUCTURE_HURTS, with both
                  known-answer arms clearing 0.70 so the instrument was licensed
                  (data/exp_structured_code_vs_flat_bag_c3_v1/metrics.json)

FOUR EXPLANATIONS ON THE TABLE
  (i)   real facets are CORRELATED, not independent as the synthetic arms were
  (ii)  the real read-out superposes FAR MORE than the 2-3 terms where the sum is safe
  (iii) the KEY COMPETES WITH THE CONTENT for the same fixed vector capacity
  (iv)  something else

WHAT THIS CELL VARIES, AND WHY THAT SEPARATES THEM
--------------------------------------------------
The two measurements differ in ONE structural way that neither (i), (ii) nor (iii) names:

  facet recovery is a WITHIN-ITEM question asked with the KEY IN HAND
  the C3 read-out is a CROSS-ITEM cosine between two anchors built INDEPENDENTLY

Binding is an isometry, so it is free within one item. Across two items it is free ONLY where
the two items happened to use the SAME key for the shared content. So the discriminating knob
is R, the size of the key alphabet:

  R = 1   every occurrence binds the same key -> a global isometry -> BOUND must equal FLAT
          EXACTLY. If (iii) were the mechanism, BOUND would lose here. It cannot.
  R > 1   shared content is bound under agreeing keys only by chance ~ 1/R.

and the second knob is B, the number of superposed terms, which is what (ii) names. If (ii)
were the whole story the BOUND-minus-FLAT gap would track B and ignore R.

A third arm, BOUND_MATCHED, forces partners to use the SAME key for their SHARED content while
leaving everything else identical to BOUND. It isolates KEY DISAGREEMENT from KEY PRESENCE.

MEASURED SCOPE. Synthetic bipolar codes, a partner-retrieval task, cosine read-out. It is an
existence/mechanism argument about the ALGEBRA that both real cells sit on; it is NOT a rerun of
either real cell and no number here may be quoted as a C3 or hub-spoke result. The real-data
counterpart (alphabet fragmentation measured on the actual C3 corpus) is a separate section of
the accompanying report.

NO EXTERNAL LLM. ASCII-only. CPU. data/foundation/** never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "bound_key_crossitem_similarity_cost_v1"
CODE_VERSION = "v1.0"

D = 1024
N_PAIRS = 512                 # 1024 items; partner retrieval over the full set
W = 4096                      # content-symbol vocabulary
B_DEFAULT = 32                # superposed terms per item
OVERLAP_DEFAULT = 0.50        # fraction of an item's terms shared with its partner
R_SWEEP = [1, 2, 4, 8, 16, 32, 64]
B_SWEEP = [2, 3, 4, 8, 16, 32, 64, 128]
OVERLAP_SWEEP = [0.25, 0.50, 0.75, 1.00]
R_DEFAULT = 16                # ~ the order of the UD relation alphabet actually used
SEEDS = [7, 17, 23]


def _bipolar(rng, shape) -> np.ndarray:
    return rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=shape)


def _l2n(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build(seed: int, R: int, B: int, overlap: float, zipf_a: float = 1.2) -> dict:
    """Two arms over IDENTICAL content: FLAT sum vs KEY-BOUND sum, plus the matched-key arm.

    Every item is a bag of B content symbols drawn WITH REPLACEMENT (so repeats reinforce, as
    a real anchor accumulated over many sentences does). Each item's partner shares
    round(overlap*B) of those draws; the rest are drawn independently. Gold = the partner.
    """
    rng = np.random.default_rng(seed * 1000003 + R * 7919 + B * 104729 + int(overlap * 1000))
    content = _bipolar(rng, (W, D))                       # shared content codebook
    keys = _bipolar(rng, (max(R, 1), D))                  # relation-key alphabet
    n_items = 2 * N_PAIRS
    n_share = int(round(overlap * B))

    # Zipfian content draw so a few symbols dominate, as real collocates do
    ranks = np.arange(1, W + 1, dtype=np.float64)
    p = 1.0 / ranks ** zipf_a
    p /= p.sum()

    sym = np.zeros((n_items, B), dtype=np.int64)
    rel = rng.integers(0, max(R, 1), size=(n_items, B))
    for pi in range(N_PAIRS):
        a, b = 2 * pi, 2 * pi + 1
        shared = rng.choice(W, size=n_share, p=p)
        sym[a, :n_share] = shared
        sym[b, :n_share] = shared
        sym[a, n_share:] = rng.choice(W, size=B - n_share, p=p)
        sym[b, n_share:] = rng.choice(W, size=B - n_share, p=p)

    flat = np.zeros((n_items, D), dtype=np.float32)
    bound = np.zeros((n_items, D), dtype=np.float32)
    bound_m = np.zeros((n_items, D), dtype=np.float32)
    # BOUND_MATCHED: partners use the SAME relation for their SHARED slots
    rel_m = rel.copy()
    for pi in range(N_PAIRS):
        a, b = 2 * pi, 2 * pi + 1
        rel_m[b, :n_share] = rel_m[a, :n_share]

    for i in range(n_items):
        c = content[sym[i]]                                # (B, D)
        flat[i] = c.sum(0)
        bound[i] = (c * keys[rel[i]]).sum(0)
        bound_m[i] = (c * keys[rel_m[i]]).sum(0)

    return {"flat": flat, "bound": bound, "bound_matched": bound_m,
            "sym": sym, "rel": rel, "n_items": n_items, "n_share": n_share}


def partner_hit_at_1(X: np.ndarray) -> float:
    """Cross-item retrieval: for each item, is its partner the nearest of all other items?"""
    Xn = _l2n(X)
    S = Xn @ Xn.T
    np.fill_diagonal(S, -np.inf)
    pick = np.argmax(S, axis=1)
    n = X.shape[0]
    partner = np.arange(n) ^ 1                            # 0<->1, 2<->3, ...
    return float(np.mean(pick == partner))


def mean_partner_cos(X: np.ndarray) -> float:
    Xn = _l2n(X)
    n = X.shape[0]
    partner = np.arange(n) ^ 1
    return float(np.mean(np.sum(Xn * Xn[partner], axis=1)))


def one_config(seed: int, R: int, B: int, overlap: float) -> dict:
    o = build(seed, R, B, overlap)
    out = {"seed": seed, "R": R, "B": B, "overlap": overlap, "n_items": o["n_items"]}
    for name in ("flat", "bound", "bound_matched"):
        out[name] = {"hit_at_1": partner_hit_at_1(o[name]),
                     "mean_partner_cos": mean_partner_cos(o[name])}
    out["gap_bound_minus_flat"] = out["bound"]["hit_at_1"] - out["flat"]["hit_at_1"]
    out["gap_boundmatched_minus_flat"] = (out["bound_matched"]["hit_at_1"]
                                          - out["flat"]["hit_at_1"])
    out["bound_equals_flat_exactly"] = bool(
        abs(out["bound"]["hit_at_1"] - out["flat"]["hit_at_1"]) < 1e-12)
    return out


def selftest() -> dict:
    """Assert VALUES, not absence of errors."""
    out = {}
    # ST1 -- at R=1 binding is a GLOBAL ISOMETRY, so every cross-item cosine is UNCHANGED.
    # If explanation (iii) (the key competes with content for capacity) were the mechanism,
    # this equality could not hold. It is the load-bearing control of the whole cell.
    o = build(7, 1, 16, 0.5)
    fn, bn = _l2n(o["flat"]), _l2n(o["bound"])
    m = float(np.max(np.abs(fn @ fn[:64].T - bn @ bn[:64].T)))
    assert m < 1e-4, f"ST1 R=1 is not an isometry: max cos delta {m}"
    out["ST1_R1_is_isometry_max_cos_delta"] = m

    # ST2 -- the arms are NOT silent aliases at R>1
    o2 = build(7, 16, 16, 0.5)
    assert not np.array_equal(o2["flat"], o2["bound"]), "ST2 arms are aliases at R=16"
    out["ST2_arms_differ"] = True

    # ST3 -- the metric can go DOWN: overlap 1.0 must beat overlap 0.25 for the flat arm
    hi = partner_hit_at_1(build(7, 16, 16, 1.0)["flat"])
    lo = partner_hit_at_1(build(7, 16, 16, 0.25)["flat"])
    assert hi > lo, f"ST3 metric does not move with overlap: {lo} -> {hi}"
    out["ST3_metric_moves"] = {"overlap0.25": lo, "overlap1.00": hi}

    # ST4 -- chance is 1/(n_items-1); the flat arm must be well above it or nothing is measurable
    ch = 1.0 / (2 * N_PAIRS - 1)
    assert hi > 20 * ch, f"ST4 flat arm too weak to discriminate: {hi} vs chance {ch}"
    out["ST4_chance"] = {"chance": ch, "flat_overlap1.0": hi}

    # ST5 -- no external LLM in the runtime path
    banned = [m for m in sys.modules if any(t in m.lower() for t in
              ("transformers", "openai", "llama", "sentence_transformers"))]
    assert not banned, f"external LLM in runtime path: {banned}"
    out["ST5_no_external_llm"] = True
    return out


def main() -> int:
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    st = selftest()
    if "--self-test" in sys.argv:
        print("[selftest] PASS " + json.dumps(st, default=str))
        return 0

    sweeps: Dict[str, List[dict]] = {"R_sweep": [], "B_sweep": [], "overlap_sweep": []}
    for R in R_SWEEP:
        for seed in SEEDS:
            sweeps["R_sweep"].append(one_config(seed, R, B_DEFAULT, OVERLAP_DEFAULT))
        print(f"  R={R} done ({time.time()-t0:.1f}s)", flush=True)
    for B in B_SWEEP:
        for seed in SEEDS:
            sweeps["B_sweep"].append(one_config(seed, R_DEFAULT, B, OVERLAP_DEFAULT))
        print(f"  B={B} done ({time.time()-t0:.1f}s)", flush=True)
    for ov in OVERLAP_SWEEP:
        for seed in SEEDS:
            sweeps["overlap_sweep"].append(one_config(seed, R_DEFAULT, B_DEFAULT, ov))
        print(f"  overlap={ov} done ({time.time()-t0:.1f}s)", flush=True)

    def agg(rows, keyfn):
        acc: Dict[str, dict] = {}
        for r in rows:
            k = keyfn(r)
            acc.setdefault(k, {"flat": [], "bound": [], "bound_matched": []})
            for a in ("flat", "bound", "bound_matched"):
                acc[k][a].append(r[a]["hit_at_1"])
        return {k: {a: {"mean": float(np.mean(v[a])), "sd": float(np.std(v[a]))}
                    for a in v} for k, v in acc.items()}

    summary = {
        "R_sweep_hit_at_1": agg(sweeps["R_sweep"], lambda r: f"R{r['R']}"),
        "B_sweep_hit_at_1": agg(sweeps["B_sweep"], lambda r: f"B{r['B']}"),
        "overlap_sweep_hit_at_1": agg(sweeps["overlap_sweep"], lambda r: f"ov{r['overlap']:g}"),
        "chance": 1.0 / (2 * N_PAIRS - 1),
    }
    r1 = summary["R_sweep_hit_at_1"]["R1"]
    gap_at_R1 = r1["bound"]["mean"] - r1["flat"]["mean"]
    rmax = summary["R_sweep_hit_at_1"][f"R{R_SWEEP[-1]}"]
    gap_at_Rmax = rmax["bound"]["mean"] - rmax["flat"]["mean"]
    b_lo = summary["B_sweep_hit_at_1"][f"B{B_SWEEP[0]}"]
    b_hi = summary["B_sweep_hit_at_1"][f"B{B_SWEEP[-1]}"]
    gap_at_Blo = b_lo["bound"]["mean"] - b_lo["flat"]["mean"]
    gap_at_Bhi = b_hi["bound"]["mean"] - b_hi["flat"]["mean"]
    # VERDICT IS DERIVED FROM THE MEASUREMENT, never asserted. Each branch names the
    # explanation it licenses and the observation that licenses it.
    if abs(gap_at_R1) > 0.02:
        verdict = "KEY_COMPETES_FOR_CAPACITY"
    elif abs(gap_at_R1) <= 0.005 and gap_at_Rmax < -0.02:
        verdict = ("KEY_DISAGREEMENT_IS_THE_COST" if abs(gap_at_Rmax) > abs(gap_at_Blo)
                   else "MIXED_KEY_DISAGREEMENT_AND_SUMMAND_COUNT")
    elif abs(gap_at_R1) <= 0.005 and abs(gap_at_Rmax) <= 0.02 and abs(gap_at_Bhi) > 0.02:
        verdict = "SUMMAND_COUNT_DOMINATES"
    else:
        verdict = "INCONCLUSIVE"
    verdict_msg = (
        f"{verdict}. "
        f"BOUND-minus-FLAT gap at R=1 (one shared key) = {gap_at_R1:+.4f}; "
        f"at R={R_SWEEP[-1]} = {gap_at_Rmax:+.4f}. "
        f"At the smallest bundle B={B_SWEEP[0]} the gap is "
        f"{b_lo['bound']['mean'] - b_lo['flat']['mean']:+.4f} and at B={B_SWEEP[-1]} it is "
        f"{b_hi['bound']['mean'] - b_hi['flat']['mean']:+.4f}. "
        f"BOUND_MATCHED (same keys on shared content) at R={R_SWEEP[-1]} = "
        f"{rmax['bound_matched']['mean']:.4f} vs FLAT {rmax['flat']['mean']:.4f}.")

    metrics = {"anchor_name": ANCHOR_NAME, "code_version": CODE_VERSION, "run_mode": "full",
               "cell_class": "DIAGNOSTIC -- no pre-registered PASS/FAIL band",
               "config": {"D": D, "W": W, "N_PAIRS": N_PAIRS, "B_DEFAULT": B_DEFAULT,
                          "R_DEFAULT": R_DEFAULT, "OVERLAP_DEFAULT": OVERLAP_DEFAULT,
                          "R_SWEEP": R_SWEEP, "B_SWEEP": B_SWEEP,
                          "OVERLAP_SWEEP": OVERLAP_SWEEP, "SEEDS": SEEDS},
               "selftest": st, "summary_block": summary, "per_config": sweeps,
               "verdict": verdict, "verdict_msg": verdict_msg,
               "summary": verdict_msg, "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics)
    print(json.dumps({"verdict_msg": verdict_msg, "summary": summary}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
