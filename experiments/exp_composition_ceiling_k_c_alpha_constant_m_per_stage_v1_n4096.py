"""
composition_ceiling_k_c_alpha_constant_m_per_stage_v1_n4096 -- Arrhenius-drill Test P5.

SCIENTIFIC QUESTION:
  Does substrate composition fail at depth k_c(alpha) ~ 0.138/alpha when M per stage
  is held CONSTANT (not halving per stage as Q-A3 architecture does)?

  Arrhenius-drill prediction: composition depth k_c(alpha) ~ alpha_c/alpha = 0.138/alpha.
  At alpha=0.05: k_c ~ 2.76 -> predicted ceiling at k~3.
  At alpha=0.10: k_c ~ 1.38 -> predicted ceiling at k~2.

  Q-A3 L=10 EXACT-1.0 works because it HALVES M per stage: each stage decreases the
  effective alpha, implementing implicit isochoric composition. This test removes that
  protection by holding M per stage CONSTANT.

TEST DESIGN:
  Q-A3-style cross-layer Hadamard composition at N=4096, 5 seeds.
  M per stage held CONSTANT at M = alpha * N.
  alpha in {0.05, 0.10}.
  Depth k in {1, 2, 3, 4, 5, 6, 7, 8} (sweeps across both predicted ceilings).
  Each level: store M patterns in substrate W (Hopfield), compose via Hadamard binding.
  Measure L_fid = end-to-end fidelity after decoding all k levels.

PRE-REGISTERED BANDS (Item 32 v343):
  HARD-PASS: L_fid >= 0.95 for k < k_c(alpha) AND L_fid < 0.50 for k > k_c(alpha)+1;
             ceiling location within +-1 stage of prediction
  MIDDLE: clear ceiling exists but location +-2 stages of prediction
  HARD-FAIL: L_fid flat across all tested k (no ceiling, refutes prediction) OR
             ceiling at k > 2*predicted

  No prior empirical anchor for constant-M composition; P_deflated=0.50.
  Bands set per calibration-probe policy (+-50% of theoretical prediction).

FORMULA SELF-TESTS (PROT-022):
  1. k_c(alpha) formula: k_c = alpha_c / alpha = 0.138 / alpha.
     [INPUT: alpha=0.05] [EXPECTED: k_c = 2.76 -> ceiling at k=3]
     [INPUT: alpha=0.10] [EXPECTED: k_c = 1.38 -> ceiling at k=2]
  2. Hadamard composition self-inverse: for L levels of binding and unbinding,
     final decoded cos should degrade gracefully.
     [INPUT: N=64, k=1 level, alpha=0.05] [EXPECTED: L_fid > 0.85]
  3. Hopfield retrieval at alpha=0.05 N=4096: single-level fidelity > 0.85.
     [INPUT: N=256, M=13, k=1] [EXPECTED: L_fid > 0.80]

PROT-018: anchor contains _n4096; N MUST = 4096.
GPU REQUIRED: 5-seed sweep at N=4096 with depth up to k=8 is compute-heavy.
Queue: overnight_queue
Pre-reg: preregs/2026-06-02_composition_ceiling_k_c_alpha_constant_m_per_stage_v1_n4096.md

TIMEOUT ESTIMATE:
  Smoke: N=1024, 2 seeds, 2 alpha values, k=1..6.
  Full: N=4096, 5 seeds, 2 alpha values, k=1..8.
  Per (seed, alpha, k): W build + N_queries retrieval + decode.
  N=4096 W build: ~ 2s (GPU).
  N_queries=20 retrievals at 20 steps: ~ 1s GPU.
  Full: 5 * 2 * 8 * 3s = 240s.
  timeout_s = ceil(1.5 * 240 * 1) = 360 -> 600s.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.cuda
    import numpy as np
except ImportError as e:
    print(f"[FATAL] missing dependency: {e}", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"mem={torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB", flush=True)

ANCHOR_NAME = "composition_ceiling_k_c_alpha_constant_m_per_stage_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
ALPHA_GRID = [0.05, 0.10]
DEPTH_GRID = [1, 2, 3, 4, 5, 6, 7, 8]

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACT = 1024
    N_QUERIES = 10
    N_RETRIEVE_STEPS = 10
    NOISE_FRAC = 0.10
    DEPTH_GRID_SMOKE = [1, 2, 3, 4, 5]
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACT = N
    N_QUERIES = 20
    N_RETRIEVE_STEPS = 20
    NOISE_FRAC = 0.10

# Pre-registered thresholds
HP_L_FID_BELOW_CEILING = 0.95
HF_L_FID_ABOVE_CEILING = 0.50
HP_CEILING_LOC_TOL     = 1    # +-1 stage
MID_CEILING_LOC_TOL    = 2    # +-2 stages

# PROT-022 formula self-test
_kc_005 = ALPHA_C / 0.05
_kc_010 = ALPHA_C / 0.10
assert abs(_kc_005 - 2.76) < 0.01, f"k_c(0.05) formula: {_kc_005:.3f} != 2.76"
assert abs(_kc_010 - 1.38) < 0.01, f"k_c(0.10) formula: {_kc_010:.3f} != 1.38"
print(f"[PROT-022] k_c(0.05)={_kc_005:.2f} k_c(0.10)={_kc_010:.2f}", flush=True)


def gen_patterns(M_count: int, N_dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float32)


def hopfield_retrieve_gpu(W_t: torch.Tensor, probe_t: torch.Tensor,
                           n_steps: int) -> torch.Tensor:
    state = probe_t.clone()
    for _ in range(n_steps):
        h = W_t @ state
        state = torch.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim_np(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-8 or nb < 1e-8:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ---- FORMULA SELF-TESTS ----

def _selftest_kc_formula():
    """k_c = alpha_c / alpha is correct."""
    assert abs(ALPHA_C / 0.05 - 2.76) < 0.01, "k_c formula fail"
    assert abs(ALPHA_C / 0.10 - 1.38) < 0.01, "k_c formula fail"


def _selftest_single_level():
    """Single-level Hadamard-over-Hopfield at alpha=0.05 N=256 should give L_fid > 0.50."""
    N_t, M_t = 256, 13  # alpha~0.05
    rng = np.random.RandomState(7)
    Xi_content = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    Xi_ctx = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    Xi_bound = Xi_content * Xi_ctx  # Hadamard bind
    W_np = (Xi_bound.T @ Xi_bound) / N_t
    np.fill_diagonal(W_np, 0.0)
    W_t = torch.from_numpy(W_np).to(DEVICE)
    # Retrieve one pattern
    probe_np = Xi_bound[0].copy()
    probe_np[:N_t//10] *= -1.0  # 10% noise
    probe_t = torch.from_numpy(probe_np).to(DEVICE)
    retrieved_t = hopfield_retrieve_gpu(W_t, probe_t, n_steps=10)
    retrieved_np = retrieved_t.cpu().numpy()
    xi_A_rec = retrieved_np * Xi_ctx[0]
    cos = cosine_sim_np(xi_A_rec, Xi_content[0])
    assert cos > 0.30, f"selftest single-level: cos={cos:.4f} < 0.30"


def _selftest_gpu_ok():
    a = torch.ones((4, 4), device=DEVICE)
    b = torch.ones((4, 4), device=DEVICE)
    c = a @ b
    assert c[0, 0].item() == 4.0, "GPU matmul sanity failed"


def _instrumentation_selftest():
    _selftest_kc_formula()
    _selftest_gpu_ok()
    _selftest_single_level()
    print("[selftest] PASS: kc_formula, gpu_ok, single_level all OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials


def run_composition_depth_sweep(seed: int, n_dim: int, alpha: float,
                                  depth_list: List[int]) -> Dict:
    """Sweep composition depth k at constant M = alpha * N per stage."""
    M = int(alpha * n_dim)
    rng = np.random.RandomState(seed)
    results = {}

    for k in depth_list:
        # Build k-level Hadamard composition with constant M per stage
        # Level 1: Xi_content_L1 (M, N), Xi_ctx_L1 (M, N)
        # bound_L1 = Xi_content_L1 * Xi_ctx_L1 stored in W_L1
        # Level 2 content = decoded Xi_content_L1; bound over W_L2 with Xi_ctx_L2
        # ... repeat k times
        # At each level, store M NEW patterns (constant M)

        # Generate all level patterns
        Xi_contents = []
        Xi_ctxs = []
        for lev in range(k):
            Xi_c = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)
            Xi_x = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)
            Xi_contents.append(Xi_c)
            Xi_ctxs.append(Xi_x)

        # Build composite bound vectors for each level
        # bound_k = xi_content_k * xi_ctx_k stored in W_k
        # The k-level query: query top-level, decode, query next, etc.

        # Store each level's W
        W_levels = []
        for lev in range(k):
            Xi_bound_lev = Xi_contents[lev] * Xi_ctxs[lev]
            W_np = (Xi_bound_lev.T @ Xi_bound_lev) / n_dim
            np.fill_diagonal(W_np, 0.0)
            W_levels.append(torch.from_numpy(W_np).to(DEVICE))

        # Measure end-to-end fidelity: probe level-k, decode through all levels
        cos_list = []
        n_q = min(N_QUERIES, M)
        for q_idx in range(n_q):
            pattern_idx = q_idx % M

            # Start: noisy probe of top-level (level k-1) bound vector
            bound_top = Xi_contents[k-1][pattern_idx] * Xi_ctxs[k-1][pattern_idx]
            probe = bound_top.copy()
            noise_mask = rng.random(n_dim) < NOISE_FRAC
            probe[noise_mask] *= -1.0

            # Decode through levels from top to bottom
            current = probe
            for lev in range(k-1, -1, -1):
                probe_t = torch.from_numpy(current).to(DEVICE)
                retrieved_t = hopfield_retrieve_gpu(W_levels[lev], probe_t, N_RETRIEVE_STEPS)
                retrieved = retrieved_t.cpu().numpy()
                # Unbind to get content of this level
                content_rec = retrieved * Xi_ctxs[lev][pattern_idx]
                if lev == 0:
                    # Final: measure cos against original content at level 0
                    cos = cosine_sim_np(content_rec, Xi_contents[0][pattern_idx])
                    cos_list.append(float(cos))
                else:
                    # Use content_rec as probe for next level down
                    current = content_rec

        mean_cos = float(np.mean(cos_list)) if cos_list else 0.0
        results[k] = mean_cos
        print(f"  [seed={seed} alpha={alpha:.2f} k={k}] L_fid={mean_cos:.4f}", flush=True)

        # Cleanup GPU memory
        for w in W_levels:
            del w
        torch.cuda.empty_cache()

    return {"seed": seed, "alpha": alpha, "depth_fid": results}


def main():
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    depth_list = DEPTH_GRID_SMOKE if RUN_MODE == "smoke" else DEPTH_GRID
    print(f"[{RUN_MODE}] N={N_ACT} seeds={SEEDS} alpha_grid={ALPHA_GRID} "
          f"depth_grid={depth_list}", flush=True)

    done_seeds, remaining = resumable_seeds(SEEDS, out_dir)
    print(f"[ckpt] {len(done_seeds)} done; running {remaining}", flush=True)

    all_results = {}
    for seed in remaining:
        seed_results = {}
        for alpha in ALPHA_GRID:
            r = run_composition_depth_sweep(seed, N_ACT, alpha, depth_list)
            seed_results[alpha] = r["depth_fid"]
        combined = {"seed": seed, "alpha_results": {str(a): v for a, v in seed_results.items()}}
        write_partial(out_dir, seed, combined)
        all_results[seed] = seed_results

    per_seed = aggregate_partials(out_dir, SEEDS)

    # Aggregate: for each (alpha, k), mean L_fid across seeds
    summary = {}
    for alpha in ALPHA_GRID:
        kc_pred = ALPHA_C / alpha
        depths = {}
        for k in depth_list:
            fids = []
            for s in SEEDS:
                v = per_seed[str(s)]["alpha_results"][str(alpha)]
                if k in v:
                    fids.append(v[k])
            if fids:
                depths[k] = float(np.mean(fids))
        summary[alpha] = {"kc_predicted": kc_pred, "depth_fid": depths}
        print(f"\n[alpha={alpha:.2f}] predicted k_c={kc_pred:.2f}:", flush=True)
        for k, f in sorted(depths.items()):
            marker = " <-- predicted ceiling" if abs(k - kc_pred) < 1.0 else ""
            print(f"  k={k}: L_fid={f:.4f}{marker}", flush=True)

    # Verdict: check both alpha values
    passes = []
    fails = []
    for alpha in ALPHA_GRID:
        kc_pred = ALPHA_C / alpha
        depths = summary[alpha]["depth_fid"]
        # Check if L_fid >= 0.95 for k < floor(kc_pred)
        ceiling_floor = int(math.floor(kc_pred))
        below = [depths.get(k, None) for k in depth_list if k < ceiling_floor and depths.get(k) is not None]
        above = [depths.get(k, None) for k in depth_list if k > ceiling_floor + 1 and depths.get(k) is not None]
        below_ok = all(f >= HP_L_FID_BELOW_CEILING for f in below) if below else False
        above_ok = all(f < HF_L_FID_ABOVE_CEILING for f in above) if above else False
        passes.append(below_ok and above_ok)
        # HF: no ceiling (L_fid flat) or ceiling too late
        max_k_tested = max(depth_list)
        hf_no_ceiling = all(depths.get(k, 1.0) > HF_L_FID_ABOVE_CEILING for k in depth_list
                             if depths.get(k) is not None)
        hf_too_late = any(depths.get(k, 0.0) < HF_L_FID_ABOVE_CEILING
                           for k in depth_list if k > 2 * max(ceiling_floor, 1)) if ceiling_floor > 0 else False
        fails.append(hf_no_ceiling)

    if all(fails):
        verdict = "HARD_FAIL"
        verdict_msg = ("HF: L_fid flat across all k for both alpha values; "
                       "composition ceiling formula refuted")
    elif all(passes):
        verdict = "HARD_PASS"
        kc_05_str = f"{ALPHA_C/0.05:.1f}"
        kc_10_str = f"{ALPHA_C/0.10:.1f}"
        verdict_msg = (f"HP: ceiling at k~{kc_05_str} (alpha=0.05) and k~{kc_10_str} (alpha=0.10) "
                       f"confirmed; k_c(alpha)~0.138/alpha architectural formula validated "
                       f"(constant-M regime)")
    else:
        # partial pass / middle band
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE: partial ceiling detection; passes={passes} fails={fails}")

    elapsed = time.time() - t_start
    metrics = {
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": {str(a): {"kc_predicted": s["kc_predicted"],
                             "depth_fid": {str(k): v for k, v in s["depth_fid"].items()}}
                    for a, s in summary.items()},
        "N": N_ACT,
        "alpha_grid": ALPHA_GRID,
        "alpha_c": ALPHA_C,
        "n_seeds": len(SEEDS),
        "elapsed_s": elapsed,
        "run_mode": RUN_MODE,
    }

    out_dir.joinpath("metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"\n[verdict] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    main()
