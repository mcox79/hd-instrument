"""PROBE v2 (strategy, pri-1): the brain's residual computation, read by read, on the GUM same-type-ambiguous slice.

Research (notes/RESEARCH_* to follow): after grammar, the brain scores each candidate token X by
  plaus(X) = P(kind(X) | agent, verb)  x  compat(state(X), preconditions(verb))  x  (1 - contradiction(state(X), result(verb)))
computed INCREMENTALLY at the verb (Bicknell 2010; Kamide 2003; Rabovsky-McClelland SG update), then fused as a Bayesian
likelihood with the salience prior x grammatical likelihood (Kehler-Rohde). This probe measures the available glass-box
reads for each factor on the 1,142 items and fuses them in LOG space (a temperature tau, swept; scramble control):
  R1 same-predicate repetition (entity-specific event memory): X was a PATIENT of this verb lemma before.
  R2 event-history coherence: mean forward PPMI(v_prev -> V) over X's prior event verbs (GEK store, ROCStories).
  R4 selectional likelihood: smoothed log P(head(X) | V, OBJ) / P(head(X)) from the reading-grown selectional store
     (simplewiki), WordNet-supersense back-off via typed_selectional_preference when the lexical count is zero.
  R5 GEK content expectation: GEKProjector.score(sentence content lemmas -> head(X)) (Elman 2009 readout, the organ).
  R6 agent-conditioned selectional: P(head(X) | V, OBJ) restricted to... (NOT available: the store holds (verb,role)
     marginals only -> reported as a coverage gap, the joint needs an offline asset).
Reports per read: coverage on the slice, gold>pick / pick>gold on the wrong set, rerank accuracy over tau with scramble.
"""
from __future__ import annotations

import math
import os
import pickle
import sys
import random
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.probe_entity_state_residual_gum_v1 as P1
import hdlab.affected_entity_resolver as AER
from hdlab.patient_tendency import lemmatize_verb

SEED = 20260912
STORE = os.path.join(REPO, "data", "selectional_preferences_v1", "selectional_slots_v1.pkl")


def load_selectional():
    with open(STORE, "rb") as f:
        SF = pickle.load(f)["slot_filler"]
    roles = set(r for _, r in SF.keys())
    obj = {}
    bg = defaultdict(float); G = 0.0
    for (verb, role), fillers in SF.items():
        if role != "OBJ":
            continue
        vl = lemmatize_verb(verb.lower())
        d = obj.setdefault(vl, defaultdict(float))
        for fw, c in fillers.items():
            fl = fw.lower().strip(".,;:'\"")
            d[fl] += c; bg[fl] += c; G += c
    return obj, bg, G, roles


def collect_with_sentences(predicted_parse=False):
    """Re-run P1.collect but also attach the current sentence's content lemmas per item."""
    import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
    import experiments.exp_affected_entity_binding_parallelism_gum_v1 as B4
    import experiments.exp_hybrid_unified_incumbent_coref_gum_v1 as HYB
    docs = B1._load_test(None)
    if predicted_parse:
        for doc in docs:
            B4._overlay_predicted(doc)
    items = P1.collect(predicted_parse=False) if not predicted_parse else P1.collect(predicted_parse=True)
    # attach sentence lemmas by re-walking docs in the same order as P1.collect
    sents = []
    for doc in docs:
        mlive = HYB.gum_to_live(doc)
        for i, m in enumerate(mlive):
            m.setdefault("order", i)
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        by_sent = defaultdict(list)
        for t in doc.toks:
            by_sent[t.sent].append(t)
        for t in doc.toks:
            if t.deprel not in B1.UND_DEPRELS or t.gidx not in head_to_mi:
                continue
            u_mi = head_to_mi[t.gidx]; u = mlive[u_mi]; M = doc.mentions[u_mi]
            if M.mtype != "pronoun":
                continue
            cands = [x for x in mlive if x["midx"] < u_mi and not x["is_pronoun"] and B1._gn_ok(u, x)]
            if len(cands) < 2:
                continue
            ents = set(x["head"] for x in cands)
            if len(ents) < 2:
                continue
            lem = [(getattr(s, "lemma", None) or s.form).lower() for s in by_sent[t.sent]
                   if getattr(s, "upos", "") in ("NOUN", "VERB", "ADJ", "PROPN") and s.gidx != t.gidx]
            sents.append(lem)
    assert len(sents) == len(items), (len(sents), len(items))
    for it, lem in zip(items, sents):
        it["sent_lemmas"] = lem
    return items


