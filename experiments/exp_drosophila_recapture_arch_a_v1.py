"""ARCH-A Drosophila-MB-sparse RECAPTURE: sparse-KEY / dense-VALUE / linear readout PRESERVED.

Tests whether sparse-key routing recaptures capacity in the substrate's LINEAR heteroassociative regime
(W = sum val key^T; argmax/sign readout), vs the substrate's TRUE-dense bipolar baseline (f_k=1.0).
Honest-recapture (prereg LOCK 2026-06-17): a HARD-FAIL is the load-bearing finding "sparse-key gives no gain
in the linear regime" (verdict HONEST_BOUNDED; row -> ARCH-B softmax next), NOT a forced pass. P_deflated 0.35.

prereg: preregs/2026-06-17_drosophila_recapture_ARCH_A_sparse_key_dense_value.md
recaptures: scorecard claim 1 (Drosophila MB sparse f=0.05; STEP-4 GENUINE OVER-CLAIM HARD_FAIL gap 0.004).
HDLAB_RUN_MODE: smoke (1 seed) | full (5 seeds). LAPTOP super-fast (N=1024).
"""
from __future__ import annotations
import json
import math
import os
import time
from pathlib import Path

import torch

N = 1024                                  # substrate-canonical small-N (matches claim's small-N regime; N=4096 confirm is a separate before-VALIDATED gate)
F_K = [0.05, 0.10, 0.20, 0.50, 1.00]      # active-fraction; 1.00 = TRUE-dense bipolar baseline (Skunkworks Ask-3); 0.05 = Drosophila op point
M_LIST = [512, 1024, 2048]                # load (N/2, N, 2N); HARD-PASS anchored at M=N=1024
ACC_THRESH = 0.90                         # exact-recall: cos(sign(recall), val) >= 0.90
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "smoke")
SEEDS = [7] if RUN_MODE == "smoke" else [7, 17, 23, 31, 41]
DEV = "cpu"
ANCHOR = "drosophila_recapture_arch_a_v1"
OUT = Path(__file__).resolve().parents[1] / "data" / ANCHOR


def _gen(seed: int) -> torch.Generator:
    return torch.Generator(device=DEV).manual_seed(seed)


def make_sparse_keys(M: int, n: int, f_k: float, g: torch.Generator) -> torch.Tensor:
    """(M,n) sparse BIPOLAR keys: k=round(f_k*n) active positions per key (random), each +/-1; rest 0."""
    k = max(1, round(f_k * n))
    keys = torch.zeros((M, n), dtype=torch.float32, device=DEV)
    signs = (torch.randint(0, 2, (M, k), generator=g, device=DEV).float() * 2 - 1)  # +/-1
    # per-row random k positions (argsort of random scores = random permutation; take first k)
    idx = torch.argsort(torch.rand((M, n), generator=g, device=DEV), dim=1)[:, :k]
    keys.scatter_(1, idx, signs)
    return keys


def make_dense_values(M: int, n: int, g: torch.Generator) -> torch.Tensor:
    """(M,n) DENSE bipolar values (+/-1) -- held dense to ISOLATE the sparse-KEY variable."""
    return (torch.randint(0, 2, (M, n), generator=g, device=DEV).float() * 2 - 1)


def exact_recall_acc(M: int, f_k: float, g: torch.Generator) -> float:
    """Store M (sparse-key, dense-val) pairs in linear W=sum val key^T; sign-readout; exact-recall fraction."""
    keys = make_sparse_keys(M, N, f_k, g)            # (M,N)
    vals = make_dense_values(M, N, g)                # (M,N)
    W = vals.t() @ keys                              # (N,N) linear outer-product store (PRESERVED)
    recalls = torch.sign(keys @ W.t())               # (M,N) recall_i = sign(W @ key_i)
    # cosine(sign(recall), val): val is +/-1 so |val|=sqrt(N); recall in {-1,0,1}
    dot = (recalls * vals).sum(dim=1)
    norm = recalls.norm(dim=1) * vals.norm(dim=1) + 1e-12
    cos = dot / norm
    return float((cos >= ACC_THRESH).float().mean().item())


