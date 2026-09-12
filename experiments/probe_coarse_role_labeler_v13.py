"""PROBE v13 (upstream pass, rung 5 first build): the Competition-Model COARSE ROLE LABELER (graded_role_assigner.coarse_roles)
vs the supervised dependency labeler, on (a) coarse-class label accuracy over GUM test nominal tokens and (b) the affected-
entity decision on the SAME 596 THIRD-person items (fixed gold targets). Variants:
  GOLD                 gold heads + gold labels
  SUP_labels           predicted POS -> predicted heads -> supervised labels        (deployment today)
  CM_labels            predicted POS -> predicted heads -> coarse_roles (competition) for nominals, supervised labels elsewhere
  CM_fb_labels         as CM_labels but the competition's OTHER ('dep') falls back to the supervised label
  CM_perc_labels       as CM_labels with validities learned on PERCEIVED cues (predicted POS/heads over UD-EWT train)
  CM_labels_goldheads  gold heads -> coarse_roles (isolates the labeler from head errors)
  SUP_labels_goldheads gold heads -> supervised labels
Paired CIs vs GOLD and vs SUP_labels.
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
import experiments.exp_affected_entity_token_history_gum_v1 as TH
import experiments.probe_parse_rung_loss_affected_entity_v11 as V11
import experiments.probe_labeler_confusion_gum_v12 as V12
from hdlab import graded_role_assigner as GRA

SEED = 20260912


_PERC = None


def _perceived_validities():
    global _PERC
    if _PERC is None:
        _PERC = GRA.load_coarse_validities(os.path.join(REPO, "data", "frontend_assets", "coarse_role_validities_ud_ewt_perceived.json"))
    return _PERC


def overlay_cm(doc, *, heads_src="pred", fallback=False, perceived=False):
    """Predicted POS, heads from parser (or gold), labels: competition for nominals, supervised elsewhere."""
    tg, pp, lb = V11._fe()
    by_sent = defaultdict(list)
    for tok in doc.toks:
        by_sent[tok.sent].append(tok)
    for sent, toks in by_sent.items():
        toks = sorted(toks, key=lambda x: x.idx)
        forms = [x.form for x in toks]
        pos = list(tg.tag(forms))
        gold_heads = {j + 1: x.head for j, x in enumerate(toks)}
        heads = dict(pp.parse(forms, pos).heads) if heads_src == "pred" else gold_heads
        sup = dict(lb.label(forms, pos, heads, competition_roles=False))
        cm = GRA.coarse_roles(forms, pos, heads, validities=_perceived_validities() if perceived else None)
        for j, x in enumerate(toks):
            i1 = j + 1
            x.head = heads.get(i1, x.head)
            c = cm.get(i1)
            if fallback and c == "dep":
                c = None   # the competition abstains on non-argument relations; keep the supervised label there
            x.deprel = c or sup.get(i1, x.deprel) or x.deprel


def overlay_live(doc):
    """The LIVE label path as deployed: predicted POS -> predicted heads -> ArcLabeler.label() with its module defaults
    (voice correction + COMPETITION_ROLES overlay: argument roles from the competition, fine relations kept)."""
    tg, pp, lb = V11._fe()
    by_sent = defaultdict(list)
    for tok in doc.toks:
        by_sent[tok.sent].append(tok)
    for sent, toks in by_sent.items():
        toks = sorted(toks, key=lambda x: x.idx)
        forms = [x.form for x in toks]
        pos = list(tg.tag(forms))
        heads = dict(pp.parse(forms, pos).heads)
        lab = dict(lb.label(forms, pos, heads))
        for j, x in enumerate(toks):
            x.head = heads.get(j + 1, x.head)
            x.deprel = lab.get(j + 1, x.deprel)


def label_accuracy(docs_gold, docs_var):
    tot = Counter(); hit = Counter()
    for dg, dv in zip(docs_gold, docs_var):
        vt = {t.gidx: t for t in dv.toks}
        for g in dg.toks:
            if getattr(g, "upos", "") not in ("NOUN", "PROPN", "PRON"):
                continue
            p = vt.get(g.gidx)
            if p is None:
                continue
            cg, cp = V12.coarse(g.deprel, None, g), V12.coarse(p.deprel, None, p)
            tot[cg] += 1; hit[cg] += int(cg == cp)
    return {c: (round(hit[c] / tot[c], 3), tot[c]) for c in ("SUBJ", "OBJ", "PASS_SUBJ", "BY_AGENT", "OBL", "OTHER") if tot[c]}


def main():
    rng = np.random.default_rng(SEED)
    gold = TH.load(False)
    targets = V11.gold_targets(gold)
    variants = {
        "GOLD": lambda d: None,
        "SUP_labels": lambda d: V11.overlay(d, pos_src="pred", heads_src="pred", labels_src="pred"),
        "CM_labels": lambda d: overlay_cm(d, heads_src="pred"),
        "CM_fb_labels": lambda d: overlay_cm(d, heads_src="pred", fallback=True),
        "CM_perc_labels": lambda d: overlay_cm(d, heads_src="pred", perceived=True),
        "LIVE_labels": lambda d: overlay_live(d),
        "SUP_labels_goldheads": lambda d: V11.overlay(d, pos_src="pred", heads_src="gold", labels_src="pred"),
        "CM_labels_goldheads": lambda d: overlay_cm(d, heads_src="gold"),
    }
    res = {}; label_acc = {}
    for name, fn in variants.items():
        data = TH.load(False)
        # the target set must be keyed by THESE doc objects
        tmap = {}
        for (dg, _), (dv, _) in zip(gold, data):
            tmap[id(dv)] = targets[id(dg)]
        for doc, _ in data:
            fn(doc)
        r = TH.run_arm(data, accrue=True, window=TH.WINDOW, principle_a=True, targets=tmap)
        res[name] = np.array([h for h, _ in r])
        if name != "GOLD":
            label_acc[name] = label_accuracy([d for d, _ in gold], [d for d, _ in data])
        print(f"{name:22s} n={len(r)} decision acc={res[name].mean():.4f}  coarse-label acc={label_acc.get(name, 'gold')}")
    n = len(res["GOLD"])
    def ci(a, b):
        d = res[a].astype(float) - res[b]; boots = np.array([d[rng.integers(0, n, n)].mean() for _ in range(2000)])
        return f"{d.mean():+.4f} CI95 [{np.percentile(boots,2.5):+.4f}, {np.percentile(boots,97.5):+.4f}]"
    print("\npaired deltas on the decision:")
    print("  CM_labels - SUP_labels (deployment, predicted heads):", ci("CM_labels", "SUP_labels"))
    print("  CM_fb_labels - SUP_labels (OTHER -> supervised)      :", ci("CM_fb_labels", "SUP_labels"))
    print("  CM_perc_labels - SUP_labels (validities on PERCEIVED cues):", ci("CM_perc_labels", "SUP_labels"))
    print("  CM_perc_labels - CM_labels                          :", ci("CM_perc_labels", "CM_labels"))
    print("  LIVE_labels - SUP_labels (the deployed overlay)       :", ci("LIVE_labels", "SUP_labels"))
    print("  LIVE_labels - CM_labels                             :", ci("LIVE_labels", "CM_labels"))
    print("  CM_labels_goldheads - SUP_labels_goldheads        :", ci("CM_labels_goldheads", "SUP_labels_goldheads"))
    print("  CM_labels - GOLD                                  :", ci("CM_labels", "GOLD"))
    print("  SUP_labels - GOLD                                 :", ci("SUP_labels", "GOLD"))


if __name__ == "__main__":
    main()
