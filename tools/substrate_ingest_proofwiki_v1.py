"""CELL 7 ProofWiki ingest -- LANE B bedrock high USER-goal alignment (3rd in sequence).

Per Research LANE B coordination. ProofWiki = ~30K mathematical proofs with explicit
proof-step structure + cross-reference links between proofs. Per-proof page format:
  - Theorem statement
  - Proof body (steps cite other proofs/definitions/axioms)
  - "Sources" section
  - "Also see" / "Linked from" sections

ProofWiki publishes XML dumps via MediaWiki export. Workflow:
  1. Download XML dump (or --xml-dump override)
  2. Parse <page> entries with namespace=0 (main content)
  3. Extract theorem statement + proof + linked-proofs from wikitext
  4. Emit MAPPER-OUTPUT schema atoms + DEPENDS_ON edges from internal links
  5. Compose with pipeline runner via --skip-mapper

ProofWiki wikitext patterns:
  == Theorem ==           (theorem statement section header)
  == Proof ==             (proof section header)
  [[<other-page>]]        (internal link; potential DEPENDS_ON)
  {{:<other-page>}}       (template inclusion; strong DEPENDS_ON)
  == Sources ==           (citation list)

This v1 uses a simplified single-pass regex parser; production ProofWiki ingest
would benefit from `wikitextparser` library but stdlib-only works for the
structural-extraction we need.

NO LLM. NO bge. NO torch. Pure XML + regex. Heat-safe.
Pre-reg HARD-PASS:
  - >= 15K atoms extracted (ProofWiki has ~30K pages; not all are theorems)
  - >= 30K DEPENDS_ON edges (proof-citation links)
  - axioms tagged where "axiom" or "definition" namespace detected
"""
from __future__ import annotations
import sys
import re
import json
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path
import xml.etree.ElementTree as ET


# ProofWiki dump URL candidates (real-world URLs change; multiple fallbacks).
PROOFWIKI_DUMP_URL_CANDIDATES = [
    "https://proofwiki.org/wiki/Special:Export",  # not a direct dump but page; can be used per page
    "https://dumps.wikimedia.org/proofwiki/latest/proofwiki-latest-pages-articles.xml.bz2",
    # local backup approach: assume user provides --xml-dump
]

PROOFWIKI_LOCAL_DIR = Path("data/external/proofwiki")
OUTPUT_DIR = Path("data/substrate_index")
ATOMS_SHARD_SIZE = 5000
EDGES_SHARD_SIZE = 20000
USER_AGENT = "substrate-ingest-proofwiki-cell-7/1.0 (academic research)"

# MediaWiki XML namespace
MW_NS = "{http://www.mediawiki.org/xml/export-0.10/}"


# Wikitext extraction patterns
THEOREM_SECTION_PATTERN = re.compile(r"==\s*Theorem\s*==\s*\n(.+?)(?=\n==|\Z)", re.DOTALL)
PROOF_SECTION_PATTERN = re.compile(r"==\s*Proof.*?==\s*\n(.+?)(?=\n==|\Z)", re.DOTALL)
DEFINITION_SECTION_PATTERN = re.compile(r"==\s*Definition\s*==\s*\n(.+?)(?=\n==|\Z)", re.DOTALL)
AXIOM_SECTION_PATTERN = re.compile(r"==\s*Axiom\s*==\s*\n(.+?)(?=\n==|\Z)", re.DOTALL)
INTERNAL_LINK_PATTERN = re.compile(r"\[\[([^\]|#]+?)(?:\|[^\]]*)?\]\]")
TEMPLATE_INCLUDE_PATTERN = re.compile(r"\{\{:([^\}|]+)\}\}")
SOURCES_PATTERN = re.compile(r"==\s*Sources?\s*==\s*\n(.+?)(?=\n==|\Z)", re.DOTALL)


def _canonical_title(title: str) -> str:
    """Convert ProofWiki page title to canonical_name."""
    return "proofwiki_" + re.sub(r"[^A-Za-z0-9]+", "_", title).lower().strip("_")


def _extract_links(text: str) -> set:
    """Extract internal links + template includes as DEPENDS_ON candidates."""
    links = set()
    for m in INTERNAL_LINK_PATTERN.finditer(text):
        target = m.group(1).strip()
        if target and not target.startswith(("File:", "Image:", "Category:", "User:")):
            links.add(target)
    for m in TEMPLATE_INCLUDE_PATTERN.finditer(text):
        links.add(m.group(1).strip())
    return links


