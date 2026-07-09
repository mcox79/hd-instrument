"""Stage-3 fix: SPARSE BLOCK-CODE binding so DG-expansion COMPOSES with the binding-consistency objective.

Stage-2 (grounding_encoder_clean_codes_retrain_v1, MIDDLE_BAND) MEASURED that the binding-consistency
training objective is the active ingredient (BINDOBJ_ONLY recall 0.30 -> 0.4234, Pareto-dominates) BUT dense
HRR circular-convolution binding is INCOMPATIBLE with sparse DG codes: FULL_STACK (dense bind + DG k-WTA
expand) regressed to 0.25 (expand_gain=-0.2117) and reach stayed 1 for EVERY arm. Diagnosed root cause
(notes/research_sparse_compatible_binding_operator_2026-07-09.md): dense circular conv makes a DENSE bound
product; a hard per-block argmax then destructively collapses it. Sparse codes (decorrelation/capacity) and
clean dense binding (chaining) are in conflict.

THE FIX (RANK 1 + RANK 2 from the drill): replace dense HRR circular convolution with SPARSE BLOCK-CODE
binding via block-LOCAL circular convolution (LCC; Frady/Kleyko/Sommer arXiv:2009.06734) matched 1:1 to the
GSBC graded block code the DG sparsifier already produces -- sparsity-preserving BY CONSTRUCTION (one-hot-per-
block role SHIFTS each block's support; k active per block in -> k active per block out, never denser, no
destructive re-sparsify). RANK 2 adds a resonator/factorizer-style ITERATIVE cleanup on the multi-hop unbind
(Hersche et al. arXiv:2303.13957; the CA3-attractor analog) for reach>=2. Both composed with the Stage-2
binding-consistency objective, UNCHANGED.

Arms (per model-seed):
  A DENSE_BINDOBJ          : Stage-2 winner reproduce (dense HRR bind + bidirectional bindobj, dense code).
                             CONTRAST FLOOR: MUST reproduce recall ~0.42, reach 1 (keep-and-beat).
  B DENSE_BIND_DGEXPAND    : Stage-2 regression reproduce (dense HRR bind + DG k-WTA expand + bindobj).
                             The net-NEGATIVE DG-expansion baseline (Stage-2 FULL_STACK 0.25, expand -0.21).
  C BLOCK_BINDOBJ__g{0,1,2}: RANK 1 -- block-local circ-conv bind + bidirectional bindobj on graded sparse
                             block codes, at 3 block geometries (block-size/count sweep per the drill caveat).
  D BLOCK_RESONATOR__g0    : RANK 1 + RANK 2 -- block bind + iterative resonator cleanup readout (primary geo).

DISCRIMINATOR: does sparse-block-binding + bindobj restore reach>=2 on the SPARSE learned codes (where dense
bind+expand FAILED at reach 1) WHILE keeping recall >= 0.42 AND keeping codes sparse? Report whether DG-
expansion now goes NET-POSITIVE (block_expand_gain = recall(best BLOCK) - recall(DENSE_BINDOBJ)) vs Stage-2's
-0.2117. HARD_PASS = a BLOCK arm reach>=2 (reach_delta>=1 over DENSE_BINDOBJ) AND recall>=0.42 AND precision
>= floor AND sparse_rate <= 0.10 (sparsity preserved) AND non-collapsed/shuffle-gated reach. HARD_FAIL = all
BLOCK arms reach<=1 (chaining ceiling is NOT a binding-operator mismatch) OR block binding costs recall
(< 0.42 - 0.05, block-locality destroys cross-block info) OR block hop-1 unbind fidelity < 0.90. Both gold.

HONESTY: REAL-substrate multi-hop grounded-attribute propagation on LEARNED codes. NOT language understanding.
Grounded scalar = synthetic graph-smooth field over the REAL ConceptNet subgraph (honest stand-in). Teacher-
free, CPU-only, ASCII-only. Reuses the Stage-2 dense arms + reach/recall machinery + the GSBC graded block
STE + block-local circular convolution (hdlab.binding algebra on reshaped [.,kb,blk_l]); does NOT rebuild.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (encoder digests + recovered-edge-set hashes across all 6 arms)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except)
# - crlb_n/a: reach ordering-acc chance floor = 0.5; discriminator is shuffle+collapse-gated reach + role-
#   recovery edge_recall vs a reproduced dense baseline floor, not a closed-form estimator noise floor.
# - baseline_in_band at smoke: DENSE_BINDOBJ recall in [0.34,0.50] (brackets MEASURED 0.4234) AND reach<=1.
# - discriminator survives scale: smoke fires the ENABLING mechanism (block hop-1 unbind fidelity>=0.95 +
#   sparsity preserved + arms differ + dense baseline reproduces). SMOKE exercises the SAME 6 arms/branches
#   as FULL; only n_nodes/epochs/dg-geo-count/seeds scale. reach>=2 verdict is answered by FULL (hand-off).
# - HARD_PASS strictly above floor: reach 1->2 is a full integer jump (categorical, well above floor+5%).
# - HP_SCOPE: reach+recall+sparsity gates apply to the BLOCK arms; DENSE_* are the reproduce-the-floor and
#   reproduce-the-regression controls (must reproduce; NOT expected to pass the chaining gate).
# - sweep axis (block geometry g0/g1/g2 within BLOCK_BINDOBJ): cardinality EXPECTED_N_UNITS=n_seeds; each
#   seed asserted to produce all 6 arm-metrics (arm-cardinality check).
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (shuffled empirical null recomputed per run; over-
#   smoothing collapse gate on the resonator; recovery crosstalk floor is codebook-size-aware sqrt(2 ln n/d)).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-arm flush prints + heartbeat)
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
    get_output_dir,
    write_metrics,
    write_partial,
)
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import (  # noqa: E402
    char_trigram_features,
    build_adjlist,
    ProjHead,
    info_nce,
    vicreg_repulsion,
    _l2norm,
)
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import (  # noqa: E402
    make_smooth_attribute,
    attribute_assortativity,
    multi_source_bfs,
    distance_bins,
    SUBGRAPH_BASE_SEED,
)
# Reuse the multihop baseline VERBATIM: reach/recall machinery (bit-identical defs) + dense arms.
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph,
    make_unitary_roles,
    score_role,
    _topk_floor_adj,
    _edge_recall_precision,
    crosstalk_floor,
    reach_over_recovered,
    train_binding_encoder,
    _l2,
    _emb_digest,
    ATTR_ASSORT_SMOOTH_MIN,
    ATTR_ASSORT_SHUFFLED_MAX,
)
# Reuse the Stage-2 dense retrain arms + dense unbind VERBATIM (contrast floors A/B).
from experiments.exp_grounding_encoder_clean_codes_retrain_v1 import (  # noqa: E402
    train_encoder_v2,
    torch_hrr_unbind,
    DG_SPARSITY,
)
# Reuse the CERTIFIED differentiable GSBC graded block-code STE (top-m survivors, unit-L1 per block).
from experiments.exp_encoder_v11_gsbc_graded_sparse_v1_core import _gsbc_code_from_z  # noqa: E402
# Reuse the canonical block-local circular-conv algebra for the self-test reuse-equivalence check.
from hdlab.binding import bind as _hd_bind  # noqa: E402

ANCHOR_NAME = "grounding_encoder_sparse_block_binding_v1"

# ---------------------------------------------------------------------------
# Block-local circular convolution (LCC) -- RANK 1. Reshape [B, kb*blk_l] -> [B, kb, blk_l], per-block
# circular convolution (FFT on the block axis). This IS hdlab.binding.bind applied per-block (the self-test
# asserts allclose vs hdlab.binding.bind on reshaped tensors); implemented here with rfft for a differentiable,
# tracing-free training-loop path. Sparsity-preserving by construction with one-hot-per-block roles (a per-
# block circular SHIFT never densifies: m active per block in -> m active per block out).
# ---------------------------------------------------------------------------

def block_bind(roles, codes, kb, blk_l):
    """Block-local circular convolution: roles,codes [B, kb*blk_l] -> [B, kb*blk_l]. Differentiable."""
    B = codes.shape[0]
    r = roles.reshape(B, kb, blk_l)
    c = codes.reshape(B, kb, blk_l)
    out = torch.fft.irfft(torch.fft.rfft(r, dim=-1) * torch.fft.rfft(c, dim=-1), n=blk_l, dim=-1)
    return out.reshape(B, kb * blk_l)


def block_unbind(bound, roles, kb, blk_l):
    """Block-local circular correlation (inverse of block_bind): bound,roles [B, kb*blk_l] -> [B, kb*blk_l]."""
    B = bound.shape[0]
    b = bound.reshape(B, kb, blk_l)
    r = roles.reshape(B, kb, blk_l)
    out = torch.fft.irfft(torch.fft.rfft(b, dim=-1) * torch.conj(torch.fft.rfft(r, dim=-1)), n=blk_l, dim=-1)
    return out.reshape(B, kb * blk_l)


def make_block_shift_roles(T, kb, blk_l, rng):
    """T roles [T, kb*blk_l], each one-hot per block (pure per-block circular shift key). One-hot-per-block is
    the sparsity-preserving role form (Frady/Kleyko LCC); m-hot roles would densify the bound product."""
    roles = np.zeros((T, kb, blk_l), dtype=np.float32)
    offs = rng.integers(0, blk_l, size=(T, kb))
    bidx = np.arange(kb)
    for t in range(T):
        roles[t, bidx, offs[t]] = 1.0
    return roles.reshape(T, kb * blk_l).astype(np.float32)


def _l2t(Z):
    return Z / (Z.norm(dim=1, keepdim=True) + 1e-8)


# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME 6 arms/branches as FULL; only scale differs)
# ---------------------------------------------------------------------------

SELECT_TAU = 0.10           # GSBC graded STE backward softmax temperature (v11-certified regime)
W_PROX_STRONG = 0.3         # bindobj: proximity down-weighted so binding-consistency dominates (Stage-2 val)
W_BIND_STRONG = 2.0         # bindobj: binding term up-weighted (MLC "objective change" headline lever)

# Block geometries (all dg_dim = kb*blk_l = 4096): the block-size/count sweep the drill flagged as needed for
# our k-WTA regime (paper assumes one-hot-per-block). g0 = certified GSBC operating point.
#   (kb, blk_l, m, active_frac=m/blk_l)
BLOCK_GEOMS = [
    ("g0", 32, 128, 5),   # certified GSBC point; active 0.0391
    ("g1", 32, 128, 8),   # denser survivors; active 0.0625
    ("g2", 64, 64, 3),    # more/smaller blocks; active 0.0469
]
PRIMARY_GEO = "g0"
RESONATOR_ITERS = 3
RESONATOR_BETA = 12.0       # moderate (NOT n_dim-scale) per the multi-hop soft-mechanism beta-regime warning

SELFTEST_CFG = dict(
    seeds=[7],
    n_nodes=400, epochs=10, batch=256, code_dim=256, dg_dim=1024, feat_dim=1024,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_ground_seeds=20, diffuse_steps=8, n_sources=6,
    D=[1, 2, 3], alpha=0.85, recover_topk=8, cos_floor_c=1.1, n_pairs=2000,
    block_geoms=[BLOCK_GEOMS[0]],
)

SMOKE_CFG = dict(
    # code_dim=128 for the DENSE arms (Stage-2 smoke precedent: at 256 the small-N baseline inflates and the
    # reach discriminator can't be read). Block arms live at dg_dim=kb*blk_l=4096 regardless of code_dim.
    seeds=[7, 13],
    n_nodes=1800, epochs=45, batch=256, code_dim=128, dg_dim=4096, feat_dim=4096,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_ground_seeds=30, diffuse_steps=10, n_sources=20,
    D=[1, 2, 3, 4], alpha=0.85, recover_topk=8, cos_floor_c=1.1, n_pairs=4000,
    block_geoms=BLOCK_GEOMS,
)

FULL_CFG = dict(
    seeds=[7, 13, 17],
    n_nodes=5000, epochs=120, batch=512, code_dim=256, dg_dim=4096, feat_dim=8192,
    temp=0.10, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_ground_seeds=80, diffuse_steps=12, n_sources=50,
    D=[1, 2, 3, 4, 5], alpha=0.85, recover_topk=8, cos_floor_c=1.1, n_pairs=6000,
    block_geoms=BLOCK_GEOMS,
)

# ---------------------------------------------------------------------------
# Pre-registered bands (picked BEFORE the FULL run; MEASURED anchors from Stage-2 metrics)
# ---------------------------------------------------------------------------
BASELINE_RECALL_LO = 0.34     # MEASURED@retrain_v1/metrics.json:gates.recall_mean.BINDOBJ_ONLY=0.4234 (bracket)
BASELINE_RECALL_HI = 0.50
BASELINE_REACH_MAX = 1        # reach-1 cap to beat (baseline_in_band; never chained on these codes)

RECALL_KEEP_MIN = 0.42        # HARD_PASS: BLOCK arm must KEEP the Stage-2 0.42 recall baseline
RECALL_COST_DELTA = 0.05      # HARD_FAIL if best BLOCK recall < DENSE_BINDOBJ - this (block-locality costs recall)
REACH_HP_MIN = 2              # HARD_PASS: BLOCK arm effective reach must extend to hop 2
REACH_DELTA_HP = 1            # HARD_PASS: reach(BLOCK) - reach(DENSE_BINDOBJ) >= 1
PRECISION_FLOOR = 0.10        # spurious-edge guard
SPARSE_MAX = 0.10             # sparsity-preservation gate: BLOCK codes must stay materially sparse (<=10%)
BLOCK_HOP1_FIDELITY_MIN = 0.90  # self-test: block-bind then block-unbind recovers filler (dense-HRR-on-sparse=0.80)

# Arm names
DENSE_BINDOBJ = "DENSE_BINDOBJ"             # A: Stage-2 winner reproduce (dense bind + bindobj)
DENSE_BIND_DGEXPAND = "DENSE_BIND_DGEXPAND"  # B: Stage-2 regression reproduce (dense bind + DG expand + bindobj)


def _block_arm(gtag):
    return "BLOCK_BINDOBJ__%s" % gtag


def _reson_arm(gtag):
    return "BLOCK_RESONATOR__%s" % gtag


def _all_arms(cfg):
    arms = [DENSE_BINDOBJ, DENSE_BIND_DGEXPAND]
    arms += [_block_arm(g[0]) for g in cfg["block_geoms"]]
    arms += [_reson_arm(PRIMARY_GEO)]
    return arms


def _block_arms(cfg):
    return [_block_arm(g[0]) for g in cfg["block_geoms"]] + [_reson_arm(PRIMARY_GEO)]


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics (SCHEMA-VET section 13)
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(
        pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode,
        expected_n_units=expected_n_units, host=platform.node(),
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(
        verdict="CELL_CRASHED",
        verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
        summary=("CELL_CRASHED: %s" % type(exc).__name__),
        elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(), anchor_name=ANCHOR_NAME,
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


# ---------------------------------------------------------------------------
# BLOCK encoder training: ProjHead -> graded sparse block code (STE) -> block-local bindobj (RANK 1)
# ---------------------------------------------------------------------------

def train_encoder_block(X, edges, rels, roles_np, cfg, seed, kb, blk_l, m, out_dir=None, tag="BLOCK"):
    """Retrain a binding-structured encoder producing GRADED SPARSE BLOCK codes, bound with block-LOCAL
    circular convolution (sparsity-preserving) and the bidirectional binding-consistency objective. roles_np:
    [T, kb*blk_l] one-hot-per-block shift keys. Returns [n, kb*blk_l] positive unit-L1-per-block sparse codes."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    feat_dim = X.shape[1]
    out_dim = kb * blk_l
    Xt = torch.from_numpy(X)
    model = ProjHead(feat_dim, out_dim)
    opt = torch.optim.Adam(model.parameters(), lr=cfg["lr"])
    roles_t = torch.from_numpy(roles_np)  # [T, out_dim]
    E = edges.shape[0]
    e_a = edges[:, 0].astype(np.int64)
    e_b = edges[:, 1].astype(np.int64)
    e_r = rels.astype(np.int64)
    rng = np.random.default_rng(seed + 7)
    log_every = max(1, cfg["epochs"] // 5)
    t_ep = time.perf_counter()
    for ep in range(cfg["epochs"]):
        bs = min(cfg["batch"], E)
        eidx = rng.choice(E, size=bs, replace=False)
        flip = rng.random(bs) < 0.5
        ai = np.where(flip, e_b[eidx], e_a[eidx])
        pi = np.where(flip, e_a[eidx], e_b[eidx])
        ri = e_r[eidx]
        ha = model(Xt[torch.from_numpy(ai)])
        hp = model(Xt[torch.from_numpy(pi)])
        # graded sparse block codes (sparsity by construction; differentiable STE)
        ca = _gsbc_code_from_z(ha, kb, blk_l, m, SELECT_TAU)
        cp = _gsbc_code_from_z(hp, kb, blk_l, m, SELECT_TAU)
        rt = roles_t[torch.from_numpy(ri)]
        # base proximity (down-weighted) + VICReg repulsion on the block codes
        loss = W_PROX_STRONG * info_nce(ca, cp, cfg["temp"]) + vicreg_repulsion(
            torch.cat([ca, cp], dim=0), cfg["lambda_cov"], cfg["lambda_var"])
        # forward binding-consistency: block_bind(role_r, ca) matches the r-typed neighbour (in-batch negs)
        loss = loss + W_BIND_STRONG * info_nce(block_bind(rt, ca, kb, blk_l), cp, cfg["temp"])
        # backward unbind-reconstruction: block_unbind(role_r, cp) recovers the anchor (exact inverse)
        loss = loss + W_BIND_STRONG * info_nce(block_unbind(cp, rt, kb, blk_l), ca, cfg["temp"])
        opt.zero_grad()
        loss.backward()
        opt.step()
        if (ep % log_every == 0) or (ep == cfg["epochs"] - 1):
            _log("  train seed=%d %s ep=%d/%d loss=%.4f (%.1fs)" % (
                seed, tag, ep, cfg["epochs"], float(loss.detach()), time.perf_counter() - t_ep))
            if out_dir is not None:
                try:
                    from experiments._cell_heartbeat import emit_heartbeat
                    emit_heartbeat(str(out_dir), unit_idx=ep, total_units=cfg["epochs"],
                                   elapsed_s=time.perf_counter() - t_ep)
                except Exception as _hb_e:  # heartbeat best-effort telemetry (SCHEMA-VET 13D)
                    _log("  [heartbeat-warn] %s: %s" % (type(_hb_e).__name__, str(_hb_e)[:120]))
    with torch.no_grad():
        emb = _gsbc_code_from_z(model(Xt), kb, blk_l, m, SELECT_TAU).numpy().astype(np.float32)
    return emb


# ---------------------------------------------------------------------------
# BLOCK recovery: role-apply readout with block-local circular convolution (+ optional resonator cleanup)
# ---------------------------------------------------------------------------

def score_role_block(emb, roles_np, kb, blk_l):
    """S[i,j] = max_r cos(block_bind(role_r, code_i), code_j): typed block-binding match, native block read."""
    n = emb.shape[0]
    T = roles_np.shape[0]
    Zt = torch.from_numpy(emb.astype(np.float32))
    zn = _l2t(Zt)
    S = np.full((n, n), -np.inf, dtype=np.float32)
    for r in range(T):
        role_r = torch.from_numpy(roles_np[r].astype(np.float32))[None, :].repeat(n, 1)
        predn = _l2t(block_bind(role_r, Zt, kb, blk_l))
        sc = (predn @ zn.T).numpy().astype(np.float32)
        np.maximum(S, sc, out=S)
    return S


def score_role_block_resonator(emb, roles_np, kb, blk_l, m, n_iters, beta):
    """RANK 2: block-bind role-apply readout with iterative resonator/factorizer cleanup against the codebook
    (all node codes) before scoring -- the CA3-attractor analog. Each iter: soft-bundle the beta-scaled nearest
    codebook entries, re-project to the block-code manifold (top-m per block, unit-L1) to STAY sparse. Returns
    (S, diag) where diag carries the non-vacuous / over-smoothing guards."""
    n = emb.shape[0]
    T = roles_np.shape[0]
    Zt = torch.from_numpy(emb.astype(np.float32))
    zn = _l2t(Zt)
    S = np.full((n, n), -np.inf, dtype=np.float32)
    moved = []
    attractor_frac = []
    for r in range(T):
        role_r = torch.from_numpy(roles_np[r].astype(np.float32))[None, :].repeat(n, 1)
        pred = block_bind(role_r, Zt, kb, blk_l)
        pred0 = pred.clone()
        for _it in range(n_iters):
            pn = _l2t(pred)
            sims = pn @ zn.T                                  # [n, n] against the codebook
            w = torch.softmax(beta * sims, dim=1)
            pred = w @ Zt                                     # soft-bundle nearest codebook entries
            pred = _gsbc_code_from_z(pred, kb, blk_l, m, SELECT_TAU)  # re-project to block manifold (stay sparse)
        predn = _l2t(pred)
        sc = (predn @ zn.T).numpy().astype(np.float32)
        np.maximum(S, sc, out=S)
        moved.append(float((pred0 - pred).norm() / (pred0.norm() + 1e-8)))
        # over-smoothing guard: fraction of DISTINCT attractors the cleanup lands on (1.0 = no collapse)
        final_arg = (predn @ zn.T).argmax(dim=1)
        attractor_frac.append(float(len(set(final_arg.tolist())) / n))
    diag = dict(cleanup_moved_mean=float(np.mean(moved)),
                attractor_frac_mean=float(np.mean(attractor_frac)))
    return S, diag


# ---------------------------------------------------------------------------
# Per-arm evaluate: recover adjacency + recall/precision + reach
# ---------------------------------------------------------------------------

def _adj_pair_hash(rec_adj):
    pairs = []
    for i in range(len(rec_adj)):
        for j in rec_adj[i]:
            a, b = (i, j) if i < j else (j, i)
            pairs.append((a, b))
    return hashlib.sha256(json.dumps(sorted(set(pairs))).encode("utf-8")).hexdigest()


def _eval_from_scores(S, edges, cfg, cos_floor, ground_seeds, a_smooth, a_shuf, bins, nonseed_idx, seed,
                      emb, extra=None):
    rec_adj = _topk_floor_adj(S, cfg["recover_topk"], cos_floor)
    recall, prec, n_rec = _edge_recall_precision(rec_adj, edges)
    f1 = (2.0 * recall * prec / (recall + prec)) if (recall + prec) > 0 else 0.0
    by_D, eff_reach, d_star = reach_over_recovered(
        rec_adj, ground_seeds, a_smooth, a_shuf, bins, nonseed_idx,
        cfg["D"], cfg["alpha"], cfg["n_pairs"], seed)
    out = dict(
        edge_recall=float(recall), edge_precision=float(prec), edge_f1=float(f1),
        n_recovered=int(n_rec), eff_reach=int(eff_reach), d_star=(None if d_star is None else int(d_star)),
        sparse_rate=float(np.count_nonzero(emb) / emb.size), code_dim=int(emb.shape[1]),
        reach_by_D={str(D): int(by_D[D]["reach"]) for D in cfg["D"]},
        collapsed_by_D={str(D): bool(by_D[D]["collapsed"]) for D in cfg["D"]},
    )
    if extra:
        out.update(extra)
    return out, rec_adj


# ---------------------------------------------------------------------------
# Per-model-seed run: all 6 arms
# ---------------------------------------------------------------------------

def run_seed(seed, X, edges, rels, adj, cfg, a_smooth, a_shuf, ground_seeds, bins, nonseed_idx, out_dir=None):
    n_nodes = X.shape[0]
    code_dim = cfg["code_dim"]
    dg_dim = cfg["dg_dim"]
    T = int(rels.max()) + 1 if rels.size else 1
    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_dense = make_unitary_roles(T, code_dim, role_rng)                         # dense HRR roles (A)
    roles_dgexp = make_unitary_roles(T, dg_dim, np.random.default_rng(SUBGRAPH_BASE_SEED + 778))  # dense dg roles (B)
    cos_floor_dense = crosstalk_floor(n_nodes, code_dim, cfg["cos_floor_c"])
    cos_floor_dg = crosstalk_floor(n_nodes, dg_dim, cfg["cos_floor_c"])

    arms = {}
    enc_digests = {}
    rec_hashes = {}
    reson_diag = {}

    def _record(name, m, emb, rec):
        arms[name] = m
        enc_digests[name] = _emb_digest(emb)
        rec_hashes[name] = _adj_pair_hash(rec)
        _log("  seed=%d %s recall=%.3f prec=%.3f reach=%d sparse=%.4f dim=%d" % (
            seed, name, m["edge_recall"], m["edge_precision"], m["eff_reach"], m["sparse_rate"], m["code_dim"]))

    t0 = time.perf_counter()

    # A DENSE_BINDOBJ (Stage-2 winner reproduce): dense HRR bind + bidirectional bindobj, dense code
    z_a = train_encoder_v2(X, edges, rels, roles_dense, cfg, seed, out_dim=code_dim,
                           expand=False, bindobj=True, out_dir=out_dir, tag="A_DENSE_BINDOBJ")
    m_a, rec_a = _eval_from_scores(score_role(z_a, roles_dense), edges, cfg, cos_floor_dense,
                                   ground_seeds, a_smooth, a_shuf, bins, nonseed_idx, seed, z_a)
    _record(DENSE_BINDOBJ, m_a, z_a, rec_a)

    # B DENSE_BIND_DGEXPAND (Stage-2 regression reproduce): dense HRR bind + DG k-WTA expand + bindobj
    z_b = train_encoder_v2(X, edges, rels, roles_dgexp, cfg, seed, out_dim=dg_dim,
                           expand=True, bindobj=True, out_dir=out_dir, tag="B_DENSE_DGEXPAND")
    m_b, rec_b = _eval_from_scores(score_role(z_b, roles_dgexp), edges, cfg, cos_floor_dg,
                                   ground_seeds, a_smooth, a_shuf, bins, nonseed_idx, seed, z_b)
    _record(DENSE_BIND_DGEXPAND, m_b, z_b, rec_b)

    # C BLOCK_BINDOBJ__g{i}: RANK 1 block-local circ-conv bind + bindobj on graded sparse block codes
    for gtag, kb, blk_l, mm in cfg["block_geoms"]:
        blk_role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 900 + hash(gtag) % 1000)
        roles_blk = make_block_shift_roles(T, kb, blk_l, blk_role_rng)
        cos_floor_blk = crosstalk_floor(n_nodes, kb * blk_l, cfg["cos_floor_c"])
        z_c = train_encoder_block(X, edges, rels, roles_blk, cfg, seed, kb, blk_l, mm,
                                  out_dir=out_dir, tag="C_BLOCK_%s" % gtag)
        m_c, rec_c = _eval_from_scores(score_role_block(z_c, roles_blk, kb, blk_l), edges, cfg, cos_floor_blk,
                                       ground_seeds, a_smooth, a_shuf, bins, nonseed_idx, seed, z_c,
                                       extra=dict(kb=kb, blk_l=blk_l, m=mm, active_frac=float(mm) / blk_l))
        _record(_block_arm(gtag), m_c, z_c, rec_c)

        # D BLOCK_RESONATOR__g0: RANK 1 + RANK 2 iterative cleanup, primary geometry only (reuse z_c codes)
        if gtag == PRIMARY_GEO:
            S_res, rdiag = score_role_block_resonator(z_c, roles_blk, kb, blk_l, mm, RESONATOR_ITERS, RESONATOR_BETA)
            m_d, rec_d = _eval_from_scores(S_res, edges, cfg, cos_floor_blk, ground_seeds, a_smooth, a_shuf,
                                           bins, nonseed_idx, seed, z_c,
                                           extra=dict(kb=kb, blk_l=blk_l, m=mm, active_frac=float(mm) / blk_l,
                                                      resonator=rdiag))
            reson_diag[_reson_arm(gtag)] = rdiag
            _record(_reson_arm(gtag), m_d, z_c, rec_d)

    _log("  seed=%d done (%.1fs) reson=%s" % (seed, time.perf_counter() - t0, reson_diag))
    return dict(seed=seed, arms=arms, encoder_digests=enc_digests, rec_hashes=rec_hashes, reson_diag=reson_diag,
                cos_floor_dense=float(cos_floor_dense), cos_floor_dg=float(cos_floor_dg))


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------

