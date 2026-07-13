"""NATIVE_CODE_FAMILY_SWEEP: does any GLASS-BOX (closed-form, NO SGD) entity/relation CODE FAMILY carry more
relational geometry through the substrate's OWN native multiplicative-Hebbian store than the store's default
random-bipolar atoms -- WITHOUT learned codes and WITHOUT the GPU? (The DEPLOYABLE half of the native-codes lever.)

THE QUESTION (CITED@notes/research_native_representational_ceiling_levers_2026-07-13.md). The VET-confirmed native
mechanism (exp_native_bind_compose_inductive_entity_cskg_v1: fixed random-bipolar E/R, n_dim=1024, multiplicative
bind key(s,p)=E[s]*R[p]*sqrt(n_dim), one-shot Hebbian W += outer(E[o],key)/n_dim, bilinear readout) lands
NATIVE_ANCHOR_COMPOSE mrr=0.0140 / ORACLE_FOLDIN=0.0231 (MEASURED@data/exp_native_bind_compose_inductive_entity_
cskg_v1/metrics.json). The additive SGD-fit construction reaches mrr=0.1282 (CITED@notes/research_native_
representational_ceiling_levers_2026-07-13.md). The ceiling-levers drill ranked the code FAMILY as a WEAK/NEUTRAL/
NEGATIVE lever (sparse in an unchanged linear W ~= wash; FHRR ~= capacity-equivalent; content/correlated codes
predicted NET-NEGATIVE via crosstalk, CITED@reference_correlation_hurts_associative_store_capacity_decouple_from_
retrieval_2026-07-08.md). This cell TESTS that prediction on the deployable, glass-box axis: swap ONLY the fixed
E/R code family (the store's bind/Hebbian/readout path is bit-identical -- CERT-584/585 code is untouched, atoms
are injected read-only), hold n_dim=1024 FIXED (dimension is settled -- separate ladder), and measure per family the
native ORACLE ceiling AND the native MECHANISM (compose-and-read) MRR + native/oracle fraction on the SAME held-out-
ENTITY arena/split/controls as the baseline.

  CODES_HELP  -> a glass-box structured family raises native ORACLE AND MECHANISM by a pre-set margin over random-
                 bipolar (with must-fails firing) => fixed glass-box codes ARE a deployable lever.
  CODES_DONT  -> all families ~= random-bipolar (or content HURTS) => fixed glass-box codes are NOT the lever; the
                 additive LEARNED construction is the only path (feeds the integration endgame).

CODE FAMILIES (all closed-form, glass-box, NO SGD; injected into the store's E/R only):
  RANDOM_BIPOLAR   : the store default {-1,+1} random atoms. THE REFERENCE (reproduces the baseline arm in-cell).
  BLOCK_SPARSE_BSDC: sparse ternary {-1,0,+1} atoms, random support at density BSDC_DENSITY (Willshaw/Rachkovskij
                     BSDC family; lever 4). Tests sparse-code capacity WITHOUT a matched nonlinear readout (the
                     drill predicts ~wash-to-hurt in an unchanged linear correlation matrix).
  GAUSSIAN_DENSE   : dense continuous N(0,1) atoms. Binarization control -- isolates whether {-1,+1} quantization
                     costs geometry vs a continuous dense code (not in the drill; a justified closed-form control).
  CONTENT_TRIGRAM  : char-trigram CONTENT codes derived from the entity/relation LABEL string (the KGStore content-
                     code option the task names; lever 7). Correlated codes -> tests the "content codes may HURT via
                     crosstalk" prediction directly. UNIQUE property: a held-out entity's content code is KNOWN from
                     its label, so MEMORIZE_CONTENT can carry zero-shot signal WITHOUT any compose (measured).

  FHRR (complex unit-phase) is DELIBERATELY EXCLUDED from this real-bilinear sweep: it requires a divergent complex64
  bind/Hebbian/readout path (phase-addition bind, complex W, real-part readout) that would break the bit-identical
  real arena/controls contract and is NOT a drop-in deployable swap of the CERT-584/585 real store (it would demand
  its own re-validation). The drill ranks it lowest (P_deflated=0.10, capacity-equivalent). It is flagged as a
  separately-scoped complex-path follow-up if the real families are inconclusive. (Scoping call within cell-author
  autonomy; documented per the task's "your call / any other you justify".)

ARMS per family (scored PAIRED on the SAME held-out QUERY edges; UNIFORM L2-normalized cosine readout so candidate
magnitude/popularity cannot confound cross-family comparison; recall is the store's native raw bind, unnormalized):
  NATIVE_ANCHOR_COMPOSE : held-out code REPLACED by L2norm(sum_i W@key(h_i,r_i)) over the entity's SUPPORT edges
                          (the mechanism; family-agnostic real bundle, projected to unit norm to match candidates).
  MEMORIZE_FIXEDCODE    : held-out code = the family's FIXED atom (random families -> ~floor; CONTENT -> known code).
  ORACLE_FOLDIN         : held-out edges folded into a SECOND Hebbian W (sharing bit-identical E/R); fixed family
                          codes recalled -> the family's arena-answerable native ceiling.
  NATIVE_SCRAMBLE       : NATIVE with SUPPORT relation ids permuted -> must-fail (relation-operator control).
  IDENTITY_SHUFFLE      : composed codes assigned to the WRONG held-out entity -> must-fail (identity control).
Family-agnostic shared arms (computed ONCE per seed):
  RANDOM_CODES          : random codes + random recall -> the null bar (family-independent).
  BASELINE_POP          : frequency incumbent (held-out tails train-freq 0 -> ~floor; fit-independence sanity).

CEILING-AWARE, DEGREE-UNBIASED EVAL. Primary metric = FILTERED MRR rank-vs-ALL-N (KGE standard; no sampled-negative
pool -> no popularity/degree bias). Per family H_f = ORACLE_f - RANDOM is the family's MEASURED oracle headroom;
CODES_HELP bands are RATIOS to the RANDOM_BIPOLAR family's own MEASURED oracle/native, so ONE FULL computes both the
reference and the challengers and scores the cross-family lift. Fairness: fair_low_mid degree stratum reported so a
lift cannot be super-hub-confined.

PRE-REG BANDS (picked BEFORE the run; primary = FILTERED MRR; means over seeds; ref = RANDOM_BIPOLAR family):
  ARENA-ANSWERABLE (positive control) : RANDOM_BIPOLAR ORACLE fires (ORACLE_bipolar >= ORACLE_FIRE_RATIO x RANDOM
                                        AND ORACLE_bipolar - RANDOM >= ORACLE_FIRE_ABS).
  CODES_HELP  : EXISTS a non-bipolar family f with ORACLE_f fires AND its scramble+identity must-fails controlled
                (SCRAMBLE_f-RANDOM <= CONTROL_CEIL_FRAC*H_f and IDSHUF_f-RANDOM <= CONTROL_CEIL_FRAC*H_f) AND
                ORACLE_f >= (1+CEIL_RAISE_FRAC)*ORACLE_bipolar AND NATIVE_f >= (1+CEIL_RAISE_FRAC)*NATIVE_bipolar AND
                NATIVE_f > RANDOM AND the lift holds on the fair low+mid degree stratum => fixed glass-box codes ARE
                a deployable lever.
  MIDDLE (ceiling-only) : some f raises ORACLE by (1+CEIL_RAISE_FRAC) but its NATIVE mechanism does NOT follow ->
                          the recoverable ceiling moved but the deployable compose path did not exploit it.
  CODES_DONT (structured hurts) : some f (predicted: CONTENT) has ORACLE_f <= (1-HURT_FRAC)*ORACLE_bipolar ->
                                  structured/correlated codes HURT via crosstalk; learned codes needed.
  CODES_DONT (wash) : all non-bipolar families sit in [1-HURT_FRAC, 1+CEIL_RAISE_FRAC) x the bipolar reference on
                      BOTH oracle and native -> fixed glass-box codes are not the lever; learned codes needed.
  Gated INCONCLUSIVE if RANDOM_BIPOLAR ORACLE does not fire (arena not answerable), too few held-out queries, or
  RANDOM beats POP by a ceiling-relative margin (broken harness).

FOUR VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight):
  (1) positive_control_passes : on a planted HOMOPHILIC-LABEL arena, RANDOM_BIPOLAR ORACLE recovers planted held-out
                                tails and clears RANDOM by the ceiling-aware ratio+abs fire gate.
  (2) metric_moves            : held-out MRR MOVES across [RANDOM, MEMORIZE_bipolar, NATIVE_bipolar, ORACLE_bipolar].
  (3) negative_control_margin : RANDOM + NATIVE_SCRAMBLE + IDENTITY_SHUFFLE (content family) sit below NATIVE_CONTENT
                                by an MRR margin, deterministically (>=3 controls).
  (4) full_gates_exercised    : aggregate_and_verdict_families runs on the planted per-seed, firing every fail-closed
                                gate.
  PLUS the cell-specific discriminator: on the planted homophilic arena, the STRUCTURED family (CONTENT_TRIGRAM,
  whose codes cluster by the planted group) BEATS RANDOM_BIPOLAR on the MEMORIZE arm by SELFTEST_STRUCT_MARGIN --
  proving the harness can DETECT a genuine code-family advantage WHEN ONE EXISTS (and, by the wash prediction on real
  data, distinguishes that from the null).

## Compute architecture
class (b) sequential-CPU with justification: the native store is ONE-SHOT Hebbian (NO SGD, NO epochs); the whole
sweep is cheap CPU (per family: 2 chunked-matmul ingests + a few (nq,n_dim)@(n_dim,N) chunked scorings). No gradient
training at all -> remote_cpu_queue (device=cpu). 4 families x 3 seeds; GPU unnecessary (small one-shot matmuls).
Storage: sharded per-atom E/R (each entity its own code) + the store's native Hebbian W (a proven CERT-584/585
primitive, untouched); the ONLY new object is the per-ENTITY L2-normed superposition of the entity's own support-
edge recall vectors -- read-only, no mutation of KGStore's bind/Hebbian/readout code.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 4 families x 5 arms + 2 shared -> >=10 distinct score sigs/seed.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: raw hits@k has a CEILING; FIX = primary FILTERED MRR + RATIO-to-reference bands ->
#   discriminator_reachability OK by construction (bands scale to whatever oracle each family MEASURES).
# - baseline_in_band: RANDOM_BIPOLAR ORACLE must fire (>=3x RANDOM AND headroom>=0.003); RANDOM/POP near 1/N floor.
# - discriminator survives scale: analytical (a fixed random-atom entity code is a random LABEL, not a structure-
#   derived position, so the memorize null persists at ANY N; a content/correlated code's crosstalk grows with load,
#   not shrinks) + self-test fires the STRUCTURED-beats-RANDOM discriminator + scramble/idshuf must-fails on a planted
#   homophilic arena where a structured code IS relationally consistent.
# - HARD/HELP strictly above floor: CEIL_RAISE_FRAC=0.25 clears the [1-HURT_FRAC,1+CEIL_RAISE_FRAC) wash band.
# - HP_SCOPE: the CODES_HELP gates apply to NON-BIPOLAR families' NATIVE+ORACLE only. RANDOM_BIPOLAR ORACLE = the
#   arena-answerable positive control (must fire); RANDOM/SCRAMBLE/IDSHUF = must-not-clear-bar controls; MEMORIZE =
#   native memorize head-to-head (and the CONTENT zero-shot probe); POP = fit-independence sanity.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 4 families + shared arms + >=10 sigs.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- all fracs/ratios pre-registered, NOT tuned on real data;
#   CODES_HELP bands are RATIOS to the in-run MEASURED reference family.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the docstring/prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-family flush prints).

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
from collections import defaultdict
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
    stratify_by_tail_degree, PRIMARY_K,
)
# Reuse the baseline's split + native read-path helpers VERBATIM so the arena/split/controls are the SAME primitive.
from experiments.exp_native_bind_compose_inductive_entity_cskg_v1 import (  # noqa: E402
    build_heldout_entity_split_ac, native_query_recall, score_from_codes, random_scores,
)
from hdlab.kg_traversal import KGStore  # noqa: E402  (the LIVE store; E/R injected read-only, bind/Hebbian untouched)

ANCHOR_NAME = "native_code_family_sweep_cskg_v1"

# ---- Code families (all glass-box, closed-form, NO SGD) ----
RANDOM_BIPOLAR = "RANDOM_BIPOLAR"
BLOCK_SPARSE = "BLOCK_SPARSE_BSDC"
GAUSSIAN_DENSE = "GAUSSIAN_DENSE"
CONTENT_TRIGRAM = "CONTENT_TRIGRAM"
FAMILIES = [RANDOM_BIPOLAR, BLOCK_SPARSE, GAUSSIAN_DENSE, CONTENT_TRIGRAM]
REFERENCE_FAMILY = RANDOM_BIPOLAR
FAM_SEED_OFFSET = {RANDOM_BIPOLAR: 1, BLOCK_SPARSE: 3, GAUSSIAN_DENSE: 2, CONTENT_TRIGRAM: 4}
BSDC_DENSITY = 0.10   # sparse-ternary atom density (fraction of nonzero coords); Rachkovskij/Willshaw BSDC regime

# ---- Per-family arm names ----
NATIVE = "NATIVE_ANCHOR_COMPOSE"
MEMORIZE = "MEMORIZE_FIXEDCODE"
ORACLE = "ORACLE_FOLDIN"
SCRAMBLE = "NATIVE_SCRAMBLE"
IDSHUF = "IDENTITY_SHUFFLE"
FAM_ARMS = [NATIVE, MEMORIZE, ORACLE, SCRAMBLE, IDSHUF]
# ---- Shared (family-agnostic) arms ----
RANDOM = "RANDOM_CODES"
POP = "BASELINE_POP"

# ---- CEILING-AWARE, DEGREE-UNBIASED evaluation ----
EVAL_KS = (1, 3, 10, 100)
CEIL_METRIC = "mrr"
ORACLE_FIRE_RATIO = 3.0
ORACLE_FIRE_ABS = 0.003
CEIL_RAISE_FRAC = 0.25     # a family must raise oracle AND native by >=25% over the bipolar reference to COUNT as HELP
HURT_FRAC = 0.25           # a family with oracle <= 0.75x bipolar reference => structured codes HURT (crosstalk)
CONTROL_CEIL_FRAC = 0.25   # scramble/identity must-fail: headroom over RANDOM must stay <= 0.25 * that family's H_f
MIN_HELDOUT = 20
MIN_STRAT_Q = 8
BROKEN_EPS = 0.005
PRIMARY_METRIC = "hits@%d" % PRIMARY_K

# ---- Held-out-entity split knobs (IDENTICAL to the baseline arena; NOT tuned on real data) ----
HELDOUT_ENTITY_FRAC = 0.15
SUPPORT_FRAC = 0.5

# ---- self-test planted thresholds on the PRIMARY metric (MRR); calibrated on the synthetic homophilic grid ----
SELFTEST_ORACLE_MRR_MIN = 0.15         # RANDOM_BIPOLAR ORACLE recovers planted held-out tails
SELFTEST_STRUCT_MARGIN = 0.02          # MEMORIZE_CONTENT - MEMORIZE_RANDOM_BIPOLAR (structured beats random)
SELFTEST_CONTENT_SCRAMBLE_MARGIN = 0.02  # NATIVE_CONTENT - SCRAMBLE_CONTENT
SELFTEST_CONTENT_IDSHUF_MARGIN = 0.02    # NATIVE_CONTENT - IDSHUF_CONTENT
SELFTEST_MIN_HO = 8

SCORE_CHUNK = 512

# Config profiles. SELFTEST/FULL exercise the SAME split->inject->ingest->compose->score->verdict path.
SELFTEST_CFG = dict(n_dim=256, heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0,
                    min_heldout=SELFTEST_MIN_HO)
# FULL: n_dim=1024 = the store default + CERT-584/585 chain-grade regime + the baseline's FULL n_dim (so the
# RANDOM_BIPOLAR ORACLE in this cell is directly comparable to the baseline's 0.0231). CSKG core k_core=12,
# same held-out-entity split (frac=0.15, support_frac=0.5), n_heldout_eval=3000, seeds=[7,13,17] as the baseline.
FULL_CFG = dict(n_dim=1024, heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                n_heldout_eval=3000, min_heldout=MIN_HELDOUT, seeds=[7, 13, 17])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


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
# Glass-box code families (closed-form; injected into KGStore.E / KGStore.R read-only).
# ---------------------------------------------------------------------------

def _bipolar(m, n, g):
    return (torch.randint(0, 2, (m, n), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float32)


def _sparse_ternary(m, n, g, density):
    """BSDC-style sparse ternary {-1,0,+1}: each row has k=round(density*n) random-support coords with random signs."""
    k = max(1, int(round(density * n)))
    X = torch.zeros(m, n, dtype=torch.float32)
    idx = torch.argsort(torch.rand(m, n, generator=g), dim=1)[:, :k]
    signs = (torch.randint(0, 2, (m, k), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float32)
    X.scatter_(1, idx, signs)
    return X


def _trigram_codes(i2lbl, m, n_dim, cache):
    """Char-trigram CONTENT code: sum of a deterministic +-1 hypervector per character 3-gram of the label string.
    Correlated across entities that share trigrams (that is the point). Deterministic (label-seeded hashes); cached."""
    X = torch.zeros(m, n_dim, dtype=torch.float32)
    for i in range(m):
        lbl = str(i2lbl.get(i, "")).lower()
        s = "#" + lbl + "#"
        grams = [s[j:j + 3] for j in range(max(1, len(s) - 2))]
        acc = torch.zeros(n_dim, dtype=torch.float32)
        for gm in grams:
            v = cache.get(gm)
            if v is None:
                hh = int.from_bytes(hashlib.blake2b(gm.encode("utf-8"), digest_size=8).digest(), "big")
                gg = torch.Generator(device="cpu").manual_seed(hh % (2 ** 63 - 1))
                v = (torch.randint(0, 2, (n_dim,), generator=gg, dtype=torch.int8) * 2 - 1).to(torch.float32)
                cache[gm] = v
            acc += v
        X[i] = acc
    return X


def build_family_codes(family, N, n_rel, n_dim, seed, i2ent, i2rel, tvec_cache):
    """Return (E [N,n_dim], R [n_rel,n_dim]) float32 for the given glass-box family. NO SGD anywhere."""
    g = torch.Generator(device="cpu").manual_seed(seed * 100000 + n_dim + FAM_SEED_OFFSET[family])
    if family == RANDOM_BIPOLAR:
        return _bipolar(N, n_dim, g), _bipolar(n_rel, n_dim, g)
    if family == GAUSSIAN_DENSE:
        return torch.randn(N, n_dim, generator=g, dtype=torch.float32), \
            torch.randn(n_rel, n_dim, generator=g, dtype=torch.float32)
    if family == BLOCK_SPARSE:
        return _sparse_ternary(N, n_dim, g, BSDC_DENSITY), _sparse_ternary(n_rel, n_dim, g, BSDC_DENSITY)
    if family == CONTENT_TRIGRAM:
        E = _trigram_codes(i2ent, N, n_dim, tvec_cache)
        R = _trigram_codes(i2rel, n_rel, n_dim, tvec_cache)
        return E, R
    raise ValueError("unknown family %r" % family)


def _l2norm_rows(X, eps=1e-8):
    nrm = torch.linalg.norm(X, dim=1, keepdim=True)
    return X / (nrm + eps)


# ---------------------------------------------------------------------------
# Native store with INJECTED family codes (KGStore bind/Hebbian/readout code untouched; only E/R are swapped).
# ---------------------------------------------------------------------------

def build_store_with_codes(E, R, n_dim, seed, train_int, fold_in=None):
    """A KGStore whose E/R are the family codes (shared by reference across train + oracle stores; only W differs)."""
    N = E.shape[0]; n_rel = R.shape[0]
    g = torch.Generator(device="cpu").manual_seed(seed * 13 + 7)
    # Base constructor ONLY (portable across KGStore versions; the random E/R it fills are immediately overwritten
    # by the injected family codes below -- do NOT pass version-specific kwargs). Bind/Hebbian/readout untouched.
    store = KGStore(n_ent=N, n_rel=n_rel, n_dim=n_dim, generator=g)
    store.E = E
    store.R = R
    tri = torch.from_numpy(train_int).long()
    if fold_in is not None and fold_in.shape[0] > 0:
        tri = torch.cat([tri, torch.from_numpy(fold_in).long()], dim=0)
    store.ingest_triples(tri)
    return store


def compose_codes_l2(store, support_int, N, rel_perm=None):
    """E_derived[t] = L2norm(sum over t's support edges of W@key(h_i,r_i)) -- family-agnostic real bundle projected
    to unit norm (degree-invariant, no magnitude confound). Returns (mask, composed_rows [n_hold,n_dim]), support_deg.
    rel_perm scrambles support relation ids."""
    E = store.E; R = store.R; W = store.W; sq = store.sq
    support_deg = np.zeros(N, dtype=np.int64)
    if support_int.shape[0] == 0:
        return (torch.zeros(N, dtype=torch.bool), torch.zeros(0, store.n_dim)), support_deg
    h = torch.from_numpy(support_int[:, 0]).long()
    r_np = support_int[:, 1].copy()
    if rel_perm is not None:
        r_np = rel_perm[r_np]
    r = torch.from_numpy(r_np).long()
    t = torch.from_numpy(support_int[:, 2]).long()
    Ks = (E[h] * R[r] * sq)
    recall = Ks @ W.T
    acc = torch.zeros(N, store.n_dim, dtype=torch.float32)
    acc.index_add_(0, t, recall)
    cnt = torch.zeros(N, dtype=torch.float32)
    cnt.index_add_(0, t, torch.ones(t.shape[0], dtype=torch.float32))
    mask = cnt > 0
    composed = _l2norm_rows(acc[mask])
    support_deg = cnt.numpy().astype(np.int64)
    return (mask, composed), support_deg


def patch_codebook(En, mask, composed):
    """Return a candidate codebook = En (L2-normed family codes) with the held-out (mask) rows replaced by composed."""
    Ep = En.clone()
    if composed.shape[0] > 0:
        Ep[mask] = composed
    return Ep


def idshuf_codebook(En, mask, composed, support_deg, hold_ids, seed):
    """Assign each composed held-out code to a DIFFERENT held-out entity (breaks entity-identity binding)."""
    Ep = En.clone()
    ids = [t for t in range(En.shape[0]) if support_deg[t] > 0 and t in hold_ids]
    if len(ids) <= 1:
        if composed.shape[0] > 0:
            Ep[mask] = composed
        return Ep
    row_of = {int(t): j for j, t in enumerate(torch.where(mask)[0].tolist())}
    rng = np.random.default_rng(seed * 7919 + 1)
    perm = rng.permutation(len(ids))
    if np.all(perm == np.arange(len(ids))):
        perm = np.roll(perm, 1)
    for j, t in enumerate(ids):
        src_t = ids[int(perm[j])]
        Ep[t] = composed[row_of[src_t]]
    return Ep


# ---------------------------------------------------------------------------
# One family: fit train + oracle stores, compose, score all arms PAIRED on the same query edges.
# ---------------------------------------------------------------------------

def run_family(family, E, R, n_dim, seed, train_int, support_int, query_int, hold_all, hold_ids, N, all_true,
               node_degree):
    En = _l2norm_rows(E)
    store = build_store_with_codes(E, R, n_dim, seed, train_int)
    store_oracle = build_store_with_codes(E, R, n_dim, seed, train_int, fold_in=hold_all)

    (mask, comp), support_deg = compose_codes_l2(store, support_int, N)
    n_rel = R.shape[0]
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)
    (mask_s, comp_s), _ = compose_codes_l2(store, support_int, N, rel_perm=rel_perm)
    Ep = patch_codebook(En, mask, comp)
    Ep_s = patch_codebook(En, mask_s, comp_s)
    Ep_i = idshuf_codebook(En, mask, comp, support_deg, hold_ids, seed)

    recall_train = native_query_recall(store, query_int)
    recall_oracle = native_query_recall(store_oracle, query_int)

    arm_scores = {
        NATIVE: score_from_codes(recall_train, Ep),
        MEMORIZE: score_from_codes(recall_train, En),
        SCRAMBLE: score_from_codes(recall_train, Ep_s),
        IDSHUF: score_from_codes(recall_train, Ep_i),
        ORACLE: score_from_codes(recall_oracle, En),
    }
    arm_metric, arm_sig = {}, {}
    for name, sc in arm_scores.items():
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())

    strat, _tert = stratify_by_tail_degree(query_int, node_degree)
    fair_mask = (strat == 0) | (strat == 1)
    fair = {}
    for name in [NATIVE, MEMORIZE, ORACLE]:
        idx = np.where(fair_mask)[0]
        if idx.size >= MIN_STRAT_Q:
            sub = filtered_hits_from_scores(arm_scores[name][idx], query_int[idx], all_true, ks=(PRIMARY_K,))
            fair[name] = round(sub["mrr"], 6)
        else:
            fair[name] = float("nan")
    matnorm = store.matrix_norm()
    return dict(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in arm_metric[a].items() if kk != "n"} for a in FAM_ARMS},
        arm_n={a: arm_metric[a]["n"] for a in FAM_ARMS},
        arm_sigs=arm_sig, fair_lowmid_mrr=fair, matrix_norm=round(float(matnorm), 4),
        support_deg=support_deg,
    )


# ---------------------------------------------------------------------------
# One seed: shared arms + all families.
# ---------------------------------------------------------------------------

def run_seed(pool_lbl, cfg, seed, corpus_name):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    i2ent = {v: k for k, v in ent2i.items()}
    i2rel = {v: k for k, v in rel2i.items()}
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = build_heldout_entity_split_ac(
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

    result = dict(corpus=corpus_name, seed=seed, N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]),
                  n_heldout_entities=len(hold_ids), n_support=int(support_int.shape[0]),
                  n_query_total=n_query_total, n_query_scored=int(query_int.shape[0]), n_cold=int(n_cold),
                  n_dim=int(cfg["n_dim"]), heldout_entity_frac=cfg["heldout_entity_frac"],
                  support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    # shared, family-agnostic arms (computed once)
    rand_sc = random_scores(N, query_int, cfg["n_dim"], seed)
    rand_m = filtered_hits_from_scores(rand_sc, query_int, all_true, ks=EVAL_KS)
    pop_m, pop_rank = pop_hits(gd.rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    strat, _t = stratify_by_tail_degree(query_int, gd.node_degree)
    fair_idx = np.where((strat == 0) | (strat == 1))[0]
    rand_fair = float("nan")
    if fair_idx.size >= MIN_STRAT_Q:
        rand_fair = round(filtered_hits_from_scores(rand_sc[fair_idx], query_int[fair_idx], all_true,
                                                    ks=(PRIMARY_K,))["mrr"], 6)
    shared = dict(
        RANDOM={kk: round(vv, 6) for kk, vv in rand_m.items() if kk != "n"},
        POP={kk: round(vv, 6) for kk, vv in pop_m.items() if kk != "n"},
        RANDOM_fair_lowmid_mrr=rand_fair,
        RANDOM_sig=_sig(rand_sc.numpy()[:min(64, rand_sc.shape[0])].ravel()),
        POP_sig=_sig(pop_rank.astype(np.float64)),
    )

    tvec_cache = {}
    fam_results = {}
    all_sigs = [shared["RANDOM_sig"], shared["POP_sig"]]
    for fam in FAMILIES:
        E, R = build_family_codes(fam, N, n_rel, cfg["n_dim"], seed, i2ent, i2rel, tvec_cache)
        fr = run_family(fam, E, R, cfg["n_dim"], seed, train_int, support_int, query_int, hold_all, hold_ids, N,
                        all_true, gd.node_degree)
        fam_results[fam] = {k: v for k, v in fr.items() if k != "support_deg"}
        all_sigs.extend(fr["arm_sigs"].values())
        _log("  seed=%d fam=%-16s MRR NATIVE=%s MEMORIZE=%s ORACLE=%s SCRAMBLE=%s IDSHUF=%s matnorm=%s"
             % (seed, fam, _fmt(fr["arm_hits"][NATIVE][CEIL_METRIC]), _fmt(fr["arm_hits"][MEMORIZE][CEIL_METRIC]),
                _fmt(fr["arm_hits"][ORACLE][CEIL_METRIC]), _fmt(fr["arm_hits"][SCRAMBLE][CEIL_METRIC]),
                _fmt(fr["arm_hits"][IDSHUF][CEIL_METRIC]), fr["matrix_norm"]))
    result["shared"] = shared
    result["families"] = fam_results
    result["n_distinct_sigs"] = len(set(all_sigs))
    return result


# ---------------------------------------------------------------------------
# Aggregate + cross-family verdict.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _fam_mrr(ps, fam, arm):
    return ps["families"][fam]["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def _fam_fair(ps, fam, arm):
    return ps["families"][fam]["fair_lowmid_mrr"].get(arm, float("nan"))


def _shared_mrr(ps, which):
    return ps["shared"][which].get(CEIL_METRIC, float("nan"))


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def aggregate_and_verdict_families(per_seed):
    def agg_fam(fam, arm):
        return _nm([_fam_mrr(ps, fam, arm) for ps in per_seed])

    def agg_fam_fair(fam, arm):
        return _nm([_fam_fair(ps, fam, arm) for ps in per_seed])

    fam_m = {fam: {arm: agg_fam(fam, arm) for arm in FAM_ARMS} for fam in FAMILIES}
    fam_fair = {fam: {arm: agg_fam_fair(fam, arm) for arm in [NATIVE, MEMORIZE, ORACLE]} for fam in FAMILIES}
    rand_m = _nm([_shared_mrr(ps, "RANDOM") for ps in per_seed])
    pop_m = _nm([_shared_mrr(ps, "POP") for ps in per_seed])
    rand_fair = _nm([ps["shared"].get("RANDOM_fair_lowmid_mrr", float("nan")) for ps in per_seed])
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))

    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {fam: {arm: {mk: _nm([ps["families"][fam]["arm_hits"][arm].get(mk, float("nan"))
                                     for ps in per_seed]) for mk in metric_keys} for arm in FAM_ARMS}
                for fam in FAMILIES}

    ref = REFERENCE_FAMILY
    ref_oracle = fam_m[ref][ORACLE]
    ref_native = fam_m[ref][NATIVE]

    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")

    per_family = {}
    for fam in FAMILIES:
        o = fam_m[fam][ORACLE]; nat = fam_m[fam][NATIVE]
        scr = fam_m[fam][SCRAMBLE]; ids = fam_m[fam][IDSHUF]
        H = _sub(o, rand_m)
        o_ratio_rand = _ratio(o, rand_m)
        oracle_fires = bool(H == H and H >= ORACLE_FIRE_ABS and o_ratio_rand == o_ratio_rand
                            and o_ratio_rand >= ORACLE_FIRE_RATIO)
        control_ceil = (CONTROL_CEIL_FRAC * H) if H == H else float("nan")
        d_scr = _sub(scr, rand_m); d_ids = _sub(ids, rand_m)
        scr_ctrl = bool(d_scr == d_scr and control_ceil == control_ceil and d_scr <= control_ceil)
        ids_ctrl = bool(d_ids == d_ids and control_ceil == control_ceil and d_ids <= control_ceil)
        o_ratio_ref = _ratio(o, ref_oracle)
        n_ratio_ref = _ratio(nat, ref_native)
        native_beats_rand = bool(nat == nat and rand_m == rand_m and nat > rand_m)
        fair_native = fam_fair[fam][NATIVE]
        fair_holds = bool(fair_native == fair_native and rand_fair == rand_fair and fair_native >= rand_fair)
        is_ref = (fam == ref)
        helps = bool((not is_ref) and oracle_fires and scr_ctrl and ids_ctrl and native_beats_rand and fair_holds
                     and o_ratio_ref == o_ratio_ref and o_ratio_ref >= (1.0 + CEIL_RAISE_FRAC)
                     and n_ratio_ref == n_ratio_ref and n_ratio_ref >= (1.0 + CEIL_RAISE_FRAC))
        ceiling_only = bool((not is_ref) and oracle_fires and o_ratio_ref == o_ratio_ref
                            and o_ratio_ref >= (1.0 + CEIL_RAISE_FRAC)
                            and not (n_ratio_ref == n_ratio_ref and n_ratio_ref >= (1.0 + CEIL_RAISE_FRAC)))
        hurts = bool((not is_ref) and o_ratio_ref == o_ratio_ref and o_ratio_ref <= (1.0 - HURT_FRAC))
        per_family[fam] = dict(
            oracle_mrr=_rnd(o), native_mrr=_rnd(nat), memorize_mrr=_rnd(fam_m[fam][MEMORIZE]),
            scramble_mrr=_rnd(scr), idshuf_mrr=_rnd(ids), oracle_headroom=_rnd(H),
            oracle_ratio_vs_random=(round(o_ratio_rand, 3) if (o_ratio_rand == o_ratio_rand
                                    and o_ratio_rand != float("inf")) else None),
            oracle_ratio_vs_ref=(round(o_ratio_ref, 3) if (o_ratio_ref == o_ratio_ref
                                 and o_ratio_ref != float("inf")) else None),
            native_ratio_vs_ref=(round(n_ratio_ref, 3) if (n_ratio_ref == n_ratio_ref
                                 and n_ratio_ref != float("inf")) else None),
            fair_lowmid_native_mrr=_rnd(fair_native),
            oracle_fires=oracle_fires, scramble_controlled=scr_ctrl, idshuf_controlled=ids_ctrl,
            native_beats_random=native_beats_rand, fair_holds=fair_holds,
            helps=helps, ceiling_only=ceiling_only, hurts=hurts,
            spectrum={arm: {mk: _rnd(spectrum[fam][arm][mk]) for mk in metric_keys} for arm in FAM_ARMS},
        )

    ref_oracle_fires = per_family[ref]["oracle_fires"]
    enough_heldout = bool(n_query >= MIN_HELDOUT)
    broken = bool(rand_m == rand_m and pop_m == pop_m and (rand_m - pop_m) > max(BROKEN_EPS, 0.0))
    help_families = [f for f in FAMILIES if per_family[f]["helps"]]
    ceiling_families = [f for f in FAMILIES if per_family[f]["ceiling_only"]]
    hurt_families = [f for f in FAMILIES if per_family[f]["hurts"]]

    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif broken:
        verdict = "BROKEN_TEST_RANDOM_BEATS_POP"
    elif not ref_oracle_fires:
        verdict = "INCONCLUSIVE_REF_ORACLE_UNDERFIT"
    elif help_families:
        verdict = "CODES_HELP_GLASSBOX_STRUCTURED_RAISES_NATIVE"
    elif ceiling_families:
        verdict = "MIDDLE_CEILING_UP_MECHANISM_LAGS"
    elif hurt_families:
        verdict = "CODES_DONT_STRUCTURED_HURTS_LEARNED_NEEDED"
    else:
        verdict = "CODES_DONT_FIXED_GLASSBOX_NOT_LEVER_LEARNED_NEEDED"

    def _famtab(fam):
        pf = per_family[fam]
        return ("%s[O=%s N=%s M=%s | O/ref=%s N/ref=%s fires=%s scrCtrl=%s idCtrl=%s fair=%s]"
                % (fam, _fmt(pf["oracle_mrr"] if pf["oracle_mrr"] is not None else float("nan")),
                   _fmt(pf["native_mrr"] if pf["native_mrr"] is not None else float("nan")),
                   _fmt(pf["memorize_mrr"] if pf["memorize_mrr"] is not None else float("nan")),
                   pf["oracle_ratio_vs_ref"], pf["native_ratio_vs_ref"], pf["oracle_fires"],
                   pf["scramble_controlled"], pf["idshuf_controlled"], pf["fair_holds"]))

    verdict_msg = (
        "%s || nq=%d n_dim=%s RANDOM=%s POP=%s ref=%s || %s || HELP=%s CEILING_ONLY=%s HURT=%s || bands: "
        "CEIL_RAISE_FRAC=%.2f HURT_FRAC=%.2f CONTROL_CEIL_FRAC=%.2f ORACLE_FIRE(>=%.1fx&>=%.3f) ref_oracle_fires=%s "
        "broken=%s seeds=%d"
        % (verdict, n_query, str(per_seed[0].get("n_dim")), _fmt(rand_m), _fmt(pop_m), ref,
           " | ".join(_famtab(f) for f in FAMILIES), help_families, ceiling_families, hurt_families,
           CEIL_RAISE_FRAC, HURT_FRAC, CONTROL_CEIL_FRAC, ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS,
           ref_oracle_fires, broken, len(per_seed)))

    gates = dict(
        verdict=verdict, ceil_metric=CEIL_METRIC, reference_family=ref,
        random_mrr=_rnd(rand_m), pop_mrr=_rnd(pop_m), random_fair_lowmid_mrr=_rnd(rand_fair),
        ref_oracle_mrr=_rnd(ref_oracle), ref_native_mrr=_rnd(ref_native),
        per_family=per_family, help_families=help_families, ceiling_only_families=ceiling_families,
        hurt_families=hurt_families,
        ref_oracle_fires=ref_oracle_fires, enough_heldout=enough_heldout, broken=broken,
        n_query_scored=n_query, primary_k=PRIMARY_K,
        bands=dict(CEIL_METRIC=CEIL_METRIC, ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS,
                   CEIL_RAISE_FRAC=CEIL_RAISE_FRAC, HURT_FRAC=HURT_FRAC, CONTROL_CEIL_FRAC=CONTROL_CEIL_FRAC,
                   MIN_HELDOUT=MIN_HELDOUT, BSDC_DENSITY=BSDC_DENSITY, HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC,
                   SUPPORT_FRAC=SUPPORT_FRAC, families=FAMILIES),
    )
    return verdict, verdict_msg, gates


def _rnd(x, nd=6):
    return round(x, nd) if (isinstance(x, float) and x == x) else (x if x is not None else None)


# ---------------------------------------------------------------------------
# Planted HOMOPHILIC-LABEL arena: group-encoding labels so CONTENT_TRIGRAM codes cluster by group (a structured code
# genuinely aligned with the latent groups) while RANDOM_BIPOLAR codes are group-agnostic. Same edge structure as the
# baseline planted arena: members bind to a group anchor via group relations -> the store's own recall is
# relationally consistent, so ORACLE fires and scramble/identity controls collapse.
# ---------------------------------------------------------------------------

def build_planted_homophilic_arena(seed, n_groups=8, members_per_group=12, rels_per_group=3, anchor_repeat=6,
                                   member_edges=4):
    rng = np.random.default_rng(seed * 100019 + 3)
    groups, ganchor, grels = [], [], []
    for g in range(n_groups):
        groups.append(["g%02dm%03d" % (g, m) for m in range(members_per_group)])
        ganchor.append("g%02danchor" % g)
        grels.append(["g%02dr%d" % (g, r) for r in range(rels_per_group)])
    anchor_edges, member_edges_l = [], []
    for g in range(n_groups):
        M = groups[g]; RG = grels[g]; A = ganchor[g]
        for a in M:
            for r in RG:
                for _ in range(anchor_repeat):
                    anchor_edges.append((a, r, A))
        for m in M:
            others = [x for x in M if x != m]
            for _ in range(member_edges):
                a = others[int(rng.integers(len(others)))]
                r = RG[int(rng.integers(len(RG)))]
                member_edges_l.append((a, r, m))
    member_edges_l = list(dict.fromkeys(member_edges_l))
    return anchor_edges + member_edges_l


# ---------------------------------------------------------------------------
# Mechanism self-test.
# ---------------------------------------------------------------------------

def _selftest_store_injection_smoke():
    """Directly exercise build_store_with_codes against the REAL KGStore constructor + injection path so a
    signature/injection mismatch (e.g. a version-specific kwarg the remote KGStore lacks) fails LOCALLY at self-test,
    not at the remote dispatch gate. Independent of the arena. Raises AssertionError/TypeError loudly on breakage."""
    N, n_rel, n_dim = 6, 2, 16
    g = torch.Generator(device="cpu").manual_seed(1)
    E = _bipolar(N, n_dim, g)
    R = _bipolar(n_rel, n_dim, g)
    train_int = np.array([[0, 0, 1], [1, 1, 2], [2, 0, 3], [3, 1, 4]], dtype=np.int64)
    store = build_store_with_codes(E, R, n_dim, 1, train_int)
    assert torch.equal(store.E, E), "injected E is not on the store (injection path broken)"
    assert torch.equal(store.R, R), "injected R is not on the store (injection path broken)"
    assert tuple(store.W.shape) == (n_dim, n_dim), "W shape wrong after ingest"
    assert float(store.matrix_norm()) > 0.0, "W is empty after ingest (Hebbian write did not run)"
    # oracle fold-in path must accept the same portable constructor too
    store_o = build_store_with_codes(E, R, n_dim, 1, train_int, fold_in=np.array([[4, 0, 5]], dtype=np.int64))
    assert float(store_o.matrix_norm()) > 0.0, "oracle fold-in store W empty"
    return dict(store_injection_smoke="ok", W_norm=round(float(store.matrix_norm()), 4))


def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body():
    injection_smoke = _selftest_store_injection_smoke()
    pool = build_planted_homophilic_arena(7)
    cfg = dict(SELFTEST_CFG)
    res = run_seed(pool, cfg, 7, "PLANTED_HOMOPHILIC_HELDOUT_ENTITY")
    out = dict(n_grid_entities=res.get("N"), n_heldout_entities=res.get("n_heldout_entities"),
               n_support=res.get("n_support"), n_query=res.get("n_query_scored"), n_cold=res.get("n_cold"),
               n_dim=res.get("n_dim"), store_injection_smoke=injection_smoke)
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted grid produced too few held-out-entity queries (%s)" % res.get("n_query_scored")
        return False, out

    fam = res["families"]
    shared = res["shared"]

    def M(f, arm):
        return fam[f]["arm_hits"][arm].get(CEIL_METRIC, float("nan"))

    rand_m = shared["RANDOM"].get(CEIL_METRIC, float("nan"))
    pop_m = shared["POP"].get(CEIL_METRIC, float("nan"))
    ref_oracle = M(RANDOM_BIPOLAR, ORACLE)
    oracle_ratio = _ratio(ref_oracle, rand_m)

    ref_oracle_recovers = bool(ref_oracle == ref_oracle and ref_oracle >= SELFTEST_ORACLE_MRR_MIN)
    ref_oracle_fires = bool((ref_oracle - rand_m) >= ORACLE_FIRE_ABS and oracle_ratio == oracle_ratio
                            and oracle_ratio >= ORACLE_FIRE_RATIO)
    struct_margin = M(CONTENT_TRIGRAM, MEMORIZE) - M(RANDOM_BIPOLAR, MEMORIZE)
    structured_beats_random = bool(struct_margin == struct_margin and struct_margin >= SELFTEST_STRUCT_MARGIN)
    content_scr_margin = M(CONTENT_TRIGRAM, NATIVE) - M(CONTENT_TRIGRAM, SCRAMBLE)
    content_ids_margin = M(CONTENT_TRIGRAM, NATIVE) - M(CONTENT_TRIGRAM, IDSHUF)
    content_scramble_fails = bool(content_scr_margin == content_scr_margin
                                  and content_scr_margin >= SELFTEST_CONTENT_SCRAMBLE_MARGIN)
    content_idshuf_fails = bool(content_ids_margin == content_ids_margin
                                and content_ids_margin >= SELFTEST_CONTENT_IDSHUF_MARGIN)
    pop_at_floor = bool(pop_m == pop_m and pop_m <= max(rand_m, 0.02) + BROKEN_EPS)
    n_sigs = res.get("n_distinct_sigs", 0)
    arms_differ = bool(n_sigs >= 10)

    # VACUOUS-SMOKE guard: the STRUCTURED code must genuinely out-rank random-bipolar on the planted arena.
    assert_discriminator_fires(bool(struct_margin <= SELFTEST_STRUCT_MARGIN), control_name="RANDOM_BIPOLAR_MEMORIZE",
                               headline_name="content_structured_code_beats_random_bipolar_memorize",
                               run_mode="self_test",
                               extra="CONTENT_TRIGRAM did not beat RANDOM_BIPOLAR on MEMORIZE on the planted "
                                     "homophilic arena -> harness cannot detect a real code-family advantage / "
                                     "arena not structured")

    st_verdict, st_msg, st_gates = aggregate_and_verdict_families([res])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(ref_oracle_recovers and ref_oracle_fires),
         "control_name": "RANDOM_BIPOLAR_ORACLE_FOLDIN", "headline_name": "ref_oracle_beats_random_heldout_mrr",
         "extra": "planted arena: the reference family's ORACLE (held-out edges folded into W) recovers held-out "
                  "tails via their fixed codes and clears RANDOM by the ceiling-aware ratio+abs fire gate -> the "
                  "arena is answerable by the native store"},
        {"kind": "metric_moves", "metric_name": "heldout_mrr",
         "values": [rand_m, M(RANDOM_BIPOLAR, MEMORIZE), M(RANDOM_BIPOLAR, NATIVE), ref_oracle],
         "extra": "MRR RANDOM=%.3f MEMORIZE=%.3f NATIVE=%.3f ORACLE=%.3f" %
                  (rand_m, M(RANDOM_BIPOLAR, MEMORIZE), M(RANDOM_BIPOLAR, NATIVE), ref_oracle)},
        {"kind": "negative_control_margin",
         "control_scores": [rand_m, M(CONTENT_TRIGRAM, SCRAMBLE), M(CONTENT_TRIGRAM, IDSHUF)],
         "headline_threshold": M(CONTENT_TRIGRAM, NATIVE), "higher_is_pass": True,
         "margin": SELFTEST_CONTENT_SCRAMBLE_MARGIN, "n_repeats_min": 3,
         "control_name": "RANDOM_SCRAMBLE_IDSHUF_below_content_native_mrr",
         "extra": "RANDOM + relation-scrambled + identity-shuffled content compose must sit below NATIVE_CONTENT by "
                  "the MRR margin -> relation operators AND entity-identity binding carry the signal"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "ref_oracle_fires", "scramble_controlled", "idshuf_controlled",
                                    "broken_test_guard", "enough_heldout", "ratio_to_reference_band_gate"],
         "exercised_gates": ["arms_differ", "ref_oracle_fires", "scramble_controlled", "idshuf_controlled",
                             "broken_test_guard", "enough_heldout", "ratio_to_reference_band_gate"],
         "extra": "aggregate_and_verdict_families verdict=%s at self-test scale" % st_verdict},
    ], run_mode="self_test")

    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    out.update(
        random_mrr=round(rand_m, 5), pop_mrr=round(pop_m, 5),
        family_mrr={f: {arm: round(M(f, arm), 5) for arm in FAM_ARMS} for f in FAMILIES},
        family_spectrum={f: {arm: {mk: round(fam[f]["arm_hits"][arm].get(mk, float("nan")), 5)
                                   for mk in metric_keys} for arm in FAM_ARMS} for f in FAMILIES},
        ref_oracle_mrr=round(ref_oracle, 5), oracle_ratio=(round(oracle_ratio, 2)
                       if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        struct_margin=round(struct_margin, 5), content_scramble_margin=round(content_scr_margin, 5),
        content_idshuf_margin=round(content_ids_margin, 5), n_distinct_sigs=n_sigs,
        ref_oracle_recovers=ref_oracle_recovers, ref_oracle_fires=ref_oracle_fires,
        structured_beats_random=structured_beats_random, content_scramble_fails=content_scramble_fails,
        content_idshuf_fails=content_idshuf_fails, pop_at_floor=pop_at_floor, arms_differ=arms_differ,
        selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest"],
    )
    ok = bool(ref_oracle_recovers and ref_oracle_fires and structured_beats_random and content_scramble_fails
              and content_idshuf_fails and pop_at_floor and arms_differ and vp_ok)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def core_main(run_mode, device):
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

    _log("device=cpu run_mode=%s seeds=%s n_dim=%s families=%s" % (run_mode, seeds, cfg["n_dim"], FAMILIES))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s struct_margin=%s content_scr=%s content_ids=%s ref_oracle_fires=%s vp_ok=%s "
         "sigs=%s" % (st_ok, st_res.get("struct_margin"), st_res.get("content_scramble_margin"),
                      st_res.get("content_idshuf_margin"), st_res.get("ref_oracle_fires"),
                      st_res.get("validity_preflight_ok"), st_res.get("n_distinct_sigs")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (ref ORACLE did not fire, or the structured CONTENT code did not "
                        "beat RANDOM_BIPOLAR on the planted homophilic arena, or content scramble/identity-shuffle "
                        "did not fail, or POP not at floor, or arms not distinct, or validity-preflight failed): %s"
                        % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS NATIVE_CODE_FAMILY_SWEEP: reference ORACLE fires, the structured content code "
                        "beats random-bipolar on MEMORIZE on the planted homophilic arena, content relation-scramble "
                        "AND identity-shuffle fail, POP at floor, >=10 distinct arm sigs, 4 validity-preflight checks",
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
            _log("cskg seed=%d core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["core_avgdeg"],
                    prov["n_rel_tokens"], len(pool)))
            res = run_seed(pool, cfg, seed, "CSKG_CORE_HELDOUT_ENTITY")
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out-entity query edges too few (%d < %d)" %
                                   (res.get("n_query_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            if len(res["families"]) != len(FAMILIES):
                raise RuntimeError("family cardinality breach seed=%d got %d families" % (seed, len(res["families"])))
            if res.get("n_distinct_sigs", 0) < 10:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs"
                                   % (seed, res.get("n_distinct_sigs", 0)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            _log("seed=%d done nq=%d n_sup=%d (%.1fs)" % (seed, res["n_query_scored"], res["n_support"],
                                                          time.time() - ts))
            _hb("cskg", si)
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

    verdict, verdict_msg, gates = aggregate_and_verdict_families(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device="cpu", n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def _resolve_device(arg_device):
    return torch.device("cpu")


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
    device = _resolve_device(args.device)
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
