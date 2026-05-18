"""Hyperbolic VSA tier-1 depth-scaling experiment.

Atoms live on the upper sheet of the Lorentz hyperboloid (Minkowski space). Bind/bundle/unbind
happen in the tangent space at the origin (Euclidean R^n), with exp/log maps for transit.
Cleanup uses hyperbolic distance for ranking.

Tier 1: this is the cheapest hyperbolic VSA construction. Bind/bundle don't directly use
the manifold curvature -- only cleanup does. If tier 1 shows promise (beta > HRR's 1.23),
tier 2 with true hyperbolic binding via Lorentz isometries is justified.

References for comparison:
  - FHRR k=2:    beta = 0.717
  - VTB:         beta = 0.979
  - Permutation: beta = 1.015
  - HRR pinned:  beta = 1.232 (likely small-N inflated)
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
from reference import hyperbolic as H  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N_VALUES = [256, 1024, 4096, 16384]
DEPTH_VALUES = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 22, 26, 30]
POOL_SIZE = 100
TRIALS = 100  # slightly fewer than HRR/VTB; hyperbolic is slower per trial


def measure_recovery_hyperbolic(
    n: int,
    depth: int,
    pool: torch.Tensor,
    role_atoms: dict[str, torch.Tensor],
    trials: int,
    gen: torch.Generator,
) -> float:
    pool_size = pool.shape[0]
    correct = 0
    for _ in range(trials):
        n_needed = depth + 1
        perm = torch.randperm(pool_size, generator=gen)[:n_needed]
        target_idx = int(perm[0].item())
        people_vecs = pool[perm]

        innermost = H.bundle(
            torch.stack(
                [
                    H.bind(people_vecs[0], role_atoms["AGENT"]),
                    H.bind(people_vecs[1], role_atoms["PATIENT"]),
                ]
            )
        )
        structure = innermost
        for d in range(depth - 1):
            structure = H.bundle(
                torch.stack(
                    [
                        H.bind(people_vecs[d + 2], role_atoms["BELIEVER"]),
                        H.bind(structure, role_atoms["CONTENT"]),
                    ]
                )
            )

        queried = structure
        for _ in range(depth - 1):
            queried = H.unbind(queried, role_atoms["CONTENT"])
        queried = H.unbind(queried, role_atoms["AGENT"])

        sims = H.similarity_to_pool(queried, pool)
        best = int(sims.argmax().item())
        if best == target_idx:
            correct += 1
    return correct / trials


def find_d_50(recovery_by_d):
    ds = sorted(recovery_by_d.keys())
    for i in range(len(ds) - 1):
        d_lo, d_hi = ds[i], ds[i + 1]
        r_lo, r_hi = recovery_by_d[d_lo], recovery_by_d[d_hi]
        if r_lo >= 0.5 and r_hi < 0.5:
            t = (0.5 - r_lo) / (r_hi - r_lo)
            return d_lo + t * (d_hi - d_lo)
    return None


def fit_beta(d_50_by_n):
    pairs = [(n, d) for n, d in d_50_by_n.items() if d is not None]
    if len(pairs) < 2:
        return float("nan"), float("nan"), float("nan")
    log2_n = np.array([math.log2(n) for n, _ in pairs])
    d_vals = np.array([d for _, d in pairs])
    coeffs = np.polyfit(log2_n, d_vals, 1)
    beta, intercept = float(coeffs[0]), float(coeffs[1])
    predicted = beta * log2_n + intercept
    ss_res = float(((d_vals - predicted) ** 2).sum())
    ss_tot = float(((d_vals - d_vals.mean()) ** 2).sum())
    r2 = 1 - ss_res / max(ss_tot, 1e-12)
    return beta, intercept, r2


def workload(ctx: experiment.ExperimentContext) -> dict:
    gen = ctx.generator
    quiet_bus = tracing.TraceBus(enabled=False)
    sweep: dict[int, dict[int, float]] = {}
    d_50_by_n: dict[int, float | None] = {}

    with tracing.using(quiet_bus):
        for n in N_VALUES:
            pool = torch.stack([H.make_atom(n, gen) for _ in range(POOL_SIZE)])
            role_atoms = {r: H.make_atom(n, gen) for r in ("AGENT", "PATIENT", "BELIEVER", "CONTENT")}
            recovery_by_d: dict[int, float] = {}
            for d in DEPTH_VALUES:
                if d + 1 > POOL_SIZE:
                    recovery_by_d[d] = 0.0
                    continue
                rate = measure_recovery_hyperbolic(
                    n=n, depth=d, pool=pool, role_atoms=role_atoms,
                    trials=TRIALS, gen=gen,
                )
                recovery_by_d[d] = rate
            sweep[n] = recovery_by_d
            d_50_by_n[n] = find_d_50(recovery_by_d)

    beta, intercept, r2 = fit_beta(d_50_by_n)
    headline = (
        f"Hyperbolic (tier 1) beta = {beta:.3f} (R^2 = {r2:.4f}); "
        f"HRR was 1.232, VTB 0.979, permutation 1.015, FHRR 0.717"
    )

    def page_curves(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        colors = plt.cm.viridis(np.linspace(0.2, 0.85, len(N_VALUES)))
        for color, n in zip(colors, N_VALUES):
            ds = sorted(sweep[n].keys())
            rs = [sweep[n][d] for d in ds]
            ax.plot(ds, rs, marker="o", color=color, linewidth=2, label=f"N={n}")
            d50 = d_50_by_n.get(n)
            if d50:
                ax.axvline(d50, color=color, linestyle=":", alpha=0.4)
        ax.set_xlabel("nesting depth")
        ax.set_ylabel("leaf-atom recovery rate")
        ax.set_title(f"Hyperbolic VSA tier-1 (tangent-space ops): beta={beta:.3f}")
        ax.set_ylim(-0.05, 1.05)
        ax.axhline(0.5, color="black", linestyle="--", alpha=0.3)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        pdf.savefig(fig)
        plt.close(fig)

    def page_compare(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ns = [n for n in N_VALUES if d_50_by_n[n] is not None]
        d50s = [d_50_by_n[n] for n in ns]
        ax.scatter(ns, d50s, color="darkgreen", s=80, zorder=3, label="Hyperbolic tier 1")
        if not math.isnan(beta):
            n_fit = np.geomspace(min(ns), max(ns), 50)
            d_fit = beta * np.log2(n_fit) + intercept
            ax.plot(n_fit, d_fit, color="darkgreen", linewidth=2,
                    label=f"Hyperbolic fit: beta={beta:.3f}, R^2={r2:.4f}")
        n_pred = np.array(ns) if ns else np.array(N_VALUES)
        ax.plot(n_pred, 1.232 * np.log2(n_pred) - 6.807, color="steelblue", linewidth=1.5, linestyle="--",
                label="HRR pinned: beta=1.232")
        ax.plot(n_pred, 1.015 * np.log2(n_pred) - 2.661, color="darkorange", linewidth=1.5, linestyle="--",
                label="Permutation: beta=1.015")
        ax.plot(n_pred, 0.979 * np.log2(n_pred) - 3.387, color="purple", linewidth=1.5, linestyle="--",
                label="VTB: beta=0.979")
        ax.plot(n_pred, 0.717 * np.log2(n_pred) - 0.629, color="firebrick", linewidth=1.5, linestyle="--",
                label="FHRR k=2: beta=0.717")
        ax.set_xscale("log")
        ax.set_xlabel("substrate dimension N (tangent-space dim)")
        ax.set_ylabel("depth_50%")
        ax.set_title("Hyperbolic VSA tier-1 vs Euclidean substrates")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3, which="both")
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "n_values": N_VALUES,
        "depth_values": DEPTH_VALUES,
        "pool_size": POOL_SIZE,
        "trials_per_cell": TRIALS,
        "recovery_sweep": {str(n): sweep[n] for n in N_VALUES},
        "d_50_by_n": {str(n): d_50_by_n[n] for n in N_VALUES},
        "beta": beta,
        "intercept": intercept,
        "r2": r2,
        "headline": headline,
        "_pdf_extras": [page_curves, page_compare],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_depth_hyperbolic", seed=42, n=1024)
    result = experiment.run(spec, workload)
    summary = {k: v for k, v in result.metrics.items() if k != "recovery_sweep"}
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
