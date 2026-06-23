"""sparse_engram_allocation_smoke_v1 -- substrate-native sparse competitive
allocation per Tonegawa engram-cell biology.

USER reframe 2026-06-22 / 2026-06-23: brain analog -- only ~1-3% of neurons
fire for any stimulus; engram-cell allocation is COMPETITIVE: the most-excited
neurons get recruited via CREB/calcineurin excitability gating
(Tonegawa 2007+ Cell, Josselyn 2015). Cerebellar granule cells use K=4-8
mossy-fiber fan-in (Cayco-Gajic 2017; Litwin-Kumar 2017). Drosophila Kenyon
cells use K=6-8.

Triple-leverage hypothesis: sparse competitive allocation gives substrate
simultaneously
  (a) higher capacity (sparse codes have less interference; Frady-Sommer 2018
      ~10x more atoms per N_DIM),
  (b) better noise tolerance (sparse codes survive higher sigma; Cayco-Gajic
      2017 K=5 noise-robust),
  (c) emergent clustering (competitive allocation IS clustering; functionally
      similar atoms compete for the same ensemble -> Tonegawa engram pattern).

5 arms:
  ARM_DENSE_BASELINE       full N_DIM bipolar (current substrate); reference.
  ARM_SPARSE_K100          100 nonzero / 4096 (2.5% sparse).
  ARM_SPARSE_K50           50 nonzero / 4096 (1.25%).
  ARM_SPARSE_K20           20 nonzero / 4096 (0.5%, close to cerebellar ratio).
  ARM_SPARSE_K10_COMPETITIVE
                           10 nonzero / 4096 (0.25%) + competitive allocation:
                           when writing atom i, sample 10 candidate position
                           sets, score by inner-product against existing W
                           rows, pick lowest-collision set (CREB-style
                           competition).

Metrics:
  (A) cleanup recall@1 at each (M, sigma) combo per arm.
  (B) capacity at sigma=1.0  : largest M s.t. recall@1 >= 0.80.
  (C) clustering emergence   : k-means purity of planted mechanism-family
      clusters at the ATOM EMBEDDING (does competitive allocation give
      better family separation than dense?).

Pre-reg (preregs/2026-06-23_sparse_engram_allocation_smoke_v1.md):
  HARD_PASS: ARM_SPARSE_K10_COMPETITIVE achieves ALL THREE:
    - recall@1 at sigma=1.5 >= 0.10 (noise lift over dense Shannon-floor ~0.02)
    - capacity at sigma=1.0 >= 2 * ARM_DENSE_BASELINE
    - clustering purity >= ARM_DENSE_BASELINE.purity + 0.10
  HARD_FAIL: ARM_SPARSE_K10_COMPETITIVE
    - recall@1 at sigma=1.5 <= ARM_DENSE_BASELINE + 0.01
    - AND capacity not lifted
    - AND clustering not improved
  MIDDLE_BAND: 1-or-2 of 3 benefits realized; partial mechanism.

Sanity self-tests (must hold for ALL arms):
  - sigma=0 endpoint     : recall@1 == 1.000 (clean cue, perfect cleanup)
  - low-load endpoint    : M=10, sigma=0  : recall@1 == 1.000

CPU; numpy-only; ASCII; per-seed checkpoint; seeds = [7, 17, 23].
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "sparse_engram_allocation_smoke_v1"

# CLI
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = _HDLAB_NAME.endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else "full"

# config: smoke is fast-but-real (N_DIM=512, M=200, single seed); full is full grid
if RUN_MODE == "smoke":
    SEEDS = [7]
    N_DIM = 512
    M_MAX = 200
    N_EVAL = 40
    SIGMA_TEST = [0.0, 0.5, 1.0, 1.5]
    M_SWEEP = [10, 50, 100, 200]
    N_FAMILIES_PLANTED = 5
    N_PER_FAMILY = 6
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    M_MAX = 10000
    N_EVAL = 200
    SIGMA_TEST = [0.0, 0.5, 1.0, 1.5, 2.0]
    M_SWEEP = [10, 100, 500, 1000, 2500, 5000, 10000]
    N_FAMILIES_PLANTED = 10
    N_PER_FAMILY = 20

# K_sparse sweep (defined relative to N_DIM for sparsity ratios)
# DENSE = full N_DIM. K_SPARSE = number of nonzero entries.
ARM_NAMES = [
    "ARM_DENSE_BASELINE",
    "ARM_SPARSE_K100",
    "ARM_SPARSE_K50",
    "ARM_SPARSE_K20",
    "ARM_SPARSE_K10_COMPETITIVE",
]

def _arm_k(arm_name: str) -> int | None:
    if arm_name == "ARM_DENSE_BASELINE":
        return None
    if arm_name == "ARM_SPARSE_K100":
        return 100
    if arm_name == "ARM_SPARSE_K50":
        return 50
    if arm_name == "ARM_SPARSE_K20":
        return 20
    if arm_name == "ARM_SPARSE_K10_COMPETITIVE":
        return 10
    raise ValueError("unknown arm: %s" % arm_name)

def _arm_competitive(arm_name: str) -> bool:
    return arm_name == "ARM_SPARSE_K10_COMPETITIVE"

# pre-registered HARD bands
HP_NOISE_FLOOR_SIGMA = 1.5
HP_NOISE_RECALL_FLOOR = 0.10
HP_CAPACITY_LIFT_MULT = 2.0
HP_CLUSTER_PURITY_GAP = 0.10
CAPACITY_SIGMA = 1.0
CAPACITY_RECALL_THRESHOLD = 0.80

# clustering: planted mechanism families
# (each "family" gets N_PER_FAMILY atoms that share a base vector + small noise)
PLANTED_FAMILY_NOISE_SIGMA = 0.3

CONFIG_VERSION = (
    "sparse_engram_allocation_smoke_v1: 5 arms "
    "(DENSE / K100 / K50 / K20 / K10_COMPETITIVE); "
    "N_DIM=%d M_MAX=%d N_EVAL=%d sigmas=%s; "
    "HP: noise-sigma=%.1f recall_floor=%.2f AND capacity-lift>=%.1fx AND cluster-gap>=%.2f"
) % (N_DIM, M_MAX, N_EVAL, SIGMA_TEST, HP_NOISE_FLOOR_SIGMA,
     HP_NOISE_RECALL_FLOOR, HP_CAPACITY_LIFT_MULT, HP_CLUSTER_PURITY_GAP)


# ===== atom generators =====

def make_dense_atom(n_dim: int, rng: np.random.Generator) -> np.ndarray:
    """Full bipolar dense atom (the current substrate baseline)."""
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def make_sparse_atom(n_dim: int, k: int, rng: np.random.Generator) -> np.ndarray:
    """k-sparse bipolar atom: k randomly placed +/-1 entries, rest zero."""
    out = np.zeros(n_dim, dtype=np.float32)
    positions = rng.choice(n_dim, size=k, replace=False)
    signs = rng.integers(0, 2, size=k) * 2 - 1
    out[positions] = signs.astype(np.float32)
    return out


def make_competitive_sparse_atom(
    n_dim: int,
    k: int,
    existing_W: np.ndarray,
    n_existing: int,
    rng: np.random.Generator,
    n_candidates: int = 10,
) -> np.ndarray:
    """Sparse atom with CREB-style competitive allocation:
    sample n_candidates candidate position-sets, score each by sum-abs of
    inner-products against existing W rows, pick the lowest-collision one.
    Vectorized: build all candidates as a [n_candidates, n_dim] matrix and
    do a single matmul with existing_W to score them all at once.
    """
    if n_existing == 0:
        # no existing atoms to compete against; just produce a sparse atom
        return make_sparse_atom(n_dim, k, rng)
    # build all candidates as a sparse matrix
    cands = np.zeros((n_candidates, n_dim), dtype=np.float32)
    for c in range(n_candidates):
        positions = rng.choice(n_dim, size=k, replace=False)
        signs = rng.integers(0, 2, size=k) * 2 - 1
        cands[c, positions] = signs.astype(np.float32)
    # single matmul: [n_existing, n_dim] @ [n_dim, n_candidates] = [n_existing, n_candidates]
    sims = existing_W[:n_existing] @ cands.T
    # score per candidate = sum of abs sims with existing rows
    scores = np.sum(np.abs(sims), axis=0)
    best_idx = int(np.argmin(scores))
    return cands[best_idx]


# ===== build W per arm =====

def build_W(arm_name: str, n_dim: int, M: int,
            rng: np.random.Generator) -> np.ndarray:
    """Build memory matrix W of shape [M, n_dim] for the given arm."""
    k = _arm_k(arm_name)
    competitive = _arm_competitive(arm_name)
    W = np.zeros((M, n_dim), dtype=np.float32)
    if arm_name == "ARM_DENSE_BASELINE":
        for i in range(M):
            W[i] = make_dense_atom(n_dim, rng)
        return W
    # sparse arms
    assert k is not None
    if not competitive:
        for i in range(M):
            W[i] = make_sparse_atom(n_dim, k, rng)
        return W
    # competitive sparse
    for i in range(M):
        W[i] = make_competitive_sparse_atom(n_dim, k, W, i, rng, n_candidates=10)
    return W


# ===== cleanup recall =====

def add_noise(cue: np.ndarray, sigma: float,
              rng: np.random.Generator) -> np.ndarray:
    """Add gaussian noise of stddev sigma to a cue vector."""
    if sigma <= 0:
        return cue.copy()
    noise = rng.normal(0.0, sigma, size=cue.shape).astype(np.float32)
    return cue + noise


def cleanup_recall_at_1(W: np.ndarray, sigma: float,
                        n_eval: int, rng: np.random.Generator) -> float:
    """Pick n_eval random atoms; add noise; recall@1 via argmax(W @ cue)."""
    M = W.shape[0]
    n_eval = min(n_eval, M)
    idxs = rng.choice(M, size=n_eval, replace=False)
    cues = W[idxs]  # [n_eval, N_DIM]
    noisy = add_noise(cues, sigma, rng)  # [n_eval, N_DIM]
    sims = noisy @ W.T  # [n_eval, M]
    preds = sims.argmax(axis=1)
    correct = int(np.sum(preds == idxs))
    return correct / n_eval


# ===== capacity-at-sigma =====

def capacity_at_sigma_from_W(W_full: np.ndarray, m_sweep: list[int],
                              sigma: float, n_eval: int, recall_thresh: float,
                              rng: np.random.Generator) -> int:
    """Largest M in m_sweep where cleanup recall@1 >= recall_thresh, computed
    by SUBSETTING W_full[:M]. Avoids rebuilding W per M-point.
    Returns 0 if no M crosses the threshold."""
    best_M = 0
    M_full = W_full.shape[0]
    for M in m_sweep:
        if M > M_full:
            break
        W = W_full[:M]
        r = cleanup_recall_at_1(W, sigma, n_eval, rng)
        if r >= recall_thresh:
            best_M = M
        else:
            # capacity sweep is monotone-down in recall; once we drop,
            # higher M won't recover at this sigma. Break early.
            break
    return best_M


# ===== clustering: planted mechanism families =====

def build_planted_family_atoms(
    arm_name: str,
    n_dim: int,
    n_families: int,
    n_per_family: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Build atoms with planted family-structure: family base + within-family noise.

    Returns (W_planted [n_families*n_per_family, n_dim], family_labels [N]).
    For sparse arms, the base is sparse and "noise" flips a small fraction of
    nonzero entries' signs. For dense arms, noise is gaussian then sign-binarized.
    """
    k = _arm_k(arm_name)
    competitive = _arm_competitive(arm_name)
    N = n_families * n_per_family
    W = np.zeros((N, n_dim), dtype=np.float32)
    labels = np.zeros(N, dtype=np.int64)

    for fam in range(n_families):
        if arm_name == "ARM_DENSE_BASELINE":
            base = make_dense_atom(n_dim, rng)
        else:
            assert k is not None
            base = make_sparse_atom(n_dim, k, rng)
        for j in range(n_per_family):
            idx = fam * n_per_family + j
            atom = base.copy()
            if arm_name == "ARM_DENSE_BASELINE":
                # add gaussian noise + re-sign
                noise = rng.normal(0.0, PLANTED_FAMILY_NOISE_SIGMA,
                                   size=n_dim).astype(np.float32)
                atom = np.sign(atom + noise).astype(np.float32)
                atom[atom == 0] = 1.0
            else:
                # flip a small fraction of the nonzero entries' signs
                nz_positions = np.where(np.abs(base) > 0)[0]
                if len(nz_positions) > 0:
                    n_flip = max(0, int(round(PLANTED_FAMILY_NOISE_SIGMA
                                              * len(nz_positions))))
                    if n_flip > 0:
                        flip = rng.choice(nz_positions, size=n_flip, replace=False)
                        atom[flip] = -atom[flip]
            W[idx] = atom
            labels[idx] = fam

    # For competitive arm, also run competitive allocation NO-OP (the planted
    # structure is the point of this metric; competition would destroy the
    # plant). We test whether the family signal SURVIVES the arm's atom
    # representation, not whether competition discovers families.
    # NOTE: competitive=True doesn't change build above; this is intentional.
    _ = competitive
    return W, labels


