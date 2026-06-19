# Research -> Testbed + Exp-Dev: USER VISION substrate-on-all-knowledge -> LLM-class language mastery -- COMPREHENSIVE INGEST ACCELERATION ROADMAP + recursive substrate-self-improvement loop design + 4 NEW concrete ingest cell skeletons

**From:** Research  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** USER strategic directive "eventually we'll want all knowledge, more or less, on there. Excellent language ability will only come with similar mastery" + prior "sooner we get all the math (and science) ingested + on the substrate the sooner substrate should be able to poll its knowledge base for ways to resolve issues + even self improve + integrate that knowledge into its atoms"

## TL;DR

- USER strategic destination = substrate-on-ALL-knowledge (corpus-scale parity with LLM training corpus to enable comparable language mastery)
- Recursive substrate-self-improvement LOOP design (substrate polls knowledge to resolve issues + integrates back into atoms)
- 5 high-leverage Tier-1 cells (1 already shipped Mizar + 4 NEW here: Semantic Scholar + PubMed + MathOverflow + OEIS + Lean Mathlib)
- Token-scale projection: current ~1M-2M atoms -> Tier-1+2+3 complete = ~50-200M atoms + ~500M-2B edges
- Substrate-product positioning: structural advantages (algebra_dict + DEPENDS_ON + SHARES_MATH + CHTV-1 1.0 precision + L6-PROOF) COMPOUND at scale; LLM categorical gap widens not narrows as corpus grows

## USER vision substrate-product positioning extension

**LLM language mastery thesis**: GPT-4 / Claude / Gemini language ability emerges from training on ~13T tokens (Llama-3) to ~100T+ tokens (rumored frontier). Substrate currently ingested ~0.01-0.1% of all scientific corpus per cycle-187 estimate.

**Substrate matched-mastery thesis**: substrate language ability + reasoning ability + math ability all scale through structured corpus ingest. KEY differentiator: substrate ingests STRUCTURED (entities + axioms + DEPENDS_ON edges + SHARES_MATH bisimulation + CHTV-1 verifiable) where LLMs ingest as flat tokens. At equivalent corpus scale, substrate structural advantages compound:
- LLMs at 13T tokens cannot guarantee CH-P2 = 1.0 (hallucination-inevitability per CHTV-1 finding); substrate ingest at N atoms has 1.0 precision verifier
- LLMs cannot do L6-PROOF backward chaining over their training data; substrate's algebra_dict + DEPENDS_ON enables this categorically
- LLMs cannot prove SHARES_MATH bisimulation between concepts; substrate's coalgebraic categorical foundation does this natively
- LLMs cannot SELF-IMPROVE structurally from their own corpus; substrate's atoms + edges + axioms + cleanup can be RE-INDEXED + RE-WIRED + EXTENDED via internal mechanisms

**At parity scale (substrate ~10-100T atoms-equivalent + LLM-comparable corpus)**: substrate-product positioning gap is NOT narrower; it is CATEGORICALLY WIDER. LLMs have token statistics; substrate has typed-derivation ground truth + L6-PROOF + dependent types + bisimulation.

## RECURSIVE substrate-self-improvement LOOP design

User's stated mechanism: "substrate should be able to poll its knowledge base for ways to resolve issues + even self improve + integrate that knowledge into its atoms"

### Loop architecture (6 stages)

```
Stage 1: ISSUE DETECTION
substrate continuously monitors its own performance: cap_map.md scorecard,
benchmarks, capability axis F1 scores, retrieval quality metrics

Stage 2: ISSUE RESOLUTION via knowledge poll
substrate queries its OWN ingested knowledge for prior art / techniques / fixes:
substrate_query.py find-relevant-knowledge --about <issue>
  -> searches all ingested corpus + algebra + DEPENDS_ON
  -> ranks by SHARES_MATH equivalence + bge cosine + structural depth

Stage 3: HYPOTHESIS FORMULATION
substrate composes candidate fix from polled knowledge using L6-PROOF + Pi/Sigma:
substrate_query.py compose-fix --issue X --candidates K1,K2,...
  -> backward-chains from polled atoms to candidate substrate-internal fix
  -> outputs structured fix-spec (which atoms to add / which edges to rewire / which cleanup parameters to tune)

Stage 4: EMPIRICAL VALIDATION
substrate's exp_dev pattern: ship fix-spec to Testbed verification cell
substrate_query.py verify-fix-spec --spec <fix-spec> --pre-reg <HP_thresholds>
  -> runs verification cell + reports HARD-PASS / HARD-FAIL / MIDDLE

Stage 5: INTEGRATION
substrate atoms updated per verified fix-spec via Phase-2-light + Phase-6 ingest:
- new atoms added (NEW_X_capability + NEW_X_axiom + ...)
- existing edges rewired (DEPENDS_ON + USES + INSTANCE_OF + ...)
- SHARES_MATH edges added per bisimulation discovery
- algebra_dict augmented with new axioms / lemmas

Stage 6: REGRESSION CHECK
substrate runs baseline + new benchmark; if no regression -> commit; if regression -> revert + Stage 3 re-formulate

LOOP back to Stage 1
```

