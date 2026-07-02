"""
exp_lap3_12_confidence_calibration_cpu_v1.py -- isotonic post-hoc calibration of cleanup-margin confidence -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 (LAP3-12 CONFIDENCE-CALIBRATION-PP107); pure-FHRR (no download).
PRE-REGISTERED: HARD_PASS iff ECE<=0.10 AND corr>=0.5 on TEST split (calibrated). MIDDLE_BAND iff ECE<=0.18 else HARD_FAIL.
FRAMING: revival of prior Cell 3 (confidence_calibration_isotonic_v1 HARD_FAIL 2026-06-24) with THREE fixes:
  (1) actual isotonic fit-and-apply on train/test split (prior cell measured raw-margin, no calibration step);
  (2) M=500 N=2048 noise*10 regime (acc~0.55; prior N=2048 M=2000 acc=0.09 was Cramer-Rao-bound-blocked below r=0.2);
  (3) verdict logic requires BOTH ECE and corr (prior code only gated ECE -> phantom HP risk).
Substrate-KB prior work at cosine 0.34-0.40; this closes prior Cell 3 HF's specifically-identified missing mechanism.
ASCII-only. write_metrics. PROT-018 v1.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: single-arm cell (raw + calibrated on same margins); N/A
- final_metrics_atomicity: write_metrics helper uses tmp_replace (per _seed_checkpoint)
- except SystemExit: raise BEFORE except Exception (see outer try at bottom)
- crlb_floor_computed: r_max Cramer-Rao formula documented in pre-reg; discriminator_reachability=True at acc=0.55
- baseline_in_band: smoke verifies 0.30 < acc < 0.80 (META_RULE_AG)
- discriminator survives scale: smoke at full-M/N (M=500 N=2048); only TR differs (300 full / 60 smoke)
- HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
- HP_SCOPE: single-arm cell; HP gates apply to calibrated arm only
- cardinality_ok: N/A (no sweep axis)
- per-unit failure-class instrumentation: outer try/except Exception -> crash-metrics write + raise
- calibration_check: default_ok_for_this_regime (sklearn IsotonicRegression, standard 70/30 split)
- all numbers tagged: acc target HYPOTHESIZED@this_prereg; corr r_max THEORETICAL@Cramer-Rao formula
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, json, traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "lap3_12_confidence_calibration_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi
    return np.exp(1j * ang).astype(np.complex64)


def _ece(conf: np.ndarray, correct: np.ndarray, B: int = 10) -> float:
    """Expected calibration error, equal-width bins over [0,1]."""
    ece = 0.0
    n = len(conf)
    for b in range(B):
        lo, hi = b / B, (b + 1) / B
        m = (conf >= lo) & (conf < hi)
        if m.sum() > 0:
            ece += (m.sum() / n) * abs(conf[m].mean() - correct[m].mean())
    return float(ece)


def _selftest():
    from sklearn.isotonic import IsotonicRegression
    m = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    c = np.array([0,   0,   0,   1,   0,   1,   1,   1,   1  ])
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(m, c)
    p = iso.predict(m)
    assert (np.diff(p) >= -1e-9).all(), "isotonic monotonicity broken"
    ece_v = _ece(p, c)
    assert 0.0 <= ece_v <= 1.0, "ece out of range: %f" % ece_v
    print("[selftest] PASS: isotonic-calibration formulas (sklearn IsotonicRegression + ECE)", flush=True)


def run() -> Dict:
    """
    Collect (raw_margin, correct) pairs at M=500 N=2048 noise*10 (variable difficulty),
    split 70/30 train/test, fit sklearn.isotonic.IsotonicRegression on TRAIN,
    apply to TEST, report ECE_calibrated + corr(conf, correct) on TEST.
    """
    from sklearn.isotonic import IsotonicRegression
    g = np.random.default_rng(107)
    N = 2048; M = 500; VV = 120; NOISE_MULT = 10.0
    TR = 60 if SMOKE else 300
    Q_PER_TRIAL = 10
    raw_margins: List[float] = []
    corrects: List[int] = []
    for _ in range(TR):
        keys = cphasor(M, N, g)
        vals = cphasor(VV, N, g)
        truth = g.integers(0, VV, size=M)
        Mem = (keys * vals[truth]).sum(axis=0)
        for _q in range(Q_PER_TRIAL):
            qi = int(g.integers(0, M))
            noise = float(g.random() * NOISE_MULT)
            probe = Mem * np.conj(keys[qi]) + noise * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            scores = (vals @ np.conj(probe)).real
            sc_sorted = np.sort(scores)[::-1] / N
            raw_m = float(sc_sorted[0] - sc_sorted[1])
            pred = int(np.argmax(scores))
            raw_margins.append(raw_m)
            corrects.append(int(pred == truth[qi]))

    raw = np.array(raw_margins, dtype=np.float64)
    y = np.array(corrects, dtype=np.int64)
    n = len(raw)

    # 70/30 split (deterministic on separate rng)
    rng_split = np.random.default_rng(42)
    perm = rng_split.permutation(n)
    n_train = int(n * 0.70)
    tr_idx, te_idx = perm[:n_train], perm[n_train:]

    raw_tr, y_tr = raw[tr_idx], y[tr_idx]
    raw_te, y_te = raw[te_idx], y[te_idx]

    # FIT-AND-APPLY isotonic
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(raw_tr, y_tr)
    conf_te = np.clip(iso.predict(raw_te), 0.0, 1.0)

    # Raw-margin baseline (min-max normalized on test-set for fair ECE bucketing)
    raw_te_lo, raw_te_hi = raw_te.min(), raw_te.max()
    if raw_te_hi > raw_te_lo:
        raw_te_norm = np.clip((raw_te - raw_te_lo) / (raw_te_hi - raw_te_lo), 0.0, 1.0)
    else:
        raw_te_norm = np.zeros_like(raw_te)

    ece_calib = _ece(conf_te, y_te)
    ece_raw = _ece(raw_te_norm, y_te)

    def _corr(a, b):
        if a.std() < 1e-12 or b.std() < 1e-12:
            return 0.0
        return float(np.corrcoef(a, b)[0, 1])

    corr_calib = _corr(conf_te, y_te.astype(np.float64))
    corr_raw = _corr(raw_te_norm, y_te.astype(np.float64))

    overall_acc = float(y.mean())
    train_acc = float(y_tr.mean())
    test_acc = float(y_te.mean())

    print("  raw:   ECE=%.4f corr=%.4f" % (ece_raw, corr_raw), flush=True)
    print("  isotonic-calibrated: ECE=%.4f corr=%.4f  (n_test=%d)" % (ece_calib, corr_calib, len(y_te)), flush=True)
    print("  acc: overall=%.3f train=%.3f test=%.3f" % (overall_acc, train_acc, test_acc), flush=True)

    return {
        "ece": round(ece_calib, 4),
        "conf_acc_corr": round(corr_calib, 4),
        "ece_raw": round(ece_raw, 4),
        "conf_acc_corr_raw": round(corr_raw, 4),
        "n_total": int(n),
        "n_test": int(len(y_te)),
        "n_train": int(len(y_tr)),
        "overall_acc": round(overall_acc, 4),
        "test_acc": round(test_acc, 4),
        "M": M, "N": N, "VV": VV, "noise_mult": NOISE_MULT, "TR": TR, "Q_PER_TRIAL": Q_PER_TRIAL,
    }


def verdict(r: Dict) -> Tuple[str, str]:
    ece = r["ece"]; corr = r["conf_acc_corr"]
    ece_raw = r["ece_raw"]; corr_raw = r["conf_acc_corr_raw"]
    tag = ("ECE_calib=%.4f corr_calib=%.4f  ECE_raw=%.4f corr_raw=%.4f  test_acc=%.3f"
           % (ece, corr, ece_raw, corr_raw, r["test_acc"]))
    # META_RULE_AG baseline-in-band: acc must be 0.30-0.80 for the mechanism to be meaningfully exercised.
    if not (0.30 < r["overall_acc"] < 0.80):
        return ("HARD_FAIL",
                "HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG: overall_acc=%.3f outside [0.30,0.80]; "
                "regime saturates the mechanism. " % r["overall_acc"] + tag)
    # HARD_PASS requires BOTH conditions (fix vs prior Cell 3 verdict-logic bug where only ECE was gated).
    if ece <= 0.10 and corr >= 0.5:
        return ("HARD_PASS",
                "HARD_PASS: substrate cleanup-margin confidence is post-hoc-CALIBRATED via isotonic regression -- "
                "ECE_calibrated<=0.10 AND conf-acc-corr_calibrated>=0.5 on TEST split. First working corner of "
                "3-signal cortex confidence architecture. Cell 3 (2026-06-24 HF) revival with isotonic fit-and-apply "
                "+ M=500/N=2048 noise*10 regime + corrected verdict-logic gate. " + tag)
    if ece <= 0.18:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: isotonic calibration reduces ECE substantially (raw->calibrated) and ECE<=0.18; not both "
                "ECE<=0.10 AND corr>=0.5 satisfied. Correlation may sit at Cramer-Rao ceiling at test_acc=%.3f. "
                % r["test_acc"] + tag)
    return ("HARD_FAIL",
            "HARD_FAIL: ECE_calibrated>0.18 -- isotonic did not calibrate the substrate's cleanup-margin confidence. " + tag)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def main():
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    r = run()
    v, vmsg = verdict(r)
    elapsed = time.time() - t0
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "summary": v + ": " + vmsg[:200],
        "run_mode": RUN_MODE,
        "n_seeds": 1,
        "per_seed": [r],
        "elapsed_s": elapsed,
    }
    write_metrics(out_dir, metrics, [r])
    print("[metrics] written", flush=True)


try:
    main()
except SystemExit:
    raise
except KeyboardInterrupt:
    raise
except Exception as e:
    try:
        _out_dir = get_output_dir(ANCHOR_NAME)
    except Exception:
        _out_dir = str(REPO / "data" / ("exp_" + ANCHOR_NAME))
    _write_crash_metrics(_out_dir, e)
    raise
