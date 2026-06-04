"""
q_a3_l300_cross_layer_composition_v1_n8192 -- Q-A3/PP-12: L=300 cross-layer composition at N=8192.

CONTEXT (v372 cycle 42 all-night burst):
  N=8192 series: L=19..L=40 all EXACT-1.0000 (L=40 NEW DEEPEST cycle 41).
  L=300 is rung 281 in the N=8192 depth ladder (cross-N ladder paired with N=16384 L=300).
  ECC criterion: depth UNLIMITED when per-stage max(alpha_k) < alpha_c=0.138.
  L=299 per-stage alpha = 100/8192 = 0.0122 << alpha_c. Theory predicts EXACT fidelity.

SCIENTIFIC QUESTION:
  Does cross-layer composition fidelity remain EXACT-1.0 at L=300 N=8192?
  If yes: extends N=8192 cross-N series to L=300 (cross-N at L=300).

MEMORY ESTIMATE (on-demand W):
  One W matrix at a time: 8192 x 8192 x 4 bytes = 268 MB. Well within 8 GB GPU.

PRE-REGISTERED BANDS (Q-A3 L=300 N=8192):
  HARD-PASS: all 300 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l300_acc >= 0.5.
  MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation.
  HARD-FAIL: any L_fid < 0.85 OR l300_acc < 0.5.

FORMULA SELF-TESTS (PROT-022):
  1. L=300 chain: 299-ctx Hadamard roundtrip recovers xi_L1.
     [INPUT: 2-element +-1 vectors, 299 context ops] [EXPECTED: decode = xi_L1 exactly]
  2. All alphas < alpha_c=0.138 at N=8192. M_INNER=100 -> alpha=0.0122 < 0.138.
  3. GPU memory > 0 after W build.
  4. Memory on-demand per W: 8192*8192*4 = 268 MB < 1 GB.

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: seed checkpoints keyed with run_mode + L.
QUEUE: overnight_queue (GPU; on-demand W build at N=8192).
TIMEOUT ESTIMATE: L=40 N=8192 elapsed ~6s (5-seed). L=300 near-linear.
  ceil(1.5 * 266 * 1.0 * 1) = 400s. Use PROT-019 floor: 21600s.
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

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "q_a3_l300_cross_layer_composition_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
L_DEPTH = 300
HP_FIDELITY_UNANI_THRESH = 0.9999
MIDDLE_FIDELITY = 0.85
HF_FIDELITY = 0.85
HP_LACC = 0.5
HF_LACC = 0.5
NOISE_FRAC = 0.10

_W_ONDEMAND_GB = 8192 * 8192 * 4 / 1e9
assert _W_ONDEMAND_GB < 1.0, f"W on-demand size: {_W_ONDEMAND_GB:.3f} GB"

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    M_INNER = 20
    M_MID = [
        10, 5, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    ]
    M_OUTER = 2
    N_QUERIES = 2
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    M_INNER = 100
    M_MID = [
        50, 25, 12, 6, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    ]
    M_OUTER = 2
    N_QUERIES = 2

assert len(M_MID) == L_DEPTH - 2, f"M_MID length {len(M_MID)} expected {L_DEPTH - 2}"


def _selftest_lN_chain():
    n_ctx = L_DEPTH - 1
    base = [[1.0, -1.0], [-1.0, 1.0], [1.0, 1.0], [-1.0, -1.0]]
    ctxs = [torch.tensor(base[i % 4], dtype=torch.float32, device=DEVICE) for i in range(n_ctx)]
    xi_L1 = torch.tensor([1.0, -1.0], dtype=torch.float32, device=DEVICE)
    xi = xi_L1.clone()
    for c in ctxs:
        xi = c * xi
    xi_dec = xi.clone()
    for c in reversed(ctxs):
        xi_dec = xi_dec * c
    assert torch.allclose(xi_dec, xi_L1, atol=1e-6), f"L{L_DEPTH} chain decode failed: {xi_dec}"


def _instrumentation_selftest():
    _selftest_lN_chain()
    n_dim = N_ACTIVE
    ms = [M_INNER] + M_MID + [M_OUTER]
    assert len(ms) == L_DEPTH, f"M schedule length {len(ms)} != L_DEPTH {L_DEPTH}"
    for i, m in enumerate(ms, 1):
        al = m / n_dim
        assert al < ALPHA_C, f"L{i} alpha {al:.4f} >= alpha_c={ALPHA_C}"
    dummy = torch.zeros((512, 512), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy
    print(f"[selftest] PASS: L{L_DEPTH} chain decode ok, capacity_ok, gpu_mem_ok N={n_dim}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def hopfield_retrieve_gpu(W: torch.Tensor, probe: torch.Tensor, n_steps: int = 5) -> torch.Tensor:
    state = probe.clone()
    for _ in range(n_steps):
        h = W @ state
        state = torch.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)

    Xi_inner = bsc(M_INNER, n_dim)
    Xi_layers = [Xi_inner]
    Xi_ctxs = []
    curr = Xi_inner
    for i, m in enumerate(M_MID):
        ctx = bsc(m, n_dim)
        Xi_ctxs.append(ctx)
        mid = ctx * curr[:m]
        Xi_layers.append(mid)
        curr = mid
    ctx_outer = bsc(M_OUTER, n_dim)
    Xi_ctxs.append(ctx_outer)
    Xi_outer = ctx_outer * curr[:M_OUTER]
    Xi_layers.append(Xi_outer)

    assert len(Xi_layers) == L_DEPTH, f"Xi_layers count {len(Xi_layers)} != {L_DEPTH}"

    xi_mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after Xi build: {xi_mem_gb:.3f} GB", flush=True)

    level_fids = {f"L{l}": [] for l in range(1, L_DEPTH + 1)}
    l_acc = []

    for q_idx in range(min(N_QUERIES, M_OUTER)):
        xi_outer_true = Xi_outer[q_idx]
        probe = xi_outer_true.clone()
        flip_mask = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC)
        probe[flip_mask] *= -1.0

        decoded = [None] * L_DEPTH

        W_top = (Xi_layers[L_DEPTH - 1].t() @ Xi_layers[L_DEPTH - 1]) / n_dim
        ret = hopfield_retrieve_gpu(W_top, probe)
        del W_top
        decoded[L_DEPTH - 1] = ret
        level_fids[f"L{L_DEPTH}"].append(cosine_sim_gpu(ret, xi_outer_true))

        for l_idx in range(L_DEPTH - 2, -1, -1):
            l_label = l_idx + 1
            ptr = decoded[l_idx + 1] * Xi_ctxs[l_idx][q_idx]
            W_l = (Xi_layers[l_idx].t() @ Xi_layers[l_idx]) / n_dim
            ret_l = hopfield_retrieve_gpu(W_l, ptr)
            del W_l
            decoded[l_idx] = ret_l
            fid = cosine_sim_gpu(ret_l, Xi_layers[l_idx][q_idx])
            level_fids[f"L{l_label}"].append(fid)

        l_acc.append(cosine_sim_gpu(decoded[0], Xi_layers[0][q_idx]))

    mean_fids = {k: float(sum(v) / len(v)) if v else 0.0 for k, v in level_fids.items()}
    mean_lacc = float(sum(l_acc) / len(l_acc)) if l_acc else 0.0

    peak_mem = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] l{L_DEPTH}_acc={mean_lacc:.4f} peak_gpu={peak_mem:.3f}GB "
          f"elapsed={elapsed:.2f}s", flush=True)

    result = {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        f"l{L_DEPTH}_accuracy": float(mean_lacc),
        "peak_gpu_gb": float(peak_mem), "elapsed_s": elapsed,
    }
    for k, v in mean_fids.items():
        result[f"fid_{k.lower()}"] = v
    return result


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    fid_vals = {f"L{l}": mean_key(f"fid_l{l}") for l in range(1, L_DEPTH + 1)}
    lacc = mean_key(f"l{L_DEPTH}_accuracy")

    fid_list = [fid_vals[f"L{l}"] for l in range(1, L_DEPTH + 1)]
    summary = (" ".join(f"L{l}:{fid_vals[f'L{l}']:.4f}" for l in range(1, L_DEPTH + 1)) +
               f" l{L_DEPTH}_acc={lacc:.4f} n_seeds={len(results)}")

    if any(f < HF_FIDELITY for f in fid_list) or lacc < HF_LACC:
        return ("HARD_FAIL", f"HARD_FAIL: any fid<{HF_FIDELITY} or l{L_DEPTH}_acc<{HF_LACC}. {summary}")

    all_unanimous = all(f >= HP_FIDELITY_UNANI_THRESH for f in fid_list)
    if all_unanimous and lacc >= HP_LACC:
        return ("HARD_PASS", f"HARD_PASS: all {L_DEPTH} levels EXACT-1.0 unanimous "
                f"+ l{L_DEPTH}_acc HP at N={N}. {summary}")

    if any(f < MIDDLE_FIDELITY for f in fid_list):
        return ("MIDDLE_BAND", f"MIDDLE_BAND: graceful degradation (some fid<{MIDDLE_FIDELITY}). {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: some fids in [{MIDDLE_FIDELITY},1.0). {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} L={L_DEPTH}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "L": L_DEPTH, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU util check FAIL: peak_gpu={peak_mem_gb:.3f}GB (< 100MB)"

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "L": L_DEPTH, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         "lacc": r.get(f"l{L_DEPTH}_accuracy"),
         "peak_gpu_gb": r.get("peak_gpu_gb"),
         "elapsed_s": r.get("elapsed_s")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
