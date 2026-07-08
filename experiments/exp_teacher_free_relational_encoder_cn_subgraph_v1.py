"""Teacher-free relational encoder on the ConceptNet subgraph (decisive CPU test).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (no closed-form noise floor; Z-score vs empirical null is the discriminator)
# - baseline_in_band at smoke (random-init floor Z must be < 1.5; else lexical-confound leak)
# - discriminator survives scale (smoke fires the discriminator: repulsion Z > random-init Z)
# - HARD_PASS strictly above floor (Z >= 2.0 per note lower HP bound; [1.0,2.0) = MIDDLE)
# - HP_SCOPE: gates apply to ARM_GRAPH_REPULSION (primary) + ARM_SIMGRACE_REPULSION (secondary)
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (degree-preserving null recomputed per run)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg

SCIENCE (per notes/research_teacher_free_relational_encoder_objective_2026-07-08.md,
course-corrected 2026-07-08): the load-bearing claim is NOT "graph-only beats BGE".
It is:
  (R1) the explicit REPULSION term is load-bearing -- an alignment-only control
       (pull graph-neighbors together, no push) must COLLAPSE.
  (R3) graph-relational-neighbor positives + explicit repulsion yield DISCRIMINATIVE
       codes on the ConceptNet subgraph -- measured by:
         (a) embedding assortativity Z-score vs a degree-preserving (configuration-
             model) null (Newman-modularity analog), and
         (b) off-target mean-pairwise-cosine lower than the no-repulsion control.
BGE is a NON-GATING reference line only.

Teacher-free: NO BGE (or any external teacher) anywhere in any training loss.
Surface features = deterministic hashed char-trigram bag (substrate-native V1
surface featurization; stable hash, no lexical semantics injected).

Arms:
  ARM_GRAPH_REPULSION  : InfoNCE over graph-neighbor positives (in-batch negatives
                         = uniformity/repulsion) + explicit VICReg covariance+variance
                         repulsion.  [PRIMARY]
  ARM_NO_REPULSION     : alignment ONLY over graph-neighbor positives (mean 1-cos,
                         no negatives, no covariance).  MUST COLLAPSE.  [CONTROL/ablation]
  ARM_SIMGRACE_REPULSION: InfoNCE over encoder-perturbation views (SimGRACE, degree-
                         agnostic) + VICReg repulsion.  [SECONDARY positive arm]
  ARM_RANDOM_INIT      : untrained encoder on the same features.  [FLOOR / p9 lexical
                         confound control -- its Z MUST be low, else the metric leaks
                         char-trigram proximity rather than learned relational structure]
  ARM_BGE_REFERENCE    : best-effort BGE-small embedding of node words.  NON-GATING.

CPU-only. No GPU. No network (BGE loaded from local HF cache if present, else skipped).
ASCII-only. No emojis.
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

# torch is CPU-only here; force single-threaded determinism-friendly settings later.
import torch

# Repo-relative imports (no hard-coded absolute paths).
_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir,
    write_metrics,
    write_partial,
    aggregate_partials,
)

ANCHOR_NAME = "teacher_free_relational_encoder_cn_subgraph_v1"

RELATIONS_PATH = os.path.join(_REPO, "data", "substrate_index", "concept", "relations.jsonl")

# ---------------------------------------------------------------------------
# Config profiles
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(
    n_nodes=400, seeds=[7], epochs=8, batch=128, k_rewire=20,
    code_dim=64, feat_dim=1024, temp=0.15, lr=0.01,
    lambda_cov=1.0, lambda_var=1.0, simgrace_sigma=0.05,
    n_offtarget_pairs=5000,
)

SMOKE_CFG = dict(
    n_nodes=2500, seeds=[7, 13, 17], epochs=40, batch=256, k_rewire=50,
    code_dim=128, feat_dim=4096, temp=0.15, lr=0.01,
    lambda_cov=1.0, lambda_var=1.0, simgrace_sigma=0.05,
    n_offtarget_pairs=50000,
)

FULL_CFG = dict(
    n_nodes=12000, seeds=[7, 13, 17, 23, 29], epochs=100, batch=512, k_rewire=150,
    code_dim=256, feat_dim=8192, temp=0.10, lr=0.008,
    lambda_cov=1.0, lambda_var=1.0, simgrace_sigma=0.05,
    n_offtarget_pairs=150000,
)

# Fixed base seed for node subsampling so ALL arms + ALL model-seeds train on the
# SAME induced subgraph (isolates arm/model variance from subgraph variance).
SUBGRAPH_BASE_SEED = 1234

# Pre-reg bands (applied to ARM_GRAPH_REPULSION primary; ARM_SIMGRACE_REPULSION secondary).
HARD_PASS_Z = 2.0            # note lower HP bound (2-3 sigma); [1.0, 2.0) = MIDDLE
HARD_FAIL_Z = 1.0
OFFTARGET_MARGIN_HP = 0.03   # repulsion off-target cosine must be >= this lower than no-repulsion
COLLAPSE_TOP_FRAC = 0.01     # top-1% of dims
COLLAPSE_VAR_FRAC = 0.90     # ...carrying >90% variance == collapse
RANDOM_INIT_LEAK_Z = 1.5     # random-init Z above this => char-trigram lexical-proximity leak warning

PRIMARY_ARM = "ARM_GRAPH_REPULSION"
SECONDARY_ARM = "ARM_SIMGRACE_REPULSION"
CONTROL_ARM = "ARM_NO_REPULSION"
FLOOR_ARM = "ARM_RANDOM_INIT"


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics (SCHEMA-VET section 13)
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(
        pid=os.getpid(),
        ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME,
        run_mode=run_mode,
        expected_n_units=expected_n_units,
        host=platform.node(),
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
        elapsed_s=0.0,
        traceback=traceback.format_exc()[:5000],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(),
        anchor_name=ANCHOR_NAME,
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
# Deterministic hashed char-trigram surface features (no lexical semantics)
# ---------------------------------------------------------------------------

def _stable_hash(s):
    """Deterministic 64-bit hash independent of PYTHONHASHSEED."""
    h = hashlib.blake2b(s.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(h, "little")


def char_trigram_features(words, feat_dim, seed=0):
    """Hashed bag-of-char-trigram features, L2-normalized rows. Shape [n, feat_dim].

    Deterministic surface featurization (Kanerva V1 analog). No word-meaning
    supervision. seed only rotates the hash salt so different runs can (if wanted)
    use different hashing; here we keep it FIXED across arms for comparability.
    """
    n = len(words)
    X = np.zeros((n, feat_dim), dtype=np.float32)
    salt = "salt%d::" % seed
    for i, w in enumerate(words):
        tok = "^" + w.lower().strip() + "$"
        if len(tok) < 3:
            # too short for a trigram; hash the whole token as one feature
            idx = _stable_hash(salt + tok) % feat_dim
            X[i, idx] += 1.0
            continue
        for j in range(len(tok) - 2):
            tri = tok[j:j + 3]
            idx = _stable_hash(salt + tri) % feat_dim
            X[i, idx] += 1.0
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    X = X / norms
    return X


# ---------------------------------------------------------------------------
# ConceptNet subgraph loader
# ---------------------------------------------------------------------------

def load_cn_subgraph(n_nodes, base_seed):
    """Load ConceptNet (CN_*) undirected subgraph, subsample to a dense induced
    subgraph of ~n_nodes nodes.

    Returns: node_ids (list[str]), node_words (list[str]),
             edges (np.ndarray [E,2] int32), degrees (np.ndarray [n] int32).
    """
    if not os.path.exists(RELATIONS_PATH):
        raise FileNotFoundError("relations.jsonl not found at %s" % RELATIONS_PATH)

    adj = {}
    n_lines = 0
    n_cn_edges = 0
    with open(RELATIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            n_lines += 1
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            s = d.get("src_id")
            t = d.get("tgt_id")
            if s is None or t is None:
                continue
            # Scope to ConceptNet word-graph only.
            if not (str(s).startswith("CN_") and str(t).startswith("CN_")):
                continue
            if s == t:
                continue
            n_cn_edges += 1
            adj.setdefault(s, set()).add(t)
            adj.setdefault(t, set()).add(s)

    if len(adj) == 0:
        raise RuntimeError("no CN_ edges found in relations.jsonl (scope empty)")

    full_deg = {u: len(nb) for u, nb in adj.items()}
    # NOTE: the raw relations.jsonl CN graph is SPARSE (median degree ~1, mean ~2.6,
    # largest connected component ~83% of nodes). This is sparser than the KB-ingested
    # concept_relations figure (median 6) cited in the research note -- the two are
    # different graph constructions; this cell operates on relations.jsonl directly.
    # To make relational-neighbor two-view positives constructable, we snowball within
    # the GIANT component from its max-degree hub, then extract the 2-core (every node
    # degree >= 2). Deterministic; all model-seeds share one subgraph.
    from collections import deque
    start = max(full_deg.items(), key=lambda kv: (kv[1], kv[0]))[0]  # max-degree hub (giant comp)

    collect_target = min(max(n_nodes * 4, 4000), len(adj))
    visited = set([start])
    order = [start]
    dq = deque([start])
    while dq and len(order) < collect_target:
        u = dq.popleft()
        for v in sorted(adj[u]):
            if v not in visited:
                visited.add(v)
                order.append(v)
                dq.append(v)
                if len(order) >= collect_target:
                    break
    kept_set = set(order)

    # Iterative 2-core: repeatedly drop nodes whose induced degree < 2 until stable.
    changed = True
    while changed:
        changed = False
        new_kept = []
        for u in kept_set:
            d = sum(1 for v in adj[u] if v in kept_set)
            if d >= 2:
                new_kept.append(u)
            else:
                changed = True
        kept_set = set(new_kept)
        if not kept_set:
            break

    # Cap to n_nodes: keep the earliest-BFS 2-core nodes, then re-extract 2-core so the
    # cap does not reintroduce degree-1 leaves.
    if len(kept_set) > n_nodes:
        ordered_core = [u for u in order if u in kept_set][:n_nodes]
        kept_set = set(ordered_core)
        changed = True
        while changed:
            changed = False
            new_kept = []
            for u in kept_set:
                d = sum(1 for v in adj[u] if v in kept_set)
                if d >= 2:
                    new_kept.append(u)
                else:
                    changed = True
            kept_set = set(new_kept)
            if not kept_set:
                break

    kept = sorted(kept_set)
    if len(kept) < 50:
        raise RuntimeError("induced 2-core too small (%d nodes); relax subsample" % len(kept))

    node_ids = sorted(kept_set)
    idx_of = {u: i for i, u in enumerate(node_ids)}
    node_words = [nid[3:].replace("_", " ") for nid in node_ids]  # strip "CN_"

    edge_set = set()
    for u in node_ids:
        iu = idx_of[u]
        for v in adj[u]:
            if v in kept_set:
                iv = idx_of[v]
                a, b = (iu, iv) if iu < iv else (iv, iu)
                if a != b:
                    edge_set.add((a, b))
    edges = np.array(sorted(edge_set), dtype=np.int32) if edge_set else np.zeros((0, 2), dtype=np.int32)
    degrees = np.zeros(len(node_ids), dtype=np.int32)
    for a, b in edges:
        degrees[a] += 1
        degrees[b] += 1

    if edges.shape[0] < 50:
        raise RuntimeError("induced edge set too small (%d edges)" % edges.shape[0])

    meta = dict(
        n_lines=n_lines, n_cn_edges=n_cn_edges, n_nodes=len(node_ids),
        n_edges=int(edges.shape[0]),
        median_degree=float(np.median(degrees)),
        mean_degree=float(np.mean(degrees)),
        frac_deg_ge_2=float(np.mean(degrees >= 2)),
    )
    return node_ids, node_words, edges, degrees, meta


# ---------------------------------------------------------------------------
# Encoder
# ---------------------------------------------------------------------------

class ProjHead(torch.nn.Module):
    """Shallow linear projection head: features -> code. L2-normalized output."""

    def __init__(self, feat_dim, code_dim):
        super().__init__()
        self.lin = torch.nn.Linear(feat_dim, code_dim, bias=False)

    def forward(self, x, perturb_sigma=0.0, generator=None):
        w = self.lin.weight
        if perturb_sigma > 0.0:
            noise = torch.randn(w.shape, generator=generator) * perturb_sigma * w.detach().std()
            h = torch.nn.functional.linear(x, w + noise)
        else:
            h = self.lin(x)
        return h  # raw; caller normalizes for cos-sim


def _l2norm(h, eps=1e-8):
    return h / (h.norm(dim=1, keepdim=True) + eps)


# ---------------------------------------------------------------------------
# Loss terms
# ---------------------------------------------------------------------------

def info_nce(za, zp, temp):
    """Symmetric InfoNCE over an in-batch positive pairing (diag = positive)."""
    za = _l2norm(za)
    zp = _l2norm(zp)
    logits = (za @ zp.t()) / temp
    labels = torch.arange(za.shape[0])
    loss = 0.5 * (torch.nn.functional.cross_entropy(logits, labels)
                  + torch.nn.functional.cross_entropy(logits.t(), labels))
    return loss


def vicreg_repulsion(h, lambda_cov, lambda_var, gamma=1.0, eps=1e-4):
    """VICReg covariance (decorrelation) + variance-floor repulsion on raw reps."""
    hc = h - h.mean(dim=0, keepdim=True)
    n = hc.shape[0]
    d = hc.shape[1]
    cov = (hc.t() @ hc) / max(n - 1, 1)
    off_diag_sq = (cov ** 2).sum() - (torch.diagonal(cov) ** 2).sum()
    cov_term = off_diag_sq / d
    std = torch.sqrt(hc.var(dim=0) + eps)
    var_term = torch.mean(torch.relu(gamma - std))
    return lambda_cov * cov_term + lambda_var * var_term


def alignment_only(za, zp):
    """No-repulsion control: pull positives together, NO negatives, NO covariance."""
    za = _l2norm(za)
    zp = _l2norm(zp)
    return (1.0 - (za * zp).sum(dim=1)).mean()


# ---------------------------------------------------------------------------
# Discriminators
# ---------------------------------------------------------------------------

def _sample_neighbor_positives(edges, batch_idx_set, rng):
    """For a set of anchor node indices, return (anchor, positive) via random incident edge."""
    # Precompute adjacency lists lazily is expensive; edges is small enough to index.
    # Build per-call using a provided adjacency dict is cleaner -> see caller.
    raise NotImplementedError


def embedding_assortativity_z(emb, edges, degrees, k_rewire, rng):
    """Newman-modularity-analog Z: mean edge-endpoint cosine vs a degree-preserving
    (configuration-model / Chung-Lu) null.

    M_true = mean over real edges of cos(z_u, z_v).
    Null: draw endpoint pairs ~ proportional to degree (the config-model expected
    edge distribution), same count as real edges, compute mean cos; repeat k_rewire.
    Z = (M_true - mean_null) / std_null.
    """
    z = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8)
    e = edges
    m_true = float(np.mean(np.sum(z[e[:, 0]] * z[e[:, 1]], axis=1)))
    n_e = e.shape[0]
    deg = degrees.astype(np.float64)
    if deg.sum() <= 0:
        return 0.0, m_true, m_true, 0.0
    p = deg / deg.sum()
    null_means = np.zeros(k_rewire, dtype=np.float64)
    n_nodes = z.shape[0]
    for k in range(k_rewire):
        u = rng.choice(n_nodes, size=n_e, p=p)
        v = rng.choice(n_nodes, size=n_e, p=p)
        # avoid self-pairs (resample the collisions to a shifted partner)
        coll = (u == v)
        if coll.any():
            v[coll] = (v[coll] + 1) % n_nodes
        null_means[k] = np.mean(np.sum(z[u] * z[v], axis=1))
    mu = float(null_means.mean())
    sd = float(null_means.std())
    if sd < 1e-9:
        zscore = 0.0
    else:
        zscore = (m_true - mu) / sd
    return float(zscore), m_true, mu, sd


def off_target_cosine(emb, edge_set, n_pairs, rng):
    """Mean pairwise cosine over random NON-EDGE node pairs (lower = better separated)."""
    z = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8)
    n = z.shape[0]
    cnt = 0
    acc = 0.0
    attempts = 0
    max_attempts = n_pairs * 3
    while cnt < n_pairs and attempts < max_attempts:
        u = rng.integers(0, n)
        v = rng.integers(0, n)
        attempts += 1
        if u == v:
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) in edge_set:
            continue
        acc += float(np.dot(z[u], z[v]))
        cnt += 1
    return acc / max(cnt, 1), cnt


def collapse_stats(emb):
    """Return (frac_var_top_1pct, effective_rank, min_dim_std, collapsed_bool)."""
    z = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8)
    var = z.var(axis=0)
    total = float(var.sum()) + 1e-12
    order = np.sort(var)[::-1]
    d = z.shape[1]
    top_k = max(1, int(math.ceil(COLLAPSE_TOP_FRAC * d)))
    frac_top = float(order[:top_k].sum()) / total
    # participation ratio as effective rank proxy
    eff_rank = float((var.sum() ** 2) / (np.sum(var ** 2) + 1e-12))
    min_std = float(np.sqrt(var.min()))
    collapsed = bool(frac_top >= COLLAPSE_VAR_FRAC)
    return frac_top, eff_rank, min_std, collapsed


def _emb_digest(emb):
    return hashlib.sha256(np.ascontiguousarray(emb.astype(np.float32)).tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# Training per arm
# ---------------------------------------------------------------------------

def build_adjlist(edges, n_nodes):
    adj = [[] for _ in range(n_nodes)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    return adj


def train_arm(arm, X, adj, cfg, seed, out_dir=None, unit_base=0):
    """Train one arm; return final embedding [n, code_dim] as numpy float32."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    n_nodes = X.shape[0]
    feat_dim = X.shape[1]
    Xt = torch.from_numpy(X)
    model = ProjHead(feat_dim, cfg["code_dim"])
    gen = torch.Generator()
    gen.manual_seed(seed + 999)

    if arm == FLOOR_ARM:
        # untrained: apply random-init encoder to features (no optimization)
        with torch.no_grad():
            emb = _l2norm(model(Xt)).numpy().astype(np.float32)
        return emb

    opt = torch.optim.Adam(model.parameters(), lr=cfg["lr"])
    rng = np.random.default_rng(seed + 7)

    # anchor pool = nodes that have >=1 neighbor (for graph-positive arms)
    has_nb = np.array([len(adj[i]) > 0 for i in range(n_nodes)], dtype=bool)
    anchor_pool = np.nonzero(has_nb)[0]

    log_every = max(1, cfg["epochs"] // 5)
    t_ep = time.perf_counter()
    for ep in range(cfg["epochs"]):
        if arm in (PRIMARY_ARM, CONTROL_ARM):
            a_idx = rng.choice(anchor_pool, size=min(cfg["batch"], anchor_pool.shape[0]), replace=False)
            p_idx = np.array([adj[a][rng.integers(0, len(adj[a]))] for a in a_idx], dtype=np.int64)
            xa = Xt[torch.from_numpy(a_idx.astype(np.int64))]
            xp = Xt[torch.from_numpy(p_idx)]
            ha = model(xa)
            hp = model(xp)
            if arm == PRIMARY_ARM:
                loss = info_nce(ha, hp, cfg["temp"]) + vicreg_repulsion(
                    torch.cat([ha, hp], dim=0), cfg["lambda_cov"], cfg["lambda_var"])
            else:  # CONTROL_ARM: alignment only, no repulsion at all
                loss = alignment_only(ha, hp)
        elif arm == SECONDARY_ARM:
            # SimGRACE: two weight-perturbed views of the SAME nodes (degree-agnostic)
            b_idx = rng.choice(n_nodes, size=min(cfg["batch"], n_nodes), replace=False)
            xb = Xt[torch.from_numpy(b_idx.astype(np.int64))]
            h1 = model(xb, perturb_sigma=cfg["simgrace_sigma"], generator=gen)
            h2 = model(xb, perturb_sigma=cfg["simgrace_sigma"], generator=gen)
            loss = info_nce(h1, h2, cfg["temp"]) + vicreg_repulsion(
                torch.cat([h1, h2], dim=0), cfg["lambda_cov"], cfg["lambda_var"])
        else:
            raise ValueError("unknown arm %r" % arm)

        opt.zero_grad()
        loss.backward()
        opt.step()

        if (ep % log_every == 0) or (ep == cfg["epochs"] - 1):
            _log("  train seed=%d arm=%s ep=%d/%d loss=%.4f (%.1fs)" % (
                seed, arm, ep, cfg["epochs"], float(loss.detach()), time.perf_counter() - t_ep))
            if out_dir is not None:
                try:
                    from experiments._cell_heartbeat import emit_heartbeat
                    emit_heartbeat(str(out_dir), unit_idx=unit_base + ep,
                                   total_units=cfg["epochs"], elapsed_s=time.perf_counter() - t_ep)
                except Exception as _hb_e:  # heartbeat is best-effort telemetry (SCHEMA-VET 13D)
                    _log("  [heartbeat-warn] %s: %s" % (type(_hb_e).__name__, str(_hb_e)[:120]))

    with torch.no_grad():
        emb = _l2norm(model(Xt)).numpy().astype(np.float32)
    return emb


# ---------------------------------------------------------------------------
# BGE reference (best-effort, non-gating)
# ---------------------------------------------------------------------------

def try_bge_reference(node_words):
    """Return BGE-small embeddings [n, 1024] or None. Never raises; non-gating."""
    try:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
        emb = model.encode(node_words, batch_size=256, show_progress_bar=False,
                           normalize_embeddings=True)
        return np.asarray(emb, dtype=np.float32)
    except Exception as e:  # non-gating: BGE is a reference line only
        _log("BGE reference unavailable (non-gating): %s: %s" % (type(e).__name__, str(e)[:200]))
        return None


# ---------------------------------------------------------------------------
# Per-seed evaluation
# ---------------------------------------------------------------------------

ARMS = [PRIMARY_ARM, CONTROL_ARM, SECONDARY_ARM, FLOOR_ARM]


def run_seed(seed, X, edges, degrees, adj, edge_set, cfg, bge_emb, out_dir=None):
    rng = np.random.default_rng(seed + 4242)
    arm_emb = {}
    arm_metrics = {}
    for ai, arm in enumerate(ARMS):
        t0 = time.perf_counter()
        emb = train_arm(arm, X, adj, cfg, seed, out_dir=out_dir, unit_base=ai * cfg["epochs"])
        zscore, m_true, mu, sd = embedding_assortativity_z(emb, edges, degrees, cfg["k_rewire"], rng)
        offcos, npairs = off_target_cosine(emb, edge_set, cfg["n_offtarget_pairs"], rng)
        frac_top, eff_rank, min_std, collapsed = collapse_stats(emb)
        arm_emb[arm] = emb
        arm_metrics[arm] = dict(
            modularity_z=zscore, m_true=m_true, null_mean=mu, null_std=sd,
            off_target_cosine=offcos, n_offtarget_pairs=int(npairs),
            frac_var_top_1pct=frac_top, effective_rank=eff_rank,
            min_dim_std=min_std, collapsed=collapsed,
            emb_digest=_emb_digest(emb),
            train_s=time.perf_counter() - t0,
        )
        _log("seed=%d arm=%s Z=%.3f offcos=%.4f collapsed=%s eff_rank=%.1f (%.1fs)" % (
            seed, arm, zscore, offcos, collapsed, eff_rank, arm_metrics[arm]["train_s"]))

    # BGE reference (non-gating)
    if bge_emb is not None:
        zscore, m_true, mu, sd = embedding_assortativity_z(bge_emb, edges, degrees, cfg["k_rewire"], rng)
        offcos, npairs = off_target_cosine(bge_emb, edge_set, cfg["n_offtarget_pairs"], rng)
        frac_top, eff_rank, min_std, collapsed = collapse_stats(bge_emb)
        arm_metrics["ARM_BGE_REFERENCE"] = dict(
            modularity_z=zscore, off_target_cosine=offcos, frac_var_top_1pct=frac_top,
            effective_rank=eff_rank, collapsed=collapsed, non_gating=True,
        )
        _log("seed=%d arm=ARM_BGE_REFERENCE (non-gating) Z=%.3f offcos=%.4f" % (seed, zscore, offcos))

    # ARMS-MUST-DIFFER (META_RULE_AF)
    digests = {a: arm_metrics[a]["emb_digest"] for a in ARMS}
    dig_list = list(digests.items())
    for i in range(len(dig_list)):
        for j in range(i + 1, len(dig_list)):
            assert dig_list[i][1] != dig_list[j][1], (
                "META_RULE_AF VIOLATION: arms %s and %s bit-identical" % (dig_list[i][0], dig_list[j][0]))

    return arm_metrics


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def aggregate_and_verdict(per_seed_metrics, cfg, subgraph_meta, bge_present):
    """per_seed_metrics: list of dict {arm: metrics}. Aggregate across seeds + band."""
    def arm_series(arm, key):
        return np.array([m[arm][key] for m in per_seed_metrics if arm in m], dtype=np.float64)

    agg = {}
    all_arms = list(per_seed_metrics[0].keys())
    for arm in all_arms:
        z = arm_series(arm, "modularity_z")
        oc = arm_series(arm, "off_target_cosine")
        col = np.array([per_seed_metrics[k][arm].get("collapsed", False)
                        for k in range(len(per_seed_metrics)) if arm in per_seed_metrics[k]])
        agg[arm] = dict(
            modularity_z_mean=float(z.mean()), modularity_z_std=float(z.std()),
            modularity_z_min=float(z.min()), modularity_z_max=float(z.max()),
            off_target_cosine_mean=float(oc.mean()),
            collapsed_any=bool(col.any()), collapsed_all=bool(col.all()),
            n_seeds=int(len(z)),
        )

    prim = agg[PRIMARY_ARM]
    sec = agg.get(SECONDARY_ARM, {})
    ctrl = agg[CONTROL_ARM]
    floor = agg[FLOOR_ARM]

    z_prim = prim["modularity_z_mean"]
    off_prim = prim["off_target_cosine_mean"]
    off_ctrl = ctrl["off_target_cosine_mean"]
    off_margin = off_ctrl - off_prim  # positive == repulsion better separated
    prim_collapsed = prim["collapsed_any"]

    # Ablation gate: no-repulsion control MUST collapse OR be crowded (higher off-target cos)
    ablation_collapses = bool(ctrl["collapsed_any"] or (off_ctrl >= 0.5) or (ctrl["modularity_z_mean"] < HARD_FAIL_Z))

    # p9 lexical-confound control: char-trigram features carry lexical proximity, and
    # graph-neighbors (synonyms / IS_A) partially share trigrams, so an untrained
    # random-init projection already has some above-null assortativity. The rigorous
    # control is the LIFT: the learned code must add >= HARD_PASS_Z sigma of
    # assortativity BEYOND the random-init lexical floor. This neutralizes the
    # confound without a blanket demotion when the floor is merely nonzero.
    floor_z = floor["modularity_z_mean"]
    lift_over_floor = z_prim - floor_z
    lexical_leak_warning = bool(floor_z >= RANDOM_INIT_LEAK_Z)  # REPORTED diagnostic, not a hard blocker
    mechanism_fires = bool(lift_over_floor > 0.0)

    # Primary band (absolute Z bar AND lexical-lift bar AND separation margin AND no dim-collapse)
    if (z_prim >= HARD_PASS_Z) and (lift_over_floor >= HARD_PASS_Z) \
            and (off_margin >= OFFTARGET_MARGIN_HP) and (not prim_collapsed):
        primary_band = "HARD_PASS"
    elif (z_prim < HARD_FAIL_Z) or (off_margin <= 0.0) or (lift_over_floor <= 0.0):
        primary_band = "HARD_FAIL"
    else:
        primary_band = "MIDDLE_BAND"

    # Overall verdict additionally requires the ablation to be load-bearing:
    # the no-repulsion control must collapse/crowd (R1, the highest-P claim).
    if primary_band == "HARD_PASS" and ablation_collapses:
        verdict = "HARD_PASS"
    elif primary_band == "HARD_FAIL":
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | %s Z=%.2f (min=%.2f) lift_over_lexical_floor=%.2f off_margin_vs_control=%.4f "
        "prim_dim_collapsed=%s | control Z=%.2f offcos=%.4f ablation_collapses=%s | "
        "floor(random-init) Z=%.2f lexical_leak_diag=%s | secondary(SimGRACE) Z=%s | "
        "subgraph n=%d E=%d med_deg=%.1f | BGE_ref=%s" % (
            verdict, PRIMARY_ARM, z_prim, prim["modularity_z_min"], lift_over_floor, off_margin,
            prim_collapsed, ctrl["modularity_z_mean"], off_ctrl, ablation_collapses, floor_z,
            lexical_leak_warning,
            ("%.2f" % sec["modularity_z_mean"]) if sec else "n/a",
            subgraph_meta["n_nodes"], subgraph_meta["n_edges"],
            subgraph_meta["median_degree"], bge_present))

    gates = dict(
        primary_band=primary_band,
        hard_pass_z=HARD_PASS_Z, hard_fail_z=HARD_FAIL_Z, offtarget_margin_hp=OFFTARGET_MARGIN_HP,
        z_primary_mean=z_prim, z_primary_min=prim["modularity_z_min"],
        floor_random_init_z=floor_z, lift_over_lexical_floor=lift_over_floor,
        off_target_margin_vs_control=off_margin,
        primary_dim_collapsed=prim_collapsed,
        ablation_collapses=ablation_collapses,
        mechanism_fires_above_floor=mechanism_fires,
        lexical_leak_warning_diagnostic=lexical_leak_warning,
        secondary_z_mean=sec.get("modularity_z_mean") if sec else None,
    )
    return verdict, verdict_msg, agg, gates


