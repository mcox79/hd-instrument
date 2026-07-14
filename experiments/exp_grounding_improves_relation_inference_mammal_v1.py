"""GROUNDING-IMPROVES-REASONING: does fusing MEASURED attributes improve HELD-OUT RELATION inference?

WHY THIS CELL EXISTS -- the deep-prize test the two prior grounding cells did NOT run.
  Prior cells (exp_grounding_periodic_xchannel_fpe_v1, exp_grounding_mammal_allometry_xchannel_fpe_v1)
  measured ATTRIBUTE RECOVERY: "does the measured channel B predict a held-out numeric ATTRIBUTE?"
  That is near-tautological (B predicting B) and came back GROUNDING_REDUNDANT where the relation
  graph already predicts the attribute. It CANNOT answer the question that matters for grounding:
  does fusing measured attributes into the substrate improve the REASONING task -- inference of
  HELD-OUT RELATIONS (link prediction)? That is the KBLRN / LiteralE result (fuse numeric literals
  into KG embeddings -> link prediction IMPROVES, documented with a with/without ablation)
  CITED@notes B-field drill (KBLRN Garcia-Duran & Niepert 2018 arXiv:1709.04676; LiteralE Kristiadi
  et al. 2019 arXiv:1802.00934). This cell runs THAT test on our substrate.

PRIMARY METRIC = HELD-OUT RELATION inference (filtered MRR + hits@{1,3,10} rank-vs-all, KGE standard,
  degree-unbiased -- NO sampled-negative pool). NOT attribute recovery.
ABLATION (the whole point): the SAME held-out-relation queries scored with vs without grounding.
  RELATIONAL_ONLY : held-out entity code = anchor-compose bundle of its support-edge estimates (pure
                    relational; the memorize/inductive baseline).
  GROUNDED_FUSED  : held-out entity code = RELATIONAL bundle FUSED with a grounded estimate = a ridge
                    map (fit on SEEN entities only) from the entity's FPE-encoded measured attributes
                    into the learned relational geometry (LiteralE: literals inform the embedding).
  Does GROUNDED_FUSED beat RELATIONAL_ONLY on held-out-relation MRR? (and beat a SCRAMBLE must-fail).

DOMAIN + why attributes are RELATION-RELEVANT (the fairness crux). Entities = 65 mammal species; the
  KG relations = phylogenetic taxonomy edges (species -HAS_ORDER-> order, -HAS_FAMILY-> family,
  -HAS_CLADE-> clade). Task = predict a held-out species' ORDER/FAMILY/CLADE tail. The measured
  attributes (adult body mass, head-body length, max longevity, gestation, litter size) are RELEVANT
  to these relations via PHYLOGENETIC SIGNAL in life-history: closely related taxa share
  life-history SCALING (long gestation+longevity+singleton litters mark primates regardless of the
  mass range; short gestation+large litters mark rodents) -- Blomberg's K / Pagel's lambda,
  CITED@comparative life-history theory. Crucially this is NOT tautological: a SINGLE attribute
  (mass) varies 10^6 WITHIN one order (mouse vs capybara both Rodentia), so no single attribute
  recovers the relation -- only the JOINT trait vector carries phylogenetic signal the pure ID-based
  relational code cannot supply for an unseen entity. Grounding can genuinely HELP the reasoning,
  and MUST clear a SCRAMBLE control to prove it is the RIGHT attributes, not just added dimensions.
  (Contrast periodic: group IS valence == the property structure, so B secretly contains the graph;
  contrast the prior mammal cell: taxonomy is A-INDEPENDENT of mass so B could not ADD to attribute
  recovery. HERE the target is the RELATION, and grounding's marginal value is the phylogenetic
  signal a sparse-support held-out entity's relational code lacks -- especially at LOW support.)

PRE-REGISTERED BANDS (BOTH sides picked BEFORE the run; primary metric filtered MRR; ABSOLUTE,
  LITERATURE-ANCHORED thresholds -- KBLRN/LiteralE numeric-literal fusion buys +0.01-0.04 MRR on
  standard KG link prediction, CITED@notes B-field drill, so a ceiling-relative bar tied to the
  saturating transductive ORACLE would be meaningless here; regime-mismatch discipline. ORACLE is
  used ONLY as the arena-answerable gate. degree/support-stratified):
  GROUNDING_IMPROVES_REASONING (HARD_PASS): mean (GROUNDED_FUSED - RELATIONAL_ONLY)_mrr >= 0.03
      (LiteralE-scale, strict end) AND per-seed gain > 0 in >= 60% of seeds (multi-seed consistency)
      AND (GROUNDED_FUSED - SCRAMBLE_FUSED)_mrr >= 0.02 (the RIGHT attributes, not added dimensions)
      AND ORACLE fires AND RELATIONAL_ONLY is itself above RANDOM (a real reasoning baseline) AND not
      broken.
  NO_IMPROVEMENT (MIDDLE_BAND = GROUNDING_REDUNDANT_FOR_REASONING): the ablation delta is within
      (-0.03, 0.03) or fails consistency / scramble-margin -- grounding neither meaningfully helps nor
      hurts held-out-relation inference on this domain.
  GROUNDING_HURTS_REASONING (HARD_FAIL): mean (GROUNDED_FUSED - RELATIONAL_ONLY)_mrr <= -0.03 with the
      ORACLE firing (fusing attributes damages inference; localize).
  Gated INCONCLUSIVE if ORACLE does not fire (arena not answerable), too few held-out queries, the
  relational baseline is at the RANDOM floor, or the RANDOM null beats the relational baseline (broken).

FAILURE-MODE classification (do NOT conflate):
  ARENA_NOT_ANSWERABLE : ORACLE (learned held-out codes) does not clear RANDOM -> INCONCLUSIVE.
  RELATIONAL_BASELINE_AT_FLOOR : pure-relational inference == random -> no reasoning to improve.
  GROUNDING_SCRAMBLE_ARTIFACT : GROUNDED_FUSED gain matched by SCRAMBLE_FUSED -> added-channel
                    dimensionality, not the attributes -> broken.
  GROUNDING_IMPROVES_REASONING / NO_IMPROVEMENT / GROUNDING_HURTS_REASONING as above.

## Compute architecture
class (b) sequential-CPU: a 65-entity taxonomy KG (N ~ 125 incl symbols; nq ~ 30 held-out edges);
  three tiny additive KGE fits (ADDITIVE scaffold, ORACLE, per seed) via minibatch SGD reused from
  _kge_anchor1_fit + a closed-form ridge grounding map + (nq,N) cdist score matrices. Whole cell is
  seconds/seed on CPU (N,nq tiny); GPU buys nothing. Storage SHARDED (each entity its own code;
  relations = per-TYPE additive displacements; the only bundle is the per-ENTITY anchor mean).
  device forced cpu on remote_cpu_queue.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 7 arms produce >=5 distinct score signatures.
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json.tmp).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: held-out MRR has a CEILING (the ORACLE headroom H); bands are FRACTIONS of the
#   MEASURED H (computed in-run), so discriminator_reachability is OK by construction.
# - baseline_in_band: ORACLE must fire (>=3x RANDOM_mrr AND headroom>=ABS); RANDOM/POP near 1/N floor.
# - discriminator survives scale: the ablation is a PAIRED delta on the SAME queries; the planted
#   self-test fires GROUNDED_FUSED-beats-RELATIONAL + scramble-fails deterministically; the real-data
#   delta is the FULL science question (not a ship gate).
# - HARD_PASS strictly above floor: 0.15*H gain + a MIN_SIG_GAIN abs floor + scramble margin.
# - HP_SCOPE: the grounding-improves gates apply to GROUNDED_FUSED vs RELATIONAL_ONLY only. ORACLE =
#   positive control (must fire); RANDOM/SCRAMBLE_FUSED = must-not-explain controls; GROUNDED_ONLY =
#   does-grounding-carry-info diagnostic; POP = fit-independence sanity.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 7 arms + >=5 sigs.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- HELDOUT/SUPPORT frac + ORACLE-fire + band
#   FRACTIONS pre-registered, NOT tuned on real data; ANCHOR/gain bands are fractions of MEASURED H.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the prereg.
# - F.1 real_code_path: self-test CALLS the REAL fit_kge_anchor1 + filtered_hits_from_scores at N~232.
# - F.2/F.3 substrate_signature: fit_kge_anchor1 bound with BASE/portable kwargs only.
# - F.4 guard_baseline_valid: RELATIONAL_ONLY (the ablation baseline) validated above RANDOM floor.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints).

ASCII-only. No em-dashes in output. No bare except; except SystemExit before except Exception.
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
from collections import Counter
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# Reused proven leaf primitives (attribute wiring + additive fit + ceiling-aware eval).
from experiments.exp_grounding_mammal_allometry_xchannel_fpe_v1 import (  # noqa: E402
    load_mammals, _norm_prop, fpe_encode, _PROP_LOG, _PROP_NAMES,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    filtered_hits_from_scores, build_true_by_hr_int, pop_hits,
)
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR, A1_GAMMA  # noqa: E402
from experiments._validity_preflight import run_validity_preflight  # noqa: E402

ANCHOR_NAME = "grounding_improves_relation_inference_mammal_v1"

# ---- Arm names ----
RELATIONAL = "RELATIONAL_ONLY"      # ablation baseline: anchor-compose bundle only (no grounding)
FUSED = "GROUNDED_FUSED"            # mechanism: relational bundle FUSED with grounded attribute estimate
GROUND_ONLY = "GROUNDED_ONLY"      # diagnostic: grounded estimate only (does grounding carry info at all)
SCRAMBLE = "SCRAMBLE_FUSED"        # must-fail: fused with attributes SHUFFLED across entities
RANDOM = "RANDOM_CODES"            # null
ORACLE = "ORACLE_ADDITIVE"         # positive control: held-out folded into the fit (codes learned) = ceiling
POP = "BASELINE_POP"               # frequency incumbent (fit-independence sanity)
GEOM_ARMS = [RELATIONAL, FUSED, GROUND_ONLY, SCRAMBLE, RANDOM, ORACLE]
ALL_ARMS = GEOM_ARMS + [POP]

# ---- Relation ids ----
REL_NAMES = ["HAS_ORDER", "HAS_FAMILY", "HAS_CLADE"]
N_REL = 3

GAMMA = A1_GAMMA                    # score = gamma - ||X_h + D_r - X_t|| (monotone; ranking-invariant)
EVAL_KS = (1, 3, 10)
CEIL_METRIC = "mrr"

# ---- arena-answerable gate (ORACLE = held-out folded in; near-saturates here BY CONSTRUCTION since it
#      trains on the query edge, so its HEADROOM is NOT a usable ceiling for the marginal ablation delta --
#      the ceiling-relative framing from the CSKG anchor arena does NOT transfer here; regime-mismatch
#      discipline). ORACLE is used ONLY to confirm the readout can rank a valid code (arena answerable). ----
ORACLE_FIRE_RATIO = 3.0            # ORACLE_mrr >= 3x RANDOM_mrr (scale-free clear separation)
ORACLE_FIRE_ABS = 0.05            # AND ORACLE_mrr - RANDOM_mrr >= this (non-noise absolute floor)
REL_ABOVE_RANDOM_MIN = 0.02      # RELATIONAL_ONLY must beat RANDOM by this (a real reasoning baseline exists)
# ---- ABSOLUTE, LITERATURE-ANCHORED ablation bands (KBLRN/LiteralE numeric-literal fusion buys +0.01-0.04
#      MRR on standard KG link prediction; CITED@notes B-field drill LiteralE arXiv:1802.00934 / KBLRN
#      arXiv:1709.04676). Pre-registered from the LITERATURE, NOT tuned on this arena's smoke. HARD_PASS is
#      set at the STRICT end (0.03) of that meaningful-gain range + REQUIRES multi-seed consistency + a
#      RIGHT-attributes margin over the SCRAMBLE control. ----
HP_ABS_GAIN = 0.03               # HARD_PASS: mean (FUSED - RELATIONAL)_mrr >= this (LiteralE-scale, strict end)
SCR_ABS_MARGIN = 0.02           # HARD_PASS: (FUSED - SCRAMBLE)_mrr >= this (the RIGHT attributes, not added dims)
SEED_CONSISTENCY_FRAC = 0.60    # HARD_PASS: fraction of seeds with per-seed gain > 0 (not a single-seed fluke)
HF_HURT_ABS = 0.03             # HARD_FAIL: mean (FUSED - RELATIONAL)_mrr <= -this (grounding damages inference)
BROKEN_EPS = 0.01             # broken: a null (RANDOM) beats the RELATIONAL baseline by more than this mrr
MIN_HELDOUT = 15             # min held-out QUERY edges per seed for a valid discriminator

# ---- split / grounding knobs (pre-registered; NOT tuned on real data) ----
HELDOUT_ENTITY_FRAC = 0.30   # fraction of SPECIES withheld from every train edge
SUPPORT_FRAC = 0.34          # fraction of a held-out species' edges reserved as SUPPORT (build the bundle)
N_FPE_FREQ = 4               # FPE random-Fourier frequencies per attribute (reuses fpe_encode)
FPE_FREQ_STD = 2.15          # matches the proven mammal-allometry FPE bandwidth
RIDGE_LAM = 1.0              # grounding ridge regularization (generalization-validated on planted self-test)
FUSE_ALPHA = 1.0             # relational weight in the fusion
FUSE_BETA = 1.0              # grounded weight in the fusion

# ---- self-test planted thresholds (calibrated on the synthetic latent-consistent arena, NOT real data) ----
SELFTEST_ORACLE_MRR_MIN = 0.20      # planted: ORACLE (learned held-out codes) mrr at least this
SELFTEST_FUSED_BEATS_REL = 0.015    # planted: (FUSED - RELATIONAL)_mrr >= this (grounding ADDS to reasoning)
SELFTEST_FUSED_BEATS_SCR = 0.015    # planted: (FUSED - SCRAMBLE)_mrr >= this (RIGHT attributes, not added dims)
SELFTEST_GROUND_BEATS_RAND = 0.02   # planted: (GROUNDED_ONLY - RANDOM)_mrr >= this (grounding carries info)
SELFTEST_MIN_HO = 20                # planted: minimum held-out QUERY edges

# ---- configs (SELFTEST planted; SMOKE + FULL on the mammal KG) ----
SELFTEST_CFG = dict(k=12, epochs=200, n_neg=32, batch=2048,
                    heldout_entity_frac=0.30, support_frac=0.34)
SMOKE_CFG = dict(k=16, epochs=120, n_neg=32, batch=1024,
                 heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                 seeds=[7, 13, 17])
FULL_CFG = dict(k=16, epochs=300, n_neg=48, batch=1024,
                heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                seeds=[7, 13, 17, 23, 29, 31, 37, 41])

SUPPORT_BINS = [(0, 0, "cold"), (1, 1, "d1"), (2, 3, "d2_3")]


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


# --------------------------------------------------------------------------- #
# KG construction: species -HAS_ORDER/FAMILY/CLADE-> taxonomy symbols.         #
# Entities = [species | order-symbols | family-symbols | clade-symbols].       #
# attr [N,5] = normalized measured traits (species rows); symbol rows = 0.     #
# eligible [N] bool = species (the grounded-eligible / held-out-able entities). #
# --------------------------------------------------------------------------- #
def build_mammal_kg():
    mm = load_mammals()
    n_sp = mm["n"]
    orders = sorted(set(mm["order"]))
    families = sorted(set(mm["family"]))
    clades = sorted(set(mm["clade"]))
    o_off = n_sp
    f_off = o_off + len(orders)
    c_off = f_off + len(families)
    N = c_off + len(clades)
    o_idx = {o: o_off + i for i, o in enumerate(orders)}
    f_idx = {f: f_off + i for i, f in enumerate(families)}
    c_idx = {c: c_off + i for i, c in enumerate(clades)}
    edges = []  # (species_i, rel_id, symbol_j) int
    for e in range(n_sp):
        edges.append((e, 0, o_idx[mm["order"][e]]))
        edges.append((e, 1, f_idx[mm["family"][e]]))
        edges.append((e, 2, c_idx[mm["clade"][e]]))
    edges = np.array(edges, dtype=np.int64)
    # normalized attribute matrix (global min-max per proven allometry wiring; log10 for size/time vars).
    norm_cols = [_norm_prop(mm["props"][:, k], _PROP_LOG[k]) for k in range(len(_PROP_NAMES))]
    attr = torch.zeros(N, len(_PROP_NAMES), dtype=torch.float64)
    for k in range(len(_PROP_NAMES)):
        attr[:n_sp, k] = torch.nan_to_num(norm_cols[k], nan=0.0).to(torch.float64)
    eligible = torch.zeros(N, dtype=torch.bool)
    eligible[:n_sp] = True
    return dict(N=N, n_rel=N_REL, edges=edges, attr=attr, eligible=eligible, n_species=n_sp,
                names=mm["name"])


def build_planted_kg(seed, n_ent=200, n_rel=N_REL, n_sym_per_rel=10, k_lat=6, attr_noise=0.35, deg=3):
    """Planted latent-consistent taxonomy arena where the measured attributes CARRY the latent that
    drives the relations, so grounding CAN improve held-out relation inference and the ablation must
    detect it. Entities get latent z ~ N(0,I) in k_lat dims; each relation r partitions space into
    n_sym_per_rel symbol-clusters (random centers); an edge (e, r, s) connects e to the symbol whose
    center is nearest z[e]. Attributes a[e] = z[e] @ M + noise (5 dims) -> a ridge map a->code recovers
    the z-geometry -> grounding places a held-out entity even with sparse support. Scrambling attributes
    destroys the a->z link. Deterministic (default_rng(seed) + order-preserving dedup)."""
    rng = np.random.default_rng(seed * 100019 + 3)
    z = rng.standard_normal((n_ent, k_lat))
    centers = [rng.standard_normal((n_sym_per_rel, k_lat)) for _ in range(n_rel)]
    M = rng.standard_normal((k_lat, len(_PROP_NAMES)))
    A = z @ M + attr_noise * rng.standard_normal((n_ent, len(_PROP_NAMES)))
    # min-max normalize attributes to [0,1] per column (matches the real wiring's normalized inputs).
    A = (A - A.min(axis=0, keepdims=True)) / (A.max(axis=0, keepdims=True) - A.min(axis=0, keepdims=True) + 1e-9)
    sym_off = n_ent
    per_rel_off = [sym_off + r * n_sym_per_rel for r in range(n_rel)]
    N = sym_off + n_rel * n_sym_per_rel
    edges = []
    for e in range(n_ent):
        rels = rng.choice(n_rel, size=deg, replace=False)
        for r in rels:
            d = np.linalg.norm(centers[r] - z[e], axis=1)
            s = int(np.argmin(d))
            edges.append((e, int(r), per_rel_off[r] + s))
    edges = np.array(list(dict.fromkeys(map(tuple, edges))), dtype=np.int64)  # order-preserving dedup
    attr = torch.zeros(N, len(_PROP_NAMES), dtype=torch.float64)
    attr[:n_ent] = torch.from_numpy(A).to(torch.float64)
    eligible = torch.zeros(N, dtype=torch.bool)
    eligible[:n_ent] = True
    return dict(N=N, n_rel=n_rel, edges=edges, attr=attr, eligible=eligible, n_species=n_ent, names=None)


# --------------------------------------------------------------------------- #
# Held-out-HEAD (species) split with per-entity SUPPORT / QUERY partition.     #
#   withhold ~frac of species from every train edge; train = heads-not-held.   #
#   a held-out species appears only as a HEAD in (species, r, symbol) edges.   #
#   partition its held edges: SUPPORT (build the bundle) + QUERY (scored).     #
#   DROP query edges whose tail symbol is absent from train (unanswerable).    #
# --------------------------------------------------------------------------- #
def build_heldout_head_split(kg, frac, support_frac, seed):
    edges = kg["edges"]
    elig = np.nonzero(kg["eligible"].numpy())[0]
    rng = np.random.default_rng(seed * 100003 + 7)
    n_hold = max(1, int(round(frac * elig.shape[0])))
    hold_ids = set(int(x) for x in rng.choice(elig, size=n_hold, replace=False))

    train, held_by_head = [], {}
    for i in range(edges.shape[0]):
        h, r, t = int(edges[i, 0]), int(edges[i, 1]), int(edges[i, 2])
        if h in hold_ids:
            held_by_head.setdefault(h, []).append((h, r, t))
        else:
            train.append((h, r, t))
    train = np.array(train, dtype=np.int64) if train else np.zeros((0, 3), dtype=np.int64)
    train_tail_symbols = set(int(t) for t in train[:, 2].tolist())

    rng2 = np.random.default_rng(seed * 991 + 5)
    support, query = [], []
    n_cold = n_dropped = 0
    for h in sorted(held_by_head.keys()):
        es = held_by_head[h]
        d = len(es)
        order = rng2.permutation(d)
        if d == 1:
            n_sup = 0
        else:
            n_sup = max(1, int(round(support_frac * d)))
            n_sup = min(n_sup, d - 1)   # always leave >=1 query edge
        sup_idx = set(int(x) for x in order[:n_sup].tolist())
        if n_sup == 0:
            n_cold += 1
        for j, e in enumerate(es):
            if j in sup_idx:
                support.append(e)
            else:
                # DROP query edges whose gold symbol never appears in train (arena cannot answer them).
                if e[2] in train_tail_symbols:
                    query.append(e)
                else:
                    n_dropped += 1
    support = np.array(support, dtype=np.int64) if support else np.zeros((0, 3), dtype=np.int64)
    query = np.array(query, dtype=np.int64) if query else np.zeros((0, 3), dtype=np.int64)
    hold_all = np.concatenate([support, query], axis=0) if query.shape[0] else support
    return dict(train=train, support=support, query=query, hold_ids=hold_ids, hold_all=hold_all,
                n_cold=n_cold, n_dropped=n_dropped)


# --------------------------------------------------------------------------- #
# Grounding: FPE random-Fourier features of the measured attributes + ridge    #
# map (fit on SEEN entities only) into the learned relational geometry.        #
# --------------------------------------------------------------------------- #
def fpe_ground_features(attr, n_freq, freq_std, seed):
    """Phi [N, 5*(1+2*n_freq)] real: per attribute, the raw normalized value + its FPE cos/sin RFF.

    Reuses fpe_encode (exp(i*freq*v)) whose real/imag parts are the cos/sin random Fourier features of
    the Gaussian kernel -- the SAME attribute wiring the proven allometry cell validated (decay 0.999).
    """
    g = torch.Generator(device="cpu").manual_seed(seed * 5701 + 3)
    cols = []
    for k in range(attr.shape[1]):
        v = attr[:, k].to(torch.float64)                       # [N] in [0,1]
        cols.append(v.view(-1, 1))
        freqs = (torch.randn(n_freq, generator=g, dtype=torch.float32) * freq_std)
        enc = fpe_encode(v, freqs)                             # [N, n_freq] complex
        cols.append(enc.real.to(torch.float64))
        cols.append(enc.imag.to(torch.float64))
    return torch.cat(cols, dim=1)                              # [N, F]


def fit_ridge(Phi_tr, X_tr, lam):
    """Closed-form ridge: W = (Phi^T Phi + lam I)^-1 Phi^T X. Phi_tr [n,F], X_tr [n,k] -> W [F,k]."""
    F = Phi_tr.shape[1]
    A = Phi_tr.t() @ Phi_tr + lam * torch.eye(F, dtype=torch.float64)
    B = Phi_tr.t() @ X_tr
    return torch.linalg.solve(A, B)


def grounded_codes(Phi, X, train_species, held_species, lam):
    """Ridge-map from attribute features to the learned latent; return grounded code [N,k] (float32)."""
    Phi64 = Phi.to(torch.float64)
    W = fit_ridge(Phi64[train_species], X[train_species].to(torch.float64), lam)
    return (Phi64 @ W).to(X.dtype)


def build_relational_bundle(X, D, support, N, device):
    """Held-out head code = mean over its support edges of (X[symbol] - D[r]) (invert TransE h=t-d).

    Returns (Xp with held-out-with-support rows patched to the bundle; cold rows keep the untrained X),
    plus support_deg [N] int (0 for cold)."""
    Xp = X.clone()
    support_deg = np.zeros(N, dtype=np.int64)
    if support.shape[0] == 0:
        return Xp, support_deg
    h = torch.from_numpy(support[:, 0]).long().to(device)
    r = torch.from_numpy(support[:, 1]).long().to(device)
    t = torch.from_numpy(support[:, 2]).long().to(device)
    est = X[t] - D[r]                                          # (S,k) per support edge
    acc = torch.zeros(N, X.shape[1], device=device, dtype=X.dtype)
    acc.index_add_(0, h, est)
    cnt = torch.zeros(N, device=device, dtype=X.dtype)
    cnt.index_add_(0, h, torch.ones(h.shape[0], device=device, dtype=X.dtype))
    mask = cnt > 0
    Xp[mask] = acc[mask] / cnt[mask].unsqueeze(1)
    support_deg = cnt.detach().to("cpu").numpy().astype(np.int64)
    return Xp, support_deg


def additive_scores(Xp, D, query, device, chunk=256):
    """(nq, N) score matrix = gamma - ||Xp[h] + D[r] - Xp[c]|| for all candidates c (higher=better)."""
    h = torch.from_numpy(query[:, 0]).long().to(device)
    r = torch.from_numpy(query[:, 1]).long().to(device)
    pred = Xp[h] + D[r]                                        # (nq,k)
    nq, N = pred.shape[0], Xp.shape[0]
    out = torch.empty(nq, N, dtype=Xp.dtype)
    for c0 in range(0, nq, chunk):
        c1 = min(c0 + chunk, nq)
        d = torch.cdist(pred[c0:c1], Xp)                      # (b,N)
        out[c0:c1] = (GAMMA - d).cpu()
    return out


# --------------------------------------------------------------------------- #
# One corpus run: fit -> construct arm codes -> score PAIRED on the SAME query. #
# --------------------------------------------------------------------------- #
def run_corpus(kg, cfg, device, seed):
    N, n_rel = kg["N"], kg["n_rel"]
    sp = build_heldout_head_split(kg, cfg["heldout_entity_frac"], cfg["support_frac"], seed)
    train, support, query, hold_all = sp["train"], sp["support"], sp["query"], sp["hold_all"]
    result = dict(seed=seed, N=int(N), n_rel=int(n_rel), n_train=int(train.shape[0]),
                  n_heldout=len(sp["hold_ids"]), n_support=int(support.shape[0]),
                  n_query_scored=int(query.shape[0]), n_cold=int(sp["n_cold"]), n_dropped=int(sp["n_dropped"]),
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query.shape[0] < 1 or train.shape[0] < 1:
        result["empty"] = True
        return result

    k = cfg["k"]
    # ADDITIVE scaffold (shared by RELATIONAL / FUSED / GROUNDED / SCRAMBLE) + ORACLE (held-out folded in).
    X, D = fit_kge_anchor1(train, N, n_rel, k, device, seed, cfg["epochs"], reciprocal=True, lr=A1_LR,
                           n_neg=cfg["n_neg"], batch_size=cfg["batch"])
    Xo, Do = fit_kge_anchor1(train, N, n_rel, k, device, seed, cfg["epochs"], transductive_extra=hold_all,
                             reciprocal=True, lr=A1_LR, n_neg=cfg["n_neg"], batch_size=cfg["batch"])
    # RANDOM null codes + readout.
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, k, generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, k, generator=gR) * 0.1).to(device)

    elig = kg["eligible"].numpy()
    held_ids = np.array(sorted(sp["hold_ids"]), dtype=np.int64)
    train_species = np.array([i for i in np.nonzero(elig)[0] if i not in sp["hold_ids"]], dtype=np.int64)

    # relational bundle (held-out-with-support rows patched; cold rows = untrained X).
    Xp_rel, support_deg = build_relational_bundle(X, D, support, N, device)

    # grounded codes (real attributes) + scrambled attributes (shuffle eligible rows).
    Phi = fpe_ground_features(kg["attr"], N_FPE_FREQ, FPE_FREQ_STD, seed)
    g_real = grounded_codes(Phi, X, train_species, held_ids, RIDGE_LAM)
    gS = np.random.default_rng(seed * 4441 + 17)
    elig_ids = np.nonzero(elig)[0]
    perm = elig_ids.copy()
    gS.shuffle(perm)
    attr_scr = kg["attr"].clone()
    attr_scr[elig_ids] = kg["attr"][perm]                     # each eligible entity gets ANOTHER's attributes
    Phi_scr = fpe_ground_features(attr_scr, N_FPE_FREQ, FPE_FREQ_STD, seed)
    g_scr = grounded_codes(Phi_scr, X, train_species, held_ids, RIDGE_LAM)

    # arm code tables: patch ONLY held-out rows (train species + symbols keep trained X).
    def _fuse(g_codes):
        Xp = X.clone()
        for s in held_ids.tolist():
            if support_deg[s] > 0:
                Xp[s] = FUSE_ALPHA * Xp_rel[s] + FUSE_BETA * g_codes[s]
            else:
                Xp[s] = g_codes[s]
        return Xp

    Xp_fused = _fuse(g_real)
    Xp_scr = _fuse(g_scr)
    Xp_ground = X.clone()
    Xp_ground[held_ids] = g_real[held_ids]

    all_true = build_true_by_hr_int(train, support, query)
    rel_tail_freq = {}
    for i in range(train.shape[0]):
        rr = int(train[i, 1]); tt = int(train[i, 2])
        rel_tail_freq.setdefault(rr, Counter())[tt] += 1

    arm_scores = {
        RELATIONAL: additive_scores(Xp_rel, D, query, device),
        FUSED: additive_scores(Xp_fused, D, query, device),
        GROUND_ONLY: additive_scores(Xp_ground, D, query, device),
        SCRAMBLE: additive_scores(Xp_scr, D, query, device),
        RANDOM: additive_scores(Xr, Dr, query, device),
        ORACLE: additive_scores(Xo, Do, query, device),
    }
    arm_hits, arm_sig = {}, {}
    for a in GEOM_ARMS:
        arm_hits[a] = filtered_hits_from_scores(arm_scores[a], query, all_true, ks=EVAL_KS)
        arm_sig[a] = _sig(arm_scores[a].numpy()[:min(64, arm_scores[a].shape[0])].ravel())
    pop_m, pop_rank_vec = pop_hits(rel_tail_freq, query, all_true, N, ks=EVAL_KS)
    arm_hits[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    # support-degree stratified ablation delta (weak-point localization: expect gain at LOW support).
    gold = query[:, 2]
    q_sup = np.array([support_deg[int(query[i, 0])] for i in range(query.shape[0])], dtype=np.int64)
    by_support = {}
    for lo, hi, nm in SUPPORT_BINS:
        mask = (q_sup >= lo) & (q_sup <= hi)
        idx = np.nonzero(mask)[0]
        if idx.size < 3:
            by_support[nm] = dict(n=int(idx.size), fused=None, relational=None, gain=None)
            continue
        fh = filtered_hits_from_scores(arm_scores[FUSED][idx], query[idx], all_true, ks=(1,))
        rh = filtered_hits_from_scores(arm_scores[RELATIONAL][idx], query[idx], all_true, ks=(1,))
        by_support[nm] = dict(n=int(idx.size), fused=round(fh["mrr"], 5), relational=round(rh["mrr"], 5),
                              gain=round(fh["mrr"] - rh["mrr"], 5))

    result.update(arm_hits={a: {kk: round(vv, 6) for kk, vv in arm_hits[a].items() if kk != "n"}
                            for a in ALL_ARMS},
                  arm_n={a: arm_hits[a]["n"] for a in ALL_ARMS}, arm_sigs=arm_sig,
                  by_support_degree=by_support,
                  support_deg_hist={nm: int(((q_sup >= lo) & (q_sup <= hi)).sum())
                                    for lo, hi, nm in SUPPORT_BINS})
    return result


# --------------------------------------------------------------------------- #
# Aggregate + verdict (pre-registered BOTH bands).                            #
# --------------------------------------------------------------------------- #
def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _m(ps, arm):
    return ps["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def aggregate_and_verdict(per_seed):
    m = {a: _nm([_m(ps, a) for ps in per_seed]) for a in ALL_ARMS}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))
    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")

    H = _sub(m[ORACLE], m[RANDOM])                            # reported headroom (arena-answerable only; saturates)
    gain = _sub(m[FUSED], m[RELATIONAL])                      # the ablation delta (does grounding help)
    scr_margin = _sub(m[FUSED], m[SCRAMBLE])                  # RIGHT-attributes margin
    ground_info = _sub(m[GROUND_ONLY], m[RANDOM])            # does grounding carry info at all
    ground_vs_rel = _sub(m[GROUND_ONLY], m[RELATIONAL])     # corroboration: grounding alone vs pure-relational
    rel_above_random = _sub(m[RELATIONAL], m[RANDOM])
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    # per-seed gain (multi-seed consistency: not a single-seed fluke).
    per_seed_gain = [_sub(_m(ps, FUSED), _m(ps, RELATIONAL)) for ps in per_seed]
    valid_gains = [g for g in per_seed_gain if g == g]
    frac_pos = (float(np.mean([1.0 if g > 0 else 0.0 for g in valid_gains])) if valid_gains else float("nan"))

    enough = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(H == H and H >= ORACLE_FIRE_ABS and oracle_ratio == oracle_ratio
                        and oracle_ratio >= ORACLE_FIRE_RATIO)
    rel_valid = bool(rel_above_random == rel_above_random and rel_above_random >= REL_ABOVE_RANDOM_MIN)

    # broken: the RANDOM null beating the RELATIONAL baseline (degenerate readout).
    broken = bool(m[RANDOM] == m[RANDOM] and m[RELATIONAL] == m[RELATIONAL]
                  and (m[RANDOM] - m[RELATIONAL]) > BROKEN_EPS)

    consistent = bool(frac_pos == frac_pos and frac_pos >= SEED_CONSISTENCY_FRAC)
    grounding_improves = bool(gain == gain and gain >= HP_ABS_GAIN
                              and scr_margin == scr_margin and scr_margin >= SCR_ABS_MARGIN
                              and consistent and oracle_fires and rel_valid and not broken)
    grounding_hurts = bool(gain == gain and gain <= -HF_HURT_ABS and oracle_fires and rel_valid)

    if not enough:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
        failure_mode = "TOO_FEW_HELDOUT"
    elif broken:
        verdict = "BROKEN_TEST_NULL_BEATS_RELATIONAL"
        failure_mode = "NULL_BEATS_RELATIONAL"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
        failure_mode = "ARENA_NOT_ANSWERABLE"
    elif not rel_valid:
        verdict = "INCONCLUSIVE_RELATIONAL_BASELINE_AT_FLOOR"
        failure_mode = "RELATIONAL_BASELINE_AT_FLOOR"
    elif grounding_improves:
        verdict = "HARD_PASS_GROUNDING_IMPROVES_REASONING"
        failure_mode = "GROUNDING_IMPROVES_REASONING"
    elif grounding_hurts:
        verdict = "HARD_FAIL_GROUNDING_HURTS_REASONING"
        failure_mode = "GROUNDING_HURTS_REASONING"
    else:
        verdict = "MIDDLE_BAND_GROUNDING_REDUNDANT_FOR_REASONING"
        failure_mode = "NO_IMPROVEMENT"

    verdict_msg = (
        "%s || HELD-OUT-RELATION MRR [nq=%d]: RELATIONAL=%s FUSED=%s (gain=%s>=%.3f? %s; seeds_pos=%s>=%.2f? %s) "
        "| GROUNDED_ONLY=%s (vs_rel=%s) SCRAMBLE=%s (fused_margin=%s>=%.3f) | RANDOM=%s ORACLE=%s POP=%s "
        "|| arena: oracle_hd=%s ratio=%sx fires=%s | rel_above_random=%s (>=%.2f)? %s | hurt(<=-%.3f)? %s "
        "| broken=%s | failure_mode=%s"
        % (verdict, n_query, _fmt(m[RELATIONAL]), _fmt(m[FUSED]), _fmt(gain), HP_ABS_GAIN, grounding_improves,
           _fmt(frac_pos), SEED_CONSISTENCY_FRAC, consistent, _fmt(m[GROUND_ONLY]), _fmt(ground_vs_rel),
           _fmt(m[SCRAMBLE]), _fmt(scr_margin), SCR_ABS_MARGIN, _fmt(m[RANDOM]), _fmt(m[ORACLE]), _fmt(m[POP]),
           _fmt(H), (_fmt(oracle_ratio) if oracle_ratio != float("inf") else "inf"), oracle_fires,
           _fmt(rel_above_random), REL_ABOVE_RANDOM_MIN, rel_valid, HF_HURT_ABS, grounding_hurts,
           broken, failure_mode))

    def _rnd(x, nd=6):
        return round(x, nd) if x == x else None

    gates = dict(
        verdict=verdict, failure_mode=failure_mode, ceil_metric=CEIL_METRIC,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        heldout_mrr={a: _rnd(m[a]) for a in ALL_ARMS},
        oracle_headroom=_rnd(H), oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio
                                               and oracle_ratio != float("inf")) else None),
        ablation_gain_fused_minus_relational=_rnd(gain),
        per_seed_gain=[_rnd(g) for g in per_seed_gain], frac_seeds_gain_positive=_rnd(frac_pos, 3),
        scramble_margin_fused_minus_scramble=_rnd(scr_margin),
        grounded_only_minus_random=_rnd(ground_info),
        grounded_only_minus_relational=_rnd(ground_vs_rel),
        relational_minus_random=_rnd(rel_above_random),
        bands=dict(ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS,
                   HP_ABS_GAIN=HP_ABS_GAIN, SCR_ABS_MARGIN=SCR_ABS_MARGIN,
                   SEED_CONSISTENCY_FRAC=SEED_CONSISTENCY_FRAC, HF_HURT_ABS=HF_HURT_ABS,
                   REL_ABOVE_RANDOM_MIN=REL_ABOVE_RANDOM_MIN, MIN_HELDOUT=MIN_HELDOUT,
                   HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC, SUPPORT_FRAC=SUPPORT_FRAC),
        enough_heldout=enough, oracle_fires=oracle_fires, rel_valid=rel_valid, broken=broken,
        consistent=consistent, grounding_improves=grounding_improves, grounding_hurts=grounding_hurts,
        n_query_scored=n_query,
        by_support_degree={ps["seed"]: ps.get("by_support_degree") for ps in per_seed},
    )
    return verdict, verdict_msg, gates


# --------------------------------------------------------------------------- #
# Mechanism self-test: planted latent-consistent arena.                        #
# --------------------------------------------------------------------------- #
def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        return _mechanism_selftest_body(device)
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body(device):
    kg = build_planted_kg(7)
    cfg = dict(SELFTEST_CFG)
    res = run_corpus(kg, cfg, device, 7)
    out = dict(N=res.get("N"), n_heldout=res.get("n_heldout"), n_support=res.get("n_support"),
               n_query=res.get("n_query_scored"), n_cold=res.get("n_cold"), n_dropped=res.get("n_dropped"))
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted arena produced too few held-out queries (%s)" % res.get("n_query_scored")
        return False, out

    m = {a: res["arm_hits"][a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    gain = m[FUSED] - m[RELATIONAL]
    scr_margin = m[FUSED] - m[SCRAMBLE]
    ground_info = m[GROUND_ONLY] - m[RANDOM]
    oracle_margin = m[ORACLE] - m[RANDOM]
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])
    n_sigs = len(set(res["arm_sigs"].values()))

    oracle_recovers = bool(m[ORACLE] == m[ORACLE] and m[ORACLE] >= SELFTEST_ORACLE_MRR_MIN)
    oracle_fires = bool(oracle_margin == oracle_margin and oracle_margin >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    fused_beats_rel = bool(gain == gain and gain >= SELFTEST_FUSED_BEATS_REL)
    fused_beats_scr = bool(scr_margin == scr_margin and scr_margin >= SELFTEST_FUSED_BEATS_SCR)
    ground_carries = bool(ground_info == ground_info and ground_info >= SELFTEST_GROUND_BEATS_RAND)
    rel_above_random = bool((m[RELATIONAL] - m[RANDOM]) >= REL_ABOVE_RANDOM_MIN)
    arms_differ = bool(n_sigs >= 5)

    st_verdict, st_msg, st_gates = aggregate_and_verdict([res])

    vp_ok = run_validity_preflight([
        # F.1: the self-test CALLS the REAL substrate code path (additive fit + ceiling-aware eval).
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["fit_kge_anchor1", "filtered_hits_from_scores"],
         "exercised_entrypoints": ["fit_kge_anchor1", "filtered_hits_from_scores"]},
        # F.2/F.3: the fit call binds the LIVE signature with BASE/portable kwargs only.
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 1, "device": None, "seed": 0, "epochs": 1}},
        # F.4: the ablation baseline (RELATIONAL_ONLY) must be ABOVE the RANDOM floor (not structurally 0).
        {"kind": "guard_baseline_valid", "baseline_score": m[RELATIONAL], "floor_score": max(m[RANDOM], 0.0),
         "guard_name": "ablation_needs_nonfloor_relational", "baseline_name": RELATIONAL,
         "floor_name": RANDOM, "eps": 0.005},
        # POSITIVE control: on the planted arena where attributes carry the latent, FUSED MUST beat
        # RELATIONAL -> the ablation can DETECT grounding-improves-reasoning when it is real.
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(fused_beats_rel and fused_beats_scr and oracle_fires),
         "control_name": "PLANTED_grounding(FUSED beats RELATIONAL & SCRAMBLE)",
         "headline_name": "grounding_improves_heldout_relation_mrr"},
        {"kind": "metric_moves", "metric_name": "heldout_relation_mrr",
         "values": [m[RANDOM], m[RELATIONAL], m[FUSED], m[ORACLE]]},
        {"kind": "negative_control_margin", "control_scores": [m[RANDOM], m[SCRAMBLE]],
         "headline_threshold": m[FUSED], "higher_is_pass": True, "margin": SELFTEST_FUSED_BEATS_SCR,
         "n_repeats_min": 2, "control_name": "RANDOM_and_SCRAMBLE_below_fused_mrr"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires", "rel_valid", "broken_guard",
                                    "enough_heldout", "ceiling_relative_gain_gate"],
         "exercised_gates": ["arms_differ", "oracle_fires", "rel_valid", "broken_guard",
                             "enough_heldout", "ceiling_relative_gain_gate"]},
    ], run_mode="self_test")

    out.update(heldout_mrr={a: round(m[a], 5) for a in ALL_ARMS}, gain=round(gain, 5),
               scramble_margin=round(scr_margin, 5), grounded_info=round(ground_info, 5),
               oracle_margin=round(oracle_margin, 5),
               oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio
                            and oracle_ratio != float("inf")) else None),
               n_distinct_sigs=n_sigs, oracle_recovers=oracle_recovers, oracle_fires=oracle_fires,
               fused_beats_rel=fused_beats_rel, fused_beats_scr=fused_beats_scr, ground_carries=ground_carries,
               rel_above_random=rel_above_random, arms_differ=arms_differ, selftest_verdict=st_verdict,
               validity_preflight_ok=bool(vp_ok))
    ok = bool(oracle_recovers and oracle_fires and fused_beats_rel and fused_beats_scr and ground_carries
              and rel_above_random and arms_differ)
    return ok, out


# --------------------------------------------------------------------------- #
# I/O helpers (start-marker / atomic metrics / crash diagnostic).             #
# --------------------------------------------------------------------------- #
def _out_dir():
    name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    return os.path.join("data", "exp_" + name)


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _write_metrics(out_dir, metrics):
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _write_crash_metrics(out_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics(out_dir, diag)


def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    if (arg_device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue"):
        return torch.device("cpu")
    want = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want and torch.cuda.is_available()) else "cpu")


# --------------------------------------------------------------------------- #
# main                                                                         #
# --------------------------------------------------------------------------- #
def core_main(run_mode, device):
    out_dir = _out_dir()
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s gain=%s scramble_margin=%s oracle_fires=%s vp_ok=%s heldout_mrr=%s"
         % (st_ok, st_res.get("gain"), st_res.get("scramble_margin"), st_res.get("oracle_fires"),
            st_res.get("validity_preflight_ok"), st_res.get("heldout_mrr")))

    if run_mode == "self_test":
        _write_start_marker(out_dir, run_mode, 1)
        if not st_ok:
            _write_metrics(out_dir, dict(
                verdict="HARD_FAIL", run_mode="self_test",
                verdict_msg="MECHANISM_SELFTEST_FAILED: %s" % st_res.get("fail", st_res),
                summary="mechanism selftest failed", elapsed_s=0.0, mechanism_selftest=st_res))
            raise SystemExit(1)
        _write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS grounding-improves-relation-inference: planted FUSED beats RELATIONAL "
                        "and SCRAMBLE on held-out-relation MRR; ORACLE fires; grounding carries info; arms distinct",
            summary="SELFTEST_PASS", elapsed_s=0.0, mechanism_selftest=st_res))
        _log("SELFTEST_PASS")
        return
    if not st_ok:
        _write_start_marker(out_dir, run_mode, 1)
        _write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (do not trust the real-data ablation): %s" % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=0.0, mechanism_selftest=st_res))
        raise SystemExit(1)

    cfg = dict(SMOKE_CFG if run_mode == "smoke" else FULL_CFG)
    seeds = cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    _log("device=%s run_mode=%s seeds=%s k=%s epochs=%s" % (device, run_mode, seeds, cfg["k"], cfg["epochs"]))

    kg = build_mammal_kg()
    _log("mammal KG: N=%d (species=%d) rels=%d edges=%d" % (kg["N"], kg["n_species"], kg["n_rel"],
                                                            kg["edges"].shape[0]))
    t0 = time.perf_counter()
    per_seed, seed_failures = [], []
    for seed in seeds:
        try:
            res = run_corpus(kg, cfg, device, seed)
            if res.get("empty") or res["n_query_scored"] < MIN_HELDOUT:
                raise RuntimeError("held-out query edges too few (%d < %d)"
                                   % (res.get("n_query_scored", 0), MIN_HELDOUT))
            if len(set(res["arm_sigs"].values())) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d sigs"
                                   % (seed, len(set(res["arm_sigs"].values()))))
            per_seed.append(res)
            ah = res["arm_hits"]
            _log("seed=%d nq=%d n_sup=%d n_cold=%d n_drop=%d | MRR REL=%s FUSED=%s GND=%s SCR=%s RAND=%s ORA=%s POP=%s (%.1fs)"
                 % (seed, res["n_query_scored"], res["n_support"], res["n_cold"], res["n_dropped"],
                    _fmt(ah[RELATIONAL]["mrr"]), _fmt(ah[FUSED]["mrr"]), _fmt(ah[GROUND_ONLY]["mrr"]),
                    _fmt(ah[SCRAMBLE]["mrr"]), _fmt(ah[RANDOM]["mrr"]), _fmt(ah[ORACLE]["mrr"]),
                    _fmt(ah[POP]["mrr"]), time.perf_counter() - t0))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            seed_failures.append(dict(seed=seed, failure_class=type(e).__name__, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, type(e).__name__, str(e)[:200]))

    elapsed = time.perf_counter() - t0
    if len(per_seed) < expected_n_units:
        _write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=round(elapsed, 3), seed_failures=seed_failures,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=round(elapsed, 3), anchor_name=ANCHOR_NAME, n_seeds=len(per_seed), seeds=seeds,
                   config=cfg, gates=gates, mechanism_selftest=st_res, seed_failures=seed_failures,
                   per_seed=per_seed, ts_iso=datetime.now(timezone.utc).isoformat(), host=platform.node(),
                   device=str(device))
    _write_metrics(out_dir, metrics)
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % elapsed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    if not args.self_test and not args.smoke and args.run_mode == "full":
        env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if env_mode in ("self_test", "smoke", "full"):
            run_mode = env_mode
    device = _resolve_device(args.device)
    out_dir = _out_dir()
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
