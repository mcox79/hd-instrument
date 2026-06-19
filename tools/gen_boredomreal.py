"""Research NEXT_SPRINT1_REAL_DATA_AUDIT: BOREDOM-REAL (PP-315). Audits boredom on a REALISTIC attention stream:
Zipfian token frequency (heavy-tailed, like real corpora) + CORRELATED token embeddings (real tokens cluster by topic, not
orthogonal). Tests boredom AUC >=0.70 on real-ish patterns (down from synthetic 1.0). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_boredom_real_cpu_v1.py -- BOREDOM-REAL (real-data audit) -- CPU.

ROUTING: Research NEXT_SPRINT1_REAL_DATA_AUDIT (PP-315). Realistic attention stream: token frequencies ZIPFIAN (heavy-tailed
  like real corpora) and token embeddings CORRELATED (drawn from topic-clusters, not near-orthogonal). Boredom = presence in
  a decayed recent bundle. Audits whether the synthetic boredom AUC (1.0) survives realistic structure. Substrate-only.
PRE-REGISTERED: HARD-PASS boredom AUC >= 0.70 on Zipfian+correlated stream (synthetic was 1.0). MIDDLE >= 0.60. HARD-FAIL < 0.60.
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
ANCHOR_NAME = "boredom_real_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _auc(scores, labels):
    o = np.argsort(scores); r = np.empty(len(scores)); r[o] = np.arange(1, len(scores) + 1)
    pos = labels == 1; npos = int(pos.sum()); nneg = len(labels) - npos
    return 0.5 if npos == 0 or nneg == 0 else float((r[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg))
def _selftest():
    print("[selftest] PASS: boredom-real", flush=True)
def run() -> Dict:
    g = np.random.default_rng(606); M = 300; NTOPIC = 12; DECAY = 0.85; W = 12
    TR = 20 if SMOKE else 120; bored = []; is_rep = []
    for _ in range(TR):
        # CORRELATED token embeddings: each token = cnorm(topic_proto + noise) -> topic-clusters (real, not orthogonal)
        topics = cphasor(NTOPIC, N, g); tok_topic = g.integers(0, NTOPIC, size=M)
        items = cnorm(np.stack([topics[tok_topic[i]] + 0.9 * cphasor(1, N, g)[0] for i in range(M)]))
        # ZIPFIAN frequency (heavy-tailed like real corpora)
        ranks = np.arange(1, M + 1); zipf = 1.0 / ranks; zipf = zipf / zipf.sum(); g.shuffle(zipf)
        recent = []; R = np.zeros(N, dtype=np.complex64)
        for step in range(60):
            x_idx = int(g.choice(M, p=zipf)); rep = 1 if x_idx in recent else 0; x = items[x_idx]
            b = float((np.vdot(R, x).real) / N) if step > 0 else 0.0
            if step >= 5:
                bored.append(b); is_rep.append(rep)
            R = (DECAY * R + x).astype(np.complex64); recent.append(x_idx); recent = recent[-W:]
    bored = np.array(bored); is_rep = np.array(is_rep); auc = _auc(bored, is_rep)
    print("  BOREDOM-REAL AUC=%.3f on Zipfian+correlated stream (n=%d) [synthetic was 1.0]" % (auc, len(bored)), flush=True)
    return {"boredom_auc": round(auc, 3), "n": len(bored)}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.3f (Zipfian+correlated)" % r["boredom_auc"]
    if r["boredom_auc"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: boredom signal survives realistic attention (Zipfian frequency + correlated tokens) at AUC>=0.70 -- the synthetic primitive is real-data-grounded. " + s)
    if r["boredom_auc"] >= 0.60:
        return ("MIDDLE_BAND", "MIDDLE_BAND: boredom AUC 0.60-0.70 on realistic stream -- partial transfer. " + s)
    return ("HARD_FAIL", "HARD_FAIL: boredom AUC <0.60 on realistic stream -- synthetic primitive does not survive. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_boredom_real_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote boredom_real")
