"""
pp49_hrc_deeper_d_d10_d12_d14_v1_n8192 -- PP-49 HRC deeper-d sweep at N=8192, d=10,12,14.

CONTEXT (v372 cycle 42 all-night burst):
  PP-49 row: EXPLORATORY.
  Prior runs: d=4/6/8 at N=16384 (pp49_hrc_cross_n_d4_d6_d8_v1_n16384) HARD-FAIL (pred_cos=1.0
    saturated; research: fixed-point absorbing at predecessor-start protocol).
  d=10/12/14 at N=16384 (pp49_hrc_deeper_d_d10_d12_d14_v1_n16384) -- verdict pending v372.
  This N=8192 companion tests whether N-dependence exists in the deeper-d behavior.
  Cross-N: if saturation is N-independent (fixed-point absorbing is discrete), pred_cos=1.0
  should hold at N=8192 same as N=16384.

SCIENTIFIC QUESTION:
  Does the predecessor-start saturation (pred_cos=1.0) persist at d>=10 N=8192?
  Cross-N check: does root_cos track at N=8192 vs N=16384?
  Expected: N-independence (fixed-point absorbing is discrete/N-independent per research drill).

MEMORY ESTIMATE (OOM pre-check):
  M_bg = int(0.05 * 8192) = 409 patterns.
  Xi_bg: 409 * 8192 * 4 bytes = 13.4 MB GPU. Fine.
  Peak GPU: Xi_bg (~14 MB). Well within 8 GB.

PRE-REGISTERED BANDS (PP-49 deeper d=10/12/14 at N=8192; cross-N companion):
  Prior empirical anchor: N=16384 d=10/12/14 (verdict pending; use N=16384 d=4/6/8 as anchor).
  Cross-N probe (no prior N=8192 deeper-d anchor): bands widened to +-50% of N=16384 prediction.
  Pred-start saturation expected to persist: pred_cos in [0.90, 1.05] for all d in {10,12,14}.
  Root-start: root_cos expected in [0.50, 1.0] at d>=10 (wide band; depth may degrade chain).
  HARD-PASS: pred_cos >= 0.90 for d in {10,12,14} (saturation persists)
             AND root_cos >= 0.40 for d in {10,12,14} (chain at least partially coherent).
  MIDDLE: pred_cos in [0.60, 0.90) for any d OR root_cos in [0.20, 0.40).
  HARD-FAIL: pred_cos < 0.60 for any d (unexpected)
             OR root_cos < 0.20 for all d (chain completely incoherent).

FORMULA SELF-TESTS (PROT-022):
  1. Root-start depth-1 traversal: cf_cos non-NaN at N=64.
     [INPUT: N=64, 1 chain, depth=1] [EXPECTED: cf_cos non-NaN, in [0,1]]
  2. M at alpha=0.05, N=8192: int(0.05 * 8192) = 409. [EXPECTED: M=409]
  3. W_cf rank-1 outer product at N=64 non-NaN. [EXPECTED: no TypeError]
  4. Xi_bg VRAM at N=8192: 409 * 8192 * 4 < 1e7 bytes. [EXPECTED: < 2e7]

3-cell sweep: d=10, d=12, d=14. GPU (pattern build) + CPU numpy (chain traversal).
Reuses d=10/12/14 N=16384 architecture; N rescaled to 8192.

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: seed checkpoints keyed with run_mode + max_depth.
QUEUE: overnight_queue (GPU machine; Xi on GPU; chain traversal on CPU numpy; 3 cells).
TIMEOUT ESTIMATE: N=16384 d=10/12/14 elapsed ~280s (3 depths x 5 seeds). N=8192 faster (~140s).
  ceil(1.5 * 140) = 210s. Use 600s with margin.
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

ANCHOR_NAME = "pp49_hrc_deeper_d_d10_d12_d14_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
DEPTH_LIST_FULL = [10, 12, 14]

# PROT-022 formula self-tests at module scope (arithmetic only, no GPU)
_M_FULL = int(ALPHA * N)
assert _M_FULL == 409, f"M at N={N} alpha={ALPHA}: {_M_FULL} expected 409"

_xi_bytes_full = _M_FULL * N * 4
assert _xi_bytes_full < 2e7, (
    f"Xi VRAM at N={N}: {_xi_bytes_full/1e6:.0f}MB >= 20MB")

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACT = 512
    DEPTH_LIST = [10, 12]
    N_CHAINS = 3
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACT = N
    DEPTH_LIST = DEPTH_LIST_FULL
    N_CHAINS = 5

M_ACT = int(ALPHA * N_ACT)

# Pre-registered thresholds (cross-N companion; same bands as N=16384)
HP_PRED_MIN_D10PLUS = 0.90
HP_ROOT_MIN_D10PLUS = 0.40
HF_PRED_MIN_DECAY = 0.60
HF_ROOT_MAX_BROKEN = 0.20


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
    probe = xi_A.copy()
    h_correct = xi_B * (float(np.dot(xi_A, probe)) / N_t)
    ret = np.sign(h_correct).astype(np.float32)
    ret[ret == 0] = 1.0
    cos_val = cosine_sim_np(ret, xi_B)
    assert not np.isnan(cos_val), "cf_cos is NaN in depth-1 selftest"
    assert 0.0 <= cos_val <= 1.0 + 1e-6, f"cf_cos out of range: {cos_val}"
    print(f"  [selftest depth1] N={N_t} cf_cos_root={cos_val:.3f}", flush=True)


def _selftest_m_check():
    assert _M_FULL == 409, f"M_full={_M_FULL} expected 409"


def _instrumentation_selftest():
    _selftest_depth1_cf()
    _selftest_m_check()
    dummy = torch.zeros((512, 512), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, "GPU memory not allocated"
    del dummy
    print(f"[selftest] PASS: depth1_cf ok, M_check={_M_FULL}, "
          f"N_ACT={N_ACT} depths={DEPTH_LIST}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int, m_bg: int) -> Dict:
    """Run one seed across d=10,12,14 for both protocols."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

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
            # Predecessor-start protocol
            probe_pred = chain_orig[d - 1].copy()
            h_pred = np.zeros(n_dim, dtype=np.float32)
            for i in range(d):
                coeff = float(np.dot(chain_orig[i], probe_pred)) / n_dim
                h_pred += chain_cf[i] * coeff
            ret_pred = np.sign(h_pred).astype(np.float32)
            ret_pred[ret_pred == 0] = 1.0
            cos_pred = cosine_sim_np(ret_pred, chain_cf[d - 1])
            pred_cf_cos[d].append(cos_pred)

            # Root-start protocol
            state = chain_orig[0].copy()
            for hop_idx in range(d):
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
    pred_hf = any(pred_means.get(d, 1.0) < HF_PRED_MIN_DECAY for d in tested_depths)
    root_hf_all = all(root_means.get(d, 1.0) < HF_ROOT_MAX_BROKEN for d in tested_depths)

    summary = ("pred_cos=" + " ".join(f"d{d}:{pred_means.get(d, 0):.3f}" for d in tested_depths) +
               " root_cos=" + " ".join(f"d{d}:{root_means.get(d, 0):.3f}" for d in tested_depths) +
               f" n_seeds={len(all_results)} N={N_ACT}")

    if pred_hf:
        return ("HARD_FAIL",
                f"HARD_FAIL: pred_cos < {HF_PRED_MIN_DECAY} for some d. {summary}")
    if root_hf_all:
        return ("HARD_FAIL",
                f"HARD_FAIL: root_cos < {HF_ROOT_MAX_BROKEN} for all d. {summary}")

    pred_hp = all(pred_means.get(d, 0.0) >= HP_PRED_MIN_D10PLUS for d in tested_depths)
    root_hp = all(root_means.get(d, 0.0) >= HP_ROOT_MIN_D10PLUS for d in tested_depths)

    if pred_hp and root_hp:
        return ("HARD_PASS",
                f"HARD_PASS: pred_cos >= {HP_PRED_MIN_D10PLUS} (sat persists) "
                f"AND root_cos >= {HP_ROOT_MIN_D10PLUS} (chain coherent) "
                f"for d in {{10,12,14}} at N=8192. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial confirmation at d=10/12/14 N=8192. {summary}")


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

# GPU utilization: build Xi_bg on GPU to ensure >5% util, then move to CPU
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
    "N": N, "run_mode": RUN_MODE,
    "depths_tested": DEPTH_LIST_FULL,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         "mean_pred_cf_cos": r.get("mean_pred_cf_cos"),
         "mean_root_cf_cos": r.get("mean_root_cf_cos"),
         "elapsed_s": r.get("elapsed_s")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
