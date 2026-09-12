"""PROBE v12 (upstream pass, rung 5): WHERE does the supervised dependency labeler lose the coarse roles this decision needs?
Confusion of coarse relation classes (SUBJ / OBJ / PASS_SUBJ / BY_AGENT / OBL / OTHER) gold vs predicted on the GUM test docs,
restricted to nominal/pronoun tokens; plus the PINNED categorical cue the labeler cannot see as a rule: object-case pronouns
(him/her/them/me/us/it as object) labelled as subjects, and subject-case pronouns (he/she/they/I/we) labelled as objects.
Numbers steer the Competition-Model coarse role labeler (cue validities: word order, case, voice, agreement, animacy).
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
import experiments.exp_affected_entity_binding_parallelism_gum_v1 as B4

OBJ_CASE = {"him", "her", "them", "me", "us", "whom"}
SUBJ_CASE = {"he", "she", "they", "i", "we", "who"}


def coarse(dep: str, toks_by_sent, tok) -> str:
    d = (dep or "").split(":")[0]; full = dep or ""
    if full.startswith("nsubj:pass") or full == "nsubjpass":
        return "PASS_SUBJ"
    if d in ("nsubj", "csubj"):
        return "SUBJ"
    if d in ("obj", "dobj", "iobj"):
        return "OBJ"
    if full == "obl:agent":
        return "BY_AGENT"
    if full == "nmod:poss":
        return "OTHER"   # a possessive is a determiner-like modifier, not an oblique argument
    if d in ("obl", "nmod"):
        return "OBL"
    return "OTHER"


def main():
    docs_gold = B1._load_test(None)
    docs_pred = B1._load_test(None)
    for d in docs_pred:
        B4._overlay_predicted(d)
    conf = Counter(); n = 0
    case_viol = Counter(); case_tot = Counter()
    per_class_total = Counter(); per_class_hit = Counter()
    for dg, dp in zip(docs_gold, docs_pred):
        gt = {t.gidx: t for t in dg.toks}; pt = {t.gidx: t for t in dp.toks}
        for g in dg.toks:
            if getattr(g, "upos", "") not in ("NOUN", "PROPN", "PRON"):
                continue
            p = pt.get(g.gidx)
            if p is None:
                continue
            cg, cp = coarse(g.deprel, None, g), coarse(p.deprel, None, p)
            conf[(cg, cp)] += 1; n += 1
            per_class_total[cg] += 1; per_class_hit[cg] += int(cg == cp)
            w = g.form.lower()
            if w in OBJ_CASE:
                case_tot["obj_case"] += 1
                if cp in ("SUBJ",): case_viol["obj_case->SUBJ"] += 1
            if w in SUBJ_CASE:
                case_tot["subj_case"] += 1
                if cp in ("OBJ", "OBL"): case_viol["subj_case->OBJ/OBL"] += 1
    print(f"nominal/pronoun tokens n={n}; coarse label accuracy per gold class:")
    for c in ("SUBJ", "OBJ", "PASS_SUBJ", "BY_AGENT", "OBL", "OTHER"):
        t = per_class_total[c]
        if t: print(f"  {c:9s} n={t:5d} acc={per_class_hit[c]/t:.3f}")
    print("top confusions (gold -> pred):")
    for (cg, cp), k in sorted(((k, v) for k, v in conf.items() if k[0] != k[1]), key=lambda x: -x[1])[:12]:
        print(f"  {cg:9s} -> {cp:9s} {k}")
    print("pronoun CASE violations by the supervised labeler (a categorical PINNED cue):")
    for k, v in case_viol.items():
        base = case_tot["obj_case"] if k.startswith("obj") else case_tot["subj_case"]
        print(f"  {k}: {v}/{base} = {v/max(1,base):.3f}")
    # how often is the gold undergoer pronoun mislabelled (so it stops being a target / changes role)?
    und_tot = und_miss = 0
    for dg, dp in zip(docs_gold, docs_pred):
        pt = {t.gidx: t for t in dp.toks}
        for g in dg.toks:
            if g.deprel in B1.UND_DEPRELS and getattr(g, "upos", "") == "PRON":
                und_tot += 1
                if pt[g.gidx].deprel not in B1.UND_DEPRELS: und_miss += 1
    print(f"gold undergoer PRONOUNS mislabelled out of the undergoer set: {und_miss}/{und_tot} = {und_miss/max(1,und_tot):.3f}")


if __name__ == "__main__":
    main()
