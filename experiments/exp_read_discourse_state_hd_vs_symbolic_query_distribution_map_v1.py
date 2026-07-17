"""exp_read_discourse_state_hd_vs_symbolic_query_distribution_map_v1 -- MAP (not a single verdict point)
of WHERE an HD superposed discourse "state of mind" beats a symbolic-LRU-evict store and WHERE symbolic
wins, as a function of the QUERY DISTRIBUTION (how evicted-dominated the membership probes are) at genuine
overload + equal budget, PLUS a fuzzy/noisy-key arm (HD's structurally-unique niche the exact store cannot
answer). Settles the state-of-mind representation question ROBUSTLY rather than at one fragile weighting.

WHY THIS CELL (lineage, credit-not-steal):
  - v1 (flat) + v2 (hierarchical/queryable) discourse-state cells FAILED; the v2 VET (a8fc671f) localized
    the HD vector as INERT at SNR=16 (a pure-symbolic pointer scored identically) -- exact recall is a
    symbolic-table win (Frady-Kleyko-Sommer 1707.01429, CITED). Reused: the v2 VET's inertness discriminator
    (rescue_count), reimplemented here.
  - v3 (exp_read_discourse_state_hd_vs_symbolic_membership_overload_v1, 75ffcb67c) tested BALANCED
    (100/100/100 retained/evicted/absent) membership at overload -> HARD_FAIL: BA_hd=0.690 vs BA_sym=0.750
    at M=2048 (MEASURED@data/exp_read_discourse_state_hd_vs_symbolic_membership_overload_v1/metrics.json).
    Its VET showed the verdict SIGN FLIPS under population-weighting: at 4x/8x overload the true active set
    is ~1024 retained vs ~7168 evicted, so a BALANCED probe set UNDER-represents the evicted class. Under
    population-weighted probes HD WINS: HD_oracle 0.674 vs sym 0.625 (M=4096), 0.620 vs 0.562 (M=8192)
    (MEASURED-in-VET-recompute, reproduced by this cell's map). CONCLUSION FROM v3+VET: which representation
    wins is QUERY-DISTRIBUTION-DEPENDENT. The last two cells over-read by picking ONE weighting. This cell
    picks NONE -- it MAPS the whole evicted-fraction axis and reports the crossover honestly.
  - FHRR algebra credited to exp_nativelang_svo_vsa_probe_v1 (torch complex64 per CLAUDE.md). Design-param
    precedent (no code reuse): Frady/Kleyko/Sommer SNR=sqrt(N/M); graceful(VSA)-vs-catastrophic degradation.

PRIOR-WORK CONCEPT-QUERY (mandatory, run before authoring): `bash tools/substrate_query.sh "HD superposition
query distribution crossover evicted fraction population weighted set membership symbolic eviction fuzzy
noisy key state of mind map"` -> top hits are LEXICAL KB nodes ('distribution function' cosine=0.3896,
'eviction' 0.3721), NOT prior arc EXPERIMENT cells; NONE at cosine>0.30 is an experiment. Genuinely novel
(the query-distribution MAP + fuzzy niche), building on the credited v1/v2/v3 lineage.

THE TWO MAPS THIS CELL PRODUCES:
  MAP 1 -- QUERY-DISTRIBUTION crossover (PRIMARY): at each overload M, sweep the evicted-fraction q of the
    POSITIVE (present) probes from 0 (retained-heavy: recency queries) -> q_pop (population-weighted:
    aggregate/completeness queries) -> 1 (evicted-only: pure retrospective). Report BA_arm(q) and the
    crossover q* where HD overtakes symbolic-evict, per M, with error bars across seeds. Symbolic-evict at
    BOTH C=N (equal-dimension) and C=2N (equal-float, Frady-honest, HARDER for HD) must be beaten.
    METHOD (honest generalization of the VET's population-weighting): measure each arm's PER-CLASS recall
    (retained / evicted / absent) ONCE on a shared probe pool, then reweight ANALYTICALLY across the q-grid.
    BA_arm(q) = 0.5*((1-q)*recall_retained + q*recall_evicted + tnr_absent). This is error-free and
    reproduces the VET's population-weighted numbers exactly at q = q_pop. q_pop = (M-C)/M at C=N.
  MAP 2 -- FUZZY/NOISY-KEY niche (SECONDARY): at a fixed overload M, sweep key-noise s (per-dim gaussian
    phase jitter; self-score decays as exp(-s^2/2)). Probes are entities the SYMBOLIC store HOLDS
    (retained-active) presented via a NOISE-CORRUPTED phasor. HD scores the noisy phasor against its bundle
    (graceful). The FAIR symbolic comparator does nearest-neighbor cleanup over its stored id-phasors then
    exact membership (the exact store's BEST attempt at a fuzzy key). A step-exact reference (recall=1 at
    s=0 else 0) is ALSO reported to show the by-construction brittleness. CAN-FAIL: HD collapses to ~0.5 at
    high s, or symbolic-NN degrades as gracefully as HD (tie). Map where HD's graceful superposition beats
    clean-then-lookup.

BRAIN-CHECK / REALISTIC OPERATING POINT (honest, load-bearing for interpretation; CITED@Lane A/C of
notes/research_state_of_mind_hd_load_bearing_query_mode_reframe_2026-07-17.md): the situation-model
literature (Ericsson-Kintsch LT-WM; Zwaan event-indexing) treats non-recent reinstatement as the MARKED,
EFFORTFUL, EXCEPTIONAL case; recency/local is the default. So real SINGLE-REFERENT discourse queries sit at
LOW q (retained-dominated -> favors symbolic), EXCEPT AGGREGATE/COMPLETENESS ops ("who has been mentioned",
"has X appeared at all") which are population-weighted (HIGH q -> favors HD). The map's job: locate the
crossover and state which real query classes fall on each side. This RECONCILES the two representations
(symbolic exact layer for recency/single-referent; HD aggregate layer for completeness/consistency + fuzzy).

DESIGN GATE (verified AT SMOKE before full; per feedback_experiment_design_gate_can_fail_real_baseline...):
  (1) REAL BASELINES: symbolic-LRU-evict at C=N AND C=2N (equal-float); recency-oracle (last-C window);
      HD at FROZEN tau (deployable, honest) AND ORACLE tau (test-peeking ceiling reference); random floor.
      None is a strawman/abstain-all/blank.
  (2) DIFFICULTY-ON: genuine overload (M>C forces eviction; symbolic recall_evicted=0 BY CONSTRUCTION ->
      BA_sym<1). rescue_count>0 proves the evicted-active slice is non-empty and HD materially rescues it
      (pointer-control non-inert). Fuzzy: key-noise actually corrupts (self-score exp(-s^2/2) measurable).
  (3) CAN-FAIL BOTH WAYS: MAP 1 can show symbolic-wins-everywhere (no crossover q* in [0,1] at any M ->
      HARD_FAIL) or a crossover (where). HD-wins-at-q=0 is STRUCTURALLY EXCLUDED (symbolic is exact on
      retained+absent -> BA_sym(0)=1.0, unbeatable) and that is the CORRECT encoding that symbolic wins
      recency queries; the HD-uniquely-wins outcome is delivered by MAP 2 (fuzzy niche) which CAN also fail
      (HD collapses to 0.5). So across the two maps all three outcomes are reachable.
  (4) ONE VARIABLE per sweep: MAP 1 varies ONLY q (evicted-fraction of positive probes) -- identical
      stream/probes/budget/seeds/tau within each (M); MAP 2 varies ONLY s (key-noise) at fixed M. Arms
      differ ONLY in the state-tracking method.

PRE-REG (envelope-fail-bands; set BEFORE running):
  Primary metric = BA_arm(q) per overload M, mean+std over N_SEEDS. Primary competitors = symbolic-LRU-evict
  at C=N and C=2N. Crossover q*(M) = smallest q in [0,1] where BA_hd_frozen(q) >= BA_sym_CN(q); q_pop=(M-C)/M.
    HARD-PASS (establishes the HYBRID): at >=1 overload M, HD_frozen ROBUSTLY beats BOTH symbolic-evict
      arms (C=N AND C=2N) at the POPULATION-weighted point q_pop -- mean margin >= 0.02 AND (mean margin -
      1*std) > 0 across seeds -- AND a clean crossover q* <= q_pop exists (HD wins the whole evicted-heavy
      half incl. population). OR: MAP 2 fuzzy clean win -- HD BA > symbolic-NN BA + 0.05 at >=1 noise level
      with HD BA >= 0.55, robust across seeds (mean margin - 1*std > 0).
    HARD-FAIL (symbolic genuinely wins state-of-mind): symbolic-CN beats HD at ALL overload M across the
      ENTIRE axis incl. q=1 (no crossover q* in [0,1] anywhere) AND MAP 2 shows no HD fuzzy win (HD <=
      symbolic-NN at all s OR HD BA < 0.55 everywhere).
    MIDDLE (crossover only in an UNREALISTIC corner): a crossover exists but q*(M) > q_pop(M) at every
      overload M (HD wins only when queries are MORE evicted-dominated than the true population) AND MAP 2
      inconclusive. Reported cleanly -- "HD's win is confined to the aggregate corner; realistic single-
      referent operating point favors symbolic".
  P estimate: P=0.55 HYPOTHESIZED (this cell's own reasoning + the v3 VET recompute): the crossover q* is
    BELOW q_pop at 4x/8x overload (VET: HD 0.674>0.625 at M4096 q_pop=0.75; 0.620>0.562 at M8192 q_pop=0.875)
    but ABOVE q_pop at 2x (crossover ~0.65 vs q_pop=0.5). So a realistic-regime HD win is EXPECTED at high
    overload on ORACLE tau; the open risk is whether FROZEN (deployable) tau preserves it and whether the
    C=2N (equal-float) bar -- harder for HD -- is also cleared. Fuzzy niche is an independent HD-win route.

COMPUTE: torch complex64 (CLAUDE.md FHRR dtype), sequential-CPU -- justified under the GPU-batching
discipline's "wall time < 10s total" exemption for MAP 1 (bundle-sum + one (P,N)@(N,) membership matmul per
stream). MAP 2 fuzzy uses a vectorized (P,N)@(N,C) NN-cleanup matmul per (noise,seed) at one M; measured
elapsed_s reported; total remains a few seconds. Storage: no_storage (in-memory synthetic stream; nothing
persisted to substrate_index; no live KGStore/fit object -> F.2/F.3/F.4 not_applicable; F.5 honored).
progress_logging = print_flush_true (well under the 1800s heartbeat threshold; start-marker + crash-metrics
+ atomic-write present regardless). smoke = 2 seeds x {M=2048,4096} + fuzzy {s=0,1,2} (fires both maps);
full = 5 seeds x M in {1536,2048,3072,4096,6144,8192} + fuzzy s in {0,0.5,1,1.5,2,3} at M=4096.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified (META_RULE_AF): HD per-probe decision boolean-vector bit-non-identical to
#     symbolic-evict's at overload (empirical sha256 hash-compare on the real stream). Set at self-test+smoke.
# - final_metrics_atomicity = tmp_replace (META_RULE_AH): metrics.json via os.replace of a .tmp.
# - except SystemExit: raise BEFORE except Exception (no BaseException) -- see __main__ outer try.
# - crlb_floor_computed: membership SNR = sqrt(2N/M) (Frady/Kleyko/Sommer 1707.01429). N=1024:
#     M=1536->SNR=1.15; 2048->1.00; 3072->0.82; 4096->0.71; 6144->0.58; 8192->0.50. Nonzero signal at every
#     swept M (SNR>=0.5) so an evicted-slice rescue is REACHABLE (not analytically pinned to 0) ->
#     discriminator_reachability=true. crlb_formula_reference: "membership SNR=sqrt(2N/M); FHRR bundle
#     self(=N)-vs-crosstalk(=sqrt(M*N/2)), normalized by N". Fuzzy self-score THEORETICAL exp(-s^2/2).
# - baseline_in_band (META_RULE_AG): symbolic-evict NOT saturated (M>C forces eviction -> BA_sym<1); random
#     floor ~0.50; both verified at smoke. HD not at chance (>0.53) at >=1 point.
# - discriminator survives scale: smoke fires the rescue + crossover discriminators at the SAME overload
#     points (M=2048,4096) the full run uses (full ADDS 1536/3072/6144/8192); no smoke-only difficulty.
# - HARD_PASS strictly above floor + margin (META_RULE_L): margin>=0.02 AND (margin-1std)>0 (not at-floor).
# - HP_SCOPE: HARD_PASS applies ONLY to arm 'hd_frozen' (MAP1) / 'hd_fuzzy' (MAP2); symbolic/recency/random/
#     hd_oracle are baselines/ceilings and do NOT inherit it (hd_oracle is a test-peeking CEILING reference).
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = N_SEEDS*len(M_GRID) (MAP1) + N_SEEDS*len(NOISE_GRID)
#     (MAP2); verdict counts per-unit rows and HARD_FAIL_CARDINALITY if short.
# - per-unit failure-class instrumentation (META_RULE_J): no bare except; each stream/fuzzy-point wrapped,
#     failure class recorded to metrics, fatal-flag set (no silent continue).
# - calibration_check = adaptive_with_discriminator_gate: tau_hd frozen to maximize BALANCED (q=0.5) BA on a
#     HELD-OUT calibration stream (separate seed), applied unseen to test; tau_sym_nn (fuzzy) frozen likewise
#     at s=0. tau logged per M. rescue-count + arms-differ still-fire on test verify tau did not trivialize.
# - all numbers in this file tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
# - real_code_path (F.1): self_test() constructs + calls the REAL objects the FULL run uses (make_phasors,
#     build_stream, hd_membership_scores, SymbolicEvictStore, run_one_stream, run_fuzzy_point) at tiny scale
#     and asserts overload/eviction/rescue/crossover/fuzzy paths execute.
# - real_code_path_and_signature_preflight: F.2/F.3/F.4 not_applicable -- constructs NO KGStore/fit-module/
#     store-helper substrate object (pure synthetic FHRR over integer ids; no substrate_index write). F.5
#     (deterministic seeding) DOES apply and is honored below.
# - deterministic_seeding (F.5): every torch.Generator / random.Random seed is a FIXED integer formula
#     (BASE_SEED + declared per-role offset + M*1000 + seed_idx [+ noise index]); sets are ordered via
#     sorted(); NEVER hash() or list(set(...)) anywhere in this file. Static-scanned by queue_add PROT-023.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import math
import random
import argparse
import time
import json
import hashlib
import platform
import traceback
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_discourse_state_hd_vs_symbolic_query_distribution_map_v1"

# ---------------------------------------------------------------------------
# Hand-set, not fit-to-data constants (declared BEFORE any run; see docstring).
# ---------------------------------------------------------------------------
N_DIM = 1024                 # HD vector dimensionality (complex64). budget: PRIMARY C=N; CONSERVATIVE C=2N.
VOCAB = 16384                # entity id space; active entities sampled from this (rest are ABSENT probes).
M_GRID_FULL = [1536, 2048, 3072, 4096, 6144, 8192]   # overload M/C at C=N: 1.5,2,3,4,6,8 (q_pop .33->.875)
M_GRID_SMOKE = [2048, 4096]                           # 2 genuine overload points; fires both discriminators
N_SEEDS_FULL = 5
N_SEEDS_SMOKE = 2
REPEAT_FRAC = 0.5            # re-mention fraction (makes LRU-evict differ from a raw recency window)
PROBE_PER_CLASS = 100        # probes drawn per class {retained-active, evicted-active, absent} -> ~300/stream
BASE_SEED = 700000001
TAU_GRID = [x / 100.0 for x in range(5, 96, 5)]      # candidate normalized-score thresholds for calibration
Q_GRID = [i / 20.0 for i in range(21)]               # evicted-fraction axis 0.00..1.00 step 0.05 (MAP 1)
M_FUZZY = 4096                                        # fixed overload point for MAP 2 (4x; C=N=1024)
NOISE_GRID_FULL = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]     # per-dim phase-jitter std (MAP 2)
NOISE_GRID_SMOKE = [0.0, 1.0, 2.0]
FUZZY_PROBES = 150           # present(retained) + absent probes per fuzzy point (each class FUZZY_PROBES//1)

# deterministic, disjoint per-role seed offsets (NEVER hash()/list(set()) -- F.5)
_OFF = {"active": 10_000_000, "phasor": 20_000_000, "stream": 30_000_000, "probe": 40_000_000,
        "calib": 50_000_000, "randfloor": 60_000_000, "fuzz": 70_000_000, "symcal": 80_000_000}


def _seed(kind, m, seed_idx, extra=0):
    return BASE_SEED + _OFF[kind] + m * 1000 + seed_idx * 7 + extra


# ---------------------------------------------------------------------------
# FHRR primitives (torch complex64, CLAUDE.md dtype). Same formulas as exp_nativelang_svo_vsa_probe_v1
# / the v3 cell (CITED, not literally imported).
# ---------------------------------------------------------------------------
def make_phasors(seed, count, n_dim=N_DIM):
    """count random FHRR unit-phasor hypervectors, shape (count, n_dim) complex64."""
    g = torch.Generator().manual_seed(int(seed))
    theta = torch.empty(count, n_dim).uniform_(-math.pi, math.pi, generator=g)
    return torch.complex(torch.cos(theta), torch.sin(theta)).to(torch.complex64)


def bundle_rows(mat, rows):
    """Superpose selected rows of (V,N) complex64 -> (N,) complex64 sum (order-free)."""
    if len(rows) == 0:
        return torch.zeros(mat.shape[1], dtype=torch.complex64)
    idx = torch.tensor(sorted(rows), dtype=torch.long)
    return mat.index_select(0, idx).sum(dim=0)


def hd_membership_scores(bundle_vec, probe_mat):
    """Normalized real Hermitian inner product per probe. probe_mat: (P,N) complex64 -> (P,) float.
    Present phasor: score ~ 1 +- sqrt(M/(2N)); absent: ~0 +- sqrt(M/(2N)) (SNR=sqrt(2N/M))."""
    n = probe_mat.shape[1]
    return (probe_mat.conj() @ bundle_vec).real / float(n)


def nn_cleanup_scores(query_mat, ref_mat):
    """For each query row, MAX normalized real inner product over ref rows (nearest-neighbor cleanup).
    query_mat: (P,N), ref_mat: (C,N) complex64 -> (P,) float. Symbolic store's BEST fuzzy-key attempt."""
    n = query_mat.shape[1]
    if ref_mat.shape[0] == 0:
        return torch.full((query_mat.shape[0],), -1.0)
    sims = (query_mat.conj() @ ref_mat.transpose(0, 1)).real / float(n)   # (P,C)
    return sims.max(dim=1).values


