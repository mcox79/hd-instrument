"""tools/measure_definitional_parse_faults_v1.py -- FREQUENCY of the 5 named parse-fault
classes across ALL 1751 v3 definitional facts (not the 50-row hand-scored sample).

READ-ONLY. Touches nothing under data/foundation/. Writes only
data/analysis_definitional_parse_faults_v1/metrics.json.

Each detector is a SURFACE test over the stored fact fields + its own source sentences, so
every count is auditable by re-reading the rows it flags (examples are dumped per class).
These are FAULT-SUSPICION counts, not hand-scored NOISE counts: a flagged row is one where
the named parse mechanism fired, which is not the same as the fact being wrong.

Fault classes (from the director's per-row scoring of the 22 NOISE rows):
  F1  proper-noun / common-noun collision   (fan->expert, technology->seller)
  F2  coordinate list read as an appositive (kidney->ureter, system->locomotion)
  F3  subject truncation losing the modifier ("transcription bubble" stored as `bubble`)
  F4  polarity inversion                    (structure->function from "without function")
  F5  truncated / adjectival definiens head (dialysis->medical, kidney->pair)
  F6  glossary run-on (no sentence boundary between glossary entries) -- ADDED by measurement,
      not in the director's list; found while verifying F5 (cancer->collective).

ASCII-only.
"""

from __future__ import annotations

import io
import json
import os
import re
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

FACTS = os.path.join(REPO, "data", "foundation", "reading_grounding_v3_definitional",
                     "definitional_facts.jsonl")
OUT_DIR = os.path.join(REPO, "data", "analysis_definitional_parse_faults_v1")

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")

_DET = {"a", "an", "the", "this", "that", "these", "those", "its", "their", "his", "her",
        "our", "your", "my", "some", "any", "each", "every", "one", "all", "both"}

# F2: verbs that introduce an enumeration of parts
_ENUM_TRIGGER = re.compile(
    r"\b(?:consists?\s+of|consisted\s+of|comprised\s+of|comprises|composed\s+of|"
    r"made\s+up\s+of|made\s+of|divided\s+into|consisting\s+of|including|include[sd]?|"
    r"such\s+as|contains?|containing|has\s+a\s+unique|between)\b", re.IGNORECASE)

# F4: negation / exclusion cues
_NEG = {"without", "no", "not", "non", "lacking", "lack", "lacks", "absence", "absent",
        "rather", "instead", "unlike", "never", "cannot", "except", "excluding", "neither",
        "nor", "un-"}

# F5: measure / partitive heads whose real content sits in the of-complement
_MEASURE = {"pair", "group", "number", "set", "collection", "variety", "bunch", "couple",
            "series", "amount", "lot", "class", "kind", "type", "sort", "form", "piece",
            "part", "member", "range", "array", "list", "handful", "majority", "portion"}

_FINITE_VERB = {"is", "are", "was", "were", "has", "have", "had", "do", "does", "did",
                "can", "will", "would", "said", "says", "means", "include", "includes",
                "become", "becomes", "occurs", "occur", "produces", "produce"}


def toks(s):
    return _TOKEN_RE.findall(s or "")


def content_toks(s):
    return [t for t in toks(s) if t.lower() not in _DET]


_WN = None


def wn():
    global _WN
    if _WN is None:
        from nltk.corpus import wordnet
        wordnet.synsets("dog")
        _WN = wordnet
    return _WN


def is_wn_noun(lemma):
    try:
        return bool(wn().synsets(lemma, pos="n"))
    except Exception as exc:  # noqa: BLE001 - degraded WordNet must be LOUD, not silent
        raise RuntimeError("WordNet unavailable; measurement cannot proceed") from exc


def in_wordnet(lemma):
    return bool(wn().synsets(lemma))


# ------------------------------------------------------------------ detectors

def detect_f1(r):
    """Proper-noun handling. Returns (flag, subclass)."""
    dfd = r.get("definiendum_surface") or ""
    dtoks = toks(dfd)
    if not dtoks:
        return False, None
    head_surface = dtoks[-1]
    if not head_surface[:1].isupper():
        return False, None
    # capitalised: is it capitalised because it is sentence-initial, or is it a real name?
    non_initial_cap = False
    preceded_by_cap = False
    for s in r.get("source_sentences", []):
        st = toks(s)
        for i, t in enumerate(st):
            if t == head_surface and i > 0:
                non_initial_cap = True
                if st[i - 1][:1].isupper() and st[i - 1].lower() not in _DET:
                    preceded_by_cap = True
    if not non_initial_cap:
        return False, None            # sentence-initial capital only -> ordinary common noun
    subj = r["subject"]
    collides = is_wn_noun(subj)
    if collides and preceded_by_cap:
        return True, "F1a_COLLIDES_AND_NAME_TRUNCATED"
    if collides:
        return True, "F1a_COLLIDES_WITH_COMMON_NOUN"
    if preceded_by_cap:
        return True, "F1c_NAME_TRUNCATED_ONLY"
    return False, "F1b_CLEAN_PROPER_NOUN"   # legitimate: piraeus->port, omikron->game


