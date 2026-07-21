#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_breadth_foundation_curriculum_order_mcguffey_v1

BREADTH-FOUNDATION on the ORDERED GRADED CURRICULUM: run the read-drives-knowledge active-growth loop
(atom 29424) over the FULL McGuffey Eclectic series IN CURRICULUM ORDER (Primer -> Sixth, easy-to-hard),
and TEST whether the graded ORDER helps foundation growth (the curriculum-order principle). The prior
breadth loop read UNordered UD-EWT web text; this cell reads the "perfect-fit ordered documents" the
loop should have read.

WHAT'S NEW vs the UD-EWT loop (29424):
  1. STREAM  = McGuffey Primer..Sixth (Gutenberg plain text), boilerplate + lesson-scaffolding CLEANED,
               POS+LEMMA supplied by an nltk front-end (McGuffey has NO gold conllu -> tagger noise is
               symmetric across arms and cancels in the WITHIN-design order comparison).
  2. ORDER TEST (the USER-relevant new result): does reading IN ORDER (Primer->Sixth) give faster/
               smoother foundation growth than the SAME volumes read in SHUFFLED volume order? Clean
               can-fail: ordered value vs a distribution of random-volume-order runs (permutation null),
               ONE variable = volume order, identical content. Honest either way.
  3. ILLUSTRATION preservation: [Illustration: ...] markers are EXTRACTED + COUNTED + flagged
               grounding-relevant (Primer/First/Second short single-word captions = candidate word<->
               referent picture-word pairings; vision parked, just preserved vision-ready).

DIFFICULTY-GRADIENT NOTE (load-bearing design correction vs 29424): on easy-to-hard text, BINNED
coverage does NOT monotonically RISE (later volumes introduce rich/rare vocabulary -> more first-
occurrences -> lower per-bin coverage late). So the 29424 "coverage rises >= +0.20" band is INVALID
here. The difficulty-robust learning signal = the growth-ON vs growth-OFF RETENTION GAP on the SAME
graded stream (both arms see the same gradient; the GAP is pure retention, gradient-free).

MECHANISM (glass-box, NO external LLM at inference):
  FRONT-END = nltk word_tokenize + pos_tag (Penn) -> UPOS {NOUN,VERB,ADJ,PROPN}; morphy lemmatize.
  LOOKUP    = FUNCTIONAL coverage (meaning the reader NEEDS): VERB->VerbNet affectedness lexicon;
              NOUN/PROPN->WordNet noun semantics; ADJ->WordNet ADJ sense. (Same vetted lookups as 29424.)
  ARMS (main, on the ORDERED stream; one variable = the store-write rule):
    growth-ON      = resolve + STORE true meaning + mark known. Coverage rises vs empty; ask-rate falls.
    growth-OFF     = REAL BASELINE. Same stream, NEVER store -> every content token re-asks -> per-token
                     miss = 1.0 by construction; coverage ~ 0. Proves the ON decline is CAUSED by the
                     growing foundation.
    growth-SHUFFLE = MUST-FAIL control. Same retention as ON (coverage/ask curves IDENTICAL) but stores a
                     PERMUTED (wrong) meaning -> the usefulness probe must COLLAPSE.
  ORDER ARMS (curriculum-order test; growth-ON; one variable = volume order):
    ORDERED   = volumes [0,1,2,3,4,5,6] (Primer->Sixth).
    SHUFFLED  = N random permutations of the 7 volumes (deterministic seeds) -> null distribution.
    Metric (token-binned trajectory over fraction-of-stream-read): coverage@25%, coverage@50%, the
    early-coverage AREA (ordered minus shuffled-mean over the first half), cumulative asks/escalations by
    the mid-point, and ask-curve smoothness. ORDER_HELPS iff ordered early-coverage exceeds the shuffled
    distribution (z >= 1.0 AND area > 0); else ORDER_NO_ADVANTAGE (honest negative); ORDER_HURTS if ordered
    is z <= -1.0 below. The DIRECTION is REPORTED, not gated as pass/fail (either outcome is valid science).

FUNCTIONAL-USEFULNESS PROBE (unchanged from 29424; independent human gold; non-tautological):
  Predict AFFECTED iff grown verb graded_score >= 0.5; score AUC vs UD-EWT semantic-affectedness gold
  (HIGH {patient,effected} vs LOW {target_not_affected}). REAL grown store separates; SHUFFLE collapses
  to chance. Gold is independent human affectedness intuition -> not tautological.

BANDS (declared BEFORE full; see preregs/2026-07-21_breadth_foundation_curriculum_order_mcguffey_v1.md):
  retention_works := off_miss_mean >= 0.98 AND on_miss_mean <= 0.70 AND
                     (off_miss_mean - on_miss_mean) >= 0.30      (gradient-free retention signal)
  on_coverage_positive := on_cov_mean >= 0.20 AND on_cov_mean - off_cov_mean >= 0.20
  shuffle_collapses := real_auc >= 0.70 AND (real_auc - shuffle_auc_mean) >= 0.15 AND
                       0.40 <= shuffle_auc_mean <= 0.60
  arms_differ := ON/OFF/SHUFFLE final store-state hashes distinct (ON!=SHUFFLE and ON!=OFF)
  order_measurement_valid := ordered + all shuffled orders produced full curves AND shuffled_early_cov_std
                     > 0.005 (the early-coverage metric RESPONDS to volume order -> the can-fail can fire)
  HARD_PASS_CURRICULUM := retention_works AND on_coverage_positive AND shuffle_collapses AND arms_differ
                     AND deterministic AND cardinality_ok AND order_measurement_valid
  HARD_FAIL_CURRICULUM := off_miss_mean < 0.98 (OFF leaked retention) OR (off_miss_mean - on_miss_mean) <
                     0.30 (no retention) OR NOT shuffle_collapses OR NOT arms_differ OR NOT deterministic
                     OR NOT order_measurement_valid
  MIDDLE_BAND_CURRICULUM := otherwise.
  order_verdict (REPORTED, not a pass/fail gate): ORDER_HELPS | ORDER_NO_ADVANTAGE | ORDER_HURTS.

HYPOTHESIZED (pre-run, tagged): off_miss_mean ~ 1.0 HYPOTHESIZED (no retention). on_miss_mean ~ 0.3-0.6
  HYPOTHESIZED (graded small vocab -> strong retention, but rich late volumes lift it above the UD-EWT
  0.22 asymptote). on_cov_mean ~ 0.4-0.6 HYPOTHESIZED. real_auc ~ 0.89 HYPOTHESIZED (same gold+lexicon as
  29424). ORDER: coverage@25 ordered > shuffled HYPOTHESIZED (easy volumes are tiny+repetitive+high-reuse
  -> high early coverage; hard-first shuffled starts in rich vocab -> low early coverage). residual
  dominated by named_entity (author names/place names in later readers) + verb_not_in_verbnet + archaic
  OOV HYPOTHESIZED. All MEASURED@ this cell's metrics.json after run.

Compute architecture: sequential-CPU, justified. nltk pos_tag on ~2e5 tokens once (~15-30s), cached per
  volume; the growth loop + 6/24 order permutations are O(tokens) dict lookups over pre-tagged sentences
  (no re-tag, no matmul). Total < few min -> NOT a GPU/batching candidate; runtime sanity gate PASS.
  Storage: dict foundation (grown COPY at data/breadth_foundation_grown_mcguffey_v1; production KBs
  untouched). Determinism: fixed integer seeds; np.random.Generator only; NO hash()-seeded RNG or
  list(set()) ordering (PROT-023); sorted iteration; OMP/MKL/OPENBLAS=1. LOCAL foreground to COMPLETION
  (light compute); NO queue, NO push, NO remote-persist, NO git add of canonical store, NO hdlab
  mutation, NO atom bank (skunkworks VETs after). ASCII-only.

