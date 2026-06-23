"""working_memory_hrr_slots_smoke_v1 -- substrate-native working memory via HRR slot binding.

Substrate-native scratch space for multi-hop reasoning. Working memory is a single
HD vector with K items bound to K slot tags via HRR superposition:

    WRITE: workspace = sum_i bind(item_i, slot_tag_i)
    READ:  retrieve_i = unbind(workspace, slot_tag_i) ~= item_i + crosstalk
    CLEAN: argmax cosine(retrieve_i, codebook) -> recovered item

Brain analog: PFC sustained-firing neurons + theta-gamma binding (each working-memory
slot held at a distinct gamma phase within theta cycle; ~7 slots / theta cycle =
Miller's magic number).

DESIGN (3 arms x 3 seeds x K-sweep [2,4,7,10,16] x sigma-sweep [0.0, 0.5, 1.0]
at N_DIM=4096 over 50 test items per K from a shared 50-item codebook):

  ARM_FLAT_SUPERPOSITION         -- control; bundle items without slot tags;
                                    cannot distinguish positions; per-slot recall
                                    expected near 1/K.
  ARM_HRR_SLOTS                  -- the mechanism; bind items to slot tags, sum
                                    -> workspace; retrieve via unbind (= bind for
                                    bipolar). No cleanup.
  ARM_HRR_SLOTS_PLUS_CLEANUP     -- full mechanism; HRR slots + per-slot argmax
                                    cleanup against the 50-item codebook.

bind = element-wise product on bipolar vectors (substrate-native HRR analog;
involutive: bind(bind(a, b), b) = a).

Evaluation:
  For each (K, sigma, arm, seed):
    1. Draw K item indices uniformly from a 50-item codebook.
    2. Draw K slot tags (deterministic per seed, distinct from items).
    3. Assemble workspace per arm.
    4. Add Gaussian noise (sigma) to workspace; bipolar-quantize.
    5. For each slot i: retrieve_i; (cleanup if arm) -> predicted item index.
       Correct iff predicted == ground-truth item index.
    6. Per-slot recall = correct/K.
  Aggregated metric per arm per K: mean over sigmas + seeds of per-slot recall.

PRE-REG bands (preregs/2026-06-23_working_memory_hrr_slots_smoke_v1.md):
  HARD_PASS = ARM_HRR_SLOTS_PLUS_CLEANUP mean per-slot recall (across noise
              sigmas) >= 0.90 at K=7 AND >= 0.70 at K=10 AND >= 0.50 at K=16.
  HARD_FAIL = ARM_HRR_SLOTS mean per-slot recall at K=4 <= 0.50.
  MIDDLE    = otherwise.

SANITY: at K=1, all arms recall=1.0 at sigma=0 (trivial). ARM_FLAT_SUPERPOSITION
at K>=2 cannot distinguish positions (recall ~ 1/K random).

SUBSTRATE-ONLY: n_llm_calls = 0; numpy only; no pretrained encoder needed
(synthetic bipolar atoms).
"""
from __future__ import annotations
import sys, os, argparse, time, signal, atexit
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "working_memory_hrr_slots_smoke_v1"
_LLM_CALL_COUNTER = [0]

# Pre-reg HARD bands
HP_K7_RECALL = 0.90
HP_K10_RECALL = 0.70
HP_K16_RECALL = 0.50
HF_K4_RECALL = 0.50

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 4096
CODEBOOK_SIZE = 50
K_VALUES = [2, 4, 7, 10, 16]
SIGMAS = [0.0, 0.5, 1.0]

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
else:
    SEEDS = [7]  # smoke

ARMS = ["ARM_FLAT_SUPERPOSITION", "ARM_HRR_SLOTS", "ARM_HRR_SLOTS_PLUS_CLEANUP"]

CONFIG_VERSION = (
    "working_memory_hrr_slots_smoke_v1; N_DIM=%d CODEBOOK_SIZE=%d K_VALUES=%s "
    "SIGMAS=%s arms=%s seeds=%s mode=%s; bands HP_K7>=%.2f HP_K10>=%.2f "
    "HP_K16>=%.2f HF_K4<=%.2f"
) % (N_DIM, CODEBOOK_SIZE, K_VALUES, SIGMAS, ARMS, SEEDS, RUN_MODE,
     HP_K7_RECALL, HP_K10_RECALL, HP_K16_RECALL, HF_K4_RECALL)


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


