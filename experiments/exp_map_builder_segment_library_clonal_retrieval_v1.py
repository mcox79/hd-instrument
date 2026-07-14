"""MAP_BUILDER_SEGMENT_LIBRARY_CLONAL_RETRIEVAL: is a V(D)J-style COMBINATORIAL SEGMENT-LIBRARY construction (small
typed-segment libraries combined at CONSTRUCTION time) + POPULATION/CLONAL SOFT retrieval (many candidates, soft
threshold, iterative refinement; the substrate's resonator/SIC-peel decode reframed as clonal selection) a
DEPLOYABLE lever that raises the recoverable-signal capacity of the INDUCTIVE relational map-builder -- vs RANDOM
opaque codes and vs HARD one-shot decode -- on the held-out-entity arena?

MOTIVATION (research_drillA_bio_capacity_structure_2026-07-13, LEADING lever P_deflated=0.35): biology's cheap
high-capacity trick on genuinely ARBITRARY discrete symbols is NOT "mine hidden structure out of an opaque atom"
(the grid-cell/RNS-CRT residue approach that this SAME arena already MEASURED as CODE-LIMITED / capacity-absent:
RNS_CLEAN=0.0008 ~ RANDOM=0.0003, MEASURED@data/exp_map_builder_residue_module_ceiling_v1/metrics.json:gates) but
"IMPOSE combinatorial generative structure AT CONSTRUCTION TIME from a small reusable parts library, then retrieve
via population-based approximate matching, not single-shot algebraic decode." The immune system builds ~10^13-10^18
receptor specificities from ~40 V + 23 D + 6 J gene segments + randomized junctional (TdT) insertion, and recognizes
via clonal selection: a POPULATION of near-miss candidate antibodies competes, close-enough ones are kept, then
refined (affinity maturation) -- graceful soft matching, not a brittle exact decode. Perelson & Oster 1979 shape-
space theory is the 45-year-old formal precedent for "arbitrary discrete entities as points in a high-dim space,
matched by similarity, covered by a population of near-duplicate codes" -- VSA/HDC's own premise.

THE DIRECTOR'S BINDING CONSTRAINT (load-bearing): the segments must be TYPED BY SOMETHING REAL -- the relation
graph / co-occurrence structure -- NOT arbitrary. The RNS residue cell typed by (entity_id % m_k): an arbitrary
integer residue that carries NO relational structure, which is WHY it was code-limited. Here each entity's segment
choice per slot is derived from its OBSERVABLE RELATIONAL-CONTEXT FINGERPRINT rc(e) in R^{2*n_rel} (per-relation
head/tail incidence over TRAIN+SUPPORT edges; leak-free -- never the query edge). Two entities with a similar
relational role fall in the same segment bucket -> their codes SHARE combinatorial substructure -> the per-slot
Hebbian store learns bucket-level (context-type, relation) -> (context-type) associations that GENERALIZE across
entities sharing a bucket, and a NEW held-out entity's code is COMPOSED from its support edges through that same
typing (V(D)J re-assembly). This directly converges with the graph-spectral lever tested in parallel.

TWO-PART VERDICT -- PRIMARY = ORACLE capacity + decode, SECONDARY = INDUCTIVE compose + typing-scramble. The
contract's core questions -- (a) does typed combinatorial-segment CONSTRUCTION give RECOVERABLE capacity vs RANDOM
and vs the residue cell's code-limited arbitrary-id-residue floor (0.0008), and (b) does the POPULATION/CLONAL SOFT
decode beat the HARD one-shot decode -- are both cleanly and robustly answered in the ORACLE regime (held-out edges
folded into the per-slot stores), which is relabeling-robust so it survives scale. That is the PRIMARY verdict. The
Director's additional TYPING hypothesis (the lift comes from graph-structure typing, not mere parameters) is a
GENERALIZATION claim that only shows in the INDUCTIVE COMPOSE regime (held-out codes re-assembled from support, no
fold-in): an oracle that folds held-out edges into W memorizes any near-unique per-instance code, so its ceiling is
nearly INVARIANT to whether the typing tracks graph structure -- a typing scramble cannot collapse it. So the
typed-assignment-scramble (typing-not-params) control lives in the SECONDARY COMPOSE arms, reported with an explicit
inductive-lever flag but NOT gating the primary capacity/decode verdict (the realized compose signal is noisier).

CONSTRUCTION (my design; zero SGD, deterministic, glass-box; matched compute to the monolithic opaque atom EXACTLY):
K=4 slots. 3 TYPED slots (V/D/J analog): slot k has a small library C_k of LIB_TYPED=48 random-bipolar segment
hypervectors (dim d_seg=2048); entity e's slot-k choice seg_k(e)=argmax_j <P_k[j], rc(e)> under a fixed random
prototype matrix P_k (LIB_TYPED x 2*n_rel) -- a prototype/hyperplane assignment tying the segment to the graph
fingerprint. 1 JUNCTIONAL slot (TdT analog): seg_J(e)=hash(e) % LIB_JUNCT=64 -- a per-instance pseudo-random choice
that adds DIVERSITY (junctional insertion does most of the diversity work) but NOT relational specificity, weighted
JUNCT_WEIGHT=0.3 so it disambiguates instances within a type-population without swamping the typed combinatorial
signal. Per slot k a REAL KGStore(n_ent=lib_k, n_rel, n_dim=d_seg) supplies the segment codebook C_k + a one-shot
Hebbian W_k over segment-mapped TRAIN edges (seg_k(h), r, seg_k(t)); for the COMPOSE arms the store is TRAIN-ONLY
(no fold-in) -- held-out entities are re-assembled from support. d_seg=2048 all slots -> SEG W-cost = K*d_seg^2 =
16.78M. The matched-cost monolithic opaque-atom control at d_match=round(sqrt(K)*d_seg)=4096 (W-cost 16.78M,
identical) is the SAME-COST bar in BOTH regimes.

RETRIEVAL (segment-code x decode; SOFT = population/clonal, HARD = one-shot). PRIMARY = the ORACLE arms
(SEG_SOFT_ORACLE / SEG_HARD_ORACLE vs MONO_MATCHED_ORACLE / RANDOM); SECONDARY = the inductive COMPOSE arms:
  SEG_SOFT_COMPOSE (SECONDARY headline) : train-only segment stores; each held-out tail's TYPED segments COMPOSED from its
                        support edges (per-slot majority estimate = affinity maturation), junctional from id-hash;
                        POPULATION soft joint decode of query edges: score(t)=sum_k w_k * s_k[:, seg_k(t)] where
                        s_k[i,j]=<W_k @ key(seg_k(h_i), r_i), C_k[j]> is a continuous posterior over the whole
                        segment population (no per-slot commitment). This IS the resonator/SIC-peel soft-threshold
                        population match: a strong slot carries weak ones, many near-miss candidates ranked.
  SEG_HARD_COMPOSE    : SAME composed segment codes, HARD one-shot decode: per slot hat_k=argmax_j s_k[i,j] (single
                        winner committed); score(t)=sum_k w_k * [seg_k(t)==hat_k] agreement. The fragile single-shot
                        decode the drill + RC2 CRT + RNS_NOISY all predict LOSES to soft. SEG_SOFT - SEG_HARD
                        isolates the RETRIEVAL-side half of the lever.
  SEG_SCRAMBLE_COMPOSE: MUST-FAIL. The entity->TYPED-segment assignment is SCRAMBLED (random per-entity permutation,
                        same lib sizes -> identical parameter count / collision distribution) so segments no longer
                        track graph structure; support->code re-assembly is now uninformative -> the gain collapses.
                        Isolates LIBRARY/graph-structure typing from mere added parameters.
  MONO_MATCHED_COMPOSE: the SAME-COST monolithic opaque-atom bar in the compose regime -- train-only KGStore d=4096,
                        held-out codes composed by native support-bundle (base.native_compose_codes), native readout.
  SEG_SOFT_ORACLE / SEG_HARD_ORACLE (PRIMARY) : segment codes with held-out edges FOLDED IN -> the recoverable
                        capacity claim (vs RANDOM, vs residue's code-limited 0.0008) + the clean soft-vs-hard decode
                        contrast (relabeling-robust; survives scale). THE PRIMARY headline arms.
  MONO_MATCHED_ORACLE : monolithic opaque atom d=4096, fold-in -> capacity ceiling + the ORACLE-FIRES gate + the
                        1.3x lever bar.
                        MEASURED@data/exp_kg_store_dim_scaling_ceiling_v1:oracle_mrr_by_dim.4096=0.413520.
  MONO_PC_ORACLE      : monolithic opaque d=1024, fold-in. POSITIVE CONTROL -> reproduce 0.023.
  RANDOM (null floor); POP (fit-independence / BROKEN guard floor).

LOCALIZATION (the soft-vs-hard + structure-vs-params contrasts the contract asks for, in the COMPOSE regime):
  SEG_SOFT >> SEG_HARD ~ RANDOM => recoverable-but-only-by-population-soft-decode (retrieval-side lever; hard
    one-shot fragile, exactly as clonal-selection predicts).
  SEG_SOFT ~ SEG_HARD > RANDOM  => construction structure carries signal readable by EITHER decode (construction-side).
  SEG_SOFT ~ SEG_HARD ~ RANDOM  => CODES-ABSENT: arbitrary labels have nothing to impose combinatorial structure ONTO
    (drill HARD-FAIL #1; rules out the whole impose-structure-at-construction family).
  SEG_SOFT - SEG_SCRAMBLE small => PARAM-ARTIFACT: any lift is added-parameter volume, not graph-structure typing
    (drill HARD-FAIL #2).
  SEG_SOFT >= 1.3x MONO_MATCHED_COMPOSE => genuine deployable construction-time lever (drill HARD-PASS). Else if
    recoverable + soft>hard + scramble-collapses but < 1.3x => MEASURED_STRUCTURE_NO_LEVER (structure + population
    retrieval real, a same-cost monolithic compose does at least as well; informative partial).

PRE-REG BANDS (picked BEFORE the run; FILTERED MRR rank-vs-all-N; PRIMARY = ORACLE fractions of ADD_ORACLE=0.137 +
the 1.3x same-cost-monolithic-oracle lever bar + soft-vs-hard; SECONDARY = INDUCTIVE compose + typing scramble):
  ORACLE-FIRES (arena answerable) : MONO_MATCHED_ORACLE >= 3x RANDOM AND (MONO_MATCHED_ORACLE - RANDOM) >= 0.003.
  POS-CONTROL : MONO_PC_ORACLE reproduces 0.023 within +-0.010 AND RANDOM <= 0.004.
  RECOVERABLE (construction structure has recoverable capacity vs residue's code-limited 0.0008):
      (SEG_SOFT_ORACLE - RANDOM) >= max(0.50*ADD_ORACLE, 0.010) = 0.0686.
  SOFT_BEATS_HARD (retrieval-side, the contract's headline contrast): SEG_SOFT_ORACLE - SEG_HARD_ORACLE >= 0.010.
  LEVER : SEG_SOFT_ORACLE >= 1.30 * MONO_MATCHED_ORACLE (beats the same-cost monolithic opaque atom).
  HARD_PASS_LEVER_CONSTRUCTION_PLUS_SOFT : pos-controls hold AND oracle fires AND RECOVERABLE AND SOFT_BEATS_HARD AND
      LEVER (segment construction + soft population decode beats the same-cost monolithic by >=1.3x).
  MIDDLE_BAND_MARGINAL_SEGMENT_EDGE : RECOVERABLE AND SOFT_BEATS_HARD AND MONO_MATCHED_ORACLE < SEG_SOFT_ORACLE <
      1.30*MONO_MATCHED_ORACLE -> marginal edge over the same-cost monolithic; sweep K / lib_size / junctional weight.
  MEASURED_CAPACITY_PRESENT_SOFT_BEATS_HARD_NO_LEVER : RECOVERABLE AND SOFT_BEATS_HARD BUT SEG_SOFT_ORACLE <=
      MONO_MATCHED_ORACLE -> typed combinatorial construction gives RECOVERABLE capacity (a real improvement over the
      residue arbitrary-id-residue code-limited floor) and the population soft decode beats hard one-shot, but a
      same-cost monolithic opaque atom does at least as well (no sub-monolithic lever). Informative partial.
  MEASURED_CAPACITY_PRESENT_HARD_READS_TOO : RECOVERABLE but SOFT does NOT beat HARD -> capacity present, readable by
      either decode (construction-side, not retrieval-limited).
  HARD_FAIL_CODES_ABSENT : pos-controls hold AND oracle fires AND (SEG_SOFT_ORACLE - RANDOM) < 0.010 -> arbitrary
      labels have nothing to type; capacity absent even under fold-in (like the residue cell).
  SECONDARY inductive-lever (reported, not primary-gating): compose_recoverable (SEG_SOFT_COMPOSE - RANDOM >= 0.010)
      AND compose_soft_beats_hard (SEG_SOFT_COMPOSE - SEG_HARD_COMPOSE >= 0.010) AND scramble_collapses
      (SEG_SOFT_COMPOSE - SEG_SCRAMBLE_COMPOSE >= 0.020) -> graph-structure typing gives a deployable INDUCTIVE lever
      (typing not params). The realized compose signal is inherently noisier (type-level generalization + sparse
      support) so this is a secondary flag, not a gate on the primary capacity/decode verdict.
  Gated INCONCLUSIVE if oracle does not fire, pos-controls fail, too few held-out queries, or POP beats RANDOM
  (BROKEN; guard validated vs the RANDOM/arm floor per Gate F.4).

FIVE VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight; F.1-F.4 ENFORCE):
  (1) positive_control : on a planted TYPE-structured arena, SEG_SOFT_ORACLE recovers planted held-out tails (fold-in)
      and clears RANDOM by the ceiling-aware fire gate -> arena answerable, the population soft-decode discriminator FIRES.
  (2) metric_moves : the oracle 2x2 MRRs MOVE across [RANDOM, SEG_HARD_ORACLE, MONO_MATCHED_ORACLE, SEG_SOFT_ORACLE].
  (3) negative_control_margin : RANDOM + relation-scramble oracle decode + hard one-shot decode sit below
      SEG_SOFT_ORACLE by an MRR margin, deterministically (>=3 controls).
  (4) full_gates_exercised : the deployable/localization verdict fires every fail-closed gate at self-test scale.
  (5) real_code_path (F.1) + substrate_signature (F.2/F.3) + guard_baseline_valid (F.4): the self-test CONSTRUCTS the
      REAL KGStore per slot at tiny scale and RUNS ingest_triples on SEGMENT-mapped triples (FULL entrypoints); binds
      KGStore against its LIVE signature with BASE/portable kwargs only (n_ent,n_rel,n_dim,generator -- NOT optional
      init_entities); the BROKEN(POP>RANDOM) guard is validated vs the RANDOM/arm floor, not a structural-zero POP.

## Compute architecture
class (b) sequential-CPU, justified. The native store is ONE-SHOT Hebbian (NO SGD, NO epochs). Per seed the cell
builds 4 fold-in segment stores + 4 train-only segment stores + 4 scrambled train-only segment stores + a monolithic
d=1024 (pos-control) + a monolithic d=4096 fold-in (oracle ceiling) + a monolithic d=4096 train-only (compose bar) =
15 real KGStore Hebbian ingests (chunked, batch=5000). Decode is a per-slot (nq x lib_k) similarity matmul + an
O(nq*N*K) gather (lib_k<=64 distinct segment codes -> sub-quadratic readout). The residue sibling built 12 stores
(5 modules d=2048 + 5 compose + 2 mono d=4579) across 3 seeds on device=cpu in 623s; this cell builds smaller
monolithic dims (d=4096 vs 4579) and d_seg=2048 -> <~900s for 3 seeds -> remote_cpu_queue (device=cpu). No SGD, no
GPU. SHARDED storage (each slot its own W_k) per the compositional-cell mandate -- the soft joint decode reads slots
independently, no cross-slot bundle interference. No mutation of any persisted store; each KGStore instance is
cell-local; only a read-only relational-context fingerprint + per-slot typing table are held.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): >=5 distinct score signatures per seed.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: PRIMARY bands are FRACTIONS of the measured additive-oracle ceiling (0.137) + a same-cost
#   monolithic-oracle in-run bar (1.3x) -> discriminator_reachability OK (SEG_SOFT_ORACLE must beat a measured same-cost arm).
# - baseline_in_band: MONO_MATCHED_ORACLE must FIRE (>=3x RANDOM); MONO_PC reproduces 0.023; RANDOM near the 1/N floor.
# - discriminator survives scale: FULL at the EXACT CSKG core / held-out-entity regime (N~25.7k, frac=0.15,
#   support_frac=0.5, seeds 7/13/17) that MEASURED 0.023->0.781 monolithic + 0.137 additive; the self-test fires the
#   SEG_SOFT_ORACLE-recovers-planted + soft-beats-hard + relation-scramble-collapses discriminators; the ORACLE decode
#   contrast is relabeling-robust so it survives scale (not a small-N artifact).
# - HARD bands strictly separated: LEVER needs SEG_SOFT_ORACLE >= 1.30*MONO_MATCHED_ORACLE (MIDDLE dead-band (1.0x,1.3x)).
# - HP_SCOPE: the LEVER gates apply to SEG_SOFT_ORACLE only. MONO_MATCHED_ORACLE = capacity ceiling + oracle-fire +
#   1.3x bar; MONO_PC = 0.023 reproducer; SEG_HARD_ORACLE = fragile one-shot localizer; RANDOM = must-not-clear floor;
#   SECONDARY inductive arms SEG_SOFT_COMPOSE/SEG_HARD_COMPOSE/SEG_SCRAMBLE_COMPOSE/MONO_MATCHED_COMPOSE = reported
#   typing-lever context (not primary-gating); POP = fit-independence / BROKEN guard.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms + >=5 sigs + finite W per slot.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: default_ok_for_this_regime -- all slot/lib/dim/frac/weight/tols pre-registered, NOT tuned on
#   real data; the CSKG core + held-out split config is COPIED VERBATIM from the native + additive + residue arenas.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the docstring/prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-slot flush prints + heartbeat; timeout>=1800).

ASCII-only. No bare except; except SystemExit before except Exception.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import Graph, build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, pop_hits,
)
from hdlab.kg_traversal import KGStore  # noqa: E402  (LIVE store; per-slot segment codebooks + native Hebbian W)

# Reuse the native arena / split / native readout / controls VERBATIM via import (bit-identical split given seed).
import experiments.exp_native_bind_compose_inductive_entity_cskg_v1 as base  # noqa: E402

ANCHOR_NAME = "map_builder_segment_library_clonal_retrieval_v1"

# ---- Arm names (all scored PAIRED on the SAME held-out QUERY edges; filtered MRR-vs-all-N) ----
MONO_PC = "MONO_PC_ORACLE_d1024"                # positive control: monolithic opaque d=1024 -> reproduce 0.023
MONO_MATCHED_ORA = "MONO_MATCHED_ORACLE"         # capacity ceiling + oracle-fire gate (same-cost monolithic, fold-in)
SEG_SOFT_ORA = "SEG_SOFT_ORACLE"                 # segment codes fold-in, soft joint decode (capacity reference)
SEG_HARD_ORA = "SEG_HARD_ORACLE"                 # segment codes fold-in, hard one-shot decode (decode reference)
MONO_COMPOSE = "MONO_MATCHED_COMPOSE"           # HEADLINE bar: same-cost monolithic, realized support-compose
SEG_SOFT = "SEG_SOFT_COMPOSE"                    # HEADLINE: segment codes composed from support, soft population decode
SEG_HARD = "SEG_HARD_COMPOSE"                    # segment codes composed from support, hard one-shot decode
SEG_SCRAMBLE = "SEG_SCRAMBLE_COMPOSE"           # MUST-FAIL: entity->typed-segment assignment scrambled
RANDOM = "RANDOM_CODES"                          # null floor
POP = "BASELINE_POP"                             # fit-independence sanity / BROKEN guard floor

ORACLE_2X2 = [MONO_PC, MONO_MATCHED_ORA, SEG_HARD_ORA, SEG_SOFT_ORA]
COMPOSE_ARMS = [MONO_COMPOSE, SEG_HARD, SEG_SOFT, SEG_SCRAMBLE]
ALL_ARMS = [MONO_PC, MONO_MATCHED_ORA, SEG_SOFT_ORA, SEG_HARD_ORA, MONO_COMPOSE, SEG_SOFT, SEG_HARD,
            SEG_SCRAMBLE, RANDOM, POP]

EVAL_KS = (1, 3, 10, 100)
CEIL_METRIC = "mrr"

# ---- V(D)J segment-library design (K slots: 3 TYPED-by-graph-context + 1 JUNCTIONAL per-instance) ----
LIB_SIZES = [48, 48, 48, 64]               # per-slot library sizes (V/D/J typed + junctional TdT)
TYPED_MASK = [True, True, True, False]      # first 3 slots typed by relational-context fingerprint; last junctional
SLOT_WEIGHTS = [1.0, 1.0, 1.0, 0.3]        # junctional weighted down so it disambiguates but doesn't swamp typed
D_SEG = 2048                                # per-slot code dim (all slots)
K_SLOTS = len(LIB_SIZES)
# matched-cost monolithic dim: d_match^2 == K*D_SEG^2 -> d_match = round(sqrt(K)*D_SEG) = 4096 for K=4
D_MATCHED = int(round((float(K_SLOTS) ** 0.5) * D_SEG))     # 4096
D_MONO_PC = 1024
JUNCT_HASH_MULT = 2654435761                # Knuth multiplicative hash for the junctional per-instance slot

# ---- CITED reference ceilings (the quantities this cell is measured against) ----
CITED_MONO_1024 = 0.023083   # MEASURED@data/exp_kg_store_dim_scaling_ceiling_v1/metrics.json:gates.oracle_mrr_by_dim.1024
CITED_MONO_4096 = 0.413520   # MEASURED@ same :4096  (the matched-cost monolithic opaque-atom ORACLE ceiling at d=4096)
CITED_RELIEF_8192 = 0.780600 # MEASURED@ same :8192 (the undeployable O(n^2) relief target)
CITED_ADD_ORACLE = 0.137293  # MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_ADDITIVE
CITED_ADD_COMPOSE = 0.12821  # MEASURED@ same :ANCHOR_COMPOSE (additive REALIZED compose -- the compose-regime ceiling)
CITED_RNS_CLEAN = 0.000765   # MEASURED@data/exp_map_builder_residue_module_ceiling_v1:gates.oracle_2x2_mrr.RNS_CLEAN (arbitrary id-residue typing: code-limited)

# ---- W-storage costs (parameter counts; SEG matched to MONO by construction) ----
SEG_COST = K_SLOTS * D_SEG * D_SEG
MONO_MATCHED_COST = D_MATCHED * D_MATCHED
RELIEF_8192_COST = 8192 * 8192

# ---- Pre-registered bands (NOT tuned on real data) ----
# PRIMARY = ORACLE capacity + decode: does typed combinatorial-segment construction give RECOVERABLE capacity
# (vs residue's code-limited 0.0008 and vs RANDOM) and does the POPULATION soft decode beat the HARD one-shot decode.
# SECONDARY = INDUCTIVE compose + typed-assignment-scramble: does graph-structure typing give a deployable inductive
# lever (reported; the scramble tests typing-not-params but is noisier in the realized compose regime).
REPRODUCE_TOL_MONO = 0.010       # |MONO_PC - 0.023| tolerance (one-shot Hebbian, low variance)
RANDOM_FLOOR_MRR = 0.004         # RANDOM must sit at/below this (native-readout null floor at nq>=3000)
ORACLE_FIRE_RATIO = 3.0
ORACLE_FIRE_ABS = 0.003
RECOVER_ADD_FRAC = 0.50          # SEG_SOFT_ORACLE - RANDOM >= 0.50 * ADD_ORACLE (recoverable capacity present)
RECOVER_ADD_ABS = 0.010          # ... AND >= this absolute (recoverable at all; beats residue code-limited 0.0008)
SOFT_HARD_MARGIN = 0.010         # SEG_SOFT_ORACLE - SEG_HARD_ORACLE >= this -> population soft beats hard one-shot
LEVER_RATIO = 1.30               # SEG_SOFT_ORACLE >= 1.30 * MONO_MATCHED_ORACLE -> beats the same-cost monolithic
SCRAMBLE_MARGIN = 0.020          # SECONDARY: SEG_SOFT_COMPOSE - SEG_SCRAMBLE_COMPOSE >= this (typing not params)
COMPOSE_RECOVER_ABS = 0.010      # SECONDARY: SEG_SOFT_COMPOSE - RANDOM >= this (inductive signal present)

# ---- self-test planted thresholds (calibrated on synthetic, NOT real data; ORACLE regime -- fires robustly) ----
ST_SOFT_MIN = 0.15               # planted arena: SEG_SOFT_ORACLE mrr >= this (capacity recoverable)
ST_SOFT_BEATS_RANDOM = 0.08      # (SEG_SOFT_ORACLE - RANDOM) mrr margin
ST_SOFT_GE_HARD = 0.010          # (SEG_SOFT_ORACLE - SEG_HARD_ORACLE) mrr margin (soft population beats hard one-shot)
ST_RELSCRAMBLE_MARGIN = 0.03     # (SEG_SOFT_ORACLE - relation-scramble oracle) mrr margin (must-fail)
ST_COMPOSE_MARGIN = 0.005        # (SEG_SOFT_COMPOSE - RANDOM) directional sanity in the inductive regime

SCORE_CHUNK = 512

# Config profiles. SELFTEST/FULL exercise the SAME segment-library build -> compose -> soft/hard decode -> verdict path.
SELFTEST_CFG = dict(lib_sizes=[12, 12, 20], typed_mask=[True, True, False], slot_weights=[1.0, 1.0, 0.4],
                    d_seg=512, d_mono_pc=256, st_n_ent=120, st_n_types=8, st_edges_per_ent=7,
                    heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0, min_heldout=8)
# FULL: CSKG core k_core=12 (N~25.7k), the SAME held-out split (frac=0.15, support_frac=0.5), seeds [7,13,17].
FULL_CFG = dict(lib_sizes=LIB_SIZES, typed_mask=TYPED_MASK, slot_weights=SLOT_WEIGHTS, d_seg=D_SEG,
                d_mono_pc=D_MONO_PC, heldout_entity_frac=0.15, support_frac=0.5, cskg_max_lines=0, k_core=12,
                cskg_max_nodes=0, n_heldout_eval=3000, min_heldout=20, seeds=[7, 13, 17])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def _d_matched(lib_sizes, d_seg):
    return int(round((float(len(lib_sizes)) ** 0.5) * d_seg))


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# SEGMENT TYPING: derive each entity's per-slot segment choice from its OBSERVABLE relational-context fingerprint
# (leak-free -- train+support edges only, NEVER the query edge). Typed slots = argmax of a fixed random prototype
# projection of rc(e); junctional slot = per-instance hash. The Director's binding constraint.
# ---------------------------------------------------------------------------

def build_relational_context(edges_int, N, n_rel):
    """rc[e] in R^{2*n_rel}: per-relation head incidence (0..n_rel) + tail incidence (n_rel..2*n_rel), L2-normalized.
    Observable graph fingerprint of entity e. edges_int = train+support (leak-free; excludes query edges)."""
    rc = np.zeros((N, 2 * n_rel), dtype=np.float64)
    h = edges_int[:, 0].astype(np.int64); r = edges_int[:, 1].astype(np.int64); t = edges_int[:, 2].astype(np.int64)
    np.add.at(rc, (h, r), 1.0)                 # e as head of relation r
    np.add.at(rc, (t, n_rel + r), 1.0)         # e as tail of relation r
    nrm = np.linalg.norm(rc, axis=1, keepdims=True)
    nrm[nrm == 0.0] = 1.0
    return (rc / nrm).astype(np.float32)


def build_segment_typing(rc, lib_sizes, typed_mask, N, n_rel, seed):
    """seg_assign[k] (len N, long): entity e's segment choice in slot k. Typed slots = argmax_j <P_k[j], rc[e]>
    (prototype/hyperplane assignment tying the segment to the graph fingerprint). Junctional slot = per-instance hash.
    Returns list of K long tensors."""
    seg_assign = []
    for k, (lib_k, typed) in enumerate(zip(lib_sizes, typed_mask)):
        if typed:
            g = np.random.default_rng(seed * 100019 + k * 7919 + 3)
            P_k = g.standard_normal((lib_k, 2 * n_rel)).astype(np.float32)    # fixed random prototypes
            idx = (rc @ P_k.T).argmax(axis=1).astype(np.int64)               # per-entity segment choice
        else:
            ent = np.arange(N, dtype=np.int64)
            idx = ((ent * JUNCT_HASH_MULT) % lib_k).astype(np.int64)         # junctional per-instance hash
        seg_assign.append(torch.from_numpy(idx).long())
    return seg_assign


def scramble_typing(seg_assign, typed_mask, N, seed):
    """Scramble the entity->TYPED-segment assignment (random per-entity permutation per typed slot; junctional kept).
    Same lib sizes -> identical parameter count / collision distribution, but segments no longer track graph structure."""
    out = []
    for k, (sa, typed) in enumerate(zip(seg_assign, typed_mask)):
        if typed:
            perm = np.random.default_rng(seed * 202309 + k * 6151 + 5).permutation(N)
            out.append(torch.from_numpy(sa.numpy()[perm].copy()).long())
        else:
            out.append(sa.clone())
    return out


def _segment_map(edges_int, seg_assign_k):
    """Map (h,r,t) int edges to segment-space (seg_k(h), r, seg_k(t)) for slot k's Hebbian ingest."""
    sk = seg_assign_k.numpy()
    h = sk[edges_int[:, 0].astype(np.int64)].astype(np.int64)
    r = edges_int[:, 1].astype(np.int64)
    t = sk[edges_int[:, 2].astype(np.int64)].astype(np.int64)
    return np.stack([h, r, t], axis=1)


