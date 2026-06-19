# Research -> Testbed: CELL 7 ProofWiki ingest parser SKELETON -- substrate_ingest_proofwiki_v1.py -- LANE B bedrock priority

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight; per WHILE-USER-AWAY L4 priority queue + diversification rule applied)

## Intuitive framing

ProofWiki is "the Wikipedia of mathematical proofs" — community-maintained, ~30K proven theorems with explicit proofs + cross-references. Each proof page shows: theorem statement + proof step by step + which other theorems it uses (DEPENDS_ON).

**Why LANE B bedrock priority**: like Mizar + Lean Mathlib + Coq, ProofWiki gives substrate INSTANT access to depth-N proof chains. Unlike Mizar (formal Mizar syntax) and Lean (Lean 4 type theory), ProofWiki uses MediaWiki markup + ~natural language math — easier to parse + closer to human mathematical exposition. Complements the formal libraries.

**Substrate-product positioning at scale**: substrate + ProofWiki + L6-PROOF FINDER = substrate can re-verify ProofWiki's 30K proofs at depth + cross-link them to BATCH 01-25 atoms. LLMs cannot soundly do this (Lean-Copilot literature).

## Skeleton

```python
#!/usr/bin/env python3
"""
tools/substrate_ingest_proofwiki_v1.py

Ingest ProofWiki (proofwiki.org) into substrate.
Output: data/substrate_index/proofwiki_{batch_id}.jsonl

Workflow:
1. Download ProofWiki MediaWiki XML dump: https://proofwiki.org/wiki/Special:Statistics (dump links)
2. Parse XML to extract pages (proofs + theorems + definitions)
3. Per page: extract title + statement + proof + cross-references via [[...]] wiki links
4. Generate JSONL atoms per Q2+Q3 substrate convention
5. Generate DEPENDS_ON edge JSONL from cross-references

Heat: remote_cpu_queue SAFE (no GPU; I/O-bound + XML parsing only).

Pre-reg HARD-PASS:
- >= 20K theorem + proof atoms ingested within 2 days
- Cross-link >= 1K to BATCH 01-25 atoms (e.g. proofwiki_Cauchy-Schwarz_Inequality -> cauchy_schwarz_inequality)
- L6-PROOF cross-validation: substrate proves 30 random ProofWiki theorems correctly via L6-PROOF generalized 6-edge typing context >= 60pct HARD-PASS
- Depth ceiling lift contribution measurable in re-probe
"""
import json
import re
import pathlib
import urllib.request
import gzip
import xml.etree.ElementTree as ET
from collections import defaultdict


PROOFWIKI_DUMP_URL = "https://proofwiki.org/dumps/proofwiki_latest.xml.gz"
PROOFWIKI_LOCAL = pathlib.Path("data/external/proofwiki")
OUTPUT_DIR = pathlib.Path("data/substrate_index")
ATOMS_BATCH_SIZE = 5000
EDGES_BATCH_SIZE = 20000

MEDIAWIKI_NS = "{http://www.mediawiki.org/xml/export-0.10/}"

# Wiki page name categories (heuristic from ProofWiki convention)
THEOREM_PATTERNS = [
    r"^Theorem:",
    r"\bTheorem\b",
    r"\bLemma\b",
    r"\bProposition\b",
    r"\bCorollary\b",
    r"\bResult\b",
]
DEFINITION_PATTERNS = [
    r"^Definition:",
    r"\bDefinition\b",
]
PROOF_PATTERNS = [
    r"^Proof",
    r"/Proof",
]


def download_proofwiki_dump():
    """Download + extract ProofWiki MediaWiki dump."""
    PROOFWIKI_LOCAL.mkdir(parents=True, exist_ok=True)
    dump_path = PROOFWIKI_LOCAL / "proofwiki_latest.xml.gz"
    if not dump_path.exists():
        print(f"Downloading ProofWiki dump from {PROOFWIKI_DUMP_URL}")
        req = urllib.request.Request(PROOFWIKI_DUMP_URL, headers={"User-Agent": "substrate-ingest/1.0"})
        with urllib.request.urlopen(req) as r, open(dump_path, "wb") as f:
            f.write(r.read())
    extracted_path = PROOFWIKI_LOCAL / "proofwiki_latest.xml"
    if not extracted_path.exists():
        print(f"Extracting {dump_path}")
        with gzip.open(dump_path, "rb") as gz, open(extracted_path, "wb") as out:
            out.write(gz.read())
    return extracted_path


def parse_mediawiki_dump(xml_path):
    """Stream-parse MediaWiki XML dump; yield page records."""
    for event, elem in ET.iterparse(xml_path, events=("end",)):
        if elem.tag == f"{MEDIAWIKI_NS}page":
            title_elem = elem.find(f"{MEDIAWIKI_NS}title")
            text_elem = elem.find(f".//{MEDIAWIKI_NS}text")
            if title_elem is not None and text_elem is not None:
                title = title_elem.text or ""
                text = text_elem.text or ""
                yield {"title": title, "text": text}
            elem.clear()


def classify_page(title, text):
    """Classify ProofWiki page as theorem / definition / proof / other."""
    text_head = text[:500] if text else ""
    title_lower = title.lower()
    for pat in THEOREM_PATTERNS:
        if re.search(pat, title, re.IGNORECASE) or re.search(pat, text_head, re.IGNORECASE):
            return "theorem"
    for pat in DEFINITION_PATTERNS:
        if re.search(pat, title, re.IGNORECASE) or re.search(pat, text_head, re.IGNORECASE):
            return "definition"
    for pat in PROOF_PATTERNS:
        if re.search(pat, title, re.IGNORECASE):
            return "proof"
    return "other"


def extract_wiki_links(text):
    """Extract [[...]] wiki links from MediaWiki text; these become DEPENDS_ON edges."""
    if not text: return []
    links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", text)
    # Filter to plausible theorem/definition names (exclude images + categories + external)
    return [
        link.replace(" ", "_")
        for link in links
        if not link.lower().startswith(("file:", "image:", "category:", "http"))
    ]


def proofwiki_page_to_substrate_atom(page, page_type):
    """Convert a ProofWiki page to substrate atom."""
    title = page["title"]
    text = page["text"] or ""
    
    # Tier heuristic:
    # T1 = definition (foundational)
    # T2 = theorem / lemma / proposition (intermediate)
    # T3 = proof / corollary (instance)
    tier_map = {"definition": "T1", "theorem": "T2", "proof": "T3", "other": "T3"}
    tier = tier_map.get(page_type, "T3")
    
    is_axiom_flag = page_type == "definition"
    
    wiki_links = extract_wiki_links(text)
    
    return {
        "canonical_name": f"proofwiki_{title.replace(' ', '_').replace('/', '__').lower()[:200]}",
        "aliases": [title, f"proofwiki_{page_type}_{title[:100]}"],
        "tier": tier,
        "partition": "math_foundation::proofwiki",
        "science_algebra_category": f"formalized_mathematics::proofwiki::{page_type}",
        "algebra_dict": {
            "kind": page_type,
            "title": title,
            "content_snippet": text[:1500],
            "wiki_links_count": len(wiki_links),
        },
        "is_axiom": is_axiom_flag,
        "serves_capability": ["proofwiki_corpus", "L6_PROOF_validation_proofwiki", "math_corpus_breadth"],
        "depends_on": [
            f"proofwiki_{link.replace('/', '__').lower()[:200]}"
            for link in wiki_links[:50]  # cap to avoid edge explosion
        ],
        "signature_hint": f"proofwiki_{page_type}",
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
    print("=== Substrate ProofWiki Ingest v1 ===")
    
    # Phase 1: Download
    xml_path = download_proofwiki_dump()
    print(f"ProofWiki dump at {xml_path}")
    
    # Phase 2: Parse + classify + convert
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    atoms = []
    edges = []
    page_count = 0
    type_counts = defaultdict(int)
    
    for page in parse_mediawiki_dump(xml_path):
        page_count += 1
        page_type = classify_page(page["title"], page["text"])
        type_counts[page_type] += 1
        
        # Skip "other" type pages (categories, talk pages, etc.)
        if page_type == "other":
            continue
        
        atom = proofwiki_page_to_substrate_atom(page, page_type)
        atoms.append(atom)
        
        for prereq in atom["depends_on"]:
            edges.append({
                "src": atom["canonical_name"],
                "dst": prereq,
                "relation": "DEPENDS_ON",
                "source": "proofwiki_wiki_link",
            })
    
    # Phase 3: Shard + write JSONL
    shard_jsonl(atoms, "proofwiki_atoms_2026", ATOMS_BATCH_SIZE)
    shard_jsonl(edges, "proofwiki_depends_on_edges_2026", EDGES_BATCH_SIZE)
    
    # Phase 4: Summary + pre-reg check
    summary = {
        "total_pages": page_count,
        "type_counts": dict(type_counts),
        "atoms_total": len(atoms),
        "edges_total": len(edges),
        "axiom_atoms": sum(1 for a in atoms if a.get("is_axiom")),
    }
    summary_path = OUTPUT_DIR / "proofwiki_ingest_summary_2026.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    
    pre_reg = {
        "atoms_at_least_20K": len(atoms) >= 20000,
        "edges_average_at_least_3": (len(edges) / max(1, len(atoms))) >= 3.0,
    }
    print(f"Pre-reg checks: {pre_reg}")


if __name__ == "__main__":
    main()
```

