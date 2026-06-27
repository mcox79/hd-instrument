# 5x Research Drill — Barrier 4: Math + Science Formal-Knowledge Ingest

Date: 2026-06-27
Discipline: 2x research drill (broad + narrow); lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis cap 0.50); generic terms only; verify-the-referent for each proposed source (does the API actually exist + is it actually usable today, not just in a paper).

## Executive Summary

ProofWiki is the wrong corpus to anchor a math-ingest path on. Its MediaWiki dump is intermittently unhosted, theorem wikitext is template-heavy (parse-hostile), and the corpus is small (~30k pages). The substrate needs three different things for M3/M4: (1) a STRUCTURED math corpus where each fact has explicit dependencies (so multi-hop reasoning has somewhere to walk); (2) a STRUCTURED science corpus with quantitative properties (so sanity-checks have ground truth); (3) a TOKEN-LEVEL encoding strategy for formula streams that char-trigram cannot deliver. Char-trigram averages over single-character permutations of "sin(x)" and "cos(x)" until they cluster — useless for math identity. Top-3 picks invert ProofWiki's failure mode: Lean4 Mathlib (parser-clean, dependency-graph-native, ~165k theorems), Materials Project API (REST, MIT-licensed, ~150k compounds with calculated properties), and OEIS (~370k sequences, simple flat dump, cross-ref-rich). Encoding: predicate-argument with sub-atom token-stream rather than char-trigram on the whole expression. Total ingest cost for all three: ~12-20 GPU/CPU hours, ~600k atoms, ~3-5M chunks. Substrate-fit ranking is dominated by structured-dependency availability, not corpus size.

## Angle 1 — Pure Math Sources (ProofWiki replacements)

**Lean4 Mathlib (recommended).** ~165k theorems + ~80k definitions in a single Git repo (`leanprover-community/mathlib4`). Every theorem declares its hypotheses + conclusion + which prior lemmas it invokes (`exact?` / `simp` resolved). Parse target: the `.lean` source files directly, OR the compiled `oleans` via `lean --print-deps`. Encoding-fit: each theorem becomes a node, each invoked lemma becomes a typed-edge `USES_LEMMA`; the dependency graph is the corpus. License: Apache 2.0, fully redistributable. Feasibility: highest of any formal-math source because it's actively maintained, monorepo, parseable without server calls.

**OEIS.** ~370k integer sequences with: definition formulas, recurrence relations, cross-references to other sequences, generating functions, related sequences (A-numbers). Bulk download: `https://oeis.org/stripped.gz` (sequence-id → first terms; ~50 MB) + per-sequence detail pages cached locally. Encoding-fit: each sequence is a leaf atom (`SEQUENCE`); formulas are predicate atoms (`FORMULA_OF(seq, expr)`); cross-refs are `RELATED_TO` edges. The cross-ref graph alone is ~3-5M edges and is what makes OEIS valuable for multi-hop ("which sequences satisfy a linear recurrence AND appear in number theory?").

**Stacks Project.** ~7000 pages of formal algebraic geometry in LaTeX, single canonical numbering, dependency tags on every theorem (`\ref{tag-XXXX}` resolved). License: GFDL. Smaller than Mathlib but DENSER cross-reference graph — a single theorem typically cites 10-30 prior tags. Encoding-fit: same predicate-edge model as Mathlib. The Stacks tags give us a flat ID space that's easier to index than Lean's hierarchical namespace.

Encoding-strategy proposal for all three: HD atom = `(theorem_id, statement_chunks, [HYP→lemma_id], [CONCL])`; binding role = predicate-class (hyp / concl / uses / generalizes); filler = lemma-id atom. Char-trigram for natural-language statement text; explicit ID-vector for symbolic references (not char-trigram of the ID string — those collide).

## Angle 2 — Materials Science / Physics Sources

**Materials Project API (recommended).** ~150k inorganic compounds with DFT-calculated band gap, formation energy, density, elastic constants, magnetic moments. REST API at `materialsproject.org/api`, requires free key, MIT-licensed data. Each compound has `material_id` (mp-XXXX), composition (a real chemistry vector), and ~30 numerical properties. Encoding-fit: this is the cleanest possible substrate target — each compound atom binds to typed numerical properties; sanity-check cells become trivial ("does the substrate retrieve band_gap > 3.0 eV materials when queried for insulators?"). Feasibility: very high; API has been stable since 2013.

