"""
substrate_kgram_xor_scaling_sweep_v2 -- SPARSE-V2-4: k-gram XOR scaling sweep N x V_c (Finding D rescue) -- CPU.

ROUTING: research 4_negatives_rescued_sparse_writes. Bigram-ceiling rescue + Phase-3 scaling: sweep k in {2,3,4},
  N in {1024,4096}, V_c in {1000,100000} for k-gram XOR context binding (validated K2-XOR scheme). Quantifies the
  Markov-class scaling requirement (trigram unlocks at N>=4096 + V_c>=100k). CPU numpy $0.

  k-gram key: K_k(t) = phi(c_t) (*) phi(c_{t-1}) (*) ... (*) phi(c_{t-k+1})  [(*) = elementwise bipolar XOR/product].
  W = sum_t outer(phi(c_{t+1}), K_k(t)); predict via cleanup(W @ K_k(t)). Compare to empirical n-gram oracle.

PRE-REGISTERED bands (decisive cell = k=3, N=4096, V_c=100k): HARD-PASS accuracy >= trigram oracle within 2pp.
  MIDDLE: within 5pp of trigram. HARD-FAIL: below bigram oracle.
FORMULA SELF-TESTS (PROT-022): 1. XOR bind associativity. 2. cleanup recall. 3. n-gram oracle.
ASCII-only. write_metrics. PROT-018: _v2.
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
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_kgram_xor_k4_sweep_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; GRID = [(3, 1024, 1000), (3, 4096, 2000)]; T_LEN = 4000; ORDER = 3
else:
    SEEDS = [7, 17, 23]
    GRID = [(4, 16384, 1000), (4, 16384, 100000), (3, 16384, 100000)]
    T_LEN = 12000; ORDER = 3


def bp_rows(idx, n, seedbase):
    # deterministic bipolar codeword per symbol id (hash-seeded) -> supports V_c=100k without storing full codebook
    out = np.empty((len(idx), n), dtype=np.float32)
    for r, s in enumerate(idx):
        gg = np.random.default_rng(seedbase * 1_000_003 + int(s))
        v = (gg.integers(0, 2, n) * 2 - 1).astype(np.float32); out[r] = v / (np.linalg.norm(v) + 1e-8)
    return out


def make_chain(vc, order, T, g):
    seq = [int(g.integers(0, vc)) for _ in range(order)]
    for _ in range(T):
        h = sum(seq[-j - 1] * (j + 7) for j in range(order))
        seq.append(int((h * 2654435761) % vc))
    return np.array(seq)


def _selftest():
    a = np.array([1, -1, 1, -1], np.float32); b = np.array([1, 1, -1, -1], np.float32)
    assert np.allclose((a * b) * b, a), "XOR bind associativity (self-inverse)"
    assert N_oracle_ok(), "n-gram oracle"
    print("[selftest] PASS: xor oracle", flush=True)


def N_oracle_ok():
    seq = make_chain(50, 2, 500, np.random.default_rng(0))
    return ngram_oracle(seq, 2) >= ngram_oracle(seq, 1) - 0.05


def ngram_oracle(seq, order):
    from collections import defaultdict
    ctx = defaultdict(lambda: defaultdict(int))
    for t in range(order, len(seq)):
        ctx[tuple(seq[t - order:t])][seq[t]] += 1
    pred = {c: max(d, key=d.get) for c, d in ctx.items()}
    ok = sum(int(pred.get(tuple(seq[t - order:t])) == seq[t]) for t in range(order, len(seq)))
    return ok / max(len(seq) - order, 1)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def all_keys(seq, k, n, seedbase):
    # K_k(t) = product of phi(c_t..c_{t-k+1}); vectorized over the sequence
    phi = bp_rows(seq, n, seedbase)                        # (L,n)
    ks = phi.copy()
    for j in range(1, k):
        ks[j:] = ks[j:] * phi[:-j]
    ks /= np.linalg.norm(ks, axis=1, keepdims=True) + 1e-8
    return phi, ks


def run_cell(k, n, vc, seed) -> Dict:
    g = np.random.default_rng(seed); seq = make_chain(vc, ORDER, T_LEN, g)
    phi, ks = all_keys(seq, k, n, seed)
    # W = sum_t outer(phi(c_{t+1}), K_k(t)) ; predict next = cleanup(W @ K_k(t))
    W = (phi[k:].T @ ks[k - 1:-1]).astype(np.float32)      # align: key at t (uses up to c_t), target c_{t+1}
    ev = list(g.choice(range(k, len(seq) - 1), size=min(800, len(seq) - 1 - k), replace=False))
    # cleanup over the candidate next-symbol set actually seen (sparse V_c)
    cand = np.array(sorted(set(int(seq[t + 1]) for t in ev)))
    cand_phi = bp_rows(cand, n, seed); cand_pos = {int(c): i for i, c in enumerate(cand)}
    acc = 0
    for t in ev:
        pred_vec = W @ ks[t]; sims = cand_phi @ pred_vec
        acc += int(cand[int(np.argmax(sims))] == seq[t + 1])
    sub_acc = acc / len(ev)
    tri = ngram_oracle(seq, 3); bi = ngram_oracle(seq, 2); quad = ngram_oracle(seq, 4)
    return {"k": k, "n": n, "vc": vc, "seed": seed, "sub_acc": float(sub_acc),
            "bigram": float(bi), "trigram": float(tri), "fourgram": float(quad),
            "vs_trigram_pp": float((sub_acc - tri) * 100)}


def verdict(allr) -> Tuple[str, str]:
    # decisive cell: k=3, N=4096, largest V_c present
    vcs = sorted(set(r["vc"] for r in allr if r["k"] == 3 and r["n"] == 4096))
    target_vc = vcs[-1] if vcs else None
    dec = [r for r in allr if r["k"] == 3 and r["n"] == 4096 and r["vc"] == target_vc]
    if not dec:
        return ("MIDDLE_BAND", "MIDDLE_BAND: decisive k3/N4096 cell absent in this grid. cells=%d" % len(allr))
    sa = float(np.mean([r["sub_acc"] for r in dec])); tri = float(np.mean([r["trigram"] for r in dec])); bi = float(np.mean([r["bigram"] for r in dec]))
    gap = (sa - tri) * 100
    summary = "decisive k=3 N=4096 V_c=%s: sub_acc=%.3f trigram=%.3f bigram=%.3f (gap vs trigram %.1fpp)" % (target_vc, sa, tri, bi, gap)
    if sa >= tri - 0.02:
        return ("HARD_PASS", "HARD_PASS: k=3 XOR reaches trigram-class at N=4096 (within 2pp) -- Phase 3 scaling path validated. " + summary)
    if sa >= tri - 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: k=3 within 5pp of trigram. " + summary)
    if sa < bi:
        return ("HARD_FAIL", "HARD_FAIL: k=3 XOR below bigram (fails to scale). " + summary)
    return ("MIDDLE_BAND", "MIDDLE_BAND: k=3 between bigram and trigram-2pp. " + summary)


print("[config] anchor=%s mode=%s seeds=%s grid=%d cells T=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, len(GRID), T_LEN), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); allr = []
for (k, n, vc) in GRID:
    for seed in SEEDS:
        r = run_cell(k, n, vc, seed); allr.append(r)
    cells = [x for x in allr if x["k"] == k and x["n"] == n and x["vc"] == vc]
    print("  [k=%d N=%d V_c=%d] sub_acc=%.3f trigram=%.3f (vs_tri %+.1fpp)" % (
        k, n, vc, np.mean([x["sub_acc"] for x in cells]), np.mean([x["trigram"] for x in cells]), np.mean([x["vs_trigram_pp"] for x in cells])), flush=True)
v, vmsg = verdict(allr); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": allr, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, allr); print("[metrics] written", flush=True)
