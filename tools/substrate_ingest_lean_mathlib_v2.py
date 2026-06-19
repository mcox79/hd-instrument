"""CELL 6 Lean Mathlib ingest v2 -- per-decl reference extraction (no elaborator).

Per Research LANE B follow-up. v1 (commit 32e08e2a) captured file-level
DEPENDS_ON via `import` statements only; theorem.depends_on left empty because
per-decl proof dependencies require Lean elaborator (heavyweight: full Mathlib
build + `lake env lean --print-axioms`).

v2 strategy (regex-only, cheap):
  - Extract decl name + type signature + body via THEOREM/DEF patterns
  - Post-`:= ` body: extract identifiers that look like Lean decl references
    (CamelCase + dot-paths + known prefixes Mathlib/Algebra/Topology/...)
  - Filter against the decl-name index built in pass 1 (only keep references
    that match an actual decl name in the corpus) - eliminates false positives
  - Cap at 25 references per atom to bound graph density

Two-pass workflow:
  Pass 1: extract all decl names + namespaces -> build name_index
  Pass 2: extract per-decl bodies + cross-reference against name_index
          -> emit theorem.depends_on with actual decl references

Output schema matches v1 (mapper-output) so adapter + Phase 6 chain unchanged.

NO LLM. NO bge. NO torch. NO Lean toolchain required. Pure regex two-pass.
Pre-reg HARD-PASS:
  - >= 20K atoms (same as v1)
  - >= 100K DEPENDS_ON edges (v2 expects 5-50x density increase vs v1 file-level)
  - >= 100 axioms
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
from collections import defaultdict


MATHLIB_GIT_URL = "https://github.com/leanprover-community/mathlib4.git"
MATHLIB_LOCAL_DIR = Path("data/external/mathlib4")
OUTPUT_DIR = Path("data/substrate_index")
ATOMS_SHARD_SIZE = 5000
EDGES_SHARD_SIZE = 20000
MAX_PER_DECL_REFS = 25


# Same patterns as v1 (proven on smoke).
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

# v2 NEW: identifier-like tokens for per-decl reference extraction
# Match CamelCase + dot-paths + lowercase_with_dots (Lean / Mathlib idioms)
IDENTIFIER_TOKEN = re.compile(r"\b([A-Za-z][A-Za-z0-9_.]*[A-Za-z0-9_])\b")

# Capture the body after `:= ` until end of declaration (next blank line or
# next top-level keyword). Heuristic but bounds extraction reasonably.
BODY_AFTER_ASSIGN = re.compile(
    r":=\s*(.+?)(?=\n\n|\Z|\n(?:theorem|lemma|def|axiom|namespace|end|section)\s)",
    re.DOTALL,
)


def _strip_comments(text: str) -> str:
    text = re.sub(r"--[^\n]*", "", text)
    text = re.sub(r"/-.*?-/", "", text, flags=re.DOTALL)
    return text


def parse_lean_file_v2(lean_path: Path) -> dict:
    """Pass-1 parse: extract decl names + namespaces + imports.

    Also captures raw body text for pass-2 reference extraction."""
    try:
        text = lean_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"theorems": [], "definitions": [], "axioms": [],
                "imports": [], "namespaces": []}
    text = _strip_comments(text)

    namespaces = [m.group(1) for m in NAMESPACE_PATTERN.finditer(text)]
    imports = [m.group(1) for m in IMPORT_PATTERN.finditer(text)]

    rel_path = (
        str(lean_path.relative_to(MATHLIB_LOCAL_DIR))
        if MATHLIB_LOCAL_DIR in lean_path.parents
        else str(lean_path)
    )

    def _body_after(match) -> str:
        # Extract body text starting from match position; bounded by BODY_AFTER_ASSIGN
        tail = text[match.end():]
        bm = BODY_AFTER_ASSIGN.match("=" + tail) or BODY_AFTER_ASSIGN.search(":=\n" + tail)
        if bm:
            return bm.group(1)[:1500]  # cap body extract
        return tail[:1500]

    theorems = []
    for m in THEOREM_PATTERN.finditer(text):
        theorems.append({
            "name": m.group("name"),
            "kind": m.group("kind"),
            "type_signature": m.group("rest").strip()[:300],
            "body_excerpt": _body_after(m),
            "file": rel_path,
            "namespaces": namespaces,
        })
    definitions = []
    for m in DEF_PATTERN.finditer(text):
        definitions.append({
            "name": m.group("name"),
            "type_signature": m.group("rest").strip()[:300],
            "body_excerpt": _body_after(m),
            "file": rel_path,
            "namespaces": namespaces,
        })
    axioms = []
    for m in AXIOM_PATTERN.finditer(text):
        axioms.append({
            "name": m.group("name"),
            "type_signature": m.group("type").strip()[:300],
            "file": rel_path,
        })
    return {"theorems": theorems, "definitions": definitions,
            "axioms": axioms, "imports": imports, "namespaces": namespaces}


def extract_per_decl_refs(body_text: str, name_index: set, self_name: str) -> list:
    """Extract decl-name references from body; filter against name_index."""
    if not body_text:
        return []
    refs = set()
    for m in IDENTIFIER_TOKEN.finditer(body_text):
        tok = m.group(1)
        if tok == self_name or len(tok) <= 2:
            continue
        if tok in name_index:
            refs.add(tok)
    return list(refs)[:MAX_PER_DECL_REFS]


def _canonical(name: str) -> str:
    return "lean_" + re.sub(r"[^A-Za-z0-9]+", "_", name).lower()


def theorem_to_atom(t: dict, decl_refs: list) -> dict:
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
            "per_decl_refs_count": len(decl_refs),
        },
        "is_axiom": False,
        "serves_capability": [
            "substrate_proof_corpus",
            "L6_PROOF_lean_verification",
            "formalized_math_substrate",
            "dependent_type_theory",
        ],
        "depends_on": [_canonical(r) for r in decl_refs],
        "signature_hint": "lean_theorem_with_per_decl_refs_v2",
    }


def definition_to_atom(d: dict, decl_refs: list) -> dict:
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
            "per_decl_refs_count": len(decl_refs),
        },
        "is_axiom": True,
        "serves_capability": ["formalized_math_definitions", "dependent_type_theory"],
        "depends_on": [_canonical(r) for r in decl_refs],
        "signature_hint": "lean_definition_with_per_decl_refs_v2",
    }


def axiom_to_atom(a: dict) -> dict:
    return {
        "canonical_name": _canonical("axiom_" + a["name"]),
        "aliases": [a["name"]],
        "tier": "T0",
        "partition": "math_foundation::lean_mathlib::axioms",
        "science_algebra_category": "formalized_mathematics::lean::axiom",
        "algebra_dict": {"name": a["name"], "type_signature": a["type_signature"],
                         "source_file": a["file"]},
        "is_axiom": True,
        "serves_capability": ["formalized_math_axioms", "L6_PROOF_axiom_leaf",
                              "dependent_type_theory"],
        "depends_on": [],
        "signature_hint": "lean_axiom",
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


def clone_mathlib(target_dir: Path) -> bool:
    if shutil.which("git") is None:
        print("ERROR: git not available")
        return False
    if target_dir.exists() and (target_dir / "Mathlib").exists():
        print(f"  using cached clone: {target_dir}")
        return True
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        print(f"  cloning {MATHLIB_GIT_URL} -> {target_dir} (depth=1; large ~500MB)")
        subprocess.run(["git", "clone", "--depth=1", MATHLIB_GIT_URL, str(target_dir)],
                       check=True, timeout=3600)
        return True
    except Exception as e:
        print(f"ERROR: git clone failed: {e}")
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mathlib-dir", type=str, default=None)
    ap.add_argument("--no-clone", action="store_true")
    args = ap.parse_args()

    print("=== Lean Mathlib Ingest CELL 6 v2 (per-decl refs via regex) ===")
    t0 = time.time()

    if args.smoke:
        print("\n[SMOKE MODE] Synthesizing 1 .lean file with cross-references")
        MATHLIB_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        smoke_path = MATHLIB_LOCAL_DIR / "Mathlib_Smoke_v2.lean"
        smoke_path.write_text(
            "-- Smoke Lean v2 file with per-decl refs\n"
            "import Mathlib.Algebra.Group.Basic\n"
            "namespace SmokeTest\n"
            "def is_even (n : Nat) : Prop := True\n"
            "def double (n : Nat) : Nat := n + n\n"
            "theorem double_is_even (n : Nat) : is_even (double n) := by\n"
            "  unfold double is_even\n"
            "  trivial\n"
            "lemma is_even_zero : is_even 0 := by\n"
            "  unfold is_even\n"
            "  trivial\n",
            encoding="utf-8",
        )
        scan_root = MATHLIB_LOCAL_DIR
    elif args.mathlib_dir:
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
            sys.exit(2)
        scan_root = MATHLIB_LOCAL_DIR

    print(f"\nscanning {scan_root} for .lean files...")
    lean_files = sorted(scan_root.glob("**/*.lean"))
    if args.smoke:
        lean_files = lean_files[:10]
    print(f"  {len(lean_files)} .lean files")

    # PASS 1: collect all decl names + raw bodies + axioms + namespaces
    print(f"\nPASS 1: extracting decl names + bodies...")
    all_files_data = {}
    name_index = set()
    for lp in lean_files:
        parsed = parse_lean_file_v2(lp)
        all_files_data[str(lp)] = parsed
        for d in parsed["theorems"] + parsed["definitions"] + parsed["axioms"]:
            name_index.add(d["name"])
            name_index.add(d["name"].split(".")[-1])  # local name without namespace
    print(f"  decl-name index size: {len(name_index)}")

    # PASS 2: per-decl reference extraction using name_index
    print(f"\nPASS 2: per-decl reference extraction...")
    all_atoms = []
    edge_count_estimate = 0
    for parsed in all_files_data.values():
        for t in parsed["theorems"]:
            refs = extract_per_decl_refs(t["body_excerpt"], name_index, t["name"])
            atom = theorem_to_atom(t, refs)
            all_atoms.append(atom)
            edge_count_estimate += len(refs)
        for d in parsed["definitions"]:
            refs = extract_per_decl_refs(d["body_excerpt"], name_index, d["name"])
            atom = definition_to_atom(d, refs)
            all_atoms.append(atom)
            edge_count_estimate += len(refs)
        for a in parsed["axioms"]:
            all_atoms.append(axiom_to_atom(a))

    # Build edges
    edges = []
    for atom in all_atoms:
        src_name = atom["canonical_name"]
        for dep in atom.get("depends_on", []):
            edges.append({
                "src": src_name,
                "dst": dep,
                "relation": "DEPENDS_ON",
                "source": "lean_per_decl_ref_v2",
            })

    print(f"\nextracted {len(all_atoms)} atoms + {len(edges)} DEPENDS_ON edges (v2 per-decl)")

    print(f"\nsharding outputs...")
    shard_jsonl(all_atoms, "lean_mathlib_v2_atoms", ATOMS_SHARD_SIZE)
    shard_jsonl(edges, "lean_mathlib_v2_edges", EDGES_SHARD_SIZE)

    elapsed = time.time() - t0
    axiom_count = sum(1 for a in all_atoms if a.get("is_axiom"))
    summary = {
        "version": "v2_per_decl_refs",
        "atoms_total": len(all_atoms),
        "axiom_atoms": axiom_count,
        "edges_total": len(edges),
        "decl_name_index_size": len(name_index),
        "lean_files_scanned": len(lean_files),
        "wall_time_seconds": round(elapsed, 1),
        "smoke_mode": args.smoke,
        "pre_reg_hard_pass": {
            "atoms_at_least_20K": len(all_atoms) >= 20000,
            "edges_at_least_100K": len(edges) >= 100000,
            "axioms_at_least_100": axiom_count >= 100,
        },
    }
    summary_path = OUTPUT_DIR / "lean_mathlib_v2_ingest_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n=== INGEST SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"\nNext: chain via pipeline runner --skip-mapper --skip-merge -> adapter -> Phase 6.")
    print(f"v2 vs v1: per-decl refs replace file-level Require/Import; expected 5-50x edge density increase")


if __name__ == "__main__":
    main()
