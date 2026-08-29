"""exp_frame_sense_bakeoff_v1 -- controlled bakeoff of the three optimization routes on the two dominant
confusions. Toggles each cue on the SAME cached SemCor gold and reports whether it lets DISAMBIG beat the
strongest floor (per-lemma MFS) CI-separated (bar 2) with the info-free twin losing.

Variants: BASE (construction cue only) | +IDIOM (stored-unit lexicon) | +FIT (sense-keyed selectional pref) |
+BOTH. Reads data/exp_frame_sense_semcor_v1/instances_v6.pkl. Writes data/exp_frame_sense_bakeoff_v1/. ASCII.
"""
from __future__ import annotations
import json, os, pickle, sys, time
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.frame_sense_disambiguator import FrameSenseDisambiguator, _IDIOM, _SELPREF
from experiments.exp_frame_sense_confusion_pairs_v1 import eval_confusion

POPS = [("motion", True), ("motion", False), ("prop", True), ("prop", False)]


def run(seed=20260828):
    t0 = time.time()
    insts, _ = pickle.load(open(os.path.join(REPO, "data", "exp_frame_sense_semcor_v1", "instances_v6.pkl"), "rb"))
    variants = {"BASE": dict(use_idioms=False, use_indep_fit=False)}
    if _IDIOM is not None:
        variants["+IDIOM"] = dict(use_idioms=True, use_indep_fit=False)
    if _SELPREF is not None:
        variants["+FIT"] = dict(use_idioms=False, use_indep_fit=True)
    if _IDIOM is not None and _SELPREF is not None:
        variants["+BOTH"] = dict(use_idioms=True, use_indep_fit=True)
    out = {}
    for vname, kw in variants.items():
        dis = FrameSenseDisambiguator(nlp="cached", **kw)
        out[vname] = {}
        for which, cur in POPS:
            key = f"{which}_{'curated' if cur else 'auto'}"
            out[vname][key] = eval_confusion(insts, dis, seed, which, cur)
    return {"anchor_name": "frame_sense_bakeoff_v1", "variants": out,
            "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}


def main():
    od = os.path.join(REPO, "data", "exp_frame_sense_bakeoff_v1")
    os.makedirs(od, exist_ok=True)
    m = run()
    tmp = os.path.join(od, "metrics.json.tmp")
    json.dump(m, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(od, "metrics.json"))
    print(f"=== frame_sense_bakeoff_v1 {m['elapsed_s']}s  variants={list(m['variants'])} ===")
    for key, _c in [(f"{w}_{'curated' if cur else 'auto'}", None) for w, cur in POPS]:
        print(f"\n[{key}]")
        # header row
        anyv = next(iter(m["variants"].values()))
        r0 = anyv[key]
        print(f"    floors: per-lemma MFS {r0['MFS_BINARY']['acc']}  un-disambiguated {r0['LEXICAL']['acc']}  (n={r0['n_test']}, pct_pos={r0['pct_pos_gold']})")
        for vname, res in m["variants"].items():
            r = res[key]
            g = r["gates"]
            tag = "BEATS-MFS-CI" if g["beats_strongest_floor_ci"] else ("beats-floor" if r["DISAMBIG"]["acc"][0] > r["MFS_BINARY"]["acc"][0] else "ties/loses")
            print(f"    {vname:8s} DISAMBIG {r['DISAMBIG']['acc']}  P/R/F1={r['DISAMBIG']['prf_pos']}  twin={r['TWIN']['acc'][0]:.3f}  McNemar_p={r['mcnemar_vs_strongest']['p']:.2e} -> {tag}")
    print("\nwrote", od)


if __name__ == "__main__":
    main()
