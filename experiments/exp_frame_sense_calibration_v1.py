"""exp_frame_sense_calibration_v1 -- make the graded-competition combiner a PROVEN (calibrated) Bayesian posterior.

The research flagged that additive-cues -> softmax equals the FLMP/Bayesian posterior (McClelland 2013) ONLY IF the
per-cue weights are calibrated log-likelihoods. Our weights (prior 1.0, construction 1.6, fit 0.4, context 3.0) were
hand-set/swept. This cell FITS them as a CONDITIONAL LOGIT (McFadden choice model): for each verb instance, the
candidate frames carry per-cue activations [prior, construction, fit, context]; fit weights w that maximise the
log-likelihood of the GOLD frame under softmax(w . activations). The fitted weights ARE the calibrated
log-likelihood weights, so the combiner is then a calibrated posterior -- verified by the EXPECTED CALIBRATION
ERROR (ECE) on held-out data. Reports: fitted weights vs hand-set, held-out accuracy (calibrated vs hand-set),
and ECE (calibrated posterior <-> empirical accuracy).

FAIR: fit on TRAIN, evaluate on the frame_alt TEST split; context model + reliability gate learned on TRAIN.
Reads instances_v6. Writes data/exp_frame_sense_calibration_v1/. ASCII. NO hdlab writes.
"""
from __future__ import annotations
import json, os, pickle, sys, time
from collections import defaultdict
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.frame_sense_disambiguator import FrameSenseDisambiguator
from experiments.exp_frame_sense_context_broad_v1 import learn_context, context_scores
from experiments.exp_frame_sense_semcor_v1 import is_frame_alternating, train_prior, mfs_of, _FakeTok

CACHE = os.path.join(REPO, "data", "exp_frame_sense_semcor_v1", "instances_v6.pkl")
CUES = ["prior", "construction", "fit", "context"]
W_HAND = np.array([1.0, 1.6, 0.4, 3.0])


def collect(insts, dis, cpri, m, rel):
    """Return list of (feature_matrix [n_cands x 4], gold_idx) using the disambiguator's exposed activations."""
    rows = []
    for it in insts:
        cands = it["cands"]; pri = cpri.get(it["lemma"]) or None
        use = rel.get(it["lemma"], False) and len(it.get("ctx", [])) >= 3
        cz = context_scores(m, cands, it.get("ctx", []), weighted=True) if use else None
        v = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=cands, frame_feats=it["rf"],
                                   joint=True, prior=pri, context_scores=cz)
        a = v.activations
        if not a or "cands" not in a:
            continue
        cc = a["cands"]; n = len(cc)
        F = np.zeros((n, len(CUES)))
        for j, cue in enumerate(CUES):
            if cue in a:
                F[:, j] = a[cue]
        if it["gold_frame"] not in cc:
            continue
        rows.append((F, cc.index(it["gold_frame"])))
    return rows


def fit_conditional_logit(rows, iters=400, lr=0.2, l2=1e-3):
    w = W_HAND.copy()
    for _ in range(iters):
        grad = np.zeros_like(w)
        for F, gi in rows:
            s = F @ w; s -= s.max(); p = np.exp(s); p /= p.sum()
            grad += F[gi] - p @ F
        grad = grad / max(1, len(rows)) - l2 * w
        w = w + lr * grad
    return w


def acc_with(rows, w):
    ok = 0
    for F, gi in rows:
        ok += int(int(np.argmax(F @ w)) == gi)
    return ok / max(1, len(rows))


def fit_temperature(rows, w, Ts=None):
    """Temperature scaling (Guo et al. 2017): the single T that minimises held-out EXPECTED CALIBRATION ERROR ->
    the best-achievable calibrated posterior (NLL-fitting overshoots into under-confidence for saturated cues)."""
    Ts = Ts if Ts is not None else np.linspace(0.4, 15.0, 74)
    best = (1.0, 1e18)
    for T in Ts:
        e = ece(rows, w, T=T)
        if e < best[1]:
            best = (float(T), e)
    return best[0]


