"""A1: 50 random atoms, exact-match query. Substrate sanity at population scale."""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, experiment, memory, metrics as metrics_mod  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def workload(ctx: experiment.ExperimentContext) -> dict:
    n = ctx.spec.n
    gen = ctx.generator
    k = 50

    # Build codebook
    cb = memory.Codebook(n, torch.complex64)
    vectors: list[torch.Tensor] = []
    for i in range(k):
        v = atoms.make_atom_fhrr(n, gen)
        cb.add(f"a{i:02d}", v)
        vectors.append(v)

    # Pairwise similarity stats
    stacked = torch.stack(vectors)
    sim_stats = metrics_mod.pairwise_similarity_stats(stacked)

    # Exact-match queries
    correct = 0
    similarity_scores: list[float] = []
    for i, v in enumerate(vectors):
        name, score = cb.lookup(v)
        similarity_scores.append(float(score))
        if name == f"a{i:02d}":
            correct += 1
    recovery_rate = correct / k

    headline = (
        f"k={k} recovery={recovery_rate * 100:.1f}%; "
        f"off-diag sim std={sim_stats['std']:.4f} (theory={1.0 / (n ** 0.5):.4f})"
    )

    def page_pairwise_hist(pdf):
        sims = (stacked @ stacked.conj().T).real / n
        mask = ~torch.eye(k, dtype=torch.bool)
        off = sims[mask].cpu().numpy()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))
        ax1.hist(off, bins=40, color="steelblue", edgecolor="white")
        theoretical_std = 1.0 / (n ** 0.5)
        ax1.axvline(0.0, color="black", linestyle="--", alpha=0.4, label="mean (theory: 0)")
        ax1.axvline(theoretical_std, color="firebrick", linestyle=":", alpha=0.6, label=f"std (theory: {theoretical_std:.3f})")
        ax1.axvline(-theoretical_std, color="firebrick", linestyle=":", alpha=0.6)
        ax1.set_xlabel("off-diagonal similarity")
        ax1.set_ylabel("count")
        ax1.set_title(f"A1: pairwise similarities of {k} random atoms at N={n}")
        ax1.legend()

        ax2.bar(range(k), similarity_scores, color="seagreen")
        ax2.set_xlabel("atom index")
        ax2.set_ylabel("retrieval similarity")
        ax2.set_title("A1: exact-match lookup score per atom")
        ax2.axhline(1.0, color="black", linestyle="--", alpha=0.4)
        ax2.set_ylim(0.95, 1.01)

        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "k": k,
        "recovery_rate": recovery_rate,
        "similarity_stats": sim_stats,
        "theoretical_std": 1.0 / (n ** 0.5),
        "min_retrieval_sim": min(similarity_scores),
        "headline": headline,
        "review": recovery_rate < 1.0,
        "_pdf_extras": [page_pairwise_hist],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_a1_recovery", seed=42, n=1024)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