def main() -> int:
    t0 = time.time()
    # grid[f_k][M] = mean exact-recall over seeds; also per-seed for the 5/5 HARD-PASS check
    grid = {f"{fk}": {} for fk in F_K}
    per_seed = {f"{fk}": {f"M{m}": [] for m in M_LIST} for fk in F_K}
    for s in SEEDS:
        for fk in F_K:
            for m in M_LIST:
                acc = exact_recall_acc(m, fk, _gen(s * 100003 + m * 7 + int(fk * 1000)))
                per_seed[f"{fk}"][f"M{m}"].append(acc)
    for fk in F_K:
        for m in M_LIST:
            v = per_seed[f"{fk}"][f"M{m}"]
            grid[f"{fk}"][f"M{m}"] = sum(v) / len(v)

    # PRIMARY band: M=1024, f_k=0.05 vs f_k=1.00 (TRUE-dense baseline)
    a_sparse = grid["0.05"]["M1024"]
    a_dense = grid["1.0"]["M1024"]
    delta = a_sparse - a_dense
    # monotone-or-flat guard across f_k at M=1024 (no degenerate single-point spike): acc should not be a lone spike at 0.05
    m1024 = [grid[f"{fk}"]["M1024"] for fk in F_K]   # ordered by increasing f_k
    spike = a_sparse > max(m1024[1:]) + 0.05         # 0.05 strictly above ALL denser points by >5pp = suspicious lone spike
    # per-seed 5/5 check for HARD-PASS
    seeds_pass = all(
        (per_seed["0.05"]["M1024"][i] - per_seed["1.0"]["M1024"][i]) >= 0.05
        for i in range(len(SEEDS))
    )

    if delta >= 0.05 and seeds_pass and not spike:
        verdict = "HARD_PASS"
        msg = (f"RECAPTURE: sparse-key f_k=0.05 exact-recall {a_sparse:.3f} >= dense f_k=1.0 {a_dense:.3f} "
               f"+5pp (delta={delta:+.3f}) {len(SEEDS)}/{len(SEEDS)} seeds at M={N}. N={N}; N=4096 confirm gate before VALIDATED.")
    elif delta <= -0.03:
        verdict = "HONEST_BOUNDED"
        msg = (f"sparse-key gives NO gain in the linear regime: f_k=0.05 {a_sparse:.3f} <= dense f_k=1.0 "
               f"{a_dense:.3f} -3pp (delta={delta:+.3f}) at M={N}. Row closes at bipolar-value end; recapture "
               f"needs a supra-linear selection step (ARCH-B softmax) per drill. Method/N-contingent (N={N}).")
    else:
        verdict = "MIDDLE_BAND"
        msg = (f"sparse-key NEUTRAL: f_k=0.05 {a_sparse:.3f} vs dense f_k=1.0 {a_dense:.3f} (delta={delta:+.3f}) "
               f"within [-3pp,+5pp] at M={N}; not a recapture; bounded.")

    metrics = {
        "anchor_name": ANCHOR,
        "verdict": verdict,
        "verdict_msg": msg,
        "headline": msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "N": N,
        "elapsed_s": round(time.time() - t0, 2),
        "grid_exact_recall": grid,
        "per_seed": per_seed,
        "primary": {"f_k_0.05_M1024": a_sparse, "f_k_1.0_M1024": a_dense, "delta": delta,
                    "seeds_pass_5pp": seeds_pass, "lone_spike_guard_tripped": bool(spike)},
        "prereg_bands": {"HARD_PASS": "acc(0.05,M1024) >= acc(1.0,M1024)+0.05 all-seeds + monotone",
                         "HARD_FAIL_HONEST_BOUNDED": "acc(0.05,M1024) <= acc(1.0,M1024)-0.03",
                         "MIDDLE": "between", "acc_thresh": ACC_THRESH},
        # Skunkworks framework refinement 1: auditable genuinely-different provenance
        "recapture_of": "scorecard_claim_1_drosophila_mb_sparse_f0.05 / EXP_substrate_drosophila_mb_sparse_single_modulator_v1 (HARD_FAIL gap 0.004)",
        "failing_config_avoided": "raw sparse-coding expecting bundle-capacity-gain through a LINEAR heteroassociative readout with NO encoder-threshold / supra-linear selection (STEP-4 mechanism); failing config made BOTH keys and values sparse-BINARY {0,1}",
        "method_delta": "sparsity on the KEY ONLY (TopK routing); VALUE held DENSE bipolar; keys sparse-BIPOLAR (+/-1, zero-mean) NOT sparse-binary; linear W=sum val key^T + sign readout PRESERVED. Tests sparse-as-ROUTING, not sparse-as-bundle-capacity.",
        "n_gate_before_validated": "N=1024 first decisive test; confirm at N=4096 (claim's original N; remote) before VALIDATED",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={RUN_MODE} seeds={len(SEEDS)} N={N} -> {verdict}")
    print(f"  primary M=1024: f_k=0.05={a_sparse:.3f} vs f_k=1.0(dense)={a_dense:.3f}  delta={delta:+.3f}")
    print(f"  grid (exact-recall) by f_k x M:")
    for fk in F_K:
        print(f"    f_k={fk}: " + "  ".join(f"M{m}={grid[str(fk)][f'M{m}']:.3f}" for m in M_LIST))
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