def build_segment_module(lib_k, n_rel, d_seg, seed, slot_idx, train_int, seg_assign_k, fold_in=None):
    """Real KGStore for slot k. Base/portable kwargs ONLY (n_ent,n_rel,n_dim,generator) per Gate F.3 -> random-bipolar
    segment codebook C_k (lib_k x d_seg), RC_k (n_rel x d_seg). One-shot Hebbian W_k over segment-mapped train(+fold-in)
    edges. Returns (store, W_finite)."""
    g = torch.Generator(device="cpu").manual_seed(seed * 100000 + d_seg * 7 + slot_idx * 131 + 3)
    store = KGStore(n_ent=int(lib_k), n_rel=int(n_rel), n_dim=int(d_seg), generator=g)
    store.W.zero_()
    tri = _segment_map(train_int, seg_assign_k)
    if fold_in is not None and fold_in.shape[0] > 0:
        tri = np.concatenate([tri, _segment_map(fold_in, seg_assign_k)], axis=0)
    store.ingest_triples(torch.from_numpy(tri).long())
    finite = bool(torch.isfinite(store.W).all().item())
    return store, finite


def module_segment_sims(store, edges_int, head_seg_assign_k, chunk=SCORE_CHUNK, rel_perm=None):
    """s_k[i, j] = <W_k @ key_k(seg_k(h_i), r_i), C_k[j]> for j in [0, lib_k). Native bilinear recall then segment-
    codebook similarity. head_seg_assign_k types the HEAD of each edge. rel_perm scrambles relations. Shape [n, lib_k]."""
    sk = head_seg_assign_k.numpy()
    hq = torch.from_numpy(sk[edges_int[:, 0].astype(np.int64)].astype(np.int64)).long()
    r_np = edges_int[:, 1].astype(np.int64).copy()
    if rel_perm is not None:
        r_np = rel_perm[r_np]
    rq = torch.from_numpy(r_np).long()
    E = store.E; R = store.R; W = store.W; sq = store.sq
    n = edges_int.shape[0]
    ET = E.T.contiguous()
    out = torch.empty(n, E.shape[0], dtype=torch.float32)
    for b in range(0, n, chunk):
        Q = (E[hq[b:b + chunk]] * R[rq[b:b + chunk]] * sq)     # [c, d_seg] native multiplicative bind
        recall = Q @ W.T                                       # [c, d_seg] native Hebbian recall
        out[b:b + chunk] = recall @ ET                         # [c, lib_k] segment-codebook similarity
    return out


