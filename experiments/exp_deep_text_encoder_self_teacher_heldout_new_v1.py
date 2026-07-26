"""DEEP from-scratch TEXT ENCODER self-teacher, judged on held-out-NEW-concept generalization.

WHY (THE_PLAN R3/R4 -> deeper encoder lever):
  R3/R4 (MEASURED@data/exp_self_teacher_gloss_relational_predictive_heldout_new_v1/metrics.json)
  showed the CHAR-TRIGRAM gloss encoder is TOO SHALLOW: the gloss arm (grounding + char-trigram BAG
  + masked-gloss BCE) added only +0.0070 over RAW-GROUNDING (0.6431 vs 0.6361 same_lex_auc), and the
  full self-teacher TIED/slightly-lost raw grounding (-0.0105). A char-trigram BAG captures surface
  morphology, not compositional meaning, and a 10-word gloss is little text. This cell fixes BOTH:
    (a) a DEEP, from-scratch, learned SEQUENCE text encoder (learned token embeddings + a small
        Transformer, MLM-trained by MASKED-TOKEN PREDICTION over the concept text) that REPLACES the
        char-trigram bag; and
    (b) MORE + LONGER real text per concept (WordNet gloss + WordNet examples + mined UD-English-EWT
        sentences that mention the concept surface), not just a 10-word gloss.
  THE QUESTION: does DEPTH + MORE TEXT extract more meaning than the +0.0070 shallow ceiling, and does
  the full fusion BREAK the RAW-GROUNDING ceiling (>= +0.03) on held-out-NEW concepts?

THE DEEP TEXT ENCODER (from scratch, teacher-free, glass-box):
  Tokenizer: WORD tokens (regex [a-z]+), each hashed (sha256) to one of V_tok buckets -> VOCAB-FREE,
    fit-free -> fully INDUCTIVE + leak-proof (no train-fit vocab). PAD=0, MASK=1 reserved.
  Model: LEARNED token embedding table [V_tok, d_model] (random init, NO pretrained vectors) + learned
    positional embeddings + a small torch.nn.TransformerEncoder (n_layers, n_heads). From scratch.
  Objective: MASKED-LANGUAGE-MODELLING (BERT-style). Mask MLM_MASK_FRAC of non-pad tokens; a tied MLM
    head predicts the original hashed token id (cross-entropy over masked positions). Trained ONLY on
    TRAIN concepts' text (held-out text never shapes the encoder params -> leak-proof generalization).
  Concept text-rep: mean-pool the trained encoder's non-pad contextual token embeddings -> [K, d_model],
    L2-normed. Held-out concepts are encoded INDUCTIVELY by the frozen trained encoder (no per-concept
    lookup, never a training target).

THE SELF-TEACHER (reused from R3/R4, teacher-free): R1 landmark geometry (match code-vs-landmark cosine
  profile to a teacher-free grounding+relational target) + VICReg anti-collapse + R4 relational-prediction
  InfoNCE (predict your TRAIN relational neighbours) + EMA self-distillation. The deep-text-rep enters as
  an INPUT branch of the fusion encoder (replacing the char-trigram branch in the DEEP arms).

HARD INVARIANTS (project locks):
  - TEACHER-FREE. NO GloVe/BGE/transformer WEIGHTS/borrowed vector ANYWHERE. Token embeddings + the
    Transformer are LEARNED FROM SCRATCH by MLM. Inputs are ONLY measured grounding norms + the
    foundation's own relational graph + WordNet gloss/example STRINGS + mined generic-English sentences,
    all encoded by OUR OWN learned encoder. WordNet lexname (supersense) is EVAL-ONLY truth.
  - INDUCTIVE: a held-out NEW concept is placed from its features (grounding + its own text + its known
    TRAIN-neighbour relational context) -> code; never a per-concept lookup. Held-out is never a
    landmark / training anchor / InfoNCE positive / MLM training example.
  - LEAK-PROOF held-out-NEW: concept-level split (sha256 on id, PYTHONHASHSEED-independent). Tokenizer is
    vocab-free hashing (no fit). MLM trains on TRAIN text only. Relational context restricted to TRAIN
    neighbours. Supersense truth disjoint from every input/target. RAW baselines share the SAME inputs.

TEST (held-out-NEW concepts, measured FAIRLY):
  (a) WordNet SAME-LEXNAME (supersense) semantic-neighbourhood AUC. Base = 0.5 exactly.
  (b) DEGREE-MATCHED relational-placement AUC: positives = the query's true TRAIN neighbours; negatives
      = TRAIN non-neighbours MATCHED to the positives' train-degree distribution (kills the popularity /
      random-neg confound that inflated random-neg rel_place to ~0.80 in R3/R4). Random-neg AUC also
      reported for contrast.

THE ONE NUMBER (Director contract): FULL_FUSION same_lex_auc MINUS RAW_GROUNDING same_lex_auc on
  held-out-NEW concepts (>= +0.03, min>0 => break the ceiling). KEY ablation: DEEP_TEXT vs
  CHARTRIGRAM_GLOSS (does DEPTH extract more than the +0.0070 shallow bag?). If the DEEP encoder STILL
  ties raw grounding, that is a MAJOR honest finding (a data-scale / grounding-saturation ceiling)
  reported as MIDDLE_BAND with the corpus scale stated plainly.

ABLATION ARMS:
  ARM_RAW_GROUNDING     : cosine over raw grounding (20d), NO learning.            [THE ceiling to break]
  ARM_RAW_DEEPTEXT      : cosine over the MLM-pretrained deep-text-rep, NO fusion. [signal in deep text?]
  ARM_CHARTRIGRAM_GLOSS : grounding + char-trigram BAG branch + geometry + masked-gloss BCE (R3/R4 shallow).
  ARM_DEEP_TEXT         : grounding + DEEP-text-rep branch + geometry + EMA.        [DEPTH; key vs chartrigram]
  ARM_FULL_FUSION       : grounding + deep-text + relational-ctx + geometry + relpred + EMA. [PRIMARY]
  ARM_RANDOM_INIT       : untrained fusion + un-MLM'd (random) deep-text encoder.   [isolate learning]
  ARM_COLLAPSE_SHUFFLE  : input rows permuted across ids, trained -> ~0.5.          [CAN-FAIL / leak witness]

CAN-FAIL GATE: ARM_COLLAPSE_SHUFFLE must sit ~0.5. RAW_GROUNDING must be a real >0.55 signal.
DEFLATE: FULL_FUSION merely tying RAW_GROUNDING = honest deeper/data-scale ceiling -> MIDDLE_BAND.

CPU-only. No GPU. No network at run time (WordNet from local NLTK cache; UD-EWT local on disk). ASCII-only.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test over code arms)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator has base=0.5 exactly; collapse + random-init controls witness the floor
# - baseline_in_band at smoke: collapse ~0.5; raw-grounding a real >0.55 signal; primary not saturated
# - discriminator survives scale: FULL runs on remote_cpu (>=2 seeds); smoke previews the number
# - HARD_PASS strictly above floor: full_fusion_auc>=0.60 AND (full-raw)>=0.03 AND margin_min>0
#   AND full>=random_init AND can_fail(collapse ~0.5)
# - HP_SCOPE: gates apply to ARM_FULL_FUSION (primary) only
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; controls witness it empirically)
# - deterministic seeding: sha256 concept split + sha256 token/gloss hash + fixed int seeds + sorted(); no hash()/list(set())
# - no substrate KGStore/fit objects (self-contained jsonl reader + NLTK + torch) -> F.1/F.2 real_code_path N/A
# - progress_logging: print_flush_true (MLM + fusion epoch logs flush=True)
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

ANCHOR_NAME = "deep_text_encoder_self_teacher_heldout_new_v1"
FOUNDATION_DIR = os.path.join(_REPO, "data", "cskg_foundation_v1")
NODES_PATH = os.path.join(FOUNDATION_DIR, "nodes.jsonl")
EDGES_GLOB = os.path.join(FOUNDATION_DIR, "edges_shard_*.jsonl")
LEXNAME_CACHE = os.path.join(_REPO, "data", "wordnet_lexname_cache_v1.json")
GLOSS_CACHE = os.path.join(_REPO, "data", "wordnet_gloss_cache_v1.json")
EXAMPLES_CACHE = os.path.join(_REPO, "data", "wordnet_examples_cache_v1.json")
UD_EWT_CONLLU = os.path.join(_REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")

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
    min_deg=2, cap_nodes=400, seeds=[7], heldout_frac=0.2, top_rel=8,
    # fusion self-teacher
    epochs=20, batch=128, code_dim=32, hidden=64, lr=5e-3,
    n_landmarks=64, n_land_batch=48, n_anchor_batch=96,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1,
    # char-trigram (shallow baseline) branch
    tri_vocab=512, tri_proj=32, gloss_mask_frac=0.3, w_trigram_pred=0.5,
    # deep text encoder
    tok_vocab=1024, max_len=32, n_mined_sents=3,
    d_model=32, n_layers=2, n_heads=2, ffn_mult=2,
    mlm_epochs=15, mlm_batch=64, mlm_mask_frac=0.15, mlm_lr=3e-3, text_proj=32,
)
SMOKE_CFG = dict(
    min_deg=2, cap_nodes=900, seeds=[7], heldout_frac=0.2, top_rel=16,
    epochs=90, batch=256, code_dim=128, hidden=256, lr=3e-3,
    n_landmarks=192, n_land_batch=128, n_anchor_batch=256,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1,
    tri_vocab=2048, tri_proj=64, gloss_mask_frac=0.3, w_trigram_pred=0.5,
    tok_vocab=4096, max_len=64, n_mined_sents=6,
    d_model=96, n_layers=2, n_heads=3, ffn_mult=2,
    mlm_epochs=60, mlm_batch=128, mlm_mask_frac=0.15, mlm_lr=3e-3, text_proj=64,
)
FULL_CFG = dict(
    min_deg=2, cap_nodes=5000, seeds=[7, 13], heldout_frac=0.2, top_rel=16,
    epochs=150, batch=256, code_dim=128, hidden=256, lr=2.5e-3,
    n_landmarks=512, n_land_batch=192, n_anchor_batch=256,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1,
    tri_vocab=2048, tri_proj=64, gloss_mask_frac=0.3, w_trigram_pred=0.5,
    tok_vocab=8192, max_len=96, n_mined_sents=8,
    d_model=128, n_layers=2, n_heads=4, ffn_mult=2,
    mlm_epochs=140, mlm_batch=256, mlm_mask_frac=0.15, mlm_lr=2.5e-3, text_proj=96,
)

# Deterministic salts / seeds
CONCEPT_SPLIT_SALT = "deep_text_enc_v1_concept_split::"
TOKEN_HASH_SALT = "deep_text_enc_v1_tok::"
EVAL_SEED = 20260726
PAD_ID = 0
MASK_ID = 1
N_SPECIAL = 2

# Pre-reg bands (applied to ARM_FULL_FUSION primary held-out SAME-LEXNAME AUC).
HP_FULL_SIGNAL = 0.60             # FULL must be a genuine held-out signal well above chance 0.5
HF_AUC = 0.53                     # below this = essentially chance = HARD_FAIL
HP_MARGIN_OVER_RAW = 0.03         # THE NUMBER: FULL - RAW_GROUNDING must exceed this (break the ceiling)
COLLAPSE_BAND = (0.44, 0.56)      # ARM_COLLAPSE_SHUFFLE MUST sit here (can-fail witness)
RAW_SIGNAL_MIN = 0.55             # RAW_GROUNDING must be a real >0.55 signal (metric-not-saturated gate)
MIN_QUERY_TASKS = 150             # power floor for the held-out AUC to be trustworthy
DEPTH_HELPS_EPS = 0.0             # DEEP_TEXT - CHARTRIGRAM_GLOSS; report; >0 => depth extracts more

# Arms
RAW_ARM = "ARM_RAW_GROUNDING"
RAW_DEEP_ARM = "ARM_RAW_DEEPTEXT"
TRIGRAM_ARM = "ARM_CHARTRIGRAM_GLOSS"
DEEP_ARM = "ARM_DEEP_TEXT"
FULL_ARM = "ARM_FULL_FUSION"
RANDINIT_ARM = "ARM_RANDOM_INIT"
SHUFFLE_ARM = "ARM_COLLAPSE_SHUFFLE"
PRIMARY_ARM = FULL_ARM
ALL_ARMS = [RAW_ARM, RAW_DEEP_ARM, TRIGRAM_ARM, DEEP_ARM, FULL_ARM, RANDINIT_ARM, SHUFFLE_ARM]


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
# WordNet lexname (EVAL truth) + gloss + examples (text INPUT)
# ---------------------------------------------------------------------------
def _dominant_synset(wn, surface):
    for cand in (surface.replace(" ", "_"), surface.replace(" ", ""), surface.split(" ")[0]):
        if not cand:
            continue
        try:
            ss = wn.synsets(cand)
        except Exception:  # noqa: BLE001 -- NLTK lookup hiccup on one token: try next candidate
            ss = []
        if ss:
            return ss[0]
    return None


def _load_json_cache(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (ValueError, OSError):
            return {}
    return {}


def _save_json_cache(path, cache):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f)
    os.replace(tmp, path)


def _build_lexname_text_maps(surfaces):
    """Return ({surface: lexname or None}, {surface: gloss str}, {surface: [example strs]}).
    lexname = EVAL-ONLY truth; gloss + examples = text INPUT. All from the dominant (first) synset.
    Cached to disk (idempotent). NLTK-local only."""
    lex_cache = _load_json_cache(LEXNAME_CACHE)
    gloss_cache = _load_json_cache(GLOSS_CACHE)
    ex_cache = _load_json_cache(EXAMPLES_CACHE)
    need = [s for s in surfaces
            if (s not in lex_cache) or (s not in gloss_cache) or (s not in ex_cache)]
    if need:
        try:
            from nltk.corpus import wordnet as wn
        except ImportError as e:
            raise RuntimeError("NLTK WordNet required for EVAL-ONLY lexname + gloss/example INPUT. "
                               "Install nltk + wordnet data.") from e
        for s in need:
            ss = _dominant_synset(wn, s)
            lex_cache[s] = ss.lexname() if ss is not None else None
            gloss_cache[s] = ss.definition() if ss is not None else ""
            try:
                ex_cache[s] = list(ss.examples()) if ss is not None else []
            except Exception:  # noqa: BLE001 -- some synsets have no examples attr; empty list is fine
                ex_cache[s] = []
        _save_json_cache(LEXNAME_CACHE, lex_cache)
        _save_json_cache(GLOSS_CACHE, gloss_cache)
        _save_json_cache(EXAMPLES_CACHE, ex_cache)
    return ({s: lex_cache.get(s) for s in surfaces},
            {s: gloss_cache.get(s, "") for s in surfaces},
            {s: ex_cache.get(s, []) for s in surfaces})


# ---------------------------------------------------------------------------
# UD-English-EWT sentence mining (MORE + LONGER real text per concept)
# ---------------------------------------------------------------------------
_WORD_RE = re.compile(r"[a-z]+")


def _load_ewt_index(max_postings=64):
    """Parse UD-EWT train conllu into (sentences:list[str], token_index:dict lemma->sorted[sent_idx]).
    Sentences are reconstructed from the FORM column, lowercased. Inverted index keyed by lowercased
    LEMMA + FORM, postings capped for bounded lookup. Deterministic. Returns ([], {}) if file absent."""
    if not os.path.exists(UD_EWT_CONLLU):
        return [], {}
    sentences = []
    index = {}
    cur_forms = []
    cur_keys = set()

    def _flush():
        if cur_forms:
            sidx = len(sentences)
            sentences.append(" ".join(cur_forms))
            for k in cur_keys:
                lst = index.setdefault(k, [])
                if len(lst) < max_postings:
                    lst.append(sidx)

    with open(UD_EWT_CONLLU, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                _flush()
                cur_forms = []
                cur_keys = set()
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) < 3:
                continue
            if "-" in cols[0] or "." in cols[0]:   # multiword-token range / empty-node rows
                continue
            form = cols[1].strip().lower()
            lemma = cols[2].strip().lower()
            if form:
                cur_forms.append(cols[1])
                for w in _WORD_RE.findall(form):
                    cur_keys.add(w)
            for w in _WORD_RE.findall(lemma):
                cur_keys.add(w)
    _flush()
    # sort postings for determinism
    for k in index:
        index[k] = sorted(index[k])
    return sentences, index


def _mine_sentences(surface, sentences, index, n_max):
    """Up to n_max EWT sentences mentioning the surface's head token. Deterministic (sorted postings)."""
    if not sentences or n_max <= 0:
        return []
    toks = _WORD_RE.findall(surface.replace("_", " ").lower())
    if not toks:
        return []
    head = toks[-1]        # head token (last word of a phrase)
    posts = index.get(head)
    if not posts:
        return []
    return [sentences[i] for i in posts[:n_max]]


