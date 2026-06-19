"""M2: bundle capacity scaling. Recovery rate of bound (role, filler) pairs as k grows.

For each k, bundle k role-filler bindings (roles fresh, fillers sampled from a codebook).
Query the bundle by each role and check via cleanup whether the right filler is recovered.
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, binding, bundling, experiment, memory  # noqa: E402


def workload(ctx: experiment.ExperimentContext) -> dict:
    n = ctx.spec.n
    gen = ctx.generator
    filler_pool_size = 200
    k_values = [2, 5, 10, 20, 30, 50, 75, 100, 150]
    trials_per_k = 20

    # Filler codebook
    cb = memory.Codebook(n, torch.complex64)
    filler_names: list[str] = []
    filler_vecs: list[torch.Tensor] = []
    for i in range(filler_pool_size):
        v = atoms.make_atom_fhrr(n, gen)
        name = f"f{i:03d}"
        cb.add(name, v)
        filler_names.append(name)
        filler_vecs.append(v)

    recovery_by_k: dict[int, float] = {}
    mean_sim_by_k: dict[int, float] = {}

    for k in k_values:
        correct = 0
        sim_total = 0.0
        sim_count = 0
        for _ in range(trials_per_k):
            # Sample k unique filler indices
            perm = torch.randperm(filler_pool_size, generator=gen)[:k]
            chosen_idx = perm.tolist()
            # Fresh roles per binding
            roles = [atoms.make_atom_fhrr(n, gen) for _ in range(k)]
            # Build bundled structure
            bindings_list = [
                binding.bind(roles[i], filler_vecs[chosen_idx[i]])
                for i in range(k)
            ]
            bundle = bundling.bundle(torch.stack(bindings_list))
            # Query each role and check cleanup
            for i in range(k):
                recovered = binding.unbind(bundle, roles[i])
                name, score = cb.lookup(recovered)
                sim_total += float(score)
                sim_count += 1
                if name == filler_names[chosen_idx[i]]:
                    correct += 1
        recovery_by_k[k] = correct / (trials_per_k * k)
        mean_sim_by_k[k] = sim_total / sim_count

    # Plate-like theoretical reference: signal/noise ratio scales with sqrt(N/k).
    # Empirically expect: high recovery for small k, transition around k~sqrt(N) = 32 at N=1024.
    import math
    theoretical_capacity_knee = int(math.sqrt(n))

    headline = (
        f"recovery@k=10: {recovery_by_k[10] * 100:.0f}%, "
        f"@k=30: {recovery_by_k[30] * 100:.0f}%, "
        f"@k=50: {recovery_by_k[50] * 100:.0f}%, "
        f"@k=100: {recovery_by_k[100] * 100:.0f}%"
    )

    def page_capacity(pdf):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))
        ks = list(recovery_by_k.keys())
        rs = [recovery_by_k[k] for k in ks]
        ms = [mean_sim_by_k[k] for k in ks]

        ax1.plot(ks, rs, marker="o", color="seagreen", linewidth=2)
        ax1.set_xlabel("bundle size k")
        ax1.set_ylabel("filler-recovery rate (via cleanup)")
        ax1.set_title(f"M2: bundle capacity at N={n} (pool of {filler_pool_size} fillers)")
        ax1.set_ylim(-0.05, 1.05)
        ax1.axvline(theoretical_capacity_knee, color="black", linestyle="--", alpha=0.4,
                    label=f"sqrt(N) = {theoretical_capacity_knee}")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        ax2.plot(ks, ms, marker="o", color="steelblue", linewidth=2)
        ax2.set_xlabel("bundle size k")
        ax2.set_ylabel("mean cleanup similarity")
        ax2.set_title("M2: raw recovery similarity vs k (before cleanup decision)")
        # Plate-style theoretical 1/sqrt(k) reference for signal magnitude after normalization
        import math


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        theoretical = [1.0 / math.sqrt(k) for k in ks]
        ax2.plot(ks, theoretical, color="firebrick", linestyle="--", alpha=0.6, label="1/sqrt(k) signal")
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "filler_pool_size": filler_pool_size,
        "k_values": k_values,
        "trials_per_k": trials_per_k,
        "recovery_by_k": recovery_by_k,
        "mean_sim_by_k": mean_sim_by_k,
        "theoretical_capacity_knee_sqrt_N": theoretical_capacity_knee,
        "headline": headline,
        "review": recovery_by_k[2] < 0.95,
        "_pdf_extras": [page_capacity],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_m2_capacity", seed=42, n=1024)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
