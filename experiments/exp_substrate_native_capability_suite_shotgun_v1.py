"""substrate_native_capability_suite_shotgun_v1 -- unified substrate-native capability benchmark on SYNTHETIC apples-to-apples.

Strategic rationale (USER 2026-06-24 master bias checklist Lane 1):
Chain-grade individual capabilities (ANCHOR 1 M=20 capacity-respecting / ANCHOR 2 K10-K20 compositional /
brain-aligned shotgun ARM 1-4 pattern-completion/WM/bidirectional) exist as SEPARATE cells. No unified
substrate-native benchmark suite exists. This cell ships the first comprehensive substrate-native
capability snapshot at production-scale on clean synthetic data (no corpus + no encoder leakage).

Lane 1 declaration: substrate-native capability ONLY. ALL arms use SAME substrate primitives (HRR
bind/unbind + sparse-bipolar codebook). Only the TASK varies. INTRA_LANE_DELTA per arm = ONE substrate
capability dimension. NO corpus, NO Pythia, NO word2vec, NO transformer baselines. Pure substrate.

Cell: 6 arms x 3 seeds x N_DIM=8192 x sparse-bipolar f=0.05 codebook (apples-to-apples).
  ARM_PATTERN_COMPLETION_AT_CORRUPTION -- M=200 patterns; corrupt 50% bits; top-1 recovery.
  ARM_COMPOSITIONAL_GENERALIZATION_HOLDOUT -- 400 (subj,obj) pairs; bind 200; recover 200 heldout.
  ARM_WORKING_MEMORY_CAPACITY_SCALING -- k in {1,4,7,10,15,20,30}; capacity at 90% accuracy.
  ARM_RETRIEVAL_PRECISION_AT_LOAD -- M in {100,500,1000,2000}; recall@1 sweep at fixed N_DIM.
  ARM_SEQUENCE_BINDING_LOSSLESS -- K in {5,10,20,50}; sequence bind/unbind exact-recovery.
  ARM_SPARSITY_F_SWEEP -- f in {0.005,0.01,0.02,0.05,0.10}; capacity at each f at N_DIM=8192.

Pre-reg HARD bands per arm (sacrosanct both directions; per master checklist top-5 bias #2):
  ARM_PATTERN_COMPLETION HARD_PASS top1 >= 0.85 (consistent w/ brain-aligned ARM 1 reference);
                         HARD_FAIL < 0.50.
  ARM_COMPOSITIONAL_GEN HARD_PASS heldout top1 >= 0.50 (CORRECTED protocol not pair-collision-bound);
                        HARD_FAIL < 0.20.
  ARM_WORKING_MEMORY HARD_PASS k_capacity_at_90pct >= 7 (Miller 7+/-2); HARD_FAIL < 4.
  ARM_RETRIEVAL_PRECISION HARD_PASS recall@1 at M=1000 >= 0.95; HARD_FAIL < 0.70.
  ARM_SEQUENCE_BINDING HARD_PASS exact recovery at K=20 >= 0.99 (lossless target); HARD_FAIL < 0.90.
  ARM_SPARSITY_F HARD_PASS capacity at f=0.02 >= 1.5x capacity at f=0.05; HARD_FAIL if f=0.02 <= f=0.05
                 (decision rule per substrate-mining drill).

Cell-level verdict:
  ARM_SUITE_NATIVE_ALIVE: ALL 6 arms HARD_PASS -> substrate-native capability uniformly chain-grade.
  ARM_SUITE_NATIVE_PARTIAL: 4-5 of 6 arms HARD_PASS -> substrate has strong native suite + 1-2 gaps.
  ARM_SUITE_NATIVE_DEAD: <=3 of 6 arms HARD_PASS -> substrate-native suite has fundamental gaps.

Confounds per arm (CONFOUND_AUDIT per master checklist top-5 bias #3-5):
  ARM_PATTERN_COMPLETION: (1) M=200 vs capacity at f=0.05 N_DIM=8192; (2) corrupt_frac sweep coverage;
                          (3) cleanup-cosine vs top-1-accuracy as different metrics.
  ARM_COMPOSITIONAL_GEN: (1) coverage at 50% may saturate sparse-bipolar crosstalk at 200 bindings;
                         (2) pair-collision-bound chance is 1/n_obj=0.05;
                         (3) heldout top-1 != in-distribution top-1 -- both reported.
  ARM_WORKING_MEMORY: (1) crosstalk scaling k*f^2/D vs signal; (2) item-pool size confounds chance;
                      (3) trials_per_k variance vs single-k accuracy.
  ARM_RETRIEVAL_PRECISION: (1) M scaling against fixed N_DIM=8192 capacity ceiling;
                           (2) recall@1 vs recall@5 (top-1 stricter);
                           (3) sparse-bipolar at f=0.05 has known load-curve drop above M~1500.
  ARM_SEQUENCE_BINDING: (1) HRR position-roles via cf-style binding (here: keyed by index codebook);
                        (2) K=50 may exceed lossless region at N_DIM=8192 sparse-bipolar f=0.05;
                        (3) exact-recovery rate is stricter than median-cosine.
  ARM_SPARSITY_F: (1) capacity definition uses fixed M=500 to compare arms across f;
                  (2) lower f means fewer nonzero -> faster decode but lower signal capacity per item;
                  (3) f=0.005 may break per-item discriminability at N_DIM=8192 below useful threshold.

Mechanism (pure numpy CPU; NO learning, NO plasticity, NO cf-RPE, NO encoder):
  - sparse-bipolar codebook entries f=0.05 (~5% nonzero), values {-1,+1}, N_DIM=8192.
  - HRR bind = circular convolution via FFT (real ifft); unbind = correlation (FFT * conj).
  - Pattern bank = sum of (key * value) bindings (superposition).
  - Recall: unbind bank with key; cosine vs codebook entries; argmax.

Citations: USER master-bias-checklist 2026-06-24 Lane 1; brain-aligned ARM 1-4 (CERT 588);
ANCHOR 1 capacity-respecting M=20 (DIAGNOSTIC_PASS); ANCHOR 2 K10-K20 compositional HARD_PASS;
N0-N4 substrate-native program; operational findings 2026-06-23 sparse-bipolar 20-300x bundle lift;
HRR involutive intuition; Miller 1956 7+/-2.

ASCII only. CPU only (numpy). per-seed checkpoint. Smoke = 1 seed + tiny grid; full = 3 seeds + full grid.
Corpus provenance tag: SYNTHETIC (sparse-bipolar drawn from rng; no external data).
"""
from __future__ import annotations
import sys, os, argparse, time
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_native_capability_suite_shotgun_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 8192
SPARSE_F = 0.05
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    # ARM PC
    ARM_PC_M = 200
    ARM_PC_CORRUPT = 0.50
    # ARM CG
    ARM_CG_N_SUBJ = 20
    ARM_CG_N_OBJ = 20
    ARM_CG_COVERAGE = 0.50  # bind 200 of 400; test heldout 200
    # ARM WM
    ARM_WM_K_GRID = [1, 4, 7, 10, 15, 20, 30]
    ARM_WM_TRIALS_PER_K = 40
    # ARM RP
    ARM_RP_M_GRID = [100, 500, 1000, 2000]
    ARM_RP_TRIALS_PER_M = 1  # all M items probed once each
    # ARM SB
    ARM_SB_K_GRID = [5, 10, 20, 50]
    ARM_SB_TRIALS_PER_K = 20  # repeats per K (different sequences)
    ARM_SB_VOCAB = 60
    # ARM SP
    ARM_SP_F_GRID = [0.005, 0.01, 0.02, 0.05, 0.10]
    ARM_SP_M_FIXED = 500  # capacity at this M across f
    ARM_SP_TRIALS = 1  # all M items probed once each
