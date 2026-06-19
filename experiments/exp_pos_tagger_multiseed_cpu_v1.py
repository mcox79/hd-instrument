"""
exp_pos_tagger_multiseed_cpu_v1.py -- POS tagger PTB n=5 seed-robustness (PP-364 Tier-A promotion) -- CPU.

ROUTING: Research POS_TAGGER_ENDORSED -- promote pos_tagger_ptb_substrate (0.906 Tier B single-seed) to Tier A via n=5
  multi-seed. Cycles HDLAB_SEED across the substrate's stochastic components (tag codebook init, OOV morphology, context
  binding); the lexicon/data split are deterministic, so this isolates substrate-encoding seed-robustness. Subprocesses the
  validated pos_tagger cell at 5 seeds; aggregates mean +/- std tag-accuracy. Corpus pre-cached (LVH-280 hardening).
PRE-REGISTERED: HARD-PASS mean tag-accuracy >= 0.90 AND std <= 0.01 (seed-robust -> Tier A). MIDDLE mean >= 0.90 std > 0.01.
  HARD-FAIL mean < 0.90. UNKNOWN if corpus load fails on any seed.
ASCII-only. write_metrics + per-seed checkpoint. PROT-018/021 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, argparse, re, time, subprocess
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics, write_partial_key, load_partial_key
ANCHOR_NAME = "pos_tagger_multiseed_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
EXP = REPO / "experiments"; CELL = "exp_pos_tagger_ptb_substrate_cpu_v1.py"
SEEDS = [1, 2, 3] if SMOKE else [1, 2, 3, 4, 5]
_ACC_RE = re.compile(r"tag-accuracy=([0-9.]+)")
def _selftest():
    assert (EXP / CELL).exists(), "missing pos_tagger cell"
    assert abs(float(_ACC_RE.search("tag-accuracy=0.9064 (").group(1)) - 0.9064) < 1e-6
    print("[selftest] PASS: pos-tagger-multiseed", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _run(seed):
    env = dict(os.environ); env["HDLAB_SEED"] = str(seed); env["HDLAB_RUN_MODE"] = "smoke" if SMOKE else "full"
    env.pop("HDLAB_EXP_NAME", None)
    cmd = [sys.executable, str(EXP / CELL)] + (["--smoke"] if SMOKE else [])
    p = subprocess.run(cmd, cwd=str(REPO), env=env, capture_output=True, text=True, timeout=900)
    acc = None
    for line in (p.stdout or "").splitlines():
        m = _ACC_RE.search(line)
        if m: acc = float(m.group(1))
    if acc is None:
        raise RuntimeError("no tag-accuracy parsed rc=%d (corpus load?)" % p.returncode)
    return acc
def run(out_dir) -> Dict:
    suf = "_smoke" if SMOKE else "_full"; vals = []
    for s in SEEDS:
        rec = load_partial_key(out_dir, str(s) + suf)
        if rec is None:
            a = _run(s); rec = {"seed": s, "tag_acc": round(a, 4)}; write_partial_key(out_dir, str(s) + suf, rec)
            print("  seed %d: tag-accuracy=%.4f" % (s, a), flush=True)
        else:
            print("  seed %d (resumed): tag-accuracy=%.4f" % (s, rec["tag_acc"]), flush=True)
        vals.append(rec["tag_acc"])
    mean = sum(vals) / len(vals); std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
    print("  POS-TAGGER n=%d: tag-acc mean=%.4f std=%.4f vals=%s" % (len(vals), mean, std, [round(v, 4) for v in vals]), flush=True)
    return {"mean_tag_acc": round(mean, 4), "std_tag_acc": round(std, 4), "vals": [round(v, 4) for v in vals], "n_seeds": len(vals)}
def verdict(r) -> Tuple[str, str]:
    m = r["mean_tag_acc"]; sd = r["std_tag_acc"]; s = "mean=%.4f std=%.4f vals=%s (n=%d)" % (m, sd, r["vals"], r["n_seeds"])
    if m >= 0.90 and sd <= 0.01:
        return ("HARD_PASS", "HARD_PASS: substrate-only POS tagger is SEED-ROBUST at n=5 (mean tag-acc>=0.90, std<=0.01) -- promotes to Tier A. Categorical refutation of 'LLM-only-for-NL-parse' is seed-stable on real PTB data. " + s)
    if m >= 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: mean>=0.90 but std>0.01 (seed-variable). " + s)
    return ("HARD_FAIL", "HARD_FAIL: mean tag-accuracy <0.90. " + s)
print("[config] anchor=%s mode=%s seeds=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run(out_dir)
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 5), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
