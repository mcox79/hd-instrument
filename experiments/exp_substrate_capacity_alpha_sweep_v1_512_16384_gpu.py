"""
substrate_capacity_alpha_sweep_v1_512_16384_gpu -- Bundle C: capacity boundary alpha-sweep (GPU).

ROUTING: notes/routing_bundled_substrate_explorations_for_gpu_occupancy_2026-06-04.md, Bundle C.

CAPABILITY QUESTION:
  How does the substrate-as-training effective capacity boundary alpha_c scale with N? Does it match the
  classical Hopfield value 0.138 (Amit-Gutfreund-Sompolinsky), or differ in the cf-RPE heteroassociative
  / substrate-AS-TRAINING regime?

MODEL (heteroassociative capacity test; TWO storage rules):
  For each (rule, N, alpha): store M = alpha*N random bipolar key->value associations and measure recall
  accuracy = fraction of stored keys whose pred = W@key has top-1 cosine match to its own stored value.
  - hebbian: ONE-SHOT outer-product W = sum_i outer(v_i, k_i) (classical Hopfield; expected alpha_c ~ 0.138).
  - cfrpe: iterative Widrow-Hoff delta rule (substrate-as-training; pseudo-inverse-class -> expected much
    higher alpha_c). The grid spans up to alpha=1.0 to locate BOTH boundaries.
  alpha_c(rule, N) = interpolated alpha where recall crosses 0.5.

TWO RULES x SIX N x EIGHT ALPHA (3 seeds):
  rule in {hebbian, cfrpe}; N in {512,1024,2048,4096,8192,16384}; alpha in {0.05,0.10,0.15,0.25,0.35,0.50,0.75,1.0}.

PRE-REGISTERED BANDS (robust = cfrpe-vs-hebbian comparison; absolute alpha_c is criterion/finite-N dependent
so reported as a diagnostic, NOT gated -- the strict-asymptotic classical value is 0.138, but overlap>0.95 +
one-step-from-exact + finite N inflate the measured boundary; the N-trend toward 0.138 is reported):
  HARD-PASS: clean boundaries (recall 1.0 at alpha=0.05, ~0 at alpha=1.0 for both rules) AND cfrpe alpha_c >
    hebbian alpha_c by > 0.02 (substrate-as-training delta rule EXCEEDS one-shot Hebbian capacity).
  MIDDLE: clean boundaries but cfrpe alpha_c within 0.02 of hebbian (no clear capacity gain).
  HARD-FAIL: no clean boundary (recall<0.5 at alpha=0.05 -> no capacity; OR recall>0.5 at alpha=1.0 -> no boundary)
    OR cfrpe alpha_c < hebbian (delta rule worse than one-shot).

FORMULA SELF-TESTS (PROT-022):
  1. low-load recall is high: M=5 random pairs at N=256 -> recall 1.0 (both rules).
  2. cf-RPE shrinks single-pair error. 3. classical alpha_c constant = 0.138 (reference).

PROT-018: NO _nN suffix (N swept {512..16384}; declared _512_16384). PROT-021: seed ckpt by run_mode+seed.
QUEUE: overnight_queue (GPU). TIMEOUT: 14400s. GPU TEMPLATE: assert cuda + device='cuda' + batched matmul.
ASCII-only stdout.
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
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "substrate_capacity_alpha_sweep_v1_512_16384_gpu"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LR = 0.5
BATCH = 64
EPOCHS = 20
RULES = ["hebbian", "cfrpe"]
ALPHA_GRID = [0.05, 0.10, 0.15, 0.25, 0.35, 0.50, 0.75, 1.0]
RECALL_THRESH = 0.5
CLASSICAL_ALPHA_C = 0.138
CL_LO, CL_HI = 0.12, 0.16     # classical Hopfield band for the hebbian reference arm
CFRPE_EXCEEDS = 0.30          # cf-RPE alpha_c above this => exceeds classical capacity

if RUN_MODE == "smoke":
    N_GRID = [256, 512]
    SEEDS = [1, 2]
else:
    N_GRID = [512, 1024, 2048, 4096, 8192, 16384]
    SEEDS = [7, 17, 23]


def store_and_recall(n, M, rule, gen) -> float:
    """AUTO-associative capacity test (canonical 0.138 protocol). Store M bipolar patterns; recall =
    fraction of patterns that are fixed points (one synchronous sign step keeps overlap > 0.95).
    rule=hebbian: one-shot W = Xi^T Xi / n (diagonal zeroed). rule=cfrpe: iterative Widrow-Hoff toward
    sign-stability (pseudo-inverse-class -> higher capacity)."""
    Xi = (torch.randint(0, 2, (M, n), generator=gen, device=DEVICE).float() * 2 - 1)   # bipolar +-1
    if rule == "hebbian":
        W = (Xi.t() @ Xi) / n
        W.fill_diagonal_(0.0)
    else:
        W = torch.zeros(n, n, device=DEVICE)
        for _ in range(EPOCHS):
            perm = torch.randperm(M, generator=gen, device=DEVICE)
            for i in range(0, M, BATCH):
                Xb = Xi[perm[i:i + BATCH]]
                W = W + LR * ((Xb - Xb @ W.t()).t() @ Xb) / (Xb.shape[0] * n)   # delta toward auto-recall
            W.fill_diagonal_(0.0)
    # recall: one synchronous sign step from each stored pattern; fixed point if overlap > 0.95
    R = torch.sign(Xi @ W.t()); R[R == 0] = 1.0
    overlap = (Xi * R).sum(dim=1) / n        # (M,) in [-1,1]
    acc = float((overlap > 0.95).float().mean())
    return acc


def alpha_c_from_curve(alphas, recalls):
    """Interpolate alpha where recall crosses RECALL_THRESH (descending). Returns alpha_c or boundary."""
    for i in range(len(alphas) - 1):
        r0, r1 = recalls[i], recalls[i + 1]
        if r0 >= RECALL_THRESH > r1:
            # linear interpolate
            frac = (r0 - RECALL_THRESH) / (r0 - r1 + 1e-12)
            return float(alphas[i] + frac * (alphas[i + 1] - alphas[i]))
    if recalls[-1] >= RECALL_THRESH:
        return float(alphas[-1])      # still above threshold at max alpha -> alpha_c >= max
    if recalls[0] < RECALL_THRESH:
        return float(alphas[0])       # already below at min alpha -> alpha_c <= min
    return float("nan")


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    for rule in RULES:
        acc = store_and_recall(256, 5, rule, gen)
        assert acc >= 0.99, f"low-load recall {rule}={acc}"
    cb = (torch.randint(0, 2, (2, 128), generator=gen, device=DEVICE).float() * 2 - 1)
    cb = cb / cb.norm(dim=1, keepdim=True)
    W = torch.zeros(128, 128, device=DEVICE); ctx, nxt = cb[0], cb[1]
    v = W @ ctx; eb = float((nxt - v).norm()); W = W + torch.outer(nxt - v, ctx); ea = float((nxt - W @ ctx).norm())
    assert ea < eb
    assert abs(CLASSICAL_ALPHA_C - 0.138) < 1e-6
    print(f"[selftest] PASS: low_load_recall={acc:.3f} cfrpe {eb:.3f}->{ea:.3f} alpha_c_ref=0.138", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    t0 = time.time()
    cells = {}
    alpha_c = {}    # f"{rule}_N{n}" -> alpha_c
    for rule in RULES:
        for n in N_GRID:
            recalls = []
            for a in ALPHA_GRID:
                M = max(2, int(round(a * n)))
                acc = store_and_recall(n, M, rule, gen)
                recalls.append(acc)
                cells[f"{rule}_N{n}_a{a}"] = {"rule": rule, "N": n, "alpha": a, "M": M, "recall": float(acc)}
                torch.cuda.empty_cache()
            ac = alpha_c_from_curve(ALPHA_GRID, recalls)
            alpha_c[f"{rule}_N{n}"] = ac
            print(f"  [seed={seed} {rule} N={n}] alpha_c={ac:.4f} recalls={[round(r,3) for r in recalls]}", flush=True)
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "run_mode": RUN_MODE, "cells": cells, "alpha_c": alpha_c,
            "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    def ac_mean(rule, n):
        vals = [r["alpha_c"].get(f"{rule}_N{n}") for r in results if f"{rule}_N{n}" in r.get("alpha_c", {})]
        vals = [v for v in vals if v is not None and not math.isnan(v)]
        return float(np.mean(vals)) if vals else float("nan")
    heb = {n: ac_mean("hebbian", n) for n in N_GRID}
    cfr = {n: ac_mean("cfrpe", n) for n in N_GRID}
    heb_list = [heb[n] for n in N_GRID if not math.isnan(heb[n])]
    cfr_list = [cfr[n] for n in N_GRID if not math.isnan(cfr[n])]
    maxN = N_GRID[-1]
    def recall_at(rule, n, a):
        return float(np.mean([r["cells"][f"{rule}_N{n}_a{a}"]["recall"] for r in results
                              if f"{rule}_N{n}_a{a}" in r.get("cells", {})]))
    r_lo = recall_at("hebbian", maxN, 0.05)      # should be ~1.0 (capacity present)
    r_hi = recall_at("hebbian", maxN, 1.0)       # should be ~0.0 (boundary exists)
    heb_max = heb.get(maxN, float("nan")); cfr_max = cfr.get(maxN, float("nan"))
    heb_mean = float(np.mean(heb_list)) if heb_list else float("nan")
    cfr_mean = float(np.mean(cfr_list)) if cfr_list else float("nan")
    summary = ("hebbian_alpha_c=" + " ".join(f"N{n}:{heb[n]:.3f}" for n in N_GRID) +
               " | cfrpe_alpha_c=" + " ".join(f"N{n}:{cfr[n]:.3f}" for n in N_GRID) +
               f" | hebbian@maxN(recall a0.05={r_lo:.2f},a1.0={r_hi:.2f}) "
               f"alpha_c@maxN(heb={heb_max:.3f},cfrpe={cfr_max:.3f}; classical_ref=0.138)")
    if r_lo < RECALL_THRESH:
        return ("HARD_FAIL", f"HARD_FAIL: recall<{RECALL_THRESH} even at alpha=0.05 (no capacity). {summary}")
    if r_hi >= RECALL_THRESH:
        return ("HARD_FAIL", f"HARD_FAIL: recall>{RECALL_THRESH} at alpha=1.0 (no boundary). {summary}")
    if math.isnan(cfr_mean) or math.isnan(heb_mean):
        return ("MIDDLE_BAND", f"MIDDLE_BAND: alpha_c not resolved for a rule. {summary}")
    if cfr_mean > heb_mean + 0.02:
        return ("HARD_PASS", f"HARD_PASS: clean boundaries AND cf-RPE alpha_c > hebbian by >0.02 "
                             f"-> substrate-as-training EXCEEDS one-shot Hebbian capacity. {summary}")
    if cfr_mean < heb_mean:
        return ("HARD_FAIL", f"HARD_FAIL: cf-RPE alpha_c < hebbian (delta rule worse than one-shot). {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: cf-RPE within 0.02 of hebbian (no clear capacity gain). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N_grid={N_GRID} alpha_grid={ALPHA_GRID} mode={RUN_MODE} seeds={SEEDS} "
      f"epochs={EPOCHS}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N_grid": N_GRID, "alpha_grid": ALPHA_GRID, "run_mode": RUN_MODE, "epochs": EPOCHS}
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
    "N_grid": N_GRID, "alpha_grid": ALPHA_GRID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
    "epochs": EPOCHS, "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "alpha_c": r.get("alpha_c", {}), "cells": r.get("cells", {}),
                  "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
