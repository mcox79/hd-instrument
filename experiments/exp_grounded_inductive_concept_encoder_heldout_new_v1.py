"""Teacher-free GROUNDED INDUCTIVE concept encoder, judged ONLY on held-out-NEW-concept generalization.

THE QUESTION (layer-1 learned meaning earned from the layer-2 foundation):
  Can a concept's EXPERIENTIAL GROUNDING (Lancaster sensorimotor + concreteness + VAD + AoA),
  passed through an encoder trained with a TEACHER-FREE relational self-teacher on KNOWN concepts,
  place an UNSEEN concept near its true relational neighbours in cskg_foundation_v1?

HARD INVARIANTS (project locks):
  - TEACHER-FREE: NO GloVe/BGE/transformer/borrowed vector anywhere (not teacher, target, init, or feature).
    The only input features are the measured grounding norms; the relational signal is the KB's own graph.
  - INDUCTIVE (not transductive): the encoder is a FUNCTION f(grounding_features) -> code. A held-out NEW
    concept (never seen in training, ALL its incident edges removed from training) gets its code from its
    grounding features ALONE. A per-concept learned lookup table is a CONTROL that MUST collapse.

DESIGN (why this is a fair, leak-proof, can-fail test):
  * Universe = grounded concepts (have a grounding dict) with induced-degree >= MIN_DEG in the
    grounded-induced subgraph of cskg_foundation_v1.
  * Concept-level held-out split (leak-proof): each concept deterministically (sha256) -> TRAIN or HELDOUT.
    Training graph = edges with BOTH endpoints TRAIN. EVERY edge incident to a held-out concept is removed
    from training. Held-out concept's edges to TRAIN concepts are used ONLY at test (eval target, never seen
    by the encoder). Held-out<->held-out edges are discarded entirely.
  * Grounding standardized using TRAIN statistics ONLY (no held-out leakage); missing groups -> 0 + mask bit.
  * Encoder = small MLP (grounding_feat -> hidden -> code), L2-normalized code. Trained TEACHER-FREE with:
      InfoNCE over relational-neighbour positives (in-batch negatives = repulsion) against an EMA self-teacher
      (BYOL/DINO-style; the target encoder is an EMA of the online encoder -> no external teacher)
      + VICReg variance/covariance repulsion (anti-collapse).
  * METRIC (held-out-NEW-concept generalization): for each held-out concept h, rank ALL TRAIN concepts by
    cosine to enc(h). AUC = P(true-neighbour ranks above a non-neighbour). base/chance AUC = 0.5.
    Also recall@10, MRR, neighbour-cosine margin.

ARMS:
  ARM_GROUNDING_ENCODER : the inductive learned encoder.                         [PRIMARY]
  ARM_RAW_GROUNDING     : NO encoder; rank by raw standardized-grounding cosine.  [must-BEAT reference]
  ARM_RANDOM_INIT       : untrained encoder (random MLP) on same grounding.       [training-added-value ref]
  ARM_FEATURE_SHUFFLE   : encoder trained on grounding SHUFFLED across concept ids.[COLLAPSE control -> 0.5]
  ARM_LOOKUP_RECALL     : transductive per-concept embedding table; held-out has   [COLLAPSE control -> 0.5]
                          NO row -> mean-train code (store-then-recall floor).

  NOTE on can-fail gating (F.4 discipline: do NOT gate on a structurally-non-floor control):
  a random projection of grounding partially preserves grounding-cosine, so ARM_RANDOM_INIT is NOT expected to
  collapse to 0.5 -- it is a REFERENCE, not a collapse gate. The TRUE collapse controls that MUST land at ~0.5
  are ARM_FEATURE_SHUFFLE (grounding<->concept correspondence destroyed) and ARM_LOOKUP_RECALL (no entry for a
  new concept). The can-fail gate is on THOSE two.

CPU-only. No GPU. No network. ASCII-only. No emojis.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator has base=0.5 exactly (random codes); collapse controls calibrate the floor
# - baseline_in_band at smoke: collapse controls (shuffle,lookup) must sit in [0.44,0.56]; else LEAK/BROKEN
# - discriminator survives scale: smoke IS a genuine held-out-new-concept test at few-thousand grounded concepts
# - HARD_PASS strictly above floor: enc_auc>=0.60 AND enc-max(collapse)>=0.07 AND enc-raw_grounding>=0.02
# - HP_SCOPE: gates apply to ARM_GROUNDING_ENCODER (primary) only
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 is analytic; collapse controls witness it)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg
# - deterministic seeding: sha256 concept split + fixed int seeds + sorted(); no hash()/list(set()) (PROT-023)
# - no substrate KGStore/fit objects (self-contained jsonl reader) -> F.1/F.2 real_code_path N/A
"""

import argparse
import glob
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

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir,
    write_metrics,
    write_partial,
)