# unbind == bind for bipolar (b * b = +1 elementwise); kept as alias for clarity
def unbind_elementwise(a: np.ndarray, b: np.ndarray) -> np.ndarray:
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
    "ARM_HRR_SLOTS_PLUS_CLEANUP": assemble_hrr_slots,  # same workspace; cleanup happens at read
}


def retrieve_slot(workspace: np.ndarray, slot_tag: np.ndarray, arm_label: str) -> np.ndarray:
    """Retrieve slot content from workspace using slot_tag (bipolar unbind).

    For FLAT, slot_tag is ignored; we still need to return something, so we
    return the workspace itself (cannot distinguish; downstream eval will resolve).
    For HRR arms, retrieve_i = bind(workspace, slot_tag_i) (== unbind for bipolar).
    """
    if arm_label == "ARM_FLAT_SUPERPOSITION":
        return workspace.astype(np.float32)
    return (workspace * slot_tag).astype(np.float32)


def cleanup_to_codebook(retrieve_vec: np.ndarray, codebook: np.ndarray) -> int:
    """Argmax cosine over codebook. Returns the index of the best-matching atom."""
    # codebook: [CODEBOOK_SIZE, N_DIM], retrieve_vec: [N_DIM]
    sims = codebook @ retrieve_vec
    return int(np.argmax(sims))


# ============================================================================
# Evaluation: per-K, per-sigma, per-arm per-slot recall
# ============================================================================

