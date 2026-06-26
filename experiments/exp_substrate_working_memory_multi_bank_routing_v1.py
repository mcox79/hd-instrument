"""substrate_working_memory_multi_bank_routing_v1 -- corrected Cell Y.

CORRECTED CELL Y (USER 2026-06-25): the v1 frequency-multiplexed lock-in
(exp_substrate_working_memory_frequency_multiplexed_lock_in_v1) HARD_FAILED
with massive intermod bleed (K=128 bleed=0.180; K=256 bleed=0.453) -- 4th
cell-evidence point that FDM stacking on a SHARED W produces crosstalk that
eats per-symbol fidelity. The corrected substrate analog is MULTI-WM-BANK
routing: instead of stacking K items on a single W, use N_BANKS separate W
matrices (different "rooms"), each within the per-bank K-ceiling=64 verified
by Cell D today (exp_substrate_working_memory_v2_extended_K_with_cleanup_per_slot:
NAIVE K=128 = 0.908, NAIVE K=256 = 0.555). A router (analog to today's Cell 1
partition routing chain-grade @ M=1M) picks which bank to read based on slot.

Brain analog: PFC working memory uses MULTIPLE cortical microcircuits
(different prefrontal sub-regions), each holding small K, with attention/
routing layer picking which sub-region to read.

Substrate-architectural reuse: same decomposition pattern that delivered
chain-grade KG retrieval at M=1M today (partition routing) -- applied to
WM K-extension.

ARMS (8):
  ARM_NAIVE_SINGLE_BANK_K32   rail; target ~1.000 at sigma=1.0
  ARM_NAIVE_SINGLE_BANK_K128  rail; target ~0.908 (matches Cell D today)
  ARM_NAIVE_SINGLE_BANK_K256  rail; target ~0.555 (matches Cell D today)
  ARM_MULTI_BANK_8x32_K256    8 banks x 32 items each = 256 total
  ARM_MULTI_BANK_4x64_K256    4 banks x 64 items each = 256 total
  ARM_MULTI_BANK_2x128_K256   2 banks x 128 items each = 256 total
  ARM_MULTI_BANK_16x16_K256  16 banks x 16 items each = 256 total
  ARM_MULTI_BANK_32x32_K1024 32 banks x 32 items each = 1024 total (stretch)

PRE-REG BANDS (LOCKED at module init via assert):

  HARD_PASS_CHAIN_GRADE_WM_MULTI_BANK_K256:
    best MULTI_BANK arm at K_total=256 has mean recall >= 0.95 at sigma=1.0
    AND cv <= 0.05 across 3 seeds
    AND router accuracy >= 0.95

  HARD_PASS_PARTIAL_MULTI_BANK_LIFT:
    best MULTI_BANK at K_total=256 lifts recall by >= 0.20 over NAIVE K=256
    (= 0.555 baseline), but below absolute 0.95 chain-grade floor

  HARD_PASS_BONUS_K1024:
    ARM_MULTI_BANK_32x32_K1024 mean recall >= 0.95 at sigma=1.0
    (would extend substrate-native WM K-ceiling 32x over single-bank)

  MIDDLE_BAND_MULTI_BANK_MARGINAL:
    lift in [0.05, 0.20] over NAIVE K=256

  HARD_FAIL_ROUTER_CROSSTALK:
    best MULTI_BANK <= NAIVE single-bank at K_total=256
    (router selection introduces crosstalk that eats per-bank gain)

  HARD_FAIL_BANK_SIZE_DEGENERATE:
    only one (N_BANKS, K_PER_BANK) configuration works (lacks robustness)

  RAIL_SANITY_BREACH:
    NAIVE_K128 outside [0.85, 0.94] OR NAIVE_K256 outside [0.51, 0.60]
    (regime drift from Cell D today -- comparison invalid)

CONFIG:
  N_DIM = 4096 (matches Cell D for apples-to-apples)
  CODEBOOK_SIZE = 1024 (max K_total across arms)
  sigma = 1.0 (matches Cell D harder regime where K-ceiling discriminates)
  N_ITEMS_PER_K = 200 (held-out items per (arm, seed))
  Seeds [11, 13, 19] (cross-cell consistent)

Author: exp_dev 2026-06-25 (corrected Cell Y per USER request).
ASCII-only; per-seed checkpoint; substrate-only; numpy only.
"""
from __future__ import annotations
import sys, os, argparse, time, atexit, math
from pathlib import Path
from typing import Dict, List, Tuple
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