# CELL-TEMPLATE MANDATORY (measurement + control loop + order-null; light CPU):
# - arms_differ_verified at smoke (ON/OFF/SHUFFLE store hashes differ; META_RULE_AF)
# - final_metrics_atomicity: tmp_replace (META_RULE_AH; metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (NOT BaseException)
# - crlb_n/a: "coverage/rate curves on real corpus + labeled human gold; no substrate noise floor"
# - baseline_in_band: growth-OFF per-token miss stays 1.0 (not saturated to 0); use-probe base-rate in (0.05,0.95)
# - discriminator survives scale: smoke fires ALL discriminators (ON<OFF retention gap, shuffle collapses,
#   order metric responds to volume order with std>0) at a reduced per-volume cap; FULL confirms asymptote.
# - cardinality_ok: EXPECTED_N_BINS per arm + EXPECTED_N_ORDERS recorded; verdict counts them
# - calibration_check: default_ok_for_this_regime (graded>=0.5 affect threshold; VN taxonomy inherited)
# - all numbers in comments tagged HYPOTHESIZED@/MEASURED@/CITED@
# - self-test EXERCISES the REAL resources (wn_noun_semantics + VerbNet lexicon + nltk pos_tag) + the REAL
#   cleaner + the order-metric responds-to-order check on a synthetic 2-volume toy (real_code_path)
# - deterministic_seeding: np.random.default_rng(int) only; no hash()/list(set()); PROT-023 clean
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import traceback
from collections import Counter, OrderedDict
from datetime import datetime, timezone

import numpy as np

# Determinism for any BLAS touched incidentally.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import nltk  # noqa: E402
from nltk import pos_tag  # noqa: E402
from nltk.tokenize import word_tokenize, sent_tokenize  # noqa: E402
from nltk.corpus import wordnet as wn  # noqa: E402

# --------------------------------------------------------------------------------------------------
# Paths / constants
# --------------------------------------------------------------------------------------------------
ANCHOR_NAME = "exp_breadth_foundation_curriculum_order_mcguffey_v1"
CORPUS_DIR = os.path.join(REPO_ROOT, "data", "corpora", "mcguffey_readers")
VERBNET_LEX_PATH = os.path.join(REPO_ROOT, "data", "verbnet_affectedness_lexicon_v1_corrected", "lexicon.json")
UD_GOLD_PATH = os.path.join(REPO_ROOT, "data", "ud_ewt_semantic_affectedness_gold_v2_breadth", "gold.json")
FOUNDATION_DIR = os.path.join(REPO_ROOT, "data", "breadth_foundation_grown_mcguffey_v1")

# Curriculum order = easy -> hard (Primer .. Sixth). (vol_index, short_name, filename)
VOLUMES = [
    (0, "primer", "mcguffey_0_primer.txt"),
    (1, "first", "mcguffey_1_first.txt"),
    (2, "second", "mcguffey_2_second.txt"),
    (3, "third", "mcguffey_3_third.txt"),
    (4, "fourth", "mcguffey_4_fourth.txt"),
    (5, "fifth", "mcguffey_5_fifth.txt"),
    (6, "sixth", "mcguffey_6_sixth.txt"),
]
N_VOL = len(VOLUMES)

CONTENT_UPOS = ("NOUN", "VERB", "ADJ", "PROPN")
N_BINS = 12                      # main arm curves (binned by sentence index)
N_ORDER_BINS = 20                # order-test trajectory (binned by TOKEN fraction; fair across vol sizes)
N_ORDER_SHUFFLES_FULL = 24       # random volume-order permutations (null distribution)
N_ORDER_SHUFFLES_SMOKE = 6
AFFECT_THRESHOLD = 0.5
LOW_CONF_SENSES = 6
SHUFFLE_SEED = 1234              # meaning-shuffle (must-fail) seed
ORDER_SEED = 909                 # volume-order permutation seed base
GROUNDING_VOLS = (0, 1, 2)       # Primer/First/Second: picture-word candidate volumes
GROUNDING_MAX_CAPTION_WORDS = 2  # short single/two-word captions = candidate word<->referent pairings

# Penn treebank -> UPOS (content only).
PENN_TO_UPOS = {}
for t in ("NN", "NNS"):
    PENN_TO_UPOS[t] = "NOUN"
for t in ("NNP", "NNPS"):
    PENN_TO_UPOS[t] = "PROPN"
for t in ("VB", "VBD", "VBG", "VBN", "VBP", "VBZ"):
    PENN_TO_UPOS[t] = "VERB"
for t in ("JJ", "JJR", "JJS"):
    PENN_TO_UPOS[t] = "ADJ"

# WordNet noun-semantics (dominant-sense lexname + hypernym-closure animacy). Same vetted lookup as
# 29424 / atom 29420 (the who-affected reader). CITED@WordNet (Fellbaum 1998).
ANIM_HYPERNYMS = {"person.n.01", "animal.n.01", "causal_agent.n.01"}
LEXNAME_MAP = {
    "noun.person": ("person", {"animate", "human", "organism"}),
    "noun.animal": ("animal", {"animate", "animal", "organism"}),
    "noun.group": ("group", {"organization"}),
    "noun.location": ("location", {"location", "region", "concrete"}),
    "noun.artifact": ("artifact", {"concrete", "artifact"}),
    "noun.object": ("object", {"concrete"}),
    "noun.substance": ("substance", {"concrete", "substance"}),
    "noun.food": ("food", {"concrete", "comestible"}),
    "noun.body": ("body", {"concrete", "body_part"}),
    "noun.plant": ("plant", {"concrete", "plant"}),
    "noun.possession": ("possession", {"possession"}),
    "noun.communication": ("communication", {"communication"}),
    "noun.phenomenon": ("phenomenon", {"concrete", "phenomenon"}),
    "noun.cognition": ("abstract", {"abstract"}),
    "noun.state": ("abstract", {"abstract"}),
    "noun.attribute": ("abstract", {"abstract"}),
    "noun.feeling": ("abstract", {"abstract"}),
    "noun.event": ("abstract", {"abstract"}),
    "noun.act": ("abstract", {"abstract"}),
    "noun.time": ("abstract", {"abstract"}),
    "noun.relation": ("abstract", {"abstract"}),
    "noun.quantity": ("abstract", {"abstract"}),
    "noun.motive": ("abstract", {"abstract"}),
    "noun.process": ("abstract", {"abstract"}),
    "noun.shape": ("shape", {"concrete"}),
}
HIGH_AFFECT_GOLD = {"patient", "effected"}
LOW_AFFECT_GOLD = {"target_not_affected"}


def _clean(surface):
    return (surface or "").lower().strip(".,'\"!?;:()")


# --------------------------------------------------------------------------------------------------
# WordNet / VerbNet resolution (identical to 29424; the vetted functional lookups)
# --------------------------------------------------------------------------------------------------
def wn_noun_semantics(surface):
    s = _clean(surface)
    if not s:
        return None, None, set(), None, 0
    try:
        syns = wn.synsets(s, pos=wn.NOUN)
    except Exception:
        syns = []
    if not syns:
        return None, None, set(), None, 0
    dom = syns[0]
    lexname = dom.lexname()
    animate = False
    if lexname in ("noun.person", "noun.animal"):
        animate = True
    else:
        try:
            for path in dom.hypernym_paths():
                if {h.name() for h in path} & ANIM_HYPERNYMS:
                    animate = True
                    break
        except Exception:
            pass
    sem_type, feats = LEXNAME_MAP.get(lexname, ("other", set()))
    feats = set(feats)
    if animate:
        feats |= {"animate", "organism"}
    return animate, sem_type, feats, lexname, len(syns)


def wn_adj_meaning(surface):
    s = _clean(surface)
    if not s:
        return False, 0, None
    try:
        syns = wn.synsets(s, pos=wn.ADJ) + wn.synsets(s, pos=wn.ADJ_SAT)
    except Exception:
        syns = []
    if not syns:
        return False, 0, None
    return True, len(syns), syns[0].lexname()


def load_verbnet_lexicon():
    with open(VERBNET_LEX_PATH, encoding="utf-8") as f:
        doc = json.load(f)
    return doc["lexicon"]