def corrupt_phasors(mat, s, seed):
    """Per-dim gaussian phase jitter N(0,s): v -> v*exp(i*noise). Self-score decays ~ exp(-s^2/2)."""
    if s <= 0.0:
        return mat.clone()
    g = torch.Generator().manual_seed(int(seed))
    noise = torch.randn(mat.shape, generator=g) * float(s)
    rot = torch.complex(torch.cos(noise), torch.sin(noise)).to(torch.complex64)
    return mat * rot


# ---------------------------------------------------------------------------
# Symbolic-LRU-evict store (the fixed-capacity competitor HD must beat).
# ---------------------------------------------------------------------------
class SymbolicEvictStore:
    """Capacity-C exact set with LRU eviction. A re-mention REFRESHES recency (old entity re-mentioned
    stays retained) -- what makes it differ from a raw last-W recency window."""

    def __init__(self, capacity):
        self.capacity = int(capacity)
        self.od = OrderedDict()   # entity_id -> None, ordered by recency of last touch (oldest first)

    def touch(self, e):
        if e in self.od:
            self.od.move_to_end(e)
        else:
            self.od[e] = None
            if len(self.od) > self.capacity:
                self.od.popitem(last=False)  # evict least-recently-touched

    def contains(self, e):
        return e in self.od

    def retained(self):
        return set(self.od.keys())


