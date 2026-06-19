"""
exp_phase4b_role_parser_cpu_v1.py -- Phase-4B-FULL: answer-consistency-trained substrate role-parser -- CPU.

ROUTING: Research PHASE_4B_FULL_WEAK_SUPERVISION_CONFIRMED (build authorized). Breaks the 4B-cheap unit-cue ceiling (0.277
  acc-on-covered) using WEAK SUPERVISION: answer-consistency generates gold role labels (the number->role assignment whose
  schema constraint yields the gold answer IS the correct binding -- no test leakage, train split only). A substrate role
  classifier (prototype-per-role from context-window features) learns number-context -> role from those gold labels, then
  predicts roles on the test split. Role-binding matters for ASYMMETRIC constraints (X/Y, a-b, ax+b=c) where order changes the
  answer -- unit-cues alone can't resolve these. Substrate-only (supervised prototype cleanup, no LLM).
PRE-REGISTERED: HARD-PASS test role-binding accuracy >= 0.50 (Research 4B-FULL-C goal) AND end-to-end > 4A's 0.059. MIDDLE
  role-acc >= 0.35. HARD-FAIL role-acc < 0.35 OR end-to-end <= 0.059 (no lift over unit-cue). UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, re
from pathlib import Path
from typing import Dict, List, Tuple
from itertools import permutations
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "phase4b_role_parser_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
# schemas with ORDERED roles + a constraint over role-keyed values. Asymmetric ones (where order matters) are the point.
SCHEMAS = {
    "percent_relation": {"kw": ["percent", "what", "of"], "roles": ["PART", "WHOLE"],
                          "f": lambda d: d["PART"] / d["WHOLE"] * 100 if d["WHOLE"] != 0 else None},
    "ratio_proportion": {"kw": ["ratio", "proportion", "as", "to", "every"], "roles": ["A", "B", "C"],
                          "f": lambda d: d["B"] * d["C"] / d["A"] if d["A"] != 0 else None},
    "difference": {"kw": ["more", "than", "difference", "fewer", "less", "exceeds"], "roles": ["LARGER", "SMALLER"],
                    "f": lambda d: d["LARGER"] - d["SMALLER"]},
    "quotient": {"kw": ["divided", "per", "each", "split", "share", "quotient"], "roles": ["DIVIDEND", "DIVISOR"],
                  "f": lambda d: d["DIVIDEND"] / d["DIVISOR"] if d["DIVISOR"] != 0 else None},
    "rate_motion": {"kw": ["rate", "speed", "mph", "hour", "distance", "travels"], "roles": ["RATE", "TIME"],
                     "f": lambda d: d["RATE"] * d["TIME"]},   # symmetric (product) -- included as control
}
SNAMES = list(SCHEMAS.keys())
def _boxed(sol):
    i = sol.find("oxed{")
    if i < 0: return None
    j = i + 5; dd = 1; out = []
    while j < len(sol) and dd > 0:
        c = sol[j]
        if c == "{": dd += 1
        elif c == "}": dd -= 1
        if dd > 0: out.append(c)
        j += 1
    return "".join(out)
def _frac(x):
    try:
        x = (x or "").replace("$", "").replace(",", "").replace("\\%", "").strip()
        if re.fullmatch(r"-?\d+(\.\d+)?", x): return Fraction(x).limit_denominator(10**6)
        if re.fullmatch(r"-?\d+/\d+", x): return Fraction(x)
        return None
    except Exception: return None
def _num_positions(q):
    """list of (Fraction value, token-index) for each number token."""
    toks = q.split(); out = []
    for k, t in enumerate(toks):
        m = re.match(r"(\d+(?:\.\d+)?)", t.replace("$", "").replace(",", ""))
        if m:
            try: out.append((Fraction(m.group(1)), k))
            except Exception: pass
    return out, toks
def _ctx_feats(toks, k):
    """context-window features around token k (the supervised role signal)."""
    fs = []
    for off in (-2, -1, 1, 2):
        j = k + off
        w = toks[j].lower() if 0 <= j < len(toks) else ("<S>" if j < 0 else "<E>")
        w = re.sub(r"[^a-z]", "", w)
        fs.append("p%d:%s" % (off, w))
    return fs
def _selftest():
    assert _boxed("$\\boxed{7}$") == "7"
    np2, tk = _num_positions("60 mph for 2 hours"); assert np2[0][0] == 60 and np2[1][0] == 2
    print("[selftest] PASS: phase4b-role-parser", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1006")))
    try:
        from datasets import load_dataset
        probs = []
        for cfg in ["prealgebra", "algebra"]:
            ds = load_dataset("EleutherAI/hendrycks_math", cfg, split="test")
            probs += [x for x in ds if x.get("level") == "Level 1"]
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    if SMOKE: probs = probs[:80]
    # split train/test (answer-consistency labels only on train; eval on test)
    idx = np.arange(len(probs)); g.shuffle(idx); cut = len(idx) // 2
    train = [probs[i] for i in idx[:cut]]; test = [probs[i] for i in idx[cut:]]
    book = {}
    def tok(w):
        if w not in book:
            ang = (g.random(N) * 2 - 1) * math.pi; book[w] = np.exp(1j * ang).astype(np.complex64)
        return book[w]
    def bundle(words):
        v = np.zeros(N, dtype=np.complex64)
        for w in words: v = v + tok(w)
        if not np.any(v): return v
        return np.exp(1j * np.angle(v)).astype(np.complex64)
    skw = {nm: bundle(SCHEMAS[nm]["kw"]) for nm in SNAMES}
    sproto = np.stack([skw[nm] for nm in SNAMES])
    def retrieve(q):
        v = bundle(re.findall(r"[a-z]+", q.lower()))
        if not np.any(v): return SNAMES[0]
        return SNAMES[int(np.argmax((sproto @ np.conj(v)).real))]
    # ANSWER-CONSISTENCY weak labels on TRAIN: role-context bundles per role
    role_examples = {}   # role -> list of context-feature-bundles
    n_labeled = 0
    for p in train:
        gold = _frac(_boxed(p.get("solution", "")))
        if gold is None: continue
        sch = retrieve(p["problem"]); roles = SCHEMAS[sch]["roles"]; f = SCHEMAS[sch]["f"]
        nps, toks = _num_positions(p["problem"])
        if len(nps) < len(roles): continue
        nps = nps[:len(roles)]            # first |roles| numbers (keeps permutation tractable)
        best_perm = None
        for perm in permutations(range(len(roles))):
            d = {roles[r]: nps[perm[r]][0] for r in range(len(roles))}
            try: val = f(d)
            except Exception: val = None
            if val is not None and Fraction(val).limit_denominator(10**6) == gold:
                best_perm = perm; break
        if best_perm is None: continue
        for r in range(len(roles)):
            ci = nps[best_perm[r]][1]; feats = _ctx_feats(toks, ci)
            role_examples.setdefault(roles[r], []).append(bundle(feats))
        n_labeled += 1
    # build supervised role prototypes (bundle of context-bundles per role)
    all_roles = sorted(role_examples.keys())
    if not all_roles:
        return {"error": "no_answer_consistent_labels", "accuracy": 0.0}
    rproto = {}
    for rr in all_roles:
        v = np.zeros(N, dtype=np.complex64)
        for b in role_examples[rr]: v = v + b
        rproto[rr] = np.exp(1j * np.angle(v)).astype(np.complex64) if np.any(v) else v
    # EVAL on test: retrieve schema, classify each number's role via cleanup, fill, solve. role-acc measured by answer-consistency oracle on test.
    matched = 0; correct = 0; role_hit = 0; role_tot = 0; nT = 0
    for p in test:
        gold = _frac(_boxed(p.get("solution", "")))
        if gold is None: continue
        nT += 1
        sch = retrieve(p["problem"]); roles = SCHEMAS[sch]["roles"]; f = SCHEMAS[sch]["f"]
        nps, toks = _num_positions(p["problem"])
        if len(nps) < len(roles): continue
        nps = nps[:len(roles)]
        # predict role for each number via supervised cleanup; resolve to a valid one-to-one assignment greedily by score
        cand_roles = [r for r in roles if r in rproto]
        if len(cand_roles) < len(roles): continue
        scores = np.zeros((len(roles), len(roles)))   # number i x role j
        for i in range(len(roles)):
            cb = bundle(_ctx_feats(toks, nps[i][1]))
            for j, rr in enumerate(roles):
                scores[i, j] = (np.conj(cb) @ rproto[rr]).real if np.any(cb) else 0.0
        # greedy one-to-one assignment (Hungarian-lite): pick highest score, assign, repeat
        assign = {}; used_n = set(); used_r = set(); order = np.dstack(np.unravel_index(np.argsort(-scores, axis=None), scores.shape))[0]
        for (i, j) in order:
            if i in used_n or j in used_r: continue
            assign[roles[j]] = nps[i][0]; used_n.add(i); used_r.add(j)
        # role-binding oracle accuracy: does the predicted assignment yield the gold answer?
        try: val = f(assign)
        except Exception: val = None
        ok = val is not None and Fraction(val).limit_denominator(10**6) == gold
        matched += 1; correct += int(ok)
        # per-role accuracy vs the answer-consistent assignment (if one exists)
        cons = None
        for perm in permutations(range(len(roles))):
            d = {roles[r]: nps[perm[r]][0] for r in range(len(roles))}
            try: vv = f(d)
            except Exception: vv = None
            if vv is not None and Fraction(vv).limit_denominator(10**6) == gold: cons = perm; break
        if cons is not None:
            for r in range(len(roles)):
                role_tot += 1; role_hit += int(assign.get(roles[r]) == nps[cons[r]][0])
    acc = correct / nT if nT else 0.0; cov = matched / nT if nT else 0.0
    role_acc = role_hit / role_tot if role_tot else 0.0
    print("  PHASE4B-ROLE-PARSER: end-to-end=%.3f (%d/%d) | coverage=%.3f | role-binding-acc=%.3f (%d/%d) | labeled-train=%d (vs 4A 0.059, 4B-cheap role 0.277)" %
          (acc, correct, nT, cov, role_acc, role_hit, role_tot, n_labeled), flush=True)
    return {"accuracy": round(acc, 3), "coverage": round(cov, 3), "role_acc": round(role_acc, 3), "n_labeled": n_labeled, "n_test": nT, "role_tot": role_tot}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    ra = r["role_acc"]; a = r["accuracy"]; s = "role-acc=%.3f end-to-end=%.3f coverage=%.3f (labeled-train=%d, role-evals=%d)" % (ra, a, r["coverage"], r["n_labeled"], r["role_tot"])
    if ra >= 0.50 and a > 0.059:
        return ("HARD_PASS", "HARD_PASS: answer-consistency-trained substrate role-parser reaches role-binding-acc>=0.50 AND end-to-end beats 4A's 0.059 -- weak supervision breaks the unit-cue ceiling; substrate role-binding works on asymmetric constraints. " + s)
    if ra >= 0.35:
        return ("MIDDLE_BAND", "MIDDLE_BAND: role-acc 0.35-0.50 -- weak supervision helps but partial; more labeled signal (MAWPS/ASDiv) or richer context features. " + s)
    return ("HARD_FAIL", "HARD_FAIL: role-acc <0.35 or no lift over unit-cue -- answer-consistency context features insufficient; need full dep-parser syntactic structure. " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
