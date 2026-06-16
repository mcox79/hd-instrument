"""
PHASE-B CARDINALITY BENCHMARK SKELETON (DECISION 159a; builds AGAINST Skunkworks gate
methodology DECISION 158a Task 1 + amendment C0/ESCAPE + Drill 1 pre-reg).

STATUS: SKELETON + SANITY TEST ONLY. NOT the graded Phase-B run. The full run is GATED to
Phase-B GO 2026-06-21 (run via HDLAB_RUN_MODE=full, n_seeds>=3). The sanity test here uses
smoke params purely to confirm the skeleton executes and TARGETS A REAL ESCAPE REGIME
(C2 beats C0+C1 by margin; C1 near null). Pre-registered thresholds are baked in but NOT
adjudicated here.

Config ladder (Skunkworks amendment + Drill 1):
  C0  GRAPH-WALK TRACE CONTROL  -- trace of the edge-outer-product matrix (the EXHAUSTED
                                   M4d-0.272 class). NAMED CONTROL. C2 must ESCAPE (beat), not match.
  C1  BASIS-ONLY (NULL)         -- bundle-norm threshold readout (Drill-1 "composable-from-basis"
                                   hypothesis). Counts MULTIPLICITY + crosstalk, not distinctness.
  C2  +CARDINALITY-PRIMITIVE    -- iterative-unbind + cleanup distinct-count (vector-native;
                                   correlation+threshold; NO matrix-power). The escape mechanism.
  C3  +INTERNAL-ABSTRACTION     -- stub here; the autonomous-discovery probe is 158b Task 3
                                   (does substrate DISCOVER the C2 primitive, not hand-supplied).

Escape regime (per my 175th feasibility finding + Drill-1 logic): DISTINCT-filler-count under
MULTIPLICITY. Norm/trace count total bindings (multiplicity-confounded) -> overestimate distinct;
cleanup-count collapses repeats -> recovers distinct. Clean single-role total-count is NOT a valid
target (it ties C0; my feasibility probe showed Pearson 0.9993 == trace 1.0000 -> ESCAPE FAILS there).

Sibling probes (DECISION 148 sibling-probe-failure; scope-vs-general):
  exact-distinct-count   metric = RMSE         type = AGGREGATE
  at-least-k             metric = accuracy     type = RATIO
  most/majority(A vs B)  metric = accuracy     type = RATIO

Integrity gates baked in (Skunkworks sec 4 + my vector-encoding assertion):
  - VECTOR-ENCODING ASSERT: C1/C2/C3 readout paths touch NO adjacency matrix-power (only C0 does).
  - gate-EVADE: any task C1 closes at >=0.70 is EVADABLE -> dropped (not a cardinality gap).
  - run_mode tier-A: full + n_seeds>=3 for the graded run (this skeleton's sanity is smoke-flagged).
  - type-aware: AGGREGATE(RMSE)/RATIO(accuracy) stamped per sibling (not capability-accuracy).
  - 11th-rule: C2 cleanup-count is substrate-internal (no learned codebook; codebook is the
    substrate's own atom vectors, cleanup is a native op).

CPU, numpy, bipolar. ASCII only.
"""
import sys
import os
import numpy as np

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "smoke")).lower()
# NOTE: default is smoke here because this is the SKELETON sanity harness. The graded Phase-B
# run MUST be invoked with HDLAB_RUN_MODE=full (asserted at graded-run entry, not here).

# ---- pre-registered thresholds (RECONCILED Drill-1 <-> Skunkworks) ----
PREREG = {
    "C1_null_accuracy_max": 0.60,      # Drill-1 at-least-k null <=0.60 (Skunkworks <=0.55; use 0.60 conservative)
    "evade_drop_accuracy": 0.70,       # Skunkworks: C1>=0.70 -> task EVADABLE -> DROP
    "C2_hardpass_accuracy": 0.80,      # Skunkworks C2 HARD-PASS floor
    "C2_C1_margin": 0.20,              # BOTH agree: (C2-C1) >= 0.20
    "exact_count_C1_rmse_min": 3.0,    # Drill-1: bundle-norm RMSE > 3.0 @ N=1024 (null)
    "exact_count_C2_rmse_max": 1.0,    # Drill-1: C2 reduces to <=1.0 (and >=2x reduction vs C1)
    "exact_count_rmse_reduction": 2.0, # Drill-1: C2 reduces RMSE by >=2x
    "escape_margin_over_C0": 0.20,     # Skunkworks amendment: C2 must BEAT C0 by margin (not match)
    "C3_P_deflated": 0.40,             # Drill-1 C3 prior; HARD-PASS needs reusability+2nd-signature
}

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_LIST = [1024]
    VOCAB = 30
    N_SCENES = 40
    ROLES = 3
