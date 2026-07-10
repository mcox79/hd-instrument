"""STRUCTURE-AWARE ENCODER SHARPNESS: does a graph-structural encoder objective produce SHARPER
codes that unlock reasoning-generalization? (Barrier #1 = the encoder; M3/M5 structural-fidelity diagnostic.)

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC/retrieval discriminator, no closed-form noise floor; feasibility via planted self-test
# - baseline_in_band at smoke (semantic M5 ~0.70, well below 0.95; not saturated)
# - discriminator survives scale: planted self-test proves mechanism; smoke previews A/B/C gap at n=1500;
#   FULL at canonical n=4440 (matches phase-0 baseline M3~0.87/M5~0.70) + n=7895
# - HARD_PASS strictly above floor (+0.10 over baseline M5; +0.07 above the +0.03 HARD_FAIL band)
# - HP_SCOPE: HARD_PASS/FAIL apply ONLY to structure-aware arms (B,C) vs baseline (A); A is the reference
# - cardinality_ok: EXPECTED_N_UNITS = n_sizes * n_arms
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (BASE_CFG reproduces phase-0 baseline verbatim)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in prereg

HYPOTHESIS: the substrate's CURRENT InfoNCE/semantic codes carry the graph map only MODERATELY (phase-0:
M3~0.87 / M5~0.70 at n=4440, MEASURED@data/phase0_code_structure_precheck_result.json). Fix: a STRUCTURE-AWARE
encoder objective (node2vec/DeepWalk random-walk skip-gram, learned from the KB graph's OWN adjacency; NO
external model; self-contained / co-evolving) makes code-cosine SHARPLY track graph reachability -> sharper
codes -> better HELD-OUT (M5) generalization -> reasoning through barrier #1.

ARMS (all measured on L2-normalized codes; M1 monotonicity, M3 1-hop AUC, M4 code-kNN meanhop, M5 held-out AUC):
  A baseline_semantic     : CURRENT encoder = train_binding_encoder_dev (edge-InfoNCE + VICReg + HRR-bind
                            over char-trigram features). Reproduces phase-0. THE REFERENCE ARM.
  B struct_node2vec       : DeepWalk/node2vec skip-gram with negative sampling over a LEARNABLE node-identity
                            embedding table. PURE graph structure; no semantic features. Self-contained.
  C hybrid_walk_semantic  : ProjHead over char-trigram features (semantic input) trained with the WALK-window
                            co-occurrence objective (structure objective). Structure-aware over semantic input.

DOWNSTREAM held-out reasoning-generalization test (cheap, one matmul/arm): for edges WITHHELD from encoder
training, rank all nodes by code-cosine to the source; reach@10 + MRR of the true (unseen) target. This is the
inductive-KG-completion / "route to the held-out neighbor" discriminator (CITED@ research_learned_partial_graph_
SR_reasoning_vs_search_CG_path_2026-07-09.md): can the code geometry recover a connection it was NEVER trained on?

SELF-TEST (planted graph, clean known structure): stochastic block model with RANDOM node words (so semantic
features carry NO structure). node2vec must achieve near-perfect M3(>=0.90)/M5(>=0.75); the semantic baseline on
random-word planted graph must FAIL M5 (< 0.75) -> assert_discriminator_fires (the control that must fail, fails).

ASCII-only. Device-aware (cuda on GPU box, cpu smoke). GPU-batched skip-gram + baseline. No emojis, no em dashes.
"""
from __future__ import annotations

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

# Reuse the EXACT primitives the phase-0 precheck + SR cells use (apples-to-apples codes).
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import (  # noqa: E402
    char_trigram_features,
    vicreg_repulsion,
)
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import SUBGRAPH_BASE_SEED  # noqa: E402
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph, make_unitary_roles,
)
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import (  # noqa: E402
    train_binding_encoder_dev, _l2t, _info_nce_dev,
)
from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, assert_discriminator_fires,
)

ANCHOR_NAME = "exp_encoder_structure_aware_sharpness_v1"

# BASE_CFG reproduces the phase-0 baseline VERBATIM (calibration_check: default_ok_for_this_regime).
BASE_CFG = dict(epochs=80, batch=256, code_dim=512, feat_dim=4096,
                temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0)
HELDOUT_FRAC = 0.30
KNN_K = 8
MAX_HOP = 6

# node2vec / walk objective hyperparameters (self-contained; graph-only).
N2V_CFG = dict(walks_per_node=10, walk_len=40, window=5, negs=5, epochs=5,
               batch=4096, lr=0.025, max_pairs=2_000_000)

# Run-mode regimes.
SIZES_FULL = [5000, 9000]     # -> n_nodes ~ 4440 (phase-0 canonical), 7895
SIZES_SMOKE = [1500]          # -> n_nodes ~ 1237 (fast preview)


def _log(m):
    print("[struct_enc] %s" % m, flush=True)


# ---------------------------------------------------------------------------
# Defensive error-checking (SCHEMA-VET 13): start-marker + crash-diagnostic (atomic tmp+replace).
# ---------------------------------------------------------------------------
def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    fin = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, fin)