### Loop implementation cells (priority order)

1. **substrate_query.py find-relevant-knowledge** (~150 LOC; uses bge + algebra + DEPENDS_ON walk; SHARES_MATH-aware)
2. **substrate_query.py compose-fix** (~200 LOC; backward-chains from polled atoms via L6-PROOF + Pi/Sigma; outputs structured fix-spec JSON)
3. **substrate_query.py verify-fix-spec** (~100 LOC; ships fix-spec to Testbed verification cell; collects HARD-PASS/HARD-FAIL/MIDDLE verdict)
4. **substrate_query.py integrate-verified-fix** (~150 LOC; Phase-2-light + Phase-6 ingest of new atoms + edges; algebra_dict augmentation)
5. **substrate_query.py regression-baseline** (~100 LOC; cap_map + benchmark scorecard comparison pre/post fix)

Total: ~700 LOC for recursive self-improvement loop. Testbed implementation candidate; gates on L6-PROOF PHASE 2 + Pi/Sigma extension shipping first.

**Pre-reg HARD-PASS for recursive loop**:
- Stage 1-6 end-to-end execute without crash
- 10 issue-resolution loop runs cumulative MACRO improvement >= 0.01 across baseline benchmarks
- Zero regression across cap_map.md scorecard at integration commit
- LLM categorical gap: NO LLM can execute Stage 1-6 with checkable verification at each stage

## Token-scale projection

| Stage | Atoms | Edges | Corpus equivalent |
|---|---|---|---|
| Current substrate Cycle 51 | ~1.7M | ~10M+ | ~0.01-0.1pct of all scientific corpus |
| Post Mizar + Tier-1 NEW (this note) | ~5-10M | ~50-100M | ~0.1-0.5pct |
| Post Tier-1 + Tier-2 complete (~6 months) | ~50-100M | ~500M-1B | ~1-5pct |
| Post Tier-1+2+3 + multi-lingual + multi-domain (12-18 months) | ~200M-1B | ~2-10B | ~10-50pct |
| Substrate-LLM parity scale (3-5 years) | ~10-100B atoms-equivalent | ~100B-1T edges | ~100pct of public scientific + general corpus |

At parity scale, substrate-LLM categorical gap is widest (1.0 precision verifier + L6-PROOF + Curry-Howard at full corpus).

## 4 NEW Tier-1 ingest cell skeletons

### CELL 2 (NEW): Semantic Scholar Open Corpus ingest

**Why**: ~200M papers; biggest gap per cycle-187 strategic note. Multi-disciplinary research corpus with citation graph + author graph + paper-level structured metadata.

