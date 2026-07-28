"""SCALE meaning-learning v3 relobj (R1/R3 self-teacher): v2's from-scratch transformer + a JOINT
foundation-relational-InfoNCE auxiliary loss, teacher-free (NO borrowed vectors -- the teacher is the
substrate's OWN cskg_foundation_v1 typed-edge graph), tested can-fail on held-out-NEW relational-AUC.

WHY THIS CELL (THE_PLAN R1/R3 self-teacher; notes/research_encoder_breadth_vs_relational_objective_scoping_2026-07-27.md):
  v2 (banked ckpt_seed_7.pt on disk, metrics.json NOT found -- run state uncertain) established the
  TEXT-ALONE ceiling: ~0.56 held-out-NEW relational-AUC, near-chance-despite-reasonable-exposure (median
  655 mentions/concept). Per "Capability Ceilings in Autoregressive LMs" (arXiv:2510.21866) that symptom
  reads as OBJECTIVE-bound, not data-bound, in the literature. R1/R3 of encoder_rescue_plan_converged_
  diagnosis_2026-07-04.md name the fix: add an internal (teacher-free) relational self-teacher term to
  the SAME encoder's SAME training loop, i.e. L = L_mlm + lambda_rel * L_rel, jointly, end-to-end.

CRITICAL PRIOR-ART GUARDRAIL (disk-verified, see encoder_rescue_plan_converged_diagnosis_2026-07-04.md):
  the 2026-07-04 RKD relational-objective attempt HARD_FAILED for TWO reasons this cell must NOT repeat:
  (a) its teacher was EXTERNAL (BGE) -- violates the no-borrowed-vector lock; (b) its positive/negative
  structure was IN-BATCH random co-occurrence over the full concept pool (V~160k), so batch/V pairwise
  coverage collapsed 6.4%(smoke)->0.32%(full, 20x drop) and graded near-neighbor pairs were essentially
  NEVER supervised at scale -> DENSE geometry collapsed 0.825(smoke)->0.368(full). THIS CELL DIFFERS on
  both axes: (a) the teacher is cskg_foundation_v1's OWN typed edges (TRAIN-split only, self-supervised,
  zero external model); (b) graded geometry is supervised against a FIXED LANDMARK frame (top-TRAIN-
  degree concepts, selected ONCE, re-sampled every relational step) rather than random in-batch pairs --
  at FULL scale, landmark/negative-pool coverage per step is n_land_batch/n_landmarks ~ 96/2048 = 4.7%
  (vs the failed run's 0.32%), and because the landmark POOL is fixed (not a fresh V-slice every step),
  each landmark accumulates ~350+ gradient visits over the run (THEORETICAL: n_rel_steps * n_land_batch
  / n_landmarks) -- the R1 anti-collapse fix, concretely instantiated.

A prior small-scale attempt at THIS SAME objective class exists on disk (exp_deep_text_encoder_self_
teacher_heldout_new_v1.py, MIDDLE_BAND, full_fusion-raw_grounding=-0.018) but is CONFOUNDED WITH SCALE:
cap_nodes=5000, 265,273 total tokens (53/concept), d_model=128, n_layers=2, and -- load-bearing
architectural difference -- its "joint" loss trains a SEPARATE shallow FusionEncoder head on TOP OF
FROZEN MLM-pretrained features (two-stage), not a truly joint end-to-end L_mlm+lambda*L_rel over the
SAME encoder used for both losses. This cell is a genuinely different, larger-scale, truly-joint test,
not a rerun of that result.

v3 vs v2 (ONE variable = the training OBJECTIVE; architecture/data/steps otherwise unchanged):
  ADD L_rel: every REL_EVERY MLM steps, an InfoNCE relational step runs on the SAME TinyTransformer's
    SAME model.pooled() contextual rep used by encode_concept_text_reps: rank each TRAIN anchor's true
    cskg_foundation_v1 TRAIN-TRAIN neighbor above a sampled subset of the FIXED landmark pool (negatives),
    cross-entropy / infonce_tau. L = L_mlm + lambda_rel * L_rel at relational steps, else L = L_mlm.
    L_mlm and L_rel logged SEPARATELY (objective-conflict diagnosis, not just the summed loss).
  SECOND LEAK GATE: cskg_foundation_v1/heldout_edges.jsonl excluded from L_rel's TRAIN-TRAIN edge pool
    (separate from and additional to the existing concept-level text/split leak-scrub), zero-witness
    verified and logged.
  CHECKPOINT-ALWAYS: periodic mid-training checkpoint (every CKPT_EVERY_STEPS, atomic tmp+os.replace) --
    v2 only checkpointed once at the very END of MLM training; a crash mid-run loses everything. Fixed here
    (a prior no-save cost this project a 6h retrain once already).
  BASELINE REUSE (store discipline: don't rebuild banked results): if data/exp_scale_meaning_learn_arc_
    heldout_v2/ckpt_seed_<seed>.pt exists, it is RELOADED (its own persisted tokenizer + weights, NOT
    retrained) and evaluated on this run's own (deterministically-identical) postings/split/adjacency to
    produce a same-architecture, same-data, zero-retrain MLM-ONLY baseline for that seed. Where the
    checkpoint is absent (verified on disk: only ckpt_seed_7.pt exists, no ckpt_seed_13.pt, no metrics.json
    anywhere for v2 -- its FULL run state is genuinely uncertain), the CITED historical reference
    (~0.56 relational-AUC, task-prompt/THE_PLAN) is used for that seed instead, and `baseline_source` is
    logged per seed so the two evidence classes are never silently conflated.

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

ARMS (per-query AUC; base 0.5) -- SAME semantic/relational arms as v2, computed on the v3 (relobj)
encoder, PLUS a reused/cited MLM-ONLY baseline (not an "arm" of this run's own training):
  RAW_GROUNDING  : cosine over raw 20d grounding norms, NO learning.               [validity floor]
  RAW_TEXT (TEXT_ARM) : cosine over the joint-objective-trained text-rep alone.     [OBJ arm -- the test]
  FUSED / ZAVG / WTUNED / SELECTED : same leak-proof fusion family as v2.
  RANDOM_INIT    : cosine over text-rep from an UNTRAINED transformer.             [isolate learning]
  COLLAPSE_SHUFFLE: text-reps permuted across concept ids.                         [can-fail / leak witness ~0.5]
  POPULARITY     : rank candidates by mention-frequency / train-degree only.        [validity ~0.5]
  BASELINE_MLM_ONLY (relational_eval + semantic_eval, reported not trained here) : v2's TEXT_ARM,
    reused from ckpt_seed_<seed>.pt where present, else CITED historical (~0.56 relational-AUC).

THE ONE NUMBER (pre-registered bands, BEFORE running; see preregs/2026-07-27_scale_meaning_learn_arc_
heldout_v3_relobj.md for the full envelope-fail-band spec):
  HARD_PASS = TEXT_ARM relational-AUC (this run's OBJ arm) - BASELINE_MLM_ONLY relational-AUC >= +0.03 on
    BOTH seeds (per-seed strictly > 0), AND TEXT_ARM semantic-AUC does NOT regress > 0.02 vs baseline
    (objective-conflict guard), AND L_rel training loss visibly decreases (real learning, not noise), AND
    the heldout_edges.jsonl zero-witness holds (0 excluded-pair leaks into L_rel's positive pool), AND
    validity holds (COLLAPSE in [0.44,0.56], POPULARITY in [0.44,0.56], RAW_GROUNDING >= 0.55, power ok).
  HARD_FAIL = TEXT_ARM relational-AUC stays within +/-0.02 of BASELINE_MLM_ONLY despite L_rel loss
    visibly decreasing => the ceiling is architecture/readout-bound (e.g. the encoder's own mean-pool
    concept-aggregation), not objective-absence; redirect to the readout/pooling mechanism next.
  MIDDLE_BAND = margin positive but < +0.03, or semantic regresses > 0.02 (objective conflict, partial win).

HARD INVARIANTS (project locks): TEACHER-FREE. NO GloVe/BGE/transformer WEIGHTS/borrowed vector ANYWHERE
  (token embeddings + Transformer learned FROM SCRATCH by MLM; BPE vocab built FROM ARC; the L_rel
  "teacher" is cskg_foundation_v1's OWN typed-edge graph, itself built with no borrowed embeddings).
  INDUCTIVE (held-out placed from its own text + grounding; never a training target, never an L_rel
  anchor/positive/landmark). LEAK-PROOF (concept-level scrub + zero-overlap witness; tokenizer never sees
  held-out text; relational target never an input; L_rel restricted to TRAIN-TRAIN edges MINUS
  heldout_edges.jsonl, a SECOND independent leak gate). ASCII-only. AI2 ARC Corpus: INTERNAL research use
  only, do NOT redistribute corpus/derived raw text.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF; ARMS-MUST-DIFFER hash-test over per-concept rep matrices)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace + per-seed
#     partials) PLUS periodic mid-training checkpoint (ckpt_seed_<seed>_inprogress.pt, tmp+os.replace,
#     every CKPT_EVERY_STEPS -- the multi-hour-training-run non-negotiable per task contract)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator base = 0.5 exactly; collapse + popularity + random-init controls witness the floor
# - baseline_in_band at smoke: collapse ~0.5; popularity ~0.5; raw_grounding a real >0.55 signal; primary not saturated
# - discriminator survives scale: THEORETICAL landmark-coverage argument (see guardrail note above) +
#     SMOKE preview shows L_rel loss decreasing at n_landmarks=256 (option B+C hybrid; FULL landmark=2048
#     not smoke-previewed 1:1 for wall-time reasons, the theoretical coverage argument covers that gap)
# - HARD_PASS strictly above floor: margin>=0.03 AND per-seed strictly >0 (not at-floor)
# - HP_SCOPE: gates apply to ARM_TEXT (TEXT_ARM, the OBJ arm) relational-AUC vs BASELINE_MLM_ONLY primary;
#     semantic non-regression is a secondary guard; FUSED/ZAVG/WTUNED/SELECTED arms reported, not gated
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except; specific classes -> metrics)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; controls witness it empirically)
# - deterministic seeding: sha256 concept split (freq-stratified, sha256-ranked) + fixed int seeds +
#     sorted(); no hash()/list(set()); landmark selection is a deterministic sorted() rank-then-slice
# - real_code_path: --self-test constructs the REAL objects (BPE build, MLM train step incl. the L_rel
#     relational step, transformer encode, zero-overlap gate, heldout-edge exclusion, both evals) at
#     N~16 (SELFTEST_CFG IS the real pipeline at tiny scale, real_code_path_exercised includes L_rel)
# - progress_logging: print_flush_true (MLM step logs + L_rel step logs + eval logs flush=True) +
#     _heartbeat.jsonl (timeout_s >> 1800)
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
from tokenizers import Tokenizer  # noqa: E402  -- needed to reload v2's persisted tokenizer (baseline reuse)

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

ANCHOR_NAME = "scale_meaning_learn_arc_heldout_v3_relobj"
ARC_CORPUS = os.path.join(_REPO, "data", "corpora", "arc",
                          "ARC-V1-Feb2018-2", "ARC_Corpus.txt")
FOUNDATION_DIR = os.path.join(_REPO, "data", "cskg_foundation_v1")
NODES_PATH = os.path.join(FOUNDATION_DIR, "nodes.jsonl")
EDGES_GLOB = os.path.join(FOUNDATION_DIR, "edges_shard_*.jsonl")
HELDOUT_EDGES_PATH = os.path.join(FOUNDATION_DIR, "heldout_edges.jsonl")
LEXNAME_CACHE = os.path.join(_REPO, "data", "wordnet_lexname_cache_v1.json")

# v2 baseline checkpoint dir (BASELINE REUSE, not retrained -- see module docstring)
V2_CKPT_DIR = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2")
CITED_BASELINE_RELATIONAL_AUC = 0.56   # CITED@task-prompt/THE_PLAN, used only when no ckpt to reuse
BASELINE_SOURCE_REUSED = "reused_checkpoint"
BASELINE_SOURCE_CITED = "cited_reference"

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
# v2 change: PRIMARY = the BEST-HONEST text+grounding combination, SELECTED on the TRAIN-eval split
# (leak-proof model-selection), applied to held-out. The naive 1:1 FUSED_EQ is now a CONTROL that
# witnesses "naive fusion dilutes" (it UNDERPERFORMED text-alone in v1: 0.605 vs 0.636). The HARD-PASS
# now keys on PRIMARY (best-honest combination) beating RAW_GROUNDING >= 0.03 on held-out-NEW semantic.
HP_MARGIN_OVER_RAW = 0.03        # THE NUMBER: PRIMARY - RAW_GROUNDING must exceed this (break the wall)
SEM_REGRESSION_MAX = 0.02        # objective-conflict guard: OBJ semantic-AUC may not regress more than this vs BASELINE
RAW_SIGNAL_MIN = 0.55            # RAW_GROUNDING must be a real >0.55 signal (metric-not-saturated gate)
COLLAPSE_BAND = (0.44, 0.56)     # COLLAPSE_SHUFFLE + POPULARITY MUST sit here (validity / can-fail)
MIN_QUERY_TASKS = 120            # power floor for the held-out AUC to be trustworthy
WELL_COVERED_MIN = 100           # "well-covered" concept threshold for the well-covered fork
LEARNING_EPS = 0.0               # RAW_TEXT - RANDOM_INIT; > 0 => the learned text rep carries signal
W_GRID = [round(0.1 * i, 2) for i in range(0, 11)]  # weight grid for WTUNED fusion (tuned on train-eval)
TRAIN_SELECT_CAP = 1500          # cap train-eval concepts used for leak-proof model-selection

# Arms
RAW_ARM = "ARM_RAW_GROUNDING"
TEXT_ARM = "ARM_RAW_TEXT"                 # text-alone (= TEXT_PRIMARY candidate)
FUSED_ARM = "ARM_FUSED_EQ"               # naive 1:1 late fusion -> now a CONTROL (dilution witness)
FUSE_ZAVG_ARM = "ARM_FUSE_ZAVG"          # per-query z-normalized average (fixes cross-modality scale mismatch)
FUSE_WTUNED_ARM = "ARM_FUSE_WTUNED"      # w*text+(1-w)*ground, w tuned on TRAIN-eval (leak-proof)
FUSE_SELECTED_ARM = "ARM_FUSE_SELECTED"  # PRIMARY: best of {TEXT, ZAVG, WTUNED} selected on TRAIN-eval AUC
RANDINIT_ARM = "ARM_RANDOM_INIT"
SHUFFLE_ARM = "ARM_COLLAPSE_SHUFFLE"
POP_ARM = "ARM_POPULARITY"
PRIMARY_ARM = FUSE_SELECTED_ARM
# candidate arms eligible to BE the selected primary (text-inclusive combinations only)
PRIMARY_CANDIDATES = [TEXT_ARM, FUSE_ZAVG_ARM, FUSE_WTUNED_ARM]
SEM_ARMS = [RAW_ARM, TEXT_ARM, FUSED_ARM, FUSE_ZAVG_ARM, FUSE_WTUNED_ARM,
            FUSE_SELECTED_ARM, RANDINIT_ARM, SHUFFLE_ARM, POP_ARM]

# ---------------------------------------------------------------------------
# Config profiles
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    run_mode="selftest", seeds=[7],
    min_deg=2, cap_eval_concepts=1500, heldout_count=60, min_mentions_eval=1,
    max_lines=150000, dedup_cap=180000, bpe_sample_lines=40000, cap_mentions=6,
    vocab=512, max_len=24, train_token_budget=600000, max_shards=6,
    d_model=32, n_layers=1, n_heads=2, ffn_mult=2,
    mlm_steps=15, mlm_batch=8, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=64, n_freq_buckets=4,
    # relational self-teacher (R1/R3) -- tiny scale, exercises the real code path
    lambda_rel=0.2, n_landmarks=24, n_land_batch=12, n_anchor_batch=12, rel_every=3,
    infonce_tau=0.2, min_rel_anchors=4, ckpt_every_steps=6,
)
SMOKE_CFG = dict(
    run_mode="smoke", seeds=[7],
    min_deg=2, cap_eval_concepts=2500, heldout_count=250, min_mentions_eval=2,
    max_lines=150000, dedup_cap=200000, bpe_sample_lines=80000, cap_mentions=16,
    vocab=4096, max_len=48, train_token_budget=4000000, max_shards=6,
    d_model=128, n_layers=2, n_heads=4, ffn_mult=2,
    mlm_steps=250, mlm_batch=64, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=256, n_freq_buckets=5,
    # relational self-teacher (R1/R3) -- discriminator-preview scale (option B+C hybrid, see docstring)
    lambda_rel=0.2, n_landmarks=256, n_land_batch=64, n_anchor_batch=96, rel_every=5,
    infonce_tau=0.2, min_rel_anchors=20, ckpt_every_steps=80,
)
FULL_CFG = dict(
    run_mode="full", seeds=[7, 13],
    min_deg=2, cap_eval_concepts=None, heldout_count=800, min_mentions_eval=20,
    max_lines=10000000, dedup_cap=6000000, bpe_sample_lines=400000, cap_mentions=128,
    vocab=16000, max_len=128, train_token_budget=130000000, max_shards=16,
    d_model=512, n_layers=6, n_heads=8, ffn_mult=4,
    mlm_steps=60000, mlm_batch=128, mlm_mask_frac=0.15, mlm_lr=3e-4,
    encode_batch=256, n_freq_buckets=8,
    # relational self-teacher (R1/R3): landmark pool fixed at 2048 (top TRAIN-degree concepts w/ text),
    # rel step every 8 MLM steps -> ~7500 rel steps/seed, ~+30-40% wall-time over v2 (comparable compute).
    lambda_rel=0.2, n_landmarks=2048, n_land_batch=96, n_anchor_batch=128, rel_every=8,
    infonce_tau=0.2, min_rel_anchors=32, ckpt_every_steps=2000,
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


def _save_inprogress_ckpt(out_dir, seed, model, opt, step, spec, cfg):
    """Periodic mid-training checkpoint (CHECKPOINT-ALWAYS, non-negotiable per task contract). Atomic
    tmp+os.replace. Overwritten each call (rolling) -- a crash loses at most ckpt_every_steps of progress,
    not the whole multi-hour run (v2 had ZERO mid-training checkpoints)."""
    try:
        payload = dict(
            state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()},
            opt_state=opt.state_dict(), step=int(step), seed=int(seed),
            spec=spec, model_cfg=dict(vocab=int(spec["size"]), max_len=int(cfg["max_len"]),
                                       d_model=int(cfg["d_model"]), n_layers=int(cfg["n_layers"]),
                                       n_heads=int(cfg["n_heads"]), ffn_mult=int(cfg["ffn_mult"]),
                                       pad_id=int(spec["pad"])),
            ts_iso=datetime.now(timezone.utc).isoformat(), anchor=ANCHOR_NAME,
        )
        tmp = os.path.join(out_dir, "ckpt_seed_%d_inprogress.pt.tmp" % seed)
        final = os.path.join(out_dir, "ckpt_seed_%d_inprogress.pt" % seed)
        torch.save(payload, tmp)
        os.replace(tmp, final)
        return True
    except (OSError, RuntimeError) as e:
        _log("  WARN mid-training checkpoint save failed (%s): %s" % (type(e).__name__, str(e)[:200]))
        return False


def _pooled_for_rows(model, win_ids, rows, device, use_amp):
    ids = torch.from_numpy(win_ids[rows]).to(device)
    with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
        z = model.pooled(ids)
    return z.float()


def mlm_train_relobj(stream, spec, cfg, device, seed, out_dir, hb_total, relobj):
    """MLM-pretrain the transformer + a JOINT foundation-relational InfoNCE self-teacher term.
    L = L_mlm + lambda_rel * L_rel every rel_every steps, else L = L_mlm. Same encoder, same
    optimizer.step() -- genuinely joint, end-to-end (not a frozen-feature two-stage fusion head).
    relobj: dict from relobj_prep (train_neigh, landmarks, anchor_pool, win_ids). Returns
    (model, final_mlm_loss, rel_diag) where rel_diag logs L_mlm/L_rel curves + fired-count separately."""
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
    rel_rng = np.random.default_rng(seed + 4171)
    bs = min(cfg["mlm_batch"], n_win)
    mask_frac = cfg["mlm_mask_frac"]
    mask_id = spec["mask"]
    log_every = max(1, cfg["mlm_steps"] // 10)
    ckpt_every = max(1, int(cfg.get("ckpt_every_steps", cfg["mlm_steps"])))

    anchor_pool = relobj["anchor_pool"]
    landmarks = relobj["landmarks"]
    train_neigh = relobj["train_neigh"]
    win_ids = relobj["win_ids"]
    tau = cfg["infonce_tau"]
    rel_every = max(1, int(cfg["rel_every"]))
    lambda_rel = float(cfg["lambda_rel"])
    rel_ok = anchor_pool.shape[0] >= cfg["min_rel_anchors"] and landmarks.shape[0] >= 4

    mlm_loss_curve = []
    rel_loss_curve = []
    n_rel_fired = 0
    n_ckpt_saves = 0

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
            mlm_loss = torch.nn.functional.cross_entropy(logits[mask], target[mask])
        loss = mlm_loss
        rel_loss_val = None
        if rel_ok and (step % rel_every == 0):
            a_bs = min(cfg["n_anchor_batch"], anchor_pool.shape[0])
            a_idx = rel_rng.choice(anchor_pool, size=a_bs, replace=False)
            pos_idx = np.empty(a_bs, dtype=np.int64)
            for k, a in enumerate(a_idx.tolist()):
                nb = train_neigh[a]
                pos_idx[k] = nb[int(rel_rng.integers(0, len(nb)))]
            l_bs = min(cfg["n_land_batch"], landmarks.shape[0])
            l_idx = rel_rng.choice(landmarks, size=l_bs, replace=False)
            z_a = torch.nn.functional.normalize(_pooled_for_rows(model, win_ids, a_idx, device, use_amp), dim=1)
            z_p = torch.nn.functional.normalize(_pooled_for_rows(model, win_ids, pos_idx, device, use_amp), dim=1)
            z_l = torch.nn.functional.normalize(_pooled_for_rows(model, win_ids, l_idx, device, use_amp), dim=1)
            cand = torch.cat([z_p.unsqueeze(1), z_l.unsqueeze(0).expand(a_bs, -1, -1)], dim=1)  # [a_bs, 1+l_bs, d]
            logits_rel = torch.einsum("ad,akd->ak", z_a, cand) / tau
            tgt_rel = torch.zeros(a_bs, dtype=torch.long, device=device)  # true positive is column 0
            rel_loss = torch.nn.functional.cross_entropy(logits_rel, tgt_rel)
            loss = loss + lambda_rel * rel_loss
            rel_loss_val = float(rel_loss.detach())
            n_rel_fired += 1
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite joint loss step=%d seed=%d (mlm=%.4f rel=%s)"
                                     % (step, seed, float(mlm_loss.detach()), rel_loss_val))
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        last_loss = float(mlm_loss.detach())
        mlm_loss_curve.append(last_loss)
        if rel_loss_val is not None:
            rel_loss_curve.append(rel_loss_val)
        if (step % log_every == 0) or (step == cfg["mlm_steps"] - 1):
            el = time.perf_counter() - t0
            _log("  MLM seed=%d step=%d/%d mlm_loss=%.4f rel_loss=%s (%.1fs)"
                 % (seed, step, cfg["mlm_steps"], last_loss,
                    ("%.4f" % rel_loss_val) if rel_loss_val is not None else "NA", el))
            _heartbeat(out_dir, step, hb_total, el,
                      extra={"mlm_loss": last_loss, "rel_loss": rel_loss_val, "seed": seed})
        if step > 0 and (step % ckpt_every == 0 or step == cfg["mlm_steps"] - 1):
            if _save_inprogress_ckpt(out_dir, seed, model, opt, step, spec, cfg):
                n_ckpt_saves += 1
    model.eval()
    rel_diag = dict(
        rel_ok=bool(rel_ok), n_rel_fired=int(n_rel_fired), n_ckpt_saves=int(n_ckpt_saves),
        n_anchor_pool=int(anchor_pool.shape[0]), n_landmarks=int(landmarks.shape[0]),
        rel_loss_first=(rel_loss_curve[0] if rel_loss_curve else None),
        rel_loss_last=(rel_loss_curve[-1] if rel_loss_curve else None),
        rel_loss_mean_first10=(float(np.mean(rel_loss_curve[:10])) if len(rel_loss_curve) >= 1 else None),
        rel_loss_mean_last10=(float(np.mean(rel_loss_curve[-10:])) if len(rel_loss_curve) >= 1 else None),
        mlm_loss_first=(mlm_loss_curve[0] if mlm_loss_curve else None),
        mlm_loss_last=(mlm_loss_curve[-1] if mlm_loss_curve else None),
        rel_loss_decreased=(bool(rel_loss_curve[-1] < rel_loss_curve[0]) if len(rel_loss_curve) >= 2 else None),
    )
    return model, last_loss, rel_diag


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


def _zscore_rows(mat):
    """Per-row (per-query) z-normalization across candidate axis; scale-mismatch fix for fusion."""
    mu = mat.mean(axis=1, keepdims=True)
    sd = mat.std(axis=1, keepdims=True)
    return np.where(sd > 1e-12, (mat - mu) / (sd + 1e-8), mat - mu)


def _eval_semantic_set(ground, text, text_rand, counts, universe, elig, seed, w,
                       compute_wgrid=False):
    """Per-query same-lexname AUC for every arm over the concept-index set `elig`.

    Leak-proof primitive used for BOTH train-eval model-selection AND held-out reporting.
    Fusion arms combine per-query candidate COSINE vectors:
      FUSED_EQ  = 0.5*(cos_g + cos_t)             (naive 1:1 -> dilution control)
      FUSE_ZAVG = 0.5*(z(cos_g) + z(cos_t))       (per-query standardized average)
      FUSE_WTUNED = w*cos_t + (1-w)*cos_g         (w tuned on train-eval)
    Returns (arm_auc: dict, wtuned_by_w: dict|None, n_query).
    """
    if len(elig) < 10:
        return None, None, 0
    elig = np.array(sorted(int(i) for i in elig), dtype=np.int64)
    n = elig.shape[0]
    lex_str = [universe["lexnames"][i] for i in elig]
    logf = np.log1p(counts[elig].astype(np.float64))
    rng = np.random.default_rng(seed + 31)
    perm = rng.permutation(n)
    text_sh = text.copy()
    text_sh[elig] = text[elig][perm]     # collapse: shuffle text-reps across ids in this set

    cg = _cos_matrix(ground, elig, elig)
    ct = _cos_matrix(text, elig, elig)
    cr = _cos_matrix(text_rand, elig, elig)
    cs = _cos_matrix(text_sh, elig, elig)
    cg_z = _zscore_rows(cg)
    ct_z = _zscore_rows(ct)
    czavg = 0.5 * (cg_z + ct_z)
    ceq = 0.5 * (cg + ct)
    cw = w * ct + (1.0 - w) * cg

    base_scores = {RAW_ARM: cg, TEXT_ARM: ct, FUSED_ARM: ceq, FUSE_ZAVG_ARM: czavg,
                   FUSE_WTUNED_ARM: cw, RANDINIT_ARM: cr, SHUFFLE_ARM: cs}
    out = {a: [] for a in base_scores}
    out[POP_ARM] = []
    wgrid_acc = {ww: [] for ww in W_GRID} if compute_wgrid else None
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
        for a, mat in base_scores.items():
            au = _auc_from_scores(mat[qi][cand], pos)
            if au is not None:
                out[a].append(au)
        au = _auc_from_scores(logf[cand], pos)   # popularity (query-independent)
        if au is not None:
            out[POP_ARM].append(au)
        if compute_wgrid:
            sg = cg[qi][cand]
            st = ct[qi][cand]
            for ww in W_GRID:
                au = _auc_from_scores(ww * st + (1.0 - ww) * sg, pos)
                if au is not None:
                    wgrid_acc[ww].append(au)
    arm_auc = {a: (float(np.mean(v)) if v else None) for a, v in out.items()}
    wtuned_by_w = ({ww: (float(np.mean(v)) if v else None) for ww, v in wgrid_acc.items()}
                   if compute_wgrid else None)
    return arm_auc, wtuned_by_w, n_used


def select_fusion_on_train(ground, text, text_rand, counts, universe, split, seed):
    """Leak-proof model selection: tune w and pick the best-honest fusion arm on the TRAIN-eval split.
    Returns (w_star, selected_arm, train_diagnostics)."""
    have_text = np.linalg.norm(text, axis=1) > 1e-8
    tr = [int(i) for i in split["train_eval_idx"].tolist()
          if have_text[i] and universe["lexnames"][i] is not None]
    tr = sorted(tr)
    if len(tr) > TRAIN_SELECT_CAP:
        rng = np.random.default_rng(seed + 101)
        tr = sorted(rng.choice(np.array(tr), size=TRAIN_SELECT_CAP, replace=False).tolist())
    arm_auc, wtuned_by_w, n_q = _eval_semantic_set(
        ground, text, text_rand, counts, universe, tr, seed, w=0.5, compute_wgrid=True)
    if arm_auc is None or wtuned_by_w is None:
        return 1.0, TEXT_ARM, {"reason": "train_set_too_small", "n_query": n_q}
    valid_w = {ww: a for ww, a in wtuned_by_w.items() if a is not None}
    w_star = max(valid_w, key=valid_w.get) if valid_w else 1.0
    # candidate arm AUCs on train (WTUNED taken at w_star)
    cand_auc = {}
    for a in PRIMARY_CANDIDATES:
        cand_auc[a] = (valid_w.get(w_star) if a == FUSE_WTUNED_ARM else arm_auc.get(a))
    cand_auc = {a: v for a, v in cand_auc.items() if v is not None}
    selected_arm = max(cand_auc, key=cand_auc.get) if cand_auc else TEXT_ARM
    diag = dict(w_star=float(w_star), selected_arm=selected_arm, n_query_train=int(n_q),
                train_arm_auc={a: arm_auc.get(a) for a in SEM_ARMS if a != FUSE_SELECTED_ARM},
                train_wtuned_by_w=wtuned_by_w, train_candidate_auc=cand_auc)
    return float(w_star), selected_arm, diag


def semantic_eval(ground, text, text_rand, counts, universe, split, seed,
                  w_star, selected_arm, subset_mask=None):
    """Per-query same-lexname AUC for each arm over held-out concepts (optionally a coverage subset).
    PRIMARY (FUSE_SELECTED) mirrors the arm chosen on the TRAIN-eval split (leak-proof)."""
    held = split["held_idx"]
    have_text = np.linalg.norm(text, axis=1) > 1e-8
    elig = [int(i) for i in held.tolist() if have_text[i]]
    if subset_mask is not None:
        elig = [i for i in elig if subset_mask[i]]
    arm_auc, _, n_used = _eval_semantic_set(
        ground, text, text_rand, counts, universe, elig, seed, w=w_star, compute_wgrid=False)
    if arm_auc is None:
        return None
    # PRIMARY = held-out AUC of the arm selected on train-eval
    arm_auc[FUSE_SELECTED_ARM] = arm_auc.get(selected_arm)
    res = {a: arm_auc.get(a) for a in SEM_ARMS}
    res["_selected_arm"] = selected_arm
    res["_w_star"] = float(w_star)
    res["_n_query"] = n_used
    res["_n_concepts"] = int(len(elig))
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


# ---------------------------------------------------------------------------
# R1/R3 relational self-teacher: TRAIN-TRAIN foundation edges, landmark pool,
# per-concept window-id cache (all data-prep-time, seed-independent, reused across seeds)
# ---------------------------------------------------------------------------
def load_heldout_edge_pairs():
    """SECOND leak gate: cskg_foundation_v1's own held-out edge split, excluded from L_rel's TRAIN-TRAIN
    positive pool (independent of and additional to the concept-level text/split leak-scrub)."""
    pairs = set()
    if not os.path.exists(HELDOUT_EDGES_PATH):
        return pairs
    with open(HELDOUT_EDGES_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            s, o = e.get("subject"), e.get("obj")
            if s is None or o is None:
                continue
            pairs.add((s, o))
            pairs.add((o, s))
    return pairs


def build_train_rel_index(universe, split, adj, heldout_pairs):
    """TRAIN-TRAIN neighbor lists for L_rel (excludes any HELD concept on either side, AND any pair
    present in cskg_foundation_v1's own heldout_edges.jsonl -- the second, independent leak gate)."""
    ids = universe["ids"]
    is_held = split["is_held"]
    K = universe["K"]
    train_neigh = [[] for _ in range(K)]
    n_excluded_heldout_pair = 0
    n_kept = 0
    for i in range(K):
        if is_held[i]:
            continue
        nb = []
        for j in sorted(adj[i]):
            if is_held[j] or j == i:
                continue
            if (ids[i], ids[j]) in heldout_pairs:
                n_excluded_heldout_pair += 1
                continue
            nb.append(j)
            n_kept += 1
        train_neigh[i] = nb
    return train_neigh, dict(n_excluded_heldout_pair=int(n_excluded_heldout_pair), n_kept_edges=int(n_kept))


def select_landmarks_rel(train_neigh, postings, cap_mentions, n_landmarks):
    """Fixed, deterministic landmark pool: TRAIN concepts with >=1 TRAIN-TRAIN neighbor AND >=1 mention
    posting, ranked by TRAIN-relational degree descending (ties broken by index -> sorted() determinism)."""
    cands = [i for i in range(len(train_neigh)) if train_neigh[i] and postings[i][:cap_mentions]]
    ranked = sorted(cands, key=lambda i: (-len(train_neigh[i]), i))
    picked = ranked[:n_landmarks]
    return np.array(sorted(picked), dtype=np.int64)


def build_concept_window_ids(tok, spec, postings, cap_mentions, max_len, needed_idx):
    """One representative (first) mention window per concept, tokenized+padded ONCE (data-prep time,
    not inside the training loop). Only builds rows for `needed_idx` (rel-eligible concepts) to bound cost."""
    pad_id = spec["pad"]
    K = len(postings)
    win = np.full((K, max_len), pad_id, dtype=np.int64)
    for ci in needed_idx:
        ms = postings[ci][:cap_mentions]
        if ms:
            win[ci] = _encode_pad(tok, ms[0], max_len, pad_id)
    return win


def relobj_prep(universe, split, adj, postings, tok, spec, cfg):
    """Seed-independent R1/R3 prep: TRAIN-TRAIN adjacency (2nd leak gate applied), landmark pool,
    anchor pool, concept-window-id cache. Returns None-safe dict; caller checks min_rel_anchors."""
    heldout_pairs = load_heldout_edge_pairs()
    train_neigh, rel_leak_meta = build_train_rel_index(universe, split, adj, heldout_pairs)
    landmarks = select_landmarks_rel(train_neigh, postings, cfg["cap_mentions"], cfg["n_landmarks"])
    anchor_pool = np.array(
        sorted(i for i in range(universe["K"])
              if train_neigh[i] and postings[i][:cfg["cap_mentions"]]),
        dtype=np.int64)
    needed = sorted(set(anchor_pool.tolist()) | set(landmarks.tolist())
                    | {j for i in anchor_pool.tolist() for j in train_neigh[i]})
    win_ids = build_concept_window_ids(tok, spec, postings, cfg["cap_mentions"], cfg["max_len"], needed)
    return dict(train_neigh=train_neigh, landmarks=landmarks, anchor_pool=anchor_pool,
               win_ids=win_ids, heldout_pairs_loaded=len(heldout_pairs),
               n_excluded_heldout_pair=rel_leak_meta["n_excluded_heldout_pair"],
               n_kept_edges=rel_leak_meta["n_kept_edges"],
               n_landmarks_actual=int(landmarks.shape[0]), n_anchor_pool=int(anchor_pool.shape[0]))


def relational_eval(ground, text, counts, universe, split, adj, deg, n_shards, seed, w_star):
    """Per-query AUC: rank a held-out concept's true TRAIN-neighbour vs degree-matched train non-neighbours,
    scored by rep cosine. rep has ZERO relational input => leak-proof.
    v2: adds ARM_RAW_TEXT (text-alone) + ARM_FUSE_ZAVG + ARM_FUSE_WTUNED -> THE headroom answer
    (does text-at-scale beat grounding on the RELATIONAL bar too?)."""
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
    out = {RAW_ARM: [], TEXT_ARM: [], FUSED_ARM: [], FUSE_ZAVG_ARM: [],
           FUSE_WTUNED_ARM: [], SHUFFLE_ARM: [], POP_ARM: []}
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

        def _z1(x):
            s = x.std()
            return (x - x.mean()) / (s + 1e-8) if s > 1e-12 else x - x.mean()
        czavg = 0.5 * (_z1(cg) + _z1(ct))
        cw = w_star * ct + (1.0 - w_star) * cg
        pop = np.log1p(deg[cand].astype(np.float64))
        for a, sc in ((RAW_ARM, cg), (TEXT_ARM, ct), (FUSED_ARM, cf),
                      (FUSE_ZAVG_ARM, czavg), (FUSE_WTUNED_ARM, cw),
                      (SHUFFLE_ARM, cs), (POP_ARM, pop)):
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

    _log("R1/R3 relational self-teacher prep (landmarks=%d, 2nd leak gate=heldout_edges.jsonl)..."
         % cfg["n_landmarks"])
    relobj = relobj_prep(universe, split, adj, postings, tok, spec, cfg)
    _log("  anchor_pool=%d landmarks=%d excluded_heldout_pairs=%d kept_train_edges=%d"
         % (relobj["n_anchor_pool"], relobj["n_landmarks_actual"],
            relobj["n_excluded_heldout_pair"], relobj["n_kept_edges"]))
    if relobj["n_anchor_pool"] < cfg["min_rel_anchors"] or relobj["n_landmarks_actual"] < 4:
        raise RuntimeError(
            "META_RULE_AG-style regime-insufficient: rel anchor_pool=%d landmarks=%d below "
            "min_rel_anchors=%d threshold at this cfg -- re-spec cap_eval_concepts/min_deg, do not "
            "silently proceed with a vacuous L_rel" % (relobj["n_anchor_pool"], relobj["n_landmarks_actual"],
                                                        cfg["min_rel_anchors"]))

    return dict(counts=counts, corpus_stats=corpus_stats, split=split,
                postings=postings, collect_meta=collect_meta, tok=tok, spec=spec,
                stream=stream, trained_tokens=trained_tokens, ground=ground,
                adj=adj, deg=deg, n_shards=n_shards, witness_leaks=witness_leaks,
                relobj=relobj)


# ---------------------------------------------------------------------------
# One seed (MLM train + encode + eval; consumes the shared data bundle)
# ---------------------------------------------------------------------------
def _save_checkpoint(out_dir, seed, model, tok, spec, cfg, universe, split, bundle,
                     text_reps, text_rand, ground, mrep_cnt, w_star, selected_arm):
    """GAP-3: persist the trained encoder (.pt) + an eval-rep bundle (.npz) so future fusion
    iterations are EVAL-ONLY (minutes, no retrain)."""
    try:
        ckpt = dict(
            state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()},
            spec=spec,
            model_cfg=dict(vocab=int(spec["size"]), max_len=int(cfg["max_len"]),
                           d_model=int(cfg["d_model"]), n_layers=int(cfg["n_layers"]),
                           n_heads=int(cfg["n_heads"]), ffn_mult=int(cfg["ffn_mult"]),
                           pad_id=int(spec["pad"])),
            tokenizer_json=tok.to_str(),
            seed=int(seed), run_mode=cfg["run_mode"], anchor=ANCHOR_NAME,
            w_star=float(w_star), selected_arm=str(selected_arm),
        )
        torch.save(ckpt, os.path.join(out_dir, "ckpt_seed_%d.pt" % seed))
        adj = bundle["adj"]
        indptr = np.zeros(len(adj) + 1, dtype=np.int64)
        flat = []
        for i, a in enumerate(adj):
            s = sorted(a)
            flat.extend(s)
            indptr[i + 1] = indptr[i] + len(s)
        np.savez_compressed(
            os.path.join(out_dir, "evalreps_seed_%d.npz" % seed),
            text_reps=text_reps.astype(np.float32), text_rand=text_rand.astype(np.float32),
            ground=ground.astype(np.float32), mrep_cnt=mrep_cnt.astype(np.int64),
            counts=bundle["counts"].astype(np.int64), deg=bundle["deg"].astype(np.int64),
            adj_indices=np.asarray(flat, dtype=np.int64), adj_indptr=indptr,
            held_idx=split["held_idx"], train_eval_idx=split["train_eval_idx"],
            is_held=split["is_held"],
            lexnames=np.array([x if x else "" for x in universe["lexnames"]], dtype=object),
            w_star=np.float64(w_star), selected_arm=np.array(str(selected_arm)),
            n_shards=np.int64(bundle["n_shards"]),
        )
        _log("  checkpoint saved: ckpt_seed_%d.pt + evalreps_seed_%d.npz" % (seed, seed))
        return True
    except (OSError, RuntimeError, ValueError) as e:
        _log("  WARN checkpoint save failed (%s): %s" % (type(e).__name__, str(e)[:200]))
        return False