else:  # smoke
    SEEDS = [0]
    ARM_PC_M = 30
    ARM_PC_CORRUPT = 0.50
    ARM_CG_N_SUBJ = 6
    ARM_CG_N_OBJ = 6
    ARM_CG_COVERAGE = 0.50
    ARM_WM_K_GRID = [1, 4, 7]
    ARM_WM_TRIALS_PER_K = 8
    ARM_RP_M_GRID = [50, 200]
    ARM_RP_TRIALS_PER_M = 1
    ARM_SB_K_GRID = [3, 5]
    ARM_SB_TRIALS_PER_K = 5
    ARM_SB_VOCAB = 15
    ARM_SP_F_GRID = [0.02, 0.05]
    ARM_SP_M_FIXED = 50
    ARM_SP_TRIALS = 1

CONFIG_VERSION = (
    "substrate_native_capability_suite_shotgun_v1; N=%d f=%.3f seeds=%s mode=%s "
    "PC_M=%d PC_corr=%.2f CG=%dx%d cov=%.2f WM_k=%s WM_trials=%d "
    "RP_M=%s SB_K=%s SB_vocab=%d SP_f=%s SP_M=%d"
) % (
    N_DIM, SPARSE_F, SEEDS, RUN_MODE,
    ARM_PC_M, ARM_PC_CORRUPT, ARM_CG_N_SUBJ, ARM_CG_N_OBJ, ARM_CG_COVERAGE,
    ARM_WM_K_GRID, ARM_WM_TRIALS_PER_K,
    ARM_RP_M_GRID, ARM_SB_K_GRID, ARM_SB_VOCAB,
    ARM_SP_F_GRID, ARM_SP_M_FIXED,
)


# ------------------------------------------------------------------
# Substrate primitives (pure numpy; no torch; identical across arms)
# ------------------------------------------------------------------
def _sparse_bipolar(n: int, dim: int, f: float, g: np.random.Generator) -> np.ndarray:
    """Stack of n sparse-bipolar vectors at dim with fraction f nonzero. Shape (n, dim)."""
    out = np.zeros((n, dim), dtype=np.float32)
    k = max(1, int(round(f * dim)))
    for i in range(n):
        idx = g.choice(dim, k, replace=False)
        signs = g.integers(0, 2, k).astype(np.float32) * 2.0 - 1.0
        out[i, idx] = signs
    return out


