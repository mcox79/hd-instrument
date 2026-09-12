"""PROBE v8 (strategy, pri-1 arm 2 opening): IN-FOCUS semantic fit from the document's OWN event history, generalised through
OUR meaning hub (no external corpus marginals). For each candidate entity X among the forward-half resolver's top-k, the
coherence of X's prior predicates with the current verb V:
  S_exact(X)  = 1[X was a PATIENT of V before]                       (R1, the only positive knowledge read so far)
  S_sim(X)    = max_{v' in hist(X)} relatedness(V, v')               (hub: hdlab.coherence_reader.relatedness, PPMI+SVD ATL hub)
  S_simrole(X)= max over hist(X) where X was PATIENT of v'            (role-matched: patient-of-similar-event)
Fused as A5_forward score + tau * z(S) INSIDE the top-k focus only, with a PRIOR-PRECISION gate (apply only when the prior's
top-2 margin < g) -- the Kuperberg-Jaeger precision weighting; scramble control (S permuted across the focus set); paired CIs.
THIRD-person items; uses the landed forward-half engine (EntityTokens) as the prior.
"""
from __future__ import annotations

import os
import random
import sys
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
import experiments.exp_affected_entity_token_history_gum_v1 as TH
import hdlab.affected_entity_resolver as AER
from hdlab.patient_tendency import lemmatize_verb
from hdlab import coherence_reader as CR

SEED = 20260912


def collect(predicted_parse=False):
    """Items with the forward-half prior's ranked focus set and per-entity predicate histories (from the document)."""
    data = TH.load(predicted_parse)
    items = []
    for doc, mlive in data:
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        mi2headg = {i: doc.mentions[i].head_g for i in range(len(doc.mentions))}
        gidx2dep = {t.gidx: t.deprel for t in doc.toks}
        gidx2tok = {t.gidx: t for t in doc.toks}
        by_sent = defaultdict(dict)
        for t in doc.toks:
            by_sent[t.sent][t.idx] = t
        und = {}
        for t in doc.toks:
            if t.deprel in B1.UND_DEPRELS and t.gidx in head_to_mi and doc.mentions[head_to_mi[t.gidx]].mtype == "pronoun":
                und[head_to_mi[t.gidx]] = t
        T = AER.EntityTokens()
        ev_hist = defaultdict(list)          # head -> [(verb lemma, was_patient)] from NON-pronoun mentions + accrued pronouns
        for mi, m in enumerate(mlive):
            M = doc.mentions[mi]
            hg = mi2headg.get(mi); tk = gidx2tok.get(hg)
            t_sent = float(tk.sent if tk is not None else 0)
            role = TH.ROLE_OF_RANK.get(m.get("sent_role_rank", 99), "OTHER")
            gov = by_sent.get(tk.sent, {}).get(tk.head) if tk is not None else None
            gov_lemma = lemmatize_verb((getattr(gov, "lemma", None) or gov.form).lower()) if gov is not None and getattr(gov, "upos", "VERB") in ("VERB", "AUX", None) else None
            is_pron = m["is_pronoun"] or (M.mtype == "pronoun" and TH.is_third(M.text))
            if not is_pron:
                T.observe(m["head"], float(m["order"]), role, t_sent, m.get("gender") or m.get("name_gender"), m.get("number"), gidx2dep.get(hg, ""), payload=m)
                if gov_lemma:
                    ev_hist[m["head"]].append((gov_lemma, gidx2dep.get(hg, "") in AER.PATIENT_DEPS))
                continue
            ug, un = m.get("gender"), m.get("number")
            coarg = None
            if mi in und:
                cg = AER.coarg_head_gidx(doc.toks, und[mi])
                if cg is not None and cg in head_to_mi and not mlive[head_to_mi[cg]]["is_pronoun"]:
                    coarg = mlive[head_to_mi[cg]]["head"]
            dep = gidx2dep.get(hg, ""); a_role = AER.role_class(dep) if dep else "OBJ"
            reflexive = AER.is_reflexive(M.text)
            # ranked focus set with scores (replicate the organ's scoring to get the ORDER, not just the pick)
            compat = T.candidates(ug, un); ents = list(compat)
            scored = None
            if ents and not (reflexive and coarg in ents):
                legal = AER.legal_candidates(ents, coarg)
                legal = AER.foreground(legal, T.last_ref_sent, t_sent, T.window)
                sc = {}
                for k in legal:
                    hist = [(mm[0], mm[1]) for mm in compat[k]] + list(T.pron_hist.get(k, ()))
                    a = AER.actr_activation(hist, float(m["order"]), decay=T.decay, role_prominence=AER.ROLE_PROMINENCE)
                    s = a if a != float("-inf") else -1e9
                    last = max(compat[k], key=lambda mm: mm[0])
                    if AER.role_class(last[4]) == a_role: s += AER.GAMMA_G
                    if last[4] in AER.PATIENT_DEPS: s += AER.GAMMA_T
                    sc[k] = s
                scored = sc
            pick, n_c = T.resolve_pronoun(float(m["order"]), t_sent, gender=ug, number=un, a_role=a_role, role=role, coarg_key=coarg, reflexive=reflexive)
            if pick is not None and gov_lemma:
                ev_hist[pick].append((gov_lemma, dep in AER.PATIENT_DEPS))
            if mi in und and TH.is_third(M.text) and scored is not None:
                cm = [x for x in mlive if x["midx"] < mi and not x["is_pronoun"] and B1._gn_ok(m, x)]
                if len(cm) >= 2 and len(set(x["head"] for x in cm)) >= 2:
                    V = gov_lemma
                    # snapshot of histories BEFORE this event (exclude the just-added accrual)
                    hist_snap = {k: [e for e in ev_hist[k]][:-1] if k == pick else list(ev_hist[k]) for k in scored}
                    cluster_of = {k: (max(compat[k], key=lambda mm: mm[0])[6]["cluster"]) for k in scored}
                    items.append({"scores": scored, "gold": M.eid, "cluster_of": cluster_of, "V": V, "hist": hist_snap, "form": M.text.lower()})
    return items


