"""exp_frame_sense_confusion_pairs_v1 -- the FAIR test of the TWO DOMINANT CONFUSIONS the brief names, on real
SemCor human-tagged senses, as BINARY decisions where the argument-structure construction is the diagnostic cue.

Motivation: the coarse-frame multiclass eval (exp_frame_sense_semcor_v1) showed WordNet LEXNAME fights the
event-frame taxonomy, and the aggregate is swamped by non-confusion verbs. THIS cell isolates the two confusions
as the BINARY decisions the front-ends actually need, on the EXEMPLAR verbs of each confusion, scored on human
SemCor senses:
  MOTION confusion (motion vs not): self-motion verbs (leave/return/come/go/...). Binary gold = lexname verb.motion.
  PROP   confusion (propositional vs not): perception/report verbs (observe/note/see/find/hear/...). Binary gold =
         lexname in {verb.communication, verb.cognition}.

ARMS: DISAMBIG (frame==motion / frame in prop) vs LEXICAL (the un-disambiguated front-end: always-motion for the
motion set / the ccomp-only cue for prop) vs MFS_BINARY (per-lemma majority) vs TWIN (shuffled construction).
Populations: CURATED exemplar verbs (named below) and AUTO (verb_confusions-selected -- honest, over-inclusive).

Reads the cached v3 SemCor instances. Writes ONLY to data/exp_frame_sense_confusion_pairs_v1[/ _smoke]. NO hdlab.
"""
from __future__ import annotations
import argparse, json, math, os, pickle, sys, time
from collections import defaultdict, Counter
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.frame_sense_disambiguator import FrameSenseDisambiguator, verb_confusions

ANCHOR = "frame_sense_confusion_pairs_v1"
MD_VERBS = {"leave", "return", "come", "go", "arrive", "depart", "withdraw", "enter", "exit", "retire",
            "pass", "rise", "fall", "step", "slip", "move", "walk", "run", "climb", "descend", "flee"}
PROP_VERBS = {"observe", "note", "see", "find", "hear", "notice", "remark", "realize", "discover",
              "declare", "admit", "understand", "perceive", "learn", "watch", "read", "announce", "reply"}
PROP = {"communication", "cognition"}


class _FakeTok:
    def __init__(self, lemma):
        self.lemma_ = lemma; self.pos_ = "VERB"


def load_insts(smoke):
    src = os.path.join(REPO, "data", "exp_frame_sense_semcor_v1" + ("_smoke" if smoke else ""), "instances_v6.pkl")
    insts, _ = pickle.load(open(src, "rb"))
    return insts


def boot(v, seed, nb=2000):
    a = np.asarray(v, float)
    if len(a) == 0:
        return 0.0, 0.0, 0.0
    r = np.random.default_rng(seed)
    m = a[r.integers(0, len(a), size=(nb, len(a)))].mean(1)
    return float(a.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, sum(math.comb(n, i) for i in range(min(b, c) + 1)) * 0.5 ** n * 2)


