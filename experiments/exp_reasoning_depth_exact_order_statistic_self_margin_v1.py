"""exp_reasoning_depth_exact_order_statistic_self_margin_v1

EXACT SELF-MARGIN for a HEADLINE capability (reasoning-depth): the substrate predicts
its OWN usable reasoning depth (the collision-bound ceiling) in closed form, via the
EXACT capture partial-credit order statistic, vs the loose occupancy-binary baseline.

Extends the exact-order-statistic self-margin CG pattern from CODEBOOKS
(exp_rns_subblock_margin_exact_prefactor_v2 HARD_PASS; exp_fhrr_bundle_capacity_exact_margin_v1
HARD_PASS) UP one level of the composition stack: per-hop decode margin -> multi-hop chain
survival. Reuses the measurement machinery of the landed reasoning-depth cell
(exp_reasoning_depth_keyslots_sharding_v1, MIDDLE_BAND) VERBATIM (factored Hebbian store,
single-shot argmax cleanup -- PROVEN optimal / MAP by exp_cortex_iterative_attractor_cleanup_
depth_ceiling_v1, so cleanup-type is FIXED and NOT reopened here) and adds ONE new PREDICTION
arm: the exact per-hop retrieval-success probability as a Poisson-occupancy-averaged capture
order statistic, composed across depth via the series-reliability law D* = ln(FLOOR)/ln(p_hop).

--------------------------------------------------------------------------------
WHY the landed reasoning-depth cell was MIDDLE_BAND (the model, not the mechanism)
--------------------------------------------------------------------------------
The landed cell's own pre-registered predictor is OCCUPANCY-BINARY: it treats a key-slot
collision as a GUARANTEED failure -> p_clean = 1 - collision_frac, D* = ln(0.5)/ln(1-cf).
That is structurally the SAME mistake the RNS union-bound and FHRR asymptotic controls make
(treating "shares a slot with a competitor" as certain failure rather than computing the
probability of still WINNING the argmax). MEASURED@landed: this occupancy-binary predictor
UNDER-predicts usable depth by a systematic geom-mean factor 2.02x (CV 0.156, 25 non-censored
op-points; MEASURED@author off-disk recompute vs
data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json:extra.per_op).

--------------------------------------------------------------------------------
THE FIX (the new prediction arm; a genuine order-statistic member of the RNS/FHRR family)
--------------------------------------------------------------------------------
A collided key slot is a SUPERPOSITION of c stored objects (c = 1 + number of OTHER distinct
objects at the slot). Single-shot argmax recovers the TRUE one with a graceful "capture"
probability, NOT 0. The EXACT capture order statistic (THEORETICAL@capture effect: Roberts
1975; Arnbak & Van Blitterswijk 1987 IEEE JSAC; order statistics as in Hajek ECE361 L8 /
Proakis Ch.4 M-ary family):
    P_capture(c, mu, D) = E_z[ Phi(z)^(c-1) * Phi(mu + z)^D ],  z ~ N(0,1)
where the c-1 co-colliding objects share the SAME elevated mean (they are stored at the same
key, each scores ~ signal) and compete by symmetry, and the D = V_CODE-1 non-colliding
codewords are zero-mean distractors at SNR mu. At the substrate's operating SNR
mu = signal/noise ~ N/sqrt(M) ~ sqrt(N) ~ 90-128 (SATURATED; the distractor factor
Phi(mu+z)^D == 1 to ~1000 decimals), this reduces EXACTLY to E_z[Phi(z)^(c-1)] = 1/c -- the
capture-partial-credit probability. THEORETICAL, parameter-free. Poisson-average over slot
multiplicity: p_hop = E_{c=1+Poisson(fill)}[ P_capture(c, mu, D) ], fill = -ln(1-collision_frac).
Compose across depth: D*_exact = ln(FLOOR) / ln(p_hop).

Off-disk cheap decisive test (zero new trials, MEASURED@author vs landed per_op):
    occupancy-binary (loose control):  measured/pred geom-mean 2.02x  (CV 0.156)  [biased]
    capture order statistic (exact):   measured/pred geom-mean 0.99x  (CV 0.104)  [unbiased]
    per-op exact ratio-error range 0.84-1.23x (ALL 25 non-censored < the 1.5x CG bar).
The exact model REMOVES the loose model's systematic +102% under-prediction. This FULL cell
re-MEASURES the reasoning-depth surface FRESH (5 seeds {7,13,19,23,29}, machinery reused
VERBATIM) and computes both predictions against the fresh measurement -> a first-class,
independently-verified metrics.json entry (not a notes-only recompute).

--------------------------------------------------------------------------------
ARMS (per (N, seed, N_TEST); measurements PAIRED by identical chains where compared)
--------------------------------------------------------------------------------
6 measurement arms span 5 collision/fill levels + 1 broken-structure control, giving many
op-points for the prediction test (identical to the landed cell's arm set):
  baseline / keyslots_2x / keyslots_4x / shard_2 / shard_4  -- 5 fill levels.  [MEASUREMENT]
  control (shuffled objects) -- structure destroyed -> usable ~ 0.             [DISCRIMINATOR-FIRES CTL]
Per NON-control arm, per op-point:
  measured usable_depth (fresh)                                                [MECHANISM]
  D*_exact  = capture-order-statistic prediction (the NEW discriminator)       [PREDICTION]
  D*_loose  = occupancy-binary prediction (ln(0.5)/ln(1-collision_frac))       [CONTROL/BASELINE, ~2x off]
The exact arm is the substrate predicting its OWN usable reasoning depth EXACTLY; the loose
occupancy-binary arm is the retained control it improves on (expected to stay ~2x off, exactly
like the RNS union-bound and FHRR asymptotic controls).

--------------------------------------------------------------------------------
BANDS (aggregate over the non-censored, non-control op-points; ratio = measured/prediction)
--------------------------------------------------------------------------------
Ratio-error(r) = max(r, 1/r) (multiplicative, >=1). Op-point = (N, N_TEST, arm) aggregated
over seeds; CENSORED (measured usable >= D_MAX-0.5, a lower bound) op-points are EXCLUDED from
the ratio gates (reported separately).
  HARD_PASS (promotes reasoning-depth self-prediction to a CG-candidate, parallel to RNS/FHRR):
    - exact per-op ratio-error <= HP_RATIO_MAX (1.5x) at ALL non-censored op-points, AND
    - exact aggregate mean-ratio in [HP_BIAS_LO, HP_BIAS_HI] = [0.80, 1.25] (UNBIASED), AND
    - loose control stays biased: loose aggregate mean-ratio >= HP_LOOSE_BIAS_MIN (1.7x) AND
      loose under-predicts (ratio>1) at >= HP_LOOSE_DIR_FRAC (0.80) of op-points, AND
    - aggregate relative improvement loose_gm_ratioerr / exact_gm_ratioerr >= REL_IMPROVE_MIN
      (1.5x), AND
    - cross-seed stability: CV of per-seed exact ratio-error <= HP_CV_MAX (0.15) aggregate, AND
    - discriminator-fires control: shuffled-control usable_depth <= HP_CTL_USABLE_MAX (1).
  HARD_FAIL (honest ACCEPT-boundary -- reasoning-depth resists exact closed-form self-prediction):
    - exact aggregate mean-ratio OUTSIDE [0.60, 1.70] (exact biased too -> capture model wrong), OR
    - exact per-op ratio-error > HF_RATIO_MAX (2.0x) at ANY non-censored op-point, OR
    - exact cross-seed CV > HF_CV_MAX (0.25).
  HARD_FAIL_CTL: shuffled control usable_depth > 1 (broken rail recovers structure).
  DISCRIMINATOR_DID_NOT_FIRE: loose aggregate mean-ratio < NOFIRE_LOOSE_MIN (1.4x) -> the loose
    baseline is NOT actually loose at this regime, so the exact-vs-loose contrast is vacuous
    (respec; NOT a refutation of the exact model).
  MIDDLE_BAND: exact tightens vs loose (mean-ratio closer to 1 than loose) but misses one of the
    HARD_PASS sub-gates (per-op <=1.5x everywhere / CV<=0.15 / bias band).

--------------------------------------------------------------------------------
CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (AF): baseline final-preds vs each mechanism arm
#   hash-distinct; exact-prediction surface vs loose-prediction surface hash-distinct.
# - final_metrics_atomicity = tmp_replace (os.replace of metrics.json.tmp).
# - except SystemExit: raise BEFORE except Exception (no BaseException; grep-clean).
# - crlb/discriminator_reachability: this is a PREDICTION-MATCH test. The measured usable_depth
#   spans ~3.2 (baseline, high fill) to censored-at-D_MAX (low-fill 4x arms), richly bracketing
#   the depth window. mu = N/sqrt(M) ~ 90-128 SATURATED (asserted >= 40 in formula_selftest) ->
#   the distractor factor is provably ~1 and the exact model reduces to the parameter-free
#   Poisson-averaged capture 1/c. discriminator_reachability: exact per-op ratio-error MEASURED@
#   author off-disk in [0.84,1.23] (all < 1.5x) while loose stays [1.46,2.80]. HP reachable.
# - baseline_in_band (AG): this is a prediction-match test, not a difficulty baseline. The
#   shuffled control is a declared must-collapse CTL (usable ~ 0), exempt from the in-band rule.
#   The loose occupancy-binary arm is a live CONTROL/BASELINE (~2x off); the exact arm is the
#   MECHANISM. The discriminator (exact-vs-loose tightness) does NOT saturate at scale (the loose
#   bias is a fixed ~2x multiplicative offset independent of N -- MEASURED N-independent).
# - discriminator survives scale: the exact prediction is a DETERMINISTIC closed form; only the
#   measured usable_depth carries seed noise. The 2.02x->0.99x closure is already verified
#   against the LANDED 8192+16384 measured surface (option B). Smoke re-fires it fresh at N=8192.
# - HARD_PASS strictly above floor: exact ratio-error <= 1.5x at EVERY op-point AND unbiased
#   (mean-ratio in [0.80,1.25]) AND >= 1.5x tighter than loose in aggregate (deflated bars above
#   the 0.84-1.23 / 0.99x / 1.84x MEASURED off-disk retrospective).
# - HP_SCOPE per-arm: HARD_PASS ratio gates apply to the 5 non-control MEASUREMENT arms; the
#   shuffled control gets ONLY the usable<=1 discriminator-fires gate (never a ratio gate).
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = seeds x N x N_TEST. Verdict gates on count.
# - per-unit failure-class instrumentation (META_RULE_J; no bare except).
# - calibration_check = default_ok_for_this_regime: the exact formula is parameter-free (mu
#   derived from N,M physics; D=V_CODE-1 fixed; 64-pt GH matches RNS/FHRR). NOT tuned-for-PASS.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in prereg + comments.
# - progress_logging = line_buffered_stdout + print(flush=True) (timeout_s >= 1800).
# - start_marker + crash_diagnostic + heartbeat (defensive error checking; 4 patterns).
# - positive_control (Gate D): the measurement machinery IS the landed reasoning cell's, reused
#   VERBATIM; the fresh baseline reproduces the collision-bound depth curve (d1>=0.80, graceful
#   decay) at the SAME regime -> validates the reused scaffold; off-disk retrospective (optional,
#   if landed metrics present) reproduces the loose-2.02x / exact-0.99x split within tolerance.
#
# USER-LOCKED: monitor-not-control. The cell only REPORTS the exact reasoning-depth prediction vs
#   the measured depth in its own metrics.json. It NEVER resizes key-slots, reshards, edits a
#   landed cell's config, or triggers a rebuild -- a REPORTING refinement (a tighter, unbiased
#   number), never a config-changing action. NOT self-improvement. Brain-grounding: HONESTLY a
#   metacognitive confidence / error-monitoring signal by shared-math analogy (ACC-adjacent
#   monitor side, Nelson & Narens 1990) -- mechanism, NOT a claim of task-level reasoning
#   competence, NOT autonomous self-improvement.
#
# Compute architecture: SEQUENCE-DEPENDENT CPU (each hop depends on hop k-1 -- genuine chained-
#   retrieval sequential dependency exemption) + the cell IS the substrate cleanup primitive being
#   validated. Storage = MIXED (bundled-Hebbian per shard; sharding is a swept fill axis, per
#   META_STORAGE_STRATEGY exemption (b)). Factored store (no NxN materialization), M-chunked numpy
#   matmul. The prediction arm is numpy Gauss-Hermite quadrature (no GPU, no scipy, no torch, no
#   LLM). Self-contained (synthetic chains; no pool/re-encode/cert_ledger dependency -> clean
#   remote gate, NON-PARKED, zero referent).
#
# PROT-018: no _n<N> suffix (N-independent collision law; N is a confirm axis, not the axis).
# ASCII-only; no unicode; no emojis; no em-dashes. Author: exp_dev 2026-07-06.
# Run: python experiments/exp_reasoning_depth_exact_order_statistic_self_margin_v1.py
#      [--self-test | --smoke]  (bare / runner-injected HDLAB_RUN_MODE=full -> full)
"""
from __future__ import annotations

