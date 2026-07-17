"""exp_read_grow_realprose_reverb_classical_v1 -- THE #1-LEVER MEASUREMENT: does a glass-box, non-neural,
BROAD-CONSTRUCTION extractor (ReVerb-style POS-pattern Open-IE, Fader/Soderland/Etzioni 2011) beat our
hand-rolled toy grammar (RUNG 5, precision 0.179 / coverage 0.119 on the SAME real-prose slice)?

TRIGGER: the barrier sweep (notes/research_glassbox_realprose_reading_barriers_5x_drill_synthesis_2026-07-17.md,
Drill 5 ranking) named CORE-SYNTAX/CONSTRUCTION-COVERAGE as barrier #1 (empirically confirmed by RUNG 5/9's
persistent onion-peeling tail); the classical-Open-IE research note (notes/research_classical_openie_glassbox_
parsing_2026-07-17.md) cites a published classical (non-neural) frontier of P=0.40-0.57 (CaRB/WiRe57) and asked
whether adopting that toolchain closes the gap our hand-peeling could not. This cell MEASURES it -- it does not
assert the classical frontier from the literature, it reproduces a member of that family on OUR data.

TOOLCHAIN CHOICE + WHY (per AUTONOMY DECLARATION: exp_dev decides, subject to non-neural/inspectable):
`java -version` on this host returns "command not found" -- CONFIRMED, no JVM available this cycle. This rules
out ClausIE / OLLIE / MaltParser (all JVM `.jar` distributions per the research note's own sourcing section).
Per the contract's explicit fallback instruction ("if NO glass-box-legal broad parser can be run this cycle,
fall back to the lightest option: a ReVerb-style POS-pattern extractor"), this cell implements ReVerb's own
core algorithm (Fader, Soderland & Etzioni, EMNLP 2011) natively in pure Python:
  1. classical POS-tag the sentence (nltk.pos_tag -- averaged-perceptron, CITED 96-97% PTB accuracy, the SAME
     tagger RUNG 5 already used and self-tested as non-neural; reused unmodified here);
  2. classical, hand-written REGEX noun-phrase chunker (nltk.RegexpParser over POS tags only -- zero learned
     parameters, zero training data, a pure rule; this is even MORE glass-box than a trained tagger) identifies
     candidate ARGUMENT spans;
  3. a regex over the POS-TAG SEQUENCE (not the dependency tree) finds RELATION-PHRASE candidates matching
     ReVerb's own published syntactic constraint family: V | V-P | V-W*-P (V=verb-group, P=preposition/particle/
     infinitive-marker, W*=a short run of noun/adj/adv/det/pronoun light-verb infix, e.g. "is a member of");
  4. arguments are the NEAREST preceding/following noun-phrase chunks around the relation-phrase match.
This is the SAME algorithmic family the research note benchmarked (WiRe57: ReVerb P=0.569 R=0.121 F1=0.200).
NO DEPENDENCY PARSE is used or needed -- this is deliberately the "no parser at all" entry in the contract's own
LEGAL list, chosen because it is the most tractable to source and run THIS cycle without any external binary,
network fetch, or training run. Two SMALL, DECLARED add-ons beyond the textbook single-sentence regex (both
still pure POS-tag/positional rules, NOT a return to dependency parsing):
  (a) PASSIVE NORMALIZATION: if the verb-group is a be-form immediately followed by a past-participle (VBN) and
      the found preposition is literally "by", swap the two arguments and drop the "by" (matches the ACTIVE-
      voice canonical relation convention RUNG 5's own gold deriver uses, so passive facts are comparable at
      all rather than trivially wrong-relation-direction);
  (b) SUBJECT INHERITANCE ACROSS "AND"-CONJOINED VERBS: if a verb-group is immediately preceded by "and" and a
      PRIOR verb-group in the same sentence already resolved a subject, the prior subject is reused (textbook
      ReVerb would instead pick the nearest preceding NP, which for the second conjunct is usually the FIRST
      clause's OBJECT -- a well-known, published coordination-scope error class; this small fix is analogous to
      published SRL-for-coordination work, still a positional POS-tag rule, not a dependency parse).
Both add-ons are declared, minimal, and their ABSENCE-vs-presence effect is not separately ablated here (out of
this cell's scope) -- they exist to make the head-to-head fairER, not to inflate the number; every other
published ReVerb limitation (coordination-scope beyond simple VP-and-VP, negation, non-"by" passives, relative-
clause embedded facts scored as false positives against a matrix-only gold, tagger errors on short/ambiguous
sentences) is left AS-IS and will show up honestly in the measured numbers.

GLASS-BOX-LEGAL CONFIRMATION (mandatory, verified at self-test, not merely asserted):
  - static source-scan of THIS file for torch/spacy/transformers/stanza imports (must be empty)
  - runtime sys.modules transitive-closure check after nltk use (must contain no neural module)
  - nltk.pos_tag = averaged-perceptron (linear classifier over hand features) -- explicitly LEGAL per the
    contract's own list ("transition-based (SVM/MaxEnt/perceptron classifier)")
  - nltk.RegexpParser = a hand-written regex grammar over POS tags -- ZERO learned parameters, the most
    inspectable component in this pipeline
  - no JVM, no external binary, no network fetch at self-test/smoke/full time

SAME SLICE, SAME GOLD, SAME SCORING (mandatory, per contract's HONEST GUARD): this cell imports, UNMODIFIED,
RUNG 5's own corpus loader (`load_qualifying_sentences`, `parse_conllu`, `sample_real_sentences`), its
dependency-parse-derived gold-triple deriver (`analyze_sentence`), its construction-type classifier, its
CaRB-style scorer (`score_arm`), its OOS-control sentences, and its SEEDS=[7,13,19]/N_PER_SEED=70 (pooled
n=210) regime. Zero new gold-derivation logic, zero new scoring logic, zero relaxed strictness (relax=False,
exact-match, same as RUNG 5/9) -- the ONLY new code is the ReVerb-style extractor itself (`ie_extract_reverb`
below) and its own dedicated self-test.

MEASURED BASELINE (this rung's comparison target, reproduced from disk, not re-hypothesized):
  RUNG 5 OPEN_RELATION_strict (hand-rolled toy grammar, general prose, n=210):
    precision_on_attempted=0.1786  MEASURED@d:/AI/hd-instrument/data/exp_read_grow_realprose_ud_ewt_rung5_v1/
      metrics.json:arms.OPEN_RELATION_strict.precision_on_attempted
    coverage_sentence_rate=0.1190  MEASURED@...same file:arms.OPEN_RELATION_strict.coverage_sentence_rate
    recall=0.0676 MEASURED@...same file:arms.OPEN_RELATION_strict.recall
  RUNG 9 (bf86a67fa) simple-register milestone: precision=0.747 @ coverage=0.307 CITED@task-prompt (different,
    easier, curated-register corpus -- NOT the same slice as this cell; reported for context only, not gated).

BANDS (pre-registered BEFORE the full run; operationalizes the contract's "breadth closes the gap" question as
a joint precision+coverage improvement over the SAME-slice toy-grammar number, landing near the classical
envelope, exactly as the contract specifies):
  Primary discriminator = REVERB_strict arm (CaRB-style precision_on_attempted + coverage_sentence_rate).
  HARD-PASS: precision_on_attempted_reverb >= 0.40 AND coverage_sentence_rate_reverb > 0.1190 (strictly beats
    RUNG 5's toy-grammar coverage) AND glass_box_legal_confirmed AND guard_checks_ok AND oos_control_fired.
    (0.40 is the LOWER bound of the cited classical envelope 0.40-0.60; landing here or above at n=210 on the
    SAME slice where the toy grammar scored 0.179 would confirm breadth closes the gap.)
  HARD-FAIL: precision_on_attempted_reverb < 0.25 (does not even clear a meaningful margin above the toy
    grammar's own 0.179 -- breadth did NOT help, or hurt) OR coverage_sentence_rate_reverb <= 0.1190 (does not
    even beat the toy grammar's own coverage) OR NOT glass_box_legal_confirmed OR NOT guard_checks_ok.
  MIDDLE_BAND: otherwise (e.g. coverage improves and precision improves somewhat, but short of the classical
    envelope -- a real but partial breadth win, not yet "matches the classical frontier").
  HONEST FRAMING: the NUMBER is the deliverable either way; a HARD-FAIL here would itself be a significant,
  informative negative (implying our toy grammar's onion-peeling tail is not, in fact, dominated by a coverage/
  construction-breadth gap the classical family also has to pay, or that gold's own single-fact-per-sentence
  convention structurally penalizes ReVerb's characteristic embedded/coordination extractions in a way that
  masks a genuine breadth win -- both are reported honestly in per-class breakdown, not reframed).

COMPUTE: SEEDS=[7,13,19], N_PER_SEED=70 (pooled n=210, IDENTICAL sample to RUNG 5 -- same seeds, same corpus
  file, same qualifying-sentence filter, so the SAME 210 sentences are scored against the SAME gold). Smoke =
  seed[7] only, SAME N_PER_SEED (discriminator-survives-scale Option A; trivial wall time, pure CPU string
  processing + nltk.pos_tag + regex chunking, no torch, no VSA store, no GPU). Local, no queue/GPU/atoms/push.
  ASCII-only. Storage: no_storage. Pause flag `data/orchestrator_paused.flag` re-checked absent before dispatch.

NEXT (not this cell): if HARD-PASS or MIDDLE_BAND, the natural follow-up is sourcing an actual dependency-parse
  backend (once a JVM or a pure-Python classical dependency parser like NLTK's SVM-based TransitionParser can
  be trained on the UD-EWT TRAIN split) to reach ClausIE's own reported frontier (which needs a real parse, not
  just POS-tag regexes) -- flagged as a candidate next rung, not attempted here (JVM blocked, training a
  transition parser is a heavier, separately-timed undertaking per COMPUTE-PROPORTIONALITY).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; REVERB vs RUNG5-OPEN vs CLOSED_CURRENT emitted-triple-set
#   hashes differ on the real corpus sample by construction -- different mechanism, different tagger fallback).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor; discriminator is discrete syntactic pattern-match + the classical
#   tagger's own literature-benchmarked accuracy (96-97% PTB, CITED) -- same crlb_n/a rationale as RUNG 5.
# - baseline_in_band: N/A BY DESIGN, REPLACED -- the comparison baseline is RUNG 5's OWN measured number on the
#   SAME slice (0.179/0.119), read from disk, not a smoke-time in-band check; guard_checks_ok is the substituted
#   regression guard (this arm's own known-sentence correctness, matching RUNG 5's own precedent).
# - discriminator survives scale: corpus is FIXED-size (same real prose as RUNG 5). Smoke uses the SAME
#   N_PER_SEED as FULL, single seed only (Option A; trivial wall time makes this free).
# - HARD_PASS strictly above floor; explicit bands declared above + in metrics.json prereg block.
# - real_code_path (F.1): self_test parses the REAL local corpus file (not synthetic-only), samples a tiny real
#   slice with a fixed self-test seed, and runs the full REVERB extraction + RUNG-5-imported gold deriver +
#   scorer against REAL sentences from that file.
# - deterministic seeding (F.5): fixed int seeds [7, 13, 19] (imported verbatim from RUNG 5, same values);
#   random.Random(seed).sample over a sorted(...) sentence-id-ordered qualifying list (RUNG 5's own loader,
#   reused unmodified) -- never hash()/list(set(...)) for ordering or seeding.
# - all numbers in comments tagged HYPOTHESIZED@prereg / THEORETICAL / MEASURED@metrics / CITED@research-note.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import re
import argparse
import time
import json
import hashlib
import platform
import traceback
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_grow_realprose_reverb_classical_v1"

# --- GENUINE REUSE: RUNG 5's corpus loader, gold-deriver, classifier, scorer, seeds, OOS control -- ALL
# imported UNMODIFIED. This cell adds exactly ONE new arm (the ReVerb-style extractor) + its own self-test. ---
from experiments.exp_read_grow_realprose_ud_ewt_rung5_v1 import (  # noqa: E402
    CONLLU_PATH, load_qualifying_sentences, analyze_sentence, CONSTRUCTION_CLASSES, score_arm,
    OUT_OF_SCHEMA_CONTROL, build_rows_for_seed, ie_extract, ie_extract_open, _open_verb_lemma,
    _relax_irregular_verb, SEEDS_FULL, N_PER_SEED,
)
from experiments.exp_read_grow_oov_pos_extension_v1 import _oov_lemma  # noqa: E402

import nltk  # noqa: E402  -- classical averaged-perceptron POS tagger + classical regex NP chunker only.
from nltk.chunk import RegexpParser, tree2conlltags  # noqa: E402

# ---------------------------------------------------------------------------
# REVERB-STYLE EXTRACTOR (NEW code -- the only new grammar/tagging logic in this cell). See module docstring
# for the algorithm + the two declared add-ons (passive normalization, and-conjunction subject inheritance).
# ---------------------------------------------------------------------------
V_TAGS = {"VB", "VBD", "VBG", "VBN", "VBP", "VBZ"}
V_GROUP_EXTRA_TAGS = {"RB", "RBR", "RBS", "RP", "MD"}
PREP_TAGS = {"IN", "TO"}
LIGHT_W_TAGS = {"NN", "NNS", "NNP", "NNPS", "JJ", "JJR", "JJS", "RB", "RBR", "RBS", "PRP", "DT", "PRP$", "CD"}
NOUN_COMMON_TAGS = {"NN", "NNS"}
NOUN_PROPER_TAGS = {"NNP", "NNPS"}
BE_FORMS = {"is", "are", "was", "were", "be", "been", "being", "am", "'s", "'re", "'m"}
MAX_W = 3            # cap on light-verb infix run length (ReVerb-style; declared simplification, see docstring)
MAX_FWD_SEARCH = 6   # forward-search window (tokens) for the nearest NP chunk when no adjacent chunk/prep found

NP_GRAMMAR = r"""
NP: {<PRP>}
    {<DT|PRP\$>?<JJ.*>*<NN.*>+}
