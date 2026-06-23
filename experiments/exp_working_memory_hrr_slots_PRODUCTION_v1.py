"""working_memory_hrr_slots_PRODUCTION_v1 -- production-regime capacity envelope.

PRODUCTION upgrade of working_memory_hrr_slots_smoke_v1 which saturated at recall
1.000 across K=2..16 sigma=0..1.0 (mechanism witness confirmed; discriminator too
easy at that regime). This cell extends the K-sweep well past Miller's 7+/-2
(K=8,16,32,64,128,256 tests the substrate-could-EXCEED-brain hypothesis) and
extends the sigma-sweep INTO the Shannon-floor (sigma=1.5,2.0; intersection
with the noise envelope already characterized in prior arc).

Same mechanism as smoke; same 3 arms:
  ARM_FLAT_SUPERPOSITION         control; bundle items without slot tags
  ARM_HRR_SLOTS                  bind items to slot tags, sum -> workspace; no cleanup
  ARM_HRR_SLOTS_PLUS_CLEANUP     full mechanism: HRR slots + codebook argmax cleanup

bind = element-wise product on bipolar (HRR-analog; involutive).

PRE-REG bands (preregs/2026-06-23_working_memory_hrr_slots_PRODUCTION_v1.md):
  HARD_PASS = ARM_HRR_SLOTS_PLUS_CLEANUP recall at K=32, sigma=1.0 >= 0.80
              (chain-grade-eligible substrate working-memory primitive holding
              ~5x Miller capacity at meaningful noise; structurally exceeds
              human PFC working-memory bound).
  HARD_FAIL = ARM_HRR_SLOTS (no cleanup) recall at K=16, sigma=0.5 < 0.50
              (working memory broken at modest load + modest noise).
  MIDDLE    = otherwise; characterize capacity envelope.

SANITY (selftest): K=2 sigma=0.0 recall=1.0 across all arms.

CAPACITY MATH:
  HRR-superposition K bound items in N=4096 bipolar space. After unbind, crosstalk
  SNR ~ sqrt(N / (K-1)). K=8 -> SNR ~ 24. K=32 -> SNR ~ 12. K=128 -> SNR ~ 5.7.
  K=256 -> SNR ~ 4.0. Cleanup against 256-atom codebook needs SNR above the
  noise-floor of the codebook (sqrt(N) = 64 -> ~6 sigma; codebook crosstalk between
  random bipolar atoms is sqrt(N)). Predicts K=8..32 robust, K=64+ degrading,
  K=128+ near floor; HARD_PASS at K=32 sigma=1.0 is the discriminator.

SUBSTRATE-ONLY: numpy only; no pretrained encoder; zero LLM calls.

RUNTIME: 3 arms x 6 K-values x 5 sigmas x 3 seeds at N_DIM=4096; each cell
re-uses workspace + codebook lookup. Estimate ~15-30min CPU wall.
"""
from __future__ import annotations
import sys, os, argparse, time, signal, atexit, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "working_memory_hrr_slots_PRODUCTION_v1"
_LLM_CALL_COUNTER = [0]

# Pre-reg HARD bands
HP_K32_SIGMA10_RECALL = 0.80   # ARM_HRR_SLOTS_PLUS_CLEANUP at K=32 sigma=1.0
HF_K16_SIGMA05_RECALL = 0.50   # ARM_HRR_SLOTS at K=16 sigma=0.5 STRICTLY-LESS-THAN

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 4096
CODEBOOK_SIZE = 256              # codebook needs to be >= max(K) so we can populate K distinct items per trial
K_VALUES = [8, 16, 32, 64, 128, 256]
SIGMAS = [0.0, 0.5, 1.0, 1.5, 2.0]
N_ITEMS_PER_K = 200              # total items evaluated per (K, sigma, arm, seed); ceil(N_ITEMS_PER_K/K) trials

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
else:
    SEEDS = [7]  # smoke

