"""
exp_asdiv_program_ranker_cpu_v1.py -- ASDiv solver: program-search + discriminative ranker (realize WK ceiling) -- CPU.

ROUTING: Research priority-1 (realize the +0.114 WK-augmented ASDiv ceiling into accuracy). The single-pair learned selector
  underperformed (0.18; can't chain 2-op, WK hurt selection). Research design: extract text-numbers + WK constants -> enumerate
  candidate PROGRAMS (operand subset <=3 numbers, op-chain <=2 ops) -> discriminative RANKER picks the gold program -> execute.
  This is the multi-hop / role-binding mechanism as a program search + learned ranker (substrate-discriminative; realizes the
  oracle's coverage with a learned policy). Bundled ASDiv. WK constants = substrate LEX_constant concept partition (rule 8). No LLM.
PRE-REGISTERED (Research gate): HARD-PASS overall >= 0.32 (from ~0.22 baseline). MIDDLE 0.28-0.32. HARD-FAIL < 0.28. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, re
from pathlib import Path
from typing import Dict, Tuple, List
from collections import defaultdict
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "asdiv_program_ranker_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: (a / b if b != 0 else None)}
OPNAMES = list(OPS.keys())
WK_TRIG: Dict[str, set] = {}
_WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
            "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100}


def _stem(w):
    w = w.lower()
    if w.endswith("ies") and len(w) > 4: return w[:-3] + "y"
    if w.endswith("s") and not w.endswith("ss") and len(w) > 2: return w[:-1]
    return w


def load_wk():
    fp = REPO / "data" / "substrate_index" / "concept_corpus_math_world_knowledge_lex_atoms.jsonl"
    if not fp.exists(): return False
    for line in open(fp, encoding="utf-8"):
        line = line.strip()
        if not line: continue
        a = json.loads(line)
        for key, val in a.get("members_named_values", {}).items():
            try: v = Fraction(str(val)).limit_denominator(10**6)
            except Exception: continue
            trig = key.split("_per_")[-1].split("_")[-1] if "_per_" in key else key
            for t in (trig, _stem(trig)):
                if t and t.isalpha(): WK_TRIG.setdefault(t, set()).add(v)
    return True


def _numinfo(text):
    toks = text.lower().split(); out = []; qstart = None
    for k, w in enumerate(toks):
        if w == "how" and qstart is None: qstart = k
    for k, w in enumerate(toks):
        ww = w.replace("$", "").replace(",", "").rstrip("?.,")
        val = Fraction(ww) if re.match(r"^\d+(?:\.\d+)?$", ww) else (Fraction(_WORDNUM[ww]) if ww in _WORDNUM else None)
        if val is not None:
            noun = re.sub(r"[^a-z]", "", toks[k + 1]) if k + 1 < len(toks) else ""
            out.append({"v": val, "noun": noun, "in_q": (qstart is not None and k >= qstart), "wk": False})
    return out


def _wk_extra(text):
    toks = text.lower().split(); isnum = [bool(re.match(r"^\d", t)) or re.sub(r"[^a-z]", "", t) in _WORDNUM for t in toks]
    extra = []; seen = set()
    for k, w in enumerate(toks):
        st = _stem(re.sub(r"[^a-z]", "", w))
        if st in WK_TRIG and any(isnum[j] for j in range(max(0, k - 2), min(len(toks), k + 3))):
            for v in WK_TRIG[st]:
                if v in seen: continue
                seen.add(v); extra.append({"v": v, "noun": st, "in_q": False, "wk": True})
    if "%" in text and Fraction(100) not in seen: extra.append({"v": Fraction(100), "noun": "percent", "in_q": False, "wk": True})
    return extra


def _target(text):
    m = re.search(r"how (?:many|much) ([a-z]+)", text.lower()); return _stem(m.group(1)) if m else ""


def _howmany(text):
    return "how many" in text.lower()


def enumerate_programs(pool, want_int):
    """all programs over <=3 numbers, <=2 ops producing a plausible positive result. Each: (nums[list of dict], ops[list], result)."""
    n = len(pool); progs = []
    maxmag = 1e7
    for i in range(n):
        for j in range(n):
            if i == j: continue
            a, b = pool[i], pool[j]
            for o1 in OPNAMES:
                r1 = OPS[o1](a["v"], b["v"])
                if r1 is None or r1 <= 0 or abs(r1) > maxmag: continue
                if want_int and r1.denominator != 1: pass  # allow; many intermediate are int
                progs.append(([a, b], [o1], r1))
                # 2-op: (a o1 b) o2 c
                for k in range(n):
                    if k == i or k == j: continue
                    c = pool[k]
                    for o2 in OPNAMES:
                        r2 = OPS[o2](r1, c["v"])
                        if r2 is None or r2 <= 0 or abs(r2) > maxmag: continue
                        progs.append(([a, b, c], [o1, o2], r2))
    return progs


def _prog_feats(nums, ops, result, target, in_q_any):
    fs = ["BIAS", "nops:%d" % len(ops), "chain:%s" % "".join(ops)]
    for o in ops: fs.append("op:" + o)
    nwk = sum(1 for d in nums if d["wk"]); ntg = sum(1 for d in nums if target and _stem(d["noun"]) == target)
    nq = sum(1 for d in nums if d["in_q"])
    fs.append("nwk:%d" % nwk); fs.append("ntgt:%d" % min(ntg, 2)); fs.append("ninq:%d" % min(nq, 2))
    if nwk: fs.append("uses_wk")
    if ntg: fs.append("uses_target")
    fs.append("res_int" if result.denominator == 1 else "res_frac")
    fs.append("nnums:%d" % len(nums))
    # last operand role (often the divisor/group-size)
    last = nums[-1]
    fs.append("last_wk" if last["wk"] else ("last_tgt" if target and _stem(last["noun"]) == target else "last_other"))
    fs.append("last_noun:" + last["noun"])
    return fs


def _selftest():
    p = enumerate_programs([{"v": Fraction(2), "noun": "dog", "in_q": False, "wk": False},
                            {"v": Fraction(4), "noun": "leg", "in_q": False, "wk": True}], True)
    assert any(r == Fraction(8) for _n, _o, r in p)
    print("[selftest] PASS: asdiv-program-ranker", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _build(items, augment):
    """build (text, pool, target, want_int, ans) instances."""
    out = []
    for text, ans in items:
        pool = _numinfo(text)
        if augment: pool = pool + _wk_extra(text)
        if len(pool) > 8: pool = pool[:8]
        if len(pool) < 2: continue
        out.append((text, pool, _target(text), _howmany(text), ans))
    return out


def _run_variant(train_items, test_full, augment, seed):
    rng = np.random.default_rng(seed)
    TR = _build([(t, a) for t, a, _o in train_items], augment)
    w = defaultdict(float); cw = defaultdict(float); c = 1
    # precompute candidate programs + gold flag for training
    train_cache = []
    for text, pool, target, wi, ans in TR:
        progs = enumerate_programs(pool, wi)
        gold = [idx for idx, (_n, _o, r) in enumerate(progs) if r == ans]
        if not gold or not progs: continue
        feats = [_prog_feats(n, o, r, target, any(d["in_q"] for d in pool)) for (n, o, r) in progs]
        train_cache.append((feats, set(gold)))
    for ep in range(8 if not SMOKE else 3):
        for ci in rng.permutation(len(train_cache)):
            feats, gold = train_cache[ci]
            scores = [sum(w[f] for f in ff) for ff in feats]
            pred = int(np.argmax(scores))
            if pred not in gold:
                gi = min(gold, key=lambda g: -sum(w[f] for f in feats[g]))  # highest-scoring gold
                for f in feats[gi]: w[f] += 1; cw[f] += c
                for f in feats[pred]: w[f] -= 1; cw[f] -= c
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    # evaluate
    flags = [0] * len(test_full)
    for ti, (text, ans, oc) in enumerate(test_full):
        pool = _numinfo(text)
        if augment: pool = pool + _wk_extra(text)
        if len(pool) > 8: pool = pool[:8]
        if len(pool) < 2: continue
        target = _target(text); wi = _howmany(text); progs = enumerate_programs(pool, wi)
        if not progs: continue
        best = max(progs, key=lambda p: sum(avg.get(f, 0.0) for f in _prog_feats(p[0], p[1], p[2], target, any(d["in_q"] for d in pool))))
        if best[2] == ans: flags[ti] = 1
    return sum(flags) / len(test_full) if test_full else 0.0, flags


def run() -> Dict:
    if not load_wk(): return {"error": "wk_atoms_missing"}
    try:
        d = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed"}
    items = []
    for e in d:
        f = e.get("formula", "")
        if "=" not in f: continue
        a = None
        m = re.search(r"-?\d+\.?\d*", str(e.get("answer", "")).replace(",", ""))
        if m:
            try: a = Fraction(m.group()).limit_denominator(10**6)
            except Exception: a = None
        if a is None: continue
        oc = sum(f.split("=")[0].count(o) for o in "+-*/")
        items.append(((e.get("body", "") + " " + e.get("question", "")).strip(), a, oc))
    cut = int(len(items) * 0.7); train_items = items[:cut]; test_full = items[cut:]
    if SMOKE: train_items = train_items[:400]; test_full = test_full[:150]
    seed = int(os.environ.get("HDLAB_SEED", "1011"))
    base_acc, base_flags = _run_variant(train_items, test_full, augment=False, seed=seed)
    wk_acc, wk_flags = _run_variant(train_items, test_full, augment=True, seed=seed)
    print("  ASDiv program-ranker: base=%.4f  +WK=%.4f  (vs prior ~0.22, test=%d)" % (base_acc, wk_acc, len(test_full)), flush=True)
    for oc in (1, 2, 3):
        idxs = [i for i, (_t, _a, o) in enumerate(test_full) if o == oc]
        if idxs:
            print("    [%d-op] base=%.4f +WK=%.4f (n=%d)" % (oc, sum(base_flags[i] for i in idxs) / len(idxs), sum(wk_flags[i] for i in idxs) / len(idxs), len(idxs)), flush=True)
    return {"accuracy": round(wk_acc, 4), "acc_wk": round(wk_acc, 4), "acc_base": round(base_acc, 4),
            "lift": round(wk_acc - base_acc, 4), "n_test": len(test_full)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    aw = r["acc_wk"]; ab = r["acc_base"]
    s = "ASDiv program-ranker +WK=%.4f vs base=%.4f (lift=%+.4f) vs prior ~0.22 (test=%d). Subset(<=3)+op-chain(<=2) search + discriminative ranker; WK = substrate LEX_constant." % (aw, ab, r["lift"], r["n_test"])
    if aw >= 0.32:
        return ("HARD_PASS", "HARD_PASS: substrate program-ranker + math-WK realizes ASDiv >=0.32 (Research target, up from ~0.22) -- multi-hop subset/chain search with discriminative ranking realizes the WK-augmented ceiling; ASDiv NOT outside-substrate. " + s)
    if aw >= 0.28:
        return ("MIDDLE_BAND", "MIDDLE_BAND: ASDiv 0.28-0.32 -- big lift over 0.22; richer ranker features / multi-hop binding for more. " + s)
    return ("HARD_FAIL", "HARD_FAIL: ASDiv <0.28. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
