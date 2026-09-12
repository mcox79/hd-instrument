"""PROBE v9 (strategy, pri-1 arm 2): the STRUCTURE of the in-focus residual on top of the landed forward half, THIRD-person.
(a) anatomy: for wrong items with gold inside the top-3, compare gold vs pick on discourse-structural features (last-mention
sentence distance; role of last mention; previous-sentence SUBJECT = Centering Cb proxy; current-sentence subject; mention count;
same-sentence distractor); (b) a CENTERING Cb-CONTINUITY term [PINNED: Grosz-Joshi-Weinstein 1995; Brennan-Friedman-Pollard
1987 ranking; the backward-looking center = the highest-ranked forward-looking center of the previous utterance realised in the
current one] as a swept likelihood bonus exp(kappa * 1[X was the previous utterance's highest-ranked Cf]); (c) a same-clause
non-co-argument penalty probe. Scramble controls; paired CIs vs the forward-half prior.
"""
from __future__ import annotations

import os
import random
import sys
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
import experiments.exp_affected_entity_token_history_gum_v1 as TH
import hdlab.affected_entity_resolver as AER

SEED = 20260912


def collect(predicted_parse=False):
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
        # per-sentence Cf ranking by role rank (subject first) of entity keys realised in that sentence (incl. resolved pronouns)
        sent_cf = defaultdict(list)          # sent -> [(rank, key)]
        for mi, m in enumerate(mlive):
            M = doc.mentions[mi]
            hg = mi2headg.get(mi); tk = gidx2tok.get(hg)
            t_sent = float(tk.sent if tk is not None else 0)
            rank = m.get("sent_role_rank", 99)
            role = TH.ROLE_OF_RANK.get(rank, "OTHER")
            is_pron = m["is_pronoun"] or (M.mtype == "pronoun" and TH.is_third(M.text))
            if not is_pron:
                T.observe(m["head"], float(m["order"]), role, t_sent, m.get("gender") or m.get("name_gender"), m.get("number"), gidx2dep.get(hg, ""), payload=m)
                sent_cf[int(t_sent)].append((rank, m["head"]))
                continue
            ug, un = m.get("gender"), m.get("number")
            coarg = None
            if mi in und:
                cg = AER.coarg_head_gidx(doc.toks, und[mi])
                if cg is not None and cg in head_to_mi and not mlive[head_to_mi[cg]]["is_pronoun"]:
                    coarg = mlive[head_to_mi[cg]]["head"]
            dep = gidx2dep.get(hg, ""); a_role = AER.role_class(dep) if dep else "OBJ"
            reflexive = AER.is_reflexive(M.text)
            compat = T.candidates(ug, un); ents = list(compat)
            scored = None; feats = None
            if ents and not (reflexive and coarg in ents):
                legal = AER.legal_candidates(ents, coarg)
                legal = AER.foreground(legal, T.last_ref_sent, t_sent, T.window)
                sc = {}; feats = {}
                prev_cf = sorted(sent_cf.get(int(t_sent) - 1, []))
                prev_top = prev_cf[0][1] if prev_cf else None
                cur_subj = {k for r, k in sent_cf.get(int(t_sent), []) if r == 0}
                for k in legal:
                    hist = [(mm[0], mm[1]) for mm in compat[k]] + list(T.pron_hist.get(k, ()))
                    a = AER.actr_activation(hist, float(m["order"]), decay=T.decay, role_prominence=AER.ROLE_PROMINENCE)
                    s = a if a != float("-inf") else -1e9
                    last = max(compat[k], key=lambda mm: mm[0])
                    if AER.role_class(last[4]) == a_role: s += AER.GAMMA_G
                    if last[4] in AER.PATIENT_DEPS: s += AER.GAMMA_T
                    sc[k] = s
                    feats[k] = {"dist": t_sent - T.last_ref_sent.get(k, -1e9), "last_role": AER.role_class(last[4]),
                                "prev_top_cf": k == prev_top, "prev_in_cf": any(kk == k for _, kk in prev_cf),
                                "cur_subj": k in cur_subj, "n_ment": len(compat[k]) + len(T.pron_hist.get(k, ())),
                                "same_sent": (t_sent - T.last_ref_sent.get(k, -1e9)) == 0}
                scored = sc
            pick, n_c = T.resolve_pronoun(float(m["order"]), t_sent, gender=ug, number=un, a_role=a_role, role=role, coarg_key=coarg, reflexive=reflexive)
            if pick is not None:
                sent_cf[int(t_sent)].append((rank, pick))
            if mi in und and TH.is_third(M.text) and scored is not None:
                cm = [x for x in mlive if x["midx"] < mi and not x["is_pronoun"] and B1._gn_ok(m, x)]
                if len(cm) >= 2 and len(set(x["head"] for x in cm)) >= 2:
                    cluster_of = {k: (max(compat[k], key=lambda mm: mm[0])[6]["cluster"]) for k in scored}
                    items.append({"scores": scored, "gold": M.eid, "cluster_of": cluster_of, "feats": feats, "form": M.text.lower()})
    return items


