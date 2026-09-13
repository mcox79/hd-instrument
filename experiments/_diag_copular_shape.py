"""DIAGNOSTIC (strategy 2026-09-13): the SHAPE the live governor builds for copular clauses vs what the copular binder reads.
For each gold PREDICATIONAL clause (holder h, property p) on UD-EWT test: where do the governor's heads put the property, the holder
and the copula; does extract_entity_states / robust_cop recover (h, p). usage: python experiments/_diag_copular_shape.py [cap]
(set HDLAB_HEADS_SOURCE to compare the stand-in)."""
import os, sys, json
from collections import Counter
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, REPO)
import hdlab.copular_binding as CB
import experiments.exp_copular_is_a_binding_readout_v1 as COP   # gold loader / typed_gold
from hdlab import frontend as FE
from hdlab.arc_labeler import ArcLabeler
import experiments._copular_nominal_events as M
cap = int(sys.argv[1]) if len(sys.argv) > 1 else 150
PRED = {"pred_adj", "pred_nom"}
pos_t = FE.tagger(); arc = FE.parser(); lab = ArcLabeler.load(M._LAB_ASSET)
sents = COP.load_ud(COP.UD_TEST, cap=cap)
COPW = {"be", "is", "are", "was", "were", "been", "being", "am", "'s", "'re", "'m", "become", "became", "seem", "seems", "seemed"}
n = 0; prop_head = Counter(); hold_head = Counter(); cop_head = Counter(); found_lab = 0; found_rob = 0; found_any = 0; ex = []
for sent in sents:
    toks = [r[1] for r in sent]; up = pos_t.tag(toks)
    gold = [(h, p, t) for (h, p, t) in COP.typed_gold(sent) if t in PRED]
    if not gold:
        continue
    heads = arc.parse(toks, up).heads
    lab_pairs = set(CB.extract_entity_states(toks, up, arc, lab, heads=heads))
    rob_pairs = CB.robust_cop(toks, up, heads, gate=True)
    for (h, p, t) in gold:
        n += 1
        ph = heads.get(p + 1, -1); hh = heads.get(h + 1, -1)
        prop_head["ROOT" if ph == 0 else ("holder" if ph == h + 1 else "other")] += 1
        hold_head["property" if hh == p + 1 else ("ROOT" if hh == 0 else "other")] += 1
        cops = [i for i in range(min(h, p), max(h, p) + 1) if toks[i].lower() in COPW or up[i] == "AUX"]
        if cops:
            ch = heads.get(cops[0] + 1, -1)
            cop_head["property" if ch == p + 1 else ("holder" if ch == h + 1 else ("ROOT" if ch == 0 else "other"))] += 1
        fl = (h, p) in lab_pairs; fr = (h, p) in rob_pairs
        found_lab += fl; found_rob += fr; found_any += (fl or fr)
        if not (fl or fr) and len(ex) < 8:
            ex.append({"sent": " ".join(toks)[:90], "holder": toks[h], "prop": toks[p], "prop_head": toks[ph - 1] if ph > 0 else str(ph),
                       "holder_head": toks[hh - 1] if hh > 0 else str(hh), "lab": sorted(lab_pairs)[:3], "rob": sorted(rob_pairs)[:3]})
print(json.dumps({"heads_source": FE.HEADS_SOURCE, "gold_pairs": n, "found_label_path": round(found_lab / max(1, n), 3),
                  "found_robust_cop": round(found_rob / max(1, n), 3), "found_any": round(found_any / max(1, n), 3),
                  "property_head": dict(prop_head), "holder_head": dict(hold_head), "copula_head": dict(cop_head)}))
for e in ex: print(json.dumps(e, ensure_ascii=False))