def build_concept_text(surface, gloss, examples, sentences, index, n_mined):
    """Concatenate gloss + WordNet examples + mined EWT sentences into one text string per concept."""
    parts = []
    if gloss:
        parts.append(gloss)
    for ex in examples:
        if ex:
            parts.append(ex)
    parts.extend(_mine_sentences(surface, sentences, index, n_mined))
    return " . ".join(parts)


# ---------------------------------------------------------------------------
# From-scratch tokenizer (vocab-free hashing) + char-trigram bag (shallow baseline INPUT)
# ---------------------------------------------------------------------------
def _tok_id(word, tok_vocab):
    """Hash a word to a token id in [N_SPECIAL, tok_vocab). Vocab-free -> inductive, deterministic."""
    b = hashlib.sha256((TOKEN_HASH_SALT + word).encode("utf-8")).digest()[:4]
    return N_SPECIAL + (int.from_bytes(b, "big") % (tok_vocab - N_SPECIAL))


def tokenize_text(text, tok_vocab, max_len):
    """Word tokens -> hashed ids, truncated/padded to max_len. Returns (ids[max_len], length)."""
    ids = np.full(max_len, PAD_ID, dtype=np.int64)
    words = _WORD_RE.findall(text.lower())
    n = 0
    for w in words:
        if n >= max_len:
            break
        ids[n] = _tok_id(w, tok_vocab)
        n += 1
    return ids, n