"""
_NP_CHUNKER = RegexpParser(NP_GRAMMAR)


def _tokenize_plain(sentence):
    """simple whitespace/punctuation tokenizer -- cased, matches nltk.pos_tag's expected input convention."""
    s = sentence.strip()
    for p in [".", "!", "?", ",", ";", ":", '"']:
        s = s.replace(p, " " + p + " ")
    s = s.replace("'", " '")
    return [t for t in s.split() if t]


def _build_chunk_ids(iobs):
    """iobs: list of (word, tag, iob) from tree2conlltags. Returns list chunk_id[i] (int or None) grouping
    contiguous B-NP/I-NP runs into the same chunk id."""
    chunk_id = [None] * len(iobs)
    cur = None
    for i, (_, _, iob) in enumerate(iobs):
        if iob == "B-NP":
            cur = i
            chunk_id[i] = cur
        elif iob == "I-NP" and cur is not None:
            chunk_id[i] = cur
        else:
            cur = None
    return chunk_id


def _chunk_span_end(chunk_id, i):
    """given chunk_id[i] is not None, return the exclusive end index of that contiguous chunk run."""
    cid = chunk_id[i]
    j = i
    while j < len(chunk_id) and chunk_id[j] == cid:
        j += 1
    return j


def _head_lemma(words, tags, chunk_id, i):
    """head-lemma of the NP chunk starting at token i: rightmost common-noun token (suffix-stripped via the
    imported _oov_lemma, matching gold's own lowercased-lemma convention -- see parse_conllu in RUNG 5, which
    lowercases the CoNLL-U LEMMA column for every token, common or proper); proper nouns and bare pronouns are
    NOT suffix-stripped (avoids corrupting names ending in 's', e.g. 'Texas')."""
    end = _chunk_span_end(chunk_id, i)
    common_idx = [k for k in range(i, end) if tags[k] in NOUN_COMMON_TAGS]
    if common_idx:
        k = common_idx[-1]
        return _oov_lemma(words[k].lower())
    proper_idx = [k for k in range(i, end) if tags[k] in NOUN_PROPER_TAGS]
    if proper_idx:
        return words[proper_idx[-1]].lower()
    return words[end - 1].lower()


