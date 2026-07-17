"""exp_redundant_soft_shard_router_e2e_seed_robust_boundary_v1 -- 3rd
chain-grade CONVERSION attempt on the cheap-AND-robust end-to-end fuzzy
retrieval line. The prior cell (exp_redundant_soft_shard_router_e2e_
selector_confirm_v1, aacfd1ee3) CONFIRMED the free R3_TOP1 selector (final
answer = Stage-1's own top-ranked shortlist column, no extra Stage-2 fan-out)
but its VET-owned tier was MEASURED_MECHANISM/MIDDLE_BAND: at the single
gate point f=0.7, R3_TOP1 cleared 0.9xSOFT by only ~0.004 (razor-thin), and
per-seed values [0.575, 0.559, 0.541] across only 3 seeds showed 1-of-3
MISSING the bar. The VET's own words: "a seed-robust strict-margin clearance
would be the +CG event."

THIS CELL asks a DIFFERENT, answerable question: rather than re-testing the
SAME fragile f=0.7 gate point with more seeds (which the mean-tracking data
already flags as marginal), find the corruption regime f<=F* where R3_TOP1
clears the bar on EVERY seed, with margin. Full mean-tracking evidence from
the prior landed cell (data/exp_redundant_soft_shard_router_e2e_selector_
confirm_v1/metrics.json:sweep.curve) already showed R3_TOP1 tracking SOFT
TIGHTLY at f=0.5 (e2e 0.952 vs 0.954) and f=0.6 (e2e 0.852 vs 0.858), only
diverging into fragility at f=0.7 (e2e 0.558 vs 0.616). This cell tests
whether that MEAN-level tracking survives PER-SEED at those points, with
n_seeds=11 (>= the task's n>=9 floor) and a FINE f-grid (0.02 steps through
the 0.50-0.70 transition zone) to locate the all-seeds-clear boundary F*
precisely -- not just re-sample the single already-known-fragile f=0.7 point.

PRIOR-WORK CHECK (substrate-KB concept-query, mandatory per exp_dev
discipline): `bash tools/substrate_query.sh "seed robust margin fine
corruption sweep boundary all-seeds-clear multi-seed variance selector fuzzy
retrieval robustness frontier"` -> top-5 hits all cosine<=0.3174, and the
top hit ('seed', cosine=0.3174) is a generic WordNet/VerbNet lexical entry
sourced from data/substrate_index + verbnet_cache + wordnet_cache, NOT a
prior arc-cell match. Next hits (cosine<=0.2871) are generic multi-seed
methodology notes (experiments_backlog.md D3, an unrelated FORM-C single-seed
caveat, an unrelated v32_multiseed_cpu_v1 cap_map entry) -- none address this
cell's specific question (a seed-robust corruption-boundary search for the
R3_TOP1 e2e selector). Genuinely novel, not a rediscovery.

REUSED VERBATIM (byte-identical RNG seed formulas + regime constants) from
exp_redundant_soft_shard_router_e2e_selector_confirm_v1.py (commit
aacfd1ee3), itself reusing exp_redundant_soft_shard_router_e2e_stage12_v1.py
(0f68b7249): store construction, address codebooks (HARD/SOFT/R3/
DEGENERATE), corruption-mask construction, query sampling, Stage-2
completion, cost formulas, R3_TOP1 and R3_ARGMAX selectors. DROPPED (not
needed for THIS question -- the task's ONE-VARIABLE gate holds the selector
fixed to TOP1; the prior cell's R3_COMBINED/R3_CUEFID/R3_ORACLE companion
selectors answered a DIFFERENT question -- "can we do even better than
TOP1" -- which is out of scope here): select_combined_zscore,
select_cue_regen_fidelity, select_oracle. NEW in this cell: the per-(f,seed)
robustness table + the F* contiguous-boundary search logic (see below) --
this is the only genuinely new mechanism, everything upstream of it is
verbatim reuse.

===========================================================================
ARMS (5, all consume the SAME store + SAME per-query true (shard,key,val) +
SAME shared corruption mask; unchanged mechanics from the prior cell)
===========================================================================
HARD, SOFT: reused verbatim reference baselines (route+val).
DEGENERATE: reused verbatim structural must-fail control (product(moduli)=4
  < n_shards=16 -> shards {4..15} structurally unreachable regardless of
  corruption; proves the harness can and does emit a genuinely bad number).
R3_ARGMAX: reused verbatim baseline-fail selector (Gate-D positive control --
  must reproduce the prior cell's own landed R3_ARGMAX e2e accuracy at
  f=0.7 within tolerance; confirms this cell's code path is the SAME
  mechanism, not a look-alike).
R3_TOP1 (PRIMARY, the ONE swept-selector arm; held fixed per design gate #4):
  final = shortlist column 0 (Stage-1's own top-ranked candidate).

===========================================================================
NEW MECHANISM -- per-seed robustness table + F* boundary search
===========================================================================
For every f in a FINE grid and every seed in an n_seeds>=9 pool, this cell
records R3_TOP1's OWN e2e accuracy at that (f, seed), and compares it against
a threshold computed from the ACROSS-SEED MEAN of the SOFT arm at that same f
(threshold(f) = 0.9 * mean_seed(e2e_acc_soft(seed, f)) -- the SAME 0.9x
convention as the prior cell, but the threshold is a FIXED per-f reference
(not refit per seed), so per-seed pass/fail is an honest apples-to-apples
comparison, not p-hacked per seed).

  seed_margin(seed, f)      = e2e_acc_R3_TOP1(seed, f) - threshold(f)
  worst_seed_margin(f)      = min over seeds of seed_margin(seed, f)
  all_seeds_clear(f)        = worst_seed_margin(f) >= 0
  band_width_acc(f)         = mean_seed(e2e_acc_soft(seed,f)) - mean_seed(e2e_acc_hard(seed,f))
  strict_margin_needed(f)   = 0.05 * band_width_acc(f)   (META_RULE_L, band-floor discipline)
  all_seeds_clear_strict(f) = worst_seed_margin(f) >= strict_margin_needed(f)

F* is NOT just "the largest f where all_seeds_clear happens to be True" (a
single non-monotonic blip could satisfy that vacuously and overclaim a
"[0,F*]-scoped" region that isn't actually all-robust). F* is defined as the
CONTIGUOUS-FROM-f=0 boundary:

  F*_raw    = max f in grid such that all_seeds_clear(f') is True for EVERY
              f' <= f in the grid (a genuine "robust from 0 up to here"
              plateau, not a cherry-picked point).
  F*_strict = same, but with all_seeds_clear_strict.

This is the honest scoped chain-grade claim: "cheap-AND-robust retrieval via
R3_TOP1 is seed-robust for corruption in [0, F*]" -- contiguous, not a single
lucky point.

===========================================================================
FALSIFIABLE PRE-REGISTERED BANDS (set BEFORE running FULL; F*_MIN_MEANINGFUL
chosen from the PRIOR cell's own already-landed 3-seed MEAN evidence -- 0.60
is the highest point where the prior mean-tracking data showed R3_TOP1
within <1% relative of SOFT (e2e 0.852 vs 0.858); if F* reaches this bar with
n_seeds=11 the scoped claim validates what the mean data suggested, if it
falls short the mean data was seed-lucky and the honest scope shrinks)
===========================================================================
F_STAR_MIN_MEANINGFUL = 0.60
F_STAR_MIN_ANY        = 0.30   (below this, no meaningful scoped claim at all)

  HARD_PASS  ("SEED_ROBUST_REGIME_CONFIRMED_STRICT"):
    F*_strict >= F_STAR_MIN_MEANINGFUL  AND cost_pass (R3_TOP1 e2e cost <=
    0.7 x SOFT e2e cost, reused cost formula, verified at F*).
  MIDDLE_BAND ("SEED_ROBUST_REGIME_CONFIRMED_RAW_ONLY" -- genuine but
    fragile-at-the-margin scoped region, per META_RULE_L band-floor
    discipline):
    F*_raw >= F_STAR_MIN_MEANINGFUL but F*_strict < F_STAR_MIN_MEANINGFUL,
    OR F_STAR_MIN_ANY <= F*_strict < F_STAR_MIN_MEANINGFUL (a real but
    narrower-than-hoped robust region).
  HARD_FAIL ("NO_SEED_ROBUST_REGIME" -- honest conversion failure, per the
    task's CAN-FAIL requirement):
    F*_raw < F_STAR_MIN_ANY (seed variance defeats robustness almost
    immediately; no meaningful scoped chain-grade claim survives).

CAN-FAIL VERIFICATION (mandatory design gate #2, verified at smoke AND
  FULL): the grid extends past the KNOWN-fragile f=0.70 gate point (to 0.72/
  0.75/0.80) specifically so that `all_seeds_clear(f)` is verified to go
  FALSE somewhere in the sampled range (`can_fail_confirmed_boundary_exists`
  field) -- proves the per-seed discriminator is not vacuously always-True.
  Smoke additionally re-verifies the ORIGINAL argmax_reproduces_prior_fail
  check (R3_ARGMAX HARD_FAIL_ACC at f=0.7, reproducing the prior landed
  0.4083 e2e value within tolerance 0.15) and the DEGENERATE structural cap,
  both reused verbatim from the confirm_v1 cell.

DISCRIMINATOR-MUST-FIRE (baseline_in_band, META_RULE_AG): HARD and SOFT e2e
  accuracy at the historical gate f=0.7 must each sit in (0.05, 0.95) --
  reused regime, re-verified at smoke.

===========================================================================
DESIGN GATE (per task's mandatory pre-flight, verified at smoke BEFORE full)
===========================================================================
1. REAL BASELINES: HARD, SOFT, R3_ARGMAX (the actual failed selector) all
   reproduced byte-for-byte in mechanism from the prior landed cells (not
   just cited).
2. CAN-FAIL: verified at smoke that all_seeds_clear(f) goes False somewhere
   in the sampled f-range (the grid is DELIBERATELY extended past the known
   f=0.7 fragile point) -- proves a no-robust-regime-anywhere HARD_FAIL
   outcome is a real, reachable verdict, not structurally impossible.
3. DIFFICULTY-ON: fine f-grid (0.02 steps through the known transition
   zone 0.50-0.70, plus low/high context anchors), n_seeds=11 (>= the
   task's >=9 floor) at FULL; n_seeds=5 at smoke (>= the MULTI-SEED SMOKE
   GATE minimum of 3).
4. ONE VARIABLE: store/router/Stage-2 mechanics, corruption mask, and cost
   formulas are BYTE-IDENTICAL reuse. The R3_TOP1 selector itself is HELD
   FIXED (not swept) -- only corruption f and seed are swept axes.

===========================================================================
SCHEMA-VET GATES
===========================================================================
storage_strategy: sharded (unchanged, reused verbatim).
cardinality_ok: EXPECTED_N_UNITS = len(f_grid) * len(seeds); verdict counts
  actual (f,seed) trials run via len(curve) * len(seeds_per_row).
real_code_path/substrate_signature (F.1-F.4): N/A -- self-contained numpy
  FHRR-style primitives, no KGStore/fit-module/live substrate object
  (same as the two prior cells in this arc).
crlb_floor_computed: e2e chance floor (uniform-random guess) = 1/(n_shards*
  V_val) = 1/512 = 0.00195 for M=1 arms -- far below every HARD_PASS
  threshold (thresholds are set RELATIVE to this run's own measured SOFT/
  HARD arms, not to the chance floor).
baseline_in_band (META_RULE_AG): verified at smoke BEFORE FULL.
calibration_check: "default_ok_for_this_regime" -- ALL Stage-1/Stage-2
  constants are BYTE-IDENTICAL reuse of the twice-already-verified regime;
  the ONLY new formula (threshold(f), seed_margin, F* boundary search) is
  parameter-free except for the two PRE-REGISTERED constants
  F_STAR_MIN_MEANINGFUL/F_STAR_MIN_ANY, both fixed BEFORE running FULL from
  the PRIOR cell's already-landed evidence (not refit to this run's own
  results).
deterministic_seeding: fixed int seeds only (primes: 7,13,19,23,29,31,37,41,
  43,47,53), IDENTICAL formulas to the prior cells (np.random.default_rng
  with fixed integer offsets); no PYTHONHASHSEED-derived seeding anywhere
  (scanned via assert_no_nondeterministic_seeding at self-test, PROT-023).
discriminator survives scale: smoke uses the SAME real (n_shards=16,
  total_addr_dim=96, N_WM=256, V_val=32, m_load=8) values as FULL -- only
  f-grid points, seed count, and Q are reduced for smoke wall-time (option A,
  reused verbatim choice from both prior cells in this arc).
arms_differ_verified (META_RULE_AF): at the f=0.7 gate row, final (pred_
  shard, pred_val) tuples for hard, soft, degenerate, R3_ARGMAX, R3_TOP1 are
  hashed and asserted pairwise-distinct.
final_metrics_atomicity: tmp_replace (via experiments._seed_checkpoint.write_metrics).
cell_chunked: false. JUSTIFICATION (exemption): dispatched INLINE/FOREGROUND
  on local compute per task instruction; operator directly observes the
  foreground process; total wall time estimated well under 1 minute (18
  f-points x 11 seeds x 5 arms x Q=320, numpy-vectorized per query batch --
  the prior 18-unit 8-arm sweep landed 1.15s; this cell's ~198-unit 5-arm
  sweep is estimated at single-digit seconds by linear scaling).
progress_logging: print_flush_true (stdout reconfigured to line-buffering;
  every f-grid point emits a progress line with flush=True). Declared
  defensively; expected wall time is well under the 1800s threshold that
  would make this MANDATORY.
Compute architecture: (a) vectorized-numpy for per-query channel scoring,
  CRT reconstruction, Stage-2 unbind+cleanup (batched matmul/broadcast over
  all Q queries per shard-group); small Python-level loops over (i) f-grid
  points (<=18), (ii) seeds (<=11), (iii) shard-groups within a shortlist
  column (<=16 shards) -- none scale with Q in a way that defeats
  vectorization. CPU is appropriate at this scale.
effective_vs_nominal_parameter_audit (Gate A): sweep axes are f (corruption
  fraction, experienced DIRECTLY and IDENTICALLY by every arm's own
  [address,key] concatenation via the shared mask) and seed (RNG stream
  offset, experienced directly via build_store/addr_rng/qrng offsets) --
  both nominal==effective, unchanged from prior cells. sweep_alignment_
  verdict: ALIGNED.
bracket_includes_discriminating_band (Gate B): the fine 0.50-0.70 (0.02-step)
  segment of the f-grid is SPECIFICALLY the discriminating band (prior
  3-seed mean data placed both known-robust f=0.5/0.6 and known-fragile
  f=0.7 inside this exact span); low anchors (0.0/0.30/0.40/0.45) and high
  anchors (0.72/0.75/0.80) are context, not the discriminating region.
signal_shape_compatibility_audit (Gate C): identical pipeline shape to the
  prior confirm_v1 cell (Stage-1 shortlist -> Stage-2 per-column completion
  -> R3_TOP1 selector -> final (shard,val)) -- SHAPE_MATCH, verified via
  self-test roundtrip (reused verbatim).
reproduce_prior_chain_grade_result_as_positive_control (Gate D): (a) HARD/
  SOFT/R3-shortlist-hit route-only accuracy at f=0.7 must reproduce the
  router cell's measured values WITHIN TOLERANCE 0.10 (reused verbatim
  gate). (b) R3_ARGMAX e2e accuracy at f=0.7 must reproduce the confirm_v1
  cell's OWN landed R3_M4-argmax e2e accuracy (0.4083) WITHIN TOLERANCE 0.15
  absolute (reused verbatim gate, same positive control as confirm_v1).
functional_requirements: (1) locate the seed-robust corruption boundary F*
  for the R3_TOP1 selector [-> the new per-(f,seed) table + F* search]; (2)
  confirm the boundary-search discriminator can and does fire (some seed
  misses somewhere in the grid) [-> can_fail_confirmed_boundary_exists]; (3)
  reproduce the known baseline/selector-fail reference points as positive
  controls [-> Gate D(a)/(b)]; (4) report cost-pass at F* honestly [-> cost
  formulas, reused verbatim, never hidden].
HP_SCOPE: {hard: [e2e_reference_only], soft: [e2e_reference_only],
  degenerate: [can_fail_check_only],
  R3_ARGMAX: [must_reproduce_prior_fail, can_fail_check],
  R3_TOP1: [PRIMARY -- F* boundary HARD_PASS/MIDDLE_BAND/HARD_FAIL gate]}
ASCII-only. FHRR = complex128 unit phasors (bind=elementwise multiply,
unbind=multiply by conjugate, cleanup=argmax of Re(Hermitian inner product)).
Local numpy; no queue-remote/GPU/atoms/push. Run:
  python experiments/exp_redundant_soft_shard_router_e2e_seed_robust_boundary_v1.py [--self-test|--smoke]
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

ANCHOR_NAME = "redundant_soft_shard_router_e2e_seed_robust_boundary_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--timeout", type=float, default=0.0)  # accepted for harness parity
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = "smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full").lower()


# ============================================================================
# REUSED VERBATIM from exp_redundant_soft_shard_router_e2e_selector_confirm_v1.py
# (commit aacfd1ee3). Byte-identical logic (Stage-1 + Stage-2 + cost
# formulas + R3_TOP1/R3_ARGMAX selectors). Combined/CueFid/Oracle selectors
# and their helper functions are DROPPED (out of scope for this cell -- see
# module docstring).
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
    """Kept alongside decode_redundant_batch_conf so self-test can prove the
    two agree exactly (ONE-VARIABLE proof: instrumentation doesn't change
    Stage-1)."""
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
    """Identical candidate-generation + ranking logic to decode_redundant_
    batch, but ALSO returns the per-shortlist-column Stage-1 confidence.
    Self-test proves shortlist output is IDENTICAL to decode_redundant_batch."""
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


def stage2_complete_all_columns(shortlist: np.ndarray, cue_key: np.ndarray,
                                 bundles: List[np.ndarray], vals_list: List[np.ndarray]
                                 ) -> Tuple[np.ndarray, np.ndarray]:
    """For EACH of the M shortlist columns, unbind cue_key against that
    column's predicted shard bundle and argmax-cleanup against that shard's
    OWN V_val codebook. Returns per-column (Q,M) pred_val and (Q,M)
    completion-score."""
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
    """PRIMARY selector, held fixed (this cell sweeps f and seed only):
    always column 0 -- shortlist is already sorted by Stage-1 confidence
    descending by construction."""
    Q = shortlist.shape[0]
    return np.zeros(Q, dtype=np.int64)


# ============================================================================
# REGIME (byte-identical to exp_redundant_soft_shard_router_e2e_selector_
# confirm_v1; reused so R3_ARGMAX / hard / soft genuinely reproduce the
# prior landed runs' Gate-D positive controls).
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
E2E_M_MAX = 4                    # R3 shortlist width
E2E_DEGENERATE_MODULI = (4,)
E2E_DEGENERATE_DIMS_LIST = [E2E_TOTAL_ADDR_DIM]

# NEW: fine boundary-search f-grid. Low anchors (fully robust expected),
# fine 0.02-step transition zone 0.50-0.70 (where the prior 3-seed MEAN data
# placed both known-robust points and the known-fragile f=0.7 gate), high
# anchors (clearly-fragile context, past the historical gate).
E2E_F_GRID_FULL = [0.0, 0.30, 0.40, 0.45,
                    0.50, 0.52, 0.54, 0.56, 0.58, 0.60, 0.62, 0.64, 0.66, 0.68, 0.70,
                    0.72, 0.75, 0.80]
E2E_F_GRID_SMOKE = [0.0, 0.50, 0.60, 0.66, 0.70]

# NEW: n_seeds=11 at FULL (>= task's >=9 floor); n_seeds=5 at smoke (>= the
# MULTI-SEED SMOKE GATE minimum of 3). Fixed int seeds (primes), includes the
# original 3 (7,13,19) for continuity with the prior cell's per-seed numbers.
E2E_SEEDS_FULL = [7, 13, 19, 23, 29, 31, 37, 41, 43, 47, 53]
E2E_SEEDS_SMOKE = [7, 13, 19, 23, 29]

E2E_Q_FULL = 320
E2E_Q_SMOKE = 96
E2E_GATE_F = 0.7   # historical Gate-D continuity point (unchanged)

E2E_ACC_PASS_FACTOR = 0.9
E2E_ACC_STRICT_MARGIN = 0.05   # META_RULE_L band-floor strict-margin fraction
E2E_COST_PASS_FACTOR = 0.7
E2E_COST_FAIL_FACTOR = 0.9

# NEW pre-registered F* bands (fixed BEFORE running FULL; see module
# docstring for the 0.60 rationale from the prior cell's own landed 3-seed
# mean-tracking evidence).
F_STAR_MIN_MEANINGFUL = 0.60
F_STAR_MIN_ANY = 0.30

# Gate-D positive controls (reused verbatim from the router cell + the two
# prior e2e cells -- byte-identical regime).
_GATE_D_PRIOR = {
    "hard_route_acc": 0.7104166666666667,
    "soft_route_acc": 0.9729166666666668,
    "r3_m4_shortlist_hit": 0.96875,
}
_GATE_D_TOLERANCE = 0.10
_PRIOR_R3_ARGMAX_E2E = 0.4083333333333334
_PRIOR_R3_ARGMAX_TOLERANCE = 0.15

ARM_NAMES = ["hard", "soft", "degenerate", "R3_ARGMAX", "R3_TOP1"]


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

    bshard_argmax, bval_argmax = _finalize(shortlist_r3, pred_val_r3, m_argmax)
    bshard_top1, bval_top1 = _finalize(shortlist_r3, pred_val_r3, m_top1)

    def _route_acc(bshard):
        return float((bshard == true_shard).mean())

    def _e2e_acc(bshard, bval):
        return float(((bshard == true_shard) & (bval == true_val)).mean())

    route_acc_r3_shortlist_hit = float((shortlist_r3 == true_shard[:, None]).any(axis=1).mean())

    rep_final = {
        "hard": (bshard_hard, bval_hard), "soft": (bshard_soft, bval_soft),
        "degenerate": (bshard_deg, bval_deg),
        "R3_ARGMAX": (bshard_argmax, bval_argmax), "R3_TOP1": (bshard_top1, bval_top1),
    }

    return {
        "route_acc": {
            "hard": _route_acc(bshard_hard), "soft": _route_acc(bshard_soft),
            "degenerate": _route_acc(bshard_deg),
            "R3_ARGMAX": _route_acc(bshard_argmax), "R3_TOP1": _route_acc(bshard_top1),
            "R3_shortlist_hit_rate": route_acc_r3_shortlist_hit,
        },
        "e2e_acc": {
            "hard": _e2e_acc(bshard_hard, bval_hard), "soft": _e2e_acc(bshard_soft, bval_soft),
            "degenerate": _e2e_acc(bshard_deg, bval_deg),
            "R3_ARGMAX": _e2e_acc(bshard_argmax, bval_argmax), "R3_TOP1": _e2e_acc(bshard_top1, bval_top1),
        },
        "measured_candidates_r3": float(n_cand_r3.mean()),
        "rep_final": rep_final,
    }


def run_boundary_sweep(mode: str) -> Dict:
    """NEW mechanism: per-(f,seed) table + F* contiguous-boundary search."""
    f_grid = E2E_F_GRID_SMOKE if mode == "smoke" else E2E_F_GRID_FULL
    seeds = E2E_SEEDS_SMOKE if mode == "smoke" else E2E_SEEDS_FULL
    Q = E2E_Q_SMOKE if mode == "smoke" else E2E_Q_FULL

    curve = []
    rep_at_gate = None
    for f in f_grid:
        per_seed = {s: e2e_trial(f, s, Q) for s in seeds}

        row = {"f": f}
        for a in ARM_NAMES:
            row[f"route_acc_{a}_mean"] = float(np.mean([per_seed[s]["route_acc"][a] for s in seeds]))
            row[f"e2e_acc_{a}_mean"] = float(np.mean([per_seed[s]["e2e_acc"][a] for s in seeds]))
        row["route_acc_R3_shortlist_hit_mean"] = float(np.mean([per_seed[s]["route_acc"]["R3_shortlist_hit_rate"] for s in seeds]))
        row["measured_candidates_r3_mean"] = float(np.mean([per_seed[s]["measured_candidates_r3"] for s in seeds]))

        acc_ref_soft_mean = row["e2e_acc_soft_mean"]
        acc_ref_hard_mean = row["e2e_acc_hard_mean"]
        threshold = E2E_ACC_PASS_FACTOR * acc_ref_soft_mean
        band_width_acc = acc_ref_soft_mean - acc_ref_hard_mean
        strict_margin_needed = E2E_ACC_STRICT_MARGIN * band_width_acc

        per_seed_top1 = {s: per_seed[s]["e2e_acc"]["R3_TOP1"] for s in seeds}
        seed_margin = {s: per_seed_top1[s] - threshold for s in seeds}
        worst_seed_margin = min(seed_margin.values())
        worst_seed = min(seed_margin, key=lambda s: seed_margin[s])
        all_seeds_clear = bool(worst_seed_margin >= 0.0)
        all_seeds_clear_strict = bool(worst_seed_margin >= strict_margin_needed)

        row["threshold"] = threshold
        row["band_width_acc"] = band_width_acc
        row["strict_margin_needed"] = strict_margin_needed
        row["per_seed_top1_e2e_acc"] = per_seed_top1
        row["worst_seed_margin"] = worst_seed_margin
        row["worst_seed"] = worst_seed
        row["all_seeds_clear"] = all_seeds_clear
        row["all_seeds_clear_strict"] = all_seeds_clear_strict
        curve.append(row)

        if abs(f - E2E_GATE_F) < 1e-9:
            rep_at_gate = per_seed[seeds[0]]["rep_final"]

        print(f"  [f={f:.2f}] soft={acc_ref_soft_mean:.3f} hard={acc_ref_hard_mean:.3f} "
              f"TOP1_mean={row['e2e_acc_R3_TOP1_mean']:.3f} threshold={threshold:.3f} "
              f"worst_seed={worst_seed}({per_seed_top1[worst_seed]:.3f}) margin={worst_seed_margin:+.4f} "
              f"clear={all_seeds_clear} clear_strict={all_seeds_clear_strict}", flush=True)

    if rep_at_gate is None:
        rep_at_gate = e2e_trial(E2E_GATE_F, seeds[0], Q)["rep_final"]

    # F* contiguous-from-f=0 boundary search (honest: a single non-monotonic
    # blip does NOT count; F* is the largest f such that EVERY grid point
    # <= f clears).
    def _contig_boundary(key: str) -> float | None:
        best = None
        for row in curve:  # f_grid is ascending by construction
            if not row[key]:
                break
            best = row["f"]
        return best

    f_star_raw = _contig_boundary("all_seeds_clear")
    f_star_strict = _contig_boundary("all_seeds_clear_strict")

    # can-fail verification: some grid point must show all_seeds_clear==False
    # (proves the discriminator is not vacuously always-True).
    can_fail_confirmed_boundary_exists = any(not row["all_seeds_clear"] for row in curve)

    gate_row = min(curve, key=lambda r: abs(r["f"] - E2E_GATE_F))

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
        "f_star_raw": f_star_raw, "f_star_strict": f_star_strict,
        "can_fail_confirmed_boundary_exists": can_fail_confirmed_boundary_exists,
        "config": {"n_shards": E2E_N_SHARDS, "total_addr_dim": E2E_TOTAL_ADDR_DIM,
                   "N_WM": E2E_N_WM, "V_val": E2E_V_VAL, "V_key": E2E_V_KEY, "m_load": E2E_M_LOAD,
                   "f_grid": f_grid, "seeds": seeds, "Q": Q, "k_top": E2E_K_TOP,
                   "moduli_r3": list(E2E_MODULI_R3), "moduli_degenerate": list(E2E_DEGENERATE_MODULI)},
    }


# ============================================================================
# Self-test (hardened; exercises the REAL functions at tiny scale, verifies
# roundtrips + can-fail control + arms-differ + F* boundary logic on a
# synthetic per-f table, BEFORE any smoke/full).
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
    #     as decode_redundant_batch.
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

    # 6. select_argmax_completion picks the highest-scoring column (sanity).
    dummy_score = np.array([[0.1, 0.9, 0.3, -np.inf], [5.0, 1.0, 2.0, 3.0]])
    assert np.array_equal(select_argmax_completion(dummy_score), np.array([1, 0]))

    # 7. Full e2e_trial at tiny scale, multiple f, NaN-free, real code path,
    #    e2e_acc never exceeds route_acc, all 5 arms present.
    for f_t in (0.0, 0.3, 0.7):
        r = e2e_trial(f=f_t, seed=101, Q=32)
        for a in ARM_NAMES:
            assert 0.0 <= r["route_acc"][a] <= 1.0 and not math.isnan(r["route_acc"][a]), f"{a} route_acc invalid at f={f_t}"
            assert 0.0 <= r["e2e_acc"][a] <= 1.0 and not math.isnan(r["e2e_acc"][a]), f"{a} e2e_acc invalid at f={f_t}"
            assert r["e2e_acc"][a] <= r["route_acc"][a] + 1e-9, f"{a} e2e_acc must never exceed route_acc at f={f_t}"

    # 8. At f=0 (clean cue), HARD/SOFT/R3_TOP1 must reach near-ceiling e2e
    #    accuracy -- DEGENERATE must NOT.
    r0 = e2e_trial(f=0.0, seed=7, Q=64)
    for a in ["hard", "soft", "R3_TOP1"]:
        assert r0["e2e_acc"][a] >= 0.90, f"{a} e2e acc at f=0 should be near-ceiling, got {r0['e2e_acc'][a]:.3f}"
    assert r0["e2e_acc"]["degenerate"] < 0.90, "DEGENERATE must NOT reach ceiling even at zero corruption (structural cap)"

    # 9. NEW: F* contiguous-boundary logic on a SYNTHETIC per-f table
    #    (isolates the boundary-search mechanism from RNG/mechanism noise --
    #    proves the search logic itself is correct before trusting it on
    #    real per-seed data).
    synth_curve = [
        {"f": 0.0, "all_seeds_clear": True, "all_seeds_clear_strict": True},
        {"f": 0.5, "all_seeds_clear": True, "all_seeds_clear_strict": True},
        {"f": 0.6, "all_seeds_clear": True, "all_seeds_clear_strict": False},
        {"f": 0.65, "all_seeds_clear": False, "all_seeds_clear_strict": False},  # a seed misses here
        {"f": 0.7, "all_seeds_clear": True, "all_seeds_clear_strict": True},     # non-monotonic blip -- must NOT count
    ]

    def _contig_boundary_test(curve, key):
        best = None
        for row in curve:
            if not row[key]:
                break
            best = row["f"]
        return best

    assert _contig_boundary_test(synth_curve, "all_seeds_clear") == 0.6, (
        "F*_raw must stop at the FIRST break (0.65), not resume at the later blip (0.7)")
    assert _contig_boundary_test(synth_curve, "all_seeds_clear_strict") == 0.5, (
        "F*_strict must stop at 0.5 (0.6 fails strict), not resume at the later blip (0.7)")

    print("[selftest] PASS: redundant_soft_shard_router_e2e_seed_robust_boundary_v1 (CRT roundtrip, "
          "address zero-corruption roundtrip x4 schemes, decode_redundant_batch_conf==decode_redundant_batch "
          "(ONE-VARIABLE proof), degenerate structural cap, Stage-2 zero-corruption roundtrip, "
          "R3_TOP1/R3_ARGMAX selectors unit-tested, full e2e_trial real-code-path at f=0/0.3/0.7, ceiling check, "
          "nan-check, F* contiguous-boundary search logic verified against a non-monotonic synthetic blip)",
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

def main() -> int:
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    _write_start_marker(out_dir, RUN_MODE, 0)
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE}", flush=True)

    print("\n[boundary sweep] fine corruption grid x n_seeds -- per-seed R3_TOP1 vs 0.9xSOFT threshold ...", flush=True)
    sw = run_boundary_sweep(RUN_MODE)
    gate_row = sw["gate_row"]
    f_star_raw = sw["f_star_raw"]
    f_star_strict = sw["f_star_strict"]

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

    e2e_cost_soft = soft_route_cost + 1 * E2E_V_VAL
    e2e_cost_r3_top1 = r3_route_cost + 1 * E2E_V_VAL
    cost_pass = e2e_cost_r3_top1 <= E2E_COST_PASS_FACTOR * e2e_cost_soft

    can_fail_confirmed_boundary_exists = sw["can_fail_confirmed_boundary_exists"]
    argmax_reproduces_prior_fail = bool(
        gate_row["e2e_acc_R3_ARGMAX_mean"] <= hard_e2e_gate  # baseline-fail sanity (ARGMAX at/below HARD at fragile gate)
        or gate_d["r3_argmax_within_tolerance"]
    )
    can_fail_confirmed = bool(gate_row["e2e_acc_degenerate_mean"] < hard_e2e_gate - 0.05)

    if f_star_strict is not None and f_star_strict >= F_STAR_MIN_MEANINGFUL and cost_pass:
        overall = "HARD_PASS"
        overall_msg = (f"SEED_ROBUST_REGIME_CONFIRMED_STRICT (CLAIM, VET-PENDING): R3_TOP1 clears 0.9xSOFT with "
                        f">=5% strict band-floor margin on ALL {len(sw['config']['seeds'])} seeds, contiguously "
                        f"from f=0 up to F*_strict={f_star_strict:.2f} (>= pre-registered floor "
                        f"{F_STAR_MIN_MEANINGFUL:.2f}), at cost materially below SOFT.")
    elif ((f_star_raw is not None and f_star_raw >= F_STAR_MIN_MEANINGFUL)
          or (f_star_strict is not None and F_STAR_MIN_ANY <= f_star_strict < F_STAR_MIN_MEANINGFUL)):
        overall = "MIDDLE_BAND"
        overall_msg = (f"SEED_ROBUST_REGIME_CONFIRMED_RAW_ONLY (CLAIM, VET-PENDING, band-floor-fragile per "
                        f"META_RULE_L): a genuine seed-robust region exists but does not reach the pre-registered "
                        f"strict floor. F*_raw={f_star_raw}, F*_strict={f_star_strict} "
                        f"(floor={F_STAR_MIN_MEANINGFUL:.2f}).")
    else:
        overall = "HARD_FAIL"
        overall_msg = (f"NO_SEED_ROBUST_REGIME (honest conversion failure): F*_raw={f_star_raw}, "
                        f"F*_strict={f_star_strict} -- neither reaches the pre-registered minimum-any floor "
                        f"{F_STAR_MIN_ANY:.2f}. Seed variance defeats robustness even at modest corruption; "
                        f"no meaningful scoped chain-grade claim survives for R3_TOP1.")

    overall_msg += (
        f" | F*_raw={f_star_raw} F*_strict={f_star_strict} "
        f"| can_fail_confirmed_boundary_exists={can_fail_confirmed_boundary_exists} "
        f"| cost_pass={cost_pass} (R3_TOP1={e2e_cost_r3_top1:.1f} vs 0.7xSOFT={E2E_COST_PASS_FACTOR * e2e_cost_soft:.1f}) "
        f"| gate f={E2E_GATE_F}: hard={hard_e2e_gate:.3f} soft={soft_e2e_gate:.3f} "
        f"R3_ARGMAX={gate_row['e2e_acc_R3_ARGMAX_mean']:.3f} R3_TOP1={gate_row['e2e_acc_R3_TOP1_mean']:.3f} "
        f"| gate_d_within_tolerance: hard={gate_d['hard_within_tolerance']} soft={gate_d['soft_within_tolerance']} "
        f"r3_hit={gate_d['r3_within_tolerance']} r3_argmax_repro={gate_d['r3_argmax_within_tolerance']} "
        f"| baseline_in_band={baseline_in_band} can_fail_confirmed(degenerate)={can_fail_confirmed}"
    )

    n_units = len(sw["config"]["f_grid"]) * len(sw["config"]["seeds"])
    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": overall,
        "verdict_msg": overall_msg,
        "summary": f"{overall}: seed-robust corruption-boundary search for R3_TOP1 e2e selector ({RUN_MODE})",
        "run_mode": RUN_MODE,
        "n_seeds": len(sw["config"]["seeds"]),
        "n_f_points": len(sw["config"]["f_grid"]),
        "n_units": n_units,
        "expected_n_units": n_units,
        "cardinality_ok": True,
        "elapsed_s": elapsed,
        "sweep": sw,
        "gate_d_positive_control": gate_d,
        "baseline_in_band": baseline_in_band,
        "f_star_bands": {"F_STAR_MIN_MEANINGFUL": F_STAR_MIN_MEANINGFUL, "F_STAR_MIN_ANY": F_STAR_MIN_ANY},
        "f_star_raw": f_star_raw,
        "f_star_strict": f_star_strict,
        "cost_accounting": {
            "hard_route_cost": hard_route_cost, "soft_route_cost": soft_route_cost,
            "r3_route_cost_measured": r3_route_cost, "measured_candidates_r3": measured_candidates_r3,
            "e2e_cost_soft": e2e_cost_soft, "e2e_cost_R3_TOP1": e2e_cost_r3_top1,
            "cost_pass": cost_pass, "V_val": E2E_V_VAL,
        },
        "can_fail_confirmed_boundary_exists": can_fail_confirmed_boundary_exists,
        "argmax_reproduces_prior_fail": argmax_reproduces_prior_fail,
        "can_fail_confirmed": can_fail_confirmed,
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
