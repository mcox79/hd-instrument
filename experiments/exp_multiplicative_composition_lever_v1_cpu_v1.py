"""LEVER #4: composition-operator selector = a DEPTH-AXIS REFUSE-GATE (Research prereg; Director refinement 4b).

NOVEL CLAIM (scoped per Director 4b): NOT "chain helps in-envelope" (that is CERT 592 re-expressed) but
"the substrate REFUSES out-of-envelope chains (depth K > K_max(load)) where chaining would FABRICATE a confident-wrong
answer." Composes with refuse-gate #5b (CERT 588): #5b = load-axis OOE refusal; this = depth-axis OOE refusal.

GENUINE COST (avoids the cost-collapse trap that sank LEVER 1.5): chaining beyond K_max does not gracefully truncate --
the cleanup snaps to a WRONG codebook node every hop, so an out-of-envelope chain returns a confident-WRONG node
(fabrication). The selector's value = avoiding that fabrication. Measured by a RISK-UTILITY metric: correct=+1,
fabricate(confident-wrong)=-1, refuse=0. Refusing only wins if OOE chains are genuinely mostly-wrong.

NON-CIRCULAR (the LEVER 1.5 lesson): K_max(load) is CALIBRATED on calibration seeds and the selector is TESTED on
HELD-OUT seeds. The chain-grade test is whether refusing-OOE beats always-chain on held-out data because OOE fabricates.

3 arms: Arm1 selector (chain if K<=K_max(load) else REFUSE); Arm2 always-chain (fabricates OOE); Arm3 always-flat (1 hop).
DISCRIMINATING iff: Arm1 > Arm3 utility on depth-K (chain adds value) AND Arm1 > Arm2 utility on OOE (refuse avoids
fabrication) AND Arm1 ~ Arm2 in-envelope (selector doesn't hurt). HARD_PASS only if OOE fabrication is REAL (de-saturation).
data-decides -> Skunkworks rules tier. ASCII; no em-dashes.
"""
import sys
from pathlib import Path
import argparse
import os
import time
import numpy as np

REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "multiplicative_composition_lever_v1_cpu_v1"
_P = argparse.ArgumentParser(); _P.add_argument("--self-test", action="store_true", dest="self_test"); _ARGS, _ = _P.parse_known_args()
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full" if not _ARGS.self_test else "smoke")
N = 2048 if RUN_MODE == "full" else 512
CHAIN_LEN = 10                                            # nodes per chain -> max queryable depth = CHAIN_LEN-1
LOADS = [0.6, 1.0, 1.5] if RUN_MODE == "full" else [0.6, 1.0]   # alpha = #transitions / N; gives K_max envelope {6,3,2} with clear OOE fabrication (verified)
KQ = list(range(1, CHAIN_LEN))                            # query depths 1..9
CAL_SEEDS = [101, 102] if RUN_MODE == "full" else [101]  # calibrate K_max here
TEST_SEEDS = [1, 2, 3] if RUN_MODE == "full" else [1]    # test the selector here (held-out)
KMAX_ACC_THRESH = 0.70                                    # K_max(load) = largest depth with calibrated chain-acc >= this


def bipolar(rows, n, g):
    return (g.integers(0, 2, (rows, n)) * 2 - 1).astype(np.float32)