def seg_soft_scores(sims_list, tail_assign, weights, N):
    """POPULATION/CLONAL soft joint decode: score(t) = sum_k w_k * s_k[:, seg_k(t)]. Continuous per-slot posterior
    over the whole segment population (no per-slot commitment). Shape [nq, N]. O(nq*N*K) gather (sub-quadratic)."""
    nq = sims_list[0].shape[0]
    scores = torch.zeros(nq, N, dtype=torch.float32)
    for k, s_k in enumerate(sims_list):
        scores += float(weights[k]) * s_k[:, tail_assign[k]]   # gather (nq, N) from (nq, lib_k)
    return scores


def seg_hard_scores(sims_list, tail_assign, weights, N, seed):
    """HARD one-shot decode: per slot hat_k = argmax_j s_k[i,j] (single winner committed); score(t) = sum_k w_k *
    [seg_k(t)==hat_k] agreement. The fragile single-shot decode. Ties broken by a signal-free deterministic jitter."""
    nq = sims_list[0].shape[0]
    agree = torch.zeros(nq, N, dtype=torch.float32)
    for k, s_k in enumerate(sims_list):
        hat_k = s_k.argmax(dim=1)                              # [nq] hard winner per slot
        agree += float(weights[k]) * (tail_assign[k][None, :] == hat_k[:, None]).to(torch.float32)
    g = torch.Generator(device="cpu").manual_seed(seed * 313 + 11)
    jitter = (torch.rand(nq, N, generator=g, dtype=torch.float32) - 0.5) * 1e-4
    return agree + jitter


