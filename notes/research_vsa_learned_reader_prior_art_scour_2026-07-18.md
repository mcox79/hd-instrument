# Research: prior-art scour — has anyone built a LEARNED vector-symbolic reader that forms grounded role-filler reasoning-maps for a compositional reasoner?

**Date:** 2026-07-18. **Filed by:** research (3 parallel Sonnet lit-scan lanes, Sonnet synthesis).
**Trigger:** direct prior-art scour request — one of 4 sibling scours (this one: VSA/HDC implementation
literature; siblings: semantic-parsing, comprehension-models, neurosymbolic-reading) feeding a director
synthesis on whether "a learned VSA reader that maps text into role-filler bound situation vectors for a
compositional reasoner" is already-done / partially-done / a genuinely novel assembly.

**Method note (2x/overlap discipline):** two very recent sibling notes already exist in this arc and were
read FIRST to avoid re-drilling: `research_vsa_hdc_state_of_mind_prior_art_scour_2026-07-17.md` (deeply
covers Plate HRR, Kanerva HD algebra, Eliasmith SPA/Nengo/Spaun, Gayler MAP, resonator networks, BEAGLE,
Random Indexing, QAVSA — established, cited not re-derived below) and
`research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md` (covers recursive/nested binding,
acquisition/neuroscience of comprehension, and the supervised-vs-grounded fairness ceiling). This note's
job was to fill the genuinely UNCOVERED ground for the specific "LEARNED parse into VSA" question: Tensor
Product Representation networks (Smolensky/McCoy/Schlag/Palangi — the learned-binding lineage), PSI
(Cohen/Widdows — VSA reasoning over hand-extracted triples), holographic/VSA knowledge-graph embeddings
(HolE/ComplEx — learned binding over pre-curated KGs, not text), VSA analogical reasoning (Kanerva's
"dollar of Mexico," Emruli & Sandin), and recent 2020-2025 HDC-NLP (Rahimi text classification, Kleyko
survey, NVSA, "Attention as Binding"). 3 parallel Sonnet lit-scan lanes dispatched on exactly these gaps.

---

## HEADLINE

