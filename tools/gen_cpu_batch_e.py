"""Generator: CPU batch E (5 pure-numpy substrate capability cells). Run: python tools/gen_cpu_batch_e.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: CPU substrate capability characterization ({tag}). {desc} Pure numpy. CPU.
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
C.append(dict(anchor="analogy_relation_transfer_cpu_v1", tag="few-shot relation learning",
  title="estimate a relation from K example pairs and apply it to a new input (analogy)",
  desc="A fixed relation T binds a->b (b = a*T + noise). Estimate T_hat from K noisy example pairs (averaging), then apply to a new c to predict d = c*T. Measures fidelity (cosine to true) vs number of examples -- few-shot relational generalization.",
  prereg="HARD-PASS cosine(d_hat, d_true) >= 0.90 at K=5 examples. MIDDLE >= 0.80. HARD-FAIL < 0.80.",
  body='''
def _selftest():
    a = cphasor(1, 16, np.random.default_rng(0))[0]; assert abs(abs(np.vdot(a, a)) - 16) < 1e-3, "phasor norm"; print("[selftest] PASS: analogy-relation-transfer-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(41); N = 2048; TR = 60 if SMOKE else 200; NOISE = 1.0; by = {}
    for K in [1, 3, 5, 10]:
        coss = []
        for _ in range(TR):
            T = cphasor(1, N, g)[0]; a = cphasor(K, N, g)
            noise = (g.standard_normal((K, N)) + 1j * g.standard_normal((K, N))).astype(np.complex64) * (NOISE / math.sqrt(2))
            b = a * T + noise; T_hat = (b * a.conj()).mean(0)
            c = cphasor(1, N, g)[0]; d_hat = c * T_hat; d_true = c * T
            coss.append(abs(np.vdot(d_hat, d_true)) / (np.linalg.norm(d_hat) * np.linalg.norm(d_true) + 1e-9))
        by["K%d" % K] = float(np.mean(coss)); print("  K=%d cosine(d_hat,d_true)=%.3f" % (K, by["K%d" % K]), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    k5 = r["by"].get("K5", 0.0); s = "cosine by #examples: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if k5 >= 0.90: return ("HARD_PASS", "HARD_PASS: a relation learned from 5 example pairs transfers to a new input at cosine>=0.90 -- few-shot relational generalization. " + s)
    if k5 >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: K=5 transfer cosine 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: K=5 transfer cosine <0.80. " + s)
'''))
C.append(dict(anchor="multi_relation_kg_cpu_v1", tag="knowledge-graph triple queries",
  title="store (subject,relation,object) triples; query (s,r)->o and (r,o)->s",
  desc="Bundle KG triples as M = sum s*r*o. Recover the object via M*(s*r).conj() + cleanup over entities, and the subject via M*(r*o).conj(). Tests bidirectional relational query over a bundled knowledge graph.",
  prereg="HARD-PASS both (s,r)->o and (r,o)->s recall >= 0.90 at T triples. MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 16, g)[0]; b = cphasor(1, 16, g)[0]; c = cphasor(1, 16, g)[0]
    assert np.argmax((np.stack([c]) @ ((a * b * c) * (a * b).conj()).conj().reshape(-1, 1)).real) == 0, "unbind"; print("[selftest] PASS: multi-relation-kg-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(42); N = 2048; VE = 150; VR = 12; T = 30 if SMOKE else 60
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
    triples = [(int(g.integers(0, VE)), int(g.integers(0, VR)), int(g.integers(0, VE))) for _ in range(T)]
    M = np.zeros(N, dtype=np.complex64)
    for s, r, o in triples:
        M = M + ents[s] * rels[r] * ents[o]
    o_hit = s_hit = 0
    for s, r, o in triples:
        po = int(np.argmax((ents @ (M * (ents[s] * rels[r]).conj()).conj()).real)); o_hit += int(po == o)
        ps = int(np.argmax((ents @ (M * (rels[r] * ents[o]).conj()).conj()).real)); s_hit += int(ps == s)
    so = o_hit / T; ss = s_hit / T; print("  (s,r)->o recall=%.3f (r,o)->s recall=%.3f (T=%d triples)" % (so, ss, T), flush=True)
    return {"sro": so, "ros": ss}
def verdict(r) -> Tuple[str, str]:
    m = min(r["sro"], r["ros"]); s = "(s,r)->o=%.3f (r,o)->s=%.3f" % (r["sro"], r["ros"])
    if m >= 0.90: return ("HARD_PASS", "HARD_PASS: bidirectional KG triple recall >=0.90 -- a bundled knowledge graph is queryable both ways. " + s)
    if m >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: KG recall 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: KG recall <0.75. " + s)
'''))
C.append(dict(anchor="markov_transition_cpu_v1", tag="sequence next-item prediction",
  title="store transitions and predict the next item from the current (Markov)",
  desc="Store sequence transitions cur->next as M = sum cur*NEXT*next (NEXT a fixed relation). Given a current item, predict the next via M*(cur*NEXT).conj() + cleanup. Tests learned sequence/transition modeling.",
  prereg="HARD-PASS next-item recall >= 0.90 at T transitions. MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  body='''
def _selftest():
    assert np.argmax([0.1, 0.8]) == 1, "argmax"; print("[selftest] PASS: markov-transition-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(43); N = 2048; V = 150; T = 30 if SMOKE else 60
    items = cphasor(V, N, g); NEXT = cphasor(1, N, g)[0]
    trans = []
    used = set()
    while len(trans) < T:
        c = int(g.integers(0, V))
        if c in used:
            continue
        used.add(c); trans.append((c, int(g.integers(0, V))))
    M = np.zeros(N, dtype=np.complex64)
    for c, nx in trans:
        M = M + items[c] * NEXT * items[nx]
    hit = 0
    for c, nx in trans:
        pred = int(np.argmax((items @ (M * (items[c] * NEXT).conj()).conj()).real)); hit += int(pred == nx)
    rec = hit / T; print("  next-item recall=%.3f (T=%d transitions, V=%d)" % (rec, T, V), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "next-item recall=%.3f" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: next-item prediction recall>=0.90 -- substrate models learned sequence transitions (Markov). " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: next-item recall 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: next-item recall <0.75. " + s)
'''))
C.append(dict(anchor="negation_query_cpu_v1", tag="A-but-not-B retrieval",
  title="negation query (A minus B) suppresses the unwanted cluster",
  desc="Items in two clusters near anchors A and B. Compare retrieving by A alone vs by A - lambda*B: the negation should drive B-cluster contamination out of the top-k while keeping A-items. Tests compositional negation in retrieval.",
  prereg="HARD-PASS B-contamination in top-20 drops below 0.05 with negation (and was higher without). MIDDLE < 0.15. HARD-FAIL >= 0.15.",
  body='''
def _selftest():
    assert (np.array([0.9, 0.1]) - 0.5 * np.array([0.0, 0.9]))[0] > 0, "negation arithmetic"; print("[selftest] PASS: negation-query-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(44); N = 1024; D = N; NA = 10; NB = 60; NN = 150; sig = 0.8; RHO = 0.6
    A = np.sign(g.standard_normal(D)).astype(np.float32)
    B = np.sign(RHO * A + math.sqrt(1 - RHO * RHO) * g.standard_normal(D)).astype(np.float32)   # B correlated with A so clusters overlap
    def near(anchor, n):
        X = np.repeat(anchor[None, :], n, 0).copy(); fl = g.random((n, D)) < sig * 0.25; X[fl] *= -1; return X
    Aitems = near(A, NA); Bitems = near(B, NB); Neut = np.sign(g.standard_normal((NN, D))).astype(np.float32)
    X = np.vstack([Aitems, Bitems, Neut]); isB = np.zeros(len(X), bool); isB[NA:NA + NB] = True
    def topk_Bfrac(query, k=20):
        sc = X @ query; top = np.argsort(-sc)[:k]; return float(isB[top].mean())
    plain = topk_Bfrac(A); neg = topk_Bfrac(A - 1.0 * B)
    print("  B-contamination in top-20: plain-A=%.3f  A-minus-B=%.3f" % (plain, neg), flush=True)
    return {"plain": plain, "neg": neg}
def verdict(r) -> Tuple[str, str]:
    s = "B-contamination top-20: plain=%.3f negated=%.3f" % (r["plain"], r["neg"])
    if r["neg"] < 0.05 and r["neg"] < r["plain"]: return ("HARD_PASS", "HARD_PASS: negation (A-B) drives B-cluster contamination below 0.05 -- compositional 'A but not B' retrieval works. " + s)
    if r["neg"] < 0.15: return ("MIDDLE_BAND", "MIDDLE_BAND: negated contamination 0.05-0.15. " + s)
    return ("HARD_FAIL", "HARD_FAIL: negation does not suppress B (>=0.15). " + s)
'''))
C.append(dict(anchor="nesting_depth_cpu_v1", tag="nested-structure depth limit",
  title="recall vs binding nesting depth (how deep can structures go)",
  desc="Build nested bindings of depth d (role_1*(role_2*(...*payload))) and unbind d levels + cleanup; sweep d to find where accumulated noise breaks recall. Maps the depth limit for nested data structures.",
  prereg="HARD-PASS payload recall >= 0.90 at depth 8 (N=2048, V=200). MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 16, g)[0]; b = cphasor(1, 16, g)[0]; assert np.allclose(a * b * b.conj(), a, atol=1e-3), "unbind"; print("[selftest] PASS: nesting-depth-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(45); N = 2048; V = 200; TR = 40 if SMOKE else 150; book = cphasor(V, N, g); by = {}
    Ds = [4, 8] if SMOKE else [2, 4, 8, 12, 16]
    for depth in Ds:
        hit = 0
        for _ in range(TR):
            roles = cphasor(depth, N, g); fi = int(g.integers(0, V)); x = book[fi]
            for k in range(depth):
                x = roles[k] * x                      # nest
            for k in range(depth - 1, -1, -1):
                x = x * roles[k].conj()               # unnest
            hit += int(np.argmax((book @ x.conj()).real) == fi)
        by["d%d" % depth] = hit / TR; print("  depth=%d payload-recall=%.3f" % (depth, by["d%d" % depth]), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    d8 = r["by"].get("d8", 0.0); s = "recall by depth: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if d8 >= 0.90: return ("HARD_PASS", "HARD_PASS: nested-structure payload recall>=0.90 at depth 8 -- deep nested data structures are representable. " + s)
    if d8 >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: depth-8 recall 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: depth-8 recall <0.75. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
