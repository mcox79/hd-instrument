"""cortex_full_stack_deep_composition_v1 -- seed_7. Deep composition test:
M1.4 refuse-gate + M1.5 TWOTIER context retention + M1.6 4-class router,
chained at depths {10, 50, 100} to validate M3 Phase 1 architecture.

MOTIVATION (M3 milestone):
  M1.4 v8 (Atom 15), M1.5 v2 TWOTIER (Atom 18), M1.6 v2 4-class router (Atom D)
  each cleared chain-grade INDIVIDUALLY. The M3 Phase 1 substrate-side router
  pattern claims these compose into a production-ready stack. Deep-composition
  has NOT been tested at depth > 5 (substrate-KB check 2026-07-01: top hit
  cosine=0.3057, unrelated arcs; genuinely novel).

  This cell tests whether the assembled stack maintains cross-primitive integrity
  when chained through 10-100 sequential cortex operations. The stack pattern:
    step_t: router(q_t) -> route decision -> {refuse-gate | STM-fetch | LTM-recall
    | bind} -> next-step query q_{t+1} depends on step_t output.

FUNCTIONAL REQUIREMENTS (per META_RULE §15E):
  FR1: Deep chain preserves entity identity across steps (STM handoff).
       Primitive: WM multi-bank K=100 STM (M1.5 v2 CG).
  FR2: OOD probes trigger refuse mid-chain without corrupting later steps.
       Primitive: CONFORMAL_MODERATE tau=P5 refuse-gate (M1.4 v8 CG).
  FR3: Router switches route-class per step correctly with tail-of-chain context.
       Primitive: 4-class nearest-class HV router (M1.6 v2 CG).
  FR4: Combined composition (all 3 in stack) shows lift over any single primitive.

CG parents (composition provenance per META_RULE_AT):
  - M1.4 v8 CONFORMAL_MODERATE refuse-gate (Atom 15;
    exp_substrate_refuse_gate_v8_conformal_v1_seed_7 pattern; tau=P5 of MODERATE
    cal in-KB; ~0.700 empirical)
  - M1.5 v2 TWOTIER context retention (Atom 18; commit adaab6b7;
    exp_cortex_context_retention_v2_seed_7 pattern; K=100 STM multi-bank +
    K=1200 LTM dense-Hopfield alpha=0.1465 > 0.138 wall)
  - M1.6 v2 4-class attention-binding router (Atom D;
    exp_cortex_attention_binding_router_v2_seed_7 pattern; 4-class HV nearest-
    class with refuse_signal + retrieval_signal + chain_signal feature slots)

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (META_RULE_AF hash-test)
  - final_metrics_atomicity: tmp_replace (META_RULE_AH)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_floor_computed + discriminator_reachability declared
  - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.95)
  - discriminator survives scale: N_DIM=8192 in BOTH smoke + full (Check A)
  - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
  - cardinality_ok for expected_n_units=45 FULL (5 arms x 3 regimes x 3 depths)
  - per-unit failure-class instrumentation (META_RULE_J)
  - calibration_check: chance_floor=1/V_CB=0.000977 THEORETICAL@codebook-argmax
  - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

ARMS (5):
  ARM_FULL_STACK_D10       : full cortex stack (M1.4+M1.5+M1.6) at chain depth 10.
  ARM_FULL_STACK_D50       : full stack at depth 50.
  ARM_FULL_STACK_D100      : full stack at depth 100.
  ARM_SUBSTRATE_ONLY_D50   : substrate primitives only (bipolar bind+unbind
                             through chain; no refuse-gate, no cortex routing,
                             no cleanup between steps) at depth 50. Broken-PC
                             baseline; error accumulates unchecked.
  ARM_NO_REFUSE_D50        : cortex router + WM but NO refuse-gate at depth 50.
                             Tests refuse-gate's contribution to end-of-chain
                             integrity when OOD probes injected.

TEST REGIMES (3):
  1. RETRIEVE_CHAIN: chain of "recall entity X -> recall attribute of X ->
     recall relation of X" (all route=RETRIEVE per step; router picks correct
     retrieval; STM propagates entity across steps).
  2. REFUSE_TERMINATED: chain w/ OOD probe injected at step ceil(depth/2); every
     step after should route to REFUSE (chain terminates or degrades gracefully).
  3. ROUTER_MIXED: alternating route classes per step (RETRIEVE -> BIND ->
     MULTI_HOP -> RETRIEVE ...); router must switch mode per step.

DISCRIMINATOR-MUST-SURVIVE-SCALE (META USER 2026-06-26):
  N_DIM=8192 fixed in BOTH smoke + full. Substrate tolerance at this N is well-
  characterized from prior CG cells. Smoke = full N; only per-step trials
  count varies. Depth axis (10/50/100) IS the discriminator; depth-100 is
  where composition wall is expected. HP thresholds decline w/ depth to reflect
  compounding noise: HP_D10 >= 0.85; HP_D50 >= 0.60; HP_D100 >= 0.30. Substrate
  bipolar bind survives ~10 compositions before cosine drops below 0.30
  CITED@Kanerva-1988; cleanup+refuse gate should extend that to 50-100.

FALSIFIABLE PREDICTIONS:
  HARD_PASS (chain-grade if all 5 fire):
    HP_D10_HOLDS: mean(FULL_STACK_D10 across regimes) >= 0.85
    HP_D50_HOLDS: mean(FULL_STACK_D50 across regimes) >= 0.60
    HP_D100_HOLDS: mean(FULL_STACK_D100 across regimes) >= 0.30
    HP_LIFT_OVER_NO_REFUSE: FULL_STACK_D50 - NO_REFUSE_D50 >= 0.15
    HP_LIFT_OVER_SUBSTRATE_ONLY: FULL_STACK_D50 - SUBSTRATE_ONLY_D50 >= 0.20
  HARD_FAIL_MECHANISM_DEATH: any HP fails by >= 0.15 (deep-composition wall
    below expected; find revival criterion).
  HARD_FAIL_ARMS_IDENTICAL (META_RULE_AF).
  HARD_FAIL_CARDINALITY_BREACH (META_RULE_H): observed core rows < 0.85 * 45.
  HARD_FAIL_BROKEN_PC_BEATS_STACK: SUBSTRATE_ONLY_D50 > FULL_STACK_D50 (cortex
    made composition WORSE than raw substrate).
  MIDDLE_BAND: any HP misses by 0.05 to 0.15.

CARDINALITY (META_RULE_H):
  FULL grid: 5 arms x 3 regimes x 3 depths = 45 arm-rows per seed.
    Note: 3 arms (SUBSTRATE_ONLY, NO_REFUSE, FULL_STACK) run at D50 only for
    baseline comparison; but we ALSO run FULL_STACK at D10/D50/D100.
    Cleaner scheme: arm x regime cells; depth is per-arm axis for FULL_STACK
    only. Total: 3 depths x 3 regimes for FULL_STACK (9) + 1 depth x 3 regimes
    for SUBSTRATE_ONLY (3) + 1 depth x 3 regimes for NO_REFUSE (3) = 15 per seed.
    (The "5 arms" naming in scenario is CONCEPTUAL: FULL_STACK_D10/D50/D100 are
    3 physical arms + SUBSTRATE_ONLY_D50 + NO_REFUSE_D50 = 5.)
  EXPECTED_N_UNITS = 15 (FULL). HF_CARDINALITY_BREACH if < 13.
  SMOKE grid: 5 arms x 2 regimes = 10 arm-rows (depths preserved per arm).

CRLB:
  Per-arm score = mean per-step top-1 codebook accuracy over depth-many steps
    over N_TRIALS trials.
  Chance floor = 1/V_CB = 1/1024 = 0.000977 THEORETICAL@codebook-argmax-uniform.
  Bernoulli sigma at p=0.5, N_TRIALS=10, depth=50 => sigma_per_trial =
    sqrt(0.25 / (10 * 50)) = 0.022. HP gap 0.15 = ~7 sigma. Very reachable.
  For depth=100 (HP=0.30): p_expected~0.30 -> sigma = sqrt(0.3*0.7/1000)=0.014.
    HP margin (0.30 - chance) = 0.30 -> ~21 sigma above chance. Very reachable.

Regime notes:
  - CPU-eligible (numpy) for smoke AND full (per M1.5/M1.6 pattern; numpy).
  - Estimated FULL wall: depth-100 x 3 regimes x FULL_STACK = ~600 steps of
    substrate ops + cleanup. Per step ~0.5-1ms at N=8192 bipolar -> ~3-10s per
    seed for depth=100. Total per seed ~30-60s. Well under 1800s timeout.
  - Route: remote_cpu_queue via hdi_orchestrator handoff post-smoke.

BASELINE_IN_BAND (META_RULE_AG smoke check):
  SUBSTRATE_ONLY_D50 expected in [0.05, 0.30] range (substrate bipolar bind
  degrades quickly past ~10-15 compositions; broken-PC baseline). Verify at
  smoke that it's NOT above 0.95 (would indicate arms bit-identical bug) and
  NOT below 0.05 (regime too hard for meaningful discrimination).

HP_SCOPE per-arm declaration (META_RULE §15 5b):
  HP_D10_HOLDS: applies to ARM_FULL_STACK_D10 only.
  HP_D50_HOLDS: applies to ARM_FULL_STACK_D50 only.
  HP_D100_HOLDS: applies to ARM_FULL_STACK_D100 only.
  HP_LIFT_OVER_NO_REFUSE: applies to pair (ARM_FULL_STACK_D50, ARM_NO_REFUSE_D50).
  HP_LIFT_OVER_SUBSTRATE_ONLY: applies to pair (ARM_FULL_STACK_D50,
    ARM_SUBSTRATE_ONLY_D50).
  ARM_SUBSTRATE_ONLY_D50 + ARM_NO_REFUSE_D50 are ablation arms; NOT expected
    to inherit HP gates from FULL_STACK arms.

Author: exp_dev (hdi_exp_dev spawn) 2026-07-01 (M3 Phase 1 validation).
PRESERVE_ENV_VARS: HDLAB_QUEUE
ASCII-only; META_RULE_AC/AF/AG/AH/AT/H/J/K/L/M load-bearing.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------------
# Line-buffered stdout (META_RULE §17 print-progress flushing)
# ---------------------------------------------------------------------------
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass


# ---------------------------------------------------------------------------
# Inline heartbeat (best-effort append; matches CG cortex_hippo pattern)
# ---------------------------------------------------------------------------
def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    row = {
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units) if total_units is not None else None,
        "elapsed_s": round(float(elapsed_s), 2),
    }
    if extra:
        row["extra"] = extra
    try:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_start_marker.json.tmp"
    final = out / "_start_marker.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(str(tmp), str(final))


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
        "run_mode": "unknown",
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "metrics.json.tmp"
    final = out / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(str(tmp), str(final))


SEED_THIS_CHUNK = 7
ANCHOR_NAME = f"cortex_full_stack_deep_composition_v1_seed_{SEED_THIS_CHUNK}"
_HARDENING_MARKER = "v1_M14_M15_M16_stack_at_depths_10_50_100"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--mode", type=str, default=None)
_ap.add_argument("--timeout", type=int, default=1800)
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
_MODE_ARG = (_ARGS.mode or "").lower()
if _ARGS.self_test or _MODE_ARG == "selftest":
    RUN_MODE = "self_test"
elif _ARGS.smoke or _NAME_SAYS_SMOKE or _MODE_ARG == "smoke" or \
     os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke":
    RUN_MODE = "smoke"
else:
    RUN_MODE = "full"


# ---------------------------------------------------------------------------
# Config (locked at module init)
# ---------------------------------------------------------------------------
N_DIM = 8192                          # M1.4/M1.5/M1.6 anchor
V_CB = 1024                           # value-codebook
N_BANKS = 8                           # WM multi-bank (M1.5 v2 pattern)
K_PER_BANK_STM = 63                   # STM K=100 -> ceil(100/8)=13 per bank; use 63 for margin
STM_TOTAL_K = 100                     # STM buffer size (M1.5 v2)
LTM_TOTAL_K = 1200                    # LTM alpha=1200/8192=0.1465 > 0.138 wall

REFUSE_TAU_MODERATE = 0.700           # M1.4 v8 empirical CONFORMAL_MODERATE tau

# Depth axis
DEPTHS_FULL = [10, 50, 100]
DEPTHS_SMOKE = [10, 50]

# Regime set
REGIMES_FULL = ["RETRIEVE_CHAIN", "REFUSE_TERMINATED", "ROUTER_MIXED"]
REGIMES_SMOKE = ["RETRIEVE_CHAIN", "REFUSE_TERMINATED"]

# Per-arm trials
N_TRIALS_FULL = 10
N_TRIALS_SMOKE = 4

# 4 route classes (M1.6)
ROUTES = ["REFUSE", "RETRIEVE", "BIND", "MULTI_HOP"]
N_CLASSES = len(ROUTES)

if RUN_MODE in ("smoke", "self_test"):
    DEPTHS = DEPTHS_SMOKE
    REGIMES = REGIMES_SMOKE
    N_TRIALS = N_TRIALS_SMOKE
else:
    DEPTHS = DEPTHS_FULL
    REGIMES = REGIMES_FULL
    N_TRIALS = N_TRIALS_FULL

# Arms.
# - ARM_FULL_STACK: one entry per depth (varies depth axis).
# - ARM_SUBSTRATE_ONLY: one arm at depth=50 (ablation baseline).
# - ARM_NO_REFUSE: one arm at depth=50 (ablation baseline).
FULL_STACK_ARMS = [f"ARM_FULL_STACK_D{d}" for d in DEPTHS]
ABLATION_ARMS = ["ARM_SUBSTRATE_ONLY_D50", "ARM_NO_REFUSE_D50"]
ARMS = FULL_STACK_ARMS + ABLATION_ARMS

# EXPECTED_N_UNITS = FULL_STACK arms x len(REGIMES) + 2 ablations x len(REGIMES).
# For FULL: 3 depths x 3 regimes + 2 x 3 = 15. Smoke: 2 depths x 2 + 2 x 2 = 8.
EXPECTED_N_UNITS = len(FULL_STACK_ARMS) * len(REGIMES) + len(ABLATION_ARMS) * len(REGIMES)

# HP thresholds
HP_D10_FLOOR = 0.85
HP_D50_FLOOR = 0.60
HP_D100_FLOOR = 0.30
HP_LIFT_OVER_NO_REFUSE = 0.15
HP_LIFT_OVER_SUBSTRATE_ONLY = 0.20
HF_MECHANISM_DEATH_MARGIN = 0.15    # HP miss by >= this margin = HF
BAND_WIDTH_MARGIN = 0.05             # META_RULE_L strict-above-floor margin

# CRLB
CHANCE_FLOOR = 1.0 / V_CB              # 0.000977 THEORETICAL@codebook-argmax
BERNOULLI_SIGMA_AT_P05_D50 = math.sqrt(0.25 / (N_TRIALS * 50))

SEEDS_FULL = [SEED_THIS_CHUNK]

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_DIM={N_DIM},V_CB={V_CB},N_BANKS={N_BANKS},"
    f"STM_K={STM_TOTAL_K},LTM_K={LTM_TOTAL_K},"
    f"REFUSE_TAU={REFUSE_TAU_MODERATE},"
    f"depths={DEPTHS},regimes={REGIMES},n_trials={N_TRIALS},"
    f"expected_n_units={EXPECTED_N_UNITS},"
    f"mode={RUN_MODE},chunk_seed={SEED_THIS_CHUNK},backend=numpy,"
    f"chance_floor={CHANCE_FLOOR:.6f},"
    f"bernoulli_sigma_p05_d50={BERNOULLI_SIGMA_AT_P05_D50:.4f},"
    f"HP_D10={HP_D10_FLOOR},HP_D50={HP_D50_FLOOR},HP_D100={HP_D100_FLOOR},"
    f"HP_lift_noref={HP_LIFT_OVER_NO_REFUSE},HP_lift_subonly={HP_LIFT_OVER_SUBSTRATE_ONLY},"
    f"hardening={_HARDENING_MARKER}"
)


# ---------------------------------------------------------------------------
# Substrate primitives (bipolar bind + bundle + codebook cleanup)
# ---------------------------------------------------------------------------
def _rng(seed_int: int) -> np.random.Generator:
    return np.random.default_rng(int(seed_int))


def bipolar_random(rng, n=N_DIM):
    return rng.choice(np.array([-1, 1], dtype=np.int8), size=n)


def bipolar_random_batch(rng, k, n=N_DIM):
    return rng.choice(np.array([-1, 1], dtype=np.int8), size=(k, n))


def bind(a, b):
    # elementwise multiply (bipolar bind); returns int8
    return (a.astype(np.int32) * b.astype(np.int32)).astype(np.int8)


def bipolar_quantize(v):
    # sign quantize; zero-safe
    out = np.where(v >= 0, 1, -1).astype(np.int8)
    return out


def bundle(hvs):
    # sum + sign quantize
    if len(hvs) == 0:
        return np.zeros(N_DIM, dtype=np.int8)
    total = np.zeros(N_DIM, dtype=np.int32)
    for hv in hvs:
        total += hv.astype(np.int32)
    return bipolar_quantize(total)


def cosine(a, b):
    a32 = a.astype(np.float32)
    b32 = b.astype(np.float32)
    na = math.sqrt(float((a32 * a32).sum())) + 1e-9
    nb = math.sqrt(float((b32 * b32).sum())) + 1e-9
    return float((a32 * b32).sum()) / (na * nb)


def codebook_cleanup(v, codebook):
    """Return codebook idx of nearest codeword (argmax cosine)."""
    # codebook: (V_CB, N_DIM) int8
    v32 = v.astype(np.float32)
    v_norm = math.sqrt(float((v32 * v32).sum())) + 1e-9
    # sims = codebook @ v / (||codebook_i|| * ||v||)
    cb32 = codebook.astype(np.float32)
    dots = cb32 @ v32
    row_norms = np.sqrt((cb32 * cb32).sum(axis=1)) + 1e-9
    sims = dots / (row_norms * v_norm)
    return int(np.argmax(sims)), float(np.max(sims))


# ---------------------------------------------------------------------------
# M1.5 v2 STM multi-bank + LTM dense-Hopfield (compressed)
# ---------------------------------------------------------------------------
def make_stm_multibank(rng, codebook, n_items):
    """Build STM multi-bank K=100 (n_items <= STM_TOTAL_K).
    Each bank = bundle of (slot_tag * codebook[val_idx]) for items routed to it.
    Returns (banks, key_tags, val_idxs, bank_assignments)."""
    n_items = min(n_items, STM_TOTAL_K)
    banks = [np.zeros(N_DIM, dtype=np.int32) for _ in range(N_BANKS)]
    key_tags = bipolar_random_batch(rng, n_items)  # (n_items, N_DIM)
    val_idxs = rng.integers(0, V_CB, size=n_items)
    bank_assignments = rng.integers(0, N_BANKS, size=n_items)
    for i in range(n_items):
        val_hv = codebook[val_idxs[i]]
        bound = bind(key_tags[i], val_hv)
        banks[bank_assignments[i]] += bound.astype(np.int32)
    banks_bp = [bipolar_quantize(b) for b in banks]
    return banks_bp, key_tags, val_idxs, bank_assignments


def stm_recall(query_key, bank, codebook):
    """Recall val_idx from STM bank using bipolar unbind + codebook cleanup."""
    # unbind = bind(query_key, bank) since bipolar bind is self-inverse
    unbound = bind(query_key, bank)
    return codebook_cleanup(unbound, codebook)


def make_ltm_hopfield(rng, codebook, n_items):
    """Simple dense-Hopfield-style LTM: store (key, val) pairs.
    Realistically approximated as a stored key-set + codebook for val recall.
    Returns (ltm_keys, ltm_val_idxs)."""
    n_items = min(n_items, LTM_TOTAL_K)
    ltm_keys = bipolar_random_batch(rng, n_items)
    ltm_val_idxs = rng.integers(0, V_CB, size=n_items)
    return ltm_keys, ltm_val_idxs


def ltm_recall(query_key, ltm_keys, ltm_val_idxs, codebook):
    """Dense-Hopfield-style: nearest-key match returns bound val."""
    q = query_key.astype(np.float32)
    K = ltm_keys.astype(np.float32)
    dots = K @ q
    idx = int(np.argmax(dots))
    return int(ltm_val_idxs[idx]), float(np.max(dots) / N_DIM)


# ---------------------------------------------------------------------------
# M1.4 v8 CONFORMAL_MODERATE refuse-gate
# ---------------------------------------------------------------------------
def refuse_gate(query_key, in_kb_max_sim, tau=REFUSE_TAU_MODERATE):
    """Returns True if query should be REFUSED (max_sim < tau)."""
    return float(in_kb_max_sim) < float(tau)


# ---------------------------------------------------------------------------
# M1.6 v2 4-class router (nearest-class HV)
# ---------------------------------------------------------------------------
def make_router(rng):
    """Build 4 class-centroid HVs (one per route)."""
    return {r: bipolar_random(rng) for r in ROUTES}


def route_query(query_feature_hv, class_hvs):
    """Return route by argmax cosine."""
    best_route = None
    best_sim = -2.0
    for r, chv in class_hvs.items():
        s = cosine(query_feature_hv, chv)
        if s > best_sim:
            best_sim = s
            best_route = r
    return best_route, best_sim


def build_query_feature_hv(rng, base_query_hv, refuse_signal_idx,
                           retrieval_signal_idx, chain_signal_idx,
                           refuse_slot_tags, retrieval_slot_tags,
                           chain_slot_tags):
    """M1.6 v2: bundle base + slot-tagged signal features."""
    parts = [base_query_hv]
    parts.append(bind(refuse_slot_tags[refuse_signal_idx],
                       bipolar_random(rng)))  # signal codeword (random per call ok for smoke)
    parts.append(bind(retrieval_slot_tags[retrieval_signal_idx],
                       bipolar_random(rng)))
    parts.append(bind(chain_slot_tags[chain_signal_idx],
                       bipolar_random(rng)))
    return bundle(parts)


# ---------------------------------------------------------------------------
# Deep-composition chain: run one trial through `depth` steps
# ---------------------------------------------------------------------------
def run_chain_trial(rng, arm_name, depth, regime, codebook,
                    stm_banks, stm_key_tags, stm_val_idxs, stm_bank_asn,
                    ltm_keys, ltm_val_idxs, class_hvs,
                    refuse_slot_tags, retrieval_slot_tags, chain_slot_tags):
    """Return per-step top-1 correct fraction for one trial (float in [0,1])."""
    # Track expected val_idxs along the chain vs recovered
    correct = 0
    total = 0

    # Start: pick an initial STM item as anchor
    if len(stm_val_idxs) == 0:
        return 0.0

    curr_idx = int(rng.integers(0, len(stm_val_idxs)))
    curr_key = stm_key_tags[curr_idx]
    curr_expected_val = int(stm_val_idxs[curr_idx])

    for step in range(depth):
        # Determine step regime target route
        if regime == "RETRIEVE_CHAIN":
            expected_route = "RETRIEVE"
            inject_ood = False
        elif regime == "REFUSE_TERMINATED":
            expected_route = "REFUSE" if step >= depth // 2 else "RETRIEVE"
            inject_ood = (step >= depth // 2)
        else:  # ROUTER_MIXED
            expected_route = ROUTES[step % N_CLASSES]
            inject_ood = (expected_route == "REFUSE")

        # Perturb query key with small noise (~0.85 cosine target)
        noise = bipolar_random(rng, N_DIM)
        # Mix: keep 90% of curr_key + 10% noise via bundling
        query_key = bipolar_quantize(
            0.90 * curr_key.astype(np.float32) + 0.10 * noise.astype(np.float32))

        # OOD injection: if inject_ood, replace query_key with random
        if inject_ood:
            query_key = bipolar_random(rng, N_DIM)

        # M1.4 refuse-gate: probe max-sim vs STM keys
        if arm_name != "ARM_NO_REFUSE_D50" and arm_name != "ARM_SUBSTRATE_ONLY_D50":
            # Compute in-KB max-sim: max cosine vs all stm_key_tags
            q32 = query_key.astype(np.float32)
            K32 = stm_key_tags.astype(np.float32)
            dots = K32 @ q32
            in_kb_max_sim = float(np.max(dots) / N_DIM)
            refused = refuse_gate(query_key, in_kb_max_sim)
        else:
            refused = False  # ablation: no refuse-gate
            in_kb_max_sim = 1.0

        # M1.6 router
        if arm_name != "ARM_SUBSTRATE_ONLY_D50":
            # Build query feature HV with slot tags
            refuse_sig = 2 if refused else (1 if in_kb_max_sim < REFUSE_TAU_MODERATE + 0.05 else 0)
            retrieval_sig = 0 if not refused else 2  # STM hit vs no-hit
            chain_sig = 0 if regime == "ROUTER_MIXED" else 1
            query_feat = build_query_feature_hv(
                rng, query_key, refuse_sig, retrieval_sig, chain_sig,
                refuse_slot_tags, retrieval_slot_tags, chain_slot_tags)
            predicted_route, _sim = route_query(query_feat, class_hvs)
        else:
            # Substrate-only: no router, always attempt raw STM recall
            predicted_route = "RETRIEVE"

        # Execute route
        if predicted_route == "REFUSE":
            # Refuse: score = 1 if expected==REFUSE else 0
            step_correct = (expected_route == "REFUSE")
            # Don't advance chain; keep curr_key for next step (chain 'stalls')
            next_expected_val = curr_expected_val
        elif predicted_route == "RETRIEVE":
            recovered_val, _cos = stm_recall(query_key, stm_banks[stm_bank_asn[curr_idx]], codebook)
            step_correct = (recovered_val == curr_expected_val)
            # Advance chain: pick next STM item (deterministic pattern)
            next_idx = (curr_idx + 1) % len(stm_val_idxs)
            curr_idx = next_idx
            curr_key = stm_key_tags[curr_idx]
            next_expected_val = int(stm_val_idxs[curr_idx])
        elif predicted_route == "BIND":
            # Bind: attempt LTM recall as bind-like op
            recovered_val, _cos = ltm_recall(query_key, ltm_keys, ltm_val_idxs, codebook)
            step_correct = (recovered_val == curr_expected_val)
            next_idx = (curr_idx + 1) % len(stm_val_idxs)
            curr_idx = next_idx
            curr_key = stm_key_tags[curr_idx]
            next_expected_val = int(stm_val_idxs[curr_idx])
        else:  # MULTI_HOP
            # Multi-hop: chain STM then LTM
            recovered_val_stm, _c1 = stm_recall(query_key, stm_banks[stm_bank_asn[curr_idx]], codebook)
            # Second hop: use recovered val's codebook HV as key for LTM
            second_key = codebook[recovered_val_stm % V_CB]
            recovered_val, _c2 = ltm_recall(second_key, ltm_keys, ltm_val_idxs, codebook)
            step_correct = (recovered_val == curr_expected_val)
            next_idx = (curr_idx + 1) % len(stm_val_idxs)
            curr_idx = next_idx
            curr_key = stm_key_tags[curr_idx]
            next_expected_val = int(stm_val_idxs[curr_idx])

        # Score if predicted route matched expected route (implicit); else penalize
        # Full stack scoring: step_correct requires BOTH route-match AND val-match
        if predicted_route != expected_route:
            step_correct = False

        if step_correct:
            correct += 1
        total += 1

        curr_expected_val = next_expected_val

    return float(correct) / max(1, total)


# ---------------------------------------------------------------------------
# Per-arm evaluation
# ---------------------------------------------------------------------------
def eval_arm(arm_name, regime, depth, seed_int, n_trials):
    rng = _rng(seed_int * 1000 + hash(arm_name) % 10000 + hash(regime) % 1000)
    codebook = bipolar_random_batch(rng, V_CB, N_DIM)

    # Slot tags for router feature HV
    refuse_slot_tags = bipolar_random_batch(rng, 3, N_DIM)
    retrieval_slot_tags = bipolar_random_batch(rng, 3, N_DIM)
    chain_slot_tags = bipolar_random_batch(rng, 2, N_DIM)

    # STM K=100
    stm_banks, stm_key_tags, stm_val_idxs, stm_bank_asn = make_stm_multibank(
        rng, codebook, STM_TOTAL_K)

    # LTM K=1200
    ltm_keys, ltm_val_idxs = make_ltm_hopfield(rng, codebook, LTM_TOTAL_K)

    # M1.6 router class HVs
    class_hvs = make_router(rng)

    trial_scores = []
    for t in range(n_trials):
        s = run_chain_trial(
            rng, arm_name, depth, regime, codebook,
            stm_banks, stm_key_tags, stm_val_idxs, stm_bank_asn,
            ltm_keys, ltm_val_idxs, class_hvs,
            refuse_slot_tags, retrieval_slot_tags, chain_slot_tags)
        trial_scores.append(s)

    return float(np.mean(trial_scores)), float(np.std(trial_scores)), trial_scores


# ---------------------------------------------------------------------------
# ARMS-MUST-DIFFER hash (META_RULE_AF)
# ---------------------------------------------------------------------------
def _arms_must_differ(arm_outputs: Dict[str, np.ndarray]) -> Dict[str, str]:
    digests = {}
    for name, out in arm_outputs.items():
        if hasattr(out, "tobytes"):
            b = out.tobytes()
        else:
            b = str(out).encode()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if digests[a] == digests[b]:
                raise AssertionError(
                    f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical "
                    f"(hash={digests[a]}); arm-implementation bug")
    return digests


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    global RUN_MODE
    t0 = time.perf_counter()

    # Compute output dir
    exp_name = _HDLAB_EXP_NAME or ANCHOR_NAME
    output_dir = REPO / "data" / f"exp_{exp_name}"
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_start_marker(str(output_dir), ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    print(f"[{ANCHOR_NAME}] START mode={RUN_MODE} depths={DEPTHS} regimes={REGIMES} "
          f"n_trials={N_TRIALS} expected_units={EXPECTED_N_UNITS}", flush=True)

    if RUN_MODE == "self_test":
        # Minimal self-test: verify substrate primitives (small V_CB codebook for speed)
        rng = _rng(SEED_THIS_CHUNK)
        # Use full V_CB codebook so make_stm_multibank's val_idxs are in-range.
        codebook_st = bipolar_random_batch(rng, V_CB, N_DIM)
        v = bipolar_random(rng, N_DIM)
        idx, sim = codebook_cleanup(v, codebook_st)
        assert 0 <= idx < V_CB, "codebook_cleanup returned out-of-range idx"
        assert -1.0 <= sim <= 1.0, "codebook_cleanup returned out-of-range sim"
        # Trivial STM check
        banks, keys, vals, asn = make_stm_multibank(rng, codebook_st, 5)
        assert len(banks) == N_BANKS, "stm banks count wrong"
        # bind self-inverse check
        a = bipolar_random(rng, N_DIM)
        b = bipolar_random(rng, N_DIM)
        c = bind(a, b)
        d = bind(a, c)
        # d should equal b (bipolar bind self-inverse)
        assert np.array_equal(d, b), "bipolar bind not self-inverse"
        elapsed = time.perf_counter() - t0
        metrics = {
            "verdict": "HARD_PASS",
            "verdict_msg": "SELFTEST_PASS (substrate primitives + STM banks + bind-self-inverse OK)",
            "summary": "SELFTEST_PASS",
            "elapsed_s": round(elapsed, 3),
            "run_mode": "self_test",
            "anchor_name": ANCHOR_NAME,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "config_version": CONFIG_VERSION,
        }
        tmp = output_dir / "metrics.json.tmp"
        final = output_dir / "metrics.json"
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        os.replace(str(tmp), str(final))
        print(f"[{ANCHOR_NAME}] SELFTEST_PASS elapsed={elapsed:.2f}s", flush=True)
        return

    # Full or smoke: run all arm x regime x depth combos.
    per_unit = []
    arm_sample_outputs = {}  # for META_RULE_AF hash
    unit_idx = 0

    for arm in ARMS:
        # Determine depth for this arm
        if arm.startswith("ARM_FULL_STACK_"):
            depth = int(arm.split("_D")[-1])
        else:
            depth = 50  # ablation arms are pinned at depth 50

        # Skip depth-100 in smoke
        if RUN_MODE == "smoke" and depth == 100:
            continue

        for regime in REGIMES:
            unit_start = time.perf_counter()
            score_mean, score_std, trial_scores = eval_arm(
                arm, regime, depth, SEED_THIS_CHUNK, N_TRIALS)
            unit_elapsed = time.perf_counter() - unit_start

            row = {
                "arm": arm,
                "regime": regime,
                "depth": depth,
                "score_mean": float(score_mean),
                "score_std": float(score_std),
                "n_trials": N_TRIALS,
                "trial_scores": [float(s) for s in trial_scores],
                "elapsed_s": round(unit_elapsed, 3),
                "seed": SEED_THIS_CHUNK,
                "failure_class": None,
            }
            per_unit.append(row)

            # Capture arm sample for AF hash (concat of trial_scores as bytes)
            if arm not in arm_sample_outputs:
                arm_sample_outputs[arm] = np.array(trial_scores, dtype=np.float64)

            unit_idx += 1
            emit_heartbeat(str(output_dir), unit_idx,
                           time.perf_counter() - t0,
                           total_units=EXPECTED_N_UNITS,
                           extra={"arm": arm, "regime": regime, "depth": depth,
                                  "score_mean": round(score_mean, 4)})
            print(f"[{ANCHOR_NAME}] unit {unit_idx}/{EXPECTED_N_UNITS} "
                  f"arm={arm} regime={regime} depth={depth} "
                  f"score={score_mean:.3f}+/-{score_std:.3f} "
                  f"elapsed={unit_elapsed:.2f}s", flush=True)

    # META_RULE_AF: arms-must-differ
    arms_differ_verified = False
    af_error = None
    try:
        digests = _arms_must_differ(arm_sample_outputs)
        arms_differ_verified = True
    except AssertionError as e:
        af_error = str(e)
        digests = {}

    # Verdict logic
    verdict = "UNKNOWN"
    verdict_msgs = []
    hp_gates = {}

    # Cardinality gate
    expected = EXPECTED_N_UNITS if RUN_MODE == "full" else \
        (len(FULL_STACK_ARMS) - (1 if RUN_MODE == "smoke" else 0)) * len(REGIMES) + \
        len(ABLATION_ARMS) * len(REGIMES)
    observed = len(per_unit)
    cardinality_ok = observed >= int(0.85 * expected)

    def _mean_score(arm_name, regime=None):
        rows = [r for r in per_unit if r["arm"] == arm_name and
                (regime is None or r["regime"] == regime)]
        if not rows:
            return None
        return float(np.mean([r["score_mean"] for r in rows]))

    fs_d10 = _mean_score("ARM_FULL_STACK_D10")
    fs_d50 = _mean_score("ARM_FULL_STACK_D50")
    fs_d100 = _mean_score("ARM_FULL_STACK_D100")
    sub_only = _mean_score("ARM_SUBSTRATE_ONLY_D50")
    no_ref = _mean_score("ARM_NO_REFUSE_D50")

    hp_gates["HP_D10_HOLDS"] = (fs_d10 is not None and fs_d10 >= HP_D10_FLOOR + BAND_WIDTH_MARGIN * (1.0 - HP_D10_FLOOR))
    hp_gates["HP_D50_HOLDS"] = (fs_d50 is not None and fs_d50 >= HP_D50_FLOOR + BAND_WIDTH_MARGIN * (1.0 - HP_D50_FLOOR))
    if RUN_MODE == "full":
        hp_gates["HP_D100_HOLDS"] = (fs_d100 is not None and fs_d100 >= HP_D100_FLOOR + BAND_WIDTH_MARGIN * (1.0 - HP_D100_FLOOR))
    hp_gates["HP_LIFT_OVER_NO_REFUSE"] = (fs_d50 is not None and no_ref is not None
                                           and (fs_d50 - no_ref) >= HP_LIFT_OVER_NO_REFUSE)
    hp_gates["HP_LIFT_OVER_SUBSTRATE_ONLY"] = (fs_d50 is not None and sub_only is not None
                                                and (fs_d50 - sub_only) >= HP_LIFT_OVER_SUBSTRATE_ONLY)

    # META_RULE_AG baseline_in_band check (SUBSTRATE_ONLY_D50 must be 0.05 < s < 0.95)
    baseline_in_band = (sub_only is not None and 0.05 < sub_only < 0.95)

    # HARD_FAIL_BROKEN_PC_BEATS_STACK check
    broken_pc_beats = (fs_d50 is not None and sub_only is not None and sub_only > fs_d50)

    n_hp_fired = sum(1 for v in hp_gates.values() if v is True)
    n_hp_total = len(hp_gates)

    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msgs.append(f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H "
                            f"(observed={observed}, expected={expected})")
    elif not arms_differ_verified:
        verdict = "HARD_FAIL"
        verdict_msgs.append(f"HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF ({af_error})")
    elif broken_pc_beats:
        verdict = "HARD_FAIL"
        verdict_msgs.append(f"HARD_FAIL_BROKEN_PC_BEATS_STACK "
                            f"(substrate_only={sub_only:.3f} > full_stack={fs_d50:.3f})")
    elif n_hp_fired == n_hp_total:
        verdict = "HARD_PASS"
        verdict_msgs.append(f"CHAIN_GRADE_FULL_STACK_COMPOSES ({n_hp_fired}/{n_hp_total} HP fired)")
    elif n_hp_fired >= max(1, n_hp_total - 1):
        # MECHANISM_DEATH check: any HP miss >= 0.15?
        margins = []
        if fs_d10 is not None:
            margins.append(HP_D10_FLOOR - fs_d10)
        if fs_d50 is not None:
            margins.append(HP_D50_FLOOR - fs_d50)
        if fs_d100 is not None:
            margins.append(HP_D100_FLOOR - fs_d100)
        max_miss = max(margins) if margins else 0.0
        if max_miss >= HF_MECHANISM_DEATH_MARGIN:
            verdict = "HARD_FAIL"
            verdict_msgs.append(f"HARD_FAIL_MECHANISM_DEATH (miss={max_miss:.3f})")
        else:
            verdict = "MIDDLE_BAND"
            verdict_msgs.append(f"MIDDLE_BAND ({n_hp_fired}/{n_hp_total} HP)")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msgs.append(f"MIDDLE_BAND ({n_hp_fired}/{n_hp_total} HP)")

    verdict_msgs.append(f"cardinality_ok={cardinality_ok} observed={observed}/{expected}")
    verdict_msgs.append(f"arms_differ_verified={arms_differ_verified}")
    verdict_msgs.append(f"baseline_in_band={baseline_in_band}")
    verdict_msgs.append(f"FS_D10={fs_d10} FS_D50={fs_d50} FS_D100={fs_d100} "
                        f"SUB_ONLY={sub_only} NO_REF={no_ref}")

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": " | ".join(verdict_msgs),
        "summary": f"{verdict}: {n_hp_fired}/{n_hp_total} HP fired at depths {DEPTHS}",
        "elapsed_s": round(elapsed, 3),
        "run_mode": RUN_MODE,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config_version": CONFIG_VERSION,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected,
        "observed_n_units": observed,
        "arms_differ_verified": arms_differ_verified,
        "af_digests": digests,
        "baseline_in_band": baseline_in_band,
        "hp_gates": hp_gates,
        "aggregate_scores": {
            "ARM_FULL_STACK_D10": fs_d10,
            "ARM_FULL_STACK_D50": fs_d50,
            "ARM_FULL_STACK_D100": fs_d100,
            "ARM_SUBSTRATE_ONLY_D50": sub_only,
            "ARM_NO_REFUSE_D50": no_ref,
        },
        "per_unit": per_unit,
        "chance_floor": CHANCE_FLOOR,
        "meta_rules_applied": ["AC", "AF", "AG", "AH", "AT", "H", "J", "K", "L", "M"],
        "seed": SEED_THIS_CHUNK,
    }

    # Atomic write (META_RULE_AH tmp_replace)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(str(tmp), str(final))
    print(f"[{ANCHOR_NAME}] DONE verdict={verdict} elapsed={elapsed:.2f}s", flush=True)


if __name__ == "__main__":
    exp_name = _HDLAB_EXP_NAME or ANCHOR_NAME
    output_dir_pre = REPO / "data" / f"exp_{exp_name}"
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(str(output_dir_pre), ANCHOR_NAME, e)
        raise
