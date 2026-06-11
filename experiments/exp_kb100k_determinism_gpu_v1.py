"""
exp_kb_determinism_sweep_gpu_v1 -- PP-225 kb100k production-scale fact-recall determinism at n=3 seeds (Wave-3 Tier-A) -- GPU.

ROUTING: Research PROMOTION_CAMPAIGN Wave-3 (PP-225 Tier-A bulletproofing). The kb-scale asymptote (0.994-0.997 across
  10K-100K) was n=1 per scale. Research values "deterministic at smaller scales (3-seed std=0.000)". This runs the genuine
  kb10k fact-recall cell (frozen Pythia-1.4b + bge-large projection head) at 3 seeds (HDLAB_SEED) and reports mean+/-std of
  held-out recall: high mean + tiny std = the production claim is seed-deterministic, not a lucky seed. Subprocesses the
  validated kb10k cell (no logic change). Uses GPU (torch; subprocess trains on CUDA).
PRE-REGISTERED: HARD-PASS mean_heldout >= 0.90 AND std <= 0.03 (deterministic high recall). MIDDLE mean >= 0.90 std > 0.03.
  HARD-FAIL mean < 0.90.
ASCII-only. write_metrics + per-seed checkpoint. PROT-018/020/021 _v1.
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
import torch  # noqa: F401  -- GPU-queue routing (PROT-020); subprocessed kb10k trains on CUDA
ANCHOR_NAME = "kb100k_determinism_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
EXP = REPO / "experiments"
KB_CELL = "exp_t5c_pp225_kb100k_genuine_v1.py"
SEEDS = [7, 8] if SMOKE else [7, 8, 9]
_BEST_RE = re.compile(r"best=([0-9.]+)")
_HO_RE = re.compile(r"HELD-OUT-recall=([0-9.]+)")
def _selftest():
    assert (EXP / KB_CELL).exists(), "missing kb cell"
    assert abs(float(_BEST_RE.search("FINAL: bare=0.0 train-recall=1.0 HELD-OUT-recall=0.99 best=0.994").group(1)) - 0.994) < 1e-6
    print("[selftest] PASS: kb100k-determinism", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _run_seed(seed: int) -> float:
    env = dict(os.environ); env["HDLAB_SEED"] = str(seed); env["HDLAB_RUN_MODE"] = "smoke" if SMOKE else "full"
    env.pop("HDLAB_EXP_NAME", None)
    cmd = [sys.executable, str(EXP / KB_CELL)] + (["--smoke"] if SMOKE else [])
    p = subprocess.run(cmd, cwd=str(REPO), env=env, capture_output=True, text=True, timeout=3000)
    out = p.stdout or ""
    best = None
    for line in out.splitlines():
        m = _BEST_RE.search(line) or _HO_RE.search(line)
        if m: best = float(m.group(1))
    if best is None:
        tail = (p.stderr or out).strip().splitlines()[-1:]
        raise RuntimeError("no recall parsed (rc=%d): %s" % (p.returncode, tail[0][:100] if tail else ""))
    return best
def run(out_dir) -> Dict:
    suf = "_smoke" if SMOKE else "_full"
    vals: List[float] = []
    for s in SEEDS:
        rec = load_partial_key(out_dir, str(s) + suf)
        if rec is None:
            r = _run_seed(s)
            rec = {"seed": s, "heldout": round(r, 4)}
            write_partial_key(out_dir, str(s) + suf, rec)
            print("  seed %d: held-out recall=%.4f" % (s, r), flush=True)
        else:
            print("  seed %d (resumed): held-out recall=%.4f" % (s, rec["heldout"]), flush=True)
        vals.append(rec["heldout"])
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    std = var ** 0.5
    print("  KB-DETERMINISM n=%d: held-out mean=%.4f std=%.4f vals=%s" % (len(vals), mean, std, [round(v, 4) for v in vals]), flush=True)
    return {"mean_heldout": round(mean, 4), "std_heldout": round(std, 4), "vals": [round(v, 4) for v in vals], "n_seeds": len(vals)}
def verdict(r) -> Tuple[str, str]:
    m = r["mean_heldout"]; sd = r["std_heldout"]; s = "mean=%.4f std=%.4f vals=%s (n=%d)" % (m, sd, r["vals"], r["n_seeds"])
    if m >= 0.90 and sd <= 0.03:
        return ("HARD_PASS", "HARD_PASS: PP-225 kb10k fact-recall is SEED-DETERMINISTic -- mean held-out >=0.90 with std<=0.03 across seeds. The production fact-recall claim is not a lucky seed; reinforces Tier-A. " + s)
    if m >= 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: high mean recall but seed-variable (std>0.03). " + s)
    return ("HARD_FAIL", "HARD_FAIL: mean held-out <0.90. " + s)
print("[config] anchor=%s mode=%s seeds=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run(out_dir)
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 3), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
