"""GRAPH_SPECTRAL_ENTITY_CODES: structure never lives in the arbitrary entity LABEL (proven dead: residue/CRT closure,
Shannon+Kolmogorov). Track-A drill lever #2 asks -- does it live in the RELATION GRAPH? Build entity codes FROM the
co-occurrence graph's OWN spectral structure (normalized-Laplacian eigenvectors / PPMI-SVD (NetMF) / discounted
successor-representation) instead of random codes, and test whether that raises the recoverable-signal ORACLE CEILING
and the realized anchor-compose magnitude vs RANDOM codes on the SAME arbitrary-label held-out-entity arena
(CSKG core, k_core=12, N~25.7k, frac=0.15, support_frac=0.5, seeds 7/13/17) that MEASURED native 0.023 @ d1024,
additive-oracle 0.137, relief 0.781 @ d8192. Glass-box: closed-form eigendecomposition (randomized SVD), inspectable,
no learned aggregator. Degree-heterogeneity corrected (symmetric-normalized Laplacian D^-1/2 A D^-1/2).

MP / SPIKED-EIGENVALUE PRE-CHECK (MEASURED on this exact graph, logged again in-run gates.mp_precheck):
  Gini(degree)=0.5368 (>0.5), lambda_2=0.9499=5.76x null-bulk-radius rho=1/sqrt(dmean)=0.1648, 59/60 top eigenvalues
  exceed rho -> SPIKED/community structure PRESENT (graph is NOT a random graph). BUT top-20 energy frac=0.0133,
  top-50=0.0228 -> NOT low-rank (most spectral energy in the incompressible ~25.7k-dim bulk). So the graph HAS
  above-null structure but it is a TINY fraction of total energy: it is an OPEN empirical question whether feeding
  that structure into the associative store's CODES raises recoverable capacity, or whether correlation-hurts-capacity
  (reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08) dominates. Honest tension:
  grounding_learned_sr_heldout_reasoning_v1 (LEARNED SR, inductive held-out edges) already found no-better-than-random;
  this cell differs -- it measures the CLOSED-FORM spectral CODEBOOK's transductive ORACLE CEILING (does a
  graph-structured codebook beat a random codebook in pure associative capacity) AND a realized inductive compose
  (does deriving a held-out entity's code from its graph-neighbors' spectral coordinates beat random assignment).

TWO SETTINGS (all scored PAIRED on the SAME held-out QUERY edges; filtered MRR-vs-all-N; matched dim d=1024):
  ORACLE (transductive ceiling; held-out edges folded into W; codes computed on the FULL graph incl held-out edges):
    RAND_ORACLE  : random-bipolar codebook. POSITIVE CONTROL -> reproduce native ~0.023 @ d1024 AND the RANDOM-CODE
                   bar the spectral codebooks must beat.
    LAP_ORACLE   : symmetric-normalized-Laplacian spectral codebook (top-d singular vectors of S=D^-1/2 A D^-1/2). HEADLINE.
    PPMI_ORACLE  : PPMI-SVD / NetMF codebook (rank-d SVD of shifted-positive PMI of the 1-step random walk). HEADLINE.
    SR_ORACLE    : discounted successor-representation codebook (rank-d SVD of sum_k gamma^k (D^-1 A)^k). HEADLINE.
  COMPOSE (inductive realized; train-only W; held-out row = aggregate of the held-out entity's SUPPORT-neighbor codes):
    LAP_COMPOSE          : held-out code = row-normalized mean of its support-neighbors' TRAIN spectral codes. HEADLINE.
    RAND_COMPOSE         : SAME neighbor-mean aggregation over RANDOM train codes (apples-to-apples random bar).
    LAP_COMPOSE_SCRAMBLE : aggregate over RANDOM entities (not the true support-neighbors) -> MUST-FAIL (needs the
                           TRUE graph neighborhood, not just spectral-code volume).
  RAND_NULL : pure chance ranking (null floor). POP : freq baseline / fit-independence / BROKEN guard.

LOCALIZATION / VERDICT (pre-registered BELOW, picked BEFORE the run; bars are a MEASURED same-dim in-run RANDOM arm
plus CITED reference ceilings; strictly-above-floor per META_RULE_L):
  best_spec_oracle = max(LAP_ORACLE, PPMI_ORACLE, SR_ORACLE).
  GRAPH_STRUCTURE_LIFTS : pos-controls hold AND oracle fires AND EITHER
      (ORACLE lift)  best_spec_oracle - RAND_ORACLE >= LIFT_MARGIN(0.010), OR
      (COMPOSE lift) LAP_COMPOSE - RAND_COMPOSE >= LIFT_MARGIN(0.010) AND LAP_COMPOSE - LAP_COMPOSE_SCRAMBLE >= 0.005.
  NO_LIFT : pos-controls hold AND oracle fires AND best_spec_oracle - RAND_ORACLE < LIFT_MARGIN AND
      LAP_COMPOSE - RAND_COMPOSE < LIFT_MARGIN (graph structure not exploitable by this store despite MP spiked
      structure -> the wall is the STORE/READOUT (correlation-hurts-capacity), not the graph -> closes this lens).
  MIDDLE_BAND : exactly one of {oracle, compose} lifts, OR a lift margin in (0, threshold] (sweep rank/dim before claim).
  Gated INCONCLUSIVE if oracle does not fire, pos-controls fail, too few held-out queries, or POP beats RAND_NULL
  (BROKEN; guard validated vs the RAND_NULL/arm floor per Gate F.4).

## Compute architecture
class (b) sequential-CPU, justified. Codes = closed-form randomized-SVD (rank d=1024) of a ~25.7k-node/~474k-edge
SPARSE operator (a few sparse matvecs; seconds per family) -- NO SGD, NO epochs, NO learned aggregator. The native
store is ONE-SHOT Hebbian (KGStore.ingest_triples). Per seed: 3 spectral factorizations (LAP/PPMI/SR) on the oracle
graph + 1 on the train graph, ~7 native d=1024 Hebbian stores (cheaper than the residue-ceiling cell's d=2048x5 +
d=4579 mono that ran ~200s/seed) + chunked query recall/score. All CPU, device=cpu -> remote_cpu_queue. No GPU needed.
Storage: cell-local KGStore instances only; no mutation of any persisted store; codes held in-memory per seed.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 9 arms produce >=5 distinct score signatures per seed.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: bands are a MEASURED in-run same-dim RANDOM arm (spectral must beat a measured random codebook)
#   + CITED additive-oracle 0.137 / relief 0.781 -> discriminator_reachability OK by construction. The filtered-MRR
#   chance floor is ~1/N (2e-5); native 0.023 @ d1024 is ~600x chance so the arena is answerable (the 0.05<baseline
#   heuristic is calibrated for accuracy metrics, NOT filtered-MRR-over-25k -- see calibration_check).
# - baseline_in_band: RAND_ORACLE must reproduce native ~0.023 (>> RAND_NULL chance floor) = ORACLE-FIRES gate; the
#   discriminator (spectral - random) is FAR from saturation (relief ceiling 0.781) so it can fire in EITHER direction.
# - discriminator survives scale: FULL at the EXACT CSKG core / held-out regime that MEASURED 0.023->0.781 + 0.137; the
#   self-test fires LAP-recovers-planted + spectral-embedding-separates-blocks + compose-scramble-collapses on a planted SBM.
# - HARD bands strictly separated: LIFTS needs >= RAND + 0.010 (MIDDLE dead-band (0,0.010]).
# - HP_SCOPE: the LIFT gates apply to LAP/PPMI/SR_ORACLE + LAP_COMPOSE only. RAND_ORACLE = pos-control + random bar;
#   RAND_COMPOSE = compose random bar; LAP_COMPOSE_SCRAMBLE = must-fail; RAND_NULL = chance floor; POP = BROKEN guard.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms + >=5 sigs + finite W.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: default_ok_for_this_regime -- all dims/ranks/fracs/tols/gammas pre-registered, NOT tuned on real
#   data; the CSKG core + held-out split config is COPIED VERBATIM from the native + additive + residue-ceiling arenas.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the docstring/prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints + heartbeat; timeout>=1800).

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
import scipy.sparse as sp
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
from hdlab.kg_traversal import KGStore  # noqa: E402  (LIVE store; codes injected then one-shot Hebbian W)
import experiments.exp_native_bind_compose_inductive_entity_cskg_v1 as base  # noqa: E402

ANCHOR_NAME = "graph_spectral_entity_codes_cskg_v1"

# ---- Arm names ----
RAND_ORACLE = "RAND_ORACLE"            # random-bipolar codebook, fold-in: pos-control (~0.023) + random-code bar
LAP_ORACLE = "LAP_ORACLE"              # normalized-Laplacian spectral codebook, fold-in: HEADLINE
PPMI_ORACLE = "PPMI_ORACLE"            # PPMI-SVD / NetMF codebook, fold-in: HEADLINE
SR_ORACLE = "SR_ORACLE"                # successor-representation codebook, fold-in: HEADLINE
LAP_COMPOSE = "LAP_COMPOSE"            # inductive: held-out code = mean of support-neighbor spectral codes: HEADLINE
RAND_COMPOSE = "RAND_COMPOSE"          # same aggregation over random train codes (apples-to-apples random bar)
LAP_COMPOSE_SCRAMBLE = "LAP_COMPOSE_SCRAMBLE"  # aggregate over RANDOM entities: MUST-FAIL
RAND_NULL = "RAND_NULL"                # pure chance floor
POP = "BASELINE_POP"                   # freq baseline / BROKEN guard floor

ORACLE_ARMS = [RAND_ORACLE, LAP_ORACLE, PPMI_ORACLE, SR_ORACLE]
SPEC_ORACLE_ARMS = [LAP_ORACLE, PPMI_ORACLE, SR_ORACLE]
ALL_ARMS = [RAND_ORACLE, LAP_ORACLE, PPMI_ORACLE, SR_ORACLE,
            LAP_COMPOSE, RAND_COMPOSE, LAP_COMPOSE_SCRAMBLE, RAND_NULL, POP]

EVAL_KS = (1, 3, 10, 100)
CEIL_METRIC = "mrr"
SCORE_CHUNK = 512

# ---- CITED reference ceilings ----
CITED_NATIVE_1024 = 0.023083   # MEASURED@data/exp_kg_store_dim_scaling_ceiling_v1/metrics.json:gates.oracle_mrr_by_dim.1024
CITED_ADD_ORACLE = 0.137293    # MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_ADDITIVE
CITED_ADD_COMPOSE = 0.12821    # MEASURED@ same :ANCHOR_COMPOSE (additive realized)
CITED_RELIEF_8192 = 0.780600   # MEASURED@ exp_kg_store_dim_scaling_ceiling_v1 :8192
# MP pre-check (MEASURED@scratch mp_precheck on this exact graph; re-logged in-run)
MP_GINI = 0.5368
MP_LAMBDA2 = 0.9499
MP_RHO_NULL = 0.1648
MP_TOP20_ENERGY = 0.0133

# ---- Spectral construction params (pre-registered; NOT tuned on real data) ----
D_CODE = 1024                  # matched code dimension for ALL code arms (native 0.023 baseline lives here)
SVD_N_ITER = 3                 # randomized-SVD power iterations (range-finding dominates; 3 ample at rank 1024, well-
                               # separated leading spectrum lam2=0.95/lam3=0.83; keeps per-seed factorization cost bounded)
SVD_OVERSAMPLE = 24
SR_GAMMA = 0.5                 # successor-representation discount
SR_KSTEPS = 6                  # truncated Neumann series length (gamma^6=0.016 negligible)
PPMI_NEG = 1.0                 # NetMF negative-sampling shift b

# ---- Pre-registered bands ----
REPRODUCE_TOL = 0.010          # |RAND_ORACLE - 0.023| tolerance (one-shot Hebbian, low variance)
RAND_NULL_FLOOR = 0.004        # RAND_NULL must sit at/below this
ORACLE_FIRE_RATIO = 3.0        # RAND_ORACLE / RAND_NULL
ORACLE_FIRE_ABS = 0.003        # RAND_ORACLE - RAND_NULL
LIFT_MARGIN = 0.010            # spectral - random >= this -> a genuine lift (strictly above the random codebook)
COMPOSE_SCRAMBLE_MARGIN = 0.005  # LAP_COMPOSE - LAP_COMPOSE_SCRAMBLE >= this

# ---- Self-test planted thresholds (calibrated on synthetic SBM, NOT real data) ----
ST_LAP_ORACLE_MIN = 0.10       # planted SBM: LAP_ORACLE recovers planted held-out tails >= this
ST_ORACLE_BEATS_NULL = 0.05    # (LAP_ORACLE - RAND_NULL) margin
ST_BLOCK_PURITY_MIN = 0.45     # spectral embedding separates planted blocks (>= this; chance=1/n_blocks~0.167)
ST_COMPOSE_SCRAMBLE_MARGIN = 0.02  # (LAP_COMPOSE - LAP_COMPOSE_SCRAMBLE) margin on planted SBM

SELFTEST_CFG = dict(d_code=96, svd_n_iter=4, st_blocks=6, st_members=14, st_rels=4, st_edges_per_member=5,
                    heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0, min_heldout=8)
FULL_CFG = dict(d_code=D_CODE, svd_n_iter=SVD_N_ITER, heldout_entity_frac=0.15, support_frac=0.5,
                cskg_max_lines=0, k_core=12, cskg_max_nodes=0, n_heldout_eval=3000, min_heldout=20,
                seeds=[7, 13, 17])


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


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(str(output_dir), "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(str(output_dir), "metrics.json"))


# ---------------------------------------------------------------------------
# Graph + closed-form spectral code construction (glass-box; randomized SVD; degree-corrected).
# ---------------------------------------------------------------------------

def build_adjacency(edges_int, N):
    """Undirected, unweighted, deduped adjacency from int (h,r,t) edges (relation type ignored for the structural graph)."""
    h = edges_int[:, 0].astype(np.int64)
    t = edges_int[:, 2].astype(np.int64)
    mask = h != t
    h = h[mask]; t = t[mask]
    lo = np.minimum(h, t); hi = np.maximum(h, t)
    key = lo.astype(np.int64) * np.int64(N) + hi.astype(np.int64)
    key = np.unique(key)
    a = (key // N).astype(np.int64); b = (key % N).astype(np.int64)
    data = np.ones(a.shape[0], dtype=np.float64)
    A = sp.coo_matrix((data, (a, b)), shape=(N, N)).tocsr()
    A = A + A.T
    return A


def _rsvd(matvec, rmatvec, n, m, rank, n_iter, oversample, seed):
    """Randomized SVD of an implicit operator M (n x m) via matvec(X)=M@X, rmatvec(X)=M.T@X. Returns U(n x r),s(r).
    Left singular vectors U are the entity embedding basis (NetMF/Laplacian-eigenmap convention)."""
    l = min(rank + oversample, n, m)
    g = np.random.default_rng(seed * 2654435761 % (2 ** 31) + 17)
    Omega = g.standard_normal((m, l)).astype(np.float64)
    Y = matvec(Omega)                                  # n x l
    Q, _ = np.linalg.qr(Y)
    for _ in range(n_iter):
        Z, _ = np.linalg.qr(rmatvec(Q))                # m x l
        Q, _ = np.linalg.qr(matvec(Z))                 # n x l
    B = rmatvec(Q).T                                   # l x m  (= Q.T @ M)
    Ub, s, _Vt = np.linalg.svd(B, full_matrices=False)
    U = Q @ Ub
    r = min(rank, U.shape[1])
    return U[:, :r].astype(np.float64), s[:r].astype(np.float64)


def _normalized_adjacency(A):
    deg = np.asarray(A.sum(axis=1)).ravel()
    dinv = np.zeros_like(deg); nz = deg > 0
    dinv[nz] = 1.0 / np.sqrt(deg[nz])
    Dm = sp.diags(dinv)
    return (Dm @ A @ Dm).tocsr(), deg


def _rw_transition(A):
    deg = np.asarray(A.sum(axis=1)).ravel()
    dinv = np.zeros_like(deg); nz = deg > 0
    dinv[nz] = 1.0 / deg[nz]
    return (sp.diags(dinv) @ A).tocsr(), deg


def row_norm_codes(U, d):
    """Row-normalize each entity embedding to L2 norm sqrt(d) (match bipolar energy; kills degree/norm confound)."""
    E = np.zeros((U.shape[0], d), dtype=np.float32)
    r = min(d, U.shape[1])
    E[:, :r] = U[:, :r]
    nrm = np.linalg.norm(E, axis=1, keepdims=True)
    nrm[nrm < 1e-9] = 1.0
    E = E * (np.sqrt(float(d)) / nrm)
    return torch.from_numpy(E.astype(np.float32))


def lap_codes(A, d, n_iter, seed):
    """Symmetric-normalized-Laplacian spectral embedding: top-d singular vectors of S=D^-1/2 A D^-1/2 (= smoothest
    L_sym eigenvectors, since L_sym=I-S). Degree-corrected. Returns row-normalized codes (N x d)."""
    S, _deg = _normalized_adjacency(A)
    U, s = _rsvd(lambda X: S @ X, lambda X: S @ X, S.shape[0], S.shape[1], d, n_iter, SVD_OVERSAMPLE, seed * 3 + 1)
    U = U * np.sqrt(np.maximum(s, 0.0))[None, :]        # spectral embedding scale
    return row_norm_codes(U, d), s


def ppmi_codes(A, d, n_iter, seed):
    """PPMI-SVD / NetMF (window-1): PPMI(P) with P=D^-1 A, shift b=PPMI_NEG. Sparse (same support as A). rank-d SVD."""
    P, deg = _rw_transition(A)
    vol = float(deg.sum())
    dinv = np.zeros_like(deg); nz = deg > 0
    dinv[nz] = 1.0 / deg[nz]
    M = (P @ sp.diags(dinv)).tocoo()                    # (D^-1 A) D^-1 ; NetMF inner term
    val = np.log(np.maximum(M.data * (vol / PPMI_NEG), 1e-12))
    val = np.maximum(val, 0.0)                          # positive PMI
    keep = val > 0
    Mp = sp.coo_matrix((val[keep], (M.row[keep], M.col[keep])), shape=A.shape).tocsr()
    U, s = _rsvd(lambda X: Mp @ X, lambda X: Mp.T @ X, Mp.shape[0], Mp.shape[1], d, n_iter, SVD_OVERSAMPLE, seed * 5 + 2)
    U = U * np.sqrt(np.maximum(s, 0.0))[None, :]
    return row_norm_codes(U, d), s


def sr_codes(A, d, n_iter, seed):
    """Discounted successor representation M_SR = sum_{k=0}^{K} gamma^k P^k, P=D^-1 A. Implicit operator (Horner);
    rank-d randomized SVD (left singular vectors = SR eigenbasis, Stachenfeld 2017)."""
    P, _deg = _rw_transition(A)
    Pt = P.T.tocsr()

    def _series(op, X):
        # sum_k gamma^k op^k @ X  via Horner: y = X + gamma*op@y iterated K times
        y = X.copy()
        for _ in range(SR_KSTEPS):
            y = X + SR_GAMMA * (op @ y)
        return y

    U, s = _rsvd(lambda X: _series(P, X), lambda X: _series(Pt, X),
                 P.shape[0], P.shape[1], d, n_iter, SVD_OVERSAMPLE, seed * 7 + 3)
    U = U * np.sqrt(np.maximum(s, 0.0))[None, :]
    return row_norm_codes(U, d), s


# ---------------------------------------------------------------------------
# Inject a codebook into a REAL KGStore + one-shot Hebbian W (base/portable kwargs only per Gate F.3).
# ---------------------------------------------------------------------------

def build_store_with_codes(N, n_rel, d, seed, codes, train_int, fold_in=None):
    """Real KGStore; overwrite E with the given codebook (N x d); zero W; ingest train (+fold_in). W is built from the
    injected E (KGStore.ingest_triples reads self.E). R stays random-bipolar. Returns (store, W_finite)."""
    g = torch.Generator(device="cpu").manual_seed(seed * 100000 + d + 1)
    store = KGStore(n_ent=int(N), n_rel=int(n_rel), n_dim=int(d), generator=g)  # base kwargs only
    if codes is not None:
        assert codes.shape == (N, d), "codebook shape mismatch %s vs %s" % (tuple(codes.shape), (N, d))
        store.E = codes.to(torch.float32).contiguous()
    store.W.zero_()
    tri = torch.from_numpy(train_int).long()
    if fold_in is not None and fold_in.shape[0] > 0:
        tri = torch.cat([tri, torch.from_numpy(fold_in).long()], dim=0)
    store.ingest_triples(tri)
    finite = bool(torch.isfinite(store.W).all().item())
    return store, finite


def oracle_score(N, n_rel, d, seed, codes, train_int, hold_all, query_int):
    """ORACLE readout: fold-in W over the injected codebook, native recall + score vs the same codebook."""
    store, fin = build_store_with_codes(N, n_rel, d, seed, codes, train_int, fold_in=hold_all)
    recall = base.native_query_recall(store, query_int)
    return base.score_from_codes(recall, store.E), fin


def compose_neighbor_codes(train_codes, support_int, N, d, seed, scramble=False):
    """Inductive compose: held-out tail t's code = row-normalized mean of its SUPPORT-neighbor (head) TRAIN codes.
    scramble=True aggregates over RANDOM entities (same count) -> must-fail (needs the TRUE neighborhood)."""
    Ep = train_codes.clone()
    heads = support_int[:, 0].astype(np.int64)
    tails = support_int[:, 2].astype(np.int64)
    if scramble:
        rng = np.random.default_rng(seed * 8887 + 5)
        heads = rng.integers(0, N, size=heads.shape[0]).astype(np.int64)
    acc = torch.zeros(N, d, dtype=torch.float32)
    acc.index_add_(0, torch.from_numpy(tails).long(), train_codes[torch.from_numpy(heads).long()])
    cnt = torch.zeros(N, dtype=torch.float32)
    cnt.index_add_(0, torch.from_numpy(tails).long(), torch.ones(tails.shape[0], dtype=torch.float32))
    mask = cnt > 0
    comp = acc[mask]
    nrm = comp.norm(dim=1, keepdim=True); nrm[nrm < 1e-9] = 1.0
    Ep[mask] = comp * (float(np.sqrt(d)) / nrm)
    return Ep


def compose_score(N, n_rel, d, seed, train_codes, train_int, support_int, query_int, scramble=False):
    """Train-only W over train_codes; patch held-out rows with composed neighbor codes; native recall + score."""
    store, fin = build_store_with_codes(N, n_rel, d, seed, train_codes, train_int, fold_in=None)
    Ep = compose_neighbor_codes(train_codes, support_int, N, d, seed, scramble=scramble)
    store.E = Ep.contiguous()                            # patched candidate codebook for the readout
    recall = base.native_query_recall(store, query_int)  # recall uses patched E for the (train) query head bind
    return base.score_from_codes(recall, store.E), fin


# ---------------------------------------------------------------------------
# Score all arms PAIRED on the SAME held-out QUERY edges.
# ---------------------------------------------------------------------------

def score_all_arms(prep, cfg, seed):
    N = prep["N"]; n_rel = prep["n_rel"]; d = cfg["d_code"]; n_iter = cfg["svd_n_iter"]
    train_int = prep["train_int"]; support_int = prep["support_int"]; query_int = prep["query_int"]
    hold_all = prep["hold_all"]; all_true = prep["all_true"]

    # oracle graph = train + held-out edges (consistent with fold-in); train graph = train-only (compose).
    A_oracle = build_adjacency(np.concatenate([train_int, hold_all], axis=0), N)
    A_train = build_adjacency(train_int, N)

    # RAND_ORACLE uses the base native path VERBATIM (bit-identical bipolar E) so the positive control reproduces the
    # CITED native ~0.023 @ d1024 exactly; its train-only store shares BIT-IDENTICAL E -> the random codebook for the
    # apples-to-apples RAND_COMPOSE / scramble aggregation.
    store_rand_o = base.build_store(N, n_rel, d, seed, train_int, fold_in=hold_all)
    recall_r = base.native_query_recall(store_rand_o, query_int)
    rand_codes = base.build_store(N, n_rel, d, seed, train_int).E.contiguous()   # same E/R as store_rand_o (seed,d)

    lap_o, lap_s = lap_codes(A_oracle, d, n_iter, seed)
    ppmi_o, ppmi_s = ppmi_codes(A_oracle, d, n_iter, seed)
    sr_o, sr_s = sr_codes(A_oracle, d, n_iter, seed)
    lap_tr, _ = lap_codes(A_train, d, n_iter, seed)

    finite = bool(torch.isfinite(store_rand_o.W).all().item())
    arm_scores = {RAND_ORACLE: base.score_from_codes(recall_r, store_rand_o.E)}
    for name, codes in [(LAP_ORACLE, lap_o), (PPMI_ORACLE, ppmi_o), (SR_ORACLE, sr_o)]:
        sc, fin = oracle_score(N, n_rel, d, seed, codes, train_int, hold_all, query_int)
        arm_scores[name] = sc; finite = finite and fin
    sc, fin = compose_score(N, n_rel, d, seed, lap_tr, train_int, support_int, query_int, scramble=False)
    arm_scores[LAP_COMPOSE] = sc; finite = finite and fin
    sc, fin = compose_score(N, n_rel, d, seed, rand_codes, train_int, support_int, query_int, scramble=False)
    arm_scores[RAND_COMPOSE] = sc; finite = finite and fin
    sc, fin = compose_score(N, n_rel, d, seed, lap_tr, train_int, support_int, query_int, scramble=True)
    arm_scores[LAP_COMPOSE_SCRAMBLE] = sc; finite = finite and fin
    arm_scores[RAND_NULL] = base.random_scores(N, query_int, d, seed)

    arm_metric, arm_sig = {}, {}
    for name, sc in arm_scores.items():
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
    pop_m, pop_rank_vec = pop_hits(prep["gd"].rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    # spectral-energy diagnostics (fraction of ||.||_F^2 captured by rank d) + block purity is self-test only
    diag = dict(finite=bool(finite), d_code=int(d), N=int(N),
                lap_singval_top=float(lap_s[0]) if lap_s.shape[0] else float("nan"),
                lap_singval_min=float(lap_s[-1]) if lap_s.shape[0] else float("nan"))
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores, diag=diag)


# ---------------------------------------------------------------------------
# Prepare a seed-deterministic split (bit-identical to base + additive + residue arenas given seed).
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
    return dict(ent2i=ent2i, rel2i=rel2i, N=N, n_rel=n_rel, train_int=train_int, support_int=support_int,
                query_int=query_int, hold_all=hold_all, hold_ids=hold_ids, n_cold=n_cold,
                n_query_total=n_query_total, gd=gd, all_true=all_true)


def run_corpus(pool_lbl, cfg, seed, corpus_name):
    prep = prepare_corpus(pool_lbl, cfg, seed)
    result = dict(corpus=corpus_name, seed=seed, N=int(prep["N"]), n_rel=int(prep["n_rel"]),
                  n_train=int(prep["train_int"].shape[0]), n_heldout_entities=len(prep["hold_ids"]),
                  n_support=int(prep["support_int"].shape[0]), n_query_total=prep["n_query_total"],
                  n_query_scored=int(prep["query_int"].shape[0]), n_cold=int(prep["n_cold"]), d_code=int(cfg["d_code"]))
    if prep["query_int"].shape[0] < 1:
        result["empty"] = True
        return result, None
    fs = score_all_arms(prep, cfg, seed)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs={a: fs["arm_sig"][a] for a in ALL_ARMS},
        diag=fs["diag"],
    )
    return result, fs


# ---------------------------------------------------------------------------
# Lift verdict over per-seed results.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _m(ps, arm):
    return ps["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def lift_verdict(per_seed):
    def agg(arm):
        return _nm([_m(ps, arm) for ps in per_seed])

    mrr = {a: agg(a) for a in ALL_ARMS}
    rand_o = mrr[RAND_ORACLE]; rand_null = mrr[RAND_NULL]; pop = mrr[POP]
    lap_o = mrr[LAP_ORACLE]; ppmi_o = mrr[PPMI_ORACLE]; sr_o = mrr[SR_ORACLE]
    lap_c = mrr[LAP_COMPOSE]; rand_c = mrr[RAND_COMPOSE]; lap_c_scr = mrr[LAP_COMPOSE_SCRAMBLE]

    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")

    spec_vals = [v for v in [lap_o, ppmi_o, sr_o] if v == v]
    best_spec = max(spec_vals) if spec_vals else float("nan")
    best_spec_name = max([(LAP_ORACLE, lap_o), (PPMI_ORACLE, ppmi_o), (SR_ORACLE, sr_o)],
                         key=lambda kv: (kv[1] if kv[1] == kv[1] else -1))[0]
    oracle_lift = _sub(best_spec, rand_o)
    compose_lift = _sub(lap_c, rand_c)
    compose_scr_margin = _sub(lap_c, lap_c_scr)

    # positive controls
    rand_reproduces = bool(rand_o == rand_o and abs(rand_o - CITED_NATIVE_1024) <= REPRODUCE_TOL)
    null_floor = bool(rand_null == rand_null and rand_null <= RAND_NULL_FLOOR)
    oracle_ratio = _ratio(rand_o, rand_null)
    oracle_fires = bool(_sub(rand_o, rand_null) == _sub(rand_o, rand_null) and _sub(rand_o, rand_null) >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    finite = all(ps.get("diag", {}).get("finite", False) for ps in per_seed)
    broken = bool(pop == pop and rand_null == rand_null and (pop - rand_null) > max(RAND_NULL_FLOOR, 0.005))
    pos_controls_ok = bool(rand_reproduces and null_floor and oracle_fires and finite and not broken)

    oracle_lifts = bool(oracle_lift == oracle_lift and oracle_lift >= LIFT_MARGIN)
    compose_lifts = bool(compose_lift == compose_lift and compose_lift >= LIFT_MARGIN
                         and compose_scr_margin == compose_scr_margin and compose_scr_margin >= COMPOSE_SCRAMBLE_MARGIN)

    if not pos_controls_ok:
        verdict = "INCONCLUSIVE_POSCONTROL_OR_ORACLE_FAILED"
    elif oracle_lifts and compose_lifts:
        verdict = "GRAPH_STRUCTURE_LIFTS_BOTH"
    elif oracle_lifts or compose_lifts:
        verdict = "GRAPH_STRUCTURE_LIFTS_PARTIAL_MIDDLE"
    else:
        verdict = "NO_LIFT_GRAPH_STRUCTURE_UNEXPLOITABLE"

    frac_add = _ratio(best_spec, CITED_ADD_ORACLE)
    verdict_msg = (
        "%s || ORACLE MRR: RAND=%s(repro0.023=%s) LAP=%s PPMI=%s SR=%s -> best_spec(%s)=%s (lift_vs_rand=%s >=%.3f=%s) "
        "|| COMPOSE MRR: LAP=%s RAND=%s (lift=%s >=%.3f=%s) SCRAMBLE=%s (scr_margin=%s >=%.3f=%s) "
        "|| RAND_NULL=%s POP=%s frac_of_add(0.137)=%s || MP: gini=%.3f lam2=%.3f=%.1fxrho top20E=%.4f "
        "(spiked_present=True,not_lowrank) || oracle_fires=%s pos_controls=%s broken=%s seeds=%d"
        % (verdict, _fmt(rand_o), rand_reproduces, _fmt(lap_o), _fmt(ppmi_o), _fmt(sr_o), best_spec_name,
           _fmt(best_spec), _fmt(oracle_lift), LIFT_MARGIN, oracle_lifts, _fmt(lap_c), _fmt(rand_c), _fmt(compose_lift),
           LIFT_MARGIN, bool(compose_lift == compose_lift and compose_lift >= LIFT_MARGIN), _fmt(lap_c_scr),
           _fmt(compose_scr_margin), COMPOSE_SCRAMBLE_MARGIN,
           bool(compose_scr_margin == compose_scr_margin and compose_scr_margin >= COMPOSE_SCRAMBLE_MARGIN),
           _fmt(rand_null), _fmt(pop), _fmt(frac_add), MP_GINI, MP_LAMBDA2, MP_LAMBDA2 / MP_RHO_NULL, MP_TOP20_ENERGY,
           oracle_fires, pos_controls_ok, broken, len(per_seed)))

    def _rnd(x, nd=6):
        return round(x, nd) if (x == x and x != float("inf")) else (None if x != x else "inf")

    metric_keys = ["hits@%d" % kk for kk in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    gates = dict(
        verdict=verdict,
        oracle_mrr=dict(RAND=_rnd(rand_o), LAP=_rnd(lap_o), PPMI=_rnd(ppmi_o), SR=_rnd(sr_o),
                        best_spec=_rnd(best_spec), best_spec_name=best_spec_name),
        compose_mrr=dict(LAP=_rnd(lap_c), RAND=_rnd(rand_c), SCRAMBLE=_rnd(lap_c_scr)),
        oracle_lift=_rnd(oracle_lift), compose_lift=_rnd(compose_lift), compose_scr_margin=_rnd(compose_scr_margin),
        oracle_lifts=oracle_lifts, compose_lifts=compose_lifts,
        random_null_mrr=_rnd(rand_null), frac_of_additive_oracle=_rnd(frac_add),
        rand_reproduces=rand_reproduces, null_floor=null_floor, oracle_fires=oracle_fires,
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        finite=finite, broken=broken, pos_controls_ok=pos_controls_ok,
        mp_precheck=dict(gini=MP_GINI, lambda2=MP_LAMBDA2, rho_null=MP_RHO_NULL, lambda2_over_rho=round(MP_LAMBDA2 / MP_RHO_NULL, 2),
                         top20_energy=MP_TOP20_ENERGY, spiked_structure_present=True, low_rank=False,
                         note="spiked community structure PRESENT above MP bulk edge but NOT low-rank (top20 energy 1.3pct)"),
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        controls=dict(POP=_rnd(pop)),
        bands=dict(CITED_NATIVE_1024=CITED_NATIVE_1024, CITED_ADD_ORACLE=CITED_ADD_ORACLE,
                   CITED_ADD_COMPOSE=CITED_ADD_COMPOSE, CITED_RELIEF_8192=CITED_RELIEF_8192,
                   D_CODE=D_CODE, LIFT_MARGIN=LIFT_MARGIN, COMPOSE_SCRAMBLE_MARGIN=COMPOSE_SCRAMBLE_MARGIN,
                   REPRODUCE_TOL=REPRODUCE_TOL, RAND_NULL_FLOOR=RAND_NULL_FLOOR, SR_GAMMA=SR_GAMMA, SR_KSTEPS=SR_KSTEPS),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Planted SBM arena: B blocks; dense intra-block, sparse inter-block edges; held-out entities in blocks. The
# normalized-Laplacian spectral embedding recovers blocks -> LAP codes cluster by block. Fold-in makes LAP_ORACLE
# answerable above the chance floor; compose over TRUE support-neighbors lands the held-out code in its block while
# aggregating RANDOM entities (scramble) collapses. Deterministic (default_rng).
# ---------------------------------------------------------------------------

def build_planted_sbm_arena(seed, n_blocks, members_per_block, n_rels, edges_per_member):
    rng = np.random.default_rng(seed * 100057 + 9)
    N = n_blocks * members_per_block
    block_of = np.repeat(np.arange(n_blocks), members_per_block)
    members = [np.where(block_of == b)[0] for b in range(n_blocks)]
    edges = []
    for v in range(N):
        b = int(block_of[v])
        for _ in range(edges_per_member):
            if rng.random() < 0.92:                                  # intra-block
                u = int(rng.choice(members[b]))
            else:                                                    # inter-block
                u = int(rng.integers(0, N))
            if u == v:
                u = (u + 1) % N
            r = int(rng.integers(0, n_rels))
            edges.append(("e%d" % v, "r%d" % r, "e%d" % u))
    return list(dict.fromkeys(edges)), block_of


def _block_purity(codes, block_of, k=8):
    """Fraction of nearest-neighbor pairs (in top-k spectral dims) that share a block -> the embedding separates blocks."""
    X = codes.numpy()[:, :k]
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    S = X @ X.T
    np.fill_diagonal(S, -1e9)
    nn = S.argmax(axis=1)
    return float((block_of[nn] == block_of).mean())


def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _selftest_real_store_smoke(cfg):
    """Gate F.1: CONSTRUCT the REAL KGStore + inject a spectral codebook + RUN ingest_triples. Populates exercised set."""
    exercised = set()
    d = cfg["d_code"]
    tri = np.array([[0, 0, 1], [1, 0, 2], [2, 1, 0], [3, 1, 0]], dtype=np.int64)
    A = build_adjacency(tri, 4)
    exercised.add("build_adjacency")
    codes, _s = lap_codes(A, d, cfg["svd_n_iter"], 7)
    exercised.add("lap_codes")
    store, fin = build_store_with_codes(4, 2, d, 7, codes, tri, fold_in=tri[:1])
    exercised.add("KGStore")
    exercised.add("build_store_with_codes")
    if store._n_triples_ingested > 0:
        exercised.add("ingest_triples")
    rec = base.native_query_recall(store, tri)
    if rec.shape == (4, d):
        exercised.add("native_query_recall")
    return exercised, bool(fin and rec.shape == (4, d))


def _mechanism_selftest_body():
    cfg = dict(SELFTEST_CFG)
    out = {}
    exercised, real_ok = _selftest_real_store_smoke(cfg)

    pool, block_of = build_planted_sbm_arena(7, cfg["st_blocks"], cfg["st_members"], cfg["st_rels"],
                                             cfg["st_edges_per_member"])
    prep = prepare_corpus(pool, cfg, 7)
    if prep["query_int"].shape[0] < cfg["min_heldout"]:
        out["fail"] = "planted SBM arena produced too few held-out queries (%d)" % prep["query_int"].shape[0]
        return False, out
    res, fs = run_corpus(pool, cfg, 7, "PLANTED_SBM")
    am = fs["arm_metric"]
    sm = {a: am[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(fs["arm_sig"][a] for a in ALL_ARMS))

    lap_o = sm[LAP_ORACLE]; rand_null = sm[RAND_NULL]; lap_c = sm[LAP_COMPOSE]; lap_c_scr = sm[LAP_COMPOSE_SCRAMBLE]
    lap_recovers = bool(lap_o == lap_o and lap_o >= ST_LAP_ORACLE_MIN)
    lap_beats_null = bool(lap_o == lap_o and rand_null == rand_null and (lap_o - rand_null) >= ST_ORACLE_BEATS_NULL)
    compose_scr_fails = bool(lap_c == lap_c and lap_c_scr == lap_c_scr and (lap_c - lap_c_scr) >= ST_COMPOSE_SCRAMBLE_MARGIN)
    arms_differ = bool(n_sigs >= 5)
    finite = bool(fs["diag"]["finite"])

    # spectral-embedding-produces-structure discriminator: the LAP embedding must separate the planted blocks.
    A_full = build_adjacency(np.concatenate([prep["train_int"], prep["hold_all"]], axis=0), prep["N"])
    lap_codes_full, _ = lap_codes(A_full, cfg["d_code"], cfg["svd_n_iter"], 7)
    purity = _block_purity(lap_codes_full, block_of, k=8)
    embedding_separates = bool(purity >= ST_BLOCK_PURITY_MIN)

    # VACUOUS-SMOKE guard: on the planted SBM the LAP oracle MUST separate from the chance floor.
    lap_frozen = bool((lap_o - rand_null) < ST_ORACLE_BEATS_NULL)
    assert_discriminator_fires(lap_frozen, control_name=RAND_NULL,
                               headline_name="lap_oracle_recovers_planted_heldout_above_chance", run_mode="self_test",
                               extra="LAP_ORACLE did NOT separate from RAND_NULL on the planted SBM arena -> arena "
                                     "not answerable / apparatus frozen")

    st_verdict, _stmsg, _stg = lift_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(lap_recovers and lap_beats_null and embedding_separates),
         "control_name": "RAND_NULL", "headline_name": "lap_oracle_recovers_planted_and_embedding_separates_blocks",
         "extra": "planted SBM: the closed-form Laplacian spectral codebook recovers planted held-out tails above "
                  "chance (fold-in) AND the embedding separates the planted blocks (purity>=%.2f) -> the spectral "
                  "code path carries recoverable structure and the readout fires" % ST_BLOCK_PURITY_MIN},
        {"kind": "metric_moves", "metric_name": "settings_mrr",
         "values": [rand_null, lap_c_scr, sm[RAND_ORACLE], lap_o],
         "extra": "the arms MOVE on synthetic: RAND_NULL=%.3f COMPOSE_SCRAMBLE=%.3f RAND_ORACLE=%.3f LAP_ORACLE=%.3f "
                  "(not frozen)" % (rand_null, lap_c_scr, sm[RAND_ORACLE], lap_o)},
        {"kind": "negative_control_margin",
         "control_scores": [rand_null, lap_c_scr, sm[POP]],
         "headline_threshold": lap_c, "higher_is_pass": True, "margin": ST_COMPOSE_SCRAMBLE_MARGIN, "n_repeats_min": 3,
         "control_name": "RANDNULL_COMPOSESCRAMBLE_POP_below_lap_compose", "extra":
         "RAND_NULL + scrambled-neighbor compose + POP sit below LAP_COMPOSE by the MRR margin -> the compose lift "
         "needs the TRUE support-neighborhood aggregation, not spectral-code volume"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["lap_recovers", "lap_beats_null", "embedding_separates", "compose_scr_fails",
                                    "arms_differ", "oracle_fires", "real_code_path", "lift_verdict"],
         "exercised_gates": ["lap_recovers", "lap_beats_null", "embedding_separates", "compose_scr_fails",
                             "arms_differ", "oracle_fires", "real_code_path", "lift_verdict"],
         "extra": "lift_verdict=%s at self-test scale" % st_verdict},
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["KGStore", "build_store_with_codes", "ingest_triples", "native_query_recall"],
         "exercised_entrypoints": exercised,
         "extra": "self-test constructs the REAL KGStore, injects a closed-form spectral codebook, runs ingest_triples"},
        {"kind": "substrate_signature", "callable_obj": KGStore, "callable_name": "KGStore",
         "kwargs": {"n_ent": 1, "n_rel": 1, "n_dim": 16, "generator": None},
         "extra": "base/portable KGStore kwargs only (n_ent,n_rel,n_dim,generator); no optional init_entities"},
        {"kind": "guard_baseline_valid", "baseline_score": sm[RAND_ORACLE], "floor_score": rand_null,
         "guard_name": "BROKEN_POP_BEATS_RANDNULL", "baseline_name": "RAND_ORACLE", "floor_name": "RAND_NULL",
         "eps": 0.02,
         "extra": "the BROKEN guard compares POP against the RAND_NULL floor (not a structural-zero POP); RAND_ORACLE "
                  "sits above the floor so the arena baseline is valid"},
    ], run_mode="self_test")

    out.update(
        real_code_path_ok=bool(real_ok), exercised_entrypoints=sorted(exercised),
        planted={a: (round(sm[a], 5) if sm[a] == sm[a] else None) for a in ALL_ARMS},
        block_purity=round(purity, 4), n_distinct_sigs=n_sigs, lap_recovers=lap_recovers,
        lap_beats_null=lap_beats_null, embedding_separates=embedding_separates, compose_scr_fails=compose_scr_fails,
        arms_differ=arms_differ, finite=finite, selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest",
                                     "real_code_path_F1", "substrate_signature_F2_F3", "guard_baseline_valid_F4"],
    )
    ok = bool(real_ok and lap_recovers and lap_beats_null and embedding_separates and compose_scr_fails
              and arms_differ and finite and vp_ok)
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

    _log("device=cpu run_mode=%s seeds=%s d_code=%s svd_iter=%s sr_gamma=%s"
         % (run_mode, seeds, cfg["d_code"], cfg["svd_n_iter"], SR_GAMMA))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s | LAP_ORACLE=%s RAND_NULL=%s LAP_COMPOSE=%s SCRAMBLE=%s purity=%s | lap_recovers=%s "
         "embedding_separates=%s compose_scr_fails=%s real_code=%s vp_ok=%s"
         % (st_ok, (st_res.get("planted") or {}).get(LAP_ORACLE), (st_res.get("planted") or {}).get(RAND_NULL),
            (st_res.get("planted") or {}).get(LAP_COMPOSE), (st_res.get("planted") or {}).get(LAP_COMPOSE_SCRAMBLE),
            st_res.get("block_purity"), st_res.get("lap_recovers"), st_res.get("embedding_separates"),
            st_res.get("compose_scr_fails"), st_res.get("real_code_path_ok"), st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s"
                        % {kk: st_res.get(kk) for kk in ("lap_recovers", "lap_beats_null", "embedding_separates",
                           "compose_scr_fails", "real_code_path_ok", "arms_differ", "validity_preflight_ok")},
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS GRAPH_SPECTRAL_ENTITY_CODES: on a planted SBM the closed-form Laplacian spectral "
                        "codebook recovers planted held-out tails above chance, the embedding separates the planted "
                        "blocks, compose over scrambled neighbors fails, the REAL KGStore spectral-code path "
                        "(ingest_triples) is exercised; 7 validity-preflight checks declared (F.1-F.4 ENFORCE)",
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
            if not res["diag"]["finite"]:
                raise RuntimeError("non-finite W seed=%d" % seed)
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            ah = res["arm_hits"]
            _log("seed=%d nq=%d | RAND_O=%s LAP_O=%s PPMI_O=%s SR_O=%s | LAP_C=%s RAND_C=%s SCR=%s NULL=%s (%.1fs)"
                 % (seed, res["n_query_scored"], _fmt(ah[RAND_ORACLE][CEIL_METRIC]), _fmt(ah[LAP_ORACLE][CEIL_METRIC]),
                    _fmt(ah[PPMI_ORACLE][CEIL_METRIC]), _fmt(ah[SR_ORACLE][CEIL_METRIC]),
                    _fmt(ah[LAP_COMPOSE][CEIL_METRIC]), _fmt(ah[RAND_COMPOSE][CEIL_METRIC]),
                    _fmt(ah[LAP_COMPOSE_SCRAMBLE][CEIL_METRIC]), _fmt(ah[RAND_NULL][CEIL_METRIC]), time.time() - ts))
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

    verdict, verdict_msg, gates = lift_verdict(per_seed)
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