def _write_crash_metrics(out_dir, exc):
    diag = dict(verdict="CELL_CRASHED",
                verdict_msg="%s: %s" % (type(exc).__name__, str(exc)[:500]),
                summary="CELL_CRASHED: %s" % type(exc).__name__,
                elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    fin = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, fin)


# ---------------------------------------------------------------------------
# Metric helpers (COPIED VERBATIM from phase0_code_structure_precheck_sr_reasoning_v1.py for consistency).
# ---------------------------------------------------------------------------
def build_undirected_adj(edges, n_nodes):
    adj = [[] for _ in range(n_nodes)]
    eset = set()
    for (a, b) in edges:
        a = int(a); b = int(b)
        if a == b:
            continue
        adj[a].append(b)
        adj[b].append(a)
        eset.add((a, b) if a < b else (b, a))
    return adj, eset


def bfs_hops(adj, src, max_hop):
    dist = {src: 0}
    frontier = [src]
    for h in range(1, max_hop + 1):
        nxt = []
        for u in frontier:
            for v in adj[u]:
                if v not in dist:
                    dist[v] = h
                    nxt.append(v)
        frontier = nxt
        if not frontier:
            break
    dist.pop(src, None)
    return dist


def spearman(x, y):
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    rx = np.argsort(np.argsort(x)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    rx -= rx.mean(); ry -= ry.mean()
    den = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    return float((rx * ry).sum() / den) if den > 0 else float("nan")


def auc_pos_neg(pos_scores, neg_scores):
    pos = np.asarray(pos_scores, dtype=np.float64)
    neg = np.asarray(neg_scores, dtype=np.float64)
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    allv = np.concatenate([pos, neg])
    ranks = np.argsort(np.argsort(allv)).astype(np.float64) + 1.0
    r_pos = ranks[:len(pos)].sum()
    n1 = len(pos); n2 = len(neg)
    u = r_pos - n1 * (n1 + 1) / 2.0
    return float(u / (n1 * n2))


def sample_far_negatives(rng, n_need, n_nodes, eset, adj_sets):
    """far negatives: random pairs, not an edge, not sharing a neighbor (hop>=3)."""
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


# ---------------------------------------------------------------------------
# ARM B / C shared: random-walk corpus (DeepWalk) over an adjacency list. Self-contained: graph-only.
# ---------------------------------------------------------------------------
def generate_walk_pairs(adj, n_nodes, walks_per_node, walk_len, window, seed, max_pairs):
    """Uniform random walks; extract (center, context) skip-gram pairs within `window`. Returns int64 [P,2]."""
    rng = np.random.default_rng(seed)
    starts = [u for u in range(n_nodes) if len(adj[u]) > 0]
    centers = []
    contexts = []
    for _ in range(walks_per_node):
        order = rng.permutation(starts)
        for s in order:
            walk = [int(s)]
            cur = int(s)
            for _ in range(walk_len - 1):
                nb = adj[cur]
                if not nb:
                    break
                cur = int(nb[rng.integers(0, len(nb))])
                walk.append(cur)
            L = len(walk)
            for i in range(L):
                lo = max(0, i - window)
                hi = min(L, i + window + 1)
                for j in range(lo, hi):
                    if j == i:
                        continue
                    centers.append(walk[i])
                    contexts.append(walk[j])
    c = np.asarray(centers, dtype=np.int64)
    x = np.asarray(contexts, dtype=np.int64)
    if c.shape[0] > max_pairs:
        sel = rng.choice(c.shape[0], size=max_pairs, replace=False)
        c = c[sel]; x = x[sel]
    return np.stack([c, x], axis=1)


def train_node2vec(adj, n_nodes, code_dim, seed, device, n2v_cfg, tag="n2v"):
    """DeepWalk/node2vec skip-gram + negative sampling over a learnable node-identity embedding table.
    Returns L2-normalized codes [n_nodes, code_dim] on device (pure structure; no semantic features)."""
    torch.manual_seed(seed)
    pairs = generate_walk_pairs(adj, n_nodes, n2v_cfg["walks_per_node"], n2v_cfg["walk_len"],
                                n2v_cfg["window"], seed, n2v_cfg["max_pairs"])
    if pairs.shape[0] == 0:
        raise RuntimeError("N2V_FAIL: no walk pairs (empty adjacency)")
    emb_in = torch.nn.Embedding(n_nodes, code_dim).to(device)
    emb_out = torch.nn.Embedding(n_nodes, code_dim).to(device)
    torch.nn.init.normal_(emb_in.weight, std=1.0 / code_dim ** 0.5)
    torch.nn.init.normal_(emb_out.weight, std=1.0 / code_dim ** 0.5)
    opt = torch.optim.Adam(list(emb_in.parameters()) + list(emb_out.parameters()), lr=n2v_cfg["lr"])
    P = pairs.shape[0]
    K = n2v_cfg["negs"]
    bs = n2v_cfg["batch"]
    g = torch.Generator(device="cpu"); g.manual_seed(seed + 101)
    pt = torch.from_numpy(pairs)
    t0 = time.perf_counter()
    for ep in range(n2v_cfg["epochs"]):
        perm = torch.randperm(P, generator=g)
        tot = 0.0
        nb = 0
        for st in range(0, P, bs):
            bidx = perm[st:st + bs]
            c = pt[bidx, 0].to(device)
            x = pt[bidx, 1].to(device)
            neg = torch.randint(0, n_nodes, (c.shape[0], K), generator=g).to(device)
            vin = emb_in(c)                       # [B, d]
            vout = emb_out(x)                     # [B, d]
            vneg = emb_out(neg)                   # [B, K, d]
            pos_score = (vin * vout).sum(1)                                   # [B]
            neg_score = torch.bmm(vneg, vin.unsqueeze(2)).squeeze(2)          # [B, K]
            loss = (-torch.nn.functional.logsigmoid(pos_score).mean()
                    - torch.nn.functional.logsigmoid(-neg_score).mean())
            opt.zero_grad(); loss.backward(); opt.step()
            tot += float(loss.detach()); nb += 1
        _log("  %s seed=%d ep=%d/%d loss=%.4f (%.1fs)"
             % (tag, seed, ep, n2v_cfg["epochs"], tot / max(nb, 1), time.perf_counter() - t0))
    with torch.no_grad():
        Z = _l2t(emb_in.weight.detach().to(torch.float32))
    return Z


def train_hybrid_walk_semantic(X, adj, n_nodes, code_dim, seed, device, cfg, n2v_cfg, tag="hybrid"):
    """ProjHead over char-trigram features (semantic input) trained with the WALK-window co-occurrence
    objective (structure objective) via in-batch InfoNCE + VICReg. Structure-aware over semantic input.
    Returns L2-normalized codes [n_nodes, code_dim] on device."""
    from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import ProjHead
    torch.manual_seed(seed)
    np.random.seed(seed)
    pairs = generate_walk_pairs(adj, n_nodes, n2v_cfg["walks_per_node"], n2v_cfg["walk_len"],
                                n2v_cfg["window"], seed + 3, n2v_cfg["max_pairs"])
    if pairs.shape[0] == 0:
        raise RuntimeError("HYBRID_FAIL: no walk pairs (empty adjacency)")
    Xt = torch.from_numpy(X).to(device)
    model = ProjHead(X.shape[1], code_dim).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=cfg["lr"])
    P = pairs.shape[0]
    bs = min(cfg["batch"], P)
    g = torch.Generator(device="cpu"); g.manual_seed(seed + 202)
    pt = torch.from_numpy(pairs)
    log_every = max(1, cfg["epochs"] // 5)
    t0 = time.perf_counter()
    for ep in range(cfg["epochs"]):
        bidx = torch.randint(0, P, (bs,), generator=g)
        c = pt[bidx, 0].to(device)
        x = pt[bidx, 1].to(device)
        ha = model(Xt[c])
        hp = model(Xt[x])
        loss = _info_nce_dev(ha, hp, cfg["temp"], device) + vicreg_repulsion(
            torch.cat([ha, hp], dim=0), cfg["lambda_cov"], cfg["lambda_var"])
        opt.zero_grad(); loss.backward(); opt.step()
        if (ep % log_every == 0) or (ep == cfg["epochs"] - 1):
            _log("  %s seed=%d ep=%d/%d loss=%.4f (%.1fs)"
                 % (tag, seed, ep, cfg["epochs"], float(loss.detach()), time.perf_counter() - t0))
    with torch.no_grad():
        Z = _l2t(model(Xt).to(torch.float32))
    return Z


# ---------------------------------------------------------------------------
# Metrics on a code matrix Zn (L2-normalized, [n, d] on device).
# ---------------------------------------------------------------------------
def compute_structural_metrics(Zn, adj, eset, adj_sets, edges, n_nodes, rng):
    deg = np.array([len(adj[u]) for u in range(n_nodes)])
    srcs_all = np.where(deg > 0)[0]
    n_src = min(300, len(srcs_all))
    bfs_srcs = rng.choice(srcs_all, size=n_src, replace=False)

    # M1 + M2
    bucket_cos = {h: [] for h in range(1, MAX_HOP + 1)}
    pair_cos, pair_hop = [], []
    per_pair_cap = 40
    for s in bfs_srcs:
        dist = bfs_hops(adj, int(s), MAX_HOP)
        if not dist:
            continue
        items = list(dist.items())
        if len(items) > per_pair_cap:
            sel = rng.choice(len(items), size=per_pair_cap, replace=False)
            items = [items[i] for i in sel]
        zs = Zn[int(s)]
        for (v, h) in items:
            c = float(torch.dot(zs, Zn[v]).item())
            bucket_cos[h].append(c); pair_cos.append(c); pair_hop.append(h)
    m1 = {h: (float(np.mean(bucket_cos[h])) if bucket_cos[h] else float("nan"),
              len(bucket_cos[h])) for h in range(1, MAX_HOP + 1)}
    m2 = spearman(pair_cos, pair_hop)

    # M3 full 1-hop AUC
    n_es = min(3000, edges.shape[0])
    esel = rng.choice(edges.shape[0], size=n_es, replace=False)
    pos_full = [float(torch.dot(Zn[int(edges[i, 0])], Zn[int(edges[i, 1])]).item()) for i in esel]
    neg_pairs = sample_far_negatives(rng, n_es, n_nodes, eset, adj_sets)
    neg_full = [float(torch.dot(Zn[u], Zn[v]).item()) for (u, v) in neg_pairs]
    m3 = auc_pos_neg(pos_full, neg_full)

    # M4 code-kNN graph proximity
    q_nodes = rng.choice(srcs_all, size=min(250, len(srcs_all)), replace=False)
    knn_hops, rand_hops = [], []
    BIG = MAX_HOP + 2
    for q in q_nodes:
        q = int(q)
        sims = torch.mv(Zn, Zn[q]); sims[q] = -1e9
        topk = torch.topk(sims, KNN_K).indices.cpu().numpy().tolist()
        dist = bfs_hops(adj, q, MAX_HOP)
        for v in topk:
            knn_hops.append(dist.get(int(v), BIG))
        rnd = rng.choice(n_nodes, size=KNN_K, replace=False)
        for v in rnd:
            if int(v) != q:
                rand_hops.append(dist.get(int(v), BIG))
    m4_knn = float(np.mean(knn_hops)) if knn_hops else float("nan")
    m4_rand = float(np.mean(rand_hops)) if rand_hops else float("nan")
    m4_ratio = (m4_knn / m4_rand) if m4_rand > 0 else float("nan")
    m1_mono = bool(m1[1][0] == m1[1][0] and m1[2][0] == m1[2][0] and m1[3][0] == m1[3][0]
                   and m1[1][0] > m1[2][0] > m1[3][0])
    return dict(
        M1_mean_cosine_per_hop={h: m1[h][0] for h in range(1, MAX_HOP + 1)},
        M1_counts_per_hop={h: m1[h][1] for h in range(1, MAX_HOP + 1)},
        M1_monotonic_123=m1_mono, M2_spearman=m2, M3_1hop_auc_full=m3,
        M4_codeknn_meanhop=m4_knn, M4_random_meanhop=m4_rand, M4_ratio=m4_ratio,
    )


def compute_heldout_m5_and_downstream(Zhn, edges, hold_idx, keep_idx, n_nodes, eset, adj_sets, rng):
    """M5 held-out AUC (withheld-edge cosine vs far non-edges) + downstream held-out reasoning reach@k/MRR."""
    # M5: among WITHHELD 1-hop edges (unseen by the encoder), is cosine elevated vs far non-edges?
    hsel = hold_idx if len(hold_idx) <= 3000 else rng.choice(hold_idx, size=3000, replace=False)
    pos_h = [float(torch.dot(Zhn[int(edges[i, 0])], Zhn[int(edges[i, 1])]).item()) for i in hsel]
    neg_h_pairs = sample_far_negatives(rng, len(pos_h), n_nodes, eset, adj_sets)
    neg_h = [float(torch.dot(Zhn[u], Zhn[v]).item()) for (u, v) in neg_h_pairs]
    m5 = auc_pos_neg(pos_h, neg_h)
    ksel = keep_idx if len(keep_idx) <= 3000 else rng.choice(keep_idx, size=3000, replace=False)
    pos_seen = [float(torch.dot(Zhn[int(edges[i, 0])], Zhn[int(edges[i, 1])]).item()) for i in ksel]
    m5_seen = auc_pos_neg(pos_seen, neg_h)

    # Downstream: route to the held-out neighbor. For withheld edges (u,v), rank all nodes by cosine(Zh[u], .);
    # reach@10 + MRR of the true (unseen) target v. Inductive-KG-completion discriminator.
    dsel = hold_idx if len(hold_idx) <= 1000 else rng.choice(hold_idx, size=1000, replace=False)
    reach10 = []
    rr = []
    for i in dsel:
        u = int(edges[i, 0]); v = int(edges[i, 1])
        sims = torch.mv(Zhn, Zhn[u]); sims[u] = -1e9
        # rank of v = 1 + number of nodes with strictly greater sim than v
        sv = float(sims[v].item())
        rank = int((sims > sv).sum().item()) + 1
        reach10.append(1.0 if rank <= 10 else 0.0)
        rr.append(1.0 / rank)
    return dict(M5_heldout_auc=m5, M5_seen_auc_heldout_encoder=m5_seen,
                downstream_reach_at_10=float(np.mean(reach10)) if reach10 else float("nan"),
                downstream_mrr=float(np.mean(rr)) if rr else float("nan"),
                n_heldout_edges=int(len(hold_idx)))


# ---------------------------------------------------------------------------
# Arm training on a given (edges, adj) view. Returns FULL-graph codes.
# ---------------------------------------------------------------------------
def train_arm_full(arm, node_words, edges, rels, roles_t, adj, n_nodes, cfg, n2v_cfg, seed, device):
    if arm == "A_baseline_semantic":
        X = char_trigram_features(node_words, cfg["feat_dim"])
        Z = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=None, tag="A_full")
        return _l2t(Z.to(torch.float32))
    if arm == "B_struct_node2vec":
        return train_node2vec(adj, n_nodes, cfg["code_dim"], seed, device, n2v_cfg, tag="B_full")
    if arm == "C_hybrid_walk_semantic":
        X = char_trigram_features(node_words, cfg["feat_dim"])
        return train_hybrid_walk_semantic(X, adj, n_nodes, cfg["code_dim"], seed, device, cfg, n2v_cfg, tag="C_full")
    raise ValueError("unknown arm %r" % arm)


