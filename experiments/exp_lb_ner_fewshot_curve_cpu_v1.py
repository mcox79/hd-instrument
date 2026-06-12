"""
exp_lb_ner_fewshot_curve_cpu_v1.py -- L-B substrate few-shot transfer curve (Research Cycle-50 language drill REC-B).

USER no-defeatism directive: substrate-classical NL is NOT universally bounded -- it has a LOW-DATA advantage. This cell quantifies it:
sweep the substrate Tier-A NER (structured-perceptron + Viterbi, PP-364_NER) across train-data fractions {1,5,10,50,100}% and report the
F1 scaling curve (mean +/- SD over seeds). The substrate-vs-LLM crossover (the full L-B claim) stacks later via a GPU LLM-0.5B baseline;
this is the substrate half (laptop-CPU), which establishes how little data substrate needs to reach usable F1.

Runs the validated `exp_ner_4type_conll_cpu_v1.py` as a SUBPROCESS with HDLAB_TRAIN_FRAC + HDLAB_SEED (subprocess avoids that cell's
module-level execution). Parses the "NER-4TYPE-CONLL: F1=..." line.

Pre-reg (drill REC-B, substrate half): report the curve; flag F1 at 5% data (the low-data point that the LLM-FT comparison will test
against). HP-context: substrate >= 0.55 at 5% data would be a strong low-data-optimal signal (LLM-0.5B-FT typically <0.50 at 5%).

CPU. --self-test + --smoke + writes metrics.json. Route via local_cpu_queue (laptop runner, dashboard-visible).
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CELL = REPO / "experiments" / "exp_ner_4type_conll_cpu_v1.py"
FRACTIONS = [0.01, 0.05, 0.10, 0.50, 1.0]
SEEDS = [1028, 1029, 1030]
_F1_RE = re.compile(r"NER-4TYPE-CONLL:\s*F1=([0-9.]+).*?train=(\d+)")


def _run(frac, seed, smoke):
    env = dict(os.environ); env["HDLAB_TRAIN_FRAC"] = str(frac); env["HDLAB_SEED"] = str(seed)
    env["HDLAB_RUN_MODE"] = "smoke" if smoke else "full"
    p = subprocess.run([sys.executable, str(CELL)] + (["--smoke"] if smoke else []),
                       cwd=str(REPO), env=env, capture_output=True, text=True, timeout=1800)
    m = _F1_RE.search(p.stdout + p.stderr)
    if not m:
        raise RuntimeError("no F1 parsed (frac=%s seed=%s): %s" % (frac, seed, (p.stdout + p.stderr)[-300:]))
    return float(m.group(1)), int(m.group(2))


def _mean_sd(xs):
    n = len(xs); mu = sum(xs) / n
    return mu, (sum((x - mu) ** 2 for x in xs) / n) ** 0.5


def run(smoke=False, verbose=True):
    seeds = SEEDS[:2] if smoke else SEEDS
    fracs = [0.05, 1.0] if smoke else FRACTIONS
    curve = []
    for frac in fracs:
        f1s = []; ntr = 0
        for s in seeds:
            f1, ntr = _run(frac, s, smoke); f1s.append(f1)
        mu, sd = _mean_sd(f1s)
        curve.append({"frac": frac, "n_train": ntr, "f1_mean": round(mu, 4), "f1_sd": round(sd, 4)})
        if verbose:
            print("  frac=%.2f n_train=%-5d F1=%.4f +/- %.4f" % (frac, ntr, mu, sd), flush=True)
    by = {r["frac"]: r["f1_mean"] for r in curve}
    f1_full = by.get(1.0, 0.0); f1_5pct = by.get(0.05, 0.0)
    retention_5pct = round(f1_5pct / f1_full, 4) if f1_full else 0.0
    if verbose:
        print("\n=== L-B substrate NER few-shot curve ===")
        print("F1 @5%% data = %.4f | @100%% = %.4f | retention @5%% = %.1f%%" % (f1_5pct, f1_full, 100 * retention_5pct))
    # verdict: substrate low-data strength (the LLM crossover comparison is the GPU follow-on)
    if f1_5pct >= 0.55:
        verdict = "PASS"; msg = "L-B substrate STRONG low-data: NER F1 %.4f at 5%% data (%.0f%% of full %.4f). Substrate-classical reaches usable NER from little data -- the low-data-optimal claim; LLM-0.5B-FT crossover is the GPU follow-on." % (f1_5pct, 100 * retention_5pct, f1_full)
    elif f1_5pct >= 0.40:
        verdict = "MIDDLE"; msg = "L-B substrate MODERATE low-data: NER F1 %.4f at 5%% data (%.0f%% of full). Curve quantified; crossover-vs-LLM is the GPU follow-on." % (f1_5pct, 100 * retention_5pct)
    else:
        verdict = "HARD_FAIL"; msg = "L-B substrate WEAK at low data: NER F1 %.4f at 5%% (<0.40) -- low-data advantage not demonstrated for NER." % f1_5pct
    return {"verdict": verdict, "verdict_msg": msg,
            "summary": {"curve": curve, "f1_5pct": f1_5pct, "f1_full": f1_full, "retention_5pct": retention_5pct}}


def _self_test():
    assert CELL.exists()
    assert _F1_RE.search("  NER-4TYPE-CONLL: F1=0.7100 (P=0.7 R=0.7) | gap=+0.1 | 4 coarse-tags, train=5982 test=500")
    print("[self-test] PASS: NER cell present + F1 regex")


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