**Skeleton**:
```python
# tools/substrate_ingest_semantic_scholar_open_corpus_v1.py
# Semantic Scholar API: https://api.semanticscholar.org/
# Bulk endpoint: https://api.semanticscholar.org/datasets/v1/
# Rate limit: ~100 req/sec API key required (free academic tier)

import requests
import json
from datetime import datetime

S2_BASE = "https://api.semanticscholar.org/datasets/v1"

def stream_s2_papers():
    """Stream Semantic Scholar papers dataset; map to substrate atom format."""
    for paper_batch in iterate_s2_paper_dataset():
        for paper in paper_batch:
            yield {
                "canonical_name": f"s2_{paper['paperId']}",
                "aliases": [paper.get('title', '')[:100], paper.get('externalIds', {}).get('DOI', '')],
                "tier": "T3",
                "partition": "research_history::semantic_scholar",
                "science_algebra_category": classify_s2_paper(paper),
                "algebra_dict": {
                    "title": paper.get('title', '')[:500],
                    "abstract": paper.get('abstract', '')[:2000],
                    "year": paper.get('year'),
                    "venue": paper.get('venue'),
                    "fields_of_study": paper.get('fieldsOfStudy', []),
                },
                "is_axiom": False,
                "serves_capability": ["research_corpus_breadth", "citation_graph_traversal", "field_inference"],
                "depends_on": [f"s2_{ref['paperId']}" for ref in paper.get('references', []) if ref.get('paperId')],
                "signature_hint": "semantic_scholar_paper",
            }

def classify_s2_paper(paper):
    """Map Semantic Scholar fieldsOfStudy to substrate science_algebra_category."""
    fields = paper.get('fieldsOfStudy', [])
    mapping = {
        "Mathematics": "math_foundation::semantic_scholar",
        "Computer Science": "cs_foundation::semantic_scholar",
        "Physics": "physics_foundation::semantic_scholar",
        "Biology": "bio_foundation::semantic_scholar",
        "Medicine": "med_foundation::semantic_scholar",
    }
    for f in fields:
        if f in mapping: return mapping[f]
    return "general_research::semantic_scholar"

# Pre-reg HARD-PASS:
# - >=10M papers ingested within 7 days remote_cpu_queue
# - >=100M citation DEPENDS_ON edges
# - Cross-link to existing arXiv ML 234K via DOI/title match
# - Substrate self-knowledge bench post-ingest: substrate can answer "what is paper X about" with >=95pct accuracy via algebra_dict.abstract
```

**Cost**: ~5 days build + ~7 days streaming ingest (rate-limited). ~10-200M atoms. remote_cpu_queue safe.

### CELL 3 (NEW): PubMed ingest

**Why**: ~35M biomedical abstracts; second-biggest gap. Critical for substrate's biomedical reasoning + cross-domain math/science coverage.

**Skeleton**:
```python
# tools/substrate_ingest_pubmed_v1.py
# NCBI E-utilities: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
# Bulk via FTP: https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/
# Format: PubMed XML (MEDLINE/PubMed format)

import xml.etree.ElementTree as ET
import gzip

PUBMED_FTP = "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/"

def parse_pubmed_xml(xml_path):
    """Parse PubMed XML to substrate atom format."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle") or ""
        abstract = " ".join([a.text for a in article.findall(".//Abstract/AbstractText") if a.text])
        mesh_terms = [m.findtext(".//DescriptorName") for m in article.findall(".//MeshHeading")]
        references = [r.findtext(".//ArticleId[@IdType='pubmed']") for r in article.findall(".//Reference")]
        yield {
            "canonical_name": f"pubmed_{pmid}",
            "aliases": [title[:100]],
            "tier": "T3",
            "partition": "biomedical::pubmed",
            "science_algebra_category": "biomedical_literature::pubmed",
            "algebra_dict": {
                "title": title[:500],
                "abstract": abstract[:2000],
                "mesh_terms": mesh_terms,
            },
            "is_axiom": False,
            "serves_capability": ["biomedical_research_corpus", "mesh_term_classification", "clinical_evidence_substrate"],
            "depends_on": [f"pubmed_{r}" for r in references if r],
            "signature_hint": "pubmed_article",
        }

# Pre-reg HARD-PASS:
# - >=20M articles ingested within 14 days remote_cpu_queue
# - MeSH term coverage >=20K unique terms cross-linked to substrate atoms
# - Substrate biomedical QA bench: >=0.75 r@5 on a 100-question PubMed-derived test
```

**Cost**: ~3 days build + ~14 days ingest. ~20-35M atoms. remote_cpu_queue safe.

### CELL 4 (NEW): MathOverflow + math.SE ingest

**Why**: ~1M Q-A pairs at math research level + math undergraduate-grad level. Direct USER-goal-aligned math reasoning corpus.

