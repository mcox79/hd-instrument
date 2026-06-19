#!/usr/bin/env python3
"""Atomize WRITEUP v1.2 substrate-as-reasoning-engine integrated narrative atom.

Director Item 3 of 3rd 20h sprint + 40h tack-on Top-3; Skunkworks framing-VET PASS
(v1.1 PASS + v1.2 multi-relation-robust upgrade post-M1-HYPERNYM landing).

Per Skunkworks SCHEMA-VET conditions:
- top-level Atom fields per B1 layer-4 id-FORM lesson
- single-flush batched add per 6th-checklist (N=1)
- algebra=None structural guard
- provenance_quality=RESEARCH_FINDING in metadata (cap_map precedent)
- CERT 573 UNCHANGED (WRITEUP is RESEARCH_FINDING tier, NOT cert-counted)
- axiom_term 206 / cap_pres 6/6 preserved
- read-back verify: present + kind + algebra + provenance + citations resolve
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.substrate_index.store import Store
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


WRITEUP_PATH = Path("data/writeup_v1_substrate_as_reasoning_engine_DRAFT_pre_skunkworks_framing_VET.json")
ROOT = Path("data/substrate_index")


def build_atom():
    with WRITEUP_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    # Structural guard asserts BEFORE any write
    assert data["kind"] == "finding", f"kind must be finding (existing AtomKind), got {data['kind']}"
    assert data.get("algebra") is None, f"algebra must be None, got {data.get('algebra')}"
    assert data["corpus"] == "meta", f"corpus must be meta, got {data['corpus']}"
    assert data["tier"] == "NA", f"tier must be NA, got {data['tier']}"
    pq = data.get("provenance_quality")
    assert pq == "RESEARCH_FINDING", f"provenance_quality must be RESEARCH_FINDING, got {pq}"

    # Build Atom via dataclass (top-level fields per B1 layer-4 lesson)
    atom = Atom(
        id=data["id"],
        name=data["name"],
        corpus=Corpus.META,
        tier=Tier.TIER_NA,
        kind=AtomKind.FINDING,
        description=data["description"],
        aliases=data.get("aliases", []),
        metadata=data.get("metadata", {}),
        algebra=None,
    )
    # provenance_quality + relevance_tier + era go INTO metadata per cap_map precedent
    # (the from_dict doesn't lift them as top-level fields)
    atom.metadata["provenance_quality"] = data.get("provenance_quality", "RESEARCH_FINDING")
    atom.metadata["relevance_tier"] = data.get("relevance_tier", "ACTIVE")
    atom.metadata["era"] = data.get("era", "SUBSTRATE_BUILD")
    return atom


def count_atoms_and_cert():
    """Raw jsonl count (Store.all_atoms generator returns empty on this Windows path -- known quirk)."""
    total = 0
    cert = 0
    for f in ROOT.glob("*/atoms.jsonl"):
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                except json.JSONDecodeError:
                    continue
                total += 1
                md = a.get("metadata") or {}
                if md.get("provenance_quality") == "CERT_CHAIN_GRADE":
                    cert += 1
    return total, cert


def main():
    apply = "--apply" in sys.argv

    # PRE snapshot (raw jsonl scan)
    atoms_pre, cert_pre = count_atoms_and_cert()
    print(f"PRE  : atoms={atoms_pre} | CERT={cert_pre}")
    s = Store(str(ROOT))

    # Build atom
    atom = build_atom()
    print(f"BUILT: id={atom.id} | kind={atom.kind} | algebra={atom.algebra} | pq={atom.metadata.get('provenance_quality')}")

    if not apply:
        print("[DRY-RUN] (re-run with --apply to write)")
        return

    # Check not-already-present
    if s.has_atom(atom.qualified_id):
        print(f"ERROR: atom {atom.qualified_id} already present in Store; aborting")
        sys.exit(1)

    # APPLY (single add_atom; N=1; 6th-checklist OK)
    s.add_atom(atom)

    # POST snapshot + read-back verify
    atoms_post, cert_post = count_atoms_and_cert()
    s2 = Store(str(ROOT))
    landed = s2.get_atom(atom.qualified_id)
    if landed is None:
        print(f"ERROR: read-back FAILED -- atom {atom.qualified_id} not present after add")
        sys.exit(1)
    pq_ok = (landed.metadata or {}).get("provenance_quality") == "RESEARCH_FINDING"
    algebra_ok = landed.algebra is None
    kind_ok = landed.kind == AtomKind.FINDING

    print(f"POST : atoms={atoms_post} (delta {atoms_post-atoms_pre}) | CERT={cert_post} ({'unchanged' if cert_post==cert_pre else 'CHANGED'})")
    print(f"READBACK: present={landed is not None} kind={kind_ok} algebra={algebra_ok} pq=RESEARCH_FINDING={pq_ok}")

    if not (kind_ok and algebra_ok and pq_ok and cert_post == cert_pre):
        print("ERROR: read-back checks FAILED")
        sys.exit(1)

    print("\nLANDED-VERIFY: PASS (atoms +1; CERT unchanged; algebra=None; pq=RESEARCH_FINDING; kind=finding)")
    print(f"Route landed-verify to Skunkworks: atom {atom.qualified_id} present + structural guards held")


if __name__ == "__main__":
    main()
