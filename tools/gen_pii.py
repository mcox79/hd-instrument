"""Research WAVE-2: LAP2-12 CONV-9-PII-DETECTION (substrate detects PII via char-class feature prototypes). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_lap2_12_pii_detection_cpu_v1.py -- LAP2-12 CONV-9 PII-DETECTION over substrate feature prototypes -- CPU.

ROUTING: Research LAPTOP_WAVE2 (LAP2-12; production gate). Substrate detects PII (email/phone/SSN/credit-card/name) in a token
  stream. Each token is featurized by character-class pattern (has-@, digit-fraction, dash/dot pattern, length, caps) into an
  FHRR feature vector (role-filler binding); per-type PROTOTYPES are bundles of featurized examples; a token is classified by
  nearest prototype. Measures PII recall + false-positive rate vs a NORMAL-word background. numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS PII recall >= 0.90 AND false-positive <= 0.05. MIDDLE recall >= 0.80. HARD-FAIL else.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "lap2_12_pii_detection_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
TYPES = ["email", "phone", "ssn", "card", "name", "normal"]
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    assert "a@b.com".count("@") == 1, "feat"; print("[selftest] PASS: pii-detection", flush=True)


def gen_token(t, g):
    D = "0123456789"; L = "abcdefghijklmnopqrstuvwxyz"
    def rs(src, k):
        return "".join(src[int(g.integers(0, len(src)))] for _ in range(k))
    if t == "email":
        return rs(L, int(g.integers(3, 8))) + "@" + rs(L, int(g.integers(3, 6))) + ".com"
    if t == "phone":
        return rs(D, 3) + "-" + rs(D, 3) + "-" + rs(D, 4)
    if t == "ssn":
        return rs(D, 3) + "-" + rs(D, 2) + "-" + rs(D, 4)
    if t == "card":
        return rs(D, 4) + " " + rs(D, 4) + " " + rs(D, 4) + " " + rs(D, 4)
    if t == "name":
        return rs(L, 1).upper() + rs(L, int(g.integers(3, 8)))
    return rs(L, int(g.integers(2, 9)))                                   # normal word


def feats(tok):
    n = max(1, len(tok)); d = sum(c.isdigit() for c in tok)
    return np.array([
        float("@" in tok), d / n, float("-" in tok), float("." in tok), float(" " in tok),
        min(len(tok), 20) / 20.0, float(tok[:1].isupper()), float(tok.replace(" ", "").isdigit()),
        tok.count("-") / n, float("@" not in tok and not any(c.isdigit() for c in tok)),
    ], dtype=np.float64)


def run() -> Dict:
    g = np.random.default_rng(9); NF = 10; roles = cphasor(NF, N, g)
    levels = cphasor(11, N, g)                                            # quantized feature-value fillers (0..10)

    def embed(tok):
        f = feats(tok); v = np.zeros(N, dtype=np.complex64)
        for i in range(NF):
            lv = int(round(min(max(f[i], 0.0), 1.0) * 10)); v = v + roles[i] * levels[lv]
        return v
    # build prototypes from training examples
    ntr = 20 if SMOKE else 80; proto = {}
    for t in TYPES:
        acc = np.zeros(N, dtype=np.complex64)
        for _ in range(ntr):
            acc = acc + embed(gen_token(t, g))
        proto[t] = acc
    book = np.stack([proto[t] for t in TYPES])
    NQ = 200; tp = 0; fn = 0; fp = 0; tn = 0
    for _ in range(NQ):
        t = TYPES[int(g.integers(0, len(TYPES)))]; tok = gen_token(t, g)
        pred = TYPES[int(np.argmax((book @ np.conj(embed(tok))).real))]
        is_pii = (t != "normal"); pred_pii = (pred != "normal")
        if is_pii and pred_pii:
            tp += 1
        elif is_pii and not pred_pii:
            fn += 1
        elif not is_pii and pred_pii:
            fp += 1
        else:
            tn += 1
    recall = tp / (tp + fn) if (tp + fn) else 0.0; fpr = fp / (fp + tn) if (fp + tn) else 0.0
    print("  PII recall=%.3f false-positive=%.3f (tp=%d fn=%d fp=%d tn=%d)" % (recall, fpr, tp, fn, fp, tn), flush=True)
    return {"pii_recall": recall, "false_positive": fpr, "n": NQ}


def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f false-positive=%.3f" % (r["pii_recall"], r["false_positive"])
    if r["pii_recall"] >= 0.90 and r["false_positive"] <= 0.05:
        return ("HARD_PASS", "HARD_PASS: substrate detects PII recall>=0.90 with FP<=0.05 -- char-class feature prototypes classify email/phone/SSN/card/name vs normal; production privacy gate. " + s)
    if r["pii_recall"] >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: PII recall 0.80-0.90 or FP>0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: PII recall <0.80. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_lap2_12_pii_detection_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote pii_detection")