import sys

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
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "reasoning_depth_exact_order_statistic_self_margin_v1"
_LLM_CALL_COUNTER = [0]  # substrate-only assert: must stay 0

# ---------------------------------------------------------------------------
# CLI + RUN_MODE (defaults to full; --smoke / --self-test flip; runner injects
# HDLAB_RUN_MODE=full and invokes bare, so env is the real channel)
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
# Config (codebook geometry reused VERBATIM from the landed reasoning cell)
# ---------------------------------------------------------------------------
USABLE_FLOOR = 0.50            # D* floor: usable while fidelity >= this (matches landed cell)

V_CODE = 512                   # total node codebook (cleanup argmax over all V_CODE rows)
V_CHAIN = 256                  # chain nodes drawn from [0, V_CHAIN); background from [V_CHAIN, V_CODE)
BASELINE_P = 8
P_REL_MAX = 32
MOVERN_FIXED = 1.0             # background fills to M/N=1 (crosstalk regime = prior regime)

# Mechanism arms (label, p_rel, n_shards, shuffle_objects, reuse_base_chains). Identical to landed.
ARMS: List[Dict[str, Any]] = [
    {"label": "baseline",    "p_rel": 8,  "shards": 1, "shuffle": False, "reuse_base": True},
    {"label": "keyslots_2x", "p_rel": 16, "shards": 1, "shuffle": False, "reuse_base": False},
    {"label": "keyslots_4x", "p_rel": 32, "shards": 1, "shuffle": False, "reuse_base": False},
    {"label": "shard_2",     "p_rel": 8,  "shards": 2, "shuffle": False, "reuse_base": True},
    {"label": "shard_4",     "p_rel": 8,  "shards": 4, "shuffle": False, "reuse_base": True},
    {"label": "control",     "p_rel": 32, "shards": 1, "shuffle": True,  "reuse_base": False},
]
BASE_ARM = "baseline"
MECH_ARMS = ["baseline", "keyslots_2x", "keyslots_4x", "shard_2", "shard_4"]  # the 5 MEASUREMENT arms tested by ratio
CTL_ARM = "control"


def eff_key_capacity(p_rel: int, shards: int) -> int:
    return V_CHAIN * p_rel * shards


def eff_fill(n_test: int, d_max: int, p_rel: int, shards: int) -> float:
    """Effective chain-edge fill per store = (N_TEST/S)*D_MAX / (V_CHAIN*P_REL)."""
    return round((n_test / float(shards)) * d_max / float(V_CHAIN * p_rel), 4)


if RUN_MODE == "self_test":
    N_LIST = [512]
    NTEST_TARGETS = [8]
    SEEDS = [0]
    D_MAX = 6
    DEPTHS = [1, 2, 3, 4, 5, 6]
elif RUN_MODE == "smoke":
    # Discriminator preview AT FULL N=8192 (option A/C). One difficulty N_TEST=32 spreads the 5
    # measurement arms across fills 0.07-0.28 (all non-censored at NT=32) so the exact-vs-loose
    # ratio discriminator fires; 3 seeds {7,13,19} (RNS/FHRR smoke precedent) for cross-seed cv.
    N_LIST = [8192]
    NTEST_TARGETS = [32]
    SEEDS = [7, 13, 19]
    D_MAX = 18
    DEPTHS = list(range(1, 19))
else:  # full
    # Fresh seeds {7,13,19,23,29} (RNS v2 / FHRR v1 CG precedent; distinct from landed {7,17,23,31,41}
    # -> independent re-measurement). N in {8192,16384} confirms N-independence of the depth law.
    N_LIST = [8192, 16384]
    NTEST_TARGETS = [24, 32, 40]
    SEEDS = [7, 13, 19, 23, 29]
    D_MAX = 18
    DEPTHS = list(range(1, 19))