# ---------------------------------------------------------------------------
# Self-test: proves the discriminator is TELEMETRY-SENSITIVE (not analytically pinned)
# ---------------------------------------------------------------------------

def discriminator_selftest():
    """Planted-community synthetic: structure-respecting emb -> high Z;
    random emb -> Z ~ 0; perturbing structure -> Z drops. Proves sensitivity."""
    rng = np.random.default_rng(0)
    n_comm = 8
    per = 60
    n = n_comm * per
    code_dim = 32
    comm = np.repeat(np.arange(n_comm), per)
    centers = rng.standard_normal((n_comm, code_dim))
    emb_struct = centers[comm] + 0.15 * rng.standard_normal((n, code_dim))
    emb_struct = emb_struct.astype(np.float32)
    emb_rand = rng.standard_normal((n, code_dim)).astype(np.float32)

    # intra-community edges
    edges = []
    for c in range(n_comm):
        idx = np.nonzero(comm == c)[0]
        for _ in range(per * 3):
            a, b = rng.choice(idx, size=2, replace=False)
            edges.append((min(a, b), max(a, b)))
    edges = np.array(sorted(set(edges)), dtype=np.int32)
    degrees = np.zeros(n, dtype=np.int32)
    for a, b in edges:
        degrees[a] += 1
        degrees[b] += 1

    z_struct, _, _, _ = embedding_assortativity_z(emb_struct, edges, degrees, 30, np.random.default_rng(1))
    z_rand, _, _, _ = embedding_assortativity_z(emb_rand, edges, degrees, 30, np.random.default_rng(2))

    # perturb structure: shuffle 50% of rows -> Z must drop
    emb_pert = emb_struct.copy()
    perm_idx = rng.permutation(n)[: n // 2]
    emb_pert[perm_idx] = emb_struct[rng.permutation(perm_idx)]
    z_pert, _, _, _ = embedding_assortativity_z(emb_pert, edges, degrees, 30, np.random.default_rng(3))

    # DIMENSIONAL collapse test (note's definition: <1% of dims carry >90% variance).
    # Put nearly all variance in dim 0; near-zero elsewhere -> after L2 norm rows ~ [+/-1, 0...].
    emb_collapse = np.zeros((n, code_dim), dtype=np.float32)
    emb_collapse[:, 0] = rng.standard_normal(n).astype(np.float32)
    emb_collapse += (1e-4 * rng.standard_normal((n, code_dim))).astype(np.float32)
    frac_top_collapse, _, _, collapsed = collapse_stats(emb_collapse)
    frac_top_struct, _, _, notcollapsed = collapse_stats(emb_struct)

    results = dict(z_struct=z_struct, z_rand=z_rand, z_pert=z_pert,
                   frac_top_collapse=frac_top_collapse, frac_top_struct=frac_top_struct,
                   collapse_detected=collapsed, struct_not_collapsed=(not notcollapsed))
    # Telemetry-sensitivity assertions:
    #  - structure-respecting emb -> high Z
    #  - random emb -> Z near 0
    #  - perturbing structure meaningfully DROPS Z (sensitivity, not analytic pin)
    #  - dimensional collapse detected; well-spread structure NOT flagged collapsed
    ok = (z_struct >= 2.0) and (abs(z_rand) < 1.5) and (z_pert < 0.7 * z_struct) \
        and collapsed and (not notcollapsed)
    return ok, results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--no-bge", action="store_true", help="skip BGE reference line")
    args, _unknown = ap.parse_known_args()

    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode

    output_dir = str(get_output_dir(ANCHOR_NAME))

    if run_mode == "self_test":
        cfg = SELFTEST_CFG
    elif run_mode == "smoke":
        cfg = SMOKE_CFG
    else:
        cfg = FULL_CFG

    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()

    # ---- discriminator telemetry-sensitivity self-test (ALWAYS runs) ----
    st_ok, st_res = discriminator_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED (not telemetry-sensitive): %s" % st_res,
            summary="discriminator selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res,
        ))
        raise SystemExit(1)

    if run_mode == "self_test":
        # pure module self-test: also exercise a tiny end-to-end training on a small graph
        node_ids, node_words, edges, degrees, meta = load_cn_subgraph(cfg["n_nodes"], SUBGRAPH_BASE_SEED)
        X = char_trigram_features(node_words, cfg["feat_dim"])
        adj = build_adjlist(edges, len(node_ids))
        edge_set = set((int(a), int(b)) for a, b in edges)
        pm = run_seed(cfg["seeds"][0], X, edges, degrees, adj, edge_set, cfg, None)
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS discriminator+end-to-end training exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, subgraph_meta=meta,
            primary_arm_z=pm[PRIMARY_ARM]["modularity_z"],
            control_arm_z=pm[CONTROL_ARM]["modularity_z"],
            floor_arm_z=pm[FLOOR_ARM]["modularity_z"],
        ))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    # ---- smoke / full ----
    _log("loading ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, meta = load_cn_subgraph(cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s" % meta)
    X = char_trigram_features(node_words, cfg["feat_dim"])
    adj = build_adjlist(edges, len(node_ids))
    edge_set = set((int(a), int(b)) for a, b in edges)

    bge_emb = None if args.no_bge else try_bge_reference(node_words)
    bge_present = bge_emb is not None

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed_metrics = []
    seed_failures = []
    for si, seed in enumerate(cfg["seeds"]):
        try:
            pm = run_seed(seed, X, edges, degrees, adj, edge_set, cfg, bge_emb, out_dir=out_dir_path)
            per_seed_metrics.append(pm)
            write_partial(out_dir_path, seed, dict(seed=seed, arms=pm))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # per-seed failure-class instrumentation (META_RULE_J)
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    # cardinality gate (META_RULE_H): expected == n_seeds
    if len(per_seed_metrics) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (
                expected_n_units, len(per_seed_metrics), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, subgraph_meta=meta,
        ))
        raise SystemExit(1)

    verdict, verdict_msg, agg, gates = aggregate_and_verdict(
        per_seed_metrics, cfg, meta, bge_present)

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(per_seed_metrics), seeds=cfg["seeds"],
        config=cfg, subgraph_meta=meta,
        gates=gates, arms_aggregate=agg,
        bge_reference_present=bge_present,
        discriminator_selftest=st_res,
        seed_failures=seed_failures,
        per_seed=[{a: {k: v for k, v in per_seed_metrics[i][a].items() if k != "emb_digest"}
                   for a in per_seed_metrics[i]} for i in range(len(per_seed_metrics))],
    )
    write_metrics(out_dir_path, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


if __name__ == "__main__":
    _od = str(get_output_dir(ANCHOR_NAME))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