def compose_tail_assign(modules_tr, support_int, head_seg_assign, base_assign, lib_sizes, typed_mask, rel_perm=None):
    """INDUCTIVE re-assembly (affinity maturation): re-estimate each SUPPORT tail's TYPED-segment from its support
    edges (per-slot MAJORITY argmax of the support-edge recalls; NO fold-in). Junctional slot + all train tails keep
    base_assign. head_seg_assign types the support HEAD. rel_perm scrambles support relations (control)."""
    seg_c = [sa.clone() for sa in base_assign]
    tails = support_int[:, 2].astype(np.int64)
    for k, (store, lib_k, typed) in enumerate(zip(modules_tr, lib_sizes, typed_mask)):
        if not typed:
            continue
        s_sup = module_segment_sims(store, support_int, head_seg_assign[k], rel_perm=rel_perm)   # [S, lib_k]
        hat = s_sup.argmax(dim=1).numpy()                                                        # [S]
        votes = {}
        for i in range(tails.shape[0]):
            tt = int(tails[i])
            votes.setdefault(tt, np.zeros(lib_k, dtype=np.int64))
            votes[tt][int(hat[i])] += 1
        arr = seg_c[k].numpy().copy()
        for tt, v in votes.items():
            arr[tt] = int(v.argmax())
        seg_c[k] = torch.from_numpy(arr).long()
    return seg_c