# ---- Pre-registered ratio bands (aggregate over non-censored, non-control op-points) ----
CENSOR_MARGIN = 0.5            # op-point CENSORED if measured usable >= D_MAX - this (lower bound)
HP_RATIO_MAX = 1.5            # HARD_PASS: exact per-op ratio-error <= this at ALL non-censored op-points (CG bar)
HF_RATIO_MAX = 2.0            # HARD_FAIL: exact per-op ratio-error > this at ANY non-censored op-point
HP_BIAS_LO = 0.80            # HARD_PASS: exact aggregate mean-ratio >= this (unbiased)
HP_BIAS_HI = 1.25            # HARD_PASS: exact aggregate mean-ratio <= this (unbiased)
HF_BIAS_LO = 0.60            # HARD_FAIL: exact aggregate mean-ratio < this (biased -> model wrong)
HF_BIAS_HI = 1.70            # HARD_FAIL: exact aggregate mean-ratio > this (biased -> model wrong)
HP_LOOSE_BIAS_MIN = 1.70     # HARD_PASS: loose aggregate mean-ratio >= this (control stays biased -> discriminator exists)
HP_LOOSE_DIR_FRAC = 0.80     # HARD_PASS: fraction of op-points where loose under-predicts (ratio>1) >= this
NOFIRE_LOOSE_MIN = 1.40      # DISCRIMINATOR_DID_NOT_FIRE: loose mean-ratio < this -> loose not actually loose (respec)
REL_IMPROVE_MIN = 1.50       # HARD_PASS: loose_gm_ratioerr / exact_gm_ratioerr >= this (exact does genuine work)
HP_CV_MAX = 0.15             # HARD_PASS: aggregate cross-seed CV of per-seed exact ratio-error <= this
HF_CV_MAX = 0.25             # HARD_FAIL: aggregate cross-seed CV > this
HP_CTL_USABLE_MAX = 1        # discriminator-fires: shuffled control usable_depth <= this
HP_D1_SANITY = 0.80          # baseline single-hop store works (base d1 >= this; positive control)
MIN_NONCENSORED = {"smoke": 3, "full": 15}   # cardinality floor on non-censored op-points

# Smoke discriminator-fires bands (looser than FULL to tolerate reduced-seed measured-depth noise).
SMOKE_RATIO_MAX = 1.70       # smoke: exact per-op ratio-error <= this (fires; loose vs FULL 1.5x)
SMOKE_BIAS_LO = 0.75
SMOKE_BIAS_HI = 1.30
SMOKE_LOOSE_MIN = 1.50       # smoke: loose mean-ratio >= this (contrast exists)
SMOKE_REL_MIN = 1.30         # smoke: rel_improve >= this

MU_SATURATED_MIN = 40.0      # formula_selftest asserts mu >= this on the measurement grids (distractor factor ~1)
MEASUREMENT_N_REF = (8192, 16384)   # the real N values the cell runs VERDICTS on (smoke/full); mu ~ 90-128
                                    # (the self_test scaffold N=512 is integrity-only, never a prediction verdict)

CHANCE_FLOOR = 1.0 / V_CODE
EXPECTED_N_UNITS = len(SEEDS) * len(N_LIST) * len(NTEST_TARGETS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%s,V=%d,V_CHAIN=%d,BASE_P=%d,PMAX=%d,D_MAX=%d,MOVERN=%.2f,NTEST=%s,SEEDS=%s,"
    "RUN_MODE=%s,arms=%s,store=FACTORED_HEBBIAN_sharded,pred=capture_order_stat_GH64_vs_occupancy_binary,"
    "hardening=startmarker+crashdiag+heartbeat+AF+AH+AG"
) % (
    ANCHOR_NAME, "-".join(str(n) for n in N_LIST), V_CODE, V_CHAIN, BASELINE_P, P_REL_MAX,
    D_MAX, MOVERN_FIXED, "-".join(str(nt) for nt in NTEST_TARGETS),
    "-".join(str(s) for s in SEEDS), RUN_MODE, "-".join(a["label"] for a in ARMS),
)


# ---------------------------------------------------------------------------
# Defensive-error-checking helpers (start marker / crash / heartbeat)
# ---------------------------------------------------------------------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(out_dir: Path, run_mode: str, expected_units: int) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode, "expected_n_units": expected_units, "host": platform.node(),
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
# Substrate primitives (numpy, CPU) -- reused VERBATIM from the landed reasoning cell
# ---------------------------------------------------------------------------
def make_bipolar(rows: int, n: int, g: np.random.Generator) -> np.ndarray:
    """rows x n bipolar (+/-1) float32 codebook."""
    return (g.integers(0, 2, size=(rows, n)).astype(np.float32) * 2.0 - 1.0)


def _chunk_for(n_dim: int) -> int:
    """Edge-chunk size bounding a block to ~256 MB (adaptive to N)."""
    return max(256, (1 << 26) // n_dim)


class FactoredStore:
    """Hebbian associative store held as EDGE-INDEX lists (NEVER materializes N x N W).
    retrieve(x) = x @ W.T where W = sum_e outer(E[o_e], E[s_e]*R[p_e]) / N."""

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
        h = hashlib.sha256()
        h.update(self.s.tobytes()); h.update(self.p.tobytes()); h.update(self.o.tobytes())
        self._edge_key = h.hexdigest()[:16]

    def retrieve(self, keys: np.ndarray) -> np.ndarray:
        """keys: (B, N) -> yhat: (B, N)."""
        m = self.s.shape[0]
        out = np.zeros((keys.shape[0], self.n_dim), dtype=np.float32)
        if m == 0 or keys.shape[0] == 0:
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


class ShardedStore:
    """S FactoredStores + a per-chain shard_id. retrieve routes chain i -> shard i % S.
    Duck-typed retrieve(keys)->(B,N) so walk_curve consumes it identically to a FactoredStore."""

    __slots__ = ("stores", "shard_id", "n_dim")

    def __init__(self, stores: List[FactoredStore], shard_id: np.ndarray):
        assert len(stores) >= 1
        self.stores = stores
        self.shard_id = np.ascontiguousarray(shard_id.astype(np.int64))
        self.n_dim = stores[0].n_dim

    def retrieve(self, keys: np.ndarray) -> np.ndarray:
        out = np.zeros((keys.shape[0], self.n_dim), dtype=np.float32)
        for s_idx, st in enumerate(self.stores):
            idx = np.where(self.shard_id == s_idx)[0]
            if idx.size:
                out[idx] = st.retrieve(keys[idx])
        return out

    def sha_edges(self) -> str:
        h = hashlib.sha256()
        for st in self.stores:
            h.update(st.sha_edges().encode("ascii"))
        h.update(self.shard_id.tobytes())
        return h.hexdigest()[:16]


def build_W_reference(s: np.ndarray, p: np.ndarray, o: np.ndarray,
                      E: np.ndarray, R: np.ndarray, n_dim: int) -> np.ndarray:
    """Materialized Hebbian W (REFERENCE ONLY; self-test proves factored == this)."""
    if s.shape[0] == 0:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    k = E[s] * R[p]
    vv = E[o]
    return (vv.T @ k).astype(np.float32) / float(n_dim)


def argmax_clean(yhat: np.ndarray, E: np.ndarray) -> np.ndarray:
    """Single-shot cleanup: snap each row of yhat (B, N) to nearest atom -> ids (B,)."""
    return np.argmax(yhat @ E.T, axis=1)


def _sha_of_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]


def make_chains(n_chains: int, d_max: int, p_rel: int, g: np.random.Generator) -> np.ndarray:
    """(n_chains, d_max, 3) int (s, p, o) using chain-partition nodes + p_rel relations."""
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
            chains[c, i, 1] = int(g.integers(0, p_rel))
            chains[c, i, 2] = nodes[i + 1]
    return chains


def make_background_edges(m_bg: int, p_rel: int, g: np.random.Generator) -> np.ndarray:
    """(m_bg, 3) distractor edges with SOURCE in [V_CHAIN, V_CODE) (never key-collide with chain
    keys), object anywhere, relation in [0, p_rel)."""
    if m_bg <= 0:
        return np.zeros((0, 3), dtype=np.int64)
    s = g.integers(V_CHAIN, V_CODE, size=m_bg)
    p = g.integers(0, p_rel, size=m_bg)
    o = g.integers(0, V_CODE, size=m_bg)
    return np.stack([s, p, o], axis=1).astype(np.int64)


def empirical_collision_frac(chain_edges: np.ndarray, p_rel: int) -> float:
    """Fraction of chain edges whose (s,p) key maps to >= 2 DISTINCT objects (the ambiguity that
    limits chain depth). chain_edges: (M, 3) int."""
    m = chain_edges.shape[0]
    if m == 0:
        return 0.0
    key_to_objs: Dict[int, set] = {}
    for i in range(m):
        s = int(chain_edges[i, 0]); p = int(chain_edges[i, 1]); o = int(chain_edges[i, 2])
        key = s * p_rel + p
        key_to_objs.setdefault(key, set()).add(o)
    colliding = 0
    for i in range(m):
        s = int(chain_edges[i, 0]); p = int(chain_edges[i, 1])
        key = s * p_rel + p
        if len(key_to_objs[key]) >= 2:
            colliding += 1
    return round(colliding / float(m), 4)


