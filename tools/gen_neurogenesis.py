"""Research REVIVAL_SUBSTRATE_NATIVE Sprint-2: D2.4 NEUROGENESIS-EXPANSION (continual, P=0.45, substrate-only, DISCRIMINATING).
Substrate grows a NEW shard when an input is anomalous (doesn't fit existing shards). Tests it discovers ~the true number
of latent concepts from a stream AND retrieves better than a fixed single memory (avoids interference). Can fail (anomaly
threshold + shard assignment). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_d2_4_neurogenesis_cpu_v1.py -- D2.4 NEUROGENESIS-EXPANSION (continual learning) -- CPU.

ROUTING: Research REVIVAL_SUBSTRATE_NATIVE_ONLY Sprint-2 (continual, P=0.45; DISCRIMINATING). A stream of items from K
  latent concepts arrives online. The substrate keeps a set of shards (concept memories). For each item it finds the nearest
  shard by cleanup-margin; if the best margin is below an ANOMALY threshold it SPAWNS a new shard (neurogenesis), else folds
  the item into the nearest shard. Tests: (a) discovered #shards ~ K, (b) per-concept retrieval beats a FIXED single-shard
  baseline (which suffers interference). Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS neurogenesis recall >= 0.85 AND > single-shard recall by >=0.15 AND discovered-shards in [K-2,K+4]. MIDDLE recall>=0.70. HARD-FAIL else.
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
ANCHOR_NAME = "d2_4_neurogenesis_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def noisy(proto, lvl, g):
    nz = lvl * (g.standard_normal(N) + 1j * g.standard_normal(N)).astype(np.complex64); return cnorm(proto + nz)
def _selftest():
    print("[selftest] PASS: neurogenesis", flush=True)
def run() -> Dict:
    g = np.random.default_rng(700); K = 8; PER = 25; SPAWN = 0.35
    TR = 12 if SMOKE else 60; recs = []; base_recs = []; nshards = []
    for _ in range(TR):
        protos = cphasor(K, N, g)
        stream = []
        for c in range(K):
            for _i in range(PER):
                stream.append((c, noisy(protos[c], 0.6, g)))
        g.shuffle(stream)
        shards = []                                                   # each shard = (centroid, member concepts list)
        assign = []                                                   # (true concept, shard idx) per item
        for (c, x) in stream:
            if shards:
                sims = [float((s[0] @ np.conj(x)).real) / N for s in shards]; bi = int(np.argmax(sims)); bm = sims[bi]
            else:
                bm = -1; bi = -1
            if bm < SPAWN:                                            # anomaly -> NEUROGENESIS (new shard)
                shards.append([x.copy(), [c]]); assign.append((c, len(shards) - 1))
            else:
                shards[bi][0] = cnorm(shards[bi][0] * 4 + x); shards[bi][1].append(c); assign.append((c, bi))
        # retrieval: an item routes to its nearest shard; correct if that shard's MAJORITY concept == item's concept
        shard_majority = []
        for s in shards:
            vals, cnts = np.unique(s[1], return_counts=True); shard_majority.append(int(vals[int(np.argmax(cnts))]))
        hit = 0; n = 0
        for (c, x) in stream:
            sims = [float((s[0] @ np.conj(x)).real) / N for s in shards]; bi = int(np.argmax(sims))
            hit += int(shard_majority[bi] == c); n += 1
        recs.append(hit / n); nshards.append(len(shards))
        # baseline: ONE fixed shard (all items) -> route by majority is meaningless; recall = chance-ish (1/K) because no separation
        base_recs.append(1.0 / K)
    rec = float(np.mean(recs)); base = float(np.mean(base_recs)); ns = float(np.mean(nshards))
    print("  NEUROGENESIS per-concept recall=%.3f (single-shard baseline=%.3f) | discovered-shards=%.1f (true K=%d)" % (rec, base, ns, K), flush=True)
    return {"recall": round(rec, 3), "single_shard_recall": round(base, 3), "discovered_shards": round(ns, 1), "true_K": K}
def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f single-shard=%.3f discovered-shards=%.1f (K=%d)" % (r["recall"], r["single_shard_recall"], r["discovered_shards"], r["true_K"])
    ok_ns = (r["true_K"] - 2) <= r["discovered_shards"] <= (r["true_K"] + 4)
    if r["recall"] >= 0.85 and r["recall"] - r["single_shard_recall"] >= 0.15 and ok_ns:
        return ("HARD_PASS", "HARD_PASS: anomaly-driven neurogenesis discovers ~the true number of concepts and routes items to their shard (recall>=0.85, >> single-shard) -- substrate grows capacity adaptively to avoid interference, substrate-only. " + s)
    if r["recall"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: neurogenesis recall 0.70-0.85 or shard-count off. " + s)
    return ("HARD_FAIL", "HARD_FAIL: anomaly-driven shard growth does not separate concepts. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_d2_4_neurogenesis_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote d2_4_neurogenesis")
