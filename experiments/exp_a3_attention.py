"""A3: attention modulator sweep yields precision/recall curves.

Mix of true noisy queries (recoverable) and junk queries (random new atoms not in codebook).
Sweep `attention` from 0 to 1 and measure precision/recall at each level.
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, experiment, memory, modulators  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def workload(ctx: experiment.ExperimentContext) -> dict:
    n = ctx.spec.n
    gen = ctx.generator
    k = 30
    n_true = 60   # noisy queries from the codebook
    n_junk = 60   # random atoms NOT in the codebook
    noise_sigma = 0.6  # moderate phase jitter
    attention_values = [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]

    cb = memory.Codebook(n, torch.complex64)
    stored: list[torch.Tensor] = []
    for i in range(k):
        v = atoms.make_atom_fhrr(n, gen)
        cb.add(f"a{i:02d}", v)
        stored.append(v)

    # Generate true (noisy) queries with their ground-truth labels.
    true_queries: list[tuple[torch.Tensor, str]] = []
    for _ in range(n_true):
        idx = int(torch.randint(0, k, (1,), generator=gen).item())
        v = stored[idx]
        jitter = (torch.rand(n, generator=gen) - 0.5) * (2.0 * noise_sigma)
        rot = torch.complex(torch.cos(jitter), torch.sin(jitter)).to(v.dtype)
        true_queries.append((v * rot, f"a{idx:02d}"))

    # Junk queries: fresh atoms not registered in the codebook.
    junk_queries: list[torch.Tensor] = [atoms.make_atom_fhrr(n, gen) for _ in range(n_junk)]

    results: list[dict] = []
    for att in attention_values:
        with modulators.using(attention=att):
            tp = 0  # correct accept
            fp = 0  # wrong accept
            fn = 0  # rejected when should accept
            tn = 0  # rejected junk
            for q, truth in true_queries:
                name, _ = cb.lookup(q)
                if name == truth:
                    tp += 1
                elif name is not None:
                    fp += 1
                else:
                    fn += 1
            for q in junk_queries:
                name, _ = cb.lookup(q)
                if name is None:
                    tn += 1
                else:
                    fp += 1
            returned = tp + fp
            precision = tp / max(returned, 1)
            recall = tp / max(tp + fn, 1)
            results.append(
                {
                    "attention": att,
                    "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                    "precision": precision,
                    "recall": recall,
                    "f1": 2 * precision * recall / max(precision + recall, 1e-9),
                }
            )

    # Best F1
    best = max(results, key=lambda r: r["f1"])

    headline = (
        f"best F1={best['f1']:.3f} at attention={best['attention']:.2f} "
        f"(P={best['precision']:.2f}, R={best['recall']:.2f}); "
        f"precision rises {results[0]['precision']:.2f} -> {results[-1]['precision']:.2f}"
    )

    def page_pr_curve(pdf):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))
        xs = [r["attention"] for r in results]
        ps = [r["precision"] for r in results]
        rs = [r["recall"] for r in results]
        f1s = [r["f1"] for r in results]
        ax1.plot(xs, ps, marker="o", label="precision", color="seagreen", linewidth=2)
        ax1.plot(xs, rs, marker="s", label="recall", color="firebrick", linewidth=2)
        ax1.plot(xs, f1s, marker="^", label="F1", color="steelblue", linewidth=2, alpha=0.7)
        ax1.set_xlabel("attention threshold")
        ax1.set_ylabel("metric")
        ax1.set_title(f"A3: P/R vs attention (k={k}, sigma={noise_sigma}, N={n})")
        ax1.set_ylim(-0.05, 1.05)
        ax1.legend(loc="best")
        ax1.grid(True, alpha=0.3)
        ax1.axvline(best["attention"], color="black", linestyle=":", alpha=0.4)

        ax2.plot(rs, ps, marker="o", color="purple", linewidth=2)
        ax2.set_xlabel("recall")
        ax2.set_ylabel("precision")
        ax2.set_title("A3: PR curve")
        ax2.set_xlim(-0.05, 1.05)
        ax2.set_ylim(-0.05, 1.05)
        ax2.grid(True, alpha=0.3)
        for r in results:
            ax2.annotate(f"{r['attention']:.2f}", (r["recall"], r["precision"]), fontsize=7, alpha=0.6)

        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    monotone_precision = all(
        results[i + 1]["precision"] >= results[i]["precision"] - 0.05
        for i in range(len(results) - 1)
    )

    return {
        "k": k,
        "n_true": n_true,
        "n_junk": n_junk,
        "noise_sigma": noise_sigma,
        "attention_values": attention_values,
        "results": results,
        "best_f1": best,
        "monotone_precision": monotone_precision,
        "headline": headline,
        "review": not monotone_precision,
        "_pdf_extras": [page_pr_curve],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_a3_attention", seed=42, n=1024)
    result = experiment.run(spec, workload)
    print(json.dumps({k: v for k, v in result.metrics.items() if k != "results"}, indent=2, default=str))
    print(f"\nFull P/R curve in: {result.pdf_path}")


if __name__ == "__main__":
    main()
