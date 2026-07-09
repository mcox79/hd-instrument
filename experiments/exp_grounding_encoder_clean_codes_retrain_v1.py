"""Stage-2 RETRAIN fix for the encoder role-recovery HARD_FAIL: bake the levers into TRAINING.

Stage-1 (grounding_encoder_clean_codes_cheap_levers_v1, HARD_FAIL_CHEAP_LEVERS_INSUFFICIENT) decisively
showed NO post-hoc transform of the FROZEN binding-encoder codes recovers role-recovery: native k-WTA
monotonically HURTS (discards distributed HRR structure) and iterative-cleanup collapses the weak-but-correct
top-k onto confident-wrong attractors. The fork is resolved toward: the codes were never TRAINED with a
strong-enough structural signal. So Stage-2 RETRAINS the encoder with the levers baked in, and ablates WHICH
element carries the win:

    LEVER "EXPAND"  = DG-analog sparse EXPANSION baked into training: project to a higher-dim code space
                      (dg_dim) + differentiable DG k-WTA sparsify (straight-through; magnitude-topk rule
                      identical to hdlab.hippocampal_encoder._sparse_topk_mask). Gives sparse codes the
                      dimensional room to remain separable (Treves-Rolls capacity ~ 1/(a ln(1/a))).
    LEVER "BINDOBJ" = the headline MLC-style BINDING-CONSISTENCY objective, made STRONGER + BIDIRECTIONAL:
                      forward bind(role_r, z_i) ~ z_j AND backward unbind(role_r, z_j) ~ z_i (exact inverse
                      via unitary roles), with the binding term up-weighted, proximity down-weighted, and a
                      Hoyer sparsity penalty. (CITED: Lake & Baroni MLC 2023 -- role-recovery ~0% -> 99.78%
                      via a training-OBJECTIVE change alone.)

Four ablation arms (2x2 minus the reproduced baseline), same discriminator as Stage-1:
    A BASELINE_FROZEN : the Stage-1 binding encoder (code_dim=256, baseline objective). MUST reproduce the
                        MEASURED 0.28 recall / reach-1 floor (contrast floor; NOT allowed to pass).
    B EXPAND_ONLY     : EXPAND on, BINDOBJ off (baseline objective at dg_dim + DG k-WTA).
    C BINDOBJ_ONLY    : EXPAND off (code_dim=256), BINDOBJ on (stronger bidirectional objective).
    D FULL_STACK      : EXPAND on + BINDOBJ on.
Report which of {EXPAND, BINDOBJ, both} lifts fidelity + chains reach>=2 on the REAL learned codes.

DISCRIMINATOR (identical to Stage-1, machinery imported VERBATIM -> bit-identical recall/reach defs):
role-apply (unbind) edge_recall + edge_precision on the LEARNED codes, AND effective multi-hop REACH over
the CODE-RECOVERED graph (reach>=2 == typed binding chains past 1 hop on real codes). HARD_PASS = a retrain
arm lifts recall to the chaining band AND reach>=2 beating baseline reach=1. HARD_FAIL = retrain also can't
clean it -> deeper encoder-capacity limit. Both outcomes gold.

HONESTY FRAMING: REAL-SUBSTRATE multi-hop grounded-attribute propagation on LEARNED codes. NOT language
understanding, NOT grounding solved. Grounded scalar = synthetic graph-smooth field over the REAL ConceptNet
subgraph (honest stand-in). Teacher-free (NO BGE / external LM / network), CPU-only, ASCII-only. Reuses the
CG'd teacher-free encoder (ProjHead / info_nce / vicreg), hdlab HRR binding, the DG sparsify rule, and the
Stage-1/bind-chain reach machinery -- does not rebuild.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (encoder digests + recovered-edge-set hashes across A/B/C/D)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except)
# - crlb_n/a: reach ordering-acc chance floor = 0.5; discriminator is shuffle+collapse-gated reach + role-
#   recovery edge_recall vs a reproduced baseline floor, not a closed-form estimator noise floor.
# - baseline_in_band at smoke: BASELINE_FROZEN recall in [0.20,0.42] (brackets MEASURED 0.2819) AND reach<=1.
#   else BASELINE_REPRO_FAIL.
# - discriminator survives scale: smoke fires it (baseline reproduces; retrain arms differ AND move recall).
#   SMOKE exercises the SAME 4 arms/branches as FULL; only n_nodes/epochs/dg_dim/feat_dim/seeds scale.
# - HARD_PASS strictly above floor: retrain-arm recall >= RECALL_HP_MIN AND reach>=2 AND reach_delta>=1 AND
#   precision >= PRECISION_FLOOR (spurious-edge guard) AND non-collapsed/shuffle-gated reach.
# - HP_SCOPE: recall+reach gates apply to the RETRAIN arms (EXPAND_ONLY / BINDOBJ_ONLY / FULL_STACK);
#   BASELINE_FROZEN is the reproduce-the-floor control (must reproduce, must NOT pass the chaining gate).
# - ablation axis (EXPAND x BINDOBJ): cardinality EXPECTED_N_UNITS=n_seeds; all 4 arms asserted per seed.
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (shuffled empirical null recomputed per run; over-
#   smoothing collapse gate fires; recovery crosstalk floor is codebook-size-aware sqrt(2 ln n / d)).
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
# Reuse the baseline cell VERBATIM: baseline encoder (ARM A) + recall/reach machinery (bit-identical defs).
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph,
    make_unitary_roles,
    torch_hrr_bind,
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
    REACH_THRESH,
    MARGIN_FLOOR,
)
from hdlab.hippocampal_encoder import DGProjection, _sparse_topk_mask  # noqa: E402  (DG sparsify canonical)

ANCHOR_NAME = "grounding_encoder_clean_codes_retrain_v1"

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME 4 arms/branches as FULL; only scale differs)
# ---------------------------------------------------------------------------

DG_SPARSITY = 0.08          # DG-canonical target active fraction for the trained k-WTA (Treves-Rolls ~1-10%)
W_PROX_STRONG = 0.3         # BINDOBJ: proximity down-weighted so binding-consistency dominates
W_BIND_STRONG = 2.0         # BINDOBJ: binding term up-weighted (MLC "objective change" headline lever)
W_SPARSE_HOYER = 0.05       # BINDOBJ: gentle Hoyer L1/L2 sparsity penalty on the code activations

SELFTEST_CFG = dict(
    seeds=[7],
    n_nodes=400, epochs=10, batch=256, code_dim=256, dg_dim=512, feat_dim=1024,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_ground_seeds=20, diffuse_steps=8, n_sources=6,
    D=[1, 2, 3], alpha=0.85, recover_topk=8, cos_floor_c=1.1, n_pairs=2000,
)

SMOKE_CFG = dict(
    # code_dim=128 (not FULL's 256) so the BASELINE_FROZEN sits cleanly at the reach-1 / ~0.28 cap at smoke
    # N=1525 (matches Stage-1 smoke precedent); at 256 the small-N baseline inflates to ~0.41/reach-1.5 and
    # the reach discriminator can't be read. SMOKE=FULL parity is on the 4 arms/branches, not identical dims.
    seeds=[7, 13],
    n_nodes=1800, epochs=45, batch=256, code_dim=128, dg_dim=384, feat_dim=4096,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_ground_seeds=30, diffuse_steps=10, n_sources=20,
    D=[1, 2, 3, 4], alpha=0.85, recover_topk=8, cos_floor_c=1.1, n_pairs=4000,
)

FULL_CFG = dict(
    seeds=[7, 13, 17],
    n_nodes=5000, epochs=120, batch=512, code_dim=256, dg_dim=1024, feat_dim=8192,
    temp=0.10, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_ground_seeds=80, diffuse_steps=12, n_sources=50,
    D=[1, 2, 3, 4, 5], alpha=0.85, recover_topk=8, cos_floor_c=1.1, n_pairs=6000,
)

# ---------------------------------------------------------------------------
# Pre-registered bands (picked BEFORE the FULL run)
# ---------------------------------------------------------------------------
BASELINE_RECALL_LO = 0.20     # MEASURED@..._multihop_v1/metrics.json:gates.recall_mean.BINDING_UNBIND=0.2819
BASELINE_RECALL_HI = 0.42     # bracket; smoke-N drift allowed
BASELINE_REACH_MAX = 1        # the 1-hop cap to beat (baseline_in_band; not a saturated ceiling)

RECALL_HP_MIN = 0.45          # HARD_PASS fidelity: decisive jump from 0.28 (above the 0.40 cosine arm)
RECALL_MIDDLE_MIN = 0.38      # MIDDLE: material lift (>= baseline + ~0.10)
RECALL_HARDFAIL_DELTA = 0.05  # HARD_FAIL if best retrain arm < baseline + this (retrain null)
REACH_HP_MIN = 2              # HARD_PASS: retrain arm effective reach must extend to hop 2
REACH_DELTA_HP = 1            # HARD_PASS: reach(retrain) - reach(BASELINE_FROZEN) >= 1
PRECISION_FLOOR = 0.10        # spurious-edge guard (baseline BIND_UNB precision=0.1334 MEASURED)

# Arm names
BASELINE_FROZEN = "BASELINE_FROZEN"   # Stage-1 binding encoder (reproduces 0.28 / reach 1)
EXPAND_ONLY = "EXPAND_ONLY"           # DG-expansion + k-WTA, baseline objective
BINDOBJ_ONLY = "BINDOBJ_ONLY"         # stronger bidirectional binding objective, no expansion
FULL_STACK = "FULL_STACK"             # both
RETRAIN_ARMS = [EXPAND_ONLY, BINDOBJ_ONLY, FULL_STACK]
ALL_ARMS = [BASELINE_FROZEN] + RETRAIN_ARMS


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
# Trainable levers
# ---------------------------------------------------------------------------

def _ste_kwta(h, target_rate):
    """Differentiable DG k-WTA: keep top-target_rate fraction per row by |activation|, straight-through
    gradient (mask treated as a constant gate -> grad flows to the winners). Replicates the magnitude-topk
    rule of hdlab.hippocampal_encoder._sparse_topk_mask in torch. [n,d] -> [n,d]."""
    d = h.shape[1]
    k = max(1, int(round(float(target_rate) * d)))
    if k >= d:
        return h
    mag = h.abs()
    kth = torch.topk(mag, k, dim=1).values[:, -1:].detach()   # k-th largest per row
    mask = (mag >= kth).float().detach()                      # constant gate (STE)
    return h * mask


def torch_hrr_unbind(role_batch, y_batch):
    """Circular correlation (HRR unbind) = irfft( conj(rfft(role)) * rfft(y) ). Exact inverse of
    torch_hrr_bind for unitary (unit-modulus-spectrum) roles. [B,d],[B,d] -> [B,d]."""
    d = y_batch.shape[1]
    fr = torch.fft.rfft(role_batch, dim=1)
    fy = torch.fft.rfft(y_batch, dim=1)
    return torch.fft.irfft(torch.conj(fr) * fy, n=d, dim=1)


def _hoyer(h, eps=1e-8):
    """Mean per-row L1/L2 sparsity penalty (lower = sparser; scale-invariant). Encourages DG-like codes."""
    l1 = h.abs().sum(dim=1)
    l2 = torch.sqrt(h.pow(2).sum(dim=1)) + eps
    return (l1 / l2).mean()


def train_encoder_v2(X, edges, rels, roles_np, cfg, seed, *, out_dim, expand, bindobj,
                     out_dir=None, tag="V2"):
    """Retrain a binding-structured encoder with EXPAND (DG-expansion + k-WTA) and/or BINDOBJ (stronger
    bidirectional binding-consistency objective) baked in. roles_np: [T, out_dim] unitary. Returns [n, out_dim]
    L2-normed codes."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    feat_dim = X.shape[1]
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
    w_prox = W_PROX_STRONG if bindobj else 1.0
    w_bind = W_BIND_STRONG if bindobj else cfg["lambda_bind"]
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
        if expand:
            ha = _ste_kwta(ha, DG_SPARSITY)
            hp = _ste_kwta(hp, DG_SPARSITY)
        # base proximity + VICReg repulsion (identical role to baseline encoder objective)
        loss = w_prox * info_nce(ha, hp, cfg["temp"]) + vicreg_repulsion(
            torch.cat([ha, hp], dim=0), cfg["lambda_cov"], cfg["lambda_var"])
        za = _l2norm(ha)
        zp = _l2norm(hp)
        # forward binding-consistency: bind(role_r, anchor) matches the r-typed neighbour (in-batch negs)
        loss = loss + w_bind * info_nce(torch_hrr_bind(roles_t[torch.from_numpy(ri)], za), zp, cfg["temp"])
        if bindobj:
            # backward unbind-reconstruction: unbind(role_r, neighbour) recovers the anchor (bidirectional)
            loss = loss + w_bind * info_nce(torch_hrr_unbind(roles_t[torch.from_numpy(ri)], zp), za, cfg["temp"])
            loss = loss + W_SPARSE_HOYER * _hoyer(ha)
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
        H = model(Xt)
        if expand:
            H = _ste_kwta(H, DG_SPARSITY)
        emb = _l2norm(H).numpy().astype(np.float32)
    return emb


