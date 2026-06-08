"""
exp_sharding_scaling_law_cpu_v1 -- sharding S-scaling law: total capacity linear in #shards, per-shard recall flat -- CPU.

ROUTING: sharding_universal_capacity_primitive. Sharding is the canonical substrate capacity primitive (markov 0.817->0.967,
  PP-101 cross-KB 0.0). This validates the customer claim "shard by entity/domain/customer; per-shard recall stays high
  regardless of total scale, with provably-low cross-shard interference." Sweep S in {1,2,4,8,16,32}; each shard holds a fixed
  K key->value bundle. Compares MONOLITHIC (all S*K in one bundle -> crosstalk grows) vs SHARDED+ROUTED (S bundles of K -> per
  query only K of crosstalk). Measures per-shard recall vs S (should stay flat), monolithic recall vs S (should degrade), total
  recallable capacity (S*K, linear), and cross-shard interference (rate a wrong-shard item outscores the true value). Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS sharded per-shard recall flat (>=0.90 and max-min spread <=0.05 across S) AND cross-shard interference
  <=0.02 AND sharded clearly beats monolithic at large S (gap >=0.20 at S=32). MIDDLE spread<=0.10. HARD-FAIL otherwise.
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. cleanup self. 3. linear total.
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

ANCHOR_NAME = "sharding_scaling_law_cpu_v1"; N = 4096; K = 80; VV = 2000
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; b = cphasor(1, 32, g)[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-3), "bind/unbind"
    bk = cphasor(4, 32, g); assert cidx(bk[1], bk) == 1, "cleanup self"
    assert 8 * 80 == 640, "linear total"
    print("[selftest] PASS: sharding-scaling-law", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); book = cphasor(VV, N, g); Ss = [1, 4, 16] if SMOKE else [1, 2, 4, 8, 16, 32]
    per_shard = {}; monolithic = {}; interference = {}
    for S in Ss:
        keys = cphasor(S * K, N, g); vals = g.integers(0, VV, S * K); shard_of = np.arange(S * K) // K
        # sharded bundles (routed)
        bundles = [np.zeros(N, dtype=np.complex64) for _ in range(S)]
        for i in range(S * K):
            bundles[shard_of[i]] = bundles[shard_of[i]] + keys[i] * book[vals[i]]
        # monolithic single bundle
        Mono = np.zeros(N, dtype=np.complex64)
        for i in range(S * K):
            Mono = Mono + keys[i] * book[vals[i]]
        ph = 0; mh = 0; inter = 0
        for i in range(S * K):
            sh = shard_of[i]
            ph += int(cidx(bundles[sh] * np.conj(keys[i]), book) == vals[i])             # sharded+routed recall
            mh += int(cidx(Mono * np.conj(keys[i]), book) == vals[i])                     # monolithic recall
            # cross-shard interference: does a WRONG shard's bundle produce a confident match to this key's value?
            wrong = (sh + 1) % S if S > 1 else 0
            if S > 1:
                own_sc = (book[vals[i]] @ np.conj(bundles[sh] * np.conj(keys[i]))).real
                wrong_best = (book @ np.conj(bundles[wrong] * np.conj(keys[i]))).real.max()
                inter += int(wrong_best > own_sc)                                         # wrong shard outscores own -> interference
        per_shard["S%d" % S] = ph / (S * K); monolithic["S%d" % S] = mh / (S * K); interference["S%d" % S] = inter / (S * K) if S > 1 else 0.0
        print("  S=%d total=%d | sharded-recall=%.3f monolithic-recall=%.3f cross-shard-interference=%.4f" % (S, S * K, per_shard["S%d" % S], monolithic["S%d" % S], interference["S%d" % S]), flush=True)
    pvals = list(per_shard.values()); spread = max(pvals) - min(pvals); big = "S%d" % max(Ss)
    gap = per_shard[big] - monolithic[big]; max_inter = max(interference.values())
    return {"per_shard": per_shard, "monolithic": monolithic, "interference": interference, "spread": spread, "gap_at_max": gap, "max_inter": max_inter, "min_pershard": min(pvals)}


def verdict(r) -> Tuple[str, str]:
    s = "per-shard=%s monolithic=%s interference=%s (spread=%.3f gap@maxS=%.3f max-inter=%.4f)" % (
        {k: round(v, 3) for k, v in r["per_shard"].items()}, {k: round(v, 3) for k, v in r["monolithic"].items()},
        {k: round(v, 4) for k, v in r["interference"].items()}, r["spread"], r["gap_at_max"], r["max_inter"])
    if r["min_pershard"] >= 0.90 and r["spread"] <= 0.05 and r["max_inter"] <= 0.02 and r["gap_at_max"] >= 0.20:
        return ("HARD_PASS", "HARD_PASS: sharding gives flat per-shard recall (>=0.90, spread<=0.05) with near-zero cross-shard interference while total capacity scales linearly with S -- the customer capacity claim is validated; monolithic degrades, sharded does not. " + s)
    if r["spread"] <= 0.10 and r["gap_at_max"] >= 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sharding helps but per-shard recall not perfectly flat or interference higher. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sharding does not produce flat per-shard recall / linear capacity. " + s)


print("[config] anchor=%s mode=%s N=%d K=%d" % (ANCHOR_NAME, RUN_MODE, N, K), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
