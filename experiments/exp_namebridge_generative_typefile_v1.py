"""exp_namebridge_generative_typefile_v1 -- the GENERATIVE SITUATION-MODEL prototype for the name-bridge residual:
an ONLINE, GRADED, fine-grained per-entity IDENTITY FILE, accrued from the document's OWN structured predicates
(no static KB), that licenses a common-noun anaphor to its proper-name antecedent for DOCUMENT-LOCAL entities.

BRAIN (PINNED-ish): Heim 1982 file-change (each entity is a file card updated online); Kuperberg 2016 generative
predictive coding (the reader infers an entity's KIND from the situation it builds); van den Broek Landscape
(activation accrues across the text); ATL person/entity-identity node (Bruce-Young) filled from discourse; CLS
hippocampal-episodic route for entities never seen before. The file is a GRADED, content-addressable type
distribution -- NOT a hard flag (a hard coarse flag OVER-LICENSES: exp_namebridge_discourse_type_v1 measured -0.025).

ONLINE ACCRUAL (glass-box, offline lexicon only) -- each named entity accrues weighted FINE type evidence from:
  - APPOSITION / COPULA in-text is-a ("Zurbaran, the artist" / "X is a country")          [strong, explicit]
  - HEAD-IN-NAME ("Amherst College" -> college)                                            [strong]
  - PERSONAL TITLE (Mr./Dr./President/Saint/Abba)                                           [person + role]
  - DEVERBAL AGENCY as subject (write->writer, compose->composer; Crutch-Warrington)        [fine occupation]
  - POSSESSED-NOUN type-diagnostic relation ("X's capital/president" -> country; "X's CEO"  [THE fine generative
        -> organization; "X's album" -> musician; "X's wife" -> person)                      signal, novel here]
  - LOCATIVE predication ("in/at/to X") -> place                                            [graded, weak]
  - GENDER (gazetteer/title) -> man/woman                                                   [graded]
At an anaphor headed h, each candidate name is scored by GRADED content-addressable match of its accrued file
against h (sum of evidence weights whose type licenses h, via the C5 is-a closure) + lambda*recency; argmax. This
is soft settling, not a filter.

CONTROLS (per the causal-testimony solver's transfer note): report the DOCUMENT-LOCAL subslice (gold in NO static
KB) with the recency floor beside it (recency is structurally ~0.34 there, so any lift is unambiguously the
generative type); matched distractors (the real co-active names, often also predicated); a WITHIN-ITEM ASYMMETRY
test (does the file license the GOLD anaphor head more than a MISMATCHED head?); and a SHUFFLE-the-file info-free
twin. Glass-box, NO external LLM. Own data dir. NO hdlab write (Q111).
Run: .venv/Scripts/python.exe experiments/exp_namebridge_generative_typefile_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_namebridge_generative_typefile_v1.py            (full)
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import argparse
import json
import math
import sys
import time

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
from experiments.exp_namebridge_enumerate_gum_v1 import propn_surface
from experiments.exp_commonnoun_wall_gum_v1 import extract_isa_edges
import experiments.exp_namebridge_coref_kb_v1 as KB
import experiments.exp_namebridge_worldknowledge_v1 as WK
import experiments._entity_type_spoke as ES

OUT_DIR = os.path.join(_REPO, "data", "exp_namebridge_generative_typefile_v1")

_LOCPREP = {"in", "at", "to", "from", "into", "within", "near", "across", "through", "onto", "inside", "via"}
# The TITLE-ROLE / TITLES / POSSESSED-TYPE who-is-who lexicons are now the DURABLE knowledge asset
# `hdlab.who_is_who_lexicon` (grown-knowledge incorporation, 2026-09-10) -- imported here byte-identically so the
# asset is the SINGLE source of truth (witness `verification/test_who_is_who_lexicon.py`). Aliased to the local
# names the rest of this cell uses.
from hdlab.who_is_who_lexicon import TITLE_ROLE as _TITLE_ROLE, TITLES as _TITLES, POSSESSED_TYPE as _POSSESSED_TYPE
_SPEECH = {"say", "tell", "ask", "reply", "argue", "explain", "claim", "state", "declare", "insist"}


def _wn():
    return ES.TS._wordnet()


def _license(head, lemma):
    return ES._license_lemma(head, lemma)


_BK = None
def _broader_lemmas(surfaces):
    """Lever 2: DBpedia InstanceOf UNION the broader recognition-cleaned Wikidata dump asset (falls back to
    DBpedia+recognition when the asset is absent/partial)."""
    global _BK
    if _BK is None:
        import experiments.exp_namebridge_broader_kb_v1 as BK
        _BK = BK
    return _BK.broader_lemmas(surfaces)


def _walk_gen(doc):
    """Per-doc name-bridge items with a GRADED type FILE per candidate name referent.
    file = dict(lemma -> summed weight). Returns items = (head, gold_eid, active[with 'file'], intext)."""
    gold_first = {}
    for m in doc.mentions:
        gold_first.setdefault(m.eid, m.order)
    gmap = {t.gidx: t for t in doc.toks}
    by_sent = {}
    for t in doc.toks:
        by_sent.setdefault(t.sent, {})[t.idx] = t
    case_children = {}
    cop_heads = set()
    appos_of = {}          # (sent, head_idx) -> [appositive noun lemmas]
    conj_noun = {}         # (sent, idx) -> [common-noun lemmas this token is COORDINATED with] (shared fine type)
    for t in doc.toks:
        d0 = t.deprel.split(":")[0]
        if d0 == "case":
            case_children.setdefault((t.sent, t.head), []).append(t.lemma.lower())
        if d0 == "cop":
            cop_heads.add((t.sent, t.head))
        if d0 == "appos" and t.upos in ("NOUN",):
            appos_of.setdefault((t.sent, t.head), []).append(t.lemma.lower())
        if d0 == "conj":                     # COORDINATION: "X and other villages" -> X is-a village (fine, shared type)
            if t.upos == "NOUN":
                conj_noun.setdefault((t.sent, t.head), []).append(t.lemma.lower())   # head <-conj- noun
    # the WALL cell's proven apposition/copula/head-in-name extractor: (common_head_lemma, name_token_set, order)
    isa_edges = [(lem, set(ntok), order) for (lem, ntok, order) in extract_isa_edges(doc)]

    head_ref = {}
    name_refs = []
    items = []

    def accrue(f, lemmas, w):
        for l in lemmas:
            f[l] = f.get(l, 0.0) + w

    for m in doc.mentions:
        if m.mtype == "name":
            nt, nstr = propn_surface(doc, m)
            if not nt:
                continue
            t = gmap.get(m.head_g)
            f = {}
            # head-in-name: a common-noun-looking token inside the name (college, university, church, sea, river)
            for tok in nt:
                if _wn() is not None and _wn().synsets(tok, pos="n"):
                    accrue(f, [tok], 2.0)
            if t is not None:
                d0 = t.deprel.split(":")[0]
                cases = case_children.get((t.sent, t.idx), [])
                # apposition: nouns appositive TO this name ("Zurbaran, the artist")
                accrue(f, appos_of.get((t.sent, t.idx), []), 3.0)
                # copula predicate-nominal: "X is a Y" -> t nsubj of Y (a noun) with a cop child
                if d0 == "nsubj":
                    gv = by_sent.get(t.sent, {}).get(t.head)
                    if gv is not None:
                        if gv.upos == "NOUN" and (t.sent, gv.idx) in cop_heads:
                            accrue(f, [gv.lemma.lower()], 3.0)
                        elif gv.upos == "VERB":
                            lv = gv.lemma.lower()
                            ag = KB.agent_types(lv)
                            if ag and lv not in KB._LIGHT_VERBS:
                                accrue(f, ag, 1.5)          # deverbal fine occupation
                            if lv in _SPEECH:
                                accrue(f, ["person"], 0.5)  # selectional: speaker is a person
                # possessed-noun relation: "X's Y" (nmod:poss on X, head Y) OR "Y of X" (X nmod of Y, case 'of')
                Y = None
                if "poss" in t.deprel:
                    Y = by_sent.get(t.sent, {}).get(t.head)
                elif d0 == "nmod" and "of" in cases:
                    Y = by_sent.get(t.sent, {}).get(t.head)
                if Y is not None and Y.upos in ("NOUN",):
                    accrue(f, _POSSESSED_TYPE.get(Y.lemma.lower(), ()), 2.0)
                # COORDINATION with a common noun -> shared FINE type (X conj-> noun, or noun conj-> X)
                if d0 == "conj":
                    H = by_sent.get(t.sent, {}).get(t.head)
                    if H is not None and H.upos == "NOUN":
                        accrue(f, [H.lemma.lower()], 2.0)
                accrue(f, conj_noun.get((t.sent, t.idx), []), 2.0)
                # CLASSIFYING HEAD NOUN via the NAMING relations only (flat/appos): "the term NEXUS" (Nexus flat
                # of term). An in-text is-a (Kamp/Heim naming) the appos/copula routes miss because here the NAME is
                # the dependent. Restricted to flat/appos -- compound/nmod OVER-FIRE on modifier compounds ("Boxer
                # Indemnity SCHOLARSHIP", "New York TIMES") that are NOT the entity's type (measured: broad HURTS).
                if d0 in ("flat", "appos"):
                    H = by_sent.get(t.sent, {}).get(t.head)
                    if H is not None and H.upos == "NOUN":
                        accrue(f, [H.lemma.lower()], 2.5)
                # locative predication -> place (graded, weak)
                if d0 in ("obl", "nmod") and any(c in _LOCPREP for c in cases):
                    accrue(f, ["location"], 1.0)
                # personal TITLE -> the FINE ROLE (who-is-who): "President Chao" -> president, not just person.
                # Check the token before the span AND the leading tokens inside the name span.
                title_toks = []
                prev = gmap.get(m.start_g - 1)
                if prev is not None:
                    title_toks.append(prev.form.rstrip(".").lower())
                for g in range(m.start_g, min(m.start_g + 2, m.end_g + 1)):
                    tt = gmap.get(g)
                    if tt is not None:
                        title_toks.append(tt.form.rstrip(".").lower())
                for tw in title_toks:
                    if tw in _TITLE_ROLE:
                        accrue(f, [_TITLE_ROLE[tw]], 2.5)      # the title IS the fine role
                        accrue(f, ["person"], 1.0)
                    elif tw in _TITLES:                        # generic honorific -> person only
                        accrue(f, ["person"], 2.0)
            # gender -> man/woman (graded)
            if m.gender == "m":
                accrue(f, ["man"], 1.0)
            elif m.gender == "f":
                accrue(f, ["woman"], 1.0)

            merged = False
            for r in name_refs:
                if r["tokens"] & nt:
                    r["tokens"] |= nt; r["order"] = m.order; r["surfaces"].add(nstr)
                    r["orders"].append(m.order)          # ALL access times -> ACT-R base-level activation
                    for l, w in f.items():
                        r["file"][l] = r["file"].get(l, 0.0) + w
                    if m.gender and not r["gender"]:
                        r["gender"] = m.gender
                    merged = True
                    break
            if not merged:
                name_refs.append({"tokens": set(nt), "surfaces": {nstr}, "order": m.order, "eid": m.eid,
                                  "gender": m.gender, "file": dict(f), "orders": [m.order]})
        elif m.mtype == "common":
            is_ana = gold_first[m.eid] < m.order
            if is_ana and m.lemma_head not in head_ref:
                gold_names = [r for r in name_refs if r["eid"] == m.eid and r["order"] < m.order]
                if gold_names:
                    active = sorted([r for r in name_refs if r["order"] < m.order], key=lambda r: -r["order"])
                    out_active = []
                    for r in active:
                        fl = dict(r["file"])
                        # FOLD the proven in-text is-a extractor (apposition/copula/head-in-name) that fired for
                        # THIS referent's name tokens BEFORE the anaphor -- the CLS episodic route, done right.
                        for lem, ntok, o in isa_edges:
                            if o < m.order and (ntok & r["tokens"]):
                                fl[lem] = fl.get(lem, 0.0) + 3.0
                        out_active.append({"surfaces": sorted(r["surfaces"]), "eid": r["eid"],
                                           "order": r["order"], "gender": r["gender"], "file": fl,
                                           "orders": list(r["orders"]), "anaphor_order": m.order})
                    items.append((m.lemma_head, m.eid, out_active, []))
            head_ref[m.lemma_head] = (m.order, m.eid)
    return items


def collect(docs):
    items = []
    for d in docs:
        items.extend(_walk_gen(d))
    return items


def _file_match(head, file):
    """GRADED content-addressable match of an anaphor head against an accrued type file."""
    s = 0.0
    for l, w in file.items():
        if _license(head, l):
            s += w
    return s


D_DECAY = 0.5    # ACT-R base-level decay (Anderson & Schooler power law) -- TESTED, see _salience note


def _salience(active):
    """BRAIN-FAITHFUL salience for definite-anaphor->name = CENTERING recency (Grosz-Joshi-Weinstein): the anaphor
    resolves to the MOST-RECENT type-compatible entity. NOT ACT-R base-level: I TESTED ACT-R (ln sum_k (t_now-t_k)^-d,
    recency+FREQUENCY) and it HURTS here (recency floor 0.392->0.320, gen 0.488->0.432) -- a frequently-mentioned
    distractor wrongly wins, because for a definite description the referent is the most-recent compatible one, not
    the most-frequent. This reproduces the acquire_wikidata P31 SOLVED's measured 'recency (0.472) beats topichood/
    frequency (0.368)'. So Centering-recency is the faithful salience math here; ACT-R frequency is the WRONG model
    for this computation (right model for a different task -- general anaphora salience). Normalized [0,1]."""
    orders = [r["order"] for r in active]
    omin, omax = min(orders), max(orders)
    return {id(r): ((r["order"] - omin) / (omax - omin) if omax > omin else 1.0) for r in active}


def _actr_salience(active):
    """The ACT-R base-level variant kept for the record (measured WORSE than Centering here -- frequency hurts)."""
    apos = max((max(r["orders"]) for r in active), default=0) + 1
    raw = {id(r): math.log(sum(max(apos - o, 1) ** (-D_DECAY) for o in r["orders"])) for r in active}
    vals = list(raw.values()); lo, hi = min(vals), max(vals)
    return {k: ((v - lo) / (hi - lo) if hi > lo else 1.0) for k, v in raw.items()}


def _typematch(head, r, arm, twin):
    f = twin.get(id(r), r["file"]) if twin is not None else r["file"]
    m = _file_match(head, f)                                  # the GENERATIVE online file (episodic route)
    if arm == "gen":
        return m
    kb = WK._reco_type_strength(head, r["surfaces"], True, None)   # consolidated route (DBpedia + fitted probe)
    if arm == "combined":
        return max(m, 3.0 * kb)
    if arm == "routed":
        return 3.0 * kb if kb > 0 else m
    if arm in ("cls_unified", "cls_full", "cls_gate"):
        # CLS: one unified ATL file (episodic file + consolidated KB fine-types), CAPPED-sum so neither swamps.
        uf = dict(f)
        kb_lems = _broader_lemmas(r["surfaces"]) if arm == "cls_full" else WK.reco_lemmas(r["surfaces"], use_wd=True)
        for l in kb_lems:
            uf[l] = max(uf.get(l, 0.0), 2.0)
        return min(sum(w for l, w in uf.items() if _license(head, l)), 3.0)
    return m


def predict(item, arm, twin=None):
    head, ge, active, intext = item
    if not active:
        return None
    sal = _salience(active)                                   # ACT-R base-level activation (brain-faithful recency)
    if arm == "recency":
        return max(active, key=lambda r: sal[id(r)])["eid"]
    tm = {id(r): _typematch(head, r, arm, twin) for r in active}
    if arm == "cls_gate":
        # GATE-then-COMPETE (Lappin-Leass): hard type-license FILTER admits compatible candidates, THEN ACT-R
        # salience selects among survivors -- the brain-faithful integration FORM (the P31 SOLVED proved a flat
        # additive blend underperforms this). Fall back to salience-only when nothing licenses.
        pool = [r for r in active if tm[id(r)] > 0] or active
        return max(pool, key=lambda r: sal[id(r)])["eid"]
    # graded constraint-integration (MacDonald-McRae): type-match + lambda * ACT-R salience
    return max(active, key=lambda r: tm[id(r)] + KB.GRADED_LAMBDA * sal[id(r)])["eid"]


def _vec(items, arm, twin=None):
    return np.array([int(predict(it, arm, twin=twin) == it[1]) for it in items], float)


def build_twin(items, seed=0):
    """Info-free twin: reassign each referent a RANDOM other referent's file (destroy the correspondence)."""
    refs = [r for _, _, active, _ in items for r in active]
    files = [r["file"] for r in refs]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(files))
    return {id(r): files[perm[i]] for i, r in enumerate(refs)}


