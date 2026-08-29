"""exp_frame_sense_context_broad_v1 -- STRENGTHEN the context win: (A) does it GENERALIZE from the motion binary
to the BROAD coarse-frame task (all frame-alternating verbs, multiclass)? and (B) does a brain-faithful
DIAGNOSTIC-WORD-WEIGHTED context model beat the flat bag (the #1a post-mortem: the brain weights the
discriminative context words, not a mean/flat bag)?

FAIR: matched train-MFS prior in every arm; context learned on TRAIN only; scored on the frame_alt TEST split
(multiclass coarse frame). Arms: MFS | CONSTR (construction+idiom+fit) | +CTX_BAG | +CTX_WEIGHTED. Decisive
metrics: full accuracy, subordinate recovery (gold != MFS), OVERRIDE PRECISION c/(b+c), McNemar vs MFS.

The DIAGNOSTIC weight of a context word w = 1 - normalized_entropy(P(frame|w)) -> a word that strongly predicts
one frame (low entropy) is weighted up; a bland word (flat over frames) is weighted down. Learned on TRAIN.

Reads instances_v6. Writes data/exp_frame_sense_context_broad_v1/. ASCII. NO hdlab writes.
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
from experiments.frame_sense_disambiguator import FrameSenseDisambiguator
from experiments.exp_frame_sense_semcor_v1 import is_frame_alternating, train_prior, mfs_of, _FakeTok

CACHE = os.path.join(REPO, "data", "exp_frame_sense_semcor_v1", "instances_v6.pkl")
ALPHA = 0.1


def learn_context(train, field="ctx"):
    wf = defaultdict(lambda: defaultdict(float)); ftot = defaultdict(float); vocab = set()
    wframe = defaultdict(lambda: defaultdict(float))     # word -> frame -> count (for diagnostic weight)
    for it in train:
        f = it["gold_frame"]
        for w in it.get(field, []):
            wf[f][w] += 1.0; ftot[f] += 1.0; vocab.add(w); wframe[w][f] += 1.0
    # diagnostic weight per word = 1 - normalized entropy of P(frame|word)
    diag = {}
    for w, fr in wframe.items():
        tot = sum(fr.values())
        if tot < 3:                                      # too rare to trust
            diag[w] = 0.0; continue
        ps = np.array([v / tot for v in fr.values()])
        h = -(ps * np.log(ps + 1e-12)).sum() / math.log(max(2, len(fr)))
        diag[w] = float(1.0 - h)
    return {"wf": {f: dict(d) for f, d in wf.items()}, "ftot": dict(ftot),
            "V": max(1, len(vocab)), "diag": diag}


def context_scores(model, cands, ctx, weighted=False):
    wf, ftot, V, diag = model["wf"], model["ftot"], model["V"], model["diag"]
    raw = []
    for f in cands:
        tot = ftot.get(f, 0.0); s = 0.0
        for w in ctx:
            c = wf.get(f, {}).get(w, 0.0)
            ll = math.log((c + ALPHA) / (tot + ALPHA * V))
            s += (diag.get(w, 0.0) if weighted else 1.0) * ll
        raw.append(s)
    raw = np.array(raw, float)
    if len(raw) < 2 or raw.std() < 1e-9:
        return {c: 0.0 for c in cands}
    z = (raw - raw.mean()) / (raw.std() + 1e-9)
    return {c: float(z[i]) for i, c in enumerate(cands)}


def mcnemar_p(b, c):
    n = b + c
    return min(1.0, sum(math.comb(n, i) for i in range(min(b, c) + 1)) * 0.5 ** n * 2) if n else 1.0


def run(w_ctx=3.0):
    t0 = time.time()
    insts, _ = pickle.load(open(CACHE, "rb"))
    sub = [it for it in insts if is_frame_alternating(it["lemma"])]     # BROAD: all frame-alternating verbs
    train = [it for it in sub if it["train"]]; test = [it for it in sub if not it["train"]]
    cpri = train_prior(sub)
    m = learn_context(train, "ctx")
    disB = FrameSenseDisambiguator(nlp="cached", context_weight=w_ctx)
    # PER-VERB CONTEXT RELIABILITY GATE (precision-weighting, learned on TRAIN, no leakage): for each verb, does
    # the context cue beat MFS on the TRAIN split? Trust context on test ONLY for verbs where it does. This is the
    # brain-faithful fix -- the reader learns which verbs' senses are context-cued (motion) vs not (taxonomy/idiom).
    per = defaultdict(lambda: [0, 0, 0])               # lemma -> [n, ctx_correct, mfs_correct] on train
    for it in train:
        cands = it["cands"]; pa = {c: cpri.get(it["lemma"], {}).get(c, 0.0) for c in cands}
        czw = context_scores(m, cands, it.get("ctx", []), weighted=True)
        ctxp = max(cands, key=lambda c: pa[c] + w_ctx * czw[c]); mfsp = mfs_of(cpri, it["lemma"], cands)
        per[it["lemma"]][0] += 1
        per[it["lemma"]][1] += int(ctxp == it["gold_frame"]); per[it["lemma"]][2] += int(mfsp == it["gold_frame"])
    ctx_reliable = {lm: (v[0] >= 5 and v[1] > v[2]) for lm, v in per.items()}
    arms = {k: [] for k in ("MFS", "CONSTR", "CTX_BAG", "CTX_WEIGHTED", "CONSTR_CTX_WEIGHTED",
                            "CTX_GATED", "CONSTR_CTX_GATED")}
    gold = []
    for it in test:
        cands = it["cands"]; pri = cpri.get(it["lemma"]) or None
        gold.append(it["gold_frame"])
        mfs = mfs_of(cpri, it["lemma"], cands)
        arms["MFS"].append(mfs)
        v = disB.disambiguate_token(None, _FakeTok(it["lemma"]), cand=cands, frame_feats=it["rf"], joint=True, prior=pri)
        arms["CONSTR"].append(v.frame)
        czb = context_scores(m, cands, it.get("ctx", []), weighted=False)
        czw = context_scores(m, cands, it.get("ctx", []), weighted=True)
        pa = {c: (pri or {}).get(c, 0.0) for c in cands}
        arms["CTX_BAG"].append(max(cands, key=lambda c: pa[c] + w_ctx * czb[c]))
        arms["CTX_WEIGHTED"].append(max(cands, key=lambda c: pa[c] + w_ctx * czw[c]))
        vw = disB.disambiguate_token(None, _FakeTok(it["lemma"]), cand=cands, frame_feats=it["rf"], joint=True,
                                     prior=pri, context_scores=czw)
        arms["CONSTR_CTX_WEIGHTED"].append(vw.frame)
        # GATED: use context only for context-reliable verbs (learned on train); else defer to MFS / construction
        rel = ctx_reliable.get(it["lemma"], False)
        arms["CTX_GATED"].append((max(cands, key=lambda c: pa[c] + w_ctx * czw[c])) if rel else mfs)
        vg = disB.disambiguate_token(None, _FakeTok(it["lemma"]), cand=cands, frame_feats=it["rf"], joint=True,
                                     prior=pri, context_scores=(czw if rel else None))
        arms["CONSTR_CTX_GATED"].append(vg.frame)
    gold = np.array(gold, dtype=object); mfs = np.array(arms["MFS"], dtype=object); subord = mfs != gold
    out = {"n": len(gold), "n_subordinate": int(subord.sum()), "pct_subordinate": round(float(subord.mean()), 3)}
    for k in arms:
        p = np.array(arms[k], dtype=object)
        b = int(((mfs == gold) & (p != gold)).sum()); c = int(((mfs != gold) & (p == gold)).sum())
        out[k] = {"acc": round(float((p == gold).mean()), 3),
                  "subord_rec": round(float((p[subord] == gold[subord]).mean()) if subord.sum() else 0.0, 3),
                  "ovr_prec": round(c / (b + c), 3) if (b + c) else None, "b": b, "c": c,
                  "mcnemar_p": round(mcnemar_p(b, c), 5)}
    out["elapsed_s"] = round(time.time() - t0, 1)
    return out


def main():
    od = os.path.join(REPO, "data", "exp_frame_sense_context_broad_v1"); os.makedirs(od, exist_ok=True)
    m = run()
    json.dump(m, open(os.path.join(od, "metrics.json.tmp"), "w", encoding="ascii"), indent=2)
    os.replace(os.path.join(od, "metrics.json.tmp"), os.path.join(od, "metrics.json"))
    print(f"=== context_broad_v1 {m['elapsed_s']}s  BROAD frame-alternating multiclass  n={m['n']} subord={m['n_subordinate']} ({m['pct_subordinate']}) ===")
    print(f"    {'arm':20s} {'acc':>6s} {'sub_rec':>8s} {'ovr_prec':>9s}  McNemar(b,c,p)")
    for k in ("MFS", "CONSTR", "CTX_BAG", "CTX_WEIGHTED", "CONSTR_CTX_WEIGHTED", "CTX_GATED", "CONSTR_CTX_GATED"):
        a = m[k]; beat = "  <== BEATS MFS" if (a["c"] > a["b"] and a["mcnemar_p"] < 0.05) else ""
        print(f"    {k:20s} {a['acc']:6.3f} {a['subord_rec']:8.3f} {str(a['ovr_prec']):>9s}  b={a['b']} c={a['c']} p={a['mcnemar_p']:.4f}{beat}")
    print("wrote", od)


if __name__ == "__main__":
    main()
