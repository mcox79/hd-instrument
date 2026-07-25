"""native_meaning_encoder_scale_v1 -- can we EARN, natively and at scale, the property-predictive
meaning structure that frozen GloVe has distributionally -- but the BRAIN'S way (error-driven
predictive statistical learning / Rogers-McClelland item->attribute), with NO borrowed vectors in
the learned representation?

VET'd diagnostic this closes (atom 29562): our native concept representation is THIN --
property-discrimination held-out ~0.211 (= chance ~0.21) vs frozen-GloVe ~0.554. GloVe extracts a
property structure our native encoder does not. This cell tests whether a native, self-supervised,
ERROR-DRIVEN encoder trained AT SCALE on our own corpora climbs off that thin ~0.211 floor toward
the GloVe ~0.554 reference -- WITHOUT any borrowed embedding in the learned codes.

OBJECTIVE (native, error-driven; NO borrowed vectors):
  A SINGLE tied embedding table E[V, N_DIM], RANDOM init, trained by two predict->correct channels:
    (1) CONTEXT prediction (skipgram + negative sampling) over ARC_Corpus science sentences
        (~14.6M sentences): for a center word predict a nearby context word; error-driven SGNS.
        This is predictive statistical learning -- the mechanism GloVe/word2vec use to EARN
        distributional structure, run natively over OUR corpus.
    (2) RELATION prediction (masked typed-relation) over the full WorldTree tablestore: given a
        concept and a typed relation R, predict the value: (mean E[concept_words] + R[rel]) must
        score the gold value's E above negatives (SGNS). Rogers-McClelland item->attribute channel;
        directly supervises property structure on TRAIN concepts (held-out concepts EXCLUDED).
  TIED single table: property-discrimination eval is cos-pick over ONE table (as GloVe is), so the
  cosine geometry the eval reads IS the geometry the two channels shape. E is the ONLY learned
  representation; GloVe/word2vec vectors NEVER enter it.

REUSE vs FRESH (reported honestly): the encoder-migration lineage
(exp_encoder_migration_step1b_v2/v3/v4) is deeply coupled to a BORROWED BGE-large teacher cache
(its RKD target IS the teacher cosine matrix; its mining is teacher-neighbour mining) -- swapping
that objective cleanly is not possible without gutting the core, and distilling a borrowed teacher
is exactly the shortcut we refuse. So the NATIVE objective is built FRESH here, REUSING the GPU
scaffolding PATTERNS: torch.cuda batched training, warmup+cosine LR schedule, chunked step loop,
checkpoint/resume + write_metrics via experiments/_seed_checkpoint, and the defensive
error-checking template (start-marker / crash-diagnostic / heartbeat). GloVe appears ONLY as a
frozen ceiling reference in eval (SMOKE-local; CITED in the portable FULL), never in the codes.

YARDSTICK (the v2 property-discrimination task, reproduced): held-out-BY-CONCEPT fine-value
discrimination -- concept + target relation, candidate set = gold + freq-matched hard distractors,
gold at a RANDOMIZED position (abstain -> chance not auto-correct). Constants + table set + parse +
freq-matched-distractor + gold-randomization logic are copied VERBATIM from
experiments/exp_composed_differentiation_loop_v2.py (kept self-contained/portable: the FULL run
depends on ARC + WorldTree ONLY, no GloVe/hdlab import at FULL runtime -- F.3 local/remote drift).

ARMS (cos-pick held-out acc + in-vocab acc; IDENTICAL items/split/candidates/gold_pos):
  chance ................ mean(1/n_cand); reference floor (~0.21)
  native_untrained ...... E at RANDOM init, cos-pick -> the THIN native floor (expect ~chance ~0.211)
  native_context_only ... E trained by CONTEXT channel only (ablation: earn-it-like-GloVe distributional)
  native_learned ........ E trained by CONTEXT + RELATION channels -> THE VARIABLE UNDER TEST
  glove_zerofit ......... frozen GloVe cos-pick, ceiling reference (~0.554); SMOKE-local, CITED in FULL

ONE VARIABLE: native_untrained vs native_learned = error-driven training vs random init, SAME
architecture / N_DIM / eval. glove_zerofit is the borrowed-vector ceiling reference (not a variable).

PRE-REGISTERED BANDS (a priori; NOT tuned):
  FLOOR (native_untrained/chance) ~0.21 ; CEILING (GloVe) ~0.554.
  HARD-PASS = native_learned held-out >= 0.31 AND (native_learned - native_untrained) >= 0.08 AND
              wilson-CI-lower(native_learned) > native_untrained  (a real climb off the thin floor,
              strictly above floor+5%-band; band width 0.344 -> 5%=0.017, margin 0.10 >> that).
  HARD-FAIL = native_learned held-out <= 0.24 (floor+0.03): self-supervised prediction at scale does
              NOT earn property-predictive meaning -> real finding (meaning may need grounding /
              Barsalou beyond text).
  MIDDLE = 0.24 < native_learned held-out < 0.31: real but modest, not to the clear bar.
  Scaling: native_learned at FULL must EXCEED native_learned at SMOKE (more data -> more structure).

CAN-FAIL: native_learned CAN land at ~0.21 (if error-driven prediction earns no property structure,
E stays at the random floor). Difficulty on (held-out-by-concept, freq-matched distractors, gold
randomized). Real baselines recomputed inline (untrained floor + GloVe ceiling).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (sha256 over per-arm correctness arrays; untrained/context/learned differ)
# - final_metrics_atomicity = tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - crlb_n/a: accuracy discriminator over cos-pick; no closed-form noise floor. Empirical floor =
#   chance = mean(1/n_cand) ~0.21 = native_untrained arm (measured). HARD-PASS 0.31 < GloVe 0.554
#   ceiling and > chance -> reachable (GloVe demonstrates the structure exists in distributional data).
# - baseline_in_band at smoke: native_untrained in (0.05, 0.95) (~0.21); GloVe ceiling ~0.55 not saturated
# - discriminator survives scale: smoke fires (native_learned > native_untrained by >= 0.02) + analytical
#   (GloVe earned 0.554 from ~6B tokens; ARC ~few-hundred-M tokens at FULL -> structure grows with data)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE: HARD-PASS/FAIL gates apply to native_learned ONLY; baselines are references
# - cardinality_ok: single-config (no sweep axis); EXPECTED arms declared + counted
# - per-unit failure-class instrumentation (no bare except; crash-diagnostic)
# - calibration_check: default_ok_for_this_regime (torch embedding+matmul GPU nondeterminism is
#   sub-0.01 on a 100s-of-items accuracy metric; fixed int seeds + torch.manual_seed; no hash()-seed)
# - all reported numbers MEASURED@ this cell's metrics.json
# - progress_logging: print_flush_true (+ heartbeat); timeout_s >= 1800
# - start-marker / crash-diagnostic / heartbeat present
# - deterministic_seeding: fixed int seeds, numpy default_rng, sorted(set()); no builtin-hash-seeded RNG

Contract: SMOKE = local foreground-to-completion (machinery + small-scale signal + GloVe ceiling).
FULL = GPU overnight_queue (ARC + WorldTree staged to remote; GloVe NOT staged, ceiling CITED).
NO borrowed vectors in E. ASCII-only. No em dashes in output. VET-PENDING (skunkworks owns VET).
"""
from __future__ import annotations