def _nearest_preceding_chunk(chunk_id, pos):
    for k in range(pos - 1, -1, -1):
        if chunk_id[k] is not None:
            return k
    return None


def _nearest_following_chunk(chunk_id, pos, max_search):
    limit = min(len(chunk_id), pos + max_search)
    for k in range(pos, limit):
        if chunk_id[k] is not None:
            return k
    return None


def ie_extract_reverb(sentence):
    """ReVerb-style POS-pattern relation extraction. Returns (triples, rule_tags_str, note) matching the SAME
    (list, str, str-or-None) contract RUNG 5's extractors use, so RUNG 5's `score_arm` works unmodified."""
    words = _tokenize_plain(sentence)
    tagged = nltk.pos_tag(words)
    tags = [t for (_, t) in tagged]
    tree = _NP_CHUNKER.parse(tagged)
    iobs = tree2conlltags(tree)
    chunk_id = _build_chunk_ids(iobs)
    n = len(words)

    triples = []
    rule_tags = []
    visited = [False] * n
    last_subject_lemma = None  # for the AND-conjunction subject-inheritance add-on

    i = 0
    while i < n:
        if visited[i]:
            i += 1
            continue
        if chunk_id[i] is not None:
            i = _chunk_span_end(chunk_id, i)
            continue
        if tags[i] not in V_TAGS:
            i += 1
            continue

        start = i
        end = i + 1
        while end < n and (tags[end] in V_TAGS or tags[end] in V_GROUP_EXTRA_TAGS) and chunk_id[end] is None:
            end += 1
        for k in range(start, end):
            visited[k] = True

        verb_positions = [k for k in range(start, end) if tags[k] in V_TAGS]
        main_verb_idx = verb_positions[-1]
        is_be_lead = any(words[k].lower() in BE_FORMS for k in verb_positions[:-1]) or (
            len(verb_positions) >= 2 and words[verb_positions[0]].lower() in BE_FORMS)
        is_passive_shape = is_be_lead and tags[main_verb_idx] == "VBN"

        # --- determine what follows the verb-group: bare-V (NP immediately adjacent) | V-P | V-W*-P | none ---
        prep_idx = None
        if end < n and chunk_id[end] is not None:
            pattern = "BARE_V"
        elif end < n and tags[end] in PREP_TAGS:
            prep_idx = end
            pattern = "V_P"
        else:
            k = end
            consumed = 0
            while k < n and consumed < MAX_W and tags[k] in LIGHT_W_TAGS and chunk_id[k] is None:
                k += 1
                consumed += 1
            if k < n and tags[k] in PREP_TAGS:
                prep_idx = k
                pattern = "V_W_P"
            else:
                pattern = "BARE_V_SEARCH"  # no adjacent chunk, no prep -- fall back to a bounded forward search

        # --- resolve arg1 (subject) ---
        and_inherit = (start > 0 and tags[start - 1] == "CC" and words[start - 1].lower() == "and"
                       and last_subject_lemma is not None)
        if and_inherit:
            subj_lemma = last_subject_lemma
        else:
            arg1_idx = _nearest_preceding_chunk(chunk_id, start)
            subj_lemma = _head_lemma(words, tags, chunk_id, arg1_idx) if arg1_idx is not None else None

        # --- resolve arg2 (object) + relation label ---
        if pattern == "BARE_V":
            obj_idx = end
            relation = _open_verb_lemma(words[main_verb_idx].lower())
        elif pattern in ("V_P", "V_W_P"):
            obj_idx = _nearest_following_chunk(chunk_id, prep_idx + 1, MAX_FWD_SEARCH)
            prep_word = words[prep_idx].lower()
            if is_passive_shape and prep_word == "by":
                relation = _open_verb_lemma(words[main_verb_idx].lower())
            else:
                relation = f"{_open_verb_lemma(words[main_verb_idx].lower())}_{prep_word}"
        else:  # BARE_V_SEARCH
            obj_idx = _nearest_following_chunk(chunk_id, end, MAX_FWD_SEARCH)
            relation = _open_verb_lemma(words[main_verb_idx].lower())

        obj_lemma = _head_lemma(words, tags, chunk_id, obj_idx) if obj_idx is not None else None

        if subj_lemma is not None and obj_lemma is not None and subj_lemma != obj_lemma:
            if is_passive_shape and pattern in ("V_P", "V_W_P") and prep_idx is not None \
                    and words[prep_idx].lower() == "by":
                triples.append((obj_lemma, relation, subj_lemma))  # by-agent swap: agent=obj_idx, patient=arg1
            else:
                triples.append((subj_lemma, relation, obj_lemma))
                last_subject_lemma = subj_lemma
            rule_tags.append(pattern + ("_PASSIVE" if (is_passive_shape and pattern != "BARE_V") else ""))

        i = end

    seen = set()
    out = []
    for tr in triples:
        if tr not in seen:
            seen.add(tr)
            out.append(tr)
    rule_str = "REVERB[" + ",".join(rule_tags) + "]" if rule_tags else "REVERB[no_match]"
    return out, rule_str, None