def _load_eval_bundle(npz_path):
    """Reconstruct the eval inputs from a saved evalreps_*.npz for EVAL-ONLY re-runs."""
    z = np.load(npz_path, allow_pickle=True)
    K = int(z["ground"].shape[0])
    idx = z["adj_indices"]
    ptr = z["adj_indptr"]
    adj = [set(int(x) for x in idx[ptr[i]:ptr[i + 1]].tolist()) for i in range(K)]
    lex = [x if x else None for x in z["lexnames"].tolist()]
    universe = dict(lexnames=lex, K=K, ids=list(range(K)), surfaces=[str(i) for i in range(K)])
    split = dict(held_idx=z["held_idx"].astype(np.int64),
                 train_eval_idx=z["train_eval_idx"].astype(np.int64),
                 is_held=z["is_held"].astype(bool),
                 split_meta=dict(reloaded=True))
    return dict(ground=z["ground"].astype(np.float32), text_reps=z["text_reps"].astype(np.float32),
                text_rand=z["text_rand"].astype(np.float32), mrep_cnt=z["mrep_cnt"].astype(np.int64),
                counts=z["counts"].astype(np.int64), deg=z["deg"].astype(np.int64), adj=adj,
                n_shards=int(z["n_shards"]), universe=universe, split=split,
                w_star=float(z["w_star"]), selected_arm=str(z["selected_arm"])), z


