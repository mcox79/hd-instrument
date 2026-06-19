"""
exp_comp_a5_provenance_crossshard_cpu_v1.py -- cross-shard 3-hop chain preserves provenance at every hop -- CPU.

ROUTING: POST-CYCLE192 Group A composition (A5 provenance+cross-shard chain (PP-157 + PP-141)). A 3-hop chain crosses 3 shards (A in shard1 -> B in shard2 -> C in shard3); each hop's fact carries a SOURCE. After traversing the chain, recover both the endpoint AND each hop's provenance. Validates provenance survives cross-shard chaining. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS endpoint recall >= 0.95 AND per-hop provenance fidelity = 100pct over the 3-hop chain. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "comp_a5_provenance_crossshard_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())

def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; r = cphasor(1, 32, g)[0]; o = cphasor(1, 32, g)[0]; s = cphasor(1, 32, g)[0]
    assert np.allclose(a * r * o * s * np.conj(a * r), o * s, atol=1e-3), "prov chain bind"; print("[selftest] PASS: comp-a5-provenance-crossshard", flush=True)
def run() -> Dict:
    g = np.random.default_rng(405); N = 16384; VE = 150; NS = 12; REL = cphasor(1, N, g)[0]; PROVTAG = cphasor(1, N, g)[0]; TR = 40 if SMOKE else 120
    ents = cphasor(VE, N, g); srcs = cphasor(NS, N, g)
    end_hit = 0; prov_hit = 0; prov_tot = 0; n = 0
    for _ in range(TR):
        # 3 shards, one hop each; fact = head*REL*tail (edge) + head*REL*PROVTAG*source (provenance role -- separable)
        chain = g.choice(VE, 4, replace=False); chsrc = g.integers(0, NS, 3)
        shards = []
        for h in range(3):
            hd = ents[int(chain[h])] * REL
            sh = hd * ents[int(chain[h + 1])] + hd * PROVTAG * srcs[int(chsrc[h])]
            for _d in range(3):                                                # distractor edges in same shard
                a = int(g.integers(0, VE)); b = int(g.integers(0, VE)); sh = sh + ents[a] * REL * ents[b]
            shards.append(sh)
        cur = int(chain[0]); ok_chain = True
        for h in range(3):
            payload = shards[h] * np.conj(ents[cur] * REL)                     # -> tail + PROVTAG*source
            tail = cidx(payload, ents); src = cidx(payload * np.conj(PROVTAG), srcs)
            prov_hit += int(src == int(chsrc[h])); prov_tot += 1
            if tail != int(chain[h + 1]):
                ok_chain = False
            cur = tail
        end_hit += int(cur == int(chain[3]) and ok_chain); n += 1
    er = end_hit / n; pr = prov_hit / prov_tot; print("  endpoint-recall=%.3f provenance-fidelity=%.3f" % (er, pr), flush=True)
    return {"endpoint": er, "provenance": pr}
def verdict(r) -> Tuple[str, str]:
    s = "endpoint=%.3f provenance=%.3f" % (r["endpoint"], r["provenance"])
    if r["endpoint"] >= 0.95 and r["provenance"] >= 0.999: return ("HARD_PASS", "HARD_PASS: cross-shard 3-hop chain reaches endpoint >=0.95 with 100pct provenance fidelity -- provenance + cross-shard chaining compose. " + s)
    if r["endpoint"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: endpoint 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: endpoint <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
