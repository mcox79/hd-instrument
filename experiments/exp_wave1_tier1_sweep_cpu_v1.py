"""
exp_wave1_tier1_sweep_cpu_v1.py -- WAVE-1 Tier-1 wrapper multi-seed completion -- CPU.

ROUTING: Research PROMOTION_CAMPAIGN WAVE-1 Tier-1 (notes/research_to_exp_dev_PROMOTION_CAMPAIGN_WAVES_2026-06-11.md).
  Completes the Sprint-4 engineered-wrapper components that were n=1/smoke to n=5 FULL (write-lock, per-role, 3x-redundant,
  cls already done by v32_multiseed_cpu_v1): RS-parity (PP-354, was n=1), v3.2-unified capstone (PP-357, was n=1), and
  per-tier-importance (PP-355, was n=1). Each runs at n=5 seeds (HDLAB_SEED override) under its own pre-registered gate;
  aggregates the verdict distribution. Confirms the wrapper layer is seed-robust (no n=1 fluke). CPU, numpy-only.
PRE-REGISTERED: HARD-PASS = all 3 wrapper cells CONFIRM (HARD_PASS in >=4/5 seeds). MIDDLE = 2/3. HARD-FAIL = <2.
  Per-anchor: >=4/5 HARD_PASS -> CONFIRM; 2-3/5 -> SEED_FRAGILE; <2 -> FAIL.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, re, time, subprocess
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics, write_partial_key, load_partial_key
ANCHOR_NAME = "wave1_tier1_sweep_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
EXP = REPO / "experiments"
ANCHORS: List[Tuple[str, str]] = [
    ("rs-parity", "exp_fhrr_rs_parity_cpu_v1.py"),
    ("v32-unified", "exp_v32_unified_wrapper_cpu_v1.py"),
    ("per-tier-importance", "exp_per_tier_importance_cpu_v1.py"),
]
_VERDICT_RE = re.compile(r"\[VERDICT\]\s*([A-Z_]+)")
def _selftest():
    assert len(ANCHORS) == 3
    for _, fn in ANCHORS:
        assert (EXP / fn).exists(), "missing cell: " + fn
    assert _VERDICT_RE.search("[VERDICT] HARD_PASS: ok").group(1) == "HARD_PASS"
    print("[selftest] PASS: wave1-tier1-sweep (3 wrapper cells present)", flush=True)
def _run_one(fn: str, seed: int) -> str:
    env = dict(os.environ); env["HDLAB_SEED"] = str(seed); env["HDLAB_RUN_MODE"] = "smoke" if SMOKE else "full"
    env.pop("HDLAB_EXP_NAME", None)   # don't leak the sweep's exp-name into children (they'd write metrics to the sweep dir)
    cmd = [sys.executable, str(EXP / fn)] + (["--smoke"] if SMOKE else [])
    try:
        p = subprocess.run(cmd, cwd=str(REPO), env=env, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if p.returncode != 0:
        tail = (p.stderr or p.stdout or "").strip().splitlines()[-1:]
        return "ERROR:" + (tail[0][:80] if tail else "rc%d" % p.returncode)
    m = None
    for line in (p.stdout or "").splitlines():
        mm = _VERDICT_RE.search(line)
        if mm: m = mm.group(1)
    return m or "NOVERDICT"
def run(out_dir) -> Dict:
    seeds = [1, 2, 3] if SMOKE else [1, 2, 3, 4, 5]
    suf = "_smoke" if SMOKE else "_full"
    per_anchor: Dict[str, Dict] = {}
    n_confirm = 0; n_fragile = 0; n_fail = 0
    for label, fn in ANCHORS:
        ckpt_key = label + suf
        rec = load_partial_key(out_dir, ckpt_key)
        if rec is not None and "decision" in rec:
            print("  %-20s (resumed) HARD_PASS=%d/%d -> %s" % (label, rec.get("n_hard_pass", 0), rec.get("n_seeds", len(seeds)), rec["decision"]), flush=True)
        else:
            verdicts = [_run_one(fn, s) for s in seeds]
            n_hp = sum(1 for v in verdicts if v in ("HARD_PASS", "PASS"))
            thr = 2 if SMOKE else 4
            if n_hp >= thr:
                decision = "CONFIRM"
            elif n_hp >= (1 if SMOKE else 2):
                decision = "SEED_FRAGILE"
            else:
                decision = "FAIL"
            rec = {"label": label, "verdicts": verdicts, "n_hard_pass": n_hp, "n_seeds": len(seeds), "decision": decision}
            write_partial_key(out_dir, ckpt_key, rec)
            print("  %-20s n=%d HARD_PASS=%d/%d -> %s  [%s]" % (label, len(seeds), n_hp, len(seeds), decision, ",".join(verdicts)), flush=True)
        per_anchor[label] = rec
        d = rec["decision"]
        if d == "CONFIRM": n_confirm += 1
        elif d == "SEED_FRAGILE": n_fragile += 1
        else: n_fail += 1
    return {"per_anchor": per_anchor, "n_confirm": n_confirm, "n_fragile": n_fragile, "n_fail": n_fail, "n_anchors": len(ANCHORS), "n_seeds": len(seeds)}
def verdict(r) -> Tuple[str, str]:
    c = r["n_confirm"]; fr = r["n_fragile"]; fa = r["n_fail"]
    s = "confirm=%d fragile=%d fail=%d of %d (n_seeds=%d)" % (c, fr, fa, r["n_anchors"], r["n_seeds"])
    if c >= 3:
        return ("HARD_PASS", "HARD_PASS: WAVE-1 Tier-1 -- all 3 remaining Sprint-4 wrapper components (RS-parity, v3.2-unified, per-tier-importance) are SEED-ROBUST at n=5; engineered-wrapper layer confirmed not n=1 flukes. " + s)
    if c >= 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 2/3 wrapper components seed-robust. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <2 wrapper components seed-robust -- route to Research. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s anchors=%d" % (ANCHOR_NAME, RUN_MODE, len(ANCHORS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run(out_dir)
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 5), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
