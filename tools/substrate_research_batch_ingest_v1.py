"""Generic Research BATCH yaml extractor + ingester.

Parses ```yaml ... ``` blocks from Research routing notes and ingests atoms +
DEPENDS_ON edges into substrate. Reusable across all future BATCH N routing notes
(BATCH 17 / 26 pattern); avoids transcribing 12+ atoms per batch.

Routing note yaml format (per Research's BATCH N convention):
```yaml
- canonical_name: <name>
  aliases: [<list>]   # optional
  tier: T1|T2|T3
  partition: <string>
  science_algebra_category: <string>
  algebra_dict: { ... }   # multi-line indented dict
  depends_on: [<list>]    # optional
  serves_capability: [<list>]
  signature_hint: <string>
```

Notes:
  - Uses minimal yaml subset; relies on `yaml.safe_load_all` if PyYAML present,
    else falls back to a simplified regex-based parser for the indented block.
  - Tolerant of missing DEPENDS_ON targets (BATCH 17 pattern).
  - DEPENDS_ON target names in spec are bare; converted to math::T<tier>/<name>
    via heuristic + tier inference from the depends-target's name when known.

Usage:
  python tools/substrate_research_batch_ingest_v1.py notes/research_to_testbed_T1_T2_BATCH_19_*.md
  python tools/substrate_research_batch_ingest_v1.py --dry-run notes/research_to_testbed_T1_T2_BATCH_22_*.md
  python tools/substrate_research_batch_ingest_v1.py --batches notes/research_to_testbed_T1_T2_BATCH_*.md

NO LLM. NO bge. Pure parsing + graph authoring.
"""
from __future__ import annotations
import sys
import re
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


YAML_BLOCK_PATTERN = re.compile(r"```yaml\s*\n(.*?)```", re.DOTALL)


def parse_yaml_atoms(yaml_text: str) -> list:
    """Parse Research BATCH yaml format into list of atom dicts."""
    try:
        import yaml
        # Try yaml.safe_load_all for documents; else treat the whole block as one list-of-dicts doc
        docs = list(yaml.safe_load_all(yaml_text))
        if docs and docs[0] is not None:
            if isinstance(docs[0], list):
                return docs[0]
            if isinstance(docs[0], dict):
                return [docs[0]]
    except ImportError:
        pass
    except Exception as e:
        print(f"  yaml.safe_load failed: {e}; falling back to regex parser")

    # Regex fallback for minimal yaml (works for Research's BATCH format)
    atoms = []
    current = None
    current_dict_field = None
    dict_indent = None
    for line_no, raw in enumerate(yaml_text.split("\n"), 1):
        if not raw.strip():
            continue
        # Top-level item starts with `- canonical_name:`
        m = re.match(r"^- canonical_name:\s*(.+?)\s*$", raw)
        if m:
            if current is not None:
                atoms.append(current)
            current = {"canonical_name": m.group(1).strip()}
            current_dict_field = None
            continue
        if current is None:
            continue
        # algebra_dict block (multi-line nested dict; we capture as opaque string)
        m = re.match(r"^  algebra_dict:\s*$", raw)
        if m:
            current_dict_field = "algebra_dict"
            current[current_dict_field] = {}
            dict_indent = 4
            continue
        if current_dict_field == "algebra_dict" and re.match(r"^    \S", raw):
            # 4-space indented child of algebra_dict
            mm = re.match(r"^    (\w+):\s*(.+?)\s*$", raw)
            if mm:
                v = mm.group(2)
                # try to parse list-form values [a, b, c]
                if v.startswith("[") and v.endswith("]"):
                    v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
                current["algebra_dict"][mm.group(1)] = v
                continue
        elif not raw.startswith("    "):
            current_dict_field = None
        # Simple key: value or key: [list]
        m = re.match(r"^  (\w+):\s*(.+?)\s*$", raw)
        if m:
            key, val = m.group(1), m.group(2)
            if val.startswith("[") and val.endswith("]"):
                val = [x.strip() for x in val[1:-1].split(",") if x.strip()]
            current[key] = val
            continue
    if current is not None:
        atoms.append(current)
    return atoms


