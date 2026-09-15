"""exp_case_through_the_reader_v1 -- FLIP THE CASE THROUGH THE LIVE READER and measure it where it lands.

problem: the_reader_lowercases_every_token_at_its_one_sentence_source_so_the_category_organ_misses_70_percent_
         of_proper_nouns_on_the_live_path_flip_the_case_through_with_a_board_ab   (priority 116)

THE DEFECT. `hdlab/scene_segment.parse_conll_sentences` is the live reader's ONE sentence source and it
LOWERCASES every token (`cols[3].lower()`, `lower=True` the shipped default at 3 of its 4 hdlab call sites).
pri 109 measured the cost AT THE ORGAN on GUM test (127,919 tokens, same organ, same text, case the only
difference): PROPN P/R/F1 0.9050/0.8232/0.8622 cased vs 0.9417/0.2996/0.4546 lowercased, all-tag 0.9302 ->
0.9027. This cell measures it THROUGH THE LIVE READER on MODERN gold (GUM, converted to the reader's own
CoNLL by the landed `exp_crosstype_gum_conll_fullread_v1.gum_to_conll`) and measures every consumer the
flip reaches.

THE FINDING THAT MADE THE FLIP BIGGER THAN A CASE FIX (this cell, phase 3): pri 112's ONE IN-ORDER FEED
(`situation_reader.read`, line ~4498) ALREADY reads the passage with `lower=False` and caches the settled
CASED posterior under `_read_parse_cache[("tag", tuple(cased_sentence))]`. Every consumer then asks
`_cached_tag(sents[i])` with the LOWERCASED sentence -- a DIFFERENT dict key -- so the feed's cased belief
is never read, the sentence is re-tagged on case-stripped text, and the reader computes the good answer and
throws it away. MEASURED: 100% of sentences tagged TWICE per read (once cased, never read; once lowercased,
read by everything). `lower=False` at the three remaining call sites makes the keys identical, so the flip
both restores the case cue AND turns pri 112's in-order feed into the thing the consumers actually read.

ARMS (the reader is UNPATCHED; the case is forced at my harness level, so no hdlab/ file is written):
  low        as it ships (lower=True at the 3 consumer call sites)
  cased      lower=False forced at every call site -- the proposed flip
  twin       lower=False on a CASE-SCRAMBLED document: the per-token capitalisation flags of each sentence
             are PERMUTED (same number of capitals per sentence, random positions) -> information-free about
             WHICH word is a name, and it must LOSE
  cased_span cased + the ONE consumer repair the flip exposes: `referent_per_np._mk_referent` keeps the
             LOWERCASED identity key in `head` (case-insensitive by design) and stores the CASED token in
             `span_toks`, so `coref.name_content_tokens`' capitalisation route is alive again

ROWS (per document, doc-paired bootstrap 2,000 resamples, floors recomputed on each arm's own population):
  categories   the tags the reader's consumers ACTUALLY READ (logged at `_cached_tag`), scored against GUM
               gold UPOS: all-tag accuracy + PROPN P/R/F1.  FLOOR = the `low` arm.
  feed         the tags pri 112's in-order feed computed, scored the same way (the signal that exists and is
               not read under `low`).
  entities     sm.entities / entities with a surface head / NAME mentions typed on the referent stream.
  coref        sm.coref_resolutions pronoun accuracy on GUM gold clusters (modern).
  whodidwhat   sm.events agent / patient vs a GUM-deprel gold, against the POSITIONAL floor.

Glass-box: no external LLM, no spaCy, no nltk, no supervised parser at inference. GUM is MODERN gold.
Run: .venv/Scripts/python.exe experiments/exp_case_through_the_reader_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_case_through_the_reader_v1.py --run --docs 12
     .venv/Scripts/python.exe experiments/exp_case_through_the_reader_v1.py --board-probe
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")
import argparse
import json
import random
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir

ANCHOR = "case_through_the_reader_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
SEED = 20260914
NBOOT = 2000

# ---------------------------------------------------------------------------------------------- arms
ARMS = ("low", "cased", "twin", "cased_span", "cased_repair")


# ---------------------------------------------------------------------------------------------- the case harness
class CaseHarness:
    """Force the sentence source's `lower=` at every hdlab call site WITHOUT editing hdlab/.

    The three consumer call sites pass `lower=True` EXPLICITLY (pri 109 landed the parameter that way), and
    the in-order category feed already passes `lower=False`; forcing False everywhere is EXACTLY the proposed
    flip, and `install(None)` restores the shipped behaviour byte-for-byte.
    """

    def __init__(self):
        import hdlab.scene_segment as SS
        self._orig = SS.parse_conll_sentences
        self._mods = []
        for name in ("hdlab.scene_segment", "hdlab.situation_reader", "hdlab.referent_per_np",
                     "hdlab.space_reader"):
            __import__(name)
            m = sys.modules[name]
            if getattr(m, "parse_conll_sentences", None) is not None:
                self._mods.append(m)
        self.n_calls = 0
        self.forced = None

    def install(self, forced):
        """forced None -> shipped default; False -> cased everywhere; True -> lowercased everywhere."""
        self.forced = forced
        orig = self._orig

        def f(path, lower=True):
            self.n_calls += 1
            return orig(path, lower=(lower if self.forced is None else self.forced))
        for m in self._mods:
            m.parse_conll_sentences = f

    def restore(self):
        for m in self._mods:
            m.parse_conll_sentences = self._orig


class TagLog:
    """Record every tag the reader's consumers actually READ (`SituationReader._cached_tag`), with whether the
    per-read cache already held it. Pure measurement -- identical in every arm."""

    def __init__(self):
        import hdlab.situation_reader as HSR
        self.HSR = HSR
        self._orig = HSR.SituationReader._cached_tag
        self.calls = []          # (tuple(toks), tuple(tags), was_hit)
        log = self

        def _ct(slf, toks):
            key = ("tag", tuple(toks))
            hit = key in slf._read_parse_cache
            out = log._orig(slf, toks)
            log.calls.append((tuple(toks), tuple(out), bool(hit)))
            return out
        HSR.SituationReader._cached_tag = _ct

    def reset(self):
        self.calls = []

    def restore(self):
        self.HSR.SituationReader._cached_tag = self._orig


# ---------------------------------------------------------------------------------------------- consumer repair
def _mk_referent_cased(head_raw, sent_idx, wpos, cluster, midx, upos=None):
    """The PROPOSED `referent_per_np._mk_referent`: the identity key stays LOWERCASED (`head` is a
    case-insensitive lookup key for every downstream dict) and `span_toks` keeps the RAW-CASED token, so
    `coref.name_content_tokens`' capitalisation route can fire on the referent stream. Byte-identical when the
    caller hands it an already-lowercased token (the shipped path)."""
    head_low = head_raw.lower()
    d = {"cluster": cluster, "gtok_start": -1, "gtok_end": -1, "sent_idx": sent_idx,
         "wtok_start": wpos, "head": head_low, "is_pronoun": False,
         "gender": None, "number": None, "name_gender": None, "span_toks": [head_raw], "midx": midx}
    if upos is not None:
        d["span_upos"] = [upos]
    return d


def _rnp_source_cased(conll_path, tagger, name_gender_map=None, use_frame=True):
    """VERBATIM `hdlab.referent_per_np.referent_per_np_source` with exactly TWO changes (the diff):
    `lower=False` at the sentence source, and the RAW-CASED token handed to `_mk_referent`."""
    import hdlab.referent_per_np as RNP
    from hdlab.coref import parse_litbank_conll
    from hdlab.affected_entity_resolver import is_reflexive, REFLEXIVE_GN
    coref, n_sents = parse_litbank_conll(conll_path, name_gender_map=name_gender_map, tagger=tagger)
    sents = RNP.parse_conll_sentences(conll_path, lower=False)
    coref_head_wpos = {}
    pron = []
    for m in coref:
        if m["is_pronoun"]:
            pron.append(m)
        elif is_reflexive(m.get("head")):
            g, n = REFLEXIVE_GN.get(m["head"].lower(), (None, None))
            m = dict(m); m["is_pronoun"] = True
            m["gender"] = m.get("gender") or g; m["number"] = m.get("number") or n
            pron.append(m)
    refl_pos = {(m["sent_idx"], m["wtok_start"]) for m in pron if is_reflexive(m.get("head"))}
    for m in coref:
        if m["is_pronoun"] or is_reflexive(m.get("head")):
            continue
        span = max(0, m["gtok_end"] - m["gtok_start"])
        coref_head_wpos[(m["sent_idx"], m["wtok_start"] + span)] = m["cluster"]
    next_cluster = max([m["cluster"] for m in coref], default=-1) + 1
    out = []
    for si, toks in enumerate(sents):
        if si >= n_sents:
            break
        up = tagger.tag(list(toks))
        base = RNP._content_head_positions(toks, up)
        heads = sorted(set(base) | RNP.frame_heads(toks, up, set(base))) if use_frame else base
        for hw in heads:
            if (si, hw) in refl_pos:
                continue
            cl = coref_head_wpos.get((si, hw))
            if cl is None:
                cl = next_cluster
                next_cluster += 1
            out.append(_mk_referent_cased(toks[hw], si, hw, cl, -1,
                                          upos=up[hw] if hw < len(up) else None))
    return RNP._finalize(pron + out), n_sents


# -------------------------------------------------------------------------------- the CONSUMER REPAIRS the flip exposes
# Two live consumers gate on a RAW token matching a lowercase literal, so a sentence-initial connective /
# auxiliary stops matching the moment the case reaches them. They are case-insensitive BY DESIGN (a closed-class
# cue word is the same word capitalised), so the repair is to fold case AT THE LOOKUP -- which is exactly what
# the brief asks for, and what every other consumer on this path already does.
REPAIRS = [
    ("_read_causation",
     "                if not (_CAUSAL_CONNECTIVES & set(toks)):",
     "                if not (_CAUSAL_CONNECTIVES & {t.lower() for t in toks}):"),
    ("_read_causation",
     "            if _CAUSAL_CONNECTIVES & set(toks):",
     "            if _CAUSAL_CONNECTIVES & {t.lower() for t in toks}:"),
    ("_read_timeline",
     '            if "had" not in toks:',
     '            if "had" not in [t.lower() for t in toks]:'),
]


def install_repairs():
    """Rebind the two methods from their OWN source with the one-line case fold applied -- the same edit the
    proposed diff makes, executed rather than described. Returns a restore() closure."""
    import inspect, textwrap
    import hdlab.situation_reader as HSR
    saved = {}
    byname = defaultdict(list)
    for name, old, new in REPAIRS:
        byname[name].append((old, new))
    for name, edits in byname.items():
        fn = getattr(HSR.SituationReader, name)
        saved[name] = HSR.SituationReader.__dict__[name]
        src = textwrap.dedent(inspect.getsource(fn))
        static = src.lstrip().startswith("@staticmethod")
        if static:
            src = src.split(chr(10), 1)[1]
        src = textwrap.dedent(src)
        for old, new in edits:
            o, n = textwrap.dedent(old), textwrap.dedent(new)
            if src.count(o) != 1:
                raise RuntimeError("REPAIR ANCHOR NOT UNIQUE in %s: %r (%d)" % (name, o, src.count(o)))
            src = src.replace(o, n)
        ns = {}
        exec(compile(src, "<case_repair:%s>" % name, "exec"), vars(HSR), ns)
        new_fn = ns[name]
        setattr(HSR.SituationReader, name, staticmethod(new_fn) if static else new_fn)

    def restore():
        for k, v in saved.items():
            setattr(HSR.SituationReader, k, v)
    return restore


# ---------------------------------------------------------------------------------------------- gold / corpus
def gold_sentences(doc):
    """[(forms, upos)] per sentence, in the reader's sentence order (the converter preserves it)."""
    by = defaultdict(list)
    for t in doc.toks:
        by[t.sent].append(t)
    out = []
    for si in sorted(by):
        toks = sorted(by[si], key=lambda t: t.idx)
        out.append(([t.form for t in toks], [t.upos for t in toks]))
    return out


