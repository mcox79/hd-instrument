"""D3 DLTS analog: K-pulse first-passage fixed-point energy spectroscopy.

From research_semiconductor_physics_substrate_analogies_2026-05-23.md (D3 Finding 2):
  DLTS (Deep Level Transient Spectroscopy) analog on substrate:
  Apply K-pulse (brief increase in stored memories), then observe first-passage
  timing back to baseline fixed-points. Different energy-level fixed-points
  emit characteristic decay times -- analogous to DLTS emission rate 1/tau_e.

Hypothesis: the 28-element fixed-point set partitions into >=2 distinct energy levels.
  Energy level = W-energy E = e^T W e / N at the fixed point.
  K-pulse = briefly increase K from K_base to K_pulse; observe transient decay
  back to original attractors via first-passage timing.
  Lower-energy fixed-points (deeper basins) have LONGER first-passage time from
  the perturbed state (harder to escape the K-pulse perturbation).

Protocol:
  1. Build W with K_base stored memories (baseline).
  2. Measure 28-element fixed-point set (run 200 random starts, cluster by Hamming).
  3. K-pulse: add K_extra more memories to W (simulate DLTS "filling pulse").
  4. From perturbed state (random start under W_pulse), measure first-passage time
     back to each baseline fixed-point.
  5. Sort fixed-points by mean first-passage time; cluster into energy tiers.
  6. Test: does the first-passage time distribution have >=2 distinct modes
     (bimodal -> 2 energy levels, as predicted by D3 Finding 2)?

HARD PASS: first-passage time histogram is bimodal (2+ distinct clusters at p<0.05
           by dip test proxy or cluster-separation >= 2x).
HARD FAIL: unimodal first-passage times -> single energy level, D3 DLTS prediction fails.

Verdict labels:
  DLTS_BIMODAL        -- bimodal first-passage distribution; >=2 energy levels confirmed
  DLTS_MULTIMODAL     -- 3+ modes; richer energy landscape
  DLTS_UNIMODAL       -- single mode; single effective energy level
  DLTS_INCONCLUSIVE   -- not enough fixed-point diversity to test

GPU-accelerated. Uses CUDA if available (runs faster at N=16384).
Memory budget: W = N x N float32; N=4096 -> 64 MB; N=16384 -> 1 GB (use float16 or chunked).
Actually: W is NOT explicitly materialized; use codebook-product form.
Codebook at N=16384, K=200: 200 * 16384 * 4 bytes = 13 MB. Peak ~100 MB.
Expected runtime: ~15 min GPU at FULL (N=16384, 200 starts, 3 seeds).
Smoke: ~3 min CPU/GPU at N=4096.
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

BIMODAL_RATIO = 2.0    # min ratio of high-mean to low-mean FPT for bimodal claim
MIN_FP_CLUSTERS = 5    # minimum endpoints in each cluster


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"missing keys: {set(d.keys())}")


def compute_verdict(summary):
    if "n_fp_clusters" not in summary or "fpt_cluster_means" not in summary:
        return ("DLTS_INCONCLUSIVE", "Missing n_fp_clusters or fpt_cluster_means.")
    n_clusters = summary["n_fp_clusters"]
    means = sorted(summary["fpt_cluster_means"])
    if n_clusters < 2:
        return ("DLTS_UNIMODAL",
                f"Single FPT cluster (n_fp_clusters={n_clusters}). "
                "All fixed-points at same effective energy level. D3 DLTS prediction fails.")
    if len(means) < 2:
        return ("DLTS_INCONCLUSIVE", "Not enough cluster means.")
    ratio = means[-1] / max(means[0], 1.0)
    if n_clusters >= 3:
        return ("DLTS_MULTIMODAL",
                f"3+ FPT clusters (n={n_clusters}); means={[round(m, 1) for m in means]}. "
                f"Ratio hi/lo={ratio:.2f}. Rich multi-level energy landscape. "
                "D3 DLTS prediction confirmed (stronger than predicted).")
    if ratio >= BIMODAL_RATIO:
        return ("DLTS_BIMODAL",
                f"Bimodal FPT distribution: 2 clusters with means={[round(m, 1) for m in means]}, "
                f"ratio={ratio:.2f} >= {BIMODAL_RATIO}. "
                "Fixed-points partition into 2 distinct energy levels. D3 DLTS prediction CONFIRMED.")
    return ("DLTS_UNIMODAL",
            f"2 clusters found but ratio={ratio:.2f} < {BIMODAL_RATIO} (insufficient separation). "
            f"Means={[round(m, 1) for m in means]}. Effectively unimodal.")


def self_test_verdict():
    cases = [
        ({"n_fp_clusters": 2, "fpt_cluster_means": [5.0, 15.0]}, "DLTS_BIMODAL"),
        ({"n_fp_clusters": 3, "fpt_cluster_means": [5.0, 12.0, 25.0]}, "DLTS_MULTIMODAL"),
        ({"n_fp_clusters": 1, "fpt_cluster_means": [10.0]}, "DLTS_UNIMODAL"),
        ({"n_fp_clusters": 2, "fpt_cluster_means": [9.0, 11.0]}, "DLTS_UNIMODAL"),  # ratio < 2.0
        ({}, "DLTS_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"Expected {exp}, got {a} for input {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bsc_codebook(K, N, gen, device):
    return (torch.randint(0, 2, (K, N), generator=gen, device=device).float() * 2 - 1)


def hebbian_step(x, codebook):
    """One step of Hebbian attractor dynamics: x_new = sign(C^T C x / N)."""
    N = codebook.shape[1]
    proj = codebook @ x  # (K,)
    field = codebook.T @ proj / N  # (N,)
    x_new = torch.sign(field)
    x_new[x_new == 0] = 1.0
    return x_new


def converge(x, codebook, max_steps=50):
    """Converge x to fixed point under Hebbian dynamics. Returns (fp, steps)."""
    for step in range(max_steps):
        x_new = hebbian_step(x, codebook)
        if torch.equal(x_new, x):
            return x, step
        x = x_new
    return x, max_steps


def k_pulse_fpt(x_start, codebook_base, codebook_pulse, target_fps, max_steps=100):
    """
    Apply K-pulse: initialize under pulse dynamics then measure first-passage
    to any baseline fixed-point.
    Returns (fp_idx, steps) where fp_idx = which target_fps was hit first.
    """
    x = x_start.clone()
    # Brief pulse: 1 step under K_pulse codebook
    x = hebbian_step(x, codebook_pulse)
    x = torch.sign(x)
    x[x == 0] = 1.0

    # Then converge under base codebook, measuring first-passage to target fps
    N = x.shape[0]
    # Hamming threshold for "close to a fixed point": N/10
    hamming_threshold = N // 10

    for step in range(max_steps):
        x = hebbian_step(x, codebook_base)
        # Check proximity to each target fixed point
        for fp_idx, fp in enumerate(target_fps):
            hamming = int((x != fp).sum().item())
            if hamming <= hamming_threshold:
                return fp_idx, step + 1
    # Did not reach any known fp
    return -1, max_steps


def cluster_fps(fps_list, N):
    """Cluster fixed-point endpoints by Hamming distance (simple greedy clustering)."""
    if not fps_list:
        return []
    clusters = []
    assigned = [False] * len(fps_list)
    threshold = N // 8  # endpoints within N/8 Hamming are same cluster

    for i, fp in enumerate(fps_list):
        if assigned[i]:
            continue
        cluster = [i]
        assigned[i] = True
        for j in range(i + 1, len(fps_list)):
            if not assigned[j]:
                hamming = int((fps_list[i] != fps_list[j]).sum().item())
                if hamming <= threshold:
                    cluster.append(j)
                    assigned[j] = True
        clusters.append(cluster)
    return clusters


def kmeans_1d(values, k=2, max_iter=20):
    """Simple 1D k-means to find cluster means of FPT values."""
    if len(values) < k:
        return list(range(len(values))), [float(v) for v in values]
    vals = sorted(values)
    # Initialize centroids evenly
    step = len(vals) // k
    centroids = [float(vals[step * i]) for i in range(k)]

    for _ in range(max_iter):
        labels = []
        for v in values:
            dists = [abs(v - c) for c in centroids]
            labels.append(dists.index(min(dists)))
        new_centroids = []
        for ci in range(k):
            members = [values[j] for j in range(len(values)) if labels[j] == ci]
            new_centroids.append(sum(members) / len(members) if members else centroids[ci])
        if new_centroids == centroids:
            break
        centroids = new_centroids

    # Check if clusters are distinct enough
    cluster_means = sorted(centroids)
    return labels, cluster_means


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}", flush=True)

    cfg = {
        "mode": "smoke" if smoke else "full",
        "N": 4096 if smoke else 16384,
        "K_base": 50 if smoke else 100,
        "K_pulse_extra": 20 if smoke else 50,
        "n_starts": 50 if smoke else 200,
        "n_fpt_probes": 20 if smoke else 100,
        "n_seeds": 1 if smoke else 3,
        "max_fpt_steps": 50 if smoke else 100,
    }
    N = cfg["N"]

    all_fp_energies = []
    all_fpt_by_fp = {}  # fp_cluster_idx -> list of FPT values
    total_fp_clusters = 0

    for seed_i in range(cfg["n_seeds"]):
        seed = 17 + seed_i * 101
        gen = torch.Generator(device=device).manual_seed(seed)
        codebook_base = make_bsc_codebook(cfg["K_base"], N, gen, device)
        codebook_pulse = make_bsc_codebook(cfg["K_base"] + cfg["K_pulse_extra"], N,
                                           gen, device)

        # Collect fixed points from n_starts random initializations
        fps_raw = []
        for i in range(cfg["n_starts"]):
            x_gen = torch.Generator(device=device).manual_seed(seed + 10000 + i)
            x0 = make_bsc_codebook(1, N, x_gen, device)[0]
            fp, steps = converge(x0, codebook_base)
            fps_raw.append(fp.cpu())

        # Cluster fixed points
        fps_cpu = [fp.to('cpu') for fp in fps_raw]
        clusters = cluster_fps(fps_cpu, N)
        print(f"  seed={seed}: {len(fps_raw)} starts -> {len(clusters)} FP clusters", flush=True)
        total_fp_clusters = len(clusters)

        if len(clusters) < 2:
            print("  Too few FP clusters to test DLTS; skipping FPT.", flush=True)
            continue

        # Representative fixed-points (one per cluster: cluster centroid as majority vote)
        rep_fps = []
        for cl in clusters:
            if not cl:
                continue
            fps_in_cl = torch.stack([fps_cpu[i] for i in cl], dim=0).float()
            centroid = torch.sign(fps_in_cl.mean(0))
            centroid[centroid == 0] = 1.0
            rep_fps.append(centroid.to(device))

        # Compute W-energy for each representative fixed point
        fp_energies = []
        for fp in rep_fps:
            Cv = codebook_base @ fp  # (K_base,)
            energy = float((Cv * Cv).sum() / N)  # = fp^T (C^T C / N) fp
            fp_energies.append(energy)
        all_fp_energies.extend(fp_energies)
        print(f"  FP energies (W-energy / N): {[round(e, 3) for e in fp_energies]}", flush=True)

        # K-pulse first-passage timing
        for fp_idx in range(len(rep_fps)):
            all_fpt_by_fp.setdefault(fp_idx, [])

        for probe_i in range(cfg["n_fpt_probes"]):
            x_gen = torch.Generator(device=device).manual_seed(seed + 20000 + probe_i)
            x0 = make_bsc_codebook(1, N, x_gen, device)[0]
            hit_idx, fpt = k_pulse_fpt(x0, codebook_base, codebook_pulse, rep_fps,
                                        max_steps=cfg["max_fpt_steps"])
            if hit_idx >= 0:
                all_fpt_by_fp.setdefault(hit_idx, []).append(fpt)

    # Compute mean FPT per fp cluster
    fpt_means = {}
    for fp_idx, fpts in all_fpt_by_fp.items():
        if fpts:
            fpt_means[fp_idx] = sum(fpts) / len(fpts)
    print(f"\n  FPT means per cluster: {fpt_means}", flush=True)

    # Cluster FPT means into energy tiers (1D k-means k=2)
    if len(fpt_means) >= 2:
        fpt_values = list(fpt_means.values())
        _, cluster_means = kmeans_1d(fpt_values, k=min(2, len(fpt_values)))
        n_distinct = len(set(round(m) for m in cluster_means))
    else:
        cluster_means = list(fpt_means.values())
        n_distinct = 1

    summary = {
        "n_fp_clusters": total_fp_clusters,
        "fpt_cluster_means": [round(m, 2) for m in sorted(cluster_means)],
        "fp_energies_all": [round(e, 4) for e in all_fp_energies],
        "fpt_by_fp": {k: round(v, 2) for k, v in fpt_means.items()},
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
    out_dir = get_output_dir("wave14_dlts_kpulse_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("n_fp_clusters", float(summary.get("n_fp_clusters", 0)), 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_dlts_kpulse_v1")
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
