"""PROBE (strategy, pri-1 opening move; NOT a build): what information is available per candidate entity on the
same-type-ambiguous pronoun-undergoer slice (GUM modern test, the exp_affected_entity_binding_parallelism_gum_v1 items),
and does ANY event-history coherence signal separate the gold entity from the grammar resolver's wrong picks?

Per item: the undergoer pronoun t (obj / nsubj:pass), its event = (governing verb lemma V, agent lemma A); candidates =
head-individuated prior entities (gn-compatible, Principle-B legal); per candidate c its EVENT HISTORY = the list of
(verb lemma, role class) for each prior mention of c (the mention head's governor).

Reports: coverage (how many candidates have ANY prior event; gold has history), the A5 grammar resolver's wrong set,
and three cheap coherence reads on the wrong set and overall:
  R1 same-predicate repetition: c was an OBJ/PATIENT of the same verb lemma V before.
  R2 GEK forward PPMI (hdlab.generalized_event_knowledge store, ROCStories word transitions): mean PPMI(v_prev -> V)
     over c's prior event verbs.
  R3 role-history: fraction of c's prior mentions as PATIENT (Dowty proto-patient persistence).
plus an ORACLE-ish read: for each read, accuracy if we rerank A5's legal set by (A5 score + lambda * z(read)) for a
lambda sweep, with a SCRAMBLE control (histories permuted across candidates). Runs in ~15 s. ASCII, glass-box.
"""
from __future__ import annotations

import os
import sys
import random
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
import experiments.exp_affected_entity_binding_parallelism_gum_v1 as B4
import hdlab.affected_entity_resolver as AER
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
from hdlab.patient_tendency import lemmatize_verb

SEED = 20260912


def _gov(doc_toks_by_sent, tok):
    """Governing token of `tok` (its head in the same sentence) or None."""
    sent = doc_toks_by_sent.get(tok.sent, {})
    return sent.get(tok.head)


def _agent_lemma(doc_toks_by_sent, verb_tok):
    sent = doc_toks_by_sent.get(verb_tok.sent, {})
    for s in sent.values():
        if s.head == verb_tok.idx and s.deprel in AER.SUBJ_DEPS:
            return (getattr(s, "lemma", None) or s.form).lower()
    return None


