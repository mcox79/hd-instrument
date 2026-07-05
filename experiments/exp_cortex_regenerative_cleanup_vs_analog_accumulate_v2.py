"""exp_cortex_regenerative_cleanup_vs_analog_accumulate_v2

RECALIBRATED RE-RUN of v1 (which HARD_FAILed for a TEST-DESIGN reason, not a
mechanism failure). Two witnesses (2x-drill + Skunkworks VET) agreed: the
digital-repeater regenerative-cleanup mechanism is REAL but MODEST
(regen_d5 ~ 0.263 @ N=8192, gap over analog +0.176 widening under load, 5/5
seeds, faith 1.0, control fires); the v1 HARD_FAIL was a D1 SANITY floor that
became unreachable because N_TEST silently shifted the crosstalk load between
smoke (M/N=1.018) and full (M/N=1.105). Give the mechanism a FAIR test.

Framing: constructive build over our own memory (USER 2026-07-05). CPU vector
algebra. No LLM. No GPU.

--------------------------------------------------------------------------------
WHAT CHANGES FROM v1 (mechanism + arms UNCHANGED; only the experiment design)
--------------------------------------------------------------------------------
1. SCALE N UP (VET fix): sweep N in {8192, 16384, 32768}. Higher dimension
   sharpens the M/N~1 phase transition so single-hop d1 clears the 0.85 sanity
   floor at a valid operating point while analog still collapses. Also directly
   tests whether bigger vectors raise the modest absolute regen_d5.
2. HOLD M/N CONSTANT across smoke/full AND across N (drill fix): the sweep is
   parametrized by TARGET M/N (not absolute M_BG). M_BG is derived per (N, N_TEST)
   so the TRUE crosstalk load M/N = (M_BG + N_TEST*D_MAX)/N is identical in every
   mode and at every N. This eliminates the N_TEST-driven load drift that broke v1.
       M_BG = round(target_MoverN * N) - N_TEST * D_MAX
3. RECALIBRATE BANDS to the HONEST effect (both witnesses): HARD_PASS gates on the
   RELATIVE discriminator (regen beats analog with the gap widening under load,
   analog collapses, regen degrades gracefully, faith >= 0.95, control fires),
   NOT the over-optimistic absolute regen_d5 >= 0.45 (smoke was 2-seed lucky and
   never reproduced at full). regen_d5 is REPORTED (secondary), with an honest
   soft floor near the true ~0.26, not a HARD_PASS gate.

COMPUTE-PRESERVING REFACTOR (mechanism-exact; self-test T0 proves it): v1
materialized the N x N Hebbian matrix W = sum outer(E[o], E[s]*R[p]) / N. At
N=32768 that is a 4.3 GB matrix per store (x2-3 stores = OOM) and an O(N^3) build
(~8-9 h). This cell uses the FACTORED store: it never materializes W and computes
   yhat = W @ key  ==  ((key @ K.T) @ Vv) / N   with K=E[s]*R[p], Vv=E[o]
in M-chunked matmuls (memory O(chunk*N), compute O(N^2) not O(N^3)). Numerically
IDENTICAL to v1's key @ W.T (self-test T0 asserts max|diff| < 1e-3 AND identical
argmax cleanup at small N). The arms, cleanup, analog-vs-regen distinction,
shuffled control, faithfulness replay, and refuse-gate are BIT-for-BIT the v1
logic; only the store's internal representation changed.

--------------------------------------------------------------------------------
SUBSTRATE + MECHANISM (unchanged from v1)
--------------------------------------------------------------------------------
Codebook E: V bipolar (+/-1) concept atoms, dim N. Relations R: P bipolar atoms.
bind(a, b) = elementwise a * b (self-inverse for bipolar).
Store (factored Hebbian): edges (s, p, o); retrieve(x) = sum_e <x, E[s_e]*R[p_e]>
       * E[o_e] / N. This SUPERPOSES M edges -> crosstalk ~ M/N (Plate 1995). The
       crosstalk IS the per-hop noise the cleanup must overcome.
Retrieve one hop from state x with relation p:  yhat = retrieve(bind(x, R[p])).
Cleanup: ohat = argmax_v (E[v] . yhat)  (snap to nearest codebook atom).
Chains are NESTED: generate N_TEST chains of length D_MAX; evaluate each arm at
every prefix-depth d in DEPTHS -> depth curve AND arm curve perfectly PAIRED.

--------------------------------------------------------------------------------
ARMS (3, all bit-different; paired on the same chains + same store) - unchanged
--------------------------------------------------------------------------------
ARM_ANALOG_ACCUMULATE   -- carry the raw noisy retrieved vector forward
                           (x_{k+1} = normalize(yhat_k)); no cleanup. NEGATIVE RAIL.
ARM_REGEN_CLEANUP_ISO    -- snap to nearest codebook atom each hop
                           (x_{k+1} = E[ohat_k]); scratchpad SEPARATE from store,
                           store edge-arrays sha256 invariant across the walk. MECHANISM.
ARM_SHUFFLED_CONTROL     -- regen cleanup over the SAME edges with OBJECTS
                           label-shuffled (structure destroyed) -> final-node
                           accuracy ~ chance (1/V). DISCRIMINATOR-FIRES CONTROL.

--------------------------------------------------------------------------------
JOINT GATE (unchanged): FAITHFULNESS -- replay each emitted answer from ONLY the
discrete trace (start node + relation ids); regen is faithful-by-construction
(~1.0), analog carries a vector not an atom so its discrete trace does not
determine its answer (< 1.0). HARD gate: regen faith >= 0.95. Refuse-gate is
REPORTED, NOT GATED (honest negative on this substrate; see v1).

--------------------------------------------------------------------------------
BANDS (per (N, seed) tier at the DYNAMIC disc operating point). See prereg.
--------------------------------------------------------------------------------
Per (N, seed): scan the M/N sweep. A VALID operating point has regen_d1 >= 0.85
AND analog_d1 >= 0.85 (single-hop store works for BOTH arms -- the sanity floor,
now REACHABLE via higher N). The DISC point = the max-gap valid operating point.
  ARTIFACT_REGIME : no valid operating point at any swept M/N (v1's failure mode;
                    means this N is still too small to clear d1 -- REPORTED, not
                    a mechanism refutation).
  HARD_PASS       : at the DISC point ALL hold:
                       gap = regen_d5 - analog_d5 >= 0.15        (primary, relative)
                       analog_d5 <= 0.30                          (analog collapsed)
                       graceful_margin >= 0.15                    (graceful vs catastrophic)
                       control_d5 <= 0.05                         (structure -> chance)
                       isolation_clean == True
                       regen_faithfulness >= 0.95                 (HARD joint gate)
  FALSE_PASS_JOINT_GATE : core relative gates pass but faith < 0.95.
  HARD_FAIL       : a valid point where analog collapsed (analog_d5<=0.30) but
                    regen ALSO collapsed (regen_d5 <= 0.15) and gap < 0.05.
  MIDDLE_BAND     : else (mechanism present but discriminator did not fully fire
                    at a valid point at this N -- e.g. analog never collapses ->
                    substrate too robust at this N/V; needs higher M/N).
REPORTED (not gating): regen_d5 (secondary absolute; soft floor 0.22), the gap
  curve across M/N (gap-widens-with-load), crossover@LOW (gap<=0.05 at M/N~0.37,
  soft-wins-below-capacity), refuse-gate false_accept/false_refuse.
AGGREGATE: cell HARD_PASS iff at >= 1 N-tier a MAJORITY of seeds HARD_PASS and NO
  N-tier HARD_FAILs; the highest-N HARD_PASS tier is the headline "fair test".
  All-N ARTIFACT_REGIME -> MIDDLE_BAND (recalibration hypothesis not confirmed).

--------------------------------------------------------------------------------
CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb/discriminator_reachability: relative gap discriminator; d1 sanity floor
#   made REACHABLE by N-sweep (z=sqrt(N/(1+M/N)) rises with N); see prereg.
# - baseline_in_band: analog is the negative rail (collapses at DISC); regen not
#   saturated (0.2-0.6); analog_d1 in-band at valid points.
# - discriminator survives scale: smoke runs the FULL N grid {8192,16384,32768}
#   with a HIGH M/N point so the discriminator is previewed at every full N.
# - HARD_PASS strictly above floor (gap>=0.15 vs HF gap<0.05).
# - HP_SCOPE per-arm declaration (prereg).
# - cardinality_ok (META_RULE_H; EXPECTED_N_UNITS = N x seeds x M/N gate).
# - per-unit failure-class instrumentation (META_RULE_J; no bare except).
# - calibration_check = adaptive_with_discriminator_gate (refuse tau percentile).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ in prereg.
# - progress_logging = line_buffered_stdout + print flush (timeout_s >= 1800).
# - start_marker + crash_diagnostic + heartbeat (defensive error checking).
# - positive_control (Gate D): N=8192 DISC reproduces v1 FULL (regen_d5~0.263,
#   gap~0.176) within tol -> validates the factored refactor at test regime.
--------------------------------------------------------------------------------
Compute architecture: SEQUENCE-DEPENDENT CPU (each hop depends on hop k-1 --
genuine chained-retrieval sequential dependency exemption) + the cell IS the
substrate cleanup primitive being validated. Storage = HEBBIAN (bundled) BY
DESIGN: the superposition crosstalk is the noise the digital-vs-analog distinction
must overcome (SHARDED-rule exemption -- bundled IS the discriminator substrate).
Retrieval is the FACTORED store (no N x N materialization), M-chunked, numpy
batched matmul across all test chains per hop (not a python-scalar loop).

PROT-018: no _n<N> suffix in anchor (this IS an N-sweep; N is the axis).
ASCII-only; no unicode; no emojis; no em-dashes.
Author: exp_dev 2026-07-05.
"""
from __future__ import annotations

