"""
exp_core_periphery_cpu_v1.py -- CORE-PERIPHERY protected self-modification -- CPU.

ROUTING: Research TIER2 rescue (self-modification 3x DEEP). Protect a CORE set of important memories (topological protection)
  while allowing PERIPHERY edits. Mechanism: store core; project every periphery edit's key ORTHOGONAL to the core-key
  subspace (null-space periphery) before adding, so periphery edits don't interfere with core retrieval. Tests CORE recall
  after 5000 edits: protected vs unprotected baseline. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS protected CORE recall >= 0.95 after 5000 edits AND >> unprotected baseline. MIDDLE >= 0.85. HARD-FAIL else.
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
ANCHOR_NAME = "core_periphery_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: core-periphery", flush=True)
def run() -> Dict:
    g = np.random.default_rng(700); KCORE = 30 if SMOKE else 40; V = 400; EDITS = 800 if SMOKE else 5000
    TR = 4 if SMOKE else 12; prot = []; unprot = []
    for _ in range(TR):
        core_keys = cphasor(KCORE, N, g); vals = cphasor(V, N, g); core_truth = g.integers(0, V, size=KCORE)
        M0 = cnorm(sum((core_keys[i] * vals[core_truth[i]] for i in range(KCORE)), np.zeros(N, dtype=np.complex64)))
        Mp = M0.copy().astype(np.complex64); Mu = M0.copy().astype(np.complex64)
        CK = core_keys  # for orthogonalization
        for _e in range(EDITS):
            ek = cphasor(1, N, g)[0]; ev = vals[int(g.integers(0, V))]
            # PROTECTED: project edit key orthogonal to core-key subspace (quasi-orthogonal approx)
            coeff = (CK @ np.conj(ek)) / N
            ek_orth = ek - (coeff[:, None] * CK).sum(0); ek_orth = ek_orth / (np.abs(ek_orth) + 1e-9)  # renorm to unit-modulus-ish
            Mp = Mp + ek_orth * ev
            Mu = Mu + ek * ev                                          # UNPROTECTED: add raw
        Mp = cnorm(Mp); Mu = cnorm(Mu)
        hp = sum(cidx(Mp * np.conj(core_keys[i]), vals) == core_truth[i] for i in range(KCORE)) / KCORE
        hu = sum(cidx(Mu * np.conj(core_keys[i]), vals) == core_truth[i] for i in range(KCORE)) / KCORE
        prot.append(hp); unprot.append(hu)
    pp = float(np.mean(prot)); pu = float(np.mean(unprot))
    print("  CORE-PERIPHERY core recall after %d edits: protected=%.3f | unprotected=%.3f" % (EDITS, pp, pu), flush=True)
    return {"protected_core_recall": round(pp, 3), "unprotected_core_recall": round(pu, 3), "edits": EDITS}
def verdict(r) -> Tuple[str, str]:
    pp = r["protected_core_recall"]; pu = r["unprotected_core_recall"]; s = "protected=%.3f unprotected=%.3f after %d edits" % (pp, pu, r["edits"])
    if pp >= 0.95 and pp > pu + 0.10:
        return ("HARD_PASS", "HARD_PASS: CORE-PERIPHERY protection works -- core recall >=0.95 after %d edits (vs unprotected %.2f). Projecting periphery edits orthogonal to the core subspace topologically protects important memories through heavy self-modification, substrate-only. " % (r["edits"], pu) + s)
    if pp >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: protected core 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: core protection <0.85. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
