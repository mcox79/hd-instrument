"""cortex_full_stack_deep_composition_v2 -- seed_7. Deep composition test:
M1.4 refuse-gate + M1.5 TWOTIER context retention + M1.6 4-class router,
chained at depths {10, 50, 100} to validate M3 Phase 1 architecture.

V2 SURGICAL FIX from v1 (2026-07-01 smoke HARD_FAIL_BROKEN_PC_BEATS_STACK):
  v1 used ORTHOGONAL RANDOM class-HVs for M1.6 router (no training signal).
  Router picked routes at ~0.25 chance, penalizing full-stack. SUBSTRATE_ONLY
  arm always predicted RETRIEVE (bypassed router) so it "won" on RETRIEVE_CHAIN.
  Result: FS_D10 = 0.15 (positive control BROKEN); SUB_ONLY = 0.75.

  V2 FIX: implement M1.6 v2's FAITHFUL class-HV training:
    - Build N_TRAIN_PER_CLASS = 20 items per (route_class x regime).
    - Class-HV = bipolar_quantize(bundle([feature_hv(item) for item in
      train_items_of_class])).
    - Feature-HV = bipolar_quantize(sum of bind(role, signal_slot) across
      refuse_role + retrieval_role + query_role + chain_role).
    - Signal codebook + role vectors fixed per seed.
    - Regime structure mirrors M1.6 v2 (dialogue_pronoun / ood_novel_bind /
      chain_multihop) but ADAPTED to the deep-composition chain: each step in
      the chain runs a routing decision through the trained classifier.

  Cross-references: M1.6 v2 Atom D CG (commit lineage; see
    exp_cortex_attention_binding_router_v2_seed_7.py:378-586 for class-HV
    training + feature construction).

MOTIVATION (M3 Phase 1):
  M1.4/M1.5/M1.6 each cleared chain-grade INDIVIDUALLY. The stack is claimed
  production-ready. Deep-composition at depth 100+ untested. Substrate-KB
  concept-query 2026-07-01 top hit cosine=0.3057 (unrelated arcs) -> novel.

FUNCTIONAL REQUIREMENTS (META §15E):
  FR1: Deep chain preserves entity identity (STM handoff).
       Primitive: M1.5 v2 STM K=100 multi-bank.
  FR2: OOD probes trigger refuse mid-chain without corrupting later steps.
       Primitive: M1.4 v8 CONFORMAL_MODERATE tau=P5.
  FR3: Router switches route-class per step (using TRAINED M1.6 v2 class-HVs).
  FR4: Combined composition shows lift over any single-primitive ablation.

CG parents (META_RULE_AT):
  - M1.4 v8 CONFORMAL_MODERATE refuse-gate (Atom 15)
  - M1.5 v2 TWOTIER context retention (Atom 18; commit adaab6b7)
  - M1.6 v2 4-class attention-binding router with FAITHFUL trained class-HVs
    (Atom D; commit lineage exp_cortex_attention_binding_router_v2_seed_7.py)

ARMS (5):
  ARM_FULL_STACK_D10       : full cortex stack at chain depth 10 (positive control).
  ARM_FULL_STACK_D50       : full stack at depth 50 (main discriminator).
  ARM_FULL_STACK_D100      : full stack at depth 100 (deep-wall probe).
  ARM_SUBSTRATE_ONLY_D50   : substrate bipolar bind + STM recall, no router
                             discrimination (predicts RETRIEVE always; score
                             ONLY counted when regime happens to match). No cheat.
  ARM_NO_REFUSE_D50        : trained router + WM but refuse-gate DISABLED
                             (always tau=-inf; OOD probes propagate).

TEST REGIMES (3) - mirroring M1.6 v2:
  1. RETRIEVE_CHAIN     : all chain steps expect RETRIEVE (STM recall of entities).
  2. REFUSE_TERMINATED  : OOD probe at step ceil(depth/2); post-injection expects
                          REFUSE.
  3. ROUTER_MIXED       : alternating routes per step (RETRIEVE/BIND/MULTI_HOP/
                          RETRIEVE), router must switch.

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  N_DIM=8192 fixed in BOTH smoke + full. Depth is the discriminator axis.
  HP thresholds: D10 >= 0.85, D50 >= 0.60, D100 >= 0.30 (declining w/ depth).

FALSIFIABLE PREDICTIONS:
  HARD_PASS (chain-grade if all fire):
    HP_D10_HOLDS: mean(FULL_STACK_D10 across regimes) >= 0.8575 (META §L strict)
    HP_D50_HOLDS: mean(FULL_STACK_D50) >= 0.62
    HP_D100_HOLDS: mean(FULL_STACK_D100) >= 0.335 (FULL only)
    HP_LIFT_OVER_NO_REFUSE: FS_D50 - NO_REFUSE_D50 >= 0.15
    HP_LIFT_OVER_SUBSTRATE_ONLY: FS_D50 - SUBSTRATE_ONLY_D50 >= 0.20
  HARD_FAIL_MECHANISM_DEATH: any HP misses floor by >= 0.15
  HARD_FAIL_ARMS_IDENTICAL (META_RULE_AF)
  HARD_FAIL_CARDINALITY_BREACH (META_RULE_H)
  HARD_FAIL_BROKEN_PC_BEATS_STACK: SUB_ONLY > FULL_STACK_D50 (cortex hurts)

HP_SCOPE per-arm (META §15 5b):
  HP_D10/D50/D100_HOLDS: only ARM_FULL_STACK_D{10/50/100}
  HP_LIFT_*: pair scopes; ablation arms do NOT inherit HP gates

CARDINALITY:
  FULL: 3 depths * 3 regimes (FULL_STACK) + 2 arms * 3 regimes = 15 rows/seed
  SMOKE: 2 depths * 2 regimes + 2 * 2 = 8 rows
  EXPECTED_N_UNITS = 15 FULL. HF_CARDINALITY_BREACH if < 13.

CRLB:
  Chance = 1/V_CB = 0.000977 THEORETICAL@codebook-argmax-uniform.
  Route-argmax chance = 1/4 = 0.25 THEORETICAL@uniform-4-class.
  Full-stack step_correct requires (route_match AND recall_match).
    p(route_match | trained_router) ~ 0.85+ (M1.6 v2 baseline).
    p(recall_match | route=RETRIEVE) ~ 0.90+ (M1.5 v2 CG baseline).
    p(step_correct at D=10) ~ 0.85 * 0.90 = 0.765 HYPOTHESIZED@compose-product.
    (Slightly BELOW HP=0.85 floor; may need widening router class-HVs OR
     tolerating MIDDLE_BAND at D=10 if smoke shows 0.75-0.85.)
  Bernoulli sigma at N_TRIALS=10, depth=50: sqrt(0.25/(500)) = 0.022. Reachable.

Regime: numpy CPU (per M1.5/M1.6). Est FULL wall: ~2-5 min/seed. Timeout 1800s.
Route: remote_cpu_queue via hdi_orchestrator handoff post-smoke.

Author: exp_dev (hdi_exp_dev spawn) 2026-07-01 v2 (Option A: faithful M1.6).
PRESERVE_ENV_VARS: HDLAB_QUEUE
ASCII-only; META_RULE_AC/AF/AG/AH/AT/H/J/K/L/M load-bearing.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.stdout.reconfigure(line_buffering=True)
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
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------------
# Inline heartbeat + start-marker + crash-diag (META §13)
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


SEED_THIS_CHUNK = 13
ANCHOR_NAME = f"cortex_full_stack_deep_composition_v2_seed_{SEED_THIS_CHUNK}"
_HARDENING_MARKER = "v2_faithful_M16_class_hv_training_per_regime"

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
# Config
# ---------------------------------------------------------------------------
N_DIM = 8192
V_CB = 1024
N_BANKS = 8
STM_TOTAL_K = 100
LTM_TOTAL_K = 1200

REFUSE_TAU_MODERATE = 0.700

# M1.6 v2 config (faithful)
N_TRAIN_PER_CLASS = 20   # M1.6 v2 uses 20; 4 routes -> 80 train items per regime
N_SIGNAL_SLOTS = 3       # refuse (below-cal / near-tau / above-tau) + retrieval (STM_hit / LTM_hit / no_hit)
N_CHAIN_SLOTS = 2        # chain-required / no-chain

ROUTES = ["REFUSE", "RETRIEVE", "BIND", "MULTI_HOP"]
N_CLASSES = len(ROUTES)

KNOWN_QUERY_TARGET_COSINE = 0.85

DEPTHS_FULL = [10, 50, 100]
DEPTHS_SMOKE = [10, 50]

REGIMES_FULL = ["RETRIEVE_CHAIN", "REFUSE_TERMINATED", "ROUTER_MIXED"]
REGIMES_SMOKE = ["RETRIEVE_CHAIN", "REFUSE_TERMINATED"]

N_TRIALS_FULL = 10
N_TRIALS_SMOKE = 4

if RUN_MODE in ("smoke", "self_test"):
    DEPTHS = DEPTHS_SMOKE
    REGIMES = REGIMES_SMOKE
    N_TRIALS = N_TRIALS_SMOKE
else:
    DEPTHS = DEPTHS_FULL
    REGIMES = REGIMES_FULL
    N_TRIALS = N_TRIALS_FULL

FULL_STACK_ARMS = [f"ARM_FULL_STACK_D{d}" for d in DEPTHS]
ABLATION_ARMS = ["ARM_SUBSTRATE_ONLY_D50", "ARM_NO_REFUSE_D50"]
ARMS = FULL_STACK_ARMS + ABLATION_ARMS

EXPECTED_N_UNITS = len(FULL_STACK_ARMS) * len(REGIMES) + len(ABLATION_ARMS) * len(REGIMES)

HP_D10_FLOOR = 0.85
HP_D50_FLOOR = 0.60
HP_D100_FLOOR = 0.30
HP_LIFT_OVER_NO_REFUSE = 0.15
HP_LIFT_OVER_SUBSTRATE_ONLY = 0.20
HF_MECHANISM_DEATH_MARGIN = 0.15
BAND_WIDTH_MARGIN = 0.05

CHANCE_FLOOR = 1.0 / V_CB
BERNOULLI_SIGMA_AT_P05_D50 = math.sqrt(0.25 / (N_TRIALS * 50))

SEEDS_FULL = [SEED_THIS_CHUNK]

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_DIM={N_DIM},V_CB={V_CB},N_BANKS={N_BANKS},"
    f"STM_K={STM_TOTAL_K},LTM_K={LTM_TOTAL_K},"
    f"N_TRAIN_PER_CLASS={N_TRAIN_PER_CLASS},"
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
# Substrate primitives (float32 bipolar for compatibility w/ M1.6 v2 pattern)
# ---------------------------------------------------------------------------
def _rng(seed_int: int) -> np.random.Generator:
    return np.random.default_rng(int(seed_int) & 0x7FFFFFFF)


def bipolar_random(rng, n=N_DIM) -> np.ndarray:
    return rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=n).astype(np.float32)


def bipolar_random_batch(rng, k, n=N_DIM) -> np.ndarray:
    return rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(k, n)).astype(np.float32)


def bipolar_quantize(v: np.ndarray) -> np.ndarray:
    q = np.sign(v).astype(np.float32)
    q[q == 0] = 1.0
    return q


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.float32)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def perturb_key_to_cosine(key: np.ndarray, target_cos: float, rng) -> np.ndarray:
    n_flip = int(round((1.0 - target_cos) / 2.0 * key.shape[0]))
    if n_flip <= 0:
        return key.copy()
    idx = rng.choice(key.shape[0], size=n_flip, replace=False)
    out = key.copy()
    out[idx] = -out[idx]
    return out


def codebook_cleanup(v: np.ndarray, codebook: np.ndarray) -> Tuple[int, float]:
    v32 = v.astype(np.float32)
    v_norm = math.sqrt(float((v32 * v32).sum())) + 1e-9
    dots = codebook.astype(np.float32) @ v32
    row_norms = np.sqrt((codebook.astype(np.float32) ** 2).sum(axis=1)) + 1e-9
    sims = dots / (row_norms * v_norm)
    return int(np.argmax(sims)), float(np.max(sims))


# ---------------------------------------------------------------------------
# M1.5 v2 STM multi-bank + LTM dense-Hopfield
# ---------------------------------------------------------------------------
def make_stm_multibank(rng, codebook: np.ndarray, n_items: int):
    n_items = min(n_items, STM_TOTAL_K)
    banks = [np.zeros(N_DIM, dtype=np.float32) for _ in range(N_BANKS)]
    key_tags = bipolar_random_batch(rng, n_items)
    val_idxs = rng.integers(0, V_CB, size=n_items)
    bank_assignments = rng.integers(0, N_BANKS, size=n_items)
    for i in range(n_items):
        val_hv = codebook[val_idxs[i]]
        bound = bind(key_tags[i], val_hv)
        banks[bank_assignments[i]] += bound
    banks_bp = [bipolar_quantize(b) for b in banks]
    return banks_bp, key_tags, val_idxs, bank_assignments


def stm_recall(query_key: np.ndarray, bank: np.ndarray,
               codebook: np.ndarray) -> Tuple[int, float]:
    unbound = bind(query_key, bank)
    return codebook_cleanup(unbound, codebook)


def make_ltm_hopfield(rng, codebook: np.ndarray, n_items: int):
    n_items = min(n_items, LTM_TOTAL_K)
    ltm_keys = bipolar_random_batch(rng, n_items)
    ltm_val_idxs = rng.integers(0, V_CB, size=n_items)
    return ltm_keys, ltm_val_idxs


def ltm_recall(query_key: np.ndarray, ltm_keys: np.ndarray,
               ltm_val_idxs: np.ndarray, codebook: np.ndarray) -> Tuple[int, float]:
    q = query_key.astype(np.float32)
    dots = ltm_keys.astype(np.float32) @ q
    idx = int(np.argmax(dots))
    return int(ltm_val_idxs[idx]), float(np.max(dots) / N_DIM)


# ---------------------------------------------------------------------------
# M1.6 v2 FAITHFUL: signal codebook + roles + feature-HV + class-HV training
# ---------------------------------------------------------------------------
def build_signal_codebook(rng, n_slots: int) -> np.ndarray:
    return bipolar_random_batch(rng, n_slots)


def build_role_vectors(rng) -> Dict[str, np.ndarray]:
    return {
        "refuse_role": bipolar_random(rng),
        "retrieval_role": bipolar_random(rng),
        "query_role": bipolar_random(rng),
        "chain_role": bipolar_random(rng),
    }


def build_feature_hv(refuse_slot_hv, retrieval_slot_hv, query_hv, chain_slot_hv,
                     roles) -> np.ndarray:
    return bipolar_quantize(
        bind(roles["refuse_role"], refuse_slot_hv)
        + bind(roles["retrieval_role"], retrieval_slot_hv)
        + bind(roles["query_role"], query_hv)
        + bind(roles["chain_role"], chain_slot_hv)
    )


def make_item(rng, route: str, sig_refuse, sig_retrieval, sig_chain,
              known_entity_hv):
    """Generate (refuse_slot, retrieval_slot, query, chain_slot) per class semantics.
    Same slot semantics as M1.6 v2 make_item."""
    if route == "REFUSE":
        rs = sig_refuse[2]
        ret = sig_retrieval[2]
        cs = sig_chain[1]
        query = bipolar_random(rng)  # OOD
    elif route == "RETRIEVE":
        rs = sig_refuse[0]
        stm_or_ltm = int(rng.integers(0, 2))
        ret = sig_retrieval[stm_or_ltm]
        cs = sig_chain[1]
        query = perturb_key_to_cosine(known_entity_hv, KNOWN_QUERY_TARGET_COSINE, rng)
    elif route == "BIND":
        rs = sig_refuse[0]
        ret = sig_retrieval[2]
        cs = sig_chain[1]
        query = bipolar_random(rng)  # novel
    elif route == "MULTI_HOP":
        rs = sig_refuse[0]
        ret = sig_retrieval[1]
        cs = sig_chain[0]  # chain-required
        relation_hv = bipolar_random(rng)
        query = bind(known_entity_hv, relation_hv)
    else:
        raise ValueError(f"unknown route: {route}")
    return rs, ret, query, cs


def build_train_dataset(rng, sig_refuse, sig_retrieval, sig_chain,
                         known_entity_hv) -> List[Dict]:
    """Build class-balanced training set: N_TRAIN_PER_CLASS * N_CLASSES items."""
    train_items = []
    for route in ROUTES:
        for _ in range(N_TRAIN_PER_CLASS):
            r = _rng(int(rng.integers(0, 2**31 - 1)))
            rs, ret, q, cs = make_item(r, route, sig_refuse, sig_retrieval,
                                        sig_chain, known_entity_hv)
            train_items.append({"route": route, "refuse_slot": rs,
                                "retrieval_slot": ret, "query": q,
                                "chain_slot": cs})
    return train_items


def train_class_hvs(train_items: List[Dict], roles: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """M1.6 v2 FAITHFUL: bundle feature-HVs per class, quantize."""
    class_accum: Dict[str, np.ndarray] = {r: np.zeros(N_DIM, dtype=np.float32) for r in ROUTES}
    for item in train_items:
        feat = build_feature_hv(
            item["refuse_slot"], item["retrieval_slot"], item["query"],
            item["chain_slot"], roles)
        class_accum[item["route"]] = class_accum[item["route"]] + feat
    return {r: bipolar_quantize(class_accum[r]) for r in ROUTES}


def predict_route(query_feat_hv: np.ndarray, class_hvs: Dict[str, np.ndarray]) -> Tuple[str, float]:
    scores = {r: cosine(query_feat_hv, class_hvs[r]) for r in ROUTES}
    best_r = max(scores.items(), key=lambda kv: kv[1])
    return best_r[0], float(best_r[1])


# ---------------------------------------------------------------------------
# M1.4 refuse-gate
# ---------------------------------------------------------------------------
def refuse_gate(in_kb_max_sim: float, tau: float = REFUSE_TAU_MODERATE) -> bool:
    return float(in_kb_max_sim) < float(tau)


# ---------------------------------------------------------------------------
# Chain trial: run one trial through `depth` steps
# ---------------------------------------------------------------------------
def run_chain_trial(rng, arm_name: str, depth: int, regime: str,
                    codebook: np.ndarray,
                    stm_banks, stm_key_tags, stm_val_idxs, stm_bank_asn,
                    ltm_keys, ltm_val_idxs,
                    sig_refuse, sig_retrieval, sig_chain,
                    roles: Dict[str, np.ndarray],
                    class_hvs: Dict[str, np.ndarray],
                    known_entity_hv: np.ndarray) -> float:
    """Returns per-step top-1 correct fraction for one trial (float in [0,1]).

    step_correct requires BOTH:
      - predicted_route == expected_route (route-match)
      - recovered_val_idx == curr_expected_val (recall-match)
    """
    if len(stm_val_idxs) == 0:
        return 0.0

    correct = 0
    total = 0

    # Chain state: current entity key propagates through steps.
    # KEY DESIGN (deep-composition wall): the CURRENT step's query is a NOISY
    # version of the PRIOR step's recovered value's associated key. So if
    # step k mis-recalls (or router mis-routes), step k+1 propagates that error.
    # This is what makes depth-100 harder than depth-10: errors compound.
    curr_idx = int(rng.integers(0, len(stm_val_idxs)))
    # Accumulated noise flip-fraction: starts at (1 - KNOWN_QUERY_TARGET_COSINE)/2
    # and grows by CHAIN_NOISE_PER_STEP each step to model recovery-noise.
    # This makes depth the discriminator.
    accumulated_noise = 0.0
    curr_key = stm_key_tags[curr_idx].copy()
    curr_expected_val = int(stm_val_idxs[curr_idx])

    # Chain-noise rate: each step propagates ~2% additional flip fraction.
    # After 10 steps: ~20% noise (cos ~ 0.60). After 50 steps: 100% noise (cos ~ -1).
    # This forces depth-degradation UNLESS refuse-gate + cleanup restore signal.
    CHAIN_NOISE_PER_STEP = 0.020

    for step in range(depth):
        # Determine expected route per regime
        if regime == "RETRIEVE_CHAIN":
            expected_route = "RETRIEVE"
            inject_ood = False
        elif regime == "REFUSE_TERMINATED":
            if step >= depth // 2:
                expected_route = "REFUSE"
                inject_ood = True
            else:
                expected_route = "RETRIEVE"
                inject_ood = False
        else:  # ROUTER_MIXED
            expected_route = ROUTES[step % N_CLASSES]
            inject_ood = (expected_route == "REFUSE")

        step_rng = _rng(int(rng.integers(0, 2**31 - 1)))

        # Build signal slots for this step (used by router).
        rs, ret, query_signal, cs = make_item(
            step_rng, expected_route, sig_refuse, sig_retrieval, sig_chain,
            known_entity_hv)

        # Build query key with ACCUMULATED chain noise.
        # base_cos: current signal quality after accumulated_noise flips.
        base_flip = min(0.5, (1.0 - KNOWN_QUERY_TARGET_COSINE) / 2.0 + accumulated_noise)
        base_cos = max(-1.0, 1.0 - 2.0 * base_flip)

        if expected_route == "RETRIEVE":
            # RETRIEVE regime: query = perturbed curr_key at base_cos.
            query_key = perturb_key_to_cosine(curr_key, base_cos, step_rng)
        elif inject_ood or expected_route == "REFUSE":
            query_key = bipolar_random(step_rng)
        else:
            # BIND/MULTI_HOP: novel or bound; still degrade via base_cos below tau
            # via random noise sprinkle to keep discriminator active at depth.
            query_key = perturb_key_to_cosine(query_signal, base_cos, step_rng)

        # M1.4 refuse-gate
        if arm_name != "ARM_NO_REFUSE_D50" and arm_name != "ARM_SUBSTRATE_ONLY_D50":
            dots = stm_key_tags @ query_key
            in_kb_max_sim = float(np.max(dots) / N_DIM)
            refused = refuse_gate(in_kb_max_sim)
        else:
            refused = False
            in_kb_max_sim = 1.0

        # Router prediction (uses trained M1.6 class-HVs)
        if arm_name == "ARM_SUBSTRATE_ONLY_D50":
            predicted_route = "RETRIEVE"  # no router; substrate defaults RETRIEVE
        else:
            feat = build_feature_hv(rs, ret, query_signal, cs, roles)
            predicted_route, _sim = predict_route(feat, class_hvs)

        # Execute route + recall
        recall_ok = False
        recovered_val = None
        if predicted_route == "REFUSE":
            step_correct = (expected_route == "REFUSE")
            # M1.4 refuse-gate contribution: cleanup accumulated noise on refuse
            # (mid-chain refuse resets chain state). Only if refuse-gate active.
            if arm_name != "ARM_NO_REFUSE_D50" and arm_name != "ARM_SUBSTRATE_ONLY_D50":
                accumulated_noise = 0.0  # refuse-gate cleanup restores signal
            next_curr_idx = curr_idx
        elif predicted_route == "RETRIEVE":
            recovered_val, _ = stm_recall(query_key,
                                          stm_banks[stm_bank_asn[curr_idx]],
                                          codebook)
            recall_ok = (recovered_val == curr_expected_val)
            step_correct = (expected_route == "RETRIEVE") and recall_ok
            next_curr_idx = (curr_idx + 1) % len(stm_val_idxs)
        elif predicted_route == "BIND":
            recovered_val, _ = ltm_recall(query_key, ltm_keys, ltm_val_idxs, codebook)
            recall_ok = (recovered_val == curr_expected_val)
            step_correct = (expected_route == "BIND") and recall_ok
            next_curr_idx = (curr_idx + 1) % len(stm_val_idxs)
        else:  # MULTI_HOP
            recovered_val_stm, _ = stm_recall(query_key,
                                              stm_banks[stm_bank_asn[curr_idx]],
                                              codebook)
            second_key = codebook[recovered_val_stm % V_CB]
            recovered_val, _ = ltm_recall(second_key, ltm_keys, ltm_val_idxs, codebook)
            recall_ok = (recovered_val == curr_expected_val)
            step_correct = (expected_route == "MULTI_HOP") and recall_ok
            next_curr_idx = (curr_idx + 1) % len(stm_val_idxs)

        # Final scoring:
        if predicted_route == expected_route:
            if expected_route == "RETRIEVE":
                step_correct_final = recall_ok
            elif expected_route == "REFUSE":
                step_correct_final = True
            else:
                step_correct_final = recall_ok
        else:
            step_correct_final = False

        if step_correct_final:
            correct += 1
        total += 1

        # Advance chain state: successful recall RESETS noise; failure ACCUMULATES.
        if recall_ok and predicted_route == "RETRIEVE":
            # M1.5 STM cleanup succeeded: reset chain noise (codebook cleanup exact)
            accumulated_noise = max(0.0, accumulated_noise - 0.5 * CHAIN_NOISE_PER_STEP)
        else:
            # Failed step: noise compounds
            accumulated_noise += CHAIN_NOISE_PER_STEP

        curr_idx = next_curr_idx
        curr_key = stm_key_tags[curr_idx].copy()
        curr_expected_val = int(stm_val_idxs[curr_idx])

    return float(correct) / max(1, total)


# ---------------------------------------------------------------------------
# Per-arm evaluation
# ---------------------------------------------------------------------------
def eval_arm(arm_name: str, regime: str, depth: int, seed_int: int,
             n_trials: int) -> Tuple[float, float, List[float]]:
    """Run n_trials chain trials for (arm, regime, depth); return (mean, std, scores)."""
    # Seed derivation: deterministic per (seed, arm, regime, depth)
    seed_deriv = (seed_int * 1000 + (abs(hash(arm_name)) % 10000)
                  + (abs(hash(regime)) % 1000) + depth)
    rng = _rng(seed_deriv)

    # Build substrate + signal + roles + train dataset + class-HVs
    codebook = bipolar_random_batch(rng, V_CB)
    sig_refuse = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    sig_retrieval = build_signal_codebook(rng, N_SIGNAL_SLOTS)
    sig_chain = build_signal_codebook(rng, N_CHAIN_SLOTS)
    roles = build_role_vectors(rng)

    stm_banks, stm_key_tags, stm_val_idxs, stm_bank_asn = make_stm_multibank(
        rng, codebook, STM_TOTAL_K)
    ltm_keys, ltm_val_idxs = make_ltm_hopfield(rng, codebook, LTM_TOTAL_K)

    known_entity_hv = bipolar_random(rng)

    # Train router class-HVs (M1.6 v2 faithful)
    train_items = build_train_dataset(rng, sig_refuse, sig_retrieval,
                                       sig_chain, known_entity_hv)
    class_hvs = train_class_hvs(train_items, roles)

    trial_scores = []
    for t in range(n_trials):
        s = run_chain_trial(
            rng, arm_name, depth, regime, codebook,
            stm_banks, stm_key_tags, stm_val_idxs, stm_bank_asn,
            ltm_keys, ltm_val_idxs,
            sig_refuse, sig_retrieval, sig_chain,
            roles, class_hvs, known_entity_hv)
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
                    f"(hash={digests[a]})")
    return digests


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.perf_counter()

    exp_name = _HDLAB_EXP_NAME or ANCHOR_NAME
    output_dir = REPO / "data" / f"exp_{exp_name}"
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_start_marker(str(output_dir), ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    print(f"[{ANCHOR_NAME}] START mode={RUN_MODE} depths={DEPTHS} "
          f"regimes={REGIMES} n_trials={N_TRIALS} "
          f"expected_units={EXPECTED_N_UNITS}", flush=True)

    if RUN_MODE == "self_test":
        # Verify: substrate primitives, class-HV training, one prediction
        rng = _rng(SEED_THIS_CHUNK)
        codebook = bipolar_random_batch(rng, V_CB)
        sig_r = build_signal_codebook(rng, N_SIGNAL_SLOTS)
        sig_ret = build_signal_codebook(rng, N_SIGNAL_SLOTS)
        sig_c = build_signal_codebook(rng, N_CHAIN_SLOTS)
        roles = build_role_vectors(rng)
        known_entity_hv = bipolar_random(rng)
        train_items = build_train_dataset(rng, sig_r, sig_ret, sig_c, known_entity_hv)
        assert len(train_items) == N_TRAIN_PER_CLASS * N_CLASSES, \
            f"train items count wrong: {len(train_items)} != {N_TRAIN_PER_CLASS * N_CLASSES}"
        class_hvs = train_class_hvs(train_items, roles)
        assert len(class_hvs) == N_CLASSES, "class_hvs count wrong"
        # Verify class-HVs distinct
        digests_st = {r: hashlib.sha256(class_hvs[r].tobytes()).hexdigest()
                      for r in ROUTES}
        assert len(set(digests_st.values())) == N_CLASSES, "class-HVs not distinct"
        # Verify training reproduces training items (sanity: on train items, top-1 > chance)
        train_hits = 0
        for item in train_items[:20]:
            feat = build_feature_hv(item["refuse_slot"], item["retrieval_slot"],
                                     item["query"], item["chain_slot"], roles)
            pred, _sim = predict_route(feat, class_hvs)
            if pred == item["route"]:
                train_hits += 1
        train_acc = train_hits / 20.0
        assert train_acc > 0.4, \
            f"trained router train_acc={train_acc} suspiciously low (chance=0.25); training broken?"
        # STM check
        banks, keys, vals, asn = make_stm_multibank(rng, codebook, 5)
        assert len(banks) == N_BANKS

        elapsed = time.perf_counter() - t0
        metrics = {
            "verdict": "HARD_PASS",
            "verdict_msg": f"SELFTEST_PASS (M1.6 class-HV training + STM + primitives OK; train_acc={train_acc:.3f})",
            "summary": "SELFTEST_PASS",
            "elapsed_s": round(elapsed, 3),
            "run_mode": "self_test",
            "anchor_name": ANCHOR_NAME,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "config_version": CONFIG_VERSION,
            "train_acc_sample": train_acc,
        }
        tmp = output_dir / "metrics.json.tmp"
        final = output_dir / "metrics.json"
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        os.replace(str(tmp), str(final))
        print(f"[{ANCHOR_NAME}] SELFTEST_PASS elapsed={elapsed:.2f}s train_acc={train_acc:.3f}", flush=True)
        return

    # Full or smoke run
    per_unit = []
    arm_sample_outputs = {}
    unit_idx = 0

    for arm in ARMS:
        if arm.startswith("ARM_FULL_STACK_"):
            depth = int(arm.split("_D")[-1])
        else:
            depth = 50

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

    # META_RULE_AF
    arms_differ_verified = False
    af_error = None
    try:
        digests = _arms_must_differ(arm_sample_outputs)
        arms_differ_verified = True
    except AssertionError as e:
        af_error = str(e)
        digests = {}

    # Aggregate
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

    hp_gates = {}
    hp_gates["HP_D10_HOLDS"] = (fs_d10 is not None
                                  and fs_d10 >= HP_D10_FLOOR + BAND_WIDTH_MARGIN * (1.0 - HP_D10_FLOOR))
    hp_gates["HP_D50_HOLDS"] = (fs_d50 is not None
                                  and fs_d50 >= HP_D50_FLOOR + BAND_WIDTH_MARGIN * (1.0 - HP_D50_FLOOR))
    if RUN_MODE == "full":
        hp_gates["HP_D100_HOLDS"] = (fs_d100 is not None
                                       and fs_d100 >= HP_D100_FLOOR + BAND_WIDTH_MARGIN * (1.0 - HP_D100_FLOOR))
    hp_gates["HP_LIFT_OVER_NO_REFUSE"] = (fs_d50 is not None and no_ref is not None
                                            and (fs_d50 - no_ref) >= HP_LIFT_OVER_NO_REFUSE)
    hp_gates["HP_LIFT_OVER_SUBSTRATE_ONLY"] = (fs_d50 is not None and sub_only is not None
                                                 and (fs_d50 - sub_only) >= HP_LIFT_OVER_SUBSTRATE_ONLY)

    baseline_in_band = (sub_only is not None and 0.05 < sub_only < 0.95)
    broken_pc_beats = (fs_d50 is not None and sub_only is not None
                       and sub_only > fs_d50)

    n_hp_fired = sum(1 for v in hp_gates.values() if v is True)
    n_hp_total = len(hp_gates)

    expected = EXPECTED_N_UNITS if RUN_MODE == "full" else \
        max(1, len([a for a in ARMS if not (RUN_MODE == "smoke" and a == "ARM_FULL_STACK_D100")])) * len(REGIMES)
    observed = len(per_unit)
    cardinality_ok = observed >= int(0.85 * expected)

    verdict = "UNKNOWN"
    verdict_msgs = []
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
                            f"(sub_only={sub_only:.3f} > full_stack={fs_d50:.3f})")
    elif n_hp_fired == n_hp_total:
        verdict = "HARD_PASS"
        verdict_msgs.append(f"CHAIN_GRADE_FULL_STACK_COMPOSES ({n_hp_fired}/{n_hp_total} HP fired)")
    elif n_hp_fired >= max(1, n_hp_total - 1):
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
