"""Bundle-capacity scaling exponent vs N. Fits k_50%(N) ~ N^alpha.

For each (N, k) cell: sample k filler indices, generate k fresh roles, bundle bindings,
unbind in batch, compute similarities in one matmul, take argmax. Fast at any N.
"""

from __future__ import annotations

import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, binding, bundling, experiment, tracing  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def _measure_recovery_batch(
    n: int,
    k: int,
    pool: torch.Tensor,
    trials: int,
    gen: torch.Generator,
) -> float:
    """Recovery rate across `trials` random bundles of size k against a fixed filler pool."""
    pool_size = pool.shape[0]
    correct = 0
    denom = 0
    for _ in range(trials):
        # Sample k filler indices with replacement (k may exceed pool_size at large N).
        indices = torch.randint(0, pool_size, (k,), generator=gen)
        chosen_fillers = pool[indices]  # (k, n)
        # Fresh role atoms
        phases = torch.rand((k, n), generator=gen) * (2.0 * math.pi)
        roles = torch.complex(torch.cos(phases), torch.sin(phases)).to(torch.complex64)
        # Bind elementwise
        bindings_tensor = roles * chosen_fillers  # (k, n)
        # Bundle: sum + per-component magnitude normalize
        s = bindings_tensor.sum(dim=0)
        mag = s.abs()
        mag = torch.where(mag > 0, mag, torch.ones_like(mag))
        bundle = s / mag.to(s.dtype)  # (n,)
        # Batch unbind: bundle * conj(roles) elementwise
        unbound = bundle.unsqueeze(0) * roles.conj()  # (k, n)
        # Batch cleanup: similarity of each unbound query vs all pool atoms
        sims = (unbound @ pool.conj().T).real / n  # (k, pool_size)
        best = sims.argmax(dim=1)  # (k,)
        correct += (best == indices).sum().item()
        denom += k
    return correct / denom


def _find_k_50(recovery_by_k: dict[int, float]) -> float | None:
    """Linear-interpolate in log(k) for where recovery crosses 0.5."""
    ks_sorted = sorted(recovery_by_k.keys())
    for i in range(len(ks_sorted) - 1):
        k_lo, k_hi = ks_sorted[i], ks_sorted[i + 1]
        r_lo, r_hi = recovery_by_k[k_lo], recovery_by_k[k_hi]
        if r_lo >= 0.5 and r_hi < 0.5:
            # interpolate in log space
            t = (0.5 - r_lo) / (r_hi - r_lo)
            log_k = math.log(k_lo) + t * (math.log(k_hi) - math.log(k_lo))
            return math.exp(log_k)
    return None


