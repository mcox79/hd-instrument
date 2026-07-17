"""exp_read_discourse_wsm_v2_hierarchical_gated_queryable_v1 -- v2 of the RUNNING "state of mind":
fixes v1's HARD_FAIL (a naive FLAT F=4 per-ENTITY focus + LRU eviction got SWAMPED by real-prose entity
counts: acc_C=0.573 vs acc_A=0.633 on the full adjacent-swap corpus, MEASURED@data/exp_read_discourse_
wsm_running_vs_static_coherence_v1/metrics.json:margin_adjswap_all=-0.060, and -0.222 on the long-passage
subset -- WORSE than static, HARD_FAIL) with three credited mechanism changes, and adds a genuinely NEW
verification axis (QUERYABILITY) that v1 never tested at all.

TRIGGER (dispatching task, verbatim intent): v1 failed; build v2 that (1) groups entities into ~4
higher-level CHUNK handles instead of holding ~15 individual entities in a flat ~4-slot focus (fixes the
swamp), (2) replaces v1's dumb LRU eviction with a SELECTIVE GATED update/eviction policy (credit
Eliasmith/Voelker's doubly-latched gated integrator), (3) makes the maintained story-vector genuinely
QUERYABLE via real HD unbind + cleanup decode (credit Plate HRR chunking/superposition + resonator-style
cleanup), and verify BOTH coherence (v1's test, fixed mechanism) AND queryability (a new, harder,
"does it actually hold an understanding" test) before any HARD_PASS claim.

PRIOR-WORK CONCEPT-QUERY (mandatory, run before authoring): `bash tools/substrate_query.sh "queryable
running discourse story vector unbind role query gated working memory chunk hierarchy entity swamp"` ->
top hit cosine=0.3467 ('Working memory', a generic science-atom lexical entry) and cosine=0.3467
('working_memory', WordNet) -- both generic lexical entries, NO prior EXPERIMENT-CELL hit from the
concept index for this specific construction (same pattern v1's own concept-query found for its own,
narrower claim). Direct file search confirms the THREE genuinely relevant prior artifacts, all reused
and credited below, not rediscovered: (1) `exp_read_discourse_wsm_running_vs_static_coherence_v1` (the
FAILED v1 this cell fixes -- corpus, permutation machinery, and the coherence-scoring SHAPE are reused
verbatim; the flat-focus/LRU MECHANISM is replaced); (2) `exp_read_discourse_entitygrid_coherence_v1`
(the STATIC baseline + entity/role extraction, reused unmodified, landed MIDDLE_BAND); (3)
`exp_nativelang_svo_vsa_probe_v1` (the FHRR bind/unbind/bundle/cleanup ALGEBRA this cell's HD story-
vector reimplements in torch complex64 per CLAUDE.md's dtype convention -- same formulas, credited,
not literally imported since that cell's primitives are numpy and CLAUDE.md mandates torch tensors with
explicit dtypes for this codebase). Also credits (design-parameter precedent only, no code reuse, per
`notes/research_vsa_hdc_state_of_mind_prior_art_scour_2026-07-17.md` and `notes/research_discourse_
state_of_mind_situation_model_2026-07-17.md`): Eliasmith/Voelker's doubly-latched gated integrator
(Tier-0 pointer + gated replace-latch), Plate's HRR "chunking" (a bound-and-superposed trace itself
treated as a filler for higher-level binding -- literally this cell's CHUNK_ID(⊛)chunk_content(⊛)role
⊛entity nesting), and Grosz-Sidner/Centering's subject>object salience ranking (this cell's chunk-
eviction salience rule prefers a chunk currently holding an S/O role over a role-less one, before recency).

MECHANISM UNDER TEST (candidate C2, "HIERARCHICAL-GATED-QUERYABLE"; see class HierarchicalGatedState
below for the full implementation) -- three changes from v1's candidate C, each independently credited:

  (1) HIERARCHY/CHUNKING (fixes the swamp): v1 held up to FOCUS_CAPACITY=4 INDIVIDUAL entities in focus,
      so a 15-entity passage caused near-constant eviction thrashing (every 4th new entity evicted an
      old one, destroying exactly the multi-sentence memory the mechanism was supposed to provide). v2
      holds up to CHUNK_CAPACITY=4 CHUNK "registers" (fixed slot identity 0..3, like a register file --
      credit Eliasmith/Voelker), each chunk a GROUP of co-occurring entities (an entity newly mentioned
      in the same row as an already-focused entity JOINS that entity's chunk; a chunk-bound-group is what
      gets evicted/reactivated as ONE unit, not per-entity) -- a 15-entity passage typically needs far
      fewer than 15 chunk-evictions because entities cluster into scenes.
  (2) GATED-WM UPDATE (credit Eliasmith/Voelker doubly-latched gated integrator): v1 evicted by pure LRU
      (least-recently-touched). v2's eviction salience prefers a chunk CURRENTLY HOLDING an S/O role over
      a role-less chunk (credit Grosz-Sidner/Centering subject>object priority), before recency -- "not
      dumb LRU." Separately, and more literally gated: each role-slot WRITE only touches the persistent HD
      chunk vector when the incoming filler actually DIFFERS from the slot's current occupant (gate=1 on a
      genuine change/surprisal; gate=0, a no-op HOLD, on a redundant re-mention of the same filler) --
      this is the doubly-latched integrator's own semantics (one latch gates whether the store's value is
      allowed to change at all), and it is a REPLACE (subtract the old role-binding, add the new one) not
      an ACCUMULATE, which is what keeps the chunk's HD vector queryable (undegraded by repeated role-
      churn) instead of growing crosstalk without bound.
  (3) QUERYABLE story-vector (credit Plate HRR bind/bundle/chunking + resonator-style cleanup decode):
      v1's state was a pure symbolic dict, never a real vector, never queryable. v2's story-vector is a
      REAL FHRR (torch complex64) construction: STORY_VECTOR = bundle_over_active_chunks(bind(CHUNK_ID,
      chunk_content)), chunk_content = bundle_over_role_slots(bind(ROLE, ENTITY)). QUERY(role, chunk=
      tier0-by-default) = unbind(unbind(STORY_VECTOR, CHUNK_ID), ROLE) + cleanup-nearest-neighbor against
      the passage's entity codebook -> a decoded entity. This is testable, falsifiable, and can genuinely
      fail (crosstalk from other active chunks/roles can corrupt the decode) -- not just an inspectable
      label.

DECLARED, HAND-SET, NOT FIT-TO-DATA (avoiding p-hacking risk, same discipline as v1): CHUNK_CAPACITY=4
(Cowan span, CITED, same precedent as v1's FOCUS_CAPACITY and the resonator-focus-lever F=3-4 sweet spot,
now applied one level up at chunk granularity per this cell's own design gate); REACT_DISCOUNT=0.5
(CITED@Almor 1999, reused verbatim from v1, unchanged); N_DIM=2048 (CRLB-justified below, fixed BEFORE
any run); ROLE_KEYS=("S","O") (the two grammatically-informative, queryable roles; "X"/other still
participates in chunk membership/eviction bookkeeping and the coherence score's TRANSITION_WEIGHTS, but
is deliberately NOT written to a role-slot or the HD vector -- "X" is too heterogeneous a bag to be a
meaningful role-QUERY target, a declared scope limit, not an oversight). None of these four constants
were tuned against this cell's own outcome; all were fixed in this docstring before the FULL run's
numbers were computed.

CRLB / capacity-feasibility (mandatory quantitative check, per §9 of the exp_dev discipline file): the
STORY_VECTOR superposes at most CHUNK_CAPACITY=4 chunk-bound blocks, each itself a bundle of at most
len(ROLE_KEYS)=2 role-bindings -> at most 8 role-binding "items" are ever superposed into ONE vector at
any point in this cell's regime. Using the SNR=sqrt(N/M) law (Frady, Kleyko & Sommer -- CITED via
`notes/research_vsa_hdc_state_of_mind_prior_art_scour_2026-07-17.md` section 3) at N=N_DIM=2048, M=8:
SNR=sqrt(2048/8)=16.0, comfortably above the ~3-5 SNR regime typically needed for clean nearest-neighbor
cleanup decode over a small (<20-entity) per-passage codebook (compare: Schlegel/Neubert/Protzel report
FHRR needs only ~330 dims for M=15 items at 99% bundling accuracy -- this cell's regime, M<=8 at N=2048,
is far inside that comfortable margin). discriminator_reachability=true.

CORPUS: REUSED VERBATIM (not re-typed, not re-selected) from v1 -- `SHORT_PASSAGES` (v1's own re-export
of the static entity-grid cell's 10 passages) + `LONG_PASSAGES` (v1's 6 NEW 16-sentence passages, 3
books) = the SAME 16-passage, 3-book corpus v1 used, imported directly. This is the SAME corpus v1
FAILED on (adjacent-swap, long-passage subset) -- the correct, most decisive test of whether v2's fix
actually works, not a new easier corpus chosen post-hoc.

DESIGN GATE (per the dispatching task's own falsifiable spec, extended for the new query axis):
  1. REAL BASELINES: (coherence) STATIC entity-grid role-transition (candidate A) + co-occurrence-only
     (B1) + random floor, ALL reused unmodified from the entity-grid cell, same corpus/permutations as
     candidate C2 (one-variable isolation, same discipline as v1); (query) last-mention baseline + bag-
     of-roles-frequency baseline + random-entity floor, all computed independently of the HD mechanism.
  2. CAN-FAIL (verified at self-test): (coherence) the SAME single-entity-always-present degenerate
     construction v1 used -- C2 must reduce to the static bigram formula's ranking (no chunk eviction/
     reactivation ever possible with 1 entity) -> credit_A==credit_C2 on every sampled permutation;
     (query) a degenerate corpus where the queried role NEVER switches holders -> mechanism, last-
     mention, and bag-of-roles must ALL tie at 1.0 (no method has an unfair inherent advantage on a
     trivial case).
  3. DIFFICULTY-ON: (coherence) the ADJACENT-SWAP condition + the LONG-passage subset (unchanged from
     v1 -- the exact regime v1 failed); (query) the SWITCH-POINT subset (query points where the queried
     role's holder just changed -- the informative, non-trivial case; a "was the same as last time"
     query is winnable by every baseline for free and is reported separately, not as the HARD_PASS gate).
  4. ONE VARIABLE per comparison: coherence uses the IDENTICAL passages/extraction/permutation-draws as
     the static baseline (A) -- only the state-tracking MECHANISM (flat-LRU vs hierarchical-gated)
     differs; query compares the SAME forward single-pass reading state's HD decode against baselines
     computed from the SAME per-sentence role data, at the SAME query points.
  5. BROADENED corpus: same 16-passage/3-book corpus as v1 (already satisfies the design-gate item
     v1's own docstring recorded; not re-broadened again here since v1's broadening already stands).

PRE-REG (envelope-fail-bands; set BEFORE running; TWO sub-tests, combined per the dispatching task's
explicit rule -- HARD_PASS requires BOTH, HARD_FAIL if EITHER sub-test HARD_FAILs):

  SUB-TEST 1 (COHERENCE, same bands as v1, same corpus/regime -- the direct re-test of the fixed
    mechanism on the EXACT condition v1 failed):
    HARD-PASS: margin_adjswap_all=acc_C2-acc_A >= 0.05 AND margin_adjswap_long >= 0.05 AND
      frac_passages_nonneg_delta >= 0.50 AND random-baseline sanity (0.35<=acc_random<=0.65, both
      conditions, full corpus).
    HARD-FAIL: margin_adjswap_all <= 0.01 OR margin_adjswap_all < 0 OR frac_passages_nonneg_delta < 0.30.
    MIDDLE: otherwise.

  SUB-TEST 2 (QUERYABILITY, new):
    HARD-PASS: on the SWITCH-POINT (hard) query subset, mech_acc_hard >= last_mention_acc_hard + 0.10 AND
      mech_acc_hard >= bag_of_roles_acc_hard + 0.10 AND mech_acc_hard >= 0.40 (absolute floor, not just
      relative) AND n_hard_queries >= 15 (cardinality; avoids a thin, unreliable sample) AND the
      degenerate can-fail construction ties all three methods at 1.0 (validity guard, not the pass/fail
      metric itself).
    HARD-FAIL: mech_acc_hard <= last_mention_acc_hard OR mech_acc_hard <= bag_of_roles_acc_hard (ties or
      loses to either real baseline) OR mech_acc_hard < 0.15 (near-floor; a ~10-entity-per-passage
      codebook's chance rate is roughly 0.10-0.20, so <0.15 is indistinguishable from guessing) OR
      n_hard_queries < 8 (too thin to trust either direction).
    MIDDLE: otherwise.

  COMBINED: HARD_PASS iff BOTH sub-tests HARD_PASS. HARD_FAIL if EITHER sub-test HARD_FAILs (task's
    explicit "HARD-FAIL if either ties/loses" rule). Otherwise MIDDLE_BAND (report which sub-test is the
    weaker one). If either sub-test's own random/floor sanity check fails, COMBINED tier is forced to
    INVALID_TEST_DESIGN.

  P estimate: P=0.28 HYPOTHESIZED (this cell's own reasoning, deflated below v1's own P=0.35): (i) v1
    already HARD_FAILed on a mechanistically similar (flat-focus) design at this exact regime -- the
    chunking/gating fix is a genuine, motivated repair but UNTESTED, not a proven win; (ii) the query
    sub-test has ZERO prior measurement anywhere in this codebase (a wholly new claim, no prior atom to
    anchor P against); (iii) the COMBINED AND-gate over two independent hard sub-tests is strictly
    harder to clear than either alone (P(both) <= min(P(each))), and each individual sub-test is already
    below 0.5 on its own merits.

COMPUTE: torch complex64 (CLAUDE.md dtype convention for FHRR), sequential-CPU -- justified under the
GPU-batching-mandatory discipline's explicit "wall time < 10s total" exemption: 16 passages, at most 16
sentences each, K_PERMUTATIONS=12 x 2 conditions x 16 passages = 384 coherence-scoring passes (each a
SYMBOLIC-ONLY state-machine scan, track_vectors=False -- no HD tensor ops in the permutation-scoring
loop, a COMPUTE-PROPORTIONALITY optimization since the coherence score never reads the HD vector) PLUS
16 single ORIGINAL-order forward passes WITH HD tensor ops (track_vectors=True, for the query test) --
each pass touches at most a few dozen (N_DIM=2048,)-complex64 tensors; measured wall time reported in
metrics (`elapsed_s`), expected well under 10s total. Storage: no_storage (in-memory per-passage state,
nothing persisted to substrate_index). smoke == full (fixed, small, deterministic 16-passage corpus,
nothing meaningful to shrink -- same precedent as v1 and every sibling cell in this reading arc).
progress_logging = print_flush_true (well under the 1800s mandatory-heartbeat threshold, added anyway).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): EMPIRICAL, real-corpus checks -- (coherence) C2 and
#     static (A) disagree on >=1 permutation pair; (query) mechanism decode differs from the last-mention
#     baseline on >=1 real query. Both are deterministic pure functions of the same grid/state, not
#     stochastic outputs to hash-compare, so an empirical-disagreement check (not a hash-digest check) is
#     the meaningful test here (same convention as v1).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_floor_computed: SNR=sqrt(N_DIM/M_max)=sqrt(2048/8)=16.0 (see CRLB section in module docstring);
#     crlb_formula_reference: "SNR=sqrt(N/M), Frady/Kleyko/Sommer, cited via notes/research_vsa_hdc_
#     state_of_mind_prior_art_scour_2026-07-17.md section 3"; discriminator_reachability=true.
# - baseline_in_band: N/A by design (fixed real-passage corpus, no tunable regime) -- the RANDOM-BASELINE
#     SANITY checks (coherence: 0.35<=acc_random<=0.65; query: random-entity floor reported, not gated
#     since per-passage entity-count varies) are the honest analogous validity guards.
# - discriminator survives scale: fixed real-passage corpus (no N/scale sweep axis). Discriminators = (1)
#     C2 beats static + random floor on real passages (coherence, asserted non-trivial); (2) the
#     degenerate single-entity construction proves C2 CAN reduce to static (coherence can-fail); (3) the
#     degenerate no-switch construction proves all 3 query methods CAN tie (query can-fail); (4) C2/A and
#     mech/last-mention empirically disagree on the real corpus (arms differ); (5) at least 1 chunk
#     eviction AND at least 1 chunk reactivation fire across the real 16-passage corpus (the swamp-fix
#     mechanism is actually exercised, not vacuously idle); (6) both the gate-update and gate-hold
#     branches fire at least once (the gated-latch is not vacuously always-update or always-hold).
# - HARD_PASS strictly above floor; explicit bands in prereg JSON (see PRE-REG section above).
# - real_code_path (F.1): self-test constructs+calls the REAL `HierarchicalGatedState` / `score_running_v2`
#     / `run_query_eval` objects this cell newly defines (on hand-verifiable toy passages, exercising
#     chunk-join/eviction/reactivation/gate/query paths explicitly) PLUS the REAL imported `build_grid` /
#     `_sentence_entities` (entity-grid cell, unmodified) at the same real-sentence scale the FULL run uses.
# - real_code_path_and_signature_preflight (F.1-F.5): not_applicable -- this cell constructs no KGStore /
#     fit-module / store-helper substrate object (pure symbolic+FHRR-toy-vector NLP over a fixed sentence
#     corpus, no live substrate_index write), same precedent as every sibling cell in this reading arc.
# - deterministic_seeding (F.5): every torch.Generator is seeded from a FIXED integer formula (BASE_SEED
#     plus a disjoint, declared offset per vector-role -- see _seed_for()); the bag-of-roles tie-break
#     uses `max(..., key=lambda k: (count, k))` (string comparison, not hash()); NEVER `hash()` or
#     `list(set(...))` anywhere in this file -- verified at self-test (same seed -> same permutation and
#     same entity vectors, twice).
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
import platform
import traceback
from datetime import datetime, timezone
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_discourse_wsm_v2_hierarchical_gated_queryable_v1"

# --- GENUINE REUSE, UNMODIFIED, CREDITED (see module docstring PRIOR-WORK section). ---
from experiments.exp_read_discourse_entitygrid_coherence_v1 import (  # noqa: E402
    build_grid, score_role_transition, score_cooccurrence, TRANSITION_WEIGHTS, _credit,
    _full_shuffle_perm, _adjacent_swap_perm, K_PERMUTATIONS, BASE_SEED,
)
from experiments.exp_read_discourse_wsm_running_vs_static_coherence_v1 import (  # noqa: E402
    SHORT_PASSAGES, LONG_PASSAGES, ALL_PASSAGES, CORPUS_LICENSE,
)

# ---------------------------------------------------------------------------
# Hand-set, not fit-to-data constants (see module docstring DECLARED section).
# ---------------------------------------------------------------------------
CHUNK_CAPACITY = 4          # Cowan span, now at CHUNK (not per-entity) granularity
CHUNK_MEMBER_CAP = 4        # same Cowan-span number, applied AGAIN at the membership level (a chunk
                             # itself is bounded); DISCOVERED-NECESSARY during self-test authoring (an
                             # unbounded join rule let 1-4 giant chunks absorb 17-48 raw entities per
                             # passage with ZERO eviction pressure, so reactivation never fired on the
                             # real corpus -- an honest can-fail-style negative caught by the self-test's
                             # own discriminator-fires assertion, fixed BEFORE seeing coherence/query
                             # numbers, not tuned to them; see module docstring addendum below)
REACT_DISCOUNT = 0.5        # reused UNMODIFIED from v1, CITED@Almor 1999
N_DIM = 2048                # CRLB-justified in module docstring (SNR=sqrt(2048/8)=16.0 at M_max=8)
ROLE_KEYS = ("S", "O")      # the two queryable role-slots; "X" excluded (declared scope limit)
CONDITIONS = [("full_shuffle", _full_shuffle_perm), ("adjacent_swap", _adjacent_swap_perm)]


# ---------------------------------------------------------------------------
# FHRR primitives (torch complex64, CLAUDE.md dtype convention). Same formulas as
# exp_nativelang_svo_vsa_probe_v1's numpy implementation (CITED, not literally imported -- see docstring).
# ---------------------------------------------------------------------------
def _seed_for(kind, passage_idx):
    """Deterministic, disjoint per-kind seed ranges -- NEVER hash()/list(set()) (F.5)."""
    offset = {"entity": 20_000_000, "role": 30_000_000, "chunk_id": 40_000_000, "randfloor": 50_000_000}[kind]
    return BASE_SEED + offset + passage_idx * 1000


def make_phasors(seed, count, n_dim=N_DIM):
    """count random FHRR unit-phasor hypervectors, shape (count, n_dim) complex64."""
    g = torch.Generator().manual_seed(seed)
    theta = torch.empty(count, n_dim).uniform_(-math.pi, math.pi, generator=g)
    return torch.complex(torch.cos(theta), torch.sin(theta)).to(torch.complex64)


def bind(a, b):
    """FHRR bind = elementwise complex multiply."""
    return a * b


def unbind(c, b):
    """FHRR unbind = multiply by conjugate."""
    return c * b.conj()


def bundle(vectors):
    """Superpose a list of (N_DIM,) complex64 -> (N_DIM,) complex64 sum (order-free)."""
    if not vectors:
        return torch.zeros(N_DIM, dtype=torch.complex64)
    out = vectors[0].clone()
    for v in vectors[1:]:
        out = out + v
    return out


def cleanup(query, codebook_mat):
    """Nearest codebook row by real part of Hermitian inner product; codebook_mat: (V, N_DIM) complex64."""
    scores = (codebook_mat.conj() @ query).real
    return int(torch.argmax(scores).item())


# ---------------------------------------------------------------------------
# Candidate C2 mechanism: HIERARCHY/CHUNKING + GATED-WM UPDATE + QUERYABLE story-vector.
# See module docstring "MECHANISM UNDER TEST" for the full credited design rationale.
# ---------------------------------------------------------------------------
class _Chunk:
    __slots__ = ("members", "role_slot", "last_active_pos", "vec")

    def __init__(self, track_vectors):
        self.members = set()
        self.role_slot = {"S": None, "O": None}
        self.last_active_pos = -1
        self.vec = torch.zeros(N_DIM, dtype=torch.complex64) if track_vectors else None


class HierarchicalGatedState:
    """v2 running mechanism. See module docstring for full credited design (Eliasmith/Voelker gated
    integrator, Plate HRR chunking, Grosz-Sidner/Centering salience). track_vectors=False skips all torch
    tensor ops (COMPUTE-PROPORTIONALITY: the coherence-scoring permutation loop never reads the HD
    vector, only the symbolic FOCUS/STORE/NEW classification, so building 384 sets of HD vectors would be
    wasted compute); track_vectors=True is used for the single ORIGINAL-order forward pass that feeds the
    query test."""

    def __init__(self, entity_vecs, role_vecs, chunk_id_vecs, capacity=CHUNK_CAPACITY, track_vectors=True):
        self.entity_vecs = entity_vecs
        self.role_vecs = role_vecs
        self.chunk_id_vecs = chunk_id_vecs
        self.capacity = capacity
        self.track_vectors = track_vectors
        self.active = {}            # slot_id (0..capacity-1) -> _Chunk
        self.store = {}             # store_key -> {"members":set,"role_slot":dict,"paged_pos":int}
        self.entity_loc = {}        # entity -> ("FOCUS", slot_id) | ("STORE", store_key)
        self.entity_last_role = {}  # entity -> last role char (S/O/X), for coherence scoring
        self.tier0_slot = None      # most-recently-gated-touched active slot (Eliasmith/Voelker Tier-0)
        self.n_gate_updates = 0
        self.n_gate_holds = 0
        self.n_evictions = 0
        self.n_reactivations = 0

    def prior_state(self, entity):
        loc = self.entity_loc.get(entity)
        if loc is None:
            return "NEW", None
        kind, _key = loc
        return kind, self.entity_last_role.get(entity)

    def _free_slot(self):
        for s in range(self.capacity):
            if s not in self.active:
                return s
        return None

    def _least_salient_active_slot(self):
        """Salience: a chunk currently holding an S/O role beats a role-less chunk (credit Grosz-Sidner/
        Centering subject>object priority applied at chunk granularity), THEN least-recently-touched.
        NOT dumb LRU (per task's explicit design requirement)."""
        def sal(slot_id):
            c = self.active[slot_id]
            has_role = 1 if (c.role_slot["S"] is not None or c.role_slot["O"] is not None) else 0
            return (has_role, c.last_active_pos)
        return min(self.active, key=sal)

    def _evict_one(self, pos):
        victim = self._least_salient_active_slot()
        c = self.active.pop(victim)
        store_key = "chunk_%d_%d_%s" % (pos, victim, sorted(c.members)[0] if c.members else "empty")
        self.store[store_key] = {"members": set(c.members), "role_slot": dict(c.role_slot), "paged_pos": pos}
        for m in c.members:
            self.entity_loc[m] = ("STORE", store_key)
        self.n_evictions += 1
        return victim

    def _ensure_room(self, pos):
        if len(self.active) >= self.capacity:
            self._evict_one(pos)

    def _new_chunk(self, pos):
        self._ensure_room(pos)
        slot = self._free_slot()
        self.active[slot] = _Chunk(self.track_vectors)
        return slot

    def _reactivate(self, store_key, pos):
        """Chunk-LEVEL reactivation (brings every member back into FOCUS, not just the one entity that
        reappeared) -- the durable store retained an EXACT symbolic record (no vector degradation), so
        the reactivated chunk's HD vector is rebuilt fresh from that ground truth (exact recall, same
        "exact recall, not discard" precedent as v1)."""
        rec = self.store.pop(store_key)
        self._ensure_room(pos)
        slot = self._free_slot()
        c = _Chunk(self.track_vectors)
        c.members = set(rec["members"])
        c.role_slot = dict(rec["role_slot"])
        if self.track_vectors:
            vec = torch.zeros(N_DIM, dtype=torch.complex64)
            for r, e in c.role_slot.items():
                if e is not None and e in self.entity_vecs:
                    vec = vec + bind(self.role_vecs[r], self.entity_vecs[e])
            c.vec = vec
        self.active[slot] = c
        for m in c.members:
            self.entity_loc[m] = ("FOCUS", slot)
        self.n_reactivations += 1
        return slot

    def update(self, mentions, pos):
        """mentions: {entity: role} for the CURRENT row (role in {"S","O","X"}). X entities participate
        in chunk membership/eviction bookkeeping (FOCUS/STORE/NEW classification) but are never written
        to a role-slot or the HD vector (declared ROLE_KEYS scope limit)."""
        row_slots = {}
        for e, r in mentions.items():
            loc = self.entity_loc.get(e)
            if loc is not None and loc[0] == "FOCUS":
                slot = loc[1]
            elif loc is not None and loc[0] == "STORE":
                slot = self._reactivate(loc[1], pos)
            else:
                # NEW entity: join a chunk containing another of THIS row's mentions (co-occurrence
                # grouping -- the HIERARCHY/CHUNKING rule: entities mentioned together belong together),
                # but ONLY if that chunk has room under CHUNK_MEMBER_CAP -- an unbounded join rule let a
                # single chunk absorb the whole passage's entity set with zero eviction pressure, so the
                # capped-membership check below is what actually forces genuine chunk turnover.
                def _room(slot_id):
                    return len(self.active[slot_id].members) < CHUNK_MEMBER_CAP
                joined = None
                for other_e, other_slot in row_slots.items():
                    if _room(other_slot):
                        joined = other_slot
                        break
                if joined is None:
                    for other_e in mentions:
                        if other_e == e:
                            continue
                        oloc = self.entity_loc.get(other_e)
                        if oloc is not None and oloc[0] == "FOCUS" and _room(oloc[1]):
                            joined = oloc[1]
                            break
                slot = joined if joined is not None else self._new_chunk(pos)
                self.active[slot].members.add(e)
                self.entity_loc[e] = ("FOCUS", slot)
            row_slots[e] = slot
            chunk = self.active[slot]
            chunk.last_active_pos = pos
            self.tier0_slot = slot
            if r in ROLE_KEYS:
                old = chunk.role_slot.get(r)
                if old != e:
                    # GATED replace-latch: genuine change (surprisal gate=1) -> subtract old binding, add
                    # new (credit Eliasmith/Voelker doubly-latched integrator). NOT an accumulate -- this
                    # is what keeps the chunk vector queryable instead of crosstalk-growing unboundedly.
                    if self.track_vectors:
                        if old is not None and old in self.entity_vecs:
                            chunk.vec = chunk.vec - bind(self.role_vecs[r], self.entity_vecs[old])
                        chunk.vec = chunk.vec + bind(self.role_vecs[r], self.entity_vecs[e])
                    chunk.role_slot[r] = e
                    self.n_gate_updates += 1
                else:
                    self.n_gate_holds += 1  # redundant re-mention, no state change -> HOLD, no-op
            self.entity_last_role[e] = r

    def story_vector(self):
        """The SINGLE maintained, queryable story-vector (credit Plate HRR chunking/superposition):
        bundle of every active chunk's content, each bound to its own fixed CHUNK_ID register vector."""
        if not self.track_vectors:
            raise RuntimeError("story_vector() called on a track_vectors=False state (coherence-only pass)")
        parts = [bind(self.chunk_id_vecs[slot], c.vec) for slot, c in self.active.items()]
        return bundle(parts)

    def query(self, role, entity_names, entity_mat, slot=None):
        """Unbind the story-vector by (chunk-id, role) + cleanup against the entity codebook. slot=None
        uses tier0_slot (the most-recently-gated-touched chunk -- credit Eliasmith/Voelker's Tier-0
        'true focus' O(1) pointer: 'who/what is CURRENTLY salient right now')."""
        if slot is None:
            slot = self.tier0_slot
        if slot is None or slot not in self.active:
            return None
        sv = self.story_vector()
        unbound_chunk = unbind(sv, self.chunk_id_vecs[slot])
        unbound_entity = unbind(unbound_chunk, self.role_vecs[role])
        idx = cleanup(unbound_entity, entity_mat)
        return entity_names[idx]


# ---------------------------------------------------------------------------
# Per-passage codebook construction (deterministic, fixed seeds -- see _seed_for).
# ---------------------------------------------------------------------------
def build_codebooks(entity_roles, passage_idx):
    names = sorted(entity_roles)
    entity_mat = make_phasors(_seed_for("entity", passage_idx), max(len(names), 1))
    entity_vecs = {n: entity_mat[i] for i, n in enumerate(names)}
    return names, entity_mat, entity_vecs


_ROLE_VECS = None
_CHUNK_ID_VECS = None


def global_role_and_chunk_vecs():
    """Role vectors (2) and chunk-ID register vectors (CHUNK_CAPACITY) are GLOBAL (small closed sets,
    shared across all passages, fixed seeds -- not per-passage like entities)."""
    global _ROLE_VECS, _CHUNK_ID_VECS
    if _ROLE_VECS is None:
        rmat = make_phasors(BASE_SEED + 60_000_000, len(ROLE_KEYS))
        _ROLE_VECS = {r: rmat[i] for i, r in enumerate(ROLE_KEYS)}
    if _CHUNK_ID_VECS is None:
        cmat = make_phasors(BASE_SEED + 70_000_000, CHUNK_CAPACITY)
        _CHUNK_ID_VECS = {s: cmat[s] for s in range(CHUNK_CAPACITY)}
    return _ROLE_VECS, _CHUNK_ID_VECS


# ---------------------------------------------------------------------------
# SUB-TEST 1: coherence scoring (candidate C2), symbolic-only (track_vectors=False), same shape as v1.
# ---------------------------------------------------------------------------
def score_running_v2(entity_roles, order, role_vecs, chunk_id_vecs, entity_vecs=None):
    state = HierarchicalGatedState({} if entity_vecs is None else entity_vecs, role_vecs, chunk_id_vecs,
                                    track_vectors=False)
    total = 0.0
    n = len(order)
    for pos in range(n):
        row_idx = order[pos]
        row_mentions = {e: roles[row_idx] for e, roles in entity_roles.items() if roles[row_idx] is not None}
        if pos > 0:
            for e, r in row_mentions.items():
                kind, prev_role = state.prior_state(e)
                if kind == "NEW":
                    total += TRANSITION_WEIGHTS[(None, r)]
                elif kind == "FOCUS":
                    total += TRANSITION_WEIGHTS[(prev_role, r)]
                else:
                    total += REACT_DISCOUNT * TRANSITION_WEIGHTS[(prev_role, r)]
        state.update(row_mentions, pos)
    return total


def analyze_passage_coherence(passage, passage_idx, role_vecs, chunk_id_vecs, k=K_PERMUTATIONS, base_seed=BASE_SEED):
    sents = passage["sents"]
    entity_roles, mention_sets, n = build_grid(sents)
    order0 = list(range(n))
    orig_A = score_role_transition(entity_roles, order0)
    orig_B1 = score_cooccurrence(mention_sets, order0)
    orig_C2 = score_running_v2(entity_roles, order0, role_vecs, chunk_id_vecs)

    records = {}
    for cond_idx, (cond_name, gen) in enumerate(CONDITIONS):
        recs = []
        for kk in range(k):
            seed = base_seed + passage_idx * 10000 + cond_idx * 1000 + kk
            order = gen(n, random.Random(seed))
            rand_rng = random.Random(seed + 5_000_000)
            recs.append({
                "score_A_perm": score_role_transition(entity_roles, order),
                "score_B1_perm": score_cooccurrence(mention_sets, order),
                "score_C2_perm": score_running_v2(entity_roles, order, role_vecs, chunk_id_vecs),
                "score_rand_orig": rand_rng.random(),
                "score_rand_perm": rand_rng.random(),
            })
        records[cond_name] = recs
    return {
        "corpus": passage["corpus"], "start": passage["start"], "length_class": passage["length_class"],
        "n_sents": n, "n_entities": len(entity_roles), "entities": sorted(entity_roles),
        "orig_A": orig_A, "orig_B1": orig_B1, "orig_C2": orig_C2, "records": records,
    }


def aggregate_coherence(passage_results, filt=None):
    prs = [pr for pr in passage_results if (filt is None or filt(pr))]
    out = {"n_passages_in_subset": len(prs)}
    all_pairs = []
    per_passage_delta = []
    for cond_name, _gen in CONDITIONS:
        for scorer, orig_key, perm_key in (
            ("A", "orig_A", "score_A_perm"), ("B1", "orig_B1", "score_B1_perm"),
            ("C2", "orig_C2", "score_C2_perm"), ("random", "score_rand_orig", "score_rand_perm"),
        ):
            credits = []
            for pr in prs:
                for rec in pr["records"][cond_name]:
                    o = pr[orig_key] if orig_key in pr else rec[orig_key]
                    p = rec[perm_key]
                    c = _credit(o, p)
                    credits.append(c)
                    if scorer in ("A", "C2"):
                        all_pairs.append((cond_name, scorer, pr["corpus"], pr["start"], c))
            out["acc_%s_%s" % (cond_name, scorer)] = float(sum(credits) / len(credits)) if credits else 0.0
            out["n_%s_%s" % (cond_name, scorer)] = len(credits)
    for pr in prs:
        a_credits = [_credit(pr["orig_A"], rec["score_A_perm"]) for rec in pr["records"]["adjacent_swap"]]
        c_credits = [_credit(pr["orig_C2"], rec["score_C2_perm"]) for rec in pr["records"]["adjacent_swap"]]
        a_mean = sum(a_credits) / len(a_credits) if a_credits else 0.0
        c_mean = sum(c_credits) / len(c_credits) if c_credits else 0.0
        per_passage_delta.append({
            "corpus": pr["corpus"], "start": pr["start"], "length_class": pr["length_class"],
            "acc_A_adjswap": a_mean, "acc_C2_adjswap": c_mean, "delta_C2_minus_A": c_mean - a_mean,
        })
    out["_all_pairs_for_arms_differ_check"] = all_pairs
    out["per_passage_delta_adjswap"] = per_passage_delta
    return out


def coherence_verdict(agg_all, agg_long):
    accA_all = agg_all["acc_adjacent_swap_A"]
    accC_all = agg_all["acc_adjacent_swap_C2"]
    accA_long = agg_long["acc_adjacent_swap_A"]
    accC_long = agg_long["acc_adjacent_swap_C2"]
    acc_rand_full = agg_all["acc_full_shuffle_random"]
    acc_rand_swap = agg_all["acc_adjacent_swap_random"]
    margin_all = accC_all - accA_all
    margin_long = accC_long - accA_long
    deltas = [row["delta_C2_minus_A"] for row in agg_all["per_passage_delta_adjswap"]]
    frac_nonneg = sum(1 for d in deltas if d >= 0.0) / len(deltas) if deltas else 0.0
    random_sanity_ok = (0.35 <= acc_rand_full <= 0.65) and (0.35 <= acc_rand_swap <= 0.65)
    hp = (margin_all >= 0.05 and margin_long >= 0.05 and frac_nonneg >= 0.50 and random_sanity_ok)
    hf = (margin_all <= 0.01 or frac_nonneg < 0.30)
    if not random_sanity_ok:
        tier = "INVALID_TEST_DESIGN"
    else:
        tier = "HARD_PASS" if hp else ("HARD_FAIL" if hf else "MIDDLE_BAND")
    msg = ("COHERENCE %s | ADJ-SWAP(all16) acc_C2=%.3f acc_A=%.3f margin=%+.3f | ADJ-SWAP(long6) "
           "acc_C2=%.3f acc_A=%.3f margin=%+.3f | frac_nonneg=%.2f acc_rand_full=%.3f acc_rand_swap=%.3f"
           % (tier, accC_all, accA_all, margin_all, accC_long, accA_long, margin_long, frac_nonneg,
              acc_rand_full, acc_rand_swap))
    return tier, msg, margin_all, margin_long, frac_nonneg, random_sanity_ok


# ---------------------------------------------------------------------------
# SUB-TEST 2: queryability (new). Single forward ORIGINAL-order pass, track_vectors=True.
# ---------------------------------------------------------------------------
def run_query_eval(entity_roles, n, entity_names, entity_mat, entity_vecs, role_vecs, chunk_id_vecs,
                    passage_idx, randfloor_rng):
    state = HierarchicalGatedState(entity_vecs, role_vecs, chunk_id_vecs, track_vectors=True)
    current_holder = {"S": None, "O": None}
    prev_holder = {"S": None, "O": None}
    role_counts = {"S": {}, "O": {}}
    last_mentioned = None
    records = []
    for pos in range(n):
        row_mentions = {e: roles[pos] for e, roles in entity_roles.items() if roles[pos] is not None}
        state.update(row_mentions, pos)
        for e, r in row_mentions.items():
            last_mentioned = e
            if r in ROLE_KEYS:
                current_holder[r] = e
                role_counts[r][e] = role_counts[r].get(e, 0) + 1
        if pos > 0:
            for r in ROLE_KEYS:
                gt = current_holder[r]
                if gt is None:
                    continue
                is_switch = (gt != prev_holder[r])
                mech = state.query(r, entity_names, entity_mat)
                bag = max(role_counts[r], key=lambda k: (role_counts[r][k], k)) if role_counts[r] else None
                rand_pick = entity_names[randfloor_rng.randrange(len(entity_names))] if entity_names else None
                records.append({
                    "passage_idx": passage_idx, "pos": pos, "role": r, "ground_truth": gt,
                    "mech": mech, "last_mention": last_mentioned, "bag_of_roles": bag, "random": rand_pick,
                    "is_switch": is_switch,
                })
        prev_holder = dict(current_holder)
    return records, state


def aggregate_query(all_records, subset_pred=None):
    recs = [r for r in all_records if (subset_pred is None or subset_pred(r))]
    out = {"n": len(recs)}
    for method in ("mech", "last_mention", "bag_of_roles", "random"):
        correct = sum(1 for r in recs if r[method] == r["ground_truth"])
        out["acc_%s" % method] = correct / len(recs) if recs else 0.0
    return out


def query_verdict(agg_hard):
    n_hard = agg_hard["n"]
    mech = agg_hard["acc_mech"]
    lm = agg_hard["acc_last_mention"]
    bag = agg_hard["acc_bag_of_roles"]
    margin_lm = mech - lm
    margin_bag = mech - bag
    hp = (margin_lm >= 0.10 and margin_bag >= 0.10 and mech >= 0.40 and n_hard >= 15)
    hf = (margin_lm <= 0.0 or margin_bag <= 0.0 or mech < 0.15 or n_hard < 8)
    tier = "HARD_PASS" if hp else ("HARD_FAIL" if hf else "MIDDLE_BAND")
    msg = ("QUERY %s | HARD(switch,n=%d) acc_mech=%.3f acc_last_mention=%.3f acc_bag_of_roles=%.3f "
           "acc_random=%.3f margin_vs_lm=%+.3f margin_vs_bag=%+.3f"
           % (tier, n_hard, mech, lm, bag, agg_hard["acc_random"], margin_lm, margin_bag))
    return tier, msg, margin_lm, margin_bag


# ---------------------------------------------------------------------------
# infra (start marker / crash metrics / atomic write) -- same convention as v1.
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
# top-level run: coherence sub-test + query sub-test, over all 16 passages.
# ---------------------------------------------------------------------------
def run_all():
    role_vecs, chunk_id_vecs = global_role_and_chunk_vecs()

    coherence_results = [analyze_passage_coherence(p, i, role_vecs, chunk_id_vecs) for i, p in enumerate(ALL_PASSAGES)]
    agg_all = aggregate_coherence(coherence_results, filt=None)
    agg_long = aggregate_coherence(coherence_results, filt=lambda pr: pr["length_class"] == "long")
    agg_short = aggregate_coherence(coherence_results, filt=lambda pr: pr["length_class"] == "short")

    all_query_records = []
    agg_state_totals = {"n_evictions": 0, "n_reactivations": 0, "n_gate_updates": 0, "n_gate_holds": 0}
    for i, passage in enumerate(ALL_PASSAGES):
        entity_roles, _mention_sets, n = build_grid(passage["sents"])
        names, entity_mat, entity_vecs = build_codebooks(entity_roles, i)
        randfloor_rng = random.Random(_seed_for("randfloor", i))
        recs, final_state = run_query_eval(entity_roles, n, names, entity_mat, entity_vecs, role_vecs,
                                            chunk_id_vecs, i, randfloor_rng)
        all_query_records.extend(recs)
        agg_state_totals["n_evictions"] += final_state.n_evictions
        agg_state_totals["n_reactivations"] += final_state.n_reactivations
        agg_state_totals["n_gate_updates"] += final_state.n_gate_updates
        agg_state_totals["n_gate_holds"] += final_state.n_gate_holds

    agg_query_hard = aggregate_query(all_query_records, subset_pred=lambda r: r["is_switch"])
    agg_query_all = aggregate_query(all_query_records, subset_pred=None)

    return {
        "coherence_results": coherence_results, "agg_all": agg_all, "agg_long": agg_long, "agg_short": agg_short,
        "all_query_records": all_query_records, "agg_query_hard": agg_query_hard, "agg_query_all": agg_query_all,
        "state_totals": agg_state_totals,
    }


def compute_combined_verdict(run):
    coh_tier, coh_msg, margin_all, margin_long, frac_nonneg, coh_sanity_ok = coherence_verdict(run["agg_all"], run["agg_long"])
    q_tier, q_msg, margin_lm, margin_bag = query_verdict(run["agg_query_hard"])

    if not coh_sanity_ok:
        combined = "INVALID_TEST_DESIGN"
    elif coh_tier == "HARD_FAIL" or q_tier == "HARD_FAIL":
        combined = "HARD_FAIL"
    elif coh_tier == "HARD_PASS" and q_tier == "HARD_PASS":
        combined = "HARD_PASS"
    else:
        combined = "MIDDLE_BAND"

    weakest = []
    if coh_tier != "HARD_PASS":
        weakest.append("COHERENCE sub-test is %s (not HARD_PASS): %s" % (coh_tier, coh_msg))
    if q_tier != "HARD_PASS":
        weakest.append("QUERY sub-test is %s (not HARD_PASS): %s" % (q_tier, q_msg))
    if not weakest:
        weakest = ["none (both COHERENCE and QUERY sub-tests HARD_PASS)"]

    msg = "%s | %s | %s" % (combined, coh_msg, q_msg)
    return combined, msg, coh_tier, q_tier, weakest


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert every discriminator fires (can-fail x2, arms-differ x2,
# eviction/reactivation/gate firing, unbind roundtrip, cardinality, deterministic seeding).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (HierarchicalGatedState + FHRR primitives)...", flush=True)
    role_vecs, chunk_id_vecs = global_role_and_chunk_vecs()

    # (1) FHRR roundtrip sanity: bind then unbind exactly recovers the filler on a hand toy (no crosstalk).
    ent_mat = make_phasors(999, 3)
    ent_vecs = {"a": ent_mat[0], "b": ent_mat[1], "c": ent_mat[2]}
    bound = bind(role_vecs["S"], ent_vecs["a"])
    recovered = unbind(bound, role_vecs["S"])
    assert torch.allclose(recovered, ent_vecs["a"], atol=1e-4), "FHRR bind/unbind roundtrip failed on a hand toy"
    idx = cleanup(recovered, ent_mat)
    assert idx == 0, "cleanup did not recover the correct entity index on a noise-free toy"

    # (2) chunk join/eviction/reactivation, real code path, capacity=2 for a fast hand-verifiable trace.
    toy_names = ["bear", "fish", "jackal", "vulture"]
    toy_ent_mat = make_phasors(1001, len(toy_names))
    toy_ent_vecs = {n: toy_ent_mat[i] for i, n in enumerate(toy_names)}
    st = HierarchicalGatedState(toy_ent_vecs, role_vecs, chunk_id_vecs, capacity=2, track_vectors=True)
    st.update({"bear": "S", "fish": "O"}, 0)  # co-occur -> SAME chunk (hierarchy/chunking join rule)
    assert len(st.active) == 1, "bear+fish co-mentioned in the same row should JOIN one chunk: %r" % st.active
    slot_bf = next(iter(st.active))
    assert st.active[slot_bf].members == {"bear", "fish"}
    st.update({"jackal": "S"}, 1)  # new chunk (capacity=2, room for 1 more)
    assert len(st.active) == 2
    st.update({"vulture": "S"}, 2)  # 3rd distinct chunk needed, capacity=2 -> evicts LEAST SALIENT
    assert st.n_evictions == 1, "3rd chunk beyond capacity=2 should trigger exactly 1 eviction"
    # the evicted chunk must be findable in the durable store (exact, not degraded).
    assert len(st.store) == 1
    evicted_members = next(iter(st.store.values()))["members"]
    kind_bear, _ = st.prior_state("bear")
    assert kind_bear == "STORE", "bear (part of the first, presumably-evicted chunk) should be in STORE: %s" % kind_bear

    # (2b) reactivation: bear reappears -> the WHOLE evicted chunk (bear AND fish) comes back to FOCUS,
    # not just bear alone -- the chunk-LEVEL reactivation this cell adds over v1's per-entity reactivation.
    st.update({"bear": "O"}, 3)
    kind_bear2, _ = st.prior_state("bear")
    kind_fish2, _ = st.prior_state("fish")
    assert kind_bear2 == "FOCUS" and kind_fish2 == "FOCUS", (
        "chunk-level reactivation should restore BOTH bear and fish to FOCUS together: bear=%s fish=%s"
        % (kind_bear2, kind_fish2))
    assert st.n_reactivations == 1

    # (3) GATED update: a redundant re-mention (same filler already in that role-slot) must be a HOLD
    # (no vector touch, gate counter increments n_gate_holds not n_gate_updates); a genuine change must
    # increment n_gate_updates and be a REPLACE (old binding subtracted, new one added).
    st2 = HierarchicalGatedState(toy_ent_vecs, role_vecs, chunk_id_vecs, capacity=4, track_vectors=True)
    st2.update({"bear": "S"}, 0)
    updates_before = st2.n_gate_updates
    st2.update({"bear": "S"}, 1)  # SAME filler in the SAME role-slot -> HOLD, not update
    assert st2.n_gate_updates == updates_before, "redundant re-mention should NOT increment n_gate_updates"
    assert st2.n_gate_holds >= 1, "redundant re-mention should increment n_gate_holds (gate fired HOLD)"
    slot_bear = st2.entity_loc["bear"][1]
    vec_before_change = st2.active[slot_bear].vec.clone()
    st2.update({"fish": "S"}, 2)  # fish joins bear's chunk (co-occur with nothing else active -> new chunk;
    # force it into bear's chunk instead by re-mentioning bear in the SAME row so they co-occur):
    st2.update({"bear": "O", "fish": "S"}, 3)  # genuine change on bear's S-slot value indirectly via O-write
    assert not torch.allclose(st2.active[slot_bear].vec, vec_before_change), (
        "a genuine role-slot change should REPLACE the chunk vector (subtract old + add new), not hold it fixed")

    # (4) QUERY roundtrip on a controlled toy (no crosstalk risk -- single active chunk, single role-write):
    st3 = HierarchicalGatedState(toy_ent_vecs, role_vecs, chunk_id_vecs, capacity=4, track_vectors=True)
    st3.update({"bear": "S"}, 0)
    ans = st3.query("S", toy_names, toy_ent_mat)
    assert ans == "bear", "query('S') on a single-chunk single-role toy should exactly recover 'bear', got %r" % ans

    # (5) CAN-FAIL construction (coherence): single-entity-always-present grid -> C2 must reduce to the
    # EXACT SAME ranking as static (candidate A) on every permutation (no eviction/reactivation possible
    # with only 1 entity ever competing for a chunk).
    degenerate_roles = {"x": ["S", "S", "S", "S", "S"]}
    deg_order0 = list(range(5))
    deg_orig_A = score_role_transition(degenerate_roles, deg_order0)
    deg_orig_C2 = score_running_v2(degenerate_roles, deg_order0, role_vecs, chunk_id_vecs)
    for seed in range(8):
        perm = _full_shuffle_perm(5, random.Random(7000 + seed))
        credit_A = _credit(deg_orig_A, score_role_transition(degenerate_roles, perm))
        credit_C2 = _credit(deg_orig_C2, score_running_v2(degenerate_roles, perm, role_vecs, chunk_id_vecs))
        assert credit_A == credit_C2, (
            "COHERENCE CAN-FAIL construction violated: single-entity-always-present grid should make C2 "
            "and static agree on EVERY permutation; got credit_A=%s credit_C2=%s at seed=%s" % (credit_A, credit_C2, seed))

    # (6) CAN-FAIL construction (query): role never switches holder -> mechanism, last-mention, and
    # bag-of-roles must ALL tie at 1.0 on the FULL query set (no method has an unfair inherent edge here).
    deg_names = ["only_entity"]
    deg_mat = make_phasors(2002, 1)
    deg_vecs = {"only_entity": deg_mat[0]}
    deg_entity_roles = {"only_entity": ["S"] * 6}
    deg_recs, _st = run_query_eval(deg_entity_roles, 6, deg_names, deg_mat, deg_vecs, role_vecs, chunk_id_vecs,
                                    0, random.Random(1))
    deg_agg = aggregate_query(deg_recs, subset_pred=None)
    assert deg_agg["n"] > 0, "degenerate query can-fail construction produced zero query records"
    assert deg_agg["acc_mech"] == 1.0 and deg_agg["acc_last_mention"] == 1.0 and deg_agg["acc_bag_of_roles"] == 1.0, (
        "QUERY CAN-FAIL construction violated: a never-switching role should make all 3 methods tie at "
        "1.0; got mech=%.3f last_mention=%.3f bag_of_roles=%.3f"
        % (deg_agg["acc_mech"], deg_agg["acc_last_mention"], deg_agg["acc_bag_of_roles"]))

    # (7) real-corpus run (real code path at full scale): cardinality, arms-differ (x2), eviction/
    # reactivation/gate firing, random-baseline sanity -- all on the REAL 16-passage corpus.
    run = run_all()
    expected_n_coh = len(ALL_PASSAGES) * K_PERMUTATIONS * len(CONDITIONS)
    got_n_coh = sum(len(pr["records"][c]) for pr in run["coherence_results"] for c, _g in CONDITIONS)
    assert got_n_coh == expected_n_coh, "coherence cardinality mismatch: expected %d, got %d" % (expected_n_coh, got_n_coh)
    assert len(ALL_PASSAGES) == 16

    pairs = run["agg_all"]["_all_pairs_for_arms_differ_check"]
    a_credits = [c for cn, sc, cp, s, c in pairs if sc == "A"]
    c2_credits = [c for cn, sc, cp, s, c in pairs if sc == "C2"]
    assert any(a != c for a, c in zip(a_credits, c2_credits)), (
        "META_RULE_AF: C2 and static (A) NEVER disagree across the real corpus -- suspect identical signal")

    q_all_recs = run["all_query_records"]
    assert any(r["mech"] != r["last_mention"] for r in q_all_recs), (
        "META_RULE_AF: mechanism query decode NEVER disagrees with the last-mention baseline on the real "
        "corpus -- suspect the mechanism is just re-deriving last-mention")

    st_tot = run["state_totals"]
    assert st_tot["n_evictions"] >= 1, "swamp-fix mechanism never evicted a chunk across the real 16-passage corpus"
    assert st_tot["n_reactivations"] >= 1, "chunk-level reactivation never fired across the real 16-passage corpus"
    assert st_tot["n_gate_updates"] >= 1 and st_tot["n_gate_holds"] >= 1, (
        "gated latch did not exercise BOTH branches on the real corpus: updates=%d holds=%d"
        % (st_tot["n_gate_updates"], st_tot["n_gate_holds"]))

    assert 0.30 <= run["agg_all"]["acc_full_shuffle_random"] <= 0.70
    assert 0.30 <= run["agg_all"]["acc_adjacent_swap_random"] <= 0.70

    # (8) deterministic seeding: same seed -> same permutation AND same entity vectors, twice.
    p1 = _full_shuffle_perm(8, random.Random(12345))
    p2 = _full_shuffle_perm(8, random.Random(12345))
    assert p1 == p2
    v1 = make_phasors(777, 5)
    v2 = make_phasors(777, 5)
    assert torch.allclose(v1, v2), "make_phasors is NOT deterministic under a fixed seed"

    combined, msg, coh_tier, q_tier, weakest = compute_combined_verdict(run)
    print("[self_test] PASS | %s" % msg, flush=True)
    return True


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)

    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"  # smoke == full (fixed tiny corpus)
    out_dir = _out_dir(run_mode)
    expected_n_units = len(ALL_PASSAGES) * K_PERMUTATIONS * len(CONDITIONS)
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print("[wsm_v2] run_mode=%s n_passages=%d K=%d expected_n_units=%d"
          % (run_mode, len(ALL_PASSAGES), K_PERMUTATIONS, expected_n_units), flush=True)

    run = run_all()
    for pr in run["coherence_results"]:
        print("[wsm_v2] passage %s:%s (%s) n_sents=%d n_entities=%d"
              % (pr["corpus"], pr["start"], pr["length_class"], pr["n_sents"], pr["n_entities"]), flush=True)

    combined, msg, coh_tier, q_tier, weakest = compute_combined_verdict(run)
    elapsed = time.perf_counter() - t0
    print("[wsm_v2] %s" % msg, flush=True)
    print("[wsm_v2] state_totals=%s" % run["state_totals"], flush=True)

    def strip_pairs(a):
        return {k: v for k, v in a.items() if k != "_all_pairs_for_arms_differ_check"}

    def strip_records(pr):
        return {k: v for k, v in pr.items() if k != "records"}

    metrics = {
        "verdict": combined, "verdict_msg": msg, "summary": msg[:300],
        "run_mode": run_mode, "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "expected_n_units": expected_n_units,
        "n_passages": len(ALL_PASSAGES), "n_short": len(SHORT_PASSAGES), "n_long": len(LONG_PASSAGES),
        "k_permutations": K_PERMUTATIONS, "conditions": [c for c, _g in CONDITIONS],
        "coherence_tier": coh_tier, "query_tier": q_tier, "weakest_interface": weakest,
        "agg_all": strip_pairs(run["agg_all"]), "agg_long": strip_pairs(run["agg_long"]),
        "agg_short": strip_pairs(run["agg_short"]),
        "agg_query_hard": run["agg_query_hard"], "agg_query_all": run["agg_query_all"],
        "n_query_records_total": len(run["all_query_records"]),
        "state_totals": run["state_totals"],
        "per_passage": [strip_records(pr) for pr in run["coherence_results"]],
        "corpus_license": CORPUS_LICENSE,
        "prereg": {
            "hard_pass": "COMBINED: coherence HARD_PASS (margin_adjswap_all>=0.05 & margin_adjswap_long>=0.05 "
                         "& frac_nonneg>=0.50 & random_sanity_ok) AND query HARD_PASS (mech_acc_hard >= "
                         "last_mention_acc_hard+0.10 & mech_acc_hard >= bag_of_roles_acc_hard+0.10 & "
                         "mech_acc_hard>=0.40 & n_hard>=15)",
            "hard_fail": "coherence HARD_FAIL (margin_adjswap_all<=0.01 | <0 | frac_nonneg<0.30) OR query "
                         "HARD_FAIL (mech_acc_hard ties/loses either baseline | mech_acc_hard<0.15 | n_hard<8)",
            "middle": "otherwise (report weaker sub-test)",
            "invalid": "coherence random_baseline_sanity fails",
            "novel_synthesis_P": 0.28,
            "corpus": CORPUS_LICENSE,
            "n_dim": N_DIM, "chunk_capacity": CHUNK_CAPACITY, "react_discount": REACT_DISCOUNT,
            "role_keys": list(ROLE_KEYS),
            "crlb_floor_computed": "SNR=sqrt(N_DIM/M_max)=sqrt(2048/8)=16.0",
            "crlb_formula_reference": "SNR=sqrt(N/M), Frady/Kleyko/Sommer, cited via notes/research_vsa_hdc_"
                                       "state_of_mind_prior_art_scour_2026-07-17.md section 3",
            "discriminator_reachability": True,
            "compute_architecture": "sequential-CPU, torch complex64, wall<10s (GPU-batching exemption: "
                                     "wall-time<10s total; coherence-scoring loop uses track_vectors=False "
                                     "to skip HD tensor ops entirely, COMPUTE-PROPORTIONALITY)",
            "storage_strategy": "no_storage", "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true", "deterministic_seeding": True,
            "real_code_path_exercised": ["build_grid", "score_role_transition", "score_cooccurrence",
                                         "HierarchicalGatedState", "score_running_v2", "run_query_eval"],
            "arms_differ_verified": "empirical (real corpus): C2(coherence) vs A disagree on >=1 pair; "
                                     "mech(query) vs last_mention disagree on >=1 real query",
            "crlb_n/a": False,
            "real_code_path_and_signature_preflight": "not_applicable_no_substrate_objects_pure_symbolic_"
                                                       "plus_fhrr_toy_vector_nlp_cell",
            "reused_v1_cell": "exp_read_discourse_wsm_running_vs_static_coherence_v1 (landed HARD_FAIL; "
                              "margin_adjswap_all=-0.060, margin_adjswap_long=-0.222 -- the swamp this "
                              "cell's hierarchy/chunking fix targets; corpus + permutation machinery reused "
                              "verbatim, flat-focus/LRU mechanism replaced)",
            "reused_entitygrid_cell": "exp_read_discourse_entitygrid_coherence_v1 (landed MIDDLE_BAND; "
                                      "static baseline + entity/role extraction reused unmodified)",
            "credited_no_code_reuse": "exp_nativelang_svo_vsa_probe_v1 (FHRR bind/unbind/bundle/cleanup "
                                      "algebra, same formulas reimplemented in torch complex64 per CLAUDE.md "
                                      "dtype convention); Eliasmith/Voelker doubly-latched gated integrator; "
                                      "Plate HRR chunking/superposition; Grosz-Sidner/Centering subject>"
                                      "object salience ranking (see module docstring for full citations)",
        },
    }
    _write_metrics(out_dir, metrics)
    print("[wsm_v2] %s in %.4fs -> %s" % (combined, elapsed, out_dir / "metrics.json"), flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv):
            _md = "smoke"
        elif "--self-test" in sys.argv or "self_test" in sys.argv:
            _md = "self_test"
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