ANCHOR_NAME = "grounded_inductive_concept_encoder_heldout_new_v1"
FOUNDATION_DIR = os.path.join(_REPO, "data", "cskg_foundation_v1")
NODES_PATH = os.path.join(FOUNDATION_DIR, "nodes.jsonl")
EDGES_GLOB = os.path.join(FOUNDATION_DIR, "edges_shard_*.jsonl")

# Grounding feature layout (16 value dims + 4 group-present mask bits = 20).
LANCASTER_KEYS = ["aud", "gus", "hap", "int", "olf", "vis",
                  "foot", "hand", "head", "mouth", "torso"]
GROUPS = [
    ("lancaster", LANCASTER_KEYS),
    ("concreteness", ["conc"]),
    ("vad", ["valence", "arousal", "dominance"]),
    ("aoa", ["aoa"]),
]
N_VALUE_DIMS = sum(len(ks) for _, ks in GROUPS)   # 16
N_GROUPS = len(GROUPS)                            # 4
FEAT_DIM = N_VALUE_DIMS + N_GROUPS                # 20

# ---------------------------------------------------------------------------
# Config profiles
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    min_deg=2, cap_nodes=500, seeds=[7], epochs=12, batch=128,
    code_dim=32, hidden=64, lr=5e-3, temp=0.2, ema=0.9,
    lambda_var=1.0, lambda_cov=1.0, heldout_frac=0.2, min_test_neighbors=1,
)
SMOKE_CFG = dict(
    min_deg=3, cap_nodes=6000, seeds=[7, 13], epochs=80, batch=512,
    code_dim=128, hidden=256, lr=3e-3, temp=0.15, ema=0.99,
    lambda_var=1.0, lambda_cov=1.0, heldout_frac=0.2, min_test_neighbors=2,
)
FULL_CFG = dict(
    min_deg=3, cap_nodes=8700, seeds=[7, 13, 17], epochs=180, batch=1024,
    code_dim=256, hidden=512, lr=2e-3, temp=0.12, ema=0.995,
    lambda_var=1.0, lambda_cov=1.0, heldout_frac=0.2, min_test_neighbors=2,
)

# Deterministic split salt + node subsample seed (fixed; identical across arms + model-seeds).
SPLIT_SALT = "gicehn_v1_split::"
SUBSAMPLE_SEED = 1234

# Pre-reg bands (applied to ARM_GROUNDING_ENCODER primary held-out AUC).
HP_AUC = 0.60                 # HARD_PASS absolute AUC floor (strictly above chance 0.5)
HF_AUC = 0.55                 # below this = HARD_FAIL (essentially chance)
HP_MARGIN_OVER_COLLAPSE = 0.07  # enc must beat max(shuffle,lookup) by this
HP_MARGIN_OVER_RAW = 0.02       # enc must beat raw-grounding by this (learning adds value)
HP_MARGIN_OVER_POP = 0.02       # enc must beat the popularity prior by this (genuine bar)
COLLAPSE_BAND = (0.44, 0.56)  # collapse controls (shuffle, lookup-random) MUST sit here (can-fail fired)

PRIMARY_ARM = "ARM_GROUNDING_ENCODER"
RAW_ARM = "ARM_RAW_GROUNDING"
RANDOM_ARM = "ARM_RANDOM_INIT"
SHUFFLE_ARM = "ARM_FEATURE_SHUFFLE"
LOOKUP_ARM = "ARM_LOOKUP_RECALL"
POP_ARM = "ARM_POPULARITY"
# CODE_ARMS get a codes matrix + cosine eval; POP_ARM is scored directly by train-degree.
CODE_ARMS = [PRIMARY_ARM, RAW_ARM, RANDOM_ARM, SHUFFLE_ARM, LOOKUP_ARM]
ALL_ARMS = CODE_ARMS + [POP_ARM]


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
# Deterministic concept split (sha256; PYTHONHASHSEED-independent)
# ---------------------------------------------------------------------------
def _split_is_heldout(concept_id, heldout_frac):
    h = hashlib.sha256((SPLIT_SALT + concept_id).encode("utf-8")).digest()
    r = int.from_bytes(h[:8], "big") / float(2 ** 64)
    return r < heldout_frac


# ---------------------------------------------------------------------------
# Foundation loader: grounded induced subgraph + grounding feature matrix
# ---------------------------------------------------------------------------
def _grounding_vector(gd):
    """Return (values[16] float with NaN for missing, group_present[4] float 0/1)."""
    vals = np.full(N_VALUE_DIMS, np.nan, dtype=np.float64)
    gpres = np.zeros(N_GROUPS, dtype=np.float64)
    off = 0
    for gi, (gname, keys) in enumerate(GROUPS):
        sub = gd.get(gname)
        if isinstance(sub, dict) and len(sub) > 0:
            gpres[gi] = 1.0
            for k in keys:
                v = sub.get(k)
                if v is not None:
                    vals[off] = float(v)
        off += len(keys)
    return vals, gpres


