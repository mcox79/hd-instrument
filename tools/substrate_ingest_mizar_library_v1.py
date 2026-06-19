"""CELL 1 Mizar Mathematical Library ingest -- LANE B bedrock highest USER-goal alignment.

Per research_to_testbed_CELL_1_MIZAR_INGEST_PARSER_SKELETON_*.md (LANE B priority 1
per LANE allocation 60/35/5 ACK). Mizar MML = ~1200+ articles + 50K+ theorems with
EXPLICIT AXIOM DEPENDENCIES; maps directly onto substrate's algebra_dict.axioms +
DEPENDS_ON + is_axiom + CHTV-1 typed-derivation graph.

Workflow:
  1. Download Mizar MML tarball (multiple URL candidates; --mizar-tarball override)
  2. Extract via stdlib tarfile (cross-platform; no tar binary required)
  3. Parse .abs files (theorem statements + citations) + .voc files (axiom primitives)
  4. Emit JSONL atoms in MAPPER-OUTPUT schema (canonical_name + partition + ...)
  5. Compose with substrate_mapper_to_atom_dict_adapter_v1.py to convert to
     Atom.from_dict-compatible form before substrate_evolve_phase6_bulk_jsonl.py

Output:
  data/external/mizar_mml/                            -- downloaded + extracted
  data/substrate_index/mizar_mml_atoms_shard_NNNN.jsonl  -- mapper-shape atoms
  data/substrate_index/mizar_mml_edges_shard_NNNN.jsonl  -- DEPENDS_ON edges
  data/substrate_index/mizar_mml_ingest_summary.json     -- counts + pre-reg verdict

NO LLM. NO bge. NO torch. Pure I/O + text parsing. Heat-safe.
Designed for remote_cpu_queue execution; Testbed local SMOKE only via --smoke.

Pre-reg HARD-PASS:
  - >= 30K atoms extracted
  - >= 100K DEPENDS_ON edges
  - axiom_atoms (citations=0) >= 1000
"""
from __future__ import annotations
import sys
import os
import re
import json
import time
import argparse
import tarfile
import urllib.request
import urllib.error
from pathlib import Path
from collections import defaultdict


# Candidate URLs (Mizar mirrors change; try in order).
MIZAR_MML_URL_CANDIDATES = [
    "http://mizar.uwb.edu.pl/~softadm/mml.tar.gz",
    "http://mizar.uwb.edu.pl/~mizar/mml.tar.gz",
    "https://github.com/MizarProject/mml/archive/refs/heads/master.tar.gz",
]

MIZAR_LOCAL_DIR = Path("data/external/mizar_mml")
OUTPUT_DIR = Path("data/substrate_index")
ATOMS_SHARD_SIZE = 5000
EDGES_SHARD_SIZE = 20000

USER_AGENT = "substrate-ingest-mizar-cell-1/1.0 (academic research)"