def doclocal_mask(items):
    """gold NOT typed by ANY static KB (DBpedia + Wikidata probe) -> the document-local subslice."""
    mask = []
    for head, ge, active, intext in items:
        gold = [r for r in active if r["eid"] == ge]
        typed = bool(gold) and any(WK.reco_lemmas([s for s in r["surfaces"]], use_wd=True) for r in gold)
        mask.append(not typed)
    return np.array(mask, bool)


def asymmetry(items):
    """WITHIN-ITEM ASYMMETRY: does the GOLD entity's file license the GOLD head more than a MISMATCHED head?
    Mismatched head chosen cross-family (person<->place). Paired over items where gold has any file evidence."""
    gold_h = []; mis_h = []
    for head, ge, active, intext in items:
        gold = [r for r in active if r["eid"] == ge]
        if not gold:
            continue
        f = {}
        for r in gold:
            for l, w in r["file"].items():
                f[l] = f.get(l, 0.0) + w
        if not f:
            continue
        mism = "country" if ES.TS.is_a(head, "person") or head in ("man", "woman", "person") else "man"
        gm = _file_match(head, f); mm = _file_match(mism, f)
        gold_h.append(gm); mis_h.append(mm)
    gold_h = np.array(gold_h); mis_h = np.array(mis_h)
    d = KB.boot_delta(gold_h, mis_h)
    return {"n_with_file": len(gold_h), "gold_head_match_mean": round(float(gold_h.mean()), 3),
            "mismatched_head_match_mean": round(float(mis_h.mean()), 3), "asymmetry_delta": d}


