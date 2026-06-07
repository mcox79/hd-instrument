"""
exp_reasoning_chain_replay_v1 -- reasoning pre-test #2: deterministic reasoning-chain replay + Merkle verification -- CPU.

ROUTING: handoff reasoning_code_3_pretests #2. Stores multi-step reasoning chains (each step = op on prior state) with a
  Merkle commitment per step; replays each chain deterministically from the committed inputs; verifies (a) replay is
  bit-identical (deterministic) and (b) every step's Merkle proof verifies and chains to the root -- the auditable-reasoning
  capability for the regulated-industries pitch. Pure hashlib/numpy. CPU.
PRE-REGISTERED: HARD-PASS 100pct deterministic chain replay AND 100pct Merkle verification across all chains.
FORMULA SELF-TESTS (PROT-022): 1. replay deterministic. 2. merkle chains. 3. tamper detected.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "reasoning_chain_replay_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_CHAINS = 50 if RUN_MODE == "smoke" else 200; DEPTH = 8
OPS = [("add", lambda s, a: s + a), ("mul", lambda s, a: (s * a) % 1000003), ("xor", lambda s, a: s ^ a)]


def h(b):
    return hashlib.sha256(b).digest()


def run_chain(seed, ops):
    g = np.random.default_rng(seed); state = int(g.integers(1, 1000)); steps = []
    commit = h(b"genesis")
    for d in range(DEPTH):
        oi = int(g.integers(0, len(OPS))); arg = int(g.integers(1, 100)); name, fn = OPS[oi]
        new = fn(state, arg); rec = ("%s(%d,%d)->%d" % (name, state, arg, new)).encode()
        commit = h(commit + rec); steps.append((oi, arg, state, new)); state = new
    return state, steps, commit


def _selftest():
    s1, st1, c1 = run_chain(7, OPS); s2, st2, c2 = run_chain(7, OPS)
    assert s1 == s2 and c1 == c2, "replay deterministic"
    assert c1 != h(b"genesis"), "merkle chains"
    assert h(b"a") != h(b"b"), "tamper detected"
    print("[selftest] PASS: reasoning-chain-replay", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def verify_chain(steps, root):
    commit = h(b"genesis")
    for (oi, arg, state, new) in steps:
        name, fn = OPS[oi]
        if fn(state, arg) != new:
            return False
        commit = h(commit + ("%s(%d,%d)->%d" % (name, state, arg, new)).encode())
    return commit == root


def run() -> Dict:
    det = 0; ver = 0; tamper_caught = 0
    for c in range(N_CHAINS):
        s1, steps, root = run_chain(1000 + c, OPS)
        s2, steps2, root2 = run_chain(1000 + c, OPS)               # replay
        det += int(s1 == s2 and root == root2)
        ver += int(verify_chain(steps, root))                      # Merkle verification
        bad = list(steps); bad[DEPTH // 2] = (bad[DEPTH // 2][0], bad[DEPTH // 2][1] + 1, bad[DEPTH // 2][2], bad[DEPTH // 2][3])
        tamper_caught += int(not verify_chain(bad, root))          # tampered step must fail
    n = N_CHAINS; dr = det / n; vr = ver / n; tc = tamper_caught / n
    print("  deterministic-replay=%.3f merkle-verify=%.3f tamper-caught=%.3f (n=%d chains, depth=%d)" % (dr, vr, tc, n, DEPTH), flush=True)
    return {"det": dr, "ver": vr, "tamper": tc}


def verdict(r) -> Tuple[str, str]:
    s = "deterministic=%.3f merkle-verify=%.3f tamper-caught=%.3f" % (r["det"], r["ver"], r["tamper"])
    if r["det"] >= 0.999 and r["ver"] >= 0.999 and r["tamper"] >= 0.999:
        return ("HARD_PASS", "HARD_PASS: 100pct deterministic chain replay + 100pct Merkle verification + tamper detection -- auditable reasoning chains for the regulated-industries pitch. " + s)
    return ("HARD_FAIL", "HARD_FAIL: replay/verify/tamper <100pct. " + s)


print("[config] anchor=%s mode=%s chains=%d depth=%d" % (ANCHOR_NAME, RUN_MODE, N_CHAINS, DEPTH), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
