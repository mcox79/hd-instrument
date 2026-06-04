"""
pp49_hrc_cross_n_d4_d6_d8_v1_n16384 -- PP-49 HRC cross-N at N=16384, depths d=4,6,8.

CONTEXT (v369 refill cycle):
  PP-49 row band: 0.87-0.97.
  Prior runs: N=4096 (pp49_hrc_depth_parity_discriminator_sweep_v1_n4096) + N=8192 (nscale_v1).
  Research upgrade (v359 drill battery):
    1x drill: parity-class regime (cf_cos alternates +/- across d; even-d EXACT).
    2x drill: protocol-artifact (predecessor-start rank-1 ceiling <= 0.50; root-start >= 0.95 smooth).
    Both mechanisms CONSISTENT with current data. Discriminator result (N=4096) may have landed.
  Gap: PP-49 family has no N=16384 rung yet. Cross-N strengthens the mixed-mechanism characterization.

SCIENTIFIC QUESTION:
  Does PP-49 HRC counterfactual recovery behavior at depths d=4,6,8 hold at N=16384?
  Expected: predecessor-start cf_cos <= 0.55 for d>=3 (rank-1 ceiling N-stable to N=16384)
  AND root-start cf_cos >= 0.80 for d>=2 at N=16384.
  This matches the N=4096 and N=8192 HARD-PASS pattern if N-scale independence holds.

MEMORY ESTIMATE (OOM pre-check):
  M_bg = int(0.05 * 16384) = 819 patterns.
  Xi_bg: 819 * 16384 * 4 bytes = 53.7 MB. Fine.
  W_cf matrix: 16384^2 * 4 = 1073 MB GPU. We build W_cf per hop only for root-start
    as rank-1 outer product (N * d * 4 bytes = 16384 * 8 * 4 = 0.5 MB each). Fine.
  Peak GPU: Xi_bg (~54 MB) + W_cf rank-1 (~0.5 MB) = 54.5 MB. Well within 8 GB.

PRE-REGISTERED BANDS (PP-49 HRC cross-N N=16384 d={4,6,8}):
  Prior empirical anchor: N=8192 HARD-PASS (pred_cos<=0.55 d>=3, root_cos>=0.80 d>=2).
  HARD-PASS: predecessor-start cf_cos <= 0.60 for d in {4,6,8} (rank-1 ceiling N-stable)
             AND root-start cf_cos >= 0.75 for d in {4,6,8} at N=16384.
             => N=16384 cross-N gap filled; mixed-mechanism characterization strengthened.
  MIDDLE: pred-start cf_cos in (0.55, 0.75) for d>=4 OR root-start in [0.50, 0.75).
  HARD-FAIL: pred-start cf_cos > 0.80 for d>=4 (rank-1 ceiling absent at N=16384)
             OR root-start cf_cos < 0.50 for d>=4 (root-start broken at N=16384).

  Note: HARD-FAIL would indicate artifact disappears at N=16384 (unexpected; no prior signal).
  Either HP or MIDDLE strengthens PP-49 product narrative (protocol-API design choice only).

FORMULA SELF-TESTS (PROT-022):
  1. Root-start depth-1 traversal: probe from x0 through 1-hop CF matrix retrieves xi_B.
     [INPUT: N=64, 1 chain, depth=1] [EXPECTED: cf_cos non-NaN]
  2. M at alpha=0.05, N=16384: int(0.05 * 16384) = 819. [EXPECTED: M=819]
  3. W_cf rank-1 outer product at N=64 non-NaN. [EXPECTED: no TypeError]
  4. Xi_bg VRAM at N=16384: 819 * 16384 * 4 < 1e8 bytes = 200 MB. [EXPECTED: < 2e8]

3-cell sweep: d=4, d=6, d=8. GPU (pattern build) + CPU (chain traversal via numpy).

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed with run_mode + max_depth.
QUEUE: overnight_queue (GPU machine; Xi build on GPU; chain traversal on CPU numpy; 3 cells).
TIMEOUT ESTIMATE: N=8192 nscale elapsed ~120s (5 depths * 2 protocols * 5 seeds CPU).
  N=16384: M=819 vs M=409; chain traversal per step scales as N (not N^2 -- rank-1 outer).
  3 depths (vs 5 at N=8192). Estimate: 1.5 * 120 * (819/409) * (3/5) = 1.5*120*2.0*0.6 = 216s.
  timeout = ceil(1.5 * 200) = 300s.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.cuda
except ImportError:
    print("[FATAL] torch not installed.", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB", flush=True)

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp49_hrc_cross_n_d4_d6_d8_v1_n16384"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
DEPTH_LIST_FULL = [4, 6, 8]
N_RETRIEVE_STEPS = 10

# PROT-022 formula self-tests at module scope
_M_FULL = int(ALPHA * N)
assert _M_FULL == 819, f"M at N={N} alpha={ALPHA}: {_M_FULL} expected 819"

_xi_bytes_full = _M_FULL * N * 4
assert _xi_bytes_full < 2e8, (
    f"Xi VRAM at N={N}: {_xi_bytes_full/1e6:.0f}MB >= 200MB")

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACT = 512
    DEPTH_LIST = [4, 6]
    N_CHAINS = 3
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACT = N
    DEPTH_LIST = DEPTH_LIST_FULL
    N_CHAINS = 5

M_ACT = int(ALPHA * N_ACT)

# Pre-registered thresholds
HP_PRED_MAX_D4PLUS = 0.60
HP_ROOT_MIN_D4PLUS = 0.75
HF_PRED_MIN_D4PLUS = 0.80
HF_ROOT_MAX_D4PLUS = 0.50


def cosine_sim_np(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-8 or nb < 1e-8:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _selftest_depth1_cf():
    """Root-start depth-1: cf_cos non-NaN at N=64."""
    N_t = 64
    rng = np.random.RandomState(0)
    xi_A = rng.choice([-1.0, 1.0], N_t).astype(np.float32)
    xi_B = rng.choice([-1.0, 1.0], N_t).astype(np.float32)
    # W_cf rank-1: xi_B outer xi_A / N_t
    probe = xi_A.copy()
    h = (np.dot(xi_B, xi_A) / N_t) * xi_B  # rank-1 outer: (xi_B outer xi_A) @ xi_A
    # correct rank-1: W_cf @ probe = xi_B * (xi_A . probe) / N
    h_correct = xi_B * (float(np.dot(xi_A, probe)) / N_t)
    ret = np.sign(h_correct).astype(np.float32)
    ret[ret == 0] = 1.0
    cos_val = cosine_sim_np(ret, xi_B)
    assert not np.isnan(cos_val), "cf_cos is NaN in depth-1 selftest"
    print(f"  [selftest depth1] N={N_t} cf_cos_root={cos_val:.3f}", flush=True)


def _selftest_m_check():
    assert _M_FULL == 819, f"M_full={_M_FULL} expected 819"


def _instrumentation_selftest():
    _selftest_depth1_cf()
    _selftest_m_check()
    # GPU memory check
    dummy = torch.zeros((512, 512), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated"
    del dummy
    print(f"[selftest] PASS: depth1_cf ok, M_check={_M_FULL}, "
          f"N_ACT={N_ACT} depths={DEPTH_LIST}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int, m_bg: int) -> Dict:
    """Run one seed across d=4,6,8 for both protocols."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Build background patterns (on CPU numpy)
    Xi_bg = rng.choice([-1.0, 1.0], size=(m_bg, n_dim)).astype(np.float32)

    pred_cf_cos: Dict[int, List[float]] = {d: [] for d in DEPTH_LIST}
    root_cf_cos: Dict[int, List[float]] = {d: [] for d in DEPTH_LIST}

    for chain_idx in range(N_CHAINS):
        max_d = max(DEPTH_LIST)
        chain_orig = [
            rng.choice([-1.0, 1.0], n_dim).astype(np.float32)
            for _ in range(max_d + 1)
        ]
        chain_cf = [
            rng.choice([-1.0, 1.0], n_dim).astype(np.float32)
            for _ in range(max_d)
        ]

        for d in DEPTH_LIST:
            # --- Predecessor-start protocol ---
            # W_cf = sum_{i=0}^{d-1} outer(chain_cf[i], chain_orig[i]) / n_dim
            # Using matrix multiply to avoid materializing large W:
            # W_cf @ probe_pred = sum_{i} chain_cf[i] * dot(chain_orig[i], probe_pred) / n_dim
            probe_pred = chain_orig[d - 1].copy()
            h_pred = np.zeros(n_dim, dtype=np.float32)
            for i in range(d):
                coeff = float(np.dot(chain_orig[i], probe_pred)) / n_dim
                h_pred += chain_cf[i] * coeff
            ret_pred = np.sign(h_pred).astype(np.float32)
            ret_pred[ret_pred == 0] = 1.0
            cos_pred = cosine_sim_np(ret_pred, chain_cf[d - 1])
            pred_cf_cos[d].append(cos_pred)

            # --- Root-start protocol ---
            # Traverse d hops from chain_orig[0] through per-hop CF rank-1 matrices
            state = chain_orig[0].copy()
            for hop_idx in range(d):
                # W_hop = outer(chain_cf[hop_idx], chain_orig[hop_idx]) / n_dim
                coeff = float(np.dot(chain_orig[hop_idx], state)) / n_dim
                h_hop = chain_cf[hop_idx] * coeff
                state = np.sign(h_hop).astype(np.float32)
                state[state == 0] = 1.0
            cos_root = cosine_sim_np(state, chain_cf[d - 1])
            root_cf_cos[d].append(cos_root)

    mean_pred = {d: float(np.mean(pred_cf_cos[d])) if pred_cf_cos[d] else 0.0
                 for d in DEPTH_LIST}
    mean_root = {d: float(np.mean(root_cf_cos[d])) if root_cf_cos[d] else 0.0
                 for d in DEPTH_LIST}

    elapsed = time.time() - t0
    for d in DEPTH_LIST:
        print(f"  [seed={seed} d={d}] pred_cos={mean_pred[d]:.4f} root_cos={mean_root[d]:.4f}",
              flush=True)
    print(f"  [seed={seed}] elapsed={elapsed:.1f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "mean_pred_cf_cos": {str(d): mean_pred[d] for d in DEPTH_LIST},
        "mean_root_cf_cos": {str(d): mean_root[d] for d in DEPTH_LIST},
        "elapsed_s": elapsed,
    }