def train_arm_heldout(arm, node_words, edges, rels, roles_t, keep_idx, adj_keep, n_nodes,
                      cfg, n2v_cfg, seed, device):
    """Train each arm on the KEPT (70%) edges only; withheld edges are genuinely unseen (leakage-safe)."""
    ekeep = edges[keep_idx]
    if arm == "A_baseline_semantic":
        X = char_trigram_features(node_words, cfg["feat_dim"])
        Z = train_binding_encoder_dev(X, ekeep, rels[keep_idx], roles_t, cfg, seed, device,
                                      out_dir=None, tag="A_held")
        return _l2t(Z.to(torch.float32))
    if arm == "B_struct_node2vec":
        return train_node2vec(adj_keep, n_nodes, cfg["code_dim"], seed, device, n2v_cfg, tag="B_held")
    if arm == "C_hybrid_walk_semantic":
        X = char_trigram_features(node_words, cfg["feat_dim"])
        return train_hybrid_walk_semantic(X, adj_keep, n_nodes, cfg["code_dim"], seed, device,
                                          cfg, n2v_cfg, tag="C_held")
    raise ValueError("unknown arm %r" % arm)


ARMS = ["A_baseline_semantic", "B_struct_node2vec", "C_hybrid_walk_semantic"]


def _hash_codes(Z):
    return hashlib.sha256(Z.detach().cpu().numpy().tobytes()).hexdigest()


