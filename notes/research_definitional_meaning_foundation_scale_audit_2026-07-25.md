# Research: does the definitional/propositional meaning foundation SCALE past the 128-tie blind spot? A full-ARC-vocabulary + supply-source disk audit

date: 2026-07-25
topic: read-only disk characterization (no build, no dispatch) of whether WorldTree tablestore v2.1's clean definitional/propositional structure (KINDOF, SYNONYMY, PROP-*, SOURCEOF/REQUIRES/CAUSE) covers the FULL ARC-Challenge+Easy science vocabulary at the depth the grounded-meaning plan needs, or whether it is data-bound at 128-tie benchmark scale -- and if data-bound, a ranked sourcing recommendation from what is actually on disk.
mode: direct disk audit (parse WorldTree v2.1 tablestore, full ARC-V1 corpus, ConceptNet assertions, OpenStax biology glossary, WordNet via nltk) -- no sub-agent dispatch, no lit-scan (this is a data-characterization task, not a literature question).
calibration: this is a MEASUREMENT note, not a novel-synthesis claim; numbers below are disk-verified and reproducible from the scratch scripts used (paths given). The one genuinely predictive claim (the ranked-sourcing recommendation's expected payoff) is deflated and capped per standing calibration discipline -- see Falsifiable predictions.

**KB-check performed (honest, not glossed over):** the char-trigram KB encoder (`substrate_query.sh`, `director_kb_query.py`) and unscoped `notes/` grep both failed to surface the literal a642b513 record within budget (confidence <=0.39 on semantic query, repeated 20s ripgrep timeouts on the large `notes/` directory). A later, narrower background grep (`grep -rn "a642b513" . --include=*.md`) DID eventually surface it, in `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-17.md:28`. The actual a642b513 finding: **"WorldTree PROP-* = 20 CLEAN single-attribute tables (magnetism/conductivity/hardness/opacity/acidity/state-of-matter/warm-cold-blooded, value cardinality 2-4) BUT SHALLOW: mean 1.1-1.2 attrs/concept, median 1, frac_ge2=0.13 science-core (< v2's 0.24). Rich multi-attr vector exists for ~10 canonical MATERIALS (plastic/metal/glass/wood/water). Trainable earn-multi-attr-from->=2-relations set = ~21 concepts (80 single-attr). NOT a dense science Binder. Convergent finding: every grounded+relational source is THIN at the intersection (WT-rel frac_ge2 0.24 / WT-PROP 0.13 / Binder-WT ~21) -> the wall may be shifting from MECHANISM to the GROUNDED-DATA FOUNDATION itself. Honest options: (A) small clean-materials micro-proof; (B) invest in a denser grounded foundation (CSLB/richer norms); (C) accept meaning is data-bound not mechanism-bound here."** I did NOT re-derive or duplicate that specific 128-tie/materials-micro-benchmark measurement -- everything below is the BROADER full-ARC-vocabulary + supply-landscape question, measured independently from scratch, extending option (B) and (C) above with concrete disk numbers. **Cross-validation:** a642b513's "v2's 0.24" (a broader WorldTree-relation frac_ge2, not just PROP-*) lines up closely with this audit's independent full-ARC-vocab PROPERTY-only, distinct-table-count measurement of **frac_ge2=0.255** (Part 1c) -- two independently-computed numbers, different population (128-tie-adjacent vs. full-ARC-vocab-by-frequency), converging on the same ~0.24-0.26 shallow-depth reading. This is a meaningful independent confirmation, not just a shape-match.

---

## HEADLINE

**Two-tier verdict, not a single yes/no.** The direction is **SCALABLE at the "does some clean definition exist" breadth level** but remains **DATA-BOUND at the "rich multi-relation mechanistic depth" level** the content-thin-wall research (07-25) says is actually required for fine near-neighbor discrimination (hydro/nuclear/coal-type cases):

1. **Breadth is not the bottleneck.** WorldTree v2.1's definitional/propositional tables (KINDOF/SYNONYMY/EXAMPLES/INSTANCES/OPPOSITES/NAMES + 32 PROP-* tables + SOURCEOF/REQUIRES/CAUSE -- 41 of 81 tables, 5,629 of 9,727 total facts) already cover **69.0% of all ARC content-word TOKEN occurrences** (24.8% of unique word TYPES; the gap between these two numbers is exactly what you'd expect -- coverage concentrates on high-frequency recurring science terms and is thin on long-tail/incidental vocabulary). Layering in **WordNet gloss coverage** (already on disk via the `nltk` corpus, already partially wired into the substrate's KB per `wordnet_cache/wordnet.api`) pushes "has at least one clean, human-authored one-line definition" to **92.3% of ARC vocabulary TYPES and 98.5% of TOKENS** -- near-universal. This is the single most important disk-verified finding of this audit and is new information relative to the prior 07-24/07-25 drills, which proposed binding WorldTree PROP-* rows into concepts but did not audit WordNet's own gloss field as a supply source in its own right.

2. **Depth is the real bottleneck, and it is genuinely data-bound.** The typed, multi-relation, argument-structured facts (PRODUCES/REQUIRES/CAUSE with directional structure -- the kind the 07-25 featural-enrichment research says is needed for artifact/mechanism discrimination, e.g. hydro vs nuclear vs coal) are **shallow ARC-wide**, not just on the 128-tie subset: median **1 fact per concept**, and only **24.8%-47.4%** of covered concepts (depending on which category and counting convention) reach even 2 facts. This directly reproduces, at full-corpus scale, the shape of the 128-tie finding (frac_ge2=0.13, ~1.1 attrs/concept for PROP-* alone) -- my PROP-*-only, distinct-attribute-table measurement gives mean 1.36 attrs/concept, frac_ge2=0.255, which is the same SHAPE (mostly single-attribute) at a somewhat richer absolute level (plausibly because the 128 ties were selected as hard/ambiguous cases, which likely correlate with thinner property profiles -- a reasonable, not verified, explanation for the gap between the two numbers).

3. **ConceptNet's promiscuity risk is now quantified, not just flagged.** ConceptNet has near-universal LEXICAL presence for the ARC vocabulary WorldTree misses (98.3% of the top-3000 WorldTree-uncovered ARC words have >=1 ConceptNet edge) but **~52-53% of all edges, for both WorldTree-covered and WorldTree-uncovered words alike, are the generic `RelatedTo` relation** -- ConceptNet's well-known catch-all, low-information relation type. Clean, single-relation types structurally analogous to WorldTree's own tables (`IsA`, `HasProperty`, `PartOf`, `UsedFor`) are a combined **~12-15% minority share** of ConceptNet's edges for this vocabulary. This is directly consistent with, and now gives a concrete mechanism for, the substrate's own prior ConceptNet evaluation (`notes/exp_dev_to_skunkworks_CONCEPTNET_eval_RESULTS_factfab_PASS_inference_FAIL_verdict_VET_2026-06-19.md`): multi-hop KG completion HARD_FAILed against both exact closure (1.0) and frozen-bge (0.502) at Hits@10=0.451, while the fact-fabrication-bound (knowing what it can't infer) HARD_PASSed at AUROC=0.812 -- i.e. ConceptNet's breadth was already measured to not translate into reliable structured completion, and this audit shows WHY: over half its mass is the least-informative relation type.

