"""M1: single (role, filler) binding fidelity. unbind(bind(r, f), r) recovers f."""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, binding, experiment  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def workload(ctx: experiment.ExperimentContext) -> dict:
    n = ctx.spec.n
    gen = ctx.generator
    trials = 100

    similarities: list[float] = []
    for _ in range(trials):
        r = atoms.make_atom_fhrr(n, gen)
        f = atoms.make_atom_fhrr(n, gen)
        c = binding.bind(r, f)
        f_rec = binding.unbind(c, r)
        sim = float(atoms.similarity(f, f_rec))
        similarities.append(sim)

    min_sim = min(similarities)
    mean_sim = sum(similarities) / len(similarities)
    perfect = sum(1 for s in similarities if s > 0.999)

    headline = f"{perfect}/{trials} at sim > 0.999; min sim = {min_sim:.6f}"

    def page_hist(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.hist(similarities, bins=30, color="seagreen", edgecolor="white")
        ax.set_xlabel("recovery similarity")
        ax.set_ylabel("count")
        ax.set_title(f"M1: single (role, filler) recovery, {trials} trials at N={n}")
        ax.axvline(1.0, color="black", linestyle="--", alpha=0.4, label="theoretical (1.0)")
        ax.axvline(min_sim, color="firebrick", linestyle=":", alpha=0.6, label=f"min observed ({min_sim:.5f})")
        ax.legend()
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "trials": trials,
        "min_sim": min_sim,
        "mean_sim": mean_sim,
        "perfect_recoveries": perfect,
        "headline": headline,
        "review": perfect < trials,
        "_pdf_extras": [page_hist],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_m1_single_binding", seed=42, n=1024)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
