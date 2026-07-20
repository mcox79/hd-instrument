# Prior-art scour: neurosymbolic / glass-box "read text -> structured KB -> reason" systems

**Filed:** 2026-07-18 by research (Opus synthesis over 4 parallel Sonnet lit-scan lanes).
**Trigger:** USER-directed prior-art due diligence — does a system that does substantially what
we're building (learned read -> vector-binding structured representation -> compositional
multi-hop reasoning, fully glass-box, no black-box LLM at inference) already exist? One of 4
sibling scours (this one; VSA-language; semantic-parsing; comprehension-models) feeding a director
cross-synthesis.
**Query-privacy:** all 4 lanes searched literal public system/paper names (NELL, DeepDive, Snorkel,
DrKIT, NS-CL, NVSA, Soar, Spaun, etc.) — these ARE the generic public terms appropriate for this
scour; no substrate-novel mechanism names or configs went off-platform.

## HEADLINE

**No published system combines all three of {learned reading, VSA/vector-binding structured
representation, glass-box multi-hop reasoning} over text.** The pieces exist in at least four
separate, non-overlapping lineages, each missing a different piece: (1) KB-construction systems
(NELL+PRA closest) have learned-if-hand-architected extraction and a genuine bolted-on multi-hop
reasoner, but the reasoner runs post-hoc over a symbolic triple store, not a vector-binding
substrate, and semantic drift shows the extraction step isn't self-correcting at the mechanism
level; (2) neurosymbolic reading/QA (DrKIT closest) has a genuinely learned, text-grounded,
multi-hop pipeline, but per-hop evidence is dense/opaque retrieval, not glass-box at the fact
level; (3) cognitive architectures (Soar/NL-Soar closest on glass-box+multi-hop; Spaun/SPA closest
on learned+grounded+glass-box+multi-hop) never scale past hand-picked sentences or digit/symbol
tasks — zero open-domain real-text reading in the SPA/Nengo literature specifically; (4) the VSA
bridging search found the decisive negative directly: NVSA (Hersche et al., IBM, *Nat. Mach.
Intell.* 2023) is the one lineage with a genuinely FIXED-algebra VSA binding + learned neural
front-end + glass-box symbolic-probabilistic reasoning — but it is exclusively visual/abstract
(RAVEN's matrices); confirmed zero extension to text/language in the literature. TPR-RNN and
TP-N2F (Schlag/Schmidhuber; Chen/Smolensky/Gao et al.) DO read text and reason multi-hop with
tensor-product binding, but the binding itself is trainable/backprop-learned end-to-end rather
than a fixed algebra — this measurably weakens the glass-box claim (the bind *shape* is
interpretable, the bind *content* is not).

**The Neuro-Symbolic Concept Learner (Mao/Tenenbaum, ICLR 2019) is the closest thing to a
gold-standard architectural TEMPLATE for the full stack** (learned perception -> learned
semantic parser -> deterministic, fully-inspectable symbolic program executor, jointly trained
with no direct parse/perception supervision) — but it is vision (CLEVR), not text, and an
exhaustive search found no direct "NS-CL-for-text" successor. DrKIT independently arrives at a
similar spirit for text but keeps its per-hop evidence dense rather than NS-CL's crisp symbolic
execution.

P_deflated (existence-claim confidence, the "does X already exist" empirical question): **0.72**
— high confidence in what each cited system does/doesn't do (cross-checked across 4 independent
lit-scan lanes, each converging on the same "no unification" conclusion via different search
angles), deflated from raw ~0.85 per lit-scan calibration discipline for residual risk that a
paper exists under different terminology not tried (esp. non-English-language venues, or very
recent 2025-2026 preprints not yet indexed).
P_deflated (novel-synthesis claim — "the specific combination we propose to build is the right
one and is genuinely ours to build"): **capped at 0.50** per mandatory novel-synthesis ceiling,
discounted to **0.42** for the reasons in the calibration section below.

## Field survey (4-way lit-scan, synthesized)

### A. Machine-reading-to-KB-construction systems

| System | Learned read? | Glass-box? | Multi-hop reasoning? | Grounded? |
|---|---|---|---|---|
| **NELL** (Mitchell et al., CMU, 2010-) | Yes (per-view statistical classifiers), ontology/coupling hand-specified | Semi — per-extractor decisions inspectable, 500+ coupled functions over years hard to fully audit; semantic drift (e.g. "Xbox" learned as a country) requires human correction | **Yes** — Path Ranking Algorithm (Lao & Cohen, EMNLP 2011) does weighted-random-walk multi-hop inference over typed-edge paths, roughly doubling precision@100 | Text-mention-grounded only |
| **DeepDive** (Ré et al., Stanford) | Hybrid (hand-declared features + learned factor-graph weights) | Yes — calibrated probabilities, inspectable factor graphs; beat human curators (PaleoDeepDive) | No — reasoning is internal consistency inference for extraction quality, not KB-level deduction | Document-internal |
| **Snorkel** (Ratner/Bach/Ré, VLDB 2017) | Hand-coded labeling functions, learned denoising/aggregation weights | Yes (LF-level provenance) | **None** — terminates at label generation, upstream of any KB | No |
| **Knowledge Vault** (Dong et al., Google KDD 2014) | Learned per-extractor classifiers, hand-fixed schema/fusion | No — opaque supervised fusion of dozens of extractor signals | No published downstream reasoner | Freebase-entity-linked (strongest grounding in this group) |
| **Universal Schema** (Riedel/Yao/McCallum, NAACL 2013) | Learned end-to-end embeddings, but reads pre-extracted mention pairs not raw text | No — dense latent factorization | Implicit only (embedding-space generalization, not explicit chaining) | Freebase-entity-pair-shared only |
| **OpenIE (+TupleInf)** (Fader/Mausam/Kolluru; Khot/Sabharwal/Clark ACL 2017) | Mix of hand-coded syntactic rules and learned sequence-labeling (OpenIE6) | Yes — literal extracted tuples | Yes, but narrow/hand-authored rule-set (TupleInf), noisy/non-canonical tuples don't scale to robust chaining | Text-internal, no entity linking by default |

**Verdict this lane:** NELL+PRA is closest overall — but the reasoning layer is a *separate
post-hoc algorithm*, not integrated into the reading loop, and none of the six unify learned-read
+ full inspectability + native multi-hop in one mechanism.

### B. Neurosymbolic reading / QA

| System | Learned front-end? | Glass-box? | Multi-hop? | Grounded? |
|---|---|---|---|---|
| **Neural Theorem Provers / GNTP / CTP** (Rocktäschel & Riedel 2017; Minervini et al.) | No — operates on pre-given KB triples | Yes — proof trees/induced rules literally readable | Yes, genuine compositional chaining | No |
| **DrKIT + TensorLog/NQL** (Dhingra et al. ICLR 2020; Cohen/Yang/Mazaitis) | **Yes** — "virtual KB" built live from a BERT-style mention encoder over raw text, no separate IE step | Partial — hop *structure* is a symbolic query program (readable), but per-hop evidence is dense MIPS retrieval over opaque embeddings | Yes (2-3 hops demonstrated, closed ~70% of text-vs-KB gap on MetaQA) | **Yes** — grounded directly in corpus text spans |
| **DeepProbLog / DeepStochLog / A-NeSI / NeurASP** | Yes but only tiny perceptual predicates (MNIST digits); no text/parse front-end found | Split — symbolic program glass-box, neural predicates opaque | Yes in the logic-program sense, only over hand-written toy programs | Minimal (pixel-level only) |
| **Logical Neural Networks** (Riegel et al., IBM 2020) | No — takes pre-formalized facts/rules | Yes, maximally (1:1 neuron-to-subformula) | Yes, arbitrary-depth | No |
| **NS-CL** (Mao/Tenenbaum, ICLR 2019) | **Yes** — perception, parser, and program executor jointly learned, zero direct supervision on parses/perception | **Yes, fully** — per-step program trace inspectable | Yes, full compositional generalization (CLEVR) | Yes (visual) |
| **Neural Module Networks for multi-hop QA** (Jiang & Bansal 2019) | Modules hand-designed, not learned compositional primitives | Partial (module trace readable, module identities fixed) | Yes, shallower than NTP | Text-internal |

**Verdict this lane:** DrKIT is closest on learned-front-end + multi-hop + text-grounding but not
glass-box at the evidence level. NTP/LNN are closest on glass-box+multi-hop but require a
pre-built KB (no reading step). NS-CL is the architectural gold standard for the *whole pattern*
but has never been ported to text — confirmed via direct search, not an assumption.

### C. Cognitive architectures

| Architecture | Learned reading? | Glass-box? | Multi-hop? | Grounded? | Open-domain text? |
|---|---|---|---|---|---|
| **Soar / NL-Soar** (Lindes & Laird, ICCM 2017; dissertation 2022) | No — ECG grammar hand-authored; only chunking (caching) is automatic | Yes, fully symbolic | Within-sentence yes; cross-document, no | Rosie line is situated/grounded; sentence-comprehension line is text-internal | **No** — hand-picked sentences / micro-worlds only |
| **ACT-R** (Lewis & Vasishth 2005; SEAM 2023) | No — grammar/retrieval-cue structure hand-coded | Yes, chunks/productions inspectable | No — targets within-sentence retrieval interference, not chained inference | No | No — small hand-constructed stimuli sets |
| **Sigma** (Rosenbloom) | Partial (learned phone/word recognition; higher structure designed) | Yes by construction, less mature tooling | Not demonstrated for language | Speech-signal only | No — largely dormant post-2016-2021 |
| **Leabra / Sentence Gestalt** (O'Reilly; Rabovsky et al. 2018) | **Yes** — the one genuinely learned reading step in this group | **No** — distributed activations, not symbolic/inspectable (opposite tradeoff from Soar/ACT-R) | No — single-sentence thematic-role modeling only | Training-corpus-grounded only | No — small synthetic sentence sets |
| **Spaun / SPA** (Eliasmith; Nengo) | Mixed — perceptual front-end learned, symbolic binding architecturally specified | Yes, semantic pointers algebraically inspectable | Yes, within induction/RPM-style tasks | Yes, visually (pixel input) | **No** — confirmed zero open-text-corpus ingestion anywhere in SPA/Nengo literature |

**Verdict this lane:** no cognitive architecture has ever combined learned reading + glass-box
structure + multi-hop reasoning + open-domain corpus scale — each has at most 2-3 of these 4
properties, never all 4. Soar/NL-Soar and Spaun are the two closest, missing different halves
(Soar: learned reading; Spaun: any real text at all).

### D. The decisive VSA-binding bridging search

| System | Fixed VSA algebra? | Learned front-end? | Text-grounded? | Multi-hop? | Glass-box? |
|---|---|---|---|---|---|
| **TPR-RNN** (Schlag & Schmidhuber, NeurIPS 2018) | **No** — role/filler vectors are trainable embeddings, bind+unbind learned via backprop | Yes | Yes (bAbI, all 20 tasks) | Yes | Weak — only the *shape* (tensor outer product) is interpretable, not the learned content |
| **TP-N2F** (Chen/Gao/Smolensky/Yih/He, Microsoft Research) | No, same backprop-learned binding | Yes (NL math word problems -> program) | Yes | Single-shot generation, not iterative multi-hop retrieval | Same weak glass-box caveat |
| **NVSA** (Hersche et al., IBM, *Nat. Mach. Intell.* 2023) | **Yes** — genuinely fixed holographic-style bind/unbind, not learned per-instance | Yes (learned perceptual front-end) | **No — confirmed zero extension to text; RAVEN/I-RAVEN only** | Yes | Yes |
| **HRR-for-parsing** (CYK-in-HRR, arXiv:1705.08843) | Yes (fixed) | No | Parse-chart encoding trick only, not a QA/reasoning pipeline | No | Yes but narrow |
| **VSA on SCAN/COGS** | N/A | N/A | **No VSA entrant found** — field's compositional-generalization benchmarks are owned by symbolic program-synthesis / stack-machine methods | — | — |
| **Kleyko/Frady/Sommer VSA/HDC survey** (arXiv:2111.06077/2112.15424) | — | — | Catalogs applications through text CLASSIFICATION; **no reading-comprehension or multi-hop-QA entry** — the omission itself is field-level evidence of the gap | — | — |

**This is the load-bearing negative result of the whole scour**: the ONE lineage that has a
genuinely fixed-algebra VSA binding + learned neural front-end + glass-box reasoning (NVSA) has
never touched text/language at all — it is exclusively visual/abstract-matrix reasoning. The
lineage that DOES read text with tensor-product-style binding (TPR-RNN, TP-N2F) sacrifices the
fixed-algebra property (binding is backprop-learned end-to-end), which is precisely the property
that makes a VSA glass-box in the strong sense (an inspectable, hand-verifiable algebraic
operation, not a black-box-trained one).

## THE DECISIVE HONEST VERDICT

**Does a system that does substantially what we're building already exist? No — bluntly, no.**
Nobody has published a raw-text-in, fixed-algebraic-VSA-bound, multi-hop-reasoning-out,
glass-box-throughout system. This conclusion is convergent across all 4 independent lit-scan
lanes searching from completely different angles (KB-construction, neurosymbolic-QA, cognitive
architecture, VSA-specific), which raises confidence this is a genuine unsearched-gap finding
rather than a missed citation.

**What's closest, piece by piece, and what we'd adopt vs. where we differ:**
- **NELL + PRA**: adopt the "coupled multi-view extraction reduces individual-extractor error"
  design principle and the path-ranking-over-typed-edges reasoning pattern (mathematically the
  same move as the AnyBURL/RuleN rule-mining approach this program already scoured and ranked #1
  on 2026-07-13 — this scour independently arrives at the same family from the KB-construction
  angle, which is convergent, not redundant). Differ: we want the reasoning substrate to be
  vector-binding-native, not a symbolic triple-store walk; we want reading to be an integrated
  loop, not a decade-long human-supervised ensemble.
- **DrKIT/TensorLog**: adopt the "read text into a live, queryable structure with no separate KG
  construction step" architectural principle — this is the single most directly transferable
  design lesson in the whole scour, since it is the one system that is genuinely learned AND
  text-grounded AND multi-hop. Differ: we want the per-hop evidence itself to be glass-box (a
  fixed VSA bind/unbind readout), not a dense retrieval score — DrKIT explicitly trades this away.
- **NS-CL**: adopt the overall THREE-STAGE TEMPLATE (learned perception/reading -> learned
  parser-to-program -> deterministic glass-box executor, jointly trained without direct
  parse/perception supervision) as the architectural pattern to port to text. This is the
  single cleanest, most citable "what would the ideal version look like" reference in the entire
  scour. Differ: substrate (VSA vector-binding vs. CLEVR's symbolic scene graph + program DSL) and
  domain (text vs. vision) — porting this pattern to text with a VSA executor instead of a
  hand-written program interpreter is, per this scour, unattempted in the literature.
- **NVSA**: adopt the fixed-algebra-binding + learned-front-end architectural split wholesale —
  this is the nearest existing proof that "learned perception -> fixed VSA bind/unbind -> glass-box
  probabilistic-symbolic reasoning" works end-to-end and beats symbolic-reasoning competitors by
  ~100x compute. Differ/gap: this is the one piece of prior art we would be DIRECTLY EXTENDING
  (not just learning from) — nobody has taken NVSA's exact pattern and pointed it at text instead
  of RAVEN's matrices. This is arguably the single most concrete, well-precedented "what to build
  next" pointer to come out of this scour.
- **Soar/NL-Soar**: credit as the deepest existing account of psycholinguistically-valid,
  fully-symbolic incremental sentence comprehension; use as a design check for our own
  incremental-parse/state-update loop, per the standing prior-art discipline (learn-from,
  build-on, credit — not reinvent from zero). Differ: their mapping is hand-authored; ours must be
  learned.

**The genuine gap/novelty that is ours to build, stated narrowly and honestly (per the no-papers,
product-only framing)**: a system that (a) LEARNS its reading/parsing step rather than hand-coding
it (unlike Soar, ACT-R, NTP, LNN, DeepProbLog's symbolic half), (b) represents what it reads in a
FIXED-ALGEBRA vector-binding substrate rather than backprop-learned tensor bindings (unlike
TPR-RNN/TP-N2F) or opaque dense embeddings (unlike DrKIT's per-hop evidence, Universal Schema,
Knowledge Vault), and (c) reasons multi-hop over that representation with the reasoning step
ITSELF inspectable as an algebraic operation, not a post-hoc symbolic-triple-store walk (unlike
NELL+PRA) or a hand-written program executor over a non-vector scene graph (unlike NS-CL). No
cited system does (a)+(b)+(c) together for text. NVSA does (a)+(b)+(c) for VISION only — it is the
single nearest analog and the most direct "port this exact pattern" candidate.

## Cheap decisive test

This scour's own decisive test is a targeted RE-SEARCH, not an experiment cell: run 3 additional
narrow queries not yet tried by any of the 4 lanes — "NVSA text" / "NVSA language" / "vector
symbolic architecture reading comprehension 2025 2026" and "holographic reduced representation
question answering multi-hop" restricted to 2024-2026 preprint venues (arXiv cs.CL, cs.AI) — to
close the residual risk that a very recent paper (post-indexing-lag) closes this exact gap. This
is a <1hr task, zero compute, pure literature hygiene.

**Pre-registered HARD-PASS (for the re-search, not a build claim):** a paper is found that
explicitly combines fixed-algebra VSA/HDC binding + a learned text-reading front-end + multi-hop
reasoning over the bound representation, published or preprinted 2023-2026. If found: re-open this
verdict, do NOT treat the gap as closed-and-safe without reading it directly.

**Pre-registered HARD-FAIL (confirms the gap holds):** all 3 additional queries return only
restatements of the systems already catalogued above (NVSA-vision-only, TPR-RNN/TP-N2F
non-fixed-binding, DrKIT non-VSA) or zero new hits. This is the expected outcome given 4
independently-converging lanes already found the same gap from different angles.

## Falsifiable predictions (calibration-penalized; novel-synthesis cap 0.50 applied)

- P(the "no unified system exists" claim survives the cheap re-search test above) = **0.85**
  (high — 4 independent lanes converged; this is an existence claim, not a novel-synthesis claim,
  so it is not subject to the 0.50 cap, only the standard 0.15-0.25 lit-scan deflation from a raw
  ~0.95-that-4-lanes-agree).
- P(NVSA's exact architectural pattern — fixed VSA bind/unbind + learned neural front-end +
  glass-box probabilistic-symbolic reasoning — transfers productively to a TEXT reading task
  without requiring a fundamentally different binding algebra) = **0.40** (deflated from a naive
  ~0.55; NVSA's domain (RAVEN's matrices) has small, closed, combinatorially-structured object
  sets — text's open-vocabulary, noisy, long-tail entity/relation space is a substantially harder
  binding target, and no field precedent tests this transfer directly).
- P(the NS-CL three-stage template — jointly-learned perception/parse + program -> deterministic
  glass-box executor — is the right architectural skeleton to port, specifically) = **0.48**
  (capped near the novel-synthesis ceiling; this is this scour's own architectural recommendation,
  well-motivated by NS-CL's demonstrated joint-training success on a structurally analogous
  problem, but untested for text specifically).
- P(a hidden paper we missed already closes this exact gap, discovered on deeper drilling) =
  **0.12** (low but non-zero; guarded against explicitly by the cheap decisive test above).

## Cross-thread synthesis

- **Directly extends `research_drill_neurosymbolic_logical_inference_theories_2026-07-13.md`**:
  that drill scoped itself explicitly to the RULE/LOGIC reasoning-over-KB mechanism family and
  found no method delivers {inductive, glass-box, cheap-at-scale} simultaneously, ranking
  AnyBURL/RuleN-style rule-mining #1. This scour's lane A (NELL+PRA) independently arrives at the
  same rule/path-based reasoning family from the KB-CONSTRUCTION angle — convergent evidence, not
  a re-test — and this scour additionally establishes that NONE of the rule/logic methods from
  07-13 operate on a vector-binding substrate at all (they are all symbolic-triple-store methods),
  which sharpens rather than contradicts 07-13's own finding.
- **Directly complements `research_vsa_hdc_state_of_mind_prior_art_scour_2026-07-17.md`** (sibling
  scour, same week): that note found no VSA/HDC paper connects to discourse/situation-model
  theories (Centering Theory, Grosz-Sidner, Kintsch-CI) for TRACKING state across sentences. This
  scour finds the parallel gap one layer over: no VSA/HDC paper connects learned-reading to
  REASONING over what was read, either. Together the two scours establish that the VSA/HDC
  literature has essentially stopped at single-proposition/single-scene binding+decode — nobody
  has extended it either to (a) a running multi-sentence state or (b) a read-then-reason pipeline.
  Both gaps point the same direction: the reading-into-vector-structure step itself is the
  unclaimed territory, not the algebra underneath it.
- **NS-CL and NVSA together bracket the exact architectural target**: NS-CL supplies the
  three-stage learned-perception/parse -> program -> executor TEMPLATE; NVSA supplies the proof
  that a FIXED VSA algebra can sit inside that exact template in place of a hand-written program
  interpreter and still beat symbolic-reasoning competitors on compute. Neither has been applied to
  text. This is the single most concrete, citable "build target" this scour produces, and should be
  weighed directly against the other 3 sibling scours' recommendations in the director synthesis.

## Substrate-product implications

1. **Novelty claim is genuinely defensible and should be framed narrowly**: "learned-read +
   fixed-algebra VSA-binding + glass-box multi-hop reasoning over open text" is, per this scour,
   unclaimed in the published literature. The honest, citable framing is "we are porting NVSA's
   proven learned-front-end + fixed-VSA-algebra + glass-box-reasoning pattern from visual
   abstract-matrix reasoning to text, using NS-CL's three-stage architectural template as the
   organizing skeleton" — a credit-the-precedent claim, not an "invented from nothing" claim, per
   the standing prior-work discipline.
2. **This scour does not itself propose a new experiment cell** — it is a landscape/novelty check
   feeding the director's cross-synthesis across 4 sibling scours (this one, VSA-language,
   semantic-parsing, comprehension-models). The concrete architectural pointer above (NVSA-pattern
   ported to text via an NS-CL-style three-stage skeleton) is offered as an input to that synthesis,
   not as a pre-registered anchor — the director should weigh it against the other 3 scours before
   committing compute.
3. **Reinforces, does not replace, the existing 07-13 rule-mining cheap decisive test**: that
   test (AnyBURL-style Horn-rule mining -> forward-chaining, CPU-only, already pre-registered with
   HARD-PASS/FAIL thresholds) remains the cheapest immediately-runnable next step regardless of
   this scour's findings, since it tests a structurally different question (does the KG's content
   support inductive inference at all) than this scour's architectural-novelty question (has
   anyone built the full pipeline). Both should stay live in parallel, not be sequenced.