def detect_f2(r):
    """Coordinate list mis-read as an appositive / definiens."""
    dfs = r.get("definiens_surface") or ""
    dfd = r.get("definiendum_surface") or ""
    ft = toks(dfs)
    if ft and ft[0].lower() in ("and", "or"):
        return True, "F2c_DEFINIENS_STARTS_WITH_COORDINATOR"
    sent = (r.get("source_sentences") or [""])[0]
    # locate definiendum in the sentence; look at what precedes it
    idx = sent.lower().find(dfd.lower()) if dfd else -1
    if idx > 0 and _ENUM_TRIGGER.search(sent[:idx]):
        # enumeration verb before the definiendum AND the definiens is a bare NP
        if len(content_toks(dfs)) <= 2:
            return True, "F2a_ENUMERATION_TRIGGER_PLUS_BARE_NP"
    # coordinate tail: after the definiens, more BARE NPs joined by and/or, with no verb of
    # any form in between. TIGHTENED after spot-check: the loose version flagged
    # `aorta -> artery` ("..., taking oxygenated blood to the organs and muscles"), where the
    # tail is a participial adjunct of the main clause, not a further list item.
    if len(content_toks(dfs)) > 3:
        return False, None                 # a descriptive definiens is not a list item
    j = sent.lower().find(dfs.lower())
    if j >= 0:
        tail = sent[j + len(dfs):]
        low = [t.lower() for t in toks(tail)]
        if ("and" in low or "or" in low):
            cut = low.index("and") if "and" in low else low.index("or")
            pre = low[:cut]
            verbish = any(t in _FINITE_VERB or t.endswith("ing") or t == "to" for t in pre)
            # what FOLLOWS the coordinator decides list-vs-coordinated-clause:
            # "urinary bladder and urethra"  -> bare NP        -> LIST
            # "..., and Indonesia is the biggest exporter" / "and it represents ..." -> CLAUSE
            post = low[cut + 1: cut + 6]
            clause_after = any(t in _FINITE_VERB for t in post) or (
                post and post[0] in ("it", "they", "he", "she", "we", "this", "that", "there"))
            if cut <= 4 and not verbish and not clause_after:
                return True, "F2b_COORDINATE_TAIL_NO_FINITE_VERB"
    return False, None


def detect_f3(r):
    """Subject truncation: the definiendum surface is a multiword term but only its head
    lemma was stored as the subject."""
    dfd = r.get("definiendum_surface") or ""
    ct = content_toks(dfd)
    if len(ct) <= 1:
        return False, None
    if len(ct) > 4 or any(t.lower() in _FINITE_VERB for t in ct):
        return True, "F3b_RUNON_DEFINIENDUM"      # not a term at all (glossary run-on)
    return True, "F3a_MULTIWORD_TERM_TRUNCATED"


def detect_f4(r):
    """Polarity inversion: a negation cue sits between the start of the definiens and the
    stored object, so the definiens ASSERTS THE ABSENCE of the object."""
    dfs = r.get("definiens_surface") or ""
    low = [t.lower() for t in toks(dfs)]
    obj = r["object"]
    if not low:
        return False, None
    pos_obj = None
    for i, t in enumerate(low):
        if t.startswith(obj[: max(3, len(obj) - 2)]):
            pos_obj = i
            break
    # TIGHTENED after spot-check: "negation ANYWHERE before the object" flagged
    # `mesophyll -> layer` from "not on the surface layers, BUT RATHER in a middle layer
    # called the mesophyll" -- there the object sits in the POSITIVE branch of a contrast.
    # Real polarity inversion needs the negator to SCOPE OVER the object, which for these
    # surface patterns means immediate adjacency and an exclusion cue (not a contrast cue).
    scoping = {"without", "lacking", "lack", "lacks", "absence", "absent", "no", "non",
               "not", "never", "cannot"}
    negs = [i for i, t in enumerate(low) if t in scoping]
    if not negs or pos_obj is None:
        return False, None
    if any(0 <= pos_obj - i <= 2 for i in negs):
        return True, "F4a_NEGATION_SCOPES_OVER_OBJECT"
    return False, None


def detect_f5(r):
    """Definiens head faults: adjectival head, or a measure/partitive head whose content
    sits in the of-complement."""
    obj = r["object"]
    dfs = r.get("definiens_surface") or ""
    if in_wordnet(obj) and not is_wn_noun(obj):
        return True, "F5a_HEAD_NOT_A_NOUN"
    if obj in _MEASURE:
        m = re.search(r"\b" + re.escape(obj) + r"[a-z]*\s+of\s+(?P<comp>.{2,60})", dfs,
                      re.IGNORECASE)
        if m:
            comp = m.group("comp")
            first = (toks(comp) or [""])[0].lower()
            if first not in ("the", "this", "that", "its", "their", "his", "her"):
                return True, "F5b_MEASURE_HEAD_INDEFINITE_OF_COMPLEMENT"
            return True, "F5c_MEASURE_HEAD_DEFINITE_OF_COMPLEMENT"
        return True, "F5d_MEASURE_HEAD_NO_OF_COMPLEMENT"
    return False, None