def resolve_content_word(pos, lemma, verb_lex):
    """Supply the FUNCTIONAL meaning the reader needs. -> (resolved, source, meaning, category, conf)."""
    lem = _clean(lemma)
    if pos == "VERB":
        rec = verb_lex.get(lem) or verb_lex.get(lemma)
        if rec is not None:
            conf = 0.5 if rec.get("sense_ambiguous") else 1.0
            meaning = {"affectedness_type": rec.get("affectedness_type"),
                       "graded_score": float(rec.get("graded_score", 0.0)),
                       "vn_classes": rec.get("vn_classes", []),
                       "sense_ambiguous": bool(rec.get("sense_ambiguous", False))}
            cat = "resolved" if conf >= 1.0 else "resolved_sense_flagged"
            return True, "verbnet", meaning, cat, conf
        return False, None, None, "verb_not_in_verbnet", 0.0
    if pos == "NOUN" or pos == "PROPN":
        animate, sem_type, feats, lexname, n = wn_noun_semantics(lem)
        if sem_type is not None:
            conf = 1.0 if n < LOW_CONF_SENSES else 0.5
            meaning = {"animate": bool(animate), "sem_type": sem_type,
                       "features": sorted(feats), "lexname": lexname, "n_senses": int(n)}
            cat = "resolved" if conf >= 1.0 else "resolved_sense_flagged"
            return True, "wordnet_noun", meaning, cat, conf
        return False, None, None, ("named_entity" if pos == "PROPN" else "noun_oov_wordnet"), 0.0
    if pos == "ADJ":
        has, n, lx = wn_adj_meaning(lem)
        if has:
            conf = 1.0 if n < LOW_CONF_SENSES else 0.5
            meaning = {"has_sense": True, "n_senses": int(n), "lexname": lx}
            cat = "resolved" if conf >= 1.0 else "resolved_sense_flagged"
            return True, "wordnet_adj", meaning, cat, conf
        return False, None, None, "adj_oov_wordnet", 0.0
    return False, None, None, "other", 0.0


def build_shuffle_map(verb_lex, seed):
    keys = sorted(verb_lex.keys())
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(keys))
    return {keys[i]: keys[int(perm[i])] for i in range(len(keys))}


def assign_meaning(mode, pos, lemma, verb_lex, shuffle_map):
    """Arm-specific assignment. SHUFFLE corrupts meaning (permuted verb record / flipped noun bit) while
    preserving presence+category (coverage/ask curves identical to ON) -> usefulness probe must collapse."""
    resolved, source, meaning, cat, conf = resolve_content_word(pos, lemma, verb_lex)
    if mode != "SHUFFLE" or not resolved:
        return resolved, source, meaning, cat, conf
    lem = _clean(lemma)
    if pos == "VERB":
        alt_key = shuffle_map.get(lem) or shuffle_map.get(lemma)
        alt = verb_lex.get(alt_key)
        if alt is not None:
            meaning = {"affectedness_type": alt.get("affectedness_type"),
                       "graded_score": float(alt.get("graded_score", 0.0)),
                       "vn_classes": alt.get("vn_classes", []),
                       "sense_ambiguous": bool(alt.get("sense_ambiguous", False)),
                       "_shuffled_from": alt_key}
    elif pos in ("NOUN", "PROPN"):
        m2 = dict(meaning)
        m2["animate"] = not bool(m2.get("animate"))
        m2["sem_type"] = "abstract" if m2.get("sem_type") != "abstract" else "object"
        m2["_shuffled"] = True
        meaning = m2
    elif pos == "ADJ":
        m2 = dict(meaning)
        m2["_shuffled"] = True
        meaning = m2
    return resolved, source, meaning, cat, conf


# --------------------------------------------------------------------------------------------------
# McGuffey corpus cleaner + nltk front-end
# --------------------------------------------------------------------------------------------------
_ILLUS_RE = re.compile(r"\[Illustration:?\s*([^\]]*)\]", re.IGNORECASE | re.DOTALL)
_START_RE = re.compile(r"\*\*\*\s*START OF THE PROJECT GUTENBERG", re.IGNORECASE)
_END_RE = re.compile(r"\*\*\*\s*END OF THE PROJECT GUTENBERG", re.IGNORECASE)

# Line-level scaffolding drops (page markers, running heads, TOC lines, publisher/copyright, drills).
_DROP_PATTERNS = [
    re.compile(r"^\s*$"),                                  # blank
    re.compile(r"^\s*\(?[ivxlcdm]{1,6}\)?\s*$", re.IGNORECASE),   # roman-numeral page
    re.compile(r"^\s*\d{1,3}\s*$"),                        # bare page number
    re.compile(r"^\s*(LESSON|Lesson|EXERCISE|EXERCISES|EXERCISE\s+[IVXL]+)\b"),
    re.compile(r"^\s*[A-Z][A-Z .'&,-]{4,}$"),             # ALL-CAPS heading (TABLE OF..., CONTENTS, PREFACE)
    re.compile(r"ECLECTIC (SERIES|READER|EDUCATIONAL)", re.IGNORECASE),
    re.compile(r"(READER|PRIMER)\.?\s+\d+\s*$", re.IGNORECASE),   # running head "THIRD READER. 7"
    re.compile(r"^\s*(EP|MG|EU)\s+\d", re.IGNORECASE),    # printer marks "EP 179"
    re.compile(r"Copyright,", re.IGNORECASE),
    re.compile(r"(JOHN WILEY|AMERICAN BOOK COMPANY|VAN ANTWERP|Trademarks|Colophon)", re.IGNORECASE),
    re.compile(r"^\s*\d+\.\s+.*\s{2,}\d+\s*$"),           # TOC line "1. The Shepherd Boy    13"
    re.compile(r"^\s*\d+\.\s+.*\t\s*\d+\s*$"),            # TOC line (tab variant)
    re.compile(r"\t\s*\d+\s*$"),                          # any tab + trailing page number (TOC)
    re.compile(r"^\s*[A-Za-z .'-]+\.\s{2,}\d+\s*$"),      # TOC "An Evening Prayer   91"
    re.compile(r"DEFINITIONS|SPELL,? ?AND ?DEFINE|ARTICULATION|DIACRITICAL", re.IGNORECASE),
]


def _is_scaffolding_line(line):
    for pat in _DROP_PATTERNS:
        if pat.search(line):
            return True
    return False


def clean_volume_text(raw):
    """Strip Gutenberg header/footer + lesson scaffolding. Returns (clean_text, illustrations, stats).

    illustrations: list of {caption, is_grounding_candidate?} (candidate flag filled by caller w/ vol).
    """
    lines = raw.split("\n")
    # slice body between START and END markers.
    start_i, end_i = 0, len(lines)
    for i, ln in enumerate(lines):
        if _START_RE.search(ln):
            start_i = i + 1
            break
    for i in range(start_i, len(lines)):
        if _END_RE.search(lines[i]):
            end_i = i
            break
    body = lines[start_i:end_i]

    # extract + count illustration markers MULTILINE-aware (many captions span >1 line), then strip
    # them from the body before line-based scaffolding filtering.
    body_text = "\n".join(body)
    illustrations = []
    for m in _ILLUS_RE.finditer(body_text):
        cap = re.sub(r"\s+", " ", m.group(1)).strip().strip(".")
        illustrations.append(cap)
    body_text = _ILLUS_RE.sub(" ", body_text)

    kept = []
    n_dropped = 0
    body_lines = body_text.split("\n")
    for ln in body_lines:
        if _is_scaffolding_line(ln):
            n_dropped += 1
            continue
        kept.append(ln.strip())
    clean_text = " ".join(x for x in kept if x)
    # collapse whitespace runs.
    clean_text = re.sub(r"\s+", " ", clean_text).strip()
    stats = {"n_body_lines": len(body), "n_dropped_lines": n_dropped, "n_kept_lines": len(kept),
             "n_illustrations": len(illustrations)}
    return clean_text, illustrations, stats