def theoretical_collision_frac(m_edges: int, key_slots: int) -> float:
    """Occupancy model: prob an edge shares its slot with >= 1 other edge = 1-((K-1)/K)^(M-1)."""
    if m_edges <= 1 or key_slots <= 0:
        return 0.0
    return round(1.0 - ((key_slots - 1) / float(key_slots)) ** (m_edges - 1), 4)


# ---------------------------------------------------------------------------
# LOOSE control predictor (occupancy-binary; the landed cell's own predictor)
# ---------------------------------------------------------------------------
def predicted_usable_depth_loose(collision_frac: float, d_max: int) -> float:
    """CONTROL/BASELINE: occupancy-BINARY -> p_clean = 1 - collision_frac; a collision is a
    GUARANTEED failure. D* ~ ln(0.5)/ln(1-collision_frac). THEORETICAL@occupancy-binary (the
    landed reasoning cell's pre-registered predictor; MEASURED ~2.02x under-prediction)."""
    p_clean = max(1e-6, 1.0 - collision_frac)
    if p_clean >= 1.0 - 1e-9:
        return float(d_max)
    val = math.log(USABLE_FLOOR) / math.log(p_clean)
    return round(min(float(d_max), max(0.0, val)), 3)


# ---------------------------------------------------------------------------
# EXACT capture partial-credit order statistic (the NEW prediction arm)
# 64-pt Gauss-Hermite (weight exp(-x^2)); numpy-only, no scipy (mirrors RNS v2 / FHRR v1).
# ---------------------------------------------------------------------------
_GH_N = 64
_GH_NODES, _GH_WEIGHTS = np.polynomial.hermite.hermgauss(_GH_N)
_INV_SQRT_PI = 1.0 / math.sqrt(math.pi)
_SQRT2 = math.sqrt(2.0)


def _logPhi(a: float) -> float:
    """Stable log standard-normal CDF. Phi(a) = 0.5*erfc(-a/sqrt2)."""
    v = 0.5 * math.erfc(-a / _SQRT2)
    return math.log(v) if v > 0.0 else -1e300


def p_capture(c: int, mu: float, dstract: int) -> float:
    """EXACT capture order statistic for a key slot holding c equal-mean(mu) colliding signals
    competing among themselves AND against `dstract` zero-mean distractors:
        P = E_z[ Phi(z)^(c-1) * Phi(mu+z)^dstract ],  z ~ N(0,1)   (64-pt Gauss-Hermite)
    THEORETICAL@order-statistic (Hajek ECE361 L8 / Proakis Ch.4 family; capture effect Roberts
    1975 / Arnbak & Van Blitterswijk 1987). At high SNR (Phi(mu+z)^dstract -> 1) this reduces
    EXACTLY to E_z[Phi(z)^(c-1)] = 1/c (the capture-partial-credit probability)."""
    acc = 0.0
    for zi, wi in zip(_GH_NODES, _GH_WEIGHTS):
        z = _SQRT2 * zi
        lp_dist = _logPhi(mu + z)                 # beat each of dstract zero-mean distractors
        term = dstract * lp_dist
        if c > 1:
            term += (c - 1) * _logPhi(z)           # beat each of c-1 equal-mean co-colliders
        acc += wi * (math.exp(term) if term > -700.0 else 0.0)
    return _INV_SQRT_PI * acc


def p_hop_exact(fill: float, mu: float, dstract: int, cmax: int = 40) -> float:
    """Poisson-occupancy-averaged per-hop success: c = 1 + Poisson(fill).
    p_hop = E_{c=1+Poisson(fill)}[ P_capture(c, mu, dstract) ]. THEORETICAL@Poisson-occupancy."""
    if fill <= 0.0:
        return p_capture(1, mu, dstract)
    tot = 0.0
    logf = math.log(fill)
    for k in range(0, cmax + 1):
        logpk = -fill + k * logf - math.lgamma(k + 1)   # log Poisson pmf
        pk = math.exp(logpk)
        tot += pk * p_capture(1 + k, mu, dstract)
    return tot


def snr_mu(n_dim: int, m_edges: int) -> float:
    """Retrieval SNR mu = signal / noise_std. Signal (self inner-product of a matched key) = N;
    crosstalk noise variance ~ number of stored edges M (each non-matching edge contributes ~unit
    variance to a codeword score). mu = N / sqrt(max(M-1,1)) ~ sqrt(N). THEORETICAL@substrate
    physics (bipolar Hebbian factored store). In THIS regime mu ~ 90-128 (SATURATED: the
    distractor factor Phi(mu+z)^D == 1 to ~1000 decimals; the exact model reduces to capture 1/c)."""
    return float(n_dim) / math.sqrt(max(m_edges - 1, 1))


def predicted_usable_depth_exact(collision_frac: float, mu: float, dstract: int, d_max: int) -> float:
    """D*_exact = ln(FLOOR)/ln(p_hop_exact), p_hop from the Poisson-averaged capture order
    statistic given the store's (measured) collision fraction. THEORETICAL, parameter-free."""
    fill = -math.log(max(1e-9, 1.0 - collision_frac))
    p = p_hop_exact(fill, mu, dstract)
    p = min(max(p, 1e-9), 1.0 - 1e-12)
    if p >= 1.0 - 1e-9:
        return float(d_max)
    val = math.log(USABLE_FLOOR) / math.log(p)
    return round(min(float(d_max), max(0.0, val)), 3)


# ---------------------------------------------------------------------------
# Depth-curve walk + usable depth (reused VERBATIM)
# ---------------------------------------------------------------------------
def walk_curve(chains: np.ndarray, store: Any, E: np.ndarray, R: np.ndarray,
               depths: List[int], clean_fn: Callable[[np.ndarray], np.ndarray]) -> Dict[str, Any]:
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
        x = E[pred].astype(np.float32)
    return {"curve": curve, "preds": preds}


def usable_depth(curve: Dict[int, float], depths: List[int], floor: float) -> int:
    """Contiguous-from-1 sustained usable depth. 0 if even d1 below floor."""
    ud = 0
    for d in sorted(depths):
        if curve.get(d, 0.0) >= floor:
            ud = d
        else:
            break
    return ud


def crossing_depth(curve: Dict[int, float], depths: List[int], floor: float) -> float:
    """Continuous fidelity=floor crossing (linear interp); D_MAX if never crosses; 0 if d1 below."""
    ds = sorted(depths)
    if curve.get(ds[0], 0.0) < floor:
        return 0.0
    last_above = ds[0]
    for d in ds:
        if curve.get(d, 0.0) >= floor:
            last_above = d
        else:
            hi = curve.get(last_above, 0.0); lo = curve.get(d, 0.0)
            frac = (hi - floor) / (hi - lo) if hi > lo else 0.0
            return round(last_above + frac, 3)
    return float(ds[-1])  # censored: sustained to D_MAX


def build_arm_store(arm: Dict[str, Any], chains: np.ndarray, m_bg: int,
                    E: np.ndarray, R: np.ndarray, n_dim: int,
                    g: np.random.Generator) -> Tuple[Any, np.ndarray, np.ndarray, int]:
    """Returns (store, chain_edges, shard_id, max_edges_per_store). max_edges_per_store is the
    largest per-store edge count (drives the retrieval-SNR mu, worst-case over shards)."""
    p_rel = int(arm["p_rel"]); shards = int(arm["shards"])
    n_test = chains.shape[0]
    chain_edges = chains.reshape(-1, 3)
    bg = make_background_edges(m_bg, p_rel, g)

    if shards == 1:
        all_e = np.concatenate([chain_edges, bg], axis=0)
        o_col = all_e[:, 2]
        if arm["shuffle"]:
            perm = g.permutation(V_CODE)
            o_col = perm[all_e[:, 2]]
        store = FactoredStore(all_e[:, 0], all_e[:, 1], o_col, E, R, n_dim)
        return store, chain_edges, np.zeros(n_test, dtype=np.int64), int(all_e.shape[0])

    shard_id = np.arange(n_test, dtype=np.int64) % shards
    bg_split = np.array_split(bg, shards) if bg.shape[0] else [np.zeros((0, 3), np.int64)] * shards
    stores: List[FactoredStore] = []
    max_edges = 0
    for s_idx in range(shards):
        chain_idx = np.where(shard_id == s_idx)[0]
        ce = chains[chain_idx].reshape(-1, 3) if chain_idx.size else np.zeros((0, 3), np.int64)
        bgs = bg_split[s_idx]
        se = np.concatenate([ce, bgs], axis=0) if bgs.shape[0] else ce
        if se.shape[0] == 0:
            se = np.zeros((0, 3), np.int64)
        stores.append(FactoredStore(se[:, 0], se[:, 1], se[:, 2], E, R, n_dim))
        max_edges = max(max_edges, int(se.shape[0]))
    return ShardedStore(stores, shard_id), chain_edges, shard_id, max_edges


