"""substrate_working_memory_frequency_multiplexed_lock_in_v1 -- WM K-extension.

USER-PROPOSED MECHANISM (verbatim Q3 2026-06-25): "if each marker was in a
different frequency and you used filters, you'd be able to read a lot more
than 32. And, if you flashed them at different frequencies (lock-in) you'd
also get way, way more"

CLOSURE TARGET: WM K-ceiling. Today's WM-v2-cleanup-per-slot cell landed
MIDDLE_BAND (K=128 sigma=1.0 NAIVE=0.908 -> CLEANUP=0.922, lift only 0.014;
K=256 NAIVE=0.555 -> CLEANUP=0.556, no lift). The bind+bundle capacity is
the bottleneck; per-slot cleanup doesn't unlock more capacity.

Brain analog: theta-gamma multiplexing in PFC (Lisman-Buzsaki). Each WM
item bound to a different gamma sub-cycle within a theta cycle; read via
gamma-frequency-selective lock-in filter.

Substrate analog: each slot k stored at a different roll offset
`k * delta_k`; read via lock-in demodulation at slot's offset.

NOT the same as Cell 6 v3 today (shared-W FDM-plasticity stacking which
MIDDLE_BAND'd; that stacked PLASTICITY RULES at different freqs;
this stacks DATA at different freqs).

ARMS (4):
  ARM_NAIVE_HRR_WM_K128     bind+bundle baseline (reproduces today WM v2 0.908)
  ARM_NAIVE_HRR_WM_K256     bind+bundle baseline (reproduces today WM v2 0.555)
  ARM_FM_LOCK_IN_K128       frequency-multiplexed + lock-in demod (new)
  ARM_FM_LOCK_IN_K256       frequency-multiplexed + lock-in demod (new)

Plus K_RAIL [32, 64] for cross-K sanity.

PRE-REG BANDS (LOCKED at module init):

  HARD_PASS_CHAIN_GRADE_WM_K_EXTENSION:
    FM_LOCK_IN_K128 sigma=1.0 >= 0.98
    AND FM_LOCK_IN_K256 sigma=1.0 >= 0.90
    AND cv <= 0.05 across 3 seeds
    AND cross-slot bleed < 0.10 per slot

  HARD_PASS_PARTIAL_LOCK_IN_LIFT:
    FM_LOCK_IN beats NAIVE by >= 0.10 at K=128 OR K=256

  MIDDLE_BAND_FM_MARGINAL:
    FM_LOCK_IN lift over NAIVE in [0.05, 0.10] at K=128 OR K=256

  HARD_FAIL_FM_NO_LIFT:
    FM_LOCK_IN <= NAIVE at K=128 AND K=256
    (frequency multiplexing doesn't help in substrate)

  HARD_FAIL_INTERMOD:
    FM_LOCK_IN cross-slot bleed > 0.10
    (FDM intermod kills mechanism; per-slot purity required)

CONFIG:
  N=4096 (apples-to-apples with WM v2 today)
  K_VALUES = [32, 64, 128, 256]
  sigma = 1.0 (the harder noise regime; matches WM v2)
  P = 8 phases per lock-in demod
  3 seeds [11, 13, 19]

SMOKE: N=4096, K_VALUES=[32, 128, 256], 1 seed.

Author: exp_dev 2026-06-25 (USER-proposed mechanism).
ASCII-only; per-seed checkpoint; substrate-only.
"""
from __future__ import annotations
import sys, os, argparse, time, atexit, math
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_working_memory_frequency_multiplexed_lock_in_v1"
_LLM_CALL_COUNTER = [0]

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Pre-reg HARD bands
HP_FM_K128_RECALL = 0.98
HP_FM_K256_RECALL = 0.90
HP_CV_MAX = 0.05
HP_PARTIAL_LIFT = 0.10
MID_LIFT_LO = 0.05
MID_LIFT_HI = 0.10
HF_INTERMOD_MAX = 0.10  # cross-slot bleed strictly greater is HARD_FAIL

# Lock assertions
assert HP_FM_K128_RECALL > HP_FM_K256_RECALL
assert MID_LIFT_HI == HP_PARTIAL_LIFT
assert 0.0 < HP_CV_MAX <= 0.10

# Config
N_DIM = 4096
CODEBOOK_SIZE = 512
P_LOCKIN = 8  # number of lock-in demod phases (matches lock-in cell ARM_LOCK_IN_P8)

