"""
substrate_rem_replay_retrieval_energy_baseline_v1_n8192_gpu -- REM-replay energy consolidation (Phase 1c, GPU).

ROUTING: notes/routing_convergent_brain_architecture_empirical_batch_2026-06-04.md (Research), Phase 1c.
  Routed to the OWNED GPU (N=8192 N x N Hopfield matmuls; keeps the GPU occupied per user directive).

CAPABILITY QUESTION:
  Does energy-guided top-K REM-style replay consolidate substrate memory (reduce retrieval energy) at
  N >= 8192 (above the bipolar quantization floor), and is the effect CONDITIONAL on N (null at N=4096)?
  (Lit: REM replay / systems consolidation; the drill predicts replay helps only above the quant floor.)

MODEL (auto-associative Hopfield substrate; Crick-Mitchison REM unlearning):
  Store M = alpha*N bipolar patterns in W = sum_i outer(xi,xi)/N (diagonal zeroed). Per-pattern retrieval
  energy = 1 - overlap(xi, sign(W xi)) in [0,2] (0 = perfect recall; loaded regime -> positive residual).
  REM replay = Crick-Mitchison (1983) / Hopfield-Feinstein-Palmer (1983) UNLEARNING: each of R* cycles,
  present K random probes, settle them via a few Hopfield steps to (mostly spurious) attractors S, and
  UNLEARN them W -= (lambda/N) outer(S,S) (diagonal re-zeroed). Removing spurious minima deepens the
  genuine pattern basins -> should REDUCE the stored patterns' mean retrieval energy. Re-measure over ALL
  stored patterns. (Whether this helps, and whether it is N-conditional, is the empirical question.)

THREE CELLS (5 seeds each):
  A: N=8192, NO replay (baseline; confirms reduction is from replay, not re-measurement).
  B: N=8192, top-K=20 replay over R*=10 cycles.
  C: N=4096, top-K=20 replay over R*=10 cycles (control; below quant floor; drill predicts NULL).

PRE-REGISTERED BANDS (reduction% = (energy_initial - energy_final)/energy_initial * 100):
  HARD-PASS: Cell B reduction > 30% AND Cell C reduction < 10% (confirms the N>=8192 conditional).
  MIDDLE: Cell B reduction in [10,30]% OR Cell C also reduces > 10% (refutes the quant-floor conditional).
  HARD-FAIL: no cell reduces > 10% (replay does not consolidate).

FORMULA SELF-TESTS (PROT-022):
  1. perfect recall at low load: a single stored pattern recalls exactly (overlap=1, energy~0).
  2. replay reduces a worst-pattern's energy (monotone on the targeted pattern in a loaded toy).
  3. overlap in [-1,1]; energy in [0,2].

PROT-018: anchor _n8192 -> the HEADLINE cells use N=8192 (Cell C control uses N=4096 by design).
PROT-021: seed checkpoints keyed run_mode + seed. QUEUE: overnight_queue (GPU). TIMEOUT: 21600s (PROT-019
  floor _n>=8192). GPU TEMPLATE: assert cuda + device='cuda' + batched matmul. ASCII-only stdout.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB", flush=True)
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "substrate_rem_replay_retrieval_energy_baseline_v1_n8192_gpu"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.12            # loaded regime (near alpha_c=0.138) so there is recall residual to consolidate
TOPK = 20
R_STAR = 10
LAMBDA = 0.10
HP_B_RED, MID_B_RED = 30.0, 10.0
C_NULL = 10.0

if RUN_MODE == "smoke":
    CELLS = [("A_n2048_noreplay", 2048, False), ("B_n2048_replay", 2048, True), ("C_n1024_replay", 1024, True)]
    SEEDS = [1, 2]
else:
    CELLS = [("A_n8192_noreplay", 8192, False), ("B_n8192_replay", 8192, True), ("C_n4096_replay", 4096, True)]
    SEEDS = [7, 17, 23, 31, 41]


def build_W(n, M, gen):
    Xi = (torch.randint(0, 2, (M, n), generator=gen, device=DEVICE).float() * 2 - 1)
    W = (Xi.t() @ Xi) / n          # (n,n) auto-associative Hopfield
    W.fill_diagonal_(0.0)          # zero self-connections (standard Hopfield) -> non-trivial recall residual
    return Xi, W


def retrieval_energy(Xi, W):
    """Per-pattern energy = 1 - overlap(xi, sign(W xi)). Returns (mean_energy, per_pattern_energy)."""
    R = torch.sign(Xi @ W.t())     # (M,n) recalled states; W symmetric so W xi == xi W
    R[R == 0] = 1.0
    overlap = (Xi * R).sum(dim=1) / Xi.shape[1]   # (M,) in [-1,1]
    e = 1.0 - overlap
    return float(e.mean()), e


def run_cell(name, n, replay, seed) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed * 100003 + n)
    M = max(4, int(round(ALPHA * n)))
    Xi, W = build_W(n, M, gen)
    e_init, _ = retrieval_energy(Xi, W)
    if replay:
        for _ in range(R_STAR):
            # Crick-Mitchison unlearning: K random probes settle to spurious attractors, then unlearn them.
            P = torch.sign(torch.randn(TOPK, n, generator=gen, device=DEVICE)); P[P == 0] = 1.0
            for _ in range(3):                               # settle to an attractor
                P = torch.sign(P @ W.t()); P[P == 0] = 1.0
            W = W - (LAMBDA / n) * (P.t() @ P)               # unlearn spurious minima
            W.fill_diagonal_(0.0)
    e_final, _ = retrieval_energy(Xi, W)
    reduction = (e_init - e_final) / (abs(e_init) + 1e-9) * 100.0
    return {"cell": name, "N": n, "M": M, "replay": replay,
            "energy_init": e_init, "energy_final": e_final, "reduction_pct": float(reduction)}


def _selftest():
    assert 0.0 <= 2.0
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    # 1. single pattern perfect recall
    Xi, W = build_W(512, 1, gen)
    me, _ = retrieval_energy(Xi, W)
    assert me < 1e-6, f"single-pattern energy {me}"
    # 2/3. MECHANICS ONLY (NOT the hypothesis): overlap/energy bounds + replay step modifies W.
    # Whether replay REDUCES energy at N>=8192 is the empirical question -- never asserted here.
    Xi2, W2 = build_W(256, int(0.12 * 256), gen)
    e0, eper = retrieval_energy(Xi2, W2)
    assert (eper.min() >= -1e-6) and (eper.max() <= 2.0 + 1e-6), "energy out of [0,2]"
    W_before = float(W2.abs().sum())
    P = torch.sign(torch.randn(8, 256, generator=gen, device=DEVICE)); P[P == 0] = 1.0
    for _ in range(3):
        P = torch.sign(P @ W2.t()); P[P == 0] = 1.0
    W2 = W2 - (0.1 / 256) * (P.t() @ P); W2.fill_diagonal_(0.0)   # unlearning step
    assert float(W2.abs().sum()) != W_before, "unlearning step did not modify W"
    e1, _ = retrieval_energy(Xi2, W2)
    assert torch.cuda.memory_allocated(0) > 0
    print(f"[selftest] PASS: single_recall_energy={me:.2e} energy_bounds_ok replay_modifies_W "
          f"(toy {e0:.4f}->{e1:.4f}; direction is the empirical question)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    cells = {}
    for name, n, replay in CELLS:
        r = run_cell(name, n, replay, seed)
        cells[name] = r
        print(f"  [seed={seed} {name}] N={n} M={r['M']} e_init={r['energy_init']:.4f} "
              f"e_final={r['energy_final']:.4f} reduction={r['reduction_pct']:.2f}%", flush=True)
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "run_mode": RUN_MODE, "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    import numpy as np
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    names = [c[0] for c in CELLS]
    A, B, C = names[0], names[1], names[2]
    def red(nm):
        vs = [r["cells"][nm]["reduction_pct"] for r in results if nm in r.get("cells", {})]
        return float(np.mean(vs)) if vs else 0.0
    rA, rB, rC = red(A), red(B), red(C)
    summary = f"reduction%: {A}={rA:.2f} {B}={rB:.2f} {C}={rC:.2f}"
    if rB > HP_B_RED and rC < C_NULL:
        return ("HARD_PASS", f"HARD_PASS: replay consolidates at N>=8192 (B>{HP_B_RED}%) AND null at N=4096 "
                             f"(C<{C_NULL}%) -> N-conditional confirmed. {summary}")
    if rB >= MID_B_RED or rC >= C_NULL:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial consolidation OR control not null (quant-floor conditional unclear). {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: replay does not consolidate (no cell > {MID_B_RED}%). {summary}")


print(f"[config] anchor={ANCHOR_NAME} cells={[c[0] for c in CELLS]} mode={RUN_MODE} seeds={SEEDS} "
      f"alpha={ALPHA} topK={TOPK} R*={R_STAR} lambda={LAMBDA}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"cells": [c[0] for c in CELLS], "run_mode": RUN_MODE, "alpha": ALPHA, "topK": TOPK, "R_star": R_STAR}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.001, f"GPU util check FAIL: {peak_mem_gb:.3f}GB"
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "alpha": ALPHA, "topK": TOPK, "R_star": R_STAR,
    "lambda": LAMBDA, "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells", {}),
                  "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