## Citations (verified count: 4 parallel lit-scan lanes, 46 distinct external sources)

**Lane A (KB-construction, 12):** Carlson et al., AAAI-10 (NELL architecture); Mitchell et al.,
AAAI-15/CACM 2018 (NELL retrospective); Lao, Mitchell & Cohen, EMNLP-11 (Path Ranking Algorithm);
Lao, CMU-LTI-12-010 thesis; DeepDive, *CACM* 2017; Shin et al./De Sa et al., VLDB 2016 (Incremental
KBC); Ratner, Bach, Ré et al., arXiv:1711.10160 (Snorkel); Bach et al. 2019 (Snorkel Drybell); Dong
et al., KDD 2014 (Knowledge Vault); Riedel, Yao, McCallum, Marlin, NAACL-13 (Universal Schema);
Khot, Sabharwal, Clark, ACL-17 (TupleInf); Kolluru et al., EMNLP-20 (OpenIE6).

**Lane B (neurosymbolic reading/QA, 13):** Rocktäschel & Riedel, NeurIPS 2017 (NTP); Minervini et
al., arXiv:1807.08204 (NaNTP) + arXiv:2007.06477 (CTP); Dhingra et al., ICLR 2020, arXiv:2002.10640
(DrKIT); Cohen, Yang, Mazaitis, arXiv:1605.06523 + arXiv:1707.05390 (TensorLog); Manhaeve et al.,
NeurIPS 2018, arXiv:1805.10872 (DeepProbLog) + arXiv:1907.08194 (KR-2021 follow-up); Winters/Marra
(DeepStochLog); van Krieken et al., arXiv:2212.12393 (A-NeSI); Yang, Ishay & Lee (NeurASP); Nguyen
et al., arXiv:2501.18202 (2025 scaling-neurosymbolic survey); Riegel et al., arXiv:2006.13155
(Logical Neural Networks); Mao, Gan, Kohli, Tenenbaum & Wu, ICLR 2019, arXiv:1904.12584 (NS-CL);
Jiang & Bansal, 2019 (NMN for multi-hop QA); arXiv:2501.01030 (2025 symbolic+parametric KB survey).

