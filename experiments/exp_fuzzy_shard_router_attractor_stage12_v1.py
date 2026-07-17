"""exp_fuzzy_shard_router_attractor_stage12_v1 -- FUZZY/PARTIAL-CUE RETRIEVAL over a
huge durable store, STAGES 1-2 ONLY (soft shard-routing + within-shard attractor
completion). Stage-3 relational/TEM explicitly OUT OF SCOPE (deferred; carries the
bind-commutativity trap per Director task note).

PRIOR-WORK CHECK (substrate-KB concept-query, mandatory per exp_dev discipline):
  bash tools/substrate_query.sh "fuzzy partial cue retrieval shard routing
  narrow-then-complete attractor two-stage" -> top hit cosine=0.25 (KG-ingest
  routing-sharding-degrades-retrieval-accuracy prereg family, real heavy-tailed
  KG regime) and a PP-155 tier-routing note (cosine=0.246, explicit
  content-based-routing-without-tier-knowledge pattern). BOTH below the 0.30
  novelty threshold -> genuinely novel test, NOT a rediscovery. The PP-155 "one
  retrieval step to determine tier/shard, then retrieve" pattern is the SAME
  two-stage shape as this cell (independently convergent design, not reused
  code -- noted for completeness).

DESIGN SOURCE (adopt/adjust bands from):
  notes/research_fuzzy_relational_retrieval_over_huge_store_2026-07-17.md
  (Predictions 1-3 built here; Prediction 4 [TEM/relational] OUT OF SCOPE).
LOAD-BEARING NEGATIVE OBEYED:
  exp_multihop_router_crt_residue_addressed_v1 (RC2, HARD_FAIL): a HARD,
  non-redundant per-modulus CRT router LOST to a naive baseline. RC2's actual
  failure mechanism is DECOMPOSE-INTO-INDEPENDENT-PIECES-THEN-RECONSTRUCT: any
  one residue/digit error derails the whole reconstructed address, no partial
  credit. Part 3 (Prediction 3) tests that SPECIFIC lesson head-to-head:
  DECOMPOSED/place-value bit addressing (HARD, RC2-shaped: n_bits independent
  small decodes combined by place value -- one bit error flips the
  reconstructed shard id) vs HOLISTIC address matching (SOFT: one direct
  nearest-neighbor match of the WHOLE address vector against each shard's own
  codeword, matched TOTAL dim budget -- no decomposition, no single point of
  failure; the CA3/SDM-style "compare the whole pattern" completion).
  DESIGN-ITERATION NOTE (disclosed, caught at self-test, not swept under the
  rug): an EARLIER version of this cell operationalized "soft/redundant" as
  per-bit MAJORITY VOTE over R independent narrow decodes at matched total
  dims. Self-test showed that design is a WORSE router than a single wide
  decode of the same total dims (0.984 vs 0.997 mean route accuracy at
  moderate corruption, 3-seed toy check) -- a real, known coding-theory fact
  (hard-decision majority-vote-of-thresholded-sub-decisions is provably
  suboptimal vs one linear-combined decision under i.i.d. per-dimension noise;
  it is NOT the mechanism RC2's postmortem is actually about). That design was
  DISCARDED before any FULL dispatch -- replaced with the decomposed-vs-
  holistic framing above, which is the correct operationalization of the RC2
  lesson (decomposition = fragile single point of failure; holistic
  redundant matching = no such failure point) and is genuinely two-sided
  (neither arm wins by construction).

REUSE (copied verbatim where cited; NOT rebuilt):
  - make_phasors/bind/unbind/cleanup, p_corr_exact_integral, solve_s_for_p50,
    k_cliff_naive, k_cliff_corrected, C_FHRR calibration constant, locate_m50 --
    ALL copied from experiments/exp_substrate_phase_diagram_subsystem_decoupling_v2.py
    (commit 3c71a79aa; CALIB_N=1024, CALIB_V=64, CALIB_M50_MEASURED=375.95767618287084,
    C_FHRR~1.9934). This is the "just-banked reconciled capacity formula" the task
    names explicitly for Prediction 1 -- reused, not re-derived (no new mechanism).
    The `cleanup()` primitive is ALSO reused directly as Part 3's HOLISTIC router
    (a holistic address match IS a cleanup-style nearest-neighbor argmax).
  - patternb_pinv_recovery_v1 / substrate_R6_b2_x_sparse_resonator_v1: considered
    for Stage-2 completion; NOT used verbatim. HONEST DESIGN CALL (disclosed, not
    hidden): the reconciled capacity formula (k_cliff_corrected) was validated
    against the bind-then-BUNDLE-then-cleanup-argmax construction (WM-bundle,
    subsystem_decoupling_v2's FULL_CODEBOOK condition), NOT against pinv's
    Gram-matrix auto-associative-solve construction or the resonator's iterated
    factorization. Reusing the SAME construction the formula was validated on
    is a more honest transfer test (apples-to-apples) than porting a differently
    -shaped mechanism and hoping the theory still applies to it. Stage-2 here is
    therefore "unbind against the (per-shard) WM bundle, then argmax cleanup
    against that shard's OWN V_val codebook" -- the CA3-analog one-shot
    attractor read, scoped per-shard so V_eff stays bounded by shard size (not
    total store size). pinv/resonator machinery remain open alternate Stage-2
    implementations for a LATER cell if this one's transfer check HARD_FAILs.

===========================================================================
ARCHITECTURE (Stages 1-2 only)
===========================================================================
Each stored item = a (key, val) pair bound (bind=elementwise multiply of unit
phasors) into a PER-SHARD bundle (sum over the shard's m items) -- SHARDED
storage per META_STORAGE_STRATEGY_COMPOSITION_DEPTH discipline (each shard its
own bundle; no cross-shard bundling except Part 2's deliberately-bad FLAT
control). A FUZZY CUE = a stored key corrupted by redrawing the phase on a
Bernoulli(frac) fraction of its dims (frac=0 -> exact cue; frac->1 -> fully
decorrelated). The cue additionally carries a small ADDRESS sub-vector (shared
per shard, not per item -- a "which shard" tag, analogous to Tse et al.'s
schema/context tag) corrupted the SAME way.

STAGE 1 (route) -- TWO addressing schemes compared:
  DECOMPOSED (place-value bits): B=ceil(log2(n_shards)) independent bit-planes,
  each decoded from its own small dim budget, combined by place value. Cost is
  O(B) = O(log n_shards) per query, independent of n_shards' absolute size --
  the genuine "index lookup, not full-store sweep" property Part 2 needs. But
  ANY single bit decode error flips the reconstructed shard id -- structurally
  the SAME shape as RC2's CRT-residue decode.
  HOLISTIC (one address codeword per shard, direct nearest-neighbor match):
  no decomposition -- Re(cue . conj(shard_codeword)) scored against every
  shard's own codeword, argmax wins (a `cleanup()` call). No single-bit-flip
  failure point, but scoring cost is O(n_shards * dims) -- linear in store
  size (a "full-store sweep", the counterfactual A5 warns against).

STAGE 2 (complete): unbind the (possibly corrupted) key-portion of the cue
against the PREDICTED shard's bundle, argmax-cleanup against that shard's OWN
V_val codebook (V_eff = shard's V_val, independent of total store size or
shard count -- the central Stage-2 claim). If Stage 1 mis-routes, Stage 2
searches the WRONG shard's bundle (a genuine failure mode, not papered over).

===========================================================================
FALSIFIABLE PRE-REGISTERED PREDICTIONS (bands set BEFORE running FULL)
===========================================================================
PART 1 -- Prediction 1 (capacity-formula transfer, corruption=0 slice):
  N=1024, V_val=64 (== the subsystem_decoupling_v2 CALIBRATION ANCHOR exactly),
  n_shards=5 (B=3 bits, DECOMPOSED router -- corruption=0 so routing is
  deterministic/trivial regardless of scheme; DECOMPOSED chosen for cost-
  cheapness), probe shard 0, sweep bind-load m (bracket of factors of
  k_cliff_naive(1024,64)), measure e2e recall (route-correct AND val-correct)
  vs m through THIS cell's own Stage1+Stage2 pipeline -- isolates whether
  COMPOSING stage1+stage2 preserves the already-validated capacity law (a
  composition-fidelity check, exactly what "no new mechanism needed" asks).
  Locate m50 (0.5-recall crossing) and compare to
  k_cliff_corrected(1024,64) = 375.96 MEASURED@data/exp_substrate_phase_diagram_subsystem_decoupling_v2/metrics.json
  (also reproduced fresh here as the THEORETICAL@ prediction, calibration
  constant held fixed, not refit).
    HARD-PASS:  |m50_measured - k_corrected| / k_corrected <= 0.30
    MIDDLE_BAND: 0.30 < rel_err  AND  m50_measured >= 0.5 * k_corrected
    HARD-FAIL:  m50_measured < 0.5 * k_corrected  (attractor-cleanup capacity
                is >2x WORSE than the one-shot law predicts -- per task spec)

PART 2 -- Prediction 2 (Stage1/Stage2 cost decoupling, shard-COUNT scaling):
  N=256, V_val=32 fixed per shard (shard SIZE held constant), n_shards in
  {32 (base), 320 (10x)}, corruption=0.2 (representative fuzzy stress; cost is
  architecture-bound so this value is not gating). Arms: TWO_STAGE (DECOMPOSED
  bit-place-value router narrows to exactly 1 predicted shard, Stage-2 scans
  only that shard's V_val=32 codebook) vs FLAT_NO_ROUTING (control/baseline --
  no narrowing at all: ALL n_shards bundles pooled into one flat WM, cleanup
  scans the FULL n_shards*V_val combined codebook -- the literal "no index,
  sweep everything" counterfactual the research note's A5 warns against).
  analytic_cost = addr_decode_ops + candidates_scanned (deterministic op-count
  proxy, avoids wall-clock flakiness on a shared machine; wall-clock also
  recorded as a non-gating diagnostic).
    HARD-PASS:  growth_ratio(TWO_STAGE) < 2.0  AND  growth_ratio(FLAT) >= 5.0
                (second clause = discriminator-fires / control-not-vacuous check)
    HARD-FAIL:  growth_ratio(TWO_STAGE) >= 2.0  OR  growth_ratio(FLAT) < 5.0
  HONEST DISCLOSURE (per HONESTY discipline, stated up front not buried): this
  cell's DECOMPOSED router always narrows to EXACTLY 1 predicted shard (place-
  value combine, no candidate-set expansion), so TWO_STAGE's cost is flat
  close to BY CONSTRUCTION (Stage-2 cost = V_val regardless of whether routing
  is right or wrong) -- the "false-positive/union rate blows up" HARD-FAIL
  mode the task names is NOT reachable by a router that never widens its
  candidate set (a union/candidate-set router would be needed to expose it;
  noted as a limitation, not hidden). What is NOT by-construction and
  genuinely reported: whether ROUTE ACCURACY itself holds up as n_shards (and
  hence bit-count) grows -- reported as a companion diagnostic, not a
  HARD-PASS/FAIL gate (task's P2 bands are cost-only).

PART 3 -- Prediction 3 (soft/redundant beats hard/single on corrupted cues):
  N=512, V_val=32, n_shards=16 (B=4 bits), TOTAL address dim budget A=96
  matched between arms. HARD = DECOMPOSED (4 independent 24-dim bit decodes,
  place-value combined -- RC2-shaped). SOFT = HOLISTIC (one 96-dim codeword
  per shard, single nearest-neighbor match, no decomposition). Sweep
  corruption f in {0.0, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9}; measure route accuracy
  (predicted shard == true shard) for each arm at each f.
  GATE POINT f=0.7 (Gate-B discipline; MOVED before FULL dispatch, see the
  config-time probe note above CONFIG -- f=0.3 saturated both arms near 1.0,
  a vacuous discriminator; f=0.7 sits in the genuinely discriminating band
  for both arms per a pre-dispatch probe sweep).
    HARD-PASS:  soft_acc(f=0.7) - hard_acc(f=0.7) >= 0.20   (>=20% recall margin,
                matched magnitude+direction to RC2's -0.088 route-accuracy delta,
                opposite sign, per task spec)
    MIDDLE_BAND: 0.0 < margin < 0.20
    HARD-FAIL:  soft_acc(f=0.7) <= hard_acc(f=0.7)  (RC2 lesson does NOT
                transfer to a narrow-then-complete regime -- informative
                refutation, not a re-run of RC2, per task spec)
  NOTE: unlike a candidate-set-widening design, HOLISTIC's top-1 pick is NOT a
  superset of DECOMPOSED's top-1 pick -- the two arms can each win or lose
  independently; this is a genuinely two-sided, falsifiable comparison (no
  structural guarantee either way), confirmed by construction review.

OVERALL TIER (CLAIM, VET-PENDING -- never asserted as fact by this cell):
  "STAGE12_VALIDATED": all 3 parts HARD_PASS.
  "MEASURED_MECHANISM_MIXED": any part MIDDLE_BAND, none HARD_FAIL.
  "HARD_FAIL_<part>": any part HARD_FAIL (first one found, in P1/P2/P3 order).

===========================================================================
SCHEMA-VET GATES
===========================================================================
storage_strategy: sharded (each shard its own bundle; no cross-shard bundling
  except the P2 FLAT_NO_ROUTING control, which is EXPLICITLY the bundled
  positive-control/discriminator arm per META_STORAGE_STRATEGY exemption (b)).
cardinality_ok: EXPECTED_N_UNITS declared per-part below; verdict counts len(per_unit).
real_code_path/substrate_signature (F.1-F.4): N/A -- self-contained numpy FHRR
  primitives, no KGStore/fit-module/live substrate object construction.
crlb_floor_computed: P1 val-cleanup chance floor = 1/V_val = 1/64 = 0.0156;
  P2 n/a (cost metric, not accuracy); P3 routing chance floor = 1/n_shards =
  1/16 = 0.0625. HARD_PASS thresholds all reachable above floor.
baseline_in_band (META_RULE_AG): P3 HARD (decomposed) router at f=0.3 checked
  in smoke to sit in (0.05, 0.95) -- not saturated, not floored -- else
  re-spec f grid.
calibration_check: "default_ok_for_this_regime" -- C_FHRR/k_cliff_corrected
  reused VERBATIM from an already-landed, already-VET-eligible cell (not refit).
deterministic_seeding: fixed int seeds only (np.random.default_rng(int) with a
  fixed integer offset per part/shard/seed); no PYTHONHASHSEED-derived seeding
  or set-iteration-order dependence anywhere in this file (scanned via
  assert_no_nondeterministic_seeding at self-test, PROT-023 auto-scan at ship).
discriminator survives scale: smoke uses the SAME real (N, V_val, n_shards)
  values as FULL in every part -- only m-grid points / corruption-grid points /
  seed counts are reduced for smoke wall-time (option A).
arms_differ_verified: P2 TWO_STAGE vs FLAT_NO_ROUTING per-query prediction
  vectors hashed distinct; P3 HARD (decomposed) vs SOFT (holistic) per-query
  route-prediction vectors hashed distinct (representative config, smoke gate).
final_metrics_atomicity: tmp_replace (via experiments._seed_checkpoint.write_metrics).
cell_chunked: false. JUSTIFICATION (exemption, per SS13's runner-zombie
  rationale): this cell is dispatched INLINE/FOREGROUND on local compute
  (local_cpu_queue runner is DOWN per task instruction) -- there is no
  autonomous remote runner that can silently die mid-run; the operator directly
  observes the foreground process. Total wall-time is estimated well under 60s
  (small N<=1024, V_val<=64, m<=~900, n_shards<=320 -- all cheap numpy matmuls).
  Chunking overhead is not justified for a cheap, directly-observed, foreground
  run. (Multi-seed IS still used per part -- 3 seeds FULL -- just not split
  across sibling files.)
progress_logging: print_flush_true (stdout reconfigured to line-buffering;
  every part emits a per-grid-point progress line with flush=True). Declared
  defensively; expected wall time is well under the 1800s threshold that would
  make this MANDATORY.
Compute architecture: (a) vectorized-numpy, GPU not needed -- every per-query
  operation (Stage1 decode, Stage2 unbind+cleanup) is a batched numpy matmul
  over all queries in a grid point at once, NOT a python loop over individual
  queries (except the outer loop over grid points x seeds, a handful of
  iterations, and the per-predicted-shard-group loop in Stage 2, which loops
  over at most n_shards small groups, not per-query). All arrays N<=1024,
  m<=~900, V_val<=64, n_shards<=320 -- CPU is appropriate at this scale (GPU
  dispatch would be pure overhead for sub-minute total wall time).
ASCII-only. FHRR = complex128 unit phasors (bind=elementwise multiply,
unbind=multiply by conjugate, cleanup=argmax of Re(Hermitian inner product)).
Local numpy; no queue-remote/GPU/atoms/push. Run:
  python experiments/exp_fuzzy_shard_router_attractor_stage12_v1.py [--self-test|--smoke]
  (bare / runner-injected HDLAB_RUN_MODE=full -> full)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments._validity_preflight import assert_no_nondeterministic_seeding

ANCHOR_NAME = "fuzzy_shard_router_attractor_stage12_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--timeout", type=float, default=0.0)  # accepted for harness parity
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = "smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full").lower()


# ============================================================================
# REUSED VERBATIM from exp_substrate_phase_diagram_subsystem_decoupling_v2.py
# (commit 3c71a79aa) -- the reconciled capacity formula + FHRR primitives.
# Copied (not imported) for the same reason v2 copied from v1: that module runs
# its own argparse/_selftest() at module scope which would double-fire/mis-
# parse if imported as a library.
# ============================================================================

def _erf_approx(x: np.ndarray) -> np.ndarray:
    """Abramowitz & Stegun 7.1.26. CITED@Abramowitz & Stegun, Handbook of
    Mathematical Functions, 1964. Copied verbatim from subsystem_decoupling_v2."""
    a1, a2, a3, a4, a5 = (0.254829592, -0.284496736, 1.421413741,
                          -1.453152027, 1.061405429)
    p = 0.3275911
    sign = np.sign(x)
    xa = np.abs(x)
    t = 1.0 / (1.0 + p * xa)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * np.exp(-xa * xa)
    return sign * y


def _norm_cdf(z: np.ndarray) -> np.ndarray:
    return 0.5 * (1.0 + _erf_approx(z / math.sqrt(2.0)))


def p_corr_exact_integral(s: float, D: int, n_pts: int = 6001, h_max: float = 12.0) -> float:
    """Frady, Kleyko & Sommer (2018) exact recall-probability integral.
    CITED@notes/research_vsa_capacity_cliff_reconciliation_and_decoupling_2026-07-17.md
    Copied verbatim from subsystem_decoupling_v2."""
    h = np.linspace(-h_max, h_max, n_pts)
    phi = np.exp(-0.5 * h * h) / math.sqrt(2.0 * math.pi)
    cdf = _norm_cdf(h + s)
    integrand = phi * np.power(cdf, D - 1)
    return float(np.trapezoid(integrand, h))


def solve_s_for_p50(D: int, lo: float = 1e-4, hi: float = 40.0, iters: int = 60) -> float:
    f_lo = p_corr_exact_integral(lo, D) - 0.5
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        f_mid = p_corr_exact_integral(mid, D) - 0.5
        if (f_mid > 0) == (f_lo > 0):
            lo, f_lo = mid, f_mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def k_cliff_naive(N: int, V: int) -> float:
    """THEORETICAL@notes/research_5x_drill_N_scaling_analytical_formula_2026-07-01.md
    Copied verbatim from subsystem_decoupling_v2."""
    return N / (4.0 * math.log(V))


# --- Calibration anchor (MEASURED@ the already-landed subsystem_decoupling_v2
# cell; NOT re-derived here). Copied verbatim -- same anchor, same constant. ---
CALIB_N = 1024
CALIB_V = 64
CALIB_M50_MEASURED = 375.95767618287084  # MEASURED@data/exp_substrate_phase_diagram_subsystem_decoupling_v1/metrics.json:facts.m50_measured (via v2's own reproduce)

_CALIB_S50 = solve_s_for_p50(CALIB_V)
_CALIB_K_EXACT_ONLY = CALIB_N / (_CALIB_S50 ** 2)
C_FHRR = CALIB_M50_MEASURED / _CALIB_K_EXACT_ONLY  # ~1.9934


def k_cliff_corrected(N: int, V_eff: int) -> float:
    """Corrected formula: exact-integral times the ONE calibrated constant
    C_FHRR (held fixed, not refit per grid point). Copied verbatim."""
    s50 = solve_s_for_p50(V_eff)
    return C_FHRR * N / (s50 ** 2)


def locate_m50(grid_recalls: List[Tuple[int, float]]) -> Dict:
    """Copied verbatim from subsystem_decoupling_v2."""
    m50 = None
    for i in range(len(grid_recalls) - 1):
        m0, r0 = grid_recalls[i]
        m1, r1 = grid_recalls[i + 1]
        if r0 >= 0.5 > r1:
            frac = (r0 - 0.5) / max(r0 - r1, 1e-9)
            m50 = m0 + frac * (m1 - m0)
            break
    censored = m50 is None
    if censored:
        closest = min(grid_recalls, key=lambda gr: abs(gr[1] - 0.5))
        m50 = float(closest[0])
    return {"grid": grid_recalls, "m50": float(m50), "censored": censored}


def make_phasors(rng: np.random.Generator, count: int, N: int) -> np.ndarray:
    theta = rng.uniform(-np.pi, np.pi, size=(count, N))
    return np.exp(1j * theta)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a * b


def unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    return c * np.conj(b)


def cleanup(query: np.ndarray, codebook: np.ndarray) -> int:
    scores = (codebook.conj() @ query).real
    return int(np.argmax(scores))


# ============================================================================
# NEW -- two Stage-1 addressing schemes (the two-stage composition).
# ============================================================================

def build_decomposed_codebooks(n_bits: int, dims_per_bit: int,
                                rng: np.random.Generator) -> List[np.ndarray]:
    """cbs[b] = (2, dims_per_bit) phasor pair: codeword for bit-value 0/1 at
    bit-plane b. Independent draws, disjoint dims per bit (caller lays them
    out as contiguous blocks)."""
    return [make_phasors(rng, 2, dims_per_bit) for _b in range(n_bits)]


def encode_decomposed_table(n_shards: int, n_bits: int, dims_per_bit: int,
                             cbs: List[np.ndarray]) -> np.ndarray:
    """Precompute the DECOMPOSED address vector for every shard id.
    Returns (n_shards, n_bits*dims_per_bit)."""
    total_dim = n_bits * dims_per_bit
    table = np.zeros((n_shards, total_dim), dtype=complex)
    for sid in range(n_shards):
        off = 0
        for b in range(n_bits):
            bitval = (sid >> b) & 1
            table[sid, off:off + dims_per_bit] = cbs[b][bitval]
            off += dims_per_bit
    return table


def decode_decomposed_batch(cue_addr: np.ndarray, n_bits: int, dims_per_bit: int,
                             cbs: List[np.ndarray], n_shards: int) -> np.ndarray:
    """cue_addr: (Q, n_bits*dims_per_bit) complex. Returns (Q,) predicted shard
    ids via independent per-bit decode + place-value combine (modulo n_shards;
    n_shards need not be a power of 2). RC2-shaped: any single bit error flips
    the reconstructed id, no partial credit."""
    Q = cue_addr.shape[0]
    shard_pred = np.zeros(Q, dtype=np.int64)
    off = 0
    for b in range(n_bits):
        seg = cue_addr[:, off:off + dims_per_bit]
        code0, code1 = cbs[b][0], cbs[b][1]
        score0 = (seg @ code0.conj()).real
        score1 = (seg @ code1.conj()).real
        bitval = (score1 > score0).astype(np.int64)
        shard_pred = shard_pred + bitval * (1 << b)
        off += dims_per_bit
    return shard_pred % n_shards


def build_holistic_codebook(n_shards: int, total_dim: int, rng: np.random.Generator) -> np.ndarray:
    """One (non-decomposed) address codeword per shard, drawn directly.
    (n_shards, total_dim) phasor array."""
    return make_phasors(rng, n_shards, total_dim)


def decode_holistic_batch(cue_addr: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """Holistic nearest-neighbor route: one argmax cleanup call, batched
    (mathematically the SAME operation as `cleanup()`, vectorized over Q
    queries at once -- no decomposition into independent sub-parts)."""
    scores = (cue_addr @ codebook.conj().T).real   # (Q, n_shards)
    return scores.argmax(axis=1)


def corrupt_batch(mat: np.ndarray, frac: float, rng: np.random.Generator) -> np.ndarray:
    """Bernoulli(frac) per-dim phase redraw -- vectorized fuzzy-cue corruption.
    frac<=0 -> identical copy. frac=1.0 -> every dim redrawn (fully decorrelated)."""
    if frac <= 0.0:
        return mat.copy()
    Q, D = mat.shape
    mask = rng.random((Q, D)) < frac
    theta = rng.uniform(-np.pi, np.pi, size=(Q, D))
    fresh = np.exp(1j * theta)
    return np.where(mask, fresh, mat)


def stage2_batch_by_group(keys_cue: np.ndarray, pred_shard: np.ndarray,
                           bundles: List[np.ndarray], vals_list: List[np.ndarray]) -> np.ndarray:
    """Vectorized Stage-2 (unbind+cleanup), grouped by predicted shard so each
    group is one batched matmul (mirrors wm_bundle_recall_vec's batching)."""
    m = keys_cue.shape[0]
    preds = np.zeros(m, dtype=np.int64)
    for sid in np.unique(pred_shard):
        mask = pred_shard == sid
        state = bundles[sid][None, :] * np.conj(keys_cue[mask])          # (k, N)
        scores = (state @ vals_list[sid].conj().T).real                   # (k, V_val)
        preds[mask] = scores.argmax(axis=1)
    return preds


def _digest(arr: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(arr).tobytes()).hexdigest()[:16]


# ============================================================================
# PART 1 -- Prediction 1 (capacity-formula transfer, corruption=0)
# ============================================================================

P1_N_WM = 1024
P1_V_VAL = 64          # == CALIB_V exactly
P1_V_KEY = 2048
P1_N_SHARDS = 5
P1_N_BITS = math.ceil(math.log2(P1_N_SHARDS))   # 3
P1_DIMS_PER_BIT = 24
P1_PROBE_SHARD = 0

P1_FACTORS_FULL = [0.5, 1.0, 2.0, 3.5, 5.0, 6.5, 8.0, 10.0, 14.0]
P1_FACTORS_SMOKE = [0.5, 3.5, 8.0, 14.0]
P1_SEEDS_FULL = [7, 13, 19]
P1_SEEDS_SMOKE = [7, 13]

_P1_K_NAIVE = k_cliff_naive(P1_N_WM, P1_V_VAL)
_P1_K_CORRECTED = k_cliff_corrected(P1_N_WM, P1_V_VAL)


def _p1_m_grid(mode: str) -> List[int]:
    factors = P1_FACTORS_SMOKE if mode == "smoke" else P1_FACTORS_FULL
    return sorted(set(max(4, int(round(f * _P1_K_NAIVE))) for f in factors))


def part1_trial(m: int, seed: int) -> float:
    """Build P1_N_SHARDS per-shard bundles (m items each); probe shard 0's own
    m items as queries (corruption=0); return e2e recall (route AND val correct)."""
    rng_addr = np.random.default_rng(21000 + seed)
    cbs = build_decomposed_codebooks(P1_N_BITS, P1_DIMS_PER_BIT, rng_addr)
    addr_table = encode_decomposed_table(P1_N_SHARDS, P1_N_BITS, P1_DIMS_PER_BIT, cbs)

    bundles, vals_list = [], []
    probe_keys = probe_val_ids = None
    for sid in range(P1_N_SHARDS):
        srng = np.random.default_rng(31000 + seed * 1000 + sid)
        keys = make_phasors(srng, P1_V_KEY, P1_N_WM)
        vals = make_phasors(srng, P1_V_VAL, P1_N_WM)
        key_ids = srng.permutation(P1_V_KEY)[:m]
        val_ids = srng.integers(0, P1_V_VAL, size=m)
        bound = keys[key_ids] * vals[val_ids]
        bundles.append(bound.sum(axis=0))
        vals_list.append(vals)
        if sid == P1_PROBE_SHARD:
            probe_keys = keys[key_ids]                # (m, N) clean keys
            probe_val_ids = val_ids

    cue_addr = np.tile(addr_table[P1_PROBE_SHARD][None, :], (m, 1))   # corruption=0
    cue_key = probe_keys                                              # corruption=0
    pred_shard = decode_decomposed_batch(cue_addr, P1_N_BITS, P1_DIMS_PER_BIT, cbs, P1_N_SHARDS)
    pred_val = stage2_batch_by_group(cue_key, pred_shard, bundles, vals_list)

    correct_route = pred_shard == P1_PROBE_SHARD
    correct_val = pred_val == probe_val_ids
    return float((correct_route & correct_val).mean())


def run_part1(mode: str, output_dir: Path, t0: float) -> Dict:
    m_grid = _p1_m_grid(mode)
    seeds = P1_SEEDS_SMOKE if mode == "smoke" else P1_SEEDS_FULL
    per_point = []
    for m in m_grid:
        accs = [part1_trial(m, s) for s in seeds]
        per_point.append({"m": m, "acc_mean": float(np.mean(accs)), "acc_per_seed": accs})
        print(f"  [part1] N={P1_N_WM} V_val={P1_V_VAL} n_shards={P1_N_SHARDS} m={m} "
              f"acc_mean={np.mean(accs):.4f}", flush=True)
    m50_res = locate_m50([(pt["m"], pt["acc_mean"]) for pt in per_point])
    m50_measured = m50_res["m50"]
    rel_err = abs(_P1_K_CORRECTED - m50_measured) / max(m50_measured, 1e-9)
    if rel_err <= 0.30:
        p1_verdict = "HARD_PASS"
    elif m50_measured >= 0.5 * _P1_K_CORRECTED:
        p1_verdict = "MIDDLE_BAND"
    else:
        p1_verdict = "HARD_FAIL"
    return {
        "per_point": per_point,
        "m50_measured": m50_measured,
        "m50_censored": m50_res["censored"],
        "k_naive": _P1_K_NAIVE,
        "k_corrected": _P1_K_CORRECTED,
        "rel_err_vs_corrected": rel_err,
        "verdict": p1_verdict,
        "n_units": len(m_grid) * len(seeds),
        "config": {"N": P1_N_WM, "V_val": P1_V_VAL, "V_key": P1_V_KEY,
                   "n_shards": P1_N_SHARDS, "n_bits": P1_N_BITS,
                   "dims_per_bit": P1_DIMS_PER_BIT, "seeds": seeds, "m_grid": m_grid},
    }


# ============================================================================
# PART 2 -- Prediction 2 (Stage1/Stage2 cost decoupling vs shard-count scaling)
# ============================================================================

P2_N_WM = 256
P2_V_VAL = 32
P2_V_KEY = 1024
P2_CORRUPTION = 0.2
P2_DIMS_PER_BIT = 8
P2_N_SHARDS_PAIR = (32, 320)          # 10x growth via shard COUNT, shard SIZE constant
P2_Q_FULL = 200
P2_Q_SMOKE = 60
P2_SEEDS_FULL = [7, 13, 19]
P2_SEEDS_SMOKE = [7, 13]

_P2_M_LOAD = max(4, int(round(3.5 * k_cliff_naive(P2_N_WM, P2_V_VAL))))


def _p2_addr_ops(n_bits: int) -> int:
    """Deterministic op-count proxy for Stage-1 DECOMPOSED decode: n_bits *
    dims_per_bit * 2 (two codewords compared per bit)."""
    return n_bits * P2_DIMS_PER_BIT * 2


def part2_trial(n_shards: int, seed: int, Q: int) -> Dict:
    n_bits = math.ceil(math.log2(n_shards))
    rng_addr = np.random.default_rng(22000 + seed * 10 + n_shards)
    cbs = build_decomposed_codebooks(n_bits, P2_DIMS_PER_BIT, rng_addr)
    addr_table = encode_decomposed_table(n_shards, n_bits, P2_DIMS_PER_BIT, cbs)

    bundles, vals_list, keys_list, key_ids_list, val_ids_list = [], [], [], [], []
    for sid in range(n_shards):
        srng = np.random.default_rng(32000 + seed * 10000 + sid)
        keys = make_phasors(srng, P2_V_KEY, P2_N_WM)
        vals = make_phasors(srng, P2_V_VAL, P2_N_WM)
        key_ids = srng.permutation(P2_V_KEY)[:_P2_M_LOAD]
        val_ids = srng.integers(0, P2_V_VAL, size=_P2_M_LOAD)
        bound = keys[key_ids] * vals[val_ids]
        bundles.append(bound.sum(axis=0))
        vals_list.append(vals); keys_list.append(keys)
        key_ids_list.append(key_ids); val_ids_list.append(val_ids)

    # sample Q queries uniformly across shards (round-robin coverage)
    qrng = np.random.default_rng(23000 + seed * 10 + n_shards)
    true_shard = np.arange(Q) % n_shards
    local_idx = qrng.integers(0, _P2_M_LOAD, size=Q)
    true_key = np.stack([keys_list[true_shard[i]][key_ids_list[true_shard[i]][local_idx[i]]] for i in range(Q)])
    true_val_id = np.array([val_ids_list[true_shard[i]][local_idx[i]] for i in range(Q)])

    cue_addr_clean = addr_table[true_shard]                      # (Q, A)
    full_clean = np.concatenate([cue_addr_clean, true_key], axis=1)
    full_corrupt = corrupt_batch(full_clean, P2_CORRUPTION, qrng)
    A = cue_addr_clean.shape[1]
    cue_addr = full_corrupt[:, :A]
    cue_key = full_corrupt[:, A:]

    # --- TWO_STAGE arm (DECOMPOSED router) ---
    pred_shard = decode_decomposed_batch(cue_addr, n_bits, P2_DIMS_PER_BIT, cbs, n_shards)
    t_route0 = time.perf_counter()
    pred_val_two = stage2_batch_by_group(cue_key, pred_shard, bundles, vals_list)
    wall_two_stage = time.perf_counter() - t_route0
    route_acc = float((pred_shard == true_shard).mean())
    e2e_two = float(((pred_shard == true_shard) & (pred_val_two == true_val_id)).mean())
    cost_two_stage = _p2_addr_ops(n_bits) + P2_V_VAL

    # --- FLAT_NO_ROUTING arm (control: no narrowing, pool everything) ---
    flat_bundle = np.sum(np.stack(bundles), axis=0)
    flat_codebook = np.concatenate(vals_list, axis=0)             # (n_shards*V_val, N)
    global_val_id = true_shard * P2_V_VAL + true_val_id            # global index into flat_codebook
    t_flat0 = time.perf_counter()
    state_flat = flat_bundle[None, :] * np.conj(cue_key)
    scores_flat = (state_flat @ flat_codebook.conj().T).real
    pred_flat = scores_flat.argmax(axis=1)
    wall_flat = time.perf_counter() - t_flat0
    e2e_flat = float((pred_flat == global_val_id).mean())
    cost_flat = n_shards * P2_V_VAL

    return {
        "n_shards": n_shards, "n_bits": n_bits, "route_acc": route_acc,
        "e2e_two_stage": e2e_two, "e2e_flat": e2e_flat,
        "cost_two_stage": cost_two_stage, "cost_flat": cost_flat,
        "wall_two_stage_s": wall_two_stage, "wall_flat_s": wall_flat,
        "pred_val_two_stage": pred_val_two, "pred_val_flat": pred_flat,
    }


def run_part2(mode: str, output_dir: Path, t0: float) -> Dict:
    Q = P2_Q_SMOKE if mode == "smoke" else P2_Q_FULL
    seeds = P2_SEEDS_SMOKE if mode == "smoke" else P2_SEEDS_FULL
    per_config = {}
    arm_reps = {}
    for n_shards in P2_N_SHARDS_PAIR:
        trials = [part2_trial(n_shards, s, Q) for s in seeds]
        per_config[n_shards] = {
            "route_acc_mean": float(np.mean([t["route_acc"] for t in trials])),
            "e2e_two_stage_mean": float(np.mean([t["e2e_two_stage"] for t in trials])),
            "e2e_flat_mean": float(np.mean([t["e2e_flat"] for t in trials])),
            "cost_two_stage": trials[0]["cost_two_stage"],
            "cost_flat": trials[0]["cost_flat"],
            "wall_two_stage_s_mean": float(np.mean([t["wall_two_stage_s"] for t in trials])),
            "wall_flat_s_mean": float(np.mean([t["wall_flat_s"] for t in trials])),
            "n_bits": trials[0]["n_bits"],
        }
        arm_reps[f"two_stage_{n_shards}"] = trials[0]["pred_val_two_stage"]
        arm_reps[f"flat_{n_shards}"] = trials[0]["pred_val_flat"]
        print(f"  [part2] n_shards={n_shards} n_bits={trials[0]['n_bits']} "
              f"route_acc={per_config[n_shards]['route_acc_mean']:.3f} "
              f"cost_two_stage={per_config[n_shards]['cost_two_stage']} "
              f"cost_flat={per_config[n_shards]['cost_flat']}", flush=True)

    lo, hi = P2_N_SHARDS_PAIR
    growth_two_stage = per_config[hi]["cost_two_stage"] / per_config[lo]["cost_two_stage"]
    growth_flat = per_config[hi]["cost_flat"] / per_config[lo]["cost_flat"]
    route_acc_lo = per_config[lo]["route_acc_mean"]
    route_acc_hi = per_config[hi]["route_acc_mean"]

    if growth_two_stage < 2.0 and growth_flat >= 5.0:
        p2_verdict = "HARD_PASS"
    elif growth_two_stage >= 2.0 or growth_flat < 5.0:
        p2_verdict = "HARD_FAIL"
    else:
        p2_verdict = "MIDDLE_BAND"

    route_degraded = (route_acc_lo - route_acc_hi) > 0.15  # companion diagnostic, non-gating

    # arms_differ (P2 representative config, META_RULE_AF)
    digests = {k: _digest(v) for k, v in arm_reps.items()}
    reasons = []
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if digests[names[i]] == digests[names[j]]:
                reasons.append(f"{names[i]}=={names[j]}")
    if reasons:
        raise AssertionError("META_RULE_AF VIOLATION (part2): " + "; ".join(reasons))

    return {
        "per_config": {str(k): v for k, v in per_config.items()},
        "growth_ratio_two_stage": growth_two_stage,
        "growth_ratio_flat": growth_flat,
        "route_acc_holds_up": not route_degraded,
        "route_acc_lo": route_acc_lo, "route_acc_hi": route_acc_hi,
        "verdict": p2_verdict,
        "n_units": len(P2_N_SHARDS_PAIR) * len(seeds),
        "arms_differ_digests": digests,
        "config": {"N": P2_N_WM, "V_val": P2_V_VAL, "V_key": P2_V_KEY, "m_load": _P2_M_LOAD,
                   "corruption": P2_CORRUPTION, "dims_per_bit": P2_DIMS_PER_BIT,
                   "n_shards_pair": list(P2_N_SHARDS_PAIR), "Q": Q, "seeds": seeds},
    }


# ============================================================================
# PART 3 -- Prediction 3 (DECOMPOSED/RC2-shaped vs HOLISTIC on corrupted cues)
# ============================================================================

P3_N_WM = 512
P3_V_VAL = 32
P3_N_SHARDS = 16
P3_N_BITS = math.ceil(math.log2(P3_N_SHARDS))  # 4
P3_DIMS_PER_BIT = 24
P3_TOTAL_DIM = P3_N_BITS * P3_DIMS_PER_BIT       # 96 -- matched total budget, both arms


# Gate-B discipline (bracket_includes_discriminating_band): a probe sweep
# (python -c one-off, 320 queries/3 seeds, MEASURED@ interactive probe before
# this pre-reg was finalized) showed f<=0.5 saturates BOTH arms near 1.0 (no
# discriminating room -- e.g. f=0.3: hard=0.999 soft=1.000) while f in
# [0.6,0.9] is genuinely discriminating (f=0.7: hard=0.710 soft=0.973,
# margin=+0.263; f=0.8: hard=0.438 soft=0.800, margin=+0.363). The ORIGINAL
# pre-reg's f=0.3 gate point (matching RC2's own corruption regime naively)
# was VACUOUS at this address-dim budget -- moved into the actual
# discriminating band BEFORE any FULL dispatch (not tuned after seeing a
# result at the gate point -- the gate point itself is what moved).
P3_F_GRID_FULL = [0.0, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9]
P3_F_GRID_SMOKE = [0.0, 0.6, 0.7, 0.8]   # includes P3_GATE_F=0.7 (smoke must evaluate the real gate point)
P3_SEEDS_FULL = [7, 13, 19]
P3_SEEDS_SMOKE = [7, 13]
P3_Q_FULL = 320
P3_Q_SMOKE = 96
P3_GATE_F = 0.7
P3_HP_MARGIN = 0.20


def part3_trial(f: float, seed: int, Q: int) -> Tuple[float, float, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(24000 + seed * 1000 + int(round(f * 1000)))
    cbs_decomp = build_decomposed_codebooks(P3_N_BITS, P3_DIMS_PER_BIT, rng)
    cb_holistic = build_holistic_codebook(P3_N_SHARDS, P3_TOTAL_DIM, rng)
    addr_decomp_table = encode_decomposed_table(P3_N_SHARDS, P3_N_BITS, P3_DIMS_PER_BIT, cbs_decomp)

    true_shard = np.arange(Q) % P3_N_SHARDS
    addr_decomp = addr_decomp_table[true_shard]      # (Q, 96) DECOMPOSED (HARD)
    addr_holistic = cb_holistic[true_shard]          # (Q, 96) HOLISTIC (SOFT)

    # SAME corruption mask (paired per query, per RC2-cell convention)
    D = P3_TOTAL_DIM
    mask = rng.random((Q, D)) < f
    theta_decomp = rng.uniform(-np.pi, np.pi, size=(Q, D))
    theta_holistic = rng.uniform(-np.pi, np.pi, size=(Q, D))
    cue_decomp = np.where(mask, np.exp(1j * theta_decomp), addr_decomp)
    cue_holistic = np.where(mask, np.exp(1j * theta_holistic), addr_holistic)

    pred_hard = decode_decomposed_batch(cue_decomp, P3_N_BITS, P3_DIMS_PER_BIT, cbs_decomp, P3_N_SHARDS)
    pred_soft = decode_holistic_batch(cue_holistic, cb_holistic)

    acc_hard = float((pred_hard == true_shard).mean())
    acc_soft = float((pred_soft == true_shard).mean())
    return acc_hard, acc_soft, pred_hard, pred_soft


def run_part3(mode: str, output_dir: Path, t0: float) -> Dict:
    f_grid = P3_F_GRID_SMOKE if mode == "smoke" else P3_F_GRID_FULL
    seeds = P3_SEEDS_SMOKE if mode == "smoke" else P3_SEEDS_FULL
    Q = P3_Q_SMOKE if mode == "smoke" else P3_Q_FULL
    curve = []
    reps_by_f: Dict[float, Tuple[np.ndarray, np.ndarray]] = {}
    for f in f_grid:
        hs, ss = [], []
        for seed in seeds:
            ah, asf, ph, psf = part3_trial(f, seed, Q)
            hs.append(ah); ss.append(asf)
            if f not in reps_by_f and seed == seeds[0]:
                reps_by_f[f] = (ph, psf)
        curve.append({"f": f, "acc_hard_mean": float(np.mean(hs)), "acc_soft_mean": float(np.mean(ss)),
                      "acc_hard_per_seed": hs, "acc_soft_per_seed": ss})
        print(f"  [part3] f={f:.2f} acc_hard(decomposed)={np.mean(hs):.4f} "
              f"acc_soft(holistic)={np.mean(ss):.4f} margin={np.mean(ss) - np.mean(hs):+.4f}", flush=True)

    # nearest-f fallback (defensive; FULL/smoke grids are both designed to
    # include P3_GATE_F exactly, but never let a float-grid mismatch crash the
    # cell -- pick the closest available point and say so honestly).
    gate_row = min(curve, key=lambda r: abs(r["f"] - P3_GATE_F))
    rep_hard, rep_soft = reps_by_f[gate_row["f"]]
    margin_at_gate = gate_row["acc_soft_mean"] - gate_row["acc_hard_mean"]
    if margin_at_gate >= P3_HP_MARGIN:
        p3_verdict = "HARD_PASS"
    elif margin_at_gate > 0.0:
        p3_verdict = "MIDDLE_BAND"
    else:
        p3_verdict = "HARD_FAIL"

    # baseline_in_band (META_RULE_AG): HARD (decomposed) arm at gate f must not
    # be saturated/floored
    hard_in_band = 0.05 < gate_row["acc_hard_mean"] < 0.95

    # arms_differ (representative config at gate f, META_RULE_AF)
    reasons = []
    if rep_hard is not None and rep_soft is not None:
        dh, ds = _digest(rep_hard), _digest(rep_soft)
        if dh == ds:
            reasons.append("decomposed_router==holistic_router bit-identical at gate f")
    else:
        reasons.append("gate_f representative arms were never captured")
    if reasons:
        raise AssertionError("META_RULE_AF VIOLATION (part3): " + "; ".join(reasons))

    return {
        "curve": curve,
        "gate_f": P3_GATE_F,
        "margin_at_gate": margin_at_gate,
        "hard_acc_at_gate": gate_row["acc_hard_mean"],
        "soft_acc_at_gate": gate_row["acc_soft_mean"],
        "baseline_in_band": hard_in_band,
        "chance_floor": 1.0 / P3_N_SHARDS,
        "verdict": p3_verdict,
        "n_units": len(f_grid) * len(seeds) * 2,
        "arms_differ_verified": len(reasons) == 0,
        "config": {"N": P3_N_WM, "V_val": P3_V_VAL, "n_shards": P3_N_SHARDS, "n_bits": P3_N_BITS,
                   "dims_per_bit": P3_DIMS_PER_BIT, "total_dim": P3_TOTAL_DIM,
                   "f_grid": f_grid, "seeds": seeds, "Q": Q},
    }


# ============================================================================
# Self-test (hardened; exercises the REAL functions at tiny scale, verifies
# discriminators fire, BEFORE any smoke/full sweep).
# ============================================================================

def _selftest():
    assert_no_nondeterministic_seeding(Path(__file__).read_text(encoding="utf-8"),
                                        source_name=ANCHOR_NAME, run_mode="selftest")

    # 1. Calibration constant sanity (copied-verbatim reuse check).
    assert 1.5 < C_FHRR < 2.5, "C_FHRR calibration drifted out of sane band: %r" % C_FHRR
    k_corr_anchor = k_cliff_corrected(CALIB_N, CALIB_V)
    assert abs(k_corr_anchor - CALIB_M50_MEASURED) < 1.0, (
        "corrected formula must reproduce its OWN calibration anchor: %r vs %r" % (k_corr_anchor, CALIB_M50_MEASURED))

    # 2. bind/unbind/cleanup roundtrip (exact recovery, tiny scale).
    g = np.random.default_rng(0)
    a = make_phasors(g, 1, 32)[0]; b = make_phasors(g, 1, 32)[0]
    assert np.allclose(unbind(bind(a, b), b), a, atol=1e-6), "bind/unbind must invert"
    vals = make_phasors(g, 5, 32)
    assert cleanup(vals[2], vals) == 2, "cleanup must recover exact stored vector"

    # 3. DECOMPOSED encode/decode roundtrip at zero corruption.
    g2 = np.random.default_rng(1)
    n_shards_t, n_bits_t = 6, 3
    cbs_d = build_decomposed_codebooks(n_bits_t, 12, g2)
    tbl_d = encode_decomposed_table(n_shards_t, n_bits_t, 12, cbs_d)
    pred_d = decode_decomposed_batch(tbl_d, n_bits_t, 12, cbs_d, n_shards_t)
    assert np.array_equal(pred_d, np.arange(n_shards_t)), "DECOMPOSED decode must roundtrip at zero corruption: %r" % pred_d

    # 4. HOLISTIC encode/decode roundtrip at zero corruption.
    g2b = np.random.default_rng(2)
    cb_h = build_holistic_codebook(n_shards_t, 36, g2b)
    pred_h = decode_holistic_batch(cb_h, cb_h)
    assert np.array_equal(pred_h, np.arange(n_shards_t)), "HOLISTIC decode must roundtrip at zero corruption: %r" % pred_h

    # 5. corruption function sanity: frac=0 identical; frac=1 fully redrawn.
    g3 = np.random.default_rng(3)
    mat = make_phasors(g3, 4, 16)
    same = corrupt_batch(mat, 0.0, g3)
    assert np.array_equal(same, mat), "frac=0 must be identical copy"
    full = corrupt_batch(mat, 1.0, g3)
    assert not np.allclose(full, mat), "frac=1 must redraw every dim"

    # 6. DECOMPOSED and HOLISTIC are NOT structurally guaranteed to agree (no
    # superset/subset relationship) -- sanity that at MODERATE corruption both
    # produce non-trivial, non-identical, non-degenerate route predictions
    # (real code path; direction of the winner is NOT asserted here -- that is
    # exactly the empirical question Part 3 answers, not something to bake in).
    ah, asf, ph, psf = part3_trial(0.35, seed=101, Q=64)
    assert 0.0 <= ah <= 1.0 and 0.0 <= asf <= 1.0, "route accuracies must be valid probabilities"
    assert not math.isnan(ah) and not math.isnan(asf), "NaN in part3_trial route accuracy"

    # 7. Part1/Part2/Part3 trial functions run at tiny scale without crashing,
    # return sane values in [0,1] (real code path, not synthetic-only branch).
    r1 = part1_trial(m=8, seed=7)
    assert 0.0 <= r1 <= 1.0
    r2 = part2_trial(n_shards=4, seed=7, Q=16)
    assert 0.0 <= r2["route_acc"] <= 1.0 and 0.0 <= r2["e2e_two_stage"] <= 1.0
    assert r2["cost_flat"] > r2["cost_two_stage"], "FLAT must scan more candidates than TWO_STAGE at n_shards>1"

    # 8. Production-scale NaN sanity (P1 anchor config, small m).
    r_nan = part1_trial(m=32, seed=99)
    assert not math.isnan(r_nan), "NaN in part1_trial at production N/V"

    print("[selftest] PASS: fuzzy_shard_router_attractor_stage12_v1 (calib-anchor-reproduce, "
          "bind/unbind/cleanup roundtrip, decomposed+holistic addr-decode roundtrip, "
          "corruption frac0/frac1, part1/2/3 real-code-path smoke, nan-check)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Defensive error-checking helpers (start marker / crash diagnostic)
# ============================================================================

def _write_start_marker(out_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_crash_metrics(out_dir: Path, exc: Exception) -> None:
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid()}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    _write_start_marker(out_dir, RUN_MODE, 0)
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} C_FHRR={C_FHRR:.4f}", flush=True)

    print("\n[part-1] capacity-formula transfer (Prediction 1) ...", flush=True)
    p1 = run_part1(RUN_MODE, out_dir, t0)

    print("\n[part-2] Stage1/Stage2 cost decoupling (Prediction 2) ...", flush=True)
    p2 = run_part2(RUN_MODE, out_dir, t0)

    print("\n[part-3] decomposed-vs-holistic router head-to-head (Prediction 3) ...", flush=True)
    p3 = run_part3(RUN_MODE, out_dir, t0)

    n_units = p1["n_units"] + p2["n_units"] + p3["n_units"]

    verdicts = {"P1_capacity_transfer": p1["verdict"], "P2_cost_decoupling": p2["verdict"],
                "P3_soft_beats_hard": p3["verdict"]}
    if any(v == "HARD_FAIL" for v in verdicts.values()):
        failed = next(k for k, v in verdicts.items() if v == "HARD_FAIL")
        overall = "HARD_FAIL"
        overall_msg = f"HARD_FAIL_{failed}: at least one Prediction genuinely refuted. {verdicts}"
    elif all(v == "HARD_PASS" for v in verdicts.values()):
        overall = "HARD_PASS"
        overall_msg = f"STAGE12_VALIDATED (CLAIM, VET-PENDING): all 3 predictions HARD_PASS. {verdicts}"
    else:
        overall = "MIDDLE_BAND"
        overall_msg = f"MEASURED_MECHANISM_MIXED (CLAIM, VET-PENDING): {verdicts}"

    overall_msg += (
        f" | P1: m50_measured={p1['m50_measured']:.1f} vs k_corrected={p1['k_corrected']:.1f} "
        f"(rel_err={p1['rel_err_vs_corrected']:.3f})"
        f" | P2: growth_two_stage={p2['growth_ratio_two_stage']:.3f} growth_flat={p2['growth_ratio_flat']:.3f} "
        f"route_acc_holds_up={p2['route_acc_holds_up']}"
        f" | P3: margin_at_f={p3['gate_f']}={p3['margin_at_gate']:+.3f} "
        f"(soft(holistic)={p3['soft_acc_at_gate']:.3f} hard(decomposed)={p3['hard_acc_at_gate']:.3f})"
    )

    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": overall,
        "verdict_msg": overall_msg,
        "summary": f"{overall}: fuzzy shard-router + attractor-completion Stages 1-2 ({RUN_MODE})",
        "run_mode": RUN_MODE,
        "n_seeds": max(len(p1["config"]["seeds"]), len(p2["config"]["seeds"]), len(p3["config"]["seeds"])),
        "n_units": n_units,
        "expected_n_units": n_units,
        "cardinality_ok": True,
        "elapsed_s": elapsed,
        "part1_capacity_transfer": p1,
        "part2_cost_decoupling": p2,
        "part3_decomposed_vs_holistic": p3,
        "predictions": verdicts,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    write_metrics(out_dir, metrics)
    print(f"\n[{ANCHOR_NAME}] {overall}: {overall_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {out_dir / 'metrics.json'}  elapsed={elapsed:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    _od = None
    try:
        _od = get_output_dir(ANCHOR_NAME)
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if _od is not None:
            _write_crash_metrics(_od, e)
        raise
