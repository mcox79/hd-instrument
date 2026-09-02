"""exp_parser_graded_cue_integration_v1 -- is the emitted attachment CONFIDENCE a who-did-what LEVER, not just a
difficulty flag? The brain integrates cues RELIABILITY-WEIGHTED (Ernst & Banks 2002 optimal cue combination;
Competition Model cue VALIDITY, Bates & MacWhinney): trust the parse where it is confident, position where it is
not. This runs the who-did-what patient decision through the landed `graded_competition` organ (the maintained-
distribution / Bayesian posterior) with the arc-eager attachment CONFIDENCE as the reliability of the structural
cue -- the brain-faithful "parse as ONE graded cue" shape -- and asks whether reliability-weighting the head-
attach cue by its confidence BEATS the unweighted (binary) version and the hard label-free rule.

ARMS (QA-SRL science FULL/HARD + 19c LitBank):
  POS            position floor
  AE_HARD        arc-eager heads + hard label-free rule (the current best; exp_parser_multiobjective)
  GRADED_BIN     graded_competition over cues {position, attach=1/0}                 (structure unweighted)
  GRADED_CONF    graded_competition over cues {position, attach=confidence}          (RELIABILITY-weighted; the lever)
  TWIN_SHUFCONF  GRADED_CONF with the confidence SHUFFLED across candidates          (info-free -> must LOSE)
Gate: GRADED_CONF beats GRADED_BIN and AE_HARD CI-separated (confidence carries who-did-what signal), twin loses.
Reuses exp_parser_multiobjective (arceager_parses) + graded_competition. spaCy NOT used. ASCII. own dir.
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
from hdlab import graded_competition as GC

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_parser_graded_cue_integration_v1")


def graded_pick(r, ae, aeconf, mode, rng=None):
    """mode in {bin,conf,shuf}. cues: position (post-verbal=1) + attach (binary or confidence)."""
    C = GD.cands(r)
    if len(C) < 2:
        return r.get("pos_pick")
    vi = r["verb_idx"]
    cmap = aeconf.get(r["sent"], {}).get(V1._lem(r["verb"]), {})
    lf = ae.get(r["sent"], ({}, {}))[1].get(V1._lem(r["verb"]), set())
    attached = set()
    passive_any = False
    for (form, tag, pas) in lf:
        attached.add(form); passive_any = passive_any or pas
    supp_pos = []; supp_att = []
    for h, idx in C:
        # position: passive -> pre-verbal filler is the patient; else post-verbal
        if passive_any:
            supp_pos.append(1.0 if idx < vi else 0.0)
        else:
            supp_pos.append(1.0 if idx > vi else 0.0)
        att = (V1._lem(h) in attached or h in attached)
        if not att:
            supp_att.append(0.0)
        elif mode == "bin":
            supp_att.append(1.0)
        else:
            supp_att.append(float(cmap.get(V1._lem(h), cmap.get(h, 0.0))))
    if mode == "shuf" and rng is not None:
        supp_att = list(np.array(supp_att)[rng.permutation(len(supp_att))])
    if not any(supp_att):
        return r.get("pos_pick")
    win = GC.map_pick({"pos": supp_pos, "att": supp_att}, {"pos": 1.0, "att": 2.0})
    return C[win][0] if 0 <= win < len(C) else r.get("pos_pick")


def run_pop(name, path, W, tg, nboot):
    rows = V1.load_pop(path); sents = sorted({r["sent"] for r in rows})
    print("[%s] %d items %d sents" % (name, len(rows), len(sents)), flush=True)
    ae, aeconf = MO.arceager_parses(sents, W, tg)

    def nonrev(r): return sum(1 for h, _ in GD.cands(r) if GD.anim(h)) < 2
    FULL = [r for r in rows if len(GD.cands(r)) >= 2 and nonrev(r)]
    HARD = [r for r in FULL if (r.get("voice") == "passive" or r.get("noncanonical"))]
    rng = np.random.default_rng(5)
    arms = {
        "POS": lambda r: r.get("pos_pick"),
        "AE_HARD": lambda r: GD.pick_labelfree(r, ae),
        "GRADED_BIN": lambda r: graded_pick(r, ae, aeconf, "bin"),
        "GRADED_CONF": lambda r: graded_pick(r, ae, aeconf, "conf"),
        "TWIN_SHUFCONF": lambda r: graded_pick(r, ae, aeconf, "shuf", rng),
    }
    acc = lambda fn, S: round(sum(1 for r in S if fn(r) == r["gold_head"]) / len(S), 4) if S else 0.0
    res = {"acc": {}, "deltas": {}, "n_FULL": len(FULL), "n_HARD": len(HARD)}
    for tag, S in (("FULL", FULL), ("HARD", HARD)):
        res["acc"][tag] = {a: acc(f, S) for a, f in arms.items()}
        print("  %s:" % tag, {a: res["acc"][tag][a] for a in arms}, flush=True)
    D = lambda a, b: {k: V1.paired_delta(FULL, arms[a], arms[b], nboot)[k] for k in ("delta", "ci_lo", "ci_hi", "frac_le_0")}
    res["deltas"] = {"CONF_vs_BIN": D("GRADED_CONF", "GRADED_BIN"),
                     "CONF_vs_AEHARD": D("GRADED_CONF", "AE_HARD"),
                     "CONF_vs_TWIN": D("GRADED_CONF", "TWIN_SHUFCONF")}
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
        json.dump({"anchor_name": "parser_graded_cue_integration_v1", "results": out,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