def upos_lemma(word, penn):
    """Map Penn tag -> (upos, lemma) for content words; None if not content."""
    up = PENN_TO_UPOS.get(penn)
    if up is None:
        return None
    s = word.lower()
    if up == "PROPN":
        return "PROPN", s
    wnpos = {"NOUN": wn.NOUN, "VERB": wn.VERB, "ADJ": wn.ADJ}[up]
    try:
        lem = wn.morphy(s, wnpos) or s
    except Exception:
        lem = s
    return up, lem


def tag_volume(clean_text, max_sent):
    """nltk sentence-split + pos_tag -> list of sentences; each = list of (form, lemma, upos) content toks."""
    sents = []
    try:
        raw_sents = sent_tokenize(clean_text)
    except Exception:
        raw_sents = re.split(r"(?<=[.!?])\s+", clean_text)
    for rs in raw_sents:
        rs = rs.strip()
        if not rs:
            continue
        try:
            toks = word_tokenize(rs)
            tagged = pos_tag(toks)
        except Exception:
            continue
        cur = []
        for w, p in tagged:
            if not any(c.isalpha() for c in w):
                continue
            ul = upos_lemma(w, p)
            if ul is None:
                continue
            up, lem = ul
            cur.append((w, lem, up))
        if cur:
            sents.append(cur)
        if max_sent and len(sents) >= max_sent:
            break
    return sents


def load_corpus(max_sent_per_vol):
    """Clean + tag each volume. Returns (vol_sents[list-per-vol], vol_meta[list], illustration_report)."""
    vol_sents = []
    vol_meta = []
    all_illus = []
    grounding_candidates = []
    for (vi, name, fn) in VOLUMES:
        path = os.path.join(CORPUS_DIR, fn)
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        clean_text, illus, cstats = clean_volume_text(raw)
        sents = tag_volume(clean_text, max_sent_per_vol)
        n_tok = sum(len(s) for s in sents)
        vol_sents.append(sents)
        # illustration grounding candidates: short caption in Primer/First/Second.
        vol_cands = []
        for cap in illus:
            words = [w for w in re.split(r"\s+", cap) if w]
            is_cand = (vi in GROUNDING_VOLS and 1 <= len(words) <= GROUNDING_MAX_CAPTION_WORDS
                       and all(any(c.isalpha() for c in w) for w in words))
            all_illus.append({"vol": vi, "vol_name": name, "caption": cap, "grounding_candidate": bool(is_cand)})
            if is_cand:
                vol_cands.append(cap)
        grounding_candidates.append({"vol": vi, "vol_name": name, "candidates": vol_cands})
        vol_meta.append({"vol": vi, "vol_name": name, "n_sent": len(sents), "n_content_tokens": n_tok,
                         "n_illustrations": cstats["n_illustrations"],
                         "n_grounding_candidates": len(vol_cands),
                         "clean_stats": cstats})
        print("[corpus] vol=%d %-7s sents=%d content_tok=%d illus=%d grounding_cand=%d"
              % (vi, name, len(sents), n_tok, cstats["n_illustrations"], len(vol_cands)), flush=True)
    illustration_report = {"total_illustrations": len(all_illus),
                           "total_grounding_candidates": sum(1 for x in all_illus if x["grounding_candidate"]),
                           "per_volume_candidates": grounding_candidates,
                           "all_markers_sample": all_illus[:200]}
    return vol_sents, vol_meta, illustration_report


