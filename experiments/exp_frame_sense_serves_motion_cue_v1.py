"""exp_frame_sense_serves_motion_cue_v1 -- the DOWNSTREAM LIFT (brief bar #3): does the construction cue improve
the ToM observation-cue front-end's MOTION decision on a REAL, human-tagged gold?

THE FRONT-END: hdlab/perceptual_access_ledger (integrated, the ToM observation cue). Its `_motion_signal` fires a
DEPARTURE / self-motion reading whenever the verb LEMMA is in DEIXIS_AWAY / DEIXIS_TOWARD ({go, leave, left, come,
return, ...}) -- REGARDLESS OF SENSE. So "she LEFT a note" / "he RETURNED a reply" / "an hour has GONE by" are
mis-read as departures. The ToM SOLVED named this verb-POLYSEMY as the exact residual wall. THIS cell measures the
lift from gating that decision with the glass-box frame disambiguator.

THE GOLD (real + human-tagged + NON-CIRCULAR): SemCor verb instances whose lemma is one the ledger treats as
motion (DEIXIS_AWAY u DEIXIS_TOWARD u the core self-motion verbs). Binary gold = is the human-annotated WordNet
sense the MOTION sense (lexname verb.motion)? This is exactly the ledger's decision, scored on senses a human
annotator assigned -- not on my own rule.

ARMS (same population):
  LEXICAL_STRING  the CURRENT ledger: lemma-in-DEIXIS -> motion=True ALWAYS (the un-disambiguated path = floor).
  MFS_BINARY      per-lemma most-frequent binary motion/not label from the TRAIN split (a stronger stateless floor).
  DISAMBIG        motion iff the frame disambiguator's event frame == 'motion' (the mechanism gating the ledger).
  TWIN            info-free: shuffled construction -> random frame -> random motion/not (must lose).

Reuses the cached SemCor instances from exp_frame_sense_semcor_v1 (no re-parse). Writes ONLY to
data/exp_frame_sense_serves_motion_cue_v1[/ _smoke]. NO hdlab writes. ASCII.
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
from experiments.frame_sense_disambiguator import FrameSenseDisambiguator
from experiments.perceptual_access_ledger import DEIXIS_AWAY, DEIXIS_TOWARD

ANCHOR = "frame_sense_serves_motion_cue_v1"
# the verbs the ledger treats as (potential) self-motion -- its DEIXIS sets, lemmatised, + core motion verbs.
CORE_MOTION = {"go", "leave", "come", "return", "depart", "withdraw", "arrive", "enter", "pass",
               "walk", "run", "move", "rise", "fall", "travel", "wander", "hurry", "step", "cross"}
LEDGER_VERBS = {w for w in (DEIXIS_AWAY | DEIXIS_TOWARD)} | CORE_MOTION


class _FakeTok:
    def __init__(self, lemma):
        self.lemma_ = lemma; self.pos_ = "VERB"


def load_insts(smoke):
    src = os.path.join(REPO, "data", "exp_frame_sense_semcor_v1" + ("_smoke" if smoke else ""), "instances_v6.pkl")
    if not os.path.exists(src):
        raise FileNotFoundError(f"run exp_frame_sense_semcor_v1 first to build {src}")
    insts, _ = pickle.load(open(src, "rb"))
    # keep instances of ledger-motion verbs that HAVE a motion candidate frame (so the confusion is real)
    return [it for it in insts if it["lemma"] in LEDGER_VERBS and "motion" in it["cands"]]


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
    k = min(b, c)
    return min(1.0, sum(math.comb(n, i) for i in range(k + 1)) * 0.5 ** n * 2)


def prf(pred, gold):
    """precision/recall/F1 of the POSITIVE (motion) class."""
    tp = sum(1 for p, g in zip(pred, gold) if p and g)
    fp = sum(1 for p, g in zip(pred, gold) if p and not g)
    fn = sum(1 for p, g in zip(pred, gold) if not p and g)
    P = tp / (tp + fp) if tp + fp else 0.0
    R = tp / (tp + fn) if tp + fn else 0.0
    F = 2 * P * R / (P + R) if P + R else 0.0
    return P, R, F


def run(smoke=False, seed=20260828):
    t0 = time.time()
    insts = load_insts(smoke)
    # train per-lemma binary motion MFS
    binmfs = defaultdict(lambda: [0, 0])       # lemma -> [not_motion, motion] train counts
    for it in insts:
        if it["train"]:
            binmfs[it["lemma"]][int(it["gold_frame"] == "motion")] += 1
    dis = FrameSenseDisambiguator(nlp="cached")
    test = [it for it in insts if not it["train"]]
    rng = np.random.default_rng(seed + 3)
    gold, lex, mfs, dab, twin = [], [], [], [], []
    for it in test:
        g = (it["gold_frame"] == "motion")
        gold.append(int(g))
        lex.append(1)                          # LEXICAL_STRING: ledger fires motion on every deixis verb
        cnt = binmfs.get(it["lemma"], [0, 0])
        mfs.append(int(cnt[1] >= cnt[0]))      # per-lemma binary MFS (tie -> motion)
        v = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=it["cands"], frame_feats=it["rf"], joint=True)
        dab.append(int(v.frame == "motion"))
        perm = rng.permutation(len(it["cands"]))
        vt = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=it["cands"], frame_feats=it["rf"],
                                    joint=True, shuffle_frame=perm)
        twin.append(int(vt.frame == "motion"))
    n = len(test)
    acc = lambda p: [int(a == b) for a, b in zip(p, gold)]
    out = {"n_test": n, "n_total": len(insts), "pct_motion_gold": float(np.mean(gold)) if n else 0.0,
           "by_lemma": dict(Counter(it["lemma"] for it in test))}
    for i, (k, p) in enumerate((("LEXICAL_STRING", lex), ("MFS_BINARY", mfs), ("DISAMBIG", dab), ("TWIN", twin))):
        m, lo, hi = boot(acc(p), seed + 101 * (i + 1))
        P, R, F = prf([bool(x) for x in p], [bool(x) for x in gold])
        out[k] = {"acc": [m, lo, hi], "motion_precision": P, "motion_recall": R, "motion_f1": F}
    # McNemar DISAMBIG vs LEXICAL (the un-disambiguated ledger) on ACCURACY
    b = sum(1 for i in range(n) if acc(lex)[i] and not acc(dab)[i])
    c = sum(1 for i in range(n) if acc(dab)[i] and not acc(lex)[i])
    out["mcnemar_disambig_vs_lexical"] = {"b_lex_only": b, "c_dab_only": c, "p": mcnemar(b, c)}
    lex_hi = out["LEXICAL_STRING"]["acc"][2]
    mfs_hi = out["MFS_BINARY"]["acc"][2]
    dab_lo = out["DISAMBIG"]["acc"][1]
    gates = {
        "disambig_beats_lexical_ledger_ci": bool(dab_lo > lex_hi),
        "disambig_beats_binary_mfs_ci": bool(dab_lo > mfs_hi),
        "twin_loses_ci": bool(dab_lo > out["TWIN"]["acc"][2]),
        "mcnemar_sig": bool(out["mcnemar_disambig_vs_lexical"]["p"] < 0.05 and c > b),
    }
    verdict = "HARD_PASS" if (gates["disambig_beats_lexical_ledger_ci"] and gates["twin_loses_ci"]
                              and gates["mcnemar_sig"]) else \
              ("MIDDLE_BAND" if out["DISAMBIG"]["acc"][0] > out["LEXICAL_STRING"]["acc"][0] else "HARD_FAIL")
    return {"anchor_name": ANCHOR, "verdict": verdict, "run_mode": "smoke" if smoke else "full", "seed": seed,
            "result": out, "gates": gates, "elapsed_s": round(time.time() - t0, 1),
            "ts_iso": datetime.now(timezone.utc).isoformat()}


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
    r = m["result"]
    print(f"=== {ANCHOR} ({m['run_mode']}) {m['elapsed_s']}s  n_test={r['n_test']} pct_motion_gold={r['pct_motion_gold']:.3f} ===")
    for k in ("LEXICAL_STRING", "MFS_BINARY", "DISAMBIG", "TWIN"):
        a = r[k]["acc"]
        print(f"    {k:15s} acc {a[0]:.3f} [{a[1]:.3f},{a[2]:.3f}]  motion P={r[k]['motion_precision']:.3f} "
              f"R={r[k]['motion_recall']:.3f} F1={r[k]['motion_f1']:.3f}")
    mc = r["mcnemar_disambig_vs_lexical"]
    print(f"    McNemar DISAMBIG vs LEXICAL-ledger: p={mc['p']:.2e} (b_lex={mc['b_lex_only']} c_dab={mc['c_dab_only']})")
    print("VERDICT:", m["verdict"], "GATES:", m["gates"])
    print("wrote", out_dir)


if __name__ == "__main__":
    main()