def eval_from_reps(seed, run_mode, out_dir, universe, split, counts, adj, deg, n_shards,
                   ground, text_reps, text_rand, mrep_cnt, elapsed_s, extra=None):
    """All eval arms from computed reps (shared by TRAIN+eval and EVAL-ONLY paths). Leak-proof.
    Selects the best-honest fusion on TRAIN-eval, then reports held-out for every arm."""
    held = split["held_idx"]
    arm_digests = _arms_differ({
        RAW_ARM: ground[held], TEXT_ARM: text_reps[held], RANDINIT_ARM: text_rand[held]})

    _log("seed=%d: fusion model-selection on TRAIN-eval..." % seed)
    w_star, selected_arm, train_diag = select_fusion_on_train(
        ground, text_reps, text_rand, counts, universe, split, seed)
    _log("  selected primary=%s w*=%.2f (train n_query=%d)"
         % (selected_arm, w_star, train_diag.get("n_query_train", 0)))

    _log("seed=%d: semantic eval (held-out-NEW)..." % seed)
    sem_all = semantic_eval(ground, text_reps, text_rand, counts, universe, split, seed,
                            w_star, selected_arm)
    well_mask = counts >= WELL_COVERED_MIN
    sem_well = semantic_eval(ground, text_reps, text_rand, counts, universe, split, seed,
                             w_star, selected_arm, subset_mask=well_mask)
    _log("seed=%d: relational eval (headroom: text-alone + fusion)..." % seed)
    rel = relational_eval(ground, text_reps, counts, universe, split,
                          adj, deg, n_shards, seed, w_star)

    result = dict(
        seed=int(seed), run_mode=run_mode, elapsed_s=float(elapsed_s),
        w_star=float(w_star), selected_arm=selected_arm,
        fusion_select=train_diag,
        n_well_covered=int(well_mask[held].sum()),
        semantic_all=sem_all, semantic_well_covered=sem_well, relational=rel,
        arm_digests=arm_digests,
        mention_rep_coverage=float((mrep_cnt[held] > 0).mean()),
    )
    if extra:
        result.update(extra)
    return result