else:
    SEEDS = [7, 17, 23, 31, 41]    # n_seeds=5 (tier A; >=3)
    N_LIST = [1024, 2048, 4096]    # Drill-1: C1 must not close by raising N
    VOCAB = 120
    N_SCENES = 300
    ROLES = 4

CLEANUP_THRESH = 0.30   # correlation threshold for distinct-cleanup-count (sim units, /N)

# ---- AMENDMENT v3a + Skunkworks VET: REGIME-CALIBRATED CAPACITY-ENVELOPE gate ----
# C2 must be evaluated WITHIN VSA bundle capacity; outside, a low C2 is a capacity ARTIFACT, NOT a
# primitive HARD-FAIL. Alpha is REGIME-DEPENDENT (Skunkworks concur): single-role (no crosstalk)
# tolerates HIGHER density than multi-role at the same N, because crosstalk consumes capacity.
# Auditor implication: the WIDER single-role envelope is where the clean-confound HARD distinctness
# claim lives -> the cleanest claim is ALSO the best-supported by capacity (more in-envelope cells).
# Empirical (Task-4 multi-role scan): ~32 bindings worked @N=4096 (~0.008); ~96 failed (~0.023).
CAPACITY_ALPHA_MULTI = 0.012    # crosstalk-laden compound capability test (tighter)
CAPACITY_ALPHA_SINGLE = 0.030   # single-role HARD distinctness claim, no crosstalk (wider; ~2.5x)

def capacity_status(max_total_bindings, N, alpha=CAPACITY_ALPHA_MULTI):
    """Returns (within_envelope, frac). Outside the envelope a C2 low score is a capacity artifact.
    Pass alpha=CAPACITY_ALPHA_SINGLE for the single-role HARD claim (wider envelope)."""
    frac = max_total_bindings / float(N)
    return (frac <= alpha), frac


def bipolar(rng, shape):
    return rng.choice([-1.0, 1.0], size=shape).astype(np.float64)


def make_scene(rng, codebook, role_vecs, query_role):
    """
    Cardinality-REQUIRED scene: bundle of bind(role, filler) with MULTIPLICITY.
    Returns scene vector, ground-truth distinct-count for query_role, per-role distinct sets,
    and per-role bound-vector lists WITH MULTIPLICITY (so the C0 control sees the same
    multiplicity-confounded data as C1/C2 -- NOT the pre-deduplicated distinct set).
    """
    N = codebook.shape[1]
    V = codebook.shape[0]
    scene = np.zeros(N)
    distinct_by_role = {r: set() for r in range(len(role_vecs))}
    bound_by_role = {r: [] for r in range(len(role_vecs))}   # WITH multiplicity (fair C0 input)
    for r in range(len(role_vecs)):
        n_distinct = int(rng.randint(1, 9))          # true distinct fillers for this role
        fillers = rng.choice(V, size=n_distinct, replace=False)
        for f in fillers:
            mult = int(rng.randint(1, 4))            # MULTIPLICITY: 1..3 repeats (the confounder)
            for _ in range(mult):
                b = role_vecs[r] * codebook[f]
                scene += b
                bound_by_role[r].append(b)           # one entry PER binding (multiplicity preserved)
            distinct_by_role[r].add(int(f))
    return scene, len(distinct_by_role[query_role]), distinct_by_role, bound_by_role


# ---------------- READOUTS (one per config) ----------------

def readout_C1_basis_norm(scene, role_vecs, query_role, codebook):
    """BASIS-ONLY null: bundle-norm estimate of bindings to role (multiplicity-confounded)."""
    N = scene.shape[0]
    u = role_vecs[query_role] * scene          # unbind (bipolar self-inverse) -- vector op, NO matrix
    est = float(np.dot(u, u) / N)              # ||u||^2/N ~ total bindings (counts multiplicity+crosstalk)
    return est