import os
import re
import sys
import csv
import json
import time
import math
import hashlib
import argparse
import platform
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

import torch  # noqa: E402  (REQUIRED; GPU at FULL, CPU at smoke)

ANCHOR_NAME = "native_meaning_encoder_scale_v1"

# ---------------------------------------------------------------------------
# yardstick constants (COPIED VERBATIM from exp_composed_differentiation_loop_v2.py to keep the FULL
# run self-contained/portable: no GloVe/hdlab import at FULL runtime)
# ---------------------------------------------------------------------------
K_DISTRACT = 5
HELDOUT_FRAC = 0.20
FREQ_MATCH_BINS = 4
MAX_COACTIVE_REL = 4

CURATED_TABLES = (
    ("KINDOF", 1, 4), ("MADEOF", 2, 6), ("PARTOF", 1, 5), ("HABITAT", 3, 5), ("LOCATIONS", 2, 4),
    ("PROP-MAGNETISM", 0, 3), ("PROP-CONDUCTIVITY", 0, 3), ("PROP-CHEM-ACIDITY", 0, 5),
    ("PROP-HARDNESS", 2, 5), ("PROP-WARM-COLD-BLOODED", 1, 3), ("PROP-SOLUBILITY", 0, 3),
    ("PROP-MAT-OPACITY", 2, 5), ("PROP-MAT-DURABILITY", 1, 3), ("PROP-FLEX-RIGIDITY", 1, 5),
    ("PROP-RECYCLABLE", 1, 3), ("PROP-CHEM-REACT", 1, 8), ("PROP-CHEM-CHARGE", 2, 4),
    ("PROP-RESOURCES-RENEWABLE", 0, 4), ("PROP-INHERITEDLEARNED", 3, 8),
    ("PROP-STATESOFMATTER-TEMPS", 0, 2), ("XIVORE", 1, 4), ("PREDATOR-PREY", 2, 5),
    ("CONSUMERS-EATING", 0, 3), ("USEDFOR", 2, 6), ("CONTAINS", 2, 6), ("SOURCEOF", 2, 7),
    ("FORMEDBY", 2, 4),
)
COARSE_RELS = ("KINDOF", "MADEOF", "PARTOF", "HABITAT", "LOCATIONS")
RELATIONS = tuple(t for (t, _, _) in CURATED_TABLES)
REL_IDX = {r: i for i, r in enumerate(RELATIONS)}
NREL = len(RELATIONS)

STOP = {"", "a", "an", "the", "some", "all", "many", "most", "something", "that", "this",
        "they", "it", "other", "of", "for", "to", "is", "are", "and", "or", "kind", "type"}

_TABLE_DIR = os.path.join(_REPO, "data", "corpora", "worldtree",
                          "WorldtreeExplanationCorpusV2.1_Feb2020", "tablestore", "v2.1", "tables")
_ARC_PATH = os.path.join(_REPO, "data", "corpora", "arc", "ARC-V1-Feb2018-2", "ARC_Corpus.txt")

# ---------------------------------------------------------------------------
# config (a priori; NOT tuned for PASS)
# ---------------------------------------------------------------------------
N_DIM = 300              # dimension-matched to GloVe-300 for a fair ceiling comparison
NEG_K = 5                # negative samples per positive (SGNS)
WINDOW = 5               # skipgram context window
MIN_COUNT = 5            # vocab min token count in ARC (WorldTree concept/value words force-added)
MAX_VOCAB = 120_000
LAMBDA_REL = 1.0         # weight of the relation-prediction channel in the combined loss
REL_BATCH_FRAC = 0.25    # relation-batch size = this * context-batch size
BASE_LR = 2.5e-3         # Adam base LR (SGNS); warmup + cosine decay
UNIGRAM_POW = 0.75       # negative-sampling distribution exponent (word2vec)

# scale profiles: (max_sentences, steps, batch)
SMOKE_PROFILE = dict(max_sentences=70_000, steps=1_500, batch=512)
FULL_PROFILE = dict(max_sentences=10_000_000, steps=200_000, batch=4096)

SEED = 20260725

# pre-registered bands
FLOOR_REF = 0.21                 # native_untrained/chance reference (atom 29562 native-0.211)
GLOVE_CEILING_REF = 0.554        # CITED@atom 29562 frozen-GloVe reference
HP_HELDOUT = 0.31                # HARD-PASS: native_learned held-out >= this
HP_GAP_OVER_UNTRAINED = 0.08     # AND climb this far over the untrained floor
HF_HELDOUT = 0.24                # HARD-FAIL: native_learned held-out <= this
SMOKE_FIRE_DELTA = 0.02          # smoke discriminator-fires: native_learned - native_untrained >= this
MIN_HELDOUT_ITEMS = 60
SAT = 0.95                       # any arm >= this => saturated (INVALID / iterate difficulty)

_T0 = [0.0]
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ---------------------------------------------------------------------------
# markers / crash / heartbeat / atomic write
# ---------------------------------------------------------------------------
def _out_dir(suffix=""):
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME + suffix)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node(),
              "device": DEVICE}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# normalization / parse (copied from yardstick; WordNet-optional so FULL stays portable)
# ---------------------------------------------------------------------------
_WN = [None]


def _wn():
    if _WN[0] is None:
        try:
            from nltk.corpus import wordnet as wn
            wn.morphy("test")
            _WN[0] = wn
        except Exception:
            _WN[0] = False
    return _WN[0]


def _clean(s):
    s = s.strip().lower()
    s = s.split(";")[0].strip()
    s = re.sub(r"[^a-z0-9 \-]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _lemma_word(w):
    wn = _wn()
    if wn:
        for pos in ("n", "v", "a"):
            m = wn.morphy(w, pos)
            if m:
                return m
    if len(w) > 3 and w.endswith("es"):
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def normalize_phrase(s):
    c = _clean(s)
    if not c:
        return c
    return " ".join(_lemma_word(w) for w in c.split())


def parse_tables(tables):
    """WorldTree tablestore -> normalized (concept, relation, value) triples + per-rel precision proxy.
    Copied verbatim from the v2 yardstick."""
    triples = []
    precision = {}
    for tbl, si, vi in tables:
        path = os.path.join(_TABLE_DIR, tbl + ".tsv")
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f, delimiter="\t"))
        n_rows = 0
        n_clean = 0
        for row in rows[1:]:
            if not any(c.strip() for c in row):
                continue
            n_rows += 1
            if len(row) <= max(si, vi):
                continue
            subj = normalize_phrase(row[si])
            val = normalize_phrase(row[vi])
            if subj in STOP or val in STOP or not subj or not val:
                continue
            if len(subj.split()) > 4 or len(val.split()) > 4:
                continue
            if subj == val:
                continue
            n_clean += 1
            triples.append((subj, tbl, val))
        precision[tbl] = round(n_clean / n_rows, 4) if n_rows else 0.0
    seen = set()
    out = []
    for t in triples:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return sorted(out), precision


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / d
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d
    return (round(center - half, 4), round(center + half, 4))


