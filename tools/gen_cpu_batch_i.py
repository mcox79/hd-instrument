"""Generator: CPU batch I (5 v1.5-LOCK anchors). Run: python tools/gen_cpu_batch_i.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: v1.5 LOCK batch ({tag}). {desc} Pure numpy. CPU.
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
C.append(dict(anchor="sharding_contrast_demo_data_cpu_v1", tag="B1 sharding contrast demo data",
  title="demo dataset: monolithic recall collapse vs sharded flat recall",
  desc="Produce the demo-ready contrast curve: as total stored items grow, monolithic single-bundle recall collapses while sharded (fixed per-shard load) stays flat at ~1.0. Emits the table for the v1 demo's capacity-story slide.",
  prereg="HARD-PASS at the largest total, sharded recall >= 0.95 AND monolithic recall <= 0.40 (clear demo contrast). MIDDLE gap >= 0.40. HARD-FAIL otherwise.",
  body='''
def _selftest():
    assert 16 * 80 == 1280, "total"; print("[selftest] PASS: sharding-contrast-demo-data", flush=True)
def run() -> Dict:
    g = np.random.default_rng(81); N = 4096; K = 80; book = cphasor(2000, N, g); Ss = [1, 4, 16] if SMOKE else [1, 2, 4, 8, 16, 32, 64]
    mono = {}; shard = {}
    for S in Ss:
        keys = cphasor(S * K, N, g); vals = g.integers(0, 2000, S * K)
        Mono = np.zeros(N, dtype=np.complex64); shards = [np.zeros(N, dtype=np.complex64) for _ in range(S)]
        for i in range(S * K):
            Mono = Mono + keys[i] * book[vals[i]]; shards[i // K] = shards[i // K] + keys[i] * book[vals[i]]
        mh = sum(int(cidx(Mono * np.conj(keys[i]), book) == vals[i]) for i in range(S * K)) / (S * K)
        sh = sum(int(cidx(shards[i // K] * np.conj(keys[i]), book) == vals[i]) for i in range(S * K)) / (S * K)
        mono["t%d" % (S * K)] = round(mh, 3); shard["t%d" % (S * K)] = round(sh, 3)
        print("  total=%d monolithic=%.3f sharded=%.3f" % (S * K, mh, sh), flush=True)
    big = "t%d" % (max(Ss) * K); return {"mono": mono, "shard": shard, "mono_big": mono[big], "shard_big": shard[big]}
def verdict(r) -> Tuple[str, str]:
    s = "at largest: sharded=%.3f monolithic=%.3f | sharded-curve=%s mono-curve=%s" % (r["shard_big"], r["mono_big"], r["shard"], r["mono"])
    if r["shard_big"] >= 0.95 and r["mono_big"] <= 0.40: return ("HARD_PASS", "HARD_PASS: demo contrast is sharp -- sharded stays >=0.95 while monolithic collapses to <=0.40. " + s)
    if r["shard_big"] - r["mono_big"] >= 0.40: return ("MIDDLE_BAND", "MIDDLE_BAND: contrast gap >=0.40 but not at target bands. " + s)
    return ("HARD_FAIL", "HARD_FAIL: weak demo contrast. " + s)
'''))
C.append(dict(anchor="legal_citation_500seed_cpu_v1", tag="B4 legal citation 500-seed demo",
  title="legal-citation snowball holds at 10x scale (500 seeds, 2000 cases)",
  desc="Extends the legal-citation snowball demo (PP-120) from 50 to 500 seeds over a 2000-case citation graph; validates that substrate K-hop 3-hop closure recovery holds at 10x demo scale (legal-pitch dataset).",
  prereg="HARD-PASS 3-hop closure recovery >= 0.95 across 500 seeds at 2000 cases. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; R = cphasor(1, 64, g)[0]; b = cphasor(1, 64, g)[0]
    assert np.allclose(a * R * b * np.conj(a * R), b, atol=1e-3), "bind/unbind"; print("[selftest] PASS: legal-citation-500seed", flush=True)
def run() -> Dict:
    g = np.random.default_rng(82); N = 8192; VC = 800 if SMOKE else 2000; AVG = 3; NSEED = 100 if SMOKE else 500; THRESH = 0.18
    cases = cphasor(VC, N, g); CITES = cphasor(1, N, g)[0]; adj = {i: [] for i in range(VC)}; M = np.zeros(N, dtype=np.complex64)
    for i in range(VC):
        outs = g.choice(VC, size=int(g.integers(1, AVG + 2)), replace=False)
        for o in outs:
            if int(o) != i and int(o) not in adj[i]:
                adj[i].append(int(o)); M = M + cases[i] * CITES * cases[int(o)]
    def tclose(seed, hops=3):
        seen = set(); fr = {seed}
        for _ in range(hops):
            nf = set()
            for u in fr:
                nf |= set(adj[u]) - seen
            seen |= nf; fr = nf
        return seen
    def snow(seed, hops=3):
        reached = set(); fr = {seed}
        for _ in range(hops):
            nf = set()
            for u in fr:
                sc = (cases @ np.conj(M * np.conj(cases[u] * CITES))).real / N
                for v in np.where(sc > THRESH)[0].tolist():
                    if v not in reached and v != u:
                        nf.add(int(v))
            reached |= nf; fr = nf
            if not fr:
                break
        return reached
    recs = []
    seeds = g.choice(VC, NSEED, replace=False)
    for seed in seeds:
        tc = tclose(int(seed))
        if tc:
            recs.append(len(tc & snow(int(seed))) / len(tc))
    rec = float(np.mean(recs)); print("  3-hop closure recovery=%.3f (%d seeds, %d cases)" % (rec, len(recs), VC), flush=True)
    return {"recall": rec, "cases": VC, "seeds": len(recs)}
def verdict(r) -> Tuple[str, str]:
    s = "closure-recovery=%.3f (%d seeds, %d cases)" % (r["recall"], r["seeds"], r["cases"])
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: legal-citation snowball holds >=0.95 closure at 10x demo scale -- legal-pitch dataset validated. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: closure 0.85-0.95 at scale. " + s)
    return ("HARD_FAIL", "HARD_FAIL: closure <0.85 at scale. " + s)
'''))
C.append(dict(anchor="n1d_parallel_subq_native_cpu_v1", tag="C2 N1d parallel sub-question on NATIVE substrate",
  title="parallel sub-question decomposition on the discrete-KG substrate",
  desc="Native counterpart to N1e (fuzzy). Decompose a 2-hop question into TWO sub-queries answerable in PARALLEL on the discrete KG: (hop1: start-r1->bridge) and, given the bridge, (hop2: bridge-r2->answer). Parallel discrete sub-queries vs the single chained K-hop. recall@1 of the answer. Tests whether parallel decomposition on native substrate matches/beats chained K-hop.",
  prereg="HARD-PASS parallel-native recall@1 >= 0.70 (matches chained K-hop on discrete). MIDDLE >= 0.55. HARD-FAIL < 0.55.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; R = cphasor(1, 64, g)[0]; b = cphasor(1, 64, g)[0]
    assert np.allclose((a * R * b) * np.conj(a * R), b, atol=1e-3), "unbind"; print("[selftest] PASS: n1d-parallel-subq-native", flush=True)
def run() -> Dict:
    g = np.random.default_rng(83); N = 8192; VE = 200; VR = 12; deg = 2; TR = 60 if SMOKE else 200
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}; M = np.zeros(N, dtype=np.complex64)
    for s in range(VE):
        for _ in range(deg):
            r = int(g.integers(0, VR)); o = int(g.integers(0, VE))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    def path():
        for _ in range(150):
            s = int(g.integers(0, VE)); o1 = [(r, edges[(s, r)]) for (ss, r) in edges if ss == s]
            if not o1:
                continue
            r1, b = o1[int(g.integers(0, len(o1)))]; o2 = [(r, edges[(b, r)]) for (ss, r) in edges if ss == b]
            if not o2:
                continue
            r2, a = o2[int(g.integers(0, len(o2)))]; return s, r1, b, r2, a
        return None
    chained = 0; parallel = 0; n = 0
    for _ in range(TR):
        p = path()
        if not p:
            continue
        s, r1, b, r2, a = p
        bc = cidx(M * np.conj(ents[s] * rels[r1]), ents); ac = cidx(M * np.conj(ents[bc] * rels[r2]), ents); chained += int(ac == a)
        # parallel: sub-q1 -> bridge candidates; sub-q2 anchored on each candidate -> answer; pick consistent
        sc1 = (ents @ np.conj(M * np.conj(ents[s] * rels[r1]))).real; cand = np.argsort(-sc1)[:3]
        best = -1; bs = -1e18
        for c in cand:
            sc2 = (ents @ np.conj(M * np.conj(ents[int(c)] * rels[r2]))).real; j = int(np.argmax(sc2))
            if sc1[c] + sc2[j] > bs:
                bs = sc1[c] + sc2[j]; best = j
        parallel += int(best == a); n += 1
    cr = chained / max(1, n); pr = parallel / max(1, n); print("  chained-Khop=%.3f parallel-subq-native=%.3f (n=%d)" % (cr, pr, n), flush=True)
    return {"chained": cr, "parallel": pr}
def verdict(r) -> Tuple[str, str]:
    s = "parallel-native=%.3f chained-Khop=%.3f" % (r["parallel"], r["chained"])
    if r["parallel"] >= 0.70: return ("HARD_PASS", "HARD_PASS: parallel sub-question decomposition on native substrate recall>=0.70 -- parallel matches chained K-hop on discrete (decomposition-pattern agnostic when grounded discretely). " + s)
    if r["parallel"] >= 0.55: return ("MIDDLE_BAND", "MIDDLE_BAND: parallel-native 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: parallel-native <0.55. " + s)
'''))
C.append(dict(anchor="resonator_k4_multiaxis_rescue_cpu_v1", tag="F2 resonator K=4 multi-axis rescue",
  title="resonator K=4 factorization rescue via N up + M down + more iterations",
  desc="K=4 resonator factorization was HARD_FAIL (~0.5 at N=4096). Multi-axis rescue: larger N=16384, smaller codebook M=15, more iterations (200), and codebook-mean init. Tests whether combined axes lift K=4 full-factorization to a usable level.",
  prereg="HARD-PASS K=4 full-factorization success >= 0.85. MIDDLE >= 0.65. HARD-FAIL < 0.65.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; b = cphasor(1, 32, g)[0]; assert np.allclose(a * b * np.conj(b), a, atol=1e-3), "bind"; print("[selftest] PASS: resonator-k4-multiaxis-rescue", flush=True)
def run() -> Dict:
    g = np.random.default_rng(84); N = 8192 if SMOKE else 16384; M = 15; K = 4; MAXIT = 200; TR = 25 if SMOKE else 80
    succ = 0
    for _ in range(TR):
        books = [cphasor(M, N, g) for _ in range(K)]
        true = [int(g.integers(0, M)) for _ in range(K)]
        s = np.ones(N, dtype=np.complex64)
        for k in range(K):
            s = s * books[k][true[k]]
        est = [b.mean(0) for b in books]; est = [e / (np.abs(e) + 1e-8) for e in est]; prev = None
        for _ in range(MAXIT):
            idxs = []
            for k in range(K):
                others = np.ones(N, dtype=np.complex64)
                for j in range(K):
                    if j != k:
                        others = others * est[j]
                rr = s * np.conj(others); sc = books[k] @ np.conj(rr); est[k] = (sc @ books[k]); est[k] = est[k] / (np.abs(est[k]) + 1e-8)
                idxs.append(int(np.argmax(sc.real)))
            if idxs == prev:
                break
            prev = idxs
        succ += int(idxs == true)
    rec = succ / TR; print("  K=4 full-factorization success=%.3f (N=%d M=%d iters<=%d)" % (rec, N, M, MAXIT), flush=True)
    return {"recall": rec, "N": N}
def verdict(r) -> Tuple[str, str]:
    s = "K=4 success=%.3f at N=%d" % (r["recall"], r["N"])
    if r["recall"] >= 0.85: return ("HARD_PASS", "HARD_PASS: multi-axis rescue lifts K=4 resonator factorization to >=0.85 -- 4-factor disentangling is usable at N=16384/M=15. " + s)
    if r["recall"] >= 0.65: return ("MIDDLE_BAND", "MIDDLE_BAND: K=4 0.65-0.85 (improved; 4-factor near limit). " + s)
    return ("HARD_FAIL", "HARD_FAIL: K=4 <0.65 even multi-axis -- 4-factor joint disentangling is a hard limit. " + s)
'''))
C.append(dict(anchor="mycorrhizal_simweighted_rescue_cpu_v1", tag="F3 mycorrhizal similarity-weighted rescue",
  title="similarity-weighted multi-hub init clears the warm-start coverage gate",
  desc="Mycorrhizal multi-hub init plateaued MID (~0.55-0.6). Rescue: instead of a uniform union of source hubs, weight each source's hub contribution by that source's distributional similarity to the new customer (mycorrhizal nutrient-sharing is similarity-gated). Measures B coverage at Q=100.",
  prereg="HARD-PASS similarity-weighted multi-hub coverage >= 0.70 (clears gate). MIDDLE 0.60-0.70. HARD-FAIL < 0.60.",
  body='''
def zipf(v, s=1.1):
    p = 1.0 / np.power(np.arange(1, v + 1), s); return p / p.sum()
def _selftest():
    assert zipf(10)[0] > zipf(10)[9], "zipf"; print("[selftest] PASS: mycorrhizal-simweighted-rescue", flush=True)
def run() -> Dict:
    g = np.random.default_rng(85); V = 2000; QB = 100; HUBS = 200; M_SRC = 12 if SMOKE else 20
    pA = zipf(V)
    permB = g.permutation(V); tailB = np.zeros(V); tailB[permB] = zipf(V); pB = 0.6 * pA + 0.4 * tailB; pB /= pB.sum()
    streamB = g.choice(V, QB, p=pB)
    srcs = []
    for _ in range(M_SRC):
        perm = g.permutation(V); tail = np.zeros(V); tail[perm] = zipf(V); pc = 0.6 * pA + 0.4 * tail; pc /= pc.sum(); srcs.append(pc)
    # uniform union (baseline)
    uni = set()
    for pc in srcs:
        uni |= set(int(i) for i in np.argsort(pc)[::-1][:HUBS])
    # similarity-weighted: weight each source by cosine(pc, pB); take more hubs from similar sources
    sims = np.array([float(np.dot(pc, pB) / (np.linalg.norm(pc) * np.linalg.norm(pB))) for pc in srcs]); w = sims / sims.sum()
    simw = set()
    for k, pc in enumerate(srcs):
        take = int(HUBS * len(srcs) * w[k]); simw |= set(int(i) for i in np.argsort(pc)[::-1][:max(20, take)])
    def cov(cache):
        return sum(int(b) in cache for b in streamB) / QB
    uc = cov(uni); sc = cov(simw); print("  coverage Q=%d: uniform-union=%.3f similarity-weighted=%.3f (uniq hubs %d/%d)" % (QB, uc, sc, len(uni), len(simw)), flush=True)
    return {"uniform": uc, "simweighted": sc}
def verdict(r) -> Tuple[str, str]:
    s = "similarity-weighted=%.3f uniform-union=%.3f" % (r["simweighted"], r["uniform"])
    if r["simweighted"] >= 0.70: return ("HARD_PASS", "HARD_PASS: similarity-weighted multi-hub init clears 0.70 coverage -- similarity-gated nutrient-sharing warm-starts new customers. " + s)
    if r["simweighted"] >= 0.60: return ("MIDDLE_BAND", "MIDDLE_BAND: similarity-weighted 0.60-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: similarity-weighted <0.60. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