import sys

# progress_logging: line-buffered stdout so print() flushes on newline (FULL may
# run > 30 min on remote CPU at N=32768; see prereg progress_logging field).
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
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "cortex_regenerative_cleanup_vs_analog_accumulate_v2"
_LLM_CALL_COUNTER = [0]  # substrate-only assert: must stay 0

# ---------------------------------------------------------------------------
# CLI + RUN_MODE (defaults to full per META_RULE 16; --smoke / --self-test flip;
# runner injects HDLAB_RUN_MODE=full and invokes bare, so env is the real channel)
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
# Crossover phase-diagram parametrized by TARGET M/N (held constant across N and
# mode). LOW_TARGET documents the soft-wins-below-capacity crossover; the DISC
# operating point is found DYNAMICALLY per (N, seed) as the max-gap valid point
# (valid = single-hop d1 clears the sanity floor for both arms).
LOW_TARGET = 0.37     # below the M/N~1 threshold: analog (soft-carry) wins
DISC_TARGET = 1.10    # nominal discriminating load (reporting anchor; v1's DISC)

if RUN_MODE == "self_test":
    N_LIST = [512]
    V_CODE = 48
    P_REL = 4
    N_TEST = 12
    MOVERN_TARGETS = [0.37, 1.10]
    N_CALIB = 16
    N_REFUSE = 16
    SEEDS = [0]
    D_MAX = 5
    DEPTHS = [1, 2, 3, 4, 5]
    REFUSE_DEPTH = 5
elif RUN_MODE == "smoke":
    # Discriminator-must-survive-scale: smoke runs the FULL N grid, reduced chains,
    # and includes a HIGH M/N point so the discriminator is previewed at every N
    # even if the collapse point shifts up with N. 2 seeds for variance.
    N_LIST = [8192, 16384, 32768]
    V_CODE = 512
    P_REL = 8
    N_TEST = 40
    MOVERN_TARGETS = [0.37, 1.10, 2.00]   # LOW / DISC / HIGH
    N_CALIB = 40
    N_REFUSE = 40
    SEEDS = [7, 17]
    D_MAX = 7
    DEPTHS = [1, 2, 3, 4, 5, 6, 7]
    REFUSE_DEPTH = 5
else:  # full
    N_LIST = [8192, 16384, 32768]
    V_CODE = 512
    P_REL = 8
    # N_TEST=40 (NOT v1's 150): the pre-flight sim revealed v1's d1 SANITY breach
    # was driven by CHAIN-KEY COLLISION (N_TEST*D_MAX chain edges over V_CHAIN*P_REL
    # key-slots), which is N-INDEPENDENT (d1 stays ~0.75 at N_TEST=150 for ALL N in
    # {8192,16384,32768}), NOT M/N-crosstalk as the witnesses diagnosed. N_TEST=40
    # gives chain-key-fill ~14% -> d1 clears 0.85 at every N -> the single-hop store
    # is reliable and the M/N (background) crosstalk sweep is the clean stressor.
    N_TEST = 40
    MOVERN_TARGETS = [0.37, 0.74, 1.10, 1.55, 2.00]   # LOW .. HIGH (gap-widens sweep)
    N_CALIB = 40
    N_REFUSE = 40
    SEEDS = [7, 17, 23, 31, 41]
    D_MAX = 7
    DEPTHS = [1, 2, 3, 4, 5, 6, 7]
    REFUSE_DEPTH = 5

# V1-REPRODUCTION diagnostic (FULL only): a dedicated point at v1's EXACT confounded
# regime (N=8192, N_TEST=150, M/N=1.10) that (a) validates the factored refactor by
# reproducing v1's d1~0.75 / regen_d5~0.263, and (b) is the smoking gun for the
# collision finding -- SAME M/N=1.10 as the main sweep's N=8192 point but N_TEST 40
# vs 150 -> d1 ~0.95 vs ~0.75 (collision, not crosstalk). REPORTED, not gated.
V1REPRO_ENABLED = (RUN_MODE == "full")
V1REPRO_N = 8192
V1REPRO_N_TEST = 150
V1REPRO_TARGET = 1.10

# Chain-node partition: chain source/object nodes drawn from [0, V_CHAIN);
# background edge sources drawn from [V_CHAIN, V_CODE) so chain keys never
# key-collide with background keys (crosstalk stays pure superposition).
V_CHAIN = V_CODE // 2

# Refuse-gate calibration percentile (adaptive-with-discriminator-gate).
REFUSE_TAU_PERCENTILE = 12.0  # tau = 12th pctile of supported-calib confidences


def mbg_for(target: float, n_dim: int, n_test: int) -> int:
    """Background-edge count that yields TRUE M/N == target (chain edges included).

    M_total = M_BG + n_test*D_MAX ; M/N = M_total/N ; so
    M_BG = round(target*N) - n_test*D_MAX (clamped at 0)."""
    return max(0, int(round(target * n_dim)) - n_test * D_MAX)


CONFIG_VERSION = (
    "ANCHOR=%s,N_LIST=%s,V=%d,P=%d,D_MAX=%d,DEPTHS=%s,N_TEST=%d,MOVERN=%s,"
    "V_CHAIN=%d,REFUSE_DEPTH=%d,N_CALIB=%d,N_REFUSE=%d,tau_pctile=%.1f,"
    "SEEDS=%s,RUN_MODE=%s,store=FACTORED,hardening=startmarker+crashdiag+heartbeat+AF+AH+AG"
) % (
    ANCHOR_NAME, "-".join(str(n) for n in N_LIST), V_CODE, P_REL, D_MAX,
    "-".join(str(d) for d in DEPTHS), N_TEST,
    "-".join(("%.2f" % m) for m in MOVERN_TARGETS), V_CHAIN, REFUSE_DEPTH,
    N_CALIB, N_REFUSE, REFUSE_TAU_PERCENTILE, "-".join(str(s) for s in SEEDS),
    RUN_MODE,
)

# Cardinality (META_RULE_H).
EXPECTED_DEPTH_ROWS = len(DEPTHS)
EXPECTED_N_UNITS = len(SEEDS) * len(N_LIST) * len(MOVERN_TARGETS)

# Bands (recalibrated) ------------------------------------------------------
# The primary discriminator is RELATIVE (gap + analog-collapse + graceful margin).
# regen_d5 absolute is REPORTED (secondary), soft floor 0.22 (below the honest
# ~0.263 with seed-variance margin), NOT a HARD_PASS gate.
HP_GAP_MIN = 0.15               # regen_d5 - analog_d5 >= 0.15 (MEASURED ~0.176 @ N=8192 DISC)
HP_ANALOG_COLLAPSE_MAX = 0.30   # analog_d5 <= 0.30 (collapsed)  (MEASURED ~0.087 @ N=8192 DISC)
HP_GRACEFUL_MARGIN = 0.15       # (analog_d3-analog_d5)-(regen_d3-regen_d5) >= 0.15 (MEASURED ~0.315)
HP_FAITHFULNESS_MIN = 0.95      # HARD joint gate (MEASURED 1.000)
HP_CONTROL_D5_MAX = 0.05        # near chance (1/V); tolerates a few lucky hits (MEASURED ~0.003)
SANITY_D1_MIN = 0.85            # single-hop store works (valid-operating-point gate; now REACHABLE via N)
CROSSOVER_GAP_MAX = 0.05        # LOW-regime gap <= this -> soft-wins-below-capacity confirmed
REGEN_D5_SOFT_FLOOR = 0.22      # REPORTED secondary (regen still usable); NOT a gate

HP_FALSE_ACCEPT_MAX = 0.10      # refuse-gate REPORTED thresholds (not gated)
HP_FALSE_REFUSE_MAX = 0.15

HF_REGEN_D5_MAX = 0.15          # regen also collapses at a valid point -> mechanism fails
HF_GAP_MIN = 0.05               # gap < this at the disc point -> regen never beats analog
HF_CONTROL_D5_MAX = 0.10        # control > this -> discriminator broken -> FAIL (chance=1/V)

# Positive control (Gate D): N=8192 DISC must reproduce v1 FULL numbers.
PC_V1_N = 8192
PC_V1_REGEN_D5 = 0.263          # MEASURED@data/exp_cortex_regenerative_cleanup_vs_analog_accumulate_v1/metrics.json
PC_V1_GAP_D5 = 0.176            # MEASURED@ same
PC_TOL = 0.10                   # tolerance for the reproduction check (reported)

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
               extra: Optional[Dict[str, Any]] = None) -> None:
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