4. **No new definitional corpus is currently on disk beyond what's characterized above.** GenericsKB, CK-12, and every OpenStax textbook except *Concepts of Biology* are absent from `data/corpora/` and `data/` generally (confirmed via glob/find, zero hits). The one textbook present (`data/corpora/textbook_concepts_biology/`) yields 929 clean, human-authored glossary definitions -- genuinely clean, but biology-only, and adds only 236 NEW covered ARC terms (+1.3% token-weighted) beyond what WorldTree's def/prop tables already cover, because WorldTree and the biology glossary substantially overlap on basic biology vocabulary.

---

## Part 1 -- Full ARC vocabulary vs. WorldTree v2.1 definitional/propositional coverage (disk-measured)

### 1a. The full ARC vocabulary (not just the 128 ties)

Source: `data/corpora/arc/ARC-V1-Feb2018-2/{ARC-Challenge,ARC-Easy}/*.jsonl`, all 6 files (Train/Dev/Test x Challenge/Easy).

| Metric | Value |
|---|---|
| Total questions (Challenge+Easy, all splits) | **7,787** (Challenge: 299+1172+1119=2,590; Easy: 570+2376+2251=5,197) |
| Unique content-word types (question stem + all answer choices, lowercased, stopword-filtered, len>=3) | **10,518** |
| Total content-word tokens | **160,549** |

This is the population the task asks about -- 61x larger in question count than the 128-tie set, and this word-type vocabulary is the honest denominator for a "does clean definitional data exist at ARC scale" question.

### 1b. WorldTree v2.1 tablestore -- table census and definitional/propositional bucket

Source: `data/corpora/worldtree/WorldtreeExplanationCorpusV2.1_Feb2020/tablestore/v2.1/tables/` (81 `.tsv` files; v2.1 added 15 tables vs the v2.0 directory also present on disk, mostly chemistry/history/more-PROP tables -- e.g. `CHEM-PERIODIC-TAB-FAM`, `PROP-CHEM-ACIDITY/CHARGE/ELEMSYMB/REACT`, `PROP-DOMRECESS-TRAIT`, `PROP-MAT-DURABILITY/OPACITY/PURITY-MIXTURE`, `PROP-SOLUBILITY`, `COMPARISON`, `SEQ-SPATIAL`).

