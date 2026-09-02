"""exp_parser_through_real_organs_v1 -- MEASURE THE BRAIN-FAITHFUL CONSUMERS' OWN OUTCOME (owner: "did you measure
the outcome of the brain-faithful downstream components, and flag components that are not brain-faithful?").

The prior cells measured who-did-what with MY OWN label-free rule (which USES the parse heads). This measures the
who-did-what patient through the ACTUAL wired brain-faithful organs and asks whether the improved parser changes
their output:
  REAL organs (PINNED-faithful, wired default-off):
    resolve_patient        hdlab.relcl_resolver -- the predict_revise drop-fill core (position + voice + filler-gap)
    hybrid_role_patient    hdlab.graded_role_assigner -- the who-did-what IDENTITY organ (Competition Model,
                           position-dominant + voice/gap OVERRIDE, over graded_competition). Owner-DONE, PINNED.
  MY rules (for comparison): AE_LABELFREE (arc-eager heads + label-free), BASE (richfeat + harmful labeler), POS.

THE STRUCTURAL FACT UNDER TEST: both real patient organs take (toks, pos, v, cands) and DO NOT consume parse
heads -- they are POSITION+VOICE organs. So a better PARSER cannot move them directly; the head-improvement is
consumed elsewhere (predicate_argument_frontend matrix-verb + PP roles; argument-attach precision). If my
head-using rule BEATS the real organ, that is a NEW opportunity: wire head-attachment as a cue into the organ.

QA-SRL science + 19c LitBank; population uses 0-based whitespace tokenization (gold/cands align 1.000). CPU
numpy, NO torch/LLM (spaCy not used). ASCII. own dir.
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
import experiments.exp_parser_multiobjective_v1 as MO
from hdlab.graded_role_assigner import hybrid_role_patient
from hdlab.relcl_resolver import resolve_patient

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_parser_through_real_organs_v1")


def organ_pick(r, tg, fn):
    """call a real organ fn(toks,pos,v,cands)->1-based idx or None; return the picked TOKEN STRING (compared to
    gold_head, consistent with the other arms)."""
    toks = r["sent"].split()
    if not toks:
        return r.get("pos_pick")
    ci = r.get("cand_idx") or []
    if len(ci) < 2:
        return r.get("pos_pick")
    pos = tg.tag(toks)
    v = r["verb_idx"] + 1                       # 0-based pop -> 1-based organ
    cands = [c + 1 for c in ci]
    try:
        idx = fn(toks, pos, v, cands)
    except Exception:
        return r.get("pos_pick")
    if idx is None or not (1 <= idx <= len(toks)):
        return r.get("pos_pick")
    return toks[idx - 1]


def run_pop(name, path, W, tg, nboot):
    rows = V1.load_pop(path); sents = sorted({r["sent"] for r in rows})
    print("[%s] %d items %d sents" % (name, len(rows), len(sents)), flush=True)
    fe = GD.frontend_parses(sents)
    ae, _ = MO.arceager_parses(sents, W, tg)

    def nonrev(r): return sum(1 for h, _ in GD.cands(r) if GD.anim(h)) < 2
    FULL = [r for r in rows if len(GD.cands(r)) >= 2 and nonrev(r)]
    HARD = [r for r in FULL if (r.get("voice") == "passive" or r.get("noncanonical"))]
    arms = {
        "POS": lambda r: r.get("pos_pick"),
        "BASE_labeler": lambda r: GD.pick_labeled(r, fe),
        "ORGAN_resolve_patient": lambda r: organ_pick(r, tg, resolve_patient),
        "ORGAN_hybrid_role": lambda r: organ_pick(r, tg, hybrid_role_patient),
        "AE_LABELFREE(mine)": lambda r: GD.pick_labelfree(r, ae),
    }
    acc = lambda fn, S: round(sum(1 for r in S if fn(r) == r["gold_head"]) / len(S), 4) if S else 0.0
    res = {"acc": {}, "deltas": {}, "n_FULL": len(FULL), "n_HARD": len(HARD)}
    for tag, S in (("FULL", FULL), ("HARD", HARD)):
        res["acc"][tag] = {a: acc(f, S) for a, f in arms.items()}
        print("  %s:" % tag, {a: res["acc"][tag][a] for a in arms}, flush=True)
    D = lambda a, b: {k: V1.paired_delta(FULL, arms[a], arms[b], nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")}
    res["deltas"] = {"AE_vs_hybrid": D("AE_LABELFREE(mine)", "ORGAN_hybrid_role"),
                     "hybrid_vs_BASE": D("ORGAN_hybrid_role", "BASE_labeler"),
                     "AE_vs_BASE": D("AE_LABELFREE(mine)", "BASE_labeler")}
    for lbl, d in res["deltas"].items():
        print("    %-16s d=%+.4f CI[%+.4f,%+.4f] frac<=0=%.3f" % (lbl, d["delta"], d["ci_lo"], d["ci_hi"], d["frac_le_0"]), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--pops", type=str, default="qa,litbank"); args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)
    out = {}
    for p in args.pops.split(","):
        out[p] = run_pop(p, {"qa": V1.QA, "litbank": V1.LB}[p], W, tg, args.nboot)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "parser_through_real_organs_v1", "results": out,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
