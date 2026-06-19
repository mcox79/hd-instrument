"""A4: skewed-frequency Hebbian. Frequent atoms accumulate stronger association weights.

Each query co-activates the recognized atom with a 'RECOGNIZED' tag in the Hebbian graph
(reward=+1 on correct retrievals). Frequent atoms should end the run with markedly higher
RECOGNIZED-association weight than rare ones.
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, experiment, learning, memory, modulators  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def workload(ctx: experiment.ExperimentContext) -> dict:
    n = ctx.spec.n
    gen = ctx.generator
    k = 30
    n_frequent = 5  # first 5 atoms get queried 5x more often
    n_queries = 1000
    noise_sigma = 0.4
    decay = 0.01

    cb = memory.Codebook(n, torch.complex64)
    stored: list[torch.Tensor] = []
    for i in range(k):
        v = atoms.make_atom_fhrr(n, gen)
        cb.add(f"a{i:02d}", v)
        stored.append(v)

    h = learning.HebbianAssociations(decay=decay)
    frequent = list(range(n_frequent))
    rare = list(range(n_frequent, k))

    # Build a skewed sampling distribution: each frequent index has weight 5, each rare has weight 1.
    weights = torch.tensor(
        [5.0 if i in frequent else 1.0 for i in range(k)],
        dtype=torch.float32,
    )
    probs = weights / weights.sum()

    counts = [0] * k
    correct_counts = [0] * k

    with modulators.using(reward=1.0, arousal=1.0):
        for _ in range(n_queries):
            idx = int(torch.multinomial(probs, 1, generator=gen).item())
            v = stored[idx]
            jitter = (torch.rand(n, generator=gen) - 0.5) * (2.0 * noise_sigma)
            rot = torch.complex(torch.cos(jitter), torch.sin(jitter)).to(v.dtype)
            noisy = v * rot
            name, _ = cb.lookup(noisy)
            counts[idx] += 1
            if name == f"a{idx:02d}":
                correct_counts[idx] += 1
                # Reinforce the (atom, RECOGNIZED) association.
                h.update([f"a{idx:02d}", "RECOGNIZED"])

    recognized_weights = [h.weight(f"a{i:02d}", "RECOGNIZED") for i in range(k)]
    freq_mean = sum(recognized_weights[i] for i in frequent) / len(frequent)
    rare_mean = sum(recognized_weights[i] for i in rare) / len(rare)
    ratio = freq_mean / rare_mean if rare_mean > 0 else float("inf")

    headline = (
        f"freq-RECOGNIZED mean={freq_mean:.2f} vs rare={rare_mean:.2f} "
        f"(ratio={ratio:.2f}); {sum(correct_counts)}/{n_queries} correct retrievals"
    )

    def page_hebbian_bars(pdf):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))
        labels = [f"a{i:02d}" for i in range(k)]
        colors = ["seagreen" if i in frequent else "steelblue" for i in range(k)]
        ax1.bar(labels, recognized_weights, color=colors)
        ax1.set_xlabel("atom (green = frequent, blue = rare)")
        ax1.set_ylabel("weight(atom, RECOGNIZED)")
        ax1.set_title("A4: Hebbian association after skewed exposure")
        ax1.tick_params(axis="x", rotation=90, labelsize=6)

        ax2.scatter(counts, recognized_weights, c=colors, s=40)
        ax2.set_xlabel("query count")
        ax2.set_ylabel("Hebbian weight to RECOGNIZED")
        ax2.set_title("A4: exposure vs association strength")
        ax2.grid(True, alpha=0.3)
        for i in frequent:
            ax2.annotate(f"a{i:02d}", (counts[i], recognized_weights[i]), fontsize=8)

        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "k": k,
        "n_frequent": n_frequent,
        "n_queries": n_queries,
        "noise_sigma": noise_sigma,
        "decay": decay,
        "frequent_mean_weight": freq_mean,
        "rare_mean_weight": rare_mean,
        "ratio_freq_to_rare": ratio,
        "total_correct": sum(correct_counts),
        "headline": headline,
        "review": ratio < 2.0,
        "_pdf_extras": [page_hebbian_bars],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_a4_hebbian", seed=42, n=1024)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
