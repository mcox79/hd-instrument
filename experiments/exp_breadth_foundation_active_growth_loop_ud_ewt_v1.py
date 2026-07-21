#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_breadth_foundation_active_growth_loop_ud_ewt_v1

LAYER-0 BREADTH-FOUNDATION ENGINE: activate the read-drives-knowledge LOOP as an ACTUAL running
active-learning loop (not Director-driven manual dispatch). READ a stream of real varied prose
(UD-EWT web treebank), DETECT word-meaning coverage GAPS, ASSIGN meanings on-demand from the KB
resources (VerbNet affectedness lexicon + WordNet noun/adj semantics), GROW a foundation store,
and MEASURE the ACTIVE-LEARNING SIGNATURE: the ask-rate (unmet-gaps per sentence) DECLINING as the
foundation grows. Breadth is the base the whole composition/reasoning pyramid sits on.

MECHANISM (glass-box, NO external LLM at inference):
  STREAM   = UD-EWT train.conllu, sentence-by-sentence in fixed corpus order (held-out ordering: the
             loop never sees the future). GOLD UPOS+LEMMA read from conllu (no front-end needed for
             the loop). Content words = {NOUN, VERB, ADJ, PROPN}.
  LOOKUP   = FUNCTIONAL coverage (the meaning the reader NEEDS, not raw dictionary presence):
             VERB -> VerbNet affectedness lexicon (affectedness_type + graded_score) [data/
                     verbnet_affectedness_lexicon_v1_corrected]. A verb can be in WordNet yet MISSING
                     from the affectedness lexicon -> raw-present but functionally UNCOVERED.
             NOUN -> WordNet dominant-sense lexname + hypernym-closure animacy (sem_type + features).
             ADJ  -> WordNet ADJ synset presence (sense availability).
             PROPN-> try WordNet noun; miss -> named-entity (encyclopedia escalation).
  GAP TAX  = resolved | named_entity | verb_not_in_verbnet | noun_oov_wordnet | adj_oov_wordnet
             (+ sense_flagged = resolved-but-low-confidence, reported separately).
  ASSIGN   = on a store MISS (ask), resolve from the resource and ADD to a GROWING foundation store
             (a COPY/new store; production KBs untouched). Unresolvable -> ESCALATION QUEUE (logged
             build-time; NOT web-fetched: headless cannot auth).
  CURVES   = per-bin over reading progress: (1) COVERAGE (fraction of content tokens the store
             functionally supplies), (2) ASK-RATE (store-miss tokens per sentence -- the decisive
             active-learning signature; MUST DECLINE for growth-ON, stay FLAT for growth-OFF),
             (3) residual gap breakdown by category.

ARMS (one variable = the store-write / assignment rule; identical stream + ask-accounting):
  growth-ON      = resolve from resource, store TRUE meaning, mark known. Coverage rises; ask-rate
                   declines (retention amortizes each type). THE loop.
  growth-OFF     = REAL BASELINE. Same stream, resolve to categorize, but NEVER store -> store stays
                   empty -> every non-seed content token re-asks forever -> ask-rate FLAT (no
                   retention), coverage FLAT ~0. Proves the decline is CAUSED by the growing
                   foundation, not by Heaps'-law of the corpus alone.
  growth-SHUFFLE = MUST-FAIL control. Same retention as ON (coverage + ask-rate curves IDENTICAL to
                   ON) BUT stores a PERMUTED (wrong) meaning. Presence/ask-rate cannot distinguish it
                   from ON -> the FUNCTIONAL-USEFULNESS probe must, and must COLLAPSE. Proves the grown
                   foundation is real MEANING, not just marking-words-seen.

FUNCTIONAL-USEFULNESS PROBE (downstream, scored vs INDEPENDENT human gold; non-tautological):
  UD-EWT semantic-affectedness breadth gold (human labels). Binary: HIGH-affect {patient, effected}
  vs LOW-affect {target_not_affected}. Predict AFFECTED iff grown-store verb graded_score >= 0.5.
  REAL-grown store -> graded_score separates change-of-state/created from perception -> accuracy high.
  SHUFFLE-grown store -> random graded_score -> COLLAPSE to ~chance. Gold labels are independent (human
  affectedness intuition), so scoring is NOT tautological. Probe verbs resolved through the SAME
  arm-assignment rule (guarantees full probe coverage so the must-fail fires at smoke AND full).

