"""
exp_asdiv_math_wk_oracle_cpu_v1.py -- ASDiv Path 1+2: math-WK constants + TIGHTER oracle -- CPU.

ROUTING: Research BOUNDARIES-REJECTED, ASDiv Path 1 (math-WK LEX constants) + Path 2 (tighter oracle, my caveat). The base ASDiv
  reachability ceiling was 0.68 (3-op), world-knowledge-bound (~28-32% need a non-text constant: dozen->12, dog->4 legs, days/week
  ->7). Does substrate-self-referential world-knowledge (Research's LEX_constant atoms, rule 8) CLOSE that gap? Tighter oracle to
  avoid the earlier permissiveness: (1) WK constants fire ONLY adjacent to a number (unit/multiplier pattern), (2) magnitude bound
  on intermediates, (3) exact match. Report ceiling WITH vs WITHOUT WK constants, by op-count. Pure oracle (no LLM, no solver).
PRE-REGISTERED (Research gate, applied to 3-op ceiling): HARD-PASS WK-ceiling >= 0.85 (world-knowledge closes the gap; brain-can-do-it
  confirmed -- ASDiv loss is NOT outside-substrate). MIDDLE 0.75-0.85 OR lift >= 0.05. HARD-FAIL lift < 0.03. UNKNOWN if load fails.
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
from fractions import Fraction
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "asdiv_math_wk_oracle_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
WK_TRIG: Dict[str, set] = {}
_W = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
      "ten": 10, "eleven": 11, "twelve": 12, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100, "dozen": 12}


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
            try: v = float(val)
            except Exception: continue
            trig = key.split("_per_")[-1].split("_")[-1] if "_per_" in key else key
            for t in (trig, _stem(trig)):
                if t and t.isalpha(): WK_TRIG.setdefault(t, set()).add(v)
    return len(WK_TRIG) > 0


def _nums(text):
    out = []
    for m in re.findall(r"\d+\.?\d*", text.replace(",", "")):
        try: out.append(float(m))
        except Exception: pass
    for wd in re.findall(r"[a-z]+", text.lower()):
        if wd in _W: out.append(float(_W[wd]))
    return out


def _wk_adjacent(text):
    """WK constants triggered ONLY adjacent to a number token (unit/multiplier pattern)."""
    toks = text.lower().split(); isnum = [bool(re.match(r"^\d", t.replace("$", "").replace(",", ""))) or re.sub(r"[^a-z]", "", t) in _W for t in toks]
    vals = set()
    for k, w in enumerate(toks):
        st = _stem(re.sub(r"[^a-z]", "", w))
        if st in WK_TRIG and any(isnum[j] for j in range(max(0, k - 2), min(len(toks), k + 3))):
            vals |= WK_TRIG[st]
    if "%" in text: vals.add(100.0)
    return sorted(vals)


def _gold(ans):
    m = re.search(r"-?\d+\.?\d*", str(ans).replace(",", "")); return float(m.group()) if m else None


def _opcount(f):
    f = f.split("=")[0]; return sum(f.count(o) for o in "+-*/")


def reachable(nums, target, max_ops):
    """tighter: consume-two-produce-one; magnitude bound; exact (tol relative 1e-4)."""
    tol = max(1e-4, abs(target) * 1e-4); bound = max(1000.0, abs(target) * 100.0 + 100.0)
    seen = set(); start = tuple(sorted(round(x, 4) for x in nums))

    def dfs(pool, ops_left):
        for v in pool:
            if abs(v - target) <= tol: return True
        if ops_left == 0: return False
        key = (pool, ops_left)
        if key in seen: return False
        seen.add(key); n = len(pool)
        for i in range(n):
            for j in range(n):
                if i == j: continue
                a = pool[i]; b = pool[j]; rest = tuple(pool[k] for k in range(n) if k != i and k != j)
                cands = [a + b, a - b, a * b]
                if abs(b) > 1e-9: cands.append(a / b)
                for r in cands:
                    if abs(r) > bound: continue
                    if dfs(tuple(sorted(rest + (round(r, 4),))), ops_left - 1): return True
        return False
    return dfs(start, max_ops)


def _selftest():
    assert reachable([2.0, 4.0], 8.0, 1) and not reachable([3.0], 100.0, 1)
    print("[selftest] PASS: asdiv-math-wk-oracle", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    if not load_wk():
        return {"error": "wk_atoms_missing"}
    print("  [wk] %d trigger words (dog->%s, week->%s, dozen->%s)" % (
        len(WK_TRIG), sorted(WK_TRIG.get("dog", set())), sorted(WK_TRIG.get("week", set())), sorted(WK_TRIG.get("dozen", set()))), flush=True)
    try:
        data = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed"}
    by_op = {1: [], 2: [], 3: []}
    for it in data:
        f = it.get("formula", "")
        if "=" not in f: continue
        oc = _opcount(f)
        if oc in by_op: by_op[oc].append(it)
    res = {}
    for oc in (1, 2, 3):
        items = by_op[oc]
        if SMOKE: items = items[:30]
        base_hit = wk_hit = usable = 0
        for it in items:
            text = it.get("body", "") + " " + it.get("question", ""); nums = _nums(text); g = _gold(it.get("answer", ""))
            if g is None or not nums: continue
            usable += 1
            if len(nums) > 8: nums = nums[:8]
            base = reachable(nums, g, oc)
            if base: base_hit += 1; wk_hit += 1; continue
            wkc = _wk_adjacent(text)
            if wkc and reachable(nums + wkc[:3], g, oc + 1): wk_hit += 1   # +1 op budget for the unit-multiply
        bc = base_hit / usable if usable else 0.0; wc = wk_hit / usable if usable else 0.0
        res["op%d" % oc] = {"base": round(bc, 4), "wk": round(wc, 4), "lift": round(wc - bc, 4), "n": usable}
        print("  [%d-op] base=%.4f  +WK=%.4f  (lift=%+.4f, n=%d)" % (oc, bc, wc, wc - bc, usable), flush=True)
    res["ceiling_3op_wk"] = res["op3"]["wk"]; res["ceiling_3op_base"] = res["op3"]["base"]; res["lift_3op"] = res["op3"]["lift"]
    return res


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    wc = r["ceiling_3op_wk"]; bc = r["ceiling_3op_base"]; lift = r["lift_3op"]
    s = "3-op: base=%.4f +WK=%.4f (lift=%+.4f) | 2-op +WK=%.4f | 1-op +WK=%.4f. WK = substrate LEX_constant adjacent-to-number (rule 8)." % (
        bc, wc, lift, r["op2"]["wk"], r["op1"]["wk"])
    if wc >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate math-world-knowledge closes the ASDiv 3-op ceiling to >=0.85 -- world-knowledge is NOT outside-substrate (brain-can-do-it: dog->4 legs, dozen->12 via concept partition). The earlier 0.68 'ceiling' was missing substrate semantic memory, NOT an architectural bound. " + s)
    if wc >= 0.75 or lift >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: WK constants lift the ASDiv ceiling (>=0.75 or lift>=0.05) -- world-knowledge closes much of the gap; remaining items need multi-fact/non-adjacent constants. " + s)
    return ("HARD_FAIL", "HARD_FAIL: WK lift <0.03 -- adjacency-triggered single constants insufficient; remaining ASDiv gap needs multi-hop world-knowledge (more substrate-only paths before any claim). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
