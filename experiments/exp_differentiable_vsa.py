"""Differentiable VSA: bind/bundle/unbind as small MLPs trained end-to-end.

Hypothesis: hand-rolled VSA operations (circular convolution, etc.) are designed for
analytical tractability, not for maximum task-specific capacity. Gradient-trained operations
should learn task-adapted constants that get better depth recovery at fixed N.

Test: train at N=256 (kept small for CPU tractability) on synthetic role-filler structures
at depths 1-10. Evaluate at depths 1-20 and measure the depth-50% crossing. Compare to
HRR's depth-50% at the same N.

If learned d_50% is substantially higher than HRR's d_50% at the same N, learning is
task-adapting the operations beyond the standard VSA information bound. If learned d_50%
is comparable to HRR, the bound is fundamental rather than just hand-rolled-VSA-specific.
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
N = 256
HIDDEN = 512  # 2x N
POOL_SIZE = 50
N_TRAIN_STEPS = 2000
BATCH_SIZE = 16
DEPTH_VALUES_EVAL = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20]
DEPTHS_TRAIN_RANGE = (1, 10)  # uniform over this range during training
TRIALS_PER_DEPTH = 50
LR = 1e-3


class LearnedVSA(torch.nn.Module):
    """Three MLPs for bind, unbind, bundle. Each takes 2 N-dim vectors -> 1 N-dim vector."""

    def __init__(self, n: int, hidden: int):
        super().__init__()
        self.n = n
        # Initialize with circular convolution as a good prior - identity-like at start
        self.bind_net = torch.nn.Sequential(
            torch.nn.Linear(2 * n, hidden),
            torch.nn.Tanh(),
            torch.nn.Linear(hidden, n),
        )
        self.unbind_net = torch.nn.Sequential(
            torch.nn.Linear(2 * n, hidden),
            torch.nn.Tanh(),
            torch.nn.Linear(hidden, n),
        )
        self.bundle_net = torch.nn.Sequential(
            torch.nn.Linear(2 * n, hidden),
            torch.nn.Tanh(),
            torch.nn.Linear(hidden, n),
        )

    def bind(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        out = self.bind_net(torch.cat([x, y], dim=-1))
        return out / (out.norm(dim=-1, keepdim=True) + 1e-9)

    def unbind(self, c: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        out = self.unbind_net(torch.cat([c, y], dim=-1))
        return out / (out.norm(dim=-1, keepdim=True) + 1e-9)

    def bundle(self, a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        out = self.bundle_net(torch.cat([a, b], dim=-1))
        return out / (out.norm(dim=-1, keepdim=True) + 1e-9)


def make_atom(n: int, gen: torch.Generator) -> torch.Tensor:
    v = torch.randn(n, generator=gen, dtype=torch.float32) / math.sqrt(n)
    return v / v.norm()


def build_nested_structure(
    model: LearnedVSA,
    depth: int,
    people: torch.Tensor,
    role_atoms: dict[str, torch.Tensor],
) -> tuple[torch.Tensor, torch.Tensor]:
    """Build a depth-d nested structure (loves at the bottom, believes wrappers above).
    Returns (structure, target_leaf_atom). target is people[0]."""
    target = people[0]
    structure = model.bundle(
        model.bind(role_atoms["AGENT"], people[0]),
        model.bind(role_atoms["PATIENT"], people[1]),
    )
    for d in range(depth - 1):
        structure = model.bundle(
            model.bind(role_atoms["BELIEVER"], people[d + 2]),
            model.bind(role_atoms["CONTENT"], structure),
        )
    return structure, target


def query_leaf(
    model: LearnedVSA,
    structure: torch.Tensor,
    role_atoms: dict[str, torch.Tensor],
    depth: int,
) -> torch.Tensor:
    """Unwind d-1 CONTENT unbinds, then 1 AGENT unbind."""
    queried = structure
    for _ in range(depth - 1):
        queried = model.unbind(queried, role_atoms["CONTENT"])
    queried = model.unbind(queried, role_atoms["AGENT"])
    return queried


def train_model(
    model: LearnedVSA,
    pool: torch.Tensor,
    role_atoms: dict[str, torch.Tensor],
    n_steps: int,
    batch_size: int,
    depth_range: tuple[int, int],
    lr: float,
    gen: torch.Generator,
) -> list[float]:
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    losses = []
    pool_size = pool.shape[0]
    for step in range(n_steps):
        optimizer.zero_grad()
        depth = int(torch.randint(depth_range[0], depth_range[1] + 1, (1,), generator=gen).item())
        batch_loss = 0.0
        for _ in range(batch_size):
            n_needed = depth + 1
            if n_needed > pool_size:
                continue
            perm = torch.randperm(pool_size, generator=gen)[:n_needed]
            people = pool[perm]
            structure, target = build_nested_structure(model, depth, people, role_atoms)
            recovered = query_leaf(model, structure, role_atoms, depth)
            # MSE loss between recovered and target (both normalized)
            loss = (1 - (recovered * target).sum()).pow(2)
            batch_loss = batch_loss + loss
        batch_loss = batch_loss / batch_size
        batch_loss.backward()
        optimizer.step()
        if step % 100 == 0:
            losses.append(float(batch_loss.item()))
    return losses


def measure_recovery_learned(
    model: LearnedVSA,
    depth: int,
    pool: torch.Tensor,
    role_atoms: dict[str, torch.Tensor],
    trials: int,
    gen: torch.Generator,
) -> float:
    model.eval()
    pool_size = pool.shape[0]
    correct = 0
    with torch.no_grad():
        for _ in range(trials):
            n_needed = depth + 1
            if n_needed > pool_size:
                return 0.0
            perm = torch.randperm(pool_size, generator=gen)[:n_needed]
            people = pool[perm]
            target_idx = int(perm[0].item())
            structure, _ = build_nested_structure(model, depth, people, role_atoms)
            recovered = query_leaf(model, structure, role_atoms, depth)
            sims = (pool * recovered).sum(dim=-1)
            best = int(sims.argmax().item())
            if best == target_idx:
                correct += 1
    model.train()
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


def workload(ctx: experiment.ExperimentContext) -> dict:
    gen = ctx.generator
    quiet_bus = tracing.TraceBus(enabled=False)
    torch.manual_seed(ctx.spec.seed)

    with tracing.using(quiet_bus):
        # Build pool and roles (frozen)
        pool = torch.stack([make_atom(N, gen) for _ in range(POOL_SIZE)])
        role_atoms = {r: make_atom(N, gen) for r in ("AGENT", "PATIENT", "BELIEVER", "CONTENT")}

        # Train
        model = LearnedVSA(N, HIDDEN)
        losses = train_model(
            model=model, pool=pool, role_atoms=role_atoms,
            n_steps=N_TRAIN_STEPS, batch_size=BATCH_SIZE,
            depth_range=DEPTHS_TRAIN_RANGE, lr=LR, gen=gen,
        )

        # Evaluate
        recovery_by_d: dict[int, float] = {}
        for d in DEPTH_VALUES_EVAL:
            rate = measure_recovery_learned(
                model=model, depth=d, pool=pool, role_atoms=role_atoms,
                trials=TRIALS_PER_DEPTH, gen=gen,
            )
            recovery_by_d[d] = rate

    d_50 = find_d_50(recovery_by_d)

    # HRR baseline at N=256: extrapolating from HRR pinned (beta=1.232, intercept=-6.807)
    # at N=256: d_50_hrr = 1.232 * log2(256) + (-6.807) = 1.232 * 8 - 6.807 = 3.05
    hrr_baseline_d50 = 1.232 * math.log2(N) - 6.807

    headline = (
        f"Learned VSA at N={N}: d_50% = {d_50}; HRR predicted d_50% at same N = {hrr_baseline_d50:.2f}; "
        f"final training loss = {losses[-1] if losses else 'n/a'}"
    )

    def page_curves(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ds = sorted(recovery_by_d.keys())
        rs = [recovery_by_d[d] for d in ds]
        ax.plot(ds, rs, marker="o", color="purple", linewidth=2, label="Learned VSA")
        if d_50 is not None:
            ax.axvline(d_50, color="purple", linestyle=":", alpha=0.4, label=f"learned d_50%={d_50:.1f}")
        ax.axvline(hrr_baseline_d50, color="firebrick", linestyle=":", alpha=0.4,
                    label=f"HRR d_50% extrapolated={hrr_baseline_d50:.2f}")
        ax.set_xlabel("nesting depth")
        ax.set_ylabel("leaf-atom recovery rate")
        ax.set_title(f"Differentiable VSA (trained): N={N}, {N_TRAIN_STEPS} steps")
        ax.set_ylim(-0.05, 1.05)
        ax.axhline(0.5, color="black", linestyle="--", alpha=0.3)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        pdf.savefig(fig)
        plt.close(fig)

    def page_training(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.plot(losses, color="steelblue", linewidth=1.5)
        ax.set_xlabel("training step / 100")
        ax.set_ylabel("batch loss")
        ax.set_title("Training loss over time")
        ax.set_yscale("log")
        ax.grid(True, alpha=0.3, which="both")
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "n": N,
        "hidden": HIDDEN,
        "pool_size": POOL_SIZE,
        "n_train_steps": N_TRAIN_STEPS,
        "batch_size": BATCH_SIZE,
        "depths_train": DEPTHS_TRAIN_RANGE,
        "depths_eval": DEPTH_VALUES_EVAL,
        "trials_per_depth": TRIALS_PER_DEPTH,
        "lr": LR,
        "recovery_by_d": recovery_by_d,
        "d_50": d_50,
        "hrr_baseline_d50": hrr_baseline_d50,
        "training_losses": losses,
        "headline": headline,
        "_pdf_extras": [page_curves, page_training],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_differentiable_vsa", seed=42, n=N)
    result = experiment.run(spec, workload)
    summary = {k: v for k, v in result.metrics.items() if k != "recovery_by_d"}
    print(json.dumps(summary, indent=2, default=str))
    print()
    print('recovery_by_d:', json.dumps(result.metrics['recovery_by_d'], default=str))


if __name__ == "__main__":
    main()
