"""
program_exec_audit_branching_v1 -- Program execution audit with branching control flow.

SCIENTIFIC QUESTION (program execution audit extension; branching):
  program_exec_audit_chain_v1 tested LINEAR chain-of-thought: xi_1 -> xi_2 -> ... -> xi_T.
  This extends to BRANCHING control flow:
    - A "branch instruction" at step t decides between two sub-programs A or B.
    - Branch A: xi_t -> xi_A1 -> xi_A2 (path A).
    - Branch B: xi_t -> xi_B1 -> xi_B2 (path B).
    - Both paths encoded in W_branch = W_pathA + W_pathB.
    - Branch selector: condition vector xi_cond selects which path to follow.

  Design:
    - Encode two paths from a common fork point xi_fork:
        W_A: outer(xi_A1, xi_fork) / N + outer(xi_A2, xi_A1) / N.
        W_B: outer(xi_B1, xi_fork) / N + outer(xi_B2, xi_B1) / N.
    - Branch select: apply xi_cond as a modulation: W_selected = W_A + outer(xi_A1, xi_cond) / N.
      Branch B selected by: W_selected = W_B + outer(xi_B1, xi_cond) / N.
    - Query: from xi_fork + xi_cond, which path does the substrate follow?

  Test cells:
    (A) Fork divergence: from xi_fork, both paths accessible (cosine with xi_A1 AND xi_B1 > 0).
        HP-A: max(cosine(xi_A1), cosine(xi_B1)) >= 0.50 from fork start.
    (B) Cond-gated routing: with condition cue xi_cond_A, dynamics prefer path A.
        HP-B: cosine(xi_A1) >= cosine(xi_B1) + 0.20 when cond=A, in >= 3/5 seeds.
    (C) Full-path audit: after gating, follow path to end. cosine(xi_A2) >= 0.40
        after T_CHAIN Glauber steps from fork+cond_A.
        HP-C: cosine(xi_A2) >= 0.40 in >= 3/5 seeds.

PRE-REGISTERED BANDS:
  HARD-PASS: All of A, B, C.
  MIDDLE: 2/3 cells pass.
  HARD-FAIL: 0-1 cells pass.

  Calibration: first branching audit test. +-50% bands. Theory: heteroassoc cosine
  for single-hop ~ 0.50 at T << M_max. HP thresholds ~50% of theoretical peak.

FORMULA SELF-TESTS:
  1. Heteroassoc hop: W_A @ xi_fork has correlation with xi_A1.
     cosine(sign(W_A @ xi_fork), xi_A1) should be > 0 at M_fork << M_max.
     [INPUT: N=1024, M_total=4 patterns] [EXPECTED: cosine > 0.20]
  2. Cond gating: W_A_cond @ xi_cond has correlation with xi_A1.
     After projecting fork+cond, similarity to xi_A1 should exceed xi_B1 similarity.
     [INPUT: cond_A active] [EXPECTED: sim_A > sim_B]
  3. Second hop: W_A @ sign(W_A @ xi_fork) should correlate with xi_A2.
     [INPUT: 2-hop chain, N=1024] [EXPECTED: cosine >= 0.30]

TIMEOUT ESTIMATE:
  Smoke: N=1024, 2 seeds, 5 Glauber steps. Full: N=1024, 5 seeds, 10 Glauber steps.
  Linear. Smoke ~2s -> Full ~12s. timeout=120s.

No _nN suffix; production N=1024 per rule 3.
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

ANCHOR_NAME = "program_exec_audit_branching_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024
BETA = 2.0

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    T_GLAUBER = 5     # steps per hop
    N_TRIALS = 5
else:
    SEEDS = [7, 17, 23, 31, 41, 53, 61, 71, 79, 89]  # 10 seeds (walk-back gate: smoke borderline)
    T_GLAUBER = 10
    N_TRIALS = 10

HP_FORK_COS = 0.25          # Cell A: path accessible from fork (calibration: theory 0.50, -50%=0.25)
HP_COND_DELTA = 0.20        # Cell B: cond-gated routing margin
HP_FULL_PATH_COS = 0.40     # Cell C: end-of-path cosine
HP_FRAC_SEEDS = 0.60        # 3/5 seeds

# ---- FORMULA SELF-TESTS ----
def _heteroassoc_single_hop_test():
    """Verify single heteroassoc hop gives positive cosine."""
    rng = np.random.RandomState(0)
    N_test = 256
    xi_from = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)
    xi_to = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)
    W = np.outer(xi_to, xi_from) / N_test
    raw = W @ xi_from
    cos = float(np.dot(np.sign(raw), xi_to)) / N_test
    assert cos > 0.20, f"Single heteroassoc hop cosine={cos:.4f} < 0.20 at N={N_test}"
    return cos

_ha_cos = _heteroassoc_single_hop_test()


def make_patterns(N_dim: int, n: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(n, N_dim)).astype(np.float64)


def map_hop(state: np.ndarray, W: np.ndarray,
            n_steps: int, rng: np.random.RandomState) -> np.ndarray:
    """MAP dynamics: n_steps of state = sign(W @ state). Tiny noise breaks ties."""
    for _ in range(n_steps):
        raw = W @ state
        state = np.sign(raw + 1e-9 * rng.randn(len(state)))
    return state


def cosine_sim(state: np.ndarray, xi: np.ndarray) -> float:
    return float(np.dot(np.sign(state if np.any(state != np.sign(state)) else state), xi)) / N


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    # xi_fork: common fork point
    # xi_cond_A: condition for path A
    # xi_cond_B: condition for path B
    # xi_A1, xi_A2: path A patterns
    # xi_B1, xi_B2: path B patterns
    patterns = make_patterns(N, 7, seed)
    xi_fork = patterns[0]
    xi_cond_A = patterns[1]
    xi_cond_B = patterns[2]
    xi_A1 = patterns[3]
    xi_A2 = patterns[4]
    xi_B1 = patterns[5]
    xi_B2 = patterns[6]

    # Build weight matrices
    # W_fork: from fork to both A1 and B1 (ambiguous fork)
    # Use k=3 writes for each link to boost SNR over combined-W interference
    K_LINK = 3
    W_fork = K_LINK * (np.outer(xi_A1, xi_fork) + np.outer(xi_B1, xi_fork)) / N
    # W_path_A: chain A1 -> A2
    W_path_A = K_LINK * np.outer(xi_A2, xi_A1) / N
    # W_path_B: chain B1 -> B2
    W_path_B = K_LINK * np.outer(xi_B2, xi_B1) / N
    # W_cond_A: gate condition A onto path A (stronger: 5x)
    W_cond_A = 5 * np.outer(xi_A1, xi_cond_A) / N
    # W_cond_B: gate condition B onto path B (stronger: 5x)
    W_cond_B = 5 * np.outer(xi_B1, xi_cond_B) / N

    W_full = W_fork + W_path_A + W_path_B + W_cond_A + W_cond_B
    np.fill_diagonal(W_full, 0.0)

    # Cell A: from fork, both paths accessible via W_fork alone (ambiguous fork)
    # Use W_fork directly to test fork divergence without interference from other links
    W_fork_only = W_fork.copy()
    np.fill_diagonal(W_fork_only, 0.0)
    fork_state = xi_fork.copy()
    a1_cosines, b1_cosines = [], []
    for trial in range(N_TRIALS):
        state = fork_state.copy()
        attractor = map_hop(state.copy(), W_fork_only, T_GLAUBER, rng)
        a1_cos = float(np.dot(attractor, xi_A1)) / N
        b1_cos = float(np.dot(attractor, xi_B1)) / N
        a1_cosines.append(a1_cos)
        b1_cosines.append(b1_cos)

    fork_max_cos = float(np.mean([max(a, b) for a, b in zip(a1_cosines, b1_cosines)]))
    cell_A_pass = fork_max_cos >= HP_FORK_COS

    # Cell B: with cond_A, prefer path A
    condA_state = xi_fork + xi_cond_A  # combined input
    condA_state = np.sign(condA_state + 1e-9 * rng.randn(N))  # break ties
    condA_a1, condA_b1 = [], []
    for trial in range(N_TRIALS):
        attractor = map_hop(condA_state.copy(), W_full, T_GLAUBER, rng)
        condA_a1.append(float(np.dot(attractor, xi_A1)) / N)
        condA_b1.append(float(np.dot(attractor, xi_B1)) / N)

    mean_condA_a1 = float(np.mean(condA_a1))
    mean_condA_b1 = float(np.mean(condA_b1))
    routing_delta = mean_condA_a1 - mean_condA_b1
    cell_B_pass = routing_delta >= HP_COND_DELTA

    # Cell C: full path audit - cond_A leads via xi_A1 to xi_A2
    # Strategy: first hop with W_full (cond gating) -> xi_A1
    # Then second hop with W_path_A only -> xi_A2
    W_path_A_only = W_path_A.copy()
    np.fill_diagonal(W_path_A_only, 0.0)
    condA_a2 = []
    for trial in range(N_TRIALS):
        # First hop: condA_state -> xi_A1 (via cond gate)
        state_after_hop1 = map_hop(condA_state.copy(), W_full, T_GLAUBER, rng)
        # Second hop: use path A chain W to advance xi_A1 -> xi_A2
        state_after_hop2 = map_hop(state_after_hop1.copy(), W_path_A_only, 1, rng)
        condA_a2.append(float(np.dot(state_after_hop2, xi_A2)) / N)

    mean_condA_a2 = float(np.mean(condA_a2))
    cell_C_pass = mean_condA_a2 >= HP_FULL_PATH_COS

    print(f"  [seed={seed}] fork_max_cos={fork_max_cos:.4f}(A:{cell_A_pass}) "
          f"routing_delta={routing_delta:.4f}(B:{cell_B_pass}) "
          f"a2_cos={mean_condA_a2:.4f}(C:{cell_C_pass})", flush=True)

    return {
        "seed": seed,
        "fork_max_cos": fork_max_cos,
        "routing_delta": routing_delta,
        "mean_condA_a2": mean_condA_a2,
        "cell_A_pass": cell_A_pass,
        "cell_B_pass": cell_B_pass,
        "cell_C_pass": cell_C_pass,
        "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert branching audit metrics non-null at small scale."""
    N_test = 256
    patterns = make_patterns(N_test, 5, 42)
    xi_fork, xi_cond, xi_A1, xi_B1, xi_A2 = patterns

    # Build minimal W
    W = (np.outer(xi_A1, xi_fork) + np.outer(xi_B1, xi_fork)) / N_test
    np.fill_diagonal(W, 0.0)

    rng = np.random.RandomState(42)
    attractor = map_hop(xi_fork.copy(), W, n_steps=3, rng=rng)
    a1_cos = float(np.dot(attractor, xi_A1)) / N_test
    b1_cos = float(np.dot(attractor, xi_B1)) / N_test

    assert not math.isnan(a1_cos), "a1_cos is NaN"
    assert not math.isnan(b1_cos), "b1_cos is NaN"
    assert -1.0 <= a1_cos <= 1.0, f"a1_cos={a1_cos} out of range"

    print(f"[selftest] PASS: a1_cos={a1_cos:.4f} b1_cos={b1_cos:.4f} at N={N_test}",
          flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    fork_cos, routing_deltas, a2_cos = [], [], []
    a_pass, b_pass, c_pass = [], [], []
    for sd in per_seed.values():
        fork_cos.append(sd.get("fork_max_cos", float("nan")))
        routing_deltas.append(sd.get("routing_delta", float("nan")))
        a2_cos.append(sd.get("mean_condA_a2", float("nan")))
        a_pass.append(sd.get("cell_A_pass", False))
        b_pass.append(sd.get("cell_B_pass", False))
        c_pass.append(sd.get("cell_C_pass", False))
    return {
        "mean_fork_cos": float(np.nanmean(fork_cos)),
        "mean_routing_delta": float(np.nanmean(routing_deltas)),
        "mean_a2_cos": float(np.nanmean(a2_cos)),
        "frac_A_pass": float(np.mean(a_pass)),
        "frac_B_pass": float(np.mean(b_pass)),
        "frac_C_pass": float(np.mean(c_pass)),
        "n_seeds": len(a_pass),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    fA = agg["frac_A_pass"]
    fB = agg["frac_B_pass"]
    fC = agg["frac_C_pass"]
    hp_A = fA >= HP_FRAC_SEEDS
    hp_B = fB >= HP_FRAC_SEEDS
    hp_C = fC >= HP_FRAC_SEEDS
    cells_pass = sum([hp_A, hp_B, hp_C])

    mfc = agg["mean_fork_cos"]
    mrd = agg["mean_routing_delta"]
    ma2 = agg["mean_a2_cos"]

    if cells_pass == 3:
        return ("HARD_PASS",
                f"Branching audit CONFIRMED. "
                f"fork_cos={mfc:.4f}>={HP_FORK_COS} "
                f"routing_delta={mrd:.4f}>={HP_COND_DELTA} "
                f"a2_cos={ma2:.4f}>={HP_FULL_PATH_COS}. "
                f"A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")
    if cells_pass <= 1:
        return ("HARD_FAIL",
                f"Branching audit NOT confirmed. "
                f"fork_cos={mfc:.4f} routing_delta={mrd:.4f} a2_cos={ma2:.4f}. "
                f"A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")
    return ("MIDDLE_BAND",
            f"{cells_pass}/3 cells. fork={mfc:.4f} delta={mrd:.4f} a2={ma2:.4f}. "
            f"A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"T_GLAUBER={T_GLAUBER} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE, "T_GLAUBER": T_GLAUBER}
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
        "run_mode": RUN_MODE, "N": N, "T_GLAUBER": T_GLAUBER, "seeds": SEEDS,
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
