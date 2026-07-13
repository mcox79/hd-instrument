"""CLOSED-FORM COORD-SOURCE probe: can a NON-SGD (closed-form / rule-derived) coordinate derivation carry enough
relational geometry for the SAME held-out-entity ANCHOR_COMPOSE arena to reach toward the LEARNED-SGD 0.128?

CONTEXT (the remaining strict-glass-box path). The code-family sweep landed CODES_DONT_STRUCTURED_HURTS_LEARNED_NEEDED
(MEASURED@data/exp_native_code_family_sweep_cskg_v1/metrics.json): fixed STRUCTURED glass-box CODES do NOT carry the
additive relational geometry (all near RANDOM ~0.02 oracle). The LEARNED-SGD coordinates ARE needed for the functional
path (built as AdditiveKGMap's default LearnedSGDCoordinateSource). The remaining STRICT (no-SGD) option is not codes
but CLOSED-FORM COORDINATES: derive the base entity coords X[N,k] and relation displacements D[n_rel,k] by a
closed-form, non-gradient method, then run the CONFIRMED ANCHOR_COMPOSE compose+direct-distance arena on them. If a
closed-form coord source reaches a MATERIAL fraction of the learned 0.128, it drops into AdditiveKGMap's swappable
CoordinateSource seam as a STRICT-glass-box source; if it collapses toward random, the LEARNED source is essential and
the functional path is the only one (documented).

THE CLOSED-FORM METHOD (spectral init + closed-form ALS of the TransE score; ALL non-gradient):
  Stage 1  SPECTRAL X: Laplacian-eigenmap embedding of the symmetric-normalized relational adjacency (train edges +
           self-loops). X0 = top-(k+1) singular vectors of Dinv A Dinv (trivial sqrt-degree component dropped) via
           truncated randomized SVD (torch.svd_lowrank; a standard scalable spectral embedding, non-gradient,
           deterministic under a seeded generator). Connected nodes -> Euclidean-close.
  Stage 2  CLOSED-FORM ALS: alternate two closed-form updates for n_sweeps (NO gradient descent):
             (a) D_r = mean_{(h,r,t)} (X_t - X_h)                 # exact LS minimizer of TransE loss over D given X
             (b) X_i = [lam*X0_i + sum_{e:h=i}(X_t - D_r) + sum_{e:t=i}(X_h + D_r)] / (deg_i + lam)   # Jacobi solve
           (b) is the Jacobi iteration of the normal equations of min_X sum_e ||X_h + D_r - X_t||^2 + lam||X - X0||^2
           (a translational least-squares; lam anchors to the spectral init and keeps isolated rows grounded). Each
           sweep is closed-form linear algebra; the alternation makes X translationally consistent so the RELATION
           operator D carries real signal (spectral-only D is ~0 -> the scramble control cannot fail; ALS fixes that).
Both stages are non-SGD. This is a drop-in CoordinateSource: only the X/D DERIVATION changes; the compose op
(build_anchor_compose_codes) + score readout (additive_direct_scores) are IMPORTED VERBATIM from the learned cell so
the compose+score path is BIT-IDENTICAL and the coord-source is the only knob (isolates the question).

ARMS (SHARDED per-entity codes; relations = per-TYPE operators; held-out bundle is a per-ENTITY mean):
  CLOSEDFORM_ANCHOR   : mechanism. closed-form X/D (TRAIN only); held-out codes REPLACED by E_derived = mean_i(X[h_i]
                        +D[r_i]) over the entity's SUPPORT edges (zero extra work; the same verbatim bundle op).
  CLOSEDFORM_MEMORIZE : control. closed-form X/D (train only); held-out codes stay at their BASE spectral row (isolated
                        held-out entities have no train edge -> degenerate row) == the no-induction analog of the
                        learned ADDITIVE_TRANSE (random-init held-out row). Expect ~floor.
  CLOSEDFORM_SCRAMBLE : must-fail. ANCHOR bundle with the SUPPORT relation ids SCRAMBLED (D[perm[r]]) -> same anchors,
                        same degrees, broken relational signal. Isolates RELATION signal vs a proximity/anchor-identity
                        /degree confound (spectral coords place neighbours close, so mean-of-anchors alone recovers a
                        chunk -> scramble quantifies that confound).
  CLOSEDFORM_ORACLE   : positive control / transductive ceiling. closed-form X/D with the held-out edges FOLDED INTO
                        the adjacency + D estimation -> held-out entities get REAL closed-form coords. If it fires, the
                        arena is answerable BY CLOSED-FORM GEOMETRY and a null in ANCHOR is interpretable (cannot
                        zero-shot compose it), not an unrepresentable geometry. If it does NOT fire, closed-form
                        spectral+ALS geometry is insufficient even transductively (a stronger strict-dead).
  RANDOM_CODES        : the null (random X + random D + same additive readout). The bar to clear.
  BASELINE_POP        : frequency incumbent (held-out tails have train freq 0 -> ~floor; fit-independence sanity).

CEILING-AWARE EVAL (identical discipline to the learned cell; primary metric = FILTERED MRR rank-vs-ALL, degree-
unbiased). The held-out-ENTITY arena has an INFO-CEILING (even the best in-arena code is constrained by an entity's
OWN sparse edges). Primary metric = filtered MRR (KGE standard, no sampled-negative pool -> no popularity/degree bias).

PRE-REG BANDS (picked BEFORE the run; primary = filtered MRR; the question is "material fraction of the LEARNED 0.128"):
  LEARNED reference (CITED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr):
      ANCHOR_COMPOSE (learned SGD) = 0.12821 ; ORACLE_ADDITIVE = 0.137293 ; RANDOM = 0.000483.
  ORACLE-FIRES (arena answerable BY CLOSED-FORM) : CF_ORACLE_mrr >= 3x RANDOM_mrr AND CF_ORACLE_mrr - RANDOM_mrr >=
      0.003. If it does not fire -> INCONCLUSIVE_CLOSEDFORM_ORACLE_UNDERFIT (closed-form geometry insufficient even
      transductively = strict-dead by geometry insufficiency).
  STRICT_VIABLE : CF_ANCHOR_mrr >= 0.50 * LEARNED_ANCHOR_REF (=0.0641; recovers >=half the learned headroom) AND
      CF_ANCHOR - RANDOM >= MIN_SIG_MRR (0.002, non-noise) AND scramble CONTROLLED ((CF_SCRAMBLE - RANDOM) <= 0.25 *
      CF_ORACLE_headroom -> the viability is RELATIONAL not a proximity confound) AND ORACLE fires AND not broken. A
      viable strict coord-source -> drops into AdditiveKGMap's CoordinateSource seam.
  MIDDLE (PARTIAL) : 0.15 * LEARNED_ANCHOR_REF (=0.0192) <= CF_ANCHOR_mrr < 0.0641 with ORACLE firing (some but
      sub-half transfer; stratify by support degree to localize).
  STRICT_DEAD : CF_ANCHOR_mrr < 0.0192 (~random) with ORACLE firing -> the learned SGD coords are essential; the
      functional path is the only one (documented). (ORACLE-underfit is the geometry-insufficiency flavour of dead.)

FIVE+ VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight; F.1-F.4 = ENFORCE):
  (1) positive_control            : CF_ORACLE recovers folded-in held-out tails and clears RANDOM by the ceiling-aware
                                    (ratio + abs) fire gate on MRR (proves the closed-form viable bar is achievable).
  (2) metric_moves                : held-out MRR MOVES across [RANDOM, CF_MEMORIZE, CF_ANCHOR, CF_ORACLE].
  (3) negative_control_margin     : RANDOM + CF_SCRAMBLE sit below CF_ANCHOR by an MRR margin, deterministically (>=2).
  (4) full_gates_exercised        : aggregate_and_verdict runs on the planted per-seed, firing every fail-closed gate.
  (5) real_code_path (F.1)        : the self-test constructs/calls the REAL closed-form objects the FULL uses
                                    (closedform_als_coords, build_anchor_compose_codes, additive_direct_scores,
                                    fit_and_score_closedform) at tiny scale -- no synthetic-only branch.
  (6) substrate_signature (F.2/3) : every closed-form / reused call binds against its LIVE inspect.signature with
                                    base/portable kwargs (closedform_als_coords, build_anchor_compose_codes,
                                    additive_direct_scores, torch.svd_lowrank).
  (7) guard_baseline_valid (F.4)  : the broken-test guard fires against CF_ORACLE (the transductive ceiling, above the
                                    floor), NOT against POP (structurally ~0 on held-out arenas) -> declared valid vs
                                    the RANDOM floor so the guard cannot mis-fire on this arena's structural zeros.

## Compute architecture
class (b) sequential-CPU with justification: this is CLOSED-FORM LINEAR ALGEBRA, NO SGD. Per corpus: one truncated
randomized SVD of a sparse (N,N) normalized adjacency (torch.svd_lowrank, q=k+1) + n_sweeps closed-form ALS updates
(vectorized index_add_ over edges) + query-chunked batched distance readouts (the (nq,N) map is never materialized
whole). No gradient training, no OOM-prone (batch,n_neg,k) transient -> no memsmoke needed; the whole FULL is a few
minutes on CPU. remote_cpu forces cpu (this is CPU-appropriate: the CPU is idle and closed-form linalg is light).
Storage SHARDED (each entity its own code; relations = per-TYPE additive displacements; the ONLY bundle is the
per-ENTITY anchor mean). device=auto; remote_cpu -> cpu.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 6 arms produce >=5 distinct score signatures per seed.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: primary metric FILTERED MRR + ceiling-relative discipline; bands as fractions of the MEASURED
#   learned reference headroom -> discriminator_reachability OK by construction (learned ORACLE=0.137 proves the arena
#   is answerable; the question is whether the CLOSED-FORM source reaches a fraction of the learned 0.128).
# - baseline_in_band: CF_ORACLE must fire (>=3x RANDOM_mrr AND headroom>=0.003); RANDOM/POP near the 1/N floor.
# - discriminator survives scale: analytical -- a spectral+ALS coord source is a FIXED derivation; the memorize null
#   (held-out has no train edge -> degenerate base row) persists at ANY N; the ORACLE-fires control proves the metric
#   can move at scale. The self-test fires ANCHOR-beats-RANDOM + scramble-fails + oracle-fires deterministically.
# - HARD-PASS strictly above floor: STRICT_VIABLE 0.50*ref clears STRICT_DEAD 0.15*ref by 0.35*ref + a MIN_SIG floor.
# - HP_SCOPE: STRICT_VIABLE gates apply to CLOSEDFORM_ANCHOR only. CF_ORACLE = positive control (must fire); RANDOM/
#   CF_SCRAMBLE = must-not-clear-bar controls; CF_MEMORIZE = no-induction head-to-head; POP = fit-independence sanity.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 6 arms + >=5 sigs.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- ORACLE_FIRE_RATIO/ABS + LEARNED-reference fractions
#   pre-registered, NOT tuned on real data; scramble ceiling is a fraction of the MEASURED closed-form oracle headroom.
# - all numbers tagged MEASURED@/CITED@ in the prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints).

ASCII-only. No bare except; except SystemExit before except Exception. Explicit float32. torch.Generator seeded.
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
from experiments._course_c_rotate_core_v1 import additive_direct_scores  # noqa: E402
# VERBATIM compose op + the confirmed held-out-entity split/arena, imported so the compose+score path is BIT-IDENTICAL
# to the learned cell and the coord-source is the ONLY thing that changes.
from experiments.exp_anchor_compose_inductive_entity_cskg_v1 import (  # noqa: E402
    build_planted_transe_arena, build_heldout_entity_split_ac, build_anchor_compose_codes,
)

ANCHOR_NAME = "anchor_compose_closedform_coord_cskg_v1"

# ---- Arm names ----
CF_ANCHOR = "CLOSEDFORM_ANCHOR"      # mechanism: closed-form X/D; held-out = anchor bundle (zero extra work)
CF_MEM = "CLOSEDFORM_MEMORIZE"       # control: closed-form X/D; held-out = base (degenerate) spectral row
CF_SCR = "CLOSEDFORM_SCRAMBLE"       # must-fail: anchor bundle with support relation ids scrambled
CF_ORACLE = "CLOSEDFORM_ORACLE"      # positive control: closed-form X/D with held-out folded in (transductive ceiling)
RANDOM = "RANDOM_CODES"              # null (clear this by >= MIN_SIG)
POP = "BASELINE_POP"                 # frequency incumbent (fit-independence sanity)
GEOM_ARMS = [CF_ANCHOR, CF_MEM, CF_SCR, CF_ORACLE, RANDOM]   # scored via geometry readouts
ALL_ARMS = GEOM_ARMS + [POP]

# ---- LEARNED reference (CITED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr) ----
LEARNED_ANCHOR_REF = 0.12821         # CITED: learned-SGD ANCHOR_COMPOSE filtered MRR (the target to reach toward)
LEARNED_ORACLE_REF = 0.137293        # CITED: learned-SGD ORACLE_ADDITIVE filtered MRR (arena is answerable)

# ---- Ceiling-aware, degree-unbiased eval (identical discipline to the learned cell) ----
EVAL_KS = (1, 3, 10, 100)
CEIL_METRIC = "mrr"
PRIMARY_METRIC = "hits@%d" % PRIMARY_K   # PRIMARY_K = 10; legacy hits display + degree stratification

# ORACLE-fire gate (arena answerable under the primary metric by CLOSED-FORM geometry)
ORACLE_FIRE_RATIO = 3.0
ORACLE_FIRE_ABS = 0.003

# STRICT bands as FRACTIONS OF THE LEARNED REFERENCE headroom (the question: material fraction of learned 0.128)
STRICT_VIABLE_FRAC = 0.50            # STRICT_VIABLE: CF_ANCHOR recovers >= 50% of the learned anchor MRR
STRICT_PARTIAL_FRAC = 0.15          # MIDDLE floor: >= 15% of learned (else strict-dead / near-random)
SCRAMBLE_CEIL_FRAC = 0.25           # scramble controlled: (CF_SCRAMBLE - RANDOM) <= 25% of CF_ORACLE headroom
MIN_SIG_MRR = 0.002                 # significance floor: STRICT_VIABLE anchor margin must ALSO clear this abs mrr
CONTROL_LOSE_EPS = 0.005            # broken guard: a control beating CF_ORACLE by > this mrr = degenerate readout
MIN_HELDOUT = 20                    # min held-out QUERY edges for a valid discriminator
MIN_STRAT_Q = 8                     # min queries in a stratum to report its margin

# resolved absolute MRR targets from the LEARNED reference (pre-registered constants; NOT tuned on real data)
STRICT_VIABLE_TARGET = STRICT_VIABLE_FRAC * LEARNED_ANCHOR_REF   # 0.06411
STRICT_PARTIAL_TARGET = STRICT_PARTIAL_FRAC * LEARNED_ANCHOR_REF  # 0.01923

# ---- Held-out-entity split knobs (SAME as the learned cell -> bit-identical split at matched seeds) ----
HELDOUT_ENTITY_FRAC = 0.15
SUPPORT_FRAC = 0.5

# ---- Closed-form derivation knobs (pre-registered; calibrated on the synthetic planted arena, NOT real data) ----
CF_N_SWEEPS = 15        # closed-form ALS sweeps (alternating closed-form D + Jacobi X solve)
CF_N_JACOBI = 3         # inner Jacobi iterations per sweep of the X normal equations
CF_LAMBDA = 0.05        # anchor weight to the spectral init X0 (grounds isolated rows; keeps the solve well-posed)
CF_SVD_NITER = 6        # power iterations for the truncated randomized SVD (spectral init accuracy)

# ---- self-test planted thresholds on the PRIMARY metric (MRR); calibrated on the synthetic planted arena, NOT real
#      data. MEASURED on the planted grid (build_planted_transe_arena seed 7, k=12): CF_ORACLE~0.327, CF_ANCHOR~0.071,
#      (CF_ANCHOR-RANDOM)~0.058, (CF_ANCHOR-CF_SCRAMBLE)~0.023. Thresholds set with headroom below measured. ----
SELFTEST_ORACLE_MRR_MIN = 0.15
SELFTEST_ANCHOR_MRR_MIN = 0.04
SELFTEST_AC_BEATS_RANDOM_MRR = 0.025
SELFTEST_SCRAMBLE_MARGIN_MRR = 0.010
SELFTEST_MIN_HO = 8

SCORE_CHUNK = 256

# Config profiles. SELFTEST/FULL exercise the SAME split->partition->closed-form->compose->score->verdict path.
SELFTEST_CFG = dict(k=12, n_sweeps=CF_N_SWEEPS, n_jacobi=CF_N_JACOBI, lam=CF_LAMBDA, svd_niter=CF_SVD_NITER,
                    heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0, min_heldout=SELFTEST_MIN_HO)
# FULL: k=24 matches the learned reference capacity knob (apples-to-apples vs the learned 0.128 at k=24). Same split
# knobs + same seeds -> the held-out arena is bit-identical to the learned run so the closed-form MRR is directly
# comparable to the learned 0.128 on the SAME held-out query edges.
FULL_CFG = dict(k=24, n_sweeps=CF_N_SWEEPS, n_jacobi=CF_N_JACOBI, lam=CF_LAMBDA, svd_niter=CF_SVD_NITER,
                heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
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
# THE CLOSED-FORM COORD SOURCE (spectral init + closed-form ALS of the TransE score; ALL non-gradient).
# ---------------------------------------------------------------------------

def _spectral_X(ed, N, k, device, seed, svd_niter):
    """Stage 1: Laplacian-eigenmap X0 = top-(k+1) singular vectors of the symmetric-normalized adjacency Dinv A Dinv
    (train edges + self-loops), trivial sqrt-degree component dropped. torch.svd_lowrank (truncated randomized SVD;
    non-gradient, deterministic under a seeded RNG state). Returns (N,k) float32 scaled to O(1) rows."""
    h = ed[:, 0]
    t = ed[:, 2]
    rows = np.concatenate([h, t, np.arange(N)])
    cols = np.concatenate([t, h, np.arange(N)])          # undirected + self-loops (isolated nodes stay well-posed)
    idx = torch.from_numpy(np.stack([rows, cols])).long()
    vals = torch.ones(idx.shape[1], dtype=torch.float32)
    A = torch.sparse_coo_tensor(idx, vals, (N, N)).coalesce()
    deg = torch.sparse.sum(A, dim=1).to_dense()
    dinv = torch.rsqrt(torch.clamp(deg, min=1.0))
    ai = A.indices()
    av = A.values()
    nv = av * dinv[ai[0]] * dinv[ai[1]]                  # Dinv A Dinv (symmetric normalized)
    Ln = torch.sparse_coo_tensor(ai, nv, (N, N)).coalesce().to(device)
    _st = torch.random.get_rng_state()
    torch.manual_seed(seed * 7919 + 11)                  # determinism for the randomized SVD; restored below
    try:
        U, _S, _V = torch.svd_lowrank(Ln, min(k + 1, N - 1), svd_niter)   # positional q,niter = portable base call
    finally:
        torch.random.set_rng_state(_st)
    kk = min(k, U.shape[1] - 1)
    X0 = U[:, 1:1 + kk].contiguous()
    if kk < k:                                           # tiny-N guard: pad missing dims with zeros (self-test only)
        X0 = torch.cat([X0, torch.zeros(N, k - kk)], dim=1)
    return (X0 * float(np.sqrt(N))).to(device, torch.float32)


def closedform_als_coords(ed, N, n_rel, k, device, seed, n_sweeps=CF_N_SWEEPS, n_jacobi=CF_N_JACOBI,
                          lam=CF_LAMBDA, svd_niter=CF_SVD_NITER):
    """Closed-form coord source: spectral init + n_sweeps closed-form ALS of the TransE score. NO gradient descent.

    ed: (E,3) int64 [h,r,t] edge set the coords are derived from (train only for the inductive arms; train+held-out
    for the transductive ORACLE). Returns (X [N,k] float32, D [n_rel,k] float32) on device.

    Per sweep: (a) D_r = mean_{(h,r,t)}(X_t - X_h)  [exact LS minimizer over D given X]; (b) n_jacobi Jacobi steps of
    the normal equations of min_X sum_e ||X_h + D_r - X_t||^2 + lam||X - X0||^2 (lam anchors to the spectral init)."""
    X0 = _spectral_X(ed, N, k, device, seed, svd_niter)
    X = X0.clone()
    h = torch.from_numpy(ed[:, 0]).long().to(device)
    r = torch.from_numpy(ed[:, 1]).long().to(device)
    t = torch.from_numpy(ed[:, 2]).long().to(device)
    ones_e = torch.ones(h.shape[0], device=device, dtype=X.dtype)
    deg = torch.zeros(N, device=device, dtype=X.dtype)
    deg.index_add_(0, h, ones_e)
    deg.index_add_(0, t, ones_e)
    denom = (deg + lam).unsqueeze(1)

    def _solve_D(Xc):
        Dsum = torch.zeros(n_rel, k, device=device, dtype=X.dtype)
        Dsum.index_add_(0, r, Xc[t] - Xc[h])
        cnt = torch.zeros(n_rel, device=device, dtype=X.dtype)
        cnt.index_add_(0, r, ones_e)
        return Dsum / torch.clamp(cnt, min=1.0).unsqueeze(1)

    for _sweep in range(n_sweeps):
        D = _solve_D(X)
        for _j in range(n_jacobi):
            acc = lam * X0
            acc = acc.index_add(0, h, X[t] - D[r])       # head rows want X_h = X_t - D_r
            acc = acc.index_add(0, t, X[h] + D[r])       # tail rows want X_t = X_h + D_r
            X = acc / denom
    D = _solve_D(X)
    return X.to(device, torch.float32), D.to(device, torch.float32)


# ---------------------------------------------------------------------------
# Fit the arms (closed-form; NO SGD) + build E_derived + score PAIRED on the SAME held-out QUERY edges.
# ---------------------------------------------------------------------------

def fit_and_score_closedform(train_int, support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                             rel_tail_freq, all_true, exercised=None):
    """Derive closed-form X/D (train + transductive-oracle), build the anchor bundle + scramble, score all arms."""
    if exercised is not None:
        exercised.add("closedform_als_coords")
        exercised.add("build_anchor_compose_codes")
        exercised.add("additive_direct_scores")
    k = cfg["k"]
    n_sweeps = cfg["n_sweeps"]
    n_jacobi = cfg["n_jacobi"]
    lam = cfg["lam"]
    svd_niter = cfg["svd_niter"]

    # closed-form X/D from TRAIN only (frozen scaffold for the inductive arms)
    Xtr, Dtr = closedform_als_coords(train_int, N, n_rel, k, device, seed, n_sweeps, n_jacobi, lam, svd_niter)
    # closed-form X/D with held-out FOLDED IN (transductive ceiling / positive control)
    ed_oracle = np.concatenate([train_int, hold_all], axis=0) if hold_all.shape[0] else train_int
    Xor, Dor = closedform_als_coords(ed_oracle, N, n_rel, k, device, seed, n_sweeps, n_jacobi, lam, svd_niter)

    # RANDOM codes (random X + random D + same additive readout) = the null
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, k, generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, k, generator=gR) * 0.1).to(device)

    # ANCHOR + SCRAMBLE codes (zero extra work; reuse the VERBATIM bundle op on the frozen closed-form scaffold)
    Xac, support_deg = build_anchor_compose_codes(Xtr, Dtr, support_int, device)
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)
    Xscr, _ = build_anchor_compose_codes(Xtr, Dtr, support_int, device, rel_perm=rel_perm)

    arm_metric, arm_sig, arm_scores = {}, {}, {}
    for name, sc in [
        (CF_ANCHOR, additive_direct_scores(Xac, Dtr, query_int, device, chunk=SCORE_CHUNK)),
        (CF_MEM, additive_direct_scores(Xtr, Dtr, query_int, device, chunk=SCORE_CHUNK)),
        (CF_SCR, additive_direct_scores(Xscr, Dtr, query_int, device, chunk=SCORE_CHUNK)),
        (CF_ORACLE, additive_direct_scores(Xor, Dor, query_int, device, chunk=SCORE_CHUNK)),
        (RANDOM, additive_direct_scores(Xr, Dr, query_int, device, chunk=SCORE_CHUNK)),
    ]:
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
        arm_scores[name] = sc
    pop_m, pop_rank_vec = pop_hits(rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    del Xtr, Dtr, Xor, Dor, Xr, Dr, Xac, Xscr
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores, support_deg=support_deg)


# ---------------------------------------------------------------------------
# Weak-point localization: by anchor-support-degree bin + fair low/mid global-degree stratum.
# ---------------------------------------------------------------------------

def _hits_subset(scores, query_int, all_true, mask, k=PRIMARY_K):
    idx = np.where(mask)[0]
    if idx.size < 1:
        return dict(hits=float("nan"), mrr=float("nan"), n=0)
    sub = filtered_hits_from_scores(scores[idx], query_int[idx], all_true, ks=(k,))
    return dict(hits=round(sub["hits@%d" % k], 5), mrr=round(sub["mrr"], 6), n=int(idx.size))


def _pop_subset(rel_tail_freq, query_int, all_true, n_ent, mask, k=PRIMARY_K):
    idx = np.where(mask)[0]
    if idx.size < 1:
        return dict(hits=float("nan"), mrr=float("nan"), n=0)
    sub, _ = pop_hits(rel_tail_freq, query_int[idx], all_true, n_ent, ks=(k,))
    return dict(hits=round(sub["hits@%d" % k], 5), mrr=round(sub["mrr"], 6), n=int(idx.size))


SUPPORT_BINS = [(0, 0, "cold"), (1, 1, "d1"), (2, 3, "d2_3"), (4, 7, "d4_7"), (8, 10 ** 9, "d8plus")]


def localize_weak_points(arm_scores, query_int, all_true, support_deg, node_degree, rel_tail_freq, N):
    nq = query_int.shape[0]
    gold = query_int[:, 2]
    q_support = np.array([support_deg[int(g)] for g in gold], dtype=np.int64)
    strat, tert = stratify_by_tail_degree(query_int, node_degree)
    report_arms = [CF_ANCHOR, CF_MEM, RANDOM, CF_ORACLE]

    def _by_mask(mask):
        out = {a: _hits_subset(arm_scores[a], query_int, all_true, mask) for a in report_arms}
        out[POP] = _pop_subset(rel_tail_freq, query_int, all_true, N, mask)
        return out

    by_support = {}
    for lo, hi, name in SUPPORT_BINS:
        by_support[name] = _by_mask((q_support >= lo) & (q_support <= hi))
    fair_lowmid = _by_mask((strat == 0) | (strat == 1))
    return dict(by_support_degree=by_support, fair_low_mid=fair_lowmid,
                global_degree_tertile_bounds=tert,
                support_deg_hist={name: int(((q_support >= lo) & (q_support <= hi)).sum())
                                  for lo, hi, name in SUPPORT_BINS})


# ---------------------------------------------------------------------------
# One corpus run.
# ---------------------------------------------------------------------------

def run_corpus(pool_lbl, cfg, device, seed, corpus_name, localize=True, exercised=None):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i)
    n_rel = len(rel2i)
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
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    fs = fit_and_score_closedform(train_int, support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                                  gd.rel_tail_freq, all_true, exercised=exercised)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 5) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs=fs["arm_sig"],
    )
    if localize:
        result["localization"] = localize_weak_points(
            fs["arm_scores"], query_int, all_true, fs["support_deg"], gd.node_degree, gd.rel_tail_freq, N)
    return result


# ---------------------------------------------------------------------------
# Aggregate + verdict (per_seed list length 1..3).
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _m(ps, arm):
    return ps["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def _h10(ps, arm):
    return ps["arm_hits"][arm].get(PRIMARY_METRIC, float("nan"))


def _fair_lowmid_mrr(ps, arm):
    loc = ps.get("localization", {})
    cell = loc.get("fair_low_mid", {}).get(arm, {})
    if cell.get("n", 0) >= MIN_STRAT_Q:
        return cell.get("mrr", float("nan"))
    return float("nan")


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def aggregate_and_verdict(per_seed):
    def agg_m(arm):
        return _nm([_m(ps, arm) for ps in per_seed])

    def agg_h10(arm):
        return _nm([_h10(ps, arm) for ps in per_seed])

    def agg_fair(arm):
        return _nm([_fair_lowmid_mrr(ps, arm) for ps in per_seed])

    m = {a: agg_m(a) for a in ALL_ARMS}
    h10 = {a: agg_h10(a) for a in ALL_ARMS}
    mf = {a: agg_fair(a) for a in [CF_ANCHOR, CF_MEM, RANDOM, CF_ORACLE, POP]}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))

    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")

    d_anchor = _sub(m[CF_ANCHOR], m[RANDOM])                     # closed-form anchor headroom over the null
    d_scramble = _sub(m[CF_SCR], m[RANDOM])
    oracle_headroom = _sub(m[CF_ORACLE], m[RANDOM])             # H_cf = closed-form transductive ceiling headroom
    oracle_ratio = _ratio(m[CF_ORACLE], m[RANDOM])
    frac_of_learned = _ratio(m[CF_ANCHOR], LEARNED_ANCHOR_REF)  # the headline: fraction of the learned 0.128
    fair_anchor_margin = _sub(mf[CF_ANCHOR], mf[RANDOM])

    enough_heldout = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(oracle_headroom == oracle_headroom and oracle_headroom >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)

    scramble_target = (SCRAMBLE_CEIL_FRAC * oracle_headroom if oracle_headroom == oracle_headroom else float("nan"))
    scramble_controlled = bool(d_scramble == d_scramble and scramble_target == scramble_target
                               and d_scramble <= scramble_target)

    # BROKEN guard (F.4-correct): a control (RANDOM / CF_SCRAMBLE) beating the CF_ORACLE transductive CEILING by more
    # than eps = degenerate readout. Baseline = CF_ORACLE (above the floor when it fires), NOT POP (structurally ~0 on
    # this held-out arena). guard_baseline_valid is declared at self-test against the RANDOM floor.
    broken = bool((m[RANDOM] == m[RANDOM] and m[CF_ORACLE] == m[CF_ORACLE] and (m[RANDOM] - m[CF_ORACLE]) > CONTROL_LOSE_EPS)
                  or (m[CF_SCR] == m[CF_SCR] and m[CF_ORACLE] == m[CF_ORACLE] and (m[CF_SCR] - m[CF_ORACLE]) > CONTROL_LOSE_EPS))
    fair_holds = bool(fair_anchor_margin == fair_anchor_margin and fair_anchor_margin > 0.0)

    strict_viable = bool(
        m[CF_ANCHOR] == m[CF_ANCHOR] and m[CF_ANCHOR] >= STRICT_VIABLE_TARGET
        and d_anchor == d_anchor and d_anchor >= MIN_SIG_MRR
        and oracle_fires and scramble_controlled and not broken and fair_holds)
    strict_dead = bool(m[CF_ANCHOR] == m[CF_ANCHOR] and m[CF_ANCHOR] < STRICT_PARTIAL_TARGET)
    middle = bool(m[CF_ANCHOR] == m[CF_ANCHOR] and not strict_viable and not strict_dead)

    oracle_fire_by_metric = {}
    for mk in metric_keys:
        ov = spectrum[CF_ORACLE][mk]
        rv = spectrum[RANDOM][mk]
        hh = _sub(ov, rv)
        rr = _ratio(ov, rv)
        oracle_fire_by_metric[mk] = dict(
            oracle=(round(ov, 6) if ov == ov else None), random=(round(rv, 6) if rv == rv else None),
            headroom=(round(hh, 6) if hh == hh else None),
            ratio=(round(rr, 2) if (rr == rr and rr != float("inf")) else None),
            fires_ratio=bool(rr == rr and rr >= ORACLE_FIRE_RATIO and hh == hh and hh > 0))

    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif broken:
        verdict = "BROKEN_TEST_CONTROL_BEATS_CLOSEDFORM_ORACLE"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_CLOSEDFORM_ORACLE_UNDERFIT"       # closed-form geometry insufficient even transductively
    elif strict_viable:
        verdict = "STRICT_VIABLE_CLOSEDFORM_COORD_SOURCE"
    elif strict_dead:
        verdict = "STRICT_DEAD_CLOSEDFORM_NEAR_RANDOM"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_CLOSEDFORM_TRANSFER"

    verdict_msg = (
        "%s || HELD-OUT MRR [nq=%d]: CF_ANCHOR=%s (=%s x learned_ref %.5f) | CF_MEMORIZE=%s CF_SCRAMBLE=%s | "
        "RANDOM=%s | CF_ORACLE=%s POP=%s || CEILING H(cf_oracle-random)=%s ratio=%sx (fires>=%.1fx&>=%.3f=%s) | "
        "anchor_margin_vs_random=%s (>=MIN_SIG %.3f) | STRICT_VIABLE>=%s (=%.2f*learned) STRICT_DEAD<%s "
        "(=%.2f*learned) | scramble_margin=%s (<=%s=%.2f*H) ctrl=%s | fair_lowmid_margin=%s (>0)=%s | broken=%s | "
        "seeds=%d frac=%.2f support_frac=%.2f"
        % (
            verdict, n_query, _fmt(m[CF_ANCHOR]),
            (_fmt(frac_of_learned) if frac_of_learned != float("inf") else "inf"), LEARNED_ANCHOR_REF,
            _fmt(m[CF_MEM]), _fmt(m[CF_SCR]), _fmt(m[RANDOM]), _fmt(m[CF_ORACLE]), _fmt(m[POP]),
            _fmt(oracle_headroom), (_fmt(oracle_ratio) if oracle_ratio != float("inf") else "inf"),
            ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS, oracle_fires, _fmt(d_anchor), MIN_SIG_MRR,
            _fmt(STRICT_VIABLE_TARGET), STRICT_VIABLE_FRAC, _fmt(STRICT_PARTIAL_TARGET), STRICT_PARTIAL_FRAC,
            _fmt(d_scramble), _fmt(scramble_target), SCRAMBLE_CEIL_FRAC, scramble_controlled,
            _fmt(fair_anchor_margin), fair_holds, broken,
            len(per_seed), _nm([ps["heldout_entity_frac"] for ps in per_seed]),
            _nm([ps["support_frac"] for ps in per_seed])))

    def _rnd(x, nd=6):
        return round(x, nd) if x == x else None

    gates = dict(
        verdict=verdict, ceil_metric=CEIL_METRIC,
        learned_anchor_ref=LEARNED_ANCHOR_REF, learned_oracle_ref=LEARNED_ORACLE_REF,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        heldout_mrr={a: _rnd(m[a]) for a in ALL_ARMS},
        heldout_hits_at_10={a: _rnd(h10[a], 5) for a in ALL_ARMS},
        fair_lowmid_mrr={a: _rnd(mf[a]) for a in [CF_ANCHOR, CF_MEM, RANDOM, CF_ORACLE, POP]},
        primary_k=PRIMARY_K,
        closedform_anchor_mrr=_rnd(m[CF_ANCHOR]),
        closedform_frac_of_learned=(round(frac_of_learned, 4) if (frac_of_learned == frac_of_learned and frac_of_learned != float("inf")) else None),
        anchor_margin_vs_random=_rnd(d_anchor),
        fair_lowmid_anchor_margin=_rnd(fair_anchor_margin),
        scramble_margin_vs_random=_rnd(d_scramble),
        closedform_oracle_headroom=_rnd(oracle_headroom),
        closedform_oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        oracle_fire_by_metric=oracle_fire_by_metric,
        resolved_thresholds=dict(strict_viable=_rnd(STRICT_VIABLE_TARGET), strict_partial=_rnd(STRICT_PARTIAL_TARGET),
                                 scramble_ceiling=_rnd(scramble_target), min_sig_mrr=MIN_SIG_MRR),
        n_query_scored=n_query,
        bands=dict(CEIL_METRIC=CEIL_METRIC, ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS,
                   STRICT_VIABLE_FRAC=STRICT_VIABLE_FRAC, STRICT_PARTIAL_FRAC=STRICT_PARTIAL_FRAC,
                   SCRAMBLE_CEIL_FRAC=SCRAMBLE_CEIL_FRAC, MIN_SIG_MRR=MIN_SIG_MRR, MIN_HELDOUT=MIN_HELDOUT,
                   HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC, SUPPORT_FRAC=SUPPORT_FRAC,
                   CF_N_SWEEPS=CF_N_SWEEPS, CF_N_JACOBI=CF_N_JACOBI, CF_LAMBDA=CF_LAMBDA),
        enough_heldout=enough_heldout, oracle_fires=oracle_fires, scramble_controlled=scramble_controlled,
        broken=broken, fair_holds=fair_holds, strict_viable=strict_viable, strict_dead=strict_dead, middle=middle,
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test. Planted DENSE additive-consistent grid (TransE-consistent, relations NECESSARY). Closed-form
# X/D (spectral+ALS) recovers held-out tails via the anchor bundle >> RANDOM; scramble fails (relation signal);
# ORACLE (held-out folded in) recovers and fires. Proves (a) split->closed-form->compose->score->verdict runs on the
# REAL objects, (b) the closed-form viable bar is achievable-in-principle, (c) RELATION operators carry the signal,
# (d) arms differ. Determinism-pinned to single-thread CPU.
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        return _mechanism_selftest_body(device)
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body(device):
    exercised = set()
    pool = build_planted_transe_arena(7, n_ent=300, n_rel=6, k_lat=8, deg=3)
    cfg = dict(SELFTEST_CFG)
    res = run_corpus(pool, cfg, device, 7, "PLANTED_TRANSE_HELDOUT_ENTITY", localize=True, exercised=exercised)
    out = dict(n_grid_entities=res.get("N"), n_heldout_entities=res.get("n_heldout_entities"),
               n_support=res.get("n_support"), n_query=res.get("n_query_scored"), n_cold=res.get("n_cold"))
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted grid produced too few held-out-entity queries (%s)" % res.get("n_query_scored")
        return False, out

    ah = res["arm_hits"]
    m = {a: ah[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    h10 = {a: ah[a].get(PRIMARY_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(res["arm_sigs"].values()))
    anchor_margin = m[CF_ANCHOR] - m[RANDOM]
    scramble_margin = m[CF_ANCHOR] - m[CF_SCR]
    oracle_margin = m[CF_ORACLE] - m[RANDOM]
    oracle_ratio = _ratio(m[CF_ORACLE], m[RANDOM])

    oracle_recovers = bool(m[CF_ORACLE] == m[CF_ORACLE] and m[CF_ORACLE] >= SELFTEST_ORACLE_MRR_MIN)
    oracle_fires = bool(oracle_margin == oracle_margin and oracle_margin >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    anchor_recovers = bool(m[CF_ANCHOR] == m[CF_ANCHOR] and m[CF_ANCHOR] >= SELFTEST_ANCHOR_MRR_MIN)
    anchor_beats_random = bool(anchor_margin == anchor_margin and anchor_margin >= SELFTEST_AC_BEATS_RANDOM_MRR)
    scramble_fails = bool(scramble_margin == scramble_margin and scramble_margin >= SELFTEST_SCRAMBLE_MARGIN_MRR)
    pop_at_floor = bool(m[POP] == m[POP] and m[POP] <= max(m[RANDOM], 0.02) + CONTROL_LOSE_EPS)
    arms_differ = bool(n_sigs >= 5)

    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    oracle_fire_by_metric = {}
    for mk in metric_keys:
        ov = ah[CF_ORACLE].get(mk, float("nan"))
        rv = ah[RANDOM].get(mk, float("nan"))
        hh = (ov - rv) if (ov == ov and rv == rv) else float("nan")
        rr = _ratio(ov, rv)
        oracle_fire_by_metric[mk] = dict(
            oracle=(round(ov, 5) if ov == ov else None), random=(round(rv, 5) if rv == rv else None),
            headroom=(round(hh, 5) if hh == hh else None),
            fires_ratio=bool(rr == rr and rr >= ORACLE_FIRE_RATIO and hh == hh and hh > 0))

    # VACUOUS-SMOKE guard: the RANDOM null must NOT reach CLOSEDFORM_ANCHOR on the planted held-out arena.
    random_reached_anchor = bool(anchor_margin <= SELFTEST_AC_BEATS_RANDOM_MRR)
    assert_discriminator_fires(random_reached_anchor, control_name=RANDOM,
                               headline_name="closedform_anchor_beats_random_heldout", run_mode="self_test",
                               extra="RANDOM reached CLOSEDFORM_ANCHOR on the planted held-out-entity arena -> arena "
                                     "not answerable by closed-form / metric frozen")

    st_verdict, st_msg, st_gates = aggregate_and_verdict([res])

    # F.1-F.4 ENFORCE + the original 4 checks. Bind the REAL callables the FULL uses against their LIVE signatures.
    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(oracle_recovers and oracle_fires),
         "control_name": "CLOSEDFORM_ORACLE", "headline_name": "closedform_oracle_beats_random_heldout_mrr",
         "extra": "planted grid: closed-form ORACLE (held-out folded in) recovers held-out tails and clears RANDOM by "
                  "the ceiling-aware ratio+abs fire gate -> the closed-form viable bar is achievable when the geometry "
                  "can represent the entity"},
        {"kind": "metric_moves", "metric_name": "closedform_heldout_mrr",
         "values": [m[RANDOM], m[CF_MEM], m[CF_ANCHOR], m[CF_ORACLE]],
         "extra": "MRR RANDOM=%.3f MEMORIZE=%.3f ANCHOR=%.3f ORACLE=%.3f: the closed-form readout responds to "
                  "composed/transductive codes" % (m[RANDOM], m[CF_MEM], m[CF_ANCHOR], m[CF_ORACLE])},
        {"kind": "negative_control_margin", "control_scores": [m[RANDOM], m[CF_SCR]],
         "headline_threshold": m[CF_ANCHOR], "higher_is_pass": True, "margin": SELFTEST_SCRAMBLE_MARGIN_MRR,
         "n_repeats_min": 2, "control_name": "RANDOM_and_CF_SCRAMBLE_below_anchor_mrr",
         "extra": "RANDOM + relation-scrambled closed-form ANCHOR must sit below CLOSEDFORM_ANCHOR by the MRR margin "
                  "-> the RELATION operators (not anchor identity/proximity) carry the signal"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires", "scramble_controlled", "broken_test_guard",
                                    "enough_heldout", "strict_band_gate"],
         "exercised_gates": ["arms_differ", "oracle_fires", "scramble_controlled", "broken_test_guard",
                             "enough_heldout", "strict_band_gate"],
         "extra": "aggregate_and_verdict verdict=%s at self-test scale" % st_verdict},
        # F.1: the self-test EXERCISED the REAL closed-form objects the FULL uses (no synthetic-only branch).
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["closedform_als_coords", "build_anchor_compose_codes",
                                        "additive_direct_scores", "fit_and_score_closedform"],
         "exercised_entrypoints": sorted(exercised | {"fit_and_score_closedform"}),
         "extra": "self-test ran run_corpus -> fit_and_score_closedform -> closed-form derivation + verbatim "
                  "compose/score on the REAL callables at N=300"},
        # F.2/F.3: every closed-form / reused call binds against its LIVE signature with base/portable kwargs.
        {"kind": "substrate_signature", "callable_obj": closedform_als_coords, "callable_name": "closedform_als_coords",
         "kwargs": {"ed": None, "N": 1, "n_rel": 1, "k": 4, "device": device, "seed": 7}},
        {"kind": "substrate_signature", "callable_obj": build_anchor_compose_codes,
         "callable_name": "build_anchor_compose_codes", "args_count": 4},
        {"kind": "substrate_signature", "callable_obj": additive_direct_scores,
         "callable_name": "additive_direct_scores", "args_count": 4},
        {"kind": "substrate_signature", "callable_obj": torch.svd_lowrank, "callable_name": "torch.svd_lowrank",
         "args_count": 3},   # positional (A, q, niter): portable base call, no version-specific optional kwargs
        # F.4: the broken-test guard fires against CF_ORACLE (above the floor), NOT POP (structurally ~0). Validate
        # the guard baseline (CF_ORACLE) is above the RANDOM floor so it cannot mis-fire on this arena's zeros.
        {"kind": "guard_baseline_valid", "baseline_score": m[CF_ORACLE], "floor_score": m[RANDOM],
         "guard_name": "BROKEN_TEST_CONTROL_BEATS_CLOSEDFORM_ORACLE", "baseline_name": "CF_ORACLE",
         "floor_name": "RANDOM", "eps": 0.02},
    ], run_mode="self_test")

    out.update(
        heldout_mrr={a: round(m[a], 5) for a in ALL_ARMS},
        heldout_hits_at_10={a: round(h10[a], 5) for a in ALL_ARMS},
        heldout_metric_spectrum={a: {mk: round(ah[a].get(mk, float("nan")), 5) for mk in metric_keys}
                                 for a in ALL_ARMS},
        oracle_fire_by_metric=oracle_fire_by_metric,
        n_distinct_sigs=n_sigs, anchor_margin=round(anchor_margin, 5), scramble_margin=round(scramble_margin, 5),
        oracle_margin=round(oracle_margin, 5),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        oracle_recovers=oracle_recovers, oracle_fires=oracle_fires, anchor_recovers=anchor_recovers,
        anchor_beats_random=anchor_beats_random, scramble_fails=scramble_fails, pop_at_floor=pop_at_floor,
        arms_differ=arms_differ, selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok),
        exercised_entrypoints=sorted(exercised | {"fit_and_score_closedform"}),
        support_deg_hist=res.get("localization", {}).get("support_deg_hist"),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest",
                                     "real_code_path_F1", "substrate_signature_F2_F3", "guard_baseline_valid_F4"],
    )
    ok = bool(oracle_recovers and oracle_fires and anchor_recovers and anchor_beats_random
              and scramble_fails and pop_at_floor and arms_differ)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (arg_device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue")
    if force_cpu:
        return torch.device("cpu")
    want_cuda = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


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

    _log("device=%s cuda=%s run_mode=%s seeds=%s k=%s sweeps=%s jacobi=%s lam=%s" %
         (device, torch.cuda.is_available(), run_mode, seeds, cfg["k"], cfg["n_sweeps"], cfg["n_jacobi"], cfg["lam"]))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s anchor_margin=%s scramble_margin=%s oracle_fires=%s vp_ok=%s heldout_mrr=%s" %
         (st_ok, st_res.get("anchor_margin"), st_res.get("scramble_margin"), st_res.get("oracle_fires"),
          st_res.get("validity_preflight_ok"), st_res.get("heldout_mrr")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (closed-form ANCHOR did not recover/beat-random, or scramble did "
                        "not fail, or ORACLE did not fire, or POP not at floor, or arms not distinct): %s"
                        % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS closed-form coord-source inductive probe: closed-form (spectral+ALS) X/D "
                        "recovers planted held-out tails via the anchor bundle and clears RANDOM; relation-scramble "
                        "fails; ORACLE fires; POP at floor; 7 validity-preflight checks declared (F.1-F.4 enforce)",
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
            res = run_corpus(pool, cfg, device, seed, "CSKG_CORE_HELDOUT_ENTITY", localize=True)
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out-entity query edges too few (%d < %d)" %
                                   (res.get("n_query_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            ah = res["arm_hits"]
            _log("seed=%d nq=%d n_sup=%d n_cold=%d | mrr CF_ANCHOR=%s CF_MEM=%s CF_SCR=%s CF_ORACLE=%s RANDOM=%s "
                 "POP=%s (%.1fs)" %
                 (seed, res["n_query_scored"], res["n_support"], res["n_cold"],
                  _fmt(ah[CF_ANCHOR][CEIL_METRIC]), _fmt(ah[CF_MEM][CEIL_METRIC]), _fmt(ah[CF_SCR][CEIL_METRIC]),
                  _fmt(ah[CF_ORACLE][CEIL_METRIC]), _fmt(ah[RANDOM][CEIL_METRIC]), _fmt(ah[POP][CEIL_METRIC]),
                  time.time() - ts))
            _hb("cskg", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
        finally:
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
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