def readout_C0_graphwalk_trace(scene_bound_list, query_role_bound):
    """GRAPH-WALK CONTROL: trace of edge-outer-product matrix (the EXHAUSTED class).
    Builds W = sum_i b_i b_i^T / N over the query-role bound vectors, recovers count via trace.
    This is the ONLY readout permitted to form an adjacency-derived matrix-power (it IS the control)."""
    if not query_role_bound:
        return 0.0
    B = np.stack(query_role_bound, axis=0)     # (m, N) the bound vectors for the role
    N = B.shape[1]
    W = (B.T @ B) / N                          # N x N outer-product-sum (adjacency-derived matrix)
    return float(np.trace(W))                  # ~ total bindings (multiplicity-confounded), via the MATRIX


def readout_C2_cleanup_distinct(scene, role_vecs, query_role, codebook):
    """+PRIMITIVE: iterative-unbind + cleanup DISTINCT-count. Vector-native (corr+threshold),
    NO matrix-power. Repeats collapse (same filler -> one match) -> recovers DISTINCT count."""
    N = scene.shape[0]
    u = role_vecs[query_role] * scene          # unbind -- vector op
    sims = (codebook @ u) / N                  # correlation with each codebook atom (cleanup) -- vector op
    return int(np.sum(sims > CLEANUP_THRESH))  # count DISTINCT atoms above threshold


# ---------------- VECTOR-ENCODING GATE ASSERTION ----------------

def assert_vector_encoding_no_matrix_power():
    """Build-time gate: C1/C2/C3 readouts must touch NO adjacency matrix-power. Only C0 (the
    named control) forms a matrix. Enforced by construction here (C1=norm, C2=corr); this
    function documents + asserts the contract for the graded build."""
    import inspect
    for fn in (readout_C1_basis_norm, readout_C2_cleanup_distinct):
        src = inspect.getsource(fn)
        assert ".T @ " not in src and "np.trace" not in src and "matrix_power" not in src, \
            f"VECTOR-ENCODING GATE VIOLATION: {fn.__name__} forms an adjacency matrix-power"
    print("[gate] VECTOR-ENCODING: C1/C2 readouts touch no matrix-power (C0 is the named control). PASS", flush=True)


# ---------------- EVAL ----------------

def eval_seed(seed, N):
    rng = np.random.RandomState(seed)
    codebook = bipolar(rng, (VOCAB, N))
    role_vecs = [bipolar(rng, N) for _ in range(ROLES)]

    truth, c0, c1, c2 = [], [], [], []
    # sibling: at-least-k (k threshold) + most(A vs B)
    k_thresh = 4
    al_truth, al_c1, al_c2 = [], [], []
    most_truth, most_c1, most_c2 = [], [], []

    for _ in range(N_SCENES):
        qr = int(rng.randint(0, ROLES))
        scene, gt, distinct_by_role, bound_by_role = make_scene(rng, codebook, role_vecs, qr)
        # C0 control sees the role's bound vectors WITH MULTIPLICITY (fair: multiplicity-confounded,
        # role-isolated strong graph-walk control -- NOT the leaked distinct set)
        qr_bound = bound_by_role[qr]

        truth.append(gt)
        c1.append(readout_C1_basis_norm(scene, role_vecs, qr, codebook))
        c0.append(readout_C0_graphwalk_trace(scene, qr_bound))
        c2.append(readout_C2_cleanup_distinct(scene, role_vecs, qr, codebook))

        # at-least-k sibling
        al_truth.append(1 if gt >= k_thresh else 0)
        al_c1.append(1 if readout_C1_basis_norm(scene, role_vecs, qr, codebook) >= k_thresh else 0)
        al_c2.append(1 if readout_C2_cleanup_distinct(scene, role_vecs, qr, codebook) >= k_thresh else 0)

        # most(A vs B) sibling
        ra, rb = 0, 1
        gta = len(distinct_by_role[ra]); gtb = len(distinct_by_role[rb])
        most_truth.append(1 if gta > gtb else 0)
        most_c1.append(1 if readout_C1_basis_norm(scene, role_vecs, ra, codebook) >
                            readout_C1_basis_norm(scene, role_vecs, rb, codebook) else 0)
        most_c2.append(1 if readout_C2_cleanup_distinct(scene, role_vecs, ra, codebook) >
                            readout_C2_cleanup_distinct(scene, role_vecs, rb, codebook) else 0)

    truth = np.array(truth, float)
    def rmse(est): return float(np.sqrt(np.mean((np.array(est, float) - truth) ** 2)))
    def acc(pred, gt): return float(np.mean(np.array(pred) == np.array(gt)))

    return {
        "N": N, "seed": seed,
        "exact_count_rmse": {"C0": rmse(c0), "C1": rmse(c1), "C2": rmse(c2)},
        "at_least_k_acc": {"C1": acc(al_c1, al_truth), "C2": acc(al_c2, al_truth)},
        "most_acc": {"C1": acc(most_c1, most_truth), "C2": acc(most_c2, most_truth)},
    }


