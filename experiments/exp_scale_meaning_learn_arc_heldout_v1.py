"""SCALE meaning-learning: from-scratch transformer over ARC (237.7M tokens), leak-proof held-out-NEW.

WHY (THE PLAN scale_corpus_and_data_integrity_plan_2026-07-26 + WHERE_WE_ARE_NOW):
  The prior from-scratch deep-text run learned ~NOTHING beyond raw grounding on held-out-NEW concepts
  (raw_deeptext-alone 0.519 near-chance; deep-text -0.018 over grounding). Diagnosis: DATA-STARVED --
  it trained on 265,273 tokens total (mean 3.07 mined sentences / 53 tokens per concept). The AI2
  ARC_Corpus (data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt: 237.7M alpha tokens, 14.62M sentences)
  gives median 376 mentions/concept over the 24k grounded vocab -- a ~100x mentions-per-concept and ~900x
  token-count increase over the exact failure point. THE QUESTION (pre-registered fork below): does REAL
  experience at scale break the data-starvation wall -- does a LEARNED text-at-scale rep BEAT raw grounding
  on held-out-NEW concepts, or is the null OBJECTIVE-level (survives at scale => redirect to R1 geometry)?

WHAT (the run):
  1. DATA-INTEGRITY PREFLIGHT: exact-line dedup (bounded set), quality filter (min length, digit/symbol
     ratio, citation-fragment regex), from-scratch BPE tokenizer built ON ARC (never on held-out text).
  2. CONCEPT-LEVEL held-out split (sha256, PYTHONHASHSEED-independent), STRATIFIED by mention-frequency
     bucket. Every held-out concept's mentioning lines are SCRUBBED from ALL training text (tokenizer +
     MLM + train postings). VERIFIED-ZERO-OVERLAP GATE: 0 training windows contain a held-out surface.
  3. TRAIN a from-scratch small Transformer (learned token embeddings, NO borrowed vectors) by MASKED-
     LANGUAGE-MODELLING over ARC training text. Device-agnostic (CUDA+AMP on the GPU box; CPU for smoke).
  4. CONCEPT MEANING = aggregate of the frozen encoder's contextual reps over the concept's mention windows
     (mean-pool per mention, averaged across mentions). Held-out concepts encoded INDUCTIVELY (never trained).
  5. EVAL (leak-proof held-out-NEW): SEMANTIC (WordNet-supersense same-lexname per-query AUC) AND
     RELATIONAL (predict a held-out concept's true train-neighbour vs degree-matched non-neighbours; the
     rep has ZERO relational input => leak-proof). Fuse text + grounding by cosine-average late fusion.

ARMS (per-query AUC; base 0.5):
  RAW_GROUNDING  : cosine over raw 20d grounding norms, NO learning.               [THE ceiling to break]
  RAW_TEXT       : cosine over the MLM-learned text-rep alone.                      [signal in text-at-scale?]
  FUSED          : 0.5*(cos_grounding + cos_text) late fusion.                      [PRIMARY: beat grounding?]
  RANDOM_INIT    : cosine over text-rep from an UNTRAINED transformer.             [isolate learning]
  COLLAPSE_SHUFFLE: text-reps permuted across concept ids.                          [can-fail / leak witness ~0.5]
  POPULARITY     : rank candidates by mention-frequency / train-degree only.        [validity ~0.5]

THE ONE NUMBER (pre-registered bands, BEFORE running):
  HARD_PASS = FUSED - RAW_GROUNDING >= 0.03 (per-seed min > 0) on SEMANTIC held-out-NEW, AND RAW_TEXT >
    RANDOM_INIT (learning is real), AND validity holds (COLLAPSE in [0.44,0.56], POPULARITY in [0.44,0.56],
    RAW_GROUNDING >= 0.55 a real signal, power >= MIN_QUERY). Relational bar reported alongside.
  HARD_FAIL (the plan's fork) = on the WELL-COVERED subset (concepts with >= WELL_COVERED_MIN mentions),
    FUSED - RAW_GROUNDING <= 0 at this ~240M-token scale => data-scale hypothesis REFUTED for this
    substrate; the null is OBJECTIVE-level (R1 geometry), not data-level. Redirect budget off larger corpora.
  MIDDLE_BAND / TIE_NULL = |margin| < 0.03 (relational learning ~null at this scale, honest + decisive).

HARD INVARIANTS (project locks): TEACHER-FREE. NO GloVe/BGE/transformer WEIGHTS/borrowed vector ANYWHERE
  (token embeddings + Transformer learned FROM SCRATCH by MLM; BPE vocab built FROM ARC). INDUCTIVE
  (held-out placed from its own text + grounding; never a training target). LEAK-PROOF (concept-level
  scrub + zero-overlap witness; tokenizer never sees held-out text; relational target never an input).
  ASCII-only. AI2 ARC Corpus: INTERNAL research use only, do NOT redistribute corpus/derived raw text.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF; ARMS-MUST-DIFFER hash-test over per-concept rep matrices)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace + per-seed partials)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator base = 0.5 exactly; collapse + popularity + random-init controls witness the floor
# - baseline_in_band at smoke: collapse ~0.5; popularity ~0.5; raw_grounding a real >0.55 signal; primary not saturated
# - discriminator survives scale: FULL runs on GPU >=2 seeds; smoke previews controls; HARD-FAIL fork on well-covered
# - HARD_PASS strictly above floor: margin>=0.03 AND per-seed min>0 (not at-floor)
# - HP_SCOPE: gates apply to ARM_FUSED (primary, semantic) only; relational is a reported secondary bar
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except; specific classes -> metrics)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; controls witness it empirically)
# - deterministic seeding: sha256 concept split (freq-stratified, sha256-ranked) + fixed int seeds + sorted(); no hash()/list(set())
# - real_code_path: --self-test constructs the REAL objects (BPE build, MLM train step, transformer encode,
#     zero-overlap gate, both evals) at N~16 (SELFTEST_CFG IS the real pipeline at tiny scale)
# - progress_logging: print_flush_true (MLM step logs + eval logs flush=True) + _heartbeat.jsonl (timeout_s >> 1800)
# - device-agnostic: cuda+AMP on the GPU box, cpu for local smoke; no hard device assumption
"""

import argparse
import glob
import hashlib
import json
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
    record_gate,
    write_metrics,
    write_partial,
    aggregate_partials,
)

ANCHOR_NAME = "scale_meaning_learn_arc_heldout_v1"
ARC_CORPUS = os.path.join(_REPO, "data", "corpora", "arc",
                          "ARC-V1-Feb2018-2", "ARC_Corpus.txt")
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

# Deterministic salts / seeds
CONCEPT_SPLIT_SALT = "scale_meaning_arc_v1_concept_split::"
EVAL_SEED = 20260726

