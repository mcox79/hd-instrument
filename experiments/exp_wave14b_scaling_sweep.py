"""Wave 14.B M5: scaling verification at larger N.

For each N in {8192, 16384, 32768, 65536}, runs the bundle-size and K-size
sweeps. Uses CUDA only since CPU at N=65K would take hours.

The substrate's capacity is theoretically O(N^2). Empirical claim from
earlier sweeps at N=4096: 100% recovery up to B=128 and K=2048. This
experiment verifies the property holds (and finds the cliff) at production-
relevant N values.

Output goes to data/exp_wave14b_scaling_sweep/metrics.json with one
section per N.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
NUM_TRIALS = 50  # reduced from 100 since larger N is slower
NUM_RESTARTS = 8
MAX_ITER = 100
BETA_INIT = 1.0
BETA_MULT = 1.2
BETA_MAX = 20.0

N_VALUES = [8192, 16384, 32768, 65536]
BUNDLE_SIZES_DEFAULT = [2, 8, 32, 128]
K_FIXED_FOR_BSWEEP = 32
K_SIZES_DEFAULT = [32, 256, 2048]
B_FIXED_FOR_KSWEEP = 2


def _say(msg: str) -> None:
    print(msg, flush=True)


def build_codebook(gen, K, N):
    bits = torch.randint(0, 2, (K, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32).to(DEVICE)


def build_positions(gen, B, N):
    bits = torch.randint(0, 2, (B, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32).to(DEVICE)


def make_bundle(atoms, positions):
    return (atoms * positions).sum(dim=0)


def cleanup_hard(v, codebook):
    scores = codebook @ v
    idx = int(scores.argmax().item())
    return codebook[idx], idx


def cleanup_soft(v, codebook, beta, N):
    scores = (codebook @ v) / math.sqrt(N)
    weights = torch.softmax(beta * scores, dim=0)
    return weights @ codebook


def run_resonator(c, positions, codebook, K, N, gen):
    B = positions.shape[0]
    best_score = -float("inf")
    best_idx = [-1] * B
    for restart in range(NUM_RESTARTS):
        init_indices = torch.randint(0, K, (B,), generator=gen)
        atoms_hat = codebook[init_indices].clone()
        beta = BETA_INIT
        prev_atoms = atoms_hat.clone()
        for it in range(MAX_ITER):
            for s in range(B):
                contribution_others = (atoms_hat * positions).sum(dim=0) - atoms_hat[s] * positions[s]
                candidate = (c - contribution_others) * positions[s]
                atoms_hat[s] = cleanup_soft(candidate, codebook, beta, N)
            beta = min(beta * BETA_MULT, BETA_MAX)
            delta = float((atoms_hat - prev_atoms).abs().mean())
            if delta < 1e-6 and beta >= BETA_MAX:
                break
            prev_atoms = atoms_hat.clone()
        pred_idx = []
        for s in range(B):
            _, idx = cleanup_hard(atoms_hat[s], codebook)
            pred_idx.append(idx)
        pred_atoms = codebook[torch.tensor(pred_idx, device=DEVICE)]
        c_recon = make_bundle(pred_atoms, positions)
        score = float((c @ c_recon) / (c.norm() * c_recon.norm() + 1e-12))
        if score > best_score:
            best_score = score
            best_idx = pred_idx
    return best_idx


def sweep_B(B, K, N, codebook, positions, num_trials):
    fully_correct = 0
    for trial in range(num_trials):
        tg = torch.Generator(device='cpu').manual_seed(SEED + 20000 + B * 1000 + trial)
        true_indices = torch.randint(0, K, (B,), generator=tg).tolist()
        true_atoms = codebook[torch.tensor(true_indices, device=DEVICE)]
        c = make_bundle(true_atoms, positions)
        pred_indices = run_resonator(c, positions, codebook, K, N, tg)
        slot_correct = sum(1 for t, p in zip(true_indices, pred_indices) if t == p)
        if slot_correct == B:
            fully_correct += 1
    return fully_correct / num_trials


def main():
    _say(f"Wave 14.B M5 scaling sweep: N in {N_VALUES}")
    _say(f"  device={DEVICE}, trials={NUM_TRIALS}, restarts={NUM_RESTARTS}")

    all_results = []
    t_start = time.perf_counter()
    for N in N_VALUES:
        _say(f"\n========== N = {N} ==========")
        gen = torch.Generator(device='cpu').manual_seed(SEED + N)
        codebook_default = build_codebook(gen, K_FIXED_FOR_BSWEEP, N)
        # Bundle-size sweep at K=32
        _say(f"\nBundle-size sweep (K={K_FIXED_FOR_BSWEEP}):")
        _say(f"  {'B':>5} | {'recovery':>9} | {'elapsed':>9}")
        b_results = []
        for B in BUNDLE_SIZES_DEFAULT:
            positions = build_positions(gen, B, N)
            t0 = time.perf_counter()
            rate = sweep_B(B, K_FIXED_FOR_BSWEEP, N, codebook_default, positions, NUM_TRIALS)
            dt = time.perf_counter() - t0
            _say(f"  {B:>5} | {100*rate:>8.1f}% | {dt:>8.1f}s")
            b_results.append({"B": B, "K": K_FIXED_FOR_BSWEEP, "recovery": rate, "wall_s": dt})
        # K-size sweep at B=2
        _say(f"\nK-size sweep (B={B_FIXED_FOR_KSWEEP}):")
        _say(f"  {'K':>5} | {'recovery':>9} | {'elapsed':>9}")
        positions_b2 = build_positions(gen, B_FIXED_FOR_KSWEEP, N)
        k_results = []
        for K in K_SIZES_DEFAULT:
            K_gen = torch.Generator(device='cpu').manual_seed(SEED + N + K)
            codebook_k = build_codebook(K_gen, K, N)
            t0 = time.perf_counter()
            rate = sweep_B(B_FIXED_FOR_KSWEEP, K, N, codebook_k, positions_b2, NUM_TRIALS)
            dt = time.perf_counter() - t0
            _say(f"  {K:>5} | {100*rate:>8.1f}% | {dt:>8.1f}s")
            k_results.append({"K": K, "B": B_FIXED_FOR_KSWEEP, "recovery": rate, "wall_s": dt})
        all_results.append({"N": N, "bundle_sweep": b_results, "K_sweep": k_results,
                          "elapsed_total": time.perf_counter() - t_start})
        # Incremental save in case of crash
        out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_scaling_sweep"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "metrics.json").write_text(json.dumps(
            {"results_so_far": all_results, "elapsed_s": time.perf_counter() - t_start},
            indent=2, default=str))
        _say(f"  -> incremental save written")

    _say(f"\n========= FULL SUMMARY =========")
    for r in all_results:
        _say(f"  N={r['N']}:")
        for b in r["bundle_sweep"]:
            _say(f"    B={b['B']}: {100*b['recovery']:.1f}%")
        for k in r["K_sweep"]:
            _say(f"    K={k['K']}: {100*k['recovery']:.1f}%")
    _say(f"\nTotal wall: {(time.perf_counter() - t_start)/60:.1f} min")


if __name__ == "__main__":
    main()