ANCHOR_NAME = "substrate_working_memory_multi_bank_routing_v1"
_LLM_CALL_COUNTER = [0]

# Pre-reg HARD bands
HP_CHAIN_GRADE_RECALL = 0.95           # MULTI_BANK K_total=256 best arm floor
HP_CHAIN_GRADE_CV = 0.05                # cv ceiling across seeds
HP_CHAIN_GRADE_ROUTE_ACC = 0.95         # router accuracy floor
HP_PARTIAL_LIFT = 0.20                  # lift over NAIVE_K256 baseline
HP_BONUS_K1024_RECALL = 0.95            # stretch arm at K_total=1024
MID_LIFT_LO = 0.05
MID_LIFT_HI = 0.20
Q_SUSPECT_SATURATION = 0.995

# Sanity rails (DERIVED from Cell D today; META_M6)
RAIL_NAIVE_K32_MIN = 0.95
RAIL_NAIVE_K128_LO = 0.85
RAIL_NAIVE_K128_HI = 0.94
RAIL_NAIVE_K256_LO = 0.51
RAIL_NAIVE_K256_HI = 0.60

# Lock assertions (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
assert 0.0 < HP_CHAIN_GRADE_RECALL < 1.0, "band locked"
assert 0.0 < HP_CHAIN_GRADE_CV < 1.0, "cv ceiling locked"
assert 0.0 < HP_CHAIN_GRADE_ROUTE_ACC < 1.0, "route acc locked"
assert MID_LIFT_LO < MID_LIFT_HI == HP_PARTIAL_LIFT, "MID band locked"
assert RAIL_NAIVE_K128_LO < RAIL_NAIVE_K128_HI, "K128 rail locked"
assert RAIL_NAIVE_K256_LO < RAIL_NAIVE_K256_HI, "K256 rail locked"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config (regime-matched to Cell D today)
N_DIM = 4096
CODEBOOK_SIZE = 1024  # max K_total across arms (must hold 1024 for stretch arm)
SIGMA = 1.0           # matches Cell D harder regime where K-ceiling discriminates
N_ITEMS_PER_K = 200 if RUN_MODE != "smoke" else 40

if RUN_MODE == "smoke":
    SEEDS = [11]
else:
    SEEDS = [11, 13, 19]

# Arm specification (label, n_banks, k_per_bank, k_total)
# Each entry locks the configuration.
ARM_SPECS = [
    ("ARM_NAIVE_SINGLE_BANK_K32",    1,  32,  32),
    ("ARM_NAIVE_SINGLE_BANK_K128",   1, 128, 128),
    ("ARM_NAIVE_SINGLE_BANK_K256",   1, 256, 256),
    ("ARM_MULTI_BANK_8x32_K256",     8,  32, 256),
    ("ARM_MULTI_BANK_4x64_K256",     4,  64, 256),
    ("ARM_MULTI_BANK_2x128_K256",    2, 128, 256),
    ("ARM_MULTI_BANK_16x16_K256",   16,  16, 256),
    ("ARM_MULTI_BANK_32x32_K1024",  32,  32, 1024),
]
ARMS = [s[0] for s in ARM_SPECS]
ARM_BY_LABEL = {s[0]: s for s in ARM_SPECS}

