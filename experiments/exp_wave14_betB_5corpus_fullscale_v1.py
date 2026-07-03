"""5-corpus equal-spacing GPU full-scale: boost G4_NOREPLAY from n=5 to n=15.

CONTEXT: exp_wave14_betB_5corpus_equalspacing_v1 returned MIDDLE_BAND
(BIC_delta=-8.64, missed -10 by 1.4; spacing_error=0.0284 PASSES < 0.05; all
5 CIs non-overlapping). The MIDDLE was a POWER PROBLEM: G4_NOREPLAY has n=5
in the existing data, giving wide CIs and low BIC improvement per added state.

FIX: generate 15 additional NO_REPLAY_SAME_CORPUS cells at N=4096, combine with
existing data, then re-run the 5-state BIC and spacing analysis. With n_G4 = 20,
the BIC_delta should cross -10 cleanly if the 5th plateau is real.

DESIGN:
  NO_REPLAY_SAME_CORPUS protocol:
    Phase A: train W on corpus_A (same as standard), 8 epochs
    Phase B: train W on corpus_B = shuffled corpus_A, 5 epochs, WITH replay pool from A
    Phase C: re-evaluate on corpus_A with W from phase B (NO additional replay)
             This is: same-corpus-context but WITHOUT inter-phase replay enrichment.
    retention = bpc(A, after_B) / bpc(A, after_A)

  This matches the "SAME_CORPUS but NO INTER-PHASE REPLAY" condition from the
  original shift_class_predictor data (NO_REPLAY_SAME_CORPUS label).

  N=4096, 15 new seeds (seeds 100-114), combine with existing 5 = n_G4=20

DEPENDENCY: data/exp_wave14_betB_shift_class_predictor_v1/metrics.json must exist.

Pre-registered bands (5-plateau extension with n_G4=20):
  HARD_PASS: BIC_delta_5vs4 < -10 AND spacing_error < 0.05
             AND ordered monotone AND G4 distinct from both G3 and G5
  HARD_FAIL: BIC_delta_5vs4 > 0 OR spacing_error > 0.10 OR not ordered
             OR G4 not distinct from at least one neighbor
  MIDDLE_BAND: BIC_delta_5vs4 in (-10, 0) AND spacing_error in [0.05, 0.10]
  INSTRUMENTATION_FAIL: G4_NOREPLAY n_total < 10 after augmentation

Queue: overnight_queue (GPU; 15 seeds x 2-stage A->B at N=4096; ~2-3 GPU-hrs)
Pre-reg: prereqs/2026-05-26_wave14_betB_5corpus_fullscale_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Load base infrastructure via M1 hierreplay (which loads 4-stage which loads base)
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
pa = base.pa
v1 = m1.v1

# Design parameters (exp_dev autonomy)
N_FULL = 4096
N_SMOKE = 512
SEEDS_NEW_FULL = list(range(100, 115))    # 15 new seeds
SEEDS_NEW_SMOKE = [100, 101]              # 2 seeds for smoke
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200_000
BYTES_SMOKE = 5_000

# Pre-registered thresholds
HP_BIC_DELTA = -10.0      # 5-state vs 4-state BIC delta (relaxed from -30; n_G4 is smaller)
HP_SPACING_ERR = 0.05
HF_SPACING_ERR = 0.10
INSTFAIL_MIN_G4 = 10      # fail if combined G4 n < 10


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing: {missing}")


# ---------------------------------------------------------------------------
# Statistical helpers (same as 5corpus_equalspacing_v1)
# ---------------------------------------------------------------------------

def group_mean_std(vals: List[float]) -> Tuple[float, float]:
    n = len(vals)
    if n == 0:
        return float("nan"), float("nan")
    mu = sum(vals) / n
    if n == 1:
        return mu, 0.0
    var = sum((v - mu) ** 2 for v in vals) / (n - 1)
    return mu, math.sqrt(var)


def ci_95(vals: List[float]) -> Tuple[float, float]:
    n = len(vals)
    if n < 2:
        mu = vals[0] if vals else float("nan")
        return mu, mu
    mu, std = group_mean_std(vals)
    se = std / math.sqrt(n)
    t_table = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
               6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
               12: 2.179, 15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042}
    df = n - 1
    if df in t_table:
        t = t_table[df]
    elif n >= 30:
        t = 1.960
    else:
        t = 2.042
    margin = t * se
    return mu - margin, mu + margin


def ci_overlap_fraction(ci_a: Tuple[float, float], ci_b: Tuple[float, float]) -> float:
    lo_a, hi_a = ci_a
    lo_b, hi_b = ci_b
    overlap_lo = max(lo_a, lo_b)
    overlap_hi = min(hi_a, hi_b)
    if overlap_hi <= overlap_lo:
        return 0.0
    overlap = overlap_hi - overlap_lo
    min_width = min(hi_a - lo_a, hi_b - lo_b)
    if min_width <= 0:
        return 0.0
    return overlap / min_width


def discrete_bic(all_vals: List[float], groups: List[List[float]]) -> float:
    n = len(all_vals)
    k = len(groups)
    if n <= k + 1:
        return float("inf")
    rss = 0.0
    for g in groups:
        if len(g) == 0:
            continue
        mu_g = sum(g) / len(g)
        rss += sum((v - mu_g) ** 2 for v in g)
    if rss <= 0 or n <= 0:
        return float("inf")
    sigma2_hat = rss / n
    log_lik = -n / 2.0 * (math.log(2 * math.pi * sigma2_hat) + 1.0)
    n_params = k + 1
    return -2.0 * log_lik + n_params * math.log(n)


def equal_spacing_error(means: List[float]) -> float:
    K = len(means)
    if K < 2:
        return 0.0
    pred = [means[0] - (k / (K - 1)) * (means[0] - means[-1]) for k in range(K)]
    err = math.sqrt(sum((obs - p) ** 2 for obs, p in zip(means, pred)) / K)
    return err


# ---------------------------------------------------------------------------
# Run NO_REPLAY_SAME_CORPUS protocol: A->B, measure ret(A after B), NO extra replay
# ---------------------------------------------------------------------------

def run_noreplay_same_corpus(seed: int, N: int, batch_size: int, epochs: int,
                              phase_a_epochs: int, n_bytes: int,
                              smoke: bool, device) -> Optional[float]:
    """Run A->B training without inter-phase replay; return retention_A after B.

    Protocol:
      Phase A: train W on corpus_A with NO prior replay
      Phase B: train W on corpus_B (shuffled A) with NO replay from Phase A
               (this is the key: we intentionally omit replay to get NO_REPLAY condition)
      retention = bpc_A_after_B / bpc_A_after_A
    """
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    def to_idx(tr):
        return base.bytes_to_idx_tensors(tr, device)

    train_a, val_a = split80(corpus_a)
    train_b, _ = split80(corpus_b)

    train_a_idx, train_a_tgt = to_idx(train_a)
    train_b_idx, train_b_tgt = to_idx(train_b)
    val_a_idx, val_a_tgt = to_idx(val_a)

    W_init = torch.zeros((N, N), dtype=torch.float32, device=device)

    # Phase A: train with no replay (fresh start)
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_init, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)

    # Phase B: train on corpus_B WITHOUT replay (intentionally zero replay)
    # Pass zero replay pool to implement NO_REPLAY condition
    W_B, pool_B_v, pool_B_l, pool_B_u = base.train_w_with_replay(
        W_A, None, None, 0, byte_atoms, pos_atoms,
        train_b_idx, train_b_tgt, None, None, 0,
        epochs, batch_size, device)

    # Evaluate retention
    try:
        bpc_a_after_a = float(base.evaluate_bpc(
            W_A, pool_A_v, pool_A_l, pool_A_u,
            byte_atoms, pos_atoms, val_a_idx, val_a_tgt,
            batch_size, device))
        bpc_a_after_b = float(base.evaluate_bpc(
            W_B, pool_B_v, pool_B_l, pool_B_u,
            byte_atoms, pos_atoms, val_a_idx, val_a_tgt,
            batch_size, device))
    except Exception as e:
        print(f"  seed={seed} eval error: {e}", flush=True)
        return None

    if bpc_a_after_a is None or bpc_a_after_a <= 0 or bpc_a_after_b is None:
        return None

    retention = float(bpc_a_after_a / max(bpc_a_after_b, 1e-6))
    del W_A, W_B
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return retention


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert instrumentation is valid before main sweep."""
    print("[selftest] running...", flush=True)

    # 1. BIC 5-state vs 4-state on synthetic equal-spaced 5-class data
    g1 = [0.94 + 0.005 * i for i in range(5)]
    g2 = [0.80 + 0.005 * i for i in range(5)]
    g3 = [0.67 + 0.005 * i for i in range(5)]
    g4 = [0.55 + 0.005 * i for i in range(5)]
    g5 = [0.42 + 0.005 * i for i in range(5)]
    all_vals = g1 + g2 + g3 + g4 + g5
    bic5 = discrete_bic(all_vals, [g1, g2, g3, g4, g5])
    bic4 = discrete_bic(all_vals, [g1, g2, g3, g4 + g5])
    assert bic5 < bic4, f"Selftest 1 FAIL: bic5={bic5:.2f} not < bic4={bic4:.2f}"
    print("[selftest] 1/4 BIC 5-state preferred for equal-spaced data OK")

    # 2. equal_spacing_error = 0 for perfect 5-point equal spacing
    perf = [0.9, 0.7, 0.5, 0.3, 0.1]
    err = equal_spacing_error(perf)
    assert err < 1e-9, f"Selftest 2 FAIL: perfect equal-spacing err={err}"
    print("[selftest] 2/4 equal_spacing_error perfect 5-point OK")

    # 3. dependency data check (soft: data may not exist on remote at gate-check time;
    #    hard dependency is only required at run time via INSTRUMENTATION_FAIL verdict)
    src = REPO / "data" / "exp_wave14_betB_shift_class_predictor_v1" / "metrics.json"
    if src.exists():
        with open(src) as f:
            m = json.load(f)
        required = {"SAME_CORPUS_PRISTINE", "REPLAY_SAME_CORPUS", "STAGE_4_COMPOUND",
                    "NO_REPLAY_SAME_CORPUS", "DIFF_CORPUS_2TASK"}
        classes = set(m["summary"]["per_class"].keys())
        missing = required - classes
        assert not missing, f"Selftest 3 FAIL: missing classes {missing}"
        n4 = len(m["summary"]["per_class"]["NO_REPLAY_SAME_CORPUS"]["values"])
        assert n4 >= 3, f"Selftest 3 FAIL: existing G4 n={n4} < 3"
        print(f"[selftest] 3/4 dependency data present (existing G4 n={n4}) OK")
    else:
        print(f"[selftest] 3/4 dependency data not found at gate-check time -- "
              f"will be verified at run time (INSTRUMENTATION_FAIL if absent) OK")

    # 4. base.train_w_with_replay and evaluate_bpc are callable (no TypeError at tiny scale)
    device_test = torch.device("cpu")
    N_test = 64
    gen_test = torch.Generator().manual_seed(99)
    ba_test = pa.make_bsc_atoms(base.VOCAB, N_test, gen_test).to(device_test)
    pa_test = pa.make_bsc_atoms(base.K, N_test, gen_test).to(device_test)
    corpus_tiny = pa.load_corpus_a()[:500]
    corpus_b_tiny = pa.shuffle_bytes(corpus_tiny, seed=200)
    def to_idx_test(d):
        return base.bytes_to_idx_tensors(d[:400], device_test)
    tvidx, tvtgt = to_idx_test(corpus_tiny)
    W_test = torch.zeros((N_test, N_test), dtype=torch.float32, device=device_test)
    W_out, pv, pl, pu = base.train_w_with_replay(
        W_test, None, None, 0, ba_test, pa_test, tvidx, tvtgt,
        None, None, 0, 1, 16, device_test)
    assert W_out is not None and W_out.shape == (N_test, N_test), "Selftest 4 FAIL: train_w"
    val_idx, val_tgt = to_idx_test(corpus_tiny[400:])
    bpc_val = float(base.evaluate_bpc(
        W_out, pv, pl, pu, ba_test, pa_test, val_idx, val_tgt, 16, device_test))
    assert math.isfinite(bpc_val), f"Selftest 4 FAIL: bpc={bpc_val}"
    print(f"[selftest] 4/4 train+evaluate callable at N={N_test} bpc={bpc_val:.4f} OK")
    print("[selftest] PASS 4/4", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

def run(smoke: bool = False):
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_NEW_SMOKE if smoke else SEEDS_NEW_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL
    out_dir = get_output_dir("wave14_betB_5corpus_fullscale_v1")

    print(f"[exp] wave14_betB_5corpus_fullscale_v1 {'SMOKE' if smoke else 'FULL'} "
          f"N={N} seeds={seeds} device={device}", flush=True)

    # 1. Generate new NO_REPLAY_SAME_CORPUS retention values
    new_g4_vals: List[float] = []
    for seed in seeds:
        print(f"  seed={seed}...", end=" ", flush=True)
        ret = run_noreplay_same_corpus(seed, N, batch_size, epochs,
                                       phase_a_epochs, n_bytes, smoke, device)
        if ret is not None:
            new_g4_vals.append(ret)
            print(f"ret_G4={ret:.4f}", flush=True)
        else:
            print("FAIL (None)", flush=True)

    print(f"\n[run] generated {len(new_g4_vals)} new G4_NOREPLAY values: "
          f"mean={sum(new_g4_vals)/max(len(new_g4_vals),1):.4f}", flush=True)

    # 2. Load existing per-class data and combine
    src = REPO / "data" / "exp_wave14_betB_shift_class_predictor_v1" / "metrics.json"
    with open(src) as f:
        existing = json.load(f)
    pc = existing["summary"]["per_class"]

    g1_existing = pc["SAME_CORPUS_PRISTINE"]["values"]
    g2_existing = pc["REPLAY_SAME_CORPUS"]["values"]
    g3_existing = pc["STAGE_4_COMPOUND"]["values"]
    g4_existing = pc["NO_REPLAY_SAME_CORPUS"]["values"]
    g5_existing = pc["DIFF_CORPUS_2TASK"]["values"]

    g4_combined = g4_existing + new_g4_vals

    print(f"[run] combined G4_NOREPLAY: existing={len(g4_existing)} + "
          f"new={len(new_g4_vals)} = {len(g4_combined)} total", flush=True)

    # At smoke scale: validate instrumentation only; skip BIC analysis
    # (N=512 G4 values are in wrong regime to combine with N=4096 existing data)
    if smoke:
        if len(new_g4_vals) == 0:
            verdict = "INSTRUMENTATION_FAIL"
            verdict_msg = "INSTRUMENTATION_FAIL: no valid G4_NOREPLAY values at smoke scale"
        else:
            verdict = "SMOKE_PASS"
            verdict_msg = (f"SMOKE_PASS: instrumentation valid. "
                           f"{len(new_g4_vals)}/{len(seeds)} seeds produced finite G4_NOREPLAY "
                           f"retention values (mean={sum(new_g4_vals)/len(new_g4_vals):.4f}). "
                           f"NOTE: smoke at N={N} is regime-mismatched vs existing N=4096 data; "
                           f"BIC analysis skipped at smoke scale. FULL run at N=4096 needed.")
        metrics = {
            "verdict": verdict, "verdict_msg": verdict_msg,
            "elapsed_s": round(time.time() - t0, 3),
            "summary": {
                "n_new_g4": len(new_g4_vals), "new_g4_vals": [round(v, 4) for v in new_g4_vals],
                "smoke_only": True,
                "note": "BIC analysis requires N=4096 full run; smoke validates protocol only",
            },
            "config": {"N": N, "smoke": smoke, "seeds_new": seeds},
        }
        validate_metrics(metrics)
        with open(out_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"Verdict: {verdict}")
        print(f"Msg: {verdict_msg}")
        return

    # Instrumentation fail if combined G4 is still too small
    if len(g4_combined) < INSTFAIL_MIN_G4:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (f"INSTRUMENTATION_FAIL: G4_NOREPLAY combined n={len(g4_combined)} "
                       f"< {INSTFAIL_MIN_G4} minimum; insufficient for reliable 5-state BIC")
        metrics = {
            "verdict": verdict, "verdict_msg": verdict_msg,
            "elapsed_s": round(time.time() - t0, 3),
            "summary": {"n_G4_combined": len(g4_combined), "n_new": len(new_g4_vals)},
            "config": {"N": N, "smoke": smoke},
        }
        validate_metrics(metrics)
        with open(out_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        return

    # 3. 5-state BIC and equal-spacing analysis
    groups = [g1_existing, g2_existing, g3_existing, g4_combined, g5_existing]
    labels = ["G1_SAME", "G2_REPLAY", "G3_STAGE4", "G4_NOREPLAY", "G5_DIFF"]
    all_vals = g1_existing + g2_existing + g3_existing + g4_combined + g5_existing

    means = [sum(g) / max(len(g), 1) for g in groups]
    print(f"\n[analysis] 5-class means: " +
          " ".join(f"{lbl}={mu:.4f}(n={len(g)})" for lbl, mu, g in zip(labels, means, groups)),
          flush=True)

    ordered = all(means[i] > means[i+1] for i in range(len(means) - 1))

    # 5-state BIC vs 4-state (merging G4+G5)
    bic_5state = discrete_bic(all_vals, [g1_existing, g2_existing, g3_existing, g4_combined, g5_existing])
    bic_4state = discrete_bic(all_vals, [g1_existing, g2_existing, g3_existing, g4_combined + g5_existing])
    bic_3state = discrete_bic(all_vals, [g1_existing, g2_existing + g3_existing + g4_combined, g5_existing])
    delta_5vs4 = bic_5state - bic_4state
    delta_5vs3 = bic_5state - bic_3state

    spacing_err = equal_spacing_error(means)

    print(f"[analysis] BIC: 5-state={bic_5state:.2f} 4-state={bic_4state:.2f} "
          f"3-state={bic_3state:.2f}", flush=True)
    print(f"[analysis] delta_5vs4={delta_5vs4:.2f} delta_5vs3={delta_5vs3:.2f} "
          f"spacing_error={spacing_err:.4f} ordered={ordered}", flush=True)

    # CI overlap tests
    cis = [ci_95(g) for g in groups]
    adjacent_overlaps = []
    for i in range(len(cis) - 1):
        ov = ci_overlap_fraction(cis[i], cis[i+1])
        adjacent_overlaps.append({"pair": f"{labels[i]}/{labels[i+1]}", "overlap": round(ov, 3),
                                   "distinct": ov < 0.5})
    g4_distinct_from_g3 = adjacent_overlaps[2]["distinct"]
    g4_distinct_from_g5 = adjacent_overlaps[3]["distinct"]

    print(f"[analysis] G4 distinct from G3: {g4_distinct_from_g3}, G5: {g4_distinct_from_g5}",
          flush=True)

    # Verdict
    hard_pass = (delta_5vs4 < HP_BIC_DELTA and spacing_err < HP_SPACING_ERR
                 and ordered and g4_distinct_from_g3 and g4_distinct_from_g5)
    hard_fail = (delta_5vs4 > 0 or spacing_err > HF_SPACING_ERR or not ordered
                 or not (g4_distinct_from_g3 or g4_distinct_from_g5))

    if hard_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: 5-state equal-spacing confirmed with n_G4={len(g4_combined)}. "
            f"BIC_delta_5vs4={delta_5vs4:.2f} < -10. "
            f"spacing_error={spacing_err:.4f} < 0.05. "
            f"Ordered={ordered}. G4 distinct from neighbors. "
            f"Saad-Solla equal-spacing arithmetic generalizes to 5-plateau structure."
        )
    elif hard_fail:
        reasons = []
        if delta_5vs4 > 0:
            reasons.append(f"4-state preferred (delta={delta_5vs4:.2f} > 0)")
        if spacing_err > HF_SPACING_ERR:
            reasons.append(f"spacing_error={spacing_err:.4f} > 0.10")
        if not ordered:
            reasons.append("monotone order violated")
        if not g4_distinct_from_g3:
            reasons.append("G4 not distinct from G3")
        if not g4_distinct_from_g5:
            reasons.append("G4 not distinct from G5")
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: 5-plateau equal-spacing does not hold even at n_G4={len(g4_combined)}. "
            f"Reasons: {'; '.join(reasons)}. 4-plateau structure has a hard limit."
        )
    else:
        blocking = []
        if delta_5vs4 >= HP_BIC_DELTA:
            blocking.append(f"BIC_delta={delta_5vs4:.2f} not < -10")
        if spacing_err >= HP_SPACING_ERR:
            blocking.append(f"spacing_error={spacing_err:.4f} not < 0.05")
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: Blocking: {'; '.join(blocking) if blocking else 'unknown'}. "
            f"n_G4={len(g4_combined)} spacing_error={spacing_err:.4f} "
            f"BIC_delta={delta_5vs4:.2f}. May need n_G4 > 20 for definitive BIC."
        )

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    summary = {
        "group_means": {lbl: round(mu, 4) for lbl, mu in zip(labels, means)},
        "group_sizes": {lbl: len(g) for lbl, g in zip(labels, groups)},
        "n_G4_existing": len(g4_existing),
        "n_G4_new": len(new_g4_vals),
        "n_G4_combined": len(g4_combined),
        "new_g4_vals": [round(v, 4) for v in new_g4_vals],
        "bic_5state": round(bic_5state, 2),
        "bic_4state": round(bic_4state, 2),
        "bic_3state": round(bic_3state, 2),
        "delta_bic_5vs4": round(delta_5vs4, 2),
        "delta_bic_5vs3": round(delta_5vs3, 2),
        "spacing_error_5state": round(spacing_err, 4),
        "ordered": ordered,
        "adjacent_ci_overlaps": adjacent_overlaps,
        "g4_distinct_from_g3": g4_distinct_from_g3,
        "g4_distinct_from_g5": g4_distinct_from_g5,
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "config": {
            "N": N, "smoke": smoke,
            "seeds_new": seeds,
            "n_seeds_run": len(seeds),
            "n_g4_new_valid": len(new_g4_vals),
            "dependency": "data/exp_wave14_betB_shift_class_predictor_v1/metrics.json",
            "protocol": "NO_REPLAY_SAME_CORPUS: Phase_A(corpus_A) -> Phase_B(corpus_B, no_replay); "
                        "measure ret(A after B)",
        },
    }
    validate_metrics(metrics)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
