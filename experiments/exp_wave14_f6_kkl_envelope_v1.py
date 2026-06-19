"""F-6 Boolean KKL envelope expansion: broader density, N, codebook stress.

Context: v195 F-6 KKL probe HARD_PASS at density=0.10, N=256.
KKL_HARD_PASS_LOW_INFLUENCE: max_inf_share=0.052 (well below 0.30 fail band).
F-6 row moves 🔬 -> 🟡 candidate. Envelope expansion required before promotion
to 🟢 or ✅ per [[feedback-envelope-expansion-fail-bands]].

Expanded envelope:
- Densities: {0.10, 0.30, 0.50, 0.70} (from 2 to 4 density points; stressing
  high-density regime where substrate may exhibit junta-like behavior)
- N values: {64, 256, 1024} (from N=256 to broader range; KKL bound grows as
  log(n) so N=1024 is the stress point)
- Seeds: {7, 17, 23, 31, 41} (from 1 to 5 seeds)

Envelope-expansion pre-registration per [[feedback-envelope-expansion-fail-bands]]:
    The BROADER claim tested here is "substrate boundaries are low-influence/
    well-distributed ACROSS the operating envelope (density in {0.10..0.70},
    N in {64..1024})." This is stronger than v195 single-density single-N.

    HARD-PASS (broader envelope): max_inf_share <= 0.30 AND kkl_ratio >= 1.0
              at ALL (N, density) operating points (16/16 cells).
              -> F-6 row promoted 🟡 -> 🟢 (envelope validated).
    HARD-FAIL (broader envelope): max_inf_share >= 0.60 at >=2 operating
              points (substrate fails junta test under stress).
              -> F-6 row reverts 🟡 -> 🔬 (envelope-dependent; narrow scope).
    MIDDLE-BAND: any intermediate (some densities fail PASS, none fail HARD-FAIL).
              -> F-6 🟡 STAYS; annotate density envelope narrowing; report at
              which density/N the substrate's boundary structure degrades.
              Next probe: cleanup or density-conditioned threshold adjustment.

Self-test cells (per [[feedback-strategy-spec-formula-selftests]]):
    (max_inf_share=0.05, kkl_ratio=1.1, all cells) -> HARD_PASS
    (max_inf_share=0.65 at 2 cells) -> HARD_FAIL
    (max_inf_share=0.45 at 1 cell, 0.05 elsewhere) -> MIDDLE_BAND

Queue: local_cpu_queue (pure-numpy; fast; N<=1024; <60s expected).
ETA: ~20-45 sec local CPU.
Pre-reg file: preregs/2026-05-24_wave14_f6_kkl_envelope_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, json, math, os, time
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent

# ───── design parameters (exp_dev autonomy) ─────
N_VALUES_FULL = [64, 256, 1024]
N_VALUES_SMOKE = [64, 256]
DENSITIES_FULL = [0.10, 0.30, 0.50, 0.70]
DENSITIES_SMOKE = [0.10, 0.30]
N_SAMPLES = 500   # boundary-function evaluations per coordinate (local CPU, not too slow)
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Envelope-expansion thresholds (broader claim)
PASS_MAX_INF_SHARE = 0.30
PASS_KKL_RATIO = 1.0
FAIL_MAX_INF_SHARE = 0.60
FAIL_N_CELLS = 2  # fail if >= 2 cells fail


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def bsc_atoms(num: int, dim: int, rng: np.random.Generator) -> np.ndarray:
    """Generate BSC atoms: {-1, +1}^dim."""
    return rng.choice(np.array([-1.0, 1.0]), size=(num, dim)).astype(np.float32)


def run_one_cell(N: int, density: float, seed: int, n_samples: int) -> dict:
    """Run one (N, density) cell: measure per-coordinate influence."""
    rng = np.random.default_rng(seed)
    M_stored = max(1, int(density * N))

    # Build Hebbian weight matrix W
    atoms = bsc_atoms(M_stored, N, rng)   # stored items
    W = (atoms.T @ atoms).astype(np.float32)  # N x N

    # Pick a query item (first stored item)
    query_key = atoms[0]  # (N,)

    # Baseline output
    raw_0 = W @ query_key
    f_baseline = int(np.sign(raw_0[0] + 1e-9))  # output bit 0 as Boolean

    # Per-coordinate influence: flip coordinate i, measure fraction of output changes
    influences = np.zeros(N, dtype=np.float64)
    random_inputs = rng.choice(np.array([-1.0, 1.0]),
                               size=(n_samples, N)).astype(np.float32)
    # Vectorized: for each i, flip bit i in all samples, measure |f(x) - f(x_i)|/2
    baseline_outputs = np.sign(random_inputs @ W[0, :] + 1e-9)  # (n_samples,) using first output coord
    for i in range(N):
        flipped = random_inputs.copy()
        flipped[:, i] *= -1
        flipped_outputs = np.sign(flipped @ W[0, :] + 1e-9)
        # Influence_i = Pr[f changes when bit i flips] = mean(|baseline - flipped| / 2)
        influences[i] = float(np.mean(np.abs(baseline_outputs - flipped_outputs) / 2.0))

    inf_total = float(influences.sum())
    max_inf = float(influences.max())
    max_inf_share = max_inf / max(inf_total, 1e-9)

    # KKL ratio: Inf_total / (Var(f) * log(N))
    # Var(f) ~ mean f^2 - mean(f)^2; since f in {-1,+1}, Var = 1 - E[f]^2
    mean_f = float(baseline_outputs.mean())
    var_f = 1.0 - mean_f ** 2
    kkl_ratio = inf_total / max(var_f * math.log(max(N, 2)), 1e-9)

    return {"N": N, "density": density, "M_stored": M_stored,
            "inf_total": inf_total, "max_inf": max_inf,
            "max_inf_share": max_inf_share, "var_f": var_f,
            "kkl_ratio": kkl_ratio}


def compute_verdict(summary: dict) -> tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("F6_ENVELOPE_INCONCLUSIVE", "No cells evaluated.")

    n_fail_hard = sum(1 for c in cells if c["max_inf_share"] >= FAIL_MAX_INF_SHARE)
    n_pass_all = sum(1 for c in cells
                     if c["max_inf_share"] <= PASS_MAX_INF_SHARE and
                        c["kkl_ratio"] >= PASS_KKL_RATIO)
    n_cells = len(cells)

    cell_summary = " | ".join(
        f"N={c['N']},d={c['density']:.2f}:share={c['max_inf_share']:.3f},kkl={c['kkl_ratio']:.3f}"
        for c in cells)

    if n_fail_hard >= FAIL_N_CELLS:
        return ("F6_ENVELOPE_HARD_FAIL",
                f"Envelope FAILS: {n_fail_hard} cells with max_inf_share>={FAIL_MAX_INF_SHARE}. "
                f"Substrate boundary junta-like at high density. "
                f"F-6 row reverts 🟡 -> 🔬. Cells: {cell_summary}.")
    if n_pass_all == n_cells:
        return ("F6_ENVELOPE_HARD_PASS",
                f"Envelope HOLDS at ALL {n_cells} operating points: "
                f"max_inf_share<={PASS_MAX_INF_SHARE} AND kkl_ratio>={PASS_KKL_RATIO} everywhere. "
                f"F-6 row promoted 🟡 -> 🟢. Cells: {cell_summary}.")
    return ("F6_ENVELOPE_MIDDLE_BAND",
            f"Partial envelope: {n_pass_all}/{n_cells} cells pass full criteria; "
            f"{n_fail_hard} hard-fail cells. "
            f"F-6 stays 🟡 with density-envelope narrowing annotation. Cells: {cell_summary}.")


def self_test_verdict():
    """Self-test: verify verdict logic with (input -> expected output) pairs."""
    def mk(*cell_tuples):
        cells = []
        for (N, d, share, kkl) in cell_tuples:
            cells.append({"N": N, "density": d, "max_inf_share": share,
                          "kkl_ratio": kkl, "inf_total": 1.0, "var_f": 0.5})
        return {"cells": cells}

    # HARD_PASS: all cells under threshold
    s_pass = mk((64, 0.10, 0.05, 1.1), (256, 0.10, 0.06, 1.2),
                (64, 0.30, 0.08, 1.05), (256, 0.30, 0.10, 1.01))
    # HARD_FAIL: 2 cells fail
    s_fail = mk((64, 0.10, 0.65, 0.8), (256, 0.10, 0.70, 0.5),
                (64, 0.30, 0.10, 1.2), (256, 0.30, 0.12, 1.1))
    # MIDDLE: 1 cell fails hard, others pass
    s_mid = mk((64, 0.10, 0.65, 0.8), (256, 0.10, 0.10, 1.2),
               (64, 0.30, 0.45, 1.05), (256, 0.30, 0.12, 1.1))
    # INCONCLUSIVE
    s_inconc = {"cells": []}

    cases = [
        (s_pass, "F6_ENVELOPE_HARD_PASS"),
        (s_fail, "F6_ENVELOPE_HARD_FAIL"),
        (s_mid, "F6_ENVELOPE_MIDDLE_BAND"),
        (s_inconc, "F6_ENVELOPE_INCONCLUSIVE"),
    ]
    for summary, expected in cases:
        v, msg = compute_verdict(summary)
        if v != expected:
            raise AssertionError(f"Expected {expected}, got {v}. msg={msg}")
    print(f"self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool) -> tuple:
    t0 = time.monotonic()
    N_values = N_VALUES_SMOKE if smoke else N_VALUES_FULL
    densities = DENSITIES_SMOKE if smoke else DENSITIES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    config = {"mode": "smoke" if smoke else "full",
              "N_values": N_values, "densities": densities,
              "n_samples": N_SAMPLES, "seeds": seeds,
              "pass_max_inf_share": PASS_MAX_INF_SHARE,
              "pass_kkl_ratio": PASS_KKL_RATIO,
              "fail_max_inf_share": FAIL_MAX_INF_SHARE,
              "fail_n_cells": FAIL_N_CELLS}
    print(f"[config] {config}", flush=True)

    cells = []
    for N in N_values:
        for density in densities:
            cell_results = []
            for seed in seeds:
                r = run_one_cell(N, density, seed, N_SAMPLES)
                cell_results.append(r)
            # Aggregate across seeds
            mean_share = sum(r["max_inf_share"] for r in cell_results) / len(cell_results)
            mean_kkl = sum(r["kkl_ratio"] for r in cell_results) / len(cell_results)
            mean_inf_total = sum(r["inf_total"] for r in cell_results) / len(cell_results)
            agg = {"N": N, "density": density,
                   "M_stored": int(density * N),
                   "max_inf_share": mean_share, "kkl_ratio": mean_kkl,
                   "inf_total": mean_inf_total, "n_seeds": len(seeds)}
            cells.append(agg)
            pass_fail = ("PASS" if mean_share <= PASS_MAX_INF_SHARE and mean_kkl >= PASS_KKL_RATIO
                         else ("HARD_FAIL" if mean_share >= FAIL_MAX_INF_SHARE else "MIDDLE"))
            print(f"  N={N} density={density:.2f}: share={mean_share:.3f} "
                  f"kkl={mean_kkl:.3f} -> {pass_fail}", flush=True)

    summary = {"cells": cells}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    out_name = ("wave14_f6_kkl_envelope_v1_smoke" if args.smoke
                else "wave14_f6_kkl_envelope_v1")
    out_dir = get_output_dir(out_name)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\n{'SMOKE' if args.smoke else 'DONE'}: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
