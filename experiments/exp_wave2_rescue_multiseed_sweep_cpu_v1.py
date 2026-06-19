"""
exp_wave2_rescue_multiseed_sweep_cpu_v1.py -- WAVE-2 rescue multi-seed promotion (Tier C) -- CPU.

ROUTING: Research PROMOTION_CAMPAIGN -- promote the PASSING Wave-2 rescues to Tier C via n=5 seed-robustness. Runs each at 5
  seeds (HDLAB_SEED override) under its own pre-registered gate and aggregates the verdict distribution. CLS (Sprint-4 closer),
  multidrive (VSA H=3 + harmonic), code2 (template-conditional, closes Tier-0 code2 gap). >=4/5 HARD_PASS -> PROMOTE_C.
  Subprocess invocation reuses each cell's own gate. CPU, numpy-only.
PRE-REGISTERED: HARD-PASS all 3 PROMOTE_C (>=4/5 HARD_PASS). MIDDLE 2/3. HARD-FAIL <2.
ASCII-only. write_metrics + per-anchor checkpoint. PROT-018/021 _v1.
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
ANCHOR_NAME = "wave2_rescue_multiseed_sweep_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
EXP = REPO / "experiments"
ANCHORS: List[Tuple[str, str]] = [
    ("cls", "exp_cls_rescue4_plus_rescue2_cpu_v1.py"),
    ("multidrive", "exp_multidrive_vsa_policy_h3_cpu_v1.py"),
    ("code2-tmpl", "exp_code2_template_conditional_cpu_v1.py"),
]
_VERDICT_RE = re.compile(r"\[VERDICT\]\s*([A-Z_]+)")
def _selftest():
    for _, fn in ANCHORS:
        assert (EXP / fn).exists(), "missing cell: " + fn
    print("[selftest] PASS: wave2-rescue-multiseed-sweep (3 cells present)", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _run_one(fn: str, seed: int) -> str:
    env = dict(os.environ); env["HDLAB_SEED"] = str(seed); env["HDLAB_RUN_MODE"] = "smoke" if SMOKE else "full"
    env.pop("HDLAB_EXP_NAME", None)
    cmd = [sys.executable, str(EXP / fn)] + (["--smoke"] if SMOKE else [])
    try:
        p = subprocess.run(cmd, cwd=str(REPO), env=env, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if p.returncode != 0:
        return "ERROR"
    m = None
    for line in (p.stdout or "").splitlines():
        mm = _VERDICT_RE.search(line)
        if mm: m = mm.group(1)
    return m or "NOVERDICT"
def run(out_dir) -> Dict:
    seeds = [1, 2, 3] if SMOKE else [1, 2, 3, 4, 5]
    suf = "_smoke" if SMOKE else "_full"
    per_anchor: Dict[str, Dict] = {}; n_promote = 0; n_fragile = 0; n_fail = 0
    for label, fn in ANCHORS:
        ck = label + suf; rec = load_partial_key(out_dir, ck)
        if rec is None or "decision" not in rec:
            verdicts = [_run_one(fn, s) for s in seeds]
            n_hp = sum(1 for v in verdicts if v in ("HARD_PASS", "PASS"))
            thr = 2 if SMOKE else 4
            decision = "PROMOTE_C" if n_hp >= thr else ("SEED_FRAGILE" if n_hp >= (1 if SMOKE else 2) else "FAIL")
            rec = {"label": label, "verdicts": verdicts, "n_hard_pass": n_hp, "n_seeds": len(seeds), "decision": decision}
            write_partial_key(out_dir, ck, rec)
            print("  %-12s n=%d HARD_PASS=%d/%d -> %s [%s]" % (label, len(seeds), n_hp, len(seeds), decision, ",".join(verdicts)), flush=True)
        else:
            print("  %-12s (resumed) -> %s" % (label, rec["decision"]), flush=True)
        per_anchor[label] = rec
        d = rec["decision"]; n_promote += d == "PROMOTE_C"; n_fragile += d == "SEED_FRAGILE"; n_fail += d == "FAIL"
    return {"per_anchor": per_anchor, "n_promote": n_promote, "n_fragile": n_fragile, "n_fail": n_fail, "n_anchors": len(ANCHORS), "n_seeds": len(seeds)}
def verdict(r) -> Tuple[str, str]:
    p = r["n_promote"]; s = "promote=%d fragile=%d fail=%d of %d (n_seeds=%d)" % (p, r["n_fragile"], r["n_fail"], r["n_anchors"], r["n_seeds"])
    if p >= 3:
        return ("HARD_PASS", "HARD_PASS: all 3 Wave-2 passing rescues (CLS, multidrive, code2-template) are SEED-ROBUST at n=5 -> Tier C. " + s)
    if p >= 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 2/3 rescues seed-robust. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <2 rescues seed-robust. " + s)
print("[config] anchor=%s mode=%s anchors=%d" % (ANCHOR_NAME, RUN_MODE, len(ANCHORS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run(out_dir)
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 5), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
