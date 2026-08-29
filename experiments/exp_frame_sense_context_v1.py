"""exp_frame_sense_context_v1 -- the brain's ACTUAL lever, tested fairly: does CONTEXT (reordered access) let the
disambiguator recover the SUBORDINATE senses MFS misses, beating MFS (c>b) with override precision > 0.5?

The brain disambiguates verb sense by CONTEXT-reordered lexical access (Duffy/Morris/Rayner): the prior discourse
primes the sense before the verb. My earlier cues used only the LOCAL argument frame -- a thin slice. This cell
adds a real, learned DISTRIBUTIONAL CONTEXT model P(coarse_frame | context content-words), the computational
model behind the landed `context_override_frequency_wsd` win (which beat MFS on subordinate SemCor items).

FAIR TEST (one variable, no leakage): the SAME train-MFS prior is injected into every arm and used for the MFS
floor; the context model is learned on TRAIN only; scored on TEST. Reported per population (motion/prop x
curated/auto): full accuracy, SUBORDINATE recovery (gold != train-MFS), and the decisive OVERRIDE PRECISION
c/(b+c) -- of the cases where an arm disagrees with MFS, how often is the arm right. >0.5 => beats MFS.

ARMS: MFS | CONSTR (construction+idiom+fit, matched prior) | CONTEXT (prior + learned context) |
CONSTR+CONTEXT (the full brain-faithful combination). Reads instances_v5 (with cached `ctx`). ASCII. No hdlab.
"""
from __future__ import annotations
import json, math, os, pickle, sys, time
from collections import defaultdict
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.frame_sense_disambiguator import FrameSenseDisambiguator, verb_confusions
from experiments.exp_frame_sense_confusion_pairs_v1 import MD_VERBS, PROP_VERBS, PROP, _FakeTok

CACHE = os.path.join(REPO, "data", "exp_frame_sense_semcor_v1", "instances_v6.pkl")
ALPHA = 0.1


def learn_context(train):
    """P(word | frame) counts over context content-lemmas, + frame marginals. Learned on TRAIN only."""
    wf = defaultdict(lambda: defaultdict(float))   # frame -> word -> count
    ftot = defaultdict(float)
    vocab = set()
    for it in train:
        f = it["gold_frame"]
        for w in it.get("ctx", []):
            wf[f][w] += 1.0
            ftot[f] += 1.0
            vocab.add(w)
    return {"wf": {f: dict(d) for f, d in wf.items()}, "ftot": dict(ftot), "V": max(1, len(vocab))}


def context_scores(model, cands, ctx):
    """log-likelihood sum_w log P(w|frame) per candidate frame (add-alpha), z-scored across the candidates."""
    wf, ftot, V = model["wf"], model["ftot"], model["V"]
    raw = []
    for f in cands:
        tot = ftot.get(f, 0.0)
        s = 0.0
        for w in ctx:
            c = wf.get(f, {}).get(w, 0.0)
            s += math.log((c + ALPHA) / (tot + ALPHA * V))
        raw.append(s)
    raw = np.array(raw, float)
    if len(raw) < 2 or raw.std() < 1e-9:
        return {c: 0.0 for c in cands}
    z = (raw - raw.mean()) / (raw.std() + 1e-9)
    return {c: float(z[i]) for i, c in enumerate(cands)}


def mcnemar_p(b, c):
    n = b + c
    return min(1.0, sum(math.comb(n, i) for i in range(min(b, c) + 1)) * 0.5 ** n * 2) if n else 1.0


