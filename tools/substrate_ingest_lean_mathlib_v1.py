"""CELL 6 Lean Mathlib ingest -- LANE B bedrock high USER-goal alignment.

Per Research LANE B coordination (next after Mizar CELL 1). Lean Mathlib = ~80K
formalized math statements with dependent-type-theoretic provenance + import-chain
structure. Maps onto substrate's algebra_dict.statement + DEPENDS_ON via imports +
INSTANCE_OF via class declarations.

Workflow:
  1. Download Mathlib via git clone OR --mathlib-tarball OR --mathlib-dir override
  2. Walk .lean files; extract: theorem/lemma/def declarations, imports, namespace
  3. Build atoms (T2 for theorems, T1 for definitions, axioms tagged) + edges
  4. Output mapper-output schema for downstream adapter + Phase 6 chain

Mathlib's structure (real, current as of 2025):
  Mathlib/Topology/MetricSpace/Basic.lean
    import Mathlib.Topology.UniformSpace.Basic
    namespace MetricSpace
    theorem dist_self (x : alpha) : dist x x = 0 := ...
    def Continuous : ... := ...

Extraction targets:
  - theorem|lemma DECL_NAME (PARAMS) : TYPE := PROOF  -> T2 theorem atom; depends_on PROOF dependencies (best-effort)
  - def DECL_NAME (PARAMS) : TYPE := BODY            -> T1 definition atom
  - axiom DECL_NAME : TYPE                           -> T0 axiom atom (is_axiom=True)
  - import OTHER_MODULE                              -> file-level DEPENDS_ON

NO LLM. NO bge. NO torch. Pure regex + filesystem walk. Heat-safe.
Designed for remote_cpu_queue. Local testbed SMOKE via --smoke.

Pre-reg HARD-PASS:
  - >= 20K atoms extracted
  - >= 50K DEPENDS_ON edges (import-chain + cross-file)
  - >= 100 axioms tagged
"""
from __future__ import annotations
import sys
import re
import json
import time
import argparse
import subprocess
import shutil
from pathlib import Path

MATHLIB_GIT_URL = "https://github.com/leanprover-community/mathlib4.git"
MATHLIB_LOCAL_DIR = Path("data/external/mathlib4")
OUTPUT_DIR = Path("data/substrate_index")
ATOMS_SHARD_SIZE = 5000
EDGES_SHARD_SIZE = 20000


# Lean declaration patterns (Lean 4 / Mathlib 4 syntax).
THEOREM_PATTERN = re.compile(
    r"^(?:protected\s+|private\s+|public\s+)?"
    r"(?P<kind>theorem|lemma)\s+"
    r"(?P<name>[\w.]+)\s+"
    r"(?P<rest>[^\n]+)",
    re.MULTILINE,
)
DEF_PATTERN = re.compile(
    r"^(?:protected\s+|private\s+|public\s+|noncomputable\s+)?"
    r"def\s+(?P<name>[\w.]+)\s+"
    r"(?P<rest>[^\n]+)",
    re.MULTILINE,
)
AXIOM_PATTERN = re.compile(
    r"^axiom\s+(?P<name>[\w.]+)\s*:\s*(?P<type>.+?)$",
    re.MULTILINE,
)
IMPORT_PATTERN = re.compile(r"^import\s+([\w.]+)", re.MULTILINE)
NAMESPACE_PATTERN = re.compile(r"^namespace\s+([\w.]+)", re.MULTILINE)


def parse_lean_file(lean_path: Path) -> dict:
    """Returns dict with theorems / definitions / axioms / imports / namespaces."""
    try:
        text = lean_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"theorems": [], "definitions": [], "axioms": [], "imports": [], "namespaces": []}

    # Strip comments to reduce false matches
    # (Lean uses -- line comments and /- ... -/ block comments)
    text = re.sub(r"--[^\n]*", "", text)
    text = re.sub(r"/-.*?-/", "", text, flags=re.DOTALL)

    namespaces = [m.group(1) for m in NAMESPACE_PATTERN.finditer(text)]
    imports = [m.group(1) for m in IMPORT_PATTERN.finditer(text)]

    theorems = []
    for m in THEOREM_PATTERN.finditer(text):
        theorems.append({
            "name": m.group("name"),
            "kind": m.group("kind"),
            "type_signature": m.group("rest").strip()[:300],
            "file": str(lean_path.relative_to(MATHLIB_LOCAL_DIR)) if MATHLIB_LOCAL_DIR in lean_path.parents else str(lean_path),
            "namespaces": namespaces,
        })

    definitions = []
    for m in DEF_PATTERN.finditer(text):
        definitions.append({
            "name": m.group("name"),
            "type_signature": m.group("rest").strip()[:300],
            "file": str(lean_path.relative_to(MATHLIB_LOCAL_DIR)) if MATHLIB_LOCAL_DIR in lean_path.parents else str(lean_path),
            "namespaces": namespaces,
        })

    axioms = []
    for m in AXIOM_PATTERN.finditer(text):
        axioms.append({
            "name": m.group("name"),
            "type_signature": m.group("type").strip()[:300],
            "file": str(lean_path.relative_to(MATHLIB_LOCAL_DIR)) if MATHLIB_LOCAL_DIR in lean_path.parents else str(lean_path),
        })

    return {
        "theorems": theorems,
        "definitions": definitions,
        "axioms": axioms,
        "imports": imports,
        "namespaces": namespaces,
    }


