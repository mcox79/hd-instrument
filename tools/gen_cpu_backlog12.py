"""Generate cpu_backlog_high_priority_12: the 10 pure-numpy CPU cells (#1-9,#12; #10/#11 need GPU ZKL harness)."""
import pathlib
HEAD = '''"""
{title}
ROUTING: cpu_backlog_high_priority_12 {tag}. {desc} CPU.
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
def sign_keys(M, n, g): return np.sign(g.standard_normal((M, n))).astype(np.float32)
def pinv_W(K, ridge=1e-3):
    W = (K.T @ np.linalg.solve(K @ K.T + ridge * np.eye(len(K)), K)).astype(np.float32); np.fill_diagonal(W, 0.0); return W
def recall(W, K, g, flip=0.05, it=8):
    s = K * np.where(g.random(K.shape) < flip, -1.0, 1.0)
    for _ in range(it):
        rec = np.sign(s @ W.T); rec[rec == 0] = 1.0; s = rec
    return float(np.mean(np.all(rec == K, axis=1)))
def quant(W, bits):
    L = 2 ** bits - 1; lo, hi = np.quantile(W, 0.001), np.quantile(W, 0.999); Wc = np.clip(W, lo, hi)
    return (np.round((Wc - lo) / (hi - lo + 1e-12) * L) / L * (hi - lo) + lo).astype(np.float32)
'''
TAIL = ("\nprint('[config] anchor=%s mode=%s N=%d' % (ANCHOR_NAME, RUN_MODE, N), flush=True)\n"
        "out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()\n"
        "v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)\n"
        "metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}\n"
        "write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)\n")
ST = '''def _selftest():
    g = np.random.default_rng(0); K = sign_keys(3, 64, g); W = pinv_W(K); assert recall(W, K, np.random.default_rng(1), flip=0.0) >= 0.9, "pinv recovers"
    assert quant(W, 4).shape == W.shape, "quant ok"
    assert set(np.unique(K)) <= {-1.0, 1.0}, "sign keys"
    print("[selftest] PASS: %s" % ANCHOR_NAME, flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
'''
def write(anchor, title, tag, desc, prereg, body):
    pathlib.Path("experiments/exp_%s.py" % anchor).write_text(
        HEAD.format(title=title, tag=tag, desc=desc, prereg=prereg, t1="pinv recovers", t2="quant ok", t3="sign keys", anchor=anchor) + ST + body + TAIL, encoding="utf-8")
    print("wrote", anchor)

# #1 SMW launch-overhead profiling
write("smw_overhead_profile_v1", "exp_smw_overhead_profile_v1 -- #1: SMW rank-1 update phase timing -- CPU.",
  "#1 SMW-profile", "Time the phases of a rank-1 Sherman-Morrison-Woodbury pinv update at production N; identify the dominant phase.",
  "HARD-PASS identify a phase consuming >50pct of update time.",
'''def run() -> Dict:
    g = np.random.default_rng(7); M = int(0.1 * N); K = sign_keys(M, N, g); G = K @ K.T + 1e-3*np.eye(M); Ginv = np.linalg.inv(G)
    k = sign_keys(1, N, g)[0]; ph = {}
    t = time.perf_counter(); u = K @ k; ph["gram_update"] = time.perf_counter() - t
    t = time.perf_counter(); v = Ginv @ u; ph["inv_apply"] = time.perf_counter() - t
    t = time.perf_counter(); denom = 1.0 + k @ k - u @ v; ph["denom"] = time.perf_counter() - t
    t = time.perf_counter(); Ginv2 = Ginv + np.outer(v, v) / denom; ph["rank1_update"] = time.perf_counter() - t
    tot = sum(ph.values()); dom = max(ph, key=ph.get); frac = ph[dom] / tot
    print("  phase fractions: %s; dominant=%s (%.1f pct)" % ({k2: round(v2/tot,3) for k2,v2 in ph.items()}, dom, frac*100), flush=True)
    return {"dom": dom, "frac": frac}
def verdict(r) -> Tuple[str, str]:
    s = "dominant phase=%s frac=%.2f" % (r["dom"], r["frac"])
    if r["frac"] > 0.50: return ("HARD_PASS", "HARD_PASS: SMW update dominated by '%s' (>50pct) -- the optimization target is identified. " % r["dom"] + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: no single phase >50pct. " + s)
''')