**"A learned VSA/HDC reader that maps raw grounded natural-language text into compressed hyperdimensional
role-filler bindings, consumed by a separate compositional reasoner" is CONFIRMED, across three
independent lit-scan lanes AND two sibling scours (four total independent searches now), to be an
UNBUILT combination — but every one of its constituent pieces exists separately, in two research
lineages that have stayed almost entirely uncross-pollinated: (1) a LEARNED-binding lineage (Smolensky's
Tensor Product Representations, made trainable by McCoy/Schlag/Palangi) that never adopted Plate's
compressed circular-convolution/HRR representation and never targeted natural sentences at scale
(bAbI/SQuAD/MNLI-era synthetic-to-mid benchmarks only); and (2) a compressed-VSA/HRR-binding lineage
(Plate, Kanerva, Eliasmith/SPA, resonator networks, HolE/ComplEx) that is either HAND-BUILT at the
text-to-structure step (SPA/Nengo sentence encoding, PSI's SemRep-extracted triples) or never touches raw
text at all (HolE/ComplEx learn only over pre-curated knowledge-graph triples).** The gap is exactly where
the task's own framing suspected: nearly all VSA/HDC language work is hand-built-parse-into-VSA or
distributional-corpus-lexicon, not learned-parse-into-VSA; and the one lineage that DOES learn
role-filler binding end-to-end (TPR-nets) uses exact/uncompressed tensor products, not the flat
fixed-width hyperdimensional vectors this task is asking about, and has not been pushed to open natural
language at scale.

P_deflated (novel-synthesis "this exact combination is unbuilt and this is the right assembly" claim,
capped per lit-scan calibration discipline): **0.42** — see calibration section.

---

## The 6 closest systems (ranked by closeness to the target: learned + VSA-compressed + text-driven + reasoning-consumed)

### 1. Schlag & Schmidhuber (2018/2019 NeurIPS), "Learning to Reason with Third-Order Tensor Products" (TPR-RNN)
- **What it does / representation:** a recurrent architecture that builds a third-order tensor memory
  (entity x relation x entity-style bindings) updated every timestep; roles AND fillers are selected via
  learned attention/gating, not hand-specified.
- **Learned or hand-built:** fully LEARNED end-to-end via gradient descent.
- **Achieved:** trained on the bAbI 20-task synthetic QA suite (including multi-hop reasoning tasks);
  state-of-the-art at publication, mean error ~1.3% jointly across all 20 tasks (best run ~0.78%),
  beating prior memory-network baselines, with evidence of improved systematic generalization on
  structurally-different train/test splits.
- **Limits:** bAbI is small, templated, synthetic — not open natural-language text; the representation is
  an exact third-order TENSOR PRODUCT, not a compressed fixed-width hyperdimensional vector (memory scales
  with entities x relations x entities, the exact blowup Plate's HRR was invented to avoid); no verified
  scaling to open-domain multi-hop text reasoning.
- **Closeness to target:** closest published match for "LEARNED role-filler binding trained end-to-end for
  multi-hop reasoning" — but wrong representation family (tensor, not compressed-VSA) and wrong input
  domain (synthetic stories, not real grounded text).

### 2. Palangi, Smolensky, He, Deng (2017/2018), TPR for QA/NLI ("grammatically-interpretable" TPR-RNN)
- **What it does / representation:** each word's symbol and role are selected via soft attention, LEARNED
  end-to-end; the resulting role-filler bound representation is used for downstream QA/entailment.
- **Learned or hand-built:** fully LEARNED.
- **Achieved:** evaluated on SQuAD (QA) and MNLI/logical entailment — comparable to LSTM/GRU baselines of
  that era, with far fewer parameters and an added interpretability property (each word's assigned role is
  legible).
- **Limits:** SQuAD/MNLI-2017-era baselines (pre-transformer); roles are a small, fixed, mostly
  grammatical-category set, not open agent/patient/goal semantic roles; still tensor-product family, not
  compressed HRR/VSA.
- **Closeness to target:** arguably the SINGLE closest published system to "a learned reader producing
  legible role-filler structure consumed by a separate reasoning head" — the main gaps are representation
  family (tensor vs compressed vector) and role richness (grammatical slots vs full semantic roles).

### 3. McCoy, Linzen, Dunbar, Smolensky (2019 ICLR), Tensor Product Decomposition Networks (TPDN)
- **What it does / representation:** NOT a system for building structure — a post-hoc DIAGNOSTIC that fits
  a TPR-approximator to an already-trained RNN/LSTM's hidden states, testing whether the net implicitly
  encodes role-filler binding.
- **Learned or hand-built:** the diagnostic network is learned; what it's diagnosing (the RNN) was
  separately trained on synthetic tasks (digit sequences, autoencoding).
- **Achieved:** trained seq2seq RNNs ARE well-approximated by TPR structure on synthetic tasks; but for
  natural-sentence encoders, a simple BAG-OF-WORDS role scheme already captures most of the variance —
  richer tree/sequential role schemes add only marginal explanatory power.
- **Limits:** interpretive only, not a proposal for HOW to build a learned binder; the natural-language
  finding is a genuine CAUTION for this whole line of work — trained neural sentence encoders do not
  spontaneously commit to rich hierarchical role structure without being explicitly pushed to.
- **Relevance:** the strongest available negative-control data point that "just train a net on text and
  hope role-filler structure emerges" is not sufficient by itself; structure has to be an explicit
  training target/inductive bias, not an emergent byproduct.

### 4. Predication-based Semantic Indexing — PSI (Cohen, Widdows, Rindflesch, Schvaneveldt, ~2009-2014)
- **What it does / representation:** encodes subject-predicate-object triples into a compressed vector
  space using PERMUTATION (not tensor product) to bind predicate+direction to filler, bundled via addition
  — built on Random-Indexing/HRR-family math, i.e. the CORRECT (compressed, fixed-width) representation
  family for this task.
- **Learned or hand-built:** the VECTOR algebra/reasoning layer is a fixed compositional scheme (not
  learned), but more importantly the TRIPLE EXTRACTION step — the actual "reading" — is entirely HAND-BUILT:
  triples are produced by SemRep, a rule-based biomedical NLP pipeline (MetaMap entity linking + syntactic/
  semantic rules mapped onto the UMLS Semantic Network). PSI only ever consumes SemRep's pre-extracted
  output.
- **Achieved:** literature-based discovery (finding multi-hop chains like drug-inhibits-substance-causes-
  disease across MEDLINE) and predictive analogical retrieval (e.g. cancer-therapy analogy retrieval) —
  genuine multi-hop reasoning DEMONSTRATED, over real text-derived (if hand-extracted) relations, at real
  corpus scale (MEDLINE/SemMedDB).
- **Limits:** entirely dependent on SemRep's rule-based extraction quality and biomedical-domain coverage;
  the "reading" step is exactly the hand-built parse this task is asking whether anyone has replaced with
  a LEARNED one — PSI is the clearest existing counterexample-by-omission: it proves VSA reasoning over
  text-derived triples works well at scale, while leaving the extraction step completely unlearned.
- **Closeness to target:** closest system on the "compressed-VSA + real text corpus + multi-hop reasoning"
  axes; the single missing piece is exactly "learned parse," making it the most informative gap-marker in
  this whole scour.

### 5. HolE / holographic knowledge-graph embeddings (Nickel, Rosasco, Poggio, AAAI 2016) — proven equivalent to ComplEx (Hayashi & Shimbo, ACL 2017)
- **What it does / representation:** circular correlation (the same operator family as Plate's HRR
  unbinding) composes subject/object embeddings for relation scoring in knowledge-graph completion.
- **Learned or hand-built:** fully LEARNED via gradient descent on a link-prediction objective; proven
  mathematically equivalent (up to an initialization constraint) to Trouillon et al.'s ComplEx (Hayashi &
  Shimbo 2017), reconciled further by Trouillon & Nickel (2017) on loss-function differences.
- **Achieved:** ~93.8% MRR / 94.1% HITS@10 on WN18; ~50.2% MRR / 72.6% HITS@10 on FB15k — competitive with
  or beating contemporary tensor-factorization baselines.
- **Limits:** operates ONLY over a pre-existing, curated knowledge graph's triples — no paper was found
  extending HolE-style circular-correlation embedding to relations extracted directly from raw text
  instead of a curated KG. Confirms the compressed-HRR-family binding operator IS learnable and effective
  for compositional relational reasoning via plain gradient descent — but the "reading text into
  structure" step is entirely absent from this lineage too, the mirror image of PSI's gap (PSI has the
  hand-built reading but real text scale; HolE has the learned binding but no text at all).

