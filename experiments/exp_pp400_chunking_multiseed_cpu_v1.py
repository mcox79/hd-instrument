"""
exp_pp400_chunking_multiseed_cpu_v1.py -- PP-400 chunking END-TASK multi-seed n=5 promotion (Research Tier-A plan, Cell 1).

USER directive (via Research note research_to_exp_dev_TIER_A_METHODICAL_PROMOTION_PLAN_PAUSE_TIER_5_TREADMILL): pause the Tier-5
mechanism treadmill; methodically promote existing capabilities to END-TASK multi-seed Tier-A. Cell 1 (cheapest) = PP-400 chunking:
take the validated single-seed cascade (chunk-F1 0.9231 on CoNLL-2000) to multi-seed n=5, report mean +/- SD + stability.

Runs the validated cell `exp_chunking_conll2000_cascade_cpu_v1.py` as a SUBPROCESS across 5 seeds (HDLAB_SEED) and aggregates --
subprocess avoids that cell's import-time module execution. CPU work -> laptop (home CPU is Testbed's).

Pre-reg (Research Cell 1): HARD-PASS multi-seed mean F1 >= 0.91 AND SD <= 0.02; MIDDLE 0.85-0.91; HARD-FAIL <0.85 OR unstable (SD>0.02).
Promotes chunking single-seed Tier-A -> end-task multi-seed Tier-A (substrate-classical NL roster 6 -> 7 multi-seed).
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CELL = REPO / "experiments" / "exp_chunking_conll2000_cascade_cpu_v1.py"
SEEDS = [1028, 1029, 1030, 1031, 1032]
_F1_RE = re.compile(r"\+POS-cascade\]\s*F1=([0-9.]+)")
_WORD_RE = re.compile(r"word-only\]\s*F1=([0-9.]+)")


def _run_seed(seed, smoke):
    env = dict(os.environ); env["HDLAB_SEED"] = str(seed); env["HDLAB_RUN_MODE"] = "smoke" if smoke else "full"
    cmd = [sys.executable, str(CELL)] + (["--smoke"] if smoke else [])
    p = subprocess.run(cmd, cwd=str(REPO), env=env, capture_output=True, text=True, timeout=3600)
    out = p.stdout + p.stderr
    m = _F1_RE.search(out); w = _WORD_RE.search(out)
    if not m:
        raise RuntimeError("no F1 parsed for seed %d; tail: %s" % (seed, out[-300:]))
    return {"seed": seed, "f1_cascade": float(m.group(1)), "f1_wordonly": float(w.group(1)) if w else None}


def _mean_sd(xs):
    n = len(xs); mu = sum(xs) / n
    sd = (sum((x - mu) ** 2 for x in xs) / n) ** 0.5
    return mu, sd


def run(smoke=False, verbose=True):
    per = []
    for s in SEEDS:
        r = _run_seed(s, smoke)
        per.append(r)
        if verbose:
            print("  seed %d: cascade F1=%.4f (word-only %.4f)" % (s, r["f1_cascade"], r["f1_wordonly"] or -1), flush=True)
    f1s = [r["f1_cascade"] for r in per]
    mu, sd = _mean_sd(f1s)
    if verbose:
        print("\n=== PP-400 chunking multi-seed n=%d ===" % len(SEEDS))
        print("cascade F1: mean=%.4f SD=%.4f min=%.4f max=%.4f | seeds=%s" % (mu, sd, min(f1s), max(f1s), SEEDS))
    if mu >= 0.91 and sd <= 0.02:
        verdict = "PASS"; msg = "PP-400 chunking PROMOTED to end-task multi-seed Tier-A: mean F1 %.4f >=0.91, SD %.4f <=0.02 (n=5 stable). Substrate-classical NL roster 6 -> 7 multi-seed." % (mu, sd)
    elif mu >= 0.85:
        verdict = "MIDDLE"; msg = "PP-400 chunking multi-seed mean F1 %.4f (SD %.4f) in [0.85,0.91) or SD>0.02 -- strong but below multi-seed-Tier-A bar." % (mu, sd)
    else:
        verdict = "HARD_FAIL"; msg = "PP-400 chunking multi-seed mean F1 %.4f < 0.85 OR unstable (SD %.4f)." % (mu, sd)
    return {"verdict": verdict, "verdict_msg": msg,
            "summary": {"mean_f1": round(mu, 4), "sd_f1": round(sd, 4), "min": round(min(f1s), 4),
                        "max": round(max(f1s), 4), "n_seeds": len(SEEDS), "per_seed": per}}


def _self_test():
    assert CELL.exists(), "cascade cell missing: %s" % CELL
    print("[self-test] PASS: cascade cell present; will run %d seeds %s" % (len(SEEDS), SEEDS))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    if args.self_test:
        _self_test(); sys.exit(0)
    res = run(smoke=args.smoke)
    res["elapsed_s"] = round(time.time() - t0, 2)
    print()
    print("VERDICT:", res["verdict"], "--", res["verdict_msg"])
    Path("metrics.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("[metrics] wrote metrics.json")