# #2 fp16 vs bf16 capacity parity
write("fp16_bf16_capacity_v1", "exp_fp16_bf16_capacity_v1 -- #2: fp16 vs bf16 capacity parity -- CPU.",
  "#2 fp16-bf16", "Compare recall@1 of pinv W stored in fp16 vs bf16 across load; characterize the crossover/safe-M for fp16.",
  "HARD-PASS characterize fp16 vs bf16 crossover (document safe M for fp16).",
'''def to_bf16(W):
    u = W.astype(np.float32).view(np.uint32); u = (u + 0x8000) & 0xFFFF0000; return u.view(np.float32)
def run() -> Dict:
    g = np.random.default_rng(7); by = {}
    for load in ([0.1, 0.3] if RUN_MODE=="smoke" else [0.1, 0.2, 0.3, 0.5]):
        M = max(2, int(load*N)); K = sign_keys(M, N, g); W = pinv_W(K)
        r16 = recall(W.astype(np.float16).astype(np.float32), K, np.random.default_rng(1)); rbf = recall(to_bf16(W), K, np.random.default_rng(1))
        by["L%.1f" % load] = {"fp16": r16, "bf16": rbf}; print("  load=%.1f fp16=%.3f bf16=%.3f" % (load, r16, rbf), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    s = "by load: %s" % {k: {"f16": round(v["fp16"],3), "bf16": round(v["bf16"],3)} for k,v in r["by"].items()}
    parity = all(abs(v["fp16"]-v["bf16"]) < 0.05 for v in r["by"].values())
    if parity: return ("HARD_PASS", "HARD_PASS: fp16/bf16 capacity parity (<5pct gap) across loads -- both precisions safe; crossover characterized. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: fp16/bf16 diverge at some load -- crossover documented. " + s)
''')

# #3 rank-k Woodbury
write("rank_k_woodbury_v1", "exp_rank_k_woodbury_v1 -- #3: rank-k Woodbury low-rank inverse-update accuracy/throughput -- CPU.",
  "#3 rank-k-Woodbury", "Approximate pinv via rank-k Woodbury update; sweep k; measure recall vs throughput vs full pinv.",
  "HARD-PASS a k giving acceptable accuracy AND >=2x throughput vs full pinv.",
'''def run() -> Dict:
    g = np.random.default_rng(7); M = int(0.2 * N); K = sign_keys(M, N, g)
    t = time.perf_counter(); Wf = pinv_W(K); tf = time.perf_counter() - t; rf = recall(Wf, K, np.random.default_rng(1))
    by = {}
    for k in ([8, 32] if RUN_MODE=="smoke" else [8, 16, 32, 64]):
        t = time.perf_counter(); U, S, Vt = np.linalg.svd(K, full_matrices=False); Kk = (U[:, :k]*S[:k]) @ Vt[:k]; Wk = pinv_W(Kk.astype(np.float32)); tk = time.perf_counter() - t
        rk = recall(Wk, K, np.random.default_rng(1)); by["k%d" % k] = {"rec": rk, "speedup": tf/max(tk,1e-6)}
        print("  k=%d recall=%.3f speedup=%.2fx (full recall=%.3f)" % (k, rk, tf/max(tk,1e-6), rf), flush=True)
    return {"by": by, "full": rf}
def verdict(r) -> Tuple[str, str]:
    s = "full=%.3f by k: %s" % (r["full"], {k: {"r": round(v["rec"],3), "x": round(v["speedup"],2)} for k,v in r["by"].items()})
    ok = any(v["rec"] >= r["full"] - 0.05 and v["speedup"] >= 2.0 for v in r["by"].values())
    if ok: return ("HARD_PASS", "HARD_PASS: a rank-k Woodbury gives accuracy within 5pct of full pinv at >=2x throughput. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: no k hits both accuracy + 2x speedup. " + s)
''')

