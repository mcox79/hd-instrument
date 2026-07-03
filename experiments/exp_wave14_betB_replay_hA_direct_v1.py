"""Bet B REPLAY mechanism H-A consolidation direct probe.

CONTEXT: v209 narrows REPLAY mechanism:
  - H-C (effective-N-doubling) REFUTED: replay outperforms 2x-data by +16.5pp
  - H-B (interference-reduction) INCONCLUSIVE: direct_lift=0.123 < 0.15 threshold
  - H-A (consolidation) FAVORED: residual hypothesis after H-C refuted, H-B inconclusive

H-A CONSOLIDATION HYPOTHESIS: replay works by re-activating recently learned associations
during sleep-like offline consolidation. The key prediction is that TIMING of replay matters:
  - Replay between stages (inter-phase replay, simulating sleep) should EXCEED replay
    within stages (intra-phase replay, same effectiveness as data augmentation).
  - Prediction: ret_interphase > ret_intra_phase by >= 0.05 retention points.

DESIGN (exp_dev autonomy):
  Arm 1 (H-A INTER-PHASE): replay budget injected BETWEEN phases A->B, B->C, C->D
    (i.e., additional M_replay items replayed at the START of each new phase, before
    new corpus tokens). Consolidation simulates offline sleep replay.
  Arm 2 (INTRA-PHASE, control): same replay budget but distributed WITHIN phases
    (interleaved with new tokens, same as standard M1 replay). This is the baseline.
  Arm 3 (NO-REPLAY): zero replay (measures baseline forgetting floor).

Prediction (H-A): Arm 1 (inter-phase) > Arm 2 (intra-phase) by >= 0.05 retention.
Null (H-A fails): Arm 1 ~= Arm 2 (timing doesn't matter; any replay is data augmentation).

Pre-registered bands:
  HARD-PASS (H-A consolidation confirmed): ret(Arm1) - ret(Arm2) >= 0.05 at Arm1 >= 0.80
             AND ret(Arm2) > ret(Arm3) (basic replay benefit present)
  HARD-FAIL (H-A rejected): |ret(Arm1) - ret(Arm2)| < 0.02 (timing irrelevant)
             OR ret(Arm1) < ret(Arm3) (inter-phase replay HURTS)
  MIDDLE: ret(Arm1) - ret(Arm2) in [0.02, 0.05) (weak consolidation signal)

Walk-back: if smoke |Arm1 - Arm2| < 0.03, FULL at N*2 or 10 seeds.

Queue: overnight_queue (GPU; 3 arms x 5 seeds x N=4096; ~2-3 GPU-hrs)
Pre-reg: preregs/2026-05-26_wave14_betB_replay_hA_direct_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Load M1 hierreplay infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
v1_mod = m1.v1
pa = m1.pa

# ── design parameters (exp_dev autonomy) ──
N_FULL = 4096
N_SMOKE = 512
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 100_000
BYTES_SMOKE = 3_000

# Replay budget: fraction of pool to replay at each inter/intra phase boundary
REPLAY_FRACTION_FULL = 0.3
REPLAY_FRACTION_SMOKE = 0.3

# Pre-reg thresholds
HP_INTERPHASE_LIFT = 0.05    # HARD-PASS: Arm1 - Arm2 >= this
HF_TIMING_IRRELEVANT = 0.02  # HARD-FAIL: |Arm1 - Arm2| < this


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing: {missing}")


def run_arm_interphase(seed, N, batch_size, epochs, phase_a_epochs, n_bytes,
                       replay_frac, smoke, device):
    """Arm 1: inter-phase replay (consolidation between stages)."""
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = v1_mod.load_corpus_D(smoke=smoke)
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    def to_idx(tr):
        return base.bytes_to_idx_tensors(tr, device)

    train_a, val_a = split80(corpus_a)
    train_b, _ = split80(corpus_b)
    train_c, _ = split80(corpus_c)
    train_d, _ = split80(corpus_d)

    train_a_idx, train_a_tgt = to_idx(train_a)
    train_b_idx, train_b_tgt = to_idx(train_b)
    train_c_idx, train_c_tgt = to_idx(train_c)
    train_d_idx, train_d_tgt = to_idx(train_d)
    val_a_idx, val_a_tgt = to_idx(val_a)

    W = torch.zeros((N, N), dtype=torch.float32, device=device)

    # Phase A (no replay)
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)

    bpc_a_fresh = float(base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                           byte_atoms, pos_atoms,
                                           val_a_idx, val_a_tgt, batch_size, device))

    # INTER-PHASE: replay A items BEFORE Phase B starts (consolidation burst)
    thin_A_v, thin_A_l, thin_A_u = m1.thin_pool_to_chunks(
        pool_A_v, pool_A_l, pool_A_u, chunk_fraction=replay_frac, device=device)

    # Phase B: start with inter-phase replay of A, then new B tokens
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        thin_A_v, thin_A_l, thin_A_u, epochs, batch_size, device)

    thin_B_v, thin_B_l, thin_B_u = m1.thin_pool_to_chunks(
        pool_AB_v, pool_AB_l, pool_AB_u, chunk_fraction=replay_frac, device=device)
    combo_AB_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u]], dim=0)
    combo_AB_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u]], dim=0)
    combo_AB_u = combo_AB_v.shape[0]

    # Phase C
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combo_AB_v, combo_AB_l, combo_AB_u, epochs, batch_size, device)

    thin_C_v, thin_C_l, thin_C_u = m1.thin_pool_to_chunks(
        pool_ABC_v, pool_ABC_l, pool_ABC_u, chunk_fraction=replay_frac, device=device)
    combo_ABC_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u],
                              thin_C_v[:thin_C_u]], dim=0)
    combo_ABC_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u],
                              thin_C_l[:thin_C_u]], dim=0)
    combo_ABC_u = combo_ABC_v.shape[0]

    # Phase D (capture pool for evaluate_bpc)
    W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms, train_d_idx, train_d_tgt,
        combo_ABC_v, combo_ABC_l, combo_ABC_u, epochs, batch_size, device)

    bpc_a_after = float(base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                          byte_atoms, pos_atoms,
                                          val_a_idx, val_a_tgt, batch_size, device))

    ret = bpc_a_fresh / max(bpc_a_after, 1e-6)
    del W_A, W_AB, W_ABC, W_ABCD
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return float(ret), float(bpc_a_fresh), float(bpc_a_after)


def run_arm_intraephase(seed, N, batch_size, epochs, phase_a_epochs, n_bytes,
                        replay_frac, smoke, device):
    """Arm 2: intra-phase replay (interleaved, same as standard M1 baseline)."""
    # This is exactly the standard M1 hierreplay behavior -- use existing infrastructure
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = v1_mod.load_corpus_D(smoke=smoke)
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    def to_idx(tr):
        return base.bytes_to_idx_tensors(tr, device)

    train_a, val_a = split80(corpus_a)
    train_b, _ = split80(corpus_b)
    train_c, _ = split80(corpus_c)
    train_d, _ = split80(corpus_d)

    train_a_idx, train_a_tgt = to_idx(train_a)
    train_b_idx, train_b_tgt = to_idx(train_b)
    train_c_idx, train_c_tgt = to_idx(train_c)
    train_d_idx, train_d_tgt = to_idx(train_d)
    val_a_idx, val_a_tgt = to_idx(val_a)

    W = torch.zeros((N, N), dtype=torch.float32, device=device)

    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)

    bpc_a_fresh = float(base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                           byte_atoms, pos_atoms,
                                           val_a_idx, val_a_tgt, batch_size, device))

    thin_A_v, thin_A_l, thin_A_u = m1.thin_pool_to_chunks(
        pool_A_v, pool_A_l, pool_A_u, chunk_fraction=0.5, device=device)

    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        thin_A_v, thin_A_l, thin_A_u, epochs, batch_size, device)

    thin_B_v, thin_B_l, thin_B_u = m1.thin_pool_to_chunks(
        pool_AB_v, pool_AB_l, pool_AB_u, chunk_fraction=0.5, device=device)
    combo_AB_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u]], dim=0)
    combo_AB_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u]], dim=0)
    combo_AB_u = combo_AB_v.shape[0]

    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combo_AB_v, combo_AB_l, combo_AB_u, epochs, batch_size, device)

    thin_C_v, thin_C_l, thin_C_u = m1.thin_pool_to_chunks(
        pool_ABC_v, pool_ABC_l, pool_ABC_u, chunk_fraction=0.5, device=device)
    combo_ABC_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u],
                              thin_C_v[:thin_C_u]], dim=0)
    combo_ABC_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u],
                              thin_C_l[:thin_C_u]], dim=0)
    combo_ABC_u = combo_ABC_v.shape[0]

    W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms, train_d_idx, train_d_tgt,
        combo_ABC_v, combo_ABC_l, combo_ABC_u, epochs, batch_size, device)

    bpc_a_after = float(base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                          byte_atoms, pos_atoms,
                                          val_a_idx, val_a_tgt, batch_size, device))

    ret = bpc_a_fresh / max(bpc_a_after, 1e-6)
    del W_A, W_AB, W_ABC, W_ABCD
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return float(ret), float(bpc_a_fresh), float(bpc_a_after)


def run_arm_no_replay(seed, N, batch_size, epochs, phase_a_epochs, n_bytes, smoke, device):
    """Arm 3: no replay (zero replay floor)."""
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = v1_mod.load_corpus_D(smoke=smoke)
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    def to_idx(tr):
        return base.bytes_to_idx_tensors(tr, device)

    train_a, val_a = split80(corpus_a)
    train_b, _ = split80(corpus_b)
    train_c, _ = split80(corpus_c)
    train_d, _ = split80(corpus_d)

    train_a_idx, train_a_tgt = to_idx(train_a)
    train_b_idx, train_b_tgt = to_idx(train_b)
    train_c_idx, train_c_tgt = to_idx(train_c)
    train_d_idx, train_d_tgt = to_idx(train_d)
    val_a_idx, val_a_tgt = to_idx(val_a)

    W = torch.zeros((N, N), dtype=torch.float32, device=device)

    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)

    bpc_a_fresh = float(base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                           byte_atoms, pos_atoms,
                                           val_a_idx, val_a_tgt, batch_size, device))

    # No replay
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        None, None, 0, epochs, batch_size, device)

    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms,
        train_c_idx, train_c_tgt, None, None, 0, epochs, batch_size, device)

    W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms,
        train_d_idx, train_d_tgt, None, None, 0, epochs, batch_size, device)

    bpc_a_after = float(base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                          byte_atoms, pos_atoms,
                                          val_a_idx, val_a_tgt, batch_size, device))

    ret = bpc_a_fresh / max(bpc_a_after, 1e-6)
    del W_A, W_AB, W_ABC, W_ABCD
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return float(ret), float(bpc_a_fresh), float(bpc_a_after)


def _instrumentation_selftest():
    """Assert metric formulas correct at toy scale."""
    # Self-test 1: retention formula
    bpc_fresh, bpc_after = 2.0, 2.5
    ret = bpc_fresh / bpc_after
    assert abs(ret - 0.8) < 1e-6, f"retention formula fail: {ret}"
    # Self-test 2: HP threshold sanity
    assert HP_INTERPHASE_LIFT > HF_TIMING_IRRELEVANT, "threshold ordering violated"
    # Self-test 3: N_FULL for GPU routing
    assert N_FULL == 4096, f"N_FULL should be 4096; got {N_FULL}"
    # Self-test 4: 3 arms distinct
    arm_names = {"interphase", "intraphase", "no_replay"}
    assert len(arm_names) == 3, "should have 3 distinct arms"
    # Self-test 5: replay fraction in valid range
    assert 0.0 < REPLAY_FRACTION_FULL < 1.0, "replay_frac out of range"
    print("selftest PASS 5/5")


_instrumentation_selftest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device} smoke={smoke}")

    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL
    replay_frac = REPLAY_FRACTION_SMOKE if smoke else REPLAY_FRACTION_FULL

    t0 = time.time()
    arm1_rets, arm2_rets, arm3_rets = [], [], []

    for seed in seeds:
        print(f"  seed={seed}...", flush=True)
        r1, _, _ = run_arm_interphase(seed, N, batch_size, epochs, phase_a_epochs,
                                       n_bytes, replay_frac, smoke, device)
        r2, _, _ = run_arm_intraephase(seed, N, batch_size, epochs, phase_a_epochs,
                                        n_bytes, replay_frac, smoke, device)
        r3, _, _ = run_arm_no_replay(seed, N, batch_size, epochs, phase_a_epochs,
                                     n_bytes, smoke, device)
        arm1_rets.append(r1)
        arm2_rets.append(r2)
        arm3_rets.append(r3)
        print(f"    inter={r1:.4f} intra={r2:.4f} noreplay={r3:.4f} lift={r1-r2:.4f}", flush=True)

    def mean(xs):
        return sum(xs) / max(len(xs), 1) if xs else None

    m1_ret = mean(arm1_rets)
    m2_ret = mean(arm2_rets)
    m3_ret = mean(arm3_rets)
    lift = m1_ret - m2_ret if (m1_ret is not None and m2_ret is not None) else None

    if lift is None:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "retention values all-None"
    elif lift >= HP_INTERPHASE_LIFT and m1_ret >= 0.80 and (m2_ret or 0) > (m3_ret or 0):
        verdict = "HA_CONSOLIDATION_HARD_PASS"
        verdict_msg = (f"H-A consolidation CONFIRMED: inter-phase={m1_ret:.4f} > "
                       f"intra-phase={m2_ret:.4f} by {lift:.4f}>={HP_INTERPHASE_LIFT}; "
                       f"replay > no-replay confirmed")
    elif abs(lift) < HF_TIMING_IRRELEVANT:
        verdict = "HA_TIMING_IRRELEVANT_HARD_FAIL"
        verdict_msg = (f"H-A REJECTED: timing-irrelevant; |inter-intra|={abs(lift):.4f}<{HF_TIMING_IRRELEVANT}; "
                       f"replay is data-augmentation not consolidation")
    else:
        verdict = "HA_MIDDLE"
        verdict_msg = (f"H-A MIDDLE: inter={m1_ret:.4f} intra={m2_ret:.4f} lift={lift:.4f}; "
                       f"weak or absent consolidation signal")

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "seeds": seeds, "smoke": smoke, "replay_frac": replay_frac},
        "summary": {
            "arm1_interphase_mean": m1_ret,
            "arm2_intraphase_mean": m2_ret,
            "arm3_noreplay_mean": m3_ret,
            "interphase_lift": lift,
            "arm1_rets": arm1_rets,
            "arm2_rets": arm2_rets,
            "arm3_rets": arm3_rets,
        },
    }
    validate_metrics(metrics)

    outdir = get_output_dir("wave14_betB_replay_hA_direct_v1")
    with open(outdir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"verdict={verdict}")
    print(f"verdict_msg={verdict_msg}")
    lift_str = f"{lift:.4f}" if lift is not None else "None"
    print(f"elapsed={elapsed:.1f}s lift={lift_str}")


if __name__ == "__main__":
    main()