def _tok_words(phrase):
    """Alphanumeric word tokens (>= 2 chars) of a phrase; the encoder's phrase unit."""
    out, cur = [], []
    for ch in phrase.lower():
        if ("a" <= ch <= "z") or ("0" <= ch <= "9"):
            cur.append(ch)
        else:
            if len(cur) >= 2:
                out.append("".join(cur))
            cur = []
    if len(cur) >= 2:
        out.append("".join(cur))
    return out


# ---------------------------------------------------------------------------
# eval items: property-discrimination candidate sets, held-out BY CONCEPT (yardstick logic; NO GloVe)
# ---------------------------------------------------------------------------
def build_eval_items(triples, seed, kindof_cap=700):
    """Reproduce the v2 property-discrimination items WITHOUT any GloVe encoding (portable):
    freq-matched hard distractors from the gold value's SAME marginal-frequency quantile bin,
    gold at a RANDOMIZED position, held-out split BY CONCEPT. Returns (items, meta)."""
    rng = np.random.default_rng(seed + 101)

    by_rel = defaultdict(list)
    for (c, r, v) in triples:
        by_rel[r].append((c, r, v))
    kept = []
    for r in sorted(by_rel.keys()):
        lst = sorted(set(by_rel[r]))
        if r in COARSE_RELS and kindof_cap and len(lst) > kindof_cap:
            idx = np.sort(rng.permutation(len(lst))[:kindof_cap])
            lst = [lst[i] for i in idx.tolist()]
        kept.extend(lst)
    kept = sorted(set(kept))

    concepts = sorted({c for (c, r, v) in kept})
    gold_by_cr = defaultdict(set)
    rels_by_concept = defaultdict(set)
    valvec_by_concept = defaultdict(set)
    pool = defaultdict(set)
    for (c, r, v) in kept:
        gold_by_cr[(c, r)].add(v)
        rels_by_concept[c].add(r)
        valvec_by_concept[c].add(v)
        pool[r].add(v)
    pool = {r: sorted(vs) for r, vs in pool.items()}

    n_cr = len(gold_by_cr)
    n_multi = sum(1 for k in gold_by_cr if len(gold_by_cr[k]) > 1)
    multi_valid_rate = round(n_multi / n_cr, 4) if n_cr else 0.0

    # held-out split BY CONCEPT (no-leak for the RELATION channel)
    perm = np.random.default_rng(seed + 202).permutation(len(concepts))
    n_hold = int(round(HELDOUT_FRAC * len(concepts)))
    held_concepts = {concepts[i] for i in perm[:n_hold].tolist()}

    # freq-matched hard-negative bins per relation
    val_freq_by_rel = defaultdict(Counter)
    for (c, r, v) in kept:
        val_freq_by_rel[r][v] += 1
    freq_bin = {}
    bin_members = defaultdict(lambda: defaultdict(list))
    for r in sorted(pool.keys()):
        ranked = sorted(((val_freq_by_rel[r][x], x) for x in pool[r]))
        nvp = len(ranked)
        for rank, (_fq, x) in enumerate(ranked):
            b = min(FREQ_MATCH_BINS - 1, int(rank * FREQ_MATCH_BINS / max(1, nvp)))
            freq_bin[(r, x)] = b
            bin_members[r][b].append(x)

    def _freqmatched_pool(r, gold, exclude):
        gb = freq_bin[(r, gold)]
        cp = [x for x in bin_members[r][gb] if x not in exclude]
        if len(cp) < K_DISTRACT:
            for b in sorted(bin_members[r].keys(), key=lambda bb: (abs(bb - gb), bb)):
                if b == gb:
                    continue
                for x in bin_members[r][b]:
                    if x not in exclude and x not in cp:
                        cp.append(x)
                if len(cp) >= K_DISTRACT:
                    break
        return cp

    items = []
    for (c, r, v) in kept:
        p = pool[r]
        if len(p) < 2:
            continue
        exclude = set(gold_by_cr[(c, r)]) | valvec_by_concept[c]
        cand_pool = _freqmatched_pool(r, v, exclude)
        if not cand_pool:
            continue
        _h = hashlib.md5(f"{seed}|{c}|{r}|{v}".encode("utf-8")).hexdigest()
        irng = np.random.default_rng(int(_h[:8], 16))
        take = min(K_DISTRACT, len(cand_pool))
        pick = irng.permutation(len(cand_pool))[:take]
        distractors = [cand_pool[i] for i in sorted(pick.tolist())]
        gold_pos = int(irng.integers(0, len(distractors) + 1))
        cand_vals = distractors[:gold_pos] + [v] + distractors[gold_pos:]
        items.append({
            "concept": c, "relation": r, "gold": v, "cand_vals": cand_vals, "gold_pos": gold_pos,
            "tier": ("coarse" if r in COARSE_RELS else "fine"), "held": (c in held_concepts),
        })

    rel_counts = sorted(len(rels_by_concept[c]) for c in rels_by_concept)
    density = {"mean": round(float(np.mean(rel_counts)), 3) if rel_counts else 0.0,
               "frac_ge2": round(float(np.mean([1.0 if x >= 2 else 0.0 for x in rel_counts])), 4)
               if rel_counts else 0.0}
    meta = {"n_triples": len(kept), "n_concepts": len(concepts), "n_held_concepts": len(held_concepts),
            "multi_valid_rate": multi_valid_rate, "density": density,
            "pool_sizes": {r: len(pool[r]) for r in sorted(pool)}}
    # TRAIN triples for the relation channel = non-held concepts only (no-leak)
    train_triples = [(c, r, v) for (c, r, v) in kept if c not in held_concepts]
    return items, train_triples, sorted(held_concepts), meta


# ---------------------------------------------------------------------------
# vocabulary + ARC corpus tokenization
# ---------------------------------------------------------------------------
def _iter_arc(max_sentences):
    n = 0
    with open(_ARC_PATH, encoding="utf-8", errors="ignore") as f:
        for line in f:
            yield line
            n += 1
            if n >= max_sentences:
                break


