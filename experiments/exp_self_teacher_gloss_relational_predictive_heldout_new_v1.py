"""R3/R4 INTERNAL SELF-TEACHER (teacher-free, PREDICTIVE) concept encoder, judged on WORDNET
SEMANTIC-NEIGHBOURHOOD generalization to HELD-OUT NEW concepts.

WHY (THE_PLAN R3/R4, encoder_rescue_plan): R1 landmark-geometry (grounded_r1_landmark_geometry
FULL, MEASURED@data/exp_grounded_r1_landmark_geometry_wordnet_neighbourhood_v1/metrics.json) added
only +0.0009 over RAW-GROUNDING (learned 0.6413 vs raw 0.6404) -> the bottleneck is INPUT, not the
objective. R3/R4's missing input is RELATIONAL + GLOSS/DEFINITIONAL-TEXT co-occurrence learned
PREDICTIVELY. The brain earns word meaning largely by PREDICTING linguistic + relational context.
This cell adds that missing input + predictive signal on top of the R1 machinery and asks: does it
BREAK the +0.0009 grounding ceiling on held-out-NEW concepts?

THE SELF-TEACHER (teacher-free, predictive; fuses grounding + learned-gloss-text + relational context):
  R1 geometry loss (reused): match code-vs-landmark cosine profile to a teacher-free target geometry
    (grounding-cosine + relational-graph overlap), row-centered smooth-L1 + VICReg variance anti-collapse.
  R4 relational-prediction (predict your relational neighbours): in-batch InfoNCE where a concept's
    positive is one of its TRAIN relational neighbours; negatives are the other batch anchors. Teacher-
    free (foundation's own graph); the temporal-contiguity / predictive-coding auxiliary.
  R3 gloss-context prediction (masked/context prediction): the gloss is encoded by OUR OWN glass-box
    learned encoder (char-trigram hashing bag -> a learned Linear projection, from scratch; NO pretrained
    text embedder). A random fraction of the concept's gloss char-trigram buckets are MASKED from the
    encoder input; a decoder head must reconstruct the FULL gloss bag from the code (masked BCE). This
    makes the code carry gloss/definitional context PREDICTIVELY.
  EMA self-distillation (stability target): a slow EMA copy of the encoder (BYOL/DINO analog; the brain's
    slow consolidated target) encodes one dropout view; the student matches it on another view. Teacher-
    free, stabilizes the fused geometry.

HARD INVARIANTS (project locks):
  - TEACHER-FREE: NO GloVe/BGE/transformer/borrowed vector anywhere. The GLOSS TEXT is encoded ONLY by our
    own learned char-trigram Linear (from scratch). Inputs are ONLY measured grounding norms + the
    foundation's own relational graph + WordNet gloss STRINGS (encoded by us). WordNet lexname (supersense)
    is EVAL-ONLY ground truth, never an input nor a training target.
  - INDUCTIVE: a held-out NEW concept is PLACED from its features (grounding + its own gloss text + its
    known TRAIN-neighbour relational context) -> code; never a learned per-concept lookup. Held-out is
    never a landmark, never a training anchor, never an InfoNCE positive/target.
  - LEAK-PROOF held-out-NEW: concept-level held-out split (sha256 on id, PYTHONHASHSEED-independent). The
    WordNet supersense truth is disjoint from every input/target. Gloss char-trigrams use a fixed HASH
    bucketing (vocab-free -> no train-fit vocab leak; fully inductive). Relational context is restricted to
    TRAIN neighbours only. RAW_GLOSS / RAW_GROUNDING baselines share the SAME inputs as the learned arms.

TEST (WordNet semantic-neighbourhood on HELD-OUT NEW concepts): SAME-LEXNAME AUC = for each held-out
query, rank the TRAIN gallery by code-cosine; AUC = P(a same-supersense gallery concept ranks above a
different-supersense one). Base = 0.5 exactly. Secondary: precision@10, recall@1, category base-rate.
Also reports a RELATIONAL-placement AUC (does the code rank the concept's true TRAIN relational neighbours
above non-neighbours) as the second head the self-teacher optimizes.

THE ONE NUMBER (Director contract): SELF_TEACHER same_lex_auc MINUS RAW_GROUNDING same_lex_auc, on
held-out-NEW concepts. Break the +0.0009 ceiling by a REAL margin (target >= 0.03, > noise, min>0). If
adding gloss-text + relational-predictive STILL ties raw grounding, that is a MAJOR honest finding (a
DEEPER input/representation ceiling) reported plainly as MIDDLE_BAND with the per-item WHY.

ABLATION (attribute WHERE any gain comes from):
  ARM_RAW_GROUNDING       : cosine over raw grounding (20d), NO learning.  [THE ceiling to break]
  ARM_RAW_GLOSS           : cosine over raw gloss char-trigram bag, NO learning.  [is the signal in the
                            gloss INPUT itself, or earned by learning?]
  ARM_GROUNDING_ONLY_LEARN: R1 landmark geometry, grounding-only input (= the prior +0.0009 arm).
  ARM_PLUS_GLOSS_LEARN    : grounding+gloss input, geometry + masked-gloss prediction (NO relpred/EMA).
  ARM_PLUS_RELPRED_LEARN  : grounding input, geometry + relational-prediction InfoNCE (NO gloss/EMA).
  ARM_SELF_TEACHER        : FULL fusion (grounding+gloss+relctx) + geometry + relpred + gloss-pred + EMA.  [PRIMARY]
  ARM_RANDOM_INIT         : untrained FULL encoder (random weights).  [isolate learning from architecture]
  ARM_COLLAPSE_SHUFFLE    : input rows permuted across ids, then trained -> ~0.5.  [CAN-FAIL / leak witness]

CAN-FAIL GATE: ARM_COLLAPSE_SHUFFLE must sit ~0.5. RAW_GROUNDING must be a real >0.5 signal (else metric
saturated/leaking). DEFLATE: SELF_TEACHER merely tying RAW_GROUNDING = honest deeper-ceiling -> MIDDLE_BAND.

CPU-only. No GPU. No network at run time (WordNet from local NLTK; lexnames + glosses cached to disk). ASCII-only.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test over code arms)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator has base=0.5 exactly; collapse+random-init controls witness the floor
# - baseline_in_band at smoke: collapse ~0.5; raw-grounding a real >0.55 signal (measured); self-teacher not saturated
# - discriminator survives scale: FULL runs foreground-to-completion (~few min) so FULL IS the discriminator test
# - HARD_PASS strictly above floor: self_teacher_auc>=0.60 AND (self_teacher-raw_grounding)>=0.03 AND margin_min>0
#   AND self_teacher>=random_init AND can_fail(collapse ~0.5)
# - HP_SCOPE: gates apply to ARM_SELF_TEACHER (primary) only
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; controls witness it empirically)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg
# - deterministic seeding: sha256 concept split + sha256 gloss-hash + fixed int seeds + sorted(); no hash()/list(set()) (PROT-023)
# - no substrate KGStore/fit objects (self-contained jsonl reader + NLTK + torch MLP) -> F.1/F.2 real_code_path N/A
# - progress_logging: print_flush_true (timeout < 30min so not mandatory, but present)
"""