### 6. Fernandez, Çelikyılmaz, Singh, Smolensky (2018), "Learning and Analyzing Vector Encoding of Symbolic Representations"
- **What it does / representation:** a seq2seq network LEARNS to encode symbol structures, benchmarked
  against hand-built TPR/HRR encodings, and answers structural queries over the learned encoding.
- **Learned or hand-built:** the encoder is LEARNED end-to-end.
- **Achieved:** shows a trained network can match/approach hand-built TPR/HRR encoding quality on
  structural-query tasks.
- **Limits:** operates over a FORMAL/synthetic symbol-structure language (constructed symbol trees), not
  natural sentences — the closest-in-spirit "learned encoder validated against real VSA/HRR baselines"
  result, but never applied to natural language at all.

**Also relevant but hand-built / non-learned / non-text (established via prior sibling scours, cited not
re-derived here):** Eliasmith's SPA/Nengo/Spaun — HRR binding + cleanup memory + gated integrators for
cognitive tasks including some QA, but sentence-to-structure mapping is hand-specified in Nengo scripts,
not learned from raw text at scale; Kanerva's "dollar of Mexico" and Emruli & Sandin's analogical mapping
with sparse distributed memory — hand-constructed or learned-mapping-BETWEEN-already-structured-vectors,
neither addresses extracting structure from raw text; BEAGLE/Random Indexing — distributional, corpus-
level, order-sensitive but NOT role-filler-structured (Recchia et al.'s "bird eats worms" vs "bird eats
wings" indistinguishability finding, already logged in the 07-17 sibling note, is the sharpest evidence
these are not proposition-structured representations at all).

---

## What we should LEARN-FROM / BUILD-ON / CREDIT (concrete)

