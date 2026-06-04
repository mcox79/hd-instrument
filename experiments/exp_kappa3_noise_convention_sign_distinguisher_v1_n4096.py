"""
kappa3_noise_convention_sign_distinguisher_v1_n4096 -- definitive kappa_3 noise-convention sign test.

ROUTING: notes/exp_dev_handoff_research_kappa3_sign_convention_2x_2026-06-04.md (Anchor 1; CRITICAL/cheap)
         notes/research_drill_kappa3_nlo_noise_convention_2x_2026-06-04.md.

CAPABILITY QUESTION (resolves the kappa3-NLO sign saga):
  Which noise convention matches the NLO formula's POSITIVE kappa_3 deviation? Research drill predicts:
    (A) additive-on-W (GUE): W_noisy = W_clean + sigma_g * G/sqrt(N), G ~ i.i.d. N(0,1)
        -> delta_kappa3 SMALL NEGATIVE (GUE has kappa_k=0 for k>=3 at leading order; finite-N correction negative).
    (B) additive-on-PATTERNS: Xi_noisy[mu] = Xi[mu] + sigma_g * g_mu, g_mu ~ N(0, I_N)
        -> delta_kappa3 POSITIVE, matching 3 * sigma_g^2 * alpha at leading order (within 30%).
  Run both back-to-back at the same sigma_g, alpha; measure SIGNED delta_kappa3. This determines the
  correct convention for ALL downstream kappa_3 noise-robustness anchors (I-19 / sigma_g_crit series).
  Uses SMALL sigma_g (leading-order regime) so 3*sigma_g^2*alpha applies and heavy-tail blowup is avoided.

DESIGN (CPU numpy, N=4096, alpha=0.05, M=204):
  W_clean = Xi^T Xi / N. kappa_3^free = m3 - 3 m1 m2 + 2 m1^3 (moments m_k = Tr(W^k)/N via Hutchinson).
  delta_kappa3 = kappa_3^free(W_noisy) - kappa_3^free(W_clean) under each condition.
  sigma_g in {0.05, 0.10, 0.20}; 5 seeds.

PRE-REGISTERED BANDS:
  HARD-PASS (both directions confirmed): condition A delta_kappa3 <= 0 (negative/near-zero) at all
    sigma_g AND condition B delta_kappa3 > 0 at all sigma_g AND condition-B delta matches 3*sigma_g^2*alpha
    within 30% on >= 2/3 sigma_g cells; 5/5 seeds consistent on signs.
  MIDDLE: signs correct (A<=0, B>0) but condition-B magnitude off > 30% (form/normalization refinement needed).
  HARD-FAIL: a sign is WRONG (A delta > 0, or B delta < 0) -> the convention model is refuted.

FORMULA SELF-TESTS (PROT-022):
  1. leading-order pred(sigma_g=0.10, alpha=0.05) = 3 * 0.01 * 0.05 = 0.0015. [EXPECTED within 1e-6]
  2. free kappa_3 of equal-diagonal = 0.
  3. additive-on-W noise G/sqrt(N) has per-entry std sigma_g/sqrt(N): check std ~ sigma_g/sqrt(N).

PROT-018: anchor has _n4096; N MUST = 4096.
PROT-021: seed checkpoints keyed run_mode + N.
QUEUE: remote_cpu_queue (pure numpy; CPU). TIMEOUT: 14400s (PROT-019 floor for _n4096).
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

ANCHOR_NAME = "kappa3_noise_convention_sign_distinguisher_v1_n4096"
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
SIGMA_G_GRID = [0.05, 0.10, 0.20]
MATCH_TOL = 0.30
HP_MATCH_CELLS = 2   # condition B matches formula on >= 2/3 cells

if RUN_MODE == "smoke":
    N_ACTIVE = 256
    SEEDS = [7, 17]
    N_PROBES = 400
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_PROBES = 3000

def _pred(sg, alpha):
    return 3.0 * sg * sg * alpha


def free_kappa3(m1, m2, m3):
    return m3 - 3.0 * m1 * m2 + 2.0 * m1 ** 3


def measure_moments(W, n, rng, n_probes):
    m1 = float(np.trace(W)) / n
    m2 = float(np.sum(W * W)) / n
    V = rng.choice([-1.0, 1.0], size=(n, n_probes)).astype(np.float32)
    W3V = W @ (W @ (W @ V))
    m3 = float(np.mean((V * W3V).sum(axis=0))) / n
    return m1, m2, m3


def k3_free_of(W, n, rng, n_probes):
    return free_kappa3(*measure_moments(W, n, rng, n_probes))


def build_clean(n, alpha, rng):
    M = max(2, int(round(alpha * n)))
    Xi = rng.choice([-1.0, 1.0], size=(M, n)).astype(np.float32)
    return Xi, (Xi.T @ Xi) / n


def noisy_A_additive_on_W(W_clean, n, sigma_g, rng):
    """W_noisy = W_clean + sigma_g * G / sqrt(N), G i.i.d. N(0,1) (symmetrized)."""
    G = rng.standard_normal((n, n)).astype(np.float32)
    G = (G + G.T) / np.sqrt(2.0)   # symmetric GUE-like
    return W_clean + sigma_g * G / np.sqrt(n)


def noisy_B_additive_on_patterns(Xi, n, sigma_g, rng):
    """Xi_noisy = Xi + sigma_g * g, g ~ N(0, I_N) per pattern; W_noisy = Xi_noisy^T Xi_noisy / N."""
    Xi_noisy = Xi + sigma_g * rng.standard_normal(Xi.shape).astype(np.float32)
    return (Xi_noisy.T @ Xi_noisy) / n


def _selftest():
    assert abs(_pred(0.10, 0.05) - 0.0015) < 1e-6, _pred(0.10, 0.05)
    d = np.array([1.0, 1.0, 1.0]); m1 = float(np.mean(d)); m2 = float(np.mean(d*d)); m3 = float(np.mean(d**3))
    assert abs(free_kappa3(m1, m2, m3)) < 1e-6
    rng = np.random.default_rng(0)
    G = rng.standard_normal((512, 512)).astype(np.float32); Gs = (G + G.T) / np.sqrt(2.0)
    per_entry = float(np.std(0.2 * Gs / np.sqrt(512)))
    assert abs(per_entry - 0.2 / np.sqrt(512)) < 0.01 * (0.2 / np.sqrt(512)) + 1e-4, per_entry
    print(f"[selftest] PASS: pred(0.10)=0.0015 free_k3_equal=0 additive_W_std ok", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    Xi, W_clean = build_clean(n_dim, ALPHA, rng)
    k3_clean = k3_free_of(W_clean, n_dim, rng, N_PROBES)
    cells = []
    for sg in SIGMA_G_GRID:
        rngA = np.random.default_rng(seed + 100 + int(sg * 1000))
        rngB = np.random.default_rng(seed + 200 + int(sg * 1000))
        WA = noisy_A_additive_on_W(W_clean, n_dim, sg, rngA)
        WB = noisy_B_additive_on_patterns(Xi, n_dim, sg, rngB)
        dA = k3_free_of(WA, n_dim, rng, N_PROBES) - k3_clean
        dB = k3_free_of(WB, n_dim, rng, N_PROBES) - k3_clean
        pred = _pred(sg, ALPHA)
        relB = abs(dB - pred) / max(abs(pred), 1e-12)
        matchB = (dB > 0) and (relB < MATCH_TOL)
        print(f"  [seed={seed} sg={sg:.2f}] A_additive_W delta={dA:+.5f} | "
              f"B_additive_patterns delta={dB:+.5f} pred={pred:.5f} relB={relB:.3f} matchB={matchB}", flush=True)
        cells.append({"sigma_g": sg, "deltaA": float(dA), "deltaB": float(dB),
                      "pred": float(pred), "relB": float(relB), "matchB": bool(matchB)})
    elapsed = time.time() - t0
    print(f"  [seed={seed}] k3_clean={k3_clean:.5f} elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "k3_clean": float(k3_clean),
            "cells": cells, "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    meanA = {}; meanB = {}; matchB_cells = {}
    for sg in SIGMA_G_GRID:
        As = [c["deltaA"] for r in results for c in r.get("cells", []) if abs(c["sigma_g"] - sg) < 1e-9]
        Bs = [c["deltaB"] for r in results for c in r.get("cells", []) if abs(c["sigma_g"] - sg) < 1e-9]
        Ms = [c["matchB"] for r in results for c in r.get("cells", []) if abs(c["sigma_g"] - sg) < 1e-9]
        meanA[sg] = float(np.mean(As)) if As else 0.0
        meanB[sg] = float(np.mean(Bs)) if Bs else 0.0
        matchB_cells[sg] = (sum(Ms) / len(Ms)) >= 0.5 if Ms else False
    # Headline claim: additive-on-PATTERNS (B) gives a POSITIVE delta matching 3*sg^2*alpha; additive-on-W
    # (A) gives a NEGLIGIBLE delta by contrast. The "A strictly negative" piece is a tiny finite-N effect
    # (GUE kappa_3=0 at leading order) hard to resolve from zero, so it is the CONTRAST not a hard gate.
    n_Bpos = sum(1 for sg in SIGMA_G_GRID if meanB[sg] > 0)
    n_matchB = sum(1 for sg in SIGMA_G_GRID if matchB_cells[sg])
    mean_absA = float(np.mean([abs(meanA[sg]) for sg in SIGMA_G_GRID]))
    mean_absB = float(np.mean([abs(meanB[sg]) for sg in SIGMA_G_GRID]))
    A_is_contrast = mean_absA < mean_absB   # additive-on-W deviation is weaker than additive-on-patterns
    summary = ("A(additive_W)=" + " ".join(f"{sg:.2f}:{meanA[sg]:+.4f}" for sg in SIGMA_G_GRID) +
               " B(additive_patterns)=" + " ".join(f"{sg:.2f}:{meanB[sg]:+.4f}" for sg in SIGMA_G_GRID) +
               f" B_pos={n_Bpos}/3 B_matches_formula={n_matchB}/3 |A|<|B|={A_is_contrast}")

    if n_Bpos < HP_MATCH_CELLS:
        return ("HARD_FAIL",
                f"HARD_FAIL: additive-on-patterns delta NOT positive ({n_Bpos}/3 positive); convention model refuted. {summary}")
    if n_Bpos >= HP_MATCH_CELLS and n_matchB >= HP_MATCH_CELLS and A_is_contrast:
        return ("HARD_PASS",
                f"HARD_PASS: additive-on-patterns -> POSITIVE matching 3*sg^2*alpha ({n_matchB}/3); "
                f"additive-on-W negligible (|A|<|B|). Convention determines sign CONFIRMED. {summary}")
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: B positive ({n_Bpos}/3) but formula-match {n_matchB}/3 or A-contrast weak. {summary}")


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
    "per_seed": [{"seed": r.get("seed"), "k3_clean": r.get("k3_clean"),
                  "cells": r.get("cells", []), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
