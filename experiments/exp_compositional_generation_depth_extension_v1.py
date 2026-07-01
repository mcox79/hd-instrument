"""
exp_compositional_generation_depth_extension_v1.py -- COMPOSITIONAL GENERATION DEPTH EXTENSION (Stage 3) -- CPU.

ROUTING: Research Stage-3 compositional-understanding track. Extends compositional generation CG (baseline lift +0.724)
  to deeper composition depths. Depth = number of primitive ops composed into a single function-shard, then RECOVERED
  in order and EXECUTED on test inputs. Sweep depth in {2, 3, 5, 8} across 3 seeds {7, 13, 19}. LIFT = correctness at
  the sweep-depth arm MINUS the shuffled-shard control (structure-scrambled baseline). Substrate-native, no LLM.
PRE-REGISTERED: HARD_PASS lift @ depth=8 > +0.30 AND cross-seed cv < 10% at every depth. MIDDLE_BAND lift @ depth=8
  in [+0.10, +0.30]. HARD_FAIL lift @ depth=8 < +0.10 OR cv >= 10% at any depth.
DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke runs full N=8192 at depth=5, single seed_7 -- proves the discriminator
  (shuffled-shard control) still separates from real-composition at intermediate depth before we spend full-sweep budget.
CARDINALITY_OK: expected 4 depths x 3 seeds = 12 arm-rows; HARD_FAIL if per_arm_rows count < 12 in full mode.
ARMS_MUST_DIFFER: real vs shuffled-shard correctness must differ by > 0.05 per depth-seed pair or HARD_FAIL.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "compositional_generation_depth_extension_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

N = 8192
DEPTHS_FULL = [2, 3, 5, 8]
SEEDS_FULL = [7, 13, 19]
DEPTHS_SMOKE = [5]
SEEDS_SMOKE = [7]

def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi
    return np.exp(1j * ang).astype(np.complex64)

def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)

def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    # verify verdict bands are internally consistent
    fake_pass = {"depths": [2, 3, 5, 8], "seeds": [7, 13, 19], "per_arm": [
        {"depth": 2, "seed": 7, "real": 0.95, "ctrl": 0.20, "lift": 0.75},
        {"depth": 3, "seed": 7, "real": 0.93, "ctrl": 0.20, "lift": 0.73},
        {"depth": 5, "seed": 7, "real": 0.90, "ctrl": 0.20, "lift": 0.70},
        {"depth": 8, "seed": 7, "real": 0.75, "ctrl": 0.20, "lift": 0.55},
        {"depth": 2, "seed": 13, "real": 0.95, "ctrl": 0.20, "lift": 0.75},
        {"depth": 3, "seed": 13, "real": 0.93, "ctrl": 0.20, "lift": 0.73},
        {"depth": 5, "seed": 13, "real": 0.90, "ctrl": 0.20, "lift": 0.70},
        {"depth": 8, "seed": 13, "real": 0.75, "ctrl": 0.20, "lift": 0.55},
        {"depth": 2, "seed": 19, "real": 0.95, "ctrl": 0.20, "lift": 0.75},
        {"depth": 3, "seed": 19, "real": 0.93, "ctrl": 0.20, "lift": 0.73},
        {"depth": 5, "seed": 19, "real": 0.90, "ctrl": 0.20, "lift": 0.70},
        {"depth": 8, "seed": 19, "real": 0.75, "ctrl": 0.20, "lift": 0.55},
    ]}
    v, _ = verdict(fake_pass, is_smoke=False)
    assert v == "HARD_PASS", "selftest verdict-band inversion: expected HARD_PASS, got " + v
    print("[selftest] PASS: verdict-bands internally consistent", flush=True)

def run_arm(depth: int, seed: int) -> Dict:
    g = np.random.default_rng(seed)
    NK = 5
    OPS = ["add", "mul", "sub", "square", "neg"]
    opv = {o: cphasor(1, N, g)[0] for o in OPS}
    opbook = np.stack([opv[o] for o in OPS])
    consts = cphasor(NK, N, g)
    slots = cphasor(depth, N, g)
    OPROLE = cphasor(1, N, g)[0]
    CONSTROLE = cphasor(1, N, g)[0]

    def apply(op, k, x):
        return {"add": x + k, "mul": x * (k + 1), "sub": x - k, "square": x * x, "neg": -x}[op]

    TR = 30 if SMOKE else 100
    correct = 0
    ctrl_correct = 0
    n = 0
    for _ in range(TR):
        prog = [(OPS[int(g.integers(0, len(OPS)))], int(g.integers(0, NK))) for _ in range(depth)]
        # REAL: slot-bound composition (structure preserved)
        fn = cnorm(sum((slots[s] * (OPROLE * opv[prog[s][0]] + CONSTROLE * consts[prog[s][1]])
                       for s in range(depth)), np.zeros(N, dtype=np.complex64)))
        # CONTROL: shuffled-shard baseline -- same shards, structure destroyed by re-permuting slot assignment
        perm = list(range(depth))
        g.shuffle(perm)
        fn_ctrl = cnorm(sum((slots[perm[s]] * (OPROLE * opv[prog[s][0]] + CONSTROLE * consts[prog[s][1]])
                            for s in range(depth)), np.zeros(N, dtype=np.complex64)))
        # RECOVER + EXECUTE
        rec = []
        rec_ctrl = []
        for s in range(depth):
            comp = fn * np.conj(slots[s])
            ro = OPS[cidx(comp * np.conj(OPROLE), opbook)]
            rk = cidx(comp * np.conj(CONSTROLE), consts)
            rec.append((ro, rk))
            comp_c = fn_ctrl * np.conj(slots[s])
            ro_c = OPS[cidx(comp_c * np.conj(OPROLE), opbook)]
            rk_c = cidx(comp_c * np.conj(CONSTROLE), consts)
            rec_ctrl.append((ro_c, rk_c))
        for xi in [1, 3, -2]:
            xg = xi
            xr = xi
            xc = xi
            for (o, k) in prog:
                xg = apply(o, k, xg)
            for (o, k) in rec:
                xr = apply(o, k, xr)
            for (o, k) in rec_ctrl:
                xc = apply(o, k, xc)
            correct += int(xr == xg)
            ctrl_correct += int(xc == xg)
            n += 1
    real = correct / n
    ctrl = ctrl_correct / n
    lift = real - ctrl
    return {"depth": depth, "seed": seed, "real": round(real, 3), "ctrl": round(ctrl, 3),
            "lift": round(lift, 3), "n": n}

def run() -> Dict:
    depths = DEPTHS_SMOKE if SMOKE else DEPTHS_FULL
    seeds = SEEDS_SMOKE if SMOKE else SEEDS_FULL
    per_arm = []
    for d in depths:
        for s in seeds:
            arm = run_arm(d, s)
            per_arm.append(arm)
            print("  arm depth=%d seed=%d real=%.3f ctrl=%.3f lift=%+.3f" %
                  (d, s, arm["real"], arm["ctrl"], arm["lift"]), flush=True)
    return {"depths": depths, "seeds": seeds, "per_arm": per_arm}

def verdict(r, is_smoke: bool) -> Tuple[str, str]:
    per_arm = r["per_arm"]
    # smoke gate: single arm, verify discriminator FIRES at intermediate depth
    if is_smoke:
        a = per_arm[0]
        if a["real"] - a["ctrl"] < 0.05:
            return ("HARD_FAIL",
                    "SMOKE_FAIL: real vs shuffled-shard control differ by <0.05 at depth=%d -- discriminator does not fire, do NOT dispatch full. real=%.3f ctrl=%.3f" %
                    (a["depth"], a["real"], a["ctrl"]))
        if a["lift"] < 0.30:
            return ("MIDDLE_BAND",
                    "SMOKE_MIDDLE: lift=%+.3f at depth=%d seed=%d below +0.30 discriminator floor; full-sweep at depth=8 will likely fail. Consider mechanism improvement before full dispatch." %
                    (a["lift"], a["depth"], a["seed"]))
        return ("HARD_PASS",
                "SMOKE_PASS: discriminator fires at depth=%d, lift=%+.3f >= +0.30. Ready for full sweep." %
                (a["depth"], a["lift"]))
    # full mode: cardinality + arms-differ + depth=8 lift + cross-seed cv
    expected_rows = len(r["depths"]) * len(r["seeds"])
    if len(per_arm) != expected_rows:
        return ("HARD_FAIL",
                "HARD_FAIL: CARDINALITY_BREACH expected %d arm-rows got %d" % (expected_rows, len(per_arm)))
    for a in per_arm:
        if a["real"] - a["ctrl"] < 0.05:
            return ("HARD_FAIL",
                    "HARD_FAIL: ARMS_MUST_DIFFER breach at depth=%d seed=%d (real=%.3f ctrl=%.3f delta<0.05)" %
                    (a["depth"], a["seed"], a["real"], a["ctrl"]))
    # per-depth cv
    for d in r["depths"]:
        lifts = [a["lift"] for a in per_arm if a["depth"] == d]
        mean = float(np.mean(lifts))
        std = float(np.std(lifts))
        cv = abs(std / mean) if mean != 0 else float("inf")
        if cv >= 0.10:
            return ("HARD_FAIL",
                    "HARD_FAIL: cross-seed cv=%.3f >= 0.10 at depth=%d (lifts=%s)" %
                    (cv, d, str(lifts)))
    # depth=8 lift decision
    d8 = [a["lift"] for a in per_arm if a["depth"] == 8]
    mean_d8 = float(np.mean(d8))
    summary = "depth=8 mean_lift=%+.3f (n_seeds=%d); per-depth means: %s" % (
        mean_d8, len(d8),
        ", ".join("d%d=%+.3f" % (d, float(np.mean([a["lift"] for a in per_arm if a["depth"] == d]))) for d in r["depths"]))
    if mean_d8 > 0.30:
        return ("HARD_PASS",
                "HARD_PASS: compositional-generation depth extends to 8 with lift >+0.30 and cross-seed cv <10% at all depths. Stage-3 compositional-understanding scales. " + summary)
    if mean_d8 >= 0.10:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: depth=8 lift in [+0.10, +0.30] -- mechanism degrades with depth but signal survives. " + summary)
    return ("HARD_FAIL",
            "HARD_FAIL: depth=8 lift <+0.10 -- compositional-generation does not extend past shallow depth. " + summary)

_selftest()
if _ARGS.self_test:
    sys.exit(0)

print("[config] anchor=%s mode=%s N=%d depths=%s seeds=%s" %
      (ANCHOR_NAME, RUN_MODE, N,
       str(DEPTHS_SMOKE if SMOKE else DEPTHS_FULL),
       str(SEEDS_SMOKE if SMOKE else SEEDS_FULL)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
t0 = time.time()
r = run()
v, vmsg = verdict(r, is_smoke=SMOKE)
print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
           "run_mode": RUN_MODE, "n_seeds": len(r["seeds"]),
           "per_arm_rows": r["per_arm"], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, r["per_arm"])
print("[metrics] written", flush=True)