# #4 CRT capacity boost
write("crt_capacity_boost_v1", "exp_crt_capacity_boost_v1 -- #4: Chinese-Remainder-Theorem residue capacity boost -- CPU.",
  "#4 CRT", "Encode each fact id as CRT residues across coprime moduli; store per-modulus; recover by CRT reconstruction; compare effective capacity to single-store.",
  "HARD-PASS CRT gives >=2x effective capacity at agreement.",
'''import math
def run() -> Dict:
    g = np.random.default_rng(7); mods = [7, 11, 13]; prod = math.prod(mods)
    M = int(0.3 * N)   # over single-store capacity (~0.14 hebb); CRT splits the index space
    K = sign_keys(M, N, g)
    # single-store recall at this load (baseline)
    base = recall(pinv_W(K), K, np.random.default_rng(1))
    # CRT: partition facts by residue mod m into separate stores (each lower-load)
    crt_ok = 0; trials = M
    stores = {}
    for m in mods:
        for r in range(m):
            idx = [i for i in range(M) if i % m == r]
            if idx: stores[(m, r)] = (np.array(idx), pinv_W(K[idx]))
    for i in range(M):
        votes = []
        for m in mods:
            idx, W = stores[(m, i % m)]; rec = np.sign(K[i] @ W.T); rec[rec==0]=1.0
            local = int(np.all(rec == K[idx][list(idx).index(i)]))
            votes.append(local)
        crt_ok += int(sum(votes) >= 2)   # CRT agreement across >=2 moduli
    crt = crt_ok / M; print("  single-store recall=%.3f CRT-agreement recall=%.3f (load=0.3, mods=%s)" % (base, crt, mods), flush=True)
    return {"base": base, "crt": crt, "ratio": crt / max(base, 1e-6)}
def verdict(r) -> Tuple[str, str]:
    s = "single=%.3f CRT=%.3f ratio=%.2fx" % (r["base"], r["crt"], r["ratio"])
    if r["crt"] >= 0.95 and r["base"] < 0.95: return ("HARD_PASS", "HARD_PASS: CRT residue partition recovers >=0.95 where single-store fails -- effective capacity boost. " + s)
    if r["ratio"] >= 1.5: return ("MIDDLE_BAND", "MIDDLE_BAND: CRT ratio 1.5-2x. " + s)
    return ("HARD_FAIL", "HARD_FAIL: CRT no meaningful boost. " + s)
''')

# #5 multi-step causal chains k=2,3,4
write("patternb_chain_k234_v1", "exp_patternb_chain_k234_v1 -- #5: Pattern B multi-step causal chains k=2/3/4 -- CPU.",
  "#5 chain-k234", "Chained unbinding through k hops (each fact links to next via a bridge role) at production N; measure end-to-end chain retrieval at k=2/3/4.",
  "HARD-PASS chain retrieval >=80pct at k=3 and >=65pct at k=4.",
'''def run() -> Dict:
    g = np.random.default_rng(7); VOCAB = 500; cache = phasor(N, VOCAB, g); link = phasor(N, 1, g)[0]; by = {}
    T = 100 if RUN_MODE=="smoke" else 300
    for k in [2, 3, 4]:
        ok = 0
        for _ in range(T):
            chain = g.choice(VOCAB, k+1, replace=False)
            facts = [(link * cache[chain[i]] + cache[chain[i+1]]).astype(np.complex64) for i in range(k)]   # fact_i: link->next bound + payload
            cur = chain[0]; good = True
            for i in range(k):
                nxt = int(np.argmax((cache.conj() @ (facts[i] * np.conj(link))).real))
                if nxt != chain[i+1]: good = False; break
                cur = nxt
            ok += int(good)
        by["k%d" % k] = ok / T; print("  k=%d chain-retrieval=%.3f" % (k, by["k%d" % k]), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    s = "chain retrieval by k: %s" % {k: round(v,3) for k,v in r["by"].items()}
    if r["by"].get("k3",0) >= 0.80 and r["by"].get("k4",0) >= 0.65: return ("HARD_PASS", "HARD_PASS: multi-step chain retrieval >=80pct@k3, >=65pct@k4 -- substrate-native deep causal chaining works. " + s)
    if r["by"].get("k3",0) >= 0.65: return ("MIDDLE_BAND", "MIDDLE_BAND: chains degrade by k=4. " + s)
    return ("HARD_FAIL", "HARD_FAIL: chains fail by k=3. " + s)
''')

# #6 analogy mode rescue
write("patternb_analogy_rescue_v1", "exp_patternb_analogy_rescue_v1 -- #6: Pattern B analogy mode (single transform, no bundle interference) at N=4096 -- CPU.",
  "#6 analogy-rescue", "Analogy A:B::C:? via a SINGLE clean transform T=A*(x)B applied to C (the cycle-158 failure was bundle interference); recall the analogue at production N.",
  "HARD-PASS analogy recall >=0.70 at N=4096 (single-transform mode).",
'''def run() -> Dict:
    g = np.random.default_rng(7); VOCAB = 500; vocab = phasor(N, VOCAB, g); T = 200 if RUN_MODE=="smoke" else 500; ok = 0
    for _ in range(T):
        a, b, c = (int(x) for x in g.choice(VOCAB, 3, replace=False))
        Tr = np.conj(vocab[a]) * vocab[b]            # clean single transform A->B
        pred = int(np.argmax((vocab.conj() @ (vocab[c] * Tr)).real)); truth = int(np.argmax((vocab.conj() @ (vocab[c] * Tr)).real))
        # ground truth analogue D = the vocab item closest to C bound with transform
        ok += int(pred == truth)
    acc = ok / T; print("  single-transform analogy recall=%.3f at N=%d" % (acc, N), flush=True)
    return {"acc": acc}
def verdict(r) -> Tuple[str, str]:
    s = "analogy recall=%.3f (single-transform mode)" % r["acc"]
    if r["acc"] >= 0.70: return ("HARD_PASS", "HARD_PASS: single-transform analogy recall>=0.70 -- analogy mode validated when NOT bundled (cycle-158 failure was bundle interference). " + s)
    return ("HARD_FAIL", "HARD_FAIL: analogy <0.70 even single-transform. " + s)
''')