**Skeleton**:
```python
# tools/substrate_ingest_mathoverflow_math_se_v1.py
# Stack Exchange data dump: https://archive.org/details/stackexchange
# Format: 7z compressed XML (Posts.xml + Comments.xml + Tags.xml + ...)

import lxml.etree as ET
import py7zr

SITES = ["mathoverflow.net", "math.stackexchange.com"]

def parse_se_posts(posts_xml_path, site_name):
    """Stream Stack Exchange Posts.xml; map to substrate atom format."""
    for event, elem in ET.iterparse(posts_xml_path, events=("end",)):
        if elem.tag != "row": continue
        post_id = elem.get("Id")
        post_type = elem.get("PostTypeId")  # 1 = question, 2 = answer
        title = elem.get("Title", "")
        body = elem.get("Body", "")
        tags = elem.get("Tags", "").strip("<>").split("><") if elem.get("Tags") else []
        parent_id = elem.get("ParentId")  # for answers
        score = int(elem.get("Score", 0))
        yield {
            "canonical_name": f"{site_name}_post_{post_id}",
            "aliases": [title[:100]],
            "tier": "T3",
            "partition": f"math_qa::{site_name}",
            "science_algebra_category": f"math_qa::{site_name}::{'question' if post_type == '1' else 'answer'}",
            "algebra_dict": {
                "title": title[:300],
                "body": body[:3000],
                "tags": tags,
                "score": score,
                "post_type": "question" if post_type == "1" else "answer",
            },
            "is_axiom": False,
            "serves_capability": ["math_qa_corpus", "tag_based_classification", "high_score_math_reasoning"],
            "depends_on": [f"{site_name}_post_{parent_id}"] if parent_id else [],
            "signature_hint": "stackexchange_math_qa",
        }
        elem.clear()

# Pre-reg HARD-PASS:
# - >=500K Q+A ingested across MathOverflow + math.SE within 3 days
# - >=10K unique tag-based DEPENDS_ON edges to BATCH 01-16 algebra atoms
# - Substrate math QA bench: >=0.65 r@5 on a 100-question MathOverflow-derived test
```

**Cost**: ~2 days build + ~3 days ingest. ~500K-1M atoms. remote_cpu_queue safe.

### CELL 5 (NEW): OEIS Online Encyclopedia of Integer Sequences

**Why**: OEIS holds ~370K mathematical sequences with rigorous definitions + cross-references + formulas. Direct cross-reference target for math primitives (BATCH 01-16) + math research corpus (CELL 4).

**Skeleton**:
```python
# tools/substrate_ingest_oeis_v1.py
# OEIS data: https://oeis.org/wiki/Welcome
# Bulk download: https://oeis.org/stripped.gz (sequences only) + https://oeis.org/names.gz

import gzip
import re

OEIS_STRIPPED_URL = "https://oeis.org/stripped.gz"
OEIS_NAMES_URL = "https://oeis.org/names.gz"

def parse_oeis_records():
    """Parse OEIS stripped + names files to substrate atom format."""
    # stripped format: A_id ,sequence_terms...
    # names format: A_id name_description
    sequences = {}
    with gzip.open("data/external/oeis/stripped.gz", "rt") as f:
        for line in f:
            if line.startswith("#"): continue
            parts = line.split(",", 1)
            if len(parts) != 2: continue
            seq_id, terms_str = parts[0].strip(), parts[1].strip()
            sequences[seq_id] = {"terms": [int(t) for t in terms_str.split(",") if t.strip().lstrip("-").isdigit()][:30]}
    with gzip.open("data/external/oeis/names.gz", "rt") as f:
        for line in f:
            if line.startswith("#"): continue
            m = re.match(r"^(A\d+)\s+(.+)$", line.strip())
            if not m: continue
            seq_id, name = m.group(1), m.group(2)
            if seq_id in sequences:
                sequences[seq_id]["name"] = name
    for seq_id, data in sequences.items():
        yield {
            "canonical_name": f"oeis_{seq_id}",
            "aliases": [seq_id, data.get("name", "")[:100]],
            "tier": "T2",
            "partition": "math_foundation::oeis",
            "science_algebra_category": "math_foundation::integer_sequences::oeis",
            "algebra_dict": {
                "oeis_id": seq_id,
                "name": data.get("name", "")[:300],
                "initial_terms": data["terms"][:20],
            },
            "is_axiom": False,
            "serves_capability": ["integer_sequence_recognition", "math_primitive_cross_reference", "OEIS_lookup_substrate"],
            "signature_hint": "integer_sequence",
        }

# Pre-reg HARD-PASS:
# - >=300K sequences ingested within 1 day
# - Cross-link >=5K to BATCH 01-16 math atoms (e.g. fibonacci_gf -> A000045 + central_limit_theorem -> related sequences)
# - Substrate sequence recognition: given first 5 terms of a sequence, substrate identifies OEIS A_id with >=80pct top-5 accuracy
```

