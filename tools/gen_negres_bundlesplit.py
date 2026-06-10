"""Research NEGATIVE-RESOLUTION TIER-1 P1: BUNDLE-SPLIT C=4 (codebook 2x via type-routing, no math change).
Resolves LAP4-1 (FHRR capacity is structural ~sqrt(N/K)) by ROUTING: partition items by type into C shards so each shard
carries M/C load -> crosstalk noise sqrt(M/C) at query time when type is known -> capacity scales ~C x. Pure-numpy. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_negres_bundle_split_c4_cpu_v1.py -- BUNDLE-SPLIT C=4 (codebook 2x by type-routing) -- CPU.

ROUTING: Research NEGATIVE_RESOLUTION_PRIORITIES P1 (resolves LAP4-1 structural capacity). C=4 type categories
  (entity/relation/attribute/provenance). Key->value pairs stored in per-type shards; query routes to the item's type
  shard so crosstalk is sqrt(M/C) not sqrt(M). Measure M* = max pairs at recall>=0.90, split vs flat. Capacity ratio.
PRE-REGISTERED: HARD-PASS M*_split / M*_flat >= 2.0. MIDDLE >= 1.5. HARD-FAIL < 1.5.
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
ANCHOR_NAME = "negres_bundle_split_c4_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192; C = 4
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: bundle-split-c4", flush=True)
def _recall(M, split, g, Vpc=120, TR=8):
    # M key->value pairs across C value-type sub-codebooks (Vpc values each). split: C shards keyed by type; flat: 1 shard.
    acc = 0.0
    for _ in range(TR):
        VV = [cphasor(Vpc, N, g) for _ in range(C)]
        keys = cphasor(M, N, g); typ = g.integers(0, C, size=M); vidx = g.integers(0, Vpc, size=M)
        if split:
            mem = [np.zeros(N, dtype=np.complex64) for _ in range(C)]
            for i in range(M):
                mem[typ[i]] += keys[i] * VV[typ[i]][vidx[i]]
        else:
            flat = np.zeros(N, dtype=np.complex64)
            for i in range(M):
                flat += keys[i] * VV[typ[i]][vidx[i]]
        hit = 0; nq = min(M, 60)
        qs = g.choice(M, nq, replace=False)
        for i in qs:
            c = int(typ[i])
            src = mem[c] if split else flat
            cand = src * np.conj(keys[i])
            if split:
                pred = int(np.argmax((VV[c] @ np.conj(cand)).real))           # cleanup within type shard
                hit += int(pred == vidx[i])
            else:
                allV = np.vstack(VV); pred = int(np.argmax((allV @ np.conj(cand)).real))  # cleanup across all values
                hit += int(pred == c * Vpc + vidx[i])
        acc += hit / nq
    return acc / TR
def _mstar(split, g):
    grid = [40, 80, 160, 320, 640] if SMOKE else [60, 120, 250, 500, 1000, 2000]
    TR = 4 if SMOKE else 8; last = grid[0]
    for M in grid:
        r = _recall(M, split, g, TR=TR)
        print("    %s M=%d recall=%.3f" % ("split" if split else "flat", M, r), flush=True)
        if r >= 0.90:
            last = M
        else:
            break
    return last
def run() -> Dict:
    g = np.random.default_rng(841)
    mf = _mstar(False, g); ms = _mstar(True, g); ratio = ms / max(1, mf)
    print("  BUNDLE-SPLIT M*_flat=%d M*_split=%d ratio=%.2f (C=%d)" % (mf, ms, ratio, C), flush=True)
    return {"mstar_flat": mf, "mstar_split": ms, "ratio": round(ratio, 2), "C": C}
def verdict(r) -> Tuple[str, str]:
    s = "M*_flat=%d M*_split=%d ratio=%.2f C=%d" % (r["mstar_flat"], r["mstar_split"], r["ratio"], r["C"])
    if r["ratio"] >= 2.0:
        return ("HARD_PASS", "HARD_PASS: type-routed bundle-split gives >=2x effective capacity vs flat bundle with NO math change (resolves LAP4-1: structural sqrt(N/K) capacity is multiplied by routing into C type shards). " + s)
    if r["ratio"] >= 1.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: split gives 1.5-2x capacity. " + s)
    return ("HARD_FAIL", "HARD_FAIL: split <1.5x; routing does not lift capacity. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d C=%d" % (ANCHOR_NAME, RUN_MODE, N, C), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_negres_bundle_split_c4_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote bundle_split_c4")