**arXiv cond-mat abstracts via OAI-PMH.** Bulk metadata + abstracts, free, ~600k papers in cond-mat alone. Endpoint: `export.arxiv.org/oai2`. Encoding-fit: each abstract is a text chunk (char-trigram-compatible); citation graph available via Semantic Scholar OpenCorpus join. Substrate-utility: enables "find papers near this concept" queries but does NOT give quantitative facts. Lower per-atom value than Materials Project but higher coverage.

**Crystallography Open Database (COD).** ~500k crystal structures in CIF format, fully open, no API key. Each entry has space group, lattice parameters, atom positions. Encoding-fit: symbolic + numerical hybrid; harder to ingest cleanly than Materials Project but covers structures Materials Project lacks (organics, minerals). Defer to Phase 2.

Encoding-strategy: numerical properties bind as quantized buckets (log-spaced for energies, linear for compositions) so retrieval-by-range works. Do NOT char-trigram numerical fields; that destroys the ordering.

## Angle 3 — Biology / Brain Sources Beyond GO/KEGG/NeuroLex

**UniProt (recommended for sheer scale).** ~250M protein sequences with functional annotation, GO term cross-refs (joins to our existing GO ingest), organism, taxonomic lineage. SwissProt subset (~570k entries) is the curated high-quality slice. Bulk download as flat-file or XML. Encoding-fit: protein-id atom binds to sequence chunks + GO terms (cross-corpus linkage that strengthens existing GO ingest) + organism atom. Feasibility: high (FTP dumps, no key).

**PubChem.** ~110M chemical compounds with InChI, SMILES, calculated properties, bioactivity. Bulk download of compound table is ~80 GB; smaller subsets (drug-like, ~5M) are tractable. Encoding-fit: SMILES strings are token sequences (atoms + bonds); char-trigram on SMILES is actively wrong (chiral centers and bond orders matter at the symbol level). Need SMILES-aware tokenization. Defer until we have token-stream encoder.

**Reactome.** ~2.6k human pathways, ~13k reactions, ~11k proteins, fully open BioPAX/SBML download. Smaller than KEGG (which we have) but DEEPER per-pathway annotation and better cross-refs to UniProt. Encoding-fit: same pattern as KEGG (already ingested); incremental value mostly through UniProt join.

## Angle 4 — Substrate-Native Encoding for Formal Content

This is the load-bearing angle. ProofWiki failed in part because we had no plan for what to DO with the wikitext once fetched. Char-trigram on "∀x∈ℝ, sin²(x)+cos²(x)=1" averages to noise; the substrate cannot distinguish that from a related-but-wrong identity.

- **Predicate-argument decomposition.** Parse each statement to a (head, args) tree; encode head as an explicit symbol vector from a fixed mathematical-symbol codebook (~2000 symbols covers most of mathlib + DLMF); encode args recursively. Bind via role-filler. Cell-test: substrate distinguishes `sin(2x) = 2 sin(x) cos(x)` from `sin(2x) = sin(x) + cos(x)` at cosine separation >= 0.6. This is testable without any external corpus by hand-encoding 50 identities.
- **Proof-tree as hierarchical bind.** A proof of theorem T using lemmas L1, L2 binds as `T = bind(USES, sum(L1, L2))`. Multi-step proofs nest: `T = bind(USES, sum(L1, bind(USES, sum(L3, L4))))`. Depth-K composition results from earlier substrate work apply directly. Existing depth-15 multi-hop result becomes the prior; we expect proof-tree retrieval to work at depth ~5-8 honestly.
- **Mixed-modal atoms.** Statement-text-chunk (char-trigram) + symbol-tree (codebook) + dependency-edge-list (id-vectors), all bound to the same theorem atom under typed roles. At retrieval time, query specifies which modality matters. This is the only honest answer to "how do I encode a Lean theorem"; no single modality suffices.
- **Token-stream encoder for formulas.** Train a tiny ~16-dim per-token embedding for the ~2000 math symbols + variable-name slot (variables get FRESH random vectors per scope, otherwise `x` in proof A pollutes `x` in proof B). This is the smallest piece of learned encoding the substrate needs; everything else can stay forward-only.
- **Variable-scoping discipline.** Mathematical variables are bound in a scope (theorem statement). Encoding `f(x) = x^2` with x as a global symbol-codebook entry is wrong; x must be a fresh random vector scoped to that theorem. Brain solves this via PFC working-memory slot allocation; substrate version = per-theorem variable-renaming pass before encode.

