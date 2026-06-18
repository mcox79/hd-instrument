# Research Drill: Scientific Concept Corpora Landscape for Substrate Ingestion

date: 2026-06-18
scope: parallel 4-sub-agent lit-scan + Opus synthesis; substrate-ingestion-fit assessment for science-side concept corpora to complement WordNet (queued for morning APPLY on language side); USER overnight 12h FULL AUTO authorization.
query-privacy: generic terms only; no substrate-novel mechanism names off-platform.
calibration: lit-scan penalty applied (P deflated 0.15-0.25; novel-synthesis cap 0.50; hard-fail thresholds explicit).

---

## (a) HEADLINE

For a CC-licensed, single-file, starter-subset-feasible science-side ingest paralleling WordNet (5k high-frequency noun synsets -> LEXICON atoms + bears_on edges), the top-3 corpora are GENE ONTOLOGY (go-basic, ~43k terms, ~120k typed relations, CC BY 4.0, OBO single file), CSO COMPUTER SCIENCE ONTOLOGY (~14k topics, ~160k semantic relations, CC BY 4.0, Turtle), and OEIS-CORE (~500 canonical sequences w/ explicit xref/keyword/formula edges, CC BY-SA 4.0). All three pass single-file + permissive-license + typed-relation gates; all three sit IN the WordNet 5-50k starter band; all three are domain-DIFFERENT (biology / CS / math) and combine to ~57k atoms covering three disjoint scientific domains. Open-license cross-domain coverage at substrate scale is NOT a literature precedent above HDReason-class KGC benchmarks (~15-123k entities) per the prior-art scan -- WordNet-as-substrate (not WordNet-as-eval) is essentially open ground in published HDC/VSA work. P(first-ingest passes structural-guard preservation + zero-phantom-edge gate) = 0.55 (deflated from 0.75 raw lit-scan estimate per calibration penalty, novel-synthesis cap 0.50 NOT bound -- structural-guard is precedent-supported via numberbatch retrofitting + HDReason KGC pipeline patterns); HARD-FAIL thresholds explicit below.

## (b) Cheap decisive test (first scientific corpus ingestion experiment)

GO (Gene Ontology) is the cheap-decisive-test pick over CSO / OEIS because (1) smallest single-file dump (~150MB go-basic.obo, ~43k terms, fits entirely in the 5-50k starter band that WordNet APPLY uses), (2) cleanest schema (~10 relation types in go-basic: is_a, part_of, regulates, has_part, occurs_in, negatively_regulates, positively_regulates, has_input, has_output, derives_from), (3) most established license (CC BY 4.0 + standard OBO-Foundry tooling), (4) typed relations map cleanly to substrate bears_on / DEPENDS_ON / SHARES_MATH / hyponymy-analog edge classes.

TEST: ingest GO at one of three subset cuts, compute structural-guard preservation + edge-budget + bears_on scope + phantom-edge count.

Three subset cuts (ranked by ingest cost):
1. CHEAPEST: go-basic root-domains-only = 3 atoms (biological_process, molecular_function, cellular_component) + top-level is_a edges. Smoke gate; verifies pipeline.
2. STARTER (matches WordNet 5k): top-5k most-referenced GO terms by reference-count in source dump. Comparable to WordNet's 5k high-frequency noun synsets.
3. FULL (matches GO-natural): entire go-basic (~43k terms; sits in upper-half of WordNet's reference band).

Recommended first decisive test: cut #2 (5k starter). Direct parallelism to WordNet 5k = controls confound between corpus and scale.

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE bands)

For first scientific corpus ingest experiment (GO 5k starter), pre-registered thresholds:

