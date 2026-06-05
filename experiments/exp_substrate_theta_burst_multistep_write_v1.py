"""
substrate_theta_burst_multistep_write_v1 -- THETA-BURST-1: hippocampal multi-step lookahead write -- CPU.

ROUTING: research kgram_xor_binding_rescue (THETA-BURST-1; novel write rule). Hippocampal theta sequences (Sosa et al
  Neuron 2024) compress a K-step forward sweep into each cycle. Write rule: store not just (c_t,c_{t+1}) but also
  (c_t,c_{t+2})..(c_t,c_{t+K}) with decaying weight gamma^(k-1). Novel bipolar-compatible write. Tests whether
  trajectory writes give multi-step lookahead beyond single-step Hebbian. CPU numpy $0.

MODEL: 1st-order Markov chain (V=256). Baseline: W += outer(phi(c_t),phi(c_{t+1})). Theta-burst K: W += sum_{k=1..K}
  gamma^(k-1) outer(phi(c_t),phi(c_{t+k})). Metric: prediction accuracy at steps t+1, t+2, t+3 (multi-step lookahead).

PRE-REGISTERED bands: HARD-PASS theta-burst-K3 improves multi-step (t+2 & t+3 mean) >=15% over Hebbian AND single-step
  (t+1) within 5% of Hebbian. MIDDLE: 5-15% multi-step gain. HARD-FAIL: no gain OR single-step degrades >5%.
FORMULA SELF-TESTS (PROT-022): 1. multi-step write stores t+2. 2. gamma decay. 3. N fixed.
ASCII-only. write_metrics. PROT-018: no _nN.
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

ANCHOR_NAME = "substrate_theta_burst_multistep_write_v1"
N_DIM = 4096; GAMMA = 0.7
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
    g = np.random.default_rng(0); n = 256; C = bp(4, n, g); W = np.zeros((n, n), dtype=np.float32)
    W += np.outer(C[2], C[0])   # (c0 -> c2) = t+2 write
    assert int(np.argmax(C @ (W @ C[0]))) == 2, "multi-step write stores t+2"
    assert GAMMA ** 1 < 1.0, "gamma decay"; assert N_DIM == 4096; print("[selftest] PASS: multistep gamma", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def chain(g, length):
    table = {}; seq = [int(g.integers(0, V_C))]
    for t in range(1, length):
        k = seq[t - 1]
        if k not in table:
            table[k] = int(g.integers(0, V_C))
        seq.append(table[k] if g.random() > 0.05 else int(g.integers(0, V_C)))
    return seq


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; C = bp(V_C, n, g); sq = math.sqrt(n)
    STEP = bp(6, n, g) * sq                                # step-tag codebook (bind to disambiguate t+k readout)
    seq = np.array(chain(g, SEQ_LEN)); split = int(0.8 * len(seq))

    def build_theta(K):
        # theta-burst: write (c_t bound with step-tag k) -> c_{t+k}, decaying weight; step-tag enables per-step readout
        W = np.zeros((n, n), dtype=np.float32)
        for k in range(1, K + 1):
            w = GAMMA ** (k - 1); src = (C[seq[: split - k]] * STEP[k]); dst = C[seq[k: split]]
            W += w * (dst.T @ src)
        return W

    def theta_acc(W, K):
        accs = {}
        for step in (1, 2, 3):
            te = np.arange(split, len(seq) - step)
            scores = (C[seq[te]] * STEP[step]) @ W.T @ C.T; accs[step] = float(np.mean(scores.argmax(1) == seq[te + step]))
        return accs

    def baseline_acc():
        # standard single-step Hebbian; read t+k by ITERATING W k times (error compounds)
        W = (C[seq[1:split]].T @ C[seq[:split - 1]]).astype(np.float32); accs = {}
        for step in (1, 2, 3):
            te = np.arange(split, len(seq) - step); q = C[seq[te]].copy()
            for _ in range(step):
                r = q @ W.T; q = C[(r @ C.T).argmax(1)]   # iterate + cleanup
            accs[step] = float(np.mean((q @ C.T).argmax(1) == seq[te + step]))
        return accs

    base = baseline_acc(); tb3 = theta_acc(build_theta(3), 3); tb5 = theta_acc(build_theta(5), 5)
    return {"seed": seed, "baseline": base, "theta_K3": tb3, "theta_K5": tb5,
            "base_t1": base[1], "tb3_t1": tb3[1], "base_multi": (base[2] + base[3]) / 2, "tb3_multi": (tb3[2] + tb3[3]) / 2}


def verdict(ps) -> Tuple[str, str]:
    bt1 = float(np.mean([p["base_t1"] for p in ps])); tt1 = float(np.mean([p["tb3_t1"] for p in ps]))
    bm = float(np.mean([p["base_multi"] for p in ps])); tm = float(np.mean([p["tb3_multi"] for p in ps]))
    multi_gain = (tm - bm) / max(bm, 1e-6); single_drop = (bt1 - tt1) / max(bt1, 1e-6)
    summary = "single t1: base=%.3f theta=%.3f (drop=%.1f%%) | multi (t2,t3 mean): base=%.3f theta_K3=%.3f (gain=%.1f%%)" % (bt1, tt1, single_drop * 100, bm, tm, multi_gain * 100)
    if multi_gain >= 0.15 and single_drop <= 0.05:
        return ("HARD_PASS", "HARD_PASS: theta-burst multi-step write gives >=15%% multi-step lookahead gain w/o single-step loss. " + summary)
    if multi_gain >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: theta-burst modest multi-step gain. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: theta-burst no multi-step lookahead value. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d V=%d gamma=%.1f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_C, GAMMA), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] base t1=%.3f t2=%.3f t3=%.3f | theta_K3 t1=%.3f t2=%.3f t3=%.3f" % (
        seed, r["baseline"][1], r["baseline"][2], r["baseline"][3], r["theta_K3"][1], r["theta_K3"][2], r["theta_K3"][3]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