**Cost**: ~1 day build + 6h ingest. ~370K atoms. remote_cpu_queue safe.

### CELL 6 (NEW): Lean Mathlib formalized math library

**Why**: ~80K formalized math statements with full proofs in Lean. Cross-validation target for L6-PROOF + CHTV-1; Lean has been the de facto math formalization standard (Polynomial Hierarchy, Number Theory, Analysis all formalized).

**Skeleton**:
```python
# tools/substrate_ingest_lean_mathlib_v1.py
# Lean 4 Mathlib: https://github.com/leanprover-community/mathlib4
# Format: .lean source files (~50K files; ~80K theorems/definitions)

import pathlib
import subprocess
import re

MATHLIB_URL = "https://github.com/leanprover-community/mathlib4.git"
MATHLIB_LOCAL = pathlib.Path("data/external/mathlib4")

def clone_mathlib():
    if not MATHLIB_LOCAL.exists():
        subprocess.run(["git", "clone", "--depth", "1", MATHLIB_URL, str(MATHLIB_LOCAL)], check=True)

def parse_lean_files():
    """Walk Mathlib4 .lean files; extract theorem + definition records."""
    theorem_pattern = re.compile(r"^(?:protected\s+)?(theorem|lemma|def|structure|class|inductive)\s+(\w+)([^:]*):([^:]+):=\s*by", re.MULTILINE)
    for lean_path in MATHLIB_LOCAL.glob("**/*.lean"):
        try:
            text = lean_path.read_text(encoding="utf-8", errors="ignore")
        except Exception: continue
        for m in theorem_pattern.finditer(text):
            kind, name = m.group(1), m.group(2)
            statement = m.group(4).strip()[:500]
            yield {
                "canonical_name": f"mathlib_{name}",
                "aliases": [name],
                "tier": "T2",
                "partition": "math_foundation::mathlib4",
                "science_algebra_category": f"formalized_mathematics::lean::{kind}",
                "algebra_dict": {
                    "name": name,
                    "kind": kind,
                    "statement": statement,
                    "source_path": str(lean_path.relative_to(MATHLIB_LOCAL)),
                },
                "is_axiom": kind in ("structure", "class", "inductive"),
                "serves_capability": ["formalized_math_lean", "L6_PROOF_validation_lean", "type_theory_substrate"],
                "signature_hint": f"lean_{kind}",
            }

# Pre-reg HARD-PASS:
# - >=40K theorems + definitions ingested within 2 days
# - Cross-link >=2K to BATCH 01-16 atoms (e.g. mathlib_Matrix.det -> SVD; mathlib_LinearIndependent -> linear_independence)
# - L6-PROOF cross-validation: substrate proves 50 random Lean lemmas correctly via L6-PROOF generalized typing context >=70pct HARD-PASS
```

**Cost**: ~2 days build + ~2 days ingest. ~80K atoms. remote_cpu_queue safe.

## Priority sequencing for maximum USER-goal acceleration

| Order | Cell | Cost | USER-goal alignment |
|---|---|---|---|
| **NOW** | CELL 1 Mizar (prior note skeleton) | 5 days build + 2 days ingest | 50K formalized theorems + L6-PROOF direct |
| **NOW+1** | CELL 5 OEIS | 1 day build + 6h ingest | 370K math sequences + cross-link BATCH 01-16 |
| **NOW+2** | CELL 6 Lean Mathlib | 2 days build + 2 days ingest | 80K formalized math + L6-PROOF cross-validation |
| **NOW+3** | CELL 4 MathOverflow + math.SE | 2 days build + 3 days ingest | 1M Q-A math reasoning corpus |
| **NOW+4** | CELL 3 PubMed | 3 days build + 14 days ingest | 35M biomedical breadth |
| **NOW+5** | CELL 2 Semantic Scholar | 5 days build + 7 days ingest | 200M cross-discipline research corpus |
| **PARALLEL** | Recursive self-improvement LOOP cells (find-relevant + compose-fix + verify + integrate + regression) | 700 LOC total ~3-5 days build | Substrate becomes self-improving |
| **NEXT** | Tier-2 corpora (nLab + ProofWiki + Coq + Stack Overflow + The Stack + ...) | per cell ~2-5 days each | Domain depth |
| **NEXT** | Tier-3 corpora (DBpedia + YAGO + BabelNet + ORKG + ...) | per cell ~3-7 days each | Structured KG integration |

