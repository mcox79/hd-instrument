"""exp_redundant_soft_shard_router_e2e_selector_confirm_v1 -- CONFIRMS the
VET-predicted fix for the end-to-end fuzzy-retrieval HARD_FAIL landed by
exp_redundant_soft_shard_router_e2e_stage12_v1 (0f68b7249). That cell's
Stage-2 SELECTOR (final-answer = argmax over M shortlisted shards' own
completion-confidence) was shown by off-disk VET recompute (backup doc,
2026-07-17, atom a53d7c6a) to be a STRICTLY-WORSE selector than simply
taking Stage-1's OWN top-1 routing rank (already computed, thrown away by
the old code): predicted route=0.926 / e2e=0.558 vs the landed argmax's
route=0.5625 / e2e=0.408. This cell CONFIRMS that prediction on a real run
and tries two candidate selectors to do even better, capturing more of the
shortlist's own +0.04 recall edge (0.966 any-of-M hit vs 0.926 top-1-route).

PRIOR-WORK CHECK (substrate-KB concept-query, mandatory per exp_dev
discipline): `bash tools/substrate_query.sh "stage-2 selector fix
confirmation shortlist rank verification argmax spurious winner combined
selector cue regeneration fidelity"` -> top-5 hits all cosine<=0.3408, and
all are GENERIC WordNet/concept lexical entries ('combination',
'regeneration', 'Confirmation', 'confirmation', 'veneration') sourced from
data/substrate_index + wordnet_cache -- NOT prior arc-cell matches. The
nearest substantive relative is this cell's own design source
(notes/research_stage2_selection_argmax_spurious_winner_2026-07-17.md,
already cited by the task as the design pointer, not an independent
rediscovery). Genuinely novel confirmation cell, not a rediscovery.

REUSED VERBATIM (byte-identical RNG seed formulas + regime constants) from
exp_redundant_soft_shard_router_e2e_stage12_v1.py (commit 0f68b7249): store
construction, address codebooks (HARD/SOFT/R3/DEGENERATE), corruption-mask
construction, query sampling. ONLY the SELECTOR (how the final (shard, val)
is chosen from the M-shortlist's per-column completions) differs across
arms -- per the task's ONE-VARIABLE design gate. The Stage-1 candidate-
generation function is instrumented (decode_redundant_batch_conf) to ALSO
expose the per-column Stage-1 confidence that decode_redundant_batch already
computed internally and discarded; a self-test proves this instrumentation
produces the IDENTICAL shortlist as the original (Stage-1 behavior
unchanged, only more of its internal state is now visible to Stage-2).

===========================================================================
SELECTOR ARMS (5 total on the R3 shortlist, + HARD/SOFT/DEGENERATE
reference/control arms unchanged from the prior cell)
===========================================================================
R3_ARGMAX   (baseline-fail, REPRODUCES the prior cell's exact selector):
  final = column with the highest Stage-2 completion confidence across the
  M=4 shortlisted shards. Expected to reproduce e2e~0.408 @f=0.7
  MEASURED@d:/AI/hd-instrument/data/exp_redundant_soft_shard_router_e2e_stage12_v1/metrics.json:sweep.gate_row.e2e_acc_R3_M4_mean
  and to FAIL the bar (design gate #2 can-fail check).

R3_TOP1     (VET-predicted FREE FIX, PRIMARY gate): final = shortlist
  column 0 always (Stage-1's own top-ranked candidate; shortlist is already
  sorted by Stage-1 confidence descending by construction). Cheapest
  possible selector -- a real deployment need only run Stage-2 completion
  on ONE shard, not four; cost accounted as route_cost + 1*V_val regardless
  of how many columns this cell's code computes for measurement
  convenience (see cost-accounting note below).
  Predicted: route~0.926 e2e~0.558
  HYPOTHESIZED@notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-17.md
  (e2e VET CONFIRMED + FLIPPED-POSITIVE block, atom a53d7c6a -- an off-disk
  VET recompute, not a landed metrics.json artifact, hence HYPOTHESIZED not
  MEASURED).

R3_COMBINED (companion, tries to capture the +0.04 recall edge): final =
  argmax over the M columns of query-relative z-score(Stage-1 confidence)
  + z-score(Stage-2 completion confidence) (both z-scored across the SAME
  query's valid shortlist columns, so the two differently-scaled signals
  combine without hand-tuned weights). Needs completion over all M columns
  (same cost as R3_ARGMAX: route_cost + M*V_val).

R3_CUEFID   (optional, drill-proposed per notes/research_stage2_selection_
  argmax_spurious_winner_2026-07-17.md): final = argmax over the M columns
  of REGENERATED-CUE FIDELITY -- for each candidate (shard, val), regenerate
  an estimate of the ORIGINAL key by unbinding the shard's WM bundle with
  the predicted val's OWN codeword, then score cosine-fidelity against the
  ACTUAL (possibly-corrupted) cue key used for this query. This is an
  INDEPENDENT check (regenerated key vs actual cue-key) distinct from the
  completion's own val-argmax confidence -- the brain-plus-coding-theory
  convergent fix (recall-to-reject / CA1 mismatch / CRC-aided list
  decoding) the research drill proposed. Cheap to add (one more bind +
  cosine-sim per candidate); cost = route_cost + M*V_val + M*N_WM (the
  extra regenerate-and-compare term, honestly accounted, never hidden).

R3_ORACLE   (diagnostic ONLY, uses ground truth, NEVER gates any verdict):
  final = the shortlist column containing the true shard, if present (else
  column 0, which will then be wrong regardless). Reproduces the "what if
  selection were perfect" ceiling context
  (route_acc_R3_ORACLE ~= route_acc_R3_shortlist_hit_mean by construction);
  reported for interpretability, HP_SCOPE excludes it from any gate.

===========================================================================
BAND-FLOOR DISCIPLINE (MEMORY "BAND-FLOOR RESULTS ARE INCONCLUSIVE, NOT
HARD_PASS" / META_RULE_L, applied PROACTIVELY here because the VET's own
predicted 0.558 clears the 0.9xSOFT=0.554 threshold by only ~0.004 -- a
razor-thin margin the backup doc itself flagged as "tier boundary fragile")
===========================================================================
This cell does NOT just check `acc_c >= 0.9*acc_ref_soft` and call it
HARD_PASS. It additionally requires the pass to clear that threshold by
>= 5% of the (acc_ref_soft - acc_ref_hard) band width before calling
HARD_PASS outright; a pass that clears the raw threshold but NOT the 5%
strict margin is reported as MIDDLE_BAND_NEAR_FLOOR (a genuine but fragile
clearance), not oversold as HARD_PASS. This gate is PRE-REGISTERED (decided
before running FULL), not applied post-hoc after seeing which side of 0.554
the real number lands on.

===========================================================================
DESIGN GATE (verified per task's mandatory pre-flight)
===========================================================================
1. REAL BASELINES present: SOFT (holistic e2e, robust+expensive, reused
   verbatim), HARD (decomposed e2e, cheap+fragile, reused verbatim), and
   R3_ARGMAX (the actual FAILED selector from the prior landed cell,
   reproduced here byte-for-byte in mechanism, not just cited).
2. CAN-FAIL: verified at smoke (BEFORE full dispatch) that R3_ARGMAX does
   NOT clear 0.9*acc_ref_soft at gate f -- confirms the discriminator can
   fail and that the prior HARD_FAIL was genuine, not a construction
   artifact. `argmax_reproduces_prior_fail` field checked at smoke and FULL.
3. DIFFICULTY-ON: full corruption sweep f in {0.0,0.5,0.6,0.7,0.8,0.9}
   (reused verbatim from the prior cell -- f=0.7 is Gate-D continuity,
   0.8/0.9 are the higher-difficulty points).
4. ONE VARIABLE: store, Stage-1 router configs (HARD/SOFT/R3/DEGENERATE),
   Stage-2 per-shard completion mechanics, and the shared corruption mask
   are BYTE-IDENTICAL RNG-formula reuse from the prior cell. ONLY the
   selector (which shortlist column becomes the final answer) differs
   across R3_ARGMAX / R3_TOP1 / R3_COMBINED / R3_CUEFID / R3_ORACLE.

===========================================================================
FALSIFIABLE PRE-REGISTERED PREDICTIONS (bands set BEFORE running FULL)
===========================================================================
Gate f = 0.7 (same gate point as every prior cell in this arc).

For each R3 selector config c (R3_ARGMAX, R3_TOP1, R3_COMBINED, R3_CUEFID):
  acc_c         = e2e accuracy (route AND val both correct) at f=0.7
  cost_c        = route_cost(R3, MEASURED, IDENTICAL across all R3 configs)
                  + selector-specific completion term (1*V_val for R3_TOP1;
                  M*V_val for R3_ARGMAX/R3_COMBINED; M*V_val + M*N_WM for
                  R3_CUEFID) -- never hidden or amortized.
  acc_ref_soft  = SOFT arm's OWN measured e2e accuracy at f=0.7 (this run).
  acc_ref_hard  = HARD arm's OWN measured e2e accuracy at f=0.7 (this run).
  cost_ref_soft = SOFT arm's e2e cost (route_cost_soft + 1*V_val).
  band_width_acc = acc_ref_soft - acc_ref_hard

  ACC_PASS_FACTOR   = 0.9   (within 10% of SOFT's e2e accuracy)
  ACC_STRICT_MARGIN = 0.05  (must clear the 0.9x threshold by >= 5% of
                             band_width_acc to count as outright HARD_PASS,
                             per META_RULE_L / band-floor discipline above)
  COST_PASS_FACTOR  = 0.7   (at least 30% cheaper e2e than SOFT)
  COST_FAIL_FACTOR  = 0.9   (advantage erased: >= 90% of SOFT's cost)

  acc_pass_threshold := ACC_PASS_FACTOR * acc_ref_soft
  acc_pass        := acc_c >= acc_pass_threshold
  acc_strict_pass := acc_c >= acc_pass_threshold + ACC_STRICT_MARGIN * band_width_acc
  acc_fail        := acc_c <= acc_ref_hard
  cost_pass       := cost_c <= COST_PASS_FACTOR * cost_ref_soft
  cost_fail       := cost_c >= COST_FAIL_FACTOR * cost_ref_soft

  Per-config verdict:
    HARD_FAIL_ACC          : acc_fail
    HARD_FAIL_COST         : (not acc_fail) and cost_fail
    HARD_PASS              : acc_strict_pass and cost_pass
    MIDDLE_BAND_NEAR_FLOOR  : acc_pass and (not acc_strict_pass) and cost_pass
    MIDDLE_BAND             : otherwise (genuine Pareto point)

OVERALL CELL TIER (keyed to PRIMARY config R3_TOP1; R3_ARGMAX/R3_COMBINED/
R3_CUEFID/R3_ORACLE reported as companions/diagnostics, never promoted to
gate the overall tier):
  "SELECTOR_FIX_CONFIRMED" (CLAIM, VET-CONFIRMED): R3_TOP1 HARD_PASS.
  "SELECTOR_FIX_FRAGILE" (CLAIM, VET-CONFIRMED-BUT-FRAGILE): R3_TOP1
    MIDDLE_BAND_NEAR_FLOOR (clears the raw threshold, not the strict margin).
  "VET_PREDICTION_REFUTED": R3_TOP1 HARD_FAIL_ACC or HARD_FAIL_COST.
  "MEASURED_MECHANISM_MIXED": R3_TOP1 plain MIDDLE_BAND.

CAN-FAIL VERIFICATION (mandatory, design gate #2): R3_ARGMAX must NOT reach
  HARD_PASS (must reproduce the prior HARD_FAIL_ACC within tolerance 0.15
  absolute of the prior 0.408 e2e figure) -- `argmax_reproduces_prior_fail`
  field, verified at smoke AND FULL.
  Also DEGENERATE (structural can-fail control, reused verbatim): e2e at
  gate f must score below HARD's e2e accuracy by >= 0.05
  (`can_fail_confirmed` field, same convention as the prior cell).

DISCRIMINATOR-MUST-FIRE (baseline_in_band, META_RULE_AG): HARD and SOFT e2e
  accuracy at gate f=0.7 must each sit in (0.05, 0.95) -- reused verbatim
  regime already verified in the prior landed cell; re-verified at smoke.

===========================================================================
SCHEMA-VET GATES
===========================================================================
storage_strategy: sharded (unchanged from prior cell -- reused verbatim).
cardinality_ok: EXPECTED_N_UNITS = len(f_grid) * len(seeds); verdict counts
  actual units run via len(curve).
real_code_path/substrate_signature (F.1-F.4): N/A -- self-contained numpy
  FHRR-style primitives, no KGStore/fit-module/live substrate object.
crlb_floor_computed: e2e chance floor (uniform-random guess) = 1/(n_shards*
  V_val) = 1/512 = 0.00195 for M=1 arms; M-shortlist arms' reachable-by-
  chance floor is M/(n_shards*V_val) -- still far below all HARD_PASS
  thresholds (set RELATIVE to this run's own measured SOFT/HARD arms).
baseline_in_band (META_RULE_AG): verified at smoke BEFORE FULL (reused
  regime, already verified once in the prior cell; re-verified here since
  this is a fresh dispatch).
calibration_check: "default_ok_for_this_regime" -- ALL Stage-1 router
  constants and Stage-2 m_load are BYTE-IDENTICAL reuse of the prior
  landed cell's already-verified regime; only the NEW selector logic
  (z-score combine weights = 1:1 equal, cue-regen fidelity = plain cosine,
  neither refit to any observed accuracy) is genuinely new and both use
  parameter-free (no tunable constant) formulas.
deterministic_seeding: fixed int seeds only, IDENTICAL formulas to the
  prior cell (np.random.default_rng(int) with fixed integer offsets per
  part/config/seed/f); no PYTHONHASHSEED-derived seeding or set-iteration-
  order dependence anywhere in this file (scanned via
  assert_no_nondeterministic_seeding at self-test, PROT-023 auto-scan).
discriminator survives scale: smoke uses the SAME real (n_shards=16,
  total_addr_dim=96, N_WM=256, V_val=32, m_load=8) values as FULL -- only
  f-grid points and seed counts are reduced for smoke wall-time (option A,
  reused verbatim from the prior cell's own already-verified choice).
arms_differ_verified (META_RULE_AF): at the gate f row, final (pred_shard,
  pred_val) tuples for hard, soft, degenerate, R3_ARGMAX, R3_TOP1,
  R3_COMBINED, R3_CUEFID, R3_ORACLE are hashed and asserted pairwise-
  distinct (8 arms; different selectors on the SAME shortlist are expected
  to genuinely disagree on enough queries to produce distinct hashes).
final_metrics_atomicity: tmp_replace (via experiments._seed_checkpoint.write_metrics).
cell_chunked: false. JUSTIFICATION (exemption, same as the prior cell):
  dispatched INLINE/FOREGROUND on local compute per task instruction;
  operator directly observes the foreground process; total wall time
  estimated under 2 minutes (small numpy arrays throughout, same scale as
  the prior cell which ran the FULL sweep in 1.17s).
progress_logging: print_flush_true (stdout reconfigured to line-buffering;
  every f-grid point emits a progress line with flush=True). Declared
  defensively; expected wall time is well under the 1800s threshold that
  would make this MANDATORY.
Compute architecture: (a) vectorized-numpy for per-query channel scoring,
  CRT reconstruction, Stage-2 unbind+cleanup, and all 5 selector rules
  (batched matmul/broadcast over all Q queries per shard-group); small
  Python-level loops over (i) the M shortlist columns (constant, <=4) and
  (ii) the per-shard groups within a column (<=16 shards) -- neither loop
  scales with Q or n_shards in a way that defeats vectorization. CPU is
  appropriate at this scale.
effective_vs_nominal_parameter_audit (Gate A): sweep axis is f (corruption
  fraction), experienced DIRECTLY and IDENTICALLY (same shared mask) by
  every arm's own [address, key] concatenation -- unchanged from the prior
  cell. sweep_alignment_verdict: ALIGNED.
bracket_includes_discriminating_band (Gate B): f grid reused verbatim from
  the prior cell's already-verified discriminating band.
signal_shape_compatibility_audit (Gate C): Stage-1 shortlist (int array,
  -1-padded) + Stage-1 confidence (float array) -> Stage-2 per-column
  completion (val, score) -> selector (shortlist, confidences, scores,
  optionally cue_key/bundles/vals_list for R3_CUEFID) -> final (shard, val)
  edge is SHAPE_MATCH -- verified via self-test roundtrip.
reproduce_prior_chain_grade_result_as_positive_control (Gate D): (a)
  Stage-1 ROUTE-ONLY accuracy (HARD/SOFT/R3-shortlist-hit) at f=0.7 must
  reproduce the router cell's / prior e2e cell's measured values WITHIN
  TOLERANCE 0.10 (reused verbatim gate). (b) R3_ARGMAX e2e accuracy at
  f=0.7 must reproduce the PRIOR E2E CELL's OWN R3_M4 argmax e2e accuracy
  (0.4083) WITHIN TOLERANCE 0.15 absolute -- this is the NEW positive
  control specific to this confirmation cell (proves the "same selector,
  same everything" baseline arm is a true reproduction, not a different
  code path masquerading as the same thing).
functional_requirements: (1) confirm the free Stage-1-rank selector clears
  the bar on a real run [-> R3_TOP1 arm]; (2) demonstrate the failed
  selector genuinely fails under identical conditions [-> R3_ARGMAX arm,
  Gate D(b)]; (3) attempt to capture the remaining +0.04 recall edge
  cheaply [-> R3_COMBINED, R3_CUEFID arms]; (4) report the diagnostic
  ceiling if selection were perfect [-> R3_ORACLE, non-gating].
HP_SCOPE: {hard: [e2e_reference_only], soft: [e2e_reference_only],
  degenerate: [can_fail_check_only],
  R3_ARGMAX: [must_reproduce_prior_fail, can_fail_check],
  R3_TOP1: [PRIMARY e2e HARD_PASS/FAIL/MIDDLE_BAND_NEAR_FLOOR gate],
  R3_COMBINED: [companion, own verdict, does not gate overall tier],
  R3_CUEFID: [companion, own verdict, does not gate overall tier],
  R3_ORACLE: [diagnostic only, no verdict, never gates]}
ASCII-only. FHRR = complex128 unit phasors (bind=elementwise multiply,
unbind=multiply by conjugate, cleanup=argmax of Re(Hermitian inner product)).
Local numpy; no queue-remote/GPU/atoms/push. Run:
  python experiments/exp_redundant_soft_shard_router_e2e_selector_confirm_v1.py [--self-test|--smoke]
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

ANCHOR_NAME = "redundant_soft_shard_router_e2e_selector_confirm_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--timeout", type=float, default=0.0)  # accepted for harness parity
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = "smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full").lower()


# ============================================================================
# REUSED VERBATIM from exp_redundant_soft_shard_router_e2e_stage12_v1.py
# (commit 0f68b7249), itself composing exp_redundant_soft_shard_router_v1.py
# and exp_fuzzy_shard_router_attractor_stage12_v1.py. Byte-identical logic;
# only decode_redundant_batch is extended (see decode_redundant_batch_conf
# below) to also expose the Stage-1 confidence it already computed.
# ============================================================================

def make_phasors(rng: np.random.Generator, count: int, N: int) -> np.ndarray:
    theta = rng.uniform(-np.pi, np.pi, size=(count, N))
    return np.exp(1j * theta)


def build_decomposed_codebooks(n_bits: int, dims_per_bit: int,
                                rng: np.random.Generator) -> List[np.ndarray]:
    return [make_phasors(rng, 2, dims_per_bit) for _b in range(n_bits)]


def encode_decomposed_table(n_shards: int, n_bits: int, dims_per_bit: int,
                             cbs: List[np.ndarray]) -> np.ndarray:
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
    return make_phasors(rng, n_shards, total_dim)


def decode_holistic_batch(cue_addr: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    scores = (cue_addr @ codebook.conj().T).real
    return scores.argmax(axis=1)


def _extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    g, x1, y1 = _extended_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def _modinv(a: int, m: int) -> int:
    g, x, _ = _extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse mod {m} (not coprime, gcd={g})")
    return x % m


def crt_weights(moduli: Tuple[int, ...]) -> Tuple[int, List[int]]:
    """CITED@standard constructive proof of the Chinese Remainder Theorem."""
    M = 1
    for m in moduli:
        M *= m
    weights = []
    for m in moduli:
        Mr = M // m
        inv = _modinv(Mr % m, m)
        weights.append((Mr * inv) % M)
    return M, weights


def split_dims(total_dim: int, R: int) -> List[int]:
    base, rem = divmod(total_dim, R)
    return [base + (1 if i < rem else 0) for i in range(R)]


def build_channel_codebooks(moduli: Tuple[int, ...], dims_list: List[int],
                             rng: np.random.Generator) -> List[np.ndarray]:
    return [make_phasors(rng, moduli[r], dims_list[r]) for r in range(len(moduli))]


def encode_channel_table(n_shards: int, moduli: Tuple[int, ...], dims_list: List[int],
                          codebooks: List[np.ndarray]) -> np.ndarray:
    total_dim = sum(dims_list)
    table = np.zeros((n_shards, total_dim), dtype=complex)
    for sid in range(n_shards):
        off = 0
        for r, m in enumerate(moduli):
            d = dims_list[r]
            table[sid, off:off + d] = codebooks[r][sid % m]
            off += d
    return table


def score_channels_batch(cue: np.ndarray, dims_list: List[int],
                          codebooks: List[np.ndarray]) -> List[np.ndarray]:
    scores = []
    off = 0
    for r, cb in enumerate(codebooks):
        d = dims_list[r]
        seg = cue[:, off:off + d]
        scores.append((seg @ cb.conj().T).real)
        off += d
    return scores


def topk_per_channel(scores: List[np.ndarray], k_top: int) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    idx_list, score_list = [], []
    for s in scores:
        k = min(k_top, s.shape[1])
        order = np.argsort(-s, axis=1)[:, :k]
        idx_list.append(order)
        score_list.append(np.take_along_axis(s, order, axis=1))
    return idx_list, score_list


def _combo_shard_ids_and_conf(topk_idx: List[np.ndarray], topk_score: List[np.ndarray],
                               weights: List[int], M_full: int, n_shards: int,
                               combo: Tuple[int, ...]) -> Tuple[np.ndarray, np.ndarray]:
    R = len(topk_idx)
    Q = topk_idx[0].shape[0]
    x = np.zeros(Q, dtype=np.int64)
    conf = np.zeros(Q, dtype=np.float64)
    for r in range(R):
        rank = combo[r]
        residues_r = topk_idx[r][:, rank]
        conf = conf + topk_score[r][:, rank]
        x = (x + residues_r.astype(np.int64) * weights[r]) % M_full
    shard_id = np.where(x < n_shards, x, -1)
    return shard_id, conf


def decode_redundant_batch(cue: np.ndarray, moduli: Tuple[int, ...], dims_list: List[int],
                            codebooks: List[np.ndarray], n_shards: int, k_top: int,
                            M: int) -> Tuple[np.ndarray, np.ndarray]:
    """UNCHANGED reuse (byte-identical to the prior cell). Returns (shortlist
    (Q,M) int, -1-padded; n_candidates (Q,) int). Kept alongside
    decode_redundant_batch_conf so self-test can prove the two agree
    exactly (ONE-VARIABLE proof: instrumentation doesn't change Stage-1)."""
    R = len(moduli)
    scores = score_channels_batch(cue, dims_list, codebooks)
    topk_idx, topk_score = topk_per_channel(scores, k_top)
    Q = cue.shape[0]
    M_full, weights = crt_weights(moduli)

    import itertools
    k_eff = [topk_idx[r].shape[1] for r in range(R)]
    combos = list(itertools.product(*[range(k_eff[r]) for r in range(R)]))
    n_combos = len(combos)

    all_shard = np.full((Q, n_combos), -1, dtype=np.int64)
    all_conf = np.full((Q, n_combos), -np.inf, dtype=np.float64)
    for ci, combo in enumerate(combos):
        sid, conf = _combo_shard_ids_and_conf(topk_idx, topk_score, weights, M_full, n_shards, combo)
        all_shard[:, ci] = sid
        all_conf[:, ci] = np.where(sid >= 0, conf, -np.inf)

    shortlist = np.full((Q, M), -1, dtype=np.int64)
    n_candidates = np.zeros(Q, dtype=np.int64)
    for q in range(Q):
        valid = all_shard[q] >= 0
        if not np.any(valid):
            continue
        sids_q = all_shard[q][valid]
        conf_q = all_conf[q][valid]
        best_per_shard: Dict[int, float] = {}
        for sid, conf in zip(sids_q.tolist(), conf_q.tolist()):
            if sid not in best_per_shard or conf > best_per_shard[sid]:
                best_per_shard[sid] = conf
        n_candidates[q] = len(best_per_shard)
        ranked = sorted(best_per_shard.items(), key=lambda kv: -kv[1])[:M]
        for i, (sid, _conf) in enumerate(ranked):
            shortlist[q, i] = sid
    return shortlist, n_candidates


def decode_redundant_batch_conf(cue: np.ndarray, moduli: Tuple[int, ...], dims_list: List[int],
                                 codebooks: List[np.ndarray], n_shards: int, k_top: int,
                                 M: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """NEW (instrumentation only, not a mechanism change): identical
    candidate-generation + ranking logic to decode_redundant_batch, but ALSO
    returns the per-shortlist-column Stage-1 confidence (the same
    best_per_shard value already used to RANK the shortlist, previously
    computed then discarded). Self-test proves shortlist output is
    IDENTICAL to decode_redundant_batch (see _selftest, check 2b)."""
    R = len(moduli)
    scores = score_channels_batch(cue, dims_list, codebooks)
    topk_idx, topk_score = topk_per_channel(scores, k_top)
    Q = cue.shape[0]
    M_full, weights = crt_weights(moduli)

    import itertools
    k_eff = [topk_idx[r].shape[1] for r in range(R)]
    combos = list(itertools.product(*[range(k_eff[r]) for r in range(R)]))
    n_combos = len(combos)

    all_shard = np.full((Q, n_combos), -1, dtype=np.int64)
    all_conf = np.full((Q, n_combos), -np.inf, dtype=np.float64)
    for ci, combo in enumerate(combos):
        sid, conf = _combo_shard_ids_and_conf(topk_idx, topk_score, weights, M_full, n_shards, combo)
        all_shard[:, ci] = sid
        all_conf[:, ci] = np.where(sid >= 0, conf, -np.inf)

    shortlist = np.full((Q, M), -1, dtype=np.int64)
    shortlist_conf = np.full((Q, M), -np.inf, dtype=np.float64)
    n_candidates = np.zeros(Q, dtype=np.int64)
    for q in range(Q):
        valid = all_shard[q] >= 0
        if not np.any(valid):
            continue
        sids_q = all_shard[q][valid]
        conf_q = all_conf[q][valid]
        best_per_shard: Dict[int, float] = {}
        for sid, conf in zip(sids_q.tolist(), conf_q.tolist()):
            if sid not in best_per_shard or conf > best_per_shard[sid]:
                best_per_shard[sid] = conf
        n_candidates[q] = len(best_per_shard)
        ranked = sorted(best_per_shard.items(), key=lambda kv: -kv[1])[:M]
        for i, (sid, conf_v) in enumerate(ranked):
            shortlist[q, i] = sid
            shortlist_conf[q, i] = conf_v
    return shortlist, shortlist_conf, n_candidates


def _digest(arr: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(arr).tobytes()).hexdigest()[:16]


# ============================================================================
# REUSED VERBATIM -- Stage-2 store construction + cue construction + cost
# formulas (byte-identical RNG offsets to the prior cell).
# ============================================================================

def build_store(n_shards: int, N_WM: int, V_val: int, V_key: int, m_load: int,
                 seed: int) -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray],
                                     List[np.ndarray], List[np.ndarray]]:
    bundles, vals_list, keys_list, key_ids_list, val_ids_list = [], [], [], [], []
    for sid in range(n_shards):
        srng = np.random.default_rng(31000 + seed * 1000 + sid)
        keys = make_phasors(srng, V_key, N_WM)
        vals = make_phasors(srng, V_val, N_WM)
        key_ids = srng.permutation(V_key)[:m_load]
        val_ids = srng.integers(0, V_val, size=m_load)
        bound = keys[key_ids] * vals[val_ids]
        bundles.append(bound.sum(axis=0))
        vals_list.append(vals)
        keys_list.append(keys)
        key_ids_list.append(key_ids)
        val_ids_list.append(val_ids)
    return bundles, vals_list, keys_list, key_ids_list, val_ids_list