- **Binding scheme to adopt:** Plate's circular convolution / Kanerva's compressed HRR family (already the
  substrate's own choice) is the RIGHT representation family for the compressed, fixed-width goal — this
  scour reinforces (does not overturn) that choice, since the tensor-product lineage's own scaling
  problem (exact blowup) is precisely what compressed HRR/VSA avoids.
- **Learned role/filler-selection mechanism to adopt/adapt:** Schlag & Schmidhuber's and Palangi et al.'s
  attention-based, end-to-end-trained role AND filler selection is the credit-worthy mechanism to port —
  NOT their tensor-product representation, but their TRAINING SIGNAL/ARCHITECTURE PATTERN (an attention
  head that learns which vocabulary entries fill which roles, trained against a downstream task loss) is
  the closest existing recipe for "how do you train a binder" that this task is asking about. This is a
  representation-family SWAP (tensor product -> circular convolution), not a wholesale invention.
- **Reasoning readout / multi-hop consumption pattern to credit:** PSI's demonstrated multi-hop chain
  discovery over compressed-VSA-encoded, text-derived triples (drug-inhibits-substance-causes-disease) is
  the closest existing proof that a compositional reasoner CAN consume VSA-encoded relational structure at
  real corpus scale — worth studying PSI's specific query/chaining algorithm directly as a design
  reference for the substrate's own multi-hop reasoner, independent of the extraction-step gap.
- **Negative/cautionary lesson to credit:** McCoy et al.'s TPDN finding (trained sentence encoders default
  to bag-of-words-like role structure, not hierarchical, unless pushed) means a learned VSA parser should
  NOT be expected to spontaneously discover role-filler structure from a generic language-modeling
  objective alone — structure has to be an explicit part of the training signal/architecture (consistent
  with, and independently reinforcing, this arc's own `research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md`
  finding that a construction-scoring mechanism, not passive exposure, is the real missing piece).
- **What NOT to copy:** SemRep-style hand-built rule pipelines (PSI's extraction step) and Nengo-script
  hand-specified sentence encodings (SPA) are the ANTI-pattern this whole task is trying to move past —
  useful as a working baseline/comparison point, not as the target architecture.

---

## HONEST VERDICT

**Is "a learned VSA reader that forms grounded role-filler reasoning-maps for a compositional reasoner"
ALREADY DONE?** No. Not by any named system found across four independent searches (this scour's 3 lanes
plus the 07-17 sibling scour).

**PARTIALLY DONE — what's missing, stated precisely:** every necessary sub-piece exists, published,
independently validated, in one of two disjoint lineages:
1. Learned role/filler binding, end-to-end trainable (Schlag/Palangi/Fernandez et al.) — but wrong
   representation family (exact tensor product, not compressed HRR/VSA) and wrong input domain (synthetic
   bAbI stories or formal symbol trees, not natural grounded sentences).
2. Compressed-VSA/HRR binding that reasons over relational structure at real scale (PSI, HolE/ComplEx,
   resonator networks) — but the text-to-structure step is either entirely hand-built (PSI's SemRep,
   SPA's Nengo scripts) or entirely absent because the system never touches raw text (HolE/ComplEx operate
   only on pre-curated KG triples).
No system combines: compressed fixed-width VSA/HDC representation + a LEARNED (not hand-ruled) text-to-
structure mapping + natural grounded sentences + downstream compositional multi-hop reasoning.

**GENUINELY NOVEL COMBINATION — what pieces exist to assemble:** the assembly implied by this task (a
learned binder, of the Schlag/Palangi attention-selects-role-and-filler pattern, retargeted from tensor
product onto circular convolution/HRR, trained against a downstream reasoning-task loss on the
substrate's own grounded lexicon and corpus, feeding a compositional VSA reasoner in the style
demonstrated by PSI's multi-hop chaining and the resonator-network decode machinery already catalogued in
the 07-17 sibling note) has not been published as one system. This is a real, confirmed, four-way-searched
gap, not a failure to search hard enough for an existing name to attach — but the honest caveat (per
calibration discipline) is that absence-of-evidence claims are structurally weaker than positive
literature findings, and the individual assembled pieces themselves are all borrowed, not new (see
LEARN-FROM section above); the novelty is specifically in the CROSS-LINEAGE COMBINATION, not in any single
new algebraic or learning-theoretic idea.

**Is the LEARNED parse into VSA the gap?** Yes, confirmed strongly and consistently: every VSA/HDC language
system found (across this scour and its 07-17/07-18 siblings) is either hand-built at the parse step
(SemRep/PSI, Nengo/SPA), purely distributional/non-relational (BEAGLE, Random Indexing, Rahimi-style text
classification), or learned-but-not-VSA-and-not-natural-text (TPR-nets on bAbI/SQuAD/formal symbols,
HolE/ComplEx on curated KGs). This matches the task's own hypothesis precisely.

---

## Cheap decisive test

**Representation-family transfer test (cheapest, run first):** reimplement Schlag & Schmidhuber's TPR-RNN
role/filler-attention update rule, but swap its third-order tensor-product binding for circular-convolution
(HRR) binding at fixed vector dimensionality, and re-run on the same bAbI 20-task suite they reported
against. This is a small, well-specified architecture swap (not a new theory), directly tests whether the
LEARNED-binding lineage and the COMPRESSED-VSA lineage are freely interchangeable, and has a clean
published baseline number to compare against (~1.3% mean joint error). No new grounding/corpus work
required — this isolates the representation-family question before touching the harder natural-language
question.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, deflated)