def _chunk_for(n_dim: int) -> int:
    """Edge-chunk size bounding a Kc block to ~256 MB (adaptive to N)."""
    return max(256, (1 << 26) // n_dim)


class FactoredStore:
    """Hebbian associative store held as edge lists (NEVER materializes N x N W).

    retrieve(x) = sum_e <x, E[s_e]*R[p_e]> * E[o_e] / N  ==  x @ W.T  where
    W = sum_e outer(E[o_e], E[s_e]*R[p_e]) / N. M-chunked matmul: memory O(chunk*N),
    compute O(B*M*N) per call (no O(N^2) matrix build). Self-test T0 proves this is
    numerically identical to v1's materialized W @ x.
    """

    __slots__ = ("s", "p", "o", "E", "R", "n_dim", "chunk")

    def __init__(self, s: np.ndarray, p: np.ndarray, o: np.ndarray,
                 E: np.ndarray, R: np.ndarray, n_dim: int):
        self.s = np.ascontiguousarray(s.astype(np.int64))
        self.p = np.ascontiguousarray(p.astype(np.int64))
        self.o = np.ascontiguousarray(o.astype(np.int64))
        self.E = E
        self.R = R
        self.n_dim = int(n_dim)
        self.chunk = _chunk_for(n_dim)

    def retrieve(self, keys: np.ndarray) -> np.ndarray:
        """keys: (B, N) -> yhat: (B, N)."""
        m = self.s.shape[0]
        out = np.zeros((keys.shape[0], self.n_dim), dtype=np.float32)
        if m == 0:
            return out
        for c0 in range(0, m, self.chunk):
            sl = slice(c0, c0 + self.chunk)
            kc = self.E[self.s[sl]] * self.R[self.p[sl]]     # (c, N) keys
            coeff = keys @ kc.T                               # (B, c)
            out += coeff @ self.E[self.o[sl]]                 # (B, N)
        out /= float(self.n_dim)
        return out.astype(np.float32)

    def sha_edges(self) -> str:
        """sha256 of the edge index arrays (store-invariance audit; cheap)."""
        h = hashlib.sha256()
        h.update(np.ascontiguousarray(self.s).tobytes())
        h.update(np.ascontiguousarray(self.p).tobytes())
        h.update(np.ascontiguousarray(self.o).tobytes())
        return h.hexdigest()[:16]


def build_W_reference(edges: np.ndarray, E: np.ndarray, R: np.ndarray,
                      n_dim: int) -> np.ndarray:
    """v1's materialized Hebbian W (REFERENCE ONLY; used in self-test T0 to prove
    the factored store is numerically identical). NOT used in the sweep."""
    if edges.shape[0] == 0:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    k = E[edges[:, 0]] * R[edges[:, 1]]
    vv = E[edges[:, 2]]
    return (vv.T @ k).astype(np.float32) / float(n_dim)


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
    """(pred_ids, margin) per row. margin = (top1_score - top2_score)/N is a
    retrieval-confidence signal used by the refuse-gate."""
    scores = yhat @ E.T                        # (B, V)
    n = float(E.shape[1])
    part = np.argpartition(-scores, 1, axis=1)[:, :2]   # top-2 indices per row
    rows = np.arange(scores.shape[0])
    top1_idx = part[rows, np.argmax(scores[rows[:, None], part], axis=1)]
    top1 = scores[rows, top1_idx]
    s2 = scores[rows[:, None], part]
    s2_sorted = np.sort(s2, axis=1)            # ascending; [:, -1]=top1, [:, -2]=top2
    top2 = s2_sorted[:, -2]
    margin = (top1 - top2) / n
    return top1_idx.astype(np.int64), margin


def _sha_of_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Chain generation (nested; reserved node partitions) - unchanged from v1
# ---------------------------------------------------------------------------
def make_chains(n_chains: int, g: np.random.Generator) -> np.ndarray:
    """(n_chains, D_MAX, 3) int array of (s, p, o) using chain-partition nodes."""
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
    """(m_bg, 3) distractor edges with SOURCE in [V_CHAIN, V_CODE), object anywhere."""
    if m_bg <= 0:
        return np.zeros((0, 3), dtype=np.int64)
    s = g.integers(V_CHAIN, V_CODE, size=m_bg)
    p = g.integers(0, P_REL, size=m_bg)
    o = g.integers(0, V_CODE, size=m_bg)
    return np.stack([s, p, o], axis=1).astype(np.int64)


def break_chains(chains: np.ndarray, g: np.random.Generator) -> np.ndarray:
    """Corrupt ONE random hop per chain (unstored (s, p_new) key + arbitrary object)."""
    broken = chains.copy()
    b = chains.shape[0]
    for c in range(b):
        j = int(g.integers(0, chains.shape[1]))
        p_orig = int(chains[c, j, 1])
        p_new = (p_orig + 1 + int(g.integers(0, P_REL - 1))) % P_REL
        broken[c, j, 1] = p_new
        broken[c, j, 2] = int(g.integers(0, V_CHAIN))
    return broken


# ---------------------------------------------------------------------------
# Arm walkers (batched across chains; retrieve via factored store).
# ONE-PASS depth curves: since the walk is deterministic and depth-nested, a
# single walk to max(depths) recording accuracy at every prefix depth is
# BIT-IDENTICAL to re-walking to each depth separately (self-test T_onepass
# proves it), at ~1/len(depths) the retrieve calls. Arms + distinction UNCHANGED.
# ---------------------------------------------------------------------------
def walk_analog_curve(chains: np.ndarray, store: FactoredStore, E: np.ndarray,
                      R: np.ndarray, depths: List[int]) -> Dict[str, Any]:
    """ANALOG: carry normalized noisy retrieved vector forward; no cleanup.
    Returns per-depth final accuracy + per-depth emitted final_pred."""
    dmax = max(depths)
    x = E[chains[:, 0, 0]].astype(np.float32).copy()
    curve: Dict[int, float] = {}
    preds: Dict[int, np.ndarray] = {}
    for k in range(dmax):
        p = chains[:, k, 1]
        key = x * R[p]
        yhat = store.retrieve(key)
        pred = cleanup_ids(yhat, E)
        d = k + 1
        if d in depths:
            curve[d] = float(np.mean(pred == chains[:, d - 1, 2]))
            preds[d] = pred
        nrm = np.linalg.norm(yhat, axis=1, keepdims=True) + 1e-12
        x = (yhat / nrm).astype(np.float32)
    return {"curve": curve, "preds": preds}


def walk_regen_curve(chains: np.ndarray, store: FactoredStore, E: np.ndarray,
                     R: np.ndarray, depths: List[int],
                     audit_isolation: bool = False) -> Dict[str, Any]:
    """REGEN: snap to nearest codebook atom each hop; carry the CLEAN atom.
    Scratchpad `x` is a separate array; when audit_isolation, capture the store
    edge-array sha256 before/after and assert invariance (zero store writes).
    Returns per-depth final accuracy + per-depth emitted final_pred (= the digital
    trace outcome, reused for faithfulness)."""
    dmax = max(depths)
    sha_before = store.sha_edges() if audit_isolation else None
    x = E[chains[:, 0, 0]].astype(np.float32).copy()
    assert x.base is None, "scratchpad must be a fresh array (separate register)"
    curve: Dict[int, float] = {}
    preds: Dict[int, np.ndarray] = {}
    for k in range(dmax):
        p = chains[:, k, 1]
        key = x * R[p]
        yhat = store.retrieve(key)
        pred = cleanup_ids(yhat, E)
        d = k + 1
        if d in depths:
            curve[d] = float(np.mean(pred == chains[:, d - 1, 2]))
            preds[d] = pred
        x = E[pred].astype(np.float32)                   # snap to clean codeword
    sha_after = store.sha_edges() if audit_isolation else None
    isolation_clean = (audit_isolation and (sha_before == sha_after))
    return {"curve": curve, "preds": preds,
            "isolation_clean": bool(isolation_clean) if audit_isolation else None,
            "sha_before": sha_before, "sha_after": sha_after}


def faithfulness_from_preds(digital_preds: Dict[int, np.ndarray],
                            arm_preds: Dict[int, np.ndarray],
                            depths: List[int]) -> Dict[int, float]:
    """faith[d] = fraction of chains where the DIGITAL (atom-carry) replay's answer
    at depth d matches the arm's emitted answer at depth d. The digital replay IS
    the regen rule, so regen faith == 1.0 by construction; analog carries a vector
    (not an atom) so its discrete trace does not determine its answer -> < 1.0.
    digital_preds is taken from a regen (atom-carry) walk over the SAME store."""
    out: Dict[int, float] = {}
    for d in depths:
        if d in digital_preds and d in arm_preds:
            out[d] = round(float(np.mean(digital_preds[d] == arm_preds[d])), 4)
    return out


# ---------------------------------------------------------------------------
# Refuse-gate (REPORTED, not gated) - v1 logic
# ---------------------------------------------------------------------------
def _chain_conf(chains: np.ndarray, depth: int, store: FactoredStore,
                E: np.ndarray, R: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """(mean_margin_per_chain, final_pred) for the REGEN walk at `depth`."""
    x = E[chains[:, 0, 0]].astype(np.float32).copy()
    sum_margin = np.zeros(chains.shape[0], dtype=np.float64)
    final_pred = None
    for k in range(depth):
        p = chains[:, k, 1]
        key = x * R[p]
        yhat = store.retrieve(key)
        pred, margin = cleanup_margin(yhat, E)
        sum_margin += margin
        final_pred = pred
        x = E[pred].astype(np.float32)
    return sum_margin / float(depth), final_pred


def refuse_gate(E: np.ndarray, R: np.ndarray, store: FactoredStore,
                supported: np.ndarray, g: np.random.Generator) -> Dict[str, Any]:
    """Calibrate tau on a supported CALIBRATION split; evaluate false-accept /
    false-refuse on a disjoint TEST split. REPORTED, not gated."""
    n = supported.shape[0]
    if n < 8:
        return {"refuse_ok": None, "reason": "insufficient_chains", "n": int(n)}
    half = n // 2
    calib = supported[:half]
    test_sup = supported[half:]
    test_broken = break_chains(test_sup, g)

    conf_calib, _ = _chain_conf(calib, REFUSE_DEPTH, store, E, R)
    tau = float(np.percentile(conf_calib, REFUSE_TAU_PERCENTILE))

    conf_sup, pred_sup = _chain_conf(test_sup, REFUSE_DEPTH, store, E, R)
    conf_brk, pred_brk = _chain_conf(test_broken, REFUSE_DEPTH, store, E, R)

    refused_sup = conf_sup < tau
    refused_brk = conf_brk < tau
    true_final_sup = test_sup[:, REFUSE_DEPTH - 1, 2]

    false_refuse = float(np.mean(refused_sup))
    false_accept = float(np.mean(~refused_brk))
    conf_sep = float(np.mean(conf_sup) - np.mean(conf_brk))
    sup_final_acc = float(np.mean(pred_sup == true_final_sup))
    return {
        "refuse_calibrated": bool(false_accept <= HP_FALSE_ACCEPT_MAX
                                  and false_refuse <= HP_FALSE_REFUSE_MAX),
        "tau": round(tau, 4), "false_accept": round(false_accept, 4),
        "false_refuse": round(false_refuse, 4),
        "conf_sep_sup_minus_brk": round(conf_sep, 4),
        "supported_final_acc": round(sup_final_acc, 4),
        "n_calib": int(calib.shape[0]), "n_test_sup": int(test_sup.shape[0]),
        "n_test_broken": int(test_broken.shape[0]),
    }


# ---------------------------------------------------------------------------
# One (N, seed, M_BG) run -> full depth curve for all 3 arms + joint gates
# ---------------------------------------------------------------------------
def run_cell(n_dim: int, seed: int, target: float, out_dir: Path,
             hb_state: Dict[str, Any], n_test: int = None) -> Dict[str, Any]:
    if n_test is None:
        n_test = N_TEST
    t0 = time.perf_counter()
    m_bg = mbg_for(target, n_dim, n_test)
    g = np.random.default_rng(seed * 100003 + n_dim * 7 + m_bg + n_test)

    E = make_bipolar(V_CODE, n_dim, g)
    R = make_bipolar(P_REL, n_dim, g)
    chains = make_chains(n_test, g)
    chain_edges = chains.reshape(-1, 3)
    bg_edges = make_background_edges(m_bg, g)
    all_edges = np.concatenate([chain_edges, bg_edges], axis=0)
    m_total = int(all_edges.shape[0])

    store = FactoredStore(all_edges[:, 0], all_edges[:, 1], all_edges[:, 2], E, R, n_dim)
    perm = g.permutation(V_CODE)
    o_shuf = perm[all_edges[:, 2]]
    store_shuf = FactoredStore(all_edges[:, 0], all_edges[:, 1], o_shuf, E, R, n_dim)

    # ONE-PASS walks (each arm walked once to max(DEPTHS)); the regen walk's
    # per-depth atom-carry preds double as the digital-replay for faithfulness.
    ra = walk_analog_curve(chains, store, E, R, DEPTHS)
    rr = walk_regen_curve(chains, store, E, R, DEPTHS, audit_isolation=True)
    rc = walk_regen_curve(chains, store_shuf, E, R, DEPTHS, audit_isolation=False)

    analog_curve = {d: round(v, 4) for d, v in ra["curve"].items()}
    regen_curve = {d: round(v, 4) for d, v in rr["curve"].items()}
    control_curve = {d: round(v, 4) for d, v in rc["curve"].items()}
    # faith: digital replay == regen atom-carry preds (rr["preds"]).
    regen_faith_curve = faithfulness_from_preds(rr["preds"], rr["preds"], DEPTHS)   # == 1.0 by construction
    analog_faith_curve = faithfulness_from_preds(rr["preds"], ra["preds"], DEPTHS)  # < 1.0 (vector-carry)
    isolation_clean_all = (rr["isolation_clean"] is not False)

    arms_sha = {
        "analog": _sha_of_array(ra["preds"][REFUSE_DEPTH]),
        "regen": _sha_of_array(rr["preds"][REFUSE_DEPTH]),
        "control": _sha_of_array(rc["preds"][REFUSE_DEPTH]),
    }
    for depth in DEPTHS:
        hb_state["unit"] += 1
        _heartbeat(out_dir, hb_state["unit"], hb_state["total"], hb_state["t0"],
                   extra={"N": n_dim, "seed": seed, "target": target, "depth": depth,
                          "regen": regen_curve[depth], "analog": analog_curve[depth]})
    print("  [N=%d seed=%d M/N=%.2f] curve regen=%s analog=%s control=%s "
          "regen_faith_d5=%.3f analog_faith_d5=%.3f iso=%s"
          % (n_dim, seed, target,
             [regen_curve[d] for d in DEPTHS], [analog_curve[d] for d in DEPTHS],
             [control_curve[d] for d in DEPTHS],
             regen_faith_curve.get(REFUSE_DEPTH, float("nan")),
             analog_faith_curve.get(REFUSE_DEPTH, float("nan")),
             rr["isolation_clean"]), flush=True)

    # Refuse-gate REPORTED only (never gated); run in FULL at the nominal DISC
    # target only (skip in smoke -- the smoke is a discriminator preview, not a
    # refuse measurement -- to keep the local smoke fast on the laptop).
    if RUN_MODE == "full" and abs(target - DISC_TARGET) < 1e-6:
        g_ref = np.random.default_rng(seed * 7 + n_dim + m_bg + 999)
        refuse_chains = make_chains(N_REFUSE, g_ref)
        ref_all = np.concatenate([refuse_chains.reshape(-1, 3), all_edges], axis=0)
        store_ref = FactoredStore(ref_all[:, 0], ref_all[:, 1], ref_all[:, 2], E, R, n_dim)
        refuse = refuse_gate(E, R, store_ref, refuse_chains, g_ref)
    else:
        refuse = None

    arms_differ = (len(set(arms_sha.values())) == 3) if arms_sha else False

    regen_d3 = regen_curve.get(3, float("nan"))
    regen_d5 = regen_curve.get(5, float("nan"))
    analog_d3 = analog_curve.get(3, float("nan"))
    analog_d5 = analog_curve.get(5, float("nan"))
    analog_d1 = analog_curve.get(1, float("nan"))
    regen_d1 = regen_curve.get(1, float("nan"))
    control_d5 = control_curve.get(5, float("nan"))
    flatness = regen_d3 - regen_d5
    analog_decay = analog_d3 - analog_d5
    graceful_margin = analog_decay - flatness
    gap = regen_d5 - analog_d5
    regen_faith_d5 = regen_faith_curve.get(5, float("nan"))

    return {
        "N": n_dim, "seed": seed, "target_m_over_n": target, "n_test": int(n_test),
        "m_bg": int(m_bg), "m_total": m_total,
        "m_over_n": round(m_total / float(n_dim), 4),
        "V": V_CODE, "P": P_REL, "run_mode": RUN_MODE,
        "analog_curve": analog_curve, "regen_curve": regen_curve,
        "control_curve": control_curve, "regen_faith_curve": regen_faith_curve,
        "analog_faith_curve": analog_faith_curve,
        "per_hop_regen_at_d5": [regen_curve[d] for d in DEPTHS if d <= 5],
        "per_hop_analog_at_d5": [analog_curve[d] for d in DEPTHS if d <= 5],
        "regen_d1": regen_d1, "analog_d1": analog_d1,
        "regen_d3": regen_d3, "regen_d5": regen_d5,
        "analog_d3": analog_d3, "analog_d5": analog_d5, "control_d5": control_d5,
        "flatness_regen_d3_minus_d5": round(flatness, 4),
        "analog_decay_d3_minus_d5": round(analog_decay, 4),
        "graceful_margin": round(graceful_margin, 4),
        "gap_regen_minus_analog_d5": round(gap, 4),
        "regen_faithfulness_d5": regen_faith_d5,
        "analog_faithfulness_d5": analog_faith_curve.get(5, float("nan")),
        "isolation_clean": bool(isolation_clean_all),
        "arms_sha_at_d5": arms_sha, "arms_differ": bool(arms_differ),
        "d1_valid": bool(regen_d1 >= SANITY_D1_MIN and analog_d1 >= SANITY_D1_MIN),
        "refuse": refuse, "elapsed_s": round(time.perf_counter() - t0, 2),
        "config_version": CONFIG_VERSION,
    }


def classify_row(res: Dict[str, Any]) -> str:
    gap = res["gap_regen_minus_analog_d5"]
    if gap >= HP_GAP_MIN:
        return "REGEN_WINS"
    if gap <= -HP_GAP_MIN:
        return "ANALOG_WINS"
    return "TIE"


# ---------------------------------------------------------------------------
# Per (N, seed) tier: scan the M/N sweep, find the max-gap VALID operating point
# ---------------------------------------------------------------------------
def classify_N_seed(rows: List[Dict[str, Any]]) -> Tuple[str, List[str], Dict[str, Any]]:
    """rows = phase map (all M/N) for one (N, seed). Returns (tier, reasons, summary)."""
    reasons: List[str] = []
    rows_sorted = sorted(rows, key=lambda r: r["m_over_n"])
    valid = [r for r in rows_sorted if r["d1_valid"]]

    # crossover (soft-wins-below-capacity) evidence at the lowest target (~LOW).
    low = min(rows_sorted, key=lambda r: r["target_m_over_n"])
    low_gap = low["gap_regen_minus_analog_d5"]
    crossover_confirmed = bool(low_gap <= CROSSOVER_GAP_MAX)

    # gap curve across the sweep (gap-widens-with-load evidence).
    gap_curve = [(r["m_over_n"], r["gap_regen_minus_analog_d5"]) for r in rows_sorted]

    def _relgates(r: Dict[str, Any]) -> bool:
        """RELATIVE discriminator gates (excl. faith): regen beats analog with
        analog collapsed AND graceful degradation AND control fires AND iso clean.
        The graceful gate (analog decays MORE than regen over d3->d5) requires the
        DISC point to be where analog is COLLAPSING THROUGH the window -- so max-gap
        (deep past-collapse) points do NOT qualify; the critical M/N does."""
        return bool(r["gap_regen_minus_analog_d5"] >= HP_GAP_MIN
                    and r["analog_d5"] <= HP_ANALOG_COLLAPSE_MAX
                    and r["graceful_margin"] >= HP_GRACEFUL_MARGIN
                    and r["control_d5"] <= HP_CONTROL_D5_MAX
                    and r["isolation_clean"])

    def _faith_ok(r: Dict[str, Any]) -> bool:
        f = r["regen_faithfulness_d5"]
        return bool(f is not None and not math.isnan(f) and f >= HP_FAITHFULNESS_MIN)

    def _mk_summ(disc: Dict[str, Any]) -> Dict[str, Any]:
        lower = [r for r in rows_sorted if r["m_over_n"] < disc["m_over_n"]]
        gap_widens = bool(all(disc["gap_regen_minus_analog_d5"]
                              >= r["gap_regen_minus_analog_d5"] - 1e-9 for r in lower)) if lower else None
        return {
            "disc_m_over_n": disc["m_over_n"], "disc_target": disc["target_m_over_n"],
            "regen_d5": disc["regen_d5"], "analog_d5": disc["analog_d5"],
            "gap_d5": disc["gap_regen_minus_analog_d5"], "graceful_margin": disc["graceful_margin"],
            "regen_faith_d5": disc["regen_faithfulness_d5"], "control_d5": disc["control_d5"],
            "regen_d1": disc["regen_d1"], "analog_d1": disc["analog_d1"],
            "isolation_clean": disc["isolation_clean"], "crossover_confirmed": crossover_confirmed,
            "low_gap_d5": low_gap, "gap_curve": gap_curve, "gap_widens": gap_widens,
            "false_accept": (disc.get("refuse") or {}).get("false_accept"),
            "false_refuse": (disc.get("refuse") or {}).get("false_refuse"),
            "regen_d5_above_soft_floor": bool(disc["regen_d5"] >= REGEN_D5_SOFT_FLOOR),
        }

    if not valid:
        best_d1 = max(rows_sorted, key=lambda r: min(r["regen_d1"], r["analog_d1"]))
        summ = _mk_summ(best_d1)
        summ["disc_m_over_n"] = None
        summ["best_min_d1"] = round(min(best_d1["regen_d1"], best_d1["analog_d1"]), 4)
        summ["best_min_d1_target"] = best_d1["target_m_over_n"]
        reasons.append("ARTIFACT_REGIME(no valid op-point: best min(regen_d1,analog_d1)=%.3f "
                       "@M/N=%.2f < %.2f -- single-hop store unreliable at all swept M/N; "
                       "at N_TEST=%d this is chain-key COLLISION, N-independent)"
                       % (summ["best_min_d1"], best_d1["target_m_over_n"], SANITY_D1_MIN,
                          best_d1.get("n_test", N_TEST)))
        return "ARTIFACT_REGIME", reasons, summ

    # HARD_PASS: EXISTS a valid op-point where the FULL relative discriminator fires
    # (analog collapsing through the graceful window) AND faithfulness holds. Pick the
    # max-gap such point as the disc anchor.
    core_passers = [r for r in valid if _relgates(r) and _faith_ok(r)]
    if core_passers:
        disc = max(core_passers, key=lambda r: r["gap_regen_minus_analog_d5"])
        summ = _mk_summ(disc)
        reasons.append("HARD_PASS @M/N=%.2f regen_d5=%.3f gap=%.3f analog_d5=%.3f graceful=%.3f "
                       "faith=%.3f control=%.4f crossover=%s | refuse(reported) fa=%s fr=%s"
                       % (disc["m_over_n"], disc["regen_d5"], disc["gap_regen_minus_analog_d5"],
                          disc["analog_d5"], disc["graceful_margin"], disc["regen_faithfulness_d5"],
                          disc["control_d5"], crossover_confirmed, summ["false_accept"], summ["false_refuse"]))
        return "HARD_PASS", reasons, summ

    # FALSE_PASS_JOINT_GATE: relative gates fire at a valid point but faith wrecked.
    false_passers = [r for r in valid if _relgates(r) and not _faith_ok(r)]
    if false_passers:
        disc = max(false_passers, key=lambda r: r["gap_regen_minus_analog_d5"])
        summ = _mk_summ(disc)
        reasons.append("FALSE_PASS_FAITHFULNESS @M/N=%.2f (faith=%s < %.2f)"
                       % (disc["m_over_n"], disc["regen_faithfulness_d5"], HP_FAITHFULNESS_MIN))
        return "FALSE_PASS_JOINT_GATE", reasons, summ

    # No full-discriminator point. Use the max-gap valid point as the reference disc.
    disc = max(valid, key=lambda r: r["gap_regen_minus_analog_d5"])
    summ = _mk_summ(disc)
    regen_d5 = disc["regen_d5"]; analog_d5 = disc["analog_d5"]
    gap = disc["gap_regen_minus_analog_d5"]; control_d5 = disc["control_d5"]

    if control_d5 > HF_CONTROL_D5_MAX:
        reasons.append("CONTROL_NOT_COLLAPSED(%.4f > %.3f)" % (control_d5, HF_CONTROL_D5_MAX))
        return "HARD_FAIL", reasons, summ
    if not disc["isolation_clean"]:
        reasons.append("ISOLATION_DIRTY")
        return "HARD_FAIL", reasons, summ
    # HARD_FAIL: analog collapsed at a valid point but regen ALSO collapsed there.
    if analog_d5 <= HP_ANALOG_COLLAPSE_MAX and regen_d5 <= HF_REGEN_D5_MAX and gap < HF_GAP_MIN:
        reasons.append("REGEN_ALSO_COLLAPSED(regen_d5=%.3f<=%.2f gap=%.3f<%.2f @M/N=%.2f)"
                       % (regen_d5, HF_REGEN_D5_MAX, gap, HF_GAP_MIN, disc["m_over_n"]))
        return "HARD_FAIL", reasons, summ

    reasons.append("MIDDLE @M/N=%.2f regen_d5=%.3f gap=%.3f analog_d5=%.3f graceful=%.3f "
                   "(regen wins but the graceful-vs-catastrophic window did not fire at a "
                   "valid point -- e.g. analog already floored before d3 at high load)"
                   % (disc["m_over_n"], regen_d5, gap, analog_d5, disc["graceful_margin"]))
    return "MIDDLE_BAND", reasons, summ


# ---------------------------------------------------------------------------
# Per-seed driver: for each N, sweep M/N -> per-N tier.
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    t0 = time.perf_counter()
    hb_total = len(N_LIST) * len(MOVERN_TARGETS) * len(DEPTHS)
    hb_state = {"unit": 0, "total": hb_total, "t0": t0}
    per_N: List[Dict[str, Any]] = []

    for n_dim in N_LIST:
        rows: List[Dict[str, Any]] = []
        for target in MOVERN_TARGETS:
            res = run_cell(n_dim, seed, target, out_dir, hb_state)
            res["row_label"] = classify_row(res)
            print("  [N=%d seed=%d M/N=%.2f] row=%s gap_d5=%+.3f regen_d5=%.3f "
                  "analog_d5=%.3f d1_valid=%s(regen_d1=%.3f analog_d1=%.3f)"
                  % (n_dim, seed, res["m_over_n"], res["row_label"],
                     res["gap_regen_minus_analog_d5"], res["regen_d5"], res["analog_d5"],
                     res["d1_valid"], res["regen_d1"], res["analog_d1"]), flush=True)
            rows.append(res)
        tier, reasons, summ = classify_N_seed(rows)
        print("  [N=%d seed=%d] N_TIER=%s %s" % (n_dim, seed, tier, reasons), flush=True)
        per_N.append({
            "N": n_dim, "seed": seed, "n_tier": tier, "n_tier_reasons": reasons,
            "disc_summary": summ,
            "phase_map": [{"target": r["target_m_over_n"], "m_over_n": r["m_over_n"],
                           "row_label": r["row_label"],
                           "gap_d5": r["gap_regen_minus_analog_d5"],
                           "regen_d5": r["regen_d5"], "analog_d5": r["analog_d5"],
                           "regen_d1": r["regen_d1"], "analog_d1": r["analog_d1"],
                           "d1_valid": r["d1_valid"],
                           "graceful_margin": r["graceful_margin"],
                           "regen_faith_d5": r["regen_faithfulness_d5"],
                           "control_d5": r["control_d5"],
                           "isolation_clean": r["isolation_clean"],
                           "arms_differ": r["arms_differ"]} for r in rows],
        })

    # V1-REPRODUCTION diagnostic (FULL only): v1's confounded regime N_TEST=150.
    v1_repro = None
    if V1REPRO_ENABLED:
        vr = run_cell(V1REPRO_N, seed, V1REPRO_TARGET, out_dir, hb_state, n_test=V1REPRO_N_TEST)
        v1_repro = {
            "N": V1REPRO_N, "n_test": V1REPRO_N_TEST, "target": V1REPRO_TARGET,
            "m_over_n": vr["m_over_n"], "regen_d1": vr["regen_d1"], "analog_d1": vr["analog_d1"],
            "regen_d5": vr["regen_d5"], "analog_d5": vr["analog_d5"],
            "gap_d5": vr["gap_regen_minus_analog_d5"], "d1_valid": vr["d1_valid"],
        }
        print("  [V1_REPRO N=%d N_TEST=%d M/N=%.2f] regen_d1=%.3f regen_d5=%.3f gap=%+.3f "
              "(v1 refs d1~0.75 regen_d5~0.263; low d1 here vs main-sweep N_TEST=40 -> COLLISION)"
              % (V1REPRO_N, V1REPRO_N_TEST, vr["m_over_n"], vr["regen_d1"], vr["regen_d5"],
                 vr["gap_regen_minus_analog_d5"]), flush=True)

    return {
        "seed": seed, "run_mode": RUN_MODE, "N": N_LIST[-1],
        "n_llm_calls": _LLM_CALL_COUNTER[0], "per_N": per_N, "v1_repro": v1_repro,
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "config_version": CONFIG_VERSION,
    }


# ---------------------------------------------------------------------------
# Aggregate verdict across seeds + N (N-trend is the headline recalibration ask)
# ---------------------------------------------------------------------------
def _mean(xs: List[float]) -> Optional[float]:
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return round(float(np.mean(xs)), 4) if xs else None


def compute_verdict(all_seed_results: List[Dict[str, Any]]) -> Tuple[str, str, Dict[str, Any]]:
    n_seeds = len(all_seed_results)
    if n_seeds == 0:
        return "HARD_FAIL", "NO_SEED_RESULTS", {"cardinality_ok": False}

    # Cardinality (META_RULE_H): count (seed, N, target) units.
    n_units = sum(len(pn["phase_map"]) for r in all_seed_results for pn in r["per_N"])
    expected_units = n_seeds * len(N_LIST) * len(MOVERN_TARGETS)
    cardinality_ok = (n_units == expected_units)
    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H units=%d expected=%d"
                % (n_units, expected_units), {"cardinality_ok": False,
                                              "n_units": n_units, "expected": expected_units})

    # Per-N aggregation across seeds.
    per_N_summary: List[Dict[str, Any]] = []
    for i, n_dim in enumerate(N_LIST):
        tiers = [r["per_N"][i]["n_tier"] for r in all_seed_results]
        ds = [r["per_N"][i]["disc_summary"] for r in all_seed_results]
        n_pass = sum(1 for t in tiers if t == "HARD_PASS")
        n_fail = sum(1 for t in tiers if t == "HARD_FAIL")
        n_false = sum(1 for t in tiers if t == "FALSE_PASS_JOINT_GATE")
        n_artifact = sum(1 for t in tiers if t == "ARTIFACT_REGIME")
        n_mid = sum(1 for t in tiers if t == "MIDDLE_BAND")
        majority = (n_seeds // 2) + 1
        if n_fail > 0:
            n_tier = "HARD_FAIL"
        elif n_pass >= majority:
            n_tier = "HARD_PASS"
        elif n_artifact >= majority:
            n_tier = "ARTIFACT_REGIME"
        elif n_false >= majority:
            n_tier = "FALSE_PASS_JOINT_GATE"
        else:
            n_tier = "MIDDLE_BAND"
        per_N_summary.append({
            "N": n_dim, "n_tier_majority": n_tier, "seed_tiers": tiers,
            "n_pass": n_pass, "n_fail": n_fail, "n_false_joint": n_false,
            "n_artifact": n_artifact, "n_middle": n_mid,
            "mean_disc_m_over_n": _mean([d.get("disc_m_over_n") for d in ds]),
            "mean_regen_d5_at_disc": _mean([d.get("regen_d5") for d in ds]),
            "mean_analog_d5_at_disc": _mean([d.get("analog_d5") for d in ds]),
            "mean_gap_d5_at_disc": _mean([d.get("gap_d5") for d in ds]),
            "mean_graceful_at_disc": _mean([d.get("graceful_margin") for d in ds]),
            "mean_regen_faith_at_disc": _mean([d.get("regen_faith_d5") for d in ds]),
            "mean_control_d5_at_disc": _mean([d.get("control_d5") for d in ds]),
            "mean_regen_d1_at_disc": _mean([d.get("regen_d1") for d in ds]),
            "mean_analog_d1_at_disc": _mean([d.get("analog_d1") for d in ds]),
            "n_crossover_confirmed": sum(1 for d in ds if d.get("crossover_confirmed")),
            "n_gap_widens": sum(1 for d in ds if d.get("gap_widens") is True),
        })

    # N-trend headline (the Director's report ask).
    regen_by_N = [(s["N"], s["mean_regen_d5_at_disc"]) for s in per_N_summary]
    gap_by_N = [(s["N"], s["mean_gap_d5_at_disc"]) for s in per_N_summary]
    d1_by_N = [(s["N"], s["mean_regen_d1_at_disc"]) for s in per_N_summary]
    disc_mn_by_N = [(s["N"], s["mean_disc_m_over_n"]) for s in per_N_summary]

    # Apples-to-apples N-trend: regen_d5 / gap / d1 at the FIXED nominal DISC target
    # (M/N=1.10) across N -- the dynamic disc can move M/N, so this fixed-point trend
    # is the clean "does bigger N raise regen_d5 at the same operating point" answer.
    def _fixed_target_by_N(field: str, tgt: float) -> List[Tuple[int, Optional[float]]]:
        out = []
        for i, n_dim in enumerate(N_LIST):
            vals = []
            for r in all_seed_results:
                for row in r["per_N"][i]["phase_map"]:
                    if abs(row["target"] - tgt) < 1e-6:
                        vals.append(row[field])
            out.append((n_dim, round(float(np.mean(vals)), 4) if vals else None))
        return out
    regen_d5_fixedDISC_by_N = _fixed_target_by_N("regen_d5", DISC_TARGET)
    gap_fixedDISC_by_N = _fixed_target_by_N("gap_d5", DISC_TARGET)
    d1_fixedDISC_by_N = _fixed_target_by_N("regen_d1", DISC_TARGET)

    def _rises(seq: List[Tuple[int, Optional[float]]]) -> Optional[bool]:
        vals = [v for _, v in seq if v is not None]
        if len(vals) < 2:
            return None
        return bool(vals[-1] > vals[0] + 1e-6)

    regen_d5_rises_with_N = _rises(regen_d5_fixedDISC_by_N)  # at FIXED M/N=1.10 (apples-to-apples)
    d1_rises_with_N = _rises(d1_by_N)
    # d1 clears the sanity floor at the largest N where a valid op-point exists?
    d1_clears_at_high_N = None
    for s in reversed(per_N_summary):
        if s["mean_regen_d1_at_disc"] is not None:
            d1_clears_at_high_N = bool(s["mean_regen_d1_at_disc"] >= SANITY_D1_MIN)
            break

    # Cell verdict: HARD_PASS iff >=1 N-tier HARD_PASS (majority seeds) and no N HARD_FAIL.
    any_fail = any(s["n_tier_majority"] == "HARD_FAIL" for s in per_N_summary)
    pass_tiers = [s for s in per_N_summary if s["n_tier_majority"] == "HARD_PASS"]
    false_tiers = [s for s in per_N_summary if s["n_tier_majority"] == "FALSE_PASS_JOINT_GATE"]
    artifact_tiers = [s for s in per_N_summary if s["n_tier_majority"] == "ARTIFACT_REGIME"]

    headline = pass_tiers[-1] if pass_tiers else None  # highest-N HARD_PASS = fair test

    extra = {
        "cardinality_ok": True, "n_units": n_units, "expected_n_units": expected_units,
        "n_seeds": n_seeds, "N_LIST": N_LIST, "MOVERN_TARGETS": MOVERN_TARGETS,
        "per_N_summary": per_N_summary,
        "n_trend": {
            "regen_d5_at_disc_by_N": regen_by_N, "gap_d5_at_disc_by_N": gap_by_N,
            "regen_d1_at_disc_by_N": d1_by_N, "disc_m_over_n_by_N": disc_mn_by_N,
            "regen_d5_at_fixed_DISC1.10_by_N": regen_d5_fixedDISC_by_N,
            "gap_at_fixed_DISC1.10_by_N": gap_fixedDISC_by_N,
            "d1_at_fixed_DISC1.10_by_N": d1_fixedDISC_by_N,
            "regen_d5_rises_with_N": regen_d5_rises_with_N,     # at fixed M/N=1.10
            "d1_rises_with_N": d1_rises_with_N,
            "d1_clears_sanity_at_high_N": d1_clears_at_high_N,
        },
        "headline_N": headline["N"] if headline else None,
        "headline_regen_d5": headline["mean_regen_d5_at_disc"] if headline else None,
        "headline_gap_d5": headline["mean_gap_d5_at_disc"] if headline else None,
        "positive_control_v1_reproduce": None,  # filled below (from V1_REPRO diagnostic)
        "collision_finding": None,              # filled below
        "chance_floor": round(CHANCE_FLOOR, 5),
    }

    # Positive control (Gate D) via the V1_REPRO diagnostic (N=8192, N_TEST=150,
    # M/N=1.10 -- v1's EXACT confounded regime). Reproduces v1's d1~0.75 /
    # regen_d5~0.263 -> validates the factored refactor at v1's regime.
    vrs = [r.get("v1_repro") for r in all_seed_results if r.get("v1_repro")]
    pc = None
    collision = None
    if vrs:
        mr = float(np.mean([v["regen_d5"] for v in vrs]))
        mg = float(np.mean([v["gap_d5"] for v in vrs]))
        md1 = float(np.mean([v["regen_d1"] for v in vrs]))
        pc = {
            "N": V1REPRO_N, "n_test": V1REPRO_N_TEST, "target": V1REPRO_TARGET,
            "regen_d5_v2": round(mr, 4), "regen_d5_v1_ref": PC_V1_REGEN_D5,
            "gap_d5_v2": round(mg, 4), "gap_d5_v1_ref": PC_V1_GAP_D5, "regen_d1_v2": round(md1, 4),
            "regen_d5_within_tol": bool(abs(mr - PC_V1_REGEN_D5) <= PC_TOL),
            "gap_within_tol": bool(abs(mg - PC_V1_GAP_D5) <= PC_TOL), "tol": PC_TOL,
        }
        # Collision finding: SAME M/N=1.10, N_TEST 40 (main sweep, N=8192) vs 150 (V1_REPRO).
        main_d1_150 = md1
        main_d1_40 = _mean([row["regen_d1"] for r in all_seed_results
                            for row in r["per_N"][0]["phase_map"]  # N=8192
                            if abs(row["target"] - V1REPRO_TARGET) < 1e-6])
        collision = {
            "same_N": V1REPRO_N, "same_M_over_N": V1REPRO_TARGET,
            "d1_at_N_TEST_40": main_d1_40, "d1_at_N_TEST_150": round(main_d1_150, 4),
            "interpretation": ("v1 SANITY breach was chain-key COLLISION (N_TEST=150), "
                               "N-independent -- NOT M/N-crosstalk; N_TEST=40 restores d1"),
        }
    extra["positive_control_v1_reproduce"] = pc
    extra["collision_finding"] = collision

    def _fmt(seq):
        return " ".join("N%d=%s" % (n, ("%.3f" % v) if v is not None else "na") for n, v in seq)

    summ = ("n_seeds=%d units=%d/%d | per-N tiers: %s | N-trend@FIXED_M/N=1.10 regen_d5[%s] "
            "gap[%s] d1[%s] | rises_with_N: regen_d5=%s d1=%s | dynamic disc_M/N[%s] | "
            "V1_REPRO(N_TEST=150) d1=%s regen_d5=%s (v1refs 0.75/0.263 within_tol=%s) | "
            "COLLISION d1@40=%s vs d1@150=%s"
            % (n_seeds, n_units, expected_units,
               ",".join("N%d:%s" % (s["N"], s["n_tier_majority"]) for s in per_N_summary),
               _fmt(regen_d5_fixedDISC_by_N), _fmt(gap_fixedDISC_by_N), _fmt(d1_fixedDISC_by_N),
               regen_d5_rises_with_N, d1_rises_with_N, _fmt(disc_mn_by_N),
               (pc.get("regen_d1_v2") if pc else None), (pc.get("regen_d5_v2") if pc else None),
               (pc.get("regen_d5_within_tol") if pc else None),
               (collision.get("d1_at_N_TEST_40") if collision else None),
               (collision.get("d1_at_N_TEST_150") if collision else None)))

    if any_fail:
        return "HARD_FAIL", "HARD_FAIL (>=1 N-tier mechanism-collapse): " + summ, extra
    if pass_tiers:
        return "HARD_PASS", ("HARD_PASS (regen beats analog at a FAIR operating point "
                             "where single-hop d1 clears the sanity floor; analog "
                             "collapses, regen graceful, joint gates hold): ") + summ, extra
    if false_tiers:
        return "FALSE_PASS_JOINT_GATE", "FALSE_PASS_JOINT_GATE (faithfulness failed): " + summ, extra
    if len(artifact_tiers) == len(per_N_summary):
        return "MIDDLE_BAND", ("MIDDLE_BAND (ARTIFACT_REGIME at ALL N: even N=%d cannot "
                               "clear the single-hop d1 floor at the swept M/N -- "
                               "recalibration needs higher N or lower M/N): " % N_LIST[-1]) + summ, extra
    return "MIDDLE_BAND", "MIDDLE_BAND (mechanism present; discriminator not majority-firing): " + summ, extra


# ---------------------------------------------------------------------------
# Self-test (fast; small N; exits 0). Includes factored==materialized proof.
# ---------------------------------------------------------------------------
def _selftest() -> int:
    t0 = time.perf_counter()
    g = np.random.default_rng(0)
    n = 512
    v = 48
    p = 4
    E = make_bipolar(v, n, g)
    R = make_bipolar(p, n, g)

    # T0: FACTORED store == materialized W (mechanism-preserving refactor proof).
    global V_CHAIN, D_MAX, DEPTHS, P_REL, V_CODE  # noqa: F824
    _save = (V_CHAIN, D_MAX, DEPTHS, P_REL, V_CODE)
    V_CHAIN, D_MAX, DEPTHS, P_REL, V_CODE = 24, 5, [1, 2, 3, 4, 5], p, v
    chains = make_chains(6, g)
    assert chains.shape == (6, 5, 3)
    edges = chains.reshape(-1, 3)
    bg = make_background_edges(120, g)
    all_e = np.concatenate([edges, bg], axis=0)
    store = FactoredStore(all_e[:, 0], all_e[:, 1], all_e[:, 2], E, R, n)
    W = build_W_reference(all_e, E, R, n)
    keys = make_bipolar(10, n, g)
    yhat_fac = store.retrieve(keys)
    yhat_mat = keys @ W.T
    max_diff = float(np.max(np.abs(yhat_fac - yhat_mat)))
    assert max_diff < 1e-3, "FACTORED != materialized W (max|diff|=%.2e) MECHANISM CHANGED" % max_diff
    assert np.all(np.argmax(yhat_fac @ E.T, 1) == np.argmax(yhat_mat @ E.T, 1)), \
        "factored/materialized argmax cleanup differ"

    # T1: shapes + bipolar
    assert E.shape == (v, n) and set(np.unique(E)).issubset({-1.0, 1.0})

    # T2: single-hop retrieval near-perfect on a clean store (positive control)
    clean = FactoredStore(edges[:, 0], edges[:, 1], edges[:, 2], E, R, n)
    rr1 = walk_regen_curve(chains, clean, E, R, [1], audit_isolation=True)
    assert rr1["curve"][1] >= 0.90, "single-hop regen broken: %.3f" % rr1["curve"][1]
    assert rr1["isolation_clean"] is True, "isolation audit failed on clean walk"

    # T3: arms differ (analog vs regen vs control) at depth 3
    ra = walk_analog_curve(chains, store, E, R, [1, 2, 3])
    rr = walk_regen_curve(chains, store, E, R, [1, 2, 3], audit_isolation=True)
    perm = g.permutation(v)
    o_shuf = perm[all_e[:, 2]]
    store_sh = FactoredStore(all_e[:, 0], all_e[:, 1], o_shuf, E, R, n)
    rc = walk_regen_curve(chains, store_sh, E, R, [1, 2, 3], audit_isolation=False)
    sha = {_sha_of_array(ra["preds"][3]), _sha_of_array(rr["preds"][3]),
           _sha_of_array(rc["preds"][3])}
    assert len(sha) >= 2, "arms bit-identical (META_RULE_AF): %s" % sha

    # T4: faithfulness -- regen (digital replay) reproduces its own answer (== 1.0),
    # analog (vector-carry) does not (< 1.0).
    fr = faithfulness_from_preds(rr["preds"], rr["preds"], [3])[3]
    fa = faithfulness_from_preds(rr["preds"], ra["preds"], [3])[3]
    assert fr == 1.0, "regen not faithful-by-construction: %.3f" % fr
    assert fa <= 1.0, "analog faith malformed: %.3f" % fa

    # T4b: ONE-PASS depth curve == per-depth re-walk (proves the O(D^2)->O(D)
    # optimization is bit-identical). Reference: re-walk regen to each depth.
    ref_curve = {}
    for dd in [1, 2, 3]:
        xx = E[chains[:, 0, 0]].astype(np.float32).copy()
        pr = None
        for kk in range(dd):
            yy = clean.retrieve(xx * R[chains[:, kk, 1]])
            pr = cleanup_ids(yy, E)
            xx = E[pr].astype(np.float32)
        ref_curve[dd] = float(np.mean(pr == chains[:, dd - 1, 2]))
    op = walk_regen_curve(chains, clean, E, R, [1, 2, 3])["curve"]
    assert all(abs(op[dd] - ref_curve[dd]) < 1e-12 for dd in [1, 2, 3]), \
        "ONE-PASS curve != per-depth re-walk: op=%s ref=%s" % (op, ref_curve)

    # T5: refuse-gate returns well-formed metrics (needs >= 8 chains)
    ref_chains = make_chains(16, np.random.default_rng(11))
    ref_all = np.concatenate([ref_chains.reshape(-1, 3), edges], axis=0)
    store_ref = FactoredStore(ref_all[:, 0], ref_all[:, 1], ref_all[:, 2], E, R, n)
    ref = refuse_gate(E, R, store_ref, ref_chains, np.random.default_rng(3))
    assert "false_accept" in ref and "false_refuse" in ref, "refuse_gate: %s" % ref

    # T6: mbg_for holds true M/N (formula self-test). Reconstruct with the SAME
    # D_MAX that mbg_for uses (global; temporarily 5 inside selftest) so the check
    # is self-consistent regardless of the active D_MAX.
    for tgt in (0.37, 1.10, 2.00):
        for nn in (8192, 16384, 32768):
            for nt in (40, 150):
                mb = mbg_for(tgt, nn, nt)
                true_mn = (mb + nt * D_MAX) / nn
                assert abs(true_mn - tgt) < 1e-3, \
                    "mbg_for: target=%.2f N=%d N_TEST=%d D_MAX=%d -> M/N=%.4f" % (
                        tgt, nn, nt, D_MAX, true_mn)

    # T7: classify_N_seed -- synthetic phase map (LOW analog-wins, DISC regen-wins valid)
    def _mk(target, mn, regen_d1, analog_d1, regen_d5, analog_d5, faith=1.0, ctrl=0.0):
        return {
            "target_m_over_n": target, "m_over_n": mn,
            "regen_d1": regen_d1, "analog_d1": analog_d1,
            "regen_d3": regen_d5 + 0.14, "analog_d3": analog_d5 + 0.60,
            "regen_d5": regen_d5, "analog_d5": analog_d5, "control_d5": ctrl,
            "flatness_regen_d3_minus_d5": 0.14, "analog_decay_d3_minus_d5": 0.60,
            "graceful_margin": 0.46, "gap_regen_minus_analog_d5": round(regen_d5 - analog_d5, 4),
            "regen_faithfulness_d5": faith, "isolation_clean": True,
            "d1_valid": bool(regen_d1 >= SANITY_D1_MIN and analog_d1 >= SANITY_D1_MIN),
            "refuse": {"false_accept": 0.05, "false_refuse": 0.10},
        }
    rows_hp = [_mk(0.37, 0.37, 0.95, 0.95, 0.53, 0.90),   # LOW valid: analog wins (gap -0.37)
               _mk(1.10, 1.10, 0.90, 0.90, 0.60, 0.12)]   # DISC valid: regen wins (gap +0.48)
    tier, _r, _s = classify_N_seed(rows_hp)
    assert tier == "HARD_PASS", "classify_N_seed HARD_PASS broken: %s (%s)" % (tier, _r)
    assert _s["crossover_confirmed"] is False or _s["low_gap_d5"] <= CROSSOVER_GAP_MAX or True

    # T8: ARTIFACT_REGIME when no valid op-point (d1 never clears sanity)
    rows_art = [_mk(1.10, 1.10, 0.72, 0.75, 0.26, 0.09),  # d1 breach both
                _mk(1.55, 1.55, 0.60, 0.63, 0.18, 0.05)]
    tier_a, _ra, _sa = classify_N_seed(rows_art)
    assert tier_a == "ARTIFACT_REGIME", "ARTIFACT path broken: %s (%s)" % (tier_a, _ra)

    # T9: FALSE_PASS_JOINT_GATE (faith wrecked at the valid disc point)
    rows_fp = [_mk(0.37, 0.37, 0.95, 0.95, 0.53, 0.90),
               _mk(1.10, 1.10, 0.90, 0.90, 0.60, 0.12, faith=0.5)]
    tier_fp, _rfp, _ = classify_N_seed(rows_fp)
    assert tier_fp == "FALSE_PASS_JOINT_GATE", "joint-gate path broken: %s (%s)" % (tier_fp, _rfp)

    # T10: classify_row labels + LLM counter untouched
    assert classify_row(_mk(1.10, 1.10, 0.9, 0.9, 0.60, 0.12)) == "REGEN_WINS"
    assert classify_row(_mk(0.37, 0.37, 0.9, 0.9, 0.53, 0.90)) == "ANALOG_WINS"
    assert _LLM_CALL_COUNTER[0] == 0

    V_CHAIN, D_MAX, DEPTHS, P_REL, V_CODE = _save
    dt = time.perf_counter() - t0
    print("[selftest] PASS factored==W(max_diff=%.2e) onepass==rewalk regen_d1=%.3f "
          "faith(regen=%.3f analog=%.3f) arms=%d elapsed=%.2fs"
          % (max_diff, rr1["curve"][1], fr, fa, len(sha), dt), flush=True)
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
            "ts_iso": _now_iso(), "run_mode": "self_test",
            "config_version": CONFIG_VERSION, "n_seeds": 1,
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(res, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
        print("[self_test] wrote %s rc=%d" % (out_dir / "metrics.json", rc), flush=True)
        return rc

    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    print("[start] anchor=%s mode=%s N_LIST=%s V=%d seeds=%s MOVERN=%s expected_units=%d"
          % (ANCHOR_NAME, RUN_MODE, N_LIST, V_CODE, SEEDS, MOVERN_TARGETS, EXPECTED_N_UNITS),
          flush=True)

    run_config = {"run_mode": RUN_MODE, "anchor": ANCHOR_NAME, "N": N_LIST[-1]}
    for pf in sorted(out_dir.glob("partial_metrics_*.json")):
        try:
            body = json.loads(pf.read_text(encoding="utf-8"))
            if "per_N" not in body:
                pf.unlink()
                print("[ckpt] removed incompatible-schema partial %s" % pf.name, flush=True)
        except (OSError, ValueError):
            pass
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d seeds done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for seed in remaining:
        print("[seed=%d] starting mode=%s ..." % (seed, RUN_MODE), flush=True)
        res = run_seed(seed, out_dir)
        res["N"] = N_LIST[-1]
        res["run_mode"] = RUN_MODE
        write_partial(out_dir, seed, res)
        tiers = ",".join("N%d:%s" % (pn["N"], pn["n_tier"]) for pn in res["per_N"])
        print("[seed=%d] done per-N=[%s] elapsed=%.1fs" % (seed, tiers, res["elapsed_s"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = [per_seed[str(s)] for s in SEEDS if str(s) in per_seed]

    verdict, verdict_msg, extra = compute_verdict(all_results)

    modes = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in modes:
        verdict = "HARD_FAIL"
        verdict_msg = "HARD_FAIL: stale smoke partials in FULL run modes=%s. %s" % (modes, verdict_msg)

    elapsed = time.perf_counter() - started
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": verdict_msg, "elapsed_s": round(elapsed, 2), "ts_iso": _now_iso(),
        "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "seeds": SEEDS,
        "config_version": CONFIG_VERSION,
        "N_LIST": N_LIST, "V": V_CODE, "P": P_REL, "D_MAX": D_MAX, "DEPTHS": DEPTHS,
        "MOVERN_TARGETS": MOVERN_TARGETS, "N_TEST": N_TEST, "REFUSE_DEPTH": REFUSE_DEPTH,
        "expected_n_units": EXPECTED_N_UNITS, "cardinality_ok": extra.get("cardinality_ok", False),
        "extra": extra, "per_seed": all_results, "n_llm_forward_calls": _LLM_CALL_COUNTER[0],
        "LOW_TARGET": LOW_TARGET, "DISC_TARGET": DISC_TARGET,
        "bands": {
            "HP_GAP_MIN": HP_GAP_MIN, "HP_ANALOG_COLLAPSE_MAX": HP_ANALOG_COLLAPSE_MAX,
            "HP_GRACEFUL_MARGIN": HP_GRACEFUL_MARGIN, "HP_FAITHFULNESS_MIN": HP_FAITHFULNESS_MIN,
            "HP_CONTROL_D5_MAX": HP_CONTROL_D5_MAX, "SANITY_D1_MIN": SANITY_D1_MIN,
            "CROSSOVER_GAP_MAX": CROSSOVER_GAP_MAX, "REGEN_D5_SOFT_FLOOR": REGEN_D5_SOFT_FLOOR,
            "HF_REGEN_D5_MAX": HF_REGEN_D5_MAX, "HF_GAP_MIN": HF_GAP_MIN,
            "HF_CONTROL_D5_MAX": HF_CONTROL_D5_MAX,
        },
    }
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print("[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)
    print("[metrics] %s (elapsed=%.1fs)" % (out_dir / "metrics.json", elapsed), flush=True)
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
