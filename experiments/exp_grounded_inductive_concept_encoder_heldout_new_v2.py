"""Teacher-free GROUNDED + TYPED-RELATIONAL-CONTEXT INDUCTIVE concept encoder, judged on
held-out-NEW-concept generalization under POPULARITY-CONTROLLED (degree-matched) evaluation.

v2 iterates the HONEST HARD_FAIL of v1
(grounded_inductive_concept_encoder_heldout_new_v1): v1 earned a real-but-marginal signal
(held-out-NEW AUC 0.588 > collapse ~0.50 and > raw-grounding 0.563) but LOST DECISIVELY to a
popularity/degree prior (0.815) under random negatives on a hub-dominated graph.

TWO DIAGNOSED GAPS (brain-fidelity + test-fairness) drive v2:

(1) BRAIN: concept meaning is largely RELATIONAL -- a concept is defined by its relations, not
    only its perceptual/affective profile. v1 gave the encoder GROUNDING-ONLY input, withholding
    relational context from the INPUT (it used relations only for the training objective).
    FIX: the encoder input for a held-out NEW concept = its grounding norms TOGETHER WITH a
    TYPED-RELATIONAL-NEIGHBOR CONTEXT (per-relation-type mean-pool of the grounding of its KNOWN
    (train) neighbors, keyed by relation type). GraIL-style genuine induction: told a few facts
    about a new thing, infer the rest.

(2) FAIRNESS: v1 used random negatives -> popularity is a confound (true neighbours ARE hubs, random
    negatives are mostly low-degree, so degree trivially separates). FIX: POPULARITY-CONTROLLED /
    DEGREE-MATCHED negatives. For each positive (a true neighbour of degree d), negatives are drawn
    from the SAME degree bucket. A pure degree/popularity score then CANNOT separate them (AUC -> 0.5
    by construction); the encoder must add signal ON TOP OF the degree prior.

HARD INVARIANTS (project locks, unchanged):
  - TEACHER-FREE: NO GloVe/BGE/transformer/borrowed vector anywhere (teacher, target, init, feature).
    The only input features are measured grounding norms + the KB's own graph structure.
  - INDUCTIVE: encoder = f(grounding_features, typed-neighbour-context) -> code. A held-out NEW concept
    is placed from its FEATURES + KNOWN-CONTEXT, never a learned per-concept lookup.
  - LEAK-PROOF: held-out concepts entirely removed from training; each concept's edges are globally
    split (deterministic sha256 on the undirected concept PAIR) into a CONTEXT set (shown as encoder
    input) and a disjoint TARGET/EVAL set (predicted). context ∩ eval = empty by construction.
    Splitting on the concept-PAIR (collapsing relations) prevents cross-relation leak (a pair that is
    a TARGET positive can never also appear in the CONTEXT aggregate via another relation).

DESIGN (fair, leak-proof, can-fail):
  * Universe = grounded concepts (grounding dict present) with induced-degree >= MIN_DEG in the
    grounded-induced subgraph of cskg_foundation_v1. Edges keep their RELATION type.
  * Concept-level held-out split (leak-proof): sha256(id) -> TRAIN or HELDOUT. Training uses only
    train-train pairs. Held-out concepts never seen by the encoder.
  * Global pair split CONTEXT/TARGET (sha256 on "min|max" concept-pair; relation-collapsed).
  * Encoder input per concept = [own grounding(16) + own group-present(4)] concat
    [per-relation-type mean of context-neighbours' standardized grounding(16) + presence(1) + log-count(1)]
    over the top-R relation types. Context neighbours are TRAIN concepts reached via CONTEXT pairs.
  * Teacher-free objective (as v1): InfoNCE over relational-neighbour positives (positives sampled
    from TARGET pairs, disjoint from context) vs an EMA self-teacher (BYOL/DINO) + VICReg anti-collapse.
  * FAIR METRIC (held-out-NEW under degree-matched negatives): for each held-out h and each TARGET
    (eval) neighbour t (degree d_t, bucket b), sample M negatives from the SAME degree bucket b
    (excluding h's neighbours). degree-matched AUC = P(score(h,t) > score(h,neg)); also recall@k / MRR
    over the {t} + M-negatives candidate set. The SAME sampled negatives are scored by every arm
    (fair comparison). ALSO report the v1-style full-candidate AUC (all train concepts) to expose the
    popularity confound directly (pop full ~0.8 vs pop degree-matched ~0.5).

ARMS:
  ARM_CONTEXT_ENCODER  : encoder on grounding + typed-relational context.          [PRIMARY]
  ARM_GROUNDING_ONLY   : v1-style encoder on grounding ALONE (context ablated).    [context added-value ref]
  ARM_RAW_CONTEXT      : NO encoder; cosine of the raw grounding+context input.    [learning added-value ref]
  ARM_POPULARITY       : degree prior. Under degree-matched -> ~0.5 (validates the [must-BEAT baseline (a)]
                         matching); under full-candidate -> strong (the v1 confound).
  ARM_STRUCT_ADAMIC_ADAR: non-learned structural heuristic (Adamic-Adar) from the  [must-BEAT baseline (b);
                         CONTEXT edges. Beating it proves LEARNED meaning adds value  THE real bar]
                         beyond graph proximity.
  ARM_INPUT_SHUFFLE    : full encoder input permuted across concept ids -> ~0.5.    [COLLAPSE / leak witness]
  ARM_LOOKUP_RECALL    : transductive table; held-out has NO row -> random code -> ~0.5. [COLLAPSE floor]

CAN-FAIL GATES: ARM_LOOKUP_RECALL and ARM_INPUT_SHUFFLE must sit at ~0.5 (else LEAK/BROKEN); and
ARM_POPULARITY under degree-matched must sit at ~0.5 (else the degree-matching is BROKEN).

DEFLATE: if the encoder still loses to popularity (won't, by construction, under degree-matched) or to
the structural heuristic, that is HONEST -> report it + the per-item WHY. Beating (a)+(b) under
degree-matched negatives is the real bar.

CPU-only. No GPU. No network. ASCII-only. No emojis.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test over code arms)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator has base=0.5 exactly; collapse+pop-degmatched controls witness the floor
# - baseline_in_band at smoke: collapse controls (input_shuffle,lookup) + pop-degmatched must sit in [0.44,0.56]
# - discriminator survives scale: smoke IS a genuine held-out-new-concept degree-matched test at few-k concepts
# - HARD_PASS strictly above floor: dm_auc>=0.60 AND dm_auc-struct>=0.02 AND dm_auc-pop_dm>=0.05 AND can_fail
# - HP_SCOPE: gates apply to ARM_CONTEXT_ENCODER (primary) only
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; controls witness it empirically)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg
# - deterministic seeding: sha256 concept+pair split + fixed int seeds + sorted(); no hash()/list(set()) (PROT-023)
# - no substrate KGStore/fit objects (self-contained jsonl reader) -> F.1/F.2 real_code_path N/A
# - progress_logging: print_flush_true (timeout < 30min so not mandatory, but present)
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

ANCHOR_NAME = "grounded_inductive_concept_encoder_heldout_new_v2"
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
GROUND_DIM = N_VALUE_DIMS + N_GROUPS              # 20

# ---------------------------------------------------------------------------
# Config profiles
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    min_deg=2, cap_nodes=600, seeds=[7], epochs=15, batch=128,
    code_dim=32, hidden=64, lr=5e-3, temp=0.2, ema=0.9,
    lambda_var=1.0, lambda_cov=1.0, heldout_frac=0.2, min_test_neighbors=1,
    top_rel=8, context_frac=0.5, m_neg=20, max_pos=5,
)
SMOKE_CFG = dict(
    min_deg=3, cap_nodes=5000, seeds=[7, 13], epochs=80, batch=512,
    code_dim=128, hidden=256, lr=3e-3, temp=0.15, ema=0.99,
    lambda_var=1.0, lambda_cov=1.0, heldout_frac=0.2, min_test_neighbors=2,
    top_rel=16, context_frac=0.5, m_neg=50, max_pos=8,
)
FULL_CFG = dict(
    min_deg=3, cap_nodes=8700, seeds=[7, 13, 17], epochs=140, batch=1024,
    code_dim=192, hidden=384, lr=2.5e-3, temp=0.12, ema=0.995,
    lambda_var=1.0, lambda_cov=1.0, heldout_frac=0.2, min_test_neighbors=2,
    top_rel=16, context_frac=0.5, m_neg=50, max_pos=10,
)

# Deterministic salts (fixed; identical across arms + model-seeds).
CONCEPT_SPLIT_SALT = "gictc_v2_concept_split::"
PAIR_SPLIT_SALT = "gictc_v2_pair_split::"
NEG_SAMPLE_SEED = 20260726     # degree-matched negatives seeded identically across arms

# Pre-reg bands (applied to ARM_CONTEXT_ENCODER primary DEGREE-MATCHED AUC).
HP_AUC = 0.60                    # HARD_PASS absolute degree-matched AUC floor (strictly above chance 0.5)
HF_AUC = 0.53                    # below this = HARD_FAIL (essentially chance under degree-matching)
HP_MARGIN_OVER_STRUCT = 0.02     # enc must beat the structural heuristic (Adamic-Adar) by this (THE bar)
HP_MARGIN_OVER_POP = 0.05        # enc must beat degree-matched popularity by this
COLLAPSE_BAND = (0.44, 0.56)     # collapse controls (input_shuffle, lookup) MUST sit here
POP_MATCH_BAND = (0.45, 0.55)    # degree-matched popularity MUST sit here (else matching broken)

PRIMARY_ARM = "ARM_CONTEXT_ENCODER"
GROUND_ARM = "ARM_GROUNDING_ONLY"
RAW_ARM = "ARM_RAW_CONTEXT"
POP_ARM = "ARM_POPULARITY"
STRUCT_ARM = "ARM_STRUCT_ADAMIC_ADAR"
SHUFFLE_ARM = "ARM_INPUT_SHUFFLE"
LOOKUP_ARM = "ARM_LOOKUP_RECALL"
# Arms scored by cosine over a codes matrix:
CODE_ARMS = [PRIMARY_ARM, GROUND_ARM, RAW_ARM, SHUFFLE_ARM, LOOKUP_ARM]
# Arms scored by a bespoke pair score fn:
FN_ARMS = [POP_ARM, STRUCT_ARM]
ALL_ARMS = CODE_ARMS + FN_ARMS


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
# Deterministic splits (sha256; PYTHONHASHSEED-independent)
# ---------------------------------------------------------------------------
def _concept_is_heldout(concept_id, heldout_frac):
    h = hashlib.sha256((CONCEPT_SPLIT_SALT + concept_id).encode("utf-8")).digest()
    r = int.from_bytes(h[:8], "big") / float(2 ** 64)
    return r < heldout_frac


def _pair_is_context(a_id, b_id, context_frac):
    """Deterministic CONTEXT/TARGET assignment for an undirected concept pair (relation-collapsed)."""
    lo, hi = (a_id, b_id) if a_id <= b_id else (b_id, a_id)
    h = hashlib.sha256((PAIR_SPLIT_SALT + lo + "|" + hi).encode("utf-8")).digest()
    r = int.from_bytes(h[:8], "big") / float(2 ** 64)
    return r < context_frac


# ---------------------------------------------------------------------------
# Foundation loader: grounded induced subgraph WITH relation types
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
                    vals[off + keys.index(k)] = float(v)
        off += len(keys)
    return vals, gpres


def load_grounded_subgraph(cfg):
    """Load grounded concepts + induced subgraph with relation types. Returns dict of arrays."""
    if not os.path.exists(NODES_PATH):
        raise FileNotFoundError("nodes.jsonl not found at %s" % NODES_PATH)

    gid_list = []
    raw_vals = []
    raw_gpres = []
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
    if len(gid_list) < 50:
        raise RuntimeError("too few grounded nodes (%d)" % len(gid_list))

    gid_set = set(gid_list)
    idx_of = {c: i for i, c in enumerate(gid_list)}

    # induced typed edges among grounded concepts: pair(a<b) -> set(relation)
    pair_rels = {}
    for shard in sorted(glob.glob(EDGES_GLOB)):
        with open(shard, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                e = json.loads(line)
                s = e.get("subject")
                o = e.get("obj")
                rel = e.get("relation") or "OTHER"
                if s is None or o is None or s == o:
                    continue
                if s in gid_set and o in gid_set:
                    a, b = idx_of[s], idx_of[o]
                    if a > b:
                        a, b = b, a
                    pair_rels.setdefault((a, b), set()).add(rel)
    if len(pair_rels) < 50:
        raise RuntimeError("too few induced pairs among grounded (%d)" % len(pair_rels))

    n_all = len(gid_list)
    induced_deg = np.zeros(n_all, dtype=np.int64)
    for (a, b) in pair_rels:
        induced_deg[a] += 1
        induced_deg[b] += 1

    keep_mask = induced_deg >= cfg["min_deg"]
    keep_idx = np.nonzero(keep_mask)[0]
    if keep_idx.shape[0] > cfg["cap_nodes"]:
        order = sorted(keep_idx.tolist(), key=lambda i: (-int(induced_deg[i]), gid_list[i]))
        keep_idx = np.array(sorted(order[:cfg["cap_nodes"]]), dtype=np.int64)
    keep_idx_set = set(keep_idx.tolist())

    kept = sorted(keep_idx.tolist())
    remap = {old: new for new, old in enumerate(kept)}
    K = len(kept)
    ids = [gid_list[o] for o in kept]
    vals = np.stack([raw_vals[o] for o in kept], axis=0)          # [K,16] NaN-filled
    gpres = np.stack([raw_gpres[o] for o in kept], axis=0)        # [K,4]

    # relation frequency among kept pairs -> top-R vocabulary (+ OTHER bucket)
    rel_freq = {}
    kept_pair_rels = {}
    for (a, b), rels in pair_rels.items():
        if a in keep_idx_set and b in keep_idx_set:
            na, nb = remap[a], remap[b]
            key = (na, nb) if na < nb else (nb, na)
            kept_pair_rels[key] = set(rels)
            for r in rels:
                rel_freq[r] = rel_freq.get(r, 0) + 1
    if len(kept_pair_rels) < 50:
        raise RuntimeError("too few kept pairs after degree filter (%d)" % len(kept_pair_rels))

    top_r = cfg["top_rel"]
    rel_sorted = sorted(rel_freq.items(), key=lambda kv: (-kv[1], kv[0]))
    top_rels = [r for r, _ in rel_sorted[:top_r]]
    rel_id = {r: i for i, r in enumerate(top_rels)}
    R = len(top_rels) + 1                    # +1 = OTHER bucket
    other_id = R - 1

    def _rel_slot(r):
        return rel_id.get(r, other_id)

    meta = dict(
        n_grounded_total=n_all, n_induced_pairs_total=len(pair_rels),
        n_kept_concepts=K, n_kept_pairs=len(kept_pair_rels),
        min_deg=cfg["min_deg"], cap_nodes=cfg["cap_nodes"],
        top_rels=top_rels, n_rel_slots=R,
    )
    return dict(ids=ids, vals=vals, gpres=gpres, pair_rels=kept_pair_rels,
                K=K, R=R, rel_slot=_rel_slot, meta=meta)


# ---------------------------------------------------------------------------
# Split + typed-relational-context feature construction
# ---------------------------------------------------------------------------
def build_split_and_features(data, cfg):
    ids = data["ids"]
    K = data["K"]
    R = data["R"]
    rel_slot = data["rel_slot"]
    heldout = np.array([_concept_is_heldout(c, cfg["heldout_frac"]) for c in ids], dtype=bool)
    is_train = ~heldout
    train_idx = np.nonzero(is_train)[0]
    held_idx = np.nonzero(heldout)[0]
    if train_idx.shape[0] < 50 or held_idx.shape[0] < 20:
        raise RuntimeError("degenerate split: train=%d held=%d" % (train_idx.shape[0], held_idx.shape[0]))
    train_set = set(train_idx.tolist())

    # standardize the 16 value dims using TRAIN statistics only (ignore NaN)
    vals = data["vals"]
    tr_vals = vals[train_idx]
    import warnings as _warnings
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore", RuntimeWarning)
        mu = np.nanmean(tr_vals, axis=0)
        sd = np.nanstd(tr_vals, axis=0)
    mu = np.nan_to_num(mu, nan=0.0)
    sd = np.where(np.isnan(sd) | (sd < 1e-6), 1.0, sd)
    z = (vals - mu[None, :]) / sd[None, :]
    z = np.where(np.isnan(z), 0.0, z).astype(np.float64)         # [K,16] standardized grounding
    own_feat = np.concatenate([z, data["gpres"]], axis=1).astype(np.float64)   # [K,20]

    # classify pairs -> CONTEXT / TARGET (relation-collapsed) + track relations
    # context neighbours (train only) per concept per relation-slot; target neighbours (train only);
    # full train adjacency (context+target, train-train only) for degree + AA + negative exclusion.
    ctx_nei_by_rel = [dict() for _ in range(K)]     # concept -> {rel_slot: set(train j)}
    target_neigh = [set() for _ in range(K)]        # concept -> set(train j) via TARGET pairs
    train_adj = [set() for _ in range(K)]           # concept -> set(train neighbours, any pair)
    ctx_neigh_all = [dict() for _ in range(K)]      # concept -> {train j: weightless} for AA context

    for (a, b), rels in data["pair_rels"].items():
        a_tr = a in train_set
        b_tr = b in train_set
        is_ctx = _pair_is_context(ids[a], ids[b], cfg["context_frac"])
        # train adjacency: only train-train pairs count (held-out excluded from train graph)
        if a_tr and b_tr:
            train_adj[a].add(b)
            train_adj[b].add(a)
        # context aggregate: neighbour must be TRAIN; endpoint receiving context can be anything
        if is_ctx:
            if b_tr:
                for r in rels:
                    s = rel_slot(r)
                    ctx_nei_by_rel[a].setdefault(s, set()).add(b)
                ctx_neigh_all[a][b] = 1
            if a_tr:
                for r in rels:
                    s = rel_slot(r)
                    ctx_nei_by_rel[b].setdefault(s, set()).add(a)
                ctx_neigh_all[b][a] = 1
        else:  # TARGET pair
            if b_tr:
                target_neigh[a].add(b)
            if a_tr:
                target_neigh[b].add(a)

    # TRAIN degree (popularity prior) over train-train adjacency
    train_degree = np.array([len(train_adj[i]) for i in range(K)], dtype=np.float64)

    # ---- typed-relational-context feature matrix [K, 20 + R*(16+1+1)] ----
    per_rel_block = N_VALUE_DIMS + 2            # 16 mean + presence + log_count
    feat_dim = GROUND_DIM + R * per_rel_block
    feats = np.zeros((K, feat_dim), dtype=np.float32)
    feats[:, :GROUND_DIM] = own_feat.astype(np.float32)
    for i in range(K):
        base = GROUND_DIM
        for s in range(R):
            neigh = ctx_nei_by_rel[i].get(s)
            off = base + s * per_rel_block
            if neigh:
                nj = np.array(sorted(neigh), dtype=np.int64)
                feats[i, off:off + N_VALUE_DIMS] = z[nj].mean(axis=0).astype(np.float32)
                feats[i, off + N_VALUE_DIMS] = 1.0                       # presence
                feats[i, off + N_VALUE_DIMS + 1] = math.log1p(len(neigh))  # log-count
            # else zeros (absent)

    # grounding-only feature view (context zeroed): first GROUND_DIM dims only
    feats_ground = np.zeros_like(feats)
    feats_ground[:, :GROUND_DIM] = feats[:, :GROUND_DIM]

    # train anchors with >=1 TARGET train-neighbour (positives for training)
    train_anchor_pool = np.array(sorted([i for i in train_idx.tolist() if len(target_neigh[i]) > 0]),
                                 dtype=np.int64)
    if train_anchor_pool.shape[0] < 20:
        raise RuntimeError("too few train anchors with TARGET train-neighbours (%d)"
                           % train_anchor_pool.shape[0])
    target_neigh_list = {int(i): sorted(target_neigh[i]) for i in train_anchor_pool.tolist()}

    # held-out concepts with >= min_test_neighbors TARGET train-neighbours (eval positives)
    eval_held = [int(i) for i in held_idx.tolist()
                 if len(target_neigh[i]) >= cfg["min_test_neighbors"]]
    eval_held = sorted(eval_held)
    if len(eval_held) < 20:
        raise RuntimeError("too few eval held-out concepts with >=%d TARGET train-neighbours (%d)"
                           % (cfg["min_test_neighbors"], len(eval_held)))
    held_eval_pos = {i: sorted(target_neigh[i]) for i in eval_held}
    held_neigh_all = {i: set(train_adj[i]) | set(ctx_neigh_all[i].keys()) | set(target_neigh[i])
                      for i in eval_held}

    split_meta = dict(
        n_train=int(train_idx.shape[0]), n_heldout=int(held_idx.shape[0]),
        n_eval_heldout=len(eval_held),
        n_train_anchors=int(train_anchor_pool.shape[0]),
        n_train_train_pairs=int(train_degree.sum() // 2),
        mean_eval_pos=float(np.mean([len(held_eval_pos[i]) for i in eval_held])),
        mean_ctx_neigh=float(np.mean([len(ctx_neigh_all[i]) for i in eval_held])),
        feat_dim=feat_dim, n_rel_slots=R,
    )
    return dict(
        feats=feats, feats_ground=feats_ground, is_train=is_train,
        train_idx=train_idx, train_degree=train_degree,
        train_anchor_pool=train_anchor_pool, target_neigh_list=target_neigh_list,
        train_adj=[set(x) for x in train_adj],
        ctx_neigh_all=ctx_neigh_all,
        eval_held=np.array(eval_held, dtype=np.int64),
        held_eval_pos=held_eval_pos, held_neigh_all=held_neigh_all,
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


def train_encoder(feats, target_neigh_list, train_anchor_pool, cfg, seed):
    """Teacher-free EMA self-distillation + VICReg. Positives sampled from TARGET pairs (disjoint
    from the CONTEXT aggregate already baked into feats -> no leak). Returns online encoder (eval)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    X = torch.from_numpy(feats.astype(np.float32))
    online = Encoder(feats.shape[1], cfg["hidden"], cfg["code_dim"])
    target = Encoder(feats.shape[1], cfg["hidden"], cfg["code_dim"])
    target.load_state_dict(online.state_dict())
    for p in target.parameters():
        p.requires_grad_(False)
    opt = torch.optim.Adam(online.parameters(), lr=cfg["lr"])
    rng = np.random.default_rng(seed + 7)
    m = cfg["ema"]
    pool = train_anchor_pool
    log_every = max(1, cfg["epochs"] // 5)
    t0 = time.perf_counter()
    for ep in range(cfg["epochs"]):
        bs = min(cfg["batch"], pool.shape[0])
        a_idx = rng.choice(pool, size=bs, replace=False)
        p_idx = np.array([target_neigh_list[int(a)][rng.integers(0, len(target_neigh_list[int(a)]))]
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
        emb = _l2(encoder(torch.from_numpy(feats.astype(np.float32)))).numpy().astype(np.float32)
    return emb


def train_lookup_table(K, train_anchor_pool, target_neigh_list, cfg, seed):
    """Transductive per-concept embedding table (store-then-recall). Held-out has no meaningful row."""
    torch.manual_seed(seed + 101)
    emb = torch.nn.Embedding(K, cfg["code_dim"])
    torch.nn.init.normal_(emb.weight, std=0.05)
    opt = torch.optim.Adam(emb.parameters(), lr=cfg["lr"])
    rng = np.random.default_rng(seed + 202)
    pool = train_anchor_pool
    for ep in range(cfg["epochs"]):
        bs = min(cfg["batch"], pool.shape[0])
        a_idx = rng.choice(pool, size=bs, replace=False)
        p_idx = np.array([target_neigh_list[int(a)][rng.integers(0, len(target_neigh_list[int(a)]))]
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
# Degree-matched evaluation task construction (shared across arms)
# ---------------------------------------------------------------------------
def _deg_bucket(deg):
    return int(math.floor(math.log2(deg + 1.0)))


def build_eval_tasks(split, cfg):
    """Precompute degree-matched (h, pos, [negs]) tasks, identical for every arm. Negatives are drawn
    from a TIGHT proportional degree window [d_t*(1-tol), d_t*(1+tol)] around the positive's degree
    (widening tol only if too few candidates), exclude h's neighbours + the positive. Tight matching
    is essential: coarse (log2) buckets leave residual degree signal so popularity does NOT collapse
    to chance. Target: ARM_POPULARITY dm_auc ~0.5 (verified by the pop_match_ok gate)."""
    train_idx = split["train_idx"]
    train_degree = split["train_degree"]
    eval_held = split["eval_held"].tolist()
    held_eval_pos = split["held_eval_pos"]
    held_neigh_all = split["held_neigh_all"]

    train_rows = sorted(train_idx.tolist())
    deg_of = {int(c): int(train_degree[c]) for c in train_rows}
    # exact-degree pools (deterministic sorted lists)
    deg_to_rows = {}
    for c in train_rows:
        deg_to_rows.setdefault(deg_of[c], []).append(int(c))
    for d in deg_to_rows:
        deg_to_rows[d] = sorted(deg_to_rows[d])

    rng = np.random.default_rng(NEG_SAMPLE_SEED)
    m_neg = cfg["m_neg"]
    max_pos = cfg["max_pos"]
    # Degree is held constant only where it CAN be: every retained negative must have degree within
    # tol_abs = max(1, round(REL_TOL*dt)) of the positive. Tasks whose tight-matched pool is too small
    # (extreme-tail hubs with unique degree) are DROPPED -- a degree-controlled test is undefined there.
    REL_TOL = 0.08
    MIN_POOL = 12

    def _matched_pool(dt, excl, t):
        """Candidates with |deg - dt| <= tol_abs only. Returns (distinct_pool_list, max_abs_delta)."""
        tol_abs = max(1, int(round(REL_TOL * dt)))
        pool = []
        max_d = 0
        for delta in range(0, tol_abs + 1):
            sides = (dt,) if delta == 0 else (dt - delta, dt + delta)
            for side in sides:
                for c in deg_to_rows.get(side, ()):
                    if c != t and c not in excl:
                        pool.append(c)
                        if delta > max_d:
                            max_d = delta
        return pool, max_d, tol_abs

    tasks = []           # each: (h, pos_concept, np.array(neg_concepts))
    delta_used = []
    n_dropped = 0
    deg_kept = []
    for h in eval_held:
        pos_list = held_eval_pos[h]
        if len(pos_list) > max_pos:
            sel = rng.choice(np.array(pos_list, dtype=np.int64), size=max_pos, replace=False)
            pos_list = sorted(int(x) for x in sel.tolist())
        excl = held_neigh_all[h]
        for t in pos_list:
            dt = deg_of[int(t)]
            pool, ud, _tol = _matched_pool(dt, excl, int(t))
            distinct = sorted(set(pool))
            if len(distinct) < MIN_POOL:
                n_dropped += 1
                continue
            cand_arr = np.array(distinct, dtype=np.int64)
            replace = cand_arr.shape[0] < m_neg
            negs = rng.choice(cand_arr, size=m_neg, replace=replace)
            tasks.append((h, int(t), negs.astype(np.int64)))
            delta_used.append(ud)
            deg_kept.append(dt)
    if len(tasks) < 20:
        raise RuntimeError("too few degree-matched eval tasks (%d dropped=%d)" % (len(tasks), n_dropped))
    diag = dict(n_tasks=len(tasks), n_dropped=n_dropped,
                frac_retained=float(len(tasks) / max(1, len(tasks) + n_dropped)),
                mean_abs_delta=float(np.mean(delta_used)),
                deg_kept_max=int(np.max(deg_kept)), deg_kept_median=float(np.median(deg_kept)))
    return tasks, diag


def _dm_metrics_from_scores(pos_scores, neg_scores_2d):
    """pos_scores: [T]; neg_scores_2d: [T, M]. Returns dm_auc, recall@1, recall@5, mrr."""
    T, M = neg_scores_2d.shape
    diff = pos_scores[:, None] - neg_scores_2d            # [T,M]
    wins = (diff > 0).sum(axis=1).astype(np.float64)
    ties = (diff == 0).sum(axis=1).astype(np.float64)
    auc = float(((wins + 0.5 * ties) / M).mean())
    # rank of pos among {pos + M negs}: 1 + (# negs strictly greater) + 0.5*(#ties)
    greater = (neg_scores_2d > pos_scores[:, None]).sum(axis=1).astype(np.float64)
    eq = (neg_scores_2d == pos_scores[:, None]).sum(axis=1).astype(np.float64)
    rank = 1.0 + greater + 0.5 * eq
    recall1 = float((rank <= 1.0).mean())
    recall5 = float((rank <= 5.0).mean())
    mrr = float((1.0 / rank).mean())
    return dict(dm_auc=auc, dm_recall_at_1=recall1, dm_recall_at_5=recall5, dm_mrr=mrr,
                n_tasks=int(T))


def eval_code_arm(codes, tasks):
    """Cosine(code[h], code[c]) scoring on precomputed degree-matched tasks."""
    T = len(tasks)
    M = tasks[0][2].shape[0]
    pos = np.empty(T, dtype=np.float64)
    neg = np.empty((T, M), dtype=np.float64)
    for i, (h, t, negs) in enumerate(tasks):
        ch = codes[h]
        pos[i] = float(codes[t] @ ch)
        neg[i, :] = codes[negs] @ ch
    return _dm_metrics_from_scores(pos, neg)


def eval_popularity_arm(train_degree, tasks):
    """Degree score. Within a bucket ~constant -> ties -> dm_auc ~0.5 (validates matching)."""
    T = len(tasks)
    M = tasks[0][2].shape[0]
    pos = np.empty(T, dtype=np.float64)
    neg = np.empty((T, M), dtype=np.float64)
    for i, (h, t, negs) in enumerate(tasks):
        pos[i] = float(train_degree[t])
        neg[i, :] = train_degree[negs]
    return _dm_metrics_from_scores(pos, neg)


def eval_adamic_adar_arm(split, tasks):
    """Non-learned structural heuristic. AA(h,c) = sum_{z in ctxN(h) ∩ trainN(c)} 1/log(1+deg(z)).
    ctxN(h) = h's CONTEXT neighbours (train); trainN(c) = c's train adjacency. THE structural bar."""
    train_degree = split["train_degree"]
    train_adj = split["train_adj"]
    ctx_neigh_all = split["ctx_neigh_all"]
    # precompute per-concept context-neighbour weight dicts
    ctx_w = {}
    for (h, t, negs) in tasks:
        if h not in ctx_w:
            w = {}
            for z in ctx_neigh_all[h].keys():
                dz = train_degree[z]
                w[z] = 1.0 / math.log(dz + 1.0 + 1e-9) if dz > 1.0 else 1.0
            ctx_w[h] = w

    def aa(h, c):
        w = ctx_w[h]
        if not w:
            return 0.0
        adj = train_adj[c]
        # iterate the smaller set
        if len(w) <= len(adj):
            return float(sum(wz for z, wz in w.items() if z in adj))
        return float(sum(w[z] for z in adj if z in w))

    T = len(tasks)
    M = tasks[0][2].shape[0]
    pos = np.empty(T, dtype=np.float64)
    neg = np.empty((T, M), dtype=np.float64)
    for i, (h, t, negs) in enumerate(tasks):
        pos[i] = aa(h, t)
        neg[i, :] = [aa(h, int(c)) for c in negs.tolist()]
    return _dm_metrics_from_scores(pos, neg)


# ---------------------------------------------------------------------------
# Full-candidate AUC (v1-comparable; exposes the popularity confound directly)
# ---------------------------------------------------------------------------
def eval_full_candidate_auc(score_matrix_fn, split):
    """Rank ALL train concepts. score_matrix_fn(h)->[T] over train rows. Returns mean rank-AUC."""
    train_idx = split["train_idx"].astype(np.int64)
    T = train_idx.shape[0]
    row_of = {int(t): r for r, t in enumerate(train_idx.tolist())}
    eval_held = split["eval_held"].tolist()
    held_eval_pos = split["held_eval_pos"]
    aucs = []
    for h in eval_held:
        pos_rows = [row_of[t] for t in held_eval_pos[h] if t in row_of]
        pos_rows = sorted(set(pos_rows))
        if len(pos_rows) == 0 or len(pos_rows) >= T:
            continue
        score = score_matrix_fn(h)
        pos_mask = np.zeros(T, dtype=bool)
        pos_mask[pos_rows] = True
        n_pos = int(pos_mask.sum())
        n_neg = T - n_pos
        order = np.argsort(score, kind="mergesort")
        ranks = np.empty(T, dtype=np.float64)
        ranks[order] = np.arange(1, T + 1)
        auc = (ranks[pos_mask].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
        aucs.append(float(auc))
    return float(np.mean(aucs)) if aucs else float("nan")


def _emb_digest(emb):
    return hashlib.sha256(np.ascontiguousarray(emb.astype(np.float32)).tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# One seed: build codes for every arm + degree-matched evaluate
# ---------------------------------------------------------------------------
def run_seed(seed, data, split, cfg, tasks):
    feats = split["feats"]
    feats_ground = split["feats_ground"]
    K = data["K"]
    pool = split["train_anchor_pool"]
    tnl = split["target_neigh_list"]
    train_idx = split["train_idx"]
    train_degree = split["train_degree"]

    arm_codes = {}
    arm_metrics = {}

    # PRIMARY: context encoder
    enc = train_encoder(feats, tnl, pool, cfg, seed)
    arm_codes[PRIMARY_ARM] = encode_all(enc, feats)

    # GROUNDING_ONLY: v1-style encoder on grounding features (context zeroed)
    enc_g = train_encoder(feats_ground, tnl, pool, cfg, seed + 33)
    arm_codes[GROUND_ARM] = encode_all(enc_g, feats_ground)

    # RAW_CONTEXT: no encoder; L2-normalized raw combined input
    arm_codes[RAW_ARM] = _l2(torch.from_numpy(feats.astype(np.float32))).numpy().astype(np.float32)

    # INPUT_SHUFFLE: permute the full input rows across concept ids, then train
    perm = np.random.default_rng(seed + 909).permutation(K)
    feats_shuf = feats[perm]
    enc_shuf = train_encoder(feats_shuf, tnl, pool, cfg, seed + 1)
    arm_codes[SHUFFLE_ARM] = encode_all(enc_shuf, feats_shuf)

    # LOOKUP_RECALL: transductive table; held-out rows -> independent random unit codes
    lut = train_lookup_table(K, pool, tnl, cfg, seed)
    lut_codes = lut.copy()
    held_rows = np.nonzero(~split["is_train"])[0]
    rc = np.random.default_rng(seed + 303).standard_normal((held_rows.shape[0], cfg["code_dim"]))
    rc = rc / (np.linalg.norm(rc, axis=1, keepdims=True) + 1e-8)
    lut_codes[held_rows] = rc.astype(np.float32)
    arm_codes[LOOKUP_ARM] = lut_codes.astype(np.float32)

    # ---- degree-matched eval per code arm ----
    for arm in CODE_ARMS:
        ev = eval_code_arm(arm_codes[arm], tasks)
        ev["emb_digest"] = _emb_digest(arm_codes[arm])
        arm_metrics[arm] = ev
        _log("seed=%d arm=%s dm_auc=%.4f dm_recall@1=%.4f dm_mrr=%.4f (tasks=%d)"
             % (seed, arm, ev["dm_auc"], ev["dm_recall_at_1"], ev["dm_mrr"], ev["n_tasks"]))

    # POPULARITY (degree-matched -> ~0.5 by construction)
    ev = eval_popularity_arm(train_degree, tasks)
    ev["emb_digest"] = hashlib.sha256(train_degree.tobytes()).hexdigest()
    arm_metrics[POP_ARM] = ev
    _log("seed=%d arm=%s dm_auc=%.4f dm_recall@1=%.4f dm_mrr=%.4f (tasks=%d)"
         % (seed, POP_ARM, ev["dm_auc"], ev["dm_recall_at_1"], ev["dm_mrr"], ev["n_tasks"]))

    # STRUCT (Adamic-Adar; degree-matched)
    ev = eval_adamic_adar_arm(split, tasks)
    ev["emb_digest"] = "aa_structural_heuristic"
    arm_metrics[STRUCT_ARM] = ev
    _log("seed=%d arm=%s dm_auc=%.4f dm_recall@1=%.4f dm_mrr=%.4f (tasks=%d)"
         % (seed, STRUCT_ARM, ev["dm_auc"], ev["dm_recall_at_1"], ev["dm_mrr"], ev["n_tasks"]))

    # ---- full-candidate AUC (v1-comparable) for a few key arms: exposes the confound ----
    row_train = train_idx.astype(np.int64)

    def code_score_fn(codes):
        Ztr = codes[row_train]
        return lambda h: (Ztr @ codes[h]).astype(np.float64)

    pop_vec = train_degree[row_train].astype(np.float64)
    full_auc = dict(
        context_encoder=eval_full_candidate_auc(code_score_fn(arm_codes[PRIMARY_ARM]), split),
        grounding_only=eval_full_candidate_auc(code_score_fn(arm_codes[GROUND_ARM]), split),
        popularity=eval_full_candidate_auc(lambda h: pop_vec, split),
    )
    for a in arm_metrics:
        arm_metrics[a]["full_auc"] = full_auc.get(
            {PRIMARY_ARM: "context_encoder", GROUND_ARM: "grounding_only",
             POP_ARM: "popularity"}.get(a, "_na"), None)
    _log("seed=%d FULL-CANDIDATE AUC context_enc=%.4f grounding_only=%.4f popularity=%.4f"
         % (seed, full_auc["context_encoder"], full_auc["grounding_only"], full_auc["popularity"]))

    # ARMS-MUST-DIFFER (META_RULE_AF) over the code arms
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
            dm_auc_mean=float(series(arm, "dm_auc").mean()),
            dm_auc_min=float(series(arm, "dm_auc").min()),
            dm_recall_at_1_mean=float(series(arm, "dm_recall_at_1").mean()),
            dm_recall_at_5_mean=float(series(arm, "dm_recall_at_5").mean()),
            dm_mrr_mean=float(series(arm, "dm_mrr").mean()),
            n_seeds=len(per_seed),
        )
        fa = [m[arm].get("full_auc") for m in per_seed if m[arm].get("full_auc") is not None]
        agg[arm]["full_auc_mean"] = float(np.mean(fa)) if fa else None

    enc = agg[PRIMARY_ARM]["dm_auc_mean"]
    ground = agg[GROUND_ARM]["dm_auc_mean"]
    raw = agg[RAW_ARM]["dm_auc_mean"]
    pop = agg[POP_ARM]["dm_auc_mean"]
    struct = agg[STRUCT_ARM]["dm_auc_mean"]
    shuf = agg[SHUFFLE_ARM]["dm_auc_mean"]
    look = agg[LOOKUP_ARM]["dm_auc_mean"]

    cb_lo, cb_hi = COLLAPSE_BAND
    pm_lo, pm_hi = POP_MATCH_BAND
    collapse_ok = bool(cb_lo <= shuf <= cb_hi and cb_lo <= look <= cb_hi)
    pop_match_ok = bool(pm_lo <= pop <= pm_hi)
    can_fail_fired = bool(collapse_ok and pop_match_ok)

    margin_struct = enc - struct
    margin_pop = enc - pop

    # Mission bar = beat BOTH degree-matched popularity AND the structural heuristic (Adamic-Adar)
    # -> proves learned meaning adds value beyond pure degree AND beyond raw graph proximity.
    if (enc >= HP_AUC and margin_struct >= HP_MARGIN_OVER_STRUCT
            and margin_pop >= HP_MARGIN_OVER_POP and can_fail_fired):
        verdict = "HARD_PASS"
    elif ((not can_fail_fired) or (enc < HF_AUC) or (margin_pop < 0.02)):
        # controls broken (matching/collapse) OR at chance OR fails to even beat degree-matched popularity
        verdict = "HARD_FAIL"
    else:
        # beats degree-matched popularity + collapse controls, but does NOT clear the structural bar:
        # weak-but-real signal beyond degree (the honest partial win)
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | CONTEXT_ENCODER dm_auc=%.4f (min=%.4f, dm_recall@1=%.4f dm_mrr=%.4f) | "
        "grounding_only=%.4f raw_context=%.4f | "
        "STRUCT_ADAMIC_ADAR=%.4f (enc-struct=%+.4f) | POP_degmatched=%.4f (enc-pop=%+.4f) | "
        "COLLAPSE input_shuffle=%.4f lookup=%.4f -> collapse_ok=%s pop_match_ok=%s | "
        "FULL-CAND AUC enc=%.4f pop=%.4f (confound witness) | "
        "train=%d heldout_eval=%d tasks_per_seed~%d | K=%d pairs=%d rels=%d"
        % (verdict, enc, agg[PRIMARY_ARM]["dm_auc_min"],
           agg[PRIMARY_ARM]["dm_recall_at_1_mean"], agg[PRIMARY_ARM]["dm_mrr_mean"],
           ground, raw, struct, margin_struct, pop, margin_pop, shuf, look,
           collapse_ok, pop_match_ok,
           (agg[PRIMARY_ARM]["full_auc_mean"] or float("nan")),
           (agg[POP_ARM]["full_auc_mean"] or float("nan")),
           split_meta["n_train"], split_meta["n_eval_heldout"],
           per_seed[0][PRIMARY_ARM]["n_tasks"],
           data_meta["n_kept_concepts"], data_meta["n_kept_pairs"], data_meta["n_rel_slots"]))

    gates = dict(
        encoder_dm_auc=enc, encoder_dm_auc_min=agg[PRIMARY_ARM]["dm_auc_min"],
        grounding_only_dm_auc=ground, raw_context_dm_auc=raw,
        struct_adamic_adar_dm_auc=struct, popularity_dm_auc=pop,
        input_shuffle_dm_auc=shuf, lookup_dm_auc=look,
        margin_over_struct=margin_struct, margin_over_popularity=margin_pop,
        collapse_ok=collapse_ok, pop_match_ok=pop_match_ok, can_fail_fired=can_fail_fired,
        collapse_band=list(COLLAPSE_BAND), pop_match_band=list(POP_MATCH_BAND),
        hp_auc=HP_AUC, hf_auc=HF_AUC,
        hp_margin_over_struct=HP_MARGIN_OVER_STRUCT, hp_margin_over_pop=HP_MARGIN_OVER_POP,
        full_candidate_auc_encoder=agg[PRIMARY_ARM]["full_auc_mean"],
        full_candidate_auc_popularity=agg[POP_ARM]["full_auc_mean"],
    )
    return verdict, verdict_msg, agg, gates


# ---------------------------------------------------------------------------
# Discriminator self-test: proves the degree-matched metric is telemetry-sensitive
# ---------------------------------------------------------------------------
def discriminator_selftest():
    """Planted-neighbourhood synthetic. Structured codes -> dm_auc high; random codes -> ~0.5;
    a degree score on degree-matched tasks -> ~0.5 (validates degree-matching neutralizes popularity)."""
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

    # synthetic degree with NO relation to block (so degree-matched neutralizes it)
    degree = rng.integers(1, 64, size=K).astype(np.float64)

    heldout = np.array([i % 5 == 0 for i in range(K)], dtype=bool)
    train_rows = np.nonzero(~heldout)[0].tolist()
    eval_h = np.nonzero(heldout)[0].tolist()

    # build degree-matched tasks: pos = same-block train concept, negs = same-degree-bucket train
    buckets = {}
    for c in train_rows:
        buckets.setdefault(_deg_bucket(degree[c]), []).append(c)
    r2 = np.random.default_rng(1)
    tasks = []
    for h in eval_h:
        same = [t for t in train_rows if block[t] == block[h]]
        if not same:
            continue
        for t in same[:4]:
            b = _deg_bucket(degree[t])
            cand = [c for c in buckets.get(b, []) if c != t and block[c] != block[h]]
            if len(cand) < 8:
                for w in (1, 2, 3):
                    cand = []
                    for bb in range(b - w, b + w + 1):
                        cand.extend([c for c in buckets.get(bb, []) if c != t and block[c] != block[h]])
                    if len(cand) >= 8:
                        break
            if len(cand) < 4:
                continue
            negs = r2.choice(np.array(sorted(set(cand)), dtype=np.int64),
                             size=min(12, len(set(cand))), replace=False)
            tasks.append((h, t, negs.astype(np.int64)))

    ev_struct = eval_code_arm(codes, tasks)
    ev_rand = eval_code_arm(rand_codes, tasks)
    ev_pop = eval_popularity_arm(degree, tasks)
    res = dict(dm_auc_struct=ev_struct["dm_auc"], dm_auc_rand=ev_rand["dm_auc"],
               dm_auc_pop_degmatched=ev_pop["dm_auc"], n_tasks=len(tasks))
    ok = (ev_struct["dm_auc"] >= 0.72
          and abs(ev_rand["dm_auc"] - 0.5) < 0.10
          and abs(ev_pop["dm_auc"] - 0.5) < 0.12)
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

    st_ok, st_res = discriminator_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED (degree-matched metric not telemetry-sensitive): %s" % st_res,
            summary="discriminator selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res))
        raise SystemExit(1)

    _log("loading grounded subgraph (min_deg=%d cap=%d top_rel=%d)..."
         % (cfg["min_deg"], cfg["cap_nodes"], cfg["top_rel"]))
    data = load_grounded_subgraph(cfg)
    _log("grounded universe: %s" % {k: v for k, v in data["meta"].items() if k != "top_rels"})
    _log("top_rels: %s" % data["meta"]["top_rels"])
    split = build_split_and_features(data, cfg)
    _log("split: %s" % split["split_meta"])
    tasks, task_diag = build_eval_tasks(split, cfg)
    _log("degree-matched eval tasks=%d dropped=%d frac_retained=%.3f mean_abs_delta=%.2f "
         "deg_kept_median=%.1f deg_kept_max=%d"
         % (len(tasks), task_diag["n_dropped"], task_diag["frac_retained"],
            task_diag["mean_abs_delta"], task_diag["deg_kept_median"], task_diag["deg_kept_max"]))

    if run_mode == "self_test":
        pm = run_seed(cfg["seeds"][0], data, split, cfg, tasks)
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS discriminator + end-to-end degree-matched held-out eval exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, data_meta=data["meta"], split_meta=split["split_meta"],
            encoder_dm_auc=pm[PRIMARY_ARM]["dm_auc"], struct_dm_auc=pm[STRUCT_ARM]["dm_auc"],
            pop_dm_auc=pm[POP_ARM]["dm_auc"], shuffle_dm_auc=pm[SHUFFLE_ARM]["dm_auc"],
            lookup_dm_auc=pm[LOOKUP_ARM]["dm_auc"]))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, data, split, cfg, tasks)
            per_seed.append(pm)
            write_partial(out_dir_path, seed, dict(seed=seed, arms=pm, run_mode=run_mode))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
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
        n_seeds=len(per_seed), seeds=cfg["seeds"],
        config={k: v for k, v in cfg.items()},
        data_meta={k: v for k, v in data["meta"].items()},
        split_meta=split["split_meta"],
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
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