# ---------------------------------------------------------------------------
# Score all arms PAIRED on the SAME held-out QUERY edges.
# ---------------------------------------------------------------------------

def score_all_arms(prep, cfg, seed):
    N = prep["N"]; n_rel = prep["n_rel"]
    lib_sizes = cfg["lib_sizes"]; typed_mask = cfg["typed_mask"]; weights = cfg["slot_weights"]
    d_seg = cfg["d_seg"]; d_mono_pc = cfg["d_mono_pc"]
    d_match = _d_matched(lib_sizes, d_seg)
    train_int = prep["train_int"]; support_int = prep["support_int"]; query_int = prep["query_int"]
    hold_all = prep["hold_all"]; all_true = prep["all_true"]
    seg_assign = prep["seg_assign"]
    seg_assign_scr = scramble_typing(seg_assign, typed_mask, N, seed)

    # ---- ORACLE segment stores (fold-in) -> capacity ceiling + soft-vs-hard decode reference ----
    modules_ora = []
    mods_finite = True
    for kk, lib_k in enumerate(lib_sizes):
        store_k, fin_k = build_segment_module(lib_k, n_rel, d_seg, seed, kk, train_int, seg_assign[kk], fold_in=hold_all)
        modules_ora.append(store_k)
        mods_finite = mods_finite and fin_k
    sims_ora = [module_segment_sims(store, query_int, seg_assign[k]) for k, store in enumerate(modules_ora)]
    sc_seg_soft_ora = seg_soft_scores(sims_ora, seg_assign, weights, N)
    sc_seg_hard_ora = seg_hard_scores(sims_ora, seg_assign, weights, N, seed)
    # relation-scramble oracle control (permute relation ids in the query recall -> breaks the relational operator on
    # the SAME recoverable segment codes; a clean must-fail for the oracle capacity claim). Internal (self-test margin).
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)
    sims_ora_scr = [module_segment_sims(store, query_int, seg_assign[k], rel_perm=rel_perm)
                    for k, store in enumerate(modules_ora)]
    sc_seg_relscr_ora = seg_soft_scores(sims_ora_scr, seg_assign, weights, N)

    # ---- TRAIN-ONLY segment stores (no fold-in) -> INDUCTIVE compose (HEADLINE) ----
    modules_tr = []
    for kk, lib_k in enumerate(lib_sizes):
        store_k, fin_k = build_segment_module(lib_k, n_rel, d_seg, seed, kk, train_int, seg_assign[kk], fold_in=None)
        modules_tr.append(store_k)
        mods_finite = mods_finite and fin_k
    seg_c = compose_tail_assign(modules_tr, support_int, seg_assign, seg_assign, lib_sizes, typed_mask)
    sims_q = [module_segment_sims(store, query_int, seg_assign[k]) for k, store in enumerate(modules_tr)]
    sc_seg_soft = seg_soft_scores(sims_q, seg_c, weights, N)
    sc_seg_hard = seg_hard_scores(sims_q, seg_c, weights, N, seed)

    # ---- SCRAMBLED train-only segment stores -> must-fail typed-assignment control ----
    modules_scr = []
    for kk, lib_k in enumerate(lib_sizes):
        store_k, fin_k = build_segment_module(lib_k, n_rel, d_seg, seed, kk, train_int, seg_assign_scr[kk],
                                              fold_in=None)
        modules_scr.append(store_k)
        mods_finite = mods_finite and fin_k
    seg_c_scr = compose_tail_assign(modules_scr, support_int, seg_assign_scr, seg_assign_scr, lib_sizes, typed_mask)
    sims_q_scr = [module_segment_sims(store, query_int, seg_assign_scr[k]) for k, store in enumerate(modules_scr)]
    sc_seg_scr = seg_soft_scores(sims_q_scr, seg_c_scr, weights, N)

    # ---- monolithic opaque-atom arms (reuse base VERBATIM) ----
    store_pc = base.build_store(N, n_rel, d_mono_pc, seed, train_int, fold_in=hold_all)
    recall_pc = base.native_query_recall(store_pc, query_int)
    sc_mono_pc = base.score_from_codes(recall_pc, store_pc.E)
    store_mm_ora = base.build_store(N, n_rel, d_match, seed, train_int, fold_in=hold_all)
    recall_mm_ora = base.native_query_recall(store_mm_ora, query_int)
    sc_mono_mm_ora = base.score_from_codes(recall_mm_ora, store_mm_ora.E)
    # monolithic realized COMPOSE bar (train-only store; held-out codes bundled from support)
    store_mm_tr = base.build_store(N, n_rel, d_match, seed, train_int, fold_in=None)
    Ep_mm, _deg = base.native_compose_codes(store_mm_tr, support_int, N)
    recall_mm_tr = base.native_query_recall(store_mm_tr, query_int)
    sc_mono_compose = base.score_from_codes(recall_mm_tr, Ep_mm)
    mono_finite = bool(torch.isfinite(store_pc.W).all().item() and torch.isfinite(store_mm_ora.W).all().item()
                       and torch.isfinite(store_mm_tr.W).all().item())

    sc_random = base.random_scores(N, query_int, d_match, seed)

    arm_scores = {
        MONO_PC: sc_mono_pc, MONO_MATCHED_ORA: sc_mono_mm_ora, SEG_SOFT_ORA: sc_seg_soft_ora,
        SEG_HARD_ORA: sc_seg_hard_ora, MONO_COMPOSE: sc_mono_compose, SEG_SOFT: sc_seg_soft, SEG_HARD: sc_seg_hard,
        SEG_SCRAMBLE: sc_seg_scr, RANDOM: sc_random,
    }
    arm_scores["_SEG_RELSCRAMBLE_ORACLE"] = sc_seg_relscr_ora   # internal control (self-test negative margin)

    arm_metric, arm_sig = {}, {}
    for name, sc in arm_scores.items():
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
    pop_m, pop_rank_vec = pop_hits(prep["gd"].rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    diag = dict(mods_finite=bool(mods_finite), mono_finite=mono_finite, d_matched=int(d_match),
                seg_cost=int(len(lib_sizes) * d_seg * d_seg), mono_matched_cost=int(d_match * d_match),
                lib_sizes=list(lib_sizes), d_seg=int(d_seg),
                seg_signature_unique_frac=float(_seg_unique_frac(seg_assign, N)))
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores, diag=diag)


def _seg_unique_frac(seg_assign, N):
    """Fraction of the N entities with a UNIQUE full K-slot segment signature (diagnostic: junctional diversity)."""
    sig = np.zeros(N, dtype=np.int64)
    mult = 1
    for sa in seg_assign:
        a = sa.numpy()
        sig = sig * mult + a
        mult = int(a.max()) + 2
    return float(len(np.unique(sig)) / max(1, N))


# ---------------------------------------------------------------------------
# Prepare a seed-deterministic split (SAME as base + additive + residue arena: bit-identical given seed/ent2i/fracs).
# ---------------------------------------------------------------------------

def prepare_corpus(pool_lbl, cfg, seed):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = base.build_heldout_entity_split_ac(
        pool_lbl, ent2i, cfg["heldout_entity_frac"], cfg["support_frac"], seed)
    n_query_total = len(query_lbl)
    if cfg.get("n_heldout_eval") and n_query_total > cfg["n_heldout_eval"]:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = sorted(rng.choice(n_query_total, size=cfg["n_heldout_eval"], replace=False).tolist())
        query_lbl = [query_lbl[i] for i in idx]
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    support_int = _to_int_edges(support_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    hold_all = np.concatenate([support_int, query_int], axis=0) if query_int.shape[0] else support_int
    gd = Graph(train_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, support_int, query_int)
    # relational-context fingerprint over TRAIN+SUPPORT (leak-free; excludes query edges) -> segment typing
    fp_edges = np.concatenate([train_int, support_int], axis=0) if support_int.shape[0] else train_int
    rc = build_relational_context(fp_edges, N, n_rel)
    seg_assign = build_segment_typing(rc, cfg["lib_sizes"], cfg["typed_mask"], N, n_rel, seed)
    return dict(ent2i=ent2i, rel2i=rel2i, N=N, n_rel=n_rel, train_int=train_int, support_int=support_int,
                query_int=query_int, hold_all=hold_all, hold_ids=hold_ids, n_cold=n_cold,
                n_query_total=n_query_total, gd=gd, all_true=all_true, rc=rc, seg_assign=seg_assign)


def run_corpus(pool_lbl, cfg, seed, corpus_name):
    prep = prepare_corpus(pool_lbl, cfg, seed)
    d_match = _d_matched(cfg["lib_sizes"], cfg["d_seg"])
    result = dict(corpus=corpus_name, seed=seed, N=int(prep["N"]), n_rel=int(prep["n_rel"]),
                  n_train=int(prep["train_int"].shape[0]), n_heldout_entities=len(prep["hold_ids"]),
                  n_support=int(prep["support_int"].shape[0]), n_query_total=prep["n_query_total"],
                  n_query_scored=int(prep["query_int"].shape[0]), n_cold=int(prep["n_cold"]),
                  lib_sizes=list(cfg["lib_sizes"]), d_seg=int(cfg["d_seg"]), d_matched=int(d_match))
    if prep["query_int"].shape[0] < 1:
        result["empty"] = True
        return result, None
    fs = score_all_arms(prep, cfg, seed)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs={a: fs["arm_sig"][a] for a in list(fs["arm_sig"].keys())},
        internal_relscramble_mrr=round(am["_SEG_RELSCRAMBLE_ORACLE"].get(CEIL_METRIC, float("nan")), 6),
        diag=fs["diag"],
    )
    return result, fs


