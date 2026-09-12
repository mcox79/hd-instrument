"""PROBE v14 (upstream pass, rung 5): WHY does the live overlay (competition argument roles + perceptron FINE relations kept)
score 0.4765 on the 596-item decision when the pure competition labels (every competition-OTHER nominal -> 'dep') score 0.4933
(-0.0168 CI-sep)? Ablation: start from the LIVE overlay and wipe ONE retained fine-relation class to 'dep' at a time; the class
whose wipe recovers the pure-CM number is the relation the decision (mention source / salience roles) mis-consumes.
Also counts which perceptron labels are retained where the competition says OTHER.
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_affected_entity_token_history_gum_v1 as TH
import experiments.probe_parse_rung_loss_affected_entity_v11 as V11
from hdlab import graded_role_assigner as GRA
from hdlab import arc_labeler as AL

SEED = 20260912
RETAINED = Counter()


def overlay(doc, *, wipe=frozenset(), pure=False):
    tg, pp, lb = V11._fe()
    by_sent = defaultdict(list)
    for tok in doc.toks:
        by_sent[tok.sent].append(tok)
    for sent, toks in by_sent.items():
        toks = sorted(toks, key=lambda x: x.idx)
        forms = [x.form for x in toks]
        pos = list(tg.tag(forms))
        heads = dict(pp.parse(forms, pos).heads)
        sup = dict(lb.label(forms, pos, heads, competition_roles=False))
        cm = GRA.coarse_roles(forms, pos, heads)
        for j, x in enumerate(toks):
            i1 = j + 1
            x.head = heads.get(i1, x.head)
            s = sup.get(i1, x.deprel)
            c = cm.get(i1)
            if c is None:
                x.deprel = s
            elif c in AL._ARG_ROLES:
                x.deprel = c
            elif pure or s in AL._ARG_ROLES or s == "iobj":
                x.deprel = "dep"
            else:
                base = (s or "").split(":")[0]
                RETAINED[s] += 1
                x.deprel = "dep" if (base in wipe or s in wipe) else s


def main():
    rng = np.random.default_rng(SEED)
    gold = TH.load(False)
    targets = V11.gold_targets(gold)
    variants = {
        "LIVE": dict(),
        "PURE": dict(pure=True),
        "LIVE-nmod": dict(wipe=frozenset({"nmod"})),
        "LIVE-compound_flat": dict(wipe=frozenset({"compound", "flat", "fixed", "goeswith"})),
        "LIVE-conj": dict(wipe=frozenset({"conj"})),
        "LIVE-appos": dict(wipe=frozenset({"appos"})),
        "LIVE-modifiers": dict(wipe=frozenset({"amod", "nummod", "det", "advmod", "acl", "advcl", "xcomp", "ccomp"})),
        "LIVE-other": dict(wipe=frozenset({"root", "parataxis", "vocative", "dislocated", "list", "discourse", "orphan", "reparandum"})),
    }
    res = {}
    for name, kw in variants.items():
        RETAINED.clear()
        data = TH.load(False)
        tmap = {id(dv): targets[id(dg)] for (dg, _), (dv, _) in zip(gold, data)}
        for doc, _ in data:
            overlay(doc, **kw)
        r = TH.run_arm(data, accrue=True, window=TH.WINDOW, principle_a=True, targets=tmap)
        res[name] = np.array([h for h, _ in r])
        print(f"{name:20s} n={len(r)} decision acc={res[name].mean():.4f}")
        if name == "LIVE":
            print("  perceptron labels retained where the competition says OTHER:", RETAINED.most_common(14))
    n = len(res["LIVE"])
    def ci(a, b):
        d = res[a].astype(float) - res[b]; boots = np.array([d[rng.integers(0, n, n)].mean() for _ in range(2000)])
        return f"{d.mean():+.4f} CI95 [{np.percentile(boots,2.5):+.4f}, {np.percentile(boots,97.5):+.4f}]"
    print("\npaired deltas vs LIVE:")
    for name in variants:
        if name != "LIVE":
            print(f"  {name:20s} - LIVE: {ci(name, 'LIVE')}")


if __name__ == "__main__":
    main()
