"""DIAG (strategy 2026-09-13): the board's who_did_what_agent read is an ISLAND -- exp_board_agent_slot_ud_v1 scores a hybrid
(word-order default + marked-cue override over clause-local nominals) that never consults the governor's heads or the role
competition's table (the weighted role table changed that dimension by 0.0000). Score the LIVE CHAIN on the SAME items:
  tags (category organ) -> heads (attachment arm, live decode) -> coarse_roles (live or named table):
  active verb: the nominal labelled nsubj under the verb; passive: the nominal labelled obl:agent under the verb.
Arms: chain-only (abstain if no labelled agent), chain + positional fallback, positional floor, and the board's hybrid for reference.
Run: HDLAB_ROLE_VALIDITIES=<table> python experiments/_diag_agent_dimension_live_chain.py [cap]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import json
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir
import experiments.exp_board_agent_slot_ud_v1 as AG
import hdlab.attachment_arm as AA
import hdlab.lexical_categories as LC
from hdlab import graded_role_assigner as GRA


def main():
    cap = int(sys.argv[1]) if len(sys.argv) > 1 else None
    sents = AG.load_ud(AG.UD_TEST)
    if cap:
        sents = sents[:cap]
    items = AG.gold_agent_items(sents)
    lc = LC.get(); tab = AA.load_attachment_validities(); val = GRA.load_coarse_validities()
    n = 0; ok = Counter(); dec = Counter(); conf = Counter()
    cache = {}
    for toks, v, gold, passive in items:
        key = tuple(toks)
        if key not in cache:
            pos = lc.tag(list(toks)); heads = AA.heads(toks, pos, tab); roles = GRA.coarse_roles(toks, pos, heads, val)
            cache[key] = (pos, heads, roles)
        pos, heads, roles = cache[key]
        n += 1
        want = "obl:agent" if passive else "nsubj"
        cands = [i for i in range(1, len(toks) + 1) if heads.get(i, -1) == v and roles.get(i) == want]
        # positional floor on the same clause-local candidates the board uses
        up = pos
        floor_c = AG._clause_local_nominals(toks, up, v)
        fl = AG.floor_positional_agent(toks, up, v, floor_c) if floor_c else None     # a head STRING or None
        fl_ok = fl is not None and AG._match(fl, toks[gold - 1])
        ok["floor"] += int(fl_ok)
        if cands:
            pick = cands[0] if not passive else cands[-1]
            dec["chain"] += 1; ok["chain_decided"] += int(pick == gold); ok["chain_fallback"] += int(pick == gold)
            if pick != gold:
                conf[("wrong", "passive" if passive else "active", roles.get(gold, "<none>"), "head_ok" if heads.get(gold, -1) == v else "head_wrong")] += 1
        else:
            conf[("abstain", "passive" if passive else "active", roles.get(gold, "<none>"), "head_ok" if heads.get(gold, -1) == v else "head_wrong")] += 1
            ok["chain_fallback"] += int(fl_ok)
    out = {"n": n, "floor_positional": round(ok["floor"] / n, 4), "chain_decision_rate": round(dec["chain"] / n, 4),
           "chain_precision_when_decided": round(ok["chain_decided"] / max(1, dec["chain"]), 4),
           "chain_plus_positional_fallback": round(ok["chain_fallback"] / n, 4),
           "role_table": os.environ.get("HDLAB_ROLE_VALIDITIES", "live"),
           "misses": {"|".join(k): c for k, c in conf.most_common(16)}}
    od = str(get_output_dir("diag_agent_dimension_live_chain_v1")); os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "misses"}))
    for k, c in out["misses"].items():
        print("  ", k, c)
    print("DONE")


if __name__ == "__main__":
    main()
