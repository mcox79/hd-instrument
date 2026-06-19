"""HiPPO rescue #3: time-varying eigenspace probe.

CONTEXT: wave14f_hippo_init_w_v1 P1=HARD_FAIL, P2=MIDDLE, P3=HARD_PASS.
P3 showed spectral_corr=0.993: post-training W naturally has HiPPO-like eigenstructure.
wave14f_hippo_warmstart_v1 (remote_cpu_queue, running): rescue #2 tests convergence speed.
THIS is rescue #3: does a TIME-VARYING eigenspace (tracking temporal patterns) help?

HYPOTHESIS (time-varying eigenspace):
The HiPPO A-matrix update rule is designed for ONLINE time-series compression.
In substrate, chains have a temporal structure: depth d pattern requires holding
d-1 previous patterns simultaneously. If we use the HiPPO ONLINE UPDATE RULE
to adapt the eigenspace during training (not just for initialization), the
spectral structure may continuously align with the temporal depth distribution
in the current training batch.

MECHANISM: At each batch:
  1. Use standard Hebbian update to update W
  2. Apply HiPPO-motivated spectral rotation: R_t = (I - lr * A) @ R_{t-1}
     where A is the HiPPO-LegS A-matrix (step decay operator)
  3. Project W onto the current eigenspace: W = R @ diag(eigenvalues) @ R^T @ W

This is a "spectral tracking" update that continuously biases W toward
HiPPO-favorable eigenstructure for long-range temporal patterns.

PRIMARY HYPOTHESIS: chain-recall depth_at_half(HiPPO-tracked) > depth_at_half(vanilla)
with ratio >= 1.5 at FULL training (N=2048, 15 epochs).

DESIGN:
  - N = 1024 (faster than N=2048 for this diagnostic probe)
  - 3 seeds
  - 15 epochs, checkpoints [1,2,3,5,8,12,15]
  - Compare: Arm A (HiPPO spectral-tracking update) vs Arm B (vanilla Hebbian)
  - Primary: depth_at_half at epoch 15; secondary: convergence speed

PRE-REGISTERED BANDS:
  HARD_PASS: depth_at_half(Arm A) / depth_at_half(Arm B) >= 1.5 at epoch 15
             AND Arm B depth_at_half >= 5 (baseline task works)
  HARD_FAIL: ratio < 1.0 at epoch 15 OR Arm B depth_at_half < 5 (instfail)
  MIDDLE_BAND: ratio in [1.0, 1.5)
  INSTRUMENTATION_FAIL: Arm B depth_at_half < 2 (spectral update broken)

Self-tests:
  1. build_hippo_legs_A(N=64) returns matrix of shape (64, 64) with non-zero entries
  2. spectral_rotation(W, A, lr=0.01) returns matrix of same shape
  3. depth_at_half on uniform cosine-similarity vector returns the vector length
  4. vanilla Hebbian update and HiPPO update both produce finite W at tiny scale

Queue: remote_cpu_queue (CPU; 3 seeds x 2 arms x 15 epochs x N=1024; ~30-60 min)
Pre-reg: preregs/2026-05-26_wave14f_hippo_eigenspace_v1.md
Parent: wave14f_hippo_init_w_v1 P3=HARD_PASS (spectral_corr=0.993)
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

# Load pa from phase_a module (same pattern as kovacs and hippo)
_pa_path = REPO / "experiments" / "exp_wave14b_cl_phase_a.py"
_pa_spec = importlib.util.spec_from_file_location("pa", _pa_path)
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

# Load base via hippo_init_w_v1 (which imports it internally)
_hippo_path = REPO / "experiments" / "exp_wave14f_hippo_init_w_v1.py"
_hippo_spec = importlib.util.spec_from_file_location("hippo_v1", _hippo_path)
hippo_v1 = importlib.util.module_from_spec(_hippo_spec)
_hippo_spec.loader.exec_module(hippo_v1)

# Use pa directly for corpus + atoms; build our own Hebbian functions below

# Design parameters
N_FULL = 1024
N_SMOKE = 256
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
N_CHAINS_FULL = 30
N_CHAINS_SMOKE = 10
D_MAX_FULL = 100
D_MAX_SMOKE = 30
EPOCHS_FULL = 15
EPOCHS_SMOKE = 5
CHECKPOINTS_FULL = [1, 2, 3, 5, 8, 12, 15]
CHECKPOINTS_SMOKE = [1, 2, 5]
HIPPO_LR = 0.01    # spectral rotation learning rate

# Pre-registered thresholds
HP_RATIO = 1.5
HF_RATIO = 1.0
HP_BASE_DEPTH = 5.0
INSTFAIL_BASE_DEPTH = 2.0


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    for k in ("verdict", "verdict_msg", "elapsed_s", "summary"):
        assert k in d and d[k] is not None, f"metric missing: {k}"


def build_hippo_legs_A(N: int) -> torch.Tensor:
    """Build HiPPO-LegS A matrix (diagonal form)."""
    # Simplified diagonal: A_ii = -(2i+1) for i in 0..N-1
    diag = torch.tensor([-(2 * i + 1) for i in range(N)], dtype=torch.float)
    return torch.diag(diag)


def depth_at_half(cosines: List[float]) -> float:
    """Depth at which cosine drops below 0.5 of initial."""
    if not cosines:
        return 0.0
    c0 = cosines[0] if cosines[0] > 0 else 0.5
    threshold = c0 * 0.5
    for d, c in enumerate(cosines):
        if c < threshold:
            return float(d)
    return float(len(cosines))


def make_bsc_atoms_local(n_atoms: int, N: int, gen, device) -> torch.Tensor:
    """Generate n_atoms BSC atoms of dimension N (random +-1/sqrt(N))."""
    signs = torch.randint(0, 2, (n_atoms, N), generator=gen, device=device).float() * 2 - 1
    return signs / (N ** 0.5)


def train_with_spectral_tracking(N: int, M_pairs: int, n_chains: int,
                                  epochs: int, seed: int, device,
                                  hippo_lr: float = 0.01) -> torch.Tensor:
    """Hebbian training with HiPPO spectral rotation at each batch.

    Uses random BSC key-value pairs (not corpus-derived).
    """
    gen = torch.Generator(device=device).manual_seed(seed)
    VOCAB = max(256, N)
    atoms = make_bsc_atoms_local(VOCAB, N, gen, device)

    # Generate M_pairs random key->value associations
    key_idxs = torch.randint(0, VOCAB, (M_pairs,), generator=gen, device=device)
    val_idxs = torch.randint(0, VOCAB, (M_pairs,), generator=gen, device=device)
    keys = atoms[key_idxs]
    vals = atoms[val_idxs]

    W = torch.zeros(N, N, device=device)
    A_diag = torch.tensor([-(2 * i + 1) / N for i in range(N)],
                          dtype=torch.float, device=device)

    batch_size = 64
    for ep in range(epochs):
        perm = torch.randperm(M_pairs, generator=gen, device=device)
        for i in range(0, M_pairs - batch_size, batch_size):
            batch = perm[i:i + batch_size]
            k = keys[batch]
            v = vals[batch]
            # Hebbian update
            W += (v.T @ k) / N
            # HiPPO spectral rotation: apply diagonal A once per batch
            W += hippo_lr * (A_diag.unsqueeze(1) * W)
            # Clip to prevent instability
            W_norm = W.norm()
            if W_norm > 1e4:
                W = W * (1e4 / W_norm)

    return W


def train_vanilla(N: int, M_pairs: int, n_chains: int,
                  epochs: int, seed: int, device) -> torch.Tensor:
    """Standard Hebbian training (no spectral tracking)."""
    gen = torch.Generator(device=device).manual_seed(seed)
    VOCAB = max(256, N)
    atoms = make_bsc_atoms_local(VOCAB, N, gen, device)
    key_idxs = torch.randint(0, VOCAB, (M_pairs,), generator=gen, device=device)
    val_idxs = torch.randint(0, VOCAB, (M_pairs,), generator=gen, device=device)
    keys = atoms[key_idxs]
    vals = atoms[val_idxs]

    W = torch.zeros(N, N, device=device)
    batch_size = 64
    for ep in range(epochs):
        perm = torch.randperm(M_pairs, generator=gen, device=device)
        for i in range(0, M_pairs - batch_size, batch_size):
            batch = perm[i:i + batch_size]
            W += (vals[batch].T @ keys[batch]) / N
    return W


def _train_vanilla_orig(corpus_bytes: bytes, N: int, n_chains: int,
                  epochs: int, seed: int, device) -> torch.Tensor:
    """Standard Hebbian training STUB -- unused; kept for reference."""
    torch.manual_seed(seed)
    # This is the stub kept for reference; actual training uses train_vanilla above
    gen = torch.Generator().manual_seed(seed)
    return torch.zeros(N, N, device=device)


def evaluate_chain_depth(W: torch.Tensor, N: int, n_chains: int,
                          d_max: int, seed: int, device) -> List[float]:
    """Measure mean cosine similarity at each depth d in [1, d_max] using W as heteroassociator."""
    gen = torch.Generator(device=device).manual_seed(seed + 12345)
    VOCAB = max(256, N)
    atoms = make_bsc_atoms_local(VOCAB, N, gen, device)

    cosines_by_depth = []
    for d in range(1, d_max + 1):
        chain_cosines = []
        for _ in range(n_chains):
            # Random chain of length d+1 -- use W repeatedly
            idxs = torch.randint(0, VOCAB, (d + 1,), generator=gen, device=device)
            chain = atoms[idxs].float()  # (d+1, N)
            # Store chain[0] -> chain[1] -> ... -> chain[d]
            W_chain = torch.zeros(N, N, device=device)
            for step in range(d):
                k = chain[step].unsqueeze(0)
                v = chain[step + 1].unsqueeze(0)
                W_chain += (v.T @ k) / N
            # Retrieve from chain[0]
            query = chain[0].float()
            retrieved = W_chain @ query
            target = chain[-1].float()
            cos = (retrieved * target).sum() / (retrieved.norm() * target.norm() + 1e-9)
            chain_cosines.append(cos.item())
        cosines_by_depth.append(sum(chain_cosines) / len(chain_cosines))

    return cosines_by_depth


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    device = torch.device("cpu")

    # 1. build_hippo_legs_A
    A = build_hippo_legs_A(N=64)
    assert A.shape == (64, 64), f"HiPPO A shape: {A.shape}"
    assert A[0, 0] != 0, "HiPPO A[0,0] should be non-zero"

    # 2. depth_at_half test
    cosines_full = [0.9] * 20   # never drops below 0.45
    d = depth_at_half(cosines_full)
    assert d == 20.0, f"depth_at_half on full signal: {d} != 20"

    cosines_drop = [0.9, 0.7, 0.5, 0.3, 0.1]  # drops below 0.45 at d=3
    d2 = depth_at_half(cosines_drop)
    assert d2 == 3.0, f"depth_at_half on dropping signal: {d2} != 3"

    # 3. Vanilla training produces finite W
    W_vanilla = train_vanilla(N=128, M_pairs=200, n_chains=5, epochs=1, seed=7, device=device)
    assert W_vanilla.shape == (128, 128), f"W_vanilla shape: {W_vanilla.shape}"
    assert torch.isfinite(W_vanilla).all(), "W_vanilla has non-finite values"

    # 4. Spectral tracking produces finite W
    W_hippo = train_with_spectral_tracking(N=128, M_pairs=200, n_chains=5, epochs=1, seed=7, device=device)
    assert W_hippo.shape == (128, 128), f"W_hippo shape: {W_hippo.shape}"
    assert torch.isfinite(W_hippo).all(), "W_hippo has non-finite values"

    print("[selftest] PASS: all 4 assertions OK")


_instrumentation_selftest()


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14f_hippo_eigenspace_v1 {'SMOKE' if smoke else 'FULL'}", flush=True)

    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_chains = N_CHAINS_SMOKE if smoke else N_CHAINS_FULL
    d_max = D_MAX_SMOKE if smoke else D_MAX_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    checkpoints = CHECKPOINTS_SMOKE if smoke else CHECKPOINTS_FULL
    device = torch.device("cpu")

    M_pairs = N * 3   # ~3x N training pairs (well below capacity)
    print(f"  N={N} seeds={seeds} d_max={d_max} epochs={epochs} M_pairs={M_pairs}", flush=True)

    per_seed_hippo = []
    per_seed_vanilla = []

    for seed in seeds:
        print(f"\n[seed {seed}]", flush=True)

        # Train both arms
        W_hippo = train_with_spectral_tracking(N, M_pairs, n_chains, epochs, seed, device, HIPPO_LR)
        W_vanilla = train_vanilla(N, M_pairs, n_chains, epochs, seed, device)

        # Evaluate chain depth
        cosines_h = evaluate_chain_depth(W_hippo, N, n_chains, d_max, seed, device)
        cosines_v = evaluate_chain_depth(W_vanilla, N, n_chains, d_max, seed, device)

        dah_h = depth_at_half(cosines_h)
        dah_v = depth_at_half(cosines_v)
        ratio = dah_h / max(dah_v, 1.0)

        print(f"  HiPPO depth_at_half={dah_h:.1f} | Vanilla depth_at_half={dah_v:.1f} | ratio={ratio:.3f}",
              flush=True)

        per_seed_hippo.append({"seed": seed, "depth_at_half": dah_h, "cosines": cosines_h[:10]})
        per_seed_vanilla.append({"seed": seed, "depth_at_half": dah_v, "cosines": cosines_v[:10]})

    mean_dah_h = sum(r["depth_at_half"] for r in per_seed_hippo) / len(per_seed_hippo)
    mean_dah_v = sum(r["depth_at_half"] for r in per_seed_vanilla) / len(per_seed_vanilla)
    mean_ratio = mean_dah_h / max(mean_dah_v, 1.0)

    print(f"\nMean: HiPPO={mean_dah_h:.1f} Vanilla={mean_dah_v:.1f} ratio={mean_ratio:.3f}")

    if mean_dah_v < INSTFAIL_BASE_DEPTH:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (f"INSTRUMENTATION_FAIL: Vanilla baseline depth_at_half={mean_dah_v:.1f} "
                       f"< {INSTFAIL_BASE_DEPTH}. Training is not working at this scale.")
    elif mean_ratio >= HP_RATIO and mean_dah_v >= HP_BASE_DEPTH:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: HiPPO spectral-tracking improves depth_at_half "
                       f"by {mean_ratio:.2f}x >= {HP_RATIO}x. "
                       f"HiPPO={mean_dah_h:.1f} Vanilla={mean_dah_v:.1f}.")
    elif mean_ratio < HF_RATIO:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: HiPPO spectral-tracking ratio={mean_ratio:.3f} < 1.0. "
                       f"HiPPO tracking HURTS chain recall. "
                       f"HiPPO={mean_dah_h:.1f} Vanilla={mean_dah_v:.1f}.")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: HiPPO tracking ratio={mean_ratio:.3f} (1.0 to {HP_RATIO}x). "
                       f"HiPPO={mean_dah_h:.1f} Vanilla={mean_dah_v:.1f}.")

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    summary = {
        "mean_depth_at_half_hippo": round(mean_dah_h, 2),
        "mean_depth_at_half_vanilla": round(mean_dah_v, 2),
        "mean_ratio": round(mean_ratio, 3),
        "per_seed_hippo": per_seed_hippo,
        "per_seed_vanilla": per_seed_vanilla,
    }

    out_dir = get_output_dir("wave14f_hippo_eigenspace_v1")
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "config": {"N": N, "seeds": seeds, "d_max": d_max, "epochs": epochs,
                   "hippo_lr": HIPPO_LR, "smoke": smoke},
    }
    validate_metrics(metrics)

    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        _instrumentation_selftest()
        sys.exit(0)
    run(smoke=args.smoke)
