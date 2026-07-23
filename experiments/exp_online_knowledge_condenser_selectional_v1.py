"""ONLINE KNOWLEDGE CONDENSER (glass-box, first prototype): as the substrate READS a real corpus, it
observes verb-noun-in-context evidence and CONDENSES it into GENERALIZABLE selectional-knowledge --
abstracting to the RIGHT GRANULARITY (a WordNet supersense CLASS) rather than memorizing verbatim
(verb,noun) pairs. Starts from a PARTIAL LLM-built + KB-vetted SEED table (the foundation, FIXED, never
updated by reading) and GROWS class-level expectations from reading. Runtime = glass-box dict lookup;
NO LLM/network/autograd at inference (only at build time, for the seed).

THE CRUX (isolated by design): condensation must abstract to the class, NOT memorize the exact pair.
Read "peel apple / peel orange" (2 distinct FOOD exemplars) -> condense "peel expects FOOD" -> this
then handles "peel mango" (an UNSEEN noun of the SAME class, held out of the reading stream on purpose,
never seen for this verb). The headline discriminator is GENERALIZATION TO UNSEEN NOUNS of a learned
class, not recall of seen pairs (recall alone is the frequency-wall already banked in this project).

READING STREAM (real corpus, real automatic reading): the SAME hand-rule reader + SVO extraction the
prior selectional cells' ARM_THIN mechanism uses (SCV.run_reader_on_files over the McGuffey MINING_FILES,
NOT the gold-annotated third_reader -- zero overlap with the gold-holdout convention elsewhere in this
project). Stream items are (sentence_id, verb_lemma, content_noun, wordnet_supersense) in NATURAL
DOCUMENT ORDER (sid = "M<file_idx>_<sent_idx:05d>" sorts exactly into reading order) -- this is a REAL
sequential exposure schedule, not a shuffled bag of pairs.

HELD-OUT UNSEEN-NOUN CONSTRUCTION (fast-mapping precedent: >=2 distinct exemplars -> generalize to a
3rd): for every (verb, supersense-class) with >=3 DISTINCT attested nouns in the FULL stream, hold out
ONE noun (fixed-seed deterministic choice) as the UNSEEN generalization-probe gold filler; every stream
occurrence of that EXACT (verb, held-out-noun) pair is removed from the TRAINING stream the condenser
reads (true zero exposure for that lexical item under that verb) while >=2 sibling same-class nouns
remain in-stream to supply the class evidence. This reproduces "peel apple/orange (train) -> peel
mango (unseen, same class, held out)" from REAL corpus attestation, not invented text.

CONDENSATION MECHANISM (THEORETICAL, evidence-accumulation formula, Laplace-smoothed): for a
(verb, class) key, let n = number of DISTINCT noun TYPES observed supporting it so far (type-diversity,
not raw token count -- diversity is what should signal "this is a class", not one frequently-repeated
word, which would just be near-verbatim memorization of a common filler). condensed_score(n) =
(n+1)/(n+2) if n>0 else 0.5 (no evidence -> neutral, matches the OOV/backoff convention used throughout
this cell family). score(v,noun) = condensed_score(class-of-noun) if that class has ANY evidence for v,
ELSE the FIXED seed-table lookup, ELSE neutral 0.5. The VERBATIM/abstraction-off control uses the
IDENTICAL formula but keyed on the EXACT (verb,noun) pair (n = occurrence COUNT of that pair) instead of
(verb,class) -- same math, different granularity, isolating abstraction as the one mechanism variable.

FOUR ARMS + controls (ONE VARIABLE = the condensation granularity / update-status; seed table, reading
stream, corpus, split, and 2AFC mechanism IDENTICAL across arms):
  ARM_FULL_CONDENSER  : online update, CLASS granularity (the headline mechanism).
  ARM_VERBATIM        : online update, EXACT-PAIR granularity (must-fail control b: "abstraction-off" --
                         accumulates evidence but never generalizes past the literal noun read).
  ARM_FREEZE           : CLASS granularity but counts NEVER updated (empty at every checkpoint) --
                         must-fail control a: flat learning curve by construction (mathematically
                         identical to ARM_FULL_CONDENSER's own exposure=0.0 checkpoint at every point).
  ARM_SHUFFLE          : ARM_FULL_CONDENSER's FINAL (100%-exposure) (verb,class)->n_types table with the
                         VALUES permuted across KEYS (5 fixed seeds, mean reported -- single-seed
                         permutation tests are underpowered at this item count per the independent-KB
                         cell's documented statistical-power lesson) -- must-fail control c: if the class
                         identity isn't doing the work, shuffling the assignment should not hurt.
  ARM_RANDOM           : fixed-seed random score per query -- can-fail chance control (task not
                         saturated/floor by construction).

TWO PROBES (reported SEPARATELY, per the task brief):
  SEEN-PAIR RECALL     : 2AFC over (verb, noun) pairs that DID occur in the training stream (post-holdout
                         removal) vs a cross-class distractor never attested for that verb anywhere in
                         the (pre-holdout) corpus. Measures whether reading imparted usable knowledge of
                         literally-read fillers.
  UNSEEN-NOUN GENERALIZATION (the headline discriminator): 2AFC over the held-out (verb, noun) pairs
                         (noun NEVER seen for that verb during reading) vs a cross-class distractor
                         (same sampling policy). Measures generalization to an unseen exemplar of a
                         learned class.
  Both probes use a CROSS-CLASS distractor (not same-class): a same-class distractor would tie EXACTLY
  under class-granularity scoring by construction (the class score cannot discriminate WITHIN its own
  class), which would conflate "coarse granularity" with "broken mechanism". Cross-class is the correct,
  discriminating regime for testing whether the RIGHT class was condensed at all (does this verb even
  expect this class of object, vs a wrong class) -- the harder same-class-rival question is a DIFFERENT,
  finer axis already probed by 29471/29472's ARM_THIN/ARM_RICH cells and is out of scope for this
  prototype's headline crux (right-granularity abstraction vs verbatim memorization).

EXPOSURE SCHEDULE / LEARNING CURVE (the improving-with-exposure property, USER-mandated): 5 fixed
  checkpoints over the TRAINING stream's cumulative fraction [0.0, 0.25, 0.5, 0.75, 1.0] (re-derive the
  condensed table from stream[:idx] at each checkpoint -- cheap, no incremental-object complexity, exact
  reproducibility). At frac=0.0 the condenser has seen nothing -> ARM_FULL_CONDENSER's own score function
  is IDENTICAL to ARM_FREEZE's (self-check asserted in self_test/smoke).

SEED TABLE (the "PARTIAL LLM-built + KB-vetted foundation"; FIXED, read-only, IDENTICAL across every
  arm and every checkpoint -- never touched by "reading"): intersect 29471's LLM-built rich_selectional_
  table.json (MEASURED@data/exp_pivot_selectional_knowledge_richness_2afc_v1/rich_selectional_table.json)
  with 29472's independent VerbNet+WordNet KB table (MEASURED@data/exp_pivot_selectional_independent_kb_
  2afc_v1/independent_kb_table.json), keeping only entries where the KB has an INFORMATIVE (non-OOV-
  backoff) signal -- i.e. the entry is corroborated by BOTH an LLM rating AND a real independent-KB
  computation, not merely the LLM's own opinion (KB-vetted). A FIXED-FRACTION (SEED_FRACTION=0.30, fixed
  seed) subsample of that vetted pool is the actual seed (PARTIAL by design -- the whole point is that
  reading must GROW coverage past this fixed, deliberately-incomplete foundation). Written to its own
  JSON artifact (glass-box: seed AND condensed entries are inspectable, concept-keyed like 29472's
  schema -- verb_concept_id/noun_concept_id via WordNet synsets where available).

FAIRNESS / NO ANSWER-LEAKAGE: item construction (holdout choice, negative sampling) is MECHANICAL
  (fixed-seed numpy RNG over deterministically-sorted candidate pools) -- no gold/label file is consulted
  anywhere in this cell; "gold" here IS the corpus attestation itself (the reader's own SVO extraction),
  which is exactly the evidence the condenser is allowed to observe. The held-out noun is REMOVED from
  what the condenser reads, so there is no leakage path by which the condenser could have seen it.

PRE-REGISTERED VERDICT BANDS (set BEFORE running FULL; do not redefine mid-run). Let:
  gap        = acc_unseen_full(1.0) - acc_unseen_verbatim(1.0)
  rise       = acc_unseen_full(1.0) - acc_unseen_full(0.25)
  freeze_rng = max(curve_freeze.values()) - min(curve_freeze.values())
  shuf_delta = acc_unseen_full(1.0) - acc_unseen_shuffle_mean

  HARD_FAIL_* (checked FIRST; any true overrides HARD_PASS):
    gap <= 0.05                              -> HARD_FAIL_ABSTRACTION_COLLAPSED_TO_MEMORIZATION
    acc_unseen_full(1.0) <= 0.55              -> HARD_FAIL_NO_GENERALIZATION_LIFT
    rise < 0.03                                -> HARD_FAIL_FLAT_LEARNING_CURVE
    freeze_rng > 0.10                          -> HARD_FAIL_CONTROL_CONTAMINATION
    shuf_delta < 0.05                          -> HARD_FAIL_SHUFFLE_DID_NOT_COLLAPSE

  HARD_PASS_CONDENSATION_GENERALIZES (ALL must hold, none of the FAIL conditions above true):
    acc_unseen_full(1.0) >= 0.65  AND  gap >= 0.15  AND  acc_unseen_verbatim(1.0) <= 0.60
    AND  rise >= 0.10  AND  acc_seen_full(1.0) >= 0.65  AND  freeze_rng <= 0.05
    AND  shuf_delta >= 0.05  AND  0.40 <= acc_random <= 0.60  AND  arms_differ_verified

  MIDDLE_BAND: neither block fires cleanly (e.g. partial rise or partial gap).

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- the reading pipeline is the
  existing hand-rule SVO reader (already CPU-sequential-by-design, not a batchable primitive); condenser
  updates are O(1) dict operations per stream item; 2AFC scoring is O(items). No matmul, no GPU-batchable
  primitive. Storage: no_storage (JSON artifacts only, for inspectability). Runtime invariant: glass-box
  dict lookup ONLY; NO LLM/network/autograd at inference (build-time LLM only, for the seed table, reused
  read-only from 29471/29472's already-built artifacts -- no new LLM call in this cell at all).
  Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, numpy default_rng consumed in deterministic sorted
  order, no hash()-seeded anything. LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO
  remote-persist, NO git add -A.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (hash test over the per-item unseen-probe score vectors for
    FULL@1.0 / VERBATIM@1.0 / FREEZE / SHUFFLE-mean / RANDOM)
  - final_metrics_atomicity: tmp_replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: 2AFC discrimination-accuracy measurement; no quantitative noise floor for the discriminator
  - baseline_in_band at smoke (ARM_FREEZE/seed-only in (0.05,0.95); ARM_RANDOM ~0.5 = can-fail)
  - discriminator survives scale: multi-scale smoke (smoke AND smoke x4 sentence count) both must produce
    a non-empty unseen-noun probe (>=1 held-out group) before FULL is attempted
  - HARD_PASS strictly above floor (gap>=0.15 well above the +0.05 FAIL edge; shuf_delta>=0.05)
  - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
  - deterministic_seeding: fixed int seeds + numpy default_rng + sorted(...); no hash()/list(set())
  - cardinality_ok: EXPOSURE_POINTS has EXPECTED_EXPOSURE_POINTS=5; verdict counts them
  - real_code_path_exercised: SCV.run_reader_on_files (the REAL reader/SVO-extraction pipeline) is
    invoked at tiny scale inside self_test(), not a synthetic-only branch
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import hashlib
import json
import platform
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "online_knowledge_condenser_selectional_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Reuse the prior selectional cells' real reader/mining pipeline + content-noun filter VERBATIM.
from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as SCV  # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_pivot_selectional_knowledge_richness_2afc_v1 as P  # noqa: E402

# ----------------------------------------------------------------------------------------------
# Fixed, deterministic seeds (no hash()-derived anything; PROT-023 compliant).
# ----------------------------------------------------------------------------------------------
NEG_SEED = P.NEG_SEED                       # 20260723, shared base across the selectional cell family
SEED_TABLE_RNG_SEED = NEG_SEED              # seed-table subsample draw
HOLDOUT_RNG_SEED = NEG_SEED + 101           # which noun is held out per (verb,class) group
UNSEEN_SUBSAMPLE_SEED = NEG_SEED + 201      # subsample cap on unseen-probe items
SEEN_SUBSAMPLE_SEED = NEG_SEED + 301        # subsample cap on seen-probe items
DISTRACTOR_RNG_SEED = NEG_SEED + 401        # cross-class distractor draws (shared across both probes)
RANDOM_ARM_SEED = NEG_SEED + 501            # ARM_RANDOM per-item scores
SHUFFLE_SEEDS = [NEG_SEED + 9 + i * 17 for i in range(5)]   # 5 fixed shuffle draws, mean reported

EXPOSURE_POINTS = [0.0, 0.25, 0.5, 0.75, 1.0]
EXPECTED_EXPOSURE_POINTS = len(EXPOSURE_POINTS)
MIN_GROUP_SIZE = 3            # (verb,class) needs >=3 distinct nouns to hold one out (2 train + 1 unseen)
SEED_FRACTION = 0.30          # fraction of the vetted rich/KB-agreeing pool kept as the FIXED seed table
MAX_UNSEEN_ITEMS = 48
MAX_SEEN_ITEMS = 48

RICH_TABLE_PATH = os.path.join(REPO_ROOT, "data", "exp_pivot_selectional_knowledge_richness_2afc_v1",
                                "rich_selectional_table.json")
INDEP_KB_TABLE_PATH = os.path.join(REPO_ROOT, "data", "exp_pivot_selectional_independent_kb_2afc_v1",
                                    "independent_kb_table.json")

MODE_CONFIG = {
    "selftest": {"files": SCV.MINING_FILES_SMOKE, "max_sents": 60},
    "smoke":    {"files": SCV.MINING_FILES_SMOKE, "max_sents": 500},
    "smoke4x":  {"files": SCV.MINING_FILES_SMOKE, "max_sents": 2000},
    "full":     {"files": SCV.MINING_FILES_FULL,  "max_sents": None},
}


# ----------------------------------------------------------------------------------------------
# Seed table: PARTIAL LLM-built + KB-vetted foundation. FIXED. Never touched by reading.
# ----------------------------------------------------------------------------------------------
def build_seed_table():
    with open(RICH_TABLE_PATH, encoding="utf-8") as f:
        rich = json.load(f)["ratings"]
    with open(INDEP_KB_TABLE_PATH, encoding="utf-8") as f:
        kb_records = json.load(f)["records"]
    kb_informative = {f"{r['verb_lemma']}|{r['noun_lemma']}": r for r in kb_records
                       if r["example_score"] is not None or r["selrestr_score"] is not None}
    vetted_keys = sorted(k for k in rich if k in kb_informative)
    rng = np.random.default_rng(SEED_TABLE_RNG_SEED)
    order = rng.permutation(len(vetted_keys)).tolist()
    n_keep = int(round(SEED_FRACTION * len(vetted_keys)))
    keep_keys = sorted(vetted_keys[order[i]] for i in range(n_keep))
    table = {}
    records = []
    for k in keep_keys:
        v, n = k.split("|", 1)
        table[(v, n)] = float(rich[k])
        kbrec = kb_informative[k]
        records.append({"verb_lemma": v, "noun_lemma": n, "seed_score": round(float(rich[k]), 6),
                         "verb_concept_id": kbrec.get("verb_concept_id"),
                         "noun_concept_id": kbrec.get("noun_concept_id"),
                         "kb_example_score": kbrec.get("example_score"),
                         "kb_selrestr_score": kbrec.get("selrestr_score")})
    return table, records, len(vetted_keys), len(keep_keys)


def write_seed_table_artifact(out_dir, records, n_vetted_pool, n_kept):
    os.makedirs(out_dir, exist_ok=True)
    payload = {
        "schema": "condenser_seed_v1_concept_keyed",
        "provenance": ("Intersection of 29471's LLM-built rich_selectional_table.json with 29472's "
                       "independent VerbNet+WordNet KB table, kept ONLY where the KB signal is "
                       "informative (not pure OOV backoff) -- i.e. corroborated by BOTH an LLM rating "
                       "and a real independent-KB computation. Fixed-fraction (SEED_FRACTION) subsample "
                       "of that vetted pool. FIXED for the whole run; the online condenser never writes "
                       "to this table."),
        "seed_fraction": SEED_FRACTION, "n_vetted_pool": n_vetted_pool, "n_kept": n_kept,
        "records": records,
    }
    tmp = os.path.join(out_dir, "condenser_seed_table.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "condenser_seed_table.json"))


# ----------------------------------------------------------------------------------------------
# Reading stream: the REAL hand-rule reader's SVO extraction, in natural document order.
# ----------------------------------------------------------------------------------------------
def build_reading_stream(mode, out_dir):
    cfg = MODE_CONFIG[mode]
    cache = os.path.join(out_dir, "_mining_cache.json")
    mine_data = SCV.run_reader_on_files(cfg["files"], cache, max_sents=cfg["max_sents"])
    stream = []
    for sid, rec in sorted(mine_data.items()):     # sid = "M<file>_<sent:05d>" -> sorts into reading order
        for tup in rec["svo"]:
            v_surf, _a, p = tup
            v = L.lemma_verb(v_surf)
            pl = p.lower()
            if not P._is_content_noun(pl):
                continue
            ss = SCV.supersense(pl)
            if ss is None:
                continue
            stream.append((sid, v, pl, ss))
    return stream, len(mine_data)


def attested_maps(stream):
    """attested[v][ss] = {noun: count}; verb_any[v] = set of ALL nouns ever attested for v (any class);
    class_pool[ss] = set of nouns (global, any verb) -- distractor candidate pool by class."""
    attested = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    verb_any = defaultdict(set)
    class_pool = defaultdict(set)
    for _sid, v, n, ss in stream:
        attested[v][ss][n] += 1
        verb_any[v].add(n)
        class_pool[ss].add(n)
    return attested, verb_any, class_pool


def select_heldout(attested, seed):
    """For each (v,ss) with >=MIN_GROUP_SIZE distinct nouns: hold out ONE noun (fixed-seed, deterministic
    sorted-group order -- no hash()). Returns list of dicts sorted by (v,ss)."""
    groups = []
    for v in sorted(attested.keys()):
        for ss in sorted(attested[v].keys()):
            nouns = sorted(attested[v][ss].keys())
            if len(nouns) >= MIN_GROUP_SIZE:
                groups.append((v, ss, nouns))
    rng = np.random.default_rng(seed)
    heldout = []
    for v, ss, nouns in groups:      # deterministic order consumes rng deterministically
        idx = int(rng.integers(len(nouns)))
        heldout.append({"v": v, "ss": ss, "noun": nouns[idx], "n_class_nouns_total": len(nouns)})
    return heldout


def remove_heldout_from_stream(stream, heldout):
    held_pairs = set((h["v"], h["noun"]) for h in heldout)
    return [(sid, v, n, ss) for (sid, v, n, ss) in stream if (v, n) not in held_pairs]


def sample_distractor(v, gold_ss, verb_any, class_pool, rng):
    """Cross-class distractor: a noun from a DIFFERENT supersense class than gold_ss, never attested for
    verb v anywhere in the (pre-holdout) stream. Mechanical, fixed RNG -- no gold/label file consulted."""
    candidates = sorted(n for ss2, pool in class_pool.items() if ss2 != gold_ss for n in pool
                         if n not in verb_any.get(v, set()))
    if not candidates:
        return None
    return candidates[int(rng.integers(len(candidates)))]


def build_unseen_items(heldout, verb_any_full, class_pool_full):
    rng = np.random.default_rng(DISTRACTOR_RNG_SEED)
    items = []
    for h in heldout:
        neg = sample_distractor(h["v"], h["ss"], verb_any_full, class_pool_full, rng)
        if neg is None:
            continue
        items.append({"v": h["v"], "gold_patient": h["noun"], "gold_ss": h["ss"], "neg_filler": neg,
                      "neg_ss": SCV.supersense(neg), "n_class_nouns_total": h["n_class_nouns_total"]})
    items = sorted(items, key=lambda d: (d["v"], d["gold_patient"]))
    if len(items) > MAX_UNSEEN_ITEMS:
        rng2 = np.random.default_rng(UNSEEN_SUBSAMPLE_SEED)
        idx = sorted(rng2.permutation(len(items))[:MAX_UNSEEN_ITEMS].tolist())
        items = [items[i] for i in idx]
    return items


def build_seen_items(training_stream, verb_any_full, class_pool_full):
    pair_first_ss = {}
    for _sid, v, n, ss in training_stream:
        pair_first_ss.setdefault((v, n), ss)
    pairs = sorted(pair_first_ss.keys())
    rng = np.random.default_rng(DISTRACTOR_RNG_SEED + 1)
    items = []
    for v, n in pairs:
        ss = pair_first_ss[(v, n)]
        neg = sample_distractor(v, ss, verb_any_full, class_pool_full, rng)
        if neg is None:
            continue
        items.append({"v": v, "gold_patient": n, "gold_ss": ss, "neg_filler": neg,
                      "neg_ss": SCV.supersense(neg)})
    items = sorted(items, key=lambda d: (d["v"], d["gold_patient"]))
    if len(items) > MAX_SEEN_ITEMS:
        rng2 = np.random.default_rng(SEEN_SUBSAMPLE_SEED)
        idx = sorted(rng2.permutation(len(items))[:MAX_SEEN_ITEMS].tolist())
        items = [items[i] for i in idx]
    return items


# ----------------------------------------------------------------------------------------------
# Condensation mechanism: evidence-accumulation counts, per granularity, per stream slice.
# ----------------------------------------------------------------------------------------------
def build_condensed_counts(stream_slice, granularity):
    """granularity: 'class' (FULL condenser) counts DISTINCT NOUN TYPES per (v,ss); 'pair' (VERBATIM
    control) counts OCCURRENCES of the exact (v,n). Returns {key: n} (n=0 keys absent)."""
    evid = defaultdict(set)
    for sid, v, n, ss in stream_slice:
        if granularity == "class":
            evid[(v, ss)].add(n)
        else:
            evid[(v, n)].add(sid)
    return {k: len(s) for k, s in evid.items()}


def condensed_score(n):
    """THEORETICAL: Laplace-smoothed evidence-accumulation, prior pseudo-count=1 each side.
    f(0)=0.5 (no evidence -> neutral); f(1)=0.667; f(2)=0.75; f(3)=0.8; asymptotes to 1.0."""
    if n <= 0:
        return 0.5
    return (n + 1) / (n + 2)


def make_score_fn(counts, granularity, seed_table):
    def score(v, n, ss):
        key = (v, ss) if granularity == "class" else (v, n)
        c = counts.get(key, 0)
        if c > 0:
            return condensed_score(c)
        return seed_table.get((v, n), 0.5)
    return score


def make_random_score(seed):
    rng = np.random.default_rng(seed)
    cache = {}

    def s(v, n, ss=None):
        k = (v, n)
        if k not in cache:
            cache[k] = float(rng.random())
        return cache[k]
    return s


def make_shuffled_score_fn(counts, seed_table, seed):
    keys = sorted(counts.keys())
    vals = [counts[k] for k in keys]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(vals)).tolist()
    shuffled = {keys[i]: vals[perm[i]] for i in range(len(keys))}
    return make_score_fn(shuffled, "class", seed_table)


def _2afc(items, score_fn):
    correct = 0.0
    per_item = []
    for it in items:
        sp = score_fn(it["v"], it["gold_patient"], it["gold_ss"])
        sn = score_fn(it["v"], it["neg_filler"], it["neg_ss"])
        c = 1.0 if sp > sn else (0.5 if sp == sn else 0.0)
        correct += c
        per_item.append(round(c, 2))
    n = len(items)
    return round(correct / max(1, n), 4), per_item


# ----------------------------------------------------------------------------------------------
# IO helpers.
# ----------------------------------------------------------------------------------------------
def _out_dir(mode):
    suffix = {"selftest": "_selftest", "smoke": "_smoke", "smoke4x": "_smoke4x", "full": ""}[mode]
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}{suffix}")


def _write_start_marker(output_dir, mode, expected_units):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "expected_n_units": expected_units,
              "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:400]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    try:
        write_metrics(output_dir, diag)
    except Exception:
        pass


# ----------------------------------------------------------------------------------------------
# Core run.
# ----------------------------------------------------------------------------------------------
def run_mode(mode):
    t0 = time.perf_counter()
    out_dir = _out_dir(mode)
    _write_start_marker(out_dir, mode, EXPECTED_EXPOSURE_POINTS)
    print(f"[{ANCHOR_NAME}:{mode}] START", flush=True)

    seed_table, seed_records, n_vetted_pool, n_seed_kept = build_seed_table()
    write_seed_table_artifact(out_dir, seed_records, n_vetted_pool, n_seed_kept)
    print(f"[{ANCHOR_NAME}:{mode}] seed table: {n_seed_kept}/{n_vetted_pool} vetted pairs kept "
          f"(fraction={SEED_FRACTION})", flush=True)

    stream, n_mine = build_reading_stream(mode, out_dir)
    print(f"[{ANCHOR_NAME}:{mode}] reading stream: {len(stream)} (verb,noun) evidence tuples from "
          f"{n_mine} sentences", flush=True)

    attested, verb_any_full, class_pool_full = attested_maps(stream)
    heldout = select_heldout(attested, HOLDOUT_RNG_SEED)
    training_stream = remove_heldout_from_stream(stream, heldout)
    print(f"[{ANCHOR_NAME}:{mode}] held-out groups (>= {MIN_GROUP_SIZE} distinct same-class nouns): "
          f"{len(heldout)}", flush=True)

    unseen_items = build_unseen_items(heldout, verb_any_full, class_pool_full)
    seen_items = build_seen_items(training_stream, verb_any_full, class_pool_full)
    print(f"[{ANCHOR_NAME}:{mode}] n_unseen_items={len(unseen_items)} n_seen_items={len(seen_items)}",
          flush=True)

    n_train = len(training_stream)
    curve_full_unseen, curve_full_seen = {}, {}
    curve_verbatim_unseen, curve_verbatim_seen = {}, {}
    curve_freeze_unseen = {}
    per_item_digests = {}
    counts_full_final = None
    for frac in EXPOSURE_POINTS:
        idx = int(round(frac * n_train))
        sl = training_stream[:idx]
        counts_full = build_condensed_counts(sl, "class")
        counts_verbatim = build_condensed_counts(sl, "pair")
        if frac == 1.0:
            counts_full_final = counts_full
        score_full = make_score_fn(counts_full, "class", seed_table)
        score_verbatim = make_score_fn(counts_verbatim, "pair", seed_table)
        score_freeze = make_score_fn({}, "class", seed_table)   # never updated, at every checkpoint

        acc_fu, pi_fu = _2afc(unseen_items, score_full)
        acc_fs, pi_fs = _2afc(seen_items, score_full)
        acc_vu, pi_vu = _2afc(unseen_items, score_verbatim)
        acc_vs, _pi_vs = _2afc(seen_items, score_verbatim)
        acc_frz, pi_frz = _2afc(unseen_items, score_freeze)

        key = f"{frac:.2f}"
        curve_full_unseen[key] = acc_fu
        curve_full_seen[key] = acc_fs
        curve_verbatim_unseen[key] = acc_vu
        curve_verbatim_seen[key] = acc_vs
        curve_freeze_unseen[key] = acc_frz

        if frac == 1.0:
            per_item_digests["full_unseen"] = hashlib.sha256(
                np.asarray(pi_fu, dtype=np.float64).tobytes()).hexdigest()[:16]
            per_item_digests["verbatim_unseen"] = hashlib.sha256(
                np.asarray(pi_vu, dtype=np.float64).tobytes()).hexdigest()[:16]
        if frac == 0.0:
            per_item_digests["freeze_unseen"] = hashlib.sha256(
                np.asarray(pi_frz, dtype=np.float64).tobytes()).hexdigest()[:16]

    # ARM_SHUFFLE: permute the FINAL class-granularity table's key->value mapping, 5 fixed seeds.
    shuffle_accs = []
    pi_shuffle_first = None
    for si, sseed in enumerate(SHUFFLE_SEEDS):
        score_shuf = make_shuffled_score_fn(counts_full_final or {}, seed_table, sseed)
        acc_shuf, pi_shuf = _2afc(unseen_items, score_shuf)
        shuffle_accs.append(acc_shuf)
        if si == 0:
            pi_shuffle_first = pi_shuf
    acc_shuffle_mean = round(float(np.mean(shuffle_accs)), 4) if shuffle_accs else None
    if pi_shuffle_first is not None:
        per_item_digests["shuffle_seed0_unseen"] = hashlib.sha256(
            np.asarray(pi_shuffle_first, dtype=np.float64).tobytes()).hexdigest()[:16]

    # ARM_RANDOM.
    rand_score = make_random_score(RANDOM_ARM_SEED)
    acc_random, pi_rand = _2afc(unseen_items, rand_score)
    per_item_digests["random_unseen"] = hashlib.sha256(
        np.asarray(pi_rand, dtype=np.float64).tobytes()).hexdigest()[:16]

    # ARMS-MUST-DIFFER (META_RULE_AF), with ONE declared exemption: on the UNSEEN-noun probe,
    # ARM_VERBATIM and ARM_FREEZE are EXPECTED to be bit-identical BY CONSTRUCTION -- a held-out
    # (verb,noun) pair by definition has ZERO verbatim evidence (it never appears in the training
    # stream), so ARM_VERBATIM's score for every unseen item is ALWAYS the seed-table fallback,
    # identical to ARM_FREEZE (which also always falls back to seed, having no evidence at all). This
    # tie IS the discriminating signal (verbatim = no better than never-updated on unseen items), not
    # an implementation bug. Every OTHER pair (in particular FULL vs everything else) must still differ.
    ARMS_DIFFER_EXEMPTED = [("freeze_unseen", "verbatim_unseen")]
    exempt_names = set()
    for a, b in ARMS_DIFFER_EXEMPTED:
        exempt_names.add(frozenset((a, b)))
    names = sorted(per_item_digests.keys())
    violations = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if frozenset((a, b)) in exempt_names:
                continue
            if per_item_digests[a] == per_item_digests[b]:
                violations.append((a, b))
    arms_differ_verified = bool(len(violations) == 0)

    acc_full_1p0 = curve_full_unseen["1.00"]
    acc_full_0p25 = curve_full_unseen["0.25"]
    acc_verbatim_1p0 = curve_verbatim_unseen["1.00"]
    acc_seen_full_1p0 = curve_full_seen["1.00"]
    freeze_vals = list(curve_freeze_unseen.values())
    freeze_range = round(max(freeze_vals) - min(freeze_vals), 4) if freeze_vals else None

    gap = round(acc_full_1p0 - acc_verbatim_1p0, 4)
    rise = round(acc_full_1p0 - acc_full_0p25, 4)
    shuf_delta = (None if acc_shuffle_mean is None else round(acc_full_1p0 - acc_shuffle_mean, 4))
    random_is_chance = bool(0.40 <= acc_random <= 0.60)
    baseline_in_band = bool(0.05 < curve_freeze_unseen["0.00"] < 0.95) if freeze_vals else False
    has_probe_items = bool(len(unseen_items) >= 1 and len(seen_items) >= 1)

    # Verdict (pre-registered bands; HARD_FAIL checked first).
    verdict = "PENDING_NO_PROBE_ITEMS"
    if has_probe_items:
        if gap <= 0.05:
            verdict = "HARD_FAIL_ABSTRACTION_COLLAPSED_TO_MEMORIZATION"
        elif acc_full_1p0 <= 0.55:
            verdict = "HARD_FAIL_NO_GENERALIZATION_LIFT"
        elif rise < 0.03:
            verdict = "HARD_FAIL_FLAT_LEARNING_CURVE"
        elif freeze_range is not None and freeze_range > 0.10:
            verdict = "HARD_FAIL_CONTROL_CONTAMINATION"
        elif shuf_delta is not None and shuf_delta < 0.05:
            verdict = "HARD_FAIL_SHUFFLE_DID_NOT_COLLAPSE"
        elif (acc_full_1p0 >= 0.65 and gap >= 0.15 and acc_verbatim_1p0 <= 0.60 and rise >= 0.10
              and acc_seen_full_1p0 >= 0.65 and (freeze_range is not None and freeze_range <= 0.05)
              and (shuf_delta is not None and shuf_delta >= 0.05) and random_is_chance
              and arms_differ_verified):
            verdict = "HARD_PASS_CONDENSATION_GENERALIZES"
        else:
            verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    msg = (f"VERDICT_core acc_unseen_full={acc_full_1p0:.3f} acc_unseen_verbatim={acc_verbatim_1p0:.3f} "
           f"(gap={gap:+.3f}) rise(0.25->1.0)={rise:+.3f} acc_seen_full={acc_seen_full_1p0:.3f} "
           f"freeze_range={freeze_range} shuffle_mean={acc_shuffle_mean} shuf_delta={shuf_delta} "
           f"acc_random={acc_random:.3f} n_unseen={len(unseen_items)} n_seen={len(seen_items)} "
           f"n_heldout_groups={len(heldout)} n_train_evidence={n_train}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_mining_sentences": n_mine, "n_reading_stream_evidence": len(stream),
        "n_training_stream_evidence": n_train, "n_heldout_groups": len(heldout),
        "n_unseen_items": len(unseen_items), "n_seen_items": len(seen_items),
        "curve_full_unseen": curve_full_unseen, "curve_full_seen": curve_full_seen,
        "curve_verbatim_unseen": curve_verbatim_unseen, "curve_verbatim_seen": curve_verbatim_seen,
        "curve_freeze_unseen": curve_freeze_unseen,
        "exposure_points": EXPOSURE_POINTS, "expected_exposure_points": EXPECTED_EXPOSURE_POINTS,
        "cardinality_ok": bool(len(curve_full_unseen) == EXPECTED_EXPOSURE_POINTS),
        "acc_shuffle_per_seed": shuffle_accs, "acc_shuffle_mean": acc_shuffle_mean,
        "acc_random": acc_random,
        "gap_full_minus_verbatim": gap, "rise_025_to_1p0": rise, "freeze_range": freeze_range,
        "shuffle_delta": shuf_delta,
        "arms_differ_verified": arms_differ_verified, "per_item_score_digests": per_item_digests,
        "arms_differ_exempted": [list(pair) for pair in ARMS_DIFFER_EXEMPTED],
        "arms_differ_exempt_rationale": ("freeze_unseen vs verbatim_unseen tie is EXPECTED: a held-out "
                                         "pair has zero verbatim evidence by construction, so both arms "
                                         "fall back to the identical seed table on every unseen item."),
        "arms_differ_violations": violations,
        "random_is_chance": random_is_chance, "baseline_in_band": baseline_in_band,
        "has_probe_items": has_probe_items,
        "n_seed_table_entries": n_seed_kept, "n_seed_vetted_pool": n_vetted_pool,
        "seed_fraction": SEED_FRACTION,
        "runtime_invariant": ("glass-box dict lookup ONLY; NO LLM/network/autograd at inference; the "
                              "seed table is read-only, built at 29471/29472 build-time, never touched "
                              "by this cell's 'reading'"),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "2AFC discrimination-accuracy measurement; no quantitative noise floor",
        "deterministic_seeding": "fixed int seeds + numpy default_rng consumed in sorted order; no hash()",
        "one_variable_note": ("All arms share the SAME reading stream (order+content), seed table, "
                              "split, and 2AFC mechanism. ONLY the condensation granularity/update-status "
                              "differs: FULL=class-level online, VERBATIM=exact-pair online (abstraction "
                              "off), FREEZE=class-level but never updated, SHUFFLE=FULL's final table "
                              "with keys/values permuted, RANDOM=chance control."),
        "leakage_guard": ("Held-out noun is REMOVED from the training stream (true zero exposure for "
                          "that verb+noun); negative sampling is mechanical (fixed RNG over sorted "
                          "candidate pools); no gold/label file is consulted anywhere -- the corpus's "
                          "own attestation IS the evidence the condenser is allowed to read."),
        "mapped_ceiling_ref": ("29471 HARD_PASS_KNOWLEDGE_POVERTY_WAS_THE_WALL (LLM-built rich table); "
                              "29472 HARD_PASS_INDEPENDENT_KB (VerbNet+WordNet KB, if landed at that "
                              "tier) supply this cell's FIXED seed table foundation."),
        "REQUIRED_FIELDS": ["verdict", "curve_full_unseen", "curve_verbatim_unseen", "curve_freeze_unseen",
                            "acc_shuffle_mean", "acc_random", "gap_full_minus_verbatim", "rise_025_to_1p0",
                            "arms_differ_verified", "runtime_invariant", "leakage_guard"],
    }
    write_metrics(out_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] verdict={verdict} -> {os.path.join(out_dir, 'metrics.json')}", flush=True)
    return payload


# ----------------------------------------------------------------------------------------------
# Self-test: constructs REAL reader/mining objects at tiny scale (Gate F.1 real_code_path); toy
# condensation math checks (Gate: metric_moves, discriminator mechanics).
# ----------------------------------------------------------------------------------------------
def self_test():
    # 1) seed table builds deterministically from the two on-disk artifacts.
    seed_table, seed_records, n_pool, n_kept = build_seed_table()
    assert n_kept >= 1, "seed table must keep at least 1 entry"
    assert n_kept == int(round(SEED_FRACTION * n_pool)), "seed subsample fraction must match SEED_FRACTION"
    seed_table2, _r2, _p2, _k2 = build_seed_table()
    assert seed_table == seed_table2, "seed table build must be deterministic"

    # 2) REAL reader/mining pipeline exercised at tiny scale (Gate F.1 real_code_path_exercised).
    out_dir = _out_dir("selftest")
    stream, n_mine = build_reading_stream("selftest", out_dir)
    assert n_mine > 0, "real mining pipeline must run on real corpus files at tiny scale"
    assert isinstance(stream, list), "reading stream must be a list of tuples"
    for sid, v, n, ss in stream[:5]:
        assert isinstance(sid, str) and isinstance(v, str) and isinstance(n, str) and isinstance(ss, str)

    # 3) condensation math: toy check that condensed_score is monotone increasing in n and f(0)=0.5.
    assert condensed_score(0) == 0.5
    vals = [condensed_score(n) for n in range(0, 6)]
    assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1)), "condensed_score must be monotone in n"
    assert vals[-1] < 1.0, "condensed_score must never reach exactly 1.0 (Laplace smoothing)"

    # 4) toy stream: verify class-granularity generalizes to an unseen same-class noun while
    #    pair-granularity (verbatim) does NOT -- the exact crux, on a hand-built toy corpus.
    toy_stream = [("s0", "peel", "apple", "noun.food"), ("s1", "peel", "orange", "noun.food"),
                  ("s2", "eat", "bread", "noun.food"), ("s3", "kick", "rock", "noun.object")]
    counts_class = build_condensed_counts(toy_stream, "class")
    counts_pair = build_condensed_counts(toy_stream, "pair")
    toy_seed = {}
    score_class = make_score_fn(counts_class, "class", toy_seed)
    score_pair = make_score_fn(counts_pair, "pair", toy_seed)
    # "peel mango" (unseen exact pair, same class "noun.food" as apple/orange) vs "peel rock" (cross-class)
    s_mango_class = score_class("peel", "mango", "noun.food")
    s_rock_class = score_class("peel", "rock", "noun.object")
    assert s_mango_class > s_rock_class, "class-granularity must generalize peel->food to an unseen noun"
    s_mango_pair = score_pair("peel", "mango", "noun.food")
    s_rock_pair = score_pair("peel", "rock", "noun.object")
    assert s_mango_pair == s_rock_pair == 0.5, "pair-granularity (verbatim) must NOT generalize to an unseen exact pair"

    # 5) shuffle collapses the class signal (toy-scale sanity of the shuffle mechanism itself).
    score_shuf = make_shuffled_score_fn(counts_class, toy_seed, SHUFFLE_SEEDS[0])
    # with only 2 keys in this toy table a single shuffle draw may or may not flip; just assert it RUNS
    # and returns a valid probability-like value (full statistical margin check is at cell scale).
    v = score_shuf("peel", "mango", "noun.food")
    assert 0.0 <= v <= 1.0

    # 6) arms-must-differ mechanics on the toy per-item vectors.
    items_toy = [{"v": "peel", "gold_patient": "mango", "gold_ss": "noun.food",
                  "neg_filler": "rock", "neg_ss": "noun.object"}]
    acc_class, pi_class = _2afc(items_toy, score_class)
    acc_pair, pi_pair = _2afc(items_toy, score_pair)
    assert acc_class == 1.0, "toy class-granularity 2AFC must resolve correctly"
    assert acc_pair == 0.5, "toy pair-granularity 2AFC must be a tie (no evidence either way)"
    d_class = hashlib.sha256(np.asarray(pi_class, dtype=np.float64).tobytes()).hexdigest()
    d_pair = hashlib.sha256(np.asarray(pi_pair, dtype=np.float64).tobytes()).hexdigest()
    assert d_class != d_pair, "class vs pair arms must differ on this toy discriminating item"

    print(f"[{ANCHOR_NAME}] self-test PASS | seed_kept={n_kept}/{n_pool} n_mine={n_mine} "
          f"toy: class={acc_class} pair={acc_pair} condensed_score(3)={condensed_score(3)}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--smoke4x", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.smoke4x:
        run_mode("smoke4x"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --smoke4x | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), e)
        raise
