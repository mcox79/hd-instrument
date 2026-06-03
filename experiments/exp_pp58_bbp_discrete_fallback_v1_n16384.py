"""
pp58_bbp_discrete_fallback_v1_n16384 -- PP-58 BBP discrete-pattern fallback test at N=16384.

CONTEXT:
  PP-58 primary test (pp58_bbp_spectral_gap_calibration_v1_n16384) tests eigenspectrum
  with Gaussian additive noise sigma_g sweep -- continuous noise model.
  This fallback tests the same BBP spectral-gap criterion using DISCRETE BSC +-1 patterns
  as the "noise" source (random additional +-1 patterns added to the memory matrix).
  Substrate's actual operating mode uses discrete +-1 patterns (SKAH-M class).
  Theoretical expectation: BBP criterion applies equally to discrete random matrices
  by universality (Marchenko-Pastur is universal for i.i.d. entries with finite variance).

SCIENTIFIC QUESTION:
  Does the discrete-pattern BBP criterion match the Gaussian sigma_g criterion?
  Specifically: does adding k_noise random +-1 patterns to W (as background noise)
  produce the same audit_crit/cap_crit/ratio as adding Gaussian noise at sigma_g?
  Equivalently: sigma_g_equiv = sqrt(k_noise / N) by MP universality.

TEST DESIGN:
  N=16384, alpha=0.05 (M=819 signal patterns), 5 seeds.
  Sweep k_noise in [0, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1500, 2000].
  For each k_noise: W = (Xi_sig.T @ Xi_sig)/N + (Xi_noise.T @ Xi_noise)/N.
  Compute eigenspectrum of W on CPU.
  Find audit_crit: k_noise where signal eigenvalues merge with bulk.
  Find cap_crit: k_noise where retrieval accuracy falls below 0.5.
  sigma_g_equiv(k_noise) = sqrt(k_noise / N).
  Compute ratio = cap_crit / audit_crit (in k_noise units OR sigma_g_equiv units).
  Compare to BBP continuous prediction: sigma_g_audit_crit = 1 - sqrt(alpha) - alpha = 0.726.
  -> k_noise_audit_crit_expected = (sigma_g_audit_crit)^2 * N = (0.726)^2 * 16384 ~ 8627.
  This is outside our sweep (k_noise_max=2000). Instead track ratio:
  ratio_discrete vs ratio_continuous (both should be ~4.13 by BBP universality).

  NOTE: memory estimate for W CPU: (M_sig + k_noise_max) * N * 4 / 1e9 << 1 GB. Fine.
  W itself: N^2 * 4 / 1e9 = 1.07 GB RAM. Fine.

OOM PRE-CHECK:
  Xi_sig: 819 * 16384 * 4 / 1e6 = 53.7 MB. Fine.
  Xi_noise: 2000 * 16384 * 4 / 1e6 = 131 MB. Fine.
  W on CPU: 16384^2 * 4 / 1e9 = 1.07 GB. Fine (remote 16+ GB RAM).
  Eigendecomp at N=16384 on CPU: ~2s per matrix. 15 k_noise * 5 seeds = 75 calls * 2s = 150s.
  Total estimated ~200-300s FULL.

FORMULA SELF-TESTS (PROT-022):
  1. BBP sigma_g_audit_crit formula: 1 - sqrt(0.05) - 0.05 = 0.7264 at alpha=0.05.
     [INPUT: alpha=0.05] [EXPECTED: 0.7264 within 0.001]
  2. k_noise_audit_crit_expected = (0.7264)^2 * 16384.
     [EXPECTED: k_noise_audit_crit_expected ~ 8627]
  3. sigma_g_equiv at k_noise=819: sqrt(819 / 16384) = sqrt(0.05) = 0.2236.
     [INPUT: k_noise=819, N=16384] [EXPECTED: 0.2236 within 0.001]
  4. M at alpha=0.05, N=16384: int(0.05 * 16384) = 819. [EXPECTED: M=819]

PRE-REGISTERED BANDS (PP-58 BBP discrete fallback; no prior discrete eigenspectrum anchor):
  Calibration probe with no prior empirical anchor; bands widened to +-50% per policy.
  Theoretical BBP prediction: ratio_discrete ~= ratio_continuous ~= 4.13 at alpha=0.05.
  HARD-PASS: ratio in [2.0, 6.0] (+-50% of 4.13) AND audit_crit_k < cap_crit_k
             (ordering preserved) AND at least one k_noise value shows measurable merging.
  MIDDLE: ratio in [1.5, 2.0) or (6.0, 7.0] (borderline).
  HARD-FAIL: ratio < 1.0 OR > 8.0 OR no merging detected at any k_noise (audit_crit=None).

  Strategic significance: HP founds discrete-universality sub-property of PP-58 row;
  equivalently confirms audit criterion applies to substrate's actual discrete operating mode.

PROT-018: anchor name has _n16384; N MUST = 16384.
  Note: _n16384 is in the anchor name suffix; production N=16384.
PROT-021: seed checkpoints keyed with run_mode.
QUEUE: remote_cpu_queue (pure numpy eigendecomp; no GPU required; ~300s FULL wall).
TIMEOUT ESTIMATE: smoke 5 k_noise * 2 seeds ~ 10 eigendecomp calls * 2s = 20s.
  FULL 15 k_noise * 5 seeds = 75 calls * 2s = 150s + overhead.
  ceil(1.5 * 20 * (15/5) * (5/2)) = ceil(1.5 * 20 * 3 * 2.5) = ceil(225) = 300s.
  With 3x walk-back margin (first discrete BBP test): timeout=900s.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import numpy as np

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp58_bbp_discrete_fallback_v1_n16384"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
CRIT_RECALL = 0.5

# PROT-022 formula self-tests at module scope
_ALPHA_C = ALPHA
_BBP_SIGMA_AUDIT = 1.0 - _ALPHA_C**0.5 - _ALPHA_C
assert abs(_BBP_SIGMA_AUDIT - 0.7264) < 0.001, f"BBP sigma_audit_crit={_BBP_SIGMA_AUDIT:.4f} expected 0.7264"
_K_AUDIT_EXPECTED = int((_BBP_SIGMA_AUDIT**2) * N)
assert 8000 < _K_AUDIT_EXPECTED < 9500, f"k_noise_audit_crit_expected={_K_AUDIT_EXPECTED}"
_SIGMA_EQUIV_K819 = (819 / N)**0.5
assert abs(_SIGMA_EQUIV_K819 - 0.2236) < 0.001, f"sigma_equiv(k=819)={_SIGMA_EQUIV_K819:.4f}"
_M_SIG = int(ALPHA * N)
assert _M_SIG == 819, f"M_sig={_M_SIG} expected 819"

# k_noise sweep values
K_NOISE_FULL = [0, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1500, 2000]
K_NOISE_SMOKE = [0, 100, 300, 600, 1000]

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACT = 512
    M_SIG = int(ALPHA * N_ACT)  # 25
    K_NOISE_LIST = [max(0, k * N_ACT // N) for k in K_NOISE_SMOKE]
    K_NOISE_LIST = sorted(set(K_NOISE_LIST))
    N_RETRIEVE_STEPS = 10
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACT = N
    M_SIG = _M_SIG  # 819
    K_NOISE_LIST = K_NOISE_FULL
    N_RETRIEVE_STEPS = 20

# Pre-registered bands
HP_RATIO_MIN = 2.0
HP_RATIO_MAX = 6.0
HF_RATIO_MIN = 1.0
HF_RATIO_MAX = 8.0


def generate_bsc(m: int, n: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float32)


def build_W(Xi_sig: np.ndarray, Xi_noise: np.ndarray, n_dim: int) -> np.ndarray:
    """W = (Xi_sig.T @ Xi_sig + Xi_noise.T @ Xi_noise) / N."""
    W = (Xi_sig.T @ Xi_sig) / n_dim
    if Xi_noise.shape[0] > 0:
        W = W + (Xi_noise.T @ Xi_noise) / n_dim
    return W


def mp_bulk_upper(c: float) -> float:
    """Marchenko-Pastur upper bulk edge: (1 + sqrt(c))^2."""
    return (1.0 + c**0.5)**2


def find_audit_crit(eig_vals: np.ndarray, bulk_upper: float) -> bool:
    """Return True if signal eigenvalues merge into bulk (audit criterion met)."""
    # Sort descending. Top eigenvalues belong to signal if > bulk_upper.
    sorted_eig = np.sort(eig_vals)[::-1]
    # Count eigenvalues above bulk: should be ~M_sig for signal; 0 when merged.
    n_above = np.sum(sorted_eig > bulk_upper * 1.01)
    return int(n_above) <= 1  # merged when <= 1 signal eigenvalue above bulk


def hopfield_retrieve_cpu(W: np.ndarray, probe: np.ndarray, n_steps: int) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h).astype(np.float32)
        state[state == 0] = 1.0
    return state


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-8 or nb < 1e-8:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _selftest_bbp_formula():
    """BBP sigma_g_audit_crit and sigma_g_equiv checks."""
    assert abs(_BBP_SIGMA_AUDIT - 0.7264) < 0.001
    assert abs(_SIGMA_EQUIV_K819 - 0.2236) < 0.001


def _selftest_eigendecomp():
    """Eigendecomp at N=64 gives plausible result."""
    rng = np.random.RandomState(0)
    M_t = 5
    N_t = 64
    Xi = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    W = (Xi.T @ Xi) / N_t
    eigs = np.linalg.eigvalsh(W)
    assert len(eigs) == N_t, f"eigendecomp size mismatch: {len(eigs)} vs {N_t}"
    assert not np.any(np.isnan(eigs)), "NaN eigenvalues"
    assert np.max(eigs) > 0.0, "All eigenvalues <= 0"


def _selftest_retrieve_one():
    """Retrieval at N=64 with M=5 returns plausible cos."""
    rng = np.random.RandomState(42)
    N_t = 64
    M_t = 3
    Xi = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    W = (Xi.T @ Xi) / N_t
    probe = Xi[0].copy()
    probe[rng.randint(0, N_t, 5)] *= -1.0
    ret = hopfield_retrieve_cpu(W, probe, n_steps=5)
    cos = cosine_sim(ret, Xi[0])
    assert not np.isnan(cos), "cosine is NaN"


def _instrumentation_selftest():
    _selftest_bbp_formula()
    _selftest_eigendecomp()
    _selftest_retrieve_one()
    print(f"[selftest] PASS: bbp_formula, eigendecomp_N64, retrieve_N64; "
          f"M_sig={M_SIG} k_noise_list={K_NOISE_LIST}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int, m_sig: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    Xi_sig = generate_bsc(m_sig, n_dim, seed)
    c = m_sig / n_dim  # load ratio
    bulk_upper = mp_bulk_upper(c)

    results_per_k = {}
    for k_noise in K_NOISE_LIST:
        if k_noise > 0:
            Xi_noise = generate_bsc(k_noise, n_dim, seed + 10000 + k_noise)
        else:
            Xi_noise = np.zeros((0, n_dim), dtype=np.float32)

        W = build_W(Xi_sig, Xi_noise, n_dim)

        # Eigenspectrum on CPU
        eigs = np.linalg.eigvalsh(W)
        merged = find_audit_crit(eigs, bulk_upper)

        # Retrieval check: can we still retrieve a signal pattern?
        n_check = min(3, m_sig)
        cos_list = []
        for k in range(n_check):
            probe = Xi_sig[k].copy()
            flip = rng.random(n_dim) < 0.10
            probe[flip] *= -1.0
            ret = hopfield_retrieve_cpu(W, probe, n_steps=N_RETRIEVE_STEPS)
            cos_list.append(cosine_sim(ret, Xi_sig[k]))
        mean_cos = float(np.mean(cos_list)) if cos_list else 0.0
        recall_ok = mean_cos >= CRIT_RECALL

        sigma_g_equiv = float((k_noise / n_dim)**0.5) if k_noise > 0 else 0.0
        results_per_k[k_noise] = {
            "k_noise": k_noise,
            "sigma_g_equiv": sigma_g_equiv,
            "merged": merged,
            "mean_cos": mean_cos,
            "recall_ok": recall_ok,
            "top3_eigs": sorted(eigs.tolist(), reverse=True)[:3],
        }
        print(f"  [seed={seed} k={k_noise}] sigma_equiv={sigma_g_equiv:.4f} "
              f"merged={merged} recall={recall_ok} cos={mean_cos:.4f}", flush=True)
        del W

    elapsed = time.time() - t0
    print(f"  [seed={seed}] elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "per_k": results_per_k, "elapsed_s": elapsed}


def find_thresholds(results_per_k: Dict) -> tuple:
    """Find audit_crit and cap_crit k_noise values."""
    k_sorted = sorted(results_per_k.keys())
    audit_crit = None
    cap_crit = None
    for k in k_sorted:
        if results_per_k[k]["merged"] and audit_crit is None:
            audit_crit = k
        if not results_per_k[k]["recall_ok"] and cap_crit is None:
            cap_crit = k
    return audit_crit, cap_crit


def main():
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    print(f"[{RUN_MODE}] N={N_ACT} M_sig={M_SIG} k_noise_list={K_NOISE_LIST} "
          f"seeds={SEEDS}", flush=True)

    done_seeds, remaining = resumable_seeds(SEEDS, out_dir)
    print(f"[ckpt] {len(done_seeds)} done; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[seed {seed}]", flush=True)
        r = run_seed(seed, N_ACT, M_SIG)
        write_partial(out_dir, seed, r)

    per_seed_data = aggregate_partials(out_dir, SEEDS)

    # Aggregate per_k across seeds
    agg_per_k: Dict[int, Dict] = {}
    for k in K_NOISE_LIST:
        merges = []
        recalls = []
        cos_vals = []
        for s in SEEDS:
            sd = per_seed_data.get(str(s), {})
            pk = sd.get("per_k", {}).get(str(k), sd.get("per_k", {}).get(k, {}))
            if pk:
                merges.append(pk.get("merged", False))
                recalls.append(pk.get("recall_ok", True))
                cos_vals.append(pk.get("mean_cos", 1.0))
        agg_per_k[k] = {
            "merged_majority": sum(merges) > len(merges) / 2,
            "recall_ok_majority": sum(recalls) > len(recalls) / 2,
            "mean_cos": float(np.mean(cos_vals)) if cos_vals else 0.0,
        }

    audit_crit = None
    cap_crit = None
    for k in sorted(K_NOISE_LIST):
        if agg_per_k[k]["merged_majority"] and audit_crit is None:
            audit_crit = k
        if not agg_per_k[k]["recall_ok_majority"] and cap_crit is None:
            cap_crit = k

    # Compute ratio
    if audit_crit is not None and cap_crit is not None and audit_crit > 0:
        ratio = float(cap_crit) / float(audit_crit)
    else:
        ratio = None

    elapsed = time.time() - t_start

    # Verdict logic
    if ratio is None:
        if audit_crit is None:
            verdict = "HARD_FAIL"
            verdict_msg = (f"HARD_FAIL: no audit_crit detected (signal never merged into bulk "
                           f"within k_noise_max={max(K_NOISE_LIST)}); discrete BBP criterion "
                           f"not observable in sweep range. N={N_ACT} M_sig={M_SIG}")
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (f"MIDDLE_BAND: audit_crit={audit_crit} detected but cap_crit not "
                           f"reached (retrieval robust throughout sweep). ratio undefined. "
                           f"N={N_ACT} M_sig={M_SIG}")
    elif ratio < HF_RATIO_MIN or ratio > HF_RATIO_MAX:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: ratio={ratio:.3f} outside [{HF_RATIO_MIN},{HF_RATIO_MAX}]; "
                       f"audit_crit_k={audit_crit} cap_crit_k={cap_crit}; "
                       f"BBP discrete universality violated. N={N_ACT} M_sig={M_SIG}")
    elif HP_RATIO_MIN <= ratio <= HP_RATIO_MAX:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: ratio={ratio:.3f} in [{HP_RATIO_MIN},{HP_RATIO_MAX}]; "
                       f"audit_crit_k={audit_crit} cap_crit_k={cap_crit}; "
                       f"discrete BBP universality confirmed (sigma_g_equiv_audit="
                       f"{(audit_crit/N_ACT)**0.5:.4f} vs BBP={_BBP_SIGMA_AUDIT:.4f}). "
                       f"N={N_ACT} M_sig={M_SIG} alpha={ALPHA}")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: ratio={ratio:.3f} borderline; "
                       f"audit_crit_k={audit_crit} cap_crit_k={cap_crit}. "
                       f"N={N_ACT} M_sig={M_SIG}")

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "ratio": ratio,
        "audit_crit_k": audit_crit,
        "cap_crit_k": cap_crit,
        "agg_per_k": {str(k): v for k, v in agg_per_k.items()},
        "N": N_ACT,
        "M_sig": M_SIG,
        "alpha": ALPHA,
        "n_seeds": len(SEEDS),
        "elapsed_s": elapsed,
        "run_mode": RUN_MODE,
        "bbp_sigma_audit_crit_theory": _BBP_SIGMA_AUDIT,
        "k_audit_crit_theory": _K_AUDIT_EXPECTED,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[metrics] written to {metrics_path}", flush=True)


main()
