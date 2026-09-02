"""exp_predarg_frontend_organ_v1 -- measure the HEAD-CONSUMING brain-faithful organ's outcome with the improved
parser (owner: "did you measure the outcome of the brain-faithful downstream components?"). The real who-did-what
PATIENT organ is head-INDEPENDENT (exp_parser_through_real_organs_v1: hybrid_role_patient/resolve_patient are
position+voice, the parser does not move them). The parser's heads are actually consumed by
`hdlab.predicate_argument_frontend`: matrix_verbs (root+coordination -> which verb gets the who-did-what frame)
and _pp_args_for_verb (PP/oblique roles -> recipient/goal, the world-state input). This measures THOSE organ
outputs on UD-EWT test with arc-eager (rich) heads vs the LIVE richfeat heads vs GOLD heads (oracle), scored
against gold. Gold UPOS is held fixed so the ONE variable is the parse HEADS.

  matrix-verb F1   : predicted matrix-verb set (per sentence) vs gold matrix-verb set.
  pp-arg F1        : for gold matrix verbs, predicted (prep,obj) oblique set vs gold (prep,obj) set.
CPU numpy only, NO torch/spaCy/LLM. ASCII. own dir.
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
import experiments.exp_arceager_parser_operator_v1 as AEO
from hdlab.predicate_argument_frontend import matrix_verbs, _pp_args_for_verb

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_predarg_frontend_organ_v1")


def gold_heads(s):
    return {t[0]: t[3] for t in s}


def prf(pred_set, gold_set):
    if not pred_set and not gold_set:
        return (1.0, 1.0, 1.0)
    tp = len(pred_set & gold_set)
    p = tp / len(pred_set) if pred_set else 0.0
    r = tp / len(gold_set) if gold_set else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return (p, r, f)


def boot_delta(a, b, nboot=2000, seed=17):
    """paired bootstrap over sentences of mean(a)-mean(b), a/b aligned per-sentence F1 lists."""
    a = np.asarray(a, float); b = np.asarray(b, float); m = min(len(a), len(b)); a = a[:m]; b = b[:m]
    rng = np.random.default_rng(seed); base = float(a.mean() - b.mean()); ds = []
    for _ in range(nboot):
        idx = rng.integers(0, m, m); ds.append(float(a[idx].mean() - b[idx].mean()))
    ds = np.array(ds)
    return {"delta": round(base, 4), "ci_lo": round(float(np.percentile(ds, 2.5)), 4),
            "ci_hi": round(float(np.percentile(ds, 97.5)), 4), "frac_le_0": round(float((ds <= 0).mean()), 3)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--nboot", type=int, default=2000); args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.arc_parser import ArcParser
    W = AEO.load_model(AEO.MODEL_PATH)
    rich = ArcParser.load(os.path.join(_REPO, "data", "frontend_assets", "arc_parser_richfeat_ud_ewt.npz"))
    test = [s for s in AEO._load_ud_feats("test") if 1 <= len(s) <= AEO.MAXLEN]
    print("[data] UD-EWT test sents=%d" % len(test), flush=True)

    def ae_h(toks, pos):
        h, _, _ = AEO.parse_with_conf(toks, pos, W); return h

    def ri_h(toks, pos):
        return rich.parse(toks, pos).heads

    mv = {"arc_eager": [], "richfeat": []}
    pp = {"arc_eager": [], "richfeat": []}
    for s in test:
        toks = [t[1] for t in s]; upos = [t[2] for t in s]
        gh = gold_heads(s)
        gmv = set(matrix_verbs(toks, upos, gh))
        gpp = set()
        for v in gmv:
            for pr, ob in _pp_args_for_verb(toks, upos, gh, v):
                gpp.add((v, pr, ob))
        for nm, hf in (("arc_eager", ae_h), ("richfeat", ri_h)):
            h = hf(toks, upos)
            pmv = set(matrix_verbs(toks, upos, h))
            mv[nm].append(prf(pmv, gmv)[2])
            ppset = set()
            for v in gmv:                                  # PP-args scored on the gold matrix verbs
                for pr, ob in _pp_args_for_verb(toks, upos, h, v):
                    ppset.add((v, pr, ob))
            pp[nm].append(prf(ppset, gpp)[2])
    res = {"matrix_verb_F1": {nm: round(float(np.mean(v)), 4) for nm, v in mv.items()},
           "pp_arg_F1": {nm: round(float(np.mean(v)), 4) for nm, v in pp.items()},
           "matrix_verb_delta_ae_vs_rich": boot_delta(mv["arc_eager"], mv["richfeat"], args.nboot),
           "pp_arg_delta_ae_vs_rich": boot_delta(pp["arc_eager"], pp["richfeat"], args.nboot),
           "n": len(test)}
    print("\n=== predicate_argument_frontend organ output (gold UPOS; ONE var = parse heads) ===", flush=True)
    print("  matrix-verb F1: arc_eager=%.4f richfeat=%.4f  delta=%+.4f CI[%+.4f,%+.4f] frac<=0=%.3f" % (
        res["matrix_verb_F1"]["arc_eager"], res["matrix_verb_F1"]["richfeat"],
        res["matrix_verb_delta_ae_vs_rich"]["delta"], res["matrix_verb_delta_ae_vs_rich"]["ci_lo"],
        res["matrix_verb_delta_ae_vs_rich"]["ci_hi"], res["matrix_verb_delta_ae_vs_rich"]["frac_le_0"]), flush=True)
    print("  pp-arg   F1: arc_eager=%.4f richfeat=%.4f  delta=%+.4f CI[%+.4f,%+.4f] frac<=0=%.3f" % (
        res["pp_arg_F1"]["arc_eager"], res["pp_arg_F1"]["richfeat"],
        res["pp_arg_delta_ae_vs_rich"]["delta"], res["pp_arg_delta_ae_vs_rich"]["ci_lo"],
        res["pp_arg_delta_ae_vs_rich"]["ci_hi"], res["pp_arg_delta_ae_vs_rich"]["frac_le_0"]), flush=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "predarg_frontend_organ_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