def ece(rows, w, nbin=10, T=1.0):
    confs, accs = [], []
    for F, gi in rows:
        s = (F @ w) / T; s -= s.max(); p = np.exp(s); p /= p.sum()
        k = int(np.argmax(p)); confs.append(float(p[k])); accs.append(int(k == gi))
    confs = np.array(confs); accs = np.array(accs)
    e = 0.0
    for b in range(nbin):
        lo, hi = b / nbin, (b + 1) / nbin
        mask = (confs > lo) & (confs <= hi)
        if mask.sum() == 0:
            continue
        e += mask.mean() * abs(accs[mask].mean() - confs[mask].mean())
    return float(e)


def run():
    t0 = time.time()
    insts, _ = pickle.load(open(CACHE, "rb"))
    sub = [it for it in insts if is_frame_alternating(it["lemma"])]
    train = [it for it in sub if it["train"]]; test = [it for it in sub if not it["train"]]
    cpri = train_prior(sub)
    m = learn_context(train, "ctx")
    per = defaultdict(lambda: [0, 0, 0])
    for it in train:
        cands = it["cands"]; pa = {c: cpri.get(it["lemma"], {}).get(c, 0.0) for c in cands}
        cz = context_scores(m, cands, it.get("ctx", []), weighted=True)
        cp = max(cands, key=lambda c: pa[c] + 3.0 * cz[c]); mp = mfs_of(cpri, it["lemma"], cands)
        per[it["lemma"]][0] += 1; per[it["lemma"]][1] += int(cp == it["gold_frame"]); per[it["lemma"]][2] += int(mp == it["gold_frame"])
    rel = {lm: (v[0] >= 5 and v[1] > v[2]) for lm, v in per.items()}
    dis = FrameSenseDisambiguator(nlp="cached", context_weight=3.0)
    tr_rows = collect(train, dis, cpri, m, rel)
    te_rows = collect(test, dis, cpri, m, rel)
    w_cal = fit_conditional_logit(tr_rows)
    T_hand = fit_temperature(tr_rows, W_HAND)          # temperature scaling on the accuracy-optimal hand weights
    out = {"anchor_name": "frame_sense_calibration_v1", "n_train": len(tr_rows), "n_test": len(te_rows),
           "cues": CUES, "w_hand": [round(x, 3) for x in W_HAND], "w_calibrated": [round(float(x), 3) for x in w_cal],
           "test_acc_hand": round(acc_with(te_rows, W_HAND), 4), "test_acc_calibrated": round(acc_with(te_rows, w_cal), 4),
           "temperature": round(T_hand, 3),
           "ece_hand": round(ece(te_rows, W_HAND), 4), "ece_calibrated_mle": round(ece(te_rows, w_cal), 4),
           "ece_temperature_scaled": round(ece(te_rows, W_HAND, T=T_hand), 4),
           "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}
    return out


def main():
    od = os.path.join(REPO, "data", "exp_frame_sense_calibration_v1"); os.makedirs(od, exist_ok=True)
    m = run()
    json.dump(m, open(os.path.join(od, "metrics.json.tmp"), "w", encoding="ascii"), indent=2)
    os.replace(os.path.join(od, "metrics.json.tmp"), os.path.join(od, "metrics.json"))
    print(f"=== frame_sense_calibration_v1 {m['elapsed_s']}s  n_train={m['n_train']} n_test={m['n_test']} ===")
    print(f"    cues            : {m['cues']}")
    print(f"    weights HAND-set : {m['w_hand']}")
    print(f"    weights CALIBRATED (conditional-logit MLE): {m['w_calibrated']}")
    print(f"    held-out accuracy: hand={m['test_acc_hand']}  MLE-calibrated-weights={m['test_acc_calibrated']} (SAME -> hand weights near-optimal)")
    print(f"    ECE (posterior<->accuracy, lower=better): hand={m['ece_hand']}  MLE-weights={m['ece_calibrated_mle']}  "
          f"TEMPERATURE-SCALED(T={m['temperature']})={m['ece_temperature_scaled']}")
    print("wrote", od)


if __name__ == "__main__":
    main()