def scramble_case(forms, rng):
    """INFO-FREE TWIN: keep each sentence's NUMBER of capital-initial tokens and PERMUTE which of the
    CAPITALISABLE tokens (alphabetic first character) get them. Same orthographic 'capital budget', zero
    information about WHICH word is a name. A token that cannot carry a capital (punctuation, a digit) is
    excluded from the permutation so the count is preserved exactly."""
    cap_ix = [i for i, w in enumerate(forms) if w[:1].isalpha()]
    flags = [bool(forms[i][:1].isupper()) for i in cap_ix]
    rng.shuffle(flags)
    out = [w.lower() for w in forms]
    for i, f in zip(cap_ix, flags):
        if f:
            wl = out[i]
            out[i] = wl[:1].upper() + wl[1:]
    return out


def write_conll(docid, sents, gold_mentions, path):
    """The reader's OntoNotes-style coref CoNLL for a token-per-sentence list + gold mention spans (global
    token index). Same column layout as exp_crosstype_gum_conll_fullread_v1.gum_to_conll."""
    opens = defaultdict(list); closes = defaultdict(list); singles = defaultdict(list)
    for (s0, s1, eid) in gold_mentions:
        if s0 == s1:
            singles[s0].append(eid)
        else:
            opens[s0].append((s1, eid)); closes[s1].append((s0, eid))
    lines = ["#begin document (%s); part 0" % docid]
    g = 0
    for toks in sents:
        for w, form in enumerate(toks):
            parts = []
            for _e, eid in sorted(opens.get(g, []), reverse=True):
                parts.append("(%d" % eid)
            for eid in singles.get(g, []):
                parts.append("(%d)" % eid)
            for _s, eid in sorted(closes.get(g, []), reverse=True):
                parts.append("%d)" % eid)
            coref = "|".join(parts) if parts else "_"
            lines.append("\t".join([docid, "0", str(w), form if form else "_",
                                    "_", "_", "_", "_", "_", "_", "_", "_", coref]))
            g += 1
        lines.append("")
    lines.append("#end document")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def gold_roles(doc):
    """A GUM-deprel who-did-what gold, one record per clause whose predicate has BOTH a nominal subject and a
    direct object (the board's UD-EWT construction, on GUM's own gold deprels):
        {sent, pred_form, agent_low, patient_low, pred_i, subj_i, obj_i, forms}
    The treebank is the ANSWER KEY only -- no reader decision reads it."""
    by = defaultdict(list)
    for t in doc.toks:
        by[t.sent].append(t)
    recs = []
    for si in sorted(by):
        toks = sorted(by[si], key=lambda t: t.idx)
        ix = {t.idx: t for t in toks}
        for t in toks:
            if t.upos not in ("VERB",):
                continue
            subj = [c for c in toks if c.head == t.idx and c.deprel.split(":")[0] in ("nsubj",)
                    and c.upos in ("NOUN", "PROPN", "PRON")]
            obj = [c for c in toks if c.head == t.idx and c.deprel.split(":")[0] in ("obj",)
                   and c.upos in ("NOUN", "PROPN", "PRON")]
            if len(subj) != 1 or len(obj) != 1:
                continue
            recs.append({"sent": si, "pred": t.form.lower(), "pred_i": t.idx - 1,
                         "agent": subj[0].form.lower(), "patient": obj[0].form.lower(),
                         "subj_i": subj[0].idx - 1, "obj_i": obj[0].idx - 1,
                         "forms": [x.form for x in toks], "upos": [x.upos for x in toks]})
        _ = ix
    return recs


def positional_floor(rec):
    """The board's own who-did-what FLOOR: the nearest nominal (gold UPOS) to the LEFT of the predicate is the
    agent, the nearest to the RIGHT is the patient. Knowledge-free word order."""
    forms, up, pi = rec["forms"], rec["upos"], rec["pred_i"]
    ag = pa = None
    for j in range(pi - 1, -1, -1):
        if up[j] in ("NOUN", "PROPN", "PRON"):
            ag = forms[j].lower(); break
    for j in range(pi + 1, len(forms)):
        if up[j] in ("NOUN", "PROPN", "PRON"):
            pa = forms[j].lower(); break
    return ag, pa


