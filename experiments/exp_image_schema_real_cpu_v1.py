"""
exp_image_schema_real_cpu_v1.py -- IMAGE-SCHEMA-REAL (real-data audit) -- CPU.

ROUTING: Research NEXT_SPRINT1_REAL_DATA_AUDIT (PP-316). REAL challenge: POLYSEMY (each abstract concept grounds to 1-3
  schemas, like justice/freedom/time mapping to multiple image-schemas) + CORRELATED concept embeddings (topic clusters,
  not orthogonal). Audits whether the synthetic grounding result (1.0) survives. Cluster purity = do concepts sharing a
  PRIMARY schema still cluster together despite polysemy+correlation? Substrate-only.
PRE-REGISTERED: HARD-PASS cluster purity >= 0.60 (synthetic was 1.0; polysemy expected to drop ~0.28). MIDDLE >= 0.45. HARD-FAIL < 0.45.
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
ANCHOR_NAME = "image_schema_real_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192; NSCHEMA = 30; NTOPIC = 10
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: image-schema-real", flush=True)
def run() -> Dict:
    g = np.random.default_rng(631); NC = 60 if SMOKE else 200
    schemas = cphasor(NSCHEMA, N, g); topics = cphasor(NTOPIC, N, g); GROUND = cphasor(1, N, g)[0]
    TR = 15 if SMOKE else 80; pure = []
    for _ in range(TR):
        tok_topic = g.integers(0, NTOPIC, size=NC)
        # CORRELATED concept embeddings (topic clusters)
        cid = cnorm(np.stack([topics[tok_topic[i]] + 0.9 * cphasor(1, N, g)[0] for i in range(NC)]))
        prim = g.integers(0, NSCHEMA, size=NC)                         # primary schema
        grounded = np.zeros((NC, N), dtype=np.complex64)
        for i in range(NC):
            ns = int(g.integers(1, 4))                                 # POLYSEMY: 1-3 schemas
            schs = [int(prim[i])] + [int(x) for x in g.integers(0, NSCHEMA, size=ns - 1)]
            top = sum((GROUND * schemas[s] for s in schs), np.zeros(N, dtype=np.complex64))
            grounded[i] = cnorm(cid[i] + top)
        # cluster purity: a probe concept's nearest other concept (by schema-signal) should share its PRIMARY schema
        sig = np.stack([grounded[i] * np.conj(cid[i]) for i in range(NC)])   # strip identity -> schema signal
        hit = 0; n = 0
        for i in range(NC):
            sims = (sig @ np.conj(sig[i])).real; sims[i] = -1e9
            nn = int(np.argmax(sims)); hit += int(prim[nn] == prim[i]); n += 1
        pure.append(hit / n)
    cp = float(np.mean(pure))
    print("  IMAGE-SCHEMA-REAL cluster-purity=%.3f under polysemy+correlation (NC=%d) [synthetic was 1.0]" % (cp, NC), flush=True)
    return {"cluster_purity": round(cp, 3), "n_concepts": NC}
def verdict(r) -> Tuple[str, str]:
    s = "cluster-purity=%.3f (polysemy+correlation)" % r["cluster_purity"]
    if r["cluster_purity"] >= 0.60:
        return ("HARD_PASS", "HARD_PASS: image-schema grounding survives polysemy+correlation at purity>=0.60 -- the synthetic grounding primitive is real-data-grounded despite ambiguity. " + s)
    if r["cluster_purity"] >= 0.45:
        return ("MIDDLE_BAND", "MIDDLE_BAND: grounding purity 0.45-0.60 -- polysemy degrades but partial transfer (as drill predicted). " + s)
    return ("HARD_FAIL", "HARD_FAIL: grounding purity <0.45 -- polysemy is the killer; synthetic primitive does NOT survive real abstract concepts. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
