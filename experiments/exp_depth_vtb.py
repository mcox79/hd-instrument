"""Depth-recovery scaling for VTB (Vector-Derived Transformation Binding), Gosmann 2019.

Same protocol as exp_depth_pinned_hrr.py, but using VTB primitives instead. Tests whether
VTB's claimed better stack-encoding depth recovery translates into a higher beta exponent
on our standard nested-structure protocol.

Reference for comparison:
- FHRR k=2: beta = 0.717
- HRR pinned: beta = 1.232
- Permutation: beta = 1.015 (theoretical optimum for noise-free VSA)

Constraint: N must be a perfect square. Picking N values from VSA-square sequence.
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
from reference import vtb  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Perfect squares: 32^2=1024, 64^2=4096, 90^2=8100~8192, 128^2=16384, 181^2=32761, 256^2=65536
N_VALUES = [1024, 4096, 16384, 65536]
DEPTH_VALUES = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22]
POOL_SIZE = 100
TRIALS = 150


def measure_recovery_vtb(
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
        people_vecs = pool[perm]
        target_idx = int(perm[0].item())

        innermost = vtb.bundle(
            torch.stack(
                [
                    vtb.bind(people_vecs[0], role_atoms["AGENT"]),
                    vtb.bind(people_vecs[1], role_atoms["PATIENT"]),
                ]
            )
        )
        structure = innermost
        for d in range(depth - 1):
            structure = vtb.bundle(
                torch.stack(
                    [
                        vtb.bind(people_vecs[d + 2], role_atoms["BELIEVER"]),
                        vtb.bind(structure, role_atoms["CONTENT"]),
                    ]
                )
            )

        queried = structure
        for _ in range(depth - 1):
            queried = vtb.unbind(queried, role_atoms["CONTENT"])
        queried = vtb.unbind(queried, role_atoms["AGENT"])

        sims = vtb.similarity(queried.unsqueeze(0).expand_as(pool), pool)
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
            pool = torch.stack([vtb.make_atom(n, gen) for _ in range(POOL_SIZE)])
            role_atoms = {r: vtb.make_atom(n, gen) for r in ("AGENT", "PATIENT", "BELIEVER", "CONTENT")}
            recovery_by_d: dict[int, float] = {}
            for d in DEPTH_VALUES:
                if d + 1 > POOL_SIZE:
                    recovery_by_d[d] = 0.0
                    continue
                rate = measure_recovery_vtb(
                    n=n, depth=d, pool=pool, role_atoms=role_atoms,
                    trials=TRIALS, gen=gen,
                )
                recovery_by_d[d] = rate
            sweep[n] = recovery_by_d
            d_50_by_n[n] = find_d_50(recovery_by_d)

    beta, intercept, r2 = fit_beta(d_50_by_n)
    headline = (
        f"VTB beta = {beta:.3f} (R^2 = {r2:.4f}); "
        f"HRR was 1.232, FHRR k=2 was 0.717, permutation was 1.015"
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
        ax.set_title(f"VTB depth scaling: beta={beta:.3f}")
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
        ax.scatter(ns, d50s, color="purple", s=80, zorder=3, label="VTB")
        if not math.isnan(beta):
            n_fit = np.geomspace(min(ns), max(ns), 50)
            d_fit = beta * np.log2(n_fit) + intercept
            ax.plot(n_fit, d_fit, color="purple", linewidth=2,
                    label=f"VTB fit: beta={beta:.3f}, R^2={r2:.4f}")
        n_pred = np.array(ns) if ns else np.array(N_VALUES)
        ax.plot(n_pred, 1.232 * np.log2(n_pred) - 6.807, color="steelblue", linewidth=1.5, linestyle="--",
                label="HRR pinned: beta=1.232")
        ax.plot(n_pred, 0.717 * np.log2(n_pred) - 0.629, color="firebrick", linewidth=1.5, linestyle="--",
                label="FHRR standard: beta=0.717")
        ax.plot(n_pred, 1.015 * np.log2(n_pred) - 2.661, color="darkorange", linewidth=1.5, linestyle="--",
                label="Permutation: beta=1.015")
        ax.set_xscale("log")
        ax.set_xlabel("substrate dimension N")
        ax.set_ylabel("depth_50%")
        ax.set_title("VTB vs HRR / FHRR / permutation depth scaling")
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
    spec = experiment.ExperimentSpec(name="exp_depth_vtb", seed=42, n=1024)
    result = experiment.run(spec, workload)
    summary = {k: v for k, v in result.metrics.items() if k != "recovery_sweep"}
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