# ---------------------------------------------------------------------------
# One (N, seed, N_TEST) unit -> per-arm measured depth + exact/loose predictions + ratios
# ---------------------------------------------------------------------------
def run_unit(n_dim: int, seed: int, n_test: int, out_dir: Path,
             hb_state: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.perf_counter()
    chain_edge_count = n_test * D_MAX
    m_total_target = int(round(MOVERN_FIXED * n_dim))
    m_bg = max(0, m_total_target - chain_edge_count)
    dstract = V_CODE - 1

    g = np.random.default_rng(seed * 100003 + n_dim * 7 + n_test)
    E = make_bipolar(V_CODE, n_dim, g)
    R = make_bipolar(P_REL_MAX, n_dim, g)
    base_chains = make_chains(n_test, D_MAX, BASELINE_P, g)

    arm_results: Dict[str, Dict[str, Any]] = {}
    arm_preds_final: Dict[str, np.ndarray] = {}
    for arm in ARMS:
        label = arm["label"]; p_rel = int(arm["p_rel"]); shards = int(arm["shards"])
        if arm["reuse_base"]:
            chains = base_chains
        else:
            gg = np.random.default_rng(seed * 100003 + n_dim * 7 + n_test + hash(label) % 9973)
            chains = make_chains(n_test, D_MAX, p_rel, gg)

        store, chain_edges, shard_id, max_edges = build_arm_store(arm, chains, m_bg, E, R, n_dim, g)
        r = walk_curve(chains, store, E, R, DEPTHS, lambda y: argmax_clean(y, E))
        curve = {d: round(v, 4) for d, v in r["curve"].items()}
        ud = usable_depth(curve, DEPTHS, USABLE_FLOOR)
        xd = crossing_depth(curve, DEPTHS, USABLE_FLOOR)

        # collision fraction over CHAIN edges (sharded -> per-shard weighted average)
        if shards == 1:
            emp = empirical_collision_frac(chain_edges, p_rel)
        else:
            emps, wts = [], []
            for s_idx in range(shards):
                cidx = np.where(shard_id == s_idx)[0]
                ce = chains[cidx].reshape(-1, 3) if cidx.size else np.zeros((0, 3), np.int64)
                if ce.shape[0] == 0:
                    continue
                emps.append(empirical_collision_frac(ce, p_rel))
                wts.append(ce.shape[0])
            wsum = float(sum(wts)) if wts else 1.0
            emp = round(float(np.dot(emps, wts) / wsum), 4) if wts else 0.0

        mu = snr_mu(n_dim, max_edges)
        pred_loose = predicted_usable_depth_loose(emp, D_MAX)
        pred_exact = predicted_usable_depth_exact(emp, mu, dstract, D_MAX)

        # ratio = measured / prediction (only meaningful for non-control, non-censored)
        censored = bool(ud >= D_MAX - CENSOR_MARGIN)
        ratio_loose = (ud / pred_loose) if pred_loose > 1e-9 else None
        ratio_exact = (ud / pred_exact) if pred_exact > 1e-9 else None

        arm_preds_final[label] = r["preds"][DEPTHS[-1]]
        arm_results[label] = {
            "label": label, "p_rel": p_rel, "shards": shards,
            "eff_key_capacity": eff_key_capacity(p_rel, shards),
            "eff_fill": eff_fill(n_test, D_MAX, p_rel, shards),
            "usable_depth": ud, "crossing_depth": xd, "d1": curve[1],
            "collision_frac_emp": emp, "mu": round(mu, 2),
            "pred_usable_loose": pred_loose, "pred_usable_exact": pred_exact,
            "ratio_loose": (round(ratio_loose, 4) if ratio_loose is not None else None),
            "ratio_exact": (round(ratio_exact, 4) if ratio_exact is not None else None),
            "censored": censored, "store_sha": store.sha_edges(),
        }

    # arms-differ (META_RULE_AF): base must differ from every mechanism arm + control.
    shas = {lab: _sha_of_array(arm_preds_final[lab]) for lab in arm_preds_final}
    all_distinct = (len(set(shas.values())) == len(shas))
    base_sha = shas[BASE_ARM]
    other = [m for m in MECH_ARMS if m != BASE_ARM] + [CTL_ARM]
    base_differs = all(shas[m] != base_sha for m in other)

    base = arm_results[BASE_ARM]
    ctl = arm_results[CTL_ARM]

    for depth in DEPTHS:
        hb_state["unit"] += 1
        _heartbeat(out_dir, hb_state["unit"], hb_state["total"], hb_state["t0"],
                   extra={"N": n_dim, "seed": seed, "n_test": n_test, "depth": depth})

    print("  [N=%d seed=%d N_TEST=%d M/N~%.2f] base_ud=%d(d1=%.3f) ctl_ud=%d | ratios(exact/loose): "
          "%s | arms_distinct=%s"
          % (n_dim, seed, n_test, round((chain_edge_count + m_bg) / float(n_dim), 2),
             base["usable_depth"], base["d1"], ctl["usable_depth"],
             " ".join("%s=%.2f/%.2f%s" % (a, arm_results[a]["ratio_exact"] or 0.0,
                                          arm_results[a]["ratio_loose"] or 0.0,
                                          "C" if arm_results[a]["censored"] else "")
                      for a in MECH_ARMS),
             all_distinct), flush=True)

    return {
        "N": n_dim, "seed": seed, "n_test": int(n_test), "m_bg": int(m_bg),
        "m_over_n": round((chain_edge_count + m_bg) / float(n_dim), 4),
        "V": V_CODE, "V_CHAIN": V_CHAIN, "dstract": dstract, "run_mode": RUN_MODE,
        "arm_results": {a: {k: v for k, v in arm_results[a].items()} for a in arm_results},
        "arm_curves": {a: arm_results[a].get("curve", {}) for a in arm_results},
        "base_usable": base["usable_depth"], "base_d1": base["d1"],
        "base_d1_ok": bool(base["d1"] >= HP_D1_SANITY),
        "ctl_usable": ctl["usable_depth"],
        "arms_all_distinct": bool(all_distinct),
        "base_differs_from_others": bool(base_differs),
        "arm_shas": shas,
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "config_version": CONFIG_VERSION,
    }


# ---------------------------------------------------------------------------
# Per-seed driver
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    t0 = time.perf_counter()
    hb_total = len(N_LIST) * len(NTEST_TARGETS) * len(DEPTHS)
    hb_state = {"unit": 0, "total": hb_total, "t0": t0}
    units: List[Dict[str, Any]] = []
    for n_dim in N_LIST:
        for n_test in NTEST_TARGETS:
            row = run_unit(n_dim, seed, n_test, out_dir, hb_state)
            units.append(row)
    return {
        "seed": seed, "run_mode": RUN_MODE, "N": N_LIST[-1],
        "n_llm_calls": _LLM_CALL_COUNTER[0], "units": units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "config_version": CONFIG_VERSION,
    }


# ---------------------------------------------------------------------------
# Aggregate verdict (ratio bands over non-censored, non-control op-points)
# ---------------------------------------------------------------------------
def _mean(xs: List[Any]) -> Optional[float]:
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return round(float(np.mean(xs)), 4) if xs else None


def _cv(xs: List[float]) -> Optional[float]:
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return None
    mu = float(np.mean(xs))
    if abs(mu) < 1e-9:
        return None
    return round(float(np.std(xs)) / abs(mu), 4)


def _ratio_err(r: Optional[float]) -> Optional[float]:
    if r is None or r <= 0:
        return None
    return max(r, 1.0 / r)


def compute_verdict(all_seed_results: List[Dict[str, Any]]) -> Tuple[str, str, Dict[str, Any]]:
    n_seeds = len(all_seed_results)
    if n_seeds == 0:
        return "HARD_FAIL", "NO_SEED_RESULTS", {"cardinality_ok": False}

    n_units = sum(len(r["units"]) for r in all_seed_results)
    expected_units = n_seeds * len(N_LIST) * len(NTEST_TARGETS)
    if n_units != expected_units:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H units=%d expected=%d" % (n_units, expected_units),
                {"cardinality_ok": False, "n_units": n_units, "expected": expected_units})

    # index units by (N, n_test) across seeds
    keyed: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}
    for r in all_seed_results:
        for u in r["units"]:
            keyed.setdefault((u["N"], u["n_test"]), []).append(u)

    # build per-(N, n_test, arm) op-points aggregated over seeds
    op_points: List[Dict[str, Any]] = []
    ctl_usables: List[int] = []
    base_d1s: List[float] = []
    any_arms_bad = False
    for (n_dim, n_test), rows in sorted(keyed.items()):
        for row in rows:
            ctl_usables.append(row["ctl_usable"])
            base_d1s.append(row["base_d1"])
            if not row["base_differs_from_others"]:
                any_arms_bad = True
        for arm in MECH_ARMS:
            uds = [row["arm_results"][arm]["usable_depth"] for row in rows]
            cens = [row["arm_results"][arm]["censored"] for row in rows]
            mean_ud = float(np.mean(uds))
            op_censored = bool(mean_ud >= D_MAX - CENSOR_MARGIN or all(cens))
            emp = float(np.mean([row["arm_results"][arm]["collision_frac_emp"] for row in rows]))
            mu = float(np.mean([row["arm_results"][arm]["mu"] for row in rows]))
            pl = float(np.mean([row["arm_results"][arm]["pred_usable_loose"] for row in rows]))
            pe = float(np.mean([row["arm_results"][arm]["pred_usable_exact"] for row in rows]))
            ratio_loose = (mean_ud / pl) if pl > 1e-9 else None
            ratio_exact = (mean_ud / pe) if pe > 1e-9 else None
            # per-seed exact ratios for cross-seed CV (non-censored seeds only)
            seed_re = [_ratio_err(row["arm_results"][arm]["ratio_exact"]) for row in rows
                       if not row["arm_results"][arm]["censored"]]
            op_points.append({
                "N": n_dim, "n_test": n_test, "arm": arm,
                "eff_key_capacity": rows[0]["arm_results"][arm]["eff_key_capacity"],
                "mean_usable_depth": round(mean_ud, 3), "mean_collision_frac_emp": round(emp, 4),
                "mu": round(mu, 2), "pred_usable_loose": round(pl, 3), "pred_usable_exact": round(pe, 3),
                "ratio_loose": (round(ratio_loose, 4) if ratio_loose is not None else None),
                "ratio_exact": (round(ratio_exact, 4) if ratio_exact is not None else None),
                "ratio_err_loose": (round(_ratio_err(ratio_loose), 4) if ratio_loose else None),
                "ratio_err_exact": (round(_ratio_err(ratio_exact), 4) if ratio_exact else None),
                "censored": op_censored, "n_seeds": len(rows),
                "per_seed_ratio_err_exact": [round(x, 4) for x in seed_re if x is not None],
            })

    nonc = [op for op in op_points if not op["censored"]]
    cens = [op for op in op_points if op["censored"]]
    n_nonc = len(nonc)

    # ---- aggregate statistics over non-censored op-points ----
    exact_ratios = [op["ratio_exact"] for op in nonc if op["ratio_exact"] is not None]
    loose_ratios = [op["ratio_loose"] for op in nonc if op["ratio_loose"] is not None]
    exact_errs = [op["ratio_err_exact"] for op in nonc if op["ratio_err_exact"] is not None]
    loose_errs = [op["ratio_err_loose"] for op in nonc if op["ratio_err_loose"] is not None]

    exact_mean_ratio = _mean(exact_ratios)
    loose_mean_ratio = _mean(loose_ratios)
    exact_gm_err = (math.exp(float(np.mean([math.log(x) for x in exact_errs]))) if exact_errs else None)
    loose_gm_err = (math.exp(float(np.mean([math.log(x) for x in loose_errs]))) if loose_errs else None)
    rel_improve = (loose_gm_err / exact_gm_err) if (exact_gm_err and loose_gm_err) else None
    max_exact_err = max(exact_errs) if exact_errs else None
    loose_dir_frac = (sum(1 for r in loose_ratios if r > 1.0) / len(loose_ratios)) if loose_ratios else 0.0
    # aggregate cross-seed CV: pool per-op CVs of per-seed exact ratio-error
    per_op_cvs = [_cv(op["per_seed_ratio_err_exact"]) for op in nonc]
    per_op_cvs = [c for c in per_op_cvs if c is not None]
    agg_cv = round(float(np.mean(per_op_cvs)), 4) if per_op_cvs else None
    max_ctl = max(ctl_usables) if ctl_usables else 0
    min_base_d1 = min(base_d1s) if base_d1s else 0.0

    mode = RUN_MODE
    extra = {
        "cardinality_ok": True, "n_units": n_units, "expected_n_units": expected_units,
        "n_seeds": n_seeds, "N_LIST": N_LIST, "NTEST_TARGETS": NTEST_TARGETS,
        "arms_tested": MECH_ARMS, "control_arm": CTL_ARM,
        "n_op_points": len(op_points), "n_noncensored": n_nonc, "n_censored": len(cens),
        "exact_mean_ratio": exact_mean_ratio, "loose_mean_ratio": loose_mean_ratio,
        "exact_gm_ratio_err": (round(exact_gm_err, 4) if exact_gm_err else None),
        "loose_gm_ratio_err": (round(loose_gm_err, 4) if loose_gm_err else None),
        "rel_improve_loose_over_exact": (round(rel_improve, 4) if rel_improve else None),
        "max_exact_ratio_err": (round(max_exact_err, 4) if max_exact_err else None),
        "loose_underpredict_frac": round(loose_dir_frac, 4),
        "aggregate_cross_seed_cv_exact": agg_cv,
        "max_ctl_usable": max_ctl, "min_base_d1": round(min_base_d1, 4),
        "op_points": op_points,
        "chance_floor": round(CHANCE_FLOOR, 5),
        "bands": {
            "HP_RATIO_MAX": HP_RATIO_MAX, "HF_RATIO_MAX": HF_RATIO_MAX,
            "HP_BIAS_LO": HP_BIAS_LO, "HP_BIAS_HI": HP_BIAS_HI,
            "HF_BIAS_LO": HF_BIAS_LO, "HF_BIAS_HI": HF_BIAS_HI,
            "HP_LOOSE_BIAS_MIN": HP_LOOSE_BIAS_MIN, "HP_LOOSE_DIR_FRAC": HP_LOOSE_DIR_FRAC,
            "NOFIRE_LOOSE_MIN": NOFIRE_LOOSE_MIN, "REL_IMPROVE_MIN": REL_IMPROVE_MIN,
            "HP_CV_MAX": HP_CV_MAX, "HF_CV_MAX": HF_CV_MAX,
            "HP_CTL_USABLE_MAX": HP_CTL_USABLE_MAX, "HP_D1_SANITY": HP_D1_SANITY,
            "SMOKE_RATIO_MAX": SMOKE_RATIO_MAX, "MIN_NONCENSORED": MIN_NONCENSORED.get(mode, 3),
        },
    }

    summ = ("n_seeds=%d units=%d/%d op_points=%d (noncensored=%d censored=%d) | "
            "EXACT mean_ratio=%s gm_err=%s max_op_err=%s | LOOSE mean_ratio=%s gm_err=%s under_frac=%s | "
            "rel_improve=%s cross_seed_cv=%s | ctl_usable_max=%d base_d1_min=%.3f"
            % (n_seeds, n_units, expected_units, len(op_points), n_nonc, len(cens),
               exact_mean_ratio, extra["exact_gm_ratio_err"], extra["max_exact_ratio_err"],
               loose_mean_ratio, extra["loose_gm_ratio_err"], extra["loose_underpredict_frac"],
               extra["rel_improve_loose_over_exact"], agg_cv, max_ctl, min_base_d1))

    # ---- gates common to all modes ----
    if any_arms_bad:
        return "HARD_FAIL", "HARD_FAIL_ARMS (baseline bit-identical to another arm -- AF): " + summ, extra
    if max_ctl > HP_CTL_USABLE_MAX:
        return "HARD_FAIL", ("HARD_FAIL_CTL (shuffled-structure control usable=%d > %d -- broken "
                             "discriminator recovers structure): " % (max_ctl, HP_CTL_USABLE_MAX)) + summ, extra
    min_nonc = MIN_NONCENSORED.get(mode, 3)
    if n_nonc < min_nonc:
        return "MIDDLE_BAND", ("MIDDLE_BAND (insufficient non-censored op-points: %d < %d -- regime "
                               "too easy, all arms censored at D_MAX; needs harder N_TEST): " % (n_nonc, min_nonc)) + summ, extra
    if loose_mean_ratio is None or exact_mean_ratio is None:
        return "MIDDLE_BAND", "MIDDLE_BAND (no valid ratios computed): " + summ, extra
    if loose_mean_ratio < NOFIRE_LOOSE_MIN:
        return "MIDDLE_BAND", ("DISCRIMINATOR_DID_NOT_FIRE (loose mean_ratio=%.3f < %.2f -- the "
                               "occupancy-binary baseline is NOT actually loose at this regime; exact-vs-loose "
                               "contrast is vacuous, respec): " % (loose_mean_ratio, NOFIRE_LOOSE_MIN)) + summ, extra

    if mode == "smoke":
        fires = (max_exact_err is not None and max_exact_err <= SMOKE_RATIO_MAX
                 and SMOKE_BIAS_LO <= exact_mean_ratio <= SMOKE_BIAS_HI
                 and loose_mean_ratio >= SMOKE_LOOSE_MIN
                 and rel_improve is not None and rel_improve >= SMOKE_REL_MIN)
        if not fires:
            return ("MIDDLE_BAND",
                    ("SMOKE_DISCRIMINATOR_DID_NOT_FIRE: exact max_op_err=%s (<= %.2f) OR mean_ratio=%.3f "
                     "(in [%.2f,%.2f]) OR loose mean_ratio=%.3f (>= %.2f) OR rel_improve=%s (>= %.2f) not met: "
                     % (extra["max_exact_ratio_err"], SMOKE_RATIO_MAX, exact_mean_ratio, SMOKE_BIAS_LO,
                        SMOKE_BIAS_HI, loose_mean_ratio, SMOKE_LOOSE_MIN,
                        extra["rel_improve_loose_over_exact"], SMOKE_REL_MIN)) + summ, extra)
        return ("HARD_PASS",
                ("SMOKE_DISCRIMINATOR_FIRES: the EXACT capture order statistic predicts fresh usable "
                 "reasoning-depth UNBIASED (mean_ratio=%.3f in [%.2f,%.2f], max_op_err=%s <= %.2f) while the "
                 "occupancy-binary control stays biased (mean_ratio=%.3f, rel_improve=%s). Canonical <=1.5x "
                 "at ALL op-points + cross-seed cv<=0.15 bars are FULL-only (remote landing). "
                 % (exact_mean_ratio, SMOKE_BIAS_LO, SMOKE_BIAS_HI, extra["max_exact_ratio_err"], SMOKE_RATIO_MAX,
                    loose_mean_ratio, extra["rel_improve_loose_over_exact"])) + summ, extra)

    # ---- FULL pre-registered bands ----
    # HARD_FAIL gates first
    if not (HF_BIAS_LO <= exact_mean_ratio <= HF_BIAS_HI):
        return ("HARD_FAIL",
                ("HARD_FAIL: exact aggregate mean_ratio=%.3f OUTSIDE [%.2f,%.2f] -- the capture order statistic "
                 "is BIASED too; reasoning-depth resists exact closed-form self-prediction. "
                 % (exact_mean_ratio, HF_BIAS_LO, HF_BIAS_HI)) + summ, extra)
    if max_exact_err is not None and max_exact_err > HF_RATIO_MAX:
        worst = max(nonc, key=lambda op: op["ratio_err_exact"] or 0.0)
        return ("HARD_FAIL",
                ("HARD_FAIL: exact per-op ratio-error %.3fx > %.2fx at N=%d NT=%d arm=%s -- higher-order dynamics "
                 "(correlated hop error / position drift) dominate; the i.i.d.-per-hop capture model breaks. "
                 % (max_exact_err, HF_RATIO_MAX, worst["N"], worst["n_test"], worst["arm"])) + summ, extra)
    if agg_cv is not None and agg_cv > HF_CV_MAX:
        return ("HARD_FAIL",
                ("HARD_FAIL: exact cross-seed CV=%.3f > %.2f -- the correction is NOT stable across seeds; "
                 "'same law' framing unsupported. " % (agg_cv, HF_CV_MAX)) + summ, extra)

    # HARD_PASS gate
    hp = (max_exact_err is not None and max_exact_err <= HP_RATIO_MAX
          and HP_BIAS_LO <= exact_mean_ratio <= HP_BIAS_HI
          and loose_mean_ratio >= HP_LOOSE_BIAS_MIN
          and loose_dir_frac >= HP_LOOSE_DIR_FRAC
          and rel_improve is not None and rel_improve >= REL_IMPROVE_MIN
          and (agg_cv is None or agg_cv <= HP_CV_MAX)
          and max_ctl <= HP_CTL_USABLE_MAX
          and min_base_d1 >= HP_D1_SANITY)
    if hp:
        return ("HARD_PASS",
                ("EXACT REASONING-DEPTH SELF-MARGIN VALID (MB->CG candidate): the substrate predicts its OWN "
                 "usable reasoning depth EXACTLY via the capture partial-credit order statistic. Exact-arm "
                 "measured/predicted mean_ratio=%.3f (UNBIASED, in [%.2f,%.2f]); per-op ratio-error <= %.2fx at "
                 "ALL %d non-censored op-points (max=%s); cross-seed cv=%s <= %.2f. The retained occupancy-binary "
                 "control stays BIASED (mean_ratio=%.3f, under-predicts at %.0f%% of op-points) -- exact is %sx "
                 "tighter (>= %.2f). Shuffled-structure control at chance (usable_max=%d). Promotes reasoning-depth "
                 "self-prediction to an exact closed form, parallel to the RNS/FHRR decode-margin CGs but one level "
                 "up the composition stack (per-hop margin -> multi-hop chain survival). "
                 % (exact_mean_ratio, HP_BIAS_LO, HP_BIAS_HI, HP_RATIO_MAX, n_nonc, extra["max_exact_ratio_err"],
                    agg_cv, HP_CV_MAX, loose_mean_ratio, loose_dir_frac * 100.0,
                    extra["rel_improve_loose_over_exact"], REL_IMPROVE_MIN, max_ctl)) + summ, extra)

    return ("MIDDLE_BAND",
            ("MIDDLE_BAND: the exact arm tightens vs the occupancy-binary control (mean_ratio %.3f vs %.3f) but "
             "misses a HARD_PASS sub-gate (max_op_err=%s vs %.2f / mean_ratio in [%.2f,%.2f] / rel_improve=%s vs "
             "%.2f / cross_seed_cv=%s vs %.2f). Tighter, but not yet exact self-prediction at every op-point. "
             % (exact_mean_ratio, loose_mean_ratio, extra["max_exact_ratio_err"], HP_RATIO_MAX, HP_BIAS_LO,
                HP_BIAS_HI, extra["rel_improve_loose_over_exact"], REL_IMPROVE_MIN, agg_cv, HP_CV_MAX)) + summ, extra)