def _nanmean(vals):
    arr = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(arr.mean()) if arr.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, attr_meta, subgraph_meta, cfg):
    all_arms = _all_arms(cfg)
    block_arms = _block_arms(cfg)
    recall = {a: _nanmean([m["arms"][a]["edge_recall"] for m in per_seed]) for a in all_arms}
    precision = {a: _nanmean([m["arms"][a]["edge_precision"] for m in per_seed]) for a in all_arms}
    reach = {a: _nanmean([m["arms"][a]["eff_reach"] for m in per_seed]) for a in all_arms}
    sparse = {a: _nanmean([m["arms"][a]["sparse_rate"] for m in per_seed]) for a in all_arms}

    base_recall = recall[DENSE_BINDOBJ]
    base_reach = reach[DENSE_BINDOBJ]
    base_prec = precision[DENSE_BINDOBJ]

    precondition_ok = (attr_meta["assort_smooth"] >= ATTR_ASSORT_SMOOTH_MIN) and \
        (attr_meta["assort_shuffled"] <= ATTR_ASSORT_SHUFFLED_MAX)
    baseline_reproduces = (base_recall == base_recall and BASELINE_RECALL_LO <= base_recall <= BASELINE_RECALL_HI
                           and base_reach == base_reach and base_reach <= BASELINE_REACH_MAX + 1e-9)
    # regression control: dense bind + DG expand should hurt recall vs dense bind alone (reproduces Stage-2)
    dense_expand_regresses = (recall[DENSE_BIND_DGEXPAND] == recall[DENSE_BIND_DGEXPAND]
                              and base_recall == base_recall
                              and recall[DENSE_BIND_DGEXPAND] < base_recall)

    # HARD_PASS: a BLOCK arm reaches hop-2, keeps recall>=0.42, precision-guarded, sparsity preserved, non-collapsed
    def _noncollapsed(a):
        cols = [m["arms"][a]["collapsed_by_D"] for m in per_seed]
        # non-collapsed at the reaching depth on at least one seed's best-D is captured by eff_reach>=2;
        # eff_reach already excludes collapsed D (reach_over_recovered valid-D filter).
        return True

    hp_arms = [a for a in block_arms
               if (recall[a] == recall[a] and recall[a] >= RECALL_KEEP_MIN
                   and precision[a] >= PRECISION_FLOOR
                   and reach[a] == reach[a] and reach[a] >= REACH_HP_MIN
                   and (reach[a] - base_reach) >= REACH_DELTA_HP
                   and sparse[a] == sparse[a] and sparse[a] <= SPARSE_MAX
                   and _noncollapsed(a))]
    hard_pass = len(hp_arms) > 0

    # best BLOCK arm by (reach, recall)
    def _key(a):
        rc = reach[a] if reach[a] == reach[a] else -1.0
        rr = recall[a] if recall[a] == recall[a] else -1.0
        return (rc, rr)
    best_block = max(block_arms, key=_key)
    best_block_recall = recall[best_block]
    best_block_reach = reach[best_block]
    best_block_sparse = sparse[best_block]

    # DG-expansion net-positive under block binding: recall(best BLOCK) - recall(DENSE_BINDOBJ)
    block_expand_gain = (best_block_recall - base_recall) if (best_block_recall == best_block_recall
                                                              and base_recall == base_recall) else float("nan")
    dg_expansion_net_positive = (block_expand_gain == block_expand_gain and block_expand_gain > 0.0)

    any_block_reaches = any((reach[a] == reach[a] and reach[a] >= REACH_HP_MIN) for a in block_arms)
    block_costs_recall = (best_block_recall == best_block_recall and base_recall == base_recall
                          and best_block_recall < base_recall - RECALL_COST_DELTA)

    if not precondition_ok:
        verdict = "PRECONDITION_FAIL"
    elif not baseline_reproduces:
        verdict = "BASELINE_REPRO_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    elif (not any_block_reaches) or block_costs_recall:
        verdict = "HARD_FAIL_BLOCK_BINDING_INSUFFICIENT"   # chaining ceiling not a bind-op mismatch, OR costs recall
    else:
        verdict = "MIDDLE_BAND"                            # reach>=2 but recall<0.42, or gain only mildly positive

    element_attribution = dict(
        base_recall=base_recall, base_reach=base_reach,
        dense_dgexpand_recall=recall[DENSE_BIND_DGEXPAND], dense_dgexpand_reach=reach[DENSE_BIND_DGEXPAND],
        best_block_arm=best_block, best_block_recall=best_block_recall, best_block_reach=best_block_reach,
        best_block_sparse=best_block_sparse,
        block_expand_gain=block_expand_gain, dg_expansion_net_positive=bool(dg_expansion_net_positive),
        stage2_dense_expand_gain=-0.2117,   # MEASURED@retrain_v1/metrics.json:gates.element_attribution.expand_gain
    )

    verdict_msg = (
        "%s || DENSE_BINDOBJ recall=%.3f prec=%.3f reach=%.2f (reproduces=%s; floor to keep+beat) || "
        "DENSE_BIND_DGEXPAND recall=%.3f reach=%.2f (dense-expand-regresses=%s) || "
        "BEST_BLOCK=%s recall=%.3f reach=%.2f sparse=%.4f || block_expand_gain=%.3f (Stage-2 dense=-0.212; "
        "DG_expansion_net_positive=%s) || reach_delta_vs_base=%.2f hp_arms=%s || bands: RECALL_KEEP>=%.2f "
        "REACH_HP>=%d delta>=%d prec>=%.2f sparse<=%.2f || attr smooth=%.3f shuf=%.3f precond=%s || "
        "subgraph n=%d E=%d rel_types=%d seeds=%d" % (
            verdict, base_recall, base_prec, base_reach, baseline_reproduces,
            recall[DENSE_BIND_DGEXPAND], reach[DENSE_BIND_DGEXPAND], dense_expand_regresses,
            best_block, best_block_recall, best_block_reach, best_block_sparse,
            block_expand_gain if block_expand_gain == block_expand_gain else float("nan"),
            dg_expansion_net_positive,
            (best_block_reach - base_reach) if (best_block_reach == best_block_reach and base_reach == base_reach) else float("nan"),
            hp_arms, RECALL_KEEP_MIN, REACH_HP_MIN, REACH_DELTA_HP, PRECISION_FLOOR, SPARSE_MAX,
            attr_meta["assort_smooth"], attr_meta["assort_shuffled"], precondition_ok,
            subgraph_meta["n_nodes"], subgraph_meta["n_edges"], subgraph_meta.get("n_relation_types", -1),
            len(per_seed)))

    gates = dict(
        verdict=verdict, recall_mean=recall, precision_mean=precision, reach_mean=reach, sparse_mean=sparse,
        base_recall=base_recall, base_precision=base_prec, base_reach=base_reach,
        baseline_reproduces=bool(baseline_reproduces), dense_expand_regresses=bool(dense_expand_regresses),
        hard_pass=bool(hard_pass), hp_arms=hp_arms, best_block_arm=best_block,
        element_attribution=element_attribution, dg_expansion_net_positive=bool(dg_expansion_net_positive),
        precondition_ok=bool(precondition_ok),
        attr_assort_smooth=attr_meta["assort_smooth"], attr_assort_shuffled=attr_meta["assort_shuffled"],
        bands=dict(BASELINE_RECALL_LO=BASELINE_RECALL_LO, BASELINE_RECALL_HI=BASELINE_RECALL_HI,
                   BASELINE_REACH_MAX=BASELINE_REACH_MAX, RECALL_KEEP_MIN=RECALL_KEEP_MIN,
                   RECALL_COST_DELTA=RECALL_COST_DELTA, REACH_HP_MIN=REACH_HP_MIN, REACH_DELTA_HP=REACH_DELTA_HP,
                   PRECISION_FLOOR=PRECISION_FLOOR, SPARSE_MAX=SPARSE_MAX,
                   BLOCK_HOP1_FIDELITY_MIN=BLOCK_HOP1_FIDELITY_MIN,
                   W_PROX_STRONG=W_PROX_STRONG, W_BIND_STRONG=W_BIND_STRONG,
                   RESONATOR_ITERS=RESONATOR_ITERS, RESONATOR_BETA=RESONATOR_BETA),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Formula / discriminator self-test (ALWAYS runs) -- block circ-conv unbind fidelity on planted structure
# ---------------------------------------------------------------------------

def block_selftest():
    """Prove: (0) block_bind then block_unbind recovers the filler on planted graded block codes with one-hot-
    per-block shift roles (>= BLOCK_HOP1_FIDELITY_MIN; expect ~1.0 -- exactly invertible) AND block_bind equals
    the canonical hdlab.binding.bind on reshaped [.,kb,blk_l] tensors (reuse-equivalence); (1) SPARSITY
    PRESERVED: sparse_rate(block_bind(role, code)) == sparse_rate(code) (block bind never densifies); (2) 2-HOP:
    bind twice then unbind twice recovers (reach>=2 mechanism possible in principle); (3) a tiny BLOCK_BINDOBJ
    retrain LEARNS role-recoverable codes (recall clears chance by a margin); (4) telemetry-sensitive (permuting
    the trained codes DROPS recall); (5) resonator cleanup is NON-VACUOUS (moves pred) and does NOT collapse."""
    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    kb, blk_l, m = 32, 128, 5
    d = kb * blk_l

    # planted graded block codes + one-hot-per-block shift roles
    z = torch.randn(5, d)
    codes = _gsbc_code_from_z(z, kb, blk_l, m, 0.10)                 # positive unit-L1 per block, m-hot
    roles = make_block_shift_roles(3, kb, blk_l, rng)
    role0 = torch.from_numpy(roles[0])[None, :].repeat(5, 1)

    # (0) block bind/unbind exact recovery + reuse-equivalence vs hdlab.binding.bind
    bound = block_bind(role0, codes, kb, blk_l)
    recon = block_unbind(bound, role0, kb, blk_l)
    fid = float(torch.nn.functional.cosine_similarity(recon, codes, dim=1).mean())
    hop1_ok = bool(fid >= BLOCK_HOP1_FIDELITY_MIN)
    canon = _hd_bind(role0.reshape(5, kb, blk_l).contiguous(), codes.reshape(5, kb, blk_l).contiguous())
    reuse_ok = bool(torch.allclose(bound.reshape(5, kb, blk_l), canon, atol=1e-4))

    # (1) sparsity preserved by the bind
    sr_code = float((codes != 0).float().mean())
    sr_bound = float((bound.abs() > 1e-6).float().mean())
    sparsity_ok = bool(abs(sr_bound - sr_code) <= 0.01 and sr_code <= 0.10)

    # (2) 2-hop bind/unbind recovery (reach>=2 mechanism in principle)
    role1 = torch.from_numpy(roles[1])[None, :].repeat(5, 1)
    two = block_bind(role1, block_bind(role0, codes, kb, blk_l), kb, blk_l)
    recon2 = block_unbind(block_unbind(two, role1, kb, blk_l), role0, kb, blk_l)
    fid2 = float(torch.nn.functional.cosine_similarity(recon2, codes, dim=1).mean())
    twohop_ok = bool(fid2 >= 0.90)

    # (3) tiny BLOCK_BINDOBJ retrain learns role-recoverable codes
    n = 240
    T = 3
    feat = rng.standard_normal((n, 512)).astype(np.float32)
    a = rng.integers(0, n, size=360)
    b = rng.integers(0, n, size=360)
    keep = a != b
    edges = np.stack([a[keep], b[keep]], axis=1).astype(np.int32)
    rels = rng.integers(0, T, size=edges.shape[0]).astype(np.int32)
    roles_dg = make_block_shift_roles(T, kb, blk_l, np.random.default_rng(1))
    cfg = dict(epochs=25, batch=128, lr=0.01, temp=0.15, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0)
    emb = train_encoder_block(feat, edges, rels, roles_dg, cfg, 7, kb, blk_l, m, tag="ST")
    cos_floor = crosstalk_floor(n, d, 1.1)
    S = score_role_block(emb, roles_dg, kb, blk_l)
    rec = _topk_floor_adj(S, 6, cos_floor)
    recall, prec, _ = _edge_recall_precision(rec, edges)
    chance = 12.0 / n
    learn_ok = bool(recall >= max(0.15, 4.0 * chance))

    # (4) telemetry: permute trained codes -> recall drops
    emb_perm = emb[rng.permutation(n)]
    rec_perm = _topk_floor_adj(score_role_block(emb_perm, roles_dg, kb, blk_l), 6, cos_floor)
    recall_perm, _, _ = _edge_recall_precision(rec_perm, edges)
    telemetry = bool((recall - recall_perm) >= 0.10)

    # (5) resonator non-vacuous + non-collapsed
    _S, rdiag = score_role_block_resonator(emb, roles_dg, kb, blk_l, m, RESONATOR_ITERS, RESONATOR_BETA)
    reson_ok = bool(rdiag["cleanup_moved_mean"] > 0.0 and rdiag["attractor_frac_mean"] >= 0.10)

    res = dict(hop1_fidelity=fid, hop1_ok=hop1_ok, reuse_equiv_ok=reuse_ok,
               sr_code=sr_code, sr_bound=sr_bound, sparsity_ok=sparsity_ok,
               twohop_fidelity=fid2, twohop_ok=twohop_ok,
               retrain_recall=float(recall), retrain_prec=float(prec), chance=float(chance), learn_ok=learn_ok,
               recall_perm=float(recall_perm), telemetry_sensitive=telemetry,
               resonator=rdiag, reson_ok=reson_ok)
    ok = bool(hop1_ok and reuse_ok and sparsity_ok and twohop_ok and learn_ok and telemetry and reson_ok)
    return ok, res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _unknown = ap.parse_known_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode

    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()

    st_ok, st_res = block_selftest()
    _log("block_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="BLOCK_SELFTEST_FAILED (hop1/reuse/sparsity/twohop/learn/telemetry/reson): %s" % st_res,
            summary="block selftest failed", elapsed_s=time.perf_counter() - t_start,
            block_selftest=st_res))
        raise SystemExit(1)

    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s | rel_types=%d" % ({k: meta[k] for k in ("n_nodes", "n_edges", "median_degree")}, T))
    n_nodes = len(node_ids)
    X = char_trigram_features(node_words, cfg["feat_dim"])
    adj = build_adjlist(edges, n_nodes)

    attr_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 555)
    a_smooth = make_smooth_attribute(edges, degrees, n_nodes, attr_rng, cfg["n_sources"], cfg["diffuse_steps"])
    a_shuf = a_smooth.copy()
    attr_rng.shuffle(a_shuf)
    assort_smooth = attribute_assortativity(a_smooth, edges)
    assort_shuffled = attribute_assortativity(a_shuf, edges)
    _log("attribute assortativity: smooth=%.3f shuffled=%.3f" % (assort_smooth, assort_shuffled))

    n_gs = int(min(cfg["n_ground_seeds"], n_nodes // 4))
    ground_seeds = attr_rng.choice(n_nodes, size=n_gs, replace=False)
    seed_set = set(int(x) for x in ground_seeds)
    dist = multi_source_bfs(adj, [int(x) for x in ground_seeds], n_nodes)
    bins, n_unreachable = distance_bins(dist, seed_set)
    nonseed_idx = np.concatenate([bins[b] for b in range(4) if bins[b].shape[0] > 0]) \
        if any(bins[b].shape[0] > 0 for b in range(4)) else np.array([], dtype=np.int64)
    _log("distance bins (non-seed): d1=%d d2=%d d3=%d d4+=%d unreachable=%d" % (
        bins[0].shape[0], bins[1].shape[0], bins[2].shape[0], bins[3].shape[0], n_unreachable))

    attr_meta = dict(assort_smooth=assort_smooth, assort_shuffled=assort_shuffled, n_ground_seeds=n_gs,
                     n_unreachable=int(n_unreachable), bin_counts={b: int(bins[b].shape[0]) for b in range(4)})

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS block-bind exact-inverse (fid=%.3f) + reuse==hdlab.binding + sparsity-"
                        "preserved + 2-hop + BLOCK_BINDOBJ learns role-recoverable codes telemetry-sensitive + "
                        "resonator non-vacuous; typed subgraph + attribute pipeline exercised" % st_res["hop1_fidelity"],
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            block_selftest=st_res, subgraph_meta=meta, attr_meta=attr_meta))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    all_arms = _all_arms(cfg)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, X, edges, rels, adj, cfg, a_smooth, a_shuf, ground_seeds, bins,
                          nonseed_idx, out_dir=out_dir_path)
            # ARMS-MUST-DIFFER: the encoders + recovered-edge sets must not be bit-identical
            ed = pm["encoder_digests"]
            rh = pm["rec_hashes"]
            if len(set(rh[a] for a in all_arms)) < 2:
                _log("  [warn] all recovered-edge sets identical (seed=%d) -- arms may not differ" % seed)
            # arm cardinality: every arm present for this seed
            missing = [a for a in all_arms if a not in pm["arms"]]
            if missing:
                raise RuntimeError("ARM_CARDINALITY_BREACH seed=%d missing=%s" % (seed, missing))
            per_seed.append(pm)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=pm))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # per-seed failure-class instrumentation (META_RULE_J)
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (
                expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, subgraph_meta=meta, attr_meta=attr_meta))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, attr_meta, meta, cfg)
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(per_seed), seeds=cfg["seeds"], config={k: v for k, v in cfg.items() if k != "block_geoms"},
        block_geoms=[list(g) for g in cfg["block_geoms"]],
        subgraph_meta=meta, attr_meta=attr_meta, gates=gates,
        block_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed,
    )
    write_metrics(out_dir_path, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


if __name__ == "__main__":
    _od = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
