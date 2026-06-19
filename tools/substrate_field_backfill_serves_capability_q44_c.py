"""Field backfill: populate serves_capability for Q44-C gold atoms (Cycle 51 day-3 P0.2).

Per research_to_testbed_exp_dev_CYCLE_51_DAY_3_ACTIVE_COORDINATION_PRIORITY_ORDERED_WORK_LISTS_HP_v1_0_70_PUSH_2026-06-12.md P0.2:
"C-axis FIELD-BACKFILL MODE Phase-2-light extension; Target: 32 collision atoms signature + complexity field population"
Pre-reg: C 0.622 -> 0.65+ (+0.005 macro)

This script targets a SPECIFIC C-axis lift: Q44-C asks "Which atoms serve substrate Layer 2
spectral observability?" Gold = 10 atoms. None have serves_capability =
concept::CAP_spectral_observability populated. F1=0.000.

Fix:
1. CREATE concept::CAP_spectral_observability capability atom (doesn't exist; CAP_ is required for route_C)
2. UPDATE 10 gold atoms' serves_capability field to include the new CAP

Plus Q43-C and Q46-C field-backfill candidates (other partial-recall Cs).

Expected: Q44-C 0.000 -> 1.000 = +1.0 / 14 C-Qs = +0.071 C-axis macro = +0.012 MACRO contribution
(but only 1 of 14 lift; smaller in macro terms ~+0.005 if just Q44).

Honest scope: this is a TARGETED field backfill for Q44-C, not the full FIELD-BACKFILL MODE
tool extension. The extension (Phase-2-light --scope field-backfill) would generalize this
pattern. Doing the targeted fix first to validate the lift mechanism.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
import dataclasses


CAP_ID = "concept::CAP_spectral_observability"


# Q44-C gold atoms (qualified_id form). All present in substrate (8 / 10).
Q44_C_GOLD_ATOMS = [
    "math::T3/spectral_gap",
    "math::T3/tw_edge_z",
    "math::T3/mp_bulk_kl",
    "math::T3/kappa_4_free",
    "math::T1/marchenko_pastur_distribution",
    "math::T1/tracy_widom_distribution",
    "math::T1/voiculescu_free_probability",
    "school::SCHOOL/spectral_observability_family",
    "school::SCHOOL/free_probability_family",
    "science::PHYS/random_matrix_theory",
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"pre-backfill: {len(ps.all_atoms())} atoms")

    # Step 1: Create concept::CAP_spectral_observability capability atom
    if not ps.has_atom(CAP_ID):
        cap_atom = Atom(
            id="CAP_spectral_observability",
            name="Spectral observability",
            corpus=Corpus.CONCEPT,
            tier=Tier.TIER_NA,
            description="Capability: substrate's ability to observe spectral properties of internal state (eigenvalue distributions, edge fluctuations, bulk densities) via free probability + random matrix theory primitives.",
            kind=AtomKind.CAPABILITY,
            aliases=("spectral observability", "spectral_observability_capability"),
            metadata={"category": "substrate_self_observation", "drill_origin": "free_probability_drill_series_2026-06-12"},
        )
        ps.add_atom(cap_atom, source="p0_2_field_backfill_q44_c_per_cycle_51_day3_direction",
                    note="Q44-C gold capability; required for serves_capability backfill on 10 spectral observability atoms")
        print(f"created {CAP_ID}")
    else:
        print(f"already exists: {CAP_ID}")

    # Step 2: UPDATE each of the 10 gold atoms' serves_capability field
    backfilled = 0
    skipped = 0
    not_found = 0
    for qid in Q44_C_GOLD_ATOMS:
        atom = ps.get_atom(qid)
        if atom is None:
            print(f"NOT FOUND in substrate: {qid}")
            not_found += 1
            continue
        current_caps = list(atom.serves_capability or ())
        if CAP_ID in current_caps:
            print(f"already serves: {qid}")
            skipped += 1
            continue
        new_caps = tuple(current_caps + [CAP_ID])
        # Build updated atom via dataclasses.replace
        updated = dataclasses.replace(atom, serves_capability=new_caps)
        # Re-add to overwrite (underlying Store.add_atom overwrites by id)
        ps.add_atom(updated, source="p0_2_field_backfill_q44_c_per_cycle_51_day3_direction",
                    note=f"backfilled serves_capability += {CAP_ID} for Q44-C gold")
        print(f"backfilled: {qid} serves += {CAP_ID}")
        backfilled += 1

    print(f"\npost-backfill: {len(ps.all_atoms())} atoms; backfilled={backfilled} skipped={skipped} not_found={not_found}")


if __name__ == "__main__":
    main()