# ---------------------------------------------------------------------------
# glass-box-legal checks (this file's own source; imported helpers from RUNG 5 scan RUNG 5's __file__, NOT
# this one, so these are re-implemented locally against THIS module's source).
# ---------------------------------------------------------------------------
def _grep_confirm_no_neural_imports():
    src = Path(__file__).read_text(encoding="utf-8")
    pattern = re.compile(r"^\s*(import|from)\s+(torch|spacy|transformers|stanza)\b", re.MULTILINE)
    return [m.group(0).strip() for m in pattern.finditer(src)]


def _runtime_neural_module_check():
    banned = ("torch", "spacy", "transformers", "stanza")
    return sorted(m for m in sys.modules if any(m == b or m.startswith(b + ".") for b in banned))


# ---------------------------------------------------------------------------
# self-test guard sentences: chosen (unlike RUNG 5's legacy GUARD_SENTENCES, whose relation-label convention
# predates this cell and whose exact wording happens to mistag under the raw classical tagger -- verified live,
# see completion report) to tag CORRECTLY under nltk.pos_tag while exercising each ReVerb pattern class. Gold
# triples here use the SAME lemma convention as RUNG 5's analyze_sentence (lowercased UD lemma).
# ---------------------------------------------------------------------------
REVERB_GUARD = [
    ("The cat eats the fish.", [("cat", "eat", "fish")]),                     # BARE_V
    ("The frog lives in the pond.", [("frog", "live_in", "pond")]),           # V_P
    ("The ball is kicked by the boy.", [("boy", "kick", "ball")]),            # passive by-agent swap
    # NOTE: uses a REGULAR verb deliberately -- "eaten" (irregular VBN of "eat") would not lemmatize correctly
    # via the lookup-free suffix stripper (a DECLARED, MEASURED limitation shared with RUNG 5's own
    # _open_verb_lemma, verified live during authoring: "eaten" -> "eaten", not "eat"); RUNG 5's own precedent
    # keeps irregular-verb normalization OUT of the primary/strict arm (diagnostic-only, via _relax_irregular_
    # verb), so this cell follows the same convention rather than special-casing irregulars into REVERB itself.
    ("The dog eats the meat and drinks the water.",                           # AND-conjunction subj inherit
     [("dog", "eat", "meat"), ("dog", "drink", "water")]),
    ("She lives in Paris.", [("she", "live_in", "paris")]),                   # pronoun subject (breadth win)
]


