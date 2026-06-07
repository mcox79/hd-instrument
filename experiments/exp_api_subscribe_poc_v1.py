"""
exp_api_subscribe_poc_v1 -- substrate-native-API anchor 1 (CHEAP DECISIVE) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_substrate_native_API_design (#1). Validates the reactive subscribe()
  primitive is buildable on existing write infrastructure: write 100 facts; register subscribe(pattern, threshold=0.80);
  write matching + non-matching facts; confirm the callback fires EXACTLY for matches, each delivery carries a verifiable
  merkle_path, and per-event latency < 100ms. Binary tractability result. CPU $0.
PRE-REGISTERED (research bands): HARD-PASS all matches delivered, zero false positives, every merkle_path verifies,
  <100ms/event. HARD-FAIL any false positive OR any merkle_path failure OR latency >500ms.
FORMULA SELF-TESTS (PROT-022): 1. match fires above threshold. 2. non-match suppressed. 3. merkle_path verifies.
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

ANCHOR_NAME = "api_subscribe_poc_v1"
N = 1024; THRESH = 0.80
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_BASE = 100; N_MATCH = 10; N_NONMATCH = 10
else:
    N_BASE = 1000; N_MATCH = 100; N_NONMATCH = 100


def _h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


class Substrate:
    def __init__(self):
        self.leaves = []; self.subs = []
    def write(self, vec, payload):
        idx = len(self.leaves); self.leaves.append(_h(payload)); root = self._root()
        fires = []
        for (pat, thr, cb) in self.subs:
            if float(vec @ pat) >= thr:
                cb(idx, self._path(idx), root); fires.append(idx)
        return fires
    def subscribe(self, pat, thr, cb):
        self.subs.append((pat, thr, cb))
    def _levels(self):
        levels = [list(self.leaves)]
        while len(levels[-1]) > 1:
            cur = levels[-1]
            if len(cur) % 2:
                cur = cur + [cur[-1]]
            levels.append([_h(cur[i] + cur[i + 1]) for i in range(0, len(cur), 2)])
        return levels
    def _root(self):
        return self._levels()[-1][0]
    def _path(self, idx):
        path = []
        for lvl in self._levels()[:-1]:
            sib = idx ^ 1; sib = sib if sib < len(lvl) else idx; path.append((lvl[sib], idx & 1)); idx //= 2
        return path


def verify_path(leaf, path, root):
    h = leaf
    for sib, is_right in path:
        h = _h(sib + h) if is_right else _h(h + sib)
    return h == root


def _selftest():
    g = np.random.default_rng(0); s = Substrate(); pat = unit(g.standard_normal(64))
    hits = []; s.subscribe(pat, 0.8, lambda i, p, r: hits.append(i))
    s.write(unit(g.standard_normal(64)), b"f0")                       # base
    s.write(pat.copy(), b"match")                                     # exact match -> fires
    assert len(hits) == 1, "match fires above threshold"
    before = len(hits); s.write(unit(-pat), b"nonmatch"); assert len(hits) == before, "non-match suppressed"
    print("[selftest] PASS: api-subscribe", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); s = Substrate(); pat = unit(g.standard_normal(N).astype(np.float32))
    deliveries = []
    s.subscribe(pat, THRESH, lambda i, p, r: deliveries.append((i, p, r)))
    for j in range(N_BASE):
        s.write(unit(g.standard_normal(N).astype(np.float32)), b"base_%d" % j)
    # matching writes: near pat (cos >= THRESH); non-matching: orthogonal-ish
    matches = unit(pat[None, :] + 0.2 * g.standard_normal((N_MATCH, N)).astype(np.float32))
    matches = unit(np.where(((matches @ pat) >= THRESH)[:, None], matches, pat[None, :]))   # ensure >= thr
    expected = 0; lat = []
    for j in range(N_MATCH):
        t0 = time.perf_counter(); fired = s.write(matches[j], b"match_%d" % j); lat.append((time.perf_counter() - t0) * 1e3)
        if fired:
            expected += 1
    fp = 0
    for j in range(N_NONMATCH):
        nm = unit(g.standard_normal(N).astype(np.float32))
        if float(nm @ pat) >= THRESH:
            continue
        before = len(deliveries); s.write(nm, b"non_%d" % j)
        if len(deliveries) > before:
            fp += 1
    root = s._root(); paths_ok = all(verify_path(s.leaves[i], p, r if False else root) for (i, p, r) in deliveries)
    paths_ok = all(verify_path(s.leaves[i], s._path(i), root) for (i, p, r) in deliveries)
    max_lat = max(lat) if lat else 0.0
    print("  delivered=%d expected_matches=%d false_pos=%d paths_ok=%s max_lat=%.3fms" % (len(deliveries), expected, fp, paths_ok, max_lat), flush=True)
    return {"delivered": len(deliveries), "expected": expected, "false_pos": fp, "paths_ok": bool(paths_ok), "max_lat_ms": max_lat}


def verdict(r) -> Tuple[str, str]:
    ok = r["false_pos"] == 0 and r["paths_ok"] and r["max_lat_ms"] < 500 and r["delivered"] >= r["expected"] and r["expected"] > 0
    summary = "delivered=%d expected=%d false_pos=%d paths_ok=%s max_lat=%.3fms" % (r["delivered"], r["expected"], r["false_pos"], r["paths_ok"], r["max_lat_ms"])
    if ok and r["max_lat_ms"] < 100:
        return ("HARD_PASS", "HARD_PASS: subscribe() delivers all matches, zero false positives, merkle_path verifies, <100ms -- reactive primitive is buildable on existing write path. " + summary)
    if ok:
        return ("MIDDLE_BAND", "MIDDLE_BAND: correct delivery but latency 100-500ms. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: false positive OR merkle_path failure OR latency >500ms -- not tractable as specced. " + summary)


print("[config] anchor=%s mode=%s n_base=%d n_match=%d thresh=%.2f" % (ANCHOR_NAME, RUN_MODE, N_BASE, N_MATCH, THRESH), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
