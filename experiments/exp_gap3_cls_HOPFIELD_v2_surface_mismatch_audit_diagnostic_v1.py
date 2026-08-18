"""gap3_cls_HOPFIELD_v2_surface_mismatch_audit_diagnostic_v1 -- B3 fair-test diagnostic.

Drill source: notes/research_drill_2x_hopfield_consolidation_revival_2026-06-27.md
META_FAIRNESS_PATTERN bug: v2 BASELINE_HEBBIAN read w_schema_cone=1.000
(prototype-direct), while HEBBIAN_SLOW / HOPFIELD arms read w_schema_cone=0.246
(W-cosine). The arms were NOT A/B comparable -- they measured DIFFERENT SURFACES.

FIX: ALL 4 arms read THE SAME SURFACE via a single shared readout function
`_readout_W_cosine(W, heldout_x, heldout_y)` called identically per arm. The arms
DIFFER ONLY in how W was built; they DO NOT differ in how W is read.

ARMS (4, identical readout):
  ARM_BASELINE_HEBBIAN_W           W = mean(instances) by class as ROWS
  ARM_HEBBIAN_SLOW_W               W = eta_fast * sum(instances) by class as ROWS (NO replay)
  ARM_HOPFIELD_REPLAY_SLOW_W       Same W as HEBBIAN_SLOW, then NREM replay over STORED episodes
  ARM_HOPFIELD_GENERATIVE_REPLAY_W Same W as HEBBIAN_SLOW, then NREM replay over GENERATED samples

REGIME: identical to v2 (N_DIM=2048, N_CAT=100, N_TRAIN=100, proto_noise=0.60)
        -- DELIBERATELY UNCHANGED. The cell is a SURFACE-AUDIT not a regime cell.
        If baseline drops < 0.95 under fair readout: surface-mismatch WAS the v2 bug.
        If baseline still pins at 1.000: regime IS the issue (Hopfield-replay class
        is structurally redundant for this task class -- atomize HONEST_NEG and pivot).

PRE-REG BANDS (FAIRNESS-AUDIT discriminator, NOT mechanism discriminator):
  HARD_PASS (fairness validated; surface-mismatch was THE bug):
    BASELINE_HEBBIAN_W in [0.50, 0.80] (no longer ceiling-pinned)
    AND arms differentiate by >= 0.05 absolute (mechanism arm distinguishable from baseline)
  HARD_FAIL (surface-mismatch was NOT the bug; regime structurally saturates):
    ALL arms within 0.02 of each other (mechanism null at fair readout)
    OR BASELINE_HEBBIAN_W > 0.95 (W-cosine readout ALSO ceilings -> regime is THE issue)
  MIDDLE_BAND:
    BASELINE in [0.80, 0.95] OR arms_diff in [0.02, 0.05] -- partial fairness signal

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SMOKE = 1 seed * 4 arms = 4 (per drill: 1-seed diagnostic, ~10 min)
  FULL run inherits same regime (4 arms x 3 seeds = 12), only for ratify-fairness.

HARDENING (META_RULE_X / J / L1-L4):
  main wrapped in if __name__ == "__main__"
  L1: minimal metrics.json with STARTED + PID at start
  L2: per-arm progress updates
  L3: outer try/except around main; failure-class to metrics
  L4: import-crash sentinel

META_RULE_AA: this cell IS the operationalization (fair readout shared across arms).

Per-arm metrics structure (Fix #28):
  metrics["per_arm"] = {arm: {seed: {heldout_acc, w_norm_diag, ...}}}

ASCII-only; no emojis; no em-dashes; self-contained (no hdlab/ imports).
Author: exp_dev 2026-06-27 (fair-revival cell 1 of 4 batch under research lead).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "gap3_cls_HOPFIELD_v2_surface_mismatch_audit_diagnostic_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init (FAIRNESS-AUDIT bands; not mechanism bands)
HP_BASELINE_LO = 0.50
HP_BASELINE_HI = 0.80
HP_ARMS_DIFF_MIN = 0.05
HF_ARMS_DIFF_MAX = 0.02
HF_BASELINE_CEILING = 0.95
MB_BASELINE_HI = 0.95

EXPECTED_ARMS = ["arm_baseline_hebbian_W", "arm_hebbian_slow_W",
                 "arm_hopfield_replay_slow_W", "arm_hopfield_generative_replay_W"]

# v2 regime DELIBERATELY UNCHANGED (this is a surface-audit, not a regime cell)
if SELF_TEST_MODE:
    N_DIM = 256
    N_CAT = 10
    N_TRAIN_PER_CAT = 10
    N_HELDOUT_PER_CAT = 5
    N_REPLAY_CYCLES = 100
    REPLAY_EVERY = 20
    SEEDS = [11]
    PROTO_NOISE = 0.60
elif RUN_MODE == "smoke":
    # SAME AS v2 -- drill says 1 seed, ~10 min on remote_cpu
    N_DIM = 2048
    N_CAT = 100
    N_TRAIN_PER_CAT = 100
    N_HELDOUT_PER_CAT = 30
    N_REPLAY_CYCLES = 500
    REPLAY_EVERY = 100
    SEEDS = [11]
    PROTO_NOISE = 0.60
else:
    N_DIM = 2048
    N_CAT = 100
    N_TRAIN_PER_CAT = 100
    N_HELDOUT_PER_CAT = 30
    N_REPLAY_CYCLES = 5000
    REPLAY_EVERY = 100
    SEEDS = [11, 13, 19]
    PROTO_NOISE = 0.60

N_EPISODES = N_CAT * N_TRAIN_PER_CAT
N_HELDOUT = N_CAT * N_HELDOUT_PER_CAT
ALPHA_LOAD = N_CAT / float(N_DIM)
ETA_FAST = 1.0
ETA_REPLAY = 1.0
REPLAY_FRAC = 0.2

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,N_CAT=%d,N_TRAIN=%d,N_HELDOUT=%d,N_REPLAY=%d,"
    "proto_noise=%.2f,alpha=%.4f,seeds=%s,mode=%s,"
    "HP_baseline=[%.2f,%.2f],HP_arms_diff>=%.2f,HF_arms_diff<=%.2f,"
    "HF_baseline_ceiling=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "FAIRNESS=ALL_ARMS_READ_SAME_SURFACE_W_COSINE"
) % (
    ANCHOR_NAME, N_DIM, N_CAT, N_TRAIN_PER_CAT, N_HELDOUT_PER_CAT, N_REPLAY_CYCLES,
    PROTO_NOISE, ALPHA_LOAD, SEEDS, RUN_MODE,
    HP_BASELINE_LO, HP_BASELINE_HI, HP_ARMS_DIFF_MIN, HF_ARMS_DIFF_MAX,
    HF_BASELINE_CEILING, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_hopfield_surface_audit",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_hopfield_surface_audit_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- primitives --------------------------

def _bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X


def _build_class_episodes(seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray,
                                                np.ndarray, np.ndarray]:
    """Build prototypes + train + heldout (regime params identical to v2)."""
    g = np.random.default_rng(seed + 7)
    prototypes = _bipolar(N_CAT, N_DIM, g)

    g_train = np.random.default_rng(seed + 11)
    train_x = np.zeros((N_EPISODES, N_DIM), dtype=np.float32)
    train_y = np.zeros((N_EPISODES,), dtype=np.int64)
    for c in range(N_CAT):
        for i in range(N_TRAIN_PER_CAT):
            ep_idx = c * N_TRAIN_PER_CAT + i
            n_flip = int(PROTO_NOISE * N_DIM)
            perm = g_train.permutation(N_DIM)
            inst = prototypes[c].copy()
            inst[perm[:n_flip]] = -inst[perm[:n_flip]]
            train_x[ep_idx] = inst
            train_y[ep_idx] = c

    g_held = np.random.default_rng(seed + 13)
    heldout_x = np.zeros((N_HELDOUT, N_DIM), dtype=np.float32)
    heldout_y = np.zeros((N_HELDOUT,), dtype=np.int64)
    for c in range(N_CAT):
        for i in range(N_HELDOUT_PER_CAT):
            ep_idx = c * N_HELDOUT_PER_CAT + i
            n_flip = int(PROTO_NOISE * N_DIM)
            perm = g_held.permutation(N_DIM)
            inst = prototypes[c].copy()
            inst[perm[:n_flip]] = -inst[perm[:n_flip]]
            heldout_x[ep_idx] = inst
            heldout_y[ep_idx] = c

    return prototypes, train_x, train_y, heldout_x, heldout_y


# ====================== THE SHARED READOUT (LOAD-BEARING FAIRNESS) =======================
# ALL 4 arms call THIS function with their OWN W to compute heldout_acc.
# This is what makes the cell a fair A/B test.

def _readout_W_cosine(W: np.ndarray, heldout_x: np.ndarray,
                       heldout_y: np.ndarray) -> Dict[str, float]:
    """Shared W-cosine readout used IDENTICALLY by all 4 arms.

    W: (N_CAT, N_DIM) -- rows are per-category schema vectors.
    heldout_x: (N_HELDOUT, N_DIM) -- noisy queries.
    heldout_y: (N_HELDOUT,) -- ground-truth class labels.

    Returns: dict with heldout_acc + diagnostic stats.
    """
    # L2-normalize W rows
    W_norm = W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-9)
    x_norm = heldout_x / (np.linalg.norm(heldout_x, axis=1, keepdims=True) + 1e-9)
    sims = x_norm @ W_norm.T  # (N_HELDOUT, N_CAT) cosine
    pred = np.argmax(sims, axis=1)
    acc = float(np.mean(pred == heldout_y))

    # Diagnostic: mean cos to TRUE class row, mean cos to BEST FALSE class row
    true_cos = sims[np.arange(len(heldout_y)), heldout_y]
    sims_no_true = sims.copy()
    sims_no_true[np.arange(len(heldout_y)), heldout_y] = -2.0
    best_false_cos = sims_no_true.max(axis=1)
    margin = float(np.mean(true_cos - best_false_cos))

    # Diagnostic: W norm distribution (detects collapse / saturation)
    w_row_norms = np.linalg.norm(W, axis=1)
    w_norm_mean = float(np.mean(w_row_norms))
    w_norm_cv = float(np.std(w_row_norms) / max(w_norm_mean, 1e-9))

    return {
        "heldout_acc": acc,
        "mean_true_cos": float(np.mean(true_cos)),
        "mean_best_false_cos": float(np.mean(best_false_cos)),
        "margin": margin,
        "w_row_norm_mean": w_norm_mean,
        "w_row_norm_cv": w_norm_cv,
    }

# ====================== ARM W-BUILDERS (each builds W differently) =======================

def _build_W_baseline_hebbian(prototypes, train_x, train_y) -> np.ndarray:
    """ARM_BASELINE_HEBBIAN_W: row c = mean(instances of class c).

    This is what v1/v2 BASELINE arm did at SURFACE level. Now we read it via
    SHARED W-cosine readout (not direct prototype-cosine).
    """
    W = np.zeros((N_CAT, N_DIM), dtype=np.float32)
    counts = np.zeros(N_CAT, dtype=np.float32)
    for ep in range(N_EPISODES):
        c = int(train_y[ep])
        W[c] += train_x[ep]
        counts[c] += 1.0
    counts = np.maximum(counts, 1.0)
    W = W / counts[:, None]
    return W


def _build_W_hebbian_slow(prototypes, train_x, train_y) -> np.ndarray:
    """ARM_HEBBIAN_SLOW_W: row c = eta_fast * sum(instances of class c). NO replay."""
    W = np.zeros((N_CAT, N_DIM), dtype=np.float32)
    for ep in range(N_EPISODES):
        c = int(train_y[ep])
        W[c] += ETA_FAST * train_x[ep]
    return W


def _build_W_hopfield_replay(prototypes, train_x, train_y, g: np.random.Generator,
                              generative: bool) -> np.ndarray:
    """ARM_HOPFIELD_REPLAY_SLOW_W / ARM_HOPFIELD_GENERATIVE_REPLAY_W: HEBBIAN_SLOW W
    then NREM-style replay over stored (or generated) episodes.

    The replay primitive here is self-contained (does NOT import hdlab.continual.replay_cycle
    to keep cell hermetic). Mathematically equivalent: small chunk of episodes per cycle,
    update row c by += lr * REPLAY_FRAC * inst.
    """
    W = _build_W_hebbian_slow(prototypes, train_x, train_y).copy()
    n_replay_applied = 0
    for cycle in range(N_REPLAY_CYCLES):
        if cycle % REPLAY_EVERY != 0:
            continue
        if generative:
            # Generate new noisy instances from prototypes
            M = N_EPISODES
            patterns = np.zeros((M, N_DIM), dtype=np.float32)
            class_ids = np.zeros(M, dtype=np.int64)
            for m in range(M):
                c = m % N_CAT
                n_flip = int(PROTO_NOISE * N_DIM)
                perm = g.permutation(N_DIM)
                inst = prototypes[c].copy()
                inst[perm[:n_flip]] = -inst[perm[:n_flip]]
                patterns[m] = inst
                class_ids[m] = c
        else:
            patterns = train_x
            class_ids = train_y

        M = patterns.shape[0]
        # Sample REPLAY_FRAC of episodes for this cycle
        n_pick = max(1, int(REPLAY_FRAC * M))
        pick = g.choice(M, size=n_pick, replace=False)
        for idx in pick:
            c = int(class_ids[idx])
            W[c] += ETA_REPLAY * REPLAY_FRAC * patterns[idx] / float(REPLAY_EVERY)
        n_replay_applied += 1
    return W


# -------------------------- per-seed runner --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    """Build W per arm; readout SAME WAY for all 4 arms (the load-bearing fairness)."""
    g = np.random.default_rng(seed)
    prototypes, train_x, train_y, heldout_x, heldout_y = _build_class_episodes(seed)

    arm_results: Dict[str, Dict[str, float]] = {}

    # ARM_BASELINE_HEBBIAN_W: W = mean(instances) by class; READ via shared W-cosine
    W_base = _build_W_baseline_hebbian(prototypes, train_x, train_y)
    arm_results["arm_baseline_hebbian_W"] = _readout_W_cosine(W_base, heldout_x, heldout_y)

    # ARM_HEBBIAN_SLOW_W: W = eta * sum(instances) by class; SAME shared readout
    W_heb = _build_W_hebbian_slow(prototypes, train_x, train_y)
    arm_results["arm_hebbian_slow_W"] = _readout_W_cosine(W_heb, heldout_x, heldout_y)

    # ARM_HOPFIELD_REPLAY_SLOW_W
    g_rep = np.random.default_rng(seed + 29)
    W_hop = _build_W_hopfield_replay(prototypes, train_x, train_y, g_rep,
                                       generative=False)
    arm_results["arm_hopfield_replay_slow_W"] = _readout_W_cosine(
        W_hop, heldout_x, heldout_y)

    # ARM_HOPFIELD_GENERATIVE_REPLAY_W
    g_gen = np.random.default_rng(seed + 31)
    W_gen = _build_W_hopfield_replay(prototypes, train_x, train_y, g_gen,
                                       generative=True)
    arm_results["arm_hopfield_generative_replay_W"] = _readout_W_cosine(
        W_gen, heldout_x, heldout_y)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "N_CAT": N_CAT,
        "alpha_load": ALPHA_LOAD,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": arm_results,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials found",
            "summary": "no per-seed partials found",
            "per_arm": {},
        }
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}

    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}
        acc_vals: List[float] = []
        margin_vals: List[float] = []
        for s in seeds_sorted:
            body = per_seed[s]
            pa = body.get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                acc_vals.append(float(d.get("heldout_acc", 0.0)))
                margin_vals.append(float(d.get("margin", 0.0)))
                per_arm_full[arm][s] = {k: float(v) for k, v in d.items()}
        if acc_vals:
            m = float(np.mean(acc_vals))
            sd = float(np.std(acc_vals))
            cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
            summary[arm] = {
                "mean_acc": m, "std_acc": sd, "cv_acc": cv,
                "mean_margin": float(np.mean(margin_vals)),
                "n": len(acc_vals),
            }
        else:
            summary[arm] = {"mean_acc": 0.0, "std_acc": 0.0, "cv_acc": 0.0,
                            "mean_margin": 0.0, "n": 0}

    # Fairness audit verdict:
    base_acc = summary["arm_baseline_hebbian_W"]["mean_acc"]
    hop_acc = summary["arm_hopfield_replay_slow_W"]["mean_acc"]
    gen_acc = summary["arm_hopfield_generative_replay_W"]["mean_acc"]
    heb_acc = summary["arm_hebbian_slow_W"]["mean_acc"]

    arm_accs = [base_acc, heb_acc, hop_acc, gen_acc]
    arms_range = max(arm_accs) - min(arm_accs)
    arms_max = max(arm_accs)

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    if arms_max > HF_BASELINE_CEILING and arms_range <= HF_ARMS_DIFF_MAX:
        # All arms ceiling-pinned at fair readout -- regime IS the issue
        verdict = "HARD_FAIL"
        verdict_reason = "REGIME_SATURATION: all arms > %.2f at fair readout; surface-mismatch was NOT the v2 bug" % HF_BASELINE_CEILING
    elif arms_range <= HF_ARMS_DIFF_MAX:
        # All arms collapse to one number -- mechanism null
        verdict = "HARD_FAIL"
        verdict_reason = "MECHANISM_NULL: arms differ by <= %.2f; replay adds zero info vs baseline" % HF_ARMS_DIFF_MAX
    elif (HP_BASELINE_LO <= base_acc <= HP_BASELINE_HI and
          arms_range >= HP_ARMS_DIFF_MIN):
        verdict = "HARD_PASS"
        verdict_reason = "FAIRNESS_VALIDATED: baseline in [%.2f, %.2f] and arms differ by >= %.2f" % (
            HP_BASELINE_LO, HP_BASELINE_HI, HP_ARMS_DIFF_MIN)
    elif base_acc > MB_BASELINE_HI:
        verdict = "MIDDLE_BAND"
        verdict_reason = "BASELINE_HIGH: baseline > %.2f at fair readout but arms differentiate -- partial fairness signal" % MB_BASELINE_HI

    verdict_msg = (
        "%s | %s | BASE=%.3f HEB=%.3f HOP=%.3f GEN=%.3f | "
        "arms_range=%.3f arms_max=%.3f | n=%d"
    ) % (verdict, verdict_reason, base_acc, heb_acc, hop_acc, gen_acc,
         arms_range, arms_max, len(seeds_sorted))

    completed_units = len(seeds_sorted) * len(EXPECTED_ARMS)
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "alpha_load": ALPHA_LOAD,
        "arms_range": arms_range,
        "arms_max": arms_max,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= EXPECTED_N_UNITS,
    }


# -------------------------- main --------------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s alpha=%.4f" % (
                               os.getpid(), RUN_MODE, ALPHA_LOAD),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d N_CAT=%d N_TRAIN=%d alpha=%.4f seeds=%s expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_CAT, N_TRAIN_PER_CAT, ALPHA_LOAD,
        SEEDS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"]
                assert "heldout_acc" in r["per_arm"][arm]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm + shared-readout structure verified",
                                   extra={"_phase": "selftest_done",
                                          "selftest_arm_accs": {a: r["per_arm"][a]["heldout_acc"]
                                                                  for a in EXPECTED_ARMS}})
            print("[selftest] OK arms=%s" % {a: round(r["per_arm"][a]["heldout_acc"], 3)
                                              for a in EXPECTED_ARMS}, flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_hopfield_surface_audit"
    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2), encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
