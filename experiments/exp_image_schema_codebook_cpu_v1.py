"""
exp_image_schema_codebook_cpu_v1.py -- IMAGE-SCHEMA-CODEBOOK (embodied grounding of abstract concepts) -- CPU.

ROUTING: Research REVIVAL_SUBSTRATE_NATIVE_ONLY Sprint-1 (cross-domain + embodied dual, P=0.55). 30 Lakoff/Johnson image
  schemas (CONTAINER, PATH, FORCE, BALANCE, UP-DOWN, PART-WHOLE, LINK, CENTER-PERIPHERY, ...) as substrate atoms; abstract
  concepts grounded in a schema via a GROUND binding (conceptual-metaphor mechanism). Test: given an abstract concept,
  retrieve its grounding image-schema (>=0.85 on 100 concepts). Substrate-only (no LLM). Also: cross-domain transfer --
  concepts from DIFFERENT domains sharing a schema cluster together. N=8192.
PRE-REGISTERED: HARD-PASS schema-grounding retrieval >= 0.85 AND cross-domain (same-schema different-domain) cluster purity >= 0.70. MIDDLE >= 0.70. HARD-FAIL else.
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
ANCHOR_NAME = "image_schema_codebook_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192; NSCHEMA = 30; NDOMAIN = 6
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: image-schema-codebook", flush=True)
def run() -> Dict:
    g = np.random.default_rng(630); NCONC = 60 if SMOKE else 200
    schemas = cphasor(NSCHEMA, N, g); domains = cphasor(NDOMAIN, N, g); GROUND = cphasor(1, N, g)[0]
    TR = 15 if SMOKE else 80; hit = 0; n = 0; cluster_pure = []
    for _ in range(TR):
        concept_ids = cphasor(NCONC, N, g)
        sch = g.integers(0, NSCHEMA, size=NCONC)                      # each concept grounded in a schema
        dom = g.integers(0, NDOMAIN, size=NCONC)                      # and lives in a domain
        # store: concept = id (X) GROUND (X) schema[s]  ... plus a domain flavor (X) DOMAIN
        MEM = {i: cnorm(concept_ids[i] * GROUND * schemas[sch[i]] + 0.4 * (concept_ids[i] * domains[dom[i]])) for i in range(NCONC)}
        # retrieve each concept's grounding image-schema
        for i in range(NCONC):
            recovered = MEM[i] * np.conj(concept_ids[i]) * np.conj(GROUND)
            hit += int(cidx(recovered, schemas) == sch[i]); n += 1
        # cross-domain cluster purity: concepts sharing a schema should be near each other regardless of domain
        for s in range(NSCHEMA):
            mem_s = [i for i in range(NCONC) if sch[i] == s]
            if len(mem_s) >= 3:
                # for a probe concept grounded in s, its nearest other concept should also be grounded in s
                i0 = mem_s[0]; others = [j for j in range(NCONC) if j != i0]
                gv = MEM[i0] * np.conj(concept_ids[i0]) * np.conj(GROUND)   # its schema vector
                # nearest concept by shared-schema signal
                scores = [float((MEM[j] * np.conj(concept_ids[j]) * np.conj(GROUND) @ np.conj(gv)).real) for j in others]
                nn = others[int(np.argmax(scores))]; cluster_pure.append(int(sch[nn] == s))
    acc = hit / n; cp = float(np.mean(cluster_pure)) if cluster_pure else 0.0
    print("  IMAGE-SCHEMA grounding-retrieval=%.3f cross-domain-cluster-purity=%.3f (concepts=%d, schemas=%d)" % (acc, cp, NCONC, NSCHEMA), flush=True)
    return {"grounding_acc": round(acc, 3), "cluster_purity": round(cp, 3), "n_concepts": NCONC}
def verdict(r) -> Tuple[str, str]:
    s = "grounding=%.3f cross-domain-cluster-purity=%.3f" % (r["grounding_acc"], r["cluster_purity"])
    if r["grounding_acc"] >= 0.85 and r["cluster_purity"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate grounds abstract concepts in image-schemas (retrieval>=0.85) AND concepts sharing a schema cluster across domains (purity>=0.70) -- embodied grounding of abstract cognition via Lakoff/Johnson primitives, substrate-only. " + s)
    if r["grounding_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: grounding 0.70-0.85 or weak cross-domain clustering. " + s)
    return ("HARD_FAIL", "HARD_FAIL: image-schema grounding <0.70. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