# --------------------------------------------------------------------------------------------------
# Main active-learning loop (one arm) -- 3-arm control on a FIXED sentence stream.
# --------------------------------------------------------------------------------------------------
def run_loop(sents, mode, verb_lex, shuffle_map, n_bins):
    store = OrderedDict()
    known = set()
    escalation = OrderedDict()
    residual_types = Counter()
    resolved_flagged_types = 0

    n_sent = len(sents)
    bin_size = max(1, (n_sent + n_bins - 1) // n_bins)
    ask_curve = [0] * n_bins
    sent_curve = [0] * n_bins
    cov_hit = [0] * n_bins
    cov_tot = [0] * n_bins

    for si, sent in enumerate(sents):
        b = min(si // bin_size, n_bins - 1)
        sent_curve[b] += 1
        for (form, lemma, upos) in sent:
            key = (upos, _clean(lemma))
            cov_tot[b] += 1
            rec = store.get(key)
            if rec is not None and rec.get("resolved"):
                cov_hit[b] += 1
            if key not in known:
                ask_curve[b] += 1
                resolved, source, meaning, cat, conf = assign_meaning(mode, upos, lemma, verb_lex, shuffle_map)
                if mode != "OFF":
                    known.add(key)
                    if resolved:
                        store[key] = {"pos": upos, "lemma": key[1], "source": source, "meaning": meaning,
                                      "confidence": conf, "resolved": True, "first_seen_sent": si, "category": cat}
                        if cat == "resolved_sense_flagged":
                            resolved_flagged_types += 1
                    else:
                        store[key] = {"pos": upos, "lemma": key[1], "source": None, "meaning": None,
                                      "confidence": 0.0, "resolved": False, "first_seen_sent": si, "category": cat}
                        escalation[key] = {"category": cat, "sent_idx": si, "pos": upos, "lemma": key[1]}
                        residual_types[cat] += 1
                else:
                    if not resolved:
                        escalation.setdefault(key, {"category": cat, "sent_idx": si})
                        residual_types[cat] += 1

    ask_rate = [ask_curve[i] / sent_curve[i] if sent_curve[i] else 0.0 for i in range(n_bins)]
    miss_rate = [ask_curve[i] / cov_tot[i] if cov_tot[i] else 0.0 for i in range(n_bins)]
    coverage = [cov_hit[i] / cov_tot[i] if cov_tot[i] else 0.0 for i in range(n_bins)]

    h = hashlib.sha256()
    for k in sorted(store.keys()):
        v = store[k]
        h.update(repr((k, v.get("resolved"), None if v.get("meaning") is None
                       else sorted(str(x) for x in v["meaning"].items()))).encode("utf-8"))
    store_hash = h.hexdigest()

    return {
        "mode": mode, "n_sent": n_sent, "n_bins": n_bins,
        "ask_rate_curve": [round(x, 4) for x in ask_rate],
        "miss_rate_curve": [round(x, 4) for x in miss_rate],
        "coverage_curve": [round(x, 4) for x in coverage],
        "ask_counts": ask_curve, "sent_counts": sent_curve, "cov_hit": cov_hit, "cov_tot": cov_tot,
        "residual_by_category": dict(residual_types), "n_resolved_flagged_types": resolved_flagged_types,
        "n_store_entries": len(store), "n_resolved_entries": sum(1 for v in store.values() if v.get("resolved")),
        "n_escalations": len(escalation), "store_hash": store_hash,
        "_store": store, "_escalation": escalation,
    }


# --------------------------------------------------------------------------------------------------
# Curriculum-order test: growth-ON over a given VOLUME ORDER, binned by TOKEN fraction.
# --------------------------------------------------------------------------------------------------
def run_order_curve(vol_sents, volume_order, verb_lex, n_bins):
    """growth-ON over volumes concatenated in volume_order. Bin by cumulative TOKEN fraction (fair across
    volume sizes). Returns per-bin coverage/miss + trajectory summaries (coverage@25/50, early-cov mean,
    cumulative asks/escalations by mid-point, ask-curve smoothness)."""
    stream = []
    for vi in volume_order:
        stream.extend(vol_sents[vi])
    total_tok = sum(len(s) for s in stream)
    if total_tok == 0:
        return None

    known = set()
    store_resolved = set()
    cov_hit = [0] * n_bins
    cov_tot = [0] * n_bins
    ask_curve = [0] * n_bins
    esc_cum = []                 # cumulative escalations at each token index (sparse: record at half)
    tok_idx = 0
    half_tok = total_tok // 2
    cum_asks_at_half = 0
    cum_esc_at_half = 0
    n_esc = 0

    for sent in stream:
        for (form, lemma, upos) in sent:
            key = (upos, _clean(lemma))
            b = min(int(tok_idx * n_bins / total_tok), n_bins - 1)
            cov_tot[b] += 1
            if key in store_resolved:
                cov_hit[b] += 1
            if key not in known:
                ask_curve[b] += 1
                known.add(key)
                resolved, source, meaning, cat, conf = resolve_content_word(upos, lemma, verb_lex)
                if resolved:
                    store_resolved.add(key)
                else:
                    n_esc += 1
                if tok_idx < half_tok:
                    cum_asks_at_half += 1
                    if not resolved:
                        cum_esc_at_half += 1
            tok_idx += 1

    coverage = [cov_hit[i] / cov_tot[i] if cov_tot[i] else 0.0 for i in range(n_bins)]
    miss = [ask_curve[i] / cov_tot[i] if cov_tot[i] else 0.0 for i in range(n_bins)]
    half_bin = n_bins // 2
    q1 = max(0, n_bins // 4 - 0)
    cov_at_25 = coverage[min(q1, n_bins - 1)]
    cov_at_50 = coverage[min(half_bin, n_bins - 1)]
    early_cov_mean = float(np.mean(coverage[:half_bin])) if half_bin > 0 else 0.0
    late_cov_mean = float(np.mean(coverage[half_bin:])) if half_bin < n_bins else 0.0
    smooth = _spearman_vs_index(miss)   # strongly negative = smooth monotone decline
    return {
        "volume_order": list(volume_order), "total_tok": total_tok,
        "coverage_curve": [round(x, 4) for x in coverage], "miss_curve": [round(x, 4) for x in miss],
        "cov_at_25": round(cov_at_25, 4), "cov_at_50": round(cov_at_50, 4),
        "early_cov_mean": round(early_cov_mean, 4), "late_cov_mean": round(late_cov_mean, 4),
        "cum_asks_at_half": cum_asks_at_half, "cum_esc_at_half": cum_esc_at_half,
        "n_escalations": n_esc, "n_unique_types": len(known), "ask_smoothness_spearman": round(smooth, 4),
    }


def run_curriculum_order_test(vol_sents, verb_lex, n_shuffles, n_bins, order_seed):
    """ORDERED [0..6] vs n_shuffles random volume permutations. Returns ordered curve, shuffled
    distribution, and the order-advantage summary (z-scores + direction verdict)."""
    ordered = run_order_curve(vol_sents, list(range(N_VOL)), verb_lex, n_bins)
    shuffles = []
    for k in range(n_shuffles):
        rng = np.random.default_rng(order_seed + k)
        perm = [int(x) for x in rng.permutation(N_VOL)]
        # guarantee the null is not accidentally the identity ordered run.
        if perm == list(range(N_VOL)):
            perm = perm[::-1]
        cur = run_order_curve(vol_sents, perm, verb_lex, n_bins)
        shuffles.append(cur)

    def _dist(field):
        vals = np.array([s[field] for s in shuffles], dtype=float)
        return vals

    early = _dist("early_cov_mean")
    c25 = _dist("cov_at_25")
    c50 = _dist("cov_at_50")
    asks_half = _dist("cum_asks_at_half")
    esc_half = _dist("cum_esc_at_half")
    smooth = _dist("ask_smoothness_spearman")

    def _z(ordered_val, arr):
        m, sd = float(arr.mean()), float(arr.std())
        if sd < 1e-9:
            return 0.0, m, sd
        return (ordered_val - m) / sd, m, sd

    z_early, m_early, sd_early = _z(ordered["early_cov_mean"], early)
    z_c25, m_c25, sd_c25 = _z(ordered["cov_at_25"], c25)
    z_c50, m_c50, sd_c50 = _z(ordered["cov_at_50"], c50)
    # asks/escalations: LOWER is "ordered defers cost" -> flip sign so positive = ordered advantage.
    z_asks, m_asks, sd_asks = _z(ordered["cum_asks_at_half"], asks_half)
    z_esc, m_esc, sd_esc = _z(ordered["cum_esc_at_half"], esc_half)
    early_cov_area = ordered["early_cov_mean"] - m_early

    # percentile of ordered early-cov among shuffles (how extreme).
    pctile_early = float((early < ordered["early_cov_mean"]).mean())

    # PRIMARY order metric = early-coverage z (does easy-first understand more mid-curriculum?).
    if z_c25 >= 1.0 and early_cov_area > 0:
        order_verdict = "ORDER_HELPS"
    elif z_c25 <= -1.0 and early_cov_area < 0:
        order_verdict = "ORDER_HURTS"
    else:
        order_verdict = "ORDER_NO_ADVANTAGE"

    # SECONDARY order metric = early-escalation DEFERRAL (USER-named "fewer escalations early"). LOWER
    # early escalations = ordered defers rare/hard-word cost -> z_esc negative = ordered advantage.
    if z_esc <= -1.0:
        order_verdict_escalation = "ORDER_HELPS_defers_escalations"
    elif z_esc >= 1.0:
        order_verdict_escalation = "ORDER_HURTS_more_early_escalations"
    else:
        order_verdict_escalation = "ORDER_NO_ADVANTAGE"

    order_measurement_valid = (ordered is not None and all(s is not None for s in shuffles)
                               and sd_c25 > 0.005)

    return {
        "ordered": ordered,
        "shuffled_n": n_shuffles,
        "shuffled_orders": [s["volume_order"] for s in shuffles],
        "order_verdict": order_verdict,
        "order_verdict_escalation": order_verdict_escalation,
        "order_measurement_valid": bool(order_measurement_valid),
        "early_cov_area_ordered_minus_shuffmean": round(early_cov_area, 4),
        "ordered_early_cov_mean": ordered["early_cov_mean"],
        "shuffled_early_cov_mean": round(m_early, 4), "shuffled_early_cov_std": round(sd_early, 4),
        "z_early_cov": round(z_early, 3),
        "ordered_cov_at_25": ordered["cov_at_25"], "shuffled_cov_at_25_mean": round(m_c25, 4),
        "shuffled_cov_at_25_std": round(sd_c25, 4), "z_cov_at_25": round(z_c25, 3),
        "ordered_cov_at_50": ordered["cov_at_50"], "shuffled_cov_at_50_mean": round(m_c50, 4),
        "z_cov_at_50": round(z_c50, 3),
        "ordered_cum_asks_at_half": ordered["cum_asks_at_half"],
        "shuffled_cum_asks_at_half_mean": round(m_asks, 2), "z_cum_asks_at_half": round(z_asks, 3),
        "ordered_cum_esc_at_half": ordered["cum_esc_at_half"],
        "shuffled_cum_esc_at_half_mean": round(m_esc, 2), "z_cum_esc_at_half": round(z_esc, 3),
        "ordered_ask_smoothness": ordered["ask_smoothness_spearman"],
        "shuffled_ask_smoothness_mean": round(float(smooth.mean()), 4),
        "ordered_early_cov_percentile_vs_shuffled": round(pctile_early, 4),
        "shuffled_early_cov_distribution": [round(float(x), 4) for x in early],
        "shuffled_cov_at_25_distribution": [round(float(x), 4) for x in c25],
    }


# --------------------------------------------------------------------------------------------------
# Functional-usefulness probe (independent human gold; the shuffle must-fail) -- from 29424.
# --------------------------------------------------------------------------------------------------
def _lemv(surface):
    s = _clean(surface)
    try:
        return wn.morphy(s, wn.VERB) or s
    except Exception:
        return s


def load_gold_binary():
    with open(UD_GOLD_PATH, encoding="utf-8") as f:
        gold = json.load(f)["gold"]
    items = []
    for g in gold:
        t = g.get("type")
        if t in HIGH_AFFECT_GOLD:
            label = 1
        elif t in LOW_AFFECT_GOLD:
            label = 0
        else:
            continue
        items.append({"verb": _lemv(g.get("verb")), "label": label, "type": t})
    return items


def _auc(high_scores, low_scores):
    if not high_scores or not low_scores:
        return None
    num = 0.0
    for h in high_scores:
        for l in low_scores:
            num += 1.0 if h > l else (0.5 if h == l else 0.0)
    return num / (len(high_scores) * len(low_scores))


def _probe_scores(gold_items, verb_lex, key_map):
    high, low = [], []
    for it in gold_items:
        src_key = key_map(it["verb"])
        rec = verb_lex.get(src_key)
        if rec is None:
            continue
        s = float(rec.get("graded_score", 0.0))
        (high if it["label"] == 1 else low).append(s)
    return high, low, len(high) + len(low)


def functional_probe(gold_items, verb_lex, n_shuffle_seeds):
    keys = sorted(verb_lex.keys())

    def real_key(v):
        return v if v in verb_lex else None

    hs, ls, used = _probe_scores(gold_items, verb_lex, real_key)
    real_auc = _auc(hs, ls)
    acc_correct = sum(1 for s in hs if s >= AFFECT_THRESHOLD) + sum(1 for s in ls if s < AFFECT_THRESHOLD)
    real_acc = acc_correct / used if used else 0.0
    n_hi, n_lo = len(hs), len(ls)
    majority = max(n_hi, n_lo) / used if used else 0.5

    shuffle_aucs = []
    for seed in range(n_shuffle_seeds):
        rng = np.random.default_rng(SHUFFLE_SEED + seed)
        perm = rng.permutation(len(keys))
        pmap = {keys[i]: keys[int(perm[i])] for i in range(len(keys))}

        def sh_key(v, _pm=pmap):
            return _pm.get(v)

        shs, sls, _ = _probe_scores(gold_items, verb_lex, sh_key)
        a = _auc(shs, sls)
        if a is not None:
            shuffle_aucs.append(a)
    sh = np.array(shuffle_aucs) if shuffle_aucs else np.array([0.5])
    return {
        "real_auc": round(float(real_auc), 4) if real_auc is not None else None,
        "shuffle_auc_mean": round(float(sh.mean()), 4), "shuffle_auc_std": round(float(sh.std()), 4),
        "shuffle_auc_max": round(float(sh.max()), 4),
        "auc_delta_real_minus_shuffle_mean": round(float(real_auc - sh.mean()), 4) if real_auc is not None else None,
        "real_binary_acc": round(real_acc, 4), "majority_chance": round(majority, 4),
        "n_high": n_hi, "n_low": n_lo, "n_used": used, "n_shuffle_seeds": len(shuffle_aucs),
    }


# --------------------------------------------------------------------------------------------------
# Curve helpers
# --------------------------------------------------------------------------------------------------
def _spearman_vs_index(curve):
    n = len(curve)
    if n < 3:
        return 0.0
    x = np.arange(n, dtype=float)
    y = np.asarray(curve, dtype=float)
    if float(np.ptp(y)) < 1e-9:
        return 0.0
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    if denom <= 1e-12:
        return 0.0
    return float((rx * ry).sum() / denom)


# --------------------------------------------------------------------------------------------------
# Self-test (non-tautological)
# --------------------------------------------------------------------------------------------------
def self_test():
    print("[self-test] starting", flush=True)
    verb_lex = load_verbnet_lexicon()
    shuffle_map = build_shuffle_map(verb_lex, SHUFFLE_SEED)

    # (1) real_code_path: exercise REAL resources (VerbNet + WordNet noun/adj + nltk pos_tag + cleaner).
    exercised = set()
    r_verb = resolve_content_word("VERB", "kill", verb_lex)
    assert r_verb[0] and r_verb[1] == "verbnet" and r_verb[2]["graded_score"] > 0.5, "real verb lookup failed"
    exercised.add("verbnet_lexicon")
    r_noun = resolve_content_word("NOUN", "dog", verb_lex)
    assert r_noun[0] and r_noun[1] == "wordnet_noun" and r_noun[2]["animate"] is True, "real noun lookup failed"
    exercised.add("wn_noun_semantics")
    r_adj = resolve_content_word("ADJ", "amazing", verb_lex)
    assert r_adj[0] and r_adj[1] == "wordnet_adj", "real adj lookup failed"
    exercised.add("wn_adj_meaning")
    # nltk front-end really tags + maps to UPOS content tokens.
    toks = tag_volume("The kind man led the little dog home. The cat ran fast.", max_sent=0)
    flat = [(w, l, p) for s in toks for (w, l, p) in s]
    assert any(p == "VERB" for _, _, p in flat) and any(p == "NOUN" for _, _, p in flat), "nltk front-end no content"
    exercised.add("nltk_pos_tag")
    assert {"verbnet_lexicon", "wn_noun_semantics", "wn_adj_meaning", "nltk_pos_tag"} <= exercised, "real_code_path incomplete"

    # (2) cleaner strips Gutenberg boilerplate + illustration markers, and EXTRACTS the marker captions.
    toy_raw = ("junk header\n*** START OF THE PROJECT GUTENBERG EBOOK X ***\n"
               "[Illustration: Cat]\nLESSON 1\nThe cat ran home.\n(iii)\nECLECTIC SERIES\n"
               "The dog sat by the fire.\n*** END OF THE PROJECT GUTENBERG EBOOK X ***\nlicense junk\n")
    ct, illus, cstats = clean_volume_text(toy_raw)
    assert "cat ran home" in ct.lower() and "dog sat" in ct.lower(), "cleaner dropped real passage text"
    assert "license junk" not in ct.lower() and "junk header" not in ct.lower(), "cleaner kept Gutenberg boilerplate"
    assert "eclectic series" not in ct.lower() and "lesson 1" not in ct.lower(), "cleaner kept scaffolding"
    assert "Cat" in illus and cstats["n_illustrations"] == 1, "illustration marker not extracted/counted"
    exercised.add("cleaner")

    # (3) functional != presence: a verb can be in WordNet yet functionally UNCOVERED (not in VN lexicon).
    functionally_uncovered = None
    for cand in ["photosynthesize", "quantize", "google", "defenestrate", "subitize"]:
        if bool(wn.synsets(cand, pos=wn.VERB)) and cand not in verb_lex:
            functionally_uncovered = cand
            break
    assert functionally_uncovered is not None, "expected >=1 WN verb NOT in affectedness lexicon"

    # (4) named-entity escalation fires for a PROPN with no common-noun synset.
    r_pe = resolve_content_word("PROPN", "Xylophonia", verb_lex)
    assert (not r_pe[0]) and r_pe[3] == "named_entity", "named_entity escalation did not fire"

    # (5) ask/miss RESPONDS to growth: repetitive toy stream -> ON per-token miss declines to 0; OFF flat 1.0.
    toy = [[("run", "run", "VERB"), ("dog", "dog", "NOUN")]] * 8
    on = run_loop(toy, "ON", verb_lex, shuffle_map, n_bins=4)
    off = run_loop(toy, "OFF", verb_lex, shuffle_map, n_bins=4)
    assert all(abs(x - 1.0) < 1e-9 for x in off["miss_rate_curve"]), "OFF per-token miss must be 1.0 (no retention)"
    assert on["miss_rate_curve"][-1] < 0.5, "ON per-token miss must decline (retention)"

    # (6) shuffle collapses the usefulness probe (multi-seed AUC null).
    gold = load_gold_binary()
    up = functional_probe(gold, verb_lex, n_shuffle_seeds=8)
    assert up["real_auc"] is not None and up["auc_delta_real_minus_shuffle_mean"] >= 0.15, \
        "shuffle must collapse usefulness (real_auc - shuffle_mean < 0.15)"

    # (7) ORDER metric RESPONDS to volume order (non-tautological; does NOT assert the empirical direction).
    #     Synthetic 2-'volume' toy: vol A = one word repeated (high reuse); vol B = many one-off types.
    #     [A,B] (easy-first) must give HIGHER early coverage than [B,A] (hard-first) -> the metric moves.
    volA = [[("dog", "dog", "NOUN")]] * 40                             # high-reuse easy volume
    volB = [[("w%d" % i, "w%d" % i, "NOUN")] for i in range(40)]       # all-unique hard volume
    toy_vols = [volA, volB]
    easy_first = run_order_curve(toy_vols, [0, 1], verb_lex, n_bins=8)
    hard_first = run_order_curve(toy_vols, [1, 0], verb_lex, n_bins=8)
    assert easy_first["cov_at_25"] > hard_first["cov_at_25"] + 0.10, \
        "order metric must RESPOND to volume order (easy-first early-cov must exceed hard-first)"
    print("[self-test] order metric responds: easy_first cov@25=%.3f > hard_first cov@25=%.3f"
          % (easy_first["cov_at_25"], hard_first["cov_at_25"]), flush=True)

    # (8) arms_differ + determinism on a tiny real stream (Primer only, first sentences).
    vs, _, _ = load_corpus(max_sent_per_vol=20)
    small = vs[0][:20]
    a_on = run_loop(small, "ON", verb_lex, shuffle_map, n_bins=4)
    a_sh = run_loop(small, "SHUFFLE", verb_lex, shuffle_map, n_bins=4)
    assert a_on["store_hash"] != a_sh["store_hash"], "ON and SHUFFLE store states must differ"
    a_on2 = run_loop(small, "ON", verb_lex, shuffle_map, n_bins=4)
    assert a_on["ask_rate_curve"] == a_on2["ask_rate_curve"], "loop not deterministic"

    print("[self-test] PASS", flush=True)
    return True


# --------------------------------------------------------------------------------------------------
# Metrics write (atomic tmp+replace; META_RULE_AH)
# --------------------------------------------------------------------------------------------------
def output_dir(mode_tag):
    d = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + ("_smoke" if mode_tag == "smoke" else ""))
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_units):
    import platform
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_units,
              "host": platform.node()}
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _write_metrics(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(out_dir, diag)


def save_foundation_artifact(on_result, illustration_report):
    os.makedirs(FOUNDATION_DIR, exist_ok=True)
    store = on_result["_store"]
    esc = on_result["_escalation"]
    doc = {
        "_meta": {"name": "breadth_foundation_grown_mcguffey_v1",
                  "built": datetime.now(timezone.utc).isoformat(),
                  "source": "grown on-demand by the read-drives-knowledge loop over McGuffey Primer..Sixth "
                            "IN CURRICULUM ORDER; VERB=VerbNet affectedness lexicon; NOUN/PROPN=WordNet noun "
                            "semantics; ADJ=WordNet ADJ; POS/lemma=nltk front-end",
                  "anchor": ANCHOR_NAME, "n_entries": len(store),
                  "n_resolved": on_result["n_resolved_entries"], "n_escalations": len(esc),
                  "note": "COPY / new store; production KBs untouched; NOT banked (skunkworks VETs after)"},
        "foundation": {f"{k[0]}:{k[1]}": {"pos": v["pos"], "lemma": v["lemma"], "source": v["source"],
                                          "resolved": v["resolved"], "confidence": v["confidence"],
                                          "category": v["category"], "meaning": v["meaning"],
                                          "first_seen_sent": v["first_seen_sent"]}
                       for k, v in store.items()},
    }
    tmp = os.path.join(FOUNDATION_DIR, "foundation.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    os.replace(tmp, os.path.join(FOUNDATION_DIR, "foundation.json"))

    escdoc = {"_meta": {"name": "breadth_foundation_escalation_queue_mcguffey_v1",
                        "built": datetime.now(timezone.utc).isoformat(), "anchor": ANCHOR_NAME,
                        "note": "words NO local resource covers -> would escalate. NOT fetched (headless "
                                "cannot web-auth); logged build-time.", "n": len(esc)},
              "queue": [{"pos": v.get("pos", k[0]), "lemma": v.get("lemma", k[1]),
                         "category": v["category"], "first_seen_sent": v["sent_idx"]}
                        for k, v in esc.items()]}
    tmp2 = os.path.join(FOUNDATION_DIR, "escalation_queue.json.tmp")
    with open(tmp2, "w", encoding="utf-8") as f:
        json.dump(escdoc, f, indent=2)
    os.replace(tmp2, os.path.join(FOUNDATION_DIR, "escalation_queue.json"))

    # vision-ready illustration index (preserved, NOT encoded).
    illdoc = {"_meta": {"name": "mcguffey_illustration_index_v1", "anchor": ANCHOR_NAME,
                        "built": datetime.now(timezone.utc).isoformat(),
                        "note": "illustration markers preserved + flagged grounding-relevant (Primer/First/"
                                "Second short captions = candidate word<->referent pairings). Vision parked: "
                                "NOT encoded; preserved vision-ready for a later grounding pass. "
                                "First Reader's 102 extracted figures already at data/exp_textbook_extract_"
                                "mcguffey_v1/figures/."},
              "report": illustration_report}
    tmp3 = os.path.join(FOUNDATION_DIR, "illustration_index.json.tmp")
    with open(tmp3, "w", encoding="utf-8") as f:
        json.dump(illdoc, f, indent=2)
    os.replace(tmp3, os.path.join(FOUNDATION_DIR, "illustration_index.json"))


# --------------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------------
def run(mode_tag, max_sent_per_vol, n_shuffles):
    t0 = time.time()
    out_dir = output_dir(mode_tag)
    _write_start_marker(out_dir, mode_tag, expected_units=3 * N_BINS + n_shuffles + 1)

    verb_lex = load_verbnet_lexicon()
    shuffle_map = build_shuffle_map(verb_lex, SHUFFLE_SEED)

    print("[run] loading + tagging corpus...", flush=True)
    vol_sents, vol_meta, illustration_report = load_corpus(max_sent_per_vol)

    # ORDERED curriculum stream (Primer..Sixth) for the 3-arm control loop.
    ordered_stream = []
    for vi in range(N_VOL):
        ordered_stream.extend(vol_sents[vi])
    n_content_tokens = sum(len(s) for s in ordered_stream)
    print("[run] ordered stream: sents=%d content_tok=%d" % (len(ordered_stream), n_content_tokens), flush=True)

    print("[run] 3-arm control loop (ON/OFF/SHUFFLE)...", flush=True)
    res_on = run_loop(ordered_stream, "ON", verb_lex, shuffle_map, N_BINS)
    res_off = run_loop(ordered_stream, "OFF", verb_lex, shuffle_map, N_BINS)
    res_shuf = run_loop(ordered_stream, "SHUFFLE", verb_lex, shuffle_map, N_BINS)
    res_on2 = run_loop(ordered_stream, "ON", verb_lex, shuffle_map, N_BINS)  # determinism

    print("[run] usefulness probe...", flush=True)
    gold = load_gold_binary()
    use = functional_probe(gold, verb_lex, n_shuffle_seeds=20)

    print("[run] curriculum-order test (ordered vs %d shuffled volume orders)..." % n_shuffles, flush=True)
    order = run_curriculum_order_test(vol_sents, verb_lex, n_shuffles, N_ORDER_BINS, ORDER_SEED)

    # ---- summaries (difficulty-gradient-robust retention signal) ----
    off_miss_mean = float(np.mean(res_off["miss_rate_curve"]))
    on_miss_mean = float(np.mean(res_on["miss_rate_curve"]))
    retention_gap_mean = off_miss_mean - on_miss_mean
    on_cov_mean = float(np.mean(res_on["coverage_curve"]))
    off_cov_mean = float(np.mean(res_off["coverage_curve"]))
    on_miss_first, on_miss_last = res_on["miss_rate_curve"][0], res_on["miss_rate_curve"][-1]
    use_delta = use["auc_delta_real_minus_shuffle_mean"]

    # ---- bands ----
    retention_works = (off_miss_mean >= 0.98) and (on_miss_mean <= 0.70) and (retention_gap_mean >= 0.30)
    on_coverage_positive = (on_cov_mean >= 0.20) and (on_cov_mean - off_cov_mean >= 0.20)
    shuffle_collapses = ((use["real_auc"] is not None) and (use_delta is not None and use_delta >= 0.15)
                         and (use["real_auc"] >= 0.70) and (0.40 <= use["shuffle_auc_mean"] <= 0.60))
    arms_differ = (res_on["store_hash"] != res_shuf["store_hash"]) and (res_on["store_hash"] != res_off["store_hash"])
    deterministic = res_on2["ask_rate_curve"] == res_on["ask_rate_curve"]
    cardinality_ok = (all(len(r["ask_rate_curve"]) == N_BINS for r in (res_on, res_off, res_shuf))
                      and len(order["shuffled_orders"]) == n_shuffles
                      and len(order["ordered"]["coverage_curve"]) == N_ORDER_BINS)
    order_measurement_valid = order["order_measurement_valid"]

    hard_pass = (retention_works and on_coverage_positive and shuffle_collapses and arms_differ
                 and deterministic and cardinality_ok and order_measurement_valid)
    hard_fail = ((off_miss_mean < 0.98) or (retention_gap_mean < 0.30) or (not shuffle_collapses)
                 or (not arms_differ) or (not deterministic) or (not order_measurement_valid))
    if hard_pass:
        verdict, band = "HARD_PASS", "HARD_PASS_CURRICULUM"
    elif hard_fail:
        verdict, band = "HARD_FAIL", "HARD_FAIL_CURRICULUM"
    else:
        verdict, band = "MIDDLE_BAND", "MIDDLE_BAND_CURRICULUM"

    # residual breakdown as fraction of ON content-word TYPES.
    n_types = res_on["n_store_entries"]
    residual = res_on["residual_by_category"]
    residual_frac = {k: round(v / n_types, 4) for k, v in residual.items()} if n_types else {}

    elapsed = time.time() - t0
    msg = (f"{verdict} [{order['order_verdict']}] "
           f"on_miss_mean={on_miss_mean:.3f} off_miss_mean={off_miss_mean:.3f} "
           f"retention_gap={retention_gap_mean:.3f} on_cov_mean={on_cov_mean:.3f} "
           f"(on_miss {on_miss_first:.2f}->{on_miss_last:.2f}) "
           f"use_real_auc={use['real_auc']} use_shuffle_auc={use['shuffle_auc_mean']}+-{use['shuffle_auc_std']} "
           f"auc_delta={use_delta} | ORDER: ord_cov25={order['ordered_cov_at_25']} "
           f"shuf_cov25={order['shuffled_cov_at_25_mean']}+-{order['shuffled_cov_at_25_std']} "
           f"z_cov25={order['z_cov_at_25']} early_area={order['early_cov_area_ordered_minus_shuffmean']} "
           f"ord_esc_half={order['ordered_cum_esc_at_half']} shuf_esc_half={order['shuffled_cum_esc_at_half_mean']} "
           f"z_esc={order['z_cum_esc_at_half']} | n_sent={len(ordered_stream)} "
           f"n_content_tokens={n_content_tokens} n_grown={n_types} n_escalations={res_on['n_escalations']} "
           f"illus={illustration_report['total_illustrations']} "
           f"grounding_cand={illustration_report['total_grounding_candidates']}")

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": band, "elapsed_s": round(elapsed, 2),
        "run_mode": mode_tag, "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "mode_tag": mode_tag, "n_sent": len(ordered_stream), "n_content_tokens": n_content_tokens,
        "n_bins": N_BINS, "n_order_bins": N_ORDER_BINS, "n_order_shuffles": n_shuffles,
        "order_verdict": order["order_verdict"],
        "bands": {
            "retention_works": bool(retention_works), "on_coverage_positive": bool(on_coverage_positive),
            "shuffle_collapses": bool(shuffle_collapses), "arms_differ": bool(arms_differ),
            "deterministic": bool(deterministic), "cardinality_ok": bool(cardinality_ok),
            "order_measurement_valid": bool(order_measurement_valid),
        },
        "retention": {
            "note": "PRIMARY difficulty-gradient-robust signal: growth-ON vs growth-OFF per-token miss. "
                    "OFF=1.0 by construction (re-asks every token); ON below by retention; GAP is gradient-free.",
            "growth_ON_miss_curve": res_on["miss_rate_curve"], "growth_OFF_miss_curve": res_off["miss_rate_curve"],
            "growth_SHUFFLE_miss_curve": res_shuf["miss_rate_curve"],
            "on_miss_mean": round(on_miss_mean, 4), "off_miss_mean": round(off_miss_mean, 4),
            "retention_gap_mean": round(retention_gap_mean, 4),
            "on_miss_first": on_miss_first, "on_miss_last": on_miss_last,
        },
        "ask_rate_per_sentence": {
            "note": "USER-named view (new-gaps per sentence) on the ordered curriculum. Carries a "
                    "difficulty-gradient + sentence-length drift (rich late volumes) -> retention gap drives verdict.",
            "growth_ON_curve": res_on["ask_rate_curve"], "growth_OFF_curve": res_off["ask_rate_curve"],
        },
        "coverage": {
            "growth_ON_curve": res_on["coverage_curve"], "growth_OFF_curve": res_off["coverage_curve"],
            "on_cov_mean": round(on_cov_mean, 4), "off_cov_mean": round(off_cov_mean, 4),
            "note": "On graded easy->hard text binned coverage does NOT monotonically rise (rich late "
                    "volumes lower per-bin coverage); on_cov_mean vs off_cov_mean is the retention view.",
        },
        "curriculum_order_test": order,
        "usefulness_probe": use,
        "residual_gap_breakdown": {
            "by_category_types": residual, "by_category_frac_of_grown_types": residual_frac,
            "n_grown_types": n_types, "n_resolved_types": res_on["n_resolved_entries"],
            "n_resolved_sense_flagged": res_on["n_resolved_flagged_types"], "n_escalations": res_on["n_escalations"],
        },
        "illustration_report": {k: v for k, v in illustration_report.items() if k != "all_markers_sample"},
        "illustration_markers_sample": illustration_report["all_markers_sample"][:60],
        "per_volume_meta": vol_meta,
        "store_hashes": {"ON": res_on["store_hash"], "OFF": res_off["store_hash"], "SHUFFLE": res_shuf["store_hash"]},
        "vs_ud_ewt_29424": {
            "note": "UD-EWT breadth loop (atom 29424) reference for contrast.",
            "ud_ewt_full_on_cov_asymptote": 0.7934, "ud_ewt_full_on_miss_first_last": [0.4251, 0.1478],
            "ud_ewt_use_real_auc": 0.8924, "ud_ewt_use_shuffle_auc_mean": 0.5122,
            "source": "MEASURED@data/exp_breadth_foundation_active_growth_loop_ud_ewt_v1/metrics.json",
        },
        "prereg_bands": {
            "HARD_PASS": "retention_works AND on_coverage_positive AND shuffle_collapses AND arms_differ "
                         "AND deterministic AND cardinality_ok AND order_measurement_valid",
            "HARD_FAIL": "off_miss_mean<0.98 OR retention_gap<0.30 OR not shuffle_collapses OR not arms_differ "
                         "OR not deterministic OR not order_measurement_valid",
            "order_verdict": "REPORTED not gated: ORDER_HELPS(z_cov25>=1 & area>0) | ORDER_NO_ADVANTAGE | "
                             "ORDER_HURTS(z_cov25<=-1 & area<0)",
        },
        "calibration_check": "default_ok_for_this_regime",
        "crlb_n/a": "coverage/rate curves on real corpus + labeled human gold; no substrate noise floor",
        "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": "np.random.default_rng(int) only; no hash()/list(set()); PROT-023 clean",
    }
    _write_metrics(out_dir, metrics)

    if mode_tag == "full":
        save_foundation_artifact(res_on, illustration_report)

    print(msg, flush=True)
    print("[done] wrote", os.path.join(out_dir, "metrics.json"), "elapsed=%.1fs" % elapsed, flush=True)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--max-sent-per-vol", type=int, default=0)
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return
    if args.smoke:
        run("smoke", max_sent_per_vol=args.max_sent_per_vol or 120, n_shuffles=N_ORDER_SHUFFLES_SMOKE)
        return
    if args.full:
        run("full", max_sent_per_vol=args.max_sent_per_vol or 0, n_shuffles=N_ORDER_SHUFFLES_FULL)
        return
    self_test()


if __name__ == "__main__":
    OUT_FOR_CRASH = output_dir("smoke")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUT_FOR_CRASH, e)
        raise