def main(predicted_parse=False):
    items = collect_with_sentences(predicted_parse)
    n = len(items)
    rng = random.Random(SEED)
    obj, bg, G, roles = load_selectional()
    print(f"selectional store roles: {sorted(roles)}; verbs with OBJ fillers: {len(obj)}; filler types: {len(bg)}")
    from hdlab import generalized_event_knowledge as GEK
    import hdlab.typed_selectional_preference as TSP
    st = GEK._store()
    tsp = TSP.get()
    proj = GEK.GEKProjector()

    def r2(it, h):
        V = it["V"]
        if V is None or V not in st["wid"]:
            return None
        vals = [GEK._ppmi(st, st["wid"][v], st["wid"][V]) for v, _, _ in it["events"][h] if v in st["wid"]]
        return float(np.mean(vals)) if vals else None

    ALPHA = 1.0
    def r4(it, h):
        V = it["V"]
        if V is None or V not in obj:
            return None
        d = obj[V]; N = sum(d.values())
        c = d.get(h, 0.0)
        pb = (bg.get(h, 0.0) + 0.5) / (G + 0.5 * len(bg))      # background rate of the head as an object
        if c > 0:
            p = (c + ALPHA * pb) / (N + ALPHA)
            return math.log(p / pb)
        # back-off: typed association A(v, class(head)) scaled to a log-ratio-like quantity
        a = tsp.score(V, h)
        if a is None:
            return 0.0
        return math.log((ALPHA * pb * (1.0 + 4.0 * max(0.0, a))) / (N + ALPHA) / pb)

    def r5(it, h):
        if not it["sent_lemmas"]:
            return None
        s = proj.score(it["sent_lemmas"], [h])
        return float(s) if s is not None else None

    def r1(it, h):
        V = it["V"]
        return float(any(v == V and pat for v, rc, pat in it["events"][h])) if V else 0.0

    READS = [("R1 same-predicate", r1), ("R2 history->V PPMI", r2), ("R4 selectional lnP(head|V)/P(head)", r4),
             ("R5 GEK content->head", r5)]

    a5 = {}
    wrong = []
    for it in items:
        sc = P1.a5_scores(it); pick = max(sc, key=sc.get); a5[id(it)] = (sc, pick)
        if it["cluster_of"][pick] != it["gold"]:
            wrong.append(it)
    base = 1 - len(wrong) / n
    print(f"items={n} A5={base:.4f} wrong={len(wrong)}")
    for name, fn in READS:
        cov_items = 0; gold_gt = pick_gt = tie = 0
        for it in items:
            vals = {h: fn(it, h) for h in it["legal"]}
            if sum(1 for v in vals.values() if v is not None) >= 2:
                cov_items += 1
        for it in wrong:
            sc, pick = a5[id(it)]
            gold_ents = [h for h in it["legal"] if it["cluster_of"][h] == it["gold"]]
            if not gold_ents:
                continue
            gv = [fn(it, h) for h in gold_ents]; gv = [v for v in gv if v is not None]
            pv = fn(it, pick)
            if not gv or pv is None:
                tie += 1; continue
            g = max(gv)
            if g > pv + 1e-9: gold_gt += 1
            elif pv > g + 1e-9: pick_gt += 1
            else: tie += 1
        print(f"  {name}: items with >=2 scored candidates {cov_items}/{n} ({cov_items/n:.2f}); WRONG set gold>pick {gold_gt}, pick>gold {pick_gt}, tie/abstain {tie}")

    def rerank(fn, tau, scramble=False, items_=items):
        hits = 0
        for it in items_:
            sc, _ = a5[id(it)]
            hs = list(sc.keys())
            vals = [fn(it, h) for h in hs]
            if scramble:
                rng.shuffle(vals)
            # abstain -> 0 contribution (no information), present -> log-likelihood term
            tot = {h: sc[h] + tau * (v if v is not None else 0.0) for h, v in zip(hs, vals)}
            pick = max(tot, key=tot.get)
            hits += int(it["cluster_of"][pick] == it["gold"])
        return hits / len(items_)

    print(f"rerank: A5 + tau*read (log space); A5 alone = {base:.4f}")
    for name, fn in READS:
        row = []
        for tau in (0.25, 0.5, 1.0, 2.0, 4.0):
            row.append(f"tau={tau}: {rerank(fn, tau):.4f} (scr {rerank(fn, tau, True):.4f})")
        print(f"  {name}: " + " | ".join(row))
    # combined R1+R4+R5 (sum of available log terms)
    def combo(it, h):
        vs = [fn(it, h) for _, fn in READS if fn is not r2]
        vs = [v for v in vs if v is not None]
        return sum(vs) if vs else None
    row = []
    for tau in (0.25, 0.5, 1.0, 2.0):
        row.append(f"tau={tau}: {rerank(combo, tau):.4f} (scr {rerank(combo, tau, True):.4f})")
    print("  COMBO R1+R4+R5: " + " | ".join(row))
    # paired bootstrap CI for the best-looking single read at tau=1 (probe-level, optimistic)
    def hits_vec(fn, tau):
        out = []
        for it in items:
            sc, _ = a5[id(it)]
            tot = {h: sc[h] + tau * (fn(it, h) or 0.0) for h in sc}
            pick = max(tot, key=tot.get); out.append(int(it["cluster_of"][pick] == it["gold"]))
        return np.array(out)
    base_vec = np.array([int(it["cluster_of"][a5[id(it)][1]] == it["gold"]) for it in items])
    rng2 = np.random.default_rng(SEED)
    for name, fn in READS + [("COMBO", combo)]:
        for tau in (0.5, 1.0):
            d = hits_vec(fn, tau) - base_vec
            boots = np.array([d[rng2.integers(0, n, n)].mean() for _ in range(2000)])
            print(f"  CI {name} tau={tau}: delta {d.mean():+.4f} CI95 [{np.percentile(boots,2.5):+.4f}, {np.percentile(boots,97.5):+.4f}]")


if __name__ == "__main__":
    main(predicted_parse="--predicted" in sys.argv)
