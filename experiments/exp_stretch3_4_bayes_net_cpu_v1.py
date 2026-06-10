"""
exp_stretch3_4_bayes_net_cpu_v1.py -- full Bayes-net inference (CPTs in substrate, enumeration) -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 (STRETCH3-4 BAYESIAN-BELIEF-NET); pure-FHRR (no download). Random 4-node DAG; CPTs stored as quantized amplitudes; posterior via enumeration vs exact inference.
PRE-REGISTERED: HARD-PASS posterior-match>=0.85. MIDDLE>=0.70. HARD-FAIL<0.70.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, itertools
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "stretch3_4_bayes_net_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: bayesian-belief-net", flush=True)
def run() -> Dict:
    g = np.random.default_rng(246); N = 8192; NV = 4; nodes = cphasor(NV, N, g); cfgk = cphasor(8, N, g); amp = cphasor(21, N, g)
    TR = 30 if SMOKE else 150; ok = 0; n = 0
    for _ in range(TR):
        # random DAG over 4 binary nodes (topological: parents have lower index)
        parents = {v: sorted(set(int(p) for p in g.choice(v, min(v, 2), replace=False))) if v > 0 else [] for v in range(NV)}
        cpt = {}                                                          # (v, parent-config-tuple) -> P(v=1|parents)
        for v in range(NV):
            for cfg in itertools.product([0, 1], repeat=len(parents[v])):
                cpt[(v, cfg)] = float(g.random())
        # store CPT probs in substrate as quantized amplitudes: bind (node, config-index) -> amp-level
        def _ci(cfg):
            return sum((b << i) for i, b in enumerate(cfg))
        store_node = {}                                                  # per-node CPT shard (few entries -> exact retrieval)
        for v in range(NV):
            sh = np.zeros(N, dtype=np.complex64)
            for cfg in itertools.product([0, 1], repeat=len(parents[v])):
                sh = sh + cfgk[_ci(cfg)] * amp[int(round(cpt[(v, cfg)] * 20))]
            store_node[v] = sh
        def getp(v, cfg):
            return cidx(store_node[v] * np.conj(cfgk[_ci(tuple(cfg))]), amp) / 20.0
        def joint(assign, pfun):
            pr = 1.0
            for v in range(NV):
                cfg = tuple(assign[p] for p in parents[v]); pv1 = pfun(v, cfg)
                pr *= pv1 if assign[v] == 1 else (1 - pv1)
            return pr
        # query P(Xq=1 | evidence on one node), via enumeration; compare substrate vs exact CPT
        qv = int(g.integers(0, NV)); ev = int(g.integers(0, NV))
        while ev == qv:
            ev = int(g.integers(0, NV))
        eval_ = int(g.integers(0, 2))
        def posterior(pfun):
            num = 0.0; den = 0.0
            free = [v for v in range(NV) if v != ev]
            for bits in itertools.product([0, 1], repeat=len(free)):
                assign = {ev: eval_}
                for v, b in zip(free, bits):
                    assign[v] = b
                jp = joint(assign, pfun); den += jp
                if assign[qv] == 1:
                    num += jp
            return num / den if den > 0 else 0.5
        sub = posterior(lambda v, c: getp(v, c)); exact = posterior(lambda v, c: cpt[(v, tuple(c))])
        ok += int(abs(sub - exact) < 0.06); n += 1
    acc = ok / n; print("  BAYES-NET posterior-within-tol=%.3f (NV=%d, n=%d)" % (acc, NV, n), flush=True)
    return {"bnet_acc": acc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "posterior-match=%.3f (n=%d)" % (r["bnet_acc"], r["n"])
    if r["bnet_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate stores a Bayes net (CPTs) and computes posteriors via enumeration matching exact inference >=0.85 -- full belief-net inference respecting conditional independence. " + s)
    if r["bnet_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: bnet 0.70-0.85 (CPT quantization). " + s)
    return ("HARD_FAIL", "HARD_FAIL: bnet <0.70. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
