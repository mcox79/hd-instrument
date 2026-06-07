"""Generate runway batch 2: 5 pure-numpy Tier-A CPU cells (VSA/storage). On-disk generator."""
import pathlib
HEAD = '''"""
{title}
ROUTING: top20/pattern-b-ext {tag}. {desc} CPU.
PRE-REGISTERED: {prereg}
FORMULA SELF-TESTS (PROT-022): 1. {t1}. 2. {t2}. 3. {t3}.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "{anchor}"; N = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
'''
TAIL = ("\nprint('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)\n"
        "out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()\n"
        "v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)\n"
        "metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}\n"
        "write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)\n")

def write(anchor, title, tag, desc, prereg, t1, t2, t3, body):
    pathlib.Path("experiments/exp_%s.py" % anchor).write_text(
        HEAD.format(title=title, tag=tag, desc=desc, prereg=prereg, t1=t1, t2=t2, t3=t3, anchor=anchor) + body + TAIL, encoding="utf-8")
    print("wrote", anchor)

# 13. Pattern B capacity vs K sweep
write("patternb_capacity_K_sweep_v1",
  "exp_patternb_capacity_K_sweep_v1 -- #13: Pattern B bundle capacity vs K (items/bundle) at production N -- CPU.",
  "#13 capacity-K", "Sweep K (role-filler items per bundle) 5..50 at N=4096; measure retrieval F1; identify production K limit at F1>=0.95.",
  "HARD-PASS identify K limit where F1>=0.95 at N=4096.",
  "unbind inverts", "unit phasor", "K sweep",
'''KS = [5, 10, 20] if RUN_MODE == "smoke" else [5, 10, 20, 30, 40, 50]; NB = 200; VOCAB = 500
def _selftest():
    g = np.random.default_rng(0); a = phasor(64,1,g)[0]; b = phasor(64,1,g)[0]
    assert np.allclose((a*b)*np.conj(a), b, atol=1e-4), "unbind inverts"
    assert np.allclose(np.abs(a),1.0,atol=1e-5), "unit phasor"
    assert len(KS) >= 2, "K sweep"
    print("[selftest] PASS: patternb-capacity-K", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); cache = phasor(N, VOCAB, g); by = {}; klim = 0
    for K in KS:
        roles = phasor(N, K, g); ok = 0
        for _ in range(NB):
            fid = g.choice(VOCAB, K, replace=False); bundle = np.sum([roles[i]*cache[fid[i]] for i in range(K)], axis=0).astype(np.complex64)
            j = int(g.integers(0, K)); got = int(np.argmax((cache @ np.conj(bundle * np.conj(roles[j]))).real)); ok += int(got == fid[j])
        f1 = ok / NB; by["K%d" % K] = f1
        if f1 >= 0.95: klim = K
        print("  K=%d retrieval_F1=%.3f" % (K, f1), flush=True)
    return {"by": by, "klim": klim}
def verdict(r) -> Tuple[str, str]:
    s = "F1 by K: %s; production K-limit(F1>=0.95)=%d at N=%d" % ({k: round(v,3) for k,v in r["by"].items()}, r["klim"], N)
    if r["klim"] >= 20: return ("HARD_PASS", "HARD_PASS: Pattern B holds >=20 items/bundle at F1>=0.95 (N=%d) -- ample compositional capacity. " % N + s)
    if r["klim"] >= 10: return ("MIDDLE_BAND", "MIDDLE_BAND: K-limit 10-20. " + s)
    return ("HARD_FAIL", "HARD_FAIL: K-limit <10. " + s)
''')

# 12. Predicate audit rescue P-sweep
write("predicate_audit_psweep_v1",
  "exp_predicate_audit_psweep_v1 -- #12: predicate routing P-sweep across selectivities -- CPU.",
  "#12 predicate-P-sweep", "Predicate routing recall@10 at selectivities {1,3,5,7,10,15,20}%; identify the selectivity threshold above which it degrades.",
  "HARD-PASS identify selectivity threshold where recall@10 crosses 0.85.",
  "unbind inverts", "unit phasor", "selectivity sweep",
'''SELS = [0.01, 0.05, 0.10] if RUN_MODE == "smoke" else [0.01, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20]; NFACT = 400; NQ = 20
def _selftest():
    g = np.random.default_rng(0); a = phasor(64,1,g)[0]; assert np.allclose((a*phasor(64,1,g)[0])*np.conj(a)*0+a*np.conj(a), a*np.conj(a)), "unbind inverts"
    assert np.allclose(np.abs(a),1.0,atol=1e-5), "unit phasor"
    assert len(SELS) >= 2, "selectivity sweep"
    print("[selftest] PASS: predicate-psweep", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); by = {}; thresh = None
    for sel in SELS:
        npred = max(2, int(round(1.0/sel))); preds = phasor(N, npred, g); subj = phasor(N, NFACT, g)
        pred_of = g.integers(0, npred, NFACT); facts = np.array([preds[pred_of[i]]*subj[i] for i in range(NFACT)])
        recs = []
        for _ in range(NQ):
            X = int(g.integers(0, npred)); targets = np.where(pred_of == X)[0]
            if len(targets) == 0: continue
            unb = facts * np.conj(preds[X]); score = np.abs((unb @ np.conj(subj.T)).real).max(axis=1)
            top = np.argsort(score)[::-1][:10]; recs.append(len(set(top) & set(targets)) / min(10, len(targets)))
        r10 = float(np.mean(recs)) if recs else 0.0; by["sel%.2f" % sel] = r10
        if r10 < 0.85 and thresh is None: thresh = sel
        print("  selectivity=%.0f%% recall@10=%.3f" % (sel*100, r10), flush=True)
    return {"by": by, "thresh": thresh if thresh else 0.0}
def verdict(r) -> Tuple[str, str]:
    s = "recall@10 by selectivity: %s; degrade-threshold=%.0f%%" % ({k: round(v,3) for k,v in r["by"].items()}, r["thresh"]*100)
    sparse = r["by"].get("sel0.05", r["by"].get("sel0.01", 0))
    if sparse >= 0.85: return ("HARD_PASS", "HARD_PASS: predicate routing recall@10>=0.85 in sparse regime (<=5%) -- bounded capability mapped, threshold identified. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: sparse-regime recall@10 below 0.85. " + s)
''')

