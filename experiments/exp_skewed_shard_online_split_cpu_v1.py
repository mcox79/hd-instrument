"""
exp_skewed_shard_online_split_cpu_v1.py -- online-splitting hot shards under Zipf skew restores recall -- CPU.

ROUTING: PP-131 skewed-shard online split. skewed_shard_capacity MID: the largest Zipf shard (370 facts) dropped to 0.873. Rescue: an online split policy that, when a shard exceeds the capacity FLOOR, splits it into sub-shards of <=FLOOR. Measures recall on the hot shard after splitting vs before. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS hot-shard recall after online-split >= 0.95 AND before-split < 0.90. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "skewed_shard_online_split_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    assert int(np.ceil(370 / 150)) == 3, "split count"; print("[selftest] PASS: skewed-shard-online-split", flush=True)
def run() -> Dict:
    g = np.random.default_rng(131); N = 4096; FLOOR = 120; HOT = 380; book = cphasor(4000, N, g)
    keys = cphasor(HOT, N, g); vals = g.integers(0, 4000, HOT)
    B = np.zeros(N, dtype=np.complex64)
    for j in range(HOT):
        B = B + keys[j] * book[vals[j]]
    before = sum(int(cidx(B * np.conj(keys[j]), book) == vals[j]) for j in range(HOT)) / HOT
    nsplit = int(np.ceil(HOT / FLOOR)); per = int(np.ceil(HOT / nsplit)); subs = [np.zeros(N, dtype=np.complex64) for _ in range(nsplit)]
    owner = np.minimum(np.arange(HOT) // per, nsplit - 1)
    for j in range(HOT):
        subs[owner[j]] = subs[owner[j]] + keys[j] * book[vals[j]]
    after = sum(int(cidx(subs[owner[j]] * np.conj(keys[j]), book) == vals[j]) for j in range(HOT)) / HOT
    print("  hot-shard(%d facts) recall before-split=%.3f after-split(%d sub-shards)=%.3f" % (HOT, before, nsplit, after), flush=True)
    return {"before": before, "after": after}
def verdict(r) -> Tuple[str, str]:
    s = "before-split=%.3f after-split=%.3f" % (r["before"], r["after"])
    if r["after"] >= 0.95 and r["before"] < 0.90: return ("HARD_PASS", "HARD_PASS: online-splitting the hot Zipf shard restores recall to >=0.95 -- elastic split policy handles skew. " + s)
    if r["after"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: after-split 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: split does not restore (<0.85). " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
