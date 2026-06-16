"""
PHASE-B PREP feasibility probe -- vector-encoding cardinality recoverable by a PURE-VECTOR
readout, distinct from the graph-walk trace control?

FEASIBILITY / INSTRUMENTATION ONLY. Not the graded Phase-B build. No pre-registered
thresholds, no capability claim. Purpose: validate the design constraint in the 11:05
readiness memo (cardinality must be VECTOR-ENCODING, with the trace formula as control)
BEFORE the 2026-06-21 build commits to that design. Verify-before-asserting on my own note.

Question: can count k be encoded in a hypervector and recovered by a pure-vector operation
(squared-norm estimate), monotone in k -- WITHOUT forming an adjacency-derived matrix?
And does the graph-walk trace control (trace of sum_i x_i x_i^T / N) recover the SAME k via
a DIFFERENT (matrix) mechanism? If both recover k but the vector path needs no matrix, the
Phase-B vector-encoding arm is FEASIBLE and the trace formula is a legitimate named control.

CPU, N=4096, bipolar. ASCII only.
"""
import sys
import numpy as np

N = 4096
K_RANGE = list(range(1, 13))   # counts 1..12
SEEDS = [7, 17, 23, 31, 41]


def pearson(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    xc = x - x.mean(); yc = y - y.mean()
    d = np.linalg.norm(xc) * np.linalg.norm(yc)
    return float(np.dot(xc, yc) / d) if d > 1e-12 else float("nan")


def run_seed(seed):
    rng = np.random.RandomState(seed)
    # one fixed role vector; fillers are fresh random bipolar per scene
    role = rng.choice([-1.0, 1.0], size=N)

    vec_estimates = []   # pure-vector norm-based count estimate
    trace_estimates = [] # graph-walk control: trace of outer-product matrix
    truth = []

    for k in K_RANGE:
        fillers = rng.choice([-1.0, 1.0], size=(k, N))
        bound = fillers * role  # bind(role, x_i) = elementwise product (bipolar)
        scene = bound.sum(axis=0)  # bundle k role-filler bindings (superposition)

        # PURE-VECTOR readout: E[||scene||^2] = k*N for k orthogonal-ish bipolar vectors.
        # estimate k_hat = ||scene||^2 / N  -- touches NO matrix.
        vec_k = float(np.dot(scene, scene) / N)

        # GRAPH-WALK CONTROL: form W = sum_i b_i b_i^T / N, recover via trace(W).
        # trace(W) = sum_i ||b_i||^2 / N = k exactly for bipolar -- but requires the matrix.
        W = (bound.T @ bound) / N   # N x N outer-product-sum (the adjacency-derived matrix)
        trace_k = float(np.trace(W))

        vec_estimates.append(vec_k)
        trace_estimates.append(trace_k)
        truth.append(k)

    return {
        "seed": seed,
        "pearson_vec": pearson(vec_estimates, truth),
        "pearson_trace": pearson(trace_estimates, truth),
        "vec_est": vec_estimates,
        "trace_est": trace_estimates,
    }


def main():
    print(f"[start] PHASE-B PREP cardinality vector-encoding feasibility probe N={N} k={K_RANGE[0]}..{K_RANGE[-1]} seeds={SEEDS}", flush=True)
    rows = [run_seed(s) for s in SEEDS]
    pv = np.mean([r["pearson_vec"] for r in rows])
    pt = np.mean([r["pearson_trace"] for r in rows])

    # mean abs error of the pure-vector estimate vs truth (across seeds, across k)
    errs = []
    for r in rows:
        for est, t in zip(r["vec_est"], K_RANGE):
            errs.append(abs(est - t))
    mae_vec = float(np.mean(errs))

    print(f"[result] pure-vector norm readout:  mean Pearson(k_hat, k) = {pv:.4f}  | MAE = {mae_vec:.3f}", flush=True)
    print(f"[result] graph-walk trace control:  mean Pearson(trace, k) = {pt:.4f}", flush=True)
    # show one seed's raw estimates for sanity
    r0 = rows[0]
    print(f"[seed {r0['seed']}] truth   : {K_RANGE}", flush=True)
    print(f"[seed {r0['seed']}] vec_hat : {[round(x,2) for x in r0['vec_est']]}", flush=True)
    print(f"[seed {r0['seed']}] trace   : {[round(x,2) for x in r0['trace_est']]}", flush=True)

    vec_feasible = pv > 0.95 and mae_vec < 1.0
    print("", flush=True)
    if vec_feasible:
        print("[FEASIBILITY] PASS: pure-vector norm readout recovers count monotone in k, no matrix formed.", flush=True)
        print("[FEASIBILITY] Phase-B cardinality VECTOR-ENCODING arm is feasible; trace control recovers", flush=True)
        print("[FEASIBILITY] the same k via the matrix mechanism -> legitimate named graph-walk control.", flush=True)
    else:
        print("[FEASIBILITY] BLOCKER: pure-vector readout did NOT recover count cleanly -- surface before build.", flush=True)


if __name__ == "__main__":
    main()
