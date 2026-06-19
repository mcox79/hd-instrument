"""M7: Hebbian density vs crosstalk.

At each step, the signal pair (a0, a1) is reinforced. Additionally, a variable number of
'noise atoms' from {a2..a19} are co-activated in a single update -- which reinforces every
pair among them. Higher co-activation count = denser Hebbian graph per step = more crosstalk
on pairs that shouldn't be associated.

Density per step = co_activation_count * (co_activation_count - 1) / 2 noise pairs reinforced,
divided by the total number of pairs available (K*(K-1)/2).
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from hdlab import experiment, learning, modulators, tracing  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def workload(ctx: experiment.ExperimentContext) -> dict:
    gen = ctx.generator
    K = 20
    T = 1000
    decay = 0.005
    noise_counts = [0, 2, 4, 6, 8, 10, 14, 18]  # atoms per noise group, drawn from {a2..a19}
    # The signal pair gets reinforced once per step at arousal*reward=1, giving
    # steady-state weight W_inf = 1/decay = 200.

    atom_names = [f"a{i:02d}" for i in range(K)]
    signal_pair = ("a00", "a01")
    noise_pool = atom_names[2:]  # 18 atoms

    total_pairs = K * (K - 1) // 2

    rows: list[dict] = []
    # Inner loop generates up to nc*(nc-1)/2 trace events per step; disabling tracing here
    # keeps the workload fast. The dashboard for M7 reads its panels from `rows` directly.
    quiet_bus = tracing.TraceBus(enabled=False)
    for nc in noise_counts:
        h = learning.HebbianAssociations(decay=decay)
        with tracing.using(quiet_bus), modulators.using(reward=1.0, arousal=1.0):
            for _ in range(T):
                h.update(list(signal_pair))
                if nc > 0:
                    perm = torch.randperm(len(noise_pool), generator=gen)[:nc].tolist()
                    group = [noise_pool[i] for i in perm]
                    h.update(group)

        # Measure signal weight
        signal_weight = h.weight(*signal_pair)

        # Measure noise weight: mean over all pairs in the noise pool
        noise_weights = []
        for i in range(len(noise_pool)):
            for j in range(i + 1, len(noise_pool)):
                noise_weights.append(h.weight(noise_pool[i], noise_pool[j]))
        mean_noise_weight = sum(noise_weights) / len(noise_weights) if noise_weights else 0.0
        max_noise_weight = max(noise_weights) if noise_weights else 0.0

        # Density per step (fraction of all pairs that get a reinforcement event)
        pairs_per_step = 1 + (nc * (nc - 1) // 2)  # signal + noise pairs
        density_per_step = pairs_per_step / total_pairs

        snr = signal_weight / max_noise_weight if max_noise_weight > 0 else float("inf")

        rows.append(
            {
                "noise_count": nc,
                "pairs_per_step": pairs_per_step,
                "density_per_step": density_per_step,
                "signal_weight": signal_weight,
                "mean_noise_weight": mean_noise_weight,
                "max_noise_weight": max_noise_weight,
                "snr_signal_to_max_noise": snr if snr != float("inf") else 1e9,
            }
        )

    # Find the density at which signal becomes indistinguishable (signal <= max noise * 2)
    cross_over = next(
        (r for r in rows if r["snr_signal_to_max_noise"] <= 2.0),
        None,
    )
    cross_over_density = cross_over["density_per_step"] if cross_over else None

    headline = (
        f"density 0 -> SNR={rows[0]['snr_signal_to_max_noise']:.1f}; "
        f"density {rows[-1]['density_per_step']:.2f} -> SNR={rows[-1]['snr_signal_to_max_noise']:.2f}"
    )

    def page_density(pdf):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))
        densities = [r["density_per_step"] for r in rows]
        signals = [r["signal_weight"] for r in rows]
        noises_mean = [r["mean_noise_weight"] for r in rows]
        noises_max = [r["max_noise_weight"] for r in rows]
        snrs = [r["snr_signal_to_max_noise"] for r in rows]

        ax1.plot(densities, signals, marker="o", color="seagreen", linewidth=2, label="signal weight (a0, a1)")
        ax1.plot(densities, noises_mean, marker="s", color="steelblue", linewidth=2, label="mean noise pair weight")
        ax1.plot(densities, noises_max, marker="^", color="firebrick", linewidth=2, alpha=0.7, label="max noise pair weight")
        ax1.set_xlabel("fraction of pairs reinforced per step (density)")
        ax1.set_ylabel("Hebbian weight after 1000 steps")
        ax1.set_title(f"M7: signal vs crosstalk noise (K={K} atoms, decay={decay})")
        ax1.set_xscale("log")
        ax1.legend(loc="best")
        ax1.grid(True, alpha=0.3)

        # SNR plot capped at a reasonable value for visibility
        snrs_capped = [min(s, 1000) for s in snrs]
        ax2.plot(densities, snrs_capped, marker="o", color="purple", linewidth=2)
        ax2.set_xlabel("density")
        ax2.set_ylabel("signal-to-(max-noise) ratio")
        ax2.set_title("M7: SNR collapse with density (capped at 1000)")
        ax2.set_xscale("log")
        ax2.set_yscale("log")
        ax2.axhline(2.0, color="firebrick", linestyle=":", alpha=0.4, label="SNR=2 cliff")
        ax2.legend()
        ax2.grid(True, alpha=0.3, which="both")

        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "K": K,
        "T": T,
        "decay": decay,
        "total_pairs": total_pairs,
        "rows": rows,
        "cross_over_density": cross_over_density,
        "headline": headline,
        "_pdf_extras": [page_density],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_m7_hebbian_density", seed=42, n=1024)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
