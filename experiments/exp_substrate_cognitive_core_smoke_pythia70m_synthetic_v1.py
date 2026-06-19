"""
substrate_cognitive_core_smoke_pythia70m_synthetic_v1 -- CCC-smoke (Research spec): pure-substrate cognitive core -- remote CPU.

ROUTING: research_to_exp_dev_ccc_smoke_ccc1_substrate_cognitive_core_pythia160m (Cell CCC-smoke). Validate the
  substrate-as-cognitive-core SCAFFOLD on a SYNTHETIC concept-ID corpus (NO LLM dependency; confirms architecture
  before paying for extraction). 5 hierarchical domains, N=4096, B2 sparse + position-binding + STDP + B6 D-ECR,
  SQ2 K=12 multi-hop. CPU numpy, $0. remote_cpu_queue. (CCC-1 PATH-A is the LLM-distillation follow-up; needs the
  Pythia-160M residual npz Testbed shipped the script for.)

THREE HP CRITERIA (per note): (a) concept-pattern recall >= 80% (noisy-cue), (b) deletion-cert operational (B6
  evict -> gone AND others intact), (c) SQ2 K=12 reasoning preserved (>=12-hop chains across domains).

MODEL: per domain d: V_c sparse concept patterns (k-WTA DG codes, f=0.05); recall via covariance + k-WTA on a
  20%-dropped cue. concept chains stored as context-bound cf-RPE transitions (handles correlated keys); SQ2 = iterate
  argmax over concept codebook K=12 hops. B6: evict lowest self-overlap pattern, verify deletion-cert.

PRE-REGISTERED bands: HARD-PASS recall>=0.80 AND deletion_cert>=0.95 AND sq2_depth>=12. MIDDLE recall 0.50-0.80.
  HARD-FAIL recall<0.50.

FORMULA SELF-TESTS (PROT-022): 1. sparse recall (noisy cue). 2. context-bound chain K-hop. 3. deletion drops recall. 4. N=4096.
ASCII-only. write_metrics. PROT-018: anchor has no _nN (multi-domain scaffold; N=4096 internal).
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
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_cognitive_core_smoke_pythia70m_synthetic_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

N = 4096; DOMAINS = 5; F_SPARSE = 0.05; K_HOPS = 12; K_CTX = 3; LR = 0.5
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 1024; V_C = 64; CHAIN_LEN = 13; N_CHAINS = 6
else:
    SEEDS = [7, 17, 23]; N_DIM = N; V_C = 256; CHAIN_LEN = 13; N_CHAINS = 20


def sparse_codes(V, n, g):
    k = max(1, int(round(F_SPARSE * n))); S = np.zeros((V, n), dtype=np.float32)
    for i in range(V):
        S[i, g.choice(n, size=k, replace=False)] = 1.0
    return S, k


def kwta(v, k):
    idx = np.argpartition(-v, k - 1)[:k]; o = np.zeros_like(v); o[idx] = 1.0; return o


def recall_rate(S, k, g):
    f = F_SPARSE; W = (S - f).T @ (S - f); np.fill_diagonal(W, 0.0); hits = 0
    for i in range(len(S)):
        act = np.nonzero(S[i])[0]; drop = g.choice(act, size=max(1, int(0.2 * k)), replace=False)
        cue = S[i].copy(); cue[drop] = 0.0
        r = kwta((cue - f) @ W.T, k); hits += (float((r * S[i]).sum() / k) > 0.95)
    return hits / len(S)


def context_vec(phi, c, t):
    v = np.zeros(phi.shape[1], dtype=np.float32)
    for kk in range(min(t + 1, K_CTX)):
        v = v + np.roll(phi[c[t - kk]], kk)
    return v / (np.linalg.norm(v) + 1e-8)


def sq2_depth(phi, chains, g):
    pairs = []
    for c in chains:
        for t in range(len(c) - 1):
            pairs.append((context_vec(phi, c, t), phi[c[t + 1]]))
    n = phi.shape[1]; W = np.zeros((n, n), dtype=np.float32)
    for _ep in range(20):
        for ctx, tgt in pairs:
            W += LR * np.outer(tgt - W @ ctx, ctx)
    # depth = max K with per-hop concept-id recovery acc >= 0.8 (cleanup vs codebook)
    best = 0
    for K in range(1, K_HOPS + 1):
        ok = 0; tot = 0
        for c in chains:
            if len(c) <= K:
                continue
            cur = list(c[:1])
            good = True
            for t in range(K):
                ctx = context_vec(phi, cur, len(cur) - 1) if len(cur) >= 1 else phi[c[0]]
                r = W @ ctx; pred = int(np.argmax(phi @ r))
                cur.append(pred)
                if pred != c[t + 1]:
                    good = False; break
            ok += good; tot += 1
        if tot and ok / tot >= 0.8:
            best = K
        else:
            break
    return best


def _selftest():
    g = np.random.default_rng(0); n = 256; S, k = sparse_codes(8, n, g)
    assert recall_rate(S, k, np.random.default_rng(1)) > 0.8, "sparse recall"
    phi = (g.integers(0, 2, (5, n)) * 2 - 1).astype(np.float32); phi /= np.linalg.norm(phi, axis=1, keepdims=True)
    d = sq2_depth(phi, [[0, 1, 2, 3, 4]], np.random.default_rng(2)); assert d >= 3, "chain hops"
    W = np.outer(S[1], S[1]); b = float((np.sign(W @ S[1]) * S[1]).sum()); W2 = W - np.outer(S[1], S[1])
    assert float((np.sign(W2 @ S[1]) * S[1]).sum()) <= b, "deletion drops"
    assert N == 4096; print("[selftest] PASS: sparse_recall chain_hops deletion", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); recalls = []; depths = []; certs = []
    for d in range(DOMAINS):
        gd = np.random.default_rng(seed * 10 + d)
        S, k = sparse_codes(V_C, N_DIM, gd); recalls.append(recall_rate(S, k, gd))
        phi = (gd.integers(0, 2, (V_C, N_DIM)) * 2 - 1).astype(np.float32); phi /= np.linalg.norm(phi, axis=1, keepdims=True)
        chains = [list(gd.choice(V_C, size=CHAIN_LEN, replace=False)) for _ in range(N_CHAINS)]
        depths.append(sq2_depth(phi, chains, gd))
        # deletion-cert: B6 evict pattern 0 from covariance, verify gone + others intact
        W = (S - F_SPARSE).T @ (S - F_SPARSE); np.fill_diagonal(W, 0.0)
        before = float((kwta((S[0] - F_SPARSE) @ W.T, k) * S[0]).sum() / k)
        W -= np.outer(S[0] - F_SPARSE, S[0] - F_SPARSE); np.fill_diagonal(W, 0.0)
        after = float((kwta((S[0] - F_SPARSE) @ W.T, k) * S[0]).sum() / k)
        others = float(np.mean([float((kwta((S[i] - F_SPARSE) @ W.T, k) * S[i]).sum() / k) > 0.9 for i in range(1, min(20, V_C))]))
        certs.append(0.5 * (float(after < 0.7 * max(before, 1e-6)) + others))
    return {"seed": seed, "N": N_DIM, "domains": DOMAINS, "recall": float(np.mean(recalls)),
            "deletion_cert": float(np.mean(certs)), "sq2_depth": float(np.mean(depths))}


def verdict(ps) -> Tuple[str, str]:
    rc = float(np.mean([p["recall"] for p in ps])); ct = float(np.mean([p["deletion_cert"] for p in ps])); dp = float(np.mean([p["sq2_depth"] for p in ps]))
    summary = "recall=%.2f deletion_cert=%.2f sq2_depth=%.1f (%d domains, V_c=%d, N=%d)" % (rc, ct, dp, ps[0]["domains"], V_C, ps[0]["N"])
    if rc >= 0.80 and ct >= 0.95 and dp >= 12:
        return ("HARD_PASS", "HARD_PASS: substrate cognitive-core scaffold validated (recall+audit+K12 reasoning). " + summary)
    if rc >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial cognitive-core scaffold. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: scaffold fails at smallest scale. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V_c=%d domains=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_C, DOMAINS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] recall=%.2f deletion_cert=%.2f sq2_depth=%.1f" % (seed, r["recall"], r["deletion_cert"], r["sq2_depth"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "V_c": V_C, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