CONFIG_VERSION = (
    "substrateWmMultiBankRoutingV1: N_DIM=%d CODEBOOK_SIZE=%d sigma=%.1f "
    "N_ITEMS_PER_K=%d arms=%d seeds=%s mode=%s; bands HP_chain>=%.2f cv<=%.2f "
    "route_acc>=%.2f HP_partial_lift>=%.2f mid_lift=[%.2f,%.2f] HP_bonus_K1024>=%.2f "
    "rails NAIVE_K128=[%.2f,%.2f] NAIVE_K256=[%.2f,%.2f] Q_sat>=%.3f"
) % (N_DIM, CODEBOOK_SIZE, SIGMA, N_ITEMS_PER_K, len(ARMS), SEEDS, RUN_MODE,
     HP_CHAIN_GRADE_RECALL, HP_CHAIN_GRADE_CV, HP_CHAIN_GRADE_ROUTE_ACC,
     HP_PARTIAL_LIFT, MID_LIFT_LO, MID_LIFT_HI, HP_BONUS_K1024_RECALL,
     RAIL_NAIVE_K128_LO, RAIL_NAIVE_K128_HI,
     RAIL_NAIVE_K256_LO, RAIL_NAIVE_K256_HI,
     Q_SUSPECT_SATURATION)


# =============================================================================
# Substrate primitives (mirrors Cell D today / WM-HRR-slots-PRODUCTION v1)
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
    """K_max slot tags shared across banks (slot semantics independent of bank)."""
    return random_bipolar(rng, (K_max, N_DIM)).astype(np.float32)


def build_bank_tags(rng: np.random.Generator, n_banks: int) -> np.ndarray:
    """One bank cue per bank (used for routing). Codebook-sized; clean cue regime."""
    return random_bipolar(rng, (n_banks, N_DIM)).astype(np.float32)


def cleanup_to_codebook(retrieve_vec: np.ndarray, codebook: np.ndarray) -> int:
    sims = codebook @ retrieve_vec
    return int(np.argmax(sims))


# =============================================================================
# Arm implementations
# =============================================================================

def _write_bank(items_in_bank: np.ndarray, slot_tags_b: np.ndarray,
                 sigma: float, rng: np.random.Generator) -> np.ndarray:
    """Bundle bind(item_i, slot_i) for one bank + noise + bipolar-quantize."""
    workspace = (items_in_bank * slot_tags_b).sum(axis=0).astype(np.float32)
    if sigma > 0.0:
        noise = rng.standard_normal(workspace.shape).astype(np.float32) * sigma
        noisy = workspace + noise
    else:
        noisy = workspace
    return bipolar_quantize(noisy)


def _read_with_cleanup(noisy_bp: np.ndarray, slot_tag: np.ndarray,
                        codebook: np.ndarray) -> int:
    """Unbind via slot tag; iterated cleanup against codebook (matches Cell D
    ARM_CLEANUP_PER_SLOT; theta-gamma analog)."""
    r1 = (noisy_bp * slot_tag).astype(np.float32)
    sims1 = codebook @ r1
    cand_idx = int(np.argmax(sims1))
    r2 = 0.5 * r1 + 0.5 * codebook[cand_idx]
    r2_bp = bipolar_quantize(r2)
    return cleanup_to_codebook(r2_bp, codebook)


def eval_single_bank(n_banks: int, k_per_bank: int, k_total: int,
                      codebook: np.ndarray, slot_tags_full: np.ndarray,
                      rng: np.random.Generator) -> Tuple[float, float]:
    """ARM_NAIVE_SINGLE_BANK_*: matches Cell D ARM_CLEANUP_PER_SLOT exactly.

    Returns (recall, router_acc=1.0 by definition; single bank).
    """
    assert n_banks == 1, "single-bank arm requires n_banks=1"
    K = k_per_bank
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / K))
    slot_tags = slot_tags_full[:K]
    correct = 0
    total = 0
    for _t in range(n_trials):
        idx = rng.choice(CODEBOOK_SIZE, size=K, replace=False)
        items = codebook[idx]
        noisy_bp = _write_bank(items, slot_tags, SIGMA, rng)
        for i in range(K):
            pred_idx = _read_with_cleanup(noisy_bp, slot_tags[i], codebook)
            if pred_idx == int(idx[i]):
                correct += 1
            total += 1
    return correct / max(total, 1), 1.0