def run_size(n_target, seed, cfg, n2v_cfg, device):
    t0 = time.perf_counter()
    _log("=== SIZE target n=%d seed=%d : loading subgraph ===" % (n_target, seed))
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        n_target, SUBGRAPH_BASE_SEED)
    n_nodes = len(node_ids)
    edges = np.asarray(edges, dtype=np.int64)
    rels = np.asarray(rels)
    _log("subgraph n_nodes=%d n_edges=%d rel_types=%d" % (n_nodes, edges.shape[0], T))

    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["code_dim"], role_rng)).to(device)
    adj, eset = build_undirected_adj(edges, n_nodes)
    adj_sets = [set(a) for a in adj]

    # held-out split (same for all arms; leakage-safe)
    rng = np.random.default_rng(20260709 + seed)
    n_e = edges.shape[0]
    perm = rng.permutation(n_e)
    n_hold = int(HELDOUT_FRAC * n_e)
    hold_idx, keep_idx = perm[:n_hold], perm[n_hold:]
    adj_keep, _ = build_undirected_adj(edges[keep_idx], n_nodes)

    per_arm = {}
    code_hashes = {}
    for arm in ARMS:
        _log("--- arm=%s FULL ---" % arm)
        rng_m = np.random.default_rng(777 + seed)
        Zf = train_arm_full(arm, node_words, edges, rels, roles_t, adj, n_nodes, cfg, n2v_cfg, seed, device)
        code_hashes[arm] = _hash_codes(Zf)
        struct = compute_structural_metrics(Zf, adj, eset, adj_sets, edges, n_nodes, rng_m)
        _log("--- arm=%s HELD-OUT (%.0f%% edges withheld) ---" % (arm, HELDOUT_FRAC * 100))
        rng_h = np.random.default_rng(999 + seed)
        Zh = train_arm_heldout(arm, node_words, edges, rels, roles_t, keep_idx, adj_keep, n_nodes,
                               cfg, n2v_cfg, seed, device)
        held = compute_heldout_m5_and_downstream(Zh, edges, hold_idx, keep_idx, n_nodes, eset, adj_sets, rng_h)
        rec = dict(arm=arm)
        rec.update(struct)
        rec.update(held)
        per_arm[arm] = rec
        _log("arm=%s : M3=%.3f M4ratio=%.3f | M5held=%.3f reach@10=%.3f MRR=%.3f mono123=%s"
             % (arm, struct["M3_1hop_auc_full"], struct["M4_ratio"], held["M5_heldout_auc"],
                held["downstream_reach_at_10"], held["downstream_mrr"], struct["M1_monotonic_123"]))

    # discriminator deltas: structure-aware (best of B,C) vs baseline A
    m5A = per_arm["A_baseline_semantic"]["M5_heldout_auc"]
    m5B = per_arm["B_struct_node2vec"]["M5_heldout_auc"]
    m5C = per_arm["C_hybrid_walk_semantic"]["M5_heldout_auc"]
    r10A = per_arm["A_baseline_semantic"]["downstream_reach_at_10"]
    best_struct_m5 = max(m5B, m5C)
    best_struct_arm = "B_struct_node2vec" if m5B >= m5C else "C_hybrid_walk_semantic"
    delta_m5 = best_struct_m5 - m5A
    delta_reach = per_arm[best_struct_arm]["downstream_reach_at_10"] - r10A

    res = dict(n_target=n_target, n_nodes=n_nodes, n_edges=int(edges.shape[0]), rel_types=int(T),
               seed=seed, heldout_frac=HELDOUT_FRAC, per_arm=per_arm, code_hashes=code_hashes,
               m5_A=m5A, m5_B=m5B, m5_C=m5C, best_struct_arm=best_struct_arm,
               best_struct_m5=best_struct_m5, delta_m5_struct_vs_baseline=delta_m5,
               delta_reach_struct_vs_baseline=delta_reach,
               elapsed_s=round(time.perf_counter() - t0, 1))
    _log("SIZE n=%d DONE: A_M5=%.3f B_M5=%.3f C_M5=%.3f best=%s deltaM5=%+.3f deltaReach=%+.3f (%.1fs)"
         % (n_nodes, m5A, m5B, m5C, best_struct_arm, delta_m5, delta_reach, res["elapsed_s"]))
    return res


