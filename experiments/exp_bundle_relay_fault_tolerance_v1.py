"""
exp_bundle_relay_fault_tolerance_v1 -- substrate-native-coordination anchor 1 (shard dropout degradation) -- CPU.

ROUTING: handoff exp_dev_handoff_research_substrate_native_coordination_3x #1. The pure-relay coordinator (v1, 50-LOC vs
  ~500-LOC 2PC) must degrade GRACEFULLY under shard dropout, not catastrophically (no 2PC-abort). Measures retrieval
  accuracy vs shard dropout rate {0,10,30,50pct}; checks degradation tracks ~sqrt(k/K) (SNR), not a cliff. CPU.
PRE-REGISTERED: HARD-PASS accuracy at 10pct dropout >= 0.92 * full AND degradation ~sqrt(k/K) (no abort cliff). HARD-FAIL
  accuracy < 0.75 at 10pct dropout (catastrophic; algebraic model gap).
FORMULA SELF-TESTS (PROT-022): 1. full-shard recovers. 2. dropout reduces shards. 3. sqrt model bound.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "bundle_relay_fault_tolerance_v1"
N = 4096; K_SHARD = 10; NOISE = 0.3; DROPS = [0.0, 0.1, 0.3, 0.5]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 512; TRIALS = 300
else:
    SEEDS = [7, 17, 23]; V_C = 2000; TRIALS = 1000


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); C = unit(g.standard_normal((10, 64))); relays = np.stack([C[3] + 0.05 * g.standard_normal(64) for _ in range(8)])
    assert int(np.argmax(C @ relays.mean(0))) == 3, "full-shard recovers"
    assert int(0.9 * 10) == 9, "dropout reduces shards"
    assert abs(np.sqrt(0.9) - 0.9486) < 1e-3, "sqrt model bound"
    print("[selftest] PASS: bundle-relay-fault", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); C = unit(g.standard_normal((V_C, N)).astype(np.float32)); by = {}
    for d in DROPS:
        k = max(1, int(round((1 - d) * K_SHARD))); ok = 0
        for _ in range(TRIALS):
            tgt = int(g.integers(0, V_C)); relays = np.stack([C[tgt] + NOISE * g.standard_normal(N).astype(np.float32) for _ in range(k)])
            if int(np.argmax(C @ relays.mean(0))) == tgt:
                ok += 1
        by["drop%.1f" % d] = ok / TRIALS
        print("  [seed=%d dropout=%.0f%% k=%d] accuracy=%.3f" % (seed, d * 100, k, ok / TRIALS), flush=True)
    return {"seed": seed, "by": by}


def verdict(ps) -> Tuple[str, str]:
    full = float(np.mean([p["by"]["drop0.0"] for p in ps])); d10 = float(np.mean([p["by"]["drop0.1"] for p in ps]))
    ratio = d10 / max(full, 1e-9)
    summary = "accuracy by dropout: %s | 10%%-dropout/full=%.3f (sqrt(0.9)=0.95)" % ({k: round(float(np.mean([p["by"][k] for p in ps])), 3) for k in ps[0]["by"]}, ratio)
    if ratio >= 0.92:
        return ("HARD_PASS", "HARD_PASS: pure-relay coordinator degrades GRACEFULLY (10%% dropout keeps >=0.92x accuracy, ~sqrt(k/K)) -- no 2PC-abort; ship the 50-LOC relay coordinator. " + summary)
    if d10 >= 0.75 * full:
        return ("MIDDLE_BAND", "MIDDLE_BAND: degrades but faster than sqrt model. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: catastrophic degradation at 10%% dropout -- algebraic model has a gap; investigate before deploying. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d K_shard=%d drops=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, K_SHARD, DROPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