if RUN_MODE == "smoke":
    K_VALUES = [32, 128, 256]
    SIGMAS = [1.0]
    N_ITEMS_PER_K = 50
    SEEDS = [11]
else:
    K_VALUES = [32, 64, 128, 256]
    SIGMAS = [1.0]
    N_ITEMS_PER_K = 200
    SEEDS = [11, 13, 19]

ARMS = ["ARM_NAIVE_HRR_WM", "ARM_FM_LOCK_IN"]

# Provenance rails (today's WM v2 values)
RAIL_NAIVE_K128_LO = 0.88
RAIL_NAIVE_K128_HI = 0.94
RAIL_NAIVE_K256_LO = 0.51
RAIL_NAIVE_K256_HI = 0.60

CONFIG_VERSION = (
    "substrateWmFreqMultiplexedLockIn-v1: N_DIM=%d CODEBOOK_SIZE=%d K=%s "
    "SIGMAS=%s N_ITEMS_PER_K=%d P_LOCKIN=%d arms=%s seeds=%s mode=%s; bands "
    "HP_FM_K128_sigma1>=%.2f HP_FM_K256_sigma1>=%.2f cv<=%.2f "
    "HP_partial_lift>=%.2f mid_lift=[%.2f,%.2f] HF_intermod>%.2f "
    "naive_K128_rail=[%.2f,%.2f] naive_K256_rail=[%.2f,%.2f]"
) % (N_DIM, CODEBOOK_SIZE, K_VALUES, SIGMAS, N_ITEMS_PER_K, P_LOCKIN, ARMS, SEEDS,
     RUN_MODE, HP_FM_K128_RECALL, HP_FM_K256_RECALL, HP_CV_MAX,
     HP_PARTIAL_LIFT, MID_LIFT_LO, MID_LIFT_HI, HF_INTERMOD_MAX,
     RAIL_NAIVE_K128_LO, RAIL_NAIVE_K128_HI,
     RAIL_NAIVE_K256_LO, RAIL_NAIVE_K256_HI)


# =============================================================================
# Substrate primitives
# =============================================================================

def random_bipolar(rng: np.random.Generator, shape) -> np.ndarray:
    return rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=shape)


def bipolar_quantize(v: np.ndarray) -> np.ndarray:
    out = np.sign(v).astype(np.float32)
    out[out == 0] = 1.0
    return out


def build_codebook(rng: np.random.Generator) -> np.ndarray:
    return random_bipolar(rng, (CODEBOOK_SIZE, N_DIM)).astype(np.float32)


def build_slot_tags(rng: np.random.Generator, K_max: int) -> np.ndarray:
    return random_bipolar(rng, (K_max, N_DIM)).astype(np.float32)


def cleanup_to_codebook(retrieve_vec: np.ndarray, codebook: np.ndarray) -> int:
    sims = codebook @ retrieve_vec
    return int(np.argmax(sims))


def cleanup_with_scores(retrieve_vec: np.ndarray,
                         codebook: np.ndarray) -> Tuple[int, np.ndarray]:
    sims = codebook @ retrieve_vec
    return int(np.argmax(sims)), sims


# =============================================================================
# Frequency-multiplexed read/write helpers
# =============================================================================

