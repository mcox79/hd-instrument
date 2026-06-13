# Research -> Testbed: CELL 1 Mizar ingest parser SKELETON -- concrete tools/substrate_ingest_mizar_library_v1.py scaffold -- substrate_evolve_phase6_bulk_jsonl.py compatible

**From:** Research  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** CELL 1 highest-priority production-scale ingest (Mizar Mathematical Library) per prior coordination note; concrete parser skeleton to accelerate Testbed implementation

## Goal

Concrete Python scaffold for tools/substrate_ingest_mizar_library_v1.py that Testbed can pick up + extend. Designed to be drop-in compatible with existing substrate_evolve_phase6_bulk_jsonl.py output JSONL format.

Mizar Mathematical Library = ~1200+ articles + 50K+ theorems with EXPLICIT AXIOM DEPENDENCIES. Maps directly onto substrate's algebra_dict.axioms + DEPENDS_ON + is_axiom flag + CHTV-1 typed-derivation graph. L6-PROOF cell can run over Mizar corpus at scale.

## Skeleton

```python
#!/usr/bin/env python3
"""
tools/substrate_ingest_mizar_library_v1.py

Ingest Mizar Mathematical Library into substrate.
Output: data/substrate_index/mizar_library_{batch_id}.jsonl
Compatible with substrate_evolve_phase6_bulk_jsonl.py downstream pipeline.

Workflow:
1. Download Mizar MML mirror to data/external/mizar_mml/
2. Parse .miz files (formal source) + .abs files (abstracts/theorems)
3. Extract: theorem_id, statement (cleaned), axiom_dependencies (list of theorem_refs), proof_steps
4. Generate JSONL atoms per Q2+Q3 substrate convention
5. Generate DEPENDS_ON edge JSONL between cited atoms

Pre-reg HARD-PASS:
- >=30K atoms extracted
- >=100K DEPENDS_ON edges (depth-3+ chains)
- 100-theorem cross-validation sample: substrate_query.py prove returns PROVED for >=80% via L6-PROOF
- Cross-check substrate's BATCH 01-16 atoms (vector_space + kl_divergence + cauchy_schwarz_inequality + ...) link to Mizar equivalents via SHARES_MATH if found

Heat: remote_cpu_queue SAFE (no GPU; I/O-bound + text parsing only).
"""
import json
import re
import pathlib
import urllib.request
import subprocess
from collections import defaultdict


MIZAR_MML_URL = "http://mizar.uwb.edu.pl/~mizar/mml.tar.gz"  # check mirror availability
MIZAR_LOCAL_DIR = pathlib.Path("data/external/mizar_mml")
OUTPUT_DIR = pathlib.Path("data/substrate_index")
ATOMS_BATCH_SIZE = 5000  # shard atoms into 5K-atom JSONL files
EDGES_BATCH_SIZE = 20000


def download_mizar_mml():
    """Download + extract Mizar MML if not present."""
    MIZAR_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    tarball = MIZAR_LOCAL_DIR / "mml.tar.gz"
    if not tarball.exists():
        print(f"Downloading {MIZAR_MML_URL} -> {tarball}")
        urllib.request.urlretrieve(MIZAR_MML_URL, tarball)
    extracted_marker = MIZAR_LOCAL_DIR / ".extracted"
    if not extracted_marker.exists():
        subprocess.run(["tar", "-xzf", str(tarball), "-C", str(MIZAR_LOCAL_DIR)], check=True)
        extracted_marker.touch()


def parse_mizar_abs_file(abs_path: pathlib.Path) -> list[dict]:
    """
    Parse a .abs file extracting theorem records.
    .abs files contain abstracts: theorem name, statement, list of cited theorems.
    Returns list of theorem dicts with keys: name, statement, citations.
    """
    theorems = []
    text = abs_path.read_text(encoding="utf-8", errors="ignore")
    # Mizar abstract format pattern (simplified; refine on real files):
    # theorem :: <article>:<id>
    # <statement>
    # by <cited_theorem_1>, <cited_theorem_2>, ... ;
    theorem_pattern = re.compile(
        r"theorem\s*::\s*(?P<article>\w+):(?P<id>\d+)\s*(?P<statement>[^\.]+?)\s*by\s*(?P<citations>[\w:,\s]+);",
        re.MULTILINE | re.DOTALL,
    )
    for m in theorem_pattern.finditer(text):
        citations = [c.strip() for c in m.group("citations").split(",") if c.strip()]
        theorems.append({
            "article": m.group("article"),
            "id": m.group("id"),
            "name": f"{m.group('article')}:{m.group('id')}",
            "statement": m.group("statement").strip(),
            "citations": citations,
        })
    return theorems


def parse_mizar_voc_file(voc_path: pathlib.Path) -> list[dict]:
    """
    Parse a .voc vocabulary file for axiom-like primitives (no citations = AXIOM).
    Returns list of vocabulary dicts.
    """
    vocab = []
    text = voc_path.read_text(encoding="utf-8", errors="ignore")
    # Vocabulary format: M<symbol> O<operator> R<relation> etc.
    voc_pattern = re.compile(r"^([MORSV])(\S+)$", re.MULTILINE)
    for m in voc_pattern.finditer(text):
        sym_type = {"M": "mode", "O": "operator", "R": "relation", "S": "structure", "V": "selector"}.get(m.group(1), "unknown")
        vocab.append({"type": sym_type, "symbol": m.group(2), "article": voc_path.stem})
    return vocab


def theorem_to_substrate_atom(theorem: dict) -> dict:
    """
    Convert a Mizar theorem record to substrate atom JSONL line.
    Q2+Q3 convention: canonical_name + tier + partition + algebra_dict + DEPENDS_ON.
    """
    is_axiom_local = len(theorem["citations"]) == 0
    return {
        "canonical_name": f"mizar_{theorem['article'].lower()}_{theorem['id']}",
        "aliases": [theorem["name"], f"{theorem['article']}:{theorem['id']}"],
        "tier": "T2",
        "partition": "math_foundation::mizar_mml",
        "science_algebra_category": "formalized_mathematics::mizar",
        "algebra_dict": {
            "statement": theorem["statement"][:500],  # truncate long statements
            "axioms": theorem["citations"],
            "source_article": theorem["article"],
            "source_id": theorem["id"],
        },
        "is_axiom": is_axiom_local,
        "serves_capability": ["substrate_proof_corpus", "L6_PROOF_mizar_verification", "formalized_math_substrate"],
        "depends_on": [
            f"mizar_{cite.split(':')[0].lower()}_{cite.split(':')[1]}"
            for cite in theorem["citations"]
            if ":" in cite
        ],
        "signature_hint": "mizar_theorem_with_citation_chain",
    }


def vocabulary_to_substrate_atom(voc: dict) -> dict:
    """
    Convert a Mizar vocabulary entry to substrate atom (primitive symbol; treat as T0 axiom).
    """
    return {
        "canonical_name": f"mizar_voc_{voc['article'].lower()}_{voc['type']}_{voc['symbol']}",
        "aliases": [voc["symbol"]],
        "tier": "T0",
        "partition": "math_foundation::mizar_mml::primitives",
        "science_algebra_category": "formalized_mathematics::mizar::vocabulary",
        "algebra_dict": {
            "type": voc["type"],
            "symbol": voc["symbol"],
        },
        "is_axiom": True,  # primitive vocabulary -> axiomatic
        "serves_capability": ["formalized_math_primitives", "L6_PROOF_axiom_leaf"],
        "signature_hint": f"mizar_primitive_{voc['type']}",
    }


def shard_jsonl(records: list[dict], output_prefix: str, batch_size: int):
    """Write records to sharded JSONL files."""
    for i in range(0, len(records), batch_size):
        shard_id = i // batch_size
        shard_path = OUTPUT_DIR / f"{output_prefix}_shard_{shard_id:04d}.jsonl"
        with shard_path.open("w", encoding="utf-8") as f:
            for record in records[i:i + batch_size]:
                f.write(json.dumps(record) + "\n")
        print(f"Wrote {shard_path} ({len(records[i:i + batch_size])} records)")


def main():
    print("=== Substrate Mizar Mathematical Library Ingest v1 ===")

    # Phase 1: Download
    download_mizar_mml()
    print(f"Mizar MML available at {MIZAR_LOCAL_DIR}")

    # Phase 2: Parse
    all_theorems = []
    all_vocab = []
    abs_files = list(MIZAR_LOCAL_DIR.glob("**/*.abs"))
    voc_files = list(MIZAR_LOCAL_DIR.glob("**/*.voc"))
    print(f"Parsing {len(abs_files)} .abs files + {len(voc_files)} .voc files")
    for abs_path in abs_files:
        theorems = parse_mizar_abs_file(abs_path)
        all_theorems.extend(theorems)
    for voc_path in voc_files:
        vocab = parse_mizar_voc_file(voc_path)
        all_vocab.extend(vocab)
    print(f"Extracted {len(all_theorems)} theorems + {len(all_vocab)} vocabulary entries")

    # Phase 3: Convert to substrate atoms
    theorem_atoms = [theorem_to_substrate_atom(t) for t in all_theorems]
    vocab_atoms = [vocabulary_to_substrate_atom(v) for v in all_vocab]
    all_atoms = theorem_atoms + vocab_atoms

    # Phase 4: Shard + write JSONL
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shard_jsonl(all_atoms, "mizar_mml_atoms_2026", ATOMS_BATCH_SIZE)

    # Phase 5: DEPENDS_ON edges JSONL
    edges = []
    for atom in theorem_atoms:
        for prereq in atom["depends_on"]:
            edges.append({
                "src": atom["canonical_name"],
                "dst": prereq,
                "relation": "DEPENDS_ON",
                "source": "mizar_mml_citation",
            })
    shard_jsonl(edges, "mizar_mml_depends_on_edges_2026", EDGES_BATCH_SIZE)

    # Phase 6: Summary
    summary = {
        "atoms_total": len(all_atoms),
        "theorem_atoms": len(theorem_atoms),
        "vocab_atoms": len(vocab_atoms),
        "axiom_atoms": sum(1 for a in all_atoms if a.get("is_axiom")),
        "edges_total": len(edges),
        "edges_per_atom_avg": len(edges) / max(1, len(theorem_atoms)),
    }
    summary_path = OUTPUT_DIR / "mizar_mml_ingest_summary_2026.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"Summary: {summary_path}")
    print(json.dumps(summary, indent=2))

    # Pre-reg HARD-PASS check
    pre_reg = {
        "atoms_at_least_30K": len(all_atoms) >= 30000,
        "edges_at_least_100K": len(edges) >= 100000,
    }
    print(f"Pre-reg checks: {pre_reg}")


if __name__ == "__main__":
    main()
```