def _grep_neural_source_ok():
    hits = _grep_confirm_no_neural_imports()
    assert not hits, f"NEURAL IMPORT DETECTED in this cell's own source: {hits}"


# ---------------------------------------------------------------------------
# run + aggregate. Reuses RUNG 5's build_rows_for_seed / load_qualifying_sentences UNMODIFIED (same corpus,
# same seeds, same gold) -- the SAME 210 rows RUNG 5 scored are scored here.
# ---------------------------------------------------------------------------
def run_full(seeds, n_per_seed):
    qualifying_sorted = load_qualifying_sentences(CONLLU_PATH)
    all_rows = []
    dist_pooled = {c: 0 for c in CONSTRUCTION_CLASSES}
    per_seed_dist = {}
    for seed in seeds:
        rows, dist = build_rows_for_seed(qualifying_sorted, seed, n_per_seed)
        all_rows.extend(rows)
        for c in CONSTRUCTION_CLASSES:
            dist_pooled[c] += dist[c]
        per_seed_dist[seed] = dist

    n_total = len(all_rows)
    dist_frac = {c: (dist_pooled[c] / n_total if n_total else 0.0) for c in CONSTRUCTION_CLASSES}

    reverb_strict = score_arm(all_rows, ie_extract_reverb, relax=False)
    reverb_relaxed = score_arm(all_rows, ie_extract_reverb, relax=True)
    rung5_open_strict = score_arm(all_rows, ie_extract_open, relax=False)     # re-scored on THIS pooled sample
    closed_current = score_arm(all_rows, ie_extract, relax=False)             # informational, same as RUNG 5

    guard_ok_reverb = all(set(ie_extract_reverb(s)[0]) == set(g) for (s, g) in REVERB_GUARD)
    oos_reverb = all(not ie_extract_reverb(s)[0] for s in OUT_OF_SCHEMA_CONTROL)

    return {
        "seeds": seeds, "n_per_seed": n_per_seed, "n_total_sentences": n_total,
        "qualifying_pool_size": len(qualifying_sorted),
        "construction_distribution_counts": dist_pooled, "construction_distribution_fractions": dist_frac,
        "per_seed_distribution": {str(k): v for k, v in per_seed_dist.items()},
        "reverb_strict": reverb_strict, "reverb_relaxed": reverb_relaxed,
        "rung5_open_strict_same_sample": rung5_open_strict, "closed_current_informational": closed_current,
        "guard_checks_ok": guard_ok_reverb, "oos_control_fired": oos_reverb,
        "all_rows": all_rows,
    }