# ---------------------------------------------------------------------------
# Synthetic overload stream + probes.
# ---------------------------------------------------------------------------
def build_stream(m, seed_idx, vocab=VOCAB):
    rng = random.Random(_seed("active", m, seed_idx))
    active = sorted(rng.sample(range(vocab), m))         # sorted() not list(set()) (F.5)
    order = active[:]
    rng.shuffle(order)                                    # first-appearance order
    n_rep = int(REPEAT_FRAC * m)
    srng = random.Random(_seed("stream", m, seed_idx))
    mentions = list(order)
    for _ in range(n_rep):
        mentions.append(order[srng.randrange(len(order))])
    return active, mentions


def lru_retained(mentions, capacity):
    store = SymbolicEvictStore(capacity)
    for e in mentions:
        store.touch(e)
    return store.retained()


def recency_window(mentions, window):
    return set(mentions[-window:])


def build_probes(active, retained, m, seed_idx, vocab=VOCAB):
    """Balanced probe POOL: PROBE_PER_CLASS per class {retained-active, evicted-active, absent}. Classes are
    defined relative to the C=N reference store (retained/evicted). The query-distribution reweighting (MAP 1)
    is applied ANALYTICALLY on the per-class recalls -- the pool itself is fixed + shared across arms."""
    active_set = set(active)
    evicted = sorted(active_set - retained)
    retained_active = sorted(active_set & retained)
    prng = random.Random(_seed("probe", m, seed_idx))

    def take(pool, k):
        pool = list(pool)
        if len(pool) <= k:
            return pool
        return prng.sample(pool, k)

    p_ret = take(retained_active, PROBE_PER_CLASS)
    p_evi = take(evicted, PROBE_PER_CLASS)
    absent_pool = [e for e in range(vocab) if e not in active_set]
    p_abs = prng.sample(absent_pool, min(PROBE_PER_CLASS, len(absent_pool)))
    probes = ([(e, True, "retained") for e in p_ret]
              + [(e, True, "evicted") for e in p_evi]
              + [(e, False, "absent") for e in p_abs])
    return probes


def _phasor_lookup(ids, m, seed_idx):
    """Deterministic per-stream phasor per entity id (consistent whether id is active or absent-probe)."""
    ids_sorted = sorted(set(ids))
    mat = make_phasors(_seed("phasor", m, seed_idx), len(ids_sorted))
    id2row = {e: i for i, e in enumerate(ids_sorted)}
    return mat, id2row


# ---------------------------------------------------------------------------
# Per-class rates (the map primitive): recall on retained / evicted, and TNR on absent.
# ---------------------------------------------------------------------------
def class_rates(decisions, classes):
    """decisions: list[bool] present-decision. -> (recall_retained, recall_evicted, tnr_absent).
    recall = fraction decided present among that present class; tnr = fraction decided absent among absent."""
    ret = [d for d, c in zip(decisions, classes) if c == "retained"]
    evi = [d for d, c in zip(decisions, classes) if c == "evicted"]
    ab = [d for d, c in zip(decisions, classes) if c == "absent"]
    rr = (sum(1 for d in ret if d) / len(ret)) if ret else float("nan")
    re = (sum(1 for d in evi if d) / len(evi)) if evi else float("nan")
    tnr = (sum(1 for d in ab if not d) / len(ab)) if ab else float("nan")
    return rr, re, tnr