def _report(items, kbt, mask, label):
    rec = _vec(items, "recency")
    gen = _vec(items, "gen")
    comb = _vec(items, "combined")
    routed = _vec(items, "routed")
    cls = _vec(items, "cls_unified")
    cls_full = _vec(items, "cls_full")
    cls_gate = _vec(items, "cls_gate")
    tw = build_twin(items)
    gen_tw = _vec(items, "gen", twin=tw)
    M = mask
    sub = {
        "n": int(M.sum()),
        "recency": round(float(rec[M].mean()), 4),
        "kb_thematic": round(float(kbt[M].mean()), 4),
        "gen": round(float(gen[M].mean()), 4),
        "combined": round(float(comb[M].mean()), 4),
        "routed": round(float(routed[M].mean()), 4),
        "cls_unified": round(float(cls[M].mean()), 4),
        "cls_full": round(float(cls_full[M].mean()), 4),
        "cls_gate": round(float(cls_gate[M].mean()), 4),
        "gen_minus_recency": KB.boot_delta(gen[M], rec[M]),
        "gen_minus_thematic": KB.boot_delta(gen[M], kbt[M]),
        "gen_minus_twin": KB.boot_delta(gen[M], gen_tw[M]),
        "cls_unified_minus_thematic": KB.boot_delta(cls[M], kbt[M]),
        "cls_gate_minus_thematic": KB.boot_delta(cls_gate[M], kbt[M]),
        "cls_full_minus_thematic": KB.boot_delta(cls_full[M], kbt[M]),
        "null_p95_cls_gate_minus_thematic": KB.null_p95(cls_gate[M], kbt[M]),
    }
    print("[%s] n=%d kb_thematic=%.4f gen=%.4f cls_unified=%.4f cls_gate=%.4f | gen-thematic %+.4f (sep=%s) | "
          "cls_gate-thematic %+.4f CI[%+.4f,%+.4f] (sep=%s) | cls_unified-thematic %+.4f (sep=%s)" % (
              label, sub["n"], sub["kb_thematic"], sub["gen"], sub["cls_unified"], sub["cls_gate"],
              sub["gen_minus_thematic"]["delta"], sub["gen_minus_thematic"]["sep"],
              sub["cls_gate_minus_thematic"]["delta"], sub["cls_gate_minus_thematic"]["lo"],
              sub["cls_gate_minus_thematic"]["hi"], sub["cls_gate_minus_thematic"]["sep"],
              sub["cls_unified_minus_thematic"]["delta"], sub["cls_unified_minus_thematic"]["sep"]), flush=True)
    return sub


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    if not ES.available():
        print("[SKIP] entity-type spoke asset absent"); return {"skipped": True}
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=(60 if smoke else None), name_gazetteer=gaz)
    items = collect(docs)
    kbi = KB.collect_items(docs)                       # aligned 1:1 (same walk order) -> the kb_thematic floor
    assert len(kbi) == len(items) and all(a[0] == b[0] and a[1] == b[1] for a, b in zip(kbi, items)), \
        "KB/gen item alignment"
    kbt = np.array([int(KB.predict(it, "kb_thematic") == it[1]) for it in kbi], float)
    n = len(items)
    whole = np.ones(n, bool)
    dl = doclocal_mask(items)

    res = {
        "n": n,
        "whole_slice": _report(items, kbt, whole, "WHOLE"),
        "document_local_subslice": _report(items, kbt, dl, "DOC-LOCAL"),
        "within_item_asymmetry": asymmetry(items),
        "elapsed_s": round(time.time() - t0, 1),
    }
    dlr = res["document_local_subslice"]; asy = res["within_item_asymmetry"]
    res["headline"] = (
        "GENERATIVE TYPE-FILE (GUM n=%d): DOC-LOCAL subslice n=%d recency=%.3f kb_thematic=%.3f -> gen=%.3f "
        "(vs kb_thematic %+.4f CI[%+.4f,%+.4f] sep=%s; vs recency %+.4f sep=%s; vs shuffle-twin %+.4f sep=%s) | "
        "asymmetry: gold-head %.2f vs mismatched %.2f (%+.4f sep=%s)" % (
            n, dlr["n"], dlr["recency"], dlr["kb_thematic"], dlr["gen"],
            dlr["gen_minus_thematic"]["delta"], dlr["gen_minus_thematic"]["lo"], dlr["gen_minus_thematic"]["hi"],
            dlr["gen_minus_thematic"]["sep"], dlr["gen_minus_recency"]["delta"], dlr["gen_minus_recency"]["sep"],
            dlr["gen_minus_twin"]["delta"], dlr["gen_minus_twin"]["sep"],
            asy["gold_head_match_mean"], asy["mismatched_head_match_mean"],
            asy["asymmetry_delta"]["delta"], asy["asymmetry_delta"]["sep"]))
    tag = "smoke" if smoke else "full"
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % tag), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "namebridge_generative_typefile_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    # possessed-noun accrual: "X's capital" -> country; licenses 'the country'
    it = ("country", 7, [{"surfaces": ["Recentville"], "eid": 3, "order": 9, "gender": "", "file": {},
                          "orders": [9]},
                         {"surfaces": ["Zubrowka"], "eid": 7, "order": 5, "gender": "",
                          "file": {"country": 2.0}, "orders": [5]}], [])
    assert predict(it, "recency") == 3, "ACT-R salience picks the more-recent Recentville (no type cue)"
    assert predict(it, "gen") == 7, "accrued 'country' file licenses 'the country' over recency"
    # graded soft: a weak locative-only file should still lose to a strong appositive-country file
    print("SELFTEST PASS: graded type-file licenses fine anaphor; possessed-noun lexicon size=%d"
          % len(_POSSESSED_TYPE), flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