import argparse
import glob
import hashlib
import json
import math
import os
import platform
import re
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

ANCHOR_NAME = "self_teacher_gloss_relational_predictive_heldout_new_v1"
FOUNDATION_DIR = os.path.join(_REPO, "data", "cskg_foundation_v1")
NODES_PATH = os.path.join(FOUNDATION_DIR, "nodes.jsonl")
EDGES_GLOB = os.path.join(FOUNDATION_DIR, "edges_shard_*.jsonl")
LEXNAME_CACHE = os.path.join(_REPO, "data", "wordnet_lexname_cache_v1.json")
GLOSS_CACHE = os.path.join(_REPO, "data", "wordnet_gloss_cache_v1.json")

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
    min_deg=2, cap_nodes=400, seeds=[7], epochs=20, batch=128,
    code_dim=32, hidden=64, lr=5e-3, n_landmarks=64, n_land_batch=48, n_anchor_batch=96,
    lambda_var=1.0, heldout_frac=0.2, top_rel=8,
    gloss_vocab=512, gloss_proj=32, gloss_mask_frac=0.3, feat_dropout=0.1,
    w_geo=1.0, w_rel=0.5, w_gloss=0.5, w_ema=0.5, ema_momentum=0.99, infonce_tau=0.2,
)
SMOKE_CFG = dict(
    min_deg=2, cap_nodes=2500, seeds=[7, 13], epochs=120, batch=256,
    code_dim=128, hidden=256, lr=3e-3, n_landmarks=256, n_land_batch=128, n_anchor_batch=256,
    lambda_var=1.0, heldout_frac=0.2, top_rel=16,
    gloss_vocab=2048, gloss_proj=64, gloss_mask_frac=0.3, feat_dropout=0.1,
    w_geo=1.0, w_rel=0.5, w_gloss=0.5, w_ema=0.5, ema_momentum=0.99, infonce_tau=0.2,
)
FULL_CFG = dict(
    min_deg=2, cap_nodes=5000, seeds=[7, 13, 17], epochs=160, batch=256,
    code_dim=128, hidden=256, lr=2.5e-3, n_landmarks=512, n_land_batch=192, n_anchor_batch=256,
    lambda_var=1.0, heldout_frac=0.2, top_rel=16,
    gloss_vocab=2048, gloss_proj=64, gloss_mask_frac=0.3, feat_dropout=0.1,
    w_geo=1.0, w_rel=0.5, w_gloss=0.5, w_ema=0.5, ema_momentum=0.99, infonce_tau=0.2,
)

# Deterministic salts / seeds
CONCEPT_SPLIT_SALT = "st_gloss_rel_v1_concept_split::"
EVAL_SEED = 20260726

# Pre-reg bands (applied to ARM_SELF_TEACHER primary held-out SAME-LEXNAME AUC).
HP_SELF_TEACHER_SIGNAL = 0.60     # SELF_TEACHER must be a genuine held-out signal well above chance 0.5
HF_AUC = 0.53                     # below this = essentially chance = HARD_FAIL
HP_MARGIN_OVER_RAW = 0.03         # THE NUMBER: SELF_TEACHER - RAW_GROUNDING must exceed this (break +0.0009)
COLLAPSE_BAND = (0.44, 0.56)      # ARM_COLLAPSE_SHUFFLE MUST sit here (can-fail witness)
RAW_SIGNAL_MIN = 0.55             # RAW_GROUNDING must be a real >0.55 signal (metric-not-saturated gate)
MIN_QUERY_TASKS = 150             # power floor for the held-out AUC to be trustworthy

# Arms
PRIMARY_ARM = "ARM_SELF_TEACHER"          # full fusion + all objectives + EMA
GROUND_ONLY_ARM = "ARM_GROUNDING_ONLY_LEARN"  # R1 geometry, grounding-only input (prior +0.0009 arm)
PLUS_GLOSS_ARM = "ARM_PLUS_GLOSS_LEARN"   # grounding+gloss input + geometry + gloss-pred
PLUS_REL_ARM = "ARM_PLUS_RELPRED_LEARN"   # grounding input + geometry + relational-prediction
RAW_ARM = "ARM_RAW_GROUNDING"             # grounding cosine, NO learning (THE ceiling)
RAWGLOSS_ARM = "ARM_RAW_GLOSS"            # raw gloss char-trigram cosine, NO learning
RANDINIT_ARM = "ARM_RANDOM_INIT"          # untrained full encoder
SHUFFLE_ARM = "ARM_COLLAPSE_SHUFFLE"      # input rows permuted across ids, trained -> ~0.5
ALL_ARMS = [PRIMARY_ARM, GROUND_ONLY_ARM, PLUS_GLOSS_ARM, PLUS_REL_ARM,
            RAW_ARM, RAWGLOSS_ARM, RANDINIT_ARM, SHUFFLE_ARM]


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
# WordNet lexname (supersense) EVAL-ONLY truth + gloss (definitional text) INPUT
# ---------------------------------------------------------------------------
def _dominant_synset(wn, surface):
    for cand in (surface.replace(" ", "_"), surface.replace(" ", ""), surface.split(" ")[0]):
        if not cand:
            continue
        try:
            ss = wn.synsets(cand)
        except Exception:  # noqa: BLE001 -- NLTK lookup hiccup on a single token: try next candidate
            ss = []
        if ss:
            return ss[0]
    return None


