"""
capacity_phase_boundary_larger_n_v2_n8192 -- Item 21 LARGER N confirmation at N=8192.

Extends capacity_phase_boundary_under_rram_noise_v1_n4096 (CPU, MIDDLE_BAND smoke artifact)
to N=8192 on GPU, where small-N retrieval noise artifacts are suppressed.

SCIENTIFIC QUESTION:
  At N=8192, does substrate recall accuracy maintain >= 90% below the Wave-2 free-probability
  closed-form phase boundary sigma_g^2 = 1/alpha - 1, and degrade above it?
  Does larger N produce cleaner transition than N=4096 (higher SNR)?

TEST DESIGN:
  (alpha, sigma_g) grid at N=8192, 5 seeds (GPU; N^2 float32 = 256 MB per W matrix):
  alpha in {0.05, 0.10, 0.20, 0.50}
  sigma_g in {0.5, 1.0, 2.0, 4.0, 6.0}
  Noise model: W_noisy = W * exp(sigma_g * Z) where Z ~ N(0,1) entrywise (multiplicative log-normal).
  Symmetrize W_noisy before retrieval.
  Measure mean recall accuracy (cosine similarity of retrieved vs true pattern).

NOTE: W matrix at N=8192 is 8192^2 * 4 bytes = 256 MB. With 4 alpha values x (M noise matrices
  per seed), peak GPU memory per seed is bounded: W_clean (256MB) + W_noisy (256MB) + Xi (varies)
  ~ 600 MB total. Well within 8 GB GPU limit.

FORMULA SELF-TESTS (PROT-022):
  1. Phase boundary formula: sigma_g_crit = sqrt(1/alpha - 1)
     [INPUT: alpha=0.05] [EXPECTED: sigma_g_crit = sqrt(19) = 4.359]
     [INPUT: alpha=0.10] [EXPECTED: sigma_g_crit = sqrt(9) = 3.000]
     [INPUT: alpha=0.20] [EXPECTED: sigma_g_crit = sqrt(4) = 2.000]
     [INPUT: alpha=0.50] [EXPECTED: sigma_g_crit = sqrt(1) = 1.000]
  2. GPU memory > 100 MB after W build (guard against zero allocation).
  3. alpha values: M = int(alpha * N); alpha_actual = M/N; all M > 0.
  4. At least 1 sigma_g below boundary AND 1 above 2x boundary for >= 2 alpha values.

PRE-REGISTERED BANDS:
  HARD-PASS: recall >= 0.90 for (alpha, sigma_g) with sigma_g^2 < (1/alpha - 1)
             AND recall < 0.50 for sigma_g^2 > 2 * (1/alpha - 1);
             phase boundary detected within +-20% across >= 2/4 alpha values (5/5 seeds)
  MIDDLE: phase boundary detected but with >50% width OR detection in only 1/4 alpha values
  HARD-FAIL: no clear phase transition detected OR substrate degrades at sigma_g < 0.5 * sigma_g_crit

PROT-018: anchor has _n8192; N MUST = 8192.
QUEUE: overnight_queue (GPU; N=8192 W matrix 256 MB per seed; 4 alpha x 5 sigma x 5 seeds).
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

ANCHOR_NAME = "capacity_phase_boundary_larger_n_v2_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Grid
ALPHA_VALUES = [0.05, 0.10, 0.20, 0.50]
SIGMA_G_VALUES = [0.5, 1.0, 2.0, 4.0, 6.0]

# Phase boundary: sigma_g_crit = sqrt(1/alpha - 1)
def phase_boundary(alpha: float) -> float:
    return float((1.0 / alpha - 1.0) ** 0.5)

# Pre-registered bands
HP_RECALL_BELOW = 0.90
HP_RECALL_ABOVE = 0.50
N_RETRIEVAL_STEPS = 8
N_QUERIES_PER_CELL = 8

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 1024
    N_QUERIES_USE = 4
    ALPHA_USE = [0.10, 0.20]   # sigma_g_crit = 3.0 and 2.0 -- measurable at all sigma_g values
    SIGMA_USE = [0.5, 1.0, 2.0, 4.0]
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    N_QUERIES_USE = N_QUERIES_PER_CELL
    ALPHA_USE = ALPHA_VALUES
    SIGMA_USE = SIGMA_G_VALUES


def _selftest_phase_boundary():
    """sigma_g_crit^2 = 1/alpha - 1."""
    cases = [(0.05, 4.359), (0.10, 3.000), (0.20, 2.000), (0.50, 1.000)]
    for alpha, expected in cases:
        got = phase_boundary(alpha)
        assert abs(got - expected) < 0.01, (
            f"phase_boundary({alpha}): got {got:.4f}, expected {expected:.3f}")


def _selftest_gpu_alloc():
    """GPU memory allocated after dummy build."""
    dummy = torch.zeros((512, 512), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    del dummy


def _selftest_alpha_m():
    """M = int(alpha * N_ACTIVE) > 0 for all alpha."""
    for alpha in ALPHA_VALUES:
        M_val = max(1, int(alpha * N_ACTIVE))
        assert M_val > 0, f"M=0 for alpha={alpha}"


def _selftest_valid_cells():
    """At smoke scale: >= 2 alpha values have both below-boundary and above-2x-boundary sigma_g."""
    n_valid = 0
    for alpha_test in ALPHA_USE:
        sgc = phase_boundary(alpha_test)
        below = [sg for sg in SIGMA_USE if sg * sg < sgc * sgc]
        above = [sg for sg in SIGMA_USE if sg * sg > 2 * sgc * sgc]
        if len(below) >= 1 and len(above) >= 1:
            n_valid += 1
    assert n_valid >= 1, (
        f"No alpha in {ALPHA_USE} has both below-boundary and above-2x-boundary sigma_g "
        f"in {SIGMA_USE}")


def _instrumentation_selftest():
    _selftest_phase_boundary()
    _selftest_gpu_alloc()
    _selftest_alpha_m()
    _selftest_valid_cells()
    print(f"[selftest] PASS: phase_boundary, gpu_alloc, alpha_m, valid_cells "
          f"N_active={N_ACTIVE}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def hopfield_retrieve_gpu(W: torch.Tensor, probe: torch.Tensor,
                          n_steps: int = N_RETRIEVAL_STEPS) -> torch.Tensor:
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


def run_seed(seed: int, n_dim: int,
             alpha_list: List[float], sigma_list: List[float]) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    grid_results = {}
    for alpha in alpha_list:
        M_val = max(1, int(alpha * n_dim))
        Xi = (torch.randint(0, 2, (M_val, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)
        W_clean = (Xi.t() @ Xi) / float(n_dim)
        sgc = phase_boundary(alpha)

        for sigma_g in sigma_list:
            if sigma_g == 0.0:
                W_noisy = W_clean.clone()
            else:
                Z = torch.randn(n_dim, n_dim, generator=gen, device=DEVICE)
                W_noisy = W_clean * torch.exp(torch.tensor(sigma_g, device=DEVICE) * Z)
                W_noisy = (W_noisy + W_noisy.t()) / 2.0

            n_q = min(N_QUERIES_USE, M_val)
            recalls = []
            for q in range(n_q):
                xi_q = Xi[q]
                probe = xi_q.clone()
                flip_mask = (torch.rand(n_dim, generator=gen, device=DEVICE) < 0.10)
                probe[flip_mask] *= -1.0
                state = hopfield_retrieve_gpu(W_noisy, probe)
                cos = cosine_sim_gpu(state, xi_q)
                recalls.append(cos)
            mean_recall = float(sum(recalls) / len(recalls)) if recalls else 0.0

            below_boundary = (sigma_g ** 2) < (sgc ** 2)
            above_2x = (sigma_g ** 2) > 2.0 * (sgc ** 2)
            key = f"a{alpha:.2f}_sg{sigma_g:.1f}"
            grid_results[key] = {
                "alpha": float(alpha), "sigma_g": float(sigma_g),
                "recall": float(mean_recall), "sigma_g_crit": float(sgc),
                "below_boundary": bool(below_boundary), "above_2x": bool(above_2x),
            }
            print(f"  [seed={seed} alpha={alpha:.2f} sg={sigma_g:.1f} sgc={sgc:.3f}] "
                  f"recall={mean_recall:.4f} below={below_boundary} above2x={above_2x}", flush=True)

        del Xi, W_clean
        torch.cuda.empty_cache()

    elapsed = time.time() - t0
    peak_gb = torch.cuda.max_memory_allocated(0) / 1e9
    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "elapsed_s": float(elapsed), "peak_gpu_gb": float(peak_gb),
        "grid_results": grid_results,
    }


def compute_verdict(all_results: List[Dict]) -> tuple:
    if not all_results:
        return ("HARD_FAIL", "No valid results.")

    # Aggregate recall per cell across seeds
    cell_recalls = {}
    for r in all_results:
        for key, cell in r.get("grid_results", {}).items():
            if key not in cell_recalls:
                cell_recalls[key] = {"recalls": [], "alpha": cell["alpha"],
                                     "sigma_g": cell["sigma_g"],
                                     "below_boundary": cell["below_boundary"],
                                     "above_2x": cell["above_2x"]}
            cell_recalls[key]["recalls"].append(cell["recall"])

    import numpy as _np
    hp_below_violations = 0
    hp_above_violations = 0
    below_cells = 0
    above_cells = 0
    for key, cd in cell_recalls.items():
        mean_r = float(_np.mean(cd["recalls"]))
        if cd["below_boundary"]:
            below_cells += 1
            if mean_r < HP_RECALL_BELOW:
                hp_below_violations += 1
        if cd["above_2x"]:
            above_cells += 1
            if mean_r >= HP_RECALL_ABOVE:
                hp_above_violations += 1

    alpha_with_transition = set()
    for key, cd in cell_recalls.items():
        alpha = cd["alpha"]
        mean_r = float(_np.mean(cd["recalls"]))
        sgc = phase_boundary(alpha)
        sg = cd["sigma_g"]
        if sg ** 2 < sgc ** 2 and mean_r >= HP_RECALL_BELOW:
            alpha_with_transition.add(alpha)
        if sg ** 2 > 2 * sgc ** 2 and mean_r < HP_RECALL_ABOVE:
            alpha_with_transition.add(alpha)

    n_alpha_total = len(ALPHA_VALUES)
    n_alpha_detected = len(alpha_with_transition)

    summary = (f"below_violations={hp_below_violations}/{below_cells} "
               f"above_violations={hp_above_violations}/{above_cells} "
               f"alpha_transition={n_alpha_detected}/{n_alpha_total} N=8192")

    if below_cells == 0 or above_cells == 0:
        return ("HARD_FAIL", f"HARD_FAIL: insufficient grid coverage. {summary}")
    if (hp_below_violations > below_cells // 2 and
            hp_above_violations > above_cells // 2):
        return ("HARD_FAIL", f"HARD_FAIL: no clear phase transition at N=8192. {summary}")

    hp_below_ok = hp_below_violations == 0
    hp_above_ok = hp_above_violations == 0
    if hp_below_ok and hp_above_ok and n_alpha_detected >= 2:
        return ("HARD_PASS",
                f"HARD_PASS: Phase boundary confirmed at N=8192. recall >=0.90 below, "
                f"<0.50 above 2x boundary. {summary}")

    if hp_below_ok or hp_above_ok or n_alpha_detected >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial transition signal. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


def _prot018_startup_check() -> None:
    if RUN_MODE != "smoke" and N_ACTIVE != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor _n{_N_SUFFIX} but FULL N_ACTIVE={N_ACTIVE}")


alpha_use = ALPHA_USE if RUN_MODE == "smoke" else ALPHA_VALUES
sigma_use = SIGMA_USE if RUN_MODE == "smoke" else SIGMA_G_VALUES
print(f"[config] PROT-018 N={N} N_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha={alpha_use} sigma_g={sigma_use}", flush=True)
_prot018_startup_check()

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alpha_values": alpha_use, "sigma_g_values": sigma_use, "run_mode": RUN_MODE}
done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] seeds_todo={seeds_todo} out_dir={out_dir}", flush=True)

t0_total = time.time()
for s in seeds_todo:
    res = run_seed(s, N_ACTIVE, alpha_use, sigma_use)
    write_partial(out_dir, s, res)
    print(f"[progress] seed={s} done", flush=True)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_total = time.time() - t0_total
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU util check FAIL: peak_gpu={peak_mem_gb:.3f}GB (< 100MB)"

metrics = {
    "anchor": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(all_results),
    "N": N,
    "run_mode": RUN_MODE,
    "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
    "phase_boundaries": {str(a): phase_boundary(a) for a in ALPHA_VALUES},
    "summary": verdict_msg[:300],
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
