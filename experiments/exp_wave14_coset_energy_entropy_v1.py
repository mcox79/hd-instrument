"""Coset-census energy vs entropy mechanism analysis.

Audit Rank 6 (research_comprehensive_audit_2026-05-23.md):
  v152 found substrate AVOIDS RM(1,16) coset with frac=0.000.
  v153 found endpoints uniform across 3 nonlinear cosets.
  MECHANISM IS OPEN: two hypotheses:
    (H1) Energetic: RM(1,16) codewords are saddles of W-dynamics (low W-energy).
    (H2) Entropic: linear coset has lower entropy density than nonlinear cosets.

Key insight: since substrate produces 0 RM(1,16) endpoints, we CANNOT compare
energy directly from trajectory endpoints. Instead we compare:
  - Synthetic RM(1,16) energy: energy of random RM(1,16)-class codewords under W
    (these are the states the substrate WOULD land in if it were linear; their
     energy under W tells us if they are attractors or repellers)
  - Actual endpoint energy: energy of nonlinear attractor endpoints under W

H1 (energetic): synthetic_RM_energy << endpoint_energy
  -> RM(1,16) codewords are NOT attractors of W (low W-energy = saddles/repellers)
H2 (entropic): We compare W-field alignment of RM(1,16) codewords vs random codewords
  -> RM(1,16) being flat/linear has lower field alignment (spread)

Verdict labels:
  COSET_ENERGY_H1      -- energetic: synthetic_RM_energy << endpoint_energy
  COSET_ENTROPY_H2     -- alignment: RM codewords have lower W-field std than endpoints
  COSET_BOTH_H1_H2     -- compound
  COSET_MECHANISM_OPEN -- no significant difference
  COSET_MECHANISM_INCONCLUSIVE -- infrastructure problem

Pure CPU. No GPU required.
Memory budget: W = N x N float32; N=4096 -> 64 MB. Peak ~200 MB.
Expected runtime: ~15-20 min CPU at FULL (N=4096, K=100, 3 seeds).
Smoke: ~2 min (N=1024, K=20, 1 seed).
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, json, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# Hard pass/fail thresholds
ENERGY_EFFECT_THRESHOLD = 0.05   # synthetic_RM_energy must be this much lower than endpoint_energy
ALIGN_EFFECT_THRESHOLD = 0.05    # RM field-std must be this much lower than endpoint field-std
N_RM_SYNTHETIC = 100             # number of synthetic RM(1,16)-class codewords to test
N_SUBCLUSTERS = 4               # k for mini-entropy clustering


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"missing keys: {set(d.keys())}")


def compute_verdict(summary):
    if "energy_delta" not in summary or "align_delta" not in summary:
        return ("COSET_MECHANISM_INCONCLUSIVE", "Missing energy_delta or align_delta.")
    e_delta = summary["energy_delta"]   # synthetic_RM_energy - endpoint_energy; negative = H1 supported
    a_delta = summary["align_delta"]    # RM_field_std - endpoint_field_std; negative = H2 supported
    h1 = e_delta < -ENERGY_EFFECT_THRESHOLD
    h2 = a_delta < -ALIGN_EFFECT_THRESHOLD
    if h1 and h2:
        return ("COSET_BOTH_H1_H2",
                f"Compound suppression: energy_delta={e_delta:.4f} < -{ENERGY_EFFECT_THRESHOLD} "
                f"AND align_delta={a_delta:.4f} < -{ALIGN_EFFECT_THRESHOLD}. "
                "Both energetic (RM codewords lower W-energy = not attractors) and "
                "alignment (RM lower field-alignment std) mechanisms contribute.")
    if h1:
        return ("COSET_ENERGY_H1",
                f"Energetic mechanism: energy_delta={e_delta:.4f} < -{ENERGY_EFFECT_THRESHOLD}. "
                f"align_delta={a_delta:.4f} (not significant). "
                "RM(1,16) codewords are NOT attractors under W; lower energy = repellers/saddles.")
    if h2:
        return ("COSET_ENTROPY_H2",
                f"Alignment mechanism: align_delta={a_delta:.4f} < -{ALIGN_EFFECT_THRESHOLD}. "
                f"energy_delta={e_delta:.4f} (not significant). "
                "RM(1,16) codewords have lower W-field alignment variance; dynamics avoid flat regions.")
    return ("COSET_MECHANISM_OPEN",
            f"No significant difference: energy_delta={e_delta:.4f}, align_delta={a_delta:.4f}. "
            f"Neither H1 nor H2 explains the RM(1,16) avoidance. Mechanism remains open.")


def self_test_verdict():
    cases = [
        ({"energy_delta": -0.10, "align_delta": -0.08}, "COSET_BOTH_H1_H2"),
        ({"energy_delta": -0.10, "align_delta": 0.02}, "COSET_ENERGY_H1"),
        ({"energy_delta": 0.01, "align_delta": -0.08}, "COSET_ENTROPY_H2"),
        ({"energy_delta": 0.01, "align_delta": 0.02}, "COSET_MECHANISM_OPEN"),
        ({}, "COSET_MECHANISM_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"Expected {exp}, got {a} for input {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def fwht_batched(X):
    """Fast Walsh-Hadamard transform (in-place over last dim)."""
    N = X.shape[-1]
    h = 1
    while h < N:
        X = X.view(*X.shape[:-1], -1, 2 * h)
        a = X[..., :h].clone()
        b = X[..., h:2 * h].clone()
        X[..., :h] = a + b
        X[..., h:2 * h] = a - b
        X = X.view(*X.shape[:-2], N)
        h *= 2
    return X


def make_bsc_codebook(K, N, gen, device):
    """BSC codebook: K x N tensor of {-1, +1}."""
    return (torch.randint(0, 2, (K, N), generator=gen, device=device).float() * 2 - 1)


def build_W(codebook, K_store):
    """Hebbian W = sum_{k=1}^{K_store} c_k c_k^T / N (outer products)."""
    C = codebook[:K_store]  # (K_store, N)
    return C.T @ C / C.shape[-1]  # (N, N)


def coset_energy(W, endpoint):
    """E = e^T W e / N; high = deep basin."""
    N = endpoint.shape[0]
    return float(endpoint @ W @ endpoint) / N


def mini_entropy(endpoints_coset):
    """Entropy from simple k-means clustering of endpoints_coset rows."""
    if endpoints_coset.shape[0] < N_SUBCLUSTERS:
        return 0.0
    k = min(N_SUBCLUSTERS, endpoints_coset.shape[0])
    # Simple random partition for entropy estimate (no sklearn needed)
    # Use random assignment as proxy (worst-case uniform = log k)
    # Better: use cosine similarity to k random centroids
    torch.manual_seed(42)
    centroids = endpoints_coset[torch.randperm(endpoints_coset.shape[0])[:k]]
    sims = endpoints_coset.float() @ centroids.float().T  # (n, k)
    assignments = sims.argmax(dim=1)
    counts = torch.bincount(assignments, minlength=k).float()
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    entropy = float(-(probs * probs.log()).sum())
    return entropy


def make_rm1m_codewords(n, N, gen, device):
    """Generate n random RM(1,m)-class codewords (linear combinations of Hadamard rows).
    RM(1,m) codewords are {+1,-1} Walsh functions f(x) = (-1)^{a^T x + b}.
    For N=2^m: each codeword is a row of the N x N Hadamard matrix (or negated).
    We pick random Hadamard rows as our RM(1,m) proxies.
    """
    m = N.bit_length() - 1
    # Build random Hadamard rows by generating random {0,1} linear forms
    indices = torch.randint(0, N, (n,), generator=gen, device=device)
    # Row k of Hadamard = (-1)^{popcount(k & j)} for j=0..N-1
    j = torch.arange(N, device=device).unsqueeze(0)  # (1, N)
    k = indices.unsqueeze(1)                           # (n, 1)
    bits = (k & j).to(torch.int32)
    # popcount via counting 1s in binary
    parities = bits.sum(dim=-1) % 2  # not quite right -- need bit-parity not sum
    # Correct popcount mod 2: xor of bits of k&j
    # Alternative: use a lookup or torch.bitwise approach
    # Efficient: convert to float and compute
    rows = torch.zeros(n, N, device=device)
    for bit_pos in range(m):
        mask = (1 << bit_pos)
        bit_j = ((j >> bit_pos) & 1).float()  # (1, N) 0/1
        bit_k = ((k >> bit_pos) & 1).float()  # (n, 1) 0/1
        rows += bit_j * bit_k
    parities = rows.long() % 2
    codewords = 1 - 2 * parities.float()  # {+1, -1}
    # Randomly negate half (b=0 or b=1 codeword)
    flip = (torch.randint(0, 2, (n, 1), generator=gen, device=device).float() * 2 - 1)
    return codewords * flip


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")  # CPU-only experiment
    cfg = {
        "N": 1024 if smoke else 4096,
        "K_store": 15 if smoke else 80,
        "n_endpoints": 200 if smoke else 800,
        "n_rm_synthetic": 50 if smoke else N_RM_SYNTHETIC,
        "n_seeds": 1 if smoke else 3,
    }
    N = cfg["N"]
    assert (N & (N - 1)) == 0, f"N={N} must be power of 2"

    energy_endpoint_all = []
    energy_rm_all = []
    align_endpoint_all = []
    align_rm_all = []

    for seed_i in range(cfg["n_seeds"]):
        seed = 17 + seed_i * 101
        gen = torch.Generator(device=device).manual_seed(seed)
        # BSC codebook for memories
        codebook = make_bsc_codebook(max(cfg["K_store"] + 10, 100), N, gen, device)
        W = build_W(codebook, cfg["K_store"])

        # Collect trajectory endpoints: random starts, converge under sign(W @ x)
        starts = make_bsc_codebook(cfg["n_endpoints"], N, gen, device)
        endpoints = []
        for i in range(starts.shape[0]):
            x = starts[i].clone()
            for _ in range(30):  # fixed-point iteration
                x_new = torch.sign(W @ x)
                x_new[x_new == 0] = 1.0
                if torch.equal(x_new, x):
                    break
                x = x_new
            endpoints.append(x)
        endpoints_t = torch.stack(endpoints, dim=0)  # (n_endpoints, N)

        # Synthetic RM(1,m) codewords
        rm_gen = torch.Generator(device=device).manual_seed(seed + 7777)
        rm_codewords = make_rm1m_codewords(cfg["n_rm_synthetic"], N, rm_gen, device)

        # Energy = x^T W x / N (higher = deeper attractor basin)
        def batch_energy(vecs, Wmat):
            Wv = Wmat @ vecs.T  # (N, n)
            return (vecs * Wv.T).sum(dim=1) / N  # (n,)

        e_ep = batch_energy(endpoints_t, W)
        e_rm = batch_energy(rm_codewords, W)

        # Alignment = std of (W @ x) over components (how "structured" the W-field is)
        # High std = W has strong pull; low std = W is diffuse -> repeller
        def batch_align_std(vecs, Wmat):
            Wv = Wmat @ vecs.T  # (N, n)
            return Wv.std(dim=0)  # per-vector std of field

        a_ep = batch_align_std(endpoints_t, W)
        a_rm = batch_align_std(rm_codewords, W)

        print(f"  seed={seed}: E_endpoint={e_ep.mean():.4f}+/-{e_ep.std():.4f}, "
              f"E_rm={e_rm.mean():.4f}+/-{e_rm.std():.4f}", flush=True)
        print(f"           align_ep={a_ep.mean():.4f}, align_rm={a_rm.mean():.4f}", flush=True)

        energy_endpoint_all.append(float(e_ep.mean()))
        energy_rm_all.append(float(e_rm.mean()))
        align_endpoint_all.append(float(a_ep.mean()))
        align_rm_all.append(float(a_rm.mean()))

    mean_e_ep = sum(energy_endpoint_all) / len(energy_endpoint_all)
    mean_e_rm = sum(energy_rm_all) / len(energy_rm_all)
    mean_a_ep = sum(align_endpoint_all) / len(align_endpoint_all)
    mean_a_rm = sum(align_rm_all) / len(align_rm_all)

    energy_delta = mean_e_rm - mean_e_ep    # negative = RM lower energy = H1
    align_delta = mean_a_rm - mean_a_ep     # negative = RM lower alignment = H2

    print(f"\n  mean_E_rm={mean_e_rm:.4f}, mean_E_endpoint={mean_e_ep:.4f}, delta={energy_delta:.4f}", flush=True)
    print(f"  mean_align_rm={mean_a_rm:.4f}, mean_align_ep={mean_a_ep:.4f}, delta={align_delta:.4f}", flush=True)

    summary = {
        "energy_delta": energy_delta,
        "align_delta": align_delta,
        "mean_E_endpoint": mean_e_ep,
        "mean_E_rm_synthetic": mean_e_rm,
        "mean_align_endpoint": mean_a_ep,
        "mean_align_rm_synthetic": mean_a_rm,
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_coset_energy_entropy_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("e_endpoint", summary["mean_E_endpoint"], 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_coset_energy_entropy_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