## Caveats + iteration plan

1. **Mizar parsing real complexity**: .abs / .miz format is more nuanced than the regex pattern shown. Real implementation needs:
   - Robust handling of comment blocks (:: comments)
   - Multi-line theorem statements
   - Proof block delimiters (proof / end;)
   - Definition vs theorem distinction
   - Type / mode declarations
   - Recommend: bootstrap with public Mizar parsers (MathSciNet, MizAR, Hammer4Mizar tooling)

2. **Cross-validation with substrate BATCH 01-16**:
   - Mizar `vector_space` (FUNCT_1 + RLVECT_1) <-> substrate `vector_space` (BATCH 01) -> SHARES_MATH edge candidate
   - Mizar `INFNORM:1` Cauchy-Schwarz <-> substrate `cauchy_schwarz_inequality` (BATCH 05) -> SHARES_MATH
   - Mizar measure theory (MEASURE_*) <-> substrate measure theory (BATCH 10) -> SHARES_MATH bridges

3. **Substrate-quality-first preservation** (methodology rule 7): Testbed must verify ingest quality on small batch first (e.g. first 1000 atoms) before scaling to full 30K-50K. Phase-2-light smoke methodology (Heaps + Good-Turing per recent drill) applies.

4. **LFS preconditioning**: 30K-50K atoms across multiple JSONL shards will exceed GitHub 100MB if any single shard grows large. ATOMS_BATCH_SIZE=5000 keeps individual JSONL <50MB safely; EDGES_BATCH_SIZE=20000 also under. But cumulative repo state may push toward needing LFS migration P0.3 sooner.

