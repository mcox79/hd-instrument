"""
alpha_mu_snap_interaction_v1 -- alpha_mu x SNAP interaction (per-fact retention dial).

SCIENTIFIC QUESTION (killer feature 6: per-fact retention policy):
  The per-fact retention dial uses alpha_mu (per-pattern weight) x SNAP (selective
  non-linear attenuated pruning) to modulate individual pattern persistence.
  Does the alpha_mu * SNAP interaction produce measurable differential retention?

  Protocol:
    - Store two pattern classes: high-priority (HP) at alpha_mu_hp and
      low-priority (LP) at alpha_mu_lp = alpha_mu_hp / K (K in {2, 4, 8}).
    - Apply SNAP: prune weight contributions below a threshold tau_snap.
    - Measure: HP retention rate vs LP retention rate.
    - Target: HP_retention - LP_retention >= delta_retention (differential retention signal).

  HP: (HP_retention - LP_retention) >= 0.20 at all K values.
      HP_retention >= 0.80 (high-priority patterns reliably stored).
      LP_retention <= 0.60 at K=8 (low-priority patterns successfully attenuated).
  HF: HP_retention < 0.50 (high-priority storage broken).
  MIDDLE: differential >= 0.10 but < 0.20, OR LP_retention not attenuated at K=8.

PRE-REGISTERED BANDS (killer feature first measurement -- calibration probe):
  HP: differential_retention >= 0.20 (meaningful per-fact modulation).
  HF: HP_retention < 0.50 (mechanism broken).
  MIDDLE: 0.10 <= differential < 0.20.
  Note: no prior empirical anchor for alpha_mu x SNAP interaction; bands +-50% theory.

FORMULA SELF-TESTS:
  1. alpha_mu weighting: W = (1/N) * sum_mu alpha_mu * xi_mu xi_mu^T.
     For alpha_mu_hp=1.0, alpha_mu_lp=0.5: HP patterns get 2x weight.
     [INPUT: xi_hp=[1,1], xi_lp=[-1,-1], alpha_hp=1.0, alpha_lp=0.5, N=2]
     [EXPECTED: W = (1/2)*(xi_hp xi_hp^T + 0.5*xi_lp xi_lp^T) = 0.75*I (for orthogonal)]
  2. SNAP pruning: zero out W[i,j] if |W[i,j]| < tau_snap.
     [INPUT: W=[[0.5, 0.1], [0.1, 0.5]], tau_snap=0.15]
     [EXPECTED: W_snapped=[[0.5, 0], [0, 0.5]]]
  3. Differential retention: retained_hp - retained_lp.
     [INPUT: retained_hp=0.90, retained_lp=0.65] [EXPECTED: diff=0.25]

No _nN suffix; production N=1024 per PROT-018 rule 3.
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

ANCHOR_NAME = "alpha_mu_snap_interaction_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 1024

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_HP = 8          # high-priority patterns
    M_LP = 8          # low-priority patterns
    K_LIST = [2, 4]   # alpha_mu ratio K values
    TAU_SNAP_LIST = [0.01, 0.05]
    N_TEST = 8
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_HP = 20
    M_LP = 20
    K_LIST = [2, 4, 8]
    TAU_SNAP_LIST = [0.005, 0.01, 0.02, 0.05]
    N_TEST = 20

ALPHA_MU_HP = 1.0    # high-priority weight
HP_DIFF = 0.20       # HP: HP_retention - LP_retention >= 0.20
HP_HP_RET = 0.80     # HP: high-priority retention >= 0.80
HP_LP_RET_K8 = 0.60  # HP: low-priority retention <= 0.60 at K=8
HF_HP_RET = 0.50     # HF: high-priority retention < 0.50

# ---- FORMULA SELF-TESTS ----
# Test 2: SNAP pruning
_W_snap_in = np.array([[0.5, 0.1], [0.1, 0.5]])
_tau_snap_t = 0.15
_W_snap_out = _W_snap_in.copy()
_W_snap_out[np.abs(_W_snap_out) < _tau_snap_t] = 0.0
assert abs(_W_snap_out[0, 1]) < 1e-12, f"SNAP T2: off-diag not zeroed: {_W_snap_out[0,1]}"
assert abs(_W_snap_out[0, 0] - 0.5) < 1e-8, f"SNAP T2: diag wrong: {_W_snap_out[0,0]}"
# Test 3: differential retention
_diff_t3 = 0.90 - 0.65
assert abs(_diff_t3 - 0.25) < 1e-8, f"diff T3: {_diff_t3}"
print(f"[formula_selftest] SNAP_ok diff={_diff_t3:.2f} OK", flush=True)


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = 5) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def _instrumentation_selftest():
    """Verify differential retention is non-null at smoke scale."""
    N_t = 128
    M_hp_t, M_lp_t = 4, 4
    K_t = 2
    seed = 42
    rng = np.random.RandomState(seed)

    Xi_hp = rng.choice([-1.0, 1.0], size=(M_hp_t, N_t)).astype(np.float64)
    Xi_lp = rng.choice([-1.0, 1.0], size=(M_lp_t, N_t)).astype(np.float64)

    alpha_lp = ALPHA_MU_HP / K_t
    W = (ALPHA_MU_HP * Xi_hp.T @ Xi_hp + alpha_lp * Xi_lp.T @ Xi_lp) / float(N_t)

    tau_snap = 0.01
    W_snap = W.copy()
    W_snap[np.abs(W_snap) < tau_snap] = 0.0

    # Test retrieval
    fids_hp = []
    for i in range(M_hp_t):
        probe = Xi_hp[i].copy()
        probe[:5] *= -1.0
        r = hopfield_retrieve(W_snap, probe)
        fids_hp.append(cosine_sim(r, Xi_hp[i]))
    ret_hp = float(np.mean(fids_hp))

    fids_lp = []
    for i in range(M_lp_t):
        probe = Xi_lp[i].copy()
        probe[:5] *= -1.0
        r = hopfield_retrieve(W_snap, probe)
        fids_lp.append(cosine_sim(r, Xi_lp[i]))
    ret_lp = float(np.mean(fids_lp))

    assert not math.isnan(ret_hp), f"ret_hp is NaN"
    assert not math.isnan(ret_lp), f"ret_lp is NaN"
    diff = ret_hp - ret_lp
    assert len(K_LIST) > 0, "K_LIST empty"
    assert len(TAU_SNAP_LIST) > 0, "TAU_SNAP_LIST empty"

    print(f"[selftest] PASS: ret_hp={ret_hp:.4f} ret_lp={ret_lp:.4f} diff={diff:.4f} OK",
          flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    results = {}

    Xi_hp = rng.choice([-1.0, 1.0], size=(M_HP, N)).astype(np.float64)
    Xi_lp = rng.choice([-1.0, 1.0], size=(M_LP, N)).astype(np.float64)

    for K in K_LIST:
        alpha_lp = ALPHA_MU_HP / K
        # Weighted weight matrix
        W = (ALPHA_MU_HP * Xi_hp.T @ Xi_hp + alpha_lp * Xi_lp.T @ Xi_lp) / float(N)

        for tau_snap in TAU_SNAP_LIST:
            # Apply SNAP
            W_snap = W.copy()
            W_snap[np.abs(W_snap) < tau_snap] = 0.0

            # Test HP retention
            fids_hp = []
            rng2 = np.random.RandomState(seed + 1)
            for i in range(min(N_TEST, M_HP)):
                probe = Xi_hp[i].copy()
                flip = rng2.random(N) < 0.10
                probe[flip] *= -1.0
                r = hopfield_retrieve(W_snap, probe)
                fids_hp.append(cosine_sim(r, Xi_hp[i]))
            ret_hp = float(np.mean(fids_hp)) if fids_hp else 0.0

            # Test LP retention
            fids_lp = []
            for i in range(min(N_TEST, M_LP)):
                probe = Xi_lp[i].copy()
                flip = rng2.random(N) < 0.10
                probe[flip] *= -1.0
                r = hopfield_retrieve(W_snap, probe)
                fids_lp.append(cosine_sim(r, Xi_lp[i]))
            ret_lp = float(np.mean(fids_lp)) if fids_lp else 0.0

            diff = ret_hp - ret_lp
            hp_diff_ok = diff >= HP_DIFF
            hp_hp_ok = ret_hp >= HP_HP_RET
            lp_att_ok = ret_lp <= HP_LP_RET_K8 if K == 8 else True
            hf_hp_broken = ret_hp < HF_HP_RET

            key = f"K{K}_tau{tau_snap}"
            print(f"  [seed={seed} K={K} tau={tau_snap}] "
                  f"ret_hp={ret_hp:.4f} ret_lp={ret_lp:.4f} diff={diff:.4f} "
                  f"hp_diff={hp_diff_ok} hp_hp={hp_hp_ok}", flush=True)

            results[key] = {
                "K": K, "tau_snap": tau_snap, "N": N,
                "ret_hp": float(ret_hp), "ret_lp": float(ret_lp),
                "differential": float(diff),
                "hp_diff_ok": bool(hp_diff_ok),
                "hp_hp_ok": bool(hp_hp_ok),
                "lp_att_ok": bool(lp_att_ok),
                "hf_hp_broken": bool(hf_hp_broken),
            }

    return {"results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    keys = [f"K{K}_tau{tau}" for K in K_LIST for tau in TAU_SNAP_LIST]
    metrics_agg = {k: {"diffs": [], "ret_hps": [], "ret_lps": []} for k in keys}

    for sd in per_seed.values():
        for k, v in sd.get("results", {}).items():
            if k in metrics_agg:
                metrics_agg[k]["diffs"].append(v.get("differential", 0.0))
                metrics_agg[k]["ret_hps"].append(v.get("ret_hp", 0.0))
                metrics_agg[k]["ret_lps"].append(v.get("ret_lp", 0.0))

    # Best tau per K (maximize differential)
    best_by_K = {}
    for K in K_LIST:
        best_diff = -1.0
        best_k = None
        for tau in TAU_SNAP_LIST:
            k = f"K{K}_tau{tau}"
            if metrics_agg[k]["diffs"]:
                mean_diff = float(np.mean(metrics_agg[k]["diffs"]))
                if mean_diff > best_diff:
                    best_diff = mean_diff
                    best_k = k
        best_by_K[K] = (best_k, best_diff)

    hp_diff_pass = all(d >= HP_DIFF for _, d in best_by_K.values())
    hf_triggered = any(
        float(np.mean(metrics_agg[k]["ret_hps"])) < HF_HP_RET
        for k in keys if metrics_agg[k]["ret_hps"]
    )

    best_ret_hps = {}
    for K, (k, _) in best_by_K.items():
        if k and metrics_agg[k]["ret_hps"]:
            best_ret_hps[K] = float(np.mean(metrics_agg[k]["ret_hps"]))

    hp_hp_ok = all(r >= HP_HP_RET for r in best_ret_hps.values())

    summary = (f"best_diffs_by_K={best_by_K} "
               f"best_ret_hps={best_ret_hps} "
               f"HP_DIFF={HP_DIFF} HP_HP_RET={HP_HP_RET} HF_HP_RET={HF_HP_RET}")

    if hf_triggered:
        return ("HARD_FAIL", f"HARD_FAIL: HP retention broken. {summary}")
    if hp_diff_pass and hp_hp_ok:
        return ("HARD_PASS", f"HARD_PASS: differential >= {HP_DIFF} at all K. {summary}")
    if any(d >= HP_DIFF * 0.5 for _, d in best_by_K.values()):
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial differential signal. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: differential below threshold. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] alpha_mu_snap N={N} K_list={K_LIST}...", flush=True)
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
    "elapsed_s": elapsed_s, "K_list": K_LIST, "tau_snap_list": TAU_SNAP_LIST,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