def load_grounded_subgraph(cfg):
    """Load grounded concepts + induced subgraph. Returns dict of arrays."""
    if not os.path.exists(NODES_PATH):
        raise FileNotFoundError("nodes.jsonl not found at %s" % NODES_PATH)

    gid_list = []
    raw_vals = []
    raw_gpres = []
    full_degree = {}
    with open(NODES_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            gd = d.get("grounding")
            if not gd:
                continue
            cid = d["id"]
            vals, gpres = _grounding_vector(gd)
            gid_list.append(cid)
            raw_vals.append(vals)
            raw_gpres.append(gpres)
            full_degree[cid] = int(d.get("degree", 0))
    if len(gid_list) < 50:
        raise RuntimeError("too few grounded nodes (%d)" % len(gid_list))

    gid_set = set(gid_list)
    idx_of = {c: i for i, c in enumerate(gid_list)}

    # induced edges among grounded concepts (undirected, dedup)
    edge_set = set()
    for shard in sorted(glob.glob(EDGES_GLOB)):
        with open(shard, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                e = json.loads(line)
                s = e.get("subject")
                o = e.get("obj")
                if s is None or o is None or s == o:
                    continue
                if s in gid_set and o in gid_set:
                    a, b = (idx_of[s], idx_of[o])
                    if a > b:
                        a, b = b, a
                    edge_set.add((a, b))
    if len(edge_set) < 50:
        raise RuntimeError("too few induced edges among grounded (%d)" % len(edge_set))

    n_all = len(gid_list)
    induced_deg = np.zeros(n_all, dtype=np.int64)
    for a, b in edge_set:
        induced_deg[a] += 1
        induced_deg[b] += 1

    # keep concepts with induced-deg >= min_deg; cap to cap_nodes by highest induced degree
    keep_mask = induced_deg >= cfg["min_deg"]
    keep_idx = np.nonzero(keep_mask)[0]
    if keep_idx.shape[0] > cfg["cap_nodes"]:
        # deterministic: sort by (-induced_deg, id) then take top cap_nodes
        order = sorted(keep_idx.tolist(), key=lambda i: (-int(induced_deg[i]), gid_list[i]))
        keep_idx = np.array(sorted(order[:cfg["cap_nodes"]]), dtype=np.int64)
    keep_idx_set = set(keep_idx.tolist())

    # remap kept concepts to compact ids 0..K-1 (sorted for determinism)
    kept = sorted(keep_idx.tolist())
    remap = {old: new for new, old in enumerate(kept)}
    K = len(kept)
    ids = [gid_list[o] for o in kept]
    vals = np.stack([raw_vals[o] for o in kept], axis=0)          # [K,16] NaN-filled
    gpres = np.stack([raw_gpres[o] for o in kept], axis=0)        # [K,4]

    # induced edges within kept set
    kept_edges = []
    for a, b in edge_set:
        if a in keep_idx_set and b in keep_idx_set:
            kept_edges.append((remap[a], remap[b]))
    kept_edges = sorted(set(kept_edges))
    if len(kept_edges) < 50:
        raise RuntimeError("too few edges after degree filter (%d)" % len(kept_edges))

    meta = dict(
        n_grounded_total=n_all, n_induced_edges_total=len(edge_set),
        n_kept_concepts=K, n_kept_edges=len(kept_edges),
        min_deg=cfg["min_deg"], cap_nodes=cfg["cap_nodes"],
    )
    return dict(ids=ids, vals=vals, gpres=gpres, edges=kept_edges, K=K, meta=meta)


def build_split_and_features(data, cfg):
    """Concept-level held-out split (leak-proof) + TRAIN-standardized grounding features."""
    ids = data["ids"]
    K = data["K"]
    heldout = np.array([_split_is_heldout(c, cfg["heldout_frac"]) for c in ids], dtype=bool)
    is_train = ~heldout
    train_idx = np.nonzero(is_train)[0]
    held_idx = np.nonzero(heldout)[0]
    if train_idx.shape[0] < 50 or held_idx.shape[0] < 20:
        raise RuntimeError("degenerate split: train=%d held=%d" % (train_idx.shape[0], held_idx.shape[0]))

    # standardize the 16 value dims using TRAIN statistics only (ignore NaN)
    vals = data["vals"]
    tr_vals = vals[train_idx]
    import warnings as _warnings
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore", RuntimeWarning)   # all-NaN column -> guarded below
        mu = np.nanmean(tr_vals, axis=0)
        sd = np.nanstd(tr_vals, axis=0)
    mu = np.nan_to_num(mu, nan=0.0)
    sd = np.where(np.isnan(sd) | (sd < 1e-6), 1.0, sd)
    z = (vals - mu[None, :]) / sd[None, :]
    z = np.where(np.isnan(z), 0.0, z)          # missing value -> train-mean (0 after centering)
    feats = np.concatenate([z, data["gpres"]], axis=1).astype(np.float32)   # [K, 20]

    # TRAIN-only training graph (both endpoints train); adjacency for positives
    train_set = set(train_idx.tolist())
    train_adj = {i: [] for i in train_idx.tolist()}
    for a, b in data["edges"]:
        if a in train_set and b in train_set:
            train_adj[a].append(b)
            train_adj[b].append(a)
    train_anchor_pool = np.array(sorted([i for i in train_idx.tolist() if len(train_adj[i]) > 0]),
                                 dtype=np.int64)
    if train_anchor_pool.shape[0] < 20:
        raise RuntimeError("too few train anchors with train-neighbours (%d)" % train_anchor_pool.shape[0])

    # held-out concept -> its TRAIN neighbours (eval target; never seen in training)
    held_test_neighbors = {i: [] for i in held_idx.tolist()}
    for a, b in data["edges"]:
        if heldout[a] and (not heldout[b]):
            held_test_neighbors[a].append(b)
        elif heldout[b] and (not heldout[a]):
            held_test_neighbors[b].append(a)
    eval_held = [i for i in held_idx.tolist()
                 if len(set(held_test_neighbors[i])) >= cfg["min_test_neighbors"]]
    eval_held = sorted(eval_held)
    if len(eval_held) < 20:
        raise RuntimeError("too few eval held-out concepts with >=%d train-neighbours (%d)"
                           % (cfg["min_test_neighbors"], len(eval_held)))

    split_meta = dict(
        n_train=int(train_idx.shape[0]), n_heldout=int(held_idx.shape[0]),
        n_eval_heldout=len(eval_held),
        n_train_anchors=int(train_anchor_pool.shape[0]),
        mean_test_neighbors=float(np.mean([len(set(held_test_neighbors[i])) for i in eval_held])),
        n_train_train_edges=int(sum(len(v) for v in train_adj.values()) // 2),
    )
    # TRAIN degree (popularity prior) aligned to train_idx ordering
    train_degree = np.array([len(train_adj[int(i)]) for i in train_idx.tolist()], dtype=np.float64)

    return dict(
        feats=feats, is_train=is_train, train_idx=train_idx,
        train_adj=train_adj, train_anchor_pool=train_anchor_pool,
        train_degree=train_degree,
        eval_held=np.array(eval_held, dtype=np.int64),
        held_test_neighbors={i: sorted(set(held_test_neighbors[i])) for i in eval_held},
        split_meta=split_meta,
    )


# ---------------------------------------------------------------------------
# Encoder + teacher-free objective
# ---------------------------------------------------------------------------
class Encoder(torch.nn.Module):
    def __init__(self, feat_dim, hidden, code_dim):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(feat_dim, hidden),
            torch.nn.GELU(),
            torch.nn.Linear(hidden, code_dim),
        )

    def forward(self, x):
        return self.net(x)


def _l2(h, eps=1e-8):
    return h / (h.norm(dim=1, keepdim=True) + eps)


def info_nce(z_anchor, z_pos_target, temp):
    """InfoNCE: anchor (online) vs a batch of positive targets (EMA); diagonal = positive."""
    za = _l2(z_anchor)
    zp = _l2(z_pos_target)
    logits = (za @ zp.t()) / temp
    labels = torch.arange(za.shape[0])
    return 0.5 * (torch.nn.functional.cross_entropy(logits, labels)
                  + torch.nn.functional.cross_entropy(logits.t(), labels))


def vicreg(h, lambda_var, lambda_cov, gamma=1.0, eps=1e-4):
    hc = h - h.mean(dim=0, keepdim=True)
    n = hc.shape[0]
    d = hc.shape[1]
    std = torch.sqrt(hc.var(dim=0) + eps)
    var_term = torch.mean(torch.relu(gamma - std))
    cov = (hc.t() @ hc) / max(n - 1, 1)
    off = (cov ** 2).sum() - (torch.diagonal(cov) ** 2).sum()
    cov_term = off / d
    return lambda_var * var_term + lambda_cov * cov_term


def train_encoder(feats, train_adj, train_anchor_pool, cfg, seed):
    """Teacher-free EMA self-distillation + VICReg. Returns online encoder (eval mode)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    X = torch.from_numpy(feats)
    online = Encoder(feats.shape[1], cfg["hidden"], cfg["code_dim"])
    target = Encoder(feats.shape[1], cfg["hidden"], cfg["code_dim"])
    target.load_state_dict(online.state_dict())
    for p in target.parameters():
        p.requires_grad_(False)
    opt = torch.optim.Adam(online.parameters(), lr=cfg["lr"])
    rng = np.random.default_rng(seed + 7)
    m = cfg["ema"]

    log_every = max(1, cfg["epochs"] // 5)
    t0 = time.perf_counter()
    for ep in range(cfg["epochs"]):
        bs = min(cfg["batch"], train_anchor_pool.shape[0])
        a_idx = rng.choice(train_anchor_pool, size=bs, replace=False)
        p_idx = np.array([train_adj[int(a)][rng.integers(0, len(train_adj[int(a)]))]
                          for a in a_idx], dtype=np.int64)
        xa = X[torch.from_numpy(a_idx.astype(np.int64))]
        xp = X[torch.from_numpy(p_idx)]
        za = online(xa)
        with torch.no_grad():
            zp_t = target(xp)
        loss = info_nce(za, zp_t, cfg["temp"]) + vicreg(za, cfg["lambda_var"], cfg["lambda_cov"])
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite loss at ep=%d (seed=%d)" % (ep, seed))
        opt.zero_grad()
        loss.backward()
        opt.step()
        with torch.no_grad():
            for pt, po in zip(target.parameters(), online.parameters()):
                pt.mul_(m).add_(po, alpha=1.0 - m)
        if (ep % log_every == 0) or (ep == cfg["epochs"] - 1):
            _log("  train seed=%d ep=%d/%d loss=%.4f (%.1fs)"
                 % (seed, ep, cfg["epochs"], float(loss.detach()), time.perf_counter() - t0))
    online.eval()
    return online


def encode_all(encoder, feats):
    with torch.no_grad():
        emb = _l2(encoder(torch.from_numpy(feats))).numpy().astype(np.float32)
    return emb


def train_lookup_table(K, train_idx, train_adj, train_anchor_pool, cfg, seed):
    """Transductive per-concept embedding table (store-then-recall floor). NOT a function of features."""
    torch.manual_seed(seed + 101)
    emb = torch.nn.Embedding(K, cfg["code_dim"])
    torch.nn.init.normal_(emb.weight, std=0.05)
    opt = torch.optim.Adam(emb.parameters(), lr=cfg["lr"])
    rng = np.random.default_rng(seed + 202)
    for ep in range(cfg["epochs"]):
        bs = min(cfg["batch"], train_anchor_pool.shape[0])
        a_idx = rng.choice(train_anchor_pool, size=bs, replace=False)
        p_idx = np.array([train_adj[int(a)][rng.integers(0, len(train_adj[int(a)]))]
                          for a in a_idx], dtype=np.int64)
        za = emb(torch.from_numpy(a_idx.astype(np.int64)))
        zp = emb(torch.from_numpy(p_idx))
        loss = info_nce(za, zp, cfg["temp"]) + vicreg(za, cfg["lambda_var"], cfg["lambda_cov"])
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite lookup loss at ep=%d" % ep)
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        codes = _l2(emb.weight.detach()).numpy().astype(np.float32)
    return codes


# ---------------------------------------------------------------------------
# Held-out-NEW-concept evaluation
# ---------------------------------------------------------------------------
def _score_metrics(score, pos_rows, T):
    """Given a per-candidate score vector over T train concepts + positive rows, return
    (auc, recall@10 hit, reciprocal-rank, pos_minus_neg_margin) or None if degenerate."""
    pos_rows = sorted(set(pos_rows))
    if len(pos_rows) == 0 or len(pos_rows) >= T:
        return None
    pos_mask = np.zeros(T, dtype=bool)
    pos_mask[pos_rows] = True
    n_pos = int(pos_mask.sum())
    n_neg = T - n_pos
    order = np.argsort(score, kind="mergesort")             # ascending
    ranks = np.empty(T, dtype=np.float64)
    ranks[order] = np.arange(1, T + 1)                      # higher score -> higher rank
    auc = (ranks[pos_mask].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    desc = np.argsort(-score, kind="mergesort")
    top10 = set(desc[:10].tolist())
    recall = 1.0 if any(p in top10 for p in pos_rows) else 0.0
    pos_set = set(pos_rows)
    rr = 0.0
    for rk, idx in enumerate(desc.tolist(), start=1):
        if idx in pos_set:
            rr = 1.0 / rk
            break
    margin = float(score[pos_mask].mean() - score[~pos_mask].mean())
    return float(auc), recall, rr, margin


def _aggregate_eval(rows, T):
    if len(rows) == 0:
        raise RuntimeError("no evaluable held-out concepts after eval filtering")
    a = np.array([r[0] for r in rows]); rc = np.array([r[1] for r in rows])
    mr = np.array([r[2] for r in rows]); mg = np.array([r[3] for r in rows])
    return dict(
        heldout_auc=float(a.mean()), heldout_auc_std=float(a.std()),
        recall_at_10=float(rc.mean()), mrr=float(mr.mean()),
        neighbor_cos_margin=float(mg.mean()),
        n_evaluated=len(rows), train_candidates=int(T),
    )


def eval_heldout(codes, train_idx, eval_held, held_test_neighbors):
    """Rank ALL train concepts by cosine to enc(held-out). AUC(base 0.5)/recall@10/MRR/margin."""
    train_idx = np.asarray(train_idx, dtype=np.int64)
    Ztr = codes[train_idx]                                  # [T, d]
    train_pos_in_row = {int(t): r for r, t in enumerate(train_idx.tolist())}
    T = Ztr.shape[0]
    rows = []
    for h in eval_held.tolist():
        cos = Ztr @ codes[h]
        pos_rows = [train_pos_in_row[n] for n in held_test_neighbors[h] if n in train_pos_in_row]
        m = _score_metrics(cos, pos_rows, T)
        if m is not None:
            rows.append(m)
    return _aggregate_eval(rows, T)


def eval_popularity(train_idx, train_degree, eval_held, held_test_neighbors):
    """Popularity prior baseline: rank train concepts by TRAIN-degree, identical for every
    held-out concept (a new concept is guessed to connect to popular hubs)."""
    train_idx = np.asarray(train_idx, dtype=np.int64)
    train_pos_in_row = {int(t): r for r, t in enumerate(train_idx.tolist())}
    T = train_idx.shape[0]
    score = train_degree.astype(np.float64)                 # shared across all held-out
    rows = []
    for h in eval_held.tolist():
        pos_rows = [train_pos_in_row[n] for n in held_test_neighbors[h] if n in train_pos_in_row]
        m = _score_metrics(score, pos_rows, T)
        if m is not None:
            rows.append(m)
    return _aggregate_eval(rows, T)


def _emb_digest(emb):
    return hashlib.sha256(np.ascontiguousarray(emb.astype(np.float32)).tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# One seed: build codes for every arm + evaluate held-out
# ---------------------------------------------------------------------------
def run_seed(seed, data, split, cfg):
    feats = split["feats"]
    K = data["K"]
    train_idx = split["train_idx"]
    train_adj = split["train_adj"]
    pool = split["train_anchor_pool"]
    eval_held = split["eval_held"]
    tn = split["held_test_neighbors"]

    arm_codes = {}
    arm_metrics = {}

    # ARM_GROUNDING_ENCODER (primary, trained)
    enc = train_encoder(feats, train_adj, pool, cfg, seed)
    arm_codes[PRIMARY_ARM] = encode_all(enc, feats)

    # ARM_RANDOM_INIT (untrained encoder on same features)
    torch.manual_seed(seed + 55)
    rand_enc = Encoder(feats.shape[1], cfg["hidden"], cfg["code_dim"]).eval()
    arm_codes[RANDOM_ARM] = encode_all(rand_enc, feats)

    # ARM_RAW_GROUNDING (no encoder; standardized grounding features L2-normalized as codes)
    arm_codes[RAW_ARM] = _l2(torch.from_numpy(feats)).numpy().astype(np.float32)

    # ARM_FEATURE_SHUFFLE (grounding rows permuted across concept ids, then train encoder)
    perm = np.random.default_rng(seed + 909).permutation(K)
    feats_shuf = feats[perm]
    enc_shuf = train_encoder(feats_shuf, train_adj, pool, cfg, seed + 1)
    arm_codes[SHUFFLE_ARM] = encode_all(enc_shuf, feats_shuf)

    # ARM_LOOKUP_RECALL (transductive table; NEW concepts have NO row -> TRUE no-information floor:
    # each held-out concept gets an independent RANDOM unit code -> ranking is random -> AUC ~ 0.5.
    # (mean-train-code fill was rejected: the train centroid encodes a POPULARITY prior, which is a
    #  strong baseline, NOT a floor -- that role is now the explicit ARM_POPULARITY below.)
    lut = train_lookup_table(K, train_idx, train_adj, pool, cfg, seed)
    is_train = split["is_train"]
    lut_codes = lut.copy()
    held_rows = np.nonzero(~is_train)[0]
    rc = np.random.default_rng(seed + 303).standard_normal((held_rows.shape[0], cfg["code_dim"]))
    rc = rc / (np.linalg.norm(rc, axis=1, keepdims=True) + 1e-8)
    lut_codes[held_rows] = rc.astype(np.float32)
    arm_codes[LOOKUP_ARM] = lut_codes.astype(np.float32)

    for arm in CODE_ARMS:
        ev = eval_heldout(arm_codes[arm], train_idx, eval_held, tn)
        ev["emb_digest"] = _emb_digest(arm_codes[arm])
        arm_metrics[arm] = ev
        _log("seed=%d arm=%s heldout_auc=%.4f recall@10=%.4f mrr=%.4f margin=%.4f (n=%d)"
             % (seed, arm, ev["heldout_auc"], ev["recall_at_10"], ev["mrr"],
                ev["neighbor_cos_margin"], ev["n_evaluated"]))

    # ARM_POPULARITY (explicit degree-prior strong baseline; scored directly, no codes)
    ev = eval_popularity(train_idx, split["train_degree"], eval_held, tn)
    ev["emb_digest"] = hashlib.sha256(split["train_degree"].tobytes()).hexdigest()
    arm_metrics[POP_ARM] = ev
    _log("seed=%d arm=%s heldout_auc=%.4f recall@10=%.4f mrr=%.4f (n=%d)"
         % (seed, POP_ARM, ev["heldout_auc"], ev["recall_at_10"], ev["mrr"], ev["n_evaluated"]))

    # ARMS-MUST-DIFFER (META_RULE_AF) over the code arms (POP_ARM is not a codes matrix)
    digs = {a: arm_metrics[a]["emb_digest"] for a in CODE_ARMS}
    dl = sorted(digs.items())
    for i in range(len(dl)):
        for j in range(i + 1, len(dl)):
            assert dl[i][1] != dl[j][1], ("META_RULE_AF VIOLATION: arms %s and %s bit-identical"
                                          % (dl[i][0], dl[j][0]))
    return arm_metrics


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed, cfg, data_meta, split_meta):
    def series(arm, key):
        return np.array([m[arm][key] for m in per_seed], dtype=np.float64)

    agg = {}
    for arm in ALL_ARMS:
        agg[arm] = dict(
            heldout_auc_mean=float(series(arm, "heldout_auc").mean()),
            heldout_auc_min=float(series(arm, "heldout_auc").min()),
            recall_at_10_mean=float(series(arm, "recall_at_10").mean()),
            mrr_mean=float(series(arm, "mrr").mean()),
            neighbor_cos_margin_mean=float(series(arm, "neighbor_cos_margin").mean()),
            n_seeds=len(per_seed),
        )

    enc = agg[PRIMARY_ARM]["heldout_auc_mean"]
    raw = agg[RAW_ARM]["heldout_auc_mean"]
    rand = agg[RANDOM_ARM]["heldout_auc_mean"]
    shuf = agg[SHUFFLE_ARM]["heldout_auc_mean"]
    look = agg[LOOKUP_ARM]["heldout_auc_mean"]
    pop = agg[POP_ARM]["heldout_auc_mean"]
    max_collapse = max(shuf, look)

    lo, hi = COLLAPSE_BAND
    can_fail_fired = bool(lo <= shuf <= hi and lo <= look <= hi)

    margin_collapse = enc - max_collapse
    margin_raw = enc - raw
    margin_pop = enc - pop            # THE genuine-generalization bar: beat the popularity prior

    if (enc >= HP_AUC and margin_collapse >= HP_MARGIN_OVER_COLLAPSE
            and margin_raw >= HP_MARGIN_OVER_RAW and margin_pop >= HP_MARGIN_OVER_POP
            and can_fail_fired):
        verdict = "HARD_PASS"
    elif ((not can_fail_fired) or (enc < HF_AUC) or (margin_collapse < 0.03)
            or (enc < raw - 0.01) or (margin_pop < 0.0)):
        # margin_pop < 0 => encoder does NOT beat a trivial popularity prior = fails the mission bar
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | ENCODER heldout_auc=%.4f (min=%.4f, recall@10=%.4f mrr=%.4f) | "
        "raw_grounding=%.4f (enc-raw=%+.4f) random_init=%.4f | "
        "POPULARITY=%.4f (enc-pop=%+.4f) | "
        "COLLAPSE shuffle=%.4f lookup_rand=%.4f -> can_fail_fired=%s (enc-maxcollapse=%+.4f) | "
        "train=%d heldout_eval=%d train_edges=%d | grounded_universe K=%d E=%d"
        % (verdict, enc, agg[PRIMARY_ARM]["heldout_auc_min"],
           agg[PRIMARY_ARM]["recall_at_10_mean"], agg[PRIMARY_ARM]["mrr_mean"],
           raw, margin_raw, rand, pop, margin_pop, shuf, look, can_fail_fired, margin_collapse,
           split_meta["n_train"], split_meta["n_eval_heldout"], split_meta["n_train_train_edges"],
           data_meta["n_kept_concepts"], data_meta["n_kept_edges"]))

    gates = dict(
        encoder_heldout_auc=enc, encoder_heldout_auc_min=agg[PRIMARY_ARM]["heldout_auc_min"],
        raw_grounding_auc=raw, random_init_auc=rand, popularity_auc=pop,
        shuffle_auc=shuf, lookup_auc=look, max_collapse_auc=max_collapse,
        margin_over_collapse=margin_collapse, margin_over_raw=margin_raw, margin_over_popularity=margin_pop,
        can_fail_fired=can_fail_fired, collapse_band=list(COLLAPSE_BAND),
        hp_auc=HP_AUC, hf_auc=HF_AUC,
        hp_margin_over_collapse=HP_MARGIN_OVER_COLLAPSE, hp_margin_over_raw=HP_MARGIN_OVER_RAW,
        hp_margin_over_popularity=HP_MARGIN_OVER_POP,
    )
    return verdict, verdict_msg, agg, gates


# ---------------------------------------------------------------------------
# Discriminator self-test: proves the held-out AUC metric is telemetry-sensitive
# ---------------------------------------------------------------------------
def discriminator_selftest():
    """Planted-neighbourhood synthetic: codes aligned to a block structure -> AUC high;
    random codes -> AUC ~0.5; a code table with NO held-out row (mean fill) -> AUC ~0.5."""
    rng = np.random.default_rng(0)
    n_blocks = 6
    per = 40
    K = n_blocks * per
    d = 16
    block = np.repeat(np.arange(n_blocks), per)
    centers = rng.standard_normal((n_blocks, d))
    codes = centers[block] + 0.10 * rng.standard_normal((K, d))
    codes = codes / (np.linalg.norm(codes, axis=1, keepdims=True) + 1e-8)
    rand_codes = rng.standard_normal((K, d))
    rand_codes = rand_codes / (np.linalg.norm(rand_codes, axis=1, keepdims=True) + 1e-8)

    heldout = np.array([i % 5 == 0 for i in range(K)], dtype=bool)
    train_idx = np.nonzero(~heldout)[0]
    eval_held = np.nonzero(heldout)[0]
    # true neighbours = same-block train concepts
    tn = {}
    for h in eval_held.tolist():
        same = [t for t in train_idx.tolist() if block[t] == block[h]]
        tn[h] = same[:8]
    eval_held = np.array([h for h in eval_held.tolist() if len(tn[h]) >= 2], dtype=np.int64)

    ev_struct = eval_heldout(codes, train_idx, eval_held, tn)
    ev_rand = eval_heldout(rand_codes, train_idx, eval_held, tn)
    # mean-fill held-out rows (store-then-recall floor)
    mean_code = codes[train_idx].mean(axis=0)
    mean_code = mean_code / (np.linalg.norm(mean_code) + 1e-8)
    look = codes.copy()
    look[heldout] = mean_code[None, :]
    ev_look = eval_heldout(look, train_idx, eval_held, tn)

    res = dict(auc_struct=ev_struct["heldout_auc"], auc_rand=ev_rand["heldout_auc"],
               auc_lookup_fill=ev_look["heldout_auc"])
    ok = (ev_struct["heldout_auc"] >= 0.75
          and abs(ev_rand["heldout_auc"] - 0.5) < 0.08
          and abs(ev_look["heldout_auc"] - 0.5) < 0.08)
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

    # discriminator telemetry-sensitivity self-test (ALWAYS runs)
    st_ok, st_res = discriminator_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED (AUC metric not telemetry-sensitive): %s" % st_res,
            summary="discriminator selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res))
        raise SystemExit(1)

    _log("loading grounded subgraph (min_deg=%d cap=%d)..." % (cfg["min_deg"], cfg["cap_nodes"]))
    data = load_grounded_subgraph(cfg)
    _log("grounded universe: %s" % data["meta"])
    split = build_split_and_features(data, cfg)
    _log("split: %s" % split["split_meta"])

    if run_mode == "self_test":
        pm = run_seed(cfg["seeds"][0], data, split, cfg)
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS discriminator + end-to-end held-out eval exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, data_meta=data["meta"], split_meta=split["split_meta"],
            encoder_auc=pm[PRIMARY_ARM]["heldout_auc"], shuffle_auc=pm[SHUFFLE_ARM]["heldout_auc"],
            lookup_auc=pm[LOOKUP_ARM]["heldout_auc"], raw_auc=pm[RAW_ARM]["heldout_auc"]))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, data, split, cfg)
            per_seed.append(pm)
            write_partial(out_dir_path, seed, dict(seed=seed, arms=pm, run_mode=run_mode))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:   # per-seed failure-class instrumentation (META_RULE_J)
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds got %d (failures=%s)"
                        % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, data_meta=data["meta"], split_meta=split["split_meta"]))
        raise SystemExit(1)

    verdict, verdict_msg, agg, gates = aggregate_and_verdict(
        per_seed, cfg, data["meta"], split["split_meta"])

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg,
        data_meta=data["meta"], split_meta=split["split_meta"],
        gates=gates, arms_aggregate=agg, discriminator_selftest=st_res,
        seed_failures=seed_failures,
        per_seed=[{a: {k: v for k, v in per_seed[i][a].items() if k != "emb_digest"}
                   for a in per_seed[i]} for i in range(len(per_seed))],
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
    except Exception as e:   # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
