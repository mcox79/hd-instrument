# Research: is the upstream input itself (frozen word2vec, one vector per surface form) the
# bottleneck, and do static sense/multi-prototype embeddings fix it cheaply?

Filed by: research sub-agent, 2026-09-03. Direct follow-up to the same-day
`research_wsd_contextual_encoding_glassbox_mechanisms_2026-09-03.md` and
`research_wsd_bem_lite_biencoder_design_validation_2026-09-03.md` — those drills fixed the QUERY
CONSTRUCTION (how context is turned into a vector) holding the input embedding fixed. This drill asks
the layer below: is the frozen w2v INPUT itself (one vector per surface form, frequency-dominated) the
real bottleneck, and can a static per-sense embedding swap fix it without touching query construction?
4 parallel Sonnet lit-scan lanes (multi-prototype/multi-sense embeddings; retrofitting/KG-embedding;
mental-lexicon brain mapping; circularity/decisive-attribution), all live WebSearch/WebFetch this pass.

## HEADLINE

**No — three independently-converging findings say static per-synset/multi-prototype embeddings are
not the cheap upstream fix, and this drill's brain-mapping lane independently re-derives the SAME
conclusion the 09-03 companion note reached from a different literature (psycholinguistics of ambiguity
resolution), now triangulated a second time from the homonymy/polysemy dissociation literature
specifically.** (1) **Brain-fidelity is wrong for THIS project's failure case.** The mental-lexicon
literature splits cleanly: true homonyms (unrelated senses) are supported by discrete, competing,
frequency-graded entries (Beretta, Fiorentino & Poeppel 2005, MEG M350; Frazier & Rayner 1990); related
polysemous senses are supported by ONE shared representation with frequency-INDEPENDENT availability
(Klepousniotou 2002/2007's N400 data; Rodd, Gaskell & Marslen-Wilson 2002/2004's "ambiguity advantage,"
modeled as one broadened attractor basin, not competing basins). The project's own failure case — a
rare sense whose context TOPICALLY OVERLAPS its dominant twin — is the polysemy case by definition, and
that is exactly where a discrete one-vector-per-synset design is the WRONG brain model, not an
unproblematic simplification. (WordNet itself doesn't distinguish homonymy from polysemy at the synset
level, so the candidate output space inherits this unfaithfulness regardless of embedding choice — a
separate, orthogonal caveat.) (2) **The one clean empirical number available says sense embeddings
alone underperform a plain supervised baseline:** AutoExtend (Rothe & Schütze, ACL 2015)'s own Table 3 —
sense/lexeme embeddings alone score 58.3/64.3 (Senseval-2/3), BELOW the plain supervised IMS classifier
(65.2/72.3); combining both gives only +1.3-1.4 F1. (3) **Every deployed sense-embedding WSD system
dodges its own context-side circularity by falling back to the exact frozen, sense-conflated word
vector the method was invented to replace** — AutoExtend's context vector is "all word vectors of the
context... excluding the test word" (plain w2v); Iacobacci, Pilehvar & Navigli (ACL 2016) integrate
SensEmbed's target-sense vector but use PLAIN Word2vec for context. Camacho-Collados & Pilehvar's 2018
JAIR survey names the gap directly: "the context words in these models are not disambiguated."

## 1. Multi-sense / multi-prototype embeddings — mechanism split, numbers, glass-box feasibility

**Unsupervised (cluster raw contexts, no WordNet tie):** Reisinger & Mooney 2010 (NAACL) — movMF
clustering of context windows, WordSim-353 ρ=0.77 vs 0.53 single-prototype. Huang et al. 2012 (ACL) —
introduces SCWS; multi-prototype AvgSimC=65.7 vs their own single-prototype 58.6. Neelakantan et al.
2014 (EMNLP, MSSG/NP-MSSG) — online clustering during skip-gram training, SCWS 69.3 (300d). All three:
inference is automatic (nearest-cluster assignment, part of the same procedure — **no separate WSD
step, no circularity**), fully glass-box (word2vec-class training only), but prototypes are NOT tied to
WordNet synsets — they don't map onto the candidate output space this project needs.

**Knowledge-based (one vector per WordNet/BabelNet synset — the 1:1-with-our-output-space case):**
SensEmbed (Iacobacci, Pilehvar & Navigli, ACL 2015) needs BabelNet + Babelfy + Wikipedia-scale
sense-tagged corpus — **fails the glass-box constraint outright**, and reports no WSD accuracy, only
similarity (avg Spearman 0.794 vs 0.644 baseline). DeConf (Pilehvar & Collier, EMNLP 2016) is WordNet-
only (Personalized PageRank sense-biasing + push on pretrained w2v) — glass-box feasible, but **reports
no WSD accuracy at all**, similarity only (SCWS AvgSimC=71.5). AutoExtend (Rothe & Schütze, ACL 2015) is
WordNet+w2v-only, glass-box feasible, and is the ONE source with real WSD numbers — see HEADLINE point 2.

## 2. Retrofitting / KG embedding

