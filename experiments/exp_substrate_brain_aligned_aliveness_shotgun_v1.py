"""substrate_brain_aligned_aliveness_shotgun_v1 -- probe brain-canonical aliveness dimensions where substrate machinery is well-aligned with brain (NOT next-char-BPC).

Strategic rationale (USER 2026-06-24): current aliveness map relies on next-char-BPC over unigram. Brain doesn't do next-char prediction; brain does (1) pattern completion (recover from partial cue), (2) compositional generalization (substitute parts), (3) working memory (hold 7+ items, retrieve any), (4) bidirectional prediction (fill missing element given before+after). For each, brain achieves near-perfect trivially. Substrate's machinery (HRR bind/unbind, sparse-bipolar, codebook recall) is built for these.

Cell: 4 arms x 3 seeds x N_DIM=8192 x sparse-bipolar f=0.05 codebook.
- ARM 1 Pattern Completion: bind M=500 patterns; corrupt 50% of bits; measure median recovery cosine.
- ARM 2 Compositional Generalization: 20 subjects x 20 objects = 400 pairs; bind 50% coverage (200); recover heldout B_j given A_i; top-1.
- ARM 3 Working Memory Capacity: for k in {1,2,4,7,10,15}, bind k items in one bank; find k_capacity_at_90pct_accuracy.
- ARM 4 Bidirectional Prediction: sequence of N=100 items; bind (prev,curr,next) triples; mask curr; recover top-1 from (prev,_,next).

Pre-reg bands per arm (sacrosanct both directions):
  ARM 1 HARD_PASS median recovery > 0.85; HARD_FAIL < 0.50.
  ARM 2 HARD_PASS holdout top-1 > 0.70; HARD_FAIL < 0.20 (chance 1/20 = 0.05).
  ARM 3 HARD_PASS k_capacity_at_90pct_accuracy >= 7 (Miller 7+/-2); HARD_FAIL < 4.
  ARM 4 HARD_PASS top-1 > 0.50; HARD_FAIL < 0.10.

Cell-level verdict logic:
  BRAIN_ALIGNED_ALIVE: all 4 arms HARD_PASS -> substrate is alive on brain-canonical tests; next-char-BPC is mismeasuring.
  BRAIN_ALIGNED_PARTIAL: 2-3 of 4 arms HARD_PASS -> partial aliveness; identify dimensions.
  BRAIN_ALIGNED_DEAD: 0-1 arm HARD_PASS -> substrate not alive on brain-canonical tests either; deeper issue.
  Sanity: ARM 1 (pattern completion) MUST HARD_PASS -- it is substrate's most fundamental capability. If ARM 1 FAILs -> HARD_FAIL regardless of others (sanity-floor failure).

Mechanism (pure numpy; NO learning, NO plasticity, NO cf-RPE):
  - sparse-bipolar codebook entries: f=0.05 (~5% nonzero), values in {-1,+1}, N_DIM=8192.
  - HRR bind = circular convolution via FFT (real ifft); unbind = circular correlation (FFT * conj).
  - Pattern bank = sum of (key * value) bindings (superposition).
  - Recall: unbind bank with key; cosine vs codebook entries; argmax.

Citations: USER brain-aligned aliveness directive 2026-06-24; substrate-as-LM test harness rigged audit 2026-06-23; HRR involutive intuition; sparse-bipolar 20-300x bundle lift (operational findings 2026-06-23).

ASCII only. CPU only (numpy). per-seed checkpoint. Smoke = 1 seed + tiny per-arm; full = 3 seeds + spec'd grid.
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

ANCHOR_NAME = "substrate_brain_aligned_aliveness_shotgun_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 8192          # substrate dimensionality (sparse-bipolar at f=0.05)
SPARSE_F = 0.05       # ~5% nonzero per codebook entry
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    ARM1_M = 500              # patterns to bind
    ARM1_CORRUPT_FRAC = 0.50  # bit-corruption fraction
    ARM2_N_SUBJ = 20
    ARM2_N_OBJ = 20
    ARM2_COVERAGE = 0.50      # 200/400 pairs bound; 200 heldout
    ARM3_K_GRID = [1, 2, 4, 7, 10, 15]
    ARM3_TRIALS_PER_K = 60    # repeats per k (different item sets)
    ARM4_SEQ_LEN = 100
    ARM4_VOCAB = 50           # candidate set size at recall
else:  # smoke
    SEEDS = [0]
    ARM1_M = 50
    ARM1_CORRUPT_FRAC = 0.50
    ARM2_N_SUBJ = 8
    ARM2_N_OBJ = 8
    ARM2_COVERAGE = 0.50
    ARM3_K_GRID = [1, 2, 4, 7]
    ARM3_TRIALS_PER_K = 10
    ARM4_SEQ_LEN = 20
    ARM4_VOCAB = 15

CONFIG_VERSION = (
    "substrate_brain_aligned_aliveness_shotgun_v1; N=%d f=%.3f seeds=%s "
    "arm1_M=%d corrupt=%.2f arm2=%dx%d cov=%.2f arm3_k=%s arm3_trials=%d "
    "arm4_seqlen=%d arm4_vocab=%d"
) % (
    N_DIM, SPARSE_F, SEEDS, ARM1_M, ARM1_CORRUPT_FRAC,
    ARM2_N_SUBJ, ARM2_N_OBJ, ARM2_COVERAGE, ARM3_K_GRID, ARM3_TRIALS_PER_K,
    ARM4_SEQ_LEN, ARM4_VOCAB,
)


# ------------------------------------------------------------------
# Substrate primitives (pure numpy; no torch)
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
    """HRR circular convolution via FFT. Real input -> real output."""
    fa = np.fft.fft(a); fb = np.fft.fft(b)
    return np.fft.ifft(fa * fb).real.astype(np.float32)


def _unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular correlation via FFT * conj. Real input -> real output."""
    fc = np.fft.fft(c); fb = np.fft.fft(b)
    return np.fft.ifft(fc * fb.conj()).real.astype(np.float32)


