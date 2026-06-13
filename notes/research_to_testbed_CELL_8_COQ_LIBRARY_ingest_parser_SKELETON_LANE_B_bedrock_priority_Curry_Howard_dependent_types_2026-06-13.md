# Research -> Testbed: CELL 8 Coq library ingest parser SKELETON -- substrate_ingest_coq_library_v1.py -- LANE B bedrock priority (Curry-Howard direct; dependent types)

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight; per WHILE-USER-AWAY L4 priority queue)

## Intuitive framing

Coq is a formal proof assistant based on **dependent type theory** (Calculus of Inductive Constructions). Its standard library + community libraries (~100K+ theorems across CompCert + Mathematical Components + iris-coq + Cosmos + Coq-Equations + ...) all use the SAME formalism: every proof IS a term whose type IS the theorem statement (Curry-Howard correspondence).

**Why LANE B bedrock priority + special**: Coq is the cleanest mapping to substrate's Curry-Howard architecture. Where Mizar/Lean encode proofs in their own logic, Coq's terms-as-proofs IS exactly what substrate's L6-PROOF + Pi/Sigma + CHTV-1 type-checker formalize. Ingesting Coq gives substrate ~100K dependent-type proof terms with EXPLICIT type information.

**Substrate-product positioning leap**: substrate + Coq library + L6-PROOF FINDER + Pi/Sigma + CHTV-1 = substrate becomes a dependent-type-aware proof checker over real formalized mathematics. LLMs cannot do this (Coq's dependent types break LLM hallucination patterns categorically).

## Skeleton

```python
#!/usr/bin/env python3
"""
tools/substrate_ingest_coq_library_v1.py

Ingest Coq standard library + Mathematical Components + CompCert into substrate.
Output: data/substrate_index/coq_library_{batch_id}.jsonl

Workflow:
1. Clone Coq libraries:
   - coq/coq (stdlib)
   - math-comp/math-comp (Mathematical Components)
   - AbsInt/CompCert (CompCert verified C compiler proofs)
2. Parse .v files for Definition + Theorem + Lemma + Inductive + Fixpoint + Record + Structure
3. Extract type signatures + dependencies via Require Import + module references
4. Generate JSONL atoms with Curry-Howard type annotations
5. Generate DEPENDS_ON edges from Coq's Require/Import + Module structure

Heat: remote_cpu_queue SAFE (no GPU; I/O-bound + text parsing only).

Pre-reg HARD-PASS:
- >= 50K Coq declarations (Definitions + Theorems + Lemmas + Inductives) ingested across 3 libraries within 3 days
- Cross-link >= 5K to BATCH 01-25 atoms (e.g. coq_Vector -> vector_space; coq_le_lt_trans -> order_relation primitive)
- L6-PROOF cross-validation: substrate proves 30 random Coq theorems via L6-PROOF generalized 6-edge typing context (CHTV-1 + Pi/Sigma + L6-PROOF unified) >= 65pct HARD-PASS
- Dependent type richness: >= 20pct of atoms carry explicit Pi-type or Sigma-type structure (substrate Curry-Howard direct mapping)
"""
import json
import re
import pathlib
import subprocess
from collections import defaultdict


COQ_REPOS = [
    ("coq_stdlib", "https://github.com/coq/coq.git", "theories/"),
    ("math_comp", "https://github.com/math-comp/math-comp.git", "mathcomp/"),
    ("compcert", "https://github.com/AbsInt/CompCert.git", "."),
]
COQ_LOCAL = pathlib.Path("data/external/coq_libraries")
OUTPUT_DIR = pathlib.Path("data/substrate_index")
ATOMS_BATCH_SIZE = 5000
EDGES_BATCH_SIZE = 20000


# Coq declaration patterns
DECLARATION_PATTERN = re.compile(
    r"(?P<kind>Definition|Theorem|Lemma|Corollary|Fact|Remark|Proposition|"
    r"Inductive|CoInductive|Fixpoint|CoFixpoint|Record|Structure|Class|Instance|"
    r"Axiom|Conjecture|Parameter|Hypothesis|Variable)"
    r"\s+(?P<name>[A-Za-z_][\w']*)"
    r"(?P<typeparams>[^:=]*?)"
    r":(?P<type_signature>[^:=]*?)"
    r"(?::=|\.\s*Proof|\.\s*\bby\b)"
    , re.MULTILINE
)

# Coq dependencies appear as: Require Import Module.Name + module.qualified.references
REQUIRE_IMPORT_PATTERN = re.compile(r"Require\s+(?:Import\s+)?([\w.]+)")
QUALIFIED_REF_PATTERN = re.compile(r"\b([A-Z][\w']*(?:\.[A-Za-z_][\w']*)+)\b")


def clone_coq_libraries():
    """Shallow clone Coq libraries."""
    COQ_LOCAL.mkdir(parents=True, exist_ok=True)
    for repo_name, url, _ in COQ_REPOS:
        repo_dir = COQ_LOCAL / repo_name
        if not (repo_dir / ".git").exists():
            print(f"Cloning {repo_name} from {url}")
            subprocess.run(["git", "clone", "--depth", "1", url, str(repo_dir)], check=True)


def parse_coq_file(coq_path):
    """Parse a .v file extracting declaration + dependency records."""
    try:
        text = coq_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"Warning: failed to read {coq_path}: {e}")
        return [], []
    
    # Strip Coq comments (* ... *)
    text_clean = strip_coq_comments(text)
    
    # Extract Require Imports
    requires = REQUIRE_IMPORT_PATTERN.findall(text_clean)
    
    declarations = []
    for m in DECLARATION_PATTERN.finditer(text_clean):
        kind = m.group("kind")
        name = m.group("name")
        type_signature = (m.group("type_signature") or "").strip()[:300]
        
        # Find dependencies in type signature + body
        deps_in_decl = set(QUALIFIED_REF_PATTERN.findall(type_signature))
        # Filter to plausible Coq library references
        deps_filtered = [
            d for d in deps_in_decl
            if d.count(".") >= 1 and not d.startswith(("True", "False", "Type", "Prop", "Set", "Nat"))
        ]
        
        declarations.append({
            "kind": kind,
            "name": name,
            "type_signature": type_signature,
            "dependencies": deps_filtered[:50],
            "source_path": str(coq_path),
        })
    
    return declarations, requires


def strip_coq_comments(text):
    """Remove Coq (* ... *) comments."""
    return re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)


def coq_declaration_to_substrate_atom(decl, repo_name):
    """Convert Coq declaration to substrate atom."""
    name = decl["name"]
    kind = decl["kind"]
    
    # Tier heuristic per Coq kind:
    # T1 = Axiom + Parameter + Hypothesis + Inductive + Record + Class (foundational)
    # T2 = Definition + Theorem + Lemma + Fixpoint (intermediate)
    # T3 = Instance + Corollary + Remark (specific applications)
    tier_map = {
        "Axiom": "T1", "Parameter": "T1", "Hypothesis": "T1", "Variable": "T1",
        "Inductive": "T1", "CoInductive": "T1", "Record": "T1", "Structure": "T1", "Class": "T1",
        "Definition": "T2", "Theorem": "T2", "Lemma": "T2", "Fixpoint": "T2", "CoFixpoint": "T2",
        "Proposition": "T2", "Fact": "T2",
        "Instance": "T3", "Corollary": "T3", "Remark": "T3", "Conjecture": "T3",
    }
    tier = tier_map.get(kind, "T2")
    
    is_axiom_flag = kind in ("Axiom", "Parameter", "Hypothesis", "Variable", "Inductive", "CoInductive",
                              "Record", "Structure", "Class")
    
    # Detect Pi-type (forall) or Sigma-type (exists / { ... | ... }) in type signature
    sig = decl["type_signature"]
    has_pi = bool(re.search(r"\bforall\b", sig))
    has_sigma = bool(re.search(r"\bexists\b|\{[^|]+\|", sig))
    
    return {
        "canonical_name": f"coq_{repo_name}_{name.lower()}",
        "aliases": [name, f"coq_{kind.lower()}_{name}"],
        "tier": tier,
        "partition": "math_foundation::coq_library",
        "science_algebra_category": f"formalized_mathematics::coq::{kind.lower()}",
        "algebra_dict": {
            "kind": kind,
            "name": name,
            "type_signature": sig,
            "source_path": decl["source_path"],
            "source_repo": repo_name,
            "has_pi_type": has_pi,
            "has_sigma_type": has_sigma,
        },
        "is_axiom": is_axiom_flag,
        "serves_capability": [
            "coq_formalized_math",
            "L6_PROOF_validation_coq",
            "dependent_type_theory_substrate",
            "Curry_Howard_substrate_direct",
        ],
        "depends_on": [
            f"coq_{repo_name}_{d.split('.')[-1].lower()}"
            for d in decl["dependencies"]
        ],
        "signature_hint": f"coq_{kind.lower()}",
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
    print("=== Substrate Coq Library Ingest v1 ===")
    
    # Phase 1: Clone
    clone_coq_libraries()
    
    # Phase 2: Parse
    all_atoms = []
    all_edges = []
    
    for repo_name, _, subdir in COQ_REPOS:
        repo_dir = COQ_LOCAL / repo_name
        coq_files = list((repo_dir / subdir).glob("**/*.v")) if (repo_dir / subdir).exists() else list(repo_dir.glob("**/*.v"))
        print(f"Parsing {len(coq_files)} .v files from {repo_name}")
        
        for coq_path in coq_files:
            declarations, requires = parse_coq_file(coq_path)
            for decl in declarations:
                atom = coq_declaration_to_substrate_atom(decl, repo_name)
                all_atoms.append(atom)
                
                for prereq in atom["depends_on"]:
                    all_edges.append({
                        "src": atom["canonical_name"],
                        "dst": prereq,
                        "relation": "DEPENDS_ON",
                        "source": f"coq_dependency_{repo_name}",
                    })
    
    # Phase 3: Shard + write JSONL
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shard_jsonl(all_atoms, "coq_library_atoms_2026", ATOMS_BATCH_SIZE)
    shard_jsonl(all_edges, "coq_library_depends_on_edges_2026", EDGES_BATCH_SIZE)
    
    # Phase 4: Summary
    summary = {
        "atoms_total": len(all_atoms),
        "edges_total": len(all_edges),
        "axiom_atoms": sum(1 for a in all_atoms if a.get("is_axiom")),
        "pi_type_atoms": sum(1 for a in all_atoms if a.get("algebra_dict", {}).get("has_pi_type")),
        "sigma_type_atoms": sum(1 for a in all_atoms if a.get("algebra_dict", {}).get("has_sigma_type")),
        "by_kind": defaultdict(int),
    }
    for a in all_atoms:
        summary["by_kind"][a["algebra_dict"]["kind"]] += 1
    summary["by_kind"] = dict(summary["by_kind"])
    
    summary_path = OUTPUT_DIR / "coq_library_ingest_summary_2026.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    
    pre_reg = {
        "atoms_at_least_50K": len(all_atoms) >= 50000,
        "edges_average_at_least_5": (len(all_edges) / max(1, len(all_atoms))) >= 5.0,
        "pi_type_richness_at_least_20pct": (summary["pi_type_atoms"] / max(1, len(all_atoms))) >= 0.20,
    }
    print(f"Pre-reg checks: {pre_reg}")


if __name__ == "__main__":
    main()
```

## Caveats + iteration plan

1. **Coq syntax real complexity**: Coq's syntax with dependent types + notations + tactics + universe polymorphism is more nuanced than the regex pattern. Real implementation may need:
   - Bootstrap via `coq-serapi` (Coq's serialization library)
   - Or use `serapi-bidirectional` for declaration extraction
   - Mathematical Components has its own SSReflect notation that needs parser support
2. **Cross-validation with substrate BATCH 01-25**:
   - coq_stdlib_Vector → vector_space (BATCH 01)
   - coq_math_comp_groupTheory → group (BATCH 06)
   - coq_stdlib_FunctionalExtensionality → axioms (BATCH 01)
   - coq_compcert_Memory → measure-theoretic atoms (BATCH 10)
3. **Pi/Sigma type richness**: 20pct minimum captures dependent-type density; can refine with more sophisticated parser

## L6-PROOF + Pi/Sigma cross-validation post ingest

- Take 30 random Coq theorems with explicit dependent-type signatures
- Run substrate's substrate_query.py prove + pi + sigma + id-type subcommands
- Pre-reg HARD-PASS >= 65pct (higher than ProofWiki due to formal type information; lower than CHTV-1 because tactic proofs harder to parse)

## Routing

- **Testbed**: pick up skeleton; refine Coq parser per real .v syntax (bootstrap via coq-serapi recommended); ship to remote_cpu_queue
- **Exp-Dev**: PHASE 3 verification post-ingest; 30-theorem L6-PROOF + Pi/Sigma cross-validation
- **Research**: motivation + time substrate primitives BATCH next per priority queue

## LANE B bedrock cells now complete

| Cell | Status | Atoms expected |
|---|---|---|
| CELL 1 Mizar (skeleton shipped earlier) | SKELETON | ~50K formalized theorems |
| CELL 5 OEIS (Testbed shipped) | OPERATIONAL | ~370K math sequences |
| CELL 6 Lean Mathlib (skeleton shipped earlier) | SKELETON | ~80K formalized math |
| CELL 7 ProofWiki (skeleton shipped earlier this cycle) | SKELETON | ~30K theorems + proofs |
| **CELL 8 Coq library (this skeleton)** | SKELETON | ~100K dependent-type proof terms across stdlib + math-comp + CompCert |

Total LANE B bedrock potential: ~630K atoms across 5 cells with EXPLICIT dependency / type information enabling depth-N L6-PROOF chains substrate cannot author manually + Curry-Howard direct mapping via Coq's dependent types.

## Cross-references

- notes/research_to_testbed_CELL_1_MIZAR_INGEST_*.md (CELL 1 predecessor)
- notes/research_to_testbed_CELL_6_LEAN_MATHLIB_*.md (CELL 6 predecessor)
- notes/research_to_testbed_CELL_7_PROOFWIKI_*.md (CELL 7 predecessor; this cycle)
- notes/research_to_testbed_exp_dev_CURRY_HOWARD_PI_SIGMA_*.md (Pi/Sigma extension spec; Coq is direct mapping target)

---

**Testbed:** CELL 8 COQ LIBRARY INGEST PARSER SKELETON tools/substrate_ingest_coq_library_v1.py concrete scaffold ~300 LOC clone coq + math-comp + CompCert + parse .v files Definition/Theorem/Lemma/Inductive/Fixpoint + extract type signatures + Require Import dependencies + detect Pi-types (forall) and Sigma-types (exists) + Q2+Q3 convention + sharded JSONL pre-reg HARD-PASS atoms >= 50K + average 5 edges/atom + Pi-type richness >= 20pct + L6-PROOF + Pi/Sigma cross-validation 30 random Coq theorems >= 65pct + LANE B bedrock complete CELL 1 Mizar + 5 OEIS + 6 Lean Mathlib + 7 ProofWiki + 8 Coq = ~630K atoms potential + USER full-auto overnight continuing.