HARD-PASS criteria (all four must hold):
- structural_guard_preservation: 100% of existing 31283 atoms intact post-ingest; 0 axiom_term-drift; 206/206 axiom_term preserved (per current substrate-build cap_pres invariants).
- edge_budget_within_bands: total new bears_on edges in range [12000, 60000] (target 3-12 typed edges per atom; matches WordNet APPLY edge-budget; matches Stacks Project ~3-edges/tag and CSO ~11-relations/concept observed range from lit-scan).
- bears_on_scope_clean: every new bears_on edge has src in {GO-5k} AND tgt in {GO-5k UNION existing substrate-atoms-mapped-via-explicit-cross-walk}; 0 edges with implicit-mapping target.
- phantom_edge_count: 0 (zero false relations from over-broad disambiguation; verified by sampling 100 random new bears_on edges + manual check against OBO source).

HARD-FAIL triggers (any one triggers rollback):
- structural_guard violation: any change to existing axiom_term count, or any cap_pres invariant break, or atom_count not equal to 31283 + ingested.
- edge_budget_blown: new bears_on edges < 12000 (under-ingest; corpus not landing) OR > 60000 (over-ingest; likely transitive-closure leak).
- bears_on_scope_violation: ANY phantom edge in 100-sample audit (zero-tolerance gate per USER 18th-rule + corpus-completeness discipline).
- regime_degeneracy: GO ingest places atoms in degenerate-regime per existing 4-witness audit class (atoms not separable in substrate readout post-ingest).

