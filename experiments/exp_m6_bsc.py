"""M6: FHRR vs BSC bundle capacity at matched N. The hardware-substrate comparison.

Same role-filler bundling experiment as M2 run twice -- once with FHRR (complex64) and once
with BSC (int8). Compares recovery curves and reports operations + storage cost per substrate.
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms as hd_atoms, binding as hd_binding, bundling as hd_bundling
from hdlab import experiment, memory  # noqa: E402
from reference import bsc  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def _bsc_codebook_lookup(stacked: torch.Tensor, names: list[str], query: torch.Tensor) -> tuple[str, float]:
    sims = bsc.similarity(query.unsqueeze(0).expand_as(stacked), stacked)
    best = int(sims.argmax())
    return names[best], float(sims[best])


def _measure_fhrr(n: int, k_values: list[int], trials: int, pool_size: int, gen: torch.Generator) -> dict:
    cb = memory.Codebook(n, torch.complex64)
    fillers: list[torch.Tensor] = []
    names: list[str] = []
    for i in range(pool_size):
        v = hd_atoms.make_atom_fhrr(n, gen)
        cb.add(f"f{i:03d}", v)
        fillers.append(v)
        names.append(f"f{i:03d}")
    recovery: dict[int, float] = {}
    for k in k_values:
        correct = 0
        denom = 0
        for _ in range(trials):
            perm = torch.randperm(pool_size, generator=gen)[:k].tolist()
            roles = [hd_atoms.make_atom_fhrr(n, gen) for _ in range(k)]
            bs = [hd_binding.bind(roles[i], fillers[perm[i]]) for i in range(k)]
            bundle = hd_bundling.bundle(torch.stack(bs))
            for i in range(k):
                rec = hd_binding.unbind(bundle, roles[i])
                got, _ = cb.lookup(rec)
                if got == names[perm[i]]:
                    correct += 1
                denom += 1
        recovery[k] = correct / denom
    return recovery


def _measure_bsc(n: int, k_values: list[int], trials: int, pool_size: int, gen: torch.Generator) -> dict:
    fillers = torch.stack([bsc.make_atom(n, gen) for _ in range(pool_size)])
    names = [f"f{i:03d}" for i in range(pool_size)]
    recovery: dict[int, float] = {}
    for k in k_values:
        correct = 0
        denom = 0
        for _ in range(trials):
            perm = torch.randperm(pool_size, generator=gen)[:k].tolist()
            roles = [bsc.make_atom(n, gen) for _ in range(k)]
            bs = torch.stack([bsc.bind(roles[i], fillers[perm[i]]) for i in range(k)])
            bundle = bsc.bundle(bs)
            for i in range(k):
                rec = bsc.unbind(bundle, roles[i])
                got, _ = _bsc_codebook_lookup(fillers, names, rec)
                if got == names[perm[i]]:
                    correct += 1
                denom += 1
        recovery[k] = correct / denom
    return recovery


def workload(ctx: experiment.ExperimentContext) -> dict:
    n = ctx.spec.n
    gen = ctx.generator
    k_values = [2, 5, 10, 20, 30, 50, 75, 100, 150]
    trials = 15  # smaller than M2 for runtime
    pool_size = 200

    # Use independent generators to ensure FHRR and BSC see the same trial structure but separate randomness
    gen_f = torch.Generator().manual_seed(ctx.spec.seed)
    gen_b = torch.Generator().manual_seed(ctx.spec.seed + 1)

    fhrr_recovery = _measure_fhrr(n, k_values, trials, pool_size, gen_f)
    bsc_recovery = _measure_bsc(n, k_values, trials, pool_size, gen_b)

    # Storage cost per atom
    fhrr_bytes_per_atom = n * 8  # complex64 = 8 bytes per component
    bsc_bytes_per_atom = n * 1   # int8 = 1 byte per component
    storage_ratio = fhrr_bytes_per_atom / bsc_bytes_per_atom

    headline = (
        f"recovery@k=50: FHRR={fhrr_recovery[50] * 100:.0f}%, "
        f"BSC={bsc_recovery[50] * 100:.0f}%; "
        f"FHRR uses {storage_ratio}x more memory per atom"
    )

    def page_compare(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        fr = [fhrr_recovery[k] for k in k_values]
        br = [bsc_recovery[k] for k in k_values]
        ax.plot(k_values, fr, marker="o", color="steelblue", linewidth=2, label="FHRR (complex64, 8 B/comp)")
        ax.plot(k_values, br, marker="s", color="firebrick", linewidth=2, label="BSC (int8, 1 B/comp)")
        ax.set_xlabel("bundle size k")
        ax.set_ylabel("recovery rate")
        ax.set_title(f"M6: FHRR vs BSC bundle capacity at N={n} ({pool_size}-filler codebook)")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "n": n,
        "k_values": k_values,
        "trials": trials,
        "pool_size": pool_size,
        "fhrr_recovery": fhrr_recovery,
        "bsc_recovery": bsc_recovery,
        "fhrr_bytes_per_atom": fhrr_bytes_per_atom,
        "bsc_bytes_per_atom": bsc_bytes_per_atom,
        "storage_ratio_fhrr_to_bsc": storage_ratio,
        "headline": headline,
        "_pdf_extras": [page_compare],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_m6_bsc", seed=42, n=1024)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
