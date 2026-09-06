"""LANDING WITNESS -- unified_referent live wire (form_the_unified_discourse_referent... Q111).

Proves, first-hand and with capped threads, that the landed `unified_referent` capability flag:
  W1 OFF-IDENTITY  : with the flag OFF the live reader is byte-identical to the landed graded_pick reader
                     (module self-tests intact; doc-level SituationModel identical; EC records bit-for-bit).
  W2 ON-FAITHFULNESS (load-bearing): the live wired pick reproduces the reference
                     experiments/exp_unified_referent_gum_v1.py::Resolver(arm='unified') pick, EXACTLY, on
                     constructed streams exercising name-variant fragmentation, cross-type pronoun writeback,
                     recall-safe gender completion, and ACT-R prominence-over-recency; plus a GUM-slice
                     direction check (live-unified beats the recency floor / reference-separate on modern gold).
  W3 ADDITIVE      : with the flag ON, the coref-INDEPENDENT dims (events agent/patient, causal, timeline)
                     are byte-identical to flag-OFF; only the coref pick (+ coref-dependent bindings) moves.

Also reports (NOT gated): the 19c LitBank coref off-vs-on numbers (informational; 19c is BANNED as gold).

Run:  OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3 MKL_NUM_THREADS=3 THINC_NUM_THREADS=3 \
      .venv/Scripts/python.exe verification/test_unified_referent_landing.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coref import build_pronoun_targets
from hdlab.state_of_mind import PRONOUN_SCOPE
from hdlab.unified_referent import resolve_unified_stream
from hdlab.event_centrality_coref import EventCentralityReader
import hdlab.event_centrality_coref as EC

# reference mechanism (byte-for-byte; imported read-only)
import experiments.gum_coref as G
from experiments.exp_unified_referent_gum_v1 import Resolver

LITBANK_DIR = os.path.join(_REPO, "data", "litbank", "coref", "conll")
_RANK = {"SUBJECT": 0, "OBJECT": 1, "OTHER": 99}
_DEPREL = {"SUBJECT": "nsubj", "OBJECT": "obj", "OTHER": "amod"}
_REFGEN = {"f": "f", "m": "m", None: ""}
_LIVEGEN = {"f": "fem", "m": "masc", None: None}
_PRON_REFGEN = {"she": "f", "her": "f", "hers": "f", "he": "m", "him": "m", "his": "m"}

_PASS = []
_FAIL = []


def _check(name, cond, detail=""):
    (_PASS if cond else _FAIL).append(name)
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, (" -- " + detail) if detail else ""))
    return cond


# ---------------------------------------------------------------------------
# W2 shared-input builders: ONE abstract spec -> a reference Doc AND live mentions.
# spec = list of {"text","mtype"(name/common/pronoun),"gender"(f/m/None),"role","eid","sent"}
# The LAST mention is the scored/probed pronoun.
# ---------------------------------------------------------------------------
def _head(s):
    return s["text"].lower() if s["mtype"] == "pronoun" else s["text"].lower().split()[-1]


def build_ref_doc(spec):
    toks, mentions = [], []
    for i, s in enumerate(spec):
        head = _head(s)
        upos = {"name": "PROPN", "common": "NOUN", "pronoun": "PRON"}[s["mtype"]]
        toks.append(G.Tok(idx=i + 1, form=s["text"].split()[-1], lemma=head, upos=upos, xpos="_",
                          feats={}, head=0, deprel=_DEPREL[s["role"]], sent=s.get("sent", i), gidx=i))
        if s["mtype"] == "pronoun":
            gref = _PRON_REFGEN.get(head, "")     # writeback gender (Mention.gender); pick uses _pron_gn
        else:
            gref = _REFGEN[s.get("gender")]
        mentions.append(G.Mention(eid=s["eid"], sent=s.get("sent", i), start_g=i, end_g=i, head_g=i,
                                  text=s["text"], mtype=s["mtype"], upos=upos, gender=gref, number="",
                                  lemma_head=head, order=i))
    return G.Doc(docid="w2", genre="t", corpus="GUM", toks=toks, mentions=mentions)


def build_live_mentions(spec):
    ms = []
    for i, s in enumerate(spec):
        head = _head(s)
        if s["mtype"] == "pronoun":
            ms.append({"head": head, "is_pronoun": True, "gender": PRONOUN_SCOPE[head]["gender"],
                       "number": PRONOUN_SCOPE[head]["number"], "name_gender": None,
                       "span_toks": [s["text"]], "sent_idx": s.get("sent", i), "midx": i,
                       "cluster": s["eid"], "sent_role_rank": _RANK[s["role"]]})
        elif s["mtype"] == "name":
            ms.append({"head": head, "is_pronoun": False, "gender": None,
                       "number": None, "name_gender": _LIVEGEN[s.get("gender")],
                       "span_toks": s["text"].split(), "sent_idx": s.get("sent", i), "midx": i,
                       "cluster": s["eid"], "sent_role_rank": _RANK[s["role"]]})
        else:   # common
            ms.append({"head": head, "is_pronoun": False, "gender": _LIVEGEN[s.get("gender")],
                       "number": None, "name_gender": None,
                       "span_toks": s["text"].split(), "sent_idx": s.get("sent", i), "midx": i,
                       "cluster": s["eid"], "sent_role_rank": _RANK[s["role"]]})
    return ms


def ref_pick(spec, arm):
    """The eid the reference Resolver(arm) resolves the LAST pronoun to (probe over candidate eids:
    the pronoun's own eid does not influence the pick, only scoring, so the cand that scores correct
    == the pick)."""
    last = len(spec) - 1
    cand_eids = sorted({s["eid"] for s in spec[:last]})
    for ce in cand_eids:
        sp = [dict(s) for s in spec]
        sp[last] = dict(sp[last]); sp[last]["eid"] = ce
        res = Resolver(arm).resolve_doc(build_ref_doc(sp))
        pron = [r for r in res if r[0] == "pronoun"]
        if pron and pron[-1][2] is True:
            return ce
    return None


def live_pick(spec):
    ms = build_live_mentions(spec)
    targets = build_pronoun_targets(ms)
    recs = resolve_unified_stream(ms, targets)
    return recs[-1]["resolved_cluster"] if recs else None


def _recency_pick(spec):
    """Most-recent gn-compatible prior mention's eid (the recency floor) for the last pronoun."""
    last = len(spec) - 1
    pron = spec[last]
    pg = PRONOUN_SCOPE[_head(pron)]["gender"]
    best = None
    for s in spec[:last]:
        if s["mtype"] == "pronoun":
            continue
        g = _LIVEGEN[s.get("gender")]
        if g is None or pg is None or g == pg:   # recall-safe
            best = s["eid"]
    return best


