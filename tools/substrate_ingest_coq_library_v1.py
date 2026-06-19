"""CELL 8 Coq Standard Library + Mathematical Components ingest -- LANE B bedrock 4th sequence.

Per Research LANE B coordination. Coq library = thousands of theorems with DEPENDENT TYPES;
Mathematical Components (mathcomp) library is the largest Coq-formalized math corpus
(~50K definitions + theorems). Coq's Curry-Howard correspondence makes its corpus
DIRECTLY relevant to substrate's CHTV-1 verifier + L6-PROOF FINDER.

Extracts from .v Coq source files:
  - Theorem/Lemma/Corollary DECL : TYPE. Proof. ... Qed.
  - Definition NAME (args) : TYPE := BODY.
  - Inductive NAME ... := ...
  - Axiom NAME : TYPE.
  - Require Import Module / Require Export Module (file-level deps)

Coq's per-decl proof dependencies require `coqc` + AST extraction (too heavy for
v1); v1 uses file-level Require/Import as DEPENDS_ON proxy + decl signatures
as algebra_dict structure.

NO LLM. NO bge. NO torch. Heat-safe; remote_cpu_queue compatible.
Pre-reg HARD-PASS:
  - >= 10K atoms (Coq stdlib + mathcomp combined)
  - >= 30K DEPENDS_ON edges (Require + Import chains)
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


COQ_REPOS = {
    "mathcomp": "https://github.com/math-comp/math-comp.git",
    "coq_stdlib": "https://github.com/coq/coq.git",  # has theories/ subdir
}
COQ_LOCAL_DIR = Path("data/external/coq_corpus")
OUTPUT_DIR = Path("data/substrate_index")
ATOMS_SHARD_SIZE = 5000
EDGES_SHARD_SIZE = 20000


# Coq declaration patterns (Coq 8.x syntax).
THEOREM_PATTERN = re.compile(
    r"^(?P<kind>Theorem|Lemma|Corollary|Proposition|Fact|Remark)\s+"
    r"(?P<name>\w+)\s+"
    r"(?P<rest>[^.]+)\.",
    re.MULTILINE,
)
DEF_PATTERN = re.compile(
    r"^Definition\s+(?P<name>\w+)\s+"
    r"(?P<rest>[^.]+)\.",
    re.MULTILINE,
)
INDUCTIVE_PATTERN = re.compile(
    r"^Inductive\s+(?P<name>\w+)\s+"
    r"(?P<rest>[^.]+)\.",
    re.MULTILINE,
)
AXIOM_PATTERN = re.compile(
    r"^Axiom\s+(?P<name>\w+)\s*:\s*(?P<type>.+?)\.",
    re.MULTILINE,
)
REQUIRE_PATTERN = re.compile(
    r"^(?:From\s+\S+\s+)?Require\s+(?:Import|Export)\s+([\w\s.]+?)\.",
    re.MULTILINE,
)


def _canonical(name: str, source: str = "") -> str:
    raw = f"coq_{source}_{name}" if source else f"coq_{name}"
    return re.sub(r"[^A-Za-z0-9]+", "_", raw).lower()


def parse_coq_file(coq_path: Path) -> dict:
    try:
        text = coq_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"theorems": [], "definitions": [], "inductives": [], "axioms": [], "requires": []}
    # Strip comments: (* ... *) nested but stdlib uses single-level; line-only fallback.
    text = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)

    theorems = [
        {"kind": m.group("kind"), "name": m.group("name"),
         "type_signature": m.group("rest").strip()[:300], "file": str(coq_path)}
        for m in THEOREM_PATTERN.finditer(text)
    ]
    definitions = [
        {"name": m.group("name"),
         "type_signature": m.group("rest").strip()[:300], "file": str(coq_path)}
        for m in DEF_PATTERN.finditer(text)
    ]
    inductives = [
        {"name": m.group("name"),
         "type_signature": m.group("rest").strip()[:300], "file": str(coq_path)}
        for m in INDUCTIVE_PATTERN.finditer(text)
    ]
    axioms = [
        {"name": m.group("name"), "type_signature": m.group("type").strip()[:300],
         "file": str(coq_path)}
        for m in AXIOM_PATTERN.finditer(text)
    ]
    requires = []
    for m in REQUIRE_PATTERN.finditer(text):
        modules = re.split(r"[\s.]+", m.group(1).strip())
        requires.extend(mod for mod in modules if mod)
    return {
        "theorems": theorems,
        "definitions": definitions,
        "inductives": inductives,
        "axioms": axioms,
        "requires": requires,
    }


def theorem_to_atom(t: dict, src: str) -> dict:
    return {
        "canonical_name": _canonical(t["name"], src),
        "aliases": [t["name"], f"coq_{t['kind'].lower()}_{t['name']}"],
        "tier": "T2",
        "partition": f"math_foundation::coq::{src}",
        "science_algebra_category": f"formalized_mathematics::coq::{t['kind'].lower()}",
        "algebra_dict": {
            "kind": t["kind"],
            "name": t["name"],
            "type_signature": t["type_signature"],
            "source_file": t["file"],
            "library": src,
        },
        "is_axiom": False,
        "serves_capability": [
            "substrate_proof_corpus",
            "L6_PROOF_coq_verification",
            "formalized_math_substrate",
            "dependent_type_theory",
            "curry_howard_correspondence",
        ],
        "depends_on": [],
        "signature_hint": "coq_theorem_with_dependent_type",
    }


def definition_to_atom(d: dict, src: str) -> dict:
    return {
        "canonical_name": _canonical("def_" + d["name"], src),
        "aliases": [d["name"]],
        "tier": "T1",
        "partition": f"math_foundation::coq::{src}",
        "science_algebra_category": f"formalized_mathematics::coq::definition",
        "algebra_dict": {
            "name": d["name"],
            "type_signature": d["type_signature"],
            "source_file": d["file"],
            "library": src,
        },
        "is_axiom": True,
        "serves_capability": ["formalized_math_definitions", "dependent_type_theory"],
        "depends_on": [],
        "signature_hint": "coq_definition",
    }


def inductive_to_atom(i: dict, src: str) -> dict:
    return {
        "canonical_name": _canonical("ind_" + i["name"], src),
        "aliases": [i["name"]],
        "tier": "T1",
        "partition": f"math_foundation::coq::{src}",
        "science_algebra_category": f"formalized_mathematics::coq::inductive_type",
        "algebra_dict": {
            "name": i["name"],
            "type_signature": i["type_signature"],
            "source_file": i["file"],
            "library": src,
        },
        "is_axiom": True,
        "serves_capability": ["dependent_type_theory", "inductive_type_substrate"],
        "depends_on": [],
        "signature_hint": "coq_inductive_type",
    }


def axiom_to_atom(a: dict, src: str) -> dict:
    return {
        "canonical_name": _canonical("axiom_" + a["name"], src),
        "aliases": [a["name"]],
        "tier": "T0",
        "partition": f"math_foundation::coq::{src}::axioms",
        "science_algebra_category": f"formalized_mathematics::coq::axiom",
        "algebra_dict": {
            "name": a["name"],
            "type_signature": a["type_signature"],
            "source_file": a["file"],
            "library": src,
        },
        "is_axiom": True,
        "serves_capability": ["formalized_math_axioms", "L6_PROOF_axiom_leaf"],
        "depends_on": [],
        "signature_hint": "coq_axiom",
    }


def shard_jsonl(records: list, prefix: str, shard_size: int):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(records), shard_size):
        sid = i // shard_size
        path = OUTPUT_DIR / f"{prefix}_shard_{sid:04d}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for r in records[i:i + shard_size]:
                f.write(json.dumps(r) + "\n")
        print(f"  wrote {path.name} ({len(records[i:i + shard_size])} records)")


def clone_repo(url: str, target: Path) -> bool:
    if shutil.which("git") is None:
        print("ERROR: git not available")
        return False
    if target.exists() and any(target.iterdir()):
        print(f"  using cached: {target}")
        return True
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        print(f"  cloning {url} -> {target} (depth=1)")
        subprocess.run(["git", "clone", "--depth=1", url, str(target)],
                       check=True, timeout=3600)
        return True
    except Exception as e:
        print(f"  FAILED clone: {e}")
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--libraries", nargs="+", default=["mathcomp"],
                    choices=list(COQ_REPOS.keys()),
                    help="Which libraries to ingest (default: mathcomp only)")
    ap.add_argument("--no-clone", action="store_true")
    ap.add_argument("--coq-dir", type=str, default=None,
                    help="Path to pre-cloned Coq library root (skips clone; ingests all .v under it)")
    args = ap.parse_args()

    print("=== Coq Library Ingest CELL 8 v1 ===")
    t0 = time.time()

    if args.smoke:
        print("\n[SMOKE MODE] Synthesizing 1 .v file")
        COQ_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        smoke_path = COQ_LOCAL_DIR / "Smoke.v"
        smoke_path.write_text(
            "(* Coq smoke test *)\n"
            "From mathcomp Require Import ssreflect ssrnat.\n"
            "Require Import Arith Lia.\n"
            "Theorem add_zero_right : forall n : nat, n + 0 = n.\n"
            "Proof. intros. lia. Qed.\n"
            "Lemma mul_comm_nat : forall n m : nat, n * m = m * n.\n"
            "Proof. intros. lia. Qed.\n"
            "Definition is_even (n : nat) : Prop := exists k, n = 2 * k.\n"
            "Inductive list_alpha (A : Type) : Type :=\n"
            "  | nil_alpha : list_alpha A\n"
            "  | cons_alpha : A -> list_alpha A -> list_alpha A.\n"
            "Axiom choice_principle : forall (A : Type), inhabited A.\n",
            encoding="utf-8",
        )
        targets = {"smoke": COQ_LOCAL_DIR}
    elif args.coq_dir:
        targets = {"user": Path(args.coq_dir)}
        for lib, path in targets.items():
            if not path.exists():
                print(f"ERROR: --coq-dir {path} does not exist")
                sys.exit(2)
    else:
        targets = {}
        for lib in args.libraries:
            lib_dir = COQ_LOCAL_DIR / lib
            if args.no_clone:
                if not lib_dir.exists():
                    print(f"ERROR: --no-clone but {lib_dir} does not exist")
                    sys.exit(2)
            else:
                if not clone_repo(COQ_REPOS[lib], lib_dir):
                    print(f"  skipping {lib} (clone failed)")
                    continue
            targets[lib] = lib_dir

    all_atoms = []
    imports_by_file = {}
    file_atoms_by_file = {}

    for lib_name, lib_root in targets.items():
        print(f"\nscanning {lib_root} for .v files...")
        v_files = sorted(lib_root.glob("**/*.v"))
        if args.smoke:
            v_files = v_files[:10]
        print(f"  {len(v_files)} .v files")
        for vp in v_files:
            parsed = parse_coq_file(vp)
            file_atoms = (
                [theorem_to_atom(t, lib_name) for t in parsed["theorems"]]
                + [definition_to_atom(d, lib_name) for d in parsed["definitions"]]
                + [inductive_to_atom(i, lib_name) for i in parsed["inductives"]]
                + [axiom_to_atom(a, lib_name) for a in parsed["axioms"]]
            )
            file_key = str(vp)
            file_atoms_by_file[file_key] = file_atoms
            imports_by_file[file_key] = parsed["requires"]
            all_atoms.extend(file_atoms)

    # Build Require/Import-based DEPENDS_ON edges
    edges = []
    for file_key, atoms_in_file in file_atoms_by_file.items():
        for req in imports_by_file.get(file_key, []):
            proxy = "coq_module_" + re.sub(r"[^A-Za-z0-9]+", "_", req).lower()
            for atom in atoms_in_file:
                edges.append({
                    "src": atom["canonical_name"],
                    "dst": proxy,
                    "relation": "DEPENDS_ON",
                    "source": "coq_require_import",
                })

    print(f"\nextracted {len(all_atoms)} atoms + {len(edges)} DEPENDS_ON edges")
    print(f"\nsharding outputs...")
    shard_jsonl(all_atoms, "coq_library_atoms", ATOMS_SHARD_SIZE)
    shard_jsonl(edges, "coq_library_edges", EDGES_SHARD_SIZE)

    elapsed = time.time() - t0
    kind_counts = {}
    for a in all_atoms:
        k = a["algebra_dict"].get("kind") or a["signature_hint"].split("_")[1]
        kind_counts[k] = kind_counts.get(k, 0) + 1
    axiom_count = sum(1 for a in all_atoms if a.get("is_axiom"))
    summary = {
        "libraries_ingested": list(targets.keys()),
        "atoms_total": len(all_atoms),
        "kind_counts": kind_counts,
        "axiom_atoms": axiom_count,
        "edges_total": len(edges),
        "wall_time_seconds": round(elapsed, 1),
        "smoke_mode": args.smoke,
        "pre_reg_hard_pass": {
            "atoms_at_least_10K": len(all_atoms) >= 10000,
            "edges_at_least_30K": len(edges) >= 30000,
            "axioms_at_least_100": axiom_count >= 100,
        },
    }
    summary_path = OUTPUT_DIR / "coq_library_ingest_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n=== INGEST SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"\nNext: chain via pipeline runner --skip-mapper --skip-merge -> adapter -> Phase 6.")


if __name__ == "__main__":
    main()
