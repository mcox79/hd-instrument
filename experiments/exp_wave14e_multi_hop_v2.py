"""Multi-hop reasoning v2 — bound triples e=subj*rel*obj with per-hop cleanup.

Per wave14e_multi_hop_reasoning_research: triple-binding with cleanup-between-hops
is THE primitive. BSC self-inverse algebra (x*x=1) makes chains clean.

Per-hop detection margin: sqrt(N/F) std devs. At N=4096, F=100: 6.4 sigma -> per-hop
error <1e-8 -> 50+ hops viable WITH cleanup.

Test:
- Build entity codebook (100 entities) and relation codebook (10 relations).
- Encode 50 facts as triples e_i = subj_i * rel_i * obj_i. Superpose: M = sign(sum e_i).
- 2-hop query: A * R1 -> recover B, then B * R2 -> recover C.
- 3-hop: A * R1 * R2 * R3 with cleanup at each step.

Pass: 2-hop >=80%, 3-hop >=60% with N=4096.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N = 4096
NUM_ENTITIES = 100
NUM_RELATIONS = 10
NUM_FACTS = 50
SEED = 17


def _say(m): print(m, flush=True)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def cleanup(noisy, codebook):
    """Hopfield-style cleanup: snap to nearest atom in codebook."""
    sims = codebook @ noisy / N
    best_idx = int(sims.argmax().item())
    return codebook[best_idx], best_idx, float(sims[best_idx].item())


def main():
    _say(f"Multi-hop reasoning v2: N={N}, {NUM_ENTITIES} entities, {NUM_RELATIONS} relations, {NUM_FACTS} facts")
    gen = torch.Generator().manual_seed(SEED)
    entity_atoms = make_bsc(NUM_ENTITIES, N, gen).to(DEVICE)
    relation_atoms = make_bsc(NUM_RELATIONS, N, gen).to(DEVICE)

    # Build a chain of facts: entity[i] --rel--> entity[i+1]
    fact_gen = torch.Generator().manual_seed(SEED * 7)
    fact_entities = torch.randperm(NUM_ENTITIES, generator=fact_gen)[:NUM_FACTS + 1].tolist()
    fact_relations = torch.randint(0, NUM_RELATIONS, (NUM_FACTS,), generator=fact_gen).tolist()
    facts = []
    for i in range(NUM_FACTS):
        subj = entity_atoms[fact_entities[i]]
        rel = relation_atoms[fact_relations[i]]
        obj = entity_atoms[fact_entities[i+1]]
        triple = subj * rel * obj  # element-wise: BSC binding
        # Sign-quantize
        triple = torch.sign(triple)
        triple = torch.where(triple == 0, torch.ones_like(triple), triple)
        facts.append(triple)

    # Superpose into fact-base M
    M = torch.sign(torch.stack(facts).sum(dim=0))
    M = torch.where(M == 0, torch.ones_like(M), M)

    # 1-hop query: A * R should give back obj (via M).
    # query = A * R; expected = M * query = obj (with cleanup)
    correct_1hop = 0
    correct_1hop_no_cleanup = 0
    for i in range(NUM_FACTS):
        A = entity_atoms[fact_entities[i]]
        R = relation_atoms[fact_relations[i]]
        query = A * R
        # Probe M: M * query = sum_j (subj_j * rel_j * obj_j) * (subj_i * rel_i)
        #                   = obj_i + noise(j != i terms)
        probe = M * query
        # Without cleanup: argmax over entity codebook
        sims_raw = entity_atoms @ probe / N
        no_cleanup_pred = int(sims_raw.argmax().item())
        if no_cleanup_pred == fact_entities[i+1]:
            correct_1hop_no_cleanup += 1
        # With cleanup: same here (already argmax)
        cleaned, idx, _ = cleanup(probe, entity_atoms)
        if idx == fact_entities[i+1]:
            correct_1hop += 1
    acc_1hop = correct_1hop / NUM_FACTS
    _say(f"\n  1-hop (probe fact i): accuracy = {acc_1hop*100:.1f}% (no-cleanup {correct_1hop_no_cleanup/NUM_FACTS*100:.1f}%)")

    # 2-hop: A * R1 -> B' (cleanup) -> B' * R2 -> C
    correct_2hop = 0
    correct_2hop_no_cleanup = 0
    for i in range(NUM_FACTS - 1):
        A = entity_atoms[fact_entities[i]]
        R1 = relation_atoms[fact_relations[i]]
        R2 = relation_atoms[fact_relations[i+1]]
        true_C = fact_entities[i+2]
        # Step 1: probe A * R1 against M -> B'
        probe1 = M * (A * R1)
        B_cleaned, b_idx, _ = cleanup(probe1, entity_atoms)
        # Step 2: probe B' * R2 against M -> C'
        probe2 = M * (B_cleaned * R2)
        C_cleaned, c_idx, _ = cleanup(probe2, entity_atoms)
        if c_idx == true_C:
            correct_2hop += 1
        # Without cleanup
        sims2 = entity_atoms @ probe2 / N
        no_cleanup_pred = int(sims2.argmax().item())
        if no_cleanup_pred == true_C:
            correct_2hop_no_cleanup += 1
    acc_2hop = correct_2hop / max(NUM_FACTS - 1, 1)
    acc_2hop_no = correct_2hop_no_cleanup / max(NUM_FACTS - 1, 1)
    _say(f"  2-hop (chain): cleanup = {acc_2hop*100:.1f}%  no-cleanup = {acc_2hop_no*100:.1f}%")

    # 3-hop
    correct_3hop = 0
    for i in range(NUM_FACTS - 2):
        A = entity_atoms[fact_entities[i]]
        R1 = relation_atoms[fact_relations[i]]
        R2 = relation_atoms[fact_relations[i+1]]
        R3 = relation_atoms[fact_relations[i+2]]
        true_D = fact_entities[i+3]
        probe1 = M * (A * R1)
        B, _, _ = cleanup(probe1, entity_atoms)
        probe2 = M * (B * R2)
        C, _, _ = cleanup(probe2, entity_atoms)
        probe3 = M * (C * R3)
        D, d_idx, _ = cleanup(probe3, entity_atoms)
        if d_idx == true_D:
            correct_3hop += 1
    acc_3hop = correct_3hop / max(NUM_FACTS - 2, 1)
    _say(f"  3-hop (chain): cleanup = {acc_3hop*100:.1f}%")

    # 5-hop (stretch goal)
    correct_5hop = 0
    for i in range(NUM_FACTS - 4):
        current = entity_atoms[fact_entities[i]]
        true_end = fact_entities[i+5]
        for h in range(5):
            R = relation_atoms[fact_relations[i+h]]
            probe = M * (current * R)
            current, _, _ = cleanup(probe, entity_atoms)
        if torch.equal(current, entity_atoms[true_end]):
            correct_5hop += 1
    acc_5hop = correct_5hop / max(NUM_FACTS - 4, 1)
    _say(f"  5-hop (chain): cleanup = {acc_5hop*100:.1f}%")

    _say("\n========= MULTI-HOP V2 VERDICT =========")
    if acc_2hop >= 0.8 and acc_3hop >= 0.6:
        _say(f"  PASS: triple-binding + cleanup enables multi-hop reasoning.")
        _say(f"        2-hop {acc_2hop*100:.0f}%, 3-hop {acc_3hop*100:.0f}%, 5-hop {acc_5hop*100:.0f}%")
    elif acc_2hop >= 0.5:
        _say(f"  PARTIAL: 2-hop works at {acc_2hop*100:.0f}% but deeper chains degrade.")
    else:
        _say(f"  WEAK: even 2-hop fails. Need sparse codes or larger N.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e_multi_hop_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "NUM_ENTITIES": NUM_ENTITIES, "NUM_RELATIONS": NUM_RELATIONS,
        "NUM_FACTS": NUM_FACTS,
        "acc_1hop": acc_1hop, "acc_2hop": acc_2hop, "acc_3hop": acc_3hop, "acc_5hop": acc_5hop,
        "acc_2hop_no_cleanup": acc_2hop_no,
    }, indent=2))


if __name__ == "__main__":
    main()