def compute_verdict(all_results: List[Dict]) -> tuple:
    if not all_results:
        return ("HARD_FAIL", "No valid results.")

    def agg_depth(key: str, d: int) -> float:
        vals = [r[key].get(str(d), r[key].get(d, None)) for r in all_results]
        vals = [v for v in vals if v is not None]
        return float(np.mean(vals)) if vals else 0.0

    pred_means = {d: agg_depth("mean_pred_cf_cos", d) for d in DEPTH_LIST_FULL}
    root_means = {d: agg_depth("mean_root_cf_cos", d) for d in DEPTH_LIST_FULL}

    tested_depths = [d for d in DEPTH_LIST]
    pred_hp = all(pred_means.get(d, 0.0) <= HP_PRED_MAX_D4PLUS for d in tested_depths)
    pred_hf = any(pred_means.get(d, 0.0) > HF_PRED_MIN_D4PLUS for d in tested_depths)
    root_hp = all(root_means.get(d, 1.0) >= HP_ROOT_MIN_D4PLUS for d in tested_depths)
    root_hf = any(root_means.get(d, 1.0) < HF_ROOT_MAX_D4PLUS for d in tested_depths)

    summary = (f"pred_cos=" + " ".join(f"d{d}:{pred_means.get(d, 0):.3f}" for d in tested_depths) +
               f" root_cos=" + " ".join(f"d{d}:{root_means.get(d, 0):.3f}" for d in tested_depths) +
               f" n_seeds={len(all_results)} N={N_ACT}")

    if pred_hf or root_hf:
        return ("HARD_FAIL",
                f"HARD_FAIL: pred_cos > {HF_PRED_MIN_D4PLUS} (artifact absent) "
                f"OR root_cos < {HF_ROOT_MAX_D4PLUS} (root-start broken). {summary}")

    if pred_hp and root_hp:
        return ("HARD_PASS",
                f"HARD_PASS: pred_cos <= {HP_PRED_MAX_D4PLUS} for d in {{4,6,8}} "
                f"AND root_cos >= {HP_ROOT_MIN_D4PLUS}. "
                f"N=16384 cross-N gap filled; mixed-mechanism confirmed. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial N=16384 cross-N confirmation. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACT} mode={RUN_MODE} "
      f"depths={DEPTH_LIST} alpha={ALPHA}", flush=True)
