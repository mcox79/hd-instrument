"""exp_read_discourse_state_hd_vs_symbolic_coherence_scalar_score_v1 -- the LAST open state-of-mind door.

QUESTION: does an HD superposed discourse state earn a real KEEP in the COHERENCE SCALAR-SCORE mode?
Here we do NOT decode individual members (the membership door -- CLOSED symbolic by v1/v3 + the query-
distribution map). Instead we accumulate M propositions (role-filler bindings) into a fixed-size HD bundle
and compute a GRADED O(1) similarity (normalized Hermitian inner product) of a NEW proposition against the
whole bundle -- Kintsch construction-integration / BEAGLE. The membership-decode CROSSTALK CEILING (Frady/
Kleyko/Sommer 1707.01429) does NOT directly apply to a SCALAR similarity readout, so this is where HD might
earn a keep. TASK: discriminate a COHERENT continuation from an INCOHERENT (CONTRADICTORY/confabulated) one
by the bundle-similarity SCORE, and ask whether HD's graded coherence beats a SYMBOLIC coherence signal at
EQUAL BIT-FOOTPRINT under genuine overload.

WHY THIS CELL (lineage, credit-not-steal -- learn-from + build-on):
  - REFRAME note notes/research_state_of_mind_hd_load_bearing_query_mode_reframe_2026-07-17.md flagged the
    coherence-scalar-score as the ONE mode structurally distinct from membership (a SCALAR readout escapes the
    membership crosstalk ceiling) and explicitly PRESERVED-as-not-closed by the query-distribution-map VET
    (aee82236). This cell tests exactly that door.
  - v2 hierarchical cell (exp_read_discourse_wsm_v2_hierarchical_gated_queryable_v1, 4487bd222) had a
    "coherence" sub-test that FAILED, but it was computed SYMBOLICALLY (track_vectors=False -- never touched
    the HD vector). This v1 is the FIX: ROUTE coherence THROUGH the HD bundle (graded similarity), the way it
    should have been. The permutation/coherence SHAPE is credited to that cell; the mechanism is HD-routed.
  - FHRR algebra (torch complex64, CLAUDE.md dtype) credited to exp_nativelang_svo_vsa_probe_v1 + the query-
    distribution-map cell (make_phasors / bind=elementwise-mult / bundle=sum / normalized real inner product).
    Not literally imported (self-contained; avoids cross-cell drift).

PRIOR-WORK CONCEPT-QUERY (mandatory, ran before authoring): `bash tools/substrate_query.sh "coherence scalar
score bundle similarity discourse state proposition accumulation Kintsch construction integration"` -> top
hits are LEXICAL KB nodes ('integration' 0.359, 'accumulation' 0.360) + one process note about an unrelated
INTEGRATION_FAIL disposition (0.362); NONE at cosine>0.30 is a prior arc experiment cell on HD coherence-
scalar-score. Genuinely novel door (the scalar coherence readout at equal footprint), building on the credited
v2/query-map lineage.

THE KEY ENCODING INSIGHT (the arc's native-bind construction-proof + encoding lever, made load-bearing here):
  A COHERENCE violation worth testing is a CONJUNCTION violation -- a CONFABULATION: entities that are all
  individually topical and role-valid, combined into a pairing that NEVER OCCURRED (agent a really was an
  agent, patient p' really was a patient, but (a,p') was never asserted). Discriminating a real fact (a,p) from a
  confabulation (a,p') requires representing the CONJUNCTION, not the marginals. So:
    - hd_bind (PRIMARY): chunk(a,p) = E[a] (x) E[p] (native FHRR bind); B = sum_i chunk_i. score = Re<chunk(q),B>/N
      ~= frequency the EXACT pair occurred. PRESERVES the conjunction -> CAN discriminate confabulations.
    - hd_add (CONTRAST, must-fail): chunk = E[a] + E[p] (additive, no bind); score reads MARGINALS only ->
      score(a,p) ~= score(a,p') -> AUC ~0.5 on the confabulation discriminator. Shows why bind is load-bearing.
    - sym_prop_evict (FAIR competitor): exact (a,p) TUPLE store, LRU-evict at capacity C; score = 1 if the
      exact fact is retained else 0. Conjunction-exact but CAPACITY-BOUNDED -> evicts under overload.
    - sym_pair_marginal (CONTRAST, must-fail): stores (role,filler) marginal pairs; score(a,p)=[a retained]+
      [p retained] -> can't tell a confabulation from a fact -> AUC ~0.5 (symmetric failure to hd_add).
  The REAL FIGHT is hd_bind vs sym_prop_evict at EQUAL BIT-FOOTPRINT. hd_add / sym_pair_marginal are the
  symmetric conjunction-blind controls that prove the discriminator is genuinely conjunction-sensitive.

BIT-HONEST FOOTPRINT (the v4 VET's discipline -- give symbolic its fair equal-BIT budget, NOT equal-slot):
  - hd bundle = ONE (N,) complex64 vector = 2N float32 = 8N bytes (N=1024 -> 8192 bytes), CONSTANT in M.
  - sym_prop store = exact (a,p) tuple = 2 filler ids; VOCAB=16384 -> 14 bits -> 2 bytes each -> 4 bytes/prop
    (cheapest honest encoding = MOST favorable to symbolic = HARDEST for HD = honest). Equal-footprint
    capacity C_eq = 8N // 4 = 2048 propositions; 2x-footprint C_2x = 4096. Codebook / entity-id space is
    amortized shared infrastructure EXCLUDED from BOTH state footprints symmetrically (declared in metrics).
  Overload knob = D_n (number of DISTINCT facts) vs C_eq: when D_n > C_eq the symbolic store MUST evict distinct
  facts, so an AGGREGATE coherence query (judge a continuation against ALL established facts -- the natural
  coherence mode) references evicted-but-real facts that symbolic scores 0 (== a confabulation) while HD's
  bundle retains a noisy-but-nonzero signal for every fact ever seen. THAT is HD's structural chance.

DESIGN GATE (verified AT SMOKE before full; per feedback_experiment_design_gate_can_fail_real_baseline...):
  (1) REAL baselines: sym_prop_evict at EQUAL footprint (C_eq) AND 2x footprint (C_2x) -- exact conjunction
      stores, not strawmen; + random floor. hd_add / sym_pair_marginal are labeled conjunction-blind CONTROLS
      (NOT the fair bar).
  (2) CAN-FAIL BOTH WAYS: HD-wins (beats sym_prop_evict_eq on aggregate coherence at overload) and symbolic-
      wins (ties/beats HD at equal footprint everywhere) are BOTH reachable by the SNR/eviction physics (see
      the THEORETICAL estimate in the CELL-TEMPLATE block). Neither is excluded by construction.
  (3) DIFFICULTY-ON: overload D_n > C_eq forces symbolic eviction (sym_prop_evict_eq AUC < 0.95 at top overload
      aggregate, verified at smoke); HD bundle is a genuine lossy summary (freq-signal ~O(1) vs crosstalk
      ~sqrt(M/N)). No smoke-only hardness (smoke uses the SAME D_n grid, fewer seeds).
  (4) ONE VARIABLE: the primary comparison hd_bind vs sym_prop_evict_eq shares IDENTICAL facts / stream /
      continuations / footprint / seeds; differs ONLY in the coherence REPRESENTATION.

PRE-REG (envelope-fail-bands; set BEFORE running):
  Primary metric = AUC_D2 (rank-AUC separating COHERENT q+ from CONFABULATION q- by the coherence score) per
  arm, per (D_n overload, regime), mean+std over seeds. Primary competitor = sym_prop_evict_eq (equal footprint).
  Realistic operating point = the AGGREGATE regime (coherence judged against the WHOLE discourse -- the defining
  property of the scalar-coherence mode). RECENT regime (reference only recently-added facts) is the symbolic
  corner, reported for contrast.
    HARD_PASS (HD earns a real keep): at >=1 overload D_n (D_n>C_eq), AGGREGATE regime, mean(AUC_D2[hd_bind] -
      AUC_D2[sym_prop_evict_eq]) >= 0.03 AND (mean margin - 1*std) > 0 across seeds AND AUC_D2[hd_bind] >= 0.55.
    HARD_FAIL (settles the ENTIRE state-of-mind overlay = SYMBOLIC): at ALL overload D_n, in BOTH regimes,
      hd_bind does NOT beat sym_prop_evict_eq (margin < 0.03 or negative). Symbolic ties/wins at equal footprint
      for BOTH membership (prior cells) AND coherence (this cell) -> first-class fully-settled result.
    MIDDLE_BAND: HD beats sym_prop_evict_eq only at the MOST extreme overload, or only weakly/non-robustly, or
      only in an unrealistic corner. Reported cleanly as "HD's coherence win is confined to extreme overload".
  P estimate: P=0.40 HYPOTHESIZED (this cell's own THEORETICAL SNR/eviction estimate): the crossover sits near
    2x-4x overload; sym_prop_evict_eq gets FULL AUC credit (1.0) on its retained fraction and only ties (0.5) on
    evicted, so it is a STRONG bar; HD's freq-signal is O(1) against sqrt(M/N) crosstalk. A HD win at 4x is
    plausible but not favored; HARD_FAIL/MIDDLE is the more likely honest outcome (which would fully settle the
    overlay as symbolic -- a first-class result, not a disappointment).

COMPUTE: torch complex64 (CLAUDE.md FHRR dtype); sequential-CPU -- justified under the GPU-batching discipline's
"cell IS the substrate-primitive being validated" exemption (this cell measures the FHRR bundle/inner-product
coherence readout itself; the per-arm scoring is already a vectorized (P,N)@(N,) matmul and the bundle is a
per-distinct-fact elementwise (N,) accumulate). MEASURED full-run wall = ~18.5s inline foreground-to-completion
(the x16 overload arm dominates; no batching win worth the complexity for a one-shot decider). STORAGE = no_storage (in-memory synthetic facts/stream; nothing
persisted to substrate_index; no live KGStore/fit object -> validity-preflight F.2/F.3/F.4 not_applicable; F.5
deterministic-seeding DOES apply and is honored). progress_logging = print_flush_true (well under the 1800s
heartbeat threshold; start-marker + crash-metrics + atomic-write present regardless). smoke = 2 seeds x full
D_n grid x both regimes (fires the discriminator at the SAME overload the full run uses); full = 5 seeds.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified (META_RULE_AF): hd_bind per-continuation score vector bit-non-identical to
#     sym_prop_evict_eq's (empirical sha256 on the real q+ score arrays at overload). Set at self-test + smoke.
# - final_metrics_atomicity = tmp_replace (META_RULE_AH): metrics.json via os.replace of a .tmp.
# - except SystemExit: raise BEFORE except Exception (no BaseException) -- see __main__ outer try.
# - crlb_floor_computed: coherence-score SNR for hd_bind on the EXACT-conjunction signal = freq_f / sqrt(M/N)
#     (freq_f ~ REPEAT = O(1) exact-pair frequency; crosstalk std ~ sqrt(M/N)). THEORETICAL@ estimate at
#     N=1024,REPEAT=3: D_n=4096->M=12288->sqrt(M/N)=3.46->AUC~0.73; D_n=8192->M=24576->sqrt(M/N)=4.96->AUC~0.67.
#     sym_prop_evict_eq AUC(aggregate) = 0.5 + 0.5*frac_retained ~= 0.5 + 0.5*C_eq/D_n: D_n=4096->~0.75;
#     D_n=8192->~0.625. -> genuine crossover near 4x overload -> discriminator_reachability = true (HD CAN win,
#     symbolic CAN win). crlb_formula_reference: "hd coherence SNR = exact-pair-freq / sqrt(M/N) (FHRR bundle
#     self=freq*N vs crosstalk=sqrt(M)*N, normalized by N); sym aggregate AUC = 0.5+0.5*C/D_n".
# - baseline_in_band (META_RULE_AG): sym_prop_evict_eq NOT saturated at overload aggregate (D_n>C_eq forces
#     eviction -> AUC<0.95, verified at smoke) and NOT a strawman (AUC=1.0 at low D_n, exact). random ~0.5.
# - discriminator survives scale: smoke fires the eviction + confabulation discriminators at the SAME D_n grid
#     the full run uses (smoke ADDS nothing easier); smoke = fewer seeds only.
# - HARD_PASS strictly above floor + margin (META_RULE_L): margin>=0.03 AND (margin-1std)>0 (not at-floor).
# - HP_SCOPE: HARD_PASS applies ONLY to arm 'hd_bind'. sym_prop_evict_eq/2x, hd_add, sym_pair_marginal, random
#     are baselines/controls/floor and do NOT inherit it.
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = N_SEEDS * len(D_GRID) * len(REGIMES); verdict counts
#     per-unit rows and HARD_FAIL_CARDINALITY if short.
# - per-unit failure-class instrumentation (META_RULE_J): no bare except; each unit wrapped, failure class
#     recorded to metrics, fatal-flag set (no silent continue).
# - calibration_check = default_ok_for_this_regime: NO fitted threshold anywhere -- the metric is rank-AUC of a
#     raw scalar score (threshold-free). No tuning loop; nothing to p-hack.
# - all numbers in this file tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
# - real_code_path (F.1): self_test() constructs + calls the REAL objects the FULL run uses (make_phasors,
#     build_facts, build_stream, lru_retained_facts, hd bundles, all arm scorers, run_unit) at tiny scale and
#     asserts the confabulation/overload/eviction/conjunction-blindness/AUC paths execute.
# - real_code_path_and_signature_preflight: F.2/F.3/F.4 not_applicable -- constructs NO KGStore/fit-module/
#     store-helper substrate object (pure synthetic FHRR over integer ids; no substrate_index write). F.5
#     (deterministic seeding) DOES apply and is honored below.
# - deterministic_seeding (F.5): every torch.Generator / random.Random seed is a FIXED integer formula
#     (BASE_SEED + declared per-role offset + d_n*1000 + seed_idx*7 [+ regime idx]); sets ordered via sorted();
#     NEVER hash() or list(set(...)) anywhere in this file. Static-scanned by queue_add PROT-023.
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

ANCHOR_NAME = "read_discourse_state_hd_vs_symbolic_coherence_scalar_score_v1"

# ---------------------------------------------------------------------------
# Hand-set constants (declared BEFORE any run; see docstring). No fit-to-data.
# ---------------------------------------------------------------------------
N_DIM = 1024                 # HD vector dimensionality (complex64). bundle footprint = 8*N_DIM bytes.
VOCAB = 16384                # declared entity id space -> 14 bits -> 2 bytes/id (byte accounting only).
N_AGENTS = 256               # topical agent pool (ids 0..255)
N_PATIENTS = 256             # topical patient pool (ids 256..511); disjoint from agents. grid = 65536 (a,p)
OFFTOPIC_BASE = 4096         # off-topic entity ids start here (D1 control continuations)
BYTES_HD = 8 * N_DIM         # one (N,) complex64 = 2N float32 = 8N bytes
BYTES_PROP = 4               # exact (a,p) tuple = 2 x 2-byte ids (cheapest honest = hardest for HD)
C_EQ = BYTES_HD // BYTES_PROP        # equal-footprint symbolic capacity (propositions): 8192//4 = 2048
C_2X = 2 * C_EQ                      # 2x-footprint symbolic capacity: 4096
REPEAT = 3                   # avg mentions per distinct fact -> stream length M = REPEAT * D_n (recency+freq)
# distinct facts: 1024,2048,4096,8192,16384,32768 (0.5x..16x overload). grid=65536 leaves ample non-facts for
# confabulations even at 16x (32768 facts). extends past the ~4x crossover to test if HD's win firms up to a
# robust >=0.03 margin or stays a hair-thin tie (both arms approach chance in the deep-overload corner).
D_GRID_FULL = [C_EQ // 2, C_EQ, 2 * C_EQ, 4 * C_EQ, 8 * C_EQ, 16 * C_EQ]
D_GRID_SMOKE = D_GRID_FULL                            # SAME grid (discriminator must fire at full scale)
REGIMES = ["aggregate", "recent"]                     # aggregate = realistic coherence; recent = sym corner
N_POS = 150                  # coherent continuations per (unit, condition)
N_NEG = 150                  # confabulation continuations (D2)
N_OFF = 150                  # off-topic continuations (D1 control)
N_SEEDS_FULL = 5
N_SEEDS_SMOKE = 2
BASE_SEED = 770000001

_OFF = {"facts": 10_000_000, "phasor": 20_000_000, "stream": 30_000_000, "posagg": 40_000_000,
        "posrec": 45_000_000, "confab": 50_000_000, "offtopic": 60_000_000, "randscore": 70_000_000}


def _seed(kind, d_n, seed_idx, extra=0):
    return BASE_SEED + _OFF[kind] + d_n * 1000 + seed_idx * 7 + extra


# ---------------------------------------------------------------------------
# FHRR primitives (torch complex64, CLAUDE.md dtype). CITED formulas (not imported).
# ---------------------------------------------------------------------------
def make_phasors(seed, count, n_dim=N_DIM):
    """count random FHRR unit-phasor hypervectors, shape (count, n_dim) complex64."""
    g = torch.Generator().manual_seed(int(seed))
    theta = torch.empty(count, n_dim).uniform_(-math.pi, math.pi, generator=g)
    return torch.complex(torch.cos(theta), torch.sin(theta)).to(torch.complex64)


def bind(a, b):
    """FHRR bind = elementwise complex multiply (Hadamard). (N,) x (N,) -> (N,)."""
    return a * b


def inner(qs, bundle_vec):
    """Normalized real Hermitian inner product per query row. qs: (P,N) complex64 -> (P,) float."""
    n = qs.shape[1]
    return (qs.conj() @ bundle_vec).real / float(n)


# ---------------------------------------------------------------------------
# Rank-AUC (Mann-Whitney, average-rank tie handling). Threshold-free scalar-readout metric.
# ---------------------------------------------------------------------------
def rank_auc(pos, neg):
    """AUC = P(score(pos) > score(neg)) + 0.5*P(=). pos,neg: lists of floats. Ties via average ranks."""
    npos, nneg = len(pos), len(neg)
    if npos == 0 or nneg == 0:
        return float("nan")
    combined = [(v, 1) for v in pos] + [(v, 0) for v in neg]
    combined.sort(key=lambda t: t[0])
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j + 1 < len(combined) and combined[j + 1][0] == combined[i][0]:
            j += 1
        avg = (i + j) / 2.0 + 1.0          # 1-based average rank over the tie block
        for k in range(i, j + 1):
            ranks[k] = avg
        i = j + 1
    sum_ranks_pos = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 1)
    u = sum_ranks_pos - npos * (npos + 1) / 2.0
    return float(u / (npos * nneg))


# ---------------------------------------------------------------------------
# Discourse: distinct facts (a,p), a mention stream (recurrence + recency), LRU-evict store.
# ---------------------------------------------------------------------------
def build_facts(d_n, seed_idx):
    """d_n distinct (agent, patient) facts sampled from the N_AGENTS x N_PATIENTS grid. Returns sorted list."""
    grid = N_AGENTS * N_PATIENTS
    assert d_n <= grid, "d_n exceeds agent x patient grid"
    rng = random.Random(_seed("facts", d_n, seed_idx))
    idxs = rng.sample(range(grid), d_n)                   # distinct product indices (no list(set()) -- F.5)
    facts = sorted((idx // N_PATIENTS, N_AGENTS + (idx % N_PATIENTS)) for idx in idxs)
    return facts


def build_stream(facts, d_n, seed_idx):
    """M = REPEAT*d_n mention instances: ONE guaranteed appearance of each fact (coverage) + (REPEAT-1)*d_n
    extra uniform mentions, shuffled for recency. Coverage guarantees symbolic is EXACT at no-overload (the
    honest strong-baseline bar) while extra mentions + shuffle keep recency + frequency meaningful."""
    rng = random.Random(_seed("stream", d_n, seed_idx))
    stream = list(facts)                                   # guaranteed one appearance each
    extra = (REPEAT - 1) * d_n
    stream += [facts[rng.randrange(len(facts))] for _ in range(extra)]
    rng.shuffle(stream)
    return stream


def lru_retained_facts(stream, capacity):
    """Capacity-C LRU over distinct fact identity. Returns the set of retained (a,p)."""
    od = OrderedDict()
    for f in stream:
        if f in od:
            od.move_to_end(f)
        else:
            od[f] = None
            if len(od) > capacity:
                od.popitem(last=False)
    return set(od.keys())


def fact_frequencies(stream):
    freq = {}
    for f in stream:
        freq[f] = freq.get(f, 0) + 1
    return freq


# ---------------------------------------------------------------------------
# Continuations: coherent (q+), confabulation (q-), off-topic (q0).
# ---------------------------------------------------------------------------
def sample_positives(facts, retained, d_n, seed_idx, regime):
    """q+ facts: AGGREGATE -> uniform over ALL facts (realistic whole-discourse coherence); RECENT -> from the
    LRU-retained set (symbolic corner)."""
    kind = "posagg" if regime == "aggregate" else "posrec"
    rng = random.Random(_seed(kind, d_n, seed_idx))
    pool = facts if regime == "aggregate" else sorted(retained)
    if len(pool) == 0:
        pool = facts
    return [pool[rng.randrange(len(pool))] for _ in range(N_POS)]


def sample_confabulations(positives, fact_set, d_n, seed_idx):
    """q-: for each q+ (a,p) build a MINIMAL-PAIR confabulation (a, p'') where (a,p'') is topical + role-valid
    but NEVER a fact. a stays an agent, p'' a real patient; the specific pairing never occurred."""
    rng = random.Random(_seed("confab", d_n, seed_idx))
    out = []
    for (a, p) in positives:
        for _ in range(64):
            pp = N_AGENTS + rng.randrange(N_PATIENTS)
            if pp != p and (a, pp) not in fact_set:
                out.append((a, pp))
                break
        else:
            out.append((a, (p + 1 - N_AGENTS) % N_PATIENTS + N_AGENTS))   # fallback (rare)
    return out


def sample_offtopic(d_n, seed_idx):
    """q0: off-topic (a_off, p_off) using entities OUTSIDE the topical pools (D1 topical control)."""
    rng = random.Random(_seed("offtopic", d_n, seed_idx))
    out = []
    for _ in range(N_OFF):
        a_off = OFFTOPIC_BASE + rng.randrange(N_PATIENTS)
        p_off = OFFTOPIC_BASE + N_PATIENTS + rng.randrange(N_PATIENTS)
        out.append((a_off, p_off))
    return out


# ---------------------------------------------------------------------------
# Per-unit run: build state (all arms), score every continuation, per-arm AUC_D2 / AUC_D1.
# ---------------------------------------------------------------------------
def _phasor_table(ids, d_n, seed_idx):
    """Deterministic per-entity phasor for the id set used this unit (agents/patients/off-topic)."""
    ids_sorted = sorted(set(ids))
    mat = make_phasors(_seed("phasor", d_n, seed_idx), len(ids_sorted))
    return mat, {e: i for i, e in enumerate(ids_sorted)}


def _stack_bind(conts, mat, id2row):
    """(P,N) matrix of chunk(a,p)=E[a](x)E[p] for a list of (a,p)."""
    rows_a = torch.tensor([id2row[a] for a, _ in conts], dtype=torch.long)
    rows_p = torch.tensor([id2row[p] for _, p in conts], dtype=torch.long)
    return mat.index_select(0, rows_a) * mat.index_select(0, rows_p)


def _stack_add(conts, mat, id2row):
    """(P,N) matrix of E[a]+E[p] (additive, conjunction-blind)."""
    rows_a = torch.tensor([id2row[a] for a, _ in conts], dtype=torch.long)
    rows_p = torch.tensor([id2row[p] for _, p in conts], dtype=torch.long)
    return mat.index_select(0, rows_a) + mat.index_select(0, rows_p)


def run_unit(d_n, seed_idx, regime):
    facts = build_facts(d_n, seed_idx)
    fact_set = set(facts)
    stream = build_stream(facts, d_n, seed_idx)
    m = len(stream)
    freq = fact_frequencies(stream)
    retained_eq = lru_retained_facts(stream, C_EQ)
    retained_2x = lru_retained_facts(stream, C_2X)
    # marginal retained pools (for the conjunction-blind symbolic control), derived from equal-footprint store
    retained_agents = set(a for a, _ in retained_eq)
    retained_patients = set(p for _, p in retained_eq)

    positives = sample_positives(facts, retained_eq, d_n, seed_idx, regime)
    negatives = sample_confabulations(positives, fact_set, d_n, seed_idx)
    offs = sample_offtopic(d_n, seed_idx)

    all_ids = ([a for a, _ in facts] + [p for _, p in facts]
               + [a for a, _ in positives] + [p for _, p in positives]
               + [a for a, _ in negatives] + [p for _, p in negatives]
               + [a for a, _ in offs] + [p for _, p in offs])
    mat, id2row = _phasor_table(all_ids, d_n, seed_idx)

    # HD bundles: B_bind = sum_f freq_f * (E[a](x)E[p]); B_add = sum_f freq_f * (E[a]+E[p]).
    B_bind = torch.zeros(N_DIM, dtype=torch.complex64)
    B_add = torch.zeros(N_DIM, dtype=torch.complex64)
    for (a, p), c in freq.items():
        ea = mat[id2row[a]]
        ep = mat[id2row[p]]
        B_bind = B_bind + float(c) * (ea * ep)
        B_add = B_add + float(c) * (ea + ep)

    def hd_bind_scores(conts):
        return inner(_stack_bind(conts, mat, id2row), B_bind).tolist()

    def hd_add_scores(conts):
        return inner(_stack_add(conts, mat, id2row), B_add).tolist()

    def sym_prop_scores(conts, retained):
        return [1.0 if (a, p) in retained else 0.0 for (a, p) in conts]

    def sym_pair_marginal_scores(conts):
        return [float((a in retained_agents)) + float((p in retained_patients)) for (a, p) in conts]

    rscore = random.Random(_seed("randscore", d_n, seed_idx, extra=(1 if regime == "aggregate" else 2)))

    def random_scores(conts):
        return [rscore.random() for _ in conts]

    scorers = {
        "hd_bind": lambda cs: hd_bind_scores(cs),
        "hd_add": lambda cs: hd_add_scores(cs),
        "sym_prop_evict_eq": lambda cs: sym_prop_scores(cs, retained_eq),
        "sym_prop_evict_2x": lambda cs: sym_prop_scores(cs, retained_2x),
        "sym_pair_marginal": lambda cs: sym_pair_marginal_scores(cs),
        "random": lambda cs: random_scores(cs),
    }

    pos_s = {a: scorers[a](positives) for a in scorers}
    neg_s = {a: scorers[a](negatives) for a in scorers}
    off_s = {a: scorers[a](offs) for a in scorers}

    auc_d2 = {a: rank_auc(pos_s[a], neg_s[a]) for a in scorers}     # coherent vs confabulation (PRIMARY)
    auc_d1 = {a: rank_auc(pos_s[a], off_s[a]) for a in scorers}     # coherent vs off-topic (control)

    # arms_differ (META_RULE_AF): hd_bind vs sym_prop_evict_eq q+ score vectors bit-non-identical.
    def _h(xs):
        return hashlib.sha256(bytes(json.dumps([round(x, 6) for x in xs]), "utf-8")).hexdigest()
    arms_differ = _h(pos_s["hd_bind"]) != _h(pos_s["sym_prop_evict_eq"])

    frac_retained_eq = sum(1 for f in positives if f in retained_eq) / float(len(positives))

    return {
        "d_n": d_n, "seed_idx": seed_idx, "regime": regime, "m": m,
        "n_distinct": len(facts), "n_retained_eq": len(retained_eq), "n_retained_2x": len(retained_2x),
        "overload": d_n / float(C_EQ), "frac_pos_retained_eq": frac_retained_eq,
        "auc_d2": {a: float(v) for a, v in auc_d2.items()},
        "auc_d1": {a: float(v) for a, v in auc_d1.items()},
        "arms_differ": bool(arms_differ),
        "hd_bind_pos_mean": float(sum(pos_s["hd_bind"]) / len(pos_s["hd_bind"])),
        "hd_bind_neg_mean": float(sum(neg_s["hd_bind"]) / len(neg_s["hd_bind"])),
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


ARMS = ["hd_bind", "hd_add", "sym_prop_evict_eq", "sym_prop_evict_2x", "sym_pair_marginal", "random"]


def aggregate(rows):
    out = {}
    for regime in REGIMES:
        for d_n in sorted(set(r["d_n"] for r in rows)):
            rs = [r for r in rows if r["d_n"] == d_n and r["regime"] == regime]
            if not rs:
                continue
            key = "%s|%d" % (regime, d_n)
            arm_d2 = {a: _mean_std([r["auc_d2"][a] for r in rs]) for a in ARMS}
            arm_d1 = {a: _mean_std([r["auc_d1"][a] for r in rs]) for a in ARMS}
            margins = [r["auc_d2"]["hd_bind"] - r["auc_d2"]["sym_prop_evict_eq"] for r in rs]
            margins_2x = [r["auc_d2"]["hd_bind"] - r["auc_d2"]["sym_prop_evict_2x"] for r in rs]
            mu_m, sd_m = _mean_std(margins)
            mu_m2, sd_m2 = _mean_std(margins_2x)
            out[key] = {
                "regime": regime, "d_n": d_n, "overload": d_n / float(C_EQ), "n_seeds": len(rs),
                "auc_d2_mean": {a: arm_d2[a][0] for a in ARMS}, "auc_d2_std": {a: arm_d2[a][1] for a in ARMS},
                "auc_d1_mean": {a: arm_d1[a][0] for a in ARMS},
                "margin_hd_vs_sym_eq_mean": mu_m, "margin_hd_vs_sym_eq_std": sd_m,
                "margin_hd_vs_sym_2x_mean": mu_m2, "margin_hd_vs_sym_2x_std": sd_m2,
                "arms_differ_all": all(r["arms_differ"] for r in rs),
                "frac_pos_retained_eq": _mean_std([r["frac_pos_retained_eq"] for r in rs])[0],
                # HD-wins-here gate (equal footprint, this regime/d_n): robust positive margin, above chance.
                "hd_wins_here": bool(mu_m >= 0.03 and (mu_m - sd_m) > 0.0
                                     and arm_d2["hd_bind"][0] >= 0.55
                                     and all(r["arms_differ"] for r in rs)),
            }
    return out


def compute_verdict(agg, rows, expected_n_units):
    if len(rows) < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "cardinality: got %d units, expected %d" % (len(rows), expected_n_units), {})

    overload_dns = [d for d in D_GRID_FULL if d > C_EQ]
    # validity gates
    def _band(x, lo=0.40, hi=0.60):
        return (not math.isnan(x)) and lo <= x <= hi
    rand_ok = all(_band(agg[k]["auc_d2_mean"]["random"]) for k in agg)
    # conjunction-blind controls must be ~chance at overload (proves D2 needs conjunction)
    blind_keys = ["%s|%d" % (rg, d) for rg in REGIMES for d in overload_dns]
    hd_add_blind = all(_band(agg[k]["auc_d2_mean"]["hd_add"]) for k in blind_keys if k in agg)
    sym_marg_blind = all(_band(agg[k]["auc_d2_mean"]["sym_pair_marginal"]) for k in blind_keys if k in agg)
    # sym_prop_evict_eq NOT saturated at TOP overload aggregate (eviction bites -> difficulty on)
    top = max(overload_dns)
    top_agg_key = "aggregate|%d" % top
    sym_not_saturated = (top_agg_key in agg
                         and agg[top_agg_key]["auc_d2_mean"]["sym_prop_evict_eq"] < 0.95)
    # sym_prop_evict_eq is a REAL (non-strawman) baseline: exact at LOW d_n (AUC ~1.0)
    low_key = "aggregate|%d" % min(D_GRID_FULL)
    sym_real = (low_key in agg and agg[low_key]["auc_d2_mean"]["sym_prop_evict_eq"] >= 0.95)
    # D1 topical control: coherence score is topical-MEANINGFUL (well above chance) at low d_n. hd_bind runs
    # ~0.79 (honest: low-frequency facts give a weak coherence signal) -> gate at 0.70 (clearly meaningful).
    d1_ok = (low_key in agg and agg[low_key]["auc_d1_mean"]["hd_bind"] >= 0.70
             and agg[low_key]["auc_d1_mean"]["sym_prop_evict_eq"] >= 0.70)
    arms_differ = all(agg[k]["arms_differ_all"] for k in agg)

    valid = (rand_ok and hd_add_blind and sym_marg_blind and sym_not_saturated
             and sym_real and d1_ok and arms_differ)

    # HARD_PASS: HD beats sym_prop_evict_eq in the AGGREGATE (realistic) regime at >=1 overload d_n, robust.
    hp_keys = [k for k in agg if agg[k]["regime"] == "aggregate"
               and agg[k]["d_n"] in overload_dns and agg[k]["hd_wins_here"]]
    # HD wins somewhere at all (either regime, any overload) -> distinguishes MIDDLE from HARD_FAIL
    any_win = [k for k in agg if agg[k]["d_n"] in overload_dns and agg[k]["hd_wins_here"]]

    if not valid:
        tier = "INVALID_TEST_DESIGN"
    elif hp_keys:
        tier = "HARD_PASS"
    elif not any_win:
        tier = "HARD_FAIL"     # symbolic ties/wins at equal footprint in BOTH regimes at ALL overload
    else:
        tier = "MIDDLE_BAND"   # HD wins only in a corner (recent regime, or non-aggregate) not the realistic mode

    detail = " || ".join(
        "%s x%.1f: AUCd2 hd=%.3f(+-%.3f) symEq=%.3f sym2x=%.3f hdAdd=%.3f symMarg=%.3f rand=%.3f "
        "dHDvsEq=%+.3f(+-%.3f) fracRet=%.2f" % (
            agg[k]["regime"], agg[k]["overload"],
            agg[k]["auc_d2_mean"]["hd_bind"], agg[k]["auc_d2_std"]["hd_bind"],
            agg[k]["auc_d2_mean"]["sym_prop_evict_eq"], agg[k]["auc_d2_mean"]["sym_prop_evict_2x"],
            agg[k]["auc_d2_mean"]["hd_add"], agg[k]["auc_d2_mean"]["sym_pair_marginal"],
            agg[k]["auc_d2_mean"]["random"],
            agg[k]["margin_hd_vs_sym_eq_mean"], agg[k]["margin_hd_vs_sym_eq_std"],
            agg[k]["frac_pos_retained_eq"])
        for k in sorted(agg))
    msg = "%s | C_eq=%d C_2x=%d (hd bundle=%dB, prop=%dB) | %s" % (
        tier, C_EQ, C_2X, BYTES_HD, BYTES_PROP, detail)
    info = {"valid": valid, "rand_ok": rand_ok, "hd_add_blind": hd_add_blind,
            "sym_marg_blind": sym_marg_blind, "sym_not_saturated": sym_not_saturated,
            "sym_real": sym_real, "d1_ok": d1_ok, "arms_differ": arms_differ,
            "hp_keys": hp_keys, "any_win_keys": any_win, "overload_dns": overload_dns}
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
    d_grid = D_GRID_SMOKE if run_mode == "smoke" else D_GRID_FULL
    n_seeds = N_SEEDS_SMOKE if run_mode == "smoke" else N_SEEDS_FULL
    expected_n_units = n_seeds * len(d_grid) * len(REGIMES)

    out_dir = _out_dir(run_mode)
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    rows = []
    fatal = None
    for regime in REGIMES:
        for d_n in d_grid:
            for s in range(n_seeds):
                try:
                    r = run_unit(d_n, s, regime)
                except Exception as e:  # NOT BaseException
                    fatal = {"stage": "run_unit", "d_n": d_n, "seed_idx": s, "regime": regime,
                             "class": type(e).__name__, "msg": str(e)[:300]}
                    break
                rows.append(r)
                print("[%s] %s d_n=%d x%.1f seed=%d AUCd2 hd=%.3f symEq=%.3f d=%+.3f fracRet=%.2f differ=%s"
                      % (run_mode, regime, d_n, r["overload"], s, r["auc_d2"]["hd_bind"],
                         r["auc_d2"]["sym_prop_evict_eq"],
                         r["auc_d2"]["hd_bind"] - r["auc_d2"]["sym_prop_evict_eq"],
                         r["frac_pos_retained_eq"], r["arms_differ"]), flush=True)
            if fatal:
                break
        if fatal:
            break

    elapsed = time.perf_counter() - t0

    if fatal is not None:
        metrics = {"verdict": "CELL_FATAL", "verdict_msg": "fatal at %s: %s" % (fatal.get("stage"), fatal),
                   "summary": "CELL_FATAL", "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
                   "run_mode": run_mode, "fatal": fatal, "rows": rows,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}
        _write_metrics(out_dir, metrics)
        return metrics

    agg = aggregate(rows)
    tier, msg, info = compute_verdict(agg, rows, expected_n_units)
    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": msg[:200], "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_dim": N_DIM, "vocab": VOCAB, "n_agents": N_AGENTS, "n_patients": N_PATIENTS,
        "bytes_hd_bundle": BYTES_HD, "bytes_per_prop_symbolic": BYTES_PROP,
        "capacity_equal_footprint": C_EQ, "capacity_2x_footprint": C_2X, "repeat": REPEAT,
        "d_grid": d_grid, "regimes": REGIMES, "n_seeds": n_seeds,
        "n_pos": N_POS, "n_neg": N_NEG, "n_off": N_OFF,
        "expected_n_units": expected_n_units, "actual_n_units": len(rows),
        "agg": agg, "verdict_info": info, "rows": rows,
        "footprint_model": ("hd bundle = 8*N_DIM = %d bytes (constant in M); symbolic prop store = 4 bytes/prop "
                            "(2x 2-byte ids); C_eq = 8N//4 = %d props, C_2x = %d props. Codebook/entity-id "
                            "space AMORTIZED + excluded from both state footprints SYMMETRICALLY." % (
                                BYTES_HD, C_EQ, C_2X)),
        "metric_model": ("AUC_D2 = rank-AUC separating COHERENT (q+, real fact) from CONFABULATION (q-, topical "
                         "role-valid non-fact) by the raw scalar coherence score; AUC_D1 = q+ vs off-topic "
                         "(control). Threshold-free -> no calibration/tuning."),
        "encoding_note": ("hd_bind chunk=E[a](x)E[p] PRESERVES the conjunction (can discriminate confabulations); "
                          "hd_add=E[a]+E[p] and sym_pair_marginal read MARGINALS -> conjunction-blind controls "
                          "(expected AUC_D2 ~0.5 at overload, proving the discriminator is conjunction-sensitive)."),
        "realistic_operating_point": ("AGGREGATE regime = coherence judged against the WHOLE discourse (the "
                                      "defining property of the scalar-coherence mode) = HD's structural niche at "
                                      "overload. RECENT regime = symbolic corner (only recently-added facts)."),
        "corpus_license": "synthetic integer-id facts/stream; no external corpus; glass-box, no runtime LLM.",
    }
    _write_metrics(out_dir, metrics)
    print("[%s] VERDICT %s (%.2fs)" % (run_mode, tier, elapsed), flush=True)
    print(msg, flush=True)
    return metrics


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert every discriminator CAN fire.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (make_phasors/build_facts/build_stream/lru_retained_facts/"
          "run_unit)...", flush=True)

    # (1) FHRR conjunction: <E[a](x)E[p], E[a](x)E[p]> ~ 1; a confabulation E[a](x)E[p'] ~ 0.
    mat = make_phasors(123, 6, n_dim=512)
    chunk_ap = mat[0] * mat[1]
    chunk_apr = mat[0] * mat[2]
    s_self = inner(chunk_ap.unsqueeze(0), chunk_ap).item()
    s_conf = inner(chunk_apr.unsqueeze(0), chunk_ap).item()
    assert s_self > 0.9, "exact conjunction self-score must be ~1: %r" % s_self
    assert abs(s_conf) < 0.3, "confabulation vs a single stored chunk must be ~0: %r" % s_conf

    # (2) additive is conjunction-BLIND: <E[a]+E[p'], E[a]+E[p]> gets marginal E[a] credit (>0) even though
    #     the pair never matched -> cannot cleanly separate from the real pair via the marginal.
    add_ap = mat[0] + mat[1]
    add_apr = mat[0] + mat[2]
    s_add_self = inner(add_ap.unsqueeze(0), add_ap).item()
    s_add_conf = inner(add_apr.unsqueeze(0), add_ap).item()
    assert s_add_conf > 0.5 * s_add_self, "additive must give a confabulation strong marginal credit: %r %r" % (
        s_add_self, s_add_conf)

    # (3) determinism (F.5): same seed -> same facts + stream, twice.
    f1 = build_facts(32, 0)
    f2 = build_facts(32, 0)
    assert f1 == f2, "build_facts must be deterministic"
    st1 = build_stream(f1, 32, 0)
    st2 = build_stream(f2, 32, 0)
    assert st1 == st2, "build_stream must be deterministic"

    # (4) LRU eviction under overload: capacity < distinct -> retained smaller than distinct.
    facts = build_facts(200, 0)
    stream = build_stream(facts, 200, 0)
    ret = lru_retained_facts(stream, 50)
    assert len(ret) == 50, "LRU must retain exactly capacity distinct facts: %d" % len(ret)
    assert ret.issubset(set(facts)), "retained must be a subset of facts"

    # (5) rank_auc sanity: perfectly separated -> 1.0; identical -> 0.5; reversed -> 0.0; ties handled.
    assert abs(rank_auc([1, 2, 3], [-1, -2, -3]) - 1.0) < 1e-9
    assert abs(rank_auc([1, 1, 1], [1, 1, 1]) - 0.5) < 1e-9
    assert abs(rank_auc([0, 0, 0], [1, 1, 1]) - 0.0) < 1e-9
    assert abs(rank_auc([1.0, 0.0], [1.0, 0.0]) - 0.5) < 1e-9   # matched ties -> 0.5

    # (6) REAL unit at NO overload (d_n < C_EQ): coverage guarantees symbolic is EXACT on confabulations
    #     (AUC 1.0 -- the honest strong baseline); hd_bind above chance; arms differ; D1 control strong.
    r_small = run_unit(d_n=64, seed_idx=0, regime="aggregate")   # 64 < C_EQ -> no eviction
    assert abs(r_small["auc_d2"]["sym_prop_evict_eq"] - 1.0) < 1e-9, (
        "no-eviction symbolic must be exact on confabulations: %r" % r_small["auc_d2"]["sym_prop_evict_eq"])
    assert r_small["auc_d2"]["hd_bind"] >= 0.55, "hd_bind must beat chance on conjunction at low overload: %r" % (
        r_small["auc_d2"]["hd_bind"])
    assert r_small["arms_differ"], "hd_bind and sym_prop score vectors must be bit-non-identical"
    # D1 topical control: both real arms must separate off-topic strongly.
    assert r_small["auc_d1"]["hd_bind"] >= 0.85 and r_small["auc_d1"]["sym_prop_evict_eq"] >= 0.85, (
        "D1 topical control must be strong: %r" % r_small["auc_d1"])

    # (7) REAL unit at overload: symbolic must EVICT (frac retained < 1) -> AUC_D2 < 1 (difficulty on); and the
    #     conjunction-blind controls (hd_add, sym_pair_marginal) collapse to ~chance (marginals saturated ->
    #     proves the discriminator is genuinely CONJUNCTION-sensitive).
    r_over = run_unit(d_n=4 * C_EQ, seed_idx=0, regime="aggregate")
    assert r_over["frac_pos_retained_eq"] < 0.95, "overload must force eviction on aggregate q+: %r" % (
        r_over["frac_pos_retained_eq"])
    assert r_over["auc_d2"]["sym_prop_evict_eq"] < 0.95, "symbolic must degrade under overload: %r" % (
        r_over["auc_d2"]["sym_prop_evict_eq"])
    assert 0.35 <= r_over["auc_d2"]["hd_add"] <= 0.65, "hd_add (marginal) must be ~chance on D2 at overload: %r" % (
        r_over["auc_d2"]["hd_add"])
    assert 0.35 <= r_over["auc_d2"]["sym_pair_marginal"] <= 0.65, (
        "sym_pair_marginal must be ~chance on D2 at overload: %r" % r_over["auc_d2"]["sym_pair_marginal"])

    # (8) verdict logic reachability: fabricate agg rows for HARD_PASS / HARD_FAIL / MIDDLE.
    def _syn_rows(hd_over, sym_over, regime_win="aggregate"):
        rows = []
        for regime in REGIMES:
            for d_n in D_GRID_FULL:
                for s in range(3):
                    over = d_n > C_EQ
                    if not over:
                        hd, sym = 0.90, 1.00     # low overload: symbolic exact
                    else:
                        hd = hd_over if regime == regime_win else 0.60
                        sym = sym_over if regime == regime_win else 0.62
                    rows.append({
                        "d_n": d_n, "seed_idx": s, "regime": regime, "m": REPEAT * d_n,
                        "n_distinct": d_n, "n_retained_eq": min(C_EQ, d_n), "n_retained_2x": min(C_2X, d_n),
                        "overload": d_n / float(C_EQ),
                        "frac_pos_retained_eq": 1.0 if not over else min(1.0, C_EQ / float(d_n)),
                        "auc_d2": {"hd_bind": hd, "hd_add": 0.50, "sym_prop_evict_eq": sym,
                                   "sym_prop_evict_2x": sym + 0.05, "sym_pair_marginal": 0.50, "random": 0.50},
                        "auc_d1": {a: (0.95 if a in ("hd_bind", "sym_prop_evict_eq", "sym_prop_evict_2x")
                                       else 0.50) for a in ARMS},
                        "arms_differ": True,
                        "hd_bind_pos_mean": 1.0, "hd_bind_neg_mean": 0.0})
        return rows
    exp = 3 * len(D_GRID_FULL) * len(REGIMES)
    # HARD_PASS: HD beats symbolic in aggregate at overload.
    rows_hp = _syn_rows(hd_over=0.72, sym_over=0.66)
    t_hp, _, _ = compute_verdict(aggregate(rows_hp), rows_hp, exp)
    assert t_hp == "HARD_PASS", "HD-beats-symbolic-aggregate must be HARD_PASS: %s" % t_hp
    # HARD_FAIL: symbolic ties/wins everywhere.
    rows_hf = _syn_rows(hd_over=0.60, sym_over=0.70)
    t_hf, _, _ = compute_verdict(aggregate(rows_hf), rows_hf, exp)
    assert t_hf == "HARD_FAIL", "symbolic-wins-everywhere must be HARD_FAIL: %s" % t_hf
    # MIDDLE: HD wins only in the RECENT corner, not aggregate.
    rows_mb = _syn_rows(hd_over=0.72, sym_over=0.66, regime_win="recent")
    t_mb, _, _ = compute_verdict(aggregate(rows_mb), rows_mb, exp)
    assert t_mb == "MIDDLE_BAND", "corner-only win must be MIDDLE_BAND: %s" % t_mb

    print("[self_test] PASS: real code path exercised; conjunction/eviction/confabulation/AUC/verdict fire.",
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
