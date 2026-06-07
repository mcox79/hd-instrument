"""
exp_subs_merkle_path_overhead_v1 -- reactive-subscriptions anchor 3 -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_reactive_subscriptions (#3). The cryptographic delivery (merkle_path per
  subscription event) is the claimed moat; if path generation is too slow it blocks WebSocket push. Measures Merkle
  authentication-path generation time per delivery as the log grows. CPU $0.
PRE-REGISTERED (research bands): HARD-PASS < 10ms per delivery (compatible with <50ms push). MID 10-50ms (acceptable if
  pre-computed at write time). HARD-FAIL > 50ms (blocks push; needs async path delivery).
FORMULA SELF-TESTS (PROT-022): 1. path verifies to root. 2. wrong leaf fails. 3. path length ~log2(n).
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "subs_merkle_path_overhead_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SIZES = [1024, 8192] if RUN_MODE == "smoke" else [1024, 16384, 131072, 1048576]
N_TRIAL = 50 if RUN_MODE == "smoke" else 500


def _h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def build_levels(leaves):
    levels = [leaves]
    while len(levels[-1]) > 1:
        cur = levels[-1]
        if len(cur) % 2:
            cur = cur + [cur[-1]]
        levels.append([_h(cur[i] + cur[i + 1]) for i in range(0, len(cur), 2)])
    return levels


def gen_path(levels, idx):
    path = []
    for lvl in levels[:-1]:
        sib = idx ^ 1; sib = sib if sib < len(lvl) else idx
        path.append((lvl[sib], idx & 1)); idx //= 2
    return path


def verify_path(leaf, path, root):
    h = leaf
    for sib, is_right in path:
        h = _h(sib + h) if is_right else _h(h + sib)
    return h == root


def _selftest():
    leaves = [_h(b"f%d" % i) for i in range(8)]; levels = build_levels(leaves); root = levels[-1][0]
    assert verify_path(leaves[3], gen_path(levels, 3), root), "path verifies to root"
    assert not verify_path(_h(b"wrong"), gen_path(levels, 3), root), "wrong leaf fails"
    assert len(gen_path(levels, 0)) == 3, "path length log2(n)"
    print("[selftest] PASS: merkle-path", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); by = {}
    for n in SIZES:
        leaves = [_h(b"fact_%d" % i) for i in range(n)]; levels = build_levels(leaves)
        idxs = g.integers(0, n, N_TRIAL); t0 = time.perf_counter()
        for idx in idxs:
            _ = gen_path(levels, int(idx))
        dt = (time.perf_counter() - t0) / N_TRIAL
        by["n%d" % n] = {"ms_per_path": dt * 1e3, "path_len": len(gen_path(levels, 0))}
        print("  [log_size=%d] %.4f ms/path (path_len=%d)" % (n, dt * 1e3, len(gen_path(levels, 0))), flush=True)
    return {"by": by}


def verdict(r) -> Tuple[str, str]:
    worst = max(v["ms_per_path"] for v in r["by"].values())
    summary = "ms/path by log size: %s | worst=%.4fms" % ({k: round(v["ms_per_path"], 4) for k, v in r["by"].items()}, worst)
    if worst < 10:
        return ("HARD_PASS", "HARD_PASS: Merkle path generation <10ms per delivery -- compatible with WebSocket push <50ms; crypto-delivery moat is usable live. " + summary)
    if worst <= 50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 10-50ms/path -- acceptable if pre-computed at write time. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: >50ms/path -- blocks push; requires async out-of-band path delivery. " + summary)


print("[config] anchor=%s mode=%s sizes=%s" % (ANCHOR_NAME, RUN_MODE, SIZES), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