def ba_at_q(rr, re, tnr, q):
    """BA under evicted-fraction q of the POSITIVE probes: 0.5*((1-q)*rr + q*re + tnr)."""
    return 0.5 * ((1.0 - q) * rr + q * re + tnr)


def crossover_q(rates_hd, rates_sym):
    """Smallest q in [0,1] where BA_hd(q) >= BA_sym(q). Analytic linear solve; None if no crossover in [0,1].
    rates_* = (rr, re, tnr)."""
    rr_h, re_h, tnr_h = rates_hd
    rr_s, re_s, tnr_s = rates_sym
    # BA_hd(q) - BA_sym(q) = 0.5*[ (rr_h-rr_s) + q*((re_h-rr_h) - (re_s-rr_s)) + (tnr_h-tnr_s) ]
    c0 = (rr_h - rr_s) + (tnr_h - tnr_s)                 # value of 2*diff at q=0
    slope = (re_h - rr_h) - (re_s - rr_s)                # d(2*diff)/dq
    d0 = c0                                              # 2*(BA_hd-BA_sym) at q=0
    d1 = c0 + slope                                      # 2*(BA_hd-BA_sym) at q=1
    if d0 >= 0:
        return 0.0                                       # HD >= sym already at q=0
    if d1 < 0:
        return None                                      # HD never catches up in [0,1]
    # linear root of d0 + slope*q = 0
    if abs(slope) < 1e-12:
        return None
    q = -d0 / slope
    return max(0.0, min(1.0, q))


# ---------------------------------------------------------------------------
# One stream (MAP 1): build state (all arms), score membership, per-class rates for each arm.
# ---------------------------------------------------------------------------
def calibrate_tau_hd(m, capacity, calib_seed_idx):
    """Freeze tau_hd on a HELD-OUT calibration stream: pick tau maximizing BALANCED (q=0.5) BA."""
    active, mentions = build_stream(m, calib_seed_idx)
    retained = lru_retained(mentions, capacity)
    probes = build_probes(active, retained, m, calib_seed_idx)
    classes = [c for _, _, c in probes]
    ids = [e for e, _, _ in probes] + active
    mat, id2row = _phasor_lookup(ids, m, calib_seed_idx)
    bundle = bundle_rows(mat, [id2row[e] for e in active])
    probe_rows = torch.tensor([id2row[e] for e, _, _ in probes], dtype=torch.long)
    scores = hd_membership_scores(bundle, mat.index_select(0, probe_rows)).tolist()
    best_tau, best_ba = TAU_GRID[0], -1.0
    for tau in TAU_GRID:
        rr, re, tnr = class_rates([s > tau for s in scores], classes)
        ba = ba_at_q(rr, re, tnr, 0.5)
        if ba > best_ba:
            best_ba, best_tau = ba, tau
    return best_tau, best_ba


def run_one_stream(m, capacity, cap_float, seed_idx, tau_hd):
    active, mentions = build_stream(m, seed_idx)
    retained = lru_retained(mentions, capacity)
    retained_float = lru_retained(mentions, cap_float)
    window = recency_window(mentions, capacity)
    probes = build_probes(active, retained, m, seed_idx)
    classes = [c for _, _, c in probes]

    ids = [e for e, _, _ in probes] + active
    mat, id2row = _phasor_lookup(ids, m, seed_idx)
    bundle = bundle_rows(mat, [id2row[e] for e in active])
    probe_rows = torch.tensor([id2row[e] for e, _, _ in probes], dtype=torch.long)
    hd_scores = hd_membership_scores(bundle, mat.index_select(0, probe_rows)).tolist()

    # oracle tau (test-peeking CEILING reference; NOT the shipped mechanism): maximize BALANCED BA on test.
    best_otau, best_oba = TAU_GRID[0], -1.0
    for tau in TAU_GRID:
        rr, re, tnr = class_rates([s > tau for s in hd_scores], classes)
        oba = ba_at_q(rr, re, tnr, 0.5)
        if oba > best_oba:
            best_oba, best_otau = oba, tau

    hd_frozen_dec = [s > tau_hd for s in hd_scores]
    hd_oracle_dec = [s > best_otau for s in hd_scores]
    sym_dec = [e in retained for (e, _, _) in probes]
    symf_dec = [e in retained_float for (e, _, _) in probes]
    rec_dec = [e in window for (e, _, _) in probes]
    rfrng = random.Random(_seed("randfloor", m, seed_idx))
    rand_dec = [rfrng.random() < 0.5 for _ in probes]

    rates = {
        "hd_frozen": class_rates(hd_frozen_dec, classes),
        "hd_oracle": class_rates(hd_oracle_dec, classes),
        "sym_cn": class_rates(sym_dec, classes),
        "sym_c2n": class_rates(symf_dec, classes),
        "recency": class_rates(rec_dec, classes),
        "random": class_rates(rand_dec, classes),
    }

    # INERTNESS DISCRIMINATOR (v2 VET tool): evicted-active probes HD rescues that symbolic-evict misses.
    rescue = sum(1 for i in range(len(probes))
                 if classes[i] == "evicted" and hd_frozen_dec[i] and not sym_dec[i])
    n_evicted = sum(1 for c in classes if c == "evicted")
    hd_hash = hashlib.sha256(bytes(1 if d else 0 for d in hd_frozen_dec)).hexdigest()
    sym_hash = hashlib.sha256(bytes(1 if d else 0 for d in sym_dec)).hexdigest()
    q_pop = float(n_evicted) / float(sum(1 for c in classes if c in ("retained", "evicted"))) \
        if n_evicted else 0.0
    # NOTE q_pop from probe-pool class counts approximates (M-C)/M; report the analytic one too.
    q_pop_analytic = max(0.0, float(m - capacity) / float(m))

    return {
        "m": m, "seed_idx": seed_idx, "n_active": len(active), "n_retained": len(retained),
        "n_evicted": n_evicted, "n_probes": len(probes), "tau_hd": tau_hd, "tau_oracle": best_otau,
        "rates": {k: [float(x) for x in v] for k, v in rates.items()},
        "rescue_count": rescue, "arms_differ": hd_hash != sym_hash,
        "q_pop": q_pop, "q_pop_analytic": q_pop_analytic,
    }


