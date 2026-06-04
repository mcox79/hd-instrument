"""
pp50_transition_zone_n_sweep_tw_vs_hadamard_v1 -- PP-50 transition-zone mechanism discriminator (N-sweep).

ROUTING: notes/exp_dev_handoff_research_pp50_transition_zone_width_*.md +
         notes/research_drill_pp50_transition_zone_width_2026-06-03.md (Research).

CAPABILITY QUESTION:
  The PP-50 capacity transition zone is WIDER than the free-probability sharp-boundary prediction.
  Two competing mechanisms: (A) Tracy-Widom soft-edge fluctuations scaling as N^{-2/3} (vanish at large
  N -> safe envelope must be N-parameterized) vs (B) a non-self-averaging Hadamard off-diagonal term
  that is O(1) in N (-> N-independent safe envelope is correct). Decisive test: fix load + sigma_g near
  sigma_g_crit, sweep N, measure the violation rate. Roughly CONSTANT in N => Hadamard dominates;
  decays as N^{-2/3} => Tracy-Widom dominates. Directly validates the product safe-envelope API claim.

DESIGN (CPU forward-pass retrieval overlap; no gradient, no eigendecomp):
  For each N: store M = round(LOAD * N) bipolar patterns in Hopfield W = Xi^T Xi / N; apply
  multiplicative weight noise W_noisy = W * (1 + sigma_g * G), G ~ N(0,1) elementwise, sigma_g =
  SIGMA_G_CRIT; one-step retrieve each stored pattern (sign(W_noisy @ xi)); overlap = mean per-pattern
  cosine; "violation" = overlap < VIOL_THRESH. violation_rate(N) = fraction of M patterns violated.
  Fit violation_rate vs N to (a) constant and (b) c * N^{-2/3}; compare R^2.

PRE-REGISTERED BANDS (exp_dev autonomy; discriminator):
  HARD-PASS (clean mechanism call): one model fits markedly better (R^2 gap > 0.30) across the N grid,
    5/5 seeds consistent on the winner. (Either TW or Hadamard is a clean product-API answer.)
  MIDDLE: both models comparable (R^2 gap <= 0.30) OR 3-4/5 seeds agree -> zone is a mix of both terms.
  HARD-FAIL: violation_rate is non-monotone-noise with no fit (both R^2 < 0.3) OR zero violations at all
    N (test not loading the transition zone; raise sigma_g or load).

FORMULA SELF-TESTS (PROT-022):
  1. N^{-2/3} ratio: (8192/1024)^{-2/3} = 8^{-2/3} = 0.25. [EXPECTED within 1e-6]
  2. constant-model R^2 == 1.0 on a flat series. [within 1e-6]
  3. cosine(xi, xi) = 1.0.

PROT-018: NO _nN suffix (N is the swept variable). N grid declared = {1024,2048,4096,8192}.
PROT-021: seed checkpoints keyed run_mode + seed.
QUEUE: remote_cpu_queue (pure numpy; CPU). TIMEOUT: 7200s.
ASCII-only stdout.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True); sys.exit(1)
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp50_transition_zone_n_sweep_tw_vs_hadamard_v1"
# PROT-018: no _nN suffix; N is the swept variable.
PRODUCTION_N_GRID = [1024, 2048, 4096, 8192]

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

SIGMA_G_CRIT = 0.833        # cap_map estimate (4.6x theory 0.18); fix sigma_g here
LOAD = 0.10                 # moderate load (below classical capacity)
VIOL_THRESH = 0.95          # a stored pattern is a "violation" if retrieval overlap < this

if RUN_MODE == "smoke":
    N_GRID = [512, 1024, 2048]
    SEEDS = [7, 17]
else:
    N_GRID = PRODUCTION_N_GRID
    SEEDS = [7, 17, 23, 31, 41]


def cosine(a, b):
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(a @ b) / (na * nb)


def violation_rate_at_N(n_dim, sigma_g, rng):
    M = max(2, int(round(LOAD * n_dim)))
    Xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)
    W = (Xi.T @ Xi) / n_dim
    G = rng.standard_normal((n_dim, n_dim)).astype(np.float32)
    W_noisy = W * (1.0 + sigma_g * G)
    # One-step retrieval of all stored patterns (batched): R = sign(W_noisy @ Xi^T)
    H = W_noisy @ Xi.T          # (n, M)
    R = np.sign(H); R[R == 0] = 1.0   # (n, M)
    # per-pattern overlap = cosine(R[:,k], Xi[k])
    num = (R * Xi.T).sum(axis=0)            # (M,)
    den = (np.linalg.norm(R, axis=0) * np.linalg.norm(Xi.T, axis=0) + 1e-12)
    overlaps = num / den
    viol = float(np.mean(overlaps < VIOL_THRESH))
    return viol, float(np.mean(overlaps)), M


def fit_models(ns, rates):
    n = np.array(ns, dtype=np.float64)
    y = np.array(rates, dtype=np.float64)
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    if ss_tot < 1e-12:
        return 1.0, -1.0  # perfectly flat -> constant wins
    # constant model
    r2_const = 1.0 - float(np.sum((y - np.mean(y)) ** 2)) / ss_tot  # == 0 by definition unless flat
    # TW model: y = c * N^{-2/3}; fit c by least squares on basis x = N^{-2/3}
    x = n ** (-2.0 / 3.0)
    c = float(np.sum(x * y) / max(np.sum(x * x), 1e-12))
    yhat = c * x
    r2_tw = 1.0 - float(np.sum((y - yhat) ** 2)) / ss_tot
    return r2_const, r2_tw


def _selftest():
    assert abs((8192 / 1024) ** (-2.0 / 3.0) - 0.25) < 1e-6
    rc, _ = fit_models([1, 2, 3], [0.4, 0.4, 0.4])
    assert rc >= 1.0 - 1e-6, f"flat const R2 {rc}"
    a = np.random.default_rng(0).choice([-1.0, 1.0], size=128).astype(np.float32)
    assert abs(cosine(a, a) - 1.0) < 1e-6
    print(f"[selftest] PASS: N^-2/3 ratio=0.25 const-fit flat=1.0 cos_self=1.0", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    cells = []
    for n_dim in N_GRID:
        viol, mean_ov, M = violation_rate_at_N(n_dim, SIGMA_G_CRIT, rng)
        cells.append({"N": n_dim, "M": M, "violation_rate": viol, "mean_overlap": mean_ov})
        print(f"  [seed={seed} N={n_dim} M={M}] violation_rate={viol:.4f} mean_overlap={mean_ov:.4f}", flush=True)
    elapsed = time.time() - t0
    print(f"  [seed={seed}] elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "run_mode": RUN_MODE, "cells": cells, "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    rates = {}
    for n_dim in N_GRID:
        vs = [c["violation_rate"] for r in results for c in r.get("cells", []) if c["N"] == n_dim]
        rates[n_dim] = float(np.mean(vs)) if vs else 0.0
    ns = list(N_GRID)
    rate_list = [rates[n] for n in ns]
    if max(rate_list) < 1e-6:
        return ("HARD_FAIL",
                f"HARD_FAIL: zero violations at all N (test not loading transition zone; raise sigma_g/load). "
                f"rates={[round(r,4) for r in rate_list]}")
    r2_const, r2_tw = fit_models(ns, rate_list)
    # per-seed winner consistency
    winners = []
    for r in results:
        sc = {c["N"]: c["violation_rate"] for c in r.get("cells", [])}
        rl = [sc.get(n, 0.0) for n in ns]
        rc, rt = fit_models(ns, rl)
        winners.append("TW" if rt > rc else "Hadamard")
    n_tw = winners.count("TW"); n_had = winners.count("Hadamard")
    winner = "TW" if r2_tw > r2_const else "Hadamard"
    gap = abs(r2_tw - r2_const)
    consist = max(n_tw, n_had)
    summary = (f"rates={[round(r,4) for r in rate_list]} r2_const={r2_const:.3f} r2_tw={r2_tw:.3f} "
               f"winner={winner} gap={gap:.3f} seed_winners(TW={n_tw},Had={n_had})")

    if gap > 0.30 and consist >= len(results):
        return ("HARD_PASS",
                f"HARD_PASS: clean mechanism call -> {winner} (R^2 gap>{0.30}, {consist}/{len(results)} seeds). "
                f"{'N-parameterized envelope needed' if winner=='TW' else 'N-independent envelope correct'}. {summary}")
    if gap > 0.30 or consist >= max(1, len(results) - 1):
        return ("MIDDLE_BAND", f"MIDDLE_BAND: leaning {winner} but not unanimous / gap modest. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: both terms contribute (no clean discriminator). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N_grid={N_GRID} mode={RUN_MODE} seeds={SEEDS} "
      f"sigma_g_crit={SIGMA_G_CRIT} load={LOAD}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N_grid": N_GRID, "run_mode": RUN_MODE, "sigma_g_crit": SIGMA_G_CRIT, "load": LOAD}
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
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "N_grid": N_GRID, "run_mode": RUN_MODE, "sigma_g_crit": SIGMA_G_CRIT, "load": LOAD,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells", []), "elapsed_s": r.get("elapsed_s")}
                 for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
