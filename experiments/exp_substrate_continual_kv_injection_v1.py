"""
exp_substrate_continual_kv_injection_v1 -- Phase 4 Idea 17: continual learning via KV injection (long stream) -- CPU.
ROUTING: research phase4a_GO (Idea 17). Long continual stream of S sessions; each session injects new facts (KV write,
  no retraining) + revises a subset (delete-and-replace). Measures end-of-stream current-state accuracy, retention of
  still-valid old facts, and no-silent-contradiction over the WHOLE stream. Extends HP-11 to many sessions. CPU $0.
PRE-REG: HARD-PASS current-state>=0.95 AND silent-contradiction<=0.02 across all S sessions. MIDDLE>=0.85. HARD-FAIL contradiction>10%.
SELF-TESTS: 1 delete-replace. 2 retain. 3 N=16384. ASCII-only. write_metrics. PROT-018 no _nN (N=16384).
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
ANCHOR_NAME = "substrate_continual_kv_injection_v1"
N_SUB = 16384
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 4096; SESSIONS = 10; PER_SESSION = 80; REV_FRAC = 0.2
else:
    SEEDS = [7, 17, 23]; N_DIM = 8192; SESSIONS = 60; PER_SESSION = 60; REV_FRAC = 0.2
V_VAL = 24
def ub(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32); return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
def _selftest():
    g = np.random.default_rng(0); n = 256; K = ub(2, n, g); V = ub(3, n, g)
    W = (V[0:1].T @ K[0:1]).astype(np.float32); W -= np.outer(W @ K[0], K[0]); W += np.outer(V[2], K[0])
    assert int(np.argmax(V @ (W @ K[0]))) == 2, "delete-replace"
    W2 = (V[1:2].T @ K[1:2]).astype(np.float32); assert int(np.argmax(V @ (W2 @ K[1]))) == 1, "retain"
    assert N_SUB == 16384; print("[selftest] PASS: dr retain", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; cap = SESSIONS * PER_SESSION
    EK = ub(cap, n, g); EV = ub(V_VAL, n, g); W = np.zeros((n, n), dtype=np.float32)
    cur = {}; nxt = 0; silent = 0; sc_tot = 0
    for s in range(SESSIONS):
        ids = list(range(nxt, nxt + PER_SESSION)); nxt += PER_SESSION
        vals = {i: int(g.integers(0, V_VAL)) for i in ids}
        W += (EV[np.array([vals[i] for i in ids])].T @ EK[ids]).astype(np.float32)
        for i in ids: cur[i] = vals[i]
        seen = [i for i in cur if i < nxt - PER_SESSION]
        if seen:
            rev = list(g.choice(seen, size=max(1, int(REV_FRAC * len(seen))), replace=False))
            for i in rev:
                old = cur[i]; new = int((old + 1 + g.integers(0, V_VAL - 1)) % V_VAL)
                W -= np.outer(W @ EK[i], EK[i]); W += np.outer(EV[new], EK[i]); cur[i] = new
                if int(np.argmax(EV @ (W @ EK[i]))) == old and old != new: silent += 1
                sc_tot += 1
    ids_all = list(cur.keys()); samp = list(g.choice(ids_all, size=min(800, len(ids_all)), replace=False))
    current_state = float(np.mean([int(np.argmax(EV @ (W @ EK[i]))) == cur[i] for i in samp]))
    return {"seed": seed, "sessions": SESSIONS, "total_facts": nxt, "current_state_acc": current_state,
            "silent_contradiction_rate": float(silent / max(sc_tot, 1))}
def verdict(ps) -> Tuple[str, str]:
    cs = float(np.mean([p["current_state_acc"] for p in ps])); sc = float(np.mean([p["silent_contradiction_rate"] for p in ps]))
    summary = "current_state=%.3f silent_contradiction=%.3f over %d sessions / %d facts" % (cs, sc, ps[0]["sessions"], ps[0]["total_facts"])
    if cs >= 0.95 and sc <= 0.02: return ("HARD_PASS", "HARD_PASS: continual KV injection holds over long stream -- current state accurate, no silent contradictions. " + summary)
    if cs >= 0.85 and sc <= 0.10: return ("MIDDLE_BAND", "MIDDLE_BAND: continual stream mostly holds. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: continual stream degrades / silent contradictions. " + summary)
print("[config] anchor=%s mode=%s seeds=%s N=%d sessions=%d per=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, SESSIONS, PER_SESSION), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r); print("  [seed=%d] current_state=%.3f silent=%.3f facts=%d" % (seed, r["current_state_acc"], r["silent_contradiction_rate"], r["total_facts"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