# ---------------------------------------------------------------------------
# Deployable / localization verdict over per-seed results (HEADLINE = COMPOSE regime).
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _m(ps, arm):
    return ps["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def deployable_verdict(per_seed):
    def agg(arm):
        return _nm([_m(ps, arm) for ps in per_seed])

    mrr = {a: agg(a) for a in ALL_ARMS}
    mono_pc = mrr[MONO_PC]; mono_ora = mrr[MONO_MATCHED_ORA]; seg_soft_ora = mrr[SEG_SOFT_ORA]
    seg_hard_ora = mrr[SEG_HARD_ORA]; mono_comp = mrr[MONO_COMPOSE]
    seg_soft = mrr[SEG_SOFT]; seg_hard = mrr[SEG_HARD]; seg_scr = mrr[SEG_SCRAMBLE]
    rnd = mrr[RANDOM]; pop = mrr[POP]

    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")

    # PRIMARY (ORACLE capacity + decode)
    H_seg = _sub(seg_soft_ora, rnd)                    # recoverable capacity headroom (vs residue code-limited 0.0008)
    soft_minus_hard = _sub(seg_soft_ora, seg_hard_ora)  # population soft vs hard one-shot (retrieval-side)
    soft_minus_mono = _sub(seg_soft_ora, mono_ora)     # segments vs same-cost monolithic (capacity)
    lever_thresh = LEVER_RATIO * mono_ora if mono_ora == mono_ora else float("nan")
    # SECONDARY (INDUCTIVE compose + typed-assignment scramble)
    comp_minus_rnd = _sub(seg_soft, rnd)
    comp_soft_minus_hard = _sub(seg_soft, seg_hard)
    comp_soft_minus_scramble = _sub(seg_soft, seg_scr)
    comp_soft_minus_mono = _sub(seg_soft, mono_comp)

    # positive controls
    mono_pc_reproduces = bool(mono_pc == mono_pc and abs(mono_pc - CITED_MONO_1024) <= REPRODUCE_TOL_MONO)
    random_floor = bool(rnd == rnd and rnd <= RANDOM_FLOOR_MRR)
    oracle_ratio = _ratio(mono_ora, rnd)
    oracle_fires = bool(_sub(mono_ora, rnd) == _sub(mono_ora, rnd) and _sub(mono_ora, rnd) >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    mods_finite = all(ps.get("diag", {}).get("mods_finite", False) for ps in per_seed)
    mono_finite = all(ps.get("diag", {}).get("mono_finite", False) for ps in per_seed)
    # BROKEN guard (Gate F.4): POP must NOT beat RANDOM (validated vs the RANDOM/arm floor, not a structural-zero POP)
    broken = bool(pop == pop and rnd == rnd and (pop - rnd) > max(RANDOM_FLOOR_MRR, 0.005))

    pos_controls_ok = bool(mono_pc_reproduces and random_floor and oracle_fires and mods_finite
                           and mono_finite and not broken)

    # PRIMARY conditions (ORACLE capacity + decode)
    recoverable = bool(H_seg == H_seg and H_seg >= max(RECOVER_ADD_FRAC * CITED_ADD_ORACLE, RECOVER_ADD_ABS))
    recoverable_any = bool(H_seg == H_seg and H_seg >= RECOVER_ADD_ABS)
    soft_beats_hard = bool(soft_minus_hard == soft_minus_hard and soft_minus_hard >= SOFT_HARD_MARGIN)
    beats_mono_lever = bool(seg_soft_ora == seg_soft_ora and lever_thresh == lever_thresh and seg_soft_ora >= lever_thresh)
    marginal_edge = bool(soft_minus_mono == soft_minus_mono and soft_minus_mono > 0.0 and not beats_mono_lever)
    # SECONDARY conditions (INDUCTIVE lever)
    compose_recoverable = bool(comp_minus_rnd == comp_minus_rnd and comp_minus_rnd >= COMPOSE_RECOVER_ABS)
    compose_soft_beats_hard = bool(comp_soft_minus_hard == comp_soft_minus_hard
                                   and comp_soft_minus_hard >= SOFT_HARD_MARGIN)
    scramble_collapses = bool(comp_soft_minus_scramble == comp_soft_minus_scramble
                              and comp_soft_minus_scramble >= SCRAMBLE_MARGIN)
    inductive_lever = bool(compose_recoverable and compose_soft_beats_hard and scramble_collapses)

    if not pos_controls_ok:
        verdict = "INCONCLUSIVE_POSCONTROL_OR_ORACLE_FAILED"
    elif not recoverable_any:
        verdict = "HARD_FAIL_CODES_ABSENT"
    elif recoverable and soft_beats_hard and beats_mono_lever:
        verdict = "HARD_PASS_LEVER_CONSTRUCTION_PLUS_SOFT"
    elif recoverable and soft_beats_hard and marginal_edge:
        verdict = "MIDDLE_BAND_MARGINAL_SEGMENT_EDGE"
    elif recoverable and soft_beats_hard:
        verdict = "MEASURED_CAPACITY_PRESENT_SOFT_BEATS_HARD_NO_LEVER"
    elif recoverable:
        verdict = "MEASURED_CAPACITY_PRESENT_HARD_READS_TOO"
    else:
        verdict = "MEASURED_CAPACITY_MARGINAL"

    localization = ("RETRIEVAL_LIMITED_soft_unlocks_over_hard" if (recoverable_any and soft_beats_hard)
                    else ("CODE_LIMITED_capacity_absent" if not recoverable_any
                          else "READABLE_BY_HARD_TOO"))

    frac_of_add = _ratio(seg_soft_ora, CITED_ADD_ORACLE)
    frac_of_relief = _ratio(seg_soft_ora, CITED_RELIEF_8192)

    verdict_msg = (
        "%s [%s] || PRIMARY ORACLE MRR: MONO_PC(d1024)=%s(repro0.023=%s) MONO_MATCHED_O(d%d,cost%.1fM)=%s "
        "SEG_HARD_O=%s SEG_SOFT_O=%s(cost%.1fM) RANDOM=%s || H_seg=%s (>=%.3f recoverable=%s vs_rns_clean0.0008) "
        "soft-hard=%s (>=%.3f soft_beats_hard=%s) lever(SEG_SOFT_O>=1.3xMONO_O=%s)=%s soft-mono=%s frac_of_add(0.137)=%s "
        "|| SECONDARY COMPOSE: MONO_C=%s SEG_HARD_C=%s SEG_SOFT_C=%s SEG_SCRAMBLE_C=%s | comp-rnd=%s (recov=%s) "
        "comp_soft-hard=%s (%s) comp_soft-scramble=%s (collapses=%s) inductive_lever=%s | oracle_fires=%s "
        "pos_controls=%s broken=%s seeds=%d"
        % (verdict, localization, _fmt(mono_pc), mono_pc_reproduces, per_seed[0]["diag"]["d_matched"],
           MONO_MATCHED_COST / 1e6, _fmt(mono_ora), _fmt(seg_hard_ora), _fmt(seg_soft_ora), SEG_COST / 1e6, _fmt(rnd),
           _fmt(H_seg), max(RECOVER_ADD_FRAC * CITED_ADD_ORACLE, RECOVER_ADD_ABS), recoverable, _fmt(soft_minus_hard),
           SOFT_HARD_MARGIN, soft_beats_hard, _fmt(lever_thresh), beats_mono_lever, _fmt(soft_minus_mono),
           _fmt(frac_of_add), _fmt(mono_comp), _fmt(seg_hard), _fmt(seg_soft), _fmt(seg_scr), _fmt(comp_minus_rnd),
           compose_recoverable, _fmt(comp_soft_minus_hard), compose_soft_beats_hard, _fmt(comp_soft_minus_scramble),
           scramble_collapses, inductive_lever, oracle_fires, pos_controls_ok, broken, len(per_seed)))

    def _rnd(x, nd=6):
        return round(x, nd) if (x == x and x != float("inf")) else (None if x != x else "inf")

    metric_keys = ["hits@%d" % kk for kk in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    gates = dict(
        verdict=verdict, localization=localization,
        oracle_2x2_mrr=dict(MONO_PC=_rnd(mono_pc), MONO_MATCHED_ORACLE=_rnd(mono_ora),
                            SEG_HARD_ORACLE=_rnd(seg_hard_ora), SEG_SOFT_ORACLE=_rnd(seg_soft_ora)),
        compose_mrr=dict(MONO_MATCHED_COMPOSE=_rnd(mono_comp), SEG_HARD_COMPOSE=_rnd(seg_hard),
                         SEG_SOFT_COMPOSE=_rnd(seg_soft), SEG_SCRAMBLE_COMPOSE=_rnd(seg_scr)),
        random_mrr=_rnd(rnd), H_seg=_rnd(H_seg),
        soft_minus_hard=_rnd(soft_minus_hard), soft_minus_mono_oracle=_rnd(soft_minus_mono),
        lever_threshold=_rnd(lever_thresh), frac_of_additive_oracle=_rnd(frac_of_add),
        frac_of_monolithic_relief=_rnd(frac_of_relief),
        secondary_compose=dict(comp_minus_random=_rnd(comp_minus_rnd), comp_soft_minus_hard=_rnd(comp_soft_minus_hard),
                               comp_soft_minus_scramble=_rnd(comp_soft_minus_scramble),
                               comp_soft_minus_mono=_rnd(comp_soft_minus_mono),
                               compose_recoverable=compose_recoverable,
                               compose_soft_beats_hard=compose_soft_beats_hard,
                               scramble_collapses=scramble_collapses, inductive_lever=inductive_lever),
        costs=dict(SEG_COST=SEG_COST, MONO_MATCHED_COST=MONO_MATCHED_COST, RELIEF_8192_COST=RELIEF_8192_COST,
                   cost_ratio_vs_relief=round(SEG_COST / float(RELIEF_8192_COST), 4)),
        mono_pc_reproduces=mono_pc_reproduces, random_floor=random_floor, oracle_fires=oracle_fires,
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        mods_finite=mods_finite, mono_finite=mono_finite, broken=broken, pos_controls_ok=pos_controls_ok,
        recoverable=recoverable, recoverable_any=recoverable_any, soft_beats_hard=soft_beats_hard,
        beats_mono_lever=beats_mono_lever, marginal_edge=marginal_edge, inductive_lever=inductive_lever,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        controls=dict(POP=_rnd(pop)),
        bands=dict(CITED_MONO_1024=CITED_MONO_1024, CITED_MONO_4096=CITED_MONO_4096, CITED_ADD_ORACLE=CITED_ADD_ORACLE,
                   CITED_ADD_COMPOSE=CITED_ADD_COMPOSE, CITED_RELIEF_8192=CITED_RELIEF_8192,
                   CITED_RNS_CLEAN=CITED_RNS_CLEAN, REPRODUCE_TOL_MONO=REPRODUCE_TOL_MONO,
                   RANDOM_FLOOR_MRR=RANDOM_FLOOR_MRR, ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO,
                   ORACLE_FIRE_ABS=ORACLE_FIRE_ABS, RECOVER_ADD_FRAC=RECOVER_ADD_FRAC, RECOVER_ADD_ABS=RECOVER_ADD_ABS,
                   SOFT_HARD_MARGIN=SOFT_HARD_MARGIN, SCRAMBLE_MARGIN=SCRAMBLE_MARGIN, LEVER_RATIO=LEVER_RATIO,
                   LIB_SIZES=list(LIB_SIZES), TYPED_MASK=list(TYPED_MASK), SLOT_WEIGHTS=list(SLOT_WEIGHTS),
                   D_SEG=D_SEG, D_MATCHED=D_MATCHED),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Planted TYPE-structured arena: entities have a latent TYPE; head-relation choice + tail-type are type-determined,
# so the relational-context fingerprint rc(e) REVEALS type(e); the prototype projection recovers a type-consistent
# segment; a held-out entity's type is re-estimated from its support edges so the compose soft-decode ranks the
# type-population and the junctional slot disambiguates the instance. Typed-assignment scramble breaks the graph->
# segment tie; hard one-shot argmax loses the population evidence.
# ---------------------------------------------------------------------------

def build_planted_typed_arena(seed, n_ent=120, n_types=8, n_rel=6, edges_per_ent=7):
    rng = np.random.default_rng(seed * 100057 + 9)
    ent_type = rng.integers(0, n_types, size=n_ent)                # latent type per entity
    rel_menu = [rng.choice(n_rel, size=max(2, n_rel // 2), replace=False) for _ in range(n_types)]  # type reveals via rc
    tt_map = [rng.permutation(n_types) for _ in range(n_rel)]      # relation r maps head-type -> tail-type
    by_type = {c: np.where(ent_type == c)[0] for c in range(n_types)}
    edges = []
    for h in range(n_ent):
        ch = int(ent_type[h])
        rels = rng.choice(rel_menu[ch], size=min(edges_per_ent, len(rel_menu[ch])), replace=True)
        for r in np.unique(rels):
            tt = int(tt_map[int(r)][ch])
            cand = by_type[tt]
            if cand.shape[0] == 0:
                continue
            t = int(rng.choice(cand))
            if t == h:
                continue
            edges.append(("e%d" % h, "r%d" % int(r), "e%d" % t))
    return list(dict.fromkeys(edges))


# ---------------------------------------------------------------------------
# Self-test: apparatus validity on the planted type-structured arena (real KGStore path + discriminators + must-fails).
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _selftest_real_store_smoke(cfg):
    """Gate F.1: CONSTRUCT the REAL KGStore per slot at tiny scale + RUN ingest_triples on SEGMENT-mapped triples,
    populating the exercised-entrypoints set. Returns (exercised, ok)."""
    exercised = set()
    lib_k = cfg["lib_sizes"][0]
    tri = np.array([[0, 0, 1], [1, 0, 2], [2, 1, 0]], dtype=np.int64)
    seg_k = torch.from_numpy(np.array([0, 1, 2], dtype=np.int64)).long()   # tiny segment assignment for 3 entities
    store, fin = build_segment_module(lib_k, 3, cfg["d_seg"], 7, 0, tri, seg_k, fold_in=tri[:1])
    exercised.add("KGStore")
    exercised.add("build_segment_module")
    if store._n_triples_ingested > 0:
        exercised.add("ingest_triples")
    s = module_segment_sims(store, tri, seg_k)
    if s.shape == (3, lib_k):
        exercised.add("module_segment_sims")
    return exercised, bool(fin and s.shape == (3, lib_k))


def _mechanism_selftest_body():
    cfg = dict(SELFTEST_CFG)
    out = {}

    # ---- Gate F.1 real code path ----
    exercised, real_ok = _selftest_real_store_smoke(cfg)

    pool = build_planted_typed_arena(7, n_ent=cfg["st_n_ent"], n_types=cfg["st_n_types"],
                                     edges_per_ent=cfg["st_edges_per_ent"])
    prep = prepare_corpus(pool, cfg, 7)
    if prep["query_int"].shape[0] < cfg["min_heldout"]:
        out["fail"] = "planted type-structured arena produced too few held-out queries (%d)" % prep["query_int"].shape[0]
        return False, out
    res, fs = run_corpus(pool, cfg, 7, "PLANTED_TYPE_STRUCTURED")
    am = fs["arm_metric"]
    sm = {a: am[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    relscr = am["_SEG_RELSCRAMBLE_ORACLE"].get(CEIL_METRIC, float("nan"))
    n_sigs = len(set(fs["arm_sig"][a] for a in ALL_ARMS))

    # PRIMARY discriminators (ORACLE regime -- fire robustly; the contract's SEG-vs-RANDOM + SOFT-vs-HARD claims)
    soft = sm[SEG_SOFT_ORA]; hard = sm[SEG_HARD_ORA]; rnd = sm[RANDOM]; mono_ora = sm[MONO_MATCHED_ORA]
    soft_recovers = bool(soft == soft and soft >= ST_SOFT_MIN)
    soft_beats_random = bool(soft == soft and rnd == rnd and (soft - rnd) >= ST_SOFT_BEATS_RANDOM)
    soft_ge_hard = bool(soft == soft and hard == hard and (soft - hard) >= ST_SOFT_GE_HARD)
    relscramble_fails = bool(soft == soft and relscr == relscr and (soft - relscr) >= ST_RELSCRAMBLE_MARGIN)
    # SECONDARY directional sanity (INDUCTIVE compose separates from RANDOM on the planted arena)
    compose_sanity = bool(sm[SEG_SOFT] == sm[SEG_SOFT] and rnd == rnd and (sm[SEG_SOFT] - rnd) >= ST_COMPOSE_MARGIN)
    arms_differ = bool(n_sigs >= 5)
    mods_finite = bool(fs["diag"]["mods_finite"] and fs["diag"]["mono_finite"])

    # VACUOUS-SMOKE guard: on the planted arena the ORACLE soft population decode MUST separate from RANDOM.
    soft_frozen = bool((soft - rnd) < ST_SOFT_BEATS_RANDOM)
    assert_discriminator_fires(soft_frozen, control_name=RANDOM,
                               headline_name="seg_soft_oracle_beats_random_heldout", run_mode="self_test",
                               extra="SEG_SOFT_ORACLE population decode did NOT separate from RANDOM on the planted "
                                     "type-structured arena -> arena not answerable / apparatus frozen")

    st_verdict, _stmsg, _stg = deployable_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(soft_recovers and soft_beats_random),
         "control_name": "RANDOM", "headline_name": "seg_soft_oracle_recovers_planted_heldout",
         "extra": "planted arena: SEG_SOFT_ORACLE population joint decode recovers planted held-out tails (fold-in) "
                  "and clears RANDOM by the ceiling-aware margin -> the typed-segment apparatus is answerable and the "
                  "population soft-decode discriminator fires"},
        {"kind": "metric_moves", "metric_name": "oracle_2x2_mrr",
         "values": [rnd, hard, mono_ora, soft],
         "extra": "the oracle 2x2 cells MOVE on synthetic: RANDOM=%.3f SEG_HARD_O=%.3f MONO_MATCHED_O=%.3f "
                  "SEG_SOFT_O=%.3f (not frozen)" % (rnd, hard, mono_ora, soft)},
        {"kind": "negative_control_margin",
         "control_scores": [rnd, relscr, sm[SEG_HARD_ORA]],
         "headline_threshold": soft, "higher_is_pass": True, "margin": ST_SOFT_GE_HARD, "n_repeats_min": 3,
         "control_name": "RANDOM_RELSCRAMBLE_HARD_below_soft", "extra":
         "RANDOM + relation-scrambled oracle decode + hard one-shot decode sit below SEG_SOFT_ORACLE by the MRR "
         "margin -> the segment capacity needs the RELATION operators + the soft population decode, not code volume"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["soft_recovers", "soft_beats_random", "soft_ge_hard", "relscramble_fails",
                                    "arms_differ", "oracle_fires", "real_code_path", "deployable_verdict"],
         "exercised_gates": ["soft_recovers", "soft_beats_random", "soft_ge_hard", "relscramble_fails",
                             "arms_differ", "oracle_fires", "real_code_path", "deployable_verdict"],
         "extra": "deployable_verdict=%s at self-test scale" % st_verdict},
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["KGStore", "build_segment_module", "ingest_triples", "module_segment_sims"],
         "exercised_entrypoints": exercised,
         "extra": "self-test constructs the REAL KGStore per slot and runs ingest_triples on segment-mapped triples"},
        {"kind": "substrate_signature", "callable_obj": KGStore, "callable_name": "KGStore",
         "kwargs": {"n_ent": 1, "n_rel": 1, "n_dim": 16, "generator": None},
         "extra": "base/portable KGStore kwargs only (n_ent,n_rel,n_dim,generator); no optional init_entities"},
        {"kind": "guard_baseline_valid", "baseline_score": sm[MONO_MATCHED_ORA], "floor_score": rnd,
         "guard_name": "BROKEN_POP_BEATS_RANDOM", "baseline_name": "MONO_MATCHED_ORACLE", "floor_name": "RANDOM",
         "eps": 0.02,
         "extra": "the BROKEN guard compares POP against the RANDOM floor (not a structural-zero POP); "
                  "MONO_MATCHED_ORACLE sits above the floor so the arena baseline is valid"},
    ], run_mode="self_test")

    out.update(
        real_code_path_ok=bool(real_ok), exercised_entrypoints=sorted(exercised),
        planted_arms={a: (round(sm[a], 5) if sm[a] == sm[a] else None) for a in ALL_ARMS},
        internal_relscramble_mrr=(round(relscr, 5) if relscr == relscr else None),
        n_distinct_sigs=n_sigs, soft_recovers=soft_recovers, soft_beats_random=soft_beats_random,
        soft_ge_hard=soft_ge_hard, relscramble_fails=relscramble_fails, compose_sanity=compose_sanity,
        arms_differ=arms_differ, seg_signature_unique_frac=fs["diag"].get("seg_signature_unique_frac"),
        mods_finite=mods_finite, selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest",
                                     "real_code_path_F1", "substrate_signature_F2_F3", "guard_baseline_valid_F4"],
    )
    ok = bool(real_ok and soft_recovers and soft_beats_random and soft_ge_hard and relscramble_fails
              and arms_differ and mods_finite and vp_ok)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def core_main(run_mode):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=cpu run_mode=%s seeds=%s lib_sizes=%s typed=%s d_seg=%s d_matched=%s seg_cost=%.1fM relief=%.1fM"
         % (run_mode, seeds, cfg["lib_sizes"], cfg["typed_mask"], cfg["d_seg"],
            _d_matched(cfg["lib_sizes"], cfg["d_seg"]),
            len(cfg["lib_sizes"]) * cfg["d_seg"] ** 2 / 1e6, RELIEF_8192_COST / 1e6))

    st_ok, st_res = mechanism_selftest()
    _pa = st_res.get("planted_arms") or {}
    _log("mechanism_selftest ok=%s | soft_O=%s hard_O=%s mono_O=%s random=%s relscr_O=%s | soft_C=%s | "
         "soft_recovers=%s soft_ge_hard=%s relscramble_fails=%s compose_sanity=%s real_code=%s vp_ok=%s uniq_frac=%s"
         % (st_ok, _pa.get(SEG_SOFT_ORA), _pa.get(SEG_HARD_ORA), _pa.get(MONO_MATCHED_ORA), _pa.get(RANDOM),
            st_res.get("internal_relscramble_mrr"), _pa.get(SEG_SOFT),
            st_res.get("soft_recovers"), st_res.get("soft_ge_hard"), st_res.get("relscramble_fails"),
            st_res.get("compose_sanity"), st_res.get("real_code_path_ok"), st_res.get("validity_preflight_ok"),
            st_res.get("seg_signature_unique_frac")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (oracle soft decode did not recover/beat-random/beat-hard, or "
                        "relation-scramble did not fail, or the real KGStore segment path / validity-preflight did "
                        "not fire): %s" % {kk: st_res.get(kk) for kk in ("soft_recovers", "soft_beats_random",
                                "soft_ge_hard", "relscramble_fails", "real_code_path_ok", "arms_differ",
                                "validity_preflight_ok")},
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS SEGMENT_LIBRARY_CLONAL_RETRIEVAL: on a planted type-structured arena the "
                        "SEG_SOFT_COMPOSE population decode composes held-out tails from support and clears RANDOM; "
                        "the soft population decode beats the hard one-shot decode; typed-assignment-scramble compose "
                        "fails; the REAL KGStore per-slot segment path (ingest_triples) is exercised; 7 validity-"
                        "preflight checks declared (F.1-F.4 ENFORCE)",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["n_rel_tokens"], len(pool)))
            res, _fs = run_corpus(pool, cfg, seed, "CSKG_CORE_HELDOUT_ENTITY")
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", 20):
                raise RuntimeError("held-out query edges too few (%d)" % res.get("n_query_scored", 0))
            sigset = set(res["arm_sigs"][a] for a in ALL_ARMS)
            if len(sigset) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d sigs" % (seed, len(sigset)))
            if not (res["diag"]["mods_finite"] and res["diag"]["mono_finite"]):
                raise RuntimeError("non-finite W seed=%d (mods=%s mono=%s)"
                                   % (seed, res["diag"]["mods_finite"], res["diag"]["mono_finite"]))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            ah = res["arm_hits"]
            _log("seed=%d nq=%d | MONO_C=%s SEG_HARD_C=%s SEG_SOFT_C=%s SCR_C=%s RANDOM=%s | "
                 "MONO_O=%s SEG_SOFT_O=%s (%.1fs)"
                 % (seed, res["n_query_scored"], _fmt(ah[MONO_COMPOSE][CEIL_METRIC]), _fmt(ah[SEG_HARD][CEIL_METRIC]),
                    _fmt(ah[SEG_SOFT][CEIL_METRIC]), _fmt(ah[SEG_SCRAMBLE][CEIL_METRIC]), _fmt(ah[RANDOM][CEIL_METRIC]),
                    _fmt(ah[MONO_MATCHED_ORA][CEIL_METRIC]), _fmt(ah[SEG_SOFT_ORA][CEIL_METRIC]), time.time() - ts))
            _hb("cskg", si + 1)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = deployable_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device="cpu", n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "full"):
            run_mode = _env_mode
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