# Pre-reg bands (SEMANTIC held-out-NEW same-lexname per-query AUC).
HP_MARGIN_OVER_RAW = 0.03        # THE NUMBER: FUSED - RAW_GROUNDING must exceed this (break the wall)
RAW_SIGNAL_MIN = 0.55            # RAW_GROUNDING must be a real >0.55 signal (metric-not-saturated gate)
COLLAPSE_BAND = (0.44, 0.56)     # COLLAPSE_SHUFFLE + POPULARITY MUST sit here (validity / can-fail)
MIN_QUERY_TASKS = 120            # power floor for the held-out AUC to be trustworthy
WELL_COVERED_MIN = 100           # "well-covered" concept threshold for the HARD-FAIL fork
LEARNING_EPS = 0.0               # RAW_TEXT - RANDOM_INIT; > 0 => the learned text rep carries signal

# Arms
RAW_ARM = "ARM_RAW_GROUNDING"
TEXT_ARM = "ARM_RAW_TEXT"
FUSED_ARM = "ARM_FUSED"
RANDINIT_ARM = "ARM_RANDOM_INIT"
SHUFFLE_ARM = "ARM_COLLAPSE_SHUFFLE"
POP_ARM = "ARM_POPULARITY"
PRIMARY_ARM = FUSED_ARM
SEM_ARMS = [RAW_ARM, TEXT_ARM, FUSED_ARM, RANDINIT_ARM, SHUFFLE_ARM, POP_ARM]

# ---------------------------------------------------------------------------
# Config profiles
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    run_mode="selftest", seeds=[7],
    min_deg=2, cap_eval_concepts=500, heldout_count=24, min_mentions_eval=1,
    max_lines=50000, dedup_cap=60000, bpe_sample_lines=20000, cap_mentions=6,
    vocab=512, max_len=24, train_token_budget=400000, max_shards=1,
    d_model=32, n_layers=1, n_heads=2, ffn_mult=2,
    mlm_steps=15, mlm_batch=8, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=64, n_freq_buckets=4,
)
SMOKE_CFG = dict(
    run_mode="smoke", seeds=[7],
    min_deg=2, cap_eval_concepts=2500, heldout_count=250, min_mentions_eval=2,
    max_lines=150000, dedup_cap=200000, bpe_sample_lines=80000, cap_mentions=16,
    vocab=4096, max_len=48, train_token_budget=4000000, max_shards=6,
    d_model=128, n_layers=2, n_heads=4, ffn_mult=2,
    mlm_steps=250, mlm_batch=64, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=256, n_freq_buckets=5,
)
FULL_CFG = dict(
    run_mode="full", seeds=[7, 13],
    min_deg=2, cap_eval_concepts=None, heldout_count=800, min_mentions_eval=20,
    max_lines=10000000, dedup_cap=6000000, bpe_sample_lines=400000, cap_mentions=128,
    vocab=16000, max_len=128, train_token_budget=130000000, max_shards=16,
    d_model=512, n_layers=6, n_heads=8, ffn_mult=4,
    mlm_steps=60000, mlm_batch=128, mlm_mask_frac=0.15, mlm_lr=3e-4,
    encode_batch=256, n_freq_buckets=8,
)

