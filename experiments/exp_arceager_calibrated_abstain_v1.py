"""exp_arceager_calibrated_abstain_v1 -- BUILD the parser's calibrated ABSTAIN/DROP signal (PARSER_SERVICE_SPEC
behavior #5: "EXPOSE DROPS, don't confabulate" -- relcl/predict_revise need the parser to leave an attachment
EMPTY when uncertain rather than over-commit a wrong bind; the per-arc MARGIN is emitted but uncalibrated
(audit: 14.40 vs 14.16 OOD -> unusable) and consumed by NO live component). This calibrates the arc-eager
per-attachment confidence on UD-EWT dev (Platt / logistic on the raw margin) and shows on test that it becomes a
usable abstain signal: (1) CALIBRATION improves (ECE down); (2) RISK-COVERAGE -- committing only the confident
attachments raises attachment accuracy monotonically; (3) the ABSTAINED (dropped) set concentrates the errors
(error-rate abstained >> committed), which is exactly the drop signal predict_revise needs; (4) a shuffled-
confidence TWIN loses (flat risk-coverage, AUC ~0.5). UD-EWT gold heads = ground truth for attachment
correctness. CPU numpy only, NO torch/spaCy/LLM. ASCII. own dir.
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

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_arceager_calibrated_abstain_v1")


def collect(sents, W):
    """per attached token: (margin, softmax_conf, correct?). ROOT-filled tokens (conf 0) excluded (not an
    active attachment decision)."""
    marg = []; conf = []; ok = []
    for s in sents:
        toks = [t[1] for t in s]; pos = [t[2] for t in s]
        heads, cf, mg = AEO.parse_with_conf(toks, pos, W)
        for t in s:
            i, h = t[0], t[3]
            if h < 0 or h > len(s):
                continue
            if mg.get(i, 0.0) == 0.0 and cf.get(i, 0.0) == 0.0:
                continue                                   # unattached ROOT-fill -> not a decision
            marg.append(mg.get(i, 0.0)); conf.append(cf.get(i, 0.0)); ok.append(int(heads.get(i, -1) == h))
    return np.array(marg, float), np.array(conf, float), np.array(ok, int)


def platt_fit(x, y, iters=500, lr=0.05):
    """logistic P(correct)=sigmoid(a*z+b) on standardized x; returns (a,b,mu,sd)."""
    mu = x.mean(); sd = x.std() + 1e-9; z = (x - mu) / sd
    a, b = 1.0, 0.0
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-(a * z + b)))
        ga = np.mean((p - y) * z); gb = np.mean(p - y)
        a -= lr * ga; b -= lr * gb
    return a, b, mu, sd


def platt_apply(x, params):
    a, b, mu, sd = params; z = (x - mu) / sd
    return 1.0 / (1.0 + np.exp(-(a * z + b)))


def ece(pconf, ok, bins=10):
    edges = np.linspace(0, 1, bins + 1); e = 0.0; n = len(ok)
    for j in range(bins):
        m = (pconf >= edges[j]) & (pconf < edges[j + 1] if j < bins - 1 else pconf <= edges[j + 1])
        if m.sum() == 0:
            continue
        e += (m.sum() / n) * abs(ok[m].mean() - pconf[m].mean())
    return float(e)


def auc(scores, labels):
    s = np.asarray(scores, float); y = np.asarray(labels, int)
    pos = (y == 1).sum(); neg = (y == 0).sum()
    if pos == 0 or neg == 0:
        return 0.5
    order = np.argsort(s); ranks = np.empty(len(s)); ranks[order] = np.arange(1, len(s) + 1)
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt); start = csum - cnt; avg = (start + csum + 1) / 2.0; ranks = avg[inv]
    return float((ranks[y == 1].sum() - pos * (pos + 1) / 2.0) / (pos * neg))


def risk_coverage(pconf, ok, covs=(1.0, 0.9, 0.8, 0.7, 0.5)):
    order = np.argsort(-pconf); oks = ok[order]; n = len(ok); out = {}
    for c in covs:
        k = max(1, int(round(c * n)))
        out["%.2f" % c] = round(float(oks[:k].mean()), 4)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--abstain_frac", type=float, default=0.2); args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    W = AEO.load_model(AEO.MODEL_PATH)
    dev = [s for s in AEO._load_ud_feats("dev") if 1 <= len(s) <= AEO.MAXLEN]
    test = [s for s in AEO._load_ud_feats("test") if 1 <= len(s) <= AEO.MAXLEN]
    print("[data] dev=%d test=%d" % (len(dev), len(test)), flush=True)
    md, cd, okd = collect(dev, W)
    mt, ct, okt = collect(test, W)
    print("[collect] dev attach decisions=%d (acc=%.4f) test=%d (acc=%.4f)" % (len(okd), okd.mean(), len(okt), okt.mean()), flush=True)

    params = platt_fit(md, okd.astype(float))           # calibrate on the RAW MARGIN
    pcal = platt_apply(mt, params)                        # calibrated P(correct) on test
    # raw softmax conf (uncalibrated, saturated) for the before/after comparison
    ece_raw = ece(ct, okt); ece_cal = ece(pcal, okt)
    auc_marg = auc(mt, okt); auc_cal = auc(pcal, okt)
    rc_cal = risk_coverage(pcal, okt)
    rng = np.random.default_rng(3); shuf = pcal[rng.permutation(len(pcal))]
    rc_shuf = risk_coverage(shuf, okt); auc_shuf = auc(shuf, okt)

    # abstain/drop demonstration: drop the bottom abstain_frac by calibrated conf
    order = np.argsort(pcal); k = int(round(args.abstain_frac * len(pcal)))
    dropped = order[:k]; kept = order[k:]
    err_dropped = 1.0 - okt[dropped].mean(); err_kept = 1.0 - okt[kept].mean(); err_all = 1.0 - okt.mean()

    res = {"n_dev": len(okd), "n_test": len(okt), "attach_acc_test": round(float(okt.mean()), 4),
           "ece_raw_softmax": round(ece_raw, 4), "ece_calibrated_margin": round(ece_cal, 4),
           "auc_raw_margin": round(auc_marg, 4), "auc_calibrated": round(auc_cal, 4), "auc_shuffled_twin": round(auc_shuf, 4),
           "risk_coverage_calibrated": rc_cal, "risk_coverage_shuffled_twin": rc_shuf,
           "abstain_frac": args.abstain_frac, "err_rate_dropped": round(float(err_dropped), 4),
           "err_rate_kept": round(float(err_kept), 4), "err_rate_all": round(float(err_all), 4),
           "drop_concentration_ratio": round(float(err_dropped / max(1e-9, err_kept)), 2)}
    print("\n=== CALIBRATED ABSTAIN SIGNAL (UD-EWT test, n=%d attach decisions, acc=%.4f) ===" % (len(okt), okt.mean()), flush=True)
    print("  CALIBRATION ECE: raw-softmax=%.4f -> calibrated-margin=%.4f (lower=better)" % (ece_raw, ece_cal), flush=True)
    print("  AUC(conf, correct): raw-margin=%.4f calibrated=%.4f shuffled-twin=%.4f" % (auc_marg, auc_cal, auc_shuf), flush=True)
    print("  RISK-COVERAGE (attach acc @ coverage): %s" % rc_cal, flush=True)
    print("       shuffled twin (flat): %s" % rc_shuf, flush=True)
    print("  ABSTAIN/DROP @ bottom %.0f%%: err_rate dropped=%.4f vs kept=%.4f vs all=%.4f (concentration %.2fx)" % (
        100 * args.abstain_frac, err_dropped, err_kept, err_all, res["drop_concentration_ratio"]), flush=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "arceager_calibrated_abstain_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
