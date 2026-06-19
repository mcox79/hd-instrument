"""Ingest substrate self-index batch 02 (refined atoms + 88 relations + 5 queries).

Research's batch 02 atoms put algebra_category / domain / concept_links inside
metadata (flat keys). Our Atom schema has them as top-level fields. Normalizer
lifts metadata fields up into the dedicated fields at ingest time.

After ingest:
- re-run discover.py to check structural_gap warnings resolved by relations
- run all 5 disclosed queries; EMBEDDING_DRIFT on Q1/Q2/Q4 should drop
- emit findings report
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

# Make repo root importable when running as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.discover import discover_all
from backend.substrate_index.encode import AtomEncoder
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.retrieve import Retriever
from backend.substrate_index.schema import (
    ALGEBRA_CATEGORIES,
    Atom,
    Corpus,
    RelationType,
    Tier,
    TestQuery,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("batch02_ingest")


DATA_ROOT = Path("data/substrate_index")
BATCH01_PATH = DATA_ROOT / "math_corpus_batch01.jsonl"
BATCH02_ATOMS_PATH = DATA_ROOT / "math_corpus_batch02_atoms_refined.jsonl"
BATCH02_RELATIONS_PATH = DATA_ROOT / "math_corpus_batch02_relations.jsonl"
BATCH02_QUERIES_PATH = DATA_ROOT / "math_corpus_batch02_disclosed_queries.json"
BATCH02_REMAINING_53_PATH = DATA_ROOT / "math_corpus_batch02_algebra_vec_remaining_53.jsonl"
CONCEPT_SUBSET_10_PATH = DATA_ROOT / "concept_corpus_early_subset_10.jsonl"


# ============================================================
# Normalize Research's batch 02 format into our Atom schema
# ============================================================

def _algebra_category_name(category_int: int) -> str:
    """Map int 1-13 -> category string from ALGEBRA_CATEGORIES."""
    idx = category_int - 1
    if 0 <= idx < len(ALGEBRA_CATEGORIES):
        return ALGEBRA_CATEGORIES[idx]
    return "unknown"


def normalize_atom_record(rec: dict) -> dict:
    """Lift Research's flat metadata keys (algebra_category/domain/concept_links)
    into dedicated top-level Atom fields.

    Idempotent: if the top-level fields already exist, leaves them.
    """
    rec = dict(rec)
    meta = dict(rec.get("metadata") or {})

    if "algebra_category" in meta or "domain" in meta:
        algebra = dict(rec.get("algebra") or {})
        if "algebra_category" in meta and "structure" not in algebra:
            cat_int = meta.pop("algebra_category")
            algebra["category_int"] = cat_int
            algebra["structure"] = _algebra_category_name(cat_int) if isinstance(cat_int, int) else str(cat_int)
        if "domain" in meta and "domain" not in algebra:
            algebra["domain"] = meta.pop("domain")
        if "commutative" in meta and "commutative" not in algebra:
            algebra["commutative"] = meta.pop("commutative")
        if "associative" in meta and "associative" not in algebra:
            algebra["associative"] = meta.pop("associative")
        if "preserves_unit_modulus" in meta and "preserves_unit_modulus" not in algebra:
            algebra["preserves_unit_modulus"] = meta.pop("preserves_unit_modulus")
        rec["algebra"] = algebra

    if "concept_links" in meta and "concept_links" not in rec:
        rec["concept_links"] = list(meta.pop("concept_links"))

    rec["metadata"] = meta
    return rec


# ============================================================
# Ingest
# ============================================================

def load_atoms_jsonl(path: Path) -> list[Atom]:
    atoms = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                log.error("line %d %s: %s", line_no, path, e)
                continue
            rec = normalize_atom_record(rec)
            try:
                atoms.append(Atom.from_dict(rec))
            except Exception as e:
                log.error("line %d %s: Atom.from_dict failed: %s", line_no, path, e)
    return atoms


def load_relations_jsonl(path: Path) -> list[tuple[str, RelationType, str, str]]:
    """Returns list of (src_qid, rel_type, tgt_qid, note)."""
    rels = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                log.error("rel line %d: %s", line_no, e)
                continue
            try:
                src = rec.get("src") or rec.get("src_id")
                tgt = rec.get("tgt") or rec.get("tgt_id")
                rt_str = rec.get("rel_type") or rec.get("type")
                rt = RelationType(rt_str)
                note = rec.get("note") or rec.get("fidelity") or ""
                if isinstance(note, dict):
                    note = json.dumps(note)
                # If ids are not qualified (no "::"), prepend math:: (default for batch 02)
                if "::" not in src:
                    src = f"math::{src}"
                if "::" not in tgt:
                    tgt = f"math::{tgt}"
                rels.append((src, rt, tgt, note))
            except Exception as e:
                log.error("rel line %d: %s (rec=%s)", line_no, e, rec)
    return rels


def main():
    pstore = PartitionedStore(DATA_ROOT)

    # 1. Ingest batch 01 (if not already present)
    if BATCH01_PATH.exists():
        atoms_01 = load_atoms_jsonl(BATCH01_PATH)
        added = 0
        for a in atoms_01:
            if not pstore.has_atom(a.qualified_id):
                pstore.add_atom(a, source="batch01", note="initial corpus")
                added += 1
        log.info("batch01: %d atoms loaded, %d added", len(atoms_01), added)

    # 2. Ingest batch 02 refined atoms (overwrites batch 01 versions of the 7)
    atoms_02 = load_atoms_jsonl(BATCH02_ATOMS_PATH)
    refined = 0
    for a in atoms_02:
        # Remove batch 01 version if present, then add refined
        if pstore.has_atom(a.qualified_id):
            pstore.remove_atom(a.qualified_id, source="batch02", note="superseded by refinement")
        pstore.add_atom(a, source="batch02_refined", note="algebra-vec + sharpened description")
        refined += 1
    log.info("batch02 refined: %d atoms re-ingested", refined)

    # 2a-bis. Ingest 10-atom concept-corpus early subset (Research follow-up;
    # 8-field schema; decomposes_to becomes USES edges to math atoms)
    if CONCEPT_SUBSET_10_PATH.exists():
        concept_atoms = load_atoms_jsonl(CONCEPT_SUBSET_10_PATH)
        added_c = 0
        rels_from_decompose = 0
        for a in concept_atoms:
            if not pstore.has_atom(a.qualified_id):
                pstore.add_atom(a, source="concept_subset_10",
                                note="early subset for v2 validation")
                added_c += 1
            # decomposes_to -> USES edges (math atoms)
            decomp = a.metadata.get("decomposes_to") or []
            for tgt in decomp:
                try:
                    pstore.add_relation(a.qualified_id, RelationType.USES, tgt,
                                        source="concept_subset_10:decomposes_to",
                                        note="auto from 8-field schema")
                    rels_from_decompose += 1
                except Exception as e:
                    log.warning("USES skip %s -> %s: %s", a.qualified_id, tgt, e)
            # related_concepts -> SPECIALIZES edges (concept atoms)
            related = a.metadata.get("related_concepts") or []
            for tgt in related:
                try:
                    pstore.add_relation(a.qualified_id, RelationType.SPECIALIZES, tgt,
                                        source="concept_subset_10:related",
                                        note="auto from 8-field schema")
                except Exception as e:
                    pass  # may not exist yet; OK
        log.info("concept subset 10: %d atoms added, %d USES edges from decomposes_to",
                 added_c, rels_from_decompose)

    # 2b. Ingest remaining-53 algebra-vec (Research follow-up; DELTA format:
    # only id + algebra/signature/complexity fields). Merges onto existing
    # atoms instead of creating new ones.
    if BATCH02_REMAINING_53_PATH.exists():
        upgraded = 0
        skipped = 0
        with BATCH02_REMAINING_53_PATH.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError as e:
                    log.error("rem53 line %d: %s", line_no, e)
                    continue
                local_id = rec["id"]
                # Determine qualified id (default math::)
                qid = local_id if "::" in local_id else f"math::{local_id}"
                existing = pstore.get_atom(qid)
                if existing is None:
                    log.warning("rem53 line %d: atom %s not in store; skipped", line_no, qid)
                    skipped += 1
                    continue
                from dataclasses import replace
                # Lift algebra_category int -> structure name if int
                alg = rec.get("algebra")
                if alg and "structure" in alg and isinstance(alg["structure"], int):
                    cat = alg["structure"]
                    if 1 <= cat <= 13:
                        alg = dict(alg)
                        alg["category_int"] = cat
                        alg["structure"] = ALGEBRA_CATEGORIES[cat - 1]
                merged = replace(
                    existing,
                    algebra=alg if alg else existing.algebra,
                    signature=rec.get("signature") or existing.signature,
                    complexity=rec.get("complexity") or existing.complexity,
                )
                pstore.remove_atom(qid, source="batch02_53", note="upgrading with algebra-vec")
                pstore.add_atom(merged, source="batch02_53",
                                note="algebra/signature/complexity fields merged")
                upgraded += 1
        log.info("batch02 remaining-53 algebra-vec: %d atoms upgraded, %d skipped",
                 upgraded, skipped)

    # 3. Ingest 88 relations
    rels = load_relations_jsonl(BATCH02_RELATIONS_PATH)
    added_rels = 0
    skipped_rels = 0
    for src, rt, tgt, note in rels:
        try:
            pstore.add_relation(src, rt, tgt, source="batch02", note=note)
            added_rels += 1
        except Exception as e:
            log.warning("rel skip %s -%s-> %s: %s", src, rt.value, tgt, e)
            skipped_rels += 1
    log.info("batch02 relations: %d added, %d skipped", added_rels, skipped_rels)

    # 4. Stats
    stats = pstore.stats()
    log.info("post-ingest stats: total_atoms=%d total_relations=%d cross_store=%d",
             stats["total_atoms"], stats["total_relations"], stats["cross_store_relations"])
    print(json.dumps(stats, indent=2))

    # 5. Build retriever + run 5 disclosed queries
    log.info("building encoder + retriever (this takes ~20-30 sec for the bge model load)")
    encoder = AtomEncoder()
    retriever = Retriever(pstore, encoder)
    t0 = time.perf_counter()
    retriever.rebuild_index()
    log.info("index built in %.1f sec", time.perf_counter() - t0)

    # 6. Run discover
    log.info("running discover_all...")
    report = discover_all(pstore, retriever=retriever)
    by_kind = {}
    for f in report.findings:
        by_kind[f.kind] = by_kind.get(f.kind, 0) + 1
    log.info("discover findings: %d total; by kind: %s", len(report.findings), by_kind)

    # 7. Load queries + run them
    with BATCH02_QUERIES_PATH.open("r", encoding="utf-8") as f:
        queries_raw = json.load(f)
    # File format may be list-of-dicts OR dict-with-queries-key
    if isinstance(queries_raw, dict):
        queries_raw = queries_raw.get("queries", []) or queries_raw.get("disclosed_queries", [])

    # Helper: encode a query and rank against a chosen atom-vector projection
    def rank_against(query_text: str, atoms_vec_attr: str, top_k: int = 10):
        import numpy as np
        q = retriever.encoder.encode_query_text(query_text)
        # Gather atom vectors for the chosen attribute
        atom_ids = []
        mat_rows = []
        for aid, av in retriever._vectors.items():
            v = getattr(av, atoms_vec_attr, None)
            if v is None:
                continue
            atom_ids.append(aid)
            mat_rows.append(v)
        if not atom_ids:
            return []
        mat = np.stack(mat_rows)
        sims = mat @ q
        order = np.argsort(-sims)[:top_k]
        return [atom_ids[i] for i in order]

    log.info("running %d disclosed queries (composite vs semantic-only attribution)...", len(queries_raw))
    results = []
    for q_rec in queries_raw:
        qid = q_rec.get("qid", q_rec.get("id", "Q?"))
        query_text = q_rec.get("query_text") or q_rec.get("text") or q_rec.get("question")
        expected = q_rec.get("expected_atom_ids", [])
        if not query_text:
            log.warning("query %s has no query_text; rec=%s", qid, q_rec)
            continue
        t0 = time.perf_counter()
        cands = retriever.semantic(query_text, top_k=10)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        top_ids = [c.atom_id for c in cands]
        # Layer 1 attribution: re-rank by semantic-only and by algebra-only
        top_semantic_only = rank_against(query_text, "semantic", top_k=10)
        top_algebra_only = rank_against(query_text, "algebra", top_k=10)
        # Compute recall@1/3/10 against expected
        if expected:
            exp_set = set(expected)
            top1 = top_ids[0] if top_ids else None
            recall_at_1 = 1.0 if top1 in exp_set else 0.0
            recall_at_3 = len(exp_set & set(top_ids[:3])) / max(1, len(exp_set))
            recall_at_10 = len(exp_set & set(top_ids[:10])) / max(1, len(exp_set))
        else:
            recall_at_1 = recall_at_3 = recall_at_10 = None
        results.append({
            "qid": qid,
            "query_text": query_text[:120],
            "expected": list(expected),
            "top10_composite": top_ids,
            "top10_semantic_only": top_semantic_only,
            "top10_algebra_only": top_algebra_only,
            "recall_at_1": recall_at_1,
            "recall_at_3": recall_at_3,
            "recall_at_10": recall_at_10,
            "latency_ms": round(elapsed_ms, 1),
        })

    out_path = DATA_ROOT / "bench_reports" / f"batch02_post_ingest_{int(time.time())}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "stats": stats,
        "discover_by_kind": by_kind,
        "discover_total": len(report.findings),
        "query_results": results,
    }, indent=2), encoding="utf-8")
    log.info("wrote bench report -> %s", out_path)

    # Print summary
    print("\n=== POST-BATCH-02 INGEST SUMMARY ===")
    print(f"atoms: {stats['total_atoms']}  relations: {stats['total_relations']}  cross_store: {stats['cross_store_relations']}")
    print(f"discover findings: {len(report.findings)} ({by_kind})")
    print("\nQuery results (composite | semantic-only | algebra-only):")
    for r in results:
        print(f"  {r['qid']:8s}  composite={r['top10_composite'][:3]}")
        print(f"            semantic ={r['top10_semantic_only'][:3]}")
        print(f"            algebra  ={r['top10_algebra_only'][:3]}")

    # v2 Index 2 demonstration: shared-algebra retrieval (atom-to-atom)
    print("\n=== v2 Index 2 atom-to-atom shared-algebra retrieval ===")
    from backend.substrate_index.algebra_index import AlgebraIndex
    aidx = AlgebraIndex(dim=1024)
    encoded = aidx.build(pstore)
    print(f"algebra_index built: {encoded} atoms with algebra fields populated")

    probes = [
        ("math::T2/fhrr_bind", "expect dual/inverse + fellow groups"),
        ("math::T3/hungarian_assignment", "expect Jonker-Volgenant, Chu-Liu-Edmonds, Viterbi (discrete-opt family)"),
        ("math::T2/bundling", "expect superposition (after distinction; same family)"),
        ("math::T3/hmm_emission", "expect hmm_transition (both probability-simplex)"),
    ]
    for atom_id, expectation in probes:
        if not pstore.has_atom(atom_id):
            print(f"  {atom_id}  SKIP (not in store)")
            continue
        results_alg = aidx.atoms_with_shared_algebra(atom_id, top_k=5)
        results_sig = aidx.atoms_with_shared_signature(atom_id, top_k=5)
        print(f"  {atom_id}")
        print(f"    expected: {expectation}")
        print(f"    shared algebra: {[(aid.split('::')[-1], round(s, 3)) for aid, s in results_alg[:3]]}")
        print(f"    shared signature: {[(aid.split('::')[-1], round(s, 3)) for aid, s in results_sig[:3]]}")


if __name__ == "__main__":
    main()
