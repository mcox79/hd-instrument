"""PROBE v10 (strategy, pri-1 arm 2): OPERATING POINT of the pinned ACT-R prior for OBJECT pronouns, on the landed forward
half (THIRD-person GUM undergoers). The computation is fixed (base-level activation over the token's reference history x
Principle A/B x parallelism); the PARAMETERS we do not share with the brain's lab constants are swept (phase diagram):
  role prominence w(SUBJECT, OBJECT, OTHER)  -- the Centering ordering is PINNED, the magnitudes are not;
  history depth m (only the last m references enter the sum) -- a limited-capacity focus;
  decay d; parallelism gammas.
Paired CIs vs the landed operating point; gold roles and predicted parse.
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
import experiments.exp_affected_entity_token_history_gum_v1 as TH
import hdlab.affected_entity_resolver as AER
from hdlab.salience_binder import actr_activation

SEED = 20260912


def collect(predicted_parse=False):
    """Items with the full candidate state at the target (histories incl. accrued pronouns, last dep, a_role, coarg) so any
    operating point can be re-scored offline. The ACCRUAL itself is run at the landed operating point (incremental)."""
    data = TH.load(predicted_parse)
    items = []
    for doc, mlive in data:
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        mi2headg = {i: doc.mentions[i].head_g for i in range(len(doc.mentions))}
        gidx2dep = {t.gidx: t.deprel for t in doc.toks}
        gidx2tok = {t.gidx: t for t in doc.toks}
        und = {}
        for t in doc.toks:
            if t.deprel in B1.UND_DEPRELS and t.gidx in head_to_mi and doc.mentions[head_to_mi[t.gidx]].mtype == "pronoun":
                und[head_to_mi[t.gidx]] = t
        T = AER.EntityTokens()
        for mi, m in enumerate(mlive):
            M = doc.mentions[mi]
            hg = mi2headg.get(mi); tk = gidx2tok.get(hg)
            t_sent = float(tk.sent if tk is not None else 0)
            role = TH.ROLE_OF_RANK.get(m.get("sent_role_rank", 99), "OTHER")
            is_pron = m["is_pronoun"] or (M.mtype == "pronoun" and TH.is_third(M.text))
            if not is_pron:
                T.observe(m["head"], float(m["order"]), role, t_sent, m.get("gender") or m.get("name_gender"), m.get("number"), gidx2dep.get(hg, ""), payload=m)
                continue
            ug, un = m.get("gender"), m.get("number")
            coarg = None
            if mi in und:
                cg = AER.coarg_head_gidx(doc.toks, und[mi])
                if cg is not None and cg in head_to_mi and not mlive[head_to_mi[cg]]["is_pronoun"]:
                    coarg = mlive[head_to_mi[cg]]["head"]
            dep = gidx2dep.get(hg, ""); a_role = AER.role_class(dep) if dep else "OBJ"
            reflexive = AER.is_reflexive(M.text)
            if mi in und and TH.is_third(M.text) and not reflexive:
                compat = T.candidates(ug, un); ents = list(compat)
                cm = [x for x in mlive if x["midx"] < mi and not x["is_pronoun"] and B1._gn_ok(m, x)]
                if ents and len(cm) >= 2 and len(set(x["head"] for x in cm)) >= 2:
                    legal = AER.legal_candidates(ents, coarg)
                    legal = AER.foreground(legal, T.last_ref_sent, t_sent, T.window)
                    cand = {}
                    for k in legal:
                        hist = [(mm[0], mm[1]) for mm in compat[k]] + list(T.pron_hist.get(k, ()))
                        last = max(compat[k], key=lambda mm: mm[0])
                        cand[k] = {"hist": sorted(hist), "last_dep": last[4], "cluster": last[6]["cluster"]}
                    items.append({"cand": cand, "now": float(m["order"]), "a_role": a_role, "gold": M.eid, "form": M.text.lower()})
            T.resolve_pronoun(float(m["order"]), t_sent, gender=ug, number=un, a_role=a_role, role=role, coarg_key=coarg, reflexive=reflexive)
    return items


def score(items, rp, decay=AER.DEFAULT_DECAY, depth=None, gamma_g=AER.GAMMA_G, gamma_t=AER.GAMMA_T):
    out = []
    for it in items:
        best, bs = None, -1e18
        for k, c in it["cand"].items():
            hist = c["hist"][-depth:] if depth else c["hist"]
            a = actr_activation(hist, it["now"], decay=decay, role_prominence=rp)
            s = a if a != float("-inf") else -1e9
            if AER.role_class(c["last_dep"]) == it["a_role"]: s += gamma_g
            if c["last_dep"] in AER.PATIENT_DEPS: s += gamma_t
            if s > bs: bs, best = s, k
        out.append(int(it["cand"][best]["cluster"] == it["gold"]))
    return np.array(out)


def main(predicted_parse=False):
    items = collect(predicted_parse)
    n = len(items); rng = np.random.default_rng(SEED)
    RP0 = dict(AER.ROLE_PROMINENCE)
    base = score(items, RP0)
    print(f"THIRD non-reflexive items={n} landed operating point acc={base.mean():.4f} (predicted_parse={predicted_parse})")
    def ci(v):
        d = v.astype(float) - base; boots = np.array([d[rng.integers(0, n, n)].mean() for _ in range(2000)])
        lo, hi = np.percentile(boots, 2.5), np.percentile(boots, 97.5); return f"{v.mean():.4f}{'*' if lo > 0 else ('-' if hi < 0 else ' ')}[{lo:+.3f},{hi:+.3f}]"
    print("\nrole prominence (SUBJECT, OBJECT, OTHER; POSSESSIVE=2.5 kept):")
    for s_, o_, x_ in [(4, 2, 1), (2, 2, 1), (1, 1, 1), (2, 2, 2), (1, 2, 1), (1, 2, 2), (4, 4, 2), (2, 4, 2), (1, 1, 2)]:
        rp = dict(RP0); rp.update({"SUBJECT": float(s_), "OBJECT": float(o_), "OTHER": float(x_)})
        print(f"  w=({s_},{o_},{x_}): {ci(score(items, rp))}")
    print("\nhistory depth m (last m references enter the base-level sum):")
    for m in (1, 2, 3, 5, None):
        print(f"  m={m}: {ci(score(items, RP0, depth=m))}")
    print("\ndecay d:")
    for d in (1.0, 2.0, 3.0, 5.0):
        print(f"  d={d}: {ci(score(items, RP0, decay=d))}")
    print("\nparallelism gammas (g, t):")
    for g, t in [(1, 1), (2, 1), (1, 2), (2, 2), (0.5, 0.5), (0, 0)]:
        print(f"  gammas=({g},{t}): {ci(score(items, RP0, gamma_g=g, gamma_t=t))}")
    print("\ncombos:")
    for s_, o_, x_, m, d in [(1, 1, 1, None, 2.0), (1, 1, 1, 2, 2.0), (2, 2, 1, 3, 2.0), (1, 2, 1, None, 3.0), (1, 1, 1, None, 3.0), (2, 2, 2, None, 3.0)]:
        rp = dict(RP0); rp.update({"SUBJECT": float(s_), "OBJECT": float(o_), "OTHER": float(x_)})
        print(f"  w=({s_},{o_},{x_}) m={m} d={d}: {ci(score(items, rp, decay=d, depth=m))}")


if __name__ == "__main__":
    main(predicted_parse="--predicted" in sys.argv)