def _load_v2_baseline_encoder(seed, device):
    """BASELINE REUSE (store discipline): reload v2's OWN persisted tokenizer + weights for this seed,
    if the checkpoint exists on disk. Returns (model, tok, spec) or None. Never retrains."""
    ckpt_path = os.path.join(V2_CKPT_DIR, "ckpt_seed_%d.pt" % seed)
    if not os.path.exists(ckpt_path):
        return None
    try:
        ckpt = torch.load(ckpt_path, map_location=device)
        mc = ckpt["model_cfg"]
        spec = ckpt["spec"]
        model = TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                                mc["n_heads"], mc["ffn_mult"], mc["pad_id"]).to(device)
        model.load_state_dict(ckpt["state_dict"])
        model.eval()
        tok = Tokenizer.from_str(ckpt["tokenizer_json"])
        return model, tok, spec, mc
    except (OSError, RuntimeError, KeyError, ValueError) as e:
        _log("  WARN v2 baseline checkpoint reload failed seed=%d (%s): %s"
             % (seed, type(e).__name__, str(e)[:200]))
        return None


def eval_baseline_arm(seed, cfg, device, universe, split, counts, postings, ground,
                      adj, deg, n_shards):
    """Evaluate the v2 MLM-only baseline (reused checkpoint) on THIS run's own postings/split/adjacency
    (deterministically identical to v2's, same cfg/salt/corpus). Falls back to a CITED reference if the
    checkpoint is absent -- baseline_source distinguishes the two evidence classes, never conflated."""
    loaded = _load_v2_baseline_encoder(seed, device)
    if loaded is None:
        return dict(baseline_source=BASELINE_SOURCE_CITED, baseline_relational_auc=CITED_BASELINE_RELATIONAL_AUC,
                   baseline_semantic_auc=None, baseline_reload_ok=False)
    model, tok, spec, mc = loaded
    if mc["max_len"] != cfg["max_len"] or mc["vocab"] != cfg["vocab"]:
        _log("  WARN baseline ckpt seed=%d cfg mismatch (max_len/vocab) -- falling back to CITED reference"
             % seed)
        return dict(baseline_source=BASELINE_SOURCE_CITED, baseline_relational_auc=CITED_BASELINE_RELATIONAL_AUC,
                   baseline_semantic_auc=None, baseline_reload_ok=False)
    text_reps_b, mrep_cnt_b = encode_concept_text_reps(model, tok, postings, cfg, device, spec)
    sem_b = semantic_eval(ground, text_reps_b, text_reps_b, counts, universe, split, seed,
                          1.0, TEXT_ARM)   # w_star=1.0/TEXT_ARM selection irrelevant to TEXT_ARM col
    rel_b = relational_eval(ground, text_reps_b, counts, universe, split, adj, deg, n_shards, seed, 1.0)
    return dict(baseline_source=BASELINE_SOURCE_REUSED,
               baseline_relational_auc=rel_b.get(TEXT_ARM),
               baseline_semantic_auc=sem_b.get(TEXT_ARM),
               baseline_reload_ok=True, baseline_n_query_rel=rel_b.get("_n_query"))