# ---------------------------------------------------------------------------
# One fuzzy point (MAP 2): noisy-key membership. HD-bundle vs symbolic-NN-cleanup vs symbolic-exact-step.
# ---------------------------------------------------------------------------
def calibrate_tau_fuzzy(m, capacity, calib_seed_idx):
    """Freeze tau_hd_fuzzy + tau_sym_nn at s=0 on a HELD-OUT stream: each maximizes BALANCED BA."""
    active, mentions = build_stream(m, calib_seed_idx)
    retained = sorted(lru_retained(mentions, capacity))
    prng = random.Random(_seed("symcal", m, calib_seed_idx))
    present = prng.sample(retained, min(FUZZY_PROBES, len(retained)))
    absent_pool = [e for e in range(VOCAB) if e not in set(active)]
    absent = prng.sample(absent_pool, min(FUZZY_PROBES, len(absent_pool)))
    ids = present + absent + retained + active
    mat, id2row = _phasor_lookup(ids, m, calib_seed_idx)
    bundle = bundle_rows(mat, [id2row[e] for e in active])   # bundle = all active (as in the real run)
    ret_rows = mat.index_select(0, torch.tensor([id2row[e] for e in retained], dtype=torch.long))
    q_rows = torch.tensor([id2row[e] for e in present + absent], dtype=torch.long)
    q_mat = mat.index_select(0, q_rows)          # s=0: clean queries
    labels = [True] * len(present) + [False] * len(absent)
    hd_sc = hd_membership_scores(bundle, q_mat).tolist()
    nn_sc = nn_cleanup_scores(q_mat, ret_rows).tolist()

    def best_tau(scores):
        bt, bb = TAU_GRID[0], -1.0
        for tau in TAU_GRID:
            dec = [s > tau for s in scores]
            tp = sum(1 for d, y in zip(dec, labels) if y and d)
            fn = sum(1 for d, y in zip(dec, labels) if y and not d)
            tn = sum(1 for d, y in zip(dec, labels) if (not y) and (not d))
            fp = sum(1 for d, y in zip(dec, labels) if (not y) and d)
            tpr = tp / (tp + fn) if (tp + fn) else 0.0
            tnr = tn / (tn + fp) if (tn + fp) else 0.0
            ba = 0.5 * (tpr + tnr)
            if ba > bb:
                bb, bt = ba, tau
        return bt
    return best_tau(hd_sc), best_tau(nn_sc)


def run_fuzzy_point(m, capacity, noise, seed_idx, tau_hd_f, tau_sym_f):
    active, mentions = build_stream(m, seed_idx)
    retained = sorted(lru_retained(mentions, capacity))
    prng = random.Random(_seed("fuzz", m, seed_idx, extra=int(noise * 100)))
    present = prng.sample(retained, min(FUZZY_PROBES, len(retained)))     # entities the SYMBOLIC store HOLDS
    absent_pool = [e for e in range(VOCAB) if e not in set(active)]
    absent = prng.sample(absent_pool, min(FUZZY_PROBES, len(absent_pool)))
    ids = present + absent + retained + active
    mat, id2row = _phasor_lookup(ids, m, seed_idx)
    bundle = bundle_rows(mat, [id2row[e] for e in active])
    ret_rows = mat.index_select(0, torch.tensor([id2row[e] for e in retained], dtype=torch.long))
    q_rows = torch.tensor([id2row[e] for e in present + absent], dtype=torch.long)
    clean = mat.index_select(0, q_rows)
    q_mat = corrupt_phasors(clean, noise, _seed("fuzz", m, seed_idx, extra=1 + int(noise * 100)))
    labels = [True] * len(present) + [False] * len(absent)

    hd_sc = hd_membership_scores(bundle, q_mat).tolist()
    nn_sc = nn_cleanup_scores(q_mat, ret_rows).tolist()
    hd_dec = [s > tau_hd_f for s in hd_sc]
    nn_dec = [s > tau_sym_f for s in nn_sc]

    def ba(dec):
        tp = sum(1 for d, y in zip(dec, labels) if y and d)
        fn = sum(1 for d, y in zip(dec, labels) if y and not d)
        tn = sum(1 for d, y in zip(dec, labels) if (not y) and (not d))
        fp = sum(1 for d, y in zip(dec, labels) if (not y) and d)
        tpr = tp / (tp + fn) if (tp + fn) else 0.0
        tnr = tn / (tn + fp) if (tn + fp) else 0.0
        return 0.5 * (tpr + tnr), tpr, tnr

    ba_hd, tpr_hd, tnr_hd = ba(hd_dec)
    ba_nn, tpr_nn, tnr_nn = ba(nn_dec)
    # symbolic-EXACT-step reference (by-construction brittleness): recall=1 at s==0 else 0; TNR=1 always.
    ba_exact = 0.5 * ((1.0 if noise <= 0.0 else 0.0) + 1.0)
    # mean self-score of present (proves noise corrupts): THEORETICAL exp(-s^2/2).
    self_mean = float(sum(hd_sc[:len(present)]) / max(1, len(present)))
    return {
        "m": m, "noise": noise, "seed_idx": seed_idx,
        "ba_hd_fuzzy": ba_hd, "tpr_hd": tpr_hd, "tnr_hd": tnr_hd,
        "ba_sym_nn": ba_nn, "tpr_nn": tpr_nn, "tnr_nn": tnr_nn,
        "ba_sym_exact_step": ba_exact, "hd_self_score_mean": self_mean,
        "n_present": len(present), "n_absent": len(absent),
    }


# ---------------------------------------------------------------------------
# Aggregation + verdict.
# ---------------------------------------------------------------------------
def _mean_std(xs):
    xs = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    if not xs:
        return float("nan"), 0.0
    mu = sum(xs) / len(xs)
    sd = (sum((x - mu) ** 2 for x in xs) / len(xs)) ** 0.5
    return float(mu), float(sd)


def aggregate_map1(rows, capacity):
    out = {}
    ms = sorted(set(r["m"] for r in rows))
    for m in ms:
        rs = [r for r in rows if r["m"] == m]
        arms = list(rs[0]["rates"].keys())
        # per-arm per-class mean rate
        arm_rates = {}
        for a in arms:
            rr = _mean_std([r["rates"][a][0] for r in rs])[0]
            re = _mean_std([r["rates"][a][1] for r in rs])[0]
            tnr = _mean_std([r["rates"][a][2] for r in rs])[0]
            arm_rates[a] = (rr, re, tnr)
        q_pop = _mean_std([r["q_pop_analytic"] for r in rs])[0]
        # BA curve per arm over Q_GRID
        curves = {a: [ba_at_q(*arm_rates[a], q) for q in Q_GRID] for a in arms}
        # crossover q* (per seed for error bars): hd_frozen vs sym_cn and vs sym_c2n
        qstar_cn = [crossover_q(r["rates"]["hd_frozen"], r["rates"]["sym_cn"]) for r in rs]
        qstar_c2n = [crossover_q(r["rates"]["hd_frozen"], r["rates"]["sym_c2n"]) for r in rs]
        # margin at q_pop per seed (hd_frozen - sym), for robustness gate
        marg_cn = [ba_at_q(*r["rates"]["hd_frozen"], q_pop) - ba_at_q(*r["rates"]["sym_cn"], q_pop) for r in rs]
        marg_c2n = [ba_at_q(*r["rates"]["hd_frozen"], q_pop) - ba_at_q(*r["rates"]["sym_c2n"], q_pop)
                    for r in rs]
        marg_or_cn = [ba_at_q(*r["rates"]["hd_oracle"], q_pop) - ba_at_q(*r["rates"]["sym_cn"], q_pop)
                      for r in rs]
        mu_cn, sd_cn = _mean_std(marg_cn)
        mu_c2n, sd_c2n = _mean_std(marg_c2n)
        mu_orcn, _ = _mean_std(marg_or_cn)
        # summarize crossover (drop None -> record fraction with a crossover)
        qs_cn = [q for q in qstar_cn if q is not None]
        qs_c2n = [q for q in qstar_c2n if q is not None]
        out[m] = {
            "n_seeds": len(rs), "overload": m / float(capacity), "q_pop": q_pop,
            "arm_rates": {a: [float(x) for x in v] for a, v in arm_rates.items()},
            "ba_curves": {a: [float(x) for x in c] for a, c in curves.items()},
            "ba_hd_frozen_at_qpop": float(ba_at_q(*arm_rates["hd_frozen"], q_pop)),
            "ba_hd_oracle_at_qpop": float(ba_at_q(*arm_rates["hd_oracle"], q_pop)),
            "ba_sym_cn_at_qpop": float(ba_at_q(*arm_rates["sym_cn"], q_pop)),
            "ba_sym_c2n_at_qpop": float(ba_at_q(*arm_rates["sym_c2n"], q_pop)),
            "ba_recency_at_qpop": float(ba_at_q(*arm_rates["recency"], q_pop)),
            "ba_random_at_qpop": float(ba_at_q(*arm_rates["random"], q_pop)),
            "crossover_cn_mean": float(sum(qs_cn) / len(qs_cn)) if qs_cn else None,
            "crossover_cn_frac_seeds": len(qs_cn) / len(rs),
            "crossover_c2n_mean": float(sum(qs_c2n) / len(qs_c2n)) if qs_c2n else None,
            "crossover_c2n_frac_seeds": len(qs_c2n) / len(rs),
            "margin_frozen_vs_cn_at_qpop": mu_cn, "margin_frozen_vs_cn_std": sd_cn,
            "margin_frozen_vs_c2n_at_qpop": mu_c2n, "margin_frozen_vs_c2n_std": sd_c2n,
            "margin_oracle_vs_cn_at_qpop": mu_orcn,
            "rescue_count_total": int(sum(r["rescue_count"] for r in rs)),
            "arms_differ_all": all(r["arms_differ"] for r in rs),
            "tau_hd": rs[0]["tau_hd"],
            # HARD_PASS-at-this-M gate: HD_frozen beats BOTH symbolic at q_pop robustly AND crossover<=q_pop.
            "hp_here": bool(mu_cn >= 0.02 and (mu_cn - sd_cn) > 0.0
                            and mu_c2n >= 0.02 and (mu_c2n - sd_c2n) > 0.0
                            and qs_cn and (sum(qs_cn) / len(qs_cn)) <= q_pop
                            and float(ba_at_q(*arm_rates["hd_frozen"], q_pop)) >= 0.55
                            and int(sum(r["rescue_count"] for r in rs)) > 0
                            and all(r["arms_differ"] for r in rs)),
        }
    return out