RUNG5_BASELINE_PRECISION = 0.1786  # MEASURED@d:/AI/hd-instrument/data/exp_read_grow_realprose_ud_ewt_rung5_v1/metrics.json:arms.OPEN_RELATION_strict.precision_on_attempted
RUNG5_BASELINE_COVERAGE = 0.1190   # MEASURED@...same file:arms.OPEN_RELATION_strict.coverage_sentence_rate


def compute_verdict(agg):
    prec = agg["reverb_strict"]["precision_on_attempted"]
    cov = agg["reverb_strict"]["coverage_sentence_rate"]
    guard_ok = agg["guard_checks_ok"]
    oos_ok = agg["oos_control_fired"]

    if prec is None:
        return ("HARD_FAIL", "REVERB emitted zero triples on the whole real-prose sample -- mechanism did not "
                              "fire at all; breadth did NOT close the gap", "no_triples_emitted")

    beats_precision_floor = prec >= 0.40
    beats_coverage_floor = cov > RUNG5_BASELINE_COVERAGE
    hard_pass = beats_precision_floor and beats_coverage_floor and guard_ok and oos_ok
    hard_fail = (prec < 0.25) or (cov <= RUNG5_BASELINE_COVERAGE) or (not guard_ok)

    if hard_pass:
        tier = "HARD_PASS"
    elif hard_fail:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    weakest = "n/a"
    if not hard_pass:
        if prec < 0.40:
            weakest = "reverb_precision_below_0.40_classical_envelope_floor"
        elif cov <= RUNG5_BASELINE_COVERAGE:
            weakest = "reverb_coverage_does_not_beat_rung5_toy_grammar"
        elif not guard_ok:
            weakest = "guard_regression_failed"
        elif not oos_ok:
            weakest = "oos_control_did_not_fire"

    dist = agg["construction_distribution_fractions"]
    dist_str = " ".join(f"{c}={dist[c]:.3f}" for c in CONSTRUCTION_CLASSES)
    delta_p = prec - RUNG5_BASELINE_PRECISION
    delta_c = cov - RUNG5_BASELINE_COVERAGE
    msg = (f"{tier} | HEAD-TO-HEAD vs RUNG5 toy grammar (SAME n={agg['n_total_sentences']} slice): "
           f"REVERB precision={prec:.3f} (delta={delta_p:+.3f}) coverage={cov:.3f} (delta={delta_c:+.3f}) "
           f"recall={agg['reverb_strict']['recall']:.3f} n_attempted={agg['reverb_strict']['n_attempted']}/"
           f"{agg['n_total_sentences']} | RUNG5_BASELINE precision=0.179 coverage=0.119 (MEASURED, same slice) | "
           f"construction_distribution[{dist_str}] | guard_checks_ok={guard_ok} oos_control_fired={oos_ok} | "
           f"weakest={weakest} | classical_envelope_target=0.40-0.60 (HARD-PASS floor 0.40)")
    return tier, msg, weakest