5. **L6-PROOF validation post ingest**: cross-validation 100 random theorems via substrate_query.py prove subcommand. Expect HARD-PASS >=80% (per CELL 1 pre-reg). Use generalized 6-edge-type typing context per L6-PROOF SPEC UPDATE.

## Routing

- **Testbed**: pick up skeleton; refine Mizar parser regex per real .abs file format; ship to remote_cpu_queue; coordinate with L6-PROOF PHASE 2 ship for post-ingest validation
- **Exp-Dev**: PHASE 3 verification cell scope: cross-validate 100 random Mizar theorems via substrate_query.py prove; pre-reg HARD-PASS >=80% (lower than BATCH 01-16 G1-G5 because Mizar mechanical proofs at scale may stress L6-PROOF unfolder)
- **Research**: standing for ingest verdicts; CELL 2 Wikidata skeleton on demand

## Cross-references

- notes/research_to_testbed_PRODUCTION_SCALE_EXTERNAL_CORPUS_INGEST_*.md (CELL 1-5 strategy)
- notes/research_to_testbed_exp_dev_L6_PROOF_PHASE_2_SPEC_UPDATE_*.md (L6-PROOF generalized typing context)
- notes/research_to_testbed_T1_ALGEBRA_DICT_BACKFILL_BATCH_01-16_*.md (BATCH 01-16 cross-validation targets)
- notes/exp_dev_to_research_CHTV1_substrate_as_verifier_HARD_PASS_*.md (CHTV-1 1.0 precision validation precedent)

---

**Testbed:** CELL 1 MIZAR INGEST PARSER SKELETON tools/substrate_ingest_mizar_library_v1.py concrete scaffold download Mizar MML parse .abs .voc files theorem_to_substrate_atom vocabulary_to_substrate_atom Q2+Q3 convention DEPENDS_ON edges sharded JSONL substrate_evolve_phase6_bulk_jsonl.py compatible pre-reg HARD-PASS atoms >=30K edges >=100K cross-validation 100 theorems L6-PROOF >=80pct + caveats real Mizar parser complexity bootstrap with MizAR Hammer4Mizar tooling + cross-validation BATCH 01-16 SHARES_MATH bridges + Phase-2-light smoke methodology Heaps + Good-Turing applies + LFS preconditioning shard size 5K atoms 20K edges + L6-PROOF generalized 6-edge typing context per SPEC UPDATE + Exp-Dev PHASE 3 verification cell scope cross-validation 100 random Mizar theorems remote_cpu_queue safe + USER full-auto overnight continuing.
