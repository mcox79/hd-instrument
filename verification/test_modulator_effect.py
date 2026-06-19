"""Each modulator moves its target metric monotonically; non-target metrics are isolated."""

from __future__ import annotations

import torch

from hdlab import atoms, binding, bundling, memory, modulators, tracing


def test_attention_changes_cleanup_precision() -> None:
    """Raising the attention threshold raises cleanup precision and lowers recall."""
    n = 1024
    k = 20
    gen = torch.Generator().manual_seed(42)

    cb = memory.Codebook(n, torch.complex64)
    stored: list[torch.Tensor] = []
    for i in range(k):
        a = atoms.make_atom_fhrr(n, gen)
        cb.add(f"a{i}", a)
        stored.append(a)

    # True queries: phase-jittered versions of stored atoms (should still match).
    true_queries: list[torch.Tensor] = []
    for a in stored:
        jitter = (torch.rand(n, generator=gen) - 0.5) * 0.4
        rot = torch.complex(torch.cos(jitter), torch.sin(jitter)).to(a.dtype)
        true_queries.append(a * rot)

    # Junk queries: random new atoms (don't match anything in the codebook).
    junk_queries = [atoms.make_atom_fhrr(n, gen) for _ in range(k)]

    precisions: list[float] = []
    recalls: list[float] = []
    for att in [0.0, 0.1, 0.3, 0.7]:
        with modulators.using(attention=att):
            tp = 0
            fp = 0
            for i, q in enumerate(true_queries):
                name, _ = cb.lookup(q)
                if name == f"a{i}":
                    tp += 1
                elif name is not None:
                    fp += 1
            for q in junk_queries:
                name, _ = cb.lookup(q)
                if name is not None:
                    fp += 1
            returned = tp + fp
            precision = tp / max(returned, 1)
            recall = tp / k
            precisions.append(precision)
            recalls.append(recall)

    # Precision should rise monotonically (allow tiny noise) as attention rises.
    assert precisions[-1] > precisions[0] + 0.1, f"Precision didn't rise: {precisions}"
    # Recall should not increase as attention rises (rejection can only remove returns).
    for i in range(1, len(recalls)):
        assert recalls[i] <= recalls[i - 1] + 1e-9, f"Recall increased with attention: {recalls}"


def test_recency_biases_bundling() -> None:
    """High recency makes the newest bundled item dominate the superposition."""
    n = 1024
    gen = torch.Generator().manual_seed(0)
    vecs = atoms.make_atoms(5, n, torch.complex64, gen)
    newest = vecs[-1]
    oldest = vecs[0]

    with modulators.using(recency=0.0):
        b_uniform = bundling.bundle(vecs)
    sim_uniform_newest = float(atoms.similarity(b_uniform, newest))
    sim_uniform_oldest = float(atoms.similarity(b_uniform, oldest))

    with modulators.using(recency=0.9):
        b_recent = bundling.bundle(vecs)
    sim_recent_newest = float(atoms.similarity(b_recent, newest))
    sim_recent_oldest = float(atoms.similarity(b_recent, oldest))

    assert sim_recent_newest > sim_uniform_newest, "High recency should boost newest sim"
    assert sim_recent_oldest < sim_uniform_oldest, "High recency should reduce oldest sim"
    assert sim_recent_newest > sim_recent_oldest + 0.3, (
        f"Recency did not bias enough: newest={sim_recent_newest:.3f}, oldest={sim_recent_oldest:.3f}"
    )


def test_modulator_isolation() -> None:
    """Changing one modulator must not move metrics controlled by another."""
    n = 1024
    gen = torch.Generator().manual_seed(0)
    vecs = atoms.make_atoms(5, n, torch.complex64, gen)

    # Bundle output should not depend on attention.
    with modulators.using(attention=0.0, recency=0.0):
        b1 = bundling.bundle(vecs)
    with modulators.using(attention=0.9, recency=0.0):
        b2 = bundling.bundle(vecs)
    assert torch.equal(b1, b2), "Bundle output should not depend on attention"

    # Cleanup behaviour on an exact match should not depend on recency.
    cb = memory.Codebook(n, torch.complex64)
    a = atoms.make_atom_fhrr(n, gen)
    cb.add("a", a)
    with modulators.using(attention=0.0, recency=0.0):
        r1 = cb.lookup(a)
    with modulators.using(attention=0.0, recency=0.9):
        r2 = cb.lookup(a)
    assert r1[0] == r2[0] and abs(r1[1] - r2[1]) < 1e-6, (
        f"Cleanup result should not depend on recency: {r1} vs {r2}"
    )


def test_setting_modulator_emits_trace_event() -> None:
    """The set_* functions and using() context manager produce trace events when active."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus):
        modulators.set_attention(0.5)
        modulators.set_reward(1.0)
        modulators.set_arousal(0.7)
        modulators.set_recency(0.3)
        modulators.set_gating("genealogy", 1.0)
    modulators.reset()
    ops = [e.op for e in bus.flush()]
    assert ops == [
        "modulators.set_attention",
        "modulators.set_reward",
        "modulators.set_arousal",
        "modulators.set_recency",
        "modulators.set_gating",
    ], f"Wrong op sequence: {ops}"


def test_modulator_state_appears_in_trace_events() -> None:
    """Each trace event records the active modulator state at the time of emission."""
    bus = tracing.TraceBus(enabled=True)
    with tracing.using(bus), modulators.using(attention=0.42, recency=0.17):
        gen = torch.Generator().manual_seed(0)
        a = atoms.make_atom_fhrr(256, gen)
        b = atoms.make_atom_fhrr(256, gen)
        _ = binding.bind(a, b)
    events = bus.flush()
    assert events, "No events emitted"
    for e in events:
        assert e.modulator_state["attention"] == 0.42
        assert e.modulator_state["recency"] == 0.17