**Prediction 1 — circular-convolution (HRR) binding can replace TPR-RNN's third-order tensor-product
binding, at fixed vector dimensionality, without material loss on bAbI-style multi-hop QA, while cutting
memory scaling from O(entities x relations x entities) to O(N).**
P = **0.40** (deflated; adjacent-method transfer between two literatures that this scour found have never
been directly combined in either direction — no precedent in either the TPR or VSA literature for this
specific swap).
HARD-PASS: HRR-binding variant reaches within 5 points of TPR-RNN's published bAbI joint accuracy (mean
error within ~5 points of the ~1.3% published figure) at equal-or-smaller dimensionality budget.
HARD-FAIL: HRR-binding variant degrades by >15 points or fails to train stably — would indicate the
tensor product's algebraic exactness (no lossy unbind) is load-bearing for TPR-RNN's specific iterative
multi-hop attention mechanism, and compressed/lossy VSA binding is not a drop-in substitute for that
architecture.

**Prediction 2 — a learned, attention-based role-assigner (Schlag/Palangi-style, retargeted to circular-
convolution binding) trained only on the substrate's own existing grounded corpus outperforms the
substrate's current hand-rule multi-cue role-assigner on the same ambiguous-construction fixture already
used in this arc's comprehension drills.**
P = **0.32** (more deflated; this combines two cross-arc extrapolations — the representation-family swap
from Prediction 1 AND a transfer from bAbI/SQuAD-scale supervision down to this substrate's much smaller
from-near-nothing grounded corpus, which the sibling comprehension-gap note already flagged as a real,
literature-documented ceiling risk).
HARD-PASS: learned attention-based role-assigner beats the current hand-rule assigner by >=10 points on
the shared ambiguous-construction fixture (reduced-RC-on-subject, PP-attachment, compound-noun-head cases
from `research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md` and
`research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md`), using only the substrate's own
corpus (no external LLM/gold-tree supervision).
HARD-FAIL: learned assigner underperforms the hand-rule baseline, or requires order-of-magnitude more
labeled examples than the corpus supplies to match it — would confirm the "learned-parser regime needs
more supervision than a from-near-nothing system can provide" ceiling already identified from the
acquisition/ML-history angle in the sibling note, this time from the TPR-transfer angle specifically.

---

## Cross-thread synthesis

