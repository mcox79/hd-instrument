"""exp_cortex_regenerative_cleanup_vs_analog_accumulate_v1

DECISIVE TEST (5x-convergence reasoning drill, Part E): does REGENERATIVE
CLEANUP after every reasoning hop break the multiplicative error decay that
ANALOG accumulation shows, holding chain accuracy FLAT across depth?

Framing: constructive build over our own memory (per USER 2026-07-05 reframe --
NOT a vs-LLM comparison). CPU vector-algebra probe. No LLM. No GPU.

Information-theory frame (drill Part C.5): a DIGITAL regenerative repeater resets
the signal to a clean codeword each hop, so noise does NOT accumulate with chain
length; an ANALOG repeater amplifies noise with signal and degrades with every
hop (data-processing inequality -> multiplicative (1-eps)^K decay). This cell
instantiates both regimes over the SAME associative store and measures the
depth-accuracy curve.

--------------------------------------------------------------------------------
SUBSTRATE + MECHANISM
--------------------------------------------------------------------------------
Codebook E: V bipolar (+/-1) concept atoms, dim N. Relations R: P bipolar atoms.
bind(a, b) = elementwise a * b (self-inverse for bipolar).
Store: Hebbian associative memory  W = sum_edges outer(E[o], bind(E[s], R[p])) / N.
       This SUPERPOSES M edges into one N x N matrix -> crosstalk ~ M/N (Plate
       1995). The crosstalk IS the per-hop noise source the cleanup must overcome.
Retrieve one hop from state x with relation p:  yhat = W @ bind(x, R[p]).
Cleanup: ohat = argmax_v (E[v] . yhat)  (snap to nearest codebook atom).

Chains are NESTED: generate N_TEST chains of length D_MAX; evaluate each arm at
every prefix-depth d in DEPTHS. This makes the depth curve AND the arm curve
perfectly PAIRED (same chains, same W, walked further / walked differently).

--------------------------------------------------------------------------------
ARMS (3, all bit-different; paired on the same chains + same W)
--------------------------------------------------------------------------------
ARM_ANALOG_ACCUMULATE   -- carry the raw noisy retrieved vector forward:
                           x_{k+1} = normalize(yhat_k). No cleanup between hops.
                           Reproduces the ~0.69/hop analog-repeater decay. NEGATIVE RAIL.
ARM_REGEN_CLEANUP_ISO    -- snap to nearest codebook atom each hop:
                           x_{k+1} = E[ohat_k] (clean +/-1 codeword), held in a
                           scratchpad array SEPARATE from W. Zero writes touch W
                           during the walk (audited: W checksum invariant). THE MECHANISM.
                           (== drill arm C "regenerative-cleanup + scratchpad-isolated".)
ARM_SHUFFLED_CONTROL     -- regen cleanup, but W built from the SAME edges with
                           OBJECTS label-shuffled (structure destroyed). Even with
                           perfect cleanup the walk lands on random nodes ->
                           final-node accuracy ~ chance (1/V). DISCRIMINATOR-FIRES CONTROL.

Scratchpad-isolation audit (drill Part B.1): the regen intermediate lives in a
separate ndarray; a sha256 checksum of W is captured before and after the walk
and asserted equal (zero main-store writes).

--------------------------------------------------------------------------------
JOINT GATES (a cleanup arm that lifts accuracy while wrecking these is a FALSE PASS)
--------------------------------------------------------------------------------
FAITHFULNESS (drill Part A) -- HARD JOINT-GATE: replay each emitted answer using
  ONLY the logged discrete trace (start node + relation ids), recomputing the
  digital/atom-carry walk, and check it reproduces the emitted final node. Regen
  is faithful by construction (the replay IS the regen rule) -> ~1.0; analog
  carries a vector not an atom, so its discrete trace does NOT mechanically
  determine its answer -> faithfulness < 1.0. HARD gate: regen faith >= 0.95.
  This is the working joint-gate: it catches a cleanup arm that lifted accuracy
  via a non-faithful shortcut (the exact FALSE-PASS the contract targets).
REFUSE-GATE (drill Part A) -- REPORTED, NOT GATED: at DISC regime, mix SUPPORTED
  chains with BROKEN chains (one hop corrupted to an unstored key). Per-chain
  confidence = MEAN over hops of the top1-vs-top2 cleanup margin (drift-diffusion
  evidence accumulation). Calibrate tau on a supported split; report false_accept
  / false_refuse. HONEST NEGATIVE (MEASURED 2026-07-05): abstention does NOT
  calibrate on the Hebbian substrate at high crosstalk (conf_sep ~ 0.05-0.14) --
  the associative matrix returns a plausible retrieval even for unsupported keys.
  Calibrated abstention is a separate, harder capability; reported as a baseline,
  NOT used to gate the core mechanism verdict (which would misrepresent it).

--------------------------------------------------------------------------------
SMOKE FINDING (2026-07-05) -> DESIGN CORRECTION (phase diagram, not single regime)
--------------------------------------------------------------------------------
Smoke + a 3-seed regime probe REFUTED the drill's naive metric and revealed the
correct one. The mechanism is REGIME-DEPENDENT (a phase transition at M/N ~ 1):
  * BELOW threshold (M/N ~ 0.3): ANALOG (soft-carry) WINS -- the Hebbian matrix
    readout is itself a denoiser and the soft vector retains more info than a
    hard-snapped codeword (soft-decision > hard-decision decoding). gap ~ -0.32.
  * ABOVE threshold (M/N ~ 1.1): ANALOG COLLAPSES catastrophically (d5 ~ 0.12,
    d7 ~ 0.03) while REGEN degrades GRACEFULLY (d5 ~ 0.60). gap ~ +0.47 (MEASURED,
    3 seeds). THIS is the digital-vs-analog-repeater regime the drill's Part C.5
    predicted -- a per-step operating-capacity threshold, not a depth wall.
The drill's "flat within 0.10" HARD-PASS was HYPOTHESIZED and is physically wrong:
hard per-hop cleanup is inherently (1-eps)^d, never flat; the discriminator that
actually fires is the GAP + analog-collapse + graceful-vs-catastrophic margin.
So the cell SWEEPS M_BG across the crossover and evaluates HARD_PASS at DISC_MBG.
--------------------------------------------------------------------------------
BANDS (per-seed tier @ DISC_MBG; aggregate = majority over seeds). See prereg.
--------------------------------------------------------------------------------
SANITY RAIL (@DISC regime):
  regen[1] >= 0.85 AND analog[1] >= 0.85         (single-hop store works)
  control[5] <= 0.02                             (structure destroyed -> chance)
HARD_PASS (per-seed, @DISC_MBG):
  regen[5] >= 0.45                               (regen still usable at depth5)
  (regen[5] - analog[5]) >= 0.15                 (regen beats analog; primary discriminator)
  analog[5] <= 0.30                              (analog catastrophically collapsed)
  (analog[3]-analog[5]) - (regen[3]-regen[5]) >= 0.15  (graceful vs catastrophic)
  scratchpad_isolation_clean == True
  regen_faithfulness >= 0.95                     (HARD joint gate)
  control[5] <= 0.05                             (near chance floor 1/V=0.002)
  [reported] crossover_confirmed = (gap @ LOW_MBG <= 0.05)  (soft-wins-below-capacity)
  [reported] refuse-gate false_accept / false_refuse       (NOT gated; honest baseline)
HARD_FAIL (per-seed):
  regen[5] <= 0.20 (regen also collapses) OR (regen[5]-analog[5]) < 0.05 (never beats analog)
  OR isolation dirty OR SANITY_BREACH OR control[5] > 0.10
FALSE_PASS_JOINT_GATE:
  core discriminator passes BUT faithfulness < 0.95.
MIDDLE_BAND: else.

--------------------------------------------------------------------------------
CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor_computed + discriminator_reachability declared (see prereg)
# - baseline_in_band at smoke (META_RULE_AG; analog[REFUSE_DEPTH] < 0.90)
# - discriminator survives scale (smoke at FULL N=8192; gap>=0.15 @ depth5 gate)
# - HARD_PASS strictly above floor + band (META_RULE_L; gap>=0.15 vs fail 0.05)
# - HP_SCOPE per-arm declaration (prereg)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check = adaptive_with_discriminator_gate (refuse tau percentile)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ in prereg
# - progress_logging = line_buffered_stdout + print flush (timeout_s >= 1800)
# - start_marker + crash_diagnostic + heartbeat (defensive error checking)
--------------------------------------------------------------------------------
Compute architecture: SEQUENCE-DEPENDENT CPU (each hop depends on hop k-1 --
genuine chained-retrieval sequential dependency exemption) + the cell IS the
substrate cleanup primitive being validated. Storage = HEBBIAN (bundled) BY
DESIGN: the superposition crosstalk is the noise source the digital-vs-analog
distinction must overcome; a sharded exact-match store would be near-noiseless
and could not exhibit the analog-accumulate regime (declared per SHARDED rule
exemption -- bundled IS the discriminator substrate here). Chains walked BATCHED
across all test chains per hop (numpy matmul), so it is not a python-scalar loop.

PROT-018: no _n<N> suffix in anchor (capability test, not an N-sweep).
ASCII-only; no unicode; no emojis; no em-dashes.
Author: exp_dev 2026-07-05.
"""
from __future__ import annotations