# ---------------------------------------------------------------------------
# Formula self-test (analytical + optional off-disk retrospective vs landed metrics)
# ---------------------------------------------------------------------------
def _formula_selftest() -> Tuple[bool, str]:
    # (a) Phi/logPhi basic correctness + monotone
    if abs(0.5 * math.erfc(0.0) - 0.5) > 1e-9:
        return False, "PHI_HALF_BROKEN"
    if not (_logPhi(1.0) > _logPhi(0.0) > _logPhi(-1.0)):
        return False, "LOGPHI_NOT_MONOTONE"
    # (b) capture reduces to 1/c at high SNR: p_capture(c, mu_big, D) ~ 1/c (order-stat normalization)
    for c in (1, 2, 3, 5, 8):
        v = p_capture(c, 90.0, V_CODE - 1)
        if abs(v - 1.0 / c) > 2e-3:
            return False, "CAPTURE_NOT_1_OVER_C c=%d val=%.5f expect=%.5f" % (c, v, 1.0 / c)
    # (c) non-colliding hop (c=1) at saturated mu is ~clean (>0.999)
    if p_capture(1, 90.0, V_CODE - 1) < 0.999:
        return False, "NONCOLLIDING_HOP_NOT_CLEAN val=%.6f" % p_capture(1, 90.0, V_CODE - 1)
    # (d) p_hop_exact monotone-decreasing in fill; and >= occupancy p_clean (=1-cf) pointwise
    #     (capture is graceful: recovers more often than binary-fail assumes)
    prev = 2.0
    for fill in (0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.6):
        p = p_hop_exact(fill, 90.0, V_CODE - 1)
        if p > prev + 1e-9:
            return False, "PHOP_NOT_MONOTONE fill=%.2f p=%.4f prev=%.4f" % (fill, p, prev)
        cf = 1.0 - math.exp(-fill)   # occupancy collision_frac at this fill
        if p < (1.0 - cf) - 1e-6:
            return False, "PHOP_BELOW_OCCUPANCY fill=%.2f phop=%.4f pclean=%.4f" % (fill, p, 1.0 - cf)
        prev = p
    # (e) D*_exact >= D*_loose pointwise (exact predicts DEEPER because capture > binary-fail)
    for cf in (0.05, 0.1, 0.2, 0.3):
        de = predicted_usable_depth_exact(cf, 90.0, V_CODE - 1, 18)
        dl = predicted_usable_depth_loose(cf, 18)
        if de < dl - 1e-6:
            return False, "EXACT_BELOW_LOOSE cf=%.2f exact=%.3f loose=%.3f" % (cf, de, dl)
    # (f) SNR saturated (mu >= MU_SATURATED_MIN) on the real MEASUREMENT grids the cell renders
    #     verdicts on (NOT the tiny self_test scaffold N) -> distractor factor provably ~1, exact
    #     reduces to the parameter-free capture Poisson-average.
    for n_dim in MEASUREMENT_N_REF:
        m_target = int(round(MOVERN_FIXED * n_dim))
        mu = snr_mu(n_dim, m_target)
        if mu < MU_SATURATED_MIN:
            return False, "MU_NOT_SATURATED N=%d mu=%.2f < %.1f" % (n_dim, mu, MU_SATURATED_MIN)
    return True, "FORMULA_SELFTEST_PASS"


