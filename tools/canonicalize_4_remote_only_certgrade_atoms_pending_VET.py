#!/usr/bin/env python3
"""Canonicalize the 4 cert-grade remote-only atoms per Skunkworks 37-VET ruling
2026-06-19.

The 4 atoms exist on the remote partition (preserved in backup) but NOT in
the canonical laptop Store -> would be silently lost on next behind-reset.

PER SKUNKWORKS RULING:
- Bring them in as RESEARCH_FINDING / cert-VET-PENDING (NOT CERT_CHAIN_GRADE).
- Skunkworks promotes verified to CERT_CHAIN_GRADE separately (via verdict-VET).
- Use the SAFE Atom-construction path (enum-MEMBER + to_dict + fresh-Store
  LOAD gate) -- NOT raw-JSONL-append (the path that caused the enum incident).

REFERENCE PATTERN (Exp-Dev's substrate_create_a2v6_grown_CERT_CHAIN_GRADE):
- Atom(...) with enum MEMBERS (Tier.* / AtomKind.* / Corpus.*)
- ps.add_atom(atom, source=..., note=...)
- Fresh PartitionedStore + get_atom read-back (Atom.from_dict round-trip gate)

SOURCE BACKUP:
- data/durability_backups/remote_math_atoms_preserve_20260619T1645Z.jsonl

THE 4 ATOMS:
- T3/EXP_b_alpha_broad_v2_denser_preview (MIDDLE_BAND)
- T3/EXP_b_alpha_broad_v3_2level (MIDDLE_BAND)
- T3/EXP_partof_broad_after (HARD_PASS)
- T3/EXP_partof_broad_before (MIDDLE_BAND)

A5-SAFE:
- Tier from backup atom's data (but coerced to enum-MEMBER).
- pq=RESEARCH_FINDING (cert-VET-PENDING; not CERT_CHAIN_GRADE).
- Per-atom add via ps.add_atom (idempotent: skip if already present).
- Post-add: fresh PartitionedStore + all_atoms() Store-LOAD gate.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

BACKUP_PATH = Path("data/durability_backups/remote_math_atoms_preserve_20260619T1645Z.jsonl")

TARGET_IDS = {
    "T3/EXP_b_alpha_broad_v2_denser_preview": {
        "expected_verdict": "MIDDLE_BAND",
    },
    "T3/EXP_b_alpha_broad_v3_2level": {
        "expected_verdict": "MIDDLE_BAND",
    },
    "T3/EXP_partof_broad_after": {
        "expected_verdict": "HARD_PASS",
    },
    "T3/EXP_partof_broad_before": {
        "expected_verdict": "MIDDLE_BAND",
    },
}


def load_target_atoms_from_backup():
    """Read backup JSONL, return target atoms as dicts."""
    if not BACKUP_PATH.exists():
        print(f"HALT: backup not found at {BACKUP_PATH}")
        return None
    found = {}
    with BACKUP_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
            except json.JSONDecodeError:
                continue
            aid = a.get("id")
            if aid in TARGET_IDS:
                found[aid] = a
    return found


def coerce_atom_from_backup(atom_dict):
    """Construct an Atom() from the backup dict using enum-MEMBER pattern.

    Per Skunkworks ruling: tier from backup (coerced); pq=RESEARCH_FINDING
    (cert-VET-PENDING; NOT CERT_CHAIN_GRADE -- Skunkworks promotes verified
    to CERT separately).
    """
    # Resolve enums from backup data
    backup_tier = atom_dict.get("tier")
    if backup_tier and isinstance(backup_tier, str):
        # Try value first (e.g. "T3"); fall back to NAME (e.g. "TIER_3_ALGORITHM")
        try:
            tier = Tier(backup_tier)
        except ValueError:
            tier = Tier[backup_tier]
    else:
        tier = Tier.TIER_3_ALGORITHM  # default for T3/EXP_* atoms

    backup_kind = atom_dict.get("kind")
    if backup_kind and isinstance(backup_kind, str):
        try:
            kind = AtomKind(backup_kind)
        except ValueError:
            kind = AtomKind[backup_kind]
    else:
        kind = AtomKind.EXPERIMENT_RECORD

    backup_corpus = atom_dict.get("corpus")
    if backup_corpus and isinstance(backup_corpus, str):
        try:
            corpus = Corpus(backup_corpus)
        except ValueError:
            corpus = Corpus[backup_corpus]
    else:
        corpus = Corpus.MATH

    # Metadata: copy from backup but coerce pq to RESEARCH_FINDING (cert-VET-pending)
    backup_metadata = dict(atom_dict.get("metadata") or {})
    backup_metadata["provenance_quality"] = "RESEARCH_FINDING"
    backup_metadata["cert_vet_status"] = "pending_skunkworks_verdict_vet"
    backup_metadata["canonicalized_from_remote_only_backup"] = True
    backup_metadata["canonicalize_ts"] = "2026-06-19"
    backup_metadata["canonicalize_source"] = (
        "data/durability_backups/remote_math_atoms_preserve_20260619T1645Z.jsonl"
    )
    backup_metadata["canonicalize_per_ruling"] = (
        "skunkworks_37VET_2026-06-19_canonicalize_before_reset"
    )
    backup_metadata["original_remote_verdict"] = backup_metadata.get("verdict")

    return Atom(
        id=atom_dict["id"],
        name=atom_dict.get("name") or atom_dict["id"],
        description=atom_dict.get("description") or "",
        kind=kind,
        tier=tier,
        corpus=corpus,
        algebra=None,
        metadata=backup_metadata,
    )


def main():
    print("=" * 80)
    print("CANONICALIZE 4 cert-grade remote-only atoms (cert-VET-PENDING)")
    print("Per Skunkworks 37-VET ruling 2026-06-19")
    print("=" * 80)
    print()

    target_atoms = load_target_atoms_from_backup()
    if target_atoms is None:
        return 1

    print(f"Found {len(target_atoms)} of {len(TARGET_IDS)} target atoms in backup:")
    for aid in target_atoms:
        print(f"  {aid}")
    print()
    missing = set(TARGET_IDS.keys()) - set(target_atoms.keys())
    if missing:
        print(f"MISSING from backup: {missing}")
        print("HALT: cannot proceed without all 4 source atoms.")
        return 1

    # Pre-state via PartitionedStore (the Atom.from_dict round-trip Store-LOAD)
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = list(ps.all_atoms())
    pre_count = len(pre_atoms)
    print(f"PRE-LOAD state: {pre_count} atoms in Store")
    print()

    # Pre-check: are any already present (idempotent)?
    pre_qids = {f"{a.corpus.value}::{a.id}" for a in pre_atoms}
    pre_ids_in_partition = {a.id for a in pre_atoms}
    print("Pre-check (idempotent):")
    for aid in TARGET_IDS:
        is_present = aid in pre_ids_in_partition
        print(f"  {aid:60s} present={is_present}")
    print()

    # Add each via the safe Atom-construction + ps.add_atom path
    added = []
    skipped = []
    for aid, backup_atom in target_atoms.items():
        if aid in pre_ids_in_partition:
            print(f"SKIP (idempotent): {aid}")
            skipped.append(aid)
            continue
        atom = coerce_atom_from_backup(backup_atom)
        print(f"ADDING: {aid}")
        print(f"  kind: {atom.kind.value}")
        print(f"  tier: {atom.tier.value}")
        print(f"  pq: {atom.metadata.get('provenance_quality')}")
        print(f"  cert_vet_status: {atom.metadata.get('cert_vet_status')}")
        ps.add_atom(
            atom,
            source="skunkworks_37VET_canonicalize_before_reset",
            note=(
                "Cert-VET-PENDING; canonicalized from preserved remote-only "
                "backup; Skunkworks's verdict-VET promotes verified to "
                "CERT_CHAIN_GRADE."
            ),
        )
        added.append(aid)
    print()

    # Post Store-LOAD verify (inst-240's rule + Exp-Dev's gate pattern)
    print("=" * 80)
    print("STORE-LOAD verify (fresh PartitionedStore + all_atoms() round-trip)")
    print("=" * 80)
    ps2 = PartitionedStore(Path("data/substrate_index"))
    post_atoms = list(ps2.all_atoms())
    post_count = len(post_atoms)
    print(f"POST-LOAD state: {post_count} atoms (expected {pre_count} + {len(added)})")

    # Per-atom read-back verification
    print()
    print("Per-atom read-back (Atom.from_dict round-trip):")
    rb_ok_count = 0
    for aid in added:
        # find the post atom
        rb = next((a for a in post_atoms if a.id == aid), None)
        if rb is None:
            print(f"  FAIL: {aid} -- not found post-add")
            continue
        md = rb.metadata or {}
        ok = (
            rb.kind == AtomKind.EXPERIMENT_RECORD
            and rb.algebra is None
            and md.get("provenance_quality") == "RESEARCH_FINDING"
            and md.get("cert_vet_status") == "pending_skunkworks_verdict_vet"
            and md.get("canonicalized_from_remote_only_backup") is True
        )
        status = "OK" if ok else "FAIL"
        print(f"  {status}: {aid[:55]:55s}  tier={rb.tier.value}  pq={md.get('provenance_quality')}")
        if ok:
            rb_ok_count += 1

    print()
    print(f"Added: {len(added)} / Skipped: {len(skipped)} / Read-back OK: {rb_ok_count}")
    print(f"Post-count check: {post_count} == {pre_count} + {len(added)}?  "
          f"{'OK' if post_count == pre_count + len(added) else 'FAIL'}")

    if rb_ok_count != len(added):
        print()
        print("FAIL: some atoms didn't round-trip cleanly. Reverting may be needed.")
        return 2

    print()
    print("=" * 80)
    print("CANONICALIZE COMPLETE.")
    print("Atoms in Store as RESEARCH_FINDING / cert-VET-PENDING.")
    print("Route to Skunkworks for per-atom verdict-VET -> CERT-promote.")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