def _tri_bag(text, vocab):
    """Bag of char-trigram HASH buckets for one text (the R3/R4 SHALLOW encoder input). L2-normed."""
    vec = np.zeros(vocab, dtype=np.float32)
    if not text:
        return vec
    for tok in _WORD_RE.findall(text.lower()):
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
# Foundation loader: grounded induced subgraph + lexname truth + concept text
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
    """Load grounded concepts WITH a WordNet lexname + concept text + induced relational subgraph."""
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

    lexmap, glossmap, exmap = _build_lexname_text_maps(surf_list)
    has_lex = [i for i in range(len(gid_list)) if lexmap[surf_list[i]] is not None]
    if len(has_lex) < 100:
        raise RuntimeError("too few grounded nodes with a WordNet lexname (%d)" % len(has_lex))

    gid_list = [gid_list[i] for i in has_lex]
    surf_list = [surf_list[i] for i in has_lex]
    raw_vals = [raw_vals[i] for i in has_lex]
    raw_gpres = [raw_gpres[i] for i in has_lex]
    lex_list = [lexmap[s] for s in surf_list]
    gloss_list = [glossmap[s] for s in surf_list]
    ex_list = [exmap[s] for s in surf_list]

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
    examples = [ex_list[o] for o in kept]
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

    # Build concept text (gloss + examples + mined EWT sentences) + tokenize + char-trigram bag
    _log("mining UD-EWT sentences (n_mined=%d/concept)..." % cfg["n_mined_sents"])
    sentences, index = _load_ewt_index()
    _log("EWT corpus: %d sentences, %d indexed tokens" % (len(sentences), len(index)))

    tok_vocab = cfg["tok_vocab"]
    max_len = cfg["max_len"]
    tri_vocab = cfg["tri_vocab"]
    tok_ids = np.full((K, max_len), PAD_ID, dtype=np.int64)
    tok_len = np.zeros(K, dtype=np.int64)
    tri_bag = np.zeros((K, tri_vocab), dtype=np.float32)
    total_tokens = 0
    n_mined_total = 0
    n_text_nonempty = 0
    text_char_total = 0
    for i in range(K):
        mined = _mine_sentences(surfaces[i], sentences, index, cfg["n_mined_sents"])
        n_mined_total += len(mined)
        text = build_concept_text(surfaces[i], glosses[i], examples[i], sentences, index,
                                  cfg["n_mined_sents"])
        if text.strip():
            n_text_nonempty += 1
        text_char_total += len(text)
        tids, n = tokenize_text(text, tok_vocab, max_len)
        tok_ids[i] = tids
        tok_len[i] = n
        total_tokens += n
        tri_bag[i] = _tri_bag(text, tri_vocab)

    uniq_lex = sorted(set(lexnames))
    lex_to_int = {lx: i for i, lx in enumerate(uniq_lex)}
    lex_labels = np.array([lex_to_int[lx] for lx in lexnames], dtype=np.int64)

    meta = dict(
        n_grounded_total=n_all, n_induced_pairs_total=len(pair_rels),
        n_kept_concepts=K, n_kept_pairs=len(kept_pair_rels),
        min_deg=cfg["min_deg"], cap_nodes=cfg["cap_nodes"],
        top_rels=top_rels, n_rel_slots=R, n_lexnames=len(uniq_lex),
        tok_vocab=tok_vocab, max_len=max_len, tri_vocab=tri_vocab,
        ewt_sentences=len(sentences), n_mined_total=n_mined_total,
        mean_mined_per_concept=float(n_mined_total) / float(K),
        text_nonempty=n_text_nonempty, text_coverage=float(n_text_nonempty) / float(K),
        total_tokens_used=int(total_tokens), mean_tokens_per_concept=float(total_tokens) / float(K),
        mean_text_chars=float(text_char_total) / float(K),
    )
    return dict(ids=ids, surfaces=surfaces, vals=vals, gpres=gpres,
                tok_ids=tok_ids, tok_len=tok_len, tri_bag=tri_bag,
                pair_rels=kept_pair_rels, K=K, R=R, rel_slot=_rel_slot,
                lex_labels=lex_labels, uniq_lex=uniq_lex, meta=meta)