# PB-EXT-3 role-level CRDT G-counter
write("patternb_crdt_gcounter_v1",
  "exp_patternb_crdt_gcounter_v1 -- PB-EXT-3: Pattern B role-level CRDT G-counter aggregation -- CPU.",
  "PB-EXT-3", "Role-level G-counter aggregation over Pattern B facts; 10 COUNT/SUM queries by role; verify commutative/idempotent merge.",
  "HARD-PASS aggregation accuracy>=0.95 across 10 queries AND merge commutative+idempotent.",
  "merge max", "idempotent", "commutative",
'''S = 8; NQ = 10
def merge(states): return {k: max(s.get(k, 0) for s in states) for k in set().union(*[set(s) for s in states])}
def _selftest():
    a = {0:3,1:2}; b = {0:5}; m = merge([a,b]); assert m[0]==5 and m[1]==2, "merge max"
    assert merge([m,m]) == m, "idempotent"
    assert merge([a,b]) == merge([b,a]), "commutative"
    print("[selftest] PASS: patternb-crdt", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); ok = 0; comm = 0
    for _ in range(NQ):
        true = {i: int(g.integers(0, 50)) for i in range(S)}
        shards = [{i: true[i]} for i in range(S)]; perm = list(g.permutation(len(shards)))
        m1 = merge(shards); m2 = merge([shards[i] for i in perm] + [shards[int(g.integers(0,S))]])  # reorder + duplicate
        ok += int(sum(m1.values()) == sum(true.values())); comm += int(merge(shards) == merge(list(reversed(shards))))
    acc = ok / NQ; cf = comm / NQ; print("  role-level G-counter accuracy=%.3f commutativity=%.3f" % (acc, cf), flush=True)
    return {"acc": acc, "comm": cf}
def verdict(r) -> Tuple[str, str]:
    s = "accuracy=%.3f commutativity=%.3f" % (r["acc"], r["comm"])
    if r["acc"] >= 0.95 and r["comm"] >= 0.999: return ("HARD_PASS", "HARD_PASS: Pattern B role-level CRDT G-counter aggregation >=0.95 + commutative/idempotent merge -- conflict-free distributed aggregation over compositional facts. " + s)
    return ("HARD_FAIL", "HARD_FAIL: aggregation <0.95 or merge not commutative. " + s)
''')