- **Directly complements, does not duplicate, `research_vsa_hdc_state_of_mind_prior_art_scour_2026-07-17.md`.**
  That note mapped the discourse/working-memory side of the VSA/cognitive-architecture literature (gated
  integrators, item-position sequence accumulation, resonator decode, stack-of-focus-spaces) and confirmed
  a running MULTI-SENTENCE discourse state in VSA is unbuilt. This note narrows in on the SINGLE-SENTENCE
  parse-to-structure step specifically and confirms a parallel, complementary gap: the LEARNED version of
  that single-sentence parse is also unbuilt, for exactly the same underlying reason (every existing VSA
  language system either hand-builds the structure-forming step or never learns it from raw text). The two
  gaps compound: even a hand-built single-sentence parser feeding a hand-built discourse tracker would still
  leave the "learned, not hand-fed" ambition (this arc's stated 07-14/07-18 foundational goal) unaddressed
  at BOTH levels.
- **Directly extends `research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md`'s Rank-2
  finding** ("a learned, grounding/comprehension-scored construction-induction mechanism" is the one
  genuinely missing capability) by supplying a CONCRETE candidate mechanism family (Schlag/Palangi
  attention-based learned role-selection, retargeted onto circular-convolution binding) rather than leaving
  the "how" abstract — Prediction 2 above is a direct, testable instantiation of that note's Rank-2 item,
  using this note's literature-sourced architecture pattern.
- **Directly extends `research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md`**
  by giving its hand-built multi-cue role-assigner a named, literature-precedented LEARNED alternative to
  be benchmarked against (Prediction 2), rather than only a hand-rule-refinement path forward.
- **PSI's demonstrated multi-hop literature-based-discovery chaining** is a useful external validation
  target for the substrate's own compositional reasoner design, independent of the parser-learning question
  — worth a follow-up read of PSI's specific chaining/query algorithm as a design reference, flagged as a
  candidate next-drill rather than pursued here (scope discipline: this note stayed on the parse-learning
  question).

---

## Substrate-product implications

1. **The honest, defensible novelty claim is narrow and specific, per the no-papers/product-only
   discipline:** "assembles a learned attention-based role-selection mechanism (borrowed from the TPR-net
   literature) with compressed circular-convolution/HRR binding (borrowed from the VSA literature) and
   applies it to natural grounded text (which neither borrowed lineage has done) to feed a compositional
   multi-hop reasoner" — NOT "invented a new binding algebra" or "invented VSA reasoning," both of which
   are extensively pre-existing per this scour and its siblings.