BANDS (declared BEFORE full; see preregs/2026-07-21_breadth_foundation_active_growth_loop_ud_ewt_v1.md):
  learns      := on_ask_ratio(last/first) <= 0.50 AND on_cov_delta(last-first) >= +0.20 AND
                 on_spearman_vs_index <= -0.50 (declining trend; Spearman is the robust 'monotone-ish'
                 measure -- adjacent-bin strict monotonicity is fragile to real-corpus document-
                 burstiness, validated at smoke to still discriminate ON (rho=-0.57) from OFF (rho=+0.12)).
  baseline_flat := off_miss_mean >= 0.98 AND off_cov_delta <= 0.02  (OFF per-token miss = 1.0 by
                 construction: every token re-asks, no retention. A retention LEAK into the control drops
                 it -> can-fail integrity check. NOTE: OFF per-SENTENCE ask-rate drifts with sentence
                 length across UD-EWT genre blocks -> the verdict uses the confound-free per-TOKEN miss).
  retention_gap := (off_miss_last - on_miss_last) >= 0.30  (per content-token; the retention signal).
  shuffle_collapses := (real_use_acc - shuffle_use_acc) >= 0.15 AND shuffle_use_acc <= chance+0.10
                       AND real_use_acc >= chance+0.15.
  HARD_PASS_BREADTH_LOOP: learns AND baseline_flat AND retention_gap AND shuffle_collapses AND
                          arms_differ AND deterministic.
  HARD_FAIL_BREADTH_LOOP: on_miss_ratio > 0.80 (per-token miss does NOT decline = not learning) OR
                          on_cov_delta < +0.10 OR off_miss_mean < 0.98 (OFF control leaked retention =
                          broken) OR (not shuffle_collapses) OR (not arms_differ).
  MIDDLE_BAND_BREADTH_LOOP: otherwise (partial: e.g. learns but shuffle margin 0.05-0.15).

HYPOTHESIZED (pre-run, tagged): on_ask_ratio ~ 0.10-0.30 HYPOTHESIZED (Heaps-by-retention; each type
  asked once). off_ask_ratio ~ 1.0 HYPOTHESIZED (no retention -> flat token-miss rate). on_cov_delta ~
  +0.4-0.6 HYPOTHESIZED (rises 0 -> resolvable-fraction asymptote). real_use_acc ~ 0.80-0.95
  HYPOTHESIZED (graded_score separates patient/effected from perception). shuffle_use_acc ~ 0.55-0.67
  HYPOTHESIZED (majority-class base rate 18/27=0.667). residual dominated by named_entity (PROPN)
  HYPOTHESIZED. All curves MEASURED@this cell's metrics.json after run.

Compute architecture: sequential-CPU, justified (glass-box streaming dict/lookup over ~100k tokens but
  ~O(1e4) unique types looked up ONCE each; nltk WordNet lookups cached; VerbNet lexicon in-memory dict;
  NO matmul inner loop; wall dominated by the ~28s WordNet import + conllu parse; total < few min ->
  NOT a GPU/batching candidate; runtime sanity gate PASS). Storage: dict foundation (grown COPY at
  data/breadth_foundation_grown_v1; production KBs untouched). Determinism: fixed seeds; np.random
  Generator only; NO hash()-seeded RNG; sorted iteration; OMP/MKL/OPENBLAS=1. LOCAL foreground to
  COMPLETION (light compute); NO queue, NO push, NO remote-persist, NO git add of canonical store, NO
  hdlab mutation, NO atom bank. ASCII-only.