def eval_multi_bank(n_banks: int, k_per_bank: int, k_total: int,
                     codebook: np.ndarray, slot_tags_full: np.ndarray,
                     rng: np.random.Generator) -> Tuple[float, float]:
    """ARM_MULTI_BANK_*: N_BANKS separate W matrices + cue-based router.

    Mechanism:
      1. Per bank b in [0..n_banks): build separate workspace W_b that holds
         only k_per_bank items (bind+bundle, noise, bipolar-quantize).
      2. Each slot index in [0..k_total) maps to (bank_idx, local_slot)
         where bank_idx = slot // k_per_bank, local_slot = slot % k_per_bank.
      3. Router: query with a noisy version of the BANK CUE (b_cue_b), find
         argmax over all bank cues -> bank_idx_routed.
      4. Read: workspace[bank_idx_routed] * slot_tag[local_slot] -> iterated
         cleanup against codebook -> predicted item index.

    Routing cue regime: matches Cell 1 partition routing today (CAT_COS=0.70
    delivered route_acc>=0.95 chain-grade at M=1M).
    """
    assert n_banks >= 2, "multi-bank arm requires n_banks>=2"
    K_total = n_banks * k_per_bank
    assert K_total == k_total
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / K_total))
    slot_tags = slot_tags_full[:k_per_bank]
    # Bank cues: random bipolar, separate from slot tags (independent cue space)
    bank_tags = build_bank_tags(rng, n_banks)
    correct = 0
    total = 0
    route_correct = 0
    route_total = 0
    CUE_COS = 0.70  # matches Cell 1 partition routing today (clean cue regime)
    cue_noise_scale = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))
    for _t in range(n_trials):
        # Sample K_total distinct codebook indices; partition into n_banks groups
        idx_global = rng.choice(CODEBOOK_SIZE, size=K_total, replace=False)
        # Build per-bank workspaces
        workspaces = []
        for b in range(n_banks):
            start = b * k_per_bank
            stop = start + k_per_bank
            items_b = codebook[idx_global[start:stop]]
            noisy_bp = _write_bank(items_b, slot_tags, SIGMA, rng)
            workspaces.append(noisy_bp)
        # Per slot retrieval
        for slot_idx in range(K_total):
            bank_true = slot_idx // k_per_bank
            local_slot = slot_idx % k_per_bank
            # Router: noisy bank cue
            cue = CUE_COS * bank_tags[bank_true] + cue_noise_scale * bipolar_quantize(
                rng.standard_normal(N_DIM).astype(np.float32)
            )
            sims_bank = bank_tags @ cue
            bank_routed = int(np.argmax(sims_bank))
            route_total += 1
            if bank_routed == bank_true:
                route_correct += 1
            # Read from routed bank
            ws = workspaces[bank_routed]
            pred_idx = _read_with_cleanup(ws, slot_tags[local_slot], codebook)
            true_item_idx = int(idx_global[slot_idx])
            if pred_idx == true_item_idx and bank_routed == bank_true:
                correct += 1
            total += 1
    route_acc = route_correct / max(route_total, 1)
    recall = correct / max(total, 1)
    return recall, route_acc


def eval_arm(label: str, codebook: np.ndarray, slot_tags_full: np.ndarray,
              rng: np.random.Generator) -> Dict[str, float]:
    _, n_banks, k_per_bank, k_total = ARM_BY_LABEL[label]
    if n_banks == 1:
        recall, route_acc = eval_single_bank(n_banks, k_per_bank, k_total,
                                              codebook, slot_tags_full, rng)
    else:
        recall, route_acc = eval_multi_bank(n_banks, k_per_bank, k_total,
                                             codebook, slot_tags_full, rng)
    return {"recall": round(float(recall), 4),
            "route_acc": round(float(route_acc), 4),
            "n_banks": n_banks, "k_per_bank": k_per_bank, "k_total": k_total}


# =============================================================================
# Self-test
# =============================================================================