def extract_yaml_block(md_path: Path) -> str | None:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    m = YAML_BLOCK_PATTERN.search(text)
    return m.group(1) if m else None


def normalize_tier(tier_val) -> Tier:
    if tier_val is None:
        return Tier.TIER_3_ALGORITHM
    s = str(tier_val).strip().upper()
    return {
        "T0": Tier.TIER_1_FOUNDATIONAL,  # T0 axiom collapsed to T1 in this schema
        "T1": Tier.TIER_1_FOUNDATIONAL,
        "T2": Tier.TIER_2_PRIMITIVE,
        "T3": Tier.TIER_3_ALGORITHM,
        "T4": Tier.TIER_4_COMPOSED,
    }.get(s, Tier.TIER_3_ALGORITHM)


def infer_id(canonical_name: str, tier: Tier) -> str:
    """Build atom id: T<n>/<canonical_name>."""
    tier_prefix = {
        Tier.TIER_1_FOUNDATIONAL: "T1",
        Tier.TIER_2_PRIMITIVE: "T2",
        Tier.TIER_3_ALGORITHM: "T3",
        Tier.TIER_4_COMPOSED: "T4",
    }.get(tier, "T3")
    return f"{tier_prefix}/{canonical_name}"


def resolve_dep_qid(dep_name: str, ps: PartitionedStore) -> str | None:
    """Try to find a target qualified id for a bare dependency name."""
    # Already qualified
    if "::" in dep_name:
        return dep_name if ps.has_atom(dep_name) else None
    # Try tier prefixes + corpus prefixes
    for tier in ("T1", "T2", "T3", "T0"):
        for corpus in ("math", "concept", "science", "school", "meta"):
            qid = f"{corpus}::{tier}/{dep_name}"
            if ps.has_atom(qid):
                return qid
    # Try just corpus prefix (no tier)
    for corpus in ("math", "concept", "science", "school", "meta"):
        qid = f"{corpus}::{dep_name}"
        if ps.has_atom(qid):
            return qid
    return None


def humanize(name: str) -> str:
    return name.replace("_", " ").title()[:120]


def ingest_atoms(atom_specs: list, ps: PartitionedStore, batch_label: str) -> dict:
    created = 0
    skipped_exists = 0
    failed = 0
    created_qids = []

    for spec in atom_specs:
        cn = spec.get("canonical_name")
        if not cn:
            continue
        tier = normalize_tier(spec.get("tier"))
        atom_id = infer_id(cn, tier)
        qid = f"math::{atom_id}"

        if ps.has_atom(qid):
            skipped_exists += 1
            continue

        # Build description from algebra_dict
        alg = spec.get("algebra_dict") or {}
        description = (
            alg.get("formula") or alg.get("definition") or alg.get("statement")
            or alg.get("role") or humanize(cn)
        )
        if isinstance(description, list):
            description = "; ".join(str(x) for x in description)

        aliases = spec.get("aliases") or ()
        if isinstance(aliases, str):
            aliases = (aliases,)
        else:
            aliases = tuple(aliases)

        metadata = {
            "science_algebra_category": spec.get("science_algebra_category"),
            "signature_hint": spec.get("signature_hint"),
            "is_axiom": alg.get("is_axiom", False) if isinstance(alg, dict) else False,
            "batch_origin": batch_label,
        }
        # Include any extra algebra_dict properties in metadata
        if isinstance(alg, dict):
            for k, v in alg.items():
                if k not in ("formula", "definition", "statement", "role", "is_axiom"):
                    metadata.setdefault(f"alg_{k}", v)

        serves = spec.get("serves_capability") or ()
        if isinstance(serves, str):
            serves = (serves,)
        else:
            serves = tuple(serves)

        try:
            atom = Atom(
                id=atom_id, name=humanize(cn), corpus=Corpus.MATH, tier=tier,
                description=str(description)[:500], kind=AtomKind.PRIMITIVE,
                aliases=aliases, metadata=metadata, serves_capability=serves,
            )
            ps.add_atom(atom, source=batch_label,
                        note=f"BATCH ingest via substrate_research_batch_ingest_v1.py")
            created += 1
            created_qids.append(qid)
            print(f"  ATOM CREATED: {qid}")
        except Exception as e:
            print(f"  ATOM FAIL: {qid}: {str(e)[:120]}")
            failed += 1

    return {"created": created, "skipped_exists": skipped_exists, "failed": failed,
            "created_qids": created_qids}