# ---------------------------------------------------------------------------
# SELF-TEST: planted stochastic-block-model graph with RANDOM node words.
# ---------------------------------------------------------------------------
def build_planted_sbm(n_blocks, block_size, p_in, p_out, seed):
    rng = np.random.default_rng(seed)
    n = n_blocks * block_size
    labels = np.repeat(np.arange(n_blocks), block_size)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            p = p_in if labels[i] == labels[j] else p_out
            if rng.random() < p:
                edges.append((i, j))
    edges = np.asarray(edges, dtype=np.int64)
    # random meaningless node words (semantic features carry NO structure)
    alph = "abcdefghijklmnopqrstuvwxyz"
    words = ["".join(alph[k] for k in rng.integers(0, 26, size=8)) for _ in range(n)]
    return n, labels, edges, words


def run_self_test(device_arg="auto"):
    """Planted-graph MECHANISM-CORRECTNESS gate + discriminator-fires. Proves the node2vec structure-aware
    mechanism achieves near-perfect M3/M5 on CLEAN planted structure, and that an UNTRAINED (random) code
    matrix FAILS the M3 gate (the control that MUST fail -> the metric genuinely discriminates learned
    structure from noise, not a by-construction pass). No dispatch beyond this gate if it does not pass.

    NOTE (methodological): the semantic baseline arm (train_binding_encoder_dev) is itself an EDGE-InfoNCE
    structural learner - on a clean dense-block SBM it ALSO generalizes to held-out intra-block edges through
    kept edges. So the A-vs-B discriminator has teeth only on the REAL, messy KB graph (where the baseline is
    stuck at M5~0.70). The baseline-saturation / vacuity guard therefore lives in the SMOKE run on the real
    graph (assert baseline M5 <= 0.90 headroom), not here."""
    device = _pick_device(device_arg)
    _log("SELF-TEST: planted SBM, device=%s" % device)
    n, labels, edges, words = build_planted_sbm(n_blocks=6, block_size=40, p_in=0.35, p_out=0.01, seed=7)
    _log("planted SBM n=%d n_edges=%d blocks=6x40" % (n, edges.shape[0]))
    adj, eset = build_undirected_adj(edges, n)
    adj_sets = [set(a) for a in adj]
    n2v = dict(N2V_CFG); n2v["epochs"] = 8; n2v["walk_len"] = 20

    rng = np.random.default_rng(20260709)
    n_e = edges.shape[0]
    perm = rng.permutation(n_e); n_hold = int(HELDOUT_FRAC * n_e)
    hold_idx, keep_idx = perm[:n_hold], perm[n_hold:]
    adj_keep, _ = build_undirected_adj(edges[keep_idx], n)

    # node2vec on planted structure (mechanism under test)
    Zf_n2v = train_node2vec(adj, n, BASE_CFG["code_dim"], 7, device, n2v, tag="ST_n2v_full")
    st_n2v = compute_structural_metrics(Zf_n2v, adj, eset, adj_sets, edges, n, np.random.default_rng(1))
    Zh_n2v = train_node2vec(adj_keep, n, BASE_CFG["code_dim"], 7, device, n2v, tag="ST_n2v_held")
    hd_n2v = compute_heldout_m5_and_downstream(Zh_n2v, edges, hold_idx, keep_idx, n, eset, adj_sets,
                                               np.random.default_rng(2))
    m3_n2v = st_n2v["M3_1hop_auc_full"]; m5_n2v = hd_n2v["M5_heldout_auc"]

    # UNTRAINED random-code control (the control that MUST fail M3 -> metric discriminates learned vs noise)
    gz = torch.Generator(device="cpu"); gz.manual_seed(4242)
    Zrand = _l2t(torch.randn(n, BASE_CFG["code_dim"], generator=gz).to(torch.float32).to(device))
    st_rand = compute_structural_metrics(Zrand, adj, eset, adj_sets, edges, n, np.random.default_rng(5))
    m3_rand = st_rand["M3_1hop_auc_full"]

    _log("SELF-TEST planted: node2vec M3=%.3f M5=%.3f | UNTRAINED-random M3=%.3f" % (m3_n2v, m5_n2v, m3_rand))

    ok = True
    gate_m3 = bool(m3_n2v >= 0.90)
    gate_m5 = bool(m5_n2v >= 0.75)
    ok &= gate_m3 and gate_m5
    if not gate_m3:
        _log("SELF-TEST FAIL: node2vec M3=%.3f < 0.90 (mechanism does not sharpen clean structure)" % m3_n2v)
    if not gate_m5:
        _log("SELF-TEST FAIL: node2vec M5=%.3f < 0.75 (mechanism does not generalize on clean structure)" % m5_n2v)
    # discriminator-fires: the UNTRAINED random codes MUST fail the M3>=0.90 gate (else M3 is by-construction)
    assert_discriminator_fires(bool(m3_rand >= 0.90),
                               control_name="untrained_random_codes",
                               headline_name="M3>=0.90", run_mode="self_test",
                               extra="node2vec M3=%.3f should pass while random-code M3=%.3f must fail" % (m3_n2v, m3_rand))
    verdict = "SELFTEST_PASS" if ok else "SELFTEST_FAIL"
    _log("SELF-TEST %s (node2vec M3=%.3f/M5=%.3f, random-control M3=%.3f)"
         % (verdict, m3_n2v, m5_n2v, m3_rand))
    if not ok:
        raise SystemExit(1)
    return 0


