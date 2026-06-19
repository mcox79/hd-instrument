"""A2: cleanup robustness vs phase-jitter noise. Recovery curve over sigma in {0.1..2.0}."""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, experiment, memory  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def workload(ctx: experiment.ExperimentContext) -> dict:
    n = ctx.spec.n
    gen = ctx.generator
    k = 50
    sigmas = [0.0, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0, 3.0]
    trials_per_sigma = 50

    cb = memory.Codebook(n, torch.complex64)
    vectors: list[torch.Tensor] = []
    for i in range(k):
        v = atoms.make_atom_fhrr(n, gen)
        cb.add(f"a{i:02d}", v)
        vectors.append(v)

    rows: list[dict] = []
    recovery_by_sigma: dict[float, float] = {}
    mean_sim_by_sigma: dict[float, float] = {}
    for sigma in sigmas:
        correct = 0
        scores: list[float] = []
        for _ in range(trials_per_sigma):
            idx = int(torch.randint(0, k, (1,), generator=gen).item())
            v = vectors[idx]
            jitter = (torch.rand(n, generator=gen) - 0.5) * (2.0 * sigma)
            rot = torch.complex(torch.cos(jitter), torch.sin(jitter)).to(v.dtype)
            noisy = v * rot
            name, score = cb.lookup(noisy)
            scores.append(float(score))
            if name == f"a{idx:02d}":
                correct += 1
        rate = correct / trials_per_sigma
        recovery_by_sigma[sigma] = rate
        mean_sim_by_sigma[sigma] = float(sum(scores) / len(scores))
        rows.append({"sigma": sigma, "recovery": rate, "mean_sim": mean_sim_by_sigma[sigma]})

    headline = (
        f"recovery@sigma=0.5 = {recovery_by_sigma[0.5] * 100:.0f}%, "
        f"@sigma=1.0 = {recovery_by_sigma[1.0] * 100:.0f}%, "
        f"@sigma=2.0 = {recovery_by_sigma[2.0] * 100:.0f}%"
    )

    def page_recovery(pdf):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))
        xs = [r["sigma"] for r in rows]
        ys = [r["recovery"] for r in rows]
        ax1.plot(xs, ys, marker="o", color="seagreen", linewidth=2)
        ax1.set_xlabel("phase jitter sigma (radians half-width)")
        ax1.set_ylabel("exact-match recovery rate")
        ax1.set_title(f"A2: cleanup robustness, k={k} atoms at N={n}")
        ax1.set_ylim(-0.05, 1.05)
        ax1.grid(True, alpha=0.3)

        sims = [r["mean_sim"] for r in rows]
        ax2.plot(xs, sims, marker="o", color="steelblue", linewidth=2)
        ax2.set_xlabel("phase jitter sigma")
        ax2.set_ylabel("mean cleanup similarity")
        ax2.set_title("A2: similarity score vs noise")
        ax2.axhline(0.0, color="black", linestyle="--", alpha=0.3, label="random baseline")
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "k": k,
        "trials_per_sigma": trials_per_sigma,
        "sigmas": sigmas,
        "recovery_by_sigma": recovery_by_sigma,
        "mean_sim_by_sigma": mean_sim_by_sigma,
        "headline": headline,
        "review": recovery_by_sigma[0.1] < 0.9,
        "_pdf_extras": [page_recovery],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_a2_noisy", seed=42, n=1024)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
