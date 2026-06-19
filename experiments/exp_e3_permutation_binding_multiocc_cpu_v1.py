"""
exp_e3_permutation_binding_multiocc_cpu_v1.py -- E3: permutation-indexed binding for non-unique (multi-occurrence) roles -- CPU.

ROUTING: Research UNROUTED inventory E3 (Drill 1 RANK 2). The earlier FHRR multi-hop binding (multihop_fhrr_binding 0.18) failed
  because numbers sharing a ROLE collide in superposition -- unbind(role, bundle) returns a MIX of same-role numbers. FIX
  (Recchia-Jones 2015 random-permutation binding; brain analogue bump-attractor desync Wei-Wang-Wang 2012): bind the k-th occurrence
  of a role with a PERMUTED key roll(role_vec, k), so distinct occurrences get near-orthogonal keys and recover cleanly.
MECHANISM-ISOLATION A/B (gold template -> tests BINDING not selection): on the ASDiv multi-occurrence subset (problems where >=2
  extracted operands share a role), recover operands via (A) plain FHRR [bind(role,num)] vs (B) permutation [bind(roll(role,occ),num)],
  execute the gold op, check the answer. Metric = operand-recovery/answer accuracy on the subset. Same FHRR primitives (D=512).
PRE-REGISTERED (Drill 1): HARD-PASS perm - FHRR >= +0.10 abs on multi-occurrence subset (permutation resolves same-role collision).
  MIDDLE +0.05-0.10. HARD-FAIL < +0.05 (collision not the bottleneck). UNKNOWN if subset empty / load fails.
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
from typing import Dict, Tuple, List
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "e3_permutation_binding_multiocc_cpu_v1"
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
_WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "twenty": 20}


def _fhrr(seed): rng = np.random.default_rng(seed); return np.exp(1j * rng.uniform(0, 2 * np.pi, D))
_ROLE_VEC = {r: _fhrr(zlib.crc32(("role:" + r).encode())) for r in ROLES}
def _num_vec(v): return _fhrr(zlib.crc32(("num:%s" % str(v)).encode()) & 0x7fffffff)
def bind(a, b): return a * b
def unbind(key, bundle): return bundle * np.conj(key)
def bundle_norm(v): m = np.abs(v); m[m < 1e-9] = 1.0; return v / m
def roll_key(role_vec, k): return role_vec if k == 0 else np.roll(role_vec, k * 7)  # permutation power = cyclic shift (stride 7)
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
    """add occurrence index per role (0,1,2,...) in reading order."""
    seen = {}
    for d in pool:
        r = d["role"]; d["occ"] = seen.get(r, 0); seen[r] = d["occ"] + 1
    return pool


def build_bundle(pool, use_perm):
    v = np.zeros(D, dtype=complex)
    for d in pool:
        key = roll_key(_ROLE_VEC[d["role"]], d["occ"]) if use_perm else _ROLE_VEC[d["role"]]
        v = v + bind(key, _num_vec(d["v"]))
    return bundle_norm(v)


def fetch(bundle, role, occ, protos, use_perm):
    key = roll_key(_ROLE_VEC[role], occ) if use_perm else _ROLE_VEC[role]
    return cleanup(unbind(key, bundle), protos)


def _is_multiocc(pool):
    seen = {}
    for d in pool: seen[d["role"]] = seen.get(d["role"], 0) + 1
    return any(c >= 2 for c in seen.values())


def _gold_slots(pool, ans):
    """find a (i,op,j) over pool indices whose op(v_i,v_j)==ans (slot-level gold; uses occ keys)."""
    n = len(pool)
    for i in range(n):
        for j in range(n):
            if i == j: continue
            for op in OPNAMES:
                r = OPS[op](pool[i]["v"], pool[j]["v"])
                if r is not None and r > 0 and Fraction(r).limit_denominator(10**6) == ans:
                    return (i, op, j)
    return None


def _eval_subset(items, use_perm):
    cor = tot = 0
    for text, ans in items:
        pool, tgt = extract(text)
        if len(pool) < 2 or not _is_multiocc(pool): continue
        _assign_occ(pool)
        gs = _gold_slots(pool, ans)
        if gs is None: continue
        tot += 1
        i, op, j = gs
        protos = [(d["v"], _num_vec(d["v"])) for d in pool]
        bun = build_bundle(pool, use_perm)
        na = fetch(bun, pool[i]["role"], pool[i]["occ"], protos, use_perm)
        nb = fetch(bun, pool[j]["role"], pool[j]["occ"], protos, use_perm)
        if na is None or nb is None: continue
        r = OPS[op](na, nb)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: cor += 1
    return (cor / tot if tot else 0.0), tot


def _selftest():
    # multi-occurrence: two CNT numbers; plain FHRR collides, permutation separates
    pool = _assign_occ([{"v": Fraction(5), "role": "CNT"}, {"v": Fraction(3), "role": "CNT"}])
    protos = [(d["v"], _num_vec(d["v"])) for d in pool]
    bun_p = build_bundle(pool, True)
    a = fetch(bun_p, "CNT", 0, protos, True); b = fetch(bun_p, "CNT", 1, protos, True)
    assert a == Fraction(5) and b == Fraction(3), "permutation must separate occurrences"
    print("[selftest] PASS: e3-permutation-binding-multiocc", flush=True)


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


def run() -> Dict:
    try:
        items = _load_asdiv_1op()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed"}
    if SMOKE: items = items[:200]
    f_acc, n = _eval_subset(items, use_perm=False)
    p_acc, n2 = _eval_subset(items, use_perm=True)
    print("  multi-occurrence subset n=%d" % n, flush=True)
    print("  FHRR (role-only key):        answer-acc=%.4f" % f_acc, flush=True)
    print("  permutation (role,occ) key:  answer-acc=%.4f" % p_acc, flush=True)
    print("  permutation lift = %+.4f (predicted >= +0.10; resolves same-role collision)" % (p_acc - f_acc), flush=True)
    return {"f1": round(p_acc, 4), "fhrr_acc": round(f_acc, 4), "perm_acc": round(p_acc, 4),
            "lift": round(p_acc - f_acc, 4), "n_subset": n}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    if r["n_subset"] == 0: return ("UNKNOWN", "UNKNOWN: multi-occurrence subset empty")
    lift = r["lift"]; s = "FHRR=%.4f permutation=%.4f lift=%+.4f (multi-occurrence subset n=%d)" % (r["fhrr_acc"], r["perm_acc"], lift, r["n_subset"])
    if lift >= 0.10:
        return ("HARD_PASS", "HARD_PASS: permutation-indexed binding resolves same-role collision +>=0.10 on multi-occurrence subset -- distinct occurrence keys recover operands FHRR superposition mixes. " + s)
    if lift >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: permutation binding adds +0.05-0.10 on multi-occurrence subset. " + s)
    return ("HARD_FAIL", "HARD_FAIL: permutation binding lift <+0.05 -- same-role superposition collision is NOT the multi-occurrence bottleneck. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
