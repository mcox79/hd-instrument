"""PROBE v6 (strategy, pri-1): THIRD-person only. (a) error anatomy; (b) the salience prior's OPERATING POINT -- the
ACT-R clock (mention order vs token position vs sentence index) and decay d are parameters we do not share with the
brain's constraints, so SWEEP them (phase diagram); (c) FOREGROUND gating by sentence window (Glenberg availability /
event-model foreground: entities from the current event are accessible first; fall back to all).
Uses the A5-heads arm (incumbent) so deltas are attributable to the clock/gate alone; paired CIs vs the incumbent.
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
import experiments.exp_affected_entity_binding_parallelism_gum_v1 as B4
import hdlab.affected_entity_resolver as AER
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
from experiments.probe_entity_state_residual_gum_v5 import pclass

SEED = 20260912


def build_items(predicted_parse=False):
    import experiments.exp_hybrid_unified_incumbent_coref_gum_v1 as HYB
    docs = B1._load_test(None)
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
        for t in doc.toks:
            if t.deprel not in B1.UND_DEPRELS or t.gidx not in head_to_mi:
                continue
            u_mi = head_to_mi[t.gidx]; u = mlive[u_mi]; M = doc.mentions[u_mi]
            if M.mtype != "pronoun" or pclass(M.text) != "THIRD":
                continue
            gold = M.eid
            cands = [x for x in mlive if x["midx"] < u_mi and not x["is_pronoun"] and B1._gn_ok(u, x)]
            if len(cands) < 2:
                continue
            cg = AER.coarg_head_gidx(doc.toks, t)
            coarg = mlive[head_to_mi[cg]]["head"] if (cg is not None and cg in head_to_mi) else None
            ents = defaultdict(list); ent_last = {}
            for x in cands:
                h = x["head"]
                hg = mi2headg.get(x["midx"]); tk = gidx2tok.get(hg)
                ents[h].append({"order": float(x["order"]), "tokpos": float(hg if hg is not None else x["order"]),
                                "sent": float(tk.sent if tk is not None else 0), "role": B1._role(x.get("sent_role_rank", 2))})
                if h not in ent_last or x["order"] >= ent_last[h]["order"]:
                    ent_last[h] = x
            if len(ents) < 2:
                continue
            role_of = {h: AER.role_class(gidx2dep.get(mi2headg.get(ent_last[h]["midx"]), "")) for h in ents}
            patient_of = {h: (gidx2dep.get(mi2headg.get(ent_last[h]["midx"]), "") in AER.PATIENT_DEPS) for h in ents}
            last_sent = {h: max(e["sent"] for e in ents[h]) for h in ents}
            items.append({"form": M.text.lower(), "gold": gold, "ents": dict(ents), "legal": AER.legal_candidates(list(ents), coarg),
                          "role_of": role_of, "patient_of": patient_of, "a_role": AER.role_class(t.deprel),
                          "now": {"order": float(u["order"]), "tokpos": float(t.gidx), "sent": float(t.sent)},
                          "cluster_of": {h: ent_last[h]["cluster"] for h in ents}, "last_sent": last_sent,
                          "gold_in_legal": any(ent_last[h]["cluster"] == gold for h in AER.legal_candidates(list(ents), coarg))})
    return items


def resolve(it, clock="order", decay=DEFAULT_DECAY, window=None, rp=ROLE_PROMINENCE):
    now = it["now"][clock]
    cand = it["legal"]
    if window is not None:
        inwin = [h for h in cand if it["now"]["sent"] - it["last_sent"][h] <= window]
        if inwin:
            cand = inwin
    sc = {}
    for h in cand:
        hist = [(e[clock], e["role"]) for e in it["ents"][h]]
        s = actr_activation(hist, now, decay, rp)
        if s == float("-inf"):
            s = -1e9
        if it["role_of"][h] == it["a_role"]: s += AER.GAMMA_G
        if it["patient_of"].get(h): s += AER.GAMMA_T
        sc[h] = s
    order = sorted(sc, key=sc.get, reverse=True)
    return order


def main(predicted_parse=False):
    items = build_items(predicted_parse)
    n = len(items)
    rng = np.random.default_rng(SEED)
    base = np.array([int(it["cluster_of"][resolve(it)[0]] == it["gold"]) for it in items])
    print(f"THIRD items={n}  A5 incumbent={base.mean():.4f}  gold_in_legal={np.mean([it['gold_in_legal'] for it in items]):.4f} (ceiling)")
    print("  forms:", Counter(it["form"] for it in items).most_common(8))
    for f, c in Counter(it["form"] for it in items).most_common(6):
        sub = [i for i, it in enumerate(items) if it["form"] == f]
        print(f"    {f}: n={len(sub)} acc={base[sub].mean():.3f} ceiling={np.mean([items[i]['gold_in_legal'] for i in sub]):.3f}")
    # distance of gold's last mention (sentences)
    def gdist(it):
        gs = [it["last_sent"][h] for h in it["ents"] if it["cluster_of"][h] == it["gold"]]
        return (it["now"]["sent"] - max(gs)) if gs else None
    dd = [gdist(it) for it in items]
    for lab, sel in [("same", lambda d: d == 0), ("prev", lambda d: d == 1), ("2-3", lambda d: d in (2, 3)), (">=4", lambda d: d is not None and d >= 4), ("absent", lambda d: d is None)]:
        idx = [i for i, d in enumerate(dd) if sel(d)]
        if idx: print(f"  gold distance {lab}: n={len(idx)} acc={base[idx].mean():.3f}")

    def ci(vec):
        d = vec.astype(float) - base
        boots = np.array([d[rng.integers(0, n, n)].mean() for _ in range(2000)])
        return d.mean(), np.percentile(boots, 2.5), np.percentile(boots, 97.5)

    print("\nOPERATING POINT sweep (clock x decay), A5 structure unchanged:")
    for clock in ("order", "tokpos", "sent"):
        row = []
        for decay in (0.3, 0.5, 0.7, 1.0, 1.5):
            v = np.array([int(it["cluster_of"][resolve(it, clock, decay)[0]] == it["gold"]) for it in items])
            dm, lo, hi = ci(v); flag = "*" if lo > 0 else ("-" if hi < 0 else " ")
            row.append(f"d={decay}: {v.mean():.4f}{flag}[{lo:+.3f},{hi:+.3f}]")
        print(f"  clock={clock:6s} " + " | ".join(row))
    print("\nFOREGROUND window (sentences; candidates in-window first, else all):")
    for clock in ("order", "sent"):
        row = []
        for w in (0, 1, 2, 3, 5):
            v = np.array([int(it["cluster_of"][resolve(it, clock, DEFAULT_DECAY, w)[0]] == it["gold"]) for it in items])
            dm, lo, hi = ci(v); flag = "*" if lo > 0 else ("-" if hi < 0 else " ")
            row.append(f"w={w}: {v.mean():.4f}{flag}[{lo:+.3f},{hi:+.3f}]")
        print(f"  clock={clock:6s} " + " | ".join(row))
    print("\nin-focus ceiling (incumbent ordering) top-1..4:",
          [round(float(np.mean([int(any(it["cluster_of"][h] == it["gold"] for h in resolve(it)[:k])) for it in items])), 4) for k in (1, 2, 3, 4)])


if __name__ == "__main__":
    main(predicted_parse="--predicted" in sys.argv)
