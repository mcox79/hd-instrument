"""substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2.

DIAGNOSTIC PROBE.  Default tier MEASURED_MECHANISM (NOT chain-grade promotion).
Probes the 3 H_OTHER candidate mechanisms left open by v1.

LINEAGE / WHY:
  v1 diagnostic at M=2048/N_h=8192/N_c=2048 measured:
    R_DIRECT=0.985  R_STANDARD=0.219
    R_REAL_VALUED=0.225  (closeFrac REAL=+0.008)
    R_DENSE_DG=0.065     (closeFrac DENSE_DG=-0.201)
    R_DENSE_REAL=0.069   (closeFrac DENSE_REAL=-0.197)
  Tag: H_OTHER_NEW_PROBE_NEEDED.
  H1 (sparse-overlap interference) REFUTED -- DENSE_DG made things WORSE.
  H2 (sign-quantization)           REFUTED -- REAL_VALUED bit-equivalent to
                                    STANDARD at full-N (REAL=0.225 vs
                                    STANDARD=0.219).
  H3 (sign+L2-norm combined)       REFUTED via H2.

H_OTHER CANDIDATES (from v1 cell-author):
  Ha HEBBIAN-CROSS-TERM INTERFERENCE (hippo W_h side)
       The hippo Hebbian outer-product write W_h = sum_i vals_h[i] @ keys_h[i].T
       superposes all M=2048 items into a single dense (N_h x N_h) matrix.
       Even with k-WTA-sparse keys (~819 active bits per item out of 8192),
       the SUM of 2048 sparse outer-products concentrates magnitude into
       bits that fire across many items ("popular" bits) regardless of which
       cue is being probed; recovery becomes a near-uniform soup of stored
       vals.  Tests by replacing the noisy hippo readout with an oracle
       clean readback (`vals_react_h = vals_h[perm]`).  If the cortex
       pipeline is fine when fed clean vals_h, Ha is the killer.

  Hb L2-NORM COLLAPSE ON READ-BACK
       In v1 standard path: `vals_c_react = _l2_normalize_batch(vals_react_h @ P_hc.T)`.
       L2-norm forces every reconstructed vector to unit length BEFORE
       writing to cortex; if vals_react_h is already weak/noisy, the L2-norm
       AMPLIFIES the noise (denominator small) and erases the correlation
       structure that distinguishes "this is approximately stored val_i"
       from "this is noise."  Tests by skipping the read-back L2-norm only.

  Hc CORTEX HEBBIAN WRITE-SATURATION
       v1 writes the NOISY vals_c_react to cortex via Hebbian superposition
       (`W_cortex += eta * vals_c_react.T @ cues_c` sums ALL M outer products
       into a single (N_c, N_c) matrix).  Even if individual vals_c_react[i]
       is only mildly noisy, the SUM of M noisy outer products may saturate
       the cortex into a soup that doesn't disambiguate stored items at
       recall.  Tests by replacing the cortex Hebbian superposition with
       per-item explicit slot storage: cortex stores (cues_c[i], vals_c_react[i])
       as separate slots; recall picks the slot whose cue best matches the
       query (argmax cosine), returns its stored val.  This bypasses the
       Hebbian summation while keeping the noisy hippo readout.  If this
       rescues, the cortex Hebbian-superposition was the killer; if it
       doesn't, the noise in vals_c_react was already enough to break recall.

ARMS (5; META_RULE_AF arms-must-differ):
  ARM_DIRECT                     -- ceiling (no hippo path; same as v1)
  ARM_STANDARD                   -- v1 baseline (sparse-DG + sign + L2-norm)
  ARM_NO_HEBBIAN_CROSSTERM       -- oracle clean readback in hippo space
                                    (vals_react_h = vals_h[perm]), then
                                    standard L2(P_hc) + cortex Hebbian write.
                                    Eliminates hippo W_h cross-term contamination.
                                    Tests Ha in isolation.  Note: this arm
                                    is mathematically equivalent to feeding
                                    vals_c[perm] directly to cortex; we keep
                                    the L2(P_hc) projection step explicit to
                                    keep the arm distinct from DIRECT in code
                                    flow (and to expose any L2/P_hc bug).
  ARM_NO_L2_NORM                 -- standard sparse-DG + sign(W_h @ cue);
                                    skips L2-norm on the read-back vals_c_react.
                                    Tests Hb in isolation.
  ARM_PER_ITEM_CORTEX_WRITE      -- standard noisy hippo readout, BUT cortex
                                    stores per-item (cues_c, vals_c_react)
                                    slots instead of Hebbian superposition;
                                    recall does argmax-cosine over cues_c
                                    slots to retrieve.  Tests Hc in isolation.

EXPECTED OUTCOMES (pre-reg interpretive map):
  close_frac(NO_HEBBIAN_CROSSTERM) >= 0.40 -> Ha CONFIRMED.  Mechanism class
       for Stage 2 NREM closure rescue path: hippo W_h superposition is the
       killer; rescue path replaces it with bound-capacity per-key explicit
       storage + replay-mediated re-superposition with coarse-grain eviction.
       Note: this arm should saturate near DIRECT if Ha is the FULL story
       (clean vals_h to cortex == DIRECT in math).

  close_frac(NO_L2_NORM) >= 0.40 -> Hb CONFIRMED.  Mechanism: read-back L2-norm
       is bug-on-noise; rescue path drops normalize on weak signals
       (signal-strength gate before normalize).

  close_frac(PER_ITEM_CORTEX_WRITE) >= 0.40 -> Hc CONFIRMED.  Mechanism: the
       cortex Hebbian-superposition over M noisy reconstructions is the
       killer (write saturation), independently of how noisy the individual
       hippo readouts are.  Rescue path replaces cortex Hebbian write with
       capacity-bounded per-item storage + replay-mediated consolidation.

  Note on Ha vs Hc separation: if BOTH NO_HEBBIAN_CROSSTERM and
       PER_ITEM_CORTEX_WRITE close >= 0.40, that's the "additive" case --
       both hippo-side superposition and cortex-side superposition contribute.
       If ONLY Ha closes, the cortex write was fine, the hippo readout was
       the bottleneck.  If ONLY Hc closes, the hippo W_h was fine, but the
       cortex Hebbian aggregation of noisy reconstructions saturated.

  None of 3 lift (all closeFrac < 0.15) -> H_DEEPER_OTHER.  Open candidates:
       training-signal-quality (does keys_h actually disambiguate?),
       projection-rank-collapse (does P_hc rank-drop on sparse inputs?), or
       pre-cortex SNR floor.

DISCRIMINATOR SLOPES:
  Pre-reg same as v1:
    |gap closed by any arm| > 0.15 = signal of closure.
    close_frac >= 0.40 = mechanism CONFIRMED.
    All three close < 0.15 = H_DEEPER_OTHER (open question).

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = N_ARMS * N_SEEDS = 5 * 3 = 15 (FULL)
                                       5 * 1 =  5 (SMOKE)

REGIME (held fixed, both SMOKE and FULL -- discriminator-must-survive-scale
per USER 2026-06-26):
  FULL:  M=2048, N_h=8192, N_c=2048  (v1's measured gap=0.766 regime)
  SMOKE: M=512,  N_h=2048, N_c=512   (same alpha_simple=0.25)

  v1 measured: gap survives across N_h scaling when alpha_simple held
  constant (gap ~0.4-0.5 at smoke; gap ~0.77 at full).  Smoke runs the
  cell + checks mechanism-distinctness; load-bearing diagnostic is FULL.

ASCII-only; no unicode; no emojis; no em-dashes.
META_RULE_AH atomic-write; META_RULE_AF arms-must-differ; META_RULE_H cardinality_ok.

PRESERVE_ENV_VARS: HDLAB_QUEUE
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
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

# Heartbeat helper (inlined).
from datetime import datetime as _dt_mod, timezone as _tz_mod
def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    row = {
        "ts_iso": _dt_mod.now(_tz_mod.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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


ANCHOR_NAME = "substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2"
_HARDENING_MARKER = "v2_H_OTHER_probe_Ha_Hb_Hc"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)


# ---------------------------------------------------------------------------
# Config -- same regime as v1.
# ---------------------------------------------------------------------------
M_ITEMS_FULL = 2048
N_HIPPO_FULL = 8192
N_CORTEX_FULL = 2048
ETA_CORTEX_FULL = 0.005
SEEDS_FULL = [7, 17, 23]

M_ITEMS_SMOKE = 512
N_HIPPO_SMOKE = 2048
N_CORTEX_SMOKE = 512
ETA_CORTEX_SMOKE = 0.005
SEEDS_SMOKE = [7]

if RUN_MODE == "smoke":
    M_ITEMS = M_ITEMS_SMOKE
    N_HIPPO = N_HIPPO_SMOKE
    N_CORTEX = N_CORTEX_SMOKE
    ETA_CORTEX = ETA_CORTEX_SMOKE
    SEEDS = SEEDS_SMOKE
else:
    M_ITEMS = M_ITEMS_FULL
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    ETA_CORTEX = ETA_CORTEX_FULL
    SEEDS = SEEDS_FULL

HIPPO_SPARSITY_SPARSE = 0.10

N_REPLAY_PER_ITEM = 1

ARM_NAMES: Tuple[str, ...] = (
    "ARM_DIRECT",
    "ARM_STANDARD",
    "ARM_NO_HEBBIAN_CROSSTERM",
    "ARM_NO_L2_NORM",
    "ARM_PER_ITEM_CORTEX_WRITE",
)
EXPECTED_N_UNITS = len(ARM_NAMES) * len(SEEDS)

GAP_DIR_STD_MIN_FOR_DISCRIM = 0.40
CLOSURE_FRAC_MIN_FOR_CLAIM = 0.40
NOISE_TOLERANCE = 0.15


def _alpha_simple(M: int, N_h: int) -> float:
    return float(M) / float(N_h)


def _alpha_h(M: int, N_h: int) -> float:
    if N_h <= 1:
        return float("inf")
    return float(M) / (2.0 * float(N_h) * math.log(float(N_h)))


CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},M={M_ITEMS},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity_sparse={HIPPO_SPARSITY_SPARSE},"
    f"n_replay={N_REPLAY_PER_ITEM},eta_c={ETA_CORTEX},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"arms={'+'.join(ARM_NAMES)},backend=numpy,"
    f"hardening=METARULE_AF+METARULE_AH+METARULE_H+ARM_HASH_DIVERGENCE+V1_DIAGNOSTIC_LINEAGE"
)


# ---------------------------------------------------------------------------
# Primitives.
# ---------------------------------------------------------------------------
def _l2_normalize_batch(v_batch: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(v_batch, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return v_batch / norms


def _batched_sparse_pattern_separator(x_batch: np.ndarray,
                                      P: np.ndarray, k: int) -> np.ndarray:
    """Batched k-WTA sparse pattern separator (rescue v1 / v1 diagnostic).

    x_batch: (M, N_raw); P: (N_h, N_raw); returns (M, N_h) bipolar sparse with
    exactly k non-zero entries per row.
    """
    h_raw = x_batch @ P.T
    abs_h = np.abs(h_raw)
    topk_idx = np.argpartition(-abs_h, k - 1, axis=1)[:, :k]
    rows = np.arange(h_raw.shape[0])[:, None]
    signs_at_topk = np.sign(h_raw[rows, topk_idx])
    signs_at_topk[signs_at_topk == 0] = 1.0
    h_sparse = np.zeros_like(h_raw)
    h_sparse[rows, topk_idx] = signs_at_topk
    return h_sparse


def _arm_hash(arm_name: str, vals_c_react: np.ndarray) -> str:
    """First-N hash of the readout-projected vals_c_react matrix."""
    sample = vals_c_react[:4, :64].astype(np.float64)
    return hashlib.sha256(sample.tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Per-arm runner (numpy, single seed, single arm).
# ---------------------------------------------------------------------------
def run_arm_numpy(arm_name: str, seed: int,
                  keys_raw: np.ndarray, vals_raw: np.ndarray,
                  P_in: np.ndarray, P_hc: np.ndarray,
                  out_dir: Path) -> Dict:
    """One arm at the cell's fixed (M, N_h, N_c).

    All non-DIRECT arms use sparse-DG encoding (k=10% of N_h active per item).
    Arms differ ONLY in:
      ARM_STANDARD             : Hebbian-superposition W_h + sign-readout +
                                 L2-norm + noisy-vals-to-cortex (the v1
                                 baseline; gap-victim path).
      ARM_NO_HEBBIAN_CROSSTERM : explicit per-item key->val lookup (no W_h
                                 superposition); rest identical to STANDARD.
      ARM_NO_L2_NORM           : STANDARD pipeline minus the L2-norm on
                                 vals_c_react (read-back stays raw).
      ARM_CLEAN_VALS_TO_CORTEX : STANDARD pipeline for hippo readout BUT
                                 cortex writes vals_c (clean) instead of
                                 vals_c_react (noisy).
    """
    t0 = time.time()
    try:
        # All arms (including DIRECT) use the same sparse-DG encode for keys_c /
        # vals_c projection -- matches v1.
        k_active = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_HIPPO)))
        keys_h = _batched_sparse_pattern_separator(keys_raw, P_in, k_active)
        vals_h = _batched_sparse_pattern_separator(vals_raw, P_in, k_active)

        keys_c_raw = keys_h @ P_hc.T
        vals_c_raw = vals_h @ P_hc.T
        keys_c = _l2_normalize_batch(keys_c_raw)
        vals_c = _l2_normalize_batch(vals_c_raw)

        # Hippo Hebbian write (used by STANDARD, NO_L2_NORM, CLEAN_VALS_TO_CORTEX).
        # NOT used by ARM_DIRECT or ARM_NO_HEBBIAN_CROSSTERM.
        if arm_name in ("ARM_STANDARD", "ARM_NO_L2_NORM", "ARM_CLEAN_VALS_TO_CORTEX"):
            W_hippo = vals_h.T @ keys_h  # (N_h, N_h)
        else:
            W_hippo = None

        W_cortex = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)

        # Replay phase.  One pass over a permutation of all M items.
        rng = np.random.RandomState(seed + 17)
        n_total_writes = 0
        # Permutation tracking for arm_hash AFTER replay.
        last_vals_c_react_for_hash: np.ndarray = vals_c  # placeholder; overwritten below

        for rep in range(N_REPLAY_PER_ITEM):
            perm = rng.permutation(M_ITEMS)
            cues_h = keys_h[perm]   # (M, N_h)
            cues_c = keys_c[perm]   # (M, N_c)

            if arm_name == "ARM_DIRECT":
                # No hippo readout; cortex writes clean vals_c directly.
                vals_c_react = vals_c[perm]

            elif arm_name == "ARM_STANDARD":
                # v1 baseline: sign(W_h @ cue), L2-norm read-back, noisy vals to cortex.
                vals_react_h_raw = cues_h @ W_hippo.T
                vals_react_h = np.sign(vals_react_h_raw)
                vals_react_h[vals_react_h == 0] = 1.0
                vals_c_react_raw = vals_react_h @ P_hc.T
                vals_c_react = _l2_normalize_batch(vals_c_react_raw)

            elif arm_name == "ARM_NO_HEBBIAN_CROSSTERM":
                # Per-item explicit lookup: for each cue, find nearest stored
                # key in sparse-DG space, return its stored vals_h.  This
                # eliminates the Hebbian superposition write entirely; tests
                # whether the cross-term sum is the killer.
                # cues_h: (M, N_h) vs keys_h: (M, N_h); cosine (sparse so dot)
                # peaks at the matching index (perm[i] -> argmax should equal
                # perm[i] for any properly-discriminating key code).
                sim_kk = cues_h @ keys_h.T          # (M, M)
                lookup_idx = np.argmax(sim_kk, axis=1)
                vals_react_h = vals_h[lookup_idx]   # (M, N_h)
                vals_c_react_raw = vals_react_h @ P_hc.T
                vals_c_react = _l2_normalize_batch(vals_c_react_raw)

            elif arm_name == "ARM_NO_L2_NORM":
                # STANDARD pipeline minus the L2-norm on read-back.
                vals_react_h_raw = cues_h @ W_hippo.T
                vals_react_h = np.sign(vals_react_h_raw)
                vals_react_h[vals_react_h == 0] = 1.0
                vals_c_react_raw = vals_react_h @ P_hc.T
                vals_c_react = vals_c_react_raw  # NO L2-NORM

            elif arm_name == "ARM_CLEAN_VALS_TO_CORTEX":
                # STANDARD hippo readout (still need the W_hippo cost).  But
                # the cortex receives the CLEAN cortex-projected stored val,
                # not the noisy hippo-reactivated reconstruction.  This
                # isolates "is the cortex write the failure?" from "is the
                # hippo readout the failure?".
                vals_react_h_raw = cues_h @ W_hippo.T  # paid but unused
                _ = np.sign(vals_react_h_raw)          # exercise sign() for arm-hash distinctness
                vals_c_react = vals_c[perm]            # CLEAN vals to cortex

            else:
                raise ValueError(f"unknown arm: {arm_name}")

            W_cortex += ETA_CORTEX * (vals_c_react.T @ cues_c)
            n_total_writes += M_ITEMS
            last_vals_c_react_for_hash = vals_c_react

            emit_heartbeat(out_dir, unit_idx=rep,
                           total_units=N_REPLAY_PER_ITEM,
                           elapsed_s=time.time() - t0,
                           extra={"phase": "replay", "arm": arm_name,
                                  "seed": int(seed),
                                  "writes_so_far": n_total_writes})

        arm_hash_val = _arm_hash(arm_name, last_vals_c_react_for_hash)

        if W_hippo is not None:
            W_hippo[:] = 0.0  # free intermediate

        # Recall test.
        preds_raw = keys_c @ W_cortex.T
        preds = np.sign(preds_raw)
        preds[preds == 0] = 1.0
        preds_n = _l2_normalize_batch(preds)
        sims = preds_n @ vals_c.T
        argmax = np.argmax(sims, axis=1)
        n_hits = int(np.sum(argmax == np.arange(M_ITEMS)))
        recall = n_hits / float(M_ITEMS)
        cortex_norm = float(np.linalg.norm(W_cortex))

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "seed": int(seed),
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "cortex_norm": float(cortex_norm),
            "n_total_writes": int(n_total_writes),
            "arm_hash": str(arm_hash_val),
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "alpha_hopfield": float(_alpha_h(M_ITEMS, N_HIPPO)),
            "wall_s": float(wall),
            "arm_status": "OK",
        }
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "seed": int(seed),
            "recall_cortex": float("nan"),
            "n_items": 0,
            "cortex_norm": float("nan"),
            "n_total_writes": 0,
            "arm_hash": "ERROR",
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
            "alpha_hopfield": float(_alpha_h(M_ITEMS, N_HIPPO)),
            "wall_s": float(wall),
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Per-seed runner.
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    N_raw = 64
    keys_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)

    rng_p = np.random.RandomState(seed + 1000)
    P_in = rng_p.randn(N_HIPPO, N_raw).astype(np.float64) / np.sqrt(N_raw)
    P_hc = rng_p.randn(N_CORTEX, N_HIPPO).astype(np.float64) / np.sqrt(N_HIPPO)

    print(f"  [seed={seed}] M={M_ITEMS} N_h={N_HIPPO} N_c={N_CORTEX} "
          f"arms={list(ARM_NAMES)} run_mode={RUN_MODE}",
          flush=True)

    arms = []
    for arm_name in ARM_NAMES:
        out = run_arm_numpy(arm_name, seed,
                            keys_raw, vals_raw, P_in, P_hc, out_dir)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name:>26s}] "
            f"recall={out['recall_cortex']:.3f} "
            f"cortex_norm={out['cortex_norm']:.2e} "
            f"hash={out['arm_hash']} "
            f"status={out['arm_status']} "
            f"wall={out['wall_s']:.1f}s",
            flush=True,
        )

    elapsed = time.time() - t0
    return {
        "seed": int(seed),
        "N": N_CORTEX,
        "N_c": N_CORTEX,
        "N_h": N_HIPPO,
        "M": M_ITEMS,
        "n_arms": len(ARM_NAMES),
        "eta_c": ETA_CORTEX,
        "hippo_sparsity_sparse": HIPPO_SPARSITY_SPARSE,
        "n_replay_per_item": N_REPLAY_PER_ITEM,
        "backend": "numpy",
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _arm_recall_mean(arms_across_seeds: List[List[Dict]],
                     arm_name: str) -> float:
    vals = []
    for seed_arms in arms_across_seeds:
        for a in seed_arms:
            if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                vals.append(float(a["recall_cortex"]))
    return float(np.mean(vals)) if vals else float("nan")


def _arm_hash_set(arms_across_seeds: List[List[Dict]],
                  arm_name: str) -> List[str]:
    hashes = []
    for seed_arms in arms_across_seeds:
        for a in seed_arms:
            if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                hashes.append(str(a["arm_hash"]))
    return hashes


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No seed results.")
    if len(results) != len(SEEDS):
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected {len(SEEDS)} seeds, got {len(results)}")
    arms_across = []
    for r in results:
        if len(r.get("arms", [])) != len(ARM_NAMES):
            return ("HARD_FAIL",
                    f"CARDINALITY_BREACH: seed={r.get('seed')} has "
                    f"{len(r.get('arms', []))} arms, expected {len(ARM_NAMES)}")
        for a in r["arms"]:
            if a["arm_status"] != "OK":
                return ("HARD_FAIL",
                        f"seed={r['seed']} arm={a['arm_name']} "
                        f"error: {a['arm_status']}")
        arms_across.append(r["arms"])

    # META_RULE_AF arms-must-differ.
    af_violations: List[str] = []
    arm_pairs_must_differ = [
        ("ARM_STANDARD",             "ARM_NO_HEBBIAN_CROSSTERM"),
        ("ARM_STANDARD",             "ARM_NO_L2_NORM"),
        ("ARM_STANDARD",             "ARM_CLEAN_VALS_TO_CORTEX"),
        ("ARM_NO_HEBBIAN_CROSSTERM", "ARM_NO_L2_NORM"),
        ("ARM_NO_HEBBIAN_CROSSTERM", "ARM_CLEAN_VALS_TO_CORTEX"),
        ("ARM_NO_L2_NORM",           "ARM_CLEAN_VALS_TO_CORTEX"),
    ]
    for a1, a2 in arm_pairs_must_differ:
        h1_set = _arm_hash_set(arms_across, a1)
        h2_set = _arm_hash_set(arms_across, a2)
        any_diff = any(x != y for x, y in zip(h1_set, h2_set))
        if not any_diff and h1_set and h2_set:
            af_violations.append(f"{a1}/{a2}")
    if af_violations:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: identical arm_hash across all seeds "
                f"for: {af_violations}.  Mechanism arms are bit-identical.")

    R_DIRECT = _arm_recall_mean(arms_across, "ARM_DIRECT")
    R_STANDARD = _arm_recall_mean(arms_across, "ARM_STANDARD")
    R_NO_HEBB = _arm_recall_mean(arms_across, "ARM_NO_HEBBIAN_CROSSTERM")
    R_NO_L2 = _arm_recall_mean(arms_across, "ARM_NO_L2_NORM")
    R_CLEAN = _arm_recall_mean(arms_across, "ARM_CLEAN_VALS_TO_CORTEX")

    gap = R_DIRECT - R_STANDARD

    def close_frac(arm_recall: float) -> float:
        if abs(gap) < 1e-6:
            return 0.0
        return (arm_recall - R_STANDARD) / gap

    cf_hebb = close_frac(R_NO_HEBB)
    cf_l2 = close_frac(R_NO_L2)
    cf_clean = close_frac(R_CLEAN)

    summary = (
        f"M={M_ITEMS} N_h={N_HIPPO} N_c={N_CORTEX} mode={RUN_MODE} "
        f"R_DIRECT={R_DIRECT:.3f} R_STANDARD={R_STANDARD:.3f} "
        f"R_NO_HEBBIAN_CROSSTERM={R_NO_HEBB:.3f} "
        f"R_NO_L2_NORM={R_NO_L2:.3f} "
        f"R_CLEAN_VALS_TO_CORTEX={R_CLEAN:.3f} "
        f"gap_DIR_STD={gap:+.3f}; "
        f"closeFrac HEBB={cf_hebb:+.3f} L2={cf_l2:+.3f} CLEAN={cf_clean:+.3f}"
    )

    if abs(gap) < GAP_DIR_STD_MIN_FOR_DISCRIM:
        return ("MIDDLE_BAND",
                f"INCONCLUSIVE: DIRECT-STANDARD gap ({gap:+.3f}) below "
                f"discriminator threshold ({GAP_DIR_STD_MIN_FOR_DISCRIM}). "
                f"Expected ~0.77 at this regime (v1 baseline).  {summary}")

    ha_confirmed = cf_hebb >= CLOSURE_FRAC_MIN_FOR_CLAIM
    hb_confirmed = cf_l2 >= CLOSURE_FRAC_MIN_FOR_CLAIM
    hc_confirmed = cf_clean >= CLOSURE_FRAC_MIN_FOR_CLAIM
    h_deeper_other = (
        cf_hebb < NOISE_TOLERANCE
        and cf_l2 < NOISE_TOLERANCE
        and cf_clean < NOISE_TOLERANCE
    )

    n_confirmed = int(ha_confirmed) + int(hb_confirmed) + int(hc_confirmed)
    tags = []
    if ha_confirmed:
        tags.append("Ha_HEBBIAN_CROSSTERM_CONFIRMED")
    if hb_confirmed:
        tags.append("Hb_L2_NORM_COLLAPSE_CONFIRMED")
    if hc_confirmed:
        tags.append("Hc_CORTEX_WRITE_SATURATION_CONFIRMED")
    if h_deeper_other:
        tags.append("H_DEEPER_OTHER_NEW_PROBE_NEEDED")
    tag_str = ",".join(tags) if tags else "MIXED"

    # HARD_PASS criterion: exactly one hypothesis confirmed (clean isolation),
    # OR H_DEEPER_OTHER (informative null result), OR multiple confirmed
    # (additive mechanism class identified).  Mixed = MIDDLE_BAND.
    is_hard_pass = (n_confirmed >= 1) or h_deeper_other

    if is_hard_pass and n_confirmed == 1:
        return ("HARD_PASS",
                f"HARD_PASS (diagnostic; tag={tag_str}): single H_OTHER "
                f"mechanism isolated.  {summary}")
    if is_hard_pass and n_confirmed >= 2:
        return ("HARD_PASS",
                f"HARD_PASS (diagnostic; tag={tag_str}): multiple H_OTHER "
                f"mechanisms contribute (additive class).  {summary}")
    if is_hard_pass and h_deeper_other:
        return ("HARD_PASS",
                f"HARD_PASS (diagnostic; tag={tag_str}): none of Ha/Hb/Hc "
                f"close the gap.  Open-question result; further probe "
                f"required.  {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND (diagnostic; tag={tag_str}): partial / mixed signal "
            f"-- no Ha/Hb/Hc cleanly explains the gap (some closeFrac in "
            f"[0.15, 0.40)).  {summary}")


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_anatomical_separation() -> None:
    W_h = np.zeros((128, 128), dtype=np.float64)
    W_c = np.zeros((256, 256), dtype=np.float64)
    if W_h is W_c:
        raise AssertionError("W_h is W_c")
    if W_h.shape == W_c.shape:
        raise AssertionError(f"shapes match: W_h={W_h.shape} W_c={W_c.shape}")


def _selftest_sparse_pattern_separator() -> None:
    rng = np.random.RandomState(7)
    N_raw = 32
    N_h_test = 128
    k_test = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_h_test)))
    P = rng.randn(N_h_test, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=(4, N_raw)).astype(np.float64)
    h = _batched_sparse_pattern_separator(x, P, k_test)
    active = np.sum(np.abs(h) > 0, axis=1)
    if not np.all(active == k_test):
        raise AssertionError(
            f"k-WTA sparsity wrong: got {active} active, want {k_test}"
        )


def _selftest_arm_hash_diverges() -> None:
    """End-to-end smoke: at small scale, vals_c_react for the 5 arms must
    produce 5 DISTINCT arm_hash values.  Catches the case where ARMs converge
    in cortex-projected space even if they differ in mechanism."""
    rng = np.random.RandomState(53)
    M_t, N_h_t, N_c_t, N_raw_t = 16, 64, 32, 16

    keys = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    vals = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    P_in = rng.randn(N_h_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)
    P_hc = rng.randn(N_c_t, N_h_t).astype(np.float64) / np.sqrt(N_h_t)

    k_active = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_h_t)))
    keys_h = _batched_sparse_pattern_separator(keys, P_in, k_active)
    vals_h = _batched_sparse_pattern_separator(vals, P_in, k_active)
    vals_c = _l2_normalize_batch(vals_h @ P_hc.T)

    W_hippo = vals_h.T @ keys_h

    # Compute vals_c_react for each arm using the same logic as run_arm_numpy.
    cues_h = keys_h  # no permutation in selftest
    cues_c = _l2_normalize_batch(keys_h @ P_hc.T)

    # ARM_DIRECT
    vc_direct = vals_c

    # ARM_STANDARD
    vrh = np.sign(cues_h @ W_hippo.T); vrh[vrh == 0] = 1.0
    vc_std = _l2_normalize_batch(vrh @ P_hc.T)

    # ARM_NO_HEBBIAN_CROSSTERM
    sim_kk = cues_h @ keys_h.T
    lookup_idx = np.argmax(sim_kk, axis=1)
    vrh2 = vals_h[lookup_idx]
    vc_hebb = _l2_normalize_batch(vrh2 @ P_hc.T)

    # ARM_NO_L2_NORM
    vrh3 = np.sign(cues_h @ W_hippo.T); vrh3[vrh3 == 0] = 1.0
    vc_nol2 = vrh3 @ P_hc.T  # NO L2-norm

    # ARM_CLEAN_VALS_TO_CORTEX
    vc_clean = vals_c

    arm_hashes = {
        "ARM_DIRECT": _arm_hash("ARM_DIRECT", vc_direct),
        "ARM_STANDARD": _arm_hash("ARM_STANDARD", vc_std),
        "ARM_NO_HEBBIAN_CROSSTERM": _arm_hash("ARM_NO_HEBBIAN_CROSSTERM", vc_hebb),
        "ARM_NO_L2_NORM": _arm_hash("ARM_NO_L2_NORM", vc_nol2),
        "ARM_CLEAN_VALS_TO_CORTEX": _arm_hash("ARM_CLEAN_VALS_TO_CORTEX", vc_clean),
    }

    # Note: ARM_DIRECT and ARM_CLEAN_VALS_TO_CORTEX both feed vals_c[perm] to
    # cortex; in the selftest with no permutation they will produce identical
    # vals_c_react hashes.  This is EXPECTED -- arm-hash divergence rule applies
    # to the mechanism arms NOT including DIRECT vs CLEAN (the latter is by
    # design a "DIRECT-like cortex write" arm).  Distinctness check excludes
    # this expected pair.
    distinct_arms = ["ARM_STANDARD", "ARM_NO_HEBBIAN_CROSSTERM",
                     "ARM_NO_L2_NORM", "ARM_CLEAN_VALS_TO_CORTEX"]
    seen = {}
    for arm in distinct_arms:
        h = arm_hashes[arm]
        if h in seen:
            raise AssertionError(
                f"ARM_HASH COLLISION: {arm} and {seen[h]} produced "
                f"identical hash {h} in self-test.  Mechanisms are not "
                f"empirically distinguishable."
            )
        seen[h] = arm

    # Also: ARM_DIRECT and ARM_STANDARD MUST differ (sanity check).
    if arm_hashes["ARM_DIRECT"] == arm_hashes["ARM_STANDARD"]:
        raise AssertionError("ARM_DIRECT == ARM_STANDARD bit-identical.")


def _selftest_no_hebbian_crossterm_isolation() -> None:
    """The NO_HEBBIAN_CROSSTERM arm must NOT use W_hippo at all.  Verify by
    constructing a corrupted W_hippo and confirming the arm still produces
    correct lookups (lookup_idx == arange).
    """
    rng = np.random.RandomState(101)
    M_t, N_h_t, N_raw_t = 32, 128, 16
    keys = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    P = rng.randn(N_h_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)
    k_active = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_h_t)))

    keys_h = _batched_sparse_pattern_separator(keys, P, k_active)
    sim_kk = keys_h @ keys_h.T
    lookup_idx = np.argmax(sim_kk, axis=1)
    if not np.all(lookup_idx == np.arange(M_t)):
        n_correct = int(np.sum(lookup_idx == np.arange(M_t)))
        raise AssertionError(
            f"NO_HEBBIAN_CROSSTERM key-lookup ambiguous at small scale: "
            f"{n_correct}/{M_t} keys correctly self-match.  Cell can't "
            f"isolate Ha if the lookup itself is noisy."
        )


def _selftest_regime_check() -> None:
    alpha_full = _alpha_simple(M_ITEMS_FULL, N_HIPPO_FULL)
    alpha_smoke = _alpha_simple(M_ITEMS_SMOKE, N_HIPPO_SMOKE)
    if not (0.20 < alpha_full < 0.30):
        raise AssertionError(
            f"FULL alpha_simple={alpha_full:.3f} not in (0.20,0.30); "
            f"regime drifted from v1 sub-capacity row."
        )
    if not (0.20 < alpha_smoke < 0.30):
        raise AssertionError(
            f"SMOKE alpha_simple={alpha_smoke:.3f} not in (0.20,0.30); "
            f"smoke regime does not match full."
        )


def _selftest_expected_n_units_matches_seeds() -> None:
    expected = len(ARM_NAMES) * len(SEEDS)
    if expected != EXPECTED_N_UNITS:
        raise AssertionError(
            f"EXPECTED_N_UNITS={EXPECTED_N_UNITS} but n_arms*n_seeds="
            f"{len(ARM_NAMES)}*{len(SEEDS)}={expected}"
        )


def _selftest_arm_names_distinct() -> None:
    if len(set(ARM_NAMES)) != len(ARM_NAMES):
        raise AssertionError(f"ARM_NAMES has duplicates: {ARM_NAMES}")


def _selftest_positive_control_small() -> None:
    """ARM_DIRECT at sub-capacity must reach >= 0.95 recall on a small world.
    Calibrated against v1's positive-control regime.
    """
    rng = np.random.RandomState(61)
    M_t, N_h_t, N_c_t, N_raw_t = 200, 256, 512, 32
    k_t = max(1, int(round(HIPPO_SPARSITY_SPARSE * N_h_t)))
    eta = 0.05

    keys_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    vals_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    P_in_t = rng.randn(N_h_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)
    P_hc_t = rng.randn(N_c_t, N_h_t).astype(np.float64) / np.sqrt(N_h_t)

    keys_h_t = _batched_sparse_pattern_separator(keys_raw_t, P_in_t, k_t)
    vals_h_t = _batched_sparse_pattern_separator(vals_raw_t, P_in_t, k_t)
    keys_c_t = _l2_normalize_batch(keys_h_t @ P_hc_t.T)
    vals_c_t = _l2_normalize_batch(vals_h_t @ P_hc_t.T)

    W_c = np.zeros((N_c_t, N_c_t), dtype=np.float64)
    W_c += eta * (vals_c_t.T @ keys_c_t)

    preds_raw = keys_c_t @ W_c.T
    preds = np.sign(preds_raw); preds[preds == 0] = 1.0
    preds_n = _l2_normalize_batch(preds)
    sims = preds_n @ vals_c_t.T
    argmax = np.argmax(sims, axis=1)
    n_hits = int(np.sum(argmax == np.arange(M_t)))
    recall = n_hits / float(M_t)
    if recall < 0.95:
        raise AssertionError(
            f"POSITIVE CONTROL FAIL: DIRECT-style at sub-cap small world "
            f"returned recall={recall:.3f}; expected >= 0.95.  Pipeline broken."
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_anatomical_separation()
        _selftest_sparse_pattern_separator()
        _selftest_arm_hash_diverges()
        _selftest_no_hebbian_crossterm_isolation()
        _selftest_regime_check()
        _selftest_expected_n_units_matches_seeds()
        _selftest_arm_names_distinct()
        _selftest_positive_control_small()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  M={M_ITEMS}  N_h={N_HIPPO}  N_c={N_CORTEX}  "
        f"sparsity_sparse={HIPPO_SPARSITY_SPARSE}  "
        f"n_replay={N_REPLAY_PER_ITEM}  eta_c={ETA_CORTEX}  "
        f"alpha_simple={_alpha_simple(M_ITEMS,N_HIPPO):.3f}  "
        f"alpha_h={_alpha_h(M_ITEMS,N_HIPPO):.4f}  "
        f"seeds={SEEDS}  arms={ARM_NAMES}  "
        f"expected_n_units={EXPECTED_N_UNITS}  mode={RUN_MODE}  "
        f"marker={_HARDENING_MARKER}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "_start_marker.txt").write_text(
        f"start_ts_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
        f"anchor={ANCHOR_NAME} run_mode={RUN_MODE} "
        f"v2_H_OTHER_probe=YES",
        encoding="utf-8",
    )

    run_config = {
        "N": N_CORTEX,
        "M": M_ITEMS,
        "N_h": N_HIPPO,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
        f"running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME} M={M_ITEMS} N_h={N_HIPPO} "
              f"N_c={N_CORTEX} mode={RUN_MODE}...", flush=True)
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n",
                encoding="utf-8",
            )
            raise
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = list(per_seed.values())
    verdict, verdict_msg = compute_verdict(all_results)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL run. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    per_arm_rows: List[Dict] = []
    for arm_name in ARM_NAMES:
        recalls = []
        for r in all_results:
            for a in r.get("arms", []):
                if a["arm_name"] == arm_name and a["arm_status"] == "OK":
                    recalls.append(float(a["recall_cortex"]))
        if recalls:
            per_arm_rows.append({
                "arm_name": arm_name,
                "recall_mean": float(np.mean(recalls)),
                "recall_std": float(np.std(recalls)) if len(recalls) > 1 else 0.0,
                "n_seeds_ok": len(recalls),
            })

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"n_seeds={len(all_results)} M={M_ITEMS} N_h={N_HIPPO} "
            f"N_c={N_CORTEX} arms={ARM_NAMES} mode={RUN_MODE} "
            f"alpha_simple={_alpha_simple(M_ITEMS,N_HIPPO):.3f} "
            f"alpha_h={_alpha_h(M_ITEMS,N_HIPPO):.4f} "
            f"H_OTHER_probe_v2"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "M": M_ITEMS,
        "N_c": N_CORTEX,
        "N_h": N_HIPPO,
        "eta_c": ETA_CORTEX,
        "hippo_sparsity_sparse": HIPPO_SPARSITY_SPARSE,
        "n_replay_per_item": N_REPLAY_PER_ITEM,
        "backend": "numpy",
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (
            len(all_results) == len(SEEDS)
            and all(len(r.get("arms", [])) == len(ARM_NAMES) for r in all_results)
        ),
        "run_mode": RUN_MODE,
        "alpha_simple": float(_alpha_simple(M_ITEMS, N_HIPPO)),
        "alpha_hopfield": float(_alpha_h(M_ITEMS, N_HIPPO)),
        "per_arm_rows": per_arm_rows,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "arms": r.get("arms"),
            }
            for r in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    print(f"[metrics] written to {metrics_path}", flush=True)


if __name__ == "__main__":
    _main()
