"""
exp_hp12_v1_demo_scale_10k_facts_v1 -- HP-12 V1 demo at TRUE scale (10K pre-seeded + 50 live, N=10^4) -- CPU.

ROUTING: research HP12_V1 (V1 sizing: 10K pre-seeded + 50 live-ingested is optimal). Validates the demo backend +
  API + crypto at the ACTUAL demo scale (N=10^4 substrate, 10000 facts) rather than the 1-3K smoke scale: live-write
  latency, query recall, certified deletion + third-party verify + 0 phantom recall, retention. CPU numpy +
  pure-Python/gmpy2 crypto $0. (Dense W at N=10^4 ~ 400MB fp32; fits RAM.)

PRE-REGISTERED bands: HARD-PASS query recall >0.95 AND all certs verify AND 0 phantom AND retention >0.95 (live-write
  latency reported, ms-scale = real-time moat). MIDDLE: phantom <1% OR recall>0.90. HARD-FAIL: phantom OR cert fail.
FORMULA SELF-TESTS (PROT-022): 1. API post+query. 2. delete+verify. 3. N marker.
ASCII-only. write_metrics. PROT-018: _v1.
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
from tools.hp12.api import SubstrateKB

ANCHOR_NAME = "exp_hp12_v1_demo_scale_10k_facts_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 4096; M_SEED = 1500; K_LIVE = 50; N_DEL = 20
else:
    SEEDS = [7, 17, 23]; N_DIM = 10000; M_SEED = 10000; K_LIVE = 50; N_DEL = 30


def kv(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32); return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); kb = SubstrateKB(256, 8, rsa_bits=128, seed=0); K = kv(3, 256, g)
    kb.post_fact("a", K[0], 2); assert kb.query(K[0])["value_id"] == 2, "API post+query"
    d = kb.delete_fact("a"); assert d["ok"] and kb.verify_audit(d["cert_id"]), "delete+verify"
    print("[selftest] PASS: api post-query delete", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; n_val = 32
    kb = SubstrateKB(n, n_val, rsa_bits=256, seed=seed)
    # pre-seed M_SEED facts (bulk via direct Hebbian for speed), then API live-ingest K_LIVE
    SK = kv(M_SEED, n, g); sval = [int(g.integers(0, n_val)) for _ in range(M_SEED)]
    kb.W = (kb.EV[np.array(sval)].T @ SK).astype(np.float32)   # bulk pre-seed
    for i in range(M_SEED):
        kb.acc.add("seed:%d" % i); kb.facts["seed:%d" % i] = (SK[i], sval[i])
    LK = kv(K_LIVE, n, g); lval = [int(g.integers(0, n_val)) for _ in range(K_LIVE)]
    write_ms = []
    for i in range(K_LIVE):
        t0 = time.perf_counter(); kb.post_fact("live:%d" % i, LK[i], lval[i]); write_ms.append((time.perf_counter() - t0) * 1000.0)
    live_recall = float(np.mean([kb.query(LK[i])["value_id"] == lval[i] for i in range(K_LIVE)]))
    # certified deletion of live facts
    del_idx = list(g.choice(K_LIVE, size=N_DEL, replace=False)); cert_ids = []
    for i in del_idx:
        d = kb.delete_fact("live:%d" % i)
        if d.get("ok"):
            cert_ids.append(d["cert_id"])
    audit_verified = sum(int(kb.verify_audit(c)) for c in cert_ids) / max(len(cert_ids), 1)
    phantom = 0
    for i in del_idx:
        q = kb.query(LK[i]); phantom += int(q["value_id"] == lval[i] and q["confidence"] > 0.30)
    phantom_rate = phantom / max(len(del_idx), 1)
    seed_keep = list(g.choice(M_SEED, size=300, replace=False))
    retention = float(np.mean([kb.query(SK[i])["value_id"] == sval[i] for i in seed_keep]))
    return {"seed": seed, "N": N_DIM, "M_seed": M_SEED, "k_live": K_LIVE, "n_del": N_DEL,
            "live_write_ms_median": float(np.median(write_ms)), "live_recall": live_recall,
            "audit_verified_frac": audit_verified, "phantom_recall_rate": phantom_rate, "preseed_retention": retention}


def verdict(ps) -> Tuple[str, str]:
    wm = float(np.mean([p["live_write_ms_median"] for p in ps])); lr = float(np.mean([p["live_recall"] for p in ps]))
    av = float(np.mean([p["audit_verified_frac"] for p in ps])); ph = float(np.mean([p["phantom_recall_rate"] for p in ps]))
    ret = float(np.mean([p["preseed_retention"] for p in ps]))
    summary = "N=%d M_seed=%d | live_write=%.3fms live_recall=%.3f certs_verified=%.3f phantom=%.3f retention=%.3f" % (
        ps[0]["N"], ps[0]["M_seed"], wm, lr, av, ph, ret)
    if lr > 0.95 and av >= 0.999 and ph == 0.0 and ret > 0.95:
        return ("HARD_PASS", "HARD_PASS: HP-12 V1 holds at TRUE demo scale (10K facts) -- live recall, certs verified, 0 phantom, retention intact. " + summary)
    if av >= 0.999 and ph < 0.01 and lr > 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: demo-scale mostly holds; recall/retention near-threshold. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: demo backend degrades at 10K scale. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d M_seed=%d K_live=%d N_del=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M_SEED, K_LIVE, N_DEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] live_write=%.3fms live_recall=%.3f certs_verified=%.3f phantom=%.3f retention=%.3f" % (
        seed, r["live_write_ms_median"], r["live_recall"], r["audit_verified_frac"], r["phantom_recall_rate"], r["preseed_retention"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
