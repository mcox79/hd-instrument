"""SPECTRAL-INIT WARM-START: does a Laplacian graph-eigenmap warm-start of the additive entity table raise the
held-out-ENTITY MRR of ANCHOR_COMPOSE over the confirmed random(gaussian)-init baseline, bit-identical otherwise?

THRUST A ("shore up what's working") cheap single-swap lever (recipe drill rank-1). The confirmed inductive map
`AdditiveKGMap` (VET HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE, held-out-entity MRR 0.12821) fits its entity coordinate
table X with a plain gaussian init (torch.randn(N,k)*0.1). The KGE literature reports structural/spectral warm-start
init as the largest, cheapest, most-composable single-swap lever (CITED@notes research_drill_training_recipe_
improvement_theories_2026-07-13: informed/schema-warm-started TransH init +9-46% task perf, 2.2-2.7x faster
convergence; deflated P=0.40, expect +3-15% RELATIVE MRR). This cell tests it on OUR inductive arena, holding the
scoring function + loss (self-adversarial CE + N3 + reciprocal) + all hyperparameters + the held-out split BIT-
IDENTICAL, changing ONLY the init of X.

MECHANISM (glass-box, closed-form, inspectable). Compute a k-dim spectral embedding of the TRAIN-edge graph:
A_norm = D^-1/2 A D^-1/2 (symmetric normalized adjacency over the N entities; edge (h,t) structural, relation-
agnostic, undirected). Its top-(k+1) eigenvectors are the smoothest graph-Laplacian eigenmaps (eigvecs of
L=I-A_norm at the SMALLEST Laplacian eigenvalues); drop the trivial constant top eigenvector, take the next k, and
RESCALE each column to the gaussian init's per-dim std (0.1) so the comparison isolates STRUCTURE, not scale. This
warm-starts ONLY the SEEN anchor rows (held-out entities are isolated in the train graph -> their rows stay gaussian,
and are overwritten by the zero-training ANCHOR_COMPOSE bundle anyway). The fit then proceeds identically; the
`X_init` kwarg on fit_kge_anchor1 (default None == bit-identical gaussian) injects the warm-start after the gaussian
X/D draw so D's init + RNG order are unchanged and only X's start point differs.

HEADLINE = the held-out-entity MRR of the ZERO-TRAINING ANCHOR_COMPOSE bundle built over the warm-started scaffold
(X_spec, D_spec) vs the gaussian scaffold (X_gauss, D_gauss). ARMS (all PAIRED on the SAME held-out QUERY edges):
  ANCHOR_GAUSS         : ANCHOR_COMPOSE over the gaussian-init additive fit. CONTROL -- reproduces the confirmed
                         0.12821 (X_init=None == bit-identical to the VET-confirmed run at the same seeds/config).
  ANCHOR_SPEC          : ANCHOR_COMPOSE over the SPECTRAL-warm-started additive fit. THE TEST arm.
  ANCHOR_SPEC_SCRAMBLE : ANCHOR_COMPOSE over a SCRAMBLED-spectral-init fit (same eigenvector column norms, row
                         assignment PERMUTED across seen entities -> destroys structure, preserves scale). MUST-FAIL
                         isolation: if the scrambled arm gets the SAME lift, the lift is a scale/norm artifact, NOT
                         structural transfer. (seed-7 only; controls do not need the full seed fan-out.)
  ORACLE_GAUSS         : gaussian additive fit with the held-out edges FOLDED IN (codes LEARNED) -> positive control
                         / arena-answerable ceiling (must fire: ORACLE_mrr >= 3x RANDOM_mrr AND headroom >= 0.003).
                         (seed-7 only.)
  RANDOM_CODES         : random X + random D + additive readout -> the null / arena floor (no fit).

CEILING-AWARE BANDS (picked BEFORE the run; primary metric = filtered MRR, degree-unbiased, rank-vs-ALL). CRITICAL
info-ceiling: the confirmed ANCHOR_COMPOSE (0.12821) is already at 93.7% of the transductive ORACLE ceiling
(0.13729) -- the residual headroom to the arena-answerable ceiling is only ~0.009 MRR. So a raw +15% relative lift
(-> 0.147) would EXCEED the transductive oracle and is IMPLAUSIBLE for a zero-training composed code; the plausible
lift is bounded near the oracle. The HARD-PASS bar is set ceiling-aware:
  LIFT           = ANCHOR_SPEC_mrr - ANCHOR_GAUSS_mrr   (headline, per-seed then aggregated)
  SCRAMBLE_LIFT  = ANCHOR_SPEC_SCRAMBLE_mrr - ANCHOR_GAUSS_mrr
  HARD-PASS (WARMSTART_LIFTS): LIFT >= LIFT_MIN (0.005; recovers >55% of the ~0.009 residual oracle headroom) AND
                 (LIFT - SCRAMBLE_LIFT) >= STRUCT_MARGIN (0.003; structure, not scale) AND ORACLE fires AND the
                 gaussian control reproduces 0.12821 within REPRO_TOL.
  SCALE-ARTIFACT (MIDDLE): LIFT >= LIFT_MIN but (LIFT - SCRAMBLE_LIFT) < STRUCT_MARGIN -> lift is a scale/norm
                 artifact (scrambled-spectral matched it), NOT structural transfer. Do not pursue scale-matched inits.
  HARD-FAIL (NO_LIFT): LIFT <= LIFT_NOISE (0.002) with ORACLE firing -> genuine, informative negative: the degree-
                 invariant MEAN compose op downstream of X,D WASHES OUT the structural init signal -> localizes the
                 wall to the COMPOSE stage (not the FIT stage) -- a useful finding for compose-op design.
  MIDDLE (PARTIAL_LIFT): LIFT_NOISE < LIFT < LIFT_MIN.
  Gated INCONCLUSIVE if ORACLE does not fire (arena not answerable) OR the gaussian control fails to reproduce
  0.12821 within REPRO_TOL (fit/env drift -> the paired comparison is invalid).

## Compute architecture
class (c) MIXED: split + support/query partition = sequential-CPU graph ops; the additive fits = minibatch SGD
(batched, neg-chunked) on GPU; the spectral embedding = one sparse scipy.sparse.linalg.eigsh (Lanczos, top-k of the
normalized adjacency; NO dense N-by-N matrix, NO LU) computed ONCE per seed and shared by the spectral + scrambled
arms; E_derived = a single vectorized index_add_ bundle (zero training). Storage SHARDED. device=auto (cuda on the
GPU host). FULL = 8 SGD refits total (ANCHOR_GAUSS + ANCHOR_SPEC over 3 seeds = 6; ANCHOR_SPEC_SCRAMBLE + ORACLE_GAUSS
seed-7 only = 2) at k=24/epochs=500/N~25.7k; MEASURED per-fit ~1342s from the confirmed arena FULL (12073s/9-fit-
equiv) -> ~10.7k s base. fit-checkpointed (ckpt_every) so an outage resumes each arm. GPU-routed because it is 8 SGD
refits (the SGD refit is the reason, per the drill). No local FULL/smoke (USER 2026-07-11) -- LOCAL gate = --self-test
on a tiny planted CPU grid; the FULL runs on overnight_queue (GPU).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor + Gate F.1-F.4 ENFORCE):
# - arms_differ_verified at self-test (META_RULE_AF): >=4 distinct arm score signatures per seed.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - info-ceiling: ANCHOR at 93.7% of ORACLE; residual headroom ~0.009 -> LIFT_MIN=0.005 is ceiling-aware and
#   ACHIEVABLE (< residual headroom); a +15% raw literature number would be UNREACHABLE (> transductive oracle).
# - baseline_in_band: ORACLE must fire (>=3x RANDOM_mrr AND headroom>=0.003); gaussian control reproduces 0.12821.
# - discriminator survives scale: the gaussian control is BIT-IDENTICAL to the VET-confirmed FULL at the same
#   seeds/config (X_init=None) -> reproduces 0.12821 by construction; the LIFT is measured against that fixed anchor.
#   The self-test fires the init-changes-the-fit + spectral-has-structure discriminators deterministically.
# - HP strictly above floor: LIFT_MIN=0.005 clears LIFT_NOISE=0.002 by 2.5x + STRUCT_MARGIN gate.
# - HP_SCOPE: the WARMSTART_LIFTS gates apply to ANCHOR_SPEC (vs ANCHOR_GAUSS) only. ORACLE_GAUSS = positive
#   control (must fire); ANCHOR_SPEC_SCRAMBLE = must-fail scale-isolation control; ANCHOR_GAUSS = the fixed
#   reproduce-0.12821 baseline; RANDOM_CODES = the null floor.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce its arms + >=4 sigs.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- LIFT_MIN/STRUCT_MARGIN/REPRO_TOL/ORACLE_FIRE_* pre-
#   registered, NOT tuned on real data. The gaussian anchor (0.12821) is CITED from the confirmed metrics on disk.
# - all numbers tagged MEASURED@/CITED@/THEORETICAL@ in the prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints).
# - Gate F.1 real_code_path: self-test constructs the REAL fit_kge_anchor1 (both gaussian and X_init) +
#   build_spectral_init + build_anchor_compose_codes at N~300.
# - Gate F.2/F.3 substrate_signature: fit_kge_anchor1(..., X_init=..., init_tag=...) bound against the live
#   signature; X_init/init_tag ship WITH the cell (Pattern-6 auto-SCP of _kge_anchor1_fit) so no remote drift.
# - Gate F.4 guard_baseline_valid: the RANDOM-beats-ANCHOR_GAUSS broken-guard validated NOT at the arena floor.

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

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import Graph, build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, PRIMARY_K,
)
from experiments._course_c_rotate_core_v1 import additive_direct_scores  # noqa: E402
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._fit_checkpoint import FitCheckpoint, cleanup_seed_checkpoints  # noqa: E402
# Reuse the CONFIRMED arena's split + compose helpers VERBATIM (guarantees the gaussian arm is bit-identical to the
# VET-confirmed run: same held-out split, same support/query partition, same E_derived bundle).
from experiments.exp_anchor_compose_inductive_entity_cskg_v1 import (  # noqa: E402
    build_planted_transe_arena, build_heldout_entity_split_ac, build_anchor_compose_codes,
    HELDOUT_ENTITY_FRAC, SUPPORT_FRAC, EVAL_KS, SCORE_CHUNK,
)

ANCHOR_NAME = "anchor_compose_spectral_init_cskg_v1"

# ---- Arms ----
ANCHOR_G = "ANCHOR_GAUSS"            # ANCHOR_COMPOSE over the gaussian(random)-init fit -> reproduces 0.12821
ANCHOR_S = "ANCHOR_SPEC"            # ANCHOR_COMPOSE over the spectral-warm-started fit -> THE test arm
ANCHOR_SS = "ANCHOR_SPEC_SCRAMBLE"  # ANCHOR_COMPOSE over scrambled-spectral init -> must-fail scale isolation
ORACLE = "ORACLE_GAUSS"            # gaussian fit, held-out folded in (codes learned) -> positive control ceiling
RANDOM = "RANDOM_CODES"            # null / arena floor (no fit)
PRIMARY_ARMS = [ANCHOR_G, ANCHOR_S]                 # scored on EVERY seed
CONTROL_ARMS = [ANCHOR_SS, ORACLE]                  # scored on control_seeds only
ALL_ARMS = [ANCHOR_G, ANCHOR_S, ANCHOR_SS, ORACLE, RANDOM]

CEIL_METRIC = "mrr"                 # primary gated metric = filtered MRR (degree-unbiased, rank-vs-all)
PRIMARY_METRIC = "hits@%d" % PRIMARY_K   # legacy hits@10 (reported, NOT gated)

# ---- CITED reference (verified on disk; the gaussian control must reproduce this) ----
# CITED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr
CONFIRMED_GAUSS_MRR = 0.12821       # ANCHOR_COMPOSE gaussian-init aggregate over seeds [7,13,17]
CONFIRMED_ORACLE_MRR = 0.137293     # ORACLE ceiling (transductive; ANCHOR already at 93.7% of this)
REPRO_TOL = 0.02                    # gaussian control must land within this of CONFIRMED_GAUSS_MRR (else drift)

# ---- ceiling-aware bands (pre-registered; NOT tuned on real data) ----
LIFT_MIN = 0.005          # HARD-PASS: spectral lift over gaussian >= this (recovers >55% of ~0.009 residual headroom)
LIFT_NOISE = 0.002        # HARD-FAIL: lift <= this = no transfer (compose-op washout)
STRUCT_MARGIN = 0.003     # HARD-PASS: (LIFT - SCRAMBLE_LIFT) >= this = structure, not scale
ORACLE_FIRE_RATIO = 3.0   # ORACLE_mrr >= 3x RANDOM_mrr (arena answerable, scale-free)
ORACLE_FIRE_ABS = 0.003   # AND ORACLE_mrr - RANDOM_mrr >= this (non-noise floor)
MIN_HELDOUT = 20          # min held-out QUERY edges for a valid discriminator
GUARD_FLOOR_EPS = 0.02    # F.4: RANDOM-beats-ANCHOR_GAUSS guard baseline must be > floor + this

# ---- self-test planted thresholds (calibrated on the synthetic additive-consistent grid, NOT real data) ----
SELFTEST_ORACLE_MRR_MIN = 0.30    # planted: ORACLE (learned held-out codes) mrr at least this
SELFTEST_ANCHOR_MRR_MIN = 0.12    # planted: ANCHOR_GAUSS mrr (zero-training bundle) at least this (path works)
SELFTEST_AC_BEATS_RANDOM = 0.06   # planted: (ANCHOR_GAUSS - RANDOM)_mrr >= this (discriminator fires)
SELFTEST_MIN_HO = 8

# Config profiles. SELFTEST/MEMSMOKE/FULL exercise the SAME spectral->fit->compose->score->verdict path.
SELFTEST_CFG = dict(k=12, epochs=350, n_neg=32, batch=4096,
                    heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0, min_heldout=SELFTEST_MIN_HO,
                    seeds=[7], control_seeds=[7])
# MEMSMOKE = FULL footprint (full N + k=24 + n_neg=128 + neg_chunk) but few epochs + 2 seeds. Proves no-OOM +
# per-seed empty_cache BEFORE the multi-hour FULL. NOT a discriminator gate (few epochs under-train).
MEMSMOKE_CFG = dict(k=24, epochs=25, n_neg=128, batch=8192, neg_chunk=16,
                    heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                    cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                    n_heldout_eval=2000, min_heldout=10, seeds=[7, 13], control_seeds=[7])
# FULL: k=24/epochs=500 == the VET-confirmed arena config (bit-identical gaussian reproduction). 3 seeds for the
# primary lift; controls (scramble/oracle) seed-7 only (they are robustness/positive controls, not the headline).
FULL_CFG = dict(k=24, epochs=500, n_neg=128, batch=8192, neg_chunk=16, ckpt_every=20,
                heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                n_heldout_eval=3000, min_heldout=MIN_HELDOUT, seeds=[7, 13, 17], control_seeds=[7])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.5f" % x) if (x == x) else "nan"


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
# Spectral warm-start: k-dim Laplacian graph-eigenmap of the TRAIN-edge graph, rescaled to the gaussian init
# std (0.1) so the comparison isolates STRUCTURE not scale. scramble=True permutes the row assignment across
# SEEN nodes (preserves per-column norms, destroys structure) for the must-fail scale-isolation control.
# Returns a torch (N,k) float tensor. Computed ONCE per seed; shared by the spectral + scrambled arms.
# ---------------------------------------------------------------------------

def build_spectral_init(train_int, N, k, seed, scramble=False, gauss_std=0.1):
    import scipy.sparse as sp
    from scipy.sparse.linalg import eigsh
    h = train_int[:, 0].astype(np.int64)
    t = train_int[:, 2].astype(np.int64)
    # undirected structural adjacency (relation-agnostic): both (h,t) and (t,h)
    rows = np.concatenate([h, t])
    cols = np.concatenate([t, h])
    data = np.ones(rows.shape[0], dtype=np.float64)
    A = sp.csr_matrix((data, (rows, cols)), shape=(N, N))
    A.data[:] = 1.0                                  # binarize (dedupe summed multi-edges)
    A.setdiag(0.0)
    A.eliminate_zeros()
    deg = np.asarray(A.sum(axis=1)).ravel()
    dinv = np.zeros(N, dtype=np.float64)
    nz = deg > 0
    dinv[nz] = 1.0 / np.sqrt(deg[nz])
    Dinv = sp.diags(dinv)
    A_norm = (Dinv @ A @ Dinv).tocsr()               # symmetric normalized adjacency (eigvecs = Laplacian eigenmaps)
    kk = int(min(k + 1, max(1, N - 2)))
    # top-kk eigenvalues of A_norm == smallest kk Laplacian eigenvalues (smoothest maps). Lanczos, no dense N-by-N.
    vals, vecs = eigsh(A_norm.astype(np.float64), k=kk, which="LA")
    order = np.argsort(vals)[::-1]                    # descending eigenvalue
    vecs = vecs[:, order]
    vecs = vecs[:, 1:1 + k]                           # drop the trivial (constant) top eigenvector; take next k
    if vecs.shape[1] < k:                             # tiny/degenerate graph -> pad with zeros (rescaled below)
        vecs = np.concatenate([vecs, np.zeros((N, k - vecs.shape[1]), dtype=np.float64)], axis=1)
    std = vecs.std(axis=0, keepdims=True)
    std[std < 1e-9] = 1.0
    vecs = vecs / std * float(gauss_std)             # match gaussian init per-dim std -> isolate STRUCTURE not scale
    if scramble:
        rng = np.random.default_rng(seed * 2777 + 11)
        seen = np.where(deg > 0)[0]
        if seen.shape[0] >= 2:
            perm = rng.permutation(seen)
            v2 = vecs.copy()
            v2[seen] = vecs[perm]                     # permute assignment across seen nodes (scale kept, structure broken)
            vecs = v2
    return torch.from_numpy(np.ascontiguousarray(vecs, dtype=np.float32))


# ---------------------------------------------------------------------------
# Fit the arms (gaussian + spectral primary; scramble + oracle controls) + build ANCHOR_COMPOSE from each +
# score PAIRED on the SAME held-out QUERY edges.
# ---------------------------------------------------------------------------

def _mk_ckpt(ckpt_dir, ckpt_every, tag, seed):
    if ckpt_dir is None or not ckpt_every:
        return None
    return FitCheckpoint(ckpt_dir, "%s_seed%d" % (tag, seed), ckpt_every)


def fit_and_score(train_int, support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                  all_true, do_controls, ckpt_dir=None):
    k = cfg["k"]; epochs = cfg["epochs"]; n_neg = cfg["n_neg"]; batch = cfg["batch"]
    neg_chunk = cfg.get("neg_chunk"); ckpt_every = cfg.get("ckpt_every")

    def _ec():
        if getattr(device, "type", "") == "cuda":
            torch.cuda.empty_cache()

    # --- spectral embedding (once; shared by spec + scramble) ---
    X_spec = build_spectral_init(train_int, N, k, seed, scramble=False)
    init_diag = dict(spec_norm=float(X_spec.norm().item()), spec_std=float(X_spec.std().item()))

    # --- gaussian(random)-init additive fit (the reproduce-0.12821 baseline) ---
    Xg, Dg = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, reciprocal=True, lr=A1_LR,
                             n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk, X_init=None, init_tag="gaussian",
                             ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive_gauss", seed))
    _ec()
    # --- spectral-warm-started additive fit (THE test arm) ---
    Xs, Ds = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, reciprocal=True, lr=A1_LR,
                             n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                             X_init=X_spec, init_tag="spectral",
                             ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive_spec", seed))
    _ec()

    # --- controls (seed in control_seeds only) ---
    Xsc = Dsc = Xo = Do = None
    X_scr = None
    if do_controls:
        X_scr = build_spectral_init(train_int, N, k, seed, scramble=True)
        Xsc, Dsc = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, reciprocal=True, lr=A1_LR,
                                   n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                                   X_init=X_scr, init_tag="spectral_scramble",
                                   ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive_scramble", seed))
        _ec()
        Xo, Do = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold_all,
                                 reciprocal=True, lr=A1_LR, n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                                 X_init=None, init_tag="gaussian_oracle",
                                 ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive_oracle", seed))
        _ec()

    # --- RANDOM null (no fit) ---
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, k, generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, k, generator=gR) * 0.1).to(device)

    # --- build ANCHOR_COMPOSE codes over each scaffold (zero training) ---
    Xac_g, support_deg = build_anchor_compose_codes(Xg, Dg, support_int, device)
    Xac_s, _ = build_anchor_compose_codes(Xs, Ds, support_int, device)

    scored = [
        (ANCHOR_G, additive_direct_scores(Xac_g, Dg, query_int, device, chunk=SCORE_CHUNK)),
        (ANCHOR_S, additive_direct_scores(Xac_s, Ds, query_int, device, chunk=SCORE_CHUNK)),
        (RANDOM, additive_direct_scores(Xr, Dr, query_int, device, chunk=SCORE_CHUNK)),
    ]
    if do_controls:
        Xac_sc, _ = build_anchor_compose_codes(Xsc, Dsc, support_int, device)
        scored.append((ANCHOR_SS, additive_direct_scores(Xac_sc, Dsc, query_int, device, chunk=SCORE_CHUNK)))
        scored.append((ORACLE, additive_direct_scores(Xo, Do, query_int, device, chunk=SCORE_CHUNK)))

    arm_metric, arm_sig = {}, {}
    for name, sc in scored:
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())

    del Xg, Dg, Xs, Ds, Xr, Dr, Xac_g, Xac_s
    if do_controls:
        del Xsc, Dsc, Xo, Do
    _ec()
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, init_diag=init_diag)


# ---------------------------------------------------------------------------
# One corpus run.
# ---------------------------------------------------------------------------

def run_corpus(pool_lbl, cfg, device, seed, corpus_name, do_controls, ckpt_dir=None):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
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
    all_true = build_true_by_hr_int(train_int, support_int, query_int)

    result = dict(corpus=corpus_name, seed=seed, N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]),
                  n_heldout_entities=len(hold_ids), n_support=int(support_int.shape[0]),
                  n_query_total=n_query_total, n_query_scored=int(query_int.shape[0]), n_cold=int(n_cold),
                  do_controls=bool(do_controls),
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    fs = fit_and_score(train_int, support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                       all_true, do_controls, ckpt_dir=ckpt_dir)
    am = fs["arm_metric"]
    scored_arms = list(am.keys())
    result.update(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in am[a].items() if kk != "n"} for a in scored_arms},
        arm_n={a: am[a]["n"] for a in scored_arms},
        arm_sigs=fs["arm_sig"], init_diag=fs["init_diag"],
    )
    return result


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _arm_mrr(ps, arm):
    return ps.get("arm_hits", {}).get(arm, {}).get(CEIL_METRIC, float("nan"))


def _arm_h10(ps, arm):
    return ps.get("arm_hits", {}).get(arm, {}).get(PRIMARY_METRIC, float("nan"))


def _sub(a, b):
    return (a - b) if (a == a and b == b) else float("nan")


def aggregate_and_verdict(per_seed):
    m = {a: _nm([_arm_mrr(ps, a) for ps in per_seed]) for a in ALL_ARMS}
    h10 = {a: _nm([_arm_h10(ps, a) for ps in per_seed]) for a in ALL_ARMS}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))
    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps.get("arm_hits", {}).get(a, {}).get(mk, float("nan")) for ps in per_seed])
                    for mk in metric_keys} for a in ALL_ARMS}

    lift = _sub(m[ANCHOR_S], m[ANCHOR_G])                       # headline: spectral vs gaussian
    scramble_lift = _sub(m[ANCHOR_SS], m[ANCHOR_G])
    struct_margin = _sub(lift, scramble_lift)                  # structure isolation (lift not explained by scramble)
    oracle_headroom = _sub(m[ORACLE], m[RANDOM])               # H
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])
    rel_lift = (lift / m[ANCHOR_G]) if (lift == lift and m[ANCHOR_G] == m[ANCHOR_G] and m[ANCHOR_G] > 0) else float("nan")

    enough_heldout = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(oracle_headroom == oracle_headroom and oracle_headroom >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    # gaussian control must reproduce the confirmed 0.12821 (else fit/env drift -> paired comparison invalid)
    gauss_repro = bool(m[ANCHOR_G] == m[ANCHOR_G] and abs(m[ANCHOR_G] - CONFIRMED_GAUSS_MRR) <= REPRO_TOL)
    # F.4 broken-guard: RANDOM must NOT beat ANCHOR_GAUSS (baseline ANCHOR_GAUSS is well above the RANDOM floor)
    broken = bool(m[RANDOM] == m[RANDOM] and m[ANCHOR_G] == m[ANCHOR_G] and (m[RANDOM] - m[ANCHOR_G]) > GUARD_FLOOR_EPS)
    have_scramble = bool(m[ANCHOR_SS] == m[ANCHOR_SS])
    struct_ok = bool(struct_margin == struct_margin and struct_margin >= STRUCT_MARGIN) if have_scramble else False

    warmstart_lifts = bool(lift == lift and lift >= LIFT_MIN and struct_ok)
    scale_artifact = bool(lift == lift and lift >= LIFT_MIN and have_scramble and not struct_ok)
    no_lift = bool(lift == lift and lift <= LIFT_NOISE)

    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif broken:
        verdict = "BROKEN_TEST_RANDOM_BEATS_GAUSS"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
    elif not gauss_repro:
        verdict = "INCONCLUSIVE_BASELINE_REPRO_DRIFT"
    elif warmstart_lifts:
        verdict = "HARD_PASS_SPECTRAL_WARMSTART_LIFTS"
    elif scale_artifact:
        verdict = "MIDDLE_BAND_SCALE_ARTIFACT_NOT_STRUCTURAL"
    elif no_lift:
        verdict = "HARD_FAIL_NO_LIFT_COMPOSE_WASHOUT"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_LIFT"

    verdict_msg = (
        "%s || HELD-OUT MRR [nq=%d,seeds=%d]: ANCHOR_GAUSS=%s (confirmed=%.5f repro=%s) ANCHOR_SPEC=%s | "
        "SCRAMBLE=%s ORACLE=%s RANDOM=%s || LIFT(spec-gauss)=%s (rel=%s) vs HARD_PASS>=%.3f HARD_FAIL<=%.3f | "
        "struct_margin(lift-scramble_lift)=%s (>=%.3f=%s) | oracle H=%s ratio=%sx (fires=%s) | broken=%s"
        % (verdict, n_query, len(per_seed), _fmt(m[ANCHOR_G]), CONFIRMED_GAUSS_MRR, gauss_repro, _fmt(m[ANCHOR_S]),
           _fmt(m[ANCHOR_SS]), _fmt(m[ORACLE]), _fmt(m[RANDOM]), _fmt(lift),
           (_fmt(rel_lift) if rel_lift == rel_lift else "nan"), LIFT_MIN, LIFT_NOISE, _fmt(struct_margin),
           STRUCT_MARGIN, struct_ok, _fmt(oracle_headroom),
           (_fmt(oracle_ratio) if oracle_ratio != float("inf") else "inf"), oracle_fires, broken))

    def _rnd(x, nd=6):
        return round(x, nd) if x == x else None

    gates = dict(
        verdict=verdict, ceil_metric=CEIL_METRIC,
        heldout_mrr={a: _rnd(m[a]) for a in ALL_ARMS},
        heldout_hits_at_10={a: _rnd(h10[a], 5) for a in ALL_ARMS},
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        lift_spec_vs_gauss=_rnd(lift), rel_lift=_rnd(rel_lift, 4),
        scramble_lift=_rnd(scramble_lift), struct_margin=_rnd(struct_margin),
        oracle_headroom=_rnd(oracle_headroom),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        confirmed_gauss_mrr=CONFIRMED_GAUSS_MRR, gauss_repro=gauss_repro,
        n_query_scored=n_query,
        bands=dict(LIFT_MIN=LIFT_MIN, LIFT_NOISE=LIFT_NOISE, STRUCT_MARGIN=STRUCT_MARGIN,
                   ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS, REPRO_TOL=REPRO_TOL,
                   MIN_HELDOUT=MIN_HELDOUT, HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC, SUPPORT_FRAC=SUPPORT_FRAC),
        enough_heldout=enough_heldout, oracle_fires=oracle_fires, struct_ok=struct_ok, broken=broken,
        warmstart_lifts=warmstart_lifts, scale_artifact=scale_artifact, no_lift=no_lift,
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test (planted TransE-consistent held-out-entity grid).
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
    pool = build_planted_transe_arena(7, n_ent=300, n_rel=6, k_lat=8, deg=3)
    cfg = dict(SELFTEST_CFG)
    res = run_corpus(pool, cfg, device, 7, "PLANTED_TRANSE_HELDOUT_ENTITY", do_controls=True)
    out = dict(n_grid_entities=res.get("N"), n_heldout_entities=res.get("n_heldout_entities"),
               n_support=res.get("n_support"), n_query=res.get("n_query_scored"), n_cold=res.get("n_cold"))
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted grid produced too few held-out-entity queries (%s)" % res.get("n_query_scored")
        return False, out

    am = res["arm_hits"]
    m = {a: am.get(a, {}).get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(res["arm_sigs"].values()))
    anchor_margin = _sub(m[ANCHOR_G], m[RANDOM])
    oracle_margin = _sub(m[ORACLE], m[RANDOM])
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    oracle_recovers = bool(m[ORACLE] == m[ORACLE] and m[ORACLE] >= SELFTEST_ORACLE_MRR_MIN)
    oracle_fires = bool(oracle_margin == oracle_margin and oracle_margin >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    anchor_recovers = bool(m[ANCHOR_G] == m[ANCHOR_G] and m[ANCHOR_G] >= SELFTEST_ANCHOR_MRR_MIN)
    anchor_beats_random = bool(anchor_margin == anchor_margin and anchor_margin >= SELFTEST_AC_BEATS_RANDOM)
    # spectral init actually altered the fit trajectory (ANCHOR_SPEC != ANCHOR_GAUSS signature)
    init_changed_fit = bool(res["arm_sigs"].get(ANCHOR_S) != res["arm_sigs"].get(ANCHOR_G))
    arms_differ = bool(n_sigs >= 4)

    # spectral coords carry STRUCTURE (spectral init != scrambled init) with MATCHED scale (per-dim std within
    # tol) -- rebuild both inits from the SAME planted train split the run used.
    ent2i, rel2i = build_ids(pool, [], [])
    N_pl = len(ent2i)
    train_lbl_pl, _sup, _qry, _hold, _nc = build_heldout_entity_split_ac(
        pool, ent2i, cfg["heldout_entity_frac"], cfg["support_frac"], 7)
    train_int_pl = _to_int_edges(train_lbl_pl, ent2i, rel2i)
    X_spec = build_spectral_init(train_int_pl, N_pl, cfg["k"], 7, scramble=False)
    X_scr = build_spectral_init(train_int_pl, N_pl, cfg["k"], 7, scramble=True)
    spec_structure = bool(not torch.equal(X_spec, X_scr))
    scale_matched = bool(abs(float(X_spec.std().item()) - float(X_scr.std().item())) < 1e-4)

    # F.4 guard baseline valid: the RANDOM-beats-ANCHOR_GAUSS broken guard's baseline (ANCHOR_GAUSS) must be
    # above the RANDOM floor on this planted arena (else the guard mis-fires).
    guard_ok_planted = bool(m[ANCHOR_G] > m[RANDOM] + GUARD_FLOOR_EPS)

    st_verdict, st_msg, st_gates = aggregate_and_verdict([res])

    # Gate F.1-F.4 declarations (ENFORCE via _validity_preflight) + classes 1-4 (warn).
    exercised_entrypoints = {"fit_kge_anchor1", "build_spectral_init", "build_anchor_compose_codes"}
    vp_ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["fit_kge_anchor1", "build_spectral_init", "build_anchor_compose_codes"],
         "exercised_entrypoints": sorted(exercised_entrypoints),
         "extra": "self-test fits the REAL additive fit (gaussian AND X_init=spectral), builds the REAL spectral "
                  "eigenmap, and the REAL ANCHOR_COMPOSE bundle at N~300"},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 1, "device": None, "seed": 1, "epochs": 1,
                    "reciprocal": True, "lr": A1_LR, "n_neg": 1, "batch_size": 1, "neg_chunk": None,
                    "X_init": None, "init_tag": "gaussian", "ckpt": None},
         "extra": "the new X_init/init_tag warm-start kwargs must bind against the live fit signature; both ship "
                  "WITH the cell via Pattern-6 auto-SCP of _kge_anchor1_fit -> no remote drift"},
        {"kind": "guard_baseline_valid", "baseline_score": m[ANCHOR_G], "floor_score": m[RANDOM],
         "guard_name": "BROKEN_TEST_RANDOM_BEATS_GAUSS", "baseline_name": "ANCHOR_GAUSS", "floor_name": "RANDOM",
         "eps": GUARD_FLOOR_EPS,
         "extra": "the RANDOM-beats-ANCHOR_GAUSS broken guard compares to ANCHOR_GAUSS, which is well above the "
                  "RANDOM floor (not structurally at floor) -> the guard is valid on this arena"},
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(oracle_recovers and oracle_fires),
         "control_name": "ORACLE_GAUSS", "headline_name": "oracle_beats_random_heldout_mrr",
         "extra": "planted: ORACLE (learned held-out codes) recovers held-out tails and clears RANDOM by the "
                  "ceiling-aware ratio+abs fire gate -> the arena is answerable and the metric can move"},
        {"kind": "metric_moves", "metric_name": "heldout_mrr",
         "values": [m[RANDOM], m[ANCHOR_G], m[ANCHOR_S], m[ORACLE]],
         "extra": "MRR RANDOM=%.3f GAUSS=%.3f SPEC=%.3f ORACLE=%.3f: the readout responds to composed/learned/"
                  "warm-started codes" % (m[RANDOM], m[ANCHOR_G], m[ANCHOR_S], m[ORACLE])},
        {"kind": "negative_control_margin", "control_scores": [m[RANDOM], m[ANCHOR_SS]],
         "headline_threshold": m[ANCHOR_G], "higher_is_pass": True, "margin": 0.0, "n_repeats_min": 2,
         "control_name": "RANDOM_and_SCRAMBLE_not_above_gauss",
         "extra": "RANDOM (null) and scrambled-spectral must not sit ABOVE the gaussian ANCHOR baseline on the "
                  "planted arena (they carry no extra structural signal that beats the confirmed baseline)"},
    ], run_mode="self_test")

    out.update(
        heldout_mrr={a: round(m[a], 6) for a in ALL_ARMS},
        heldout_hits_at_10={a: round(am.get(a, {}).get(PRIMARY_METRIC, float("nan")), 5) for a in ALL_ARMS},
        n_distinct_sigs=n_sigs, anchor_margin=round(anchor_margin, 6), oracle_margin=round(oracle_margin, 6),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        lift_spec_vs_gauss=round(_sub(m[ANCHOR_S], m[ANCHOR_G]), 6),
        scramble_lift=round(_sub(m[ANCHOR_SS], m[ANCHOR_G]), 6),
        oracle_recovers=oracle_recovers, oracle_fires=oracle_fires, anchor_recovers=anchor_recovers,
        anchor_beats_random=anchor_beats_random, init_changed_fit=init_changed_fit, arms_differ=arms_differ,
        spec_structure=spec_structure, scale_matched=scale_matched, guard_ok_planted=guard_ok_planted,
        selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok), init_diag=res.get("init_diag"),
        validity_preflight_declared=["real_code_path", "substrate_signature", "guard_baseline_valid",
                                     "positive_control", "metric_moves", "negative_control_margin"],
    )
    ok = bool(oracle_recovers and oracle_fires and anchor_recovers and anchor_beats_random
              and init_changed_fit and arms_differ and spec_structure and scale_matched and guard_ok_planted)
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
    cfg = dict({"self_test": SELFTEST_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    control_seeds = set(cfg.get("control_seeds", [seeds[0]]))
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s control_seeds=%s k=%s epochs=%s" %
         (device, torch.cuda.is_available(), run_mode, seeds, sorted(control_seeds), cfg["k"], cfg["epochs"]))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s lift=%s scramble_lift=%s init_changed_fit=%s spec_structure=%s oracle_fires=%s "
         "vp_ok=%s" % (st_ok, st_res.get("lift_spec_vs_gauss"), st_res.get("scramble_lift"),
                       st_res.get("init_changed_fit"), st_res.get("spec_structure"), st_res.get("oracle_fires"),
                       st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s" % json.dumps(
                {k: st_res.get(k) for k in ("oracle_recovers", "oracle_fires", "anchor_recovers",
                                            "anchor_beats_random", "init_changed_fit", "arms_differ",
                                            "spec_structure", "scale_matched", "guard_ok_planted", "fail")}),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS spectral-init warm-start: real fit runs with X_init (gaussian AND spectral); "
                        "spectral init changes the fit and carries scale-matched structure; ORACLE fires; 6 "
                        "validity-preflight checks declared (F.1-F.4 ENFORCE)",
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
            do_controls = seed in control_seeds
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d pool_edges=%d do_controls=%s"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["core_avgdeg"],
                    prov["n_rel_tokens"], len(pool), do_controls))
            res = run_corpus(pool, cfg, device, seed, "CSKG_CORE_HELDOUT_ENTITY", do_controls, ckpt_dir=out_dir)
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out-entity query edges too few (%d < %d)" %
                                   (res.get("n_query_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            min_sigs = 4 if do_controls else 3
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < min_sigs:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs (<%d)"
                                   % (seed, len(sigset), min_sigs))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            cleanup_seed_checkpoints(out_dir, seed)
            am = res["arm_hits"]
            _log("seed=%d nq=%d n_sup=%d | mrr GAUSS=%s SPEC=%s SCRAMBLE=%s ORACLE=%s RANDOM=%s (%.1fs)" %
                 (seed, res["n_query_scored"], res["n_support"],
                  _fmt(am.get(ANCHOR_G, {}).get(CEIL_METRIC, float("nan"))),
                  _fmt(am.get(ANCHOR_S, {}).get(CEIL_METRIC, float("nan"))),
                  _fmt(am.get(ANCHOR_SS, {}).get(CEIL_METRIC, float("nan"))),
                  _fmt(am.get(ORACLE, {}).get(CEIL_METRIC, float("nan"))),
                  _fmt(am.get(RANDOM, {}).get(CEIL_METRIC, float("nan"))), time.time() - ts))
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
                   seeds=seeds, control_seeds=sorted(control_seeds), config=cfg, gates=gates,
                   mechanism_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "memsmoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--memsmoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("memsmoke" if args.memsmoke else args.run_mode)
    if not args.self_test and not args.memsmoke and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "memsmoke", "full"):
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