**Lane C (cognitive architectures, 12):** Lindes & Laird, ICCM 2017 + AAAI Symposium 2017 (NL-Soar
ECG); Lindes, 2022 dissertation ("Constructing Meaning, Piece by Piece"); Laird, arXiv:2205.03854
(Soar intro); Mohan & Laird (Rosie ITL, cited via Soar literature); Lewis & Vasishth, *Cognitive
Science* 2005; Engelmann et al., arXiv:2303.05221 (SEAM); Rosenbloom (Sigma architecture);
Joshi & Rosenbloom (Sigma phone/word recognition); O'Reilly et al. (Leabra); Rabovsky et al., 2018
(Sentence Gestalt); Eliasmith et al., *Science* 2012 (Spaun); Eliasmith 2013 (*How to Build a
Brain*); Voelker & Eliasmith, *PLOS ONE* 2016 (semantic pointer optimization).

**Lane D (VSA-binding bridging, 9):** Schlag & Schmidhuber, NeurIPS 2018, arXiv:1811.12143
(TPR-RNN); Chen, Gao, Smolensky, Yih, He et al., arXiv:1910.02339 (TP-N2F); Huang, Smolensky, Yih,
He, Gao, ACL 2018, arXiv:1709.09118 (TPGN); Hersche et al., *Nat. Mach. Intell.* 2023,
arXiv:2203.04571 (NVSA) + IBM Research ES-Week continual-learning follow-up; arXiv:1705.08843
(CYK-in-HRR); NeurIPS 2021 HRR-stability paper (proceedings.neurips.cc); Kleyko, Frady, Sommer et
al., arXiv:2111.06077 + arXiv:2112.15424 (VSA/HDC survey Parts I-II); arXiv:2512.14709 (attention-
as-binding reframing, interpretive lens on transformers, not a new system).

All 4 lanes' individual per-system claims (learned/glass-box/multi-hop/grounded assessment) are
cross-checked against each other where systems overlap across lanes (NS-CL appears in lanes B and
implicitly frames lane D's verdict; NELL's PRA reasoning independently converges with the 07-13
rule-mining finding) — no contradiction found between lanes.