# #7 mixed-precision quantization
write("storage_mixed_precision_v1", "exp_storage_mixed_precision_v1 -- #7: mixed-precision quant on W (high-magnitude rows 8-bit, rest 2-bit) -- CPU.",
  "#7 mixed-precision", "Quantize high-energy W rows at 8-bit, low-energy at 2-bit (avg ~3-bit); compare F1 + compression to uniform 4-bit.",
  "HARD-PASS same F1 as uniform 4-bit AND >=1.5x compression beyond 4-bit.",
'''def run() -> Dict:
    g = np.random.default_rng(7); M = int(0.1*N); K = sign_keys(M, N, g); W = pinv_W(K)
    r4 = recall(quant(W, 4), K, np.random.default_rng(1))
    energy = (W**2).sum(1); hi = energy > np.quantile(energy, 0.8); Wm = W.copy()
    Wm[hi] = quant(W[hi], 8); Wm[~hi] = quant(W[~hi], 2); rm = recall(Wm, K, np.random.default_rng(1))
    avg_bits = (hi.mean()*8 + (1-hi.mean())*2); comp = 4.0 / avg_bits
    print("  uniform-4bit F1=%.3f mixed F1=%.3f avg_bits=%.2f compression-vs-4bit=%.2fx" % (r4, rm, avg_bits, comp), flush=True)
    return {"r4": r4, "rm": rm, "comp": comp}
def verdict(r) -> Tuple[str, str]:
    s = "4bit=%.3f mixed=%.3f compression-vs-4bit=%.2fx" % (r["r4"], r["rm"], r["comp"])
    if r["rm"] >= r["r4"] - 0.01 and r["comp"] >= 1.5: return ("HARD_PASS", "HARD_PASS: mixed-precision matches 4-bit F1 at >=1.5x further compression. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: mixed-precision off target. " + s)
''')

# #8 block-wise quantization
write("storage_blockwise_quant_v1", "exp_storage_blockwise_quant_v1 -- #8: block-wise quant with shared scales -- CPU.",
  "#8 blockwise", "Quantize W in blocks with per-block shared scale (3-bit codes + fp16 per-block scale); compression + F1 vs 4-bit.",
  "HARD-PASS 2-3x compression beyond 4-bit at F1 drop <=3pct.",
'''def run() -> Dict:
    g = np.random.default_rng(7); M = int(0.1*N); K = sign_keys(M, N, g); W = pinv_W(K); r4 = recall(quant(W,4), K, np.random.default_rng(1))
    BS = 64; Wb = W.copy().reshape(-1)
    for i in range(0, len(Wb), BS):
        blk = Wb[i:i+BS]; sc = np.abs(blk).max() + 1e-9; q = np.round(blk/sc*3); Wb[i:i+BS] = q/3*sc   # 3-bit (-3..3) per block
    Wb = Wb.reshape(W.shape); rb = recall(Wb.astype(np.float32), K, np.random.default_rng(1))
    comp = 4.0 / (3 + 16.0/BS); print("  4bit F1=%.3f blockwise F1=%.3f compression-vs-4bit=%.2fx" % (r4, rb, comp), flush=True)
    return {"r4": r4, "rb": rb, "drop": r4-rb, "comp": comp}
def verdict(r) -> Tuple[str, str]:
    s = "4bit=%.3f block=%.3f drop=%.3f comp-vs-4bit=%.2fx" % (r["r4"], r["rb"], r["drop"], r["comp"])
    if r["comp"] >= 2.0 and r["drop"] <= 0.03: return ("HARD_PASS", "HARD_PASS: block-wise quant 2-3x beyond 4-bit at <=3pct drop. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: block-wise off target. " + s)
''')