def fm_delta_k(K: int) -> int:
    """Per-slot roll offset spacing. delta_k = N // (K+1) so that K distinct
    non-zero k_signals all fit strictly in (0, N): {1*dk, 2*dk, ..., K*dk}.

    Using N // K would cause slot k=K-1 to have offset (K-1)*N//K = N - N//K ~ N
    and the (k+1)*delta_k formulation for lock-in k_signal would wrap to 0 for
    slot K-1, collapsing lock-in to identity. (K+1) denominator avoids this.
    """
    return max(1, N_DIM // (K + 1))


def fm_offsets(K: int) -> np.ndarray:
    """Per-slot roll offsets used by SIMPLE-FM: slot k -> offset = (k+1) * delta_k.

    Matches lock-in's k_signal_k = (k+1) * delta_k so simple-FM and lock-in-FM
    use the SAME per-slot frequency channel for apples-to-apples ablation.
    """
    dk = fm_delta_k(K)
    return np.array([(k + 1) * dk for k in range(K)], dtype=np.int64)


def fm_write_workspace_simple(items: np.ndarray, K: int) -> np.ndarray:
    """SIMPLE-FM write (no lock-in carrier): workspace = sum_k roll(item_k, k * delta_k).

    items shape: (K, N_DIM). Returns shape (N_DIM,). This is the NAIVE-FM
    write (data at different roll offsets; no per-phase carrier modulation).
    Lacks the carrier signal that lock-in READ relies on -- used as ablation
    arm to discriminate "FM helps via orthogonal-roll" from "FM helps via
    lock-in carrier-demod gain".
    """
    offsets = fm_offsets(K)
    workspace = np.zeros(N_DIM, dtype=np.float32)
    for k in range(K):
        workspace = workspace + np.roll(items[k], int(offsets[k]))
    return workspace


def fm_write_workspace_lock_in(items: np.ndarray, K: int, P: int) -> np.ndarray:
    """LOCK-IN-FM write: per-slot P-phase carrier modulation summed into workspace.

    For each slot k, the lock-in WRITE protocol is:
      transmit_{k,p} = roll(item_k, p * delta_k) * cos(2*pi*p/P)
      contribution_k = sum_p transmit_{k,p}
      workspace += contribution_k  -- with k_signal = (k+1) * delta_k for slot k
                                       so slot 0 uses k_signal = delta_k (NOT 0).

    The carrier-cosine modulation is the load-bearing piece -- it gives the
    READ-side demod something to coherently sum. Without it (simple-FM
    above), the demod has no signal to lock onto.

    Per-slot k_signal must be distinct AND non-zero (k_signal=0 collapses
    the P-phase roll to identity). We use k_signal_k = (k+1) * delta_k.

    items shape: (K, N_DIM). Returns workspace shape (N_DIM,).
    """
    workspace = np.zeros(N_DIM, dtype=np.float32)
    dk = fm_delta_k(K)
    for k in range(K):
        k_signal = (k + 1) * dk
        slot_contrib = np.zeros(N_DIM, dtype=np.float32)
        for p in range(P):
            carrier = math.cos(2.0 * math.pi * p / P)
            rolled = np.roll(items[k], p * k_signal) * carrier
            slot_contrib = slot_contrib + rolled
        workspace = workspace + slot_contrib
    return workspace


def fm_read_simple(noisy_workspace: np.ndarray, slot_k: int, K: int,
                    codebook: np.ndarray) -> Tuple[int, np.ndarray]:
    """Simple FM read: roll back by -k*delta_k, cleanup against codebook.

    Matched to fm_write_workspace_simple. NO lock-in demod.
    """
    offsets = fm_offsets(K)
    retrieve = np.roll(noisy_workspace, -int(offsets[slot_k]))
    return cleanup_with_scores(retrieve, codebook)


def fm_read_lock_in(noisy_workspace: np.ndarray, slot_k: int, K: int,
                     codebook: np.ndarray, P: int) -> Tuple[int, np.ndarray]:
    """LOCK-IN-FM read: P-phase demod at slot k's k_signal = (k+1)*delta_k.

    Inverse of fm_write_workspace_lock_in:
      demod_{k,p} = roll(noisy_workspace, -p * k_signal) * cos(2*pi*p/P)
      decoded_k = (2/P) * sum_p demod_{k,p}

    For the TARGET slot k, demod sums coherently (cos*cos integrates to P/2).
    For NON-TARGET slot j!=k, the cos*cos cross-term averages to 0 over P
    phases AND the rolls don't realign -- producing a noise-floor contribution.

    Returns (pred_idx, decoded_codebook_scores).
    """
    if P <= 1:
        return fm_read_simple(noisy_workspace, slot_k, K, codebook)
    dk = fm_delta_k(K)
    k_signal = (slot_k + 1) * dk
    acc = np.zeros(N_DIM, dtype=np.float32)
    for p in range(P):
        carrier = math.cos(2.0 * math.pi * p / P)
        rolled = np.roll(noisy_workspace, -p * k_signal) * carrier
        acc = acc + rolled
    acc = (2.0 / P) * acc
    return cleanup_with_scores(acc, codebook)


# =============================================================================
# Arms
# =============================================================================

def eval_naive_hrr_wm(K: int, sigma: float, codebook: np.ndarray,
                       slot_tags_full: np.ndarray,
                       rng: np.random.Generator
                       ) -> Tuple[float, float]:
    """ARM_NAIVE_HRR_WM: standard bind+bundle WM (reproduces WM v2 today).

    Returns (mean_recall, mean_cross_slot_bleed). Bleed = avg over slots of
    P(retrieved item index belongs to a DIFFERENT slot than the queried one).
    """
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / K))
    slot_tags = slot_tags_full[:K]
    correct = 0
    total = 0
    bleed_count = 0
    bleed_total = 0
    for _t in range(n_trials):
        idx = rng.choice(CODEBOOK_SIZE, size=K, replace=False)
        items = codebook[idx]
        workspace = (items * slot_tags).sum(axis=0).astype(np.float32)
        if sigma > 0.0:
            noise = rng.standard_normal(workspace.shape).astype(np.float32) * sigma
            noisy = workspace + noise
        else:
            noisy = workspace
        noisy_bp = bipolar_quantize(noisy)
        idx_set = set(int(x) for x in idx)
        for i in range(K):
            r = (noisy_bp * slot_tags[i]).astype(np.float32)
            pred_idx = cleanup_to_codebook(r, codebook)
            if pred_idx == int(idx[i]):
                correct += 1
            else:
                # cross-slot bleed: predicted index is some OTHER slot's stored item
                if pred_idx in idx_set:
                    bleed_count += 1
            total += 1
            bleed_total += 1
    return (correct / max(total, 1),
            bleed_count / max(bleed_total, 1))


