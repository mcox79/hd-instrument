"""Pin the HRR depth exponent with 150 trials/cell so the d_50% interpolation is stable.

Shared protocol with exp_depth_pinned_fhrr_clipped.py and exp_depth_pinned_fhrr_fanout3.py:
- Same N grid {2048, 4096, 8192, 16384, 32768, 65536}
- Same depth grid
- 150 trials per cell
- pool=100 atoms, fan-out=2 per bundle level (same role-filler structure as M4)
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
N_VALUES = [2048, 4096, 8192, 16384, 32768, 65536]
DEPTH_VALUES = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22]
POOL_SIZE = 100
TRIALS = 150


def measure_recovery_hrr(
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

        innermost = bundling.bundle(
            torch.stack(
                [
                    binding.bind(role_atoms["AGENT"], people_vecs[0]),
                    binding.bind(role_atoms["PATIENT"], people_vecs[1]),
                ]
            )
        )
        structure = innermost
        for d in range(depth - 1):
            structure = bundling.bundle(
                torch.stack(
                    [
                        binding.bind(role_atoms["BELIEVER"], people_vecs[d + 2]),
                        binding.bind(role_atoms["CONTENT"], structure),
                    ]
                )
            )

        queried = structure
        for _ in range(depth - 1):
            queried = binding.unbind(queried, role_atoms["CONTENT"])
        queried = binding.unbind(queried, role_atoms["AGENT"])

        sims = atoms.similarity(queried.unsqueeze(0).expand_as(pool), pool)
        best = int(sims.argmax().item())
        if best == target_idx:
            correct += 1
    return correct / trials


def find_d_50(recovery_by_d: dict[int, float]) -> float | None:
    ds_sorted = sorted(recovery_by_d.keys())
    for i in range(len(ds_sorted) - 1):
        d_lo, d_hi = ds_sorted[i], ds_sorted[i + 1]
        r_lo, r_hi = recovery_by_d[d_lo], recovery_by_d[d_hi]
        if r_lo >= 0.5 and r_hi < 0.5:
            t = (0.5 - r_lo) / (r_hi - r_lo)
            return d_lo + t * (d_hi - d_lo)
    return None


def fit_beta(d_50_by_n: dict[int, float | None]) -> tuple[float, float, float]:
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
            pool = torch.randn((POOL_SIZE, n), generator=gen, dtype=torch.float32) / math.sqrt(n)
            role_atoms = {
                role_name: atoms.make_atom_hrr(n, gen)
                for role_name in ("AGENT", "PATIENT", "BELIEVER", "CONTENT")
            }
            recovery_by_d: dict[int, float] = {}
            for d in DEPTH_VALUES:
                if d + 1 > POOL_SIZE:
                    recovery_by_d[d] = 0.0
                    continue
                rate = measure_recovery_hrr(
                    n=n, depth=d, pool=pool, role_atoms=role_atoms,
                    trials=TRIALS, gen=gen,
                )
                recovery_by_d[d] = rate
            sweep[n] = recovery_by_d
            d_50_by_n[n] = find_d_50(recovery_by_d)

    beta, intercept, r2 = fit_beta(d_50_by_n)
    headline = f"HRR (150 trials) beta = {beta:.3f} (R^2 = {r2:.4f})"

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
        ax.set_title(f"HRR pinned (150 trials/cell): beta={beta:.3f}")
        ax.set_ylim(-0.05, 1.05)
        ax.axhline(0.5, color="black", linestyle="--", alpha=0.3)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        pdf.savefig(fig)
        plt.close(fig)

    def page_fit(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ns = [n for n in N_VALUES if d_50_by_n[n] is not None]
        d50s = [d_50_by_n[n] for n in ns]
        ax.scatter(ns, d50s, color="steelblue", s=80, zorder=3, label="HRR pinned")
        if not math.isnan(beta):
            n_fit = np.geomspace(min(ns), max(ns), 50)
            d_fit = beta * np.log2(n_fit) + intercept
            ax.plot(n_fit, d_fit, color="steelblue", linewidth=2,
                    label=f"fit: beta={beta:.3f}, R^2={r2:.4f}")
        ax.set_xscale("log")
        ax.set_xlabel("substrate dimension N")
        ax.set_ylabel("depth_50%")
        ax.set_title("HRR pinned depth-scaling fit")
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
        "_pdf_extras": [page_curves, page_fit],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_depth_pinned_hrr", seed=42, n=1024)
    result = experiment.run(spec, workload)
    summary = {k: v for k, v in result.metrics.items() if k != "recovery_sweep"}
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