def _build_lexname_gloss_maps(surfaces):
    """surfaces: list[str]. Return ({surface: lexname or None}, {surface: gloss str or ''}).
    Both from the SAME dominant (first) synset; lexname is EVAL-ONLY truth, gloss is an INPUT feature.
    Cached to disk (idempotent). NLTK-local only."""
    lex_cache, gloss_cache = {}, {}
    if os.path.exists(LEXNAME_CACHE):
        try:
            with open(LEXNAME_CACHE, "r", encoding="utf-8") as f:
                lex_cache = json.load(f)
        except (ValueError, OSError):
            lex_cache = {}
    if os.path.exists(GLOSS_CACHE):
        try:
            with open(GLOSS_CACHE, "r", encoding="utf-8") as f:
                gloss_cache = json.load(f)
        except (ValueError, OSError):
            gloss_cache = {}
    need = [s for s in surfaces if (s not in lex_cache) or (s not in gloss_cache)]
    if need:
        try:
            from nltk.corpus import wordnet as wn
        except ImportError as e:
            raise RuntimeError("NLTK WordNet required for EVAL-ONLY lexname + gloss INPUT. "
                               "Install nltk + wordnet data.") from e
        for s in need:
            ss = _dominant_synset(wn, s)
            lex_cache[s] = ss.lexname() if ss is not None else None
            gloss_cache[s] = ss.definition() if ss is not None else ""
        for path, cache in ((LEXNAME_CACHE, lex_cache), (GLOSS_CACHE, gloss_cache)):
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(cache, f)
            os.replace(tmp, path)
    return ({s: lex_cache.get(s) for s in surfaces},
            {s: gloss_cache.get(s, "") for s in surfaces})


# ---------------------------------------------------------------------------
# Glass-box gloss encoder INPUT: char-trigram HASHING bag (vocab-free, inductive, teacher-free)
# ---------------------------------------------------------------------------
_WORD_RE = re.compile(r"[a-z]+")


def _gloss_bag(gloss, vocab):
    """Bag of char-trigram HASH buckets for one gloss string. Deterministic sha256 hashing (no train-fit
    vocab -> fully inductive; PROT-023 deterministic). L2-normalized. Returns float32 [vocab]."""
    vec = np.zeros(vocab, dtype=np.float32)
    if not gloss:
        return vec
    for tok in _WORD_RE.findall(gloss.lower()):
        s = "<" + tok + ">"
        for i in range(len(s) - 2):
            tri = s[i:i + 3]
            b = int.from_bytes(hashlib.sha256(tri.encode("utf-8")).digest()[:4], "big") % vocab
            vec[b] += 1.0
    nrm = math.sqrt(float((vec * vec).sum()) + 1e-8)
    if nrm > 0:
        vec /= nrm
    return vec


# ---------------------------------------------------------------------------
# Foundation loader: grounded induced subgraph WITH relations, lexname truth, gloss text
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
    """Load grounded concepts WITH a WordNet lexname + gloss + induced relational subgraph."""
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

    # EVAL-ONLY WordNet lexname truth + gloss INPUT; keep ONLY concepts with a lexname (98.5% of grounded).
    lexmap, glossmap = _build_lexname_gloss_maps(surf_list)
    has_lex = [i for i in range(len(gid_list)) if lexmap[surf_list[i]] is not None]
    if len(has_lex) < 100:
        raise RuntimeError("too few grounded nodes with a WordNet lexname (%d)" % len(has_lex))

    gid_list = [gid_list[i] for i in has_lex]
    surf_list = [surf_list[i] for i in has_lex]
    raw_vals = [raw_vals[i] for i in has_lex]
    raw_gpres = [raw_gpres[i] for i in has_lex]
    lex_list = [lexmap[s] for s in surf_list]
    gloss_list = [glossmap[s] for s in surf_list]

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
    glosses = [gloss_list[o] for o in kept]
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

    # gloss char-trigram HASH bag [K, vocab] (glass-box learned-encoder INPUT; vocab-free hashing)
    V = cfg["gloss_vocab"]
    gloss_bag = np.stack([_gloss_bag(g, V) for g in glosses], axis=0).astype(np.float32)
    n_gloss_nonempty = int((gloss_bag.sum(axis=1) > 0).sum())

    # lexname -> integer label
    uniq_lex = sorted(set(lexnames))
    lex_to_int = {lx: i for i, lx in enumerate(uniq_lex)}
    lex_labels = np.array([lex_to_int[lx] for lx in lexnames], dtype=np.int64)

    meta = dict(
        n_grounded_total=n_all, n_induced_pairs_total=len(pair_rels),
        n_kept_concepts=K, n_kept_pairs=len(kept_pair_rels),
        min_deg=cfg["min_deg"], cap_nodes=cfg["cap_nodes"],
        top_rels=top_rels, n_rel_slots=R, n_lexnames=len(uniq_lex),
        gloss_vocab=V, n_gloss_nonempty=n_gloss_nonempty,
        gloss_coverage=float(n_gloss_nonempty) / float(K),
    )
    return dict(ids=ids, surfaces=surfaces, vals=vals, gpres=gpres, gloss_bag=gloss_bag,
                pair_rels=kept_pair_rels, K=K, R=R, rel_slot=_rel_slot,
                lex_labels=lex_labels, uniq_lex=uniq_lex, meta=meta)


