"""
exp_substrate_permutation_binding_multiocc_v2_full.py -- E3 v2 FULL 3-seed promotion (USER 2026-06-25).

PROMOTION CONTEXT: the v1 cell (`exp_e3_permutation_binding_multiocc_cpu_v1`) HARD_PASS'd permutation-indexed binding at
n_seeds=1 (FHRR=0.0119 permutation=1.0000 lift=+0.9881 on n=84 multi-occurrence subset). Not chain-grade-tier-eligible per
BIAS-14.

v2: re-run at n_seeds=3 (seeds [11,13,19]) with PER-SEED FHRR-base perturbation so seeds give genuinely independent
vector realizations. v1's vectors were CRC32-hash-derived from value-strings, identical across runs; v2 XORs the role +
num vector seeds with the per-seed offset to randomize. The MECHANISM (random-permutation binding via cyclic shift) is
unchanged.

MECHANISM (Recchia-Jones 2015; brain analogue Wei-Wang-Wang 2012 bump-attractor desync):
  bind the k-th occurrence of a role with a PERMUTED key roll(role_vec, k * stride), so distinct occurrences get
  near-orthogonal keys + recover cleanly even when they share a role label. FHRR baseline (plain role-key, no
  occurrence-index) collides + recovers a MIX of same-role numbers.

On the ASDiv multi-occurrence subset (problems where >=2 extracted operands share a role; v1 n=84):
  metric = answer-accuracy = recover operand pair via bind/unbind, execute gold operation, check answer.

PROSPECTIVE BANDS (LOCKED via assert):
  HARD_PASS_CHAIN_GRADE:  permutation mean top1 >= 0.95 AND FHRR baseline mean < 0.10 AND lift mean >= 0.85 AND cv <= 0.05 (across seeds)
  HARD_PASS_PARTIAL:      permutation mean 0.70 - 0.95 OR cv 0.05 - 0.10
  HARD_FAIL:              permutation mean < 0.70

ASCII-only. --self-test + --smoke + metrics.json. local_cpu_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, re, zlib, math
from pathlib import Path
from typing import Dict, Tuple, List
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "substrate_permutation_binding_multiocc_v2_full"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
D = 512                                # FHRR dim (smoke == full)
OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "rs": lambda a, b: b - a, "*": lambda a, b: a * b,
       "/": lambda a, b: (a / b if b != 0 else None), "rd": lambda a, b: (b / a if a != 0 else None)}
OPNAMES = list(OPS.keys())
ROLES = ["PER", "TGT", "TOT", "SUB", "ADD", "INQ", "CNT", "WK"]
PER_CUES = ("each", "per", "every", "apiece")
TOT_CUES = ("total", "altogether", "all", "combined", "sum", "together")
SUB_CUES = ("gave", "lost", "spent", "sold", "ate", "used", "removed", "left", "fewer", "remain", "broke", "dropped", "away")
ADD_CUES = ("got", "bought", "received", "found", "added", "gained", "more", "picked", "another")
_WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "twenty": 20}

SEEDS_FULL = [11, 13, 19]
SEEDS_SMOKE = [11]
SEEDS = SEEDS_SMOKE if SMOKE else SEEDS_FULL
N_ITEMS_SMOKE = 200
N_ITEMS_FULL = None                    # None = use all asdiv (v1 full=all)

# PROSPECTIVE BANDS (LOCKED via assert per META_PROSPECTIVE_BANDS_FRESH_SEEDS)
BAND_HARD_PASS_PERM = 0.95
BAND_HARD_PASS_FHRR_MAX = 0.10
BAND_HARD_PASS_LIFT = 0.85
BAND_HARD_PASS_CV = 0.05
BAND_HARD_PASS_PARTIAL_PERM_LOW = 0.70
BAND_HARD_PASS_PARTIAL_PERM_HIGH = 0.95
BAND_HARD_PASS_PARTIAL_CV_LOW = 0.05
BAND_HARD_PASS_PARTIAL_CV_HIGH = 0.10
BAND_HARD_FAIL_PERM = 0.70
assert BAND_HARD_PASS_PERM > BAND_HARD_FAIL_PERM
assert BAND_HARD_PASS_LIFT > 0
assert BAND_HARD_PASS_CV <= BAND_HARD_PASS_PARTIAL_CV_LOW


def _fhrr_seeded(name: str, seed: int):
    """Per-seed FHRR vector. v1 used CRC32(name) alone -> seed-independent. v2 XORs in per-seed offset."""
    s = (zlib.crc32(name.encode()) ^ (seed * 2_654_435_761)) & 0x7fffffff
    rng = np.random.default_rng(s)
    return np.exp(1j * rng.uniform(0, 2 * np.pi, D))


def bind(a, b): return a * b
def unbind(key, bundle): return bundle * np.conj(key)
def bundle_norm(v): m = np.abs(v); m[m < 1e-9] = 1.0; return v / m
def roll_key(role_vec, k): return role_vec if k == 0 else np.roll(role_vec, k * 7)


def cleanup(vec, protos):
    best = None; bs = -1e18
    for val, pv in protos:
        s = float(np.real(np.vdot(pv, vec)))
        if s > bs: bs = s; best = val
    return best


def _st(w):
    w = w.lower()
    if w.endswith("ies") and len(w) > 4: return w[:-3] + "y"
    if w.endswith("s") and not w.endswith("ss") and len(w) > 2: return w[:-1]
    return w


def _primary_role(roles):
    for r in ["PER", "TGT", "TOT", "SUB", "ADD", "INQ", "CNT"]:
        if r in roles: return r
    return "CNT"


def extract(text):
    low = text.lower(); toks = low.split(); qs = None
    for k, w in enumerate(toks):
        if w == "how" and qs is None: qs = k
    m = re.search(r"how (?:many|much) ([a-z]+)", low); tgt = _st(m.group(1)) if m else ""
    out = []
    for k, w in enumerate(toks):
        ww = w.replace("$", "").replace(",", "").rstrip("?.,")
        val = Fraction(ww) if re.match(r"^\d+(?:\.\d+)?$", ww) else (Fraction(_WORDNUM[ww]) if ww in _WORDNUM else None)
        if val is None: continue
        noun = _st(re.sub(r"[^a-z]", "", toks[k + 1])) if k + 1 < len(toks) else ""
        ctx = " ".join(toks[max(0, k - 3):k + 6]); roles = set()
        if any(c in ctx for c in PER_CUES): roles.add("PER")
        if tgt and noun == tgt: roles.add("TGT")
        if any(c in ctx for c in TOT_CUES): roles.add("TOT")
        if any(c in ctx for c in SUB_CUES): roles.add("SUB")
        if any(c in ctx for c in ADD_CUES): roles.add("ADD")
        if qs is not None and k >= qs: roles.add("INQ")
        if not roles: roles.add("CNT")
        out.append({"v": val, "role": _primary_role(roles)})
    return out, tgt


def _assign_occ(pool):
    seen = {}
    for d in pool:
        r = d["role"]; d["occ"] = seen.get(r, 0); seen[r] = d["occ"] + 1
    return pool


def build_bundle(pool, use_perm, role_vec_fn, num_vec_fn):
    v = np.zeros(D, dtype=complex)
    for d in pool:
        key = roll_key(role_vec_fn(d["role"]), d["occ"]) if use_perm else role_vec_fn(d["role"])
        v = v + bind(key, num_vec_fn(d["v"]))
    return bundle_norm(v)


def fetch(bundle, role, occ, protos, use_perm, role_vec_fn):
    key = roll_key(role_vec_fn(role), occ) if use_perm else role_vec_fn(role)
    return cleanup(unbind(key, bundle), protos)


def _is_multiocc(pool):
    seen = {}
    for d in pool: seen[d["role"]] = seen.get(d["role"], 0) + 1
    return any(c >= 2 for c in seen.values())


def _gold_slots(pool, ans):
    n = len(pool)
    for i in range(n):
        for j in range(n):
            if i == j: continue
            for op in OPNAMES:
                r = OPS[op](pool[i]["v"], pool[j]["v"])
                if r is not None and r > 0 and Fraction(r).limit_denominator(10**6) == ans:
                    return (i, op, j)
    return None


def _eval_subset(items, use_perm, seed):
    role_vec_fn = lambda r: _fhrr_seeded("role:" + r, seed)
    num_vec_fn = lambda v: _fhrr_seeded("num:" + str(v), seed)
    cor = tot = 0
    for text, ans in items:
        pool, tgt = extract(text)
        if len(pool) < 2 or not _is_multiocc(pool): continue
        _assign_occ(pool)
        gs = _gold_slots(pool, ans)
        if gs is None: continue
        tot += 1
        i, op, j = gs
        protos = [(d["v"], num_vec_fn(d["v"])) for d in pool]
        bun = build_bundle(pool, use_perm, role_vec_fn, num_vec_fn)
        na = fetch(bun, pool[i]["role"], pool[i]["occ"], protos, use_perm, role_vec_fn)
        nb = fetch(bun, pool[j]["role"], pool[j]["occ"], protos, use_perm, role_vec_fn)
        if na is None or nb is None: continue
        r = OPS[op](na, nb)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: cor += 1
    return (cor / tot if tot else 0.0), tot


def _selftest():
    seed = 11
    role_vec_fn = lambda r: _fhrr_seeded("role:" + r, seed)
    num_vec_fn = lambda v: _fhrr_seeded("num:" + str(v), seed)
    pool = _assign_occ([{"v": Fraction(5), "role": "CNT"}, {"v": Fraction(3), "role": "CNT"}])
    protos = [(d["v"], num_vec_fn(d["v"])) for d in pool]
    bun_p = build_bundle(pool, True, role_vec_fn, num_vec_fn)
    a = fetch(bun_p, "CNT", 0, protos, True, role_vec_fn)
    b = fetch(bun_p, "CNT", 1, protos, True, role_vec_fn)
    assert a == Fraction(5) and b == Fraction(3), "permutation must separate occurrences at seed=%d" % seed
    # cross-seed: different seed must give different vectors
    v1 = _fhrr_seeded("role:CNT", 11); v2 = _fhrr_seeded("role:CNT", 13)
    assert not np.allclose(v1, v2), "per-seed FHRR vectors must differ across seeds"
    # band sanity
    assert BAND_HARD_PASS_PERM > BAND_HARD_FAIL_PERM
    assert BAND_HARD_PASS_LIFT > 0
    print("[selftest] PASS: substrate_permutation_binding_multiocc_v2_full (per-seed FHRR + bands locked)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _load_asdiv_1op():
    d = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8")); items = []
    for e in d:
        f = e.get("formula", "")
        if "=" not in f or sum(f.split("=")[0].count(o) for o in "+-*/") != 1: continue
        m = re.search(r"-?\d+\.?\d*", str(e.get("answer", "")))
        if not m: continue
        items.append(((e.get("body", "") + " " + e.get("question", "")).strip(), Fraction(m.group()).limit_denominator(10**6)))
    return items


def run_one_seed(seed: int) -> Dict:
    items = _load_asdiv_1op()
    if SMOKE: items = items[:N_ITEMS_SMOKE]
    f_acc, n = _eval_subset(items, use_perm=False, seed=seed)
    p_acc, n2 = _eval_subset(items, use_perm=True, seed=seed)
    lift = p_acc - f_acc
    print("  seed=%d multi-occ subset n=%d | FHRR=%.4f permutation=%.4f lift=%+.4f" % (seed, n, f_acc, p_acc, lift), flush=True)
    return {"seed": seed, "fhrr_acc": round(f_acc, 4), "perm_acc": round(p_acc, 4),
            "lift": round(lift, 4), "n_subset": n, "run_mode": RUN_MODE, "N": D}


def aggregate_seeds(per_seed: List[Dict]) -> Dict:
    perms = [s["perm_acc"] for s in per_seed]
    fhrrs = [s["fhrr_acc"] for s in per_seed]
    lifts = [s["lift"] for s in per_seed]
    perm_mean = float(np.mean(perms)); perm_cv = float(np.std(perms) / perm_mean) if perm_mean > 1e-9 else float("inf")
    fhrr_mean = float(np.mean(fhrrs))
    lift_mean = float(np.mean(lifts)); lift_cv = float(np.std(lifts) / lift_mean) if lift_mean > 1e-9 else float("inf")
    return {"n_seeds": len(per_seed), "seeds": [s["seed"] for s in per_seed],
            "perm_acc_mean": round(perm_mean, 4), "perm_acc_cv": round(perm_cv, 4),
            "fhrr_acc_mean": round(fhrr_mean, 4),
            "lift_mean": round(lift_mean, 4), "lift_cv": round(lift_cv, 4),
            "perm_per_seed": perms, "fhrr_per_seed": fhrrs, "lift_per_seed": lifts,
            "n_subset_per_seed": [s["n_subset"] for s in per_seed]}


def verdict(agg: Dict, per_seed: List[Dict]) -> Tuple[str, str]:
    if agg["n_seeds"] == 0:
        return ("UNKNOWN", "UNKNOWN: no seeds completed")
    pm = agg["perm_acc_mean"]; pcv = agg["perm_acc_cv"]
    fm = agg["fhrr_acc_mean"]; lm = agg["lift_mean"]
    n_subset = agg["n_subset_per_seed"]
    per_seed_str = "perm_per_seed=%s fhrr_per_seed=%s lift_per_seed=%s n_subset=%s" % (
        agg["perm_per_seed"], agg["fhrr_per_seed"], agg["lift_per_seed"], n_subset)
    base = "3-seed mean perm=%.4f cv=%.4f | FHRR=%.4f | lift=%.4f cv=%.4f | %s" % (
        pm, pcv, fm, lm, agg["lift_cv"], per_seed_str)
    if pm >= BAND_HARD_PASS_PERM and fm <= BAND_HARD_PASS_FHRR_MAX and lm >= BAND_HARD_PASS_LIFT and pcv <= BAND_HARD_PASS_CV:
        return ("HARD_PASS", "HARD_PASS_CHAIN_GRADE: permutation-indexed binding resolves same-role collision across 3 seeds. %s" % base)
    if pm >= BAND_HARD_PASS_PARTIAL_PERM_LOW and (pcv > BAND_HARD_PASS_CV or fm > BAND_HARD_PASS_FHRR_MAX or lm < BAND_HARD_PASS_LIFT):
        return ("MIDDLE_BAND", "MIDDLE_BAND_PARTIAL: permutation lift present but at least one band not cleared. %s" % base)
    if pm < BAND_HARD_FAIL_PERM:
        return ("HARD_FAIL", "HARD_FAIL: permutation top1 %.4f < %.2f -- same-role collision is NOT the multi-occurrence bottleneck. %s" % (pm, BAND_HARD_FAIL_PERM, base))
    return ("MIDDLE_BAND", "MIDDLE_BAND: %s" % base)


print("[config] anchor=%s mode=%s D=%d seeds=%s" % (ANCHOR_NAME, RUN_MODE, D, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
t0 = time.time()
run_config = {"N": D, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d of %d seeds already complete; running %s" % (len(done), len(SEEDS), remaining), flush=True)
for seed in remaining:
    res = run_one_seed(seed)
    write_partial(out_dir, seed, res)
per_seed = list(aggregate_partials(out_dir, SEEDS).values())
agg = aggregate_seeds(per_seed)
v, vmsg = verdict(agg, per_seed)
print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "headline": vmsg,
           "run_mode": RUN_MODE, "n_seeds": len(per_seed), "seeds": [s["seed"] for s in per_seed],
           "aggregate": agg, "per_seed": per_seed, "elapsed_s": round(time.time() - t0, 2), "D": D,
           "bands": {"HARD_PASS_PERM": BAND_HARD_PASS_PERM, "HARD_PASS_FHRR_MAX": BAND_HARD_PASS_FHRR_MAX,
                     "HARD_PASS_LIFT": BAND_HARD_PASS_LIFT, "HARD_PASS_CV": BAND_HARD_PASS_CV, "HARD_FAIL_PERM": BAND_HARD_FAIL_PERM},
           "config_version": "v2_seeds_11_13_19_per_seed_FHRR_perturbed"}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
