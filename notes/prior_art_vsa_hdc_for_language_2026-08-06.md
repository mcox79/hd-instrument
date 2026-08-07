# Prior-art scan (Area 3 of 3): VSA/HDC for language, compositional semantics, and relational reasoning

**Date:** 2026-08-06. **Filed by:** research (3 parallel Sonnet lit-scan lanes + Sonnet synthesis).
**Trigger:** deep prior-art due-diligence scan of our own substrate family (glass-box FHRR: bind/bundle/cleanup,
goal/outcome/causal registers, goal-ownership tracking) — know-the-landscape only, no direction change.

**Method note (dedup discipline):** two deep sibling scours already exist in this codebase and were read
FIRST, in full, before dispatching anything new: `notes/research_vsa_hdc_state_of_mind_prior_art_scour_2026-07-17.md`
(4 lanes: cognitive architectures / SPA-Spaun / Nengo, BEAGLE / Random Indexing, structured state + resonator
networks + capacity math, and an explicit discourse/situation-model gap-check) and
`notes/research_vsa_learned_reader_prior_art_scour_2026-07-18.md` (3 lanes: the learned-TPR lineage vs. the
compressed-VSA lineage, PSI, HolE/ComplEx, VSA analogy). Those two notes are **not re-derived below** — their
findings are cited and carried forward. Today's 3 new lanes targeted only genuinely uncovered ground: (A)
foundations precision (FHRR specifically) + the 2020s fMRI evidence connecting TPR-style binding to real
neural data (not in either prior note); (B) the documented LIMITS of VSA for language — the grounding/vocabulary
problem and capacity/compositional-depth ceilings, specifically; (C) exactly what Spaun does with language, plus
one more fresh (2023-2026-biased) sweep for any VSA narrative/goal-tracking system, using search angles the
07-17 note's 13 combinations didn't try.

---

## HEADLINE

