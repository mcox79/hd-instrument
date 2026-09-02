"""exp_19c_tagging_lever_ceiling_v1 -- SIZE the tagging lever + identify the exact 19c failure mechanism.
The reach-failure diagnosis showed 65% of 19c gold-unreachable cases have the TARGET VERB MISTAGGED by our tagger.
This cell (a) shows WHAT the mistagged 19c verbs get tagged as (the archaic mechanism), and (b) measures the
CEILING: if the tagger got the target verb right, how much does PP-chain reachability + who-did-what rise?
We KNOW verb_idx is a verb (the who-did-what gold says so), so forcing pos[verb_idx]='VERB' and re-parsing is a
clean, honest ceiling for the register-tagging lever (verb identification only). Compares:
  BASE        our tagger + arc-eager
  VERBFIX     force pos[verb_idx]=VERB (+ gold NOUN if mistagged), re-parse   [tagging-lever ceiling]
Metrics: gold PP-chain reachability (`_attaches_to_verb`) and CHAIN who-did-what (parent's chain_pick), 19c + modern.
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
OUT_DIR = get_output_dir("exp_19c_tagging_lever_ceiling_v1")
MAX_HOPS = 8


def boot(a, b, nboot=2000, seed=13):
    a = np.array(a, float); b = np.array(b, float); d = a - b; n = len(d)
    rng = np.random.default_rng(seed)
    bs = np.array([d[rng.integers(0, n, n)].mean() for _ in range(nboot)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    null = np.array([(d * rng.choice([-1, 1], n)).mean() for _ in range(nboot)])
    return {"a": float(a.mean()), "b": float(b.mean()), "delta": float(d.mean()), "ci_lo": float(lo),
            "ci_hi": float(hi), "half": float((hi - lo) / 2), "null_p95": float(np.percentile(np.abs(null), 95))}


def run(path, tg, W, smoke):
    rows = [r for r in V1.load_pop(path) if REG.cand_ok(r)]
    if smoke:
        rows = rows[:400]
    R = {"base_reach": [], "vfix_reach": [], "base_wdw": [], "vfix_wdw": []}
    mistag = Counter(); examples = []
    for r in rows:
        toks = r["sent"].split(); vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        pos = tg.tag(toks)
        if pos[vi0] != "VERB":
            mistag[pos[vi0]] += 1
            if len(examples) < 15:
                examples.append({"verb": toks[vi0], "tagged": pos[vi0], "ctx": " ".join(toks[max(0, vi0 - 2):vi0 + 3])})
        vi1, gi1 = vi0 + 1, gi0 + 1
        hb, _, _ = AEO.parse_with_conf(toks, pos, W)
        pos2 = list(pos); pos2[vi0] = "VERB"
        if pos2[gi0] not in ("NOUN", "PROPN"):
            pos2[gi0] = "NOUN"
        hv, _, _ = AEO.parse_with_conf(toks, pos2, W)
        R["base_reach"].append(int(_attaches_to_verb(gi1, vi1, hb, pos, max_hops=MAX_HOPS)))
        R["vfix_reach"].append(int(_attaches_to_verb(gi1, vi1, hv, pos2, max_hops=MAX_HOPS)))
        R["base_wdw"].append(int(REG.chain_pick(r, toks, pos, hb, "far") == r["gold_head"]))
        R["vfix_wdw"].append(int(REG.chain_pick(r, toks, pos2, hv, "far") == r["gold_head"]))
    reach = boot(R["vfix_reach"], R["base_reach"])
    wdw = boot(R["vfix_wdw"], R["base_wdw"])
    return {"n": len(R["base_reach"]), "reach": reach, "wdw": wdw,
            "verb_mistag_rate": round(sum(mistag.values()) / max(1, len(R["base_reach"])), 4),
            "mistag_as": dict(mistag.most_common()), "examples": examples}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)
    out = {}
    for nm, path in (("LB_19c", V1.LB), ("QA_modern", V1.QA)):
        print("\n=== %s ===" % nm, flush=True)
        res = run(path, tg, W, args.smoke); out[nm] = res
        print("  verb-mistag rate=%.3f  mistagged AS: %s" % (res["verb_mistag_rate"], res["mistag_as"]), flush=True)
        print("  REACH  base=%.4f  verbfix=%.4f  d=%+.4f CI[%+.4f,%+.4f] null_p95=%.4f" % (
            res["reach"]["b"], res["reach"]["a"], res["reach"]["delta"], res["reach"]["ci_lo"], res["reach"]["ci_hi"], res["reach"]["null_p95"]), flush=True)
        print("  WHODIDWHAT base=%.4f verbfix=%.4f  d=%+.4f CI[%+.4f,%+.4f] null_p95=%.4f" % (
            res["wdw"]["b"], res["wdw"]["a"], res["wdw"]["delta"], res["wdw"]["ci_lo"], res["wdw"]["ci_hi"], res["wdw"]["null_p95"]), flush=True)
    print("\n[19c archaic-verb examples that our tagger misses]", flush=True)
    for e in out["LB_19c"]["examples"][:12]:
        print("   '%s' -> %s   in: ...%s..." % (e["verb"], e["tagged"], e["ctx"]), flush=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "c19_tagging_lever_ceiling_v1", "results": out,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