def eval_single_role_isolation(seed, N):
    """AMENDMENT v3b: single-role distinct-under-multiplicity sibling. ONLY the query role is
    present -> NO cross-role crosstalk (a) -> the C1 fair-null fails ONLY on multiplicity-dedup (b),
    so (C2-C1) attributes to genuine distinctness-counting, not crosstalk-filtering."""
    rng = np.random.RandomState(seed)
    codebook = bipolar(rng, (VOCAB, N))
    role = bipolar(rng, N)
    truth, c0, c1, c2 = [], [], [], []
    max_total = 0
    for _ in range(N_SCENES):
        n_distinct = int(rng.randint(1, 9))
        fillers = rng.choice(VOCAB, size=n_distinct, replace=False)
        scene = np.zeros(N); total = 0; bound = []
        for f in fillers:
            mult = int(rng.randint(1, 4))
            for _ in range(mult):
                b = role * codebook[f]; scene += b; bound.append(b); total += 1
        max_total = max(max_total, total)
        truth.append(n_distinct)
        # C0 graph-walk-trace control (single-role): trace(B^T B / N) = total bindings (multiplicity-
        # confounded), via the matrix -> counts total NOT distinct, like C1 but the named control.
        B = np.stack(bound, axis=0)
        c0.append(round(float(np.trace((B.T @ B) / N))))
        # C1 fair-null single-role: ||role*scene||^2/N ~ TOTAL bindings (counts multiplicity), NOT distinct.
        u = role * scene
        c1.append(round(float(np.dot(u, u) / N)))
        # C2: cleanup distinct-count (escapes both -- collapses multiplicity)
        sims = (codebook @ u) / N
        c2.append(int(np.sum(sims > CLEANUP_THRESH)))
    truth = np.array(truth, float)
    def rmse(e): return float(np.sqrt(np.mean((np.array(e, float) - truth) ** 2)))
    return {"c0_rmse": rmse(c0), "c1_rmse": rmse(c1), "c2_rmse": rmse(c2), "max_total_bindings": max_total}


# ===== PRE-REGISTERED GRADED VERDICT LOGIC (pre-registers HARD-PASS/FAIL bands in code BEFORE the graded
# run -- Lakatos no-ex-post-adjustment). Pure threshold logic; NO data. Applied at the graded run on GO. =====

def verdict_exact_count(c0_rmse, c1_rmse, c2_rmse, within_envelope):
    """AGGREGATE/RMSE sibling. C2 must ESCAPE C0 (beat, not match) + reduce C1 by >=2x + reach <=1.0,
    EVALUATED WITHIN the capacity envelope (else a low C2 is a capacity artifact, not a primitive fail)."""
    if not within_envelope:
        return ("CAPACITY-ARTIFACT", "outside capacity envelope; C2 score is not a primitive verdict")
    beats_c0 = c2_rmse < c0_rmse
    reduces_c1 = c1_rmse > 0 and (c1_rmse / max(c2_rmse, 1e-9)) >= PREREG["exact_count_rmse_reduction"]
    reaches_bar = c2_rmse <= PREREG["exact_count_C2_rmse_max"]
    if beats_c0 and reduces_c1 and reaches_bar:
        return ("HARD_PASS", f"C2 RMSE {c2_rmse:.2f} escapes C0 {c0_rmse:.2f} + >=2x C1 {c1_rmse:.2f} + <=1.0")
    if (not beats_c0) or c2_rmse >= c1_rmse:
        return ("HARD_FAIL", f"C2 RMSE {c2_rmse:.2f} does not escape (C0 {c0_rmse:.2f} / C1 {c1_rmse:.2f})")
    return ("MIDDLE_BAND", f"C2 RMSE {c2_rmse:.2f} partial (C0 {c0_rmse:.2f} / C1 {c1_rmse:.2f})")