# ---------------------------------------------------------------------------
# Split + standardize + typed TRAIN-neighbour context + relpred positives
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

    ctx_nei_by_rel = [dict() for _ in range(K)]
    train_neigh = [set() for _ in range(K)]
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


# ---------------------------------------------------------------------------
# DEEP TEXT ENCODER (from scratch): learned token emb + Transformer, MLM-pretrained
# ---------------------------------------------------------------------------
class DeepTextEncoder(torch.nn.Module):
    def __init__(self, tok_vocab, max_len, d_model, n_layers, n_heads, ffn_mult):
        super().__init__()
        self.tok_emb = torch.nn.Embedding(tok_vocab, d_model, padding_idx=PAD_ID)
        self.pos_emb = torch.nn.Embedding(max_len, d_model)
        layer = torch.nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=ffn_mult * d_model,
            dropout=0.0, activation="gelu", batch_first=True)
        self.enc = torch.nn.TransformerEncoder(layer, num_layers=n_layers)
        self.mlm_head = torch.nn.Linear(d_model, tok_vocab)
        self.max_len = max_len
        self.d_model = d_model
        self._pos_ids = torch.arange(max_len).unsqueeze(0)

    def _contextual(self, ids):
        pad_mask = (ids == PAD_ID)                                   # [B, L] True where PAD
        pos = self._pos_ids[:, :ids.shape[1]].to(ids.device)
        h = self.tok_emb(ids) + self.pos_emb(pos)
        h = self.enc(h, src_key_padding_mask=pad_mask)
        return h, pad_mask

    def mlm_logits(self, ids):
        h, _ = self._contextual(ids)
        return self.mlm_head(h)                                     # [B, L, V]

    def pooled(self, ids):
        """Mean-pool non-pad contextual embeddings -> [B, d_model], L2-normed."""
        h, pad_mask = self._contextual(ids)
        keep = (~pad_mask).float().unsqueeze(-1)                    # [B, L, 1]
        summed = (h * keep).sum(dim=1)
        cnt = keep.sum(dim=1).clamp_min(1.0)
        rep = summed / cnt
        return rep / (rep.norm(dim=1, keepdim=True) + 1e-8)


def mlm_pretrain_deeptext(tok_ids_all, train_idx, cfg, seed):
    """MLM-pretrain the deep text encoder on TRAIN concepts' text ONLY. Returns (encoder, final_loss).
    Held-out text never shapes the params. BERT-style 15% masking; CE over masked positions."""
    torch.manual_seed(seed)
    tok_vocab = cfg["tok_vocab"]
    max_len = cfg["max_len"]
    enc = DeepTextEncoder(tok_vocab, max_len, cfg["d_model"], cfg["n_layers"],
                          cfg["n_heads"], cfg["ffn_mult"])
    X = torch.from_numpy(tok_ids_all).long()
    tr = torch.from_numpy(np.asarray(train_idx, dtype=np.int64))
    opt = torch.optim.Adam(enc.parameters(), lr=cfg["mlm_lr"])
    g = torch.Generator().manual_seed(seed + 5)
    mask_frac = cfg["mlm_mask_frac"]
    bs = min(cfg["mlm_batch"], tr.shape[0])
    n_tr = tr.shape[0]
    log_every = max(1, cfg["mlm_epochs"] // 4)
    last_loss = float("nan")
    t0 = time.perf_counter()
    enc.train()
    for ep in range(cfg["mlm_epochs"]):
        sel = tr[torch.randperm(n_tr, generator=g)[:bs]]
        ids = X[sel].clone()                                        # [bs, L]
        nonpad = (ids != PAD_ID)
        rnd = torch.rand(ids.shape, generator=g)
        mask = nonpad & (rnd < mask_frac)
        if int(mask.sum()) < 1:
            continue
        target = ids.clone()
        inp = ids.clone()
        inp[mask] = MASK_ID
        logits = enc.mlm_logits(inp)                                # [bs, L, V]
        loss = torch.nn.functional.cross_entropy(
            logits[mask], target[mask])
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite MLM loss ep=%d seed=%d" % (ep, seed))
        opt.zero_grad()
        loss.backward()
        opt.step()
        last_loss = float(loss.detach())
        if (ep % log_every == 0) or (ep == cfg["mlm_epochs"] - 1):
            _log("  MLM seed=%d ep=%d/%d loss=%.4f n_mask=%d (%.1fs)"
                 % (seed, ep, cfg["mlm_epochs"], last_loss, int(mask.sum()),
                    time.perf_counter() - t0))
    enc.eval()
    return enc, last_loss


def encode_deeptext_all(enc, tok_ids_all, batch=512):
    """Inductively encode ALL concepts (train + held-out) with the trained (or random) encoder."""
    X = torch.from_numpy(tok_ids_all).long()
    reps = []
    with torch.no_grad():
        for i in range(0, X.shape[0], batch):
            reps.append(enc.pooled(X[i:i + batch]).numpy().astype(np.float32))
    return np.concatenate(reps, axis=0)


# ---------------------------------------------------------------------------
# Fusion encoder (grounding + text branch + relational-ctx) + trigram-reconstruction head
# ---------------------------------------------------------------------------
class FusionEncoder(torch.nn.Module):
    """Text branch input is a fixed precomputed vector: either the deep-text-rep (DEEP arms) OR the
    char-trigram bag (SHALLOW arm). use_text_pred adds a trigram-bag reconstruction head (shallow arm)."""
    def __init__(self, ground_dim, ctx_dim, text_dim, text_proj, hidden, code_dim,
                 use_ctx, use_text, tri_vocab, use_text_pred):
        super().__init__()
        self.use_ctx = use_ctx
        self.use_text = use_text
        self.use_text_pred = use_text_pred
        in_dim = ground_dim
        if use_ctx:
            in_dim += ctx_dim
        if use_text:
            self.text_branch = torch.nn.Sequential(
                torch.nn.Linear(text_dim, text_proj), torch.nn.GELU())
            in_dim += text_proj
        self.net = torch.nn.Sequential(
            torch.nn.Linear(in_dim, hidden), torch.nn.GELU(),
            torch.nn.Linear(hidden, code_dim))
        if use_text_pred:
            self.text_head = torch.nn.Linear(code_dim, tri_vocab)

    def encode(self, ground, ctx, text):
        parts = [ground]
        if self.use_ctx:
            parts.append(ctx)
        if self.use_text:
            parts.append(self.text_branch(text))
        return self.net(torch.cat(parts, dim=1))

    def forward(self, ground, ctx, text):
        return self.encode(ground, ctx, text)


def _l2_np(x, eps=1e-8):
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + eps)


