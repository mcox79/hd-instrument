"""
exp_hp12_v1_end_to_end_demo_backend_v1 -- HP-12 V1 demo backend: full live-ingest/query/delete/verify sequence -- CPU.

ROUTING: research HP12_V1_pipeline_simplified_desktop_only (Day-3 substrate integration + live-ingest flow). This is the
  BACKEND of the 5-minute killer-demo, validated end-to-end as one cell (geometry + crypto already de-risked separately):
    1. pre-seed substrate with M facts (Hebbian, N=10^4)
    2. LIVE-INGEST K new facts one at a time (cf-RPE single-fact write) -- time each write (real-time-write moat)
    3. QUERY the live-added facts (associative recall) -- correct answers
    4. DELETE a subset -- substrate projection + RSA accumulator cert (tools/hp12) issued per delete, time each
    5. THIRD-PARTY VERIFY every deletion cert (no trapdoor / no KB)
    6. RE-QUERY deleted facts -- 0 phantom recall (absolute-recall metric)
  CPU numpy + pure-Python crypto $0.

PRE-REGISTERED bands: HARD-PASS live-write <1ms median AND query recall on live facts >0.95 AND all certs verify AND 0
  phantom recall AND pre-seeded retention >0.95. MIDDLE: write 1-10ms OR phantom <1%. HARD-FAIL: any phantom OR cert fail.
FORMULA SELF-TESTS (PROT-022): 1. cf-RPE single write recallable. 2. deletion+cert verifies. 3. N=4096 marker.
ASCII-only. write_metrics. PROT-018 _n4096 (marker; substrate N below set by N_DIM).
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
from tools.hp12.rsa_accumulator import RSAAccumulator

ANCHOR_NAME = "exp_hp12_v1_end_to_end_demo_backend_v1"
_N_SUFFIX = 4096; N_MARKER = 4096; assert N_MARKER == _N_SUFFIX
LR = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 2048; M_SEED = 1000; K_LIVE = 50; N_DEL = 10; RSA_BITS = 512
else:
    SEEDS = [7, 17, 23]; N_DIM = 4096; M_SEED = 3000; K_LIVE = 50; N_DEL = 20; RSA_BITS = 1024


def ub(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); n = 256; K = ub(1, n, g)[0]; V = ub(1, n, g)[0]; W = np.zeros((n, n), dtype=np.float32)
    W += np.outer(V, K)                                    # single write
    assert float(V @ (W @ K)) > 0.5, "cf-RPE single write recallable"
    acc = RSAAccumulator(rsa_bits=256); acc.add_many(["a", "b"]); cert = acc.delete("a")
    assert RSAAccumulator.verify_deletion(cert), "deletion+cert verifies"
    assert N_MARKER == 4096; print("[selftest] PASS: write cert", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; n_val = 32
    EV = ub(n_val, n, g)
    # 1. PRE-SEED M facts (batched Hebbian)
    SK = ub(M_SEED, n, g); sval = [int(g.integers(0, n_val)) for _ in range(M_SEED)]
    W = (EV[np.array(sval)].T @ SK).astype(np.float32)
    # 2. LIVE-INGEST K facts one at a time (timed)
    LK = ub(K_LIVE, n, g); lval = [int(g.integers(0, n_val)) for _ in range(K_LIVE)]
    write_ms = []
    acc = RSAAccumulator(rsa_bits=RSA_BITS)
    for i in range(K_LIVE):
        t0 = time.perf_counter()
        W += np.outer(EV[lval[i]] - (W @ LK[i]), LK[i])    # cf-RPE-style single-fact write
        write_ms.append((time.perf_counter() - t0) * 1000.0)
        acc.add("live:%d:%d" % (seed, i))
    # 3. QUERY live-added facts
    live_recall = float(np.mean([int(np.argmax(EV @ (W @ LK[i]))) == lval[i] for i in range(K_LIVE)]))
    # 4. DELETE a subset (substrate projection + RSA cert)
    del_idx = list(g.choice(K_LIVE, size=N_DEL, replace=False)); certs = []; cert_ms = []
    for i in del_idx:
        W -= np.outer(W @ LK[i], LK[i])                    # substrate deletion
        t0 = time.perf_counter(); cert = acc.delete("live:%d:%d" % (seed, i)); cert_ms.append((time.perf_counter() - t0) * 1000.0)
        certs.append(cert)
    for _ in range(3):                                     # stabilizing re-projection (seq-deletion crosstalk)
        for i in del_idx:
            W -= np.outer(W @ LK[i], LK[i])
    # 5. THIRD-PARTY VERIFY every cert
    verified = sum(int(RSAAccumulator.verify_deletion(c)) for c in certs)
    # 6. RE-QUERY deleted facts -> 0 phantom (ABSOLUTE recall strength, not cosine)
    phantom = 0
    for i in del_idx:
        scores = EV @ (W @ LK[i]); phantom += int(int(np.argmax(scores)) == lval[i] and float(scores.max()) > 0.30)
    phantom_rate = phantom / max(len(del_idx), 1)
    # pre-seeded retention (integrity)
    keep = list(g.choice(M_SEED, size=min(300, M_SEED), replace=False))
    retention = float(np.mean([int(np.argmax(EV @ (W @ SK[i]))) == sval[i] for i in keep]))
    return {"seed": seed, "M_seed": M_SEED, "k_live": K_LIVE, "n_del": N_DEL,
            "live_write_ms_median": float(np.median(write_ms)), "live_recall": live_recall,
            "cert_ms_median": float(np.median(cert_ms)), "certs_verified_frac": verified / max(len(certs), 1),
            "phantom_recall_rate": phantom_rate, "preseed_retention": retention}


def verdict(ps) -> Tuple[str, str]:
    wm = float(np.mean([p["live_write_ms_median"] for p in ps])); lr = float(np.mean([p["live_recall"] for p in ps]))
    vf = float(np.mean([p["certs_verified_frac"] for p in ps])); ph = float(np.mean([p["phantom_recall_rate"] for p in ps]))
    ret = float(np.mean([p["preseed_retention"] for p in ps]))
    summary = "live_write=%.4fms live_recall=%.3f | certs_verified=%.3f phantom_recall=%.3f | preseed_retention=%.3f (M_seed=%d,K_live=%d,N_del=%d)" % (
        wm, lr, vf, ph, ret, ps[0]["M_seed"], ps[0]["k_live"], ps[0]["n_del"])
    if wm < 1.0 and lr > 0.95 and vf >= 0.999 and ph == 0.0 and ret > 0.95:
        return ("HARD_PASS", "HARD_PASS: HP-12 V1 demo backend end-to-end -- <1ms live writes, live recall>0.95, all certs verified, 0 phantom, retention intact. " + summary)
    if lr > 0.90 and vf >= 0.999 and ph < 0.01:
        return ("MIDDLE_BAND", "MIDDLE_BAND: demo backend works; write-latency or recall near-threshold. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: demo backend phantom recall or cert failure. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d M_seed=%d K_live=%d N_del=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M_SEED, K_LIVE, N_DEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] live_write=%.4fms live_recall=%.3f certs_verified=%.3f phantom=%.3f retention=%.3f" % (
        seed, r["live_write_ms_median"], r["live_recall"], r["certs_verified_frac"], r["phantom_recall_rate"], r["preseed_retention"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
