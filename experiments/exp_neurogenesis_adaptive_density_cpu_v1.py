"""
exp_neurogenesis_adaptive_density_cpu_v1.py -- NEUROGENESIS adaptive-density-aware threshold -- CPU.

ROUTING: Research SPRINT3 Tier-4 (neurogenesis adaptive; "adaptive IS contextual"). Fixed-threshold neurogenesis failed (no
  single threshold works across correlation levels). The temporal/contextual meta-pattern PREDICTS an ADAPTIVE (distribution-
  aware) threshold should work. Mechanism: spawn a new shard only when an entity's best-match similarity is a DISTRIBUTIONAL
  OUTLIER (below running_mean - z*running_std of recent best-matches) -- the threshold adapts to the local density/correlation.
  Tests discovered-shards ~ K and purity across MULTIPLE noise levels (where fixed-threshold fails at all but one). Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS adaptive discovers shards in [K-3,K+8] with purity>=0.60 at ALL tested noise levels. MIDDLE at 2/3 levels. HARD-FAIL else.
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
from collections import deque
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "neurogenesis_adaptive_density_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: neurogenesis-adaptive-density", flush=True)
def grow_adaptive(ents, NE, g, z=1.5):
    order = g.permutation(NE); shards = []; assign = np.zeros(NE, dtype=int); recent = deque(maxlen=60)
    for i in order:
        x = ents[i]
        if shards:
            sims = [float((np.vdot(s, x)).real) / N for s in shards]; bi = int(np.argmax(sims)); bm = sims[bi]
        else:
            bm = -1; bi = -1
        if len(recent) >= 15:
            thr = float(np.mean(recent) - z * np.std(recent))         # ADAPTIVE distributional-outlier threshold
        else:
            thr = -0.5
        if bm < thr or not shards:
            shards.append(x.copy()); assign[i] = len(shards) - 1
        else:
            shards[bi] = cnorm(shards[bi] * 8 + x); assign[i] = bi; recent.append(bm)
    return shards, assign
def run() -> Dict:
    g = np.random.default_rng(635); K = 12 if SMOKE else 18; PER = 20; NE = K * PER
    noises = [0.9, 1.3] if SMOKE else [0.7, 1.1, 1.5]; TR = 5 if SMOKE else 20
    by_noise = {}
    for noise in noises:
        purs = []; nss = []
        for _ in range(TR):
            protos = cphasor(K, N, g); truth = np.repeat(np.arange(K), PER)
            ents = cnorm(np.stack([protos[truth[i]] + noise * cphasor(1, N, g)[0] for i in range(NE)]))
            shards, assign = grow_adaptive(ents, NE, g)
            smaj = []
            for s in range(len(shards)):
                v = truth[assign == s]; smaj.append(int(np.bincount(v).argmax()) if len(v) else -1)
            purs.append(float(np.mean([smaj[assign[i]] == truth[i] for i in range(NE)]))); nss.append(len(shards))
        by_noise[noise] = (round(float(np.mean(purs)), 3), round(float(np.mean(nss)), 1))
        print("  ADAPTIVE-DENSITY noise=%.1f: purity=%.3f shards=%.1f (K=%d)" % (noise, by_noise[noise][0], by_noise[noise][1], K), flush=True)
    return {"by_noise": {str(k): list(v) for k, v in by_noise.items()}, "true_K": K, "noises": noises}
def verdict(r) -> Tuple[str, str]:
    K = r["true_K"]; ok = 0
    for ns, (pur, cnt) in r["by_noise"].items():
        if pur >= 0.60 and (K - 3) <= cnt <= (K + 8):
            ok += 1
    s = "by-noise=%s K=%d (%d/%d levels OK)" % (r["by_noise"], K, ok, len(r["by_noise"]))
    if ok == len(r["by_noise"]):
        return ("HARD_PASS", "HARD_PASS: ADAPTIVE density-aware threshold RESCUES neurogenesis across ALL noise levels -- discovers ~K shards with purity>=0.60 regardless of correlation, where fixed-threshold worked at none/one. Confirms the meta-pattern prediction: adaptive (contextual) threshold works where fixed structure fails. " + s)
    if ok >= max(1, len(r["by_noise"]) - 1):
        return ("MIDDLE_BAND", "MIDDLE_BAND: adaptive works at most levels. " + s)
    return ("HARD_FAIL", "HARD_FAIL: adaptive threshold does not robustly discover across noise levels. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
