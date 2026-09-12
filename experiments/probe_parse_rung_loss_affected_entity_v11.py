"""PROBE v11 (upstream math-BF pass, rung 5): decompose the PARSE SPINE's loss on the affected-entity decision.
Fixed target set = the GOLD undergoer pronouns (THIRD-person), so every variant scores the SAME items; only the information
fed to the forward-half resolver changes:
  GOLD          gold UPOS / heads / deprels
  PRED_ALL      predicted POS -> predicted heads -> predicted labels           (deployment)
  PRED_goldPOS  gold UPOS fed to the parser + labeler (isolates the tagger)
  HEADS_pred    predicted heads (from predicted POS), GOLD deprels             (isolates head attachment)
  LABELS_pred   gold heads, predicted labels (from predicted POS + gold heads) (isolates the labeler)
Paired CIs vs GOLD. The per-rung loss tells which NOT_BF organ (pos_tagger / arc_parser / arc_labeler) costs the decision.
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

SEED = 20260912
_FRONTEND = None


def _fe():
    global _FRONTEND
    if _FRONTEND is None:
        import hdlab.causation_typing as CT
        _FRONTEND = CT._frontend()
    return _FRONTEND


def overlay(doc, *, pos_src="pred", heads_src="pred", labels_src="pred"):
    """Replace doc.toks heads/deprels per variant. pos_src in {gold, pred}; heads_src/labels_src in {gold, pred}."""
    tg, pp, lb = _fe()
    by_sent = defaultdict(list)
    for tok in doc.toks:
        by_sent[tok.sent].append(tok)
    for sent, toks in by_sent.items():
        toks = sorted(toks, key=lambda x: x.idx)
        forms = [x.form for x in toks]
        pos = list(tg.tag(forms)) if pos_src == "pred" else [getattr(x, "upos", "X") or "X" for x in toks]
        gold_heads = {j + 1: x.head for j, x in enumerate(toks)}
        gold_labels = {j + 1: x.deprel for j, x in enumerate(toks)}
        heads = dict(pp.parse(forms, pos).heads) if heads_src == "pred" else gold_heads
        labels = dict(lb.label(forms, pos, heads)) if labels_src == "pred" else gold_labels
        for j, x in enumerate(toks):
            i1 = j + 1
            x.deprel = labels.get(i1, x.deprel) or x.deprel
            x.head = heads.get(i1, x.head)


def gold_targets(data):
    t = {}
    for doc, mlive in data:
        t[id(doc)] = {tok.gidx for tok in doc.toks if tok.deprel in B1.UND_DEPRELS}
    return t


def main():
    rng = np.random.default_rng(SEED)
    variants = [("GOLD", None), ("PRED_ALL", dict(pos_src="pred", heads_src="pred", labels_src="pred")),
                ("PRED_goldPOS", dict(pos_src="gold", heads_src="pred", labels_src="pred")),
                ("HEADS_pred", dict(pos_src="pred", heads_src="pred", labels_src="gold")),
                ("LABELS_pred", dict(pos_src="pred", heads_src="gold", labels_src="pred"))]
    results = {}
    base_items = None
    for name, cfg in variants:
        data = TH.load(False)                       # fresh gold docs each time
        targets = gold_targets(data)                # the SAME gold target tokens for every variant
        if cfg is not None:
            for doc, _ in data:
                overlay(doc, **cfg)
        res = TH.run_arm(data, accrue=True, window=TH.WINDOW, principle_a=True, targets=targets)
        results[name] = np.array([h for h, _ in res])
        print(f"{name:13s} n={len(res)} acc={results[name].mean():.4f}")
    base = results["GOLD"]; n = len(base)
    print("\nloss vs GOLD (paired, same items):")
    for name in ("PRED_ALL", "PRED_goldPOS", "HEADS_pred", "LABELS_pred"):
        v = results[name]
        if len(v) != n:
            print(f"  {name}: item count differs ({len(v)} vs {n}) -- target alignment failed"); continue
        d = v.astype(float) - base; boots = np.array([d[rng.integers(0, n, n)].mean() for _ in range(2000)])
        print(f"  {name:13s} {d.mean():+.4f} CI95 [{np.percentile(boots,2.5):+.4f}, {np.percentile(boots,97.5):+.4f}]")
    loss_all = base.mean() - results["PRED_ALL"].mean()
    if loss_all > 0:
        print(f"\nshare of the total parse loss ({loss_all:.4f}): tagger {(results['PRED_goldPOS'].mean()-results['PRED_ALL'].mean())/loss_all:.2f} "
              f"(PRED_goldPOS recovers), heads {(base.mean()-results['HEADS_pred'].mean())/loss_all:.2f}, labels {(base.mean()-results['LABELS_pred'].mean())/loss_all:.2f}")


if __name__ == "__main__":
    main()