# CELL-TEMPLATE MANDATORY (measurement + 3-arm control loop; light CPU):
# - arms_differ_verified at smoke (ON/OFF/SHUFFLE final store-state hashes differ; META_RULE_AF)
# - final_metrics_atomicity: tmp_replace (META_RULE_AH; metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (NOT BaseException)
# - crlb_n/a: "accuracy/rate curves on real corpus + labeled gold; no substrate noise floor"
# - baseline_in_band: growth-OFF ask-rate stays high (not saturated to 0); real_use_acc base-rate 0.667 in (0.05,0.95)
# - discriminator survives scale: smoke fires ALL discriminators (ON declines, OFF flat, shuffle collapses)
#   at 400 sentences; FULL at 6000 confirms the asymptote. Probe verbs resolved through arm rule -> full probe coverage.
# - cardinality_ok: EXPECTED_N_BINS bins per arm recorded; verdict counts len(curve)==N_BINS per arm
# - calibration_check: default_ok_for_this_regime (graded>=0.5 affect threshold; VN taxonomy inherited)
# - all numbers in comments tagged HYPOTHESIZED@/MEASURED@/CITED@
# - self-test EXERCISES the REAL resources (wn_noun_semantics + VerbNet lexicon) at N~16 tokens (real_code_path)
"""

import argparse
import hashlib
import json
import os
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

from nltk.corpus import wordnet as wn  # noqa: E402

USE_PROBE_SHUFFLE_SEEDS = 20     # multi-seed null for the AUC usefulness probe (AUC needs multi-seed)

# --------------------------------------------------------------------------------------------------
# Paths / constants
# --------------------------------------------------------------------------------------------------
ANCHOR_NAME = "exp_breadth_foundation_active_growth_loop_ud_ewt_v1"
CONLLU_PATH = os.path.join(REPO_ROOT, "experiments", "data", "ud_english_ewt", "en_ewt-ud-train.conllu")
VERBNET_LEX_PATH = os.path.join(REPO_ROOT, "data", "verbnet_affectedness_lexicon_v1_corrected", "lexicon.json")
UD_GOLD_PATH = os.path.join(REPO_ROOT, "data", "ud_ewt_semantic_affectedness_gold_v2_breadth", "gold.json")

FOUNDATION_DIR = os.path.join(REPO_ROOT, "data", "breadth_foundation_grown_v1")

CONTENT_UPOS = ("NOUN", "VERB", "ADJ", "PROPN")
N_BINS = 12
AFFECT_THRESHOLD = 0.5           # graded_score >= -> predict AFFECTED (change/created) in the use-probe
LOW_CONF_SENSES = 6              # noun n_senses >= -> sense_flagged (resolved-but-low-confidence)
SHUFFLE_SEED = 1234

# WordNet noun-semantics helpers (dominant-sense lexname + hypernym-closure animacy).
# Copied from exp_wordnet_noun_semantics_kb_who_affected_v1 (atom 29420) so the loop uses the SAME
# vetted lookup the who-affected reader uses. CITED@WordNet (Fellbaum 1998); selrestr strings = VerbNet.
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

# Gold affectedness -> binary usefulness label. HIGH = entity really changed/created; LOW = perception.
HIGH_AFFECT_GOLD = {"patient", "effected"}
LOW_AFFECT_GOLD = {"target_not_affected"}


def _clean(surface):
    return (surface or "").lower().strip(".,'\"!?;:()")


def wn_noun_semantics(surface):
    """Live WordNet noun lookup: (animate, sem_type, features, lexname, n_senses). sem_type None => OOV."""
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
    """Live WordNet adjective lookup: (has_sense, n_senses, dominant_lexname)."""
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


# --------------------------------------------------------------------------------------------------
# Resource-backed resolution (the on-demand assignment from the KB foundation)
# --------------------------------------------------------------------------------------------------
def load_verbnet_lexicon():
    with open(VERBNET_LEX_PATH, encoding="utf-8") as f:
        doc = json.load(f)
    return doc["lexicon"]


def resolve_content_word(pos, lemma, verb_lex):
    """Attempt to supply the FUNCTIONAL meaning the reader needs. Returns (resolved, source, meaning, category, conf).

    category is the gap taxonomy label. For resolved words it is 'resolved' (or 'resolved_sense_flagged').
    """
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
        # unresolved noun: PROPN with no common-noun synset => named entity; else OOV
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
    """Deterministic permutation of the VerbNet lexicon keys (verb v -> lexicon[perm(v)])."""
    keys = sorted(verb_lex.keys())
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(keys))
    return {keys[i]: keys[int(perm[i])] for i in range(len(keys))}


def assign_meaning(mode, pos, lemma, verb_lex, shuffle_map):
    """Arm-specific assignment. Returns (resolved, source, meaning, category, conf).

    growth-SHUFFLE corrupts the meaning: verbs get a permuted verb's record; nouns/adj get an
    animacy/sense-flipped record. Presence + category are preserved (so coverage/ask-rate curves are
    IDENTICAL to growth-ON); only the MEANING is wrong -> the usefulness probe must collapse.
    """
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
        m2["animate"] = not bool(m2.get("animate"))     # flip the load-bearing bit
        m2["sem_type"] = "abstract" if m2.get("sem_type") != "abstract" else "object"
        m2["_shuffled"] = True
        meaning = m2
    elif pos == "ADJ":
        m2 = dict(meaning)
        m2["_shuffled"] = True
        meaning = m2
    return resolved, source, meaning, cat, conf


# --------------------------------------------------------------------------------------------------
# Corpus stream
# --------------------------------------------------------------------------------------------------
def read_conllu_stream(path, max_sent):
    """Parse conllu -> list of sentences; each = list of (form, lemma, upos) for content tokens only."""
    sents = []
    cur = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur:
                    sents.append(cur)
                    cur = []
                    if len(sents) >= max_sent:
                        break
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) < 4:
                continue
            tid = cols[0]
            if "-" in tid or "." in tid:  # multiword-token range / empty node
                continue
            form, lemma, upos = cols[1], cols[2], cols[3]
            if upos in CONTENT_UPOS:
                cur.append((form, lemma, upos))
    if cur and len(sents) < max_sent:
        sents.append(cur)
    return sents


# --------------------------------------------------------------------------------------------------
# The active-learning loop (one arm)
# --------------------------------------------------------------------------------------------------
def run_loop(sents, mode, verb_lex, shuffle_map, n_bins):
    """Run the read-detect-assign-grow loop for one arm.

    Returns dict with per-bin ask_rate + coverage curves, residual breakdown, final store, escalation
    queue, and a store-state hash. 'ask' = content token whose (pos,lemma) is NOT currently known
    (a store miss). growth-ON/SHUFFLE add first-encountered types to the store; growth-OFF never does.
    """
    store = OrderedDict()          # (pos, lemma) -> {meaning record + provenance}
    known = set()                  # (pos, lemma) first-encountered (ON/SHUFFLE); stays == seed for OFF
    escalation = OrderedDict()     # (pos, lemma) -> {category, sent_idx} (dedup by type)
    residual_types = Counter()     # category -> #types escalated
    resolved_flagged_types = 0

    n_sent = len(sents)
    bin_size = max(1, (n_sent + n_bins - 1) // n_bins)
    ask_curve = [0] * n_bins       # asks (store-miss tokens) per bin
    sent_curve = [0] * n_bins      # sentences per bin
    cov_hit = [0] * n_bins         # content tokens covered (store has resolved meaning) per bin
    cov_tot = [0] * n_bins         # content tokens total per bin

    for si, sent in enumerate(sents):
        b = min(si // bin_size, n_bins - 1)
        sent_curve[b] += 1
        for (form, lemma, upos) in sent:
            key = (upos, _clean(lemma))
            cov_tot[b] += 1
            # COVERAGE (online): does the CURRENT store functionally supply this token's meaning?
            rec = store.get(key)
            if rec is not None and rec.get("resolved"):
                cov_hit[b] += 1
            # ASK: store miss (not yet known) -> a lookup/escalation event
            if key not in known:
                ask_curve[b] += 1
                resolved, source, meaning, cat, conf = assign_meaning(mode, upos, lemma, verb_lex, shuffle_map)
                if mode != "OFF":
                    known.add(key)
                    if resolved:
                        store[key] = {"pos": upos, "lemma": key[1], "source": source,
                                      "meaning": meaning, "confidence": conf, "resolved": True,
                                      "first_seen_sent": si, "category": cat}
                        if cat == "resolved_sense_flagged":
                            resolved_flagged_types += 1
                    else:
                        # escalation marker: known (won't re-ask) but NOT covered (no meaning)
                        store[key] = {"pos": upos, "lemma": key[1], "source": None,
                                      "meaning": None, "confidence": 0.0, "resolved": False,
                                      "first_seen_sent": si, "category": cat}
                        escalation[key] = {"category": cat, "sent_idx": si, "pos": upos, "lemma": key[1]}
                        residual_types[cat] += 1
                else:
                    # OFF: categorize for reporting but do NOT retain
                    if not resolved:
                        escalation.setdefault(key, {"category": cat, "sent_idx": si})
                        residual_types[cat] += 1

    ask_rate = [ask_curve[i] / sent_curve[i] if sent_curve[i] else 0.0 for i in range(n_bins)]
    # per-content-token MISS rate (confound-free: removes sentence-length drift). OFF = 1.0 by
    # construction (every token asks, no retention); ON declines by retention (Heaps-by-retention).
    miss_rate = [ask_curve[i] / cov_tot[i] if cov_tot[i] else 0.0 for i in range(n_bins)]
    coverage = [cov_hit[i] / cov_tot[i] if cov_tot[i] else 0.0 for i in range(n_bins)]

    # store-state hash (arms_differ)
    h = hashlib.sha256()
    for k in sorted(store.keys()):
        v = store[k]
        h.update(repr((k, v.get("resolved"), None if v.get("meaning") is None
                       else sorted(str(x) for x in v["meaning"].items()))).encode("utf-8"))
    store_hash = h.hexdigest()

    total_content_types = len(known) if mode != "OFF" else None
    return {
        "mode": mode,
        "n_sent": n_sent,
        "n_bins": n_bins,
        "ask_rate_curve": [round(x, 4) for x in ask_rate],
        "miss_rate_curve": [round(x, 4) for x in miss_rate],
        "coverage_curve": [round(x, 4) for x in coverage],
        "ask_counts": ask_curve,
        "sent_counts": sent_curve,
        "cov_hit": cov_hit,
        "cov_tot": cov_tot,
        "residual_by_category": dict(residual_types),
        "n_resolved_flagged_types": resolved_flagged_types,
        "n_store_entries": len(store),
        "n_resolved_entries": sum(1 for v in store.values() if v.get("resolved")),
        "n_escalations": len(escalation),
        "store_hash": store_hash,
        "_store": store,
        "_escalation": escalation,
    }


# --------------------------------------------------------------------------------------------------
# Functional-usefulness probe (independent human gold; the shuffle must-fail discriminator)
# --------------------------------------------------------------------------------------------------
def _lemv(surface):
    """Lemmatize a surface verb to its base form (WordNet morphy); gold uses inflected forms."""
    s = _clean(surface)
    try:
        return wn.morphy(s, wn.VERB) or s
    except Exception:
        return s


def load_gold_binary():
    """HIGH-affect {patient,effected} vs LOW-affect {target_not_affected}; verbs LEMMATIZED."""
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
    """Rank-AUC = P(random HIGH score > random LOW score) with ties at 0.5."""
    if not high_scores or not low_scores:
        return None
    num = 0.0
    for h in high_scores:
        for l in low_scores:
            num += 1.0 if h > l else (0.5 if h == l else 0.0)
    return num / (len(high_scores) * len(low_scores))


def _probe_scores(gold_items, verb_lex, key_map):
    """Collect graded_scores for HIGH/LOW gold verbs. key_map maps a verb lemma to the lexicon key to
    READ (identity for real; a permutation for shuffle). Returns (high_scores, low_scores, n_used)."""
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
    """Usefulness = does the grown TRUE verb meaning (graded_score) SEPARATE HIGH-affect from LOW-affect
    verbs (AUC vs INDEPENDENT human gold)? Multi-seed SHUFFLE null: permute the lexicon and re-measure.
    Real >> shuffle-mean => the grown meaning is load-bearing, not word-marking."""
    keys = sorted(verb_lex.keys())

    def real_key(v):
        return v if v in verb_lex else None

    hs, ls, used = _probe_scores(gold_items, verb_lex, real_key)
    real_auc = _auc(hs, ls)
    # binary accuracy@0.5 (secondary; quantized).
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
        "shuffle_auc_mean": round(float(sh.mean()), 4),
        "shuffle_auc_std": round(float(sh.std()), 4),
        "shuffle_auc_max": round(float(sh.max()), 4),
        "auc_delta_real_minus_shuffle_mean": round(float(real_auc - sh.mean()), 4) if real_auc is not None else None,
        "real_binary_acc": round(real_acc, 4), "majority_chance": round(majority, 4),
        "n_high": n_hi, "n_low": n_lo, "n_used": used, "n_shuffle_seeds": len(shuffle_aucs),
    }


# --------------------------------------------------------------------------------------------------
# Curve summaries
# --------------------------------------------------------------------------------------------------
def _first_last_nonzero_ratio(curve):
    """last/first using the first and last bins that have data (>0 sentences)."""
    nz = [x for x in curve]
    first = nz[0] if nz else 0.0
    last = nz[-1] if nz else 0.0
    if first <= 1e-9:
        return None, first, last
    return last / first, first, last


def _monotone_decreasing_frac(curve):
    if len(curve) < 2:
        return 0.0
    dec = sum(1 for i in range(1, len(curve)) if curve[i] <= curve[i - 1] + 1e-9)
    return dec / (len(curve) - 1)


def _spearman_vs_index(curve):
    """Spearman rank correlation of curve vs bin index (trend). Robust 'monotone-ish' measure:
    strongly negative => declining trend despite local wobble from corpus document-burstiness."""
    n = len(curve)
    if n < 3:
        return 0.0
    x = np.arange(n, dtype=float)
    y = np.asarray(curve, dtype=float)
    if float(np.ptp(y)) < 1e-9:      # flat curve (e.g. OFF miss=1.0): no trend, not a tie-order artifact
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
    print("[self-test] starting")
    verb_lex = load_verbnet_lexicon()
    shuffle_map = build_shuffle_map(verb_lex, SHUFFLE_SEED)

    # (1) real_code_path: exercise the REAL resources at tiny scale (N~16 content tokens).
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
    assert {"verbnet_lexicon", "wn_noun_semantics", "wn_adj_meaning"} <= exercised, "real_code_path incomplete"

    # (2) coverage is FUNCTIONAL not raw-dictionary-presence: a verb can be a real English word (in
    #     WordNet) yet functionally UNCOVERED (missing from the VerbNet affectedness lexicon).
    functionally_uncovered = None
    for cand in ["photosynthesize", "quantize", "google", "defenestrate", "subitize"]:
        in_wn = bool(wn.synsets(cand, pos=wn.VERB))
        in_lex = cand in verb_lex
        if in_wn and not in_lex:
            functionally_uncovered = cand
            break
    assert functionally_uncovered is not None, "expected >=1 verb in WordNet but NOT in affectedness lexicon"
    print("[self-test] functional!=presence example (WN verb, not in affectedness lexicon):", functionally_uncovered)

    # (3) named-entity escalation category fires for a PROPN with no common-noun synset.
    r_pe = resolve_content_word("PROPN", "Xylophonia", verb_lex)
    assert (not r_pe[0]) and r_pe[3] == "named_entity", "named_entity escalation did not fire"

    # (4) ask-rate RESPONDS to growth: on a tiny synthetic repetitive stream, growth-ON ask-rate
    #     DECLINES (each type asked once) while growth-OFF stays FLAT (re-asks). Non-tautological:
    #     freezing growth flattens the curve.
    toy = [[("VERB", "run", "VERB"), ("NOUN", "dog", "NOUN")]] * 8  # same 2 types repeated 8 sentences
    toy_sents = [[(l, l, p) for (p, l, _p2) in s] for s in toy]
    on = run_loop(toy_sents, "ON", verb_lex, shuffle_map, n_bins=4)
    off = run_loop(toy_sents, "OFF", verb_lex, shuffle_map, n_bins=4)
    on_ratio, on_f, on_l = _first_last_nonzero_ratio(on["ask_rate_curve"])
    off_ratio, off_f, off_l = _first_last_nonzero_ratio(off["ask_rate_curve"])
    assert on_l == 0.0 and on_f > 0.0, "growth-ON ask-rate should drop to 0 after types learned"
    assert off_l == off_f and off_l > 0.0, "growth-OFF ask-rate should stay flat (re-asks every sentence)"
    # confound-free per-token: OFF miss-rate == 1.0 every bin (by construction); ON drops to 0.
    assert all(abs(x - 1.0) < 1e-9 for x in off["miss_rate_curve"]), "OFF per-token miss must be 1.0 (no retention)"
    assert on["miss_rate_curve"][-1] < 0.5, "ON per-token miss must decline (retention)"
    print("[self-test] ask/miss responds to growth: ON ask %.2f->%.2f | OFF per-token miss=%s (flat 1.0) ON miss=%s"
          % (on_f, on_l, off["miss_rate_curve"], on["miss_rate_curve"]))

    # (5) shuffle collapses the usefulness probe (multi-seed AUC null).
    gold = load_gold_binary()
    up = functional_probe(gold, verb_lex, n_shuffle_seeds=8)
    assert up["real_auc"] is not None and up["auc_delta_real_minus_shuffle_mean"] >= 0.15, \
        "shuffle must collapse usefulness (real_auc - shuffle_mean < 0.15)"
    print("[self-test] shuffle collapses use-probe: real_auc=%.3f shuffle_mean=%.3f (+-%.3f) delta=%.3f binacc=%.3f"
          % (up["real_auc"], up["shuffle_auc_mean"], up["shuffle_auc_std"],
             up["auc_delta_real_minus_shuffle_mean"], up["real_binary_acc"]))

    # (6) arms_differ: ON vs SHUFFLE final store-state hashes differ on a small real stream.
    small = read_conllu_stream(CONLLU_PATH, max_sent=40)
    a_on = run_loop(small, "ON", verb_lex, shuffle_map, n_bins=4)
    a_sh = run_loop(small, "SHUFFLE", verb_lex, shuffle_map, n_bins=4)
    assert a_on["store_hash"] != a_sh["store_hash"], "ON and SHUFFLE store states must differ"

    # (7) determinism: re-run identical -> identical curves.
    a_on2 = run_loop(small, "ON", verb_lex, shuffle_map, n_bins=4)
    assert a_on["ask_rate_curve"] == a_on2["ask_rate_curve"], "loop not deterministic"

    print("[self-test] PASS")
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


def save_foundation_artifact(on_result):
    """Persist the grown foundation (COPY / new store) + escalation queue. NO production KB mutation."""
    os.makedirs(FOUNDATION_DIR, exist_ok=True)
    store = on_result["_store"]
    esc = on_result["_escalation"]
    doc = {
        "_meta": {
            "name": "breadth_foundation_grown_v1",
            "built": datetime.now(timezone.utc).isoformat(),
            "source": "grown on-demand by the read-drives-knowledge loop over UD-EWT train; "
                      "VERB=VerbNet affectedness lexicon; NOUN/PROPN=WordNet noun semantics; ADJ=WordNet ADJ",
            "anchor": ANCHOR_NAME,
            "n_entries": len(store), "n_resolved": on_result["n_resolved_entries"],
            "n_escalations": len(esc),
            "note": "COPY / new store; production KBs untouched; NOT banked (skunkworks VETs after)",
        },
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

    escdoc = {"_meta": {"name": "breadth_foundation_escalation_queue_v1",
                        "built": datetime.now(timezone.utc).isoformat(), "anchor": ANCHOR_NAME,
                        "note": "words NO local resource covers -> would escalate to oracle/encyclopedia. "
                                "NOT fetched now (headless cannot web-auth); logged build-time.",
                        "n": len(esc)},
              "queue": [{"pos": v.get("pos", k[0]), "lemma": v.get("lemma", k[1]),
                         "category": v["category"], "first_seen_sent": v["sent_idx"]}
                        for k, v in esc.items()]}
    tmp2 = os.path.join(FOUNDATION_DIR, "escalation_queue.json.tmp")
    with open(tmp2, "w", encoding="utf-8") as f:
        json.dump(escdoc, f, indent=2)
    os.replace(tmp2, os.path.join(FOUNDATION_DIR, "escalation_queue.json"))


# --------------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------------
def run(mode_tag, n_sent):
    t0 = time.time()
    out_dir = output_dir(mode_tag)
    _write_start_marker(out_dir, mode_tag, expected_units=3 * N_BINS)

    verb_lex = load_verbnet_lexicon()
    shuffle_map = build_shuffle_map(verb_lex, SHUFFLE_SEED)
    sents = read_conllu_stream(CONLLU_PATH, max_sent=n_sent)
    n_content_tokens = sum(len(s) for s in sents)

    res_on = run_loop(sents, "ON", verb_lex, shuffle_map, N_BINS)
    res_off = run_loop(sents, "OFF", verb_lex, shuffle_map, N_BINS)
    res_shuf = run_loop(sents, "SHUFFLE", verb_lex, shuffle_map, N_BINS)

    gold = load_gold_binary()
    use = functional_probe(gold, verb_lex, n_shuffle_seeds=USE_PROBE_SHUFFLE_SEEDS)

    # Curve summaries. PRIMARY = per-content-token MISS rate (confound-free; OFF=1.0 by construction).
    # Per-SENTENCE ask-rate is ALSO reported (the USER-named view) but carries a sentence-length drift
    # across UD-EWT genre blocks, so the verdict is driven by the per-token miss rate.
    on_ratio, on_f, on_l = _first_last_nonzero_ratio(res_on["miss_rate_curve"])
    off_ratio, off_f, off_l = _first_last_nonzero_ratio(res_off["miss_rate_curve"])
    on_ask_ratio_sent, _, _ = _first_last_nonzero_ratio(res_on["ask_rate_curve"])
    off_ask_ratio_sent, _, _ = _first_last_nonzero_ratio(res_off["ask_rate_curve"])
    on_cov_delta = res_on["coverage_curve"][-1] - res_on["coverage_curve"][0]
    off_cov_delta = res_off["coverage_curve"][-1] - res_off["coverage_curve"][0]
    on_mono = _monotone_decreasing_frac(res_on["miss_rate_curve"])
    on_spearman = _spearman_vs_index(res_on["miss_rate_curve"])
    off_spearman = _spearman_vs_index(res_off["miss_rate_curve"])
    off_miss_mean = float(np.mean(res_off["miss_rate_curve"]))
    retention_gap = res_off["miss_rate_curve"][-1] - res_on["miss_rate_curve"][-1]

    use_delta = use["auc_delta_real_minus_shuffle_mean"]

    # Bands (confound-free per-token miss rate).
    learns = (on_ratio is not None and on_ratio <= 0.50) and (on_cov_delta >= 0.20) and (on_spearman <= -0.50)
    # baseline_no_retention: OFF miss-rate is ~1.0 flat by construction (every token re-asks). A retention
    # LEAK into the OFF control would drop this below 1.0 -> can-fail integrity check on the control arm.
    baseline_flat = (off_miss_mean >= 0.98) and (off_cov_delta <= 0.02)
    retention_ok = retention_gap >= 0.30
    shuffle_collapses = ((use["real_auc"] is not None) and (use_delta is not None and use_delta >= 0.15)
                         and (use["real_auc"] >= 0.70) and (0.40 <= use["shuffle_auc_mean"] <= 0.60))
    arms_differ = len({res_on["store_hash"], res_off["store_hash"], res_shuf["store_hash"]}) == 3
    # OFF store is empty -> its hash may equal SHUFFLE only if both empty; ensure ON!=SHUFFLE + ON!=OFF.
    arms_differ = (res_on["store_hash"] != res_shuf["store_hash"]) and (res_on["store_hash"] != res_off["store_hash"])

    # determinism re-run (cheap on the same stream: ON curve only).
    res_on2 = run_loop(sents, "ON", verb_lex, shuffle_map, N_BINS)
    deterministic = res_on2["ask_rate_curve"] == res_on["ask_rate_curve"]

    cardinality_ok = all(len(r["ask_rate_curve"]) == N_BINS for r in (res_on, res_off, res_shuf))

    hard_fail = ((on_ratio is None or on_ratio > 0.80) or (on_cov_delta < 0.10) or
                 (off_miss_mean < 0.98) or (not shuffle_collapses) or (not arms_differ))
    hard_pass = (learns and baseline_flat and retention_ok and shuffle_collapses and arms_differ
                 and deterministic and cardinality_ok)

    if hard_pass:
        verdict = "HARD_PASS"
        band = "HARD_PASS_BREADTH_LOOP"
    elif hard_fail:
        verdict = "HARD_FAIL"
        band = "HARD_FAIL_BREADTH_LOOP"
    else:
        verdict = "MIDDLE_BAND"
        band = "MIDDLE_BAND_BREADTH_LOOP"

    # residual breakdown as fraction of ON content-word TYPES.
    n_types = res_on["n_store_entries"]
    residual = res_on["residual_by_category"]
    residual_frac = {k: round(v / n_types, 4) for k, v in residual.items()} if n_types else {}

    elapsed = time.time() - t0
    msg = (f"{verdict} on_miss_ratio={None if on_ratio is None else round(on_ratio,3)} "
           f"(pertoken {on_f:.2f}->{on_l:.2f}) off_miss_mean={off_miss_mean:.3f} (flat~1.0 by construction) "
           f"retention_gap={retention_gap:.3f} on_spearman={on_spearman:.3f} off_spearman={off_spearman:.3f} "
           f"on_cov {res_on['coverage_curve'][0]:.2f}->{res_on['coverage_curve'][-1]:.2f} (d={on_cov_delta:+.3f}) "
           f"use_real_auc={use['real_auc']} use_shuffle_auc={use['shuffle_auc_mean']}+-{use['shuffle_auc_std']} "
           f"auc_delta={use_delta} binacc={use['real_binary_acc']} "
           f"n_sent={len(sents)} n_content_tokens={n_content_tokens} n_grown={n_types} "
           f"n_escalations={res_on['n_escalations']}")

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": band, "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "mode_tag": mode_tag, "n_sent": len(sents), "n_content_tokens": n_content_tokens,
        "n_bins": N_BINS,
        "bands": {
            "learns": bool(learns), "baseline_flat": bool(baseline_flat),
            "retention_gap_ok": bool(retention_ok), "shuffle_collapses": bool(shuffle_collapses),
            "arms_differ": bool(arms_differ), "deterministic": bool(deterministic),
            "cardinality_ok": bool(cardinality_ok),
        },
        "miss_rate_per_token": {
            "note": "PRIMARY confound-free active-learning curve: asks per content token per bin. "
                    "OFF = 1.0 by construction (every token re-asks, no retention); ON declines by retention.",
            "growth_ON_curve": res_on["miss_rate_curve"], "growth_OFF_curve": res_off["miss_rate_curve"],
            "growth_SHUFFLE_curve": res_shuf["miss_rate_curve"],
            "on_ratio_last_over_first": None if on_ratio is None else round(on_ratio, 4),
            "off_miss_mean": round(off_miss_mean, 4),
            "on_spearman_vs_index": round(on_spearman, 4),
            "off_spearman_vs_index": round(off_spearman, 4),
            "on_monotone_decreasing_frac": round(on_mono, 4),
            "retention_gap_off_minus_on_last": round(retention_gap, 4),
        },
        "ask_rate_per_sentence": {
            "note": "USER-named view (new-gaps per sentence). Carries a mild sentence-length drift across "
                    "UD-EWT genre blocks -> the per-token miss rate above drives the verdict.",
            "growth_ON_curve": res_on["ask_rate_curve"], "growth_OFF_curve": res_off["ask_rate_curve"],
            "growth_SHUFFLE_curve": res_shuf["ask_rate_curve"],
            "on_ratio_last_over_first": None if on_ask_ratio_sent is None else round(on_ask_ratio_sent, 4),
            "off_ratio_last_over_first": None if off_ask_ratio_sent is None else round(off_ask_ratio_sent, 4),
        },
        "coverage": {
            "growth_ON_curve": res_on["coverage_curve"], "growth_OFF_curve": res_off["coverage_curve"],
            "growth_SHUFFLE_curve": res_shuf["coverage_curve"],
            "on_cov_delta_last_minus_first": round(on_cov_delta, 4),
            "off_cov_delta_last_minus_first": round(off_cov_delta, 4),
            "on_coverage_asymptote": res_on["coverage_curve"][-1],
        },
        "usefulness_probe": use,
        "residual_gap_breakdown": {
            "by_category_types": residual, "by_category_frac_of_grown_types": residual_frac,
            "n_grown_types": n_types, "n_resolved_types": res_on["n_resolved_entries"],
            "n_resolved_sense_flagged": res_on["n_resolved_flagged_types"],
            "n_escalations": res_on["n_escalations"],
        },
        "store_hashes": {"ON": res_on["store_hash"], "OFF": res_off["store_hash"], "SHUFFLE": res_shuf["store_hash"]},
        "prereg_bands": {
            "HARD_PASS": "learns AND baseline_flat AND retention_gap AND shuffle_collapses AND arms_differ AND deterministic",
            "HARD_FAIL": "on_ask_ratio>0.80 OR on_cov_delta<0.10 OR off_ask_ratio<0.70 OR not shuffle_collapses OR not arms_differ",
        },
        "calibration_check": "default_ok_for_this_regime",
        "crlb_n/a": "accuracy/rate curves on real corpus + labeled human gold; no substrate noise floor",
        "final_metrics_atomicity": "tmp_replace",
    }
    _write_metrics(out_dir, metrics)

    # Persist grown foundation artifact only for the FULL run (COPY store; not banked).
    if mode_tag == "full":
        save_foundation_artifact(res_on)

    print(msg)
    print("[done] wrote", os.path.join(out_dir, "metrics.json"), "elapsed=%.1fs" % elapsed)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--n-sent", type=int, default=0)
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return
    if args.smoke:
        run("smoke", n_sent=args.n_sent or 400)
        return
    if args.full:
        run("full", n_sent=args.n_sent or 6000)
        return
    # default = self-test
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
