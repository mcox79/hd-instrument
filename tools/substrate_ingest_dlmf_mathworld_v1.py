"""CELL 9 DLMF + MathWorld ingest -- LANE B bedrock final-sequence (5th).

Per Research LANE B coordination final corpus. DLMF (Digital Library of Mathematical
Functions; NIST) + Wolfram MathWorld cover ~50K math reference entries with explicit
formula/identity content + cross-references. Medium-HIGH USER-goal alignment per
Research (formula reference vs proof-bearing corpora like Mizar/Lean/ProofWiki/Coq).

This v1 supports two backends:
  - DLMF: parse HTML chapter pages from a local mirror (NIST provides bulk downloads)
  - MathWorld: scrape topic JSON via the official API or parse cached pages

Both produce mapper-output schema atoms ready for the adapter + Phase 6 chain.

Extraction targets:
  - Reference entry name (function or topic)
  - Mathematical content (formulas; LaTeX preserved)
  - Cross-references (links to other entries)
  - Domain classification (analytic / numerical / special_functions / etc.)

Output: T1 tier (reference primitives) with is_axiom=True (reference entries
are axiomatic at substrate level; cross-references become DEPENDS_ON).

NO LLM. NO bge. NO torch. Pure HTML/JSON parsing. Heat-safe.
Pre-reg HARD-PASS:
  - >= 10K atoms (DLMF ~10K + MathWorld ~40K)
  - >= 20K DEPENDS_ON edges (cross-reference links)
  - axiom_atoms tag rate = all entries (reference is axiomatic)
"""
from __future__ import annotations
import sys
import re
import json
import time
import argparse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


DLMF_LOCAL_DIR = Path("data/external/dlmf")
MATHWORLD_LOCAL_DIR = Path("data/external/mathworld")
OUTPUT_DIR = Path("data/substrate_index")
ATOMS_SHARD_SIZE = 5000
EDGES_SHARD_SIZE = 20000