def collect(limit=None, predicted_parse=False):
    import experiments.exp_hybrid_unified_incumbent_coref_gum_v1 as HYB
    docs = B1._load_test(limit)
    if predicted_parse:
        for doc in docs:
            B4._overlay_predicted(doc)
    items = []
    for doc in docs:
        mlive = HYB.gum_to_live(doc)
        for i, m in enumerate(mlive):
            m.setdefault("order", i)
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        mi2headg = {i: doc.mentions[i].head_g for i in range(len(doc.mentions))}
        gidx2dep = {t.gidx: t.deprel for t in doc.toks}
        gidx2tok = {t.gidx: t for t in doc.toks}
        by_sent = defaultdict(dict)
        for t in doc.toks:
            by_sent[t.sent][t.idx] = t
        for t in doc.toks:
            if t.deprel not in B1.UND_DEPRELS or t.gidx not in head_to_mi:
                continue
            u_mi = head_to_mi[t.gidx]; u = mlive[u_mi]; M = doc.mentions[u_mi]
            if M.mtype != "pronoun":
                continue
            gold = M.eid
            cands = [x for x in mlive if x["midx"] < u_mi and not x["is_pronoun"] and B1._gn_ok(u, x)]
            if len(cands) < 2:
                continue
            cg = AER.coarg_head_gidx(doc.toks, t)
            coarg = mlive[head_to_mi[cg]]["head"] if (cg is not None and cg in head_to_mi) else None
            ent_hist = defaultdict(list); ent_last = {}; ent_events = defaultdict(list)
            for x in cands:
                h = x["head"]
                ent_hist[h].append((float(x["order"]), B1._role(x.get("sent_role_rank", 2))))
                if h not in ent_last or x["order"] >= ent_last[h]["order"]:
                    ent_last[h] = x
                hg = mi2headg.get(x["midx"])
                htok = gidx2tok.get(hg)
                if htok is not None:
                    g = _gov(by_sent, htok)
                    if g is not None and getattr(g, "upos", "VERB") in ("VERB", "AUX", None):
                        ent_events[h].append((lemmatize_verb((getattr(g, "lemma", None) or g.form).lower()),
                                              AER.role_class(htok.deprel), htok.deprel in AER.PATIENT_DEPS))
            ents = list(ent_hist.keys())
            if len(ents) < 2:
                continue
            now = float(u["order"])
            sal = {h: actr_activation(ent_hist[h], now, DEFAULT_DECAY, ROLE_PROMINENCE) for h in ents}
            role_of = {h: AER.role_class(gidx2dep.get(mi2headg.get(ent_last[h]["midx"]), "")) for h in ents}
            patient_of = {h: (gidx2dep.get(mi2headg.get(ent_last[h]["midx"]), "") in AER.PATIENT_DEPS) for h in ents}
            a_role = AER.role_class(t.deprel)
            legal = AER.legal_candidates(ents, coarg)
            vt = _gov(by_sent, t)
            V = lemmatize_verb((getattr(vt, "lemma", None) or vt.form).lower()) if vt is not None else None
            A = _agent_lemma(by_sent, vt) if vt is not None else None
            items.append({
                "doc": getattr(doc, "name", ""), "gold": gold, "ents": ents, "legal": legal, "sal": sal,
                "role_of": role_of, "patient_of": patient_of, "a_role": a_role, "V": V, "A": A,
                "events": {h: ent_events.get(h, []) for h in ents}, "cluster_of": {h: ent_last[h]["cluster"] for h in ents},
                "n_mentions": {h: len(ent_hist[h]) for h in ents},
            })
    return items


def a5_scores(it):
    out = {}
    for h in it["legal"]:
        s = it["sal"][h]
        if it["role_of"][h] == it["a_role"]:
            s += AER.GAMMA_G
        if it["patient_of"].get(h):
            s += AER.GAMMA_T
        out[h] = s
    return out