def _retrospective_offdisk() -> Tuple[Optional[bool], str]:
    """OPTIONAL: if the landed reasoning-depth metrics are present on disk, reproduce the
    loose~2.02x / exact~0.99x split off its per_op capacity_law (zero new trials). Skipped
    gracefully on remote (landed data is not git-committed)."""
    path = REPO / "data" / "exp_reasoning_depth_keyslots_sharding_v1" / "metrics.json"
    if not path.exists():
        return None, "RETRO_SKIP (landed metrics absent -- fresh re-measurement is the primary check)"
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        per_op = d["extra"]["per_op"]
        land_dmax = int(d.get("D_MAX", 18))       # use the LANDED cell's own D_MAX, not this run's scaffold D_MAX
        land_v = int(d.get("V", V_CODE))
    except (OSError, ValueError, KeyError) as e:
        return None, "RETRO_SKIP (landed metrics unreadable: %s)" % type(e).__name__
    dstract = land_v - 1
    exact_r, loose_r = [], []
    for op in per_op:
        n_dim = op["N"]
        mu = snr_mu(n_dim, n_dim)   # M ~ N
        for arm in MECH_ARMS:
            cl = op["capacity_law"].get(arm)
            if cl is None:
                continue
            meas = cl["mean_usable_depth"]
            if meas >= land_dmax - CENSOR_MARGIN:
                continue
            cf = cl["mean_collision_frac_emp"]
            pl = predicted_usable_depth_loose(cf, land_dmax)
            pe = predicted_usable_depth_exact(cf, mu, dstract, land_dmax)
            if pl > 0:
                loose_r.append(meas / pl)
            if pe > 0:
                exact_r.append(meas / pe)
    if not exact_r:
        return None, "RETRO_SKIP (no non-censored landed op-points)"
    em = float(np.mean(exact_r)); lm = float(np.mean(loose_r))
    ok = (0.85 <= em <= 1.15) and (lm >= 1.7)
    return ok, ("RETRO n=%d exact_mean_ratio=%.3f (expect ~0.99) loose_mean_ratio=%.3f (expect ~2.02) -> %s"
                % (len(exact_r), em, lm, "OK" if ok else "OFF"))


