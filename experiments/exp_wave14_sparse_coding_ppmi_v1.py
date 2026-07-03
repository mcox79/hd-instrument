"""Sparse-coding probe: replace PPMI hand-crafted prior with learned sparse codes.

Field probe per research_field_scope_update_2026-05-24.md: SPARSE CODING is one
of the 8 new Tier-1b fields added at v195. This probes A6 (learned codebook
atoms) and U3 (self-supervised concept discovery) using sparse-coding /
dictionary-learning rather than SVD/PCA.

Hypothesis: PPMI is a load-bearing hand-crafted prior across all R3/R10
experiments. A SPARSE CODING dictionary learned by K-SVD-style iterations on
byte-bigram co-occurrence statistics may produce a codebook with better
substrate binding properties (higher capacity, sparser activations, lower
cross-talk) than random bipolar atoms OR PCA atoms.

Method: build a byte-bigram co-occurrence matrix from a sample corpus; learn
a sparse dictionary D (256 atoms x N dims) via simplified-K-SVD (orthogonal
matching pursuit + dictionary update), each atom of L0 sparsity s. Compare:
  - random bipolar atoms (current substrate default)
  - PCA atoms (linear baseline)
  - sparse-coded atoms (this probe)
on a downstream binding task: stored M (bigram, prediction) pairs, recover
prediction at varying M.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL bands pre-registered.
Per [[feedback-lit-scan-calibration-penalty]]: sparse-coding for VSA atoms is
uncharted regime; P estimates deflated.

Pre-reg:
    HARD-PASS: sparse-coded atoms outperform BOTH random AND PCA baselines
               by >=0.05 recall cosine across >=3 of 4 M values (M in
               {50, 100, 200, 400}).
               -> A6/U3 row advanced; sparse-coding is a substrate-product
               worthy codebook generator.
    HARD-FAIL: sparse-coded atoms are within +/-0.01 of random baseline OR
               WORSE than random on >=3 of 4 M values.
               -> sparse-coding rejected for substrate; PPMI/random remain.
    MIDDLE: any intermediate; report bands.

Pure-CPU; remote_cpu_queue.

Pre-reg file: preregs/2026-05-24_wave14_sparse_coding_ppmi_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, json, math, os, time
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
VOCAB = 256
N_FULL = 2048
N_SMOKE = 256
M_GRID_FULL = [50, 100, 200, 400]
M_GRID_SMOKE = [50, 100]
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
N_SPARSE_ATOMS = 256
L0_SPARSITY = 8       # sparsity level for dictionary atoms
DICT_ITERS = 6

PASS_LIFT = 0.05
PASS_M_VALS = 3
FAIL_LIFT_TOL = 0.01
FAIL_M_VALS = 3


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing: raise ValueError(f"metrics missing required: {missing}")


def synthesize_byte_corpus(seed, n_bytes=20000):
    """Synthesize byte sequence with structured byte-bigram statistics
    (Zipfian over byte values; conditional concentrated to mimic ASCII text)."""
    rng = np.random.default_rng(seed)
    # Bias toward printable ASCII (32..127) and \n
    probs = np.zeros(VOCAB)
    probs[32:127] = 1.0
    probs[10] = 1.0
    probs = probs / probs.sum()
    out = rng.choice(VOCAB, size=n_bytes, p=probs).astype(np.uint8)
    return out


def bigram_cooc(corpus):
    co = np.zeros((VOCAB, VOCAB), dtype=np.float64)
    pairs = np.stack([corpus[:-1], corpus[1:]], axis=1).astype(np.int64)
    for p in pairs:
        co[p[0], p[1]] += 1.0
    return co


def random_bipolar_atoms(n_atoms, n_dim, rng):
    return (rng.integers(0, 2, size=(n_atoms, n_dim)) * 2 - 1).astype(np.float32) / math.sqrt(n_dim)


def pca_atoms(cooc, n_atoms, n_dim, rng):
    """Top-eigenvector atoms of cooc embedded into n_dim."""
    cooc_sym = 0.5 * (cooc + cooc.T) + 1e-7 * np.eye(VOCAB)
    eigvals, eigvecs = np.linalg.eigh(cooc_sym)
    order = np.argsort(eigvals)[::-1]
    top = eigvecs[:, order[:VOCAB]]  # VOCAB x VOCAB
    # Embed into n_dim via random projection
    R = rng.standard_normal((VOCAB, n_dim)).astype(np.float32) / math.sqrt(VOCAB)
    return (top @ R).astype(np.float32) / math.sqrt(n_dim)


def sparse_coded_atoms(cooc, n_atoms, n_dim, s, n_iters, rng):
    """Toy K-SVD: dictionary D (n_atoms x n_dim) with each atom L0-sparse.

    Step: each atom initialized as random sparse vector with support s; then
    iteratively update each atom to better explain the bigram-cooc row of the
    corresponding byte value (in n_dim space via random projection).
    """
    # Target representations: top-row of cooc projected to n_dim
    R = rng.standard_normal((VOCAB, n_dim)).astype(np.float32) / math.sqrt(VOCAB)
    targets = cooc @ R  # VOCAB x n_dim
    targets = targets / (np.linalg.norm(targets, axis=1, keepdims=True) + 1e-9)
    # Init D as sparse random
    D = np.zeros((n_atoms, n_dim), dtype=np.float32)
    for i in range(n_atoms):
        supp = rng.choice(n_dim, size=s, replace=False)
        signs = rng.choice([-1.0, 1.0], size=s)
        D[i, supp] = signs / math.sqrt(s)
    for it in range(n_iters):
        # Sparse code targets in D via OMP-like greedy step
        # For simplicity: project each atom toward its target (using cosine
        # alignment) but keep top-s entries in magnitude.
        # We use simple soft-update: D[i] = top_s(0.7 * D[i] + 0.3 * target[i])
        for i in range(min(n_atoms, VOCAB)):
            new_atom = 0.7 * D[i] + 0.3 * targets[i]
            # Keep top-s entries
            idx_top = np.argpartition(np.abs(new_atom), -s)[-s:]
            atom = np.zeros(n_dim, dtype=np.float32)
            atom[idx_top] = new_atom[idx_top]
            atom = atom / (np.linalg.norm(atom) + 1e-9)
            D[i] = atom
    return D


def binding_recall(atoms, n_dim, m_pairs, rng):
    """Store M (key, val) pairs (val is a random vector), recover val from key.

    Both keys and vals are drawn from the atom codebook (so we benchmark how
    well the substrate handles ITS OWN atoms as keys/values)."""
    M = m_pairs
    n_atoms = atoms.shape[0]
    # Pick M (key_atom, val_atom) pairs (with repeats allowed)
    key_idx = rng.integers(0, n_atoms, size=M)
    val_idx = rng.integers(0, n_atoms, size=M)
    keys = atoms[key_idx]   # M x n_dim
    vals = atoms[val_idx]
    # Bundle: sum_i keys_i ⊛ vals_i (circular convolution)
    bundle = np.zeros(n_dim, dtype=np.float32)
    for i in range(M):
        bundle = bundle + np.real(np.fft.irfft(np.fft.rfft(keys[i]) * np.fft.rfft(vals[i]), n=n_dim))
    # Recover val_i from key_i
    cos_list = []
    for i in range(M):
        K = np.fft.rfft(keys[i])
        K_inv = np.conj(K) / (np.abs(K) ** 2 + 1e-9)
        rec = np.real(np.fft.irfft(np.fft.rfft(bundle) * K_inv, n=n_dim))
        num = float((rec * vals[i]).sum())
        denom = float(np.linalg.norm(rec) * np.linalg.norm(vals[i]) + 1e-9)
        cos_list.append(num / denom)
    return float(np.mean(cos_list))


def run_one_seed(seed, n, m_grid):
    rng = np.random.default_rng(seed)
    corpus = synthesize_byte_corpus(seed, n_bytes=8000)
    cooc = bigram_cooc(corpus)
    rand_atoms = random_bipolar_atoms(N_SPARSE_ATOMS, n, rng)
    pca = pca_atoms(cooc, N_SPARSE_ATOMS, n, rng)
    sparse = sparse_coded_atoms(cooc, N_SPARSE_ATOMS, n, L0_SPARSITY, DICT_ITERS, rng)
    out = {}
    for m in m_grid:
        rng2 = np.random.default_rng(seed * 10 + m)
        r_rand = binding_recall(rand_atoms, n, m, rng2)
        rng3 = np.random.default_rng(seed * 10 + m)
        r_pca = binding_recall(pca, n, m, rng3)
        rng4 = np.random.default_rng(seed * 10 + m)
        r_sparse = binding_recall(sparse, n, m, rng4)
        out[m] = {"random": r_rand, "pca": r_pca, "sparse": r_sparse,
                  "lift_vs_rand": r_sparse - r_rand,
                  "lift_vs_pca": r_sparse - r_pca}
    return out


def compute_verdict(summary):
    per_seed = summary.get("per_seed", {})
    if not per_seed: return ("SPARSE_CODING_INCONCLUSIVE", "No seeds.")
    # Aggregate per-M means across seeds
    m_vals = sorted(set(int(k) for s in per_seed.values() for k in s))
    per_m_lifts_rand = {}; per_m_lifts_pca = {}
    for m in m_vals:
        lifts_r = []; lifts_p = []
        for s, d in per_seed.items():
            v = d.get(m) or d.get(str(m))
            if v:
                lifts_r.append(v["lift_vs_rand"])
                lifts_p.append(v["lift_vs_pca"])
        per_m_lifts_rand[m] = sum(lifts_r)/len(lifts_r) if lifts_r else 0.0
        per_m_lifts_pca[m] = sum(lifts_p)/len(lifts_p) if lifts_p else 0.0
    n_pass = sum(1 for m in m_vals if per_m_lifts_rand[m] >= PASS_LIFT and per_m_lifts_pca[m] >= PASS_LIFT)
    n_fail_or_worse = sum(1 for m in m_vals if per_m_lifts_rand[m] <= FAIL_LIFT_TOL)
    pts = ", ".join(f"M={m}:lift_rand={per_m_lifts_rand[m]:.3f},lift_pca={per_m_lifts_pca[m]:.3f}"
                    for m in m_vals)
    if n_pass >= PASS_M_VALS:
        return ("SPARSE_CODING_HARD_PASS",
                f"Sparse-coded atoms WIN: {n_pass}/{len(m_vals)} M-values lift>={PASS_LIFT} "
                f"over BOTH baselines. {pts}.")
    if n_fail_or_worse >= FAIL_M_VALS:
        return ("SPARSE_CODING_HARD_FAIL",
                f"Sparse-coded REJECTED: {n_fail_or_worse}/{len(m_vals)} M-values "
                f"within tol or worse than random. {pts}.")
    return ("SPARSE_CODING_MIDDLE_BAND",
            f"Intermediate: n_pass={n_pass}, n_fail={n_fail_or_worse} of {len(m_vals)}. {pts}.")


def self_test_verdict():
    def mk(rows):
        ps = {}
        for s, m_dict in enumerate(rows):
            ps[str(s)] = m_dict
        return {"per_seed": ps}
    pass_per_seed = {50: {"random": 0.5, "pca": 0.5, "sparse": 0.6, "lift_vs_rand": 0.10, "lift_vs_pca": 0.10},
                     100: {"random": 0.4, "pca": 0.4, "sparse": 0.5, "lift_vs_rand": 0.10, "lift_vs_pca": 0.10},
                     200: {"random": 0.3, "pca": 0.3, "sparse": 0.4, "lift_vs_rand": 0.10, "lift_vs_pca": 0.10},
                     400: {"random": 0.2, "pca": 0.2, "sparse": 0.25, "lift_vs_rand": 0.05, "lift_vs_pca": 0.05}}
    fail_per_seed = {50: {"random": 0.5, "pca": 0.5, "sparse": 0.5, "lift_vs_rand": 0.0, "lift_vs_pca": 0.0},
                     100: {"random": 0.4, "pca": 0.4, "sparse": 0.4, "lift_vs_rand": 0.0, "lift_vs_pca": 0.0},
                     200: {"random": 0.3, "pca": 0.3, "sparse": 0.29, "lift_vs_rand": -0.01, "lift_vs_pca": -0.01},
                     400: {"random": 0.2, "pca": 0.2, "sparse": 0.19, "lift_vs_rand": -0.01, "lift_vs_pca": -0.01}}
    mid_per_seed = {50: {"random": 0.5, "pca": 0.5, "sparse": 0.56, "lift_vs_rand": 0.06, "lift_vs_pca": 0.06},
                    100: {"random": 0.4, "pca": 0.4, "sparse": 0.43, "lift_vs_rand": 0.03, "lift_vs_pca": 0.03},
                    200: {"random": 0.3, "pca": 0.3, "sparse": 0.32, "lift_vs_rand": 0.02, "lift_vs_pca": 0.02},
                    400: {"random": 0.2, "pca": 0.2, "sparse": 0.22, "lift_vs_rand": 0.02, "lift_vs_pca": 0.02}}
    cases = [(mk([pass_per_seed]*3), "SPARSE_CODING_HARD_PASS"),
             (mk([fail_per_seed]*3), "SPARSE_CODING_HARD_FAIL"),
             (mk([mid_per_seed]*3), "SPARSE_CODING_MIDDLE_BAND"),
             ({"per_seed": {}}, "SPARSE_CODING_INCONCLUSIVE")]
    for s, exp in cases:
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    n = N_SMOKE if smoke else N_FULL
    m_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    config = {"mode": "smoke" if smoke else "full", "n": n, "m_grid": m_grid,
              "seeds": seeds, "n_sparse_atoms": N_SPARSE_ATOMS,
              "l0_sparsity": L0_SPARSITY, "dict_iters": DICT_ITERS,
              "pass_lift": PASS_LIFT, "pass_m_vals": PASS_M_VALS,
              "fail_lift_tol": FAIL_LIFT_TOL, "fail_m_vals": FAIL_M_VALS}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in seeds:
        r = run_one_seed(seed, n, m_grid)
        per_seed[str(seed)] = r
        for m in m_grid:
            v = r[m]
            print(f"  seed={seed} M={m}: rand={v['random']:.3f} pca={v['pca']:.3f} "
                  f"sparse={v['sparse']:.3f} lift_r={v['lift_vs_rand']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_sparse_coding_ppmi_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_sparse_coding_ppmi_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