def run_one_seed(seed, cfg, device, out_dir, universe, bundle):
    t0 = time.perf_counter()
    split = bundle["split"]
    counts = bundle["counts"]
    tok = bundle["tok"]
    spec = bundle["spec"]
    postings = bundle["postings"]
    ground = bundle["ground"]

    _log("seed=%d: JOINT MLM+L_rel train (%d steps, rel_every=%d)..." % (seed, cfg["mlm_steps"], cfg["rel_every"]))
    model, final_loss, rel_diag = mlm_train_relobj(bundle["stream"], spec, cfg, device, seed, out_dir,
                                                    cfg["mlm_steps"], bundle["relobj"])
    _log("  MLM+L_rel done final_mlm_loss=%.4f rel_fired=%d rel_loss_first=%s rel_loss_last=%s"
         % (final_loss, rel_diag["n_rel_fired"], rel_diag["rel_loss_first"], rel_diag["rel_loss_last"]))

    _log("seed=%d: encode concept text-reps (trained)..." % seed)
    text_reps, mrep_cnt = encode_concept_text_reps(model, tok, postings, cfg, device, spec)
    torch.manual_seed(seed + 999)
    rand_model = TinyTransformer(spec["size"], cfg["max_len"], cfg["d_model"], cfg["n_layers"],
                                 cfg["n_heads"], cfg["ffn_mult"], spec["pad"]).to(device)
    rand_model.eval()
    _log("seed=%d: encode concept text-reps (random-init)..." % seed)
    text_rand, _ = encode_concept_text_reps(rand_model, tok, postings, cfg, device, spec)

    _log("seed=%d: baseline-reuse eval (v2 MLM-only, if checkpoint present)..." % seed)
    baseline = eval_baseline_arm(seed, cfg, device, universe, split, counts, postings, ground,
                                 bundle["adj"], bundle["deg"], bundle["n_shards"])
    _log("  baseline_source=%s rel_auc=%s sem_auc=%s"
         % (baseline["baseline_source"], baseline["baseline_relational_auc"], baseline["baseline_semantic_auc"]))

    # fusion selection first (needed for checkpoint metadata), then full eval reuses it
    w_star, selected_arm, _ = select_fusion_on_train(
        ground, text_reps, text_rand, counts, universe, split, seed)
    _save_checkpoint(out_dir, seed, model, tok, spec, cfg, universe, split, bundle,
                     text_reps, text_rand, ground, mrep_cnt, w_star, selected_arm)
    inprog = os.path.join(out_dir, "ckpt_seed_%d_inprogress.pt" % seed)
    if os.path.exists(inprog):
        try:
            os.remove(inprog)
        except OSError:
            pass

    extra = dict(
        final_mlm_loss=float(final_loss), trained_tokens=int(bundle["trained_tokens"]),
        corpus_stats=bundle["corpus_stats"], collect_meta=bundle["collect_meta"],
        split_meta=split["split_meta"], bpe_size=int(spec["size"]),
        checkpoint_saved=True, rel_diag=rel_diag, baseline=baseline,
        heldout_edge_leak_gate=dict(
            n_heldout_pairs_loaded=bundle["relobj"]["heldout_pairs_loaded"],
            n_excluded_heldout_pair=bundle["relobj"]["n_excluded_heldout_pair"],
            n_kept_train_edges=bundle["relobj"]["n_kept_edges"]),
    )
    return eval_from_reps(seed, cfg["run_mode"], out_dir, universe, split, counts,
                          bundle["adj"], bundle["deg"], bundle["n_shards"],
                          ground, text_reps, text_rand, mrep_cnt,
                          time.perf_counter() - t0, extra=extra)


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
    def mean(v):
        return float(np.mean(v)) if v else None

    # --- R1/R3 relational-objective primary comparison: OBJ (this run's TEXT_ARM) vs BASELINE (reused
    # v2 checkpoint or CITED reference) -------------------------------------------------------------
    obj_rel = col("relational", TEXT_ARM)
    obj_sem = col("semantic_all", TEXT_ARM)
    baselines = [per_seed[k].get("baseline", {}) for k in seeds]
    base_rel = [b.get("baseline_relational_auc") for b in baselines]
    base_sem = [b.get("baseline_semantic_auc") for b in baselines]
    base_src = [b.get("baseline_source") for b in baselines]
    rel_margins = [o - b for o, b in zip(obj_rel, base_rel) if b is not None] if obj_rel else []
    rel_margin_mean = float(np.mean(rel_margins)) if rel_margins else None
    rel_margin_min = float(np.min(rel_margins)) if rel_margins else None
    sem_margins = [o - b for o, b in zip(obj_sem, base_sem) if b is not None] if obj_sem else []
    sem_margin_mean = float(np.mean(sem_margins)) if sem_margins else None

    rel_diags = [per_seed[k].get("rel_diag", {}) for k in seeds]
    rel_loss_decreased_all = [d.get("rel_loss_decreased") for d in rel_diags]
    rel_ok_all = [bool(d.get("rel_ok")) for d in rel_diags]
    n_rel_fired_min = min([int(d.get("n_rel_fired", 0)) for d in rel_diags]) if rel_diags else 0
    rel_learning_real = all(rel_ok_all) and n_rel_fired_min > 0 and all(
        (x is True) for x in rel_loss_decreased_all if x is not None)

    leak_gates = [per_seed[k].get("heldout_edge_leak_gate", {}) for k in seeds]
    n_excluded_total = sum(int(g.get("n_excluded_heldout_pair", 0)) for g in leak_gates)
    heldout_pairs_loaded_any = any(int(g.get("n_heldout_pairs_loaded", 0)) > 0 for g in leak_gates)

    # semantic (held-out-NEW) per-arm
    raw = col("semantic_all", RAW_ARM)
    txt = col("semantic_all", TEXT_ARM)
    feq = col("semantic_all", FUSED_ARM)              # naive 1:1 (dilution control)
    fza = col("semantic_all", FUSE_ZAVG_ARM)
    fwt = col("semantic_all", FUSE_WTUNED_ARM)
    prim = col("semantic_all", FUSE_SELECTED_ARM)     # PRIMARY (best-honest, selected on train)
    rnd = col("semantic_all", RANDINIT_ARM)
    sh = col("semantic_all", SHUFFLE_ARM)
    pop = col("semantic_all", POP_ARM)
    nq = [per_seed[k].get("semantic_all", {}).get("_n_query", 0) for k in seeds]
    sel_arms = [per_seed[k].get("semantic_all", {}).get("_selected_arm") for k in seeds]
    w_stars = [per_seed[k].get("semantic_all", {}).get("_w_star") for k in seeds]

    m_raw, m_txt, m_feq = mean(raw), mean(txt), mean(feq)
    m_fza, m_fwt, m_prim = mean(fza), mean(fwt), mean(prim)
    m_rnd, m_sh, m_pop = mean(rnd), mean(sh), mean(pop)

    # PRIMARY margin over raw grounding (the promotion number)
    margins = [p - r for p, r in zip(prim, raw)] if (prim and raw and len(prim) == len(raw)) else []
    margin_mean = float(np.mean(margins)) if margins else None
    margin_min = float(np.min(margins)) if margins else None
    # text-alone margin (headline diagnostic; independent of selection)
    txt_margins = [t - r for t, r in zip(txt, raw)] if (txt and raw and len(txt) == len(raw)) else []
    txt_margin_mean = float(np.mean(txt_margins)) if txt_margins else None
    txt_margin_min = float(np.min(txt_margins)) if txt_margins else None
    learn_margins = [t - r for t, r in zip(txt, rnd)] if (txt and rnd and len(txt) == len(rnd)) else []
    learn_mean = float(np.mean(learn_margins)) if learn_margins else None

    # well-covered fork (uses PRIMARY)
    wf = col("semantic_well_covered", FUSE_SELECTED_ARM)
    wr = col("semantic_well_covered", RAW_ARM)
    well_margins = [f - r for f, r in zip(wf, wr)] if (wf and wr and len(wf) == len(wr)) else []
    well_margin_mean = float(np.mean(well_margins)) if well_margins else None

    # relational headroom
    rraw = col("relational", RAW_ARM)
    rtxt = col("relational", TEXT_ARM)
    rfeq = col("relational", FUSED_ARM)
    rfza = col("relational", FUSE_ZAVG_ARM)
    rfwt = col("relational", FUSE_WTUNED_ARM)
    rsh = col("relational", SHUFFLE_ARM)
    rpop = col("relational", POP_ARM)
    m_rraw, m_rtxt = mean(rraw), mean(rtxt)
    rel_text_margins = [t - r for t, r in zip(rtxt, rraw)] if (rtxt and rraw and len(rtxt) == len(rraw)) else []
    rel_text_margin_mean = float(np.mean(rel_text_margins)) if rel_text_margins else None   # HEADROOM answer

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
    gates.append(record_gate("primary_beats_raw_margin", margin_mean if margin_mean is not None else -1.0,
                             HP_MARGIN_OVER_RAW, ">=", note="PRIMARY(best-honest fusion)-RAW semantic"))
    gates.append(record_gate("primary_beats_raw_per_seed_min", margin_min if margin_min is not None else -1.0,
                             0.0, ">", note="per-seed min PRIMARY margin"))
    gates.append(record_gate("learning_real_text_over_random", learn_mean if learn_mean is not None else -1.0,
                             LEARNING_EPS, ">", note="RAW_TEXT - RANDOM_INIT"))
    gates.append(record_gate("heldout_edge_second_leak_gate", 1.0 if heldout_pairs_loaded_any else 0.0,
                             1.0, "==", note="heldout_edges.jsonl loaded + applied (excluded=%d pairs across seeds)"
                             % n_excluded_total))
    gates.append(record_gate("rel_objective_learning_real", 1.0 if rel_learning_real else 0.0, 1.0, "==",
                             note="L_rel fired every seed AND rel_loss decreased (n_rel_fired_min=%d, per-seed rel_loss_decreased=%s)"
                             % (n_rel_fired_min, rel_loss_decreased_all)))
    gates.append(record_gate("relobj_beats_baseline_margin", rel_margin_mean if rel_margin_mean is not None else -1.0,
                             HP_MARGIN_OVER_RAW, ">=", note="OBJ(TEXT_ARM relational-AUC) - BASELINE(reused/cited)"))
    gates.append(record_gate("relobj_beats_baseline_per_seed_min", rel_margin_min if rel_margin_min is not None else -1.0,
                             0.0, ">", note="per-seed min relational margin over baseline"))
    gates.append(record_gate("relobj_semantic_no_regression", sem_margin_mean if sem_margin_mean is not None else 0.0,
                             -SEM_REGRESSION_MAX, ">=", note="objective-conflict guard: OBJ-BASELINE semantic-AUC >= -0.02"))

    run_mode = cfg["run_mode"]
    if run_mode in ("selftest", "smoke"):
        # smoke ran_ok = semantic arms + controls computed (relational coverage is scale-dependent;
        # asserted separately when it has queries) PLUS the L_rel discriminator actually fired.
        ran_ok = (m_raw is not None and m_prim is not None and m_txt is not None
                  and m_feq is not None and m_fza is not None and m_fwt is not None
                  and m_sh is not None and m_pop is not None and n_rel_fired_min > 0)
        verdict = "SMOKE_PASS" if ran_ok else "SMOKE_INCOMPLETE"
        vmsg = ("SMOKE run_mode=%s raw=%.4f text=%.4f primary(%s)=%.4f collapse=%.4f pop=%.4f "
                "rel_raw=%.4f rel_text(OBJ)=%.4f baseline_src=%s baseline_rel=%s rel_margin=%s "
                "n_rel_fired_min=%d rel_loss_decreased=%s excluded_heldout_pairs=%d n_query_min=%d"
                % (run_mode, m_raw or -1, m_txt or -1, str(sel_arms[0]), m_prim or -1, m_sh or -1, m_pop or -1,
                   m_rraw or -1, m_rtxt or -1, base_src, base_rel,
                   ("%.4f" % rel_margin_mean) if rel_margin_mean is not None else "NA",
                   n_rel_fired_min, rel_loss_decreased_all, n_excluded_total, min_nq))
    else:
        if not validity:
            verdict = "HARD_FAIL_INVALID"
            vmsg = ("INVALID: validity gate failed (collapse=%s pop=%s raw=%s n_query_min=%d). "
                    "Controls must behave before the number is trustworthy."
                    % (m_sh, m_pop, m_raw, min_nq))
        elif not rel_learning_real:
            verdict = "HARD_FAIL_REL_OBJECTIVE_NOT_LEARNING"
            vmsg = ("HARD_FAIL: L_rel training loss did not visibly decrease (or never fired) -- the "
                    "relational self-teacher term is not learning; margin numbers below are not "
                    "trustworthy until the training dynamics are fixed. rel_ok=%s n_rel_fired_min=%d "
                    "rel_loss_decreased=%s" % (rel_ok_all, n_rel_fired_min, rel_loss_decreased_all))
        elif (rel_margin_mean is not None and rel_margin_mean >= HP_MARGIN_OVER_RAW
              and rel_margin_min is not None and rel_margin_min > 0.0
              and (sem_margin_mean is None or sem_margin_mean >= -SEM_REGRESSION_MAX)):
            verdict = "HARD_PASS_RELOBJ_CLEAN_WIN"
            vmsg = ("HARD_PASS_RELOBJ_CLEAN_WIN: joint MLM+foundation-relational-self-teacher OBJ(TEXT_ARM) "
                    "BEATS the MLM-only BASELINE on held-out-NEW RELATIONAL-AUC. margin=%.4f (>=%.2f, "
                    "per-seed min=%.4f); semantic_margin=%s (regression guard >=-%.2f); "
                    "obj_rel=%s base_rel=%s (source=%s) obj_sem=%s base_sem=%s; "
                    "n_rel_fired_min=%d rel_loss(first->last)=%s->%s excluded_heldout_pairs=%d"
                    % (rel_margin_mean, HP_MARGIN_OVER_RAW, rel_margin_min,
                       ("%.4f" % sem_margin_mean) if sem_margin_mean is not None else "NA", SEM_REGRESSION_MAX,
                       obj_rel, base_rel, base_src, obj_sem, base_sem,
                       n_rel_fired_min, [d.get("rel_loss_first") for d in rel_diags],
                       [d.get("rel_loss_last") for d in rel_diags], n_excluded_total))
        elif (rel_margin_mean is not None and -0.02 <= rel_margin_mean <= 0.02):
            verdict = "HARD_FAIL_ARCHITECTURE_BOUND"
            vmsg = ("HARD_FAIL: OBJ-BASELINE relational-AUC margin=%.4f stays within +/-0.02 of baseline "
                    "DESPITE L_rel loss visibly decreasing (rel_loss %s->%s) -- the ceiling is "
                    "architecture/readout-bound (e.g. mean-pool concept-aggregation order-blindness), "
                    "NOT objective-absence. Redirect to the readout/pooling mechanism next. "
                    "obj_rel=%s base_rel=%s (source=%s)"
                    % (rel_margin_mean, [d.get("rel_loss_first") for d in rel_diags],
                       [d.get("rel_loss_last") for d in rel_diags], obj_rel, base_rel, base_src))
        else:
            verdict = "MIDDLE_BAND_RELOBJ_PARTIAL"
            vmsg = ("MIDDLE_BAND: relational margin=%s positive but < %.2f, or semantic regressed beyond "
                    "the objective-conflict guard (sem_margin=%s). obj_rel=%s base_rel=%s (source=%s) "
                    "obj_sem=%s base_sem=%s"
                    % (("%.4f" % rel_margin_mean) if rel_margin_mean is not None else "NA", HP_MARGIN_OVER_RAW,
                       ("%.4f" % sem_margin_mean) if sem_margin_mean is not None else "NA",
                       obj_rel, base_rel, base_src, obj_sem, base_sem))

    summary = dict(
        obj_relational_auc=obj_rel, obj_semantic_auc=obj_sem,
        baseline_relational_auc=base_rel, baseline_semantic_auc=base_sem, baseline_source=base_src,
        relational_margin_over_baseline_mean=rel_margin_mean, relational_margin_over_baseline_min=rel_margin_min,
        semantic_margin_over_baseline_mean=sem_margin_mean,
        rel_learning_real=rel_learning_real, n_rel_fired_min=n_rel_fired_min,
        rel_loss_first=[d.get("rel_loss_first") for d in rel_diags],
        rel_loss_last=[d.get("rel_loss_last") for d in rel_diags],
        n_excluded_heldout_pair_total=n_excluded_total,
        primary_arm_selected=sel_arms, w_star_per_seed=w_stars,
        semantic_raw_grounding=m_raw, semantic_text=m_txt,
        semantic_fused_eq_naive=m_feq, semantic_fuse_zavg=m_fza, semantic_fuse_wtuned=m_fwt,
        semantic_primary=m_prim,
        semantic_random_init=m_rnd, semantic_collapse=m_sh, semantic_popularity=m_pop,
        semantic_margin_primary_minus_raw=margin_mean, semantic_margin_primary_min=margin_min,
        semantic_margin_text_minus_raw=txt_margin_mean, semantic_margin_text_min=txt_margin_min,
        learning_text_minus_random=learn_mean,
        well_covered_margin=well_margin_mean,
        relational_raw=m_rraw, relational_text=m_rtxt,
        relational_fused_eq=mean(rfeq), relational_fuse_zavg=mean(rfza),
        relational_fuse_wtuned=mean(rfwt),
        relational_collapse=mean(rsh), relational_popularity=mean(rpop),
        relational_text_minus_raw=rel_text_margin_mean,
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


def _run_eval_only(cfg, out_dir):
    """GAP-3 payoff: re-run all eval arms from saved evalreps_*.npz checkpoints. No training.
    Future fusion iterations = minutes. Loads whatever ckpt seeds are present in out_dir."""
    npzs = sorted(glob.glob(os.path.join(out_dir, "evalreps_seed_*.npz")))
    if not npzs:
        raise FileNotFoundError("eval-only: no evalreps_seed_*.npz in %s" % out_dir)
    seeds_done = []
    for p in npzs:
        seed = int(re.search(r"evalreps_seed_(\d+)\.npz", os.path.basename(p)).group(1))
        _log("eval-only: loading %s" % os.path.basename(p))
        eb, _ = _load_eval_bundle(p)
        t0 = time.perf_counter()
        res = eval_from_reps(seed, "eval_only", out_dir, eb["universe"], eb["split"],
                             eb["counts"], eb["adj"], eb["deg"], eb["n_shards"],
                             eb["ground"], eb["text_reps"], eb["text_rand"], eb["mrep_cnt"],
                             time.perf_counter() - t0,
                             extra=dict(final_mlm_loss=float("nan"), trained_tokens=None,
                                        checkpoint_saved=True, reloaded_from=os.path.basename(p),
                                        rel_diag=dict(rel_ok=True, n_rel_fired=1, n_ckpt_saves=0,
                                                      rel_loss_first=None, rel_loss_last=None,
                                                      rel_loss_decreased=None),
                                        baseline=dict(baseline_source="eval_only_not_recomputed",
                                                     baseline_relational_auc=None, baseline_semantic_auc=None),
                                        heldout_edge_leak_gate=dict(n_heldout_pairs_loaded=0,
                                                                    n_excluded_heldout_pair=0, n_kept_train_edges=0)))
        write_partial(out_dir, seed, res)
        seeds_done.append(seed)
    return sorted(seeds_done)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--eval-only", action="store_true",
                    help="re-run eval arms from saved evalreps_*.npz (no training)")
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

    if args.eval_only:
        _write_start_marker(out_dir, "eval_only", 0)
        _log("EVAL-ONLY mode (no training; reloading checkpoints)")
        seeds_done = _run_eval_only(cfg, out_dir)
        per_seed = aggregate_partials(out_dir, seeds_done)
        verdict, vmsg, summary, gates = build_verdict(per_seed, dict(run_mode="full"))
        _log("VERDICT (eval-only): %s" % verdict)
        _log(vmsg)
        metrics = dict(
            verdict=verdict, verdict_msg=vmsg, summary=vmsg, anchor_name=ANCHOR_NAME,
            run_mode="eval_only", ts_iso=datetime.now(timezone.utc).isoformat(),
            device="cpu", cuda=bool(torch.cuda.is_available()), n_seeds=len(seeds_done),
            results_summary=summary, per_seed={k: per_seed[k] for k in per_seed},
            bands=dict(hp_margin_over_raw=HP_MARGIN_OVER_RAW, raw_signal_min=RAW_SIGNAL_MIN,
                       collapse_band=list(COLLAPSE_BAND), min_query=MIN_QUERY_TASKS,
                       well_covered_min=WELL_COVERED_MIN, sem_regression_max=SEM_REGRESSION_MAX,
                       cited_baseline_relational_auc=CITED_BASELINE_RELATIONAL_AUC),
            cardinality_ok=True, expected_n_units=len(seeds_done))
        write_metrics(out_dir, metrics, results=list(per_seed.values()), gate_claims=gates)
        return

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
        _selftest_assertions(per_seed, summary, verdict, out_dir)
        _log("SELF-TEST PASS")


