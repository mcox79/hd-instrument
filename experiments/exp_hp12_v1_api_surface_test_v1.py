"""
exp_hp12_v1_api_surface_test_v1 -- HP-12 V1 HIPAA API surface end-to-end test (Day-4 deliverable) -- CPU.

ROUTING: research HP12_V1_pipeline_simplified_desktop_only (Day-4 API surface). Exercises ALL FOUR demo endpoints
  (tools/hp12/api.SubstrateKB) end-to-end: POST /facts (ingest M) -> POST /query (recall) -> DELETE /facts/{id}
  (cert) -> GET /audit/{cert_id} (retrieve + third-party verify) -> POST /query again (0 phantom). CPU numpy +
  pure-Python/gmpy2 crypto $0.

PRE-REGISTERED bands: HARD-PASS all 4 endpoints functional AND query recall >0.95 AND every retrieved audit cert
  third-party-verifies AND 0 phantom recall after delete AND retention >0.95. MIDDLE: phantom <1% OR recall>0.90.
  HARD-FAIL: endpoint error OR phantom OR cert fail.
FORMULA SELF-TESTS (PROT-022): 1. post+query round-trip. 2. delete+audit+verify. 3. N=4096.
ASCII-only. write_metrics. PROT-018 _n4096 -> N=4096.
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

ANCHOR_NAME = "exp_hp12_v1_api_surface_test_v1"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 2048; M_FACTS = 400; N_DEL = 30; RSA_BITS = 256
else:
    SEEDS = [7, 17, 23]; N_DIM = 4096; M_FACTS = 1200; N_DEL = 100; RSA_BITS = 256


def keyvecs(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); kb = SubstrateKB(256, 8, rsa_bits=128, seed=0); K = keyvecs(3, 256, g)
    kb.post_fact("f0", K[0], 2); kb.post_fact("f1", K[1], 5)
    assert kb.query(K[0])["value_id"] == 2, "post+query round-trip"
    d = kb.delete_fact("f0"); assert d["ok"] and kb.verify_audit(d["cert_id"]), "delete+audit+verify"
    assert N == 4096; print("[selftest] PASS: post-query delete-audit", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; n_val = 32
    kb = SubstrateKB(n, n_val, rsa_bits=RSA_BITS, seed=seed)
    K = keyvecs(M_FACTS, n, g); vals = [int(g.integers(0, n_val)) for _ in range(M_FACTS)]
    # POST /facts
    for i in range(M_FACTS):
        kb.post_fact("fact:%d" % i, K[i], vals[i])
    # POST /query (recall accuracy on a sample)
    ev = list(g.choice(M_FACTS, size=min(300, M_FACTS), replace=False))
    recall = float(np.mean([kb.query(K[i])["value_id"] == vals[i] for i in ev]))
    # DELETE /facts/{id} + GET /audit + third-party verify
    del_ids = list(g.choice(M_FACTS, size=N_DEL, replace=False))
    audit_verified = 0; endpoints_ok = True
    cert_ids = []
    for i in del_ids:
        d = kb.delete_fact("fact:%d" % i)
        if not d.get("ok"):
            endpoints_ok = False; continue
        cert_ids.append(d["cert_id"])
    for cid in cert_ids:
        c = kb.get_audit(cid)                              # GET /audit/{cert_id}
        audit_verified += int(c is not None and kb.verify_audit(cid))
    audit_verified_frac = audit_verified / max(len(cert_ids), 1)
    # POST /query again -> 0 phantom recall on deleted facts (absolute confidence gate)
    phantom = 0
    for i in del_ids:
        q = kb.query(K[i]); phantom += int(q["value_id"] == vals[i] and q["confidence"] > 0.30)
    phantom_rate = phantom / max(len(del_ids), 1)
    # retention of non-deleted
    keep = [i for i in range(M_FACTS) if i not in set(del_ids)][:200]
    retention = float(np.mean([kb.query(K[i])["value_id"] == vals[i] for i in keep]))
    return {"seed": seed, "M_facts": M_FACTS, "n_del": N_DEL, "endpoints_ok": endpoints_ok,
            "query_recall": recall, "audit_verified_frac": audit_verified_frac,
            "phantom_recall_rate": phantom_rate, "retention": retention}


def verdict(ps) -> Tuple[str, str]:
    rc = float(np.mean([p["query_recall"] for p in ps])); av = float(np.mean([p["audit_verified_frac"] for p in ps]))
    ph = float(np.mean([p["phantom_recall_rate"] for p in ps])); ret = float(np.mean([p["retention"] for p in ps]))
    eok = all(p["endpoints_ok"] for p in ps)
    summary = "endpoints_ok=%s query_recall=%.3f audit_verified=%.3f phantom_recall=%.3f retention=%.3f (M=%d,N_del=%d)" % (
        eok, rc, av, ph, ret, ps[0]["M_facts"], ps[0]["n_del"])
    if eok and rc > 0.95 and av >= 0.999 and ph == 0.0 and ret > 0.95:
        return ("HARD_PASS", "HARD_PASS: all 4 HP-12 V1 API endpoints functional e2e -- ingest+query+delete+audit, every cert third-party-verified, 0 phantom. " + summary)
    if eok and av >= 0.999 and ph < 0.01:
        return ("MIDDLE_BAND", "MIDDLE_BAND: API works; recall/phantom near-threshold. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: API endpoint failure, phantom recall, or cert fail. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d M=%d N_del=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M_FACTS, N_DEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] endpoints_ok=%s query_recall=%.3f audit_verified=%.3f phantom=%.3f retention=%.3f" % (
        seed, r["endpoints_ok"], r["query_recall"], r["audit_verified_frac"], r["phantom_recall_rate"], r["retention"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
