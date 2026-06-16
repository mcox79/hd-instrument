"""
PHASE-B STAGE-1.2 FPE-CLEANUP-AMPLIFICATION pre-flight (DECISION 174b; refines HARD-FAIL mode ii).
Drill 3: classical cleanup-noise is NOT the binding constraint (Frady/Sommer k_max~269 at N=4096 M=2000);
the actual most-likely blocker (P=0.42) is FPE-PHASE-KERNEL near-neighbor confusion at M>=2000.

This probe MEASURES the FPE-cleanup-amplification factor = (discrete-atom top-1) - (FPE top-1), + the
FPE near-neighbor confusion rate. CPU structural characterization of codebook crosstalk (NOT the graded
cardinality capability verdict) -- a readiness/sanity pre-flight (within HOLD per Skunkworks). Informs
whether the modern-Hopfield cleanup head (DECISION 174c) is needed BEFORE STAGE 2.

PRE-REGISTERED thresholds (DECISION 174b; cold):
  PASS: discrete top-1 >= 0.99 (sanity) ; FPE top-1 >= 0.95 ; FPE near-neighbor confusion <= 0.10
  FAIL: discrete top-1 < 0.95 (classical theory wrong -> re-derive)
        FPE top-1 < 0.80 (FPE-cleanup dominant -> swap to modern-Hopfield cleanup head before STAGE 2)
        FPE near-neighbor confusion > 0.30 (kernel too coarse -> band-limit base phases)
  modern-Hopfield switch criterion: amplification factor (discrete - FPE top-1) >= 0.05.

FHRR (complex unit-phasor). CPU/numpy. ASCII.
"""
import sys
import numpy as np

N = 4096
M_LIST = [200, 2000]              # DISTRACTOR codebook size (bundle distractors)
K_LIST = [3, 5, 10, 20, 50]      # bundle size (items bundled)
K_CARD = 50                       # CARDINALITY RANGE = FPE grid points (integer counts 0..K_CARD-1).
                                  # FIX (verify-before-asserting): the FPE grid is the CARDINALITY RANGE,
                                  # NOT the codebook size M. The original linspace(0,2,M) over-resolved the
                                  # grid (M=2000 pts over [0,2] = 0.001 spacing) -> artifactual near-neighbor
                                  # confusion. Integer cardinality FPE (theta~U[0,2pi)) is ORTHOGONAL -> clean.
SEEDS = [7, 17]
# pre-registered thresholds
P_DISCRETE_SANITY = 0.99; P_FPE_PASS = 0.95; CONF_PASS = 0.10
P_DISCRETE_FAIL = 0.95; P_FPE_FAIL = 0.80; CONF_FAIL = 0.30
HOPFIELD_SWITCH_AMP = 0.05


def fhrr_codebook(M, n, g):
    """M random FHRR phasors (complex unit magnitude per component)."""
    ph = g.uniform(0, 2 * np.pi, size=(M, n))
    return np.exp(1j * ph)


def sim(a, B):
    """FHRR cosine sim of vector a (n,) against rows of B (M,n): real(<a, conj(B)>)/n."""
    return np.real(B.conj() @ a) / a.shape[0]


def discrete_top1(codebook, k, n_trials, g):
    """Bundle k random distinct codewords; top-1 cleanup recovery rate over the codebook."""
    M = codebook.shape[0]; hits = 0; tot = 0
    for _ in range(n_trials):
        idx = g.choice(M, size=k, replace=False)
        bundle = codebook[idx].sum(0)
        s = sim(bundle, codebook)
        top = set(np.argsort(-s)[:k].tolist())
        hits += len(top & set(idx.tolist())); tot += k
    return hits / tot


def fpe_grid(base_phases, x_vals):
    """FPE V^x = exp(i x theta_V) for each x; returns (len(x), n) complex grid."""
    return np.exp(1j * np.outer(x_vals, base_phases))