def main(predicted_parse=False):
    items = collect(predicted_parse=predicted_parse)
    n = len(items)
    rng = random.Random(SEED)
    gek = None
    try:
        from hdlab import generalized_event_knowledge as GEK
        if GEK.available():
            gek = GEK
    except Exception:
        gek = None

    def gek_ppmi(v_prev, v_now):
        if gek is None or v_prev is None or v_now is None:
            return 0.0
        st = gek._store()
        vi = st["vocab_index"] if "vocab_index" in st else None
        if vi is None:
            return 0.0
        a, c = vi.get(v_prev), vi.get(v_now)
        if a is None or c is None:
            return 0.0
        return float(gek._ppmi(st, a, c))

    def reads(it, h, ev):
        V = it["V"]
        r1 = float(any(v == V and pat for v, rc, pat in ev)) if V else 0.0
        r2 = float(np.mean([gek_ppmi(v, V) for v, _, _ in ev])) if (ev and V) else 0.0
        r3 = float(np.mean([1.0 if pat else 0.0 for _, _, pat in ev])) if ev else 0.0
        return r1, r2, r3

    # coverage
    gold_has_hist = 0; two_plus_with_hist = 0; gold_in_legal = 0; legal_ge2 = 0; a5_right = 0
    wrong = []
    for it in items:
        gold_ents = [h for h in it["ents"] if it["cluster_of"][h] == it["gold"]]
        if any(it["events"][h] for h in gold_ents):
            gold_has_hist += 1
        if sum(1 for h in it["legal"] if it["events"][h]) >= 2:
            two_plus_with_hist += 1
        if any(it["cluster_of"][h] == it["gold"] for h in it["legal"]):
            gold_in_legal += 1
        if len(it["legal"]) >= 2:
            legal_ge2 += 1
        sc = a5_scores(it); pick = max(sc, key=sc.get)
        if it["cluster_of"][pick] == it["gold"]:
            a5_right += 1
        else:
            wrong.append(it)
    print(f"items={n}  legal>=2: {legal_ge2}  gold_in_legal: {gold_in_legal} ({gold_in_legal/n:.3f} = ceiling)  "
          f"A5 right: {a5_right} ({a5_right/n:.4f})  wrong: {len(wrong)}")
    print(f"coverage: gold entity has >=1 prior event: {gold_has_hist}/{n} ({gold_has_hist/n:.3f}); "
          f">=2 legal candidates with history: {two_plus_with_hist}/{n} ({two_plus_with_hist/n:.3f})")
    mean_legal = np.mean([len(it["legal"]) for it in items]); mean_ev = np.mean([np.mean([len(it["events"][h]) for h in it["legal"]]) for it in items])
    print(f"mean legal candidates {mean_legal:.2f}; mean prior events per candidate {mean_ev:.2f}; GEK store available: {gek is not None}")
    # on the WRONG set: does gold beat A5's pick on each read?
    for ri, name in enumerate(["R1 same-predicate repetition", "R2 GEK forward PPMI", "R3 patient-role history"]):
        gold_gt = pick_gt = tie = 0
        for it in wrong:
            sc = a5_scores(it); pick = max(sc, key=sc.get)
            gold_ents = [h for h in it["legal"] if it["cluster_of"][h] == it["gold"]]
            if not gold_ents:
                continue
            g = max(reads(it, h, it["events"][h])[ri] for h in gold_ents)
            p = reads(it, pick, it["events"][pick])[ri]
            if g > p: gold_gt += 1
            elif p > g: pick_gt += 1
            else: tie += 1
        print(f"  WRONG set (gold in legal): {name}: gold>pick {gold_gt}, pick>gold {pick_gt}, tie {tie}")
    # rerank sweep with scramble control
    def rerank_acc(ri, lam, scramble=False):
        hits = 0
        for it in items:
            sc = a5_scores(it)
            hs = list(sc.keys())
            evs = [it["events"][h] for h in hs]
            if scramble:
                evs = evs[:]; rng.shuffle(evs)
            vals = np.array([reads(it, h, ev)[ri] for h, ev in zip(hs, evs)])
            z = (vals - vals.mean()) / (vals.std() + 1e-9) if vals.std() > 0 else np.zeros_like(vals)
            tot = {h: sc[h] + lam * z[i] for i, h in enumerate(hs)}
            pick = max(tot, key=tot.get)
            hits += int(it["cluster_of"][pick] == it["gold"])
        return hits / n
    print("rerank sweep (A5 + lambda*z(read)); A5 alone = %.4f" % (a5_right / n))
    for ri, name in enumerate(["R1", "R2", "R3"]):
        row = []
        for lam in (0.25, 0.5, 1.0, 2.0):
            row.append(f"lam={lam}: {rerank_acc(ri, lam):.4f} (scr {rerank_acc(ri, lam, True):.4f})")
        print(f"  {name}: " + " | ".join(row))
    # examples of wrong items with the event histories, for eyeballing
    print("\nexamples (wrong set, first 6):")
    for it in wrong[:6]:
        sc = a5_scores(it); pick = max(sc, key=sc.get)
        gold_ents = [h for h in it["ents"] if it["cluster_of"][h] == it["gold"]]
        print(f"  event V={it['V']} A={it['A']} a_role={it['a_role']} | pick={pick} ev={it['events'][pick][:4]} | gold={gold_ents} ev={[it['events'][h][:4] for h in gold_ents]}")


if __name__ == "__main__":
    main(predicted_parse="--predicted" in sys.argv)