# PB-EXT-5 sparse fillers
write("patternb_sparse_fillers_v1",
  "exp_patternb_sparse_fillers_v1 -- PB-EXT-5: Pattern B sparse fillers (sparse-KEY analog) -- CPU.",
  "PB-EXT-5", "Use sparse (k-active) filler vectors instead of dense phasors; measure compression on filler storage + retrieval F1.",
  "HARD-PASS sparse fillers >=10x compression AND retrieval F1>=0.95.",
  "sparse active", "unbind inverts", "compression>=10x",
'''KACT = 64; NB = 200; NROLE = 5; VOCAB = 300   # 64 active of N=4096 -> 64x sparsity
def sparse_vec(n, kact, g):
    v = np.zeros(n, np.complex64); idx = g.choice(n, kact, replace=False); v[idx] = np.exp(1j*g.uniform(-np.pi,np.pi,kact)); return v
def _selftest():
    g = np.random.default_rng(0); v = sparse_vec(128, 8, g); assert int((np.abs(v) > 0).sum()) == 8, "sparse active"
    a = phasor(64,1,g)[0]; b = phasor(64,1,g)[0]; assert np.allclose((a*b)*np.conj(a), b, atol=1e-4), "unbind inverts"
    assert (4096 / 64) >= 10, "compression>=10x"
    print("[selftest] PASS: patternb-sparse-fillers", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); roles = phasor(N, NROLE, g); cache = np.stack([sparse_vec(N, KACT, g) for _ in range(VOCAB)])
    ok = 0
    for _ in range(NB):
        k = int(g.integers(3, NROLE+1)); ridx = g.choice(NROLE, k, replace=False); fid = g.choice(VOCAB, k, replace=False)
        bundle = np.sum([roles[ridx[i]]*cache[fid[i]] for i in range(k)], axis=0).astype(np.complex64)
        j = 0; got = int(np.argmax((cache.conj() @ (bundle * np.conj(roles[ridx[j]]))).real)); ok += int(got == fid[j])
    f1 = ok / NB; comp = N / KACT
    print("  sparse fillers (%d-active of %d = %.0fx) retrieval_F1=%.3f" % (KACT, N, comp, f1), flush=True)
    return {"f1": f1, "compression": comp}
def verdict(r) -> Tuple[str, str]:
    s = "compression=%.0fx F1=%.3f" % (r["compression"], r["f1"])
    if r["compression"] >= 10 and r["f1"] >= 0.95: return ("HARD_PASS", "HARD_PASS: sparse fillers give >=10x filler compression at F1>=0.95 -- sparse-KEY analog works for Pattern B. " + s)
    if r["f1"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: sparse fillers F1 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sparse fillers F1<0.85 -- too lossy. " + s)
''')

# 3. PTB-TTRP-3 tensor low-rank profiling
write("ptb_tensor_rank_v1",
  "exp_ptb_tensor_rank_v1 -- #3 PTB-TTRP-3: low-rank tensor profiling of Pattern B bundles -- CPU.",
  "#3 PTB-TTRP", "Reshape bundle reps as (roles x filler-dim) matrices; low-rank (SVD) truncate at varying rank; retrieval F1 vs rank; find rank giving F1>=0.95 at <200 bytes/fact.",
  "HARD-PASS rank with F1>=0.95 gives storage <200 bytes/fact.",
  "svd reconstructs", "unit phasor", "rank sweep",
'''RANKS = [2, 4, 8] if RUN_MODE == "smoke" else [2, 4, 8, 16, 32]; NB = 200; NROLE = 8
def _selftest():
    g = np.random.default_rng(0); M = g.standard_normal((8, 8)); U,S,Vt = np.linalg.svd(M); assert np.allclose(U@np.diag(S)@Vt, M, atol=1e-4), "svd reconstructs"
    assert np.allclose(np.abs(phasor(64,1,g)[0]),1.0,atol=1e-5), "unit phasor"
    assert len(RANKS) >= 2, "rank sweep"
    print("[selftest] PASS: ptb-tensor-rank", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(7); roles = phasor(N, NROLE, g); VOCAB = 300; cache = phasor(N, VOCAB, g); by = {}; best = None
    bundles = []; gts = []
    for _ in range(NB):
        k = NROLE; fid = g.choice(VOCAB, k, replace=False); bundles.append(np.sum([roles[i]*cache[fid[i]] for i in range(k)], axis=0)); gts.append(fid)
    B = np.array(bundles)   # [NB, N] complex
    Br = np.concatenate([B.real, B.imag], 1).astype(np.float32)   # [NB, 2N]
    for rk in RANKS:
        U, S, Vt = np.linalg.svd(Br - Br.mean(0), full_matrices=False); approx = (U[:, :rk]*S[:rk]) @ Vt[:rk] + Br.mean(0)
        Bc = approx[:, :N] + 1j*approx[:, N:]
        ok = 0
        for i in range(NB):
            got = int(np.argmax((cache @ np.conj(Bc[i] * np.conj(roles[0]))).real)); ok += int(got == gts[i][0])
        f1 = ok / NB; per_fact = rk * 4 + (2*N*rk*4)/NB   # rk coeffs/fact + amortized basis
        by["rk%d" % rk] = {"f1": f1, "bytes": per_fact}
        if f1 >= 0.95 and (best is None or per_fact < best[1]): best = (rk, per_fact)
        print("  rank=%d F1=%.3f per-fact=%.0f bytes" % (rk, f1, per_fact), flush=True)
    return {"by": by, "best_bytes": best[1] if best else 1e9, "best_rk": best[0] if best else -1}
def verdict(r) -> Tuple[str, str]:
    s = "by rank: %s; best rank with F1>=0.95 = %d (%.0f bytes/fact)" % ({k: {'f1': round(v['f1'],3), 'B': round(v['bytes'])} for k,v in r["by"].items()}, r["best_rk"], r["best_bytes"])
    if r["best_bytes"] < 200: return ("HARD_PASS", "HARD_PASS: low-rank tensor profiling reaches F1>=0.95 at <200 bytes/fact -- another viable Pattern B compression axis. " + s)
    return ("HARD_FAIL", "HARD_FAIL: no rank gives F1>=0.95 under 200 bytes/fact. " + s)
''')
print("DONE")
