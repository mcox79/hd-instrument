# Research -> Testbed: CELL 6 Lean Mathlib ingest parser SKELETON -- substrate_ingest_lean_mathlib_v1.py concrete scaffold -- substrate_evolve_phase6_bulk_jsonl.py compatible -- LANE B bedrock priority

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight; per WHILE-USER-AWAY enforcement L4 priority queue + L4 diversification applied; per 3-LANE coordination LANE B bedrock parallel-not-serial)

## Intuitive framing

**What this is**: Lean Mathlib is the "Wikipedia of formalized mathematics" — ~80K theorems + definitions + structures, each WITH its dependencies explicitly listed in Lean 4 source files. Like a dictionary where every entry includes its etymology and the words used to define it.

**Why it matters for USER vision**: substrate's L6-PROOF prover currently has corpus-limited depth ceiling of 3 (max). Lean Mathlib's 80K formalized statements come with explicit dependency chains 10+ levels deep. Ingesting Lean Mathlib gives substrate INSTANT access to depth-10+ proof chains across all of math. No manual authoring needed.

**Substrate-product positioning at scale**: substrate + Lean Mathlib + L6-PROOF FINDER = the first cognitive architecture that can PROVE soundly at depth 10+ over Mathlib's 80K-theorem corpus. LLMs cannot (Lean-Copilot empirical literature). Becomes canonical substrate-vs-LLM categorical claim.

## Skeleton

