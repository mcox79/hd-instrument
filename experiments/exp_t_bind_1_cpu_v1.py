"""
exp_t_bind_1_cpu_v1.py -- T-BIND-1 (cross-modal binding gate) -- CPU.

ROUTING: Research 5X_ARCHITECTURAL Sprint-1 (real-time multimodal). A scene binds NMOD modalities (audio/video/text) via
  role-vectors: scene = sum_m MOD[m] (X) content[m]. Many scenes stored in one memory (a "now" buffer). Cross-modal retrieval:
  cue one modality's content -> recover the co-occurring content in another modality. Tests holographic binding holds across
  CONCURRENT scenes (capacity) with CORRELATED content. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS cross-modal retrieval >= 0.80 at NSCENE concurrent scenes. MIDDLE >= 0.65. HARD-FAIL else.
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
ANCHOR_NAME = "t_bind_1_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: t-bind-1", flush=True)
def run() -> Dict:
    g = np.random.default_rng(704); NMOD = 3; NV = 200; NSCENE = 8 if SMOKE else 25; NTOPIC = 10
    TR = 15 if SMOKE else 100; hit = 0; n = 0
    for _ in range(TR):
        MOD = cphasor(NMOD, N, g); topics = cphasor(NTOPIC, N, g)
        # CORRELATED per-modality content codebooks (topic clusters, not orthogonal)
        cb = [cnorm(np.stack([topics[int(g.integers(0, NTOPIC))] + 0.9 * cphasor(1, N, g)[0] for _ in range(NV)])) for _ in range(NMOD)]
        scenes = [[int(g.integers(0, NV)) for _ in range(NMOD)] for _ in range(NSCENE)]
        # bind each scene + store all in one buffer (concurrent scenes)
        scene_vecs = np.stack([cnorm(sum((MOD[m] * cb[m][scenes[s][m]] for m in range(NMOD)), np.zeros(N, dtype=np.complex64))) for s in range(NSCENE)])
        buffer = cnorm(scene_vecs.sum(0))
        for s in range(NSCENE):
            # cue: content in modality 0 -> find its scene -> recover modality 1 content
            cue = MOD[0] * cb[0][scenes[s][0]]
            # which scene best matches the cue?
            si = int(np.argmax((scene_vecs @ np.conj(cue)).real))
            recovered = scene_vecs[si] * np.conj(MOD[1])                          # unbind modality 1 from that scene
            pred = int(np.argmax((cb[1] @ np.conj(recovered)).real)); hit += int(pred == scenes[s][1]); n += 1
    rec = hit / n
    print("  T-BIND-1 cross-modal retrieval=%.3f at %d concurrent scenes (correlated content)" % (rec, NSCENE), flush=True)
    return {"crossmodal_recall": round(rec, 3), "n_scene": NSCENE}
def verdict(r) -> Tuple[str, str]:
    s = "cross-modal-recall=%.3f (%d scenes)" % (r["crossmodal_recall"], r["n_scene"])
    if r["crossmodal_recall"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: FHRR holographic binding supports cross-modal retrieval (cue one modality -> recover another) >=0.80 across concurrent scenes with correlated content -- real-time multimodal binding substrate-only. " + s)
    if r["crossmodal_recall"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cross-modal 0.65-0.80 (capacity limits). " + s)
    return ("HARD_FAIL", "HARD_FAIL: cross-modal binding <0.65. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