def verdict_quantifier(c1_acc, c2_acc):
    """RATIO/accuracy sibling (at-least-k, most). gate-EVADE if C1 closes; else HARD-PASS needs
    C2>=0.80 AND (C2-C1)>=0.20 margin."""
    if c1_acc >= PREREG["evade_drop_accuracy"]:
        return ("EVADABLE-DROP", f"C1 {c1_acc:.3f} >= {PREREG['evade_drop_accuracy']}; task basis-evadable -> DROP")
    margin = c2_acc - c1_acc
    if c2_acc >= PREREG["C2_hardpass_accuracy"] and margin >= PREREG["C2_C1_margin"]:
        return ("HARD_PASS", f"C2 {c2_acc:.3f} >= 0.80 + margin {margin:.3f} >= 0.20 over C1 {c1_acc:.3f}")
    if c2_acc < 0.65:
        return ("HARD_FAIL", f"C2 {c2_acc:.3f} < 0.65; primitive does not close it")
    return ("MIDDLE_BAND", f"C2 {c2_acc:.3f} (margin {margin:.3f}); 0.65-0.80 band")


def _verdict_selftests():
    assert verdict_exact_count(5.0, 60.0, 0.9, True)[0] == "HARD_PASS"
    assert verdict_exact_count(5.0, 60.0, 6.0, True)[0] == "HARD_FAIL"   # doesn't beat C0
    assert verdict_exact_count(5.0, 60.0, 0.9, False)[0] == "CAPACITY-ARTIFACT"
    assert verdict_exact_count(5.0, 4.0, 3.0, True)[0] == "MIDDLE_BAND"  # beats C0 but <2x C1 + >1.0
    assert verdict_quantifier(0.55, 0.80)[0] == "HARD_PASS"
    assert verdict_quantifier(0.72, 0.95)[0] == "EVADABLE-DROP"           # C1 closes -> evadable
    assert verdict_quantifier(0.55, 0.60)[0] == "HARD_FAIL"               # C2 < 0.65
    assert verdict_quantifier(0.55, 0.72)[0] == "MIDDLE_BAND"
    print("[verdict-selftests] PASS: pre-registered exact-count(RMSE) + quantifier(accuracy) bands verified", flush=True)


_verdict_selftests()