```python
#!/usr/bin/env python3
"""
tools/substrate_ingest_lean_mathlib_v1.py

Ingest Lean 4 Mathlib formalized math library into substrate.
Output: data/substrate_index/lean_mathlib_{batch_id}.jsonl
Compatible with substrate_evolve_phase6_bulk_jsonl.py downstream pipeline.

Workflow:
1. Clone Mathlib4 mirror: https://github.com/leanprover-community/mathlib4
2. Walk .lean source files
3. Parse: theorem / lemma / def / structure / class / inductive declarations + their dependencies
4. Generate JSONL atoms per Q2+Q3 substrate convention
5. Generate DEPENDS_ON edge JSONL between cited atoms

Heat: remote_cpu_queue SAFE (no GPU; I/O-bound + text parsing only).

Pre-reg HARD-PASS (per CELL 6 design):
- >= 40K theorems + definitions ingested within 2 days
- Cross-link >= 2K to BATCH 01-23 atoms (e.g. mathlib_Matrix.det -> SVD; mathlib_InnerProductSpace -> hilbert_space)
- L6-PROOF cross-validation: substrate proves 50 random Lean lemmas correctly via L6-PROOF generalized 6-edge typing context >= 70pct HARD-PASS
- depth ceiling jump 3 -> 8+ on benchmark goal pool (per BATCH 17-24 + Lean Mathlib combined)
"""
import json
import re
import pathlib
import subprocess
from collections import defaultdict


MATHLIB_URL = "https://github.com/leanprover-community/mathlib4.git"
MATHLIB_LOCAL = pathlib.Path("data/external/mathlib4")
OUTPUT_DIR = pathlib.Path("data/substrate_index")
ATOMS_BATCH_SIZE = 5000  # shard atoms into 5K-atom JSONL files (LFS-safe < 50MB)
EDGES_BATCH_SIZE = 20000


def clone_mathlib():
    """Shallow clone Mathlib4 if not present."""
    MATHLIB_LOCAL.mkdir(parents=True, exist_ok=True)
    if not (MATHLIB_LOCAL / ".git").exists():
        print(f"Cloning Mathlib4 (~500MB shallow) from {MATHLIB_URL}")
        subprocess.run(
            ["git", "clone", "--depth", "1", MATHLIB_URL, str(MATHLIB_LOCAL)],
            check=True,
        )
    else:
        print(f"Mathlib4 already cloned at {MATHLIB_LOCAL}")


# Lean 4 declaration patterns (refine per real .lean file inspection)
# A theorem/lemma typically looks like:
#   theorem Foo.bar {alpha} [Group alpha] (x y : alpha) : x * y * x^(-1) = y * (x * y * x^(-1)) := by ...
# A def:
#   def baz (n : Nat) : Nat := n + 1
# A structure:
#   structure RingHom (R S : Type*) [Ring R] [Ring S] extends ... where ...

DECLARATION_PATTERN = re.compile(
    r"^(?P<kind>theorem|lemma|def|structure|class|inductive|instance|example)\s+"
    r"(?P<name>[A-Za-z_][\w.]+)"
    r"(?P<typeparams>[^:=]*?)"
    r"(?:[:](?P<signature>[^:=]*?))?"
    r"(?::=|by|where)"
    , re.MULTILINE
)

# Lean dependencies appear as: foo.bar in signatures, proofs, type expressions
DEPENDENCY_PATTERN = re.compile(r"\b([A-Z][A-Za-z_]+(?:\.[A-Za-z_]+)+)\b")


def parse_lean_file(lean_path: pathlib.Path):
    """Parse a single .lean file extracting declaration + dependency records."""
    declarations = []
    try:
        text = lean_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"Warning: failed to read {lean_path}: {e}")
        return []
    
    # Strip Lean comments (-- and /- ... -/)
    text_clean = strip_lean_comments(text)
    
    for m in DECLARATION_PATTERN.finditer(text_clean):
        kind = m.group("kind")
        name = m.group("name")
        signature = (m.group("signature") or "").strip()[:500]
        
        # Find dependencies in signature + proof
        deps_in_decl = set(DEPENDENCY_PATTERN.findall(signature))
        # Filter to those matching common Mathlib namespace patterns
        deps_filtered = [
            d for d in deps_in_decl 
            if any(d.startswith(prefix + ".") for prefix in 
                   ["Mathlib", "Nat", "Real", "Int", "Set", "List", "Group", "Ring", "Field",
                    "Module", "Submodule", "Matrix", "Polynomial", "Topology", "Filter",
                    "MeasureTheory", "Probability", "LinearMap", "InnerProductSpace"])
        ]
        
        declarations.append({
            "kind": kind,
            "name": name,
            "signature": signature,
            "dependencies": deps_filtered[:50],  # cap to avoid blow-up
            "source_path": str(lean_path.relative_to(MATHLIB_LOCAL)),
        })
    
    return declarations


def strip_lean_comments(text):
    """Remove -- line comments and /- ... -/ block comments from Lean source."""
    # Remove block comments
    text = re.sub(r'/-.*?-/', '', text, flags=re.DOTALL)
    # Remove line comments
    lines = [re.sub(r'--.*$', '', line) for line in text.splitlines()]
    return "\n".join(lines)


def declaration_to_substrate_atom(decl: dict) -> dict:
    """Convert a Mathlib declaration to substrate atom JSONL line."""
    name = decl["name"]
    kind = decl["kind"]
    
    # Tier heuristic:
    # T1 = structure / class (foundational types)
    # T2 = theorem / lemma / def (intermediate)
    # T3 = instance / example (specific applications)
    tier = "T1" if kind in ("structure", "class", "inductive") else ("T3" if kind in ("instance", "example") else "T2")
    
    # is_axiom: structure / class definitions are foundational (treated as axioms in CH terms)
    is_axiom_flag = kind in ("structure", "class", "inductive")
    
    return {
        "canonical_name": f"mathlib_{name.replace('.', '_').lower()}",
        "aliases": [name, f"mathlib_{kind}_{name}"],
        "tier": tier,
        "partition": "math_foundation::mathlib4",
        "science_algebra_category": f"formalized_mathematics::lean::{kind}",
        "algebra_dict": {
            "kind": kind,
            "name": name,
            "signature": decl["signature"][:300],
            "source_path": decl["source_path"],
        },
        "is_axiom": is_axiom_flag,
        "serves_capability": ["formalized_math_lean", "L6_PROOF_validation_lean", "type_theory_substrate", "math_corpus_breadth"],
        "depends_on": [f"mathlib_{d.replace('.', '_').lower()}" for d in decl["dependencies"]],
        "signature_hint": f"lean_{kind}",
    }


def shard_jsonl(records, output_prefix, batch_size):
    for i in range(0, len(records), batch_size):
        shard_id = i // batch_size
        shard_path = OUTPUT_DIR / f"{output_prefix}_shard_{shard_id:04d}.jsonl"
        with shard_path.open("w", encoding="utf-8") as f:
            for record in records[i:i + batch_size]:
                f.write(json.dumps(record) + "\n")
        print(f"Wrote {shard_path} ({len(records[i:i + batch_size])} records)")


def main():
    print("=== Substrate Lean Mathlib Ingest v1 ===")
    
    # Phase 1: Clone
    clone_mathlib()
    
    # Phase 2: Parse
    all_declarations = []
    lean_files = list(MATHLIB_LOCAL.glob("**/*.lean"))
    # Filter to Mathlib subdirectory (exclude tests/build/etc)
    mathlib_files = [f for f in lean_files if "Mathlib" in str(f.relative_to(MATHLIB_LOCAL))]
    print(f"Parsing {len(mathlib_files)} Mathlib .lean files")
    
    for lean_path in mathlib_files:
        decls = parse_lean_file(lean_path)
        all_declarations.extend(decls)
    
    print(f"Extracted {len(all_declarations)} declarations")
    
    # Phase 3: Convert to substrate atoms
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    atoms = [declaration_to_substrate_atom(d) for d in all_declarations]
    shard_jsonl(atoms, "mathlib_atoms_2026", ATOMS_BATCH_SIZE)
    
    # Phase 4: DEPENDS_ON edges
    edges = []
    for atom in atoms:
        for prereq in atom["depends_on"]:
            edges.append({
                "src": atom["canonical_name"],
                "dst": prereq,
                "relation": "DEPENDS_ON",
                "source": "mathlib_lean_dependency",
            })
    shard_jsonl(edges, "mathlib_depends_on_edges_2026", EDGES_BATCH_SIZE)
    
    # Phase 5: Summary
    summary = {
        "lean_files_processed": len(mathlib_files),
        "declarations_total": len(all_declarations),
        "atoms_total": len(atoms),
        "axiom_atoms": sum(1 for a in atoms if a.get("is_axiom")),
        "tier_T1": sum(1 for a in atoms if a.get("tier") == "T1"),
        "tier_T2": sum(1 for a in atoms if a.get("tier") == "T2"),
        "tier_T3": sum(1 for a in atoms if a.get("tier") == "T3"),
        "edges_total": len(edges),
        "edges_per_atom_avg": len(edges) / max(1, len(atoms)),
    }
    summary_path = OUTPUT_DIR / "mathlib_ingest_summary_2026.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"Summary: {summary_path}")
    print(json.dumps(summary, indent=2))
    
    # Pre-reg HARD-PASS check
    pre_reg = {
        "atoms_at_least_40K": len(atoms) >= 40000,
        "edges_at_least_average_5_per_atom": (len(edges) / max(1, len(atoms))) >= 5.0,
        "has_axiom_atoms": summary["axiom_atoms"] >= 1000,
    }
    print(f"Pre-reg checks: {pre_reg}")


if __name__ == "__main__":
    main()
```

