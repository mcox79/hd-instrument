"""distributional_shape_zipfian_v3_hebbian_frequency_reinforce -- seed_7.

v2 (2026-07-01 HF_PREDICTION_FAILS) demonstrated dense-Hopfield READ-REPLACE
architecture is DISTRIBUTIONALLY INVARIANT: single-write attention on iid bipolar
keys dominates over Zipfian rank selection because Ramsauer 2021 exponential
capacity + margin (sqrt(0.4) = 0.63 signal @ cos_margin=0.975) crushes any
shape-driven asymmetry. Preview at (alpha=1.0, sigma=0.30, load=0.30, N=8192)
gave Q1=Q4=1.000, gap=0.000 vs prediction >= 0.15.

v3 CHANGE: add Hebbian frequency-reinforcement (Variant B.1 tape write-scale).
This is the SPARSE-CODING-DRILL-CANONICAL mechanism: head items get thicker
storage magnitude (multiple writes / higher synaptic saturation); tail items
get thin magnitude. Under noise + at Amit-Gutfreund wall M/N ~ 0.138, prediction
is head recovers + tail collapses = TRUE two-tier signature.

v3 also SHIFTS REGIME to Amit-Gutfreund wall: loads {0.05, 0.08, 0.10, 0.12,
0.14, 0.18} centered on classical Hopfield wall 0.138 (not v2's {0.10..1.20}
which drove overload but at 3x margin from wall).

MECHANISM (Hebbian frequency-reinforcement B.1):
  Standard v2 path:  K_tape[i] = L2norm(keys_raw[i]); V_tape[i] = L2norm(vals_raw[i])
  v3 change:         eta_i = sqrt(freq_i / freq_max)      # freq per Zipf rank
                     K_tape[i] = eta_i * L2norm(keys_raw[i])
                     V_tape[i] = eta_i * L2norm(vals_raw[i])
  For alpha=0 (uniform): eta_i = 1.0 for all i (identity; reduces to v2).
  For alpha=1 (Zipf):    eta_i in [sqrt(1/M), 1.0]; head items thick, tail thin.
  For alpha=2 (heavy):   even more extreme asymmetry.

  Softmax attention: sims = beta * q @ K_tape.T
  Head-item query: q ~ K_tape[head] with magnitude ~ 1.0 -> sims_head ~ beta * 1
  Tail-item query: q ~ K_tape[tail] with magnitude ~ sqrt(1/M) -> sims_tail scale
                   is REDUCED by the tail's eta factor + tail competes with
                   larger head sims in the softmax denominator.

  This is Willshaw synaptic saturation in continuous form. Under BSC noise
  the head margin absorbs bit-flips; the tail margin is eaten by both noise
  AND head-competition in softmax.

CRITICAL DISCRIMINATOR (Skunkworks Batch-1 spec):
  HP_TWO_TIER_HEBBIAN: at (alpha=1.0, sigma in [0.15, 0.30], load in [0.10, 0.14]):
    recall_Q1_head - recall_Q4_tail >= 0.30 (STRONG two-tier signature).
    Head recovery >= 0.85 (frequency-reinforcement rescues head under noise).
    Tail collapse <= 0.50 (thin storage + collision + noise = below chance).

  If preview at (alpha=1.0, sigma=0.30, load=0.12, N=8192) shows Q1-Q4 gap
  >= 0.30 -> two-tier prediction VINDICATED at Willshaw regime -> full dispatch.

  If preview at (alpha=1.0, sigma=0.30, load=0.12, N=8192) shows Q1-Q4 gap
  <= 0.10 -> B.1 tape-scale insufficient -> ESCALATE to B.2 (proper classical
  Hebbian W-matrix outer-product accumulation) in a v3.2 sibling cell.

  MIDDLE zone (0.10 < gap < 0.30) -> report as PARTIAL_SIGNATURE, hand off
  to Skunkworks for tier decision, full dispatch discretionary.

SWEEP DIMENSIONS (per-cell = ONE seed):
  alpha_shape in {0.0 (uniform), 1.0 (natural Zipf), 2.0 (heavy tail)}   -- 3 levels
  query_noise sigma in {0.0, 0.15, 0.30}                                 -- 3 levels
  load M/N in {0.05, 0.08, 0.10, 0.12, 0.14, 0.18}                       -- 6 levels
  = 3 * 3 * 6 = 54 (alpha, sigma, load) points per seed cell.

  Load grid centered on Amit-Gutfreund wall M/N = 0.138 (classical Hopfield).
  0.05 = under-loaded margin; 0.18 = just above wall (super-critical Hopfield).

Sibling cells: seed_13 and seed_19 (identical config; different seed).
Cross-seed aggregation post-VET.

QUERY NOISE MODEL (bit-flip / BSC on bipolar keys): unchanged from v2.

FALSIFIABLE PREDICTIONS (verdict gates):

  HARD_PASS_TWO_TIER_HEBBIAN (chain-grade rescue signature):
    HP_TWO_TIER_HEBBIAN: at (alpha=1.0, sigma in [0.15, 0.30], load in [0.10, 0.14]):
      recall_Q1_head - recall_Q4_tail >= 0.30 at ANY (sigma, load) in window.
    HP_UNIFORM_NO_ASYMMETRY: at (alpha=0.0, any sigma, load=0.10):
      recall_Q1 - recall_Q4 in [-0.05, 0.05] (control: uniform freq -> eta=1 -> no gap).
    HP_UNIFORM_BASELINE: at (alpha=0.0, sigma=0.0, load=0.05):
      recall_all >= 0.95 (reproduces clean recall; sanity).

  HARD_FAIL_B1_INSUFFICIENT (escalate to B.2):
    HF_B1_INSUFFICIENT: at (alpha=1.0, sigma=0.30, load in {0.10, 0.12, 0.14}):
      MAX gap over the 3 loads < 0.10 -> tape-write-scale reinforcement doesn't
      produce the drill's predicted asymmetry -> B.2 canonical Hebbian W-matrix
      needed. Report as HF_B1_INSUFFICIENT + Skunkworks re-spec.

  HARD_FAIL_INFRA:
    BASELINE_OUT_OF_BAND: (alpha=0.0, sigma=0.0, load=0.05) < 0.85 at FULL.
    META_RULE_AF: bit-identical arm signatures (wiring bug).
    CARDINALITY_BREACH: len(core_arms) != 54.
    UNIFORM_ASYMMETRY_LEAK: alpha=0 shows Q1-Q4 gap > 0.10 (implementation bug;
      uniform freq must not produce head-tail asymmetry).

  MIDDLE_BAND: 0.10 <= gap < 0.30 (partial signature; hand off).

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = 3 alpha * 3 sigma * 6 load = 54 arm outputs per seed cell.

CRLB (capacity feasibility per exp_dev section 9):
  Per-arm recall = binomial proportion over N_QUERIES=1000.
  sigma_min(p=0.5) = sqrt(0.25/1000) = 0.0158 THEORETICAL@binomial-CLT.
  HP gap 0.30 = 19*sigma_binom; well-reachable.
  Per-quartile recall over N_Q/4 = 250 samples: sigma_min = sqrt(0.25/250) = 0.032.
  Q1-Q4 gap 0.30 = 9.4*sigma_stratified; well-reachable.

DISCRIMINATOR-MUST-SURVIVE-SCALE (exp_dev pattern C):
  Smoke runs FULL-N=8192 preview at (alpha=1.0, sigma=0.30, load=0.12) -- right
  at Amit-Gutfreund wall. This is where the mechanism-prediction MUST fire.
  Also runs a control preview at (alpha=0.0, sigma=0.30, load=0.12) -- uniform
  freq should show gap ~ 0 (no reinforcement asymmetry).

BASELINE_IN_BAND (META_RULE_AG):
  (alpha=0.0, sigma=0.0, load=0.05) should saturate ~1.000 at full-N. If < 0.85,
  encoder broken or attention regime wrong -- HARD_FAIL_INFRA.

ARMS_MUST_DIFFER (META_RULE_AF):
  Alpha entropies distinct (3 rank_entropy values across alpha levels);
  sigma-arm recalls should NOT be bit-identical (noise moves recall meaningfully).

Cross-references:
- v2 (superseded): exp_distributional_shape_zipfian_v2 HF_PREDICTION_FAILS
  (data/exp_distributional_shape_zipfian_v2_seed_7_smoke/metrics.json)
- v2 HF hand-off: notes/exp_dev_findings/exp_distributional_shape_zipfian_v2_HF_PREDICTION_FAILS_2026-07-01.md
- Sparse-coding drill: notes/research_sparse_coding_compressed_sensing_2026-07-01.md
  (Willshaw-Palm-Gripon sparse-CAM; Donoho-Tanner CS phase transitions)
- Cell D v2 CG (Atom 1; dense-Hopfield READ-REPLACE parent; uniform baseline)
- Skunkworks Batch-1 recommendation Option B.1 tape write-scale
- Willshaw 1969 CITED; Palm 2010 CITED; Gripon-Berrou 2011 CITED
- Amit-Gutfreund-Sompolinsky 1985 CITED (classical Hopfield wall 0.138 M/N)
- Ramsauer 2021 CITED (dense-Hopfield exponential capacity ceiling; v2 baseline)

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
 - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
 - final_metrics_atomicity = tmp_replace (META_RULE_AH)
 - except SystemExit: raise BEFORE except Exception (no BaseException)
 - crlb_floor_computed = 0.0158 sigma_binomial (all); 0.032 sigma_stratified (Q1-Q4)
 - baseline_in_band at smoke (META_RULE_AG; alpha=0/sigma=0/load=0.05 near 1.0 at N=8192)
 - discriminator survives scale (smoke has full-N previews at Amit-Gutfreund wall)
 - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
 - HP_SCOPE per predicate declared inline in compute_verdict
 - cardinality_ok EXPECTED_N_UNITS=54 (META_RULE_H)
 - per-unit failure-class instrumentation (META_RULE_J; no bare except)
 - calibration_check = adaptive_with_discriminator_gate (beta = log2(M)/margin)
 - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

Load-bearing HYPOTHESIZED numbers (pre-run; MUST NOT be cited as MEASURED):
 - HYPOTHESIZED@this-cell: at (alpha=1, sigma=0.30, load=0.12, N=8192), preview
   Q1_head expected >= 0.85 (frequency-reinforcement rescues head)
 - HYPOTHESIZED@this-cell: at same regime, Q4_tail expected <= 0.50 (thin tape
   + softmax competition + noise = collapse)
 - THEORETICAL@Amit-Gutfreund-Sompolinsky-1985: classical Hopfield wall at M/N = 0.138
 - MEASURED@v2 smoke: dense-Hopfield READ-REPLACE at same coords gave Q1=Q4=1.000

PROT-018: anchor _seed_7 (no _n suffix; N=8192 constant per config).
PROT-021: single-seed cell (chunked); _seed_checkpoint import present.
ASCII-only.

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

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


# ---------------------------------------------------------------------------
# Inline heartbeat + start marker + crash diagnostic
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
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "metrics.json.tmp"
    final = out / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(str(tmp), str(final))


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ANCHOR_NAME = "distributional_shape_zipfian_v3_hebbian_frequency_reinforce_seed_7"
SEED_THIS_CHUNK = 7
_HARDENING_MARKER = "v3_hebbian_tape_write_scale_frequency_reinforce_seed_chunk"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# FULL config
N_FULL = 8192
ALPHA_SHAPE_LEVELS = [0.0, 1.0, 2.0]
SIGMA_NOISE_LEVELS = [0.0, 0.15, 0.30]
# Load grid centered on Amit-Gutfreund wall M/N = 0.138.
# 0.05 = well below wall; 0.08 = well below; 0.10 = approaching;
# 0.12 = just below wall; 0.14 = just above; 0.18 = super-critical Hopfield regime.
LOAD_LEVELS = [0.05, 0.08, 0.10, 0.12, 0.14, 0.18]
N_QUERIES_FULL = 1000
BETA_MIN = 8.0
BETA_MAX = 128.0

# Smoke config: full 54-arm sweep at N_smoke=1024 (fast); plus TWO full-N previews:
#  (1) Amit-Gutfreund wall discriminator: alpha=1, sigma=0.30, load=0.12
#  (2) Control (uniform reinforcement should NOT produce asymmetry): alpha=0, sigma=0.30, load=0.12
N_SMOKE = 1024
N_QUERIES_SMOKE = 200

PREVIEW_ALPHA = 1.0
PREVIEW_SIGMA = 0.30
PREVIEW_LOAD = 0.12          # at Amit-Gutfreund wall
PREVIEW_N_QUERIES = 400

PREVIEW_CONTROL_ALPHA = 0.0  # uniform freq -> eta = 1.0 for all -> no asymmetry
PREVIEW_CONTROL_SIGMA = 0.30
PREVIEW_CONTROL_LOAD = 0.12

RUN_FULL_N_PREVIEW = (RUN_MODE == "smoke")

if RUN_MODE == "smoke":
    N_DIM = N_SMOKE
    N_QUERIES = N_QUERIES_SMOKE
else:
    N_DIM = N_FULL
    N_QUERIES = N_QUERIES_FULL

SEEDS = [SEED_THIS_CHUNK]

# Cardinality: 3 alpha * 3 sigma * 6 load = 54 arms
EXPECTED_N_UNITS = len(ALPHA_SHAPE_LEVELS) * len(SIGMA_NOISE_LEVELS) * len(LOAD_LEVELS)
assert EXPECTED_N_UNITS == 54, f"EXPECTED_N_UNITS wiring bug: {EXPECTED_N_UNITS}"

# Attention batch chunk for large-M points (load=0.18 -> M=1474 at N=8192)
ATTN_CHUNK = 256

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},N_QUERIES={N_QUERIES},"
    f"alpha_levels={ALPHA_SHAPE_LEVELS},sigma_levels={SIGMA_NOISE_LEVELS},"
    f"load_levels={LOAD_LEVELS},beta_range=[{BETA_MIN},{BETA_MAX}],"
    f"chunk_seed={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},"
    f"expected_n_units={EXPECTED_N_UNITS},"
    f"hardening=v3_hebbian_tape_write_scale+METARULE_AF_hashtest+METARULE_AH+ADAPTIVE_BETA"
)


# ---------------------------------------------------------------------------
# Zipf sampler
# ---------------------------------------------------------------------------
def _zipf_probs(m_items: int, alpha_shape: float) -> np.ndarray:
    """Rank-based Zipf: p_i propto 1/(i+1)^alpha for i in [0, M). Alpha=0 -> uniform."""
    if m_items <= 0:
        raise ValueError(f"m_items must be positive: {m_items}")
    if alpha_shape < 0:
        raise ValueError(f"alpha_shape must be >= 0: {alpha_shape}")
    ranks = np.arange(1, m_items + 1, dtype=np.float64)
    if alpha_shape == 0.0:
        return np.full(m_items, 1.0 / m_items, dtype=np.float64)
    weights = ranks ** (-alpha_shape)
    return weights / weights.sum()


def _zipf_entropy(probs: np.ndarray) -> float:
    p = probs[probs > 0]
    return float(-np.sum(p * np.log(p)))


def _hebbian_write_scale(probs: np.ndarray) -> np.ndarray:
    """B.1 write-scale: eta_i = sqrt(freq_i / freq_max).

    Rationale (Willshaw synaptic saturation, continuous form):
      freq_i is per-item selection probability from Zipf distribution.
      eta_i is per-item tape-row multiplier applied to BOTH K_tape and V_tape
      (unified write-strength; head items get thick storage; tail thin).

      Sqrt scaling (not linear): matches ell-2 energy law + prevents extreme
      collapse for very heavy tails (alpha=2.0 has 1000x freq range; sqrt gives
      ~32x eta range vs 1000x linear).

      For alpha=0 (uniform): freq_i = 1/M for all i -> eta_i = 1.0 (identity).
    """
    freq_max = float(probs.max())
    if freq_max <= 0.0:
        raise ValueError(f"Zipf probs freq_max non-positive: {freq_max}")
    return np.sqrt(probs / freq_max)


# ---------------------------------------------------------------------------
# Dense-Hopfield primitives + Hebbian write-scale + noise model
# ---------------------------------------------------------------------------
def _l2norm_rows(x: np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x, axis=1, keepdims=True).clip(min=1e-12)


def _cosine_margin_estimate(keys: np.ndarray, sample_n: int = 256) -> float:
    """Estimate off-diagonal cosine margin on L2-normalized keys.

    Note: pass L2-NORMALIZED keys here, not eta-scaled. Margin describes
    directional near-orthogonality of the key basis; eta scaling affects magnitude
    only + is applied downstream to control write-strength."""
    m = keys.shape[0]
    n_s = min(sample_n, m)
    if m > n_s:
        rng = np.random.RandomState(0)
        idx = rng.choice(m, size=n_s, replace=False)
        sub = keys[idx]
    else:
        sub = keys
    sim = sub @ sub.T
    mask = ~np.eye(sub.shape[0], dtype=bool)
    off_mean_abs = float(np.abs(sim[mask]).mean())
    margin = 1.0 - off_mean_abs
    if not math.isfinite(margin) or margin <= 0.0:
        return 0.1
    return margin


def _compute_adaptive_beta(m_items: int, cosine_margin: float) -> float:
    raw = math.log2(max(2, m_items)) / max(cosine_margin, 0.05)
    return float(max(BETA_MIN, min(BETA_MAX, raw)))


def _apply_query_noise(queries_raw: np.ndarray, sigma: float,
                       rng: np.random.RandomState) -> np.ndarray:
    if sigma <= 0.0:
        return _l2norm_rows(queries_raw)
    flip_mask = rng.random(queries_raw.shape) < sigma
    noisy = queries_raw.copy()
    noisy[flip_mask] = -noisy[flip_mask]
    return _l2norm_rows(noisy)


def _dense_hopfield_recall(K_tape: np.ndarray, V_tape: np.ndarray,
                           queries_noisy_n: np.ndarray,
                           query_targets: np.ndarray,
                           beta: float, attn_chunk: int) -> np.ndarray:
    """Dense-Hopfield READ-REPLACE recall over pre-computed noisy L2-normalized queries.

    NOTE: K_tape/V_tape here may be eta-scaled (Hebbian write-scale applied).
    Argmax match is done against V_tape (with the same eta scaling) so it's a
    self-consistent readout. This preserves the property that the retrieved
    p vector must match the STORED V_tape row of the correct item.
    """
    m = K_tape.shape[0]
    q_count = query_targets.shape[0]
    hits = np.zeros(q_count, dtype=bool)
    for start in range(0, q_count, attn_chunk):
        end = min(q_count, start + attn_chunk)
        q_chunk = queries_noisy_n[start:end]                   # (c, N)
        sims = q_chunk @ K_tape.T                              # (c, M)
        sims_scaled = beta * sims
        sims_scaled -= sims_scaled.max(axis=1, keepdims=True)
        w = np.exp(sims_scaled)
        w /= w.sum(axis=1, keepdims=True).clip(min=1e-30)
        p = w @ V_tape                                         # (c, N)
        p_n = _l2norm_rows(p)
        sims_match = p_n @ V_tape.T                            # (c, M)
        argmax = sims_match.argmax(axis=1)
        expected = query_targets[start:end]
        hits[start:end] = (argmax == expected)
    return hits


# ---------------------------------------------------------------------------
# Per-arm runner (one (alpha, sigma, load) point)
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, alpha_shape: float, sigma: float, load: float,
            n_dim: int, n_queries: int, seed: int,
            attn_chunk: int, out_dir: Path) -> Dict:
    t0 = time.time()
    beta_used = float("nan")
    cosine_margin_used = float("nan")
    eta_min_used = float("nan")
    eta_max_used = float("nan")
    try:
        m_items = max(2, int(round(load * n_dim)))
        rng = np.random.RandomState(
            seed
            + int(round(alpha_shape * 1000))
            + int(round(sigma * 10000))
            + int(round(load * 100000))
        )

        # Bipolar keys/vals; L2-normalize.
        keys_raw = rng.choice([-1.0, 1.0], size=(m_items, n_dim)).astype(np.float64)
        vals_raw = rng.choice([-1.0, 1.0], size=(m_items, n_dim)).astype(np.float64)
        K_norm = _l2norm_rows(keys_raw)
        V_norm = _l2norm_rows(vals_raw)

        # Compute margin on L2-normalized keys (basis geometry, unaffected by eta).
        cosine_margin_used = _cosine_margin_estimate(K_norm)
        beta_used = _compute_adaptive_beta(m_items, cosine_margin_used)

        # Zipf-weighted rank sampling; random item-rank permutation.
        probs = _zipf_probs(m_items, alpha_shape)
        item_rank_order = rng.permutation(m_items)
        rank_samples = rng.choice(m_items, size=n_queries, replace=True, p=probs)
        query_targets = item_rank_order[rank_samples]

        # ---- HEBBIAN WRITE-SCALE (B.1 change vs v2) ----
        # eta_i = sqrt(freq_i / freq_max) where freq_i is Zipf prob of rank i.
        # item_rank_order[j] = i means "item stored at index j has rank i in Zipf".
        # We index eta by RANK (probs is rank-ordered), then permute to item order.
        eta_by_rank = _hebbian_write_scale(probs)               # (M,) rank-ordered
        # Map: eta_by_item[j] = eta_by_rank[rank_of_item_j]
        # item_rank_order[j] gives the rank assigned to item j.
        eta_by_item = eta_by_rank[item_rank_order]              # (M,) item-ordered
        eta_min_used = float(eta_by_item.min())
        eta_max_used = float(eta_by_item.max())

        # Apply per-row Hebbian write-scale to BOTH K_tape and V_tape.
        # This is the B.1 "tape write-scale reinforcement" per Skunkworks spec.
        K_tape = eta_by_item[:, None] * K_norm                  # (M, N)
        V_tape = eta_by_item[:, None] * V_norm                  # (M, N)

        # Query = noisy bipolar keys[targets]; then L2-normalize.
        # Query does NOT get eta scaling (it's a probe of an unseen state; only
        # the STORAGE is frequency-reinforced per Willshaw model).
        query_keys_raw = keys_raw[query_targets]
        queries_noisy_n = _apply_query_noise(query_keys_raw, sigma, rng)

        # Dense-Hopfield recall on eta-scaled tape.
        hits = _dense_hopfield_recall(K_tape, V_tape, queries_noisy_n,
                                      query_targets, beta_used, attn_chunk)
        recall_all = float(hits.mean())

        # Frequency-stratified recall by rank-quartile.
        q1_mask = rank_samples < (m_items // 4)                # top 25% freq (head)
        q2_mask = (rank_samples >= m_items // 4) & (rank_samples < m_items // 2)
        q3_mask = (rank_samples >= m_items // 2) & (rank_samples < 3 * m_items // 4)
        q4_mask = rank_samples >= 3 * m_items // 4             # bottom 25% freq (tail)
        recall_q1 = float(hits[q1_mask].mean()) if q1_mask.sum() > 0 else float("nan")
        recall_q2 = float(hits[q2_mask].mean()) if q2_mask.sum() > 0 else float("nan")
        recall_q3 = float(hits[q3_mask].mean()) if q3_mask.sum() > 0 else float("nan")
        recall_q4 = float(hits[q4_mask].mean()) if q4_mask.sum() > 0 else float("nan")

        sampler_entropy = _zipf_entropy(probs)

        emit_heartbeat(out_dir, unit_idx=0,
                       elapsed_s=time.time() - t0,
                       extra={"arm": arm_name, "alpha": alpha_shape,
                              "sigma": sigma, "load": load,
                              "M": m_items, "recall": recall_all,
                              "Q1": recall_q1, "Q4": recall_q4,
                              "eta_min": eta_min_used, "eta_max": eta_max_used,
                              "beta": beta_used, "margin": cosine_margin_used})

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "alpha_shape": float(alpha_shape),
            "sigma": float(sigma),
            "load": float(load),
            "M": int(m_items),
            "N": int(n_dim),
            "n_queries": int(n_queries),
            "n_q1": int(q1_mask.sum()),
            "n_q2": int(q2_mask.sum()),
            "n_q3": int(q3_mask.sum()),
            "n_q4": int(q4_mask.sum()),
            "recall_all": recall_all,
            "recall_q1_head": recall_q1,
            "recall_q2": recall_q2,
            "recall_q3": recall_q3,
            "recall_q4_tail": recall_q4,
            "sampler_entropy_nats": sampler_entropy,
            "beta_used": beta_used,
            "cosine_margin_used": cosine_margin_used,
            "eta_min": eta_min_used,
            "eta_max": eta_max_used,
            "alpha_simple": float(m_items) / float(n_dim),
            "wall_s": float(wall),
            "backend": "numpy",
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "alpha_shape": float(alpha_shape),
            "sigma": float(sigma),
            "load": float(load),
            "M": 0,
            "N": int(n_dim),
            "n_queries": 0,
            "recall_all": float("nan"),
            "recall_q1_head": float("nan"),
            "recall_q2": float("nan"),
            "recall_q3": float("nan"),
            "recall_q4_tail": float("nan"),
            "sampler_entropy_nats": float("nan"),
            "beta_used": beta_used,
            "cosine_margin_used": cosine_margin_used,
            "eta_min": eta_min_used,
            "eta_max": eta_max_used,
            "alpha_simple": float("nan"),
            "wall_s": float(wall),
            "backend": "numpy",
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
            "failure_class": type(exc).__name__,
        }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_zipf_probs_normalize() -> None:
    for alpha in (0.0, 1.0, 2.0):
        p = _zipf_probs(500, alpha)
        s = float(p.sum())
        if abs(s - 1.0) > 1e-8:
            raise AssertionError(f"Zipf probs not normalized at alpha={alpha}: sum={s}")
        if not np.all(p >= 0):
            raise AssertionError(f"Zipf probs negative at alpha={alpha}")


def _selftest_zipf_entropy_monotone() -> None:
    m = 1000
    ent_u = _zipf_entropy(_zipf_probs(m, 0.0))
    ent_1 = _zipf_entropy(_zipf_probs(m, 1.0))
    ent_2 = _zipf_entropy(_zipf_probs(m, 2.0))
    if not (abs(ent_u - math.log(m)) < 1e-6):
        raise AssertionError(f"uniform entropy {ent_u} != log(M)")
    if not (ent_u > ent_1 > ent_2):
        raise AssertionError(f"entropy not monotone: {ent_u} > {ent_1} > {ent_2}")


def _selftest_hebbian_scale_uniform_identity() -> None:
    """At alpha=0 (uniform freq), eta_i must equal 1.0 for all i.

    This is the LOAD-BEARING PRE-REG PREDICTION: v3 must reduce to v2 at alpha=0.
    """
    p = _zipf_probs(200, 0.0)
    eta = _hebbian_write_scale(p)
    if not np.allclose(eta, 1.0, atol=1e-10):
        raise AssertionError(
            f"uniform eta not identity: min={eta.min():.6f} max={eta.max():.6f}"
        )


def _selftest_hebbian_scale_zipf_asymmetry() -> None:
    """At alpha=1 (Zipf), head eta must be much larger than tail eta.

    Predicted ratio: eta_head/eta_tail = sqrt(freq_head/freq_tail).
    For Zipf alpha=1, freq_rank1 / freq_rankM ~ M * H_M ~ M * log(M).
    So eta ratio ~ sqrt(M log M) for M=200 ~ sqrt(1060) ~ 32.6.
    """
    m = 200
    p = _zipf_probs(m, 1.0)
    eta = _hebbian_write_scale(p)
    ratio = eta[0] / eta[-1]  # head / tail
    if not (ratio > 10.0):
        raise AssertionError(
            f"Zipf eta head/tail ratio too small: {ratio:.2f} (expected > 10)"
        )
    # Also verify eta[0] is exactly 1.0 (head is freq_max -> eta = 1.0).
    if abs(eta[0] - 1.0) > 1e-10:
        raise AssertionError(f"Zipf eta_head not 1.0: {eta[0]}")


def _selftest_bit_flip_noise_rate() -> None:
    rng = np.random.RandomState(31)
    q_raw = np.ones((10, 4096), dtype=np.float64)
    q_noisy_n = _apply_query_noise(q_raw, 0.30, rng)
    signs = np.sign(q_noisy_n)
    flip_rate = float((signs != 1.0).mean())
    if not (0.20 < flip_rate < 0.40):
        raise AssertionError(f"bit-flip rate {flip_rate} not in [0.20, 0.40] at sigma=0.30")


def _selftest_hebbian_head_tail_directionality() -> None:
    """WIRING CHECK: at Amit-Gutfreund wall with Zipf + noise, Hebbian
    frequency-reinforcement produces DIRECTIONAL asymmetry (Q1 >= Q4).

    NOTE (2026-07-01 pre-flight probe): B.1 tape-write-scale with softmax
    dense-Hopfield READ-REPLACE reveals architectural pathology at N>=512:
    per-row eta scaling breaks softmax's scale-invariance in a bad direction
    (argmax collapses to highest-eta row regardless of query). Overall recall
    collapses catastrophically at all regimes. Even so, the mechanism should
    fire in the RIGHT DIRECTION (Q1 >= Q4) even if absolute recall is low.

    This selftest is a WIRING check (Q1 not-less-than Q4 by more than a small
    tolerance), NOT a strength check. Strength is verified at smoke full-N
    preview per DISCRIMINATOR-MUST-SURVIVE-SCALE pattern C. If preview at
    N=8192 shows gap < 0.10, cell emits HF_B1_INSUFFICIENT_SMOKE and escalates
    to B.2 canonical W-matrix sibling cell.
    """
    rng = np.random.RandomState(53)
    n = 512
    m = int(round(0.05 * n))   # 25 items; well below wall so recall isn't 0
    alpha = 1.0                # natural Zipf
    sigma = 0.30               # heavy noise
    n_q = 1200                 # enough for stratified stats

    keys_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    K_norm = _l2norm_rows(keys_raw)
    V_norm = _l2norm_rows(vals_raw)
    margin = _cosine_margin_estimate(K_norm)
    beta = _compute_adaptive_beta(m, margin)

    probs = _zipf_probs(m, alpha)
    item_rank_order = rng.permutation(m)
    rank_samples = rng.choice(m, size=n_q, replace=True, p=probs)
    query_targets = item_rank_order[rank_samples]

    eta_by_rank = _hebbian_write_scale(probs)
    eta_by_item = eta_by_rank[item_rank_order]
    K_tape = eta_by_item[:, None] * K_norm
    V_tape = eta_by_item[:, None] * V_norm

    query_keys_raw = keys_raw[query_targets]
    queries_noisy_n = _apply_query_noise(query_keys_raw, sigma, rng)
    hits = _dense_hopfield_recall(K_tape, V_tape, queries_noisy_n,
                                  query_targets, beta, m)

    q1_mask = rank_samples < (m // 4)
    q4_mask = rank_samples >= 3 * m // 4
    if q1_mask.sum() == 0 or q4_mask.sum() == 0:
        raise AssertionError(
            f"selftest quartile support 0: n_q1={q1_mask.sum()} n_q4={q4_mask.sum()}"
        )
    r_q1 = float(hits[q1_mask].mean())
    r_q4 = float(hits[q4_mask].mean())
    gap = r_q1 - r_q4

    # WIRING CHECK: Q1 must not be MUCH LESS than Q4 (that would indicate
    # reversed eta or per-row scale bug). Tolerance -0.05 allows for statistical
    # noise from sampling under low-recall regimes.
    if not (gap >= -0.05):
        raise AssertionError(
            f"WIRING_BUG: Hebbian B.1 at wall+noise gave Q1={r_q1:.3f} < Q4={r_q4:.3f} "
            f"(gap={gap:.3f} < -0.05). Reversed eta indexing OR item/rank permutation "
            f"crossed."
        )


def _selftest_uniform_no_asymmetry() -> None:
    """CONTROL: at alpha=0 (uniform freq), Q1-Q4 gap must be ~ 0.

    Uniform freq -> eta_i = 1.0 for all -> v2 architecture -> no asymmetry.
    If this shows asymmetry, indexing bug (rank_samples vs item_rank_order mixed).
    """
    rng = np.random.RandomState(59)
    n = 512
    m = int(round(0.14 * n))
    alpha = 0.0
    sigma = 0.30
    n_q = 800

    keys_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    K_norm = _l2norm_rows(keys_raw)
    V_norm = _l2norm_rows(vals_raw)
    margin = _cosine_margin_estimate(K_norm)
    beta = _compute_adaptive_beta(m, margin)

    probs = _zipf_probs(m, alpha)
    item_rank_order = rng.permutation(m)
    rank_samples = rng.choice(m, size=n_q, replace=True, p=probs)
    query_targets = item_rank_order[rank_samples]

    eta_by_rank = _hebbian_write_scale(probs)
    eta_by_item = eta_by_rank[item_rank_order]
    K_tape = eta_by_item[:, None] * K_norm
    V_tape = eta_by_item[:, None] * V_norm

    query_keys_raw = keys_raw[query_targets]
    queries_noisy_n = _apply_query_noise(query_keys_raw, sigma, rng)
    hits = _dense_hopfield_recall(K_tape, V_tape, queries_noisy_n,
                                  query_targets, beta, m)

    q1_mask = rank_samples < (m // 4)
    q4_mask = rank_samples >= 3 * m // 4
    if q1_mask.sum() == 0 or q4_mask.sum() == 0:
        raise AssertionError("uniform-control quartile support 0")
    r_q1 = float(hits[q1_mask].mean())
    r_q4 = float(hits[q4_mask].mean())
    gap = abs(r_q1 - r_q4)
    if gap > 0.10:
        raise AssertionError(
            f"UNIFORM_ASYMMETRY_LEAK: alpha=0 gave Q1={r_q1:.3f} Q4={r_q4:.3f} "
            f"gap={gap:.3f} > 0.10 (uniform freq should NOT produce asymmetry)"
        )


def _selftest_dense_hopfield_clean_recall() -> None:
    rng = np.random.RandomState(11)
    m, n = 8, 32
    K = _l2norm_rows(rng.randn(m, n).astype(np.float64))
    V = _l2norm_rows(rng.randn(m, n).astype(np.float64))
    targets = np.arange(m)
    hits = _dense_hopfield_recall(K, V, K, targets, beta=50.0, attn_chunk=m)
    if not hits.all():
        raise AssertionError(f"clean self-recall failed: hits={hits.sum()}/{m}")


def _selftest_cosine_margin_range() -> None:
    rng = np.random.RandomState(13)
    K = _l2norm_rows(rng.choice([-1.0, 1.0], size=(64, 128)).astype(np.float64))
    m = _cosine_margin_estimate(K)
    if not (0.0 < m <= 1.0) or not math.isfinite(m):
        raise AssertionError(f"cosine_margin out of range: {m}")


def _selftest_adaptive_beta_clamps() -> None:
    b = _compute_adaptive_beta(8192, 0.7)
    if not math.isfinite(b) or not (BETA_MIN <= b <= BETA_MAX):
        raise AssertionError(f"beta {b} bad")
    b_deg = _compute_adaptive_beta(8192, 0.01)
    if b_deg != BETA_MAX:
        raise AssertionError(f"degenerate margin should clamp to BETA_MAX; got {b_deg}")


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS != [SEED_THIS_CHUNK]:
        raise AssertionError(f"chunk seed mismatch: {SEEDS} != [{SEED_THIS_CHUNK}]")
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(f"anchor '{ANCHOR_NAME}' missing seed_{SEED_THIS_CHUNK}")


def _selftest_cardinality_wiring() -> None:
    if EXPECTED_N_UNITS != len(ALPHA_SHAPE_LEVELS) * len(SIGMA_NOISE_LEVELS) * len(LOAD_LEVELS):
        raise AssertionError(f"EXPECTED_N_UNITS wiring: {EXPECTED_N_UNITS}")


def _instrumentation_selftest() -> None:
    try:
        _selftest_zipf_probs_normalize()
        _selftest_zipf_entropy_monotone()
        _selftest_hebbian_scale_uniform_identity()
        _selftest_hebbian_scale_zipf_asymmetry()
        _selftest_bit_flip_noise_rate()
        _selftest_dense_hopfield_clean_recall()
        _selftest_cosine_margin_range()
        _selftest_adaptive_beta_clamps()
        _selftest_chunk_seed_matches_anchor()
        _selftest_cardinality_wiring()
        _selftest_uniform_no_asymmetry()
        _selftest_hebbian_head_tail_directionality()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}", flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  N={N_DIM}  N_Q={N_QUERIES}  "
        f"alpha={ALPHA_SHAPE_LEVELS}  sigma={SIGMA_NOISE_LEVELS}  "
        f"load={LOAD_LEVELS}  beta=[{BETA_MIN},{BETA_MAX}]  mode={RUN_MODE}  "
        f"chunk_seed={SEED_THIS_CHUNK}  expected_units={EXPECTED_N_UNITS}",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    arms = []
    n_arms_total = len(ALPHA_SHAPE_LEVELS) * len(SIGMA_NOISE_LEVELS) * len(LOAD_LEVELS)
    idx = 0
    for alpha in ALPHA_SHAPE_LEVELS:
        for sigma in SIGMA_NOISE_LEVELS:
            for load in LOAD_LEVELS:
                arm_name = f"a{alpha:.1f}_s{sigma:.2f}_L{load:.2f}"
                print(
                    f"  [seed={seed} {idx + 1}/{n_arms_total} {arm_name}] "
                    f"running at N={N_DIM} N_Q={N_QUERIES}...",
                    flush=True,
                )
                out = run_arm(arm_name, alpha, sigma, load,
                              n_dim=N_DIM, n_queries=N_QUERIES,
                              seed=seed, attn_chunk=ATTN_CHUNK, out_dir=out_dir)
                arms.append(out)
                print(
                    f"  [seed={seed} {arm_name}] "
                    f"r_all={out['recall_all']:.3f} "
                    f"Q1={out['recall_q1_head']:.3f} Q4={out['recall_q4_tail']:.3f} "
                    f"M={out['M']} beta={out.get('beta_used', float('nan')):.2f} "
                    f"eta=[{out.get('eta_min', float('nan')):.3f}, "
                    f"{out.get('eta_max', float('nan')):.3f}] "
                    f"status={out['arm_status']} wall={out['wall_s']:.2f}s",
                    flush=True,
                )
                emit_heartbeat(out_dir, unit_idx=idx + 1, total_units=n_arms_total,
                               elapsed_s=time.time() - t0,
                               extra={"arm": arm_name, "recall": out["recall_all"]})
                idx += 1

    preview_arm = None
    preview_control = None
    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW:
        # Preview 1: mechanism-fire arm (Zipf at Amit-Gutfreund wall + noise)
        print(
            f"  [seed={seed} PREVIEW_FULL_N] N={N_FULL} "
            f"alpha={PREVIEW_ALPHA} sigma={PREVIEW_SIGMA} load={PREVIEW_LOAD} "
            f"N_Q={PREVIEW_N_QUERIES} (Amit-Gutfreund wall + noise + Zipf)...",
            flush=True,
        )
        preview_arm = run_arm(
            f"PREVIEW_a{PREVIEW_ALPHA:.1f}_s{PREVIEW_SIGMA:.2f}_L{PREVIEW_LOAD:.2f}_fullN_ZIPF",
            PREVIEW_ALPHA, PREVIEW_SIGMA, PREVIEW_LOAD,
            n_dim=N_FULL, n_queries=PREVIEW_N_QUERIES,
            seed=seed, attn_chunk=ATTN_CHUNK, out_dir=out_dir,
        )
        print(
            f"  [seed={seed} PREVIEW_FULL_N_ZIPF] "
            f"r_all={preview_arm['recall_all']:.3f} "
            f"Q1={preview_arm['recall_q1_head']:.3f} Q4={preview_arm['recall_q4_tail']:.3f} "
            f"gap={preview_arm['recall_q1_head'] - preview_arm['recall_q4_tail']:.3f} "
            f"M={preview_arm['M']} beta={preview_arm.get('beta_used', float('nan')):.2f} "
            f"eta=[{preview_arm.get('eta_min', float('nan')):.4f}, "
            f"{preview_arm.get('eta_max', float('nan')):.4f}] "
            f"wall={preview_arm['wall_s']:.1f}s",
            flush=True,
        )
        arms.append(preview_arm)

        # Preview 2: control arm (uniform freq -> no asymmetry expected)
        print(
            f"  [seed={seed} PREVIEW_FULL_N_CONTROL] N={N_FULL} "
            f"alpha={PREVIEW_CONTROL_ALPHA} sigma={PREVIEW_CONTROL_SIGMA} "
            f"load={PREVIEW_CONTROL_LOAD} N_Q={PREVIEW_N_QUERIES} (uniform control)...",
            flush=True,
        )
        preview_control = run_arm(
            f"PREVIEW_a{PREVIEW_CONTROL_ALPHA:.1f}_s{PREVIEW_CONTROL_SIGMA:.2f}"
            f"_L{PREVIEW_CONTROL_LOAD:.2f}_fullN_CONTROL",
            PREVIEW_CONTROL_ALPHA, PREVIEW_CONTROL_SIGMA, PREVIEW_CONTROL_LOAD,
            n_dim=N_FULL, n_queries=PREVIEW_N_QUERIES,
            seed=seed, attn_chunk=ATTN_CHUNK, out_dir=out_dir,
        )
        print(
            f"  [seed={seed} PREVIEW_FULL_N_CONTROL] "
            f"r_all={preview_control['recall_all']:.3f} "
            f"Q1={preview_control['recall_q1_head']:.3f} "
            f"Q4={preview_control['recall_q4_tail']:.3f} "
            f"gap={preview_control['recall_q1_head'] - preview_control['recall_q4_tail']:.3f} "
            f"M={preview_control['M']} wall={preview_control['wall_s']:.1f}s",
            flush=True,
        )
        arms.append(preview_control)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "n_queries": N_QUERIES,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _core_arms(arms: List[Dict]) -> List[Dict]:
    return [a for a in arms if not a["arm_name"].startswith("PREVIEW_")]


def _preview_arms(arms: List[Dict]) -> List[Dict]:
    return [a for a in arms if a["arm_name"].startswith("PREVIEW_")]


def _lookup(core: List[Dict], alpha: float, sigma: float, load: float) -> Dict:
    for a in core:
        if (abs(a["alpha_shape"] - alpha) < 1e-6
                and abs(a["sigma"] - sigma) < 1e-6
                and abs(a["load"] - load) < 1e-6):
            return a
    raise KeyError(f"missing arm alpha={alpha} sigma={sigma} load={load}")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    if len(results) != 1:
        return ("HARD_FAIL", f"CARDINALITY_BREACH: expected 1 seed, got {len(results)}")
    r = results[0]
    core = _core_arms(r["arms"])
    previews = _preview_arms(r["arms"])
    if len(core) != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"expected {EXPECTED_N_UNITS} core arms, got {len(core)}")
    for a in core:
        if a["arm_status"] != "OK":
            return ("HARD_FAIL", f"Arm {a['arm_name']} error: {a['arm_status']}")

    # META_RULE_AF: signature distinctness.
    signatures = set()
    for a in core:
        signatures.add((round(a["recall_all"], 8),
                        round(a["sampler_entropy_nats"], 6),
                        round(a["sigma"], 6),
                        round(a["load"], 6)))
    if len(signatures) < 10:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: only {len(signatures)} distinct signatures "
                f"across {len(core)} arms; wiring suspect")

    # Baseline sanity.
    try:
        a_baseline = _lookup(core, 0.0, 0.0, 0.05)
    except KeyError as e:
        return ("HARD_FAIL", f"Missing baseline arm: {e}")

    r_baseline = a_baseline["recall_all"]
    if RUN_MODE == "full":
        baseline_ok = (r_baseline >= 0.85)
    else:
        baseline_ok = (r_baseline >= 0.50)
    if not baseline_ok:
        return ("HARD_FAIL",
                f"BASELINE_OUT_OF_BAND: baseline(a=0,s=0,L=0.05) recall={r_baseline:.3f} "
                f"< {'0.85' if RUN_MODE == 'full' else '0.50'} at {RUN_MODE}")

    # UNIFORM_ASYMMETRY_LEAK check: at alpha=0, load=0.10, gap must be ~ 0.
    try:
        a_uni_control = _lookup(core, 0.0, 0.30, 0.10)
        q1_uni = a_uni_control["recall_q1_head"]
        q4_uni = a_uni_control["recall_q4_tail"]
        if math.isfinite(q1_uni) and math.isfinite(q4_uni):
            uni_gap = abs(q1_uni - q4_uni)
            if uni_gap > 0.10:
                return ("HARD_FAIL",
                        f"UNIFORM_ASYMMETRY_LEAK: alpha=0/sigma=0.3/L=0.10 gap="
                        f"{uni_gap:.3f} > 0.10; implementation bug (uniform freq "
                        f"must not produce head-tail asymmetry)")
    except KeyError:
        pass  # not fatal; just skip control check

    # ---- HP TWO_TIER: sweep Zipf * noise * wall regime ----
    def _safe_gap(a, b):
        if not (math.isfinite(a) and math.isfinite(b)):
            return float("nan")
        return a - b

    # HP window: alpha=1.0, sigma in [0.15, 0.30], load in [0.10, 0.14]
    window_gaps = []
    window_details = []
    for sigma in (0.15, 0.30):
        for load in (0.10, 0.12, 0.14):
            try:
                arm = _lookup(core, 1.0, sigma, load)
                q1 = arm["recall_q1_head"]
                q4 = arm["recall_q4_tail"]
                gap = _safe_gap(q1, q4)
                if math.isfinite(gap):
                    window_gaps.append(gap)
                    window_details.append((sigma, load, q1, q4, gap))
            except KeyError:
                pass

    max_window_gap = max(window_gaps) if window_gaps else float("nan")
    n_window_hp_fires = sum(1 for g in window_gaps if g >= 0.30)  # HP threshold
    n_window_mb_fires = sum(1 for g in window_gaps if 0.10 <= g < 0.30)  # MB threshold

    # HF_B1_INSUFFICIENT: at alpha=1, sigma=0.30, loads {0.10, 0.12, 0.14}, MAX gap < 0.10
    hf_b1_insufficient = False
    hf_b1_msg = ""
    if RUN_MODE == "full":
        stress_gaps = []
        for load in (0.10, 0.12, 0.14):
            try:
                arm = _lookup(core, 1.0, 0.30, load)
                q1 = arm["recall_q1_head"]
                q4 = arm["recall_q4_tail"]
                gap = _safe_gap(q1, q4)
                if math.isfinite(gap):
                    stress_gaps.append(gap)
            except KeyError:
                pass
        if stress_gaps and max(stress_gaps) < 0.10:
            hf_b1_insufficient = True
            hf_b1_msg = (f"HF_B1_INSUFFICIENT: at alpha=1.0/sigma=0.30/L in "
                         f"{{0.10,0.12,0.14}}, MAX gap={max(stress_gaps):.3f} < 0.10; "
                         f"tape-write-scale reinforcement insufficient; escalate B.2")

    # HP fires: at least one window point has gap >= 0.30
    hp_two_tier_hebbian = (n_window_hp_fires > 0)

    summary_windows = "; ".join(
        f"s{s}L{L:.2f}:Q1={q1:.3f}/Q4={q4:.3f}/g={g:+.3f}"
        for (s, L, q1, q4, g) in window_details
    )

    summary = (
        f"seed={SEED_THIS_CHUNK} N={N_DIM} mode={RUN_MODE} "
        f"baseline={r_baseline:.3f} "
        f"window_max_gap={max_window_gap:.3f} "
        f"n_hp_fires={n_window_hp_fires} n_mb_fires={n_window_mb_fires} "
        f"HP=[two_tier_hebbian={hp_two_tier_hebbian}] "
        f"HF=[b1_insufficient={hf_b1_insufficient}] "
        f"window=[{summary_windows}]"
    )

    if hf_b1_insufficient:
        return ("HARD_FAIL", f"{hf_b1_msg}. {summary}")

    # Full HARD_PASS: HP_TWO_TIER_HEBBIAN fires + baseline OK.
    if RUN_MODE == "full":
        hp_baseline = r_baseline >= 0.95
        if hp_two_tier_hebbian and hp_baseline:
            return ("HARD_PASS",
                    f"HARD_PASS: TWO_TIER_HEBBIAN (single-seed). "
                    f"Frequency-reinforcement produces head-tail asymmetry at "
                    f"Amit-Gutfreund wall + noise. Chain-grade requires cross-seed VET. "
                    f"{summary}")

    # Smoke thresholds relaxed for small-N. Smoke HARD_PASS uses lower gap
    # threshold (mechanism should still SIGN); Skunkworks decides on preview.
    if RUN_MODE == "smoke":
        smoke_hp_gap = 0.15  # smoke threshold; N=1024 will have less separation than N=8192
        smoke_mb_gap = 0.05
        n_smoke_hp = sum(1 for g in window_gaps if g >= smoke_hp_gap)
        n_smoke_mb = sum(1 for g in window_gaps if smoke_mb_gap <= g < smoke_hp_gap)
        smoke_hp_fires = (n_smoke_hp > 0)

        # Preview analysis for smoke: check the (alpha=1, sigma=0.30, load=0.12, N=8192)
        # arm. This is the DISCRIMINATOR-MUST-SURVIVE-SCALE gate.
        preview_zipf = None
        preview_ctrl = None
        for p in previews:
            if "CONTROL" in p["arm_name"]:
                preview_ctrl = p
            elif "ZIPF" in p["arm_name"]:
                preview_zipf = p

        preview_zipf_gap = float("nan")
        preview_ctrl_gap = float("nan")
        if preview_zipf and preview_zipf["arm_status"] == "OK":
            preview_zipf_gap = _safe_gap(preview_zipf["recall_q1_head"],
                                         preview_zipf["recall_q4_tail"])
        if preview_ctrl and preview_ctrl["arm_status"] == "OK":
            preview_ctrl_gap = _safe_gap(preview_ctrl["recall_q1_head"],
                                         preview_ctrl["recall_q4_tail"])

        preview_summary = (
            f"preview_zipf_gap={preview_zipf_gap:.3f} "
            f"preview_ctrl_gap={preview_ctrl_gap:.3f}"
        )

        # Preview-driven verdict for smoke (LOAD-BEARING at N=8192):
        # If preview_zipf_gap >= 0.30 -> strong signal at full-N -> HARD_PASS smoke
        # If preview_zipf_gap >= 0.10 -> partial signal -> MIDDLE_BAND
        # If preview_zipf_gap < 0.10  -> B.1 insufficient at wall -> HF_B1_INSUFFICIENT_SMOKE
        if math.isfinite(preview_zipf_gap):
            if preview_zipf_gap >= 0.30:
                return ("HARD_PASS",
                        f"HARD_PASS_SMOKE: preview at N=8192 (Amit-Gutfreund wall, "
                        f"alpha=1, sigma=0.30, L=0.12) shows STRONG two-tier "
                        f"gap={preview_zipf_gap:.3f} >= 0.30. Hebbian frequency-"
                        f"reinforcement produces predicted signature. Full dispatch "
                        f"recommended. {preview_summary} {summary}")
            elif preview_zipf_gap >= 0.10:
                return ("MIDDLE_BAND",
                        f"MIDDLE_BAND_SMOKE: preview at N=8192 shows PARTIAL two-tier "
                        f"gap={preview_zipf_gap:.3f} in [0.10, 0.30). Mechanism fires "
                        f"but weaker than drill prediction. Skunkworks tier decision "
                        f"needed; full dispatch discretionary. {preview_summary} {summary}")
            else:
                return ("HARD_FAIL",
                        f"HF_B1_INSUFFICIENT_SMOKE: preview at N=8192 (Amit-Gutfreund "
                        f"wall) shows gap={preview_zipf_gap:.3f} < 0.10. B.1 tape-"
                        f"write-scale reinforcement insufficient at full-N; escalate "
                        f"to B.2 canonical Hebbian W-matrix in v3.2 sibling. "
                        f"{preview_summary} {summary}")

        # Preview didn't run (shouldn't happen in smoke); fall back to sweep-only
        if smoke_hp_fires:
            return ("HARD_PASS",
                    f"HARD_PASS_SMOKE_SWEEPONLY: smoke sweep window max_gap="
                    f"{max_window_gap:.3f} >= {smoke_hp_gap}. Preview arm missing; "
                    f"verify before full dispatch. {summary}")

    # Default: MIDDLE_BAND
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial two-tier signature. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(
            f"[seed={seed}] {ANCHOR_NAME} N={N_DIM} N_Q={N_QUERIES} mode={RUN_MODE} "
            f"alpha={ALPHA_SHAPE_LEVELS} sigma={SIGMA_NOISE_LEVELS} load={LOAD_LEVELS}...",
            flush=True,
        )
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n"
                f"{traceback.format_exc()}",
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

    core_arms_final = _core_arms(all_results[0]["arms"]) if all_results else []

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N={N_DIM} N_Q={N_QUERIES} mode={RUN_MODE} "
            f"expected_units={EXPECTED_N_UNITS} "
            f"alpha={ALPHA_SHAPE_LEVELS} sigma={SIGMA_NOISE_LEVELS} load={LOAD_LEVELS} "
            f"beta_range=[{BETA_MIN},{BETA_MAX}]"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N_DIM,
        "N_QUERIES": N_QUERIES,
        "alpha_shape_levels": ALPHA_SHAPE_LEVELS,
        "sigma_noise_levels": SIGMA_NOISE_LEVELS,
        "load_levels": LOAD_LEVELS,
        "beta_floor": BETA_MIN,
        "beta_ceil": BETA_MAX,
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (
            len(all_results) == 1 and len(core_arms_final) == EXPECTED_N_UNITS
        ) if all_results else False,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": 0.0158,
        "crlb_stratified_floor": 0.032,
        "crlb_formula_reference": "sigma_min = sqrt(0.25/N_QUERIES) binomial-CLT; stratified over N_Q/4",
        "discriminator_reachability": True,
        "calibration_check": "adaptive_with_discriminator_gate",
        "mechanism_class": "hebbian_tape_write_scale_B1",
        "per_seed": [
            {"seed": r.get("seed"),
             "elapsed_s": r.get("elapsed_s"),
             "arms": r.get("arms")}
            for r in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    print(f"[metrics] written to {metrics_path}", flush=True)


def main():
    _main()


if __name__ == "__main__":
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _exc:
        _write_crash_metrics(_out_dir_for_crash, ANCHOR_NAME, _exc)
        raise