def ingest_edges(atom_specs: list, ps: PartitionedStore, batch_label: str) -> dict:
    existing = set()
    for r in ps.iter_all_relations():
        try:
            existing.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    added = 0
    skipped_miss_tgt = 0
    skipped_dup = 0
    failed = 0

    for spec in atom_specs:
        cn = spec.get("canonical_name")
        if not cn:
            continue
        tier = normalize_tier(spec.get("tier"))
        src_qid = f"math::{infer_id(cn, tier)}"
        if not ps.has_atom(src_qid):
            continue
        deps = spec.get("depends_on") or ()
        if isinstance(deps, str):
            deps = (deps,)
        for dep_name in deps:
            tgt_qid = resolve_dep_qid(dep_name, ps)
            if tgt_qid is None:
                print(f"  EDGE SKIP_MISS_TGT: {src_qid} -> {dep_name!r} (unresolved)")
                skipped_miss_tgt += 1
                continue
            key = (src_qid, "DEPENDS_ON", tgt_qid)
            if key in existing:
                skipped_dup += 1
                continue
            try:
                ps.add_relation(src_qid, RelationType.DEPENDS_ON, tgt_qid,
                                source=batch_label,
                                note=f"BATCH DEPENDS_ON via substrate_research_batch_ingest_v1.py")
                added += 1
                existing.add(key)
            except Exception as e:
                msg = str(e)[:120]
                if any(k in msg.lower() for k in ("already", "duplicate")):
                    skipped_dup += 1
                else:
                    print(f"  EDGE FAIL: {src_qid} -> {tgt_qid}: {msg}")
                    failed += 1

    return {"added": added, "skipped_miss_tgt": skipped_miss_tgt,
            "skipped_dup": skipped_dup, "failed": failed}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("notes", nargs="+", help="Path(s) to BATCH routing notes")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    overall = {"atoms_created": 0, "atoms_failed": 0, "edges_added": 0, "edges_failed": 0}
    for note_path in args.notes:
        path = Path(note_path)
        if not path.exists():
            print(f"SKIP missing: {note_path}")
            continue
        # Extract batch label from filename (BATCH_NN)
        m = re.search(r"BATCH_(\d+)", path.name)
        batch_label = f"BATCH_{m.group(1)}" if m else path.stem[:40]
        print(f"\n=== {batch_label} ({path.name}) ===")

        yaml_text = extract_yaml_block(path)
        if yaml_text is None:
            print(f"  no yaml block found; skipping")
            continue
        atom_specs = parse_yaml_atoms(yaml_text)
        print(f"  parsed {len(atom_specs)} atom specs")
        if not atom_specs:
            print(f"  no atoms parsed; skipping")
            continue
        if args.dry_run:
            for s in atom_specs[:3]:
                print(f"    sample: {s.get('canonical_name')!r} tier={s.get('tier')} "
                      f"deps={s.get('depends_on')}")
            continue

        atom_result = ingest_atoms(atom_specs, ps, batch_label)
        overall["atoms_created"] += atom_result["created"]
        overall["atoms_failed"] += atom_result["failed"]
        print(f"  atoms: created={atom_result['created']} "
              f"skipped_exists={atom_result['skipped_exists']} failed={atom_result['failed']}")

        edge_result = ingest_edges(atom_specs, ps, batch_label)
        overall["edges_added"] += edge_result["added"]
        overall["edges_failed"] += edge_result["failed"]
        print(f"  edges: added={edge_result['added']} "
              f"skipped_miss_tgt={edge_result['skipped_miss_tgt']} "
              f"skipped_dup={edge_result['skipped_dup']} failed={edge_result['failed']}")

    if args.dry_run:
        return
    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== UNIFIED INGEST SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  atoms created: {overall['atoms_created']}; failed: {overall['atoms_failed']}")
    print(f"  edges added: {overall['edges_added']}; failed: {overall['edges_failed']}")


if __name__ == "__main__":
    main()