def eval_fm_lock_in(K: int, sigma: float, codebook: np.ndarray,
                     slot_tags_full: np.ndarray,
                     rng: np.random.Generator,
                     P: int) -> Tuple[float, float]:
    """ARM_FM_LOCK_IN: frequency-multiplexed WM with lock-in WRITE + READ.

    WRITE: per-slot P-phase carrier-modulated roll into shared workspace
           (fm_write_workspace_lock_in). Each slot k has k_signal=(k+1)*delta_k.
    READ:  P-phase lock-in demod at slot's k_signal (fm_read_lock_in).

    Slot tags NOT used; the roll-offset carrier IS the slot identity.

    Returns (mean_recall, mean_cross_slot_bleed).
    """
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / K))
    correct = 0
    total = 0
    bleed_count = 0
    bleed_total = 0
    for _t in range(n_trials):
        idx = rng.choice(CODEBOOK_SIZE, size=K, replace=False)
        items = codebook[idx]  # (K, N_DIM)
        workspace = fm_write_workspace_lock_in(items, K, P)
        if sigma > 0.0:
            noise = rng.standard_normal(workspace.shape).astype(np.float32) * sigma
            noisy = workspace + noise
        else:
            noisy = workspace
        # NOT bipolar-quantize -- lock-in math needs raw amplitudes to
        # coherently sum.
        idx_set = set(int(x) for x in idx)
        for i in range(K):
            pred_idx, _ = fm_read_lock_in(noisy, i, K, codebook, P)
            if pred_idx == int(idx[i]):
                correct += 1
            else:
                if pred_idx in idx_set:
                    bleed_count += 1
            total += 1
            bleed_total += 1
    return (correct / max(total, 1),
            bleed_count / max(bleed_total, 1))


ARM_EVALS = {
    "ARM_NAIVE_HRR_WM": eval_naive_hrr_wm,
    "ARM_FM_LOCK_IN": eval_fm_lock_in,
}


# =============================================================================
# Self-test
# =============================================================================

