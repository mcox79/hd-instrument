"""exp_redundant_soft_shard_router_e2e_stage12_v1 -- TRUE END-TO-END fuzzy
retrieval: Stage-1 (REDUNDANT_SOFT route -> top-M shard shortlist) -> Stage-2
(within-shard attractor completion, WM-bundle unbind+cleanup) -> retrieved
(shard, val) item. Answers the question the prior two cells did NOT answer:
does the shortlist approach stay cheap-AND-robust END-TO-END, or does the
M-factor in Stage-2 (M x completion cost, one completion run PER shortlisted
shard) eat the routing win?

PRIOR-WORK CHECK (substrate-KB concept-query, mandatory per exp_dev
discipline): `bash tools/substrate_query.sh "end-to-end fuzzy retrieval
two-stage router shard shortlist attractor completion honest cost
M-factor"` -> top hit cosine=0.25 ('attractor'/'shortlist' WordNet entries),
all top-5 <= 0.25, NONE at cosine > 0.30 -> genuinely novel test, not a
rediscovery.

DESIGN SOURCE: notes/research_shard_router_cheap_and_robust_redundant_soft_2026-07-17.md
REUSED CELLS (this cell composes both, does not re-derive either mechanism):
  - exp_redundant_soft_shard_router_v1 (commits 16a37a528+1034bae79): Stage-1
    REDUNDANT_SOFT router. Best config R3_M4: shortlist route-recall=0.969 at
    f=0.7, cost-growth=1.271 MEASURED@data/exp_redundant_soft_shard_router_v1/
    metrics.json:part_A_corruption_sweep.gate_row (hard=0.710, soft=0.973 at
    same gate f=0.7, same regime n_shards=16/total_addr_dim=96 -- reused
    VERBATIM here as Gate-D positive-control target, WITHIN TOLERANCE not
    byte-identical -- see note below on why not byte-identical).
  - exp_fuzzy_shard_router_attractor_stage12_v1 (a1955850e): Stage-2
    within-shard attractor completion (unbind cue-key against the predicted
    shard's OWN WM bundle, argmax-cleanup against that shard's OWN V_val
    codebook) + the two extreme Stage-1 routers (HARD/decomposed, SOFT/
    holistic) reused here as the end-to-end baselines this cell's design gate
    requires.

WHY NOT BYTE-IDENTICAL to the router cell's Gate-D claim (disclosed, not
hidden): the router cell corrupted ONLY the address vector (Q, 96). THIS
cell must corrupt a JOINT [address, key] concatenation with a SINGLE shared
corruption mask (matching stage12 Part-2's own joint-corruption convention,
since a real fuzzy cue corrupts the whole recall probe, not just its
address sub-field) -- the RNG draw ORDER differs from a standalone (Q,96)
draw even though the per-dim Bernoulli(f) statistics are identical. Gate D is
therefore satisfied as a WITHIN-TOLERANCE positive control (route-only
accuracy, ignoring Stage-2, must reproduce the router cell's hard=0.710 /
soft=0.973 at f=0.7 within 0.10 absolute), not a byte-identical reproduction.

===========================================================================
THE HONEST-COST CRUX (this cell's entire reason to exist)
===========================================================================
REDUNDANT_SOFT returns a top-M shortlist (M=2 or M=4 tested). Stage-2 MUST
run completion in EACH of the M shortlisted shards and pick the best
(highest completion-confidence) -- M x the Stage-2 cost of a top-1 route.
This cell measures TRUE end-to-end accuracy (is the FINAL picked (shard,val)
correct, after the M-way best-of-M selection) AND TRUE end-to-end cost
(route ops + M x completion ops), and reports both HONESTLY -- the M-factor
is never hidden or amortized away. Candidate generation (which shards make
the shortlist) is IDENTICAL for the M=2 and M=4 variants of REDUNDANT_SOFT
(M only trims the final ranked list), so the R3_M2 vs R3_M4 comparison
isolates the M-factor as cleanly as possible: same route cost, only the
M x V_val completion-cost term differs.

===========================================================================
ARCHITECTURE (ONE VARIABLE per design gate #4: same store/shards/Stage-2;
arms differ ONLY in the Stage-1 router + its M)
===========================================================================
Single regime (n_shards=16, total_addr_dim=96 -- exactly stage12 Part-3 /
router-cell's regime, for Gate-D continuity). n_shards-COUNT scaling of
Stage-1 cost was already HARD_PASSed in the router cell's Part B; this cell
does NOT re-litigate that axis -- it isolates the NEW M-factor-in-Stage-2
question at a fixed shard count.

Per (f, seed) trial: ONE store is built (16 shards, each an independent WM
bundle of m_load=8 bound key*val pairs, N_WM=256, V_val=32, V_key=64 -- see
capacity-feasibility note below). ONE shared Bernoulli(f) corruption mask is
drawn per trial and applied identically (same positions redrawn) to every
arm's OWN [address, key] concatenation -- same cue-corruption PROCESS seen
by every arm, only the address ENCODING differs per arm (ONE VARIABLE).

Arms (5 total; all consume the SAME store + SAME per-query true (shard,
key, val) + SAME corruption mask):
  HARD (decomposed, top-1 route, cheap+fragile): reused verbatim decode.
  SOFT (holistic, top-1 route, robust+expensive): reused verbatim decode.
  REDUNDANT_SOFT R3 (moduli=(5,7,11), k_top=5 -- reused verbatim from the
    router cell's best-scoring config family): ONE decode_redundant_batch
    call at M=4 produces the ranked shortlist; R3_M2's shortlist is the
    PREFIX shortlist[:, :2] of that SAME ranked list (top-M is nested by
    construction -- top-2 is always a prefix of top-4), so R3_M2 and R3_M4
    share IDENTICAL candidate generation and cost up to the M x V_val
    completion term -- the cleanest possible M-factor isolation.
  DEGENERATE (R=1, modulus=4 < n_shards=16, M=1): can-fail/must-fail
    control, reused verbatim from the router cell -- structurally capped
    route ceiling (product(moduli)=4 -> shards {4..15} unreachable)
    regardless of corruption, proving the verdict machinery emits a genuine
    bad number for a bad design, not a vacuously-always-passing one.

Stage-2 (NEW, generalizes stage12's single-shard stage2_batch_by_group to an
arbitrary per-query M-column shortlist): for EACH of the M shortlisted shard
columns, run unbind(cue_key, shard_bundle) + argmax-cleanup against that
shard's OWN V_val codebook, keep a running per-query best (shard, val,
score) across the M columns (score = the cleanup argmax's own real-inner-
product value -- the natural "pick the highest-confidence completion across
candidates" combine rule). HARD/SOFT/DEGENERATE call the SAME function with
a width-1 shortlist (M=1) -- one unified code path for all 5 arms, no
special-cased single-shard branch.

CAPACITY-FEASIBILITY (m_load well below the naive capacity cliff, so Stage-2
degradation at a given f is driven by CUE CORRUPTION, not by bundle-capacity
saturation -- keeps the two effects from being confounded): k_cliff_naive(N=
256, V=32) = 256/(4*ln(32)) = 18.47 THEORETICAL@k_cliff_naive=N/(4*ln(V))
(copied formula, CITED@notes/research_5x_drill_N_scaling_analytical_formula_
2026-07-01.md via stage12 reuse). m_load=8 = 43% of the naive cliff (well
below; the CORRECTED/calibrated cliff, per stage12's own C_FHRR~1.99x
correction, is larger still) -- Stage-2 completion at f=0 is expected near-
ceiling, so any degradation across the f-sweep is attributable to cue
corruption, not capacity pressure.

===========================================================================
FALSIFIABLE PRE-REGISTERED PREDICTIONS (bands set BEFORE running FULL)
===========================================================================
Gate f = 0.7 (Gate-D continuity: the SAME gate point as the router cell /
stage12 Part 3). Full corruption sweep f in {0.0, 0.5, 0.6, 0.7, 0.8, 0.9}
(difficulty-ON per design gate #3, includes points ABOVE 0.7; f=0.0 is the
EXACT-KEY / clean-cue UPPER-BOUND reference point per design gate #1(a) --
NOT the headline, just the ceiling check that every non-degenerate arm
reaches ~1.0 when given a clean cue end-to-end).

For REDUNDANT_SOFT config c in {R3_M2, R3_M4} (R3_M4 is PRIMARY -- the
"best config" the task pointer names; R3_M2 is a companion/diagnostic
showing the M-lever tradeoff, not separately gating the overall cell tier):
  acc_c        = e2e accuracy (route AND val both correct) at f=0.7
  cost_c       = route_cost(R3, MEASURED empirically, IDENTICAL for M=2/M=4)
                 + M_c * V_val   (the M-factor, explicit, never hidden)
  acc_ref_soft = SOFT arm's OWN measured e2e accuracy at f=0.7 (this run,
                 not a hardcoded prior value -- self-referential yardstick,
                 same pattern as the router cell's own Prediction 1)
  acc_ref_hard = HARD arm's OWN measured e2e accuracy at f=0.7
  cost_ref_soft = SOFT arm's e2e cost (route_cost_soft + 1*V_val)

  ACC_PASS_FACTOR  = 0.9   (within 10% of SOFT's e2e accuracy)
  COST_PASS_FACTOR = 0.7   ("materially below" = at least 30% cheaper e2e)
  COST_FAIL_FACTOR = 0.9   ("advantage erased" = within 10% of SOFT's cost
                             or more expensive)

  acc_pass  := acc_c >= ACC_PASS_FACTOR * acc_ref_soft
  acc_fail  := acc_c <= acc_ref_hard        (no better than the cheap-
               fragile HARD arm at all -- end-to-end acc CRATERED)
  cost_pass := cost_c <= COST_PASS_FACTOR * cost_ref_soft
  cost_fail := cost_c >= COST_FAIL_FACTOR * cost_ref_soft   (the M-factor
               erased the routing cost advantage -- no cheap-AND-robust
               point end-to-end)

  HARD-PASS (config c):   acc_pass AND cost_pass
  HARD-FAIL (config c):   acc_fail OR cost_fail
  MIDDLE_BAND (config c): otherwise (a genuine Pareto-frontier point --
                          explicitly NOT reported as domination, per CONTRACT)

OVERALL CELL TIER (keyed to the PRIMARY config R3_M4; R3_M2 reported as a
companion, never itself promoted to the overall tier):
  "E2E_CLOSES_GAP" (CLAIM, VET-PENDING): R3_M4 HARD-PASS.
  "HARD_FAIL_ACC" / "HARD_FAIL_COST": R3_M4 HARD-FAIL (acc_fail checked
    first; if acc_fail is False but cost_fail is True, HARD_FAIL_COST).
  "MEASURED_MECHANISM_MIXED" (CLAIM, VET-PENDING): otherwise (Pareto point).

CAN-FAIL VERIFICATION (design gate #2, MANDATORY, verified at self-test AND
  reported at smoke+FULL): DEGENERATE e2e accuracy at gate f MUST score
  below HARD's e2e accuracy by >= 0.05 (`can_fail_confirmed` field) --
  demonstrates the verdict machinery emits a genuinely bad number for a bad
  design, structurally forced (product(moduli)=4 < 16), not cherry-picked.

DISCRIMINATOR-MUST-FIRE (baseline_in_band, META_RULE_AG): HARD and SOFT e2e
  accuracy at gate f=0.7 must each sit in (0.05, 0.95) -- verified at smoke
  BEFORE FULL dispatch; if either saturates (key corruption at f=0.7 turns
  out too weak to touch Stage-2 given m_load=8's generous capacity
  headroom), the f-grid/gate point is re-spec'd before FULL, exactly the
  same iteration discipline both reused cells already exercised once each.

===========================================================================
SCHEMA-VET GATES
===========================================================================
storage_strategy: sharded (each of the 16 shards its own independent WM
  bundle; no cross-shard bundling anywhere in this cell).
cardinality_ok: EXPECTED_N_UNITS = len(f_grid) * len(seeds); verdict counts
  actual units run via len(curve).
real_code_path/substrate_signature (F.1-F.4): N/A -- self-contained numpy
  FHRR-style primitives, no KGStore/fit-module/live substrate object.
crlb_floor_computed: e2e chance floor (uniform-random guess) = 1/(n_shards*
  V_val) = 1/(16*32) = 1/512 = 0.00195 for HARD/SOFT/DEGENERATE (M=1);
  M-shortlist arms' "reachable-by-chance" floor is M/(n_shards*V_val) --
  still far below all HARD_PASS thresholds (which are set RELATIVE to this
  run's own measured SOFT arm, itself far above floor per the router cell's
  and stage12's own prior measurements in this exact regime).
baseline_in_band (META_RULE_AG): verified at smoke BEFORE FULL (see
  DISCRIMINATOR-MUST-FIRE above) -- HARD/SOFT e2e acc at gate f in (0.05,0.95).
calibration_check: "default_ok_for_this_regime" -- Stage-1 router constants
  (moduli, k_top, dims_per_bit, total_addr_dim) are BYTE-IDENTICAL reuse of
  the router cell's already-landed R3 config; Stage-2's m_load is chosen via
  the CRLB-style capacity-feasibility note above (43% of naive cliff), not
  refit to any observed accuracy.
deterministic_seeding: fixed int seeds only (np.random.default_rng(int) with
  fixed integer offsets per part/config/seed/f); no PYTHONHASHSEED-derived
  seeding or set-iteration-order dependence anywhere in this file (scanned
  via assert_no_nondeterministic_seeding at self-test, PROT-023 auto-scan at
  ship).
discriminator survives scale: smoke uses the SAME real (n_shards=16,
  total_addr_dim=96, N_WM=256, V_val=32, m_load=8) values as FULL -- only
  f-grid points and seed counts are reduced for smoke wall-time (option A).
arms_differ_verified (META_RULE_AF): at the gate f row, final (pred_shard,
  pred_val) tuples for HARD, SOFT, R3_M2, R3_M4, DEGENERATE are hashed and
  asserted pairwise-distinct.
final_metrics_atomicity: tmp_replace (via experiments._seed_checkpoint.write_metrics).
cell_chunked: false. JUSTIFICATION (exemption, per SS13's runner-zombie
  rationale, same as both reused cells): dispatched INLINE/FOREGROUND on
  local compute per task instruction (queue is down) -- operator directly
  observes the foreground process; total wall time estimated well under 2
  minutes (all numpy matmuls at N_WM<=256, n_shards=16, V_val<=32, m_load=8,
  Q<=320 -- small arrays throughout).
progress_logging: print_flush_true (stdout reconfigured to line-buffering;
  every f-grid point emits a progress line with flush=True). Declared
  defensively; expected wall time is well under the 1800s threshold that
  would make this MANDATORY.
Compute architecture: (a) vectorized-numpy for per-query channel scoring,
  CRT reconstruction, and Stage-2 unbind+cleanup (batched matmul/broadcast
  over all Q queries at once per shard-group); small Python-level loops over
  (i) the M shortlist columns (constant, <=4) and (ii) the per-shard groups
  within a column (<=16 shards) -- neither loop scales with Q or n_shards
  in a way that defeats vectorization. CPU is appropriate at this scale (GPU
  dispatch would be pure overhead for a sub-minute total wall time).
effective_vs_nominal_parameter_audit (Gate A): sweep axis is f (corruption
  fraction); experienced DIRECTLY and IDENTICALLY (same shared mask) by
  every arm's own [address, key] concatenation -- no upstream re-scoping
  layer. sweep_alignment_verdict: ALIGNED.
bracket_includes_discriminating_band (Gate B): f grid reuses the router
  cell's / stage12 Part-3's own pre-dispatch-probed discriminating band for
  Stage-1 routing ({0.6,0.7,0.8,0.9} non-saturated for HARD/SOFT); Stage-2's
  OWN sensitivity to key corruption is verified NOT saturated at smoke
  (baseline_in_band check above) before FULL dispatch.
signal_shape_compatibility_audit (Gate C): Stage-1 shortlist (int array,
  -1-padded) -> Stage-2 completion (per-column grouped unbind+cleanup) edge
  is SHAPE_MATCH -- verified via self-test roundtrip (M=1 and M>1 both
  exercised at zero corruption).
reproduce_prior_chain_grade_result_as_positive_control (Gate D): HARD/SOFT/
  REDUNDANT_SOFT-R3/DEGENERATE Stage-1 ROUTE-ONLY accuracy (ignoring Stage-2)
  at f=0.7 must reproduce the router cell's MEASURED@data/exp_redundant_soft_
  shard_router_v1/metrics.json:part_A_corruption_sweep.gate_row values
  (hard=0.7104, soft=0.9729, R3_M4-shortlist-hit=0.9688) WITHIN TOLERANCE
  0.10 absolute (NOT byte-identical -- see the joint-corruption note above
  for why). Verified at smoke before FULL; reported in metrics as
  `gate_d_positive_control`.
HP_SCOPE: {HARD: [e2e_reference_only], SOFT: [e2e_reference_only],
  R3_M4: [PRIMARY e2e HARD_PASS/FAIL gate], R3_M2: [companion, own verdict
  reported, does not gate overall tier], DEGENERATE: [can_fail_check_only]}
ASCII-only. FHRR = complex128 unit phasors (bind=elementwise multiply,
unbind=multiply by conjugate, cleanup=argmax of Re(Hermitian inner product)).
Local numpy; no queue-remote/GPU/atoms/push. Run:
  python experiments/exp_redundant_soft_shard_router_e2e_stage12_v1.py [--self-test|--smoke]
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

ANCHOR_NAME = "redundant_soft_shard_router_e2e_stage12_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--timeout", type=float, default=0.0)  # accepted for harness parity
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = "smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full").lower()


# ============================================================================
# REUSED VERBATIM from exp_redundant_soft_shard_router_v1.py (commit 1034bae79)
# and exp_fuzzy_shard_router_attractor_stage12_v1.py (commit a1955850e).
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
    """Soft-sum combine ONLY (this cell does not re-test hard-vote -- that
    Prediction-2 question was already answered in the router cell). Returns
    (shortlist (Q,M) int, -1-padded; n_candidates (Q,) int)."""
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


def _digest(arr: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(arr).tobytes()).hexdigest()[:16]


# ============================================================================
# NEW -- Stage-2 store construction + generalized M-column shortlist completion.
# ============================================================================

def build_store(n_shards: int, N_WM: int, V_val: int, V_key: int, m_load: int,
                 seed: int) -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray],
                                     List[np.ndarray], List[np.ndarray]]:
    """One WM bundle per shard (m_load bound key*val pairs, summed). Formula
    family matches stage12 Part-1's per-shard srng offset (31000 + seed*1000
    + sid) -- reused convention, not byte-identical (fewer/different V_key,
    V_val, N_WM here)."""
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


def complete_over_shortlist(shortlist: np.ndarray, cue_key: np.ndarray,
                             bundles: List[np.ndarray], vals_list: List[np.ndarray]
                             ) -> Tuple[np.ndarray, np.ndarray]:
    """Generalized Stage-2: for EACH of the M shortlist columns, unbind
    cue_key against that column's predicted shard bundle and argmax-cleanup
    against that shard's OWN V_val codebook; keep the running best-scoring
    (shard, val) across all M columns per query (the M-way "run completion in
    every shortlisted shard, pick the highest-confidence" rule -- explicitly
    NOT free; this is exactly where the M-factor Stage-2 cost comes from).
    Works uniformly for M=1 (HARD/SOFT/DEGENERATE) and M>1 (REDUNDANT_SOFT)
    -- one code path, no special-cased single-shard branch."""
    Q, M = shortlist.shape
    best_shard = np.full(Q, -1, dtype=np.int64)
    best_val = np.full(Q, -1, dtype=np.int64)
    best_score = np.full(Q, -np.inf, dtype=np.float64)
    for m_idx in range(M):
        sid_col = shortlist[:, m_idx]
        valid = sid_col >= 0
        if not np.any(valid):
            continue
        pv = np.full(Q, -1, dtype=np.int64)
        sc = np.full(Q, -np.inf, dtype=np.float64)
        for sid in np.unique(sid_col[valid]):
            grp = valid & (sid_col == sid)
            state = bundles[sid][None, :] * np.conj(cue_key[grp])
            scores = (state @ vals_list[sid].conj().T).real
            pv[grp] = scores.argmax(axis=1)
            sc[grp] = scores.max(axis=1)
        improve = sc > best_score
        best_shard = np.where(improve, sid_col, best_shard)
        best_val = np.where(improve, pv, best_val)
        best_score = np.where(improve, sc, best_score)
    return best_shard, best_val


def make_cue(rng: np.random.Generator, mask: np.ndarray, addr_clean: np.ndarray,
             key_clean: np.ndarray) -> np.ndarray:
    """One shared mask (Q, D_addr+D_key); fresh replacement phase per arm.
    Returns the full corrupted [address, key] concatenation."""
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
# REGIME (single, matching stage12 Part 3 / router cell's Stage-1 regime;
# Stage-2 capacity-feasibility per the CAPACITY-FEASIBILITY docstring note).
# ============================================================================

E2E_N_SHARDS = 16
E2E_N_BITS = 4                    # ceil(log2(16)) -- matches P3/router cell
E2E_DIMS_PER_BIT = 24             # matches P3/router cell
E2E_TOTAL_ADDR_DIM = E2E_N_BITS * E2E_DIMS_PER_BIT   # 96 -- Gate D target

E2E_N_WM = 256                    # Stage-2 key/val vector dim
E2E_V_VAL = 32                    # per-shard value alphabet
E2E_V_KEY = 64                    # key pool per shard (8x m_load, generous)
E2E_M_LOAD = 8                    # items per shard: 43% of naive cliff (18.47)

E2E_MODULI_R3 = (5, 7, 11)        # product=385 >= 16 -- reused verbatim (router cell's best config family)
E2E_K_TOP = 5                     # reused verbatim (router cell's post-design-iteration fix)
E2E_DIMS_LIST_R3 = split_dims(E2E_TOTAL_ADDR_DIM, 3)     # [32, 32, 32]
E2E_M_MAX = 4                     # R3_M4 primary; R3_M2 = prefix shortlist[:, :2]
E2E_M_CONFIGS = [2, 4]            # R3_M2 (companion), R3_M4 (PRIMARY)
E2E_DEGENERATE_MODULI = (4,)      # product=4 < 16 -- structural can-fail control
E2E_DEGENERATE_DIMS_LIST = [E2E_TOTAL_ADDR_DIM]

E2E_F_GRID_FULL = [0.0, 0.5, 0.6, 0.7, 0.8, 0.9]
E2E_F_GRID_SMOKE = [0.0, 0.7, 0.8]
E2E_SEEDS_FULL = [7, 13, 19]
E2E_SEEDS_SMOKE = [7, 13]
E2E_Q_FULL = 320
E2E_Q_SMOKE = 96
E2E_GATE_F = 0.7

E2E_ACC_PASS_FACTOR = 0.9
E2E_COST_PASS_FACTOR = 0.7
E2E_COST_FAIL_FACTOR = 0.9

# Gate-D positive-control reference (WITHIN TOLERANCE, not byte-identical --
# see docstring). MEASURED@data/exp_redundant_soft_shard_router_v1/metrics.json
_GATE_D_PRIOR = {
    "hard_route_acc": 0.7104166666666667,
    "soft_route_acc": 0.9729166666666668,
    "r3_m4_shortlist_hit": 0.96875,
}
_GATE_D_TOLERANCE = 0.10


def e2e_trial(f: float, seed: int, Q: int) -> Dict:
    # --- Stage-2 store (independent of f; SAME store reused across the
    # f-sweep for a given seed -- realistic "same data, corrupted query"). ---
    bundles, vals_list, keys_list, key_ids_list, val_ids_list = build_store(
        E2E_N_SHARDS, E2E_N_WM, E2E_V_VAL, E2E_V_KEY, E2E_M_LOAD, seed)

    # --- Address codebooks (Gate D reuse convention: SAME rng-formula family
    # as the router cell's parta_trial). ---
    addr_rng = np.random.default_rng(24000 + seed * 1000 + int(round(f * 1000)))
    cbs_decomp = build_decomposed_codebooks(E2E_N_BITS, E2E_DIMS_PER_BIT, addr_rng)
    cb_holistic = build_holistic_codebook(E2E_N_SHARDS, E2E_TOTAL_ADDR_DIM, addr_rng)
    addr_decomp_table = encode_decomposed_table(E2E_N_SHARDS, E2E_N_BITS, E2E_DIMS_PER_BIT, cbs_decomp)

    rng2 = np.random.default_rng(44000 + seed * 1000 + int(round(f * 1000)))
    cb_r3 = build_channel_codebooks(E2E_MODULI_R3, E2E_DIMS_LIST_R3, rng2)
    addr_r3_table = encode_channel_table(E2E_N_SHARDS, E2E_MODULI_R3, E2E_DIMS_LIST_R3, cb_r3)
    cb_deg = build_channel_codebooks(E2E_DEGENERATE_MODULI, E2E_DEGENERATE_DIMS_LIST, rng2)
    addr_deg_table = encode_channel_table(E2E_N_SHARDS, E2E_DEGENERATE_MODULI, E2E_DEGENERATE_DIMS_LIST, cb_deg)

    # --- Query sampling (round-robin true_shard, matches stage12 Part-2). ---
    qrng = np.random.default_rng(23000 + seed * 1000 + int(round(f * 1000)))
    true_shard = np.arange(Q) % E2E_N_SHARDS
    local_idx = qrng.integers(0, E2E_M_LOAD, size=Q)
    true_key = np.stack([keys_list[true_shard[i]][key_ids_list[true_shard[i]][local_idx[i]]] for i in range(Q)])
    true_val = np.array([val_ids_list[true_shard[i]][local_idx[i]] for i in range(Q)])

    # --- ONE shared corruption mask across ALL arms (ONE VARIABLE gate). ---
    D_total = E2E_TOTAL_ADDR_DIM + E2E_N_WM
    mask = qrng.random((Q, D_total)) < f

    cue_hard = make_cue(qrng, mask, addr_decomp_table[true_shard], true_key)
    cue_soft = make_cue(qrng, mask, cb_holistic[true_shard], true_key)
    cue_r3 = make_cue(qrng, mask, addr_r3_table[true_shard], true_key)
    cue_deg = make_cue(qrng, mask, addr_deg_table[true_shard], true_key)

    A = E2E_TOTAL_ADDR_DIM

    # --- Stage 1: route ---
    pred_hard = decode_decomposed_batch(cue_hard[:, :A], E2E_N_BITS, E2E_DIMS_PER_BIT, cbs_decomp, E2E_N_SHARDS)
    pred_soft = decode_holistic_batch(cue_soft[:, :A], cb_holistic)
    shortlist_r3_m4, n_cand_r3 = decode_redundant_batch(
        cue_r3[:, :A], E2E_MODULI_R3, E2E_DIMS_LIST_R3, cb_r3, E2E_N_SHARDS, E2E_K_TOP, E2E_M_MAX)
    shortlist_r3_m2 = shortlist_r3_m4[:, :2]   # nested prefix -- SAME candidate generation
    shortlist_deg, _ = decode_redundant_batch(
        cue_deg[:, :A], E2E_DEGENERATE_MODULI, E2E_DEGENERATE_DIMS_LIST, cb_deg, E2E_N_SHARDS, k_top=1, M=1)

    # --- Stage 2: complete over each arm's shortlist (unified function) ---
    cue_key_hard = cue_hard[:, A:]
    cue_key_soft = cue_soft[:, A:]
    cue_key_r3 = cue_r3[:, A:]
    cue_key_deg = cue_deg[:, A:]

    bshard_hard, bval_hard = complete_over_shortlist(pred_hard.reshape(-1, 1), cue_key_hard, bundles, vals_list)
    bshard_soft, bval_soft = complete_over_shortlist(pred_soft.reshape(-1, 1), cue_key_soft, bundles, vals_list)
    bshard_r3m4, bval_r3m4 = complete_over_shortlist(shortlist_r3_m4, cue_key_r3, bundles, vals_list)
    bshard_r3m2, bval_r3m2 = complete_over_shortlist(shortlist_r3_m2, cue_key_r3, bundles, vals_list)
    bshard_deg, bval_deg = complete_over_shortlist(shortlist_deg, cue_key_deg, bundles, vals_list)

    def _route_acc(bshard):
        return float((bshard == true_shard).mean())

    def _e2e_acc(bshard, bval):
        return float(((bshard == true_shard) & (bval == true_val)).mean())

    route_acc_r3_shortlist_hit = float((shortlist_r3_m4 == true_shard[:, None]).any(axis=1).mean())

    return {
        "route_acc": {
            "hard": _route_acc(bshard_hard), "soft": _route_acc(bshard_soft),
            "R3_M4": _route_acc(bshard_r3m4), "R3_M2": _route_acc(bshard_r3m2),
            "degenerate": _route_acc(bshard_deg),
            "R3_shortlist_hit_rate": route_acc_r3_shortlist_hit,
        },
        "e2e_acc": {
            "hard": _e2e_acc(bshard_hard, bval_hard), "soft": _e2e_acc(bshard_soft, bval_soft),
            "R3_M4": _e2e_acc(bshard_r3m4, bval_r3m4), "R3_M2": _e2e_acc(bshard_r3m2, bval_r3m2),
            "degenerate": _e2e_acc(bshard_deg, bval_deg),
        },
        "measured_candidates_r3": float(n_cand_r3.mean()),
        "rep_final": {
            "hard": (bshard_hard, bval_hard), "soft": (bshard_soft, bval_soft),
            "R3_M4": (bshard_r3m4, bval_r3m4), "R3_M2": (bshard_r3m2, bval_r3m2),
            "degenerate": (bshard_deg, bval_deg),
        },
    }


def run_sweep(mode: str) -> Dict:
    f_grid = E2E_F_GRID_SMOKE if mode == "smoke" else E2E_F_GRID_FULL
    seeds = E2E_SEEDS_SMOKE if mode == "smoke" else E2E_SEEDS_FULL
    Q = E2E_Q_SMOKE if mode == "smoke" else E2E_Q_FULL

    arm_names = ["hard", "soft", "R3_M4", "R3_M2", "degenerate"]
    curve = []
    rep_at_gate = None
    for f in f_grid:
        trials = [e2e_trial(f, s, Q) for s in seeds]
        row = {"f": f}
        for a in arm_names:
            row[f"route_acc_{a}_mean"] = float(np.mean([t["route_acc"][a] for t in trials]))
            row[f"e2e_acc_{a}_mean"] = float(np.mean([t["e2e_acc"][a] for t in trials]))
        row["route_acc_R3_shortlist_hit_mean"] = float(np.mean([t["route_acc"]["R3_shortlist_hit_rate"] for t in trials]))
        row["measured_candidates_r3_mean"] = float(np.mean([t["measured_candidates_r3"] for t in trials]))
        curve.append(row)
        if abs(f - E2E_GATE_F) < 1e-9:
            rep_at_gate = trials[0]["rep_final"]
        print(f"  [e2e f={f:.2f}] "
              f"route(hard={row['route_acc_hard_mean']:.3f} soft={row['route_acc_soft_mean']:.3f} "
              f"R3M4={row['route_acc_R3_M4_mean']:.3f} R3M2={row['route_acc_R3_M2_mean']:.3f} "
              f"deg={row['route_acc_degenerate_mean']:.3f}) "
              f"e2e(hard={row['e2e_acc_hard_mean']:.3f} soft={row['e2e_acc_soft_mean']:.3f} "
              f"R3M4={row['e2e_acc_R3_M4_mean']:.3f} R3M2={row['e2e_acc_R3_M2_mean']:.3f} "
              f"deg={row['e2e_acc_degenerate_mean']:.3f})", flush=True)

    gate_row = min(curve, key=lambda r: abs(r["f"] - E2E_GATE_F))
    if rep_at_gate is None:
        rep_at_gate = e2e_trial(E2E_GATE_F, seeds[0], Q)["rep_final"]

    # arms_differ (META_RULE_AF) at gate f: hash concat(shard,val) per arm
    digests = {}
    for a in arm_names:
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
# roundtrips + can-fail control + arms-differ, BEFORE any smoke/full).
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

    # 2. Address zero-corruption roundtrip (HARD/SOFT/REDUNDANT/DEGENERATE).
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

    # 3. DEGENERATE structural cap at ZERO corruption (product(moduli)=4 < n_shards=8).
    g4 = np.random.default_rng(3)
    deg_moduli, deg_dims = (4,), [36]
    deg_cb = build_channel_codebooks(deg_moduli, deg_dims, g4)
    deg_tbl = encode_channel_table(n_shards_t, deg_moduli, deg_dims, deg_cb)
    sl_deg, _ = decode_redundant_batch(deg_tbl, deg_moduli, deg_dims, deg_cb, n_shards_t, k_top=1, M=1)
    deg_acc = float((sl_deg[:, 0] == np.arange(n_shards_t)).mean())
    assert deg_acc <= 0.60, (  # 4/8 shards reachable at n_shards_t=8 test scale -> cap ~0.50
        f"DEGENERATE must be structurally capped even at ZERO corruption, got {deg_acc:.3f}")

    # 4. Stage-2 store construction + completion zero-corruption roundtrip
    #    (pred_shard = true_shard directly, isolating Stage-2 alone).
    n_shards_t2, N_WM_t, V_val_t, V_key_t, m_load_t = 4, 32, 8, 16, 4
    bundles_t, vals_t, keys_t, key_ids_t, val_ids_t = build_store(n_shards_t2, N_WM_t, V_val_t, V_key_t, m_load_t, seed=7)
    for sid in range(n_shards_t2):
        cue_key_t = keys_t[sid][key_ids_t[sid]]     # (m_load_t, N_WM_t) exact stored keys
        shortlist_t = np.full((m_load_t, 1), sid, dtype=np.int64)
        bshard_t, bval_t = complete_over_shortlist(shortlist_t, cue_key_t, bundles_t, vals_t)
        assert np.array_equal(bshard_t, np.full(m_load_t, sid))
        assert np.array_equal(bval_t, val_ids_t[sid]), f"Stage-2 must recover exact val ids at zero corruption, shard {sid}"

    # 5. Stage-2 completion over an M>1 shortlist (best-of-M picks the correct
    #    shard when it's IN the shortlist, at zero corruption).
    shortlist_m2 = np.stack([np.full(m_load_t, 0), np.full(m_load_t, sid)], axis=1)  # shard0 wrong, sid right, for sid>0
    for sid in range(1, n_shards_t2):
        cue_key_t = keys_t[sid][key_ids_t[sid]]
        sl = np.stack([np.full(m_load_t, 0), np.full(m_load_t, sid)], axis=1)
        bshard_t, bval_t = complete_over_shortlist(sl, cue_key_t, bundles_t, vals_t)
        assert np.array_equal(bshard_t, np.full(m_load_t, sid)), (
            f"best-of-M must pick the TRUE shard's higher completion confidence over a decoy, shard {sid}: {bshard_t}")

    # 6. Full e2e_trial at tiny scale, multiple f, NaN-free, real code path.
    for f_t in (0.0, 0.3, 0.7):
        r = e2e_trial(f=f_t, seed=101, Q=32)
        for a in ["hard", "soft", "R3_M4", "R3_M2", "degenerate"]:
            assert 0.0 <= r["route_acc"][a] <= 1.0 and not math.isnan(r["route_acc"][a]), f"{a} route_acc invalid at f={f_t}"
            assert 0.0 <= r["e2e_acc"][a] <= 1.0 and not math.isnan(r["e2e_acc"][a]), f"{a} e2e_acc invalid at f={f_t}"
            assert r["e2e_acc"][a] <= r["route_acc"][a] + 1e-9, f"{a} e2e_acc must never exceed route_acc at f={f_t}"

    # 7. At f=0 (clean cue, EXACT-KEY reference), HARD/SOFT/R3_M4 must reach
    #    (or be very near) ceiling e2e accuracy -- DEGENERATE must NOT (structural cap).
    r0 = e2e_trial(f=0.0, seed=7, Q=64)
    assert r0["e2e_acc"]["hard"] >= 0.90, f"HARD e2e acc at f=0 should be near-ceiling, got {r0['e2e_acc']['hard']:.3f}"
    assert r0["e2e_acc"]["soft"] >= 0.90, f"SOFT e2e acc at f=0 should be near-ceiling, got {r0['e2e_acc']['soft']:.3f}"
    assert r0["e2e_acc"]["R3_M4"] >= 0.90, f"R3_M4 e2e acc at f=0 should be near-ceiling, got {r0['e2e_acc']['R3_M4']:.3f}"
    assert r0["e2e_acc"]["degenerate"] < 0.90, "DEGENERATE must NOT reach ceiling even at zero corruption (structural cap)"

    print("[selftest] PASS: redundant_soft_shard_router_e2e_stage12_v1 (CRT roundtrip, "
          "address zero-corruption roundtrip x4 schemes, degenerate structural cap, "
          "Stage-2 store zero-corruption roundtrip, best-of-M shortlist completion, "
          "full e2e_trial real-code-path at f=0/0.3/0.7, ceiling check, nan-check)", flush=True)


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

    print("\n[e2e sweep] corruption-vs-e2e-accuracy, HARD/SOFT/R3_M4/R3_M2/DEGENERATE ...", flush=True)
    sw = run_sweep(RUN_MODE)
    gate_row = sw["gate_row"]

    # --- Gate D positive control (WITHIN TOLERANCE, see docstring) ---
    gate_d = {
        "hard_route_acc_measured": gate_row["route_acc_hard_mean"],
        "hard_route_acc_prior": _GATE_D_PRIOR["hard_route_acc"],
        "hard_within_tolerance": abs(gate_row["route_acc_hard_mean"] - _GATE_D_PRIOR["hard_route_acc"]) <= _GATE_D_TOLERANCE,
        "soft_route_acc_measured": gate_row["route_acc_soft_mean"],
        "soft_route_acc_prior": _GATE_D_PRIOR["soft_route_acc"],
        "soft_within_tolerance": abs(gate_row["route_acc_soft_mean"] - _GATE_D_PRIOR["soft_route_acc"]) <= _GATE_D_TOLERANCE,
        "r3_m4_shortlist_hit_measured": gate_row["route_acc_R3_shortlist_hit_mean"],
        "r3_m4_shortlist_hit_prior": _GATE_D_PRIOR["r3_m4_shortlist_hit"],
        "r3_within_tolerance": abs(gate_row["route_acc_R3_shortlist_hit_mean"] - _GATE_D_PRIOR["r3_m4_shortlist_hit"]) <= _GATE_D_TOLERANCE,
    }

    # --- baseline_in_band (META_RULE_AG) ---
    hard_e2e_gate = gate_row["e2e_acc_hard_mean"]
    soft_e2e_gate = gate_row["e2e_acc_soft_mean"]
    baseline_in_band = (0.05 < hard_e2e_gate < 0.95) and (0.05 < soft_e2e_gate < 0.95)

    # --- Cost accounting (honest M-factor) ---
    hard_route_cost = hard_route_cost_formula(E2E_N_BITS, E2E_DIMS_PER_BIT)
    soft_route_cost = soft_route_cost_formula(E2E_N_SHARDS, E2E_TOTAL_ADDR_DIM)
    measured_candidates_r3 = gate_row["measured_candidates_r3_mean"]
    r3_route_cost = redundant_route_cost_formula(E2E_MODULI_R3, E2E_DIMS_LIST_R3, E2E_K_TOP, measured_candidates_r3)

    e2e_cost_hard = hard_route_cost + 1 * E2E_V_VAL
    e2e_cost_soft = soft_route_cost + 1 * E2E_V_VAL
    e2e_cost_r3_m2 = r3_route_cost + 2 * E2E_V_VAL
    e2e_cost_r3_m4 = r3_route_cost + 4 * E2E_V_VAL

    acc_ref_soft = soft_e2e_gate
    acc_ref_hard = hard_e2e_gate

    def _config_verdict(acc_c: float, cost_c: float) -> Tuple[str, Dict]:
        acc_pass = acc_c >= E2E_ACC_PASS_FACTOR * acc_ref_soft
        acc_fail = acc_c <= acc_ref_hard
        cost_pass = cost_c <= E2E_COST_PASS_FACTOR * e2e_cost_soft
        cost_fail = cost_c >= E2E_COST_FAIL_FACTOR * e2e_cost_soft
        if acc_fail:
            v = "HARD_FAIL_ACC"
        elif cost_fail:
            v = "HARD_FAIL_COST"
        elif acc_pass and cost_pass:
            v = "HARD_PASS"
        else:
            v = "MIDDLE_BAND"
        return v, {"acc_pass": acc_pass, "acc_fail": acc_fail, "cost_pass": cost_pass, "cost_fail": cost_fail}

    r3m4_verdict, r3m4_detail = _config_verdict(gate_row["e2e_acc_R3_M4_mean"], e2e_cost_r3_m4)
    r3m2_verdict, r3m2_detail = _config_verdict(gate_row["e2e_acc_R3_M2_mean"], e2e_cost_r3_m2)

    can_fail_confirmed = bool(gate_row["e2e_acc_degenerate_mean"] < hard_e2e_gate - 0.05)

    if r3m4_verdict == "HARD_PASS":
        overall = "HARD_PASS"
        overall_msg = "E2E_CLOSES_GAP (CLAIM, VET-PENDING): R3_M4 end-to-end HARD_PASS (acc within band of SOFT, cost materially below SOFT)."
    elif r3m4_verdict in ("HARD_FAIL_ACC", "HARD_FAIL_COST"):
        overall = "HARD_FAIL"
        overall_msg = f"{r3m4_verdict}: R3_M4 end-to-end genuinely refuted."
    else:
        overall = "MIDDLE_BAND"
        overall_msg = "MEASURED_MECHANISM_MIXED (CLAIM, VET-PENDING): R3_M4 end-to-end lands on/inside the Pareto frontier of HARD/SOFT -- NOT framed as domination per CONTRACT."

    overall_msg += (
        f" | e2e_acc@f{E2E_GATE_F}: hard={hard_e2e_gate:.3f} soft={soft_e2e_gate:.3f} "
        f"R3_M4={gate_row['e2e_acc_R3_M4_mean']:.3f} R3_M2={gate_row['e2e_acc_R3_M2_mean']:.3f} "
        f"degenerate={gate_row['e2e_acc_degenerate_mean']:.3f}"
        f" | e2e_cost: hard={e2e_cost_hard:.1f} soft={e2e_cost_soft:.1f} "
        f"R3_M4={e2e_cost_r3_m4:.1f} (route={r3_route_cost:.1f}+M*V={4*E2E_V_VAL}) "
        f"R3_M2={e2e_cost_r3_m2:.1f} (route={r3_route_cost:.1f}+M*V={2*E2E_V_VAL})"
        f" | R3_M4 verdict={r3m4_verdict} {r3m4_detail} | R3_M2 verdict={r3m2_verdict} {r3m2_detail}"
        f" | can_fail_confirmed={can_fail_confirmed}"
        f" | gate_d_within_tolerance: hard={gate_d['hard_within_tolerance']} soft={gate_d['soft_within_tolerance']} r3={gate_d['r3_within_tolerance']}"
        f" | baseline_in_band={baseline_in_band}"
    )

    n_units = len(sw["config"]["f_grid"]) * len(sw["config"]["seeds"])
    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": overall,
        "verdict_msg": overall_msg,
        "summary": f"{overall}: true end-to-end fuzzy retrieval (REDUNDANT_SOFT route -> M-shortlist -> attractor completion) ({RUN_MODE})",
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
            "e2e_cost_R3_M2": e2e_cost_r3_m2, "e2e_cost_R3_M4": e2e_cost_r3_m4,
            "V_val": E2E_V_VAL,
        },
        "predictions": {"R3_M4_PRIMARY": r3m4_verdict, "R3_M2_companion": r3m2_verdict},
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
