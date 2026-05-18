"""Sparse VSA smoke test: does naive sparse bipolar VSA support bundle+query at all?

Sparse atoms have k_active non-zero +/-1 components out of N. Binding by elementwise
multiplication reduces density (bind density ~ d^2). Bundle uses top-k_active by sum magnitude
to re-sparsify.

Naive sparse VSA is known to have issues; this experiment quantifies them by measuring
recovery vs bundle size k at different sparsity levels.
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from hdlab import experiment, tracing  # noqa: E402
from reference import sparse_vsa  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N = 1024
SPARSITIES = [0.02, 0.05, 0.1, 0.2, 0.5, 1.0]  # fraction of N that's non-zero
K_VALUES = [2, 5, 10, 20, 50, 100]
POOL_SIZE = 200
TRIALS = 20


def workload(ctx: experiment.ExperimentContext) -> dict:
    gen = ctx.generator
    quiet_bus = tracing.TraceBus(enabled=False)

    results: dict[float, dict[int, float]] = {}

    with tracing.using(quiet_bus):
        for sparsity in SPARSITIES:
            k_active = max(1, int(N * sparsity))
            # Build pool of sparse filler atoms
            pool = torch.stack([sparse_vsa.make_atom(N, k_active, gen) for _ in range(POOL_SIZE)])

            recovery_by_k: dict[int, float] = {}
            for k in K_VALUES:
                correct = 0
                denom = 0
                for _ in range(TRIALS):
                    indices = torch.randint(0, POOL_SIZE, (k,), generator=gen)
                    chosen_fillers = pool[indices]
                    # Generate k fresh sparse role atoms
                    roles = torch.stack([sparse_vsa.make_atom(N, k_active, gen) for _ in range(k)])
                    # Bind
                    bindings = torch.stack([sparse_vsa.bind(roles[i], chosen_fillers[i]) for i in range(k)])
                    # Bundle (sum + top-k_active re-sparsify)
                    bundle = sparse_vsa.bundle(bindings, k_active)
                    # Query each role
                    for i in range(k):
                        recovered = sparse_vsa.unbind(bundle, roles[i])
                        # Cleanup: similarity to every pool atom
                        sims = (pool.to(torch.float32) * recovered.to(torch.float32)).sum(dim=-1) / N
                        best = int(sims.argmax().item())
                        if best == int(indices[i].item()):
                            correct += 1
                        denom += 1
                recovery_by_k[k] = correct / max(denom, 1)
            results[sparsity] = recovery_by_k

    def page_curves(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        for sparsity, recovery_by_k in results.items():
            ks = sorted(recovery_by_k.keys())
            rs = [recovery_by_k[k] for k in ks]
            ax.plot(ks, rs, marker="o", linewidth=2, label=f"density={sparsity:.2f} (k_active={int(N*sparsity)})")
        ax.set_xlabel("bundle size k")
        ax.set_ylabel("recovery rate")
        ax.set_title(f"Sparse VSA: recovery vs bundle size at N={N}, pool={POOL_SIZE}")
        ax.set_xscale("log")
        ax.set_ylim(-0.05, 1.05)
        ax.axhline(0.5, color="black", linestyle="--", alpha=0.3)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3, which="both")
        pdf.savefig(fig)
        plt.close(fig)

    headline_lines = []
    for sparsity, recovery_by_k in results.items():
        r_k10 = recovery_by_k.get(10, float("nan"))
        headline_lines.append(f"density={sparsity:.2f}: recovery@k=10 = {r_k10:.2f}")
    headline = " | ".join(headline_lines[:3])

    return {
        "n": N,
        "sparsities": SPARSITIES,
        "k_values": K_VALUES,
        "pool_size": POOL_SIZE,
        "trials_per_cell": TRIALS,
        "recovery_sweep": {str(s): results[s] for s in SPARSITIES},
        "headline": headline,
        "_pdf_extras": [page_curves],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_sparse_smoke", seed=42, n=N)
    result = experiment.run(spec, workload)
    summary = {k: v for k, v in result.metrics.items() if k != "recovery_sweep"}
    print(json.dumps(summary, indent=2, default=str))
    # Also print the full sweep
    print("\nFull sweep:")
    for sparsity, sweep in result.metrics["recovery_sweep"].items():
        print(f"  density={float(sparsity):.2f}: " + ", ".join(f"k={int(k)}={r:.2f}" for k, r in sorted(sweep.items(), key=lambda kv: int(kv[0]))))


if __name__ == "__main__":
    main()