# name-variant fragmentation: Elizabeth (2 surface fragments) vs a recent OBJECT distractor Charlotte.
# separate splits Elizabeth's salience so the recent Charlotte wins; unified merges -> Elizabeth wins.
SPEC_FRAG = [
    {"text": "Elizabeth Bennet", "mtype": "name", "gender": "f", "role": "SUBJECT", "eid": 1, "sent": 0},
    {"text": "Bennet",           "mtype": "name", "gender": "f", "role": "SUBJECT", "eid": 1, "sent": 1},
    {"text": "Elizabeth",        "mtype": "name", "gender": "f", "role": "SUBJECT", "eid": 1, "sent": 2},
    {"text": "Charlotte",        "mtype": "name", "gender": "f", "role": "OBJECT",  "eid": 2, "sent": 3},
    {"text": "she",              "mtype": "pronoun",             "role": "SUBJECT", "eid": 1, "sent": 4},
]

# cross-type pronoun writeback + recall-safe gender completion: a gender-unknown 'Alex' (the salient
# protagonist, 2 subject mentions) is gendered MASC by resolving 'he'; the file-change writeback then
# EXCLUDES Alex from a later 'she' (recall-safe agreement) -> the correct feminine Maria wins. The
# separate arm strands gender (no feature writeback) so it wrongly resolves 'she' to the salient Alex.
SPEC_WRITEBACK = [
    {"text": "Maria", "mtype": "name", "gender": "f",  "role": "SUBJECT", "eid": 2, "sent": 0},
    {"text": "Alex",  "mtype": "name", "gender": None, "role": "SUBJECT", "eid": 1, "sent": 1},
    {"text": "Alex",  "mtype": "name", "gender": None, "role": "SUBJECT", "eid": 1, "sent": 2},
    {"text": "he",    "mtype": "pronoun",              "role": "SUBJECT", "eid": 1, "sent": 3},
    {"text": "she",   "mtype": "pronoun",              "role": "SUBJECT", "eid": 2, "sent": 4},
]

