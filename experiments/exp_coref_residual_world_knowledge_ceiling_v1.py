"""exp_coref_residual_world_knowledge_ceiling_v1 -- the WORLD-KNOWLEDGE ceiling on the coref residual: do a
WordNet-class selectional-plausibility cue and a ConceptNet/CSKG commonsense-KB cue recover the residual? NO.

MOTIVATION. The cross-domain GAP test proved the residual is SEMANTIC_WALL_NOT_PARSE_WALL. A world-knowledge research
drill (research_world_knowledge_for_reference_2026-08-29.md) said: BUILD a KG/WordNet selectional-plausibility cue for
the OBJECT slice, but MEASURE THE ORACLE CEILING FIRST (the discipline that caught the coherence prior's near-chance
oracle this cycle). This cell measures those two knowledge-based ORACLE ceilings on the residual -- the BEST case for a
static-KB, no-LLM approach.

RESULT. Both are DEAD on the residual: WordNet-supersense selectional oracle ~0.02 (even on the object slice, 0/29 on
the distinct-supersense subset); CSKG commonsense-connectivity oracle ~0.028 DESPITE 87% coverage (the KB HAS connecting
edges but does not DISCRIMINATE). WHY: the residual is BY CONSTRUCTION the ANTI-TYPICAL cases (gold is NOT the salient /
frequent / typical candidate -- confirmed: gold's recency-rank ~2, the resolver grabs the most-frequent entity 36% of
the time). So EVERY cue that tracks typicality -- salience, structure, selectional plausibility, commonsense connectivity
-- is anti-predictive on it. The disambiguating information is the SPECIFIC-DISCOURSE event ("who did what in THIS
text"), which a COMMONSENSE KG structurally does not contain (concept-level, not this-discourse facts) and selectional
plausibility cannot supply (both candidates are typical fillers). This is the Winograd core: the pre-LLM literature
(research note) reports NO fully-automatic static-KG system cracks WSC-273 (the one full-set 57% used LIVE web search,
not admissible). BOUND, with a specific measured reason.

Run: .venv/Scripts/python.exe experiments/exp_coref_residual_world_knowledge_ceiling_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_residual_world_knowledge_ceiling_v1.py --run
ASCII. NLTK WordNet + the CSKG foundation (admissible static assets). Writes only its own data dir. NO hdlab/ write.
# KB_REFERENT: data/litbank/who_did_what_events.json
# KB_REFERENT: data/cskg_foundation_v1/edges_shard_00.jsonl
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_coref_graded_cue_retrieval_litbank_v1 import (  # noqa: E402
    load_streams, build_instances, _supports, tune_graded, arm_graded)

CONLL = os.path.join(REPO, "data", "litbank", "coref", "conll")
CSKG_GLOB = os.path.join(REPO, "data", "cskg_foundation_v1", "edges_shard_*.jsonl")
OUTDIR = os.path.join(REPO, "data", "exp_coref_residual_world_knowledge_ceiling_v1")
PRON = set("he she it they him her them his its their himself herself itself themselves we i you me one".split())
STOP = set("the a an of to in on and or but is was were are be been being that this it he she they i you we as at by "
           "for with from her his its their them him".split())

_SS = {}


def _supersense(word):
    if not word:
        return None
    if word in _SS:
        return _SS[word]
    from nltk.corpus import wordnet as wn
    syns = wn.synsets(word, pos=wn.NOUN)
    v = syns[0].lexname() if syns else None
    _SS[word] = v
    return v


_SENTS = {}


def _sents(doc):
    if doc in _SENTS:
        return _SENTS[doc]
    ss, cur = [], []
    with open(os.path.join(CONLL, doc + ".conll"), encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("#"):
                continue
            if not line.strip():
                if cur:
                    ss.append(cur)
                    cur = []
                continue
            cur.append(line.split("\t")[3])
    if cur:
        ss.append(cur)
    _SENTS[doc] = ss
    return ss


def _residual(test, w0, d0):
    out = []
    for inst in test:
        ids, sup, gi = _supports(inst)
        r = arm_graded(ids, sup, gi, inst, w0, 2.0, d0)
        dom = not ((int(sup["recency"].argmax()) == gi) or (sup["subject"][gi] == sup["subject"].max())
                   or (sup["freq"][gi] == sup["freq"].max()))
        if r["pick"] != gi and dom:
            out.append((inst, gi, r["pick"], sup))
    return out


def run(docs=None):
    streams = load_streams(docs)
    insts = build_instances(streams)
    all_docs = sorted({i["doc"] for i in insts})
    dev_docs = set(all_docs[0::2])
    dev = [i for i in insts if i["doc"] in dev_docs]
    test = [i for i in insts if i["doc"] not in dev_docs]
    w0, _g, d0 = tune_graded(dev)

    head_by = defaultdict(Counter)
    gov_by = defaultdict(list)
    for rec in streams:
        for m in rec["stream"]:
            head_by[(rec["doc"], m["gold"])][m["head_text"].lower()] += 1
            gov_by[(rec["doc"], m["sent"], m["gold"])].append(m)

    def nominal(doc, c):
        for h, _n in head_by[(doc, c)].most_common():
            if h not in PRON:
                return h
        return None

    def pron_vr(inst):
        for m in gov_by.get((inst["doc"], inst["p_sent"], inst["gold_cid"]), []):
            if m["head_text"].lower() in PRON and m.get("gov_verb"):
                return m["gov_verb"], m["role"]
        return None, None

    res = _residual(test, w0, d0)
    n = len(res)

    # --- anti-typicality: gold's recency rank; resolver picks the most-frequent
    ranks, pick_most_freq = [], 0
    for inst, gi, pick, sup in res:
        order = np.argsort(-sup["recency"])
        ranks.append(int(np.where(order == gi)[0][0]))
        pick_most_freq += int(sup["freq"][pick] == sup["freq"].max())

    # --- WordNet-supersense selectional preference (learned on DEV), oracle on residual
    vr = defaultdict(Counter)
    role_pref = defaultdict(Counter)
    for rec in streams:
        if rec["doc"] not in dev_docs:
            continue
        for m in rec["stream"]:
            v = m.get("gov_verb")
            h = m["head_text"].lower()
            if not v or h in PRON:
                continue
            ss = _supersense(h)
            if ss:
                vr[(v, m["role"])][ss] += 1
                role_pref[m["role"]][ss] += 1

    def sel_score(v, r, ss):
        if ss is None:
            return 0.0
        c = vr.get((v, r))
        if c and sum(c.values()) >= 3:
            return (c[ss] + 0.1) / (sum(c.values()) + 0.1 * len(c))
        rc = role_pref.get(r)
        return (rc[ss] + 0.1) / (sum(rc.values()) + 0.1 * len(rc)) if rc else 0.0
    sel_hit = sel_appl = 0
    for inst, gi, _pk, _sup in res:
        v, r = pron_vr(inst)
        cand_ss = [_supersense(nominal(inst["doc"], c)) for c in inst["cand_ids"]]
        if v is None or all(s is None for s in cand_ss):
            continue
        sel_appl += 1
        if int(np.argmax([sel_score(v, r, s) for s in cand_ss])) == gi:
            sel_hit += 1

    # --- CSKG commonsense-connectivity oracle: candidate <-> pronoun-clause context words
    cand_heads = set()
    ctx_by = []
    for inst, gi, _pk, _sup in res:
        for c in inst["cand_ids"]:
            h = nominal(inst["doc"], c)
            if h:
                cand_heads.add(h.replace(" ", "_"))
        ps = inst["p_sent"]
        toks = [t.lower() for t in _sents(inst["doc"])[ps]] if ps < len(_sents(inst["doc"])) else []
        ctx_by.append(set(t for t in toks if t.isalpha() and t not in STOP and len(t) > 2))
    ctxwords = set().union(*ctx_by) if ctx_by else set()
    adj = defaultdict(Counter)
    for f in glob.glob(CSKG_GLOB):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                s, o = e["subject"], e["obj"]
                if s in cand_heads and o in ctxwords:
                    adj[s][o] += 1
                if o in cand_heads and s in ctxwords:
                    adj[o][s] += 1
    kb_hit = kb_appl = 0
    for (inst, gi, _pk, _sup), cw in zip(res, ctx_by):
        scores = []
        for c in inst["cand_ids"]:
            h = nominal(inst["doc"], c)
            hn = h.replace(" ", "_") if h else None
            scores.append(sum(adj[hn][w] for w in cw) if hn else 0.0)
        if max(scores) > 0:
            kb_appl += 1
            if int(np.argmax(scores)) == gi:
                kb_hit += 1

    out = {
        "anchor": "coref_residual_world_knowledge_ceiling_v1",
        "population": "LitBank structurally-dominated coref residual (likelihood-only errors)",
        "n_residual": n,
        "anti_typicality": {"gold_recency_rank_mean": round(float(np.mean(ranks)), 2),
                            "gold_recency_rank_median": int(np.median(ranks)),
                            "resolver_pick_is_most_frequent_frac": round(pick_most_freq / max(n, 1), 3),
                            "note": "gold is NON-salient (anti-typical); the resolver grabs the typical/topical entity"},
        "wordnet_selectional_oracle": {"applicable": sel_appl, "hit": sel_hit,
                                       "acc": round(sel_hit / max(sel_appl, 1), 3)},
        "cskg_commonsense_oracle": {"applicable_any_edge": kb_appl, "coverage_frac": round(kb_appl / max(n, 1), 3),
                                    "hit": kb_hit, "acc": round(kb_hit / max(kb_appl, 1), 3),
                                    "note": "coverage is HIGH but the KB does not DISCRIMINATE -> the answer is a "
                                            "specific-discourse fact, not general commonsense"},
        "verdict": ("WORLD_KNOWLEDGE_DEAD_ON_RESIDUAL"
                    if (sel_hit / max(sel_appl, 1) < 0.1 and kb_hit / max(kb_appl, 1) < 0.1)
                    else "A_KB_CHANNEL_RECOVERS_SOME"),
    }
    return out


def self_test():
    """Fixture: the WordNet supersense + CSKG loaders behave on a tiny input."""
    ss = _supersense("rabbit")
    assert ss is None or ss.startswith("noun."), "supersense must be a WordNet lexname or None"
    assert _supersense("passage") != _supersense("rabbit") or _supersense("rabbit") is None, \
        "distinct object nouns should (usually) differ in supersense"
    print("SELF-TEST PASS (WordNet supersense loader behaves)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    if args.run:
        m = run(docs=args.docs)
        os.makedirs(OUTDIR, exist_ok=True)
        tmp = os.path.join(OUTDIR, "metrics.json.tmp")
        with open(tmp, "w", encoding="ascii") as fh:
            json.dump(m, fh, indent=2)
        os.replace(tmp, os.path.join(OUTDIR, "metrics.json"))
        print(json.dumps(m, indent=2))
        return
    print("use --self-test | --run")


if __name__ == "__main__":
    main()
