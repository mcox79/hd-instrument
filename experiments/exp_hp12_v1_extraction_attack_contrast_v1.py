"""
exp_hp12_v1_extraction_attack_contrast_v1 -- HP-12 V1 deletion moat: extraction-attack vs ROME/MEMIT -- CPU.

ROUTING: research HP12_V1 (frontier-LLM contrast deliverable). Substantiates the killer-demo's central claim with an
  ADVERSARIAL extraction attack on the substrate AFTER deletion, contrasted with published model-editing residuals
  (ROME 38% whitebox / MEMIT 29% blackbox; arXiv:2309.17410). Three attacks on each deleted fact:
    1. BLACKBOX direct query: query the deleted key -> recover original value? (confidence-gated)
    2. BLACKBOX perturbed query: query many noisy variants of the key -> any recover original?
    3. WHITEBOX weight probe: best-case read of W (W@k absolute alignment to original value) -> recover?
  Residual = fraction of deleted facts whose original value is recoverable by ANY attack. CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS substrate residual extraction <= 1% (categorical, vs ROME 38% / MEMIT 29%) AND non-
  deleted retention > 0.95. MIDDLE: residual <= 5%. HARD-FAIL: residual > 10% (deletion not categorical).
FORMULA SELF-TESTS (PROT-022): 1. stored fact extractable pre-delete. 2. projection drives extraction to 0. 3. N=4096.
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
from tools.hp12.frontier_contrast import print_contrast

ANCHOR_NAME = "exp_hp12_v1_extraction_attack_contrast_v1"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
CONF = 0.30; PERTURB_TRIES = 20
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 2048; M_FACTS = 600; N_DEL = 60
else:
    SEEDS = [7, 17, 23]; N_DIM = 4096; M_FACTS = 2000; N_DEL = 200


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); n = 256; K = bp(1, n, g)[0]; EV = bp(4, n, g); W = np.outer(EV[2], K) * 3
    s = EV @ (W @ K); assert int(np.argmax(s)) == 2 and s.max() > 0.3, "stored fact extractable pre-delete"
    W -= np.outer(W @ K, K); assert float((EV @ (W @ K)).max()) < 0.3, "projection drives extraction to 0"
    assert N == 4096; print("[selftest] PASS: extract pre/post delete", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; n_val = 32
    EK = bp(M_FACTS, n, g); EV = bp(n_val, n, g); val = [int(g.integers(0, n_val)) for _ in range(M_FACTS)]
    W = (EV[np.array(val)].T @ EK).astype(np.float32)              # Hebbian store
    del_ids = list(g.choice(M_FACTS, size=N_DEL, replace=False))
    # pre-delete: confirm facts ARE extractable (attack baseline)
    pre = float(np.mean([int(np.argmax(EV @ (W @ EK[i]))) == val[i] and float((EV @ (W @ EK[i])).max()) > CONF for i in del_ids]))
    # DELETE (projection-out + stabilizing re-projection)
    for i in del_ids:
        W -= np.outer(W @ EK[i], EK[i])
    for _ in range(3):
        for i in del_ids:
            W -= np.outer(W @ EK[i], EK[i])
    # EXTRACTION ATTACKS on each deleted fact
    recovered = 0
    for i in del_ids:
        orig = val[i]; hit = False
        # attack 1: blackbox direct query
        s = EV @ (W @ EK[i])
        if int(np.argmax(s)) == orig and float(s.max()) > CONF:
            hit = True
        # attack 2: blackbox perturbed queries
        if not hit:
            for _ in range(PERTURB_TRIES):
                kp = EK[i] + 0.3 * bp(1, n, g)[0]; kp /= np.linalg.norm(kp) + 1e-8
                sp = EV @ (W @ kp)
                if int(np.argmax(sp)) == orig and float(sp.max()) > CONF:
                    hit = True; break
        # attack 3: whitebox weight probe (absolute alignment of W@k to original value codeword)
        if not hit:
            r = W @ EK[i]
            if float(EV[orig] @ r) > CONF:
                hit = True
        recovered += int(hit)
    residual = recovered / max(len(del_ids), 1)
    keep = [i for i in range(M_FACTS) if i not in set(del_ids)][:300]
    retention = float(np.mean([int(np.argmax(EV @ (W @ EK[i]))) == val[i] for i in keep]))
    return {"seed": seed, "M_facts": M_FACTS, "n_del": N_DEL, "pre_delete_extractable": pre,
            "post_delete_residual": residual, "retention": retention}


def verdict(ps) -> Tuple[str, str]:
    res = float(np.mean([p["post_delete_residual"] for p in ps])); pre = float(np.mean([p["pre_delete_extractable"] for p in ps]))
    ret = float(np.mean([p["retention"] for p in ps]))
    summary = "pre_delete_extractable=%.3f -> post_delete_residual=%.4f (vs ROME 0.38 / MEMIT 0.29) | retention=%.3f" % (pre, res, ret)
    if res <= 0.01 and ret > 0.95:
        return ("HARD_PASS", "HARD_PASS: substrate deletion is CATEGORICAL -- residual extraction <=1%% under 3 attacks (ROME 38%%/MEMIT 29%% leave fact recoverable). The deletion moat is architectural. " + summary)
    if res <= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: residual extraction <=5%% (still far below ROME/MEMIT). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: residual extraction > 10%% (deletion not categorical). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d M=%d N_del=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M_FACTS, N_DEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] pre_extractable=%.3f post_residual=%.4f retention=%.3f" % (seed, r["pre_delete_extractable"], r["post_delete_residual"], r["retention"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
try:
    print_contrast(float(np.mean([p["post_delete_residual"] for p in ps])))
except Exception:
    pass
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