def eval_pop(insts, dis, which, curated, w_ctx=1.0):
    target_is = (lambda f: f == "motion") if which == "motion" else (lambda f: f in PROP)
    fam = "md" if which == "motion" else "prop"
    keyset = {"motion"} if which == "motion" else PROP
    if curated:
        verbs = MD_VERBS if which == "motion" else PROP_VERBS
        sub = [it for it in insts if it["lemma"] in verbs and (set(it["cands"]) & keyset)]
    else:
        sub = [it for it in insts if fam in verb_confusions(it["cands"]) and (set(it["cands"]) & keyset)]
    train = [it for it in sub if it["train"]]
    test = [it for it in sub if not it["train"]]
    cpri = defaultdict(lambda: defaultdict(float))
    for it in train:
        cpri[it["lemma"]][it["gold_frame"]] += 1.0
    cpri = {lm: dict(d) for lm, d in cpri.items()}
    ctxmodel = learn_context(train)

    def mfs_pred(it):
        d = cpri.get(it["lemma"], {})
        return target_is(max(it["cands"], key=lambda c: d.get(c, 0.0))) if d else target_is(it["cands"][0])

    arms = {"MFS": [], "CONSTR": [], "CONTEXT": [], "CONSTR_CONTEXT": []}
    gold = []
    for it in test:
        gold.append(target_is(it["gold_frame"]))
        cands = it["cands"]
        pri = cpri.get(it["lemma"]) or None
        arms["MFS"].append(mfs_pred(it))
        v = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=cands, frame_feats=it["rf"],
                                   joint=True, prior=pri)
        arms["CONSTR"].append(target_is(v.frame))
        cz = context_scores(ctxmodel, cands, it.get("ctx", []))
        prio = pri or {}
        prior_arr = {c: prio.get(c, 0.0) for c in cands}
        # CONTEXT arm: prior + context (no construction)
        cpick = max(cands, key=lambda c: prior_arr[c] + w_ctx * cz[c])
        arms["CONTEXT"].append(target_is(cpick))
        # CONSTR+CONTEXT: proper ACTIVATION-level combination (construction + idiom + fit + context as one graded
        # competition), via the disambiguator's first-class context cue (no softmax-of-softmax).
        v2 = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=cands, frame_feats=it["rf"],
                                    joint=True, prior=pri, context_scores=cz)
        arms["CONSTR_CONTEXT"].append(target_is(v2.frame))
    gold = np.array(gold)
    mfs = np.array(arms["MFS"])
    subord = mfs != gold
    out = {"n": len(gold), "n_subordinate": int(subord.sum()), "pct_subordinate": round(float(subord.mean()), 3)}
    for arm in arms:
        p = np.array(arms[arm])
        b = int(((mfs == gold) & (p != gold)).sum())
        c = int(((mfs != gold) & (p == gold)).sum())
        prec = c / (b + c) if (b + c) else float("nan")
        out[arm] = {"acc": round(float((p == gold).mean()), 3),
                    "subord_recovery": round(float((p[subord] == gold[subord]).mean()) if subord.sum() else 0.0, 3),
                    "override_precision": round(prec, 3) if (b + c) else None,
                    "b_mfsonly": b, "c_armonly": c, "mcnemar_p": round(mcnemar_p(b, c), 4)}
    return out


def run(w_ctx=1.0):
    t0 = time.time()
    insts, _ = pickle.load(open(CACHE, "rb"))
    dis = FrameSenseDisambiguator(nlp="cached", context_weight=w_ctx)
    pops = {}
    for which in ("motion", "prop"):
        for cur in (True, False):
            pops[f"{which}_{'curated' if cur else 'auto'}"] = eval_pop(insts, dis, which, cur, w_ctx=w_ctx)
    return {"anchor_name": "frame_sense_context_v1", "w_ctx": w_ctx, "pops": pops,
            "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}


def main():
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--w", type=float, default=1.0); a = ap.parse_args()
    od = os.path.join(REPO, "data", "exp_frame_sense_context_v1")
    os.makedirs(od, exist_ok=True)
    m = run(w_ctx=a.w)
    json.dump(m, open(os.path.join(od, "metrics.json.tmp"), "w", encoding="ascii"), indent=2)
    os.replace(os.path.join(od, "metrics.json.tmp"), os.path.join(od, "metrics.json"))
    print(f"=== frame_sense_context_v1 (w_ctx={m['w_ctx']}) {m['elapsed_s']}s ===")
    for pop, r in m["pops"].items():
        print(f"\n[{pop}] n={r['n']} subordinate(MFS-wrong)={r['n_subordinate']} ({r['pct_subordinate']})")
        print(f"    {'arm':16s} {'acc':>6s} {'sub_rec':>8s} {'ovr_prec':>9s}  McNemar(b,c,p)")
        for arm in ("MFS", "CONSTR", "CONTEXT", "CONSTR_CONTEXT"):
            a_ = r[arm]
            beat = "  <== BEATS MFS" if (a_["c_armonly"] > a_["b_mfsonly"] and a_["mcnemar_p"] < 0.05) else ""
            print(f"    {arm:16s} {a_['acc']:6.3f} {a_['subord_recovery']:8.3f} {str(a_['override_precision']):>9s}  "
                  f"b={a_['b_mfsonly']} c={a_['c_armonly']} p={a_['mcnemar_p']:.3f}{beat}")
    print("\nwrote", od)


if __name__ == "__main__":
    main()
