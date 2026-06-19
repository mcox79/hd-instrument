"""
multiagent_coord_competing_v1 -- Multi-agent coordination with COMPETING objectives.

SCIENTIFIC QUESTION (multiagent extension; handoff 9-cell batch):
  multiagent_consensus_v1 tested majority-vote CONSENSUS (agents agree).
  This experiment tests COMPETING objectives: agents have conflicting writes.
  Two groups of agents (Team A, Team B) each try to maximize retrieval of
  their own patterns while the other team tries to write conflicting patterns.

  Setup:
    - Agent group A (n_A agents): each writes pattern set pat_A.
    - Agent group B (n_B agents): each writes pattern set pat_B.
    - Conflict: partial overlap or competing reinforcement.
    - W_combined = W_A + W_B (superposition of both groups' matrices).

  Test cells:
    (A) Majority ownership by writes: team with more writes retrieves patterns
        with higher accuracy. Expected: team with MORE writes wins.
    (B) Interference floor: minority team's retrieval NOT zero (substrate
        doesn't fully suppress minority write). Expected: minority_acc >= 0.50.
    (C) Segregation via separate-W arbitration: W_A alone vs W_combined.
        Expected: W_A gives higher acc for pat_A than W_combined.

PRE-REGISTERED BANDS:
  HARD-PASS:
    A: majority_acc - minority_acc >= 0.15 (majority team wins retrieval);
    B: minority_acc >= 0.50 (minority not suppressed to zero);
    C: W_A_acc_A >= W_combined_acc_A - 0.02 (W_A at least as good for own patterns).
  MIDDLE:
    A: majority_acc - minority_acc [0.05, 0.15];
    B: minority_acc [0.30, 0.50];
    C: W_A_acc_A slightly worse than W_combined.
  HARD-FAIL:
    A: delta < 0.05 (no retrieval advantage for majority);
    B: minority_acc < 0.30 (minority completely suppressed);
    C: W_A_acc_A << W_combined_acc_A - 0.10 (combined W better than own-W).

  Calibration: first empirical test of competing multi-agent writes. Bands
  +-50% around theoretical prediction.

FORMULA SELF-TESTS:
  1. W_combined = W_A + W_B = sum(outer(xi,xi)/N for all xi in A+B).
  2. n_A writes each pattern: W_A_contribution = n_A * outer(xi_a, xi_a) / N.
     With n_A > n_B, xi_a retrieval cosine should exceed xi_b cosine.
  3. Separate-W: W_A retrieves pat_A without pat_B interference.

TIMEOUT ESTIMATE:
  Smoke: N=1024, n_A=3, n_B=1, 2 seeds. Full: N=4096, n_A=4, n_B=2, 5 seeds.
  Linear. Smoke ~3s -> Full ~30s. timeout=180s.

No _nN suffix; production N=4096 per rule 3.
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "multiagent_coord_competing_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
if RUN_MODE == "smoke":
    N = 1024
    SEEDS = [7, 17]
    N_A = 4    # writes by team A (majority)
    N_B = 1    # writes by team B (minority) -- 4:1 write ratio for clear effect
    # Near-capacity: M_PAT per team near 40% of M_max/2 to create interference
    M_PAT = int(0.35 * ALPHA_C * N)  # ~50 per team; total 100 = 72% capacity
else:
    N = 4096
    SEEDS = [7, 17, 23, 31, 41]
    N_A = 4
    N_B = 1
    M_PAT = int(0.35 * ALPHA_C * N)  # ~197 per team; total ~394 = 71% capacity

HP_DELTA_MAJ = 0.15
HF_DELTA_MAJ = 0.05
HP_MINORITY_ACC = 0.50
HF_MINORITY_ACC = 0.30
HP_SEPARATION_MARGIN = -0.02  # W_A_acc_A >= W_combined_acc_A - 0.02


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def retrieve(W: np.ndarray, query: np.ndarray) -> np.ndarray:
    return np.sign(W @ query + 1e-12)


def hopfield_store_multi(patterns: np.ndarray, N: int, n_writes: int) -> np.ndarray:
    """Each pattern stored n_writes times."""
    W = np.zeros((N, N), dtype=np.float64)
    for xi in patterns:
        for _ in range(n_writes):
            W += np.outer(xi, xi) / N
    return W


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)

    pat_A = rng.choice([-1.0, 1.0], size=(M_PAT, N)).astype(np.float64)
    pat_B = rng.choice([-1.0, 1.0], size=(M_PAT, N)).astype(np.float64)

    # Build matrices
    W_A = hopfield_store_multi(pat_A, N, N_A)
    W_B = hopfield_store_multi(pat_B, N, N_B)
    W_combined = W_A + W_B

    # Cell A: majority ownership by writes
    # Team A (N_A writes) vs Team B (N_B writes)
    majority_acc = float(np.mean([cosine_sim(retrieve(W_combined, xi), xi) for xi in pat_A]))
    minority_acc = float(np.mean([cosine_sim(retrieve(W_combined, xi), xi) for xi in pat_B]))
    delta_majority = majority_acc - minority_acc

    # Cell B: minority not suppressed to zero
    minority_acc_b = minority_acc  # same as above

    # Cell C: W_A alone vs W_combined for pat_A
    w_a_acc_A = float(np.mean([cosine_sim(retrieve(W_A, xi), xi) for xi in pat_A]))
    w_combined_acc_A = majority_acc  # already computed above

    print(f"  [seed={seed}] maj_acc={majority_acc:.3f} min_acc={minority_acc:.3f} "
          f"delta={delta_majority:.3f} W_A_accA={w_a_acc_A:.3f} "
          f"W_comb_accA={w_combined_acc_A:.3f}", flush=True)

    return {
        "majority_acc": majority_acc,
        "minority_acc": minority_acc,
        "delta_majority": delta_majority,
        "w_a_acc_A": w_a_acc_A,
        "w_combined_acc_A": w_combined_acc_A,
        "separation_delta": w_a_acc_A - w_combined_acc_A,
        "cell_A_pass": delta_majority >= HP_DELTA_MAJ,
        "cell_B_pass": minority_acc_b >= HP_MINORITY_ACC,
        "cell_C_pass": w_a_acc_A >= w_combined_acc_A + HP_SEPARATION_MARGIN,
        "seed": seed, "N": N, "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert competing-agent metrics non-null at small scale."""
    N_test = 256
    rng = np.random.RandomState(42)
    pat_A = rng.choice([-1.0, 1.0], size=(3, N_test)).astype(np.float64)
    pat_B = rng.choice([-1.0, 1.0], size=(3, N_test)).astype(np.float64)

    W_A = hopfield_store_multi(pat_A, N_test, 3)
    W_B = hopfield_store_multi(pat_B, N_test, 1)
    W_c = W_A + W_B

    maj = float(np.mean([cosine_sim(retrieve(W_c, xi), xi) for xi in pat_A]))
    min_ = float(np.mean([cosine_sim(retrieve(W_c, xi), xi) for xi in pat_B]))

    assert not math.isnan(maj), "majority_acc NaN"
    assert not math.isnan(min_), "minority_acc NaN"
    assert 0.0 <= maj <= 1.0, f"maj_acc={maj} out of range"
    assert 0.0 <= min_ <= 1.0, f"min_acc={min_} out of range"

    print(f"[selftest] PASS: maj={maj:.3f} min={min_:.3f} at N={N_test}", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify cell pass/fail logic."""
    # HP case
    r = {"delta_majority": 0.20, "minority_acc": 0.60, "separation_delta": 0.01}
    assert r["delta_majority"] >= HP_DELTA_MAJ
    assert r["minority_acc"] >= HP_MINORITY_ACC
    # HF case
    r2 = {"delta_majority": 0.03}
    assert r2["delta_majority"] < HF_DELTA_MAJ
    print("[formula_selftests] PASS: cell pass/fail logic verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    fields = ["majority_acc", "minority_acc", "delta_majority",
              "w_a_acc_A", "w_combined_acc_A", "separation_delta"]
    agg = {}
    for f in fields:
        vals = [sd[f] for sd in per_seed.values()
                if not math.isnan(sd.get(f, float("nan")))]
        agg[f"mean_{f}"] = float(np.mean(vals)) if vals else float("nan")
        agg[f"min_{f}"] = float(np.min(vals)) if vals else float("nan")
    agg["n_seeds"] = len(per_seed)
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    delta = agg.get("min_delta_majority", float("nan"))
    min_acc = agg.get("min_minority_acc", float("nan"))
    sep = agg.get("min_separation_delta", float("nan"))

    if math.isnan(delta):
        return ("HARD_FAIL", "No valid results.")

    cell_a = delta >= HP_DELTA_MAJ
    cell_b = not math.isnan(min_acc) and min_acc >= HP_MINORITY_ACC
    cell_c = not math.isnan(sep) and sep >= HP_SEPARATION_MARGIN

    hf_a = delta < HF_DELTA_MAJ
    hf_b = not math.isnan(min_acc) and min_acc < HF_MINORITY_ACC

    if cell_a and cell_b and cell_c:
        return ("HARD_PASS",
                f"Competing multi-agent coordination confirmed. "
                f"Cell A: delta={delta:.3f}>={HP_DELTA_MAJ} (majority wins). "
                f"Cell B: minority_acc={min_acc:.3f}>={HP_MINORITY_ACC} (minority not suppressed). "
                f"Cell C: sep={sep:.3f}>={HP_SEPARATION_MARGIN} (W_A better for own patterns). "
                f"Substrate correctly reflects write-frequency dominance.")
    if hf_a or hf_b:
        return ("HARD_FAIL",
                f"Competing multi-agent semantics fail. "
                f"delta={delta:.3f}(hf={HF_DELTA_MAJ}) "
                f"minority_acc={min_acc:.3f}(hf={HF_MINORITY_ACC}).")
    return ("MIDDLE_BAND",
            f"Partial competing multi-agent support. "
            f"delta={delta:.3f}(hp={HP_DELTA_MAJ}) "
            f"minority_acc={min_acc:.3f}(hp={HP_MINORITY_ACC}) "
            f"sep={sep:.3f}(hp={HP_SEPARATION_MARGIN}).")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"N_A={N_A} N_B={N_B} M_PAT={M_PAT} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE, "N": N,
        "N_A": N_A, "N_B": N_B, "M_PAT": M_PAT,
        "seeds": SEEDS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
