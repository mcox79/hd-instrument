"""
exp_tier4_multiseed_sweep_cpu_v1.py -- multi-seed promotion of the new Tier-4 passes (n=5 -> Tier C) -- CPU.

ROUTING: Research cycle-229/230 -- "multi-seed promote anything that lands." Runs the 4 newly-passing self-contained Tier-4
  anchors at n=5 seeds (HDLAB_SEED) under their own gates; aggregates verdict distribution. Crystallized (PP-363), Excitability
  Gated (Sprint-4 last arch), code2-adversarial (Tier-C reinforce), key-rotation-scale-adversarial (10K). >=4/5 HARD_PASS -> PROMOTE_C.
PRE-REGISTERED: HARD-PASS all 4 PROMOTE_C (>=4/5 HARD_PASS). MIDDLE 2-3/4. HARD-FAIL <2.
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
ANCHOR_NAME = "tier4_multiseed_sweep_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
EXP = REPO / "experiments"
ANCHORS: List[Tuple[str, str]] = [
    ("crystallized", "exp_crystallized_substrate_cpu_v1.py"),
    ("excitability", "exp_excitability_gated_substrate_cpu_v1.py"),
    ("code2-adv", "exp_code2_adversarial_cpu_v1.py"),
    ("key-rot-10k", "exp_key_rotation_scale_adversarial_cpu_v1.py"),
]
_VERDICT_RE = re.compile(r"\[VERDICT\]\s*([A-Z_]+)")
def _selftest():
    for _, fn in ANCHORS:
        assert (EXP / fn).exists(), "missing " + fn
    print("[selftest] PASS: tier4-multiseed-sweep (4 cells present)", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _run_one(fn, seed):
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
    seeds = [1, 2, 3] if SMOKE else [1, 2, 3, 4, 5]; suf = "_smoke" if SMOKE else "_full"
    per_anchor = {}; n_promote = 0; n_fragile = 0; n_fail = 0
    for label, fn in ANCHORS:
        ck = label + suf; rec = load_partial_key(out_dir, ck)
        if rec is None or "decision" not in rec:
            verdicts = [_run_one(fn, s) for s in seeds]; n_hp = sum(1 for v in verdicts if v in ("HARD_PASS", "PASS"))
            thr = 2 if SMOKE else 4
            decision = "PROMOTE_C" if n_hp >= thr else ("SEED_FRAGILE" if n_hp >= (1 if SMOKE else 2) else "FAIL")
            rec = {"label": label, "verdicts": verdicts, "n_hard_pass": n_hp, "n_seeds": len(seeds), "decision": decision}
            write_partial_key(out_dir, ck, rec)
            print("  %-14s n=%d HARD_PASS=%d/%d -> %s [%s]" % (label, len(seeds), n_hp, len(seeds), decision, ",".join(verdicts)), flush=True)
        else:
            print("  %-14s (resumed) -> %s" % (label, rec["decision"]), flush=True)
        per_anchor[label] = rec; d = rec["decision"]; n_promote += d == "PROMOTE_C"; n_fragile += d == "SEED_FRAGILE"; n_fail += d == "FAIL"
    return {"per_anchor": per_anchor, "n_promote": n_promote, "n_fragile": n_fragile, "n_fail": n_fail, "n_anchors": len(ANCHORS), "n_seeds": len(seeds)}
def verdict(r) -> Tuple[str, str]:
    p = r["n_promote"]; s = "promote=%d fragile=%d fail=%d of %d (n_seeds=%d)" % (p, r["n_fragile"], r["n_fail"], r["n_anchors"], r["n_seeds"])
    if p >= 4:
        return ("HARD_PASS", "HARD_PASS: all 4 new Tier-4 anchors (crystallized, excitability-gated, code2-adversarial, key-rotation-10K) SEED-ROBUST at n=5 -> Tier C. " + s)
    if p >= 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: %d/4 seed-robust. " % p + s)
    return ("HARD_FAIL", "HARD_FAIL: <2 seed-robust. " + s)
print("[config] anchor=%s mode=%s anchors=%d" % (ANCHOR_NAME, RUN_MODE, len(ANCHORS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run(out_dir)
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 5), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