def classify_and_extract(title: str, wikitext: str) -> dict | None:
    """Classify the page as theorem / definition / axiom and extract structure.

    Returns dict with: kind, title, statement, proof_text, sources, internal_links.
    Returns None if page is not a recognized math entity."""
    if not wikitext or len(wikitext.strip()) < 50:
        return None

    has_theorem = THEOREM_SECTION_PATTERN.search(wikitext)
    has_proof = PROOF_SECTION_PATTERN.search(wikitext)
    has_definition = DEFINITION_SECTION_PATTERN.search(wikitext)
    has_axiom = AXIOM_SECTION_PATTERN.search(wikitext)

    # Title-based heuristics
    title_lower = title.lower()
    is_definition_page = title.startswith("Definition:") or has_definition
    is_axiom_page = title.startswith("Axiom:") or has_axiom
    is_theorem_page = has_theorem or has_proof or any(
        kw in title_lower for kw in ("theorem", "lemma", "proposition", "corollary")
    )

    kind = None
    if is_axiom_page:
        kind = "axiom"
        body_match = has_axiom
    elif is_definition_page:
        kind = "definition"
        body_match = has_definition
    elif is_theorem_page:
        kind = "theorem"
        body_match = has_theorem
    else:
        return None

    statement = (body_match.group(1).strip() if body_match else wikitext[:400])[:400]
    proof_text = ""
    if has_proof:
        proof_text = has_proof.group(1).strip()[:600]
    sources_text = ""
    s_match = SOURCES_PATTERN.search(wikitext)
    if s_match:
        sources_text = s_match.group(1).strip()[:300]

    links = _extract_links(wikitext)
    # Filter out non-math links by simple heuristic
    math_links = {l for l in links if not l.lower().startswith(("help:", "talk:", "main page"))}

    return {
        "kind": kind,
        "title": title,
        "statement": statement,
        "proof_text": proof_text,
        "sources": sources_text,
        "internal_links": list(math_links),
    }