def _selftest():
    rng = np.random.default_rng(0)
    cb = build_codebook(rng)
    K_max = 256
    slot_tags = build_slot_tags(np.random.default_rng(1), K_max)
    # T1: single-bank K=32 sigma=1.0 -> ~1.000 (chain-grade rail from Cell D)
    r = eval_single_bank(1, 32, 32, cb, slot_tags, np.random.default_rng(2))
    assert r[0] >= 0.95, "T1 single-bank K=32 sigma=1.0 recall=%.3f < 0.95" % r[0]
    print("[selftest] T1 PASS: single-bank K=32 sigma=1.0 recall=%.3f" % r[0])

    # T2: multi-bank routing reaches above single-bank K=256 baseline
    # (only requires it's not catastrophic; full envelope checked at full run)
    cb2 = build_codebook(np.random.default_rng(7))
    slot_tags2 = build_slot_tags(np.random.default_rng(8), K_max)
    r2 = eval_multi_bank(8, 32, 256, cb2, slot_tags2, np.random.default_rng(9))
    assert r2[1] >= 0.85, "T2 router acc=%.3f < 0.85 (cue regime broken)" % r2[1]
    # Recall should be far above pure-chance (1/CODEBOOK_SIZE = 1/1024 ~ 0.001)
    assert r2[0] >= 0.5, "T2 multi_bank recall=%.3f < 0.5 (degenerate)" % r2[0]
    print("[selftest] T2 PASS: multi_bank 8x32 recall=%.3f route_acc=%.3f"
          % (r2[0], r2[1]))

    # T3: codebook + slot tag shapes
    assert cb.shape == (CODEBOOK_SIZE, N_DIM), "T3 codebook shape %s" % (cb.shape,)
    assert slot_tags.shape == (K_max, N_DIM), "T3 slot_tags shape %s" % (slot_tags.shape,)
    print("[selftest] T3 PASS: shapes correct")

    # T4: bipolar quantize preserves sign
    v = np.array([0.5, -0.3, 0.0, -1.0, 0.1], dtype=np.float32)
    q = bipolar_quantize(v)
    assert (q == np.array([1.0, -1.0, 1.0, -1.0, 1.0])).all(), "T4 bipolar quant: %s" % q
    print("[selftest] T4 PASS: bipolar_quantize sign correct")

    # T5: arm spec invariants (n_banks * k_per_bank == k_total for all arms)
    for label, n_b, k_pb, k_t in ARM_SPECS:
        assert n_b * k_pb == k_t, "arm %s n_b*k_pb=%d != k_total=%d" % (
            label, n_b * k_pb, k_t)
    print("[selftest] T5 PASS: arm specs consistent")

    # T6: bands locked
    assert HP_CHAIN_GRADE_RECALL == 0.95
    assert MID_LIFT_LO < MID_LIFT_HI
    print("[selftest] T6 PASS: bands locked")

    # T7: substrate-only-decode gate
    assert _LLM_CALL_COUNTER[0] == 0, "T7 LLM counter non-zero"
    print("[selftest] T7 PASS: LLM counter = 0")

    # T8: CODEBOOK_SIZE large enough for stretch arm
    assert CODEBOOK_SIZE >= 1024, "T8 codebook too small for K_total=1024"
    print("[selftest] T8 PASS: CODEBOOK_SIZE=%d >= 1024" % CODEBOOK_SIZE)

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
    print("\n[seed=%d] building codebook + slot tags at N_DIM=%d ..." % (
        seed, N_DIM), flush=True)
    codebook_rng = np.random.default_rng(seed * 1000 + 1)
    slot_rng = np.random.default_rng(seed * 1000 + 2)
    codebook = build_codebook(codebook_rng)
    K_max = max(spec[2] for spec in ARM_SPECS)  # max k_per_bank
    slot_tags = build_slot_tags(slot_rng, K_max)
    print("[seed=%d] codebook %s slot tags %s ready" % (
        seed, codebook.shape, slot_tags.shape), flush=True)
    by_arm = {}
    for arm_idx, (label, n_b, k_pb, k_t) in enumerate(ARM_SPECS):
        t_arm = time.time()
        trial_rng = np.random.default_rng(seed * 1000 + 3 + arm_idx * 100)
        res = eval_arm(label, codebook, slot_tags, trial_rng)
        res["wall_s"] = round(time.time() - t_arm, 2)
        by_arm[label] = res
        print("  [seed=%d arm=%s] recall=%.4f route_acc=%.4f (n_banks=%d "
              "k_per_bank=%d k_total=%d) wall=%.1fs" % (
                  seed, label, res["recall"], res["route_acc"], n_b, k_pb, k_t,
                  res["wall_s"]), flush=True)
    return {
        "seed": seed,
        "by_arm": by_arm,
        "N": N_DIM,
        "CODEBOOK_SIZE": CODEBOOK_SIZE,
        "SIGMA": SIGMA,
        "N_ITEMS_PER_K": N_ITEMS_PER_K,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }


