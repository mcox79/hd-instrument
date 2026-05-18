"""BSC bundle-capacity scaling exponent vs N.

Same protocol as exp_scaling_capacity.py but for BSC (+/-1 binary substrate):
  - atoms: random +/-1 vectors (int8 storage)
  - bind/unbind: elementwise multiplication (self-inverse)
  - bundle: sign of column sum
  - similarity: normalized integer inner product
"""

from __future__ import annotations

import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

from hdlab import experiment, tracing  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def _make_bsc_atoms_batch(k: int, n: int, gen: torch.Generator) -> torch.Tensor:
    """Batch of k random +/-1 atoms, int8."""
    bits = torch.randint(0, 2, (k, n), generator=gen)
    return (2 * bits - 1).to(torch.int8)


def _measure_recovery_batch(
    n: int,
    k: int,
    pool: torch.Tensor,
    trials: int,
    gen: torch.Generator,
) -> float:
    pool_size = pool.shape[0]
    pool_f = pool.to(torch.float32)  # for matmul
    correct = 0
    denom = 0
    for _ in range(trials):
        indices = torch.randint(0, pool_size, (k,), generator=gen)
        chosen_fillers = pool[indices]  # (k, n)
        roles = _make_bsc_atoms_batch(k, n, gen)
        # BSC bind: elementwise mul
        bindings_tensor = (roles * chosen_fillers).to(torch.int8)  # (k, n)
        # BSC bundle: sign of column sum
        s = bindings_tensor.to(torch.int32).sum(dim=0)
        bundle = torch.where(s >= 0, torch.ones_like(s), -torch.ones_like(s)).to(torch.int8)
        # Batch unbind: bundle * roles elementwise
        unbound = (bundle.unsqueeze(0) * roles).to(torch.float32)  # (k, n)
        # Batch similarity: unbound @ pool.T / n
        sims = unbound @ pool_f.T / n  # (k, pool_size)
        best = sims.argmax(dim=1)
        correct += (best == indices).sum().item()
        denom += k
    return correct / denom


def _find_k_50(recovery_by_k: dict[int, float]) -> float | None:
    ks_sorted = sorted(recovery_by_k.keys())
    for i in range(len(ks_sorted) - 1):
        k_lo, k_hi = ks_sorted[i], ks_sorted[i + 1]
        r_lo, r_hi = recovery_by_k[k_lo], recovery_by_k[k_hi]
        if r_lo >= 0.5 and r_hi < 0.5:
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

    quiet_bus = tracing.TraceBus(enabled=False)

    sweep: dict[int, dict[int, float]] = {}
    k_50_by_n: dict[int, float | None] = {}

    with tracing.using(quiet_bus):
        for n in n_values:
            pool = _make_bsc_atoms_batch(pool_size, n, gen)
            recovery_by_k: dict[int, float] = {}
            for k in k_values:
                rate = _measure_recovery_batch(n=n, k=k, pool=pool, trials=trials, gen=gen)
                recovery_by_k[k] = rate
            sweep[n] = recovery_by_k
            k_50_by_n[n] = _find_k_50(recovery_by_k)

    pairs = [(n, k) for n, k in k_50_by_n.items() if k is not None]
    if len(pairs) >= 2:
        logs_n = np.array([math.log(n) for n, _ in pairs])
        logs_k = np.array([math.log(k) for _, k in pairs])
        coeffs = np.polyfit(logs_n, logs_k, 1)
        alpha = float(coeffs[0])
        intercept = float(coeffs[1])
        predicted = alpha * logs_n + intercept
        ss_res = float(((logs_k - predicted) ** 2).sum())
        ss_tot = float(((logs_k - logs_k.mean()) ** 2).sum())
        r2 = 1 - ss_res / max(ss_tot, 1e-12)
    else:
        alpha = float("nan")
        intercept = float("nan")
        r2 = float("nan")

    # Comparison anchor: FHRR result at N=1024 was k_50% ~ 217 (from previous experiment).
    # BSC at N=1024 from M6 had ~50% at k ~ 85.
    fhrr_k50_at_1024 = 217
    bsc_k50_at_1024 = k_50_by_n.get(1024)
    ratio_fhrr_to_bsc = fhrr_k50_at_1024 / bsc_k50_at_1024 if bsc_k50_at_1024 else None

    headline = (
        f"BSC alpha = {alpha:.3f} (R^2 = {r2:.4f}); "
        f"k_50%(1024)={bsc_k50_at_1024}, k_50%(16384)={k_50_by_n.get(16384)}; "
        f"FHRR/BSC capacity ratio = {ratio_fhrr_to_bsc:.2f}"
        if ratio_fhrr_to_bsc else f"BSC alpha = {alpha:.3f}; k_50%(1024)={bsc_k50_at_1024}"
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
        ax.set_title("Week 8: BSC bundle-capacity recovery curves across N")
        ax.set_xscale("log")
        ax.set_ylim(-0.05, 1.05)
        ax.axhline(0.5, color="black", linestyle="--", alpha=0.3)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3, which="both")
        pdf.savefig(fig)
        plt.close(fig)

    def page_alpha_fit(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ns = [n for n in n_values if k_50_by_n[n] is not None]
        k50s = [k_50_by_n[n] for n in ns]
        ax.scatter(ns, k50s, color="firebrick", s=80, zorder=3, label="BSC empirical k_50%")
        if not math.isnan(alpha):
            n_fit = np.geomspace(min(ns), max(ns), 50)
            k_fit = np.exp(alpha * np.log(n_fit) + intercept)
            ax.plot(n_fit, k_fit, color="black", linewidth=2,
                    label=f"BSC fit: k_50% = N^{alpha:.3f} (R^2={r2:.4f})")
        # Overlay FHRR result for comparison
        fhrr_alpha = 1.003
        fhrr_intercept = -1.575
        n_fhrr = np.array(ns)
        k_fhrr = np.exp(fhrr_alpha * np.log(n_fhrr) + fhrr_intercept)
        ax.plot(n_fhrr, k_fhrr, color="steelblue", linewidth=1.5, linestyle="--",
                label=f"FHRR (alpha={fhrr_alpha:.3f}, from prior experiment)")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("substrate dimension N")
        ax.set_ylabel("k_50%")
        ax.set_title("Week 8: BSC vs FHRR capacity-scaling comparison")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3, which="both")
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "n_values": n_values,
        "k_values": k_values,
        "pool_size": pool_size,
        "trials_per_cell": trials,
        "recovery_sweep": {str(n): sweep[n] for n in n_values},
        "k_50_by_n": {str(n): k_50_by_n[n] for n in n_values},
        "alpha_bsc": alpha,
        "intercept_bsc": intercept,
        "r2_bsc": r2,
        "fhrr_alpha_reference": 1.003,
        "fhrr_k50_at_1024_reference": fhrr_k50_at_1024,
        "ratio_fhrr_to_bsc_at_1024": ratio_fhrr_to_bsc,
        "headline": headline,
        "review": math.isnan(alpha) or not (0.8 <= alpha <= 1.2),
        "_pdf_extras": [page_curves, page_alpha_fit],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_scaling_bsc", seed=42, n=1024)
    result = experiment.run(spec, workload)
    summary = {k: v for k, v in result.metrics.items() if k != "recovery_sweep"}
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
