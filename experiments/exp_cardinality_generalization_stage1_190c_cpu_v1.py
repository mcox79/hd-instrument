"""
190c STAGE-1 -- CARDINALITY GENERALIZATION test (DECISION 192 GO). Tests whether ARM-1's ratified
cleanup_distinct_count operator GENERALIZES to a DIFFERENT generator distribution than the one it was
authored on -- i.e. generalization, NOT refit. The OPERATOR IS UNCHANGED (CLEANUP_THRESH = 0.30, the
ARM-1 ratified value; NOT re-tuned -- re-tuning would be refit, not generalization).

DISTRIBUTION SHIFT vs ARM-1 cell (exp_cardinality_phase_B_skeleton_cpu_v1):
  ARM-1:   VOCAB=120  ROLES=4  n_distinct in [1,9)  mult in [1,4)  N in {1024,2048,4096}
  STAGE-1: VOCAB=200  ROLES=5  n_distinct in [2,13) mult in [1,6)  N in {2048,4096}
  (wider+shifted count range; higher multiplicity stresses the dedup harder; larger vocab; N>=2048 to
   keep the higher-count single-role test WITHIN the capacity envelope alpha_single=0.030.)

PIPELINE (pure-substrate; NO LLM): scene = FHRR superposition of bind(role,filler) with MULTIPLICITY
  -> cleanup_distinct_count (unbind + corr-cleanup + threshold-count; the ARM-1 T3 operator, UNCHANGED)
  -> readout (exact-count RMSE / AGGREGATE ; quantifier-most accuracy / RATIO).
Controls (FAIR-NULL, reused from ARM-1): C0 graph-walk-trace (B^T@B matrix; the EXHAUSTED M4d class; HEAVY
  -> REMOTE per USER thermal policy for the full run) ; C1 basis-norm null (multiplicity-confounded).

PRE-REGISTERED BARS (carried from ARM-1; locked BEFORE the full run; tune-free):
  exact-count (single-role HARD distinctness): RMSE<=1.0 AND >=2x reduction vs C1 AND beats C0, WITHIN envelope.
  quantifier-most: acc>=0.80 AND margin>=0.20 over C1.
HELD-OUT GOLD: the generator's ground-truth distinct count is FIREWALLED -- generated at eval time, NEVER
  ingested into the corpus (22nd-rule discipline, parallel to q54-q65 / 56d).
HONEST-NEGATIVE PATH: if the operator does NOT transfer (RMSE blows up / acc drops), that is an HONEST NEGATIVE
  -> ARM-1 capabilities stay SCOPED to their original cell distribution; NO manufactured transfer claim.

Queue-compatible: --self-test, --smoke, full-mode metrics.json. CPU/numpy, bipolar, ASCII only.
NOTE: full mode (N=4096, n=5 seeds, C0 matrix) is HEAVY -> REMOTE. --smoke is light (laptop-OK).
"""
import sys, os, time, json
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR = "cardinality_generalization_stage1_190c_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SELFTEST = "--self-test" in sys.argv

# ---- DISTRIBUTION SHIFT (different from ARM-1; the generalization test) ----
if RUN_MODE == "smoke":
    SEEDS = [7, 17]; N_LIST = [2048]; VOCAB = 60; N_SCENES = 40
    ND_LO, ND_HI = 2, 9; MULT_LO, MULT_HI = 1, 5
else:
    SEEDS = [7, 17, 23, 31, 41]; N_LIST = [2048, 4096]; VOCAB = 200; N_SCENES = 300
    ND_LO, ND_HI = 2, 13; MULT_LO, MULT_HI = 1, 6   # wider counts + higher multiplicity than ARM-1

# ---- OPERATOR CONSTANT: LOCKED to the ARM-1 ratified value (NOT re-tuned -- generalization not refit) ----
CLEANUP_THRESH = 0.30   # ARM-1 ratified cleanup correlation threshold; FROZEN here by design.

# ---- pre-registered bars (carried from ARM-1; locked) ----
PREREG = {
    "exact_count_C2_rmse_max": 1.0,
    "exact_count_rmse_reduction": 2.0,
    "quant_hardpass_acc": 0.80,
    "quant_margin": 0.20,
}
CAPACITY_ALPHA_SINGLE = 0.030   # single-role HARD distinctness envelope (ARM-1)


def bipolar(rng, shape):
    return rng.choice([-1.0, 1.0], size=shape).astype(np.float64)