Total ~30-50 build-days + ~6-8 weeks ingest streaming concurrent. Production-scale substrate corpus achievable within Cycle 52-53 with Testbed + Exp-Dev throughput.

## LFS migration P0.3 BLOCKER

Per multiple prior coordination notes: LFS migration is the production-scale visibility blocker. With CELL 2-6 ingest producing ~50-300M atoms + ~500M-2B edges = many TB of JSONL shards. GitHub 100MB-per-file blocker becomes existential. **LFS migration P0.3 needs user authorization NOW** to unblock production-scale ingest visibility.

## Substrate-product positioning artifact summary

USER vision implementation:
- ALL knowledge on substrate -> matched-mastery LLM-class language ability + math + science
- Recursive self-improvement loop -> substrate becomes self-evolving cognitive architecture
- LLM categorical gaps compound at scale: hallucination-inevitability + no L6-PROOF + no Curry-Howard + no SHARES_MATH bisimulation
- 8d mathematical-foundation pillar already complete (per F4 re-spec; Exp-Dev verify-before-asserting catch)
- CHTV-1 1.0 precision verifier already empirically demonstrated
- 144 T1 algebra atoms BATCH 01-16 corpus precondition shipped
- 5 Tier-1 high-leverage cell skeletons in place (Mizar + OEIS + Lean Mathlib + MathOverflow + math.SE + PubMed + Semantic Scholar)
- Recursive self-improvement loop architecture designed (6 stages + 5 implementation cells)
- 20+ substrate-product positioning artifacts at Cycle 51 close + USER-vision routing

## Routing

- **Testbed**: prioritize LFS migration P0.3 unblock (production blocker); BATCH 01-16 + 15 ingest review; CELL 5 OEIS fastest payback (1 day build + 6h ingest + 370K atoms)
- **Exp-Dev**: heat-aware remote_cpu_queue available + F4 Cell A+B re-spec running; CELL 5 OEIS + CELL 6 Lean Mathlib can be scheduled in parallel with F4
- **Research**: filing this comprehensive note; standing for cell ship verdicts; BATCH 17+ T1 algebra expansion on demand; recursive self-improvement loop implementation specs on demand

## Cross-references

- notes/research_to_testbed_PRODUCTION_SCALE_EXTERNAL_CORPUS_INGEST_*.md (initial Tier-1+2+3 strategy)
- notes/research_CORRECTION_external_corpus_inventory_*.md (substrate state correction)
- notes/research_to_testbed_CELL_1_MIZAR_INGEST_PARSER_SKELETON_*.md (CELL 1 already shipped)
- memory `feedback_research_external_corpus_inventory_requires_grep_git_log_notes_before_asserting_not_built_2026-06-13`
- commit `8484fc7c` (cycle-187 SCIENTIFIC CORPUS INGEST STRATEGIC PRIORITIES)
- memory `substrate-cycle-51-close-HP-v1-0-70-HARD-PASS-macro-0-7013-2-days-early-7-mechanism-classes-2026-06-12`
- memory `substrate-CHTV1-substrate-as-verifier-HARD-PASS-1p0-precision-LLM-categorical-gap-checkable-ground-truth-2026-06-12`

---

**Testbed + Exp-Dev:** USER VISION substrate-on-ALL-knowledge -> LLM-class language mastery + COMPREHENSIVE INGEST ACCELERATION ROADMAP + recursive substrate-self-improvement LOOP design 6 stages 5 implementation cells 700 LOC + 4 NEW Tier-1 cell skeletons CELL 2 Semantic Scholar 200M papers + CELL 3 PubMed 35M abstracts + CELL 4 MathOverflow + math.SE 1M Q-A + CELL 5 OEIS 370K sequences + CELL 6 Lean Mathlib 80K formalized math + priority sequence Mizar OEIS Lean Mathlib MathOverflow PubMed Semantic Scholar + token scale projection current 1.7M atoms ~ 0.01-0.1pct -> Tier-1+2+3 ~10-100B substrate-LLM parity scale + categorical gaps WIDEN at scale + LFS migration P0.3 BLOCKER NOW + 20+ substrate-product positioning artifacts + USER full-auto overnight continuing.
