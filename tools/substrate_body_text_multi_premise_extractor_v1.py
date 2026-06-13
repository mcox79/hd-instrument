"""Body-text multi-premise DEPENDS_ON extractor v1.

Per Research A1 MPM DECISIVE verdict (commit cda08bb9 + 6b8aa294 + 2e5143f0):
12 hand-verified T3 atoms; mean extracted DEPENDS_ON = 0.0; mean gold = 2.9.
Atom BODIES literally describe multi-premise structure but the extractor
captures NONE. PARSER-FIDELITY GAP at decisive scale; parser-v2 is the lever
to depth-7+ trajectory.

Concrete examples of body-text descriptions Research surfaced:
  "Foundation for vector_space"  -> DEPENDS_ON vector_space
  "DP for sequence_alignment under HMM"  -> DP + sequence_alignment + HMM
  "approximation to newton_method"  -> newton_method
  "via convolution_theorem"  -> convolution_theorem

This v1 builds a SUBSTRATE-AWARE name+alias index across all atoms then scans
each atom's description + algebra_dict text + metadata for substring matches.
Matches authored as DEPENDS_ON edges if both atoms exist.

Heuristics to avoid false positives:
  - Match only canonical_names with underscores OR multi-word names (not "field")
  - Word-boundary regex match
  - Skip matches that map to atom's own qualified id
  - Skip cyclic edges (src == tgt after resolution)
  - Cap edges per atom at MAX_EDGES_PER_ATOM (50) to bound graph density
  - Exclude common substrate vocabulary leakage (atom + axioms + theorem)

Expected impact at 20820-atom scale:
  - Current avg premise count: 1.00 (per A5 PRECNT metric)
  - Target Mathlib baseline: >= 2.6
  - Target Mizar baseline: >= 5
  - Likely uplift: 1.00 -> 2-4 (depends on body-text density)
  - Combined with OEIS extractor (this session's `363236f2`): pushes toward 3+ baseline

NO LLM. NO bge. Pure regex + substring match. Tolerant of missing atoms.

Usage:
  python tools/substrate_body_text_multi_premise_extractor_v1.py --dry-run --limit 100
  python tools/substrate_body_text_multi_premise_extractor_v1.py [--no-canonical-name-only] [--limit N]
"""
from __future__ import annotations
import sys
import re
import argparse
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


# Stop-words: tokens that are too common to use as atom-match anchors.
STOP_INDEX_TERMS = {
    # common atom-name fragments that match almost anything
    "atom", "axiom", "axioms", "theorem", "lemma", "definition", "proof",
    "rule", "rules", "set", "value", "data", "number", "function", "operation",
    "type", "vector", "matrix", "tensor", "graph", "node", "edge", "tree",
    "node", "math", "concept", "field", "ring", "group", "category", "is_axiom",
    "true", "false", "none", "null", "name", "id", "tier",
    # english stop words
    "and", "the", "for", "with", "from", "into", "this", "that", "via",
    "between", "across", "such", "than", "then", "when", "where", "while",
}

MAX_EDGES_PER_ATOM = 50


def normalize_name_token(name: str) -> str:
    """Normalize an atom name for body-text matching: lowercase, underscores preserved."""
    return name.strip().lower()


def collect_text_to_scan(atom) -> str:
    """Aggregate body-text fields where multi-premise references appear."""
    parts = [atom.description or "", atom.name or ""]
    alg = atom.algebra or {}
    for k, v in alg.items():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                parts.append(str(item))
    meta = atom.metadata or {}
    for k, v in meta.items():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                parts.append(str(item))
    return " ".join(parts).lower()


def build_name_index(all_atoms, canonical_name_only: bool = True) -> dict:
    """Build {match_token: qualified_id} index for body-text matching.

    canonical_name_only: only index names/aliases with underscores OR multi-word
    (filters common short names like 'field' that match too aggressively)."""
    index = {}
    for atom in all_atoms:
        candidates = []
        # canonical name parts (atom id like T2/fhrr_bind -> "fhrr_bind")
        if "/" in atom.id:
            cn = atom.id.split("/", 1)[1]
        else:
            cn = atom.id
        candidates.append(cn)
        # aliases (may include free-form text)
        for alias in (atom.aliases or ()):
            candidates.append(alias)

        for c in candidates:
            tok = normalize_name_token(c)
            if not tok or tok in STOP_INDEX_TERMS:
                continue
            if canonical_name_only:
                # Require either underscore or multi-word (whitespace) OR length >= 8 letters
                if "_" not in tok and " " not in tok and len(tok) < 8:
                    continue
            # Don't overwrite if already indexed (first-seen wins; arbitrary)
            if tok not in index:
                index[tok] = atom.qualified_id
    return index