def _bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    fa = np.fft.fft(a); fb = np.fft.fft(b)
    return np.fft.ifft(fa * fb).real.astype(np.float32)


def _unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    fc = np.fft.fft(c); fb = np.fft.fft(b)
    return np.fft.ifft(fc * fb.conj()).real.astype(np.float32)


def _norm_rows(X: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return (X / n).astype(np.float32)


def _cosine(a: np.ndarray, B: np.ndarray) -> np.ndarray:
    an = a / (np.linalg.norm(a) + 1e-8)
    Bn = _norm_rows(B)
    return Bn @ an


# ------------------------------------------------------------------
# ARM_PATTERN_COMPLETION_AT_CORRUPTION
# Primary metric: top1_recovery_rate
# ------------------------------------------------------------------
def _arm_pc(seed: int, dim: int, M: int, corrupt_frac: float, f: float) -> dict:
    g = np.random.default_rng(seed * 1009 + 1)
    pats = _sparse_bipolar(M, dim, f, g)
    correct = 0
    sims_cleanup = []
    for i in range(M):
        p = pats[i]
        nz = np.nonzero(p)[0]
        nkeep = max(1, int(round((1.0 - corrupt_frac) * len(nz))))
        keep_idx = g.choice(len(nz), nkeep, replace=False)
        cue = np.zeros(dim, dtype=np.float32)
        cue[nz[keep_idx]] = p[nz[keep_idx]]
        cos = _cosine(cue, pats)
        top1 = int(np.argmax(cos))
        if top1 == i:
            correct += 1
        sims_cleanup.append(float(_cosine(pats[top1], p[None, :])[0]))
    return {
        "M": M,
        "corrupt_frac": corrupt_frac,
        "top1_recovery_rate": float(correct / max(M, 1)),     # PRIMARY
        "median_cleanup_cosine": float(np.median(sims_cleanup)),
        "mean_cleanup_cosine": float(np.mean(sims_cleanup)),
    }


# ------------------------------------------------------------------
# ARM_COMPOSITIONAL_GENERALIZATION_HOLDOUT
# Primary metric: heldout_top1
# ------------------------------------------------------------------
def _arm_cg(seed: int, dim: int, n_subj: int, n_obj: int, coverage: float, f: float) -> dict:
    g = np.random.default_rng(seed * 1009 + 2)
    subj = _sparse_bipolar(n_subj, dim, f, g)
    obj = _sparse_bipolar(n_obj, dim, f, g)
    all_pairs = [(i, j) for i in range(n_subj) for j in range(n_obj)]
    g.shuffle(all_pairs)
    n_train = int(round(coverage * len(all_pairs)))
    train_pairs = all_pairs[:n_train]
    held_pairs = all_pairs[n_train:]
    bank = np.zeros(dim, dtype=np.float32)
    for (i, j) in train_pairs:
        bank += _bind(subj[i], obj[j])
    correct = 0
    cosines = []
    for (i, j) in held_pairs:
        rec = _unbind(bank, subj[i])
        cos = _cosine(rec, obj)
        pred = int(np.argmax(cos))
        cosines.append(float(cos[j]))
        if pred == j:
            correct += 1
    holdout_top1 = correct / max(len(held_pairs), 1)
    in_correct = 0
    for (i, j) in train_pairs:
        rec = _unbind(bank, subj[i])
        if int(np.argmax(_cosine(rec, obj))) == j:
            in_correct += 1
    in_top1 = in_correct / max(len(train_pairs), 1)
    return {
        "n_subj": n_subj,
        "n_obj": n_obj,
        "coverage": coverage,
        "n_train": n_train,
        "n_held": len(held_pairs),
        "heldout_top1": float(holdout_top1),      # PRIMARY
        "in_distribution_top1": float(in_top1),
        "chance_top1": 1.0 / n_obj,
        "mean_cosine_correct_held": float(np.mean(cosines)) if cosines else 0.0,
    }


# ------------------------------------------------------------------
# ARM_WORKING_MEMORY_CAPACITY_SCALING
# Primary metric: k_capacity_at_90pct
# ------------------------------------------------------------------
def _arm_wm(seed: int, dim: int, k_grid: list, trials_per_k: int, f: float) -> dict:
    g = np.random.default_rng(seed * 1009 + 3)
    K_MAX = max(k_grid)
    ITEM_POOL = max(40, 2 * K_MAX)
    slot_book = _sparse_bipolar(K_MAX, dim, f, g)
    item_book = _sparse_bipolar(ITEM_POOL, dim, f, g)
    per_k = {}
    for k in k_grid:
        correct = 0
        total = 0
        for _t in range(trials_per_k):
            item_ids = g.choice(ITEM_POOL, k, replace=False)
            bank = np.zeros(dim, dtype=np.float32)
            for s in range(k):
                bank += _bind(slot_book[s], item_book[item_ids[s]])
            for s in range(k):
                rec = _unbind(bank, slot_book[s])
                pred = int(np.argmax(_cosine(rec, item_book)))
                if pred == item_ids[s]:
                    correct += 1
                total += 1
        per_k[k] = float(correct / max(total, 1))
    capacity = 0
    for k in sorted(k_grid):
        if per_k[k] >= 0.90:
            capacity = k
        else:
            break
    return {
        "k_grid": k_grid,
        "per_k_accuracy": per_k,
        "k_capacity_at_90pct": int(capacity),     # PRIMARY
        "trials_per_k": trials_per_k,
        "item_pool_size": ITEM_POOL,
    }


# ------------------------------------------------------------------
# ARM_RETRIEVAL_PRECISION_AT_LOAD
# Primary metric: recall_at_1_at_M_1000  (or nearest M to 1000)
# ------------------------------------------------------------------
def _arm_rp(seed: int, dim: int, M_grid: list, f: float) -> dict:
    g = np.random.default_rng(seed * 1009 + 4)
    M_MAX = max(M_grid)
    # Single codebook of size M_MAX; for each M, probe top-1 over first M entries
    pool = _sparse_bipolar(M_MAX, dim, f, g)
    keys = _sparse_bipolar(M_MAX, dim, f, g)
    per_M = {}
    for M in M_grid:
        # Bank: sum_{i<M} bind(keys[i], pool[i])
        bank = np.zeros(dim, dtype=np.float32)
        for i in range(M):
            bank += _bind(keys[i], pool[i])
        correct = 0
        for i in range(M):
            rec = _unbind(bank, keys[i])
            pred = int(np.argmax(_cosine(rec, pool[:M])))
            if pred == i:
                correct += 1
        per_M[M] = float(correct / max(M, 1))
    # PRIMARY: nearest M to 1000 (in smoke we use max of M_grid as proxy)
    target = 1000
    closest_M = min(M_grid, key=lambda x: abs(x - target))
    return {
        "M_grid": M_grid,
        "per_M_recall_at_1": per_M,
        "recall_at_1_at_M_target": float(per_M[closest_M]),   # PRIMARY (at M=1000 in full)
        "M_target": closest_M,
        "recall_curve_min": float(min(per_M.values())),
        "recall_curve_max": float(max(per_M.values())),
    }


# ------------------------------------------------------------------
# ARM_SEQUENCE_BINDING_LOSSLESS
# Primary metric: exact_recovery_at_K_target (K=20)
# ------------------------------------------------------------------
def _arm_sb(seed: int, dim: int, K_grid: list, trials_per_K: int, vocab: int, f: float) -> dict:
    g = np.random.default_rng(seed * 1009 + 5)
    K_MAX = max(K_grid)
    voc = _sparse_bipolar(vocab, dim, f, g)
    pos_codebook = _sparse_bipolar(K_MAX, dim, f, g)
    per_K = {}
    for K in K_grid:
        correct = 0
        total = 0
        for _t in range(trials_per_K):
            seq = g.integers(0, vocab, K)
            bank = np.zeros(dim, dtype=np.float32)
            for k in range(K):
                bank += _bind(pos_codebook[k], voc[seq[k]])
            for k in range(K):
                rec = _unbind(bank, pos_codebook[k])
                pred = int(np.argmax(_cosine(rec, voc)))
                if pred == int(seq[k]):
                    correct += 1
                total += 1
        per_K[K] = float(correct / max(total, 1))
    # PRIMARY: K=20 (nearest in grid)
    target = 20
    closest_K = min(K_grid, key=lambda x: abs(x - target))
    return {
        "K_grid": K_grid,
        "per_K_exact_recovery": per_K,
        "exact_recovery_at_K_target": float(per_K[closest_K]),  # PRIMARY (at K=20 in full)
        "K_target": closest_K,
        "vocab": vocab,
        "trials_per_K": trials_per_K,
    }


# ------------------------------------------------------------------
# ARM_SPARSITY_F_SWEEP
# Primary metric: capacity_ratio_f002_over_f005 (must >= 1.5 for HARD_PASS)
# ------------------------------------------------------------------
def _arm_sp(seed: int, dim: int, f_grid: list, M_fixed: int) -> dict:
    g = np.random.default_rng(seed * 1009 + 6)
    per_f = {}
    for f in f_grid:
        pool = _sparse_bipolar(M_fixed, dim, f, g)
        keys = _sparse_bipolar(M_fixed, dim, f, g)
        bank = np.zeros(dim, dtype=np.float32)
        for i in range(M_fixed):
            bank += _bind(keys[i], pool[i])
        correct = 0
        for i in range(M_fixed):
            rec = _unbind(bank, keys[i])
            pred = int(np.argmax(_cosine(rec, pool)))
            if pred == i:
                correct += 1
        per_f[f] = float(correct / max(M_fixed, 1))
    # Compute the substrate-mining drill ratio: f=0.02 recall / f=0.05 recall.
    # Use exact keys; if not present, use closest f values in grid.
    target_low = 0.02
    target_high = 0.05
    closest_low = min(per_f.keys(), key=lambda x: abs(x - target_low))
    closest_high = min(per_f.keys(), key=lambda x: abs(x - target_high))
    if closest_low == closest_high:
        ratio = 1.0  # degenerate: smoke may only have one f
    else:
        # use recall as proxy for capacity at fixed M (higher recall == higher capacity at this M)
        ratio = per_f[closest_low] / max(per_f[closest_high], 1e-6)
    return {
        "f_grid": f_grid,
        "M_fixed": M_fixed,
        "per_f_recall_at_1": per_f,
        "capacity_ratio_f002_over_f005": float(ratio),         # PRIMARY (>= 1.5 for HARD_PASS)
        "f_low_used": closest_low,
        "f_high_used": closest_high,
        "recall_at_f_low": per_f[closest_low],
        "recall_at_f_high": per_f[closest_high],
    }


# ------------------------------------------------------------------
# Per-seed driver
# ------------------------------------------------------------------
def run_unit(seed: int) -> dict:
    t0 = time.time()
    print("  [seed=%d] ARM_PATTERN_COMPLETION starting" % seed, flush=True)
    pc = _arm_pc(seed, N_DIM, ARM_PC_M, ARM_PC_CORRUPT, SPARSE_F)
    print("  [seed=%d] ARM_PC top1=%.3f median_cleanup_cos=%.3f" % (
        seed, pc["top1_recovery_rate"], pc["median_cleanup_cosine"]), flush=True)
    print("  [seed=%d] ARM_COMPOSITIONAL_GEN starting" % seed, flush=True)
    cg = _arm_cg(seed, N_DIM, ARM_CG_N_SUBJ, ARM_CG_N_OBJ, ARM_CG_COVERAGE, SPARSE_F)
    print("  [seed=%d] ARM_CG heldout_top1=%.3f in_dist=%.3f chance=%.3f" % (
        seed, cg["heldout_top1"], cg["in_distribution_top1"], cg["chance_top1"]), flush=True)
    print("  [seed=%d] ARM_WORKING_MEMORY starting" % seed, flush=True)
    wm = _arm_wm(seed, N_DIM, ARM_WM_K_GRID, ARM_WM_TRIALS_PER_K, SPARSE_F)
    print("  [seed=%d] ARM_WM capacity_at_90pct=%d per_k=%s" % (
        seed, wm["k_capacity_at_90pct"], wm["per_k_accuracy"]), flush=True)
    print("  [seed=%d] ARM_RETRIEVAL_PRECISION starting" % seed, flush=True)
    rp = _arm_rp(seed, N_DIM, ARM_RP_M_GRID, SPARSE_F)
    print("  [seed=%d] ARM_RP recall@M_target=%.3f (M=%d) per_M=%s" % (
        seed, rp["recall_at_1_at_M_target"], rp["M_target"], rp["per_M_recall_at_1"]), flush=True)
    print("  [seed=%d] ARM_SEQUENCE_BINDING starting" % seed, flush=True)
    sb = _arm_sb(seed, N_DIM, ARM_SB_K_GRID, ARM_SB_TRIALS_PER_K, ARM_SB_VOCAB, SPARSE_F)
    print("  [seed=%d] ARM_SB exact_recovery@K_target=%.3f (K=%d) per_K=%s" % (
        seed, sb["exact_recovery_at_K_target"], sb["K_target"], sb["per_K_exact_recovery"]), flush=True)
    print("  [seed=%d] ARM_SPARSITY_F starting" % seed, flush=True)
    sp = _arm_sp(seed, N_DIM, ARM_SP_F_GRID, ARM_SP_M_FIXED)
    print("  [seed=%d] ARM_SP ratio_f002/f005=%.3f per_f=%s" % (
        seed, sp["capacity_ratio_f002_over_f005"], sp["per_f_recall_at_1"]), flush=True)
    return {
        "seed": seed,
        "arm_pattern_completion": pc,
        "arm_compositional_gen": cg,
        "arm_working_memory": wm,
        "arm_retrieval_precision": rp,
        "arm_sequence_binding": sb,
        "arm_sparsity_f": sp,
        "wall_s": time.time() - t0,
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "config_version": CONFIG_VERSION,
    }


# ------------------------------------------------------------------
# Verdict logic (PRIMARY metric per arm; no OR-gates per master checklist bias #1)
# ------------------------------------------------------------------
def _band(metric: float, hard_pass: float, hard_fail: float, direction: str = "high_good") -> str:
    if direction == "high_good":
        if metric >= hard_pass: return "HARD_PASS"
        if metric < hard_fail: return "HARD_FAIL"
        return "MIDDLE_BAND"
    else:
        if metric <= hard_pass: return "HARD_PASS"
        if metric > hard_fail: return "HARD_FAIL"
        return "MIDDLE_BAND"


def compute_verdict(units: list) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})

    # PRIMARY metrics per arm (averaged across seeds; min for capacity-style integers)
    pc_top1 = [u["arm_pattern_completion"]["top1_recovery_rate"] for u in units]
    cg_top1 = [u["arm_compositional_gen"]["heldout_top1"] for u in units]
    wm_cap = [u["arm_working_memory"]["k_capacity_at_90pct"] for u in units]
    rp_rec = [u["arm_retrieval_precision"]["recall_at_1_at_M_target"] for u in units]
    sb_exact = [u["arm_sequence_binding"]["exact_recovery_at_K_target"] for u in units]
    sp_ratio = [u["arm_sparsity_f"]["capacity_ratio_f002_over_f005"] for u in units]

    pc_mean = float(np.mean(pc_top1)); pc_cv = float(np.std(pc_top1) / max(pc_mean, 1e-6))
    cg_mean = float(np.mean(cg_top1)); cg_cv = float(np.std(cg_top1) / max(cg_mean, 1e-6))
    wm_min = int(min(wm_cap)); wm_mean = float(np.mean(wm_cap))
    rp_mean = float(np.mean(rp_rec)); rp_cv = float(np.std(rp_rec) / max(rp_mean, 1e-6))
    sb_mean = float(np.mean(sb_exact)); sb_cv = float(np.std(sb_exact) / max(sb_mean, 1e-6))
    sp_mean = float(np.mean(sp_ratio)); sp_cv = float(np.std(sp_ratio) / max(sp_mean, 1e-6))

    # PRE-REG bands (sacrosanct):
    v_pc = _band(pc_mean, hard_pass=0.85, hard_fail=0.50, direction="high_good")
    v_cg = _band(cg_mean, hard_pass=0.50, hard_fail=0.20, direction="high_good")
    # WM: integer capacity; use MIN across seeds for conservative
    if wm_min >= 7:
        v_wm = "HARD_PASS"
    elif wm_min < 4:
        v_wm = "HARD_FAIL"
    else:
        v_wm = "MIDDLE_BAND"
    v_rp = _band(rp_mean, hard_pass=0.95, hard_fail=0.70, direction="high_good")
    v_sb = _band(sb_mean, hard_pass=0.99, hard_fail=0.90, direction="high_good")
    # SP: ratio test; HARD_PASS >= 1.5; HARD_FAIL <= 1.0
    if sp_mean >= 1.5:
        v_sp = "HARD_PASS"
    elif sp_mean <= 1.0:
        v_sp = "HARD_FAIL"
    else:
        v_sp = "MIDDLE_BAND"

    arm_verdicts = [v_pc, v_cg, v_wm, v_rp, v_sb, v_sp]
    arm_names = [
        "ARM_PATTERN_COMPLETION", "ARM_COMPOSITIONAL_GEN", "ARM_WORKING_MEMORY",
        "ARM_RETRIEVAL_PRECISION", "ARM_SEQUENCE_BINDING", "ARM_SPARSITY_F",
    ]
    n_pass = sum(1 for v in arm_verdicts if v == "HARD_PASS")

    if n_pass == 6:
        cell_verdict = "ARM_SUITE_NATIVE_ALIVE"
        cell_msg = (
            "ARM_SUITE_NATIVE_ALIVE: all 6 arms HARD_PASS. PC top1=%.3f / CG heldout=%.3f "
            "(chance %.3f) / WM cap_min=%d (Miller>=7) / RP recall@M=%d=%.3f / SB exact@K=%d=%.3f / "
            "SP ratio f002/f005=%.2f. Substrate-native capability uniformly chain-grade on apples-to-"
            "apples synthetic. Lane 1 substrate-native suite is alive."
        ) % (
            pc_mean, cg_mean, units[0]["arm_compositional_gen"]["chance_top1"], wm_min,
            units[0]["arm_retrieval_precision"]["M_target"], rp_mean,
            units[0]["arm_sequence_binding"]["K_target"], sb_mean, sp_mean,
        )
    elif n_pass >= 4:
        gap_list = [n for n, v in zip(arm_names, arm_verdicts) if v != "HARD_PASS"]
        cell_verdict = "ARM_SUITE_NATIVE_PARTIAL"
        cell_msg = (
            "ARM_SUITE_NATIVE_PARTIAL: %d of 6 arms HARD_PASS. Gaps: %s. "
            "PC=%s(%.3f) CG=%s(%.3f) WM=%s(min=%d) RP=%s(%.3f) SB=%s(%.3f) SP=%s(%.2f). "
            "Substrate has strong native suite with %d gap(s) to fix."
        ) % (
            n_pass, ",".join(gap_list),
            v_pc, pc_mean, v_cg, cg_mean, v_wm, wm_min, v_rp, rp_mean, v_sb, sb_mean, v_sp, sp_mean,
            len(gap_list),
        )
    else:
        cell_verdict = "ARM_SUITE_NATIVE_DEAD"
        cell_msg = (
            "ARM_SUITE_NATIVE_DEAD: only %d of 6 arms HARD_PASS. "
            "PC=%s(%.3f) CG=%s(%.3f) WM=%s(min=%d) RP=%s(%.3f) SB=%s(%.3f) SP=%s(%.2f). "
            "Substrate-native suite has fundamental gaps; suite-product story needs work."
        ) % (
            n_pass,
            v_pc, pc_mean, v_cg, cg_mean, v_wm, wm_min, v_rp, rp_mean, v_sb, sb_mean, v_sp, sp_mean,
        )

    detail = {
        "n_seeds": len(units),
        "lane": "Lane 1 substrate-native capability (apples-to-apples; synthetic)",
        "corpus_provenance": "synthetic",
        "intra_lane_delta": "all arms share substrate primitives (HRR + sparse-bipolar); only TASK varies",
        "arms": {
            "ARM_PATTERN_COMPLETION": {
                "primary_metric": "top1_recovery_rate",
                "mean": pc_mean, "cv": pc_cv, "verdict": v_pc,
                "band": "HARD_PASS>=0.85, HARD_FAIL<0.50",
            },
            "ARM_COMPOSITIONAL_GEN": {
                "primary_metric": "heldout_top1",
                "mean": cg_mean, "cv": cg_cv, "verdict": v_cg,
                "in_distribution_top1_mean": float(np.mean([u["arm_compositional_gen"]["in_distribution_top1"] for u in units])),
                "chance": units[0]["arm_compositional_gen"]["chance_top1"],
                "band": "HARD_PASS>=0.50, HARD_FAIL<0.20",
            },
            "ARM_WORKING_MEMORY": {
                "primary_metric": "k_capacity_at_90pct",
                "mean_capacity": wm_mean, "min_capacity": wm_min,
                "per_seed_capacities": wm_cap, "verdict": v_wm,
                "band": "HARD_PASS>=7 (Miller 7+/-2), HARD_FAIL<4",
            },
            "ARM_RETRIEVAL_PRECISION": {
                "primary_metric": "recall_at_1_at_M_target",
                "M_target": units[0]["arm_retrieval_precision"]["M_target"],
                "mean": rp_mean, "cv": rp_cv, "verdict": v_rp,
                "band": "HARD_PASS>=0.95, HARD_FAIL<0.70",
            },
            "ARM_SEQUENCE_BINDING": {
                "primary_metric": "exact_recovery_at_K_target",
                "K_target": units[0]["arm_sequence_binding"]["K_target"],
                "mean": sb_mean, "cv": sb_cv, "verdict": v_sb,
                "band": "HARD_PASS>=0.99 (lossless), HARD_FAIL<0.90",
            },
            "ARM_SPARSITY_F": {
                "primary_metric": "capacity_ratio_f002_over_f005",
                "mean": sp_mean, "cv": sp_cv, "verdict": v_sp,
                "band": "HARD_PASS>=1.5, HARD_FAIL<=1.0",
            },
        },
        "n_arms_hard_pass": n_pass,
        "CONFIG_VERSION": CONFIG_VERSION,
        "what_this_does_not_show": (
            "Pure substrate-native capability characterization on synthetic data. Does NOT show: "
            "(1) any language-task performance; (2) learning / plasticity (no cf-RPE, no gradients); "
            "(3) corpus-bound generalization (no Pythia / no word2vec / no text); "
            "(4) interaction effects with downstream substrate-as-LM components. "
            "An ARM_SUITE_NATIVE_ALIVE verdict is a substrate-primitive-suite characterization, "
            "not a cert of any downstream task. PRIMARY metric per arm declared pre-reg; no OR-gates."
        ),
        "honest_scope": (
            "Pure substrate primitives (HRR bind/unbind + sparse-bipolar codebook); NO learning; "
            "synthetic data only; CPU numpy; apples-to-apples Lane 1. "
            "Per USER master-bias-checklist 2026-06-24 Lane 1."
        ),
        "cites": [
            "USER_master_bias_checklist_lane1_substrate_native_2026-06-24",
            "anchor1_capacity_respecting_M20_diagnostic_pass",
            "anchor2_compositional_K10_K20_hard_pass",
            "brain_aligned_shotgun_v1_pattern_completion_wm_bidirectional",
            "operational_findings_2026-06-23_sparse_bipolar_20_300x_bundle_lift",
            "Miller_1956_seven_plus_minus_two_working_memory",
        ],
    }
    return (cell_verdict, cell_msg, detail)


