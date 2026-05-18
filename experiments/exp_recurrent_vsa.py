"""Recurrent VSA: cleanup-at-each-unbind-step during nested-structure unwinding.

Different from exp_connectivity_resonator.py: that experiment did multi-hop graph traversal.
This one tests SINGLE-EXPRESSION nested-structure recovery (same protocol as the depth-scaling
experiments) with iterative cleanup applied at every level of the unwinding chain.

Hypothesis: standard VSA unwinding compounds noise across d unbinding steps. If we 'snap'
the partial result to the nearest pool atom (or a softmax-weighted combination) at each step,
the per-step error is bounded rather than compounding. This is conceptually a Modern Hopfield
iteration applied to the nested-structure recovery problem.

If recovery is depth-independent (beta = 0), this is equivalent in spirit to memory-augmented
HDC but realized through soft cleanup rather than discrete pointer addressing.

If recovery still degrades with depth (beta > 0), the iterative cleanup isn't enough -- the
encoded representation has already lost information that no amount of post-hoc cleanup can
recover.
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
N_VALUES = [1024, 4096, 16384, 65536]
DEPTH_VALUES = [3, 5, 7, 9, 11, 13, 16, 20, 25, 30]
POOL_SIZE = 100
TRIALS = 100
CLEANUP_TEMPERATURE = 10.0  # softmax sharpness for per-step cleanup


def soft_cleanup_to_pool(raw: torch.Tensor, pool: torch.Tensor, temperature: float) -> torch.Tensor:
    """Soft cleanup: softmax-weighted sum of pool atoms based on similarity to raw.

    Hopfield-style associative recall, parametrized by temperature.
    """
    n = pool.shape[-1]
    sims = (pool @ raw.conj()).real / n
    weights = torch.softmax(sims * temperature, dim=0)
    return (weights.unsqueeze(-1) * pool).sum(dim=0)


def measure_recovery_recurrent(
    n: int,
    depth: int,
    pool: torch.Tensor,
    role_atoms: dict[str, torch.Tensor],
    trials: int,
    gen: torch.Generator,
    temperature: float,
) -> float:
    pool_size = pool.shape[0]
    # Build the cleanup pool for INTERMEDIATE results -- it should include the role atoms too
    # because the recovered intermediate at depth k is approximately some role*filler structure.
    # But to keep it simple, let's first try cleanup against just the filler pool.
    correct = 0
    for _ in range(trials):
        n_needed = depth + 1
        if n_needed > pool_size:
            return 0.0
        perm = torch.randperm(pool_size, generator=gen)[:n_needed]
        people_vecs = pool[perm]
        target_idx = int(perm[0].item())

        # Encode standard nested structure (like other depth experiments)
        innermost = bundling.bundle(
            torch.stack(
                [
                    binding.bind(role_atoms["AGENT"], people_vecs[0]),
                    binding.bind(role_atoms["PATIENT"], people_vecs[1]),
                ]
            )
        )
        structure = innermost
        intermediate_atoms_pool = [innermost]  # we'll keep these for cleanup
        for d in range(depth - 1):
            structure = bundling.bundle(
                torch.stack(
                    [
                        binding.bind(role_atoms["BELIEVER"], people_vecs[d + 2]),
                        binding.bind(role_atoms["CONTENT"], structure),
                    ]
                )
            )
            intermediate_atoms_pool.append(structure)

        # Build the cleanup pool: filler atoms + intermediate structures
        cleanup_pool = torch.cat(
            [pool, torch.stack(intermediate_atoms_pool)],
            dim=0,
        )

        # Query: unwind (depth - 1) CONTENT unbinds with soft cleanup at each step
        queried = structure
        for _ in range(depth - 1):
            queried = binding.unbind(queried, role_atoms["CONTENT"])
            queried = soft_cleanup_to_pool(queried, cleanup_pool, temperature)
        # Final unbind by AGENT, then cleanup against just the filler pool
        queried = binding.unbind(queried, role_atoms["AGENT"])
        sims = (pool @ queried.conj()).real / n
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
            pool = torch.stack([atoms.make_atom_fhrr(n, gen) for _ in range(POOL_SIZE)]).to(DEVICE)
            role_atoms = {
                r: atoms.make_atom_fhrr(n, gen)
                for r in ("AGENT", "PATIENT", "BELIEVER", "CONTENT")
            }
            recovery_by_d: dict[int, float] = {}
            for d in DEPTH_VALUES:
                if d + 1 > POOL_SIZE:
                    recovery_by_d[d] = 0.0
                    continue
                rate = measure_recovery_recurrent(
                    n=n, depth=d, pool=pool, role_atoms=role_atoms,
                    trials=TRIALS, gen=gen, temperature=CLEANUP_TEMPERATURE,
                )
                recovery_by_d[d] = rate
            sweep[n] = recovery_by_d
            d_50_by_n[n] = find_d_50(recovery_by_d)

    beta, intercept, r2 = fit_beta(d_50_by_n)
    headline = (
        f"Recurrent VSA (cleanup at each unbind) beta = {beta:.3f} (R^2 = {r2:.4f}); "
        f"reference: HRR pinned 1.232, pointer chain 0.0, FHRR 0.717"
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
        ax.set_title(f"Recurrent VSA (Hopfield-style cleanup at each unbind): beta={beta:.3f}")
        ax.set_ylim(-0.05, 1.05)
        ax.axhline(0.5, color="black", linestyle="--", alpha=0.3)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        pdf.savefig(fig)
        plt.close(fig)

    def page_compare(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ns = [n for n in N_VALUES if d_50_by_n[n] is not None]
        if ns:
            d50s = [d_50_by_n[n] for n in ns]
            ax.scatter(ns, d50s, color="orchid", s=100, zorder=3, label="Recurrent VSA (this)")
            if not math.isnan(beta):
                n_fit = np.geomspace(min(ns), max(ns), 50)
                d_fit = beta * np.log2(n_fit) + intercept
                ax.plot(n_fit, d_fit, color="orchid", linewidth=2,
                        label=f"Recurrent fit: beta={beta:.3f}, R^2={r2:.4f}")
        n_arr = np.array(N_VALUES)
        ax.axhline(87.5, color="darkgreen", linewidth=1.5, linestyle="--",
                   label="Pointer chain: d_50%~87 (limited by pool, not N)")
        ax.plot(n_arr, 1.232 * np.log2(n_arr) - 6.807, color="steelblue", linewidth=1.5, linestyle="--",
                label="HRR pinned: beta=1.232")
        ax.plot(n_arr, 0.717 * np.log2(n_arr) - 0.629, color="firebrick", linewidth=1.5, linestyle="--",
                label="FHRR k=2: beta=0.717")
        ax.set_xscale("log")
        ax.set_xlabel("substrate dimension N")
        ax.set_ylabel("depth_50%")
        ax.set_title("Recurrent VSA vs other architectures")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3, which="both")
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "n_values": N_VALUES,
        "depth_values": DEPTH_VALUES,
        "pool_size": POOL_SIZE,
        "trials_per_cell": TRIALS,
        "cleanup_temperature": CLEANUP_TEMPERATURE,
        "recovery_sweep": {str(n): sweep[n] for n in N_VALUES},
        "d_50_by_n": {str(n): d_50_by_n[n] for n in N_VALUES},
        "beta": beta,
        "intercept": intercept,
        "r2": r2,
        "headline": headline,
        "_pdf_extras": [page_curves, page_compare],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_recurrent_vsa", seed=42, n=1024)
    result = experiment.run(spec, workload)
    summary = {k: v for k, v in result.metrics.items() if k != "recovery_sweep"}
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