def main(predicted_parse=False):
    items = collect(predicted_parse)
    n = len(items); rng = random.Random(SEED); rng2 = np.random.default_rng(SEED)
    def top(it): return sorted(it["scores"], key=it["scores"].get, reverse=True)
    base = np.array([int(it["cluster_of"][top(it)[0]] == it["gold"]) for it in items])
    print(f"THIRD items={n} forward-half prior acc={base.mean():.4f}")
    # (a) anatomy inside top-3
    feat_names = ["dist", "last_role", "prev_top_cf", "prev_in_cf", "cur_subj", "n_ment", "same_sent"]
    gold_c = defaultdict(Counter); pick_c = defaultdict(Counter); m_ = 0
    for it in items:
        order = top(it); pick = order[0]
        if it["cluster_of"][pick] == it["gold"]: continue
        golds = [k for k in order[:3] if it["cluster_of"][k] == it["gold"]]
        if not golds: continue
        m_ += 1; g = golds[0]
        for f in feat_names:
            gv, pv = it["feats"][g][f], it["feats"][pick][f]
            if f == "dist": gv, pv = min(int(gv), 5), min(int(pv), 5)
            if f == "n_ment": gv, pv = min(gv, 6), min(pv, 6)
            gold_c[f][gv] += 1; pick_c[f][pv] += 1
    print(f"\nWRONG with gold in top-3: {m_} items (of {int((1-base.mean())*n)} wrong)")
    for f in feat_names:
        print(f"  {f:12s} gold {dict(sorted(gold_c[f].items(), key=lambda x: str(x[0])))} | pick {dict(sorted(pick_c[f].items(), key=lambda x: str(x[0])))}")
    # (b) Cb-continuity bonus and (c) current-sentence-subject penalty, swept, with scramble
    def run(kind, kappa, k=None, scramble=False):
        out = []
        for it in items:
            order = top(it); focus = order[:k] if k else order
            vals = {h: it["feats"][h][kind] for h in focus}
            if scramble:
                vs = list(vals.values()); rng.shuffle(vs); vals = dict(zip(focus, vs))
            sign = -1.0 if kind == "cur_subj" else 1.0
            tot = {h: it["scores"][h] + sign * kappa * float(vals[h]) for h in focus}
            pick = max(tot, key=tot.get); out.append(int(it["cluster_of"][pick] == it["gold"]))
        return np.array(out)
    def ci(v):
        d = v.astype(float) - base; boots = np.array([d[rng2.integers(0, n, n)].mean() for _ in range(2000)])
        lo, hi = np.percentile(boots, 2.5), np.percentile(boots, 97.5); return f"{v.mean():.4f}{'*' if lo > 0 else ('-' if hi < 0 else ' ')}[{lo:+.3f},{hi:+.3f}]"
    for kind in ("prev_top_cf", "prev_in_cf", "cur_subj", "same_sent"):
        row = [f"kappa={kp}: {ci(run(kind, kp))} (scr {run(kind, kp, scramble=True).mean():.4f})" for kp in (0.5, 1.0, 2.0, 4.0)]
        print(f"\n{kind:12s} all candidates: " + " | ".join(row))
        row = [f"kappa={kp}: {ci(run(kind, kp, k=3))}" for kp in (0.5, 1.0, 2.0, 4.0)]
        print(f"{'':12s} top-3 only:     " + " | ".join(row))


if __name__ == "__main__":
    main(predicted_parse="--predicted" in sys.argv)