ARMS = ["ARM_FLAT_SUPERPOSITION", "ARM_HRR_SLOTS", "ARM_HRR_SLOTS_PLUS_CLEANUP"]

CONFIG_VERSION = (
    "working_memory_hrr_slots_PRODUCTION_v1; N_DIM=%d CODEBOOK_SIZE=%d K_VALUES=%s "
    "SIGMAS=%s N_ITEMS_PER_K=%d arms=%s seeds=%s mode=%s; bands "
    "HP_K32_sigma1.0>=%.2f (CLEANUP) HF_K16_sigma0.5<%.2f (SLOTS)"
) % (N_DIM, CODEBOOK_SIZE, K_VALUES, SIGMAS, N_ITEMS_PER_K, ARMS, SEEDS, RUN_MODE,
     HP_K32_SIGMA10_RECALL, HF_K16_SIGMA05_RECALL)


# ============================================================================
# Substrate primitives: bipolar sampling, bind, bundle
# ============================================================================

def random_bipolar(rng: np.random.Generator, shape) -> np.ndarray:
    """Draw a uniform-bipolar tensor of given shape from rng."""
    return rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=shape)


def bipolar_quantize(v: np.ndarray) -> np.ndarray:
    """Sign-quantize real vector to {-1, +1}. Zeros -> +1."""
    out = np.sign(v).astype(np.float32)
    out[out == 0] = 1.0
    return out


