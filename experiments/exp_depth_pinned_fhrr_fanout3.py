"""FHRR with fan-out=3 per bundle level: tests engineering alternative to wider substrate.

Standard depth experiments use k=2 per bundle level (e.g. believes() has BELIEVER + CONTENT).
With k=3, each outer level bundles three (role, filler) pairs. Fewer outer levels are needed
to reach the same content (since each one carries more information), but per-level signal
attenuation grows: signal magnitude per component after k=3 bundle is ~1/sqrt(3) vs 1/sqrt(2).

We measure "depth" the same way (number of outer wrappings), and compare beta. If k=3 gives
better effective compositional capacity at the same N, it's a useful engineering knob even
without switching substrates.

Inner-most structure: 3 (role, filler) bindings (AGENT, PATIENT, PREDICATE).
Outer wrappings: 3 (role, filler) bindings (BELIEVER, MODE, CONTENT).
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
FAN_OUT = 3


def measure_recovery_fanout3(
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
        # We need depth+2 distinct fillers: target leaf at AGENT, plus PATIENT, PREDICATE,
        # plus one BELIEVER per outer level.
        n_needed = (depth - 1) + 3  # 3 inner-most fillers + 1 BELIEVER per outer level
        if n_needed > pool_size:
            return 0.0
        perm = torch.randperm(pool_size, generator=gen)[:n_needed]
        target_idx = int(perm[0].item())

        # Innermost: bundle of 3 (role, filler) pairs.
        innermost = bundling.bundle(
            torch.stack(
                [
                    binding.bind(role_atoms["AGENT"], pool[perm[0]]),
                    binding.bind(role_atoms["PATIENT"], pool[perm[1]]),
                    binding.bind(role_atoms["PREDICATE"], pool[perm[2]]),
                ]
            )
        )
        structure = innermost
        # Outer wrappings, each adds 1 fresh BELIEVER filler from perm[3..]
        for d in range(depth - 1):
            believer_filler = pool[perm[3 + d]] if 3 + d < n_needed else pool[perm[-1]]
            mode_filler = pool[perm[3 + d]] if 3 + d < n_needed else pool[perm[-1]]
            structure = bundling.bundle(
                torch.stack(
                    [
                        binding.bind(role_atoms["BELIEVER"], believer_filler),
                        binding.bind(role_atoms["MODE"], mode_filler),
                        binding.bind(role_atoms["CONTENT"], structure),
                    ]
                )
            )

        queried = structure
        for _ in range(depth - 1):
            queried = binding.unbind(queried, role_atoms["CONTENT"])
        queried = binding.unbind(queried, role_atoms["AGENT"])

        sims = (queried.unsqueeze(0) @ pool.conj().T).real / n
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
            phases = torch.rand((POOL_SIZE, n), generator=gen) * (2.0 * math.pi)
            pool = torch.complex(torch.cos(phases), torch.sin(phases)).to(torch.complex64)
            role_atoms = {
                r: atoms.make_atom_fhrr(n, gen)
                for r in ("AGENT", "PATIENT", "PREDICATE", "BELIEVER", "MODE", "CONTENT")
            }
            recovery_by_d: dict[int, float] = {}
            for d in DEPTH_VALUES:
                rate = measure_recovery_fanout3(
                    n=n, depth=d, pool=pool, role_atoms=role_atoms,
                    trials=TRIALS, gen=gen,
                )
                recovery_by_d[d] = rate
            sweep[n] = recovery_by_d
            d_50_by_n[n] = find_d_50(recovery_by_d)

    beta, intercept, r2 = fit_beta(d_50_by_n)
    headline = (
        f"FHRR fan-out=3 (150 trials) beta = {beta:.3f} (R^2 = {r2:.4f}); "
        f"std FHRR fan-out=2 was beta=0.717"
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
        ax.set_title(f"FHRR fan-out=3: beta={beta:.3f}")
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
        ax.scatter(ns, d50s, color="purple", s=80, zorder=3, label="FHRR fan-out=3")
        if not math.isnan(beta):
            n_fit = np.geomspace(min(ns), max(ns), 50)
            d_fit = beta * np.log2(n_fit) + intercept
            ax.plot(n_fit, d_fit, color="purple", linewidth=2,
                    label=f"fan-out=3 fit: beta={beta:.3f}")
        n_pred = np.array(ns)
        ax.plot(n_pred, 0.717 * np.log2(n_pred) - 0.629, color="firebrick", linewidth=1.5, linestyle="--",
                label="FHRR fan-out=2: beta=0.717")
        ax.set_xscale("log")
        ax.set_xlabel("substrate dimension N")
        ax.set_ylabel("depth_50%")
        ax.set_title("FHRR fan-out=3 vs fan-out=2")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3, which="both")
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "n_values": N_VALUES,
        "depth_values": DEPTH_VALUES,
        "pool_size": POOL_SIZE,
        "trials_per_cell": TRIALS,
        "fan_out": FAN_OUT,
        "recovery_sweep": {str(n): sweep[n] for n in N_VALUES},
        "d_50_by_n": {str(n): d_50_by_n[n] for n in N_VALUES},
        "beta": beta,
        "intercept": intercept,
        "r2": r2,
        "headline": headline,
        "_pdf_extras": [page_curves, page_compare],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_depth_pinned_fhrr_fanout3", seed=42, n=1024)
    result = experiment.run(spec, workload)
    summary = {k: v for k, v in result.metrics.items() if k != "recovery_sweep"}
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