# =============================================================================
# Verdict
# =============================================================================

def _arm_mean(units: List[Dict], label: str, field: str) -> Tuple[float, float, List[float]]:
    vals = [u["by_arm"][label][field] for u in units]
    m = float(np.mean(vals)) if vals else float("nan")
    cv = float(np.std(vals) / max(abs(m), 1e-9)) if len(vals) >= 2 else 0.0
    return m, cv, vals


def compute_verdict(units: List[Dict]) -> Tuple[str, str]:
    if not units:
        return ("HARD_FAIL", "no per-seed data")

    # Per-arm aggregates (Fix #28: per-arm metrics; no summary-only verdicts)
    arm_stats = {}
    for label, _, _, _ in ARM_SPECS:
        m, cv, raw = _arm_mean(units, label, "recall")
        ra_m, ra_cv, ra_raw = _arm_mean(units, label, "route_acc")
        arm_stats[label] = {
            "recall_mean": round(m, 4), "recall_cv": round(cv, 4),
            "recall_per_seed": [round(v, 4) for v in raw],
            "route_acc_mean": round(ra_m, 4), "route_acc_cv": round(ra_cv, 4),
        }

    # Rail check: NAIVE_K128 + NAIVE_K256 must reproduce Cell D today
    naive_k32 = arm_stats["ARM_NAIVE_SINGLE_BANK_K32"]["recall_mean"]
    naive_k128 = arm_stats["ARM_NAIVE_SINGLE_BANK_K128"]["recall_mean"]
    naive_k256 = arm_stats["ARM_NAIVE_SINGLE_BANK_K256"]["recall_mean"]
    rail_k32_ok = naive_k32 >= RAIL_NAIVE_K32_MIN
    rail_k128_ok = RAIL_NAIVE_K128_LO <= naive_k128 <= RAIL_NAIVE_K128_HI
    rail_k256_ok = RAIL_NAIVE_K256_LO <= naive_k256 <= RAIL_NAIVE_K256_HI
    rails_breached = []
    if not rail_k32_ok:
        rails_breached.append("K32=%.4f<%.2f" % (naive_k32, RAIL_NAIVE_K32_MIN))
    if not rail_k128_ok:
        rails_breached.append("K128=%.4f not in [%.2f,%.2f]" % (
            naive_k128, RAIL_NAIVE_K128_LO, RAIL_NAIVE_K128_HI))
    if not rail_k256_ok:
        rails_breached.append("K256=%.4f not in [%.2f,%.2f]" % (
            naive_k256, RAIL_NAIVE_K256_LO, RAIL_NAIVE_K256_HI))

    # MULTI_BANK_K256 candidates
    multi_k256_labels = [
        "ARM_MULTI_BANK_8x32_K256", "ARM_MULTI_BANK_4x64_K256",
        "ARM_MULTI_BANK_2x128_K256", "ARM_MULTI_BANK_16x16_K256",
    ]
    multi_k256_recalls = [(L, arm_stats[L]["recall_mean"],
                            arm_stats[L]["recall_cv"],
                            arm_stats[L]["route_acc_mean"])
                           for L in multi_k256_labels]
    best_multi = max(multi_k256_recalls, key=lambda x: x[1])
    best_label, best_recall, best_cv, best_route = best_multi
    lift_over_naive = best_recall - naive_k256

    # K1024 stretch
    bonus_k1024 = arm_stats["ARM_MULTI_BANK_32x32_K1024"]
    k1024_recall = bonus_k1024["recall_mean"]
    k1024_cv = bonus_k1024["recall_cv"]
    k1024_route = bonus_k1024["route_acc_mean"]

    # Q-discipline saturation
    suspect_sat = (best_recall >= Q_SUSPECT_SATURATION) or (k1024_recall >= Q_SUSPECT_SATURATION)
    sat_note = ""
    if suspect_sat:
        sat_note = " [Q-DISCIPLINE: suspect saturation -- recall >= %.3f; UNDER-CLAIM tier]" % Q_SUSPECT_SATURATION

    # Bank-size-degenerate check: how many configs cleared 0.20-lift bar
    n_lift_pass = sum(1 for (_, r, _, _) in multi_k256_recalls if (r - naive_k256) >= HP_PARTIAL_LIFT)

    # Per-arm summary string (Fix #28)
    per_arm_str = "; ".join([
        "%s: recall=%.4f cv=%.4f route_acc=%.4f" % (
            L, arm_stats[L]["recall_mean"], arm_stats[L]["recall_cv"],
            arm_stats[L]["route_acc_mean"])
        for L, _, _, _ in ARM_SPECS
    ])
    summ = ("per-arm: %s | rails: K32=%.4f K128=%.4f K256=%.4f (rails_ok=%s%s) "
            "| best_multi_K256=%s recall=%.4f cv=%.4f route_acc=%.4f "
            "lift_over_naive_K256=%+.4f | K1024_stretch recall=%.4f cv=%.4f "
            "route_acc=%.4f | n_multi_K256_lift_pass=%d/4") % (
                per_arm_str, naive_k32, naive_k128, naive_k256,
                rail_k32_ok and rail_k128_ok and rail_k256_ok,
                (" rails_breached=[" + ",".join(rails_breached) + "]") if rails_breached else "",
                best_label, best_recall, best_cv, best_route, lift_over_naive,
                k1024_recall, k1024_cv, k1024_route, n_lift_pass)

    # RAIL_SANITY_BREACH first (USER MASTER BIAS CHECKLIST 2026-06-24 BIAS-S)
    if rails_breached:
        return ("RAIL_SANITY_BREACH",
                "RAIL_SANITY_BREACH_NAIVE_OUT_OF_CELL_D_BAND: " + summ + sat_note)

    # HARD_FAIL_ROUTER_CROSSTALK: best multi <= naive at K=256
    if best_recall <= naive_k256:
        return ("HARD_FAIL",
                "HARD_FAIL_ROUTER_CROSSTALK: best multi_bank K_total=256 recall %.4f "
                "<= NAIVE K=256 recall %.4f -- router selection eats per-bank gain. %s" % (
                    best_recall, naive_k256, summ) + sat_note)

    # HARD_PASS_CHAIN_GRADE first (highest tier)
    chain_grade_pass = (best_recall >= HP_CHAIN_GRADE_RECALL
                         and best_cv <= HP_CHAIN_GRADE_CV
                         and best_route >= HP_CHAIN_GRADE_ROUTE_ACC)

    bonus_k1024_pass = (k1024_recall >= HP_BONUS_K1024_RECALL
                         and k1024_cv <= HP_CHAIN_GRADE_CV
                         and k1024_route >= HP_CHAIN_GRADE_ROUTE_ACC)

    if chain_grade_pass and not suspect_sat:
        # Bank-size-degenerate check: at least 2 configs must hit the partial-lift bar
        # for robustness; else flag as configuration-specific
        degen_note = ""
        if n_lift_pass < 2:
            degen_note = " [BANK_SIZE_ROBUSTNESS_NOTE: only %d/4 multi-bank configs cleared partial-lift bar; possible configuration-specific lift]" % n_lift_pass
        if bonus_k1024_pass:
            return ("HARD_PASS",
                    "HARD_PASS_CHAIN_GRADE_WM_MULTI_BANK_K256_PLUS_BONUS_K1024: "
                    "best_multi (%s) recall=%.4f cv=%.4f route_acc=%.4f passes "
                    "chain-grade band AND stretch K_total=1024 recall=%.4f passes "
                    "(WM K-ceiling 32x lift over single-bank). %s" % (
                        best_label, best_recall, best_cv, best_route,
                        k1024_recall, summ) + degen_note + sat_note)
        return ("HARD_PASS",
                "HARD_PASS_CHAIN_GRADE_WM_MULTI_BANK_K256: best_multi (%s) "
                "recall=%.4f cv=%.4f route_acc=%.4f passes chain-grade band -- "
                "substrate WM K-ceiling extended from 32 (single-bank) to 256 via "
                "multi-bank routing. K1024 stretch: %.4f. %s" % (
                    best_label, best_recall, best_cv, best_route,
                    k1024_recall, summ) + degen_note + sat_note)

    if chain_grade_pass and suspect_sat:
        return ("HARD_PASS",
                "HARD_PASS_CHAIN_GRADE_WM_MULTI_BANK_K256 (UNDER-CLAIMED per Q-discipline): "
                "best_multi (%s) recall=%.4f passes but suspect saturation; "
                "tier as MEASURED_MECHANISM by cert-owner unless mechanism story. %s" % (
                    best_label, best_recall, summ) + sat_note)

    # HARD_PASS_PARTIAL_LIFT
    if lift_over_naive >= HP_PARTIAL_LIFT:
        return ("HARD_PASS",
                "HARD_PASS_PARTIAL_MULTI_BANK_LIFT: best_multi (%s) recall=%.4f "
                "(lift=%+.4f over NAIVE K=256) passes >=%.2f partial-lift band but "
                "below absolute %.2f chain-grade floor. %s" % (
                    best_label, best_recall, lift_over_naive,
                    HP_PARTIAL_LIFT, HP_CHAIN_GRADE_RECALL, summ) + sat_note)

    # MIDDLE_BAND
    if MID_LIFT_LO <= lift_over_naive < MID_LIFT_HI:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_MULTI_BANK_MARGINAL: best_multi (%s) recall=%.4f "
                "lift=%+.4f over NAIVE K=256 is in marginal [%.2f, %.2f] band. %s" % (
                    best_label, best_recall, lift_over_naive,
                    MID_LIFT_LO, MID_LIFT_HI, summ) + sat_note)

    # Below middle band -> HARD_FAIL_BANK_SIZE_DEGENERATE or generic HARD_FAIL
    if n_lift_pass == 1:
        return ("HARD_FAIL",
                "HARD_FAIL_BANK_SIZE_DEGENERATE: only 1 multi-bank configuration "
                "cleared partial-lift bar (=%s) -- mechanism not robust across "
                "bank-size choices. %s" % (best_label, summ) + sat_note)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND_UNCLASSIFIED: best_multi (%s) recall=%.4f lift=%+.4f "
            "below MIDDLE_BAND floor %.2f. %s" % (
                best_label, best_recall, lift_over_naive, MID_LIFT_LO, summ) + sat_note)


# =============================================================================
# atexit synthesizer (recovery if subprocess killed mid-run)
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
    print("[config] anchor=%s mode=%s seeds=%s N=%d sigma=%.1f | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, SIGMA, CONFIG_VERSION), flush=True)
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
            "Corrected Cell Y (USER 2026-06-25). Original FM lock-in v1 "
            "HARD_FAILED with intermod bleed (K128=0.180; K256=0.453) -- 4th "
            "cell-evidence point that FDM stacking on shared W produces "
            "crosstalk. Corrected substrate analog: MULTI-WM-BANK routing. "
            "N_BANKS separate W matrices each within per-bank K-ceiling=64 "
            "(Cell D today). Router (analog to Cell 1 partition routing "
            "chain-grade @ M=1M today) picks bank from slot. Brain analog: "
            "PFC multi-microcircuit WM with attention routing. Strategic: "
            "extends WM K from 32 (single-bank chain-grade) to 256 "
            "(8x32 multi-bank) at substrate-native -- same architectural "
            "decomposition pattern as KG. Stretch arm 32x32_K1024 tests "
            "32x K-ceiling extension."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
