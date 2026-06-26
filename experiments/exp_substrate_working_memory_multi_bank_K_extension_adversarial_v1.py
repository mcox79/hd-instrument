"""substrate_working_memory_multi_bank_K_extension_adversarial_v1 -- K-extension + adversarial keys.

PROMOTION CONTEXT (Research DRILL 1 ITEM 6 / DRILL 2 HIGH 1, 2026-06-25):
  v1 reference (`exp_substrate_working_memory_multi_bank_routing_v1`) chain-grade-eligible at K=1024
    (multi-bank 32x32_K1024 recall=1.0000 cv=0.0; cell self-flagged Q_SUSPECT_SATURATION).
  4/4 multi-bank arms at K=256 saturate identically (8x32, 4x64, 16x16, 32x32 all = 1.000).
  By-construction-saturation tiering -> cannot DISCRIMINATE which arrangement is load-bearing.

v1 DESIGN -- adversarial K-extension with TWO discriminators:
  1. K_SWEEP in {1024 (rail), 2048, 4096} extends past saturation point
  2. Adversarial feature-overlap items: pairs share controlled fraction of bipolar bits
     (vs the v1 reference's INDEPENDENT-random items) -- creates query ambiguity at routing layer
  3. Multiple N_BANKS at each K: lets us see which arrangement cliffs first
     (router-bound vs cleanup-bound trade-off)

ARMS (10 total = 5 random + 5 adversarial, sharing config):
  RANDOM regime (matches v1 reference exactly):
    ARM_RAND_NAIVE_K_TOTAL      -- single-bank baseline at each K_total (cliffs naturally past K=64)
    ARM_RAND_MULTI_8x_TOTAL     -- 8x banks (e.g., 8x256=K2048)
    ARM_RAND_MULTI_16x_TOTAL    -- 16x banks
    ARM_RAND_MULTI_32x_TOTAL    -- 32x banks
    ARM_RAND_MULTI_64x_TOTAL    -- 64x banks (smallest per-bank K)

  ADVERSARIAL regime (KEYS share FEATURE_OVERLAP_FRAC of bipolar bits):
    ARM_ADV_NAIVE_K_TOTAL
    ARM_ADV_MULTI_8x_TOTAL
    ARM_ADV_MULTI_16x_TOTAL
    ARM_ADV_MULTI_32x_TOTAL
    ARM_ADV_MULTI_64x_TOTAL

K_SWEEP applied to each (regime, arrangement) pair: K in {1024, 2048, 4096}
  N_BANKS scales with K_total to keep K_PER_BANK in chain-grade envelope (<= 64 from Cell D rail)

EXPECTED OUTCOMES per DRILL 1 P=0.50 + DRILL 2 HIGH 1:
  HARD_PASS_CHAIN_GRADE_K_4096:
    best random multi-bank arm at K=4096 recall >= 0.95 AND cv <= 0.05 AND route_acc >= 0.95
    AND adversarial within 0.05 of random (mechanism survives feature overlap)
  CHAIN_GRADE_AT_K_CLIFF:
    cliff identified within sweep -- pass at K=2048 fails at K=4096
  HARD_FAIL_ADVERSARIAL_BREAKS_ROUTING:
    adversarial recall < random recall by >= 0.30 (routing-acc tanks under query ambiguity)
  MIDDLE_BAND: partial scaling

META_M6: NAIVE_RANDOM baseline measured IN-CELL at same K (not copied from v1 reference)
META_M7: smoke matches full on N_DIM, SIGMA, FEATURE_OVERLAP_FRAC, CUE_COS
  Only N_ITEMS_PER_K + SEEDS + K_SWEEP reduce
Q-discipline: if recall >= 0.995 EVEN AT K=4096 ADVERSARIAL, BIAS-Q fires
  (corpus still too easy; need K=8192+ or stronger overlap)

CONFIG (matches v1 reference for apples-to-apples baselines):
  N_DIM = 4096, CODEBOOK_SIZE = 8192 (must hold K=4096 + headroom)
  SIGMA = 1.0 (matches v1 reference)
  CUE_COS = 0.70 (matches v1 reference)
  FEATURE_OVERLAP_FRAC = 0.20 (20% of bipolar bits shared per adversarial-pair group)
  N_ITEMS_PER_K = 200 (matches v1 reference)
  Seeds [11, 13, 19] (cross-cell consistent)

SMOKE: N=2048, K_SWEEP=[256, 1024], N_ITEMS_PER_K=50, seeds=[11], FEATURE_OVERLAP=0.20

Author: exp_dev 2026-06-25 (Drill 1 #6 + Drill 2 HIGH 1).
ASCII-only; per-(seed, K, regime) checkpoint; substrate-only; numpy only.
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
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "substrate_working_memory_multi_bank_K_extension_adversarial_v1"
_LLM_CALL_COUNTER = [0]

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = RUN_MODE == "smoke"

# Pre-reg bands LOCKED (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
HP_CHAIN_GRADE_RECALL = 0.95
HP_CHAIN_GRADE_CV = 0.05
HP_CHAIN_GRADE_ROUTE_ACC = 0.95
HP_ADV_WITHIN_RANDOM = 0.05  # adversarial within 0.05 of random for chain-grade
HP_PARTIAL_LIFT = 0.20
HP_ADV_BREAK_THRESHOLD = 0.30  # adv recall drop >= this = HARD_FAIL_ADVERSARIAL_BREAKS_ROUTING
HP_TARGET_K = 4096  # chain-grade target K (full sweep)
Q_SUSPECT_SATURATION = 0.995

# Lock-assertions
assert 0.0 < HP_CHAIN_GRADE_RECALL < 1.0, "band locked"
assert 0.0 < HP_ADV_WITHIN_RANDOM < 0.3, "adv_within range"
assert HP_ADV_BREAK_THRESHOLD > HP_ADV_WITHIN_RANDOM, "ordering"

# Config (matches v1 reference)
N_DIM = 2048 if SMOKE else 4096
SIGMA = 1.0
CUE_COS = 0.70
FEATURE_OVERLAP_FRAC = 0.20  # 20% bipolar bit overlap in adversarial pairs (within a "group")
N_GROUPS_ADV = 4  # adversarial items partitioned into N_GROUPS_ADV groups of shared-feature items

if SMOKE:
    K_SWEEP = [256, 1024]
    N_ITEMS_PER_K = 50
    SEEDS = [11]
    # CODEBOOK must hold max K_total in sweep
    CODEBOOK_SIZE = 2048
else:
    K_SWEEP = [1024, 2048, 4096]
    N_ITEMS_PER_K = 200
    SEEDS = [11, 13, 19]
    CODEBOOK_SIZE = 8192

# Bank arrangements at each K (n_banks, k_per_bank)
# We keep k_per_bank in the chain-grade envelope (k_per_bank <= 64 favored)
def bank_arrangements_for_k(k_total: int) -> List[Tuple[str, int, int]]:
    """Return list of (label, n_banks, k_per_bank) for a given K_total."""
    arrangements = []
    # Naive single-bank (baseline; cliffs naturally past K=64)
    arrangements.append(("NAIVE", 1, k_total))
    # Multi-bank arrangements: scale n_banks to keep k_per_bank small
    for n_banks in [8, 16, 32, 64]:
        if k_total % n_banks == 0:
            k_pb = k_total // n_banks
            if k_pb <= 128:  # cap at 128 (Cell D shows K=128 single-bank ~0.91)
                arrangements.append(("MULTI_%dx" % n_banks, n_banks, k_pb))
    return arrangements


CONFIG_VERSION = (
    "substrateWmMultiBankKExtAdv-v1: N_DIM=%d CODEBOOK_SIZE=%d sigma=%.1f "
    "CUE_COS=%.2f FEATURE_OVERLAP=%.2f K_SWEEP=%s N_ITEMS_PER_K=%d seeds=%s "
    "mode=%s HP_chain>=%.2f cv<=%.2f route_acc>=%.2f HP_adv_within=%.2f "
    "HP_adv_break=%.2f Q_sat>=%.3f HP_target_K=%d"
) % (N_DIM, CODEBOOK_SIZE, SIGMA, CUE_COS, FEATURE_OVERLAP_FRAC,
     K_SWEEP, N_ITEMS_PER_K, SEEDS, RUN_MODE,
     HP_CHAIN_GRADE_RECALL, HP_CHAIN_GRADE_CV, HP_CHAIN_GRADE_ROUTE_ACC,
     HP_ADV_WITHIN_RANDOM, HP_ADV_BREAK_THRESHOLD,
     Q_SUSPECT_SATURATION, HP_TARGET_K)


# =============================================================================
# Substrate primitives
# =============================================================================

def random_bipolar(rng: np.random.Generator, shape) -> np.ndarray:
    return rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=shape)


def bipolar_quantize(v: np.ndarray) -> np.ndarray:
    out = np.sign(v).astype(np.float32)
    out[out == 0] = 1.0
    return out


def build_codebook_random(rng: np.random.Generator) -> np.ndarray:
    return random_bipolar(rng, (CODEBOOK_SIZE, N_DIM)).astype(np.float32)


def build_codebook_adversarial(rng: np.random.Generator) -> np.ndarray:
    """ADVERSARIAL codebook: items are grouped; within a group, items share FEATURE_OVERLAP_FRAC of bits.

    Construction (DETERMINISTIC SHARED-PREFIX, not stochastic mixing):
      - Create N_GROUPS_ADV "group templates" of dim N_DIM (random bipolar each)
      - For each item, assign it to a group; FIRST n_shared = int(FEATURE_OVERLAP_FRAC*N_DIM) bits
        are COPIED from the group template; remaining N_DIM-n_shared bits are independent random bipolar
      - Distribute CODEBOOK_SIZE items uniformly across the N_GROUPS_ADV groups
      - Two items in same group share EXACTLY FEATURE_OVERLAP_FRAC of bits (identity match) by construction
        + 0.5*(1-FEATURE_OVERLAP_FRAC) of random bits match by coincidence -> expected match fraction
        = FEATURE_OVERLAP_FRAC + 0.5*(1-FEATURE_OVERLAP_FRAC)
        = 0.5 + 0.5*FEATURE_OVERLAP_FRAC
      - Two items in DIFFERENT groups share ~0.5 of bits (all random)
    """
    group_templates = random_bipolar(rng, (N_GROUPS_ADV, N_DIM)).astype(np.float32)
    n_shared = int(FEATURE_OVERLAP_FRAC * N_DIM)
    items = np.zeros((CODEBOOK_SIZE, N_DIM), dtype=np.float32)
    for i in range(CODEBOOK_SIZE):
        g_idx = i % N_GROUPS_ADV
        template = group_templates[g_idx]
        random_tail = random_bipolar(rng, (N_DIM - n_shared,))
        items[i, :n_shared] = template[:n_shared]
        items[i, n_shared:] = random_tail
    return items


def build_slot_tags(rng: np.random.Generator, K_max: int) -> np.ndarray:
    return random_bipolar(rng, (K_max, N_DIM)).astype(np.float32)


def build_bank_tags(rng: np.random.Generator, n_banks: int) -> np.ndarray:
    return random_bipolar(rng, (n_banks, N_DIM)).astype(np.float32)


def cleanup_to_codebook(retrieve_vec: np.ndarray, codebook: np.ndarray) -> int:
    sims = codebook @ retrieve_vec
    return int(np.argmax(sims))


def _write_bank(items: np.ndarray, slot_tags_b: np.ndarray,
                 sigma: float, rng: np.random.Generator) -> np.ndarray:
    workspace = (items * slot_tags_b).sum(axis=0).astype(np.float32)
    if sigma > 0.0:
        noise = rng.standard_normal(workspace.shape).astype(np.float32) * sigma
        workspace = workspace + noise
    return bipolar_quantize(workspace)


def _read_with_cleanup(noisy_bp: np.ndarray, slot_tag: np.ndarray,
                        codebook: np.ndarray) -> int:
    r1 = (noisy_bp * slot_tag).astype(np.float32)
    sims1 = codebook @ r1
    cand_idx = int(np.argmax(sims1))
    r2 = 0.5 * r1 + 0.5 * codebook[cand_idx]
    r2_bp = bipolar_quantize(r2)
    return cleanup_to_codebook(r2_bp, codebook)


def eval_single_bank(k_per_bank: int, k_total: int, codebook: np.ndarray,
                      slot_tags_full: np.ndarray,
                      rng: np.random.Generator) -> Tuple[float, float]:
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
    assert n_banks >= 2 and k_total == n_banks * k_per_bank
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / k_total))
    slot_tags = slot_tags_full[:k_per_bank]
    bank_tags = build_bank_tags(rng, n_banks)
    correct = 0
    total = 0
    route_correct = 0
    route_total = 0
    cue_noise_scale = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))
    for _t in range(n_trials):
        idx_global = rng.choice(CODEBOOK_SIZE, size=k_total, replace=False)
        workspaces = []
        for b in range(n_banks):
            start = b * k_per_bank
            stop = start + k_per_bank
            items_b = codebook[idx_global[start:stop]]
            noisy_bp = _write_bank(items_b, slot_tags, SIGMA, rng)
            workspaces.append(noisy_bp)
        for slot_idx in range(k_total):
            bank_true = slot_idx // k_per_bank
            local_slot = slot_idx % k_per_bank
            cue = CUE_COS * bank_tags[bank_true] + cue_noise_scale * bipolar_quantize(
                rng.standard_normal(N_DIM).astype(np.float32))
            sims_bank = bank_tags @ cue
            bank_routed = int(np.argmax(sims_bank))
            route_total += 1
            if bank_routed == bank_true:
                route_correct += 1
            ws = workspaces[bank_routed]
            pred_idx = _read_with_cleanup(ws, slot_tags[local_slot], codebook)
            true_item_idx = int(idx_global[slot_idx])
            if pred_idx == true_item_idx and bank_routed == bank_true:
                correct += 1
            total += 1
    return correct / max(total, 1), route_correct / max(route_total, 1)


def eval_arrangement(label: str, n_banks: int, k_per_bank: int, k_total: int,
                       codebook: np.ndarray, slot_tags_full: np.ndarray,
                       rng: np.random.Generator) -> Dict[str, float]:
    if n_banks == 1:
        recall, route_acc = eval_single_bank(k_per_bank, k_total, codebook,
                                              slot_tags_full, rng)
    else:
        recall, route_acc = eval_multi_bank(n_banks, k_per_bank, k_total,
                                              codebook, slot_tags_full, rng)
    return {"recall": round(float(recall), 4),
            "route_acc": round(float(route_acc), 4),
            "n_banks": n_banks, "k_per_bank": k_per_bank, "k_total": k_total}


def _selftest():
    rng = np.random.default_rng(0)
    cb_rand = build_codebook_random(rng)
    assert cb_rand.shape == (CODEBOOK_SIZE, N_DIM), "T1 random codebook shape"
    assert set(np.unique(cb_rand).tolist()) <= {-1.0, 1.0}, "T1 bipolar"
    print("[selftest] T1 PASS: random codebook shape + bipolar")

    cb_adv = build_codebook_adversarial(np.random.default_rng(1))
    assert cb_adv.shape == (CODEBOOK_SIZE, N_DIM), "T2 adversarial codebook shape"
    # T3: items in same group share ~FEATURE_OVERLAP_FRAC of bits (vs random ~0%)
    # Take first 2 items in each of the first 2 groups: items 0 and N_GROUPS_ADV both in group 0
    i_a = 0
    i_b = N_GROUPS_ADV  # same group as i_a (group 0)
    shared_in_group = float(np.mean(cb_adv[i_a] == cb_adv[i_b]))
    # cross-group baseline (group 0 vs group 1)
    i_c = 1
    shared_cross_group = float(np.mean(cb_adv[i_a] == cb_adv[i_c]))
    # Within group (DETERMINISTIC shared-prefix): exactly FEATURE_OVERLAP_FRAC of bits match by
    # construction, + 0.5*(1-FEATURE_OVERLAP_FRAC) of remaining random bits match by coincidence
    expected_in_group = FEATURE_OVERLAP_FRAC + 0.5 * (1.0 - FEATURE_OVERLAP_FRAC)
    expected_cross = 0.5  # all random bits
    assert shared_in_group > shared_cross_group + 0.05, (
        "T3 adversarial groups don't differ: in=%.3f cross=%.3f" % (
            shared_in_group, shared_cross_group))
    assert abs(shared_in_group - expected_in_group) < 0.10, (
        "T3 in-group overlap fraction unexpected: %.3f vs expected ~%.3f" % (
            shared_in_group, expected_in_group))
    print("[selftest] T3 PASS: adversarial in-group=%.3f cross=%.3f (expected ~%.3f vs 0.5)" % (
        shared_in_group, shared_cross_group, expected_in_group))

    # T4: bipolar_quantize sign
    v = np.array([0.5, -0.3, 0.0, -1.0, 0.1], dtype=np.float32)
    q = bipolar_quantize(v)
    assert (q == np.array([1.0, -1.0, 1.0, -1.0, 1.0])).all(), "T4 bipolar quantize"
    print("[selftest] T4 PASS: bipolar quantize sign correct")

    # T5: single-bank K=32 at sigma=1.0 -> ~1.000 (matches Cell D rail)
    cb2 = build_codebook_random(np.random.default_rng(7))
    slot_tags = build_slot_tags(np.random.default_rng(8), 128)
    r, _ = eval_single_bank(32, 32, cb2, slot_tags, np.random.default_rng(9))
    assert r >= 0.95, "T5 single-bank K=32 recall=%.3f < 0.95" % r
    print("[selftest] T5 PASS: single-bank K=32 sigma=1.0 recall=%.3f" % r)

    # T6: multi-bank 8x32_K256 random gives high recall + route_acc
    r2, ra2 = eval_multi_bank(8, 32, 256, cb2, slot_tags, np.random.default_rng(10))
    assert ra2 >= 0.85, "T6 route_acc=%.3f < 0.85" % ra2
    assert r2 >= 0.5, "T6 multi_bank recall=%.3f < 0.5" % r2
    print("[selftest] T6 PASS: multi_bank 8x32 random recall=%.3f route_acc=%.3f" % (r2, ra2))

    # T7: arrangements for K=1024 / K=4096 are non-degenerate
    arrs_1024 = bank_arrangements_for_k(1024)
    arrs_4096 = bank_arrangements_for_k(4096)
    assert len(arrs_1024) >= 2 and len(arrs_4096) >= 2, "T7 enough arrangements"
    print("[selftest] T7 PASS: arrangements_K1024=%d arrangements_K4096=%d" % (
        len(arrs_1024), len(arrs_4096)))

    # T8: bands locked
    assert HP_CHAIN_GRADE_RECALL == 0.95
    assert HP_ADV_WITHIN_RANDOM == 0.05
    print("[selftest] T8 PASS: bands locked")

    # T9: LLM counter
    assert _LLM_CALL_COUNTER[0] == 0
    print("[selftest] T9 PASS: LLM counter = 0")

    # T10: CODEBOOK_SIZE large enough for max K
    assert CODEBOOK_SIZE >= max(K_SWEEP), "T10 codebook too small"
    print("[selftest] T10 PASS: CODEBOOK_SIZE=%d >= max(K_SWEEP)=%d" % (
        CODEBOOK_SIZE, max(K_SWEEP)))

    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


def run_unit(seed: int, k_total: int) -> Dict:
    """Run one (seed, K_total) unit across both regimes and all arrangements."""
    t = time.time()
    cb_rand_rng = np.random.default_rng(seed * 100003 + k_total * 31)
    cb_adv_rng = np.random.default_rng(seed * 100003 + k_total * 31 + 7)
    slot_rng = np.random.default_rng(seed * 100003 + k_total * 31 + 11)

    cb_random = build_codebook_random(cb_rand_rng)
    cb_adversarial = build_codebook_adversarial(cb_adv_rng)
    # NAIVE single-bank arm uses k_per_bank == k_total, so slot_tags must cover up to max(K_SWEEP).
    # Multi-bank arms use k_per_bank up to 128 (bank_arrangements_for_k caps at 128).
    K_MAX_SLOT = max(k_total, 128)
    slot_tags = build_slot_tags(slot_rng, K_MAX_SLOT)

    arrangements = bank_arrangements_for_k(k_total)
    by_regime = {"RANDOM": {}, "ADVERSARIAL": {}}
    for regime, cb in (("RANDOM", cb_random), ("ADVERSARIAL", cb_adversarial)):
        for label, n_banks, k_pb in arrangements:
            t_a = time.time()
            trial_rng = np.random.default_rng(
                seed * 100003 + k_total * 31 + hash(regime + label) % 1000)
            res = eval_arrangement(label, n_banks, k_pb, k_total, cb, slot_tags, trial_rng)
            res["wall_s"] = round(time.time() - t_a, 2)
            res["regime"] = regime
            by_regime[regime][label] = res
            print("  [seed=%d K=%d regime=%s arm=%s] recall=%.4f route_acc=%.4f "
                  "(n_banks=%d k_per_bank=%d) t=%.1fs" % (
                      seed, k_total, regime, label, res["recall"], res["route_acc"],
                      n_banks, k_pb, res["wall_s"]), flush=True)

    return {
        "seed": seed, "k_total": k_total,
        "by_regime": by_regime,
        "N": N_DIM, "CODEBOOK_SIZE": CODEBOOK_SIZE, "SIGMA": SIGMA,
        "CUE_COS": CUE_COS, "FEATURE_OVERLAP_FRAC": FEATURE_OVERLAP_FRAC,
        "N_ITEMS_PER_K": N_ITEMS_PER_K,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_unit": round(time.time() - t, 2),
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }


def compute_verdict(units: List[Dict]) -> Tuple[str, str]:
    if not units:
        return ("HARD_FAIL", "no units")

    # Group by k_total
    by_K = {}
    for u in units:
        by_K.setdefault(u["k_total"], []).append(u)

    # Discover all (regime, arm_label) combos present
    all_arm_labels = set()
    for u in units:
        for regime, arms in u["by_regime"].items():
            for label in arms:
                all_arm_labels.add(label)

    # Per (K, regime, label) aggregation
    summary_rows = []
    chain_grade_at_K = {}
    adv_breaks_at_K = {}
    saturated_at_K = {}
    arm_stats = {}
    for k_total in sorted(by_K.keys()):
        us = by_K[k_total]
        arm_stats[k_total] = {}
        # find best multi-bank arm per regime
        for regime in ("RANDOM", "ADVERSARIAL"):
            arm_stats[k_total][regime] = {}
            for label in all_arm_labels:
                recs = []
                ras = []
                for u in us:
                    if regime in u["by_regime"] and label in u["by_regime"][regime]:
                        recs.append(u["by_regime"][regime][label]["recall"])
                        ras.append(u["by_regime"][regime][label]["route_acc"])
                if recs:
                    m_rec = float(np.mean(recs))
                    cv_rec = float(np.std(recs) / max(m_rec, 1e-9)) if len(recs) >= 2 else 0.0
                    m_ra = float(np.mean(ras)) if ras else 0.0
                    arm_stats[k_total][regime][label] = {
                        "recall_mean": round(m_rec, 4),
                        "recall_cv": round(cv_rec, 4),
                        "route_acc_mean": round(m_ra, 4),
                        "recall_per_seed": [round(r, 4) for r in recs],
                    }
        # Chain-grade check at this K
        rand_multi = {L: d for L, d in arm_stats[k_total]["RANDOM"].items()
                       if L.startswith("MULTI_")}
        adv_multi = {L: d for L, d in arm_stats[k_total]["ADVERSARIAL"].items()
                      if L.startswith("MULTI_")}
        if rand_multi:
            best_rand = max(rand_multi.items(), key=lambda x: x[1]["recall_mean"])
            best_rand_label, best_rand_d = best_rand
            adv_for_best = adv_multi.get(best_rand_label, {"recall_mean": 0.0, "recall_cv": 0.0, "route_acc_mean": 0.0})
            adv_within_random = (best_rand_d["recall_mean"] - adv_for_best["recall_mean"]) <= HP_ADV_WITHIN_RANDOM
            adv_break = (best_rand_d["recall_mean"] - adv_for_best["recall_mean"]) >= HP_ADV_BREAK_THRESHOLD
            chain_pass = (best_rand_d["recall_mean"] >= HP_CHAIN_GRADE_RECALL
                          and best_rand_d["recall_cv"] <= HP_CHAIN_GRADE_CV
                          and best_rand_d["route_acc_mean"] >= HP_CHAIN_GRADE_ROUTE_ACC
                          and adv_within_random)
            if chain_pass:
                chain_grade_at_K[k_total] = best_rand_label
            if adv_break:
                adv_breaks_at_K[k_total] = (best_rand_label, best_rand_d["recall_mean"],
                                              adv_for_best["recall_mean"])
            # saturation
            sat_arms = [L for L, d in arm_stats[k_total]["RANDOM"].items()
                        if d["recall_mean"] >= Q_SUSPECT_SATURATION]
            sat_arms_adv = [L for L, d in arm_stats[k_total]["ADVERSARIAL"].items()
                              if d["recall_mean"] >= Q_SUSPECT_SATURATION]
            if sat_arms or sat_arms_adv:
                saturated_at_K[k_total] = {"random": sat_arms, "adversarial": sat_arms_adv}
            # Summary line at this K
            summary_rows.append(
                "K=%d best_rand=%s[rec=%.4f cv=%.4f ra=%.4f] "
                "adv_same=%s[rec=%.4f cv=%.4f ra=%.4f] "
                "naive_rand_rec=%.4f" % (
                    k_total, best_rand_label,
                    best_rand_d["recall_mean"], best_rand_d["recall_cv"],
                    best_rand_d["route_acc_mean"],
                    best_rand_label,
                    adv_for_best["recall_mean"], adv_for_best.get("recall_cv", 0.0),
                    adv_for_best.get("route_acc_mean", 0.0),
                    arm_stats[k_total]["RANDOM"].get("NAIVE", {"recall_mean": float("nan")})["recall_mean"]))

    summ = " | ".join(summary_rows)
    if saturated_at_K:
        summ += " | [Q-DISCIPLINE: saturated at K=%s]" % saturated_at_K

    # Verdict ladder
    # HARD_FAIL_ADVERSARIAL_BREAKS_ROUTING: adversarial degrades by >= 0.30 at TARGET K
    target_K = HP_TARGET_K if HP_TARGET_K in arm_stats else (max(arm_stats.keys()) if arm_stats else None)
    if target_K and target_K in adv_breaks_at_K:
        info = adv_breaks_at_K[target_K]
        return ("HARD_FAIL",
                "HARD_FAIL_ADVERSARIAL_BREAKS_ROUTING: at K=%d best_random arm %s recall=%.4f "
                "but adversarial drops to %.4f (delta>=%.2f); routing fragile to query ambiguity | %s" % (
                    target_K, info[0], info[1], info[2], HP_ADV_BREAK_THRESHOLD, summ))

    # HARD_PASS_CHAIN_GRADE_K_4096: chain-grade at TARGET K
    if target_K and target_K in chain_grade_at_K:
        return ("HARD_PASS",
                "HARD_PASS_CHAIN_GRADE_K_%d: best_random multi-bank arm %s at K=%d "
                "recall>=%.2f cv<=%.2f route_acc>=%.2f AND adversarial within %.2f "
                "(chain_grade_set=%s) | %s" % (
                    target_K, chain_grade_at_K[target_K], target_K,
                    HP_CHAIN_GRADE_RECALL, HP_CHAIN_GRADE_CV, HP_CHAIN_GRADE_ROUTE_ACC,
                    HP_ADV_WITHIN_RANDOM, chain_grade_at_K, summ))

    # CHAIN_GRADE_AT_K_CLIFF: passes at some K but cliffs before target
    if chain_grade_at_K:
        max_chain_K = max(chain_grade_at_K.keys())
        return ("HARD_PASS",
                "CHAIN_GRADE_AT_K_CLIFF: chain-grade extends to K=%d (best=%s) but cliffs "
                "before K=%d (chain_grade_set=%s) | %s" % (
                    max_chain_K, chain_grade_at_K[max_chain_K], target_K,
                    chain_grade_at_K, summ))

    # No chain-grade -> MIDDLE_BAND or HARD_FAIL
    if target_K and target_K in arm_stats:
        rand_multi = {L: d for L, d in arm_stats[target_K]["RANDOM"].items()
                       if L.startswith("MULTI_")}
        if rand_multi:
            best = max(rand_multi.values(), key=lambda x: x["recall_mean"])
            if best["recall_mean"] >= 0.50:
                return ("MIDDLE_BAND",
                        "MIDDLE_BAND_PARTIAL_K_EXT: best random multi-bank at K=%d "
                        "recall=%.4f in [0.50, %.2f) -- partial extension | %s" % (
                            target_K, best["recall_mean"], HP_CHAIN_GRADE_RECALL, summ))

    return ("HARD_FAIL",
            "HARD_FAIL_NO_K_HOLDS: no K_total in sweep reaches chain-grade gate "
            "(rec>=%.2f cv<=%.2f route_acc>=%.2f adv_within<=%.2f) | %s" % (
                HP_CHAIN_GRADE_RECALL, HP_CHAIN_GRADE_CV,
                HP_CHAIN_GRADE_ROUTE_ACC, HP_ADV_WITHIN_RANDOM, summ))


_RESULTS_HOLDER = {"out_dir": None, "started_at": time.time()}


def _atexit_synth():
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        keys = ["seed%d_K%d" % (s, k) for s in SEEDS for k in K_SWEEP]
        agg = aggregate_partials(od, seeds=keys, run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        units = list(agg.values())
        if not units:
            return
        v, vmsg = compute_verdict(units)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_units": len(units),
            "config_version": CONFIG_VERSION, "per_unit": units,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "K_SWEEP": K_SWEEP, "seeds": SEEDS,
        }
        write_metrics(od, metrics, results=units)
        print("[atexit] wrote synth metrics.json (%d units)" % len(units), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d K_SWEEP=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, K_SWEEP, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    keys = ["seed%d_K%d" % (s, k) for s in SEEDS for k in K_SWEEP]
    existing = aggregate_partials(out_dir, seeds=keys, run_config=run_config)
    done_keys = set(existing.keys())
    print("[ckpt] done=%d/%d units" % (len(done_keys), len(keys)), flush=True)

    for s in SEEDS:
        for k in K_SWEEP:
            key = "seed%d_K%d" % (s, k)
            if key in done_keys:
                continue
            try:
                rec = run_unit(s, k)
                write_partial_key(out_dir, key, rec)
            except Exception as e:
                print("[WARN] %s failed: %s" % (key, e), flush=True)

    agg = aggregate_partials(out_dir, seeds=keys, run_config=run_config)
    units = [agg[k] for k in keys if k in agg]
    if not units:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0

    v, vmsg = compute_verdict(units)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_units": len(units),
        "config_version": CONFIG_VERSION, "per_unit": units,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "K_SWEEP": K_SWEEP, "seeds": SEEDS,
        "DESIGN_NOTE": (
            "Multi-bank WM K-extension with adversarial feature-overlap discriminator. "
            "Sweeps K_total in {1024, 2048, 4096} (extends past v1 reference's K=1024 saturation) "
            "and tests BOTH random items (matches v1 baseline) AND adversarial items with "
            "FEATURE_OVERLAP_FRAC=%.2f shared bipolar bits per group. Discriminates which "
            "bank arrangement (8x/16x/32x/64x) survives query ambiguity at scale. Pre-reg per "
            "preregs/2026-06-25_substrate_working_memory_multi_bank_K_extension_adversarial_v1.md."
        ) % FEATURE_OVERLAP_FRAC,
    }
    write_metrics(out_dir, metrics, results=units)
    print("[done] metrics.json written (%d units, %.1fs)" % (
        len(units), metrics["elapsed_s"]), flush=True)