def download_with_user_agent(url: str, dest: Path) -> bool:
    """Download with User-Agent (some mirrors block default urllib)."""
    print(f"  trying URL: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=120) as resp:
            total = int(resp.headers.get("Content-Length", 0)) or None
            with open(dest, "wb") as f:
                downloaded = 0
                t0 = time.time()
                while chunk := resp.read(1024 * 256):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total and downloaded % (1024 * 1024 * 10) < 256 * 1024:
                        pct = 100 * downloaded / total
                        rate = downloaded / max(time.time() - t0, 0.01) / 1024 / 1024
                        print(f"    {pct:.1f}% ({downloaded/1024/1024:.0f}MB / {total/1024/1024:.0f}MB; {rate:.1f}MB/s)")
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        print(f"  FAILED: {e}")
        return False


def download_mizar_mml(override_tarball: Path | None = None) -> Path:
    """Locate or download Mizar MML tarball. Returns extracted directory path."""
    MIZAR_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    if override_tarball is not None and override_tarball.exists():
        tarball = override_tarball
        print(f"using user-supplied tarball: {tarball}")
    else:
        tarball = MIZAR_LOCAL_DIR / "mml.tar.gz"
        if not tarball.exists() or tarball.stat().st_size < 1024:
            print(f"downloading Mizar MML...")
            success = False
            for url in MIZAR_MML_URL_CANDIDATES:
                if download_with_user_agent(url, tarball):
                    success = True
                    break
            if not success:
                raise RuntimeError(
                    f"all {len(MIZAR_MML_URL_CANDIDATES)} URL candidates failed. "
                    f"Download manually + use --mizar-tarball PATH"
                )
        else:
            print(f"  using cached tarball: {tarball}")

    extracted_marker = MIZAR_LOCAL_DIR / ".extracted"
    if not extracted_marker.exists():
        print(f"extracting {tarball} -> {MIZAR_LOCAL_DIR} (cross-platform tarfile)...")
        with tarfile.open(tarball, "r:gz") as tf:
            tf.extractall(MIZAR_LOCAL_DIR)
        extracted_marker.touch()
    else:
        print(f"  using cached extraction")
    return MIZAR_LOCAL_DIR


# Mizar .abs file theorem record pattern.
# Real Mizar formats vary; this is a starter pattern matching the common forms.
THEOREM_PATTERN = re.compile(
    r"theorem\s*::\s*(?P<article>[\w_]+)\s*:\s*(?P<id>\d+)\s*"
    r"(?P<statement>.+?)\s*"
    r"(?:by\s+(?P<citations>[\w:,.\s]+);|;)",
    re.MULTILINE | re.DOTALL,
)

DEFINITION_PATTERN = re.compile(
    r"definition\s*::\s*(?P<article>[\w_]+)\s*:\s*(?P<id>\d+)\s*"
    r"(?P<statement>.+?)\s*;",
    re.MULTILINE | re.DOTALL,
)

VOC_PATTERN = re.compile(r"^([MORSVKLG])(\S+)\s*$", re.MULTILINE)
VOC_TYPE = {
    "M": "mode", "O": "operator", "R": "relation", "S": "structure",
    "V": "selector", "K": "constructor", "L": "literal", "G": "group",
}


def parse_mizar_abs_file(abs_path: Path) -> tuple:
    """Returns (theorems, definitions) lists from one .abs file."""
    try:
        text = abs_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return [], []
    theorems = []
    for m in THEOREM_PATTERN.finditer(text):
        cite_str = m.group("citations") or ""
        citations = [c.strip() for c in re.split(r"[,\s]+", cite_str) if c.strip() and ":" in c]
        theorems.append({
            "article": m.group("article"),
            "id": m.group("id"),
            "statement": m.group("statement").strip()[:400],
            "citations": citations,
        })
    definitions = []
    for m in DEFINITION_PATTERN.finditer(text):
        definitions.append({
            "article": m.group("article"),
            "id": m.group("id"),
            "statement": m.group("statement").strip()[:400],
        })
    return theorems, definitions


def parse_mizar_voc_file(voc_path: Path) -> list:
    try:
        text = voc_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    out = []
    for m in VOC_PATTERN.finditer(text):
        out.append({
            "type": VOC_TYPE.get(m.group(1), "unknown"),
            "symbol": m.group(2),
            "article": voc_path.stem,
        })
    return out


def theorem_to_atom(t: dict) -> dict:
    is_axiom_local = len(t["citations"]) == 0
    return {
        "canonical_name": f"mizar_{t['article'].lower()}_{t['id']}",
        "aliases": [f"{t['article']}:{t['id']}"],
        "tier": "T2",
        "partition": "math_foundation::mizar_mml",
        "science_algebra_category": "formalized_mathematics::mizar::theorem",
        "algebra_dict": {
            "statement": t["statement"],
            "axioms": t["citations"],
            "source_article": t["article"],
            "source_id": t["id"],
        },
        "is_axiom": is_axiom_local,
        "serves_capability": [
            "substrate_proof_corpus",
            "L6_PROOF_mizar_verification",
            "formalized_math_substrate",
        ],
        "depends_on": [
            f"mizar_{c.split(':')[0].lower()}_{c.split(':')[1]}"
            for c in t["citations"]
            if ":" in c
        ],
        "signature_hint": "mizar_theorem_with_citation_chain",
    }


def definition_to_atom(d: dict) -> dict:
    return {
        "canonical_name": f"mizar_def_{d['article'].lower()}_{d['id']}",
        "aliases": [f"{d['article']}_def_{d['id']}"],
        "tier": "T1",
        "partition": "math_foundation::mizar_mml",
        "science_algebra_category": "formalized_mathematics::mizar::definition",
        "algebra_dict": {
            "statement": d["statement"],
            "source_article": d["article"],
            "source_id": d["id"],
        },
        "is_axiom": True,
        "serves_capability": ["formalized_math_definitions"],
        "depends_on": [],
        "signature_hint": "mizar_definition",
    }


def vocab_to_atom(v: dict) -> dict:
    return {
        "canonical_name": f"mizar_voc_{v['article'].lower()}_{v['type']}_{v['symbol']}",
        "aliases": [v["symbol"]],
        "tier": "T0",
        "partition": "math_foundation::mizar_mml::primitives",
        "science_algebra_category": f"formalized_mathematics::mizar::vocabulary::{v['type']}",
        "algebra_dict": {"type": v["type"], "symbol": v["symbol"]},
        "is_axiom": True,
        "serves_capability": ["formalized_math_primitives", "L6_PROOF_axiom_leaf"],
        "depends_on": [],
        "signature_hint": f"mizar_primitive_{v['type']}",
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--smoke", action="store_true",
                    help="Smoke mode: parse first 10 files only, no download")
    ap.add_argument("--mizar-tarball", type=str, default=None,
                    help="Path to pre-downloaded Mizar MML tarball (skip auto-download)")
    ap.add_argument("--no-download", action="store_true",
                    help="Require pre-existing data/external/mizar_mml/ directory; do not download")
    args = ap.parse_args()

    print("=== Mizar Mathematical Library Ingest CELL 1 v1 ===")
    t0 = time.time()

    if args.smoke:
        print("\n[SMOKE MODE] Skipping download; will parse <=10 files for schema validation")
        if not MIZAR_LOCAL_DIR.exists():
            print("smoke mode requires data/external/mizar_mml/ to already exist (use --mizar-tarball for full)")
            print("creating synthetic test files...")
            MIZAR_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
            (MIZAR_LOCAL_DIR / "smoke_test.abs").write_text(
                "theorem :: SMOKE:1 for x being Real holds x + 0 = x by VECTSP_1:1, RLVECT_1:def 4;\n"
                "theorem :: SMOKE:2 for x,y being Real holds x*y = y*x;\n"
                "definition :: SMOKE:3 Real := set of real numbers;\n",
                encoding="utf-8",
            )
            (MIZAR_LOCAL_DIR / "smoke_test.voc").write_text(
                "Mreal\nOplus\nRequal\nSring\n",
                encoding="utf-8",
            )
    elif args.no_download:
        if not MIZAR_LOCAL_DIR.exists():
            print(f"ERROR: --no-download but {MIZAR_LOCAL_DIR} does not exist")
            sys.exit(2)
    else:
        override = Path(args.mizar_tarball) if args.mizar_tarball else None
        try:
            download_mizar_mml(override)
        except Exception as e:
            print(f"\nERROR downloading Mizar MML: {e}")
            print("Manual fallback: download mml.tar.gz from http://mizar.uwb.edu.pl/")
            print(f"  then re-run with: --mizar-tarball /path/to/mml.tar.gz")
            sys.exit(2)

    print(f"\nscanning {MIZAR_LOCAL_DIR} for .abs and .voc files...")
    abs_files = sorted(MIZAR_LOCAL_DIR.glob("**/*.abs"))
    voc_files = sorted(MIZAR_LOCAL_DIR.glob("**/*.voc"))
    if args.smoke:
        abs_files = abs_files[:10]
        voc_files = voc_files[:10]
    print(f"  {len(abs_files)} .abs files, {len(voc_files)} .voc files")

    all_theorems, all_definitions, all_vocab = [], [], []
    for ap_ in abs_files:
        ths, defs = parse_mizar_abs_file(ap_)
        all_theorems.extend(ths)
        all_definitions.extend(defs)
    for vp in voc_files:
        all_vocab.extend(parse_mizar_voc_file(vp))
    print(f"  extracted {len(all_theorems)} theorems, {len(all_definitions)} definitions, {len(all_vocab)} vocab")

    theorem_atoms = [theorem_to_atom(t) for t in all_theorems]
    definition_atoms = [definition_to_atom(d) for d in all_definitions]
    vocab_atoms = [vocab_to_atom(v) for v in all_vocab]
    all_atoms = theorem_atoms + definition_atoms + vocab_atoms
    print(f"\nconverted to {len(all_atoms)} substrate atoms (mapper-output schema)")

    edges = []
    for a in theorem_atoms:
        for dep in a["depends_on"]:
            edges.append({
                "src": a["canonical_name"],
                "dst": dep,
                "relation": "DEPENDS_ON",
                "source": "mizar_mml_citation",
            })
    print(f"derived {len(edges)} DEPENDS_ON edges from theorem citations")

    print(f"\nsharding outputs...")
    shard_jsonl(all_atoms, "mizar_mml_atoms", ATOMS_SHARD_SIZE)
    shard_jsonl(edges, "mizar_mml_edges", EDGES_SHARD_SIZE)

    elapsed = time.time() - t0
    axiom_count = sum(1 for a in all_atoms if a.get("is_axiom"))
    summary = {
        "atoms_total": len(all_atoms),
        "theorem_atoms": len(theorem_atoms),
        "definition_atoms": len(definition_atoms),
        "vocab_atoms": len(vocab_atoms),
        "axiom_atoms": axiom_count,
        "edges_total": len(edges),
        "edges_per_theorem_avg": len(edges) / max(1, len(theorem_atoms)),
        "wall_time_seconds": round(elapsed, 1),
        "smoke_mode": args.smoke,
        "pre_reg_hard_pass": {
            "atoms_at_least_30K": len(all_atoms) >= 30000,
            "edges_at_least_100K": len(edges) >= 100000,
            "axioms_at_least_1K": axiom_count >= 1000,
        },
    }
    summary_path = OUTPUT_DIR / "mizar_mml_ingest_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n=== INGEST SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"\nNext steps:")
    print(f"  1. merge shards: cat {OUTPUT_DIR}/mizar_mml_atoms_shard_*.jsonl > mizar_mml_atoms.jsonl")
    print(f"  2. run adapter:  python tools/substrate_mapper_to_atom_dict_adapter_v1.py "
          f"--mapper-jsonl mizar_mml_atoms.jsonl --output mizar_mml_atoms_adapted")
    print(f"  3. phase 6 ingest: python tools/substrate_evolve_phase6_bulk_jsonl.py mizar_mml_atoms_adapted.jsonl")
    print(f"  4. edge ingest: python tools/substrate_ingest_math_batch03_relations.py mizar_mml_atoms_adapted_relations.jsonl")


if __name__ == "__main__":
    main()
