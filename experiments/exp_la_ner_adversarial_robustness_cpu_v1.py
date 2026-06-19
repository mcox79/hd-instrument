"""
exp_la_ner_adversarial_robustness_cpu_v1.py -- L-A substrate NER adversarial-robustness curve (Research Cycle-50 language drill REC-A).

USER no-defeatism: substrate-classical NL has a STRUCTURAL-ROBUSTNESS advantage LLMs lack (Nature SciRep 2025: LLM NER collapses
under char/word noise). This cell measures the substrate half: substrate Tier-A NER (structured perceptron + Viterbi, PP-364_NER) span-F1
as test input is char-perturbed at {0, 5, 10, 20}% noise. Graceful degradation = substrate-product robustness claim. The LLM-0.5B
comparison (does it collapse to <0.30 at 20%?) is the GPU follow-on that completes the head-to-head.

Runs the validated `exp_ner_4type_conll_cpu_v1.py` as a SUBPROCESS with HDLAB_TEST_NOISE + HDLAB_SEED (HDLAB_EXP_NAME unset so the
subprocess writes its own anchor dir). Parses the F1 line.

Pre-reg (drill REC-A, substrate half): HP substrate F1 stays >= 0.55 at 20% noise (graceful); MIDDLE 0.45-0.55; FAIL <0.45 (substrate
degrades like an LLM -> no robustness advantage). Retention @20% = F1(20%)/F1(0%) is the headline.

CPU. --self-test + --smoke + metrics.json. Route via local_cpu_queue (dashboard-visible).
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CELL = REPO / "experiments" / "exp_ner_4type_conll_cpu_v1.py"
NOISES = [0.0, 0.05, 0.10, 0.20]
SEEDS = [1028, 1029, 1030]
_F1_RE = re.compile(r"NER-4TYPE-CONLL:\s*F1=([0-9.]+)")


def _run(noise, seed, smoke):
    env = dict(os.environ); env["HDLAB_TEST_NOISE"] = str(noise); env["HDLAB_SEED"] = str(seed)
    env["HDLAB_RUN_MODE"] = "smoke" if smoke else "full"
    env.pop("HDLAB_EXP_NAME", None)  # let the NER subprocess use its own anchor dir
    p = subprocess.run([sys.executable, str(CELL)] + (["--smoke"] if smoke else []),
                       cwd=str(REPO), env=env, capture_output=True, text=True, timeout=1800)
    m = _F1_RE.search(p.stdout + p.stderr)
    if not m:
        raise RuntimeError("no F1 (noise=%s seed=%s): %s" % (noise, seed, (p.stdout + p.stderr)[-300:]))
    return float(m.group(1))


def _mean_sd(xs):
    n = len(xs); mu = sum(xs) / n
    return mu, (sum((x - mu) ** 2 for x in xs) / n) ** 0.5


def run(smoke=False, verbose=True):
    seeds = SEEDS[:2] if smoke else SEEDS
    noises = [0.0, 0.20] if smoke else NOISES
    curve = []
    for nz in noises:
        f1s = [_run(nz, s, smoke) for s in seeds]
        mu, sd = _mean_sd(f1s)
        curve.append({"noise": nz, "f1_mean": round(mu, 4), "f1_sd": round(sd, 4)})
        if verbose:
            print("  noise=%.0f%% F1=%.4f +/- %.4f" % (100 * nz, mu, sd), flush=True)
    by = {r["noise"]: r["f1_mean"] for r in curve}
    f0 = by.get(0.0, 0.0); f20 = by.get(0.20, 0.0)
    retention = round(f20 / f0, 4) if f0 else 0.0
    if verbose:
        print("\n=== L-A substrate NER adversarial-robustness ===")
        print("F1 clean=%.4f | @20%% char-noise=%.4f | retention=%.1f%%" % (f0, f20, 100 * retention))
    if f20 >= 0.55:
        verdict = "PASS"; msg = "L-A substrate ROBUST: NER F1 %.4f at 20%% char-noise (%.0f%% retention of clean %.4f) -- substrate-classical NER degrades gracefully where LLMs collapse (Nature SciRep 2025). LLM-0.5B head-to-head is the GPU follow-on." % (f20, 100 * retention, f0)
    elif f20 >= 0.45:
        verdict = "MIDDLE"; msg = "L-A substrate MODERATE robustness: NER F1 %.4f at 20%% noise (%.0f%% retention). Curve quantified; LLM head-to-head is the GPU follow-on." % (f20, 100 * retention)
    else:
        verdict = "HARD_FAIL"; msg = "L-A substrate FRAGILE: NER F1 %.4f at 20%% noise (<0.45) -- substrate degrades steeply; robustness advantage not demonstrated." % f20
    return {"verdict": verdict, "verdict_msg": msg,
            "summary": {"curve": curve, "f1_clean": f0, "f1_20pct_noise": f20, "retention_20pct": retention}}


def _self_test():
    import numpy as np
    sys.path.insert(0, str(REPO / "experiments"))
    from exp_ner_4type_conll_cpu_v1 import _char_perturb
    rng = np.random.default_rng(1)
    p = _char_perturb("Washington", 0.5, rng)
    assert isinstance(p, str) and _char_perturb("Washington", 0.0, rng) == "Washington"
    assert _F1_RE.search("  NER-4TYPE-CONLL: F1=0.71 (P=0.7 R=0.7) | 4 tags")
    print("[self-test] PASS: char-perturb + F1 regex ('%s')" % p)


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
