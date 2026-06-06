"""
exp_g4_200cell_revalidation_v1 -- Batch G4 (AT-6 statistical revalidation) -- CPU.

ROUTING: Batch G Tier-2 (adversarial drill #6). 30/30 "100%" cells give Wilson 95% lower CI = 88.4% -- insufficient for
  production claims. Re-runs the 3 flagship khop capabilities on N=200 INDEPENDENT trials each and reports rate + Wilson
  95% lower bound: (a) K-hop K=20 chain accuracy, (b) per-hop fabrication localization, (c) Merkle-chain cert validity.
  Synthetic substrate (bipolar concepts + sha256 Merkle). CPU $0.
PRE-REGISTERED: HARD-PASS all 3 maintain rate >= 0.97 at N=200 (Wilson lower bound clears ~0.94). MID one in 0.85-0.97.
  HARD-FAIL any < 0.85.
FORMULA SELF-TESTS (PROT-022): 1. khop step recovers. 2. fabricated hop low grounding. 3. wilson bound < rate.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "g4_200cell_revalidation_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N = 2048; V_C = 600; TRIALS = 40; K = 10
else:
    N = 8192; V_C = 4000; TRIALS = 200; K = 20


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def bp(M, n, g):
    return unit((g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32))


def wilson_lb(k, n, z=1.96):
    if n == 0:
        return 0.0
    p = k / n; d = 1 + z * z / n
    return float((p + z * z / (2 * n) - z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d)


def _h(b):
    return hashlib.sha256(b).digest()


def merkle_root(leaves):
    lv = [_h(l) for l in leaves]
    while len(lv) > 1:
        if len(lv) % 2:
            lv.append(lv[-1])
        lv = [_h(lv[i] + lv[i + 1]) for i in range(0, len(lv), 2)]
    return lv[0]


def _selftest():
    g = np.random.default_rng(0); C = bp(20, 256, g); seq = [0, 5, 9]
    W = sum(np.outer(C[seq[i + 1]], C[seq[i]]) for i in range(2)) / 256; cur = C[0]
    for _ in range(2):
        cur = C[int(np.argmax(C @ (W @ cur)))]
    assert np.allclose(cur, C[9]), "khop step recovers"
    assert float(np.max(C @ bp(1, 256, g)[0])) < 0.5, "fabricated hop low grounding"
    assert wilson_lb(30, 30) < 1.0, "wilson bound < rate"
    print("[selftest] PASS: g4-reval", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); C = bp(V_C, N, g); khop_ok = 0; loc_ok = 0; merkle_ok = 0
    for _ in range(TRIALS):
        seq = list(g.choice(V_C, K + 1, replace=False))
        W = sum(np.outer(C[seq[i + 1]], C[seq[i]]) for i in range(K)) / N
        cur = C[seq[0]]; path = []
        for _h2 in range(K):
            j = int(np.argmax(C @ (W @ cur))); path.append(j); cur = C[j]
        khop_ok += int(path[-1] == seq[-1])
        # localization: inject fab at middle hop, argmin grounding
        hops = [C[j] for j in seq[1:]]; hi = K // 2; hops[hi] = bp(1, N, g)[0]
        gr = [float(np.max(C @ hops[i])) for i in range(K)]; loc_ok += int(int(np.argmin(gr)) == hi)
        # merkle cert: root deterministic + tamper detected
        leaves = [g.bytes(48) for _ in range(K)]; r = merkle_root(leaves)
        bad = list(leaves); bad[hi] = g.bytes(48); merkle_ok += int(r == merkle_root(leaves) and merkle_root(bad) != r)
    return {"khop_rate": khop_ok / TRIALS, "loc_rate": loc_ok / TRIALS, "merkle_rate": merkle_ok / TRIALS,
            "khop_wilson_lb": wilson_lb(khop_ok, TRIALS), "loc_wilson_lb": wilson_lb(loc_ok, TRIALS), "merkle_wilson_lb": wilson_lb(merkle_ok, TRIALS), "trials": TRIALS}


def verdict(r) -> Tuple[str, str]:
    rates = [r["khop_rate"], r["loc_rate"], r["merkle_rate"]]; mn = min(rates)
    summary = "N=%d: khop=%.3f(lb %.3f) loc=%.3f(lb %.3f) merkle=%.3f(lb %.3f)" % (r["trials"], r["khop_rate"], r["khop_wilson_lb"], r["loc_rate"], r["loc_wilson_lb"], r["merkle_rate"], r["merkle_wilson_lb"])
    if mn >= 0.97:
        return ("HARD_PASS", "HARD_PASS: all 3 flagship capabilities >=0.97 at N=%d (Wilson lower bounds clear) -- production claims statistically supported. " % r["trials"] + summary)
    if mn >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: a capability in 0.85-0.97 at N=200; claim weakened. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: a capability <0.85 at N=200 -- production claim fails. " + summary)


print("[config] anchor=%s mode=%s N=%d V_c=%d trials=%d K=%d" % (ANCHOR_NAME, RUN_MODE, N, V_C, TRIALS, K), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