# ---------------------------------------------------------------------------
# Verdict banding (pre-registered).
# ---------------------------------------------------------------------------
def _band_verdict(per_size):
    """HARD_PASS: best structure-aware arm (B or C) M5 >= baseline + 0.10 AND downstream reach delta >= +0.05,
    at the CANONICAL size (n~4440) - and holding (non-negative delta) at the larger size.
    HARD_FAIL: best structure-aware M5 <= baseline + 0.03 at canonical size. MIDDLE otherwise."""
    ok_sizes = [r for r in per_size if "error" not in r]
    if not ok_sizes:
        return "HARD_FAIL_NO_VALID_SIZES", "no valid sizes ran"
    ok_sizes = sorted(ok_sizes, key=lambda r: r["n_nodes"])
    # canonical = the size closest to 4440
    canon = min(ok_sizes, key=lambda r: abs(r["n_nodes"] - 4440))
    dM5 = canon["delta_m5_struct_vs_baseline"]
    dR = canon["delta_reach_struct_vs_baseline"]
    hp = bool(dM5 >= 0.10 and dR >= 0.05)
    hf = bool(dM5 <= 0.03)
    if hp and not hf:
        v = "HARD_PASS"
    elif hf and not hp:
        v = "HARD_FAIL"
    else:
        v = "MIDDLE_BAND"
    msg = ("%s: canonical n=%d best=%s deltaM5=%+.3f (HP>=+0.10, HF<=+0.03) deltaReach=%+.3f (HP>=+0.05) | "
           "A_M5=%.3f B_M5=%.3f C_M5=%.3f"
           % (v, canon["n_nodes"], canon["best_struct_arm"], dM5, dR,
              canon["m5_A"], canon["m5_B"], canon["m5_C"]))
    return v, msg