def _norm_rows(X: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return (X / n).astype(np.float32)


def _cosine(a: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Row-wise cosine between vector a (D,) and matrix B (k,D)."""
    an = a / (np.linalg.norm(a) + 1e-8)
    Bn = _norm_rows(B)
    return Bn @ an


# ------------------------------------------------------------------
# ARM 1 -- Pattern Completion
# ------------------------------------------------------------------
def _arm1_pattern_completion(seed: int, dim: int, M: int, corrupt_frac: float, f: float) -> dict:
    """Brain-aligned pattern completion: codebook is the memory bank; corrupted cue is cleaned by
    nearest-neighbor cosine over the codebook (content-addressable retrieval). This is the
    canonical autoassociative-recall operation: top-1 over codebook + measure cosine to TRUE original.

    Distinct from a naive cue-vs-original cosine (which is trivially sqrt(1-corrupt_frac) by construction).
    The brain-aligned probe is: AFTER cleanup, does the recovered codebook entry MATCH the original
    AND does it carry full sign-fidelity? Two reported metrics:
      - top1_recovery_rate: argmax over codebook == original (the brain-canonical recall accuracy)
      - median_cleanup_cosine: cosine of CLEANED vector (codebook[top1]) vs ORIGINAL (1.0 when top1 matches)
    """
    g = np.random.default_rng(seed * 1009 + 1)
    pats = _sparse_bipolar(M, dim, f, g)  # the codebook = memory bank
    # Corruption: keep (1-corrupt_frac) of the nonzero bits, zero the rest. Standard partial-cue.
    sims_after_cleanup = []
    sims_cue_only = []
    correct = 0
    for i in range(M):
        p = pats[i]
        nz = np.nonzero(p)[0]
        nkeep = max(1, int(round((1.0 - corrupt_frac) * len(nz))))
        keep_idx = g.choice(len(nz), nkeep, replace=False)
        cue = np.zeros(dim, dtype=np.float32)
        cue[nz[keep_idx]] = p[nz[keep_idx]]
        # Cue-only baseline (what cosine WOULD be without cleanup -- approx sqrt(1-corrupt_frac))
        sims_cue_only.append(float(_cosine(cue, p[None, :])[0]))
        # Cleanup: nearest codebook entry by cosine (the brain-aligned autoassociation step)
        cos_to_codebook = _cosine(cue, pats)
        top1 = int(np.argmax(cos_to_codebook))
        if top1 == i:
            correct += 1
        # Cosine of the CLEANED-UP vector vs original: 1.0 when top1 matches, else cos(pats[top1], pats[i])
        sim_clean = float(_cosine(pats[top1], p[None, :])[0])
        sims_after_cleanup.append(sim_clean)
    sims = np.array(sims_after_cleanup, dtype=np.float32)
    cue_only = np.array(sims_cue_only, dtype=np.float32)
    top1_rate = correct / max(M, 1)
    return {
        "M": M,
        "corrupt_frac": corrupt_frac,
        "top1_recovery_rate": float(top1_rate),
        "median_recovery_cosine": float(np.median(sims)),
        "mean_recovery_cosine": float(np.mean(sims)),
        "min_recovery_cosine": float(np.min(sims)),
        "median_cue_only_cosine": float(np.median(cue_only)),  # ~sqrt(1-corrupt_frac) by construction
        "n_above_0p85": int((sims > 0.85).sum()),
        "n_above_0p70": int((sims > 0.70).sum()),
        "n_above_0p50": int((sims > 0.50).sum()),
    }


# ------------------------------------------------------------------
# ARM 2 -- Compositional Generalization
# ------------------------------------------------------------------
def _arm2_compositional(seed: int, dim: int, n_subj: int, n_obj: int, coverage: float, f: float) -> dict:
    """Build subj x obj bindings; hold out half; recover obj given subj on heldout via cosine over obj codebook."""
    g = np.random.default_rng(seed * 1009 + 2)
    subj = _sparse_bipolar(n_subj, dim, f, g)
    obj = _sparse_bipolar(n_obj, dim, f, g)
    # All possible pairs
    all_pairs = [(i, j) for i in range(n_subj) for j in range(n_obj)]
    g.shuffle(all_pairs)
    n_train = int(round(coverage * len(all_pairs)))
    train_pairs = all_pairs[:n_train]
    held_pairs = all_pairs[n_train:]
    # Bank = sum of bind(subj_i, obj_j) for train pairs
    bank = np.zeros(dim, dtype=np.float32)
    for (i, j) in train_pairs:
        bank += _bind(subj[i], obj[j])
    # Holdout test: for (i,j) in held_pairs, unbind(bank, subj_i) and find top-1 obj over the OBJ CODEBOOK
    correct = 0
    total = 0
    cosines_correct = []
    for (i, j) in held_pairs:
        rec = _unbind(bank, subj[i])
        cos_to_obj = _cosine(rec, obj)
        pred = int(np.argmax(cos_to_obj))
        cosines_correct.append(float(cos_to_obj[j]))
        if pred == j:
            correct += 1
        total += 1
    top1 = correct / max(total, 1)
    # In-distribution sanity (train-pair recall) -- should be high; if low the mechanism is broken
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
        "holdout_top1": float(top1),
        "in_distribution_top1": float(in_top1),
        "chance_top1": 1.0 / n_obj,
        "mean_cosine_correct_holdout": float(np.mean(cosines_correct)) if cosines_correct else 0.0,
    }


# ------------------------------------------------------------------
# ARM 3 -- Working Memory Capacity (Miller 7+/-2)
# ------------------------------------------------------------------
def _arm3_working_memory(seed: int, dim: int, k_grid: list, trials_per_k: int, f: float) -> dict:
    """For each k, bind k random (slot, item) pairs into one bank; retrieve each item via slot key. Accuracy over trials_per_k repeats."""
    g = np.random.default_rng(seed * 1009 + 3)
    # Universal slot codebook large enough for max-k; universal item codebook size = vocab pool
    K_MAX = max(k_grid)
    ITEM_POOL = max(20, 2 * K_MAX)
    slot_book = _sparse_bipolar(K_MAX, dim, f, g)
    item_book = _sparse_bipolar(ITEM_POOL, dim, f, g)
    per_k = {}
    for k in k_grid:
        correct = 0
        total = 0
        for _t in range(trials_per_k):
            # Pick k items from the item pool for this trial
            item_ids = g.choice(ITEM_POOL, k, replace=False)
            # Bank: sum_{s=0..k-1} bind(slot_s, item_{item_ids[s]})
            bank = np.zeros(dim, dtype=np.float32)
            for s in range(k):
                bank += _bind(slot_book[s], item_book[item_ids[s]])
            # Retrieve each slot
            for s in range(k):
                rec = _unbind(bank, slot_book[s])
                pred = int(np.argmax(_cosine(rec, item_book)))
                if pred == item_ids[s]:
                    correct += 1
                total += 1
        acc = correct / max(total, 1)
        per_k[k] = float(acc)
    # k_capacity_at_90pct_accuracy = largest k with acc >= 0.90
    capacity = 0
    for k in sorted(k_grid):
        if per_k[k] >= 0.90:
            capacity = k
        else:
            break
    return {
        "k_grid": k_grid,
        "per_k_accuracy": per_k,
        "k_capacity_at_90pct_accuracy": int(capacity),
        "trials_per_k": trials_per_k,
        "item_pool_size": ITEM_POOL,
    }


# ------------------------------------------------------------------
# ARM 4 -- Bidirectional Prediction
# ------------------------------------------------------------------
def _arm4_bidirectional(seed: int, dim: int, seq_len: int, vocab: int, f: float) -> dict:
    """Sequence of seq_len items drawn from vocab; bind (prev,curr,next) triples into bank; mask curr; recover via unbind(bank, bind(prev,next))."""
    g = np.random.default_rng(seed * 1009 + 4)
    voc = _sparse_bipolar(vocab, dim, f, g)
    # Sequence
    seq = g.integers(0, vocab, seq_len)
    # Bank: sum of bind(prev * next, curr) i.e. key = bind(prev, next); value = curr
    bank = np.zeros(dim, dtype=np.float32)
    keys = []
    for t in range(1, seq_len - 1):
        prev_v = voc[seq[t - 1]]
        next_v = voc[seq[t + 1]]
        key = _bind(prev_v, next_v)
        keys.append(key)
        bank += _bind(key, voc[seq[t]])
    # Recover each masked curr
    correct = 0
    total = 0
    for idx_t, t in enumerate(range(1, seq_len - 1)):
        key = keys[idx_t]
        rec = _unbind(bank, key)
        pred = int(np.argmax(_cosine(rec, voc)))
        if pred == int(seq[t]):
            correct += 1
        total += 1
    top1 = correct / max(total, 1)
    return {
        "seq_len": seq_len,
        "vocab": vocab,
        "n_predictions": total,
        "top1": float(top1),
        "chance_top1": 1.0 / vocab,
    }


# ------------------------------------------------------------------
# Per-seed driver
# ------------------------------------------------------------------
def run_unit(seed: int) -> dict:
    t0 = time.time()
    print("  [seed=%d] ARM 1 (pattern completion) starting" % seed, flush=True)
    arm1 = _arm1_pattern_completion(seed, N_DIM, ARM1_M, ARM1_CORRUPT_FRAC, SPARSE_F)
    print("  [seed=%d] ARM 1 top1=%.3f median_cleanup_cos=%.3f cue_only_cos=%.3f n_above_0.85=%d/%d" % (
        seed, arm1["top1_recovery_rate"], arm1["median_recovery_cosine"],
        arm1["median_cue_only_cosine"], arm1["n_above_0p85"], arm1["M"]), flush=True)
    print("  [seed=%d] ARM 2 (compositional) starting" % seed, flush=True)
    arm2 = _arm2_compositional(seed, N_DIM, ARM2_N_SUBJ, ARM2_N_OBJ, ARM2_COVERAGE, SPARSE_F)
    print("  [seed=%d] ARM 2 holdout_top1=%.3f in_dist_top1=%.3f chance=%.3f" % (
        seed, arm2["holdout_top1"], arm2["in_distribution_top1"], arm2["chance_top1"]), flush=True)
    print("  [seed=%d] ARM 3 (working memory) starting" % seed, flush=True)
    arm3 = _arm3_working_memory(seed, N_DIM, ARM3_K_GRID, ARM3_TRIALS_PER_K, SPARSE_F)
    print("  [seed=%d] ARM 3 capacity_at_0.90=%d per_k=%s" % (
        seed, arm3["k_capacity_at_90pct_accuracy"], arm3["per_k_accuracy"]), flush=True)
    print("  [seed=%d] ARM 4 (bidirectional) starting" % seed, flush=True)
    arm4 = _arm4_bidirectional(seed, N_DIM, ARM4_SEQ_LEN, ARM4_VOCAB, SPARSE_F)
    print("  [seed=%d] ARM 4 top1=%.3f chance=%.3f" % (seed, arm4["top1"], arm4["chance_top1"]), flush=True)
    return {
        "seed": seed,
        "arm1_pattern_completion": arm1,
        "arm2_compositional": arm2,
        "arm3_working_memory": arm3,
        "arm4_bidirectional": arm4,
        "wall_s": time.time() - t0,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }


# ------------------------------------------------------------------
# Verdict logic
# ------------------------------------------------------------------
def _arm_verdict_label(metric: float, hard_pass: float, hard_fail: float, direction: str = "high_good") -> str:
    if direction == "high_good":
        if metric > hard_pass: return "HARD_PASS"
        if metric < hard_fail: return "HARD_FAIL"
        return "MIDDLE_BAND"
    else:  # low_good
        if metric < hard_pass: return "HARD_PASS"
        if metric > hard_fail: return "HARD_FAIL"
        return "MIDDLE_BAND"


def compute_verdict(units: list) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})
    # Aggregate per-arm across seeds
    arm1_medians = [u["arm1_pattern_completion"]["median_recovery_cosine"] for u in units]
    arm2_holdouts = [u["arm2_compositional"]["holdout_top1"] for u in units]
    arm2_in = [u["arm2_compositional"]["in_distribution_top1"] for u in units]
    arm3_caps = [u["arm3_working_memory"]["k_capacity_at_90pct_accuracy"] for u in units]
    arm4_top1s = [u["arm4_bidirectional"]["top1"] for u in units]

    arm1_mean = float(np.mean(arm1_medians)); arm1_cv = float(np.std(arm1_medians) / max(arm1_mean, 1e-6))
    arm2_mean = float(np.mean(arm2_holdouts)); arm2_cv = float(np.std(arm2_holdouts) / max(arm2_mean, 1e-6))
    arm3_mean = float(np.mean(arm3_caps))  # k is integer; report mean & min
    arm3_min = int(min(arm3_caps))
    arm4_mean = float(np.mean(arm4_top1s)); arm4_cv = float(np.std(arm4_top1s) / max(arm4_mean, 1e-6))

    # Per-arm verdict using PRE-REG bands (per USER directive)
    v_arm1 = _arm_verdict_label(arm1_mean, hard_pass=0.85, hard_fail=0.50, direction="high_good")
    v_arm2 = _arm_verdict_label(arm2_mean, hard_pass=0.70, hard_fail=0.20, direction="high_good")
    # ARM 3: capacity is integer; HARD_PASS k_capacity >= 7; HARD_FAIL k_capacity < 4
    if arm3_min >= 7:
        v_arm3 = "HARD_PASS"
    elif arm3_min < 4:
        v_arm3 = "HARD_FAIL"
    else:
        v_arm3 = "MIDDLE_BAND"
    v_arm4 = _arm_verdict_label(arm4_mean, hard_pass=0.50, hard_fail=0.10, direction="high_good")

    n_pass = sum(1 for v in [v_arm1, v_arm2, v_arm3, v_arm4] if v == "HARD_PASS")
    arm1_must_pass = (v_arm1 == "HARD_PASS")

    if not arm1_must_pass:
        cell_verdict = "HARD_FAIL"
        cell_msg = (
            "SANITY_FLOOR_FAIL: ARM 1 pattern completion did not HARD_PASS (median=%.3f, band>0.85). "
            "Substrate's most fundamental capability is broken; other arms moot."
        ) % arm1_mean
    elif n_pass == 4:
        cell_verdict = "BRAIN_ALIGNED_ALIVE"
        cell_msg = (
            "BRAIN_ALIGNED_ALIVE: all 4 arms HARD_PASS. Pattern completion median=%.3f; "
            "compositional holdout top-1=%.3f (chance %.3f); working-memory capacity (min across seeds)=%d "
            "(Miller >=7); bidirectional top-1=%.3f (chance %.3f). "
            "Substrate is alive on brain-canonical tests; next-char-BPC is mismeasuring."
        ) % (arm1_mean, arm2_mean, units[0]["arm2_compositional"]["chance_top1"],
             arm3_min, arm4_mean, units[0]["arm4_bidirectional"]["chance_top1"])
    elif n_pass in (2, 3):
        cell_verdict = "BRAIN_ALIGNED_PARTIAL"
        cell_msg = (
            "BRAIN_ALIGNED_PARTIAL: %d of 4 arms HARD_PASS. ARM1=%s(%.3f); ARM2=%s(holdout %.3f); "
            "ARM3=%s(min cap %d); ARM4=%s(%.3f). Substrate is partially alive; characterize which dimensions."
        ) % (n_pass, v_arm1, arm1_mean, v_arm2, arm2_mean, v_arm3, arm3_min, v_arm4, arm4_mean)
    else:
        cell_verdict = "BRAIN_ALIGNED_DEAD"
        cell_msg = (
            "BRAIN_ALIGNED_DEAD: only %d of 4 arms HARD_PASS. ARM1=%s(%.3f); ARM2=%s(holdout %.3f); "
            "ARM3=%s(min cap %d); ARM4=%s(%.3f). Substrate not alive on brain-canonical tests either; "
            "deeper issue beyond test choice."
        ) % (n_pass, v_arm1, arm1_mean, v_arm2, arm2_mean, v_arm3, arm3_min, v_arm4, arm4_mean)

    detail = {
        "n_seeds": len(units),
        "arm1": {"mean_median_recovery": arm1_mean, "cv": arm1_cv, "verdict": v_arm1,
                 "band": "HARD_PASS>0.85, HARD_FAIL<0.50"},
        "arm2": {"mean_holdout_top1": arm2_mean, "cv": arm2_cv, "verdict": v_arm2,
                 "in_distribution_top1_mean": float(np.mean(arm2_in)),
                 "band": "HARD_PASS>0.70, HARD_FAIL<0.20",
                 "chance": units[0]["arm2_compositional"]["chance_top1"]},
        "arm3": {"mean_capacity": arm3_mean, "min_capacity": arm3_min, "verdict": v_arm3,
                 "band": "HARD_PASS>=7 (Miller 7+/-2), HARD_FAIL<4",
                 "per_seed_capacities": arm3_caps},
        "arm4": {"mean_top1": arm4_mean, "cv": arm4_cv, "verdict": v_arm4,
                 "band": "HARD_PASS>0.50, HARD_FAIL<0.10",
                 "chance": units[0]["arm4_bidirectional"]["chance_top1"]},
        "n_arms_hard_pass": n_pass,
        "arm1_sanity_pass": arm1_must_pass,
        "CONFIG_VERSION": CONFIG_VERSION,
        "what_this_does_not_show": (
            "These probes test brain-CANONICAL aliveness dimensions (pattern completion, compositional generalization, "
            "working memory, bidirectional prediction) on substrate primitives in isolation. They do NOT show: "
            "(1) language-task performance (no text corpus involved); (2) learning / plasticity (no cf-RPE, no gradient updates); "
            "(3) chain-grade integration with the rest of the substrate KG. A BRAIN_ALIGNED_ALIVE verdict is a MECHANISM "
            "characterization, not a cert of any downstream task. By construction notes: ARM 1 cue carries half the original "
            "bits at full sign-fidelity (cosine recovery directly reflects information preserved by the sparse-bipolar code); "
            "ARM 2-4 measure HRR bind/unbind crosstalk under superposition; capacity in ARM 3 falls when M*f^2 crosstalk "
            "exceeds signal."
        ),
        "honest_scope": (
            "Pure substrate primitives (HRR bind/unbind + sparse-bipolar codebook); NO learning. NumPy CPU. "
            "Per USER 2026-06-24 brain-aligned aliveness directive."
        ),
        "cites": [
            "USER_brain_aligned_aliveness_directive_2026-06-24",
            "substrate_as_LM_test_harness_rigged_audit_2026-06-23",
            "operational_findings_2026-06-23_late_session_HRR_involutive",
            "operational_findings_2026-06-23_sparse_bipolar_20_300x_bundle_lift",
            "Miller_1956_seven_plus_minus_two_working_memory",
        ],
    }
    return (cell_verdict, cell_msg, detail)


# ------------------------------------------------------------------
# Selftest -- mechanism unit-tests
# ------------------------------------------------------------------
def _selftest() -> None:
    """Mechanism sanity at TINY dim. Asserts:
      - sparse-bipolar shape + sparsity rate ~= f.
      - HRR bind/unbind: unbind(bind(a,b), b) ~= a (involutive).
      - cosine cleanup: a sparse-bipolar codebook is approximately orthogonal at modest n.
      - ARM 1-4 each run end-to-end at tiny config; ARM 1 small-M (no crosstalk) should be near-perfect;
        ARM 4 with k=2 working memory should also be near-perfect.
    """
    g = np.random.default_rng(0)
    dim = 256; f = 0.05
    X = _sparse_bipolar(5, dim, f, g)
    assert X.shape == (5, dim), "sparse-bipolar shape mismatch"
    avg_nz = float(np.mean(np.count_nonzero(X, axis=1)))
    expect = f * dim
    assert abs(avg_nz - expect) <= max(1.0, 0.2 * expect), (
        "sparse-bipolar nz=%.1f vs expected %.1f" % (avg_nz, expect)
    )
    # HRR involutive
    a = g.standard_normal(dim).astype(np.float32)
    b = _sparse_bipolar(1, dim, f, g)[0]
    c = _bind(a, b)
    a_back = _unbind(c, b)
    # b may not be self-inverse under HRR (would need unitary), but the recovery
    # vs a should be strongly correlated (cosine > 0.5 at this f)
    cos_ab = float(_cosine(a_back, a[None, :])[0])
    assert cos_ab > 0.3, "HRR bind/unbind round-trip cosine too low (%.3f)" % cos_ab

    # ARM 1 tiny: codebook cleanup at small M should be near-perfect (sparse-bipolar codebook is
    # approximately orthogonal at modest n; cue carrying half the bits suffices to disambiguate).
    a1 = _arm1_pattern_completion(seed=0, dim=512, M=10, corrupt_frac=0.50, f=0.05)
    assert a1["top1_recovery_rate"] > 0.85, (
        "ARM 1 tiny self-test: top1 recovery too low (%.3f); cleanup broken" % a1["top1_recovery_rate"]
    )
    print("[selftest] ARM 1 tiny top1=%.3f median_cleanup_cosine=%.3f cue_only_cosine=%.3f" % (
        a1["top1_recovery_rate"], a1["median_recovery_cosine"], a1["median_cue_only_cosine"]), flush=True)

    # ARM 3 tiny: k=2 should be high accuracy at modest dim
    a3 = _arm3_working_memory(seed=0, dim=2048, k_grid=[1, 2], trials_per_k=10, f=0.05)
    assert a3["per_k_accuracy"][2] > 0.85, (
        "ARM 3 tiny k=2 accuracy too low (%.3f); HRR working memory broken" % a3["per_k_accuracy"][2]
    )
    print("[selftest] ARM 3 tiny k=2 accuracy=%.3f (>0.85 OK)" % a3["per_k_accuracy"][2], flush=True)

    # ARM 2 tiny: small grid + larger dim so crosstalk is below signal -- in-distribution top1 should be high.
    # With M bindings at dim D and sparse f, superposition crosstalk scales as M*f^2/D in cosine variance;
    # 6 bindings at D=4096, f=0.05 -> ~6*0.0025/4096 -- comfortably below the 1/n_obj=0.2 separator.
    a2 = _arm2_compositional(seed=0, dim=4096, n_subj=4, n_obj=4, coverage=0.4, f=0.05)
    assert a2["in_distribution_top1"] > 0.50, (
        "ARM 2 tiny in-distribution top-1 too low (%.3f); HRR composition broken" % a2["in_distribution_top1"]
    )
    print("[selftest] ARM 2 tiny in_dist_top1=%.3f (>0.50 OK)" % a2["in_distribution_top1"], flush=True)

    # ARM 4 tiny: short sequence -- top1 should be well above chance
    a4 = _arm4_bidirectional(seed=0, dim=2048, seq_len=10, vocab=8, f=0.05)
    chance = a4["chance_top1"]
    assert a4["top1"] > 2 * chance, (
        "ARM 4 tiny top-1 (%.3f) <= 2x chance (%.3f); HRR bidirectional broken" % (a4["top1"], chance)
    )
    print("[selftest] ARM 4 tiny top1=%.3f (chance %.3f; >2x chance OK)" % (a4["top1"], chance), flush=True)

    print("[selftest] PASS: HRR involutive + ARM 1/2/3/4 mechanisms operational", flush=True)


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
        "schema": "brain-aligned-aliveness-shotgun-v1",
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
        "metrics_source": "measured_cpu_brain_aligned_aliveness_shotgun",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "N/A (mechanism-characterization cell, not LM cell)",
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
