"""A5: substrate operating envelope.

Two heat maps, each cell = recovery rate at given parameters under phase-jitter noise:
1. Fixed N=1024, varying codebook size k and noise sigma.
2. Fixed k=50, varying substrate dimension N and noise sigma.

A2 showed the substrate at N=1024 with k=50 is robust well past sigma=2.0 with the dominant
junk-similarity floor at ~0.08. Predictions for A5 are derived analytically and pre-registered.
"""

from __future__ import annotations

import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, experiment, memory  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def _measure_recovery(
    n: int,
    k: int,
    sigma: float,
    trials: int,
    gen: torch.Generator,
) -> float:
    cb = memory.Codebook(n, torch.complex64)
    stored: list[torch.Tensor] = []
    for i in range(k):
        v = atoms.make_atom_fhrr(n, gen)
        cb.add(f"a{i:04d}", v)
        stored.append(v)

    correct = 0
    for _ in range(trials):
        idx = int(torch.randint(0, k, (1,), generator=gen).item())
        v = stored[idx]
        jitter = (torch.rand(n, generator=gen) - 0.5) * (2.0 * sigma)
        rot = torch.complex(torch.cos(jitter), torch.sin(jitter)).to(v.dtype)
        noisy = v * rot
        name, _ = cb.lookup(noisy)
        if name == f"a{idx:04d}":
            correct += 1
    return correct / trials


def workload(ctx: experiment.ExperimentContext) -> dict:
    gen = ctx.generator
    trials = 30
    k_values = [10, 50, 200, 500, 1000, 2000]
    n_values = [128, 256, 512, 1024, 2048, 4096]
    sigma_values = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5]

    # Sweep 1: fixed N=1024, vary k and sigma
    sweep_k = np.zeros((len(k_values), len(sigma_values)))
    for i, k in enumerate(k_values):
        for j, sigma in enumerate(sigma_values):
            sweep_k[i, j] = _measure_recovery(n=1024, k=k, sigma=sigma, trials=trials, gen=gen)

    # Sweep 2: fixed k=50, vary N and sigma
    sweep_n = np.zeros((len(n_values), len(sigma_values)))
    for i, n in enumerate(n_values):
        for j, sigma in enumerate(sigma_values):
            sweep_n[i, j] = _measure_recovery(n=n, k=50, sigma=sigma, trials=trials, gen=gen)

    # Predicted boundaries (analytic):
    # max-of-k similarity floor ~ 1/sqrt(2N) * sqrt(2 ln k); true-sim at sigma is empirically
    # well-fit by cos-like decay. Failure region: where max-junk >= true-sim.
    def predicted_max_junk(n: int, k: int) -> float:
        return (1.0 / math.sqrt(2 * n)) * math.sqrt(2 * math.log(max(k, 2)))

    junk_floor_at_n1024 = [predicted_max_junk(1024, k) for k in k_values]
    junk_floor_at_k50 = [predicted_max_junk(n, 50) for n in n_values]

    def page_envelope_k(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        im = ax.imshow(sweep_k, aspect="auto", cmap="viridis", vmin=0, vmax=1, origin="lower")
        ax.set_xticks(range(len(sigma_values)))
        ax.set_xticklabels([f"{s:.1f}" for s in sigma_values])
        ax.set_yticks(range(len(k_values)))
        ax.set_yticklabels([str(k) for k in k_values])
        ax.set_xlabel("phase jitter sigma")
        ax.set_ylabel("codebook size k")
        ax.set_title("A5 sweep 1: recovery rate at N=1024 (color = fraction correct)")
        for i in range(len(k_values)):
            for j in range(len(sigma_values)):
                v = sweep_k[i, j]
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", color="white" if v < 0.5 else "black", fontsize=8)
        fig.colorbar(im, ax=ax, label="recovery rate")
        pdf.savefig(fig)
        plt.close(fig)

    def page_envelope_n(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        im = ax.imshow(sweep_n, aspect="auto", cmap="viridis", vmin=0, vmax=1, origin="lower")
        ax.set_xticks(range(len(sigma_values)))
        ax.set_xticklabels([f"{s:.1f}" for s in sigma_values])
        ax.set_yticks(range(len(n_values)))
        ax.set_yticklabels([str(n) for n in n_values])
        ax.set_xlabel("phase jitter sigma")
        ax.set_ylabel("substrate dimension N")
        ax.set_title("A5 sweep 2: recovery rate at k=50 (color = fraction correct)")
        for i in range(len(n_values)):
            for j in range(len(sigma_values)):
                v = sweep_n[i, j]
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", color="white" if v < 0.5 else "black", fontsize=8)
        fig.colorbar(im, ax=ax, label="recovery rate")
        pdf.savefig(fig)
        plt.close(fig)

    def page_floor_analysis(pdf):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))
        # Junk floor vs k at N=1024
        ax1.plot(k_values, junk_floor_at_n1024, marker="o", color="firebrick", linewidth=2)
        ax1.set_xscale("log")
        ax1.set_xlabel("codebook size k")
        ax1.set_ylabel("predicted max-junk similarity floor")
        ax1.set_title("A5: junk floor vs k at N=1024  (1/sqrt(2N) * sqrt(2 ln k))")
        ax1.grid(True, alpha=0.3)
        # Junk floor vs N at k=50
        ax2.plot(n_values, junk_floor_at_k50, marker="o", color="steelblue", linewidth=2)
        ax2.set_xscale("log")
        ax2.set_xlabel("substrate dimension N")
        ax2.set_ylabel("predicted max-junk similarity floor")
        ax2.set_title("A5: junk floor vs N at k=50  (1/sqrt(2N) * sqrt(2 ln k))")
        ax2.grid(True, alpha=0.3)
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    # Headline summary: where does recovery first drop below 95%?
    def first_boundary(matrix, axis_values, sigmas):
        out = []
        for i, ax in enumerate(axis_values):
            row = matrix[i]
            boundary_sigma = None
            for j, sigma in enumerate(sigmas):
                if row[j] < 0.95:
                    boundary_sigma = sigma
                    break
            out.append({"axis": ax, "boundary_sigma": boundary_sigma})
        return out

    boundary_k = first_boundary(sweep_k, k_values, sigma_values)
    boundary_n = first_boundary(sweep_n, n_values, sigma_values)

    headline = (
        f"k=10 breaks at sigma={boundary_k[0]['boundary_sigma']}, "
        f"k=2000 breaks at sigma={boundary_k[-1]['boundary_sigma']}; "
        f"N=128 breaks at sigma={boundary_n[0]['boundary_sigma']}, "
        f"N=4096 breaks at sigma={boundary_n[-1]['boundary_sigma']}"
    )

    return {
        "trials_per_cell": trials,
        "k_values": k_values,
        "n_values": n_values,
        "sigma_values": sigma_values,
        "sweep_k_n1024": sweep_k.tolist(),
        "sweep_n_k50": sweep_n.tolist(),
        "boundary_k": boundary_k,
        "boundary_n": boundary_n,
        "predicted_junk_floor_n1024": junk_floor_at_n1024,
        "predicted_junk_floor_k50": junk_floor_at_k50,
        "headline": headline,
        "_pdf_extras": [page_envelope_k, page_envelope_n, page_floor_analysis],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_a5_envelope", seed=42, n=1024)
    result = experiment.run(spec, workload)
    print(json.dumps({k: v for k, v in result.metrics.items()
                       if k not in ("sweep_k_n1024", "sweep_n_k50")}, indent=2, default=str))


if __name__ == "__main__":
    main()