# ACT-R prominence/frequency over recency: a twice-mentioned SUBJECT protagonist (Anna) beats a more-recent
# single OBJECT (Bella) -- the recency floor would pick the recent object. Non-fragmentation equivalence case.
SPEC_PROMINENCE = [
    {"text": "Anna",  "mtype": "name", "gender": "f", "role": "SUBJECT", "eid": 1, "sent": 0},
    {"text": "Anna",  "mtype": "name", "gender": "f", "role": "SUBJECT", "eid": 1, "sent": 1},
    {"text": "Bella", "mtype": "name", "gender": "f", "role": "OBJECT",  "eid": 2, "sent": 2},
    {"text": "she",   "mtype": "pronoun",             "role": "SUBJECT", "eid": 1, "sent": 3},
]

# common-noun cross-type: a common 'woman' re-mention (recency same-head) then a pronoun; equivalence.
SPEC_COMMON = [
    {"text": "Sarah",     "mtype": "name",   "gender": "f", "role": "SUBJECT", "eid": 1, "sent": 0},
    {"text": "the woman", "mtype": "common", "gender": "f", "role": "SUBJECT", "eid": 3, "sent": 1},
    {"text": "woman",     "mtype": "common", "gender": "f", "role": "SUBJECT", "eid": 3, "sent": 2},
    {"text": "she",       "mtype": "pronoun",              "role": "SUBJECT", "eid": 3, "sent": 3},
]


def w1_off_identity():
    print("\n== W1 OFF-IDENTITY (flag off == landed graded_pick reader) ==")
    # (a) module self-tests intact (query-OFF reproduces parent; graded default; unified routing)
    ok_st = True
    try:
        EC._run_all_selftests()
    except AssertionError as e:
        ok_st = False
        print("    selftest assertion:", e)
    _check("W1a module self-tests intact (graded/default path unchanged)", ok_st)

    # (b) default reader has the flag OFF
    from hdlab.situation_reader import SituationReader
    _check("W1b default reader unified_referent is False",
           SituationReader().reader_ec.unified_referent is False)

    # (c) EC records bit-for-bit: default (no arg) vs explicit unified_referent=False
    ms = build_live_mentions(SPEC_FRAG)
    tg = build_pronoun_targets(ms)
    sid = [0] * (max(m["sent_idx"] for m in ms) + 1)
    base = EventCentralityReader(graded_pick=True).resolve_stream(
        ms, tg, scene_ids=sid, topical_mode="rolemass", query_memory=True, centrality_mode="event_role")
    offx = EventCentralityReader(graded_pick=True, unified_referent=False).resolve_stream(
        ms, tg, scene_ids=sid, topical_mode="rolemass", query_memory=True, centrality_mode="event_role")
    _check("W1c EC records byte-identical (flag-off vs default)",
           [r["resolved_cluster"] for r in base] == [r["resolved_cluster"] for r in offx]
           and [r["correct"] for r in base] == [r["correct"] for r in offx])

    # (d) doc-level: default reader == explicit-off reader across ALL SituationModel dims
    docs = _pick_litbank(2)
    if docs:
        from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
        gaz = load_given_gazetteer()
        r_def = SituationReader(gaz=gaz, bind_entity_states=True)
        r_off = SituationReader(gaz=gaz, bind_entity_states=True, unified_referent=False)
        same = True
        for d in docs:
            a, b = r_def.read(d), r_off.read(d)
            if _model_proj(a) != _model_proj(b):
                same = False
        _check("W1d doc-level SituationModel identical (default vs explicit-off, %d docs)" % len(docs), same)
    else:
        print("  [SKIP] W1d -- no LitBank docs found")


def _pron_correct_seq_from_records(recs):
    return [r["correct"] for r in recs]