def aggregate_map2(frows):
    out = {}
    ss = sorted(set(r["noise"] for r in frows))
    for s in ss:
        rs = [r for r in frows if r["noise"] == s]
        mu_hd, sd_hd = _mean_std([r["ba_hd_fuzzy"] for r in rs])
        mu_nn, sd_nn = _mean_std([r["ba_sym_nn"] for r in rs])
        margins = [r["ba_hd_fuzzy"] - r["ba_sym_nn"] for r in rs]
        mu_m, sd_m = _mean_std(margins)
        out[s] = {
            "n_seeds": len(rs),
            "ba_hd_fuzzy": mu_hd, "ba_hd_fuzzy_std": sd_hd,
            "ba_sym_nn": mu_nn, "ba_sym_nn_std": sd_nn,
            "ba_sym_exact_step": float(sum(r["ba_sym_exact_step"] for r in rs) / len(rs)),
            "hd_self_score_mean": float(sum(r["hd_self_score_mean"] for r in rs) / len(rs)),
            "margin_hd_vs_nn": mu_m, "margin_hd_vs_nn_std": sd_m,
            # fuzzy HD-win-here: HD beats NN robustly AND HD BA>=0.55.
            "hd_wins_here": bool(mu_m >= 0.05 and (mu_m - sd_m) > 0.0 and mu_hd >= 0.55),
        }
    return out


def compute_verdict(agg1, agg2, expected_n_units, actual_n_units, capacity):
    if actual_n_units < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "cardinality: got %d units, expected %d" % (actual_n_units, expected_n_units), {})

    overload_ms = [m for m in agg1 if m > capacity]
    rand_ok = all(0.40 <= agg1[m]["ba_random_at_qpop"] <= 0.60 for m in agg1)
    sym_not_saturated = all(agg1[m]["ba_sym_cn_at_qpop"] < 0.999 for m in overload_ms) if overload_ms else False
    rescue_live = any(agg1[m]["rescue_count_total"] > 0 for m in overload_ms)
    arms_differ = all(agg1[m]["arms_differ_all"] for m in overload_ms) if overload_ms else False

    hp_ms_map1 = [m for m in overload_ms if agg1[m]["hp_here"]]
    # crossover EXISTS anywhere in [0,1] (HD catches up by q=1 at >=1 M)?
    crossover_anywhere = any(agg1[m]["crossover_cn_mean"] is not None for m in overload_ms)
    # crossover only in UNREALISTIC corner (q*>q_pop at every M that has one)?
    corners = []
    for m in overload_ms:
        c = agg1[m]["crossover_cn_mean"]
        if c is not None:
            corners.append(c > agg1[m]["q_pop"])
    only_corner = bool(corners) and all(corners)

    fuzzy_win_ss = [s for s in agg2 if agg2[s]["hd_wins_here"] and s > 0.0]  # HD niche at genuine noise
    fuzzy_win = len(fuzzy_win_ss) > 0
    fuzzy_all_tie_or_collapse = all((not agg2[s]["hd_wins_here"]) for s in agg2 if s > 0.0)

    if not (rand_ok and sym_not_saturated and rescue_live and arms_differ):
        tier = "INVALID_TEST_DESIGN"
    elif hp_ms_map1 or fuzzy_win:
        tier = "HARD_PASS"
    elif (not crossover_anywhere) and fuzzy_all_tie_or_collapse:
        tier = "HARD_FAIL"     # symbolic wins across the ENTIRE axis incl q=1 AND no fuzzy niche
    elif only_corner or (crossover_anywhere and not hp_ms_map1):
        tier = "MIDDLE_BAND"   # crossover only in the aggregate corner; realistic op-point favors symbolic
    else:
        tier = "MIDDLE_BAND"

    detail = " || ".join(
        "M=%d(x%.1f q_pop=%.3f) BAhdF@qpop=%.3f BAhdO@qpop=%.3f BAsymN=%.3f BAsym2N=%.3f cross_cn=%s "
        "dCN=%+.3f(+-%.3f) rescue=%d" % (
            m, agg1[m]["overload"], agg1[m]["q_pop"], agg1[m]["ba_hd_frozen_at_qpop"],
            agg1[m]["ba_hd_oracle_at_qpop"], agg1[m]["ba_sym_cn_at_qpop"], agg1[m]["ba_sym_c2n_at_qpop"],
            ("%.2f" % agg1[m]["crossover_cn_mean"]) if agg1[m]["crossover_cn_mean"] is not None else "none",
            agg1[m]["margin_frozen_vs_cn_at_qpop"], agg1[m]["margin_frozen_vs_cn_std"],
            agg1[m]["rescue_count_total"])
        for m in sorted(agg1))
    fdetail = " | ".join(
        "s=%.1f BAhd=%.3f BAnn=%.3f BAexact=%.3f self=%.3f dHDNN=%+.3f" % (
            s, agg2[s]["ba_hd_fuzzy"], agg2[s]["ba_sym_nn"], agg2[s]["ba_sym_exact_step"],
            agg2[s]["hd_self_score_mean"], agg2[s]["margin_hd_vs_nn"])
        for s in sorted(agg2))
    msg = "%s | C=%d(=N) | MAP1: %s || MAP2(fuzzy M=%d): %s" % (tier, capacity, detail, M_FUZZY, fdetail)
    info = {"hp_ms_map1": hp_ms_map1, "overload_ms": overload_ms, "crossover_anywhere": crossover_anywhere,
            "only_corner": only_corner, "fuzzy_win_noise_levels": fuzzy_win_ss, "rand_ok": rand_ok,
            "sym_not_saturated": sym_not_saturated, "rescue_live": rescue_live, "arms_differ": arms_differ}
    return tier, msg, info