def _canonical(name: str) -> str:
    """Lean uses dotted hierarchical names; flatten to canonical_name."""
    return "lean_" + re.sub(r"[^A-Za-z0-9]+", "_", name).lower()


def theorem_to_atom(t: dict) -> dict:
    return {
        "canonical_name": _canonical(t["name"]),
        "aliases": [t["name"], f"lean_{t['kind']}_{t['name'].split('.')[-1]}"],
        "tier": "T2",
        "partition": "math_foundation::lean_mathlib",
        "science_algebra_category": f"formalized_mathematics::lean::{t['kind']}",
        "algebra_dict": {
            "kind": t["kind"],
            "name": t["name"],
            "type_signature": t["type_signature"],
            "source_file": t["file"],
            "namespaces": t["namespaces"],
        },
        "is_axiom": False,  # theorems have proofs (assume non-axiom)
        "serves_capability": [
            "substrate_proof_corpus",
            "L6_PROOF_lean_verification",
            "formalized_math_substrate",
            "dependent_type_theory",
        ],
        "depends_on": [],  # imports added at file-level; per-decl deps need elaborator (not extractable from .lean source)
        "signature_hint": "lean_theorem_with_type_signature",
    }


def definition_to_atom(d: dict) -> dict:
    return {
        "canonical_name": _canonical("def_" + d["name"]),
        "aliases": [d["name"]],
        "tier": "T1",
        "partition": "math_foundation::lean_mathlib",
        "science_algebra_category": "formalized_mathematics::lean::definition",
        "algebra_dict": {
            "name": d["name"],
            "type_signature": d["type_signature"],
            "source_file": d["file"],
            "namespaces": d["namespaces"],
        },
        "is_axiom": True,  # definitions are taken as primitives at substrate-ingest tier
        "serves_capability": ["formalized_math_definitions", "dependent_type_theory"],
        "depends_on": [],
        "signature_hint": "lean_definition",
    }


def axiom_to_atom(a: dict) -> dict:
    return {
        "canonical_name": _canonical("axiom_" + a["name"]),
        "aliases": [a["name"]],
        "tier": "T0",
        "partition": "math_foundation::lean_mathlib::axioms",
        "science_algebra_category": "formalized_mathematics::lean::axiom",
        "algebra_dict": {
            "name": a["name"],
            "type_signature": a["type_signature"],
            "source_file": a["file"],
        },
        "is_axiom": True,
        "serves_capability": ["formalized_math_axioms", "L6_PROOF_axiom_leaf", "dependent_type_theory"],
        "depends_on": [],
        "signature_hint": "lean_axiom",
    }


def import_edges(file_atoms: dict, imports_by_file: dict) -> list:
    """Build DEPENDS_ON edges between files via Lean import declarations.

    Lean's `import Mathlib.A.B` -> file Mathlib/A/B.lean. Every theorem/def in the
    importing file has an architectural dependency on the imported module."""
    edges = []
    for src_file, file_data in file_atoms.items():
        imports = imports_by_file.get(src_file, [])
        for imp in imports:
            tgt_file = imp.replace(".", "/") + ".lean"
            for src_atom in file_data:
                # Edge: src_atom DEPENDS_ON the imported module (file-level proxy)
                tgt_proxy = "lean_module_" + re.sub(r"[^A-Za-z0-9]+", "_", imp).lower()
                edges.append({
                    "src": src_atom["canonical_name"],
                    "dst": tgt_proxy,
                    "relation": "DEPENDS_ON",
                    "source": "lean_import_chain",
                })
    return edges


def shard_jsonl(records: list, prefix: str, shard_size: int):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(records), shard_size):
        sid = i // shard_size
        path = OUTPUT_DIR / f"{prefix}_shard_{sid:04d}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for r in records[i:i + shard_size]:
                f.write(json.dumps(r) + "\n")
        print(f"  wrote {path.name} ({len(records[i:i + shard_size])} records)")