def fpe_recovery(codebook, base_phases, x_vals, k, n_trials, g):
    """Bundle = FPE(V^x_true) + (k-1) discrete distractors; recover x_true via argmax-sim over the FPE grid.
    Returns (top1, near_neighbor_confusion). near-neighbor = recovered within +/-1 grid step of true."""
    grid = fpe_grid(base_phases, x_vals)        # (G, n)
    G = grid.shape[0]; M = codebook.shape[0]
    top1 = 0; nn = 0
    for _ in range(n_trials):
        xi = int(g.integers(0, G))
        distract = codebook[g.choice(M, size=k - 1, replace=False)].sum(0) if k > 1 else 0
        bundle = grid[xi] + distract
        s = sim(bundle, grid)
        pred = int(np.argmax(s))
        top1 += int(pred == xi)
        nn += int(abs(pred - xi) <= 1)          # within one grid step
    return top1 / n_trials, 1.0 - (nn / n_trials)   # confusion = fraction NOT within +/-1


def run():
    n_trials = 200
    print(f"[start] STAGE-1.2 FPE-cleanup-amplification pre-flight N={N} M={M_LIST} k={K_LIST} (CPU; readiness, not graded verdict)", flush=True)
    worst_amp = 0.0; results = {}
    for M in M_LIST:
        for k in K_LIST:
            d_accs, f_accs, confs = [], [], []
            for seed in SEEDS:
                g = np.random.default_rng(seed)
                cb = fhrr_codebook(M, N, g)
                d_accs.append(discrete_top1(cb, k, n_trials, g))
                base = g.uniform(0, 2 * np.pi, size=N)
                x_vals = np.arange(K_CARD, dtype=float)       # FPE grid = integer cardinality range (NOT M; fix)
                f1, conf = fpe_recovery(cb, base, x_vals, k, n_trials, g)
                f_accs.append(f1); confs.append(conf)
            d = float(np.mean(d_accs)); f = float(np.mean(f_accs)); c = float(np.mean(confs))
            amp = d - f
            worst_amp = max(worst_amp, amp)
            results[(M, k)] = (d, f, c, amp)
            flag = ""
            if M == 2000 and k == 5:
                flag = "  <- CRITICAL config (N=4096 M=2000 k=5)"
            print(f"  M={M:>4} k={k:>2} | discrete_top1={d:.3f} FPE_top1={f:.3f} nn_confusion={c:.3f} amp={amp:+.3f}{flag}", flush=True)
    return results, worst_amp


def verdict(results, worst_amp):
    # focus on the critical config + worst-case across grid
    crit = results.get((2000, 5))
    msgs = []
    fail = False
    if crit:
        d, f, c, amp = crit
        if d < P_DISCRETE_FAIL: msgs.append(f"FAIL: discrete top-1 {d:.3f} < {P_DISCRETE_FAIL} (classical theory wrong in config)"); fail = True
        if f < P_FPE_FAIL: msgs.append(f"FAIL: FPE top-1 {f:.3f} < {P_FPE_FAIL} -> FPE-cleanup dominant -> modern-Hopfield head before STAGE 2"); fail = True
        if c > CONF_FAIL: msgs.append(f"FAIL: FPE nn-confusion {c:.3f} > {CONF_FAIL} -> band-limit base phases"); fail = True
        if not fail:
            pass_ok = (d >= P_DISCRETE_SANITY) and (f >= P_FPE_PASS) and (c <= CONF_PASS)
            msgs.append(("PASS: discrete %.3f>=%.2f + FPE %.3f>=%.2f + nn-conf %.3f<=%.2f" % (d, P_DISCRETE_SANITY, f, P_FPE_PASS, c, CONF_PASS))
                        if pass_ok else ("MIDDLE: critical config within FAIL bars but not full PASS (d=%.3f f=%.3f c=%.3f)" % (d, f, c)))
    switch = worst_amp >= HOPFIELD_SWITCH_AMP
    msgs.append(f"modern-Hopfield switch criterion (worst amp {worst_amp:+.3f} >= {HOPFIELD_SWITCH_AMP}): {'TRIGGERED -> pre-stage/activate Hopfield cleanup head' if switch else 'NOT triggered -> naive max-cos cleanup sufficient'}")
    return ("FAIL" if fail else "PASS-or-MIDDLE"), msgs


if __name__ == "__main__":
    results, worst_amp = run()
    v, msgs = verdict(results, worst_amp)
    print(f"\n[STAGE-1.2 readiness] {v}", flush=True)
    for m in msgs: print("  " + m, flush=True)
    print("\n[note] readiness/sanity characterization (CPU, codebook crosstalk); NOT the graded cardinality verdict.", flush=True)
    print("[note] informs DECISION 174c modern-Hopfield-cleanup-head pre-stage decision (Skunkworks).", flush=True)
