"""
exp_multihop_fhrr_binding_cpu_v1.py -- Path 1 (pulled forward): literal FHRR role-VECTOR binding + template enumeration -- CPU.

ROUTING: Research GO (Path 1 forward + Path 3 parallel). Path 2 (learned role labels) REFUTED -- role-label quality is not the
  bottleneck; selection AMBIGUITY is. Hypothesis (Exp-Dev + Research): role-as-VECTOR binding disambiguates where role-as-LABEL +
  discriminative features cannot. Mechanism (Cycle-#5 CAP_fhrr_bind/unbind/cleanup): each number bound to its role vector; bundle =
  sum bind(role_i, n_i); a TEMPLATE (role_a, op, role_b) is predicted discriminatively; operands FETCHED by unbind(role, bundle) ->
  cleanup to the problem's number codebook (vector geometry selects the operand, NOT a learned pair-selector). Combines Path 1
  (binding) + Path 3 (template enumeration). SVAMP + ASDiv-1op. Brain analogue: theta-gamma phase binding (Lisman 2013). No LLM.
PRE-REGISTERED (Research gate): HARD-PASS ASDiv-1op >= 0.45 (binding disambiguates). MIDDLE 0.40-0.45. HARD-FAIL <= 0.40 (binding
  doesn't beat role-labels -> bottleneck is question-semantics, pivot to FCG). UNKNOWN if load fails.
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
from collections import defaultdict
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "multihop_fhrr_binding_cpu_v1"
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
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100}
WK_PER: List = []; WK_COLL: Dict = {}


# ---------- FHRR primitives (complex unit-modulus) ----------
def _fhrr(seed):
    rng = np.random.default_rng(seed); return np.exp(1j * rng.uniform(0, 2 * np.pi, D))


_ROLE_VEC = {r: _fhrr(zlib.crc32(("role:" + r).encode())) for r in ROLES}


def _num_vec(v):
    return _fhrr(zlib.crc32(("num:%s" % str(v)).encode()) & 0x7fffffff)


def bind(a, b): return a * b
def unbind(role, bundle): return bundle * np.conj(role)
def bundle_norm(v):
    m = np.abs(v); m[m < 1e-9] = 1.0; return v / m


def cleanup(vec, protos):
    """nearest prototype by real-cosine; protos = list of (value, vector)."""
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
            if "_per_" in key:
                x = _st(key.split("_per_")[0].split("_")[-1]); y = _st(key.split("_per_")[-1].split("_")[-1])
                if x.isalpha() and y.isalpha(): WK_PER.append((x, y, v))
            elif key.isalpha(): WK_COLL[_st(key)] = v
    return True


def _primary_role(roles):
    for r in ["PER", "TGT", "TOT", "SUB", "ADD", "INQ", "CNT"]:
        if r in roles: return r
    return "CNT"


def extract(text):
    low = text.lower(); toks = low.split(); qs = None
    for k, w in enumerate(toks):
        if w == "how" and qs is None: qs = k
    m = re.search(r"how (?:many|much) ([a-z]+)", low); tgt = _st(m.group(1)) if m else ""
    wordset = set(_st(re.sub(r"[^a-z]", "", w)) for w in toks)
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
    for (x, y, v) in WK_PER:
        if tgt and tgt == x and y in wordset: out.append({"v": v, "role": "WK"})
    for k, w in enumerate(toks):
        st = _st(re.sub(r"[^a-z]", "", w)); isn = lambda j: 0 <= j < len(toks) and bool(re.match(r"^\d", toks[j]))
        if st in WK_COLL and (isn(k - 1) or isn(k + 1) or isn(k - 2) or isn(k + 2)): out.append({"v": WK_COLL[st], "role": "WK"})
    if "%" in text: out.append({"v": Fraction(100), "role": "WK"})
    return out, tgt


def build_bundle(pool):
    v = np.zeros(D, dtype=complex)
    for d in pool: v = v + bind(_ROLE_VEC[d["role"]], _num_vec(d["v"]))
    return bundle_norm(v)


def fetch(bundle, role, protos):
    return cleanup(unbind(_ROLE_VEC[role], bundle), protos)


def _qfeats(text):
    low = text.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    for cue in PER_CUES + TOT_CUES + SUB_CUES + ADD_CUES + ("times", "divide", "share", "groups", "each", "left", "difference"):
        if cue in low: fs.add("q:" + cue)
    fs.add("QBIAS"); return fs


def _templates(pool):
    """candidate templates (role_a, op, role_b) over roles PRESENT in the pool."""
    present = sorted(set(d["role"] for d in pool))
    return [(ra, op, rb) for ra in present for rb in present for op in OPNAMES]


def _exec_template(pool, tmpl, protos):
    ra, op, rb = tmpl; na = fetch(build_bundle(pool), ra, protos); nb = fetch(build_bundle(pool), rb, protos)
    if na is None or nb is None: return None
    return OPS[op](na, nb)


def _selftest():
    # FHRR bind/unbind/cleanup recovers the bound number
    pool = [{"v": Fraction(5), "role": "PER"}, {"v": Fraction(3), "role": "TGT"}]
    protos = [(d["v"], _num_vec(d["v"])) for d in pool]; bun = build_bundle(pool)
    assert fetch(bun, "PER", protos) == Fraction(5) and fetch(bun, "TGT", protos) == Fraction(3)
    print("[selftest] PASS: multihop-fhrr-binding", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _solve(train, test, seed):
    rng = np.random.default_rng(seed)
    TR = []
    for text, ans in train:
        pool, tgt = extract(text)
        if len(pool) < 2: continue
        protos = [(d["v"], _num_vec(d["v"])) for d in pool]; bun = build_bundle(pool)
        # gold template: search (ra, op, rb) whose binding-fetch yields the answer
        gold = None
        for tmpl in _templates(pool):
            r = _exec_template(pool, tmpl, protos)
            if r is not None and r > 0 and Fraction(r).limit_denominator(10**6) == ans: gold = tmpl; break
        if gold is None: continue
        TR.append((text, pool, gold))
    if not TR: return 0.0, 0
    # discriminative template-selector: question features -> template (predict role_a, op, role_b jointly via 3 heads + role-presence gating)
    w = defaultdict(float); cw = defaultdict(float); c = 1
    def tfeats(text, tmpl):
        ra, op, rb = tmpl; qf = _qfeats(text)
        fs = ["T:%s_%s_%s" % (ra, op, rb), "op:" + op, "ra:" + ra, "rb:" + rb]
        for q in qf:
            fs.append("%s|op:%s" % (q, op)); fs.append("%s|ra:%s" % (q, ra)); fs.append("%s|rb:%s" % (q, rb))
        return fs
    cache = []
    for text, pool, gold in TR:
        cands = _templates(pool)
        gi = next((idx for idx, t in enumerate(cands) if t == gold), None)
        if gi is None: continue
        cache.append(([tfeats(text, t) for t in cands], gi))
    for ep in range(8 if not SMOKE else 3):
        for ci in rng.permutation(len(cache)):
            feats, gi = cache[ci]; scores = [sum(w[f] for f in ff) for ff in feats]
            pred = int(np.argmax(scores))
            if pred != gi:
                for f in feats[gi]: w[f] += 1; cw[f] += c
                for f in feats[pred]: w[f] -= 1; cw[f] -= c
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    cor = 0
    for text, ans in test:
        pool, tgt = extract(text)
        if len(pool) < 2: continue
        protos = [(d["v"], _num_vec(d["v"])) for d in pool]; cands = _templates(pool)
        if not cands: continue
        best = max(cands, key=lambda t: sum(avg.get(f, 0.0) for f in tfeats(text, t)))
        r = _exec_template(pool, best, protos)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: cor += 1
    return cor / len(test) if test else 0.0, len(TR)


def _load_svamp():
    d = json.load(open(REPO / "experiments" / "data" / "svamp.json", encoding="utf-8"))
    def conv(sp): return [((e.get("body", "") + " " + e.get("question", "")).strip(), Fraction(re.search(r"-?\d+\.?\d*", str(e.get("answer"))).group()).limit_denominator(10**6)) for e in d.get(sp, []) if re.search(r"-?\d+\.?\d*", str(e.get("answer")))]
    return conv("train"), conv("test")


def _load_asdiv_1op():
    d = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8")); items = []
    for e in d:
        f = e.get("formula", "")
        if "=" not in f or sum(f.split("=")[0].count(o) for o in "+-*/") != 1: continue
        m = re.search(r"-?\d+\.?\d*", str(e.get("answer", "")))
        if not m: continue
        items.append(((e.get("body", "") + " " + e.get("question", "")).strip(), Fraction(m.group()).limit_denominator(10**6)))
    cut = int(len(items) * 0.7); return items[:cut], items[cut:]


def run() -> Dict:
    load_wk(); res = {}
    try:
        s_tr, s_te = _load_svamp()
        if SMOKE: s_tr = s_tr[:200]; s_te = s_te[:80]
        sv, _ = _solve(s_tr, s_te, 11); print("  SVAMP: acc=%.4f (prior 0.367, test=%d)" % (sv, len(s_te)), flush=True); res["svamp"] = round(sv, 4)
    except Exception as e:
        print("  SVAMP fail %s" % str(e)[:90], flush=True); res["svamp"] = None
    try:
        a_tr, a_te = _load_asdiv_1op()
        if SMOKE: a_tr = a_tr[:300]; a_te = a_te[:120]
        av, _ = _solve(a_tr, a_te, 11); print("  ASDiv-1op: acc=%.4f (prior 0.376 heuristic, test=%d)" % (av, len(a_te)), flush=True); res["asdiv_1op"] = round(av, 4)
    except Exception as e:
        print("  ASDiv fail %s" % str(e)[:90], flush=True); res["asdiv_1op"] = None
    return res


def verdict(r) -> Tuple[str, str]:
    sv = r.get("svamp"); a1 = r.get("asdiv_1op")
    if sv is None and a1 is None: return ("UNKNOWN", "UNKNOWN: load fail")
    s = "ASDiv-1op=%s (heuristic 0.376, target 0.45) | SVAMP=%s (prior 0.367). FHRR role-vector binding + template enumeration." % (a1, sv)
    if a1 is not None and a1 >= 0.45:
        return ("HARD_PASS", "HARD_PASS: FHRR vector binding disambiguates -- ASDiv-1op>=0.45; role-as-vector beats role-as-label (binding geometry adds beyond discrimination). " + s)
    if a1 is not None and a1 >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: vector binding adds modest disambiguation (0.40-0.45). " + s)
    return ("HARD_FAIL", "HARD_FAIL: binding does NOT beat role-labels (ASDiv-1op<=0.40) -- selection ambiguity is at the QUESTION-SEMANTICS level, not role/binding level. Pivot to FCG construction grammar. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
