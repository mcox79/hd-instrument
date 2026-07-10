"""DECISIVE TEST #4: the graph's OWN inductive-predictability CEILING (held-out edge prediction from RAW STRUCTURE).

QUESTION. Held-out relational reasoning on the ConceptNet subgraph fails: substrate codes route no better than random
(learned-SR reach 0.115), and NEITHER a sharper encoder (#1) NOR a stronger readout (#3) rescues it. The codes carry
only a WEAK inductive signal (phase-0 M5 held-out edge AUC ~0.69-0.71). Surviving hypothesis (#4): the graph's
structure is not inductively RICH enough -- held-out edges cannot be predicted from structure by ANY method, so the
limit is the KNOWLEDGE, not our encoder/readout. This cell measures the BEST-POSSIBLE held-out edge-prediction AUC
achievable from RAW GRAPH STRUCTURE ALONE (independent of substrate codes) = the inductive-predictability ceiling.

CONSTRUCTION (reuses phase-0 M5 held-out split VERBATIM, so structural ceiling is apples-to-apples with codes 0.70):
withhold 30% of edges (random permutation split); train predictors on the VISIBLE graph; score WITHHELD edges
(positives) vs FAR non-edges (random pairs that are not an edge AND share no common neighbor => hop>=3) as negatives;
AUC = P(pos ranks above neg). Same split, same negatives that phase-0's code-cosine M5 = 0.6945 used.

METHOD LADDER (increasing power; BEST over the ladder = the ceiling):
  Classic parameter-free structural link-predictors on the visible graph:
    CN  = |Gamma(u) cap Gamma(v)|                 (common neighbors)
    AA  = sum_{w in cap} 1/log(deg(w))            (Adamic-Adar)
    RA  = sum_{w in cap} 1/deg(w)                 (resource allocation)
    JC  = |cap| / |Gamma(u) cup Gamma(v)|         (Jaccard)
    PA  = deg(u)*deg(v)                           (preferential attachment; degree-only control)
  GCN = a small 2-layer graph-conv link-predictor (structural features + learnable node embedding), trained on visible
        edges via BCE with negative sampling, scored on held-out. The ML ceiling (pure torch; no torch_geometric).
  CODE_COSINE = paired reproduction of phase-0 M5 (char-trigram + binding encoder trained on the SAME visible edges;
        cosine AUC on the SAME held-out split). Positive control: reproduces our ~0.70 on THIS construction, so the
        structural/GNN ceiling is compared to codes on an identical split (not just cited from a different run).

DENSITY AXIS (directly tests the USER 'thin-knowledge' hypothesis). Also compute the ceiling on a DENSER subgraph =
the k-core (largest k with >= MIN_CORE_NODES nodes) of the same subgraph (restricts to high-degree nodes => higher
mean-degree + clustering = a denser/richer KB region). If the ceiling RISES with density -> richer knowledge yields a
higher inductive ceiling => CONFIRMS 'thin knowledge is the limit; the fix is richer ingest'.

DISCRIMINATOR (pre-registered; primary metric = best held-out edge AUC over the ladder on the FAR-negative split):
  HARD_PASS_SIGNAL_EXISTS  = best_auc_sparse >= 0.85 -> some structural/GNN method achieves materially higher held-out
                             AUC than our codes 0.70 -> a strong inductive signal EXISTS that our machinery misses ->
                             back to #1 encoder / #3 readout (NOT a knowledge limit).
  HARD_FAIL_KNOWLEDGE_IS_THE_LIMIT = best_auc_sparse <= 0.75 (full ladder incl PA; no method beats our codes
                             materially; every predictor also caps near 0.70) AND the RELATIONAL ceiling RISES with
                             density (best_rel_dense - best_rel_sparse >= 0.03; relational = CN/AA/RA/JC/GCN, PA
                             excluded as a degree/popularity artifact -- see REL_METHODS)
                             -> the graph's inductive signal is fundamentally weak = KNOWLEDGE is the wall; richer
                             ingest (not a better encoder/readout) is the fix. NOTE: this HARD_FAIL is the EXPECTED
                             confirmation of the surviving hypothesis -- the naming follows the pre-reg, not desirability.
  MIDDLE_BAND              = otherwise (0.75 < best_sparse < 0.85, OR caps near 0.70 but ceiling does NOT rise with
                             density -> knowledge-limited but denser ingest may not by itself help).
Reported (never gated): per-method AUC (far + hard negatives), LP-Hits@1/@2 (tail-corruption ranking; NOT identical to
SR routing reach -- reported for the reach comparison to learned-SR 0.115, labelled distinct), CODE_COSINE AUC
(paired M5 reproduction), sparse vs dense mean-degree + clustering, chosen k-core, held-out/negative counts.

SELF-TEST (mechanism; proves the test DETECTS inductive signal when present and is NULL when absent):
  PLANTED_SBM (community structure, high clustering): held-out intra-community edges have many common neighbors ->
    classic predictors + GCN MUST hit high AUC (>= 0.85). PLANTED_ER (Erdos-Renyi, matched avg degree, no clustering):
    common-neighbor signal is absent -> classic predictors must NOT beat chance (<= 0.65). Gap >= 0.20. If the test
    cannot separate signal-rich from signal-poor graphs, the ceiling measurement is meaningless -> BLOCK_DISPATCH.

## Compute architecture
class: (b) sequential-CPU with justification. Classic predictors are parameter-free set-intersections over neighbor
lists (no matmul); the GCN is a tiny 2-layer conv over a dense normalized adjacency (n<=5000 -> 5000x5000 dense
matmul, ~0.1 GFLOP/layer, trivial); the CODE_COSINE encoder reproduces phase-0 (13s/seed at n=4440 CPU). No
Python-loop-over-independent-points matmul; the only heavy op is the GCN/encoder which are single dense passes. Total
wall < 10 min/seed. Storage strategy: no_storage / no_composition (this is a graph-analysis ceiling probe; no HD
bundling or chained retrieval). Device-aware torch; CPU is adequate -> routes to remote_cpu_queue for FULL.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): CN/AA/RA/JC/PA/GCN/CODE_COSINE produce distinct score vectors
#   on the held-out set (hashed per seed; assert >= 6 distinct among the 7 methods).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: AUC chance floor = 0.50. best_auc <= 0.75 (HARD_FAIL) is strictly above the 0.50 floor and below the 0.85
#   SIGNAL bar; SIGNAL bar 0.85 is achievable (self-test SBM demonstrates >= 0.85). crlb_reachability: OK.
# - baseline_in_band: the ER-null self-test arm is the 'must-not-saturate on structureless graph' control (<= 0.65);
#   the SBM arm is the 'must-fire when signal present' control (>= 0.85). On the real graph the ceiling is the
#   measurement itself (not a saturating baseline).
# - discriminator survives scale: the SIGNAL-vs-KNOWLEDGE-LIMIT discriminator is (best_auc >= 0.85) vs (<= 0.75);
#   the planted self-test proves the ladder separates signal-rich (SBM) from signal-poor (ER) graphs by >= 0.20.
#   Smoke previews on real graph at reduced n; FULL (3 seeds, n=4440) canonical -- classic-predictor AUC is
#   deterministic given the graph+split (no training), so smoke is representative for those; GCN re-verified at FULL.
# - HARD_PASS(SIGNAL) 0.85 strictly above HARD_FAIL(cap) 0.75 + band width; density-rise margin adds strictness.
# - HP_SCOPE: the SIGNAL gate applies to best-over-ladder AUC (CN/AA/RA/JC/PA/GCN). CODE_COSINE = reference/positive
#   control (reproduce M5 ~0.69-0.73). PLANTED_SBM/PLANTED_ER = self-test signal/null controls.
# - positive_control (Gate D): CODE_COSINE reproduces phase-0 M5 (0.6945 @ n=4440) within 0.10 on the same construction.
# - sweep axis: density regime in {SPARSE, DENSE}; EXPECTED_N_UNITS = n_seeds; each seed asserted to produce both
#   regimes x all methods (method/regime-cardinality).
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: default_ok_for_this_regime. HELDOUT_FRAC=0.30 + far-negative construction are inherited
#   VERBATIM from phase-0 M5 (the exact split our 0.70 code baseline used); k-core threshold is chosen by a fixed
#   MIN_CORE_NODES rule, not tuned for the density verdict.
# - PAIRED: sparse and dense ceilings computed per seed on the same loaded subgraph; CODE_COSINE + structural + GCN
#   share the identical held-out split + far/hard negatives per seed (paired comparison).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-regime/per-method flush prints).
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
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import SUBGRAPH_BASE_SEED  # noqa: E402
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph, make_unitary_roles,
)
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import char_trigram_features  # noqa: E402
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import train_binding_encoder_dev  # noqa: E402

try:
    from experiments._cell_heartbeat import emit_heartbeat  # noqa: E402
except Exception:  # noqa: E722 -- optional instrumentation; explicit Exception, no bare except
    def emit_heartbeat(*a, **k):
        return None

ANCHOR_NAME = "graph_inductive_ceiling_v1"

# ---- Method names ----
CN = "CN"; AA = "AA"; RA = "RA"; JC = "JC"; PA = "PA"; GCN = "GCN"; CODE = "CODE_COSINE"
STRUCTURAL_METHODS = [CN, AA, RA, JC, PA, GCN]          # ceiling ladder (the SIGNAL/CAP gate is over these)
# Relational-structure subset (PA excluded): PA = deg(u)*deg(v) is node-POPULARITY, a degree/size artifact, not
# relational-knowledge richness. The DENSITY axis tests whether richer RELATIONAL structure raises the ceiling, so
# the density-rise gate uses the relational subset (smoke revealed PA saturates the full-ladder best on the sparse
# graph and masks the relational density signal; SIGNAL/CAP gates stay on the full ladder incl PA). Documented
# pre-dispatch confound-removal, not threshold-chasing.
REL_METHODS = [CN, AA, RA, JC, GCN]
ALL_METHODS = STRUCTURAL_METHODS + [CODE]

# ---- Pre-registered bands (picked BEFORE the run) ----
SIGNAL_EXISTS_AUC = 0.85      # HARD_PASS_SIGNAL_EXISTS: best ladder AUC >= this (materially beats codes 0.70)
CAP_NEAR_CODES_AUC = 0.75     # HARD_FAIL cap: best ladder AUC <= this (no method beats our 0.70 materially)
DENSITY_RISE_MARGIN = 0.03    # ceiling 'rises with density' if dense_best - sparse_best >= this
CODES_M5_REF = 0.6945         # MEASURED@data/phase0_code_structure_precheck_result.json:per_size[1].M5_heldout_auc
CODE_REPRO_TOL = 0.10         # CODE_COSINE positive-control reproduction tolerance vs phase-0 M5

# ---- Held-out construction (inherited VERBATIM from phase-0 M5) ----
HELDOUT_FRAC = 0.30
MIN_HELDOUT_EDGES = 60        # minimum held-out edges for a valid AUC (else INCONCLUSIVE_TOO_FEW_HELDOUT)
N_RANK_NEG = 99              # tail-corruption negatives per positive for LP-Hits@k
MIN_CORE_NODES_FULL = 250    # k-core density-axis: largest k with >= this many nodes
MIN_CORE_NODES_SMOKE = 120

# ---- GCN hyperparams (structure-only ML ceiling) ----
GCN_HIDDEN = 128; GCN_OUT = 64; GCN_EMB = 64

# Config profiles. SMOKE exercises the SAME methods / code path as FULL; only n + epochs differ.
SELFTEST_CFG = dict(seeds=[7], n_nodes=1200, enc=dict(epochs=30, batch=256, code_dim=256, feat_dim=2048,
                    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0),
                    gcn_epochs=60, min_core=100)
SMOKE_CFG = dict(seeds=[7, 13], n_nodes=1800, enc=dict(epochs=60, batch=256, code_dim=512, feat_dim=4096,
                 temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0),
                 gcn_epochs=120, min_core=MIN_CORE_NODES_SMOKE)
FULL_CFG = dict(seeds=[7, 13, 17], n_nodes=5000, enc=dict(epochs=80, batch=256, code_dim=512, feat_dim=4096,
                temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0),
                gcn_epochs=200, min_core=MIN_CORE_NODES_FULL)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Graph utilities (undirected simple graph from an edge list).
# ---------------------------------------------------------------------------

def build_adj_sets(edges, n_nodes):
    """Undirected neighbor sets + edge set from an [E,2] edge list (self-loops dropped)."""
    adj = [set() for _ in range(n_nodes)]
    eset = set()
    for (a, b) in edges:
        a = int(a); b = int(b)
        if a == b:
            continue
        adj[a].add(b); adj[b].add(a)
        eset.add((a, b) if a < b else (b, a))
    return adj, eset


def clustering_coeffs(adj, n_nodes):
    cc = np.zeros(n_nodes, dtype=np.float64)
    for u in range(n_nodes):
        nb = adj[u]
        d = len(nb)
        if d < 2:
            continue
        nb_list = list(nb)
        tri = 0
        for i in range(len(nb_list)):
            wi = nb_list[i]
            ai = adj[wi]
            for j in range(i + 1, len(nb_list)):
                if nb_list[j] in ai:
                    tri += 1
        cc[u] = 2.0 * tri / (d * (d - 1))
    return cc


def core_numbers(adj, n_nodes):
    """k-core decomposition by min-degree peeling (heap, lazy-delete). O((n+E) log n). Returns core number per node."""
    import heapq
    deg = np.array([len(adj[u]) for u in range(n_nodes)], dtype=np.int64)
    core = np.zeros(n_nodes, dtype=np.int64)
    removed = np.zeros(n_nodes, dtype=bool)
    heap = [(int(deg[u]), int(u)) for u in range(n_nodes)]
    heapq.heapify(heap)
    cur_max = 0
    while heap:
        d, u = heapq.heappop(heap)
        if removed[u]:
            continue
        if d < deg[u]:  # stale entry (degree decreased since pushed)
            heapq.heappush(heap, (int(deg[u]), u))
            continue
        cur_max = max(cur_max, int(deg[u]))
        core[u] = cur_max
        removed[u] = True
        for w in adj[u]:
            if not removed[w]:
                deg[w] -= 1
                heapq.heappush(heap, (int(deg[w]), int(w)))
    return core


def select_kcore(adj, n_nodes, min_core_nodes):
    """Largest k with >= min_core_nodes nodes in the k-core. Returns (k, node_mask)."""
    core = core_numbers(adj, n_nodes)
    best_k = 1
    for k in range(int(core.max()), 1, -1):
        mask = core >= k
        if int(mask.sum()) >= min_core_nodes:
            best_k = k
            return best_k, mask
    mask = core >= best_k
    return best_k, mask


def subgraph_reindex(edges, rels, node_words, keep_mask):
    """Restrict to nodes in keep_mask; edges with both endpoints kept; reindex 0..m-1."""
    old_ids = np.where(keep_mask)[0]
    remap = -np.ones(len(keep_mask), dtype=np.int64)
    remap[old_ids] = np.arange(len(old_ids))
    keep_e = keep_mask[edges[:, 0]] & keep_mask[edges[:, 1]]
    e2 = np.stack([remap[edges[keep_e, 0]], remap[edges[keep_e, 1]]], axis=1)
    r2 = np.asarray(rels)[keep_e]
    nw2 = [node_words[i] for i in old_ids]
    return e2, r2, nw2, old_ids


# ---------------------------------------------------------------------------
# Held-out split + negatives (VERBATIM logic from phase-0 M5).
# ---------------------------------------------------------------------------

def sample_far_negatives(n_need, n_nodes, eset, adj_sets, rng):
    """Random pairs, not an edge, sharing no common neighbor (hop>=3). Same as phase-0 M5 negatives."""
    neg = []
    tries = 0
    cap = max(n_need * 40, 10000)
    while len(neg) < n_need and tries < cap:
        tries += 1
        u = int(rng.integers(0, n_nodes)); v = int(rng.integers(0, n_nodes))
        if u == v:
            continue
        key = (u, v) if u < v else (v, u)
        if key in eset:
            continue
        if adj_sets[u] & adj_sets[v]:
            continue
        neg.append((u, v))
    return neg


def sample_hard_negatives(n_need, n_nodes, eset, rng):
    """Random non-edge pairs regardless of common neighbors (the harder LP negative set)."""
    neg = []
    tries = 0
    cap = max(n_need * 40, 10000)
    while len(neg) < n_need and tries < cap:
        tries += 1
        u = int(rng.integers(0, n_nodes)); v = int(rng.integers(0, n_nodes))
        if u == v:
            continue
        key = (u, v) if u < v else (v, u)
        if key in eset:
            continue
        neg.append((u, v))
    return neg


# ---------------------------------------------------------------------------
# AUC (average-rank tie correction -- ESSENTIAL: classic predictors tie many pairs at 0).
# ---------------------------------------------------------------------------

def _avg_ranks(vals):
    v = np.asarray(vals, dtype=np.float64)
    order = np.argsort(v, kind="mergesort")
    ranks = np.empty(len(v), dtype=np.float64)
    sv = v[order]
    i = 0
    n = len(v)
    while i < n:
        j = i
        while j + 1 < n and sv[j + 1] == sv[i]:
            j += 1
        avg = (i + j) / 2.0 + 1.0  # 1-based average rank for ties [i..j]
        ranks[order[i:j + 1]] = avg
        i = j + 1
    return ranks


def auc_pos_neg(pos, neg):
    pos = np.asarray(pos, dtype=np.float64); neg = np.asarray(neg, dtype=np.float64)
    n1 = len(pos); n2 = len(neg)
    if n1 == 0 or n2 == 0:
        return float("nan")
    ranks = _avg_ranks(np.concatenate([pos, neg]))
    r_pos = ranks[:n1].sum()
    u = r_pos - n1 * (n1 + 1) / 2.0
    return float(u / (n1 * n2))


# ---------------------------------------------------------------------------
# Classic structural link-predictor scores for a batch of node pairs on the VISIBLE graph.
# ---------------------------------------------------------------------------

def score_classic(pairs, adj, deg):
    """Return dict method -> np.array of scores for each (u,v) in pairs, on the visible adjacency `adj`."""
    m = len(pairs)
    cn = np.zeros(m); aa = np.zeros(m); ra = np.zeros(m); jc = np.zeros(m); pa = np.zeros(m)
    for i, (u, v) in enumerate(pairs):
        u = int(u); v = int(v)
        au = adj[u]; av = adj[v]
        inter = au & av
        du = len(au); dv = len(av)
        cn[i] = len(inter)
        pa[i] = du * dv
        union = du + dv - len(inter)
        jc[i] = (len(inter) / union) if union > 0 else 0.0
        s_aa = 0.0; s_ra = 0.0
        for w in inter:
            dw = deg[w]
            if dw > 1:
                s_aa += 1.0 / math.log(dw)
            if dw > 0:
                s_ra += 1.0 / dw
        aa[i] = s_aa; ra[i] = s_ra
    return {CN: cn, AA: aa, RA: ra, JC: jc, PA: pa}


# ---------------------------------------------------------------------------
# GCN link-predictor (pure torch; structural features + learnable embedding; visible-graph conv).
# ---------------------------------------------------------------------------

def build_norm_adj(vis_edges, n_nodes, device):
    """Symmetric-normalized dense adjacency with self loops: D^-1/2 (A+I) D^-1/2."""
    A = torch.zeros(n_nodes, n_nodes, device=device)
    for (a, b) in vis_edges:
        a = int(a); b = int(b)
        if a == b:
            continue
        A[a, b] = 1.0; A[b, a] = 1.0
    A += torch.eye(n_nodes, device=device)
    d = A.sum(dim=1).clamp(min=1.0)
    dinv = d.pow(-0.5)
    return dinv[:, None] * A * dinv[None, :]


def structural_features(adj, deg, cc, n_nodes, device):
    dn = deg.astype(np.float64)
    avg_nb = np.zeros(n_nodes, dtype=np.float64)
    for u in range(n_nodes):
        if deg[u] > 0:
            avg_nb[u] = np.mean([deg[w] for w in adj[u]])
    feats = np.stack([
        dn / max(dn.max(), 1.0),
        np.log1p(dn),
        cc,
        avg_nb / max(avg_nb.max(), 1.0),
    ], axis=1)
    feats = (feats - feats.mean(axis=0)) / (feats.std(axis=0) + 1e-6)
    return torch.tensor(feats, dtype=torch.float32, device=device)


class GCNLink(torch.nn.Module):
    def __init__(self, n_nodes, f_in, hidden, out, emb, device):
        super().__init__()
        self.emb = torch.nn.Parameter(torch.randn(n_nodes, emb, device=device) * 0.1)
        self.w0 = torch.nn.Linear(f_in + emb, hidden).to(device)
        self.w1 = torch.nn.Linear(hidden, out).to(device)

    def forward(self, Ahat, F):
        h = torch.cat([F, self.emb], dim=1)
        h = torch.relu(Ahat @ self.w0(h))
        h = Ahat @ self.w1(h)
        return torch.nn.functional.normalize(h, dim=1)


def train_gcn(Ahat, F, vis_edges, n_nodes, epochs, device, seed):
    torch.manual_seed(seed)
    model = GCNLink(n_nodes, F.shape[1], GCN_HIDDEN, GCN_OUT, GCN_EMB, device)
    opt = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-5)
    ep = torch.tensor(np.asarray(vis_edges, dtype=np.int64), device=device)
    n_pos = ep.shape[0]
    if n_pos == 0:
        return model
    gen = torch.Generator(device="cpu").manual_seed(seed + 1)
    for e in range(epochs):
        model.train(); opt.zero_grad()
        h = model(Ahat, F)
        pu = h[ep[:, 0]]; pv = h[ep[:, 1]]
        pos_s = (pu * pv).sum(dim=1)
        neg_u = torch.randint(0, n_nodes, (n_pos,), generator=gen).to(device)
        neg_v = torch.randint(0, n_nodes, (n_pos,), generator=gen).to(device)
        neg_s = (h[neg_u] * h[neg_v]).sum(dim=1)
        logits = torch.cat([pos_s, neg_s])
        labels = torch.cat([torch.ones(n_pos, device=device), torch.zeros(n_pos, device=device)])
        loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, labels)
        loss.backward(); opt.step()
    model.eval()
    return model


def gcn_scores(model, Ahat, F, pairs, device):
    with torch.no_grad():
        h = model(Ahat, F)
    idx = torch.tensor(np.asarray(pairs, dtype=np.int64), device=device)
    return ((h[idx[:, 0]] * h[idx[:, 1]]).sum(dim=1)).cpu().numpy()


def gcn_h(model, Ahat, F):
    with torch.no_grad():
        return model(Ahat, F)


# ---------------------------------------------------------------------------
# CODE_COSINE (paired M5 reproduction): train binding encoder on visible edges, cosine AUC on held-out.
# ---------------------------------------------------------------------------

def train_code_cosine(node_words, vis_edges, vis_rels, roles_t, enc_cfg, seed, device):
    X = char_trigram_features(node_words, enc_cfg["feat_dim"])
    Z = train_binding_encoder_dev(X, np.asarray(vis_edges, dtype=np.int64), np.asarray(vis_rels), roles_t,
                                  enc_cfg, seed, device, out_dir=None, tag="ceil_code")
    return torch.nn.functional.normalize(Z.to(torch.float32), dim=1)


def code_scores(Zn, pairs):
    idx = torch.tensor(np.asarray(pairs, dtype=np.int64), device=Zn.device)
    return ((Zn[idx[:, 0]] * Zn[idx[:, 1]]).sum(dim=1)).cpu().numpy()


# ---------------------------------------------------------------------------
# LP-Hits@k (tail-corruption ranking). For each positive (u,v): rank {v} u {N_RANK_NEG random non-neighbors of u}.
# scorer(u, cand_array) -> np.array. Reported (not gated); NOT identical to SR routing reach.
# ---------------------------------------------------------------------------

def hits_at_k(pos_pairs, adj, n_nodes, scorer_pairs, rng, n_neg=N_RANK_NEG, cap=400):
    if len(pos_pairs) > cap:
        sel = rng.choice(len(pos_pairs), size=cap, replace=False)
        pos_pairs = [pos_pairs[i] for i in sel]
    hit1 = 0.0; hit2 = 0.0; nq = 0
    for (u, v) in pos_pairs:
        u = int(u); v = int(v)
        cand = [v]
        nb = adj[u]
        t = 0
        while len(cand) < n_neg + 1 and t < n_neg * 40:
            t += 1
            c = int(rng.integers(0, n_nodes))
            if c == u or c == v or c in nb:
                continue
            cand.append(c)
        pairs = [(u, c) for c in cand]
        sc = scorer_pairs(pairs)
        order = np.argsort(-sc, kind="mergesort")
        rank_true = int(np.where(order == 0)[0][0])  # position of the true target (index 0 in cand)
        if rank_true < 1:
            hit1 += 1.0
        if rank_true < 2:
            hit2 += 1.0
        nq += 1
    if nq == 0:
        return float("nan"), float("nan")
    return hit1 / nq, hit2 / nq


# ---------------------------------------------------------------------------
# Run one regime (a graph = edges + node_words) end-to-end: split, train, score, AUC + Hits per method.
# ---------------------------------------------------------------------------

def run_regime(regime_name, edges, rels, node_words, roles_t, enc_cfg, gcn_epochs, seed, device,
               out_dir=None, do_code=True):
    n_nodes = len(node_words)
    edges = np.asarray(edges, dtype=np.int64)
    rng = np.random.default_rng(seed * 100003 + hash(regime_name) % 100000)

    adj_full, eset_full = build_adj_sets(edges, n_nodes)

    # held-out split (30% edges withheld)
    n_e = edges.shape[0]
    perm = rng.permutation(n_e)
    n_hold = int(HELDOUT_FRAC * n_e)
    hold_idx, keep_idx = perm[:n_hold], perm[n_hold:]
    vis_edges = edges[keep_idx]
    vis_rels = np.asarray(rels)[keep_idx]

    # visible-graph adjacency (predictors trained on VISIBLE edges only)
    adj_vis, _ = build_adj_sets(vis_edges, n_nodes)
    deg_vis = np.array([len(adj_vis[u]) for u in range(n_nodes)], dtype=np.int64)

    # positives = held-out edges; cap for speed
    hsel = hold_idx if n_hold <= 3000 else rng.choice(hold_idx, size=3000, replace=False)
    pos_pairs = [(int(edges[i, 0]), int(edges[i, 1])) for i in hsel]
    n_pos = len(pos_pairs)
    neg_far = sample_far_negatives(n_pos, n_nodes, eset_full, adj_full, rng)
    neg_hard = sample_hard_negatives(n_pos, n_nodes, eset_full, rng)

    result = dict(regime=regime_name, n_nodes=int(n_nodes), n_edges=int(n_e),
                  mean_degree=float(2.0 * n_e / max(n_nodes, 1)),
                  n_heldout=int(n_pos), n_neg_far=len(neg_far), n_neg_hard=len(neg_hard),
                  methods={}, sigs={}, failures=[])

    cc_full = clustering_coeffs(adj_full, n_nodes)
    result["mean_clustering"] = float(np.mean(cc_full))

    if n_pos < MIN_HELDOUT_EDGES or len(neg_far) < max(20, n_pos // 4):
        result["too_few"] = True
        return result
    result["too_few"] = False

    # ---- classic predictors ----
    sc_pos = score_classic(pos_pairs, adj_vis, deg_vis)
    sc_far = score_classic(neg_far, adj_vis, deg_vis)
    sc_hard = score_classic(neg_hard, adj_vis, deg_vis)
    for meth in [CN, AA, RA, JC, PA]:
        auc_far = auc_pos_neg(sc_pos[meth], sc_far[meth])
        auc_hard = auc_pos_neg(sc_pos[meth], sc_hard[meth])
        h1, h2 = hits_at_k(pos_pairs, adj_vis, n_nodes,
                           lambda prs, mm=meth: score_classic(prs, adj_vis, deg_vis)[mm], rng)
        result["methods"][meth] = dict(auc_far=auc_far, auc_hard=auc_hard, hits1=h1, hits2=h2)
        result["sigs"][meth] = hashlib.sha256(np.round(sc_pos[meth], 6).tobytes()).hexdigest()

    # ---- GCN ----
    try:
        Ahat = build_norm_adj(vis_edges, n_nodes, device)
        F = structural_features(adj_vis, deg_vis, cc_full, n_nodes, device)
        model = train_gcn(Ahat, F, vis_edges, n_nodes, gcn_epochs, device, seed)
        gp = gcn_scores(model, Ahat, F, pos_pairs, device)
        gf = gcn_scores(model, Ahat, F, neg_far, device)
        gh = gcn_scores(model, Ahat, F, neg_hard, device)
        h_emb = gcn_h(model, Ahat, F)

        def _gcn_scorer(prs, hh=h_emb):
            idx = torch.tensor(np.asarray(prs, dtype=np.int64), device=hh.device)
            return ((hh[idx[:, 0]] * hh[idx[:, 1]]).sum(dim=1)).cpu().numpy()

        gh1, gh2 = hits_at_k(pos_pairs, adj_vis, n_nodes, _gcn_scorer, rng)
        result["methods"][GCN] = dict(auc_far=auc_pos_neg(gp, gf), auc_hard=auc_pos_neg(gp, gh),
                                      hits1=gh1, hits2=gh2)
        result["sigs"][GCN] = hashlib.sha256(np.round(gp, 6).tobytes()).hexdigest()
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:  # noqa -- record failure-class, do not silently continue (META_RULE_J)
        result["failures"].append(dict(method=GCN, failure_class=type(e).__name__, msg=str(e)[:200]))
        result["methods"][GCN] = dict(auc_far=float("nan"), auc_hard=float("nan"),
                                      hits1=float("nan"), hits2=float("nan"))
        result["sigs"][GCN] = "gcn_failed"

    # ---- CODE_COSINE (paired M5 reproduction) ----
    if do_code:
        try:
            Zn = train_code_cosine(node_words, vis_edges, vis_rels, roles_t, enc_cfg, seed, device)
            cp = code_scores(Zn, pos_pairs)
            cf = code_scores(Zn, neg_far)
            chd = code_scores(Zn, neg_hard)

            def _code_scorer(prs, zz=Zn):
                idx = torch.tensor(np.asarray(prs, dtype=np.int64), device=zz.device)
                return ((zz[idx[:, 0]] * zz[idx[:, 1]]).sum(dim=1)).cpu().numpy()

            ch1, ch2 = hits_at_k(pos_pairs, adj_vis, n_nodes, _code_scorer, rng)
            result["methods"][CODE] = dict(auc_far=auc_pos_neg(cp, cf), auc_hard=auc_pos_neg(cp, chd),
                                           hits1=ch1, hits2=ch2)
            result["sigs"][CODE] = hashlib.sha256(np.round(cp, 6).tobytes()).hexdigest()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # noqa
            result["failures"].append(dict(method=CODE, failure_class=type(e).__name__, msg=str(e)[:200]))
            result["methods"][CODE] = dict(auc_far=float("nan"), auc_hard=float("nan"),
                                           hits1=float("nan"), hits2=float("nan"))
            result["sigs"][CODE] = "code_failed"

    best = max([result["methods"][m]["auc_far"] for m in STRUCTURAL_METHODS
                if result["methods"][m]["auc_far"] == result["methods"][m]["auc_far"]] or [float("nan")])
    best_rel = max([result["methods"][m]["auc_far"] for m in REL_METHODS
                    if result["methods"][m]["auc_far"] == result["methods"][m]["auc_far"]] or [float("nan")])
    result["best_structural_auc_far"] = float(best)
    result["best_relational_auc_far"] = float(best_rel)
    _log("  seed=%d regime=%s n=%d E=%d mean_deg=%.2f clust=%.3f n_ho=%d :: %s | best_struct=%.3f" % (
        seed, regime_name, n_nodes, n_e, result["mean_degree"], result["mean_clustering"], n_pos,
        " ".join("%s=%.3f" % (m, result["methods"][m]["auc_far"]) for m in ALL_METHODS if m in result["methods"]),
        best))
    return result


# ---------------------------------------------------------------------------
# Per-seed: SPARSE (full subgraph) + DENSE (k-core).
# ---------------------------------------------------------------------------

def run_seed(seed, edges, rels, node_words, roles_t, enc_cfg, gcn_epochs, min_core, device, out_dir=None):
    n_nodes = len(node_words)
    t0 = time.perf_counter()
    adj_full, _ = build_adj_sets(edges, n_nodes)

    sparse = run_regime("SPARSE", edges, rels, node_words, roles_t, enc_cfg, gcn_epochs, seed, device,
                        out_dir=out_dir, do_code=True)
    if out_dir:
        emit_heartbeat(out_dir, unit_idx=0, total_units=2, elapsed_s=time.perf_counter() - t0)

    k, mask = select_kcore(adj_full, n_nodes, min_core)
    e2, r2, nw2, _old = subgraph_reindex(edges, rels, node_words, mask)
    dense = run_regime("DENSE", e2, r2, nw2, roles_t, enc_cfg, gcn_epochs, seed, device,
                       out_dir=out_dir, do_code=True)
    dense["kcore_k"] = int(k)
    if out_dir:
        emit_heartbeat(out_dir, unit_idx=1, total_units=2, elapsed_s=time.perf_counter() - t0)

    return dict(seed=seed, sparse=sparse, dense=dense, kcore_k=int(k))


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed):
    def regA(regime, meth, key):
        return _nm([m[regime]["methods"].get(meth, {}).get(key, float("nan")) for m in per_seed])

    def bestA(regime):
        return _nm([m[regime]["best_structural_auc_far"] for m in per_seed])

    def bestRel(regime):
        return _nm([m[regime]["best_relational_auc_far"] for m in per_seed])

    sparse_methods = {m: dict(auc_far=regA("sparse", m, "auc_far"), auc_hard=regA("sparse", m, "auc_hard"),
                              hits1=regA("sparse", m, "hits1"), hits2=regA("sparse", m, "hits2"))
                      for m in ALL_METHODS}
    dense_methods = {m: dict(auc_far=regA("dense", m, "auc_far"), auc_hard=regA("dense", m, "auc_hard"),
                             hits1=regA("dense", m, "hits1"), hits2=regA("dense", m, "hits2"))
                     for m in ALL_METHODS}

    best_sparse = bestA("sparse")                # full ladder incl PA -> SIGNAL/CAP gates
    best_dense = bestA("dense")
    best_rel_sparse = bestRel("sparse")          # relational subset excl PA -> DENSITY gate (see REL_METHODS note)
    best_rel_dense = bestRel("dense")
    code_sparse = sparse_methods[CODE]["auc_far"]
    code_dense = dense_methods[CODE]["auc_far"]
    # density delta (full ladder, reported) + relational density delta (the GATE, PA-artifact removed) + code delta
    density_delta_full = (best_dense - best_sparse) if (best_dense == best_dense and best_sparse == best_sparse) else float("nan")
    density_delta = (best_rel_dense - best_rel_sparse) if (best_rel_dense == best_rel_dense and best_rel_sparse == best_rel_sparse) else float("nan")
    density_delta_code = (code_dense - code_sparse) if (code_dense == code_dense and code_sparse == code_sparse) else float("nan")
    density_rises = bool(density_delta == density_delta and density_delta >= DENSITY_RISE_MARGIN)

    sparse_deg = _nm([m["sparse"]["mean_degree"] for m in per_seed])
    dense_deg = _nm([m["dense"]["mean_degree"] for m in per_seed])
    sparse_clust = _nm([m["sparse"]["mean_clustering"] for m in per_seed])
    dense_clust = _nm([m["dense"]["mean_clustering"] for m in per_seed])
    n_ho_sparse = int(_nm([m["sparse"]["n_heldout"] for m in per_seed]))
    kcore_k = int(_nm([m["kcore_k"] for m in per_seed]))

    # positive control: CODE_COSINE reproduces phase-0 M5
    code_repro_ok = bool(code_sparse == code_sparse and abs(code_sparse - CODES_M5_REF) <= CODE_REPRO_TOL)

    enough = bool(n_ho_sparse >= MIN_HELDOUT_EDGES)
    signal_exists = bool(best_sparse == best_sparse and best_sparse >= SIGNAL_EXISTS_AUC)
    caps_near_codes = bool(best_sparse == best_sparse and best_sparse <= CAP_NEAR_CODES_AUC)

    if not enough:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif signal_exists:
        verdict = "HARD_PASS_SIGNAL_EXISTS"
    elif caps_near_codes and density_rises:
        verdict = "HARD_FAIL_KNOWLEDGE_IS_THE_LIMIT"
    else:
        verdict = "MIDDLE_BAND_INDUCTIVE_CEILING"

    beats_codes = (best_sparse - code_sparse) if (code_sparse == code_sparse) else float("nan")
    verdict_msg = (
        "%s || SPARSE(deg=%.2f clust=%.3f n_ho=%d): %s best_struct=%.3f best_rel=%.3f | CODE=%.3f "
        "(M5repro_ok=%s vs %.3f) || DENSE(k=%d deg=%.2f clust=%.3f): %s best_struct=%.3f best_rel=%.3f CODE=%.3f || "
        "density_delta_rel(GATE)=%s density_delta_full=%s density_delta_code=%s rises(>=%.2f)=%s || "
        "SIGNAL_EXISTS(best>=%.2f)=%s CAPS_NEAR_CODES(best<=%.2f)=%s best_minus_code=%s || seeds=%d" % (
            verdict, sparse_deg, sparse_clust, n_ho_sparse,
            " ".join("%s=%.3f" % (m, sparse_methods[m]["auc_far"]) for m in STRUCTURAL_METHODS),
            best_sparse, best_rel_sparse, code_sparse, code_repro_ok, CODES_M5_REF,
            kcore_k, dense_deg, dense_clust,
            " ".join("%s=%.3f" % (m, dense_methods[m]["auc_far"]) for m in STRUCTURAL_METHODS),
            best_dense, best_rel_dense, code_dense,
            _fmt(density_delta), _fmt(density_delta_full), _fmt(density_delta_code), DENSITY_RISE_MARGIN, density_rises,
            SIGNAL_EXISTS_AUC, signal_exists, CAP_NEAR_CODES_AUC, caps_near_codes, _fmt(beats_codes),
            len(per_seed)))

    gates = dict(
        verdict=verdict,
        best_structural_auc_far_sparse=best_sparse, best_structural_auc_far_dense=best_dense,
        best_relational_auc_far_sparse=best_rel_sparse, best_relational_auc_far_dense=best_rel_dense,
        code_cosine_auc_far_sparse=code_sparse, code_cosine_auc_far_dense=code_dense, best_minus_code=beats_codes,
        density_delta_relational_GATE=density_delta, density_delta_full=density_delta_full,
        density_delta_code=density_delta_code, density_rises=density_rises,
        signal_exists=signal_exists, caps_near_codes=caps_near_codes,
        code_repro_ok=code_repro_ok, enough_heldout=enough,
        sparse_mean_degree=sparse_deg, dense_mean_degree=dense_deg,
        sparse_mean_clustering=sparse_clust, dense_mean_clustering=dense_clust,
        kcore_k=kcore_k, n_heldout_sparse=n_ho_sparse,
        sparse_methods=sparse_methods, dense_methods=dense_methods,
        bands=dict(SIGNAL_EXISTS_AUC=SIGNAL_EXISTS_AUC, CAP_NEAR_CODES_AUC=CAP_NEAR_CODES_AUC,
                   DENSITY_RISE_MARGIN=DENSITY_RISE_MARGIN, CODES_M5_REF=CODES_M5_REF,
                   HELDOUT_FRAC=HELDOUT_FRAC, MIN_HELDOUT_EDGES=MIN_HELDOUT_EDGES),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test: SBM (signal present) vs ER (signal absent). Ladder MUST separate them.
# ---------------------------------------------------------------------------

def _planted_sbm(n_comm, comm_size, p_in, p_out, rng):
    n = n_comm * comm_size
    comm = np.repeat(np.arange(n_comm), comm_size)
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            p = p_in if comm[u] == comm[v] else p_out
            if rng.random() < p:
                edges.append((u, v))
    return n, np.asarray(edges, dtype=np.int64)


def _planted_er(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append((u, v))
    return n, np.asarray(edges, dtype=np.int64)


def _selftest_regime_best(n, edges, gcn_epochs, device, seed, tag):
    node_words = ["n%d" % i for i in range(n)]
    res = run_regime(tag, edges, np.zeros(len(edges), dtype=np.int64), node_words, None,
                     None, gcn_epochs, seed, device, out_dir=None, do_code=False)
    return res


def _mechanism_selftest(device):
    rng = np.random.default_rng(0)
    # SBM: 12 communities of 40, dense intra, sparse inter -> strong common-neighbor signal.
    n_s, e_s = _planted_sbm(12, 40, 0.35, 0.005, rng)
    sbm = _selftest_regime_best(n_s, e_s, 60, device, 7, "SBM")
    # ER: matched n, avg degree comparable, no clustering -> common-neighbor signal absent.
    avg_deg = 2.0 * len(e_s) / n_s
    p_er = min(0.99, avg_deg / (n_s - 1))
    n_e, e_e = _planted_er(n_s, p_er, rng)
    er = _selftest_regime_best(n_e, e_e, 60, device, 7, "ER")

    best_sbm = sbm.get("best_structural_auc_far", float("nan"))
    # classic-only best on ER (GCN can pick up PA/degree noise; the parameter-free predictors are the null test)
    er_classic = [er["methods"][m]["auc_far"] for m in [CN, AA, RA, JC]
                  if m in er["methods"] and er["methods"][m]["auc_far"] == er["methods"][m]["auc_far"]]
    best_er_classic = max(er_classic) if er_classic else float("nan")
    sbm_cn = sbm["methods"].get(CN, {}).get("auc_far", float("nan"))

    signal_detected = bool(best_sbm == best_sbm and best_sbm >= 0.85)
    null_when_absent = bool(best_er_classic == best_er_classic and best_er_classic <= 0.65)
    gap_ok = bool(best_sbm == best_sbm and best_er_classic == best_er_classic
                  and (best_sbm - best_er_classic) >= 0.20)
    # arms differ: at least 6 distinct score signatures among the 6 structural methods on SBM
    sig_vals = set(v for k, v in sbm.get("sigs", {}).items() if k in STRUCTURAL_METHODS and v not in ("gcn_failed",))
    arms_differ = bool(len(sig_vals) >= 5)

    res = dict(
        sbm_best=best_sbm, sbm_cn=sbm_cn, sbm_methods={m: sbm["methods"][m]["auc_far"] for m in sbm["methods"]},
        er_best_classic=best_er_classic, er_methods={m: er["methods"][m]["auc_far"] for m in er["methods"]},
        sbm_n=n_s, sbm_edges=int(len(e_s)), er_n=n_e, er_edges=int(len(e_e)),
        signal_detected=signal_detected, null_when_absent=null_when_absent, gap_ok=gap_ok,
        arms_differ=arms_differ,
    )
    ok = bool(signal_detected and null_when_absent and gap_ok and arms_differ)
    return ok, res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    device = torch.device("cpu") if args.device == "cpu" else torch.device(
        "cuda" if (args.device == "cuda" and torch.cuda.is_available()) else "cpu")

    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    _log("device=%s cuda=%s run_mode=%s" % (device, torch.cuda.is_available(), run_mode))

    st_ok, st_res = _mechanism_selftest(device)
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (ladder cannot separate SBM signal from ER null): %s" % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS graph-inductive-ceiling: ladder fires on SBM (best>=0.85), null on ER classic "
                        "(<=0.65), gap>=0.20, arms differ; classic predictors + GCN + AUC + Hits + k-core exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    edges = np.asarray(edges, dtype=np.int64)
    _log("subgraph: n_nodes=%d n_edges=%d rel_types=%d median_degree=%s"
         % (len(node_ids), edges.shape[0], T, meta.get("median_degree")))
    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["enc"]["code_dim"], role_rng)).to(device)

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, edges, rels, node_words, roles_t, cfg["enc"], cfg["gcn_epochs"],
                          cfg["min_core"], device, out_dir=out_dir_path)
            # ARMS-MUST-DIFFER (META_RULE_AF): structural methods produce distinct held-out score signatures.
            sig_vals = set(v for k, v in pm["sparse"]["sigs"].items()
                           if k in STRUCTURAL_METHODS and v not in ("gcn_failed", "code_failed"))
            if len(sig_vals) < 4:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct structural sigs"
                                   % (seed, len(sig_vals)))
            per_seed.append(pm)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=pm))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, subgraph_meta=meta))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=cfg["seeds"], config=dict(seeds=cfg["seeds"], n_nodes=cfg["n_nodes"],
                                                   gcn_epochs=cfg["gcn_epochs"], min_core=cfg["min_core"],
                                                   enc=cfg["enc"]),
                   subgraph_meta=meta, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
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
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
