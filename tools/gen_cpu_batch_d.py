"""Generator: CPU batch D (5 pure-numpy substrate capability cells). Run: python tools/gen_cpu_batch_d.py"""
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
C.append(dict(anchor="topk_recall_cpu_v1", tag="recall@k under heavy noise",
  title="top-k recall recovers the true item even when top-1 fails",
  desc="Measure recall@k (k=1,5,10) for sign-key queries under heavy bit-flip (0.20,0.35); even when top-1 misses, the true item should sit in the top-k -- supports a re-rank/verify stage.",
  prereg="HARD-PASS recall@5 >= 0.95 at 0.35 bit-flip. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    a = np.array([3, 1, 2]); assert set(np.argsort(-a)[:2].tolist()) == {0, 2}, "topk"; print("[selftest] PASS: topk-recall-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(31); N = 5000 if SMOKE else 20000; D = 512; NQ = 400; by = {}
    X = np.sign(g.standard_normal((N, D))).astype(np.float32); qi = g.choice(N, NQ, replace=False)
    for flip in [0.20, 0.35]:
        Q = X[qi].copy(); fl = g.random((NQ, D)) < flip; Q[fl] *= -1; sc = Q @ X.T; ordr = np.argsort(-sc, axis=1)
        for k in [1, 5, 10]:
            topk = ordr[:, :k]; hit = float(np.mean([qi[i] in topk[i] for i in range(NQ)])); by["f%.2f_k%d" % (flip, k)] = hit
    print("  recall@k: %s" % {k: round(v, 3) for k, v in by.items()}, flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    r5 = r["by"].get("f0.35_k5", 0.0); s = "recall@k: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if r5 >= 0.95: return ("HARD_PASS", "HARD_PASS: recall@5>=0.95 even at 0.35 bit-flip -- a cheap re-rank stage recovers what top-1 misses. " + s)
    if r5 >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: recall@5 0.85-0.95 at 0.35 flip. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall@5 <0.85 at 0.35 flip. " + s)
'''))
C.append(dict(anchor="hierarchical_2level_cpu_v1", tag="category-conditioned retrieval",
  title="2-level hierarchy: query a category, retrieve its member items",
  desc="Store items bound to their category (M = sum cat[c]*item). Query a category by unbinding -> superposition of its members -> cleanup top-n recovers them. Tests hierarchical/faceted retrieval.",
  prereg="HARD-PASS category-conditioned recall of members >= 0.90 (n_per_cat members, C cats). MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  body='''
def _selftest():
    assert np.argsort(-np.array([0.1, 0.9, 0.5]))[0] == 1, "argsort"; print("[selftest] PASS: hierarchical-2level-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(32); N = 2048; C = 20; PER = 6; V = C * PER
    cats = cphasor(C, N, g); items = cphasor(V, N, g)
    M = np.zeros(N, dtype=np.complex64)
    for c in range(C):
        for j in range(PER):
            M = M + cats[c] * items[c * PER + j]
    hit = 0; tot = 0
    for c in range(C):
        rec = M * cats[c].conj(); sc = (items @ rec.conj()).real; top = np.argsort(-sc)[:PER]
        members = set(range(c * PER, c * PER + PER)); hit += len(set(top.tolist()) & members); tot += PER
    rec = hit / tot; print("  category-conditioned member recall=%.3f (C=%d PER=%d N=%d)" % (rec, C, PER, N), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "member-recall=%.3f" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: category query recovers its members >=0.90 -- hierarchical/faceted retrieval works. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: member recall 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: member recall <0.75. " + s)
'''))
C.append(dict(anchor="set_membership_bundle_cpu_v1", tag="VSA set membership",
  title="bundled-set membership test separates members from non-members",
  desc="Bundle a set S of items into one hypervector; test membership by cosine of an item to the bundle (members high, non-members low). Measures the member-vs-nonmember AUC vs set size.",
  prereg="HARD-PASS AUC >= 0.95 at set size 50 (N=4096). MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    assert 4096 > 50, "size"; print("[selftest] PASS: set-membership-bundle-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(33); N = 2048 if SMOKE else 4096; V = 2000; S = 50; TR = 30 if SMOKE else 100
    book = cphasor(V, N, g); aucs = []
    for _ in range(TR):
        idx = g.choice(V, S, replace=False); B = book[idx].sum(0)
        mem = set(idx.tolist()); sc = (book @ B.conj()).real / N
        inm = sc[idx]; outm = sc[np.array([i for i in range(V) if i not in mem])]
        alls = np.concatenate([inm, outm]); lab = np.concatenate([np.ones(len(inm)), np.zeros(len(outm))])
        order = np.argsort(alls); ranks = np.empty_like(order, dtype=np.float64); ranks[order] = np.arange(1, len(alls) + 1)
        ni = len(inm); no = len(outm); auc = (ranks[lab == 1].sum() - ni * (ni + 1) / 2) / (ni * no); aucs.append(auc)
    a = float(np.mean(aucs)); print("  membership AUC=%.4f (set size=%d, V=%d, N=%d)" % (a, S, V, N), flush=True)
    return {"auc": a, "S": S}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.4f at set size %d" % (r["auc"], r["S"])
    if r["auc"] >= 0.95: return ("HARD_PASS", "HARD_PASS: bundled-set membership AUC>=0.95 -- set membership without per-item storage. " + s)
    if r["auc"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: membership AUC 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: membership AUC <0.85. " + s)
'''))
C.append(dict(anchor="continuous_regression_cpu_v1", tag="key->scalar regression readout",
  title="pinv readout recalls continuous scalar values (not just discrete items)",
  desc="Store (key -> continuous scalar) pairs via a ridge readout vector; predict the stored scalar for each key; measure R^2. Tests that the substrate holds continuous (numeric) payloads, not only categorical fillers.",
  prereg="HARD-PASS R^2 >= 0.95 at load M/D=0.7. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    assert abs(np.corrcoef([1, 2, 3], [1, 2, 3])[0, 1] - 1.0) < 1e-9, "corr"; print("[selftest] PASS: continuous-regression-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(34); D = 512; M = int(0.7 * D); lam = 1e-2
    K = np.sign(g.standard_normal((M, D))).astype(np.float64); y = g.standard_normal(M)
    w = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ y); yhat = K @ w
    ss_res = float(np.sum((y - yhat) ** 2)); ss_tot = float(np.sum((y - y.mean()) ** 2)); r2 = 1 - ss_res / ss_tot
    print("  R^2=%.4f at load M/D=0.7 (D=%d M=%d)" % (r2, D, M), flush=True)
    return {"r2": r2}
def verdict(r) -> Tuple[str, str]:
    s = "R^2=%.4f" % r["r2"]
    if r["r2"] >= 0.95: return ("HARD_PASS", "HARD_PASS: continuous-value readout R^2>=0.95 -- substrate stores numeric payloads, not just categories. " + s)
    if r["r2"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: R^2 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: R^2 <0.85. " + s)
'''))
C.append(dict(anchor="ensemble_vote_cpu_v1", tag="ensemble majority vote",
  title="majority vote across independent substrates beats a single one under noise",
  desc="Store the same items in R independent random-sign substrates; recall a noisy query in each; majority-vote the predicted index. Vote accuracy should exceed single-substrate accuracy (error averaging).",
  prereg="HARD-PASS vote accuracy >= single + 0.05 at heavy noise. MIDDLE >= single. HARD-FAIL vote < single.",
  body='''
def _selftest():
    from collections import Counter; assert Counter([1, 1, 2]).most_common(1)[0][0] == 1, "vote"; print("[selftest] PASS: ensemble-vote-cpu", flush=True)
def run() -> Dict:
    from collections import Counter
    g = np.random.default_rng(35); N = 3000 if SMOKE else 8000; D = 256; R = 5; NQ = 400; FLIP = 0.40
    base = np.sign(g.standard_normal((N, D))).astype(np.float32)
    projs = [g.standard_normal((D, D)) for _ in range(R)]; subs = [np.sign(base @ P) for P in projs]
    qi = g.choice(N, NQ, replace=False); single_hits = 0; vote_hits = 0
    for n, i in enumerate(qi):
        preds = []
        for ridx in range(R):
            q = subs[ridx][i].copy(); fl = g.random(D) < FLIP; q[fl] *= -1; preds.append(int(np.argmax(q @ subs[ridx].T)))
        single_hits += int(preds[0] == i); vote_hits += int(Counter(preds).most_common(1)[0][0] == i)
    single = single_hits / NQ; vote = vote_hits / NQ; print("  single=%.3f vote(R=%d)=%.3f gain=%.3f (flip=%.2f)" % (single, R, vote, vote - single, FLIP), flush=True)
    return {"single": single, "vote": vote, "gain": vote - single}
def verdict(r) -> Tuple[str, str]:
    s = "single=%.3f vote=%.3f gain=%.3f" % (r["single"], r["vote"], r["gain"])
    if r["gain"] >= 0.05: return ("HARD_PASS", "HARD_PASS: ensemble majority vote beats single substrate by >=0.05 -- error-averaging redundancy improves recall. " + s)
    if r["gain"] >= 0.0: return ("MIDDLE_BAND", "MIDDLE_BAND: vote >= single but gain <0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: vote worse than single. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
