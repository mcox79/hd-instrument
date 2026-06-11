"""
exp_wave1_multiseed_sweep_cpu_v1.py -- WAVE-1 multi-seed promotion sweep (Tier-0; D->C) -- CPU.

ROUTING: Research PROMOTION_CAMPAIGN WAVE-1 Tier-0 (notes/research_to_exp_dev_PROMOTION_CAMPAIGN_WAVES_2026-06-11.md).
  Runs each cycle-224..227 ceiling-win anchor at n=5 seeds (HDLAB_SEED override; same pre-registered gates) and aggregates
  the per-seed verdict distribution. An anchor PROMOTES D->C if it HARD_PASSes in >=4/5 seeds (seed-robust, not an n=1 fluke;
  closes LVH-277). Sub-process invocation reuses each cell's own pre-registered gate -- no gate duplication here. CPU, numpy-only.
PRE-REGISTERED (sweep-level): HARD-PASS = >=12/15 anchors promote (>=4/5 HARD_PASS). MIDDLE = 8-11 promote. HARD-FAIL = <8.
  Per-anchor promotion: >=4/5 HARD_PASS -> PROMOTE_C; 2-3/5 -> SEED_FRAGILE (route back, n=1 was fluke); <2 -> FAIL.
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
ANCHOR_NAME = "wave1_multiseed_sweep_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
EXP = REPO / "experiments"
# (label, cell filename) -- the 15 Wave-1 Tier-0 ceiling-win anchors (all currently Tier D, n=1)
ANCHORS: List[Tuple[str, str]] = [
    ("comm1", "exp_comm1_paragraph_compose_cpu_v1.py"),
    ("comm2", "exp_comm2_translation_distant_cpu_v1.py"),
    ("comm6", "exp_comm6_intent_decoding_cpu_v1.py"),
    ("comm-lex", "exp_comm_lex_emission_cpu_v1.py"),
    ("math1", "exp_math1_algebra_simplify_cpu_v1.py"),
    ("math2", "exp_math2_equation_solve_cpu_v1.py"),
    ("math3", "exp_math3_calculus_derivative_cpu_v1.py"),
    ("math4", "exp_math4_proof_chains_cpu_v1.py"),
    ("math4-rung3", "exp_math4_rung3_deep_chains_cpu_v1.py"),
    ("code1", "exp_code1_function_compose_cpu_v1.py"),
    ("code2", "exp_code2_bug_detection_cpu_v1.py"),
    ("code6", "exp_code6_algorithm_compose_cpu_v1.py"),
    ("lex-wug", "exp_lex_wug_test_cpu_v1.py"),
    ("key-rotation", "exp_key_rotation_cert_cpu_v1.py"),
    ("slipnet-noise", "exp_slipnet_noise_cpu_v1.py"),
]
_VERDICT_RE = re.compile(r"\[VERDICT\]\s*([A-Z_]+)")
def _selftest():
    assert len(ANCHORS) == 15
    for _, fn in ANCHORS:
        assert (EXP / fn).exists(), "missing cell: " + fn
    assert _VERDICT_RE.search("[VERDICT] HARD_PASS: ok").group(1) == "HARD_PASS"
    print("[selftest] PASS: wave1-multiseed-sweep (15 anchors present)", flush=True)
def _run_one(fn: str, seed: int) -> str:
    """Run cell as subprocess with HDLAB_SEED=seed; return parsed verdict type (or ERROR/TIMEOUT)."""
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
    n_promote = 0; n_fragile = 0; n_fail = 0
    for label, fn in ANCHORS:
        ckpt_key = label + suf
        rec = load_partial_key(out_dir, ckpt_key)
        if rec is not None and "decision" in rec:
            print("  %-14s (resumed) HARD_PASS=%d/%d -> %s" % (label, rec.get("n_hard_pass", 0), rec.get("n_seeds", len(seeds)), rec["decision"]), flush=True)
        else:
            verdicts = [_run_one(fn, s) for s in seeds]
            n_hp = sum(1 for v in verdicts if v in ("HARD_PASS", "PASS"))
            thr = 2 if SMOKE else 4   # >=4/5 (or >=2/3 smoke) HARD_PASS to promote
            if n_hp >= thr:
                decision = "PROMOTE_C"
            elif n_hp >= (1 if SMOKE else 2):
                decision = "SEED_FRAGILE"
            else:
                decision = "FAIL"
            rec = {"label": label, "verdicts": verdicts, "n_hard_pass": n_hp, "n_seeds": len(seeds), "decision": decision}
            write_partial_key(out_dir, ckpt_key, rec)   # checkpoint per anchor (resume-safe)
            print("  %-14s n=%d HARD_PASS=%d/%d -> %s  [%s]" % (label, len(seeds), n_hp, len(seeds), decision, ",".join(verdicts)), flush=True)
        per_anchor[label] = rec
        d = rec["decision"]
        if d == "PROMOTE_C": n_promote += 1
        elif d == "SEED_FRAGILE": n_fragile += 1
        else: n_fail += 1
    return {"per_anchor": per_anchor, "n_promote": n_promote, "n_fragile": n_fragile, "n_fail": n_fail, "n_anchors": len(ANCHORS), "n_seeds": len(seeds)}
def verdict(r) -> Tuple[str, str]:
    p = r["n_promote"]; fr = r["n_fragile"]; fa = r["n_fail"]
    s = "promote=%d fragile=%d fail=%d of %d anchors (n_seeds=%d)" % (p, fr, fa, r["n_anchors"], r["n_seeds"])
    thr_hp = 8 if SMOKE else 12; thr_mid = 5 if SMOKE else 8
    if p >= thr_hp:
        return ("HARD_PASS", "HARD_PASS: WAVE-1 multi-seed promotion -- >=%d/%d ceiling-win anchors are SEED-ROBUST (>=4/5 HARD_PASS) and promote D->C; n=1 exploratory wins confirmed not flukes (closes LVH-277). " % (thr_hp, r["n_anchors"]) + s)
    if p >= thr_mid:
        return ("MIDDLE_BAND", "MIDDLE_BAND: %d anchors promote D->C; %d seed-fragile need re-examination. " % (p, fr) + s)
    return ("HARD_FAIL", "HARD_FAIL: <%d anchors seed-robust; many n=1 wins were flukes -- route fragile anchors to Research. " % thr_mid + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s anchors=%d" % (ANCHOR_NAME, RUN_MODE, len(ANCHORS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run(out_dir)
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 5), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
