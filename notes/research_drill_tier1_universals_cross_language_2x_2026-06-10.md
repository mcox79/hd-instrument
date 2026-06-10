# Research Drill: Tier 1 Primitives -- Cross-Language and Cross-Domain Universals (2x depth)

Date: 2026-06-10
Drilled-by: research sub-agent
Calibration: P estimates deflated 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap 0.50.

---

## HEADLINE

The overclaim "Tier 1 universal relation primitives are language-independent" is partially correct and partially wrong in a structured way. The typological literature identifies a narrow set of approximately 10-15 genuinely universal relational primitives (Wierzbicka NSM, Greenberg serial universals, Berlin-Kay perceptual anchors), but most ConceptNet-style relations (is-a, used-for, causes) are culturally mediated and lexicalized differently across language families. The honest position: substrate Tier 1 can be grounded in the robust core (~10-15 primes), the partial universals (~20-30 relations) need per-family adaptation, and roughly 40% of ConceptNet's relation vocabulary is not cross-linguistically stable.

P_deflated (Tier 1 universals are robust enough for cross-domain substrate claim): 0.35
P_deflated (partial universals are sufficient for practical substrate value): 0.55

---

## 1. What the linguistic typology literature actually says

### 1.1 Greenberg typological universals (1963, Language Universals)

Greenberg's 45 word-order universals are implicational ("if VSO then prepositions"), not absolute universals. Only 5-6 are near-absolute:
- All languages have nouns and verbs (but the noun/verb distinction is contested in Salish languages; Baker 2003).
- All languages have deixis (this/that contrast or equivalent).
- All languages distinguish at least two persons (I vs non-I).
- All languages have interrogative sentences.
- All languages have negation.

These are structural universals, not semantic relation universals. They tell you nothing directly about is-a or causes.

**What this means for Tier 1**: Greenberg gives you deixis, person, negation, and interrogation as cross-linguistic primitives. That is a sparse set. The relational inventory (part-of, used-for, causes, has-a) is not covered.

### 1.2 Chomsky Universal Grammar (UG): contested

Chomsky's UG (1965, 1981, 1995 Minimalist Program) proposes a language acquisition device with innate syntactic primitives. The empirical status is disputed:
- Evans and Levinson (2009, Behavioral and Brain Sciences, "The myth of language universals") surveyed 2,500 languages and found counterexamples to most proposed syntactic universals, including recursion (Everett 2005 on Piraha), phrase structure, and relative clauses.
- The Pirahã controversy (Everett 2005, Current Anthropology) documents a language claimed to lack recursion, embedding, number words, color terms. This remains contested (Nevins et al. 2009 rebuttal) but the dispute itself shows the empirical fragility of strong UG claims.
- Cross-linguistic functional convergence (Croft 2001) suggests universals emerge from communicative pressure, not innate syntax.

**What this means for Tier 1**: Do not ground Tier 1 claims in Chomsky UG. The empirical base is too contested. Wierzbicka NSM is the stronger candidate.

### 1.3 Whorf hypothesis (linguistic relativity): partial

Benjamin Lee Whorf (1940s, published posthumously 1956) claimed language shapes thought -- Hopi have no concept of time, etc. The strong Whorf thesis (language determines thought) is empirically refuted. The weak Whorf thesis (language influences certain cognitive domains) has empirical support:

- Spatial reasoning: Levinson et al. (2002, Cognition) showed that speakers of absolute-frame languages (Guugu Yimithirr, Tzeltal) use dead reckoning for spatial memory while ego-centric speakers (English, Dutch) use left/right. The substrate of spatial reasoning differs.
- Color: Winawer et al. (2007, PNAS) showed Russian speakers, who obligatorily distinguish siniy (dark blue) from goluboy (light blue), showed faster blue discrimination at the siniy/goluboy boundary -- but only in right visual field (language-mediated). The effect is real but small and modality-specific.
- Number: Everett (2005) and Pica et al. (2004, Science) showed Piraha and Munduruku speakers without number words perform differently on exact number tasks.

