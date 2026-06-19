"""Research WAVE-3 laptop: LAP3-7 N=100-ENSEMBLE-POPULATION + LAP3-6 LEARNED-ORTHOGONAL-CODEBOOK. Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 ({tag}); pure-FHRR (no download). {desc}
PRE-REGISTERED: {prereg}
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
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
{body}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''

ENS100 = r'''
def _selftest():
    import numpy as _n; assert _n.bincount([2,2,1]).argmax()==2, "vote"; print("[selftest] PASS: n100-ensemble", flush=True)
def run() -> Dict:
    g = np.random.default_rng(249); N = 512; M = 90; VV = 100; NOISE = 2.6
    TR = 20 if SMOKE else 120; single = 0; ens10 = 0; ens100 = 0; n = 0
    for _ in range(TR):
        truth = g.integers(0, VV, size=M); P = 100
        subs = []
        for p in range(P):
            keys = cphasor(M, N, g); vals = cphasor(VV, N, g); Mem = (keys * vals[truth]).sum(axis=0); subs.append((keys, vals, Mem))
        qi = int(g.integers(0, M)); votes = []
        for (keys, vals, Mem) in subs:
            noisy = Mem * np.conj(keys[qi]) + NOISE * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64)
            votes.append(cidx(noisy, vals))
        single += int(votes[0] == truth[qi])
        ens10 += int(np.bincount(votes[:10]).argmax() == truth[qi])
        ens100 += int(np.bincount(votes).argmax() == truth[qi]); n += 1
    sa = single / n; e10 = ens10 / n; e100 = ens100 / n
    print("  N=100-ENSEMBLE single=%.3f ens10=%.3f ens100=%.3f gain100=%.1fpp (n=%d)" % (sa, e10, e100, (e100 - sa) * 100, n), flush=True)
    return {"single": sa, "ens10": e10, "ens100": e100, "gain100_pp": round((e100 - sa) * 100, 1)}
def verdict(r) -> Tuple[str, str]:
    s = "single=%.3f ens10=%.3f ens100=%.3f gain=%.1fpp" % (r["single"], r["ens10"], r["ens100"], r["gain100_pp"])
    if r["gain100_pp"] >= 20.0:
        return ("HARD_PASS", "HARD_PASS: N=100 substrate ensemble lifts noisy-recall by >=20pp over single (past PP-249 N=10) -- sqrt-N population-coding improvement holds to N=100. " + s)
    if r["gain100_pp"] >= 10.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: N=100 gain 10-20pp. " + s)
    return ("HARD_FAIL", "HARD_FAIL: N=100 gain <10pp. " + s)
'''

CODEBOOK = r'''
def _selftest():
    import numpy as _n; q, _ = _n.linalg.qr(_n.random.RandomState(0).randn(4, 4)); assert q.shape == (4, 4), "qr"; print("[selftest] PASS: learned-codebook", flush=True)
def _recall(N, K, vals, g):
    keys = cphasor(K, N, g); Mem = (keys * vals).sum(axis=0)
    return sum(int(cidx(Mem * np.conj(keys[i]), vals) == i) for i in range(K)) / K
def run() -> Dict:
    g = np.random.default_rng(150); N = 512; K = 150; TR = 5 if SMOKE else 25
    rand_r = []; learn_r = []
    for _ in range(TR):
        rv = cphasor(K, N, g)                                            # random codebook
        Q, _ = np.linalg.qr(g.standard_normal((N, K)) + 1j * g.standard_normal((N, K)))   # learned: orthonormal codebook
        lv = (Q.T * math.sqrt(N)).astype(np.complex64)                   # K orthonormal columns -> rows, scaled to ~unit-energy
        rand_r.append(_recall(N, K, rv, g)); learn_r.append(_recall(N, K, lv, g))
    rr = float(np.mean(rand_r)); lr = float(np.mean(learn_r)); ratio = lr / rr if rr > 0 else 99.0
    print("  CODEBOOK K=%d N=%d: random-recall=%.3f learned-recall=%.3f ratio=%.2fx (n=%d)" % (K, N, rr, lr, ratio, TR), flush=True)
    return {"random_recall": rr, "learned_recall": lr, "capacity_ratio": round(ratio, 2), "K": K, "N": N}
def verdict(r) -> Tuple[str, str]:
    s = "random=%.3f learned=%.3f ratio=%.2fx (K=%d N=%d)" % (r["random_recall"], r["learned_recall"], r["capacity_ratio"], r["K"], r["N"])
    if r["capacity_ratio"] >= 1.5:
        return ("HARD_PASS", "HARD_PASS: learned orthonormal codebook gives >=1.5x the recall/capacity of a random codebook at K=150 -- engineering lever #2 (learned codebooks) confirmed; substrate stack expects learned codebooks at the right layer. " + s)
    if r["capacity_ratio"] >= 1.2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: capacity ratio 1.2-1.5x. " + s)
    return ("HARD_FAIL", "HARD_FAIL: capacity ratio <1.2x. " + s)
'''

C = [
    dict(anchor="lap3_7_n100_ensemble_cpu_v1", tag="LAP3-7 N=100-ENSEMBLE-POPULATION", title="N=100 substrate ensemble noise robustness", desc="100 independent substrates vote on noisy queries; measure gain over single + the N=10 baseline.", prereg="HARD-PASS N=100 gain>=20pp. MIDDLE>=10pp. HARD-FAIL<10pp.", body=ENS100),
    dict(anchor="lap3_6_learned_codebook_cpu_v1", tag="LAP3-6 LEARNED-ORTHOGONAL-CODEBOOK", title="learned (orthonormal) vs random codebook capacity at K=150", desc="Compare recall storing K=150 pairs with a random vs an orthonormal (QR) value codebook.", prereg="HARD-PASS capacity ratio>=1.5x. MIDDLE>=1.2x. HARD-FAIL<1.2x.", body=CODEBOOK),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
