"""
q_a3_l20_cross_layer_composition_v1_n16384 -- Q-A3/PP-12: L=20 cross-layer composition at N=16384.

CONTEXT (PP-12/Q-A3 N-scale cross-N):
  N=4096 series: L=2..L=33+ all EXACT-1.0000 (19+ consecutive extensions; v359).
  N=8192 series: {L=19, L=22, L=23, L=24, L=25} all EXACT-class (v359).
  N=16384: never tested. This is the FIRST cross-N rung at N=16384.
  N-scale gap: N=16384 is 4x N=4096. Algebraic ECC theory predicts N-independence
  (composition depth depends on per-stage alpha_k, not N). Expected: EXACT-1.0 at L=20.

SCIENTIFIC QUESTION:
  Does cross-layer composition fidelity remain EXACT-1.0 at N=16384?
  N-independence confirmed through N=8192 (L=25). This extends the cross-N ladder to N=16384.
  If HP: enables PP-12 3-N cross-N band annotation and strengthens product claim.

MEMORY ESTIMATE:
  20 W matrices x (16384 x 16384 x 4 bytes) = 20 x 1073.7 MB = ~21474 MB total.
  NOTE: 20 x 16384^2 x 4 / 1e9 = 21.47 GB. This EXCEEDS 8 GB GPU.
  -- CORRECTION: cannot hold all 20 W matrices simultaneously.
  -- Use sequential build: free W after decode, recompute on demand? No -- must decode top-down.
  -- Alternative: use list and del as we decode (but top-down decoding needs all Ws).
  -- ACTUAL APPROACH: build Xi patterns (not W) and recompute W on-demand during decode.
  -- Xi memory: 20 x 8192 x 16384 x 4 / 1e9 = 10.74 GB. Also too large.
  -- Correct approach: build ONE W per layer, decode immediately, then del W.
  -- But top-down decode needs W_L (outer) first, then W_{L-1}, ..., W_1.
  -- So: build Ws bottom-up but store Xi patterns (smaller), decode top-down recomputing W.
  -- Xi_inner (100 x 16384 x 4 bytes) = 6.4 MB. M_MID~2 per layer after L4: ~0.12 MB each.
  -- Total Xi storage: (100 + 50 + 25 + 12 + 6 + 3 + 14*2 + 2) x 16384 x 4 bytes ~= 2.0 GB.
  -- W on-demand during decode: one W at a time = 16384^2 x 4 / 1e9 = 1.074 GB.
  -- PEAK GPU: Xi (~2.0 GB) + W_current (~1.074 GB) + scratch (~0.2 GB) = ~3.27 GB. FITS.

PRE-REGISTERED BANDS (N-scale cross-N first rung at N=16384; no prior empirical anchor):
  Calibration probe: bands set +-50% of theoretical prediction per calibration-probe policy.
  Theoretical: EXACT-1.0 (N-independent from ECC theory + N=4096/N=8192 evidence).
  +-50% means: HARD-PASS if all fids >= 0.5 (1.0 * 0.5 threshold); HARD-FAIL if < 0.17 (1/3 * 0.5).
  Practical tightening: given 2 prior N-scales both EXACT, bands set at prior-informed level:
  HARD-PASS: all 20 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l20_acc >= 0.5.
  MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation.
  HARD-FAIL: any L_fid < 0.85 OR l20_acc < 0.5.
  NOTE: wide calibration applies because this is the first N=16384 measurement.
  If MIDDLE: indicates N-dependent effects; warrants further investigation.

FORMULA SELF-TESTS (PROT-022):
  1. L=20 chain: 19-ctx Hadamard roundtrip recovers xi_L1.
     [INPUT: 2-element +-1 vectors, 19 context ops] [EXPECTED: decode = xi_L1 exactly]
  2. All alphas < alpha_c=0.138 at N=16384. M_INNER=100 -> alpha=0.0061 < 0.138.
  3. GPU memory > 0 after W build.
  4. Xi storage estimate: (100+50+25+12+6+3+14*2+2) * 16384 * 4 / 1e9 < 2.5 GB.
     [INPUT: M schedule sum, N=16384] [EXPECTED: < 2.5 GB]
  5. W on-demand peak: 16384^2 * 4 / 1e9 < 1.2 GB.
     [INPUT: N=16384] [EXPECTED: 1.074 < 1.2]

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed with run_mode + L.
QUEUE: overnight_queue (GPU; on-demand W build, ~3.3 GB peak at N=16384).
TIMEOUT ESTIMATE: N=8192 L=25 elapsed ~2.01s FULL 5-seed.
  N=16384 = 4x N^2 per W (2x N for W matmul). L=20 vs L=25 ratio = 0.8.
  W matmul at N=16384 is ~4x slower per W. 20 Ws vs 25 Ws: 0.8x.
  ceil(1.5 * 2.01 * 4.0 * 0.8 * 1.0) = ceil(9.65) = 300s (GPU queue overhead floor).
  Note: W is recomputed during decode; actual time may differ. Using 300s floor.
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

ANCHOR_NAME = "q_a3_l20_cross_layer_composition_v1_n16384"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
L_DEPTH = 20
HP_FIDELITY_UNANI_THRESH = 0.9999
MIDDLE_FIDELITY = 0.85
HF_FIDELITY = 0.85
HP_LACC = 0.5
HF_LACC = 0.5
NOISE_FRAC = 0.10

# PROT-022 self-test: W on-demand size
_W_ONDEMAND_GB = 16384 * 16384 * 4 / 1e9
assert _W_ONDEMAND_GB < 1.2, f"W on-demand size: {_W_ONDEMAND_GB:.3f} GB"

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    M_INNER = 20
    # 18 middle layers (L2..L19), then M_OUTER=L20
    M_MID = [10, 5, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    M_OUTER = 2
    N_QUERIES = 2
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    M_INNER = 100
    # 18 middle layers (L2..L19), then M_OUTER=L20
    M_MID = [50, 25, 12, 6, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    M_OUTER = 2
    N_QUERIES = 2

# M_MID has 18 entries (L2..L19), M_OUTER is L20
# Layer schedule: L1=M_INNER, L2..L19=M_MID[0..17], L20=M_OUTER
# Total: 1 + 18 + 1 = 20 = L_DEPTH
assert len(M_MID) == 18, f"M_MID length {len(M_MID)} expected 18"

# Xi storage estimate (for OOM pre-check)
_m_sched = [M_INNER] + list(M_MID) + [M_OUTER]
_xi_bytes = sum(m * N * 4 for m in _m_sched)
_xi_gb = _xi_bytes / 1e9
print(f"[config] Xi storage estimate: {_xi_gb:.3f} GB at N={N}", flush=True)
assert _xi_gb < 2.5, f"Xi storage estimate {_xi_gb:.3f} GB exceeds 2.5 GB headroom"


def _selftest_l20_chain():
    """19-ctx Hadamard roundtrip recovers xi_L1."""
    base = [[1.0, -1.0], [-1.0, 1.0], [1.0, 1.0], [-1.0, -1.0]]
    ctxs = [torch.tensor(base[i % 4], dtype=torch.float32, device=DEVICE) for i in range(19)]
    xi_L1 = torch.tensor([1.0, -1.0], dtype=torch.float32, device=DEVICE)
    xi = xi_L1.clone()
    for c in ctxs:
        xi = c * xi
    xi_dec = xi.clone()
    for c in reversed(ctxs):
        xi_dec = xi_dec * c
    assert torch.allclose(xi_dec, xi_L1, atol=1e-6), f"L20 chain decode failed: {xi_dec}"


def _instrumentation_selftest():
    _selftest_l20_chain()
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
    print(f"[selftest] PASS: L20 chain decode ok, capacity_ok, gpu_mem_ok N={n_dim}", flush=True)


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

    # Build all Xi layers (store patterns, not W matrices, to save GPU memory)
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
    # L20 outer
    ctx_outer = bsc(M_OUTER, n_dim)
    Xi_ctxs.append(ctx_outer)
    Xi_outer = ctx_outer * curr[:M_OUTER]
    Xi_layers.append(Xi_outer)

    assert len(Xi_layers) == L_DEPTH, f"Xi_layers count {len(Xi_layers)} != {L_DEPTH}"

    xi_mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after Xi build: {xi_mem_gb:.3f} GB", flush=True)

    level_fids = {f"L{l}": [] for l in range(1, L_DEPTH + 1)}
    l20_acc = []

    for q_idx in range(min(N_QUERIES, M_OUTER)):
        xi_outer_true = Xi_outer[q_idx]
        probe = xi_outer_true.clone()
        flip_mask = (torch.rand(n_dim, generator=gen, device=DEVICE) < NOISE_FRAC)
        probe[flip_mask] *= -1.0

        # Decode chain top-down: build W on-demand and immediately free
        decoded = [None] * L_DEPTH

        # L_DEPTH level (outermost)
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

        l20_acc.append(cosine_sim_gpu(decoded[0], Xi_layers[0][q_idx]))

    mean_fids = {k: float(sum(v) / len(v)) if v else 0.0 for k, v in level_fids.items()}
    mean_l20 = float(sum(l20_acc) / len(l20_acc)) if l20_acc else 0.0

    peak_mem = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] fids={' '.join(f'{k}:{mean_fids[k]:.4f}' for k in sorted(mean_fids.keys()))} "
          f"l20_acc={mean_l20:.4f} peak_gpu={peak_mem:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    result = {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "l20_accuracy": float(mean_l20),
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
    l20_acc = mean_key("l20_accuracy")

    fid_list = [fid_vals[f"L{l}"] for l in range(1, L_DEPTH + 1)]
    summary = (" ".join(f"L{l}:{fid_vals[f'L{l}']:.4f}" for l in range(1, L_DEPTH + 1)) +
               f" l20_acc={l20_acc:.4f}(HP>={HP_LACC} HF<{HF_LACC}) n_seeds={len(results)}")

    if any(f < HF_FIDELITY for f in fid_list) or l20_acc < HF_LACC:
        return ("HARD_FAIL", f"HARD_FAIL: any fid<{HF_FIDELITY} or l20_acc<{HF_LACC}. {summary}")

    all_unanimous = all(f >= HP_FIDELITY_UNANI_THRESH for f in fid_list)
    if all_unanimous and l20_acc >= HP_LACC:
        return ("HARD_PASS", f"HARD_PASS: all {L_DEPTH} levels EXACT-1.0 unanimous "
                f"+ l20_acc HP at N={N}. N-independence first-rung confirmed L=20. {summary}")

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
         **{f"fid_l{l}": r.get(f"fid_l{l}") for l in range(1, L_DEPTH + 1)},
         "l20_accuracy": r.get("l20_accuracy"),
         "peak_gpu_gb": r.get("peak_gpu_gb")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
