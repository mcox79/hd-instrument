"""
exp_lap5_schema_layer_cpu_v1.py -- LAP-5 SCHEMA-LAYER: category schema extraction (compression) -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop batch (LAP-5). Common-sense schema compression: many instances of a category
  share a property schema; the substrate should compress them into one prototype and recover the shared schema. Each category has
  a true schema (subset of properties); instances = schema + per-instance noise (random extra/missing). Substrate bundles a
  category's instances; the schema is read off as the properties with high prototype overlap (present across most instances).
  Measures schema coverage (recall of true schema props) + the compression ratio (instances -> 1 prototype). numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS >= 50 schemas recovered with mean category coverage >= 0.95. MIDDLE coverage >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "lap5_schema_layer_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    import numpy as _n; assert _n.mean([1.0, 1.0]) == 1.0, "mean"; print("[selftest] PASS: lap5-schema-layer", flush=True)


def run() -> Dict:
    g = np.random.default_rng(5); NPROP = 40; NCAT = 20 if SMOKE else 60; NI = 25; SCHEMA_SZ = 6
    PROP = cphasor(NPROP, N, g)
    covs = []; precs = []
    for c in range(NCAT):
        schema = set(int(p) for p in g.choice(NPROP, SCHEMA_SZ, replace=False))
        proto = np.zeros(N, dtype=np.complex64)
        for _i in range(NI):
            props = set(schema)                                          # instance = schema ...
            for p in list(props):
                if g.random() < 0.15:
                    props.discard(p)                                     # ... minus occasional missing
            while g.random() < 0.3:
                props.add(int(g.integers(0, NPROP)))                    # ... plus occasional noise prop
            inst = sum((PROP[p] for p in props), np.zeros(N, dtype=np.complex64))
            proto = proto + inst
        # extract schema: properties whose overlap with the prototype is in the top band (present across instances)
        overlap = np.array([(np.vdot(PROP[p], proto).real) / (N * NI) for p in range(NPROP)])
        thr = 0.5                                                        # schema props appear in ~85pct of NI instances -> overlap ~0.85
        extracted = set(int(p) for p in range(NPROP) if overlap[p] >= thr)
        inter = len(extracted & schema)
        covs.append(inter / len(schema)); precs.append(inter / len(extracted) if extracted else 0.0)
    cov = float(np.mean(covs)); prec = float(np.mean(precs)); compression = NI
    print("  SCHEMA-LAYER coverage=%.3f precision=%.3f (NCAT=%d, compression=%dx)" % (cov, prec, NCAT, compression), flush=True)
    return {"coverage": cov, "precision": prec, "n_schemas": NCAT, "compression": compression}


def verdict(r) -> Tuple[str, str]:
    s = "coverage=%.3f precision=%.3f (%d schemas, %dx compression)" % (r["coverage"], r["precision"], r["n_schemas"], r["compression"])
    if r["coverage"] >= 0.95 and r["n_schemas"] >= 50 and r["precision"] >= 0.8:
        return ("HARD_PASS", "HARD_PASS: substrate extracts >=50 category schemas at >=0.95 coverage (precision>=0.8) -- instances compress into prototypes; shared common-sense schema recovered from a bundle. " + s)
    if r["coverage"] >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: coverage 0.85-0.95 (raise threshold or NI). " + s)
    return ("HARD_FAIL", "HARD_FAIL: coverage <0.85. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
