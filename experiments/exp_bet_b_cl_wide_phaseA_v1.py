"""Bet-B 4-stage CL architectural rescue C1: wider Phase A (N=8192) then project to N=4096.

CONTEXT:
  Training-axis rescues exhausted (epochs v3, batch_size v4, loss-weighting v5 -- all
  confirmed Stage-A sub-0.80 bar). v272 HARD_FAIL: architectural rescue is the only path.
  C1 tests: run Phase A at N=8192 (2x representational capacity), then project W_A to
  N=4096 for Phases B/C/D. Hypothesis: Phase-A retention bottleneck is storage-bound --
  the N=4096 W_A cannot store enough of corpus_A to sustain ret_A >= 0.80 after
  subsequent phase interference. N=8192 Phase A may encode corpus_A more robustly before
  the projection lossy-compresses back to N=4096.

ARCHITECTURAL CHANGE from v1/v2/v3:
  Phase A: N_A = 8192. byte_atoms and pos_atoms are N_A-dimensional.
           W_A is (N_A x N_A) after Phase A training.
  Projection: random Gaussian projection P of shape (N_B, N_A) = (4096, 8192).
    P is orthogonal-row (np.linalg.qr of Gaussian noise, first N_B rows).
    W_A_proj = P @ W_A @ P.T  (N_B x N_B)
    byte_atoms_proj = byte_atoms_A @ P.T  (rebind to N_B-dimensional codebook atoms)
    pos_atoms_proj = pos_atoms_A @ P.T
  Phases B/C/D: N_B = 4096. Normal 4-stage CL using W_A_proj as initial W.
  Retention metrics: same as v1 (bpc_A_after_D / bpc_A_baseline).

SCIENTIFIC QUESTION:
  Does a wider Phase A (N=8192) improve ret_A when projected to N=4096?
  If YES: capacity bottleneck is real; larger Phase-A representation survives projection.
  If NO: bottleneck is not storage-bound; architectural alternative needed.

PRE-REGISTERED BANDS:
  HARD_PASS: mean ret_A >= 0.80 AND mean ret_B >= 0.70 AND mean ret_C >= 0.70 (>= 3/3 seeds).
    Interpretation: wider Phase A rescues the ret_A ceiling.
  HARD_FAIL: mean ret_A <= 0.50 (worse than v1/v2; projection does active harm).
  MIDDLE_BAND: mean ret_A in (0.50, 0.80) -- same as v1 result range.
    -> If ret_A in (0.74, 0.80): slight improvement from v2 (0.745), still below threshold.
    -> If ret_A <= 0.60: projection degrades Phase-A retention further.

FORMULA SELF-TESTS:
  1. P @ P.T != I (P is not square; not orthogonal in general), but rows of P are unit vectors.
  2. W_A_proj = P @ W_A @ P.T: shape (N_B, N_B) when P is (N_B, N_A).
  3. byte_atoms_proj = byte_atoms_A @ P.T: shape (N_B, VOCAB) -- wait, wrong.
     byte_atoms is (VOCAB, N). Projection: byte_atoms_proj = byte_atoms_A @ P.T: shape (VOCAB, N_B). OK.
  4. retention = bpc_A_baseline / bpc_A_after_D. For perfect retention: ratio = 1.0.
  5. N_A = 8192 (PROT-018: no _nN suffix needed since N_A is the Phase A N; full N declared below).
  6. N_B = 4096 (Phases B/C/D dimensionality).

OOM CHECK:
  W_A at N_A=8192 float32 = 268MB. P at (4096, 8192) float32 = 128MB.
  W_A_proj = (4096, 4096) = 64MB. byte_atoms_A = (256, 8192) = 8MB. OK.
  Total peak: ~500MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  v3 (N=8192, 10 seeds) ~4080s. C1 has N_A=8192 phase + projection + N_B=4096 phases.
  Phase A cost ~ v3 Phase A cost: N=8192 Hebbian outer-product.
  Phases B/C/D cost ~ v1 (N=4096): much faster.
  Rough estimate: 1.5x v1 cost (N=8192 Phase A + N=4096 B/C/D).
  v1 5-seed GPU time ~ 1020s. C1 3-seed: 1020 * (3/5) * 1.5 = 918s.
  Safety: ceil(1.5 * 918) = 1377s. No _nN suffix in anchor name -> no PROT-019 floor.
  timeout_s = 1500s.

N-suffix: no _nN suffix (anchor uses two N values; PROT-018 inapplicable; see N declaration below).
N declaration: N_A = 8192 (Phase A), N_B = 4096 (Phases B/C/D). Explicitly stated: no _nN suffix.
Anchor: bet_b_cl_wide_phaseA_v1
Queue: overnight_queue (GPU; N_A=8192 Phase A + N_B=4096 B/C/D; 3 seeds)
Pre-reg: prereqs/2026-05-29_bet_b_cl_wide_phaseA_v1.md
Parent: bet_b_4stage_rehab_epochs_v3 (training-axis exhausted; C1 is architectural rescue)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load wave14_betB_4stage_continual_v1 for run infrastructure
_v1_path = REPO / "experiments" / "exp_wave14_betB_4stage_continual_v1.py"
_v1_spec = importlib.util.spec_from_file_location("betb4stage_c1", _v1_path)
v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1_mod)

# Load bet_b_n8192_4stage_v1 for N=8192 infrastructure
_n8k_path = REPO / "experiments" / "exp_bet_b_n8192_4stage_v1.py"
_n8k_spec = importlib.util.spec_from_file_location("bet_b_n8k_c1", _n8k_path)
n8k_mod = importlib.util.module_from_spec(_n8k_spec)
_n8k_spec.loader.exec_module(n8k_mod)

pa = n8k_mod.pa
base = n8k_mod.base
load_corpus_D = v1_mod.load_corpus_D
compute_verdict = v1_mod.compute_verdict

# PRODUCTION CONFIG
# N_A = 8192 (Phase A wider representation)
# N_B = 4096 (Phases B/C/D)
# No _nN anchor suffix (two-N design; PROT-018 inapplicable).
N_A_FULL  = 8192
N_B_FULL  = 4096
N_A_SMOKE = 2048
N_B_SMOKE = 1024

BATCH_SIZE_FULL  = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL      = 5
EPOCHS_SMOKE     = 1
PHASE_A_EPOCHS_FULL  = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL  = 200_000
BYTES_SMOKE = 50_000
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (same as v1/v2/v3)
PASS_RET_A = 0.80
PASS_RET_B = 0.70
PASS_RET_C = 0.70
FAIL_RET_A = 0.50


def get_output_dir(default_name: str = "bet_b_cl_wide_phaseA_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_projection_matrix(N_B: int, N_A: int, seed: int,
                             device: torch.device) -> torch.Tensor:
    """Random orthogonal projection P: (N_B, N_A).

    Rows of P are orthonormal (P @ P.T = I_NB).
    Use Gram-Schmidt on random Gaussian matrix.
    """
    gen = torch.Generator(device=device)
    gen.manual_seed(seed + 9999)
    G = torch.randn(N_A, N_B, generator=gen, device=device, dtype=torch.float32)
    # QR decomposition: Q has orthonormal columns (N_A x N_B)
    Q, _ = torch.linalg.qr(G)  # Q: (N_A, N_B)
    P = Q.T                     # (N_B, N_A)
    return P


def run_one_seed_wide_phaseA(seed: int, config: Dict,
                               device: torch.device) -> Dict:
    """Run 4-stage CL with wider Phase A at N_A then project to N_B for B/C/D."""
    N_A = config["N_A"]
    N_B = config["N_B"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    smoke = config.get("mode") == "smoke"

    gen = torch.Generator().manual_seed(seed)

    # Phase A: N_A-dimensional atoms
    byte_atoms_A = pa.make_bsc_atoms(base.VOCAB, N_A, gen).to(device)
    pos_atoms_A  = pa.make_bsc_atoms(base.K, N_A, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    train_a, test_a = corpus_a[:int(0.8 * len(corpus_a))], corpus_a[int(0.8 * len(corpus_a)):]
    train_a_idx, train_a_tgt = base.bytes_to_idx_tensors(train_a, device)
    test_a_idx, test_a_tgt = base.bytes_to_idx_tensors(test_a, device)

    # Phase A training at N_A
    W_zero_A = torch.zeros((N_A, N_A), dtype=torch.float32, device=device)
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero_A, None, None, 0,
        byte_atoms_A, pos_atoms_A,
        train_a_idx, train_a_tgt,
        None, None, 0,
        phase_a_epochs, batch_size, device)

    # Compute bpc_A_baseline at N_A
    bpc_A_baseline_NA = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                            byte_atoms_A, pos_atoms_A,
                                            test_a_idx, test_a_tgt, batch_size, device)

    # PROJECT: W_A (N_A x N_A) -> W_A_proj (N_B x N_B)
    # P: (N_B, N_A); W_A_proj = P @ W_A @ P.T
    P = make_projection_matrix(N_B, N_A, seed, device)
    W_A_proj = P @ W_A @ P.T   # (N_B, N_B)

    # Project atoms to N_B space
    # byte_atoms_A: (VOCAB, N_A) -> byte_atoms_B: (VOCAB, N_B) via @ P.T
    byte_atoms_B = byte_atoms_A @ P.T  # (VOCAB, N_B)
    pos_atoms_B  = pos_atoms_A  @ P.T  # (K, N_B)

    # Project Phase A pool to N_B space (pool_A_v: (pool_size, N_A))
    if pool_A_v is not None and pool_A_u > 0:
        pool_A_v_proj = pool_A_v[:pool_A_u] @ P.T   # (pool_A_u, N_B)
        pool_A_l_proj = pool_A_l[:pool_A_u]          # labels unchanged
        pool_A_u_proj = pool_A_u
        # Create correctly-sized pool tensors
        pool_size_B = pool_A_v_proj.shape[0]
        pool_A_v_b = torch.zeros((pool_size_B * 2, N_B), dtype=torch.float32, device=device)
        pool_A_v_b[:pool_size_B] = pool_A_v_proj
        pool_A_l_b = torch.zeros(pool_size_B * 2, dtype=torch.long, device=device)
        pool_A_l_b[:pool_size_B] = pool_A_l_proj
        pool_A_u_b = pool_size_B
    else:
        pool_size_B = 1
        pool_A_v_b = torch.zeros((pool_size_B, N_B), dtype=torch.float32, device=device)
        pool_A_l_b = torch.zeros(pool_size_B, dtype=torch.long, device=device)
        pool_A_u_b = 0

    # Evaluate bpc_A_baseline at N_B using projected W and atoms
    bpc_A_baseline = base.evaluate_bpc(W_A_proj, pool_A_v_b, pool_A_l_b, pool_A_u_b,
                                         byte_atoms_B, pos_atoms_B,
                                         test_a_idx, test_a_tgt, batch_size, device)

    # Phases B/C/D at N_B using normal 4-stage protocol
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = load_corpus_D(smoke=smoke)
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full

    def split(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    train_b, test_b = split(corpus_b)
    train_c, test_c = split(corpus_c)
    train_d, test_d = split(corpus_d)

    train_b_idx, train_b_tgt = base.bytes_to_idx_tensors(train_b, device)
    test_b_idx, test_b_tgt   = base.bytes_to_idx_tensors(test_b, device)
    train_c_idx, train_c_tgt = base.bytes_to_idx_tensors(train_c, device)
    test_c_idx, test_c_tgt   = base.bytes_to_idx_tensors(test_c, device)
    train_d_idx, train_d_tgt = base.bytes_to_idx_tensors(train_d, device)
    test_d_idx, test_d_tgt   = base.bytes_to_idx_tensors(test_d, device)

    # Phase B with A replay at N_B
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A_proj, pool_A_v_b.clone(), pool_A_l_b.clone(), pool_A_u_b,
        byte_atoms_B, pos_atoms_B,
        train_b_idx, train_b_tgt,
        pool_A_v_b, pool_A_l_b, pool_A_u_b,
        n_epochs, batch_size, device)
    bpc_B_baseline = base.evaluate_bpc(W_AB, pool_AB_v, pool_AB_l, pool_AB_u,
                                          byte_atoms_B, pos_atoms_B,
                                          test_b_idx, test_b_tgt, batch_size, device)

    # Phase C with A+B replay at N_B
    combined_AB_v = torch.cat([pool_A_v_b[:pool_A_u_b], pool_AB_v[:pool_AB_u]], dim=0)
    combined_AB_l = torch.cat([pool_A_l_b[:pool_A_u_b], pool_AB_l[:pool_AB_u]], dim=0)
    combined_AB_u = combined_AB_v.shape[0]
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms_B, pos_atoms_B,
        train_c_idx, train_c_tgt,
        combined_AB_v, combined_AB_l, combined_AB_u,
        n_epochs, batch_size, device)
    bpc_C_baseline = base.evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                          byte_atoms_B, pos_atoms_B,
                                          test_c_idx, test_c_tgt, batch_size, device)

    # Phase D with A+B+C replay at N_B
    combined_ABC_v = torch.cat([pool_A_v_b[:pool_A_u_b], pool_AB_v[:pool_AB_u],
                                  pool_ABC_v[:pool_ABC_u]], dim=0)
    combined_ABC_l = torch.cat([pool_A_l_b[:pool_A_u_b], pool_AB_l[:pool_AB_u],
                                  pool_ABC_l[:pool_ABC_u]], dim=0)
    combined_ABC_u = combined_ABC_v.shape[0]
    W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms_B, pos_atoms_B,
        train_d_idx, train_d_tgt,
        combined_ABC_v, combined_ABC_l, combined_ABC_u,
        n_epochs, batch_size, device)

    # Retention checks at N_B
    bpc_A_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                          byte_atoms_B, pos_atoms_B,
                                          test_a_idx, test_a_tgt, batch_size, device)
    bpc_B_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                          byte_atoms_B, pos_atoms_B,
                                          test_b_idx, test_b_tgt, batch_size, device)
    bpc_C_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                          byte_atoms_B, pos_atoms_B,
                                          test_c_idx, test_c_tgt, batch_size, device)

    retention_A = min(bpc_A_baseline / max(bpc_A_after_D, 1e-6), 1.0)
    retention_B = min(bpc_B_baseline / max(bpc_B_after_D, 1e-6), 1.0)
    retention_C = min(bpc_C_baseline / max(bpc_C_after_D, 1e-6), 1.0)

    return {
        "retention_A": retention_A, "retention_B": retention_B, "retention_C": retention_C,
        "bpc_A_baseline_NA": bpc_A_baseline_NA,  # before projection
        "bpc_A_baseline": bpc_A_baseline,         # after projection (N_B eval)
        "bpc_A_after_D": bpc_A_after_D,
        "bpc_B_baseline": bpc_B_baseline, "bpc_B_after_D": bpc_B_after_D,
        "bpc_C_baseline": bpc_C_baseline, "bpc_C_after_D": bpc_C_after_D,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Formula self-test 1: projection matrix
    device = torch.device("cpu")
    P = make_projection_matrix(4, 8, 42, device)
    assert P.shape == (4, 8), f"P shape: {P.shape}"
    # Rows should be approximately orthonormal
    gram = P @ P.T
    for i in range(4):
        for j in range(4):
            expected = 1.0 if i == j else 0.0
            assert abs(gram[i, j].item() - expected) < 1e-4, \
                f"P @ P.T not identity at ({i},{j}): {gram[i,j]:.5f}"

    # Formula self-test 2: W projection formula
    W_test = torch.randn(8, 8, device=device)
    P_test = make_projection_matrix(4, 8, 99, device)
    W_proj = P_test @ W_test @ P_test.T
    assert W_proj.shape == (4, 4), f"W_proj shape: {W_proj.shape}"

    # Formula self-test 3: compute_verdict gate
    assert callable(compute_verdict), "compute_verdict not callable"

    # Smoke run at tiny scale (N_A=256, N_B=128)
    config_smoke = {
        "mode": "smoke",
        "N_A": 256, "N_B": 128,
        "batch_size": 16, "epochs": 1, "phase_a_epochs": 1,
        "bytes_per_corpus": 5_000,
        "seeds": [17],
    }
    result = run_one_seed_wide_phaseA(17, config_smoke, device)
    assert "retention_A" in result, f"retention_A missing: {list(result.keys())}"
    ret_A = result["retention_A"]
    assert isinstance(ret_A, float) and 0.0 < ret_A <= 1.0, f"retention_A out of (0,1]: {ret_A}"

    # OOM check: N_A=8192 W matrix peak
    oom_bytes = 8192 * 8192 * 4  # W_A at N_A
    oom_bytes += (4096 * 8192 * 4)  # P matrix
    oom_bytes += (4096 * 4096 * 4)  # W_A_proj
    assert oom_bytes < 6e9, f"OOM pre-check: {oom_bytes:.2e} >= 6GB"

    print(f"[selftest] bet_b_cl_wide_phaseA_v1 PASS "
          f"N_A=256 N_B=128 smoke ret_A={ret_A:.4f} "
          f"P-orthogonality OK OOM={oom_bytes:.2e}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    config = {
        "mode": "smoke" if smoke else "full",
        "N_A": N_A_SMOKE if smoke else N_A_FULL,
        "N_B": N_B_SMOKE if smoke else N_B_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
    }
    exp_name = os.environ.get("HDLAB_EXP_NAME", "bet_b_cl_wide_phaseA_v1")
    print(f"[run] {exp_name} mode={config['mode']} N_A={config['N_A']} N_B={config['N_B']} "
          f"device={device}", flush=True)

    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed_wide_phaseA(seed, config, device)
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
        "verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
        "summary": summary, "config": config,
        "N_A": config["N_A"], "N_B": config["N_B"],
    }
    mpath = get_output_dir(exp_name) / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