def eval_confusion(insts, dis, seed, which, curated):
    """which in {'motion','prop'}. curated=True -> exemplar verb list; else AUTO via verb_confusions."""
    if which == "motion":
        pos = lambda it: it["gold_frame"] == "motion"
        target = "motion"
        keep = (lambda it: it["lemma"] in MD_VERBS) if curated else \
               (lambda it: "md" in verb_confusions(it["cands"]) and "motion" in it["cands"])
        naive = lambda it: 1                                  # the un-disambiguated front-end: always motion
    else:
        pos = lambda it: it["gold_frame"] in PROP
        target = "prop"
        keep = (lambda it: it["lemma"] in PROP_VERBS) if curated else \
               (lambda it: "prop" in verb_confusions(it["cands"]))
        naive = lambda it: int(it["rf"].has_ccomp)            # un-disambiguated: the raw ccomp cue only
    sub = [it for it in insts if keep(it) and (set(it["cands"]) & (PROP if which == "prop" else {"motion"}))]
    train = [it for it in sub if it["train"]]
    test = [it for it in sub if not it["train"]]
    binmfs = defaultdict(lambda: [0, 0])
    for it in train:
        binmfs[it["lemma"]][int(pos(it))] += 1
    rng = np.random.default_rng(seed + 9)
    gold, dab, lex, mfs, twin = [], [], [], [], []
    for it in test:
        g = pos(it); gold.append(int(g))
        cnt = binmfs.get(it["lemma"], [0, 0])
        mfs.append(int(cnt[1] >= cnt[0]))
        lex.append(int(naive(it)))
        v = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=it["cands"], frame_feats=it["rf"], joint=True)
        pred = (v.frame == "motion") if which == "motion" else (v.frame in PROP)
        dab.append(int(pred))
        perm = rng.permutation(len(it["cands"]))
        vt = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=it["cands"], frame_feats=it["rf"],
                                    joint=True, shuffle_frame=perm)
        predt = (vt.frame == "motion") if which == "motion" else (vt.frame in PROP)
        twin.append(int(predt))
    n = len(test)
    acc = lambda p: [int(a == b) for a, b in zip(p, gold)]

    def prf(p):
        tp = sum(1 for a, g in zip(p, gold) if a and g); fp = sum(1 for a, g in zip(p, gold) if a and not g)
        fn = sum(1 for a, g in zip(p, gold) if not a and g)
        P = tp / (tp + fp) if tp + fp else 0.0; R = tp / (tp + fn) if tp + fn else 0.0
        return round(P, 3), round(R, 3), round(2 * P * R / (P + R), 3) if P + R else 0.0
    out = {"n_test": n, "pct_pos_gold": round(float(np.mean(gold)), 3) if n else 0.0,
           "lemmas": dict(Counter(it["lemma"] for it in test).most_common(10))}
    arms = {"DISAMBIG": dab, "LEXICAL": lex, "MFS_BINARY": mfs, "TWIN": twin}
    for i, k in enumerate(("DISAMBIG", "LEXICAL", "MFS_BINARY", "TWIN")):
        m, lo, hi = boot(acc(arms[k]), seed + 101 * (i + 1))
        out[k] = {"acc": [round(m, 3), round(lo, 3), round(hi, 3)], "prf_pos": prf(arms[k])}
    # McNemar DISAMBIG vs the strongest of {LEXICAL, MFS_BINARY}
    strong = "MFS_BINARY" if out["MFS_BINARY"]["acc"][0] >= out["LEXICAL"]["acc"][0] else "LEXICAL"
    sp = arms[strong]
    b = sum(1 for i in range(n) if acc(sp)[i] and not acc(dab)[i])
    c = sum(1 for i in range(n) if acc(dab)[i] and not acc(sp)[i])
    out["mcnemar_vs_strongest"] = {"floor": strong, "b_floor_only": b, "c_dab_only": c, "p": mcnemar(b, c)}
    out["gates"] = {
        "beats_strongest_floor_ci": bool(out["DISAMBIG"]["acc"][1] > max(out["LEXICAL"]["acc"][2], out["MFS_BINARY"]["acc"][2])),
        "twin_loses_ci": bool(out["DISAMBIG"]["acc"][1] > out["TWIN"]["acc"][2]),
        "mcnemar_sig": bool(out["mcnemar_vs_strongest"]["p"] < 0.05 and c > b),
    }
    return out


def run(smoke=False, seed=20260828):
    t0 = time.time()
    insts = load_insts(smoke)
    dis = FrameSenseDisambiguator(nlp="cached")
    res = {}
    for which in ("motion", "prop"):
        for cur in (True, False):
            res[f"{which}_{'curated' if cur else 'auto'}"] = eval_confusion(insts, dis, seed, which, cur)
    any_pass = any(r["gates"]["beats_strongest_floor_ci"] and r["gates"]["twin_loses_ci"] for r in res.values())
    return {"anchor_name": ANCHOR, "verdict": "HARD_PASS" if any_pass else "MIDDLE_BAND_OR_TIE",
            "run_mode": "smoke" if smoke else "full", "seed": seed, "results": res,
            "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full"); ap.add_argument("--seed", type=int, default=20260828)
    args = ap.parse_args()
    smoke = bool(args.smoke) or args.self_test or args.mode == "smoke"
    out_dir = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if smoke else ""))
    os.makedirs(out_dir, exist_ok=True)
    m = run(smoke=smoke, seed=args.seed)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    json.dump(m, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print(f"=== {ANCHOR} ({m['run_mode']}) {m['elapsed_s']}s ===")
    for key, r in m["results"].items():
        print(f"[{key}] n={r['n_test']} pct_pos={r['pct_pos_gold']} lemmas={list(r['lemmas'])[:6]}")
        for k in ("DISAMBIG", "LEXICAL", "MFS_BINARY", "TWIN"):
            print(f"    {k:11s} acc {r[k]['acc']}  P/R/F1(pos)={r[k]['prf_pos']}")
        mc = r["mcnemar_vs_strongest"]
        print(f"    McNemar vs {mc['floor']}: p={mc['p']:.2e} (b={mc['b_floor_only']} c={mc['c_dab_only']}) GATES={r['gates']}")
    print("VERDICT:", m["verdict"]); print("wrote", out_dir)


if __name__ == "__main__":
    main()