def main():
    print(f"[start] cardinality Phase-B SKELETON run_mode={RUN_MODE} (SANITY ONLY; full run gated 2026-06-21)", flush=True)
    print(f"[start] N_LIST={N_LIST} VOCAB={VOCAB} N_SCENES={N_SCENES} ROLES={ROLES} seeds={SEEDS}", flush=True)
    assert_vector_encoding_no_matrix_power()

    for N in N_LIST:
        rows = [eval_seed(s, N) for s in SEEDS]
        ec0 = np.mean([r["exact_count_rmse"]["C0"] for r in rows])
        ec1 = np.mean([r["exact_count_rmse"]["C1"] for r in rows])
        ec2 = np.mean([r["exact_count_rmse"]["C2"] for r in rows])
        alk1 = np.mean([r["at_least_k_acc"]["C1"] for r in rows])
        alk2 = np.mean([r["at_least_k_acc"]["C2"] for r in rows])
        m1 = np.mean([r["most_acc"]["C1"] for r in rows])
        m2 = np.mean([r["most_acc"]["C2"] for r in rows])
        print(f"\n[N={N}] EXACT-COUNT RMSE (AGGREGATE): C0={ec0:.2f} C1={ec1:.2f} C2={ec2:.2f}", flush=True)
        print(f"[N={N}] AT-LEAST-{4} acc (RATIO):     C1={alk1:.3f} C2={alk2:.3f}", flush=True)
        print(f"[N={N}] MOST(A>B) acc (RATIO):        C1={m1:.3f} C2={m2:.3f}", flush=True)

        # directional SANITY checks (NOT graded pass; just confirm skeleton targets a real escape regime)
        escape_rmse = (ec2 <= ec1 / PREREG["exact_count_rmse_reduction"]) and (ec2 < ec0)
        escape_alk = (alk2 - alk1) >= PREREG["C2_C1_margin"]
        print(f"[N={N}] SANITY exact-count ESCAPE (C2 beats C1 by>=2x AND beats C0 control): {escape_rmse}", flush=True)
        print(f"[N={N}] SANITY at-least-k ESCAPE (C2-C1>={PREREG['C2_C1_margin']}): {escape_alk} (margin={alk2-alk1:.3f})", flush=True)

        # AMENDMENT v3b: single-role CONFOUND-ISOLATION sibling (distinctness confound, no crosstalk)
        sr_rows = [eval_single_role_isolation(s, N) for s in SEEDS]
        sr_c0 = np.mean([r["c0_rmse"] for r in sr_rows])
        sr_c1 = np.mean([r["c1_rmse"] for r in sr_rows])
        sr_c2 = np.mean([r["c2_rmse"] for r in sr_rows])
        sr_maxtot = max(r["max_total_bindings"] for r in sr_rows)
        print(f"[N={N}] SINGLE-ROLE ISOLATION RMSE (distinctness-only): C0={sr_c0:.2f} C1_fair_null={sr_c1:.2f} C2={sr_c2:.2f}", flush=True)

        # AMENDMENT v3a: CAPACITY-ENVELOPE gate (multi-role compound + single-role)
        max_total_multi = 8 * 3 * ROLES   # upper bound on total bindings in the compound task (max nd x max mult x roles)
        in_env_multi, frac_multi = capacity_status(max_total_multi, N, alpha=CAPACITY_ALPHA_MULTI)
        in_env_sr, frac_sr = capacity_status(sr_maxtot, N, alpha=CAPACITY_ALPHA_SINGLE)  # wider envelope for HARD claim
        print(f"[N={N}] CAPACITY-ENVELOPE: compound max_total~{max_total_multi} frac={frac_multi:.4f} within={in_env_multi} "
              f"(alpha_multi={CAPACITY_ALPHA_MULTI}) | single-role(HARD) max_total={sr_maxtot} frac={frac_sr:.4f} "
              f"within={in_env_sr} (alpha_single={CAPACITY_ALPHA_SINGLE})", flush=True)
        if not in_env_multi:
            print(f"[N={N}] CAPACITY NOTE: compound task EXCEEDS envelope at this N -> a C2 low score here is a "
                  f"CAPACITY ARTIFACT, not a primitive HARD-FAIL (raise N or cap density for the graded run).", flush=True)

        # ===== GRADED VERDICTS (pre-registered compute_verdict applied to real metrics) =====
        v_ec_single = verdict_exact_count(sr_c0, sr_c1, sr_c2, in_env_sr)       # HARD exact-count claim (clean confound)
        v_ec_multi = verdict_exact_count(ec0, ec1, ec2, in_env_multi)            # compound (capacity-limited at high N)
        v_alk = verdict_quantifier(alk1, alk2)
        v_most = verdict_quantifier(m1, m2)
        print(f"[N={N}] GRADED VERDICT exact-count SINGLE-ROLE (HARD distinctness claim): {v_ec_single[0]} -- {v_ec_single[1]}", flush=True)
        print(f"[N={N}] GRADED VERDICT exact-count compound: {v_ec_multi[0]} -- {v_ec_multi[1]}", flush=True)
        print(f"[N={N}] GRADED VERDICT at-least-{4}: {v_alk[0]} -- {v_alk[1]}", flush=True)
        print(f"[N={N}] GRADED VERDICT most(A>B): {v_most[0]} -- {v_most[1]}", flush=True)

        # SEED-VARIANCE / mode-(iii) drift check (Skunkworks run_mode tier-A requirement): report per-seed
        # spread; wide spread = drift-to-attractor (Singh-Eliasmith 2006) -> NOT tier-A corroboration.
        sr_c2_std = float(np.std([r["c2_rmse"] for r in sr_rows]))
        alk2_std = float(np.std([r["at_least_k_acc"]["C2"] for r in rows]))
        m2_std = float(np.std([r["most_acc"]["C2"] for r in rows]))
        drift = (alk2_std > 0.40) or (m2_std > 0.40)   # accuracy seed-std > 0.40 = mode-iii drift (Drill-1)
        print(f"[N={N}] SEED-VARIANCE (mode-iii): exact-count(SR) C2 std={sr_c2_std:.3f} | at-least-k C2 std={alk2_std:.3f} | most C2 std={m2_std:.3f} -> {'DRIFT (mode-iii FAIL)' if drift else 'tight (no drift; tier-A OK)'}", flush=True)

    print("\n[skeleton] SANITY COMPLETE. Pre-registered gates baked in; graded run gated to Phase-B GO 2026-06-21", flush=True)
    print("[skeleton] C3 (internal-abstraction-discovery) = stub; 158b Task 3 probe verifies discovery (P_deflated=0.40)", flush=True)
    print(f"[skeleton] reconciled prereg: {PREREG}", flush=True)


if __name__ == "__main__":
    main()