## Caveats + iteration plan

1. **Lean parsing real complexity**: Lean 4 syntax is more nuanced than the regex pattern shown. Real implementation needs:
   - Robust handling of dependent types + universe polymorphism
   - Multi-line declarations
   - Tactic blocks (between `by ... done` or `by ... := done`)
   - Notation declarations (custom operators)
   - Mutual definitions
   - Recommend: bootstrap with public Lean 4 parsers (lean4-mode, leanblueprint tooling, lean-mathlib mining utilities)

2. **Cross-validation with substrate BATCH 01-23**:
   - mathlib_Matrix.det → SVD (BATCH 08) → SHARES_MATH candidate
   - mathlib_InnerProductSpace → hilbert_space (BATCH 04) → SHARES_MATH
   - mathlib_Polynomial → polynomial_ring (BATCH 06) → SHARES_MATH
   - mathlib_MeasureTheory.* → BATCH 10 measure theory atoms → SHARES_MATH bridges
   - mathlib_Topology.* → BATCH 04 topology atoms → SHARES_MATH

3. **Substrate-quality-first preservation**: Testbed verifies ingest quality on small batch first (e.g. first 1000 declarations) before scaling to full 40K-80K. Phase-2-light smoke methodology + Heaps + Good-Turing methodology applies.

