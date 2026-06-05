"""
substrate_kgram_xor_context_binding_v1 -- K2-XOR-1: rescue bigram-level prediction via XOR k-gram context -- CPU.

ROUTING: research kgram_xor_binding_rescue (K2-XOR-1, highest priority). EX-CONCEPT honest finding: substrate next-
  token is bigram-class because W*phi(c_t) is linear in the SINGLE last token. Rescue (retrieval-side ONLY, write
  rule UNCHANGED, all moats preserved): encode the k-gram context into ONE vector via XOR-binding BEFORE the
  matrix-vector product -> k-th order Markov. Prior position-binding extctx failed (1/K SNR penalty at flat codebook);
  XOR context binding avoids that. CPU numpy $0, ~30s.

MODEL: synthetic 2nd-order Markov chain (c_{t+1} depends on (c_{t-1},c_t)). Variants (standard Hebbian write on the
  context key): K1 query=phi(c_t); K2 query=phi(c_{t-1})*phi(c_t) [XOR bind]; K3 query=phi(c_{t-2})*phi(c_{t-1})*phi(c_t).
  Next-token accuracy on held-out 20%.

PRE-REGISTERED bands: HARD-PASS acc(K2) >= 1.20x acc(K1). MIDDLE: 1.05-1.20x. HARD-FAIL: <=1.02x (substrate fundamentally co-occurrence-bigram).
FORMULA SELF-TESTS (PROT-022): 1. XOR bind self-inverse. 2. k-gram key distinguishes contexts. 3. N=4096.
ASCII-only. write_metrics. PROT-018 _n -- N fixed 4096 via config.
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

ANCHOR_NAME = "substrate_kgram_xor_context_binding_v1"
N_DIM = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; V_C = 256; SEQ_LEN = 4000
else:
    SEEDS = [7, 17, 23]; V_C = 256; SEQ_LEN = 8000


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); n = 256; C = bp(3, n, g) * math.sqrt(n)   # un-normalize for XOR self-inverse check
    b = C[0] * C[1]; assert np.allclose((b * C[1]) / n, C[0] / n, atol=1e-4), "XOR bind self-inverse"
    k_ab = C[0] * C[1]; k_cb = C[2] * C[1]
    assert float((k_ab * k_cb).sum()) < float((k_ab * k_ab).sum()), "k-gram key distinguishes contexts"
    assert N_DIM == 4096; print("[selftest] PASS: xor kgram", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def make_2nd_order_chain(g, length):
    # 2nd-order transition: next depends on (prev2, prev1). Deterministic-ish table + small noise.
    table = {}
    seq = [int(g.integers(0, V_C)), int(g.integers(0, V_C))]
    for t in range(2, length):
        key = (seq[t - 2], seq[t - 1])
        if key not in table:
            table[key] = int(g.integers(0, V_C))
        nxt = table[key] if g.random() > 0.05 else int(g.integers(0, V_C))   # 5% noise
        seq.append(nxt)
    return seq


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; C = bp(V_C, n, g) * math.sqrt(n)   # scale so XOR products stay ~unit-ish
    seq = make_2nd_order_chain(g, SEQ_LEN); split = int(0.8 * len(seq))
    sq = math.sqrt(n)

    Cn = C / sq                                           # normalized rows (unit)
    seqa = np.array(seq)

    def all_keys(k):
        # key[t] = normalize(Cn[seq[t]] * Cn[seq[t-1]] * ... * Cn[seq[t-k+1]]) -- XOR k-gram context bind
        ks = Cn[seqa].copy()
        for j in range(1, k):
            ks[j:] = ks[j:] * Cn[seqa[:-j]]
        ks /= (np.linalg.norm(ks, axis=1, keepdims=True) + 1e-8)
        return ks

    res = {}
    for k in (1, 2, 3):
        keys = all_keys(k); tr = np.arange(k - 1, split - 1); te = np.arange(max(k - 1, split), len(seq) - 1)
        W = (Cn[seqa[tr + 1]].T @ keys[tr]).astype(np.float32)        # batched Hebbian write
        scores = keys[te] @ W.T @ C.T                                 # (|te|, V) prediction scores
        preds = scores.argmax(1)
        res["K%d_acc" % k] = float(np.mean(preds == seqa[te + 1]))
    res["seed"] = seed; res["ratio_K2_K1"] = float(res["K2_acc"] / max(res["K1_acc"], 1e-6))
    res["ratio_K3_K1"] = float(res["K3_acc"] / max(res["K1_acc"], 1e-6))
    return res


def verdict(ps) -> Tuple[str, str]:
    k1 = float(np.mean([p["K1_acc"] for p in ps])); k2 = float(np.mean([p["K2_acc"] for p in ps])); k3 = float(np.mean([p["K3_acc"] for p in ps]))
    r2 = k2 / max(k1, 1e-6)
    summary = "K1=%.3f K2=%.3f K3=%.3f | K2/K1=%.2fx K3/K1=%.2fx (2nd-order chain, V=%d)" % (k1, k2, k3, r2, k3 / max(k1, 1e-6), V_C)
    if r2 >= 1.20:
        return ("HARD_PASS", "HARD_PASS: XOR k-gram context binding rescues k-th-order prediction >=1.2x bigram (retrieval-side only; all moats preserved). " + summary)
    if r2 >= 1.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: XOR context binding modest 1.05-1.2x. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: XOR context no benefit (substrate fundamentally co-occurrence-bigram). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V=%d seq=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_C, SEQ_LEN), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] K1=%.3f K2=%.3f K3=%.3f (K2/K1=%.2fx)" % (seed, r["K1_acc"], r["K2_acc"], r["K3_acc"], r["ratio_K2_K1"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