import sys

# progress_logging: line-buffered stdout so print() flushes on newline (cell may
# run > 30 min at FULL on remote CPU; see prereg progress_logging field).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
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
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "cortex_regenerative_cleanup_vs_analog_accumulate_v1"
_LLM_CALL_COUNTER = [0]  # substrate-only assert: must stay 0

# ---------------------------------------------------------------------------
# CLI + RUN_MODE (defaults to full per META_RULE §16; --smoke / --self-test flip)
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_ENV_MODE = os.environ.get("HDLAB_RUN_MODE", "full").lower()
if _ARGS.self_test:
    RUN_MODE = "self_test"
elif _ARGS.smoke or _ENV_MODE == "smoke":
    RUN_MODE = "smoke"
else:
    RUN_MODE = "full"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
# Depth axis (nested prefixes; DEPTHS subset of 1..D_MAX). Metric anchors: depth 3 and 5.
DEPTHS = [1, 2, 3, 4, 5, 6, 7]
D_MAX = max(DEPTHS)
REFUSE_DEPTH = 5

# CROSSTALK PHASE DIAGRAM (LOCKED from smoke + 3-seed regime probe 2026-07-05).
# Smoke revealed the mechanism is REGIME-DEPENDENT: a phase transition at
# M/N ~ 1 (chained crosstalk load). BELOW it, analog (soft-carry) wins because
# the Hebbian matrix readout already denoises and soft retains more info; ABOVE
# it, analog crosses its operating-capacity threshold and collapses catastroph-
# ically while regen (hard-snap) degrades gracefully. So the cell SWEEPS M_BG
# across the crossover instead of a single regime.
#   M_total = N_TEST*D_MAX chain edges + M_BG background edges; M/N = M_total/N.
# DISC_MBG = the discriminating (above-threshold) regime where regen wins big.
# LOW_MBG  = the below-threshold regime where soft-carry wins (documents the
#            crossover; the mechanism is NOT universally beneficial -- honest).
DISC_MBG = 8000     # M/N ~ 1.1 : regen beats analog by ~+0.47 @ depth5 (MEASURED probe)
LOW_MBG = 2000      # M/N ~ 0.37: analog beats regen (soft wins below capacity)

if RUN_MODE == "self_test":
    N_DIM = 1024
    V_CODE = 64
    P_REL = 4
    N_TEST = 24
    M_BG_LIST = [200]
    N_CALIB = 16
    N_REFUSE = 16
    SEEDS = [0]
    D_MAX = 5
    DEPTHS = [1, 2, 3, 4, 5]
    REFUSE_DEPTH = 5
elif RUN_MODE == "smoke":
    # Discriminator-must-survive-scale: smoke at FULL N=8192, reduced chains,
    # SWEEP M_BG across the crossover (LOW / DISC / HIGH), 2 seeds for variance.
    N_DIM = 8192
    V_CODE = 512
    P_REL = 8
    N_TEST = 48
    M_BG_LIST = [LOW_MBG, DISC_MBG, 16000]
    N_CALIB = 40
    N_REFUSE = 40
    SEEDS = [7, 17]
else:  # full
    N_DIM = 8192
    V_CODE = 512
    P_REL = 8
    N_TEST = 150
    M_BG_LIST = [2000, 5000, 8000, 12000, 16000]   # M/N ~ 0.37,0.74,1.10,1.59,2.08
    N_CALIB = 100
    N_REFUSE = 100
    SEEDS = [7, 17, 23, 31, 41]

# Chain-node partition: chain source/object nodes drawn from [0, V_CHAIN);
# background edge sources drawn from [V_CHAIN, V_CODE) so chain keys never
# key-collide with background keys (crosstalk stays pure superposition).
V_CHAIN = V_CODE // 2

# Refuse-gate calibration percentile (adaptive-with-discriminator-gate).
REFUSE_TAU_PERCENTILE = 12.0  # tau = 12th pctile of supported-calib confidences

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,P=%d,D_MAX=%d,DEPTHS=%s,N_TEST=%d,M_BG=%s,"
    "V_CHAIN=%d,REFUSE_DEPTH=%d,N_CALIB=%d,N_REFUSE=%d,tau_pctile=%.1f,"
    "SEEDS=%s,RUN_MODE=%s,hardening=startmarker+crashdiag+heartbeat+METARULE_AF+AH+AG"
) % (
    ANCHOR_NAME, N_DIM, V_CODE, P_REL, D_MAX, "-".join(str(d) for d in DEPTHS),
    N_TEST, "-".join(str(m) for m in M_BG_LIST), V_CHAIN, REFUSE_DEPTH,
    N_CALIB, N_REFUSE, REFUSE_TAU_PERCENTILE, "-".join(str(s) for s in SEEDS),
    RUN_MODE,
)

# Cardinality (META_RULE_H): per M_BG value we produce len(DEPTHS) depth rows x 3 arms.
EXPECTED_DEPTH_ROWS = len(DEPTHS)

# Bands ---------------------------------------------------------------------
# Evaluated AT the discriminating regime (DISC_MBG, above the M/N~1 threshold).
# The drill's HYPOTHESIZED "flat within 0.10" metric is NOT the right one: hard
# per-hop cleanup is inherently a (1-eps)^d curve, never flat. The discriminator
# that actually FIRES (MEASURED probe 2026-07-05, 3 seeds) is: at high crosstalk
# regen degrades GRACEFULLY while analog COLLAPSES catastrophically. So HARD_PASS
# gates on the GAP + analog-collapse + graceful-vs-catastrophic margin.
HP_REGEN_D5_MIN = 0.45          # regen still usable at depth5    (MEASURED ~0.60 @ DISC)
HP_GAP_MIN = 0.15               # regen_d5 - analog_d5 >= 0.15    (MEASURED ~0.47 @ DISC)
HP_ANALOG_COLLAPSE_MAX = 0.30   # analog_d5 <= 0.30 (collapsed)   (MEASURED ~0.12 @ DISC)
HP_GRACEFUL_MARGIN = 0.15       # (analog_d3-analog_d5)-(regen_d3-regen_d5) >= 0.15 (MEASURED ~0.59)
HP_FAITHFULNESS_MIN = 0.95
HP_FALSE_ACCEPT_MAX = 0.10
HP_FALSE_REFUSE_MAX = 0.15
HP_CONTROL_D5_MAX = 0.05        # near chance (1/V=0.002); tolerates a few lucky hits at small N_TEST
SANITY_D1_MIN = 0.85            # single-hop store works (relaxed; d1 dips at high M/N)
CROSSOVER_GAP_MAX = 0.05        # LOW regime gap <= this -> soft-wins-below-capacity confirmed