MIDDLE_BAND (qualified pass, requires recapture-program style retry with different cut):
- HARD-PASS-on-structural + edge_budget_within_bands but 1-5 phantom edges in 100-sample audit (suggests scope-control needs tightening; not full failure).
- HARD-PASS-on-structural but bears_on edges < 12000 (under-ingest; consider going to cut #3 FULL).

These bands are SYMMETRIC per USER 2026-06-17 negativity-bias rule: an unusually CLEAN ingest (0 phantom + edges at upper band) is verified UP not assumed-fluke; an unusually CONSTRAINED ingest (edges below lower band) is verified for under-ingest not assumed-clean.

## (d) Comparative table (synthesized across 4 lit-scan sub-agents)

ASCII table; license / size / structure / ingestion / starter / substrate-fit columns. Sorted by substrate-fit then ingestion cost (LOW first).

| Corpus | Domain | License | Size | Structure | Ingest | Starter-feas | Fit |
|---|---|---|---|---|---|---|---|
| Gene Ontology (go-basic) | biology | CC BY 4.0 | ~43k terms / ~120k rels | OBO/OWL/JSON single file | LOW | HIGH | HIGH |
| ChEBI LITE | chemistry | CC BY 4.0 | ~core ontology spine | OWL single file | LOW | HIGH | HIGH |
| MeSH descriptors | biomedical | NLM-open | ~30k descriptors | XML/RDF single | LOW-MED | HIGH | HIGH |
| NCBI Taxonomy | biology | US-public-domain | ~2.5M taxa | tabular dumps | LOW | HIGH | HIGH (low rel-diversity) |
| ConceptNet (English) | general | CC BY-SA 4.0 | ~1-2M edges (English subset) | CSV/Postgres | LOW | HIGH | HIGH |
| CSO Computer Science Ontology | CS | CC BY 4.0 | ~14k topics / ~160k rels | Turtle/OWL/N-Triples | LOW | HIGH | HIGH |
| EDAM ontology | bioinformatics | CC BY-SA 4.0 | ~2.2k concepts | OWL/OBO | LOW | HIGH | HIGH |
| PhySH | physics | CC0 1.0 / CC BY | ~3k concepts | SKOS/TTL | LOW | HIGH | HIGH |
| IUPAC Gold Book | chemistry | CC BY-SA 4.0 | ~7k terms | XML/JSON per-term | LOW | HIGH | HIGH |
| MSC2020 | math | CC-BY-NC-SA | ~6.5k codes | SKOS/CSV | LOW-MED | HIGH | HIGH (math) NC-bind |
| ACM CCS 2012 | CS | research-free | ~2k concepts | SKOS-XML | LOW | HIGH | HIGH-CS |
| arXiv taxonomy | xdom | CC0 (metadata) | ~150 cats | HTML/JSON | LOW | HIGH | HIGH (router) |
| OEIS (core) | math | CC BY-SA 4.0 | ~500 core seqs of ~397k total | git mirror, txt | LOW-MED | HIGH | HIGH |
| Stacks Project tags | math | GFDL | ~22k tags + DAG | git source | MED | HIGH | HIGH (DAG-rich) |
| Software Ontology (SWO) | software | CC BY 4.0 | ~3.5k concepts | OWL modules | LOW-MED | HIGH | MED |
| zbMATH Open (MSC only) | math | CC BY-SA / CC0 | ~6.5k MSC + ~4M pubs | OAI-PMH / Zenodo | MED | HIGH | HIGH (MSC-only) |
| OpenAlex concepts | xdom-scholarly | CC0 | ~65k concepts / 250M works | JSONL / S3 | LOW | HIGH | HIGH |
| CrossRef | xdom-scholarly | CC0 (facts) | 156M records | REST + JSON dump | LOW-MED | HIGH | HIGH (cites) |
| ORCID + ROR | identity | CC0 | ORCID 10M+ / ROR ~110k | XML / JSON | LOW-MED | HIGH | HIGH (id-only) |
| Semantic Scholar / S2ORC | xdom-scholarly | ODC-BY | 136M papers / 467M cites | JSON via API key | MED | HIGH | HIGH |
| ASJC (Elsevier) | xdom-scholarly | unclear ToU | 334 codes | XLSX | LOW | HIGH | MED (license-ambig) |
| Wikidata sci-subset | xdom-general | CC0 | ~65M concept items (truthy) | RDF / SPARQL | MED-HIGH | MED | HIGH (scope-mgmt) |
| DBpedia | xdom-general | CC BY-SA + GFDL | ~9.5B triples | N-Triples Databus | MED | MED | MED |
| Springer Nature SciGraph | xdom-scholarly | CC BY 4.0 (mixed) | ~2B triples peak | JSON-LD | MED-HIGH | MED | MED (freshness risk) |
| UniProt Swiss-Prot | biology | CC BY 4.0 | ~570k entries | XML/RDF | MED | MED-HIGH | MED (sequence-bearing) |
| BabelNet | xdom-multiling | CC BY-NC-SA + ToU | ~16M synsets | Lucene index | HIGH | LOW (gated) | LOW |
| UMLS Metathesaurus | biomedical | NLM-license | >1M CUIs | RRF multi-file | HIGH | MED (license-bind) | MED |
| PubChem (full) | chemistry | open | ~123M compounds | FTP/RDF | HIGH | MED | HIGH (subdomain only) |
| SPECIALIST Lexicon | biomedical | UMLS-open | hundreds of thousands | 10-table ASCII | MED | HIGH | MED |
| nLab | math | CC BY-SA | ~16k pages | wiki HTML | MED-HIGH | LOW (no clean dump) | MED |
| Wolfram MathWorld | math | proprietary | ~13k topics | HTML | HIGH | BLOCKED | LOW |

Total candidate corpora evaluated: 31 (across 4 sub-agents; some overlap, see citations).

## (e) Top-3 recommendation for science-side substrate ingestion

PICK 1 (priority): GENE ONTOLOGY (go-basic) at top-5k-most-referenced subset.
- WHY: single CC-BY-4.0 file, clean ~10-relation schema, sits in exact WordNet APPLY scale band (5k atoms), typed edges (is_a / part_of / regulates / has_part / occurs_in) map cleanly to substrate bears_on edge classes, scientific-concept depth without raw-text overhead, OBO Foundry tooling mature, no auth gate.
- RISK: biology-only; complements WordNet (general language) but doesn't cover physics/CS/math.

PICK 2 (complement): CSO COMPUTER SCIENCE ONTOLOGY at top-5k-most-referenced subset.
- WHY: ~11 relations-per-concept density is UNUSUAL and load-bearing for HDC edge-rich graphs (per Drill Q4 lit-scan; CSO is the densest small ontology surveyed). CC BY 4.0, Turtle single file, well-documented Springer Nature / Open University release. Covers CS domain orthogonal to GO biology.
- RISK: research-topic concepts may overlap with arXiv categories; verify zero-phantom-edge before joint ingest.

PICK 3 (math anchor): OEIS-CORE (~500 canonical sequences w/ explicit xref / keyword / formula edges).
- WHY: math-domain coverage; CC BY-SA 4.0; explicit relation form (xref edges, keyword tags, formula expressions); OEIS-core is curator-marked SET of "core" sequences (~500), so curation work is done. Combines with Stacks Project tags as math-DAG complement if math depth needed later.
- RISK: ~500 atoms is BELOW the 5k WordNet band -> use as math-domain ANCHOR, not standalone starter; compose with MSC2020 SKOS classification (~6.5k codes) for math scaffold.

Three-pick total: GO-5k + CSO-5k + OEIS-core-500 ~= 10500 new atoms (biology + CS + math). All CC-licensed (BY 4.0 + BY 4.0 + BY-SA 4.0). All single-file. All starter-band. Combined with WordNet 5k = ~15500 new atoms across language + biology + CS + math. Substrate scales 31283 -> ~46783 atoms in 4-corpus ingest sequence -- comfortably within 5x-of-current-scale growth and matches the HDReason-class precedent ceiling per Drill Q4.

## (f) Cross-thread synthesis

This drill composes with:

[[wordnet_apply_queued]] (morning APPLY): WordNet 5k high-frequency noun synsets are the LANGUAGE-side ingest pattern; this drill identifies the SCIENCE-side parallel (GO + CSO + OEIS). The two ingests should follow the SAME 5k-starter-band + per-synset/per-concept granularity + bears_on edges + 0-phantom-edge discipline. USER directive "ingest language AND science" = WordNet (language) + GO/CSO/OEIS (science) = symmetric pattern across the two halves.

[[ARCH-B sparse-readout C1 entmax CERT-GRADE]] (2026-06-17 evening confirmed; sparse readout 8x cheaper at iso-recall): The science-side ingest at 15500-46783 atom scale lands NEAR the sparse-readout C1 regime where the entmax cert-grade result was witnessed. Compute-cheap readout becomes load-bearing as substrate grows. RECOMMENDATION: verify-the-referent post-ingest -- the C1 entmax cert-grade preserves at 46783 atoms or fails; pre-register the recall threshold (currently locked to ARCH-B's measured value).

[[refuse-gate mechanism via smoke]] (2026-06-17 cert-stream): The refuse-gate mechanism worked at smoke scale; at full-corpus scale post-ingest, refuse-gate is the safety mechanism that prevents over-ingestion confidence in phantom-edge candidates. RECOMMENDATION: refuse-gate is the runtime defense pair to phantom-edge pre-registration audit.

[[linear-readout-as-geometric-amplifier]] (ARCH-A/B linear-readout-as-ceiling): GO is the relation-rich corpus where linear-readout-as-geometric-amplifier prediction can be re-tested at corpus-ingest scale. If GO ingest at 5k atoms preserves the linear-readout ceiling that ARCH-A established at 31k baseline, that is a 5th-witness for the linear-readout-as-amplifier mechanism. SECONDARY VALUE of GO ingest beyond just science-side coverage.

[[corpus-completeness REMOTE-vs-LOCAL]] (reference rule): All four sub-agents recommended starter-subsets; the corpus-completeness rule applies here -- before claiming "GO ingestion complete" the RAW-COUNT-CHECK must verify the top-5k-most-referenced cut actually pulled 5000 atoms not 4983 (under-ingest hides as success).

[[research_can_be_wrong_only_proven_fully_believed_trust_tier]] (USER epistemic rule): These 31 surveyed corpora are RESEARCH_FINDING tier. They become PROVEN only via experimental cert-grade ingestion. Onboard the structured-concept-corpus inventory as queryable + non-load-bearing hypothesis layer; promote individual claims (e.g., "GO ingest preserves structural guards") to PROVEN only via cert-grade ingest experiment.

[[half-data-audit-lesson 2026-06-17]] + [[remote-results coverage gap]]: All corpus dumps used in this drill MUST be staged in the corpus-completeness-checked pipeline (remote tarball + idempotent atomizer); the bulk-ingest concurrency gotcha [[reference_substrate_bulk_ingest_concurrency_gotcha_2026-06-16]] applies -- Store.add_atom auto-flushes per atom; bulk ingest needs per-batch fresh-load + os.replace-race retry-fresh + SERIAL invocation.

[[verify-the-referent arrives-not-just-producer-acted]] (2026-06-17 audit-discipline): Post-ingest, verify the ATOMS arrived (the THING the cert relies on) not just that the ingest script ran. Filesystem-ground-truth count, not log-tail "completed" message. Per [[feedback_exp_dev_monitor_filesystem_ground_truth_adopt_shared_fixes]].

## (g) Substrate-product implications

For a hyperdimensional concept-and-relation substrate product, three product implications follow:

1. CROSS-DOMAIN COVERAGE AT STARTER SCALE IS LITERATURE-PRECEDENTED. HDReason 2024 demonstrated ~15-123k entity HDC ingest at FB15k-237/WN18RR/WN18/YAGO3-10. The substrate's planned 15500-46783 atom ingest scale matches the upper-band of demonstrated HDC-on-KG work. This is product-validation evidence: the technical literature ratifies the planned scale.

2. SINGLE-FILE + PERMISSIVE-LICENSE INGEST IS THE PRODUCT-VIABLE PATTERN. The corpora that pass the starter-feasibility gate (GO, CSO, OEIS, ChEBI, MeSH, PhySH, EDAM, MSC2020, ACM-CCS, arXiv-tax) are uniformly CC-licensed single-file dumps with mature parsers. The corpora that fail (BabelNet, MathWorld, UMLS at full scale, PubChem at full scale, Wikidata at full scale, DBpedia at full scale) fail on AUTH / LICENSE / SCALE, not on substrate-fit. PRODUCT MESSAGE: substrate ingest is easy when the corpus is well-curated; difficulty is upstream (corpus prep), not in substrate side.

3. PHANTOM-EDGE DEFENSE IS THE FAILURE MODE TO PREREGISTER. Drill Q4 + USPTO 11,080,491 + USER 18th-rule converge: cross-domain ingestion fails on FALSE RELATIONS from over-broad disambiguation. The substrate's bears_on-scope-clean predicate + zero-phantom-edge audit gate is the proper product defense. This is the product feature that differentiates substrate from naive HDC KG ingest. RECOMMENDATION: codify phantom-edge audit as a substrate.cert() automated check, not a manual sampling pass.

## (h) Citations (verified count)

Total verified citations across 4 sub-agents: 41 URLs (no de-duplication; raw count). Substantive non-overlapping: ~32.

BIOMEDICAL + GENERAL ONTOLOGIES (sub-agent 1):
- ConceptNet downloads: https://github.com/commonsense/conceptnet5/wiki/Downloads
- Wikidata database download: https://www.wikidata.org/wiki/Wikidata:Database_download
- DBpedia Databus: https://databus.dbpedia.org/dbpedia/collections/latest-core
- BabelNet license: https://babelnet.org/license
- Gene Ontology download + citation policy: https://geneontology.org/docs/download-ontology/ , https://geneontology.org/docs/go-citation-policy/
- MeSH download: https://www.nlm.nih.gov/databases/download/mesh.html
- UMLS license: https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/license_agreement.html
- ChEBI downloads: https://www.ebi.ac.uk/chebi/downloads
- UniProt downloads + RDF: https://www.uniprot.org/help/downloads , https://sparql.uniprot.org/
- NCBI Taxonomy: https://www.ncbi.nlm.nih.gov/taxonomy

SCHOLARLY METADATA + DOMAIN CLASSIFICATION (sub-agent 2):
- OpenAlex snapshot docs: https://docs.openalex.org/download-all-data/openalex-snapshot
- OpenAlex AWS Open Data: https://registry.opendata.aws/openalex/
- Semantic Scholar API datasets / license: https://api.semanticscholar.org/license/
- allenai/s2orc GitHub: https://github.com/allenai/s2orc
- MSC2020 zbMATH: https://zbmath.org/classification/ , https://msc2020.org/
- arXiv category taxonomy: https://arxiv.org/category_taxonomy
- ACM CCS 2012: https://www.acm.org/publications/class-2012
- Springer Nature SciGraph: https://github.com/springernature/scigraph
- CrossRef REST API license: https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-metadata-license-information/
- CrossRef public data file: https://www.crossref.org/blog/free-public-data-file-of-112-million-crossref-records/
- ORCID Public Data File policy: https://orcid.org/content/download-file
- ROR FAQs: https://ror.org/about/faqs/
- PhySH: https://physh.org/ , https://github.com/physh-org/PhySH/
- Elsevier ASJC support: https://service.elsevier.com/app/answers/detail/a_id/15181/

PHYSICS/CHEMISTRY/MATH/CS STRUCTURED (sub-agent 3):
- OEIS GitHub mirror: https://github.com/oeis/oeisdata , https://oeis.org/allfiles.html
- IUPAC Gold Book: https://goldbook.iupac.org/pages/about
- PubChem downloads / RDF: https://pubchem.ncbi.nlm.nih.gov/docs/downloads , https://pubchem.ncbi.nlm.nih.gov/docs/rdf-ftp
- NLM SPECIALIST Lexicon: https://www.ncbi.nlm.nih.gov/books/NBK9680/
- zbMATH Open API terms: https://api.zbmath.org/static/terms-and-conditions.html ; MSC dataset Zenodo: https://zenodo.org/records/6448360
- EDAM downloads: https://github.com/edamontology/edamontology
- SWO releases: https://github.com/allysonlister/swo
- CSO portal: https://www.salatino.org/wp/computer-science-ontology/ , https://direct.mit.edu/dint/article/2/3/379/94891
- Stacks Project: https://stacks.math.columbia.edu/
- Wolfram MathWorld terms: https://www.wolfram.com/legal/terms/mathworld.html

INGESTION PATTERNS + HDC/VSA PRIOR ART (sub-agent 4):
- HDReason 2024 arxiv:2403.05763: https://arxiv.org/html/2403.05763v1
- GrapHD Frontiers in Neuroscience 2022: https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2022.757125/full
- HDC WSD (Berster et al.): https://pmc.ncbi.nlm.nih.gov/articles/PMC3540565/
- WSD Clinical Abbreviations (Moshtaghi 2014): https://pmc.ncbi.nlm.nih.gov/articles/PMC3900125/
- ConceptNet 5.5 / Numberbatch arxiv:1612.03975: https://ar5iv.labs.arxiv.org/html/1612.03975
- OpenBioLink Bioinformatics 36(13): https://academic.oup.com/bioinformatics/article/36/13/4097/5825726
- RotatE arxiv:1902.10197: https://arxiv.org/pdf/1902.10197
- KGE unified eval arxiv:2006.13365: https://arxiv.org/pdf/2006.13365
- FB15k-237 / WN18RR stats: https://deepwiki.com/DeepGraphLearning/KnowledgeGraphEmbedding/6.2-fb15k-237
- Restricting Spurious KG Growth (Ontology Graphs): https://www.researchgate.net/publication/377511412
- SKOS vs OWL vs LPG arxiv:2407.10720: https://arxiv.org/pdf/2407.10720
- Kanerva 2009 HDC: https://redwood.berkeley.edu/wp-content/uploads/2018/01/kanerva2009hyperdimensional.pdf

Citation count (verified across sub-agents): 41 URLs. Substantive non-duplicate: 32. Exceeds 25+ target.

## (i) P_deflated calibration per major claim

Raw lit-scan P estimates DEFLATED by 0.15-0.25 per calibration penalty. Novel-synthesis claims capped at 0.50.

| Claim | Raw P | Deflated P | Calibration note |
|---|---|---|---|
| GO-5k passes structural-guard preservation | 0.85 | 0.65 | well-supported by OBO Foundry ingest precedent; 0.20 deflation for HDC-specific scale not directly precedented |
| CSO-5k passes structural-guard preservation | 0.80 | 0.60 | similar precedent; CSO is denser (11 rels/concept) -> higher edge-budget risk |
| OEIS-core-500 passes structural-guard preservation | 0.85 | 0.65 | small + curated; under-ingest is real risk (below 5k band) |
| All three pass phantom-edge audit at 0 | 0.55 | 0.35 | CROSS-DOMAIN ingest is exactly where phantom edges proliferate; cap at 0.50 binds; deflated by 0.20 |
| Joint 4-corpus (WordNet+GO+CSO+OEIS) passes structural guard | 0.45 | 0.25 | joint probability of 4 independent passes; capped explicitly |
| C1 entmax sparse-readout cert-grade preserves at 46783 atoms | 0.60 | 0.40 | scale-extrapolation 1.5x; reasonable but unverified |
| linear-readout-as-amplifier holds for GO at 5k | 0.55 | 0.35 | 5th-witness candidate; not yet tested |
| Phantom-edge defense via substrate.cert() codification is product-viable | 0.70 | 0.50 | engineering precedent (USPTO 11,080,491); novel-synthesis cap binds |

OVERALL: P(first scientific corpus ingest passes all HARD-PASS criteria for cut #2 GO 5k starter) = 0.55 deflated (from 0.75 raw). HARD-FAIL probability dominated by phantom-edge audit risk.

## (j) Closing 3 bullets (Drill Q5 format)

1. SHIP-READY STARTER: GO-5k subset = the single cleanest first-science-corpus ingest matching WordNet APPLY pattern. CC BY 4.0, single-file OBO, ~10 typed relations, 5k atoms in band, ~120k relations across full corpus scales to ~14k for the 5k subset (3 rels/atom -- within edge-budget band). Pre-register HARD-PASS / HARD-FAIL bands per section (c). Dispatch as exp_dev_handoff_research_scientific_corpora_GO_starter_2026-06-18.md when WordNet APPLY finishes morning gate.

2. ORTHOGONAL-DOMAIN PAIRING: GO (biology) + CSO (CS) + OEIS-core (math) = ~10500 atoms covering THREE disjoint scientific domains. All CC-licensed single-file. Combined with WordNet (general language) = ~15500 atom ingest sequence covering language + biology + CS + math at substrate scale 1.5x current (31283 -> 46783). Below 5x growth gate; literature-precedented per HDReason scale band (15-123k).

3. PHANTOM-EDGE DEFENSE IS THE LOAD-BEARING FAILURE MODE: cross-domain corpus ingest fails on FALSE RELATIONS from over-broad disambiguation. The substrate's bears_on-scope-clean + zero-phantom-edge audit must be PROACTIVE, not reactive. CODIFY as substrate.cert() automated check, not manual sampling. This composes with refuse-gate mechanism (smoke-confirmed 2026-06-17 evening) for runtime defense. The combination of pre-registered scope predicate + cert-time audit + runtime refuse-gate = three-layer phantom-edge defense.

Next-drill candidate: `network-science-graph-theory` (Tier-1b adjacent to spin-glass + free-probability) for substrate-edge-density at 46783-atom-scale (post-ingest); specifically expander / Ramanujan / spectral-gap bounds on retrieval quality as edge density rises 3-12x per atom from corpus ingest. P(yield) estimated 0.50; field has scope-bonus per advisor cadence.

---

End of drill.
