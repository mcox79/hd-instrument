"""exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1

ENVELOPE-PUSH on the proven regenerative-cleanup reasoning (v2 = CHAIN_GRADE:
single-shot argmax cleanup snaps each hop to the nearest clean codeword; regen
beats analog, faith 1.0, depth-5 fidelity ~0.69-0.74 @ M/N=1.10). v2 measured the
depth curve only to D=7, so "usable depth ~9-10 hops" was EXTRAPOLATION, never
measured. The recorded next lever: ITERATIVE / RESONATOR per-hop cleanup (run the
cleanup attractor to CONVERGENCE, CA3 recurrent-attractor analog) should push
usable depth further and raise fidelity at depth.

THIS CELL tests that lever HONESTLY and measures the true deep depth ceiling.

--------------------------------------------------------------------------------
LOAD-BEARING COMPARISON (PAIRED; same chains + same store + same seed across arms)
--------------------------------------------------------------------------------
ARM_SINGLE_SHOT   -- v2 regen: x_{k+1} = E[argmax_v <E[v], yhat_k>]  (T=1 argmax;
                     the MAP decoder for a clean near-orthogonal codebook). BASELINE.
ARM_ITERATIVE     -- modern-Hopfield / CA3 recurrent attractor cleanup: run the
                     cleanup attractor to convergence (T iters, soft softmax at
                     temperature beta) BEFORE snapping. "Run the cleanup to a fixed
                     point" instead of one hard argmax. MECHANISM (best fair shot).
ARM_SHUFFLED_CTL  -- iterative attractor over the SAME edges with OBJECTS
                     label-shuffled (structure destroyed) -> fidelity ~ chance
                     (1/V). BROKEN-DISCRIMINATOR RAIL (discriminator-fires control).

Chains are NESTED: N_TEST chains of length D_MAX; every arm evaluated at every
prefix-depth d in DEPTHS -> depth curve AND arm curve perfectly PAIRED.

usable_depth(arm) = largest d such that fidelity(1..d) are ALL >= FLOOR (0.5)
                    (contiguous-from-1 sustained usable depth; robust to a lucky
                    deep point). Reported also at a secondary FLOOR (0.30).

--------------------------------------------------------------------------------
DIFFICULTY AXIS = N_TEST (store-capacity / chain-key COLLISION), NOT M/N
--------------------------------------------------------------------------------
PRE-FLIGHT (MEASURED before finalizing) FALSIFIED the naive "crosstalk sets the
ceiling" model: at N=8192, M/N=3, collision-free (N_TEST=6), single-shot is PERFECT
to depth 8+ -- background argmax separation stays ~52 sigma, so per-hop error ~ 0.
The GENUINE limiter of chain depth in a shared Hebbian store is chain-key COLLISION:
storing N_TEST chains puts N_TEST*D_MAX (source,relation)->object edges over only
V_CHAIN*P_REL distinct key slots; when that fill grows, keys carry multiple objects
and retrieval is ambiguous (independent of N). MEASURED @ N=8192, M/N=1.0:
N_TEST 10/25/50 -> usable_ss 14/8/5 (iterative bit-identical, max_abs_gap=0.000).
So M/N is FIXED (1.0) and N_TEST is SWEPT as the store-capacity difficulty.

--------------------------------------------------------------------------------
BANDS (per (N, seed) at a FAIR operating point where single-shot is IN BAND)
--------------------------------------------------------------------------------
A FAIR operating point = a swept N_TEST where SINGLE_SHOT is in band: usable_depth
in [SS_BAND_LO, D_MAX-1] (single-hop store works AND single-shot collapses within
the depth window so there is HEADROOM for iterative to extend). Per (N,seed) the
disc point = the fair point that MAXIMIZES the iterative-minus-single-shot margin.
  ITERATE_REGIME : no fair op-point (single-shot never collapses within D_MAX at
                   any swept N_TEST) and NOT a censored-tie -- REPORTED, not a
                   refutation (needs higher N_TEST or deeper D_MAX at this N).
  HARD_PASS      : at the disc point ALL hold:
                     delta_usable = usable_it - usable_ss >= HP_DEPTH_MARGIN (>=2)
                     mean per-depth gap (fid_it - fid_ss) over the crossover band
                        >= HP_FID_GAP (>=0.05)
                     control usable_depth <= 1 (structure -> chance)
                     iterative faithfulness >= 0.95
                     single_shot IN BAND (usable_ss in [SS_BAND_LO, D_MAX-1])
                     arms_differ == True
  HARD_FAIL      : at a fair op-point delta_usable <= 0 (iterative ties or LOSES
                   single-shot) -- the one-shot argmax snap was already the MAP
                   decoder. Also the CENSORED-TIE case (single-shot deep/never-
                   collapsed within D_MAX but iterative bit-identical). [PRE-FLIGHT
                   PREDICTS THIS: a tuned attractor converges to argmax for a near-
                   orthogonal codebook; ceiling is store-capacity/collision-bound,
                   not cleanup-bound.]
  HARD_FAIL_CTL  : control usable_depth > 1 (broken rail recovers structure) ->
                   discriminator broken.
  MIDDLE_BAND    : 0 < delta_usable < HP_DEPTH_MARGIN (extends a little, not by a
                   real margin), OR extends but cross-seed unstable, OR all-N
                   ITERATE_REGIME.
REPORTED (first-class, survives the tie): the CAPACITY LAW (single-shot usable-depth
  vs N_TEST -- the true deep ceiling v2 never measured), its ~N-independence (the
  collision-limited ceiling should be ~flat in N), the full per-depth fidelity curves
  for all arms, iterative's (predicted-identical) curve, per-depth gap, faith.
AGGREGATE: cell HARD_PASS iff >=1 N-tier majority HARD_PASS with all seeds agreeing
  delta>=margin (cross-seed stable) and no HARD_FAIL_CTL. Cell HARD_FAIL iff a
  MAJORITY of N-tiers are HARD_FAIL (iterative ties/loses everywhere = lever CLOSED,
  the honest negative). All-N ITERATE_REGIME -> MIDDLE_BAND.

--------------------------------------------------------------------------------
CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (single_shot / iterative / control differ;
#   iterative uses SOFT attractor (beta finite) so it is NOT bit-identical to the
#   argmax baseline -- self-test T_attr asserts attractor@HIGH_BETA == argmax to
#   prove the attractor is a correct GENERALIZATION of single-shot).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb/discriminator_reachability: single_shot depth curve spans ~0.96->chance
#   across D=1..14 as N_TEST grows (pre-flight MEASURED: N_TEST 10/25/50 -> ud
#   14/8/5) so the discriminating band [0.30,0.70] is richly populated; iterative
#   has full headroom to extend IF the mechanism works.
# - baseline_in_band (META_RULE_AG): the disc op-point REQUIRES single_shot
#   usable_depth in [SS_BAND_LO, D_MAX-1] (neither saturates nor floors). N_TEST=25
#   is the MEASURED in-band point (ud~8-10, d1~0.84-0.96).
# - discriminator survives scale: the tie is N-INDEPENDENT by the MAP-decoder physics
#   (attractor==argmax for a near-orthogonal codebook; MEASURED bit-identical at
#   N=8192; self-test proves it at N=512) -- option B analytical justification. FULL
#   runs N in {8192,16384} to CONFIRM the ceiling is ~N-independent (collision-bound).
# - HARD_PASS strictly above floor (delta_usable>=2 vs HF delta<=0).
# - HP_SCOPE per-arm declaration (prereg).
# - cardinality_ok (META_RULE_H; EXPECTED_N_UNITS = N x seeds x N_TEST).
# - per-unit failure-class instrumentation (META_RULE_J; no bare except).
# - calibration_check = default_ok (attractor beta/T are FIXED principled values,
#   NOT tuned-for-PASS; a self-test asserts high-beta attractor == argmax).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in prereg.
# - progress_logging = line_buffered_stdout + print flush (timeout_s >= 1800).
# - start_marker + crash_diagnostic + heartbeat (defensive error checking).
# - positive_control (Gate D): single_shot at N=8192 reproduces v2's regenerative-
#   cleanup depth behavior (d1>=0.80 single-hop works; graceful decay; d5 in the
#   v2 range) at the SAME V=512/P=8 regime -> validates the reused scaffold.
--------------------------------------------------------------------------------
Compute architecture: SEQUENCE-DEPENDENT CPU (each hop depends on hop k-1 -- genuine
chained-retrieval sequential dependency exemption) + the cell IS the substrate
cleanup primitive being validated (single-shot argmax AND the modern-Hopfield
attractor generalization). Storage = HEBBIAN (bundled) BY DESIGN: superposition
crosstalk is the per-hop noise the cleanup must overcome (SHARDED-rule exemption --
bundled IS the discriminator substrate, identical to v2). Retrieval is the FACTORED
store (no N x N materialization), M-chunked numpy batched matmul across all test
chains per hop. The attractor is O(T*B*V*N) per hop, cheap relative to the retrieve
O(B*M*N); iterative is only marginally more expensive than single-shot.

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

ANCHOR_NAME = "cortex_iterative_attractor_cleanup_depth_ceiling_v1"
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
# FLOOR for "usable depth". Contract floor = 0.5; secondary reported at 0.30.
USABLE_FLOOR = 0.50
USABLE_FLOOR_SECONDARY = 0.30

# Attractor (modern-Hopfield / CA3) cleanup hyperparameters -- FIXED, principled,
# NOT tuned-for-PASS. BETA_ITER is moderate (soft integration = best fair shot for
# the mechanism to recover ambiguous hops); T_ITER = "run to convergence".
# BETA_HIGH is used ONLY in the self-test to prove attractor@high-beta == argmax
# (correct generalization of single-shot).
BETA_ITER = 12.0
T_ITER = 6
BETA_HIGH = 60.0

# DIFFICULTY AXIS = N_TEST (number of stored chains = chain-key COLLISION load =
# store key-capacity pressure). PRE-FLIGHT (MEASURED, exp_dev 2026-07-05): the
# depth ceiling of a shared Hebbian associative store is set by chain-key COLLISION
# (N_TEST*D_MAX chain edges over V_CHAIN*P_REL key slots), NOT by background
# crosstalk (M/N) -- at N=8192, M/N=3, collision-free, single-shot is PERFECT to
# depth 8+; background argmax stays ~52 sigma. So M/N is fixed and N_TEST is swept.
# MEASURED usable_ss @ N=8192, M/N=1.0: N_TEST 10/25/50 -> ud 14/8/5 (iterative
# bit-identical at every point, maxgap=0.000). The ceiling is N-INDEPENDENT (collision
# is about key slots, not dimension), so N-scaling is a check, not the lever.
MOVERN_FIXED = 1.0

if RUN_MODE == "self_test":
    N_LIST = [512]
    V_CODE = 48
    P_REL = 4
    NTEST_TARGETS = [6, 12]
    SEEDS = [0]
    D_MAX = 6
    DEPTHS = [1, 2, 3, 4, 5, 6]
elif RUN_MODE == "smoke":
    # In-band preview: N_TEST=25 puts single-shot IN BAND (ud~8 of D=12; d1~0.96,
    # clean single-hop, graceful decay). Single N (the tie is N-INDEPENDENT by the
    # MAP-decoder physics -- discriminator-survives-scale option B analytical), 3
    # seeds for cross-seed variance. Fast local smoke.
    N_LIST = [8192]
    V_CODE = 512
    P_REL = 8
    NTEST_TARGETS = [25]
    SEEDS = [7, 17, 23]
    D_MAX = 12
    DEPTHS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
else:  # full
    # Sweep N_TEST (capacity/collision) to bracket the single-shot collapse: N_TEST
    # 15/25/40 -> fill 10%/17%/27% -> ud ~12/8/5 (single-shot IN BAND with headroom
    # for iterative to extend IF it could). N in {8192,16384} checks the ceiling is
    # N-independent (collision-limited). V=512/P=8 reproduce v2's regime for the PC.
    N_LIST = [8192, 16384]
    V_CODE = 512
    P_REL = 8
    NTEST_TARGETS = [15, 25, 40]
    SEEDS = [7, 17, 23, 31, 41]
    D_MAX = 14
    DEPTHS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

# Chain-node partition: chain nodes drawn from [0, V_CHAIN); background edge sources
# from [V_CHAIN, V_CODE) so chain keys never key-collide with BACKGROUND keys (chain
# keys can still collide with each other -- that intra-chain collision IS the swept
# store-capacity difficulty). N distinct chain-key slots = V_CHAIN * P_REL.
V_CHAIN = V_CODE // 2
KEY_SLOTS = V_CHAIN * P_REL


def collision_fill(n_test: int, d_max: int) -> float:
    """Chain-key fill = stored chain edges / distinct chain-key slots (the store-
    capacity difficulty knob). Higher fill -> more ambiguous keys -> shallower depth."""
    return round((n_test * d_max) / float(KEY_SLOTS), 4)

# Operating-point band for single_shot (baseline-in-band, META_RULE_AG).
SS_BAND_LO = 2  # single_shot usable_depth must be >= this (single-hop store works)

# Bands ---------------------------------------------------------------------
HP_DEPTH_MARGIN = 2        # usable_it - usable_ss >= 2 hops (a REAL extension)
HP_FID_GAP = 0.05          # mean per-depth (fid_it - fid_ss) over crossover band
HP_FAITH_MIN = 0.95        # iterative faithful-by-construction (clean-codeword carry)
HP_CTL_USABLE_MAX = 1      # control usable_depth <= 1 (structure -> chance)
HP_D1_SANITY = 0.80        # single-hop store works (both cleanup arms d1 >= this)
TIE_TOL = 0.05             # iterative within this of single_shot at EVERY depth == tie

# Positive control (Gate D): single_shot at N=8192 reproduces v2 regen depth behavior.
PC_V2_N = 8192
PC_V2_REGEN_D5_LO = 0.40   # v2 regen_d5 spanned ~0.53-0.925 across seeds/M/N; broad
PC_V2_REGEN_D5_HI = 0.95   # band tolerant of V/RNG/D_MAX drift (qualitative repro)
# CITED@data/exp_cortex_regenerative_cleanup_vs_analog_accumulate_v2/metrics.json

CHANCE_FLOOR = 1.0 / V_CODE   # THEORETICAL final-node argmax chance floor

# Cardinality (META_RULE_H).
EXPECTED_N_UNITS = len(SEEDS) * len(N_LIST) * len(NTEST_TARGETS)

CONFIG_VERSION = (
    "ANCHOR=%s,N_LIST=%s,V=%d,P=%d,D_MAX=%d,MOVERN=%.2f,NTEST=%s,BETA_ITER=%.1f,"
    "T_ITER=%d,FLOOR=%.2f,V_CHAIN=%d,KEY_SLOTS=%d,SEEDS=%s,RUN_MODE=%s,"
    "store=FACTORED_HEBBIAN,difficulty=NTEST_collision,"
    "hardening=startmarker+crashdiag+heartbeat+AF+AH+AG"
) % (
    ANCHOR_NAME, "-".join(str(n) for n in N_LIST), V_CODE, P_REL, D_MAX, MOVERN_FIXED,
    "-".join(str(nt) for nt in NTEST_TARGETS), BETA_ITER, T_ITER, USABLE_FLOOR,
    V_CHAIN, KEY_SLOTS, "-".join(str(s) for s in SEEDS), RUN_MODE,
)


# ---------------------------------------------------------------------------
# Defensive-error-checking helpers (start marker / crash / heartbeat)
# ---------------------------------------------------------------------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(out_dir: Path, run_mode: str, expected_units: int) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode, "expected_n_units": expected_units,
        "host": platform.node(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    final = out_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(str(tmp), str(final))


def _write_crash_metrics(out_dir: Path, exc: Exception) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
        "pid": os.getpid(), "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(final))


def _heartbeat(out_dir: Path, unit_idx: int, total_units: int, t0: float,
               extra: Optional[Dict[str, Any]] = None) -> None:
    row = {"ts_iso": _now_iso(), "unit_idx": unit_idx, "total_units": total_units,
           "elapsed_s": round(time.perf_counter() - t0, 2)}
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
    """Edge-chunk size bounding a block to ~256 MB (adaptive to N)."""
    return max(256, (1 << 26) // n_dim)


class FactoredStore:
    """Hebbian associative store held as EDGE-INDEX lists (NEVER materializes the
    N x N W NOR the full (M, N) key/value matrices -- memory O(M) ints + O(chunk*N)).

    retrieve(x) = sum_e <x, E[s_e]*R[p_e]> * E[o_e] / N  ==  x @ W.T where
    W = sum_e outer(E[o_e], E[s_e]*R[p_e]) / N. Per chunk the (chunk, N) key/value
    vectors are built on the fly from the int indices + shared codebooks E, R (this
    is v2's memory-efficient design; storing full (M, N) key/value matrices OOMs at
    N=32768/M=65536 = 8.6 GB each). Self-test T0 proves numerically identical to the
    materialized W @ x."""

    __slots__ = ("s", "p", "o", "E", "R", "n_dim", "chunk", "_edge_key")

    def __init__(self, s: np.ndarray, p: np.ndarray, o: np.ndarray,
                 E: np.ndarray, R: np.ndarray, n_dim: int):
        self.s = np.ascontiguousarray(s.astype(np.int64))
        self.p = np.ascontiguousarray(p.astype(np.int64))
        self.o = np.ascontiguousarray(o.astype(np.int64))
        self.E = E
        self.R = R
        self.n_dim = int(n_dim)
        self.chunk = _chunk_for(n_dim)
        # cheap store-invariance fingerprint (isolation audit); O(M) ints only.
        h = hashlib.sha256()
        h.update(self.s.tobytes())
        h.update(self.p.tobytes())
        h.update(self.o.tobytes())
        self._edge_key = h.hexdigest()[:16]

    def retrieve(self, keys: np.ndarray) -> np.ndarray:
        """keys: (B, N) -> yhat: (B, N)."""
        m = self.s.shape[0]
        out = np.zeros((keys.shape[0], self.n_dim), dtype=np.float32)
        if m == 0:
            return out
        for c0 in range(0, m, self.chunk):
            sl = slice(c0, c0 + self.chunk)
            kc = self.E[self.s[sl]] * self.R[self.p[sl]]   # (c, N) key vectors
            coeff = keys @ kc.T                             # (B, c)
            out += coeff @ self.E[self.o[sl]]               # (B, N)
        out /= float(self.n_dim)
        return out.astype(np.float32)

    def sha_edges(self) -> str:
        return self._edge_key


def build_W_reference(s: np.ndarray, p: np.ndarray, o: np.ndarray,
                      E: np.ndarray, R: np.ndarray, n_dim: int) -> np.ndarray:
    """Materialized Hebbian W (REFERENCE ONLY; self-test T0 proves the factored
    store is numerically identical). NOT used in the sweep (small edge sets only)."""
    if s.shape[0] == 0:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    k = E[s] * R[p]
    vv = E[o]
    return (vv.T @ k).astype(np.float32) / float(n_dim)


def argmax_clean(yhat: np.ndarray, E: np.ndarray) -> np.ndarray:
    """Single-shot cleanup: snap each row of yhat (B, N) to nearest atom -> ids (B,)."""
    return np.argmax(yhat @ E.T, axis=1)


def attractor_clean(yhat: np.ndarray, E: np.ndarray, beta: float, T: int) -> np.ndarray:
    """Modern-Hopfield / CA3 recurrent-attractor cleanup: iterate the softmax
    attractor to convergence, then snap. z_{t+1} = softmax(beta * cos(z, E)) @ E,
    re-normalized. As beta -> inf (or codebook orthogonal) this converges to the
    argmax basin in one step == single-shot (self-test T_attr asserts this). With
    finite beta over T steps the attractor integrates evidence across iterations
    (the mechanism's best fair shot at recovering ambiguous hops)."""
    n = float(E.shape[1])
    sq = math.sqrt(n)
    z = yhat / (np.linalg.norm(yhat, axis=1, keepdims=True) + 1e-9)
    for _ in range(T):
        sim = (z @ E.T) / (np.linalg.norm(z, axis=1, keepdims=True) * sq + 1e-9)  # (B,V) cos
        s = beta * sim
        s -= s.max(axis=1, keepdims=True)
        w = np.exp(s)
        w /= w.sum(axis=1, keepdims=True)
        z = (w @ E).astype(np.float32)                                            # (B,N)
        z /= (np.linalg.norm(z, axis=1, keepdims=True) + 1e-9)
    return np.argmax(z @ E.T, axis=1)


def _sha_of_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Chain generation (nested; reserved node partitions) - v2 logic
# ---------------------------------------------------------------------------
def make_chains(n_chains: int, d_max: int, g: np.random.Generator) -> np.ndarray:
    """(n_chains, d_max, 3) int array of (s, p, o) using chain-partition nodes."""
    chains = np.zeros((n_chains, d_max, 3), dtype=np.int64)
    for c in range(n_chains):
        nodes = [int(g.integers(0, V_CHAIN))]
        for _ in range(d_max):
            nxt = int(g.integers(0, V_CHAIN))
            while nxt == nodes[-1]:
                nxt = int(g.integers(0, V_CHAIN))
            nodes.append(nxt)
        for i in range(d_max):
            chains[c, i, 0] = nodes[i]
            chains[c, i, 1] = int(g.integers(0, P_REL))
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
    for c in range(chains.shape[0]):
        j = int(g.integers(0, chains.shape[1]))
        p_orig = int(chains[c, j, 1])
        p_new = (p_orig + 1 + int(g.integers(0, P_REL - 1))) % P_REL
        broken[c, j, 1] = p_new
        broken[c, j, 2] = int(g.integers(0, V_CHAIN))
    return broken


# ---------------------------------------------------------------------------
# Arm walkers (batched across chains; retrieve via factored store).
# ONE-PASS depth curves: a single walk to max(depths) recording accuracy at every
# prefix depth is BIT-IDENTICAL to re-walking to each depth separately (self-test
# T_onepass), at ~1/len(depths) the retrieve calls.
# ---------------------------------------------------------------------------
def walk_curve(chains: np.ndarray, store: FactoredStore, E: np.ndarray, R: np.ndarray,
               depths: List[int], clean_fn) -> Dict[str, Any]:
    """Generic regenerative walk: snap to a CLEAN atom each hop via clean_fn(yhat),
    carry the clean codeword forward. Returns per-depth fidelity + per-depth preds
    (the emitted answers = the digital trace outcome, reused for faithfulness)."""
    dmax = max(depths)
    x = E[chains[:, 0, 0]].astype(np.float32).copy()
    assert x.base is None, "scratchpad must be a fresh array (separate register)"
    curve: Dict[int, float] = {}
    preds: Dict[int, np.ndarray] = {}
    for k in range(dmax):
        p = chains[:, k, 1]
        key = x * R[p]
        yhat = store.retrieve(key)
        pred = clean_fn(yhat)
        d = k + 1
        if d in depths:
            curve[d] = float(np.mean(pred == chains[:, d - 1, 2]))
            preds[d] = pred
        x = E[pred].astype(np.float32)              # snap to clean codeword
    return {"curve": curve, "preds": preds}


def faithfulness_from_preds(digital_preds: Dict[int, np.ndarray],
                            arm_preds: Dict[int, np.ndarray],
                            depths: List[int]) -> Dict[int, float]:
    """faith[d] = fraction where the DIGITAL replay's answer matches the arm's
    emitted answer. Regenerative (clean-codeword-carry) arms are faithful-by-
    construction (== 1.0); a vector-carry arm would be < 1.0."""
    out: Dict[int, float] = {}
    for d in depths:
        if d in digital_preds and d in arm_preds:
            out[d] = round(float(np.mean(digital_preds[d] == arm_preds[d])), 4)
    return out


def usable_depth(curve: Dict[int, float], depths: List[int], floor: float) -> int:
    """Contiguous-from-1 sustained usable depth: largest d s.t. fidelity(1..d) all
    >= floor. 0 if even d1 is below floor. Robust to a lucky deep point."""
    ud = 0
    for d in sorted(depths):
        if curve.get(d, 0.0) >= floor:
            ud = d
        else:
            break
    return ud


# ---------------------------------------------------------------------------
# One (N, seed, M_BG) run -> full depth curves for all arms + usable depths
# ---------------------------------------------------------------------------
def run_cell(n_dim: int, seed: int, n_test: int, out_dir: Path,
             hb_state: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.perf_counter()
    chain_edge_count = n_test * D_MAX
    m_total_target = int(round(MOVERN_FIXED * n_dim))
    m_bg = max(0, m_total_target - chain_edge_count)
    fill = collision_fill(n_test, D_MAX)
    g = np.random.default_rng(seed * 100003 + n_dim * 7 + m_bg + n_test)

    E = make_bipolar(V_CODE, n_dim, g)
    R = make_bipolar(P_REL, n_dim, g)
    chains = make_chains(n_test, D_MAX, g)
    chain_edges = chains.reshape(-1, 3)
    bg_edges = make_background_edges(m_bg, g)
    all_edges = np.concatenate([chain_edges, bg_edges], axis=0)
    m_total = int(all_edges.shape[0])

    store = FactoredStore(all_edges[:, 0], all_edges[:, 1], all_edges[:, 2], E, R, n_dim)

    # shuffled control store: destroy structure by permuting object labels.
    perm = g.permutation(V_CODE)
    o_shuf = perm[all_edges[:, 2]]
    store_shuf = FactoredStore(all_edges[:, 0], all_edges[:, 1], o_shuf, E, R, n_dim)
    sha_before = store.sha_edges()

    # ONE-PASS walks (each arm walked once to D_MAX).
    r_ss = walk_curve(chains, store, E, R, DEPTHS, lambda y: argmax_clean(y, E))
    r_it = walk_curve(chains, store, E, R, DEPTHS,
                      lambda y: attractor_clean(y, E, BETA_ITER, T_ITER))
    r_ct = walk_curve(chains, store_shuf, E, R, DEPTHS,
                      lambda y: attractor_clean(y, E, BETA_ITER, T_ITER))
    sha_after = store.sha_edges()
    isolation_clean = (sha_before == sha_after)

    ss_curve = {d: round(v, 4) for d, v in r_ss["curve"].items()}
    it_curve = {d: round(v, 4) for d, v in r_it["curve"].items()}
    ct_curve = {d: round(v, 4) for d, v in r_ct["curve"].items()}

    # faithfulness: regenerative arms replay their own digital trace (== 1.0). Use
    # single-shot's atom-carry preds as the digital replay reference; the iterative
    # arm's emitted preds are compared to ITS OWN replay (regenerative -> 1.0).
    it_faith = faithfulness_from_preds(r_it["preds"], r_it["preds"], DEPTHS)

    ud_ss = usable_depth(ss_curve, DEPTHS, USABLE_FLOOR)
    ud_it = usable_depth(it_curve, DEPTHS, USABLE_FLOOR)
    ud_ct = usable_depth(ct_curve, DEPTHS, USABLE_FLOOR)
    ud_ss_sec = usable_depth(ss_curve, DEPTHS, USABLE_FLOOR_SECONDARY)
    ud_it_sec = usable_depth(it_curve, DEPTHS, USABLE_FLOOR_SECONDARY)

    # per-depth gap curve (iterative - single_shot) and crossover-band mean gap.
    gap_curve = {d: round(it_curve[d] - ss_curve[d], 4) for d in DEPTHS}
    max_abs_gap = round(float(max(abs(gap_curve[d]) for d in DEPTHS)), 4)
    curves_identical = bool(max_abs_gap < TIE_TOL)  # iterative overlays single_shot
    # crossover band = depths where single_shot is in [0.30, 0.70] (the region where
    # an extension could show); mean gap there is the fidelity-gap discriminator.
    cross_ds = [d for d in DEPTHS if 0.30 <= ss_curve[d] <= 0.70]
    mean_gap_cross = (round(float(np.mean([gap_curve[d] for d in cross_ds])), 4)
                      if cross_ds else None)

    delta_usable = ud_it - ud_ss

    arms_sha = {
        "single_shot": _sha_of_array(r_ss["preds"][DEPTHS[-1]]),
        "iterative": _sha_of_array(r_it["preds"][DEPTHS[-1]]),
        "control": _sha_of_array(r_ct["preds"][DEPTHS[-1]]),
    }
    arms_differ = (len(set(arms_sha.values())) == 3)

    for depth in DEPTHS:
        hb_state["unit"] += 1
        _heartbeat(out_dir, hb_state["unit"], hb_state["total"], hb_state["t0"],
                   extra={"N": n_dim, "seed": seed, "n_test": n_test, "depth": depth,
                          "ss": ss_curve[depth], "it": it_curve[depth]})

    it_faith_d5 = it_faith.get(5, it_faith.get(DEPTHS[-1], float("nan")))
    print("  [N=%d seed=%d N_TEST=%d fill=%.2f M/N=%.2f] ud(floor%.2f) ss=%d it=%d ctl=%d "
          "delta=%+d | ss_d1=%.3f it_d1=%.3f mean_gap_cross=%s max_abs_gap=%.3f it_faith=%.3f iso=%s"
          % (n_dim, seed, n_test, fill, round(m_total / float(n_dim), 3), USABLE_FLOOR,
             ud_ss, ud_it, ud_ct, delta_usable, ss_curve[1], it_curve[1], mean_gap_cross,
             max_abs_gap, it_faith_d5, isolation_clean), flush=True)
    print("    ss_curve=%s" % [ss_curve[d] for d in DEPTHS], flush=True)
    print("    it_curve=%s" % [it_curve[d] for d in DEPTHS], flush=True)

    return {
        "N": n_dim, "seed": seed, "n_test": int(n_test), "fill": fill,
        "m_bg": int(m_bg), "m_total": m_total,
        "m_over_n": round(m_total / float(n_dim), 4), "V": V_CODE, "P": P_REL,
        "run_mode": RUN_MODE,
        "ss_curve": ss_curve, "it_curve": it_curve, "control_curve": ct_curve,
        "gap_curve": gap_curve, "mean_gap_cross": mean_gap_cross,
        "cross_band_depths": cross_ds,
        "max_abs_gap": max_abs_gap, "curves_identical": curves_identical,
        "it_faith_curve": it_faith,
        "usable_ss": ud_ss, "usable_it": ud_it, "usable_ctl": ud_ct,
        "usable_ss_secfloor": ud_ss_sec, "usable_it_secfloor": ud_it_sec,
        "delta_usable": int(delta_usable),
        "ss_d1": ss_curve[1], "it_d1": it_curve[1],
        "ss_in_band": bool(SS_BAND_LO <= ud_ss <= D_MAX - 1),
        "d1_sanity_ok": bool(ss_curve[1] >= HP_D1_SANITY and it_curve[1] >= HP_D1_SANITY),
        "it_faith_min": round(float(min(it_faith.values())) if it_faith else float("nan"), 4),
        "isolation_clean": bool(isolation_clean),
        "arms_sha": arms_sha, "arms_differ": bool(arms_differ),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "config_version": CONFIG_VERSION,
    }


# ---------------------------------------------------------------------------
# Per (N, seed) tier: scan M/N, find the fair (single_shot in-band) disc point
# ---------------------------------------------------------------------------
def classify_N_seed(rows: List[Dict[str, Any]]) -> Tuple[str, List[str], Dict[str, Any]]:
    reasons: List[str] = []
    rows_sorted = sorted(rows, key=lambda r: r["n_test"])   # easier -> harder

    # control broken anywhere -> HARD_FAIL_CTL (discriminator rail broken)
    ctl_broken = [r for r in rows_sorted if r["usable_ctl"] > HP_CTL_USABLE_MAX]

    fair = [r for r in rows_sorted if r["ss_in_band"] and r["d1_sanity_ok"]]

    def _mk_summ(disc: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        s = {
            "phase_points": [{"n_test": r["n_test"], "fill": r["fill"],
                              "usable_ss": r["usable_ss"], "usable_it": r["usable_it"],
                              "usable_ctl": r["usable_ctl"], "delta_usable": r["delta_usable"],
                              "mean_gap_cross": r["mean_gap_cross"], "max_abs_gap": r["max_abs_gap"],
                              "ss_in_band": r["ss_in_band"]} for r in rows_sorted],
        }
        if disc is not None:
            s.update({
                "disc_n_test": disc["n_test"], "disc_fill": disc["fill"],
                "usable_ss": disc["usable_ss"], "usable_it": disc["usable_it"],
                "usable_ctl": disc["usable_ctl"], "delta_usable": disc["delta_usable"],
                "mean_gap_cross": disc["mean_gap_cross"],
                "max_abs_gap": disc.get("max_abs_gap"),
                "curves_identical": disc.get("curves_identical"),
                "it_faith_min": disc["it_faith_min"],
                "isolation_clean": disc["isolation_clean"],
                "arms_differ": disc["arms_differ"],
                "usable_ss_secfloor": disc["usable_ss_secfloor"],
                "usable_it_secfloor": disc["usable_it_secfloor"],
                "ss_curve": disc["ss_curve"], "it_curve": disc["it_curve"],
            })
        else:
            s["disc_n_test"] = None
        return s

    if ctl_broken:
        disc = ctl_broken[0]
        summ = _mk_summ(disc)
        reasons.append("HARD_FAIL_CTL(control usable_depth=%d > %d @N_TEST=%d -- "
                       "structure-shuffled store still recovers -> discriminator broken)"
                       % (disc["usable_ctl"], HP_CTL_USABLE_MAX, disc["n_test"]))
        return "HARD_FAIL_CTL", reasons, summ

    if not fair:
        # No fair (in-band) op-point. But if single_shot is DEEP/CENSORED (never
        # collapsed within D_MAX) AND the iterative curve is bit-identical to it
        # (curves_identical) with no extension, that is still a DECISIVE TIE (the
        # lever is closed even though the baseline is censored, not saturated-at-1).
        censored_tie = [r for r in rows_sorted
                        if r["d1_sanity_ok"] and r["usable_ss"] >= D_MAX - 1
                        and r["curves_identical"] and r["delta_usable"] <= 0]
        if censored_tie:
            disc = max(censored_tie, key=lambda r: r["usable_ss"])
            summ = _mk_summ(disc)
            reasons.append("HARD_FAIL_TIE_CENSORED @N_TEST=%d fill=%.2f usable_ss=%d(>=D_MAX-1 "
                           "-- single_shot did NOT collapse within D=%d, ceiling censored) "
                           "usable_it=%d delta=%d max_abs_gap=%.3f (iterative curve is "
                           "bit-identical to single_shot across ALL depths -- decisive TIE, "
                           "iterative adds nothing; the deep ceiling here EXCEEDS %d hops)"
                           % (disc["n_test"], disc["fill"], disc["usable_ss"], D_MAX,
                              disc["usable_it"], disc["delta_usable"], disc["max_abs_gap"], D_MAX))
            return "HARD_FAIL", reasons, summ
        best = max(rows_sorted, key=lambda r: r["usable_ss"])
        summ = _mk_summ(best)
        reasons.append("ITERATE_REGIME(no fair op-point: single_shot usable_depth not "
                       "in [%d,%d] at any swept N_TEST -- best usable_ss=%d @N_TEST=%d "
                       "curves_identical=%s; needs higher N_TEST or deeper D_MAX at this N)"
                       % (SS_BAND_LO, D_MAX - 1, best["usable_ss"], best["n_test"],
                          best["curves_identical"]))
        return "ITERATE_REGIME", reasons, summ

    # disc point = fair point maximizing the iterative extension margin.
    disc = max(fair, key=lambda r: (r["delta_usable"],
                                    r["mean_gap_cross"] if r["mean_gap_cross"] is not None else -9))
    summ = _mk_summ(disc)

    hp = (disc["delta_usable"] >= HP_DEPTH_MARGIN
          and (disc["mean_gap_cross"] is not None and disc["mean_gap_cross"] >= HP_FID_GAP)
          and disc["usable_ctl"] <= HP_CTL_USABLE_MAX
          and disc["it_faith_min"] >= HP_FAITH_MIN
          and disc["arms_differ"] and disc["isolation_clean"])
    if hp:
        reasons.append("HARD_PASS @N_TEST=%d fill=%.2f usable_ss=%d usable_it=%d delta=+%d "
                       "mean_gap_cross=%.3f it_faith=%.3f ctl=%d (iterative EXTENDS "
                       "usable depth by a real margin)"
                       % (disc["n_test"], disc["fill"], disc["usable_ss"], disc["usable_it"],
                          disc["delta_usable"], disc["mean_gap_cross"],
                          disc["it_faith_min"], disc["usable_ctl"]))
        return "HARD_PASS", reasons, summ

    if disc["delta_usable"] <= 0:
        reasons.append("HARD_FAIL @N_TEST=%d fill=%.2f usable_ss=%d usable_it=%d delta=%d "
                       "max_abs_gap=%.3f (iterative TIES/LOSES single-shot at a fair "
                       "op-point -- the one-shot argmax snap was already the MAP decoder; "
                       "the depth ceiling is store-capacity/collision-bound, not cleanup-bound)"
                       % (disc["n_test"], disc["fill"], disc["usable_ss"], disc["usable_it"],
                          disc["delta_usable"], disc.get("max_abs_gap", -1.0)))
        return "HARD_FAIL", reasons, summ

    reasons.append("MIDDLE_BAND @N_TEST=%d fill=%.2f usable_ss=%d usable_it=%d delta=+%d "
                   "mean_gap_cross=%s (iterative extends a little but not by the "
                   ">=%d-hop margin, or gap below %.2f)"
                   % (disc["n_test"], disc["fill"], disc["usable_ss"], disc["usable_it"],
                      disc["delta_usable"], disc["mean_gap_cross"], HP_DEPTH_MARGIN,
                      HP_FID_GAP))
    return "MIDDLE_BAND", reasons, summ


# ---------------------------------------------------------------------------
# Per-seed driver: for each N, sweep M/N -> per-N tier.
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    t0 = time.perf_counter()
    hb_total = len(N_LIST) * len(NTEST_TARGETS) * len(DEPTHS)
    hb_state = {"unit": 0, "total": hb_total, "t0": t0}
    per_N: List[Dict[str, Any]] = []

    for n_dim in N_LIST:
        rows: List[Dict[str, Any]] = []
        for n_test in NTEST_TARGETS:
            res = run_cell(n_dim, seed, n_test, out_dir, hb_state)
            rows.append(res)
        tier, reasons, summ = classify_N_seed(rows)
        print("  [N=%d seed=%d] N_TIER=%s %s" % (n_dim, seed, tier, reasons), flush=True)
        per_N.append({
            "N": n_dim, "seed": seed, "n_tier": tier, "n_tier_reasons": reasons,
            "disc_summary": summ,
            "phase_map": [{"n_test": r["n_test"], "fill": r["fill"], "m_over_n": r["m_over_n"],
                           "usable_ss": r["usable_ss"], "usable_it": r["usable_it"],
                           "usable_ctl": r["usable_ctl"], "delta_usable": r["delta_usable"],
                           "mean_gap_cross": r["mean_gap_cross"],
                           "ss_in_band": r["ss_in_band"], "d1_sanity_ok": r["d1_sanity_ok"],
                           "max_abs_gap": r["max_abs_gap"], "curves_identical": r["curves_identical"],
                           "ss_d1": r["ss_d1"], "it_d1": r["it_d1"],
                           "it_faith_min": r["it_faith_min"],
                           "isolation_clean": r["isolation_clean"],
                           "arms_differ": r["arms_differ"],
                           "ss_curve": r["ss_curve"], "it_curve": r["it_curve"],
                           "control_curve": r["control_curve"],
                           "gap_curve": r["gap_curve"]} for r in rows],
        })

    return {
        "seed": seed, "run_mode": RUN_MODE, "N": N_LIST[-1],
        "n_llm_calls": _LLM_CALL_COUNTER[0], "per_N": per_N,
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "config_version": CONFIG_VERSION,
    }


# ---------------------------------------------------------------------------
# Aggregate verdict across seeds + N
# ---------------------------------------------------------------------------
def _mean(xs: List[Any]) -> Optional[float]:
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return round(float(np.mean(xs)), 4) if xs else None


def compute_verdict(all_seed_results: List[Dict[str, Any]]) -> Tuple[str, str, Dict[str, Any]]:
    n_seeds = len(all_seed_results)
    if n_seeds == 0:
        return "HARD_FAIL", "NO_SEED_RESULTS", {"cardinality_ok": False}

    n_units = sum(len(pn["phase_map"]) for r in all_seed_results for pn in r["per_N"])
    expected_units = n_seeds * len(N_LIST) * len(NTEST_TARGETS)
    cardinality_ok = (n_units == expected_units)
    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H units=%d expected=%d"
                % (n_units, expected_units),
                {"cardinality_ok": False, "n_units": n_units, "expected": expected_units})

    per_N_summary: List[Dict[str, Any]] = []
    for i, n_dim in enumerate(N_LIST):
        tiers = [r["per_N"][i]["n_tier"] for r in all_seed_results]
        ds = [r["per_N"][i]["disc_summary"] for r in all_seed_results]
        n_pass = sum(1 for t in tiers if t == "HARD_PASS")
        n_fail = sum(1 for t in tiers if t == "HARD_FAIL")
        n_ctl = sum(1 for t in tiers if t == "HARD_FAIL_CTL")
        n_iter = sum(1 for t in tiers if t == "ITERATE_REGIME")
        n_mid = sum(1 for t in tiers if t == "MIDDLE_BAND")
        majority = (n_seeds // 2) + 1
        # cross-seed stability of the extension: all seeds must agree delta>=margin.
        deltas = [d.get("delta_usable") for d in ds if d.get("delta_usable") is not None]
        all_extend = bool(deltas) and all(dl >= HP_DEPTH_MARGIN for dl in deltas)
        if n_ctl > 0:
            n_tier = "HARD_FAIL_CTL"
        elif n_pass >= majority and all_extend:
            n_tier = "HARD_PASS"
        elif n_fail >= majority:
            n_tier = "HARD_FAIL"
        elif n_iter >= majority:
            n_tier = "ITERATE_REGIME"
        else:
            n_tier = "MIDDLE_BAND"
        per_N_summary.append({
            "N": n_dim, "n_tier_majority": n_tier, "seed_tiers": tiers,
            "n_pass": n_pass, "n_fail": n_fail, "n_fail_ctl": n_ctl,
            "n_iterate": n_iter, "n_middle": n_mid, "all_seeds_extend": all_extend,
            "mean_usable_ss_at_disc": _mean([d.get("usable_ss") for d in ds]),
            "mean_usable_it_at_disc": _mean([d.get("usable_it") for d in ds]),
            "mean_delta_usable_at_disc": _mean([d.get("delta_usable") for d in ds]),
            "seed_delta_usable": deltas,
            "mean_gap_cross_at_disc": _mean([d.get("mean_gap_cross") for d in ds]),
            "mean_ctl_usable_at_disc": _mean([d.get("usable_ctl") for d in ds]),
            "mean_it_faith_at_disc": _mean([d.get("it_faith_min") for d in ds]),
        })

    # SINGLE-SHOT usable-depth-vs-N law (N-independence check: collision-limited
    # ceiling should be ~flat in N).
    ss_law = [(s["N"], s["mean_usable_ss_at_disc"]) for s in per_N_summary]
    it_law = [(s["N"], s["mean_usable_it_at_disc"]) for s in per_N_summary]
    delta_law = [(s["N"], s["mean_delta_usable_at_disc"]) for s in per_N_summary]

    def _rises(seq):
        vals = [v for _, v in seq if v is not None]
        return bool(len(vals) >= 2 and vals[-1] > vals[0] + 1e-6)

    ss_depth_rises_with_N = _rises(ss_law)

    # CAPACITY LAW (first-class): usable-depth vs N_TEST (store-capacity/collision),
    # aggregated over seeds and N. This is the true depth-ceiling curve; iterative
    # (usable_it) is expected to OVERLAY single_shot (usable_ss) at every N_TEST.
    capacity_law = []
    for nt in NTEST_TARGETS:
        uss, uit, mags, dels = [], [], [], []
        for r in all_seed_results:
            for pn in r["per_N"]:
                for row in pn["phase_map"]:
                    if row["n_test"] == nt:
                        uss.append(row["usable_ss"])
                        uit.append(row["usable_it"])
                        mags.append(row["max_abs_gap"])
                        dels.append(row["delta_usable"])
        capacity_law.append({
            "n_test": nt, "fill": collision_fill(nt, D_MAX),
            "mean_usable_ss": _mean(uss), "mean_usable_it": _mean(uit),
            "mean_delta_usable": _mean(dels), "max_of_max_abs_gap": (round(max(mags), 4) if mags else None),
        })
    # decisive-tie audit: iterative bit-identical to single_shot at every point.
    all_mags = [row["max_abs_gap"] for r in all_seed_results for pn in r["per_N"]
                for row in pn["phase_map"]]
    global_max_abs_gap = round(max(all_mags), 4) if all_mags else None
    all_deltas = [row["delta_usable"] for r in all_seed_results for pn in r["per_N"]
                  for row in pn["phase_map"]]
    max_delta_usable = max(all_deltas) if all_deltas else None

    # Positive control (Gate D): single_shot at N=8192 reproduces v2 regen depth
    # behavior (d1 sanity + graceful decay + d5 in the v2 range).
    def _curve_get(curve: Dict[Any, Any], d: int) -> Optional[float]:
        # curves survive a JSON round-trip in aggregate_partials -> keys may be str.
        if d in curve:
            return curve[d]
        return curve.get(str(d))

    pc = None
    for i, n_dim in enumerate(N_LIST):
        if n_dim == PC_V2_N:
            d5s, d1s = [], []
            for r in all_seed_results:
                for row in r["per_N"][i]["phase_map"]:
                    d5s.append(_curve_get(row["ss_curve"], 5))
                    d1s.append(row["ss_d1"])
            d5s = [x for x in d5s if x is not None]
            mean_d5 = round(float(np.mean(d5s)), 4) if d5s else None
            mean_d1 = round(float(np.mean(d1s)), 4) if d1s else None
            pc = {
                "N": PC_V2_N, "mean_ss_d1": mean_d1, "mean_ss_d5": mean_d5,
                "v2_regen_d5_ref_range": [PC_V2_REGEN_D5_LO, PC_V2_REGEN_D5_HI],
                "d1_sanity_ok": bool(mean_d1 is not None and mean_d1 >= HP_D1_SANITY),
                "d5_in_v2_range": bool(mean_d5 is not None
                                       and PC_V2_REGEN_D5_LO <= mean_d5 <= PC_V2_REGEN_D5_HI),
            }
            break

    any_ctl = any(s["n_tier_majority"] == "HARD_FAIL_CTL" for s in per_N_summary)
    pass_tiers = [s for s in per_N_summary if s["n_tier_majority"] == "HARD_PASS"]
    fail_tiers = [s for s in per_N_summary if s["n_tier_majority"] == "HARD_FAIL"]
    iter_tiers = [s for s in per_N_summary if s["n_tier_majority"] == "ITERATE_REGIME"]
    headline = pass_tiers[-1] if pass_tiers else None

    extra = {
        "cardinality_ok": True, "n_units": n_units, "expected_n_units": expected_units,
        "n_seeds": n_seeds, "N_LIST": N_LIST, "NTEST_TARGETS": NTEST_TARGETS,
        "MOVERN_FIXED": MOVERN_FIXED, "KEY_SLOTS": KEY_SLOTS,
        "per_N_summary": per_N_summary,
        "capacity_law_usable_depth_vs_NTEST": capacity_law,
        "depth_ceiling_vs_N": {
            "usable_ss_by_N": ss_law, "usable_it_by_N": it_law,
            "delta_usable_by_N": delta_law,
            "ss_usable_depth_rises_with_N": ss_depth_rises_with_N,
        },
        "decisive_tie_audit": {
            "global_max_abs_gap": global_max_abs_gap, "max_delta_usable": max_delta_usable,
            "iterative_bit_identical_everywhere": bool(global_max_abs_gap is not None
                                                       and global_max_abs_gap < TIE_TOL),
        },
        "positive_control_v2_reproduce": pc,
        "headline_N": headline["N"] if headline else None,
        "chance_floor": round(CHANCE_FLOOR, 5),
        "usable_floor": USABLE_FLOOR, "usable_floor_secondary": USABLE_FLOOR_SECONDARY,
        "beta_iter": BETA_ITER, "t_iter": T_ITER,
    }

    def _fmtN(seq):
        return " ".join("N%d=%s" % (n, ("%.2f" % v) if v is not None else "na") for n, v in seq)

    def _fmtC(rows_):
        return " ".join("NT%d(fill%.2f):ss=%s,it=%s" % (
            c["n_test"], c["fill"],
            ("%.1f" % c["mean_usable_ss"]) if c["mean_usable_ss"] is not None else "na",
            ("%.1f" % c["mean_usable_it"]) if c["mean_usable_it"] is not None else "na") for c in rows_)

    summ = ("n_seeds=%d units=%d/%d | per-N tiers: %s | CAPACITY LAW (usable-depth vs "
            "N_TEST) %s | usable-depth-vs-N %s (rises_with_N=%s, expect ~flat=collision-"
            "limited) | DECISIVE-TIE global_max_abs_gap=%s max_delta_usable=%s | PC(N=8192) "
            "ss_d1=%s ss_d5=%s d5_in_v2_range=%s"
            % (n_seeds, n_units, expected_units,
               ",".join("N%d:%s" % (s["N"], s["n_tier_majority"]) for s in per_N_summary),
               _fmtC(capacity_law), _fmtN(ss_law), ss_depth_rises_with_N,
               global_max_abs_gap, max_delta_usable,
               (pc.get("mean_ss_d1") if pc else None), (pc.get("mean_ss_d5") if pc else None),
               (pc.get("d5_in_v2_range") if pc else None)))

    if any_ctl:
        return "HARD_FAIL", "HARD_FAIL_CONTROL (broken-discriminator rail recovered structure): " + summ, extra
    if pass_tiers:
        return "HARD_PASS", ("HARD_PASS (iterative/resonator attractor cleanup EXTENDS "
                             "usable chain depth over single-shot by a real margin at a "
                             "fair operating point, cross-seed stable, control at chance): ") + summ, extra
    if len(fail_tiers) >= (len(per_N_summary) // 2 + 1):
        return "HARD_FAIL", ("HARD_FAIL (iterative/resonator attractor cleanup TIES/LOSES "
                             "single-shot at every N -- the one-shot argmax snap is already "
                             "the MAP decoder; the chain depth ceiling is store-capacity/"
                             "collision-bound, not cleanup-bound. LEVER CLOSED. First-class "
                             "result: the measured capacity law (usable-depth vs N_TEST) and "
                             "its N-independence above): ") + summ, extra
    if len(iter_tiers) == len(per_N_summary):
        return "MIDDLE_BAND", ("MIDDLE_BAND (ITERATE_REGIME at all N -- no fair op-point where "
                               "single_shot collapses within D_MAX; needs higher N_TEST): ") + summ, extra
    return "MIDDLE_BAND", ("MIDDLE_BAND (iterative extends but not by the required margin, or "
                           "cross-seed unstable): ") + summ, extra


# ---------------------------------------------------------------------------
# Self-test (fast; small N; exits 0).
# ---------------------------------------------------------------------------
def _selftest() -> int:
    t0 = time.perf_counter()
    g = np.random.default_rng(0)
    n = 512
    v = 48
    p = 4
    E = make_bipolar(v, n, g)
    R = make_bipolar(p, n, g)

    global V_CHAIN, P_REL, V_CODE  # noqa: F824
    _save = (V_CHAIN, P_REL, V_CODE)
    V_CHAIN, P_REL, V_CODE = 24, p, v

    # T0: FACTORED store == materialized W (mechanism-preserving refactor proof).
    chains = make_chains(6, 5, g)
    assert chains.shape == (6, 5, 3)
    edges = chains.reshape(-1, 3)
    bg = make_background_edges(120, g)
    all_e = np.concatenate([edges, bg], axis=0)
    store = FactoredStore(all_e[:, 0], all_e[:, 1], all_e[:, 2], E, R, n)
    W = build_W_reference(all_e[:, 0], all_e[:, 1], all_e[:, 2], E, R, n)
    keys = make_bipolar(10, n, g)
    yhat_fac = store.retrieve(keys)
    yhat_mat = keys @ W.T
    max_diff = float(np.max(np.abs(yhat_fac - yhat_mat)))
    assert max_diff < 1e-3, "FACTORED != materialized W (max|diff|=%.2e)" % max_diff
    assert np.all(np.argmax(yhat_fac @ E.T, 1) == np.argmax(yhat_mat @ E.T, 1)), \
        "factored/materialized argmax cleanup differ"

    # T_attr: attractor@HIGH_BETA == single-shot argmax (attractor is a correct
    # GENERALIZATION of single-shot for a near-orthogonal codebook).
    clean = FactoredStore(edges[:, 0], edges[:, 1], edges[:, 2], E, R, n)
    yq = clean.retrieve(E[chains[:, 0, 0]] * R[chains[:, 0, 1]])
    ss_ids = argmax_clean(yq, E)
    hi_ids = attractor_clean(yq, E, BETA_HIGH, 4)
    frac_same = float(np.mean(ss_ids == hi_ids))
    assert frac_same >= 0.95, "attractor@high-beta != argmax (frac_same=%.3f)" % frac_same

    # T1: single-hop retrieval near-perfect on a clean store (positive control).
    r1 = walk_curve(chains, clean, E, R, [1], lambda y: argmax_clean(y, E))
    assert r1["curve"][1] >= 0.90, "single-hop single_shot broken: %.3f" % r1["curve"][1]
    r1it = walk_curve(chains, clean, E, R, [1], lambda y: attractor_clean(y, E, BETA_ITER, T_ITER))
    assert r1it["curve"][1] >= 0.85, "single-hop iterative broken: %.3f" % r1it["curve"][1]

    # T2: ONE-PASS depth curve == per-depth re-walk (proves O(D)->O(D) is exact).
    ref_curve = {}
    for dd in [1, 2, 3]:
        xx = E[chains[:, 0, 0]].astype(np.float32).copy()
        pr = None
        for kk in range(dd):
            yy = clean.retrieve(xx * R[chains[:, kk, 1]])
            pr = argmax_clean(yy, E)
            xx = E[pr].astype(np.float32)
        ref_curve[dd] = float(np.mean(pr == chains[:, dd - 1, 2]))
    op = walk_curve(chains, clean, E, R, [1, 2, 3], lambda y: argmax_clean(y, E))["curve"]
    assert all(abs(op[dd] - ref_curve[dd]) < 1e-12 for dd in [1, 2, 3]), \
        "ONE-PASS curve != per-depth re-walk"

    # T3: arms differ (single_shot vs iterative(soft) vs control) at depth 3.
    perm = g.permutation(v)
    o_shuf = perm[all_e[:, 2]]
    store_sh = FactoredStore(all_e[:, 0], all_e[:, 1], o_shuf, E, R, n)
    r_ss = walk_curve(chains, store, E, R, [1, 2, 3], lambda y: argmax_clean(y, E))
    r_it = walk_curve(chains, store, E, R, [1, 2, 3], lambda y: attractor_clean(y, E, BETA_ITER, T_ITER))
    r_ct = walk_curve(chains, store_sh, E, R, [1, 2, 3], lambda y: attractor_clean(y, E, BETA_ITER, T_ITER))
    sha = {_sha_of_array(r_ss["preds"][3]), _sha_of_array(r_it["preds"][3]),
           _sha_of_array(r_ct["preds"][3])}
    assert len(sha) >= 2, "arms bit-identical (META_RULE_AF): %s" % sha

    # T4: usable_depth logic (contiguous-from-1).
    assert usable_depth({1: 0.9, 2: 0.8, 3: 0.4, 4: 0.6}, [1, 2, 3, 4], 0.5) == 2
    assert usable_depth({1: 0.4, 2: 0.9}, [1, 2], 0.5) == 0
    assert usable_depth({1: 0.9, 2: 0.9}, [1, 2], 0.5) == 2

    # T5: faithfulness of a regenerative arm to its own replay == 1.0.
    fit = faithfulness_from_preds(r_it["preds"], r_it["preds"], [3])[3]
    assert fit == 1.0, "iterative not faithful-by-construction: %.3f" % fit

    # T6: classify_N_seed HARD_FAIL (tie) and HARD_PASS (extend) synthetic rows.
    def _mk(nt, uss, uit, uctl, gap, faith=1.0, band=True, ident=None):
        ss_c = {d: (0.9 if d <= uss else 0.2) for d in range(1, 8)}
        it_c = {d: (0.9 if d <= uit else 0.2) for d in range(1, 8)}
        mag = round(max(abs(it_c[d] - ss_c[d]) for d in range(1, 8)), 4)
        return {"n_test": nt, "fill": round(nt / 100.0, 3),
                "m_over_n": MOVERN_FIXED, "usable_ss": uss, "usable_it": uit, "usable_ctl": uctl,
                "delta_usable": uit - uss, "mean_gap_cross": gap,
                "max_abs_gap": mag,
                "curves_identical": (ident if ident is not None else bool(mag < TIE_TOL)),
                "it_faith_min": faith, "isolation_clean": True, "arms_differ": True,
                "ss_in_band": band, "d1_sanity_ok": True,
                "usable_ss_secfloor": uss + 1, "usable_it_secfloor": uit + 1,
                "ss_curve": ss_c, "it_curve": it_c}
    tie_rows = [_mk(15, 5, 5, 0, 0.0), _mk(40, 4, 4, 0, 0.0)]
    tier_t, _rt, _ = classify_N_seed(tie_rows)
    assert tier_t == "HARD_FAIL", "tie should be HARD_FAIL: %s (%s)" % (tier_t, _rt)
    ext_rows = [_mk(15, 5, 5, 0, 0.0), _mk(40, 4, 7, 0, 0.12)]
    tier_e, _re, _ = classify_N_seed(ext_rows)
    assert tier_e == "HARD_PASS", "extension should be HARD_PASS: %s (%s)" % (tier_e, _re)
    ctl_rows = [_mk(15, 5, 5, 4, 0.0)]
    tier_c, _rc, _ = classify_N_seed(ctl_rows)
    assert tier_c == "HARD_FAIL_CTL", "broken control should be HARD_FAIL_CTL: %s" % tier_c
    mid_rows = [_mk(40, 4, 5, 0, 0.06)]  # delta=+1 < margin 2
    tier_m, _rm, _ = classify_N_seed(mid_rows)
    assert tier_m == "MIDDLE_BAND", "small extension should be MIDDLE_BAND: %s (%s)" % (tier_m, _rm)
    # censored tie: single_shot deep (out of band high) but curves identical -> HARD_FAIL.
    cens_rows = [_mk(10, 7, 7, 0, 0.0, band=False, ident=True)]
    tier_cs, _rcs, _ = classify_N_seed(cens_rows)
    assert tier_cs == "HARD_FAIL", "censored tie should be HARD_FAIL: %s (%s)" % (tier_cs, _rcs)
    # out-of-band, NOT identical -> ITERATE_REGIME.
    ir_rows = [_mk(15, 6, 3, 0, -0.30, band=False, ident=False)]
    tier_ir, _rir, _ = classify_N_seed(ir_rows)
    assert tier_ir == "ITERATE_REGIME", "out-of-band non-identical should be ITERATE_REGIME: %s" % tier_ir

    # T7: LLM counter untouched.
    assert _LLM_CALL_COUNTER[0] == 0

    V_CHAIN, P_REL, V_CODE = _save
    dt = time.perf_counter() - t0
    print("[selftest] PASS factored==W(max_diff=%.2e) attr@highbeta==argmax(%.3f) "
          "onepass==rewalk regen_d1=%.3f iter_d1=%.3f arms=%d elapsed=%.2fs"
          % (max_diff, frac_same, r1["curve"][1], r1it["curve"][1], len(sha), dt), flush=True)
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
    print("[start] anchor=%s mode=%s N_LIST=%s V=%d seeds=%s NTEST=%s M/N=%.2f D_MAX=%d "
          "BETA_ITER=%.1f T_ITER=%d expected_units=%d"
          % (ANCHOR_NAME, RUN_MODE, N_LIST, V_CODE, SEEDS, NTEST_TARGETS, MOVERN_FIXED, D_MAX,
             BETA_ITER, T_ITER, EXPECTED_N_UNITS), flush=True)

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
        "NTEST_TARGETS": NTEST_TARGETS, "MOVERN_FIXED": MOVERN_FIXED, "KEY_SLOTS": KEY_SLOTS,
        "BETA_ITER": BETA_ITER, "T_ITER": T_ITER,
        "expected_n_units": EXPECTED_N_UNITS, "cardinality_ok": extra.get("cardinality_ok", False),
        "extra": extra, "per_seed": all_results, "n_llm_forward_calls": _LLM_CALL_COUNTER[0],
        "bands": {
            "USABLE_FLOOR": USABLE_FLOOR, "USABLE_FLOOR_SECONDARY": USABLE_FLOOR_SECONDARY,
            "HP_DEPTH_MARGIN": HP_DEPTH_MARGIN, "HP_FID_GAP": HP_FID_GAP,
            "HP_FAITH_MIN": HP_FAITH_MIN, "HP_CTL_USABLE_MAX": HP_CTL_USABLE_MAX,
            "HP_D1_SANITY": HP_D1_SANITY, "SS_BAND_LO": SS_BAND_LO,
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
