"""DIAGNOSTIC (strategy 2026-09-13): anatomy of the attachment arm's errors for ONE relation under ONE asset.
usage: python experiments/_diag_rel_attachment_errors.py <asset.json> <rel> [cap]
For each gold <rel> dependent with a wrong predicted head: category of the chosen head, left/right, whether the dependent is a PP
object (preceded by ADP), and whether its wrong head is a VERB (the order-aware teacher's subject/object pull)."""
import os, sys, json
from collections import Counter
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, REPO)
import hdlab.attachment_arm as AA
from tools.build_attachment_validities import sentences, TEST
asset, rel = sys.argv[1], sys.argv[2]; cap = int(sys.argv[3]) if len(sys.argv) > 3 else 400
test = sentences(TEST, cap=cap, maxlen=10**6); tab = AA.load_attachment_validities(asset)
tot = ok = 0; kind = Counter(); ppobj_wrong = Counter(); ex = []
for toks, pos, heads_g, rels in test:
    hd = AA.heads(toks, pos, tab)
    for i, (g, r) in enumerate(zip(heads_g, rels), start=1):
        if r != rel or not (1 <= g <= len(toks)):
            continue
        tot += 1; p = hd.get(i, -1)
        is_pp = i >= 2 and pos[i - 2] == "ADP"
        if p == g:
            ok += 1; continue
        pc = pos[p - 1] if 1 <= p <= len(toks) else "ROOT"
        side = "L" if (1 <= p <= len(toks) and p < i) else "R"
        k = f"{pc}:{side}" + (":verb_before_dep" if (pc == "VERB" and p < i) else "")
        kind[k] += 1; ppobj_wrong["pp_obj" if is_pp else "bare"] += 1
        if pc == "VERB" and len(ex) < 8:
            ex.append({"sent": " ".join(toks)[:100], "dep": toks[i - 1], "gold": toks[g - 1], "pred": toks[p - 1], "pp": is_pp})
print(json.dumps({"asset": os.path.basename(asset), "rel": rel, "n": tot, "recall": round(ok / max(1, tot), 4), "wrong": tot - ok,
                  "wrong_kind": dict(kind.most_common(8)), "wrong_dep_is_pp_object": dict(ppobj_wrong)}))
for e in ex:
    print(json.dumps(e, ensure_ascii=False))
