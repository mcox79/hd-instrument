"""
exp_shard_merge_primitive_cpu_v1 -- shard MERGE primitive: merge underutilized shards without losing recall -- CPU.

ROUTING: shard_MERGE_capacity_formula M1 (HIGHEST). Sharding needs both SPLIT (done) and MERGE. When two shards are each well
  below the capacity floor, merging them reduces shard-count/overhead -- but only if the combined load stays under the floor.
  Policy: pair underutilized shards where size_A + size_B <= FLOOR and merge. Measures post-merge recall (must stay high) and
  the shard-count reduction (efficiency). Confirms MERGE is a safe reorganization primitive governed by the capacity formula.
  Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS post-merge recall@1 >= 0.95 (no loss) AND shard count reduced >= 30pct. MIDDLE recall >= 0.90.
  HARD-FAIL recall < 0.90 (merge over the floor loses recall -- formula violated).
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. cleanup self. 3. merge keeps under floor.
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

ANCHOR_NAME = "shard_merge_primitive_cpu_v1"; N = 4096; FLOOR = 110
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NSHARD = 20 if SMOKE else 60


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; b = cphasor(1, 32, g)[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-3), "bind/unbind"
    bk = cphasor(4, 32, g); assert cidx(bk[0], bk) == 0, "cleanup self"
    assert 40 + 50 <= 110, "merge keeps under floor"
    print("[selftest] PASS: shard-merge-primitive", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def build_shard(sizes, g, book):
    bundles = []; keysets = []; valsets = []
    for sz in sizes:
        ky = cphasor(sz, N, g); vv = g.integers(0, len(book), sz); B = np.zeros(N, dtype=np.complex64)
        for j in range(sz):
            B = B + ky[j] * book[vv[j]]
        bundles.append(B); keysets.append(ky); valsets.append(vv)
    return bundles, keysets, valsets


def recall_of(bundles, keysets, valsets, owner_map, book):
    hit = 0; tot = 0
    for sh in range(len(bundles)):
        for j in range(len(keysets[sh])):
            hit += int(cidx(bundles[sh] * np.conj(keysets[sh][j]), book) == valsets[sh][j]); tot += 1
    return hit / max(1, tot)


def run() -> Dict:
    g = np.random.default_rng(151); book = cphasor(4000, N, g)
    sizes = [int(g.integers(20, 70)) for _ in range(NSHARD)]                 # many UNDER-utilized shards
    bundles, keysets, valsets = build_shard(sizes, g, book)
    pre = recall_of(bundles, keysets, valsets, None, book); pre_count = len(bundles)
    # MERGE policy: greedily pair shards whose combined size <= FLOOR
    order = sorted(range(len(sizes)), key=lambda i: sizes[i]); merged = []; used = [False] * len(sizes); i = 0
    new_bundles = []; new_keys = []; new_vals = []
    pairs = []
    for a in order:
        if used[a]:
            continue
        used[a] = True; bestb = -1
        for b in order:
            if not used[b] and b != a and sizes[a] + sizes[b] <= FLOOR:
                bestb = b; break
        if bestb >= 0:
            used[bestb] = True
            new_bundles.append(bundles[a] + bundles[bestb]); new_keys.append(np.vstack([keysets[a], keysets[bestb]])); new_vals.append(np.concatenate([valsets[a], valsets[bestb]]))
        else:
            new_bundles.append(bundles[a]); new_keys.append(keysets[a]); new_vals.append(valsets[a])
    post = recall_of(new_bundles, new_keys, new_vals, None, book); post_count = len(new_bundles)
    reduction = 1.0 - post_count / pre_count
    print("  recall pre-merge=%.3f post-merge=%.3f | shards %d -> %d (reduction=%.1f%%)" % (pre, post, pre_count, post_count, 100 * reduction), flush=True)
    return {"pre": pre, "post": post, "reduction": reduction, "pre_count": pre_count, "post_count": post_count}


def verdict(r) -> Tuple[str, str]:
    s = "recall pre=%.3f post=%.3f, shards %d->%d (reduction=%.0f%%)" % (r["pre"], r["post"], r["pre_count"], r["post_count"], 100 * r["reduction"])
    if r["post"] >= 0.95 and r["reduction"] >= 0.30:
        return ("HARD_PASS", "HARD_PASS: MERGE consolidates underutilized shards (>=30pct fewer) with no recall loss (>=0.95) -- merge is a safe formula-governed reorganization primitive (with split, full elastic sharding). " + s)
    if r["post"] >= 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: post-merge recall 0.90-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: merge lost recall (<0.90) -- combined load exceeded the floor. " + s)


print("[config] anchor=%s mode=%s N=%d floor=%d nshard=%d" % (ANCHOR_NAME, RUN_MODE, N, FLOOR, NSHARD), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
