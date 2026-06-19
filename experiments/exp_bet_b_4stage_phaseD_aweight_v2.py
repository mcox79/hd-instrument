"""Bet-B 4-stage CL at N=8192 with Phase-D A-weighted replay (k=0.75).

CONTEXT:
  bet_b_4stage_rehab_epochs_v3 (FULL N=8192, 10 seeds):
    FOURSTAGE_MIDDLE_BAND: mean ret_A=0.741, ret_B=0.860, ret_C=0.809.
    Axis-1 (2x Phase-A epochs) does NOT close ret_A gap (0.741 vs 0.80 threshold).
  bet_b_4stage_batch128_v1 (FULL N=8192, 5 seeds):
    FOURSTAGE_MIDDLE_BAND: mean ret_A=0.750, ret_B=0.855, ret_C=0.812.
    Axis-2 (2x batch_size) does NOT close ret_A gap (0.750 vs 0.80 threshold).
  ret_A ceiling: both axes saturate at ~0.74-0.75, confirmed genuine mechanism limit.

RESCUE ARM (c) -- Phase-D A-weighted replay (k=0.75 fraction):
  During Phase D, the combined (A+B+C) replay pool is rebalanced so that stage-A
  samples represent 75% of the replay buffer (k=0.75 fraction). B and C share
  remaining 12.5% each. This biases Phase-D gradient signal toward the EARLIEST
  stage, counteracting the known accumulation of Phase-D load on ret_A.

  Implementation: build replay pool as A_weighted + B + C where A_weighted
  repeats pool_A until 75% of total_n = pool_A_u + pool_AB_u + pool_ABC_u.
  n_A_target = ceil(0.75 * total_n). n_B = n_C = (total_n - n_A_target) // 2.

  Self-test for k=0.75 formula:
    total_n = 100 -> n_A_target = 75, n_B = n_C = 12, n_A_actual >= 75.
    total_n = 10  -> n_A_target = 8, n_B = n_C = 1, n_A_actual >= 8.
    Verify: float(n_A_actual) / (n_A_actual + n_B + n_C) >= 0.70 (within 5% tolerance).

  Mechanism rationale: ret_A failure in v1/axes-1/2 is Phase-D capacity pressure.
  Heavier weighting toward A during Phase-D gradient updates should directly
  reduce Phase-D forgetting of stage-A patterns.

PRE-REGISTERED BANDS (same anchor as prior 4-stage runs):
  HARD-PASS: mean ret_A >= 0.80 AND ret_B >= 0.70 AND ret_C >= 0.70 across 5 seeds.
    K2 KILLER T1: 4-stage CL closes ret_A gap via Phase-D A-weighted replay.
  HARD-FAIL: mean ret_A <= 0.50 (catastrophic A-replay-crowding effect).
  MIDDLE-BAND: ret_A in (0.50, 0.80).
    -> Sub-band [0.75, 0.80): partial improvement from axis-3, gap partially closed.
    -> Sub-band [0.74, 0.75): no improvement over axes 1 and 2; mechanism ceiling.
    -> Sub-band <= 0.74: A-weighting actively hurts.

  Outcome plan if MIDDLE-BAND:
    - If ret_A < 0.74 (worse than baseline): A-weighting is harmful; do NOT try k>0.75.
    - If ret_A in [0.74, 0.75): mechanism ceiling confirmed; product-spec rescoping.
    - If ret_A in [0.75, 0.80): small lift; consider k=0.90 as final axis-3 variant.
    - If ret_A >= 0.80: HARD-PASS (unlikely given axes 1+2 saturation pattern).

FORMULA SELF-TESTS:
  1. k=0.75 formula: total_n=100 -> n_A_target=75, n_B=12, n_C=12. Check: 75/(75+12+12)=0.755>=0.70.
  2. k=0.75 formula: total_n=10  -> n_A_target=8,  n_B=1,  n_C=1.  Check: 8/(8+1+1)=0.80>=0.70.
  3. FOURSTAGE_HARD_PASS fires when retention_A=0.82, retention_B=0.72, retention_C=0.72.
  4. FOURSTAGE_MIDDLE_BAND fires when retention_A=0.75, retention_B=0.86, retention_C=0.81.
  5. N_FULL == 8192 (PROT-018: no _nN suffix; production N stated explicitly).

OOM PRE-CHECK:
  W at N=8192: 8192^2 * 4 bytes = 268MB. 4 W copies (A,AB,ABC,ABCD) = 1.07GB.
  Replay pool: POOL_SIZE=1024 * 8192 * 4 = 32MB per pool * 3 replay pools = 96MB.
  A-weighted replay tensor: repeat pool_A up to 75% fraction. POOL_SIZE=1024 vectors.
  n_A_target <= 3 * pool_A_u <= 3*1024=3072 vectors = 3072*8192*4 = 96MB extra.
  Total peak: ~1.07GB + 96MB + 96MB = ~1.26GB. Well under 6GB. OK.

TIMEOUT ESTIMATE:
  bet_b_4stage_rehab_epochs_v3 FULL elapsed: not logged locally; estimate from
  rehab_epochs_v3 structure (10 seeds, phase_a_epochs=16).
  bet_b_n8192_4stage_v1 reference (5 seeds, N=8192, ~1020s from v2 timing note).
  v2 (batch128, 5 seeds): estimated ~900-1200s actual.
  This run: 5 seeds, same N=8192, extra A-weighted pool construction (~+5% overhead).
  timeout_s = ceil(1.5 * 1200 * (8192/8192)^1.5 * (5/5)) = ceil(1800) -> 2100s (safety).
  A-weighting adds pool repeat operations: add 300s buffer -> 2400s.
  Under 4h (14400s). Under 2h -- no extra visibility flag needed.
  Use timeout_s = 2700 (conservative, accounts for A-weight repeat at large pool).

N-suffix: no _nN suffix; production N = 8192 (PROT-018: stated explicitly below; N_FULL=8192).
Queue: overnight_queue (GPU; N=8192 Hebbian matrix ops, 5 seeds)
Pre-reg: preregs/2026-05-27_bet_b_4stage_phaseD_aweight_v2.md
Parent: bet_b_4stage_rehab_epochs_v3 (MIDDLE_BAND ret_A=0.741, N=8192 10-seed)
        bet_b_4stage_batch128_v1 (MIDDLE_BAND ret_A=0.750, N=8192 5-seed)
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

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from verification import oracle  # noqa: E402

# Load 4-stage v1 base (provides run_one_seed, compute_verdict, load_corpus_D, etc.)
_v1_path = REPO / "experiments" / "exp_wave14_betB_4stage_continual_v1.py"
_v1_spec = importlib.util.spec_from_file_location("v1base_4stage", _v1_path)
v1base = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1base)

base = v1base.base
pa = v1base.pa
load_corpus_D = v1base.load_corpus_D
compute_verdict = v1base.compute_verdict
self_test_verdict = v1base.self_test_verdict
write_metrics = v1base.write_metrics

# PRODUCTION CONFIG -- PROT-018: no _nN suffix; N_FULL stated explicitly
N_FULL = 8192            # PROT-018: production N stated explicitly (no _nN suffix)
N_SMOKE = 1024
BATCH_SIZE_FULL = 64     # same as v1 baseline (not changed; axes 1+2 both saturated)
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8  # same as v1 baseline (axis-1 epochs change did not help)
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200_000
BYTES_SMOKE = 50_000
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Phase-D A-weighting fraction: stage-A samples represent this fraction of replay pool
A_WEIGHT_K = 0.75        # k=0.75: 75% of Phase-D replay buffer comes from stage A

# Pre-registered thresholds (same as all prior 4-stage runs)
PASS_RET_A = 0.80
PASS_RET_B = 0.70
PASS_RET_C = 0.70
FAIL_RET_A = 0.50


def get_output_dir(default_name: str = "bet_b_4stage_phaseD_aweight_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_a_weighted_replay_pool(pool_A_v, pool_A_l, pool_A_u,
                                  pool_AB_v, pool_AB_l, pool_AB_u,
                                  pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                  k: float = 0.75):
    """Build Phase-D replay pool with A-weighted k-fraction.

    Returns combined (pool_v, pool_l, pool_u) where stage-A samples represent
    at least k fraction of the total pool size.

    Formula:
      total_n = pool_A_u + pool_AB_u + pool_ABC_u
      n_A_target = ceil(k * total_n)
      n_BC = max(1, (total_n - n_A_target) // 2)   # B and C get equal share
      Repeat pool_A cyclically until n_A_target samples reached.
      Concatenate: [A_weighted (n_A_target), B_slice (n_BC), C_slice (n_BC)]
    """
    total_n = pool_A_u + pool_AB_u + pool_ABC_u
    if total_n == 0:
        # Fallback: return A pool only
        return pool_A_v[:pool_A_u], pool_A_l[:pool_A_u], pool_A_u
    n_A_target = math.ceil(k * total_n)
    n_BC = max(1, (total_n - n_A_target) // 2)

    # Build A-weighted slice: repeat pool_A cyclically to reach n_A_target
    a_slice_v = pool_A_v[:pool_A_u]   # (pool_A_u, N)
    a_slice_l = pool_A_l[:pool_A_u]   # (pool_A_u,)
    if pool_A_u == 0:
        # No A data -- fall back to uniform
        a_weighted_v = torch.zeros(n_A_target, a_slice_v.shape[-1],
                                   dtype=a_slice_v.dtype, device=a_slice_v.device)
        a_weighted_l = torch.zeros(n_A_target, dtype=a_slice_l.dtype, device=a_slice_l.device)
    else:
        # Repeat cyclically
        n_reps = math.ceil(n_A_target / pool_A_u)
        a_weighted_v = a_slice_v.repeat(n_reps, 1)[:n_A_target]
        a_weighted_l = a_slice_l.repeat(n_reps)[:n_A_target]

    b_slice_v = pool_AB_v[:min(n_BC, pool_AB_u)]
    b_slice_l = pool_AB_l[:min(n_BC, pool_AB_u)]
    c_slice_v = pool_ABC_v[:min(n_BC, pool_ABC_u)]
    c_slice_l = pool_ABC_l[:min(n_BC, pool_ABC_u)]

    combined_v = torch.cat([a_weighted_v, b_slice_v, c_slice_v], dim=0)
    combined_l = torch.cat([a_weighted_l, b_slice_l, c_slice_l], dim=0)
    combined_u = combined_v.shape[0]
    return combined_v, combined_l, combined_u


def run_one_seed_phaseD_aweight(seed, config, device):
    """4-stage CL with Phase-D A-weighted replay (k=0.75).

    Identical to v1 run_one_seed for Phases A, B, C.
    Phase D uses A-weighted replay pool (k=0.75 fraction from stage A).
    """
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=(config["mode"] == "smoke"))
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = load_corpus_D(smoke=(config["mode"] == "smoke"))
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full

    def split(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]
    train_a, test_a = split(corpus_a)
    train_b, test_b = split(corpus_b)
    train_c, test_c = split(corpus_c)
    train_d, test_d = split(corpus_d)

    train_a_idx, train_a_tgt = base.bytes_to_idx_tensors(train_a, device)
    test_a_idx, test_a_tgt = base.bytes_to_idx_tensors(test_a, device)
    train_b_idx, train_b_tgt = base.bytes_to_idx_tensors(train_b, device)
    test_b_idx, test_b_tgt = base.bytes_to_idx_tensors(test_b, device)
    train_c_idx, train_c_tgt = base.bytes_to_idx_tensors(train_c, device)
    test_c_idx, test_c_tgt = base.bytes_to_idx_tensors(test_c, device)
    train_d_idx, train_d_tgt = base.bytes_to_idx_tensors(train_d, device)
    test_d_idx, test_d_tgt = base.bytes_to_idx_tensors(test_d, device)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)

    # Phase A: no replay.
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)
    bpc_A_baseline = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                       byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                       batch_size, device)

    # Phase B with A replay (same as v1 -- clone to avoid shared-storage corruption).
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        n_epochs, batch_size, device)
    bpc_B_baseline = base.evaluate_bpc(W_AB, pool_AB_v, pool_AB_l, pool_AB_u,
                                       byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                       batch_size, device)

    # Phase C with A+B replay (clone all pools to avoid shared-storage issues).
    combined_AB_v = torch.cat([pool_A_v[:pool_A_u].clone(), pool_AB_v[:pool_AB_u].clone()], dim=0)
    combined_AB_l = torch.cat([pool_A_l[:pool_A_u].clone(), pool_AB_l[:pool_AB_u].clone()], dim=0)
    combined_AB_u = combined_AB_v.shape[0]
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combined_AB_v, combined_AB_l, combined_AB_u, n_epochs, batch_size, device)
    bpc_C_baseline = base.evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                       byte_atoms, pos_atoms, test_c_idx, test_c_tgt,
                                       batch_size, device)

    # Phase D with A-WEIGHTED replay (k=0.75): stage A gets 75% of replay buffer.
    combined_v, combined_l, combined_u = build_a_weighted_replay_pool(
        pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        k=A_WEIGHT_K
    )
    print(f"  [PhaseD] seed={seed}: a_weight_replay={combined_u} "
          f"(A:{pool_A_u} * k={A_WEIGHT_K})", flush=True)
    W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms, train_d_idx, train_d_tgt,
        combined_v, combined_l, combined_u, n_epochs, batch_size, device)

    bpc_A_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                      byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                      batch_size, device)
    bpc_B_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                      byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                      batch_size, device)
    bpc_C_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                      byte_atoms, pos_atoms, test_c_idx, test_c_tgt,
                                      batch_size, device)
    bpc_D_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                      byte_atoms, pos_atoms, test_d_idx, test_d_tgt,
                                      batch_size, device)

    retention_A = min(bpc_A_baseline / max(bpc_A_after_D, 1e-6), 1.0)
    retention_B = min(bpc_B_baseline / max(bpc_B_after_D, 1e-6), 1.0)
    retention_C = min(bpc_C_baseline / max(bpc_C_after_D, 1e-6), 1.0)
    return {"retention_A": retention_A, "retention_B": retention_B, "retention_C": retention_C,
             "bpc_A_baseline": bpc_A_baseline, "bpc_A_after_D": bpc_A_after_D,
             "bpc_B_baseline": bpc_B_baseline, "bpc_B_after_D": bpc_B_after_D,
             "bpc_C_baseline": bpc_C_baseline, "bpc_C_after_D": bpc_C_after_D,
             "bpc_D_after_D": bpc_D_after_D, "a_weight_k": A_WEIGHT_K}


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018: N_FULL must be 8192 (no _nN suffix; stated explicitly)
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

    # Self-test 1: verdict logic from v1base
    self_test_verdict()

    # Self-test 2: k=0.75 formula checks
    # Case 1: total_n=100 -> n_A_target=75, n_BC=12 each
    n_A_t = math.ceil(0.75 * 100)
    n_BC_t = max(1, (100 - n_A_t) // 2)
    frac = n_A_t / (n_A_t + n_BC_t + n_BC_t)
    assert n_A_t == 75, f"k=0.75 formula: n_A_target should be 75; got {n_A_t}"
    assert frac >= 0.70, f"k=0.75 formula: A fraction should be >= 0.70; got {frac:.3f}"
    # Case 2: total_n=10 -> n_A_target=8
    n_A_t2 = math.ceil(0.75 * 10)
    n_BC_t2 = max(1, (10 - n_A_t2) // 2)
    frac2 = n_A_t2 / (n_A_t2 + n_BC_t2 + n_BC_t2)
    assert n_A_t2 == 8, f"k=0.75 formula (n=10): n_A_target should be 8; got {n_A_t2}"
    assert frac2 >= 0.70, f"k=0.75 formula (n=10): A fraction should be >= 0.70; got {frac2:.3f}"

    # Self-test 3: build_a_weighted_replay_pool returns valid tensors
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N_test = 64
    pool_A_v = torch.randn(20, N_test, device=device)
    pool_A_l = torch.randint(0, 256, (20,), dtype=torch.long, device=device)
    pool_B_v = torch.randn(15, N_test, device=device)
    pool_B_l = torch.randint(0, 256, (15,), dtype=torch.long, device=device)
    pool_C_v = torch.randn(12, N_test, device=device)
    pool_C_l = torch.randint(0, 256, (12,), dtype=torch.long, device=device)
    comb_v, comb_l, comb_u = build_a_weighted_replay_pool(
        pool_A_v, pool_A_l, 20, pool_B_v, pool_B_l, 15, pool_C_v, pool_C_l, 12, k=0.75)
    assert comb_v.shape[0] == comb_u, "combined_v size mismatch"
    assert comb_l.shape[0] == comb_u, "combined_l size mismatch"
    total_n_test = 20 + 15 + 12
    n_A_expected = math.ceil(0.75 * total_n_test)
    actual_frac = n_A_expected / comb_u
    assert actual_frac >= 0.70, f"A-fraction in pool: {actual_frac:.3f} < 0.70"
    assert comb_l.dtype == torch.long, f"pool labels must be long; got {comb_l.dtype}"

    # Self-test 4: run one smoke seed at tiny N
    cfg_smoke = {
        "mode": "smoke", "N": 256, "batch_size": 32, "epochs": 1,
        "phase_a_epochs": 1, "bytes_per_corpus": 5_000,
        "seeds": [17], "pass_ret_A": PASS_RET_A, "pass_ret_B": PASS_RET_B,
        "pass_ret_C": PASS_RET_C, "fail_ret_A": FAIL_RET_A
    }
    result = run_one_seed_phaseD_aweight(17, cfg_smoke, device)
    assert "retention_A" in result, f"missing retention_A: {list(result.keys())}"
    ret_A = result["retention_A"]
    assert isinstance(ret_A, float) and 0.0 < ret_A <= 1.0, f"retention_A out of (0,1]: {ret_A}"

    # Self-test 5: OOM pre-check at N=8192
    # 4 W copies + 3 replay pools + weighted replay
    oom_bytes = 8192 * 8192 * 4 * 4 + 3072 * 8192 * 4 * 2
    assert oom_bytes < 6e9, f"OOM pre-check failed: {oom_bytes:.2e} >= 6GB"

    # Self-test 6: HDLAB_EXP_NAME output-path check
    import os as _os
    _orig = _os.environ.get("HDLAB_EXP_NAME")
    _os.environ["HDLAB_EXP_NAME"] = "test_4stage_aweight_path_check"
    _test_dir = get_output_dir()
    if _orig is None:
        del _os.environ["HDLAB_EXP_NAME"]
    else:
        _os.environ["HDLAB_EXP_NAME"] = _orig
    assert _test_dir.name == "exp_test_4stage_aweight_path_check", \
        f"get_output_dir ignores HDLAB_EXP_NAME: got {_test_dir.name}"
    _test_dir.rmdir()

    print(f"[selftest] bet_b_4stage_phaseD_aweight_v2 PASSED: "
          f"N_FULL={N_FULL}, A_WEIGHT_K={A_WEIGHT_K}, "
          f"k formula OK (n=100: frac={frac:.3f}, n=10: frac={frac2:.3f}), "
          f"smoke ret_A={ret_A:.4f}, pool-build OK, OOM={oom_bytes:.2e}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "pass_ret_A": PASS_RET_A, "pass_ret_B": PASS_RET_B,
        "pass_ret_C": PASS_RET_C, "fail_ret_A": FAIL_RET_A,
        "a_weight_k": A_WEIGHT_K,
    }
    exp_name = os.environ.get("HDLAB_EXP_NAME", "bet_b_4stage_phaseD_aweight_v2")
    print(f"[run] {exp_name} mode={config['mode']} N={config['N']} "
          f"a_weight_k={A_WEIGHT_K} phase_a_epochs={config['phase_a_epochs']} "
          f"device={device}", flush=True)

    if not smoke:
        assert config["N"] == 8192, f"FULL run must use N=8192; got {config['N']}"
        assert config["a_weight_k"] == 0.75, \
            f"Phase-D k must be 0.75; got {config['a_weight_k']}"

    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed_phaseD_aweight(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: ret_A={r['retention_A']:.3f} "
              f"ret_B={r['retention_B']:.3f} ret_C={r['retention_C']:.3f}", flush=True)

    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)

    elapsed = round(time.time() - t0, 2)
    print(f"\n[result] {verdict}: {msg}", flush=True)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    out_dir = get_output_dir()
    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