# ---------------------------------------------------------------------------------------------- scoring one read
def _tally(tags, gold):
    c = {"n": 0, "corr": 0, "tp": 0, "fp": 0, "fn": 0, "sents": 0}
    for t, g in zip(tags, gold):
        for gg, pp in zip(g, t):
            c["n"] += 1
            c["corr"] += int(gg == pp)
            if pp == "PROPN" and gg == "PROPN":
                c["tp"] += 1
            elif pp == "PROPN":
                c["fp"] += 1
            elif gg == "PROPN":
                c["fn"] += 1
        c["sents"] += 1
    return c


def score_categories(taglog_calls, gsents, cache, arm_sents, file_sents):
    """THE TWO TAG STREAMS THE READER ACTUALLY HAS, scored against the SAME GUM gold UPOS.

    main   -- the tags keyed by the token lists in the reader's `sents` variable, i.e. what EVERY organ that
              receives `sents` reads (events, roles, timeline, world-state, goals, affect, senses, causation,
              space, bridges, affected-entity, ...). This is the row the flip moves.
    coref  -- the tags keyed by the RAW-CASED tokens of the CoNLL file, i.e. what `coref.parse_litbank_conll`'s
              mention typing reads. Already cased in BOTH arms (pri 109's 18c-bis), so it is the control that
              says the difference below is the `sents` stream and nothing else.
    """
    main_t, main_g, cor_t, cor_g = [], [], [], []
    for si, (forms, up) in enumerate(gsents):
        if si >= len(arm_sents):
            break
        t = cache.get(("tag", tuple(arm_sents[si])))
        if t is not None and len(t) == len(up):
            main_t.append(t); main_g.append(up)
        t2 = cache.get(("tag", tuple(file_sents[si])))
        if t2 is not None and len(t2) == len(up):
            cor_t.append(t2); cor_g.append(up)
    main = _tally(main_t, main_g)
    cor = _tally(cor_t, cor_g)
    # WIRING: how much of the reader READS a case-stripped sentence, and how much work is done twice
    n_hit = sum(1 for _t, _g, h in taglog_calls if h)
    calls_low = sum(1 for t, _g, _h in taglog_calls if all(w == w.lower() for w in t))
    calls_cased = len(taglog_calls) - calls_low
    keys = [k[1] for k in cache if isinstance(k, tuple) and len(k) == 2 and k[0] == "tag"]
    low_keys = {k for k in keys if all(w == w.lower() for w in k)}
    cased_keys = {k for k in keys if any(w != w.lower() for w in k)}
    dup = sum(1 for k in cased_keys if tuple(w.lower() for w in k) in low_keys)
    wiring = {"tag_calls": len(taglog_calls), "cache_hits": n_hit,
              "cache_misses": len(taglog_calls) - n_hit,
              "calls_on_lowercased_text": calls_low, "calls_on_cased_text": calls_cased,
              "cache_tag_entries": len(keys), "cased_entries": len(cased_keys),
              "lower_entries": len(low_keys), "sentences_tagged_under_both_casings": dup}
    return main, cor, wiring


def score_coref(sm):
    rs = list(getattr(sm, "coref_resolutions", []) or [])
    return {"n": len(rs), "corr": sum(1 for r in rs if r.correct),
            "att": sum(1 for r in rs if r.attempted)}


def score_entities(sm, role_mentions):
    from hdlab.coref import name_content_tokens
    ents = list(getattr(sm, "entities", []) or [])
    named = 0
    for m in role_mentions:
        if m.get("is_pronoun"):
            continue
        if name_content_tokens(m.get("span_toks", [m.get("head", "")]), upos=m.get("span_upos")):
            named += 1
    return {"entities": len(ents), "with_heads": sum(1 for e in ents if e.heads),
            "name_typed": named, "nonpron_mentions": sum(1 for m in role_mentions if not m.get("is_pronoun"))}


def score_events_vs_gold(sm, doc):
    """THE EVENT-DETECTION ROW, so a raw count change cannot be mistaken for a regression. Gold = every token
    GUM tags VERB (the answer key; pri 113 also fires events on a NON-VERBAL predicate slot, so a predicate the
    gold calls ADJ/NOUN is counted separately rather than as a false positive)."""
    by = defaultdict(list)
    for t in doc.toks:
        by[t.sent].append(t)
    gold = {}
    upos_at = {}
    for si in sorted(by):
        toks = sorted(by[si], key=lambda t: t.idx)
        gold[si] = {i for i, t in enumerate(toks) if t.upos == "VERB"}
        upos_at[si] = [t.upos for t in toks]
    pred = defaultdict(set)
    for e in getattr(sm, "events", []) or []:
        i = getattr(e, "pred_idx", None)
        if i is not None:
            pred[e.sent_idx].add(int(i))
    tp = fp = fn = 0
    nonverb = defaultdict(int)
    for si, g in gold.items():
        p = pred.get(si, set())
        tp += len(g & p); fn += len(g - p); fp += len(p - g)
        for i in (p - g):
            up = upos_at[si][i] if i < len(upos_at[si]) else "?"
            nonverb[up] += 1
    return {"tp": tp, "fp": fp, "fn": fn, "n": tp + fn,
            **{"fp_gold_" + k: v for k, v in nonverb.items()}}


def sm_summary(sm):
    """THE NO-REGRESS POPULATION: one count per situation-model dimension the reader built. Every one of these
    organs receives the reader's `sents`, so every one of them is a consumer of the case decision. A count that
    DROPS under the flip is a consumer to repair (never a reason to revert the brain-foundational rung)."""
    def n(x):
        try:
            return len(x)
        except Exception:
            return 0
    loc = getattr(sm, "locations", None)
    ws = getattr(sm, "world_state", None)
    out = {
        "events": n(getattr(sm, "events", [])),
        "suppressed_predicates": n(getattr(sm, "suppressed_predicates", [])),
        "coref_resolutions": n(getattr(sm, "coref_resolutions", [])),
        "timeline_frames": n(getattr(sm, "timeline_frames", [])),
        "timeline_order": n(getattr(sm, "timeline_order", [])),
        "causal_links": n(getattr(sm, "causal_links", [])),
        "typed_causal_links": n(getattr(sm, "typed_causal_links", [])),
        "inferred_coherence_links": n(getattr(sm, "inferred_coherence_links", [])),
        "entities": n(getattr(sm, "entities", [])),
        "event_tokens": n(getattr(sm, "event_tokens", []) or []),
        "events_with_agent": sum(1 for e in (getattr(sm, "events", []) or []) if e.agent and e.agent != "?"),
        "events_with_patient": sum(1 for e in (getattr(sm, "events", []) or []) if e.patient and e.patient != "?"),
        "events_with_affect": sum(1 for e in (getattr(sm, "events", []) or []) if e.affect),
        "events_with_subj_role": sum(1 for e in (getattr(sm, "events", []) or []) if e.subj_role),
        "locations": n(getattr(loc, "nodes", []) if loc is not None else []),
    }
    for attr in ("bridges", "senses", "entity_states"):
        out[attr] = n(getattr(sm, attr, []) or [])
    gr = getattr(sm, "goal_register", None)
    if gr is not None:
        out["goals"] = n(getattr(gr, "goals", []) or [])
    ar = getattr(sm, "affect_register", None)
    if ar is not None:
        out["affect_states"] = n(getattr(ar, "states", None) or getattr(ar, "affects", None) or [])
    sr = getattr(sm, "state_register", None)
    if sr is not None:
        out["state_records"] = n(getattr(sr, "records", None) or getattr(sr, "_records", None) or [])
    if ws is not None:
        out["world_state_facts"] = n(getattr(ws, "facts", None) or getattr(ws, "_events", None) or [])
    return out


