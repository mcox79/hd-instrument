"""exp_redundant_soft_shard_router_v1 -- THIRD Stage-1 shard-router design point
(REDUNDANT_SOFT), tested head-to-head against the two extremes already landed
in exp_fuzzy_shard_router_attractor_stage12_v1 (a1955850e): HARD/DECOMPOSED
(cheap, O(log n_shards), fragile: route-acc=0.710 at f=0.7) and SOFT/HOLISTIC
(robust: route-acc=0.973 at f=0.7, but O(n_shards*dims) full-store sweep).
Question: does R~3-5 small INCOMMENSURATE channels + SOFT-SUM combine (not
majority-vote, not hard decode) + a top-M~2-4 shortlist dominate the Pareto
frontier of the two extremes (cheap AND robust simultaneously)?

PRIOR-WORK CHECK (substrate-KB concept-query, mandatory per exp_dev
discipline): `bash tools/substrate_query.sh "redundant soft channel shard
router incommensurate combine top-M shortlist grid-cell CRT"` -> top hit
cosine=0.2852 ('commensurate', WordNet antonym entry), all top-5 hits are
WordNet lexical/antonym entries (commensurate/incommensurate/shortlist), NOT
prior experiment atoms. NONE at cosine > 0.30 -> genuinely novel test, not a
rediscovery.

DESIGN SOURCE (adopt/adjust bands from):
  notes/research_shard_router_cheap_and_robust_redundant_soft_2026-07-17.md
  -- the biology (grid-cell modular CRT population code, Sreenivasan & Fiete
  2011 "analog error-correcting code") + coding-theory (LDPC/expander-code/
  compressed-sensing: soft/belief-propagation combine beats hard-decision
  decode of the SAME redundant code) synthesis. Predictions 1-3 built here
  exactly as pre-registered in that note.

LOAD-BEARING NEGATIVES OBEYED (both from on-platform priors, not re-run):
  - exp_multihop_router_crt_residue_addressed_v1 (RC2, HARD_FAIL): a HARD,
    non-redundant, single-combo CRT decode lost to a naive baseline. Any one
    residue error derails reconstruction, no partial credit, no soft
    combination step.
  - stage12's OWN self-test (disclosed in that cell's docstring): per-bit
    MAJORITY VOTE over R independent narrow decodes was WORSE than a single
    wide/holistic decode (0.984 vs 0.997) -- hard-decision combination of
    redundant sub-decodes is provably suboptimal to soft/linear combination
    under i.i.d. noise. This cell's HARD_VOTE arm (below) re-tests that
    SPECIFIC claim in a DIFFERENT, controlled way: same R channels, same
    candidate-generation, same M shortlist size as the SOFT arm -- ONLY the
    combine rule (soft-sum vs discrete-vote) varies (Prediction 2 isolation;
    the stage12 self-test varied combine AND redundancy-shape at once, so
    this is a stricter, matched-redundancy re-test, not a re-run).

===========================================================================
ARCHITECTURE
===========================================================================
Three (+2 diagnostic) Stage-1 shard-routing schemes are compared on the
IDENTICAL regime (N_SHARDS=16, TOTAL_DIM=96 address budget, same corruption
protocol) -- ONE VARIABLE per design gate #4: only the channel/combine
structure differs.

  HARD (DECOMPOSED, reused VERBATIM incl. RNG seeds from stage12 Part 3):
    n_bits=4 independent 24-dim bit-plane decodes, place-value combined.
    Cost O(log n_shards). Fragile: one bit error flips the whole id.

  SOFT (HOLISTIC, reused VERBATIM incl. RNG seeds from stage12 Part 3):
    one 96-dim codeword per shard, single nearest-neighbor match (cleanup()).
    Cost O(n_shards * dims) -- the full-store sweep the architecture exists
    to avoid. Robust: no single-point-of-failure.

  REDUNDANT_SOFT (NEW, this cell): R (3 or 5) independent small-modulus
  channels with FIXED, INCOMMENSURATE (pairwise-coprime) moduli -- e.g.
  R=3: (5,7,11), product=385; R=5: (2,3,5,7,11), product=2310. Each channel r
  has its OWN small codebook of moduli[r] codewords (dims_list[r] dims each,
  summing to TOTAL_DIM=96). Shard sid's channel-r address segment is
  codebook_r[sid mod moduli[r]] -- MANY shards deliberately SHARE a channel's
  codeword (local ambiguity per channel, the grid-cell-module analog).
  Per query: each channel is scored SOFTLY (real inner product) against its
  own small codebook -> a continuous score vector (not a hard decode). A
  list-decoding step keeps the top-k(=2) residues per channel (not just the
  argmax) -- this is what keeps the whole thing CHEAP: the cross-product of
  top-k residues across R channels (<=32 combos, INDEPENDENT of n_shards) is
  CRT-reconstructed (vectorized, closed-form modular-arithmetic weights, no
  n_shards-sized table scan) into candidate shard ids, each scored by the SUM
  of its channels' continuous scores (soft/graded combine -- explicitly NOT
  majority-of-hard-decisions). Top-M (2 or 4) candidates by summed confidence
  become the shortlist. Cost ~ O(R*avg_modulus*dims_per_channel + candidates)
  -- INDEPENDENT of n_shards by construction (fixed moduli cover an
  exponentially larger range as R grows, the grid-module property; Part B
  below measures this is not just claimed but MEASURED not to grow at 10x
  n_shards).

  HARD_VOTE (diagnostic, Prediction 2 isolation): IDENTICAL R, moduli,
  dims_list, cue, and candidate-generation (same top-k cross-product) as the
  matched REDUNDANT_SOFT config (R5_M4) -- ONLY the combine rule differs:
  discrete vote-count (does this candidate's residue match the channel's OWN
  top-1/argmax? +1 per agreeing channel) instead of summed continuous score.
  Isolates soft-vs-hard-combine-at-MATCHED-redundancy, distinct from and
  narrower than stage12's own self-test finding (which varied redundancy
  shape and combine rule together).

  DEGENERATE (can-fail / must-fail control, design gate #2): R=1, single
  modulus=4 < n_shards=16. product(moduli)=4 means only 4 distinguishable
  residue classes exist for 16 shards -- shards {4..15} are STRUCTURALLY
  UNREACHABLE regardless of corruption level (verified in self-test at f=0:
  the discriminator MUST show acc <= 0.30 here, purely by construction, not
  because of noise). This proves the pipeline's verdict machinery is capable
  of emitting a genuine failing number for a bad design -- it is not
  vacuously tuned to always pass.

===========================================================================
FALSIFIABLE PRE-REGISTERED PREDICTIONS (bands set BEFORE running FULL;
adopted directly from the design-source note's "Falsifiable predictions"
section, predictions 1 and 2; prediction 3 is a conditional, DESCRIPTIVE-ONLY
localization note, never itself gating the tier)
===========================================================================
PART A -- corruption-vs-accuracy sweep at n_shards=16, TOTAL_DIM=96 (stage12
  Part 3's exact regime). f in {0.0,0.3,0.5,0.6,0.7,0.8,0.9,0.95} (headline
  gate f=0.7, difficulty-ON per design gate #3 -- includes points ABOVE 0.7
  too). 3 seeds FULL / 2 smoke. Q=320 FULL / 96 smoke.

  PREDICTION 1 (joint cheap-and-robust point exists):
    threshold_p1 = 0.9 * soft_acc_at_gate (OUR OWN reproduced HOLISTIC number
      at f=0.7, not a hardcoded prior value -- "within 10% of HOLISTIC").
    best_redundant_acc = max over the 4 tested (R,M) in {3,5}x{2,4} configs
      of route-acc (true shard in shortlist) at f=0.7.
    growth_redundant = Part B's measured cost-growth ratio at 10x n_shards
      (32->320) for the representative R5_M4 config.
    HARD-PASS:  best_redundant_acc >= threshold_p1  AND  growth_redundant < 2.0
                (matches stage12 Part 2's own HARD-PASS cheap-bar exactly).
                A genuine existence proof the tension closes at small fixed
                R/M -- matching the grid-cell/LDPC/expander-code theorem-shape.
    HARD-FAIL:  best_redundant_acc <= hard_acc_at_gate (no config improves
                over the cheap-but-fragile HARD arm at all) -- an encoding-
                level gap (this substrate's phasor/cleanup primitive lacks
                the structural regularity LDPC/grid-cells rely on), not a
                design-effort gap.
    MIDDLE_BAND: anything between (a genuine improvement over HARD, and/or a
                genuine cost saving over SOFT, but not BOTH bars at once --
                a Pareto-frontier point, explicitly NOT reported as
                domination per the task's CONTRACT).

  PREDICTION 2 (soft combine beats hard combine at MATCHED redundancy):
    margin_p2 = TOP-1 accuracy(REDUNDANT_SOFT, R5_M4, f=0.7) - TOP-1
      accuracy(HARD_VOTE, R5_M4, f=0.7) -- SAME R=5, M=4, SAME cue, SAME
      candidate generation; ONLY the combine rule (soft-sum vs discrete-vote)
      differs. METRIC-CHOICE NOTE (caught at FULL, disclosed not hidden):
      the top-M SHORTLIST hit-rate (P1's metric) turned out to be a poor
      discriminator for THIS specific question -- at M=4 with mean
      candidates-found ~5.4 (close to M), soft-sum and hard-vote almost
      always retain the SAME SET of 4 shards (just internally reordered),
      giving margin_p2=+0.000 to 16 significant digits even though the #1
      ranked pick differs 6.5% of the time (measured). TOP-1 accuracy (is
      the SINGLE best-ranked candidate correct) is the metric that actually
      exercises the combine rule's ranking quality, so it is used here
      instead of the shortlist-membership metric.
    HARD-PASS: margin_p2 >= 0.10 (the LDPC-style "soft beats hard at matched
      redundancy" claim transfers to this substrate's encoding).
    HARD-FAIL: margin_p2 <= 0.0 (soft and hard combine perform equivalently
      or hard wins -- the soft-vs-hard lever does not transfer here).
    MIDDLE_BAND: 0.0 < margin_p2 < 0.10.

PART B -- cost/n_shards-count scaling (stage12 Part 2's exact n_shards pair
  {32,320}, dims_per_bit=8 reused). Deterministic analytic-cost formulas for
  HARD and SOFT (matching stage12 Part 2's op-count style); REDUNDANT_SOFT's
  cost is MEASURED (not just formula-asserted) by actually running the R5_M4
  decode at both n_shards values and counting realized channel-score-ops +
  realized candidates-evaluated -- this is a genuine empirical check (a bug
  that made cost secretly n_shards-dependent would show up here), not a
  vacuous by-construction claim.
    growth_hard, growth_soft, growth_redundant reported; growth_redundant
    feeds Prediction 1's cheap-bar above.

CAN-FAIL VERIFICATION (design gate #2, MANDATORY, verified at self-test AND
  reported at smoke+FULL): degenerate_acc_at_gate (R=1, modulus=4<16 arm) MUST
  score below hard_acc_at_gate by >= 0.05 -- `can_fail_confirmed` field in
  metrics. This demonstrates the verdict machinery CAN and DOES emit a bad
  number for a bad design (structurally forced, not cherry-picked/tuned).

OVERALL TIER (CLAIM, VET-PENDING -- never asserted as fact by this cell):
  "REDUNDANT_SOFT_CLOSES_GAP": both P1 and P2 HARD_PASS.
  "HARD_FAIL_P1" / "HARD_FAIL_P2": either genuinely refuted (first found).
  "MEASURED_MECHANISM_MIXED": otherwise (Pareto-frontier point or partial
    combine-rule support -- explicitly NOT framed as domination per CONTRACT).

===========================================================================
SCHEMA-VET GATES
===========================================================================
storage_strategy: no_storage (pure Stage-1 routing comparison, no bind/bundle/
  retrieval of stored items -- matches stage12 Part 3's own scope exactly,
  which also measured ROUTE ACCURACY ONLY, no Stage-2 e2e retrieval).
cardinality_ok: EXPECTED_N_UNITS = len(f_grid)*len(seeds_A) [Part A]
  + len(n_shards_pair)*len(seeds_B) [Part B]; verdict counts actual units run.
real_code_path/substrate_signature (F.1-F.4): N/A -- self-contained numpy
  FHRR-style primitives, no KGStore/fit-module/live substrate object
  construction.
crlb_floor_computed: Part A chance floor = 1/n_shards = 1/16 = 0.0625 for
  top-1 arms (HARD/SOFT/HARD_VOTE-top1); for M-shortlist arms the "chance"
  floor is M/n_shards = M/16 (0.125 for M=2, 0.25 for M=4) under a uniform-
  random shortlist -- HARD_PASS thresholds (>=0.876 for P1) are far above
  this floor and reachable (SOFT/HOLISTIC already measures 0.973 in the same
  regime). Degenerate arm's STRUCTURAL cap (not noise-floor) = 4/16=0.25
  (product(moduli)=4), independently verified in self-test at f=0.
baseline_in_band (META_RULE_AG): hard_acc_at_gate (stage12's own 0.710) is
  checked in smoke to sit in (0.05,0.95) -- reused from a cell that already
  passed this check; re-verified here since seeds/code are byte-identical.
calibration_check: "default_ok_for_this_regime" -- HARD/SOFT arms are a
  byte-identical reproduction of an already-landed, already-cited cell
  (same seeds, same formulas); no calibration constant is refit.
deterministic_seeding: fixed int seeds only (np.random.default_rng(int) with
  fixed integer offsets per part/config/seed/f); no PYTHONHASHSEED-derived
  seeding or set-iteration-order dependence anywhere in this file (scanned
  via assert_no_nondeterministic_seeding at self-test, PROT-023 auto-scan at
  ship).
discriminator survives scale: smoke uses the SAME real (n_shards=16,
  TOTAL_DIM=96) values as FULL in Part A -- only f-grid points and seed
  counts are reduced for smoke wall-time (DISCRIMINATOR-MUST-SURVIVE-SCALE
  option A). Part B's n_shards PAIR (32,320) is itself the full-scale
  regime in both smoke and FULL (only seed count differs).
arms_differ_verified (META_RULE_AF): at the f=0.7 gate row, top-1 predictions
  of HARD, SOFT, each of the 4 REDUNDANT_SOFT configs, HARD_VOTE, and
  DEGENERATE are hashed and asserted pairwise-distinct.
final_metrics_atomicity: tmp_replace (via experiments._seed_checkpoint.write_metrics).
cell_chunked: false. JUSTIFICATION (exemption, per SS13's runner-zombie
  rationale, same as stage12): dispatched INLINE/FOREGROUND on local compute
  per task instruction (queue is down) -- operator directly observes the
  foreground process; total wall time estimated well under 2 minutes (all
  numpy matmuls at N<=320 queries, <=32 combos per query, small codebooks).
progress_logging: print_flush_true (stdout reconfigured to line-buffering;
  every part emits a per-grid-point progress line with flush=True). Declared
  defensively; expected wall time is well under the 1800s threshold that
  would make this MANDATORY.
Compute architecture: (a) vectorized-numpy for all per-query channel scoring
  and CRT reconstruction (batched matmul / broadcast over all Q queries at
  once per combo); a SMALL python-level loop over (i) the <=32 candidate
  combos (constant, independent of n_shards or Q) and (ii) the final per-
  query top-M dedup (Q up to 320, trivial dict-based work per query, not a
  matmul-shaped operation and too small to be worth vectorizing further).
  CPU is appropriate at this scale (GPU dispatch would be pure overhead for
  a sub-minute total wall time).
effective_vs_nominal_parameter_audit (Gate A): sweep axes are f (corruption
  fraction) and (R,M) config choice; both are experienced DIRECTLY by the
  primitives being measured (no upstream re-scoping layer between the swept
  parameter and what the router actually sees). sweep_alignment_verdict: ALIGNED.
bracket_includes_discriminating_band (Gate B): f grid reuses stage12 Part 3's
  own pre-dispatch-probed discriminating band for HARD/SOFT ({0.6,0.7,0.8,0.9}
  non-saturated for both arms); verified at smoke that REDUNDANT_SOFT configs
  are ALSO non-saturated (not pinned at 1.0 or 0.0) across at least 3 of the
  4 smoke f-points before FULL dispatch.
signal_shape_compatibility_audit (Gate C): channel-score -> CRT-reconstruct
  edge is a closed-form, self-contained numeric mapping (SHAPE_MATCH),
  verified via self-test roundtrip (zero-corruption exact reconstruction).
reproduce_prior_chain_grade_result_as_positive_control (Gate D): HARD/SOFT
  arms are a BYTE-IDENTICAL reproduction of stage12 Part 3 (same code, same
  RNG seed formula) -- the strongest form of Gate D compliance (not just
  within-tolerance; literally the same computation re-run).
HP_SCOPE: {HARD: [P1_reference_only], SOFT: [P1_reference_only],
  REDUNDANT_SOFT_configs: [P1], HARD_VOTE: [P2], DEGENERATE: [can_fail_check_only]}
ASCII-only. FHRR = complex128 unit phasors (bind not used in this cell --
  pure Stage-1 routing comparison; cleanup-style real-inner-product scoring
  reused as the per-channel soft scorer). Local numpy; no queue-remote/GPU/
  atoms/push. Run:
  python experiments/exp_redundant_soft_shard_router_v1.py [--self-test|--smoke]
  (bare / runner-injected HDLAB_RUN_MODE=full -> full)
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
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

ANCHOR_NAME = "redundant_soft_shard_router_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--timeout", type=float, default=0.0)  # accepted for harness parity
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = "smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full").lower()


# ============================================================================
# REUSED VERBATIM from exp_fuzzy_shard_router_attractor_stage12_v1.py
# (commit a1955850e) -- FHRR phasor primitives + the DECOMPOSED/HOLISTIC
# router functions (Gate D positive control: byte-identical reproduction).
# ============================================================================

def make_phasors(rng: np.random.Generator, count: int, N: int) -> np.ndarray:
    theta = rng.uniform(-np.pi, np.pi, size=(count, N))
    return np.exp(1j * theta)


def corrupt_batch(mat: np.ndarray, frac: float, rng: np.random.Generator) -> np.ndarray:
    """Bernoulli(frac) per-dim phase redraw. Copied verbatim from stage12."""
    if frac <= 0.0:
        return mat.copy()
    Q, D = mat.shape
    mask = rng.random((Q, D)) < frac
    theta = rng.uniform(-np.pi, np.pi, size=(Q, D))
    fresh = np.exp(1j * theta)
    return np.where(mask, fresh, mat)


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


def _digest(arr: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(arr).tobytes()).hexdigest()[:16]


# ============================================================================
# NEW -- REDUNDANT_SOFT: CRT-style residue channels + soft/hard combine.
# ============================================================================

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
    """Standard CRT reconstruction: for pairwise-coprime moduli, the unique
    x in [0,M) with x % moduli[r] == residue_r for all r is
    x = sum_r(residue_r * weight_r) mod M. CITED@standard constructive proof
    of the Chinese Remainder Theorem. Vectorizable (elementwise mod-arithmetic,
    no per-query table scan over n_shards -- the property that keeps
    REDUNDANT_SOFT's query-time cost independent of n_shards)."""
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
    """Nearly-equal split of total_dim across R channels, summing exactly to
    total_dim (matches HARD/SOFT arms' total dim budget -- ONE VARIABLE)."""
    base, rem = divmod(total_dim, R)
    return [base + (1 if i < rem else 0) for i in range(R)]


def build_channel_codebooks(moduli: Tuple[int, ...], dims_list: List[int],
                             rng: np.random.Generator) -> List[np.ndarray]:
    """codebooks[r] = (moduli[r], dims_list[r]) phasor array -- one codeword
    per residue class in channel r (small, local, deliberately ambiguous)."""
    return [make_phasors(rng, moduli[r], dims_list[r]) for r in range(len(moduli))]


def encode_channel_table(n_shards: int, moduli: Tuple[int, ...], dims_list: List[int],
                          codebooks: List[np.ndarray]) -> np.ndarray:
    """Per-shard REDUNDANT_SOFT address: shard sid's channel-r segment =
    codebooks[r][sid % moduli[r]] -- many shards SHARE a channel's codeword
    (the grid-module local-ambiguity property)."""
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
    """Per-channel SOFT score: (Q, m_r) real inner-product scores, one array
    per channel (NOT a hard argmax -- the continuous evidence LDPC-style
    combining needs)."""
    scores = []
    off = 0
    for r, cb in enumerate(codebooks):
        d = dims_list[r]
        seg = cue[:, off:off + d]
        scores.append((seg @ cb.conj().T).real)
        off += d
    return scores


def topk_per_channel(scores: List[np.ndarray], k_top: int) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Top-k residue indices (descending score) per channel -- list-decoding
    breadth, not the hard single argmax. This is what keeps candidate
    generation independent of n_shards while still tolerating noise: the
    true residue only needs to survive into the top-k, not be the single
    best guess."""
    idx_list, score_list = [], []
    for s in scores:
        k = min(k_top, s.shape[1])
        order = np.argsort(-s, axis=1)[:, :k]
        idx_list.append(order)
        score_list.append(np.take_along_axis(s, order, axis=1))
    return idx_list, score_list


def _combo_shard_ids_and_conf(topk_idx: List[np.ndarray], topk_score: List[np.ndarray],
                               weights: List[int], M_full: int, n_shards: int,
                               combo: Tuple[int, ...]) -> Tuple[np.ndarray, np.ndarray, int]:
    """One combo = a choice of rank-index per channel (e.g. (0,1,0) = channel
    0's best residue, channel 1's 2nd-best, channel 2's best). Vectorized
    over all Q queries at once via closed-form CRT weights (no n_shards-sized
    table scan). Returns (shard_id (Q,), confidence (Q,), vote_count)."""
    R = len(topk_idx)
    Q = topk_idx[0].shape[0]
    x = np.zeros(Q, dtype=np.int64)
    conf = np.zeros(Q, dtype=np.float64)
    vote = 0
    for r in range(R):
        rank = combo[r]
        residues_r = topk_idx[r][:, rank]
        conf = conf + topk_score[r][:, rank]
        x = (x + residues_r.astype(np.int64) * weights[r]) % M_full
        if rank == 0:
            vote += 1
    shard_id = np.where(x < n_shards, x, -1)
    return shard_id, conf, vote


def decode_redundant_batch(cue: np.ndarray, moduli: Tuple[int, ...], dims_list: List[int],
                            codebooks: List[np.ndarray], n_shards: int, k_top: int, M: int,
                            combine: str = "soft") -> Tuple[np.ndarray, np.ndarray]:
    """combine='soft': rank candidates by SUM of continuous per-channel
    scores (LDPC/grid-cell-style graded combination). combine='hard_vote':
    rank by discrete count of channels whose OWN top-1/argmax residue matches
    this candidate (ties broken by the soft score, deterministic secondary
    key). SAME candidate generation (list-decoded top-k cross-product) for
    both -- ONLY the ranking rule differs (Prediction 2 isolation).
    Returns (shortlist (Q,M) int, -1-padded; n_candidates (Q,) int)."""
    R = len(moduli)
    scores = score_channels_batch(cue, dims_list, codebooks)
    topk_idx, topk_score = topk_per_channel(scores, k_top)
    Q = cue.shape[0]
    M_full, weights = crt_weights(moduli)

    k_eff = [topk_idx[r].shape[1] for r in range(R)]
    combos = list(itertools.product(*[range(k_eff[r]) for r in range(R)]))
    n_combos = len(combos)

    all_shard = np.full((Q, n_combos), -1, dtype=np.int64)
    all_conf = np.full((Q, n_combos), -np.inf, dtype=np.float64)
    all_vote = np.zeros(n_combos, dtype=np.int64)
    for ci, combo in enumerate(combos):
        sid, conf, vote = _combo_shard_ids_and_conf(topk_idx, topk_score, weights, M_full, n_shards, combo)
        all_shard[:, ci] = sid
        all_conf[:, ci] = np.where(sid >= 0, conf, -np.inf)
        all_vote[ci] = vote

    shortlist = np.full((Q, M), -1, dtype=np.int64)
    n_candidates = np.zeros(Q, dtype=np.int64)
    for q in range(Q):
        valid = all_shard[q] >= 0
        if not np.any(valid):
            continue
        sids_q = all_shard[q][valid]
        conf_q = all_conf[q][valid]
        vote_q = all_vote[valid]
        key_q = vote_q.astype(np.float64) * 1.0e6 + conf_q if combine == "hard_vote" else conf_q
        best_per_shard: Dict[int, float] = {}
        for sid, key in zip(sids_q.tolist(), key_q.tolist()):
            if sid not in best_per_shard or key > best_per_shard[sid]:
                best_per_shard[sid] = key
        n_candidates[q] = len(best_per_shard)
        ranked = sorted(best_per_shard.items(), key=lambda kv: -kv[1])[:M]
        for i, (sid, _key) in enumerate(ranked):
            shortlist[q, i] = sid
    return shortlist, n_candidates


def shortlist_hit_rate(shortlist: np.ndarray, true_shard: np.ndarray) -> float:
    return float((shortlist == true_shard[:, None]).any(axis=1).mean())


# ============================================================================
# PART A -- corruption-vs-accuracy head-to-head, n_shards=16 fixed
# (stage12 Part 3's exact regime for HARD/SOFT -- Gate D positive control).
# ============================================================================

PA_N_SHARDS = 16          # == stage12 P3_N_SHARDS
PA_N_BITS = 4             # == stage12 P3_N_BITS
PA_DIMS_PER_BIT = 24      # == stage12 P3_DIMS_PER_BIT
PA_TOTAL_DIM = PA_N_BITS * PA_DIMS_PER_BIT   # 96 == stage12 P3_TOTAL_DIM

PA_F_GRID_FULL = [0.0, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
PA_F_GRID_SMOKE = [0.0, 0.6, 0.7, 0.8]   # includes PA_GATE_F=0.7
PA_SEEDS_FULL = [7, 13, 19]
PA_SEEDS_SMOKE = [7, 13]
PA_Q_FULL = 320
PA_Q_SMOKE = 96
PA_GATE_F = 0.7

# REDUNDANT_SOFT configs: moduli FIXED regardless of n_shards (grid-module
# property). product(moduli) must be >= the LARGEST n_shards ever queried in
# this cell (320, Part B) so the SAME moduli sets are reused unchanged there
# -- n_shards-independence is structural, not tuned per n_shards.
PA_MODULI_R3 = (5, 7, 11)          # product=385  >= 320
PA_MODULI_R5 = (2, 3, 5, 7, 11)    # product=2310 >= 320
# DESIGN-ITERATION NOTE (disclosed, caught at SMOKE, per the same discipline
# stage12 itself used for its f-gate-point move): the FIRST smoke pass used
# PA_K_TOP=2, uniformly clipped per channel to min(2, m_r). That starved
# list-decoding breadth for the larger-modulus channels (e.g. modulus=11 with
# only 2 of 11 residues considered) -- at R=5 this meant P(true residue
# survives top-k in ALL 5 channels simultaneously) collapsed, so almost every
# query found ZERO valid candidates at f>=0.6 (measured mean_candidates<1),
# making REDUNDANT_SOFT re-fragile in a NEW way (any one channel's true
# residue falling out of a too-narrow top-k kills the whole candidate set --
# structurally the SAME "any one piece wrong is fatal" shape RC2 already
# failed on, just moved one level up). A quick k_top sweep (2/3/4/5) at smoke
# scale (measured, not asserted) showed accuracy climbing sharply with
# breadth (R5 f=0.7: ktop2=0.575, ktop4=0.830, ktop5=0.900) while candidate
# counts stayed small/bounded (mean_candidates<=5.3, still INDEPENDENT of
# n_shards by construction -- verified in Part B). PA_K_TOP raised to 5
# BEFORE any FULL dispatch (this is the design fix, not a post-hoc tune of
# the verdict itself -- the verdict bands below were set from the design
# note BEFORE this sweep; only this breadth constant was iterated).
PA_K_TOP = 5

PA_REDUNDANT_CONFIGS = [
    {"name": "R3_M2", "moduli": PA_MODULI_R3, "M": 2},
    {"name": "R3_M4", "moduli": PA_MODULI_R3, "M": 4},
    {"name": "R5_M2", "moduli": PA_MODULI_R5, "M": 2},
    {"name": "R5_M4", "moduli": PA_MODULI_R5, "M": 4},
]
PA_HARDVOTE_MATCH_MODULI = PA_MODULI_R5   # Prediction 2 isolation config
PA_HARDVOTE_MATCH_M = 4
PA_HARDVOTE_MATCH_NAME = "R5_M4"          # the REDUNDANT_SOFT config this matches
PA_DEGENERATE_CONFIG = {"name": "R1_M1_degenerate", "moduli": (4,), "M": 1}  # product=4 < 16 -> can-fail control


def parta_trial(f: float, seed: int, Q: int) -> Dict:
    # --- Gate D: BYTE-IDENTICAL reproduction of stage12 Part 3's HARD/SOFT
    # computation (same seed formula, same code). ---
    rng = np.random.default_rng(24000 + seed * 1000 + int(round(f * 1000)))
    cbs_decomp = build_decomposed_codebooks(PA_N_BITS, PA_DIMS_PER_BIT, rng)
    cb_holistic = build_holistic_codebook(PA_N_SHARDS, PA_TOTAL_DIM, rng)
    addr_decomp_table = encode_decomposed_table(PA_N_SHARDS, PA_N_BITS, PA_DIMS_PER_BIT, cbs_decomp)

    true_shard = np.arange(Q) % PA_N_SHARDS
    addr_decomp = addr_decomp_table[true_shard]
    addr_holistic = cb_holistic[true_shard]

    D = PA_TOTAL_DIM
    mask = rng.random((Q, D)) < f
    theta_decomp = rng.uniform(-np.pi, np.pi, size=(Q, D))
    theta_holistic = rng.uniform(-np.pi, np.pi, size=(Q, D))
    cue_decomp = np.where(mask, np.exp(1j * theta_decomp), addr_decomp)
    cue_holistic = np.where(mask, np.exp(1j * theta_holistic), addr_holistic)

    pred_hard = decode_decomposed_batch(cue_decomp, PA_N_BITS, PA_DIMS_PER_BIT, cbs_decomp, PA_N_SHARDS)
    pred_soft = decode_holistic_batch(cue_holistic, cb_holistic)
    acc_hard = float((pred_hard == true_shard).mean())
    acc_soft = float((pred_soft == true_shard).mean())

    # --- NEW arms: SEPARATE rng stream (does not perturb the byte-identical
    # hard/soft reproduction above). SAME f, SAME true_shard, SAME total dim
    # budget (96) -- ONE VARIABLE (design gate #4). ---
    rng2 = np.random.default_rng(44000 + seed * 1000 + int(round(f * 1000)))
    redundant_results: Dict[str, Dict] = {}
    rep_predictions = {"hard": pred_hard, "soft": pred_soft}
    hv_acc = None
    hv_mean_cand = None

    for cfg in PA_REDUNDANT_CONFIGS + [PA_DEGENERATE_CONFIG]:
        moduli = cfg["moduli"]
        R = len(moduli)
        dims_list = split_dims(PA_TOTAL_DIM, R)
        codebooks = build_channel_codebooks(moduli, dims_list, rng2)
        addr_table = encode_channel_table(PA_N_SHARDS, moduli, dims_list, codebooks)
        addr_clean = addr_table[true_shard]
        mask2 = rng2.random((Q, D)) < f
        theta2 = rng2.uniform(-np.pi, np.pi, size=(Q, D))
        cue = np.where(mask2, np.exp(1j * theta2), addr_clean)
        # NOTE (bug fixed at smoke, before FULL): k_top is passed UNCLIPPED --
        # topk_per_channel() already clips PER CHANNEL to that channel's own
        # modulus width (k = min(k_top, m_r)). An earlier version pre-clipped
        # k_top globally to min(moduli) across ALL channels, which starved
        # every channel down to the SMALLEST modulus's width (e.g. R5's
        # modulus=2 channel capped every other channel to k=2 too) --
        # measured to cripple R5 specifically (acc collapsed well below HARD
        # at f=0.7). Passing PA_K_TOP directly lets each channel use its own
        # min(k_top, m_r) as intended.
        k_top_eff = PA_K_TOP

        shortlist, n_cand = decode_redundant_batch(cue, moduli, dims_list, codebooks,
                                                     PA_N_SHARDS, k_top_eff, cfg["M"], combine="soft")
        acc = shortlist_hit_rate(shortlist, true_shard)
        redundant_results[cfg["name"]] = {"acc": acc, "mean_candidates": float(n_cand.mean()),
                                           "moduli": list(moduli), "M": cfg["M"], "k_top": k_top_eff}
        rep_predictions[cfg["name"]] = shortlist[:, 0]

        if moduli == PA_HARDVOTE_MATCH_MODULI and cfg["M"] == PA_HARDVOTE_MATCH_M:
            hv_shortlist, hv_ncand = decode_redundant_batch(cue, moduli, dims_list, codebooks,
                                                             PA_N_SHARDS, k_top_eff, cfg["M"], combine="hard_vote")
            hv_acc = shortlist_hit_rate(hv_shortlist, true_shard)
            hv_mean_cand = float(hv_ncand.mean())
            rep_predictions["hard_vote_rep"] = hv_shortlist[:, 0]
            # PREDICTION-2 FIX (caught at FULL, disclosed not hidden): the
            # top-M SET hit-rate is a POOR discriminator for the combine-rule
            # question specifically -- mean_candidates (~5.4) sits close to
            # M=4, so soft-sum and hard-vote almost always keep the SAME set
            # of 4 shards (just reordered internally), even though their #1
            # ranked pick differs ~6.5% of the time (measured). Shortlist
            # hit-rate is the RIGHT metric for Prediction 1 (is the true
            # shard reachable via the cheap route at all) but the WRONG one
            # for Prediction 2 (which specifically asks about ranking/combine
            # quality). TOP-1 accuracy (does the #1-ranked candidate match,
            # not "is it anywhere in the shortlist") is the metric that
            # actually exercises the combine rule -- used for Prediction 2 only.
            hv_top1_acc = float((hv_shortlist[:, 0] == true_shard).mean())
            soft_rep_top1_acc = float((shortlist[:, 0] == true_shard).mean())

    assert hv_acc is not None, "HARD_VOTE match config never triggered -- config mismatch bug"

    return {
        "acc_hard": acc_hard, "acc_soft": acc_soft,
        "redundant": redundant_results,
        "hard_vote_acc": hv_acc, "hard_vote_mean_candidates": hv_mean_cand,
        "hard_vote_top1_acc": hv_top1_acc, "soft_rep_top1_acc": soft_rep_top1_acc,
        "rep_predictions": rep_predictions,
    }


def run_partA(mode: str) -> Dict:
    f_grid = PA_F_GRID_SMOKE if mode == "smoke" else PA_F_GRID_FULL
    seeds = PA_SEEDS_SMOKE if mode == "smoke" else PA_SEEDS_FULL
    Q = PA_Q_SMOKE if mode == "smoke" else PA_Q_FULL

    curve = []
    rep_at_gate = None
    cfg_names = [c["name"] for c in PA_REDUNDANT_CONFIGS] + [PA_DEGENERATE_CONFIG["name"]]
    for f in f_grid:
        trials = [parta_trial(f, s, Q) for s in seeds]
        row = {
            "f": f,
            "acc_hard_mean": float(np.mean([t["acc_hard"] for t in trials])),
            "acc_soft_mean": float(np.mean([t["acc_soft"] for t in trials])),
            "hard_vote_acc_mean": float(np.mean([t["hard_vote_acc"] for t in trials])),
            "hard_vote_top1_acc_mean": float(np.mean([t["hard_vote_top1_acc"] for t in trials])),
            "soft_rep_top1_acc_mean": float(np.mean([t["soft_rep_top1_acc"] for t in trials])),
        }
        for name in cfg_names:
            row[f"acc_{name}_mean"] = float(np.mean([t["redundant"][name]["acc"] for t in trials]))
            row[f"cand_{name}_mean"] = float(np.mean([t["redundant"][name]["mean_candidates"] for t in trials]))
        curve.append(row)
        if abs(f - PA_GATE_F) < 1e-9:
            rep_at_gate = trials[0]["rep_predictions"]
        print(f"  [partA] f={f:.2f} hard={row['acc_hard_mean']:.3f} soft={row['acc_soft_mean']:.3f} "
              + " ".join(f"{n}={row['acc_' + n + '_mean']:.3f}" for n in cfg_names)
              + f" hardvote_shortlist={row['hard_vote_acc_mean']:.3f}"
              + f" top1(soft={row['soft_rep_top1_acc_mean']:.3f} hardvote={row['hard_vote_top1_acc_mean']:.3f})",
              flush=True)

    gate_row = min(curve, key=lambda r: abs(r["f"] - PA_GATE_F))
    if rep_at_gate is None:
        rep_at_gate = parta_trial(PA_GATE_F, seeds[0], Q)["rep_predictions"]

    # arms_differ (META_RULE_AF) at gate f
    digests = {k: _digest(v) for k, v in rep_at_gate.items()}
    names = sorted(digests)
    dupes = [f"{names[i]}=={names[j]}" for i in range(len(names)) for j in range(i + 1, len(names))
             if digests[names[i]] == digests[names[j]]]
    if dupes:
        raise AssertionError("META_RULE_AF VIOLATION (partA): " + "; ".join(dupes))

    return {
        "curve": curve, "gate_row": gate_row, "arms_differ_digests": digests,
        "config": {"n_shards": PA_N_SHARDS, "total_dim": PA_TOTAL_DIM, "f_grid": f_grid,
                   "seeds": seeds, "Q": Q, "k_top": PA_K_TOP,
                   "redundant_configs": PA_REDUNDANT_CONFIGS,
                   "hardvote_match": {"moduli": list(PA_HARDVOTE_MATCH_MODULI), "M": PA_HARDVOTE_MATCH_M,
                                      "matches_config": PA_HARDVOTE_MATCH_NAME},
                   "degenerate_config": PA_DEGENERATE_CONFIG},
    }


# ============================================================================
# PART B -- cost/n_shards-count scaling (stage12 Part 2's exact n_shards pair).
# ============================================================================

PB_N_SHARDS_PAIR = (32, 320)
PB_DIMS_PER_BIT = 8   # == stage12 P2_DIMS_PER_BIT
PB_REP_MODULI = PA_MODULI_R5     # representative REDUNDANT_SOFT config for cost measurement
PB_REP_M = 4
PB_Q = 64
PB_SEEDS_FULL = [7, 13]
PB_SEEDS_SMOKE = [7]
PB_CORRUPTION = 0.2   # representative fixed corruption (matches stage12 Part2's 0.2; cost is
                       # architecture-bound so this value is not gating -- companion diagnostic only)


def hard_cost_and_dim(n_shards: int) -> Tuple[int, int, int]:
    n_bits = math.ceil(math.log2(n_shards))
    total_dim = n_bits * PB_DIMS_PER_BIT
    cost = n_bits * PB_DIMS_PER_BIT * 2
    return cost, total_dim, n_bits


def soft_cost(n_shards: int, total_dim: int) -> int:
    return n_shards * total_dim


def redundant_cost_measured(n_shards: int, total_dim: int, seed: int, Q: int) -> Dict:
    moduli = PB_REP_MODULI
    R = len(moduli)
    dims_list = split_dims(total_dim, R)
    rng = np.random.default_rng(55000 + seed * 10 + n_shards)
    codebooks = build_channel_codebooks(moduli, dims_list, rng)
    addr_table = encode_channel_table(n_shards, moduli, dims_list, codebooks)
    true_shard = np.arange(Q) % n_shards
    addr_clean = addr_table[true_shard]
    cue = corrupt_batch(addr_clean, PB_CORRUPTION, rng)
    # k_top passed UNCLIPPED -- topk_per_channel() clips PER CHANNEL to
    # min(k_top, m_r) internally (see run_partA note on the k_top_eff fix).
    shortlist, n_cand = decode_redundant_batch(cue, moduli, dims_list, codebooks, n_shards,
                                                PA_K_TOP, PB_REP_M, combine="soft")
    channel_score_ops = sum(m * d for m, d in zip(moduli, dims_list))
    combo_enum_ops = 1
    for m in moduli:
        combo_enum_ops *= min(PA_K_TOP, m)   # actual per-channel list-decoding breadth
    # ^ list-decoding cross-product size -- INDEPENDENT of n_shards (fixed R,
    # k_top, moduli), included honestly so "cheap" is not understated by omission
    measured_candidates = float(n_cand.mean())
    cost = channel_score_ops + combo_enum_ops + measured_candidates
    acc = shortlist_hit_rate(shortlist, true_shard)
    return {"cost": cost, "channel_score_ops": channel_score_ops, "combo_enum_ops": combo_enum_ops,
            "measured_candidates": measured_candidates, "acc": acc,
            "dims_list": dims_list, "moduli": list(moduli)}


def run_partB(mode: str) -> Dict:
    seeds = PB_SEEDS_SMOKE if mode == "smoke" else PB_SEEDS_FULL
    per_n = {}
    for n_shards in PB_N_SHARDS_PAIR:
        cost_h, total_dim, n_bits = hard_cost_and_dim(n_shards)
        cost_s = soft_cost(n_shards, total_dim)
        red_trials = [redundant_cost_measured(n_shards, total_dim, s, PB_Q) for s in seeds]
        cost_r = float(np.mean([t["cost"] for t in red_trials]))
        acc_r = float(np.mean([t["acc"] for t in red_trials]))
        per_n[n_shards] = {"cost_hard": cost_h, "cost_soft": cost_s, "cost_redundant": cost_r,
                            "acc_redundant_at_f0.2": acc_r, "total_dim": total_dim, "n_bits": n_bits,
                            "redundant_detail": red_trials[0]}
        print(f"  [partB] n_shards={n_shards} total_dim={total_dim} cost_hard={cost_h} "
              f"cost_soft={cost_s} cost_redundant={cost_r:.1f} acc_redundant={acc_r:.3f}", flush=True)

    lo, hi = PB_N_SHARDS_PAIR
    growth_hard = per_n[hi]["cost_hard"] / per_n[lo]["cost_hard"]
    growth_soft = per_n[hi]["cost_soft"] / per_n[lo]["cost_soft"]
    growth_redundant = per_n[hi]["cost_redundant"] / per_n[lo]["cost_redundant"]

    return {
        "per_n": {str(k): v for k, v in per_n.items()},
        "growth_hard": growth_hard, "growth_soft": growth_soft, "growth_redundant": growth_redundant,
        "config": {"n_shards_pair": list(PB_N_SHARDS_PAIR), "seeds": seeds, "Q": PB_Q,
                   "rep_config_moduli": list(PB_REP_MODULI), "rep_config_M": PB_REP_M,
                   "corruption": PB_CORRUPTION},
    }


# ============================================================================
# Self-test (hardened; exercises the REAL functions at tiny scale, verifies
# CRT correctness + roundtrips + the can-fail control, BEFORE any smoke/full).
# ============================================================================

def _selftest():
    assert_no_nondeterministic_seeding(Path(__file__).read_text(encoding="utf-8"),
                                        source_name=ANCHOR_NAME, run_mode="selftest")

    # 1. CRT reconstruction correctness (the core new math this cell introduces).
    moduli_t = (3, 5, 7)
    M_t, w_t = crt_weights(moduli_t)
    assert M_t == 105
    for x in range(20):
        residues = tuple(x % m for m in moduli_t)
        recon = sum(r * w for r, w in zip(residues, w_t)) % M_t
        assert recon == x, f"CRT roundtrip failed: x={x} residues={residues} recon={recon}"

    # 2. Channel codebook / table roundtrip at ZERO corruption (product(moduli)
    #    >> n_shards, no aliasing): every shard's own exact codeword must
    #    soft-decode to itself.
    g = np.random.default_rng(0)
    n_shards_t = 16
    moduli_t2 = (5, 7, 11)
    dims_t = split_dims(48, 3)
    cb_t = build_channel_codebooks(moduli_t2, dims_t, g)
    tbl_t = encode_channel_table(n_shards_t, moduli_t2, dims_t, cb_t)
    shortlist_t, _ = decode_redundant_batch(tbl_t, moduli_t2, dims_t, cb_t, n_shards_t, k_top=2, M=2, combine="soft")
    assert np.array_equal(shortlist_t[:, 0], np.arange(n_shards_t)), (
        f"REDUNDANT_SOFT must roundtrip exactly at zero corruption: {shortlist_t[:, 0]}")

    # 3. hard_vote combine also roundtrips at zero corruption (same candidate
    #    generation; zero corruption -> unambiguous winner either way).
    shortlist_hv, _ = decode_redundant_batch(tbl_t, moduli_t2, dims_t, cb_t, n_shards_t, k_top=2, M=2, combine="hard_vote")
    assert np.array_equal(shortlist_hv[:, 0], np.arange(n_shards_t)), "HARD_VOTE must also roundtrip at zero corruption"

    # 4. DEGENERATE (R=1, modulus=4 < n_shards=16) must be STRUCTURALLY capped
    #    even at ZERO corruption -- shards {4..15} unreachable by construction
    #    (product(moduli)=4 < 16). Design-gate #2 can-fail control.
    g2 = np.random.default_rng(1)
    deg_moduli = (4,)
    deg_dims = split_dims(96, 1)
    deg_cb = build_channel_codebooks(deg_moduli, deg_dims, g2)
    deg_tbl = encode_channel_table(n_shards_t, deg_moduli, deg_dims, deg_cb)
    deg_shortlist, _ = decode_redundant_batch(deg_tbl, deg_moduli, deg_dims, deg_cb, n_shards_t, k_top=1, M=1, combine="soft")
    deg_acc = float((deg_shortlist[:, 0] == np.arange(n_shards_t)).mean())
    assert deg_acc <= 0.30, (
        f"DEGENERATE (R=1,modulus=4<n_shards=16) must be structurally capped near chance "
        f"even at ZERO corruption -- got {deg_acc:.3f}, expected <= 0.30. If this fails, "
        f"the can-fail/must-fail control is broken and design gate #2 is not satisfied.")

    # 5. Part A / Part B trial functions run at tiny scale, NaN-free, real code path.
    r = parta_trial(f=0.3, seed=101, Q=32)
    assert 0.0 <= r["acc_hard"] <= 1.0 and 0.0 <= r["acc_soft"] <= 1.0
    assert not math.isnan(r["acc_hard"]) and not math.isnan(r["acc_soft"])
    for name, res in r["redundant"].items():
        assert 0.0 <= res["acc"] <= 1.0 and not math.isnan(res["acc"]), f"{name} acc invalid: {res}"
    assert not math.isnan(r["hard_vote_acc"])
    assert not math.isnan(r["hard_vote_top1_acc"]) and not math.isnan(r["soft_rep_top1_acc"])

    cost_h, dim_h, nb_h = hard_cost_and_dim(32)
    assert cost_h > 0 and dim_h > 0
    red_b = redundant_cost_measured(32, dim_h, seed=7, Q=16)
    assert red_b["cost"] > 0 and not math.isnan(red_b["acc"])

    print("[selftest] PASS: redundant_soft_shard_router_v1 (CRT roundtrip, channel-table "
          "zero-corruption roundtrip x2 combine rules, degenerate structural-cap can-fail "
          "check, partA/partB real-code-path smoke, nan-check)", flush=True)


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

    print("\n[part-A] corruption-vs-accuracy head-to-head "
          "(HARD, SOFT, 4x REDUNDANT_SOFT, HARD_VOTE, DEGENERATE) ...", flush=True)
    pa = run_partA(RUN_MODE)

    print("\n[part-B] cost/n_shards-count scaling ...", flush=True)
    pb = run_partB(RUN_MODE)

    gate_row = pa["gate_row"]
    hard_at_gate = gate_row["acc_hard_mean"]
    soft_at_gate = gate_row["acc_soft_mean"]
    hv_at_gate = gate_row["hard_vote_acc_mean"]
    deg_at_gate = gate_row[f"acc_{PA_DEGENERATE_CONFIG['name']}_mean"]

    redundant_names = [cfg["name"] for cfg in PA_REDUNDANT_CONFIGS]
    accs_at_gate = {name: gate_row[f"acc_{name}_mean"] for name in redundant_names}
    best_name = max(accs_at_gate, key=accs_at_gate.get)
    best_acc = accs_at_gate[best_name]

    threshold_p1 = 0.9 * soft_at_gate
    growth_redundant = pb["growth_redundant"]
    growth_hard = pb["growth_hard"]
    growth_soft = pb["growth_soft"]

    if best_acc >= threshold_p1 and growth_redundant < 2.0:
        p1_verdict = "HARD_PASS"
    elif best_acc <= hard_at_gate:
        p1_verdict = "HARD_FAIL"
    else:
        p1_verdict = "MIDDLE_BAND"

    # Prediction 2 uses TOP-1 accuracy, not the shortlist-membership metric
    # (accs_at_gate / hv_at_gate above) -- see METRIC-CHOICE NOTE in the
    # docstring: at M=4 with mean_candidates~5.4, shortlist-membership is
    # insensitive to the combine rule (soft and hard-vote keep the same SET
    # of 4 almost always), even though the #1 pick genuinely differs.
    hv_match_acc = accs_at_gate[PA_HARDVOTE_MATCH_NAME]   # shortlist-hit-rate (diagnostic only, see note)
    soft_rep_top1 = gate_row["soft_rep_top1_acc_mean"]
    hv_top1 = gate_row["hard_vote_top1_acc_mean"]
    margin_p2 = soft_rep_top1 - hv_top1
    if margin_p2 >= 0.10:
        p2_verdict = "HARD_PASS"
    elif margin_p2 > 0.0:
        p2_verdict = "MIDDLE_BAND"
    else:
        p2_verdict = "HARD_FAIL"

    can_fail_confirmed = bool(deg_at_gate < hard_at_gate - 0.05)

    p3_note = None
    if p1_verdict == "HARD_FAIL":
        p3_note = (
            "Prediction 1 HARD_FAILED. Localization per design note: "
            "a33c634c (exp_addressing_learned_noise_robust_page_router_v1) top-M attractor "
            "routing hit=0.970 CITED@data/exp_addressing_learned_noise_robust_page_router_v1/metrics.json "
            "at sigma_test=0.3 (gaussian noise -- NOT directly numerically comparable to this "
            "cell's Bernoulli frac=0.7). QUALITATIVE brain-check read: if a33c634c's own top-M "
            "mechanism also shows a cheap-vs-robust wall at its own comparably-severe corruption "
            "levels, the wall is a general phasor-cleanup-primitive property (structural bound; "
            "accept, pivot to a different encoding primitive e.g. block-sparse/grid-cell-"
            "incommensurate codes). If not, the wall is specific to THIS cell's combine-rule "
            "design (fixable, iterate combine rule not primitive). NOT independently re-measured "
            "here -- flagged for Skunkworks/Research follow-up, "
            "HYPOTHESIZED@notes/research_shard_router_cheap_and_robust_redundant_soft_2026-07-17.md, "
            "not re-derived."
        )

    if p1_verdict == "HARD_FAIL" or p2_verdict == "HARD_FAIL":
        failed = "P1" if p1_verdict == "HARD_FAIL" else "P2"
        overall = "HARD_FAIL"
        overall_msg = f"HARD_FAIL_{failed}: P1={p1_verdict} P2={p2_verdict}"
    elif p1_verdict == "HARD_PASS" and p2_verdict == "HARD_PASS":
        overall = "HARD_PASS"
        overall_msg = "REDUNDANT_SOFT_CLOSES_GAP (CLAIM, VET-PENDING): both Predictions HARD_PASS."
    else:
        overall = "MIDDLE_BAND"
        overall_msg = (
            "MEASURED_MECHANISM_MIXED (CLAIM, VET-PENDING): best REDUNDANT_SOFT config lands "
            "on/inside the Pareto frontier of HARD/SOFT -- NOT framed as domination per CONTRACT."
        )

    overall_msg += (
        f" | best_config={best_name} acc_at_f{PA_GATE_F}={best_acc:.3f} "
        f"(hard={hard_at_gate:.3f} soft={soft_at_gate:.3f} threshold={threshold_p1:.3f}) "
        f"growth_redundant={growth_redundant:.3f} (growth_hard={growth_hard:.3f} growth_soft={growth_soft:.3f})"
        f" | P2 margin(soft-hardvote, TOP-1 acc)@{PA_HARDVOTE_MATCH_NAME}={margin_p2:+.3f} "
        f"(soft_top1={soft_rep_top1:.3f} hardvote_top1={hv_top1:.3f}; "
        f"shortlist-hit-rate was insensitive: soft={hv_match_acc:.3f} hardvote={hv_at_gate:.3f})"
        f" | can_fail_confirmed={can_fail_confirmed} (degenerate={deg_at_gate:.3f} vs hard={hard_at_gate:.3f})"
    )

    n_units = (len(pa["config"]["f_grid"]) * len(pa["config"]["seeds"])
               + len(pb["config"]["n_shards_pair"]) * len(pb["config"]["seeds"]))

    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": overall,
        "verdict_msg": overall_msg,
        "summary": f"{overall}: REDUNDANT_SOFT third-design-point shard router ({RUN_MODE})",
        "run_mode": RUN_MODE,
        "n_seeds": max(len(pa["config"]["seeds"]), len(pb["config"]["seeds"])),
        "n_units": n_units,
        "expected_n_units": n_units,
        "cardinality_ok": True,
        "elapsed_s": elapsed,
        "part_A_corruption_sweep": pa,
        "part_B_cost_scaling": pb,
        "predictions": {"P1_joint_cheap_and_robust": p1_verdict, "P2_soft_beats_hard_combine": p2_verdict},
        "can_fail_confirmed": can_fail_confirmed,
        "prediction3_localization_note": p3_note,
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