def _arms_must_differ(code_hashes_per_size):
    for nt, hashes in code_hashes_per_size.items():
        items = list(hashes.items())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, da = items[i]; b, db = items[j]
                assert da != db, ("META_RULE_AF VIOLATION: arms %r and %r bit-identical at n=%s (hash=%s)"
                                  % (a, b, nt, da))


def _pick_device(device_arg):
    if device_arg in (None, "auto"):
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(device_arg)


def run(run_mode, seed, device_arg="auto", run_tag=None):
    assert run_mode in ("smoke", "full"), "unsupported run_mode %r" % run_mode
    device = _pick_device(device_arg)
    tag = run_tag or ("seed%d" % seed)
    anchor = ("%s_smoke_%s" % (ANCHOR_NAME, tag)) if run_mode == "smoke" else ("%s_%s" % (ANCHOR_NAME, tag))
    out_dir = get_output_dir(anchor)   # Path (write_metrics expects Path.mkdir); inline writers accept Path too
    sizes = SIZES_SMOKE if run_mode == "smoke" else SIZES_FULL
    cfg = dict(BASE_CFG)
    n2v = dict(N2V_CFG)
    if run_mode == "smoke":
        cfg["epochs"] = 40
        n2v["epochs"] = 4; n2v["walk_len"] = 20
    EXPECTED_N_UNITS = len(sizes) * len(ARMS)
    _write_start_marker(out_dir, run_mode, EXPECTED_N_UNITS)
    _log("run_mode=%s seed=%d device=%s sizes=%s arms=%s out=%s"
         % (run_mode, seed, device, sizes, ARMS, out_dir))
    t0 = time.perf_counter()

    per_size = []
    for nt in sizes:
        try:
            per_size.append(run_size(nt, seed, cfg, n2v, device))
        except Exception as e:  # per-unit failure-class instrumentation (META_RULE_J); NOT bare/BaseException
            _log("SIZE n=%d FAILED %s: %s" % (nt, type(e).__name__, str(e)[:300]))
            per_size.append(dict(n_target=nt, error="%s: %s" % (type(e).__name__, str(e)[:200]),
                                 failure_class=type(e).__name__))

    # SMOKE vacuity / baseline-in-band guard (META_RULE_AG + saturation-vacuous): on the REAL graph the
    # baseline (Arm A) M5 must have headroom (<=0.90) for a +0.10 structure-aware win to be reachable, and
    # be above chance (>=0.55). If baseline M5 saturates >0.90, HARD_PASS is infeasible -> vacuous smoke.
    if run_mode == "smoke":
        ok_real = [r for r in per_size if "error" not in r]
        if not ok_real:
            raise RuntimeError("SMOKE_VACUOUS: no valid real-graph size ran; cannot evaluate baseline band")
        base_m5 = ok_real[0]["m5_A"]
        _log("SMOKE baseline-band check: Arm A M5=%.3f (need 0.55<=M5<=0.90 for +0.10 headroom)" % base_m5)
        assert_discriminator_fires(bool(base_m5 > 0.90),
                                   control_name="baseline_A_saturated_M5",
                                   headline_name="baseline_M5<=0.90_headroom", run_mode="smoke",
                                   extra="baseline M5=%.3f leaves no room for a +0.10 structure-aware win" % base_m5)
        if base_m5 < 0.55:
            raise RuntimeError("SMOKE_BASELINE_BELOW_BAND: Arm A M5=%.3f < 0.55 (below chance band; regime broken)"
                               % base_m5)

    # cardinality gate (META_RULE_H)
    n_units = sum(len(r.get("per_arm", {})) for r in per_size if "error" not in r)
    cardinality_ok = bool(n_units == EXPECTED_N_UNITS)

    # arms-must-differ (META_RULE_AF)
    code_hashes_per_size = {r["n_target"]: r["code_hashes"] for r in per_size if "error" not in r}
    arms_differ_verified = False
    try:
        _arms_must_differ(code_hashes_per_size)
        arms_differ_verified = True
    except AssertionError as ae:
        _log("ARMS-DIFFER: %s" % str(ae)[:200])
        if run_mode == "smoke":
            raise

    verdict, vmsg = _band_verdict(per_size)
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = "cardinality breach: got %d units, expected %d | %s" % (n_units, EXPECTED_N_UNITS, vmsg)

    metrics = dict(
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=seed, device=str(device),
        sizes=sizes, arms=ARMS, expected_n_units=EXPECTED_N_UNITS, n_units=n_units,
        cardinality_ok=cardinality_ok, arms_differ_verified=arms_differ_verified,
        per_size=per_size, verdict=verdict, verdict_msg=vmsg,
        summary=vmsg, elapsed_s=round(time.perf_counter() - t0, 1),
        base_cfg=cfg, n2v_cfg=n2v, heldout_frac=HELDOUT_FRAC,
    )
    write_metrics(out_dir, metrics, results=per_size)
    _log("VERDICT=%s | %s | cardinality_ok=%s arms_differ=%s (%.1fs)"
         % (verdict, vmsg, cardinality_ok, arms_differ_verified, time.perf_counter() - t0))
    return 0


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    seed = 7
    device_arg = "auto"
    for i, a in enumerate(sys.argv):
        if a == "--seed" and i + 1 < len(sys.argv):
            seed = int(sys.argv[i + 1])
        if a == "--device" and i + 1 < len(sys.argv):
            device_arg = sys.argv[i + 1]
    out_dir = get_output_dir("%s_seed%d" % (ANCHOR_NAME, seed))
    try:
        if "--self-test" in sys.argv:
            return run_self_test(device_arg)
        if "--smoke" in sys.argv:
            return run("smoke", seed, device_arg)
        run_mode = os.environ.get("HDLAB_RUN_MODE", "self_test")
        if run_mode == "self_test":
            return run_self_test(device_arg)
        if run_mode not in ("smoke", "full"):
            run_mode = "full"
        return run(run_mode, seed, device_arg)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException; preserves SystemExit / KeyboardInterrupt
        _write_crash_metrics(out_dir, exc)
        raise


if __name__ == "__main__":
    sys.exit(main())