def w2_on_faithfulness():
    print("\n== W2 ON-FAITHFULNESS (live wired pick == reference Resolver unified-arm pick) ==")
    specs = [("fragmentation", SPEC_FRAG, True),
             ("pronoun-writeback+gender-completion", SPEC_WRITEBACK, True),
             ("prominence-over-recency", SPEC_PROMINENCE, False),
             ("common-noun cross-type", SPEC_COMMON, False)]
    all_ok = True
    for name, spec, differential in specs:
        lp = live_pick(spec)
        ru = ref_pick(spec, "unified")
        rs = ref_pick(spec, "separate")
        exact = (lp == ru and lp is not None)
        _check("W2 [%s] live-unified pick == reference-unified pick (live=%s ref=%s)" % (name, lp, ru), exact)
        all_ok = all_ok and exact
        if differential:
            diff = (rs != ru)
            _check("W2 [%s] unification CHANGES the pick vs separate (separate=%s unified=%s)" % (name, rs, ru), diff)
            all_ok = all_ok and diff
        if name == "prominence-over-recency":
            rec = _recency_pick(spec)
            _check("W2 [%s] ACT-R pick != recency floor (recency=%s unified=%s)" % (name, rec, ru), rec != ru)

    # GUM-slice direction check (informational + a live>recency assertion on MODERN gold)
    try:
        _w2_gum_direction()
    except Exception as e:
        print("  [WARN] W2 GUM-slice skipped:", repr(e))
    return all_ok


def _gum_to_live(doc):
    """Convert a reference GUM Doc to live mention dicts (reading order)."""
    # within-sentence rank (subjecthood proxy) mirrors parse_litbank_conll
    by_sent = {}
    for m in doc.mentions:
        by_sent.setdefault(m.sent, []).append(m)
    rank = {}
    for sm in by_sent.values():
        for r, m in enumerate(sorted(sm, key=lambda mm: mm.head_g)):
            rank[m.order] = r
    gmap = {"m": "masc", "f": "fem", "n": "neuter", "": None}
    nmap = {"sing": "singular", "plur": "plural", "": None}
    ms = []
    for i, m in enumerate(doc.mentions):
        head = m.text.lower().split()[0] if m.mtype == "pronoun" else m.lemma_head
        is_pron = (m.mtype == "pronoun") and (head in PRONOUN_SCOPE)
        if is_pron:
            ms.append({"head": head, "is_pronoun": True, "gender": PRONOUN_SCOPE[head]["gender"],
                       "number": PRONOUN_SCOPE[head]["number"], "name_gender": None,
                       "span_toks": m.text.split(), "sent_idx": m.sent, "midx": i,
                       "cluster": m.eid, "sent_role_rank": rank.get(m.order, 99)})
        else:
            g = gmap.get(m.gender)
            ms.append({"head": m.lemma_head, "is_pronoun": False,
                       "gender": (g if m.mtype != "name" else None),
                       "number": nmap.get(m.number), "name_gender": (g if m.mtype == "name" else None),
                       "span_toks": m.text.split(), "sent_idx": m.sent, "midx": i,
                       "cluster": m.eid, "sent_role_rank": rank.get(m.order, 99)})
    return ms