# ------------------------------------------------------------------
# Selftest -- mechanism unit-tests at tiny dim
# ------------------------------------------------------------------
def _selftest() -> None:
    g = np.random.default_rng(0)
    dim = 256; f = 0.05
    X = _sparse_bipolar(5, dim, f, g)
    assert X.shape == (5, dim)
    avg_nz = float(np.mean(np.count_nonzero(X, axis=1)))
    expect = f * dim
    assert abs(avg_nz - expect) <= max(1.0, 0.2 * expect), (
        "sparse-bipolar nz=%.1f vs expected %.1f" % (avg_nz, expect)
    )
    # HRR involutive sanity
    a = g.standard_normal(dim).astype(np.float32)
    b = _sparse_bipolar(1, dim, f, g)[0]
    a_back = _unbind(_bind(a, b), b)
    cos_ab = float(_cosine(a_back, a[None, :])[0])
    assert cos_ab > 0.3, "HRR round-trip cosine too low (%.3f)" % cos_ab

    # ARM PC tiny: cleanup at small M near-perfect
    pc = _arm_pc(seed=0, dim=512, M=10, corrupt_frac=0.50, f=0.05)
    assert pc["top1_recovery_rate"] > 0.85, (
        "ARM_PC tiny top1 too low (%.3f)" % pc["top1_recovery_rate"]
    )
    print("[selftest] ARM_PC tiny top1=%.3f median_cleanup_cos=%.3f" % (
        pc["top1_recovery_rate"], pc["median_cleanup_cosine"]), flush=True)

    # ARM WM tiny: k=2 high accuracy at modest dim
    wm = _arm_wm(seed=0, dim=2048, k_grid=[1, 2], trials_per_k=8, f=0.05)
    assert wm["per_k_accuracy"][2] > 0.85, (
        "ARM_WM tiny k=2 accuracy too low (%.3f)" % wm["per_k_accuracy"][2]
    )
    print("[selftest] ARM_WM tiny k=2 acc=%.3f" % wm["per_k_accuracy"][2], flush=True)

    # ARM CG tiny: in-distribution top1 high (crosstalk well below signal at small M)
    cg = _arm_cg(seed=0, dim=4096, n_subj=4, n_obj=4, coverage=0.4, f=0.05)
    assert cg["in_distribution_top1"] > 0.50, (
        "ARM_CG tiny in-dist top-1 too low (%.3f)" % cg["in_distribution_top1"]
    )
    print("[selftest] ARM_CG tiny in_dist_top1=%.3f heldout=%.3f" % (
        cg["in_distribution_top1"], cg["heldout_top1"]), flush=True)

    # ARM RP tiny: small-M recall near-perfect
    rp = _arm_rp(seed=0, dim=2048, M_grid=[10, 30], f=0.05)
    # at M=10 we expect near-perfect; at M=30 still high
    assert rp["per_M_recall_at_1"][10] > 0.85, (
        "ARM_RP tiny M=10 recall too low (%.3f)" % rp["per_M_recall_at_1"][10]
    )
    print("[selftest] ARM_RP tiny M=10 recall=%.3f M=30 recall=%.3f" % (
        rp["per_M_recall_at_1"][10], rp["per_M_recall_at_1"][30]), flush=True)

    # ARM SB tiny: short K near-lossless
    sb = _arm_sb(seed=0, dim=2048, K_grid=[3, 5], trials_per_K=5, vocab=10, f=0.05)
    assert sb["per_K_exact_recovery"][3] > 0.85, (
        "ARM_SB tiny K=3 exact-recovery too low (%.3f)" % sb["per_K_exact_recovery"][3]
    )
    print("[selftest] ARM_SB tiny K=3 exact=%.3f K=5 exact=%.3f" % (
        sb["per_K_exact_recovery"][3], sb["per_K_exact_recovery"][5]), flush=True)

    # ARM SP tiny: two f values produce valid recall numbers and a finite ratio
    sp = _arm_sp(seed=0, dim=2048, f_grid=[0.02, 0.05], M_fixed=20)
    assert sp["capacity_ratio_f002_over_f005"] > 0.0
    assert sp["recall_at_f_low"] >= 0.0 and sp["recall_at_f_high"] >= 0.0
    print("[selftest] ARM_SP tiny ratio=%.3f recall@f=0.02=%.3f @f=0.05=%.3f" % (
        sp["capacity_ratio_f002_over_f005"], sp["recall_at_f_low"], sp["recall_at_f_high"]),
        flush=True)

    print("[selftest] PASS: HRR involutive + 6 arms mechanism operational", flush=True)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print(
        "[config] %s mode=%s N=%d f=%.3f seeds=%s | %s" % (
            ANCHOR_NAME, RUN_MODE, N_DIM, SPARSE_F, SEEDS, CONFIG_VERSION
        ),
        flush=True,
    )
    out_dir = get_output_dir(ANCHOR_NAME)
    run_cfg = {
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "schema": "substrate-native-capability-suite-shotgun-v1",
    }
    t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        already = aggregate_partials(out_dir, [key], run_config=run_cfg)
        if key in already:
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        result = run_unit(seed)
        write_partial_key(out_dir, key, result)
    units = list(aggregate_partials(
        out_dir, ["s%d" % s for s in SEEDS], run_config=run_cfg
    ).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "SPARSE_F": SPARSE_F,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_substrate_native_capability_suite_shotgun",
        "lane": "Lane 1 substrate-native capability",
        "corpus_provenance": "synthetic",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "N/A (mechanism-suite cell, not LM cell)",
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