def _l2_t(h, eps=1e-8):
    return h / (h.norm(dim=1, keepdim=True) + eps)


def select_landmarks(split, cfg):
    train_idx = split["train_idx"].tolist()
    train_deg = split["train_deg"]
    ranked = sorted(train_idx, key=lambda i: (-float(train_deg[i]), i))
    L = min(cfg["n_landmarks"], len(ranked))
    return np.array(sorted(ranked[:L]), dtype=np.int64)


def build_train_adjacency(split):
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
    Lm_own = own_norm[landmarks]
    G = own_norm @ Lm_own.T
    Lm_A = A[landmarks]
    shared = A @ Lm_A.T
    deg = np.sqrt((A * A).sum(axis=1) + 1e-6)
    deg_l = deg[landmarks]
    R = shared / (deg[:, None] * deg_l[None, :] + 1e-6)
    T = alpha * _zscore_matrix(G) + (1.0 - alpha) * _zscore_matrix(R)
    return T.astype(np.float32)


# ---------------------------------------------------------------------------
# Fusion self-teacher training (teacher-free geometry + relpred + EMA)
# ---------------------------------------------------------------------------
def _pick_relpred_positive(anchor_ids, train_neigh, rng):
    valid = np.zeros(anchor_ids.shape[0], dtype=bool)
    pos = np.zeros(anchor_ids.shape[0], dtype=np.int64)
    for k, a in enumerate(anchor_ids.tolist()):
        nb = train_neigh[a]
        if nb:
            arr = np.fromiter(sorted(nb), dtype=np.int64, count=len(nb))
            pos[k] = int(arr[rng.integers(0, arr.shape[0])])
            valid[k] = True
    return valid, pos


