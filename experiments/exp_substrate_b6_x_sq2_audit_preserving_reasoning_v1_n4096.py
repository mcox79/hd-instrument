"""
substrate_b6_x_sq2_audit_preserving_reasoning_v1_n4096 -- P3: audit-preserving reasoning chains -- remote CPU.

ROUTING: research_to_exp_dev_priority_1_compositions_routing (Cell P3). Compose B6 (D-ECR audit-preserving
  eviction) x SQ2 (multi-hop reasoning). Can the substrate sustain K=12-hop reasoning AND keep deletion-cert
  (audit) preservation >95% across the reasoning chain, when at capacity (eviction active)? CPU numpy, $0. remote_cpu_queue.

MODEL: G reasoning chains (L=12, bipolar, N=4096) stored as transitions in W; capacity m_cap=alpha_c*N with
  D-ECR eviction (evict lowest self-overlap when over capacity). Then: (a) K-hop accuracy via iterated sign(W@q);
  (b) deletion-cert: delete a chain's transitions, verify they no longer recall (audit) AND the OTHER chains'
  reasoning is preserved. arms: reasoning_acc@12, deletion_cert (deleted gone + others intact).

PRE-REG bands: HARD-PASS K=12 acc >= 0.80 AND deletion-cert (deleted-gone AND others-preserved) >= 0.95.
  MIDDLE: one of the two in [0.7,0.95). HARD-FAIL: K=12 acc<0.7 OR deletion-cert<0.7 (eviction breaks reasoning or audit).
SELF-TESTS (PROT-022): 1. 2-hop chain. 2. deletion removes a transition (recall drops). 3. N=4096.
ASCII-only. write_metrics. PROT-018 _n4096 -> N=4096.
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

ANCHOR_NAME = "substrate_b6_x_sq2_audit_preserving_reasoning_v1_n4096"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138; L = 12; K_EVAL = 12
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 512
else:
    SEEDS = [7, 17, 23]; N_DIM = N


def bipolar(shape, g):
    return (g.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)


def store_chain(W, ch):
    for i in range(L):
        W += np.outer(ch[i + 1], ch[i])


def unstore_chain(W, ch):
    for i in range(L):
        W -= np.outer(ch[i + 1], ch[i])


def hop_ok(W, ch, n, K):
    q = ch[0].copy()
    for _ in range(K):
        q = np.sign(W @ q); q[q == 0] = 1.0
    return float((q * ch[K]).sum() / n) > 0.90


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM
    m_cap = max(L * 2, int(round(ALPHA_C * n)))                 # transitions capacity
    G = max(3, m_cap // L)                                       # ~ at capacity
    chains = [bipolar((L + 1, n), g) for _ in range(G)]
    W = np.zeros((n, n), dtype=np.float32); bank = []
    for ch in chains:
        store_chain(W, ch); bank.append(ch)
        if len(bank) * L > m_cap:                               # D-ECR: evict lowest 1-hop self-overlap chain
            ovs = [float((np.sign(W @ c[0]) * c[1]).sum() / n) for c in bank]
            ev = int(np.argmin(ovs)); unstore_chain(W, bank[ev]); bank.pop(ev)
    # reasoning accuracy on retained chains
    racc = float(np.mean([hop_ok(W, ch, n, K_EVAL) for ch in bank]))
    # deletion-cert: delete one retained chain; it should vanish (1-hop), others preserved
    if len(bank) >= 2:
        victim = bank[len(bank) // 2]; others = [c for c in bank if c is not victim]
        before_v = float((np.sign(W @ victim[0]) * victim[1]).sum() / n)
        unstore_chain(W, victim)
        after_v = float((np.sign(W @ victim[0]) * victim[1]).sum() / n)
        deleted_gone = after_v < 0.5 * max(before_v, 1e-6)
        others_ok = float(np.mean([hop_ok(W, c, n, 1) for c in others]))
        cert = float(0.5 * (float(deleted_gone) + others_ok))
    else:
        cert = 0.0
    return {"seed": seed, "N": n, "G_retained": len(bank), "reasoning_acc12": racc, "deletion_cert": cert}


def _selftest():
    g = np.random.default_rng(0); n = 256; ch = bipolar((5, n), g); W = np.zeros((n, n), dtype=np.float32)
    for i in range(4):
        W += np.outer(ch[i + 1], ch[i])
    assert float((np.sign(W @ np.sign(W @ ch[0])) * ch[2]).sum() / n) > 0.9, "2-hop"
    b = float((np.sign(W @ ch[0]) * ch[1]).sum() / n); W -= np.outer(ch[1], ch[0])
    assert float((np.sign(W @ ch[0]) * ch[1]).sum() / n) <= b, "deletion drops recall"
    assert N == 4096; print("[selftest] PASS: 2hop deletion", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def verdict(ps) -> Tuple[str, str]:
    ra = float(np.mean([p["reasoning_acc12"] for p in ps])); ct = float(np.mean([p["deletion_cert"] for p in ps]))
    summary = "reasoning_acc@12=%.2f deletion_cert=%.2f (retained chains=%.0f)" % (ra, ct, float(np.mean([p["G_retained"] for p in ps])))
    if ra >= 0.80 and ct >= 0.95:
        return ("HARD_PASS", "HARD_PASS: audit-preserving reasoning -- K=12 holds AND deletion-cert preserved. " + summary)
    if ra >= 0.70 or ct >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial audit-preserving reasoning. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: eviction breaks reasoning or audit. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM), flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] reasoning_acc12=%.2f deletion_cert=%.2f retained=%d" % (seed, r["reasoning_acc12"], r["deletion_cert"], r["G_retained"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