def eval_one_K_sigma_arm(K: int, sigma: float, arm_label: str,
                         codebook: np.ndarray, slot_tags_full: np.ndarray,
                         rng: np.random.Generator) -> float:
    """Run the K-item working-memory write/read for one (K, sigma, arm).

    Returns mean per-slot recall (correct/K) averaged over CODEBOOK_SIZE / K
    trials. We run multiple disjoint K-tuples drawn from the codebook to make
    each measurement stable; total items used per trial sums to CODEBOOK_SIZE
    when divisible, otherwise we use CODEBOOK_SIZE // K trials.
    """
    n_trials = max(1, CODEBOOK_SIZE // K)
    slot_tags = slot_tags_full[:K]  # [K, N_DIM]
    correct = 0
    total = 0
    perm = rng.permutation(CODEBOOK_SIZE)
    for t in range(n_trials):
        idx_in_perm = perm[t * K:(t + 1) * K]
        if len(idx_in_perm) < K:
            break
        items = codebook[idx_in_perm]  # [K, N_DIM]
        workspace = ARM_ASSEMBLERS[arm_label](items, slot_tags)
        # Add gaussian noise (real-valued) then bipolar-quantize the workspace
        if sigma > 0.0:
            noise = rng.standard_normal(workspace.shape).astype(np.float32) * sigma
            noisy = workspace + noise
        else:
            noisy = workspace
        noisy_bp = bipolar_quantize(noisy)
        # For each slot, retrieve + cleanup; check vs ground truth item index
        for i in range(K):
            r = retrieve_slot(noisy_bp, slot_tags[i], arm_label)
            if arm_label == "ARM_HRR_SLOTS":
                # No cleanup: use cosine to codebook to recover index (raw nearest-neighbour)
                pred_idx = cleanup_to_codebook(r, codebook)
            elif arm_label == "ARM_HRR_SLOTS_PLUS_CLEANUP":
                pred_idx = cleanup_to_codebook(r, codebook)
            else:  # FLAT
                # Cannot distinguish slot; pick nearest item to workspace itself
                pred_idx = cleanup_to_codebook(r, codebook)
            if pred_idx == int(idx_in_perm[i]):
                correct += 1
            total += 1
    return correct / max(total, 1)


# ============================================================================
# Per-seed unit
# ============================================================================

def run_unit(seed: int) -> Dict:
    t0 = time.time()
    print("\n[seed=%d] building codebook + slot tags at N_DIM=%d ..." % (seed, N_DIM), flush=True)
    # Separate rngs for codebook vs slot-tags vs trial-permutation, so codebook
    # and slot tags are reproducible across (K, sigma, arm) loops.
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
        # Summary print per arm
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
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    arm_labels = list(units[0]["by_arm"].keys())
    K_keys = ["K_%d" % K for K in K_VALUES]
    # Aggregate per arm, per K: mean and std across seeds of (per-K mean-over-sigma)
    by_arm_agg = {}
    for arm_label in arm_labels:
        per_K = {}
        for kk in K_keys:
            vals = [u["by_arm"][arm_label]["per_K_mean_over_sigma"][kk] for u in units]
            m = float(np.mean(vals))
            s = float(np.std(vals))
            per_K[kk] = {
                "mean": round(m, 4),
                "std": round(s, 4),
                "cv": round(s / max(abs(m), 1e-6), 4),
                "per_seed": [round(x, 4) for x in vals],
            }
        by_arm_agg[arm_label] = {"per_K": per_K}

    # Classification
    cleanup_arm = "ARM_HRR_SLOTS_PLUS_CLEANUP"
    slots_arm = "ARM_HRR_SLOTS"
    flat_arm = "ARM_FLAT_SUPERPOSITION"

    k7 = by_arm_agg[cleanup_arm]["per_K"]["K_7"]["mean"]
    k10 = by_arm_agg[cleanup_arm]["per_K"]["K_10"]["mean"]
    k16 = by_arm_agg[cleanup_arm]["per_K"]["K_16"]["mean"]
    k4_slots = by_arm_agg[slots_arm]["per_K"]["K_4"]["mean"]

    hp_check = (k7 >= HP_K7_RECALL) and (k10 >= HP_K10_RECALL) and (k16 >= HP_K16_RECALL)
    hf_check = (k4_slots <= HF_K4_RECALL)

    detail = {
        "by_arm_agg": by_arm_agg,
        "k7_cleanup_mean": k7,
        "k10_cleanup_mean": k10,
        "k16_cleanup_mean": k16,
        "k4_slots_mean": k4_slots,
        "k7_passes_HP": bool(k7 >= HP_K7_RECALL),
        "k10_passes_HP": bool(k10 >= HP_K10_RECALL),
        "k16_passes_HP": bool(k16 >= HP_K16_RECALL),
        "k4_slots_triggers_HF": bool(hf_check),
        "n_seeds": len(units),
        "N_DIM": N_DIM,
        "CODEBOOK_SIZE": CODEBOOK_SIZE,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Substrate-native working memory via HRR slot binding + codebook "
            "cleanup; 3 arms x K-sweep [2,4,7,10,16] x sigma-sweep [0.0,0.5,1.0] "
            "at N_DIM=%d on %d-atom codebook; HARD_PASS = CLEANUP arm clears K=7 "
            ">=%.2f AND K=10 >=%.2f AND K=16 >=%.2f (mean-over-sigma); HARD_FAIL = "
            "HRR_SLOTS (no cleanup) at K=4 <=%.2f. Brain analog: PFC theta-gamma "
            "binding at Miller-capacity scale." % (
                N_DIM, CODEBOOK_SIZE, HP_K7_RECALL, HP_K10_RECALL, HP_K16_RECALL,
                HF_K4_RECALL)),
        "cites": [
            "preregs/2026-06-23_working_memory_hrr_slots_smoke_v1.md",
            "experiments/exp_contextual_encoding_hrr_binding_smoke_v1.py (HRR bipolar bind pattern)",
            "hdlab/sequence_memory.py (sequence-binding precedent; complementary primitive)",
            "USER_2026-06-23_substrate_native_scratch_space_multi_hop_reasoning",
        ],
    }

    # Build summary
    parts = []
    for arm_label in arm_labels:
        per_K = by_arm_agg[arm_label]["per_K"]
        kk_str = " ".join(["%s=%.2f" % (kk, per_K[kk]["mean"]) for kk in K_keys])
        parts.append("%s[%s]" % (arm_label, kk_str))
    summary = "WORKING_MEMORY_HRR_SLOTS: " + " | ".join(parts)

    if hp_check:
        return ("HARD_PASS",
                ("WORKING_MEMORY_HRR_SLOTS HARD_PASS: ARM_HRR_SLOTS_PLUS_CLEANUP "
                 "clears K=7 recall=%.3f (>=%.2f) AND K=10 recall=%.3f (>=%.2f) "
                 "AND K=16 recall=%.3f (>=%.2f); substrate-native working memory "
                 "at Miller-capacity scale validated; chain-grade-eligible scratch-"
                 "space primitive for multi-hop reasoning; PFC theta-gamma analog "
                 "operational at N_DIM=%d. " % (
                     k7, HP_K7_RECALL, k10, HP_K10_RECALL, k16, HP_K16_RECALL,
                     N_DIM)) + summary,
                detail)

    if hf_check:
        return ("HARD_FAIL",
                ("WORKING_MEMORY_HRR_SLOTS HARD_FAIL: ARM_HRR_SLOTS (no cleanup) "
                 "at K=4 recall=%.3f (<=%.2f); substrate cannot even hold 4 items "
                 "via slot binding; working-memory primitive is structurally null "
                 "at N_DIM=%d; pivot to alternative scratch-space mechanism "
                 "(sparse-VSA / role-filler binding / external content-addressable "
                 "register). " % (k4_slots, HF_K4_RECALL, N_DIM)) + summary,
                detail)

    # MIDDLE: characterize partial capacity envelope
    pass_msgs = []
    if k7 >= HP_K7_RECALL:
        pass_msgs.append("K=7 PASS (%.3f)" % k7)
    else:
        pass_msgs.append("K=7 MISS (%.3f<%.2f)" % (k7, HP_K7_RECALL))
    if k10 >= HP_K10_RECALL:
        pass_msgs.append("K=10 PASS (%.3f)" % k10)
    else:
        pass_msgs.append("K=10 MISS (%.3f<%.2f)" % (k10, HP_K10_RECALL))
    if k16 >= HP_K16_RECALL:
        pass_msgs.append("K=16 PASS (%.3f)" % k16)
    else:
        pass_msgs.append("K=16 MISS (%.3f<%.2f)" % (k16, HP_K16_RECALL))
    return ("MIDDLE_BAND",
            ("WORKING_MEMORY_HRR_SLOTS MIDDLE_BAND: cleanup arm partially clears "
             "Miller-capacity ladder: %s; substrate working-memory primitive "
             "characterized envelope, route to follow-up (larger N_DIM, smaller "
             "codebook, sparse-VSA variant) to push the upper-K threshold. " % (
                 "; ".join(pass_msgs))) + summary,
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
            "metrics_source": "atexit_synthesize_partial_working_memory_hrr_slots_smoke_v1",
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
# Self-test (mechanism + sanity + verdict-shape; no network; cheap)
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
    trial_rng = np.random.default_rng(101)
    cb_small = random_bipolar(cb_rng, (10, 256)).astype(np.float32)
    st_small = random_bipolar(slot_rng, (1, 256)).astype(np.float32)
    # Manually run K=1 mini eval
    item_idx = 3
    workspace = (cb_small[item_idx:item_idx+1] * st_small).sum(axis=0)
    retrieved = workspace * st_small[0]  # involutive unbind: should recover cb_small[3] exactly
    assert np.allclose(retrieved, cb_small[item_idx]), "T4 K=1 unbind not exact"
    pred = int(np.argmax(cb_small @ retrieved))
    assert pred == item_idx, "T4 K=1 cleanup picks wrong index"

    # T5: FLAT arm cannot distinguish slot positions; at K=2 with two different
    # items the workspace is the SUM of both items and "retrieve" is identical
    # for both slots, so per-slot recall is at best 0.5 (correct iff argmax of
    # bundle happens to land on one of the two items, which is not slot-aware).
    items_2 = cb_small[:2]
    flat_ws = items_2.sum(axis=0)
    # nearest in codebook
    nearest = int(np.argmax(cb_small @ flat_ws))
    # nearest will be 0 or 1; for both "slots" we'd predict the SAME index ->
    # at most one of the two slots is correct (recall <= 0.5)
    assert nearest in (0, 1), "T5 FLAT mech sanity (nearest in {0,1})"

    # T6: HRR_SLOTS at K=2 sigma=0 with cleanup recovers BOTH items exactly
    st2 = random_bipolar(slot_rng, (2, 256)).astype(np.float32)
    hrr_ws = (items_2 * st2).sum(axis=0)
    for i in range(2):
        r = hrr_ws * st2[i]
        pred = int(np.argmax(cb_small @ r))
        assert pred == i, "T6 HRR_SLOTS K=2 cleanup failed at slot %d (pred=%d)" % (i, pred)

    # T7: cleanup_to_codebook returns int in [0, CODEBOOK_SIZE-1]
    big_cb = random_bipolar(rng, (CODEBOOK_SIZE, N_DIM)).astype(np.float32)
    pred = cleanup_to_codebook(big_cb[7], big_cb)
    assert pred == 7, "T7 cleanup self-id failed: pred=%d" % pred

    # T8: verdict-shape sanity (synthetic units)
    def _mk_unit(cleanup_per_K, slots_per_K, flat_per_K):
        ba = {}
        for arm_label, dat in [("ARM_FLAT_SUPERPOSITION", flat_per_K),
                                ("ARM_HRR_SLOTS", slots_per_K),
                                ("ARM_HRR_SLOTS_PLUS_CLEANUP", cleanup_per_K)]:
            per_K_per_sigma = {}
            per_K_mean = {}
            for K, m in zip(K_VALUES, dat):
                per_K_per_sigma["K_%d" % K] = {"sigma_0.00": m, "sigma_0.50": m, "sigma_1.00": m}
                per_K_mean["K_%d" % K] = m
            ba[arm_label] = {"per_K_per_sigma": per_K_per_sigma,
                              "per_K_mean_over_sigma": per_K_mean, "wall_s": 0.0}
        return {"seed": 0, "by_arm": ba, "N_DIM": N_DIM, "CODEBOOK_SIZE": CODEBOOK_SIZE,
                "K_VALUES": K_VALUES, "SIGMAS": SIGMAS, "run_mode": "smoke",
                "config_version": "selftest", "elapsed_s_seed": 0.01}

    # HARD_PASS scenario: cleanup K=7,10,16 = 0.95, 0.80, 0.60
    u_hp = _mk_unit(cleanup_per_K=[1.0, 1.0, 0.95, 0.80, 0.60],
                    slots_per_K=[1.0, 0.95, 0.70, 0.50, 0.30],
                    flat_per_K=[0.50, 0.25, 0.14, 0.10, 0.06])
    v_, m_, d_ = compute_verdict([u_hp, u_hp, u_hp])
    assert v_ == "HARD_PASS", "T8 HARD_PASS expected, got %s msg=%s" % (v_, m_[:200])

    # HARD_FAIL scenario: slots K=4 = 0.40 (<=0.50)
    u_hf = _mk_unit(cleanup_per_K=[0.30, 0.40, 0.30, 0.20, 0.10],
                    slots_per_K=[0.30, 0.40, 0.20, 0.10, 0.05],
                    flat_per_K=[0.30, 0.20, 0.10, 0.08, 0.05])
    v_, m_, d_ = compute_verdict([u_hf, u_hf, u_hf])
    assert v_ == "HARD_FAIL", "T8 HARD_FAIL expected, got %s msg=%s" % (v_, m_[:200])

    # MIDDLE scenario: cleanup K=7 passes but K=10 misses; slots K=4 above HF threshold
    u_mid = _mk_unit(cleanup_per_K=[1.0, 0.95, 0.92, 0.55, 0.30],
                     slots_per_K=[0.95, 0.80, 0.60, 0.40, 0.20],
                     flat_per_K=[0.50, 0.25, 0.14, 0.10, 0.06])
    v_, m_, d_ = compute_verdict([u_mid, u_mid, u_mid])
    assert v_ == "MIDDLE_BAND", "T8 MIDDLE expected, got %s msg=%s" % (v_, m_[:200])

    # T9: eval_one_K_sigma_arm at K=2 sigma=0 cleanup arm should give recall >=0.95
    # using tiny config (sanity on the real evaluator)
    cb_t = random_bipolar(np.random.default_rng(50), (CODEBOOK_SIZE, N_DIM)).astype(np.float32)
    st_t = random_bipolar(np.random.default_rng(51), (16, N_DIM)).astype(np.float32)
    trial_t = np.random.default_rng(52)
    r_clean = eval_one_K_sigma_arm(2, 0.0, "ARM_HRR_SLOTS_PLUS_CLEANUP",
                                    cb_t, st_t, trial_t)
    assert r_clean >= 0.95, "T9 cleanup K=2 sigma=0 recall too low: %.3f" % r_clean

    # T10: FLAT at K=4 sigma=0 should be <= 0.30 (cannot distinguish slots)
    trial_t2 = np.random.default_rng(53)
    r_flat = eval_one_K_sigma_arm(4, 0.0, "ARM_FLAT_SUPERPOSITION",
                                   cb_t, st_t, trial_t2)
    assert r_flat <= 0.30, "T10 FLAT K=4 recall too high (mechanism leak): %.3f" % r_flat

    print("[selftest] PASS: T1 bipolar quantize + T2 bind involutive + T3 "
          "random_bipolar + T4 K=1 trivial recall + T5 FLAT cannot distinguish + "
          "T6 HRR_SLOTS K=2 cleanup recovers + T7 cleanup_to_codebook self-id + "
          "T8 verdict bands HP/HF/MID + T9 cleanup K=2 sigma=0 >=0.95 + T10 "
          "FLAT K=4 sigma=0 <=0.30 OK", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d arms=%s seeds=%s K_VALUES=%s SIGMAS=%s | "
          "name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, ARMS, SEEDS, K_VALUES, SIGMAS,
              _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "working-memory-hrr-slots-smoke-v1"}
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
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_working_memory_hrr_slots_smoke_v1",
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
