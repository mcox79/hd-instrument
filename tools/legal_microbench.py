"""Microbench: measure per-seed cost of the legal-1000 algorithm at VC=4000 to estimate progress. Standalone."""
import time, math
import numpy as np


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi
    return np.exp(1j * ang).astype(np.complex64)


g = np.random.default_rng(82); N = 8192; VC = 4000; AVG = 3; THRESH = 0.18
t_build0 = time.perf_counter()
cases = cphasor(VC, N, g); CITES = cphasor(1, N, g)[0]; adj = {i: [] for i in range(VC)}; M = np.zeros(N, dtype=np.complex64)
for i in range(VC):
    outs = g.choice(VC, size=int(g.integers(1, AVG + 2)), replace=False)
    for o in outs:
        if int(o) != i and int(o) not in adj[i]:
            adj[i].append(int(o)); M = M + cases[i] * CITES * cases[int(o)]
t_build = time.perf_counter() - t_build0


def tclose(seed, hops=3):
    seen = set(); fr = {seed}
    for _ in range(hops):
        nf = set()
        for u in fr:
            nf |= set(adj[u]) - seen
        seen |= nf; fr = nf
    return seen


def snow(seed, hops=3):
    reached = set(); fr = {seed}
    for _ in range(hops):
        nf = set()
        for u in fr:
            sc = (cases @ np.conj(M * np.conj(cases[u] * CITES))).real / N
            for v in np.where(sc > THRESH)[0].tolist():
                if v not in reached and v != u:
                    nf.add(int(v))
        reached |= nf; fr = nf
        if not fr:
            break
    return reached


NS = 3
seeds = g.choice(VC, NS, replace=False)
t0 = time.perf_counter()
for seed in seeds:
    tc = tclose(int(seed))
    if tc:
        _ = len(tc & snow(int(seed))) / len(tc)
t_seeds = time.perf_counter() - t0
per_seed = t_seeds / NS
print("corpus_build_s=%.2f | per_seed_s=%.3f (avg over %d) | est_total_1000_s=%.1f = %.1f min"
      % (t_build, per_seed, NS, t_build + 1000 * per_seed, (t_build + 1000 * per_seed) / 60), flush=True)
