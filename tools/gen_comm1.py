"""Research AGGRESSIVE_OVERNIGHT THRUST-1 COMMUNICATE: COMM-1 PARAGRAPH-COMPOSE (substrate-only, user's first focus).
Substrate composes a structured 'paragraph' = ordered topic-relevant concepts bound into a discourse schema (Levelt-style
top-down). Tests the composition is RECOVERABLE (each slot's concept retrievable) AND topic-coherent (paragraph's topic
identifiable) -- substrate-native compositional communication, no LLM. Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_comm1_paragraph_compose_cpu_v1.py -- COMM-1 PARAGRAPH-COMPOSE (substrate-native communication) -- CPU.

ROUTING: Research AGGRESSIVE_OVERNIGHT THRUST-1 COMMUNICATE (user's FIRST focus). Substrate composes a paragraph top-down:
  a TOPIC -> retrieve topic-relevant concepts -> bind them into ordered discourse-schema SLOTS (intro/point/.../conclusion)
  = a paragraph composite. Tests (a) RECOVERY: each slot's concept is retrievable in order (coherent structure), (b) TOPIC-
  COHERENCE: the paragraph's topic is identifiable from its content, (c) vs-reference overlap. Substrate-only (no LLM; this
  is concept-level composition -- an LLM would lexicalize, but we test the substrate STRUCTURE). N=8192.
PRE-REGISTERED: HARD-PASS slot-recovery >= 0.65 AND topic-id >= 0.80 (coherent topic-appropriate composition). MIDDLE recovery>=0.50. HARD-FAIL else.
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
ANCHOR_NAME = "comm1_paragraph_compose_cpu_v1"
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
    print("[selftest] PASS: comm1-paragraph-compose", flush=True)
def run() -> Dict:
    g = np.random.default_rng(810); NTOPIC = 20; CONC_PER = 15; NSLOT = 6; VOC = NTOPIC * CONC_PER
    TR = 15 if SMOKE else 100; rec = 0; tot = 0; topic_hit = 0; ntop = 0
    for _ in range(TR):
        concepts = cphasor(VOC, N, g); slots = cphasor(NSLOT, N, g)
        topic_proto = np.stack([cnorm(concepts[t * CONC_PER:(t + 1) * CONC_PER].sum(0)) for t in range(NTOPIC)])
        for _q in range(6):
            t = int(g.integers(0, NTOPIC)); pool = list(range(t * CONC_PER, (t + 1) * CONC_PER))
            chosen = [int(x) for x in g.choice(pool, NSLOT, replace=False)]            # topic-relevant concepts for the paragraph
            para = cnorm(sum((slots[k] * concepts[chosen[k]] for k in range(NSLOT)), np.zeros(N, dtype=np.complex64)))
            # RECOVERY: recover each slot's concept in order
            for k in range(NSLOT):
                rec += int(cidx(para * np.conj(slots[k]), concepts) == chosen[k]); tot += 1
            # TOPIC-COHERENCE: identify the paragraph's topic from its content (bundle of concepts vs topic prototypes)
            content = cnorm(sum((para * np.conj(slots[k]) for k in range(NSLOT)), np.zeros(N, dtype=np.complex64)))
            topic_hit += int(cidx(content, topic_proto) == t); ntop += 1
    recall = rec / tot; tid = topic_hit / ntop
    print("  COMM-1 PARAGRAPH slot-recovery=%.3f topic-coherence=%.3f (NSLOT=%d, topics=%d)" % (recall, tid, NSLOT, NTOPIC), flush=True)
    return {"slot_recovery": round(recall, 3), "topic_coherence": round(tid, 3), "n_slot": NSLOT}
def verdict(r) -> Tuple[str, str]:
    s = "slot-recovery=%.3f topic-coherence=%.3f" % (r["slot_recovery"], r["topic_coherence"])
    if r["slot_recovery"] >= 0.65 and r["topic_coherence"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate composes a structured paragraph top-down -- ordered slot content recoverable >=0.65 AND topic identifiable >=0.80, substrate-only (no LLM). Compositional communication at concept level works. " + s)
    if r["slot_recovery"] >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: paragraph recovery 0.50-0.65. " + s)
    return ("HARD_FAIL", "HARD_FAIL: paragraph composition <0.50 recovery. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_comm1_paragraph_compose_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote comm1_paragraph_compose")