def _selftest():
    rng = np.random.default_rng(0)
    cb = build_codebook(rng)
    K_max = max(K_VALUES)
    slot_tags = build_slot_tags(np.random.default_rng(1), K_max)

    # T1: at K=2 sigma=0.0, both arms recall ~ 1.0
    r_naive, bleed_naive = eval_naive_hrr_wm(2, 0.0, cb, slot_tags,
                                              np.random.default_rng(2))
    r_fm, bleed_fm = eval_fm_lock_in(2, 0.0, cb, slot_tags,
                                       np.random.default_rng(3), P=P_LOCKIN)
    assert r_naive >= 0.95, "T1 naive recall=%.3f at K=2 sigma=0.0" % r_naive
    assert r_fm >= 0.95, "T1 fm recall=%.3f at K=2 sigma=0.0" % r_fm
    print("[selftest] T1 PASS: K=2 sigma=0.0 naive=%.3f bleed=%.3f fm=%.3f bleed=%.3f"
          % (r_naive, bleed_naive, r_fm, bleed_fm))

    # T2: roll orthogonality at N=4096 (smaller N than the lock-in cell's 8192)
    v = np.random.default_rng(7).standard_normal(N_DIM).astype(np.float32)
    v_self = float((v @ v) / N_DIM)
    v_rot_16 = float((np.roll(v, 16) @ v) / N_DIM)
    v_rot_32 = float((np.roll(v, 32) @ v) / N_DIM)
    v_rot_128 = float((np.roll(v, 128) @ v) / N_DIM)
    assert v_self > 0.5, "T2 random self-norm should be ~1: %.3f" % v_self
    assert abs(v_rot_16) < 0.2, "T2 roll(v,16) orthogonality: |%.3f| > 0.2" % v_rot_16
    assert abs(v_rot_32) < 0.2, "T2 roll(v,32) orthogonality: |%.3f| > 0.2" % v_rot_32
    assert abs(v_rot_128) < 0.2, "T2 roll(v,128) orthogonality: |%.3f| > 0.2" % v_rot_128
    print("[selftest] T2 PASS: roll orthogonality at N=%d k=16,32,128 self=%.3f"
          % (N_DIM, v_self))

    # T3: at K=8 sigma=0.0, FM with lock-in recall >= 0.80
    r_naive_8, _ = eval_naive_hrr_wm(8, 0.0, cb, slot_tags,
                                       np.random.default_rng(4))
    r_fm_8, _ = eval_fm_lock_in(8, 0.0, cb, slot_tags,
                                  np.random.default_rng(5), P=P_LOCKIN)
    # K=8 with no noise: FM might be lower than NAIVE due to roll-correlation;
    # at minimum it shouldn't be at chance
    assert r_naive_8 >= 0.80, "T3 naive K=8 recall=%.3f < 0.80" % r_naive_8
    assert r_fm_8 > 5.0 / CODEBOOK_SIZE, \
        "T3 fm K=8 recall=%.3f at-or-below chance" % r_fm_8
    print("[selftest] T3 PASS: K=8 sigma=0.0 naive=%.3f fm=%.3f" % (r_naive_8, r_fm_8))

    # T4: FM lock-in P=1 degenerates to fm_read_simple (when WRITE is also simple)
    items = cb[:4]  # K=4 items
    workspace_simple = fm_write_workspace_simple(items, 4)
    pred_p1, _ = fm_read_lock_in(workspace_simple, 0, 4, cb, P=1)
    pred_simple, _ = fm_read_simple(workspace_simple, 0, 4, cb)
    assert pred_p1 == pred_simple, "T4 P=1 should match simple: %d vs %d" % (pred_p1, pred_simple)
    print("[selftest] T4 PASS: P=1 lock-in == simple read")

    # T4b: FM lock-in WRITE + READ at sigma=0, K=4: should perfectly recover slot 0
    workspace_lock = fm_write_workspace_lock_in(items, 4, P=P_LOCKIN)
    pred_lock, _ = fm_read_lock_in(workspace_lock, 0, 4, cb, P=P_LOCKIN)
    assert pred_lock == 0, "T4b lock-in WRITE+READ slot 0 should recover idx 0: got %d" % pred_lock
    # also slot 1, 2, 3
    for s in range(4):
        pred_s, _ = fm_read_lock_in(workspace_lock, s, 4, cb, P=P_LOCKIN)
        assert pred_s == s, "T4b lock-in slot %d should recover idx %d: got %d" % (s, s, pred_s)
    print("[selftest] T4b PASS: lock-in WRITE+READ at K=4 P=%d sigma=0 perfectly recovers all slots" % P_LOCKIN)

    # T5: shapes correct
    assert cb.shape == (CODEBOOK_SIZE, N_DIM), "T5 codebook %s" % (cb.shape,)
    assert slot_tags.shape == (K_max, N_DIM), "T5 slot_tags %s" % (slot_tags.shape,)
    print("[selftest] T5 PASS: shapes correct")

    # T6: delta_k orthogonality margin (chain-grade lock-in sanity)
    # For K=128 at N=4096, delta_k = N//(K+1) = 4096//129 = 31. Verify roll(v, 31) orthogonal.
    K_test = 128
    dk_test = fm_delta_k(K_test)
    expected_dk = N_DIM // (K_test + 1)
    assert dk_test == expected_dk, "T6 delta_k wrong: %d (expected %d)" % (dk_test, expected_dk)
    v_test = np.random.default_rng(13).standard_normal(N_DIM).astype(np.float32)
    overlap_dk = abs(float((np.roll(v_test, dk_test) @ v_test) / N_DIM))
    assert overlap_dk < 0.2, "T6 delta_k=%d at K=%d overlap=%.3f > 0.2 (orth broken)" \
        % (dk_test, K_test, overlap_dk)
    # Also verify max-offset for the LAST slot (K*delta_k) is still < N (no wrap)
    max_offset = K_test * dk_test
    assert max_offset < N_DIM, "T6 max offset %d >= N_DIM %d (slot %d would wrap)" \
        % (max_offset, N_DIM, K_test - 1)
    print("[selftest] T6 PASS: K=%d delta_k=%d max_offset=%d (< N=%d) roll-orth %.3f"
          % (K_test, dk_test, max_offset, N_DIM, overlap_dk))

    # T7: bands locked
    assert HP_FM_K128_RECALL == 0.98
    assert HP_FM_K256_RECALL == 0.90
    print("[selftest] T7 PASS: bands locked")

    # T8: substrate-only
    assert _LLM_CALL_COUNTER[0] == 0, "T8 LLM counter non-zero"
    print("[selftest] T8 PASS: LLM counter = 0")

    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# =============================================================================
