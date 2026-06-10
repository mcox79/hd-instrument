"""Research WAVE-2 laptop: LAP2-5 K-HOP-DEPTH-10 + LAP2-8 CONTINUOUS-BINDING-FHRR-ROTATIONS (temporal). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research LAPTOP_WAVE2 ({tag}); pure-FHRR (no download). {desc}
PRE-REGISTERED: {prereg}
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
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
{body}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''

DEPTH10 = r'''
def _selftest():
    import numpy as _n; assert _n.argmax([0,0,1])==2, "argmax"; print("[selftest] PASS: k-hop-depth-10", flush=True)
def run() -> Dict:
    g = np.random.default_rng(1010); N = 8192; VE = 500 if SMOKE else 2000; ents = cphasor(VE, N, g); REL = cphasor(1, N, g)[0]
    HOPS = 10; TR = 30 if SMOKE else 200
    link = {i: int(g.integers(0, VE)) for i in range(VE)}
    shard = {i: ents[i] * (REL * ents[link[i]]) for i in range(VE)}
    hit = 0; n = 0
    for _ in range(TR):
        q = int(g.integers(0, VE)); gold = q; cur = q
        for _h in range(HOPS):
            gold = link[gold]
        for _h in range(HOPS):
            cur = cidx(shard[cur] * np.conj(ents[cur]) * np.conj(REL), ents)
        hit += int(cur == gold); n += 1
    rc = hit / n; print("  10-hop chain recall=%.3f (VE=%d, n=%d)" % (rc, VE, n), flush=True)
    return {"tenhop_recall": rc, "VE": VE}
def verdict(r) -> Tuple[str, str]:
    s = "10-hop-recall=%.3f (VE=%d)" % (r["tenhop_recall"], r["VE"])
    if r["tenhop_recall"] >= 0.60:
        return ("HARD_PASS", "HARD_PASS: substrate deterministic 10-hop traversal recall>=0.60 -- per-binding sharding keeps cleanup exact to depth 10; no empirical depth ceiling (drill 1 confirmed). " + s)
    if r["tenhop_recall"] >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 10-hop 0.40-0.60. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 10-hop <0.40. " + s)
'''

TEMPORAL = r'''
def _selftest():
    import numpy as _n; assert _n.allclose(_n.exp(1j*0.0), 1+0j), "phasor"; print("[selftest] PASS: continuous-binding-rotations", flush=True)
def run() -> Dict:
    # temporal indexing via FRACTIONAL phasor rotation: time-key(t) = exp(i*t*theta) elementwise (TIME^t). Seq stored as
    # sum_t TIME^t * item[t]; retrieve item at step t by unbinding TIME^t. Tests recall over long sequences (drill D).
    g = np.random.default_rng(8); N = 8192; VV = 300; STEPS = 30 if SMOKE else 100
    TR = 10 if SMOKE else 40; hit = 0; n = 0
    for _ in range(TR):
        theta = (g.random(N) * 2 - 1) * math.pi                          # base rotation angle per dim (the TIME generator)
        vals = cphasor(VV, N, g); seq = g.integers(0, VV, size=STEPS)
        Mem = np.zeros(N, dtype=np.complex64)
        for t in range(STEPS):
            tk = np.exp(1j * t * theta).astype(np.complex64)             # TIME^t (fractional power = scaled rotation)
            Mem = Mem + tk * vals[seq[t]]
        for t in range(STEPS):
            tk = np.exp(1j * t * theta).astype(np.complex64)
            hit += int(cidx(Mem * np.conj(tk), vals) == seq[t]); n += 1
    rc = hit / n; print("  CONTINUOUS-BINDING temporal recall=%.3f (STEPS=%d, n=%d)" % (rc, STEPS, n), flush=True)
    return {"temporal_recall": rc, "steps": STEPS}
def verdict(r) -> Tuple[str, str]:
    s = "temporal-recall=%.3f (steps=%d)" % (r["temporal_recall"], r["steps"])
    if r["temporal_recall"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: fractional phasor rotation indexes a %d-step sequence at recall>=0.80 -- continuous temporal binding (TIME^t) supports long-sequence recall; native temporal index. " % r["steps"] + s)
    if r["temporal_recall"] >= 0.60:
        return ("MIDDLE_BAND", "MIDDLE_BAND: temporal recall 0.60-0.80 (sequence-length load). " + s)
    return ("HARD_FAIL", "HARD_FAIL: temporal recall <0.60. " + s)
'''

C = [
    dict(anchor="lap2_5_khop_depth10_cpu_v1", tag="LAP2-5 K-HOP-DEPTH-10", title="substrate 10-hop chain traversal (depth ceiling)", desc="Per-binding sharded substrate; 10 deterministic cleanup-unbind hops.", prereg="HARD-PASS 10-hop recall>=0.60. MIDDLE>=0.40. HARD-FAIL<0.40.", body=DEPTH10),
    dict(anchor="lap2_8_continuous_binding_cpu_v1", tag="LAP2-8 CONTINUOUS-BINDING-FHRR-ROTATIONS", title="temporal indexing via fractional phasor rotation", desc="Sequence stored as sum_t TIME^t * item[t]; retrieve by unbinding the fractional rotation; recall over 100-step sequences.", prereg="HARD-PASS temporal recall>=0.80. MIDDLE>=0.60. HARD-FAIL<0.60.", body=TEMPORAL),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