# ===== k-means (numpy-only Lloyd) =====

def kmeans_simple(X: np.ndarray, k: int, seed: int, n_iter: int = 50) -> np.ndarray:
    """Plain Lloyd's k-means on cosine-normalized rows; returns cluster ids [N]."""
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    Xn = X / norms
    init_idx = rng.choice(n, size=min(k, n), replace=False)
    centers = Xn[init_idx].copy()
    assign = np.zeros(n, dtype=np.int64)
    for _ in range(n_iter):
        sims = Xn @ centers.T
        new_assign = sims.argmax(axis=1)
        if np.array_equal(new_assign, assign):
            break
        assign = new_assign
        for kk in range(min(k, n)):
            mask = assign == kk
            if mask.any():
                m = Xn[mask].mean(axis=0)
                mn = np.linalg.norm(m) + 1e-8
                centers[kk] = m / mn
    return assign


def cluster_purity(labels: np.ndarray, gt: np.ndarray) -> float:
    """Modal-label fraction per cluster; weighted average."""
    n = len(gt)
    if n == 0:
        return 0.0
    total_correct = 0
    for c in sorted(set(labels.tolist())):
        idxs = [i for i, lab in enumerate(labels) if lab == c]
        if not idxs:
            continue
        true_at_idx = [int(gt[i]) for i in idxs]
        counts: dict[int, int] = {}
        for t in true_at_idx:
            counts[t] = counts.get(t, 0) + 1
        total_correct += max(counts.values())
    return total_correct / n