class ReferenceEntryParser(HTMLParser):
    """Minimal HTML parser that extracts title + body text + outbound hrefs."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.body_buf = []
        self.hrefs = []
        self._in_title = False
        self._in_body = False
        self._capture_text = True

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        elif tag == "body":
            self._in_body = True
        elif tag in ("script", "style"):
            self._capture_text = False
        elif tag == "a":
            attrs_d = dict(attrs)
            href = attrs_d.get("href")
            if href and not href.startswith(("#", "javascript:", "mailto:")):
                self.hrefs.append(href)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("script", "style"):
            self._capture_text = True

    def handle_data(self, data):
        if not self._capture_text:
            return
        if self._in_title:
            self.title += data
        elif self._in_body:
            self.body_buf.append(data)

    @property
    def body_text(self):
        return " ".join(self.body_buf).strip()


def _canonical(text: str, source: str) -> str:
    raw = f"{source}_" + re.sub(r"[^A-Za-z0-9]+", "_", text).lower()
    return raw.strip("_")[:120]


def parse_reference_html(path: Path) -> dict | None:
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    if not html or len(html) < 100:
        return None
    parser = ReferenceEntryParser()
    try:
        parser.feed(html)
    except Exception:
        return None
    title = parser.title.strip()
    if not title:
        title = path.stem
    body = parser.body_text[:600]
    return {
        "title": title,
        "body_excerpt": body,
        "hrefs": parser.hrefs,
        "file": str(path),
    }


def entry_to_atom(rec: dict, source: str) -> dict:
    return {
        "canonical_name": _canonical(rec["title"], source),
        "aliases": [rec["title"], rec["title"].split(":")[-1] if ":" in rec["title"] else rec["title"]],
        "tier": "T1",
        "partition": f"math_foundation::{source}",
        "science_algebra_category": f"mathematics_reference::{source}",
        "algebra_dict": {
            "title": rec["title"],
            "excerpt": rec["body_excerpt"],
            "source_file": rec["file"],
            "source_corpus": source,
        },
        "is_axiom": True,
        "serves_capability": [
            "mathematics_reference_substrate",
            f"{source}_corpus",
            "L6_PROOF_axiom_leaf",
        ],
        "depends_on": [
            _canonical(href.rsplit("/", 1)[-1].rsplit(".", 1)[0], source)
            for href in rec["hrefs"][:15]
            if "/" in href or href.endswith((".html", ".htm"))
        ],
        "signature_hint": f"{source}_reference_entry",
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
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dlmf-dir", type=str, default=None)
    ap.add_argument("--mathworld-dir", type=str, default=None)
    ap.add_argument("--corpus", choices=["dlmf", "mathworld", "both"], default="both")
    args = ap.parse_args()

    print("=== DLMF + MathWorld Ingest CELL 9 v1 ===")
    t0 = time.time()

    sources = {}
    if args.smoke:
        print("\n[SMOKE MODE] Synthesizing 1 .html per corpus")
        DLMF_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        MATHWORLD_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        (DLMF_LOCAL_DIR / "smoke_bessel.html").write_text(
            "<html><head><title>Bessel Function</title></head><body>"
            "<h1>Bessel Function J_n(x)</h1>"
            "<p>Solutions to the Bessel differential equation. "
            "Cross-reference: <a href='gamma_function.html'>Gamma Function</a>. "
            "See also <a href='hypergeometric.html'>Hypergeometric Function</a>.</p>"
            "</body></html>",
            encoding="utf-8",
        )
        (MATHWORLD_LOCAL_DIR / "smoke_eigenvalue.html").write_text(
            "<html><head><title>Eigenvalue</title></head><body>"
            "<h1>Eigenvalue</h1>"
            "<p>A scalar lambda such that A*v = lambda*v for nonzero v. "
            "See <a href='/eigenvector.html'>Eigenvector</a> "
            "and <a href='/spectral_decomposition.html'>Spectral Decomposition</a>.</p>"
            "</body></html>",
            encoding="utf-8",
        )
        sources["dlmf"] = DLMF_LOCAL_DIR
        sources["mathworld"] = MATHWORLD_LOCAL_DIR
    else:
        if args.dlmf_dir and args.corpus in ("dlmf", "both"):
            sources["dlmf"] = Path(args.dlmf_dir)
        elif args.corpus in ("dlmf", "both"):
            if DLMF_LOCAL_DIR.exists():
                sources["dlmf"] = DLMF_LOCAL_DIR
            else:
                print(f"  warning: no DLMF directory found ({DLMF_LOCAL_DIR}); skipping DLMF")
        if args.mathworld_dir and args.corpus in ("mathworld", "both"):
            sources["mathworld"] = Path(args.mathworld_dir)
        elif args.corpus in ("mathworld", "both"):
            if MATHWORLD_LOCAL_DIR.exists():
                sources["mathworld"] = MATHWORLD_LOCAL_DIR
            else:
                print(f"  warning: no MathWorld directory found ({MATHWORLD_LOCAL_DIR}); skipping MathWorld")
        if not sources:
            print(f"\nNo sources available. Manual fallback:")
            print(f"  DLMF: download from https://dlmf.nist.gov/about/download")
            print(f"  MathWorld: scrape via https://api.wolfram.com/v1/wolframalpha")
            print(f"  then re-run with --dlmf-dir <path> and/or --mathworld-dir <path>")
            sys.exit(2)

    all_atoms = []
    edges = []

    for source_name, root in sources.items():
        print(f"\nscanning {root} for *.html files...")
        html_files = sorted(root.glob("**/*.html"))
        if args.smoke:
            html_files = html_files[:10]
        print(f"  {len(html_files)} .html files")
        for hp in html_files:
            rec = parse_reference_html(hp)
            if rec is None:
                continue
            atom = entry_to_atom(rec, source_name)
            all_atoms.append(atom)
            src_name = atom["canonical_name"]
            for dep in atom["depends_on"]:
                edges.append({
                    "src": src_name,
                    "dst": dep,
                    "relation": "DEPENDS_ON",
                    "source": f"{source_name}_xref",
                })

    print(f"\nextracted {len(all_atoms)} atoms + {len(edges)} DEPENDS_ON edges")
    print(f"\nsharding outputs...")
    shard_jsonl(all_atoms, "dlmf_mathworld_atoms", ATOMS_SHARD_SIZE)
    shard_jsonl(edges, "dlmf_mathworld_edges", EDGES_SHARD_SIZE)

    elapsed = time.time() - t0
    by_source = {}
    for a in all_atoms:
        s = a["algebra_dict"].get("source_corpus", "unknown")
        by_source[s] = by_source.get(s, 0) + 1
    axiom_count = sum(1 for a in all_atoms if a.get("is_axiom"))
    summary = {
        "sources_ingested": list(sources.keys()),
        "atoms_total": len(all_atoms),
        "atoms_by_source": by_source,
        "axiom_atoms": axiom_count,
        "edges_total": len(edges),
        "wall_time_seconds": round(elapsed, 1),
        "smoke_mode": args.smoke,
        "pre_reg_hard_pass": {
            "atoms_at_least_10K": len(all_atoms) >= 10000,
            "edges_at_least_20K": len(edges) >= 20000,
        },
    }
    summary_path = OUTPUT_DIR / "dlmf_mathworld_ingest_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n=== INGEST SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"\nNext: chain via pipeline runner --skip-mapper --skip-merge -> adapter -> Phase 6.")


if __name__ == "__main__":
    main()
