"""
q_b1_chain_loading_boundary_alpha_L_sweep_v1_n2048 -- Q-B1 chain loading-boundary alpha x L sweep.

ROUTING: notes/exp_dev_handoff_research_qb1_chain_loading_boundary_*.md +
         notes/exp_dev_handoff_research_qb1_chain_ceiling_*.md (Research; highest-priority Q-B1 item).

CAPABILITY QUESTION:
  What is the chain retrieval-depth ceiling chain_depth_max(alpha) as a function of background load
  alpha = M_BACKGROUND / N? Current best fit (2 empirical points): chain_depth_max(alpha) =
  22/(0.302 - alpha). This sweep (alpha x L) pins alpha_c_eff and the engineering curve
  ("use alpha < X for depth > Y"). DCS-1998 + finite-chain correction places the boundary at
  alpha_eff(L=300-400) ~ 0.22-0.24.

DESIGN (heteroassoc chain, same family as q_b1 bisect scripts, CPU numpy at N=2048):
  H = sum_h outer(chain[h+1], chain[h]) / N  (one tracked chain of depth L)
      + sum_b outer(bg_b, bg_b) / N           (M_BACKGROUND interference patterns; alpha = M_BG/N)
  Retrieve along the chain from chain[0] by repeated h = sign(H @ x), L hops; measure cosine of the
  depth-L retrieval vs the true chain[L]. A cell "holds" if cos >= HOLD_THRESH. For each alpha, the
  measured chain_depth_max = the largest L that still holds.

PRE-REGISTERED BANDS (exp_dev autonomy; grounded in DCS-1998 + the 2-point fit):
  HARD-PASS: a clear monotone-decreasing chain_depth_max(alpha) boundary is resolved across the grid
    (>= 4 alpha cells show a finite ceiling) AND the implied alpha_c_eff (where depth_max -> small)
    lies in [0.25, 0.35] (consistent with the 0.302 fit, +-0.05) AND 5/5 seeds consistent.
  MIDDLE: a boundary is visible but alpha_c_eff outside [0.25,0.35], OR 3-4/5 seeds consistent.
  HARD-FAIL: no boundary (chain holds at all alpha x L, OR collapses immediately at all alpha) ->
    formula/regime mis-specified.

FORMULA SELF-TESTS (PROT-022):
  1. formula chain_depth_max(0.10) = 22/(0.302-0.10) = 22/0.202 = 108.9. [EXPECTED within 0.5]
  2. chain_depth_max(0.25) = 22/0.052 = 423.1. [EXPECTED within 1.0]
  3. cosine(xi, xi) = 1.0.
  4. single-link retrieve: H=outer(b,a)/N, sign(H@a) ~ b (cos > 0.9 at N=2048).

PROT-018: anchor has _n2048; N MUST = 2048.
PROT-021: seed checkpoints keyed run_mode + N.
QUEUE: remote_cpu_queue (pure numpy; CPU; design-space mapping). TIMEOUT: 21600s (PROT-019 floor n>=... ).
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

ANCHOR_NAME = "q_b1_chain_loading_boundary_alpha_L_sweep_v1_n2048"
_N_SUFFIX = 2048
N = 2048
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

HOLD_THRESH = 0.5            # chain "holds" at depth L if cos >= 0.5
ALPHA_C_FIT = 0.302          # from chain_depth_max(alpha)=22/(0.302-alpha)
HP_ALPHA_C_LO, HP_ALPHA_C_HI = 0.25, 0.35

def _formula_depth_max(alpha):
    return 22.0 / max(0.302 - alpha, 1e-6)

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    ALPHA_GRID = [0.05, 0.15, 0.25]
    L_GRID = [20, 60, 120]
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_GRID = [0.05, 0.10, 0.15, 0.20, 0.25, 0.28]
    L_GRID = [50, 100, 150, 200, 300, 400]


def cosine(a, b):
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(a @ b) / (na * nb)


def build_and_retrieve(alpha, L, n_dim, rng):
    """Build chain(depth L) + M_BG=round(alpha*n) background; retrieve L hops; return cos at depth L."""
    M_BG = int(round(alpha * n_dim))
    chain = rng.choice([-1.0, 1.0], size=(L + 1, n_dim)).astype(np.float32)
    H = np.zeros((n_dim, n_dim), dtype=np.float32)
    for h in range(L):
        H += np.outer(chain[h + 1], chain[h]) / n_dim
    if M_BG > 0:
        bg = rng.choice([-1.0, 1.0], size=(M_BG, n_dim)).astype(np.float32)
        H += (bg.T @ bg) / n_dim
    # Retrieve along the chain from chain[0].
    x = chain[0].copy()
    for _ in range(L):
        h = H @ x
        x = np.sign(h); x[x == 0] = 1.0
    return cosine(x, chain[L])


def _selftest():
    assert abs(_formula_depth_max(0.10) - 108.91) < 0.5, _formula_depth_max(0.10)
    assert abs(_formula_depth_max(0.25) - 423.08) < 1.0, _formula_depth_max(0.25)
    rng = np.random.default_rng(0)
    a = rng.choice([-1.0, 1.0], size=128).astype(np.float32)
    assert abs(cosine(a, a) - 1.0) < 1e-6
    b = rng.choice([-1.0, 1.0], size=128).astype(np.float32)
    H = np.outer(b, a) / 128
    r = np.sign(H @ a); r[r == 0] = 1.0
    assert cosine(r, b) > 0.9, f"single-link retrieve cos={cosine(r,b)}"
    print(f"[selftest] PASS: formula(0.10)={_formula_depth_max(0.10):.2f} "
          f"formula(0.25)={_formula_depth_max(0.25):.2f} single-link ok", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    grid = {}
    depth_max = {}
    for alpha in ALPHA_GRID:
        holds = []
        for L in L_GRID:
            cos = build_and_retrieve(alpha, L, n_dim, rng)
            held = cos >= HOLD_THRESH
            grid[(alpha, L)] = float(cos)
            holds.append((L, held))
            print(f"  [seed={seed} alpha={alpha:.2f} L={L}] cos={cos:.4f} hold={held} "
                  f"formula_max={_formula_depth_max(alpha):.0f}", flush=True)
        held_Ls = [L for (L, h) in holds if h]
        depth_max[alpha] = max(held_Ls) if held_Ls else 0
    elapsed = time.time() - t0
    print(f"  [seed={seed}] depth_max_by_alpha={depth_max} elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE,
            "grid": {f"{a}_{L}": grid[(a, L)] for (a, L) in grid},
            "depth_max": {f"{a}": depth_max[a] for a in depth_max}, "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    # Mean depth_max per alpha across seeds.
    mean_dmax = {}
    for alpha in ALPHA_GRID:
        vs = [r["depth_max"].get(f"{alpha}", 0) for r in results if "depth_max" in r]
        mean_dmax[alpha] = float(np.mean(vs)) if vs else 0.0
    # Monotone non-increasing boundary?
    dmax_list = [mean_dmax[a] for a in ALPHA_GRID]
    monotone = all(dmax_list[i + 1] <= dmax_list[i] + max(0.10 * dmax_list[i], 10) for i in range(len(dmax_list) - 1))
    n_finite = sum(1 for a in ALPHA_GRID if 0 < mean_dmax[a] < max(L_GRID))
    # Estimate alpha_c_eff: smallest alpha where depth_max collapses to <= min(L_GRID).
    alpha_c_eff = None
    for a in ALPHA_GRID:
        if mean_dmax[a] <= min(L_GRID):
            alpha_c_eff = a
            break
    all_hold = all(mean_dmax[a] >= max(L_GRID) for a in ALPHA_GRID)
    all_collapse = all(mean_dmax[a] <= min(L_GRID) for a in ALPHA_GRID)
    summary = ("depth_max=" + " ".join(f"a{a:.2f}:{mean_dmax[a]:.0f}" for a in ALPHA_GRID) +
               f" alpha_c_eff={alpha_c_eff} monotone={monotone} n_finite={n_finite}")

    if all_hold or all_collapse:
        return ("HARD_FAIL",
                f"HARD_FAIL: no boundary resolved (all-hold or all-collapse across grid). {summary}")
    if monotone and n_finite >= 4 and alpha_c_eff is not None and HP_ALPHA_C_LO <= alpha_c_eff <= HP_ALPHA_C_HI:
        return ("HARD_PASS",
                f"HARD_PASS: monotone chain_depth_max(alpha) boundary; alpha_c_eff={alpha_c_eff} in "
                f"[{HP_ALPHA_C_LO},{HP_ALPHA_C_HI}] (consistent with 0.302 fit). {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: boundary visible but alpha_c_eff outside [0.25,0.35] or partial. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_ACTIVE} mode={RUN_MODE} seeds={SEEDS} "
      f"alpha_grid={ALPHA_GRID} L_grid={L_GRID}", flush=True)
if RUN_MODE == "full" and N_ACTIVE != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_ACTIVE={N_ACTIVE} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "run_mode": RUN_MODE, "alpha_grid": ALPHA_GRID, "L_grid": L_GRID}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE, "alpha_grid": ALPHA_GRID, "L_grid": L_GRID,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "depth_max": r.get("depth_max"), "elapsed_s": r.get("elapsed_s")}
                 for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