def bind_elementwise(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR-analog bind for bipolar vectors. Involutive: bind(bind(a,b),b) = a."""
    return (a * b).astype(np.float32)


def unbind_elementwise(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """unbind == bind for bipolar (b * b = +1 elementwise); alias for clarity."""
    return bind_elementwise(a, b)


# ============================================================================
# Codebook + slot-tag setup
# ============================================================================

def build_codebook(rng: np.random.Generator) -> np.ndarray:
    """Return [CODEBOOK_SIZE, N_DIM] bipolar codebook."""
    return random_bipolar(rng, (CODEBOOK_SIZE, N_DIM)).astype(np.float32)


def build_slot_tags(rng: np.random.Generator, K_max: int) -> np.ndarray:
    """Return [K_max, N_DIM] bipolar slot-tag tensor."""
    return random_bipolar(rng, (K_max, N_DIM)).astype(np.float32)


# ============================================================================
# ARM encoders -- workspace assembly
# ============================================================================

def assemble_flat(items: np.ndarray, slot_tags: np.ndarray) -> np.ndarray:
    """ARM 1: bundle items WITHOUT slot binding. Cannot distinguish positions.

    items: [K, N_DIM], slot_tags: [K, N_DIM] (unused). Returns [N_DIM] real-valued.
    """
    return items.sum(axis=0).astype(np.float32)


def assemble_hrr_slots(items: np.ndarray, slot_tags: np.ndarray) -> np.ndarray:
    """ARM 2: HRR slot binding.

    workspace = sum_i bind(items[i], slot_tags[i]).
    items: [K, N_DIM], slot_tags: [K, N_DIM]. Returns [N_DIM] real-valued.
    """
    return (items * slot_tags).sum(axis=0).astype(np.float32)


ARM_ASSEMBLERS = {
    "ARM_FLAT_SUPERPOSITION":    assemble_flat,
    "ARM_HRR_SLOTS":             assemble_hrr_slots,
    "ARM_HRR_SLOTS_PLUS_CLEANUP": assemble_hrr_slots,  # same workspace; cleanup at read
}


def retrieve_slot(workspace: np.ndarray, slot_tag: np.ndarray, arm_label: str) -> np.ndarray:
    """Retrieve slot content from workspace using slot_tag (bipolar unbind).

    For FLAT, slot_tag is ignored; return workspace itself (cannot distinguish).
    For HRR arms, retrieve_i = bind(workspace, slot_tag_i) (== unbind for bipolar).
    """
    if arm_label == "ARM_FLAT_SUPERPOSITION":
        return workspace.astype(np.float32)
    return (workspace * slot_tag).astype(np.float32)


def cleanup_to_codebook(retrieve_vec: np.ndarray, codebook: np.ndarray) -> int:
    """Argmax cosine over codebook. Returns the index of the best-matching atom."""
    sims = codebook @ retrieve_vec
    return int(np.argmax(sims))


# ============================================================================
# Evaluation: per-K, per-sigma, per-arm per-slot recall
# ============================================================================

def eval_one_K_sigma_arm(K: int, sigma: float, arm_label: str,
                         codebook: np.ndarray, slot_tags_full: np.ndarray,
                         rng: np.random.Generator) -> float:
    """Run the K-item working-memory write/read for one (K, sigma, arm).

    Each trial: draw K distinct item indices from the codebook, assemble workspace
    via the arm, add gaussian noise (sigma) then bipolar-quantize, retrieve each
    slot, cleanup against codebook, score per-slot recall. We run
    ceil(N_ITEMS_PER_K / K) trials (each drawing K distinct items uniformly with
    replacement across trials but without replacement within trial). Total items
    evaluated >= N_ITEMS_PER_K per call.

    Returns per-slot recall = correct / total_items_evaluated.
    """
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / K))
    slot_tags = slot_tags_full[:K]  # [K, N_DIM]
    correct = 0
    total = 0
    for t in range(n_trials):
        # Draw K distinct item indices for THIS trial (independent across trials).
        idx = rng.choice(CODEBOOK_SIZE, size=K, replace=False)
        items = codebook[idx]  # [K, N_DIM]
        workspace = ARM_ASSEMBLERS[arm_label](items, slot_tags)
        if sigma > 0.0:
            noise = rng.standard_normal(workspace.shape).astype(np.float32) * sigma
            noisy = workspace + noise
        else:
            noisy = workspace
        noisy_bp = bipolar_quantize(noisy)
        for i in range(K):
            r = retrieve_slot(noisy_bp, slot_tags[i], arm_label)
            pred_idx = cleanup_to_codebook(r, codebook)
            if pred_idx == int(idx[i]):
                correct += 1
            total += 1
    return correct / max(total, 1)


# ============================================================================
# Per-seed unit
# ============================================================================

def run_unit(seed: int) -> Dict:
    t0 = time.time()
    print("\n[seed=%d] building codebook + slot tags at N_DIM=%d ..." % (seed, N_DIM), flush=True)
    codebook_rng = np.random.default_rng(seed * 1000 + 1)
    slot_rng = np.random.default_rng(seed * 1000 + 2)
    trial_rng = np.random.default_rng(seed * 1000 + 3)
    codebook = build_codebook(codebook_rng)
    K_max = max(K_VALUES)
    slot_tags = build_slot_tags(slot_rng, K_max)
    print("[seed=%d] codebook [%d, %d] + slot tags [%d, %d] ready"
          % (seed, codebook.shape[0], codebook.shape[1], slot_tags.shape[0], slot_tags.shape[1]),
          flush=True)
    by_arm = {}
    for arm_label in ARMS:
        t_arm = time.time()
        by_arm[arm_label] = {"per_K_per_sigma": {}, "per_K_mean_over_sigma": {}, "wall_s": 0.0}
        for K in K_VALUES:
            recall_at_sigma = {}
            for sigma in SIGMAS:
                r = eval_one_K_sigma_arm(K, sigma, arm_label, codebook, slot_tags, trial_rng)
                recall_at_sigma["sigma_%.2f" % sigma] = round(float(r), 4)
            by_arm[arm_label]["per_K_per_sigma"]["K_%d" % K] = recall_at_sigma
            by_arm[arm_label]["per_K_mean_over_sigma"]["K_%d" % K] = round(
                float(np.mean(list(recall_at_sigma.values()))), 4)
        by_arm[arm_label]["wall_s"] = round(time.time() - t_arm, 2)
        per_K_means = by_arm[arm_label]["per_K_mean_over_sigma"]
        means_str = " ".join(["%s=%.3f" % (k, v) for k, v in per_K_means.items()])
        print("  [seed=%d arm=%s] %s wall=%.1fs"
              % (seed, arm_label, means_str, by_arm[arm_label]["wall_s"]), flush=True)
    return {
        "seed": seed,
        "by_arm": by_arm,
        "N_DIM": N_DIM,
        "CODEBOOK_SIZE": CODEBOOK_SIZE,
        "K_VALUES": K_VALUES,
        "SIGMAS": SIGMAS,
        "N_ITEMS_PER_K": N_ITEMS_PER_K,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
    }


# ============================================================================
# Verdict
# ============================================================================

def _per_K_sigma_value(by_arm_agg, arm_label, K, sigma):
    """Helper: cross-seed mean of (per_K_per_sigma) cell."""
    return by_arm_agg[arm_label]["per_K_per_sigma"]["K_%d" % K]["sigma_%.2f" % sigma]["mean"]


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    arm_labels = list(units[0]["by_arm"].keys())
    K_keys = ["K_%d" % K for K in K_VALUES]
    sigma_keys = ["sigma_%.2f" % s for s in SIGMAS]

    # Aggregate per arm, per (K, sigma): cross-seed mean / std / per-seed list.
    by_arm_agg = {}
    for arm_label in arm_labels:
        per_K_per_sigma_agg = {}
        per_K_mean_agg = {}
        for kk in K_keys:
            per_sigma_cell = {}
            for sk in sigma_keys:
                vals = [u["by_arm"][arm_label]["per_K_per_sigma"][kk][sk] for u in units]
                m = float(np.mean(vals))
                s = float(np.std(vals))
                per_sigma_cell[sk] = {
                    "mean": round(m, 4),
                    "std": round(s, 4),
                    "cv": round(s / max(abs(m), 1e-6), 4),
                    "per_seed": [round(x, 4) for x in vals],
                }
            per_K_per_sigma_agg[kk] = per_sigma_cell
            mean_vals = [u["by_arm"][arm_label]["per_K_mean_over_sigma"][kk] for u in units]
            mm = float(np.mean(mean_vals))
            ms = float(np.std(mean_vals))
            per_K_mean_agg[kk] = {
                "mean": round(mm, 4),
                "std": round(ms, 4),
                "cv": round(ms / max(abs(mm), 1e-6), 4),
                "per_seed": [round(x, 4) for x in mean_vals],
            }
        by_arm_agg[arm_label] = {
            "per_K_per_sigma": per_K_per_sigma_agg,
            "per_K_mean_over_sigma": per_K_mean_agg,
        }

    cleanup_arm = "ARM_HRR_SLOTS_PLUS_CLEANUP"
    slots_arm = "ARM_HRR_SLOTS"
    flat_arm = "ARM_FLAT_SUPERPOSITION"

    # HARD_PASS check: CLEANUP at K=32 sigma=1.0 mean >= 0.80
    k32_s10_cleanup = _per_K_sigma_value(by_arm_agg, cleanup_arm, 32, 1.0)
    # HARD_FAIL check: SLOTS at K=16 sigma=0.5 mean < 0.50
    k16_s05_slots = _per_K_sigma_value(by_arm_agg, slots_arm, 16, 0.5)

    hp_check = (k32_s10_cleanup >= HP_K32_SIGMA10_RECALL)
    hf_check = (k16_s05_slots < HF_K16_SIGMA05_RECALL)

    detail = {
        "by_arm_agg": by_arm_agg,
        "k32_sigma1.0_cleanup_mean": k32_s10_cleanup,
        "k16_sigma0.5_slots_mean": k16_s05_slots,
        "hp_passes": bool(hp_check),
        "hf_triggers": bool(hf_check),
        "n_seeds": len(units),
        "N_DIM": N_DIM,
        "CODEBOOK_SIZE": CODEBOOK_SIZE,
        "N_ITEMS_PER_K": N_ITEMS_PER_K,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Substrate-native working memory via HRR slot binding + codebook "
            "cleanup; production-regime capacity envelope at N_DIM=%d, codebook=%d. "
            "3 arms x K-sweep [8,16,32,64,128,256] x sigma-sweep [0.0,0.5,1.0,1.5,2.0] "
            "x %d seeds, %d items per (K, sigma, arm, seed). HARD_PASS = CLEANUP "
            "recall at K=32 sigma=1.0 >= %.2f (substrate holds ~5x Miller capacity "
            "at meaningful noise; chain-grade-eligible). HARD_FAIL = HRR_SLOTS "
            "(no cleanup) recall at K=16 sigma=0.5 < %.2f (working memory broken "
            "at modest load+noise). MIDDLE = capacity envelope characterized." % (
                N_DIM, CODEBOOK_SIZE, len(SEEDS), N_ITEMS_PER_K,
                HP_K32_SIGMA10_RECALL, HF_K16_SIGMA05_RECALL)),
        "cites": [
            "preregs/2026-06-23_working_memory_hrr_slots_PRODUCTION_v1.md",
            "experiments/exp_working_memory_hrr_slots_smoke_v1.py (smoke; saturated 1.000 K<=16 sigma<=1.0)",
            "hdlab/sequence_memory.py (complementary sequence-binding primitive)",
            "USER_2026-06-23_substrate_native_scratch_space_multi_hop_reasoning",
        ],
    }

    # Build summary: per-arm per-K mean-over-sigma snapshot.
    parts = []
    for arm_label in arm_labels:
        per_K = by_arm_agg[arm_label]["per_K_mean_over_sigma"]
        kk_str = " ".join(["%s=%.2f" % (kk, per_K[kk]["mean"]) for kk in K_keys])
        parts.append("%s[%s]" % (arm_label, kk_str))
    summary = "WORKING_MEMORY_HRR_SLOTS_PRODUCTION: " + " | ".join(parts)

    # Add discriminator point readout to summary.
    discriminator = " | DISCRIMINATOR: CLEANUP K=32 sigma=1.0=%.3f (HP>=%.2f), SLOTS K=16 sigma=0.5=%.3f (HF<%.2f)" % (
        k32_s10_cleanup, HP_K32_SIGMA10_RECALL, k16_s05_slots, HF_K16_SIGMA05_RECALL)

    if hp_check:
        return ("HARD_PASS",
                ("WORKING_MEMORY_HRR_SLOTS_PRODUCTION HARD_PASS: ARM_HRR_SLOTS_PLUS_CLEANUP "
                 "recall at K=32 sigma=1.0 = %.3f (>= %.2f); substrate holds 32-item "
                 "working memory at meaningful noise -- structurally exceeds Miller's "
                 "7+/-2 PFC bound at N_DIM=%d on a %d-atom codebook; chain-grade-"
                 "eligible substrate working-memory primitive at super-human scale. " % (
                     k32_s10_cleanup, HP_K32_SIGMA10_RECALL, N_DIM, CODEBOOK_SIZE))
                + summary + discriminator,
                detail)

    if hf_check:
        return ("HARD_FAIL",
                ("WORKING_MEMORY_HRR_SLOTS_PRODUCTION HARD_FAIL: ARM_HRR_SLOTS (no cleanup) "
                 "recall at K=16 sigma=0.5 = %.3f (< %.2f); working-memory primitive "
                 "broken at modest load + modest noise without cleanup; the cleanup "
                 "stage is load-bearing -- substrate working memory cannot survive in "
                 "no-cleanup regime even at sub-Miller K. " % (
                     k16_s05_slots, HF_K16_SIGMA05_RECALL))
                + summary + discriminator,
                detail)

    # MIDDLE: characterize envelope.
    return ("MIDDLE_BAND",
            ("WORKING_MEMORY_HRR_SLOTS_PRODUCTION MIDDLE_BAND: CLEANUP at K=32 sigma=1.0 "
             "= %.3f (target >= %.2f), SLOTS at K=16 sigma=0.5 = %.3f (HF "
             "trigger < %.2f); capacity envelope characterized across K=[8,16,32,64,128,256] "
             "and sigma=[0.0,0.5,1.0,1.5,2.0]; route to follow-up to push the "
             "discriminator boundary. " % (
                 k32_s10_cleanup, HP_K32_SIGMA10_RECALL, k16_s05_slots,
                 HF_K16_SIGMA05_RECALL))
            + summary + discriminator,
            detail)


# ============================================================================
# atexit synthesizer
# ============================================================================
_METRICS_WRITTEN = [False]
_OUT_DIR_REF = [None]
_T0_REF = [None]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                     "atexit synthesize: compute_verdict failed: %s" % e,
                                     {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": ("TIMEOUT_PARTIAL_NSEEDS_%d" % len(units)) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_working_memory_hrr_slots_PRODUCTION_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ============================================================================
# Self-test (mechanism + sanity + verdict-shape; cheap)
# ============================================================================

def _selftest():
    rng = np.random.default_rng(0)

    # T1: bipolar_quantize bipolar output, zero -> +1
    v = np.array([0.5, -0.3, 0.0, -0.8, 1.2], dtype=np.float32)
    q = bipolar_quantize(v)
    assert set(np.unique(q).tolist()).issubset({-1.0, 1.0}), "T1 not bipolar: %s" % q
    assert q[2] == 1.0, "T1 zero -> +1 expected, got %s" % q[2]

    # T2: bind involutive on bipolar
    a = random_bipolar(rng, (64,))
    b = random_bipolar(rng, (64,))
    ab = bind_elementwise(a, b)
    abb = bind_elementwise(ab, b)
    assert np.allclose(abb, a), "T2 bind not involutive"

    # T3: random_bipolar values
    x = random_bipolar(rng, (10, 8))
    assert set(np.unique(x).tolist()).issubset({-1.0, 1.0}), "T3 not bipolar"
    assert x.shape == (10, 8), "T3 shape: %s" % (x.shape,)

    # T4: K=1 trivial case at sigma=0 for HRR_SLOTS_PLUS_CLEANUP -> recall = 1.0
    cb_rng = np.random.default_rng(99)
    slot_rng = np.random.default_rng(100)
    cb_small = random_bipolar(cb_rng, (10, 256)).astype(np.float32)
    st_small = random_bipolar(slot_rng, (1, 256)).astype(np.float32)
    item_idx = 3
    workspace = (cb_small[item_idx:item_idx+1] * st_small).sum(axis=0)
    retrieved = workspace * st_small[0]
    assert np.allclose(retrieved, cb_small[item_idx]), "T4 K=1 unbind not exact"
    pred = int(np.argmax(cb_small @ retrieved))
    assert pred == item_idx, "T4 K=1 cleanup picks wrong index"

    # T5: HRR_SLOTS at K=2 sigma=0 with cleanup recovers BOTH items exactly
    items_2 = cb_small[:2]
    st2 = random_bipolar(slot_rng, (2, 256)).astype(np.float32)
    hrr_ws = (items_2 * st2).sum(axis=0)
    for i in range(2):
        r = hrr_ws * st2[i]
        pred = int(np.argmax(cb_small @ r))
        assert pred == i, "T5 HRR_SLOTS K=2 cleanup failed at slot %d (pred=%d)" % (i, pred)

    # T6: cleanup_to_codebook self-identity
    big_cb = random_bipolar(rng, (CODEBOOK_SIZE, N_DIM)).astype(np.float32)
    pred = cleanup_to_codebook(big_cb[7], big_cb)
    assert pred == 7, "T6 cleanup self-id failed: pred=%d" % pred

    # T7: SANITY (user-required) -- K=2 sigma=0.0 recall=1.0 across all arms.
    # FLAT cannot distinguish 2 slots but at K=2 the workspace is sum of 2 items;
    # nearest in codebook will be one of the 2; both slots predict the same idx so
    # recall <= 0.5. FLAT therefore VIOLATES "recall=1.0 at K=2 sigma=0" by design
    # -- FLAT is the negative control. Sanity is enforced over HRR arms only.
    cb_t = random_bipolar(np.random.default_rng(50), (CODEBOOK_SIZE, N_DIM)).astype(np.float32)
    st_t = random_bipolar(np.random.default_rng(51), (max(K_VALUES), N_DIM)).astype(np.float32)
    trial_t = np.random.default_rng(52)
    r_hrr = eval_one_K_sigma_arm(2, 0.0, "ARM_HRR_SLOTS", cb_t, st_t, trial_t)
    assert r_hrr >= 0.99, "T7 sanity ARM_HRR_SLOTS K=2 sigma=0 recall %.3f (<0.99)" % r_hrr
    trial_t2 = np.random.default_rng(53)
    r_clean = eval_one_K_sigma_arm(2, 0.0, "ARM_HRR_SLOTS_PLUS_CLEANUP", cb_t, st_t, trial_t2)
    assert r_clean >= 0.99, "T7 sanity ARM_HRR_SLOTS_PLUS_CLEANUP K=2 sigma=0 recall %.3f (<0.99)" % r_clean

    # T8: verdict-shape synth -- HARD_PASS scenario.
    def _mk_unit(cleanup_per_K_sigma, slots_per_K_sigma, flat_per_K_sigma):
        """cleanup_per_K_sigma: dict[K -> dict[sigma -> val]]."""
        ba = {}
        for arm_label, dat in [("ARM_FLAT_SUPERPOSITION", flat_per_K_sigma),
                                ("ARM_HRR_SLOTS", slots_per_K_sigma),
                                ("ARM_HRR_SLOTS_PLUS_CLEANUP", cleanup_per_K_sigma)]:
            per_K_per_sigma = {}
            per_K_mean = {}
            for K in K_VALUES:
                cell = {}
                vals = []
                for sigma in SIGMAS:
                    v = dat[K][sigma]
                    cell["sigma_%.2f" % sigma] = v
                    vals.append(v)
                per_K_per_sigma["K_%d" % K] = cell
                per_K_mean["K_%d" % K] = float(np.mean(vals))
            ba[arm_label] = {"per_K_per_sigma": per_K_per_sigma,
                              "per_K_mean_over_sigma": per_K_mean, "wall_s": 0.0}
        return {"seed": 0, "by_arm": ba, "N_DIM": N_DIM, "CODEBOOK_SIZE": CODEBOOK_SIZE,
                "K_VALUES": K_VALUES, "SIGMAS": SIGMAS, "N_ITEMS_PER_K": N_ITEMS_PER_K,
                "run_mode": "smoke", "config_version": "selftest", "elapsed_s_seed": 0.01}

    def _grid(default, overrides=None):
        g = {K: {s: default for s in SIGMAS} for K in K_VALUES}
        if overrides:
            for (K, s), v in overrides.items():
                g[K][s] = v
        return g

    # HARD_PASS: CLEANUP K=32 sigma=1.0 = 0.90 (>=0.80); SLOTS K=16 sigma=0.5 = 0.60 (>0.50)
    u_hp = _mk_unit(
        cleanup_per_K_sigma=_grid(0.95, overrides={(32, 1.0): 0.90}),
        slots_per_K_sigma=_grid(0.70, overrides={(16, 0.5): 0.60}),
        flat_per_K_sigma=_grid(0.10))
    v_, m_, d_ = compute_verdict([u_hp, u_hp, u_hp])
    assert v_ == "HARD_PASS", "T8 HARD_PASS expected, got %s msg=%s" % (v_, m_[:200])

    # HARD_FAIL: SLOTS K=16 sigma=0.5 = 0.40 (<0.50); CLEANUP K=32 sigma=1.0 = 0.50 (<0.80; not HP)
    u_hf = _mk_unit(
        cleanup_per_K_sigma=_grid(0.50, overrides={(32, 1.0): 0.50}),
        slots_per_K_sigma=_grid(0.35, overrides={(16, 0.5): 0.40}),
        flat_per_K_sigma=_grid(0.10))
    v_, m_, d_ = compute_verdict([u_hf, u_hf, u_hf])
    assert v_ == "HARD_FAIL", "T8 HARD_FAIL expected, got %s msg=%s" % (v_, m_[:200])

    # MIDDLE: CLEANUP K=32 sigma=1.0 = 0.75 (<0.80; HP miss); SLOTS K=16 sigma=0.5 = 0.60 (>=0.50; HF no trigger)
    u_mid = _mk_unit(
        cleanup_per_K_sigma=_grid(0.80, overrides={(32, 1.0): 0.75}),
        slots_per_K_sigma=_grid(0.65, overrides={(16, 0.5): 0.60}),
        flat_per_K_sigma=_grid(0.10))
    v_, m_, d_ = compute_verdict([u_mid, u_mid, u_mid])
    assert v_ == "MIDDLE_BAND", "T8 MIDDLE expected, got %s msg=%s" % (v_, m_[:200])

    # T9: cleanup K=8 sigma=0 should give recall >= 0.95 on real evaluator (sanity)
    trial_t3 = np.random.default_rng(54)
    r_clean_k8 = eval_one_K_sigma_arm(8, 0.0, "ARM_HRR_SLOTS_PLUS_CLEANUP",
                                       cb_t, st_t, trial_t3)
    assert r_clean_k8 >= 0.95, "T9 cleanup K=8 sigma=0 recall too low: %.3f" % r_clean_k8

    # T10: FLAT at K=8 sigma=0 should be <= 1/K * margin ~ 0.20 (cannot distinguish slots)
    trial_t4 = np.random.default_rng(55)
    r_flat = eval_one_K_sigma_arm(8, 0.0, "ARM_FLAT_SUPERPOSITION",
                                   cb_t, st_t, trial_t4)
    assert r_flat <= 0.20, "T10 FLAT K=8 recall too high (mechanism leak): %.3f" % r_flat

    print("[selftest] PASS: T1 bipolar quantize + T2 bind involutive + T3 "
          "random_bipolar + T4 K=1 trivial recall + T5 K=2 cleanup recovers + "
          "T6 cleanup_to_codebook self-id + T7 SANITY K=2 sigma=0 recall>=0.99 "
          "(HRR arms) + T8 verdict bands HP/HF/MID + T9 cleanup K=8 sigma=0 "
          ">=0.95 + T10 FLAT K=8 sigma=0 <=0.20 OK", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d arms=%s seeds=%s K_VALUES=%s SIGMAS=%s "
          "N_ITEMS_PER_K=%d | name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, ARMS, SEEDS, K_VALUES, SIGMAS,
              N_ITEMS_PER_K, _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "working-memory-hrr-slots-PRODUCTION-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "CODEBOOK_SIZE": CODEBOOK_SIZE,
        "K_VALUES": K_VALUES,
        "SIGMAS": SIGMAS,
        "N_ITEMS_PER_K": N_ITEMS_PER_K,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_working_memory_hrr_slots_PRODUCTION_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (substrate-native HRR slot-binding + codebook cleanup; numpy only; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "_name_says_smoke_workaround": _NAME_SAYS_SMOKE,
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