def _selftest() -> int:
    t0 = time.perf_counter()
    # T0: FACTORED store == materialized W (measurement scaffold integrity)
    g = np.random.default_rng(0)
    n = 512
    global V_CHAIN, V_CODE  # noqa: F824
    _save = (V_CHAIN, V_CODE)
    V_CODE, V_CHAIN = 64, 32
    E = make_bipolar(V_CODE, n, g)
    R = make_bipolar(8, n, g)
    chains = make_chains(6, 5, 4, g)
    edges = chains.reshape(-1, 3)
    bg = make_background_edges(60, 4, g)
    all_e = np.concatenate([edges, bg], axis=0)
    store = FactoredStore(all_e[:, 0], all_e[:, 1], all_e[:, 2], E, R, n)
    W = build_W_reference(all_e[:, 0], all_e[:, 1], all_e[:, 2], E, R, n)
    keys = make_bipolar(10, n, g)
    max_diff = float(np.max(np.abs(store.retrieve(keys) - keys @ W.T)))
    assert max_diff < 1e-3, "FACTORED != materialized W (max|diff|=%.2e)" % max_diff
    # T1: shard routing correctness
    S = 2
    shard_id = np.arange(6, dtype=np.int64) % S
    stores = []
    for si in range(S):
        cidx = np.where(shard_id == si)[0]
        ce = chains[cidx].reshape(-1, 3)
        stores.append(FactoredStore(ce[:, 0], ce[:, 1], ce[:, 2], E, R, n))
    sharded = ShardedStore(stores, shard_id)
    kb = E[chains[:, 0, 0]] * R[chains[:, 0, 1]]
    got = sharded.retrieve(kb)
    ref_r = np.zeros_like(got)
    for i in range(6):
        ref_r[i] = stores[int(shard_id[i])].retrieve(kb[i:i + 1])[0]
    assert float(np.max(np.abs(got - ref_r))) < 1e-5, "shard routing mis-routes"
    V_CHAIN, V_CODE = _save

    # T2: FORMULA self-test (order statistic, capture->1/c, monotonicity, exact>=loose, mu saturated)
    ok_f, msg_f = _formula_selftest()
    assert ok_f, "FORMULA_SELFTEST_FAIL: %s" % msg_f

    # T3: OPTIONAL off-disk retrospective vs the landed reasoning-depth cell
    retro_ok, retro_msg = _retrospective_offdisk()
    if retro_ok is False:
        raise AssertionError("RETRO_OFFDISK_FAIL: " + retro_msg)

    dt = time.perf_counter() - t0
    print("[selftest] PASS factored==W(%.2e) shard-routing-ok | %s | %s | elapsed=%.2fs"
          % (max_diff, msg_f, retro_msg, dt), flush=True)
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
            "summary": "selftest rc=%d" % rc, "elapsed_s": round(time.perf_counter() - started, 2),
            "ts_iso": _now_iso(), "run_mode": "self_test",
            "config_version": CONFIG_VERSION, "n_seeds": 1,
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(res, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
        print("[self_test] wrote %s rc=%d" % (out_dir / "metrics.json", rc), flush=True)
        return rc

    # formula self-test gates every full/smoke run BEFORE measurement
    ok_f, msg_f = _formula_selftest()
    if not ok_f:
        raise AssertionError("FORMULA_SELFTEST_FAIL: %s" % msg_f)
    print("[formula] %s" % msg_f, flush=True)

    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    print("[start] anchor=%s mode=%s N_LIST=%s V=%d V_CHAIN=%d seeds=%s NTEST=%s M/N=%.2f D_MAX=%d "
          "arms=%s expected_units=%d"
          % (ANCHOR_NAME, RUN_MODE, N_LIST, V_CODE, V_CHAIN, SEEDS, NTEST_TARGETS, MOVERN_FIXED,
             D_MAX, [a["label"] for a in ARMS], EXPECTED_N_UNITS), flush=True)

    run_config = {"run_mode": RUN_MODE, "anchor": ANCHOR_NAME, "N": N_LIST[-1]}
    for pf in sorted(out_dir.glob("partial_metrics_*.json")):
        try:
            body = json.loads(pf.read_text(encoding="utf-8"))
            if "units" not in body:
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
        print("[seed=%d] done elapsed=%.1fs" % (seed, res["elapsed_s"]), flush=True)

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
        "N_LIST": N_LIST, "V": V_CODE, "V_CHAIN": V_CHAIN, "P_REL_MAX": P_REL_MAX,
        "D_MAX": D_MAX, "DEPTHS": DEPTHS, "NTEST_TARGETS": NTEST_TARGETS, "MOVERN_FIXED": MOVERN_FIXED,
        "expected_n_units": EXPECTED_N_UNITS, "cardinality_ok": extra.get("cardinality_ok", False),
        "extra": extra, "per_seed": all_results, "n_llm_forward_calls": _LLM_CALL_COUNTER[0],
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