def score_roles(sm, recs):
    """Per gold clause: does the reader's event for that sentence name the gold agent / patient head?
    Matched on the sentence and the predicate surface (case-folded); a clause with no reader event counts as
    wrong (the same abstention-is-an-error convention as the board's who-did-what rows)."""
    ev_by = defaultdict(list)
    for e in getattr(sm, "events", []) or []:
        ev_by[e.sent_idx].append(e)
    out = {"n": 0, "ag": 0, "pa": 0, "ag_f": 0, "pa_f": 0, "matched": 0}
    for r in recs:
        out["n"] += 1
        fa, fp = positional_floor(r)
        out["ag_f"] += int(fa == r["agent"])
        out["pa_f"] += int(fp == r["patient"])
        ev = None
        for e in ev_by.get(r["sent"], []):
            if (e.predicate or "").lower() == r["pred"]:
                ev = e; break
        if ev is None:
            continue
        out["matched"] += 1
        out["ag"] += int((ev.agent or "").lower() == r["agent"])
        out["pa"] += int((ev.patient or "").lower() == r["patient"])
    return out


# ---------------------------------------------------------------------------------------------- bootstrap
def paired_boot(per_doc_a, per_doc_b, num_key, den_key, nboot=NBOOT, seed=SEED):
    """Doc-paired bootstrap of the POOLED ratio difference (a - b). per_doc_* are aligned lists of dicts."""
    a_n = np.array([d[num_key] for d in per_doc_a], float)
    a_d = np.array([d[den_key] for d in per_doc_a], float)
    b_n = np.array([d[num_key] for d in per_doc_b], float)
    b_d = np.array([d[den_key] for d in per_doc_b], float)

    def rat(n, d):
        s = d.sum()
        return float(n.sum() / s) if s else float("nan")
    obs = rat(a_n, a_d) - rat(b_n, b_d)
    rng = np.random.default_rng(seed)
    k = len(a_n)
    ds = np.empty(nboot)
    for i in range(nboot):
        ix = rng.integers(0, k, k)
        ds[i] = rat(a_n[ix], a_d[ix]) - rat(b_n[ix], b_d[ix])
    lo, hi = np.percentile(ds, [2.5, 97.5])
    return [round(obs, 4), round(float(lo), 4), round(float(hi), 4)], bool(lo > 0 or hi < 0)


def f1(c):
    tp, fp, fn = c["tp"], c["fp"], c["fn"]
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    return (round(p, 4), round(r, 4), round(2 * p * r / (p + r), 4) if (p + r) else 0.0)


def boot_f1(per_doc_a, per_doc_b, nboot=NBOOT, seed=SEED):
    """Paired bootstrap of the PROPN F1 DIFFERENCE (F1 is not a ratio of one numerator, so it gets its own)."""
    def F(ds, ix):
        tp = sum(ds[j]["tp"] for j in ix); fp = sum(ds[j]["fp"] for j in ix); fn = sum(ds[j]["fn"] for j in ix)
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        return 2 * p * r / (p + r) if (p + r) else 0.0
    k = len(per_doc_a)
    full = list(range(k))
    obs = F(per_doc_a, full) - F(per_doc_b, full)
    rng = np.random.default_rng(seed)
    ds = np.empty(nboot)
    for i in range(nboot):
        ix = rng.integers(0, k, k)
        ds[i] = F(per_doc_a, ix) - F(per_doc_b, ix)
    lo, hi = np.percentile(ds, [2.5, 97.5])
    return [round(obs, 4), round(float(lo), 4), round(float(hi), 4)], bool(lo > 0 or hi < 0)


# ---------------------------------------------------------------------------------------------- the run
def _prepare(docs, scratch, rng):
    """Write the reader-CoNLL (true case) and the case-SCRAMBLED twin for each doc. Returns [(doc, p, p_twin)]."""
    from experiments.exp_crosstype_gum_conll_fullread_v1 import gum_to_conll
    out = []
    for d in docs:
        p = os.path.join(scratch, d.docid + ".conll")
        gum_to_conll(d, p)
        gs = gold_sentences(d)
        spans = [(m.start_g, m.end_g, m.eid) for m in d.mentions]
        pt = os.path.join(scratch, d.docid + ".twin.conll")
        write_conll(d.docid, [scramble_case(forms, rng) for forms, _ in gs], spans, pt)
        out.append((d, p, pt))
    return out


def _read_one(arm, harness, taglog, doc, path, path_twin, gaz):
    import hdlab.situation_reader as HSR
    import hdlab.referent_per_np as RNP
    from hdlab.referent_per_np import referent_per_np_source as _rnp_ship
    p = path_twin if arm == "twin" else path
    harness.install(None if arm == "low" else False)
    restore_repairs = install_repairs() if arm == "cased_repair" else None
    if arm == "cased_span":
        RNP.referent_per_np_source = _rnp_source_cased
    else:
        RNP.referent_per_np_source = _rnp_ship
    taglog.reset()
    reader = HSR.SituationReader(gaz=gaz)
    t0 = time.time()
    sm = reader.read(p)
    dt = time.time() - t0
    cache = dict(reader._read_parse_cache)
    gs = gold_sentences(doc)
    import hdlab.scene_segment as _SS
    file_sents = harness._orig(p, lower=False)          # the RAW file tokens (the coref mention stream)
    arm_sents = harness._orig(p, lower=(arm == "low"))  # EXACTLY the reader's own `sents` in this arm
    _ = _SS
    cons, feed, wiring = score_categories(taglog.calls, gs, cache, arm_sents, file_sents)
    mentions, _ns = RNP.referent_per_np_source(p, HSR._CachedTagShim(reader), name_gender_map=gaz)
    ent = score_entities(sm, mentions)
    cor = score_coref(sm)
    rol = score_roles(sm, gold_roles(doc))
    dims = sm_summary(sm)
    evg = score_events_vs_gold(sm, doc)
    RNP.referent_per_np_source = _rnp_ship
    harness.restore()
    if restore_repairs is not None:
        restore_repairs()
    return {"doc": doc.docid, "secs": round(dt, 1), "cat": cons, "feed": feed, "wiring": wiring,
            "ent": ent, "coref": cor, "roles": rol, "dims": dims, "evg": evg}


