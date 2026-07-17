"""exp_read_grow_foundation_realprose_glassbox_ie_v1 -- THE SUBSTANTIVE READING STEP.

The read->grow JOIN (exp_read_grow_foundation_endtoend_v1) passed, but its "reading" was a hardcoded
POSITIONAL SVO parser over pre-cleaned known-vocab TUPLES (extraction_acc = 1.0 by construction). That is a
stub. This cell takes the real step: a GLASS-BOX, RULE-BASED IE parser (deterministic symbolic rules over
syntactic structure -- ReVerb / ClausIE / SRL-style; NO LLM) over REAL simple PROSE (actual English sentences,
not pre-cleaned tuples) -> extract (s, r, o) triples -> feed the PROVEN learned-lexicon + ingest-gate + grow a
foundation. This is the USER's glass-box-reading-no-LLM north star made real.

WHAT CHANGES vs v1 (and what is REUSED VERBATIM):
  REPLACED: the input is now a REAL-PROSE corpus (`PROSE_CORPUS`: real sentences + a ground-truth triple per
            sentence), and the parse step is a real symbolic IE extractor (`ie_extract`) -- POS-lexicon tagging
            (closed-class function words + a content lexicon + morphology) then deterministic pattern rules
            (active SVO / SVO+prep / continuous / passive / coordination) over the tag sequence.
  REUSED VERBATIM (imported from v1, genuine reuse not rebuild): the LEARNED LEXICON (word->concept), the
            INGEST GATE (schema-fit / provisional-hold / novelty), the growing SHARDED VSA FoundationStore, the
            role-filler SVO encode/decode, and the type foundation. See imports below.

GLASS-BOX / NO-LLM (load-bearing honesty): the parser is FULLY SYMBOLIC. No neural dependency parser, no LLM.
  The POS lexicon injects SYNTACTIC STRUCTURE (word classes: which token is a determiner / verb / noun), NOT
  FACTS. Closed-class words (DET / PREP / CONJ / AUX / ADV) are genuinely finite in English; open-class content
  words use a small lexicon + productive morphology (plural -s, gerund -ing, 3sg -s). The parser CANNOT
  hallucinate a fact -- it can only MIS-APPLY a rule (produce a wrong or no triple). A general system would
  swap the hand lexicon for a learned/statistical POS tagger; that is the SCALE-UP, not a different mechanism.

HONEST EXPECTATION (the POINT of this cell): glass-box IE is NOISIER than an LLM. Coverage / correctness will
  be MODEST vs the positional stub's 1.0. That is exactly the trade -- CONTROL + TRANSPARENCY vs COVERAGE, and
  the INGEST GATE is what cleans up the parser's noise (type-violating misfires get rejected; benign duplicate
  misfires are harmless). Coverage is reported HONESTLY, per sentence-structure class, so the failure envelope
  IS the deliverable. Do NOT over-read a cherry-picked easy subset as "reads prose".

METRICS (reported SEPARATELY):
  (a) EXTRACTION on real prose (seed-independent, pure parser):
        parser_coverage       = fraction of sentences yielding ANY well-formed triple
        parser_precision       = fraction of YIELDED triples that are CORRECT (== ground truth)
        parser_correct_rate   = fraction of ALL sentences yielding the CORRECT triple  [vs stub 1.0]
        per_class breakdown   = coverage + correct rate per sentence-structure class (the failure modes)
  (b) FOUNDATION correctness on what IS extracted: precision (no false/misfire fact admitted) + true-recall.
  (c) QUERY accuracy: retrieve a stored object given an (s, r) cue via the grown VSA store.
  (d) GATE behavior: accept-true rate + reject/hold-false rate; FULL vs NO_GATE precision (does the gate
      clean up parser noise?).
  Localization arms: ORACLE lexicon (isolates PARSER error from lexicon error) + RANDOM lexicon (floor).

PRE-REG (envelope-fail-bands; I own the bands; set BEFORE running):
  HARD-PASS (glass-box no-LLM IE reads real simple prose at USABLE coverage AND the read->grow loop builds a
             correct queryable foundation from real-prose-derived triples):
    parser_coverage >= 0.60 AND parser_precision >= 0.80 AND FULL endtoend_correct_rate >= 0.55 AND
    FULL foundation_precision >= 0.90 AND accept_false_rate == 0.0 AND FULL true_recall >= 0.70 AND
    query_acc >= 0.80 AND (FULL foundation_precision - NO_GATE foundation_precision) >= 0.05 AND
    novel_owl_ok AND hold_release_ok.
  HARD-FAIL (glass-box parsing of real prose not yet viable):
    parser_coverage < 0.25 OR FULL endtoend_correct_rate < 0.20 OR parser_precision < 0.40 OR
    FULL foundation_precision < 0.60 OR accept_false_rate == 1.0 OR query_acc < 0.40.
  MIDDLE otherwise (partial: works on a SUBSET of sentence structures -- characterize the envelope + report the
    per-class coverage table + failure modes as the roadmap). A modest-coverage result IS informative.

Local numpy, no queue/GPU/atoms/push. ASCII-only. Sequential-CPU (foundation grows fact-by-fact, gate state
depends on prior admissions -> genuine chained dependency; wall < 10s). Storage: SHARDED (one VSA vector per
accepted fact) per META_STORAGE_STRATEGY. progress_logging = print_flush_true.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; FULL_LOOP vs NO_GATE accepted-store hash differs).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor. FHRR cleanup among ~25 concepts at N=1024 with 3-term bundle is
#     z ~ sqrt(2N/3) ~ 26 sigma -> VSA decode reachable ~1.0; extraction is gated by PARSER rule-misfire +
#     LEXICON map error, NOT by phasor noise.
# - baseline_in_band at smoke: NO_GATE foundation_precision < 1.0 (admits false + parser-misfire facts);
#     FULL_LOOP foundation_precision target ~1.0; RANDOM-lexicon extraction ~ chance -> not saturated.
# - discriminator survives scale: corpus is FIXED-size (real prose, hand-authored GT). Discriminators =
#     (1) parser correctness < 1.0 on hard structures (deterministic misfire, verified at self-test),
#     (2) gate-vs-nogate precision + accept_false_rate (the injected type-violating false facts are
#     deterministic; FULL rejects, NO_GATE admits -- verified at self-test).
# - HARD_PASS strictly above floor; explicit bands in prereg JSON.
# - real_code_path (F.1): self_test constructs the REAL imported objects (learn_lexicon + SVO encode/decode +
#     FoundationStore) at tiny scale + the REAL ie_extract, and asserts (not a synthetic-only branch).
# - deterministic seeding (F.5): fixed int seeds; sorted() vocab ordering; NO hash()/list(set()) for seeds.
# - all numbers in comments tagged HYPOTHESIZED@prereg / THEORETICAL / MEASURED@metrics.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import time
import json
import hashlib
import platform
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_grow_foundation_realprose_glassbox_ie_v1"

# --- GENUINE REUSE of the proven downstream (imported, not rebuilt) ---
# Learned-lexicon + ingest-gate + SHARDED VSA FoundationStore + role-filler SVO encode/decode + type foundation
# all come from the v1 read->grow cell VERBATIM. This cell ONLY replaces the INPUT (real prose) + the PARSE.
from experiments.exp_read_grow_foundation_endtoend_v1 import (
    N_DIM,
    RELATIONS,
    ENTITIES,
    ANIMALS,
    FOODS,
    PLACES,
    GT_TYPE,
    build_typed_foundation,
    build_lexicon_train,
    FoundationStore,
    _svo_make_phasors,
    _encode_meaning,
    _decode_meaning,
    _learn_lexicon,
    _lexicon_top,
)

# ---------------------------------------------------------------------------
# GLASS-BOX SYMBOLIC IE PARSER (deterministic; NO LLM; no neural dependency parser).
# Layer 1: POS-lexicon tagging (closed-class function words + content lexicon + productive morphology).
# Layer 2: ClausIE/ReVerb-style pattern rules over the tag sequence -> (subj, relation, obj).
# The tagging injects WORD-CLASS structure (not facts); the rules can MIS-APPLY (wrong/no triple) but never
# hallucinate a fact. Relation vocabulary is the schema's RELATIONS (eats / lives_in / chases).
# ---------------------------------------------------------------------------
DETS = {"the", "a", "an"}
PREPS = {"in", "on", "by", "at", "near", "under", "with", "to"}
CONJS = {"and", "that", "which", "who"}
AUXES = {"is", "are", "was", "were", "be", "been", "am"}
ADJS = {"hungry", "little", "small", "big", "brown", "fast", "lazy", "happy", "quick",
        "old", "young", "grey", "gray", "black", "white", "red", "wet", "green"}
ADVS = {"quickly", "slowly", "happily", "then", "always", "often", "gently"}
# verb surface forms -> canonical relation-verb stem. "live" needs a following "in" to become lives_in.
EAT_FORMS = {"eat", "eats", "eating", "ate", "eaten"}
CHASE_FORMS = {"chase", "chases", "chasing", "chased"}
LIVE_FORMS = {"live", "lives", "living", "lived"}
NOUNS = set(ENTITIES)   # singular canonical nouns (the schema vocabulary)


def _noun_lemma(w):
    """productive singular morphology: birds->bird, seeds->seed, foxes->fox. Glass-box, no lexicon lookup of the
    plural form itself."""
    if w in NOUNS:
        return w
    if len(w) > 3 and w.endswith("es") and w[:-2] in NOUNS:
        return w[:-2]
    if len(w) > 2 and w.endswith("s") and w[:-1] in NOUNS:
        return w[:-1]
    return None


def _tag_token(w):
    """return (tag, lemma). tag in {DET, AUX, PREP, CONJ, ADV, ADJ, VERB, NOUN, UNK}."""
    if w in DETS:
        return "DET", None
    if w in AUXES:
        return "AUX", None
    if w in PREPS:
        return "PREP", w
    if w in CONJS:
        return "CONJ", w
    if w in ADVS:
        return "ADV", None
    if w in ADJS:
        return "ADJ", None
    if w in EAT_FORMS:
        return "VERB", "eats"
    if w in CHASE_FORMS:
        return "VERB", "chases"
    if w in LIVE_FORMS:
        return "VERB", "live"          # provisional; resolved to lives_in only with a following "in"
    nl = _noun_lemma(w)
    if nl is not None:
        return "NOUN", nl
    return "UNK", None


def _tokenize(sentence):
    s = sentence.lower().strip()
    for p in [".", "!", "?", ",", ";", ":", '"', "'"]:
        s = s.replace(p, " ")
    return [t for t in s.split() if t]


def ie_extract(sentence):
    """GLASS-BOX rule-based IE: real sentence -> (subj, relation, obj) surface-token triple, or None.
    Returns (triple_or_None, rule_name, fail_reason). Deterministic; provenance = (sentence, rule_name)."""
    toks = _tokenize(sentence)
    tags = [(t,) + _tag_token(t) for t in toks]   # (word, tag, lemma)
    # main verb = FIRST token tagged VERB (relative-clause verbs win first -> a documented failure mode).
    vi = None
    for i, (w, tg, lm) in enumerate(tags):
        if tg == "VERB":
            vi = i
            break
    if vi is None:
        return None, "NO_VERB", "no known verb (out-of-schema relation)"
    verb_lemma = tags[vi][2]
    # SUBJECT = nearest NOUN to the LEFT of the verb (head of the preceding NP; coordination -> nearest only).
    subj = None
    for j in range(vi - 1, -1, -1):
        if tags[j][1] == "NOUN":
            subj = tags[j][2]
            break
    if subj is None:
        return None, "NO_SUBJECT", "no noun left of verb"
    # OBJECT + RELATION: scan right of verb, skip DET/ADJ/ADV/AUX; capture at most one governing PREP then a NOUN.
    prep = None
    obj = None
    j = vi + 1
    while j < len(tags):
        tg = tags[j][1]
        if tg in ("DET", "ADJ", "ADV", "AUX"):
            j += 1
            continue
        if tg == "PREP" and prep is None and obj is None:
            prep = tags[j][2]
            j += 1
            continue
        if tg == "NOUN":
            obj = tags[j][2]
            break
        break   # CONJ / UNK / a second VERB before a noun -> stop (no object found)
    # relation resolution (glass-box normalization table).
    if verb_lemma == "live":
        if prep == "in":
            relation = "lives_in"
        else:
            return None, "LIVE_WITHOUT_IN", "live verb without governing 'in'"
    elif verb_lemma in ("eats", "chases"):
        relation = verb_lemma            # a following 'by' (passive) is NOT specially handled -> misfire by design
    else:
        return None, "UNKNOWN_VERB", "verb not in relation schema"
    if obj is None:
        return None, "NO_OBJECT", "no object noun after verb"
    if subj == obj:
        return None, "SUBJ_EQ_OBJ", "subject == object"
    if relation not in RELATIONS:
        return None, "REL_NOT_IN_SCHEMA", "relation not in schema"
    if subj not in ENTITIES or obj not in ENTITIES:
        return None, "TOKEN_OOV", "subj/obj not in entity vocab"
    if prep == "by":
        rule = "SVO_PASSIVE_MISFIRE"     # rule fired but 'by'-agent was taken as object -> reversed (misfire)
    elif prep == "in" and relation == "lives_in":
        rule = "SVO_PREP"
    else:
        rule = "SVO_ACTIVE"
    return (subj, relation, obj), rule, None


# ---------------------------------------------------------------------------
# REAL-PROSE CORPUS (early-reader-register simple declaratives + a deliberately-hard tail).
# Every sentence has: text, gt (target ground-truth triple), label (gate role), cls (structure class),
# role (foundation role), expect_parse (my HYPOTHESIS whether the symbolic rules handle it).
# Curriculum order: foundational block first (bootstraps the schema), schema-checkable next, hard-structure
# probes, mid-stream FALSE injection, out-of-order HOLD, novel-grounding support, novel late entity.
# The hard-structure probes DUPLICATE facts already asserted by easy sentences (or yield type-violating
# misfires) so a parser miss/misfire does NOT silently reduce required-recall -- it shows up in EXTRACTION
# metrics + is caught by the gate. Vocabulary = the schema's ENTITIES/RELATIONS so the proven lexicon applies.
# ---------------------------------------------------------------------------
def _row(text, gt, label, cls, role, expect_parse):
    return {"text": text, "gt": gt, "label": label, "cls": cls, "role": role, "expect_parse": expect_parse}


PROSE_CORPUS = [
    # -- foundational block: simple SVO (eats) -- bootstraps relation argument-type profiles --
    _row("The cat eats the fish.", ("cat", "eats", "fish"), "TRUE_ACCEPT", "simple_svo", "required", True),
    _row("The dog eats the bread.", ("dog", "eats", "bread"), "TRUE_ACCEPT", "simple_svo", "required", True),
    _row("A cow eats grass.", ("cow", "eats", "grass"), "TRUE_ACCEPT", "svo_no_determiner", "required", True),
    _row("The bird eats a seed.", ("bird", "eats", "seed"), "TRUE_ACCEPT", "simple_svo", "required", True),
    _row("The frog eats the worm.", ("frog", "eats", "worm"), "TRUE_ACCEPT", "simple_svo", "required", True),
    # -- foundational block: SVO + preposition (lives_in) --
    _row("The cat lives in the barn.", ("cat", "lives_in", "barn"), "TRUE_ACCEPT", "svo_prep", "required", True),
    _row("The dog lives in a barn.", ("dog", "lives_in", "barn"), "TRUE_ACCEPT", "svo_prep", "required", True),
    _row("The bird lives in the nest.", ("bird", "lives_in", "nest"), "TRUE_ACCEPT", "svo_prep", "required", True),
    _row("The fish lives in the pond.", ("fish", "lives_in", "pond"), "TRUE_ACCEPT", "svo_prep", "required", True),
    _row("The frog lives in the pond.", ("frog", "lives_in", "pond"), "TRUE_ACCEPT", "svo_prep", "required", True),
    # -- foundational block: simple SVO (chases) --
    _row("The cat chases the bird.", ("cat", "chases", "bird"), "TRUE_ACCEPT", "simple_svo", "required", True),
    _row("The dog chases the cat.", ("dog", "chases", "cat"), "TRUE_ACCEPT", "simple_svo", "required", True),
    _row("The bird chases the frog.", ("bird", "chases", "frog"), "TRUE_ACCEPT", "simple_svo", "required", True),
    # -- schema-checkable TRUE facts (gate now has argument-type profiles; some harder-but-handleable) --
    _row("The cow lives in a field.", ("cow", "lives_in", "field"), "TRUE_ACCEPT", "svo_prep", "required", True),
    _row("The hungry frog eats a seed.", ("frog", "eats", "seed"), "TRUE_ACCEPT", "adjective_modifier", "required", True),
    _row("The cat is eating a worm.", ("cat", "eats", "worm"), "TRUE_ACCEPT", "present_continuous", "required", True),
    _row("The small dog eats an apple.", ("dog", "eats", "apple"), "TRUE_ACCEPT", "adjective_modifier", "required", True),
    # -- HARD-STRUCTURE probes (coverage-only; facts duplicate easy sentences OR yield type-violating misfires) --
    _row("Birds eat seeds.", ("bird", "eats", "seed"), "TRUE_ACCEPT", "plural_no_determiner", "probe", True),
    _row("The cat quickly eats the fish.", ("cat", "eats", "fish"), "TRUE_ACCEPT", "adverb_modifier", "probe", True),
    _row("The worm is eaten by the frog.", ("frog", "eats", "worm"), "TRUE_ACCEPT", "passive", "probe", False),
    _row("The seed is eaten by the bird.", ("bird", "eats", "seed"), "TRUE_ACCEPT", "passive", "probe", False),
    _row("The cat and the dog eat bread.", ("cat", "eats", "bread"), "TRUE_ACCEPT", "coordination_subject", "probe", False),
    _row("The dog and the cat chase the bird.", ("dog", "chases", "bird"), "TRUE_ACCEPT", "coordination_subject", "probe", False),
    _row("The cat that lives in the barn eats a fish.", ("cat", "eats", "fish"), "TRUE_ACCEPT", "relative_clause", "probe", False),
    _row("The frog that eats worms lives in the pond.", ("frog", "lives_in", "pond"), "TRUE_ACCEPT", "relative_clause", "probe", False),
    _row("The owl sleeps in the tree.", ("owl", "sleeps", "tree"), "TRUE_ACCEPT", "out_of_schema_relation", "probe", False),
    _row("The mouse runs to the barn.", ("mouse", "runs", "barn"), "TRUE_ACCEPT", "out_of_schema_relation", "probe", False),
    # -- FALSE injection (simple + schema-checkable + TYPE-VIOLATING; gate must reject) --
    _row("The cat eats the barn.", ("cat", "eats", "barn"), "FALSE_REJECT", "simple_svo", "false", True),
    _row("The bird lives in the worm.", ("bird", "lives_in", "worm"), "FALSE_REJECT", "svo_prep", "false", True),
    # -- OUT-OF-ORDER (provisional-hold-bootstrap): both concepts ungrounded on arrival -> HOLD --
    _row("The kitten chases the mouse.", ("kitten", "chases", "mouse"), "HOLD_THEN_ACCEPT", "simple_svo", "hold", True),
    # -- support arrives (grounds kitten + mouse) -> held fact releases --
    _row("The kitten eats a seed.", ("kitten", "eats", "seed"), "NOVEL", "simple_svo", "novel", True),
    _row("The mouse eats the grass.", ("mouse", "eats", "grass"), "NOVEL", "simple_svo", "novel", True),
    # -- NOVEL entity late (owl) slots into the known schema -> admit + queryable --
    _row("The owl eats a worm.", ("owl", "eats", "worm"), "NOVEL", "simple_svo", "novel", True),
    _row("The owl lives in the nest.", ("owl", "lives_in", "nest"), "NOVEL", "svo_prep", "novel", True),
]

# ground-truth accept/reject sets over REQUIRED + NOVEL + HOLD facts (probe facts are coverage-only, NOT
# required for recall -- they duplicate easy facts or are type-violating misfires).
SHOULD_ACCEPT = set(d["gt"] for d in PROSE_CORPUS if d["role"] in ("required", "novel", "hold"))
SHOULD_REJECT = set(d["gt"] for d in PROSE_CORPUS if d["role"] == "false")


# ---------------------------------------------------------------------------
# METRIC (a): pure PARSER analysis (seed/lexicon-independent). Coverage + precision + per-class failure modes.
# ---------------------------------------------------------------------------
def analyze_parser():
    per_class = defaultdict(lambda: {"n": 0, "covered": 0, "correct": 0})
    rows = []
    for d in PROSE_CORPUS:
        tri, rule, freason = ie_extract(d["text"])
        covered = tri is not None
        correct = bool(covered and tri == d["gt"])
        c = d["cls"]
        per_class[c]["n"] += 1
        per_class[c]["covered"] += int(covered)
        per_class[c]["correct"] += int(correct)
        rows.append({"text": d["text"], "gt": list(d["gt"]), "extracted": (list(tri) if tri else None),
                     "rule": rule, "fail_reason": freason, "cls": c, "expect_parse": d["expect_parse"],
                     "covered": covered, "correct": correct})
    n = len(PROSE_CORPUS)
    yielded = [r for r in rows if r["covered"]]
    coverage = len(yielded) / float(n)
    precision = (sum(r["correct"] for r in yielded) / float(len(yielded))) if yielded else 0.0
    correct_rate = sum(r["correct"] for r in rows) / float(n)
    # per-class rates
    per_class_out = {}
    for c, v in per_class.items():
        per_class_out[c] = {
            "n": v["n"],
            "coverage": v["covered"] / float(v["n"]),
            "correct_rate": v["correct"] / float(v["n"]),
        }
    # failure-mode summary: sentences that are covered-but-WRONG (misfire) vs not-covered (abstain).
    misfire = [{"text": r["text"], "gt": r["gt"], "got": r["extracted"], "rule": r["rule"], "cls": r["cls"]}
               for r in rows if r["covered"] and not r["correct"]]
    abstain = [{"text": r["text"], "gt": r["gt"], "fail_reason": r["fail_reason"], "cls": r["cls"]}
               for r in rows if not r["covered"]]
    return {
        "parser_coverage": coverage,
        "parser_precision": precision,
        "parser_correct_rate": correct_rate,
        "n_sentences": n,
        "per_class": per_class_out,
        "misfire_examples": misfire,
        "abstain_examples": abstain,
        "rows": rows,
    }


# ---------------------------------------------------------------------------
# ONE end-to-end read->grow loop for one seed + one arm, with GLASS-BOX IE parse.
# (mirror of v1.run_loop but the parse is ie_extract over real prose, not positional over tuples.)
# ---------------------------------------------------------------------------
def run_loop(seed, use_gate, lexicon_kind="learned"):
    rng = np.random.default_rng(seed)
    scene_rng = np.random.default_rng(seed * 7 + 1)
    foundation = build_typed_foundation()
    cid_idx = foundation["cid_idx"]
    n_concept = len(foundation["concept_ids"])
    C = _svo_make_phasors(rng, n_concept, N_DIM)
    roles = _svo_make_phasors(rng, 3, N_DIM)

    # PIECE 1: LEARN the lexicon (glass-box cross-situational) -- reused verbatim from v1's learner.
    if lexicon_kind == "random":
        top_map = {w: foundation["concept_ids"][rng.integers(n_concept)] for w in foundation["words"]}
        mapping_acc = float(np.mean([top_map[w] == foundation["true_map"][w] for w in foundation["words"]]))
    elif lexicon_kind == "oracle":
        top_map = dict(foundation["true_map"])
        mapping_acc = 1.0
    else:
        train = build_lexicon_train(rng, foundation, n_per_word_min=14)
        assoc, _ = _learn_lexicon(
            train, foundation, scene_rng,
            role_gating=True, soft_me=True, fast_map=True,
            n_dist_noun=2, n_dist_verb=2, p_drop=0.05, p_syst=0.0,
        )
        top_map = _lexicon_top(assoc, foundation)
        tm = foundation["true_map"]
        mapping_acc = float(np.mean([top_map.get(w) == tm[w] for w in foundation["words"]]))

    store = FoundationStore(C, roles, cid_idx)

    # PIECE 2 + 3: READ each real sentence -> GLASS-BOX IE parse -> lexicon map -> encode/decode -> GATE -> GROW.
    n_extract_ok = 0
    n_sent = len(PROSE_CORPUS)
    per_sentence = []
    for d in PROSE_CORPUS:
        text, gt_triple, label, role = d["text"], d["gt"], d["label"], d["role"]
        parsed, rule, freason = ie_extract(text)   # GLASS-BOX symbolic IE
        if parsed is None:
            per_sentence.append({"text": text, "gt": gt_triple, "extracted": None, "rule": rule,
                                 "fail_reason": freason, "label": label, "role": role,
                                 "extract_ok": False, "gate": "IE_NO_TRIPLE"})
            continue
        # map parsed surface tokens -> concepts via the LEARNED lexicon; encode role-filler bundle; decode.
        try:
            learned_concepts = tuple(top_map.get(w) for w in parsed)
            filler_idx = tuple(cid_idx[c] if c in cid_idx else 0 for c in learned_concepts)
            M = _encode_meaning(filler_idx, C, roles)
            dec_idx = _decode_meaning(M, C, roles, 3)
            inv = {v: k for k, v in cid_idx.items()}
            extracted = tuple(inv[i] for i in dec_idx)
        except Exception as ex:   # attributable interface failure, never silent
            per_sentence.append({"text": text, "gt": gt_triple, "stage_fail": "lexicon_vsa",
                                 "err": repr(ex), "label": label, "role": role, "extract_ok": False})
            continue
        extract_ok = (extracted == gt_triple)
        if extract_ok:
            n_extract_ok += 1
        cand = extracted   # the triple fed to the gate is what the loop EXTRACTED (genuine end-to-end)
        rec = {"text": text, "gt": gt_triple, "extracted": extracted, "rule": rule, "label": label,
               "role": role, "extract_ok": extract_ok}
        well_formed = (cand[1] in RELATIONS and cand[0] != cand[2]
                       and cand[0] in ENTITIES and cand[2] in ENTITIES)
        if not well_formed:
            rec.update(gate="SKIP_MALFORMED")
            per_sentence.append(rec)
            continue
        if use_gate:
            dec, info = store.gate(cand)
            rec.update(gate=dec, gate_reason=info.get("reason"))
            store.decisions.append({"stage": "read", **info, "decision": dec})
            if dec == "ACCEPT":
                store.commit(cand)
            elif dec == "HOLD":
                store.held.append([cand, 0])
            store.reeval_holds()
        else:
            rec.update(gate="ACCEPT_NOGATE")
            store.commit(cand)
        per_sentence.append(rec)
    if use_gate:
        store.reeval_holds()

    endtoend_correct_rate = n_extract_ok / float(n_sent)

    # METRIC (b): FOUNDATION correctness (accepted concept triples vs GT accept/reject sets).
    accepted = store.accepted
    n_false_in_store = len(accepted & SHOULD_REJECT)
    true_in_store = accepted & SHOULD_ACCEPT
    precision = (len(true_in_store) / float(len(accepted))) if accepted else 0.0
    true_recall = len(true_in_store) / float(len(SHOULD_ACCEPT))
    accept_false_rate = (n_false_in_store / float(len(SHOULD_REJECT))) if SHOULD_REJECT else 0.0

    # METRIC (d): GATE behavior over correctly-extracted, gate-relevant TRUE candidates.
    true_extracted = [r for r in per_sentence
                      if r.get("extract_ok") and r.get("role") in ("required", "novel", "hold")]
    true_accepted = [r for r in true_extracted if r["gt"] in accepted]
    accept_true_rate = (len(true_accepted) / float(len(true_extracted))) if true_extracted else 0.0

    # METRIC (c): QUERY accuracy (VSA retrieval over the grown store).
    obj_sets = defaultdict(set)
    for (s, r, o) in accepted:
        if (s, r, o) in SHOULD_ACCEPT:
            obj_sets[(s, r)].add(o)
    q_total = 0
    q_ok = 0
    for (s, r), objs in sorted(obj_sets.items()):
        got = store.query(s, r)
        q_total += 1
        if got in objs:
            q_ok += 1
    query_acc = (q_ok / float(q_total)) if q_total else 0.0

    # targeted NOVEL + HOLD queryability checks.
    novel_owl_ok = ("owl", "eats", "worm") in accepted and store.query("owl", "eats") == "worm"
    novel_owl_place_ok = ("owl", "lives_in", "nest") in accepted
    hold_release_ok = ("kitten", "chases", "mouse") in accepted
    kitten_query_ok = store.query("kitten", "eats") in obj_sets.get(("kitten", "eats"), {"seed"})

    # store round-trip (localizes gate->store / store->query).
    rt_total = 0
    rt_ok = 0
    for (s, r, o) in sorted(true_in_store):
        rt_total += 1
        if store.query(s, r) in obj_sets.get((s, r), {o}):
            rt_ok += 1
    store_roundtrip_acc = (rt_ok / float(rt_total)) if rt_total else 0.0

    return {
        "seed": seed, "use_gate": use_gate, "lexicon_kind": lexicon_kind,
        "mapping_acc": mapping_acc,
        "endtoend_correct_rate": endtoend_correct_rate,
        "n_sentences": n_sent,
        "n_accepted": len(accepted),
        "foundation_precision": precision,
        "true_recall": true_recall,
        "accept_false_rate": accept_false_rate,
        "n_false_in_store": n_false_in_store,
        "accept_true_rate": accept_true_rate,
        "query_acc": query_acc,
        "store_roundtrip_acc": store_roundtrip_acc,
        "novel_owl_ok": bool(novel_owl_ok),
        "novel_owl_place_ok": bool(novel_owl_place_ok),
        "hold_release_ok": bool(hold_release_ok),
        "kitten_query_ok": bool(kitten_query_ok),
        "accepted_hash": store.accepted_hash(),
        "accepted_sorted": sorted(accepted),
    }


def avg_arm(seeds, use_gate, lexicon_kind="learned"):
    runs = [run_loop(s, use_gate, lexicon_kind) for s in seeds]
    keys_mean = ["mapping_acc", "endtoend_correct_rate", "foundation_precision", "true_recall",
                 "accept_false_rate", "accept_true_rate", "query_acc", "store_roundtrip_acc",
                 "n_accepted", "n_false_in_store"]
    keys_all = ["novel_owl_ok", "novel_owl_place_ok", "hold_release_ok", "kitten_query_ok"]
    out = {k: float(np.mean([r[k] for r in runs])) for k in keys_mean}
    out.update({k: bool(all(r[k] for r in runs)) for k in keys_all})
    out["per_seed"] = runs
    return out


# ---------------------------------------------------------------------------
# Verdict (envelope-fail-bands per pre-reg; parser stats seed-independent, downstream over seeds).
# ---------------------------------------------------------------------------
def compute_verdict(parser, full, nogate, oracle, random_ctrl):
    cov = parser["parser_coverage"]
    prec = parser["parser_precision"]
    hp = (
        cov >= 0.60 and
        prec >= 0.80 and
        full["endtoend_correct_rate"] >= 0.55 and
        full["foundation_precision"] >= 0.90 and
        full["accept_false_rate"] == 0.0 and
        full["true_recall"] >= 0.70 and
        full["query_acc"] >= 0.80 and
        (full["foundation_precision"] - nogate["foundation_precision"]) >= 0.05 and
        full["novel_owl_ok"] and full["hold_release_ok"]
    )
    hf = (
        cov < 0.25 or
        full["endtoend_correct_rate"] < 0.20 or
        prec < 0.40 or
        full["foundation_precision"] < 0.60 or
        full["accept_false_rate"] == 1.0 or
        full["query_acc"] < 0.40
    )
    if hp:
        tier = "HARD_PASS"
    elif hf:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"
    # localization: which interface is weakest (attributable).
    localize = []
    if cov < 0.60:
        localize.append("parser->coverage (symbolic rules abstain on too many real-prose structures)")
    if prec < 0.80:
        localize.append("parser->precision (symbolic rules MISFIRE on hard structures: %s)"
                        % ",".join(sorted({m["cls"] for m in parser["misfire_examples"]})))
    if full["endtoend_correct_rate"] < oracle["endtoend_correct_rate"] - 0.05:
        localize.append("parse->lexicon (learned map degrades vs oracle; lexicon is the extra bottleneck)")
    if full["accept_false_rate"] > 0.0:
        localize.append("triple->gate (gate admitted a type-violating false fact)")
    if full["true_recall"] < 0.70:
        localize.append("triple->gate (gate rejected/held required true facts)")
    if full["query_acc"] < 0.80 and full["store_roundtrip_acc"] >= 0.80:
        localize.append("store->query (round-trip ok but multi-object cue retrieval degrades)")
    weakest = localize if localize else ["none (all interfaces at/above target)"]
    msg = (f"{tier} | PARSER: coverage={cov:.3f} precision={prec:.3f} correct_rate={parser['parser_correct_rate']:.3f} "
           f"(vs positional-stub 1.000) | endtoend_correct FULL={full['endtoend_correct_rate']:.3f} "
           f"(oracle-lex={oracle['endtoend_correct_rate']:.3f} random-lex={random_ctrl['endtoend_correct_rate']:.3f}) | "
           f"foundation_prec FULL={full['foundation_precision']:.3f} vs NO_GATE={nogate['foundation_precision']:.3f} | "
           f"true_recall={full['true_recall']:.3f} accept_false_rate={full['accept_false_rate']:.3f} "
           f"query_acc={full['query_acc']:.3f} | novel_owl={full['novel_owl_ok']} hold_release={full['hold_release_ok']} | "
           f"weakest={weakest}")
    return tier, msg, weakest


# ---------------------------------------------------------------------------
# infra: out-dir / start-marker / crash-metrics / atomic write.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_read_grow_foundation_realprose_glassbox_ie_v1",
           "smoke": "exp_read_grow_foundation_realprose_glassbox_ie_v1_smoke",
           "self_test": "exp_read_grow_foundation_realprose_glassbox_ie_v1_selftest"}[run_mode]
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")   # atomic per META_RULE_AH


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path (ie_extract + imported learn_lexicon + encode/decode + FoundationStore)
# + assert the discriminators FIRE (parser misfires deterministically on hard structures; gate cleans up).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (ie_extract + imported learn_lexicon + SVO encode/decode + "
          "FoundationStore)...", flush=True)
    exercised = set()
    # (1) REAL glass-box IE parser on known sentences -- assert deterministic correct + deterministic misfire.
    exercised.add("ie_extract")
    assert ie_extract("The cat eats the fish.")[0] == ("cat", "eats", "fish"), "simple SVO extraction broke"
    assert ie_extract("The bird lives in the nest.")[0] == ("bird", "lives_in", "nest"), "SVO+prep extraction broke"
    assert ie_extract("The cat is eating a worm.")[0] == ("cat", "eats", "worm"), "present-continuous extraction broke"
    assert ie_extract("Birds eat seeds.")[0] == ("bird", "eats", "seed"), "plural morphology extraction broke"
    # passive MUST misfire (reversed) -- proves the failure-mode instrumentation is real, not decorative.
    pv = ie_extract("The worm is eaten by the frog.")[0]
    assert pv is not None and pv != ("frog", "eats", "worm"), f"passive should misfire; got {pv}"
    # out-of-schema verb MUST abstain.
    assert ie_extract("The owl sleeps in the tree.")[0] is None, "out-of-schema verb should abstain"
    # (2) parser analysis: coverage + precision must be in a sane band (not 1.0 = not the stub; not ~0 = works).
    pa = analyze_parser()
    assert 0.30 <= pa["parser_precision"] < 1.0, f"parser precision out of sane band: {pa['parser_precision']}"
    assert pa["parser_coverage"] >= 0.50, f"parser coverage too low to be usable: {pa['parser_coverage']}"
    assert pa["parser_correct_rate"] < 1.0, "parser cannot be perfect on real prose (would mean it's still a stub)"
    # (3) REAL lexicon learner over the tiny grounded corpus (imported verbatim).
    foundation = build_typed_foundation()
    train = build_lexicon_train(np.random.default_rng(5), foundation, n_per_word_min=10)
    assoc, _ = _learn_lexicon(train, foundation, np.random.default_rng(9),
                              role_gating=True, soft_me=True, fast_map=True,
                              n_dist_noun=2, n_dist_verb=2, p_drop=0.05, p_syst=0.0)
    top = _lexicon_top(assoc, foundation); exercised.add("learn_lexicon")
    macc = float(np.mean([top.get(w) == foundation["true_map"][w] for w in foundation["words"]]))
    assert macc >= 0.5, f"lexicon learner degenerate in self-test: mapping_acc={macc}"
    # (4) REAL end-to-end single seed (FULL_LOOP) + assertions on gate + store discriminator FIRING.
    full = run_loop(11, use_gate=True, lexicon_kind="learned"); exercised.add("run_loop")
    nogate = run_loop(11, use_gate=False, lexicon_kind="learned")
    assert full["endtoend_correct_rate"] > 0.0, "end-to-end extraction cratered in self-test"
    assert full["accepted_hash"] != nogate["accepted_hash"], \
        "META_RULE_AF: FULL_LOOP and NO_GATE accepted-store bit-identical (gate not firing on prose noise)"
    assert full["n_false_in_store"] <= nogate["n_false_in_store"], "gate did not reduce false facts vs accept-all"
    assert nogate["n_false_in_store"] >= 1, \
        "smoke-vacuous: NO_GATE did not admit the false fact (gate discriminator not exercised)"
    for ep in ["ie_extract", "learn_lexicon", "run_loop"]:
        assert ep in exercised, f"real_code_path: entrypoint {ep} not exercised"
    print(f"[self_test] PASS | parser coverage={pa['parser_coverage']:.3f} precision={pa['parser_precision']:.3f} "
          f"correct_rate={pa['parser_correct_rate']:.3f} | lexicon_macc={macc:.3f} | "
          f"endtoend_correct={full['endtoend_correct_rate']:.3f} full_false={full['n_false_in_store']} "
          f"nogate_false={nogate['n_false_in_store']} gate_fires={full['accepted_hash']!=nogate['accepted_hash']}",
          flush=True)
    return True


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)

    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    seeds = [11, 23] if run_mode == "smoke" else [11, 23, 37, 41, 53]
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds) * 4   # 4 arms x seeds
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[realprose_ie] run_mode={run_mode} seeds={seeds} corpus={len(PROSE_CORPUS)} real sentences", flush=True)

    # METRIC (a): pure parser analysis (seed-independent, deterministic).
    parser = analyze_parser()
    print(f"[realprose_ie] PARSER coverage={parser['parser_coverage']:.3f} precision={parser['parser_precision']:.3f} "
          f"correct_rate={parser['parser_correct_rate']:.3f} (vs positional-stub 1.000)", flush=True)
    for c, v in sorted(parser["per_class"].items()):
        print(f"[realprose_ie]   class {c:24s} n={v['n']:2d} coverage={v['coverage']:.2f} correct={v['correct_rate']:.2f}",
              flush=True)

    full = avg_arm(seeds, use_gate=True, lexicon_kind="learned")
    print(f"[realprose_ie] FULL_LOOP endtoend_correct={full['endtoend_correct_rate']:.3f} "
          f"foundation_prec={full['foundation_precision']:.3f} recall={full['true_recall']:.3f} "
          f"query={full['query_acc']:.3f} false_in_store={full['n_false_in_store']:.2f}", flush=True)
    nogate = avg_arm(seeds, use_gate=False, lexicon_kind="learned")
    print(f"[realprose_ie] NO_GATE foundation_prec={nogate['foundation_precision']:.3f} "
          f"false_in_store={nogate['n_false_in_store']:.2f}", flush=True)
    oracle = avg_arm(seeds, use_gate=True, lexicon_kind="oracle")
    random_ctrl = avg_arm(seeds, use_gate=True, lexicon_kind="random")
    print(f"[realprose_ie] ORACLE-lex endtoend_correct={oracle['endtoend_correct_rate']:.3f} "
          f"RANDOM-lex endtoend_correct={random_ctrl['endtoend_correct_rate']:.3f}", flush=True)

    tier, msg, weakest = compute_verdict(parser, full, nogate, oracle, random_ctrl)
    elapsed = time.perf_counter() - t0

    def strip(a):
        return {k: v for k, v in a.items() if k != "per_seed"}

    metrics = {
        "verdict": tier,
        "verdict_msg": msg,
        "summary": msg[:300],
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "n_read_sentences": len(PROSE_CORPUS),
        "expected_n_units": expected_n_units,
        "weakest_interface": weakest,
        # METRIC (a) -- pure glass-box IE parser on real prose (the headline reading result).
        "metric_a_parser_coverage": parser["parser_coverage"],
        "metric_a_parser_precision": parser["parser_precision"],
        "metric_a_parser_correct_rate": parser["parser_correct_rate"],
        "metric_a_positional_stub_correct_rate": 1.0,   # MEASURED@data/exp_read_grow_foundation_endtoend_v1/metrics.json
        "parser_per_class": parser["per_class"],
        "parser_failure_modes": {"misfire": parser["misfire_examples"], "abstain": parser["abstain_examples"]},
        "parser_rows": parser["rows"],
        # METRIC (b/c/d) -- downstream foundation on real-prose-derived triples.
        "metric_b_foundation_precision": full["foundation_precision"],
        "metric_b_true_recall": full["true_recall"],
        "metric_c_query_acc": full["query_acc"],
        "metric_d_accept_true_rate": full["accept_true_rate"],
        "metric_d_accept_false_rate": full["accept_false_rate"],
        "endtoend_correct_rate_learned": full["endtoend_correct_rate"],
        "endtoend_correct_rate_oracle_lex": oracle["endtoend_correct_rate"],
        "endtoend_correct_rate_random_lex": random_ctrl["endtoend_correct_rate"],
        "gate_vs_accept_all_precision_gain": full["foundation_precision"] - nogate["foundation_precision"],
        "arms": {
            "FULL_LOOP": strip(full),
            "NO_GATE": strip(nogate),
            "ORACLE_LEXICON": strip(oracle),
            "RANDOM_LEXICON": strip(random_ctrl),
        },
        "full_loop_per_seed": full["per_seed"],
        "prereg": {
            "hard_pass": "parser_coverage>=0.60 & parser_precision>=0.80 & FULL endtoend_correct>=0.55 & "
                         "FULL foundation_prec>=0.90 & accept_false_rate==0 & FULL recall>=0.70 & query>=0.80 & "
                         "(FULL-NOGATE prec)>=0.05 & novel_owl & hold_release",
            "hard_fail": "parser_coverage<0.25 | FULL endtoend_correct<0.20 | parser_precision<0.40 | "
                         "FULL foundation_prec<0.60 | accept_false_rate==1.0 | query<0.40",
            "middle": "otherwise (partial: works on a subset of structures; characterize the per-class envelope)",
            "compute_architecture": "sequential-CPU (genuine sequential dependency: foundation grows fact-by-fact)",
            "storage_strategy": "sharded (one VSA vector per accepted fact)",
            "parser_class": "fully-symbolic glass-box rule-based IE (NO LLM, NO neural dependency parser)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["ie_extract", "learn_lexicon", "encode_meaning", "decode_meaning", "run_loop"],
            "crlb_n/a": "no quantitative noise floor; extraction gated by rule-misfire + lexicon-map error, not phasor noise",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[realprose_ie] {tier} in {elapsed:.2f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[realprose_ie] {msg}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv):
            _md = "smoke"
        elif "--self-test" in sys.argv or "self_test" in sys.argv:
            _md = "self_test"
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