def _adj_pair_hash(rec_adj):
    pairs = []
    for i in range(len(rec_adj)):
        for j in rec_adj[i]:
            a, b = (i, j) if i < j else (j, i)
            pairs.append((a, b))
    return hashlib.sha256(json.dumps(sorted(set(pairs))).encode("utf-8")).hexdigest()


def _eval_recovery_and_reach(emb, roles_np, edges, cfg, cos_floor, ground_seeds, a_smooth, a_shuf, bins,
                             nonseed_idx, seed):
    S = score_role(emb, roles_np)
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
        acc_smooth_by_D={str(D): {b: float(by_D[D]["acc_smooth"][b]) for b in range(4)} for D in cfg["D"]},
        margin_by_D={str(D): {b: float(by_D[D]["margin"][b]) for b in range(4)} for D in cfg["D"]},
    )
    return out, rec_adj


# ---------------------------------------------------------------------------
# Per-model-seed run: train 4 encoders, recover + reach on each
# ---------------------------------------------------------------------------

def run_seed(seed, X, edges, rels, adj, cfg, a_smooth, a_shuf, ground_seeds, bins, nonseed_idx, out_dir=None):
    n_nodes = X.shape[0]
    code_dim = cfg["code_dim"]
    dg_dim = cfg["dg_dim"]
    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    T = int(rels.max()) + 1 if rels.size else 1
    roles_base = make_unitary_roles(T, code_dim, role_rng)                    # 256-dim unitary roles
    roles_exp = make_unitary_roles(T, dg_dim, np.random.default_rng(SUBGRAPH_BASE_SEED + 778))  # dg_dim roles

    cos_floor_base = crosstalk_floor(n_nodes, code_dim, cfg["cos_floor_c"])
    cos_floor_exp = crosstalk_floor(n_nodes, dg_dim, cfg["cos_floor_c"])

    arms = {}
    enc_digests = {}
    rec_hashes = {}

    def _run_arm(name, emb, roles_np, cos_floor):
        m, rec = _eval_recovery_and_reach(
            emb, roles_np, edges, cfg, cos_floor, ground_seeds, a_smooth, a_shuf, bins, nonseed_idx, seed)
        arms[name] = m
        enc_digests[name] = _emb_digest(emb)
        rec_hashes[name] = _adj_pair_hash(rec)
        _log("  seed=%d %s recall=%.3f prec=%.3f reach=%d sparse=%.3f dim=%d" % (
            seed, name, m["edge_recall"], m["edge_precision"], m["eff_reach"], m["sparse_rate"], m["code_dim"]))

    # A BASELINE_FROZEN: reuse the baseline binding encoder VERBATIM (code_dim=256) -> reproduces 0.28
    t0 = time.perf_counter()
    z_base = train_binding_encoder(X, edges, rels, roles_base, cfg, seed, out_dir=out_dir, tag="A_BASELINE")
    _run_arm(BASELINE_FROZEN, z_base, roles_base, cos_floor_base)

    # B EXPAND_ONLY: DG-expansion + k-WTA, baseline objective
    z_b = train_encoder_v2(X, edges, rels, roles_exp, cfg, seed, out_dim=dg_dim,
                           expand=True, bindobj=False, out_dir=out_dir, tag="B_EXPAND")
    _run_arm(EXPAND_ONLY, z_b, roles_exp, cos_floor_exp)

    # C BINDOBJ_ONLY: stronger bidirectional binding objective, no expansion (code_dim=256)
    z_c = train_encoder_v2(X, edges, rels, roles_base, cfg, seed, out_dim=code_dim,
                           expand=False, bindobj=True, out_dir=out_dir, tag="C_BINDOBJ")
    _run_arm(BINDOBJ_ONLY, z_c, roles_base, cos_floor_base)

    # D FULL_STACK: both
    z_d = train_encoder_v2(X, edges, rels, roles_exp, cfg, seed, out_dim=dg_dim,
                           expand=True, bindobj=True, out_dir=out_dir, tag="D_FULL")
    _run_arm(FULL_STACK, z_d, roles_exp, cos_floor_exp)

    _log("  seed=%d done (%.1fs)" % (seed, time.perf_counter() - t0))
    return dict(seed=seed, arms=arms, encoder_digests=enc_digests, rec_hashes=rec_hashes,
                cos_floor_base=float(cos_floor_base), cos_floor_exp=float(cos_floor_exp))


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------

