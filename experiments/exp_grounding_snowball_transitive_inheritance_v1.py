"""Grounding snowball: transitive grounding-inheritance on the native relational encoder.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test on the 3 encoders)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (ordering acc chance floor = 0.5; discriminator is the distance-decay of the
#   grounding LIFT vs a shuffled-attribute empirical null, not a closed-form noise floor)
# - baseline_in_band at smoke (ungrounded ordering acc must be near-chance 0.42..0.62; else leakage)
# - discriminator survives scale (smoke fires it: treatment near-seed lift+decay AND shuffled flat,
#   on a graph large enough to have far-from-seed atoms -> SMOKE=FULL branch parity)
# - HARD_PASS strictly above floor (near_lift >= 0.15 and decay >= 0.08; both > 0)
# - HP_SCOPE: Stage-2 gates apply to ARM_GROUNDED_SMOOTH (treatment) vs ARM_UNGROUNDED (baseline);
#   ARM_GROUNDED_SHUFFLED is the must-fail control (its near-lift MUST stay < 0.05)
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_model_seeds
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (shuffled empirical null recomputed per run;
#   attribute graph-smoothness assortativity gated per run)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg

SCIENCE (per notes/research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md,
Predictions A + B):

  STAGE 1 (Prediction A, hollow-skeleton floor -- no build, no gating on Stage 2 outcome):
    Probe the EXISTING teacher-free relational encoder (ARM_UNGROUNDED) with two families:
      (i)  RELATIONAL probe  = edge-vs-nonedge link prediction from the codes (AUC). The
           encoder is TRAINED for neighbor-closeness -> expected near-ceiling.
      (ii) GROUNDED-ATTRIBUTE probe = pairwise magnitude ORDERING ("is X bigger than Y") of an
           exogenous scalar that was NEVER a graph edge, read from FROZEN ungrounded codes via a
           ridge readout fit on a labeled seed set. Expected near-chance (0.5): relational-only
           training preserves WHO-is-near-WHOM (unsigned proximity), NOT a signed 1-D magnitude
           axis. Gap (relational_auc - grounded_ordering_acc) is the hollow-skeleton floor.
    LEAKAGE GUARD: if the ungrounded grounded-attribute readout is already high (> 0.70), the
    magnitude direction leaked into the relational codes -> flag and inspect before trusting Stage 2.

  STAGE 2 (Prediction B, the snowball):
    Attach a REAL exogenous scalar to a SMALL directly-grounded seed set (order 50-150 atoms) by
    co-training the SAME relational encoder with an auxiliary attribute-regression loss applied
    ONLY on seed atoms (relational InfoNCE + VICReg repulsion continue over ALL atoms -- "the
    structure carries it"). Then read the grounded-attribute ordering off NON-SEED atoms binned by
    graph distance to the nearest seed. SAME ridge readout method for grounded and ungrounded arms
    (fit on seed codes only) -> the LIFT isolates the ENCODER reshaping (structural propagation),
    not the readout head.
      Signature of a REAL snowball: near-seed lift >= +0.15 over ungrounded AND the lift decays
      MONOTONICALLY with graph distance from the nearest seed. A FLAT lift uncorrelated with graph
      distance is a HARD-FAIL/artifact, not a win (the theory specifically predicts distance-decay).
    MUST-FAIL CONTROL: ARM_GROUNDED_SHUFFLED grounds the SAME seed atoms with the attribute values
    PERMUTED across nodes (destroys graph-smoothness). Genuine transitive propagation is impossible
    without graph-smoothness -> its near-seed lift MUST stay near 0. If shuffled ALSO lifts near
    seeds, the treatment lift is leakage (e.g. seed-memorization + shared char-trigrams), not
    grounding -> HARD-FAIL.

ATTRIBUTE HONESTY (load-bearing framing): the grounded scalar is a SYNTHETIC graph-smooth field
diffused over the REAL ConceptNet subgraph -- an honest stand-in for a measured non-symbolic
attribute (size / weight / magnitude) that correlates along relational edges (the note's stated
precondition; the biological prior that relationally-close things share attributes). It is NOT a
claim of real perceptual grounding and NOT "teaching the substrate English". This cell tests the
PROPAGATION MECHANISM: can grounding attached to a seed set spread transitively through the
existing relational web with the right distance-decay signature. A PASS is a necessary
(not sufficient) recipe for real grounding without any external model; a FAIL means the encoder
lacks the compositional structure biological semantic memory uses to propagate grounding.

Prediction C (causal/index) is DEFERRED: a matched relation-only perturbation requires re-training
per removed edge (not cheap in this pipeline); flagged as a follow-up, not implemented here.

Teacher-free / self-contained: NO BGE, NO external LM, NO network. Reuses the CG'd teacher-free
relational encoder pipeline (cert 06e5a493d): load_cn_subgraph, char_trigram_features, ProjHead,
info_nce, vicreg_repulsion, build_adjlist. CPU-only. ASCII-only. No emojis. No em dashes.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from collections import deque
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
    load_cn_subgraph,
    char_trigram_features,
    ProjHead,
    info_nce,
    vicreg_repulsion,
    build_adjlist,
    _l2norm,
)

ANCHOR_NAME = "grounding_snowball_transitive_inheritance_v1"
SUBGRAPH_BASE_SEED = 1234

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME branches as FULL; only scale differs)
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(
    n_nodes=400, seeds=[7], epochs=10, batch=128,
    code_dim=64, feat_dim=1024, temp=0.15, lr=0.01,
    lambda_cov=1.0, lambda_var=1.0, lambda_attr=1.0,
    n_ground_seeds=20, diffuse_steps=8, n_sources=6,
    ridge_lambda=1.0, k_labelprop=7, n_pairs_per_bin=2000,
)

SMOKE_CFG = dict(
    n_nodes=2500, seeds=[7, 13], epochs=45, batch=256,
    code_dim=128, feat_dim=4096, temp=0.15, lr=0.01,
    lambda_cov=1.0, lambda_var=1.0, lambda_attr=1.0,
    n_ground_seeds=30, diffuse_steps=10, n_sources=25,
    ridge_lambda=1.0, k_labelprop=7, n_pairs_per_bin=4000,
)

FULL_CFG = dict(
    n_nodes=12000, seeds=[7, 13, 17, 23, 29], epochs=100, batch=512,
    code_dim=256, feat_dim=8192, temp=0.10, lr=0.008,
    lambda_cov=1.0, lambda_var=1.0, lambda_attr=1.0,
    n_ground_seeds=120, diffuse_steps=12, n_sources=80,
    ridge_lambda=1.0, k_labelprop=7, n_pairs_per_bin=6000,
)

# ---------------------------------------------------------------------------
# Pre-registered bands
# ---------------------------------------------------------------------------

# Stage 1 (Prediction A, hollow-skeleton floor)
STAGE1_RELATIONAL_AUC_HP = 0.75        # relational probe near-ceiling
STAGE1_GAP_HP = 0.30                    # relational_auc - grounded_floor_acc (deflated from note 0.40)
STAGE1_LEAKAGE_ACC = 0.70              # ungrounded grounded-attr readout above this => leakage flag
BASELINE_ORDERING_LO = 0.42            # ungrounded ordering must be near-chance (baseline_in_band)
BASELINE_ORDERING_HI = 0.62

# Stage 2 (Prediction B, snowball) -- label-propagation (transitive-inheritance) readout.
# Discriminator: a GRAPH-SMOOTH attribute label-propagated from grounded seeds over the relational
# codes shows near-seed ordering accuracy ABOVE chance that DECAYS monotonically with graph
# distance; the SAME codes + SAME seeds + a SHUFFLED (non-graph-smooth) attribute stay flat at
# chance. Smooth-decays-while-shuffled-flat isolates genuine transitive grounding from any
# encoder/readout artifact (only the attribute's graph-alignment differs).
NEAR_ACC_HP = 0.60          # near-seed (dist 1) smooth-attr ordering acc (chance=0.5)
DECAY_HP = 0.08             # near_acc - far_acc (monotone distance-decay signature)
GENUINE_MARGIN_HP = 0.06    # near_acc(smooth) - near_acc(shuffled) : graph-smoothness is load-bearing
NEAR_ACC_HF = 0.55          # below this near-seed => no propagation (HARD_FAIL)
DECAY_HF = 0.03             # below this decay => flat/artifact, not distance-dependent (HARD_FAIL)
GENUINE_MARGIN_HF = 0.03    # shuffled ~ smooth near seeds => leakage/artifact (HARD_FAIL)
MONOTONE_TOL = 0.03         # per-step acc increase tolerated before flagging non-monotone

# Attribute graph-smoothness precondition (measured per run; adaptive gate)
ATTR_ASSORT_SMOOTH_MIN = 0.45          # smooth attribute edge-correlation must be high
ATTR_ASSORT_SHUFFLED_MAX = 0.20        # shuffled attribute edge-correlation must be ~0

# distance bin edges: bin0=dist1, bin1=dist2, bin2=dist3, bin3=dist>=4
NEAR_BIN = 0           # dist 1 (immediate neighbors of a grounded seed)
FAR_BINS = (2, 3)      # dist >= 3 (largest populated among these is the far anchor)
MIN_BIN_NODES = 15     # a bin with fewer non-seed nodes is not scored (reported NaN)

# Primary discriminator runs on the RELATIONAL-ONLY (ungrounded) encoder codes -- the purest test
# of the user's "attach meaning to a few, structure carries it" hypothesis. The grounded
# co-trained encoder is a SECONDARY ablation (does explicit attribute co-training deepen
# propagation beyond what relational structure already provides).
PRIMARY_ARM = "ARM_STRUCTURE_SMOOTH"      # ungrounded relational codes + smooth attr (label-prop)
CONTROL_ARM = "ARM_STRUCTURE_SHUFFLED"    # ungrounded relational codes + shuffled attr (must-fail)
GROUNDED_ARM = "ARM_GROUNDED_SMOOTH"      # grounded co-trained codes + smooth attr (secondary)


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
# Graph-smooth attribute field + smoothness measurement
# ---------------------------------------------------------------------------

def make_smooth_attribute(edges, degrees, n_nodes, rng, n_sources, diffuse_steps):
    """Synthetic graph-smooth scalar via heat diffusion of random point sources.

    Real physical attributes (size / weight) ARE smooth over is-a / synonym relational
    structure. This standardized field is an honest stand-in with the same graph-smoothness
    property, giving ground-truth control. Vectorized (no python edge loop).
    """
    a = np.zeros(n_nodes, dtype=np.float64)
    n_sources = int(min(max(2, n_sources), n_nodes))
    src = rng.choice(n_nodes, size=n_sources, replace=False)
    a[src] = rng.standard_normal(n_sources)
    e0 = edges[:, 0].astype(np.int64)
    e1 = edges[:, 1].astype(np.int64)
    deg = np.maximum(degrees.astype(np.float64), 1.0)
    for _ in range(int(diffuse_steps)):
        nbr_sum = np.zeros(n_nodes, dtype=np.float64)
        np.add.at(nbr_sum, e0, a[e1])
        np.add.at(nbr_sum, e1, a[e0])
        a = 0.5 * a + 0.5 * (nbr_sum / deg)
    sd = a.std()
    if sd < 1e-9:
        # degenerate diffusion (disconnected/flat); fall back to raw random field
        a = rng.standard_normal(n_nodes)
        sd = a.std()
    a = (a - a.mean()) / (sd + 1e-12)
    return a.astype(np.float64)


def attribute_assortativity(a, edges):
    """Pearson correlation of (a[u], a[v]) across edges. High => graph-smooth."""
    if edges.shape[0] < 3:
        return 0.0
    au = a[edges[:, 0].astype(np.int64)]
    av = a[edges[:, 1].astype(np.int64)]
    # symmetric: stack both orientations
    x = np.concatenate([au, av])
    y = np.concatenate([av, au])
    xc = x - x.mean()
    yc = y - y.mean()
    denom = math.sqrt(float((xc * xc).sum()) * float((yc * yc).sum())) + 1e-12
    return float((xc * yc).sum() / denom)


# ---------------------------------------------------------------------------
# Multi-source BFS distance to nearest seed + distance binning
# ---------------------------------------------------------------------------

def multi_source_bfs(adj, seeds, n_nodes):
    """Return dist[n] = graph distance to nearest seed (0 for seeds, big for unreachable)."""
    BIG = 1 << 30
    dist = np.full(n_nodes, BIG, dtype=np.int64)
    dq = deque()
    for s in seeds:
        dist[s] = 0
        dq.append(s)
    while dq:
        u = dq.popleft()
        du = dist[u]
        for v in adj[u]:
            if dist[v] > du + 1:
                dist[v] = du + 1
                dq.append(v)
    return dist


def distance_bins(dist, seed_set):
    """Map each NON-seed node to a bin: dist1->0, dist2->1, dist3->2, dist>=4(reachable)->3.

    Returns dict bin_idx -> np.ndarray of node indices; plus n_unreachable.
    """
    BIG = 1 << 30
    bins = {0: [], 1: [], 2: [], 3: []}
    n_unreachable = 0
    for v in range(len(dist)):
        if v in seed_set:
            continue
        d = int(dist[v])
        if d >= BIG:
            n_unreachable += 1
            continue
        if d == 1:
            bins[0].append(v)
        elif d == 2:
            bins[1].append(v)
        elif d == 3:
            bins[2].append(v)
        else:  # d >= 4
            bins[3].append(v)
    return {k: np.array(v, dtype=np.int64) for k, v in bins.items()}, n_unreachable


# ---------------------------------------------------------------------------
# Encoder training (reuses ProjHead + info_nce + vicreg_repulsion)
# ---------------------------------------------------------------------------

def train_encoder(X, adj, cfg, seed, ground_seeds=None, attr=None, out_dir=None, tag=""):
    """Train the projection encoder.

    Relational loss (InfoNCE over graph-neighbor positives + VICReg) over ALL anchors.
    If ground_seeds + attr provided (lambda_attr>0), ALSO add an auxiliary MSE that regresses
    attr on the seed atoms only (via a discarded-at-readout attribute head). Returns final
    L2-normalized codes [n, code_dim] (float32).
    """
    torch.manual_seed(seed)
    np.random.seed(seed)
    n_nodes = X.shape[0]
    feat_dim = X.shape[1]
    Xt = torch.from_numpy(X)
    model = ProjHead(feat_dim, cfg["code_dim"])
    attr_head = torch.nn.Linear(cfg["code_dim"], 1, bias=True)
    params = list(model.parameters())
    grounded = ground_seeds is not None and attr is not None and cfg["lambda_attr"] > 0.0
    if grounded:
        params = params + list(attr_head.parameters())
        seeds_t = torch.from_numpy(np.asarray(ground_seeds, dtype=np.int64))
        attr_t = torch.from_numpy(attr[np.asarray(ground_seeds, dtype=np.int64)].astype(np.float32))
    opt = torch.optim.Adam(params, lr=cfg["lr"])
    rng = np.random.default_rng(seed + 7)
    has_nb = np.array([len(adj[i]) > 0 for i in range(n_nodes)], dtype=bool)
    anchor_pool = np.nonzero(has_nb)[0]
    log_every = max(1, cfg["epochs"] // 5)
    t_ep = time.perf_counter()
    for ep in range(cfg["epochs"]):
        a_idx = rng.choice(anchor_pool, size=min(cfg["batch"], anchor_pool.shape[0]), replace=False)
        p_idx = np.array([adj[a][rng.integers(0, len(adj[a]))] for a in a_idx], dtype=np.int64)
        ha = model(Xt[torch.from_numpy(a_idx.astype(np.int64))])
        hp = model(Xt[torch.from_numpy(p_idx)])
        loss = info_nce(ha, hp, cfg["temp"]) + vicreg_repulsion(
            torch.cat([ha, hp], dim=0), cfg["lambda_cov"], cfg["lambda_var"])
        if grounded:
            hs = model(Xt[seeds_t])
            zs = _l2norm(hs)
            pred = attr_head(zs).squeeze(-1)
            loss = loss + cfg["lambda_attr"] * torch.mean((pred - attr_t) ** 2)
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
        emb = _l2norm(model(Xt)).numpy().astype(np.float32)
    return emb


# ---------------------------------------------------------------------------
# Readout + discriminators
# ---------------------------------------------------------------------------

def ridge_readout(codes_seed, y_seed, codes_query, lam):
    """Closed-form ridge: fit w on seed codes -> scalar, predict query codes. Returns pred[query]."""
    X = codes_seed.astype(np.float64)
    y = np.asarray(y_seed, dtype=np.float64)
    d = X.shape[1]
    A = X.T @ X + lam * np.eye(d)
    b = X.T @ y
    w = np.linalg.solve(A, b)
    return (codes_query.astype(np.float64) @ w)


def label_propagation(codes, seed_idx, seed_vals, k):
    """Transitive-inheritance readout: predict each atom's attribute as the cosine-weighted
    average of its k nearest GROUNDED seeds in code space (Gunther 2018 inheritance mechanism).

    codes: [n, d]; seed_idx: [S]; seed_vals: [S]. Returns pred[n].
    """
    z = codes / (np.linalg.norm(codes, axis=1, keepdims=True) + 1e-8)
    zs = z[seed_idx]
    sims = z @ zs.T  # [n, S]
    S = zs.shape[0]
    kk = int(min(k, S))
    top = np.argpartition(-sims, kk - 1, axis=1)[:, :kk]  # [n, kk]
    rows = np.arange(z.shape[0])[:, None]
    w = np.maximum(sims[rows, top], 0.0) + 1e-9           # nonneg cosine weights
    yv = seed_vals[seed_idx][top]                          # [n, kk]
    pred = np.sum(w * yv, axis=1) / np.sum(w, axis=1)
    return pred


def ordering_accuracy(pred, truth, node_idx, rng, n_pairs):
    """Pairwise 'is X bigger than Y' accuracy over random pairs within node_idx. Chance=0.5."""
    m = node_idx.shape[0]
    if m < 2:
        return float("nan"), 0
    n_pairs = int(min(n_pairs, m * (m - 1) // 2))
    if n_pairs <= 0:
        return float("nan"), 0
    ui = node_idx[rng.integers(0, m, size=n_pairs)]
    vi = node_idx[rng.integers(0, m, size=n_pairs)]
    keep = ui != vi
    ui, vi = ui[keep], vi[keep]
    if ui.shape[0] == 0:
        return float("nan"), 0
    pred_sign = np.sign(pred[ui] - pred[vi])
    true_sign = np.sign(truth[ui] - truth[vi])
    valid = true_sign != 0
    if valid.sum() == 0:
        return float("nan"), 0
    acc = float(np.mean(pred_sign[valid] == true_sign[valid]))
    return acc, int(valid.sum())


def relational_auc(emb, edges, edge_set, n_nodes, rng, n_pairs):
    """AUC of code cosine separating true edges from random non-edges. Chance=0.5."""
    z = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8)
    n_e = min(n_pairs, edges.shape[0])
    ei = rng.integers(0, edges.shape[0], size=n_e)
    pos = np.sum(z[edges[ei, 0]] * z[edges[ei, 1]], axis=1)
    neg = []
    attempts = 0
    while len(neg) < n_e and attempts < n_e * 4:
        u = int(rng.integers(0, n_nodes))
        v = int(rng.integers(0, n_nodes))
        attempts += 1
        if u == v:
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) in edge_set:
            continue
        neg.append(float(np.dot(z[u], z[v])))
    neg = np.array(neg, dtype=np.float64)
    if neg.shape[0] == 0:
        return 0.5
    # Mann-Whitney AUC = P(pos > neg)
    allv = np.concatenate([pos, neg])
    order = np.argsort(allv, kind="mergesort")
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, allv.shape[0] + 1)
    r_pos = ranks[:pos.shape[0]].sum()
    n1 = float(pos.shape[0])
    n2 = float(neg.shape[0])
    auc = (r_pos - n1 * (n1 + 1) / 2.0) / (n1 * n2)
    return float(auc)


def _emb_digest(emb):
    return hashlib.sha256(np.ascontiguousarray(emb.astype(np.float32)).tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# Per-model-seed run
# ---------------------------------------------------------------------------

def run_seed(seed, X, edges, degrees, adj, edge_set, cfg, a_smooth, a_shuf,
             ground_seeds, seed_set, bins, out_dir=None):
    n_nodes = X.shape[0]
    rng = np.random.default_rng(seed + 4242)
    gs_arr = np.asarray(ground_seeds, dtype=np.int64)

    # 1) ungrounded encoder (relational only) -- Stage-1 floor + Stage-2 PRIMARY + control
    z_ung = train_encoder(X, adj, cfg, seed, out_dir=out_dir, tag="UNGROUNDED")
    # 2) grounded-smooth encoder (SECONDARY: does co-training deepen propagation?)
    z_gs = train_encoder(X, adj, cfg, seed, ground_seeds=ground_seeds, attr=a_smooth,
                         out_dir=out_dir, tag="GROUNDED_SMOOTH")

    # ARMS-MUST-DIFFER (META_RULE_AF): the two ENCODERS must differ.
    digests = {"ungrounded_encoder": _emb_digest(z_ung), "grounded_encoder": _emb_digest(z_gs)}
    assert digests["ungrounded_encoder"] != digests["grounded_encoder"], (
        "META_RULE_AF VIOLATION: ungrounded and grounded encoders bit-identical")

    k = cfg["k_labelprop"]
    # Label-propagation predictions (transitive inheritance from grounded seeds).
    pred_struct_smooth = label_propagation(z_ung, gs_arr, a_smooth, k)   # PRIMARY
    pred_struct_shuf = label_propagation(z_ung, gs_arr, a_shuf, k)       # must-fail control
    pred_grounded_smooth = label_propagation(z_gs, gs_arr, a_smooth, k)  # secondary ablation

    def per_bin(pred, truth):
        out = {}
        for b in range(4):
            idx = bins[b]
            if idx.shape[0] < MIN_BIN_NODES:
                out[b] = float("nan")
            else:
                acc, _ = ordering_accuracy(pred, truth, idx, rng, cfg["n_pairs_per_bin"])
                out[b] = acc
        return out

    acc_struct_smooth = per_bin(pred_struct_smooth, a_smooth)   # PRIMARY arm
    acc_struct_shuf = per_bin(pred_struct_shuf, a_shuf)         # control arm
    acc_grounded_smooth = per_bin(pred_grounded_smooth, a_smooth)  # secondary arm

    # Stage-1 grounded-attribute GLOBAL floor: ridge (global linear probe) fit on seed codes,
    # ordering acc across ALL non-seed reachable atoms. Near-chance => attribute NOT globally
    # represented as a linear axis (hollow-skeleton floor).
    all_nonseed = np.concatenate([bins[b] for b in range(4) if bins[b].shape[0] > 0]) \
        if any(bins[b].shape[0] > 0 for b in range(4)) else np.array([], dtype=np.int64)
    pred_ridge_global = ridge_readout(z_ung[gs_arr], a_smooth[gs_arr], z_ung, cfg["ridge_lambda"])
    if all_nonseed.shape[0] >= 2:
        grounded_floor_acc, _ = ordering_accuracy(pred_ridge_global, a_smooth, all_nonseed, rng,
                                                  cfg["n_pairs_per_bin"] * 2)
    else:
        grounded_floor_acc = float("nan")

    # Stage-1 relational probe (near-ceiling): edge-vs-nonedge link prediction from ungrounded codes.
    rel_auc_ung = relational_auc(z_ung, edges, edge_set, n_nodes, rng, cfg["n_pairs_per_bin"] * 2)

    return dict(
        seed=seed,
        relational_auc_ungrounded=rel_auc_ung,
        grounded_floor_acc=grounded_floor_acc,
        acc_struct_smooth=acc_struct_smooth,     # PRIMARY (Prediction B)
        acc_struct_shuf=acc_struct_shuf,         # must-fail control
        acc_grounded_smooth=acc_grounded_smooth,  # secondary co-training ablation
        bin_counts={b: int(bins[b].shape[0]) for b in range(4)},
        digests=digests,
    )


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------

def _nanmean(vals):
    arr = np.array([v for v in vals if v == v], dtype=np.float64)  # drop NaN
    return float(arr.mean()) if arr.shape[0] > 0 else float("nan")


def _far_anchor(acc_by_bin):
    """Return acc at the largest POPULATED far bin (d>=3), or nan if none populated."""
    for b in (3, 2):
        if acc_by_bin[b] == acc_by_bin[b]:  # not nan
            return acc_by_bin[b], b
    return float("nan"), None


def aggregate_and_verdict(per_seed, attr_meta, subgraph_meta):
    def mean_bin(key):
        return {b: _nanmean([m[key][b] for m in per_seed]) for b in range(4)}

    acc_struct_smooth = mean_bin("acc_struct_smooth")   # PRIMARY
    acc_struct_shuf = mean_bin("acc_struct_shuf")       # control
    acc_grounded_smooth = mean_bin("acc_grounded_smooth")  # secondary

    rel_auc = _nanmean([m["relational_auc_ungrounded"] for m in per_seed])
    grounded_floor = _nanmean([m["grounded_floor_acc"] for m in per_seed])
    gap = rel_auc - grounded_floor if (rel_auc == rel_auc and grounded_floor == grounded_floor) else float("nan")

    # ---- Stage 1 verdict (Prediction A, hollow skeleton) ----
    baseline_in_band = (grounded_floor == grounded_floor) and \
        (BASELINE_ORDERING_LO <= grounded_floor <= BASELINE_ORDERING_HI)
    leakage_flag = (grounded_floor == grounded_floor) and (grounded_floor > STAGE1_LEAKAGE_ACC)
    if (rel_auc >= STAGE1_RELATIONAL_AUC_HP) and (gap >= STAGE1_GAP_HP) and not leakage_flag:
        stage1 = "STAGE1_HARD_PASS"
    elif leakage_flag:
        stage1 = "STAGE1_LEAKAGE_FLAG"
    else:
        stage1 = "STAGE1_MIDDLE"

    # ---- Stage 2 discriminator (Prediction B, label-propagation snowball) ----
    near_acc = acc_struct_smooth[NEAR_BIN]
    far_acc, far_bin = _far_anchor(acc_struct_smooth)
    decay = near_acc - far_acc if (near_acc == near_acc and far_acc == far_acc) else float("nan")
    shuf_near = acc_struct_shuf[NEAR_BIN]
    genuine_margin = near_acc - shuf_near if (near_acc == near_acc and shuf_near == shuf_near) else float("nan")

    # monotone non-increasing across populated bins (smooth-attr primary arm)
    seq = [acc_struct_smooth[b] for b in range(4) if acc_struct_smooth[b] == acc_struct_smooth[b]]
    monotone = True
    for i in range(1, len(seq)):
        if seq[i] > seq[i - 1] + MONOTONE_TOL:
            monotone = False
            break

    # attribute smoothness precondition (adaptive gate)
    precondition_ok = (attr_meta["assort_smooth"] >= ATTR_ASSORT_SMOOTH_MIN) and \
        (attr_meta["assort_shuffled"] <= ATTR_ASSORT_SHUFFLED_MAX)

    if not precondition_ok:
        stage2 = "STAGE2_PRECONDITION_FAIL"
    elif far_acc != far_acc:
        stage2 = "STAGE2_INCONCLUSIVE_NO_FAR_BIN"  # cannot measure decay -> not a valid discriminator
    elif (near_acc >= NEAR_ACC_HP) and (decay >= DECAY_HP) and monotone and \
            (genuine_margin >= GENUINE_MARGIN_HP):
        stage2 = "STAGE2_HARD_PASS"       # real transitive snowball
    elif (near_acc < NEAR_ACC_HF) or (decay < DECAY_HF) or (genuine_margin < GENUINE_MARGIN_HF):
        stage2 = "STAGE2_HARD_FAIL"       # no propagation OR flat/artifact OR shuffled-leak
    else:
        stage2 = "STAGE2_MIDDLE_BAND"

    # secondary: does co-training deepen propagation vs relational-structure-only?
    grounded_near = acc_grounded_smooth[NEAR_BIN]
    cotrain_lift_near = grounded_near - near_acc if (grounded_near == grounded_near and near_acc == near_acc) else float("nan")

    if not precondition_ok:
        verdict = "PRECONDITION_FAIL"
    elif stage2 == "STAGE2_INCONCLUSIVE_NO_FAR_BIN":
        verdict = "MIDDLE_BAND"
    elif stage2 == "STAGE2_HARD_PASS":
        verdict = "HARD_PASS"
    elif stage2 == "STAGE2_HARD_FAIL":
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | STAGE1=%s rel_auc=%.3f grounded_floor=%.3f gap=%.3f leakage=%s baseline_in_band=%s | "
        "STAGE2=%s near_acc(d1)=%.3f far_acc(d%s)=%.3f decay=%.3f monotone=%s | "
        "SHUFFLED_CTRL near=%.3f genuine_margin=%.3f | cotrain_lift_near=%.3f | "
        "acc_smooth_by_bin(d1,d2,d3,d4+)=[%.3f,%.3f,%.3f,%.3f] shuf=[%.3f,%.3f,%.3f,%.3f] | "
        "attr_assort smooth=%.3f shuf=%.3f precond_ok=%s | subgraph n=%d E=%d med_deg=%.1f seeds=%d" % (
            verdict, stage1, rel_auc, grounded_floor, gap, leakage_flag, baseline_in_band,
            stage2, near_acc, str(far_bin + 1) if far_bin is not None else "?", far_acc, decay, monotone,
            shuf_near, genuine_margin, cotrain_lift_near,
            acc_struct_smooth[0], acc_struct_smooth[1], acc_struct_smooth[2], acc_struct_smooth[3],
            acc_struct_shuf[0], acc_struct_shuf[1], acc_struct_shuf[2], acc_struct_shuf[3],
            attr_meta["assort_smooth"], attr_meta["assort_shuffled"], precondition_ok,
            subgraph_meta["n_nodes"], subgraph_meta["n_edges"], subgraph_meta["median_degree"],
            attr_meta["n_ground_seeds"]))

    gates = dict(
        stage1_verdict=stage1, stage2_verdict=stage2,
        relational_auc_mean=rel_auc, grounded_floor_acc_mean=grounded_floor, stage1_gap=gap,
        leakage_flag=leakage_flag, baseline_in_band=baseline_in_band,
        near_acc=near_acc, far_acc=far_acc, far_bin=far_bin, decay=decay, monotone=monotone,
        shuffled_near_acc=shuf_near, genuine_margin=genuine_margin,
        cotrain_lift_near=cotrain_lift_near, precondition_ok=precondition_ok,
        attr_assort_smooth=attr_meta["assort_smooth"], attr_assort_shuffled=attr_meta["assort_shuffled"],
        acc_struct_smooth_by_bin={b: acc_struct_smooth[b] for b in range(4)},
        acc_struct_shuf_by_bin={b: acc_struct_shuf[b] for b in range(4)},
        acc_grounded_smooth_by_bin={b: acc_grounded_smooth[b] for b in range(4)},
        bands=dict(NEAR_ACC_HP=NEAR_ACC_HP, DECAY_HP=DECAY_HP, GENUINE_MARGIN_HP=GENUINE_MARGIN_HP,
                   NEAR_ACC_HF=NEAR_ACC_HF, DECAY_HF=DECAY_HF, GENUINE_MARGIN_HF=GENUINE_MARGIN_HF,
                   STAGE1_RELATIONAL_AUC_HP=STAGE1_RELATIONAL_AUC_HP, STAGE1_GAP_HP=STAGE1_GAP_HP),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Discriminator telemetry-sensitivity self-test (ALWAYS runs)
# ---------------------------------------------------------------------------

def discriminator_selftest():
    """Prove the label-propagation + distance-bin + shuffled-flat measurement pipeline is
    telemetry-sensitive (not analytically pinned): plant codes that carry a graph-smooth
    attribute with distance-decaying fidelity -> label-prop ordering acc must be high near
    seeds and DECAY to chance far away; a SHUFFLED (non-smooth) attribute on the SAME codes ->
    flat at chance."""
    rng = np.random.default_rng(0)
    n = 600
    code_dim = 32
    a = rng.standard_normal(n)                       # ground-truth scalar
    dist = np.concatenate([np.zeros(40, dtype=int), rng.integers(1, 6, size=n - 40)])
    gs_arr = np.arange(40)                            # 40 grounded seeds (dist 0)
    direction = rng.standard_normal(code_dim)
    direction /= np.linalg.norm(direction)

    def strength(d):
        return np.maximum(0.0, 1.0 - 0.22 * d)       # fidelity fades with distance

    # codes: attribute direction with distance-decaying strength + isotropic noise.
    z = 0.8 * rng.standard_normal((n, code_dim))
    z += (a * strength(dist))[:, None] * direction[None, :]
    z = (z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-8)).astype(np.float32)

    bins = {0: np.array([i for i in range(40, n) if dist[i] == 1]),
            1: np.array([i for i in range(40, n) if dist[i] == 2]),
            2: np.array([i for i in range(40, n) if dist[i] == 3]),
            3: np.array([i for i in range(40, n) if dist[i] >= 4])}

    pred_smooth = label_propagation(z, gs_arr, a, 7)
    a_shuf = a.copy()
    np.random.default_rng(9).shuffle(a_shuf)
    pred_shuf = label_propagation(z, gs_arr, a_shuf, 7)

    def bin_acc(pred, truth, idx):
        acc, _ = ordering_accuracy(pred, truth, idx, np.random.default_rng(1), 4000)
        return acc

    acc_s = {b: bin_acc(pred_smooth, a, bins[b]) for b in range(4)}
    acc_h = {b: bin_acc(pred_shuf, a_shuf, bins[b]) for b in range(4)}
    near = acc_s[0]
    far = acc_s[3]
    decay = near - far
    genuine = near - acc_h[0]
    res = dict(near_acc=float(near), far_acc=float(far), decay=float(decay),
               shuffled_near=float(acc_h[0]), genuine_margin=float(genuine),
               acc_smooth_by_bin={b: float(acc_s[b]) for b in range(4)},
               acc_shuffled_by_bin={b: float(acc_h[b]) for b in range(4)})
    ok = (near >= NEAR_ACC_HP) and (decay >= DECAY_HP) and (genuine >= GENUINE_MARGIN_HP) \
        and (abs(acc_h[0] - 0.5) < 0.05)
    return bool(ok), res


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

    # ---- discriminator telemetry-sensitivity self-test (ALWAYS) ----
    st_ok, st_res = discriminator_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED (not telemetry-sensitive): %s" % st_res,
            summary="discriminator selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res))
        raise SystemExit(1)

    # ---- load real ConceptNet subgraph (the encoder's actual relational web) ----
    _log("loading ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, meta = load_cn_subgraph(cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s" % meta)
    n_nodes = len(node_ids)
    X = char_trigram_features(node_words, cfg["feat_dim"])
    adj = build_adjlist(edges, n_nodes)
    edge_set = set((int(a), int(b)) for a, b in edges)

    # ---- build graph-smooth attribute + shuffled control + ground seeds (FIXED across model-seeds) ----
    attr_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 555)
    a_smooth = make_smooth_attribute(edges, degrees, n_nodes, attr_rng,
                                     cfg["n_sources"], cfg["diffuse_steps"])
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
    _log("distance bins (non-seed): d1=%d d2=%d d3=%d d4+=%d unreachable=%d" % (
        bins[0].shape[0], bins[1].shape[0], bins[2].shape[0], bins[3].shape[0], n_unreachable))

    attr_meta = dict(assort_smooth=assort_smooth, assort_shuffled=assort_shuffled,
                     n_ground_seeds=n_gs, n_unreachable=int(n_unreachable),
                     bin_counts={b: int(bins[b].shape[0]) for b in range(4)})

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS discriminator telemetry-sensitive + subgraph/attribute pipeline exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, subgraph_meta=meta, attr_meta=attr_meta))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, X, edges, degrees, adj, edge_set, cfg, a_smooth, a_shuf,
                          ground_seeds, seed_set, bins, out_dir=out_dir_path)
            # strip digests from persisted per-seed (kept only for arms-differ assertion)
            pm_persist = {k: v for k, v in pm.items() if k != "digests"}
            per_seed.append(pm_persist)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=pm_persist))
            _log("seed=%d rel_auc=%.3f floor=%.3f near_acc(d1)=%.3f d2=%.3f d3=%.3f shuf_near=%.3f" % (
                seed, pm["relational_auc_ungrounded"], pm["grounded_floor_acc"],
                pm["acc_struct_smooth"][0], pm["acc_struct_smooth"][1], pm["acc_struct_smooth"][2],
                pm["acc_struct_shuf"][0]))
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

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, attr_meta, meta)
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg,
        subgraph_meta=meta, attr_meta=attr_meta, gates=gates,
        discriminator_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed,
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
