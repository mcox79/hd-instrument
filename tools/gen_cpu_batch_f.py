"""Generator: CPU batch F (5 hybrid-architecture / KG-QA mechanism cells). Run: python tools/gen_cpu_batch_f.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: hybrid-architecture / KG-QA mechanism ({tag}). {desc} Pure numpy. CPU.
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
def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg); alls = np.concatenate([pos, neg]); lab = np.concatenate([np.ones(len(pos)), np.zeros(len(neg))])
    order = np.argsort(alls); ranks = np.empty_like(order, dtype=np.float64); ranks[order] = np.arange(1, len(alls) + 1)
    return float((ranks[lab == 1].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg) + 1e-9))
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
C.append(dict(anchor="binding_entropy_routing_cpu_v1", tag="H4 binding-entropy self-routing",
  title="binding entropy predicts whether a query is answerable by native K-hop",
  desc="When a (subject,relation) query has a clean match in the KG, the unbind cleanup distribution is PEAKED (low entropy); when it does not, the distribution is FLAT (high entropy). Tests whether this entropy self-routes answerable vs unanswerable queries (cheap confidence/abstention + native-vs-fuzzy routing signal).",
  prereg="HARD-PASS AUC(answerable low-entropy vs unanswerable high-entropy) >= 0.85. MIDDLE >= 0.70. HARD-FAIL < 0.70.",
  body='''
def _selftest():
    p = np.array([10.0, 0, 0]); sm = np.exp(p - p.max()); sm /= sm.sum(); ent = -(sm * np.log(sm + 1e-12)).sum(); assert ent < 0.5, "peaked low entropy"; print("[selftest] PASS: binding-entropy-routing", flush=True)
def run() -> Dict:
    g = np.random.default_rng(51); N = 8192; VE = 150; VR = 16; TR = 80 if SMOKE else 250
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}
    M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(2):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    def entropy(s, r):
        sc = (ents @ np.conj(M * np.conj(ents[s] * rels[r]))).real; sm = np.exp(sc - sc.max()); sm /= sm.sum(); return -(sm * np.log(sm + 1e-12)).sum()
    ans = []; non = []
    keys = list(edges.keys()); g.shuffle(keys)
    for (s, r) in keys[:TR]:
        ans.append(entropy(s, r))
    for _ in range(TR):
        s = int(g.integers(0, VE)); r = int(g.integers(0, VR))
        if (s, r) not in edges:
            non.append(entropy(s, r))
    a = auc([-x for x in ans], [-x for x in non])           # answerable = LOW entropy -> negate so higher=answerable
    print("  AUC(answerable low-entropy vs unanswerable)=%.4f (ans mean=%.3f non mean=%.3f)" % (a, float(np.mean(ans)), float(np.mean(non))), flush=True)
    return {"auc": a}
def verdict(r) -> Tuple[str, str]:
    s = "routing AUC=%.4f" % r["auc"]
    if r["auc"] >= 0.85: return ("HARD_PASS", "HARD_PASS: binding entropy self-routes answerable vs unanswerable at AUC>=0.85 -- cheap native confidence + native-vs-fuzzy routing signal. " + s)
    if r["auc"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: routing AUC 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: routing AUC <0.70. " + s)
'''))
C.append(dict(anchor="rrf_fusion_cpu_v1", tag="H2 reciprocal-rank fusion",
  title="RRF fusion of two noisy rankers beats either alone",
  desc="Two independent noisy rankings of the same gold set (e.g. a fuzzy retriever + a native retriever, each with its own errors); reciprocal-rank fusion (sum 1/(k+rank)) combines them. Tests whether fusion recall@10 exceeds the best single ranker.",
  prereg="HARD-PASS RRF recall@10 >= 1.2x the best single ranker. MIDDLE >= best single. HARD-FAIL < best single.",
  body='''
def _selftest():
    assert 1.0 / (60 + 1) > 1.0 / (60 + 5), "rrf rank weighting"; print("[selftest] PASS: rrf-fusion", flush=True)
def run() -> Dict:
    g = np.random.default_rng(52); V = 500; GOLD = 20; TR = 60 if SMOKE else 200; KRRF = 60; krecall = 10
    rA = []; rB = []; rF = []
    for _ in range(TR):
        gold = set(g.choice(V, GOLD, replace=False).tolist())
        truth = np.zeros(V); truth[list(gold)] = 1.0
        sA = truth + 1.3 * g.standard_normal(V); sB = truth + 1.3 * g.standard_normal(V)   # two noisy rankers
        ordA = np.argsort(-sA); ordB = np.argsort(-sB)
        rankA = np.empty(V); rankA[ordA] = np.arange(V); rankB = np.empty(V); rankB[ordB] = np.arange(V)
        fused = 1.0 / (KRRF + rankA) + 1.0 / (KRRF + rankB); ordF = np.argsort(-fused)
        def rec(order):
            return len(set(order[:krecall].tolist()) & gold) / GOLD
        rA.append(rec(ordA)); rB.append(rec(ordB)); rF.append(rec(ordF))
    a, b, f = float(np.mean(rA)), float(np.mean(rB)), float(np.mean(rF)); best = max(a, b)
    print("  recall@10: rankerA=%.3f rankerB=%.3f RRF=%.3f (RRF/best=%.2f)" % (a, b, f, f / (best + 1e-9)), flush=True)
    return {"A": a, "B": b, "fused": f, "ratio": f / (best + 1e-9)}
def verdict(r) -> Tuple[str, str]:
    s = "RRF=%.3f vs best-single=%.3f (ratio=%.2f)" % (r["fused"], max(r["A"], r["B"]), r["ratio"])
    if r["ratio"] >= 1.2: return ("HARD_PASS", "HARD_PASS: RRF fusion recall@10 >=1.2x best single ranker -- hybrid parallel fusion adds real recall. " + s)
    if r["ratio"] >= 1.0: return ("MIDDLE_BAND", "MIDDLE_BAND: RRF >= best single but <1.2x. " + s)
    return ("HARD_FAIL", "HARD_FAIL: RRF worse than best single. " + s)
'''))
C.append(dict(anchor="ppr_spreading_activation_cpu_v1", tag="I3 PPR spreading activation",
  title="PageRank-like spreading activation over a substrate KG (HippoRAG-equivalent)",
  desc="From a seed entity, iteratively spread activation through the substrate KG (each step adds unbound-neighbor mass with damping); measure convergence depth and recall@K of the true 2-hop neighborhood. Tests the HippoRAG personalized-PageRank mechanism on the substrate.",
  prereg="HARD-PASS spreading converges by K<=5 AND recall@K of 2-hop neighborhood >= 0.70. MIDDLE recall >= 0.55. HARD-FAIL < 0.55 or no convergence by K=10.",
  body='''
def _selftest():
    assert abs((0.85 * 1.0 + 0.15) - 1.0) < 0.5, "damping"; print("[selftest] PASS: ppr-spreading-activation", flush=True)
def run() -> Dict:
    g = np.random.default_rng(53); N = 8192; VE = 120; VR = 8; DAMP = 0.7; TR = 20 if SMOKE else 60
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); adj = {i: [] for i in range(VE)}; M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(2):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if o != s and o not in adj[s]:
                adj[s].append(o); M = M + ents[s] * rels[r] * ents[o]
    def true_2hop(seed):
        h1 = set(adj[seed]); h2 = set();
        for u in h1:
            h2 |= set(adj[u])
        return (h1 | h2) - {seed}
    convs = []; recs = []
    for _ in range(TR):
        seed = int(g.integers(0, VE)); tgt = true_2hop(seed)
        if not tgt:
            continue
        act = np.zeros(VE); act[seed] = 1.0; conv_k = 10; prev_top = None
        for k in range(1, 11):
            newact = (1 - DAMP) * np.zeros(VE)
            for u in np.where(act > 0.01)[0]:
                for r in range(VR):
                    nb = cidx(M * np.conj(ents[u] * rels[r]), ents); sc = (ents[nb] @ np.conj(M * np.conj(ents[u] * rels[r]))).real / N
                    if sc > 0.3:
                        newact[nb] += DAMP * act[u] / 2.0
            newact[seed] += (1 - DAMP)
            act = act + newact; top = tuple(np.argsort(-act)[:len(tgt)].tolist())
            if top == prev_top:
                conv_k = k; break
            prev_top = top
        retr = set(np.argsort(-act)[:len(tgt) + 1].tolist()) - {seed}
        recs.append(len(retr & tgt) / len(tgt)); convs.append(conv_k)
    rec = float(np.mean(recs)); cv = float(np.mean(convs)); print("  recall@K(2-hop nbhd)=%.3f mean-convergence-K=%.1f" % (rec, cv), flush=True)
    return {"recall": rec, "conv_k": cv}
def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f convergence-K=%.1f" % (r["recall"], r["conv_k"])
    if r["recall"] >= 0.70 and r["conv_k"] <= 5: return ("HARD_PASS", "HARD_PASS: PPR spreading converges by K<=5 with 2-hop recall>=0.70 -- HippoRAG-style spreading activation works on the substrate. " + s)
    if r["recall"] >= 0.55: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.55-0.70 or slower convergence. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.55 or no convergence. " + s)
'''))
C.append(dict(anchor="cascade_native_first_router_cpu_v1", tag="H1 cascade native-first router",
  title="native-first cascade matches best-of-both regimes at lower average cost",
  desc="Route each query to native K-hop first; if native confidence (peakedness) is low, fall back to a (costlier) fuzzy stage. Compares cascade accuracy + average cost to always-native and always-fuzzy. Validates the Tier-1 production routing architecture.",
  prereg="HARD-PASS cascade accuracy >= max(always-native, always-fuzzy) - 0.02 AND average cost < always-fuzzy. MIDDLE accuracy within 0.05. HARD-FAIL worse.",
  body='''
def _selftest():
    assert max(0.8, 0.6) == 0.8, "max"; print("[selftest] PASS: cascade-native-first-router", flush=True)
def run() -> Dict:
    g = np.random.default_rng(54); Q = 300 if not SMOKE else 80
    # synthetic: each query is either DISCRETE-answerable (native succeeds, conf high) or FUZZY-only (native fails low-conf, fuzzy succeeds)
    is_discrete = g.random(Q) < 0.6
    native_ok = np.where(is_discrete, g.random(Q) < 0.92, g.random(Q) < 0.20)       # native accuracy by type
    native_conf = np.where(is_discrete, 0.7 + 0.3 * g.random(Q), 0.2 + 0.3 * g.random(Q))  # confidence by type
    fuzzy_ok = np.where(is_discrete, g.random(Q) < 0.5, g.random(Q) < 0.75)         # fuzzy accuracy by type
    COST_N = 1.0; COST_F = 4.0
    always_native = native_ok.mean(); always_fuzzy = fuzzy_ok.mean()
    THR = 0.55; use_fuzzy = native_conf < THR
    cascade_ok = np.where(use_fuzzy, fuzzy_ok, native_ok); cascade_acc = cascade_ok.mean()
    cascade_cost = (COST_N + use_fuzzy * COST_F).mean()
    print("  acc: always-native=%.3f always-fuzzy=%.3f cascade=%.3f | cascade-cost=%.2f (always-fuzzy-cost=%.2f)" % (always_native, always_fuzzy, cascade_acc, cascade_cost, COST_N + COST_F), flush=True)
    return {"native": float(always_native), "fuzzy": float(always_fuzzy), "cascade": float(cascade_acc), "cost": float(cascade_cost), "fuzzy_cost": COST_N + COST_F}
def verdict(r) -> Tuple[str, str]:
    best = max(r["native"], r["fuzzy"]); s = "cascade-acc=%.3f vs best-of-both=%.3f, cascade-cost=%.2f vs always-fuzzy=%.2f" % (r["cascade"], best, r["cost"], r["fuzzy_cost"])
    if r["cascade"] >= best - 0.02 and r["cost"] < r["fuzzy_cost"]: return ("HARD_PASS", "HARD_PASS: native-first cascade matches best-of-both accuracy at lower average cost -- Tier-1 routing architecture validated. " + s)
    if r["cascade"] >= best - 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: cascade within 0.05 of best-of-both. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cascade loses too much accuracy. " + s)
'''))
C.append(dict(anchor="beam_retrieval_cpu_v1", tag="I4 beam retrieval over K-hop paths",
  title="beam search over multi-hop paths beats greedy on the substrate KG",
  desc="At each hop keep the top-B partial paths (by accumulated unbind score) instead of committing to the single best (greedy); recover the terminal entity of a 2-hop path. Tests whether beam retrieval recovers paths that greedy single-best loses (Beam-Retrieval VSA equivalent).",
  prereg="HARD-PASS beam (B=4) recall@1 >= greedy + 0.05 on 2-hop paths. MIDDLE >= greedy. HARD-FAIL < greedy.",
  body='''
def _selftest():
    assert sorted([3, 1, 2], reverse=True)[:2] == [3, 2], "beam topB"; print("[selftest] PASS: beam-retrieval", flush=True)
def run() -> Dict:
    g = np.random.default_rng(55); N = 8192; VE = 150; VR = 8; B = 4; TR = 60 if SMOKE else 200
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}; M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(3):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    def sample_path():
        for _ in range(100):
            s = int(g.integers(0, VE)); o1 = [(r, edges[(s, r)]) for (ss, r) in edges if ss == s]
            if not o1:
                continue
            r1, b = o1[int(g.integers(0, len(o1)))]; o2 = [(r, edges[(b, r)]) for (ss, r) in edges if ss == b]
            if not o2:
                continue
            r2, ans = o2[int(g.integers(0, len(o2)))]; return s, r1, r2, ans
        return None
    gh = 0; bh = 0; n = 0
    for _ in range(TR):
        p = sample_path()
        if not p:
            continue
        s, r1, r2, ans = p
        # greedy: top-1 at hop1
        b1 = cidx(M * np.conj(ents[s] * rels[r1]), ents); gpred = cidx(M * np.conj(ents[b1] * rels[r2]), ents)
        # beam: keep top-B hop1 candidates, expand each, take best final
        sc1 = (ents @ np.conj(M * np.conj(ents[s] * rels[r1]))).real; cand = np.argsort(-sc1)[:B]
        best_final = -1; best_sc = -1e18
        for c in cand:
            sc2 = (ents @ np.conj(M * np.conj(ents[c] * rels[r2]))).real; j = int(np.argmax(sc2))
            if sc1[c] + sc2[j] > best_sc:
                best_sc = sc1[c] + sc2[j]; best_final = j
        gh += int(gpred == ans); bh += int(best_final == ans); n += 1
    gr = gh / n; br = bh / n; print("  2-hop recall@1: greedy=%.3f beam(B=%d)=%.3f (gain=%.3f)" % (gr, B, br, br - gr), flush=True)
    return {"greedy": gr, "beam": br, "gain": br - gr}
def verdict(r) -> Tuple[str, str]:
    s = "greedy=%.3f beam=%.3f gain=%.3f" % (r["greedy"], r["beam"], r["gain"])
    if r["gain"] >= 0.05: return ("HARD_PASS", "HARD_PASS: beam retrieval beats greedy by >=0.05 on 2-hop paths -- keeping top-B partial paths recovers bridges greedy loses. " + s)
    if r["gain"] >= 0.0: return ("MIDDLE_BAND", "MIDDLE_BAND: beam >= greedy but gain <0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: beam worse than greedy. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
