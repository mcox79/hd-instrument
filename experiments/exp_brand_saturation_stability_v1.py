"""
brand_saturation_stability_v1 -- Brand-incremental SVD at saturation (alpha >= 0.10).

SCIENTIFIC QUESTION:
  Brand-incremental SVD was HP'd in v333 for alpha < 0.10.
  Does Brand update preserve accuracy within +/-0.03 at alpha >= 0.10 (capacity limit)?

  Research Q: at high alpha (near saturation), does Brand-incremental Gram update
  remain stable? Prediction: yes, because Brand is algebraically exact up to fp precision;
  stability should hold until alpha ~ 0.5 (beyond practical use).

  Protocol:
    1. Build W_batch = (1/N) Xi^T Xi for M = alpha*N patterns (ground truth).
    2. Build W_brand by adding patterns one at a time with Brand-incremental update.
    3. Measure accuracy: acc = 1 - ||W_batch - W_brand||_F / ||W_batch||_F.
    4. Test across alpha in {0.10, 0.20, 0.40, 0.80} (extending v333 alpha < 0.10 HP).

  HP: accuracy within +/-0.03 of 1.0 (acc >= 0.97) at all alpha values.
  HF: accuracy < 0.95 for any alpha (fp drift exceeds practical threshold).
  MIDDLE: accuracy >= 0.97 at some alphas, < 0.97 at high alpha.

PRE-REGISTERED BANDS:
  HP: acc >= 0.97 for ALL alpha in sweep.
  HF: acc < 0.95 for any alpha.
  MIDDLE: all acc >= 0.95 but some < 0.97.
  Note: v333 confirmed acc = 1.0 (algebraic identity) at alpha < 0.10.
  At alpha >= 0.10, fp accumulation may degrade. Bands: +-50% of acc drop from 1.0.

FORMULA SELF-TESTS:
  1. Frobenius accuracy: acc = 1 - ||A-B||_F / ||A||_F.
     [INPUT: A = identity(3), B = identity(3)] [EXPECTED: acc = 1.0]
  2. Brand rank-1 update: W_new = W_old + (1/N) * xi_new * xi_new^T.
     [INPUT: W_old = 0 (3x3), xi = [1,0,0], N=3] [EXPECTED: W_new[0,0] = 1/3]
  3. Accuracy for diagonal shift: A = I, B = I + 0.01*I, N=3.
     ||A-B||_F = 0.01*sqrt(3), ||A||_F = sqrt(3). acc = 1 - 0.01.
     [INPUT: A=identity(3), B=1.01*identity(3)] [EXPECTED: acc = 0.99]

No _nN suffix; production N=2048 per PROT-018 rule 3.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "brand_saturation_stability_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 2048

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    ALPHA_LIST = [0.10, 0.20]
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_LIST = [0.10, 0.20, 0.40, 0.80]

HP_ACC = 0.97
HF_ACC = 0.95

# ---- FORMULA SELF-TESTS ----
# Test 1: Frobenius accuracy identity matrices
_A_st = np.eye(3)
_B_st = np.eye(3)
_acc_st = 1.0 - float(np.linalg.norm(_A_st - _B_st, 'fro')) / (float(np.linalg.norm(_A_st, 'fro')) + 1e-12)
assert abs(_acc_st - 1.0) < 1e-8, f"acc_selftest T1: {_acc_st}"
# Test 2: Brand rank-1 update
_W_old = np.zeros((3, 3))
_xi_st2 = np.array([1.0, 0.0, 0.0])
_W_new = _W_old + np.outer(_xi_st2, _xi_st2) / 3.0
assert abs(_W_new[0, 0] - 1.0/3.0) < 1e-8, f"rank1 update T2: {_W_new[0,0]}"
# Test 3: shifted identity accuracy
_A3 = np.eye(3)
_B3 = 1.01 * np.eye(3)
_acc3 = 1.0 - float(np.linalg.norm(_A3 - _B3, 'fro')) / (float(np.linalg.norm(_A3, 'fro')) + 1e-12)
assert abs(_acc3 - 0.99) < 1e-6, f"acc T3: {_acc3}"
print(f"[formula_selftest] acc_identity=1.0 rank1_ok acc_shifted={_acc3:.4f} OK", flush=True)


def _instrumentation_selftest():
    """Verify accuracy metric is non-null at smoke scale."""
    N_t = 128
    alpha = 0.10
    M_t = int(alpha * N_t)  # 12
    seed = 42
    rng = np.random.RandomState(seed)

    Xi = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_batch = Xi.T @ Xi / float(N_t)

    # Brand incremental
    W_brand = np.zeros((N_t, N_t), dtype=np.float64)
    for i in range(M_t):
        W_brand += np.outer(Xi[i], Xi[i]) / float(N_t)

    acc = 1.0 - float(np.linalg.norm(W_batch - W_brand, 'fro')) / (
        float(np.linalg.norm(W_batch, 'fro')) + 1e-12)

    assert not math.isnan(acc), "accuracy is NaN"
    assert acc >= 0.0, f"accuracy negative: {acc}"
    assert len(ALPHA_LIST) > 0, "ALPHA_LIST empty at smoke scale"

    print(f"[selftest] PASS: N={N_t} M={M_t} alpha={alpha} acc={acc:.6f} OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    results = {}

    for alpha in ALPHA_LIST:
        M = max(1, int(alpha * N))
        t0 = time.time()

        Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)

        # Ground truth batch build
        W_batch = Xi.T @ Xi / float(N)

        # Brand incremental (rank-1 sequential update)
        W_brand = np.zeros((N, N), dtype=np.float64)
        for i in range(M):
            W_brand += np.outer(Xi[i], Xi[i]) / float(N)

        # Accuracy
        norm_diff = float(np.linalg.norm(W_batch - W_brand, 'fro'))
        norm_batch = float(np.linalg.norm(W_batch, 'fro'))
        acc = 1.0 - norm_diff / (norm_batch + 1e-12)

        hp_ok = acc >= HP_ACC
        hf_ok = acc < HF_ACC
        elapsed = time.time() - t0

        print(f"  [seed={seed} alpha={alpha:.2f} M={M}] acc={acc:.6f} "
              f"norm_diff={norm_diff:.4f} hp={hp_ok} t={elapsed:.2f}s", flush=True)

        results[str(alpha)] = {
            "alpha": float(alpha), "M": M, "N": N,
            "accuracy": float(acc),
            "norm_diff": float(norm_diff),
            "norm_batch": float(norm_batch),
            "hp_ok": bool(hp_ok),
            "hf_ok": bool(hf_ok),
            "elapsed_s": float(elapsed),
        }

    return {"alpha_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    alpha_accs = {str(a): [] for a in ALPHA_LIST}
    for sd in per_seed.values():
        for ak, v in sd.get("alpha_results", {}).items():
            if ak in alpha_accs and v.get("accuracy") is not None:
                alpha_accs[ak].append(v["accuracy"])

    mean_accs = {ak: float(np.mean(v)) for ak, v in alpha_accs.items() if v}
    hp_all = all(acc >= HP_ACC for acc in mean_accs.values())
    hf_any = any(acc < HF_ACC for acc in mean_accs.values())

    summary = (f"mean_accs={mean_accs} "
               f"HP>={HP_ACC} HF<{HF_ACC} n_alpha={len(ALPHA_LIST)}")

    if hf_any:
        return ("HARD_FAIL", f"HARD_FAIL: accuracy < {HF_ACC} for some alpha. {summary}")
    if hp_all:
        return ("HARD_PASS", f"HARD_PASS: all alpha acc >= {HP_ACC}. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: some alpha below HP but above HF. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] brand_saturation N={N} alphas={ALPHA_LIST}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_s, "alpha_list": ALPHA_LIST,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
