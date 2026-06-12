"""Dedup batch 2 T2/* atoms vs existing T3+ atoms by canonical name.

Per Research ACK research_to_testbed_BATCH_2_NAMESPACE_DUPLICATION_*.md:
- For each batch 2 T2 atom: check if same canonical_name exists at T3/T4
- If yes: MERGE aliases + algebra into the existing T3+ atom, REMOVE the T2 version
- If no: keep T2 as genuinely new

Per [[substrate-vsa-position-is-meaning-validated-2026-06-12]] + rule 12 CONFIRMED:
duplication breaks UNION because both candidates compete for same gold slot.

Local-allowed (no encoder load).
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("dedup_batch2")

DATA_ROOT = Path("data/substrate_index")


def name_key(s: str) -> str:
    """Normalize an atom name/id-tail for matching across tiers."""
    return s.lower().replace("-", "_").replace(" ", "_").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("backfill_jsonl", type=Path)
    ap.add_argument("--apply", action="store_true",
                    help="Actually merge+remove; default is dry-run")
    args = ap.parse_args()

    pstore = PartitionedStore(DATA_ROOT)
    all_atoms = pstore.all_atoms()
    log.info("pre-dedup: %d atoms total", len(all_atoms))

    # Build index of canonical_name -> existing atom (excluding T2 batch 2 themselves)
    canonical_index: dict[str, list[Atom]] = {}
    for a in all_atoms:
        # Skip batch 2 source (we'll match against everything else)
        if a.id.startswith("T2/") and "batch2" in (str(a) if False else ""):
            continue
        # Use atom name as canonical key
        keys = {name_key(a.name)}
        # Also key by last id segment
        last = a.id.split("/")[-1] if "/" in a.id else a.id
        keys.add(name_key(last))
        # Add aliases as additional matching keys
        for al in (a.aliases or []):
            keys.add(name_key(al))
        for k in keys:
            canonical_index.setdefault(k, []).append(a)

    # Process batch 2
    merges = []
    keeps = []
    with open(args.backfill_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            qid = rec["atom_id"]
            new_aliases = rec.get("aliases_add", []) or []
            algebra_add = rec.get("algebra_additions", {}) or {}

            # T2/q_learning -> "q_learning"
            local_id = qid.split("::", 1)[1] if "::" in qid else qid
            last = local_id.split("/")[-1] if "/" in local_id else local_id
            key = name_key(last)

            # Find candidate existing matches at T3/T4 NOT in T2 tier
            candidates = canonical_index.get(key, [])
            existing_non_t2 = [a for a in candidates if not a.id.startswith("T2/") or a.id == local_id]
            existing_higher = [a for a in candidates
                                if a.id.startswith(("T3/", "T4/"))
                                or a.tier.value in ("T3", "T4")]

            if existing_higher and pstore.has_atom(qid):
                # Found a higher-tier match AND the T2 duplicate exists -- dedup
                target = existing_higher[0]
                target_qid = f"{target.corpus.value}::{target.id}"
                merges.append((qid, target_qid, new_aliases, algebra_add))
            else:
                keeps.append(qid)

    log.info("dedup plan: %d merges (T2 -> existing T3+) + %d keeps", len(merges), len(keeps))
    for t2_qid, target_qid, _, _ in merges[:20]:
        log.info("  MERGE %s -> %s", t2_qid, target_qid)
    if not merges[20:]:
        pass
    else:
        log.info("  ... and %d more", len(merges) - 20)
    for k in keeps[:10]:
        log.info("  KEEP %s", k)

    if not args.apply:
        print(f"\nDRY-RUN: {len(merges)} merges + {len(keeps)} keeps. Re-run with --apply to commit.")
        return

    # Apply merges: extend target's aliases + algebra, then remove T2 duplicate
    for t2_qid, target_qid, new_aliases, algebra_add in merges:
        if not pstore.has_atom(target_qid):
            log.warning("target gone: %s", target_qid)
            continue
        target = pstore.get_atom(target_qid)
        merged_aliases = list(dict.fromkeys(list(target.aliases or []) + new_aliases))
        merged_algebra = dict(target.algebra or {})
        merged_algebra.update(algebra_add)
        new_target = Atom(
            id=target.id, name=target.name, corpus=target.corpus, tier=target.tier,
            description=target.description, kind=target.kind, aliases=merged_aliases,
            metadata=target.metadata, algebra=merged_algebra,
            signature=target.signature, complexity=target.complexity,
            equivalences=target.equivalences, concept_links=target.concept_links,
            current_best_solution=target.current_best_solution,
            solution_history=target.solution_history,
            serves_capability=target.serves_capability,
        )
        pstore.add_atom(new_target, source="batch2_dedup_merge",
                        note=f"merged from {t2_qid}: +{len(new_aliases)} aliases +{len(algebra_add)} algebra")
        # Remove the T2 duplicate
        ok = pstore.remove_atom(t2_qid, source="batch2_dedup_remove",
                                 note=f"duplicate of {target_qid}; merged into target")
        if not ok:
            log.warning("remove failed: %s", t2_qid)

    log.info("post-dedup: %d atoms total", len(pstore.all_atoms()))
    print(f"\nAPPLIED: {len(merges)} merges + {len(keeps)} keeps")


if __name__ == "__main__":
    main()