def eval_single_role_isolation(seed, N):
    """Single-role distinct-under-multiplicity (the clean HARD distinctness claim; no cross-role crosstalk).
    NEW distribution (shifted counts + higher multiplicity). Operator (CLEANUP_THRESH) UNCHANGED."""
    rng = np.random.RandomState(seed)
    codebook = bipolar(rng, (VOCAB, N))
    role = bipolar(rng, N)
    truth, c0, c1, c2 = [], [], [], []
    max_total = 0
    for _ in range(N_SCENES):
        n_distinct = int(rng.randint(ND_LO, ND_HI))
        fillers = rng.choice(VOCAB, size=n_distinct, replace=False)
        scene = np.zeros(N); total = 0; bound = []
        for f in fillers:
            mult = int(rng.randint(MULT_LO, MULT_HI))
            for _ in range(mult):
                b = role * codebook[f]; scene += b; bound.append(b); total += 1
        max_total = max(max_total, total)
        truth.append(n_distinct)                                  # FIREWALLED gold (generated; not ingested)
        B = np.stack(bound, axis=0)
        c0.append(round(float(np.trace((B.T @ B) / N))))         # C0 graph-walk-trace (HEAVY matrix; REMOTE)
        u = role * scene
        c1.append(round(float(np.dot(u, u) / N)))                # C1 basis-norm null (total, not distinct)
        sims = (codebook @ u) / N
        c2.append(int(np.sum(sims > CLEANUP_THRESH)))            # C2 cleanup_distinct_count (UNCHANGED operator)
    truth = np.array(truth, float)
    def rmse(e): return float(np.sqrt(np.mean((np.array(e, float) - truth) ** 2)))
    return {"c0_rmse": rmse(c0), "c1_rmse": rmse(c1), "c2_rmse": rmse(c2), "max_total_bindings": max_total}


def eval_quantifier_most(seed, N):
    """most(A vs B): is role-A distinct-count > role-B distinct-count? accuracy/RATIO. Two roles present
    (cross-role); C1 vs C2 readout. NEW distribution. Operator UNCHANGED."""
    rng = np.random.RandomState(seed)
    codebook = bipolar(rng, (VOCAB, N))
    rA, rB = bipolar(rng, N), bipolar(rng, N)
    most_truth, most_c1, most_c2 = [], [], []
    for _ in range(N_SCENES):
        scene = np.zeros(N); da = db = 0
        for (role, _set) in ((rA, "A"), (rB, "B")):
            nd = int(rng.randint(ND_LO, ND_HI))
            fillers = rng.choice(VOCAB, size=nd, replace=False)
            for f in fillers:
                for _ in range(int(rng.randint(MULT_LO, MULT_HI))):
                    scene += role * codebook[f]
            if _set == "A": da = nd
            else: db = nd
        most_truth.append(1 if da > db else 0)
        uA, uB = rA * scene, rB * scene
        most_c1.append(1 if float(np.dot(uA, uA)) > float(np.dot(uB, uB)) else 0)        # C1 norm
        cA = int(np.sum((codebook @ uA) / N > CLEANUP_THRESH))
        cB = int(np.sum((codebook @ uB) / N > CLEANUP_THRESH))
        most_c2.append(1 if cA > cB else 0)                                              # C2 cleanup-count
    def acc(p, g): return float(np.mean(np.array(p) == np.array(g)))
    return {"c1_acc": acc(most_c1, most_truth), "c2_acc": acc(most_c2, most_truth)}


def capacity_status(max_total, N, alpha=CAPACITY_ALPHA_SINGLE):
    frac = max_total / float(N)
    return (frac <= alpha), frac


# ---- pre-registered verdicts (carried from ARM-1; tune-free) ----
def verdict_exact_count(c0, c1, c2, within_env):
    if not within_env:
        return ("CAPACITY-ARTIFACT", "outside envelope; C2 not a primitive verdict")
    beats_c0 = c2 < c0
    reduces_c1 = c1 > 0 and (c1 / max(c2, 1e-9)) >= PREREG["exact_count_rmse_reduction"]
    reaches = c2 <= PREREG["exact_count_C2_rmse_max"]
    if beats_c0 and reduces_c1 and reaches:
        return ("HARD_PASS", f"C2 {c2:.2f} escapes C0 {c0:.2f} + >=2x C1 {c1:.2f} + <=1.0 (GENERALIZES)")
    if (not beats_c0) or c2 >= c1:
        return ("HARD_FAIL", f"C2 {c2:.2f} does not escape (C0 {c0:.2f}/C1 {c1:.2f}) -> no transfer; ARM-1 stays scoped")
    return ("MIDDLE_BAND", f"C2 {c2:.2f} partial (C0 {c0:.2f}/C1 {c1:.2f})")


def verdict_quantifier(c1, c2):
    margin = c2 - c1
    if c2 >= PREREG["quant_hardpass_acc"] and margin >= PREREG["quant_margin"]:
        return ("HARD_PASS", f"C2 {c2:.3f}>=0.80 + margin {margin:.3f}>=0.20 (GENERALIZES)")
    if c2 < 0.65:
        return ("HARD_FAIL", f"C2 {c2:.3f}<0.65 -> no transfer; ARM-1 stays scoped")
    return ("MIDDLE_BAND", f"C2 {c2:.3f} (margin {margin:.3f})")