def workload(ctx: experiment.ExperimentContext) -> dict:
    gen = ctx.generator
    n_values = [1024, 4096, 8192, 16384]
    k_values = [10, 25, 50, 100, 200, 400, 800, 1600, 3200, 6400]
    pool_size = 200
    trials = 10

    # Tracing every torch op here would generate millions of events; we record the harness
    # entry/exit only.
    quiet_bus = tracing.TraceBus(enabled=False)

    sweep: dict[int, dict[int, float]] = {}
    k_50_by_n: dict[int, float | None] = {}

    with tracing.using(quiet_bus):
        for n in n_values:
            # Build the filler pool at this N (fixed for all k sweeps at this N)
            phases = torch.rand((pool_size, n), generator=gen) * (2.0 * math.pi)
            pool = torch.complex(torch.cos(phases), torch.sin(phases)).to(torch.complex64)

            recovery_by_k: dict[int, float] = {}
            for k in k_values:
                rate = _measure_recovery_batch(n=n, k=k, pool=pool, trials=trials, gen=gen)
                recovery_by_k[k] = rate
            sweep[n] = recovery_by_k
            k_50_by_n[n] = _find_k_50(recovery_by_k)

    # Fit log(k_50) = alpha * log(N) + const
    pairs = [(n, k) for n, k in k_50_by_n.items() if k is not None]
    if len(pairs) >= 2:
        logs_n = np.array([math.log(n) for n, _ in pairs])
        logs_k = np.array([math.log(k) for _, k in pairs])
        # OLS slope
        alpha = float(np.polyfit(logs_n, logs_k, 1)[0])
        intercept = float(np.polyfit(logs_n, logs_k, 1)[1])
        # R^2
        predicted = alpha * logs_n + intercept
        ss_res = float(((logs_k - predicted) ** 2).sum())
        ss_tot = float(((logs_k - logs_k.mean()) ** 2).sum())
        r2 = 1 - ss_res / max(ss_tot, 1e-12)
    else:
        alpha = float("nan")
        intercept = float("nan")
        r2 = float("nan")

    headline = (
        f"alpha = {alpha:.3f} (R^2 = {r2:.3f}); "
        f"k_50%(1024)={k_50_by_n.get(1024)}, k_50%(4096)={k_50_by_n.get(4096)}, "
        f"k_50%(16384)={k_50_by_n.get(16384)}"
    )

    def page_curves(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(n_values)))
        for color, n in zip(colors, n_values):
            ks = sorted(sweep[n].keys())
            rs = [sweep[n][k] for k in ks]
            ax.plot(ks, rs, marker="o", color=color, linewidth=2, label=f"N={n}")
            k50 = k_50_by_n.get(n)
            if k50:
                ax.axvline(k50, color=color, linestyle=":", alpha=0.4)
        ax.set_xlabel("bundle size k")
        ax.set_ylabel("recovery rate")
        ax.set_title("Week 8: bundle-capacity recovery curves across N")
        ax.set_xscale("log")
        ax.set_ylim(-0.05, 1.05)
        ax.axhline(0.5, color="black", linestyle="--", alpha=0.3, label="50% recovery line")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3, which="both")
        pdf.savefig(fig)
        plt.close(fig)

    def page_alpha_fit(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ns_with_k50 = [n for n in n_values if k_50_by_n[n] is not None]
        k50s = [k_50_by_n[n] for n in ns_with_k50]
        ax.scatter(ns_with_k50, k50s, color="firebrick", s=80, zorder=3, label="empirical k_50%")
        # Fitted line
        if not math.isnan(alpha):
            n_fit = np.geomspace(min(ns_with_k50), max(ns_with_k50), 50)
            k_fit = np.exp(alpha * np.log(n_fit) + intercept)
            ax.plot(n_fit, k_fit, color="black", linewidth=2,
                    label=f"fit: k_50% = N^{alpha:.3f} * exp({intercept:.3f}) (R^2={r2:.3f})")
        # Predicted line: alpha=1 with M2 anchor
        anchor = k_50_by_n.get(1024) or 190
        n_pred = np.array(ns_with_k50)
        k_pred = anchor * (n_pred / 1024)
        ax.plot(n_pred, k_pred, color="steelblue", linewidth=1.5, linestyle="--",
                label=f"prediction alpha=1.0 (anchor at N=1024)")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("substrate dimension N")
        ax.set_ylabel("k_50% (bundle size at 50% recovery)")
        ax.set_title("Week 8: capacity scaling exponent fit")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3, which="both")
        pdf.savefig(fig)
        plt.close(fig)

    review = math.isnan(alpha) or not (0.8 <= alpha <= 1.2)

    return {
        "n_values": n_values,
        "k_values": k_values,
        "pool_size": pool_size,
        "trials_per_cell": trials,
        "recovery_sweep": {str(n): sweep[n] for n in n_values},
        "k_50_by_n": {str(n): k_50_by_n[n] for n in n_values},
        "alpha": alpha,
        "intercept": intercept,
        "r2": r2,
        "headline": headline,
        "review": review,
        "_pdf_extras": [page_curves, page_alpha_fit],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_scaling_capacity", seed=42, n=1024)
    result = experiment.run(spec, workload)
    summary = {k: v for k, v in result.metrics.items() if k not in ("recovery_sweep",)}
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