Faruqui et al. 2015 (NAACL) retrofits one vector PER WORD TYPE (not per sense) toward its pooled
WordNet-neighbor average — **confirmed a red herring for this problem**: nothing in the objective
privileges a minority sense; it smooths toward a symmetric blend of ALL the word's senses' neighbors.
No WSD evaluation in the paper at all. NASARI (Camacho-Collados et al. 2016) gives per-concept vectors
but requires BabelNet+Wikipedia — fails glass-box. Goikoetxea, Soroa & Agirre 2015 (NAACL) — PPR random
walk over WordNet+glosses → word2vec-trained word vectors — glass-box feasible (WordNet+word2vec only)
but reports similarity/relatedness only, no WSD number. Saedi et al. 2018 is Katz-similarity matrix
inversion (not node2vec/DeepWalk as sometimes assumed), scales badly (full 155K-synset WordNet was
infeasible even on a 430GB-RAM machine), word-level not sense-level output, no WSD number. **No source
in this lane reports a WSD F1 comparable to the MFS-65.5/BERT-73.7/BEM-79.0 numbers already established
in the companion note** — this entire family has never been benchmarked on the standard task.

## 3. Brain mapping — see HEADLINE point 1. One addition: Klein & Murphy 2001 / Foraker & Murphy 2012
dissent, arguing for sense-enumeration even in polysemy — genuinely unresolved (task-dependent per
Eddington & Tokowicz's review), not a clean refutation of the majority view. Treat as an open dispute,
not settled against per-sense entries — but the majority/mechanistic (MEG, N400) evidence still argues
against this drill's hypothesized fix for exactly the project's failure population.

## 4. The decisive attribution — relocation, not a fix (numbers)

Confirmed circular in practice, with hard numbers: AutoExtend-alone 58.3 < plain-supervised IMS 65.2;
Iacobacci et al. 2016's best combination gains only +0.1-0.8 F1 over IMS alone; in the unified benchmark
(Raganato, Camacho-Collados & Navigli, EACL 2017), Babelfy (the closest deployed knowledge-embedding-
adjacent system) scores BELOW the WordNet-first-sense frequency baseline on 2 of 5 test sets (63.5 vs
66.2; 51.6 vs 55.2). **No paper in any lane reports a least-frequent-sense/rare-sense breakdown for any
sense-embedding method** — an absence that, combined with the above, is itself informative rather than
neutral (a real rare-sense win would be reported).

## Cheap decisive test (registered as a confirmatory NULL test, not a promising build)

Build the one glass-box-feasible per-synset candidate — DeConf-style WordNet-only PPR sense-biasing
pushing existing frozen w2v toward each sense's WordNet-neighborhood region (no BabelNet/Babelfy/corpus
needed) — as a drop-in input swap into the SAME diagnostic-query readout (same gloss targets, same
argmax), scored on the SAME subordinate held-out set from the companion note, stratified two ways:
(a) TOPIC-CONFOUNDED vs TOPIC-DISTINCT (existing split), (b) HOMONYM-type vs POLYSEME-type pairs (new
split this drill's brain-fidelity finding requires). Mandatory controls: same-dimensionality
RANDOM-vector perturbation (rules out "any push off the base vector helps"); report both splits, not
just the aggregate.

## Falsifiable predictions

**HARD-PASS:** CI-separated gain over the bag-of-words+gloss floor on TOPIC-CONFOUNDED/POLYSEME items
specifically, surviving the random-vector control. (This would falsify all three of this note's
converging priors and re-open static per-sense embeddings as a real candidate — a high-value surprise
if it happens, precisely because the priors are unusually well-triangulated.)

**HARD-FAIL:** no CI-separated gain on TOPIC-CONFOUNDED/POLYSEME items; OR any observed gain disappears
under the random-vector control; OR (the brain-fidelity-consistent pattern) any real gain is confined to
HOMONYM-type items while POLYSEME/TOPIC-CONFOUNDED items show no gain or a loss — this specific
asymmetry would be a positive, actionable confirmation of the homonymy/polysemy dissociation finding,
not just a null result, and would argue for permanently deprioritizing static per-sense-embedding
architectures for this project's actual (mostly-polysemous) failure population.

**P_deflated: 0.10** (raw ~0.15-0.20 — three converging negative signals of different kinds: a
brain-fidelity mismatch specific to this project's failure population, one clean empirical number
showing underperformance vs. a plain supervised baseline, and a confirmed circularity-relocation pattern
across every real deployed system — deflated 0.10 per the mandatory penalty, well below the arm 1/2/3
candidates already registered in the companion note at 0.40/0.35). This is registered as a LOW-priority
confirmatory test, not a competing primary build.

## Cross-thread synthesis

- **Independently re-derives, via a different literature (homonymy/polysemy neurolinguistics rather
  than pure ambiguity-advantage psycholinguistics), the SAME conclusion as the same-day
  `research_wsd_contextual_encoding_glassbox_mechanisms_2026-09-03.md`:** related/topically-overlapping
  senses need ONE representation dynamically reshaped by context, not discrete competing entries. That
  note's arms 1-3 (dependency-filtered second-order context vector; exemplar retrieval instead of
  centroid averaging; small recurrent contextual encoder / BEM-lite) remain the correctly-targeted
  upstream fix; this drill rules OUT the sibling hypothesis (fix the STATIC INPUT instead of the QUERY
  CONSTRUCTION) as the higher-probability lever, for this project's specific failure population.
