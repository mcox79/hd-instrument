"""
exp_kb_determinism_scales_gpu_v1 -- PP-225 kb25k + kb50k fact-recall determinism at n=3 seeds -- GPU.

ROUTING: Research PROMOTION_CAMPAIGN Wave-3 (PP-225 Tier-A bulletproofing, extends kb10k determinism to more scales).
  Runs the validated kb25k and kb50k genuine fact-recall cells (frozen Pythia-1.4b + bge-large head) at 3 seeds each
  (HDLAB_SEED) and reports per-scale mean +/- std of held-out recall. Confirms the production fact-recall claim is
  seed-deterministic across the 25K-50K range, not just at 10K. Subprocesses the validated cells (no logic change).
  Uses GPU (torch; subprocessed cells train on CUDA). Sustained GPU backlog (~1 hr).
PRE-REGISTERED: HARD-PASS BOTH scales mean held-out >= 0.90 AND std <= 0.03. MIDDLE one scale. HARD-FAIL neither.
ASCII-only. write_metrics + per (scale,seed) checkpoint. PROT-018/020/021 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, re, time, subprocess
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics, write_partial_key, load_partial_key
import torch  # noqa: F401  -- GPU-queue routing (PROT-020); subprocessed cells train on CUDA
ANCHOR_NAME = "kb_determinism_scales_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
EXP = REPO / "experiments"
SCALES = [("kb25k", "exp_t5c_pp225_kb25k_genuine_v1.py"), ("kb50k", "exp_t5c_pp225_kb50k_genuine_v1.py")]
SEEDS = [7, 8] if SMOKE else [7, 8, 9]
_BEST_RE = re.compile(r"best=([0-9.]+)"); _HO_RE = re.compile(r"HELD-OUT-recall=([0-9.]+)")
def _selftest():
    for _, fn in SCALES:
        assert (EXP / fn).exists(), "missing " + fn
    assert abs(float(_BEST_RE.search("best=0.994").group(1)) - 0.994) < 1e-6
    print("[selftest] PASS: kb-determinism-scales", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _run(fn, seed):
    env = dict(os.environ); env["HDLAB_SEED"] = str(seed); env["HDLAB_RUN_MODE"] = "smoke" if SMOKE else "full"
    env.pop("HDLAB_EXP_NAME", None)
    cmd = [sys.executable, str(EXP / fn)] + (["--smoke"] if SMOKE else [])
    p = subprocess.run(cmd, cwd=str(REPO), env=env, capture_output=True, text=True, timeout=3600)
    best = None
    for line in (p.stdout or "").splitlines():
        m = _BEST_RE.search(line) or _HO_RE.search(line)
        if m: best = float(m.group(1))
    if best is None:
        raise RuntimeError("no recall parsed rc=%d" % p.returncode)
    return best
def run(out_dir) -> Dict:
    suf = "_smoke" if SMOKE else "_full"; per_scale = {}
    for label, fn in SCALES:
        vals = []
        for s in SEEDS:
            rec = load_partial_key(out_dir, "%s_s%d%s" % (label, s, suf))
            if rec is None:
                r = _run(fn, s); rec = {"scale": label, "seed": s, "heldout": round(r, 4)}
                write_partial_key(out_dir, "%s_s%d%s" % (label, s, suf), rec)
                print("  %s seed %d: held-out=%.4f" % (label, s, r), flush=True)
            else:
                print("  %s seed %d (resumed): held-out=%.4f" % (label, s, rec["heldout"]), flush=True)
            vals.append(rec["heldout"])
        mean = sum(vals) / len(vals); std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
        per_scale[label] = {"mean": round(mean, 4), "std": round(std, 4), "vals": [round(v, 4) for v in vals]}
        print("  %s: mean=%.4f std=%.4f" % (label, mean, std), flush=True)
    return {"per_scale": per_scale, "n_seeds": len(SEEDS)}
def verdict(r) -> Tuple[str, str]:
    ps = r["per_scale"]; oks = sum(1 for v in ps.values() if v["mean"] >= 0.90 and v["std"] <= 0.03)
    s = " ".join("%s(mean=%.3f std=%.3f)" % (k, v["mean"], v["std"]) for k, v in ps.items())
    if oks == len(ps):
        return ("HARD_PASS", "HARD_PASS: PP-225 fact-recall is seed-deterministic across kb25k+kb50k (mean>=0.90, std<=0.03 both) -- production claim holds across the 25K-50K range, not a lucky seed. " + s)
    if oks >= 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: %d/%d scales seed-deterministic. " % (oks, len(ps)) + s)
    return ("HARD_FAIL", "HARD_FAIL: neither scale seed-deterministic at the bar. " + s)
print("[config] anchor=%s mode=%s scales=%s seeds=%s" % (ANCHOR_NAME, RUN_MODE, [s[0] for s in SCALES], SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run(out_dir)
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 3), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