def clone_mathlib(target_dir: Path) -> bool:
    if shutil.which("git") is None:
        print("ERROR: git not available; --mathlib-dir override required")
        return False
    if target_dir.exists() and (target_dir / "Mathlib").exists():
        print(f"  using cached clone: {target_dir}")
        return True
    print(f"  cloning {MATHLIB_GIT_URL} -> {target_dir} (depth=1; large ~500MB)")
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["git", "clone", "--depth=1", MATHLIB_GIT_URL, str(target_dir)],
            check=True, timeout=3600,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"ERROR: git clone failed: {e}")
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--smoke", action="store_true",
                    help="Smoke mode: synthetic Lean files; no clone")
    ap.add_argument("--mathlib-dir", type=str, default=None,
                    help="Path to pre-cloned mathlib4 (skips git clone)")
    ap.add_argument("--no-clone", action="store_true",
                    help="Require pre-cloned Mathlib; do not git clone")
    args = ap.parse_args()

    print("=== Lean Mathlib Ingest CELL 6 v1 ===")
    t0 = time.time()

    if args.smoke:
        print("\n[SMOKE MODE] Synthesizing 1 .lean file")
        MATHLIB_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        smoke_path = MATHLIB_LOCAL_DIR / "Mathlib_Smoke.lean"
        smoke_path.write_text(
            "-- Smoke Lean file\n"
            "import Mathlib.Algebra.Group.Basic\n"
            "import Mathlib.Topology.Basic\n"
            "namespace SmokeTest\n"
            "theorem add_zero (x : Real) : x + 0 = x := by simp\n"
            "lemma mul_one (x : Real) : x * 1 = x := by ring\n"
            "def Continuous (f : Real -> Real) : Prop := True\n"
            "axiom choice : forall (a : Type), Nonempty a\n",
            encoding="utf-8",
        )
        scan_root = MATHLIB_LOCAL_DIR
    else:
        if args.mathlib_dir:
            scan_root = Path(args.mathlib_dir)
            if not scan_root.exists():
                print(f"ERROR: --mathlib-dir {scan_root} does not exist")
                sys.exit(2)
        elif args.no_clone:
            scan_root = MATHLIB_LOCAL_DIR
            if not scan_root.exists():
                print(f"ERROR: --no-clone but {scan_root} does not exist")
                sys.exit(2)
        else:
            if not clone_mathlib(MATHLIB_LOCAL_DIR):
                print(f"\nERROR cloning Mathlib. Manual fallback:")
                print(f"  git clone --depth=1 {MATHLIB_GIT_URL} {MATHLIB_LOCAL_DIR}")
                print(f"  then re-run with --no-clone")
                sys.exit(2)
            scan_root = MATHLIB_LOCAL_DIR

    print(f"\nscanning {scan_root} for .lean files...")
    lean_files = sorted(scan_root.glob("**/*.lean"))
    if args.smoke:
        lean_files = lean_files[:10]
    print(f"  {len(lean_files)} .lean files")

    all_theorems, all_definitions, all_axioms = [], [], []
    imports_by_file = {}
    file_atom_index = {}

    for lp in lean_files:
        parsed = parse_lean_file(lp)
        all_theorems.extend(parsed["theorems"])
        all_definitions.extend(parsed["definitions"])
        all_axioms.extend(parsed["axioms"])
        file_key = str(lp)
        imports_by_file[file_key] = parsed["imports"]
        file_atoms = (
            [theorem_to_atom(t) for t in parsed["theorems"]]
            + [definition_to_atom(d) for d in parsed["definitions"]]
            + [axiom_to_atom(a) for a in parsed["axioms"]]
        )
        file_atom_index[file_key] = file_atoms

    print(f"  extracted {len(all_theorems)} theorems, {len(all_definitions)} definitions, {len(all_axioms)} axioms")

    theorem_atoms = [theorem_to_atom(t) for t in all_theorems]
    def_atoms = [definition_to_atom(d) for d in all_definitions]
    ax_atoms = [axiom_to_atom(a) for a in all_axioms]
    all_atoms = theorem_atoms + def_atoms + ax_atoms

    edges = import_edges(file_atom_index, imports_by_file)
    print(f"  derived {len(edges)} import-chain DEPENDS_ON edges")

    print(f"\nsharding outputs...")
    shard_jsonl(all_atoms, "lean_mathlib_atoms", ATOMS_SHARD_SIZE)
    shard_jsonl(edges, "lean_mathlib_edges", EDGES_SHARD_SIZE)

    elapsed = time.time() - t0
    summary = {
        "atoms_total": len(all_atoms),
        "theorem_atoms": len(theorem_atoms),
        "definition_atoms": len(def_atoms),
        "axiom_atoms": len(ax_atoms),
        "edges_total": len(edges),
        "lean_files_scanned": len(lean_files),
        "wall_time_seconds": round(elapsed, 1),
        "smoke_mode": args.smoke,
        "pre_reg_hard_pass": {
            "atoms_at_least_20K": len(all_atoms) >= 20000,
            "edges_at_least_50K": len(edges) >= 50000,
            "axioms_at_least_100": len(ax_atoms) >= 100,
        },
    }
    summary_path = OUTPUT_DIR / "lean_mathlib_ingest_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n=== INGEST SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"\nNext steps (pipeline runner chains the rest):")
    print(f"  python tools/substrate_ingest_pipeline_runner_v1.py \\")
    print(f"      --skip-mapper --skip-merge \\")
    print(f"      --facts-jsonl data/substrate_index/lean_mathlib_atoms_shard_0000.jsonl \\")
    print(f"      --corpus wikidata --partition math_foundation::lean_mathlib \\")
    print(f"      --output-prefix data/substrate_index/lean_mathlib_atoms")
    print(f"  (or run adapter + Phase 6 manually per Mizar CELL 1 instructions)")


if __name__ == "__main__":
    main()