2. **Two concrete, literature-precedented experiment candidates are now open, sequenced by cost:**
   (a) Prediction 1 — the cheap representation-family swap test (TPR-RNN's tensor binding -> circular
   convolution), a pure architecture-transfer check with a published baseline number, no new corpus/
   grounding work needed; (b) Prediction 2 — the harder, more substrate-specific test (learned role-
   assigner vs current hand-rule assigner on the arc's own ambiguous-construction fixture), which depends
   on (a) succeeding first and reuses existing arc fixtures rather than requiring new data collection.
3. **A real, literature-grounded expectation-setting point:** even if this assembly is built and works,
   the supervision-scarcity ceiling already identified in the sibling comprehension-gap note (unsupervised/
   grounded structure-induction sits meaningfully below supervised-treebank accuracy, especially on long/
   complex prose) applies here too — a learned VSA role-assigner trained on a from-near-nothing corpus
   should be expected to show the SAME register-dependent pattern (near-ceiling on simple/short text, a
   real gap on complex prose), not treated as a bug if it does.
4. **PSI is a genuinely useful, underused design reference** for the substrate's downstream multi-hop
   reasoner specifically (not the parsing question) — flagged as a candidate follow-up drill, not pursued
   in this note to keep scope bounded to the parse-learning question this scour was dispatched to answer.

---

## Calibration reasoning (P_deflated = 0.42 headline; per-prediction P 0.32-0.40)

Raw confidence in the DIRECT literature findings (what TPR-RNN/Palangi-TPR/TPDN/PSI/HolE-ComplEx/Emruli-
Sandin/Rahimi-text-classification/Kleyko-survey/Fernandez-et-al. each actually report) is high (~0.75-0.85),
cross-checked across 3 independent lit-scan lanes plus alignment with the two sibling scours' independent
findings, with explicit unverifiable items flagged rather than smoothed over (one lane could not verify
detailed TPR-on-SCAN/COGS numeric results within its search budget; PDF full-text extraction failed for
Kleyko's survey papers, so its "NLP is treated as a classification sub-area" characterization rests on
search-snippet-level evidence, not confirmed full-text reading — flagged inline in that lane's report).
Standard lit-scan deflation (0.15-0.25) brings direct-citation confidence to ~0.55-0.65. The GAP-CONFIRMATION
claim itself (that the specific combination is unbuilt) is inherently an absence-of-evidence claim, weaker
than a positive literature finding even before the mandatory novel-synthesis cap — discounted further to
0.42 because: (i) four independent searches converging on the same gap is strong but not proof a
differently-named or differently-venued system doesn't exist; (ii) neither of the two falsifiable
predictions has been run — both are pre-registration-stage claims; (iii) the "right assembly" judgment
(which pieces to combine, and how) is this note's own synthesis, not a citation.

---

## Citations (verified count)

**3 parallel Sonnet lit-scan lanes this cycle, ~24 distinct external primary sources located and
cross-checked this session**, plus ~15 additional sources credited from the two sibling scours (cited,
not re-verified here): Smolensky 1990 (*Artificial Intelligence* 46:159-216, TPR foundational); McCoy,
Linzen, Dunbar & Smolensky 2019 (ICLR, TPDN); Schlag & Schmidhuber 2018/2019 (NeurIPS, TPR-RNN); Huang,
Zhu, Smolensky, He, Deng & Wu 2018 (NAACL, Tensor Product Generation Networks); Palangi, Smolensky, He &
Deng 2017/2018 (grammatically-interpretable TPR-RNN for QA/NLI); "Differentiable Tree Operations Promote
Compositional Generalization" 2023 and "Attention-based Iterative Decomposition for TPR" (AID) 2024
(flagged as search-level-only, not fully verified); Coecke, Sadrzadeh & Clark ~2010 (DisCoCat, brief
comparison only); Cohen & Schvaneveldt / Widdows & Cohen 2009-2014 (PSI, incl. *Logic Journal IGPL* 2014);
Nickel, Rosasco & Poggio 2016 (AAAI, arXiv:1510.04935, HolE); Hayashi & Shimbo 2017 (ACL, arXiv:1702.05563,
HolE-ComplEx equivalence proof); Trouillon & Nickel 2017 (arXiv:1707.01475); Trouillon et al. 2016
(ComplEx); Kanerva 2010 (AAAI Fall Symposium, "dollar of Mexico"); Emruli & Sandin 2014 (*Cognitive
Computation*, analogical mapping with SDM); Emruli, Gayler & Sandin 2013; Najafabadi, Rahimi, Kanerva,
Rabaey 2016 (HDC for text classification, foundational cite); Kleyko, Rachkovskij, Osipov & Rahimi
2021/2023 (arXiv:2111.06077 and arXiv:2112.15424, ACM CSUR, VSA/HDC survey Parts I & II); Cotteret,
Greatorex, Ziegler & Chicca 2024 (*Neural Computation*, arXiv:2212.01196, VSA finite-state machines);
"Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning" (arXiv:2512.14709, under
review, flagged as reinterpretation not new system); IBM Neuro-Vector-Symbolic Architecture (NVSA, ~2023,
visual/Raven's-matrices, not text); Fernandez, Çelikyılmaz, Singh & Smolensky 2018 (arXiv:1803.03834);
Chen, Lu, Beukers, Baldassano & Norman 2021 (*PeerJ*, RNN/DNC role-filler binding, non-VSA control); Frady,
Kleyko, Kymn, Olshausen & Sommer 2022 (arXiv:2109.03429, NICE, VFA capacity theory, no language content).
Two lanes explicitly flagged unverifiable items (PDF extraction failures for the Kleyko surveys; unable to
confirm detailed TPR-on-SCAN/COGS numbers) rather than guessing — excluded from load-bearing predictions.

**Internal cross-thread**: `research_vsa_hdc_state_of_mind_prior_art_scour_2026-07-17.md`;
`research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md`;
`research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md`.

---

## Status

Written per research-agent contract. USER-locked discipline applied: **no `exp_dev_handoff_*.md` or
`strategy_request_to_*.md` routing files written** (ferry mechanism deprecated per current session
instructions) — every actionable pointer is inline above (ranked closest-systems list, LEARN-FROM/BUILD-ON/
CREDIT section, falsifiable predictions with pre-registered thresholds, cheap-decisive-test call-out). This
note is one of 4 sibling scours (semantic-parsing, comprehension-models, neurosymbolic-reading, and this
one) feeding a director synthesis — no independent exp_dev pickup is filed here; the director's cross-scour
synthesis is the intended next consumer. No cap_map or strategy files modified.
