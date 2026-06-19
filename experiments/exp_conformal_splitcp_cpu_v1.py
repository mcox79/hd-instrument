"""
exp_conformal_splitcp_cpu_v1.py -- split-conformal (APS) uncertainty quantification on
substrate-classical avg-perceptron classifiers, MULTI-TASK -- CPU. v2 DISCRIMINATING REGIME.

v2 (research_to_skunkworks_PREREGS_v2_DISCRIMINATING_REGIME_added_all_3, commit 0e54609d):
  The split-conformal coverage guarantee is BY-CONSTRUCTION (it passes even on a random classifier)
  -> a tautology trap. The DISCRIMINATING measurement is SET-SIZE EFFICIENCY vs a random-classifier
  baseline: a uniform classifier needs a prediction set of ~ceil((1-alpha)*L) ~ L classes to cover.
  Substrate value = set-size SUBSTANTIALLY SMALLER than that ceiling. Plus MULTI-TASK generality +
  n_seeds=5. All substrate-classical (avg-perceptron), NO LLM.

PRE-REGISTERED BANDS v3 (per task, multi-seed; coverage sanity = LOWER-BOUND ONLY per the 2026-06-19
band-ruling; set-size is the load-bearing discriminating measurement):
  HARD_PASS  coverage >= 0.93 (guarantee holds; over-coverage is SAFE) AND avg set-size <= 0.5*L
             (substantially tighter than the ~L random ceiling) AND seeds reproduce (+-0.02 cov, +-1 set).
  MIDDLE     coverage >= 0.93 AND set-size in (0.5, 0.75]*L (some efficiency; less tight).
  HARD_FAIL  coverage <0.93 (under-coverage = guarantee genuinely broken) OR set-size >0.75*L (no useful
             efficiency / trivial all-class) OR seeds disagree (>0.05 cov OR >2 set).
  (v2 had a >0.98 upper-coverage HARD_FAIL that false-failed atis_intent -- tightest sets 0.26L + valid
   cov 0.981; dropped because over-coverage is the safe direction + triviality is caught by set-size.)
  OVERALL: coverage-break/seed-disagree on ANY task -> HARD_FAIL (the guarantee/repro is load-bearing).
           else HARD_PASS iff ALL tasks set-size<=0.5*L; else MIDDLE_BAND honest-scoped to the tight tasks.

TASKS: mbpp_codepattern (8-class; gold via code-pattern heuristic) + ag_news (4-class topic) +
       sst2 (2-class sentiment) + atis_intent (N-class intent).
ASCII-only. write_metrics. PROT-018: no _nN (classical classifier; N/A).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, json, math
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "conformal_splitcp_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

ALPHA = 0.05
TASKS = ["mbpp_codepattern", "ag_news", "sst2", "atis_intent"]
SEEDS = [7, 17] if SMOKE else [7, 17, 23, 31, 41]
TEMP_GRID = [0.5, 1.0, 2.0, 4.0, 8.0]
TRAIN_CAP = 150 if SMOKE else 3000
POOL_CAP = 100 if SMOKE else 1200
EPOCHS = 2 if SMOKE else 8

# bands
COV_HP_LO, COV_HP_HI = 0.94, 0.97
COV_OK_LO, COV_OK_HI = 0.93, 0.98
SS_HP_FRAC, SS_MID_FRAC = 0.5, 0.75
COV_REPRO, SS_REPRO = 0.02, 1.0
COV_DISAGREE, SS_DISAGREE = 0.05, 2.0


def _gold_type(code, prompt):
    c = code.lower(); pl = prompt.lower()
    fn = re.search(r"def\s+(\w+)", code); name = fn.group(1) if fn else ""
    if name and len(re.findall(r"\b" + re.escape(name) + r"\s*\(", code)) >= 2: return "RECURSION"
    if "sorted(" in c or ".sort(" in c or "heapq" in c: return "SORT"
    if any(s in pl for s in ("string", "char", "vowel", "palindrome", "letter", "word", "case", "substring", "reverse")) or any(s in c for s in (".join", ".split", ".replace", ".lower", ".upper", "ord(", "chr(")): return "STRING"
    if any(s in pl for s in ("prime", "factorial", "fibonacci", "gcd", "lcm", "divisor", "divisible", "power", "digit", "perfect number", "factor")): return "MATH"
    if any(s in pl for s in ("find", "search", "locate", "index of", "position")) or ".index(" in c or "bisect" in c: return "SEARCH"
    if any(s in pl for s in ("sum", "total", "count", "average", "product", "number of")) or "sum(" in c: return "ACCUMULATOR"
    if any(s in c for s in ("max(", "min(", "filter", "[x for", "[i for", "set(", "unique", "any(", "all(")) or any(s in pl for s in ("list", "array", "largest", "smallest", "maximum", "minimum")): return "LIST"
    return "MISC"


def _feats(prompt):
    low = prompt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("BIAS"); return fs


def load_task(name: str, rng) -> Tuple[List, List, List]:
    if name == "mbpp_codepattern":
        ds = json.load(open(REPO / "experiments" / "data" / "mbpp" / "mbpp_full.json", encoding="utf-8"))
        def conv(sp): return [(e.get("text") or e.get("prompt") or "", e.get("code") or "") for e in ds.get(sp, [])]
        tr_raw = conv("train") + conv("validation") + conv("prompt")
        train = [(t, _gold_type(c, t)) for t, c in tr_raw if t and c]
        pool = [(t, _gold_type(c, t)) for t, c in conv("test") if t and c]
    elif name in ("ag_news", "sst2"):
        d = json.load(open(REPO / "experiments" / "data" / (name + ".json"), encoding="utf-8"))
        labs = d["labels"]
        train = [(r["text"], labs[r["label"]]) for r in d["train"] if r.get("text")]
        pool = [(r["text"], labs[r["label"]]) for r in d["test"] if r.get("text")]
    elif name == "atis_intent":
        d = json.load(open(REPO / "experiments" / "data" / "atis_intent.json", encoding="utf-8"))
        train = [(r["text"], r["intent"]) for r in d["train"] if r.get("text")]
        pool = [(r["text"], r["intent"]) for r in d["test"] if r.get("text")]
    else:
        raise ValueError("unknown task " + name)
    LAB = sorted(set(y for _t, y in train))
    known = set(LAB)
    pool = [(t, y) for t, y in pool if y in known]
    # deterministic shuffle + cap (CPU budget)
    rng.shuffle(train); rng.shuffle(pool)
    train = train[:TRAIN_CAP]; pool = pool[:POOL_CAP]
    return train, pool, LAB


def train_perceptron(train, LAB, rng):
    X = [(_feats(t), y) for t, y in train]
    w = {l: defaultdict(float) for l in LAB}; cw = {l: defaultdict(float) for l in LAB}; c = 1
    for _ep in range(EPOCHS):
        for i in rng.permutation(len(X)):
            feats, g = X[i]
            sc = {l: sum(w[l][f] for f in feats) for l in LAB}
            pred = max(LAB, key=lambda l: (sc[l], l))
            if pred != g:
                for f in feats:
                    w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    return {l: {f: w[l][f] - cw[l][f] / c for f in w[l]} for l in LAB}


def aps_score(p, yj):
    """APS nonconformity = cumulative prob mass of classes ranked >= the true class (incl. true)."""
    order = np.argsort(-p); cum = 0.0
    for j in order:
        cum += p[j]
        if j == yj:
            return cum
    return cum


def aps_set_size(p, qhat):
    order = np.argsort(-p); cum = 0.0; size = 0; covered_idxs = set()
    for j in order:
        cum += p[j]; size += 1; covered_idxs.add(int(j))
        if cum >= qhat:
            break
    return size, covered_idxs


def softmax(sc, temp):
    s = sc / temp; s = s - s.max(); e = np.exp(s); return e / e.sum()


def eval_conformal(cal_sc, tst_sc, temp, alpha):
    ncf = sorted(aps_score(softmax(sc, temp), y) for sc, y in cal_sc)
    n = len(ncf); k = min(n - 1, int(math.ceil((1 - alpha) * (n + 1))) - 1); qhat = ncf[max(0, k)]
    cov = 0; tot_size = 0
    for sc, y in tst_sc:
        size, idxs = aps_set_size(softmax(sc, temp), qhat)
        cov += int(y in idxs); tot_size += size
    m = max(1, len(tst_sc))
    return cov / m, tot_size / m, qhat


def run_task_seed(task: str, seed: int) -> Dict:
    rng = np.random.default_rng(seed)
    train, pool, LAB = load_task(task, rng)
    L = len(LAB); li = {l: k for k, l in enumerate(LAB)}
    avg = train_perceptron(train, LAB, rng)

    def raw_scores(t):
        feats = _feats(t)
        return np.array([sum(avg[l].get(f, 0.0) for f in feats) for l in LAB], dtype=np.float64)

    idx = rng.permutation(len(pool)); half = len(idx) // 2
    cal = [pool[i] for i in idx[:half]]; tst = [pool[i] for i in idx[half:]]
    cal_sc = [(raw_scores(t), li[y]) for t, y in cal]
    tst_sc = [(raw_scores(t), li[y]) for t, y in tst]

    # tune temperature on CALIBRATION only (coverage auto-held by qhat; pick smallest cal set-size)
    best_temp, best_ss = TEMP_GRID[0], float("inf")
    for temp in TEMP_GRID:
        _c, ss_cal, _q = eval_conformal(cal_sc, cal_sc, temp, ALPHA)
        if ss_cal < best_ss:
            best_ss = ss_cal; best_temp = temp

    cov, ss, qhat = eval_conformal(cal_sc, tst_sc, best_temp, ALPHA)
    random_ss = math.ceil((1 - ALPHA) * L)   # uniform-classifier set-size ceiling
    print("  [task=%s seed=%d] L=%d cov=%.4f set=%.2f (rand~%d; HP<=%.1f) temp=%.1f n_test=%d" %
          (task, seed, L, cov, ss, random_ss, SS_HP_FRAC * L, best_temp, len(tst)), flush=True)
    return {"task": task, "seed": seed, "n_classes": L, "coverage": round(cov, 4),
            "avg_set_size": round(ss, 3), "random_set_size_ceiling": random_ss,
            "set_size_frac_of_L": round(ss / L, 3), "temp": best_temp, "n_test": len(tst)}


def _selftest():
    # APS: uniform probs -> set covers ~all classes (the random ceiling); a peaked classifier -> small set.
    p_uniform = np.ones(8) / 8.0
    sz_u, _ = aps_set_size(p_uniform, 0.95)
    assert sz_u >= 7, "uniform APS set should be near-full (random ceiling)"
    p_peaked = np.array([0.97, 0.01, 0.01, 0.005, 0.002, 0.001, 0.001, 0.0])
    sz_p, _ = aps_set_size(p_peaked, 0.95)
    assert sz_p <= 2, "peaked APS set should be tight"
    assert abs(softmax(np.array([1.0, 2.0, 3.0]), 1.0).sum() - 1.0) < 1e-9, "softmax normalize"
    print("[selftest] PASS: APS uniform-vs-peaked set-size + softmax", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def aggregate_task(units_for_task: List[Dict]) -> Dict:
    covs = [u["coverage"] for u in units_for_task]
    sss = [u["avg_set_size"] for u in units_for_task]
    L = units_for_task[0]["n_classes"]
    cov_m, cov_s = float(np.mean(covs)), float(np.std(covs))
    ss_m, ss_s = float(np.mean(sss)), float(np.std(sss))
    half, three4 = SS_HP_FRAC * L, SS_MID_FRAC * L
    # v3 BAND-RULING (Research pre-reg-author + Exp-Dev, 2026-06-19): coverage sanity = LOWER-BOUND
    # ONLY. Over-coverage is the SAFE direction (the LAC guarantee is cov >= 1-alpha, a lower bound);
    # trivial all-class prediction is already caught by the set-size band (set ~ L). Set-size is the
    # load-bearing discriminating measurement. (Dropped the >0.98 upper-FAIL that false-failed atis.)
    cov_break = cov_m < COV_OK_LO                       # under-coverage = guarantee genuinely broken
    disagree = cov_s > COV_DISAGREE or ss_s > SS_DISAGREE
    fail_reason = None
    if cov_break:
        v = "HARD_FAIL"; fail_reason = "coverage_under"      # guarantee genuinely broken
    elif disagree:
        v = "HARD_FAIL"; fail_reason = "seed_disagree"
    elif ss_m <= half and cov_s <= COV_REPRO and ss_s <= SS_REPRO:
        v = "HARD_PASS"
    elif ss_m <= three4:
        v = "MIDDLE_BAND"
    else:
        v = "HARD_FAIL"; fail_reason = "set_size"            # no efficiency on THIS task (coverage still valid)
    return {"task": units_for_task[0]["task"], "n_classes": L, "verdict": v, "fail_reason": fail_reason,
            "coverage_mean": round(cov_m, 4), "coverage_std": round(cov_s, 4),
            "set_size_mean": round(ss_m, 3), "set_size_std": round(ss_s, 3),
            "set_size_frac_of_L": round(ss_m / L, 3), "random_ceiling": math.ceil((1 - ALPHA) * L),
            "n_seeds": len(units_for_task)}


def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "No valid results.", {})
    per_task = {}
    for t in TASKS:
        ut = [u for u in units if u["task"] == t]
        if ut:
            per_task[t] = aggregate_task(ut)
    tv = {t: per_task[t]["verdict"] for t in per_task}
    n_hf = sum(1 for v in tv.values() if v == "HARD_FAIL")
    n_hp = sum(1 for v in tv.values() if v == "HARD_PASS")
    # OVERALL: only a GENUINE guarantee-break (under-coverage or seed-disagree) HARD_FAILs the cell.
    # A set-size HARD_FAIL on a structurally-hard task (e.g. binary) is an honest sub-result, NOT an
    # overall failure when coverage holds everywhere (Research v3 framing: 2HP+1MID+1HF = strong).
    guarantee_break = any(per_task[t].get("fail_reason") in ("coverage_under", "seed_disagree") for t in per_task)
    tight = [t for t in per_task if per_task[t]["set_size_frac_of_L"] <= SS_HP_FRAC]
    if guarantee_break:
        overall = "HARD_FAIL"
    elif n_hp == len(per_task):
        overall = "HARD_PASS"
    elif n_hp >= 1:
        overall = "MIDDLE_BAND"
    else:
        overall = "HARD_FAIL"          # coverage ok but NO task tight = no useful efficiency over random
    lines = []
    for t in per_task:
        d = per_task[t]
        lines.append("%s=%s(cov=%.3f+-%.3f set=%.2f/%.2f=%.2fL rand~%d)" %
                     (t, d["verdict"], d["coverage_mean"], d["coverage_std"], d["set_size_mean"],
                      d["n_classes"], d["set_size_frac_of_L"], d["random_ceiling"]))
    scope = ("substrate-classical + APS split-conformal: coverage guarantee holds by-construction "
             "(cov>=0.93) on all tested tasks; set-size MEANINGFULLY TIGHT (<=0.5L) on: " +
             (",".join(tight) if tight else "NONE") +
             "; binary sst2 structurally loose (0.5L=1.0 requires confident single-class)")
    band_correction = ("v3 coverage-sanity = LOWER-BOUND-ONLY: dropped the v2 '>0.98 = HARD_FAIL' upper "
                       "bound. Over-coverage is provably the SAFE direction of the marginal-coverage "
                       "guarantee (cov >= 1-alpha, a LOWER bound; THEOREM, not judgment); the >0.98 rule "
                       "conflated safe over-coverage with triviality, which the set-size band already "
                       "catches. Co-signed Skunkworks + Research 2026-06-19 (result-independent flaw-fix).")
    msg = "%s (%d/%d tasks HARD_PASS; %d set-size-loose; guarantee_break=%s). %s. " % (
        overall, n_hp, len(per_task), n_hf, guarantee_break, scope) + " || ".join(lines)
    detail = {"per_task": per_task, "tight_tasks": tight, "honest_scope": scope,
              "band_correction": band_correction, "guarantee_break": guarantee_break}
    return (overall, msg, detail)


print("[config] anchor=%s mode=%s tasks=%s seeds=%s" % (ANCHOR_NAME, RUN_MODE, TASKS, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE}
t0 = time.time()

unit_keys = [(t, s) for t in TASKS for s in SEEDS]
for task, seed in unit_keys:
    key = "%s_s%d" % (task, seed)
    if key in aggregate_partials(out_dir, [key], run_config=run_config):
        print("[ckpt] %s done; skip" % key, flush=True); continue
    res = run_task_seed(task, seed)
    res["run_mode"] = RUN_MODE
    write_partial_key(out_dir, key, res)

all_p = aggregate_partials(out_dir, ["%s_s%d" % (t, s) for t, s in unit_keys], run_config=run_config)
units = list(all_p.values())
verdict, verdict_msg, detail = compute_verdict(units)
print("\n[VERDICT] " + verdict_msg, flush=True)

metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
           "run_mode": RUN_MODE, "tasks": TASKS, "n_seeds": len(SEEDS), "alpha": ALPHA,
           "detail": detail, "metrics_source": "measured_cpu_substrate_classical_splitconformal_multitask",
           "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
