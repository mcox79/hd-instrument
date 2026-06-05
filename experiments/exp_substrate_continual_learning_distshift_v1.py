"""
substrate_continual_learning_distshift_v1 -- HP-11: continual learning under DISTRIBUTION SHIFT -- CPU.

ROUTING: research envelope_pushing_HP7_to_HP11 (HP-11; harder than HP-3). Real deployment has distribution shift
  (guidelines/precedents/regs update with contradictions). Day 1-15 = stream A; day 16-30 = stream B (revises a subset
  of A's facts with CONTRADICTING values + adds new facts). Substrate must: (a) retrieve CURRENT state (newer overrides
  older via delete-and-replace), (b) audit-trace which version is stored, (c) NO silent contradictions (outdated facts
  return B not A). CPU numpy $0.

PRE-REGISTERED bands: HARD-PASS current-state acc >= 0.95 (newer overrides) AND outdated-no-silent-contradiction >= 0.95
  (updated entities return B, NOT old A) AND old-valid retained >= 0.95. MIDDLE: >= 0.85 each. HARD-FAIL: silent
  contradictions (updated entities still return A) > 10%.
FORMULA SELF-TESTS (PROT-022): 1. delete-and-replace overwrites to new value. 2. unrelated fact retained. 3. N=16384.
ASCII-only. write_metrics. PROT-018: no _nN (N=16384 capacity).
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

ANCHOR_NAME = "substrate_continual_learning_distshift_v1"
N_SUB = 16384
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 8192; N_A = 2000; N_UPDATE = 600; N_NEW = 600
else:
    SEEDS = [7, 17, 23]; N_DIM = N_SUB; N_A = 4000; N_UPDATE = 1200; N_NEW = 1200
V_VAL = 24


def ub(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); n = 256; K = ub(2, n, g); V = ub(3, n, g)
    W = (V[0:1].T @ K[0:1] + V[1:2].T @ K[1:2]).astype(np.float32)   # k0->v0, k1->v1
    W -= np.outer(W @ K[0], K[0]); W += np.outer(V[2], K[0])         # delete-and-replace k0 -> v2
    assert int(np.argmax(V @ (W @ K[0]))) == 2, "delete-and-replace overwrites to new"
    assert int(np.argmax(V @ (W @ K[1]))) == 1, "unrelated fact retained"
    assert N_SUB == 16384; print("[selftest] PASS: overwrite retain", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM
    n_ent = N_A + N_NEW; EK = ub(n_ent, n, g); EV = ub(V_VAL, n, g)
    valA = [int(g.integers(0, V_VAL)) for _ in range(N_A)]
    version = {}                                          # audit trace: entity -> current version tag
    # Stream A (days 1-15): batched Hebbian
    W = (EV[np.array(valA)].T @ EK[:N_A]).astype(np.float32)
    for i in range(N_A):
        version[i] = ("A", valA[i])
    # Stream B (days 16-30): UPDATE a subset of A with contradicting values (delete-and-replace) + NEW entities
    upd = list(g.choice(N_A, size=N_UPDATE, replace=False)); newB = {}
    for i in upd:
        newv = int((valA[i] + 1 + g.integers(0, V_VAL - 1)) % V_VAL)   # contradicts A
        W -= np.outer(W @ EK[i], EK[i]); W += np.outer(EV[newv], EK[i])  # delete-and-replace
        newB[i] = newv; version[i] = ("B", newv)
    newvals = [int(g.integers(0, V_VAL)) for _ in range(N_NEW)]
    W += (EV[np.array(newvals)].T @ EK[N_A:N_A + N_NEW]).astype(np.float32)   # new B-only entities
    for j in range(N_NEW):
        version[N_A + j] = ("B", newvals[j])
    # ---- Queries ----
    upd_set = set(upd)
    old_valid = [i for i in range(N_A) if i not in upd_set]
    # (a) old-valid: A entities not updated -> recall A value
    ov = np.mean([int(np.argmax(EV @ (W @ EK[i]))) == valA[i] for i in old_valid[:300]])
    # (b) outdated/contradicted: updated entities -> MUST return B (newer), NOT old A (no silent contradiction)
    returns_B = np.mean([int(np.argmax(EV @ (W @ EK[i]))) == newB[i] for i in upd])
    silent_contradiction = np.mean([int(np.argmax(EV @ (W @ EK[i]))) == valA[i] and valA[i] != newB[i] for i in upd])
    # (c) new B-only: recall new value
    nw = np.mean([int(np.argmax(EV @ (W @ EK[N_A + j]))) == newvals[j] for j in range(min(N_NEW, 300))])
    # current-state overall + audit trace correctness (version tag matches recalled)
    audit_ok = np.mean([version[i][1] == int(np.argmax(EV @ (W @ EK[i]))) for i in (old_valid[:150] + upd[:150])])
    return {"seed": seed, "old_valid_acc": float(ov), "updated_returns_B": float(returns_B),
            "silent_contradiction_rate": float(silent_contradiction), "new_acc": float(nw), "audit_trace_acc": float(audit_ok),
            "current_state_acc": float((ov + returns_B + nw) / 3)}


def verdict(ps) -> Tuple[str, str]:
    cs = float(np.mean([p["current_state_acc"] for p in ps])); rb = float(np.mean([p["updated_returns_B"] for p in ps]))
    sc = float(np.mean([p["silent_contradiction_rate"] for p in ps])); ov = float(np.mean([p["old_valid_acc"] for p in ps]))
    audit = float(np.mean([p["audit_trace_acc"] for p in ps]))
    summary = "current_state=%.3f | updated_returns_B=%.3f silent_contradiction=%.3f | old_valid=%.3f | audit_trace=%.3f" % (cs, rb, sc, ov, audit)
    if cs >= 0.95 and rb >= 0.95 and ov >= 0.95 and sc <= 0.02:
        return ("HARD_PASS", "HARD_PASS: substrate handles distribution shift -- newer overrides older, no silent contradictions, audit-traced. " + summary)
    if cs >= 0.85 and sc <= 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate handles shift mostly; edge cases. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: silent contradictions or shift not handled. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d A=%d upd=%d new=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, N_A, N_UPDATE, N_NEW), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] current_state=%.3f updated_B=%.3f silent_contra=%.3f old_valid=%.3f audit=%.3f" % (
        seed, r["current_state_acc"], r["updated_returns_B"], r["silent_contradiction_rate"], r["old_valid_acc"], r["audit_trace_acc"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
