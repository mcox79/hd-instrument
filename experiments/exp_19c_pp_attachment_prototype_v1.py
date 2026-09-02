"""exp_19c_pp_attachment_prototype_v1 -- PROPERLY prototype the RIGHT component for the 19c who-did-what wall.
The failure diagnostic (exp_19c_selection_failure_v1) showed 93% of 19c who-did-what failures are PP-EMBEDDING:
the gold argument is a PREPOSITION's object ~9 tokens after the verb, reachable from the verb only through a
head-chain (verb -> prep -> ... -> gold), NOT a direct post-verbal object. The position-organ (nearest post-
verbal) structurally cannot get these; the parser's head-chain / PP-attachment (predicate_argument_frontend.
_attaches_to_verb) is the mechanism designed for exactly this. So the RIGHT prototype is: does a parse-based
head-chain selector recover these, and does the RICH parser (UAS 0.842) beat the LIVE richfeat parser at it?

ARMS (19c LitBank + QA modern), who-did-what patient accuracy:
  POS_ORGAN     hybrid_role_patient (position+voice; the current live path)     -> the floor for these
  CHAIN_rich    among candidates that TRANSITIVELY attach to the verb (arc-eager RICH heads), pick the FARTHEST
                (deepest PP object = the 19c gold pattern); else position fallback
  CHAIN_richfeat same, with the LIVE richfeat heads                              -> rich vs live parser
  ORACLE_reach  can ANY parser reach it: gold is transitively attached to the verb (rich heads)  [upper bound]
Also reports the transitive-REACHABILITY rate of the gold (rich vs richfeat) -- does the parser even reach the
PP-embedded gold? CPU numpy, NO torch/spaCy/LLM. ASCII. own dir.
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
from hdlab.graded_role_assigner import hybrid_role_patient
from hdlab.predicate_argument_frontend import _attaches_to_verb
from hdlab.arc_parser import ArcParser

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_19c_pp_attachment_prototype_v1")
MAX_HOPS = 8  # deep PP chains (mean 19c dist = 9)


def cand_ok(r):
    return len(GD.cands(r)) >= 2 and sum(1 for h, _ in GD.cands(r) if GD.anim(h)) < 2


def chain_pick(r, toks, pos, heads, prefer="far"):
    """among candidates that TRANSITIVELY attach to the verb (head-chain), pick farthest/nearest post-verbal."""
    vi0 = r["verb_idx"]; v1 = vi0 + 1
    attached = []
    for c0 in r["cand_idx"]:
        c1 = c0 + 1
        if _attaches_to_verb(c1, v1, heads, pos, max_hops=MAX_HOPS):
            attached.append(c0)
    post = [c for c in attached if c > vi0]
    pool = post or attached
    if not pool:
        return r.get("pos_pick")
    idx = max(pool) if prefer == "far" else min(pool)
    return toks[idx]


def analyze(name, path, W, rich, tg):
    rows = [r for r in V1.load_pop(path) if cand_ok(r)]
    n = 0; hitP = hitCr = hitCf = reach_r = reach_f = 0
    for r in rows:
        toks = r["sent"].split()
        vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        n += 1
        pos = tg.tag(toks)
        hr, _, _ = AEO.parse_with_conf(toks, pos, W)
        hf = rich.parse(toks, pos).heads
        v1 = vi0 + 1; cands = [c + 1 for c in r["cand_idx"]]
        try:
            oidx = hybrid_role_patient(toks, pos, v1, cands)
            porg = toks[oidx - 1] if (oidx and 1 <= oidx <= len(toks)) else r.get("pos_pick")
        except Exception:
            porg = r.get("pos_pick")
        hitP += int(porg == r["gold_head"])
        hitCr += int(chain_pick(r, toks, pos, hr, "far") == r["gold_head"])
        hitCf += int(chain_pick(r, toks, pos, hf, "far") == r["gold_head"])
        reach_r += int(_attaches_to_verb(gi0 + 1, v1, hr, pos, max_hops=MAX_HOPS))
        reach_f += int(_attaches_to_verb(gi0 + 1, v1, hf, pos, max_hops=MAX_HOPS))
    res = {"n": n, "POS_ORGAN": round(hitP / n, 4), "CHAIN_rich": round(hitCr / n, 4),
           "CHAIN_richfeat": round(hitCf / n, 4), "gold_reach_rich": round(reach_r / n, 4),
           "gold_reach_richfeat": round(reach_f / n, 4)}
    print("[%s] n=%d" % (name, n), flush=True)
    print("  POS_ORGAN(live)=%.4f  CHAIN_rich=%.4f  CHAIN_richfeat=%.4f" % (res["POS_ORGAN"], res["CHAIN_rich"], res["CHAIN_richfeat"]), flush=True)
    print("  gold transitively-REACHABLE from verb: rich=%.4f richfeat=%.4f" % (res["gold_reach_rich"], res["gold_reach_richfeat"]), flush=True)
    # CI on CHAIN_rich vs POS_ORGAN and vs CHAIN_richfeat
    def arm(fn):
        return fn
    return res, rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--nboot", type=int, default=2000); ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)
    rich = ArcParser.load(os.path.join(_REPO, "data", "frontend_assets", "arc_parser_richfeat_ud_ewt.npz"))
    out = {}
    for nm, path in (("litbank_19c", V1.LB), ("qa_modern", V1.QA)):
        print("\n=== %s ===" % nm, flush=True)
        res, _ = analyze(nm, path, W, rich, tg)
        out[nm] = res
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "c19_pp_attachment_prototype_v1", "results": out,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