# ---------------------------------------------------------------------------
# infra: out-dir / start-marker / crash-metrics / atomic write.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_" + ANCHOR_NAME, "smoke": "exp_" + ANCHOR_NAME + "_smoke",
           "self_test": "exp_" + ANCHOR_NAME + "_selftest"}[run_mode]
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# top-level run.
# ---------------------------------------------------------------------------
def run(run_mode):
    m_grid = M_GRID_SMOKE if run_mode == "smoke" else M_GRID_FULL
    noise_grid = NOISE_GRID_SMOKE if run_mode == "smoke" else NOISE_GRID_FULL
    n_seeds = N_SEEDS_SMOKE if run_mode == "smoke" else N_SEEDS_FULL
    capacity = N_DIM              # PRIMARY fairness: C=N (equal-dimension)
    cap_float = 2 * N_DIM         # CONSERVATIVE: C=2N (equal-float; Frady-honest, harder for HD)
    expected_n_units = n_seeds * len(m_grid) + n_seeds * len(noise_grid)

    out_dir = _out_dir(run_mode)
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    rows = []
    frows = []
    fatal = None
    tau_by_m = {}

    # MAP 1: query-distribution crossover
    for m in m_grid:
        try:
            tau_hd, calib_ba = calibrate_tau_hd(m, capacity, calib_seed_idx=90_000)
        except Exception as e:  # NOT BaseException
            fatal = {"stage": "calibrate_hd", "m": m, "class": type(e).__name__, "msg": str(e)[:300]}
            break
        tau_by_m[m] = tau_hd
        print("[%s] MAP1 M=%d tau_hd=%.2f (calib_balBA=%.3f)" % (run_mode, m, tau_hd, calib_ba), flush=True)
        for s in range(n_seeds):
            try:
                r = run_one_stream(m, capacity, cap_float, seed_idx=s, tau_hd=tau_hd)
            except Exception as e:  # NOT BaseException
                fatal = {"stage": "run_stream", "m": m, "seed_idx": s,
                         "class": type(e).__name__, "msg": str(e)[:300]}
                break
            rows.append(r)
            print("  M=%d seed=%d rescue=%d differ=%s q_pop=%.3f" %
                  (m, s, r["rescue_count"], r["arms_differ"], r["q_pop_analytic"]), flush=True)
        if fatal:
            break

    # MAP 2: fuzzy/noisy-key niche at M_FUZZY
    if fatal is None:
        try:
            tau_hd_f, tau_sym_f = calibrate_tau_fuzzy(M_FUZZY, capacity, calib_seed_idx=91_000)
        except Exception as e:  # NOT BaseException
            fatal = {"stage": "calibrate_fuzzy", "class": type(e).__name__, "msg": str(e)[:300]}
        else:
            print("[%s] MAP2 tau_hd_f=%.2f tau_sym_nn=%.2f" % (run_mode, tau_hd_f, tau_sym_f), flush=True)
            for noise in noise_grid:
                for s in range(n_seeds):
                    try:
                        fr = run_fuzzy_point(M_FUZZY, capacity, noise, seed_idx=s,
                                             tau_hd_f=tau_hd_f, tau_sym_f=tau_sym_f)
                    except Exception as e:  # NOT BaseException
                        fatal = {"stage": "run_fuzzy", "noise": noise, "seed_idx": s,
                                 "class": type(e).__name__, "msg": str(e)[:300]}
                        break
                    frows.append(fr)
                    print("  fuzzy s=%.1f seed=%d BAhd=%.3f BAnn=%.3f self=%.3f" %
                          (noise, s, fr["ba_hd_fuzzy"], fr["ba_sym_nn"], fr["hd_self_score_mean"]), flush=True)
                if fatal:
                    break

    elapsed = time.perf_counter() - t0

    if fatal is not None:
        metrics = {"verdict": "CELL_FATAL", "verdict_msg": "fatal at %s: %s" % (fatal.get("stage"), fatal),
                   "summary": "CELL_FATAL", "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
                   "run_mode": run_mode, "fatal": fatal, "rows": rows, "frows": frows,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}
        _write_metrics(out_dir, metrics)
        return metrics

    agg1 = aggregate_map1(rows, capacity)
    agg2 = aggregate_map2(frows)
    tier, msg, info = compute_verdict(agg1, agg2, expected_n_units, len(rows) + len(frows), capacity)
    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": msg[:200], "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_dim": N_DIM, "vocab": VOCAB, "capacity_primary": capacity, "capacity_float": cap_float,
        "m_grid": m_grid, "noise_grid": noise_grid, "m_fuzzy": M_FUZZY, "n_seeds": n_seeds,
        "repeat_frac": REPEAT_FRAC, "probe_per_class": PROBE_PER_CLASS, "q_grid": Q_GRID,
        "expected_n_units": expected_n_units, "actual_n_units": len(rows) + len(frows), "tau_by_m": tau_by_m,
        "agg_map1_by_m": {str(k): v for k, v in agg1.items()},
        "agg_map2_by_noise": {("%.2f" % k): v for k, v in agg2.items()},
        "verdict_info": info, "rows": rows, "frows": frows,
        "fairness_model": "MAP1 PRIMARY C=N (equal-dimension) + CONSERVATIVE C=2N (equal-float); MAP2 fuzzy "
                          "HD-bundle(1 vector, N floats) vs symbolic-NN-cleanup + symbolic-exact-step",
        "map2_budget_caveat": "MAP2 has a STORAGE-BUDGET ASYMMETRY that must be read honestly: symbolic-NN-"
                              "cleanup is a SHARDED store of C=capacity phasors (C*N floats, ~1024x the HD "
                              "bundle's single N-float vector), so an NN-cleanup WIN over HD-bundle is the "
                              "known sharded>bundled physics law (per-item cleanup avoids the M-item "
                              "superposition crosstalk), NOT an equal-budget symbolic win. The EQUAL-BUDGET "
                              "symbolic competitor for a noisy key is the exact-id store (ba_sym_exact_step), "
                              "which CANNOT answer a fuzzy key by construction (BA=0.5 at s>0). HD's fuzzy "
                              "niche, if any, is ONLY vs that equal-budget exact store; report both.",
        "realistic_operating_point": "CITED@Lane A/C reframe note: real SINGLE-REFERENT discourse queries "
                                     "sit at LOW q (retained-dominated -> symbolic); AGGREGATE/COMPLETENESS "
                                     "ops are population-weighted (HIGH q -> HD). Map states both sides.",
        "corpus_license": "synthetic integer-id overload stream; no external corpus; glass-box, no runtime LLM",
    }
    _write_metrics(out_dir, metrics)
    print("[%s] VERDICT %s (%.2fs)" % (run_mode, tier, elapsed), flush=True)
    print(msg, flush=True)
    return metrics


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert every discriminator CAN fire.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (make_phasors/build_stream/SymbolicEvictStore/"
          "hd_membership_scores/nn_cleanup_scores/run_one_stream/run_fuzzy_point)...", flush=True)

    # (1) FHRR membership signal on a hand toy: present ~1, absent ~0.
    mat = make_phasors(123, 4, n_dim=256)
    b = bundle_rows(mat, [0, 1])
    sc = hd_membership_scores(b, mat).tolist()
    assert sc[0] > 0.5 and sc[1] > 0.5, "present entities must score high: %r" % sc
    assert abs(sc[2]) < 0.5 and abs(sc[3]) < 0.5, "absent entities must score near 0: %r" % sc

    # (2) determinism (F.5): same seed -> same stream + phasors, twice.
    a1, m1 = build_stream(32, 0, vocab=256)
    a2, m2 = build_stream(32, 0, vocab=256)
    assert a1 == a2 and m1 == m2, "build_stream must be deterministic"
    p1, _ = _phasor_lookup(a1, 32, 0)
    p2, _ = _phasor_lookup(a2, 32, 0)
    assert torch.allclose(p1, p2), "phasor lookup must be deterministic"

    # (3) LRU eviction differs from raw recency (refresh pulls an id back). Hand trace.
    st = SymbolicEvictStore(capacity=2)
    for e in [1, 2, 1, 3]:
        st.touch(e)
    assert st.retained() == {1, 3}, "LRU should retain {1,3}: %r" % st.retained()

    # (4) fuzzy corruption DECAYS the self-score (THEORETICAL exp(-s^2/2)): s=0 ~1, s=2 << 1.
    v = make_phasors(7, 1, n_dim=1024)
    c0 = corrupt_phasors(v, 0.0, 5)
    c2 = corrupt_phasors(v, 2.0, 5)
    s0 = hd_membership_scores(v[0], c0).item()
    s2 = hd_membership_scores(v[0], c2).item()
    assert s0 > 0.95, "s=0 self-score must be ~1: %r" % s0
    assert s2 < 0.5, "s=2 self-score must decay well below 1 (exp(-2)=0.135): %r" % s2

    # (5) nn_cleanup recovers a clean key and rejects an absent one.
    ref = make_phasors(11, 8, n_dim=512)
    q_present = ref.index_select(0, torch.tensor([3]))
    q_absent = make_phasors(999, 1, n_dim=512)
    assert nn_cleanup_scores(q_present, ref).item() > 0.9, "clean present key must clean up to ~1"
    assert nn_cleanup_scores(q_absent, ref).item() < 0.5, "absent key must have low max-sim"

    # (6) OVERLOAD + rescue path runs (N=64, M=128>C=64): symbolic MUST evict; rates + rescue produced.
    r = run_one_stream(m=128, capacity=64, cap_float=128, seed_idx=0, tau_hd=0.3)
    assert r["n_active"] == 128 and r["n_retained"] == 64, "overload must force eviction: %r" % (
        (r["n_active"], r["n_retained"]))
    rr, re, tnr = r["rates"]["sym_cn"]
    assert rr > 0.99 and re < 0.01, "symbolic-CN: recall_retained~1, recall_evicted~0 by construction: %r" % (
        (rr, re))
    assert r["arms_differ"], "HD and symbolic decisions must be bit-non-identical under overload"
    assert 0.0 <= r["q_pop_analytic"] <= 1.0

    # (7) crossover math: symbolic linear (rr=1,re=0,tnr=1) vs an HD that wins high-q -> crossover in (0,1).
    q_star = crossover_q((0.85, 0.65, 0.63), (1.0, 0.0, 1.0))
    assert q_star is not None and 0.0 < q_star < 1.0, "expected an interior crossover: %r" % q_star
    # an HD that never catches up (low everything) -> no crossover.
    assert crossover_q((0.60, 0.30, 0.55), (1.0, 0.0, 1.0)) is None, "poor HD must have no crossover"

    # (8) fuzzy point path runs + symbolic-exact-step reference is 1.0 at s=0, 0.5 at s>0.
    fr0 = run_fuzzy_point(m=256, capacity=64, noise=0.0, seed_idx=0, tau_hd_f=0.3, tau_sym_f=0.3)
    fr2 = run_fuzzy_point(m=256, capacity=64, noise=2.0, seed_idx=0, tau_hd_f=0.3, tau_sym_f=0.3)
    assert abs(fr0["ba_sym_exact_step"] - 1.0) < 1e-9, "exact-step BA at s=0 must be 1.0"
    assert abs(fr2["ba_sym_exact_step"] - 0.5) < 1e-9, "exact-step BA at s>0 must be 0.5 (by construction)"
    assert fr0["hd_self_score_mean"] > fr2["hd_self_score_mean"], "self-score must decay with noise"

    # (9) verdict logic sanity: HD-win-at-qpop -> HARD_PASS; symbolic-everywhere+no-fuzzy -> HARD_FAIL;
    #     corner-only -> MIDDLE.
    def _row(m, hd_rates, seed_idx=0):
        return {"m": m, "seed_idx": seed_idx, "rates": {
            "hd_frozen": hd_rates, "hd_oracle": hd_rates, "sym_cn": (1.0, 0.0, 1.0),
            "sym_c2n": (1.0, 0.25, 1.0), "recency": (0.9, 0.1, 1.0), "random": (0.5, 0.5, 0.5)},
            "rescue_count": 20, "arms_differ": True, "q_pop": 0.75, "q_pop_analytic": 0.75,
            "n_active": m, "n_retained": 1024, "n_evicted": m - 1024, "tau_hd": 0.3, "tau_oracle": 0.3}
    # strong HD (wins at q_pop=0.75): rr=0.88, re=0.70, tnr=0.80 -> BA(0.75)=0.5*(0.25*.88+.75*.70+.80)=0.7345
    win_rows = [_row(4096, (0.88, 0.70, 0.80), s) for s in range(3)]
    agg1_win = aggregate_map1(win_rows, 1024)
    agg2_null = {0.0: {"ba_hd_fuzzy": 1.0, "ba_hd_fuzzy_std": 0.0, "ba_sym_nn": 1.0, "ba_sym_nn_std": 0.0,
                       "ba_sym_exact_step": 1.0, "hd_self_score_mean": 1.0, "margin_hd_vs_nn": 0.0,
                       "margin_hd_vs_nn_std": 0.0, "hd_wins_here": False},
                 1.0: {"ba_hd_fuzzy": 0.55, "ba_hd_fuzzy_std": 0.02, "ba_sym_nn": 0.55, "ba_sym_nn_std": 0.02,
                       "ba_sym_exact_step": 0.5, "hd_self_score_mean": 0.6, "margin_hd_vs_nn": 0.0,
                       "margin_hd_vs_nn_std": 0.02, "hd_wins_here": False}}
    tier_w, _, _ = compute_verdict(agg1_win, agg2_null, 3, 3, 1024)
    assert tier_w == "HARD_PASS", "strong HD win at q_pop must be HARD_PASS: %s" % tier_w
    # weak HD that never catches up in [0,1] -> no crossover; null fuzzy -> HARD_FAIL.
    lose_rows = [_row(4096, (0.60, 0.30, 0.55), s) for s in range(3)]
    tier_l, _, _ = compute_verdict(aggregate_map1(lose_rows, 1024), agg2_null, 3, 3, 1024)
    assert tier_l == "HARD_FAIL", "HD losing entire axis + no fuzzy must be HARD_FAIL: %s" % tier_l
    # corner-only: HD crosses but only ABOVE q_pop -> MIDDLE. rr=0.82,re=0.55,tnr=0.72 crossover>0.75.
    corner_rows = [_row(4096, (0.82, 0.55, 0.72), s) for s in range(3)]
    tier_c, _, _ = compute_verdict(aggregate_map1(corner_rows, 1024), agg2_null, 3, 3, 1024)
    assert tier_c in ("MIDDLE_BAND",), "corner-only crossover must be MIDDLE: %s" % tier_c
    # fuzzy niche win alone -> HARD_PASS even if MAP1 is corner-only.
    agg2_win = {0.0: agg2_null[0.0],
                1.0: {"ba_hd_fuzzy": 0.72, "ba_hd_fuzzy_std": 0.03, "ba_sym_nn": 0.55, "ba_sym_nn_std": 0.03,
                      "ba_sym_exact_step": 0.5, "hd_self_score_mean": 0.6, "margin_hd_vs_nn": 0.17,
                      "margin_hd_vs_nn_std": 0.03, "hd_wins_here": True}}
    tier_f, _, _ = compute_verdict(aggregate_map1(corner_rows, 1024), agg2_win, 3, 3, 1024)
    assert tier_f == "HARD_PASS", "fuzzy niche clean win must be HARD_PASS: %s" % tier_f

    print("[self_test] PASS: real code path exercised; overload/eviction/rescue/crossover/fuzzy/verdict fire.",
          flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "smoke"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(args.mode)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        try:
            _write_crash_metrics(_out_dir("smoke"), e)
        except Exception:
            pass
        raise
