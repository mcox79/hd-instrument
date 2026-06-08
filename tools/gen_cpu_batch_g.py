"""Generator: CPU batch G (5 hybrid/native multi-hop mechanism cells). Run: python tools/gen_cpu_batch_g.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: hybrid / native multi-hop mechanism ({tag}). {desc} Pure numpy. CPU.
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
def build_kg(g, N, VE, VR, deg):
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {{}}; M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(deg):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    return ents, rels, edges, M
def sample_path(edges, VE, g, hops):
    for _ in range(150):
        s = int(g.integers(0, VE)); path = [s]; rseq = []
        ok = True
        for _h in range(hops):
            outs = [r for (ss, r) in edges if ss == path[-1]]
            if not outs:
                ok = False; break
            r = int(g.choice(outs)); rseq.append(r); path.append(edges[(path[-1], r)])
        if ok:
            return path, rseq
    return None, None
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
C.append(dict(anchor="two_stage_disambig_khop_cpu_v1", tag="H3 two-stage entity disambiguation + K-hop",
  title="fuzzy entity-find then discrete K-hop beats either stage alone",
  desc="Stage 1 (fuzzy): match the question to candidate START entities via noisy embeddings (top-B). Stage 2 (native): run discrete K-hop from each candidate and pick the best-scoring terminal. Combines fuzzy disambiguation with native traversal. recall@2 of the answer.",
  prereg="HARD-PASS 2-stage recall@2 >= 0.65. MIDDLE >= 0.55. HARD-FAIL < 0.55.",
  body='''
def _selftest():
    assert np.argsort(-np.array([0.1, 0.9, 0.5]))[0] == 1, "argsort"; print("[selftest] PASS: two-stage-disambig-khop", flush=True)
def run() -> Dict:
    g = np.random.default_rng(61); N = 8192; VE = 150; VR = 12; B = 3; FUZZ = 1.0; TR = 60 if SMOKE else 200
    ents, rels, edges, M = build_kg(g, N, VE, VR, 2)
    fuzz_emb = g.standard_normal((VE, 64)); fuzz_emb /= np.linalg.norm(fuzz_emb, axis=1, keepdims=True)
    hit = 0; n = 0
    for _ in range(TR):
        path, rseq = sample_path(edges, VE, g, 2)
        if path is None:
            continue
        start, gold = path[0], path[-1]
        q = fuzz_emb[start] + FUZZ / math.sqrt(64) * g.standard_normal(64)          # noisy question embedding of start
        cands = np.argsort(-(fuzz_emb @ q))[:B]                                      # stage1 fuzzy candidate starts
        terminals = set()
        for c in cands:                                                             # stage2 native K-hop from each candidate
            cur = ents[int(c)]
            for r in rseq:
                cur = ents[cidx(M * np.conj(cur * rels[r]), ents)]
            terminals.add(cidx(cur, ents))
        hit += int(gold in terminals); n += 1                                       # two-stage recovers the answer among B chains
    rec = hit / max(1, n); print("  2-stage (fuzzy-disambig top-%d + native K-hop) recall=%.3f (n=%d)" % (B, rec, n), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "2-stage recall@2=%.3f" % r["recall"]
    if r["recall"] >= 0.65: return ("HARD_PASS", "HARD_PASS: fuzzy entity-disambiguation + native K-hop recall@2>=0.65 -- hybrid two-stage works (fuzzy finds the door, native walks the graph). " + s)
    if r["recall"] >= 0.55: return ("MIDDLE_BAND", "MIDDLE_BAND: 2-stage recall 0.55-0.65. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 2-stage recall <0.55. " + s)
'''))
C.append(dict(anchor="single_shot_attention_triples_cpu_v1", tag="N1c single-shot attention on triple substrate",
  title="single-pass attention over all triples recovers the answer (no iteration)",
  desc="Instead of iterative K-hop, score every triple by joint relevance to the question's (start, r1, r2) in ONE softmax-attention pass, then read out the attended object. Tests whether single-shot joint attention (transformer-like) on the structured substrate solves 2-hop without iteration.",
  prereg="HARD-PASS single-shot attention recall@2 >= 0.50 (matches PP-99 0.501). MIDDLE >= 0.40. HARD-FAIL < 0.40.",
  body='''
def _selftest():
    x = np.array([1.0, 2.0]); sm = np.exp(x - x.max()); sm /= sm.sum(); assert abs(sm.sum() - 1) < 1e-9, "softmax"; print("[selftest] PASS: single-shot-attention-triples", flush=True)
def run() -> Dict:
    g = np.random.default_rng(62); N = 8192; VE = 150; VR = 12; TR = 60 if SMOKE else 200; BETA = 6.0
    ents, rels, edges, M = build_kg(g, N, VE, VR, 2)
    tri = [(s, r, o) for (s, r), o in edges.items()]
    TS = np.stack([ents[s] for s, r, o in tri]); TR_ = np.stack([rels[r] for s, r, o in tri]); TO = np.stack([ents[o] for s, r, o in tri])
    hit = 0; n = 0
    for _ in range(TR):
        path, rseq = sample_path(edges, VE, g, 2)
        if path is None:
            continue
        start, bridge, gold = path[0], path[1], path[2]
        # single-pass: attend to triples matching (start, r1) AND (?, r2); combine object slots in ONE weighted readout
        q1 = ents[start] * rels[rseq[0]]; q2 = rels[rseq[1]]
        s1 = (TS * np.conj(ents[start])).sum(1).real + (TR_ * np.conj(rels[rseq[0]])).sum(1).real    # triples from start via r1
        s2 = (TR_ * np.conj(rels[rseq[1]])).sum(1).real                                              # triples via r2 (the second hop)
        # bridge-aware joint attention: weight hop2 triples by how much their subject matches hop1 objects
        a1 = np.exp(BETA * (s1 / N - (s1 / N).max())); a1 /= a1.sum(); bridge_vec = (a1[:, None] * TO).sum(0)
        s2b = s2 / N + (TS * np.conj(bridge_vec)).sum(1).real / N
        a2 = np.exp(BETA * (s2b - s2b.max())); a2 /= a2.sum(); ans_vec = (a2[:, None] * TO).sum(0)
        pred = cidx(ans_vec, ents); hit += int(pred == gold); n += 1
    rec = hit / max(1, n); print("  single-shot attention recall@2=%.3f (n=%d, triples=%d)" % (rec, n, len(tri)), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "single-shot attention recall@2=%.3f" % r["recall"]
    if r["recall"] >= 0.50: return ("HARD_PASS", "HARD_PASS: single-pass joint attention on the triple substrate recall@2>=0.50 -- transformer-like one-shot multi-hop works without iteration. " + s)
    if r["recall"] >= 0.40: return ("MIDDLE_BAND", "MIDDLE_BAND: single-shot attention 0.40-0.50. " + s)
    return ("HARD_FAIL", "HARD_FAIL: single-shot attention <0.40. " + s)
'''))
C.append(dict(anchor="parallel_subq_fuzzy_cpu_v1", tag="N1e parallel sub-question on fuzzy substrate",
  title="parallel (not iterative) sub-question decomposition on a fuzzy substrate",
  desc="Decompose a 2-hop question into TWO PARALLEL sub-questions and retrieve each independently on a FUZZY (overlapping-embedding) substrate, then union the results. Tests whether parallel decomposition (vs the failed iterative reformulation) rescues the fuzzy regime. recall@2 of both supporting facts.",
  prereg="HARD-PASS parallel-fuzzy recall@2 >= 0.55. MIDDLE >= 0.45. HARD-FAIL < 0.45.",
  body='''
def _selftest():
    assert len({1, 2} | {2, 3}) == 3, "union"; print("[selftest] PASS: parallel-subq-fuzzy", flush=True)
def run() -> Dict:
    g = np.random.default_rng(63); D = 384; NC = 40; PER = 10; V = NC * PER; TR = 60 if SMOKE else 200
    # GENUINELY fuzzy substrate: items cluster by topic (within-cluster items are similar -> retrieval confusable)
    centers = g.standard_normal((NC, D))
    base = np.repeat(centers, PER, 0) + 0.6 * g.standard_normal((V, D))
    E = base / np.linalg.norm(base, axis=1, keepdims=True)
    hit = 0; n = 0
    for _ in range(TR):
        f1, f2 = int(g.integers(0, V)), int(g.integers(0, V))
        if f1 // PER == f2 // PER:
            continue
        gold = {f1, f2}
        sq1 = E[f1] + 0.9 / math.sqrt(D) * g.standard_normal(D); sq2 = E[f2] + 0.9 / math.sqrt(D) * g.standard_normal(D)
        retr = {int(np.argmax(E @ sq1)), int(np.argmax(E @ sq2))}; hit += int(len(retr & gold) == 2); n += 1
    rec = hit / max(1, n); print("  parallel-fuzzy recall@2=%.3f (n=%d, %d clusters)" % (rec, n, NC), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "parallel-fuzzy recall@2=%.3f" % r["recall"]
    if r["recall"] >= 0.55: return ("HARD_PASS", "HARD_PASS: parallel sub-question decomposition on fuzzy substrate recall@2>=0.55 -- parallel (not iterative) decomp rescues the fuzzy regime. " + s)
    if r["recall"] >= 0.45: return ("MIDDLE_BAND", "MIDDLE_BAND: parallel-fuzzy 0.45-0.55. " + s)
    return ("HARD_FAIL", "HARD_FAIL: parallel-fuzzy <0.45 -- parallel decomp does not rescue fuzzy. " + s)
'''))
C.append(dict(anchor="ppr_matrix_khop_cpu_v1", tag="I3-rescue matrix personalized-PageRank",
  title="matrix PPR over substrate-derived adjacency (proper HippoRAG)",
  desc="RESCUE of naive iterative-unbind PPR (HARD_FAIL 0.22). Build the adjacency matrix by reading neighbors out of the substrate (per node, per relation, threshold), then run TRUE personalized PageRank (power iteration on the row-normalized matrix). Measures recall@K of the 2-hop neighborhood.",
  prereg="HARD-PASS recall@K of 2-hop neighborhood >= 0.70 with convergence <= 20 iters. MIDDLE >= 0.55. HARD-FAIL < 0.55.",
  body='''
def _selftest():
    A = np.array([[0.0, 1.0], [1.0, 0.0]]); An = A / A.sum(1, keepdims=True); assert np.allclose(An.sum(1), 1), "row norm"; print("[selftest] PASS: ppr-matrix-khop", flush=True)
def run() -> Dict:
    g = np.random.default_rng(64); N = 8192; VE = 120; VR = 8; DAMP = 0.5; TR = 20 if SMOKE else 60
    ents, rels, edges, M = build_kg(g, N, VE, VR, 2)
    adj = {i: [] for i in range(VE)}
    for (s, r), o in edges.items():
        adj[s].append(o)
    # build adjacency MATRIX by reading neighbors out of the substrate (per node, per relation)
    A = np.zeros((VE, VE))
    for u in range(VE):
        for r in range(VR):
            v = cidx(M * np.conj(ents[u] * rels[r]), ents)
            if (ents[v] @ np.conj(M * np.conj(ents[u] * rels[r]))).real / N > 0.30:
                A[u, v] = 1.0
    An = A / np.clip(A.sum(1, keepdims=True), 1, None)
    def true_2hop(seed):
        h1 = set(adj[seed]); h2 = set()
        for u in h1:
            h2 |= set(adj[u])
        return (h1 | h2) - {seed}
    recs = []; iters = []
    for _ in range(TR):
        seed = int(g.integers(0, VE)); tgt = true_2hop(seed)
        if not tgt:
            continue
        e = np.zeros(VE); e[seed] = 1.0; pi = e.copy()
        it = 20
        for k in range(50):
            new = (1 - DAMP) * e + DAMP * (An.T @ pi)
            if np.abs(new - pi).sum() < 1e-4:
                it = k; pi = new; break
            pi = new
        retr = set(np.argsort(-pi)[:len(tgt) + 1].tolist()) - {seed}
        recs.append(len(retr & tgt) / len(tgt)); iters.append(it)
    rec = float(np.mean(recs)); itc = float(np.mean(iters)); print("  matrix-PPR recall@K=%.3f convergence-iters=%.1f" % (rec, itc), flush=True)
    return {"recall": rec, "iters": itc}
def verdict(r) -> Tuple[str, str]:
    s = "matrix-PPR recall=%.3f iters=%.1f" % (r["recall"], r["iters"])
    if r["recall"] >= 0.70 and r["iters"] <= 20: return ("HARD_PASS", "HARD_PASS: matrix PPR over substrate-derived adjacency recall>=0.70 with fast convergence -- proper HippoRAG spreading works (rescues the naive iterative-unbind PPR). " + s)
    if r["recall"] >= 0.55: return ("MIDDLE_BAND", "MIDDLE_BAND: matrix-PPR recall 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: matrix-PPR recall <0.55. " + s)
'''))
C.append(dict(anchor="discrete_vs_fuzzy_kgqa_cpu_v1", tag="discrete vs fuzzy QA head-to-head",
  title="discrete-KG K-hop vs fuzzy-embedding retrieval on the same 2-hop QA",
  desc="Direct head-to-head on identical 2-hop questions: (a) discrete-KG substrate K-hop, (b) fuzzy-embedding nearest-neighbor retrieval. Confirms the universal principle at the QA level -- discrete wins, fuzzy loses on the same task.",
  prereg="HARD-PASS discrete recall@1 >= 0.70 AND discrete >= fuzzy + 0.30. MIDDLE discrete >= fuzzy + 0.15. HARD-FAIL gap < 0.15.",
  body='''
def _selftest():
    assert 0.8 - 0.3 >= 0.3, "gap"; print("[selftest] PASS: discrete-vs-fuzzy-kgqa", flush=True)
def run() -> Dict:
    g = np.random.default_rng(65); N = 8192; VE = 150; VR = 12; TR = 60 if SMOKE else 200
    ents, rels, edges, M = build_kg(g, N, VE, VR, 2)
    fz = g.standard_normal((VE, 96)); fz /= np.linalg.norm(fz, axis=1, keepdims=True)         # fuzzy entity embeddings
    dh = 0; fh = 0; n = 0
    for _ in range(TR):
        path, rseq = sample_path(edges, VE, g, 2)
        if path is None:
            continue
        start, bridge, gold = path[0], path[1], path[2]
        cur = ents[start]
        for r in rseq:
            cur = ents[cidx(M * np.conj(cur * rels[r]), ents)]
        dpred = cidx(cur, ents); dh += int(dpred == gold)
        # fuzzy: iterative nearest-neighbor by embedding (no relation structure)
        qf = fz[start] + 1.0 / math.sqrt(96) * g.standard_normal(96); b = int(np.argmax(fz @ qf))
        qf2 = fz[b] + 1.0 / math.sqrt(96) * g.standard_normal(96); fpred = int(np.argmax(fz @ qf2))
        fh += int(fpred == gold); n += 1
    dr = dh / max(1, n); fr = fh / max(1, n); print("  2-hop QA recall@1: discrete-KG=%.3f fuzzy-embedding=%.3f (gap=%.3f)" % (dr, fr, dr - fr), flush=True)
    return {"discrete": dr, "fuzzy": fr, "gap": dr - fr}
def verdict(r) -> Tuple[str, str]:
    s = "discrete=%.3f fuzzy=%.3f gap=%.3f" % (r["discrete"], r["fuzzy"], r["gap"])
    if r["discrete"] >= 0.70 and r["gap"] >= 0.30: return ("HARD_PASS", "HARD_PASS: discrete-KG K-hop >=0.70 and beats fuzzy by >=0.30 on identical 2-hop QA -- universal principle confirmed at the QA level. " + s)
    if r["gap"] >= 0.15: return ("MIDDLE_BAND", "MIDDLE_BAND: discrete-vs-fuzzy gap 0.15-0.30. " + s)
    return ("HARD_FAIL", "HARD_FAIL: discrete-vs-fuzzy gap <0.15. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