# Per-seed run
# =============================================================================

def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print("\n[seed=%d] building codebook + slot tags at N_DIM=%d ..." % (seed, N_DIM), flush=True)
    codebook_rng = np.random.default_rng(seed * 1000 + 1)
    slot_rng = np.random.default_rng(seed * 1000 + 2)
    codebook = build_codebook(codebook_rng)
    K_max = max(K_VALUES)
    slot_tags = build_slot_tags(slot_rng, K_max)
    print("[seed=%d] codebook %s slot tags %s ready"
          % (seed, codebook.shape, slot_tags.shape), flush=True)

    by_arm = {}
    for arm_label in ARMS:
        t_arm = time.time()
        by_arm[arm_label] = {"per_K_per_sigma": {}, "per_K_bleed": {}, "wall_s": 0.0}
        trial_rng = np.random.default_rng(seed * 1000 + 3 + ARMS.index(arm_label) * 100)
        for K in K_VALUES:
            recall_at_sigma = {}
            bleed_at_sigma = {}
            for sigma in SIGMAS:
                if arm_label == "ARM_FM_LOCK_IN":
                    recall, bleed = eval_fm_lock_in(K, sigma, codebook, slot_tags,
                                                      trial_rng, P=P_LOCKIN)
                else:
                    recall, bleed = eval_naive_hrr_wm(K, sigma, codebook,
                                                       slot_tags, trial_rng)
                recall_at_sigma["sigma_%.2f" % sigma] = round(float(recall), 4)
                bleed_at_sigma["sigma_%.2f" % sigma] = round(float(bleed), 4)
            by_arm[arm_label]["per_K_per_sigma"]["K_%d" % K] = recall_at_sigma
            by_arm[arm_label]["per_K_bleed"]["K_%d" % K] = bleed_at_sigma
        by_arm[arm_label]["wall_s"] = round(time.time() - t_arm, 2)
        per_K = by_arm[arm_label]["per_K_per_sigma"]
        per_K_bleed = by_arm[arm_label]["per_K_bleed"]
        summary = " ".join(["K%d_s1.0=%.3f(bleed=%.3f)" % (
            int(k.split("_")[1]),
            v.get("sigma_1.00", 0.0),
            per_K_bleed[k].get("sigma_1.00", 0.0))
            for k, v in per_K.items()])
        print("  [seed=%d arm=%s] %s wall=%.1fs"
              % (seed, arm_label, summary, by_arm[arm_label]["wall_s"]), flush=True)

    # Provenance rail check: NAIVE_K128 + NAIVE_K256 should reproduce WM v2
    naive_k128 = by_arm["ARM_NAIVE_HRR_WM"]["per_K_per_sigma"].get(
        "K_128", {}).get("sigma_1.00", float("nan"))
    naive_k256 = by_arm["ARM_NAIVE_HRR_WM"]["per_K_per_sigma"].get(
        "K_256", {}).get("sigma_1.00", float("nan"))
    rail_k128_ok = RAIL_NAIVE_K128_LO <= naive_k128 <= RAIL_NAIVE_K128_HI
    rail_k256_ok = (math.isnan(naive_k256)
                     or RAIL_NAIVE_K256_LO <= naive_k256 <= RAIL_NAIVE_K256_HI)

    return {
        "seed": seed,
        "by_arm": by_arm,
        "N": N_DIM,
        "CODEBOOK_SIZE": CODEBOOK_SIZE,
        "K_VALUES": K_VALUES,
        "SIGMAS": SIGMAS,
        "N_ITEMS_PER_K": N_ITEMS_PER_K,
        "P_LOCKIN": P_LOCKIN,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "rail_naive_k128_ok": rail_k128_ok,
        "rail_naive_k256_ok": rail_k256_ok,
        "naive_k128_sigma1": float(naive_k128) if not math.isnan(naive_k128) else None,
        "naive_k256_sigma1": float(naive_k256) if not math.isnan(naive_k256) else None,
    }


