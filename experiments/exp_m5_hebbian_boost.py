"""M5: Hebbian-augmented bundling. Does learning shift the M2 capacity curve up?

Setup: persistent (role, filler) facts with fixed atom identities. A training phase reinforces
correct (role, filler) co-occurrence via reward-modulated Hebbian. A test phase compares
recovery via plain similarity cleanup vs cleanup boosted by Hebbian weight.

Cleanup-with-boost rule:
    score(candidate) = similarity(query, candidate) + alpha * hebbian.weight(role, candidate)

If the substrate is doing its job, plain cleanup is already strong below k=75 (per M2).
The boost matters in the regime k >= 75 where M2 showed degradation.
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, binding, bundling, experiment, learning, memory, modulators  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def workload(ctx: experiment.ExperimentContext) -> dict:
    n = ctx.spec.n
    gen = ctx.generator
    n_facts = 30
    n_distractors = 100
    train_iterations = 800
    train_bundle_k = 5
    test_k_values = [10, 20, 30, 40, 50, 75]
    test_trials_per_k = 30
    # Small alpha because Hebbian weights grow to O(arousal*reward/decay) = ~200 at saturation.
    # Setting alpha ~ 1/200 puts the boost on the same scale as similarity scores.
    boost_alpha = 0.005

    # Filler codebook: 50 "fact fillers" + 100 distractors = 150 total
    cb = memory.Codebook(n, torch.complex64)
    filler_names: list[str] = []
    filler_vecs: list[torch.Tensor] = []
    for i in range(n_facts):
        name = f"fact_filler_{i:03d}"
        v = atoms.make_atom_fhrr(n, gen)
        cb.add(name, v)
        filler_names.append(name)
        filler_vecs.append(v)
    distractor_names: list[str] = []
    for i in range(n_distractors):
        name = f"distractor_{i:03d}"
        v = atoms.make_atom_fhrr(n, gen)
        cb.add(name, v)
        distractor_names.append(name)

    # Persistent role atoms and named role identities for Hebbian.
    role_vecs: dict[str, torch.Tensor] = {}
    role_names: list[str] = []
    for i in range(n_facts):
        name = f"role_{i:03d}"
        role_vecs[name] = atoms.make_atom_fhrr(n, gen)
        role_names.append(name)

    h = learning.HebbianAssociations(decay=0.005)

    # Training phase: bundle 10 random facts, query each, reinforce on success.
    with modulators.using(reward=1.0, arousal=1.0):
        for _ in range(train_iterations):
            perm = torch.randperm(n_facts, generator=gen)[:train_bundle_k].tolist()
            bindings_list = [
                binding.bind(role_vecs[role_names[i]], filler_vecs[i])
                for i in perm
            ]
            bundle = bundling.bundle(torch.stack(bindings_list))
            for i in perm:
                recovered_v = binding.unbind(bundle, role_vecs[role_names[i]])
                name, _ = cb.lookup(recovered_v)
                if name == filler_names[i]:
                    h.update([role_names[i], filler_names[i]])

    def hebbian_boosted_lookup(query: torch.Tensor, role_name: str) -> tuple[str | None, float]:
        """Plain sim + alpha * Hebbian weight, pick argmax."""
        stacked = torch.stack(cb._vectors)
        sims = atoms.similarity(query, stacked)
        all_names = cb._names
        boosts = torch.tensor(
            [h.weight(role_name, name) for name in all_names],
            dtype=sims.dtype,
        )
        combined = sims + boost_alpha * boosts
        best = int(combined.argmax())
        return all_names[best], float(sims[best])

    # Test phase: at each k, measure recovery with vs without boost.
    plain_recovery: dict[int, float] = {}
    boosted_recovery: dict[int, float] = {}
    for k in test_k_values:
        plain_correct = 0
        boosted_correct = 0
        denom = 0
        for _ in range(test_trials_per_k):
            perm = torch.randperm(n_facts, generator=gen)[:k].tolist()
            bindings_list = [
                binding.bind(role_vecs[role_names[i]], filler_vecs[i])
                for i in perm
            ]
            bundle = bundling.bundle(torch.stack(bindings_list))
            for i in perm:
                recovered_v = binding.unbind(bundle, role_vecs[role_names[i]])
                # Plain cleanup
                plain_name, _ = cb.lookup(recovered_v)
                if plain_name == filler_names[i]:
                    plain_correct += 1
                # Hebbian-boosted cleanup
                boosted_name, _ = hebbian_boosted_lookup(recovered_v, role_names[i])
                if boosted_name == filler_names[i]:
                    boosted_correct += 1
                denom += 1
        plain_recovery[k] = plain_correct / denom
        boosted_recovery[k] = boosted_correct / denom

    improvement_by_k = {k: boosted_recovery[k] - plain_recovery[k] for k in test_k_values}
    max_improvement_k = max(improvement_by_k, key=improvement_by_k.get)
    max_improvement = improvement_by_k[max_improvement_k]

    headline = (
        f"max improvement {max_improvement * 100:+.1f} pp at k={max_improvement_k} "
        f"(plain={plain_recovery[max_improvement_k] * 100:.0f}% -> "
        f"boosted={boosted_recovery[max_improvement_k] * 100:.0f}%)"
    )

    def page_compare(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ks = test_k_values
        plain = [plain_recovery[k] for k in ks]
        boosted = [boosted_recovery[k] for k in ks]
        ax.plot(ks, plain, marker="o", color="steelblue", linewidth=2, label="plain cleanup")
        ax.plot(ks, boosted, marker="s", color="seagreen", linewidth=2, label="Hebbian-boosted cleanup")
        for k in ks:
            ax.annotate(
                f"+{(boosted_recovery[k] - plain_recovery[k]) * 100:+.1f}pp",
                xy=(k, boosted_recovery[k]),
                xytext=(0, 6),
                textcoords="offset points",
                fontsize=8,
                ha="center",
                color="darkgreen" if boosted_recovery[k] > plain_recovery[k] else "darkred",
            )
        ax.set_xlabel("bundle size k")
        ax.set_ylabel("filler-recovery rate")
        ax.set_title(
            f"M5: Hebbian boost on cleanup ({train_iterations} training iters, alpha={boost_alpha})"
        )
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "n_facts": n_facts,
        "n_distractors": n_distractors,
        "train_iterations": train_iterations,
        "train_bundle_k": train_bundle_k,
        "test_k_values": test_k_values,
        "test_trials_per_k": test_trials_per_k,
        "boost_alpha": boost_alpha,
        "plain_recovery": plain_recovery,
        "boosted_recovery": boosted_recovery,
        "improvement_by_k": improvement_by_k,
        "max_improvement_k": max_improvement_k,
        "max_improvement": max_improvement,
        "headline": headline,
        "review": max_improvement < 0.0,
        "_pdf_extras": [page_compare],
    }


def main() -> None:
    # N=256 puts us in the cleanup-degradation regime where Hebbian can plausibly help
    # (per the cliff analysis in A5 + M2's junk-floor math).
    spec = experiment.ExperimentSpec(name="exp_m5_hebbian_boost", seed=42, n=256)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
