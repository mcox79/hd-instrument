"""R1 LANDMARK-ANCHORED GRADED-GEOMETRY teacher-free concept encoder, judged on WORDNET
SEMANTIC-NEIGHBOURHOOD generalization to HELD-OUT NEW concepts.

A CONSIDERED PIVOT off the v1->v2->v3 link-prediction encoder arc (which plateaued: raw grounding
carried the modest novel-concept signal; the learned objective added only ~+0.043 over raw grounding and
v3's mechanism regressed; the "beats structure" headline was a construction artifact). Here we CHANGE
BOTH the OBJECTIVE and the TEST:

OBJECTIVE (R1 graded-geometry, teacher-free) -- from encoder_rescue_plan_converged_diagnosis_2026-07-04
and THE_PLAN_learned_grounded_representation_foundation_2026-07-26 ("R1 = global/landmark objective to
form graded geometry at scale"):
  Form a semantic manifold where concept-to-concept distances are GRADED by shared-vs-distinct RELATIONAL
  structure. LANDMARK-ANCHORED relational KD: match each concept's code-vs-landmark-code cosine profile to
  a FIXED anchor frame of ~L landmark (top-degree TRAIN) concepts, where the TARGET geometry is the
  concepts' OWN RELATIONAL-GRAPH overlap in the foundation -- T[c,l] = cosine of train-neighbour indicator
  vectors = |N(c) INTERSECT N(l)| / sqrt(|N(c)||N(l)|) -- NOT a borrowed vector. The encoder input is
  GROUNDING; it learns to map grounding into a geometry aligned with relational structure (a signal raw
  grounding cosine does NOT directly expose). This is the fair test of "does learning add over raw
  grounding": PRIMARY (learned) and RAW_GROUNDING share the SAME grounding input, differing only by the
  learned relational-alignment. It supervises graded geometry independent of random in-batch co-occurrence
  (the diagnosed failure of in-batch contrastive link-prediction at scale, encoder_rescue R1).

TEST (WordNet semantic-neighbourhood on HELD-OUT NEW concepts) -- an INDEPENDENT semantic structure as
ground truth: the WordNet dominant-synset LEXNAME (supersense, e.g. noun.animal / noun.artifact /
noun.food; 45 classes) of each concept, from NLTK WordNet. This truth is NEVER seen during training and is
INDEPENDENT of the ConceptNet/ATOMIC relational edges used as input (commonsense relations, not taxonomy).
For each held-out NEW concept placed inductively from its features, does its learned code land near its
true semantic neighbours / recover its category?
  Primary metric: SAME-LEXNAME AUC = for each held-out query, rank the TRAIN gallery by code-cosine;
  AUC = P(a same-lexname gallery concept ranks above a different-lexname one). Base = 0.5 exactly (class-
  balance-independent). Secondary: precision@10, recall@1, + the category base-rate (random-retrieval floor).

THE ONE NUMBER THAT MATTERS (Director contract): does LEARNING add a REAL margin OVER RAW GROUNDING on
held-out-NEW concepts (grow the +0.043)? margin = AUC(LEARNED) - AUC(RAW_GROUNDING). If learning still
adds ~nothing, that is an HONEST, important finding (points to an INPUT-CEILING, not an objective tweak) --
reported plainly as MIDDLE_BAND with the per-item WHY.

HARD INVARIANTS (project locks):
  - TEACHER-FREE: NO GloVe/BGE/transformer/borrowed vector anywhere (teacher/target/init/feature). Inputs
    are ONLY measured grounding norms + the foundation's own relational graph. The target geometry is the
    concepts' own property/relational overlap. WordNet lexname is EVAL-ONLY ground truth, never an input
    nor a training target.
  - INDUCTIVE: a held-out NEW concept is PLACED from its features (grounding + its known train-neighbour
    context) -> code, never a learned per-concept lookup. Held-out is never a landmark nor a train anchor.
  - LEAK-PROOF held-out-NEW: concept-level held-out split (sha256 on id). Held-out concepts are never in
    landmark selection, never training anchors; the WordNet truth is disjoint from every input/target.

ARMS (all scored by the SAME same-lexname metric over a codes matrix; gallery = train, query = held-out):
  ARM_LEARNED              : R1 landmark-geometry encoder; GROUNDING-ONLY input (same input as        [PRIMARY]
                             RAW_GROUNDING -> the margin isolates learning), blended property+relational target.
  ARM_LEARNED_RICH         : R1 landmark-geometry encoder; grounding+ctx input, same target. [does richer input help learning?]
  ARM_RAW_GROUNDING        : cosine over raw standardized grounding (20d), NO learning.  [THE contract baseline;
                             the margin that matters = LEARNED - this]
  ARM_RAW_GROUND_PLUS_CTX  : cosine over raw [grounding ++ context], NO learning.        [decompose: is any
                             margin from the richer INPUT vs the LEARNING?]
  ARM_RANDOM_INIT          : untrained encoder (random weights), grounding input.        [isolate learning
                             from architecture]
  ARM_COLLAPSE_SHUFFLE     : grounding input rows permuted across ids, then trained.     [COLLAPSE / leak witness ~0.5]

CAN-FAIL GATE: ARM_COLLAPSE_SHUFFLE must sit ~0.5 (else the metric is saturated / leaking). category
base-rate reported as the random-retrieval floor. DEFLATE: if LEARNED only ties RAW_GROUNDING, that is the
honest input-ceiling finding -> MIDDLE_BAND, said plainly.

CPU-only. No GPU. No network at run time (WordNet from local NLTK data; lexnames cached to disk). ASCII-only.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test over code arms)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator has base=0.5 exactly; collapse+random-init controls witness the floor
# - baseline_in_band at smoke: collapse control ~0.5; raw-grounding must be a real >0.5 signal (measured)
# - discriminator survives scale: smoke IS a genuine held-out-new-concept WordNet-neighbourhood test
# - HARD_PASS strictly above floor: learned_auc>=0.60 AND (learned-raw_grounding)>=0.03 AND margin_min>0
#   AND learned>=random_init AND can_fail
# - HP_SCOPE: gates apply to ARM_LEARNED (primary) only
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; controls witness it empirically)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg
# - deterministic seeding: sha256 concept split + fixed int seeds + sorted(); no hash()/list(set()) (PROT-023)
# - no substrate KGStore/fit objects (self-contained jsonl reader + NLTK) -> F.1/F.2 real_code_path N/A
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

ANCHOR_NAME = "grounded_r1_landmark_geometry_wordnet_neighbourhood_v1"
FOUNDATION_DIR = os.path.join(_REPO, "data", "cskg_foundation_v1")
NODES_PATH = os.path.join(FOUNDATION_DIR, "nodes.jsonl")
EDGES_GLOB = os.path.join(FOUNDATION_DIR, "edges_shard_*.jsonl")
LEXNAME_CACHE = os.path.join(_REPO, "data", "wordnet_lexname_cache_v1.json")

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
    min_deg=2, cap_nodes=400, seeds=[7], epochs=25, batch=128,
    code_dim=32, hidden=64, lr=5e-3, n_landmarks=64, n_land_batch=48, n_anchor_batch=96,
    lambda_var=1.0, heldout_frac=0.2, top_rel=8, ctx_min_neigh=1,
)
SMOKE_CFG = dict(
    min_deg=2, cap_nodes=2500, seeds=[7, 13], epochs=140, batch=256,
    code_dim=128, hidden=256, lr=3e-3, n_landmarks=256, n_land_batch=128, n_anchor_batch=256,
    lambda_var=1.0, heldout_frac=0.2, top_rel=16, ctx_min_neigh=1,
)
FULL_CFG = dict(
    min_deg=2, cap_nodes=5000, seeds=[7, 13, 17], epochs=180, batch=256,
    code_dim=128, hidden=256, lr=2.5e-3, n_landmarks=512, n_land_batch=192, n_anchor_batch=256,
    lambda_var=1.0, heldout_frac=0.2, top_rel=16, ctx_min_neigh=1,
)

# Deterministic salts / seeds
CONCEPT_SPLIT_SALT = "r1lg_wn_v1_concept_split::"
EVAL_SEED = 20260726

# Pre-reg bands (applied to ARM_LEARNED primary held-out SAME-LEXNAME AUC).
HP_LEARNED_SIGNAL = 0.60         # LEARNED must be a genuine held-out signal well above chance 0.5
HF_AUC = 0.53                    # below this = essentially chance = HARD_FAIL
HP_MARGIN_OVER_RAW = 0.03        # THE NUMBER: LEARNED - RAW_GROUNDING must exceed this (grow the +0.043)
COLLAPSE_BAND = (0.44, 0.56)     # ARM_COLLAPSE_SHUFFLE MUST sit here (can-fail witness)
MIN_QUERY_TASKS = 150            # power floor for the held-out AUC to be trustworthy

PRIMARY_ARM = "ARM_LEARNED"            # grounding-only input, relational-graph target geometry
LEARNED_RICH_ARM = "ARM_LEARNED_RICH"  # grounding+ctx input, same relational target
RAW_ARM = "ARM_RAW_GROUNDING"          # grounding cosine, NO learning (THE contract contrast; same input as PRIMARY)
RAWCTX_ARM = "ARM_RAW_GROUND_PLUS_CTX" # grounding+ctx cosine, NO learning
RANDINIT_ARM = "ARM_RANDOM_INIT"       # untrained encoder on grounding input
SHUFFLE_ARM = "ARM_COLLAPSE_SHUFFLE"   # grounding rows permuted across ids, trained -> ~0.5
ALL_ARMS = [PRIMARY_ARM, LEARNED_RICH_ARM, RAW_ARM, RAWCTX_ARM, RANDINIT_ARM, SHUFFLE_ARM]


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
# Deterministic held-out split (sha256; PYTHONHASHSEED-independent)
# ---------------------------------------------------------------------------
def _concept_is_heldout(concept_id, heldout_frac):
    h = hashlib.sha256((CONCEPT_SPLIT_SALT + concept_id).encode("utf-8")).digest()
    r = int.from_bytes(h[:8], "big") / float(2 ** 64)
    return r < heldout_frac


# ---------------------------------------------------------------------------
# WordNet lexname (supersense) EVAL-ONLY ground truth
# ---------------------------------------------------------------------------
def _build_lexname_map(surfaces):
    """surfaces: list[str]. Return {surface: lexname or None}. Cached to disk (idempotent).
    Dominant (first) synset lexname; try surface underscored, collapsed, first-token. NLTK-local only."""
    cache = {}
    if os.path.exists(LEXNAME_CACHE):
        try:
            with open(LEXNAME_CACHE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except (ValueError, OSError):
            cache = {}
    need = [s for s in surfaces if s not in cache]
    if need:
        try:
            from nltk.corpus import wordnet as wn
        except ImportError as e:
            raise RuntimeError("NLTK WordNet required for the EVAL-ONLY semantic-truth "
                               "(lexname). Install nltk + wordnet data.") from e
        for s in need:
            lx = None
            for cand in (s.replace(" ", "_"), s.replace(" ", ""), s.split(" ")[0]):
                if not cand:
                    continue
                try:
                    ss = wn.synsets(cand)
                except Exception:  # noqa: BLE001 -- NLTK lookup hiccup on a single token: record None, continue
                    ss = []
                if ss:
                    lx = ss[0].lexname()
                    break
            cache[s] = lx
        tmp = LEXNAME_CACHE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cache, f)
        os.replace(tmp, LEXNAME_CACHE)
    return {s: cache.get(s) for s in surfaces}


# ---------------------------------------------------------------------------
# Foundation loader: grounded induced subgraph WITH relation types + lexname truth
# ---------------------------------------------------------------------------
def _grounding_vector(gd):
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
    """Load grounded concepts WITH a WordNet lexname + induced relational subgraph. Returns arrays."""
    if not os.path.exists(NODES_PATH):
        raise FileNotFoundError("nodes.jsonl not found at %s" % NODES_PATH)

    gid_list, surf_list, raw_vals, raw_gpres = [], [], [], []
    with open(NODES_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            gd = d.get("grounding")
            if not gd:
                continue
            vals, gpres = _grounding_vector(gd)
            gid_list.append(d["id"])
            surf_list.append(d.get("surface", d["id"]))
            raw_vals.append(vals)
            raw_gpres.append(gpres)
    if len(gid_list) < 100:
        raise RuntimeError("too few grounded nodes (%d)" % len(gid_list))

    # EVAL-ONLY WordNet lexname truth; keep ONLY concepts with a lexname (98.5% of grounded).
    lexmap = _build_lexname_map(surf_list)
    has_lex = [i for i in range(len(gid_list)) if lexmap[surf_list[i]] is not None]
    if len(has_lex) < 100:
        raise RuntimeError("too few grounded nodes with a WordNet lexname (%d)" % len(has_lex))

    gid_list = [gid_list[i] for i in has_lex]
    surf_list = [surf_list[i] for i in has_lex]
    raw_vals = [raw_vals[i] for i in has_lex]
    raw_gpres = [raw_gpres[i] for i in has_lex]
    lex_list = [lexmap[s] for s in surf_list]

    gid_set = set(gid_list)
    idx_of = {c: i for i, c in enumerate(gid_list)}

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
    surfaces = [surf_list[o] for o in kept]
    lexnames = [lex_list[o] for o in kept]
    vals = np.stack([raw_vals[o] for o in kept], axis=0)
    gpres = np.stack([raw_gpres[o] for o in kept], axis=0)

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

    rel_sorted = sorted(rel_freq.items(), key=lambda kv: (-kv[1], kv[0]))
    top_rels = [r for r, _ in rel_sorted[:cfg["top_rel"]]]
    rel_id = {r: i for i, r in enumerate(top_rels)}
    R = len(top_rels) + 1
    other_id = R - 1

    def _rel_slot(r):
        return rel_id.get(r, other_id)

    # lexname -> integer label
    uniq_lex = sorted(set(lexnames))
    lex_to_int = {lx: i for i, lx in enumerate(uniq_lex)}
    lex_labels = np.array([lex_to_int[lx] for lx in lexnames], dtype=np.int64)

    meta = dict(
        n_grounded_total=n_all, n_induced_pairs_total=len(pair_rels),
        n_kept_concepts=K, n_kept_pairs=len(kept_pair_rels),
        min_deg=cfg["min_deg"], cap_nodes=cfg["cap_nodes"],
        top_rels=top_rels, n_rel_slots=R,
        n_lexnames=len(uniq_lex),
    )
    return dict(ids=ids, surfaces=surfaces, vals=vals, gpres=gpres,
                pair_rels=kept_pair_rels, K=K, R=R, rel_slot=_rel_slot,
                lex_labels=lex_labels, uniq_lex=uniq_lex, meta=meta)


# ---------------------------------------------------------------------------
# Split + standardize + typed TRAIN-neighbour context aggregation
# ---------------------------------------------------------------------------
def build_split(data, cfg):
    ids = data["ids"]
    K = data["K"]
    R = data["R"]
    rel_slot = data["rel_slot"]
    heldout = np.array([_concept_is_heldout(c, cfg["heldout_frac"]) for c in ids], dtype=bool)
    is_train = ~heldout
    train_idx = np.nonzero(is_train)[0]
    held_idx = np.nonzero(heldout)[0]
    if train_idx.shape[0] < 80 or held_idx.shape[0] < 40:
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
    z = np.where(np.isnan(z), 0.0, z).astype(np.float64)
    own_feat = np.concatenate([z, data["gpres"]], axis=1).astype(np.float64)   # [K,20]

    # typed TRAIN-neighbour sets (a concept's neighbours restricted to TRAIN concepts -> inductive input)
    ctx_nei_by_rel = [dict() for _ in range(K)]    # concept -> {rel_slot: set(train j)}
    train_deg = np.zeros(K, dtype=np.float64)
    for (a, b), rels in data["pair_rels"].items():
        if b in train_set:
            for r in rels:
                ctx_nei_by_rel[a].setdefault(rel_slot(r), set()).add(b)
        if a in train_set:
            for r in rels:
                ctx_nei_by_rel[b].setdefault(rel_slot(r), set()).add(a)
        if (a in train_set) and (b in train_set):
            train_deg[a] += 1
            train_deg[b] += 1

    split_meta = dict(
        n_train=int(train_idx.shape[0]), n_heldout=int(held_idx.shape[0]),
        mean_train_ctx_neigh=float(np.mean([sum(len(v) for v in ctx_nei_by_rel[i].values())
                                            for i in train_idx.tolist()])),
        mean_held_ctx_neigh=float(np.mean([sum(len(v) for v in ctx_nei_by_rel[i].values())
                                           for i in held_idx.tolist()])),
        n_rel_slots=R,
    )
    return dict(own_feat=own_feat, is_train=is_train, K=K, R=R,
                train_idx=train_idx, held_idx=held_idx, train_deg=train_deg,
                ctx_nei_by_rel=ctx_nei_by_rel, split_meta=split_meta)


def _pooled_ctx_block(split, per_source, block_dim):
    """[K, R*(block_dim+2)] typed context block: per rel slot, MEAN of per_source over the concept's TRAIN
    neighbours in that slot + presence bit + log-count."""
    K = split["K"]
    R = split["R"]
    ctx_nei_by_rel = split["ctx_nei_by_rel"]
    per_rel = block_dim + 2
    out = np.zeros((K, R * per_rel), dtype=np.float64)
    ps = per_source.astype(np.float64)
    for i in range(K):
        for s in range(R):
            neigh = ctx_nei_by_rel[i].get(s)
            off = s * per_rel
            if neigh:
                nj = np.fromiter(sorted(neigh), dtype=np.int64, count=len(neigh))
                out[i, off:off + block_dim] = ps[nj].mean(axis=0)
                out[i, off + block_dim] = 1.0
                out[i, off + block_dim + 1] = math.log1p(len(neigh))
    return out


def build_features(split):
    """Return raw feature matrices used by every arm (encoder input + raw baselines + target geometry)."""
    own = split["own_feat"]                                   # [K,20]
    ctx = _pooled_ctx_block(split, own, GROUND_DIM)           # [K, R*22]
    rich = np.concatenate([own, ctx], axis=1)                 # [K, 20 + R*22]
    return dict(own=own.astype(np.float32), rich=rich.astype(np.float32))


# ---------------------------------------------------------------------------
# Encoder + R1 landmark-anchored graded-geometry objective (teacher-free)
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


def _l2_np(x, eps=1e-8):
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + eps)


def _l2_t(h, eps=1e-8):
    return h / (h.norm(dim=1, keepdim=True) + eps)


def select_landmarks(split, cfg):
    """Deterministic anchor frame: stratified by lexname is not available here (labels are eval-only), so
    use TRAIN concepts with the highest train-degree (dense, well-grounded, span the manifold). Landmarks
    are TRAIN-ONLY (held-out never a landmark)."""
    train_idx = split["train_idx"].tolist()
    train_deg = split["train_deg"]
    ranked = sorted(train_idx, key=lambda i: (-float(train_deg[i]), i))
    L = min(cfg["n_landmarks"], len(ranked))
    return np.array(sorted(ranked[:L]), dtype=np.int64)


def build_train_adjacency(split):
    """Binary TRAIN-neighbour adjacency A[K, K] (float32): A[c, j] = 1 if train-concept j is a neighbour of
    c (via ctx_nei_by_rel, which is already train-restricted). Teacher-free (the foundation's own graph)."""
    K = split["K"]
    ctx_nei_by_rel = split["ctx_nei_by_rel"]
    A = np.zeros((K, K), dtype=np.float32)
    for i in range(K):
        for s, neigh in ctx_nei_by_rel[i].items():
            for j in neigh:
                A[i, j] = 1.0
    return A


def _zscore_matrix(M):
    mu = float(M.mean())
    sd = float(M.std()) + 1e-6
    return (M - mu) / sd


def compute_target_geometry(own_norm, A, landmarks, alpha=0.5):
    """Teacher-free TARGET geometry graded by shared-vs-distinct PROPERTY + RELATIONAL overlap (contract):
      G[c,l] = cosine(grounding_c, grounding_l)                         (property overlap)
      R[c,l] = |N(c) INT N(l)| / sqrt(|N(c)||N(l)|)                     (relational-graph overlap)
      T = alpha * z(G) + (1-alpha) * z(R)   (each z-scored so neither dominates by scale)
    Both derived from the concepts' OWN grounding + the foundation's OWN graph, NO borrowed vector. The
    property term keeps the geometry grounding-consistent; the relational term is the extra teacher-free
    structure the encoder must PREDICT from its input (a signal raw grounding cosine does not expose).
    Returns [K, L]."""
    Lm_own = own_norm[landmarks]                      # [L, D]
    G = own_norm @ Lm_own.T                           # [K, L] grounding cosine in [-1,1]
    Lm_A = A[landmarks]                               # [L, K]
    shared = A @ Lm_A.T                               # [K, L] shared-neighbour counts
    deg = np.sqrt((A * A).sum(axis=1) + 1e-6)         # [K]
    deg_l = deg[landmarks]                            # [L]
    R = shared / (deg[:, None] * deg_l[None, :] + 1e-6)
    T = alpha * _zscore_matrix(G) + (1.0 - alpha) * _zscore_matrix(R)
    return T.astype(np.float32)                        # [K, L]


def train_landmark_encoder(feats, target_geo, landmarks, train_idx, cfg, seed, do_train=True):
    """R1: match each TRAIN anchor's code-vs-landmark-code cosine profile to the fixed teacher-free target
    geometry. Relational-KD: minimize row-centered smooth-L1(S, T) + a VICReg variance term (anti-collapse).
    do_train=False returns the random-init encoder (ARM_RANDOM_INIT)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    X = torch.from_numpy(feats.astype(np.float32))
    enc = Encoder(feats.shape[1], cfg["hidden"], cfg["code_dim"])
    if not do_train:
        enc.eval()
        return enc
    opt = torch.optim.Adam(enc.parameters(), lr=cfg["lr"])
    rng = np.random.default_rng(seed + 17)
    Lm_all = torch.from_numpy(landmarks.astype(np.int64))
    T_all = torch.from_numpy(target_geo.astype(np.float32))    # [K, L]
    anchors = np.asarray(train_idx, dtype=np.int64)
    nL = landmarks.shape[0]
    log_every = max(1, cfg["epochs"] // 5)
    t0 = time.perf_counter()
    for ep in range(cfg["epochs"]):
        a_bs = min(cfg["n_anchor_batch"], anchors.shape[0])
        l_bs = min(cfg["n_land_batch"], nL)
        a_idx = rng.choice(anchors, size=a_bs, replace=False)
        l_sel = rng.choice(nL, size=l_bs, replace=False)
        l_rows = Lm_all[torch.from_numpy(np.sort(l_sel).astype(np.int64))]

        z_a = _l2_t(enc(X[torch.from_numpy(a_idx)]))                # [a_bs, code]
        z_l = _l2_t(enc(X[l_rows]))                                 # [l_bs, code]
        S = z_a @ z_l.t()                                           # [a_bs, l_bs]
        T = T_all[torch.from_numpy(a_idx)][:, torch.from_numpy(np.sort(l_sel).astype(np.int64))]
        # row-center both -> match RELATIONAL geometry (scale/shift-robust RKD)
        S_c = S - S.mean(dim=1, keepdim=True)
        T_c = T - T.mean(dim=1, keepdim=True)
        geo_loss = torch.nn.functional.smooth_l1_loss(S_c, T_c, beta=0.1)
        # anti-collapse variance term on the batch codes
        hc = z_a - z_a.mean(dim=0, keepdim=True)
        std = torch.sqrt(hc.var(dim=0) + 1e-4)
        var_term = torch.mean(torch.relu(1.0 - std))
        loss = geo_loss + cfg["lambda_var"] * var_term
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite loss at ep=%d (seed=%d)" % (ep, seed))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if (ep % log_every == 0) or (ep == cfg["epochs"] - 1):
            _log("  train seed=%d ep=%d/%d geo=%.4f var=%.4f (%.1fs)"
                 % (seed, ep, cfg["epochs"], float(geo_loss.detach()), float(var_term.detach()),
                    time.perf_counter() - t0))
    enc.eval()
    return enc


def encode_all(enc, feats):
    with torch.no_grad():
        emb = _l2_t(enc(torch.from_numpy(feats.astype(np.float32)))).numpy().astype(np.float32)
    return emb


# ---------------------------------------------------------------------------
# WordNet semantic-neighbourhood eval (shared across arms)
# ---------------------------------------------------------------------------
def _auc_from_scores(scores, pos_mask):
    """Mann-Whitney AUC for one query: P(pos gallery ranked above neg gallery). Base 0.5."""
    n_pos = int(pos_mask.sum())
    n_neg = int(pos_mask.shape[0] - n_pos)
    if n_pos == 0 or n_neg == 0:
        return None
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(scores.shape[0], dtype=np.float64)
    ranks[order] = np.arange(1, scores.shape[0] + 1)
    return float((ranks[pos_mask].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def eval_semantic_neighbourhood(codes, split, lex_labels, k=10):
    """Query = held-out concepts; gallery = TRAIN concepts. Rank gallery by code-cosine.
    Returns same-lexname AUC (primary), precision@k, recall@1, + category base-rate (random floor)."""
    train_idx = split["train_idx"].astype(np.int64)
    held_idx = split["held_idx"].astype(np.int64)
    Zg = codes[train_idx]                                       # [G, code]
    gl = lex_labels[train_idx]                                  # [G]
    aucs, precs, rec1 = [], [], []
    base_rates = []
    G = train_idx.shape[0]
    for h in held_idx.tolist():
        ql = lex_labels[h]
        pos_mask = (gl == ql)
        n_pos = int(pos_mask.sum())
        if n_pos == 0 or n_pos == G:
            continue
        scores = Zg @ codes[h]                                  # [G]
        a = _auc_from_scores(scores, pos_mask)
        if a is None:
            continue
        aucs.append(a)
        topk = np.argsort(-scores, kind="mergesort")[:k]
        precs.append(float(pos_mask[topk].mean()))
        rec1.append(float(pos_mask[topk[0]]))
        base_rates.append(float(n_pos) / float(G))
    if len(aucs) < 5:
        return dict(same_lex_auc=float("nan"), precision_at_k=float("nan"),
                    recall_at_1=float("nan"), category_base_rate=float("nan"), n_query=len(aucs))
    return dict(same_lex_auc=float(np.mean(aucs)),
                precision_at_k=float(np.mean(precs)),
                recall_at_1=float(np.mean(rec1)),
                category_base_rate=float(np.mean(base_rates)),
                n_query=len(aucs))


def _emb_digest(emb):
    return hashlib.sha256(np.ascontiguousarray(emb.astype(np.float32)).tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# One seed
# ---------------------------------------------------------------------------
def run_seed(seed, split, feats, landmarks, target_geo, lex_labels, cfg):
    train_idx = split["train_idx"]
    K = split["K"]

    arm_codes = {}
    # PRIMARY: R1 landmark-geometry encoder; GROUNDING-ONLY input, RELATIONAL-graph target geometry.
    # Same input as RAW_GROUNDING -> LEARNED - RAW_GROUNDING isolates the value of learning.
    enc = train_landmark_encoder(feats["own"], target_geo, landmarks, train_idx, cfg, seed, do_train=True)
    arm_codes[PRIMARY_ARM] = encode_all(enc, feats["own"])

    # LEARNED_RICH: grounding+ctx input, same relational target (does the richer input help learning?)
    enc_rich = train_landmark_encoder(feats["rich"], target_geo, landmarks, train_idx, cfg,
                                      seed + 55, do_train=True)
    arm_codes[LEARNED_RICH_ARM] = encode_all(enc_rich, feats["rich"])

    # RAW baselines (no learning): cosine over raw features
    arm_codes[RAW_ARM] = _l2_np(feats["own"].astype(np.float64)).astype(np.float32)
    arm_codes[RAWCTX_ARM] = _l2_np(feats["rich"].astype(np.float64)).astype(np.float32)

    # RANDOM_INIT: untrained encoder, SAME grounding input as PRIMARY
    enc_r = train_landmark_encoder(feats["own"], target_geo, landmarks, train_idx, cfg,
                                   seed + 101, do_train=False)
    arm_codes[RANDINIT_ARM] = encode_all(enc_r, feats["own"])

    # COLLAPSE_SHUFFLE: permute grounding input rows across ids (destroys id<->grounding correspondence),
    # keep the relational target from the true graph, train -> encoder cannot align -> ~0.5 (leak witness)
    perm = np.random.default_rng(seed + 909).permutation(K)
    own_shuf = feats["own"][perm]
    enc_s = train_landmark_encoder(own_shuf, target_geo, landmarks, train_idx, cfg, seed + 1, do_train=True)
    arm_codes[SHUFFLE_ARM] = encode_all(enc_s, own_shuf)

    arm_metrics = {}
    for arm in ALL_ARMS:
        ev = eval_semantic_neighbourhood(arm_codes[arm], split, lex_labels, k=10)
        ev["emb_digest"] = _emb_digest(arm_codes[arm])
        arm_metrics[arm] = ev
        _log("seed=%d arm=%s same_lex_auc=%.4f prec@10=%.4f rec@1=%.4f base=%.4f n_q=%d"
             % (seed, arm, ev["same_lex_auc"], ev["precision_at_k"], ev["recall_at_1"],
                ev["category_base_rate"], ev["n_query"]))

    # ARMS-MUST-DIFFER (META_RULE_AF)
    digs = {a: arm_metrics[a]["emb_digest"] for a in ALL_ARMS}
    dl = sorted(digs.items())
    for i in range(len(dl)):
        for j in range(i + 1, len(dl)):
            assert dl[i][1] != dl[j][1], ("META_RULE_AF VIOLATION: arms %s and %s bit-identical"
                                          % (dl[i][0], dl[j][0]))
    return arm_metrics


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed, data_meta, split_meta):
    def series(arm, key):
        return np.array([m[arm][key] for m in per_seed], dtype=np.float64)

    agg = {}
    for arm in ALL_ARMS:
        agg[arm] = dict(
            same_lex_auc_mean=float(series(arm, "same_lex_auc").mean()),
            same_lex_auc_min=float(series(arm, "same_lex_auc").min()),
            precision_at_k_mean=float(series(arm, "precision_at_k").mean()),
            recall_at_1_mean=float(series(arm, "recall_at_1").mean()),
            category_base_rate_mean=float(series(arm, "category_base_rate").mean()),
            n_seeds=len(per_seed),
        )

    learned = agg[PRIMARY_ARM]["same_lex_auc_mean"]
    learned_min = agg[PRIMARY_ARM]["same_lex_auc_min"]
    learned_rich = agg[LEARNED_RICH_ARM]["same_lex_auc_mean"]
    raw = agg[RAW_ARM]["same_lex_auc_mean"]
    rawctx = agg[RAWCTX_ARM]["same_lex_auc_mean"]
    randinit = agg[RANDINIT_ARM]["same_lex_auc_mean"]
    shuf = agg[SHUFFLE_ARM]["same_lex_auc_mean"]
    base_rate = agg[RAW_ARM]["category_base_rate_mean"]

    # per-seed margin over raw grounding (THE number) -> robustness
    margin_raw_series = (series(PRIMARY_ARM, "same_lex_auc") - series(RAW_ARM, "same_lex_auc"))
    margin_raw = float(margin_raw_series.mean())
    margin_raw_min = float(margin_raw_series.min())
    margin_ctx = learned - rawctx                    # value of learning beyond the richer raw input
    ctx_input_value = rawctx - raw                   # value of the context input alone (no learning)
    margin_randinit = learned - randinit             # learning vs untrained arch/input-mixing

    cb_lo, cb_hi = COLLAPSE_BAND
    can_fail_fired = bool(cb_lo <= shuf <= cb_hi)
    n_query = int(np.min(series(PRIMARY_ARM, "n_query")))
    power_ok = bool(n_query >= MIN_QUERY_TASKS)

    real_margin = bool(margin_raw >= HP_MARGIN_OVER_RAW and margin_raw_min > 0.0)
    hard_pass = bool(can_fail_fired and power_ok and real_margin
                     and learned >= HP_LEARNED_SIGNAL and learned >= randinit)
    hard_fail = bool((not can_fail_fired) or (learned < HF_AUC) or (not power_ok))

    if hard_pass:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        # LEARNED is a real held-out signal + controls valid, but the margin OVER RAW GROUNDING is below the
        # real-margin bar -> the honest INPUT-CEILING finding (grounding carries the signal; learning adds
        # ~nothing). Reported plainly per the Director contract.
        verdict = "MIDDLE_BAND"

    input_ceiling = bool(verdict == "MIDDLE_BAND" and margin_raw < HP_MARGIN_OVER_RAW)

    verdict_msg = (
        "%s | THE-NUMBER learned - raw_grounding = %.4f - %.4f = %+.4f (min=%+.4f, need>=%.2f, n_q=%d power_ok=%s) | "
        "LEARNED same_lex_auc=%.4f (min=%.4f) prec@10=%.4f rec@1=%.4f | "
        "RAW_GROUNDING=%.4f RAW+CTX=%.4f (ctx_input_value=%+.4f, learning_beyond_ctx=%+.4f) | "
        "LEARNED_RICH(ground+ctx)=%.4f | "
        "RANDOM_INIT=%.4f (learned-randinit=%+.4f) COLLAPSE_shuffle=%.4f -> can_fail=%s | "
        "category_base_rate(random floor)=%.4f | input_ceiling=%s | "
        "train=%d heldout=%d K=%d pairs=%d rels=%d lexnames=%d"
        % (verdict, learned, raw, margin_raw, margin_raw_min, HP_MARGIN_OVER_RAW, n_query, power_ok,
           learned, learned_min, agg[PRIMARY_ARM]["precision_at_k_mean"], agg[PRIMARY_ARM]["recall_at_1_mean"],
           raw, rawctx, ctx_input_value, margin_ctx,
           learned_rich,
           randinit, margin_randinit, shuf, can_fail_fired,
           base_rate, input_ceiling,
           split_meta["n_train"], split_meta["n_heldout"], data_meta["n_kept_concepts"],
           data_meta["n_kept_pairs"], data_meta["n_rel_slots"], data_meta["n_lexnames"]))

    gates = dict(
        learned_same_lex_auc=learned, learned_same_lex_auc_min=learned_min,
        learned_rich_same_lex_auc=learned_rich,
        raw_grounding_same_lex_auc=raw, raw_ground_plus_ctx_same_lex_auc=rawctx,
        random_init_same_lex_auc=randinit, collapse_shuffle_same_lex_auc=shuf,
        margin_over_raw_grounding=margin_raw, margin_over_raw_grounding_min=margin_raw_min,
        margin_over_raw_plus_ctx=margin_ctx, ctx_input_value=ctx_input_value,
        margin_over_random_init=margin_randinit,
        category_base_rate=base_rate,
        can_fail_fired=can_fail_fired, power_ok=power_ok, n_query=n_query,
        input_ceiling=input_ceiling, real_margin=real_margin,
        collapse_band=list(COLLAPSE_BAND), hp_learned_signal=HP_LEARNED_SIGNAL,
        hf_auc=HF_AUC, hp_margin_over_raw=HP_MARGIN_OVER_RAW, min_query_tasks=MIN_QUERY_TASKS,
        learned_precision_at_10=agg[PRIMARY_ARM]["precision_at_k_mean"],
        raw_precision_at_10=agg[RAW_ARM]["precision_at_k_mean"],
    )
    return verdict, verdict_msg, agg, gates


# ---------------------------------------------------------------------------
# Discriminator self-test: proves the same-lexname AUC metric is telemetry-sensitive
# ---------------------------------------------------------------------------
def discriminator_selftest():
    """Planted-category synthetic. Codes clustered by category -> AUC high; random codes -> ~0.5;
    shuffled category assignment -> ~0.5. Proves the same-lexname AUC metric moves with structure."""
    rng = np.random.default_rng(0)
    n_cat = 6
    per = 50
    K = n_cat * per
    d = 16
    cat = np.repeat(np.arange(n_cat), per).astype(np.int64)
    centers = rng.standard_normal((n_cat, d))
    struct = centers[cat] + 0.15 * rng.standard_normal((K, d))
    struct = _l2_np(struct).astype(np.float32)
    rand = _l2_np(rng.standard_normal((K, d))).astype(np.float32)

    heldout = np.array([i % 5 == 0 for i in range(K)], dtype=bool)
    fake_split = dict(train_idx=np.nonzero(~heldout)[0].astype(np.int64),
                      held_idx=np.nonzero(heldout)[0].astype(np.int64))

    ev_struct = eval_semantic_neighbourhood(struct, fake_split, cat, k=10)
    ev_rand = eval_semantic_neighbourhood(rand, fake_split, cat, k=10)
    cat_shuf = cat.copy()
    np.random.default_rng(1).shuffle(cat_shuf)
    ev_shuf = eval_semantic_neighbourhood(struct, fake_split, cat_shuf, k=10)

    res = dict(auc_struct=ev_struct["same_lex_auc"], auc_rand=ev_rand["same_lex_auc"],
               auc_label_shuffle=ev_shuf["same_lex_auc"],
               prec_struct=ev_struct["precision_at_k"], base_rate=ev_struct["category_base_rate"],
               n_query=ev_struct["n_query"])
    ok = (ev_struct["same_lex_auc"] >= 0.85
          and abs(ev_rand["same_lex_auc"] - 0.5) < 0.10
          and abs(ev_shuf["same_lex_auc"] - 0.5) < 0.10
          and ev_struct["precision_at_k"] > ev_struct["category_base_rate"] + 0.2)
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

    st_ok, st_res = discriminator_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED (same-lexname AUC metric not telemetry-sensitive): %s" % st_res,
            summary="discriminator selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res))
        raise SystemExit(1)

    _log("loading grounded subgraph (min_deg=%d cap=%d top_rel=%d)..."
         % (cfg["min_deg"], cfg["cap_nodes"], cfg["top_rel"]))
    data = load_grounded_subgraph(cfg)
    _log("grounded universe: %s" % {k: v for k, v in data["meta"].items() if k != "top_rels"})
    split = build_split(data, cfg)
    _log("split: %s" % split["split_meta"])
    feats = build_features(split)
    landmarks = select_landmarks(split, cfg)
    A = build_train_adjacency(split)
    own_norm = _l2_np(feats["own"].astype(np.float64)).astype(np.float32)
    target_geo = compute_target_geometry(own_norm, A, landmarks)
    _log("landmarks=%d own_dim=%d rich_dim=%d target_geo shape=%s tgeo_mean=%.4f tgeo_std=%.4f"
         % (landmarks.shape[0], feats["own"].shape[1], feats["rich"].shape[1], target_geo.shape,
            float(target_geo.mean()), float(target_geo.std())))

    if run_mode == "self_test":
        pm = run_seed(cfg["seeds"][0], split, feats, landmarks, target_geo, data["lex_labels"], cfg)
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS discriminator + end-to-end held-out WordNet-neighbourhood eval exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, data_meta=data["meta"], split_meta=split["split_meta"],
            learned_same_lex_auc=pm[PRIMARY_ARM]["same_lex_auc"],
            raw_grounding_same_lex_auc=pm[RAW_ARM]["same_lex_auc"],
            collapse_shuffle_same_lex_auc=pm[SHUFFLE_ARM]["same_lex_auc"]))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, split, feats, landmarks, target_geo, data["lex_labels"], cfg)
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

    verdict, verdict_msg, agg, gates = aggregate_and_verdict(per_seed, data["meta"], split["split_meta"])

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