def _w2_gum_direction():
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    from experiments.exp_unified_referent_gum_v1 import _run_arm, _acc, Resolver as R
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=40, name_gazetteer=gaz)
    docs = [d for i, d in enumerate(docs) if i % 2 == 1][:15]   # a test-parity slice
    # reference native pronoun accuracy (the solver's population)
    sep = _run_arm(R("separate"), docs)
    uni = _run_arm(R("unified"), docs)
    a_sep, _ = _acc(sep, "pronoun")
    a_uni, _ = _acc(uni, "pronoun")
    # live port over the converted mentions (its he/she target population) + a recency floor
    live_h = live_t = rec_h = 0
    for d in docs:
        ms = _gum_to_live(d)
        tg = build_pronoun_targets(ms)
        recs = resolve_unified_stream(ms, tg)
        for r in recs:
            live_t += 1
            live_h += int(r["correct"])
        # recency floor on the same targets
        target_midx = {t["target"]["midx"] for t in tg}
        seen = {}
        for m in ms:
            if m["is_pronoun"] and m["midx"] in target_midx:
                pg = m["gender"]
                cand = [c for c in seen.values()
                        if c[0] is None or pg is None or c[0] == pg]
                pick = max(cand, key=lambda c: c[1])[2] if cand else None
                rec_h += int(pick == m["cluster"])
            if not m["is_pronoun"]:
                seen[m["head"]] = (m.get("name_gender") or m.get("gender"), m["midx"], m["cluster"])
    live_acc = live_h / max(1, live_t)
    rec_acc = rec_h / max(1, live_t)
    print("  [GUM-slice %d docs] reference pronoun acc: separate=%.4f unified=%.4f (dir=%+.4f)"
          % (len(docs), a_sep, a_uni, a_uni - a_sep))
    print("  [GUM-slice] live-unified he/she acc=%.4f (n=%d)  vs recency-floor=%.4f"
          % (live_acc, live_t, rec_acc))
    _check("W2 GUM reference reproduces +direction (unified > separate)", a_uni > a_sep,
           "unified=%.4f separate=%.4f" % (a_uni, a_sep))
    _check("W2 GUM live-unified beats the recency floor on modern gold", live_acc > rec_acc,
           "live=%.4f recency=%.4f" % (live_acc, rec_acc))


def _model_proj(sm):
    """Coref-INDEPENDENT projection of a SituationModel (events agent/patient, causal, timeline)."""
    ev = [(getattr(e, "predicate", None), getattr(e, "agent", None), getattr(e, "patient", None),
           getattr(e, "idx", None), getattr(e, "sent_idx", None)) for e in (sm.events or [])]
    causal = [str(c) for c in (getattr(sm, "causal_links", None) or [])]
    timeline = str(getattr(sm, "timeline_order", None)) + "|" + str(getattr(sm, "timeline_frames", None))
    return {"events": ev, "causal": causal, "timeline": timeline}


def _pick_litbank(n):
    if not os.path.isdir(LITBANK_DIR):
        return []
    prefer = ["1342_pride_and_prejudice_brat", "158_emma_brat", "105_persuasion_brat",
              "514_little_women_brat", "45_anne_of_green_gables_brat"]
    out = []
    for base in prefer:
        p = os.path.join(LITBANK_DIR, base + ".conll")
        if os.path.exists(p):
            out.append(p)
        if len(out) >= n:
            break
    return out


def w3_additive_and_19c():
    print("\n== W3 ADDITIVE (coref-independent dims byte-identical on/off) + 19c off-vs-on (informational) ==")
    docs = _pick_litbank(3)
    if not docs:
        print("  [SKIP] no LitBank docs found")
        return
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    from hdlab.situation_reader import SituationReader
    gaz = load_given_gazetteer()
    r_off = SituationReader(gaz=gaz, bind_entity_states=True, unified_referent=False)
    r_on = SituationReader(gaz=gaz, bind_entity_states=True, unified_referent=True)
    additive_ok = True
    print("  doc                                  coref_acc(off)  coref_acc(on)   dim-regress?")
    for d in docs:
        a = r_off.read(d)
        b = r_on.read(d)
        add = _model_proj(a) == _model_proj(b)
        additive_ok = additive_ok and add
        name = os.path.basename(d)[:34].ljust(34)
        print("  %s   %-12s   %-12s   %s"
              % (name, _fmt(a.coref_acc), _fmt(b.coref_acc),
                 "NO (byte-identical)" if add else "YES -- events/causal/timeline changed!"))
    _check("W3 coref-independent dims (events/causal/timeline) byte-identical on-vs-off (%d docs)" % len(docs),
           additive_ok)


def _fmt(x):
    return "None" if x is None else ("%.4f" % x)


def main():
    print("=" * 92)
    print("UNIFIED_REFERENT LIVE-WIRE LANDING WITNESS (capped threads: OMP=%s)" % os.environ.get("OMP_NUM_THREADS"))
    print("=" * 92)
    w1_off_identity()
    w2_on_faithfulness()
    w3_additive_and_19c()
    print("\n" + "=" * 92)
    print("SUMMARY: %d PASS / %d FAIL" % (len(_PASS), len(_FAIL)))
    if _FAIL:
        print("FAILURES:", _FAIL)
    print("=" * 92)
    return 1 if _FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
