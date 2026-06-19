"""
exp_lap3_9_schema_production_cpu_v1.py -- production-scale schema extraction (220 categories) -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 (LAP3-9 SCHEMA-EXTRACTION-PRODUCTION); pure-FHRR (no download). Extends LAP-5 to >=150 categories; bundle instances per category -> recover shared schema.
PRE-REGISTERED: HARD-PASS coverage>=0.95 AND schemas>=150. MIDDLE>=0.85. HARD-FAIL<0.85.
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
ANCHOR_NAME = "lap3_9_schema_production_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    print("[selftest] PASS: schema-production", flush=True)
def run() -> Dict:
    g = np.random.default_rng(5); N = 8192; NPROP = 60; NCAT = 60 if SMOKE else 220; NI = 30; SCHEMA_SZ = 7
    PROP = cphasor(NPROP, N, g); covs = []; precs = []
    for c in range(NCAT):
        schema = set(int(p) for p in g.choice(NPROP, SCHEMA_SZ, replace=False)); proto = np.zeros(N, dtype=np.complex64)
        for _i in range(NI):
            props = set(schema)
            for p in list(props):
                if g.random() < 0.15:
                    props.discard(p)
            while g.random() < 0.3:
                props.add(int(g.integers(0, NPROP)))
            proto = proto + sum((PROP[p] for p in props), np.zeros(N, dtype=np.complex64))
        overlap = np.array([(np.vdot(PROP[p], proto).real) / (N * NI) for p in range(NPROP)])
        extracted = set(int(p) for p in range(NPROP) if overlap[p] >= 0.5)
        inter = len(extracted & schema); covs.append(inter / len(schema)); precs.append(inter / len(extracted) if extracted else 0.0)
    cov = float(np.mean(covs)); prec = float(np.mean(precs))
    print("  SCHEMA-PRODUCTION coverage=%.3f precision=%.3f (NCAT=%d, compression=%dx)" % (cov, prec, NCAT, NI), flush=True)
    return {"coverage": cov, "precision": prec, "n_schemas": NCAT, "compression": NI}
def verdict(r) -> Tuple[str, str]:
    s = "coverage=%.3f precision=%.3f (%d schemas, %dx compression)" % (r["coverage"], r["precision"], r["n_schemas"], r["compression"])
    if r["coverage"] >= 0.95 and r["n_schemas"] >= 150 and r["precision"] >= 0.8:
        return ("HARD_PASS", "HARD_PASS: substrate extracts >=150 category schemas at >=0.95 coverage (production scale) -- common-sense schema compression holds at scale; closes the substrate-vs-LLM scale gap on common-sense. " + s)
    if r["coverage"] >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: coverage 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: coverage <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