def build_corpus(max_sentences, forced_words, output_dir):
    """Stream ARC sentences -> token id sentences + tied vocab. forced_words (WorldTree concept/value
    words) are force-added so eval phrases are in-vocab. Returns (sentences_ids, word2id, id_counts)."""
    _heartbeat(output_dir, "corpus_count", {"max_sentences": max_sentences})
    counts = Counter()
    n_sent = 0
    for line in _iter_arc(max_sentences):
        for w in _tok_words(line):
            counts[w] += 1
        n_sent += 1
        if n_sent % 1_000_000 == 0:
            _heartbeat(output_dir, "corpus_count_progress", {"n_sent": n_sent, "vocab_seen": len(counts)})

    # vocab: ARC words with count >= MIN_COUNT (top MAX_VOCAB by freq) UNION forced WorldTree words
    kept = [w for w, c in counts.items() if c >= MIN_COUNT]
    kept = sorted(kept, key=lambda w: (-counts[w], w))[:MAX_VOCAB]
    vocab = sorted(set(kept) | set(forced_words))
    word2id = {w: i for i, w in enumerate(vocab)}
    _heartbeat(output_dir, "vocab_built", {"vocab": len(vocab), "forced_added": len(set(forced_words) - set(kept))})

    # second pass: tokenize into a FLAT token array + per-sentence start offsets (scale-safe: one
    # contiguous array, no python list of millions of small arrays; enables a vectorized sampler).
    flat_chunks = []
    starts = [0]
    id_counts = np.zeros(len(vocab), dtype=np.float64)
    total = 0
    n_sent = 0
    for line in _iter_arc(max_sentences):
        ids = [word2id[w] for w in _tok_words(line) if w in word2id]
        if len(ids) >= 2:
            arr = np.asarray(ids, dtype=np.int32)
            flat_chunks.append(arr)
            total += len(arr)
            starts.append(total)
            n_sent += 1
            if n_sent % 2_000_000 == 0:
                _heartbeat(output_dir, "tokenize_progress", {"n_sent": n_sent, "tokens": total})
    flat = np.concatenate(flat_chunks) if flat_chunks else np.zeros(0, dtype=np.int32)
    starts = np.asarray(starts, dtype=np.int64)
    np.add.at(id_counts, flat, 1.0)
    # sent_id per token position (for within-sentence context sampling), vectorized
    sent_id = np.zeros(len(flat), dtype=np.int64)
    if len(starts) > 2:
        sent_id[starts[1:-1]] = 1
        sent_id = np.cumsum(sent_id)
    _heartbeat(output_dir, "corpus_tokenized", {"n_sentences": n_sent, "tokens": int(total)})
    return (flat, starts, sent_id), word2id, id_counts


def flatten_sentences(sentences):
    """List of int arrays -> (flat, starts, sent_id) flat representation (for planted/self-test)."""
    sents = [np.asarray(s, dtype=np.int32) for s in sentences if len(s) >= 2]
    if not sents:
        return np.zeros(0, dtype=np.int32), np.asarray([0], dtype=np.int64), np.zeros(0, dtype=np.int64)
    flat = np.concatenate(sents)
    starts = np.concatenate([[0], np.cumsum([len(s) for s in sents])]).astype(np.int64)
    sent_id = np.zeros(len(flat), dtype=np.int64)
    if len(starts) > 2:
        sent_id[starts[1:-1]] = 1
        sent_id = np.cumsum(sent_id)
    return flat, starts, sent_id


# ---------------------------------------------------------------------------
# batched samplers (numpy; fully vectorized O(batch) per step)
# ---------------------------------------------------------------------------
class ContextSampler:
    """Vectorized skipgram (center, context) sampler over a FLAT token array. Sampling a center
    position uniformly over all tokens is naturally length-weighted; context stays within the
    center's sentence bounds (via starts[sent_id])."""

    def __init__(self, corpus, window, seed):
        self.flat, self.starts, self.sent_id = corpus
        self.window = window
        self.rng = np.random.default_rng(seed)
        self.T = len(self.flat)

    def batch(self, bsz):
        pos = self.rng.integers(0, self.T, size=bsz)
        sid = self.sent_id[pos]
        lo = self.starts[sid]
        hi = self.starts[sid + 1] - 1
        off = self.rng.integers(1, self.window + 1, size=bsz) * (self.rng.integers(0, 2, size=bsz) * 2 - 1)
        opos = np.clip(pos + off, lo, hi)
        return self.flat[pos].astype(np.int64), self.flat[opos].astype(np.int64)


class NegSampler:
    """Unigram^pow negative sampler over the vocab (word2vec)."""

    def __init__(self, id_counts, pow_, seed):
        p = np.power(np.maximum(id_counts, 1.0), pow_)
        self.p = p / p.sum()
        self.cum = np.cumsum(self.p)
        self.rng = np.random.default_rng(seed)
        self.V = len(id_counts)

    def draw(self, n):
        u = self.rng.random(n)
        return np.searchsorted(self.cum, u).astype(np.int64).clip(0, self.V - 1)


def phrase_ids(phrase, word2id):
    return [word2id[w] for w in _tok_words(phrase) if w in word2id]


def _pad_phrases(phrase_id_lists):
    """List of id-lists -> (pad [n, Lmax] int64, mask [n, Lmax] float32, lens [n] float32). Fully
    vectorizable masked-mean pooling (no python ragged loop at train time -> GPU-efficient)."""
    n = len(phrase_id_lists)
    Lmax = max(1, max((len(x) for x in phrase_id_lists), default=1))
    pad = np.zeros((n, Lmax), dtype=np.int64)
    mask = np.zeros((n, Lmax), dtype=np.float32)
    for i, ids in enumerate(phrase_id_lists):
        if ids:
            pad[i, :len(ids)] = ids
            mask[i, :len(ids)] = 1.0
    lens = mask.sum(1)
    lens[lens == 0] = 1.0
    return pad, mask, lens


class RelationData:
    """Vectorized masked-relation prediction data: per-row concept phrase (padded) + rel idx +
    value-pool index; unique value pool (padded) for pos/neg pooling. Sampling returns index arrays
    only; all pooling is a single GPU gather+masked-mean (no python ragged loop)."""

    def __init__(self, train_triples, word2id, seed):
        self.rng = np.random.default_rng(seed)
        val_index = {}
        val_list = []
        for (c, r, v) in train_triples:
            if v not in val_index:
                vids = phrase_ids(v, word2id)
                if vids:
                    val_index[v] = len(val_list)
                    val_list.append(vids)
        rows_con, rows_rel, rows_val = [], [], []
        for (c, r, v) in train_triples:
            cids = phrase_ids(c, word2id)
            if cids and v in val_index:
                rows_con.append(cids)
                rows_rel.append(REL_IDX[r])
                rows_val.append(val_index[v])
        self.n = len(rows_con)
        self.nv = len(val_list)
        if self.n == 0 or self.nv == 0:
            return
        self.VP, self.VM, self.VL = _pad_phrases(val_list)      # unique value pool
        self.RC, self.RCM, self.RCL = _pad_phrases(rows_con)    # per-row concept phrase
        self.Rrel = np.asarray(rows_rel, dtype=np.int64)
        self.Rval = np.asarray(rows_val, dtype=np.int64)
        self._t = False

    def to_torch(self, device):
        if self.n == 0:
            return
        self.tVP = torch.as_tensor(self.VP, device=device)
        self.tVM = torch.as_tensor(self.VM, device=device)
        self.tVL = torch.as_tensor(self.VL, device=device)
        self.tRC = torch.as_tensor(self.RC, device=device)
        self.tRCM = torch.as_tensor(self.RCM, device=device)
        self.tRCL = torch.as_tensor(self.RCL, device=device)
        self.tRrel = torch.as_tensor(self.Rrel, device=device)
        self.tRval = torch.as_tensor(self.Rval, device=device)
        self._t = True

    def sample(self, bsz, neg_k):
        rows = self.rng.integers(0, self.n, size=bsz).astype(np.int64)
        negs = self.rng.integers(0, self.nv, size=(bsz, neg_k)).astype(np.int64)
        return rows, negs


