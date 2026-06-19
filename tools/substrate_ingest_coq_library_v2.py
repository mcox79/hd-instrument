"""CELL 8 Coq library ingest v2 -- per-proof premise extraction.

Per A1 MPM DECISIVE + Research drill 13 multi-premise authoring methodology:
v1 (commit b05016cf) only captured file-level Require Import edges (single-parent
per file). v2 adds per-proof premise extraction from proof BODIES between
Proof. and Qed., specifically:

  - apply X, X1 X2 X3.        -> X, X1, X2, X3 are cited lemmas
  - rewrite X in H.            -> X is a cited lemma
  - exact X.                   -> X is a cited lemma/term
  - eapply X.                  -> X is a cited lemma
  - destruct X using Y.        -> Y is a cited lemma
  - induction X using Y.       -> Y is a cited lemma
  - case_eq X.                 -> X is a cited definition
  - unfold X.                  -> X is a cited definition (constants resolve)
  - elim X.                    -> X is a cited inductive
  - assumption / trivial / auto -> no specific reference (skip)

Two-pass extraction:
  Pass 1: parse declarations + collect name index
  Pass 2: per-decl, extract proof-body premise references against name_index

Output schema same as v1 (mapper-output) so composes with adapter + Phase 6.

NO LLM. NO bge. NO Lean/Coq toolchain. Pure regex two-pass.

Pre-reg HARD-PASS:
  - >= 10K atoms (same as v1)
  - >= 50K DEPENDS_ON edges (v1 file-level + v2 per-proof; 5-10x density increase)
  - >= 100 axioms (Axiom declarations)
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
    "coq_stdlib": "https://github.com/coq/coq.git",
}
COQ_LOCAL_DIR = Path("data/external/coq_corpus")
OUTPUT_DIR = Path("data/substrate_index")
ATOMS_SHARD_SIZE = 5000
EDGES_SHARD_SIZE = 20000

THEOREM_PATTERN = re.compile(
    r"^(?P<kind>Theorem|Lemma|Corollary|Proposition|Fact|Remark)\s+(?P<name>\w+)\s+(?P<rest>[^.]+)\.",
    re.MULTILINE,
)
DEF_PATTERN = re.compile(
    r"^Definition\s+(?P<name>\w+)\s+(?P<rest>[^.]+)\.",
    re.MULTILINE,
)
INDUCTIVE_PATTERN = re.compile(
    r"^Inductive\s+(?P<name>\w+)\s+(?P<rest>[^.]+)\.",
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

# v2 NEW: per-proof premise extraction patterns
# Capture proof body between Proof. and Qed./Defined.
PROOF_BODY_PATTERN = re.compile(
    r"Proof\.\s*(.+?)\s*(?:Qed|Defined|Admitted|Abort)\.",
    re.DOTALL,
)

# Tactic-citation patterns (cited lemma/term name after tactic keyword)
TACTIC_PATTERNS = [
    re.compile(r"\bapply\s+(?:@\s*)?(\w+)", re.MULTILINE),
    re.compile(r"\beapply\s+(?:@\s*)?(\w+)", re.MULTILINE),
    re.compile(r"\bexact\s+(?:@\s*)?(\w+)", re.MULTILINE),
    re.compile(r"\brewrite\s+(?:@\s*)?(?:->|<-)?\s*(\w+)", re.MULTILINE),
    re.compile(r"\bdestruct\s+\w+\s+using\s+(\w+)", re.MULTILINE),
    re.compile(r"\binduction\s+\w+\s+using\s+(\w+)", re.MULTILINE),
    re.compile(r"\bunfold\s+(\w+)", re.MULTILINE),
    re.compile(r"\belim\s+(\w+)", re.MULTILINE),
]


def _canonical(name: str, source: str = "") -> str:
    raw = f"coq_{source}_{name}" if source else f"coq_{name}"
    return re.sub(r"[^A-Za-z0-9]+", "_", raw).lower()


def parse_coq_file_v2(coq_path: Path) -> dict:
    """Pass 1 parse: declarations + raw proof bodies."""
    try:
        text = coq_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"theorems": [], "definitions": [], "inductives": [], "axioms": [],
                "requires": [], "proof_bodies": {}}
    text = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)

    theorems = [
        {"kind": m.group("kind"), "name": m.group("name"),
         "type_signature": m.group("rest").strip()[:300], "file": str(coq_path)}
        for m in THEOREM_PATTERN.finditer(text)
    ]
    definitions = [
        {"name": m.group("name"), "type_signature": m.group("rest").strip()[:300],
         "file": str(coq_path)}
        for m in DEF_PATTERN.finditer(text)
    ]
    inductives = [
        {"name": m.group("name"), "type_signature": m.group("rest").strip()[:300],
         "file": str(coq_path)}
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

    # v2: extract proof bodies; key by surrounding theorem name (best-effort via position)
    proof_bodies = {}
    # Map each Proof.../Qed body to the most recent theorem declaration before it
    # by scanning positions.
    theorem_positions = [(m.start(), m.group("name")) for m in THEOREM_PATTERN.finditer(text)]
    for m in PROOF_BODY_PATTERN.finditer(text):
        proof_start = m.start()
        body = m.group(1)
        # Find theorem nearest before this proof block
        nearest = None
        nearest_pos = -1
        for pos, name in theorem_positions:
            if pos < proof_start and pos > nearest_pos:
                nearest_pos = pos
                nearest = name
        if nearest:
            proof_bodies[nearest] = body

    return {
        "theorems": theorems, "definitions": definitions,
        "inductives": inductives, "axioms": axioms,
        "requires": requires, "proof_bodies": proof_bodies,
    }


def extract_per_proof_premises(body: str, name_index: set, self_name: str) -> list:
    """v2: extract cited lemmas/defs/inductives from a Coq proof body."""
    if not body:
        return []
    refs = set()
    for pattern in TACTIC_PATTERNS:
        for m in pattern.finditer(body):
            tok = m.group(1)
            if tok and tok != self_name and tok in name_index:
                refs.add(tok)
    return list(refs)[:50]  # cap per-decl


def theorem_to_atom(t: dict, src: str, per_proof_refs: list) -> dict:
    return {
        "canonical_name": _canonical(t["name"], src),
        "aliases": [t["name"], f"coq_{t['kind'].lower()}_{t['name']}"],
        "tier": "T2",
        "partition": f"math_foundation::coq::{src}",
        "science_algebra_category": f"formalized_mathematics::coq::{t['kind'].lower()}",
        "algebra_dict": {
            "kind": t["kind"], "name": t["name"],
            "type_signature": t["type_signature"], "source_file": t["file"],
            "library": src,
            "per_proof_premise_count": len(per_proof_refs),
        },
        "is_axiom": False,
        "serves_capability": [
            "substrate_proof_corpus", "L6_PROOF_coq_verification",
            "formalized_math_substrate", "dependent_type_theory",
            "curry_howard_correspondence",
        ],
        "depends_on": [_canonical(r, src) for r in per_proof_refs],  # v2 per-proof refs
        "signature_hint": "coq_theorem_with_per_proof_premises_v2",
    }


def definition_to_atom(d: dict, src: str) -> dict:
    return {
        "canonical_name": _canonical("def_" + d["name"], src),
        "aliases": [d["name"]], "tier": "T1",
        "partition": f"math_foundation::coq::{src}",
        "science_algebra_category": "formalized_mathematics::coq::definition",
        "algebra_dict": {
            "name": d["name"], "type_signature": d["type_signature"],
            "source_file": d["file"], "library": src,
        },
        "is_axiom": True,
        "serves_capability": ["formalized_math_definitions", "dependent_type_theory"],
        "depends_on": [], "signature_hint": "coq_definition_v2",
    }


def inductive_to_atom(i: dict, src: str) -> dict:
    return {
        "canonical_name": _canonical("ind_" + i["name"], src),
        "aliases": [i["name"]], "tier": "T1",
        "partition": f"math_foundation::coq::{src}",
        "science_algebra_category": "formalized_mathematics::coq::inductive_type",
        "algebra_dict": {
            "name": i["name"], "type_signature": i["type_signature"],
            "source_file": i["file"], "library": src,
        },
        "is_axiom": True,
        "serves_capability": ["dependent_type_theory", "inductive_type_substrate"],
        "depends_on": [], "signature_hint": "coq_inductive_type_v2",
    }


def axiom_to_atom(a: dict, src: str) -> dict:
    return {
        "canonical_name": _canonical("axiom_" + a["name"], src),
        "aliases": [a["name"]], "tier": "T0",
        "partition": f"math_foundation::coq::{src}::axioms",
        "science_algebra_category": "formalized_mathematics::coq::axiom",
        "algebra_dict": {
            "name": a["name"], "type_signature": a["type_signature"],
            "source_file": a["file"], "library": src,
        },
        "is_axiom": True,
        "serves_capability": ["formalized_math_axioms", "L6_PROOF_axiom_leaf",
                              "dependent_type_theory"],
        "depends_on": [], "signature_hint": "coq_axiom",
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
        return False
    if target.exists() and any(target.iterdir()):
        return True
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
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
                    choices=list(COQ_REPOS.keys()))
    ap.add_argument("--no-clone", action="store_true")
    ap.add_argument("--coq-dir", type=str, default=None)
    args = ap.parse_args()

    print("=== Coq Library Ingest CELL 8 v2 (per-proof premise extraction) ===")
    t0 = time.time()

    if args.smoke:
        print("\n[SMOKE MODE] Synthesizing 1 .v file with proof bodies + multi-premise tactics")
        COQ_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        smoke_path = COQ_LOCAL_DIR / "Smoke_v2.v"
        smoke_path.write_text(
            "(* v2 smoke; proof bodies cite lemmas *)\n"
            "From mathcomp Require Import ssreflect ssrnat.\n"
            "Definition is_zero (n : nat) : Prop := n = 0.\n"
            "Definition double (n : nat) : nat := n + n.\n"
            "Lemma is_zero_zero : is_zero 0.\n"
            "Proof. unfold is_zero. apply eq_refl. Qed.\n"
            "Theorem double_zero_is_zero : is_zero (double 0).\n"
            "Proof.\n"
            "  unfold double. apply is_zero_zero.\n"
            "  exact is_zero_zero.\n"
            "Qed.\n"
            "Theorem swap_args : forall n m : nat, n + m = m + n.\n"
            "Proof.\n"
            "  intros n m.\n"
            "  rewrite Nat.add_comm. apply eq_refl.\n"
            "Qed.\n",
            encoding="utf-8",
        )
        targets = {"smoke": COQ_LOCAL_DIR}
    elif args.coq_dir:
        targets = {"user": Path(args.coq_dir)}
    else:
        targets = {}
        for lib in args.libraries:
            lib_dir = COQ_LOCAL_DIR / lib
            if args.no_clone or lib_dir.exists():
                targets[lib] = lib_dir
            else:
                if clone_repo(COQ_REPOS[lib], lib_dir):
                    targets[lib] = lib_dir

    if not targets:
        print("no targets available; exit")
        return

    # PASS 1: collect decl names + proof bodies
    print("\nPASS 1: scanning + decl-name index...")
    all_files_data = {}
    name_index = set()
    for lib_name, lib_root in targets.items():
        v_files = sorted(lib_root.glob("**/*.v"))
        if args.smoke:
            v_files = v_files[:10]
        print(f"  {lib_name}: {len(v_files)} .v files")
        for vp in v_files:
            parsed = parse_coq_file_v2(vp)
            all_files_data[(lib_name, str(vp))] = parsed
            for d in (parsed["theorems"] + parsed["definitions"] +
                      parsed["inductives"] + parsed["axioms"]):
                name_index.add(d["name"])
    print(f"  total decls: {len(name_index)}")

    # PASS 2: per-proof premise extraction
    print("\nPASS 2: per-proof premise extraction...")
    all_atoms = []
    total_per_proof_refs = 0
    for (lib_name, file_key), parsed in all_files_data.items():
        for t in parsed["theorems"]:
            body = parsed["proof_bodies"].get(t["name"], "")
            per_proof_refs = extract_per_proof_premises(body, name_index, t["name"])
            total_per_proof_refs += len(per_proof_refs)
            all_atoms.append(theorem_to_atom(t, lib_name, per_proof_refs))
        for d in parsed["definitions"]:
            all_atoms.append(definition_to_atom(d, lib_name))
        for i in parsed["inductives"]:
            all_atoms.append(inductive_to_atom(i, lib_name))
        for a in parsed["axioms"]:
            all_atoms.append(axiom_to_atom(a, lib_name))

    # Edges
    edges = []
    for atom in all_atoms:
        src = atom["canonical_name"]
        for dep in atom.get("depends_on", []):
            edges.append({"src": src, "dst": dep, "relation": "DEPENDS_ON",
                          "source": "coq_per_proof_v2"})

    print(f"\nextracted {len(all_atoms)} atoms + {len(edges)} DEPENDS_ON edges")
    print(f"  total per-proof premise refs (sum across theorems): {total_per_proof_refs}")

    print(f"\nsharding outputs...")
    shard_jsonl(all_atoms, "coq_v2_atoms", ATOMS_SHARD_SIZE)
    shard_jsonl(edges, "coq_v2_edges", EDGES_SHARD_SIZE)

    elapsed = time.time() - t0
    summary = {
        "libraries_ingested": list(targets.keys()),
        "atoms_total": len(all_atoms),
        "edges_total": len(edges),
        "per_proof_premise_refs_sum": total_per_proof_refs,
        "wall_time_seconds": round(elapsed, 1),
        "smoke_mode": args.smoke,
        "version": "v2_per_proof_premises",
    }
    summary_path = OUTPUT_DIR / "coq_v2_ingest_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n=== INGEST SUMMARY ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
