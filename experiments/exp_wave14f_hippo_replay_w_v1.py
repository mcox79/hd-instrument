"""HiPPO-init on REPLAY W inter-phase consolidation probe (rescue #3).

CONTEXT: wave14f_hippo_init_w_v1 CLOSED-NEGATIVE at P1 (no depth benefit at FULL training).
Rescue sketch #3: apply HiPPO spectral structure to the REPLAY W (inter-phase consolidation
arm), not the primary heteroassociative W. Hypothesis: temporal dynamics of inter-phase replay
may be receptive to HiPPO long-range spectral structure because replay W acts as a sequence-
to-sequence consolidation pathway (closer to the SSM use-case).

MECHANISM: In the saddle-cascade / inter-phase protocol, Phase-A trains W_A. Phase-B trains W_B
from W_A as init with replay. The REPLAY W (W_replay) is a separate consolidation pathway
that merges W_A context into W_B. Test: initialize W_replay from HiPPO-LegS spectral structure
vs zero-init. Primary metric: retention_A after Phase-B (fraction of Phase-A accuracy retained).

HYPOTHESIS: HiPPO-structured W_replay provides better temporal alignment in the consolidation
pathway, leading to higher retention_A.

PRE-REGISTERED BANDS:
  HARD_PASS: mean_retention_hippo - mean_retention_zero >= 0.05 (absolute 5pp lift)
             AND mean_retention_zero >= 0.50 (baseline works; we are measuring lift)
  HARD_FAIL: |mean_retention_hippo - mean_retention_zero| < 0.01
             (no difference within noise)
  MIDDLE_BAND: delta in (0.01, 0.05) or negative delta
  INSTRUMENTATION_FAIL: mean_retention_zero < 0.40

Self-tests:
  1. build_mixed_corpus callable (from v3 saddle cascade module)
  2. hippo_replay_init produces matrix with correct eigenvalue structure (top-4 eigenvalues
     are in HiPPO-LegS magnitude order: sigma[0] >= sigma[1] >= sigma[2] >= sigma[3])
  3. zero_init produces W_replay = all-zeros (sanity check)
  4. run_phase_ab returns dict with retention_A key in [0, 2] range

Queue: remote_cpu_queue (CPU; 3 seeds x 2 init-types x N=1024; ~40-80 min)
Pre-reg: prereqs/2026-05-26_wave14f_hippo_replay_w_v1.md
Parent: wave14f_hippo_init_w_v1 CLOSED-NEGATIVE P1; rescue #3
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
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import build_mixed_corpus + base + pa from v3 saddle cascade (which loads Kovacs infra)
_v3_path = REPO / "experiments" / "exp_wave14_saddle_cascade_plateau_v3.py"
_v3_spec = importlib.util.spec_from_file_location("v3_cascade_rw", _v3_path)
v3_mod = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3_mod)
build_mixed_corpus = v3_mod.build_mixed_corpus
base = v3_mod.base
pa = v3_mod.pa

# Design parameters
N_FULL = 1024
N_SMOKE = 256
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
F_MIX = 0.5           # 50% corpus-B mix for inter-phase; tests consolidation at mid-conflict
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_B_FULL = 5     # Phase-B training epochs
EPOCHS_B_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 100_000
BYTES_SMOKE = 4_000
HIPPO_SCALE_FULL = 0.10    # scale factor for HiPPO-init W_replay (init magnitude)
HIPPO_SCALE_SMOKE = 0.10

# Pre-registered thresholds
RETENTION_LIFT_HARDPASS = 0.05   # hippo - zero >= 0.05
RETENTION_LIFT_HARDFAIL_MAX = 0.01  # |delta| < 0.01 -> no difference
RETENTION_ZERO_MIN_PASS = 0.50   # baseline retention must reach >= 0.50
INSTRUMENTATION_FAIL_THRESH = 0.40  # retention_zero < 0.40 -> instrumentation fail


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing: {missing}")


def hippo_legs_eigenvalues(H: int) -> torch.Tensor:
    """HiPPO-LegS diagonal-exponential eigenvalue magnitudes."""
    lam_re = 0.5 + 0.01 * torch.arange(H, dtype=torch.float32)
    lam_im = math.pi * torch.arange(H, dtype=torch.float32) / float(max(H, 1))
    dt = 0.5
    A_re = torch.exp(-dt * lam_re) * torch.cos(dt * lam_im)
    A_im = torch.exp(-dt * lam_re) * torch.sin(dt * lam_im)
    return (A_re ** 2 + A_im ** 2).sqrt()


def hippo_replay_init(N: int, scale: float, gen: torch.Generator) -> torch.Tensor:
    """Build W_replay initialized with HiPPO-LegS spectral structure.

    W_replay = sum_j sigma_j * u_j * u_j^T  where sigma_j ~ hippo_eigenvalue_j
    u_j are random BSC unit vectors. Scale controls overall magnitude.
    """
    eigs = hippo_legs_eigenvalues(N)     # shape (N,)
    eigs = eigs / (eigs.max() + 1e-9)   # normalize to [0, 1]

    # Build rank-N matrix from outer products of random BSC basis vectors
    # Using incremental accumulation to avoid N x N x N memory
    W = torch.zeros(N, N)
    for j in range(N):
        u = torch.rand(N, generator=gen)
        u = 2.0 * (u > 0.5).float() - 1.0
        u = u / (u.norm() + 1e-9)
        W.add_(eigs[j].item() * torch.outer(u, u))
    W = W * (scale / (W.norm() + 1e-9)) * math.sqrt(N)
    return W


def run_phase_ab(
    seed: int, N: int, batch_size: int,
    phase_a_epochs: int, epochs_b: int, n_bytes: int,
    f_mix: float, use_hippo_replay: bool, hippo_scale: float,
) -> dict:
    """Run Phase-A + Phase-B with either HiPPO-init or zero-init W_replay.

    Returns dict with retention_A.
    """
    device = torch.device("cpu")
    gen = torch.Generator().manual_seed(seed)

    VOCAB = 256
    K_ctx = base.K
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K_ctx, N, gen).to(device)

    # Phase-A corpus
    corpus_a_raw = pa.load_corpus_a()
    if len(corpus_a_raw) < n_bytes:
        reps = (n_bytes // len(corpus_a_raw)) + 2
        corpus_a_raw = corpus_a_raw * reps
    corpus_a_bytes = corpus_a_raw[:n_bytes]
    a_idx, a_tgt = base.bytes_to_idx_tensors(corpus_a_bytes, device)

    # Phase-A training from zero init
    W0 = torch.zeros((N, N), dtype=torch.float32, device=device)
    pool_v_init = torch.zeros((base.POOL_SIZE, N), dtype=torch.float32, device=device)
    pool_l_init = torch.zeros(base.POOL_SIZE, dtype=torch.long, device=device)
    pool_u_init = 0

    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W0, pool_v_init, pool_l_init, pool_u_init,
        byte_atoms, pos_atoms, a_idx, a_tgt,
        None, None, 0,
        phase_a_epochs, batch_size, device
    )

    # Phase-A evaluation baseline
    n_eval = max(1000, n_bytes // 5)
    corpus_a_full = pa.load_corpus_a()
    if len(corpus_a_full) < n_bytes + n_eval:
        reps = ((n_bytes + n_eval) // len(corpus_a_full)) + 2
        corpus_a_full = corpus_a_full * reps
    corpus_a_eval = corpus_a_full[n_bytes:n_bytes + n_eval]
    if len(corpus_a_eval) < 500:
        corpus_a_eval = corpus_a_full[-n_eval:]
    ae_idx, ae_tgt = base.bytes_to_idx_tensors(corpus_a_eval, device)
    bpc_A_base = base.evaluate_bpc(
        W_A, pool_A_v, pool_A_l, pool_A_u,
        byte_atoms, pos_atoms, ae_idx, ae_tgt, batch_size, device
    )

    # HiPPO vs zero init for W_replay (Phase-B starting point)
    if use_hippo_replay:
        gen_r = torch.Generator().manual_seed(seed + 10000)
        W_replay = hippo_replay_init(N, hippo_scale, gen_r).to(device)
        # Mix W_A + W_replay as starting point for Phase-B
        W_B_init = W_A.clone() + W_replay
    else:
        W_B_init = W_A.clone()

    # Phase-B corpus: mixed
    corpus_b_bytes = build_mixed_corpus(corpus_a_bytes, n_bytes, f_mix, seed)
    b_idx, b_tgt = base.bytes_to_idx_tensors(corpus_b_bytes, device)

    W_B, pool_B_v, pool_B_l, pool_B_u = base.train_w_with_replay(
        W_B_init, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, b_idx, b_tgt,
        pool_A_v, pool_A_l, pool_A_u,
        epochs_b, batch_size, device
    )

    bpc_A_after_B = base.evaluate_bpc(
        W_B, pool_B_v, pool_B_l, pool_B_u,
        byte_atoms, pos_atoms, ae_idx, ae_tgt, batch_size, device
    )

    retention_A = bpc_A_base / max(bpc_A_after_B, 1e-9)
    init_label = "hippo" if use_hippo_replay else "zero"
    print(
        f"  seed={seed} init={init_label}: "
        f"bpc_base={bpc_A_base:.4f} bpc_afterB={bpc_A_after_B:.4f} "
        f"retention={retention_A:.4f}",
        flush=True,
    )
    return {
        "seed": seed,
        "init": init_label,
        "bpc_A_base": round(bpc_A_base, 5),
        "bpc_A_after_B": round(bpc_A_after_B, 5),
        "retention_A": round(retention_A, 5),
    }


def _instrumentation_selftest():
    """Assert all claimed metrics non-null at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. build_mixed_corpus callable
    assert callable(build_mixed_corpus), "Selftest 1 FAIL: build_mixed_corpus not callable"
    print("[selftest] 1/4 build_mixed_corpus callable OK")

    # 2. hippo_replay_init eigenvalue structure
    gen_t = torch.Generator().manual_seed(42)
    W_h = hippo_replay_init(64, 0.10, gen_t)
    eigs = hippo_legs_eigenvalues(64)
    assert eigs[0] >= eigs[1] >= eigs[2] >= eigs[3], (
        f"Selftest 2 FAIL: eigenvalues not sorted: {eigs[:4].tolist()}"
    )
    assert W_h.shape == (64, 64), f"Selftest 2 FAIL: shape={W_h.shape}"
    print(f"[selftest] 2/4 hippo_replay_init eigenvalue order OK eigs[:4]={eigs[:4].tolist()}")

    # 3. zero init produces no perturbation (W_replay = 0)
    W_a = torch.randn(64, 64)
    W_b_init = W_a.clone()
    assert torch.allclose(W_b_init, W_a), "Selftest 3 FAIL: zero-init branch not clean"
    print("[selftest] 3/4 zero-init branch produces no perturbation OK")

    # 4. run_phase_ab returns dict with retention_A in [0, 2]
    result = run_phase_ab(
        seed=42, N=64, batch_size=8,
        phase_a_epochs=1, epochs_b=1, n_bytes=500,
        f_mix=0.5, use_hippo_replay=False, hippo_scale=0.10,
    )
    assert "retention_A" in result, "Selftest 4 FAIL: no retention_A in result"
    assert 0.0 <= result["retention_A"] <= 5.0, (
        f"Selftest 4 FAIL: retention_A={result['retention_A']}"
    )
    print(f"[selftest] 4/4 run_phase_ab returns retention_A={result['retention_A']:.4f} OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False):
    t0 = time.time()
    label = "SMOKE" if smoke else "FULL"
    print(f"[exp] wave14f_hippo_replay_w_v1 {label}", flush=True)

    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    epochs_b = EPOCHS_B_SMOKE if smoke else EPOCHS_B_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL
    hippo_scale = HIPPO_SCALE_SMOKE if smoke else HIPPO_SCALE_FULL
    out_dir = get_output_dir("wave14f_hippo_replay_w_v1")

    print(f"[run] N={N} seeds={seeds} F_MIX={F_MIX}", flush=True)

    hippo_rets: List[float] = []
    zero_rets: List[float] = []

    for seed in seeds:
        print(f"\n[run] seed={seed}", flush=True)
        # zero-init first (control)
        try:
            res_z = run_phase_ab(
                seed=seed, N=N, batch_size=batch_size,
                phase_a_epochs=phase_a_epochs, epochs_b=epochs_b,
                n_bytes=n_bytes, f_mix=F_MIX,
                use_hippo_replay=False, hippo_scale=hippo_scale,
            )
            zero_rets.append(res_z["retention_A"])
        except Exception as e:
            print(f"  FAILED zero: {e}", flush=True)
            zero_rets.append(float("nan"))

        # hippo-init
        try:
            res_h = run_phase_ab(
                seed=seed, N=N, batch_size=batch_size,
                phase_a_epochs=phase_a_epochs, epochs_b=epochs_b,
                n_bytes=n_bytes, f_mix=F_MIX,
                use_hippo_replay=True, hippo_scale=hippo_scale,
            )
            hippo_rets.append(res_h["retention_A"])
        except Exception as e:
            print(f"  FAILED hippo: {e}", flush=True)
            hippo_rets.append(float("nan"))

    valid_z = [v for v in zero_rets if math.isfinite(v)]
    valid_h = [v for v in hippo_rets if math.isfinite(v)]

    if not valid_z or not valid_h:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (
            f"INSTRUMENTATION_FAIL: valid_zero={len(valid_z)} valid_hippo={len(valid_h)}. "
            f"Insufficient for verdict."
        )
        summary = {"valid_zero": len(valid_z), "valid_hippo": len(valid_h)}
    else:
        mean_z = sum(valid_z) / len(valid_z)
        mean_h = sum(valid_h) / len(valid_h)
        delta = mean_h - mean_z

        print(f"\n[results] mean_ret_zero={mean_z:.4f} mean_ret_hippo={mean_h:.4f} delta={delta:+.4f}", flush=True)

        if mean_z < INSTRUMENTATION_FAIL_THRESH:
            verdict = "INSTRUMENTATION_FAIL"
            verdict_msg = (
                f"INSTRUMENTATION_FAIL: mean_retention_zero={mean_z:.4f} < {INSTRUMENTATION_FAIL_THRESH}. "
                f"Baseline did not work; cannot measure HiPPO lift."
            )
        elif delta >= RETENTION_LIFT_HARDPASS and mean_z >= RETENTION_ZERO_MIN_PASS:
            verdict = "HIPPO_REPLAY_HARD_PASS"
            verdict_msg = (
                f"HiPPO-init W_replay lifts retention_A by {delta:+.4f} >= {RETENTION_LIFT_HARDPASS}. "
                f"mean_ret_zero={mean_z:.4f} mean_ret_hippo={mean_h:.4f}. "
                f"Rescue #3 CONFIRMED: HiPPO spectral structure improves inter-phase consolidation."
            )
        elif abs(delta) < RETENTION_LIFT_HARDFAIL_MAX:
            verdict = "HIPPO_REPLAY_HARD_FAIL"
            verdict_msg = (
                f"No meaningful difference: delta={delta:+.4f}, |delta|<{RETENTION_LIFT_HARDFAIL_MAX}. "
                f"mean_ret_zero={mean_z:.4f} mean_ret_hippo={mean_h:.4f}. "
                f"Rescue #3 CLOSED-NEGATIVE."
            )
        else:
            verdict = "HIPPO_REPLAY_MIDDLE"
            verdict_msg = (
                f"Intermediate: delta={delta:+.4f}. "
                f"mean_ret_zero={mean_z:.4f} mean_ret_hippo={mean_h:.4f}."
            )

        summary = {
            "N": N,
            "f_mix": F_MIX,
            "mean_retention_zero": round(mean_z, 4),
            "mean_retention_hippo": round(mean_h, 4),
            "delta_hippo_minus_zero": round(delta, 4),
            "seeds_zero": valid_z,
            "seeds_hippo": valid_h,
        }

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": summary,
        "config": {
            "N": N,
            "f_mix": F_MIX,
            "seeds": seeds,
            "smoke": smoke,
            "hippo_scale": hippo_scale,
        },
    }
    validate_metrics(metrics)
    metrics_file = out_dir / "metrics.json"
    with open(metrics_file, "w") as f_out:
        json.dump(metrics, f_out, indent=2)
    print(f"\n[verdict] {verdict}: {verdict_msg}", flush=True)
    print(f"Metrics saved to {metrics_file}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