def extract_premise_refs(text: str, name_index: dict, self_qid: str) -> set:
    """Scan body text for substrate-atom name matches; return qids set (excluding self)."""
    refs = set()
    for tok, qid in name_index.items():
        if qid == self_qid:
            continue
        # Word-boundary substring match
        # Use re.escape since tokens may contain regex-special chars
        pattern = r"\b" + re.escape(tok) + r"\b"
        if re.search(pattern, text):
            refs.add(qid)
            if len(refs) >= MAX_EDGES_PER_ATOM:
                break
    return refs


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None,
                    help="Only process first N atoms (smoke)")
    ap.add_argument("--no-canonical-name-only", action="store_true",
                    help="Disable underscore-or-multiword filter (more matches, more false positives)")
    ap.add_argument("--skip-corpus", nargs="*", default=["meta"],
                    help="Skip atoms in these corpora (default: meta)")
    args = ap.parse_args()

    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"loading atoms...")
    all_atoms = ps.all_atoms()
    print(f"total atoms: {len(all_atoms)}")

    # Build name index
    canonical_only = not args.no_canonical_name_only
    print(f"building name index (canonical_name_only={canonical_only})...")
    name_index = build_name_index(all_atoms, canonical_name_only=canonical_only)
    print(f"name index size: {len(name_index)}")

    # Filter atoms to scan
    scan_atoms = [a for a in all_atoms
                  if (a.corpus.value if hasattr(a.corpus, "value") else str(a.corpus)) not in args.skip_corpus]
    print(f"atoms to scan (after skip-corpus): {len(scan_atoms)}")
    if args.limit:
        scan_atoms = scan_atoms[: args.limit]
        print(f"limited to first {len(scan_atoms)}")

    # Existing edges
    print(f"building existing edge set...")
    existing = set()
    for r in ps.iter_all_relations():
        try:
            existing.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass
    print(f"existing relations: {len(existing)}")

    # Process atoms
    atoms_with_refs = 0
    total_refs_found = 0
    edges_added = 0
    skipped_dup = 0
    failed = 0
    sample_extractions = []

    for i, atom in enumerate(scan_atoms):
        text = collect_text_to_scan(atom)
        if not text or len(text) < 20:
            continue
        refs = extract_premise_refs(text, name_index, atom.qualified_id)
        if not refs:
            continue
        atoms_with_refs += 1
        total_refs_found += len(refs)
        if len(sample_extractions) < 6 and len(refs) >= 2:
            sample_extractions.append((atom.qualified_id, atom.name, sorted(refs)[:6]))

        src_qid = atom.qualified_id
        for tgt_qid in refs:
            key = (src_qid, "DEPENDS_ON", tgt_qid)
            if key in existing:
                skipped_dup += 1
                continue
            if args.dry_run:
                edges_added += 1
                existing.add(key)
                continue
            try:
                ps.add_relation(src_qid, RelationType.DEPENDS_ON, tgt_qid,
                                source="body_text_multi_premise_extractor_v1",
                                note=f"body-text multi-premise match: {atom.name[:40]}")
                edges_added += 1
                existing.add(key)
            except Exception as e:
                msg = str(e)[:100]
                if any(k in msg.lower() for k in ("already", "duplicate")):
                    skipped_dup += 1
                else:
                    failed += 1

        if (i + 1) % 2000 == 0:
            print(f"  progress: {i+1}/{len(scan_atoms)} atoms; {edges_added} edges; {atoms_with_refs} with refs")

    print(f"\n=== BODY-TEXT MULTI-PREMISE EXTRACTION SUMMARY ===")
    print(f"atoms scanned: {len(scan_atoms)}")
    print(f"atoms with >=1 premise ref: {atoms_with_refs}")
    print(f"total refs found: {total_refs_found}")
    print(f"avg refs (when present): {total_refs_found / max(atoms_with_refs, 1):.2f}")
    print(f"edges added: {edges_added}")
    print(f"edges skipped (duplicate): {skipped_dup}")
    print(f"edges failed: {failed}")
    print(f"\nsample extractions (atoms with >=2 refs):")
    for qid, name, refs in sample_extractions:
        refs_short = [r.split("::")[-1] for r in refs]
        print(f"  {qid} ({name[:30]})")
        print(f"    -> {refs_short}")
    if args.dry_run:
        print(f"\n[DRY RUN] no edges written. Re-run without --dry-run to author.")


if __name__ == "__main__":
    main()