def run(n_docs=12, arms=ARMS, verbose=True):
    import experiments.gum_coref as G
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    os.makedirs(OUT_DIR, exist_ok=True)
    scratch = os.path.join(OUT_DIR, "conll")
    os.makedirs(scratch, exist_ok=True)
    rng = random.Random(SEED)
    t0 = time.time()
    alldocs = G.load_docs(gum_only=True, decision_source="gold")   # GOLD columns = the ANSWER KEY only
    test = alldocs[1::2]                       # the board's own split: TEST = odd doc index
    step = max(1, len(test) // max(1, n_docs))
    docs = [test[i] for i in range(0, len(test), step)][:n_docs]   # spread across GUM genres
    if verbose:
        print("GUM: %d docs loaded (%.1fs), TEST=%d, using %d" % (len(alldocs), time.time() - t0, len(test), len(docs)))
    prepared = _prepare(docs, scratch, rng)
    gaz = load_given_gazetteer()
    harness = CaseHarness()
    taglog = TagLog()
    per_arm = {a: [] for a in arms}
    try:
        for a in arms:
            for (d, p, pt) in prepared:
                r = _read_one(a, harness, taglog, d, p, pt, gaz)
                per_arm[a].append(r)
                if verbose:
                    c = r["cat"]
                    print("  %-10s %-32s tags %5d acc %.4f PROPN %s  ents %d/%d named %d  coref %d/%d  %.0fs"
                          % (a, d.docid, c["n"], (c["corr"] / c["n"]) if c["n"] else float("nan"), f1(c),
                             r["ent"]["with_heads"], r["ent"]["entities"], r["ent"]["name_typed"],
                             r["coref"]["corr"], r["coref"]["n"], r["secs"]))
    finally:
        taglog.restore()
        harness.restore()
    res = summarize(per_arm, arms)
    res["n_docs"] = len(docs)
    res["docs"] = [d.docid for d, _p, _t in prepared]
    res["ts_iso"] = datetime.now(timezone.utc).isoformat()
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["per_arm_per_doc"] = per_arm
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    if verbose:
        report(res, arms)
    return res


def _agg(rows, key):
    out = defaultdict(int)
    for r in rows:
        for k, v in r[key].items():
            if isinstance(v, (int, float)):
                out[k] += v
    return dict(out)


def summarize(per_arm, arms):
    out = {"arms": {}, "contrasts": {}}
    for a in arms:
        rows = per_arm[a]
        cat = _agg(rows, "cat"); feed = _agg(rows, "feed"); ent = _agg(rows, "ent")
        cor = _agg(rows, "coref"); rol = _agg(rows, "roles"); wir = _agg(rows, "wiring")
        dims = _agg(rows, "dims"); evg = _agg(rows, "evg")
        out["arms"][a] = {
            "categories": {"n_tokens": cat.get("n", 0), "sents": cat.get("sents", 0),
                           "cased_input_sents": cat.get("cased_in", 0),
                           "all_tag_acc": round(cat.get("corr", 0) / cat["n"], 4) if cat.get("n") else None,
                           "propn_p_r_f1": f1(cat), "propn_tp_fp_fn": [cat.get("tp", 0), cat.get("fp", 0), cat.get("fn", 0)]},
            "coref_stream_tags": {"sents": feed.get("sents", 0), "n_tokens": feed.get("n", 0),
                          "all_tag_acc": round(feed.get("corr", 0) / feed["n"], 4) if feed.get("n") else None,
                          "propn_p_r_f1": f1(feed)},
            "entities": ent, "coref": {**cor, "acc": round(cor.get("corr", 0) / cor["n"], 4) if cor.get("n") else None},
            "roles": {**rol,
                      "agent_acc": round(rol.get("ag", 0) / rol["n"], 4) if rol.get("n") else None,
                      "patient_acc": round(rol.get("pa", 0) / rol["n"], 4) if rol.get("n") else None,
                      "agent_floor": round(rol.get("ag_f", 0) / rol["n"], 4) if rol.get("n") else None,
                      "patient_floor": round(rol.get("pa_f", 0) / rol["n"], 4) if rol.get("n") else None},
            "wiring": wir, "dimensions": dims,
            "event_detection": {**evg, "p_r_f1": f1(evg)},
        }
    pairs = [(a, "low") for a in arms if a != "low"]
    if "twin" in arms:
        pairs += [(a, "twin") for a in arms if a not in ("twin", "low")]
    if True:
        for a, base in pairs:
            A = per_arm[a]; B = per_arm[base]
            c = {}
            c["all_tag_acc"], c["all_tag_sep"] = paired_boot([r["cat"] for r in A], [r["cat"] for r in B], "corr", "n")
            c["propn_f1"], c["propn_f1_sep"] = boot_f1([r["cat"] for r in A], [r["cat"] for r in B])
            c["coref_acc"], c["coref_sep"] = paired_boot([r["coref"] for r in A], [r["coref"] for r in B], "corr", "n")
            c["agent_acc"], c["agent_sep"] = paired_boot([r["roles"] for r in A], [r["roles"] for r in B], "ag", "n")
            c["patient_acc"], c["patient_sep"] = paired_boot([r["roles"] for r in A], [r["roles"] for r in B], "pa", "n")
            c["event_f1"], c["event_f1_sep"] = boot_f1([r["evg"] for r in A], [r["evg"] for r in B])
            c["event_recall"], c["event_recall_sep"] = paired_boot([r["evg"] for r in A], [r["evg"] for r in B], "tp", "n")
            c["name_typed"] = [sum(r["ent"]["name_typed"] for r in A), sum(r["ent"]["name_typed"] for r in B)]
            c["entities"] = [sum(r["ent"]["entities"] for r in A), sum(r["ent"]["entities"] for r in B)]
            out["contrasts"]["%s_minus_%s" % (a, base)] = c
    return out


def report(res, arms):
    print("=" * 110)
    print("CASE THROUGH THE LIVE READER -- %d MODERN GUM test documents (paired bootstrap %d over documents)"
          % (res["n_docs"], NBOOT))
    print("=" * 110)
    hdr = "%-11s %8s %9s %-24s %8s %7s %7s %9s %9s"
    print("THE `sents` STREAM -- the tags every organ below the sentence source reads")
    print(hdr % ("arm", "tokens", "all-tag", "PROPN P/R/F1", "ents", "named", "coref", "agent", "patient"))
    for a in arms:
        A = res["arms"][a]
        print(hdr % (a, A["categories"]["n_tokens"], A["categories"]["all_tag_acc"],
                     str(A["categories"]["propn_p_r_f1"]), A["entities"]["entities"],
                     A["entities"]["name_typed"], A["coref"]["acc"],
                     A["roles"]["agent_acc"], A["roles"]["patient_acc"]))
    print("CONTROL -- the COREF mention stream's tags (raw-cased CoNLL tokens in BOTH arms)")
    for a in arms:
        A = res["arms"][a]["coref_stream_tags"]
        print(hdr % (a, A["n_tokens"], A["all_tag_acc"], str(A["propn_p_r_f1"]), "", "", "", "", ""))
    print("-" * 110)
    print("FLOOR (who-did-what, positional): agent %s patient %s"
          % (res["arms"][arms[0]]["roles"]["agent_floor"], res["arms"][arms[0]]["roles"]["patient_floor"]))
    print("-" * 110)
    for a in arms:
        w = res["arms"][a]["wiring"]
        print("  wiring %-11s tag_calls %4d hits %4d misses %4d | cache tag entries %4d (cased %4d / lower %4d) "
              "| sentences tagged under BOTH casings %4d"
              % (a, w.get("tag_calls", 0), w.get("cache_hits", 0), w.get("cache_misses", 0),
                 w.get("cache_tag_entries", 0), w.get("cased_entries", 0), w.get("lower_entries", 0),
                 w.get("sentences_tagged_under_both_casings", 0)))
    print("-" * 110)
    print("EVENT DETECTION vs GUM gold VERB tokens")
    for a in arms:
        E = res["arms"][a]["event_detection"]
        print("  %-11s tp %5d fp %5d fn %5d  P/R/F1 %s  (fp by gold upos: %s)"
              % (a, E["tp"], E["fp"], E["fn"], E["p_r_f1"],
                 ", ".join("%s %d" % (k[8:], v) for k, v in sorted(E.items()) if k.startswith("fp_gold_"))))
    print("-" * 110)
    print("NO-REGRESS: every situation-model dimension the reader built (sum over documents)")
    keys = sorted(set().union(*[set(res["arms"][a]["dimensions"]) for a in arms]))
    print("  %-28s %s" % ("dimension", " ".join("%12s" % a for a in arms)))
    for k in keys:
        print("  %-28s %s" % (k, " ".join("%12s" % res["arms"][a]["dimensions"].get(k, "-") for a in arms)))
    print("-" * 110)
    for k, c in res["contrasts"].items():
        print("  %-22s all-tag %s sep=%s | PROPN F1 %s sep=%s | coref %s sep=%s | agent %s sep=%s | patient %s sep=%s"
              % (k, c["all_tag_acc"], c["all_tag_sep"], c["propn_f1"], c["propn_f1_sep"],
                 c["coref_acc"], c["coref_sep"], c["agent_acc"], c["agent_sep"],
                 c["patient_acc"], c["patient_sep"]))
        print("  %-22s event-detect F1 %s sep=%s | event recall %s sep=%s | named %s | entities %s"
              % ("", c["event_f1"], c["event_f1_sep"], c["event_recall"], c["event_recall_sep"],
                 c["name_typed"], c["entities"]))
    print("=" * 110)


# ---------------------------------------------------------------------------------------------- the organ path
def organ_path(n_docs=0, thetas=(None,), boot=NBOOT, verbose=True):
    """THE READER'S CATEGORY PATH, REPLICATED EXACTLY AND CHEAPLY, so it can be measured on the WHOLE GUM test
    split instead of the 16 documents a full read affords.

    What the reader does per passage (situation_reader.read): `new_document()` -> `feed_passage(CASED sentences)`
    (the ONE in-order feed, pri 112, which also builds the passage SHAPE register) -> every consumer then calls
    `posterior(sents[i])` as a READ, with `sents` LOWERCASED under the shipped default and CASED under the flip.
    This function makes exactly those calls and scores the READ's tags against GUM gold UPOS.

    It also counts the two things the lowercasing destroys INSIDE the organ:
      shape alphabet  -- how many of the organ's 19 orthographic-shape symbols the input can even realize
                         (`word_shape_rich`); the six case symbols are UNREACHABLE on lowercased text.
      register hits   -- how often the passage SHAPE register (ENT_THETA_DOC, pri 104's convention arm, built by
                         the feed from CASED text) answers the READ with evidence: a read that asks with the wrong
                         symbol gets the passage's `lower@m` statistics instead of its capitalisation convention.
    """
    import experiments.gum_coref as G
    from hdlab import lexical_categories as LC
    os.makedirs(OUT_DIR, exist_ok=True)
    docs = G.load_docs(gum_only=True, decision_source="gold")[1::2]
    if n_docs:
        docs = docs[:n_docs]
    rng = random.Random(SEED)
    gs_by = [(d.docid, gold_sentences(d)) for d in docs]
    # count the shape alphabet the input can realize (pure function of the text, no organ call)
    alpha = {}
    for name, kind in (("cased", "cased"), ("low", "low"), ("twin", "twin")):
        syms = defaultdict(int)
        for _id, gs in gs_by:
            for forms, _up in gs:
                ws = (forms if kind == "cased" else
                      [w.lower() for w in forms] if kind == "low" else scramble_case(forms, rng))
                for i, w in enumerate(ws):
                    syms[LC.word_shape_rich(w) + LC.position_class(ws, i)] += 1
        alpha[name] = {"n_symbols": len(syms), "case_symbols": sorted(
            k for k in syms if k[:-2] in ("Cap", "CamelCap", "ALLCAP", "ACRO", "UP1", "mixed", "hyphenCap")),
            "tokens": sum(syms.values())}
    out = {"n_docs": len(docs), "shape_alphabet": alpha, "arms": {}, "contrasts": {}}
    lc = LC.get()
    theta0 = LC.ENT_THETA_DOC
    for theta in thetas:
        LC.ENT_THETA_DOC = theta
        for arm in ("low", "cased", "twin"):
            rng2 = random.Random(SEED)
            per_doc = []
            hits = {"calls": 0, "unknown": 0, "reg_hit": 0}
            anat = {}; conf = {}
            _orig_lsf = LC.LexicalCategories._log_shape_factor

            def _lsf(slf, w_raw, pos, known, _o=_orig_lsf, _h=hits):
                _h["calls"] += 1
                if not known:
                    _h["unknown"] += 1
                    if LC.ENT_THETA_DOC is not None:
                        r = slf._doc_shape_asof(slf._unk_sym(w_raw, pos))
                        if r is not None and float(r.sum()) > 0:
                            _h["reg_hit"] += 1
                return _o(slf, w_raw, pos, known)
            LC.LexicalCategories._log_shape_factor = _lsf
            try:
                for _id, gs in gs_by:
                    cased = [list(f) for f, _u in gs]
                    if arm == "twin":
                        cased = [scramble_case(f, rng2) for f, _u in gs]
                    read_in = ([[w.lower() for w in s] for s in cased] if arm == "low" else cased)
                    lc.new_document()
                    lc.feed_passage(cased)                      # the ONE in-order feed: always the file's own case
                    tags, gold = [], []
                    for si, (_f, up) in enumerate(gs):
                        post = lc.posterior(list(read_in[si]))   # a consumer READ, exactly as _cached_tag makes it
                        tg = [lc.tags[int(np.argmax(post[i]))] for i in range(len(read_in[si]))]
                        tags.append(tg); gold.append(up)
                        # ERROR ANATOMY: where do the surviving PROPN misses sit?
                        ws = read_in[si]
                        for i, (g, pr) in enumerate(zip(up, tg)):
                            if g != "PROPN" and pr != "PROPN":
                                continue
                            pc = LC.position_class(ws, i)
                            kn = "known" if ws[i].lower() in lc.vocab else "novel"
                            k = ("TP" if (g == "PROPN" and pr == "PROPN") else
                                 "FN" if g == "PROPN" else "FP") + "|" + pc + "|" + kn
                            anat[k] = anat.get(k, 0) + 1
                            if g == "PROPN" and pr != "PROPN":
                                conf["FN->" + pr] = conf.get("FN->" + pr, 0) + 1
                            elif pr == "PROPN" and g != "PROPN":
                                conf["FP<-" + g] = conf.get("FP<-" + g, 0) + 1
                    per_doc.append(_tally(tags, gold))
            finally:
                LC.LexicalCategories._log_shape_factor = _orig_lsf
            key = arm if theta is None else "%s_theta%g" % (arm, theta)
            a = _agg([{"c": c} for c in per_doc], "c")
            out["arms"][key] = {"n_tokens": a["n"], "all_tag_acc": round(a["corr"] / a["n"], 4),
                               "propn_p_r_f1": f1(a), "propn_tp_fp_fn": [a["tp"], a["fp"], a["fn"]],
                               "shape_register": dict(hits), "per_doc": per_doc,
                               "error_anatomy": dict(sorted(anat.items())),
                               "propn_confusions": dict(sorted(conf.items(), key=lambda kv: -kv[1]))}
            if verbose:
                print("  theta=%-5s %-6s n=%d all-tag %.4f PROPN %s | shape-register hits %d/%d unknown calls"
                      % (theta, arm, a["n"], a["corr"] / a["n"], f1(a), hits["reg_hit"], hits["unknown"]))
    LC.ENT_THETA_DOC = theta0
    keys = list(out["arms"])
    for a in keys:
        for b in keys:
            if a == b or a.split("_")[0] == b.split("_")[0] and a != b:
                pass
        if a.startswith("cased"):
            suf = a[len("cased"):]
            for base in ("low" + suf, "twin" + suf):
                if base in out["arms"]:
                    A = [{"c": c} for c in out["arms"][a]["per_doc"]]
                    B = [{"c": c} for c in out["arms"][base]["per_doc"]]
                    d1, s1 = paired_boot([x["c"] for x in A], [x["c"] for x in B], "corr", "n", nboot=boot)
                    d2, s2 = boot_f1([x["c"] for x in A], [x["c"] for x in B], nboot=boot)
                    out["contrasts"]["%s_minus_%s" % (a, base)] = {
                        "all_tag_acc": d1, "all_tag_sep": s1, "propn_f1": d2, "propn_f1_sep": s2}
    if verbose:
        print("  shape alphabet realizable by the input: " + ", ".join(
            "%s %d symbols (%d case symbols)" % (k, v["n_symbols"], len(v["case_symbols"])) for k, v in alpha.items()))
        for k, c in out["contrasts"].items():
            print("  %-30s all-tag %s sep=%s | PROPN F1 %s sep=%s"
                  % (k, c["all_tag_acc"], c["all_tag_sep"], c["propn_f1"], c["propn_f1_sep"]))
    # WITHIN-ARM: what the passage SHAPE register (pri 104's convention arm, ENT_THETA_DOC) is worth on each input
    for arm in ("low", "cased", "twin"):
        a, b = "%s_theta100" % arm, arm
        if a in out["arms"] and b in out["arms"]:
            A = out["arms"][a]["per_doc"]; B = out["arms"][b]["per_doc"]
            d1, s1 = paired_boot(A, B, "corr", "n", nboot=boot)
            d2, s2 = boot_f1(A, B, nboot=boot)
            out["contrasts"]["register_on_%s" % arm] = {"all_tag_acc": d1, "all_tag_sep": s1,
                                                        "propn_f1": d2, "propn_f1_sep": s2}
            if verbose:
                print("  register(theta100) on %-6s all-tag %s sep=%s | PROPN F1 %s sep=%s"
                      % (arm, d1, s1, d2, s2))
    with open(os.path.join(OUT_DIR, "organ_path.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    return out


# ---------------------------------------------------------------------------------------------- board probe
def board_probe():
    """Can the MODERN BOARD see the flip at all? Count the sentence-source calls the board makes. The flip
    changes ONLY what `parse_conll_sentences` returns, so a board that never calls it is flat BY ARITHMETIC.
    """
    # NEVER overwrite the board's LANDED record (notes/problems/README.md's reverify hazard): the board's
    # own get_output_dir(ANCHOR) reads HDLAB_EXP_NAME, so this run must be routed to its OWN directory.
    en = os.environ.get("HDLAB_EXP_NAME", "")
    if not en or "situation_model_qa" in en:
        raise SystemExit("REFUSING: set HDLAB_EXP_NAME to an OWN directory (e.g. case_board_probe_v1) so the "
                         "board's landed data/exp_situation_model_qa_modern_v1/metrics.json is not rewritten.")
    import hdlab.scene_segment as SS
    calls = []
    orig = SS.parse_conll_sentences

    def f(path, lower=True):
        calls.append((path, lower))
        return orig(path, lower=lower)
    mods = []
    for name in ("hdlab.scene_segment", "hdlab.situation_reader", "hdlab.referent_per_np", "hdlab.space_reader"):
        __import__(name)
        m = sys.modules[name]
        if getattr(m, "parse_conll_sentences", None) is not None:
            m.parse_conll_sentences = f
            mods.append(m)
    try:
        import experiments.exp_situation_model_qa_modern_v1 as B
        t0 = time.time()
        res = B.run()
        dt = time.time() - t0
    finally:
        for m in mods:
            m.parse_conll_sentences = orig
    out = {"sentence_source_calls": len(calls),
           "distinct_paths": sorted({os.path.basename(p) for p, _l in calls})[:20],
           "lower_true_calls": sum(1 for _p, l in calls if l),
           "lower_false_calls": sum(1 for _p, l in calls if not l),
           "board_elapsed_s": round(dt, 1),
           "aggregate": (res or {}).get("aggregate") if isinstance(res, dict) else None}
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "board_probe.json"), "w", encoding="utf-8") as fh:
        json.dump({"probe": out, "board": res if isinstance(res, dict) else None}, fh, indent=2, default=str)
    print(json.dumps(out, indent=2)[:4000])
    return out


# ---------------------------------------------------------------------------------------------- self-test
def _self_test():
    ok = True
    # (1) the harness forces the case and restores the shipped default byte-for-byte
    import hdlab.scene_segment as SS
    import experiments.gum_coref as G
    from experiments.exp_crosstype_gum_conll_fullread_v1 import gum_to_conll
    scratch = os.path.join(OUT_DIR, "selftest")
    os.makedirs(scratch, exist_ok=True)
    d = G.load_docs(gum_only=True, limit=1, decision_source="gold")[0]
    p = gum_to_conll(d, os.path.join(scratch, "st.conll")) and os.path.join(scratch, "st.conll")
    ship = SS.parse_conll_sentences(p, lower=True)
    cased = SS.parse_conll_sentences(p, lower=False)
    h = CaseHarness()
    h.install(None)
    import hdlab.referent_per_np as RNP
    a = RNP.parse_conll_sentences(p, lower=True)
    h.install(False)
    b = RNP.parse_conll_sentences(p, lower=True)
    h.restore()
    c = RNP.parse_conll_sentences(p, lower=True)
    print("  harness shipped==ship: %s | forced==cased: %s | restored==ship: %s"
          % (a == ship, b == cased, c == ship))
    ok &= (a == ship) and (b == cased) and (c == ship)
    # (2) the case really is the only difference
    same = all(len(x) == len(y) and all(u.lower() == v.lower() for u, v in zip(x, y))
               for x, y in zip(ship, cased))
    n_cap = sum(1 for s in cased for w in s if w[:1].isupper())
    print("  token identity invariant under case: %s | capital-initial tokens in the cased text: %d" % (same, n_cap))
    ok &= same and n_cap > 0
    # (3) the TWIN preserves the capital COUNT per sentence and moves the positions
    rng = random.Random(0)
    gs = gold_sentences(d)
    moved = kept = 0
    for forms, _u in gs:
        sc = scramble_case(forms, rng)
        kept += int(sum(1 for w in forms if w[:1].isupper()) == sum(1 for w in sc if w[:1].isupper()))
        moved += int(any((a_[:1].isupper()) != (b_[:1].isupper()) for a_, b_ in zip(forms, sc)))
    print("  twin: capital count preserved on %d/%d sentences; positions moved on %d" % (kept, len(gs), moved))
    ok &= (kept == len(gs)) and moved > 0
    # (4) the proposed _mk_referent is byte-identical on an already-lowercased token and cased otherwise
    import hdlab.referent_per_np as R2
    shipd = R2._mk_referent("dog", 0, 3, 7, -1, upos="NOUN")
    newd = _mk_referent_cased("dog", 0, 3, 7, -1, upos="NOUN")
    capd = _mk_referent_cased("Dog", 0, 3, 7, -1, upos="PROPN")
    print("  _mk_referent byte-identical on lowercase input: %s | cased span_toks: %s | head still lower: %s"
          % (shipd == newd, capd["span_toks"], capd["head"]))
    ok &= (shipd == newd) and capd["span_toks"] == ["Dog"] and capd["head"] == "dog"
    # (5) name_content_tokens -- the consumer the repair unblocks
    from hdlab.coref import name_content_tokens
    print("  name_content_tokens(['dog'])=%s  (['Dog'])=%s"
          % (name_content_tokens(["dog"]), name_content_tokens(["Dog"])))
    ok &= (not name_content_tokens(["dog"])) and bool(name_content_tokens(["Dog"]))
    # (6) THE CONSUMER REPAIRS install from their own source and restore exactly
    import hdlab.situation_reader as _H
    _before = _H.SituationReader._read_causation
    _r = install_repairs()
    _ok6 = (_H.SituationReader._read_causation.__code__.co_filename.startswith("<case_repair")
            and _H.SituationReader._read_timeline.__code__.co_filename.startswith("<case_repair")
            and isinstance(_H.SituationReader.__dict__["_read_timeline"], staticmethod))
    _r()
    _ok6 = _ok6 and (_H.SituationReader._read_causation is _before)
    print("  consumer repairs install from their own source and restore: %s" % _ok6)
    ok &= _ok6
    # (6b) the gold role builder finds clauses and the positional floor is not the gold
    recs = gold_roles(d)
    agree = sum(1 for r in recs if positional_floor(r) == (r["agent"], r["patient"]))
    print("  gold who-did-what clauses: %d ; positional floor agrees on %d" % (len(recs), agree))
    ok &= len(recs) > 0
    print("SELF-TEST: %s" % ("PASS" if ok else "FAIL"))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--board-probe", action="store_true")
    ap.add_argument("--organ", action="store_true")
    ap.add_argument("--capcard", action="store_true")
    ap.add_argument("--thetas", default="")
    ap.add_argument("--docs", type=int, default=12)
    ap.add_argument("--arms", default=",".join(ARMS))
    a = ap.parse_args()
    if a.self_test:
        sys.exit(0 if _self_test() else 1)
    if a.board_probe:
        board_probe(); return
    if a.capcard:
        capcard_probe(n_docs=(0 if a.docs <= 0 else a.docs)); return
    if a.organ:
        th = tuple(None if x in ("none", "None") else float(x) for x in a.thetas.split(",")) if a.thetas else (None,)
        organ_path(n_docs=(0 if a.docs <= 0 else a.docs), thetas=th); return
    run(n_docs=a.docs, arms=tuple(x for x in a.arms.split(",") if x))




# ------------------------------------------------------------------- PHASE 4: the passage's per-STRING CASE card
def capcard_probe(n_docs=0, boot=NBOOT, verbose=True):
    """THE QUALITY PUSH, and it only becomes possible once the case reaches the organ.

    THE BRAIN. Heim (1982) file-change semantics: the comprehender opens a FILE CARD per string/referent and
    writes what the passage has established about it; the organ already HAS those cards
    (`lexical_categories.DiscourseRegister.h`, keyed on the lowercased string, written by the ONE in-order feed
    and read AS OF the sentence -- pri 112). What the cards do NOT yet record is the ORTHOGRAPHIC fact.
    The Competition Model's cue-validity argument (MacWhinney & Bates 1989) says why that matters: a capital is
    a cue with two very different validities depending on position -- at a sentence's first word capitalisation
    is FORCED, so its RELIABILITY is ~0 (the organ already knows this: `position_class` makes Cap@i a different
    symbol from Cap@m); mid-sentence it is highly reliable. A reader who has met `Marcie` capitalised MID
    sentence has ESTABLISHED that this string names an individual, and at the start of the next sentence -- where
    the capital tells them nothing -- that established fact is the cue they use instead.

    THE PROTOTYPE (a LOCATOR, not the landed form): when a token at a FORCED position is capital-initial and the
    passage's own record, AS OF sentences strictly before this one, has met that exact string capitalised at a
    NON-forced position, read its orthographic-shape emission against the Cap@m statistics it established rather
    than the uninformative Cap@i ones. No new parameter, no new table -- it re-reads an existing learned count
    row through the passage's own evidence. The LANDED form must be a graded card (the count of forced/non-forced
    observations, shrunk the way the organ's other reliability terms are: a = n/(n+theta)), written by the feed
    and read as-of; this prototype uses the hard bit to locate the signal.

    ARMS: cased (the flip alone) | capcard (the prototype) | capcard_twin (an INFO-FREE twin: the same NUMBER of
    established strings per passage, drawn at random from the passage's own vocabulary) | oracle_mid (the upper
    bound: read EVERY capital-initial forced-position token as Cap@m -- what the cue could be worth at most).
    """
    import experiments.gum_coref as G
    from hdlab import lexical_categories as LC
    os.makedirs(OUT_DIR, exist_ok=True)
    docs = G.load_docs(gum_only=True, decision_source="gold")[1::2]
    if n_docs:
        docs = docs[:n_docs]
    gs_by = [(d.docid, gold_sentences(d)) for d in docs]
    lc = LC.get()
    out = {"n_docs": len(docs), "arms": {}, "contrasts": {}}
    state = {"sub": set(), "on": False, "n_sub": 0, "n_init_cap": 0, "mode": "capcard", "perm": None}
    _orig = LC.LexicalCategories._log_shape_factor

    def _blend(slf, sp, base, r):
        """The organ's OWN reliability shrinkage, verbatim from `_log_shape_factor`'s unknown branch:
        a = n/(n+theta) toward the passage's local distribution for this shape symbol, with the offline
        known/unknown bias correction (ENT_REG_OFFSET) applied to the local part."""
        nd = float(r.sum()) if r is not None else 0.0
        if nd <= 0:
            return base
        a = nd / (nd + LC.ENT_THETA_DOC)
        mx = float(base.max())
        loc = r / nd
        off = slf._sp_offset.get(sp) if LC.ENT_REG_OFFSET else None
        if off is not None:
            loc = loc * np.exp(off)
            loc = loc / loc.sum()
        pr = a * loc + (1.0 - a) * np.exp(base - mx)
        return np.log(pr / pr.sum() + 1e-12) + mx

    def _lsf(slf, w_raw, pos, known, _o=_orig, _s=state):
        if _s["on"] and _s["mode"] == "capcard":
            if pos == LC.INIT and w_raw[:1].isupper():
                _s["n_init_cap"] += 1
                if _s["sub"] is True or w_raw.lower() in _s["sub"]:
                    _s["n_sub"] += 1
                    pos = LC.MID
        elif _s["on"] and _s["mode"] == "regknown" and known and LC.ENT_THETA_DOC is not None:
            # THE PASSAGE'S CONVENTION, READ FOR A WORD THE LEXICON ALREADY KNOWS. The organ writes the
            # register from known tokens (ENT_REG_KNOWN) but READS it only for novel forms; a competent
            # reader applies the passage's convention to every word, and most of the residual PROPN errors
            # are on KNOWN forms (Bill / May / Mark / Chemistry in a title).
            sp = slf._unk_sym(w_raw, pos)
            base = np.array([slf.log_shape_pos[t].get(sp, slf._shape_pos_back[t]) for t in slf.tags])
            r = slf._doc_shape_asof(sp)
            if _s["perm"] is not None and r is not None:
                r = slf._doc_shape_asof(_s["perm"].get(sp, sp))    # the info-free twin: the WRONG symbol's record
            if r is not None:
                _s["n_sub"] += 1
            return _blend(slf, sp, base, r)
        return _o(slf, w_raw, pos, known)
    LC.LexicalCategories._log_shape_factor = _lsf
    try:
        for arm in ("cased", "capcard", "capcard_twin", "oracle_mid", "regknown", "regknown_twin"):
            rng = random.Random(SEED)
            per_doc = []
            state["n_sub"] = state["n_init_cap"] = 0
            for _id, gs in gs_by:
                cased = [list(f) for f, _u in gs]
                # the passage's own record, AS OF each sentence: strings met capitalised at a NON-forced position
                asof, seen = [], set()
                vocab = sorted({w.lower() for s in cased for w in s if w[:1].isalpha()})
                for s in cased:
                    asof.append(set(seen))
                    for i, w in enumerate(s):
                        if w[:1].isupper() and LC.position_class(s, i) == LC.MID:
                            seen.add(w.lower())
                lc.new_document()
                state["on"] = False
                lc.feed_passage(cased)          # the feed is unchanged in every arm
                # the info-free twin for the register arm: the SAME local records attached to the WRONG shape
                # symbols (same distributional shape, zero information about which orthography means what)
                _syms = list(lc._doc_shape)
                _sh = list(_syms)
                rng.shuffle(_sh)
                permap = dict(zip(_syms, _sh))
                tags, gold = [], []
                for si, (_f, up) in enumerate(gs):
                    state["mode"] = "regknown" if arm.startswith("regknown") else "capcard"
                    if arm == "cased":
                        state["on"] = False
                    elif arm.startswith("regknown"):
                        state["on"] = True
                        state["perm"] = permap if arm.endswith("_twin") else None
                    else:
                        state["on"] = True
                        if arm == "capcard":
                            state["sub"] = asof[si]
                        elif arm == "oracle_mid":
                            state["sub"] = True
                        else:                    # the info-free twin: as many strings, chosen at random
                            k = len(asof[si])
                            state["sub"] = set(rng.sample(vocab, min(k, len(vocab)))) if vocab else set()
                    post = lc.posterior(list(cased[si]))
                    tags.append([lc.tags[int(np.argmax(post[i]))] for i in range(len(cased[si]))])
                    gold.append(up)
                state["on"] = False
                per_doc.append(_tally(tags, gold))
            a = _agg([{"c": c} for c in per_doc], "c")
            out["arms"][arm] = {"n_tokens": a["n"], "all_tag_acc": round(a["corr"] / a["n"], 4),
                                "propn_p_r_f1": f1(a), "propn_tp_fp_fn": [a["tp"], a["fp"], a["fn"]],
                                "forced_position_capitals": state["n_init_cap"],
                                "substituted": state["n_sub"], "per_doc": per_doc}
            if verbose:
                print("  %-13s n=%d all-tag %.4f PROPN %s | forced-position capitals %d, read as established %d"
                      % (arm, a["n"], a["corr"] / a["n"], f1(a), state["n_init_cap"], state["n_sub"]))
    finally:
        LC.LexicalCategories._log_shape_factor = _orig
    for a in ("capcard", "capcard_twin", "oracle_mid", "regknown", "regknown_twin"):
        for b in ("cased", "capcard_twin", "regknown_twin"):
            if a == b or a not in out["arms"]:
                continue
            A = out["arms"][a]["per_doc"]; B = out["arms"][b]["per_doc"]
            d1, s1 = paired_boot(A, B, "corr", "n", nboot=boot)
            d2, s2 = boot_f1(A, B, nboot=boot)
            out["contrasts"]["%s_minus_%s" % (a, b)] = {"all_tag_acc": d1, "all_tag_sep": s1,
                                                        "propn_f1": d2, "propn_f1_sep": s2}
            if verbose:
                print("  %-26s all-tag %s sep=%s | PROPN F1 %s sep=%s" % (a + " - " + b, d1, s1, d2, s2))
    for v in out["arms"].values():
        v.pop("per_doc", None)
    with open(os.path.join(OUT_DIR, "capcard.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    return out


if __name__ == "__main__":
    main()
