"""exp_frame_sense_serves_motion_cue_v2 -- BAR 3 (downstream lift), powered by 5-fold CV to tighten the CI.

The un-disambiguated front-end (the ToM ledger / any mined-event extractor) fires a MOTION/departure reading on
every deixis/motion verb STRING ("left", "went", "returned", "passed") regardless of sense -- so "left a note",
"went bad", "passed a law", "leave off" are false motion events. THIS cell measures the lift from the glass-box
disambiguator + reliability-gated CONTEXT cue gating that decision, on a REAL human-tagged gold (SemCor senses ->
binary is-motion), the exact decision the front-end makes.

POWER: single held-out split gave a large, paired-significant lift (0.581->0.692, McNemar p=0.003) but marginal
bootstrap CIs overlapped at n=172. This cell does 5-FOLD CROSS-VALIDATION (each instance predicted with the
context model + reliability gate trained on the OTHER 4 folds -- NO leakage) and POOLS the held-out predictions,
~5x the n, to tighten the marginal CIs.

ARMS (pooled held-out): UN_DISAMBIGUATED (verb-string -> motion always) | DISAMBIG_CTX (motion iff the
disambiguator+gated-context frame == motion) | TWIN (shuffled-label context -> info-free). MFS binary floor too.
Reports pooled accuracy [bootstrap 95% CI], motion precision/recall/F1, McNemar vs un-disambiguated + vs MFS, and
whether DISAMBIG_CTX is CI-separated (non-overlapping marginal CI) over the un-disambiguated path.

Reads instances_v6. spaCy-free (scores cached rf + ctx). Writes data/exp_frame_sense_serves_motion_cue_v2/. ASCII.
"""
from __future__ import annotations
import argparse, json, math, os, pickle, sys, time
from collections import defaultdict
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import hashlib
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.frame_sense_disambiguator import FrameSenseDisambiguator
from experiments.exp_frame_sense_context_broad_v1 import learn_context, context_scores
from experiments.exp_frame_sense_serves_motion_cue_v1 import LEDGER_VERBS, _FakeTok
from experiments.exp_frame_sense_semcor_v1 import mfs_of

ANCHOR = "frame_sense_serves_motion_cue_v2"
CACHE = os.path.join(REPO, "data", "exp_frame_sense_semcor_v1", "instances_v6.pkl")
W = 3.0
K = 5


def fold_of(it, k=K):
    return int(hashlib.md5((it["lemma"] + "|" + " ".join(it.get("ctx", [])[:6])).encode()).hexdigest(), 16) % k


def _reliability(train, cpri, model):
    per = defaultdict(lambda: [0, 0, 0])
    for it in train:
        cands = it["cands"]; pa = {c: cpri.get(it["lemma"], {}).get(c, 0.0) for c in cands}
        cz = context_scores(model, cands, it.get("ctx", []), weighted=True)
        cp = max(cands, key=lambda c: pa[c] + W * cz[c]); mp = mfs_of(cpri, it["lemma"], cands)
        per[it["lemma"]][0] += 1
        per[it["lemma"]][1] += int(cp == it["gold_frame"]); per[it["lemma"]][2] += int(mp == it["gold_frame"])
    return {lm: (v[0] >= 5 and v[1] > v[2]) for lm, v in per.items()}