## Angle 5 — Cross-Domain / Meta Sources

**Semantic Scholar OpenCorpus (recommended for citation graph).** ~200M papers with title, abstract, references, citations. Free for non-commercial use, bulk dumps available. Encoding-fit: complements arXiv abstracts by providing the citation graph that arXiv lacks. Citation-graph + abstract-text is the closest thing to a "scientific knowledge atlas" at substrate scale. Use as METADATA layer over arXiv full-text ingest.

**OpenAlex.** Replacement for Microsoft Academic Graph; ~250M works metadata, free CC0, REST API. Cleaner schema than Semantic Scholar for concepts (`concept_id` taxonomy ~65k nodes). Encoding-fit: concept hierarchy is a clean class-system atom; works become instance atoms bound to concepts.

**The Stack / CodeSearchNet.** ~6 TB / ~2M functions of source code. Different formal-knowledge style: code as executable formal artifact. Encoding-fit: tokenized via language-aware lexer (per-language); not a Phase-1 priority because M3/M4 are reasoning-about-math goals, not code-gen. Reserve for M5.

**Wikidata RDF subset.** ~100M entities, structured triples. Already partially covered via FB15k ingest. Incremental value over what we have is small.

## TOP-3 Recommended Ingest Sources

Selection criteria: (a) feasibility today (API stable, dump downloadable, license clean); (b) substrate-fit (structured dependencies or quantitative properties, not just text); (c) M3-utility (does it enable reasoning, or just bulk the KB?).

**1. Lean4 Mathlib.** Justification: monorepo Git clone (no API risk), explicit dependency graph (multi-hop substrate has somewhere to walk), 165k theorems is a useful but not overwhelming first target. Estimated cost: 3-5 hours one-time parse, ~500k content chunks. M3-utility: HIGHEST — gives the substrate a corpus of formally-true statements with known dependencies, the exact substrate the depth-15-multi-hop result needs to be tested against. P(useful) = 0.70 (lit-scan-calibrated; novel-synthesis cap doesn't bite because this is import-not-invent).

**2. Materials Project API.** Justification: clean numerical properties, MIT data license, API stable >10 years, 150k compounds covers most of inorganic chemistry. Estimated cost: 1-2 days API ingest at rate limits, ~50k atoms with rich numerical bindings. M3-utility: HIGH — gives substrate ground-truth numerical sanity-check capability (a USER goal). P(useful) = 0.65.

**3. OEIS.** Justification: 50 MB stripped dump (trivial cost), 370k sequences, cross-reference graph is the corpus's value. Estimated cost: <1 hour ingest + chunking. M3-utility: MEDIUM-HIGH — narrow domain (integer sequences) but enables clean discriminator cells for "does the substrate retrieve generating-function-related sequences when queried for a recurrence?" P(useful) = 0.55.

**Encoding-strategy recommendation (load-bearing across all three):** ship the sub-atom token-stream encoder before ingest. Without it, all three sources collapse to char-trigram-of-text and we lose the structural information that made us pick them over ProofWiki. The encoder spec: ~2000-symbol math codebook + per-scope variable renaming + role-filler bind for predicate-argument structure. Build cost: ~2-3 cells, ~1 GPU-day. This is the prerequisite cell, not the ingest cells.

**Deferral list:** UniProt (defer to Phase 2; cross-ref join to GO is the real value, not standalone), PubChem (defer until SMILES tokenizer ships), Stacks Project (defer; ship after Mathlib pattern proven), arXiv full-text (defer; OAI-PMH abstracts is enough for M3), CodeSearchNet (defer to M5).

## Pre-dispatch verify-the-referent gates

Before committing to any TOP-3 source, run one cell per source to verify the actual download works TODAY:
- Mathlib: `git clone --depth=1 https://github.com/leanprover-community/mathlib4` should complete in <5 min; file count ~6000 `.lean` files
- Materials Project: register key, single `mp-149` (silicon) query should return JSON with band_gap field
- OEIS: `curl -O https://oeis.org/stripped.gz` should return ~50 MB gzip

If any of these fail at the verify step, switch to the next-ranked source in that angle before authoring ingest cells. This is the discipline that ProofWiki bypassed (and paid for).

---

Word count: ~1180.
Author: research (Director).
Filed for: USER review + Director sequencing into ingest queue once Wave 4 content-chunk substrate-KB lands.