# ===== self-test =====

def _selftest():
    """Quick endpoint sanity: sigma=0 + low-M => recall@1 == 1.000 for all arms."""
    n_dim_test = 256
    M_test = 10
    rng = np.random.default_rng(0)
    for arm in ARM_NAMES:
        W = build_W(arm, n_dim_test, M_test, rng)
        # endpoint: sigma=0 + M=10 => perfect recall by construction
        r = cleanup_recall_at_1(W, sigma=0.0, n_eval=M_test,
                                rng=np.random.default_rng(1))
        assert r == 1.0, (
            "[selftest] FAIL: arm=%s sigma=0 M=%d recall=%.3f (must be 1.000)"
            % (arm, M_test, r)
        )
        # capacity sweep sanity: capacity_at_sigma_from_W returns int >= 0
        W_for_cap = build_W(arm, n_dim_test, 10, np.random.default_rng(99))
        cap = capacity_at_sigma_from_W(W_for_cap, [5, 10], sigma=0.0,
                                       n_eval=5, recall_thresh=0.80,
                                       rng=np.random.default_rng(2))
        assert cap >= 5, "[selftest] FAIL: arm=%s capacity at sigma=0 = %d" % (arm, cap)
        # planted-family clustering sanity
        Wp, labels = build_planted_family_atoms(arm, n_dim_test, 3, 4,
                                                rng=np.random.default_rng(3))
        cl = kmeans_simple(Wp, k=3, seed=0)
        pur = cluster_purity(cl, labels)
        assert 0.0 <= pur <= 1.0, "[selftest] FAIL: arm=%s purity=%.3f" % (arm, pur)
    print("[selftest] PASS: all 5 arms sigma=0 M=%d recall=1.000 + capacity sane + "
          "clustering sane" % M_test, flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ===== main run =====

def run_one_seed(seed: int) -> dict:
    """Run all 5 arms x sigma sweep x M sweep + planted-family clustering."""
    t0 = time.time()
    arm_results: dict[str, dict] = {}

    for arm in ARM_NAMES:
        arm_t0 = time.time()
        print("[%s] seed=%d arm=%s starting" % (ANCHOR_NAME, seed, arm), flush=True)

        # Build W ONCE at M_MAX, then subset for the (M, sigma) recall grid +
        # capacity sweep. This is principled: atoms generated at M=M_MAX form
        # a valid M'<=M_MAX substrate via W[:M']. For competitive allocation,
        # the lowest-collision atoms are written first; subsetting to M' uses
        # the first M' atoms, which is the natural "small-substrate" snapshot.
        # Avoids O(M^2) rebuild cost for competitive arm.
        rng = np.random.default_rng(seed)
        W_full = build_W(arm, N_DIM, M_MAX, rng)

        # (A) cleanup recall over (M, sigma) grid via subsetting
        recall_grid: dict[str, dict[str, float]] = {}
        for M in M_SWEEP:
            if M > M_MAX:
                continue
            W = W_full[:M]
            row: dict[str, float] = {}
            for sigma in SIGMA_TEST:
                r = cleanup_recall_at_1(W, sigma, N_EVAL,
                                        rng=np.random.default_rng(seed + int(sigma * 100) + M))
                row["sigma_%.1f" % sigma] = float(r)
            recall_grid["M_%d" % M] = row

        # (B) capacity at sigma=1.0 -- largest M with recall >= threshold
        rng_cap = np.random.default_rng(seed + 31337)
        capacity = capacity_at_sigma_from_W(W_full, M_SWEEP, CAPACITY_SIGMA,
                                            N_EVAL, CAPACITY_RECALL_THRESHOLD, rng_cap)

        # noise-floor metric: recall at M=M_MAX, sigma=HP_NOISE_FLOOR_SIGMA
        noise_recall = recall_grid["M_%d" % M_MAX]["sigma_%.1f" % HP_NOISE_FLOOR_SIGMA]

        # (C) clustering purity on planted family atoms
        rng_cl = np.random.default_rng(seed + 91)
        Wp, labels = build_planted_family_atoms(arm, N_DIM, N_FAMILIES_PLANTED,
                                                N_PER_FAMILY, rng_cl)
        cluster_labels = kmeans_simple(Wp, k=N_FAMILIES_PLANTED, seed=seed)
        purity = cluster_purity(cluster_labels, labels)

        arm_elapsed = time.time() - arm_t0
        arm_results[arm] = {
            "recall_grid": recall_grid,
            "capacity_at_sigma_1p0": int(capacity),
            "noise_recall_sigma_%.1f" % HP_NOISE_FLOOR_SIGMA: float(noise_recall),
            "cluster_purity": float(purity),
            "arm_elapsed_s": float(arm_elapsed),
        }
        print(
            "[%s] seed=%d arm=%s done: cap@s1.0=%d noise@s%.1f=%.3f purity=%.3f (%.1fs)"
            % (ANCHOR_NAME, seed, arm, capacity, HP_NOISE_FLOOR_SIGMA,
               noise_recall, purity, arm_elapsed),
            flush=True,
        )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "M": M_MAX,
        "run_mode": RUN_MODE,
        "arms": arm_results,
        "elapsed_s": elapsed,
    }


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[%s] start mode=%s seeds=%s N_DIM=%d M_MAX=%d arms=%d"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M_MAX, len(ARM_NAMES)),
          flush=True)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "M": M_MAX}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[%s] ckpt: %d done; running %d" %
          (ANCHOR_NAME, len(done), len(remaining)), flush=True)

    for seed in remaining:
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)

    # aggregate across seeds
    # collect per-arm: mean noise-recall, mean capacity, mean purity
    per_arm_summary: dict[str, dict] = {}
    for arm in ARM_NAMES:
        noise_vals = [per_seed[str(s)]["arms"][arm]
                      ["noise_recall_sigma_%.1f" % HP_NOISE_FLOOR_SIGMA]
                      for s in SEEDS]
        cap_vals = [per_seed[str(s)]["arms"][arm]["capacity_at_sigma_1p0"]
                    for s in SEEDS]
        pur_vals = [per_seed[str(s)]["arms"][arm]["cluster_purity"]
                    for s in SEEDS]
        per_arm_summary[arm] = {
            "noise_recall_mean": float(np.mean(noise_vals)),
            "noise_recall_std": float(np.std(noise_vals)),
            "capacity_mean": float(np.mean(cap_vals)),
            "capacity_std": float(np.std(cap_vals)),
            "purity_mean": float(np.mean(pur_vals)),
            "purity_std": float(np.std(pur_vals)),
        }

    dense = per_arm_summary["ARM_DENSE_BASELINE"]
    comp = per_arm_summary["ARM_SPARSE_K10_COMPETITIVE"]

    # HP/HF/MIDDLE evaluation
    hp_noise_ok = comp["noise_recall_mean"] >= HP_NOISE_RECALL_FLOOR
    hp_cap_ok = (comp["capacity_mean"]
                 >= HP_CAPACITY_LIFT_MULT * max(1.0, dense["capacity_mean"]))
    hp_cluster_ok = (comp["purity_mean"]
                     >= dense["purity_mean"] + HP_CLUSTER_PURITY_GAP)

    hf_noise = comp["noise_recall_mean"] <= dense["noise_recall_mean"] + 0.01
    hf_cap = comp["capacity_mean"] <= dense["capacity_mean"]
    hf_cluster = comp["purity_mean"] <= dense["purity_mean"]

    if hp_noise_ok and hp_cap_ok and hp_cluster_ok:
        verdict = "HARD_PASS"
    elif hf_noise and hf_cap and hf_cluster:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    # endpoint sanity sweep across all arms at sigma=0 + M=10 -> all must be 1.000
    endpoint_ok = True
    for arm in ARM_NAMES:
        # M=10 in M_SWEEP? smoke M_SWEEP starts [10,...]; full starts [10,...]
        m10_key = "M_10"
        if m10_key not in per_seed[str(SEEDS[0])]["arms"][arm]["recall_grid"]:
            # if 10 isn't in the sweep, skip
            continue
        rs = [per_seed[str(s)]["arms"][arm]["recall_grid"][m10_key]["sigma_0.0"]
              for s in SEEDS]
        if not all(r == 1.0 for r in rs):
            endpoint_ok = False
    if not endpoint_ok:
        verdict = "HARD_FAIL"
        verdict_extra = "_ENDPOINT_VIOLATION"
    else:
        verdict_extra = ""

    elapsed_s = float(sum(per_seed[str(s)]["elapsed_s"] for s in SEEDS))

    verdict_msg = (
        "%s%s_%s_%dseeds_N%d_Mmax%d_DENSE_noise%.3f_cap%.0f_pur%.3f_"
        "COMP_noise%.3f_cap%.0f_pur%.3f_HPnoise=%s_HPcap=%s_HPcluster=%s_"
        "endpoint=%s_elapsed_%.1fs"
    ) % (
        verdict, verdict_extra, RUN_MODE.upper(), len(SEEDS), N_DIM, M_MAX,
        dense["noise_recall_mean"], dense["capacity_mean"], dense["purity_mean"],
        comp["noise_recall_mean"], comp["capacity_mean"], comp["purity_mean"],
        hp_noise_ok, hp_cap_ok, hp_cluster_ok,
        endpoint_ok, elapsed_s,
    )

    summary = {
        "anchor": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "seeds": SEEDS,
        "N_DIM": N_DIM,
        "M_MAX": M_MAX,
        "N_EVAL": N_EVAL,
        "SIGMA_TEST": SIGMA_TEST,
        "M_SWEEP": M_SWEEP,
        "arms": per_arm_summary,
        "hp_gates": {
            "hp_noise_ok": hp_noise_ok,
            "hp_cap_ok": hp_cap_ok,
            "hp_cluster_ok": hp_cluster_ok,
            "endpoint_ok": endpoint_ok,
            "hp_noise_floor": HP_NOISE_RECALL_FLOOR,
            "hp_noise_sigma": HP_NOISE_FLOOR_SIGMA,
            "hp_capacity_lift_mult": HP_CAPACITY_LIFT_MULT,
            "hp_cluster_gap": HP_CLUSTER_PURITY_GAP,
        },
        "hf_gates": {
            "hf_noise": hf_noise,
            "hf_cap": hf_cap,
            "hf_cluster": hf_cluster,
        },
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed_s,
        "summary": summary,
        "per_seed": per_seed,
    }

    write_metrics(out_dir, metrics)
    print("[%s] %s" % (ANCHOR_NAME, verdict_msg), flush=True)


if __name__ == "__main__":
    main()
