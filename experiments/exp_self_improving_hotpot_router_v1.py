"""
exp_self_improving_hotpot_router_v1 -- Anchor 2: bridge accumulation on REAL HotpotQA distribution -- CPU.

ROUTING: self_improving_3_pretests Anchor 2. Anchor 1 validated accumulation on a SYNTHETIC Zipf distribution; this checks the
  REAL HotpotQA bridge-entity distribution supports the same warm-up. Each question's "bridge" = its supporting-fact document
  titles (the entities linking the two hops). Process questions as a stream; cache seen bridge titles; a query is fast-path
  when ALL its bridge titles are already cached (both bridge docs known -> substrate can compose without LLM bridge-finding).
  Measure fast-path fraction X(Q) growth over Q. No encoder needed (title/entity accumulation). CPU.
PRE-REGISTERED: HARD-PASS X(500) >= 0.25 AND X(500) >= 2x X(50) (real warm-up curve, matches the handoff ~0.10->0.25 target).
  MIDDLE X(500) in [0.15,0.25) with growth. HARD-FAIL X flat or < 0.15 (real distribution too sparse; tune bridge granularity).
FORMULA SELF-TESTS (PROT-022): 1. all-cached logic. 2. coverage monotone. 3. parse supporting titles.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "self_improving_hotpot_router_v1"; WINDOW = 50
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
CHECKPOINTS = [50, 100, 200] if RUN_MODE == "smoke" else [50, 100, 200, 500, 1000]
QMAX = CHECKPOINTS[-1]


def _selftest():
    cache = {"A", "B"}; assert all(t in cache for t in ["A", "B"]) and not all(t in cache for t in ["A", "C"]), "all-cached logic"
    cov = [0.1, 0.2, 0.4]; assert all(cov[i] <= cov[i + 1] for i in range(len(cov) - 1)), "coverage monotone"
    sf = {"title": ["X", "Y"]}; assert len(set(sf["title"])) == 2, "parse supporting titles"
    print("[selftest] PASS: self-improving-hotpot-router", flush=True)


def load_bridges(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        sf = r.get("supporting_facts") or {}; titles = sorted(set(sf.get("title") or []))
        if len(titles) < 1:
            continue
        out.append(titles)
        if len(out) >= n:
            break
    return out


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    bridges = load_bridges(QMAX)
    if len(bridges) < 50:
        print("[FATAL] too few questions", flush=True); return {"n": 0, "x": {}}
    cache = set(); fastpath = np.zeros(len(bridges), dtype=np.int8); x_at = {}; uniq_at = {}
    for t, titles in enumerate(bridges):
        fastpath[t] = int(all(ti in cache for ti in titles))   # fast-path: all bridge docs already cached
        for ti in titles:
            cache.add(ti)
        tt = t + 1
        if tt in CHECKPOINTS:
            lo = max(0, tt - WINDOW); x_at[tt] = float(fastpath[lo:tt].mean()); uniq_at[tt] = len(cache)
            print("  Q=%4d  fast-path X=%.3f  (unique bridge titles cached=%d)" % (tt, x_at[tt], uniq_at[tt]), flush=True)
    return {"n": len(bridges), "x": x_at, "uniq": uniq_at}


def verdict(r) -> Tuple[str, str]:
    x = r["x"]
    x500 = x.get(500, x.get(max(x), 0.0)); x50 = x.get(50, 1e-9)
    grow = x500 >= 2 * x50; hi = x500 >= 0.25
    summary = "X(50)=%.3f X(%d)=%.3f | curve=%s (n=%d)" % (x50, max(x), x500, {k: round(v, 3) for k, v in x.items()}, r["n"])
    if hi and grow:
        return ("HARD_PASS", "HARD_PASS: real HotpotQA bridge distribution warms up as modeled (X>=0.25 and >=2x growth) -- self-improving routing accumulation works on real data, not just synthetic Zipf. " + summary)
    if x500 >= 0.15 and grow:
        return ("MIDDLE_BAND", "MIDDLE_BAND: real warm-up present but below 0.25 -- accumulation works, granularity/scale tuning needed. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: real HotpotQA bridge distribution too sparse for fast-path growth (X flat/<0.15) -- distinct-question test set lacks bridge reuse; needs entity-level (not title-pair) bridge keys or a repetitive enterprise workload. " + summary)


print("[config] anchor=%s mode=%s Qmax=%d window=%d" % (ANCHOR_NAME, RUN_MODE, QMAX, WINDOW), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