def run(seed=20260828):
    t0 = time.time()
    insts, _ = pickle.load(open(CACHE, "rb"))
    sub = [it for it in insts if it["lemma"] in LEDGER_VERBS and "motion" in it["cands"]]
    dis = FrameSenseDisambiguator(nlp="cached", context_weight=W)
    gold, lex, mfsb, dab, twin = [], [], [], [], []
    for f in range(K):
        train = [it for it in sub if fold_of(it) != f]
        test = [it for it in sub if fold_of(it) == f]
        cpri = defaultdict(lambda: defaultdict(float))
        for it in train:
            cpri[it["lemma"]][it["gold_frame"]] += 1.0
        m = learn_context(train, "ctx"); rel = _reliability(train, cpri, m)
        # info-free twin: context model learned on SHUFFLED gold labels (train-only), same gate machinery
        rng = np.random.default_rng(seed + f)
        labs = [it["gold_frame"] for it in train]; rng.shuffle(labs)
        trx = [dict(it, gold_frame=labs[i]) for i, it in enumerate(train)]
        mtw = learn_context(trx, "ctx"); reltw = _reliability(trx, cpri, mtw)
        for it in test:
            g = (it["gold_frame"] == "motion"); gold.append(int(g))
            cands = it["cands"]; pri = cpri.get(it["lemma"]) or None
            lex.append(1)                                   # un-disambiguated: motion always
            mp = mfs_of(cpri, it["lemma"], cands); mfsb.append(int(mp == "motion"))
            use = rel.get(it["lemma"], False) and len(it.get("ctx", [])) >= 3
            cz = context_scores(m, cands, it.get("ctx", []), weighted=True) if use else None
            v = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=cands, frame_feats=it["rf"],
                                       joint=True, prior=pri, context_scores=cz)
            dab.append(int(v.frame == "motion"))
            uset = reltw.get(it["lemma"], False) and len(it.get("ctx", [])) >= 3
            czt = context_scores(mtw, cands, it.get("ctx", []), weighted=True) if uset else None
            vt = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=cands, frame_feats=it["rf"],
                                        joint=True, prior=pri, context_scores=czt)
            twin.append(int(vt.frame == "motion"))
    gold = np.array(gold); n = len(gold)

    def boot(pred, s):
        ok = (np.array(pred) == gold).astype(float); r = np.random.default_rng(s)
        mm = ok[r.integers(0, n, size=(3000, n))].mean(1)
        return round(float(ok.mean()), 3), round(float(np.percentile(mm, 2.5)), 3), round(float(np.percentile(mm, 97.5)), 3)

    def prf(pred):
        p = np.array(pred).astype(bool); gg = gold.astype(bool)
        tp = int((p & gg).sum()); fp = int((p & ~gg).sum()); fn = int((~p & gg).sum())
        P = tp / (tp + fp) if tp + fp else 0.0; R = tp / (tp + fn) if tp + fn else 0.0
        return round(P, 3), round(R, 3), round(2 * P * R / (P + R), 3) if P + R else 0.0

    def mcp(a, bb):
        aa = (np.array(a) == gold); b2 = (np.array(bb) == gold)
        x = int((aa & ~b2).sum()); y = int((~aa & b2).sum()); nn = x + y
        return {"b": x, "c": y, "p": round(min(1.0, sum(math.comb(nn, i) for i in range(min(x, y) + 1)) * 0.5 ** nn * 2) if nn else 1.0, 6)}
    out = {"anchor_name": ANCHOR, "n": n, "pct_motion_gold": round(float(gold.mean()), 3), "K": K}
    for name, pred in (("UN_DISAMBIGUATED", lex), ("MFS_BINARY", mfsb), ("DISAMBIG_CTX", dab), ("TWIN", twin)):
        acc = boot(pred, hash(name) % 999 if False else {"UN_DISAMBIGUATED": 11, "MFS_BINARY": 22, "DISAMBIG_CTX": 33, "TWIN": 44}[name])
        P, R, F = prf(pred)
        out[name] = {"acc": acc, "motion_P": P, "motion_R": R, "motion_F1": F}
    out["mcnemar_disambig_vs_undisambig"] = mcp(lex, dab)
    out["mcnemar_disambig_vs_mfs"] = mcp(mfsb, dab)
    out["mcnemar_twin_vs_undisambig"] = mcp(lex, twin)
    dab_lo = out["DISAMBIG_CTX"]["acc"][1]; lex_hi = out["UN_DISAMBIGUATED"]["acc"][2]; mfs_hi = out["MFS_BINARY"]["acc"][2]
    out["gates"] = {
        "ci_separated_over_undisambiguated": bool(dab_lo > lex_hi),
        "ci_separated_over_mfs": bool(dab_lo > mfs_hi),
        "mcnemar_sig_vs_undisambig": bool(out["mcnemar_disambig_vs_undisambig"]["p"] < 0.05
                                          and out["mcnemar_disambig_vs_undisambig"]["c"] > out["mcnemar_disambig_vs_undisambig"]["b"]),
        "twin_loses": bool(out["TWIN"]["acc"][0] < out["DISAMBIG_CTX"]["acc"][0]),
    }
    out["verdict"] = "HARD_PASS" if (out["gates"]["ci_separated_over_undisambiguated"] and out["gates"]["twin_loses"]) else \
                     ("PAIRED_SIG" if out["gates"]["mcnemar_sig_vs_undisambig"] else "MIDDLE_BAND")
    out["elapsed_s"] = round(time.time() - t0, 1); out["ts_iso"] = datetime.now(timezone.utc).isoformat()
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--self-test", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full"); ap.add_argument("--seed", type=int, default=20260828); ap.parse_args()
    od = os.path.join(REPO, "data", f"exp_{ANCHOR}"); os.makedirs(od, exist_ok=True)
    m = run()
    json.dump(m, open(os.path.join(od, "metrics.json.tmp"), "w", encoding="ascii"), indent=2)
    os.replace(os.path.join(od, "metrics.json.tmp"), os.path.join(od, "metrics.json"))
    print(f"=== {ANCHOR} {m['elapsed_s']}s  {K}-fold CV pooled  n={m['n']} pct_motion={m['pct_motion_gold']} ===")
    for k in ("UN_DISAMBIGUATED", "MFS_BINARY", "DISAMBIG_CTX", "TWIN"):
        a = m[k]; print(f"    {k:16s} acc {a['acc']}  motion P/R/F1={a['motion_P']}/{a['motion_R']}/{a['motion_F1']}")
    print(f"    McNemar DISAMBIG vs un-disambiguated: {m['mcnemar_disambig_vs_undisambig']}")
    print(f"    McNemar DISAMBIG vs MFS-binary:       {m['mcnemar_disambig_vs_mfs']}")
    print("    GATES:", m["gates"]); print("    VERDICT:", m["verdict"]); print("wrote", od)


if __name__ == "__main__":
    main()
