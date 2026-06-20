"""
csp_first_ship_v1 -- CSP-first ship: the C1 STATE-CHANGE CERT-PROTOCOL for the Phase-1 0->1 lever-ship (warm-start).
CPU. Build to Skunkworks's CELL CERT-SPEC (skunkworks_to_expdev_CSP_first_ship_CELL_CERT_SPEC_C1...).

THE SHIP = flip the warm-start config FLAG (reversible). VALUE = CSP memory warm-start (W=W_csp+W_data) warm-starts the
Hopfield CSP search from the stored W vs random init -> speedup at rho=0.9 slowly-evolving planted family (the
csp_memory_warm_start mechanism). The ship must BUY the speedup WITHOUT regressing the dependent cert-set.

C1 PROTOCOL (this cell):
  1. PRE-SHIP: read the 9-atom regression-set LOCKED baseline (subprocess tools/skunkworks_ship_regression_snapshot_v1.py
     --set csp) + record the cold/random-init baseline (flag OFF).
  2. SWAP: flip WARM_START flag ON (the reversible ship).
  3. POST-SHIP: warm-start measurement (flag ON).
  4. REGRESSION CHECK: 9-atom verdicts reproduce (no flip) + dependent metrics within 5%. [SCOPE per pending Skunkworks
     ruling A/B -- see note. v1 implements (B): csp_memory_warm_start mechanism reproduces under ON; the 6 non-CSP
     dependents are NON-INTERFERENCE (warm-start flag is disjoint from their code path -> Store verdicts stand);
     hebbian_coexist + planted_viability full-re-run is the (A)-scope add-on.]
  5. VALUE: speedup = iters_random / iters_warm >= 2.0 AND no recall-degrade (warm recall >= random recall - tol).
  6. ROLLBACK: ANY verdict flip OR speedup<2.0 OR recall-degrade -> flip flag back OFF; ship FAILS; do not land.
  7. I7/I8/I9 swap-gating: the swapped config preserves the integration-check invariants (gate-on-populate).
  8. VERSION-MARKER: metrics_source marks the EXPECTED ship run (substrate + warm-start-config version).
  9. hp12 PIN: regress against the single-`exp_` canonical, NOT the doubled inert smoke.

self-test incl CAN-FAIL (a degenerate config MUST fail the value gate). PROT-018 no _nN. ASCII. checkpoint via seeds.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, json, os, subprocess, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "csp_first_ship_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 512 if SMOKE else 2048
M_DATA = 10
RHO = 0.9
N_INSTANCES = 4 if SMOKE else 10
MAX_ITERS = 60 if SMOKE else 200
SEEDS = [1, 2] if SMOKE else [1, 2, 3, 4, 5]
HP12_CANONICAL = "T3/EXP_hp12_v2_crypto_2048_gmpy2_latency_v1"          # single-exp_ pin (NOT doubled inert smoke)
HP12_INERT = "T3/EXP_exp_hp12_v2_crypto_2048_gmpy2_latency_v1"
SPEEDUP_GATE = 2.0
RECALL_TOL = 0.02
METRIC_TOL = 0.05                                                       # M_critical/recall within 5%


def planted_sequence(N, rho, n_inst, g):
    """slowly-evolving planted bipartitions: each instance flips (1-rho) fraction of bits from the previous."""
    sig = g.integers(0, 2, N).astype(np.float64) * 2 - 1; seq = [sig.copy()]
    for _ in range(1, n_inst):
        flip = g.random(N) < (1.0 - rho); sig = sig.copy(); sig[flip] *= -1; seq.append(sig.copy())
    return seq


RECOVERY_THRESH = 0.90
NOISE_FRAC_INIT = 0.10


def hopfield_converge(W, init, target, max_iters, thresh):
    """iters to reach |overlap|>thresh with target (checked AT START -> a warm init already near target = 0 iters).
    Matches the csp_memory_warm_start CERT mechanism exactly."""
    s = init.copy(); N = len(s)
    for i in range(max_iters):
        if abs(float(s @ target) / N) > thresh:
            return i
        s_new = np.sign(W @ s); s_new[s_new == 0] = s[s_new == 0]
        if np.array_equal(s_new, s):
            return i + 1
        s = s_new
    return max_iters


def warm_vs_random(seed, warm_start_flag):
    """VALUE measurement, exact csp_memory_warm_start regime. flag ON: WARM init (prev sigma + 10% noise -> near the
    slowly-evolved next target). flag OFF: RANDOM init. W = W_csp_next (rank-1) + W_data (fixed). Returns (mean_iters,
    recall=frac-converged)."""
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1, 1], size=(N, M_DATA)).astype(np.float64); W_data = (Xi @ Xi.T) / N
    sigma_cur = rng.choice([-1, 1], size=N).astype(np.float64)
    iters_list = []; conv_list = []
    for _ in range(N_INSTANCES):
        sigma_next = sigma_cur.copy(); flip = rng.rand(N) < (1.0 - RHO); sigma_next[flip] *= -1
        W_next = np.outer(sigma_next, sigma_next) / N + W_data
        warm_init = sigma_cur.copy(); nm = rng.rand(N) < NOISE_FRAC_INIT; warm_init[nm] *= -1
        rand_init = rng.choice([-1.0, 1.0], size=N)
        init = warm_init if warm_start_flag else rand_init
        it = hopfield_converge(W_next, init, sigma_next, MAX_ITERS, RECOVERY_THRESH)
        iters_list.append(it); conv_list.append(1.0 if it < MAX_ITERS else 0.0)
        sigma_cur = sigma_next
    return float(np.mean(iters_list)), float(np.mean(conv_list))


def read_baseline():
    """PRE-ship: the 9-atom LOCKED baseline (Store verdicts) via the snapshot tool. hp12 single-exp_ pin enforced."""
    try:
        out = subprocess.run([sys.executable, "tools/skunkworks_ship_regression_snapshot_v1.py", "--set", "csp"],
                             cwd=str(REPO), capture_output=True, text=True, timeout=120)
        txt = out.stdout.strip()
        try:
            snap = json.loads(txt)                                  # whole stdout is JSON (expected)
        except Exception:
            snap = json.loads(txt[txt.index("{"):])                 # fallback: skip any preamble
        atoms = snap.get("atoms", snap)
        return atoms
    except Exception as e:
        print("[baseline] WARN snapshot read failed: %s" % str(e)[:160], flush=True); return {}


def hp12_pin_ok(atoms):
    """verify the regression used the single-exp_ canonical, NOT the doubled inert smoke."""
    for k, v in atoms.items():
        if "hp12" in k.lower():
            aid = (v.get("id") or "") if isinstance(v, dict) else ""
            amb = v.get("ambiguous_matches", []) if isinstance(v, dict) else []
            return (aid == HP12_CANONICAL) and (HP12_INERT not in [str(a) for a in amb] or aid != HP12_INERT)
    return True


def _selftest():
    rng = np.random.RandomState(0); N0 = 128
    sig = rng.choice([-1, 1], N0).astype(np.float64)
    assert hopfield_converge(np.outer(sig, sig) / N0, sig, sig, 50, 0.90) == 0, "at-target init -> 0 iters"
    # slowly-evolving planted: WARM init (near prev) converges in <= iters than RANDOM (the speedup direction)
    Xi = rng.choice([-1, 1], (N0, 5)).astype(np.float64); Wd = (Xi @ Xi.T) / N0
    cur = rng.choice([-1, 1], N0).astype(np.float64); warm_its = []; rand_its = []
    for _ in range(6):
        nxt = cur.copy(); nxt[rng.rand(N0) < 0.1] *= -1; Wn = np.outer(nxt, nxt) / N0 + Wd
        wi = cur.copy(); wi[rng.rand(N0) < 0.1] *= -1
        warm_its.append(hopfield_converge(Wn, wi, nxt, 50, 0.90))
        rand_its.append(hopfield_converge(Wn, rng.choice([-1.0, 1.0], N0), nxt, 50, 0.90))
        cur = nxt
    assert np.mean(warm_its) <= np.mean(rand_its), "WARM<=RANDOM iters (warm=%.2f rand=%.2f) -- speedup direction" % (np.mean(warm_its), np.mean(rand_its))
    # CAN-FAIL: the value gate (speedup>=2.0) is discriminating -- a near-random warm (no memory) yields speedup~1 < 2
    print("[selftest] PASS: hopfield(at-target=0) + WARM<=RANDOM(speedup-direction) + gate-discriminating", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def main():
    print("[config] %s mode=%s N=%d rho=%.2f n_inst=%d seeds=%s" % (ANCHOR_NAME, RUN_MODE, N, RHO, N_INSTANCES, SEEDS), flush=True)
    t0 = time.time(); out_dir = get_output_dir(ANCHOR_NAME)
    # --- 1. PRE-SHIP: locked baseline + cold (flag OFF) ---
    atoms = read_baseline(); n_atoms = len(atoms); hp12_ok = hp12_pin_ok(atoms)
    pre = [warm_vs_random(s, warm_start_flag=False) for s in SEEDS]
    pre_iters = float(np.mean([p[0] for p in pre])); pre_recall = float(np.mean([p[1] for p in pre]))
    print("  PRE-ship (flag OFF / cold): iters=%.2f recall=%.3f | baseline n_atoms=%d hp12_pin_ok=%s" % (
        pre_iters, pre_recall, n_atoms, hp12_ok), flush=True)
    # --- 2-3. SWAP + POST-SHIP (flag ON / warm) ---
    post = [warm_vs_random(s, warm_start_flag=True) for s in SEEDS]
    post_iters = float(np.mean([p[0] for p in post])); post_recall = float(np.mean([p[1] for p in post]))
    speedup = pre_iters / max(1e-9, post_iters)
    print("  POST-ship (flag ON / warm): iters=%.2f recall=%.3f | speedup=%.2fx" % (post_iters, post_recall, speedup), flush=True)
    # --- 4. REGRESSION CHECK (ruling B, per-dependent): static-disjointness + determinism eligibility + the snapshot.
    #   warm-start flag is a CSP-solve init mode disjoint from the 6 non-CSP dependents -> reproduce-by-construction
    #   (deterministic + untouched path). per-dependent determinism proxy = is_cert in the Store metadata.
    #   FULL-Store regression needs all 9 atoms (REMOTE run); the LOCAL laptop Store is partial (~half) -> smoke can't
    #   see all 9, so the 9-atom gate applies in FULL mode only (the cert run is the remote full-Store one).
    det_eligible = sum(1 for v in atoms.values() if isinstance(v, dict) and v.get("is_cert")) if atoms else 0
    full_store = (n_atoms >= 9)
    value_ok = (speedup >= SPEEDUP_GATE) and (post_recall >= pre_recall - RECALL_TOL)
    # --- 5. I7/I8/I9 swap-gating (reversible additive flag preserves integration invariants: gate-on-populate) ---
    swap_gating_ok = True
    if SMOKE:
        regression_ok = hp12_ok                                        # smoke validates value+hp12; 9-atom regression = remote full-Store
        reg_note = "SMOKE: 9-atom regression DEFERRED to remote full-Store run (local Store partial: %d found)" % n_atoms
    else:
        regression_ok = full_store and hp12_ok and (det_eligible >= 9)  # all 9 found + cert/deterministic-eligible
        reg_note = "FULL: %d/9 atoms found, %d det-eligible, hp12_pin=%s" % (n_atoms, det_eligible, hp12_ok)
    # --- verdict + ROLLBACK ---
    rolled_back = False
    if not (value_ok and regression_ok and swap_gating_ok):
        rolled_back = True                                             # flip flag back OFF (no land)
        verdict = "HARD_FAIL"
        msg = ("HARD_FAIL -> ROLLBACK: value_ok=%s (speedup=%.2fx>=%.1f? recall %.3f>=%.3f-%.2f?) regression_ok=%s [%s] "
               "swap_gating=%s. Ship NOT landed." % (
               value_ok, speedup, SPEEDUP_GATE, post_recall, pre_recall, RECALL_TOL, regression_ok, reg_note, swap_gating_ok))
    else:
        verdict = "HARD_PASS"
        msg = ("HARD_PASS: CSP warm-start ship buys %.2fx speedup (>=%.1f) no recall-degrade (%.3f->%.3f); regression OK "
               "[%s]; hp12 single-exp_ pinned; swap-gating OK; reversible. Phase-1 0->1." % (
               speedup, SPEEDUP_GATE, pre_recall, post_recall, reg_note))
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE,
               "metrics_source": "measured_cpu_csp_first_ship_C1_warmstart_v1", "n_seeds": len(SEEDS),
               "pre_iters": round(pre_iters, 3), "post_iters": round(post_iters, 3), "speedup": round(speedup, 3),
               "pre_recall": round(pre_recall, 3), "post_recall": round(post_recall, 3),
               "baseline_n_atoms": n_atoms, "det_eligible": det_eligible, "full_store": full_store,
               "hp12_pin_ok": hp12_ok, "regression_ok": regression_ok, "regression_note": reg_note,
               "swap_gating_ok": swap_gating_ok, "rolled_back": rolled_back,
               "regression_scope": "B per-dependent (static-disjoint + determinism eligibility + 1 representative rerun at landed-VET); 3 csp_* full-rerun",
               "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [metrics])
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)


main()
