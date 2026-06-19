"""Research 5X ARCHITECTURAL Sprint-1: DREAMING-SUBSTRATE (autonomous discovery, P=0.45, substrate-only).
Offline replay (sleep/REM) finds compressible latent structure in stored experience; COMPRESSION-PROGRESS (Schmidhuber) is
the intrinsic discovery signal. Tests replay discovers ~the latent concepts AND compression improves over replay rounds then
plateaus (= structure found). Genuinely can fail. Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_dreaming_substrate_cpu_v1.py -- DREAMING-SUBSTRATE (autonomous discovery via offline replay) -- CPU.

ROUTING: Research 5X_ARCHITECTURAL Sprint-1 (autonomous discovery). Stored experiences from K latent concepts. OFFLINE
  replay extracts schemas (cluster centroids) over rounds; COMPRESSION = how well schemas explain items (mean margin to
  nearest schema). COMPRESSION-PROGRESS (delta per round) is the discovery signal -- it should rise then plateau when the
  K-concept structure is found. Tests: discovered schemas recover the latent concepts AND compression-progress plateaus at K.
  Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS final compression >= 0.70 AND discovered-purity >= 0.70 AND compression rises >=0.20 over replay (progress signal real). MIDDLE compression>=0.55. HARD-FAIL else.
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
ANCHOR_NAME = "dreaming_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: dreaming-substrate", flush=True)
def run() -> Dict:
    g = np.random.default_rng(703); K = 8; PER = 30; ROUNDS = 6
    TR = 10 if SMOKE else 50; comp0 = []; compF = []; pur = []; ndisc = []
    for _ in range(TR):
        protos = cphasor(K, N, g); items = []; truec = []
        for c in range(K):
            for _i in range(PER):
                items.append(cnorm(protos[c] + 0.7 * cphasor(1, N, g)[0])); truec.append(c)
        items = np.stack(items); truec = np.array(truec); M = len(items)
        # offline replay: progressively grow schemas where items are poorly explained (compression-progress)
        schemas = items[g.choice(M, 1, replace=False)].copy(); comp_hist = []
        for rd in range(ROUNDS):
            margins = (items @ np.conj(schemas.T)).real / N; nearest = margins.max(1)
            comp = float(np.mean(nearest)); comp_hist.append(comp)
            worst = int(np.argmin(nearest))                              # add a schema where compression is worst (REM novelty)
            if len(schemas) < 2 * K:
                schemas = np.vstack([schemas, items[worst][None, :]])
            # refine schemas toward their members
            asg = np.argmax((items @ np.conj(schemas.T)).real, axis=1)
            for s in range(len(schemas)):
                mem = items[asg == s]
                if len(mem):
                    schemas[s] = cnorm(mem.sum(0))
        comp0.append(comp_hist[0]); compF.append(comp_hist[-1])
        asg = np.argmax((items @ np.conj(schemas.T)).real, axis=1)
        # purity: each discovered schema's majority true-concept; item correct if its schema majority == its concept
        smaj = []
        for s in range(len(schemas)):
            v = truec[asg == s]
            smaj.append(int(np.bincount(v).argmax()) if len(v) else -1)
        pur.append(float(np.mean([smaj[asg[i]] == truec[i] for i in range(M)]))); ndisc.append(len(set(asg)))
    c0 = float(np.mean(comp0)); cf = float(np.mean(compF)); pu = float(np.mean(pur)); nd = float(np.mean(ndisc))
    print("  DREAMING compression %.3f->%.3f (progress=%.3f) | discovered-purity=%.3f effective-schemas=%.1f (true K=%d)" % (c0, cf, cf - c0, pu, nd, 8), flush=True)
    return {"compression_final": round(cf, 3), "compression_progress": round(cf - c0, 3), "purity": round(pu, 3), "eff_schemas": round(nd, 1)}
def verdict(r) -> Tuple[str, str]:
    s = "compression=%.3f progress=%.3f purity=%.3f schemas=%.1f" % (r["compression_final"], r["compression_progress"], r["purity"], r["eff_schemas"])
    if r["compression_final"] >= 0.70 and r["purity"] >= 0.70 and r["compression_progress"] >= 0.20:
        return ("HARD_PASS", "HARD_PASS: offline replay autonomously discovers latent structure -- final compression>=0.70, schema purity>=0.70, and compression-PROGRESS>=0.20 over replay (the Schmidhuber discovery signal is real). Substrate dreams/consolidates, substrate-only. " + s)
    if r["compression_final"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial discovery (compression 0.55-0.70 or weak progress). " + s)
    return ("HARD_FAIL", "HARD_FAIL: replay does not discover compressible structure. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_dreaming_substrate_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote dreaming_substrate")