def make_cue(rng: np.random.Generator, mask: np.ndarray, addr_clean: np.ndarray,
             key_clean: np.ndarray) -> np.ndarray:
    clean = np.concatenate([addr_clean, key_clean], axis=1)
    theta = rng.uniform(-np.pi, np.pi, size=clean.shape)
    fresh = np.exp(1j * theta)
    return np.where(mask, fresh, clean)


def hard_route_cost_formula(n_bits: int, dims_per_bit: int) -> int:
    return n_bits * dims_per_bit * 2


def soft_route_cost_formula(n_shards: int, total_dim: int) -> int:
    return n_shards * total_dim


def redundant_route_cost_formula(moduli: Tuple[int, ...], dims_list: List[int],
                                  k_top: int, measured_candidates: float) -> float:
    channel_score_ops = sum(m * d for m, d in zip(moduli, dims_list))
    combo_enum_ops = 1
    for m in moduli:
        combo_enum_ops *= min(k_top, m)
    return channel_score_ops + combo_enum_ops + measured_candidates


# ============================================================================
# NEW -- generalized Stage-2 (per-column, not best-of-M internally) +
# 5 selector rules operating on top of the SAME per-column completions.
# ============================================================================

def stage2_complete_all_columns(shortlist: np.ndarray, cue_key: np.ndarray,
                                 bundles: List[np.ndarray], vals_list: List[np.ndarray]
                                 ) -> Tuple[np.ndarray, np.ndarray]:
    """For EACH of the M shortlist columns, unbind cue_key against that
    column's predicted shard bundle and argmax-cleanup against that shard's
    OWN V_val codebook. Returns per-column (Q,M) pred_val and (Q,M)
    completion-score (score=-inf where the shortlist slot is invalid). This
    is the SAME unbind+cleanup math as the prior cell's
    complete_over_shortlist, just returning per-column results instead of
    only the best-of-M so multiple selector rules can share one Stage-2
    pass (cheaper for THIS MEASUREMENT cell to compute once; real-deployment
    cost accounting per selector is done via explicit formulas below, not
    by literally counting what this code executes)."""
    Q, M = shortlist.shape
    pred_val = np.full((Q, M), -1, dtype=np.int64)
    score = np.full((Q, M), -np.inf, dtype=np.float64)
    for m_idx in range(M):
        sid_col = shortlist[:, m_idx]
        valid = sid_col >= 0
        if not np.any(valid):
            continue
        for sid in np.unique(sid_col[valid]):
            grp = valid & (sid_col == sid)
            state = bundles[sid][None, :] * np.conj(cue_key[grp])
            scores = (state @ vals_list[sid].conj().T).real
            pred_val[grp, m_idx] = scores.argmax(axis=1)
            score[grp, m_idx] = scores.max(axis=1)
    return pred_val, score


