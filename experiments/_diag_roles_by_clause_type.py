"""DIAG (strategy 2026-09-13): the LABELS rung split by CLAUSE TYPE. Where does the Competition-Model role labeler lose subjects and
objects -- matrix clauses, EMBEDDED clauses (ccomp/xcomp/advcl/acl/relcl/csubj governors) or COPULAR clauses (the subject's head is a
non-verbal predicate)? UD-EWT test 700 under (a) the LIVE chain (organ categories -> attachment arm heads -> coarse_roles) and
(b) gold heads (isolates the labeler). Per type: gold nsubj / nsubj:pass / obj recall and the labeler's confusions. Read-only.
Output: data/exp_diag_roles_by_clause_type_v1/metrics.json.   Run: python experiments/_diag_roles_by_clause_type.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import json
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir
import hdlab.attachment_arm as AA
import hdlab.lexical_categories as LC
from hdlab import graded_role_assigner as GRA
from tools.build_attachment_validities import sentences, TEST

EMBED = {"ccomp", "xcomp", "advcl", "acl", "acl:relcl", "csubj", "csubj:pass", "parataxis"}
TARGET = {"nsubj", "nsubj:pass", "obj"}


def clause_type(i, gold_pos, gold_heads, rels):
    """Type of the clause the nominal i (1-based) is an argument of, from the GOLD tree: copular if its head is not a VERB/AUX;
    embedded if the head's own relation is a clausal one; else matrix."""
    h = gold_heads[i - 1]
    if h <= 0:
        return "matrix"
    if gold_pos[h - 1] not in ("VERB", "AUX"):
        return "copular"
    return "embedded" if rels[h - 1] in EMBED else "matrix"


def main():
    test = sentences(TEST, cap=700, maxlen=10**6)
    tab = AA.load_attachment_validities(); lc = LC.get(); val = GRA.load_coarse_validities()
    out = {}
    for arm in ("live", "goldheads"):
        rec = defaultdict(Counter); conf = defaultdict(Counter); n_head_ok = Counter(); n_tot = Counter()
        for toks, gold_pos, gold_heads, rels in test:
            if arm == "live":
                pos = lc.tag(list(toks)); heads = AA.heads(toks, pos, tab)
            else:
                pos = list(gold_pos); heads = {i: gold_heads[i - 1] for i in range(1, len(toks) + 1)}
            roles = GRA.coarse_roles(toks, pos, heads, val)
            for i in range(1, len(toks) + 1):
                g = rels[i - 1]
                if g not in TARGET:
                    continue
                ct = clause_type(i, gold_pos, gold_heads, rels)
                p = roles.get(i, "<none>")
                n_tot[ct] += 1; n_head_ok[ct] += int(heads.get(i, -1) == gold_heads[i - 1])
                rec[(ct, g)]["n"] += 1; rec[(ct, g)]["ok"] += int(p == g)
                if p != g:
                    conf[(ct, g)][p] += 1
        res = {"head_correct_rate": {ct: round(n_head_ok[ct] / n_tot[ct], 3) for ct in n_tot}, "n": dict(n_tot), "recall": {}, "confusions": {}}
        for (ct, g), c in sorted(rec.items()):
            res["recall"]["%s|%s" % (ct, g)] = {"n": c["n"], "recall": round(c["ok"] / c["n"], 3)}
            res["confusions"]["%s|%s" % (ct, g)] = dict(conf[(ct, g)].most_common(4))
        out[arm] = res
        print("== %s heads" % arm, "| head-correct rate by clause type:", res["head_correct_rate"], "| n:", res["n"])
        for k, v in res["recall"].items():
            print("   %-22s n=%4d recall %.3f  misses -> %s" % (k, v["n"], v["recall"], res["confusions"][k]))
    od = str(get_output_dir("diag_roles_by_clause_type_v1")); os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)
    print("DONE")


if __name__ == "__main__":
    main()