## Caveats + iteration plan

1. **MediaWiki XML format**: ProofWiki uses MediaWiki dump format. Real implementation needs robust handling of templates, transclusions, math markup ({{Begin Math}}, <math>...</math>), proof step markup (specific to ProofWiki style)
2. **Cross-validation with substrate BATCH 01-25**:
   - proofwiki_cauchy-schwarz_inequality → cauchy_schwarz_inequality (BATCH 05) via SHARES_MATH
   - proofwiki_jensen's_inequality → jensen_inequality (BATCH 03)
   - proofwiki_eckart-young_theorem → eckart_young_mirsky_theorem (BATCH 18)
   - proofwiki_birkhoff_ergodic_theorem → birkhoff_ergodic_theorem (BATCH 24)
3. **Substrate-quality-first**: Testbed verifies first 500 pages before full 30K ingest; Phase-2-light methodology applies

## L6-PROOF cross-validation post ingest

- Take 30 random ProofWiki theorems
- Run substrate's L6-PROOF FINDER on them
- Pre-reg HARD-PASS >=60pct (lower than Mathlib since ProofWiki proofs less formal than Lean 4 types)

## Routing

- **Testbed**: pick up skeleton; refine MediaWiki parser per real dump format (or bootstrap via existing MediaWiki Python parsers like `wikitextparser`); ship to remote_cpu_queue
- **Exp-Dev**: PHASE 3 verification post-ingest; 30-theorem L6-PROOF cross-validation
- **Research**: BATCH 26+ or motivation/time atoms next per priority queue

## Cross-references

- notes/research_to_testbed_CELL_1_MIZAR_INGEST_*.md (CELL 1 Mizar predecessor; similar structure)
- notes/research_to_testbed_CELL_6_LEAN_MATHLIB_*.md (CELL 6 Lean Mathlib predecessor; similar structure)
- notes/research_to_testbed_exp_dev_MATH_SCIENCE_CORPUS_PARALLEL_INGEST_*.md (LANE B coordination)

---

**Testbed:** CELL 7 PROOFWIKI INGEST PARSER SKELETON tools/substrate_ingest_proofwiki_v1.py concrete scaffold ~250 LOC download ProofWiki MediaWiki XML dump + parse pages theorem/lemma/definition/proof classification + extract [[wiki links]] DEPENDS_ON edges + Q2+Q3 convention + sharded JSONL substrate_evolve_phase6_bulk_jsonl.py compatible pre-reg HARD-PASS atoms >= 20K + average 3 edges/atom + cross-link >= 1K to BATCH 01-25 atoms + L6-PROOF cross-validation 30 random theorems >= 60pct + USER full-auto overnight continuing.