# ---------------------------------------------------------------------------
# Split + standardize + typed TRAIN-neighbour context aggregation + relpred positives
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
    train_neigh = [set() for _ in range(K)]        # concept -> set(train neighbour j) untyped (relpred positives)
    train_deg = np.zeros(K, dtype=np.float64)
    for (a, b), rels in data["pair_rels"].items():
        if b in train_set:
            for r in rels:
                ctx_nei_by_rel[a].setdefault(rel_slot(r), set()).add(b)
            train_neigh[a].add(b)
        if a in train_set:
            for r in rels:
                ctx_nei_by_rel[b].setdefault(rel_slot(r), set()).add(a)
            train_neigh[b].add(a)
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
                ctx_nei_by_rel=ctx_nei_by_rel, train_neigh=train_neigh, split_meta=split_meta)


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


def build_features(split, data):
    """Raw feature matrices used by arms: grounding (own), relational-context pooled (ctx), gloss bag."""
    own = split["own_feat"]                                   # [K,20]
    ctx = _pooled_ctx_block(split, own, GROUND_DIM)           # [K, R*22]
    return dict(own=own.astype(np.float32), ctx=ctx.astype(np.float32),
                gloss=data["gloss_bag"].astype(np.float32))   # gloss [K, vocab]


# ---------------------------------------------------------------------------
# Fusion encoder (grounding + gloss branch + relational-context) + gloss reconstruction head
# ---------------------------------------------------------------------------
class FusionEncoder(torch.nn.Module):
    def __init__(self, ground_dim, ctx_dim, gloss_vocab, gloss_proj, hidden, code_dim,
                 use_ctx, use_gloss):
        super().__init__()
        self.use_ctx = use_ctx
        self.use_gloss = use_gloss
        in_dim = ground_dim
        if use_ctx:
            in_dim += ctx_dim
        if use_gloss:
            self.gloss_branch = torch.nn.Sequential(
                torch.nn.Linear(gloss_vocab, gloss_proj), torch.nn.GELU())
            in_dim += gloss_proj
        self.net = torch.nn.Sequential(
            torch.nn.Linear(in_dim, hidden), torch.nn.GELU(),
            torch.nn.Linear(hidden, code_dim))
        if use_gloss:
            # decoder head: code -> full gloss bag (masked-context prediction target)
            self.gloss_head = torch.nn.Linear(code_dim, gloss_vocab)

    def encode(self, ground, ctx, gloss):
        parts = [ground]
        if self.use_ctx:
            parts.append(ctx)
        if self.use_gloss:
            parts.append(self.gloss_branch(gloss))
        return self.net(torch.cat(parts, dim=1))

    def forward(self, ground, ctx, gloss):
        return self.encode(ground, ctx, gloss)


def _l2_np(x, eps=1e-8):
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + eps)


def _l2_t(h, eps=1e-8):
    return h / (h.norm(dim=1, keepdim=True) + eps)


def select_landmarks(split, cfg):
    """Deterministic anchor frame: TRAIN concepts with the highest train-degree (dense, span the manifold).
    Landmarks are TRAIN-ONLY (held-out never a landmark)."""
    train_idx = split["train_idx"].tolist()
    train_deg = split["train_deg"]
    ranked = sorted(train_idx, key=lambda i: (-float(train_deg[i]), i))
    L = min(cfg["n_landmarks"], len(ranked))
    return np.array(sorted(ranked[:L]), dtype=np.int64)


def build_train_adjacency(split):
    """Binary TRAIN-neighbour adjacency A[K, K] (float32) via the train-restricted ctx sets. Teacher-free."""
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
    """Teacher-free R1 TARGET geometry graded by shared-vs-distinct PROPERTY + RELATIONAL overlap:
      G[c,l] = cosine(grounding_c, grounding_l); R[c,l] = |N(c) INT N(l)| / sqrt(|N(c)||N(l)|)
      T = alpha*z(G) + (1-alpha)*z(R). Both from the concepts' OWN grounding + the foundation's OWN graph."""
    Lm_own = own_norm[landmarks]                      # [L, D]
    G = own_norm @ Lm_own.T                           # [K, L]
    Lm_A = A[landmarks]                               # [L, K]
    shared = A @ Lm_A.T                               # [K, L]
    deg = np.sqrt((A * A).sum(axis=1) + 1e-6)         # [K]
    deg_l = deg[landmarks]                            # [L]
    R = shared / (deg[:, None] * deg_l[None, :] + 1e-6)
    T = alpha * _zscore_matrix(G) + (1.0 - alpha) * _zscore_matrix(R)
    return T.astype(np.float32)                        # [K, L]


# ---------------------------------------------------------------------------
# The self-teacher training loop (weighted, teacher-free, predictive + EMA)
# ---------------------------------------------------------------------------
def _pick_relpred_positive(anchor_ids, train_neigh, rng):
    """For each anchor, pick one TRAIN neighbour (in-batch InfoNCE positive). Returns (valid_mask, pos_j)
    arrays aligned to anchor_ids. Anchors with no train neighbour are masked out of the relpred loss."""
    valid = np.zeros(anchor_ids.shape[0], dtype=bool)
    pos = np.zeros(anchor_ids.shape[0], dtype=np.int64)
    for k, a in enumerate(anchor_ids.tolist()):
        nb = train_neigh[a]
        if nb:
            arr = np.fromiter(sorted(nb), dtype=np.int64, count=len(nb))
            pos[k] = int(arr[rng.integers(0, arr.shape[0])])
            valid[k] = True
    return valid, pos