def record_to_atom(rec: dict) -> dict:
    kind = rec["kind"]
    tier_map = {"theorem": "T2", "definition": "T1", "axiom": "T0"}
    is_axiom_map = {"theorem": False, "definition": True, "axiom": True}
    return {
        "canonical_name": _canonical_title(rec["title"]),
        "aliases": [rec["title"], rec["title"].split(":")[-1] if ":" in rec["title"] else rec["title"]],
        "tier": tier_map[kind],
        "partition": f"math_foundation::proofwiki::{kind}",
        "science_algebra_category": f"formalized_mathematics::proofwiki::{kind}",
        "algebra_dict": {
            "kind": kind,
            "title": rec["title"],
            "statement": rec["statement"],
            "proof_excerpt": rec["proof_text"][:300],
            "sources_excerpt": rec["sources"][:200],
        },
        "is_axiom": is_axiom_map[kind],
        "serves_capability": [
            "substrate_proof_corpus",
            "L6_PROOF_proofwiki_verification",
            "formalized_math_substrate",
            f"proofwiki_{kind}",
        ],
        "depends_on": [_canonical_title(l) for l in rec["internal_links"][:20]],  # cap at 20 links per atom
        "signature_hint": f"proofwiki_{kind}_with_citation_links",
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


def download_proofwiki_dump(dest: Path) -> bool:
    """Try multiple URLs; ProofWiki dump URLs are unstable."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    for url in PROOFWIKI_DUMP_URL_CANDIDATES:
        if url.endswith(":Export"):
            continue  # skip non-direct-dump candidates
        print(f"  trying URL: {url}")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=300) as resp:
                with open(dest, "wb") as f:
                    while chunk := resp.read(1024 * 256):
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"  FAILED: {e}")
            continue
    return False


def parse_dump(xml_path: Path, smoke_limit: int | None = None):
    """Stream-parse MediaWiki XML dump; yield (title, wikitext) tuples."""
    count = 0
    # Use iterparse for streaming (handles GB-scale dumps)
    for event, elem in ET.iterparse(str(xml_path), events=("end",)):
        tag = elem.tag.replace(MW_NS, "")
        if tag != "page":
            continue
        title_el = elem.find(f"{MW_NS}title")
        ns_el = elem.find(f"{MW_NS}ns")
        if ns_el is not None and ns_el.text not in (None, "0", "100", "102", "104"):
            elem.clear()
            continue
        rev = elem.find(f"{MW_NS}revision")
        if rev is None:
            elem.clear()
            continue
        text_el = rev.find(f"{MW_NS}text")
        if title_el is None or text_el is None:
            elem.clear()
            continue
        title = title_el.text or ""
        wikitext = text_el.text or ""
        elem.clear()
        yield title, wikitext
        count += 1
        if smoke_limit and count >= smoke_limit:
            break


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--smoke", action="store_true",
                    help="Smoke: synthetic dump; no download")
    ap.add_argument("--xml-dump", type=str, default=None,
                    help="Path to pre-downloaded ProofWiki XML dump (skips download)")
    ap.add_argument("--no-download", action="store_true",
                    help="Require pre-existing dump; do not download")
    ap.add_argument("--max-pages", type=int, default=None,
                    help="Cap pages processed (smoke / partial-run)")
    args = ap.parse_args()

    print("=== ProofWiki Ingest CELL 7 v1 ===")
    t0 = time.time()

    if args.smoke:
        print("\n[SMOKE MODE] Synthesizing 1 .xml file with 3 sample pages")
        PROOFWIKI_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        smoke_path = PROOFWIKI_LOCAL_DIR / "smoke_dump.xml"
        smoke_path.write_text(
            '<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/">'
            '<page><title>Cauchy-Schwarz Inequality</title><ns>0</ns>'
            '<revision><text>== Theorem ==\nFor inner product space [[Vector Space]], '
            '|inner(u,v)|^2 leq inner(u,u) inner(v,v).\n\n== Proof ==\n'
            'Apply [[Triangle Inequality]] and [[Inner Product Axioms]].\n\n'
            '== Sources ==\nApostol 1969.\n</text></revision></page>'
            '<page><title>Definition:Inner Product</title><ns>0</ns>'
            '<revision><text>== Definition ==\nA symmetric positive-definite bilinear form.\n'
            '[[Vector Space]] structure required.</text></revision></page>'
            '<page><title>Axiom:Zermelo Choice</title><ns>0</ns>'
            '<revision><text>== Axiom ==\nFor any set X of nonempty sets, '
            'there exists a function f selecting one element from each.</text></revision></page>'
            '</mediawiki>',
            encoding="utf-8",
        )
        xml_path = smoke_path
    elif args.xml_dump:
        xml_path = Path(args.xml_dump)
        if not xml_path.exists():
            print(f"ERROR: --xml-dump {xml_path} does not exist")
            sys.exit(2)
    else:
        xml_path = PROOFWIKI_LOCAL_DIR / "proofwiki-latest-pages-articles.xml"
        if not xml_path.exists() and not args.no_download:
            print(f"\ndownloading ProofWiki dump...")
            ok = download_proofwiki_dump(xml_path)
            if not ok:
                print(f"\nERROR: ProofWiki dump candidates all failed.")
                print(f"Manual fallback: download a ProofWiki XML export then:")
                print(f"  python tools/substrate_ingest_proofwiki_v1.py --xml-dump /path/to/dump.xml")
                sys.exit(2)
        if not xml_path.exists():
            print(f"ERROR: --no-download but {xml_path} does not exist")
            sys.exit(2)

    print(f"\nparsing dump: {xml_path}")
    atoms = []
    edges = []
    parse_count = 0
    accept_count = 0
    for title, wikitext in parse_dump(xml_path, smoke_limit=args.max_pages):
        parse_count += 1
        rec = classify_and_extract(title, wikitext)
        if rec is None:
            continue
        accept_count += 1
        atom = record_to_atom(rec)
        atoms.append(atom)
        src_name = atom["canonical_name"]
        for dep in atom["depends_on"]:
            edges.append({
                "src": src_name,
                "dst": dep,
                "relation": "DEPENDS_ON",
                "source": "proofwiki_wikitext_link",
            })

    print(f"  parsed {parse_count} pages, accepted {accept_count} as math entities")
    print(f"  generated {len(atoms)} atoms + {len(edges)} DEPENDS_ON edges")

    print(f"\nsharding outputs...")
    shard_jsonl(atoms, "proofwiki_atoms", ATOMS_SHARD_SIZE)
    shard_jsonl(edges, "proofwiki_edges", EDGES_SHARD_SIZE)

    elapsed = time.time() - t0
    kind_counts = {}
    for a in atoms:
        k = a["algebra_dict"].get("kind", "unknown")
        kind_counts[k] = kind_counts.get(k, 0) + 1
    axiom_count = sum(1 for a in atoms if a.get("is_axiom"))
    summary = {
        "pages_parsed": parse_count,
        "pages_accepted": accept_count,
        "atoms_total": len(atoms),
        "kind_counts": kind_counts,
        "axiom_atoms": axiom_count,
        "edges_total": len(edges),
        "wall_time_seconds": round(elapsed, 1),
        "smoke_mode": args.smoke,
        "pre_reg_hard_pass": {
            "atoms_at_least_15K": len(atoms) >= 15000,
            "edges_at_least_30K": len(edges) >= 30000,
            "axioms_tagged": axiom_count >= 100,
        },
    }
    summary_path = OUTPUT_DIR / "proofwiki_ingest_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n=== INGEST SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"\nNext: chain via pipeline runner (--skip-mapper --skip-merge), then adapter + Phase 6.")


if __name__ == "__main__":
    main()