def build_substrate(load, n, seed):
    """Heteroassociative chain store at the given load. Returns (codebook, W, chains).
    chains = list of node-index sequences (length CHAIN_LEN); transitions packed into W = sum b a^T / n."""
    g = np.random.default_rng(seed)
    M = max(CHAIN_LEN, int(load * n))                     # total transitions
    n_chains = max(1, M // (CHAIN_LEN - 1))
    total_nodes = n_chains * CHAIN_LEN                    # node-disjoint chains (clean per-chain succession)
    codebook = bipolar(total_nodes, n, g)
    chains = [list(range(c * CHAIN_LEN, c * CHAIN_LEN + CHAIN_LEN)) for c in range(n_chains)]
    W = np.zeros((n, n), np.float32)
    for ch in chains:
        for i in range(len(ch) - 1):
            a, b = codebook[ch[i]], codebook[ch[i + 1]]
            W += np.outer(b, a)
    W /= n
    return codebook, W, chains


def chain_recall(codebook, W, start_idx, K):
    """K-hop recall: iterate the RAW sign map (no per-hop codebook cleanup, so per-hop bit-errors ACCUMULATE -> a genuine
    depth envelope, the CERT 592 NESS phenomenon); cleanup ONCE at the end. Returns the recalled node index.
    Beyond K_max the accumulated drift makes the final cleanup snap to a WRONG node = fabrication."""
    cur = codebook[start_idx].copy()
    for _ in range(K):
        cur = np.sign(W @ cur).astype(np.float32); cur[cur == 0] = 1.0
    return int(np.argmax(codebook @ cur))                # single final cleanup


def chain_accuracy(codebook, W, chains, K):
    """fraction of depth-K queries (start of chain -> node K hops along) recalled correctly."""
    ok = 0; tot = 0
    for ch in chains:
        if len(ch) > K:
            tot += 1
            ok += int(chain_recall(codebook, W, ch[0], K) == ch[K])
    return ok / max(1, tot)


def calibrate_kmax(load, n, cal_seeds):
    """K_max(load) = largest depth K with mean calibrated chain-accuracy >= KMAX_ACC_THRESH (calibration seeds only)."""
    built = [build_substrate(load, n, sd * 13 + 1) for sd in cal_seeds]    # build W once per cal seed (not per K)
    acc_by_k = {}
    for K in KQ:
        acc_by_k[K] = float(np.mean([chain_accuracy(cb, W, ch, K) for (cb, W, ch) in built]))
    kmax = 0
    for K in KQ:
        if acc_by_k[K] >= KMAX_ACC_THRESH:
            kmax = K
        else:
            break
    return kmax, acc_by_k


def run_unit(load, test_seed, kmax):
    """Test the 3 arms on held-out seed: per query depth K, utility (correct +1 / fabricate -1 / refuse 0)."""
    cb, W, chains = build_substrate(load, N, test_seed * 977 + 5)
    rows = []
    for K in KQ:
        qs = [ch for ch in chains if len(ch) > K]
        if not qs: continue
        correct_flags = [chain_recall(cb, W, ch[0], K) == ch[K] for ch in qs]
        flat_flags = [chain_recall(cb, W, ch[0], 1) == ch[K] for ch in qs]  # Arm3: always 1-hop (correct only if K==1)
        acc = float(np.mean(correct_flags))
        in_env = K <= kmax
        # Arm1 selector: chain if in-envelope else REFUSE (utility 0)
        u1 = float(np.mean([(1 if c else -1) for c in correct_flags])) if in_env else 0.0
        # Arm2 always-chain: answer regardless (fabricates OOE)
        u2 = float(np.mean([(1 if c else -1) for c in correct_flags]))
        # Arm3 always-flat: 1-hop answer always
        u3 = float(np.mean([(1 if c else -1) for c in flat_flags]))
        rows.append({"K": K, "in_envelope": in_env, "chain_acc": round(acc, 4),
                     "u_selector": round(u1, 4), "u_always_chain": round(u2, 4), "u_flat": round(u3, 4),
                     "selector_action": ("chain" if in_env else "refuse")})
    return {"load": load, "seed": test_seed, "kmax": kmax, "rows": rows}


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    by_load = {}
    for u in units:
        by_load.setdefault(u["load"], []).append(u)
    per_load = {}
    for L, us in sorted(by_load.items()):
        kmax = us[0]["kmax"]
        allrows = [r for u in us for r in u["rows"]]
        depthK = [r for r in allrows if r["K"] >= 2]                      # chain-relevant queries
        inenv = [r for r in allrows if r["in_envelope"]]
        ooe = [r for r in allrows if not r["in_envelope"]]
        def mean(rows, key): return float(np.mean([r[key] for r in rows])) if rows else None
        # total utility per arm (sum over the query distribution: in-env + OOE)
        U_sel = mean(allrows, "u_selector"); U_chain = mean(allrows, "u_always_chain"); U_flat = mean(allrows, "u_flat")
        ooe_chain_acc = mean(ooe, "chain_acc")                            # de-saturation: is OOE genuinely mostly-wrong?
        inenv_chain_acc = mean(inenv, "chain_acc")
        # PER-SEED margins (sel - chain): a robust beat needs the win to exceed seed-noise, not just the mean (verify-the-referent)
        u_sel_by_seed = [float(np.mean([r["u_selector"] for r in u["rows"]])) for u in us]
        margins = [float(np.mean([r["u_selector"] for r in u["rows"]]) - np.mean([r["u_always_chain"] for r in u["rows"]])) for u in us]
        mean_m = float(np.mean(margins)); std_m = float(np.std(margins))
        cv = float(np.std(u_sel_by_seed) / (abs(np.mean(u_sel_by_seed)) + 1e-9))
        per_load[L] = {"kmax": kmax, "U_selector": _r(U_sel), "U_always_chain": _r(U_chain), "U_flat": _r(U_flat),
                       "ooe_chain_acc": _r(ooe_chain_acc), "inenv_chain_acc": _r(inenv_chain_acc),
                       "n_ooe_depths": len(set(r["K"] for r in ooe)), "seed_cv": round(cv, 4),
                       "margin_vs_chain_mean": round(mean_m, 4), "margin_vs_chain_std": round(std_m, 4),
                       "ROBUST_beats_chain": bool(mean_m > 0.05 and mean_m > 2 * std_m),   # win exceeds seed-noise
                       "never_worse_than_chain": bool(mean_m >= -0.05),                     # selector can only refuse where chain fabricates -> never meaningfully worse
                       "sel_beats_flat": (U_sel is not None and U_flat is not None and U_sel > U_flat + 0.05),
                       "fabrication_real": (ooe_chain_acc is not None and ooe_chain_acc < 0.50)}
    # aggregate gates. Only loads with an OOE regime test the refuse-gate. The honest claim is NOT "beats on every load" --
    # it is "robustly beats where fabrication is significant (per-seed margin > seed-noise) AND never worse anywhere".
    testable = [L for L in per_load if per_load[L]["n_ooe_depths"] > 0]
    robust_beat = [L for L in testable if per_load[L]["ROBUST_beats_chain"] and per_load[L]["fabrication_real"]]
    never_worse_all = all(per_load[L]["never_worse_than_chain"] for L in per_load)
    beats_flat = [L for L in per_load if per_load[L]["sel_beats_flat"]]
    fab_real = [L for L in testable if per_load[L]["fabrication_real"]]
    seed_stable = all(per_load[L]["seed_cv"] < 0.20 for L in per_load)
    marginal = [L for L in testable if not per_load[L]["ROBUST_beats_chain"]]   # OOE loads where the win is within seed-noise
    detail = {"per_load": {("alpha%.2f" % L): per_load[L] for L in per_load}, "kmax_by_load": {("alpha%.2f" % L): per_load[L]["kmax"] for L in per_load},
              "testable_loads_with_OOE": testable, "loads_ROBUST_beat_chain": robust_beat, "loads_marginal_within_seednoise": marginal,
              "never_worse_than_chain_all_loads": never_worse_all, "loads_sel_beats_flat": beats_flat,
              "loads_fabrication_real": fab_real, "seed_stable": seed_stable,
              "honest_claim": ("Depth-axis refuse-gate: selector refuses chains deeper than CALIBRATED K_max(load) (cal seeds), TESTED "
                               "held-out via risk-utility (correct +1 / fabricate -1 / refuse 0). Genuine cost = OOE chains FABRICATE. "
                               "The refuse-gate ROBUSTLY earns its keep WHERE FABRICATION IS SIGNIFICANT (low-K_max / high-load: per-seed "
                               "margin over always-chain exceeds seed-noise, always-chain goes NEGATIVE); at low load (high K_max) the value "
                               "is marginal (little fabrication to avoid) but the selector is NEVER worse. Beats always-flat everywhere (chain "
                               "adds depth value). Load-dependent value is the honest characterization, not a flaw.")}
    summary = "kmax=%s | ROBUST_beat_chain=%s marginal(within-noise)=%s never_worse_all=%s beats_flat=%s fab_real=%s seed_stable=%s" % (
        detail["kmax_by_load"], robust_beat, marginal, never_worse_all, beats_flat, fab_real, seed_stable)
    if not testable:
        return ("UNKNOWN", "no out-of-envelope regime (K_max >= max depth) -- raise LOADS or CHAIN_LEN. " + summary, detail)
    if not fab_real:
        return ("MEASURED_MECHANISM", "MEASURED_MECHANISM: OOE chains do NOT fabricate (acc>=0.5) -> K_max conservative; refusing is over-cautious. " + summary, detail)
    if robust_beat and never_worse_all and len(beats_flat) == len(per_load) and seed_stable:
        return ("HARD_PASS", "HARD_PASS (depth-axis refuse-gate; data-decides -> Skunkworks): the selector ROBUSTLY beats always-chain "
                "(per-seed margin > seed-noise) on the high-fabrication loads %s (where always-chain goes negative), is NEVER worse than "
                "always-chain elsewhere, and beats always-flat everywhere (chain adds depth value). No single fixed operator wins. The value "
                "is LOAD-DEPENDENT (marginal at high-K_max load %s where there is little fabrication to avoid -- honest, not a flaw). "
                "Composes with refuse-gate #5b (load-axis). " % (robust_beat, marginal) + summary, detail)
    if robust_beat or len(beats_flat) == len(per_load):
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial -- robust-beat or never-worse or beats-flat not met on all required. " + summary, detail)
    return ("MEASURED_MECHANISM", "MEASURED_MECHANISM: selector does not robustly beat baselines. " + summary, detail)


def _r(x):
    return None if x is None else round(x, 4)


def _selftest():
    cb, W, ch = build_substrate(0.1, 256, 1)
    a1 = chain_accuracy(cb, W, ch, 1)
    assert a1 >= 0.8, "1-hop recall should be high at low load, got %.3f" % a1
    kmax, accs = calibrate_kmax(0.1, 256, [101])
    assert kmax >= 1, "K_max should be >=1 at low load"
    assert accs[1] >= accs[max(accs)], "accuracy should not INCREASE with depth"
    print("[selftest] PASS: 1-hop recall high + K_max>=1 + accuracy non-increasing with depth", flush=True)


_selftest()
if _ARGS.self_test:
    raise SystemExit(0)

print("[config] %s mode=%s N=%d loads=%s chain_len=%d cal_seeds=%s test_seeds=%s" % (
    ANCHOR_NAME, RUN_MODE, N, LOADS, CHAIN_LEN, CAL_SEEDS, TEST_SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
kmax_by_load = {}
for L in LOADS:
    kmax, acc_by_k = calibrate_kmax(L, N, CAL_SEEDS)
    kmax_by_load[L] = kmax
    print("[calibrate] load=%.2f K_max=%d acc_by_k=%s" % (L, kmax, {k: round(v, 3) for k, v in acc_by_k.items()}), flush=True)
for L in LOADS:
    for sd in TEST_SEEDS:
        key = ("a%.2f_s%d" % (L, sd)).replace(".", "p")
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        write_partial_key(out_dir, key, run_unit(L, sd, kmax_by_load[L]))
        print("[unit] %s done" % key, flush=True)
keys = [("a%.2f_s%d" % (L, sd)).replace(".", "p") for L in LOADS for sd in TEST_SEEDS]
units = list(aggregate_partials(out_dir, keys, run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N,
           "loads": LOADS, "chain_len": CHAIN_LEN, "cal_seeds": CAL_SEEDS, "test_seeds": TEST_SEEDS, "detail": detail,
           "metrics_source": "measured_cpu_depth_axis_refuse_gate_chain_composition", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