def _selftest():
    # verdict bands
    assert verdict_exact_count(5.0, 60.0, 0.9, True)[0] == "HARD_PASS"
    assert verdict_exact_count(5.0, 60.0, 6.0, True)[0] == "HARD_FAIL"
    assert verdict_exact_count(5.0, 60.0, 0.9, False)[0] == "CAPACITY-ARTIFACT"
    assert verdict_quantifier(0.55, 0.82)[0] == "HARD_PASS"
    assert verdict_quantifier(0.55, 0.60)[0] == "HARD_FAIL"
    # operator locked
    assert CLEANUP_THRESH == 0.30, "operator threshold must be the ARM-1 ratified value (no refit)"
    # distribution actually shifted vs ARM-1 (generalization, not refit)
    assert (VOCAB, ND_HI, MULT_HI) != (120, 9, 4), "distribution must differ from ARM-1 (generalization test)"
    # pipeline runs + recovers distinct under multiplicity on a tiny case
    r = eval_single_role_isolation(0, 512)
    assert r["c2_rmse"] < r["c1_rmse"], "C2 should beat C1 null even on tiny sanity (distinctness escape)"
    print("[selftest] PASS: verdict bands + operator-locked + distribution-shifted + pipeline-runs", flush=True)


def main():
    print(f"[start] {ANCHOR} run_mode={RUN_MODE} N_LIST={N_LIST} VOCAB={VOCAB} "
          f"n_distinct[{ND_LO},{ND_HI}) mult[{MULT_LO},{MULT_HI}) CLEANUP_THRESH={CLEANUP_THRESH}(LOCKED)", flush=True)
    _selftest()
    out_dir = get_output_dir(os.environ.get("HDLAB_EXP_NAME", ANCHOR)); t0 = time.time()
    results = {}
    for N in N_LIST:
        sr = [eval_single_role_isolation(s, N) for s in SEEDS]
        q = [eval_quantifier_most(s, N) for s in SEEDS]
        sr_c0 = float(np.mean([r["c0_rmse"] for r in sr]))
        sr_c1 = float(np.mean([r["c1_rmse"] for r in sr]))
        sr_c2 = float(np.mean([r["c2_rmse"] for r in sr]))
        sr_c2_std = float(np.std([r["c2_rmse"] for r in sr]))
        maxtot = max(r["max_total_bindings"] for r in sr)
        in_env, frac = capacity_status(maxtot, N)
        q_c1 = float(np.mean([r["c1_acc"] for r in q]))
        q_c2 = float(np.mean([r["c2_acc"] for r in q]))
        q_c2_std = float(np.std([r["c2_acc"] for r in q]))
        v_ec = verdict_exact_count(sr_c0, sr_c1, sr_c2, in_env)
        v_q = verdict_quantifier(q_c1, q_c2)
        drift = q_c2_std > 0.40
        print(f"\n[N={N}] SINGLE-ROLE exact-count RMSE: C0={sr_c0:.2f} C1={sr_c1:.2f} C2={sr_c2:.2f} "
              f"(std {sr_c2_std:.3f}) | envelope: max_total={maxtot} frac={frac:.4f} within={in_env}", flush=True)
        print(f"[N={N}] MOST(A>B) acc: C1={q_c1:.3f} C2={q_c2:.3f} (std {q_c2_std:.3f})", flush=True)
        print(f"[N={N}] VERDICT exact-count(generalization): {v_ec[0]} -- {v_ec[1]}", flush=True)
        print(f"[N={N}] VERDICT most(generalization): {v_q[0]} -- {v_q[1]}", flush=True)
        print(f"[N={N}] SEED-VARIANCE most C2 std={q_c2_std:.3f} -> {'DRIFT' if drift else 'no-drift'}", flush=True)
        results[str(N)] = {"exact_count": {"c0": sr_c0, "c1": sr_c1, "c2": sr_c2, "c2_std": sr_c2_std,
                                            "within_envelope": in_env, "frac": frac, "verdict": v_ec[0], "msg": v_ec[1]},
                           "most": {"c1": q_c1, "c2": q_c2, "c2_std": q_c2_std, "verdict": v_q[0], "msg": v_q[1],
                                    "drift": drift}}
    metrics = {"anchor_name": ANCHOR, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "N_list": N_LIST,
               "operator_cleanup_thresh_LOCKED": CLEANUP_THRESH, "distribution": {"VOCAB": VOCAB,
               "n_distinct": [ND_LO, ND_HI], "mult": [MULT_LO, MULT_HI]}, "prereg": PREREG,
               "results": results, "elapsed_s": time.time() - t0, "compute_backend": "cpu", "dtype": "float64",
               "note": "generalization-not-refit: operator UNCHANGED, distribution SHIFTED vs ARM-1; gold firewalled"}
    write_metrics(out_dir, metrics, [results])
    print(f"\n[metrics] written {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    if SELFTEST:
        _selftest(); sys.exit(0)
    main()