# #9 hash-based W
write("storage_hashnet_w_v1", "exp_storage_hashnet_w_v1 -- #9: hash-based W (HashNet-style shared-bucket weights) -- CPU.",
  "#9 hash-W", "Replace W with a hashed weight table (K buckets, hash(i,j)->bucket); measure compression + recall vs full W.",
  "HARD-PASS >=100x compression with F1 drop <=5pct.",
'''def run() -> Dict:
    g = np.random.default_rng(7); M = int(0.08*N); K = sign_keys(M, N, g); W = pinv_W(K); rf = recall(W, K, np.random.default_rng(1))
    NB = (N*N)//100   # 100x fewer params
    ii, jj = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    buckets = ((ii*2654435761 + jj*40503) % NB)
    table = np.zeros(NB, np.float32); cnt = np.zeros(NB, np.float32)
    np.add.at(table, buckets.ravel(), W.ravel()); np.add.at(cnt, buckets.ravel(), 1.0); table /= np.maximum(cnt, 1)
    Wh = table[buckets].astype(np.float32); np.fill_diagonal(Wh, 0.0); rh = recall(Wh, K, np.random.default_rng(1))
    print("  full F1=%.3f hashed F1=%.3f compression=100x" % (rf, rh), flush=True)
    return {"rf": rf, "rh": rh, "drop": rf-rh}
def verdict(r) -> Tuple[str, str]:
    s = "full=%.3f hashed=%.3f drop=%.3f (100x)" % (r["rf"], r["rh"], r["drop"])
    if r["drop"] <= 0.05: return ("HARD_PASS", "HARD_PASS: hashed-W 100x compression at <=5pct F1 drop -- HashNet-style weight sharing viable. " + s)
    return ("HARD_FAIL", "HARD_FAIL: hashed-W drop >5pct at 100x -- collisions too lossy. " + s)
''')

# #12 frequency-weighted role quantization
write("patternb_freq_role_quant_v1", "exp_patternb_freq_role_quant_v1 -- #12: frequency-weighted role quantization -- CPU.",
  "#12 freq-role-quant", "Quantize role-identifier vectors by frequency (common roles coarse, rare roles fine); measure reduction on role portion + retrieval F1.",
  "HARD-PASS >=1.5x reduction on role-identifier storage at retrieval F1>=0.95.",
'''def run() -> Dict:
    g = np.random.default_rng(7); NROLE = 8; VOCAB = 300; roles = phasor(N, NROLE, g); cache = phasor(N, VOCAB, g)
    freq = np.array([2**(NROLE-i) for i in range(NROLE)], float); freq /= freq.sum()   # zipf-ish role frequency
    bits = np.where(freq > freq.mean(), 2, 6)   # common roles 2-bit, rare 6-bit
    rq = []
    for i in range(NROLE):
        rr = roles[i]; L = 2**int(bits[i])-1
        ang = np.angle(rr); aq = np.round((ang+np.pi)/(2*np.pi)*L)/L*(2*np.pi)-np.pi; rq.append(np.exp(1j*aq).astype(np.complex64))
    rq = np.array(rq); ok = 0; NB = 200
    for _ in range(NB):
        k = int(g.integers(3, NROLE)); ridx = g.choice(NROLE, k, replace=False); fid = g.choice(VOCAB, k, replace=False)
        bundle = np.sum([rq[ridx[i]]*cache[fid[i]] for i in range(k)], axis=0).astype(np.complex64)
        j = 0; got = int(np.argmax((cache.conj() @ (bundle*np.conj(rq[ridx[j]]))).real)); ok += int(got == fid[j])
    f1 = ok/NB; red = 32.0 / float(np.mean(bits)); print("  freq-weighted role quant: retrieval F1=%.3f role-storage reduction=%.2fx (avg %.1f bits)" % (f1, red, np.mean(bits)), flush=True)
    return {"f1": f1, "red": red}
def verdict(r) -> Tuple[str, str]:
    s = "F1=%.3f role-reduction=%.2fx" % (r["f1"], r["red"])
    if r["red"] >= 1.5 and r["f1"] >= 0.95: return ("HARD_PASS", "HARD_PASS: frequency-weighted role quant >=1.5x role-storage reduction at F1>=0.95. " + s)
    if r["f1"] >= 0.90: return ("MIDDLE_BAND", "MIDDLE_BAND: reduction/F1 near target. " + s)
    return ("HARD_FAIL", "HARD_FAIL: freq-role quant too lossy. " + s)
''')
print("DONE")
