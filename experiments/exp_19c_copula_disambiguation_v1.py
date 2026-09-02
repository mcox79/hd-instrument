"""exp_19c_copula_disambiguation_v1 -- DISAMBIGUATE the 19c reachability gap into its TRUE components, because the
tagging-ceiling result showed 84% of the '19c verb mistags' are COPULA/AUX (are/is/was/were/has), NOT archaic
open-class verbs. In UD a copula is AUX and the PREDICATE COMPLEMENT is the head (predicate-as-head), so the
who-did-what gold (which points verb_idx AT the copula, copula-as-head convention) makes the argument unreachable
FROM the copula token by CONVENTION, not by parser/tagger error.

Partitions LB_19c by verb_idx lemma:
  COPULA_AUX   verb is be/have/do/modal (copula or auxiliary)   -> the convention-mismatch slice
  OPEN_VERB    verb is a content verb
For each: base reachability, and a COPULA-AWARE reachability (traverse the cop relation: credit reaching the
copula's PREDICATE head heads[cop]) -- the brain-faithful fix (copular predication is a real construction: subject
BE predicate). Also isolates the GENUINE archaic open-class mistag slice (content verb tagged NOUN/ADJ) and its
size. Answers: how much of the +0.158 tagging-ceiling is copula-convention vs genuine archaic morphology, and does
a copula-aware reader recover the copula slice WITHOUT re-tagging (no gold, no LLM).
CPU numpy only. ASCII. own dir. --smoke fast.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from collections import Counter
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
OUT_DIR = get_output_dir("exp_19c_copula_disambiguation_v1")
MAX_HOPS = 8
COP_AUX = {"be", "is", "are", "was", "were", "been", "being", "am", "'s", "'re", "'m",
           "have", "has", "had", "'ve", "'d", "do", "does", "did",
           "will", "would", "shall", "should", "can", "could", "may", "might", "must"}


def cop_aware_reach(gold1, v1, heads, pos, toks):
    """credit reaching v OR (if v is a copula/aux) its PREDICATE head heads[v] -- copular predication:
    subject and complement attach to the predicate, the copula is a cop-child of it."""
    if _attaches_to_verb(gold1, v1, heads, pos, max_hops=MAX_HOPS):
        return True
    if pos[v1 - 1] == "AUX" or toks[v1 - 1].lower() in COP_AUX:
        pred = heads.get(v1)
        if pred and pred not in (0, v1):
            if gold1 == pred or _attaches_to_verb(gold1, pred, heads, pos, max_hops=MAX_HOPS):
                return True
    return False


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)
    rows = [r for r in V1.load_pop(V1.LB) if REG.cand_ok(r)]
    if args.smoke:
        rows = rows[:400]

    part = {"COPULA_AUX": {"n": 0, "base": 0, "copaware": 0, "wdw_base": 0, "wdw_cop": 0},
            "OPEN_VERB": {"n": 0, "base": 0, "copaware": 0, "wdw_base": 0, "wdw_cop": 0}}
    genuine_mistag = 0; genuine_examples = []; cop_examples = []
    per = {"base": [], "cop": [], "wdw_base": [], "wdw_cop": []}
    for r in rows:
        toks = r["sent"].split(); vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        pos = tg.tag(toks); vi1, gi1 = vi0 + 1, gi0 + 1
        heads, _, _ = AEO.parse_with_conf(toks, pos, W)
        is_cop = (toks[vi0].lower() in COP_AUX)
        base_r = int(_attaches_to_verb(gi1, vi1, heads, pos, max_hops=MAX_HOPS))
        cop_r = int(cop_aware_reach(gi1, vi1, heads, pos, toks))
        # who-did-what: chain_pick on base heads, vs a copula-aware chain (pick from candidates reaching v OR its pred)
        wdw_b = int(REG.chain_pick(r, toks, pos, heads, "far") == r["gold_head"])
        # copula-aware chain: if copula, add the predicate's subtree candidates
        def cop_chain_pick():
            attached = [c0 for c0 in r["cand_idx"] if cop_aware_reach(c0 + 1, vi1, heads, pos, toks)]
            post = [c for c in attached if c > vi0]; pool = post or attached
            if not pool:
                return r.get("pos_pick")
            idx = max(pool); return toks[idx] if 0 <= idx < len(toks) else r.get("pos_pick")
        wdw_c = int(cop_chain_pick() == r["gold_head"])
        key = "COPULA_AUX" if is_cop else "OPEN_VERB"
        part[key]["n"] += 1; part[key]["base"] += base_r; part[key]["copaware"] += cop_r
        part[key]["wdw_base"] += wdw_b; part[key]["wdw_cop"] += wdw_c
        per["base"].append(base_r); per["cop"].append(cop_r); per["wdw_base"].append(wdw_b); per["wdw_cop"].append(wdw_c)
        if not is_cop and pos[vi0] in ("NOUN", "PROPN", "ADJ"):
            genuine_mistag += 1
            if len(genuine_examples) < 12:
                genuine_examples.append({"verb": toks[vi0], "as": pos[vi0], "ctx": " ".join(toks[max(0, vi0 - 2):vi0 + 3])})
        if is_cop and not base_r and len(cop_examples) < 8:
            cop_examples.append({"cop": toks[vi0], "gold": r["gold_head"], "ctx": " ".join(toks[max(0, vi0 - 1):vi0 + 5])})

    def rate(d, k):
        return round(d[k] / max(1, d["n"]), 4)
    def bootd(a, b, nboot=2000, seed=13):
        a = np.array(a, float); b = np.array(b, float); d = a - b; n = len(d); rng = np.random.default_rng(seed)
        bs = np.array([d[rng.integers(0, n, n)].mean() for _ in range(nboot)]); lo, hi = np.percentile(bs, [2.5, 97.5])
        nu = np.array([(d * rng.choice([-1, 1], n)).mean() for _ in range(nboot)])
        return {"delta": round(float(d.mean()), 4), "ci_lo": round(float(lo), 4), "ci_hi": round(float(hi), 4),
                "null_p95": round(float(np.percentile(np.abs(nu), 95)), 4)}
    N = len(per["base"])
    res = {"n": N,
           "COPULA_AUX": {"n": part["COPULA_AUX"]["n"], "share": round(part["COPULA_AUX"]["n"] / N, 4),
                          "base_reach": rate(part["COPULA_AUX"], "base"), "copaware_reach": rate(part["COPULA_AUX"], "copaware"),
                          "wdw_base": rate(part["COPULA_AUX"], "wdw_base"), "wdw_cop": rate(part["COPULA_AUX"], "wdw_cop")},
           "OPEN_VERB": {"n": part["OPEN_VERB"]["n"], "share": round(part["OPEN_VERB"]["n"] / N, 4),
                         "base_reach": rate(part["OPEN_VERB"], "base"), "copaware_reach": rate(part["OPEN_VERB"], "copaware"),
                         "wdw_base": rate(part["OPEN_VERB"], "wdw_base"), "wdw_cop": rate(part["OPEN_VERB"], "wdw_cop")},
           "genuine_openclass_mistag_n": genuine_mistag, "genuine_openclass_mistag_share": round(genuine_mistag / N, 4),
           "ALL_reach_base": round(np.mean(per["base"]), 4), "ALL_reach_copaware": round(np.mean(per["cop"]), 4),
           "ALL_reach_delta": bootd(per["cop"], per["base"]),
           "ALL_wdw_base": round(np.mean(per["wdw_base"]), 4), "ALL_wdw_cop": round(np.mean(per["wdw_cop"]), 4),
           "ALL_wdw_delta": bootd(per["wdw_cop"], per["wdw_base"]),
           "genuine_examples": genuine_examples, "cop_examples": cop_examples}
    print(json.dumps({k: v for k, v in res.items() if k not in ("genuine_examples", "cop_examples")}, indent=2), flush=True)
    print("\n[COPULA slice] share=%.3f base_reach=%.3f -> cop-aware=%.3f ; who-did-what %.3f -> %.3f" % (
        res["COPULA_AUX"]["share"], res["COPULA_AUX"]["base_reach"], res["COPULA_AUX"]["copaware_reach"],
        res["COPULA_AUX"]["wdw_base"], res["COPULA_AUX"]["wdw_cop"]), flush=True)
    print("[OPEN slice]   share=%.3f base_reach=%.3f -> cop-aware=%.3f" % (
        res["OPEN_VERB"]["share"], res["OPEN_VERB"]["base_reach"], res["OPEN_VERB"]["copaware_reach"]), flush=True)
    print("[GENUINE archaic open-class mistag] n=%d share=%.3f" % (genuine_mistag, res["genuine_openclass_mistag_share"]), flush=True)
    print("[ALL] reach %.3f -> %.3f (d=%+.4f CI[%+.4f,%+.4f]) ; who-did-what %.3f -> %.3f (d=%+.4f CI[%+.4f,%+.4f])" % (
        res["ALL_reach_base"], res["ALL_reach_copaware"], res["ALL_reach_delta"]["delta"], res["ALL_reach_delta"]["ci_lo"], res["ALL_reach_delta"]["ci_hi"],
        res["ALL_wdw_base"], res["ALL_wdw_cop"], res["ALL_wdw_delta"]["delta"], res["ALL_wdw_delta"]["ci_lo"], res["ALL_wdw_delta"]["ci_hi"]), flush=True)
    print("\n[genuine archaic open-class verbs missed]:", flush=True)
    for e in genuine_examples:
        print("   '%s' ->%s  ...%s..." % (e["verb"], e["as"], e["ctx"]), flush=True)
    print("\n[copula cases unreachable at base]:", flush=True)
    for e in cop_examples:
        print("   cop='%s' gold='%s'  ...%s..." % (e["cop"], e["gold"], e["ctx"]), flush=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "c19_copula_disambiguation_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
