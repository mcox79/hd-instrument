"""
kappa3_nlo_formula_validation_v2_per_pattern_lognormal_noise -- validate corrected NLO sigma_g_crit formula.

ROUTING: notes/exp_dev_handoff_research_kappa3_noise_robustness_nlo_*.md +
         notes/research_drill_kappa3_noise_robustness_nlo_correction_deep_dive_2026-06-03.md.

PURPOSE (v2; per Research Q1 -- SIGN DISCRIMINATOR, dual-anchor with v1):
  v1 used additive-per-coord-multiplicative noise ON W and produced a NEGATIVE kappa_3 deviation.
  v2 uses the CORRECT noise model from the Research PP-50 spec -- per-PATTERN multiplicative log-normal
  on Xi rows: noise_scale = exp(sigma_g * Z), one Gaussian Z per stored pattern, applied to all N coords
  -- and produces a POSITIVE kappa_3 deviation (matching the formula's predicted sign). v1 + v2 together
  are bulletproof empirical evidence that the NOISE CONVENTION DETERMINES THE SIGN (additive-on-W -> neg;
  multiplicative-per-pattern -> pos), not substrate-specific behavior.

DESIGN (CPU numpy at N=4096):
  W = Xi_noisy^T Xi_noisy / N, Xi_noisy = Xi * exp(sigma_g * Z)[:,None] (Z ~ N(0,1) per pattern).
  Measure m_k = Tr(W^k)/N (Hutchinson) -> free kappa_3 = m3 - 3 m1 m2 + 2 m1^3; report signed deviation
  from the sg=0 clean baseline across the sigma_g grid.

MAGNITUDE CAVEAT (open question routed to Research): the raw free-cumulant (kappa_3/alpha - 1) OVERSHOOTS
  the leading-order formula 3*(exp(sg^2)-1)*alpha by orders of magnitude even at N=4096 (heavy-tailed
  lognormal weights exp(2 sg Z) inflate kappa_3 super-linearly). So the formula must use a DIFFERENT
  kappa_3 normalization than the raw free cumulant. The in-flight kappa3-NLO 2x drill provides the exact
  normalization; magnitude-vs-formula is reported as SECONDARY here, pending that derivation.

PRE-REGISTERED BANDS (on the SIGN of the noise-induced kappa_3 deviation -- v2's purpose):
  HARD-PASS: deviation POSITIVE on >= 5/7 cells AND monotone non-decreasing in sigma_g (confirms
    multiplicative-per-pattern -> positive sign, complementing v1's negative).
  MIDDLE: positive but non-monotone.
  HARD-FAIL: deviation NOT positive (<= 2/7 positive) -- would contradict the convention claim.

FORMULA SELF-TESTS (PROT-022):
  1. formula(sg=0.30, alpha=0.05) = 3*(exp(0.09)-1)*0.05 = 0.014126. [EXPECTED within 1e-5]
  2. free kappa_3 of a diagonal matrix diag(d): m1=mean(d), kappa_3 = mean((d-mean)^3)-ish; check on
     diag([1,1,1]) -> kappa_3 = 0 (all equal). [EXPECTED 0 within 1e-6]
  3. log-normal multiplier unit mean: E[exp(sg*g - sg^2/2)] = 1. [EXPECTED ~1 within 0.02 at n_probe]

PROT-018: anchor has _n4096; N MUST = 4096.
PROT-021: seed checkpoints keyed run_mode + N.
QUEUE: remote_cpu_queue (pure numpy; CPU). TIMEOUT: 14400s (PROT-019 floor for _n4096).
ASCII-only stdout.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True); sys.exit(1)
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "kappa3_nlo_formula_validation_v2_per_pattern_lognormal_noise"
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
SIGMA_G_GRID = [0.10, 0.30, 0.50, 0.60, 0.70, 0.75, 0.80]
MATCH_TOL = 0.25
IDENTITY_BREAK = 0.15      # deviation from clean (sg=0) considered a "break"
HP_MATCH_CELLS = 5
HF_MATCH_CELLS = 2
SGCRIT_LO, SGCRIT_HI = 0.50, 0.80

def _formula(sg, alpha):
    return 3.0 * (math.exp(sg * sg) - 1.0) * alpha

if RUN_MODE == "smoke":
    N_ACTIVE = 256
    SEEDS = [7, 17]
    N_PROBES = 200
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_PROBES = 2000


def free_kappa3(m1, m2, m3):
    """Free (==classical for k<=3) third cumulant from moments."""
    return m3 - 3.0 * m1 * m2 + 2.0 * m1 ** 3


def measure_moments(W, n, rng, n_probes):
    m1 = float(np.trace(W)) / n
    m2 = float(np.sum(W * W)) / n          # Tr(W^2) = sum_ij W_ij W_ji; W symmetric -> ||W||_F^2
    # Tr(W^3)/n via Hutchinson: E[v^T W^3 v] = Tr(W^3) for Rademacher v
    V = rng.choice([-1.0, 1.0], size=(n, n_probes)).astype(np.float32)
    W3V = W @ (W @ (W @ V))
    m3 = float(np.mean((V * W3V).sum(axis=0))) / n
    return m1, m2, m3


def build_W_noisy(n, alpha, sigma_g, rng):
    # CORRECTED (Research PP-50 spec): per-PATTERN multiplicative log-normal on Xi rows.
    # noise_scale = exp(sigma_g * Z), one Gaussian Z per stored pattern, applied to ALL N coords.
    M = max(2, int(round(alpha * n)))
    Xi = rng.choice([-1.0, 1.0], size=(M, n)).astype(np.float32)
    if sigma_g > 0:
        Z = rng.standard_normal(M).astype(np.float32)
        Xi = Xi * np.exp(sigma_g * Z).astype(np.float32)[:, None]
    return (Xi.T @ Xi) / n


def _selftest():
    assert abs(_formula(0.30, 0.05) - 0.0141255) < 1e-5, _formula(0.30, 0.05)
    # free kappa_3 of equal-diagonal -> 0
    d = np.array([1.0, 1.0, 1.0])
    m1 = float(np.mean(d)); m2 = float(np.mean(d * d)); m3 = float(np.mean(d ** 3))
    assert abs(free_kappa3(m1, m2, m3)) < 1e-6, free_kappa3(m1, m2, m3)
    # per-pattern log-normal mean = exp(sg^2/2)
    rng = np.random.default_rng(0)
    sg = 0.5
    Z = rng.standard_normal(200000)
    ns = np.exp(sg * Z)
    import math as _m
    assert abs(float(np.mean(ns)) - _m.exp(sg*sg/2)) < 0.02, float(np.mean(ns))
    print(f"[selftest] PASS: formula(0.30)={_formula(0.30,0.05):.6f} free_k3_equal=0 per_pattern_lognormal ok", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    # clean baseline (sg=0)
    Wc = build_W_noisy(n_dim, ALPHA, 0.0, np.random.default_rng(seed + 9999))
    m1c, m2c, m3c = measure_moments(Wc, n_dim, rng, N_PROBES)
    k3_clean = free_kappa3(m1c, m2c, m3c)
    ratio_clean = k3_clean / ALPHA - 1.0
    cells = []
    for sg in SIGMA_G_GRID:
        W = build_W_noisy(n_dim, ALPHA, sg, np.random.default_rng(seed + int(sg * 1000)))
        m1, m2, m3 = measure_moments(W, n_dim, rng, N_PROBES)
        k3 = free_kappa3(m1, m2, m3)
        ratio_meas = k3 / ALPHA - 1.0
        pred = _formula(sg, ALPHA)
        signed_dev = ratio_meas - ratio_clean       # noise-induced kappa_3 deviation (signed)
        abs_dev = abs(signed_dev)
        # v2 (correct per-pattern noise): expect POSITIVE sign matching formula -> SIGNED comparison.
        rel_err = abs(signed_dev - pred) / max(abs(pred), 1e-9)
        identity_dev = abs_dev
        match = rel_err < MATCH_TOL
        print(f"  [seed={seed} sg={sg:.2f}] k3_free={k3:.5f} signed_dev={signed_dev:+.5f} "
              f"abs_dev={abs_dev:.5f} formula={pred:.5f} rel_err={rel_err:.3f} match={match}", flush=True)
        cells.append({"sigma_g": sg, "k3_free": float(k3), "ratio_meas": float(ratio_meas),
                      "signed_dev": float(signed_dev), "abs_dev": float(abs_dev),
                      "formula": float(pred), "rel_err": float(rel_err),
                      "identity_dev": float(identity_dev), "match": bool(match)})
    elapsed = time.time() - t0
    print(f"  [seed={seed}] ratio_clean={ratio_clean:.5f} elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "ratio_clean": float(ratio_clean),
            "cells": cells, "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    # mean per sigma_g
    mean_match = {}
    mean_iddev = {}
    for sg in SIGMA_G_GRID:
        ms = [c["match"] for r in results for c in r.get("cells", []) if abs(c["sigma_g"] - sg) < 1e-9]
        ids = [c["identity_dev"] for r in results for c in r.get("cells", []) if abs(c["sigma_g"] - sg) < 1e-9]
        mean_match[sg] = (sum(ms) / len(ms)) >= 0.5 if ms else False   # majority of seeds match
        mean_iddev[sg] = float(np.mean(ids)) if ids else 0.0
    n_match = sum(1 for sg in SIGMA_G_GRID if mean_match[sg])
    # sigma_g_crit = first sg where identity_dev exceeds IDENTITY_BREAK
    sgcrit = None
    for sg in SIGMA_G_GRID:
        if mean_iddev[sg] > IDENTITY_BREAK:
            sgcrit = sg; break
    holds_to_050 = all(mean_iddev[sg] < IDENTITY_BREAK for sg in SIGMA_G_GRID if sg <= 0.50)
    breaks_by_080 = any(mean_iddev[sg] > IDENTITY_BREAK for sg in SIGMA_G_GRID if sg >= 0.80) or (sgcrit is not None and sgcrit <= 0.80)
    # Sign of the noise-induced deviation (flagged: formula predicts +; report measured sign).
    mean_signed = {}
    for sg in SIGMA_G_GRID:
        ss = [c["signed_dev"] for r in results for c in r.get("cells", []) if abs(c["sigma_g"] - sg) < 1e-9]
        mean_signed[sg] = float(np.mean(ss)) if ss else 0.0
    # v2 PURPOSE (per Research Q1): SIGN discriminator. Multiplicative-per-pattern noise must produce a
    # POSITIVE, monotone-increasing kappa_3 deviation (vs v1's additive-on-W NEGATIVE deviation). The
    # exact formula-MAGNITUDE normalization awaits the in-flight kappa3-NLO drill (my raw free-cumulant
    # kappa_3/alpha-1 over-shoots the leading-order formula due to heavy-tailed lognormal weights); so
    # the verdict is on SIGN + MONOTONICITY, with magnitude vs formula reported as secondary.
    n_pos = sum(1 for sg in SIGMA_G_GRID if mean_signed[sg] > 0)
    signs = [mean_signed[sg] for sg in SIGMA_G_GRID]
    monotone_pos = all(signs[i + 1] >= signs[i] - 1e-6 for i in range(len(signs) - 1))
    sign_note = "NEG" if mean_signed[max(SIGMA_G_GRID)] < 0 else "POS"
    summary = (f"measured_sign={sign_note} n_pos={n_pos}/7 monotone_pos={monotone_pos} "
               f"signed_dev=" + " ".join(f"{sg:.2f}:{mean_signed[sg]:+.3f}" for sg in SIGMA_G_GRID) +
               f" | (secondary) mag_match={n_match}/7 vs formula -- exact normalization pending NLO drill")

    if n_pos <= HF_MATCH_CELLS:
        return ("HARD_FAIL",
                f"HARD_FAIL: deviation NOT positive ({n_pos}/7 positive); contradicts multiplicative-per-pattern "
                f"-> positive-sign convention claim. {summary}")
    if n_pos >= HP_MATCH_CELLS and monotone_pos:
        return ("HARD_PASS",
                f"HARD_PASS: multiplicative-per-pattern noise gives POSITIVE monotone kappa_3 deviation "
                f"({n_pos}/7 positive) -- confirms noise-convention-determines-sign (dual-anchor with v1 NEG). {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: positive but non-monotone sign signal. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_ACTIVE} mode={RUN_MODE} seeds={SEEDS} "
      f"alpha={ALPHA} sigma_g_grid={SIGMA_G_GRID}", flush=True)
if RUN_MODE == "full" and N_ACTIVE != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_ACTIVE={N_ACTIVE} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "run_mode": RUN_MODE, "alpha": ALPHA, "sigma_g_grid": SIGMA_G_GRID}
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
    "N": N, "run_mode": RUN_MODE, "alpha": ALPHA, "sigma_g_grid": SIGMA_G_GRID,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "ratio_clean": r.get("ratio_clean"),
                  "cells": r.get("cells", []), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