def main(predicted_parse=False):
    items = collect(predicted_parse)
    n = len(items); rng = random.Random(SEED); rng2 = np.random.default_rng(SEED)
    base = np.array([int(it["cluster_of"][max(it["scores"], key=it["scores"].get)] == it["gold"]) for it in items])
    print(f"THIRD items={n} forward-half prior acc={base.mean():.4f}")
    cache = {}
    def rel(a, b):
        if a is None or b is None: return None
        key = (a, b) if a <= b else (b, a)
        if key not in cache:
            try: cache[key] = CR.relatedness(a, b)
            except Exception: cache[key] = None
        return cache[key]
    def s_exact(it, k): return float(any(v == it["V"] and pat for v, pat in it["hist"].get(k, [])))
    def s_sim(it, k):
        vals = [rel(it["V"], v) for v, _ in it["hist"].get(k, [])]; vals = [v for v in vals if v is not None]
        return max(vals) if vals else None
    def s_simrole(it, k):
        vals = [rel(it["V"], v) for v, pat in it["hist"].get(k, []) if pat]; vals = [v for v in vals if v is not None]
        return max(vals) if vals else None
    READS = [("exact same-predicate", s_exact), ("hub sim(V, past predicates)", s_sim), ("hub sim, patient-role only", s_simrole)]
    # coverage + wrong-set direction inside top-3
    for name, fn in READS:
        cov = gg = pg = 0
        for it in items:
            order = sorted(it["scores"], key=it["scores"].get, reverse=True)[:3]
            vals = {k: fn(it, k) for k in order}
            if sum(v is not None for v in vals.values()) >= 2: cov += 1
            pick = order[0]
            if it["cluster_of"][pick] != it["gold"]:
                golds = [k for k in order if it["cluster_of"][k] == it["gold"]]
                if golds and vals[pick] is not None:
                    g = max((vals[k] for k in golds if vals[k] is not None), default=None)
                    if g is not None:
                        if g > vals[pick] + 1e-9: gg += 1
                        elif vals[pick] > g + 1e-9: pg += 1
        print(f"  {name}: top-3 items with >=2 scored {cov}/{n}; WRONG set (gold in top-3): gold>pick {gg}, pick>gold {pg}")
    def run(fn, k, tau, gate, scramble=False):
        out = []
        for it in items:
            order = sorted(it["scores"], key=it["scores"].get, reverse=True)
            focus = order[:k]
            if len(order) < 2 or (gate is not None and it["scores"][order[0]] - it["scores"][order[1]] >= gate):
                pick = order[0]
            else:
                vals = [fn(it, h) for h in focus]
                if scramble: rng.shuffle(vals)
                present = [v for v in vals if v is not None]
                if len(present) >= 2 and (max(present) - min(present)) > 1e-9:
                    arr = np.array([v if v is not None else np.mean(present) for v in vals]); z = (arr - arr.mean()) / (arr.std() + 1e-9)
                else:
                    z = np.zeros(len(focus))
                tot = {h: it["scores"][h] + tau * z[i] for i, h in enumerate(focus)}
                pick = max(tot, key=tot.get)
            out.append(int(it["cluster_of"][pick] == it["gold"]))
        return np.array(out)
    def ci(v):
        d = v.astype(float) - base; boots = np.array([d[rng2.integers(0, n, n)].mean() for _ in range(2000)])
        lo, hi = np.percentile(boots, 2.5), np.percentile(boots, 97.5); return f"{v.mean():.4f}{'*' if lo > 0 else ('-' if hi < 0 else ' ')}[{lo:+.3f},{hi:+.3f}]"
    for name, fn in READS:
        print(f"\n{name}")
        for k in (2, 3):
            for gate in (None, 1.0, 0.5):
                row = [f"tau={tau}: {ci(run(fn, k, tau, gate))} (scr {run(fn, k, tau, gate, True).mean():.4f})" for tau in (0.5, 1.0, 2.0)]
                print(f"  top-{k} gate={gate}: " + " | ".join(row))


if __name__ == "__main__":
    main(predicted_parse="--predicted" in sys.argv)
