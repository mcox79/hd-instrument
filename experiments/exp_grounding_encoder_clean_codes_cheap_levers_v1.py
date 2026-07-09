"""Stage-1 NO-RETRAIN cheap-lever fix for the encoder role-recovery HARD_FAIL.

Baseline (MEASURED@data/exp_grounding_binding_structured_encoder_multihop_v1/metrics.json):
the binding-structured encoder's LEARNED codes give role-apply (unbind) edge_recall = 0.2819 and
effective reach = 1 -- too noisy to chain typed binding past 1 hop. Diagnosis (landed-VET +
research_encoder_clean_composable_relational_codes_2026-07-09.md): the bind op is lossless on PLANTED
structure; the encoder's LEARNED codes are the weak link. The drill delivered a 4-lever stack and a
near-zero-cost NO-RETRAIN decisive test to resolve the fork:
    (a) codes are just insufficiently SPARSE (cheap post-hoc fix, no retrain), vs
    (b) codes were never trained with a strong-enough structural signal (needs Stage-2 retrain).

THIS cell is STAGE 1 -- the cheap decisive test. It trains the binding encoder ONCE per seed
(reproducing the ~0.28 baseline as the BASELINE_RAW contrast floor), then applies three cheap
NO-RETRAIN levers to the SAME learned codes and re-measures the SAME role-recovery + reach eval:
    LEVER 1 SPARSE       : native-space k-WTA sparsification, sweeping active-fraction a
                           (recovery-vs-sparsity is a sharp PHASE TRANSITION per Donoho-Tanner --
                           CITED@research_encoder_clean_composable_relational_codes_2026-07-09.md S1b;
                           so we SWEEP a to find the knee rather than nudge).
    LEVER 2 SPARSE_ORTHO : + Lowdin-orthonormalized role basis (reduce cross-role unbind crosstalk).
    LEVER 3 RESONATOR    : + iterative soft-attractor cleanup of the bind product toward the codebook
                           (hdlab.iterative_attractor.iterative_cleanup) at a fixed DG-canonical
                           sparsity a_res -- the mechanism built to stop per-hop error compounding.

No expansion recode (DGProjection to higher dim) here: HRR bind structure lives in the native code
space, so a fixed random expansion would break bind(role_r, z_i) ~= z_j without re-establishing it
(a retrain). Native-space k-WTA is the faithful NO-RETRAIN sparsity lever (drill S2.1); DG-expansion +
binding-consistency objective is deferred to Stage-2 retrain (gated on this cell's verdict).

DISCRIMINATOR: role-recovery edge_recall (+ precision, spurious-edge guard) of role-apply unbind on the
LEARNED codes, AND effective multi-hop REACH over the CODE-RECOVERED graph (reach>=2 == typed binding
chains past 1 hop on real codes). HARD_PASS = a cheap lever lifts recall to the chaining band AND
reach>=2 beating the baseline reach=1. HARD_FAIL = no cheap lever moves fidelity -> Stage-2 retrain is
NECESSARY not optional (resolves the fork toward (b)). MIDDLE = partial lift (sparsity helps but under-
delivers; proceed to Stage-2). Both outcomes are gold.

HONESTY FRAMING: REAL-SUBSTRATE multi-hop grounded-attribute propagation on LEARNED codes. NOT language
understanding, NOT grounding solved. The grounded scalar is a synthetic graph-smooth field over the REAL
ConceptNet subgraph (honest stand-in). PASS = a necessary (not sufficient) recipe. Teacher-free, CPU-only,
ASCII-only, no external LM/BGE/network. Reuses the CG'd binding-encoder + reach machinery VERBATIM so the
recall/reach definitions are bit-identical to the baseline this fixes.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (recovered-edge-set hash: lever arms != BASELINE_RAW)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: reach ordering-acc chance floor = 0.5; discriminator is the shuffle-gated, over-smoothing-
#   gated effective REACH + the role-recovery edge_recall vs a reproduced baseline floor, not a closed-form
#   estimator noise floor.
# - baseline_in_band at smoke: BASELINE_RAW recall in [0.20,0.42] (brackets MEASURED 0.2819) AND reach<=1
#   (a genuine floor to beat, NOT a saturated ceiling). else BASELINE_REPRO_FAIL.
# - discriminator survives scale: smoke fires it (baseline reproduces the 0.28/reach-1 floor; the sparsity
#   sweep produces a non-flat recall curve; lever arms differ). SMOKE exercises the SAME arms/branches/sweep
#   as FULL; only n_nodes/epochs/code_dim/feat_dim/seeds scale.
# - HARD_PASS strictly above floor: best-lever recall >= RECALL_HP_MIN AND reach>=2 AND reach_delta>=1 AND
#   precision >= PRECISION_FLOOR (spurious-edge guard) AND non-collapsed/shuffle-gated reach.
# - HP_SCOPE: recall+reach gates apply to the LEVER arms (SPARSE / SPARSE_ORTHO / RESONATOR); BASELINE_RAW is
#   the reproduce-the-floor control (must reproduce, must NOT pass the chaining gate).
# - sweep axis: sparsity a (SPARSITY_SWEEP) for SPARSE + SPARSE_ORTHO; cardinality EXPECTED_N_UNITS=n_seeds,
#   sweep coverage asserted WITHIN each seed unit (len(recall_by_a)==len(SPARSITY_SWEEP)).
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (shuffled empirical null recomputed per run;
#   over-smoothing collapse gate fires; recovery crosstalk floor is codebook-size-aware sqrt(2 ln n / d)).
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
)
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import (  # noqa: E402
    make_smooth_attribute,
    attribute_assortativity,
    multi_source_bfs,
    distance_bins,
    SUBGRAPH_BASE_SEED,
)
# Reuse the baseline cell VERBATIM so recall/reach definitions are bit-identical to what we fix.
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph,
    make_unitary_roles,
    np_hrr_bind,
    score_role,
    score_cosine,
    _topk_floor_adj,
    _edge_recall_precision,
    crosstalk_floor,
    reach_over_recovered,
    train_binding_encoder,
    _l2,
    _emb_digest,
    recover_role_adj,
    ATTR_ASSORT_SMOOTH_MIN,
    ATTR_ASSORT_SHUFFLED_MAX,
    REACH_THRESH,
    MARGIN_FLOOR,
)
from hdlab.iterative_attractor import iterative_cleanup  # noqa: E402

ANCHOR_NAME = "grounding_encoder_clean_codes_cheap_levers_v1"

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME arms/branches/sweep as FULL; only scale differs)
# ---------------------------------------------------------------------------

SPARSITY_SWEEP = [0.02, 0.05, 0.10, 0.20, 0.35, 0.50]  # native-space k-WTA active fraction (phase sweep)
# Resonator operates on the codes' FAIR-BEST (dense) representation: the smoke sparsity sweep shows native-
# space k-WTA MONOTONICALLY degrades role-recovery (it discards distributed HRR structure), so dense (a=1.0)
# is the codes' best operating point. Cleaning already-destroyed sparse codes tests nothing; the resonator is
# the denoising lever and is applied where the binding signal is intact.
A_RES = 1.0                                             # dense codes for the resonator (fair operating point)
RES_MAX_STEPS = 4                                       # iterative-cleanup theta/gamma cap (brain ref ~7-10)
RES_TEMP = 4.0                                          # sqrt(D)-scaled inverse temp (Ramsauer 2021 default)

SELFTEST_CFG = dict(
    seeds=[7],
    n_nodes=400, epochs=10, batch=256, code_dim=64, feat_dim=1024,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_ground_seeds=20, diffuse_steps=8, n_sources=6,
    D=[1, 2, 3], alpha=0.85, recover_topk=8, cos_floor_c=1.1, n_pairs=2000,
)

SMOKE_CFG = dict(
    seeds=[7, 13],
    n_nodes=1800, epochs=45, batch=256, code_dim=128, feat_dim=4096,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_ground_seeds=30, diffuse_steps=10, n_sources=20,
    D=[1, 2, 3, 4], alpha=0.85, recover_topk=8, cos_floor_c=1.1, n_pairs=4000,
)

FULL_CFG = dict(
    seeds=[7, 13, 17],
    n_nodes=5000, epochs=100, batch=512, code_dim=256, feat_dim=8192,
    temp=0.10, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_ground_seeds=80, diffuse_steps=12, n_sources=50,
    D=[1, 2, 3, 4, 5], alpha=0.85, recover_topk=8, cos_floor_c=1.1, n_pairs=6000,
)

# ---------------------------------------------------------------------------
# Pre-registered bands (picked BEFORE the FULL run)
# ---------------------------------------------------------------------------
# Baseline reproduce contract (contrast floor): the SAME binding encoder + role-apply must reproduce the
# MEASURED ~0.28 recall / reach-1 cap. If it does not, contrasts are untrustworthy (BASELINE_REPRO_FAIL).
BASELINE_RECALL_LO = 0.20          # MEASURED@..._multihop_v1/metrics.json:gates.recall_mean.BINDING_UNBIND=0.2819
BASELINE_RECALL_HI = 0.42          # (bracket; smoke-N drift allowed)
BASELINE_REACH_MAX = 1             # the 1-hop cap to beat (baseline_in_band; not a saturated ceiling)

# Best cheap-lever gates (apply to LEVER arms only)
RECALL_HP_MIN = 0.45               # HARD_PASS fidelity: decisive jump from 0.28 (above the 0.40 cosine arm)
RECALL_MIDDLE_MIN = 0.38           # MIDDLE: material lift (>= baseline + ~0.10)
RECALL_HARDFAIL_DELTA = 0.05       # HARD_FAIL if best lever < baseline + this (cheap levers null)
REACH_HP_MIN = 2                   # HARD_PASS: best lever effective reach must extend to hop 2
REACH_DELTA_HP = 1                 # HARD_PASS: reach(best lever) - reach(BASELINE_RAW) >= 1
PRECISION_FLOOR = 0.10             # spurious-edge guard (baseline BIND_UNB precision=0.133 MEASURED)

# Arm names
BASELINE_RAW = "BASELINE_RAW"       # z_bind dense, native unitary roles (reproduces 0.28 / reach 1)
SPARSE = "SPARSE"                   # k-WTA(a), native unitary roles
SPARSE_ORTHO = "SPARSE_ORTHO"       # k-WTA(a), Lowdin-orthonormal roles
RESONATOR = "RESONATOR"             # k-WTA(A_RES), ortho roles, iterative-cleanup readout
LEVER_ARMS = [SPARSE, SPARSE_ORTHO, RESONATOR]


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
# Cheap NO-RETRAIN levers
# ---------------------------------------------------------------------------

def kwta_sparsify(Z, a):
    """Native-space k-WTA: keep top-a fraction of dims by |value| per row, zero the rest, L2-renorm.
    [n,d] -> [n,d]. a>=1.0 returns the dense L2-normed codes (== BASELINE_RAW representation)."""
    Zf = Z.astype(np.float32)
    if a >= 1.0:
        return _l2(Zf).astype(np.float32)
    n, d = Zf.shape
    k = max(1, int(round(float(a) * d)))
    if k >= d:
        return _l2(Zf).astype(np.float32)
    mag = np.abs(Zf)
    thresh = np.partition(mag, d - k, axis=1)[:, d - k][:, None]
    mask = mag >= thresh
    Zs = (Zf * mask).astype(np.float32)
    return _l2(Zs).astype(np.float32)


def orthogonalize_roles(roles_np):
    """Lowdin (symmetric) orthonormalization of the T role vectors: R_ortho = (R R^T)^{-1/2} R.
    Rows become mutually orthonormal -> reduced cross-role unbind crosstalk. [T,d] -> [T,d].
    Trades the exact unit-modulus (unitary) spectrum for orthonormal role vectors; roles stay unit-norm."""
    R = roles_np.astype(np.float64)
    T = R.shape[0]
    if T < 2:
        return _l2(R).astype(np.float32)
    G = R @ R.T                       # [T,T] Gram
    w, V = np.linalg.eigh(G)
    w = np.clip(w, 1e-8, None)
    G_inv_sqrt = (V * (1.0 / np.sqrt(w))) @ V.T
    R_ortho = G_inv_sqrt @ R          # orthonormal rows (up to numerical tol)
    return R_ortho.astype(np.float32)


def score_role_resonator(Z, roles_np, max_steps=RES_MAX_STEPS, temp=RES_TEMP):
    """S[i,j] = max_r cos( cleanup(bind(role_r, z_i)) , z_j ) where cleanup = iterative soft-attractor
    settle of the bind product toward the codebook Z (hdlab iterative_cleanup, alpha=0 self-consistent).
    Sharpens the true-neighbour match. Returns a COSINE-scale matrix so the SAME crosstalk floor + top-k
    rule apply IDENTICALLY to the non-resonator arms (spurious-edge guard = size-aware floor + precision)."""
    z = _l2(Z).astype(np.float32)
    n = z.shape[0]
    T = roles_np.shape[0]
    S = np.full((n, n), -np.inf, dtype=np.float32)
    for r in range(T):
        pred = _l2(np_hrr_bind(roles_np[r], z)).astype(np.float32)
        cleaned = iterative_cleanup(pred, z, temp=temp, max_steps=max_steps, alpha=0.0)["state"]
        cleaned = _l2(np.asarray(cleaned, dtype=np.float32)).astype(np.float32)
        sc = (cleaned @ z.T).astype(np.float32)
        np.maximum(S, sc, out=S)
    return S


def _adj_pair_hash(rec_adj):
    """Deterministic hash of a recovered undirected edge set (ARMS-MUST-DIFFER telemetry)."""
    pairs = []
    for i in range(len(rec_adj)):
        for j in rec_adj[i]:
            a, b = (i, j) if i < j else (j, i)
            pairs.append((a, b))
    pairs = sorted(set(pairs))
    return hashlib.sha256(json.dumps(pairs).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# One recovery arm: score matrix -> adjacency -> recall/precision + reach
# ---------------------------------------------------------------------------

def _eval_recovery_and_reach(S, edges, topk, floor, cfg, ground_seeds, a_smooth, a_shuf, bins,
                             nonseed_idx, seed):
    rec_adj = _topk_floor_adj(S, topk, floor)
    recall, prec, n_rec = _edge_recall_precision(rec_adj, edges)
    f1 = (2.0 * recall * prec / (recall + prec)) if (recall + prec) > 0 else 0.0
    by_D, eff_reach, d_star = reach_over_recovered(
        rec_adj, ground_seeds, a_smooth, a_shuf, bins, nonseed_idx,
        cfg["D"], cfg["alpha"], cfg["n_pairs"], seed)
    out = dict(
        edge_recall=float(recall), edge_precision=float(prec), edge_f1=float(f1),
        n_recovered=int(n_rec), eff_reach=int(eff_reach), d_star=(None if d_star is None else int(d_star)),
        reach_by_D={str(D): int(by_D[D]["reach"]) for D in cfg["D"]},
        collapsed_by_D={str(D): bool(by_D[D]["collapsed"]) for D in cfg["D"]},
        acc_smooth_by_D={str(D): {b: float(by_D[D]["acc_smooth"][b]) for b in range(4)} for D in cfg["D"]},
        margin_by_D={str(D): {b: float(by_D[D]["margin"][b]) for b in range(4)} for D in cfg["D"]},
    )
    return out, rec_adj


# ---------------------------------------------------------------------------
# Per-model-seed run
# ---------------------------------------------------------------------------

def run_seed(seed, X, edges, rels, roles_unitary, adj, cfg, a_smooth, a_shuf, ground_seeds, bins,
             nonseed_idx, out_dir=None):
    d = cfg["code_dim"]
    n_nodes = X.shape[0]
    cos_floor = crosstalk_floor(n_nodes, d, cfg["cos_floor_c"])
    topk = cfg["recover_topk"]

    # --- train the binding encoder ONCE; reuse z_bind for ALL no-retrain levers ---
    t0 = time.perf_counter()
    z_bind = train_binding_encoder(X, edges, rels, roles_unitary, cfg, seed, out_dir=out_dir, tag="BINDING")
    enc_digest = _emb_digest(z_bind)
    _log("  seed=%d binding encoder trained (%.1fs) digest=%s" % (seed, time.perf_counter() - t0, enc_digest[:12]))

    roles_ortho = orthogonalize_roles(roles_unitary)
    # orthonormality diagnostic (off-diagonal Gram mass before/after)
    def _offdiag_mass(R):
        Rn = _l2(R.astype(np.float64))
        G = np.abs(Rn @ Rn.T)
        T = R.shape[0]
        return float((G.sum() - np.trace(G)) / max(1, T * (T - 1)))
    ortho_diag = dict(offdiag_unitary=_offdiag_mass(roles_unitary), offdiag_ortho=_offdiag_mass(roles_ortho))

    arms = {}
    rec_hashes = {}

    # BASELINE_RAW: dense z_bind + native unitary roles (reproduces 0.28 / reach 1)
    S_base = score_role(z_bind, roles_unitary)
    arms[BASELINE_RAW], rec_base = _eval_recovery_and_reach(
        S_base, edges, topk, cos_floor, cfg, ground_seeds, a_smooth, a_shuf, bins, nonseed_idx, seed)
    rec_hashes[BASELINE_RAW] = _adj_pair_hash(rec_base)
    _log("  seed=%d %s recall=%.3f prec=%.3f reach=%d" % (
        seed, BASELINE_RAW, arms[BASELINE_RAW]["edge_recall"], arms[BASELINE_RAW]["edge_precision"],
        arms[BASELINE_RAW]["eff_reach"]))

    # LEVER 1 SPARSE + LEVER 2 SPARSE_ORTHO: sweep sparsity a (phase transition)
    sparse_by_a = {}
    sparse_ortho_by_a = {}
    for ai, a in enumerate(SPARSITY_SWEEP):
        z_sp = kwta_sparsify(z_bind, a)
        m_sp, rec_sp = _eval_recovery_and_reach(
            score_role(z_sp, roles_unitary), edges, topk, cos_floor, cfg,
            ground_seeds, a_smooth, a_shuf, bins, nonseed_idx, seed)
        sparse_by_a[str(a)] = m_sp
        m_spo, rec_spo = _eval_recovery_and_reach(
            score_role(z_sp, roles_ortho), edges, topk, cos_floor, cfg,
            ground_seeds, a_smooth, a_shuf, bins, nonseed_idx, seed)
        sparse_ortho_by_a[str(a)] = m_spo
        if ai == 0:  # keep one representative hash for ARMS-MUST-DIFFER
            rec_hashes[SPARSE] = _adj_pair_hash(rec_sp)
            rec_hashes[SPARSE_ORTHO] = _adj_pair_hash(rec_spo)
        if out_dir is not None:
            try:
                from experiments._cell_heartbeat import emit_heartbeat
                emit_heartbeat(str(out_dir), unit_idx=ai, total_units=len(SPARSITY_SWEEP),
                               elapsed_s=time.perf_counter() - t0)
            except Exception as _hb_e:  # heartbeat best-effort telemetry (SCHEMA-VET 13D)
                _log("  [heartbeat-warn] %s: %s" % (type(_hb_e).__name__, str(_hb_e)[:120]))
        _log("  seed=%d a=%.2f SPARSE recall=%.3f reach=%d | SPARSE_ORTHO recall=%.3f reach=%d" % (
            seed, a, m_sp["edge_recall"], m_sp["eff_reach"], m_spo["edge_recall"], m_spo["eff_reach"]))
    arms[SPARSE] = dict(by_a=sparse_by_a)
    arms[SPARSE_ORTHO] = dict(by_a=sparse_ortho_by_a)

    # LEVER 3 RESONATOR: fixed DG-canonical sparsity + ortho roles + iterative cleanup
    z_res = kwta_sparsify(z_bind, A_RES)
    S_res = score_role_resonator(z_res, roles_ortho)
    arms[RESONATOR], rec_res = _eval_recovery_and_reach(
        S_res, edges, topk, cos_floor, cfg, ground_seeds, a_smooth, a_shuf, bins, nonseed_idx, seed)
    arms[RESONATOR]["a_res"] = A_RES
    rec_hashes[RESONATOR] = _adj_pair_hash(rec_res)
    _log("  seed=%d %s(a=%.2f) recall=%.3f prec=%.3f reach=%d" % (
        seed, RESONATOR, A_RES, arms[RESONATOR]["edge_recall"], arms[RESONATOR]["edge_precision"],
        arms[RESONATOR]["eff_reach"]))

    # sweep-coverage cardinality assert WITHIN the seed unit (META_RULE_H)
    assert len(sparse_by_a) == len(SPARSITY_SWEEP) and len(sparse_ortho_by_a) == len(SPARSITY_SWEEP), (
        "SWEEP_CARDINALITY_BREACH seed=%d got sparse=%d sparse_ortho=%d expected=%d" % (
            seed, len(sparse_by_a), len(sparse_ortho_by_a), len(SPARSITY_SWEEP)))

    return dict(seed=seed, encoder_digest=enc_digest, rec_hashes=rec_hashes, ortho_diag=ortho_diag,
                arms=arms, cos_floor=float(cos_floor))


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------

def _nanmean(vals):
    arr = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(arr.mean()) if arr.shape[0] > 0 else float("nan")


def _flatten_lever_points(per_seed):
    """Return list of (arm_label, recall_mean, precision_mean, reach_mean) averaged over seeds."""
    pts = []
    # SPARSE / SPARSE_ORTHO across the sweep
    for arm in (SPARSE, SPARSE_ORTHO):
        for a in SPARSITY_SWEEP:
            key = str(a)
            recs = [m["arms"][arm]["by_a"][key]["edge_recall"] for m in per_seed]
            precs = [m["arms"][arm]["by_a"][key]["edge_precision"] for m in per_seed]
            reach = [m["arms"][arm]["by_a"][key]["eff_reach"] for m in per_seed]
            pts.append(("%s@a=%.2f" % (arm, a), _nanmean(recs), _nanmean(precs), _nanmean(reach)))
    # RESONATOR (single fixed a)
    recs = [m["arms"][RESONATOR]["edge_recall"] for m in per_seed]
    precs = [m["arms"][RESONATOR]["edge_precision"] for m in per_seed]
    reach = [m["arms"][RESONATOR]["eff_reach"] for m in per_seed]
    pts.append(("%s@a=%.2f" % (RESONATOR, A_RES), _nanmean(recs), _nanmean(precs), _nanmean(reach)))
    return pts


def aggregate_and_verdict(per_seed, attr_meta, subgraph_meta, cfg):
    base_recall = _nanmean([m["arms"][BASELINE_RAW]["edge_recall"] for m in per_seed])
    base_prec = _nanmean([m["arms"][BASELINE_RAW]["edge_precision"] for m in per_seed])
    base_reach = _nanmean([m["arms"][BASELINE_RAW]["eff_reach"] for m in per_seed])

    pts = _flatten_lever_points(per_seed)

    # best lever by recall subject to spurious-edge (precision) guard; fallback to best recall overall
    guarded = [p for p in pts if p[2] >= PRECISION_FLOOR]
    best_pool = guarded if guarded else pts
    best_by_recall = max(best_pool, key=lambda p: (p[1] if p[1] == p[1] else -1.0))
    best_label, best_recall, best_prec, best_recall_reach = best_by_recall
    # reach-extension is only credited to lever points that PRESERVE recall vs baseline: a reach win on
    # codes that are WORSE than the raw baseline is reach-probe noise, not a chaining gain on real codes.
    reach_pool = [p for p in best_pool
                  if (p[1] == p[1] and base_recall == base_recall and p[1] >= base_recall - 0.02)]
    if reach_pool:
        best_by_reach = max(reach_pool, key=lambda p: (p[3] if p[3] == p[3] else -1.0))
        reach_best_label, reach_best_recall, reach_best_prec, best_reach = best_by_reach
    else:
        reach_best_label, reach_best_recall, reach_best_prec, best_reach = "none_preserves_recall", float("nan"), float("nan"), base_reach
    reach_delta = best_reach - base_reach if (base_reach == base_reach and best_reach == best_reach) else float("nan")

    # attribute smoothness precondition
    precondition_ok = (attr_meta["assort_smooth"] >= ATTR_ASSORT_SMOOTH_MIN) and \
        (attr_meta["assort_shuffled"] <= ATTR_ASSORT_SHUFFLED_MAX)

    # baseline reproduce contract (contrast floor)
    baseline_reproduces = (base_recall == base_recall and BASELINE_RECALL_LO <= base_recall <= BASELINE_RECALL_HI
                           and base_reach == base_reach and base_reach <= BASELINE_REACH_MAX + 1e-9)

    # HARD_PASS: a lever point that BOTH lifts recall to the chaining band AND chains reach>=2
    hp_points = [p for p in best_pool
                 if (p[1] == p[1] and p[1] >= RECALL_HP_MIN and p[2] >= PRECISION_FLOOR
                     and p[3] == p[3] and p[3] >= REACH_HP_MIN and (p[3] - base_reach) >= REACH_DELTA_HP)]
    hard_pass = len(hp_points) > 0

    material_lift = (best_recall == best_recall) and (best_recall >= RECALL_MIDDLE_MIN)
    reach_extends = (best_reach == best_reach) and (best_reach >= REACH_HP_MIN)
    cheap_null = ((best_recall == best_recall) and base_recall == base_recall
                  and best_recall < base_recall + RECALL_HARDFAIL_DELTA
                  and (best_reach == best_reach) and best_reach <= BASELINE_REACH_MAX + 1e-9)

    if not precondition_ok:
        verdict = "PRECONDITION_FAIL"
    elif not baseline_reproduces:
        verdict = "BASELINE_REPRO_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    elif material_lift or reach_extends:
        verdict = "MIDDLE_BAND"                    # sparsity partially helps; Stage-2 retrain indicated
    elif cheap_null:
        verdict = "HARD_FAIL_CHEAP_LEVERS_INSUFFICIENT"   # resolves the fork -> Stage-2 retrain NECESSARY
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s || BASELINE_RAW recall=%.3f prec=%.3f reach=%.2f (reproduces=%s, floor to beat) || "
        "BEST_RECALL_LEVER=%s recall=%.3f prec=%.3f | BEST_REACH_LEVER=%s reach=%.2f recall=%.3f "
        "reach_delta_vs_base=%s || bands: RECALL_HP>=%.2f REACH_HP>=%d delta>=%d prec_floor>=%.2f || "
        "attr_assort smooth=%.3f shuf=%.3f precond=%s || subgraph n=%d E=%d n_rel_types=%d seeds=%d" % (
            verdict, base_recall, base_prec, base_reach, baseline_reproduces,
            best_label, best_recall, best_prec, reach_best_label, best_reach, reach_best_recall,
            ("%.2f" % reach_delta) if reach_delta == reach_delta else "nan",
            RECALL_HP_MIN, REACH_HP_MIN, REACH_DELTA_HP, PRECISION_FLOOR,
            attr_meta["assort_smooth"], attr_meta["assort_shuffled"], precondition_ok,
            subgraph_meta["n_nodes"], subgraph_meta["n_edges"], subgraph_meta.get("n_relation_types", -1),
            len(per_seed)))

    gates = dict(
        verdict=verdict,
        base_recall=base_recall, base_precision=base_prec, base_reach=base_reach,
        baseline_reproduces=bool(baseline_reproduces),
        best_recall_label=best_label, best_recall=best_recall, best_recall_precision=best_prec,
        best_reach_label=reach_best_label, best_reach=best_reach, best_reach_recall=reach_best_recall,
        reach_delta_vs_base=reach_delta, hard_pass=bool(hard_pass), precondition_ok=bool(precondition_ok),
        lever_points={p[0]: dict(recall=p[1], precision=p[2], reach=p[3]) for p in pts},
        attr_assort_smooth=attr_meta["assort_smooth"], attr_assort_shuffled=attr_meta["assort_shuffled"],
        bands=dict(BASELINE_RECALL_LO=BASELINE_RECALL_LO, BASELINE_RECALL_HI=BASELINE_RECALL_HI,
                   BASELINE_REACH_MAX=BASELINE_REACH_MAX, RECALL_HP_MIN=RECALL_HP_MIN,
                   RECALL_MIDDLE_MIN=RECALL_MIDDLE_MIN, RECALL_HARDFAIL_DELTA=RECALL_HARDFAIL_DELTA,
                   REACH_HP_MIN=REACH_HP_MIN, REACH_DELTA_HP=REACH_DELTA_HP, PRECISION_FLOOR=PRECISION_FLOOR,
                   SPARSITY_SWEEP=SPARSITY_SWEEP, A_RES=A_RES),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Discriminator + lever self-test (ALWAYS runs)
# ---------------------------------------------------------------------------

def lever_selftest():
    """Prove on PLANTED binding structure: (0) kwta_sparsify hits target sparsity; (1) orthogonalize_roles
    yields near-orthonormal rows (off-diagonal Gram mass drops); (2) on a planted typed chain, the RESONATOR
    readout recovers role-apply edges at recall >= raw score_role AND >= 0.5 (mechanism fires); (3) telemetry-
    sensitive: permuting the codes DROPS resonator recall."""
    rng = np.random.default_rng(0)
    d = 256
    n = 500
    T = 3

    # (0) sparsity target
    Zr = rng.standard_normal((n, d)).astype(np.float32)
    for a in (0.05, 0.10, 0.25):
        zs = kwta_sparsify(Zr, a)
        rate = float(np.count_nonzero(zs) / zs.size)
        assert abs(rate - a) <= 0.02, "kwta sparsity off: a=%.2f rate=%.3f" % (a, rate)

    # (1) orthonormalization reduces off-diagonal Gram mass
    roles = make_unitary_roles(T, d, rng)
    ro = orthogonalize_roles(roles)
    def _off(R):
        Rn = _l2(R.astype(np.float64)); G = np.abs(Rn @ Rn.T)
        return float((G.sum() - np.trace(G)) / (T * (T - 1)))
    off_u, off_o = _off(roles), _off(ro)
    ortho_ok = bool(off_o <= off_u + 1e-6 and off_o < 0.05)

    # (2) planted typed chain: z_{k+1} = bind(role_r, z_k) + noise
    z = np.zeros((n, d), dtype=np.float32)
    z[0] = rng.standard_normal(d)
    chain_edges = []
    for k in range(1, n):
        r = int(rng.integers(0, T))
        z[k] = np_hrr_bind(roles[r], z[k - 1:k])[0] + 0.05 * rng.standard_normal(d).astype(np.float32)
        chain_edges.append((k - 1, k))
    z = _l2(z).astype(np.float32)
    edges = np.array(chain_edges, dtype=np.int32)
    cos_floor = crosstalk_floor(n, d, 1.1)

    rec_raw = _topk_floor_adj(score_role(z, roles), 6, cos_floor)
    rec_res = _topk_floor_adj(score_role_resonator(z, ro), 6, cos_floor)
    recall_raw, _, _ = _edge_recall_precision(rec_raw, edges)
    recall_res, _, _ = _edge_recall_precision(rec_res, edges)
    resonator_fires = bool(recall_res >= 0.5 and recall_res >= recall_raw - 1e-6)

    # (3) telemetry: permute codes -> resonator recall drops
    zperm = z[rng.permutation(n)]
    rec_res_perm = _topk_floor_adj(score_role_resonator(zperm, ro), 6, cos_floor)
    recall_res_perm, _, _ = _edge_recall_precision(rec_res_perm, edges)
    telemetry = bool((recall_res - recall_res_perm) >= 0.25)

    res = dict(off_unitary=off_u, off_ortho=off_o, ortho_ok=ortho_ok,
               recall_raw=float(recall_raw), recall_res=float(recall_res), resonator_fires=resonator_fires,
               recall_res_perm=float(recall_res_perm), telemetry_sensitive=telemetry)
    ok = bool(ortho_ok and resonator_fires and telemetry)
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

    # ---- discriminator + lever self-test (ALWAYS) ----
    st_ok, st_res = lever_selftest()
    _log("lever_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="LEVER_SELFTEST_FAILED (ortho/resonator/telemetry): %s" % st_res,
            summary="lever selftest failed", elapsed_s=time.perf_counter() - t_start,
            lever_selftest=st_res))
        raise SystemExit(1)

    # ---- load typed real ConceptNet subgraph ----
    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s | rel_types=%d" % (
        {k: meta[k] for k in ("n_nodes", "n_edges", "median_degree")}, T))
    n_nodes = len(node_ids)
    X = char_trigram_features(node_words, cfg["feat_dim"])
    adj = build_adjlist(edges, n_nodes)

    # ---- graph-smooth grounded attribute + shuffled control + ground seeds + distance bins ----
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

    # ---- fixed unitary role codebook (one per relation type) ----
    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_unitary = make_unitary_roles(T, cfg["code_dim"], role_rng)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS kwta/ortho/resonator levers + planted-structure recovery telemetry-"
                        "sensitive; typed subgraph + attribute pipeline exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            lever_selftest=st_res, subgraph_meta=meta, attr_meta=attr_meta))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, X, edges, rels, roles_unitary, adj, cfg, a_smooth, a_shuf,
                          ground_seeds, bins, nonseed_idx, out_dir=out_dir_path)
            # ARMS-MUST-DIFFER: lever recovered-edge sets must differ from BASELINE_RAW
            rh = pm["rec_hashes"]
            for lv in LEVER_ARMS:
                if rh.get(lv) == rh.get(BASELINE_RAW):
                    _log("  [warn] recovered edges identical for %s and %s (seed=%d)" % (
                        lv, BASELINE_RAW, seed))
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
        n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg,
        subgraph_meta=meta, attr_meta=attr_meta, gates=gates,
        lever_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed,
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