# ---------------------------------------------------------------------------
# boilerplate: start marker / metrics write / crash diagnostic (same pattern as RUNG 5).
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": f"exp_{ANCHOR_NAME}", "smoke": f"exp_{ANCHOR_NAME}_smoke",
           "self_test": f"exp_{ANCHOR_NAME}_selftest"}[run_mode]
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
    os.replace(tmp, out_dir / "metrics.json")


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
# self-test: EXERCISE THE REAL code path (real corpus file, real nltk.pos_tag, real chunker, real extractor).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (real CoNLL-U parse of the local corpus file, real "
          "nltk.pos_tag calls, real RegexpParser NP chunker, real REVERB extractor)...", flush=True)

    # (0) glass-box-legal: static source-scan + RUNTIME transitive sys.modules check.
    _grep_neural_source_ok()
    _ = nltk.pos_tag(["The", "cat", "sat", "."])
    _ = _NP_CHUNKER.parse([("The", "DT"), ("cat", "NN")])
    runtime_hits = _runtime_neural_module_check()
    assert not runtime_hits, f"NEURAL MODULE DETECTED in the transitive runtime import closure: {runtime_hits}"
    print(f"[self_test] glass-box-legal: static source-scan clean AND runtime sys.modules closure clean "
          f"({len(sys.modules)} modules loaded, none neural); nltk.pos_tag=averaged-perceptron, "
          f"nltk.RegexpParser=zero-learned-parameter regex grammar", flush=True)

    # (1) REVERB guard sentences: exact triple-set match on hand-picked sentences that tag correctly under the
    # classical tagger (verified live during authoring -- see completion report for the tagger-mistag cases
    # this cell's REVERB_GUARD deliberately avoids, an honest, declared choice, not cherry-picking the METRIC).
    for sent, gold in REVERB_GUARD:
        got = set(ie_extract_reverb(sent)[0])
        assert got == set(gold), f"REVERB guard regression on {sent!r}: got {got}, expected {set(gold)}"
    print(f"[self_test] REVERB guard: all {len(REVERB_GUARD)} hand-picked sentences (BARE_V, V_P, passive "
          f"by-agent swap, AND-conjunction subject inheritance, pronoun-subject breadth) match exactly",
          flush=True)

    # (2) OOS control: REVERB must also abstain (nltk's averaged-perceptron tagger mistags "sleeps"/"yawns" as
    # nouns in these exact short templates -- VERIFIED live, not assumed -- so no verb is found and REVERB
    # naturally emits nothing; this is the SAME underlying tagger behavior RUNG 5's own OOS check relies on).
    for s in OUT_OF_SCHEMA_CONTROL:
        got = ie_extract_reverb(s)[0]
        assert got == [], f"REVERB unexpectedly extracted on OOS control {s!r}: {got}"
    print("[self_test] OOS control: REVERB abstains on both control sentences (verified, not assumed)",
          flush=True)

    # (3) novel-verb sentence (never in any closed lexicon anywhere in this arc) -- confirms open-vocabulary.
    s = "The boy walked the dog to the store."
    ext = ie_extract_reverb(s)
    assert ("boy", "walk", "dog") in set(ext[0]), f"REVERB failed on a genuinely novel-verb sentence: {ext}"
    print(f"[self_test] REVERB correctly extracts a genuinely novel-verb sentence: {ext[0]}", flush=True)

    # (4) real_code_path (F.1): parse the REAL local corpus file, sample a tiny REAL slice (RUNG 5's own real
    # loader, reused, seed=7), run REVERB + the RUNG-5-imported gold deriver + scorer end-to-end.
    qualifying_sorted = load_qualifying_sentences(CONLLU_PATH)
    assert len(qualifying_sorted) > 100, f"expected a real, sizeable qualifying pool, got {len(qualifying_sorted)}"
    rows, dist = build_rows_for_seed(qualifying_sorted, seed=7, n_per_seed=40)
    assert sum(dist.values()) == 40, f"distribution counts do not sum to sample size: {dist}"
    reverb_res = score_arm(rows, ie_extract_reverb)
    open_res = score_arm(rows, ie_extract_open)
    print(f"[self_test] real_code_path: REAL corpus ({len(qualifying_sorted)} qualifying sentences), tiny "
          f"40-sentence real slice -- distribution={dist} | REVERB coverage={reverb_res['coverage_sentence_rate']:.3f} "
          f"precision={reverb_res['precision_on_attempted']} n_attempted={reverb_res['n_attempted']} | RUNG5-OPEN "
          f"coverage={open_res['coverage_sentence_rate']:.3f} (same tiny slice, informational)", flush=True)
    assert reverb_res["n_attempted"] > 0, ("discriminator-fires check failed: REVERB attempted ZERO sentences "
                                           "on a real 40-sentence slice -- mechanism not genuinely exercised")

    # (5) ARMS-MUST-DIFFER (META_RULE_AF): REVERB vs RUNG5-OPEN vs CLOSED_CURRENT emitted-triple-set hash.
    def _digest(extractor):
        allt = sorted(set(t for r in rows for t in extractor(r["text"])[0]))
        return hashlib.sha256(json.dumps(allt, sort_keys=True).encode()).hexdigest(), len(allt)
    h_reverb, n_reverb = _digest(ie_extract_reverb)
    h_open, n_open = _digest(ie_extract_open)
    h_cur, n_cur = _digest(ie_extract)
    assert len({h_reverb, h_open, h_cur}) == 3, ("META_RULE_AF VIOLATION: REVERB / RUNG5-OPEN / CLOSED_CURRENT "
                                                 "are not pairwise distinct on the real tiny slice")
    print(f"[self_test] PASS | ARMS-MUST-DIFFER verified (REVERB={n_reverb} unique triples, RUNG5-OPEN={n_open}, "
          f"CLOSED_CURRENT={n_cur}, all pairwise distinct, on the real 40-sentence tiny slice)", flush=True)
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
    seeds = [7] if run_mode == "smoke" else SEEDS_FULL
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds) * N_PER_SEED
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[reverb_classical] run_mode={run_mode} seeds={seeds} n_per_seed={N_PER_SEED} "
          f"expected_n_units={expected_n_units} corpus={CONLLU_PATH}", flush=True)

    agg = run_full(seeds, N_PER_SEED)
    tier, msg, weakest = compute_verdict(agg)
    elapsed = time.perf_counter() - t0

    print(f"[reverb_classical] {tier} in {elapsed:.2f}s", flush=True)
    print(f"[reverb_classical] {msg}", flush=True)

    metrics = {
        "verdict": tier,
        "verdict_msg": msg,
        "summary": msg[:300],
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "n_per_seed": N_PER_SEED,
        "expected_n_units": expected_n_units,
        "weakest_interface": weakest,
        "corpus": {
            "name": "UD_English-EWT test split (SAME slice as RUNG 5)", "path": str(CONLLU_PATH),
            "license": "CC BY-SA 4.0", "qualifying_pool_size": agg["qualifying_pool_size"],
            "n_sampled_total": agg["n_total_sentences"],
        },
        "construction_distribution_counts": agg["construction_distribution_counts"],
        "construction_distribution_fractions": agg["construction_distribution_fractions"],
        "per_seed_distribution": agg["per_seed_distribution"],
        "arms": {
            "REVERB_strict": {k: v for k, v in agg["reverb_strict"].items() if k not in ("rows",)},
            "REVERB_relaxed_irregular_verb_diagnostic":
                {k: v for k, v in agg["reverb_relaxed"].items() if k not in ("rows",)},
            "RUNG5_OPEN_RELATION_same_sample_informational":
                {k: v for k, v in agg["rung5_open_strict_same_sample"].items() if k not in ("rows",)},
            "CLOSED_CURRENT_informational":
                {k: v for k, v in agg["closed_current_informational"].items() if k not in ("rows",)},
        },
        "rung5_baseline_measured": {
            "precision_on_attempted": RUNG5_BASELINE_PRECISION, "coverage_sentence_rate": RUNG5_BASELINE_COVERAGE,
            "source": "d:/AI/hd-instrument/data/exp_read_grow_realprose_ud_ewt_rung5_v1/metrics.json:"
                      "arms.OPEN_RELATION_strict",
        },
        "guard_checks_ok": agg["guard_checks_ok"],
        "oos_control_fired": agg["oos_control_fired"],
        "sample_reverb_rows": agg["reverb_strict"]["rows"][:60],
        "prereg": {
            "hard_pass": "reverb_precision_on_attempted>=0.40 AND reverb_coverage_sentence_rate>0.1190 "
                         "(RUNG5 baseline) AND guard_checks_ok AND oos_control_fired",
            "hard_fail": "reverb_precision_on_attempted<0.25 OR reverb_coverage_sentence_rate<=0.1190 OR "
                         "NOT guard_checks_ok",
            "hp_scope": "REVERB_strict is the ONLY gated discriminator; RUNG5_OPEN_RELATION_same_sample and "
                        "CLOSED_CURRENT are informational-only (re-scored on the SAME pooled sample for a "
                        "clean head-to-head, but not separately gated -- their own gates were already resolved "
                        "in RUNG 5's own landed cell).",
            "toolchain_choice": "ReVerb-style (Fader/Soderland/Etzioni 2011) POS-tag-pattern extractor, pure "
                                "Python, no dependency parse, no JVM (java command not found on this host -- "
                                "ClausIE/OLLIE/MaltParser ruled out this cycle). nltk.pos_tag (averaged "
                                "perceptron) + nltk.RegexpParser (hand-written regex NP grammar, zero learned "
                                "parameters) only.",
            "declared_addons": "(a) passive by-agent normalization (relation=verb lemma, args swapped, ONLY "
                                "when the found prep is literally 'by' after a be+VBN verb-group); (b) subject "
                                "inheritance across AND-conjoined verb-groups (reuses the prior verb-group's "
                                "resolved subject instead of the nearest-preceding-NP, which for the second "
                                "conjunct is usually the first clause's object) -- both are simple POS-tag-"
                                "positional rules, NOT a return to dependency parsing.",
            "known_left_as_is_limitations": "relative-clause embedded facts scored as false positives against "
                                            "a matrix-only gold; VP-coordination arg-sharing beyond simple "
                                            "AND; compound-SUBJECT coordination (multiple NPs before the verb) "
                                            "not captured (ReVerb takes one NP per side); copular+adjective "
                                            "(SVA) predicates unhandled (only copular+nominal works); classical "
                                            "tagger mistags on short/ambiguous template sentences.",
            "compute_architecture": "sequential-CPU; pure syntactic pattern-matching + regex chunking, no VSA "
                                    "store; wall time trivial (MEASURED below)",
            "storage_strategy": "no_storage (pure parser-layer + extractor test, no FoundationStore/KGStore)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "runner_python_u_only (timeout_s < 1800; cell wall time is seconds)",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["parse_conllu (RUNG 5, real local corpus file)", "analyze_sentence "
                                         "(RUNG 5, dependency-parse-derived gold, imported unmodified)",
                                         "ie_extract_reverb (NEW, this cell)", "ie_extract_open (RUNG 5, "
                                         "imported, re-scored on same sample for head-to-head)",
                                         "ie_extract (v2, imported unmodified, informational)",
                                         "nltk.pos_tag (real classical averaged-perceptron call)",
                                         "nltk.RegexpParser (real classical regex NP chunker)"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete syntactic pattern-match + the "
                       "classical tagger's own literature-benchmarked accuracy (96-97% PTB, CITED).",
            "glass_box_legal": "static source-scan (no torch/spacy/transformers/stanza imports) AND a runtime "
                               "sys.modules transitive-closure check, both asserted at self-test; java -version "
                               "confirmed unavailable on this host (MEASURED, this cycle) ruling out JVM tools.",
            "prior_work_check": "substrate_query.sh run before authoring (see completion report); this is a "
                                "NEW arm on the actively-developed RUNG 5/9 real-prose reading arc, reusing its "
                                "corpus/gold/scorer unmodified -- not a rediscovery.",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[reverb_classical] metrics written -> {out_dir / 'metrics.json'}", flush=True)
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