def train_fusion(feats, target_geo, landmarks, split, cfg, seed,
                 use_ctx, use_text, w_rel, w_ema, use_text_pred,
                 do_train=True, shuffle_rows=False):
    """Train a fusion encoder over precomputed features. feats has own/ctx/text (text = deep-rep OR
    trigram-bag depending on the arm). w_rel/w_ema=0 ablate; do_train=False = random-init;
    shuffle_rows permutes input rows across ids (COLLAPSE witness)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed + 17)

    K = split["K"]
    ground = feats["own"].astype(np.float32)
    ctx = feats["ctx"].astype(np.float32)
    text = feats["text"].astype(np.float32)
    tri = feats["tri"].astype(np.float32)          # trigram bag (target for text-pred head)
    if shuffle_rows:
        perm = np.random.default_rng(seed + 909).permutation(K)
        ground = ground[perm]
        ctx = ctx[perm]
        text = text[perm]
        tri = tri[perm]

    Xg = torch.from_numpy(ground)
    Xc = torch.from_numpy(ctx)
    Xt = torch.from_numpy(text)
    Xtri = torch.from_numpy(tri)
    text_dim = text.shape[1]
    tri_vocab = tri.shape[1]

    enc = FusionEncoder(GROUND_DIM, ctx.shape[1], text_dim, cfg["text_proj"],
                        cfg["hidden"], cfg["code_dim"], use_ctx=use_ctx, use_text=use_text,
                        tri_vocab=tri_vocab, use_text_pred=use_text_pred)
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
    T_all = torch.from_numpy(target_geo.astype(np.float32))
    anchors = np.asarray(split["train_idx"], dtype=np.int64)
    train_neigh = split["train_neigh"]
    nL = landmarks.shape[0]
    fd = cfg["feat_dropout"]
    tau = cfg["infonce_tau"]
    w_text_pred = cfg["w_trigram_pred"] if use_text_pred else 0.0
    mask_frac = cfg["gloss_mask_frac"]
    log_every = max(1, cfg["epochs"] // 4)
    t0 = time.perf_counter()

    def _enc_rows(module, rows, feat_drop=0.0):
        g = Xg[rows]
        c = Xc[rows]
        t = Xt[rows]
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

        rel_loss_val = 0.0
        if w_rel > 0.0:
            valid, pos_j = _pick_relpred_positive(a_idx, train_neigh, rng)
            if valid.sum() >= 4:
                vsel = np.nonzero(valid)[0]
                z_anc = z_a[torch.from_numpy(vsel.astype(np.int64))]
                pos_rows = torch.from_numpy(pos_j[vsel].astype(np.int64))
                z_pos = _l2_t(_enc_rows(enc, pos_rows))
                logits = (z_anc @ z_pos.t()) / tau
                tgt = torch.arange(z_anc.shape[0])
                rel_loss = torch.nn.functional.cross_entropy(logits, tgt)
                loss = loss + w_rel * rel_loss
                rel_loss_val = float(rel_loss.detach())

        text_pred_val = 0.0
        if w_text_pred > 0.0 and use_text_pred:
            keep = (torch.rand(a_bs, text_dim) > mask_frac).float()
            z_masked = enc.encode(Xg[a_rows], Xc[a_rows], Xt[a_rows] * keep)
            logits_t = enc.text_head(z_masked)
            tgt_t = (Xtri[a_rows] > 0).float()
            text_loss = torch.nn.functional.binary_cross_entropy_with_logits(logits_t, tgt_t)
            loss = loss + w_text_pred * text_loss
            text_pred_val = float(text_loss.detach())

        ema_loss_val = 0.0
        if w_ema > 0.0 and ema is not None:
            z_stud = _l2_t(_enc_rows(enc, a_rows, feat_drop=fd))
            with torch.no_grad():
                z_teach = _l2_t(_enc_rows(ema, a_rows, feat_drop=fd))
            ema_loss = (1.0 - (z_stud * z_teach).sum(dim=1)).mean()
            loss = loss + w_ema * ema_loss
            ema_loss_val = float(ema_loss.detach())

        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite fusion loss ep=%d seed=%d" % (ep, seed))
        opt.zero_grad()
        loss.backward()
        opt.step()

        if ema is not None:
            m = cfg["ema_momentum"]
            with torch.no_grad():
                for pe, ps in zip(ema.parameters(), enc.parameters()):
                    pe.mul_(m).add_(ps, alpha=1.0 - m)

        if (ep % log_every == 0) or (ep == cfg["epochs"] - 1):
            _log("  fusion seed=%d ep=%d/%d geo=%.4f var=%.4f rel=%.4f textpred=%.4f ema=%.4f (%.1fs)"
                 % (seed, ep, cfg["epochs"], float(geo_loss.detach()), float(var_term.detach()),
                    rel_loss_val, text_pred_val, ema_loss_val, time.perf_counter() - t0))
    enc.eval()
    return enc


def encode_all(enc, feats):
    with torch.no_grad():
        g = torch.from_numpy(feats["own"].astype(np.float32))
        c = torch.from_numpy(feats["ctx"].astype(np.float32))
        t = torch.from_numpy(feats["text"].astype(np.float32))
        emb = _l2_t(enc.encode(g, c, t)).numpy().astype(np.float32)
    return emb


# ---------------------------------------------------------------------------
# Eval: WordNet supersense neighbourhood + DEGREE-MATCHED relational placement
# ---------------------------------------------------------------------------
def _auc_from_scores(scores, pos_mask):
    n_pos = int(pos_mask.sum())
    n_neg = int(pos_mask.shape[0] - n_pos)
    if n_pos == 0 or n_neg == 0:
        return None
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(scores.shape[0], dtype=np.float64)
    ranks[order] = np.arange(1, scores.shape[0] + 1)
    return float((ranks[pos_mask].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def eval_semantic_neighbourhood(codes, split, lex_labels, k=10):
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


def _degree_bins(train_deg_on_train, n_bins=5):
    """Quantile-bin train-gallery concepts by their train-degree. Returns bin id per gallery position."""
    d = train_deg_on_train.astype(np.float64)
    qs = np.quantile(d, np.linspace(0, 1, n_bins + 1)[1:-1]) if d.shape[0] > n_bins else np.array([])
    return np.digitize(d, qs)


def eval_relational_placement(codes, split, degree_matched=True, n_bins=5):
    """Held-out RELATIONAL-placement AUC. positives = query's true TRAIN neighbours.
    degree_matched=True: negatives drawn from TRAIN non-neighbours MATCHED to the positives' train-degree
    bin distribution (kills the popularity confound). degree_matched=False: all non-neighbours (random-neg)."""
    train_idx = split["train_idx"].astype(np.int64)
    held_idx = split["held_idx"].astype(np.int64)
    train_neigh = split["train_neigh"]
    train_deg = split["train_deg"]
    tset = {int(t): p for p, t in enumerate(train_idx.tolist())}
    Zg = codes[train_idx]
    G = train_idx.shape[0]
    deg_on_train = train_deg[train_idx]
    bins = _degree_bins(deg_on_train, n_bins=n_bins)
    rng = np.random.default_rng(EVAL_SEED)
    aucs = []
    for h in held_idx.tolist():
        nb = [tset[j] for j in train_neigh[h] if j in tset]
        n_pos = len(nb)
        if n_pos == 0 or n_pos >= G:
            continue
        pos_arr = np.asarray(nb, dtype=np.int64)
        pos_set = set(nb)
        scores = Zg @ codes[h]
        if degree_matched:
            neg_pool = []
            for pb in bins[pos_arr]:
                cand = np.nonzero((bins == pb))[0]
                cand = np.asarray([c for c in cand.tolist() if c not in pos_set], dtype=np.int64)
                if cand.shape[0] > 0:
                    neg_pool.append(int(cand[rng.integers(0, cand.shape[0])]))
            if len(neg_pool) < 1:
                continue
            neg_arr = np.asarray(sorted(set(neg_pool)), dtype=np.int64)
            sel = np.concatenate([pos_arr, neg_arr])
            pm = np.zeros(sel.shape[0], dtype=bool)
            pm[:pos_arr.shape[0]] = True
            a = _auc_from_scores(scores[sel], pm)
        else:
            pm = np.zeros(G, dtype=bool)
            pm[pos_arr] = True
            a = _auc_from_scores(scores, pm)
        if a is not None:
            aucs.append(a)
    if len(aucs) < 5:
        return float("nan"), len(aucs)
    return float(np.mean(aucs)), len(aucs)


def _emb_digest(emb):
    return hashlib.sha256(np.ascontiguousarray(emb.astype(np.float32)).tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# One seed: build deep-text rep (MLM), then all arms
# ---------------------------------------------------------------------------
def run_seed(seed, split, base_feats, tok_ids_all, landmarks, target_geo, lex_labels, cfg):
    c = cfg
    train_idx = split["train_idx"]

    # DEEP TEXT ENCODER: MLM-pretrain on TRAIN text only, then encode ALL concepts inductively.
    _log("seed=%d MLM-pretraining deep text encoder (d=%d L=%d H=%d vocab=%d max_len=%d)..."
         % (seed, c["d_model"], c["n_layers"], c["n_heads"], c["tok_vocab"], c["max_len"]))
    dt_enc, mlm_loss = mlm_pretrain_deeptext(tok_ids_all, train_idx, c, seed)
    deep_rep = encode_deeptext_all(dt_enc, tok_ids_all)             # [K, d_model] MLM-trained
    _log("seed=%d MLM final loss=%.4f deep_rep shape=%s" % (seed, mlm_loss, deep_rep.shape))

    # RANDOM (un-MLM'd) deep text encoder for the RANDOM_INIT arm
    torch.manual_seed(seed + 777)
    dt_rand = DeepTextEncoder(c["tok_vocab"], c["max_len"], c["d_model"], c["n_layers"],
                              c["n_heads"], c["ffn_mult"]).eval()
    deep_rep_rand = encode_deeptext_all(dt_rand, tok_ids_all)

    own = base_feats["own"]
    ctx = base_feats["ctx"]
    tri = base_feats["tri"]

    def _feats(text):
        return dict(own=own, ctx=ctx, text=text, tri=tri)

    feats_deep = _feats(deep_rep)
    feats_tri = _feats(tri)                                          # shallow arm: text branch = trigram bag
    feats_rand = _feats(deep_rep_rand)

    arm_codes = {}

    # RAW baselines (no learning)
    arm_codes[RAW_ARM] = _l2_np(own.astype(np.float64)).astype(np.float32)
    arm_codes[RAW_DEEP_ARM] = _l2_np(deep_rep.astype(np.float64) + 1e-9).astype(np.float32)

    # CHARTRIGRAM_GLOSS (R3/R4 shallow): grounding + trigram-bag branch + geometry + masked-tri BCE
    enc_tri = train_fusion(feats_tri, target_geo, landmarks, split, c, seed + 33,
                           use_ctx=False, use_text=True, w_rel=0.0, w_ema=0.0,
                           use_text_pred=True, do_train=True)
    arm_codes[TRIGRAM_ARM] = encode_all(enc_tri, feats_tri)

    # DEEP_TEXT: grounding + deep-text-rep branch + geometry + EMA
    enc_deep = train_fusion(feats_deep, target_geo, landmarks, split, c, seed + 45,
                            use_ctx=False, use_text=True, w_rel=0.0, w_ema=c["w_ema"],
                            use_text_pred=False, do_train=True)
    arm_codes[DEEP_ARM] = encode_all(enc_deep, feats_deep)

    # FULL_FUSION (PRIMARY): grounding + deep-text + relational-ctx + geometry + relpred + EMA
    enc_full = train_fusion(feats_deep, target_geo, landmarks, split, c, seed,
                            use_ctx=True, use_text=True, w_rel=c["w_rel"], w_ema=c["w_ema"],
                            use_text_pred=False, do_train=True)
    arm_codes[FULL_ARM] = encode_all(enc_full, feats_deep)

    # RANDOM_INIT: untrained full fusion over the RANDOM (un-MLM'd) deep text rep
    enc_r = train_fusion(feats_rand, target_geo, landmarks, split, c, seed + 101,
                         use_ctx=True, use_text=True, w_rel=c["w_rel"], w_ema=c["w_ema"],
                         use_text_pred=False, do_train=False)
    arm_codes[RANDINIT_ARM] = encode_all(enc_r, feats_rand)

    # COLLAPSE_SHUFFLE: permute ALL input rows across ids, train full objective -> ~0.5 witness
    enc_s = train_fusion(feats_deep, target_geo, landmarks, split, c, seed + 1,
                         use_ctx=True, use_text=True, w_rel=c["w_rel"], w_ema=c["w_ema"],
                         use_text_pred=False, do_train=True, shuffle_rows=True)
    Kk = split["K"]
    perm = np.random.default_rng(seed + 1 + 909).permutation(Kk)
    feats_shuf = dict(own=own[perm], ctx=ctx[perm], text=deep_rep[perm], tri=tri[perm])
    arm_codes[SHUFFLE_ARM] = encode_all(enc_s, feats_shuf)

    arm_metrics = {}
    for arm in ALL_ARMS:
        ev = eval_semantic_neighbourhood(arm_codes[arm], split, lex_labels, k=10)
        rp_dm, nq_dm = eval_relational_placement(arm_codes[arm], split, degree_matched=True)
        rp_rand, _ = eval_relational_placement(arm_codes[arm], split, degree_matched=False)
        ev["rel_place_auc_degmatched"] = rp_dm
        ev["rel_place_auc_randomneg"] = rp_rand
        ev["rel_place_n_query"] = nq_dm
        ev["emb_digest"] = _emb_digest(arm_codes[arm])
        arm_metrics[arm] = ev
        _log("seed=%d arm=%s same_lex_auc=%.4f rel_dm=%.4f rel_rand=%.4f prec@10=%.4f rec@1=%.4f base=%.4f n_q=%d"
             % (seed, arm, ev["same_lex_auc"], rp_dm, rp_rand, ev["precision_at_k"],
                ev["recall_at_1"], ev["category_base_rate"], ev["n_query"]))
    arm_metrics["_mlm_final_loss"] = mlm_loss

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
            rel_place_auc_degmatched_mean=float(np.nanmean(series(arm, "rel_place_auc_degmatched"))),
            rel_place_auc_randomneg_mean=float(np.nanmean(series(arm, "rel_place_auc_randomneg"))),
            precision_at_k_mean=float(series(arm, "precision_at_k").mean()),
            recall_at_1_mean=float(series(arm, "recall_at_1").mean()),
            category_base_rate_mean=float(series(arm, "category_base_rate").mean()),
            n_seeds=len(per_seed),
        )

    full = agg[FULL_ARM]["same_lex_auc_mean"]
    full_min = agg[FULL_ARM]["same_lex_auc_min"]
    deep = agg[DEEP_ARM]["same_lex_auc_mean"]
    trigram = agg[TRIGRAM_ARM]["same_lex_auc_mean"]
    raw = agg[RAW_ARM]["same_lex_auc_mean"]
    raw_deep = agg[RAW_DEEP_ARM]["same_lex_auc_mean"]
    randinit = agg[RANDINIT_ARM]["same_lex_auc_mean"]
    shuf = agg[SHUFFLE_ARM]["same_lex_auc_mean"]
    base_rate = agg[RAW_ARM]["category_base_rate_mean"]

    # THE NUMBER: FULL_FUSION - RAW_GROUNDING (per-seed for robustness)
    margin_series = (series(FULL_ARM, "same_lex_auc") - series(RAW_ARM, "same_lex_auc"))
    margin_raw = float(margin_series.mean())
    margin_raw_min = float(margin_series.min())

    # KEY DEPTH ablation: DEEP_TEXT - CHARTRIGRAM_GLOSS
    depth_series = (series(DEEP_ARM, "same_lex_auc") - series(TRIGRAM_ARM, "same_lex_auc"))
    depth_gain = float(depth_series.mean())
    depth_gain_min = float(depth_series.min())

    gain_raw_deep = raw_deep - raw           # deep-text-rep alone vs grounding
    gain_trigram = trigram - raw             # shallow char-trigram fused vs grounding (R3/R4 ~+0.007)
    gain_deep = deep - raw                   # deep-text fused vs grounding
    gain_full = full - raw                   # full fusion vs grounding (== margin_raw)
    margin_over_randinit = full - randinit

    cb_lo, cb_hi = COLLAPSE_BAND
    can_fail_fired = bool(cb_lo <= shuf <= cb_hi)
    raw_signal_ok = bool(raw >= RAW_SIGNAL_MIN)
    n_query = int(np.min(series(FULL_ARM, "n_query")))
    power_ok = bool(n_query >= MIN_QUERY_TASKS)

    real_margin = bool(margin_raw >= HP_MARGIN_OVER_RAW and margin_raw_min > 0.0)
    depth_helps = bool(depth_gain > DEPTH_HELPS_EPS)
    hard_pass = bool(can_fail_fired and raw_signal_ok and power_ok and real_margin
                     and full >= HP_FULL_SIGNAL and full >= randinit)
    hard_fail = bool((not can_fail_fired) or (not raw_signal_ok) or (full < HF_AUC) or (not power_ok))

    if hard_pass:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    deeper_ceiling = bool(verdict == "MIDDLE_BAND" and margin_raw < HP_MARGIN_OVER_RAW)

    verdict_msg = (
        "%s | THE-NUMBER full_fusion - raw_grounding = %.4f - %.4f = %+.4f (min=%+.4f, need>=%.2f, "
        "n_q=%d power_ok=%s) | DEPTH deep_text - chartrigram = %.4f - %.4f = %+.4f (min=%+.4f, helps=%s) | "
        "FULL same_lex_auc=%.4f (min=%.4f) rel_place[degmatched]=%.4f [randomneg]=%.4f prec@10=%.4f rec@1=%.4f | "
        "ABLATION vs raw_grounding=%.4f: raw_deeptext=%.4f(%+.4f) chartrigram=%.4f(%+.4f) "
        "deep_text=%.4f(%+.4f) FULL(%+.4f) | RANDOM_INIT=%.4f (full-randinit=%+.4f) COLLAPSE=%.4f "
        "-> can_fail=%s raw_signal_ok=%s | base_rate=%.4f | deeper_ceiling=%s | "
        "corpus: K=%d tokens_used=%d mean_tok/concept=%.1f mined/concept=%.2f text_cov=%.3f ewt_sents=%d | "
        "train=%d heldout=%d pairs=%d rels=%d lexnames=%d"
        % (verdict, full, raw, margin_raw, margin_raw_min, HP_MARGIN_OVER_RAW, n_query, power_ok,
           deep, trigram, depth_gain, depth_gain_min, depth_helps,
           full, full_min, agg[FULL_ARM]["rel_place_auc_degmatched_mean"],
           agg[FULL_ARM]["rel_place_auc_randomneg_mean"],
           agg[FULL_ARM]["precision_at_k_mean"], agg[FULL_ARM]["recall_at_1_mean"],
           raw, raw_deep, gain_raw_deep, trigram, gain_trigram, deep, gain_deep, gain_full,
           randinit, margin_over_randinit, shuf, can_fail_fired, raw_signal_ok, base_rate, deeper_ceiling,
           data_meta["n_kept_concepts"], data_meta["total_tokens_used"],
           data_meta["mean_tokens_per_concept"], data_meta["mean_mined_per_concept"],
           data_meta["text_coverage"], data_meta["ewt_sentences"],
           split_meta["n_train"], split_meta["n_heldout"], data_meta["n_kept_pairs"],
           data_meta["n_rel_slots"], data_meta["n_lexnames"]))

    gates = dict(
        full_fusion_same_lex_auc=full, full_fusion_same_lex_auc_min=full_min,
        deep_text_same_lex_auc=deep, chartrigram_gloss_same_lex_auc=trigram,
        raw_grounding_same_lex_auc=raw, raw_deeptext_same_lex_auc=raw_deep,
        random_init_same_lex_auc=randinit, collapse_shuffle_same_lex_auc=shuf,
        margin_over_raw_grounding=margin_raw, margin_over_raw_grounding_min=margin_raw_min,
        margin_over_random_init=margin_over_randinit,
        depth_gain_deep_minus_trigram=depth_gain, depth_gain_min=depth_gain_min, depth_helps=depth_helps,
        ablation_gain_raw_deeptext=gain_raw_deep, ablation_gain_chartrigram=gain_trigram,
        ablation_gain_deep_text=gain_deep, ablation_gain_full=gain_full,
        full_rel_place_degmatched=agg[FULL_ARM]["rel_place_auc_degmatched_mean"],
        full_rel_place_randomneg=agg[FULL_ARM]["rel_place_auc_randomneg_mean"],
        category_base_rate=base_rate,
        can_fail_fired=can_fail_fired, raw_signal_ok=raw_signal_ok, power_ok=power_ok, n_query=n_query,
        deeper_ceiling=deeper_ceiling, real_margin=real_margin,
        collapse_band=list(COLLAPSE_BAND), hp_full_signal=HP_FULL_SIGNAL,
        hf_auc=HF_AUC, hp_margin_over_raw=HP_MARGIN_OVER_RAW, raw_signal_min=RAW_SIGNAL_MIN,
        min_query_tasks=MIN_QUERY_TASKS,
        mlm_final_loss=float(np.mean([m.get("_mlm_final_loss", float("nan")) for m in per_seed])),
    )
    return verdict, verdict_msg, agg, gates


# ---------------------------------------------------------------------------
# Self-tests: discriminator telemetry-sensitivity + deep-text encoder trains (real code path)
# ---------------------------------------------------------------------------
def discriminator_selftest():
    """Planted-category synthetic: clustered codes -> AUC high; random -> ~0.5; shuffled labels -> ~0.5."""
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


def deeptext_selftest():
    """REAL-CODE-PATH: build the actual DeepTextEncoder + MLM-pretrain at tiny scale; assert MLM loss
    drops and pooled reps are finite + distinct. Also tokenizer determinism + degree-matched eval sanity."""
    tok_vocab, max_len, K = 128, 16, 40
    rng = np.random.default_rng(2)
    # planted: two token-cluster families -> distinguishable text
    ids = np.full((K, max_len), PAD_ID, dtype=np.int64)
    for i in range(K):
        fam = i % 2
        L = int(rng.integers(6, max_len))
        base = 2 + fam * 40
        ids[i, :L] = base + rng.integers(0, 20, size=L)
    cfg = dict(tok_vocab=tok_vocab, max_len=max_len, d_model=32, n_layers=2, n_heads=2, ffn_mult=2,
               mlm_epochs=30, mlm_batch=32, mlm_mask_frac=0.15, mlm_lr=3e-3)
    train_idx = np.arange(K)
    enc, last_loss = mlm_pretrain_deeptext(ids, train_idx, cfg, seed=7)
    # capture an early-loss reference by re-running 1 epoch fresh
    enc0, loss0 = mlm_pretrain_deeptext(ids, train_idx, dict(cfg, mlm_epochs=1), seed=7)
    rep = encode_deeptext_all(enc, ids)
    tok_det = (tokenize_text("the cat sat", tok_vocab, max_len)[0]
               == tokenize_text("the cat sat", tok_vocab, max_len)[0]).all()
    finite = bool(np.isfinite(rep).all())
    distinct = bool(_emb_digest(rep[0:1]) != _emb_digest(rep[1:2]))
    loss_dropped = bool(last_loss < loss0)
    res = dict(mlm_loss0=float(loss0), mlm_lossN=float(last_loss), loss_dropped=loss_dropped,
               rep_finite=finite, rep_distinct=distinct, tok_deterministic=bool(tok_det),
               rep_shape=list(rep.shape))
    ok = finite and distinct and loss_dropped and bool(tok_det)
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

    torch.set_num_threads(max(1, os.cpu_count() or 1))
    output_dir = get_output_dir(ANCHOR_NAME)
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()

    st_ok, st_res = discriminator_selftest()
    dt_ok, dt_res = deeptext_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    _log("deeptext_selftest ok=%s %s" % (dt_ok, dt_res))
    if not (st_ok and dt_ok):
        write_metrics(output_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="SELFTEST_FAILED discriminator_ok=%s deeptext_ok=%s: %s | %s"
                        % (st_ok, dt_ok, st_res, dt_res),
            summary="selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, deeptext_selftest=dt_res))
        raise SystemExit(1)

    _log("loading grounded subgraph (min_deg=%d cap=%d top_rel=%d)..."
         % (cfg["min_deg"], cfg["cap_nodes"], cfg["top_rel"]))
    data = load_grounded_subgraph(cfg)
    _log("grounded universe: %s" % {k: v for k, v in data["meta"].items() if k != "top_rels"})
    split = build_split(data, cfg)
    _log("split: %s" % split["split_meta"])

    own = split["own_feat"]
    ctx = _pooled_ctx_block(split, own, GROUND_DIM)
    base_feats = dict(own=own.astype(np.float32), ctx=ctx.astype(np.float32),
                      tri=data["tri_bag"].astype(np.float32))
    landmarks = select_landmarks(split, cfg)
    A = build_train_adjacency(split)
    own_norm = _l2_np(own.astype(np.float64)).astype(np.float32)
    target_geo = compute_target_geometry(own_norm, A, landmarks)
    _log("landmarks=%d own_dim=%d ctx_dim=%d tri_dim=%d target_geo shape=%s"
         % (landmarks.shape[0], base_feats["own"].shape[1], base_feats["ctx"].shape[1],
            base_feats["tri"].shape[1], target_geo.shape))

    if run_mode == "self_test":
        pm = run_seed(cfg["seeds"][0], split, base_feats, data["tok_ids"],
                      landmarks, target_geo, data["lex_labels"], cfg)
        write_metrics(output_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS discriminator + deeptext-MLM + end-to-end held-out eval exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, deeptext_selftest=dt_res,
            data_meta=data["meta"], split_meta=split["split_meta"],
            full_fusion_same_lex_auc=pm[FULL_ARM]["same_lex_auc"],
            deep_text_same_lex_auc=pm[DEEP_ARM]["same_lex_auc"],
            chartrigram_gloss_same_lex_auc=pm[TRIGRAM_ARM]["same_lex_auc"],
            raw_grounding_same_lex_auc=pm[RAW_ARM]["same_lex_auc"],
            collapse_shuffle_same_lex_auc=pm[SHUFFLE_ARM]["same_lex_auc"]))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, split, base_feats, data["tok_ids"],
                          landmarks, target_geo, data["lex_labels"], cfg)
            per_seed.append(pm)
            write_partial(output_dir, seed, dict(seed=seed,
                          arms={a: {k: v for k, v in pm[a].items() if k != "emb_digest"}
                                for a in ALL_ARMS}, run_mode=run_mode))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(output_dir, dict(
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
        gates=gates, arms_aggregate=agg,
        discriminator_selftest=st_res, deeptext_selftest=dt_res,
        seed_failures=seed_failures,
        per_seed=[{a: {k: v for k, v in per_seed[i][a].items() if k != "emb_digest"}
                   for a in ALL_ARMS} for i in range(len(per_seed))],
    )
    write_metrics(output_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


if __name__ == "__main__":
    _od = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