def train_self_teacher(feats, target_geo, landmarks, split, cfg, seed,
                       use_ctx, use_gloss, w_rel, w_gloss, w_ema, do_train=True, shuffle_rows=False):
    """Train a fusion encoder with a weighted teacher-free objective. Setting w_rel/w_gloss/w_ema to 0
    ablates that component; use_ctx/use_gloss select the input branches. do_train=False = random-init.
    shuffle_rows permutes the input rows across ids (COLLAPSE witness)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed + 17)

    K = split["K"]
    ground = feats["own"].astype(np.float32)
    ctx = feats["ctx"].astype(np.float32)
    gloss = feats["gloss"].astype(np.float32)
    if shuffle_rows:
        perm = np.random.default_rng(seed + 909).permutation(K)
        ground = ground[perm]
        ctx = ctx[perm]
        gloss = gloss[perm]

    Xg = torch.from_numpy(ground)
    Xc = torch.from_numpy(ctx)
    Xt = torch.from_numpy(gloss)
    gloss_vocab = gloss.shape[1]

    enc = FusionEncoder(GROUND_DIM, ctx.shape[1], gloss_vocab, cfg["gloss_proj"],
                        cfg["hidden"], cfg["code_dim"], use_ctx=use_ctx, use_gloss=use_gloss)
    if not do_train:
        enc.eval()
        return enc

    ema = None
    if w_ema > 0.0:
        import copy
        ema = copy.deepcopy(enc)
        for p in ema.parameters():
            p.requires_grad_(False)

    opt = torch.optim.Adam([p for p in enc.parameters() if p.requires_grad], lr=cfg["lr"])
    Lm_all = torch.from_numpy(landmarks.astype(np.int64))
    T_all = torch.from_numpy(target_geo.astype(np.float32))     # [K, L]
    anchors = np.asarray(split["train_idx"], dtype=np.int64)
    train_neigh = split["train_neigh"]
    nL = landmarks.shape[0]
    fd = cfg["feat_dropout"]
    mask_frac = cfg["gloss_mask_frac"]
    tau = cfg["infonce_tau"]
    log_every = max(1, cfg["epochs"] // 5)
    t0 = time.perf_counter()

    def _enc_rows(module, rows, gloss_mask=None, feat_drop=0.0):
        g = Xg[rows]
        c = Xc[rows]
        t = Xt[rows]
        if gloss_mask is not None:
            t = t * gloss_mask
        if feat_drop > 0.0:
            g = torch.nn.functional.dropout(g, p=feat_drop, training=True)
            c = torch.nn.functional.dropout(c, p=feat_drop, training=True)
        return module.encode(g, c, t)

    for ep in range(cfg["epochs"]):
        a_bs = min(cfg["n_anchor_batch"], anchors.shape[0])
        l_bs = min(cfg["n_land_batch"], nL)
        a_idx = rng.choice(anchors, size=a_bs, replace=False)
        l_sel = np.sort(rng.choice(nL, size=l_bs, replace=False))
        a_rows = torch.from_numpy(a_idx)
        l_rows = Lm_all[torch.from_numpy(l_sel)]

        # --- R1 landmark geometry (always on) ---
        z_a = _l2_t(_enc_rows(enc, a_rows))
        z_l = _l2_t(_enc_rows(enc, l_rows))
        S = z_a @ z_l.t()
        T = T_all[a_rows][:, torch.from_numpy(l_sel)]
        S_c = S - S.mean(dim=1, keepdim=True)
        T_c = T - T.mean(dim=1, keepdim=True)
        geo_loss = torch.nn.functional.smooth_l1_loss(S_c, T_c, beta=0.1)
        hc = z_a - z_a.mean(dim=0, keepdim=True)
        std = torch.sqrt(hc.var(dim=0) + 1e-4)
        var_term = torch.mean(torch.relu(1.0 - std))
        loss = cfg["w_geo"] * geo_loss + cfg["lambda_var"] * var_term

        # --- R4 relational prediction (predict your train neighbours; in-batch InfoNCE) ---
        rel_loss_val = 0.0
        if w_rel > 0.0:
            valid, pos_j = _pick_relpred_positive(a_idx, train_neigh, rng)
            if valid.sum() >= 4:
                vsel = np.nonzero(valid)[0]
                z_anc = z_a[torch.from_numpy(vsel.astype(np.int64))]         # [nv, code]
                pos_rows = torch.from_numpy(pos_j[vsel].astype(np.int64))
                z_pos = _l2_t(_enc_rows(enc, pos_rows))                      # [nv, code]
                logits = (z_anc @ z_pos.t()) / tau                          # [nv, nv]; diagonal = positive
                tgt = torch.arange(z_anc.shape[0])
                rel_loss = torch.nn.functional.cross_entropy(logits, tgt)
                loss = loss + w_rel * rel_loss
                rel_loss_val = float(rel_loss.detach())

        # --- R3 masked gloss-context prediction (reconstruct full gloss bag from masked input) ---
        gloss_loss_val = 0.0
        if w_gloss > 0.0 and use_gloss:
            keep = (torch.rand(a_bs, gloss_vocab) > mask_frac).float()      # random bucket mask
            z_masked = enc.encode(Xg[a_rows], Xc[a_rows], Xt[a_rows] * keep)
            logits_g = enc.gloss_head(z_masked)                            # [a_bs, vocab]
            tgt_g = (Xt[a_rows] > 0).float()                               # multi-hot presence target (full bag)
            gloss_loss = torch.nn.functional.binary_cross_entropy_with_logits(logits_g, tgt_g)
            loss = loss + w_gloss * gloss_loss
            gloss_loss_val = float(gloss_loss.detach())

        # --- EMA self-distillation (student view A matches slow-teacher view B) ---
        ema_loss_val = 0.0
        if w_ema > 0.0 and ema is not None:
            z_stud = _l2_t(_enc_rows(enc, a_rows, feat_drop=fd))
            with torch.no_grad():
                z_teach = _l2_t(_enc_rows(ema, a_rows, feat_drop=fd))
            ema_loss = (1.0 - (z_stud * z_teach).sum(dim=1)).mean()
            loss = loss + w_ema * ema_loss
            ema_loss_val = float(ema_loss.detach())

        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite loss at ep=%d (seed=%d)" % (ep, seed))
        opt.zero_grad()
        loss.backward()
        opt.step()

        if ema is not None:
            m = cfg["ema_momentum"]
            with torch.no_grad():
                for pe, ps in zip(ema.parameters(), enc.parameters()):
                    pe.mul_(m).add_(ps, alpha=1.0 - m)

        if (ep % log_every == 0) or (ep == cfg["epochs"] - 1):
            _log("  train seed=%d ep=%d/%d geo=%.4f var=%.4f rel=%.4f gloss=%.4f ema=%.4f (%.1fs)"
                 % (seed, ep, cfg["epochs"], float(geo_loss.detach()), float(var_term.detach()),
                    rel_loss_val, gloss_loss_val, ema_loss_val, time.perf_counter() - t0))
    enc.eval()
    return enc


def encode_all(enc, feats):
    with torch.no_grad():
        g = torch.from_numpy(feats["own"].astype(np.float32))
        c = torch.from_numpy(feats["ctx"].astype(np.float32))
        t = torch.from_numpy(feats["gloss"].astype(np.float32))
        emb = _l2_t(enc.encode(g, c, t)).numpy().astype(np.float32)
    return emb


# ---------------------------------------------------------------------------
# WordNet semantic-neighbourhood eval + relational-placement eval (shared across arms)
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
    Zg = codes[train_idx]
    gl = lex_labels[train_idx]
    aucs, precs, rec1, base_rates = [], [], [], []
    G = train_idx.shape[0]
    for h in held_idx.tolist():
        ql = lex_labels[h]
        pos_mask = (gl == ql)
        n_pos = int(pos_mask.sum())
        if n_pos == 0 or n_pos == G:
            continue
        scores = Zg @ codes[h]
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
    return dict(same_lex_auc=float(np.mean(aucs)), precision_at_k=float(np.mean(precs)),
                recall_at_1=float(np.mean(rec1)), category_base_rate=float(np.mean(base_rates)),
                n_query=len(aucs))


def eval_relational_placement(codes, split):
    """Held-out RELATIONAL-placement AUC: query = held-out concepts with >=1 TRAIN neighbour; gallery =
    TRAIN concepts; positives = the query's true TRAIN neighbours. Does the code rank a concept's real
    relational neighbours above non-neighbours? (the head the self-teacher's relpred optimizes)."""
    train_idx = split["train_idx"].astype(np.int64)
    held_idx = split["held_idx"].astype(np.int64)
    train_neigh = split["train_neigh"]
    tset = {int(t): p for p, t in enumerate(train_idx.tolist())}
    Zg = codes[train_idx]
    aucs = []
    G = train_idx.shape[0]
    for h in held_idx.tolist():
        nb = [tset[j] for j in train_neigh[h] if j in tset]
        n_pos = len(nb)
        if n_pos == 0 or n_pos == G:
            continue
        pos_mask = np.zeros(G, dtype=bool)
        pos_mask[np.asarray(nb, dtype=np.int64)] = True
        scores = Zg @ codes[h]
        a = _auc_from_scores(scores, pos_mask)
        if a is not None:
            aucs.append(a)
    if len(aucs) < 5:
        return dict(rel_place_auc=float("nan"), n_query=len(aucs))
    return dict(rel_place_auc=float(np.mean(aucs)), n_query=len(aucs))


def _emb_digest(emb):
    return hashlib.sha256(np.ascontiguousarray(emb.astype(np.float32)).tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# One seed
# ---------------------------------------------------------------------------
def run_seed(seed, split, feats, landmarks, target_geo, lex_labels, cfg):
    c = cfg
    arm_codes = {}

    # PRIMARY: full fusion (grounding + gloss + relctx) + geometry + relpred + gloss-pred + EMA
    enc = train_self_teacher(feats, target_geo, landmarks, split, c, seed,
                             use_ctx=True, use_gloss=True,
                             w_rel=c["w_rel"], w_gloss=c["w_gloss"], w_ema=c["w_ema"], do_train=True)
    arm_codes[PRIMARY_ARM] = encode_all(enc, feats)

    # GROUNDING_ONLY_LEARN: R1 geometry, grounding-only input (prior +0.0009 arm)
    enc_go = train_self_teacher(feats, target_geo, landmarks, split, c, seed + 21,
                                use_ctx=False, use_gloss=False,
                                w_rel=0.0, w_gloss=0.0, w_ema=0.0, do_train=True)
    arm_codes[GROUND_ONLY_ARM] = encode_all(enc_go, feats)

    # PLUS_GLOSS_LEARN: grounding+gloss input + geometry + masked-gloss prediction (no relpred/EMA)
    enc_pg = train_self_teacher(feats, target_geo, landmarks, split, c, seed + 33,
                                use_ctx=False, use_gloss=True,
                                w_rel=0.0, w_gloss=c["w_gloss"], w_ema=0.0, do_train=True)
    arm_codes[PLUS_GLOSS_ARM] = encode_all(enc_pg, feats)

    # PLUS_RELPRED_LEARN: grounding input + geometry + relational-prediction (no gloss/EMA)
    enc_pr = train_self_teacher(feats, target_geo, landmarks, split, c, seed + 45,
                                use_ctx=False, use_gloss=False,
                                w_rel=c["w_rel"], w_gloss=0.0, w_ema=0.0, do_train=True)
    arm_codes[PLUS_REL_ARM] = encode_all(enc_pr, feats)

    # RAW baselines (no learning)
    arm_codes[RAW_ARM] = _l2_np(feats["own"].astype(np.float64)).astype(np.float32)
    arm_codes[RAWGLOSS_ARM] = _l2_np(feats["gloss"].astype(np.float64) + 1e-9).astype(np.float32)

    # RANDOM_INIT: untrained full encoder
    enc_r = train_self_teacher(feats, target_geo, landmarks, split, c, seed + 101,
                               use_ctx=True, use_gloss=True,
                               w_rel=c["w_rel"], w_gloss=c["w_gloss"], w_ema=c["w_ema"], do_train=False)
    arm_codes[RANDINIT_ARM] = encode_all(enc_r, feats)

    # COLLAPSE_SHUFFLE: permute ALL input rows across ids, train full objective -> ~0.5 witness
    enc_s = train_self_teacher(feats, target_geo, landmarks, split, c, seed + 1,
                               use_ctx=True, use_gloss=True,
                               w_rel=c["w_rel"], w_gloss=c["w_gloss"], w_ema=c["w_ema"],
                               do_train=True, shuffle_rows=True)
    # encode the shuffled arm on the SAME shuffled inputs it trained on
    Kk = split["K"]
    perm = np.random.default_rng(seed + 1 + 909).permutation(Kk)
    feats_shuf = dict(own=feats["own"][perm], ctx=feats["ctx"][perm], gloss=feats["gloss"][perm])
    arm_codes[SHUFFLE_ARM] = encode_all(enc_s, feats_shuf)

    arm_metrics = {}
    for arm in ALL_ARMS:
        ev = eval_semantic_neighbourhood(arm_codes[arm], split, lex_labels, k=10)
        rp = eval_relational_placement(arm_codes[arm], split)
        ev["rel_place_auc"] = rp["rel_place_auc"]
        ev["emb_digest"] = _emb_digest(arm_codes[arm])
        arm_metrics[arm] = ev
        _log("seed=%d arm=%s same_lex_auc=%.4f rel_place_auc=%.4f prec@10=%.4f rec@1=%.4f base=%.4f n_q=%d"
             % (seed, arm, ev["same_lex_auc"], ev["rel_place_auc"], ev["precision_at_k"],
                ev["recall_at_1"], ev["category_base_rate"], ev["n_query"]))

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
            rel_place_auc_mean=float(np.nanmean(series(arm, "rel_place_auc"))),
            precision_at_k_mean=float(series(arm, "precision_at_k").mean()),
            recall_at_1_mean=float(series(arm, "recall_at_1").mean()),
            category_base_rate_mean=float(series(arm, "category_base_rate").mean()),
            n_seeds=len(per_seed),
        )

    st = agg[PRIMARY_ARM]["same_lex_auc_mean"]
    st_min = agg[PRIMARY_ARM]["same_lex_auc_min"]
    ground_only = agg[GROUND_ONLY_ARM]["same_lex_auc_mean"]
    plus_gloss = agg[PLUS_GLOSS_ARM]["same_lex_auc_mean"]
    plus_rel = agg[PLUS_REL_ARM]["same_lex_auc_mean"]
    raw = agg[RAW_ARM]["same_lex_auc_mean"]
    raw_gloss = agg[RAWGLOSS_ARM]["same_lex_auc_mean"]
    randinit = agg[RANDINIT_ARM]["same_lex_auc_mean"]
    shuf = agg[SHUFFLE_ARM]["same_lex_auc_mean"]
    base_rate = agg[RAW_ARM]["category_base_rate_mean"]

    # THE NUMBER: SELF_TEACHER - RAW_GROUNDING (per-seed for robustness)
    margin_series = (series(PRIMARY_ARM, "same_lex_auc") - series(RAW_ARM, "same_lex_auc"))
    margin_raw = float(margin_series.mean())
    margin_raw_min = float(margin_series.min())

    # ablation attribution (all vs the raw-grounding ceiling)
    gain_gloss_input = raw_gloss - raw           # raw gloss input alone (no learning) vs grounding
    gain_ground_learn = ground_only - raw        # learning on grounding alone (prior +0.0009)
    gain_plus_gloss = plus_gloss - raw           # + gloss input+prediction
    gain_plus_rel = plus_rel - raw               # + relational-prediction
    gain_full = st - raw                          # full self-teacher (== margin_raw)
    margin_over_randinit = st - randinit

    cb_lo, cb_hi = COLLAPSE_BAND
    can_fail_fired = bool(cb_lo <= shuf <= cb_hi)
    raw_signal_ok = bool(raw >= RAW_SIGNAL_MIN)
    n_query = int(np.min(series(PRIMARY_ARM, "n_query")))
    power_ok = bool(n_query >= MIN_QUERY_TASKS)

    real_margin = bool(margin_raw >= HP_MARGIN_OVER_RAW and margin_raw_min > 0.0)
    hard_pass = bool(can_fail_fired and raw_signal_ok and power_ok and real_margin
                     and st >= HP_SELF_TEACHER_SIGNAL and st >= randinit)
    hard_fail = bool((not can_fail_fired) or (not raw_signal_ok) or (st < HF_AUC) or (not power_ok))

    if hard_pass:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        # SELF_TEACHER is a real held-out signal + controls valid, but the margin OVER RAW GROUNDING is
        # below the real-margin bar -> honest DEEPER-CEILING finding (gloss-text + relational-predictive
        # still tie raw grounding). Reported plainly per the Director contract.
        verdict = "MIDDLE_BAND"

    deeper_ceiling = bool(verdict == "MIDDLE_BAND" and margin_raw < HP_MARGIN_OVER_RAW)

    verdict_msg = (
        "%s | THE-NUMBER self_teacher - raw_grounding = %.4f - %.4f = %+.4f (min=%+.4f, need>=%.2f, "
        "n_q=%d power_ok=%s) | SELF_TEACHER same_lex_auc=%.4f (min=%.4f) rel_place_auc=%.4f prec@10=%.4f rec@1=%.4f | "
        "ABLATION vs raw_grounding=%.4f: raw_gloss=%.4f(%+.4f) ground_only_learn=%.4f(%+.4f) "
        "plus_gloss=%.4f(%+.4f) plus_relpred=%.4f(%+.4f) FULL(%+.4f) | "
        "RANDOM_INIT=%.4f (st-randinit=%+.4f) COLLAPSE_shuffle=%.4f -> can_fail=%s raw_signal_ok=%s | "
        "category_base_rate(random floor)=%.4f | deeper_ceiling=%s | "
        "train=%d heldout=%d K=%d pairs=%d rels=%d lexnames=%d gloss_cov=%.3f"
        % (verdict, st, raw, margin_raw, margin_raw_min, HP_MARGIN_OVER_RAW, n_query, power_ok,
           st, st_min, agg[PRIMARY_ARM]["rel_place_auc_mean"],
           agg[PRIMARY_ARM]["precision_at_k_mean"], agg[PRIMARY_ARM]["recall_at_1_mean"],
           raw, raw_gloss, gain_gloss_input, ground_only, gain_ground_learn,
           plus_gloss, gain_plus_gloss, plus_rel, gain_plus_rel, gain_full,
           randinit, margin_over_randinit, shuf, can_fail_fired, raw_signal_ok,
           base_rate, deeper_ceiling,
           split_meta["n_train"], split_meta["n_heldout"], data_meta["n_kept_concepts"],
           data_meta["n_kept_pairs"], data_meta["n_rel_slots"], data_meta["n_lexnames"],
           data_meta.get("gloss_coverage", float("nan"))))

    gates = dict(
        self_teacher_same_lex_auc=st, self_teacher_same_lex_auc_min=st_min,
        self_teacher_rel_place_auc=agg[PRIMARY_ARM]["rel_place_auc_mean"],
        grounding_only_learn_same_lex_auc=ground_only,
        plus_gloss_learn_same_lex_auc=plus_gloss, plus_relpred_learn_same_lex_auc=plus_rel,
        raw_grounding_same_lex_auc=raw, raw_gloss_same_lex_auc=raw_gloss,
        random_init_same_lex_auc=randinit, collapse_shuffle_same_lex_auc=shuf,
        margin_over_raw_grounding=margin_raw, margin_over_raw_grounding_min=margin_raw_min,
        margin_over_random_init=margin_over_randinit,
        ablation_gain_gloss_input=gain_gloss_input, ablation_gain_ground_learn=gain_ground_learn,
        ablation_gain_plus_gloss=gain_plus_gloss, ablation_gain_plus_relpred=gain_plus_rel,
        ablation_gain_full=gain_full,
        category_base_rate=base_rate,
        can_fail_fired=can_fail_fired, raw_signal_ok=raw_signal_ok, power_ok=power_ok, n_query=n_query,
        deeper_ceiling=deeper_ceiling, real_margin=real_margin,
        collapse_band=list(COLLAPSE_BAND), hp_self_teacher_signal=HP_SELF_TEACHER_SIGNAL,
        hf_auc=HF_AUC, hp_margin_over_raw=HP_MARGIN_OVER_RAW, raw_signal_min=RAW_SIGNAL_MIN,
        min_query_tasks=MIN_QUERY_TASKS,
        self_teacher_precision_at_10=agg[PRIMARY_ARM]["precision_at_k_mean"],
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
    n_cat, per, d = 6, 50, 16
    K = n_cat * per
    cat = np.repeat(np.arange(n_cat), per).astype(np.int64)
    centers = rng.standard_normal((n_cat, d))
    struct = _l2_np(centers[cat] + 0.15 * rng.standard_normal((K, d))).astype(np.float32)
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
               auc_label_shuffle=ev_shuf["same_lex_auc"], prec_struct=ev_struct["precision_at_k"],
               base_rate=ev_struct["category_base_rate"], n_query=ev_struct["n_query"])
    ok = (ev_struct["same_lex_auc"] >= 0.85
          and abs(ev_rand["same_lex_auc"] - 0.5) < 0.10
          and abs(ev_shuf["same_lex_auc"] - 0.5) < 0.10
          and ev_struct["precision_at_k"] > ev_struct["category_base_rate"] + 0.2)
    return bool(ok), res


def gloss_bag_selftest():
    """Proves the glass-box gloss encoder INPUT is teacher-free + discriminative: two animal glosses share
    more trigram-bucket mass than an animal vs a number gloss. Deterministic hashing (reproducible)."""
    V = 2048
    a1 = _gloss_bag("a domesticated carnivorous mammal with four legs and a tail", V)
    a2 = _gloss_bag("a wild carnivorous mammal of the cat family with four legs", V)
    n1 = _gloss_bag("the cardinal number that is the sum of six and one", V)
    sim_aa = float(a1 @ a2)
    sim_an = float(a1 @ n1)
    ok = bool(sim_aa > sim_an and sim_aa > 0.0)
    return ok, dict(sim_animal_animal=sim_aa, sim_animal_number=sim_an, vocab=V)


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
    g_ok, g_res = gloss_bag_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    _log("gloss_bag_selftest ok=%s %s" % (g_ok, g_res))
    if not (st_ok and g_ok):
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="SELFTEST_FAILED discriminator_ok=%s gloss_ok=%s: %s | %s"
                        % (st_ok, g_ok, st_res, g_res),
            summary="selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, gloss_bag_selftest=g_res))
        raise SystemExit(1)

    _log("loading grounded subgraph (min_deg=%d cap=%d top_rel=%d vocab=%d)..."
         % (cfg["min_deg"], cfg["cap_nodes"], cfg["top_rel"], cfg["gloss_vocab"]))
    data = load_grounded_subgraph(cfg)
    _log("grounded universe: %s" % {k: v for k, v in data["meta"].items() if k != "top_rels"})
    split = build_split(data, cfg)
    _log("split: %s" % split["split_meta"])
    feats = build_features(split, data)
    landmarks = select_landmarks(split, cfg)
    A = build_train_adjacency(split)
    own_norm = _l2_np(feats["own"].astype(np.float64)).astype(np.float32)
    target_geo = compute_target_geometry(own_norm, A, landmarks)
    _log("landmarks=%d own_dim=%d ctx_dim=%d gloss_dim=%d target_geo shape=%s tgeo_mean=%.4f tgeo_std=%.4f"
         % (landmarks.shape[0], feats["own"].shape[1], feats["ctx"].shape[1], feats["gloss"].shape[1],
            target_geo.shape, float(target_geo.mean()), float(target_geo.std())))

    if run_mode == "self_test":
        pm = run_seed(cfg["seeds"][0], split, feats, landmarks, target_geo, data["lex_labels"], cfg)
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS discriminator + gloss-bag + end-to-end held-out eval exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, gloss_bag_selftest=g_res,
            data_meta=data["meta"], split_meta=split["split_meta"],
            self_teacher_same_lex_auc=pm[PRIMARY_ARM]["same_lex_auc"],
            raw_grounding_same_lex_auc=pm[RAW_ARM]["same_lex_auc"],
            raw_gloss_same_lex_auc=pm[RAWGLOSS_ARM]["same_lex_auc"],
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
        gates=gates, arms_aggregate=agg, discriminator_selftest=st_res, gloss_bag_selftest=g_res,
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