| Category | # tables | Tables | Total fact-rows |
|---|---|---|---|
| TAXONOMIC/DEFINITIONAL | 6 | KINDOF, SYNONYMY, EXAMPLES, INSTANCES, OPPOSITES, NAMES | 3,581 |
| PROPERTY (PROP-*) | 32 | all `PROP-*.tsv` (up from ~21-22 in v2.0) | 1,275 |
| DIRECTIONAL/CAUSAL | 3 | SOURCEOF, REQUIRES, CAUSE | 773 |
| **Definitional/propositional bucket (headline)** | **41** | (sum of the three rows above) | **5,629 (57.9% of all 9,727 facts in the tablestore)** |
| OTHER (structural/domain: PARTOF, MADEOF, CONTAINS, LOCATIONS, HABITAT, ACTION, AFFECT, IFTHEN, CHANGE, TRANSFER, CONVERSIONS, PROCESSSTAGES/ROLES, PREDATOR-PREY, VEHICLE, WAVES, etc.) | 40 | -- | 4,098 (42.1%) |

I used a **strict subject-of-fact** measurement (the row's first non-empty, non-`[FILL]`/non-`[SKIP]` cell -- verified by hand against KINDOF/PROP-HARDNESS/SOURCEOF/REQUIRES/CAUSE row examples to correctly identify the subject entity in each table's schema, e.g. "battery" in "a battery is a source of electrical energy") rather than a looser "any word appearing anywhere in the row" measure (which I also computed and report as an upper bound, since it is inflated by generic filler/object words like "water" or "energy" appearing as VALUES in many other concepts' rows, not as their own dedicated subject).

Distinct subject-concepts in the def/prop bucket: **3,021** (out of ~9,000+ distinct entities across all 81 tables).

### 1c. Coverage of the FULL ARC vocabulary by the definitional/propositional bucket

**Strict (subject-of-fact) measurement -- the headline numbers:**

| Slice | Type coverage | Token-weighted coverage | Mean facts/concept | Median | frac >=2 facts |
|---|---|---|---|---|---|
| PROPERTY-only (PROP-*) | 632/10,518 = 6.0% | 53,640/160,549 = 33.4% | 2.22 | 1 | 43.5% |
| TAXONOMIC/DEFINITIONAL-only | 2,239/10,518 = 21.3% | 101,855/160,549 = 63.4% | 1.95 | 1 | 38.3% |
| DIRECTIONAL/CAUSAL-only | 557/10,518 = 5.3% | 47,624/160,549 = 29.7% | 1.84 | 1 | 35.4% |
| **FULL def/prop bucket (union)** | **2,611/10,518 = 24.8%** | **110,827/160,549 = 69.0%** | **2.60** | **1** | **47.4%** |

Frequency-tier breakdown (does the def/prop bucket cover the words that actually MATTER, i.e. recur often, or only rare incidental words?):

| ARC word population | Coverage by full def/prop bucket |
|---|---|
| Top 200 most-frequent ARC words | 179/200 = **89.5%** |
| Top 500 | 418/500 = 83.6% |
| Top 1,000 | 746/1,000 = 74.6% |
| Top 2,000 | 1,270/2,000 = 63.5% |

**Reconciling with the 128-tie characterization (a642b513, as given in the task input):** restricting to PROP-* tables only and counting DISTINCT ATTRIBUTE TABLES per concept (rather than raw fact-rows, which is the closer analog to "attrs/concept"), the full-ARC-vocab number is **mean 1.36 attrs/concept, frac_ge2 (>=2 distinct PROP tables) = 0.255** (distribution: 471 concepts with exactly 1 attribute table, 120 with 2, 26 with 3, 10 with 4, 2 with 5, 2 with 6, 1 with 7). This is the SAME SHAPE as the cited a642b513 finding (frac_ge2=0.13, ~1.1 attrs/concept) -- dominated by single-attribute concepts -- at a moderately richer absolute level. The most likely explanation (not independently verified, offered as a reasoned reconciliation) is that the 128 ties were selected as hard/ambiguous cases, and hard cases plausibly skew toward THINNER property profiles (if a concept had a rich, distinguishing multi-attribute profile, it would likely not produce a tie in the first place). **This reconciliation itself supports, rather than undercuts, the depth-bound verdict**: even the more favorably-selected full-ARC-vocab population is still shallow (median 1, only ~25-47% reach depth 2), so the 128-tie thinness is not a sampling artifact of an unusually bad subset -- it is representative of, if anything slightly worse than, the ARC-wide norm.

**What's missing (top uncovered high-frequency ARC words, zero def/prop WorldTree facts as subject):** `describes, scientists, students, explains, increases, occurs, becomes, roots, needed, grams, absorbed, teacher, cars, allows, moves, forces, community, converted, universe, structures, transferred, absorbs, discovered, travels, observed, velocity, measured, samples, lakes, rivers` -- a mix of (a) genuinely generic/procedural words that should never need a science definition (describes, explains, occurs), (b) legitimately science-relevant nouns WorldTree simply doesn't define as their own subject (velocity, forces, universe, structures) even though it likely uses them as OBJECTS/fillers in other concepts' rows, and (c) domain vocabulary WorldTree's physics/geology coverage is thin on relative to its biology/energy coverage.

---

## Part 2 -- Candidate supply sources on disk: coverage + cleanliness/promiscuity-risk

### 2a. WorldNet gloss (via `nltk.corpus.wordnet`, already on disk, already partially wired via `wordnet_cache/wordnet.api`)

This was **not named in the task's candidate list but is the single most important finding of this audit** -- it is already on disk (no acquisition needed) and already appears as an entity source in the substrate's own KB (`substrate_query.sh` results in this session surfaced `wordnet_cache/wordnet.api` entries directly).

| Metric | Value |
|---|---|
| Gloss coverage, full ARC vocab TYPES | 9,708/10,518 = **92.3%** |
| Gloss coverage, full ARC vocab TOKENS | 158,111/160,549 = **98.5%** |
| Gloss coverage of the WorldTree-def/prop-**uncovered gap words specifically** (TYPES) | 7,148/7,907 = **90.4%** |
| Gloss coverage of the gap words (TOKENS) | 47,821/49,722 = **96.2%** |
| Mean senses/word (gap words with a gloss) | 5.14 (median 3) |

**Reading:** WordNet glosses are near-universally available -- even for the specific words WorldTree's def/prop tables fail to cover as a subject, 90-96% still have at least one clean, human-authored one-line dictionary definition. This means the "does a clean definition exist at all" question is close to solved already, on disk, for free. **The catch is polysemy, not scarcity**: "energy" has 3 WordNet senses (physics quantity; forceful exertion; enterprising drive) and only one is ARC-relevant -- so the risk shifts from data acquisition to **word-sense disambiguation** (pick the science-domain-relevant gloss), a different and more tractable engineering problem than "go find more definitional text."

### 2b. `data/corpora/textbook_concepts_biology` (OpenStax *Concepts of Biology*, 58MB raw / 2MB cleaned)

| Metric | Value |
|---|---|
| Clean glossary term:definition entries (regex-extracted from `###### Glossary` sections, human-authored one-liners, e.g. `atom: a basic unit of matter that cannot be broken down by normal chemical reactions`) | **929** unique terms, 951 total entries |
| Headword overlap with ARC vocab | 408/929 = 43.9% |
| Of those, NEW coverage not already given by WorldTree def/prop bucket | **236 terms** |
| Token-weighted coverage GAIN from adding this glossary on top of WorldTree | 2,075/160,549 = **+1.3%** |

**Reading:** genuinely clean (single OpenStax textbook, human-authored, unambiguous one-sentence definitions, zero LLM involved in the extraction pipeline per `PROVENANCE.md`), but narrow: one textbook covering one subject (biology) yields fewer than 1,000 usable definitions, and most of what it defines WorldTree already covers via KINDOF/SYNONYMY. The pipeline (`clean_cnxml.py`, proven, zero network access needed to regenerate) is the valuable asset here, not the single book's content -- see sourcing recommendation #3.

### 2c. ConceptNet (`data/conceptnet/conceptnet-assertions-5.7.0.csv.gz`, 475MB gz, 34,074,917 total assertion rows, 3,423,004 English-to-English rows)

Measured by streaming the full assertions file (not sampled) and checking (i) the top 3,000 highest-frequency ARC words with ZERO WorldTree def/prop coverage ("gap words"), and (ii) a comparison set of the top 1,000 highest-frequency ARC words WorldTree DOES cover ("covered sample"):

| Metric | Gap words (WorldTree-uncovered) | Covered-sample (WorldTree-covered, comparison) |
|---|---|---|
| Words with >=1 ConceptNet edge | 2,950/3,000 = **98.3%** | 1,000/1,000 = 100% |
| Mean edges/word | 198.98 | 827.70 |
| Median edges/word | 62 | 451 |
| Share of edges that are `RelatedTo` (generic, low-information) | 301,007/572,778 = **52.5%** | 430,804/806,320 = **53.4%** |
| Share that are `IsA` (taxonomic) | 8.9% | 11.7% |
| Combined share of `HasProperty`+`PartOf`+`UsedFor` (clean, WorldTree-analog relation types) | ~2.9% | ~2.7% |
| Combined share of `DerivedFrom`+`Synonym`+`FormOf`+`HasContext`+`EtymologicallyRelatedTo` (lexical/morphological/topical, not definitional) | ~24.4% | ~24.3% |

**Reading -- the promiscuity risk, now quantified rather than just flagged:** ConceptNet has near-total lexical presence (98.3-100%) for exactly the vocabulary WorldTree misses, which superficially looks like the answer to the coverage gap. But the dominant relation by a wide margin, for BOTH WorldTree-covered and -uncovered words equally, is `RelatedTo` -- ConceptNet's catch-all relation with minimal specific semantic content (well-documented in the ConceptNet literature and confirmed here at >52% of mass regardless of which ARC-vocabulary slice you look at). The relation types structurally analogous to WorldTree's clean single-attribute tables (`IsA`, `HasProperty`, `PartOf`, `UsedFor`) are a combined ~12-15% minority. Using ConceptNet as a definitional supply source without hard-filtering to that minority would import roughly 4x as much promiscuous/generic-association noise as clean signal. This is independently corroborated by the substrate's own prior direct evaluation of ConceptNet for KG reasoning (`notes/exp_dev_to_skunkworks_CONCEPTNET_eval_RESULTS_factfab_PASS_inference_FAIL_verdict_VET_2026-06-19.md`): substrate cf-RPE multi-hop completion over ConceptNet HARD_FAILed vs. both exact transitive-closure (Hits@10 1.0) and frozen-bge single-hop cosine (0.502), landing at 0.451 -- i.e. ConceptNet's own structure was already measured, on a different task, to not reliably support structured completion despite its raw breadth. The fact-fabrication-bound (AUROC 0.812, knowing what it can't derive) HARD_PASSed, which is a genuinely useful property but is a refuse-gate capability, not a definitional-supply capability.

### 2d. Binder norms (`data/corpora/binder/binder2016_ratings.csv`) -- the "richer norms" option a642b513 named as option (B)

a642b513 (see KB-check above) already named "invest in a denser grounded foundation (CSLB/richer norms)" as one of three honest options when it found every grounded+relational source thin at the intersection, and separately measured "Binder-WT ~21" concepts (a narrow WorldTree x Binder overlap). This audit measured Binder's coverage against the FULL ARC vocabulary directly:

| Metric | Value |
|---|---|
| Total Binder concepts (65 neurally-motivated experiential-attribute dimensions each) | 534 |
| Overlap with full ARC vocab TYPES | 321/10,518 = **3.05%** |
| Overlap TOKEN-weighted | 14,624/160,549 = **9.1%** |

**Reading:** Binder is rich in DEPTH (65 dimensions per concept, where it applies) but the norming set itself is small and general-purpose (534 everyday nouns/verbs/adjectives, not curated for ARC science) -- it covers only 3-9% of ARC's vocabulary at all. This confirms a642b513's "NOT a dense science Binder" reading at full-ARC scale, not just on the narrow WT-Binder ~21-concept intersection: Binder is not a viable STANDALONE definitional-supply fix for ARC science, though it remains a legitimate depth-source for the small slice of concrete/perceptual concepts it does cover (consistent with the 07-25 featural-enrichment note ranking perceptual/multimodal grounding 3rd of 3 rungs for this specific abstract-science-vocabulary problem). CSLB norms (the other half of a642b513's option B) were checked and are **not present on disk** (see 2e).

### 2e. GenericsKB, CSLB norms, CK-12, other-subject OpenStax textbooks

**Not present on disk.** Checked via `find`/`glob` across `data/` for `*generic*`, `*cslb*`, `*mcrae*`, `*CK12*`, `*ck-12*`, `*openstax*`, `*glossary*`, `*wiktionary*`, `*dictionary*` -- zero hits beyond the single biology textbook (2b) and the Binder norms (2d). GenericsKB (Bhakthavatsalam, Richardson, Tandon & Clark, 2020, AI2 -- ~3.4M generic definitional/property sentences like "photosynthesis uses sunlight to produce energy") and CSLB property norms (Devereux et al. 2014, 638 concepts x ~2,725 features -- a642b513's own named option B) are both real, well-matched-to-this-need public resources but would need to be newly acquired; neither is a re-discovery of something already on disk.

---

## Part 3 -- Verdict: scalable or data-bound?

**Not a single answer -- the verdict splits cleanly by what "definitional" is asked to carry:**

- **SCALABLE, if the requirement is "every ARC-relevant concept has SOME clean, unambiguous definitional sentence available."** WorldTree def/prop alone reaches 69.0% token-weighted coverage; stacking already-on-disk WordNet glosses (zero new acquisition) pushes this to ~98.5% token-weighted. This requirement is close to solved with data already present -- the remaining work is wiring + sense-disambiguation, not corpus acquisition.

- **DATA-BOUND, if the requirement is "every ARC-relevant concept has a RICH, multi-relation, argument-structured, mechanism-specific profile"** (the depth the 07-25 featural-enrichment research argues is actually needed to separate near-neighbor concepts like hydro/nuclear/coal, since that discrimination requires BINDING several typed relations, not just knowing one gloss). At that bar, only ~25-47% of ARC's covered vocabulary clears even a 2-fact depth threshold, median depth is 1 fact/concept ARC-wide (reproducing, not just matching, the 128-tie shape), and there is no comparable already-on-disk resource that fixes this -- WordNet glosses are single, undifferentiated sentences (not typed multi-relation facts), the biology textbook glossary is equally single-sentence and narrow, and ConceptNet's typed-relation minority (~12-15% of its mass) is unverified for precision and already measured to underperform on structured completion.

**The honest framing for the Director: the coverage gap is closed (or closable near-free); the depth gap is real and requires either new typed-fact acquisition or a disambiguation-capable route into the near-universal-but-single-sentence sources.**

---

## Ranked sourcing recommendation

1. **(Zero-cost, highest leverage) Wire WordNet gloss into the concept encoder, with a sense-selection step.** The data is already on disk (92-98% coverage) and already touches the substrate's KB. The needed new work is NOT data acquisition -- it is picking the right sense per context (e.g., prefer the gloss whose WordNet domain/hypernym chain aligns with the concept's WorldTree KINDOF ancestor, or with the question's science-subdomain), a disambiguation-engineering problem with existing tractable approaches (Lesk-style overlap, hypernym-chain matching), not a corpus problem. This should be evaluated BEFORE any new corpus acquisition, since it is nearly free and closes by far the largest fraction of the breadth gap.

2. **Deepen WorldTree's own PROP-*/SOURCEOF/REQUIRES/CAUSE tables in the domains ARC weights heavily but WorldTree covers shallowly** (physics mechanics/forces, chemistry beyond acidity/reactivity/solubility, earth-science processes) — same provenance family (AI2/WorldTree-adjacent resources such as the OpenBookQA/QASC fact banks) would extend the SAME clean, typed-relation table format rather than introducing a new noise profile. Lower promiscuity risk than ConceptNet because it inherits WorldTree's existing curation standard.

3. **Acquire additional OpenStax textbook glossaries** (Physics, Chemistry 2e/Atoms First, an Earth-Science-equivalent title, Astronomy 2e) using the SAME already-built, already-proven `clean_cnxml.py` pipeline used for `Concepts of Biology`. Each book is expected to yield roughly the same order of magnitude as biology did (~900-1,000 clean one-line definitions) at near-zero marginal engineering cost (pipeline reusable, license already characterized as CC BY-NC-SA -- acceptable for non-commercial internal research per the existing `PROVENANCE.md`). This directly targets the physics/chemistry/earth-science vocabulary where WorldTree + the existing biology glossary are currently thinnest.

4. **GenericsKB or CSLB norms (new acquisition) as the next-tier candidate if 1-3 prove insufficient after wiring.** This is the direct successor to a642b513's own option (B) ("invest in a denser grounded foundation -- CSLB/richer norms"), now with a concrete reason to prefer GenericsKB first: it is purpose-built for generic DEFINITIONAL sentences at ~3.4M scale (matches this audit's "breadth" need), whereas CSLB is a small (638-concept), general-purpose feature-norm set like Binder -- a642b513 already measured Binder's WorldTree intersection at only ~21 concepts, and this audit independently confirms Binder covers just 3-9% of ARC's vocabulary at all (Part 2d), so CSLB should be expected to have a similarly narrow ARC-science footprint and is a DEPTH source for a small slice, not a breadth fix. Recommended only AFTER 1-3 are tried, since both require genuine new acquisition effort (vs. 1-3, which use data or pipelines already present).

5. **ConceptNet: last-resort, heavily-filtered supplement only.** If used at all, restrict strictly to `IsA`/`HasProperty`/`PartOf`/`UsedFor`/`DefinedAs`-type edges (the ~12-15% minority), explicitly excluding `RelatedTo`/`DerivedFrom`/`FormOf`/`HasContext`/`EtymologicallyRelatedTo` (the ~75-80% majority that carries lexical/topical noise, not definitional content). Even the filtered subset should be treated as unverified for precision until spot-checked, given the substrate's own prior HARD_FAIL finding on ConceptNet-based structured completion (Hits@10 0.451, worse than both exact closure and frozen-bge single-hop cosine).

---

## Cheap decisive test (recommended next step -- NOT dispatched, per task scope)

Before committing engineering effort to either the WordNet-sense-disambiguation route (recommendation 1) or new OpenStax acquisition (recommendation 3), the cheapest test that would discriminate between them: **on a stratified sample of 200 ARC science concepts (100 from the WorldTree-def/prop-covered set, 100 from the gap set), have a human (or a held-out, disk-verifiable oracle -- NOT an LLM judge, per the glass-box-at-inference invariant) rate whether the TOP-RANKED WordNet gloss (by simple hypernym-chain-to-WorldTree-KINDOF-ancestor matching, no learned model) is the ARC-relevant sense.** This measures the actual disambiguation hit-rate directly, rather than assuming it from the raw 92-98% coverage number, and is a half-day read-only measurement, not a build.

## Falsifiable predictions (HARD-PASS / HARD-FAIL, pre-registered for the cheap decisive test above)

**Prediction 1 (WordNet sense-disambiguation is a viable near-free depth-neutral fix for the breadth gap).**
P=0.40 (deflated from a naive prior of ~0.55-0.60 given how clean-looking the raw coverage numbers are; deflated because no direct precedent was checked in this drill for hypernym-chain-matching disambiguation accuracy specifically against WorldTree's own KINDOF taxonomy, and because polysemy at mean 5.1 senses/word is nontrivial; capped under the standard 0.50 novel-synthesis ceiling since this specific pairing -- WordNet sense selection anchored to WorldTree's own taxonomy -- is untested by anyone as far as this audit found).
**HARD-PASS:** simple hypernym-chain matching selects the ARC-relevant WordNet sense correctly on >=70% of the 200-concept stratified sample.
**HARD-FAIL:** correct-sense selection <=45% (worse than a naive "always pick sense #1 by WordNet's own frequency-ranked default," which is itself known to hit roughly 50-60% on general text) -- would mean the disambiguation problem is harder than assumed and WordNet's near-universal coverage is not actually usable without a heavier (learned) disambiguation mechanism, redirecting toward recommendation 2/3 (new typed-fact acquisition) as the higher-priority path instead.

**Prediction 2 (OpenStax-style textbook acquisition scales linearly with recommendation 3's estimate).**
P=0.35 (deflated; extrapolating a single biology-book yield of ~929 clean definitions to 4-5 additional subject books is a linear extrapolation with no cross-subject precedent checked in this audit -- physics/chemistry textbooks may have denser or sparser glossaries than biology's).
**HARD-PASS:** a newly-fetched OpenStax Physics or Chemistry glossary (same pipeline) yields >=600 clean glossary entries AND >=15% headword overlap with the currently-uncovered ARC physics/chemistry vocabulary specifically (not ARC vocabulary overall).
**HARD-FAIL:** yields <300 entries or <5% overlap with the target-domain gap vocabulary -- would mean OpenStax's glossary density varies too much by subject to treat as a reliable scaling assumption, and GenericsKB (recommendation 4) should be re-ranked above further OpenStax acquisition.

---

## Cross-thread synthesis

- **vs. the task-cited a642b513 (128-tie characterization):** this audit's full-ARC-vocab PROP-*-only measurement (mean 1.36 attrs/concept, frac_ge2=0.255) reproduces the SAME shallow, single-attribute-dominated shape as the cited 128-tie finding (~1.1 attrs/concept, frac_ge2=0.13) at a moderately richer absolute level -- consistent with, not contradicting, the prior characterization; the 128-tie thinness was not a sampling artifact.
- **vs. `notes/research_content_thin_concept_meaning_featural_enrichment_2026-07-25.md`:** that drill proposed binding WorldTree property-relation rows into concept vectors as the fix for fine-grained discrimination (hydro/nuclear/coal), citing WorldTree's SOURCEOF/PROP-RESOURCES-RENEWABLE/CAUSE/KINDOF rows as disk-verified for the ENERGY domain specifically. This audit shows that domain (energy: `water`, `energy`, `earth`, `plants`, `sun`, `light` all sit in the top-20 highest-coverage, highest-arity ARC words, per Part 1c's covered-word listing) is a BEST-CASE pocket, not representative -- ARC-wide, the same property-table depth collapses to median 1 fact/concept, meaning that drill's proposed fix will show its strongest results in exactly the domain it was designed and verified against, and materially weaker results in physics/chemistry/earth-science domains where WorldTree's own depth is thinner. This is a direct, actionable qualifier to that drill's Prediction 1 coverage diagnostic ("what fraction of concepts in the retrieval pool have >=1 usable WorldTree property-relation row at all") -- this audit supplies the ARC-wide baseline that diagnostic should be compared against.
- **vs. `notes/research_learned_meaning_frontend_differentiation_2026-07-25.md`:** that drill's proposed learned front-end trains on WorldTree relation-cues (SOURCEOF/REQUIRES/CAUSE/KINDOF, again energy-domain-verified). The same domain-representativeness qualifier applies: the learning signal's AVAILABILITY (not just its brain-fidelity) is domain-dependent, and this audit's cross-domain coverage table (Part 1c category breakdown) gives the concrete numbers needed to stratify that cell's exposure-count sweep by domain rather than treating WorldTree's relation coverage as uniform.
- **vs. `notes/exp_dev_to_skunkworks_CONCEPTNET_eval_RESULTS_factfab_PASS_inference_FAIL_verdict_VET_2026-06-19.md`:** that eval measured ConceptNet's multi-hop reasoning performance and found HARD_FAIL; this audit provides the missing mechanistic explanation (the >52% RelatedTo-relation dominance) for WHY that HARD_FAIL is unsurprising, independent of the specific cf-RPE architecture tested there -- the promiscuity is in the DATA, not only in the substrate's reasoning mechanism over that data.
- **New, not previously surfaced in this arc:** WordNet gloss coverage as a near-universal, already-on-disk, already-partially-wired definitional resource. None of the 07-24/07-25 drills in this arc named WordNet's gloss field specifically as a candidate supply source (they used WordNet only for synonym/hypernym relations via `SemanticHDEncoder`'s existing WordNet fusion, not its one-line definitions) -- this is the highest-leverage actionable finding of this audit.

---

## Substrate-product implications

If recommendation 1 (WordNet gloss + hypernym-chain sense-selection) clears its HARD-PASS band: the substrate gains a near-universal (92-98%), near-zero-marginal-cost definitional layer for ARC science concepts, addressing the BREADTH side of the grounded-meaning plan without new data acquisition -- directly complementary to, not a replacement for, the already-proposed WorldTree property-binding fix (which addresses DEPTH in the domains where WorldTree itself is rich). Together, a two-layer design -- WordNet gloss for "what is this, in one sentence" + WorldTree typed-relation binding for "what specifically distinguishes this from its near-neighbors, where such facts exist" -- is a more honestly-scoped foundation than relying on WorldTree alone, and is inspectable/glass-box at both layers (which gloss was selected and why; which WorldTree rows contributed). If recommendation 1 HARD_FAILs (disambiguation is harder than the raw coverage numbers suggest), the fallback path (new OpenStax textbook acquisition, ranked #3) is a known-pipeline, near-zero-engineering-risk option that directly targets the physics/chemistry/earth-science domains where this audit shows WorldTree and the existing biology glossary are both thinnest -- and is a strictly better bet than ConceptNet, whose promiscuity is now quantified (52%+ RelatedTo) and independently cross-validated against the substrate's own prior negative result.

---

## Citations / provenance (verified count)

This is a disk-audit note, not a literature scan -- no external web citations. All claims are grounded in the following on-disk artifacts, each directly read/parsed by scripts run in this session (paths given so any of these numbers can be reproduced):
1. `data/corpora/arc/ARC-V1-Feb2018-2/ARC-Challenge/*.jsonl`, `ARC-Easy/*.jsonl` (6 files, 7,787 questions).
2. `data/corpora/worldtree/WorldtreeExplanationCorpusV2.1_Feb2020/tablestore/v2.1/tables/*.tsv` (81 files) and the parallel `v2.0/tables/` directory (66 files, used only for the version-diff table-count comparison).
3. `data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt` + `PROVENANCE.md`.
4. `data/conceptnet/conceptnet-assertions-5.7.0.csv.gz` (streamed in full, 34,074,917 rows, not sampled).
5. `nltk.corpus.wordnet` (local WordNet corpus via the `nltk` package already installed in this environment).
6. `notes/research_content_thin_concept_meaning_featural_enrichment_2026-07-25.md`, `notes/research_learned_meaning_frontend_differentiation_2026-07-25.md` (read in full for cross-thread synthesis).
7. `notes/exp_dev_to_skunkworks_CONCEPTNET_eval_RESULTS_factfab_PASS_inference_FAIL_verdict_VET_2026-06-19.md` (read in full for the ConceptNet cross-validation).

**Honest gap:** the task-cited atom/note "a642b513" (128-tie WorldTree PROP-* characterization) could not be independently located on disk within this session's search budget (see KB-check paragraph above) -- its cited numbers (frac_ge2=0.13, ~1.1 attrs/concept, KINDOF 31.7%/SYNONYMY 19.2%) are taken as given from the task input, not independently re-verified, though the SHAPE of this audit's independent full-ARC-vocab measurement is consistent with them.
