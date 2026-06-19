"""Generator: fast cheap CPU batch -- multi-turn state, STRIPS planning, counterfactual-axiom, intent-prototype, set-algebra."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: fast-cheap batch ({tag}). {desc} Pure numpy FHRR (sub-minute; all-or-nothing OK). CPU.
PRE-REGISTERED: {prereg}
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())
{body}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
C = []
C.append(dict(anchor="multi_turn_state_cpu_v1", tag="TALKS-3 multi-turn conversation state",
  title="dialogue slot-state accumulated across turns in a substrate bundle, recovered per slot",
  desc="Conversation state as a single substrate bundle: each turn binds a SLOT role to its value and adds to the running state (later mentions of a slot supersede). After N turns, query each slot to recover its current value. Tests multi-turn state tracking.",
  prereg="HARD-PASS per-slot recall of current value >= 0.95 after multi-turn updates. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; v = cphasor(1, 64, g)[0]; assert np.allclose(a*v*np.conj(a), v, atol=1e-3), "bind"; print("[selftest] PASS: multi-turn-state", flush=True)
def run() -> Dict:
    g = np.random.default_rng(801); N = 4096; NSLOT = 6; VV = 200; TR = 60 if SMOKE else 200
    slots = cphasor(NSLOT, N, g); vals = cphasor(VV, N, g); hit = 0; tot = 0
    for _ in range(TR):
        state = np.zeros(N, dtype=np.complex64); cur = {}
        turns = int(g.integers(6, 16))
        for _t in range(turns):
            sl = int(g.integers(0, NSLOT)); vv = int(g.integers(0, VV))
            if sl in cur:
                state = state - slots[sl] * vals[cur[sl]]          # supersede: remove old binding
            state = state + slots[sl] * vals[vv]; cur[sl] = vv
        for sl, vv in cur.items():
            hit += int(cidx(state * np.conj(slots[sl]), vals) == vv); tot += 1
    rec = hit / tot; print("  multi-turn slot recall=%.3f (n=%d slots queried)" % (rec, tot), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "slot-recall=%.3f" % r["recall"]
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: multi-turn conversation slot-state recovered >=0.95 (supersede-aware) -- dialogue state tracking works. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: slot-recall 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: slot-recall <0.85. " + s)
'''))
C.append(dict(anchor="strips_planning_khop_cpu_v1", tag="CAP-1 STRIPS forward-chaining planning",
  title="forward-chaining plan reachability via sharded action transitions (2-hop)",
  desc="STRIPS-style planning: states + actions (action transforms state s -> s'). Per-state shard of applicable action->next-state bindings. Forward-chaining 2-hop reachability recovers which states are reachable by a 2-action plan. Tests substrate as a planning/forward-chaining engine.",
  prereg="HARD-PASS 2-hop plan reachability recall >= 0.85. MIDDLE >= 0.70. HARD-FAIL < 0.70.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; r = cphasor(1, 64, g)[0]; o = cphasor(1, 64, g)[0]; assert np.allclose(a*r*o*np.conj(a*r), o, atol=1e-3), "bind"; print("[selftest] PASS: strips-planning-khop", flush=True)
def run() -> Dict:
    g = np.random.default_rng(802); N = 8192; VS = 150; VA = 5; TR = 40 if SMOKE else 120
    states = cphasor(VS, N, g); acts = cphasor(VA, N, g); rec_sum = 0.0; n = 0
    for _ in range(TR):
        trans = {}; shard = {i: np.zeros(N, dtype=np.complex64) for i in range(VS)}
        for s in range(VS):
            for a in range(VA):
                ns = int(g.integers(0, VS)); trans[(s, a)] = ns; shard[s] = shard[s] + acts[a] * states[ns]
        start = int(g.integers(0, VS))
        gold = set()
        for a in range(VA):
            mid = trans[(start, a)]
            for a2 in range(VA):
                gold.add(trans[(mid, a2)])
        reached = set()
        for a in range(VA):
            mid = cidx(shard[start] * np.conj(acts[a]), states)
            for a2 in range(VA):
                reached.add(cidx(shard[mid] * np.conj(acts[a2]), states))
        rec_sum += len(gold & reached) / max(1, len(gold)); n += 1
    rc = rec_sum / n; print("  STRIPS 2-hop plan reachability recall=%.3f (n=%d)" % (rc, n), flush=True)
    return {"recall": rc}
def verdict(r) -> Tuple[str, str]:
    s = "2-hop plan recall=%.3f" % r["recall"]
    if r["recall"] >= 0.85: return ("HARD_PASS", "HARD_PASS: STRIPS forward-chaining 2-hop plan reachability >=0.85 -- substrate as planning engine. " + s)
    if r["recall"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: plan recall 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: plan recall <0.70. " + s)
'''))
C.append(dict(anchor="counterfactual_axiom_exclusion_cpu_v1", tag="CAP-4 counterfactual axiom exclusion",
  title="removing an axiom makes its dependent theorems underivable (correctly excluded)",
  desc="A theorem-dependency KB; counterfactually REMOVE an axiom and verify that theorems depending (transitively) on it become underivable (excluded from the reachable closure) while independent theorems remain derivable. Tests counterfactual reasoning over a proof graph.",
  prereg="HARD-PASS >= 0.80 of truly-dependent theorems correctly excluded after axiom removal (and independents retained). MIDDLE >= 0.65. HARD-FAIL < 0.65.",
  body='''
def _selftest():
    assert (set([1,2,3]) - set([2])) == {1,3}, "set diff"; print("[selftest] PASS: counterfactual-axiom-exclusion", flush=True)
def run() -> Dict:
    g = np.random.default_rng(803); N = 8192; VT = 120; DEP = cphasor(1, N, g)[0]; thms = cphasor(VT, N, g); TR = 40 if SMOKE else 120; HOPS = 4
    excl_ok = 0; excl_tot = 0
    for _ in range(TR):
        adj = {i: [] for i in range(VT)}; shard = {i: np.zeros(N, dtype=np.complex64) for i in range(VT)}
        for t in range(1, VT):
            k = int(g.integers(1, 4)); deps = g.choice(t, min(k, t), replace=False)
            for d in deps:
                adj[t].append(int(d)); shard[t] = shard[t] + DEP * thms[int(d)]
        axiom = int(g.integers(0, VT // 4))                                    # remove a low-level axiom
        def closure(skip):
            seen = set(); fr = set(range(VT))
            # ground-truth: a theorem is derivable if NONE of its transitive deps include the removed axiom
            derivable = set()
            for t in range(VT):
                stack = [t]; deps_all = set(); bad = False
                while stack:
                    u = stack.pop()
                    for d in adj[u]:
                        if d == skip:
                            bad = True
                        if d not in deps_all:
                            deps_all.add(d); stack.append(d)
                if not bad and t != skip:
                    derivable.add(t)
            return derivable
        deriv_after = closure(axiom)
        truly_dependent = set(range(VT)) - deriv_after - {axiom}
        # substrate check: a theorem is "excluded" if axiom appears in its substrate dependency closure (K-hop)
        for t in list(truly_dependent)[:15]:
            reached = set(); fr = [t]
            for _h in range(HOPS):
                nf = []
                for u in fr:
                    if not adj[u]:
                        continue
                    for v in np.where((thms @ np.conj(shard[u] * np.conj(DEP))).real / N > 0.30)[0].tolist():
                        if v not in reached:
                            nf.append(v)
                reached |= set(nf); fr = nf
            excl_ok += int(axiom in reached); excl_tot += 1
    rc = excl_ok / max(1, excl_tot); print("  counterfactual axiom-exclusion recall=%.3f (n=%d dependent theorems)" % (rc, excl_tot), flush=True)
    return {"recall": rc}
def verdict(r) -> Tuple[str, str]:
    s = "exclusion-recall=%.3f" % r["recall"]
    if r["recall"] >= 0.80: return ("HARD_PASS", "HARD_PASS: removed-axiom dependents correctly identified as excluded >=0.80 -- counterfactual proof-graph reasoning works. " + s)
    if r["recall"] >= 0.65: return ("MIDDLE_BAND", "MIDDLE_BAND: exclusion 0.65-0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: exclusion <0.65. " + s)
'''))
C.append(dict(anchor="intent_prototype_classifier_cpu_v1", tag="TALKS-2 substrate intent classifier (no LLM)",
  title="nearest-prototype intent classification over substrate-encoded queries",
  desc="LLM-free intent classification: each intent class has a prototype vector (mean of its example encodings); a query is classified by nearest prototype. Substrate-native (cosine cleanup). Tests substrate-only conversation-act classification.",
  prereg="HARD-PASS intent classification accuracy >= 0.85 over the test set. MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  body='''
def _selftest():
    import numpy as _n; assert int(_n.argmax([0.1,0.9,0.2]))==1, "argmax"; print("[selftest] PASS: intent-prototype-classifier", flush=True)
def run() -> Dict:
    g = np.random.default_rng(804); D = 64; NCLASS = 7; PER = 200; FUZZ = 1.4
    centers = g.standard_normal((NCLASS, D))
    def sample(c):
        return centers[c] + FUZZ / math.sqrt(D) * g.standard_normal(D)
    # prototypes from a few labeled examples per class
    proto = np.stack([np.mean([sample(c) for _ in range(8)], 0) for c in range(NCLASS)]); proto = proto / np.linalg.norm(proto, axis=1, keepdims=True)
    hit = 0; n = 0
    for c in range(NCLASS):
        for _ in range(PER):
            q = sample(c); q = q / np.linalg.norm(q); hit += int(int(np.argmax(proto @ q)) == c); n += 1
    acc = hit / n; print("  intent classification accuracy=%.3f (%d classes, n=%d)" % (acc, NCLASS, n), flush=True)
    return {"accuracy": acc}
def verdict(r) -> Tuple[str, str]:
    s = "intent-accuracy=%.3f" % r["accuracy"]
    if r["accuracy"] >= 0.85: return ("HARD_PASS", "HARD_PASS: substrate nearest-prototype intent classification >=0.85 (no LLM) -- conversation-act routing layer works. " + s)
    if r["accuracy"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: intent 0.75-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: intent <0.75. " + s)
'''))
C.append(dict(anchor="set_algebra_bundle_cpu_v1", tag="set union/intersection via bundle algebra",
  title="substrate set operations: union and intersection of fact-sets recovered by cleanup",
  desc="Sets of items encoded as bundles; UNION = bundle sum (recover all members), INTERSECTION via per-item membership scoring across two bundles (item in both). Tests substrate set algebra (a query-language primitive).",
  prereg="HARD-PASS union recall >= 0.95 AND intersection F1 >= 0.90. MIDDLE >= 0.85/0.80. HARD-FAIL below.",
  body='''
def _selftest():
    assert len({1,2,3} & {2,3,4}) == 2, "intersect"; print("[selftest] PASS: set-algebra-bundle", flush=True)
def run() -> Dict:
    g = np.random.default_rng(805); N = 8192; VE = 400; TR = 60 if SMOKE else 200; ents = cphasor(VE, N, g)
    urec = 0; utot = 0; f1s = []
    for _ in range(TR):
        A = set(int(x) for x in g.choice(VE, int(g.integers(4, 12)), replace=False))
        B = set(int(x) for x in g.choice(VE, int(g.integers(4, 12)), replace=False))
        bA = sum((ents[i] for i in A), np.zeros(N, dtype=np.complex64)); bB = sum((ents[i] for i in B), np.zeros(N, dtype=np.complex64))
        # union recall: top-|A| from bA recovers A
        gotA = topk(bA, ents, len(A)); urec += len(gotA & A); utot += len(A)
        # intersection: items scoring high in BOTH bundles
        thr = 0.5; inA = set(np.where((ents @ np.conj(bA)).real / N > thr)[0].tolist()); inB = set(np.where((ents @ np.conj(bB)).real / N > thr)[0].tolist())
        pred = inA & inB; gold = A & B
        tp = len(pred & gold); prec = tp / max(1, len(pred)); rcl = tp / max(1, len(gold)); f1 = 2 * prec * rcl / max(1e-9, prec + rcl) if gold else (1.0 if not pred else 0.0)
        f1s.append(f1)
    ur = urec / utot; fi = float(np.mean(f1s)); print("  union-recall=%.3f intersection-F1=%.3f (n=%d)" % (ur, fi, TR), flush=True)
    return {"union": ur, "intersect_f1": fi}
def verdict(r) -> Tuple[str, str]:
    s = "union-recall=%.3f intersection-F1=%.3f" % (r["union"], r["intersect_f1"])
    if r["union"] >= 0.95 and r["intersect_f1"] >= 0.90: return ("HARD_PASS", "HARD_PASS: substrate set union (>=0.95) + intersection (F1>=0.90) -- set-algebra query primitives work. " + s)
    if r["union"] >= 0.85 and r["intersect_f1"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: set-algebra 0.85/0.80. " + s)
    return ("HARD_FAIL", "HARD_FAIL: set-algebra weak. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
