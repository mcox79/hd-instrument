"""exp_19c_reach_failure_diagnosis_v1 -- WHY does the arc-eager parser fail to reach the 19c gold argument 30% of
the time? Partition the base-parser reachability FAILURES by cause, to decide which lever owns the residual:
PP-ATTACHMENT (fixable by selectional preference) vs TAGGING (verb/prep/gold mistagged -> structure fundamentally
wrong, needs register-native tagging) vs STRUCTURAL (long chain / wrong-verb block).

Also tests whether the selectional signal is REAL when the confound (which verb) is removed: given the KNOWN target
verb, does attaching the gold-bearing PP to it recover reachability, and does the register association LA(verb,prep)
DISCRIMINATE gold-bearing prepositions from the sentence's other prepositions (a clean AUC test of the signal).

Partitions on LB_19c (cand_ok), for rows where base_reach==0:
  VERB_MISTAGGED   pos[verb_idx] != VERB          (upstream tagging error -> not a PP-attach problem)
  GOLD_MISTAGGED   pos[gold_idx] not NOUN/PROPN   (upstream tagging error)
  NO_PREP_PATH     no ADP token governs the gold chain (not a PP case)
  WRONGVERB_BLOCK  gold chain hits a DIFFERENT verb before the target (attachment/structural)
  PP_ATTACH_ERR    tags OK, prep present, but PP attached low (the true PP-attach residual)
CEILING: force gold-object -> known target verb; reach should approach 1 - tag-error rate.
CPU numpy only. ASCII. own dir. --smoke fast.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_parser_gap_decomp_v1 as GD
import experiments.exp_arceager_parser_operator_v1 as AEO
import experiments.exp_register_native_pp_attachment_v1 as REG
from hdlab.predicate_argument_frontend import _attaches_to_verb

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_19c_reach_failure_diagnosis_v1")
MAX_HOPS = 8


def gov_prep_of_gold(toks, pos, heads, gi1):
    """walk UP from gold; return the index of the ADP whose object subtree contains gold (the prep that must
    high-attach), or None. In UD the ADP is a child (case) of the nominal, so we scan for an ADP attached into
    the gold's chain."""
    # collect the chain gold -> ... -> root
    chain = []; cur = gi1
    for _ in range(MAX_HOPS + 1):
        if cur is None or cur == 0:
            break
        chain.append(cur); cur = heads.get(cur)
    # any ADP whose head is in the chain (case-marks a nominal on the path)
    for p in range(1, len(toks) + 1):
        if pos[p - 1] == "ADP" and heads.get(p) in chain:
            return p
    return None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)

    rows = [r for r in V1.load_pop(V1.LB) if REG.cand_ok(r)]
    if args.smoke:
        rows = rows[:400]
    n = 0; base_reach = 0; ceil_reach = 0
    buckets = {"VERB_MISTAGGED": 0, "GOLD_MISTAGGED": 0, "NO_PREP_PATH": 0, "WRONGVERB_BLOCK": 0, "PP_ATTACH_ERR": 0}
    # selectional-signal AUC: for each row, LA(known_verb, prep_of_gold) vs LA(known_verb, prep) of a NON-gold PP
    la_gold = []; la_nongold = []
    # build a moderate 19c association for the signal test (reuse REG.build_assoc)
    tag19 = REG.load_or_tag(os.path.join(REG.OUT_DIR, "tagged_19c_%d.jsonl" % (6000 if args.smoke else 120000)),
                            REG.LB_RAW, 6000 if args.smoke else 120000, tg)
    A19 = REG.build_assoc(tag19)

    for r in rows:
        toks = r["sent"].split(); vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        n += 1
        pos = tg.tag(toks)
        heads, _, _ = AEO.parse_with_conf(toks, pos, W)
        vi1, gi1 = vi0 + 1, gi0 + 1
        reached = _attaches_to_verb(gi1, vi1, heads, pos, max_hops=MAX_HOPS)
        base_reach += int(reached)
        # ceiling: force gold-object subtree onto the known target verb (attach gold's TOP pre-verb ancestor to verb)
        h2 = dict(heads); h2[gi1] = vi1
        ceil_reach += int(_attaches_to_verb(gi1, vi1, h2, pos, max_hops=MAX_HOPS))
        # selectional signal: prep that governs gold vs a random other prep in the sentence
        pg = gov_prep_of_gold(toks, pos, heads, gi1)
        vlem = V1._lem(toks[vi0])
        if pg is not None:
            la_gold.append(REG.assoc_LA(A19, vlem, None, toks[pg - 1].lower()))
        other = [p for p in range(1, len(toks) + 1) if pos[p - 1] == "ADP" and p != pg
                 and toks[p - 1].lower() in REG.PREPS]
        if other:
            la_nongold.append(REG.assoc_LA(A19, vlem, None, toks[other[0] - 1].lower()))
        if reached:
            continue
        # classify the FAILURE
        if pos[vi0] != "VERB":
            buckets["VERB_MISTAGGED"] += 1
        elif pos[gi0] not in ("NOUN", "PROPN"):
            buckets["GOLD_MISTAGGED"] += 1
        elif pg is None:
            buckets["NO_PREP_PATH"] += 1
        else:
            # does the gold chain hit a DIFFERENT verb before the target?
            cur = gi1; blocked = False
            for _ in range(MAX_HOPS + 1):
                if cur == vi1 or cur is None or cur == 0:
                    break
                if pos[cur - 1] == "VERB" and cur != vi1:
                    blocked = True; break
                cur = heads.get(cur)
            buckets["WRONGVERB_BLOCK" if blocked else "PP_ATTACH_ERR"] += 1

    nfail = n - base_reach
    def auc(pos_s, neg_s):
        pos_s = np.array(pos_s); neg_s = np.array(neg_s)
        if len(pos_s) == 0 or len(neg_s) == 0:
            return 0.5
        return float(np.mean([np.mean(p > neg_s) + 0.5 * np.mean(p == neg_s) for p in pos_s]))
    sig_auc = auc(la_gold, la_nongold)

    res = {"n": n, "base_reach": round(base_reach / n, 4), "ceiling_forced_verb": round(ceil_reach / n, 4),
           "n_fail": nfail, "failure_buckets": buckets,
           "failure_shares": {k: round(v / max(1, nfail), 4) for k, v in buckets.items()},
           "tag_error_share_of_fail": round((buckets["VERB_MISTAGGED"] + buckets["GOLD_MISTAGGED"]) / max(1, nfail), 4),
           "selectional_signal_auc": round(sig_auc, 4),
           "la_gold_mean": round(float(np.mean(la_gold)) if la_gold else 0, 3),
           "la_nongold_mean": round(float(np.mean(la_nongold)) if la_nongold else 0, 3),
           "n_la_gold": len(la_gold), "n_la_nongold": len(la_nongold)}
    print(json.dumps(res, indent=2), flush=True)
    print("\n[READ] base reach=%.3f  ceiling(force gold->verb)=%.3f  fails=%d" % (res["base_reach"], res["ceiling_forced_verb"], nfail), flush=True)
    print("[READ] of the failures: TAG-error=%.0f%%  wrong-verb-block=%.0f%%  PP-attach-err=%.0f%%  no-prep=%.0f%%" % (
        100 * res["tag_error_share_of_fail"], 100 * res["failure_shares"]["WRONGVERB_BLOCK"],
        100 * res["failure_shares"]["PP_ATTACH_ERR"], 100 * res["failure_shares"]["NO_PREP_PATH"]), flush=True)
    print("[READ] selectional-signal AUC (does LA(verb,gold-prep) > LA(verb,other-prep)?) = %.3f  [gold %.2f vs other %.2f]" % (
        sig_auc, res["la_gold_mean"], res["la_nongold_mean"]), flush=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "c19_reach_failure_diagnosis_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
