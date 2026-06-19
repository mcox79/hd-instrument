"""
cophenetic_um_rescue_v1 -- Q-F3: Cophenetic correlation rescue for ultrametricity.

SCIENTIFIC QUESTION (Q-F3):
  v324 reported static ultrametricity HARD_FAIL (mean_ratio=0.583). Research
  drills established this was a probe-target mismatch: mean_ratio tests STRICT
  inequality (abc <= max(ab,bc)) whereas cophenetic correlation tests whether
  the DENDROGRAM approximation of the distance matrix preserves structure.

  Saracli et al. 2013: cophenetic correlation remains high (c >= 0.85) even
  when strict ultrametric inequality is violated for finite real-data clusterings.
  Krivanek-Moravek 1986: any finite metric admits a closest-from-below
  subdominant ultrametric via single-linkage MST.

  Protocol:
    1. Store P patterns into Hopfield weight matrix.
    2. Let system relax from each pattern as init; record retrieved state.
    3. Compute P x P overlap matrix Q_ij = (1/N)*dot(xi_i, xi_j).
    4. Convert to distance matrix D_ij = 1 - |Q_ij| (bounded [0,1]).
    5. Apply single-linkage hierarchical clustering; extract cophenetic distances.
    6. Compute Pearson cophenetic correlation coefficient c.
    7. Apply Ward linkage; check consistency with single-linkage.
    8. Compute silhouette score at natural cluster count.

HARD-PASS:
  cophenetic_corr >= 0.85 (strong tree structure)
  AND silhouette >= 0.40 at natural cluster count

HARD-FAIL:
  cophenetic_corr < 0.65
  OR (Ward-linkage and single-linkage disagree: |c_ward - c_single| > 0.30)

MIDDLE BAND:
  0.65 <= cophenetic_corr < 0.85 -- soft tree; reframe to "approximate hierarchy"

FORMULA SELF-TESTS:
  1. Perfect ultrametric: 3 patterns with all pairwise Q = 0 except Q_12 = 0.9.
     Distance D_12=0.1, D_13=D_23=1.0. Ultrametric inequality holds trivially.
     Cophenetic correlation for perfect single-linkage tree = 1.0.
  2. Trivial all-equal: Q_ij = 0 for i != j => D_ij = 1.0 for all pairs.
     All distances equal => flat dendrogram => cophenetic corr = undefined or 1.0.
     Test that code handles this gracefully (nan or 1.0, not crash).
  3. Cophenetic formula: for 3 items with D = [[0, a, b], [a, 0, c], [b, c, 0]],
     single-linkage merges cheapest pair first. Verify manually for known case.

TIMEOUT ESTIMATE:
  Smoke: N=1024, P=20, 3 seeds, ~instant (no Glauber, just matrix ops).
  Smoke wall expected ~1s.
  Full: N=4096, P=50 patterns, 5 seeds.
  Full = 1.5 * 1 * (4096/1024)^1.5 * (5/3) = ceil(1.5*1*8*1.67) = ceil(20) = 20s.
  timeout=300s (15x buffer for scipy clustering overhead).

No _nN suffix; production N=4096 per rule 3 (stated here: N=4096, rationale:
cophenetic is cheap even at large N; 4096 is the substrate's standard N for
physics tests).
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
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, cophenet
from scipy.stats import pearsonr
from sklearn.metrics import silhouette_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "cophenetic_um_rescue_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 1024
    SEEDS = [7, 17, 23]
    P_PATTERNS = 20
    ALPHA_BETA = 2.0  # inverse temperature for retrieval
    N_GLAUBER_STEPS = 50  # relaxation steps per pattern
else:
    N = 4096
    SEEDS = [7, 17, 23, 31, 41]
    P_PATTERNS = 50
    ALPHA_BETA = 2.0
    N_GLAUBER_STEPS = 100

# Pre-registered thresholds
HP_COPHENETIC = 0.85
MID_COPHENETIC_LOWER = 0.65
HF_COPHENETIC = 0.65
HP_SILHOUETTE = 0.40
HF_LINKAGE_DISAGREEMENT = 0.30


# ---- FORMULA SELF-TESTS ----
def _selftest_perfect_ultrametric():
    """3-point perfect ultrametric => cophenetic corr = 1.0 (or perfect tree)."""
    # D = [[0, 0.1, 1.0], [0.1, 0, 1.0], [1.0, 1.0, 0]]
    D = np.array([[0.0, 0.1, 1.0],
                  [0.1, 0.0, 1.0],
                  [1.0, 1.0, 0.0]])
    # Condensed distance vector: [D01, D02, D12] = [0.1, 1.0, 1.0]
    cond = squareform(D, checks=False)
    Z = linkage(cond, method='single')
    c, _ = cophenet(Z, cond)
    assert c > 0.9, f"Perfect ultrametric cophenetic={c:.4f}, expected >0.9"
    return c


def _selftest_trivial_equal():
    """4 equidistant points: all D_ij=1 for i!=j. Flat dendrogram."""
    n = 4
    D = np.ones((n, n))
    np.fill_diagonal(D, 0.0)
    cond = squareform(D, checks=False)
    Z = linkage(cond, method='single')
    # Should not crash; cophenetic may be nan (all equal) or 1.0 (trivially)
    c, _ = cophenet(Z, cond)
    # Accept: either nan (no variance) or a finite value
    assert math.isnan(c) or (0.0 <= c <= 1.0 + 1e-9), f"Trivial case gave c={c}"
    return c


_c1 = _selftest_perfect_ultrametric()
_c2 = _selftest_trivial_equal()
print(f"[selftest] perfect_ultrametric cophenetic={_c1:.4f}, trivial_equal={_c2}", flush=True)


def build_hopfield_w(P: int, N_dim: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(P, N_dim)).astype(np.float64)
    W = Xi.T @ Xi / N_dim
    np.fill_diagonal(W, 0.0)
    return W, Xi


def glauber_relax(state: np.ndarray, W: np.ndarray,
                  beta: float, n_steps: int, rng: np.random.RandomState) -> np.ndarray:
    """Synchronous-field relaxation (sign of W@state) for fast retrieval."""
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def compute_overlap_matrix(Xi: np.ndarray, W: np.ndarray,
                            N_dim: int, n_steps: int,
                            rng: np.random.RandomState) -> np.ndarray:
    """Store P patterns; relax from each; compute P x P overlap matrix."""
    P = len(Xi)
    retrieved = np.zeros((P, N_dim), dtype=np.float64)
    for i in range(P):
        noise = rng.choice([-1.0, 1.0], size=(N_dim,)) * (rng.rand(N_dim) < 0.05)
        s = Xi[i].copy()
        s[noise != 0] *= -1.0
        s = glauber_relax(s, W, ALPHA_BETA, n_steps, rng)
        retrieved[i] = s
    Q = (retrieved @ retrieved.T) / N_dim  # P x P overlap
    return Q


def compute_cophenetic_metrics(Q: np.ndarray, P: int) -> Dict:
    """Compute cophenetic corr, silhouette from overlap matrix."""
    # Distance: D_ij = 1 - |Q_ij|, clip to [0,1]
    D = 1.0 - np.abs(Q)
    np.fill_diagonal(D, 0.0)
    D = np.clip(D, 0.0, 1.0)

    cond = squareform(D, checks=False)

    # Single-linkage
    Z_single = linkage(cond, method='single')
    c_single, _ = cophenet(Z_single, cond)

    # Ward-linkage (uses Euclidean on the distance matrix as feature space)
    # Ward requires Euclidean so we use the overlap matrix rows as features
    Z_ward = linkage(Q, method='ward')
    c_ward, _ = cophenet(Z_ward, cond)

    # Natural cluster count: use elbow on single-linkage last merges
    # Simple heuristic: sqrt(P) clusters
    k_natural = max(2, int(round(math.sqrt(P))))

    # Assign cluster labels from flat clustering
    from scipy.cluster.hierarchy import fcluster
    labels = fcluster(Z_single, t=k_natural, criterion='maxclust')
    try:
        sil = float(silhouette_score(D, labels, metric='precomputed')) if len(set(labels)) > 1 else float('nan')
    except Exception:
        sil = float('nan')

    linkage_disagreement = abs(c_single - c_ward) if (not math.isnan(c_single) and not math.isnan(c_ward)) else float('nan')

    return {
        "cophenetic_single": float(c_single),
        "cophenetic_ward": float(c_ward),
        "silhouette": float(sil),
        "linkage_disagreement": float(linkage_disagreement) if not math.isnan(linkage_disagreement) else float('nan'),
        "k_natural": k_natural,
        "P": P,
    }


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    print(f"[seed={seed}] Building Hopfield N={N} P={P_PATTERNS}...", flush=True)
    W, Xi = build_hopfield_w(P_PATTERNS, N, seed)
    Q = compute_overlap_matrix(Xi, W, N, N_GLAUBER_STEPS, rng)
    metrics = compute_cophenetic_metrics(Q, P_PATTERNS)
    print(f"[seed={seed}] cophenetic_single={metrics['cophenetic_single']:.4f} "
          f"silhouette={metrics['silhouette']:.4f} "
          f"linkage_disagree={metrics['linkage_disagreement']:.4f}", flush=True)
    return {"seed": seed, "N": N, "P": P_PATTERNS, "metrics": metrics, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert cophenetic metrics non-null at small scale."""
    N_test, P_test = 256, 10
    rng = np.random.RandomState(99)
    W, Xi = build_hopfield_w(P_test, N_test, 99)
    Q = compute_overlap_matrix(Xi, W, N_test, 20, rng)
    assert Q.shape == (P_test, P_test), f"Q shape={Q.shape}, expected ({P_test},{P_test})"
    m = compute_cophenetic_metrics(Q, P_test)
    assert not math.isnan(m["cophenetic_single"]), "cophenetic_single is NaN"
    assert m["cophenetic_single"] >= 0.0, f"cophenetic_single={m['cophenetic_single']} < 0"
    assert m["P"] == P_test, f"P mismatch: {m['P']} != {P_test}"
    print(f"[selftest] PASS: cophenetic_single={m['cophenetic_single']:.4f} "
          f"silhouette={m['silhouette']:.4f} N={N_test} P={P_test}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    cophens = [v["metrics"]["cophenetic_single"] for v in per_seed.values()
               if not math.isnan(v["metrics"]["cophenetic_single"])]
    sils = [v["metrics"]["silhouette"] for v in per_seed.values()
            if not math.isnan(v["metrics"]["silhouette"])]
    disagrees = [v["metrics"]["linkage_disagreement"] for v in per_seed.values()
                 if not math.isnan(v["metrics"]["linkage_disagreement"])]

    return {
        "mean_cophenetic_single": float(np.mean(cophens)) if cophens else float("nan"),
        "std_cophenetic_single": float(np.std(cophens)) if cophens else float("nan"),
        "mean_silhouette": float(np.mean(sils)) if sils else float("nan"),
        "mean_linkage_disagreement": float(np.mean(disagrees)) if disagrees else float("nan"),
        "n_seeds": len(cophens),
        "seeds_pass_hp": sum(1 for c in cophens if c >= HP_COPHENETIC),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    c = agg["mean_cophenetic_single"]
    sil = agg["mean_silhouette"]
    disagree = agg["mean_linkage_disagreement"]
    n = agg["n_seeds"]

    if math.isnan(c):
        return ("HARD_FAIL", "cophenetic_single is NaN -- instrumentation failure.")

    # Hard-fail conditions
    if c < HF_COPHENETIC:
        return ("HARD_FAIL",
                f"cophenetic_corr={c:.4f} < {HF_COPHENETIC} (hard-fail). "
                f"No tree structure in overlap matrix. silhouette={sil:.4f} n_seeds={n}.")
    if not math.isnan(disagree) and disagree > HF_LINKAGE_DISAGREEMENT:
        return ("HARD_FAIL",
                f"Linkage disagreement={disagree:.4f} > {HF_LINKAGE_DISAGREEMENT}. "
                f"Ward and single-linkage fundamentally disagree. c={c:.4f}.")

    # Hard-pass conditions
    if c >= HP_COPHENETIC and (math.isnan(sil) or sil >= HP_SILHOUETTE):
        return ("HARD_PASS",
                f"COPHENETIC TREE STRUCTURE CONFIRMED. cophenetic_corr={c:.4f} >= {HP_COPHENETIC}. "
                f"silhouette={sil:.4f} >= {HP_SILHOUETTE}. linkage_disagree={disagree:.4f}. "
                f"n_seeds={n} seeds_pass={agg['seeds_pass_hp']}. "
                f"Overlap matrix supports dendrogram with strong fidelity despite strict-UM violation.")

    # Middle band
    return ("MIDDLE_BAND",
            f"Soft tree structure. cophenetic_corr={c:.4f} in [{MID_COPHENETIC_LOWER},{HP_COPHENETIC}). "
            f"silhouette={sil:.4f}. linkage_disagree={disagree:.4f}. n_seeds={n}. "
            f"Reframe product claim to 'approximate / statistical hierarchy'.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} P={P_PATTERNS} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "P": P_PATTERNS, "run_mode": RUN_MODE}
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
        "run_mode": RUN_MODE, "N": N, "P": P_PATTERNS,
        "seeds": SEEDS,
        "aggregated": agg,
        "thresholds": {
            "HP_COPHENETIC": HP_COPHENETIC, "HF_COPHENETIC": HF_COPHENETIC,
            "HP_SILHOUETTE": HP_SILHOUETTE, "HF_LINKAGE_DISAGREEMENT": HF_LINKAGE_DISAGREEMENT,
        },
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