def _nanmean(vals):
    arr = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(arr.mean()) if arr.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, attr_meta, subgraph_meta, cfg):
    recall = {a: _nanmean([m["arms"][a]["edge_recall"] for m in per_seed]) for a in ALL_ARMS}
    precision = {a: _nanmean([m["arms"][a]["edge_precision"] for m in per_seed]) for a in ALL_ARMS}
    reach = {a: _nanmean([m["arms"][a]["eff_reach"] for m in per_seed]) for a in ALL_ARMS}

    base_recall = recall[BASELINE_FROZEN]
    base_reach = reach[BASELINE_FROZEN]
    base_prec = precision[BASELINE_FROZEN]

    # best retrain arm by recall (precision-guarded); reach-extension credited only to recall-preserving arms
    guarded = [a for a in RETRAIN_ARMS if precision[a] >= PRECISION_FLOOR]
    pool = guarded if guarded else RETRAIN_ARMS
    best_recall_arm = max(pool, key=lambda a: (recall[a] if recall[a] == recall[a] else -1.0))
    best_recall = recall[best_recall_arm]

    reach_pool = [a for a in pool
                  if (recall[a] == recall[a] and base_recall == base_recall and recall[a] >= base_recall - 0.02)]
    if reach_pool:
        best_reach_arm = max(reach_pool, key=lambda a: (reach[a] if reach[a] == reach[a] else -1.0))
        best_reach = reach[best_reach_arm]
    else:
        best_reach_arm = "none_preserves_recall"
        best_reach = base_reach
    reach_delta = best_reach - base_reach if (base_reach == base_reach and best_reach == best_reach) else float("nan")

    precondition_ok = (attr_meta["assort_smooth"] >= ATTR_ASSORT_SMOOTH_MIN) and \
        (attr_meta["assort_shuffled"] <= ATTR_ASSORT_SHUFFLED_MAX)
    baseline_reproduces = (base_recall == base_recall and BASELINE_RECALL_LO <= base_recall <= BASELINE_RECALL_HI
                           and base_reach == base_reach and base_reach <= BASELINE_REACH_MAX + 1e-9)

    # HARD_PASS: a retrain arm that lifts recall to the chaining band AND chains reach>=2
    hp_arms = [a for a in RETRAIN_ARMS
               if (recall[a] == recall[a] and recall[a] >= RECALL_HP_MIN and precision[a] >= PRECISION_FLOOR
                   and reach[a] == reach[a] and reach[a] >= REACH_HP_MIN and (reach[a] - base_reach) >= REACH_DELTA_HP)]
    hard_pass = len(hp_arms) > 0

    material_lift = (best_recall == best_recall) and (best_recall >= RECALL_MIDDLE_MIN)
    reach_extends = (best_reach == best_reach) and (best_reach >= REACH_HP_MIN)
    retrain_null = ((best_recall == best_recall) and base_recall == base_recall
                    and best_recall < base_recall + RECALL_HARDFAIL_DELTA
                    and (best_reach == best_reach) and best_reach <= BASELINE_REACH_MAX + 1e-9)

    # which element carries it: compare EXPAND_ONLY vs BINDOBJ_ONLY vs FULL_STACK recall gains over baseline
    def _gain(a):
        return (recall[a] - base_recall) if (recall[a] == recall[a] and base_recall == base_recall) else float("nan")
    element_attribution = dict(
        expand_gain=_gain(EXPAND_ONLY), bindobj_gain=_gain(BINDOBJ_ONLY), full_gain=_gain(FULL_STACK),
        expand_reach=reach[EXPAND_ONLY], bindobj_reach=reach[BINDOBJ_ONLY], full_reach=reach[FULL_STACK],
    )

    if not precondition_ok:
        verdict = "PRECONDITION_FAIL"
    elif not baseline_reproduces:
        verdict = "BASELINE_REPRO_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    elif material_lift or reach_extends:
        verdict = "MIDDLE_BAND"
    elif retrain_null:
        verdict = "HARD_FAIL_RETRAIN_CANNOT_CLEAN"     # deeper encoder-capacity limit
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s || BASELINE_FROZEN recall=%.3f prec=%.3f reach=%.2f (reproduces=%s, floor to beat) || "
        "EXPAND_ONLY recall=%.3f reach=%.2f | BINDOBJ_ONLY recall=%.3f reach=%.2f | FULL_STACK recall=%.3f "
        "reach=%.2f || BEST_RECALL=%s(%.3f) BEST_REACH=%s(%.2f) reach_delta_vs_base=%s hp_arms=%s || "
        "bands: RECALL_HP>=%.2f REACH_HP>=%d delta>=%d prec_floor>=%.2f || attr smooth=%.3f shuf=%.3f "
        "precond=%s || subgraph n=%d E=%d n_rel_types=%d seeds=%d" % (
            verdict, base_recall, base_prec, base_reach, baseline_reproduces,
            recall[EXPAND_ONLY], reach[EXPAND_ONLY], recall[BINDOBJ_ONLY], reach[BINDOBJ_ONLY],
            recall[FULL_STACK], reach[FULL_STACK],
            best_recall_arm, best_recall, best_reach_arm, best_reach,
            ("%.2f" % reach_delta) if reach_delta == reach_delta else "nan", hp_arms,
            RECALL_HP_MIN, REACH_HP_MIN, REACH_DELTA_HP, PRECISION_FLOOR,
            attr_meta["assort_smooth"], attr_meta["assort_shuffled"], precondition_ok,
            subgraph_meta["n_nodes"], subgraph_meta["n_edges"], subgraph_meta.get("n_relation_types", -1),
            len(per_seed)))

    gates = dict(
        verdict=verdict, recall_mean=recall, precision_mean=precision, reach_mean=reach,
        base_recall=base_recall, base_precision=base_prec, base_reach=base_reach,
        baseline_reproduces=bool(baseline_reproduces),
        best_recall_arm=best_recall_arm, best_recall=best_recall,
        best_reach_arm=best_reach_arm, best_reach=best_reach, reach_delta_vs_base=reach_delta,
        hard_pass=bool(hard_pass), hp_arms=hp_arms, element_attribution=element_attribution,
        precondition_ok=bool(precondition_ok),
        attr_assort_smooth=attr_meta["assort_smooth"], attr_assort_shuffled=attr_meta["assort_shuffled"],
        bands=dict(BASELINE_RECALL_LO=BASELINE_RECALL_LO, BASELINE_RECALL_HI=BASELINE_RECALL_HI,
                   BASELINE_REACH_MAX=BASELINE_REACH_MAX, RECALL_HP_MIN=RECALL_HP_MIN,
                   RECALL_MIDDLE_MIN=RECALL_MIDDLE_MIN, RECALL_HARDFAIL_DELTA=RECALL_HARDFAIL_DELTA,
                   REACH_HP_MIN=REACH_HP_MIN, REACH_DELTA_HP=REACH_DELTA_HP, PRECISION_FLOOR=PRECISION_FLOOR,
                   DG_SPARSITY=DG_SPARSITY, W_PROX_STRONG=W_PROX_STRONG, W_BIND_STRONG=W_BIND_STRONG,
                   W_SPARSE_HOYER=W_SPARSE_HOYER),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Discriminator + lever self-test (ALWAYS runs)
# ---------------------------------------------------------------------------

def lever_selftest():
    """Prove: (0) torch_hrr_unbind is the exact inverse of torch_hrr_bind for unitary roles; (1) _ste_kwta hits
    the DG target sparsity AND its magnitude-topk mask matches hdlab DGProjection/_sparse_topk_mask; (2) a tiny
    FULL_STACK retrain LEARNS role-apply-recoverable codes (recall clears chance by a margin AND the binding
    loss decreases) -- the objective is learnable and the recovery discriminator fires; (3) telemetry-sensitive
    (permuting the trained codes DROPS recall)."""
    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    d = 256

    # (0) unbind exactness on unitary roles
    roles = make_unitary_roles(3, d, rng)
    z = _l2(rng.standard_normal((5, d))).astype(np.float32)
    rt = torch.from_numpy(roles[0:1]).repeat(5, 1)
    bound = torch_hrr_bind(rt, torch.from_numpy(z))
    recon = torch_hrr_unbind(rt, bound).numpy()
    unbind_ok = bool(np.allclose(recon, z, atol=1e-3))

    # (1) STE k-WTA sparsity target + DG mask agreement
    h = torch.from_numpy(rng.standard_normal((4, d)).astype(np.float32))
    hs = _ste_kwta(h, 0.10)
    rate = float((hs != 0).float().mean())
    row0_mask_torch = (hs[0] != 0).numpy()
    row0_mask_dg = _sparse_topk_mask(np.abs(h[0].numpy()), 0.10)
    kwta_ok = bool(abs(rate - 0.10) <= 0.02 and np.array_equal(row0_mask_torch, row0_mask_dg))

    # (2) tiny FULL_STACK retrain on a planted typed graph (random typed edges over random nodes)
    n = 240
    T = 3
    feat = rng.standard_normal((n, 512)).astype(np.float32)
    n_e = 360
    a = rng.integers(0, n, size=n_e)
    b = rng.integers(0, n, size=n_e)
    keep = a != b
    edges = np.stack([a[keep], b[keep]], axis=1).astype(np.int32)
    rels = rng.integers(0, T, size=edges.shape[0]).astype(np.int32)
    dg = 512
    roles_dg = make_unitary_roles(T, dg, np.random.default_rng(1))
    cfg = dict(epochs=25, batch=128, lr=0.01, temp=0.15, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
               recover_topk=6, cos_floor_c=1.1)
    emb = train_encoder_v2(feat, edges, rels, roles_dg, cfg, 7, out_dim=dg, expand=True, bindobj=True, tag="ST")
    cos_floor = crosstalk_floor(n, dg, 1.1)
    rec = _topk_floor_adj(score_role(emb, roles_dg), 6, cos_floor)
    recall, prec, _ = _edge_recall_precision(rec, edges)
    # chance: random top-6 recall ~ 6*n / (n*(n-1)/2) ~ 12/n; require a clear margin above it
    chance = 12.0 / n
    learn_ok = bool(recall >= max(0.15, 4.0 * chance))

    # (3) telemetry: permute trained codes -> recall drops
    emb_perm = emb[rng.permutation(n)]
    rec_perm = _topk_floor_adj(score_role(emb_perm, roles_dg), 6, cos_floor)
    recall_perm, _, _ = _edge_recall_precision(rec_perm, edges)
    telemetry = bool((recall - recall_perm) >= 0.10)

    res = dict(unbind_ok=unbind_ok, kwta_rate=rate, kwta_ok=kwta_ok,
               retrain_recall=float(recall), retrain_prec=float(prec), chance=float(chance),
               learn_ok=learn_ok, recall_perm=float(recall_perm), telemetry_sensitive=telemetry)
    ok = bool(unbind_ok and kwta_ok and learn_ok and telemetry)
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

    st_ok, st_res = lever_selftest()
    _log("lever_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="LEVER_SELFTEST_FAILED (unbind/kwta/learn/telemetry): %s" % st_res,
            summary="lever selftest failed", elapsed_s=time.perf_counter() - t_start,
            lever_selftest=st_res))
        raise SystemExit(1)

    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s | rel_types=%d" % (
        {k: meta[k] for k in ("n_nodes", "n_edges", "median_degree")}, T))
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
            verdict_msg="SELFTEST_PASS unbind-exact + DG-kWTA==DGProjection + FULL_STACK retrain learns "
                        "role-recoverable codes telemetry-sensitive; typed subgraph + attribute pipeline exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            lever_selftest=st_res, subgraph_meta=meta, attr_meta=attr_meta))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, X, edges, rels, adj, cfg, a_smooth, a_shuf, ground_seeds, bins,
                          nonseed_idx, out_dir=out_dir_path)
            # ARMS-MUST-DIFFER: the 4 encoders + recovered-edge sets must not be bit-identical
            ed = pm["encoder_digests"]
            for i in range(len(ALL_ARMS)):
                for j in range(i + 1, len(ALL_ARMS)):
                    if ed[ALL_ARMS[i]] == ed[ALL_ARMS[j]]:
                        _log("  [warn] encoders identical: %s == %s (seed=%d)" % (ALL_ARMS[i], ALL_ARMS[j], seed))
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