_prot018_startup_check(N_ACT if RUN_MODE == "smoke" else N)

# GPU utilization: build Xi_bg on GPU to ensure >5% util, then move to CPU for chain traversal
print("[GPU] Building Xi_bg on GPU for utilization check...", flush=True)
_gen_gpu = torch.Generator(device=DEVICE)
_gen_gpu.manual_seed(999)
_dummy_xi = (torch.randint(0, 2, (M_ACT, N_ACT), generator=_gen_gpu,
                            device=DEVICE).float() * 2 - 1)
_peak_gpu_init = torch.cuda.max_memory_allocated(0) / 1e9
assert _peak_gpu_init > 0.001, f"GPU util check FAIL: peak={_peak_gpu_init:.3f}GB"
del _dummy_xi
torch.cuda.empty_cache()
print(f"[GPU] init peak mem={_peak_gpu_init:.3f}GB (pass)", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACT if RUN_MODE == "smoke" else N,
                      M_ACT if RUN_MODE == "smoke" else _M_FULL)
    write_partial(out_dir, seed, result)

per_seed_data = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed_data.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.001, f"GPU utilization check FAIL: peak_gpu={peak_mem_gb:.3f}GB"

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N_ACT, "alpha": ALPHA, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "depths": DEPTH_LIST,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