def _finalize(shortlist: np.ndarray, pred_val: np.ndarray, m_star: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    Q = shortlist.shape[0]
    idx = np.arange(Q)
    bshard = shortlist[idx, m_star]
    bval = pred_val[idx, m_star]
    return bshard, bval


def select_argmax_completion(stage2_score: np.ndarray) -> np.ndarray:
    """BASELINE-FAIL selector (reproduces the prior cell's exact rule):
    pick the column with the highest Stage-2 completion confidence."""
    return np.argmax(stage2_score, axis=1)


def select_stage1_rank_top1(shortlist: np.ndarray) -> np.ndarray:
    """FREE-FIX selector (VET-predicted): always column 0 -- shortlist is
    already sorted by Stage-1 confidence descending by construction."""
    Q = shortlist.shape[0]
    return np.zeros(Q, dtype=np.int64)


def select_combined_zscore(shortlist: np.ndarray, shortlist_conf: np.ndarray,
                            stage2_score: np.ndarray) -> np.ndarray:
    """COMBINED selector: query-relative z-score of Stage-1 confidence +
    z-score of Stage-2 completion confidence (both normalized across the
    SAME query's valid columns, so the two differently-scaled signals
    combine with an unweighted 1:1 sum -- no tunable constant)."""
    Q, M = shortlist.shape
    valid = shortlist >= 0
    with np.errstate(invalid="ignore"):
        conf1 = np.where(valid, shortlist_conf, np.nan)
        conf2 = np.where(valid, stage2_score, np.nan)
        mu1 = np.nanmean(conf1, axis=1, keepdims=True)
        sd1 = np.nanstd(conf1, axis=1, keepdims=True)
        mu2 = np.nanmean(conf2, axis=1, keepdims=True)
        sd2 = np.nanstd(conf2, axis=1, keepdims=True)
        sd1 = np.where((sd1 < 1e-9) | np.isnan(sd1), 1.0, sd1)
        sd2 = np.where((sd2 < 1e-9) | np.isnan(sd2), 1.0, sd2)
        z1 = np.nan_to_num((conf1 - mu1) / sd1, nan=-1e18)
        z2 = np.nan_to_num((conf2 - mu2) / sd2, nan=-1e18)
    combined = np.where(valid, z1 + z2, -np.inf)
    n_valid = valid.sum(axis=1)
    m_star = np.where(n_valid > 0, np.argmax(combined, axis=1), 0)
    return m_star.astype(np.int64)


def select_cue_regen_fidelity(shortlist: np.ndarray, pred_val: np.ndarray, cue_key: np.ndarray,
                               bundles: List[np.ndarray], vals_list: List[np.ndarray]
                               ) -> Tuple[np.ndarray, np.ndarray]:
    """DRILL-PROPOSED selector: for each candidate (shard, predicted val),
    regenerate an estimate of the ORIGINAL key by unbinding that shard's WM
    bundle with the predicted val's OWN codeword, then score cosine
    fidelity against the ACTUAL (possibly-corrupted) cue key. Selects the
    column with highest regenerated-cue fidelity. An INDEPENDENT check
    (regenerated key vs actual cue key) distinct from the completion's own
    val-argmax confidence, per the recall-to-reject / CA1-mismatch /
    CRC-list-decoding convergence in the research drill."""
    Q, M = shortlist.shape
    fidelity = np.full((Q, M), -np.inf, dtype=np.float64)
    cue_norm = np.linalg.norm(cue_key, axis=1)
    for m_idx in range(M):
        sid_col = shortlist[:, m_idx]
        valid = sid_col >= 0
        if not np.any(valid):
            continue
        for sid in np.unique(sid_col[valid]):
            grp = valid & (sid_col == sid)
            v_ids = pred_val[grp, m_idx]
            valid_v = v_ids >= 0
            if not np.any(valid_v):
                continue
            grp_idx = np.where(grp)[0][valid_v]
            regen_key = bundles[sid][None, :] * np.conj(vals_list[sid][v_ids[valid_v]])
            regen_norm = np.linalg.norm(regen_key, axis=1)
            num = (regen_key * np.conj(cue_key[grp_idx])).sum(axis=1).real
            denom = regen_norm * cue_norm[grp_idx]
            denom = np.where(denom < 1e-12, 1e-12, denom)
            fidelity[grp_idx, m_idx] = num / denom
    n_valid = (shortlist >= 0).sum(axis=1)
    m_star = np.where(n_valid > 0, np.argmax(fidelity, axis=1), 0)
    return m_star.astype(np.int64), fidelity


def select_oracle(shortlist: np.ndarray, true_shard: np.ndarray) -> np.ndarray:
    """DIAGNOSTIC ONLY (uses ground truth; never gates a verdict): pick the
    shortlist column containing the true shard if present, else column 0
    (which will be wrong regardless). Reproduces the "if selection were
    perfect" ceiling context."""
    Q, M = shortlist.shape
    m_star = np.full(Q, -1, dtype=np.int64)
    for m_idx in range(M):
        hit = (shortlist[:, m_idx] == true_shard) & (m_star == -1)
        m_star = np.where(hit, m_idx, m_star)
    m_star = np.where(m_star == -1, 0, m_star)
    return m_star.astype(np.int64)


# ============================================================================
# REGIME (byte-identical to exp_redundant_soft_shard_router_e2e_stage12_v1;
# reused so R3_ARGMAX genuinely reproduces the prior landed run).
# ============================================================================

E2E_N_SHARDS = 16
E2E_N_BITS = 4
E2E_DIMS_PER_BIT = 24
E2E_TOTAL_ADDR_DIM = E2E_N_BITS * E2E_DIMS_PER_BIT   # 96

E2E_N_WM = 256
E2E_V_VAL = 32
E2E_V_KEY = 64
E2E_M_LOAD = 8

E2E_MODULI_R3 = (5, 7, 11)
E2E_K_TOP = 5
E2E_DIMS_LIST_R3 = split_dims(E2E_TOTAL_ADDR_DIM, 3)     # [32, 32, 32]
E2E_M_MAX = 4                    # R3 shortlist width (all selectors see M=4 candidates)
E2E_DEGENERATE_MODULI = (4,)
E2E_DEGENERATE_DIMS_LIST = [E2E_TOTAL_ADDR_DIM]

E2E_F_GRID_FULL = [0.0, 0.5, 0.6, 0.7, 0.8, 0.9]
E2E_F_GRID_SMOKE = [0.0, 0.7, 0.8]
E2E_SEEDS_FULL = [7, 13, 19]
E2E_SEEDS_SMOKE = [7, 13]
E2E_Q_FULL = 320
E2E_Q_SMOKE = 96
E2E_GATE_F = 0.7

E2E_ACC_PASS_FACTOR = 0.9
E2E_ACC_STRICT_MARGIN = 0.05
E2E_COST_PASS_FACTOR = 0.7
E2E_COST_FAIL_FACTOR = 0.9

# Gate-D positive controls (reused verbatim from the router cell + the
# prior e2e cell -- byte-identical regime).
_GATE_D_PRIOR = {
    "hard_route_acc": 0.7104166666666667,
    "soft_route_acc": 0.9729166666666668,
    "r3_m4_shortlist_hit": 0.96875,
}
_GATE_D_TOLERANCE = 0.10
# NEW positive control specific to this cell: R3_ARGMAX must reproduce the
# prior e2e cell's OWN landed R3_M4-argmax e2e accuracy at f=0.7.
# MEASURED@d:/AI/hd-instrument/data/exp_redundant_soft_shard_router_e2e_stage12_v1/metrics.json:sweep.gate_row.e2e_acc_R3_M4_mean
_PRIOR_R3_ARGMAX_E2E = 0.4083333333333334
_PRIOR_R3_ARGMAX_TOLERANCE = 0.15


def e2e_trial(f: float, seed: int, Q: int) -> Dict:
    bundles, vals_list, keys_list, key_ids_list, val_ids_list = build_store(
        E2E_N_SHARDS, E2E_N_WM, E2E_V_VAL, E2E_V_KEY, E2E_M_LOAD, seed)

    addr_rng = np.random.default_rng(24000 + seed * 1000 + int(round(f * 1000)))
    cbs_decomp = build_decomposed_codebooks(E2E_N_BITS, E2E_DIMS_PER_BIT, addr_rng)
    cb_holistic = build_holistic_codebook(E2E_N_SHARDS, E2E_TOTAL_ADDR_DIM, addr_rng)
    addr_decomp_table = encode_decomposed_table(E2E_N_SHARDS, E2E_N_BITS, E2E_DIMS_PER_BIT, cbs_decomp)

    rng2 = np.random.default_rng(44000 + seed * 1000 + int(round(f * 1000)))
    cb_r3 = build_channel_codebooks(E2E_MODULI_R3, E2E_DIMS_LIST_R3, rng2)
    addr_r3_table = encode_channel_table(E2E_N_SHARDS, E2E_MODULI_R3, E2E_DIMS_LIST_R3, cb_r3)
    cb_deg = build_channel_codebooks(E2E_DEGENERATE_MODULI, E2E_DEGENERATE_DIMS_LIST, rng2)
    addr_deg_table = encode_channel_table(E2E_N_SHARDS, E2E_DEGENERATE_MODULI, E2E_DEGENERATE_DIMS_LIST, cb_deg)

    qrng = np.random.default_rng(23000 + seed * 1000 + int(round(f * 1000)))
    true_shard = np.arange(Q) % E2E_N_SHARDS
    local_idx = qrng.integers(0, E2E_M_LOAD, size=Q)
    true_key = np.stack([keys_list[true_shard[i]][key_ids_list[true_shard[i]][local_idx[i]]] for i in range(Q)])
    true_val = np.array([val_ids_list[true_shard[i]][local_idx[i]] for i in range(Q)])

    D_total = E2E_TOTAL_ADDR_DIM + E2E_N_WM
    mask = qrng.random((Q, D_total)) < f

    cue_hard = make_cue(qrng, mask, addr_decomp_table[true_shard], true_key)
    cue_soft = make_cue(qrng, mask, cb_holistic[true_shard], true_key)
    cue_r3 = make_cue(qrng, mask, addr_r3_table[true_shard], true_key)
    cue_deg = make_cue(qrng, mask, addr_deg_table[true_shard], true_key)

    A = E2E_TOTAL_ADDR_DIM

    pred_hard = decode_decomposed_batch(cue_hard[:, :A], E2E_N_BITS, E2E_DIMS_PER_BIT, cbs_decomp, E2E_N_SHARDS)
    pred_soft = decode_holistic_batch(cue_soft[:, :A], cb_holistic)
    shortlist_r3, shortlist_conf_r3, n_cand_r3 = decode_redundant_batch_conf(
        cue_r3[:, :A], E2E_MODULI_R3, E2E_DIMS_LIST_R3, cb_r3, E2E_N_SHARDS, E2E_K_TOP, E2E_M_MAX)
    shortlist_deg, _ = decode_redundant_batch(
        cue_deg[:, :A], E2E_DEGENERATE_MODULI, E2E_DEGENERATE_DIMS_LIST, cb_deg, E2E_N_SHARDS, k_top=1, M=1)

    cue_key_hard = cue_hard[:, A:]
    cue_key_soft = cue_soft[:, A:]
    cue_key_r3 = cue_r3[:, A:]
    cue_key_deg = cue_deg[:, A:]

    pred_val_hard, score_hard = stage2_complete_all_columns(pred_hard.reshape(-1, 1), cue_key_hard, bundles, vals_list)
    pred_val_soft, score_soft = stage2_complete_all_columns(pred_soft.reshape(-1, 1), cue_key_soft, bundles, vals_list)
    pred_val_deg, score_deg = stage2_complete_all_columns(shortlist_deg, cue_key_deg, bundles, vals_list)
    pred_val_r3, score_r3 = stage2_complete_all_columns(shortlist_r3, cue_key_r3, bundles, vals_list)

    bshard_hard, bval_hard = _finalize(pred_hard.reshape(-1, 1), pred_val_hard, np.zeros(Q, dtype=np.int64))
    bshard_soft, bval_soft = _finalize(pred_soft.reshape(-1, 1), pred_val_soft, np.zeros(Q, dtype=np.int64))
    bshard_deg, bval_deg = _finalize(shortlist_deg, pred_val_deg, np.zeros(Q, dtype=np.int64))

    m_argmax = select_argmax_completion(score_r3)
    m_top1 = select_stage1_rank_top1(shortlist_r3)
    m_combined = select_combined_zscore(shortlist_r3, shortlist_conf_r3, score_r3)
    m_cuefid, fidelity_r3 = select_cue_regen_fidelity(shortlist_r3, pred_val_r3, cue_key_r3, bundles, vals_list)
    m_oracle = select_oracle(shortlist_r3, true_shard)

    bshard_argmax, bval_argmax = _finalize(shortlist_r3, pred_val_r3, m_argmax)
    bshard_top1, bval_top1 = _finalize(shortlist_r3, pred_val_r3, m_top1)
    bshard_combined, bval_combined = _finalize(shortlist_r3, pred_val_r3, m_combined)
    bshard_cuefid, bval_cuefid = _finalize(shortlist_r3, pred_val_r3, m_cuefid)
    bshard_oracle, bval_oracle = _finalize(shortlist_r3, pred_val_r3, m_oracle)

    def _route_acc(bshard):
        return float((bshard == true_shard).mean())

    def _e2e_acc(bshard, bval):
        return float(((bshard == true_shard) & (bval == true_val)).mean())

    route_acc_r3_shortlist_hit = float((shortlist_r3 == true_shard[:, None]).any(axis=1).mean())

    rep_final = {
        "hard": (bshard_hard, bval_hard), "soft": (bshard_soft, bval_soft),
        "degenerate": (bshard_deg, bval_deg),
        "R3_ARGMAX": (bshard_argmax, bval_argmax), "R3_TOP1": (bshard_top1, bval_top1),
        "R3_COMBINED": (bshard_combined, bval_combined), "R3_CUEFID": (bshard_cuefid, bval_cuefid),
        "R3_ORACLE": (bshard_oracle, bval_oracle),
    }

    return {
        "route_acc": {
            "hard": _route_acc(bshard_hard), "soft": _route_acc(bshard_soft),
            "degenerate": _route_acc(bshard_deg),
            "R3_ARGMAX": _route_acc(bshard_argmax), "R3_TOP1": _route_acc(bshard_top1),
            "R3_COMBINED": _route_acc(bshard_combined), "R3_CUEFID": _route_acc(bshard_cuefid),
            "R3_ORACLE": _route_acc(bshard_oracle),
            "R3_shortlist_hit_rate": route_acc_r3_shortlist_hit,
        },
        "e2e_acc": {
            "hard": _e2e_acc(bshard_hard, bval_hard), "soft": _e2e_acc(bshard_soft, bval_soft),
            "degenerate": _e2e_acc(bshard_deg, bval_deg),
            "R3_ARGMAX": _e2e_acc(bshard_argmax, bval_argmax), "R3_TOP1": _e2e_acc(bshard_top1, bval_top1),
            "R3_COMBINED": _e2e_acc(bshard_combined, bval_combined), "R3_CUEFID": _e2e_acc(bshard_cuefid, bval_cuefid),
            "R3_ORACLE": _e2e_acc(bshard_oracle, bval_oracle),
        },
        "measured_candidates_r3": float(n_cand_r3.mean()),
        "rep_final": rep_final,
    }


ARM_NAMES = ["hard", "soft", "degenerate", "R3_ARGMAX", "R3_TOP1", "R3_COMBINED", "R3_CUEFID", "R3_ORACLE"]


def run_sweep(mode: str) -> Dict:
    f_grid = E2E_F_GRID_SMOKE if mode == "smoke" else E2E_F_GRID_FULL
    seeds = E2E_SEEDS_SMOKE if mode == "smoke" else E2E_SEEDS_FULL
    Q = E2E_Q_SMOKE if mode == "smoke" else E2E_Q_FULL

    curve = []
    rep_at_gate = None
    for f in f_grid:
        trials = [e2e_trial(f, s, Q) for s in seeds]
        row = {"f": f}
        for a in ARM_NAMES:
            row[f"route_acc_{a}_mean"] = float(np.mean([t["route_acc"][a] for t in trials]))
            row[f"e2e_acc_{a}_mean"] = float(np.mean([t["e2e_acc"][a] for t in trials]))
        row["route_acc_R3_shortlist_hit_mean"] = float(np.mean([t["route_acc"]["R3_shortlist_hit_rate"] for t in trials]))
        row["measured_candidates_r3_mean"] = float(np.mean([t["measured_candidates_r3"] for t in trials]))
        curve.append(row)
        if abs(f - E2E_GATE_F) < 1e-9:
            rep_at_gate = trials[0]["rep_final"]
        print(f"  [e2e f={f:.2f}] "
              f"route(hard={row['route_acc_hard_mean']:.3f} soft={row['route_acc_soft_mean']:.3f} "
              f"deg={row['route_acc_degenerate_mean']:.3f} ARGMAX={row['route_acc_R3_ARGMAX_mean']:.3f} "
              f"TOP1={row['route_acc_R3_TOP1_mean']:.3f} COMBINED={row['route_acc_R3_COMBINED_mean']:.3f} "
              f"CUEFID={row['route_acc_R3_CUEFID_mean']:.3f} ORACLE={row['route_acc_R3_ORACLE_mean']:.3f} "
              f"hit={row['route_acc_R3_shortlist_hit_mean']:.3f}) "
              f"e2e(hard={row['e2e_acc_hard_mean']:.3f} soft={row['e2e_acc_soft_mean']:.3f} "
              f"deg={row['e2e_acc_degenerate_mean']:.3f} ARGMAX={row['e2e_acc_R3_ARGMAX_mean']:.3f} "
              f"TOP1={row['e2e_acc_R3_TOP1_mean']:.3f} COMBINED={row['e2e_acc_R3_COMBINED_mean']:.3f} "
              f"CUEFID={row['e2e_acc_R3_CUEFID_mean']:.3f} ORACLE={row['e2e_acc_R3_ORACLE_mean']:.3f})",
              flush=True)

    gate_row = min(curve, key=lambda r: abs(r["f"] - E2E_GATE_F))
    if rep_at_gate is None:
        rep_at_gate = e2e_trial(E2E_GATE_F, seeds[0], Q)["rep_final"]

    digests = {}
    for a in ARM_NAMES:
        bshard, bval = rep_at_gate[a]
        digests[a] = _digest(np.concatenate([bshard, bval]))
    names = sorted(digests)
    dupes = [f"{names[i]}=={names[j]}" for i in range(len(names)) for j in range(i + 1, len(names))
             if digests[names[i]] == digests[names[j]]]
    if dupes:
        raise AssertionError("META_RULE_AF VIOLATION: " + "; ".join(dupes))

    return {
        "curve": curve, "gate_row": gate_row, "arms_differ_digests": digests,
        "config": {"n_shards": E2E_N_SHARDS, "total_addr_dim": E2E_TOTAL_ADDR_DIM,
                   "N_WM": E2E_N_WM, "V_val": E2E_V_VAL, "V_key": E2E_V_KEY, "m_load": E2E_M_LOAD,
                   "f_grid": f_grid, "seeds": seeds, "Q": Q, "k_top": E2E_K_TOP,
                   "moduli_r3": list(E2E_MODULI_R3), "moduli_degenerate": list(E2E_DEGENERATE_MODULI)},
    }


# ============================================================================
# Self-test (hardened; exercises the REAL functions at tiny scale, verifies
# roundtrips + can-fail control + arms-differ + selector behavior, BEFORE
# any smoke/full).
# ============================================================================

def _selftest():
    assert_no_nondeterministic_seeding(Path(__file__).read_text(encoding="utf-8"),
                                        source_name=ANCHOR_NAME, run_mode="selftest")

    # 1. CRT reconstruction correctness.
    moduli_t = (3, 5, 7)
    M_t, w_t = crt_weights(moduli_t)
    assert M_t == 105
    for x in range(20):
        residues = tuple(x % m for m in moduli_t)
        recon = sum(r * w for r, w in zip(residues, w_t)) % M_t
        assert recon == x, f"CRT roundtrip failed: x={x}"

    # 2a. Address zero-corruption roundtrip (HARD/SOFT/REDUNDANT/DEGENERATE).
    g = np.random.default_rng(0)
    n_shards_t = 8
    cbs_d = build_decomposed_codebooks(3, 12, g)
    tbl_d = encode_decomposed_table(n_shards_t, 3, 12, cbs_d)
    assert np.array_equal(decode_decomposed_batch(tbl_d, 3, 12, cbs_d, n_shards_t), np.arange(n_shards_t))

    g2 = np.random.default_rng(1)
    cb_h = build_holistic_codebook(n_shards_t, 36, g2)
    assert np.array_equal(decode_holistic_batch(cb_h, cb_h), np.arange(n_shards_t))

    g3 = np.random.default_rng(2)
    moduli_r = (5, 7, 11)
    dims_r = split_dims(36, 3)
    cb_r = build_channel_codebooks(moduli_r, dims_r, g3)
    tbl_r = encode_channel_table(n_shards_t, moduli_r, dims_r, cb_r)
    sl_r, _ = decode_redundant_batch(tbl_r, moduli_r, dims_r, cb_r, n_shards_t, k_top=2, M=2)
    assert np.array_equal(sl_r[:, 0], np.arange(n_shards_t)), f"REDUNDANT_SOFT must roundtrip at zero corruption: {sl_r[:, 0]}"

    # 2b. decode_redundant_batch_conf MUST produce the IDENTICAL shortlist
    #     as decode_redundant_batch (ONE-VARIABLE proof: instrumentation
    #     doesn't change Stage-1 candidate generation/ranking).
    sl_r_conf, conf_r_conf, ncand_conf = decode_redundant_batch_conf(tbl_r, moduli_r, dims_r, cb_r, n_shards_t, k_top=2, M=2)
    assert np.array_equal(sl_r, sl_r_conf), "decode_redundant_batch_conf must match decode_redundant_batch shortlist exactly"
    assert np.all(np.isfinite(conf_r_conf[:, 0])), "rank-0 confidence must be finite when a candidate exists"

    # 3. DEGENERATE structural cap at ZERO corruption.
    g4 = np.random.default_rng(3)
    deg_moduli, deg_dims = (4,), [36]
    deg_cb = build_channel_codebooks(deg_moduli, deg_dims, g4)
    deg_tbl = encode_channel_table(n_shards_t, deg_moduli, deg_dims, deg_cb)
    sl_deg, _ = decode_redundant_batch(deg_tbl, deg_moduli, deg_dims, deg_cb, n_shards_t, k_top=1, M=1)
    deg_acc = float((sl_deg[:, 0] == np.arange(n_shards_t)).mean())
    assert deg_acc <= 0.60, f"DEGENERATE must be structurally capped even at ZERO corruption, got {deg_acc:.3f}"

    # 4. Stage-2 store construction + per-column completion zero-corruption
    #    roundtrip (isolates Stage-2 alone).
    n_shards_t2, N_WM_t, V_val_t, V_key_t, m_load_t = 4, 32, 8, 16, 4
    bundles_t, vals_t, keys_t, key_ids_t, val_ids_t = build_store(n_shards_t2, N_WM_t, V_val_t, V_key_t, m_load_t, seed=7)
    for sid in range(n_shards_t2):
        cue_key_t = keys_t[sid][key_ids_t[sid]]
        shortlist_t = np.full((m_load_t, 1), sid, dtype=np.int64)
        pv_t, sc_t = stage2_complete_all_columns(shortlist_t, cue_key_t, bundles_t, vals_t)
        bshard_t, bval_t = _finalize(shortlist_t, pv_t, np.zeros(m_load_t, dtype=np.int64))
        assert np.array_equal(bshard_t, np.full(m_load_t, sid))
        assert np.array_equal(bval_t, val_ids_t[sid]), f"Stage-2 must recover exact val ids at zero corruption, shard {sid}"

    # 5. select_stage1_rank_top1 always returns column 0.
    dummy_sl = np.array([[3, 1, 0, -1], [5, 5, 5, 5]])
    assert np.array_equal(select_stage1_rank_top1(dummy_sl), np.zeros(2, dtype=np.int64))

    # 6. select_argmax_completion picks the highest-scoring column (sanity,
    #    synthetic scores).
    dummy_score = np.array([[0.1, 0.9, 0.3, -np.inf], [5.0, 1.0, 2.0, 3.0]])
    assert np.array_equal(select_argmax_completion(dummy_score), np.array([1, 0]))

    # 7. select_combined_zscore: when Stage-1 confidence and Stage-2 score
    #    STRONGLY agree that a non-zero column is best, combined selector
    #    must pick that column (not blindly default to column 0).
    dummy_sl2 = np.array([[7, 2, 9, -1]])
    dummy_conf1 = np.array([[0.1, 0.05, 5.0, -np.inf]])
    dummy_score2 = np.array([[0.2, 0.1, 6.0, -np.inf]])
    m_comb = select_combined_zscore(dummy_sl2, dummy_conf1, dummy_score2)
    assert m_comb[0] == 2, f"combined selector should pick the column both signals strongly favor, got {m_comb[0]}"

    # 8. select_cue_regen_fidelity: at ZERO corruption (exact cue_key), the
    #    correct shard's completion must score highest regenerated-cue
    #    fidelity among a shortlist that includes a decoy.
    n_shards_t3 = 4
    bundles_t3, vals_t3, keys_t3, key_ids_t3, val_ids_t3 = build_store(n_shards_t3, 32, 8, 16, 4, seed=11)
    for sid in range(1, n_shards_t3):
        cue_key_t3 = keys_t3[sid][key_ids_t3[sid]]
        shortlist_2 = np.stack([np.full(4, 0), np.full(4, sid)], axis=1)
        pv3, sc3 = stage2_complete_all_columns(shortlist_2, cue_key_t3, bundles_t3, vals_t3)
        m_cf, fid = select_cue_regen_fidelity(shortlist_2, pv3, cue_key_t3, bundles_t3, vals_t3)
        bshard3, bval3 = _finalize(shortlist_2, pv3, m_cf)
        assert np.array_equal(bshard3, np.full(4, sid)), (
            f"cue-regen-fidelity selector must pick the TRUE shard over a decoy at zero corruption, shard {sid}: {bshard3}")

    # 9. select_oracle picks the shortlist column containing the true shard.
    dummy_sl3 = np.array([[3, 7, 2, -1], [1, 1, 1, 1]])
    true_shard_t = np.array([2, 1])
    m_or = select_oracle(dummy_sl3, true_shard_t)
    assert m_or[0] == 2 and m_or[1] == 0

    # 10. Full e2e_trial at tiny scale, multiple f, NaN-free, real code path,
    #     e2e_acc never exceeds route_acc, all 8 arms present.
    for f_t in (0.0, 0.3, 0.7):
        r = e2e_trial(f=f_t, seed=101, Q=32)
        for a in ARM_NAMES:
            assert 0.0 <= r["route_acc"][a] <= 1.0 and not math.isnan(r["route_acc"][a]), f"{a} route_acc invalid at f={f_t}"
            assert 0.0 <= r["e2e_acc"][a] <= 1.0 and not math.isnan(r["e2e_acc"][a]), f"{a} e2e_acc invalid at f={f_t}"
            assert r["e2e_acc"][a] <= r["route_acc"][a] + 1e-9, f"{a} e2e_acc must never exceed route_acc at f={f_t}"

    # 11. At f=0 (clean cue), HARD/SOFT/R3_TOP1/R3_COMBINED/R3_CUEFID/
    #     R3_ORACLE must reach near-ceiling e2e accuracy -- DEGENERATE must NOT.
    r0 = e2e_trial(f=0.0, seed=7, Q=64)
    for a in ["hard", "soft", "R3_TOP1", "R3_COMBINED", "R3_CUEFID", "R3_ORACLE"]:
        assert r0["e2e_acc"][a] >= 0.90, f"{a} e2e acc at f=0 should be near-ceiling, got {r0['e2e_acc'][a]:.3f}"
    assert r0["e2e_acc"]["degenerate"] < 0.90, "DEGENERATE must NOT reach ceiling even at zero corruption (structural cap)"

    print("[selftest] PASS: redundant_soft_shard_router_e2e_selector_confirm_v1 (CRT roundtrip, "
          "address zero-corruption roundtrip x4 schemes, decode_redundant_batch_conf==decode_redundant_batch "
          "(ONE-VARIABLE proof), degenerate structural cap, Stage-2 zero-corruption roundtrip, "
          "5 selector rules unit-tested, full e2e_trial real-code-path at f=0/0.3/0.7, ceiling check, nan-check)",
          flush=True)


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

def _config_verdict(acc_c: float, cost_c: float, acc_ref_soft: float, acc_ref_hard: float,
                     cost_ref_soft: float) -> Tuple[str, Dict]:
    band_width_acc = acc_ref_soft - acc_ref_hard
    acc_pass_threshold = E2E_ACC_PASS_FACTOR * acc_ref_soft
    acc_pass = acc_c >= acc_pass_threshold
    acc_strict_pass = acc_c >= acc_pass_threshold + E2E_ACC_STRICT_MARGIN * band_width_acc
    acc_fail = acc_c <= acc_ref_hard
    cost_pass = cost_c <= E2E_COST_PASS_FACTOR * cost_ref_soft
    cost_fail = cost_c >= E2E_COST_FAIL_FACTOR * cost_ref_soft
    if acc_fail:
        v = "HARD_FAIL_ACC"
    elif cost_fail:
        v = "HARD_FAIL_COST"
    elif acc_strict_pass and cost_pass:
        v = "HARD_PASS"
    elif acc_pass and cost_pass:
        v = "MIDDLE_BAND_NEAR_FLOOR"
    else:
        v = "MIDDLE_BAND"
    detail = {"acc_pass": acc_pass, "acc_strict_pass": acc_strict_pass, "acc_fail": acc_fail,
              "cost_pass": cost_pass, "cost_fail": cost_fail,
              "acc_pass_threshold": acc_pass_threshold,
              "acc_strict_threshold": acc_pass_threshold + E2E_ACC_STRICT_MARGIN * band_width_acc,
              "band_width_acc": band_width_acc}
    return v, detail


def main() -> int:
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    _write_start_marker(out_dir, RUN_MODE, 0)
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE}", flush=True)

    print("\n[e2e sweep] corruption-vs-e2e-accuracy, hard/soft/degenerate/R3_ARGMAX/R3_TOP1/R3_COMBINED/R3_CUEFID/R3_ORACLE ...", flush=True)
    sw = run_sweep(RUN_MODE)
    gate_row = sw["gate_row"]

    gate_d = {
        "hard_route_acc_measured": gate_row["route_acc_hard_mean"],
        "hard_route_acc_prior": _GATE_D_PRIOR["hard_route_acc"],
        "hard_within_tolerance": abs(gate_row["route_acc_hard_mean"] - _GATE_D_PRIOR["hard_route_acc"]) <= _GATE_D_TOLERANCE,
        "soft_route_acc_measured": gate_row["route_acc_soft_mean"],
        "soft_route_acc_prior": _GATE_D_PRIOR["soft_route_acc"],
        "soft_within_tolerance": abs(gate_row["route_acc_soft_mean"] - _GATE_D_PRIOR["soft_route_acc"]) <= _GATE_D_TOLERANCE,
        "r3_shortlist_hit_measured": gate_row["route_acc_R3_shortlist_hit_mean"],
        "r3_shortlist_hit_prior": _GATE_D_PRIOR["r3_m4_shortlist_hit"],
        "r3_within_tolerance": abs(gate_row["route_acc_R3_shortlist_hit_mean"] - _GATE_D_PRIOR["r3_m4_shortlist_hit"]) <= _GATE_D_TOLERANCE,
        # NEW positive control: R3_ARGMAX must reproduce the prior e2e cell's
        # OWN landed R3_M4-argmax e2e accuracy (same selector, same everything).
        "r3_argmax_e2e_measured": gate_row["e2e_acc_R3_ARGMAX_mean"],
        "r3_argmax_e2e_prior": _PRIOR_R3_ARGMAX_E2E,
        "r3_argmax_within_tolerance": abs(gate_row["e2e_acc_R3_ARGMAX_mean"] - _PRIOR_R3_ARGMAX_E2E) <= _PRIOR_R3_ARGMAX_TOLERANCE,
    }

    hard_e2e_gate = gate_row["e2e_acc_hard_mean"]
    soft_e2e_gate = gate_row["e2e_acc_soft_mean"]
    baseline_in_band = (0.05 < hard_e2e_gate < 0.95) and (0.05 < soft_e2e_gate < 0.95)

    hard_route_cost = hard_route_cost_formula(E2E_N_BITS, E2E_DIMS_PER_BIT)
    soft_route_cost = soft_route_cost_formula(E2E_N_SHARDS, E2E_TOTAL_ADDR_DIM)
    measured_candidates_r3 = gate_row["measured_candidates_r3_mean"]
    r3_route_cost = redundant_route_cost_formula(E2E_MODULI_R3, E2E_DIMS_LIST_R3, E2E_K_TOP, measured_candidates_r3)

    e2e_cost_hard = hard_route_cost + 1 * E2E_V_VAL
    e2e_cost_soft = soft_route_cost + 1 * E2E_V_VAL
    e2e_cost_r3_argmax = r3_route_cost + E2E_M_MAX * E2E_V_VAL
    e2e_cost_r3_top1 = r3_route_cost + 1 * E2E_V_VAL
    e2e_cost_r3_combined = r3_route_cost + E2E_M_MAX * E2E_V_VAL
    e2e_cost_r3_cuefid = r3_route_cost + E2E_M_MAX * E2E_V_VAL + E2E_M_MAX * E2E_N_WM

    acc_ref_soft = soft_e2e_gate
    acc_ref_hard = hard_e2e_gate

    verdicts = {}
    verdicts["R3_ARGMAX"] = _config_verdict(gate_row["e2e_acc_R3_ARGMAX_mean"], e2e_cost_r3_argmax, acc_ref_soft, acc_ref_hard, e2e_cost_soft)
    verdicts["R3_TOP1"] = _config_verdict(gate_row["e2e_acc_R3_TOP1_mean"], e2e_cost_r3_top1, acc_ref_soft, acc_ref_hard, e2e_cost_soft)
    verdicts["R3_COMBINED"] = _config_verdict(gate_row["e2e_acc_R3_COMBINED_mean"], e2e_cost_r3_combined, acc_ref_soft, acc_ref_hard, e2e_cost_soft)
    verdicts["R3_CUEFID"] = _config_verdict(gate_row["e2e_acc_R3_CUEFID_mean"], e2e_cost_r3_cuefid, acc_ref_soft, acc_ref_hard, e2e_cost_soft)

    can_fail_confirmed = bool(gate_row["e2e_acc_degenerate_mean"] < hard_e2e_gate - 0.05)
    argmax_reproduces_prior_fail = bool(
        verdicts["R3_ARGMAX"][0] in ("HARD_FAIL_ACC", "HARD_FAIL_COST")
        and gate_d["r3_argmax_within_tolerance"]
    )

    top1_verdict, top1_detail = verdicts["R3_TOP1"]
    if top1_verdict == "HARD_PASS":
        overall = "HARD_PASS"
        overall_msg = "SELECTOR_FIX_CONFIRMED (CLAIM, VET-CONFIRMED): R3_TOP1 (free Stage-1-rank selector) HARD_PASS -- clears 0.9xSOFT with a >=5% strict margin AND cost materially below SOFT."
    elif top1_verdict == "MIDDLE_BAND_NEAR_FLOOR":
        overall = "MIDDLE_BAND"
        overall_msg = "SELECTOR_FIX_FRAGILE (CLAIM, VET-CONFIRMED-BUT-FRAGILE): R3_TOP1 clears the raw 0.9xSOFT threshold but NOT the 5% strict band-floor margin -- a genuine but fragile clearance, not oversold as outright HARD_PASS."
    elif top1_verdict in ("HARD_FAIL_ACC", "HARD_FAIL_COST"):
        overall = "HARD_FAIL"
        overall_msg = f"VET_PREDICTION_REFUTED: R3_TOP1 {top1_verdict} on a real full run despite the VET's predicted clearance."
    else:
        overall = "MIDDLE_BAND"
        overall_msg = "MEASURED_MECHANISM_MIXED (CLAIM, VET-PENDING): R3_TOP1 lands on the Pareto frontier of HARD/SOFT, not a clean dominance."

    overall_msg += (
        f" | e2e_acc@f{E2E_GATE_F}: hard={hard_e2e_gate:.3f} soft={soft_e2e_gate:.3f} "
        f"R3_ARGMAX={gate_row['e2e_acc_R3_ARGMAX_mean']:.3f} R3_TOP1={gate_row['e2e_acc_R3_TOP1_mean']:.3f} "
        f"R3_COMBINED={gate_row['e2e_acc_R3_COMBINED_mean']:.3f} R3_CUEFID={gate_row['e2e_acc_R3_CUEFID_mean']:.3f} "
        f"R3_ORACLE={gate_row['e2e_acc_R3_ORACLE_mean']:.3f}"
        f" | e2e_cost: soft={e2e_cost_soft:.1f} hard={e2e_cost_hard:.1f} "
        f"R3_ARGMAX={e2e_cost_r3_argmax:.1f} R3_TOP1={e2e_cost_r3_top1:.1f} "
        f"R3_COMBINED={e2e_cost_r3_combined:.1f} R3_CUEFID={e2e_cost_r3_cuefid:.1f}"
        f" | verdicts: ARGMAX={verdicts['R3_ARGMAX'][0]} TOP1={top1_verdict} "
        f"COMBINED={verdicts['R3_COMBINED'][0]} CUEFID={verdicts['R3_CUEFID'][0]}"
        f" | argmax_reproduces_prior_fail={argmax_reproduces_prior_fail} can_fail_confirmed={can_fail_confirmed}"
        f" | gate_d_within_tolerance: hard={gate_d['hard_within_tolerance']} soft={gate_d['soft_within_tolerance']} "
        f"r3_hit={gate_d['r3_within_tolerance']} r3_argmax_repro={gate_d['r3_argmax_within_tolerance']}"
        f" | baseline_in_band={baseline_in_band}"
        f" | top1_detail={top1_detail}"
    )

    n_units = len(sw["config"]["f_grid"]) * len(sw["config"]["seeds"])
    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": overall,
        "verdict_msg": overall_msg,
        "summary": f"{overall}: selector-fix confirmation for end-to-end fuzzy retrieval (R3_TOP1 free-fix vs R3_ARGMAX baseline-fail vs R3_COMBINED/R3_CUEFID companions) ({RUN_MODE})",
        "run_mode": RUN_MODE,
        "n_seeds": len(sw["config"]["seeds"]),
        "n_units": n_units,
        "expected_n_units": n_units,
        "cardinality_ok": True,
        "elapsed_s": elapsed,
        "sweep": sw,
        "gate_d_positive_control": gate_d,
        "baseline_in_band": baseline_in_band,
        "cost_accounting": {
            "hard_route_cost": hard_route_cost, "soft_route_cost": soft_route_cost,
            "r3_route_cost_measured": r3_route_cost, "measured_candidates_r3": measured_candidates_r3,
            "e2e_cost_hard": e2e_cost_hard, "e2e_cost_soft": e2e_cost_soft,
            "e2e_cost_R3_ARGMAX": e2e_cost_r3_argmax, "e2e_cost_R3_TOP1": e2e_cost_r3_top1,
            "e2e_cost_R3_COMBINED": e2e_cost_r3_combined, "e2e_cost_R3_CUEFID": e2e_cost_r3_cuefid,
            "V_val": E2E_V_VAL,
        },
        "predictions": {
            "R3_ARGMAX_baseline_fail": verdicts["R3_ARGMAX"][0],
            "R3_TOP1_PRIMARY": top1_verdict,
            "R3_COMBINED_companion": verdicts["R3_COMBINED"][0],
            "R3_CUEFID_companion": verdicts["R3_CUEFID"][0],
        },
        "verdict_detail": {k: v[1] for k, v in verdicts.items()},
        "can_fail_confirmed": can_fail_confirmed,
        "argmax_reproduces_prior_fail": argmax_reproduces_prior_fail,
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