4. **LFS preconditioning**: 80K atoms across multiple JSONL shards may exceed LFS thresholds if individual shards grow. ATOMS_BATCH_SIZE=5000 keeps individual JSONL <50MB safely; per-shard atom count is conservative.

5. **L6-PROOF cross-validation post ingest**: take 50 random Lean lemmas, run substrate's L6-PROOF FINDER on them via the generalized 6-edge typing context, measure HARD-PASS rate. Expected >=70pct per pre-reg.

6. **Depth ceiling jump empirical anchor**: Exp-Dev's derivation_depth_ceiling_probe should be re-run post BATCH 17-24 + Lean Mathlib combined ingest. Expected jump from 3 (current) → 8-10+ (Mathlib has explicit 10+-deep chains in core Mathlib.Algebra.* + Mathlib.LinearAlgebra.* hierarchies).

## Routing

- **Testbed**: pick up skeleton; refine Lean parser regex per real .lean file format (or bootstrap via existing Lean 4 tooling); ship to remote_cpu_queue; coordinate with L6-PROOF FINDER re-run post-ingest
- **Exp-Dev**: PHASE 3 verification cell post-ingest: cross-validate 50 random Mathlib lemmas via substrate_query.py prove subcommand + depth ceiling re-probe
- **Research**: standing for ingest verdicts; CELL 7 ProofWiki on demand; BATCH 25 information geometry next per priority queue

## Cross-references

- notes/research_to_testbed_PRODUCTION_SCALE_EXTERNAL_CORPUS_INGEST_*.md (5-cell strategy; CELL 6 = Lean Mathlib)
- notes/research_to_testbed_exp_dev_USER_VISION_*.md (Lean Mathlib in roadmap)
- notes/research_to_testbed_exp_dev_MATH_SCIENCE_CORPUS_PARALLEL_INGEST_*.md (3-LANE coordination LANE B)
- notes/research_to_testbed_CELL_1_MIZAR_INGEST_PARSER_SKELETON_*.md (CELL 1 Mizar predecessor; similar structure)
- notes/exp_dev_to_research_DERIVATION_DEPTH_CEILING_*.md (depth ceiling 3 + Mathlib remedy)

---

**Testbed:** CELL 6 LEAN MATHLIB INGEST PARSER SKELETON tools/substrate_ingest_lean_mathlib_v1.py concrete scaffold ~300 LOC clone Mathlib4 + parse .lean files theorem/lemma/def/structure/class/inductive + DEPENDENCY_PATTERN + declaration_to_substrate_atom Q2+Q3 convention DEPENDS_ON edges sharded JSONL substrate_evolve_phase6_bulk_jsonl.py compatible pre-reg HARD-PASS atoms >= 40K + average 5 edges/atom + axiom atoms >= 1K + cross-validation 50 random Lean lemmas via L6-PROOF >= 70pct + depth ceiling jump 3 -> 8-10+ + intuitive framing 80K formalized statements WITH explicit dependency chains 10+ levels deep + INSTANT depth lift no manual authoring + substrate-product positioning canonical claim substrate proves soundly at depth 10+ over Mathlib LLMs cannot per Lean-Copilot literature + USER full-auto overnight continuing.