- **Does not conflict with `research_wsd_bem_lite_biencoder_design_validation_2026-09-03.md`** — that
  note's BiGRU contextual encoder over frozen w2v is UNAFFECTED by this finding; it changes query
  construction on top of the same frozen input, not the input itself, and remains the highest-registered
  candidate (P_deflated 0.35) of the three live threads on this topic.
- **ORGAN_MAP C3 (semantic control / multiplicative per-dimension gain):** already HARD_FAILED on
  estimation-noise grounds. This drill's finding is a DIFFERENT reason for the same practical
  conclusion (don't invest in re-weighting/re-deriving a per-word-type static vector) — C3 failed on
  noise, this fails on brain-fidelity + empirical precedent + circularity, for a related-but-distinct
  representational family (per-sense static vectors rather than per-dimension gains on one vector).
- **`research_subordinate_sense_topdown_predictive_precision_2026-09-02.md`:** that drill found no
  human behavioral benchmark exists for `a_s` at WordNet-granularity, and flagged discourse-scale
  generalized-event conflict as the one literature-corroborated untested lever. This drill adds a
  second, orthogonal reason the "richer static representation" family (of which per-synset embeddings
  are a member) is not where the fix lives — consistent with that note's broader pattern that local/bag/
  static fixes keep failing while discourse/context-structured fixes keep getting corroborated.

## Substrate-product implications

Do not build a static per-synset/multi-prototype embedding swap as a primary next step — the three
converging findings (brain-unfaithful for this project's actual failure population, empirically
underperforms a plain supervised baseline in the one clean number available, and every real system
circularly falls back to the same frozen sense-conflated context vector) all point away from it, and
none of the three companion 09-03 notes' registered candidates (arm 1, arm 2, arm 3/BEM-lite) are
affected — they remain the correctly-targeted builds. If capacity opens for a confirmatory test, the
value is in the STRATIFIED NULL RESULT itself (confirming the homonym/polyseme asymmetry) more than in
any hoped-for gain — it would close off this entire representational family with evidence specific to
this substrate, freeing attention fully onto the contextual-encoding arms already in flight.

## Citations (verified count)

**17 primary/secondary sources checked this pass**, all via live WebSearch/WebFetch (not memory):
Reisinger & Mooney 2010 (NAACL); Huang, Socher, Manning & Ng 2012 (ACL); Neelakantan, Shankar, Passos &
McCallum 2014 (EMNLP, MSSG/NP-MSSG); Iacobacci, Pilehvar & Navigli 2015 (ACL, SensEmbed); Pilehvar &
Collier 2016 (EMNLP, DeConf); Rothe & Schütze 2015 (ACL, AutoExtend — Table 3/4 read directly); Faruqui,
Dodge, Jauhar, Dyer, Hovy & Smith 2015 (NAACL, retrofitting); Camacho-Collados, Pilehvar & Navigli 2016
(AIJ/NAACL-2015 workshop, NASARI); Goikoetxea, Soroa & Agirre 2015 (NAACL); Saedi, Branco, Rodrigues &
Silva 2018 (ACL RepL4NLP); Camacho-Collados & Pilehvar 2018 (JAIR 63:743-788, survey, two independent
full-text passes); Iacobacci, Pilehvar & Navigli 2016 (ACL, "Embeddings for WSD: An Evaluation Study");
Raganato, Camacho-Collados & Navigli 2017 (EACL, unified evaluation framework); Rodd, Gaskell &
Marslen-Wilson 2002 (J Mem Lang) / 2004 (Cognitive Science) — carried forward, re-verified this pass;
Frazier & Rayner 1990 (J Mem Lang); Beretta, Fiorentino & Poeppel 2005 (Cognitive Brain Research);
Klepousniotou 2002 (Brain & Language) / Klepousniotou & Baum 2007; Klein & Murphy 2001 (J Mem Lang,
abstract 403-blocked, corroborated via secondary sources) / Foraker & Murphy 2012; Pustejovsky 1995;
Vicente & Falkum 2017 (Oxford Research Encyclopedia). Blevins & Zettlemoyer 2020 (BEM) numbers carried
forward from the companion 09-03 note, not re-verified this pass.

## Caveats on this note

- Per the mandatory lit-scan calibration penalty, the P estimate above is deflated to 0.10 (raw
  0.15-0.20), below the novel-synthesis cap.
- This note does not itself run the cheap decisive test — building the DeConf-style WordNet-only PPR
  input swap and re-scoring with the mandatory homonym/polyseme stratification is the next actionable
  step if this low-priority confirmatory test is picked up.
- `research_field_advisor.py`'s candidate list is scoped to substrate-physics and is not applicable to
  this cognitive-neuroscience/NLP question, same disposition as the three companion 09-03 notes.
- The Klein & Murphy / Foraker & Murphy dissent means the brain-fidelity argument in this note is
  majority-evidence, not unanimous — flagged, not glossed over.