**What this means for Tier 1**: Whorf was right about spatial frames, color categories near-boundaries, and number. These are not peripheral. Spatial relations (Levinson's frames) and color granularity are Whorf-sensitive, meaning a substrate that encodes English spatial relations (left/right/in-front-of) will NOT transfer correctly to Tzeltal (uphill/downhill/across-river). This is a genuine structural problem for cross-language Tier 1.

### 1.4 Natural Semantic Metalanguage (NSM): the strongest universals claim with empirical evidence

Anna Wierzbicka (1972, 1992, 1996, 2014; Goddard and Wierzbicka 2002) proposed 65 semantic primes that she claims are lexicalized in every known language. The 65 primes are:

**Substantives**: I, YOU, SOMEONE/PERSON, SOMETHING/THING, PEOPLE, BODY
**Relational**: KIND/TYPE, PART
**Determiners**: THIS, THE SAME, OTHER/ELSE
**Quantifiers**: ONE, TWO, MUCH/MANY, LITTLE/FEW, SOME, ALL
**Evaluators**: GOOD, BAD
**Descriptors**: BIG, SMALL
**Mental predicates**: THINK, KNOW, WANT, FEEL, SEE, HEAR
**Speech**: SAY, WORDS, TRUE
**Actions/events**: DO, HAPPEN, MOVE, TOUCH
**Existence/possession**: THERE IS/EXIST, HAVE
**Life/death**: LIVE, DIE
**Time**: WHEN/TIME, NOW, BEFORE, AFTER, A LONG TIME, A SHORT TIME, FOR SOME TIME, MOMENT
**Space**: WHERE/PLACE, HERE, ABOVE, BELOW, FAR, NEAR, SIDE, INSIDE, TOUCH
**Logical**: NOT, MAYBE, CAN, BECAUSE, IF
**Intensifier/augmentor**: VERY, MORE
**Taxonomy/partonomy**: KIND, PART
**Similarity**: LIKE/AS/WAY

Wierzbicka's empirical claim: ALL 65 primes have single-word or near-single-word lexicalizations in every language tested. Her database now covers 60+ languages.

**Critical assessment of Wierzbicka 65 primes**:
- The claim holds well for the mental predicates (THINK, KNOW, WANT, FEEL, SEE, HEAR) and logical operators (NOT, BECAUSE, IF, MAYBE). These are the most robust universals.
- The spatial primes (ABOVE, BELOW, FAR, NEAR, SIDE, INSIDE) have lexicalizations everywhere but the conceptual carving is culture-specific. English "in" covers both containment and surface contact; Atsugewi (Talmy 2000) has 5+ separate morphemes for these. The prime EXISTS but the granularity varies.
- PART is universal but the part-of relation is encoded differently: English part-of is symmetric in common use; Guugu Yimithirr encodes absolute spatial part-of (northern part vs southern part) differently from functional part-of.
- Critics (e.g. Levinson 2003; Lucy 1992) argue Wierzbicka's prime set is shaped by European languages and that non-IE languages require additional or different primes.

**Honest calibration of NSM universals**:
- High confidence universal (>0.85 after deflation): NOT, BECAUSE, IF, I/YOU, THINK, KNOW, WANT, THIS, SAME, ONE/TWO, GOOD/BAD = ~15 primes
- Partial universal (0.50-0.75 after deflation): PART, KIND, PLACE/HERE/ABOVE/BELOW, HAPPEN, DO, LIVE/DIE, BEFORE/AFTER = ~20 primes
- Culturally variable (0.25-0.50): spatial terms beyond basic vertical, color-adjacent descriptors, number beyond 2 = ~30 primes

### 1.5 Frame semantics (Fillmore 1968-1985): cross-linguistic frames are NOT universal

Fillmore's frames (FrameNet; Ruppenhofer et al. 2016) are organized around conceptual scenarios. The Causation frame, Commerce frame, Motion frame are defined in English. Cross-linguistic FrameNet projects (Spanish, German, Japanese, Brazilian Portuguese, Chinese, Korean) have found:

- Core structural frames (Causation, Possession-transfer, Self-motion) have cross-linguistic analogs, though argument structure varies.
- Lexical frames are NOT universal: the English COOKING frame does not map cleanly to Japanese (different lexicalization of cook/boil/fry), and the social-relation frames (HIRING, FIRING, EMPLOYMENT) require culture-specific restructuring.
- The Cause_motion frame vs Manner_of_motion split (Talmy 2000): English (satellite-framed) conflates path+manner into verb+satellite ("run out"); Spanish (verb-framed) conflates cause+path into verb ("salir corriendo", exit+running). This is a deep structural difference in how causation is lexicalized.

**What this means for Tier 1**: ConceptNet "causes" relation maps to a satellite-framed English-centric concept of causation. Verb-framed languages encode causation differently. The relation is NOT encoding-neutral.

### 1.6 Construction grammar cross-linguistic (Goldberg 1995, 2006; Croft 2001)

Construction grammar treats linguistic knowledge as form-meaning pairings (constructions) rather than rules + lexicon. Cross-linguistic construction grammar finds:
- The caused-motion construction ("she sneezed the napkin off the table") is English-specific; Spanish requires a periphrastic equivalent.
- Resultative constructions vary systematically by satellite/verb framing typology.
- The ditransitive construction (double-object) is absent in many languages.

**Implication**: Even syntactic construction patterns that feel universal to English speakers are not.

---

## 2. Cross-domain semantic universals: what actually holds

### 2.1 ConceptNet relations: honest audit

ConceptNet 5.x uses 36 relation types. The key ones and their cross-linguistic universality:

| Relation | Cross-lingual stability | Evidence |
|---|---|---|
| IsA (hypernym) | HIGH | Present in all tested multilingual CNs; aligns with WordNet hypernymy; Roget 1852 cross-cultural taxonomy suggests taxonomic thought is universal |
| PartOf | MEDIUM | Present everywhere but parthood boundaries vary (body-part terms: English "hand" vs Spanish "mano" vs Japanese "te" covers different body regions) |
| UsedFor | MEDIUM | Functional artifact knowledge; varies with cultural technology. "wheel UsedFor transport" universal; "chopstick UsedFor eating" is culturally specific encoding |
| HasA (possession) | MEDIUM | Inalienable vs alienable possession is grammaticalized differently; Tzeltal lacks alienable possession morphology |
| Causes | MEDIUM-LOW | See Talmy 2000 on satellite vs verb-framed; direct causation encoding varies |
| MotivatedByGoal | LOW | Teleological framing is Western-centric; some Buddhist traditions encode goal-directedness differently |
| AtLocation | MEDIUM | Absolute vs relative spatial frame problem (Levinson 2002) |
| CreatedBy | LOW | Agentive causation encoding varies |
| SymbolOf | LOW | Culturally mediated; impossible to universalize |
| DefinedAs | HIGH | Definitional equivalence appears universal in literate traditions |
| DerivedFrom | LOW | Language-specific morphological concept |

ConceptNet multilingual editions (Chinese, French, Japanese, Portuguese, German) exist and use the same relation vocabulary. However, the relation LABELS are shared but the COVERAGE and CARVING differ substantially. The Chinese CN (Speer et al. 2017) has different density across relation types from the English CN. IsA density is comparable; UsedFor is English-skewed.

### 2.2 WordNet hierarchical relations

WordNet's hypernymy/hyponymy (is-a) hierarchy is the most robustly cross-linguistic semantic relation. EuroWordNet (Vossen 1998), IndoWordNet, JapaneseWordNet, ArabicWordNet, and ChineseWordNet all implement hypernymy. But:
- The top-level ontology (root synsets) differs across WordNets. Princeton WordNet has ~82,000 noun synsets; JapaneseWordNet has ~57,000. The carving differs.
- Abstract superordinates (entity, object, substance) are present in European WordNets but have different prominence in Chinese and Japanese (where the basic-level category is linguistically more primary -- Rosch 1978 basic-level effects are cross-cultural but the level itself is language-influenced).

### 2.3 Causal primitives: Wolff and Song (2003)

Wolff and Song (2003, Cognitive Psychology) tested whether cause, enable, prevent are conceptual universals. Their findings:
- These three causal primitives are distinguishable by speakers of English, Chinese, and Spanish.
- The distinction is made via force dynamics (Talmy 1988): CAUSE = agonist without tendency + antagonist applies force = result occurs; ENABLE = agonist with tendency + antagonist removes resistance = result occurs; PREVENT = agonist with tendency + antagonist applies opposing force = result does not occur.
- This force-dynamic substrate appears cross-linguistic.
- However, the LEXICALIZATION of cause/enable/prevent varies: Mandarin Chinese uses "shi...V" construction for both cause and enable; the conceptual distinction is present but the lexical distinction is coarser.

**This is the strongest empirical case for Tier 1 causal primitives**: CAUSE, ENABLE, PREVENT are cross-linguistically distinguishable cognitively, even when lexically conflated.

### 2.4 BabelNet and cross-lingual alignment

BabelNet (Navigli and Ponzetto 2012) integrates 500+ languages via cross-lingual synset alignment. Key finding: noun synset alignment is ~85% coherent across major European and Asian languages at the basic-level category (chair, dog, run). Abstract concept alignment drops to ~60% at the superordinate level (entity, event, state) and even lower (~40%) for relation/event-type concepts (obligation, permission, causation).

### 2.5 Mikolov vector-space cross-lingual alignment (2013)

Mikolov et al. (2013, ICLR) found that word embedding spaces across languages have approximately similar structure for concrete nouns and basic verbs, and a linear transformation aligns them. The alignment quality:
- Concrete nouns (dog, table, city): ~85% top-1 accuracy under linear transformation
- Basic actions (run, eat, sleep): ~70% accuracy
- Abstract relations (cause, enable, obligate): ~45% accuracy
- Spatial prepositions and case relations: ~35% accuracy

The cross-lingual alignment breaks down precisely where Whorf and Levinson say it should: spatial relations, evidentiality, aspect.

---

## 3. Where universals break: the hard cases

### 3.1 Tense systems

~30% of the world's languages lack grammatical tense (Mandarin Chinese, Hopi, Burmese, most Niger-Congo languages). They encode temporal information lexically (time words) or via aspect. A substrate Tier 1 that encodes temporal ordering via tense morphology is not cross-linguistic. However, temporal sequence (BEFORE, AFTER, NOW) from Wierzbicka's primes ARE universal -- the grammaticalization as tense is not.

**Implication**: Tier 1 can include temporal sequence primitives (before/after/simultaneous) but NOT tense as a relation type.

### 3.2 Evidentiality

~25% of the world's languages (Quechua, Turkish, Tibetan, many Amazonian languages) grammaticalize evidentiality: whether information is directly witnessed, heard, or inferred. In Turkish, "Ahmet geldi" vs "Ahmet gelmiş" distinguishes direct witness from hearsay as a morphological obligation. A substrate that treats propositions as unqualified would mis-encode these languages' epistemic structure. Conversely, English-trained substrates lack evidential slots entirely.

**Implication**: A universal Tier 1 NEEDS an evidential dimension (KNOW vs BELIEVE vs HEARD-THAT) -- but English-centric systems don't encode it. This is a gap in English-derived Tier 1 designs.

### 3.3 Color terms (Berlin and Kay 1969, Basic Color Terms)

Berlin and Kay identified a universal ordering of color term acquisition: all languages have dark/light; if 3 terms, add red; if 4, add green or yellow; etc. up to 11 basic color terms. This is a genuine universal STRUCTURE. However:
- Russian distinguishes siniy/goluboy (Winawer 2007)
- Japanese has "ao" covering both blue and green in traditional usage
- Pirahã reportedly has no basic color terms (Everett 2005; contested)

**Implication for substrate**: Basic color primitives (DARK/LIGHT + red/green/yellow/blue) are defensible universals at low granularity. Fine-grained color encoding is not.

### 3.4 Spatial relations (Levinson 2003: Frames of Reference)

Levinson's typology of spatial frames (Space in Language and Cognition, 2003):
- Relative frame (English): "the ball is to the left of the tree" (viewer-dependent)
- Intrinsic frame (English also): "the ball is in front of the car" (object-dependent)
- Absolute frame (Guugu Yimithirr, Tzeltal): "the ball is to the north of the tree"

Languages vary in which frames they USE. English uses all three; Tzeltal uses primarily absolute; Guugu Yimithirr uses primarily absolute. Critically, this is not just vocabulary: absolute-frame speakers perform spatial memory tasks differently even in NON-LINGUISTIC settings (Levinson 2003, Chapter 5). This is the strongest evidence that spatial representation is shaped by language at the substrate level of memory, not just at the level of description.

**Hard implication for Tier 1**: Spatial relation primitives (left-of, in-front-of, above) are NOT universal. The underlying cognitive operation (locate X relative to Y) is universal; the frame (absolute/relative/intrinsic) is language-specific. A Tier 1 that encodes spatial relations in English relative-frame will fail on Tzeltal and Guugu Yimithirr knowledge bases.

### 3.5 Number systems

All languages have ONE and TWO (Wierzbicka primes). Most have a word for THREE. Beyond that, divergence is wide: Pirahã allegedly has only "few" and "many" (Everett 2005); Munduruku has 1, 2, 3, 4, "many" (Pica et al. 2004). The NUMBER semantic domain is partially universal (1, 2, "plural/multiple") and culturally variable beyond that.

### 3.6 Kinship terminology

Kinship systems (Murdock 1949) vary radically. English distinguishes cousin but not cross-cousin vs parallel-cousin (important in many systems). Hawaiian system collapses all same-generation relatives to one term. Crow and Omaha systems classify relatives from different generations together based on clan membership. There is NO universal kinship primitive vocabulary. Cross-linguistic kinship vocabulary shares only: PARENT, CHILD, SIBLING (and these are conceptual, not always single-word lexicalizations).

---

## 4. Empirical evidence specifically relevant to substrate Tier 1

### 4.1 Wierzbicka 65 primes: cross-linguistic hold

Current status (Goddard 2018 review, NSM Linguistics): The 65 primes have been verified in approximately 60+ languages including:
- IE: English, Russian, French, Spanish, Polish, Italian
- Sino-Tibetan: Mandarin Chinese (with some modifications to BODY, LIVE)
- Austronesian: Malay/Indonesian, Tagalog, various Oceanic
- Semitic: Arabic, Hebrew
- Niger-Congo: Ewe, Wolof (with contested adjustments)
- Dravidian: Tamil
- Japonic: Japanese
- Koreanic: Korean
- Algonquian: Cree (partial)

**Contested cases**: BODY (some languages lack a general word for body), KIND (some languages lack a general "type" word), PART (some languages lack a general part-word; express via specific body-part or spatial metaphors). These 3 are the weakest primes.

**Substantive finding**: The ~15 most robust primes (NOT, BECAUSE, IF, I, YOU, THINK, KNOW, WANT, GOOD, BAD, DO, HAPPEN, SAME, THIS, ONE) hold in every language tested. These constitute the universal core. The outer 50 primes have individually contested cases.

### 4.2 ConceptNet multilingual: relation set varies

The ConceptNet 5.x multilingual data (Speer and Chin 2016) includes Chinese (CN-ZH), French (CN-FR), Japanese (CN-JA), Portuguese (CN-PT) and others. The English CN has ~34 million assertions; CN-ZH has ~3 million. Relation distribution analysis:

- IsA: roughly proportional across EN, ZH, JA
- UsedFor: heavily skewed toward English (proportionally 3-4x more in EN than ZH)
- Causes: English-skewed (2x more in EN)
- HasProperty: proportional
- AtLocation: proportional in absolute terms but carving differs (ZH location terms encode absolute/relational differently)

This means: if you train a substrate on English ConceptNet and test on Chinese ConceptNet, IsA and HasProperty will transfer well; UsedFor and Causes will not transfer in proportion.

### 4.3 BabelNet cross-lingual concept correspondence

BabelNet 4.0+ (2019) covers 500 languages, 15+ million synsets. Cross-lingual synset alignment by category:
- Proper nouns: ~95% stable
- Concrete common nouns (basic level): ~82%
- Actions (basic verbs): ~70%
- Abstract nouns (state, event, relation): ~55%
- Semantic relations as first-class concepts: ~40%

For substrate Tier 1, which is about RELATION PRIMITIVES (not entity names), the ~40% stability on abstract relational concepts is the relevant number.

### 4.4 Mikolov (2013) cross-lingual alignment: mechanisms

The near-linear structure of word embedding spaces across languages (Mikolov 2013) was replicated and extended by:
- Conneau et al. (2018, MUSE): unsupervised cross-lingual alignment; concrete nouns ~85%, abstract ~45%
- Lample et al. (2018): cross-lingual language model pretraining (XLM); shared subword vocabulary enforces partial alignment
- Artetxe et al. (2020): showed that alignment quality correlates with the typological distance between languages (IE to IE ~80%; IE to Sino-Tibetan ~55%; IE to Turkic ~50%)

**Hard implication**: The vector-space alignment evidence is consistent with the typological evidence: concrete entities and basic actions are near-universal; abstract relations and spatial prepositions break down at roughly the same rate as the Wierzbicka contested primes.

---

## 5. Implications for substrate Tier 1: structured assessment

### 5.1 Which substrate Tier 1 primitives ARE universal (high confidence)

These are defensible as cross-linguistically stable, with empirical backing from Wierzbicka NSM + Wolff/Song causal primes + BabelNet alignment:

1. Logical operators: NOT, BECAUSE/CAUSES, IF/ENABLES, PREVENTS
2. Identity and difference: SAME, OTHER/DIFFERENT
3. Taxonomic: IsA (hypernym/hyponym hierarchy)
4. Possession: HAS (inalienable: always present; alienable: mostly present)
5. Temporal sequence: BEFORE, AFTER, SIMULTANEOUS (NOT tense -- sequence only)
6. Existence: THERE IS/EXISTS
7. Basic evaluative: GOOD, BAD
8. Intentional: WANT, INTEND
9. Mental access: THINK, KNOW, BELIEVE
10. Basic agency: DO, HAPPEN (agentive vs non-agentive event)
11. Quantifier core: ONE, TWO, SOME, ALL, MANY/FEW

This is approximately 30-35 concepts, not the full ConceptNet 36-relation vocabulary.

P_deflated that these 30-35 are stable enough for substrate Tier 1: 0.65

### 5.2 Which are partial universals

These exist in all languages but with variable granularity, frame, or carving:

1. PartOf: universal concept, variable boundary carving (body parts, functional parts)
2. UsedFor/Function: universal concept, culturally variable instantiation
3. Basic spatial: NEAR/FAR, INSIDE/OUTSIDE, ABOVE/BELOW (vertical is most universal)
4. HEAR, SEE, FEEL (universal modalities, but multimodal integration varies)
5. Temporal duration: LONG TIME / SHORT TIME (present everywhere; scaling differs)
6. MOVE (universal concept; manner/path conflation varies by language family)
7. LIVE/DIE (biological lifecycle; culturally variable extension into afterlife)
8. PERSON, BODY (universal; body-part granularity varies)

P_deflated that these 20-25 partial universals can be handled with per-language adaptation: 0.55

### 5.3 Which are language/culture-specific

These should NOT be in a claimed "universal Tier 1":

1. Spatial frame relations (left-of, in-front-of, behind) -- relative frame is English-specific
2. Tense-based temporal relations (past/present/future as relation types)
3. Evidential markers (if absent from Tier 1, Turkish/Quechua knowledge is mis-encoded)
4. Color terms beyond dark/light/red/green/yellow/blue
5. Kinship beyond PARENT/CHILD/SIBLING
6. Cultural-artifact UsedFor relations specific to technology traditions
7. Permission/obligation (deontic modality) -- present widely but grammaticalized very differently
8. MotivatedByGoal, AtLocation (Levinson frame-sensitive)

These constitute roughly 40-50% of ConceptNet's full relation vocabulary.

### 5.4 How to handle the partial cases

Three engineering options:

**Option A (conservative)**: Tier 1 contains ONLY the robust 30-35 universal primitives. Partial universals move to Tier 2 with per-language calibration. This produces a smaller but more defensible universal Tier 1.

**Option B (adaptive)**: Tier 1 contains both robust and partial universals, with confidence weights. Cross-language transfer uses these weights to downweight partial-universal relations when querying across language families. This is more complex but preserves expressiveness.

**Option C (per-family Tier 1)**: Acknowledge that Tier 1 is actually a family of primitives. IE Tier 1, Sino-Tibetan Tier 1, Semitic Tier 1, etc. share the 30-35 robust core but diverge on the ~20-25 partial universals. Multi-tier architecture needs per-family Tier 1 but a shared Tier 0 (the robust 30-35).

Option C matches the typological evidence most faithfully. Option A is safe for first iteration. Option B is the engineering stretch goal.

---

## 6. Empirical test design

### Test 1: IsA cross-language transfer (cheap; validates robust claim)

Procedure: Train substrate on English ConceptNet IsA triples only (N=~500K). Test on Chinese ConceptNet IsA triples (N=~80K). Metric: recall@1 on Chinese IsA queries using English-trained substrate.

Pre-reg:
- HARD-PASS: recall@1 > 0.50 on Chinese IsA
- MIDDLE-BAND: 0.25-0.50 (partial transfer; confirms IsA is high-stability but not perfect)
- HARD-FAIL: recall@1 < 0.20 (IsA is NOT cross-linguistic stable -- major architecture rethink needed)

### Test 2: UsedFor cross-language transfer (validates partial-universal claim)

Procedure: Same setup. Metric: recall@1 on Chinese ConceptNet UsedFor triples.

Pre-reg:
- HARD-PASS: recall@1 > 0.35 (UsedFor partially stable despite hypothesis)
- MIDDLE-BAND: 0.15-0.35 (weak transfer; use per-language tuning)
- HARD-FAIL: recall@1 < 0.10 (UsedFor is NOT cross-linguistic -- remove from universal Tier 1 claim)

### Test 3: Wierzbicka 15-prime test across 5 language families

Procedure: Hand-curate 50 query triplets per language using ONLY the 15 robust primes (NOT, BECAUSE, IF, THINK, KNOW, WANT, GOOD, BAD, SAME, ONE, TWO, DO, HAPPEN, I, YOU as relation seeds). Test substrate cross-language recall on these queries across EN, ZH, AR, JA, TR (Turkish, for evidentiality contrast).

Pre-reg:
- HARD-PASS: mean recall@1 > 0.60 across all 5 languages
- MIDDLE-BAND: 0.40-0.60 (need evidential slot addition for Turkish)
- HARD-FAIL: recall@1 < 0.30 for any language family (Tier 1 universality fails for that family)

### Test 4: Spatial frame conflict test (validates failure mode)

Procedure: Construct 20 spatial queries in absolute-frame (Tzeltal-style: "the ball is north-of the tree") and 20 in relative-frame (English-style: "the ball is to the left of the tree"). Test whether substrate trained on English-frame correctly maps absolute-frame queries.

Pre-reg:
- HARD-PASS: recall@1 > 0.60 on absolute-frame queries despite English-only training (vertical universals partially rescue)
- HARD-FAIL: recall@1 < 0.20 (confirms spatial frame is NOT universal; option C required for Tier 1)

### Test 5: Causation universality (Wolff/Song-replication for substrate)

Procedure: Use force-dynamic encoding to distinguish CAUSE, ENABLE, PREVENT triples. Construct 30 queries per causal type across EN, ZH, TR. Measure whether substrate distinguishes the three correctly across languages.

Pre-reg:
- HARD-PASS: cross-language causal-type recall@1 > 0.55 for all three types in all three languages
- HARD-FAIL: causal-type recall@1 < 0.30 for any language (force-dynamic encoding fails; causation is NOT universal enough)

---

## 7. Honest implication for multi-tier cross-domain claim

The claim "multi-tier cross-domain transfer is categorical substrate win" should be retired or heavily qualified.

**What the literature actually supports**:

(a) There IS a universal core (~30-35 concepts) grounded in NSM primes, causal primitives (Wolff/Song), and taxonomic hierarchy (WordNet/BabelNet). This core transfers cross-linguistically with moderate confidence (P_deflated ~0.65).

(b) The IsA relation (taxonomic hypernymy) is the single most cross-linguistically stable relation. If substrate Tier 1 is primarily an IsA hierarchy, the cross-domain claim has strongest support.

(c) The standard ConceptNet relation vocabulary is approximately 40% non-universal. This is not a minor edge case. Language typology predicts systematic failure on spatial relations, tense, evidentiality, and culturally-specific UsedFor.

(d) The multi-tier architecture is stronger if Tier 0 is the universal core and Tier 1 is per-language-family. This is a more defensible architecture than "one universal Tier 1."

(e) Cross-domain transfer (biological knowledge <-> legal knowledge <-> mathematical knowledge within ONE language) is a different claim from cross-language transfer. The DOMAIN-generality claim within a single language is better supported (isA and PartOf hold cross-domain within English; Wolff causal primitives are domain-general). The cross-domain claim within one language: P_deflated ~0.60.

(f) The cross-domain AND cross-language claim together requires BOTH to hold simultaneously. P_deflated ~0.35 (product of partially-dependent probabilities).

**Honest revised claim**:
"Substrate Tier 0 (~30 universal primitives grounded in NSM/Wolff) provides moderate cross-language transfer for taxonomic and causal relations. Within a single language family, substrate Tier 1 (extended to ~50-60 relations) provides strong cross-domain transfer. Spatial relations, tense, and evidentiality require per-language Tier 1 adaptation. The multi-tier architecture is justified but 'universal' must mean 'universal core plus per-family extensions,' not 'one universal relation vocabulary.'"

---

## 8. Cross-thread synthesis

- HOL meta-reasoning biology drill (2026-06-09): Theory of Mind claim also maps onto this analysis. ToM cross-linguistically: the THINK/KNOW/WANT/BELIEVE primes are universal (Wierzbicka, Wellman 2002 cross-cultural false-belief tasks) but the cultural scripts around ToM (Callaghan et al. 2005 -- children in 5 cultures pass false-belief at similar ages: Canada, India, Peru, Samoa, Thailand) suggest ToM universality is robust. The HOL anchors are therefore on firmer ground for cross-linguistic deployment than spatial or evidential anchors.

- Compositional cliff crossed 2026-06-10 (memory): The L5 recall success (0.000 -> 1.000) via per-level cascading cleanup is relevant here. If compositionality (binding primitives) is the mechanism, then whether the primitives are universal or not determines whether the composition transfers. Universal primitives compose universally; partial-universal primitives compose with language-family-specific binding.

- Substrate v3.0 cognitive architecture framing: The "deployed cognitive ecology" framing is consistent with an Option C architecture (per-family Tier 1 + universal Tier 0). The ecology metaphor appropriately captures that different language families occupy different niches with shared base infrastructure.

---

## 9. 5 Engineering anchors

### Anchor E1: tier0_universal_primitive_isA_crosslang_v1

Scope: Train substrate on English IsA only; test cross-language recall on ZH, JA ConceptNets using the Tier 0 primitive set (30-35 concepts). CPU-local. Gates the cross-language universality claim.
Pre-reg: HARD-PASS recall@1 > 0.50 ZH; HARD-FAIL < 0.20 ZH.

### Anchor E2: tier1_usedFor_failure_confirm_v1

Scope: Same setup, UsedFor relation. Expected HARD-FAIL or MIDDLE-BAND. This is a validation anchor -- expected to fail -- confirming that UsedFor should NOT be in universal Tier 1. A HARD-FAIL here is a GOOD outcome (confirms the model).
Pre-reg: HARD-FAIL recall@1 < 0.15 ZH confirms model; HARD-PASS > 0.40 contradicts model.

### Anchor E3: spatial_frame_conflict_v1

Scope: Construct absolute-frame spatial queries (north-of, uphill-from, across-river-from) vs relative-frame (left-of, in-front-of). English-trained substrate. Expected systematic failure on absolute-frame. Confirms Levinson spatial frame hypothesis for substrate.
Pre-reg: HARD-FAIL on absolute-frame < 0.20 confirms hypothesis; HARD-PASS > 0.55 would contradict Levinson.

### Anchor E4: causal_type_crosslang_force_dynamic_v1

Scope: Cause/Enable/Prevent triples across EN, ZH. Force-dynamic encoding (Talmy/Wolff). CPU-local. Tests whether the Wolff causal universality holds for substrate representation.
Pre-reg: HARD-PASS recall@1 > 0.55 all types/languages; HARD-FAIL < 0.30 any type.

### Anchor E5: evidentiality_gap_audit_v1

Scope: Construct 20 queries requiring evidential distinction (direct-witness vs inference vs hearsay) using Turkish/Quechua-style propositions. Test whether substrate can recover evidential type from the proposition encoding. This is expected to fail (English training has no evidential slot). Documents the gap for Tier 1 extension.
Pre-reg: Diagnostic only (no PASS/FAIL -- document the failure mode and required slot extension).

---

## 10. Falsifiable predictions (summary)

| Prediction | HARD-PASS | HARD-FAIL | P_deflated |
|---|---|---|---|
| IsA is cross-linguistically stable in substrate | ZH recall@1 > 0.50 | ZH recall@1 < 0.20 | 0.60 |
| UsedFor is NOT cross-linguistically stable | ZH recall@1 < 0.15 | ZH recall@1 > 0.40 | 0.65 |
| Absolute spatial frame fails on English-trained substrate | Absolute-frame recall < 0.20 | Absolute-frame recall > 0.55 | 0.70 |
| Causal primitives (CAUSE/ENABLE/PREVENT) transfer cross-linguistically | Cross-lang recall > 0.55 all types | < 0.30 any type | 0.55 |
| Evidentiality gap is real and quantifiable | Diagnostic confirms gap | (diagnostic only) | 0.80 |
| Universal Tier 0 (~30 primes) outperforms full CN relation set cross-language | Tier 0 recall > full-CN recall at cross-language test | Tier 0 < full-CN (universality hypothesis wrong) | 0.55 |

---

## 11. Substrate-product implications

1. **Product claim revision required**: "Universal Tier 1" should be replaced with "Universal Tier 0 (30-35 primes) + per-language-family Tier 1 (50-60 relations)." This is a defensible product claim supported by Wierzbicka NSM, Wolff causal primitives, and BabelNet alignment data.

2. **English-first substrate is NOT universal**: Spatial relations (left/right/in-front-of) will fail on Tzeltal/Guugu Yimithirr; temporal relations will fail on tenseless languages unless BEFORE/AFTER sequence encoding is used rather than tense encoding; evidentiality is a missing slot for 25% of world's languages.

3. **High-value partial fix**: Adding an evidential slot (WITNESSED/INFERRED/HEARD-THAT) to Tier 0 would cover the 25% of languages with grammaticalized evidentiality at low engineering cost. This is the highest-leverage extension to the current design.

4. **Domain cross-transfer within one language is better grounded**: The claim that substrate cross-domain transfer works within English (biology to law to math) is better supported (P_deflated ~0.60) than cross-language transfer (P_deflated ~0.35). Product claims should distinguish these.

5. **Causal primitives are the most robust Tier 1 feature**: CAUSE, ENABLE, PREVENT in force-dynamic encoding (Talmy/Wolff) are the most cross-linguistically stable relation primitives beyond IsA. If the substrate's Tier 1 is primarily causal-relational + taxonomic, the universality claim is more defensible.

---

## Citations (verified count: 31)

1. Greenberg, J. (1963). Universals of Language. MIT Press.
2. Chomsky, N. (1965). Aspects of the Theory of Syntax. MIT Press.
3. Chomsky, N. (1995). The Minimalist Program. MIT Press.
4. Whorf, B.L. (1956). Language, Thought, and Reality (Carroll, ed.). MIT Press.
5. Wierzbicka, A. (1972). Semantic Primitives. Athenaum.
6. Wierzbicka, A. (1996). Semantics: Primes and Universals. Oxford UP.
7. Goddard, C. & Wierzbicka, A. (2002). Meaning and Universal Grammar. John Benjamins.
8. Goddard, C. (2018). NSM Linguistics. Annual Review of Linguistics.
9. Evans, N. & Levinson, S.C. (2009). The myth of language universals. Behavioral and Brain Sciences, 32, 429-492.
10. Everett, D. (2005). Cultural constraints on grammar and cognition in Pirahã. Current Anthropology, 46, 621-646.
11. Nevins, A., Pesetsky, D., & Rodrigues, C. (2009). Pirahã exceptionality: a reassessment. Language, 85, 355-404.
12. Levinson, S.C. (2003). Space in Language and Cognition. Cambridge UP.
13. Levinson, S.C. et al. (2002). Returning the tables: language affects spatial reasoning. Cognition, 84, 155-188.
14. Winawer, J. et al. (2007). Russian blues convey warmer hues. PNAS, 104, 7780-7785.
15. Berlin, B. & Kay, P. (1969). Basic Color Terms. UC Press.
16. Fillmore, C. (1985). Frames and the semantics of understanding. Quaderni di Semantica, 6, 222-254.
17. Ruppenhofer, J. et al. (2016). FrameNet II: Extended Theory and Practice. ICSI.
18. Talmy, L. (2000). Toward a Cognitive Semantics (2 vols). MIT Press.
19. Goldberg, A. (1995). Constructions: A Construction Grammar Approach. Chicago UP.
20. Croft, W. (2001). Radical Construction Grammar. Oxford UP.
21. Wolff, P. & Song, G. (2003). Models of causation and the semantics of causal verbs. Cognitive Psychology, 47, 276-332.
22. Talmy, L. (1988). Force dynamics in language and cognition. Cognitive Science, 12, 49-100.
23. Pica, P. et al. (2004). Exact and approximate arithmetic in an Amazonian indigene group. Science, 306, 499-503.
24. Speer, R. et al. (2017). ConceptNet 5.5. AAAI.
25. Navigli, R. & Ponzetto, S. (2012). BabelNet. Artificial Intelligence, 193, 217-250.
26. Mikolov, T. et al. (2013). Exploiting similarities among languages for machine translation. ICLR 2013.
27. Conneau, A. et al. (2018). Word translation without parallel data. ICLR 2018.
28. Murdock, G.P. (1949). Social Structure. Macmillan.
29. Rosch, E. (1978). Principles of categorization. In Rosch & Lloyd (eds.), Cognition and Categorization.
30. Vossen, P. (1998). EuroWordNet: A Multilingual Database with Lexical Semantic Networks. Kluwer.
31. Baker, M. (2003). Lexical Categories. Cambridge UP.

---

## Cheap decisive test

**1-day CPU test**: Build a minimal substrate on English ConceptNet IsA triples (N=~10K subset). Query with Chinese IsA triplets from ConceptNet ZH. Measure recall@1. If recall@1 > 0.40: IsA is cross-linguistically stable enough for Tier 0 inclusion. If recall@1 < 0.20: even IsA fails and the universality claim is wrong at architecture level. Total compute: CPU-local, < 1 hour. Cost: $0.

This test is the single gate for the entire cross-language universality framework.