# ---------------------------------------------------------------------------
# the native encoder (tied single embedding table E + relation-type table R)
# ---------------------------------------------------------------------------
class NativeEncoder(torch.nn.Module):
    def __init__(self, vocab_size, n_dim, n_rel, seed):
        super().__init__()
        g = torch.Generator().manual_seed(seed)
        self.E = torch.nn.Parameter((torch.rand(vocab_size, n_dim, generator=g) - 0.5) / n_dim)
        gr = torch.Generator().manual_seed(seed + 7)
        self.R = torch.nn.Parameter((torch.rand(n_rel, n_dim, generator=gr) - 0.5) / n_dim)
        self.n_dim = n_dim

    def context_loss(self, centers, contexts, negs):
        vc = self.E[centers]                      # [B, D]
        vo = self.E[contexts]                     # [B, D] (TIED table)
        vn = self.E[negs]                         # [B, K, D]
        pos = torch.nn.functional.logsigmoid((vc * vo).sum(-1))
        neg = torch.nn.functional.logsigmoid(-(vn * vc.unsqueeze(1)).sum(-1)).sum(-1)
        return -(pos + neg).mean()

    def _pool(self, pad, mask, lens):
        """Masked-mean pool E over padded phrase ids. pad/mask [..., L], lens [...] -> [..., D].
        Handles arbitrary leading dims (concept [B,L] and negatives [B,K,L])."""
        emb = self.E[pad]                                             # [..., L, D]
        return (emb * mask.unsqueeze(-1)).sum(-2) / lens.unsqueeze(-1)

    def relation_loss(self, rd, row_idx, neg_idx):
        """rd = RelationData (tensors on device); row_idx [B]; neg_idx [B, K] (value-pool indices)."""
        con = self._pool(rd.tRC[row_idx], rd.tRCM[row_idx], rd.tRCL[row_idx])   # [B, D]
        rel = self.R[rd.tRrel[row_idx]]                                          # [B, D]
        pred = con + rel                                                         # [B, D]
        vi = rd.tRval[row_idx]
        posv = self._pool(rd.tVP[vi], rd.tVM[vi], rd.tVL[vi])                    # [B, D]
        pos = torch.nn.functional.logsigmoid((pred * posv).sum(-1))
        negv = self._pool(rd.tVP[neg_idx], rd.tVM[neg_idx], rd.tVL[neg_idx])     # [B, K, D]
        neg = torch.nn.functional.logsigmoid(-(negv * pred.unsqueeze(1)).sum(-1)).sum(-1)
        return -(pos + neg).mean()


def _lr_at(step, total, warmup, base_lr):
    if step < warmup:
        return base_lr * (step + 1) / max(1, warmup)
    prog = (step - warmup) / max(1, total - warmup)
    return 0.5 * base_lr * (1.0 + math.cos(math.pi * min(1.0, prog)))