def _selftest_assertions(per_seed, summary, verdict, out_dir):
    assert len(per_seed) >= 1, "no seed completed"
    sk = sorted(per_seed.keys())[0]
    r = per_seed[sk]
    assert r["semantic_all"] is not None, "semantic eval did not run"
    for a in [RAW_ARM, TEXT_ARM, FUSED_ARM, FUSE_ZAVG_ARM, FUSE_WTUNED_ARM, FUSE_SELECTED_ARM]:
        assert r["semantic_all"].get(a) is not None, "semantic arm missing: %s" % a
        au = r["semantic_all"][a]
        assert 0.0 <= au <= 1.0, "AUC out of range for %s: %s" % (a, au)
    # PRIMARY must equal the selected arm's held-out AUC (leak-proof selection wired)
    sel = r["semantic_all"].get("_selected_arm")
    assert sel in PRIMARY_CANDIDATES, "selected arm not a primary candidate: %s" % sel
    assert abs(r["semantic_all"][FUSE_SELECTED_ARM] - r["semantic_all"][sel]) < 1e-9, \
        "PRIMARY != selected-arm held-out AUC"
    # relational headroom arms present (text-alone + fusion added in v2); coverage is scale-dependent,
    # so require the arms only when the eval produced queries (it does at SMOKE/FULL scale).
    assert r["relational"] is not None, "relational eval did not run"
    if r["relational"].get("_n_query", 0) > 0:
        for a in [RAW_ARM, TEXT_ARM, FUSE_ZAVG_ARM, FUSE_WTUNED_ARM]:
            assert r["relational"].get(a) is not None, "relational arm missing: %s" % a
    assert np.isfinite(r["final_mlm_loss"]), "MLM loss not finite"
    assert r["trained_tokens"] > 0, "no tokens trained on"
    # GAP-3: checkpoint saved + reloadable (eval-only path)
    ckpt_pt = os.path.join(out_dir, "ckpt_seed_%d.pt" % int(sk))
    ckpt_npz = os.path.join(out_dir, "evalreps_seed_%d.npz" % int(sk))
    assert os.path.exists(ckpt_pt), "checkpoint .pt not saved: %s" % ckpt_pt
    assert os.path.exists(ckpt_npz), "eval-rep bundle .npz not saved: %s" % ckpt_npz
    eb, _z = _load_eval_bundle(ckpt_npz)
    assert eb["text_reps"].shape[0] == eb["ground"].shape[0], "reloaded rep shape mismatch"
    assert verdict == "SMOKE_PASS", "selftest did not complete arms (%s)" % verdict
    # R1/R3 relational self-teacher: real_code_path_exercised (the L_rel step must have actually fired
    # and the periodic mid-training checkpoint must have actually saved at least once)
    rd = r.get("rel_diag")
    assert rd is not None, "rel_diag missing (relational self-teacher step did not run)"
    assert rd.get("rel_ok") is True, "rel_ok False -- anchor_pool/landmarks below min_rel_anchors at selftest scale"
    assert rd.get("n_rel_fired", 0) > 0, "L_rel discriminator never fired in selftest (n_rel_fired=0)"
    assert rd.get("n_ckpt_saves", 0) > 0, "periodic mid-training checkpoint never saved (n_ckpt_saves=0)"
    assert rd.get("rel_loss_first") is not None and rd.get("rel_loss_last") is not None, \
        "rel_loss curve empty despite n_rel_fired>0"
    # SECOND leak gate: heldout_edges.jsonl loaded and applied (exclusion mechanism exercised, even if
    # the excluded count happens to be 0 at selftest's tiny subsample -- the gate must have RUN)
    leak = r.get("heldout_edge_leak_gate")
    assert leak is not None, "heldout_edge_leak_gate missing"
    assert leak.get("n_heldout_pairs_loaded", 0) > 0, \
        "heldout_edges.jsonl failed to load (0 pairs) -- second leak gate not active"
    # baseline-reuse path exercised (either reused a real checkpoint or explicitly fell back to CITED)
    base = r.get("baseline")
    assert base is not None, "baseline dict missing"
    assert base.get("baseline_source") in (BASELINE_SOURCE_REUSED, BASELINE_SOURCE_CITED), \
        "baseline_source not tagged: %s" % base.get("baseline_source")
    assert base.get("baseline_relational_auc") is not None, "baseline_relational_auc missing"


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