def detect_f6(r):
    """Glossary run-on: a second `term:` entry inside the same 'sentence', so definiens and
    definiendum straddle two dictionary entries."""
    dfs = r.get("definiens_surface") or ""
    dfd = r.get("definiendum_surface") or ""
    if re.search(r"[a-z]\s*:\s*[a-z]", dfs) or re.search(r"[a-z]\s*:\s*[a-z]", dfd):
        return True, "F6_GLOSSARY_RUNON"
    return False, None


DETECTORS = [("F1_proper_noun", detect_f1), ("F2_list_as_appositive", detect_f2),
             ("F3_subject_truncation", detect_f3), ("F4_polarity_inversion", detect_f4),
             ("F5_bad_definiens_head", detect_f5), ("F6_glossary_runon", detect_f6)]


def multisense_yield(rows):
    """Counts the sense eval depends on: multi-sense words, and senses (facts) carrying more
    than one source sentence."""
    by_subj = defaultdict(set)
    for r in rows:
        by_subj[r["subject"]].add(r["object"])
    multi = {s for s, o in by_subj.items() if len(o) > 1}
    facts_in_multi = [r for r in rows if r["subject"] in multi]
    n_sent = Counter(len(r.get("source_sentences") or []) for r in facts_in_multi)
    senses_multi_sent = sum(1 for r in facts_in_multi
                            if len(r.get("source_sentences") or []) > 1)
    # words where EVERY sense has >1 sentence (the population a leave-one-sentence-out
    # sense-selection eval can actually run on)
    per_word = defaultdict(list)
    for r in facts_in_multi:
        per_word[r["subject"]].append(len(r.get("source_sentences") or []))
    words_all_multi = sum(1 for s, v in per_word.items() if all(x > 1 for x in v))
    words_any_multi = sum(1 for s, v in per_word.items() if any(x > 1 for x in v))
    return {
        "n_facts": len(rows),
        "n_distinct_subjects": len(by_subj),
        "n_multi_sense_words": len(multi),
        "n_facts_in_multi_sense_words": len(facts_in_multi),
        "n_senses_with_gt1_source_sentence": senses_multi_sent,
        "n_multi_sense_words_with_ALL_senses_gt1_sentence": words_all_multi,
        "n_multi_sense_words_with_ANY_sense_gt1_sentence": words_any_multi,
        "sentence_count_dist_in_multi_sense": dict(sorted(n_sent.items())),
    }


def main():
    rows = [json.loads(l) for l in io.open(FACTS, encoding="utf-8") if l.strip()]
    per_class = {}
    flags_per_row = [set() for _ in rows]
    for name, fn in DETECTORS:
        sub = Counter()
        hits = []
        for i, r in enumerate(rows):
            flag, subclass = fn(r)
            if flag:
                sub[subclass] += 1
                hits.append(i)
                flags_per_row[i].add(name)
            elif subclass:
                sub[subclass] += 1          # informational sub-class (e.g. clean proper noun)
        per_class[name] = {
            "n_flagged": len(hits),
            "frac_of_1751": round(len(hits) / len(rows), 4),
            "subclasses": dict(sub),
            "examples": [
                {"subject": rows[i]["subject"], "object": rows[i]["object"],
                 "pattern": rows[i]["pattern"],
                 "definiendum_surface": rows[i]["definiendum_surface"],
                 "definiens_surface": rows[i]["definiens_surface"][:90],
                 "sentence": (rows[i]["source_sentences"] or [""])[0][:160]}
                for i in hits[:12]],
        }
    n_any = sum(1 for f in flags_per_row if f)
    overlap = Counter(tuple(sorted(f)) for f in flags_per_row if f)
    metrics = {
        "verdict": "MEASURED",
        "verdict_msg": "parse-fault frequency over all %d v3 definitional facts; %d rows (%.1f%%) "
                       "carry >=1 fault flag" % (len(rows), n_any, 100.0 * n_any / len(rows)),
        "summary": "definitional parse-fault frequency v1",
        "elapsed_s": 0.0,
        "n_facts": len(rows),
        "n_rows_with_any_flag": n_any,
        "frac_rows_with_any_flag": round(n_any / len(rows), 4),
        "per_class": per_class,
        "flag_cooccurrence_top20": [{"classes": list(k), "n": v}
                                    for k, v in overlap.most_common(20)],
        "multisense_yield_BEFORE": multisense_yield(rows),
        "source": FACTS,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    for name, d in per_class.items():
        print("%-24s %4d  %6.2f%%  %s" % (name, d["n_flagged"], 100 * d["frac_of_1751"],
                                          d["subclasses"]))
    print("ANY FLAG: %d / %d (%.1f%%)" % (n_any, len(rows), 100.0 * n_any / len(rows)))
    print(json.dumps(metrics["multisense_yield_BEFORE"], indent=2))


if __name__ == "__main__":
    main()