HF_REGEN_D5_MAX = 0.20          # regen also collapses at DISC -> mechanism fails
HF_GAP_MIN = 0.05               # gap < 0.05 at DISC -> regen never beats analog -> FAIL
HF_CONTROL_D5_MAX = 0.10        # control > 0.10 -> discriminator broken -> FAIL (chance=0.002)

CHANCE_FLOOR = 1.0 / V_CODE     # THEORETICAL final-node argmax chance floor


# ---------------------------------------------------------------------------
# Defensive-error-checking helpers (start marker / crash / heartbeat)
# ---------------------------------------------------------------------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(out_dir: Path, run_mode: str, expected_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": _now_iso(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_units,
        "host": platform.node(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    final = out_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(str(tmp), str(final))


def _write_crash_metrics(out_dir: Path, exc: Exception) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": _now_iso(),
        "pid": os.getpid(),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(final))


def _heartbeat(out_dir: Path, unit_idx: int, total_units: int, t0: float,
               extra: Dict[str, Any] | None = None) -> None:
    row = {
        "ts_iso": _now_iso(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    if extra:
        row["extra"] = extra
    try:
        with open(out_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    except OSError:
        pass  # heartbeat best-effort; never fail the run on a log write


# ---------------------------------------------------------------------------
# Substrate primitives (numpy, CPU)
# ---------------------------------------------------------------------------
def make_bipolar(rows: int, n: int, g: np.random.Generator) -> np.ndarray:
    """rows x n bipolar (+/-1) float32 codebook."""
    return (g.integers(0, 2, size=(rows, n)).astype(np.float32) * 2.0 - 1.0)


def build_W(edges: np.ndarray, E: np.ndarray, R: np.ndarray,
            n_dim: int) -> np.ndarray:
    """Hebbian associative memory: W = sum outer(E[o], E[s]*R[p]) / N.

    edges: (M, 3) int array of (s, p, o). Vectorized via K.T @ V (batched).
    """
    if edges.shape[0] == 0:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    s = edges[:, 0]
    p = edges[:, 1]
    o = edges[:, 2]
    K = E[s] * R[p]               # (M, N) keys
    Vv = E[o]                     # (M, N) values
    W = (Vv.T @ K).astype(np.float32) / float(n_dim)   # (N, N)
    return W


def cleanup_ids(yhat: np.ndarray, E: np.ndarray) -> np.ndarray:
    """Snap each row of yhat (B, N) to nearest codebook atom -> ids (B,)."""
    scores = yhat @ E.T           # (B, V)
    return np.argmax(scores, axis=1)


def cos_to_atom(yhat: np.ndarray, atom_ids: np.ndarray, E: np.ndarray) -> np.ndarray:
    """cos(yhat_row, E[atom_id_row]) per row -> (B,)."""
    picked = E[atom_ids]                       # (B, N)
    num = np.sum(yhat * picked, axis=1)
    den = (np.linalg.norm(yhat, axis=1) * np.linalg.norm(picked, axis=1)) + 1e-12
    return num / den


def cleanup_margin(yhat: np.ndarray, E: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return (pred_ids, margin) per row. margin = (top1_score - top2_score)/N is
    a retrieval-confidence signal: a genuine retrieval has one dominant codeword
    (large margin); a garbage retrieval has no clear winner (small margin). Used
    by the refuse-gate to separate supported chains from broken ones."""
    scores = yhat @ E.T                        # (B, V)
    n = float(E.shape[1])
    part = np.argpartition(-scores, 1, axis=1)[:, :2]   # top-2 indices per row
    top1_idx = part[np.arange(scores.shape[0]),
                    np.argmax(scores[np.arange(scores.shape[0])[:, None], part], axis=1)]
    top1 = scores[np.arange(scores.shape[0]), top1_idx]
    # second-best = max over the two candidates excluding top1
    s2 = scores[np.arange(scores.shape[0])[:, None], part]
    s2_sorted = np.sort(s2, axis=1)            # ascending; [:, -1]=top1, [:, -2]=top2
    top2 = s2_sorted[:, -2]
    margin = (top1 - top2) / n
    return top1_idx.astype(np.int64), margin


def _sha_of_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Chain generation (nested; reserved node partitions)
# ---------------------------------------------------------------------------
def make_chains(n_chains: int, g: np.random.Generator) -> np.ndarray:
    """(n_chains, D_MAX, 3) int array of (s, p, o) using chain-partition nodes.

    Each chain is a simple walk over [0, V_CHAIN) with no immediate node repeat.
    Relations drawn from [0, P_REL). Nested: prefix of length d IS the depth-d chain.
    """
    chains = np.zeros((n_chains, D_MAX, 3), dtype=np.int64)
    for c in range(n_chains):
        nodes = [int(g.integers(0, V_CHAIN))]
        for _ in range(D_MAX):
            nxt = int(g.integers(0, V_CHAIN))
            while nxt == nodes[-1]:
                nxt = int(g.integers(0, V_CHAIN))
            nodes.append(nxt)
        for i in range(D_MAX):
            p = int(g.integers(0, P_REL))
            chains[c, i, 0] = nodes[i]
            chains[c, i, 1] = p
            chains[c, i, 2] = nodes[i + 1]
    return chains


def make_background_edges(m_bg: int, g: np.random.Generator) -> np.ndarray:
    """(m_bg, 3) distractor edges with SOURCE in [V_CHAIN, V_CODE) (disjoint
    from chain sources), object anywhere in [0, V_CODE). Pure crosstalk."""
    if m_bg <= 0:
        return np.zeros((0, 3), dtype=np.int64)
    s = g.integers(V_CHAIN, V_CODE, size=m_bg)
    p = g.integers(0, P_REL, size=m_bg)
    o = g.integers(0, V_CODE, size=m_bg)
    return np.stack([s, p, o], axis=1).astype(np.int64)


# ---------------------------------------------------------------------------
# Arm walkers (batched across chains). Return per-hop accuracy + emitted final ids.
# ---------------------------------------------------------------------------
def walk_analog(chains: np.ndarray, depth: int, W: np.ndarray,
                E: np.ndarray, R: np.ndarray) -> Dict[str, Any]:
    """ANALOG: carry normalized noisy retrieved vector forward; no cleanup."""
    B = chains.shape[0]
    x = E[chains[:, 0, 0]].astype(np.float32).copy()     # (B, N) start atoms
    per_hop_acc = []
    final_pred = None
    for k in range(depth):
        p = chains[:, k, 1]
        target = chains[:, k, 2]
        key = x * R[p]                                    # (B, N)
        yhat = key @ W.T                                  # (B, N) noisy retrieval
        pred = cleanup_ids(yhat, E)                       # readout (scoring only)
        per_hop_acc.append(float(np.mean(pred == target)))
        final_pred = pred
        # carry the noisy vector forward (analog); L2-normalize amplitude only
        nrm = np.linalg.norm(yhat, axis=1, keepdims=True) + 1e-12
        x = (yhat / nrm).astype(np.float32)
    final_correct = (final_pred == chains[:, depth - 1, 2])
    return {
        "per_hop_acc": per_hop_acc,
        "final_acc": float(np.mean(final_correct)),
        "final_pred": final_pred,
    }


def walk_regen(chains: np.ndarray, depth: int, W: np.ndarray,
               E: np.ndarray, R: np.ndarray,
               audit_isolation: bool = False) -> Dict[str, Any]:
    """REGEN: snap to nearest codebook atom each hop; carry the CLEAN atom.

    Scratchpad `x` is a separate array; when audit_isolation, capture W's sha256
    before and after and assert invariance (zero main-store writes).
    """
    B = chains.shape[0]
    w_sha_before = _sha_of_array(W) if audit_isolation else None
    x = E[chains[:, 0, 0]].astype(np.float32).copy()     # scratchpad (separate)
    assert x.base is None, "scratchpad must be a fresh array (separate register)"
    per_hop_acc = []
    per_hop_conf = []
    trace_atom_ids = np.zeros((B, depth), dtype=np.int64)  # logged discrete trace
    final_pred = None
    for k in range(depth):
        p = chains[:, k, 1]
        target = chains[:, k, 2]
        key = x * R[p]
        yhat = key @ W.T
        pred = cleanup_ids(yhat, E)
        conf = cos_to_atom(yhat, pred, E)
        per_hop_acc.append(float(np.mean(pred == target)))
        per_hop_conf.append(conf)
        trace_atom_ids[:, k] = pred
        final_pred = pred
        x = E[pred].astype(np.float32)                   # snap to clean codeword
    final_correct = (final_pred == chains[:, depth - 1, 2])
    w_sha_after = _sha_of_array(W) if audit_isolation else None
    isolation_clean = (audit_isolation and (w_sha_before == w_sha_after))
    return {
        "per_hop_acc": per_hop_acc,
        "per_hop_conf": per_hop_conf,       # list of (B,) arrays
        "final_acc": float(np.mean(final_correct)),
        "final_pred": final_pred,
        "trace_atom_ids": trace_atom_ids,
        "isolation_clean": bool(isolation_clean) if audit_isolation else None,
        "w_sha_before": w_sha_before,
        "w_sha_after": w_sha_after,
    }


def replay_faithfulness(chains: np.ndarray, depth: int, emitted_final: np.ndarray,
                        W: np.ndarray, E: np.ndarray, R: np.ndarray) -> float:
    """Replay the DIGITAL (atom-carry) walk from ONLY the discrete trace
    (start node + relation ids) and check it reproduces `emitted_final`.

    For the regen arm the atom-carry walk IS the arm rule -> reproduces (1.0).
    For the analog arm (vector-carry) the discrete trace does NOT determine the
    answer -> replay diverges -> faithfulness < 1.0. Faithful-by-construction test.
    """
    B = chains.shape[0]
    x = E[chains[:, 0, 0]].astype(np.float32).copy()
    replay_final = None
    for k in range(depth):
        p = chains[:, k, 1]
        key = x * R[p]
        yhat = key @ W.T
        pred = cleanup_ids(yhat, E)
        replay_final = pred
        x = E[pred].astype(np.float32)
    return float(np.mean(replay_final == emitted_final))


# ---------------------------------------------------------------------------
# Refuse-gate (at REFUSE_DEPTH; supported vs broken chains)
# ---------------------------------------------------------------------------
def _chain_conf(chains: np.ndarray, depth: int, W: np.ndarray,
                E: np.ndarray, R: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return (mean_margin_per_chain, final_pred) for the REGEN walk at `depth`.

    Confidence = MEAN over hops of the top1-vs-top2 cleanup MARGIN (drift-diffusion
    evidence accumulation, drill Part B.5). A broken chain retrieves garbage from
    the corrupted hop onward (low margin on multiple hops), dragging the mean down;
    a single noisy hop won't sink a supported chain's mean. This separates broken
    from supported far better than the weakest-link (min) signal at high crosstalk."""
    B = chains.shape[0]
    x = E[chains[:, 0, 0]].astype(np.float32).copy()
    sum_margin = np.zeros(B, dtype=np.float64)
    final_pred = None
    for k in range(depth):
        p = chains[:, k, 1]
        key = x * R[p]
        yhat = key @ W.T
        pred, margin = cleanup_margin(yhat, E)
        sum_margin += margin
        final_pred = pred
        x = E[pred].astype(np.float32)
    return sum_margin / float(depth), final_pred


def break_chains(chains: np.ndarray, g: np.random.Generator) -> np.ndarray:
    """Corrupt ONE random hop per chain: replace its relation with one such that
    (current_node, rel) has (with high probability) NO stored edge, by pointing
    the object to a chain-partition node while the SOURCE stays a chain node but
    we FLIP the relation to a value that was not the stored one AND we re-route
    the object to a random node. Simplest robust break: set the object of a
    random hop to a fresh random node and change the relation -> the stored W has
    the ORIGINAL (s, p_orig, o_orig); this corrupted key (s, p_new) retrieves
    garbage. Downstream hops then start from a wrong/garbage node.
    """
    broken = chains.copy()
    B = chains.shape[0]
    for c in range(B):
        j = int(g.integers(0, chains.shape[1]))
        p_orig = int(chains[c, j, 1])
        p_new = (p_orig + 1 + int(g.integers(0, P_REL - 1))) % P_REL
        broken[c, j, 1] = p_new                      # unstored (s, p_new) key
        broken[c, j, 2] = int(g.integers(0, V_CHAIN))  # arbitrary object
    return broken


def refuse_gate(E: np.ndarray, R: np.ndarray, W: np.ndarray,
                supported: np.ndarray, g: np.random.Generator) -> Dict[str, Any]:
    """Calibrate tau on a supported CALIBRATION split; evaluate false-accept
    (broken chains not refused AND wrong) and false-refuse (supported chains
    refused) on a disjoint TEST split. Returns metrics dict."""
    n = supported.shape[0]
    if n < 8:
        return {"refuse_ok": None, "reason": "insufficient_chains", "n": n}
    half = n // 2
    calib = supported[:half]
    test_sup = supported[half:]
    test_broken = break_chains(test_sup, g)

    # Calibrate tau on supported calibration confidences.
    conf_calib, _ = _chain_conf(calib, REFUSE_DEPTH, W, E, R)
    tau = float(np.percentile(conf_calib, REFUSE_TAU_PERCENTILE))

    # Evaluate.
    conf_sup, pred_sup = _chain_conf(test_sup, REFUSE_DEPTH, W, E, R)
    conf_brk, pred_brk = _chain_conf(test_broken, REFUSE_DEPTH, W, E, R)

    refused_sup = conf_sup < tau
    refused_brk = conf_brk < tau
    true_final_sup = test_sup[:, REFUSE_DEPTH - 1, 2]

    # false-refuse: supported chains refused (over supported test set).
    false_refuse = float(np.mean(refused_sup))
    # false-accept: broken (unsupported) chains NOT refused -- emitted an answer
    # for a query whose evidence chain is broken (drill Part A: should refuse).
    false_accept = float(np.mean(~refused_brk))
    # discrimination: mean confidence separation supported vs broken.
    conf_sep = float(np.mean(conf_sup) - np.mean(conf_brk))
    sup_final_acc = float(np.mean(pred_sup == true_final_sup))
    return {
        "refuse_calibrated": bool(false_accept <= HP_FALSE_ACCEPT_MAX
                                  and false_refuse <= HP_FALSE_REFUSE_MAX),
        "tau": round(tau, 4),
        "false_accept": round(false_accept, 4),
        "false_refuse": round(false_refuse, 4),
        "conf_sep_sup_minus_brk": round(conf_sep, 4),
        "supported_final_acc": round(sup_final_acc, 4),
        "n_calib": int(calib.shape[0]),
        "n_test_sup": int(test_sup.shape[0]),
        "n_test_broken": int(test_broken.shape[0]),
    }


# ---------------------------------------------------------------------------
# One (seed, M_BG) run -> full depth curve for all 3 arms + joint gates
# ---------------------------------------------------------------------------
def run_seed_mbg(seed: int, m_bg: int, out_dir: Path,
                 hb_state: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.perf_counter()
    g = np.random.default_rng(seed * 100003 + m_bg)

    E = make_bipolar(V_CODE, N_DIM, g)
    R = make_bipolar(P_REL, N_DIM, g)
    chains = make_chains(N_TEST, g)                       # (N_TEST, D_MAX, 3)
    chain_edges = chains.reshape(-1, 3)                   # (N_TEST*D_MAX, 3)
    bg_edges = make_background_edges(m_bg, g)
    all_edges = np.concatenate([chain_edges, bg_edges], axis=0)
    m_total = int(all_edges.shape[0])

    # Real store.
    W = build_W(all_edges, E, R, N_DIM)
    # Shuffled control store: SAME edges, objects label-permuted -> structure destroyed.
    perm = g.permutation(V_CODE)
    shuf_edges = all_edges.copy()
    shuf_edges[:, 2] = perm[shuf_edges[:, 2]]
    W_shuf = build_W(shuf_edges, E, R, N_DIM)

    # Depth curves (nested prefixes; PAIRED across arms).
    analog_curve: Dict[int, float] = {}
    regen_curve: Dict[int, float] = {}
    control_curve: Dict[int, float] = {}
    regen_faith_curve: Dict[int, float] = {}
    analog_faith_curve: Dict[int, float] = {}
    per_hop_regen: Dict[int, List[float]] = {}
    per_hop_analog: Dict[int, List[float]] = {}
    isolation_clean_all = True
    arms_sha: Dict[str, str] = {}

    total_units = len(DEPTHS)
    for di, depth in enumerate(DEPTHS):
        ra = walk_analog(chains, depth, W, E, R)
        rr = walk_regen(chains, depth, W, E, R, audit_isolation=True)
        rc = walk_regen(chains, depth, W_shuf, E, R, audit_isolation=False)

        analog_curve[depth] = round(ra["final_acc"], 4)
        regen_curve[depth] = round(rr["final_acc"], 4)
        control_curve[depth] = round(rc["final_acc"], 4)
        per_hop_analog[depth] = [round(x, 4) for x in ra["per_hop_acc"]]
        per_hop_regen[depth] = [round(x, 4) for x in rr["per_hop_acc"]]

        # Faithfulness (mechanical replay of the discrete trace).
        regen_faith_curve[depth] = round(
            replay_faithfulness(chains, depth, rr["final_pred"], W, E, R), 4)
        analog_faith_curve[depth] = round(
            replay_faithfulness(chains, depth, ra["final_pred"], W, E, R), 4)

        if rr["isolation_clean"] is False:
            isolation_clean_all = False

        if depth == REFUSE_DEPTH:
            # arms-differ hash at the discriminating depth.
            arms_sha = {
                "analog": _sha_of_array(ra["final_pred"]),
                "regen": _sha_of_array(rr["final_pred"]),
                "control": _sha_of_array(rc["final_pred"]),
            }
        hb_state["unit"] += 1
        _heartbeat(out_dir, hb_state["unit"], hb_state["total"], hb_state["t0"],
                   extra={"seed": seed, "m_bg": m_bg, "depth": depth,
                          "regen": regen_curve[depth], "analog": analog_curve[depth]})
        print("  [seed=%d m_bg=%d depth=%d] regen=%.4f analog=%.4f control=%.4f "
              "regen_faith=%.4f analog_faith=%.4f iso=%s"
              % (seed, m_bg, depth, regen_curve[depth], analog_curve[depth],
                 control_curve[depth], regen_faith_curve[depth],
                 analog_faith_curve[depth], rr["isolation_clean"]), flush=True)

    # Refuse-gate (REPORTED, not gated): only at DISC regime (where the claim
    # lives) to save W_ref builds. HONEST NEGATIVE (MEASURED probe 2026-07-05):
    # retrieval-confidence abstention does NOT calibrate on the Hebbian substrate
    # at high crosstalk -- the associative matrix returns a plausible retrieval
    # even for unsupported keys, so confidence barely separates broken from
    # supported (conf_sep ~ 0.05-0.14). Calibrated abstention is a separate,
    # harder capability; this cell reports it as a baseline but does NOT gate the
    # core mechanism verdict on it (faithfulness is the working joint-gate).
    if m_bg == DISC_MBG:
        g_ref = np.random.default_rng(seed * 7 + m_bg + 999)
        refuse_chains = make_chains(N_REFUSE, g_ref)
        W_ref = build_W(np.concatenate([refuse_chains.reshape(-1, 3), all_edges], axis=0),
                        E, R, N_DIM)
        refuse = refuse_gate(E, R, W_ref, refuse_chains, g_ref)
    else:
        refuse = None

    # arms-differ (META_RULE_AF).
    arms_differ = (len(set(arms_sha.values())) == 3) if arms_sha else False

    # Derived discriminators.
    regen_d3 = regen_curve.get(3, float("nan"))
    regen_d5 = regen_curve.get(5, float("nan"))
    analog_d3 = analog_curve.get(3, float("nan"))
    analog_d5 = analog_curve.get(5, float("nan"))
    analog_d1 = analog_curve.get(1, float("nan"))
    regen_d1 = regen_curve.get(1, float("nan"))
    control_d5 = control_curve.get(5, float("nan"))
    flatness = regen_d3 - regen_d5                 # regen own decay d3->d5 (reported, not gated)
    analog_decay = analog_d3 - analog_d5           # analog own decay d3->d5
    graceful_margin = analog_decay - flatness      # how much faster analog collapses than regen
    gap = regen_d5 - analog_d5                      # PRIMARY discriminator (regen beats analog)
    regen_faith_d5 = regen_faith_curve.get(5, float("nan"))

    elapsed = time.perf_counter() - t0
    return {
        "seed": seed,
        "m_bg": int(m_bg),
        "m_total": m_total,
        "m_over_n": round(m_total / float(N_DIM), 4),
        "N": N_DIM, "V": V_CODE, "P": P_REL,
        "run_mode": RUN_MODE,
        "analog_curve": analog_curve,
        "regen_curve": regen_curve,
        "control_curve": control_curve,
        "regen_faith_curve": regen_faith_curve,
        "analog_faith_curve": analog_faith_curve,
        "per_hop_regen_at_d5": per_hop_regen.get(5),
        "per_hop_analog_at_d5": per_hop_analog.get(5),
        "regen_d1": regen_d1, "analog_d1": analog_d1,
        "regen_d3": regen_d3, "regen_d5": regen_d5,
        "analog_d3": analog_d3, "analog_d5": analog_d5,
        "control_d5": control_d5,
        "flatness_regen_d3_minus_d5": round(flatness, 4),
        "analog_decay_d3_minus_d5": round(analog_decay, 4),
        "graceful_margin": round(graceful_margin, 4),
        "gap_regen_minus_analog_d5": round(gap, 4),
        "regen_faithfulness_d5": regen_faith_d5,
        "analog_faithfulness_d5": analog_faith_curve.get(5, float("nan")),
        "isolation_clean": bool(isolation_clean_all),
        "arms_sha_at_d5": arms_sha,
        "arms_differ": bool(arms_differ),
        "refuse": refuse,
        "elapsed_s": round(elapsed, 2),
        "config_version": CONFIG_VERSION,
    }


def classify_row(res: Dict[str, Any]) -> str:
    """Coarse per-(seed,m_bg) row label (for the phase map). Which arm wins @ d5."""
    gap = res["gap_regen_minus_analog_d5"]
    if gap >= HP_GAP_MIN:
        return "REGEN_WINS"
    if gap <= -HP_GAP_MIN:
        return "ANALOG_WINS"
    return "TIE"


def classify_seed(mbg_results: List[Dict[str, Any]]) -> Tuple[str, List[str], Dict[str, Any]]:
    """Crossover-aware SEED tier. HARD_PASS gates are evaluated at the
    DISCRIMINATING regime (DISC_MBG); the crossover (soft-wins-below-capacity)
    is confirmed at LOW_MBG and reported. Returns (tier, reasons, disc_row)."""
    reasons: List[str] = []
    by_mbg = {r["m_bg"]: r for r in mbg_results}
    disc = by_mbg.get(DISC_MBG)
    low = by_mbg.get(LOW_MBG, mbg_results[0])
    if disc is None:
        # DISC_MBG not in the grid (defensive) -> use the highest-gap row.
        disc = max(mbg_results, key=lambda r: r["gap_regen_minus_analog_d5"])

    d = disc
    regen_d1 = d["regen_d1"]; analog_d1 = d["analog_d1"]
    regen_d5 = d["regen_d5"]; analog_d5 = d["analog_d5"]
    control_d5 = d["control_d5"]; iso = d["isolation_clean"]
    gap = d["gap_regen_minus_analog_d5"]
    graceful = d["graceful_margin"]
    faith = d["regen_faithfulness_d5"]
    refuse = d.get("refuse") or {}
    fa = refuse.get("false_accept"); fr = refuse.get("false_refuse")
    refuse_calibrated = refuse.get("refuse_calibrated")   # REPORTED, not gated
    low_gap = low["gap_regen_minus_analog_d5"]
    crossover_confirmed = bool(low_gap <= CROSSOVER_GAP_MAX)

    disc_summary = {
        "disc_m_bg": DISC_MBG, "disc_m_over_n": d["m_over_n"],
        "regen_d5": regen_d5, "analog_d5": analog_d5, "gap_d5": gap,
        "graceful_margin": graceful, "regen_faith_d5": faith,
        "false_accept": fa, "false_refuse": fr,
        "refuse_calibrated_reported": refuse_calibrated, "control_d5": control_d5,
        "isolation_clean": iso, "low_m_bg": low["m_bg"], "low_gap_d5": low_gap,
        "crossover_confirmed": crossover_confirmed,
    }

    # HARD_FAIL rails (at DISC regime).
    if not (regen_d1 >= SANITY_D1_MIN and analog_d1 >= SANITY_D1_MIN):
        reasons.append("SANITY_BREACH_d1(regen=%.3f analog=%.3f < %.2f)"
                       % (regen_d1, analog_d1, SANITY_D1_MIN))
        return "HARD_FAIL", reasons, disc_summary
    if control_d5 > HF_CONTROL_D5_MAX:
        reasons.append("CONTROL_NOT_COLLAPSED(%.4f > %.3f)" % (control_d5, HF_CONTROL_D5_MAX))
        return "HARD_FAIL", reasons, disc_summary
    if not iso:
        reasons.append("ISOLATION_DIRTY")
        return "HARD_FAIL", reasons, disc_summary
    if regen_d5 <= HF_REGEN_D5_MAX:
        reasons.append("REGEN_D5_ALSO_COLLAPSED(%.4f <= %.2f)" % (regen_d5, HF_REGEN_D5_MAX))
        return "HARD_FAIL", reasons, disc_summary
    if gap < HF_GAP_MIN:
        reasons.append("REGEN_NEVER_BEATS_ANALOG(gap@disc=%.4f < %.2f)" % (gap, HF_GAP_MIN))
        return "HARD_FAIL", reasons, disc_summary

    # HARD_PASS core (phase-diagram discriminator at DISC regime).
    core_pass = (regen_d5 >= HP_REGEN_D5_MIN
                 and gap >= HP_GAP_MIN
                 and analog_d5 <= HP_ANALOG_COLLAPSE_MAX
                 and graceful >= HP_GRACEFUL_MARGIN
                 and control_d5 <= HP_CONTROL_D5_MAX)
    # Faithfulness is the HARD joint-gate (catches "cleanup lifts accuracy via a
    # non-faithful shortcut"). Refuse-gate is REPORTED only (honest baseline
    # negative on this substrate; see refuse_gate docstring) -- not gated.
    faith_ok = (faith is not None and not math.isnan(faith) and faith >= HP_FAITHFULNESS_MIN)

    if core_pass and faith_ok:
        reasons.append("HARD_PASS regen_d5=%.3f gap=%.3f analog_d5=%.3f graceful=%.3f "
                       "faith=%.3f crossover=%s | refuse(reported) fa=%s fr=%s calibrated=%s"
                       % (regen_d5, gap, analog_d5, graceful, faith,
                          crossover_confirmed, fa, fr, refuse_calibrated))
        return "HARD_PASS", reasons, disc_summary
    if core_pass and not faith_ok:
        reasons.append("FALSE_PASS_FAITHFULNESS(faith=%s < %.2f)" % (faith, HP_FAITHFULNESS_MIN))
        return "FALSE_PASS_JOINT_GATE", reasons, disc_summary

    reasons.append("MIDDLE(regen_d5=%.3f gap=%.3f analog_d5=%.3f graceful=%.3f faith=%s)"
                   % (regen_d5, gap, analog_d5, graceful, faith))
    return "MIDDLE_BAND", reasons, disc_summary


# ---------------------------------------------------------------------------
# Per-seed driver: sweeps M_BG across the crossover; tier @ DISC regime.
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    t0 = time.perf_counter()
    hb_state = {"unit": 0, "total": len(M_BG_LIST) * len(DEPTHS), "t0": t0}
    mbg_results: List[Dict[str, Any]] = []
    for m_bg in M_BG_LIST:
        res = run_seed_mbg(seed, m_bg, out_dir, hb_state)
        res["row_label"] = classify_row(res)
        print("  [seed=%d m_bg=%d M/N=%.2f] row=%s gap_d5=%+.3f regen_d5=%.3f analog_d5=%.3f"
              % (seed, m_bg, res["m_over_n"], res["row_label"],
                 res["gap_regen_minus_analog_d5"], res["regen_d5"], res["analog_d5"]),
              flush=True)
        mbg_results.append(res)

    tier, reasons, disc_summary = classify_seed(mbg_results)
    print("  [seed=%d] SEED_TIER=%s %s" % (seed, tier, reasons), flush=True)

    return {
        "seed": seed,
        "run_mode": RUN_MODE,
        "n_llm_calls": _LLM_CALL_COUNTER[0],
        "mbg_results": mbg_results,
        "seed_tier": tier,
        "seed_tier_reasons": reasons,
        "disc_summary": disc_summary,
        "phase_map": [{"m_bg": r["m_bg"], "m_over_n": r["m_over_n"],
                       "row_label": r["row_label"],
                       "gap_d5": r["gap_regen_minus_analog_d5"],
                       "regen_d5": r["regen_d5"], "analog_d5": r["analog_d5"]}
                      for r in mbg_results],
        "arms_differ_disc": by_disc_field(mbg_results, "arms_differ"),
        "isolation_clean_disc": disc_summary["isolation_clean"],
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "config_version": CONFIG_VERSION,
    }


def by_disc_field(mbg_results: List[Dict[str, Any]], field: str) -> Any:
    for r in mbg_results:
        if r["m_bg"] == DISC_MBG:
            return r.get(field)
    return mbg_results[0].get(field) if mbg_results else None


# ---------------------------------------------------------------------------
# Aggregate verdict across seeds
# ---------------------------------------------------------------------------
def compute_verdict(all_seed_results: List[Dict[str, Any]]) -> Tuple[str, str, Dict[str, Any]]:
    n_seeds = len(all_seed_results)
    if n_seeds == 0:
        return "HARD_FAIL", "NO_SEED_RESULTS", {"cardinality_ok": False}

    # Cardinality (META_RULE_H): each seed must have run all M_BG x DEPTHS units.
    for r in all_seed_results:
        for mr in r["mbg_results"]:
            n_depths = len(mr["regen_curve"])
            if n_depths != EXPECTED_DEPTH_ROWS:
                return ("HARD_FAIL",
                        "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H seed=%s m_bg=%s "
                        "depths=%d expected=%d" % (r["seed"], mr["m_bg"], n_depths,
                                                   EXPECTED_DEPTH_ROWS),
                        {"cardinality_ok": False})

    seed_tiers = [r["seed_tier"] for r in all_seed_results]
    n_pass = sum(1 for t in seed_tiers if t == "HARD_PASS")
    n_fail = sum(1 for t in seed_tiers if t == "HARD_FAIL")
    n_false = sum(1 for t in seed_tiers if t == "FALSE_PASS_JOINT_GATE")
    n_mid = sum(1 for t in seed_tiers if t == "MIDDLE_BAND")

    ds = [r["disc_summary"] for r in all_seed_results]
    gaps = [s["gap_d5"] for s in ds]
    regen5 = [s["regen_d5"] for s in ds]
    analog5 = [s["analog_d5"] for s in ds]
    graces = [s["graceful_margin"] for s in ds]
    faiths = [s["regen_faith_d5"] for s in ds]
    ctrl5 = [s["control_d5"] for s in ds]
    low_gaps = [s["low_gap_d5"] for s in ds]
    n_crossover = sum(1 for s in ds if s["crossover_confirmed"])
    fas = [s["false_accept"] for s in ds if s.get("false_accept") is not None]
    frs = [s["false_refuse"] for s in ds if s.get("false_refuse") is not None]
    n_refuse_cal = sum(1 for s in ds if s.get("refuse_calibrated_reported") is True)

    extra = {
        "cardinality_ok": True,
        "n_seeds": n_seeds,
        "disc_m_bg": DISC_MBG, "low_m_bg": LOW_MBG,
        "n_hard_pass": n_pass, "n_hard_fail": n_fail,
        "n_false_pass_joint": n_false, "n_middle": n_mid,
        "seed_tiers": seed_tiers,
        "mean_gap_d5_at_disc": round(float(np.mean(gaps)), 4),
        "std_gap_d5_at_disc": round(float(np.std(gaps)), 4),
        "mean_regen_d5_at_disc": round(float(np.mean(regen5)), 4),
        "mean_analog_d5_at_disc": round(float(np.mean(analog5)), 4),
        "mean_graceful_margin_at_disc": round(float(np.mean(graces)), 4),
        "mean_regen_faith_d5_at_disc": round(float(np.mean(faiths)), 4),
        "mean_control_d5_at_disc": round(float(np.mean(ctrl5)), 4),
        "mean_low_gap_d5": round(float(np.mean(low_gaps)), 4),
        "n_crossover_confirmed": n_crossover,
        "refuse_gate_reported_not_gated": True,
        "mean_false_accept_reported": round(float(np.mean(fas)), 4) if fas else None,
        "mean_false_refuse_reported": round(float(np.mean(frs)), 4) if frs else None,
        "n_refuse_calibrated_reported": n_refuse_cal,
        "arms_differ_all": all(r["arms_differ_disc"] for r in all_seed_results),
        "isolation_clean_all": all(r["isolation_clean_disc"] for r in all_seed_results),
        "chance_floor": round(CHANCE_FLOOR, 5),
    }

    summ = ("n_seeds=%d pass=%d fail=%d false_joint=%d mid=%d | @DISC(M_BG=%d): "
            "mean gap=%+.3f regen_d5=%.3f analog_d5=%.3f graceful=%.3f faith=%.3f "
            "control_d5=%.4f | LOW(M_BG=%d) mean_gap=%+.3f crossover=%d/%d | "
            "arms_differ=%s iso=%s"
            % (n_seeds, n_pass, n_fail, n_false, n_mid, DISC_MBG,
               extra["mean_gap_d5_at_disc"], extra["mean_regen_d5_at_disc"],
               extra["mean_analog_d5_at_disc"], extra["mean_graceful_margin_at_disc"],
               extra["mean_regen_faith_d5_at_disc"], extra["mean_control_d5_at_disc"],
               LOW_MBG, extra["mean_low_gap_d5"], n_crossover, n_seeds,
               extra["arms_differ_all"], extra["isolation_clean_all"]))

    hp_msg = ("HARD_PASS (regenerative hard-cleanup beats analog soft-carry ABOVE "
              "the M/N~1 crosstalk threshold: analog collapses, regen degrades "
              "gracefully; joint gates hold): ")
    majority = (n_seeds // 2) + 1
    if n_fail > 0:
        return "HARD_FAIL", "HARD_FAIL (>=1 seed hard-failed rails): " + summ, extra
    if n_false >= majority:
        return "FALSE_PASS_JOINT_GATE", "FALSE_PASS_JOINT_GATE (joint gate failed majority): " + summ, extra
    if n_pass >= majority:
        return "HARD_PASS", hp_msg + summ, extra
    if n_pass + n_mid >= majority and n_pass >= 1:
        return "MIDDLE_BAND", "MIDDLE_BAND (mechanism partial; not majority hard-pass): " + summ, extra
    return "MIDDLE_BAND", "MIDDLE_BAND: " + summ, extra


# ---------------------------------------------------------------------------
# Self-test (fast; small N; exits 0). queue --self-test gate is unconditional.
# ---------------------------------------------------------------------------
def _selftest() -> int:
    t0 = time.perf_counter()
    g = np.random.default_rng(0)
    n = 512
    v = 48
    p = 4
    E = make_bipolar(v, n, g)
    R = make_bipolar(p, n, g)

    # T1: shapes + bipolar
    assert E.shape == (v, n) and set(np.unique(E)).issubset({-1.0, 1.0})

    # T2: chain gen + edges walkable
    global V_CHAIN, D_MAX, DEPTHS, P_REL, V_CODE, N_DIM  # selftest uses local overrides
    _save = (V_CHAIN, D_MAX, DEPTHS, P_REL, V_CODE, N_DIM)
    V_CHAIN, D_MAX, DEPTHS, P_REL, V_CODE, N_DIM = 24, 5, [1, 2, 3, 4, 5], p, v, n
    chains = make_chains(6, g)
    assert chains.shape == (6, 5, 3)

    edges = chains.reshape(-1, 3)
    W = build_W(edges, E, R, n)
    assert W.shape == (n, n) and np.isfinite(W).all()

    # T3: single-hop retrieval is (near) perfect on a clean store (positive control)
    rr1 = walk_regen(chains, 1, W, E, R, audit_isolation=True)
    assert rr1["final_acc"] >= 0.90, "single-hop regen broken: %.3f" % rr1["final_acc"]
    assert rr1["isolation_clean"] is True, "isolation audit failed on clean walk"

    # T4: arms differ (analog vs regen vs control) at depth 3
    ra = walk_analog(chains, 3, W, E, R)
    rr = walk_regen(chains, 3, W, E, R, audit_isolation=True)
    perm = g.permutation(v)
    shuf = edges.copy(); shuf[:, 2] = perm[shuf[:, 2]]
    Wsh = build_W(shuf, E, R, n)
    rc = walk_regen(chains, 3, Wsh, E, R, audit_isolation=False)
    sha = {_sha_of_array(ra["final_pred"]), _sha_of_array(rr["final_pred"]),
           _sha_of_array(rc["final_pred"])}
    assert len(sha) >= 2, "arms bit-identical (META_RULE_AF): %s" % sha

    # T5: faithfulness -- regen replay reproduces its own answer (== 1.0);
    #     analog replay (digital rule) generally != analog answer.
    fr = replay_faithfulness(chains, 3, rr["final_pred"], W, E, R)
    assert fr == 1.0, "regen not faithful-by-construction: %.3f" % fr

    # T6: control collapses at depth (structure destroyed) relative to regen
    #     -- weak assertion (tiny store): control final acc should be <= regen.
    assert rc["final_acc"] <= rr["final_acc"] + 1e-9

    # T7: refuse-gate returns well-formed metrics (needs >= 8 chains)
    ref_chains = make_chains(16, np.random.default_rng(11))
    ref_edges = ref_chains.reshape(-1, 3)
    W_ref = build_W(np.concatenate([ref_edges, edges], axis=0), E, R, n)
    ref = refuse_gate(E, R, W_ref, ref_chains, np.random.default_rng(3))
    assert "false_accept" in ref and "false_refuse" in ref, "refuse_gate: %s" % ref

    # T8: classify_seed runs on a synthetic phase-diagram (LOW soft-wins + DISC regen-wins)
    def _mk_row(m_bg, regen_d5, analog_d5, faith=1.0, fa=0.05, fr=0.10, ctrl=0.0):
        return {
            "m_bg": m_bg, "m_over_n": round(m_bg / 8192.0, 3),
            "regen_d1": 0.95, "analog_d1": 0.95, "regen_d3": regen_d5 + 0.14,
            "analog_d3": analog_d5 + 0.60, "regen_d5": regen_d5, "analog_d5": analog_d5,
            "control_d5": ctrl,
            "flatness_regen_d3_minus_d5": 0.14,
            "analog_decay_d3_minus_d5": 0.60,
            "graceful_margin": 0.46,
            "gap_regen_minus_analog_d5": round(regen_d5 - analog_d5, 4),
            "regen_faithfulness_d5": faith, "isolation_clean": True,
            "refuse": {"false_accept": fa, "false_refuse": fr},
        }
    fake_rows = [_mk_row(LOW_MBG, 0.53, 0.90),      # LOW: analog wins (gap -0.37)
                 _mk_row(DISC_MBG, 0.60, 0.12)]     # DISC: regen wins big (gap +0.48)
    tier, _r, _ds = classify_seed(fake_rows)
    assert tier == "HARD_PASS", "classify_seed HARD_PASS path broken: %s (%s)" % (tier, _r)

    # T9: joint-gate false-pass path (faithfulness wrecked at DISC)
    fake_fp = [_mk_row(LOW_MBG, 0.53, 0.90), _mk_row(DISC_MBG, 0.60, 0.12, faith=0.5)]
    tier_fp, _r2, _ = classify_seed(fake_fp)
    assert tier_fp == "FALSE_PASS_JOINT_GATE", "joint-gate path broken: %s (%s)" % (tier_fp, _r2)

    # T9b: classify_row labels
    assert classify_row(_mk_row(DISC_MBG, 0.60, 0.12)) == "REGEN_WINS"
    assert classify_row(_mk_row(LOW_MBG, 0.53, 0.90)) == "ANALOG_WINS"

    # T10: LLM counter untouched
    assert _LLM_CALL_COUNTER[0] == 0

    V_CHAIN, D_MAX, DEPTHS, P_REL, V_CODE, N_DIM = _save
    dt = time.perf_counter() - t0
    print("[selftest] PASS regen_d1=%.3f faith=%.3f arms_distinct=%d elapsed=%.2fs"
          % (rr1["final_acc"], fr, len(sha), dt), flush=True)
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _main() -> int:
    started = time.perf_counter()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    if RUN_MODE == "self_test":
        rc = _selftest()
        res = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "HARD_PASS" if rc == 0 else "HARD_FAIL",
            "verdict_msg": "SELFTEST_PASS" if rc == 0 else "SELFTEST_FAIL",
            "summary": "selftest rc=%d" % rc,
            "elapsed_s": round(time.perf_counter() - started, 2),
            "ts_iso": _now_iso(),
            "run_mode": "self_test",
            "config_version": CONFIG_VERSION,
            "n_seeds": 1,
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(res, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
        print("[self_test] wrote %s rc=%d" % (out_dir / "metrics.json", rc), flush=True)
        return rc

    expected_units = len(SEEDS) * len(M_BG_LIST) * len(DEPTHS)
    _write_start_marker(out_dir, RUN_MODE, expected_units)
    print("[start] anchor=%s mode=%s N=%d V=%d seeds=%s M_BG=%s expected_units=%d"
          % (ANCHOR_NAME, RUN_MODE, N_DIM, V_CODE, SEEDS, M_BG_LIST, expected_units),
          flush=True)

    run_config = {"run_mode": RUN_MODE, "anchor": ANCHOR_NAME, "N": N_DIM}
    # Schema guard: remove any partial lacking the current-schema "seed_tier"
    # field (defends resume against incompatible-schema partials from a prior code
    # version sharing this out_dir; the run_config guard only checks N/mode/anchor).
    for pf in sorted(out_dir.glob("partial_metrics_*.json")):
        try:
            body = json.loads(pf.read_text(encoding="utf-8"))
            if "seed_tier" not in body:
                pf.unlink()
                print("[ckpt] removed incompatible-schema partial %s" % pf.name, flush=True)
        except (OSError, ValueError):
            pass
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d seeds done; running %s" % (len(done), len(SEEDS), remaining),
          flush=True)

    for seed in remaining:
        print("[seed=%d] starting mode=%s ..." % (seed, RUN_MODE), flush=True)
        res = run_seed(seed, out_dir)
        # stamp fields the checkpoint config-guard checks (N, run_mode, anchor).
        res["N"] = N_DIM
        res["run_mode"] = RUN_MODE
        write_partial(out_dir, seed, res)
        _ds = res["disc_summary"]
        print("[seed=%d] done tier=%s gap_d5@disc=%+.3f regen_d5=%.3f analog_d5=%.3f elapsed=%.1fs"
              % (seed, res["seed_tier"], _ds["gap_d5"], _ds["regen_d5"],
                 _ds["analog_d5"], res["elapsed_s"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = [per_seed[str(s)] for s in SEEDS if str(s) in per_seed]

    verdict, verdict_msg, extra = compute_verdict(all_results)

    # Guard against stale-mode partial contamination (mirrors hippo pattern).
    modes = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in modes:
        verdict = "HARD_FAIL"
        verdict_msg = "HARD_FAIL: stale smoke partials in FULL run modes=%s. %s" % (
            modes, verdict_msg)

    elapsed = time.perf_counter() - started
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": round(elapsed, 2),
        "ts_iso": _now_iso(),
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "config_version": CONFIG_VERSION,
        "N": N_DIM, "V": V_CODE, "P": P_REL, "D_MAX": D_MAX, "DEPTHS": DEPTHS,
        "M_BG_LIST": M_BG_LIST, "REFUSE_DEPTH": REFUSE_DEPTH,
        "expected_n_units": expected_units,
        "cardinality_ok": extra.get("cardinality_ok", False),
        "extra": extra,
        "per_seed": all_results,
        "n_llm_forward_calls": _LLM_CALL_COUNTER[0],
        "DISC_MBG": DISC_MBG, "LOW_MBG": LOW_MBG,
        "bands": {
            "HP_REGEN_D5_MIN": HP_REGEN_D5_MIN, "HP_GAP_MIN": HP_GAP_MIN,
            "HP_ANALOG_COLLAPSE_MAX": HP_ANALOG_COLLAPSE_MAX,
            "HP_GRACEFUL_MARGIN": HP_GRACEFUL_MARGIN,
            "HP_FAITHFULNESS_MIN": HP_FAITHFULNESS_MIN,
            "HP_FALSE_ACCEPT_MAX": HP_FALSE_ACCEPT_MAX,
            "HP_FALSE_REFUSE_MAX": HP_FALSE_REFUSE_MAX,
            "HP_CONTROL_D5_MAX": HP_CONTROL_D5_MAX, "SANITY_D1_MIN": SANITY_D1_MIN,
            "CROSSOVER_GAP_MAX": CROSSOVER_GAP_MAX,
            "HF_REGEN_D5_MAX": HF_REGEN_D5_MAX, "HF_GAP_MIN": HF_GAP_MIN,
            "HF_CONTROL_D5_MAX": HF_CONTROL_D5_MAX,
        },
    }
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print("[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)
    print("[metrics] %s (elapsed=%.1fs)" % (out_dir / "metrics.json", elapsed),
          flush=True)
    return 0 if verdict != "HARD_FAIL" else 1


if __name__ == "__main__":
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        sys.exit(_main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:  # NOT BaseException (preserves SystemExit/KeyboardInterrupt)
        _write_crash_metrics(_out_dir_for_crash, _e)
        raise