# =============================================================================
# Verdict
# =============================================================================

def _per_K_sigma_mean(units, arm_label, K, sigma, field="per_K_per_sigma"):
    vals = []
    for u in units:
        d = u["by_arm"][arm_label].get(field, {})
        v = d.get("K_%d" % K, {}).get("sigma_%.2f" % sigma, float("nan"))
        if not math.isnan(v):
            vals.append(v)
    if not vals:
        return float("nan"), 0.0, []
    m = float(np.mean(vals))
    cv = float(np.std(vals) / max(abs(m), 1e-9)) if len(vals) >= 2 else 0.0
    return m, cv, vals


def compute_verdict(units: List[Dict]) -> Tuple[str, str]:
    if not units:
        return ("HARD_FAIL", "no per-seed data")

    out_by_arm = {}
    for arm in ARMS:
        rows = {}
        for K in K_VALUES:
            for sigma in SIGMAS:
                m, cv, raw = _per_K_sigma_mean(units, arm, K, sigma)
                m_b, _, _ = _per_K_sigma_mean(units, arm, K, sigma,
                                                field="per_K_bleed")
                rows["K%d_sigma%.1f" % (K, sigma)] = {
                    "mean": round(m, 4), "cv": round(cv, 4),
                    "bleed": round(m_b, 4),
                    "per_seed": [round(v, 4) for v in raw],
                }
        out_by_arm[arm] = rows

    fm_k128, fm_k128_cv, _ = _per_K_sigma_mean(units, "ARM_FM_LOCK_IN", 128, 1.0)
    fm_k256, fm_k256_cv, _ = _per_K_sigma_mean(units, "ARM_FM_LOCK_IN", 256, 1.0)
    naive_k128, naive_k128_cv, _ = _per_K_sigma_mean(units, "ARM_NAIVE_HRR_WM", 128, 1.0)
    naive_k256, naive_k256_cv, _ = _per_K_sigma_mean(units, "ARM_NAIVE_HRR_WM", 256, 1.0)

    fm_k128_bleed, _, _ = _per_K_sigma_mean(units, "ARM_FM_LOCK_IN", 128, 1.0,
                                              field="per_K_bleed")
    fm_k256_bleed, _, _ = _per_K_sigma_mean(units, "ARM_FM_LOCK_IN", 256, 1.0,
                                              field="per_K_bleed")
    max_fm_bleed = max(
        b for b in [fm_k128_bleed, fm_k256_bleed] if not math.isnan(b)
    ) if any(not math.isnan(b) for b in [fm_k128_bleed, fm_k256_bleed]) else 0.0

    rail_breached = sum(1 for u in units
                         if not (u.get("rail_naive_k128_ok", True)
                                  and u.get("rail_naive_k256_ok", True)))

    lift_k128 = fm_k128 - naive_k128 if not (math.isnan(fm_k128) or math.isnan(naive_k128)) else float("nan")
    lift_k256 = fm_k256 - naive_k256 if not (math.isnan(fm_k256) or math.isnan(naive_k256)) else float("nan")
    max_lift = max(
        l for l in [lift_k128, lift_k256] if not math.isnan(l)
    ) if any(not math.isnan(l) for l in [lift_k128, lift_k256]) else float("nan")

    per_K_summary = " ".join("K%d_NAIVE=%.3f_FM=%.3f_bleed=%.3f" % (
        K,
        out_by_arm["ARM_NAIVE_HRR_WM"]["K%d_sigma1.0" % K]["mean"],
        out_by_arm["ARM_FM_LOCK_IN"]["K%d_sigma1.0" % K]["mean"],
        out_by_arm["ARM_FM_LOCK_IN"]["K%d_sigma1.0" % K]["bleed"])
        for K in K_VALUES)

    summ = ("FM_K128=%.4f (cv=%.3f bleed=%.3f) FM_K256=%.4f (cv=%.3f bleed=%.3f) "
            "NAIVE_K128=%.4f (cv=%.3f) NAIVE_K256=%.4f (cv=%.3f) "
            "lift_K128=%.4f lift_K256=%.4f max_lift=%.4f max_bleed=%.4f "
            "rail_breach=%d/%d | per-K: %s | WM_v2_NAIVE_K128=0.908 WM_v2_NAIVE_K256=0.555 (ref)"
            ) % (
        fm_k128, fm_k128_cv, fm_k128_bleed,
        fm_k256, fm_k256_cv, fm_k256_bleed,
        naive_k128, naive_k128_cv, naive_k256, naive_k256_cv,
        lift_k128, lift_k256, max_lift, max_fm_bleed,
        rail_breached, len(units), per_K_summary,
    )

    # RAIL_SANITY_BREACH
    if rail_breached >= max(1, (len(units) + 1) // 2):
        return ("RAIL_SANITY_BREACH",
                "RAIL_SANITY_BREACH_NAIVE_OUT_OF_WM_V2_BAND: " + summ)

    # HARD_FAIL_INTERMOD
    if max_fm_bleed > HF_INTERMOD_MAX:
        return ("HARD_FAIL_INTERMOD",
                "HARD_FAIL_FM_CROSS_SLOT_BLEED_TOO_HIGH: " + summ)

    # HARD_PASS_CHAIN_GRADE
    if (not math.isnan(fm_k128) and fm_k128 >= HP_FM_K128_RECALL
            and not math.isnan(fm_k256) and fm_k256 >= HP_FM_K256_RECALL
            and fm_k128_cv <= HP_CV_MAX and fm_k256_cv <= HP_CV_MAX
            and max_fm_bleed <= HF_INTERMOD_MAX):
        return ("HARD_PASS_CHAIN_GRADE_WM_K_EXTENSION",
                "HARD_PASS_CHAIN_GRADE_WM_K_EXTENSION_FM_LOCK_IN: " + summ)

    # HARD_FAIL_FM_NO_LIFT (FM <= NAIVE at BOTH K)
    if (not math.isnan(lift_k128) and not math.isnan(lift_k256)
            and lift_k128 <= 0.0 and lift_k256 <= 0.0):
        return ("HARD_FAIL_FM_NO_LIFT",
                "HARD_FAIL_FM_NO_LIFT_OVER_NAIVE: " + summ)

    # HARD_PASS_PARTIAL (lift >= 0.10 at K=128 OR K=256)
    if not math.isnan(max_lift) and max_lift >= HP_PARTIAL_LIFT:
        return ("HARD_PASS_PARTIAL_LOCK_IN_LIFT",
                "HARD_PASS_PARTIAL_FM_LOCK_IN_LIFTS_NAIVE: " + summ)

    # MIDDLE_BAND (lift in [0.05, 0.10])
    if not math.isnan(max_lift) and MID_LIFT_LO <= max_lift < MID_LIFT_HI:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_FM_MARGINAL: " + summ)

    return ("MIDDLE_BAND", "MIDDLE_BAND_UNCLASSIFIED: " + summ)


# =============================================================================
# atexit synthesizer
# =============================================================================

_RESULTS_HOLDER: Dict = {"out_dir": None, "started_at": time.time()}


def _atexit_synth():
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        v, vmsg = compute_verdict(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS],
                              run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

    v, vmsg = compute_verdict(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "USER-proposed mechanism (Q3 2026-06-25): frequency-multiplexed WM "
            "where each slot k stored at a different roll offset (k * delta_k) "
            "instead of a slot-tag bind. Read uses P=%d phase lock-in demodulation. "
            "Brain analog: theta-gamma multiplexing in PFC (Lisman-Buzsaki). "
            "Substrate analog: chain-grade lock-in primitive applied as slot-"
            "isolation filter. NOT same as Cell 6 v3 today (shared-W FDM-"
            "plasticity stacking which MIDDLE_BAND'd; that stacked PLASTICITY "
            "RULES at different freqs -- this stacks DATA at different freqs). "
            "Pre-reg per preregs/2026-06-25_substrate_working_memory_frequency_"
            "multiplexed_lock_in_v1.md."
            % P_LOCKIN
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
