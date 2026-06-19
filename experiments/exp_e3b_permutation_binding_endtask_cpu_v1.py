"""
exp_e3b_permutation_binding_endtask_cpu_v1.py -- E3 END-TASK: permutation binding effect on multi-occurrence MWP solving -- CPU.

ROUTING: completes Research E3 pre-reg ("+10 abs pts ASDiv multi-occurrence subset") -- the end-task version of the binding-isolation
  E3 (which gave FHRR 0.07 -> perm 1.0 with GOLD slots). Here a SHARED discriminative selector picks (slot_i, op, slot_j) from
  per-slot + question features; the ONLY difference between arms is RETRIEVAL from the number bundle: FHRR role-only key (collides on
  same-role occurrences) vs permutation (role,occ) key roll(role_vec, occ*7) (clean). Selection held constant -> isolates the binding
  effect on actual answer accuracy. ASDiv-1op multi-occurrence subset, train/test split. Same FHRR primitives (D=512).
PRE-REGISTERED (Drill 1 / Research E3): HARD-PASS perm - FHRR end-acc >= +0.10 on multi-occurrence subset. MIDDLE +0.05-0.10.
  HARD-FAIL < +0.05. UNKNOWN if subset/gold empty.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, re, zlib
from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "e3b_permutation_binding_endtask_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
D = 512
OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "rs": lambda a, b: b - a, "*": lambda a, b: a * b,
       "/": lambda a, b: (a / b if b != 0 else None), "rd": lambda a, b: (b / a if a != 0 else None)}
OPNAMES = list(OPS.keys())
ROLES = ["PER", "TGT", "TOT", "SUB", "ADD", "INQ", "CNT", "WK"]
PER_CUES = ("each", "per", "every", "apiece"); TOT_CUES = ("total", "altogether", "all", "combined", "sum", "together")
SUB_CUES = ("gave", "lost", "spent", "sold", "ate", "used", "removed", "left", "fewer", "remain", "broke", "dropped", "away")
ADD_CUES = ("got", "bought", "received", "found", "added", "gained", "more", "picked", "another")
_WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "twelve": 12}


def _fhrr(seed): rng = np.random.default_rng(seed); return np.exp(1j * rng.uniform(0, 2 * np.pi, D))
_ROLE_VEC = {r: _fhrr(zlib.crc32(("role:" + r).encode())) for r in ROLES}
def _num_vec(v): return _fhrr(zlib.crc32(("num:%s" % str(v)).encode()) & 0x7fffffff)
def bind(a, b): return a * b
def unbind(key, bundle): return bundle * np.conj(key)
def bundle_norm(v): m = np.abs(v); m[m < 1e-9] = 1.0; return v / m
def roll_key(rv, k): return rv if k == 0 else np.roll(rv, k * 7)
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
        out.append({"v": val, "role": _primary_role(roles), "pos": k, "ctx": ctx, "noun": noun})
    seen = {}
    for d in out:
        r = d["role"]; d["occ"] = seen.get(r, 0); seen[r] = d["occ"] + 1
    return out, tgt


def _is_multiocc(pool):
    seen = {}
    for d in pool: seen[d["role"]] = seen.get(d["role"], 0) + 1
    return any(c >= 2 for c in seen.values())


def build_bundle(pool, use_perm):
    v = np.zeros(D, dtype=complex)
    for d in pool:
        key = roll_key(_ROLE_VEC[d["role"]], d["occ"]) if use_perm else _ROLE_VEC[d["role"]]
        v = v + bind(key, _num_vec(d["v"]))
    return bundle_norm(v)


def retrieve(pool, i, use_perm, protos):
    d = pool[i]; key = roll_key(_ROLE_VEC[d["role"]], d["occ"]) if use_perm else _ROLE_VEC[d["role"]]
    return cleanup(unbind(key, build_bundle(pool, use_perm)), protos)


def _slot_feats(pool, i, n):
    d = pool[i]; fs = ["r:" + d["role"], "occ:%d" % min(d["occ"], 3), "posb:%d" % (0 if d["pos"] < 5 else (1 if d["pos"] < 12 else 2))]
    for c in PER_CUES + SUB_CUES + ADD_CUES + TOT_CUES:
        if c in d["ctx"]: fs.append("c:" + c)
    if i == n - 1: fs.append("LAST")
    if i == 0: fs.append("FIRST")
    return fs


def _qfeats(text):
    low = text.lower(); fs = set()
    for cue in PER_CUES + TOT_CUES + SUB_CUES + ADD_CUES + ("times", "divide", "share", "groups", "left", "difference", "each", "more", "fewer"):
        if cue in low: fs.add("q:" + cue)
    fs.add("QB"); return fs


def _cand_feats(text, pool, cand, qf):
    i, op, j = cand; n = len(pool)
    fs = ["op:" + op]
    for f in _slot_feats(pool, i, n): fs.append("A|" + f + "|" + op)
    for f in _slot_feats(pool, j, n): fs.append("B|" + f + "|" + op)
    for q in qf: fs.append(q + "|op:" + op)
    return fs


def _gold_cand(pool, ans):
    n = len(pool)
    for i in range(n):
        for j in range(n):
            if i == j: continue
            for op in OPNAMES:
                r = OPS[op](pool[i]["v"], pool[j]["v"])
                if r is not None and r > 0 and Fraction(r).limit_denominator(10**6) == ans:
                    return (i, op, j)
    return None


def _selftest():
    pool, _ = extract("Tom has 5 marbles and then found 3 marbles . how many marbles ?")
    assert _is_multiocc(pool) or len(pool) >= 2
    p2, _ = extract("a has 5 x and b has 3 x")
    protos = [(d["v"], _num_vec(d["v"])) for d in p2]
    if _is_multiocc(p2):
        assert retrieve(p2, 0, True, protos) == p2[0]["v"]
    print("[selftest] PASS: e3b-permutation-binding-endtask", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _build_examples(items):
    ex = []
    for text, ans in items:
        pool, tgt = extract(text)
        if len(pool) < 2 or not _is_multiocc(pool): continue
        gc = _gold_cand(pool, ans)
        if gc is None: continue
        ex.append((text, pool, gc, ans))
    return ex


def _train_selector(train_ex, seed):
    rng = np.random.default_rng(seed); w = defaultdict(float); cw = defaultdict(float); c = 1
    cache = []
    for text, pool, gc, ans in train_ex:
        n = len(pool); qf = _qfeats(text)
        cands = [(i, op, j) for i in range(n) for j in range(n) if i != j for op in OPNAMES]
        gi = cands.index(gc) if gc in cands else None
        if gi is None: continue
        cache.append(([_cand_feats(text, pool, ca, qf) for ca in cands], gi))
    for ep in range(8 if not SMOKE else 3):
        for ci in rng.permutation(len(cache)):
            feats, gi = cache[ci]; scores = [sum(w[f] for f in ff) for ff in feats]
            pred = int(np.argmax(scores))
            if pred != gi:
                for f in feats[gi]: w[f] += 1; cw[f] += c
                for f in feats[pred]: w[f] -= 1; cw[f] -= c
            c += 1
    return {f: w[f] - cw[f] / c for f in w}


def _eval(test_ex, avg, use_perm):
    cor = tot = 0
    for text, pool, gc, ans in test_ex:
        n = len(pool); qf = _qfeats(text)
        cands = [(i, op, j) for i in range(n) for j in range(n) if i != j for op in OPNAMES]
        best = max(cands, key=lambda ca: sum(avg.get(f, 0.0) for f in _cand_feats(text, pool, ca, qf)))
        i, op, j = best
        protos = [(d["v"], _num_vec(d["v"])) for d in pool]
        na = retrieve(pool, i, use_perm, protos); nb = retrieve(pool, j, use_perm, protos)
        tot += 1
        if na is None or nb is None: continue
        r = OPS[op](na, nb)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: cor += 1
    return cor / tot if tot else 0.0, tot


def _load_asdiv_1op():
    d = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8")); items = []
    for e in d:
        f = e.get("formula", "")
        if "=" not in f or sum(f.split("=")[0].count(o) for o in "+-*/") != 1: continue
        m = re.search(r"-?\d+\.?\d*", str(e.get("answer", "")))
        if not m: continue
        items.append(((e.get("body", "") + " " + e.get("question", "")).strip(), Fraction(m.group()).limit_denominator(10**6)))
    return items


def run() -> Dict:
    try:
        items = _load_asdiv_1op()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed"}
    if SMOKE: items = items[:300]
    ex = _build_examples(items)
    if len(ex) < 10: return {"error": "subset_too_small_%d" % len(ex)}
    cut = int(len(ex) * 0.7); train_ex, test_ex = ex[:cut], ex[cut:]
    avg = _train_selector(train_ex, seed=11)
    f_acc, n = _eval(test_ex, avg, use_perm=False)
    p_acc, _ = _eval(test_ex, avg, use_perm=True)
    print("  multi-occurrence end-task: train=%d test=%d" % (len(train_ex), len(test_ex)), flush=True)
    print("  FHRR role-only retrieval:   end-acc=%.4f" % f_acc, flush=True)
    print("  permutation (role,occ):     end-acc=%.4f" % p_acc, flush=True)
    print("  permutation lift = %+.4f (shared selector; only retrieval differs)" % (p_acc - f_acc), flush=True)
    return {"f1": round(p_acc, 4), "fhrr_endacc": round(f_acc, 4), "perm_endacc": round(p_acc, 4),
            "lift": round(p_acc - f_acc, 4), "n_test": n, "n_subset": len(ex)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    lift = r["lift"]; s = "FHRR=%.4f perm=%.4f lift=%+.4f (multi-occ end-task, test=%d, subset=%d)" % (r["fhrr_endacc"], r["perm_endacc"], lift, r["n_test"], r["n_subset"])
    if lift >= 0.10:
        return ("HARD_PASS", "HARD_PASS: permutation binding lifts END-TASK multi-occurrence MWP accuracy >=+0.10 (shared selector; FHRR can't retrieve same-role occurrences, permutation can). " + s)
    if lift >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: permutation binding end-task lift +0.05-0.10. " + s)
    return ("HARD_FAIL", "HARD_FAIL: permutation binding end-task lift <+0.05 -- retrieval collision not the end-task bottleneck (selection dominates). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
