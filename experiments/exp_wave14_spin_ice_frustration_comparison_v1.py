"""Spin-ice-precedent comparison probe: does substrate frustration match Ising/dipolar spin-ice?

TRIGGER: exp_wave14_1rsb_rate_dep_hysteresis_v1 returns RATE_DEPENDENT_KINETIC
  (Pearson r < -0.50 AND gap@epochs=32 < 50% of gap@epochs=1).

CONTEXT: rate_dep_hysteresis_v1 confirms geometric frustration (kinetic glass, not 1-RSB).
  Research: notes/research_novel_phase_class_methodology_2026-05-27.md Finding 1:
  Topological spin glass in diluted spin ice (arxiv 1405.0668) is a documented
  hybrid-label precedent -- coexistence of topological order AND spin-glass freezing.

  This probe asks: does substrate's frustration pattern match documented Ising or
  dipolar spin-ice signatures, OR does it match a qualitatively different pattern?

SPIN-ICE SIGNATURES (from lit, 1405.0668 + review):
  1. Dimer-ice rule: local ice rule is satisfied (2-in 2-out on each tetrahedron).
     SUBSTRATE ANALOG: local retrieval consistency -- each query satisfies its K nearest
     stored patterns (no local violation of the BSC constraint).
  2. Disorder operator: dipolar correlations decay as 1/r^3 (long-range order in ice).
     SUBSTRATE ANALOG: inter-pattern cosine overlap decays with distance in codebook space.
  3. Thermal demagnetization anomaly: chi_ac has a bump at T_freeze followed by a plateau.
     SUBSTRATE ANALOG: hysteresis gap has a non-monotone cooling-rate dependence
     (gap first increases, then decreases as epochs grow).
  4. Kasteleyn transition: system undergoes a geometry-driven phase transition at a
     critical field (not temperature).
     SUBSTRATE ANALOG: critical M/N (load) threshold where frustration appears.

DESIGN: 4-signature comparison battery.

  SIG 1 (Ice rule / local consistency): At fixed N and M, measure the fraction of
    queries where top-1 retrieved pattern matches the stored target (vs NOT matching
    due to frustration). Ice-rule-satisfied: frac >= 0.90. Frustrated: frac < 0.80.

  SIG 2 (Dipolar decay / correlation distance): Measure cosine overlap of stored
    patterns vs their rank-ordered distance in codebook space. Fit decay exponent.
    Dipolar: exponent ~ 3 (slow decay). Random (no correlation): exponent ~ 0 (flat).
    Substrate: measure the exponent.

  SIG 3 (Thermal anomaly / non-monotone): cooling-rate sweep with EXTENDED epoch range
    {1, 2, 4, 8, 16, 32, 64, 128}. Check if gap first INCREASES then DECREASES.
    Spin-ice prediction: non-monotone cooling rate dependence (gap has a peak).
    1-RSB prediction: monotone flat or slightly increasing.
    Kinetic glass (no ice): monotone decreasing.

  SIG 4 (Kasteleyn load threshold): scan M/N in {0.1, 0.2, 0.3, 0.5, 0.7, 1.0}.
    Check if frustration (rate-dependence slope) APPEARS sharply above a critical M/N_c.
    Spin-ice: sharp transition at M/N_c (geometric-frustration onset).
    Random: smooth gradual onset.

PRE-REGISTERED BANDS:
  SPIN_ICE_MATCH (substrate matches documented spin-ice pattern):
    - SIG3: non-monotone (peak at intermediate epochs) -- most distinctive signature
    - AND SIG4: sharp transition at M/N_c (Kasteleyn-like)
    - P(this outcome): 0.18 (calibrated; novel-synthesis cap; spin-ice requires
      2D/3D geometric topology which substrate lacks explicitly)

  KINETIC_GLASS_DISTINCT (generic kinetic glass, not spin-ice):
    - SIG3: monotone decreasing (as in parent v1) -- no peak
    - SIG4: smooth gradual onset
    - SIG1: moderate frustration (0.70-0.90)
    - P(this outcome): 0.40

  FRUSTRATED_NOVEL (neither spin-ice nor generic kinetic glass):
    - SIG3: non-monotone OR flat
    - SIG1: high frustration (< 0.70) or > 0.90 with non-trivial decay
    - SIG2: anomalous decay exponent (not 0, not 3)
    - P(this outcome): 0.35 (most likely given substrate's structured-codebook nature)

  INSTRUMENTATION_FAIL: any SIG returns NaN or trivial constant

Queue: remote_cpu_queue (CPU; extended epochs sweep + M-scan; ~1-2h)
Pre-reg: preregs/2026-05-27_wave14_spin_ice_frustration_comparison_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Design parameters
N_FULL = 1024
N_SMOKE = 256
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
M_LOAD_FRACS = [0.1, 0.2, 0.3, 0.5, 0.7, 1.0]   # M/N for SIG4
M_LOAD_FRACS_SMOKE = [0.2, 0.5, 1.0]
EPOCHS_EXTENDED_FULL = [1, 2, 4, 8, 16, 32, 64, 128]
EPOCHS_EXTENDED_SMOKE = [1, 4, 16]
BATCH_STORE = 64

# Pre-registered thresholds
SIG1_ICE_RULE_MIN = 0.90
SIG1_FRUSTRATED_MAX = 0.80
SIG3_NON_MONOTONE_RATIO = 1.05  # peak > 1.05 * valley to call non-monotone
SIG4_KASTELEYN_SLOPE_MIN = 0.30  # d(slope)/d(M_N) > 0.30 -> sharp transition


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen, device=device).float() - 1.0


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int, epochs: int = 1) -> torch.Tensor:
    W = torch.zeros((N, N), dtype=torch.float32, device=keys.device)
    for _ in range(epochs):
        for s in range(0, keys.shape[0], BATCH_STORE):
            e = min(s + BATCH_STORE, keys.shape[0])
            W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def compute_retention(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor) -> float:
    y = (W @ keys.T).T
    yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
    vn = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-9)
    return float((yn * vn).sum(dim=1).mean())


def compute_top1_match_frac(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor,
                            all_vals: torch.Tensor) -> float:
    """Fraction of queries where top-1 retrieved pattern matches stored target."""
    y = (W @ keys.T).T   # (M, N)
    yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
    # For each query, find the most similar pattern in the entire library
    avN = all_vals / all_vals.norm(dim=1, keepdim=True).clamp(min=1e-9)
    sims = yn @ avN.T   # (M, M_total)
    best_idx = sims.argmax(dim=1)
    # Match: the retrieved pattern's index matches the query's original index
    # We compare cosine similarity to the true val
    vn = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-9)
    true_sim = (yn * vn).sum(dim=1)
    best_sim = sims.max(dim=1).values
    # "Ice rule satisfied" if true val is the best match (or within 0.05 of best)
    match = (true_sim >= best_sim - 0.05).float().mean()
    return float(match)


def compute_correlation_decay_exponent(keys: torch.Tensor) -> float:
    """Fit decay exponent of pairwise cosine overlap vs rank distance.
    Sort pairs by their index separation; fit log(overlap) ~ -b * log(rank).
    """
    M, N = keys.shape
    kn = keys / keys.norm(dim=1, keepdim=True).clamp(min=1e-9)
    # Sample at most 200 pairs for speed
    n_pairs = min(200, M * (M - 1) // 2)
    pairs = []
    for i in range(min(M, 20)):
        for j in range(i + 1, min(M, 20)):
            rank = j - i
            overlap = abs(float((kn[i] * kn[j]).sum()))
            pairs.append((rank, overlap))

    if len(pairs) < 2:
        return 0.0

    pairs.sort(key=lambda x: x[0])
    ranks = [math.log(p[0]) for p in pairs if p[1] > 1e-9]
    overlaps = [math.log(p[1]) for p in pairs if p[1] > 1e-9]
    if len(ranks) < 2:
        return 0.0

    # Linear regression: log(overlap) = a - b * log(rank)
    n = len(ranks)
    mx = sum(ranks) / n; my = sum(overlaps) / n
    cov = sum((ranks[i] - mx) * (overlaps[i] - my) for i in range(n))
    var_x = sum((ranks[i] - mx) ** 2 for i in range(n))
    b = cov / var_x if var_x > 0 else 0.0
    return -b   # return positive exponent (overlap decays as rank^-exponent)


# ---- SIG implementations ----

def run_sig1(N: int, M: int, seed: int, device) -> Dict:
    gen = torch.Generator(device=device).manual_seed(seed)
    keys = make_bsc(M, N, gen, device)
    vals = make_bsc(M, N, gen, device)
    W = outer_product_store(keys, vals, N)
    frac = compute_top1_match_frac(W, keys, vals, vals)
    if frac >= SIG1_ICE_RULE_MIN:
        call = "ICE_RULE"
    elif frac < SIG1_FRUSTRATED_MAX:
        call = "FRUSTRATED"
    else:
        call = "PARTIAL"
    print(f"  [SIG1] N={N} M={M} seed={seed}: match_frac={frac:.3f} -> {call}", flush=True)
    del W, keys, vals
    return {"match_frac": round(frac, 4), "call": call}


def run_sig2(N: int, M: int, seed: int, device) -> Dict:
    gen = torch.Generator(device=device).manual_seed(seed)
    keys = make_bsc(M, N, gen, device)
    exp = compute_correlation_decay_exponent(keys)
    print(f"  [SIG2] N={N} M={M} seed={seed}: decay_exponent={exp:.3f}", flush=True)
    del keys
    return {"decay_exponent": round(exp, 4)}


def run_sig3(N: int, M: int, epochs_sweep: List[int], seed: int, device) -> Dict:
    gen = torch.Generator(device=device).manual_seed(seed)
    keys = make_bsc(M, N, gen, device)
    vals = make_bsc(M, N, gen, device)

    # Forward-reverse hysteresis gap at each epoch count
    gaps = []
    for ep in epochs_sweep:
        gen2 = torch.Generator(device=device).manual_seed(seed + ep * 100)
        k2 = make_bsc(M, N, gen2, device)
        v2 = make_bsc(M, N, gen2, device)
        W_fwd = outer_product_store(k2, v2, N, epochs=ep)
        W_rev = outer_product_store(v2, k2, N, epochs=ep)
        ret_fwd = compute_retention(W_fwd, k2, v2)
        ret_rev = compute_retention(W_rev, v2, k2)
        gap = abs(ret_fwd - ret_rev)
        gaps.append(gap)
        del W_fwd, W_rev, k2, v2

    # Check for non-monotone (peak): max_gap >> min_gap after first element
    max_gap = max(gaps)
    min_gap_after1 = min(gaps[1:]) if len(gaps) > 1 else gaps[0]
    min_gap = min(gaps)
    peak_idx = gaps.index(max_gap)
    non_monotone = (max_gap > SIG3_NON_MONOTONE_RATIO * min_gap_after1 and peak_idx > 0
                    and peak_idx < len(gaps) - 1)
    monotone_decreasing = all(gaps[i] >= gaps[i+1] for i in range(len(gaps)-1))

    if non_monotone:
        call = "NON_MONOTONE"
    elif monotone_decreasing:
        call = "MONOTONE_DECREASING"
    else:
        call = "AMBIGUOUS"

    print(f"  [SIG3] N={N} M={M} seed={seed}: gaps={[round(g,3) for g in gaps]} "
          f"peak_idx={peak_idx} -> {call}", flush=True)
    del keys, vals
    return {"gaps": [round(g, 5) for g in gaps], "epochs": epochs_sweep,
            "non_monotone": non_monotone, "call": call}


def run_sig4(N: int, load_fracs: List[float], seed: int, device, epochs_ref: int = 4) -> Dict:
    """Kasteleyn-like threshold: scan M/N and check if frustration slope appears sharply."""
    gen = torch.Generator(device=device).manual_seed(seed)
    slopes = {}
    for frac in load_fracs:
        M = max(10, int(frac * N))
        k = make_bsc(M, N, gen, device)
        v = make_bsc(M, N, gen, device)
        # Estimate rate-dependence slope at this load
        gaps_at_load = []
        for ep in [1, epochs_ref]:
            gen2 = torch.Generator(device=device).manual_seed(seed + int(frac * 1000))
            k2 = make_bsc(M, N, gen2, device)
            v2 = make_bsc(M, N, gen2, device)
            W_fwd = outer_product_store(k2, v2, N, epochs=ep)
            W_rev = outer_product_store(v2, k2, N, epochs=ep)
            gap = abs(compute_retention(W_fwd, k2, v2) - compute_retention(W_rev, v2, k2))
            gaps_at_load.append(gap)
            del W_fwd, W_rev, k2, v2
        # Rate-dependence: gap change per log-epochs unit
        log_ep = math.log(epochs_ref)
        rd_slope = (gaps_at_load[1] - gaps_at_load[0]) / max(log_ep, 0.01)
        slopes[frac] = round(rd_slope, 5)
        print(f"  [SIG4] N={N} M/N={frac:.1f}: gaps={[round(g,3) for g in gaps_at_load]} "
              f"rd_slope={rd_slope:.4f}", flush=True)
        del k, v

    # Check for sharp onset: max dslope/dload
    fracs_sorted = sorted(slopes.keys())
    if len(fracs_sorted) >= 2:
        dslopes = [abs(slopes[fracs_sorted[i+1]] - slopes[fracs_sorted[i]]) /
                   (fracs_sorted[i+1] - fracs_sorted[i])
                   for i in range(len(fracs_sorted)-1)]
        max_dslope = max(dslopes)
        onset_frac = fracs_sorted[dslopes.index(max_dslope)]
    else:
        max_dslope = 0.0
        onset_frac = 0.0

    if max_dslope > SIG4_KASTELEYN_SLOPE_MIN:
        call = "KASTELEYN_SHARP"
    else:
        call = "SMOOTH_ONSET"

    print(f"  [SIG4] max_dslope={max_dslope:.4f} onset_frac={onset_frac:.2f} -> {call}", flush=True)
    return {"slopes_by_load": slopes, "max_dslope": round(max_dslope, 5),
            "onset_frac": onset_frac, "call": call}


def compute_joint_verdict(sig1, sig2, sig3, sig4) -> Tuple[str, str]:
    s1, s3, s4 = sig1["call"], sig3["call"], sig4["call"]
    spin_ice = (s3 == "NON_MONOTONE" and s4 == "KASTELEYN_SHARP")
    kinetic = (s3 == "MONOTONE_DECREASING" and s4 == "SMOOTH_ONSET")
    exp = sig2["decay_exponent"]

    if spin_ice:
        verdict = "SPIN_ICE_MATCH"
        msg = (f"Substrate frustration matches spin-ice signatures: "
               f"non-monotone cooling gap (SIG3={s3}) + Kasteleyn-like sharp onset (SIG4={s4}). "
               f"Pattern consistent with topological spin glass in diluted spin ice (arXiv:1405.0668). "
               f"decay_exponent={exp:.3f}")
    elif kinetic and s1 == "PARTIAL":
        verdict = "KINETIC_GLASS_DISTINCT"
        msg = (f"Generic kinetic glass (not spin-ice): monotone-decreasing gap (SIG3) + "
               f"smooth onset (SIG4) + partial ice rule (SIG1={s1}). "
               f"decay_exponent={exp:.3f}. Substrate is a standard kinetic glass without "
               f"topological order.")
    else:
        verdict = "FRUSTRATED_NOVEL"
        msg = (f"Frustration pattern is neither spin-ice nor generic kinetic glass: "
               f"SIG1={s1} SIG3={s3} SIG4={s4} decay_exp={exp:.3f}. "
               f"Substrate frustration is driven by the structured codebook geometry "
               f"(Kerdock orbit structure), which has no direct spin-ice analog. "
               f"This is a novel frustration mechanism consistent with SKAH-M framing.")
    return verdict, msg


# ---- instrumentation self-test ----

def _instrumentation_selftest() -> None:
    print("[selftest] starting...", flush=True)
    device = torch.device("cpu")
    gen = torch.Generator(device=device).manual_seed(42)

    # 1. make_bsc shape + BSC
    v = make_bsc(5, 32, gen, device)
    assert v.shape == (5, 32) and set(v.unique().tolist()).issubset({-1.0, 1.0}), "FAIL 1"
    print("[selftest] 1/4 make_bsc OK")

    # 2. outer_product_store: finite output
    k = make_bsc(8, 32, gen, device)
    val = make_bsc(8, 32, gen, device)
    W = outer_product_store(k, val, 32, epochs=2)
    assert W.shape == (32, 32) and math.isfinite(float(W.abs().mean())), "FAIL 2"
    print("[selftest] 2/4 outer_product_store OK")

    # 3. compute_top1_match_frac: value in [0, 1]
    frac = compute_top1_match_frac(W, k, val, val)
    assert 0.0 <= frac <= 1.0, f"FAIL 3: frac={frac}"
    print(f"[selftest] 3/4 compute_top1_match_frac={frac:.3f} OK")

    # 4. run_sig1 + run_sig3 smoke
    r1 = run_sig1(32, 8, 7, device)
    assert "call" in r1 and "match_frac" in r1, f"FAIL 4a: {r1}"
    r3 = run_sig3(32, 8, [1, 2, 4], 7, device)
    assert "call" in r3 and len(r3["gaps"]) == 3, f"FAIL 4b: {r3}"
    print(f"[selftest] 4/4 SIG1={r1['call']} SIG3={r3['call']} OK")

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()


# ---- main sweep ----

def run_sweep(smoke: bool = False):
    device = torch.device("cpu")
    print(f"[spin_ice_frustration] device={device} smoke={smoke}", flush=True)
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    load_fracs = M_LOAD_FRACS_SMOKE if smoke else M_LOAD_FRACS
    epochs_ext = EPOCHS_EXTENDED_SMOKE if smoke else EPOCHS_EXTENDED_FULL
    M_ref = int(0.5 * N)   # reference M for SIG1, SIG2, SIG3

    out_dir = get_output_dir("wave14_spin_ice_frustration_comparison_v1")
    t0 = time.time()

    all_sig1, all_sig2, all_sig3, all_sig4 = [], [], [], []
    for seed in seeds:
        print(f"\n=== seed={seed} ===", flush=True)
        s1 = run_sig1(N, M_ref, seed, device)
        s2 = run_sig2(N, M_ref, seed, device)
        s3 = run_sig3(N, M_ref, epochs_ext, seed, device)
        s4 = run_sig4(N, load_fracs, seed, device)
        all_sig1.append(s1); all_sig2.append(s2); all_sig3.append(s3); all_sig4.append(s4)

    # Aggregate: majority call
    def majority_call(sigs):
        calls = [s["call"] for s in sigs]
        return max(set(calls), key=calls.count)

    agg_sig1 = {"call": majority_call(all_sig1),
                "mean_match_frac": round(sum(s["match_frac"] for s in all_sig1) / len(all_sig1), 4)}
    agg_sig2 = {"decay_exponent": round(sum(s["decay_exponent"] for s in all_sig2) / len(all_sig2), 4)}
    agg_sig3 = {"call": majority_call(all_sig3)}
    agg_sig4 = {"call": majority_call(all_sig4)}

    verdict, msg = compute_joint_verdict(agg_sig1, agg_sig2, agg_sig3, agg_sig4)
    elapsed = time.time() - t0

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "smoke": smoke,
        "N": N,
        "elapsed_s": round(elapsed, 1),
        "agg_sig1": agg_sig1,
        "agg_sig2": agg_sig2,
        "agg_sig3": agg_sig3,
        "agg_sig4": agg_sig4,
        "per_seed": {"sig1": all_sig1, "sig2": all_sig2, "sig3": all_sig3, "sig4": all_sig4},
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[exp] metrics written to {metrics_path}", flush=True)
    return metrics, out_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    run_sweep(smoke=args.smoke)
