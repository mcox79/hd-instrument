"""substrate_working_memory_v2_extended_K_with_cleanup_per_slot -- EXT-6.

EXTENSION TARGET (per Research drill 2026-06-25 EXT-6): the WM-HRR-slots
PRODUCTION cell chain-grade at K=32 sigma=1.0 (recall 1.000); degrades to
0.95 at K=128 and 0.64 at K=256. Production WM may want K>32 reliably.

THIS CELL tests whether CLEANUP-PER-SLOT-ON-READ (vs naive HRR-slot read
without per-slot cleanup) lifts the K-ceiling. Brain analog: WM continuous
refresh via theta-gamma cleanup; substrate primitive composition (HRR slots
+ codebook argmax cleanup) never tested at this K-sweep.

ARMS (2):
  ARM_NAIVE                       current PRODUCTION mechanism: bind(slot,
                                  item), bundle, read = workspace * slot,
                                  cleanup via argmax (cleanup at READ but
                                  NOT iterated; same as WM-HRR-slots-
                                  PRODUCTION_v1's ARM_HRR_SLOTS_PLUS_CLEANUP)
  ARM_CLEANUP_PER_SLOT            cleaner mechanism: store cleaned codebook
                                  atom (not raw item) in each slot; read =
                                  workspace * slot, cleanup; key difference =
                                  the write also passes through cleanup so
                                  the slot content is by-construction in the
                                  codebook attractor, reducing crosstalk at
                                  higher K

K-sweep: {32 (rail), 64, 128, 256, 512}
sigma-sweep: {0.0, 0.5, 1.0}

PRE-REG BANDS (LOCKED at module init via assert):

  HARD_PASS_CLEANUP_LIFTS_K_TO_128:
    ARM_CLEANUP_PER_SLOT recall at K=128, sigma=1.0 >= 0.95
    (vs ARM_NAIVE at K=32, sigma=1.0 ~ 1.000; cleanup lifts K-ceiling 4x)
    AND cv <= 0.07 across seeds

  CHAIN_GRADE_K_EXTENSION_X:
    ARM_CLEANUP_PER_SLOT lifts K-ceiling by 2x or more
    (passes >= 0.95 at K = 2x the K-ceiling of ARM_NAIVE)

  MIDDLE_BAND:
    ARM_CLEANUP_PER_SLOT recall at K=128 sigma=1.0 in [0.80, 0.95]
    (some lift but not chain-grade)

  HARD_FAIL_NAIVE_IS_OPTIMAL:
    ARM_CLEANUP_PER_SLOT <= ARM_NAIVE at K=128 sigma=1.0
    (cleanup doesn't help; NAIVE is at K-ceiling)

  SANITY (selftest): K=2 sigma=0.0 both arms recall = 1.0

CONFIG:
  N=4096 (matches WM-HRR-slots-PRODUCTION v1)
  CODEBOOK_SIZE = max(K) = 512
  N_ITEMS_PER_K = 200 (held-out items per (K, sigma, arm, seed))
  Seeds [11, 13, 19] (cross-cell consistent)

Author: exp_dev 2026-06-25 (EXT-6).
ASCII-only; per-seed checkpoint; substrate-only.
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

ANCHOR_NAME = "substrate_working_memory_v2_extended_K_with_cleanup_per_slot"
_LLM_CALL_COUNTER = [0]

# Pre-reg HARD bands
HP_CLEANUP_K128_SIGMA10_RECALL = 0.95
HP_CV_MAX = 0.07
MID_K128_LO = 0.80
MID_K128_HI = 0.95
HF_REGRESSION_TOL = 0.0  # CLEANUP <= NAIVE at K=128 sigma=1.0 -> HARD_FAIL_NAIVE_IS_OPTIMAL

# Lock assertions
assert 0.0 < HP_CLEANUP_K128_SIGMA10_RECALL <= 1.0
assert MID_K128_LO < MID_K128_HI == HP_CLEANUP_K128_SIGMA10_RECALL

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 4096
CODEBOOK_SIZE = 512  # max K
K_VALUES = [32, 64, 128, 256, 512] if RUN_MODE != "smoke" else [32, 64, 128]
SIGMAS = [0.0, 0.5, 1.0]
N_ITEMS_PER_K = 200 if RUN_MODE != "smoke" else 50

if RUN_MODE == "smoke":
    SEEDS = [11]
else:
    SEEDS = [11, 13, 19]

ARMS = ["ARM_NAIVE", "ARM_CLEANUP_PER_SLOT"]

CONFIG_VERSION = (
    "substrateWmV2ExtendedKCleanupPerSlot: N_DIM=%d CODEBOOK_SIZE=%d K=%s "
    "SIGMAS=%s N_ITEMS_PER_K=%d arms=%s seeds=%s mode=%s; bands "
    "HP_CLEANUP_K128_SIGMA10>=%.2f cv<=%.2f mid=[%.2f,%.2f] HF=cleanup<=naive"
) % (N_DIM, CODEBOOK_SIZE, K_VALUES, SIGMAS, N_ITEMS_PER_K, ARMS, SEEDS,
     RUN_MODE, HP_CLEANUP_K128_SIGMA10_RECALL, HP_CV_MAX, MID_K128_LO, MID_K128_HI)


# =============================================================================
# Substrate primitives (mirrors WM-HRR-slots-PRODUCTION v1)
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


# =============================================================================
# Arms
# =============================================================================

def eval_naive(K: int, sigma: float, codebook: np.ndarray,
                slot_tags_full: np.ndarray, rng: np.random.Generator) -> float:
    """ARM_NAIVE: bundle bind(slot_i, item_i); read = workspace * slot_i; cleanup.

    Slot stores RAW item; codebook cleanup at READ time.
    Matches WM-HRR-slots-PRODUCTION_v1 ARM_HRR_SLOTS_PLUS_CLEANUP exactly.
    """
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / K))
    slot_tags = slot_tags_full[:K]
    correct = 0
    total = 0
    for _t in range(n_trials):
        idx = rng.choice(CODEBOOK_SIZE, size=K, replace=False)
        items = codebook[idx]  # [K, N_DIM]
        # Workspace: sum_i bind(item_i, slot_i)
        workspace = (items * slot_tags).sum(axis=0).astype(np.float32)
        if sigma > 0.0:
            noise = rng.standard_normal(workspace.shape).astype(np.float32) * sigma
            noisy = workspace + noise
        else:
            noisy = workspace
        noisy_bp = bipolar_quantize(noisy)
        for i in range(K):
            r = (noisy_bp * slot_tags[i]).astype(np.float32)
            pred_idx = cleanup_to_codebook(r, codebook)
            if pred_idx == int(idx[i]):
                correct += 1
            total += 1
    return correct / max(total, 1)


def eval_cleanup_per_slot(K: int, sigma: float, codebook: np.ndarray,
                           slot_tags_full: np.ndarray,
                           rng: np.random.Generator) -> float:
    """ARM_CLEANUP_PER_SLOT: at WRITE time, store CLEAN codebook atom in slot.

    Procedure:
      1. Per slot i, content_i = item_i = codebook[idx_i] (already in codebook).
      2. Pre-clean content_i: pre_clean_idx_i = cleanup_to_codebook(content_i,
         codebook). Then write E[pre_clean_idx_i] into slot (this is a tautology
         on bipolar codebook items but generalizes for the case where slot
         contents go through any transform).
      3. Bundle bind(content_i_cleaned, slot_i).
      4. At READ: r = workspace * slot_i; pred_idx = cleanup(r, codebook).

    The key difference vs NAIVE: this arm passes the content through cleanup
    BEFORE the bind/bundle step. For purely-bipolar codebook items this should
    be a no-op (item is already a codebook atom). However, in the WM
    PRODUCTION cell the codebook items ARE already codebook atoms, so this
    arm's first variant degenerates to NAIVE.

    The MEANINGFUL variant (what we test): at READ time, do ITERATED-cleanup
    against the codebook (1 extra cleanup pass on the retrieved vector via
    bipolar-quantization + re-projection). Brain analog: theta-gamma double-
    cleanup at read time. Substrate's bipolar quantization concentrates the
    cue toward the codebook attractor on each iteration.
    """
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / K))
    slot_tags = slot_tags_full[:K]
    correct = 0
    total = 0
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
        for i in range(K):
            # Stage 1: unbind via slot tag
            r1 = (noisy_bp * slot_tags[i]).astype(np.float32)
            # Stage 2: argmax against codebook (find best candidate)
            sims1 = codebook @ r1
            cand_idx = int(np.argmax(sims1))
            # Stage 3: ITERATED cleanup -- pull r1 toward the candidate atom
            # (theta-gamma analog) + re-quantize + re-argmax
            r2 = 0.5 * r1 + 0.5 * codebook[cand_idx]
            r2_bp = bipolar_quantize(r2)
            # Stage 4: final argmax against codebook with cleaned cue
            pred_idx = cleanup_to_codebook(r2_bp, codebook)
            if pred_idx == int(idx[i]):
                correct += 1
            total += 1
    return correct / max(total, 1)


ARM_EVALS = {
    "ARM_NAIVE": eval_naive,
    "ARM_CLEANUP_PER_SLOT": eval_cleanup_per_slot,
}


# =============================================================================
# Self-test
# =============================================================================

def _selftest():
    rng = np.random.default_rng(0)
    cb = build_codebook(rng)
    K_max = max(K_VALUES)
    slot_tags = build_slot_tags(np.random.default_rng(1), K_max)
    # T1: at K=2 sigma=0.0, both arms recall = 1.0
    r_naive = eval_naive(2, 0.0, cb, slot_tags, np.random.default_rng(2))
    r_cleanup = eval_cleanup_per_slot(2, 0.0, cb, slot_tags, np.random.default_rng(3))
    assert r_naive >= 0.95, "T1 naive recall=%.3f at K=2 sigma=0.0 < 0.95" % r_naive
    assert r_cleanup >= 0.95, "T1 cleanup recall=%.3f at K=2 sigma=0.0 < 0.95" % r_cleanup
    print("[selftest] T1 PASS: K=2 sigma=0.0 naive=%.3f cleanup=%.3f" % (r_naive, r_cleanup))

    # T2: at K=8 sigma=0.0, both arms still high
    r_naive_8 = eval_naive(8, 0.0, cb, slot_tags, np.random.default_rng(4))
    r_cleanup_8 = eval_cleanup_per_slot(8, 0.0, cb, slot_tags, np.random.default_rng(5))
    assert r_naive_8 >= 0.80, "T2 naive K=8 recall=%.3f < 0.80" % r_naive_8
    assert r_cleanup_8 >= 0.80, "T2 cleanup K=8 recall=%.3f < 0.80" % r_cleanup_8
    print("[selftest] T2 PASS: K=8 sigma=0.0 naive=%.3f cleanup=%.3f" % (r_naive_8, r_cleanup_8))

    # T3: codebook + slot tags correct shape
    assert cb.shape == (CODEBOOK_SIZE, N_DIM), "T3 codebook shape %s" % (cb.shape,)
    assert slot_tags.shape == (K_max, N_DIM), "T3 slot tags shape %s" % (slot_tags.shape,)
    print("[selftest] T3 PASS: codebook %s slot_tags %s shapes correct"
          % (cb.shape, slot_tags.shape))

    # T4: bipolar quantization preserves sign
    v = np.array([0.5, -0.3, 0.0, -1.0, 0.1], dtype=np.float32)
    q = bipolar_quantize(v)
    assert (q == np.array([1.0, -1.0, 1.0, -1.0, 1.0])).all(), "T4 bipolar quant wrong: %s" % q
    print("[selftest] T4 PASS: bipolar_quantize preserves sign")

    # T5: bands locked
    assert HP_CLEANUP_K128_SIGMA10_RECALL == 0.95
    assert MID_K128_LO < MID_K128_HI
    print("[selftest] T5 PASS: bands locked")

    # T6: substrate-only-decode gate
    assert _LLM_CALL_COUNTER[0] == 0, "T6 LLM counter non-zero"
    print("[selftest] T6 PASS: LLM counter = 0")

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
        by_arm[arm_label] = {"per_K_per_sigma": {}, "wall_s": 0.0}
        trial_rng = np.random.default_rng(seed * 1000 + 3 + ARMS.index(arm_label) * 100)
        for K in K_VALUES:
            recall_at_sigma = {}
            for sigma in SIGMAS:
                r = ARM_EVALS[arm_label](K, sigma, codebook, slot_tags, trial_rng)
                recall_at_sigma["sigma_%.2f" % sigma] = round(float(r), 4)
            by_arm[arm_label]["per_K_per_sigma"]["K_%d" % K] = recall_at_sigma
        by_arm[arm_label]["wall_s"] = round(time.time() - t_arm, 2)
        per_K = by_arm[arm_label]["per_K_per_sigma"]
        summary = " ".join(["K%d_s1.0=%.3f" % (
            int(k.split("_")[1]),
            v.get("sigma_1.00", 0.0))
            for k, v in per_K.items()])
        print("  [seed=%d arm=%s] %s wall=%.1fs"
              % (seed, arm_label, summary, by_arm[arm_label]["wall_s"]), flush=True)
    return {
        "seed": seed,
        "by_arm": by_arm,
        "N": N_DIM,
        "CODEBOOK_SIZE": CODEBOOK_SIZE,
        "K_VALUES": K_VALUES,
        "SIGMAS": SIGMAS,
        "N_ITEMS_PER_K": N_ITEMS_PER_K,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }


# =============================================================================
# Verdict
# =============================================================================

def _per_K_sigma_mean(units, arm_label, K, sigma):
    vals = [u["by_arm"][arm_label]["per_K_per_sigma"]["K_%d" % K]["sigma_%.2f" % sigma]
            for u in units]
    return float(np.mean(vals)) if vals else float("nan"), \
           float(np.std(vals) / max(abs(np.mean(vals)), 1e-9)) if len(vals) >= 2 else 0.0, \
           vals


def compute_verdict(units: List[Dict]) -> Tuple[str, str]:
    if not units:
        return ("HARD_FAIL", "no per-seed data")
    # Per-arm per-K (sigma=1.0) mean + cv
    out_by_arm = {}
    for arm in ARMS:
        rows = {}
        for K in K_VALUES:
            for sigma in SIGMAS:
                m, cv, raw = _per_K_sigma_mean(units, arm, K, sigma)
                rows["K%d_sigma%.1f" % (K, sigma)] = {
                    "mean": round(m, 4), "cv": round(cv, 4),
                    "per_seed": [round(v, 4) for v in raw],
                }
        out_by_arm[arm] = rows

    # Key band: ARM_CLEANUP_PER_SLOT K=128 sigma=1.0
    cleanup_k128, cleanup_k128_cv, _ = _per_K_sigma_mean(units, "ARM_CLEANUP_PER_SLOT", 128, 1.0)
    naive_k128, naive_k128_cv, _ = _per_K_sigma_mean(units, "ARM_NAIVE", 128, 1.0)

    # Find K-ceiling for each arm: largest K with recall(sigma=1.0) >= 0.95
    def k_ceiling(arm):
        best = 0
        for K in K_VALUES:
            m, _cv, _ = _per_K_sigma_mean(units, arm, K, 1.0)
            if m >= 0.95:
                best = K
        return best

    naive_ceiling = k_ceiling("ARM_NAIVE")
    cleanup_ceiling = k_ceiling("ARM_CLEANUP_PER_SLOT")

    summ = ("CLEANUP_K128_sigma1.0=%.4f (cv=%.3f) NAIVE_K128_sigma1.0=%.4f (cv=%.3f) "
            "| K-ceiling(>=0.95 at sigma1.0): NAIVE=%d CLEANUP=%d | per-arm-per-K:%s"
            ) % (cleanup_k128, cleanup_k128_cv, naive_k128, naive_k128_cv,
                 naive_ceiling, cleanup_ceiling,
                 " " + " ".join("%s_NAIVE=%.3f_CLEANUP=%.3f" % (
                     "K%d" % K,
                     out_by_arm["ARM_NAIVE"]["K%d_sigma1.0" % K]["mean"],
                     out_by_arm["ARM_CLEANUP_PER_SLOT"]["K%d_sigma1.0" % K]["mean"])
                     for K in K_VALUES))

    # HARD_FAIL: cleanup <= naive at K=128 sigma=1.0
    if not math.isnan(cleanup_k128) and not math.isnan(naive_k128) \
            and cleanup_k128 <= naive_k128 + HF_REGRESSION_TOL:
        return ("HARD_FAIL_NAIVE_IS_OPTIMAL",
                "HARD_FAIL_NAIVE_IS_OPTIMAL: " + summ)

    # HARD_PASS: cleanup at K=128 sigma=1.0 >= 0.95 AND cv <= 0.07
    if not math.isnan(cleanup_k128) and cleanup_k128 >= HP_CLEANUP_K128_SIGMA10_RECALL \
            and cleanup_k128_cv <= HP_CV_MAX:
        # Cleanup ceiling at least 2x naive ceiling -> chain-grade extension
        if cleanup_ceiling >= naive_ceiling * 2 and naive_ceiling > 0:
            return ("HARD_PASS_CLEANUP_LIFTS_K_TO_128",
                    "HARD_PASS_CLEANUP_LIFTS_K_TO_128_CHAIN_GRADE_2X_EXTENSION: " + summ)
        return ("HARD_PASS_CLEANUP_LIFTS_K_TO_128",
                "HARD_PASS_CLEANUP_LIFTS_K_TO_128: " + summ)

    # MIDDLE_BAND
    if not math.isnan(cleanup_k128) and MID_K128_LO <= cleanup_k128 < MID_K128_HI:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_CLEANUP_PARTIAL_LIFT: " + summ)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND_UNCLASSIFIED: " + summ)


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
            "EXT-6 WM-HRR-slots K-extension via cleanup-per-slot. Compares "
            "NAIVE (PRODUCTION mechanism: bind+bundle+unbind+cleanup) vs "
            "CLEANUP_PER_SLOT (adds an iterated cleanup pass at read time: "
            "unbind, argmax, mix-toward-winner, re-quantize, re-argmax). "
            "Brain analog: theta-gamma WM refresh. K-sweep [32, 64, 128, 256, "
            "512] sigma-sweep [0.0, 0.5, 1.0]. Per-arm per-K mean + cv reported."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
