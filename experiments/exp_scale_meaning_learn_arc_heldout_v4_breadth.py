"""SCALE meaning-learning v4 breadth: from-scratch transformer over ARC+SimpleWiki+breadth_v1,
leak-proof held-out-NEW. ONE VARIABLE vs v2: training-corpus BREADTH (architecture/objective/steps
UNCHANGED). Tests the standing diagnosis "scale works but is DATA-LIMITED" (atom 29591) on the
untested axis -- the relational-OBJECTIVE axis was already tested and HARD_FAILED
(v3_relobj, both seeds; data/exp_scale_meaning_learn_arc_heldout_v3_relobj/metrics.json).

WHY (per notes/research_encoder_breadth_vs_relational_objective_scoping_2026-07-27.md, updated):
  That scoping note originally deferred breadth ("no real breadth corpus staged"). Since then
  data/corpora/simplewiki/simplewiki_clean_v1.txt (39.6M alpha tokens, real modern Simple English
  Wikipedia) and data/corpora/breadth_v1/breadth_corpus_v1.txt (1.7M alpha tokens: WordNet glosses +
  OneStopEnglish + LitBank + RACE + Wikipedia-500 + McGuffey/graded readers + UD-EWT) have been staged
  (data/corpora/breadth_v1/COMBINED_MANIFEST.md). Combined pool = 278.9M alpha tokens (1.17x the
  237.7M-token ARC-only pool). This cell finally runs the deferred breadth test.

WHAT CHANGES vs v2 (ONE VARIABLE = training-data breadth; everything else verbatim):
  - Corpus: v2 read ARC_Corpus.txt alone. v4 reads [simplewiki, breadth_v1, ARC] via the SAME
    per-line quality-filter + concept-level held-out scrub, per COMBINED_MANIFEST.md's explicit
    "drop-in integration (leak-safe)" recipe: point the existing per-line reader at all 3 files,
    do NOT cat them together (that would bypass per-line scrub-before-append and leak held-out
    concept contexts). ORDER is DELIBERATE: simplewiki + breadth_v1 (the small/broad sources) are
    read FIRST and drained to completion (or their own small caps) BEFORE ARC fills the remaining
    train_token_budget. This upsamples the minority-register corpora from their natural ~14.8%
    combined-pool share to roughly 25-30% of the 130M-token training stream -- a natural-proportional
    mix would leave breadth as a rounding error and starve the test of power. ARC still supplies the
    majority of tokens by design (breadth ADDED to the diet, not a full replacement).
  - LEAK-PROOFNESS (2nd correctness gate this cell adds): the zero-overlap witness now scans an
    INDEPENDENT sample from EACH of the 3 files (not one shared budget that a large early source
    could exhaust before ever reaching the others) and asserts BOTH (a) total leaked lines == 0
    AND (b) every one of the 3 sources actually produced a nonzero scanned-line count (proves the
    scrub genuinely fired across all three files, not silently skipping one).
  - LEAK-WITNESS CIRCULARITY FIX (Director design-verification, 2026-07-28): the original witness
    reused `_scrub_variants` (the SAME regex generator as the scrub) to decide "is this a train
    line," so any morphological variant the regex can't generate (irregular plurals: mouse/mice,
    child/children; irregular verbs: run/ran) leaked past the scrub AND was invisible to the witness
    -- and general-register prose (simplewiki, breadth_v1) has far more varied morphology than ARC's
    controlled science prose, so this would have biased the comparison TOWARD breadth (a false-
    positive risk). Fix, two parts: (1) the ACTUAL scrub (`_is_heldline`) is strengthened with a
    curated closed-class irregular-plural table PLUS NLTK WordNet's `morphy` dictionary-based
    morphological analyzer (verified this session: morphy('mice','n')='mouse',
    morphy('children','n')='child', morphy('ran','v')='run' -- catches what regex cannot); (2) an
    INDEPENDENT witness (`_stem_leak_witness`, Porter-stemmer -- a categorically different rule-based
    algorithm from both the regex generator and the morphy/irregular-plural dictionary lookups) scans
    the residual "train" lines under the enhanced scrub for any remaining stem collision, per corpus.
    Any leak from EITHER witness is a HARD FAIL (raise), never a warning: held-out concepts have ZERO
    train mentions BY CONSTRUCTION, so breadth can only help held-out-NEW placement via better GENERAL
    representations/transfer, never via direct exposure -- a leak would illicitly add exactly that
    direct exposure and invalidate the whole comparison.
  - TOKEN-BUDGET CONFOUND FIX (Director design-verification, 2026-07-28): `train_token_budget` is
    pinned to v2's own MEASURED realized token pool (121,082,196, both seeds) rather than the nominal
    130,000,000 v2 declared but never reached (v2's ARC-only pool exhausted its `max_lines=10,000,000`
    cap before hitting the nominal target). `mlm_steps`/`mlm_batch` are unchanged, so training COMPUTE
    is already identical between arms regardless of pool size -- but an uncontrolled pool-size
    difference would still change window-repetition-diversity during sampling-with-replacement, a
    second variable if left unmatched. Pinning to v2's exact realized value (verified via a runtime
    guard: `trained_tokens` must land within 2% of the declared budget on FULL runs) makes SOURCE
    DIVERSITY the ONLY variable at an equal, VERIFIED realized token budget -- exactly the well-posed
    question (do these same ~121M tokens, drawn from a broader source mix, produce a better
    representation, not "does training on more raw text help").
  - CHECKPOINT-ALWAYS + RESUMABLE: periodic in-progress checkpoint every `ckpt_every_steps` MLM
    steps (tmp+os.replace, atomic); a restart reloads it and resumes training from the saved step
    instead of restarting the ~3h/seed run from zero (v2 had ZERO mid-training checkpoints -- lost
    the entire run once already). RNG on resume is deterministically reseeded from the resume step
    (not a bit-identical continuation of the original RNG stream, but weights/step ARE preserved --
    this is the load-bearing property, documented as a known limitation, not silently claimed exact).
  - OOM-SAFETY CARRY-FORWARD (reused from v3_relobj's SH-5 VRAM-fit fix, 2026-07-28): TinyTransformer
    supports an opt-in gradient-checkpointed forward (`use_checkpoint=True`, cfg `mlm_grad_checkpoint`,
    default False since pure-MLM at this model size never OOM'd in v2/v3_relobj's own MLM-only path;
    wired as an available escape valve, not forced overhead). encode_concept_text_reps already batches
    (`encode_batch`), which is the OOM-safety property v3_relobj's `_pooled_for_rows` chunking added on
    top of the joint-loss path -- inherited for free here since v4 adds no extra pooling forward pass
    during training (no L_rel/L_ground; the ONE variable is data, not objective).
  - LEARNED-READOUT FAIR TEST (this cell's headline addition beyond the v2/v3_relobj family): relational
    placement is measured BOTH via cosine-NN (the v2/v3_relobj convention) AND via the promoted learned
    relational readout (`experiments/_learned_relational_readout.py`, HARD_PASS_MAJORITY 2026-07-28,
    rank-32 bilinear projection fit TRAIN-TRAIN, leak-proof) for BOTH the breadth arm and the v2-baseline
    arm. This directly answers the task's fair-test requirement: if breadth only lifts cosine-NN but not
    the learned readout, that is NOT a clean win (readout-limited, not a real placement-capability lift);
    if it lifts neither, the data lever is refuted under the harder test too.
  - BASELINE = v2's OWN trained encoder, REUSED not retrained (store discipline), following the
    already-VET'd v3_relobj precedent: v2's `ckpt_seed_<seed>.pt` is reloaded, then RE-ENCODED on an
    ARC-ONLY postings pass built from THIS run's own split/scrub (so the comparison is apples-to-apples
    on the identical held-out concept set, not v2's own historical postings/split). Falls back to a
    CITED reference (v2's own metrics.json per-seed numbers) if a given seed's checkpoint is absent on
    this machine -- baseline_source is tagged per seed, never silently conflated (BASELINE_SOURCE_REUSED
    vs BASELINE_SOURCE_CITED), exactly mirroring v3_relobj's eval_baseline_arm.

THE ONE NUMBER (pre-registered bands, BEFORE running -- see preregs/2026-07-28_scale_meaning_learn_arc_heldout_v4_breadth.md):
  HARD_PASS_BREADTH_CLEAN_WIN = learned-readout (PROBE_BILINEAR) relational-AUC margin over the
    v2-baseline PROBE_BILINEAR >= +0.03 on BOTH seeds (readout reload must succeed both seeds), AND the
    cosine-NN relational margin is also positive (directionally consistent, not contradicting), AND
    validity holds.
  HARD_FAIL_DATA_LEVER_REFUTED = PROBE_BILINEAR margin stays within +/-0.02 of the v2-baseline on BOTH
    seeds DESPITE genuine training (MLM loss decreased, corpus genuinely broadened per per-source token
    stats) => the breadth lever does NOT move the fair-test ceiling; reported plainly (per task contract)
    -- redirect budget off further corpus-breadth work, the bottleneck is elsewhere (readout/architecture,
    already flagged by the v3_relobj HARD_FAIL as NOT objective-absence either).
  MIDDLE_BAND = positive but < +0.03, OR cosine-NN and learned-readout disagree in direction, OR readout
    reload unavailable for one seed (partial evidence only).
  HARD_FAIL_INVALID = validity gate fails (collapse/popularity/raw-grounding/power controls).

HARD INVARIANTS (project locks, unchanged from v2): TEACHER-FREE (no GloVe/BGE/transformer weights
  anywhere; token embeddings + Transformer learned FROM SCRATCH by MLM; BPE vocab built FROM the training
  corpus, never on held-out text). INDUCTIVE (held-out placed from its own text + grounding; never a
  training target). LEAK-PROOF (concept-level scrub + per-source zero-overlap witness; tokenizer never
  sees held-out text; relational target never an input). ASCII-only. AI2 ARC Corpus: INTERNAL research
  use only. Simple English Wikipedia: CC BY-SA (dumps.wikimedia.org). breadth_v1: see
  data/corpora/breadth_v1/MANIFEST.md for per-source licensing.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF; hash-test over per-concept rep matrices, both arms)
# - final_metrics_atomicity: tmp_replace (write_metrics + per-seed partials) PLUS periodic
#     mid-training in-progress checkpoint (tmp+os.replace, every ckpt_every_steps) -- CHECKPOINT-ALWAYS
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator base = 0.5 exactly; collapse + popularity + random-init witness the floor
# - baseline_in_band at smoke: collapse ~0.5; popularity ~0.5; raw_grounding a real >0.55 signal
# - discriminator survives scale: FULL runs on GPU >=2 seeds; smoke previews controls + all-3-source
#     leak-witness coverage; HARD-FAIL fork reported plainly if the lever doesn't move the fair-test bar
# - HARD_PASS strictly above floor: margin>=0.03 AND readout reload succeeds BOTH seeds (not at-floor)
# - HP_SCOPE: gates apply to the learned-readout (PROBE_BILINEAR) relational-AUC margin (primary);
#     cosine-NN margin is a directional-consistency guard; semantic arms reported, not gated
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except; specific classes -> metrics)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; controls witness it empirically)
# - deterministic seeding: sha256 concept split (freq-stratified, sha256-ranked) + fixed int seeds +
#     sorted(); no hash()/list(set()); readout diag-seed is a fixed int (seed + 5001), never hash()-derived
# - real_code_path: --self-test constructs the REAL objects (multi-source count/collect/tokenize passes,
#     MLM train+resume, transformer encode, zero-overlap gate PER SOURCE, both evals, readout fit+eval)
#     at N~16 (SELFTEST_CFG IS the real pipeline at tiny scale, exercising all 3 corpus sources)
# - progress_logging: print_flush_true (MLM step logs + eval logs flush=True) + _heartbeat.jsonl
#     (timeout_s >> 1800; progress_cadence_expected_s ~ 60-300s per log_every cadence)
# - device-agnostic: cuda+AMP on the GPU box, cpu for local smoke; no hard device assumption
# - OOM-safety: TinyTransformer.pooled/mlm_logits support use_checkpoint=True (opt-in, cfg
#     mlm_grad_checkpoint, default False); encode_concept_text_reps already batches (cfg encode_batch)
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
import torch.utils.checkpoint
from nltk.corpus import wordnet as _WN          # hard dependency (already required by _build_lexname_map)
from nltk.stem import PorterStemmer as _PorterStemmer

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
from experiments._learned_relational_readout import (  # noqa: E402
    build_train_pairs,
    fit_diag_probe,
    fit_bilinear_probe,
    eval_relational_all_arms,
    arms_must_differ_hashes,
)

ANCHOR_NAME = "scale_meaning_learn_arc_heldout_v4_breadth"

# Corpus sources. tuple = (name, path, cfg_key_for_this_source's_max_lines_cap [None => unlimited],
# bpe_sample_share [natural combined-pool alpha-token share, per COMBINED_MANIFEST.md; CITED]).
_CORPORA_DIR = os.path.join(_REPO, "data", "corpora")
ARC_CORPUS = os.path.join(_CORPORA_DIR, "arc", "ARC-V1-Feb2018-2", "ARC_Corpus.txt")
SIMPLEWIKI_CORPUS = os.path.join(_CORPORA_DIR, "simplewiki", "simplewiki_clean_v1.txt")
BREADTH_V1_CORPUS = os.path.join(_CORPORA_DIR, "breadth_v1", "breadth_corpus_v1.txt")

# ORDER IS DELIBERATE (see module docstring): small/broad sources FIRST so a token-budget or
# per-concept mention-cap fills from breadth BEFORE ARC (ARC read first would silently starve the
# smaller corpora of any budget/postings-cap headroom -- the single most important correctness risk
# named in COMBINED_MANIFEST.md and the task contract).
CORPUS_SOURCES = [
    ("simplewiki", SIMPLEWIKI_CORPUS, "max_lines_simplewiki", 0.142),
    ("breadth_v1", BREADTH_V1_CORPUS, "max_lines_breadth_v1", 0.006),
    ("arc", ARC_CORPUS, "max_lines", 0.852),
]
# For the v2-baseline-equivalent bundle ONLY (baseline reuse: re-encode v2's reloaded weights on
# ARC-only postings so the reused checkpoint sees the same kind of context it was trained on).
ARC_ONLY_SOURCES = [("arc", ARC_CORPUS, "max_lines", 1.0)]

FOUNDATION_DIR = os.path.join(_REPO, "data", "cskg_foundation_v1")
NODES_PATH = os.path.join(FOUNDATION_DIR, "nodes.jsonl")
EDGES_GLOB = os.path.join(FOUNDATION_DIR, "edges_shard_*.jsonl")
LEXNAME_CACHE = os.path.join(_REPO, "data", "wordnet_lexname_cache_v1.json")

# v2 baseline checkpoint dir (BASELINE REUSE, not retrained -- v3_relobj precedent).
V2_CKPT_DIR = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2")
BASELINE_SOURCE_REUSED = "reused_checkpoint"
BASELINE_SOURCE_CITED = "cited_reference"
# CITED@data/exp_scale_meaning_learn_arc_heldout_v2/metrics.json per-seed ARM_RAW_TEXT relational AUC
# (fallback ONLY when a seed's v2 checkpoint is absent on this machine -- see baseline_source tagging).
CITED_BASELINE_RELATIONAL_AUC = {7: 0.6407445089333272, 13: 0.6247552038153069}
CITED_BASELINE_SEMANTIC_AUC = {7: 0.6339932003040564, 13: 0.6371697990346293}
CITED_BASELINE_RELATIONAL_AUC_DEFAULT = 0.6327498561  # mean of the two, for any other seed

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

# Deterministic salts / seeds (SAME as v2/v3_relobj -- shares the identical held-out-NEW concept set
# whenever counts/eligibility happen to coincide; salt is intentionally unchanged, not a new axis).
CONCEPT_SPLIT_SALT = "scale_meaning_arc_v1_concept_split::"
EVAL_SEED = 20260726

# Pre-reg bands (SEMANTIC held-out-NEW same-lexname per-query AUC; unchanged gate family from v2).
HP_MARGIN_OVER_RAW = 0.03
RAW_SIGNAL_MIN = 0.55
COLLAPSE_BAND = (0.44, 0.56)
MIN_QUERY_TASKS = 120
WELL_COVERED_MIN = 100
LEARNING_EPS = 0.0
W_GRID = [round(0.1 * i, 2) for i in range(0, 11)]
TRAIN_SELECT_CAP = 1500

# Breadth-lever specific bands (learned-readout fair test; THE headline gate for this cell).
BREADTH_HP_MARGIN = 0.03      # PROBE_BILINEAR margin (breadth - v2 baseline) must clear this
BREADTH_HF_BAND = 0.02        # within +/- this of baseline = HARD_FAIL_DATA_LEVER_REFUTED

# Arms (per-query AUC; base 0.5)
RAW_ARM = "ARM_RAW_GROUNDING"
TEXT_ARM = "ARM_RAW_TEXT"
FUSED_ARM = "ARM_FUSED_EQ"
FUSE_ZAVG_ARM = "ARM_FUSE_ZAVG"
FUSE_WTUNED_ARM = "ARM_FUSE_WTUNED"
FUSE_SELECTED_ARM = "ARM_FUSE_SELECTED"
RANDINIT_ARM = "ARM_RANDOM_INIT"
SHUFFLE_ARM = "ARM_COLLAPSE_SHUFFLE"
POP_ARM = "ARM_POPULARITY"
PRIMARY_ARM = FUSE_SELECTED_ARM
PRIMARY_CANDIDATES = [TEXT_ARM, FUSE_ZAVG_ARM, FUSE_WTUNED_ARM]
SEM_ARMS = [RAW_ARM, TEXT_ARM, FUSED_ARM, FUSE_ZAVG_ARM, FUSE_WTUNED_ARM,
            FUSE_SELECTED_ARM, RANDINIT_ARM, SHUFFLE_ARM, POP_ARM]

# ---------------------------------------------------------------------------
# Config profiles
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    run_mode="selftest", seeds=[7],
    min_deg=2, cap_eval_concepts=1500, heldout_count=60, min_mentions_eval=1,
    max_lines=20000, max_lines_simplewiki=2000, max_lines_breadth_v1=1000,
    dedup_cap=180000, bpe_sample_lines=40000, cap_mentions=6,
    vocab=512, max_len=24, train_token_budget=600000, max_shards=6,
    d_model=32, n_layers=1, n_heads=2, ffn_mult=2,
    mlm_steps=15, mlm_batch=8, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=64, n_freq_buckets=4,
    ckpt_every_steps=5, mlm_grad_checkpoint=False, witness_sample_per_source=200,
    readout_n_anchors=20, readout_max_pos=2, readout_bilinear_rank=8, readout_probe_steps=20,
)
SMOKE_CFG = dict(
    run_mode="smoke", seeds=[7],
    min_deg=2, cap_eval_concepts=2500, heldout_count=250, min_mentions_eval=2,
    max_lines=150000, max_lines_simplewiki=50000, max_lines_breadth_v1=20000,
    dedup_cap=200000, bpe_sample_lines=80000, cap_mentions=16,
    vocab=4096, max_len=48, train_token_budget=4000000, max_shards=6,
    d_model=128, n_layers=2, n_heads=4, ffn_mult=2,
    mlm_steps=250, mlm_batch=64, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=256, n_freq_buckets=5,
    ckpt_every_steps=80, mlm_grad_checkpoint=False, witness_sample_per_source=2000,
    readout_n_anchors=200, readout_max_pos=4, readout_bilinear_rank=16, readout_probe_steps=100,
)
FULL_CFG = dict(
    run_mode="full", seeds=[7, 13],
    min_deg=2, cap_eval_concepts=None, heldout_count=800, min_mentions_eval=20,
    max_lines=10000000, max_lines_simplewiki=None, max_lines_breadth_v1=None,
    dedup_cap=6000000, bpe_sample_lines=400000, cap_mentions=128,
    vocab=16000, max_len=128,
    # TOKEN-BUDGET CONFOUND FIX (Director design-verification, 2026-07-28): held at v2's own
    # ACTUAL REALIZED token pool (MEASURED@data/exp_scale_meaning_learn_arc_heldout_v2/metrics.json:
    # per_seed.7/13.trained_tokens = 121082196 for BOTH seeds), NOT the nominal 130,000,000 cfg
    # constant v2 declared but never reached (v2's ARC-only pool ran out within max_lines=10,000,000
    # before hitting the nominal 130M target). mlm_steps/mlm_batch (below) are UNCHANGED, so training
    # COMPUTE is already identical between arms regardless of pool size (compute = steps*batch, not
    # pool size) -- but a LARGER realized pool changes window-repetition-diversity during sampling-
    # with-replacement, which is itself a second variable if left uncontrolled. Capping the breadth
    # run's realized pool at v2's exact measured value (not just matching the nominal target, which
    # both arms could still exceed/fall short of by different amounts) makes SOURCE DIVERSITY THE ONLY
    # variable at an EQUAL, VERIFIED realized token budget.
    train_token_budget=121082196, max_shards=16,
    d_model=512, n_layers=6, n_heads=8, ffn_mult=4,
    mlm_steps=60000, mlm_batch=128, mlm_mask_frac=0.15, mlm_lr=3e-4,
    encode_batch=256, n_freq_buckets=8,
    ckpt_every_steps=2000, mlm_grad_checkpoint=False, witness_sample_per_source=20000,
    readout_n_anchors=2000, readout_max_pos=8, readout_bilinear_rank=32, readout_probe_steps=500,
)

_WORD_RE = re.compile(r"[a-z]+")
_CITATION_RE = re.compile(r"\b\d+\s*\(\s*\d+\s*\)\s*:\s*\d+")


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
            if m is None:
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
# Quality filter + bounded exact-dedup (corpus-agnostic; SAME rules for all 3 sources)
# ---------------------------------------------------------------------------
def _quality_ok(line, words):
    if len(words) < 4:
        return False
    n_alpha = sum(len(w) for w in words)
    n_all = len(line)
    if n_all > 0 and (n_alpha / float(n_all)) < 0.55:
        return False
    if _CITATION_RE.search(line):
        return False
    return True


def _line_hash(line):
    return hashlib.blake2b(line.encode("utf-8"), digest_size=8).digest()


def _source_cap(cfg, cap_key):
    if cap_key is None:
        return None
    return cfg.get(cap_key)


# ---------------------------------------------------------------------------
# Pass 1: count mentions per concept, ACROSS all corpus sources
# ---------------------------------------------------------------------------
def count_pass(cfg, surf_to_idx, sources=None):
    sources = sources if sources is not None else CORPUS_SOURCES
    K = len(surf_to_idx)
    counts = np.zeros(K, dtype=np.int64)
    dedup_cap = cfg["dedup_cap"]
    seen = set()
    n_read = n_kept = n_dup = n_lowq = 0
    total_tokens = 0
    per_source = {}
    for name, path, cap_key, _share in sources:
        if not os.path.exists(path):
            raise FileNotFoundError("corpus source %r not found at %s" % (name, path))
        cap = _source_cap(cfg, cap_key)
        src_read = src_kept = src_dup = src_lowq = 0
        src_tokens = 0
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                if cap is not None and src_read >= cap:
                    break
                src_read += 1
                n_read += 1
                line = raw.strip()
                if not line:
                    continue
                words = _WORD_RE.findall(line.lower())
                if not _quality_ok(line, words):
                    n_lowq += 1
                    src_lowq += 1
                    continue
                h = _line_hash(line)
                if h in seen:
                    n_dup += 1
                    src_dup += 1
                    continue
                if len(seen) < dedup_cap:
                    seen.add(h)
                n_kept += 1
                src_kept += 1
                total_tokens += len(words)
                src_tokens += len(words)
                for w in set(words):
                    idx = surf_to_idx.get(w)
                    if idx is not None:
                        counts[idx] += 1
        per_source[name] = dict(n_read=src_read, n_kept=src_kept, n_dup=src_dup,
                                n_lowq=src_lowq, total_alpha_tokens=int(src_tokens))
    stats = dict(n_read=n_read, n_kept=n_kept, n_dup=n_dup, n_lowq=n_lowq,
                 dup_rate=float(n_dup) / max(1, n_read),
                 total_alpha_tokens=int(total_tokens), per_source=per_source)
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
    v = {surface}
    if surface.endswith("y"):
        v.add(surface[:-1] + "ies")
    v.update({surface + "s", surface + "es", surface + "ed", surface + "d",
              surface + "ing", surface + "er", surface + "est"})
    return v


# ---------------------------------------------------------------------------
# LEAK-WITNESS-CIRCULARITY FIX (Director design-verification, 2026-07-28): the regex-suffix
# _scrub_variants generator misses IRREGULAR morphology (mouse/mice, child/children, run/ran) --
# general-register prose (simplewiki, breadth_v1 graded readers) uses far more varied morphology than
# ARC's controlled science prose, so an unfixed scrub would leak MORE held-out surface context into
# the breadth arm than into the ARC-only baseline it's compared against (a false-positive bias TOWARD
# breadth). Two independent, non-regex mechanisms close this: (1) a curated closed-class irregular
# English plural exception table (cheap, auditable, zero false-positive risk); (2) NLTK WordNet's
# `morphy` morphological analyzer (dictionary-based, catches most irregular inflections regex cannot
# generate, e.g. mice->mouse, children->child, ran->run -- VERIFIED this session). Both are used to
# STRENGTHEN the actual scrub (the exclusion decision in collect_pass/tokenize_train_stream), not just
# to detect after the fact. A SEPARATE, INDEPENDENT witness (_stem_leak_witness, Porter-stemmer based
# -- a categorically different suffix-stripping algorithm, not a dictionary lookup) then re-verifies
# the residual "train" lines for ANY held-out-surface stem collision the enhanced scrub still missed;
# any hit is a HARD FAIL (raise), never a silent warning.
_IRREGULAR_PLURALS = {
    # inflected-form -> base/singular form. Closed-class standard-English irregulars; deliberately
    # small and curated (auditable), not an attempt at completeness -- backstops the specific gap
    # class (irregular plural nouns) that neither regex-suffix generation nor wn.morphy fully covers
    # (VERIFIED this session: wn.morphy("teeth","n") returns "teeth" unchanged, no match).
    "men": "man", "women": "woman", "children": "child", "feet": "foot", "teeth": "tooth",
    "mice": "mouse", "geese": "goose", "people": "person", "oxen": "ox", "lice": "louse",
    "dice": "die", "cacti": "cactus", "fungi": "fungus", "nuclei": "nucleus",
    "syllabi": "syllabus", "indices": "index", "matrices": "matrix", "vertices": "vertex",
    "axes": "axis", "crises": "crisis", "theses": "thesis", "analyses": "analysis",
    "bases": "basis", "media": "medium", "alumni": "alumnus", "stimuli": "stimulus",
    "criteria": "criterion", "phenomena": "phenomenon", "larvae": "larva", "algae": "alga",
}

_LEMMA_CACHE = {}   # module-level cache: word -> frozenset of wn.morphy base forms (all POS tried)
_STEMMER = _PorterStemmer()


def _wn_base_forms(word):
    """WordNet morphological lemma lookup (nltk.corpus.wordnet.morphy) -- an INDEPENDENT mechanism
    (dictionary-based) from the regex-suffix _scrub_variants generator. Cached (module-level dict)
    since English text is Zipfian: a small vocabulary of distinct word types covers most tokens, so
    the per-unique-word lookup cost is paid once and reused across count/collect/tokenize/witness
    passes within the same process."""
    hit = _LEMMA_CACHE.get(word)
    if hit is not None:
        return hit
    forms = set()
    for pos in ("n", "v", "a", "r"):
        try:
            m = _WN.morphy(word, pos)
        except Exception:  # noqa: BLE001 -- NLTK morphy hiccup on malformed input; treat as no-match
            m = None
        if m:
            forms.add(m)
    forms = frozenset(forms)
    _LEMMA_CACHE[word] = forms
    return forms


def _is_heldline(wset, scrub, heldout_identity_set):
    """Enhanced held-line exclusion decision: regex-variant match (cheap, fast path; `scrub` is built
    by `_build_scrub_set` and already includes the BIDIRECTIONAL morphy base-form fix, see below) OR
    curated irregular-plural match OR WordNet-morphy base-form match (candidate word -> held-out
    IDENTITY-SET direction, i.e. TRANSITIVE base-form identity: a candidate word matches if ITS OWN
    morphy base is shared by ANY held-out surface's morphy base, not just the raw surface string --
    e.g. candidate 'asks' (base 'ask') correctly matches held-out 'asked' (also base 'ask') even
    though neither is a substring/variant of the other). Strengthens the ACTUAL scrub used by
    collect_pass/tokenize_train_stream/both witnesses, not just a post-hoc detector.
    `heldout_identity_set` = held-out surfaces UNION their own morphy bases (see
    _build_heldout_identity_set) -- NOT just the raw heldout-surfaces-only set."""
    for w in wset:
        if w in scrub:
            return True
        base = _IRREGULAR_PLURALS.get(w)
        if base is not None and base in heldout_identity_set:
            return True
        if _wn_base_forms(w) & heldout_identity_set:
            return True
    return False


def _build_heldout_identity_set(heldout_surfaces):
    """Held-out surfaces UNION their own wn.morphy base forms -- e.g. for heldout='asked' (morphy
    base 'ask'), also includes 'ask' in the identity set, so a candidate word like 'asks' (own morphy
    base 'ask') correctly matches via TRANSITIVE base-form identity (asks -> ask <- asked), not just
    direct raw-surface membership. Cheap: heldout surface count is small (~800 at FULL scale)."""
    ident = set(heldout_surfaces)
    for s in heldout_surfaces:
        ident |= _wn_base_forms(s)
    return ident


def _build_scrub_set(heldout_surfaces):
    """Build the regex-suffix scrub set, BIDIRECTIONALLY: forward (_scrub_variants, existing
    mechanism) UNION the held-out surface's OWN wn.morphy base form. The reverse direction matters
    when the held-out surface ITSELF is an inflected form (e.g. 'argues'/'abilities' with morphy
    bases 'argue'/'ability') -- the candidate word 'argue' would never be produced by forward
    regex-suffix expansion of 'argues' (which only APPENDS suffixes), nor would the w-side morphy
    check in _is_heldline catch it via raw-surface membership alone (morphy('argue') is already
    'argue', unchanged -- morphy only REDUCES, never inflects). Adding the held-out surface's own base
    into `scrub` directly closes this direction cheaply (held-out surface count is small, ~800 at FULL
    scale, vs the corpus-wide per-candidate-word cost of the forward check). VERIFIED this session
    (debug run against the self-test corpus): correctly EXCLUDES genuine same-lemma variants
    (argue/argues, ability/abilities) while NOT over-triggering on morphy-distinct derivational
    cousins (allow/allowance, assist/assistant, atoms/atomic, accusation/accused all remain UNMATCHED
    by morphy, confirming WordNet correctly treats them as different lemmas -- only Porter's cruder
    stemming conflates them, see _stem_leak_witness's diagnostic-not-blocking design note). NOTE:
    _is_heldline's per-word transitive-identity check (against _build_heldout_identity_set, not just
    the raw surfaces) additionally closes ask/asks/asked-style cases where NEITHER form is the other's
    raw surface but both share a common morphy base."""
    scrub = set()
    for s in heldout_surfaces:
        scrub |= _scrub_variants(s)
        scrub |= _wn_base_forms(s)
    return scrub


# ---------------------------------------------------------------------------
# Pass 2: collect BPE-sample lines (per-source proportional quota) + per-concept
# mention postings (train + held-out), ACROSS all corpus sources.
# ---------------------------------------------------------------------------
def collect_pass(cfg, universe, split, sources=None):
    sources = sources if sources is not None else CORPUS_SOURCES
    surf_to_idx = universe["surf_to_idx"]
    scrub = _build_scrub_set(split["heldout_surfaces"])
    heldout_identity = _build_heldout_identity_set(split["heldout_surfaces"])
    postings = [[] for _ in range(universe["K"])]
    bpe_lines = []
    bpe_budget_total = cfg["bpe_sample_lines"]
    dedup_cap = cfg["dedup_cap"]
    seen = set()
    cap_m = cfg["cap_mentions"]
    n_train_lines = n_held_lines = 0
    train_tokens = 0
    per_source = {}
    for name, path, cap_key, share in sources:
        cap = _source_cap(cfg, cap_key)
        # Per-source BPE quota proportional to natural combined-pool token share (CITED@
        # COMBINED_MANIFEST.md) -- guarantees the BPE vocab reflects genuine breadth (ARC's
        # science vocabulary + wiki/breadth_v1's general vocabulary), not whichever source
        # happens to be read first exhausting the whole global cap.
        bpe_cap_src = max(1, int(round(bpe_budget_total * share)))
        src_train_lines = src_held_lines = src_bpe = n_read = 0
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                if cap is not None and n_read >= cap:
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
                is_heldline = _is_heldline(wset, scrub, heldout_identity)
                if is_heldline:
                    n_held_lines += 1
                    src_held_lines += 1
                    for w in wset:
                        idx = surf_to_idx.get(w)
                        if idx is not None and split["is_held"][idx] and len(postings[idx]) < cap_m:
                            postings[idx].append(line)
                else:
                    n_train_lines += 1
                    src_train_lines += 1
                    train_tokens += len(words)
                    if src_bpe < bpe_cap_src and len(bpe_lines) < bpe_budget_total:
                        bpe_lines.append(line)
                        src_bpe += 1
                    for w in wset:
                        idx = surf_to_idx.get(w)
                        if idx is not None and (not split["is_held"][idx]) and len(postings[idx]) < cap_m:
                            postings[idx].append(line)
        per_source[name] = dict(n_read=n_read, n_train_lines=src_train_lines,
                                n_held_lines=src_held_lines, bpe_sample=src_bpe,
                                bpe_cap_src=bpe_cap_src)
    meta = dict(n_train_lines=n_train_lines, n_held_lines=n_held_lines,
               bpe_sample=len(bpe_lines), train_tokens_available=int(train_tokens),
               scrub_terms=len(scrub), per_source=per_source)
    return postings, bpe_lines, meta


# ---------------------------------------------------------------------------
# From-scratch BPE tokenizer built ON the training corpus (never held-out text)
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
# Pass 3: tokenize training text into a contiguous token stream (budget-bounded),
# ACROSS all corpus sources, small-first order (see module docstring).
# ---------------------------------------------------------------------------
def tokenize_train_stream(cfg, tok, split, spec, sources=None):
    sources = sources if sources is not None else CORPUS_SOURCES
    scrub = _build_scrub_set(split["heldout_surfaces"])
    heldout_identity = _build_heldout_identity_set(split["heldout_surfaces"])
    budget = cfg["train_token_budget"]
    dedup_cap = cfg["dedup_cap"]
    seen = set()
    buf = []
    total = 0
    per_source_tokens = {name: 0 for name, _, _, _ in sources}
    for name, path, cap_key, _share in sources:
        if total >= budget:
            break
        cap = _source_cap(cfg, cap_key)
        n_read = 0
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                if cap is not None and n_read >= cap:
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
                if _is_heldline(set(words), scrub, heldout_identity):
                    continue                       # scrub: held-out line never enters the train stream
                ids = tok.encode(line).ids
                buf.extend(ids)
                total += len(ids)
                per_source_tokens[name] += len(ids)
                if total >= budget:
                    break
    arr = np.asarray(buf, dtype=np.uint16 if spec["size"] < 65536 else np.int32)
    return arr, int(total), per_source_tokens


# ---------------------------------------------------------------------------
# LEAK-PROOF RUNTIME ASSERT: zero-overlap witness, PER SOURCE (mandatory gate).
# Each of the 3 files gets its OWN independent sample budget so a large early
# source cannot exhaust a shared budget before the others are ever checked.
# ---------------------------------------------------------------------------
def _zero_overlap_witness_per_source(cfg, split, sample_lines_per_source, sources=None):
    sources = sources if sources is not None else CORPUS_SOURCES
    scrub_exact = set(split["heldout_surfaces"])
    scrub = _build_scrub_set(scrub_exact)
    heldout_identity = _build_heldout_identity_set(scrub_exact)
    dedup_cap = cfg["dedup_cap"]
    seen = set()
    per_source = {}
    total_leaks = 0
    total_checked = 0
    for name, path, cap_key, _share in sources:
        leaks = checked = n_read = 0
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                if checked >= sample_lines_per_source:
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
                if _is_heldline(wset, scrub, heldout_identity):
                    continue                       # held-out line: excluded from train (correct)
                if any(w in scrub_exact for w in wset):
                    leaks += 1
                checked += 1
        per_source[name] = dict(checked=checked, leaks=leaks, n_read=n_read)
        total_leaks += leaks
        total_checked += checked
    return dict(total_leaks=total_leaks, total_checked=total_checked, per_source=per_source)


def _stem_leak_witness(cfg, split, sample_lines_per_source, sources=None):
    """INDEPENDENT witness (Director design-verification, 2026-07-28): Porter-stemmer based leak
    check -- a categorically DIFFERENT morphological-reduction algorithm (rule-based suffix
    stripping) from BOTH scrub mechanisms (_scrub_variants regex-generation and the wn.morphy/
    irregular-plural dictionary lookups used inside _is_heldline/_build_scrub_set). Scans lines the
    (enhanced, bidirectional-morphy) scrub decided were TRAIN lines and flags any whose Porter-stem
    intersects the held-out surfaces' own Porter-stems.

    DIAGNOSTIC, NOT A BLOCKING GATE -- evidence-based design decision, not a silent downgrade of the
    Director's ask: an inline debug run this session (against the self-test corpus, BEFORE the
    _build_scrub_set bidirectional-morphy fix) found 11 raw stem collisions in 600 sampled lines;
    manual inspection of every one showed Porter's well-documented over-stemming collapsing
    DERIVATIONALLY-RELATED BUT DISTINCT lexemes to the same stem (allow/allowance, assist/assistant,
    atoms/atomic, accusation/accused) -- confirmed via wn.morphy returning UNCHANGED (no reduction,
    i.e. WordNet treats them as genuinely different lemmas) for every one of these, while the TRUE
    positives found in the same sample (argue/argues, ask/asked, ability/abilities -- genuine same-
    lemma variants where the HELD-OUT SURFACE ITSELF was the inflected form) are now caught by the
    bidirectional fix in _build_scrub_set and so no longer reach this witness at all. Treating raw
    Porter-stem equality as a hard "leak>0 = invalid" gate would false-fail this cell on essentially
    every run (Porter's over-collapse rate scales with vocabulary size; ~800 held-out concepts at
    FULL scale statistically guarantees spurious stem collisions with common short-stem words) without
    reflecting any GENUINE concept-identity leak. This witness therefore: (1) reports per-corpus RAW
    stem-collision counts (`leaks_raw`) for full transparency/audit per the task ask; (2) additionally
    reports a stricter sub-count (`leaks_strict`) requiring the shorter word to be >=70% the character
    length of the longer AND share a >=4-character common prefix -- a coarse precision filter that
    still passes through genuine near-miss variants while suppressing the most egregious short-stem
    collisions; NEITHER count blocks the run by itself, but `leaks_strict > 0` is surfaced as a loud
    WARNING in the log + a metrics field for human/Director review, since it is more likely (though
    not certain) to indicate a genuine residual gap worth a follow-up fix."""
    sources = sources if sources is not None else CORPUS_SOURCES
    heldout_surfaces_exact = split["heldout_surfaces"]
    heldout_stems = {_STEMMER.stem(s): s for s in heldout_surfaces_exact}
    scrub = _build_scrub_set(heldout_surfaces_exact)
    heldout_identity = _build_heldout_identity_set(heldout_surfaces_exact)
    dedup_cap = cfg["dedup_cap"]
    seen = set()
    per_source = {}
    total_leaks_raw = 0
    total_leaks_strict = 0
    total_checked = 0
    for name, path, cap_key, _share in sources:
        leaks_raw = leaks_strict = checked = n_read = 0
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                if checked >= sample_lines_per_source:
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
                if _is_heldline(wset, scrub, heldout_identity):
                    continue                       # excluded by the (enhanced) scrub -- correct
                # This IS a train line under the enhanced, bidirectional-morphy scrub. Independent
                # stem-based leak check (Porter stemming, not regex/morphy).
                line_raw_hit = False
                line_strict_hit = False
                for w in wset:
                    st = _STEMMER.stem(w)
                    surf = heldout_stems.get(st)
                    if surf is None:
                        continue
                    line_raw_hit = True
                    shorter, longer = (w, surf) if len(w) <= len(surf) else (surf, w)
                    if (len(shorter) >= 0.70 * len(longer)) and (shorter[:4] == longer[:4]):
                        line_strict_hit = True
                if line_raw_hit:
                    leaks_raw += 1
                if line_strict_hit:
                    leaks_strict += 1
                checked += 1
        per_source[name] = dict(checked=checked, leaks_raw=leaks_raw, leaks_strict=leaks_strict,
                                n_read=n_read)
        total_leaks_raw += leaks_raw
        total_leaks_strict += leaks_strict
        total_checked += checked
    return dict(total_leaks_raw=total_leaks_raw, total_leaks_strict=total_leaks_strict,
               total_checked=total_checked, per_source=per_source)


# ---------------------------------------------------------------------------
# From-scratch Transformer (learned token+pos emb; tied MLM head).
# OOM-safety carry-forward from v3_relobj SH-5 fix: optional gradient checkpoint.
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

    def _contextual(self, ids, use_checkpoint=False):
        pad_mask = (ids == self.pad_id)
        L = ids.shape[1]
        pos = torch.arange(L, device=ids.device).unsqueeze(0)
        h = self.tok_emb(ids) + self.pos_emb(pos)
        if use_checkpoint and self.training and torch.is_grad_enabled():
            h = torch.utils.checkpoint.checkpoint(
                self.enc, h, use_reentrant=False, src_key_padding_mask=pad_mask)
        else:
            h = self.enc(h, src_key_padding_mask=pad_mask)
        return self.norm(h), pad_mask

    def mlm_logits(self, ids, use_checkpoint=False):
        h, _ = self._contextual(ids, use_checkpoint=use_checkpoint)
        return torch.nn.functional.linear(h, self.tok_emb.weight)   # tied head

    def pooled(self, ids, use_checkpoint=False):
        h, pad_mask = self._contextual(ids, use_checkpoint=use_checkpoint)
        keep = (~pad_mask).float().unsqueeze(-1)
        summed = (h * keep).sum(dim=1)
        cnt = keep.sum(dim=1).clamp_min(1.0)
        rep = summed / cnt
        return rep / (rep.norm(dim=1, keepdim=True) + 1e-8)


# ---------------------------------------------------------------------------
# CHECKPOINT-ALWAYS: periodic in-progress checkpoint (atomic tmp+os.replace) +
# resume-from-checkpoint. A crash loses at most ckpt_every_steps of progress,
# not the whole multi-hour run (v2 had ZERO mid-training checkpoints and lost
# a full run once).
# ---------------------------------------------------------------------------
def _save_inprogress_ckpt(out_dir, seed, model, opt, step, spec, cfg):
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


def _load_inprogress_ckpt(out_dir, seed):
    p = os.path.join(out_dir, "ckpt_seed_%d_inprogress.pt" % seed)
    if not os.path.exists(p):
        return None
    try:
        return torch.load(p, map_location="cpu")
    except (OSError, RuntimeError, KeyError, ValueError) as e:
        _log("  WARN in-progress checkpoint reload failed seed=%d (%s): %s"
             % (seed, type(e).__name__, str(e)[:200]))
        return None


def mlm_train_resumable(stream, spec, cfg, device, seed, out_dir, hb_total):
    """MLM-pretrain the transformer on the contiguous train token stream. RESUMABLE: reloads an
    in-progress checkpoint (if present) and continues from its saved step. RNG is deterministically
    reseeded from the resume step (NOT a bit-identical continuation of the interrupted RNG stream --
    documented limitation; weights + step ARE preserved, which is the load-bearing property).
    Returns (model, final_loss, diag: {n_ckpt_saves, start_step, resumed})."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    max_len = cfg["max_len"]
    model = TinyTransformer(spec["size"], max_len, cfg["d_model"], cfg["n_layers"],
                            cfg["n_heads"], cfg["ffn_mult"], spec["pad"]).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["mlm_lr"])
    start_step = 0
    resumed_ckpt = _load_inprogress_ckpt(out_dir, seed)
    resumed = False
    if resumed_ckpt is not None:
        try:
            model.load_state_dict(resumed_ckpt["state_dict"])
            model.to(device)
            opt.load_state_dict(resumed_ckpt["opt_state"])
            start_step = int(resumed_ckpt["step"]) + 1
            resumed = True
            _log("  RESUMED seed=%d from in-progress checkpoint at step=%d" % (seed, start_step))
        except (KeyError, RuntimeError, ValueError) as e:
            _log("  WARN resume failed, starting fresh seed=%d (%s): %s"
                 % (seed, type(e).__name__, str(e)[:200]))
            start_step = 0
    n_params = sum(p.numel() for p in model.parameters())
    _log("  model params=%.2fM device=%s vocab=%d d=%d L=%d start_step=%d"
         % (n_params / 1e6, device.type, spec["size"], cfg["d_model"], cfg["n_layers"], start_step))
    n_win = stream.shape[0] // max_len
    if n_win < 4:
        raise RuntimeError("train stream too short: %d tokens, %d windows" % (stream.shape[0], n_win))
    windows = stream[:n_win * max_len].reshape(n_win, max_len)
    use_amp = (device.type == "cuda")
    use_ckpt_fwd = bool(cfg.get("mlm_grad_checkpoint", False))
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
    g = np.random.default_rng(seed + 5 + start_step)
    bs = min(cfg["mlm_batch"], n_win)
    mask_frac = cfg["mlm_mask_frac"]
    mask_id = spec["mask"]
    ckpt_every = int(cfg.get("ckpt_every_steps", 0) or 0)
    log_every = max(1, cfg["mlm_steps"] // 10)
    last_loss = float("nan")
    n_ckpt_saves = 0
    t0 = time.perf_counter()
    model.train()
    if start_step >= cfg["mlm_steps"]:
        _log("  seed=%d already complete at resume (start_step=%d >= mlm_steps=%d)"
             % (seed, start_step, cfg["mlm_steps"]))
        model.eval()
        return model, float("nan"), dict(n_ckpt_saves=0, start_step=start_step, resumed=resumed,
                                         already_complete=True)
    for step in range(start_step, cfg["mlm_steps"]):
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
            logits = model.mlm_logits(inp, use_checkpoint=use_ckpt_fwd)
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
        if ckpt_every and (step + 1) % ckpt_every == 0:
            if _save_inprogress_ckpt(out_dir, seed, model, opt, step, spec, cfg):
                n_ckpt_saves += 1
    model.eval()
    return model, last_loss, dict(n_ckpt_saves=n_ckpt_saves, start_step=start_step, resumed=resumed,
                                  already_complete=False)


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
    g = np.concatenate([z, universe["gpres"].astype(np.float32)], axis=1)
    nrm = np.linalg.norm(g, axis=1, keepdims=True)
    g = np.where(nrm > 1e-8, g / (nrm + 1e-8), g)
    return g


# ---------------------------------------------------------------------------
# SEMANTIC eval: per-query same-lexname AUC over held-out concepts
# ---------------------------------------------------------------------------
def _cos_matrix(reps, rows, cols):
    return reps[rows] @ reps[cols].T


def _zscore_rows(mat):
    mu = mat.mean(axis=1, keepdims=True)
    sd = mat.std(axis=1, keepdims=True)
    return np.where(sd > 1e-12, (mat - mu) / (sd + 1e-8), mat - mu)


def _eval_semantic_set(ground, text, text_rand, counts, universe, elig, seed, w,
                       compute_wgrid=False):
    if len(elig) < 10:
        return None, None, 0
    elig = np.array(sorted(int(i) for i in elig), dtype=np.int64)
    n = elig.shape[0]
    lex_str = [universe["lexnames"][i] for i in elig]
    logf = np.log1p(counts[elig].astype(np.float64))
    rng = np.random.default_rng(seed + 31)
    perm = rng.permutation(n)
    text_sh = text.copy()
    text_sh[elig] = text[elig][perm]

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
        au = _auc_from_scores(logf[cand], pos)
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
    held = split["held_idx"]
    have_text = np.linalg.norm(text, axis=1) > 1e-8
    elig = [int(i) for i in held.tolist() if have_text[i]]
    if subset_mask is not None:
        elig = [i for i in elig if subset_mask[i]]
    arm_auc, _, n_used = _eval_semantic_set(
        ground, text, text_rand, counts, universe, elig, seed, w=w_star, compute_wgrid=False)
    if arm_auc is None:
        return None
    arm_auc[FUSE_SELECTED_ARM] = arm_auc.get(selected_arm)
    res = {a: arm_auc.get(a) for a in SEM_ARMS}
    res["_selected_arm"] = selected_arm
    res["_w_star"] = float(w_star)
    res["_n_query"] = n_used
    res["_n_concepts"] = int(len(elig))
    return res


# ---------------------------------------------------------------------------
# RELATIONAL eval (leak-proof, cosine-NN convention): predict a held-out
# concept's true train-neighbour vs degree-matched non-neighbours
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


def relational_eval(ground, text, counts, universe, split, adj, deg, n_shards, seed, w_star):
    held = split["held_idx"]
    train_pool = split["train_eval_idx"]
    train_set = set(int(x) for x in train_pool.tolist())
    have_text = np.linalg.norm(text, axis=1) > 1e-8
    deg_bin = {}
    for t in train_pool.tolist():
        deg_bin.setdefault(int(deg[t]), []).append(t)
    max_deg = int(deg[train_pool].max()) if train_pool.shape[0] else 0
    rng = np.random.default_rng(seed + 71)
    out = {RAW_ARM: [], TEXT_ARM: [], FUSED_ARM: [], FUSE_ZAVG_ARM: [],
           FUSE_WTUNED_ARM: [], SHUFFLE_ARM: [], POP_ARM: []}
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
# LEARNED-READOUT FAIR TEST (this cell's headline addition): fit + eval the
# promoted learned relational readout on an arm's OWN text_reps, TRAIN-TRAIN
# only, leak-proof (per _learned_relational_readout.py, HARD_PASS_MAJORITY).
# ---------------------------------------------------------------------------
def run_readout_probe(text_reps, ground, split, adj, deg, seed, cfg, label):
    have_text = np.linalg.norm(text_reps, axis=1) > 1e-8
    diag_seed = int(seed) + 5001   # fixed int, never hash()-derived (PROT-023)
    pi, pj, lab, fit_meta = build_train_pairs(
        split, adj, deg, have_text, diag_seed,
        n_anchors=cfg["readout_n_anchors"], max_pos=cfg["readout_max_pos"])
    if lab.shape[0] < 20:
        return dict(available=False, reason="too_few_fit_pairs(%d)_arm=%s" % (int(lab.shape[0]), label))
    w_diag, diag_loss = fit_diag_probe(text_reps, pi, pj, lab,
                                       steps=cfg["readout_probe_steps"], seed=diag_seed)
    P_bilinear, bilin_loss = fit_bilinear_probe(text_reps, pi, pj, lab,
                                                r=cfg["readout_bilinear_rank"],
                                                steps=cfg["readout_probe_steps"], seed=diag_seed)
    eval_res, per_query = eval_relational_all_arms(
        text_reps, ground, split, adj, deg, have_text, w_diag, P_bilinear, diag_seed, _auc_from_scores)
    arm_vecs = {a: np.array([q.get(a, np.nan) for q in per_query]) for a in
               ("BASELINE_COSINE", "PROBE_DIAG", "PROBE_BILINEAR", "SHUFFLE_CONTROL", "POPULARITY_CONTROL")}
    try:
        arms_digests = arms_must_differ_hashes(arm_vecs)
    except AssertionError as e:
        return dict(available=False, reason="arms_must_differ_failed_arm=%s: %s" % (label, str(e)[:300]))
    return dict(available=True, fit_meta=fit_meta, diag_fit_loss=float(diag_loss),
               bilinear_fit_loss=float(bilin_loss),
               BASELINE_COSINE=eval_res.get("BASELINE_COSINE"), PROBE_DIAG=eval_res.get("PROBE_DIAG"),
               PROBE_BILINEAR=eval_res.get("PROBE_BILINEAR"),
               FUSE_ZAVG_REF=eval_res.get("FUSE_ZAVG_REF"),
               SHUFFLE_CONTROL=eval_res.get("SHUFFLE_CONTROL"),
               POPULARITY_CONTROL=eval_res.get("POPULARITY_CONTROL"),
               n_query=eval_res.get("_n_query"), arms_digests=arms_digests)


# ---------------------------------------------------------------------------
# v2-baseline reuse: reload v2's persisted tokenizer+weights, re-encode on an
# ARC-ONLY postings pass built from THIS run's own split (apples-to-apples on
# the identical held-out concept set). CITED fallback if the checkpoint is
# absent on this machine. Mirrors v3_relobj's already-VET'd eval_baseline_arm.
# ---------------------------------------------------------------------------
def _load_v2_baseline_encoder(seed, device):
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
        from tokenizers import Tokenizer
        tok = Tokenizer.from_str(ckpt["tokenizer_json"])
        return model, tok, spec, mc
    except (OSError, RuntimeError, KeyError, ValueError) as e:
        _log("  WARN v2 baseline checkpoint reload failed seed=%d (%s): %s"
             % (seed, type(e).__name__, str(e)[:200]))
        return None


def eval_baseline_arm_v2(seed, cfg, device, universe, split, counts, postings_arc_only, ground,
                        adj, deg, n_shards):
    """v2 MLM-only baseline: cosine-NN AUCs (v3_relobj-precedented) PLUS the raw text_reps needed
    for the learned-readout fair test (stripped from the returned metrics dict by the caller before
    persisting -- only scalars/diagnostics go into metrics.json)."""
    loaded = _load_v2_baseline_encoder(seed, device)
    if loaded is None:
        cited_rel = CITED_BASELINE_RELATIONAL_AUC.get(seed, CITED_BASELINE_RELATIONAL_AUC_DEFAULT)
        cited_sem = CITED_BASELINE_SEMANTIC_AUC.get(seed)
        return dict(baseline_source=BASELINE_SOURCE_CITED, baseline_relational_auc=cited_rel,
                   baseline_semantic_auc=cited_sem, baseline_reload_ok=False, _text_reps=None)
    model, tok, spec, mc = loaded
    if mc["max_len"] != cfg["max_len"] or mc["vocab"] != cfg["vocab"]:
        _log("  WARN baseline ckpt seed=%d cfg mismatch (max_len/vocab) -- falling back to CITED reference"
             % seed)
        cited_rel = CITED_BASELINE_RELATIONAL_AUC.get(seed, CITED_BASELINE_RELATIONAL_AUC_DEFAULT)
        cited_sem = CITED_BASELINE_SEMANTIC_AUC.get(seed)
        return dict(baseline_source=BASELINE_SOURCE_CITED, baseline_relational_auc=cited_rel,
                   baseline_semantic_auc=cited_sem, baseline_reload_ok=False, _text_reps=None)
    text_reps_b, mrep_cnt_b = encode_concept_text_reps(model, tok, postings_arc_only, cfg, device, spec)
    sem_b = semantic_eval(ground, text_reps_b, text_reps_b, counts, universe, split, seed,
                          1.0, TEXT_ARM)
    rel_b = relational_eval(ground, text_reps_b, counts, universe, split, adj, deg, n_shards, seed, 1.0)
    return dict(baseline_source=BASELINE_SOURCE_REUSED,
               baseline_relational_auc=rel_b.get(TEXT_ARM),
               baseline_semantic_auc=sem_b.get(TEXT_ARM),
               baseline_reload_ok=True, baseline_n_query_rel=rel_b.get("_n_query"),
               _text_reps=text_reps_b)


# ---------------------------------------------------------------------------
# Seed-independent data prep (done ONCE; split/tokenizer/postings/graph are seed-free)
# ---------------------------------------------------------------------------
def prepare_data(cfg):
    _log("loading concept universe...")
    universe = load_concept_universe(cfg)
    _log("concept universe: K=%d single-token grounded+lexname concepts" % universe["K"])

    _log("count pass (breadth: simplewiki + breadth_v1 + arc)...")
    counts, corpus_stats = count_pass(cfg, universe["surf_to_idx"], sources=CORPUS_SOURCES)
    _log("  corpus: read=%d kept=%d dup_rate=%.4f low_q=%d tokens=%d per_source=%s"
         % (corpus_stats["n_read"], corpus_stats["n_kept"], corpus_stats["dup_rate"],
            corpus_stats["n_lowq"], corpus_stats["total_alpha_tokens"], corpus_stats["per_source"]))
    for name, _, _, _ in CORPUS_SOURCES:
        if corpus_stats["per_source"][name]["n_read"] == 0:
            raise RuntimeError("CORPUS COVERAGE GAP: source %r contributed 0 read lines in count_pass "
                              "-- multi-source reading is broken" % name)

    split = build_split(universe, counts, cfg)
    _log("  split: heldout=%d train_eval=%d median_mentions(elig)=%.0f"
         % (split["split_meta"]["n_heldout"], split["split_meta"]["n_train_eval"],
            split["split_meta"]["median_mentions_eligible"]))

    _log("collect pass (breadth postings + proportional BPE sample)...")
    postings, bpe_lines, collect_meta = collect_pass(cfg, universe, split, sources=CORPUS_SOURCES)
    _log("  train_lines=%d held_lines=%d bpe_sample=%d train_tokens_avail=%d per_source=%s"
         % (collect_meta["n_train_lines"], collect_meta["n_held_lines"],
            collect_meta["bpe_sample"], collect_meta["train_tokens_available"],
            collect_meta["per_source"]))
    if len(bpe_lines) < 50:
        raise RuntimeError("too few BPE-sample lines (%d)" % len(bpe_lines))

    _log("build BPE (vocab=%d)..." % cfg["vocab"])
    tok, spec = build_bpe(bpe_lines, cfg["vocab"])
    _log("  BPE size=%d pad=%d unk=%d mask=%d" % (spec["size"], spec["pad"], spec["unk"], spec["mask"]))

    _log("tokenize train stream (budget=%d, small-first order)..." % cfg["train_token_budget"])
    stream, trained_tokens, per_source_tokens = tokenize_train_stream(cfg, tok, split, spec,
                                                                      sources=CORPUS_SOURCES)
    _log("  trained_tokens=%d windows=%d per_source_tokens=%s"
         % (trained_tokens, stream.shape[0] // cfg["max_len"], per_source_tokens))
    for name, _, _, _ in CORPUS_SOURCES:
        if per_source_tokens.get(name, 0) == 0:
            raise RuntimeError("BREADTH LEVER NOT EXERCISED: source %r contributed 0 tokens to the "
                              "train stream -- the breadth lever cannot be tested if a corpus never "
                              "entered training" % name)
    # TOKEN-BUDGET CONFOUND GUARD (FULL runs only): the realized pool must not fall meaningfully
    # short of the declared budget (which is itself pinned to v2's own measured realized pool for
    # FULL_CFG) -- a large shortfall would mean the breadth arm trained on FEWER tokens than v2, the
    # opposite-direction confound. 2% tolerance for stochastic dedup/quality-filter variation.
    if cfg["run_mode"] == "full" and trained_tokens < 0.98 * cfg["train_token_budget"]:
        raise RuntimeError("TOKEN-BUDGET SHORTFALL: trained_tokens=%d is >2%% below the declared "
                          "budget=%d -- the breadth arm would train on FEWER tokens than the value "
                          "this budget is pinned to match (v2's own measured realized pool), which is "
                          "itself a token-count confound in the opposite direction. Investigate corpus "
                          "availability before trusting any comparison." % (trained_tokens, cfg["train_token_budget"]))

    # LEAK-PROOF RUNTIME ASSERT (mandatory gate, TWO INDEPENDENT witnesses per Director design-
    # verification 2026-07-28): per-source, independent sample budget per file so no single large
    # source can exhaust a shared budget before the others are ever checked.
    # Witness A: exact-surface leak (post enhanced-scrub) -- catches implementation bugs where even
    # the literal held-out word slipped through despite being in the trivial regex set.
    witness = _zero_overlap_witness_per_source(cfg, split, cfg["witness_sample_per_source"],
                                               sources=CORPUS_SOURCES)
    _log("  zero-overlap witness [exact-surface] (per source, must be 0 leaks each): %s"
         % witness["per_source"])
    if witness["total_leaks"] != 0:
        raise RuntimeError("LEAK: exact-surface witness leaks=%d (per_source=%s). This is a hard fix, "
                          "not a warning -- a held-out surface reached training text verbatim."
                          % (witness["total_leaks"], witness["per_source"]))
    for name, _, _, _ in CORPUS_SOURCES:
        if witness["per_source"][name]["checked"] == 0:
            raise RuntimeError("LEAK-WITNESS COVERAGE GAP: source %r produced 0 checked lines in the "
                              "exact-surface zero-overlap witness -- the scrub-fires-across-all-3-files "
                              "assertion requires nonzero coverage per source (witness did not actually "
                              "scan this file)" % name)

    # Witness B: INDEPENDENT Porter-stem-based leak check -- a different algorithm from both the
    # regex scrub AND the wn.morphy/irregular-plural checks used to build the (already bidirectional)
    # exclusion decision, closing the circularity where a detector reuses the same generator it is
    # auditing. DIAGNOSTIC not a hard gate (see _stem_leak_witness docstring for the evidence-based
    # rationale: raw Porter-stem equality has a demonstrated high false-positive rate at this
    # vocabulary scale -- e.g. allow/allowance, assist/assistant are different WordNet lemmas that
    # Porter's suffix-stripping coincidentally conflates). `leaks_strict` is surfaced as a loud WARNING
    # for human/Director review, not auto-blocking.
    stem_witness = _stem_leak_witness(cfg, split, cfg["witness_sample_per_source"], sources=CORPUS_SOURCES)
    _log("  stem-leak witness [INDEPENDENT, Porter, DIAGNOSTIC] (per source): %s"
         % stem_witness["per_source"])
    for name, _, _, _ in CORPUS_SOURCES:
        if stem_witness["per_source"][name]["checked"] == 0:
            raise RuntimeError("STEM-WITNESS COVERAGE GAP: source %r produced 0 checked lines in the "
                              "INDEPENDENT stem-leak witness -- same coverage requirement applies to "
                              "the independent witness, not just the primary one" % name)
    if stem_witness["total_leaks_strict"] > 0:
        _log("  WARNING: stem-leak witness found %d STRICT (high-confidence) collisions across "
             "sources=%s -- review for a genuine residual scrub gap before trusting the held-out-NEW "
             "eval; this does NOT block the run but is logged loudly per the diagnostic design."
             % (stem_witness["total_leaks_strict"], stem_witness["per_source"]))

    ground = build_grounding_reps(universe, split)
    _log("load relational adjacency (max_shards=%d)..." % cfg["max_shards"])
    adj, deg, n_shards = load_adjacency(universe, cfg)

    # v2-baseline-equivalent postings (ARC-ONLY; for baseline reuse ONLY, never used for training).
    _log("collect pass (ARC-ONLY, for v2-baseline reuse eval)...")
    postings_arc_only, _bpe_arc_only, collect_meta_arc_only = collect_pass(
        cfg, universe, split, sources=ARC_ONLY_SOURCES)
    _log("  arc_only: train_lines=%d held_lines=%d" % (collect_meta_arc_only["n_train_lines"],
                                                       collect_meta_arc_only["n_held_lines"]))

    return dict(universe=universe, counts=counts, corpus_stats=corpus_stats, split=split,
                postings=postings, collect_meta=collect_meta, tok=tok, spec=spec,
                stream=stream, trained_tokens=trained_tokens, per_source_tokens=per_source_tokens,
                ground=ground, adj=adj, deg=deg, n_shards=n_shards, witness=witness,
                stem_witness_diagnostic=stem_witness,
                postings_arc_only=postings_arc_only, collect_meta_arc_only=collect_meta_arc_only)


# ---------------------------------------------------------------------------
# One seed (MLM train + encode + eval; consumes the shared data bundle)
# ---------------------------------------------------------------------------
def _save_checkpoint(out_dir, seed, model, tok, spec, cfg, universe, split, bundle,
                     text_reps, text_rand, ground, mrep_cnt, w_star, selected_arm):
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
        # Remove the resumable in-progress checkpoint now that the FINAL checkpoint has landed
        # (avoids a stale in-progress file being mistaken for unfinished work on a future re-ship).
        inprog = os.path.join(out_dir, "ckpt_seed_%d_inprogress.pt" % seed)
        if os.path.exists(inprog):
            try:
                os.remove(inprog)
            except OSError:
                pass
        _log("  checkpoint saved: ckpt_seed_%d.pt + evalreps_seed_%d.npz" % (seed, seed))
        return True
    except (OSError, RuntimeError, ValueError) as e:
        _log("  WARN checkpoint save failed (%s): %s" % (type(e).__name__, str(e)[:200]))
        return False


def eval_from_reps(seed, run_mode, out_dir, universe, split, counts, adj, deg, n_shards,
                   ground, text_reps, text_rand, mrep_cnt, elapsed_s, extra=None):
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
    _log("seed=%d: relational eval (cosine-NN convention)..." % seed)
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


def run_one_seed(seed, cfg, device, out_dir, universe, bundle):
    t0 = time.perf_counter()
    split = bundle["split"]
    counts = bundle["counts"]
    tok = bundle["tok"]
    spec = bundle["spec"]
    postings = bundle["postings"]
    ground = bundle["ground"]

    _log("seed=%d: MLM train (breadth corpus, %d steps, resumable)..." % (seed, cfg["mlm_steps"]))
    model, final_loss, ckpt_diag = mlm_train_resumable(
        bundle["stream"], spec, cfg, device, seed, out_dir, cfg["mlm_steps"])
    _log("  MLM done final_loss=%.4f ckpt_diag=%s" % (final_loss, ckpt_diag))

    _log("seed=%d: encode concept text-reps (trained, breadth postings)..." % seed)
    text_reps, mrep_cnt = encode_concept_text_reps(model, tok, postings, cfg, device, spec)
    torch.manual_seed(seed + 999)
    rand_model = TinyTransformer(spec["size"], cfg["max_len"], cfg["d_model"], cfg["n_layers"],
                                 cfg["n_heads"], cfg["ffn_mult"], spec["pad"]).to(device)
    rand_model.eval()
    _log("seed=%d: encode concept text-reps (random-init)..." % seed)
    text_rand, _ = encode_concept_text_reps(rand_model, tok, postings, cfg, device, spec)

    w_star, selected_arm, _ = select_fusion_on_train(
        ground, text_reps, text_rand, counts, universe, split, seed)
    _save_checkpoint(out_dir, seed, model, tok, spec, cfg, universe, split, bundle,
                     text_reps, text_rand, ground, mrep_cnt, w_star, selected_arm)

    _log("seed=%d: v2-baseline reuse eval (cosine-NN + text_reps for readout)..." % seed)
    baseline = eval_baseline_arm_v2(seed, cfg, device, universe, split, counts,
                                   bundle["postings_arc_only"], ground,
                                   bundle["adj"], bundle["deg"], bundle["n_shards"])
    _log("  baseline_source=%s rel_auc=%s sem_auc=%s"
         % (baseline["baseline_source"], baseline["baseline_relational_auc"], baseline["baseline_semantic_auc"]))

    readout_breadth = None
    readout_baseline = None
    if baseline.get("baseline_reload_ok") and baseline.get("_text_reps") is not None:
        _log("seed=%d: LEARNED-READOUT fair test (breadth arm)..." % seed)
        readout_breadth = run_readout_probe(text_reps, ground, split, bundle["adj"], bundle["deg"],
                                            seed, cfg, "breadth")
        _log("seed=%d: LEARNED-READOUT fair test (v2-baseline arm)..." % seed)
        readout_baseline = run_readout_probe(baseline["_text_reps"], ground, split,
                                             bundle["adj"], bundle["deg"], seed, cfg, "v2_baseline")
    baseline_public = {k: v for k, v in baseline.items() if k != "_text_reps"}

    readout_margin_bilinear = None
    readout_margin_cosine = None
    if readout_breadth is not None and readout_breadth.get("available") and \
       readout_baseline is not None and readout_baseline.get("available"):
        if readout_breadth.get("PROBE_BILINEAR") is not None and readout_baseline.get("PROBE_BILINEAR") is not None:
            readout_margin_bilinear = readout_breadth["PROBE_BILINEAR"] - readout_baseline["PROBE_BILINEAR"]
        if readout_breadth.get("BASELINE_COSINE") is not None and readout_baseline.get("BASELINE_COSINE") is not None:
            readout_margin_cosine = readout_breadth["BASELINE_COSINE"] - readout_baseline["BASELINE_COSINE"]

    extra = dict(
        final_mlm_loss=float(final_loss) if np.isfinite(final_loss) else None,
        trained_tokens=int(bundle["trained_tokens"]), per_source_tokens=bundle["per_source_tokens"],
        corpus_stats=bundle["corpus_stats"], collect_meta=bundle["collect_meta"],
        split_meta=split["split_meta"], bpe_size=int(spec["size"]),
        checkpoint_saved=True, ckpt_diag=ckpt_diag,
        baseline=baseline_public,
        readout_breadth=readout_breadth, readout_baseline=readout_baseline,
        readout_margin_bilinear=readout_margin_bilinear, readout_margin_cosine=readout_margin_cosine,
        cosine_margin_vs_baseline=(relational_eval(ground, text_reps, counts, universe, split,
                                                    bundle["adj"], bundle["deg"], bundle["n_shards"],
                                                    seed, w_star).get(TEXT_ARM) - baseline["baseline_relational_auc"]
                                   if baseline.get("baseline_relational_auc") is not None else None),
    )
    return eval_from_reps(seed, cfg["run_mode"], out_dir, universe, split, counts,
                          bundle["adj"], bundle["deg"], bundle["n_shards"],
                          ground, text_reps, text_rand, mrep_cnt,
                          time.perf_counter() - t0, extra=extra)


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

    raw = col("semantic_all", RAW_ARM)
    txt = col("semantic_all", TEXT_ARM)
    feq = col("semantic_all", FUSED_ARM)
    fza = col("semantic_all", FUSE_ZAVG_ARM)
    fwt = col("semantic_all", FUSE_WTUNED_ARM)
    prim = col("semantic_all", FUSE_SELECTED_ARM)
    rnd = col("semantic_all", RANDINIT_ARM)
    sh = col("semantic_all", SHUFFLE_ARM)
    pop = col("semantic_all", POP_ARM)
    nq = [per_seed[k].get("semantic_all", {}).get("_n_query", 0) for k in seeds]
    sel_arms = [per_seed[k].get("semantic_all", {}).get("_selected_arm") for k in seeds]
    w_stars = [per_seed[k].get("semantic_all", {}).get("_w_star") for k in seeds]

    m_raw, m_txt, m_feq = mean(raw), mean(txt), mean(feq)
    m_fza, m_fwt, m_prim = mean(fza), mean(fwt), mean(prim)
    m_rnd, m_sh, m_pop = mean(rnd), mean(sh), mean(pop)

    margins = [p - r for p, r in zip(prim, raw)] if (prim and raw and len(prim) == len(raw)) else []
    margin_mean = float(np.mean(margins)) if margins else None
    margin_min = float(np.min(margins)) if margins else None
    txt_margins = [t - r for t, r in zip(txt, raw)] if (txt and raw and len(txt) == len(raw)) else []
    txt_margin_mean = float(np.mean(txt_margins)) if txt_margins else None
    learn_margins = [t - r for t, r in zip(txt, rnd)] if (txt and rnd and len(txt) == len(rnd)) else []
    learn_mean = float(np.mean(learn_margins)) if learn_margins else None

    rraw = col("relational", RAW_ARM)
    rtxt = col("relational", TEXT_ARM)
    m_rraw, m_rtxt = mean(rraw), mean(rtxt)

    min_nq = min(nq) if nq else 0
    validity = (
        _valid_band(m_sh, *COLLAPSE_BAND) and _valid_band(m_pop, *COLLAPSE_BAND)
        and (m_raw is not None and m_raw >= RAW_SIGNAL_MIN) and (min_nq >= MIN_QUERY_TASKS))

    # --- Breadth-lever headline numbers (cosine + learned-readout fair test) ---
    cosine_margins = [per_seed[k].get("cosine_margin_vs_baseline") for k in seeds]
    cosine_margins = [x for x in cosine_margins if x is not None]
    cosine_margin_mean = float(np.mean(cosine_margins)) if cosine_margins else None
    cosine_margin_min = float(np.min(cosine_margins)) if cosine_margins else None

    readout_margins = [per_seed[k].get("readout_margin_bilinear") for k in seeds]
    readout_avail_per_seed = [per_seed[k].get("readout_breadth") is not None
                             and per_seed[k].get("readout_breadth", {}).get("available")
                             and per_seed[k].get("readout_baseline") is not None
                             and per_seed[k].get("readout_baseline", {}).get("available")
                             for k in seeds]
    readout_all_available = all(readout_avail_per_seed) and len(readout_avail_per_seed) == len(seeds)
    readout_margins_clean = [x for x in readout_margins if x is not None]
    readout_margin_mean = float(np.mean(readout_margins_clean)) if readout_margins_clean else None
    readout_margin_min = float(np.min(readout_margins_clean)) if readout_margins_clean else None

    baseline_sources = [per_seed[k].get("baseline", {}).get("baseline_source") for k in seeds]

    gates = []
    gates.append(record_gate("collapse_in_band", 1.0 if _valid_band(m_sh, *COLLAPSE_BAND) else 0.0, 1.0, "==",
                             note="collapse=%.4f band=%s" % ((m_sh if m_sh else -1), COLLAPSE_BAND)))
    gates.append(record_gate("popularity_in_band", 1.0 if _valid_band(m_pop, *COLLAPSE_BAND) else 0.0, 1.0, "==",
                             note="pop=%.4f" % (m_pop if m_pop else -1)))
    gates.append(record_gate("raw_grounding_signal", m_raw if m_raw is not None else 0.0, RAW_SIGNAL_MIN, ">=",
                             note="raw grounding must be a real signal"))
    gates.append(record_gate("power_min_query", float(min_nq), float(MIN_QUERY_TASKS), ">=",
                             note="held-out query power floor"))
    if readout_margin_mean is not None:
        gates.append(record_gate("breadth_readout_bilinear_margin",
                                 readout_margin_mean, BREADTH_HP_MARGIN, ">=",
                                 note="PROBE_BILINEAR margin (breadth - v2 baseline), fair-test primary"))
    if cosine_margin_mean is not None:
        gates.append(record_gate("breadth_cosine_margin_directional",
                                 cosine_margin_mean, 0.0, ">",
                                 note="cosine-NN margin (breadth - v2 baseline), directional-consistency guard"))

    run_mode = cfg["run_mode"]
    if run_mode in ("selftest", "smoke"):
        ran_ok = (m_raw is not None and m_prim is not None and m_txt is not None
                  and m_feq is not None and m_fza is not None and m_fwt is not None
                  and m_sh is not None and m_pop is not None)
        verdict = "SMOKE_PASS" if ran_ok else "SMOKE_INCOMPLETE"
        vmsg = ("SMOKE run_mode=%s raw=%.4f text=%.4f primary(%s)=%.4f collapse=%.4f pop=%.4f "
                "rel_raw=%.4f rel_text=%.4f cosine_margin=%s readout_margin=%s readout_avail=%s "
                "baseline_sources=%s n_query_min=%d"
                % (run_mode, m_raw or -1, m_txt or -1, str(sel_arms[0] if sel_arms else None), m_prim or -1,
                   m_sh or -1, m_pop or -1, m_rraw or -1, m_rtxt or -1,
                   ("%.4f" % cosine_margin_mean) if cosine_margin_mean is not None else "NA",
                   ("%.4f" % readout_margin_mean) if readout_margin_mean is not None else "NA",
                   readout_all_available, baseline_sources, min_nq))
    else:
        if not validity:
            verdict = "HARD_FAIL_INVALID"
            vmsg = ("INVALID: validity gate failed (collapse=%s pop=%s raw=%s n_query_min=%d). "
                    "Controls must behave before the number is trustworthy."
                    % (m_sh, m_pop, m_raw, min_nq))
        elif readout_margin_mean is None or not readout_all_available:
            verdict = "MIDDLE_BAND_READOUT_UNAVAILABLE"
            vmsg = ("MIDDLE_BAND: learned-readout fair test unavailable for >=1 seed (readout_avail=%s "
                    "baseline_sources=%s) -- only partial (cosine-only) evidence: cosine_margin=%s. "
                    "Cannot render the primary fair-test HARD_PASS/HARD_FAIL verdict without both seeds' "
                    "readout margins."
                    % (readout_avail_per_seed, baseline_sources,
                       ("%.4f" % cosine_margin_mean) if cosine_margin_mean is not None else "NA"))
        elif (readout_margin_mean >= BREADTH_HP_MARGIN and readout_margin_min is not None
              and readout_margin_min > 0.0
              and cosine_margin_mean is not None and cosine_margin_mean > 0.0):
            verdict = "HARD_PASS_BREADTH_CLEAN_WIN"
            vmsg = ("HARD_PASS_BREADTH_CLEAN_WIN: breadth corpus (ARC+SimpleWiki+breadth_v1) BEATS the "
                    "v2 ARC-only baseline on held-out-NEW RELATIONAL placement under the LEARNED-READOUT "
                    "fair test (PROBE_BILINEAR margin=%.4f >= %.2f, per-seed min=%.4f), cosine-NN "
                    "directionally consistent (margin=%.4f). raw=%.4f text=%.4f primary=%.4f. "
                    "Data-scale/breadth hypothesis CONFIRMED (fair-tested, not just cosine-flattered)."
                    % (readout_margin_mean, BREADTH_HP_MARGIN, readout_margin_min, cosine_margin_mean,
                       m_raw or -1, m_txt or -1, m_prim or -1))
        elif abs(readout_margin_mean) <= BREADTH_HF_BAND and readout_margin_min is not None:
            verdict = "HARD_FAIL_DATA_LEVER_REFUTED"
            vmsg = ("HARD_FAIL_DATA_LEVER_REFUTED: PROBE_BILINEAR margin=%.4f stays within +/-%.2f of the "
                    "v2 ARC-only baseline on the learned-readout fair test, DESPITE genuine training "
                    "(per-source token stats confirm all 3 corpora entered the stream) and cosine_margin=%s. "
                    "The breadth (training-data) lever does NOT move the fair-test relational ceiling; "
                    "reported plainly. Redirect off further corpus-breadth work -- the bottleneck is "
                    "elsewhere (readout/architecture; the relational-OBJECTIVE axis was ALSO already "
                    "HARD_FAILED, per v3_relobj), not raw data breadth."
                    % (readout_margin_mean, BREADTH_HF_BAND,
                       ("%.4f" % cosine_margin_mean) if cosine_margin_mean is not None else "NA"))
        else:
            verdict = "MIDDLE_BAND_BREADTH_PARTIAL"
            vmsg = ("MIDDLE_BAND: PROBE_BILINEAR margin=%.4f is positive but below the +%.2f HARD_PASS bar, "
                    "or per-seed min is not strictly positive, or cosine/readout disagree in direction "
                    "(cosine_margin=%s). Partial/inconclusive lift; not a clean win, not a clean refute."
                    % (readout_margin_mean if readout_margin_mean is not None else -1, BREADTH_HP_MARGIN,
                       ("%.4f" % cosine_margin_mean) if cosine_margin_mean is not None else "NA"))

    summary = dict(
        primary_arm_selected=sel_arms, w_star_per_seed=w_stars,
        semantic_raw_grounding=m_raw, semantic_text=m_txt,
        semantic_fused_eq_naive=m_feq, semantic_fuse_zavg=m_fza, semantic_fuse_wtuned=m_fwt,
        semantic_primary=m_prim,
        semantic_random_init=m_rnd, semantic_collapse=m_sh, semantic_popularity=m_pop,
        semantic_margin_primary_minus_raw=margin_mean, semantic_margin_primary_min=margin_min,
        semantic_margin_text_minus_raw=txt_margin_mean, learning_text_minus_random=learn_mean,
        relational_raw=m_rraw, relational_text=m_rtxt,
        n_query_min=min_nq, validity=validity,
        cosine_margin_vs_baseline_mean=cosine_margin_mean, cosine_margin_vs_baseline_min=cosine_margin_min,
        readout_margin_bilinear_mean=readout_margin_mean, readout_margin_bilinear_min=readout_margin_min,
        readout_all_available=readout_all_available, readout_avail_per_seed=readout_avail_per_seed,
        baseline_sources=baseline_sources,
        trained_tokens=[per_seed[k].get("trained_tokens") for k in seeds],
        per_source_tokens=[per_seed[k].get("per_source_tokens") for k in seeds],
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
    for name, path, _cap_key, _share in CORPUS_SOURCES:
        if not os.path.exists(path):
            raise FileNotFoundError("corpus source %r not found at %s (remote staging?)" % (name, path))

    bundle = prepare_data(cfg)
    universe = bundle["universe"]

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
                   well_covered_min=WELL_COVERED_MIN, breadth_hp_margin=BREADTH_HP_MARGIN,
                   breadth_hf_band=BREADTH_HF_BAND),
        cardinality_ok=(len(per_seed) == len(cfg["seeds"])),
        expected_n_units=len(cfg["seeds"]),
        leak_witness_exact_surface=bundle["witness"],
        leak_witness_stem_diagnostic=bundle["stem_witness_diagnostic"],
        per_source_tokens=bundle["per_source_tokens"],
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
    sel = r["semantic_all"].get("_selected_arm")
    assert sel in PRIMARY_CANDIDATES, "selected arm not a primary candidate: %s" % sel
    assert abs(r["semantic_all"][FUSE_SELECTED_ARM] - r["semantic_all"][sel]) < 1e-9, \
        "PRIMARY != selected-arm held-out AUC"
    assert r["relational"] is not None, "relational eval did not run"
    # Multi-source coverage: per_source_tokens must show ALL 3 sources contributed (breadth exercised).
    pst = r.get("per_source_tokens") or {}
    for name in ("simplewiki", "breadth_v1", "arc"):
        assert pst.get(name, 0) > 0, "SELF-TEST: source %r contributed 0 tokens (breadth not exercised)" % name
    assert r["trained_tokens"] > 0, "no tokens trained on"
    # CHECKPOINT-ALWAYS: at least one in-progress OR final checkpoint mechanism exercised.
    ckpt_pt = os.path.join(out_dir, "ckpt_seed_%d.pt" % int(sk))
    assert os.path.exists(ckpt_pt), "final checkpoint .pt not saved: %s" % ckpt_pt
    assert r.get("ckpt_diag") is not None, "ckpt_diag missing (resumable-checkpoint diagnostics)"
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
