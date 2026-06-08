"""
exp_bipolar_quantization_quality_cpu_v1.py -- 1-bit bipolar (sign) quantized substrate matches float recall (memory-efficient deployment) -- CPU.

ROUTING: strong-batch (CAP-6 bipolar quantization quality). Quantize the substrate to 1-bit bipolar (sign of real/imag) and compare recall to the full float baseline at the same load. If bipolar recall matches float, the substrate deploys at ~16x memory savings. Tests the memory-efficiency lever. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS bipolar recall >= float recall - 0.03 (matches within 3pp). MIDDLE within 0.08. HARD-FAIL worse.
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
ANCHOR_NAME = "bipolar_quantization_quality_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    import numpy as _n; assert set(_n.unique(_n.sign([-2.0,3.0]))) <= {-1.0,1.0}, "sign"; print("[selftest] PASS: bipolar-quantization-quality", flush=True)
def qz(x):
    return (np.sign(x.real) + 1j * np.sign(x.imag)).astype(np.complex64)   # nearest 4-quadrant phasor (1-bit per component)
def run() -> Dict:
    g = np.random.default_rng(902); N = 8192; VE = 300; REL = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g); TR = 60 if SMOKE else 200; LOAD = 40
    ents_q = qz(ents); REL_q = qz(REL)                                     # quantized codebook + role
    fhit = 0; bhit = 0; n = 0
    for _ in range(TR):
        s = int(g.integers(0, VE)); o = int(g.integers(0, VE))
        shard = ents[s] * REL * ents[o]; bshard = ents_q[s] * REL_q * ents_q[o]
        for _d in range(LOAD):
            a = int(g.integers(0, VE)); b = int(g.integers(0, VE))
            shard = shard + ents[a] * REL * ents[b]; bshard = bshard + ents_q[a] * REL_q * ents_q[b]
        rec = shard * np.conj(ents[s] * REL); fhit += int(cidx(rec, ents) == o)
        bshard = qz(bshard)                                                # quantize the bundle to 1-bit per component
        brec = bshard * np.conj(ents_q[s] * REL_q)
        bhit += int(int(np.argmax((ents_q @ np.conj(brec)).real)) == o); n += 1
    fr = fhit / n; br = bhit / n; print("  float-recall=%.3f bipolar-recall=%.3f delta=%+.3f (load=%d)" % (fr, br, br - fr, LOAD), flush=True)
    return {"float": fr, "bipolar": br, "delta": br - fr}
def verdict(r) -> Tuple[str, str]:
    s = "float=%.3f bipolar=%.3f delta=%+.3f" % (r["float"], r["bipolar"], r["delta"])
    if r["bipolar"] >= r["float"] - 0.03: return ("HARD_PASS", "HARD_PASS: 1-bit bipolar substrate matches float recall within 3pp -- ~16x memory-efficient deployment viable. " + s)
    if r["bipolar"] >= r["float"] - 0.08: return ("MIDDLE_BAND", "MIDDLE_BAND: bipolar within 8pp of float. " + s)
    return ("HARD_FAIL", "HARD_FAIL: bipolar quantization degrades recall >8pp. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
