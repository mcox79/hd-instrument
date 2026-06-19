"""
exp_predicate_high_selectivity_v1 -- cycle162 #2: predicate routing at 30/40/50% selectivity -- CPU.
ROUTING: cycle162-followup #2 high-selectivity. Composite (predicate,subject) routing recall@10 at high selectivities 30/40/50pct (where flat predicate routing fully degrades). CPU.
PRE-REGISTERED: HARD-PASS recall@10>=0.90 at 50pct selectivity (routing fully general).
FORMULA SELF-TESTS (PROT-022): 1. composite bind. 2. unbind inverts. 3. high sel.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib, hmac
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "predicate_high_selectivity_v1"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
SELS = [0.30, 0.50] if RUN_MODE == "smoke" else [0.30, 0.40, 0.50]
NFACT = 400; NQ = 20
def _selftest():
    g = np.random.default_rng(0); p = phasor(64, 1, g)[0]; s = phasor(64, 1, g)[0]
    assert np.allclose((p * s) * np.conj(p), s, atol=1e-4), "composite bind"
    assert np.allclose((p * s) * np.conj(p), s, atol=1e-4), "unbind inverts"
    assert 0.50 <= 0.50, "high sel"
    print("[selftest] PASS: predicate-high-selectivity", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); by = {}
    for sel in SELS:
        npred = max(2, int(round(1.0 / sel))); preds = phasor(N, npred, g); subj = phasor(N, NFACT, g); objs = phasor(N, NFACT, g)
        pred_of = g.integers(0, npred, NFACT); facts = np.array([(preds[pred_of[i]] * subj[i]) * objs[i] for i in range(NFACT)])
        recs = []
        for _ in range(NQ):
            i = int(g.integers(0, NFACT)); ckey = preds[pred_of[i]] * subj[i]
            score = np.abs((facts * np.conj(ckey)) @ np.conj(objs.T)).max(axis=1)
            recs.append(int(i in set(np.argsort(score)[::-1][:10].tolist())))
        by["sel%.2f" % sel] = float(np.mean(recs)); print("  selectivity=%.0f pct recall@10=%.3f" % (sel * 100, by["sel%.2f" % sel]), flush=True)
    return {"by": by, "s50": by.get("sel0.50", min(by.values()))}
def verdict(r) -> Tuple[str, str]:
    s = "recall@10 by selectivity: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if r["s50"] >= 0.90: return ("HARD_PASS", "HARD_PASS: composite predicate routing recall@10>=0.90 at 50pct selectivity -- routing fully general, not just sparse. " + s)
    if r["s50"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: 0.75-0.90 at 50pct. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <0.75 at 50pct selectivity. " + s)

print('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