**Four independent lit-scans now (the two 2026-07 sibling notes plus today's two fresh angles) converge on the
same finding: nobody has built a VSA/HDC system that reads narrative text and tracks goals, outcomes, or
causal/relational structure across a story — this space is confirmed EMPTY, not merely unsearched.** Every
constituent primitive we use (FHRR bind/bundle/cleanup, role-filler binding, resonator-style factorization,
gated registers) is decades-deep, independently-validated prior art; the assembly of those primitives into a
goal/outcome/causal-tracking narrative comprehender is not published anywhere found. Separately, the VSA/HDC
literature is structurally, near-universally silent on where its atomic vectors' MEANING comes from — the
surveys describe assignment as "random" or "problem-dependent," never resolve it, and no major primary source
explicitly invokes the symbol-grounding problem by name — which is consistent with (does not contradict) our
own grounding wall being a real, family-wide structural feature of VSA, not a substrate-specific defect. A
second real limit, also confirmed absent from the literature rather than just unfavorable: nobody states a hard
numeric ceiling on COMPOSITIONAL NESTING DEPTH (as opposed to flat bundling capacity, which IS well-quantified)
— crosstalk-with-depth is acknowledged as real and is only kept manageable via an external cleanup memory, never
bounded with a number.

P_deflated (novel-synthesis "our narrative-goal-tracking VSA combination is unbuilt and this positioning is
correct" claim, capped per lit-scan calibration discipline): **0.42** — consistent with, not lower than, the two
prior sibling notes' independently-derived 0.42 figures; four convergent searches raise absence-of-evidence
confidence somewhat but the mandatory 0.50 novel-synthesis ceiling and standard deflation still apply. See
calibration section.

---

## Per-work table

| Work | What the VSA/HDC does | Language/narrative use? | Reusable for us | Known limit |
|---|---|---|---|---|
| Kanerva 1988 *Sparse Distributed Memory*; Kanerva 2009 (*Cognitive Computation* 1:139-159) | Foundational HDC: bundling (add/majority), binding (XOR/multiply), permutation, cerebellum-inspired associative memory | No — general-purpose; NLP use (HyperEmbed etc.) is later, downstream work | Kanerva's permutation-based stack construction (push/pop via re-permuting a superposed trace) — ready-made mechanism for our tier/register paging | Original proposal has no language-specific machinery at all |
| Plate 1995 (*IEEE TNN* 6(3):623-641); Plate 2003 book | HRR: circular convolution bind (real-valued), circular correlation (approximate) unbind + cleanup memory | Yes — explicitly motivated by encoding propositions (`eat(John,apple)`) and sentence semantics | The core algebra our substrate already uses; cleanup-memory pattern | Circular convolution is commutative — limits faithful encoding of nested/ordered structure without extra machinery; unbind is *approximate*, needs cleanup |
| **FHRR specifically** (Fourier-domain HRR: complex unit-magnitude phasors, binding = elementwise complex multiply, unbind = elementwise conjugate multiply) | Same algebra as HRR, exact by construction — unbind is EXACT (not approximate) and stays unit-magnitude, avoiding HRR's real-valued renormalization noise | Inherits Plate's language motivation | This IS our substrate's own representation family — confirms the choice is the field's own best-regarded variant (Schlegel/Neubert/Protzel found FHRR the most dimension-efficient of the compared VSA models) | Exact unbind removes ONE noise source (renormalization) but crosstalk from superposition/bundling still accumulates exactly as in real HRR |
| Gayler 2003 (ICCS/ASCS; arXiv:cs/0412059), MAP (Multiply-Add-Permute) | Bipolar {-1,+1} vectors, elementwise-multiply bind (self-inverse — no separate unbind op), add bundle, permutation for order | Motivated by rebutting Jackendoff's connectionism-binding challenges, but the framework itself is general-purpose | Algebraic contrast case: self-inverse bind vs. our conjugate-unbind; O(d) vs O(d log d) cost tradeoff worth knowing | Explicitly answers the SYNTAX/structure-binding challenge only — could not verify (PDF fetch failed both times across two independent scours) whether Gayler's own text ever states the semantics/grounding side is left open; treat as the standard secondary-literature reading, not a confirmed direct quote |
| Smolensky 1990 (*Artificial Intelligence* 46:159-216), Tensor Product Representations (TPR) | Role-filler binding via exact outer/tensor product; VSA operators (convolution, elementwise multiply) are understood field-wide as fixed-dimension LOSSY COMPRESSIONS of this same tensor-product binding | Not language-specific per se, but the parent formalism for later TPR-RNN language/QA work (see 07-18 note) | Conceptual parent of our bind operator; TPR-RNN's learned attention-based role/filler SELECTION mechanism (see 07-18 sibling note) is a credit-worthy training-signal pattern, retargetable onto our circular-convolution/FHRR binding | Dimensionality grows multiplicatively with nesting depth — exactly the blowup compressed VSA (HRR/FHRR/MAP) exists to avoid |
| **Frankland & Greene 2015 (*PNAS*), "An Architecture for Encoding Sentence Meaning in Left mid-STC"; Frankland & Greene 2020 (*Cerebral Cortex*), "Two Ways to Build a Thought"** | Not VSA — human fMRI. Decodes agent-vs-patient thematic-role assignment ("truck hit ball" vs "ball hit truck") from distinct neural populations in left mid-superior temporal cortex; 2020 paper adds amPFC (narrow, reused noun-verb conjunctions) as a second, complementary binding scheme | Yes — real sentence comprehension in human subjects, the actual target behavior | Independent biological existence-proof that the brain performs role-filler-style binding for sentence meaning, at all, in real neural tissue — directly supports our brain-foundational framing at the CONCEPT level | Purely behavioral/decoding evidence; does not itself specify which algebraic operator (tensor product vs. compressed convolution/multiply) the brain implements |
| **Lalisse & Smolensky 2021 (arXiv:2110.12342)**, reanalysis of the Frankland-Greene 2015 fMRI dataset | Reanalyzes the SAME fMRI dataset above, explicitly invoking Smolensky's 1990 TPR as motivating theory; tests whether neural role-bound patterns combine by (additive) vector superposition rather than bag-of-words | Yes — same sentence-comprehension fMRI data | The single most direct available link between TPR/VSA-style theory and real neural data — worth citing precisely, with the caveat below, for our "brain-vindicated" claim | **Important nuance, verified full-text (HIGH confidence): the actual analysis is linear-regression/additive superposition, NOT a literal tensor/outer-product test.** It shows joint agent+patient encoding beats single-role encoding (p=.010, p=.030) and that the two roles' neural codes are non-orthogonal/overlapping — consistent with distributed, superpositional binding IN GENERAL (compatible with the whole VSA family, including compressed operators like ours), but it does NOT decide between tensor-product-exact binding and compressed circular-convolution/multiply binding specifically. Cite this as "the brain does superpositional role-binding" — do not oversell it as "the brain uses circular convolution" or "the brain uses FHRR." |
| Kleyko, Rachkovskij, Osipov, Rahimi 2022 (ACM CSUR; arXiv:2111.06077 Part I, arXiv:2112.15424 Part II), VSA/HDC survey | Comprehensive survey of models, data transformations, applications, cognitive models, open challenges | Treats language as one application domain among many; does not systematically audit VSA's adequacy for open natural-language understanding | The field's own reference taxonomy — useful for standardized terminology and citing "state of the field" claims | States atomic hypervector meaning-assignment is "random" or must be "problem-dependent" and explicitly warns fully-random assignment "does not lead to any useful behavior" for many problems — the closest the survey gets to naming the grounding issue, but frames it as an encoding-DESIGN choice, not as an unresolved semantics/grounding problem by name |
| Schlegel, Neubert, Protzel (arXiv:2001.11797, *Artificial Intelligence Review*), VSA comparison | Head-to-head empirical comparison of VSA model families (HRR/FHRR/MAP/BSDC/VTB etc.) on bundling and binding+bundling capacity, and on sequential binding-chain degradation up to n=40 | No — capacity/engineering benchmark only, not a language task | **Standardized capacity-reporting format** (dimension-vs-item-count-at-99%-accuracy) our own capacity claims should be reported in for direct field comparability; concrete numbers: **FHRR needs ~330 dims to bundle 15 items at 99% accuracy; ~340 dims for combined binding+bundling** (MEDIUM confidence — pulled from a summarized table, not hand-verified against the primary PDF table) | Tests binding chains to depth 40 and finds VTB degrades less than HRR's convolution/correlation across the chain, but reports **no explicit numeric nesting-depth ceiling** — crosstalk accumulation is shown to require an external cleanup memory to stay usable, not bounded by the algebra itself. This appears to be a genuine literature gap (no paper found states a hard depth ceiling), not a search failure |
| Frady, Kent, Olshausen, Sommer 2020 (*Neural Computation* 32(12); arXiv:1906.11684), resonator networks | Iterative alternating-projection factorization of a bound composite vector back into codebook constituents, when direct search is combinatorially infeasible | No — general factorization/decode machinery | **Directly reusable upgrade candidate** for our own multi-role scene/register decode, already flagged in the 07-17 sibling note: stability threshold D_f/N <= 0.056, beats optimization baselines by ~2 orders of magnitude in operational capacity | Requires a formal stability regime (D_f/N <= 0.056) — not a drop-in win at arbitrary codebook-size/dimension ratios; needs a head-to-head test against our current direct-unbind+cleanup decode (already a pre-registered prediction in the 07-17 note) |
| Eliasmith et al. 2012 (*Science* 338:1202-1207), Semantic Pointer Architecture (SPA) / **Spaun** | SPA: circular convolution bind + superposition bundle + cleanup memory + gated neural integrators + basal-ganglia routing, all implemented in spiking neurons via the Neural Engineering Framework. Spaun = "the largest functional brain model," 8 tasks on ONE fixed model | **No open-text reading anywhere in the 8-task suite** — confirmed precisely today: copy-drawing, digit recognition, 3-armed-bandit RL, serial digit working memory, counting, position/identity query over a MEMORIZED DIGIT LIST (its "QA"), rapid rule induction, and a Raven's-matrices-style digit-sequence fluid-reasoning task. Every input is a handwritten digit image or digit/symbol sequence — there is no sentence, phrase, or story read or comprehended anywhere in Spaun | Eliasmith/Voelker's gated/latched integrator (register primitive), basal-ganglia-style routing/gating pattern, Choo's OSE item-position accumulation (already flagged, 07-17 note) | Spaun should never be cited as evidence VSA/SPA "does language" — it demonstrates cognitive breadth (perception-cognition-action integration) entirely within a closed, small, non-linguistic symbol vocabulary. This is a correction worth making explicitly if Spaun is ever invoked in our own product narrative |
| BEAGLE (Jones & Mewhort 2007, *Psychological Review* 114(1):1-37) | Holographic lexicon: signal vectors + convolution-built memory vectors, order via a placeholder vector, all superposed into one composite per word | Yes — reproduces synonymy, priming, cloze-probability effects from raw corpus text, no hand-coded grammar | Established prior art for corpus-driven distributional meaning; NOT a source of role-filler structure (see limit) | **Recchia et al. (2015) show directly that "bird eats worms" and "bird eats wings" are rated equally plausible** — BEAGLE conflates order-sensitivity with unordered gist and does not preserve retrievable role-filler bindings; static batch-trained corpus lexicon, not a running per-passage state (already established, 07-17 note) |
| Random Indexing (Kanerva/Sahlgren 2000/2005) | Incremental, fixed-dimension corpus-level lexicon via sparse random context-index accumulation | Yes — comparable to LSA on synonym tests | Incrementality lesson (accumulate-then-optionally-reduce) | Same as BEAGLE: static word-space construction method, not a discourse/relational tracker (07-17 note) |
| Kanerva 2010 (AAAI Fall Symposium), "dollar of Mexico" analogy | Bind two composite role-filler country-records together; corresponding-role cross-terms dominate; cleanup-memory nearest-neighbor decode recovers "Peso" | Yes, as a worked toy example — not a system for open text | Confirms our own goal/outcome REGISTER approach (bind attribute-role to filler, bundle into one composite, decode via cleanup) is exactly this field's own canonical reasoning pattern, just applied to registers instead of country-records | Toy/small-vocabulary demonstration, not validated at open-domain scale |
| Schlag & Schmidhuber 2018/2019 (NeurIPS), TPR-RNN; Palangi, Smolensky, He, Deng 2017/2018 | LEARNED, end-to-end-trained role/filler binding via attention, evaluated on bAbI / SQuAD / MNLI-era baselines | Yes, synthetic/mid-scale QA and NLI | Attention-based learned role-AND-filler-selection training pattern is the closest existing recipe for "how do you train a binder" (07-18 note); representation-family SWAP target (tensor product -> our FHRR) is a pre-registered, not-yet-run prediction from that note | Exact tensor-product representation (not compressed VSA), and small/synthetic/pre-transformer-era benchmarks only — never pushed to open natural-language narrative at scale (07-18 note) |
| PSI (Cohen, Widdows, Rindflesch, Schvaneveldt, ~2009-2014) | Compressed-VSA (permutation+bundling, HRR/Random-Indexing family) reasoning over SemRep-extracted subject-predicate-object triples at real MEDLINE corpus scale; demonstrated genuine multi-hop chain discovery | Yes, over real (if hand-extracted) biomedical text at scale | Closest existing proof that a compositional VSA reasoner CAN consume relational structure at real scale; its multi-hop chaining/query algorithm is a concrete design reference for our own causal-register reasoner (07-18 note) | The "reading" step (triple extraction) is entirely HAND-BUILT via SemRep's rule-based pipeline — proves VSA reasoning over text-derived triples works, while leaving learned extraction completely unaddressed |
| HolE (Nickel, Rosasco, Poggio 2016) / ComplEx-equivalence (Hayashi & Shimbo 2017) | Circular-correlation-based (same operator family as HRR unbind) LEARNED knowledge-graph embeddings, competitive link-prediction accuracy | No — operates only over pre-curated KG triples, never touches raw text | Confirms compressed-HRR-family binding IS learnable end-to-end via plain gradient descent for compositional relational scoring | No paper extends this to relations extracted directly from raw text instead of a curated KG (07-18 note) |
| Grosz & Sidner 1986 (*Computational Linguistics* 12(3):175-204) | NOT VSA — symbolic discourse theory: attentional state = a stack of focus spaces, push/popped per discourse segment | Yes — genuine multi-sentence discourse structure theory | Closest existing STRUCTURAL precedent (non-vector) for our own tiered register/paging design; already a pre-registered design-audit prediction in the 07-17 note | Never cast in vectors by anyone; own 1999 follow-up flags interruption/pronominal edge cases plain stacks don't cleanly handle |
| QAVSA (Laube & Eliasmith 2024, RepL4NLP-2024, ACL Anthology) | VSA encoding of a STATIC, pre-loaded knowledge graph to augment an LM on multiple-choice QA | Reasoning over pre-loaded KG triples, not per-instance narrative tracking | Confirms Eliasmith's own group is still active in this space as of 2024 — periodically worth re-checking for follow-on work; re-verified today, **no 2025/2026 follow-up found** despite a targeted search | Static KG, not a story/passage read sentence-by-sentence; does not track goals/outcomes/causal structure across a narrative |
| PathHD (arXiv:2512.09369, late 2025) | HDC relation-path encoding coupled with an external LLM call per query over knowledge-graph paths | Adjacent — KG-based, not narrative text | None directly (requires an LLM at inference, disqualifying for our glass-box design anyway) | Newest adjacent 2025 hit found in today's fresh sweep; still not narrative comprehension, still not glass-box |

---

## Focus questions — answered explicitly

### 1. Has anyone built a VSA/HDC system that reads narrative and tracks goals/outcomes/relations — or is that space empty?

**Empty, confirmed across four independent search passes now** (07-17 note's discourse/situation-model gap-check
with 13 distinct search-term combinations against Centering Theory/Grosz-Sidner/Kintsch-CI/Zwaan; 07-18 note's
learned-parse-into-VSA scour; and today's two fresh lanes — Spaun's actual task suite, and a 12-angle
2023-2026-biased re-sweep using plan-recognition/goal-tracking/story-understanding/reading-comprehension search
terms not tried before). The 2023-2026-biased sweep's closest hits (QAVSA, PathHD, abductive-reasoning-on-Raven's-matrices,
ARC-puzzle VSA, LARS-VSA, VSA4VQA, a probing-only "Hyperdimensional Probe") are all either static
pre-loaded-knowledge-graph reasoning, visual/grid-puzzle abstraction, or post-hoc probing of an LLM's own
internals — none reads a story and tracks what a character wants, whether they got it, and why. **Say plainly:
our combination (FHRR + goal/outcome/causal registers + goal-ownership tracking, applied to narrative
comprehension) is genuinely unbuilt prior art, not merely under-searched.** The standard absence-of-evidence
caveat applies (a differently-named or differently-venued system could exist), but four independent, differently-angled
searches converging on the same gap is about as strong as this kind of negative claim gets without exhaustively
enumerating every venue.

### 2. What are the documented limits of VSA for language — especially grounding/vocabulary and compositional-depth/capacity — and do these predict our grounding wall?

**Grounding/vocabulary problem: the literature is structurally silent, not structurally solved — and that
silence is itself informative.** The two flagship modern surveys (Kleyko/Rachkovskij/Osipov/Rahimi Parts I & II)
describe atomic hypervector assignment as "random" or requiring "problem-dependent" encoding design, and warn
that fully-random assignment "does not lead to any useful behavior" for many problems — but this is framed as an
encoding-DESIGN choice, never resolved, and never explicitly named as the symbol-grounding problem (Harnad
1990) despite that being the obvious frame. No primary VSA source found (Kanerva, Plate, Gayler, or the modern
surveys) explicitly states "VSA supplies compositional syntax/algebra but not semantic grounding" in so many
words — though Gayler's own framing (VSA answers Jackendoff's *combinatoriality/binding* challenges specifically)
is consistent with that reading, and no counter-claim was found anywhere either. **This predicts our grounding
wall directly: it is a family-wide, decades-old, never-resolved gap in the whole VSA/HDC literature, not a
substrate-specific defect we introduced.** Every VSA language system found across all four scours (BEAGLE,
Random Indexing, PSI, HolE/ComplEx, TPR-RNN, SPA/Spaun) either (a) derives its atomic vectors from distributional
corpus statistics (meaning = co-occurrence pattern, not grounded reference), (b) hand-assigns them by fiat
(SPA/Nengo scripts, PSI's SemRep pipeline), or (c) never addresses the question because it operates over
pre-curated symbolic input (HolE/ComplEx's KG triples) — none grounds atomic meaning in perception/action, which
is exactly our own stated open wall.

**Compositional-depth/capacity: flat capacity IS well-quantified; nested-depth ceilings are NOT, and that gap
is itself the literature's limit, not ours.** Schlegel/Neubert/Protzel give concrete, standardized numbers (FHRR
needs ~330 dimensions to bundle 15 items at 99% accuracy, ~340 with combined binding+bundling — MEDIUM
confidence, pulled from a summarized table) and test sequential binding chains to depth 40, finding VTB degrades
less than HRR's convolution/correlation across the chain — but no paper anywhere in this scour states an explicit
numeric "fails beyond nesting depth k" threshold; crosstalk-with-depth is acknowledged as real and is only kept
usable via an external cleanup/denoising memory. This means our own multi-level register nesting (goal inside
outcome inside causal-chain) sits in a regime the field itself has not bounded with a number — a real limit on
what we can borrow (there's no formula to check our own depth against), not evidence our depth is fine or unfine
either way.

### 3. What VSA techniques are directly reusable/instructive for our goal-outcome registers + referent tracking?

Ranked by direct applicability (full detail already logged in the 07-17/07-18 sibling notes, carried forward
here, plus two additions from today):

1. **Resonator networks (Frady/Kent/Olshausen/Sommer)** — iterative factor-decode upgrade over naive
   unbind+nearest-neighbor cleanup for our multi-role scene/register retrieval; comes with a formal stability
   threshold (D_f/N <= 0.056) to check our own decode setup against, and a standardized "operational capacity"
   metric.
2. **Eliasmith/Voelker's doubly-latched gated integrator + Choo's Ordinal Serial Encoding** — a controllably-latched
   O(1) register primitive (for a "current active goal" pointer) plus item-position accumulation (for "when was
   this outcome recorded") — both independently validated against human primacy/recency data, not just
   capacity claims.
3. **Kanerva's permutation-based stack construction** (shift-permute-then-bundle) — ready-made push/pop
   mechanism for tiered register paging (e.g. goal -> sub-goal -> outcome), rather than inventing a new paging
   primitive.
4. **Grosz & Sidner's stack-of-focus-spaces** — the closest non-vector structural precedent for a tiered
   attentional/register design; worth a cheap structural cross-check against our own tier boundaries before
   committing further engineering (flagged as a pre-registered, near-zero-cost design audit in the 07-17 note).
5. **PSI's multi-hop chaining/query algorithm** — closest existing proof-of-concept that a compressed-VSA
   reasoner consumes relational structure at real scale; a concrete design reference for our causal-register
   reasoner specifically.
6. **Schlegel/Neubert/Protzel's standardized capacity-reporting format** (dimension-vs-item-count-at-99%-accuracy)
   and Frady/Kleyko/Sommer's SNR-scaling law (`s = sqrt(N/M)`) — adopt as the reporting convention for our own
   register-capacity claims, for direct field comparability instead of ad hoc framing.
7. **(New today) The Lalisse & Smolensky fMRI reanalysis** — a legitimate, citable data point for "the brain
   does distributed/superpositional role-binding for sentence meaning, at all" (supports our conceptual
   brain-foundational framing), used CAREFULLY: it validates superpositional binding IN GENERAL, not our specific
   compressed circular-convolution/FHRR operator over tensor-product-exact binding. Do not overclaim
   operator-level neural vindication.
8. **(New today) FHRR's exact (not approximate) unbind via conjugate multiplication** — confirmed as the
   field's own most dimension-efficient compared variant (Schlegel/Neubert/Protzel) and structurally cleaner
   than real-valued HRR (no renormalization-noise source) — an validation, not a change, of our existing
   representation choice.

---

## Cheap decisive test

No new cell required — this is a landscape scan, not a falsifiable-mechanism drill. The single cheapest
next action already flagged in the 07-17 sibling note (Prediction 4: cross-check our Tier-0/1/2/3 register
design against Grosz-Sidner's focus-space stack on 5 hand-constructed interruption/topic-return passages) remains
the lowest-cost, zero-compute follow-up open from this whole three-note arc, and is reaffirmed here rather than
duplicated.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, carried forward + one new)

The 07-17 and 07-18 sibling notes already carry 6 pre-registered, not-yet-run predictions (resonator-decode vs.
direct-decode; permutation vs. convolution order encoding; ACT-R fan-effect crosstalk validation; Grosz-Sidner
structural design audit; TPR-tensor-to-FHRR representation swap on bAbI; learned vs. hand-rule role-assigner) —
not restated in full here to avoid duplication; see those notes directly. One new prediction from today's scan:

**Prediction 7 — our register-capacity claims, reported in Schlegel/Neubert/Protzel's standardized
dimension-vs-item-count-at-99%-accuracy format, land within the same order of magnitude as their reported FHRR
figures (~330-340 dims for ~15 bundled items) at our own operating dimensionality.**
P = **0.40** (deflated; their benchmark task (arbitrary random-vector bundling) differs from our specific
goal/outcome/causal register content and access pattern, and this is our own extrapolation, not a cited
transfer).
HARD-PASS: at matched dimensionality, our registers hold >=15 concurrently-bundled role-filler pairs at >=99%
correct-retrieval, consistent with (within ~20%) the published FHRR curve.
HARD-FAIL: our registers require >2x the dimensionality Schlegel/Neubert/Protzel's curve predicts for the same
item count/accuracy — would indicate our specific register content (goal/outcome semantics, not arbitrary random
vectors) is harder-than-generic for FHRR to hold, and the published capacity curve is not a safe planning number
for us without a correction factor.

---

## Cross-thread synthesis

- **Directly extends, does not duplicate,** `research_vsa_hdc_state_of_mind_prior_art_scour_2026-07-17.md` and
  `research_vsa_learned_reader_prior_art_scour_2026-07-18.md`. Those two notes established: (a) the
  discourse/situation-model gap in VSA is confirmed empty via 13 search-term combinations; (b) the
  learned-parse-into-VSA combination is confirmed empty via 3 lanes; (c) a ranked list of 9 reusable mechanisms.
  Today's scan reaffirms (a) and (b) under a FOURTH independent, more recent-dated search (raising confidence in
  the negative finding without changing it), and adds three genuinely new items those notes did not have: FHRR's
  precise mathematical distinction from real-valued HRR, the Frankland-Greene/Lalisse-Smolensky fMRI evidence
  (with the important "superpositional-in-general, not operator-specific" caveat), and the explicit finding that
  the grounding/vocabulary problem is structurally UNADDRESSED (not solved, not even named) across the modern
  survey literature — the strongest available evidence that our own grounding wall is a field-wide condition,
  not a build defect.
- **Directly informs `notes/SYNTHESIS_grounding_wall_definitive_2026-08-06.md`** and
  `notes/audit_SYNTHESIS_semantic_meaning_barrier_2026-08-06.md` (today's other in-flight grounding-wall work,
  not read in full here to keep this scan's scope bounded to literature per its own dispatch instructions) — this
  note supplies the EXTERNAL literature confirmation that the grounding wall those documents are working through
  from the brain-fidelity side is not unique to our substrate; it is the whole VSA/HDC family's unresolved
  condition, which should sharpen (not soften) the internal framing of grounding as the deep, structural,
  decades-old open problem it is.
- **Reaffirms, does not revise, the standing choice of FHRR** as our representation family — it is the field's
  own best-performing compared variant on the one standardized capacity benchmark that exists (Schlegel et al.),
  and its exact-unbind property is a genuine (if narrow) mathematical advantage over real-valued HRR.

---

## Substrate-product implications

1. **The novelty claim for "VSA-based narrative goal/outcome/causal tracker" is defensible and should stay
   narrow and specific**, exactly as the two sibling notes already concluded: we did not invent bind/bundle/
   cleanup, role-filler binding, or resonator decode — we assembled decades-old, independently-validated VSA
   primitives into a discourse-level, goal/outcome-tracking assembly that, across four independent searches, no
   one else has published. This is the accurate framing; "novel algebra" or "novel binding operator" claims are
   not supported and should not be made.
2. **The grounding wall should be framed, internally and in any product narrative, as a known, unresolved,
   field-wide VSA/HDC condition** — not a bug specific to our build. This is a stronger and more honest position
   than either overclaiming a fix or treating it as evidence something is wrong with our specific implementation.
   It also means: don't expect an off-the-shelf VSA-literature fix to arrive for grounding — the field has not
   solved this in 35+ years of HRR/VSA work; whatever grounding mechanism we build will itself be the novel
   contribution, not a borrowed one.
3. **No paper anywhere in this scan bounds compositional nesting depth with a number** — our own register-nesting
   design (goal inside outcome inside causal chain) cannot be checked against a published depth ceiling; only
   flat bundling capacity is standardized. Any depth-related capacity claim we make is necessarily our own
   measurement, not a literature-anchored one.
4. **Cite the Lalisse & Smolensky fMRI reanalysis carefully.** It is a real, verifiable, directly-relevant data
   point supporting "the brain performs distributed/superpositional role-binding for sentence meaning" — useful
   for our brain-foundational framing at the concept level. It does NOT specifically validate circular
   convolution / FHRR's operator over tensor-product-exact binding; oversell here would be an unforced,
   easily-caught overclaim.
5. **Spaun should not be cited as prior evidence that VSA/SPA systems "do language."** Its entire 8-task suite
   operates over handwritten digits and small closed symbol sequences; it never reads a sentence or answers a
   comprehension question about a passage. If Spaun comes up in future product or research framing, this
   correction should be applied.

---

## Calibration reasoning (P_deflated = 0.42 headline; per-prediction P 0.40)

Raw confidence in the DIRECT literature findings from today's three lanes (FHRR's exact mathematical
distinction from HRR, the Frankland-Greene/Lalisse-Smolensky citation chain and its actual analysis method,
Kleyko et al.'s survey framing of atomic-vector assignment, Schlegel/Neubert/Protzel's capacity numbers, Spaun's
precise 8-task suite, and the fresh 12-angle narrative-VSA re-sweep) is high (~0.75-0.85) for the items verified
via direct source fetch (Spaun's task list via the primary Science paper; Lalisse & Smolensky's method via ar5iv
full text; Schlegel/Neubert/Protzel's qualitative depth-chain finding), and explicitly lower (~0.45-0.55,
flagged inline per-item above) for items where PDF/table extraction degraded or failed during this session (the
exact 330/340-dimension figures; the precise wording of Kleyko Part II's "Open issues" section; Gayler's own
primary-text wording on the syntax-not-semantics distinction) — these are marked LOW/MEDIUM confidence inline in
the per-work table rather than smoothed into the headline number. Standard lit-scan deflation (0.15-0.25) applied
throughout. The overall novel-synthesis claim (that our narrative-goal-tracking VSA combination is genuinely
unbuilt, and that this positioning + the reusable-mechanism ranking is the right read of the field) is capped at
the mandatory 0.50 ceiling and held at 0.42 — matching, not exceeding, the two sibling notes' independently-derived
figures — because: (i) absence-of-evidence claims are structurally weaker than positive findings even after four
convergent searches; (ii) none of today's or the sibling notes' falsifiable predictions have been run; (iii) two
of today's three lanes explicitly flagged PDF/table extraction failures requiring reliance on
summarized/secondary readings for some numeric claims (noted per-item above, not hidden).

---

## Citations (verified count)

**3 parallel Sonnet lit-scan lanes this cycle, ~29 distinct external primary/secondary sources located and
cross-checked** (a mix of direct full-text fetches — HIGH confidence — and search-snippet-level findings —
flagged MEDIUM/LOW inline above), plus ~55 additional sources credited from the two 2026-07 sibling notes
(cited, not re-verified here — see those notes' own citation lists for the full count): Kanerva 1988 (SDM,
MIT Press); Kanerva 2009 (*Cognitive Computation* 1:139-159); Plate 1995 (*IEEE TNN* 6(3):623-641); Plate 2003
(book); Gayler 2003 (ICCS/ASCS; arXiv:cs/0412059); Smolensky 1990 (*Artificial Intelligence* 46:159-216);
**Frankland & Greene 2015 (*PNAS*, sentence-meaning fMRI decoding)**; **Frankland & Greene 2020 (*Cerebral
Cortex*, "Two Ways to Build a Thought")**; **Lalisse & Smolensky 2021 (arXiv:2110.12342)**; Kleyko, Rachkovskij,
Osipov & Rahimi 2022 (ACM CSUR; arXiv:2111.06077 Part I, arXiv:2112.15424 Part II); Schlegel, Neubert & Protzel
(arXiv:2001.11797, *Artificial Intelligence Review*); Clarkson, Ubaru, Yang et al. (arXiv:2301.10352, VSA
capacity analysis); Harnad 1990 (symbol grounding problem, canonical source, cited for definitional framing
only); Frady, Kent, Olshausen & Sommer 2020 (*Neural Computation* 32(12); arXiv:1906.11684, resonator networks);
**Eliasmith, Stewart, Choo, Bekolay, DeWolf, Tang & Rasmussen 2012 (*Science* 338:1202-1207, Spaun full task
suite re-verified today)**; **Kanerva 2010 (AAAI Fall Symposium, "dollar of Mexico" re-verified today)**; Laube
& Eliasmith 2024 (RepL4NLP-2024, ACL Anthology, QAVSA, re-verified today, no 2025/2026 follow-up found);
**PathHD, arXiv:2512.09369 (late 2025, new hit today)**; arXiv:2501.11896 (abductive reasoning on Raven's
matrices, checked and excluded — not narrative); arXiv:2511.08747 (VSA for ARC visual puzzles, checked and
excluded); LARS-VSA arXiv:2405.14436, VSA4VQA arXiv:2405.03852, Hyperdimensional Probe arXiv:2509.25045 (all
checked and excluded — visual/spatial or LLM-probing, not narrative text). Two of today's three lanes explicitly
flagged PDF/table-extraction tooling failures (Gayler's primary text; Kleyko Part II's "Open issues" section
body; exact Schlegel et al. table figures) rather than guessing — excluded from load-bearing predictions, noted
inline per-item in the table above.

**Internal cross-thread**: `research_vsa_hdc_state_of_mind_prior_art_scour_2026-07-17.md`;
`research_vsa_learned_reader_prior_art_scour_2026-07-18.md`; `SYNTHESIS_grounding_wall_definitive_2026-08-06.md`;
`audit_SYNTHESIS_semantic_meaning_barrier_2026-08-06.md` (today's other in-flight grounding-wall work, cited by
title only, not read in full — out of scope for this literature scan per its own dispatch instructions).

---

## Status

Written per research-agent contract. USER-locked discipline applied: **no `exp_dev_handoff_*.md` or
`strategy_request_to_*.md` routing files written** (ferry mechanism deprecated per current session
instructions) — every actionable pointer is inline above (per-work table, ranked reusable-mechanism list,
one new falsifiable prediction with pre-registered thresholds, cheap-decisive-test pointer to the existing
07-17-note prediction). Know-the-landscape only; no direction change recommended. No cap_map, strategy files,
or `goal_typing.py` modified.