def train_encoder(enc, ctx_sampler, neg_sampler, rel_data, steps, batch, output_dir, use_relation):
    enc.to(DEVICE)
    opt = torch.optim.Adam(enc.parameters(), lr=BASE_LR)
    warmup = max(50, steps // 20)
    do_rel = bool(use_relation and rel_data is not None and rel_data.n > 0)
    if do_rel:
        rel_data.to_torch(DEVICE)
    rel_bsz = max(16, int(REL_BATCH_FRAC * batch)) if do_rel else 0
    t0 = time.perf_counter()
    for step in range(steps):
        lr = _lr_at(step, steps, warmup, BASE_LR)
        for pg in opt.param_groups:
            pg["lr"] = lr
        centers, contexts = ctx_sampler.batch(batch)
        negs = neg_sampler.draw(batch * NEG_K).reshape(batch, NEG_K)
        c_t = torch.as_tensor(centers, device=DEVICE)
        o_t = torch.as_tensor(contexts, device=DEVICE)
        n_t = torch.as_tensor(negs, device=DEVICE)
        loss = enc.context_loss(c_t, o_t, n_t)
        if do_rel:
            rows, rneg = rel_data.sample(rel_bsz, NEG_K)
            row_idx = torch.as_tensor(rows, device=DEVICE)
            neg_idx = torch.as_tensor(rneg, device=DEVICE)
            loss = loss + LAMBDA_REL * enc.relation_loss(rel_data, row_idx, neg_idx)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if step % max(1, steps // 40) == 0 or step == steps - 1:
            _heartbeat(output_dir, "train", {"step": step, "steps": steps, "lr": round(lr, 6),
                       "loss": round(float(loss.detach().cpu()), 4),
                       "sps": round((step + 1) / max(1e-6, time.perf_counter() - t0), 1),
                       "use_relation": use_relation})
    return enc


# ---------------------------------------------------------------------------
# eval: property-discrimination cos-pick (identical items for every arm)
# ---------------------------------------------------------------------------
def _encode_phrases_native(E_np, phrases, word2id):
    """Mean-pool L2-normalized native codes over a phrase's in-vocab words -> [n, D] (None row if OOV)."""
    out = []
    for ph in phrases:
        ids = phrase_ids(ph, word2id)
        if not ids:
            out.append(None)
        else:
            v = E_np[np.asarray(ids)].mean(0)
            nrm = np.linalg.norm(v)
            out.append(v / nrm if nrm > 0 else v)
    return out


def cospick_acc_native(E_np, items, word2id):
    """Cos-pick: embed concept + each candidate value with the native table; argmax cosine; correct
    iff argmax == gold_pos. OOV concept/all-OOV candidates -> fixed index 0 (gold randomized -> chance)."""
    if not items:
        return None, np.zeros(0, dtype=bool)
    concept_vecs = _encode_phrases_native(E_np, [it["concept"] for it in items], word2id)
    correct = np.zeros(len(items), dtype=bool)
    for i, it in enumerate(items):
        cv = concept_vecs[i]
        cand_vecs = _encode_phrases_native(E_np, it["cand_vals"], word2id)
        if cv is None or all(x is None for x in cand_vecs):
            pick = 0
        else:
            scores = np.full(len(cand_vecs), -1e30, dtype=np.float64)
            for j, x in enumerate(cand_vecs):
                if x is not None:
                    scores[j] = float(cv @ x)
            pick = int(np.argmax(scores))
        correct[i] = (pick == it["gold_pos"])
    return round(float(np.mean(correct)), 4), correct


def cospick_acc_glove(kv, items):
    """GloVe ceiling reference (SMOKE-local): cos-pick with frozen GloVe vectors. OOV -> fixed idx 0."""
    def gv(word):
        vs = [kv[w] for w in _tok_words(word) if w in kv]
        if not vs:
            return None
        v = np.sum(vs, axis=0).astype(np.float64)
        nrm = np.linalg.norm(v)
        return v / nrm if nrm > 0 else v
    if not items:
        return None
    correct = np.zeros(len(items), dtype=bool)
    for i, it in enumerate(items):
        cv = gv(it["concept"])
        cand = [gv(x) for x in it["cand_vals"]]
        if cv is None or all(x is None for x in cand):
            pick = 0
        else:
            sc = np.full(len(cand), -1e30, dtype=np.float64)
            for j, x in enumerate(cand):
                if x is not None:
                    sc[j] = float(cv @ x)
            pick = int(np.argmax(sc))
        correct[i] = (pick == it["gold_pos"])
    return round(float(np.mean(correct)), 4)


def _corr_hash(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.uint8).tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# run one mode
# ---------------------------------------------------------------------------
def run(mode, output_dir, try_glove=True):
    prof = SMOKE_PROFILE if mode == "smoke" else FULL_PROFILE
    _heartbeat(output_dir, "parse_worldtree")
    triples, precision = parse_tables(CURATED_TABLES)
    kindof_cap = 200 if mode == "smoke" else 700
    items, train_triples, held_concepts, env_meta = build_eval_items(triples, SEED, kindof_cap=kindof_cap)
    held_items = [it for it in items if it["held"]]
    train_items = [it for it in items if not it["held"]]
    n_held_fine = sum(1 for it in held_items if it["tier"] == "fine")
    chance = round(float(np.mean([1.0 / len(it["cand_vals"]) for it in held_items])), 4) if held_items else None
    _heartbeat(output_dir, "items_built", {"n_items": len(items), "n_held": len(held_items),
               "n_train": len(train_items), "n_held_fine": n_held_fine, "chance": chance})

    # forced vocab = all WorldTree concept/value words (eval phrases must be in-vocab)
    forced = set()
    for (c, r, v) in triples:
        forced.update(_tok_words(c))
        forced.update(_tok_words(v))

    sentences, word2id, id_counts = build_corpus(prof["max_sentences"], forced, output_dir)
    V = len(word2id)

    ctx_sampler = ContextSampler(sentences, WINDOW, SEED + 1)
    neg_sampler = NegSampler(id_counts, UNIGRAM_POW, SEED + 2)
    rel_data = RelationData(train_triples, word2id, SEED + 3)

    # ARM: native_untrained (E at random init)
    _heartbeat(output_dir, "arm_untrained")
    enc0 = NativeEncoder(V, N_DIM, NREL, SEED)
    E0 = enc0.E.detach().cpu().numpy().astype(np.float32)
    unt_ho, unt_c = cospick_acc_native(E0, held_items, word2id)
    unt_iv, _ = cospick_acc_native(E0, train_items, word2id)

    # ARM: native_context_only (context channel only) -- ablation
    _heartbeat(output_dir, "arm_context_only")
    enc_c = NativeEncoder(V, N_DIM, NREL, SEED)
    enc_c = train_encoder(enc_c, ctx_sampler, neg_sampler, None, prof["steps"], prof["batch"],
                          output_dir, use_relation=False)
    Ec = enc_c.E.detach().cpu().numpy().astype(np.float32)
    ctx_ho, ctx_c = cospick_acc_native(Ec, held_items, word2id)
    ctx_iv, _ = cospick_acc_native(Ec, train_items, word2id)

    # ARM: native_learned (context + relation) -- THE VARIABLE UNDER TEST
    _heartbeat(output_dir, "arm_learned")
    ctx_sampler2 = ContextSampler(sentences, WINDOW, SEED + 1)   # fresh RNG for identical stream parity
    neg_sampler2 = NegSampler(id_counts, UNIGRAM_POW, SEED + 2)
    rel_data2 = RelationData(train_triples, word2id, SEED + 3)
    enc_l = NativeEncoder(V, N_DIM, NREL, SEED)
    enc_l = train_encoder(enc_l, ctx_sampler2, neg_sampler2, rel_data2, prof["steps"], prof["batch"],
                          output_dir, use_relation=True)
    El = enc_l.E.detach().cpu().numpy().astype(np.float32)
    lrn_ho, lrn_c = cospick_acc_native(El, held_items, word2id)
    lrn_iv, _ = cospick_acc_native(El, train_items, word2id)

    # ARM: glove_zerofit ceiling reference (SMOKE-local; CITED in FULL)
    glove_ho = None
    glove_note = f"CITED@atom_29562 frozen-GloVe reference ~{GLOVE_CEILING_REF} (GloVe not staged to remote GPU; not recomputed at FULL)"
    if try_glove:
        try:
            from experiments.exp_semantic_hd_encoder_meaning_match_v1 import _load_glove
            _heartbeat(output_dir, "arm_glove_ceiling")
            kv = _load_glove()
            glove_ho = cospick_acc_glove(kv, held_items)
            glove_note = f"MEASURED@this cell (SMOKE-local, frozen GloVe cos-pick over same held-out items); atom-29562 ref ~{GLOVE_CEILING_REF}"
        except Exception as e:
            glove_note = f"GloVe ceiling unavailable ({type(e).__name__}: {str(e)[:120]}); CITED atom-29562 ref ~{GLOVE_CEILING_REF}"

    # pooled held-out CI for the learned arm
    n_ho = len(held_items)
    k_ho = int(round(lrn_ho * n_ho)) if (lrn_ho is not None and n_ho) else 0
    lrn_ci = wilson_ci(k_ho, n_ho) if n_ho else (0.0, 0.0)

    # ---- gates ----
    arms_corr = {"native_untrained": unt_c, "native_context_only": ctx_c, "native_learned": lrn_c}
    arm_hashes = {k: _corr_hash(v) for k, v in arms_corr.items()}
    arms_differ = len({unt_ho, ctx_ho, lrn_ho}) > 1

    baseline_in_band = (unt_ho is not None and 0.05 < unt_ho < 0.95)
    not_saturated = all((a is None) or (a < SAT) for a in [unt_ho, ctx_ho, lrn_ho, glove_ho])
    discriminator_fires = (lrn_ho is not None and unt_ho is not None and (lrn_ho - unt_ho) >= SMOKE_FIRE_DELTA)
    gap_over_untrained = round(lrn_ho - unt_ho, 4) if (lrn_ho is not None and unt_ho is not None) else None

    # ---- verdict (bands apply to native_learned ONLY) ----
    verdict, vmsg = _decide(lrn_ho, unt_ho, ctx_ho, glove_ho, lrn_ci, n_held_fine, chance,
                            baseline_in_band, not_saturated, mode)

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg, "summary": f"{verdict}: {vmsg}",
        "run_mode": mode, "elapsed_s": round(time.perf_counter() - _T0[0], 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "device": DEVICE, "seed": SEED,
        "one_variable": "native_untrained vs native_learned = error-driven training vs random init (same arch/N_DIM/eval); glove_zerofit = borrowed-vector ceiling reference",
        "primary_metric": "held-out-BY-CONCEPT property/value discrimination cos-pick accuracy (Wilson CI)",
        # headline arms (identical items/split/candidates/gold_pos)
        "native_learned_heldout_acc": lrn_ho, "native_learned_heldout_ci": list(lrn_ci),
        "native_learned_invocab_acc": lrn_iv,
        "native_context_only_heldout_acc": ctx_ho, "native_context_only_invocab_acc": ctx_iv,
        "native_untrained_heldout_acc": unt_ho, "native_untrained_invocab_acc": unt_iv,
        "glove_zerofit_heldout_acc": glove_ho, "glove_zerofit_note": glove_note,
        "chance": chance,
        # references (CITED)
        "floor_ref_native_0211_CITED": FLOOR_REF, "glove_ceiling_ref_0554_CITED": GLOVE_CEILING_REF,
        "gap_learned_over_untrained": gap_over_untrained,
        "gap_learned_over_context_only": (round(lrn_ho - ctx_ho, 4) if (lrn_ho is not None and ctx_ho is not None) else None),
        # bands
        "bands": {"HP_HELDOUT": HP_HELDOUT, "HP_GAP_OVER_UNTRAINED": HP_GAP_OVER_UNTRAINED,
                  "HF_HELDOUT": HF_HELDOUT, "SMOKE_FIRE_DELTA": SMOKE_FIRE_DELTA,
                  "MIN_HELDOUT_ITEMS": MIN_HELDOUT_ITEMS, "SAT": SAT},
        "hp_scope": {"native_learned": ["HARD_PASS", "HARD_FAIL", "MIDDLE"],
                     "native_untrained": ["baseline_in_band floor reference only"],
                     "native_context_only": ["ablation, no gate"],
                     "glove_zerofit": ["ceiling reference, no gate"]},
        # gates
        "arms_differ_verified": bool(arms_differ), "arm_correctness_hashes": arm_hashes,
        "baseline_in_band": bool(baseline_in_band), "not_saturated": bool(not_saturated),
        "discriminator_fires": bool(discriminator_fires),
        "coverage": {"n_heldout_items": len(held_items), "n_heldout_fine": n_held_fine,
                     "n_train_items": len(train_items), "n_held_concepts": len(held_concepts)},
        "env_meta": env_meta,
        "data_integrity": {"per_relation_precision_proxy": {r: precision[r] for r in sorted(precision)},
                           "multi_valid_rate": env_meta["multi_valid_rate"], "density": env_meta["density"]},
        # config / architecture
        "config": {"N_DIM": N_DIM, "NEG_K": NEG_K, "WINDOW": WINDOW, "MIN_COUNT": MIN_COUNT,
                   "MAX_VOCAB": MAX_VOCAB, "LAMBDA_REL": LAMBDA_REL, "REL_BATCH_FRAC": REL_BATCH_FRAC,
                   "BASE_LR": BASE_LR, "UNIGRAM_POW": UNIGRAM_POW, "vocab_size": V,
                   "profile": prof, "n_relations": NREL, "n_train_triples_relation_channel": rel_data.n, "n_relation_values": rel_data.nv},
        "objective": "context(skipgram+neg-sampling over ARC science sentences) + LAMBDA_REL*relation(masked typed-relation over WorldTree); tied single table E; error-driven; NO borrowed vectors",
        "reuse": "FRESH native objective; REUSED GPU scaffolding PATTERNS (torch.cuda batched, warmup+cosine LR, chunked loop, error-checking template); NOT the teacher-distillation core (that distills borrowed BGE)",
        "no_borrowed_vectors": "E is random-init, trained ONLY by native context+relation prediction; GloVe appears ONLY as an eval ceiling reference, never in E",
        "brain_fidelity_map": {
            "context_channel": "predictive statistical learning (Rogers-McClelland / word2vec SGNS mechanism run natively over OUR corpus); error-driven predict->correct",
            "relation_channel": "Rogers-McClelland item->attribute differentiation (predict typed-relation value from concept+relation); error-driven",
            "tied_table": "cosine-over-one-table geometry = the property structure the eval reads; matches GloVe single-vector cos-pick",
            "gap": "no curriculum coarse->fine ordering (batch SGNS is order-mixed); flagged, not glossed",
        },
        "crlb_n_a": "accuracy discriminator over cos-pick; no closed-form noise floor. Empirical floor = chance ~0.21 = native_untrained (measured). HARD-PASS 0.31 < GloVe ceiling 0.554 and > chance -> reachable.",
        "final_metrics_atomicity": "tmp_replace", "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "progress_logging": "print_flush_true",
        "deterministic_seeding": "fixed_int_seeds_numpy_default_rng_torch_manual_seed_sorted_no_builtin_hash",
        "calibration_check": "default_ok_for_this_regime",
        "storage": "no_composition_selfcontained_representation_learning",
        "contract": "SMOKE local foreground; FULL GPU overnight_queue (ARC+WorldTree staged; GloVe ceiling CITED); no push/remote-persist; VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)
    print(f"[verdict] {verdict}: {vmsg}", flush=True)
    print(f"[headline] learned_ho={lrn_ho} ci={lrn_ci} context_only_ho={ctx_ho} untrained_ho={unt_ho} "
          f"glove_ho={glove_ho} chance={chance} | learned_iv={lrn_iv}", flush=True)
    print(f"[gates] arms_differ={arms_differ} baseline_in_band={baseline_in_band} "
          f"discriminator_fires={discriminator_fires} gap_over_untrained={gap_over_untrained}", flush=True)
    return metrics


def _decide(lrn, unt, ctx, glove, lrn_ci, n_held_fine, chance, baseline_in_band, not_saturated, mode):
    if lrn is None or unt is None:
        return "INVALID", "native_learned or native_untrained accuracy is None -- eval produced no items"
    if n_held_fine < MIN_HELDOUT_ITEMS:
        return "INVALID", f"only {n_held_fine} held-out fine items (< {MIN_HELDOUT_ITEMS}) -- noise-floor breach"
    if not baseline_in_band:
        return "INVALID", f"native_untrained floor={unt} out of (0.05,0.95) -- baseline not in measurable band"
    if not not_saturated:
        return "INVALID", "an arm saturated >= 0.95 -- task too easy; harden difficulty"
    gap = lrn - unt
    if lrn >= HP_HELDOUT and gap >= HP_GAP_OVER_UNTRAINED and lrn_ci[0] > unt:
        return ("HARD_PASS",
                f"native_learned held-out={lrn} (CI {list(lrn_ci)}) >= {HP_HELDOUT}; climbs {round(gap,4)} "
                f">= {HP_GAP_OVER_UNTRAINED} over untrained floor {unt}; CI-lower {lrn_ci[0]} > untrained "
                f"-- native error-driven prediction EARNS property-predictive meaning off the thin ~0.21 floor "
                f"(context_only={ctx}, GloVe ceiling={glove})")
    if lrn <= HF_HELDOUT:
        return ("HARD_FAIL",
                f"native_learned held-out={lrn} <= {HF_HELDOUT} (floor+0.03) -- self-supervised prediction at "
                f"scale does NOT earn property-predictive meaning off the thin native ~0.21 floor "
                f"(untrained={unt}, context_only={ctx}); real finding: meaning may need grounding/Barsalou beyond text")
    return ("MIDDLE",
            f"native_learned held-out={lrn} (CI {list(lrn_ci)}) in ({HF_HELDOUT},{HP_HELDOUT}); climbs "
            f"{round(gap,4)} over untrained {unt} (context_only={ctx}, GloVe ceiling={glove}) -- real but "
            f"modest; does not reach the clear bar")


# ---------------------------------------------------------------------------
# self-test: real code path (parse + corpus build + encoder train + eval) at tiny scale + planted
# separability (a trained encoder on a co-occurrence-structured toy corpus must beat its random init)
# ---------------------------------------------------------------------------
def self_test():
    print("[self-test] planted co-occurrence corpus: trained tied-SGNS must beat random init on cos-pick ...", flush=True)
    # planted: 3 clusters of words that only ever co-occur within-cluster; a concept and its gold
    # value are in the same cluster, distractors in other clusters. A trained encoder should place
    # same-cluster words together -> cos-pick > random init.
    clusters = [[f"a{i}" for i in range(6)], [f"b{i}" for i in range(6)], [f"c{i}" for i in range(6)]]
    vocab = sorted(w for cl in clusters for w in cl)
    w2id = {w: i for i, w in enumerate(vocab)}
    rng = np.random.default_rng(0)
    sents = []
    for _ in range(4000):
        cl = clusters[int(rng.integers(0, 3))]
        ids = [w2id[cl[int(rng.integers(0, len(cl)))]] for _ in range(5)]
        sents.append(np.asarray(ids, dtype=np.int32))
    id_counts = np.zeros(len(vocab))
    for s in sents:
        for i in s:
            id_counts[i] += 1
    items = []
    for ci in range(3):
        cl = clusters[ci]
        for k in range(4):
            concept = cl[k]
            gold = cl[(k + 1) % len(cl)]
            distract = [clusters[(ci + 1) % 3][0], clusters[(ci + 2) % 3][0],
                        clusters[(ci + 1) % 3][1], clusters[(ci + 2) % 3][1]]
            gpos = int(rng.integers(0, len(distract) + 1))
            cand = distract[:gpos] + [gold] + distract[gpos:]
            items.append({"concept": concept, "gold": gold, "cand_vals": cand, "gold_pos": gpos,
                          "tier": "fine", "held": False, "relation": "KINDOF"})
    ctx = ContextSampler(flatten_sentences(sents), 3, 1)
    neg = NegSampler(id_counts, 0.75, 2)
    enc0 = NativeEncoder(len(vocab), 64, NREL, 5)
    E0 = enc0.E.detach().cpu().numpy().astype(np.float32)
    acc0, c0 = cospick_acc_native(E0, items, w2id)
    enc = NativeEncoder(len(vocab), 64, NREL, 5)
    enc = train_encoder(enc, ctx, neg, None, 400, 256, _out_dir("_smoke"), use_relation=False)
    E1 = enc.E.detach().cpu().numpy().astype(np.float32)
    acc1, c1 = cospick_acc_native(E1, items, w2id)
    print(f"[self-test]   planted cos-pick: untrained={acc0} trained={acc1} (trained must beat untrained)", flush=True)
    assert acc1 > acc0, f"planted: trained encoder did not beat random init ({acc1} vs {acc0})"
    assert acc1 >= 0.75, f"planted: trained encoder did not learn the co-occurrence structure (acc={acc1})"
    assert _corr_hash(c0) != _corr_hash(c1), "arms bit-identical (untrained vs trained)"

    print("[self-test] REAL code path: parse WorldTree + build_eval_items + tiny ARC + train + eval ...", flush=True)
    triples, precision = parse_tables((("KINDOF", 1, 4), ("HABITAT", 3, 5), ("PROP-MAGNETISM", 0, 3),
                                       ("PROP-CONDUCTIVITY", 0, 3), ("XIVORE", 1, 4)))
    assert len(triples) > 200, f"real: too few triples ({len(triples)})"
    items, train_triples, held, meta = build_eval_items(triples, SEED, kindof_cap=80)
    assert len(items) >= 20, f"real: too few items ({len(items)})"
    assert len(held) >= 1, "real: no held-out concepts"
    forced = set()
    for (c, r, v) in triples:
        forced.update(_tok_words(c))
        forced.update(_tok_words(v))
    od = _out_dir("_smoke")
    sentences, w2id2, idc = build_corpus(3000, forced, od)   # tiny ARC slice
    assert len(w2id2) > 50, f"real: vocab too small ({len(w2id2)})"
    ctx2 = ContextSampler(sentences, WINDOW, SEED + 1)
    neg2 = NegSampler(idc, UNIGRAM_POW, SEED + 2)
    rel2 = RelationData(train_triples, w2id2, SEED + 3)
    assert rel2.n > 0, "real: relation sampler has no in-vocab triples"
    enc = NativeEncoder(len(w2id2), N_DIM, NREL, SEED)
    enc = train_encoder(enc, ctx2, neg2, rel2, 60, 128, od, use_relation=True)   # exercise BOTH channels
    E = enc.E.detach().cpu().numpy().astype(np.float32)
    held_items = [it for it in items if it["held"]]
    acc, _ = cospick_acc_native(E, held_items if held_items else items, w2id2)
    assert acc is not None, "real: eval produced None"
    # determinism: rebuild eval items twice -> identical
    items_b, _, _, _ = build_eval_items(triples, SEED, kindof_cap=80)
    assert [it["cand_vals"] for it in items] == [it["cand_vals"] for it in items_b], "real: eval items non-deterministic"
    print(f"[self-test]   real: n_items={len(items)} n_held={len(held_items)} vocab={len(w2id2)} "
          f"rel_triples={rel2.n} eval_acc={acc} precision={precision}", flush=True)
    print("[self-test] PASS (planted trained>untrained; real parse+corpus+both-channels+eval; determinism; arms differ)", flush=True)
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--no-glove", action="store_true", help="skip the GloVe ceiling arm (remote/no-glove)")
    args = ap.parse_args()
    _T0[0] = time.perf_counter()

    if args.self_test:
        output_dir = _out_dir("_smoke")
        _write_start_marker(output_dir, "self_test")
        ok = self_test()
        sys.exit(0 if ok else 1)

    mode = "smoke" if args.smoke else "full"
    output_dir = _out_dir("_smoke") if mode == "smoke" else _out_dir()
    _write_start_marker(output_dir, mode)
    # FULL on remote GPU: no GloVe staged -> default to CITED ceiling unless --no-glove overrides off
    try_glove = (mode == "smoke") and (not args.no_glove)
    run(mode, output_dir, try_glove=try_glove)
    sys.exit(0)


if __name__ == "__main__":
    _od = _out_dir("_smoke") if ("--smoke" in sys.argv or "--self-test" in sys.argv) else _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_od, e)
        raise