_WORD_RE = re.compile(r"[a-z]+")
_CITATION_RE = re.compile(r"\b\d+\s*\(\s*\d+\s*\)\s*:\s*\d+")   # "8(2): 193-208" style bibliographic stub


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics / logging / heartbeat
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(
        pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode,
        expected_n_units=expected_n_units, host=platform.node(),
        cuda=bool(torch.cuda.is_available()),
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


def _heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = dict(ts_iso=datetime.now(timezone.utc).isoformat(),
               unit_idx=int(unit_idx), total_units=int(total_units),
               elapsed_s=float(elapsed_s))
    if extra:
        row["extra"] = extra
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a",
                  encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Deterministic held-out split (sha256; PYTHONHASHSEED-independent)
# ---------------------------------------------------------------------------
def _split_rank(concept_id):
    h = hashlib.sha256((CONCEPT_SPLIT_SALT + concept_id).encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") / float(2 ** 64)


# ---------------------------------------------------------------------------
# Tie-corrected Mann-Whitney AUC (average ranks; exact popularity -> 0.5)
# ---------------------------------------------------------------------------
def _auc_from_scores(scores, pos_mask):
    n_pos = int(pos_mask.sum())
    n_neg = int(pos_mask.shape[0] - n_pos)
    if n_pos == 0 or n_neg == 0:
        return None
    order = np.argsort(scores, kind="mergesort")
    ss = scores[order]
    ranks_sorted = np.empty(ss.shape[0], dtype=np.float64)
    i = 0
    n = ss.shape[0]
    while i < n:
        j = i
        while j + 1 < n and ss[j + 1] == ss[i]:
            j += 1
        avg = (i + 1 + j + 1) / 2.0
        ranks_sorted[i:j + 1] = avg
        i = j + 1
    ranks = np.empty(n, dtype=np.float64)
    ranks[order] = ranks_sorted
    return float((ranks[pos_mask].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


# ---------------------------------------------------------------------------
# WordNet lexname (EVAL-ONLY truth)
# ---------------------------------------------------------------------------
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


def _build_lexname_map(surfaces):
    """{surface: lexname or None} from the dominant (first) WordNet synset. EVAL-ONLY truth. Cached."""
    cache = _load_json_cache(LEXNAME_CACHE)
    need = [s for s in surfaces if s not in cache]
    if need:
        try:
            from nltk.corpus import wordnet as wn
        except ImportError as e:
            raise RuntimeError("NLTK WordNet required for EVAL-ONLY lexname truth.") from e
        for s in need:
            ss = None
            for cand in (s.replace(" ", "_"), s.replace(" ", ""), s.split(" ")[0]):
                if not cand:
                    continue
                try:
                    got = wn.synsets(cand)
                except Exception:  # noqa: BLE001 -- NLTK lookup hiccup: try next candidate
                    got = []
                if got:
                    ss = got[0]
                    break
            cache[s] = ss.lexname() if ss is not None else None
        _save_json_cache(LEXNAME_CACHE, cache)
    return {s: cache.get(s) for s in surfaces}


# ---------------------------------------------------------------------------
# Concept universe: single-token grounded surfaces with a WordNet lexname
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


def load_concept_universe(cfg):
    """Single-token alpha surfaces with grounding + degree>=min_deg + a WordNet lexname.
    Returns dict: ids, surfaces, vals[K,16], gpres[K,4], lexnames[K], surf_to_idx."""
    if not os.path.exists(NODES_PATH):
        raise FileNotFoundError("nodes.jsonl not found at %s" % NODES_PATH)
    ids, surfaces, raw_vals, raw_gpres = [], [], [], []
    seen_surf = set()
    with open(NODES_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            gd = d.get("grounding")
            if not gd:
                continue
            if int(d.get("degree", 0)) < cfg["min_deg"]:
                continue
            surf = str(d.get("surface", d["id"])).strip().lower()
            m = _WORD_RE.fullmatch(surf)
            if m is None:                # single alpha token only
                continue
            if surf in seen_surf:
                continue
            seen_surf.add(surf)
            vals, gpres = _grounding_vector(gd)
            ids.append(d["id"])
            surfaces.append(surf)
            raw_vals.append(vals)
            raw_gpres.append(gpres)
    if len(ids) < 100:
        raise RuntimeError("too few single-token grounded concepts (%d)" % len(ids))
    lexmap = _build_lexname_map(surfaces)
    keep = [i for i in range(len(ids)) if lexmap[surfaces[i]] is not None]
    if len(keep) < 100:
        raise RuntimeError("too few grounded concepts with a WordNet lexname (%d)" % len(keep))
    # deterministic order by id
    keep = sorted(keep, key=lambda i: ids[i])
    cap = cfg["cap_eval_concepts"]
    if cap is not None and len(keep) > cap:
        keep = keep[:cap]
    ids = [ids[i] for i in keep]
    surfaces = [surfaces[i] for i in keep]
    vals = np.stack([raw_vals[i] for i in keep], axis=0)
    gpres = np.stack([raw_gpres[i] for i in keep], axis=0)
    lexnames = [lexmap[s] for s in surfaces]
    surf_to_idx = {s: i for i, s in enumerate(surfaces)}
    return dict(ids=ids, surfaces=surfaces, vals=vals, gpres=gpres,
                lexnames=lexnames, surf_to_idx=surf_to_idx, K=len(ids))


# ---------------------------------------------------------------------------
# Quality filter + bounded exact-dedup
# ---------------------------------------------------------------------------
def _quality_ok(line, words):
    if len(words) < 4:
        return False
    n_alpha = sum(len(w) for w in words)
    n_all = len(line)
    if n_all > 0 and (n_alpha / float(n_all)) < 0.55:   # too many digits/symbols
        return False
    if _CITATION_RE.search(line):
        return False
    return True


def _line_hash(line):
    return hashlib.blake2b(line.encode("utf-8"), digest_size=8).digest()


# ---------------------------------------------------------------------------
# Pass 1: count mentions per concept (deduped + quality-filtered), corpus stats
# ---------------------------------------------------------------------------
def count_pass(cfg, surf_to_idx):
    K = len(surf_to_idx)
    counts = np.zeros(K, dtype=np.int64)
    dedup_cap = cfg["dedup_cap"]
    seen = set()
    n_read = n_kept = n_dup = n_lowq = 0
    total_tokens = 0
    with open(ARC_CORPUS, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            if cfg["max_lines"] is not None and n_read >= cfg["max_lines"]:
                break
            n_read += 1
            line = raw.strip()
            if not line:
                continue
            words = _WORD_RE.findall(line.lower())
            if not _quality_ok(line, words):
                n_lowq += 1
                continue
            h = _line_hash(line)
            if h in seen:
                n_dup += 1
                continue
            if len(seen) < dedup_cap:
                seen.add(h)
            n_kept += 1
            total_tokens += len(words)
            for w in set(words):
                idx = surf_to_idx.get(w)
                if idx is not None:
                    counts[idx] += 1
    stats = dict(n_read=n_read, n_kept=n_kept, n_dup=n_dup, n_lowq=n_lowq,
                 dup_rate=float(n_dup) / max(1, n_read),
                 total_alpha_tokens=int(total_tokens))
    return counts, stats


# ---------------------------------------------------------------------------
# Held-out split: freq-stratified, sha256-ranked (deterministic, leak-proof)
# ---------------------------------------------------------------------------
def build_split(universe, counts, cfg):
    K = universe["K"]
    ids = universe["ids"]
    eligible = [i for i in range(K) if counts[i] >= cfg["min_mentions_eval"]]
    if len(eligible) < cfg["heldout_count"] + 80:
        raise RuntimeError("too few eligible concepts (%d) for heldout_count=%d"
                           % (len(eligible), cfg["heldout_count"]))
    order = sorted(eligible, key=lambda i: counts[i])
    nb = cfg["n_freq_buckets"]
    buckets = [order[b * len(order) // nb:(b + 1) * len(order) // nb] for b in range(nb)]
    per_bucket = cfg["heldout_count"] // nb
    held = []
    for bk in buckets:
        ranked = sorted(bk, key=lambda i: _split_rank(ids[i]))
        held.extend(ranked[:per_bucket])
    held = sorted(set(held))
    held_set = set(held)
    train_eligible = [i for i in eligible if i not in held_set]
    is_held = np.zeros(K, dtype=bool)
    is_held[held] = True
    heldout_surfaces = set(universe["surfaces"][i] for i in held)
    split_meta = dict(
        n_eligible=len(eligible), n_heldout=len(held), n_train_eval=len(train_eligible),
        median_mentions_eligible=float(np.median(counts[eligible])),
        median_mentions_heldout=float(np.median(counts[held])),
    )
    return dict(held_idx=np.array(held, dtype=np.int64),
                train_eval_idx=np.array(sorted(train_eligible), dtype=np.int64),
                is_held=is_held, heldout_surfaces=heldout_surfaces,
                split_meta=split_meta)


def _scrub_variants(surface):
    """Deterministic light inflection set for a single-word surface (approximate lemma coverage)."""
    v = {surface}
    if surface.endswith("y"):
        v.add(surface[:-1] + "ies")
    v.update({surface + "s", surface + "es", surface + "ed", surface + "d",
              surface + "ing", surface + "er", surface + "est"})
    return v


# ---------------------------------------------------------------------------
# Pass 2: collect BPE-sample lines + per-concept mention postings (train + held-out)
# ---------------------------------------------------------------------------
def collect_pass(cfg, universe, split):
    surf_to_idx = universe["surf_to_idx"]
    scrub = set()
    for s in split["heldout_surfaces"]:
        scrub |= _scrub_variants(s)
    postings = [[] for _ in range(universe["K"])]     # per-concept list of raw sentence strings
    bpe_lines = []
    dedup_cap = cfg["dedup_cap"]
    seen = set()
    cap_m = cfg["cap_mentions"]
    n_train_lines = n_held_lines = 0
    train_tokens = 0
    n_read = 0
    with open(ARC_CORPUS, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            if cfg["max_lines"] is not None and n_read >= cfg["max_lines"]:
                break
            n_read += 1
            line = raw.strip()
            if not line:
                continue
            words = _WORD_RE.findall(line.lower())
            if not _quality_ok(line, words):
                continue
            h = _line_hash(line)
            if h in seen:
                continue
            if len(seen) < dedup_cap:
                seen.add(h)
            wset = set(words)
            is_heldline = any(w in scrub for w in wset)
            if is_heldline:
                n_held_lines += 1
                for w in wset:
                    idx = surf_to_idx.get(w)
                    if idx is not None and split["is_held"][idx] and len(postings[idx]) < cap_m:
                        postings[idx].append(line)
            else:
                n_train_lines += 1
                train_tokens += len(words)
                if len(bpe_lines) < cfg["bpe_sample_lines"]:
                    bpe_lines.append(line)
                for w in wset:
                    idx = surf_to_idx.get(w)
                    if idx is not None and (not split["is_held"][idx]) and len(postings[idx]) < cap_m:
                        postings[idx].append(line)
    meta = dict(n_train_lines=n_train_lines, n_held_lines=n_held_lines,
                bpe_sample=len(bpe_lines), train_tokens_available=int(train_tokens),
                scrub_terms=len(scrub))
    return postings, bpe_lines, meta


# ---------------------------------------------------------------------------
# From-scratch BPE tokenizer built ON ARC training text (never held-out text)
# ---------------------------------------------------------------------------
def build_bpe(bpe_lines, vocab):
    from tokenizers import Tokenizer, models, trainers, pre_tokenizers
    tok = Tokenizer(models.BPE(unk_token="[UNK]"))
    tok.pre_tokenizer = pre_tokenizers.Whitespace()
    trainer = trainers.BpeTrainer(
        vocab_size=int(vocab),
        special_tokens=["[PAD]", "[UNK]", "[MASK]"],
        show_progress=False)
    tok.train_from_iterator(iter(bpe_lines), trainer=trainer)
    pad_id = tok.token_to_id("[PAD]")
    unk_id = tok.token_to_id("[UNK]")
    mask_id = tok.token_to_id("[MASK]")
    if pad_id is None or unk_id is None or mask_id is None:
        raise RuntimeError("BPE special tokens missing after training")
    return tok, dict(pad=pad_id, unk=unk_id, mask=mask_id, size=tok.get_vocab_size())


def _encode_pad(tok, text, max_len, pad_id):
    ids = tok.encode(text).ids[:max_len]
    n = len(ids)
    if n < max_len:
        ids = ids + [pad_id] * (max_len - n)
    return np.asarray(ids, dtype=np.int64)


# ---------------------------------------------------------------------------
# Pass 3: tokenize training text into a contiguous token stream (budget-bounded)
# ---------------------------------------------------------------------------
def tokenize_train_stream(cfg, tok, split, spec):
    scrub = set()
    for s in split["heldout_surfaces"]:
        scrub |= _scrub_variants(s)
    budget = cfg["train_token_budget"]
    dedup_cap = cfg["dedup_cap"]
    seen = set()
    buf = []
    total = 0
    n_read = 0
    with open(ARC_CORPUS, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            if cfg["max_lines"] is not None and n_read >= cfg["max_lines"]:
                break
            n_read += 1
            line = raw.strip()
            if not line:
                continue
            words = _WORD_RE.findall(line.lower())
            if not _quality_ok(line, words):
                continue
            h = _line_hash(line)
            if h in seen:
                continue
            if len(seen) < dedup_cap:
                seen.add(h)
            if any(w in scrub for w in set(words)):
                continue                       # scrub: held-out line never enters the train stream
            ids = tok.encode(line).ids
            buf.extend(ids)
            total += len(ids)
            if total >= budget:
                break
    arr = np.asarray(buf, dtype=np.uint16 if spec["size"] < 65536 else np.int32)
    return arr, int(total)


# ---------------------------------------------------------------------------
# From-scratch Transformer (learned token+pos emb; tied MLM head)
# ---------------------------------------------------------------------------
class TinyTransformer(torch.nn.Module):
    def __init__(self, vocab, max_len, d_model, n_layers, n_heads, ffn_mult, pad_id):
        super().__init__()
        self.pad_id = pad_id
        self.tok_emb = torch.nn.Embedding(vocab, d_model, padding_idx=pad_id)
        self.pos_emb = torch.nn.Embedding(max_len, d_model)
        layer = torch.nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=ffn_mult * d_model,
            dropout=0.0, activation="gelu", batch_first=True, norm_first=True)
        self.enc = torch.nn.TransformerEncoder(layer, num_layers=n_layers)
        self.norm = torch.nn.LayerNorm(d_model)
        self.max_len = max_len
        self.d_model = d_model

    def _contextual(self, ids):
        pad_mask = (ids == self.pad_id)
        L = ids.shape[1]
        pos = torch.arange(L, device=ids.device).unsqueeze(0)
        h = self.tok_emb(ids) + self.pos_emb(pos)
        h = self.enc(h, src_key_padding_mask=pad_mask)
        return self.norm(h), pad_mask

    def mlm_logits(self, ids):
        h, _ = self._contextual(ids)
        return torch.nn.functional.linear(h, self.tok_emb.weight)   # tied head

    def pooled(self, ids):
        h, pad_mask = self._contextual(ids)
        keep = (~pad_mask).float().unsqueeze(-1)
        summed = (h * keep).sum(dim=1)
        cnt = keep.sum(dim=1).clamp_min(1.0)
        rep = summed / cnt
        return rep / (rep.norm(dim=1, keepdim=True) + 1e-8)


def mlm_train(stream, spec, cfg, device, seed, out_dir, hb_total):
    """MLM-pretrain the transformer on the contiguous train token stream. Returns (model, final_loss)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    max_len = cfg["max_len"]
    model = TinyTransformer(spec["size"], max_len, cfg["d_model"], cfg["n_layers"],
                            cfg["n_heads"], cfg["ffn_mult"], spec["pad"]).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    _log("  model params=%.2fM device=%s vocab=%d d=%d L=%d"
         % (n_params / 1e6, device.type, spec["size"], cfg["d_model"], cfg["n_layers"]))
    n_win = stream.shape[0] // max_len
    if n_win < 4:
        raise RuntimeError("train stream too short: %d tokens, %d windows" % (stream.shape[0], n_win))
    windows = stream[:n_win * max_len].reshape(n_win, max_len)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["mlm_lr"])
    use_amp = (device.type == "cuda")
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
    g = np.random.default_rng(seed + 5)
    bs = min(cfg["mlm_batch"], n_win)
    mask_frac = cfg["mlm_mask_frac"]
    mask_id = spec["mask"]
    log_every = max(1, cfg["mlm_steps"] // 10)
    last_loss = float("nan")
    t0 = time.perf_counter()
    model.train()
    for step in range(cfg["mlm_steps"]):
        sel = g.integers(0, n_win, size=bs)
        ids = torch.from_numpy(windows[sel].astype(np.int64)).to(device)
        rnd = torch.rand(ids.shape, device=device)
        mask = rnd < mask_frac
        if int(mask.sum()) < 1:
            mask[:, 0] = True
        target = ids.clone()
        inp = ids.clone()
        inp[mask] = mask_id
        opt.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
            logits = model.mlm_logits(inp)
            loss = torch.nn.functional.cross_entropy(logits[mask], target[mask])
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite MLM loss step=%d seed=%d" % (step, seed))
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        last_loss = float(loss.detach())
        if (step % log_every == 0) or (step == cfg["mlm_steps"] - 1):
            el = time.perf_counter() - t0
            _log("  MLM seed=%d step=%d/%d loss=%.4f (%.1fs)"
                 % (seed, step, cfg["mlm_steps"], last_loss, el))
            _heartbeat(out_dir, step, hb_total, el, extra={"mlm_loss": last_loss, "seed": seed})
    model.eval()
    return model, last_loss


# ---------------------------------------------------------------------------
# Concept text-rep: mean-pool contextual reps over mention windows, avg across mentions
# ---------------------------------------------------------------------------
def encode_concept_text_reps(model, tok, postings, cfg, device, spec):
    K = len(postings)
    d = model.d_model
    reps = np.zeros((K, d), dtype=np.float32)
    cnt = np.zeros(K, dtype=np.int64)
    max_len = cfg["max_len"]
    pad_id = spec["pad"]
    flat_idx = []
    flat_ids = []
    for ci in range(K):
        for s in postings[ci][:cfg["cap_mentions"]]:
            flat_idx.append(ci)
            flat_ids.append(_encode_pad(tok, s, max_len, pad_id))
    if not flat_ids:
        return reps, cnt
    flat_idx = np.asarray(flat_idx, dtype=np.int64)
    X = np.stack(flat_ids, axis=0)
    bs = cfg["encode_batch"]
    use_amp = (device.type == "cuda")
    with torch.no_grad():
        for i in range(0, X.shape[0], bs):
            ids = torch.from_numpy(X[i:i + bs]).to(device)
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
                pooled = model.pooled(ids)
            pooled = pooled.float().cpu().numpy()
            seg = flat_idx[i:i + bs]
            for r in range(pooled.shape[0]):
                reps[seg[r]] += pooled[r]
                cnt[seg[r]] += 1
    nz = cnt > 0
    reps[nz] /= cnt[nz][:, None]
    nrm = np.linalg.norm(reps, axis=1, keepdims=True)
    reps = np.where(nrm > 1e-8, reps / (nrm + 1e-8), reps)
    return reps, cnt


# ---------------------------------------------------------------------------
# Grounding rep (standardized on train, L2-normed) for cosine
# ---------------------------------------------------------------------------
def build_grounding_reps(universe, split):
    vals = universe["vals"]
    tr = split["train_eval_idx"]
    import warnings as _w
    with _w.catch_warnings():
        _w.simplefilter("ignore", RuntimeWarning)
        mu = np.nanmean(vals[tr], axis=0)
        sd = np.nanstd(vals[tr], axis=0)
    mu = np.nan_to_num(mu, nan=0.0)
    sd = np.where(np.isnan(sd) | (sd < 1e-6), 1.0, sd)
    z = (vals - mu[None, :]) / sd[None, :]
    z = np.where(np.isnan(z), 0.0, z).astype(np.float32)
    g = np.concatenate([z, universe["gpres"].astype(np.float32)], axis=1)   # [K,20]
    nrm = np.linalg.norm(g, axis=1, keepdims=True)
    g = np.where(nrm > 1e-8, g / (nrm + 1e-8), g)
    return g


# ---------------------------------------------------------------------------
# SEMANTIC eval: per-query same-lexname AUC over held-out concepts
# ---------------------------------------------------------------------------
def _cos_matrix(reps, rows, cols):
    return reps[rows] @ reps[cols].T


def semantic_eval(ground, text, text_rand, counts, universe, split, seed, subset_mask=None):
    """Per-query same-lexname AUC for each arm over held-out concepts (optionally a coverage subset)."""
    held = split["held_idx"]
    have_text = np.linalg.norm(text, axis=1) > 1e-8
    elig = [int(i) for i in held.tolist() if have_text[i]]
    if subset_mask is not None:
        elig = [i for i in elig if subset_mask[i]]
    if len(elig) < 10:
        return None
    elig = np.array(sorted(elig), dtype=np.int64)
    lex_str = [universe["lexnames"][i] for i in elig]
    logf = np.log1p(counts[elig].astype(np.float64))
    rng = np.random.default_rng(seed + 31)
    perm = rng.permutation(elig.shape[0])
    text_sh = text.copy()
    text_sh[elig] = text[elig][perm]     # collapse: shuffle text-reps across held-out ids

    cg = _cos_matrix(ground, elig, elig)
    ct = _cos_matrix(text, elig, elig)
    cr = _cos_matrix(text_rand, elig, elig)
    cs = _cos_matrix(text_sh, elig, elig)
    cf = 0.5 * (cg + ct)

    arm_scores = {RAW_ARM: cg, TEXT_ARM: ct, FUSED_ARM: cf,
                  RANDINIT_ARM: cr, SHUFFLE_ARM: cs}
    out = {a: [] for a in SEM_ARMS}
    n = elig.shape[0]
    n_used = 0
    for qi in range(n):
        same = np.array([lex_str[j] == lex_str[qi] for j in range(n)])
        same[qi] = False
        cand = np.ones(n, dtype=bool)
        cand[qi] = False
        pos = same[cand]
        if pos.sum() == 0 or pos.sum() == pos.shape[0]:
            continue
        n_used += 1
        for a in [RAW_ARM, TEXT_ARM, FUSED_ARM, RANDINIT_ARM, SHUFFLE_ARM]:
            sc = arm_scores[a][qi][cand]
            au = _auc_from_scores(sc, pos)
            if au is not None:
                out[a].append(au)
        # popularity: candidate frequency only (query-independent)
        pop = logf[cand]
        au = _auc_from_scores(pop, pos)
        if au is not None:
            out[POP_ARM].append(au)
    res = {a: (float(np.mean(v)) if v else None) for a, v in out.items()}
    res["_n_query"] = n_used
    res["_n_concepts"] = int(n)
    return res


# ---------------------------------------------------------------------------
# RELATIONAL eval (leak-proof): predict a held-out concept's true train-neighbour
# ---------------------------------------------------------------------------
def load_adjacency(universe, cfg):
    id_to_idx = {c: i for i, c in enumerate(universe["ids"])}
    K = universe["K"]
    adj = [set() for _ in range(K)]
    shards = sorted(glob.glob(EDGES_GLOB))[:cfg["max_shards"]]
    for shard in shards:
        with open(shard, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                e = json.loads(line)
                s = id_to_idx.get(e.get("subject"))
                o = id_to_idx.get(e.get("obj"))
                if s is None or o is None or s == o:
                    continue
                adj[s].add(o)
                adj[o].add(s)
    deg = np.array([len(a) for a in adj], dtype=np.int64)
    return adj, deg, len(shards)


def relational_eval(ground, text, counts, universe, split, adj, deg, n_shards, seed):
    """Per-query AUC: rank a held-out concept's true TRAIN-neighbour vs degree-matched train non-neighbours,
    scored by rep cosine. rep has ZERO relational input => leak-proof."""
    held = split["held_idx"]
    train_pool = split["train_eval_idx"]
    train_set = set(int(x) for x in train_pool.tolist())
    have_text = np.linalg.norm(text, axis=1) > 1e-8
    # degree bins over train pool for matched negatives
    deg_bin = {}
    for t in train_pool.tolist():
        deg_bin.setdefault(int(deg[t]), []).append(t)
    max_deg = int(deg[train_pool].max()) if train_pool.shape[0] else 0
    rng = np.random.default_rng(seed + 71)
    out = {RAW_ARM: [], FUSED_ARM: [], SHUFFLE_ARM: [], POP_ARM: []}
    # collapse: shuffled text
    elig_q = [int(h) for h in held.tolist() if have_text[h]]
    if elig_q:
        eq = np.array(sorted(elig_q), dtype=np.int64)
        perm = rng.permutation(eq.shape[0])
        text_sh = text.copy()
        text_sh[eq] = text[eq][perm]
    else:
        text_sh = text
    n_used = 0
    for h in elig_q:
        pos_neigh = sorted(j for j in adj[h] if j in train_set and have_text[j])
        if not pos_neigh:
            continue
        pos_neigh = pos_neigh[:8]
        exclude = set(adj[h]) | {h}
        negs = []
        used = set()
        ok = True
        for p in pos_neigh:
            dp = int(deg[p])
            picked = -1
            for tol in range(0, max_deg + 1):
                cands = []
                for dd in ((dp,) if tol == 0 else (dp - tol, dp + tol)):
                    if dd in deg_bin:
                        cands.extend(deg_bin[dd])
                cands = [c for c in cands if c not in exclude and c not in used and have_text[c]]
                if cands:
                    picked = cands[int(rng.integers(0, len(cands)))]
                    break
            if picked < 0:
                ok = False
                break
            negs.append(picked)
            used.add(picked)
        if not ok or not negs:
            continue
        n_used += 1
        cand = np.array(pos_neigh + negs, dtype=np.int64)
        posm = np.array([True] * len(pos_neigh) + [False] * len(negs))
        cg = ground[h] @ ground[cand].T
        ct = text[h] @ text[cand].T
        cf = 0.5 * (cg + ct)
        cs = text_sh[h] @ text[cand].T
        pop = np.log1p(deg[cand].astype(np.float64))
        for a, sc in ((RAW_ARM, cg), (FUSED_ARM, cf), (SHUFFLE_ARM, cs), (POP_ARM, pop)):
            au = _auc_from_scores(sc, posm)
            if au is not None:
                out[a].append(au)
    res = {a: (float(np.mean(v)) if v else None) for a, v in out.items()}
    res["_n_query"] = n_used
    res["_n_shards"] = n_shards
    return res


# ---------------------------------------------------------------------------
# ARMS-MUST-DIFFER (META_RULE_AF)
# ---------------------------------------------------------------------------
def _arms_differ(rep_dict):
    dig = {}
    for name, arr in rep_dict.items():
        dig[name] = hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()
    names = sorted(dig)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            assert dig[names[a]] != dig[names[b]], \
                "META_RULE_AF VIOLATION: %s and %s bit-identical" % (names[a], names[b])
    return dig


# ---------------------------------------------------------------------------
# Seed-independent data prep (done ONCE; split/tokenizer/postings/graph are seed-free)
# ---------------------------------------------------------------------------
def prepare_data(cfg, universe):
    _log("count pass...")
    counts, corpus_stats = count_pass(cfg, universe["surf_to_idx"])
    _log("  corpus: read=%d kept=%d dup_rate=%.4f low_q=%d tokens=%d"
         % (corpus_stats["n_read"], corpus_stats["n_kept"], corpus_stats["dup_rate"],
            corpus_stats["n_lowq"], corpus_stats["total_alpha_tokens"]))
    split = build_split(universe, counts, cfg)
    _log("  split: heldout=%d train_eval=%d median_mentions(elig)=%.0f"
         % (split["split_meta"]["n_heldout"], split["split_meta"]["n_train_eval"],
            split["split_meta"]["median_mentions_eligible"]))

    _log("collect pass (postings + BPE sample)...")
    postings, bpe_lines, collect_meta = collect_pass(cfg, universe, split)
    _log("  train_lines=%d held_lines=%d bpe_sample=%d train_tokens_avail=%d"
         % (collect_meta["n_train_lines"], collect_meta["n_held_lines"],
            collect_meta["bpe_sample"], collect_meta["train_tokens_available"]))
    if len(bpe_lines) < 50:
        raise RuntimeError("too few BPE-sample lines (%d)" % len(bpe_lines))

    _log("build BPE (vocab=%d)..." % cfg["vocab"])
    tok, spec = build_bpe(bpe_lines, cfg["vocab"])
    _log("  BPE size=%d pad=%d unk=%d mask=%d" % (spec["size"], spec["pad"], spec["unk"], spec["mask"]))

    _log("tokenize train stream (budget=%d)..." % cfg["train_token_budget"])
    stream, trained_tokens = tokenize_train_stream(cfg, tok, split, spec)
    _log("  trained_tokens=%d windows=%d" % (trained_tokens, stream.shape[0] // cfg["max_len"]))

    # ZERO-OVERLAP WITNESS: no held-out surface may appear in any TRAIN line (leak-proof gate).
    witness_leaks = _zero_overlap_witness(cfg, split, sample_lines=20000)
    _log("  zero-overlap witness: %d leaked train lines (must be 0)" % witness_leaks)
    if witness_leaks != 0:
        raise RuntimeError("LEAK: %d train lines contain a held-out surface" % witness_leaks)

    ground = build_grounding_reps(universe, split)
    _log("load relational adjacency (max_shards=%d)..." % cfg["max_shards"])
    adj, deg, n_shards = load_adjacency(universe, cfg)

    return dict(counts=counts, corpus_stats=corpus_stats, split=split,
                postings=postings, collect_meta=collect_meta, tok=tok, spec=spec,
                stream=stream, trained_tokens=trained_tokens, ground=ground,
                adj=adj, deg=deg, n_shards=n_shards, witness_leaks=witness_leaks)


# ---------------------------------------------------------------------------
# One seed (MLM train + encode + eval; consumes the shared data bundle)
# ---------------------------------------------------------------------------
def run_one_seed(seed, cfg, device, out_dir, universe, bundle):
    t0 = time.perf_counter()
    split = bundle["split"]
    counts = bundle["counts"]
    tok = bundle["tok"]
    spec = bundle["spec"]
    postings = bundle["postings"]
    ground = bundle["ground"]

    _log("seed=%d: MLM train (%d steps)..." % (seed, cfg["mlm_steps"]))
    model, final_loss = mlm_train(bundle["stream"], spec, cfg, device, seed, out_dir, cfg["mlm_steps"])
    _log("  MLM done final_loss=%.4f" % final_loss)

    _log("seed=%d: encode concept text-reps (trained)..." % seed)
    text_reps, mrep_cnt = encode_concept_text_reps(model, tok, postings, cfg, device, spec)
    torch.manual_seed(seed + 999)
    rand_model = TinyTransformer(spec["size"], cfg["max_len"], cfg["d_model"], cfg["n_layers"],
                                 cfg["n_heads"], cfg["ffn_mult"], spec["pad"]).to(device)
    rand_model.eval()
    _log("seed=%d: encode concept text-reps (random-init)..." % seed)
    text_rand, _ = encode_concept_text_reps(rand_model, tok, postings, cfg, device, spec)

    held = split["held_idx"]
    arm_digests = _arms_differ({
        RAW_ARM: ground[held], TEXT_ARM: text_reps[held], RANDINIT_ARM: text_rand[held]})

    _log("seed=%d: semantic eval..." % seed)
    sem_all = semantic_eval(ground, text_reps, text_rand, counts, universe, split, seed)
    well_mask = counts >= WELL_COVERED_MIN
    sem_well = semantic_eval(ground, text_reps, text_rand, counts, universe, split, seed,
                             subset_mask=well_mask)
    _log("seed=%d: relational eval..." % seed)
    rel = relational_eval(ground, text_reps, counts, universe, split,
                          bundle["adj"], bundle["deg"], bundle["n_shards"], seed)

    result = dict(
        seed=int(seed), run_mode=cfg["run_mode"],
        elapsed_s=float(time.perf_counter() - t0),
        final_mlm_loss=float(final_loss),
        trained_tokens=int(bundle["trained_tokens"]),
        corpus_stats=bundle["corpus_stats"],
        collect_meta=bundle["collect_meta"],
        split_meta=split["split_meta"],
        bpe_size=int(spec["size"]),
        n_well_covered=int(well_mask[held].sum()),
        semantic_all=sem_all,
        semantic_well_covered=sem_well,
        relational=rel,
        arm_digests=arm_digests,
        mention_rep_coverage=float((mrep_cnt[held] > 0).mean()),
    )
    return result


def _zero_overlap_witness(cfg, split, sample_lines):
    """Scan a sample of reconstructed TRAIN lines; count any that contain a held-out surface (must be 0)."""
    scrub_exact = set(split["heldout_surfaces"])
    scrub = set()
    for s in scrub_exact:
        scrub |= _scrub_variants(s)
    dedup_cap = cfg["dedup_cap"]
    seen = set()
    leaks = 0
    checked = 0
    n_read = 0
    with open(ARC_CORPUS, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            if cfg["max_lines"] is not None and n_read >= cfg["max_lines"]:
                break
            n_read += 1
            line = raw.strip()
            if not line:
                continue
            words = _WORD_RE.findall(line.lower())
            if not _quality_ok(line, words):
                continue
            h = _line_hash(line)
            if h in seen:
                continue
            if len(seen) < dedup_cap:
                seen.add(h)
            wset = set(words)
            if any(w in scrub for w in wset):
                continue                          # held-out line: excluded from train (correct)
            # this is a TRAIN line -> must contain NO held-out exact surface
            if any(w in scrub_exact for w in wset):
                leaks += 1
            checked += 1
            if checked >= sample_lines:
                break
    return leaks


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _valid_band(x, lo, hi):
    return (x is not None) and (lo <= x <= hi)


def build_verdict(per_seed, cfg):
    seeds = sorted(per_seed.keys(), key=lambda k: int(k))
    def col(section, arm):
        vals = []
        for k in seeds:
            sec = per_seed[k].get(section)
            if sec and sec.get(arm) is not None:
                vals.append(sec[arm])
        return vals
    raw = col("semantic_all", RAW_ARM)
    txt = col("semantic_all", TEXT_ARM)
    fus = col("semantic_all", FUSED_ARM)
    rnd = col("semantic_all", RANDINIT_ARM)
    sh = col("semantic_all", SHUFFLE_ARM)
    pop = col("semantic_all", POP_ARM)
    nq = [per_seed[k].get("semantic_all", {}).get("_n_query", 0) for k in seeds]

    def mean(v):
        return float(np.mean(v)) if v else None
    m_raw, m_txt, m_fus = mean(raw), mean(txt), mean(fus)
    m_rnd, m_sh, m_pop = mean(rnd), mean(sh), mean(pop)
    margins = [f - r for f, r in zip(fus, raw)] if (fus and raw and len(fus) == len(raw)) else []
    margin_mean = float(np.mean(margins)) if margins else None
    margin_min = float(np.min(margins)) if margins else None
    learn_margins = [t - r for t, r in zip(txt, rnd)] if (txt and rnd and len(txt) == len(rnd)) else []
    learn_mean = float(np.mean(learn_margins)) if learn_margins else None

    # well-covered fork
    wf = col("semantic_well_covered", FUSED_ARM)
    wr = col("semantic_well_covered", RAW_ARM)
    well_margins = [f - r for f, r in zip(wf, wr)] if (wf and wr and len(wf) == len(wr)) else []
    well_margin_mean = float(np.mean(well_margins)) if well_margins else None

    # relational
    rraw = col("relational", RAW_ARM)
    rfus = col("relational", FUSED_ARM)
    rsh = col("relational", SHUFFLE_ARM)
    rpop = col("relational", POP_ARM)
    rel_margins = [f - r for f, r in zip(rfus, rraw)] if (rfus and rraw and len(rfus) == len(rraw)) else []
    rel_margin_mean = float(np.mean(rel_margins)) if rel_margins else None

    min_nq = min(nq) if nq else 0
    validity = (
        _valid_band(m_sh, *COLLAPSE_BAND) and _valid_band(m_pop, *COLLAPSE_BAND)
        and (m_raw is not None and m_raw >= RAW_SIGNAL_MIN) and (min_nq >= MIN_QUERY_TASKS))

    gates = []
    gates.append(record_gate("collapse_in_band", 1.0 if _valid_band(m_sh, *COLLAPSE_BAND) else 0.0, 1.0, "==",
                             note="collapse=%.4f band=%s" % ((m_sh if m_sh else -1), COLLAPSE_BAND)))
    gates.append(record_gate("popularity_in_band", 1.0 if _valid_band(m_pop, *COLLAPSE_BAND) else 0.0, 1.0, "==",
                             note="pop=%.4f" % (m_pop if m_pop else -1)))
    gates.append(record_gate("raw_grounding_signal", m_raw if m_raw is not None else 0.0, RAW_SIGNAL_MIN, ">=",
                             note="raw grounding must be a real signal"))
    gates.append(record_gate("power_min_query", float(min_nq), float(MIN_QUERY_TASKS), ">=",
                             note="held-out query power floor"))
    gates.append(record_gate("fused_beats_raw_margin", margin_mean if margin_mean is not None else -1.0,
                             HP_MARGIN_OVER_RAW, ">=", note="PRIMARY: FUSED-RAW semantic"))
    gates.append(record_gate("fused_beats_raw_per_seed_min", margin_min if margin_min is not None else -1.0,
                             0.0, ">", note="per-seed min margin"))
    gates.append(record_gate("learning_real_text_over_random", learn_mean if learn_mean is not None else -1.0,
                             LEARNING_EPS, ">", note="RAW_TEXT - RANDOM_INIT"))

    run_mode = cfg["run_mode"]
    if run_mode in ("selftest", "smoke"):
        # smoke/self-test: PASS iff the cell RAN, leak-gate fired, arms differ, controls computed.
        ran_ok = (m_raw is not None and m_fus is not None and m_txt is not None
                  and m_sh is not None and m_pop is not None)
        verdict = "SMOKE_PASS" if ran_ok else "SMOKE_INCOMPLETE"
        vmsg = ("SMOKE run_mode=%s raw=%.4f text=%.4f fused=%.4f margin=%s learn(txt-rand)=%s "
                "collapse=%.4f pop=%.4f rel_margin=%s well_margin=%s n_query_min=%d"
                % (run_mode, m_raw or -1, m_txt or -1, m_fus or -1,
                   ("%.4f" % margin_mean) if margin_mean is not None else "NA",
                   ("%.4f" % learn_mean) if learn_mean is not None else "NA",
                   m_sh or -1, m_pop or -1,
                   ("%.4f" % rel_margin_mean) if rel_margin_mean is not None else "NA",
                   ("%.4f" % well_margin_mean) if well_margin_mean is not None else "NA", min_nq))
    else:
        if not validity:
            verdict = "HARD_FAIL_INVALID"
            vmsg = ("INVALID: validity gate failed (collapse=%s pop=%s raw=%s n_query_min=%d). "
                    "Controls must behave before the number is trustworthy."
                    % (m_sh, m_pop, m_raw, min_nq))
        elif (margin_mean is not None and margin_mean >= HP_MARGIN_OVER_RAW
              and margin_min is not None and margin_min > 0.0
              and learn_mean is not None and learn_mean > LEARNING_EPS):
            verdict = "HARD_PASS"
            vmsg = ("HARD_PASS: scale broke the wall. FUSED-RAW=%.4f (>=%.2f, per-seed min=%.4f); "
                    "RAW_TEXT-RANDOM=%.4f; raw=%.4f text=%.4f fused=%.4f; well_covered_margin=%s; "
                    "rel_margin=%s" % (margin_mean, HP_MARGIN_OVER_RAW, margin_min, learn_mean,
                                       m_raw, m_txt, m_fus,
                                       ("%.4f" % well_margin_mean) if well_margin_mean is not None else "NA",
                                       ("%.4f" % rel_margin_mean) if rel_margin_mean is not None else "NA"))
        elif well_margin_mean is not None and well_margin_mean <= 0.0:
            verdict = "HARD_FAIL_DATASCALE_REFUTED"
            vmsg = ("HARD_FAIL fork: on WELL-COVERED concepts (>=%d mentions) FUSED-RAW=%.4f <= 0 at scale. "
                    "Data-scale hypothesis REFUTED; the null is OBJECTIVE-level (R1 geometry), not data. "
                    "raw=%.4f text=%.4f fused=%.4f margin_all=%s"
                    % (WELL_COVERED_MIN, well_margin_mean, m_raw, m_txt, m_fus,
                       ("%.4f" % margin_mean) if margin_mean is not None else "NA"))
        else:
            verdict = "MIDDLE_BAND_TIE_NULL"
            vmsg = ("TIE_NULL: |FUSED-RAW|=%s < %.2f -> text-at-scale ties raw grounding on held-out-NEW "
                    "(learning ~null at this data scale, decisive honest finding). raw=%.4f text=%.4f "
                    "fused=%.4f learn(txt-rand)=%s well_margin=%s rel_margin=%s"
                    % (("%.4f" % margin_mean) if margin_mean is not None else "NA", HP_MARGIN_OVER_RAW,
                       m_raw or -1, m_txt or -1, m_fus or -1,
                       ("%.4f" % learn_mean) if learn_mean is not None else "NA",
                       ("%.4f" % well_margin_mean) if well_margin_mean is not None else "NA",
                       ("%.4f" % rel_margin_mean) if rel_margin_mean is not None else "NA"))

    summary = dict(
        semantic_raw_grounding=m_raw, semantic_text=m_txt, semantic_fused=m_fus,
        semantic_random_init=m_rnd, semantic_collapse=m_sh, semantic_popularity=m_pop,
        semantic_margin_fused_minus_raw=margin_mean, semantic_margin_min=margin_min,
        learning_text_minus_random=learn_mean,
        well_covered_margin=well_margin_mean,
        relational_raw=mean(rraw), relational_fused=mean(rfus),
        relational_collapse=mean(rsh), relational_popularity=mean(rpop),
        relational_margin=rel_margin_mean,
        n_query_min=min_nq, validity=validity,
        trained_tokens=[per_seed[k].get("trained_tokens") for k in seeds],
    )
    return verdict, vmsg, summary, gates


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _select_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default=None)
    args = ap.parse_args()

    if args.self_test:
        cfg = SELFTEST_CFG
    elif args.smoke:
        cfg = SMOKE_CFG
    else:
        cfg = FULL_CFG

    out_dir = get_output_dir(ANCHOR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    _write_start_marker(out_dir, cfg["run_mode"], len(cfg["seeds"]))

    device = torch.device(args.device) if args.device else _select_device()
    _log("run_mode=%s device=%s seeds=%s cuda=%s"
         % (cfg["run_mode"], device.type, cfg["seeds"], torch.cuda.is_available()))
    if not os.path.exists(ARC_CORPUS):
        raise FileNotFoundError("ARC corpus not found at %s (remote staging?)" % ARC_CORPUS)

    _log("loading concept universe...")
    universe = load_concept_universe(cfg)
    _log("concept universe: K=%d single-token grounded+lexname concepts" % universe["K"])

    _log("preparing shared data (seed-independent: split, tokenizer, postings, stream, graph)...")
    bundle = prepare_data(cfg, universe)

    for seed in cfg["seeds"]:
        res = run_one_seed(seed, cfg, device, out_dir, universe, bundle)
        write_partial(out_dir, seed, res)
        _log("seed=%d done in %.1fs" % (seed, res["elapsed_s"]))

    per_seed = aggregate_partials(out_dir, cfg["seeds"])
    verdict, vmsg, summary, gates = build_verdict(per_seed, cfg)
    _log("VERDICT: %s" % verdict)
    _log(vmsg)

    metrics = dict(
        verdict=verdict, verdict_msg=vmsg, summary=vmsg,
        anchor_name=ANCHOR_NAME, run_mode=cfg["run_mode"],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        device=device.type, cuda=bool(torch.cuda.is_available()),
        n_seeds=len(cfg["seeds"]),
        results_summary=summary,
        per_seed={k: per_seed[k] for k in per_seed},
        bands=dict(hp_margin_over_raw=HP_MARGIN_OVER_RAW, raw_signal_min=RAW_SIGNAL_MIN,
                   collapse_band=list(COLLAPSE_BAND), min_query=MIN_QUERY_TASKS,
                   well_covered_min=WELL_COVERED_MIN),
        cardinality_ok=(len(per_seed) == len(cfg["seeds"])),
        expected_n_units=len(cfg["seeds"]),
    )
    write_metrics(out_dir, metrics, results=list(per_seed.values()), gate_claims=gates)

    if args.self_test:
        _selftest_assertions(per_seed, summary, verdict)
        _log("SELF-TEST PASS")


def _selftest_assertions(per_seed, summary, verdict):
    assert len(per_seed) >= 1, "no seed completed"
    r = per_seed[sorted(per_seed.keys())[0]]
    assert r["semantic_all"] is not None, "semantic eval did not run"
    assert r["semantic_all"].get(RAW_ARM) is not None, "raw-grounding arm missing"
    assert r["semantic_all"].get(FUSED_ARM) is not None, "fused arm missing"
    assert r["semantic_all"].get(TEXT_ARM) is not None, "text arm missing"
    assert r["relational"] is not None, "relational eval did not run"
    assert np.isfinite(r["final_mlm_loss"]), "MLM loss not finite"
    assert r["trained_tokens"] > 0, "no tokens trained on"
    for a in [RAW_ARM, TEXT_ARM, FUSED_ARM]:
        au = r["semantic_all"][a]
        assert 0.0 <= au <= 1.0, "AUC out of range for %s: %s" % (a, au)
    assert verdict in ("SMOKE_PASS", "SMOKE_INCOMPLETE"), "unexpected selftest verdict %s" % verdict
    assert verdict == "SMOKE_PASS", "selftest did not complete arms (%s)" % verdict


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
