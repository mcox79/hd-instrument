#!/usr/bin/env python3
"""Quarantine 3 corrupt rows in data/substrate_index/meta/atoms.jsonl that use
the deprecated raw-JSONL 'atom_id' schema instead of Atom-construction 'id'.

DISCOVERED during Wave-1 SMOKE_HF verify-off-data audit (2026-06-27). The
Store fresh-LOAD round-trip pre-write check (the inst-240 gate) caught
KeyError 'id' on first PartitionedStore() construction -- meaning the Store
has been UNLOADABLE since these 3 lines landed today (2026-06-27T22:30:00Z),
which means EVERY subsequent A5-gated write would have failed too. This is
exactly the inst-239/240 corruption-incident family.

Bad rows (line numbers in atoms.jsonl):
  206  META_FINDING_hopfield_consolidation_family_honest_neg_at_substrate_regime_v1
  207  META_RULE_CANDIDATE_by_construction_arm_equivalence_under_l2_normalized_readout_v1
  208  META_RULE_CANDIDATE_n1_fair_diagnostic_can_close_family_if_discriminator_structural_v1

All 3 written by `skunkworks_landed_vet_2026-06-27` (timestamp 22:30:00Z) using
raw-JSONL append with the WRONG SCHEMA (atom_id/atom_type instead of id/name/
description/kind/tier/corpus enum members + metadata.provenance_quality). Same
inst-239/240 anti-pattern that the SAFE-template was designed to prevent.

REPAIR STRATEGY (safest; per inst-240 lesson):
- DO NOT attempt to in-place rewrite the bad rows. Re-author through
  Atom-construction is the only safe path, and the original author should
  do that (they have full context for description/composes_with).
- DO atomic-rewrite atoms.jsonl WITHOUT the 3 bad rows; preserve the rows in a
  .quarantine file alongside for the original author to re-author through
  add_audit_lesson_safely().
- Atomic via tmp + os.replace (per layer-1 protection).
- Post-write verify-LOAD via fresh PartitionedStore (per layer-2 gate).

NOTIFY: Director + the original author (skunkworks_landed_vet batch 2026-06-27)
that they need to re-atomize the 3 META findings/rules through the SAFE
template.
"""
from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path("d:/AI/hd-instrument").resolve()))

META_DIR = Path("d:/AI/hd-instrument/data/substrate_index/meta")
ATOMS_PATH = META_DIR / "atoms.jsonl"
QUARANTINE_PATH = META_DIR / f"atoms.jsonl.quarantine_bad_schema_2026-06-27_{int(time.time())}"


def main() -> int:
    if "--apply" not in sys.argv and "--dry-run" not in sys.argv:
        print(__doc__)
        print("Use --dry-run to preview, --apply to repair.")
        return 1

    good_lines = []
    bad_lines = []

    with open(ATOMS_PATH, encoding="utf-8") as f:
        for i, ln in enumerate(f, 1):
            raw = ln.rstrip("\n")
            if not raw.strip():
                continue
            try:
                d = json.loads(raw)
            except Exception as e:
                bad_lines.append((i, "parse_error: " + str(e), raw))
                continue
            if "id" not in d:
                bad_lines.append((i, "missing_id_uses_" + ("atom_id" if "atom_id" in d else "unknown"), raw))
            else:
                good_lines.append(raw)

    print(f"Total rows: {len(good_lines) + len(bad_lines)}")
    print(f"Good rows: {len(good_lines)}")
    print(f"Bad rows: {len(bad_lines)}")
    for i, reason, raw in bad_lines:
        print(f"  bad line {i} [{reason}]: {raw[:130]}")

    if not bad_lines:
        print("No bad rows; nothing to quarantine.")
        return 0

    if "--dry-run" in sys.argv:
        print(f"\nDRY: would quarantine {len(bad_lines)} bad rows to {QUARANTINE_PATH}")
        print(f"DRY: would rewrite atoms.jsonl with {len(good_lines)} good rows via tmp+os.replace")
        return 0

    # Write quarantine file first (no loss; preserve the content for re-authoring)
    QUARANTINE_PATH.write_text(
        "\n".join(raw for _, _, raw in bad_lines) + "\n",
        encoding="utf-8",
    )
    print(f"WROTE quarantine: {QUARANTINE_PATH} ({QUARANTINE_PATH.stat().st_size} bytes)")

    # Atomic rewrite of atoms.jsonl with good rows only
    pid = os.getpid()
    monotonic = int(time.monotonic_ns())
    tmp = ATOMS_PATH.with_suffix(f".jsonl.tmp_repair_{pid}_{monotonic}")
    tmp.write_text("\n".join(good_lines) + "\n", encoding="utf-8")
    print(f"WROTE tmp: {tmp} ({tmp.stat().st_size} bytes)")
    os.replace(str(tmp), str(ATOMS_PATH))
    print(f"REPLACED: atoms.jsonl now has {len(good_lines)} rows")

    # Layer-2 gate: fresh-Store LOAD must succeed
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(Path("d:/AI/hd-instrument/data/substrate_index"))
    atoms = list(ps.all_atoms())
    print(f"VERIFY: fresh Store loaded {len(atoms)} total atoms across all partitions")
    print("PASS: Store now loadable. Original 3 bad rows preserved in quarantine for re-authoring.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
