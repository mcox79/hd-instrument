# Research: Flagship-benchmark scoping -- WIQA / TORQUE / MC-TACO (2026-08-10)

Filed by: research (Sonnet, foreground, no nested sub-agents, no background waits, per explicit
dispatch instruction). This drill scopes the flagship-benchmark pivot that E4's temporal gate-test
(MIDDLE_BAND, 2026-08-10) opened: the augment-not-replace + abstain-gate architecture is validated
(no-regression confirmed 3 seeds; order-attributable lift where it fires) but MCScript2.0 is now
CONFIRMED (twice) content-saturable and the temporal residual is thin (+0.017, fires on ~11% of
temporal questions) -- the flagship demonstration needs a benchmark where content/BoW is PROVABLY
ceilinged, not thinly swamped.

KB-CHECK DONE FIRST: `substrate_query.sh "WIQA TORQUE MCTACO causal temporal benchmark glass-box
no-LLM feasibility BoW ceiling"` returned no prior drills on these three benchmarks (top hit
cosine=0.27, generic "feasibility" atom match, not a substantive prior finding) -- confirmed this is
new ground, not a rediscovery. `research_field_advisor.py` run (110 drills, 22 fields) -- its
field-coverage heuristic covers substrate-physics fields (thermodynamics, spin-glass, free-probability
etc.), not benchmark selection, so it does not directly rank this drill; noted and not force-fit.
Read in full this cycle: `notes/research_e4_inference_augmented_comprehension_design_2026-08-10.md`
(Section 1d already named TORQUE/MCTACO/WIQA/ROPES/QuaRTz as candidates and gave a directional
recommendation -- this drill VETS that recommendation with real data rather than re-deriving it from
scratch) and the TOP block of `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` (full night arc:
store arc 2A-2G closed, E3 grounding-shape fix, E4 augment design + gate-test MIDDLE_BAND, current
strategic fork). Local disk checked: `data/corpora/` has no WIQA/TORQUE/MCTACO data present (confirmed
via directory listing + filename search) -- all three would be a fresh pull. Owned organs inventoried
directly from `hdlab/`: `situation_model_accumulate.py` (`CausalLinkRegister` with
`add_causal_link`/`query_cause_of`/`query_effect_of`, `RelationRegister`), `kg_traversal.py`,
`selection_weighted_sharded_typer.py`, `cleanup_family.py`, `hippocampal_encoder.py`,
`situation_focus.py`, `situation_reader.py`, `mcscript_extraction.py`, `outcome_event_extraction.py`,
`coreference_resolver.py`. Four generic-term web scans this cycle (public benchmark names only, no
substrate-novel terms, per query-privacy discipline -- consistent with the E4 note's own precedent of
naming MCScript2.0/TORQUE/MCTACO/WIQA as public dataset names off-platform).

---

## HEADLINE

**WIQA is the recommended flagship pick.** It is the only one of the three whose task SHAPE is a
near-literal match for our one HARD_PASS-certified inference mechanism (Stage-2A retrieve-VALIDATE-
advance causal chaining, whose validated finding is specifically that VALIDATE arrests multiplicative
error across multi-hop chains) -- WIQA's core structure (paragraph = process steps, perturbation =
signed cause, question = "more/less/no effect" on a downstream step) IS a multi-hop signed causal-chain
propagation problem, which is exactly `CausalLinkRegister` plus one small polarity extension, not a new
organ. It is public, downloadable now (Hugging Face `allenai/wiqa`), sized well (29,808 train / 6,894
dev / 3,003 test), and has a large, well-documented SOTA-to-human gap (73.8 vs 96.3, +22.5) with a
near-chance majority baseline (30.66% vs 33% chance on a 3-way task) that rules out the single most
common shortcut (always guess the frequent label).

**The honest gap: no one has published a strict bag-of-words / lexical-overlap baseline for WIQA** (the
original paper reports majority-class and neural baselines, not an IR-style lexical baseline, because
the task is 3-way classification, not span-picking over free text the way MCScript2.0 is). This means
axis 3 (content ceiling) is NOT yet proven by citation the way it was for MCScript2.0 (BoW=0.629,
measured directly off our own disk). It must be measured ourselves, first, before any HARD-PASS claim
-- and the right WIQA-analog of "BoW" is not text-overlap-with-the-passage (weak signal, since answers
are fixed labels, not text spans) but **polarity-echo**: predict the label literally stated in the
perturbation clause ("suppose MORE sunlight..." -> predict "more") ignoring the causal chain. This is
the surface shortcut most likely to fool a naive glass-box scorer on WIQA, is cheap to build, and is
the correct first-experiment baseline arm (see Section 4). Until that number is on disk, "WIQA is
content-ceilinged" is a strong hypothesis (majority-class near-chance + explicit external-perturbation
design + large SOTA/human gap), not a verified fact -- flagged honestly, not glossed over.

**TORQUE has the cleanest structural content-ceiling of the three** (candidates are drawn FROM the
passage's own event-trigger vocabulary, so lexical overlap cannot discriminate between them at all --
every candidate shares the source text), but its task format (multi-label span selection over a
pre-tagged event set, scored by macro F1/EM over sets) is the largest departure from our existing
pick-the-answer MC scorer and needs full-pairwise temporal-relation extraction we have not built or
validated at this granularity (our owned temporal mechanism, from the E4 gate-test, is adjacency-based
predecessor/successor retrieval in an accumulated sequence, not full pairwise before/after/includes/
simultaneous classification over an event set). Recommended as the STRONG SECOND pick / near-term
follow-on, not the first move.

**MC-TACO is the weakest fit.** Only 1 of its 5 categories (event ordering, ~20% of 13k) maps onto our
validated temporal-adjacency mechanism; the other four (duration, frequency, typical-time, stationarity)
require a MAGNITUDE/DURATION commonsense knowledge base we do not have and CSKG's causal edges do not
supply (CSKG is a causal graph, not a durational one). Binary yes/no format is the simplest to score,
and data access is clean (Hugging Face `CogComp/mc_taco`), but building toward it means building a new
knowledge source, not reusing the validated organ -- recommend NOT the flagship, revisit only if a
durational-KB acquisition project is independently justified later.

P_deflated = **0.32** for "the WIQA causal-chain-loop HARD-PASSes the pre-registered first experiment"
(Section 4) -- deflated per lit-scan calibration (novel-synthesis cap 0.50; minus: no published lexical
baseline to anchor against, the polarity-echo shortcut is untested and could be strong on single-hop
questions, and the CausalLinkRegister polarity extension + paragraph-to-chain extraction is new
engineering, not yet built). P = **0.60** (less deflated -- this is a benchmark-fit/selection judgment,
a materially lower-risk claim than a mechanism win) for "WIQA is the correct flagship choice among the
three named candidates," which is the actual question this drill answers.

---

## 1. Per-candidate scorecard

### 1a. WIQA (Tandon et al. 2019, EMNLP-IJCNLP, "What if... reasoning over procedural text")

| Axis | Finding |
|---|---|
| **1. Data availability** | Public, `allenai/wiqa` on Hugging Face + original AI2 release. 39,705 questions total: 29,808 train / 6,894 dev / 3,003 test, over 2,107 crowdsourced influence graphs across 379 process paragraphs. Test labels are likely leaderboard-reserved (not independently confirmed this cycle) -- use DEV (6,894, plenty for statistics) as our held-out split, same practice as MCScript2.0. No license blocker found in this scan; AI2 datasets are typically open for research use -- NOT independently verified this cycle, flag for exp_dev to confirm at pull time. |
| **2. Task format** | 3-way classification per (paragraph, perturbation-clause, outcome-clause) triple: label in {MORE, LESS, NO_EFFECT}. Not span-picking, not open generation -- closest to MCTACO's binary-per-candidate shape but with 3 fixed classes instead of yes/no. Requires a small reshape of our existing 2-candidate MC scorer into a 3-class scorer (or equivalently, a directed-sign classifier), not a wholly new scoring paradigm. |
| **3. Content ceiling** | Majority-class baseline = 30.66% (near the 33% 3-way chance floor -- the label distribution is roughly balanced, so "always guess most common" is not a shortcut). Published SOTA = 73.8%, human = 96.3% -- a 22.5-point gap above SOTA and a 43-point gap above majority, both large. BUT: no published bag-of-words / lexical-overlap baseline exists (the paper's baselines are majority-class and neural, e.g., BERT/GPT-style). The dataset was explicitly designed with "external" (out-of-paragraph, commonsense) perturbation questions specifically to force reasoning beyond the paragraph text. Net honest read: STRONG CIRCUMSTANTIAL evidence of a content ceiling (near-chance majority baseline + explicit out-of-text design + large human gap), NOT yet a verified number the way MCScript2.0's BoW=0.629 was. The real risk is a DIFFERENT shortcut than BoW: **polarity-echo** (predicting the label word literally stated in the perturbation), which the first experiment must measure and beat (Section 4). |
| **4. Glass-box feasibility** | HIGH. The encode+augment loop needs: (a) per-step event/predicate extraction from the process paragraph (reuse `extract_events`/`mcscript_extraction.extract_args`, both owned, with the E3 present-tense fix already scoped); (b) a SIGNED CAUSE/EFFECT edge between adjacent/connective-linked steps -- a direct, small extension of `CausalLinkRegister.add_causal_link` (add a polarity bit to the existing CAUSE/EFFECT role pair, same accumulate-register infrastructure, same bind/bundle/unbind/cleanup_argmax chain the class's own docstring describes as the reusable pattern -- this is NOT a new organ, it is the same organ's third instantiation after `AccumulateRegister`/`RelationRegister`); (c) anchor location for the perturbation clause and the outcome clause via `cleanup_family.iterative_attractor`/`pull_in` (owned, HARD_PASS toy-validated in Stage-1); (d) SIGN PROPAGATION along the retrieved causal path (multiply polarities hop-by-hop) with VALIDATE at each hop -- this is EXACTLY the Stage-2A mechanism (multi-hop chaining, VALIDATE arrests multiplicative error), just with a sign-multiply instead of a plain traversal. No LLM at inference anywhere in this chain. |
| **5. Fit with validated machinery** | BEST of the three. Stage-2A's HARD_PASS finding (VALIDATE arrests multiplicative error across multi-hop causal chains) is precisely what WIQA's multi-hop influence-graph structure exercises, and MCScript2.0 gave that organ almost no target (0.7% causal-"why" questions, per the E4 note). WIQA is effectively the causal loop's home benchmark by construction (Tandon et al. built the dataset AS a causal-chain-of-effects task). |

### 1b. TORQUE (Ning, Wu, Han, Peng, Roth 2020, EMNLP, "A Reading Comprehension Dataset of Temporal Ordering Questions")

| Axis | Finding |
|---|---|
| **1. Data availability** | Public, GitHub `qiangning/TORQUE-dataset` + AllenNLP-hosted leaderboard/talk. 3.2k news-snippet passages, ~21k-30.4k questions depending on how "3 hard-coded (past/ongoing/future) + user-generated" questions are counted in different summaries (this discrepancy is UNRESOLVED this cycle -- flag for exp_dev to pull and count directly rather than trust either secondary summary). Dev split should exist per standard EMNLP release practice; not independently confirmed this cycle. No license blocker found. |
| **2. Task format** | Multi-label span/set selection: given a passage with PRE-TAGGED event triggers (the triggers are provided, not something we must detect ourselves) and a question ("what events had already started before event E", "what is ongoing now"), the answer is a SUBSET of the provided event-trigger tokens. Scored by macro F1 + exact-match (EM) over the answer SET, not accuracy over a fixed small candidate list. This is a materially different scorer shape than the 2-way/3-way pick-the-best-candidate machinery built for MCScript2.0/proposed for WIQA -- needs a set-valued scorer and a per-event-pair temporal-relation judgment, not a single best-of-N pick. |
| **3. Content ceiling** | CLEANEST of the three, structurally. Because every answer candidate IS a token drawn from the same passage (the event triggers are pre-extracted from the text itself), a bag-of-words/lexical-overlap-with-passage baseline is close to VACUOUS -- all candidates share the source vocabulary by construction, so overlap-with-passage cannot discriminate between "this event happened before E" and "this event happened after E." The only way to answer is genuine temporal-relation reasoning. Numbers: RoBERTa-large (best system found this cycle) = 51% EM on test, human = 84.5% EM / 95.3 F1 (measured by one author against crowd annotations on 100 test questions) -- a 33.5-point EM gap, the largest human/SOTA gap of the three. |
| **4. Glass-box feasibility** | MEDIUM. Upside: event triggers are GIVEN (removes the MCScript2.0-style "39% of candidates extract to zero events" extraction failure mode entirely -- the hardest part of our real-prose pipeline is pre-solved by the dataset's own annotation). Downside: TORQUE questions require genuine PAIRWISE temporal-relation judgments (before/after/includes/simultaneous) across potentially many event pairs per passage, not just adjacency in one accumulated sequence. Our currently-validated temporal mechanism (from the E4 gate-test, MIDDLE_BAND, this same session) is adjacency-based (predecessor/successor retrieval in `situation_model_accumulate`'s accumulated sequence) -- it has NOT been tested as a full pairwise relation classifier across a whole event set. This is a real, not cosmetic, capability gap: extending accumulated-sequence adjacency retrieval to answer "did event A start before OR during OR after event B, for arbitrary A/B in this passage" needs either (a) a transitive-closure walk over the accumulated ordering (cheap, reuses the sequence structure, if the ordering is fully linearizable) or (b) genuine interval/Allen-relation reasoning (harder, if the passage has concurrent/overlapping event structure TORQUE explicitly targets with "ongoing" questions). |
| **5. Fit with validated machinery** | GOOD but PARTIAL. Directly exercises the E4 temporal route (already gate-tested, MIDDLE_BAND, no-regression confirmed) rather than the causal route. But the E4 route was validated on SIMPLE precedence questions ("when did X happen relative to Y") at a thin fire-rate (~11% on MCScript2.0); TORQUE's "ongoing"/multi-relation questions ask a strictly harder question of the same underlying mechanism. Fit is real but shallower than WIQA's fit to the causal loop, and the F1-over-sets scorer is new engineering. |

### 1c. MC-TACO (Zhou, Khashabi, Ning, Roth 2019, EMNLP, "Going on a vacation takes longer than going for a walk")

| Axis | Finding |
|---|---|
| **1. Data availability** | Public, Hugging Face `CogComp/mc_taco` + GitHub `CogComp/MCTACO`. 13k (sentence, question, candidate-answer) tuples with dev/test splits specified in the paper (exact counts not independently pulled this cycle). No license blocker found. |
| **2. Task format** | Binary classification per candidate: given (context sentence, question, one candidate answer), predict plausible (yes) or not (no). Simplest scorer shape of the three (no set-valued or multi-class machinery needed) -- a direct extension of a margin/confidence-gated binary scorer. |
| **3. Content ceiling** | Real but the least CLEAN of the three as a "content cannot answer this" story. Random F1=36.2/EM=8.1; Always-Positive F1=49.8/EM=12.1; Always-Negative F1=17.4/EM (search result gave 17.4 for both metrics on this arm, which reads as a possible transcription artifact in the secondary source -- flag as UNVERIFIED, re-derive from the primary paper table before use); ESIM+GloVe F1=50.3/EM=20.9; ESIM+ELMo F1=54.9/EM=26.4; BERT F1=66.1/EM=39.6. Human performance is reported as "~20 points ahead of the best model" in prose (exact F1/EM ceiling number not found in this cycle's scan -- needs a primary-source pull). The headroom is real (always-yes/always-no near-random, BERT well short of human) but the REASON content fails on 4 of 5 subcategories (duration, frequency, typical-time, stationarity) is that they ask for MAGNITUDE/durational world knowledge ("how long does X take"), not for order/causal reasoning a bag-of-words or a causal-chain mechanism would plausibly get right OR wrong in a mechanism-attributable way -- a system without a duration KB would fail for the RIGHT non-mechanism reason on those four categories, muddying any scramble-collapse control (there is no "duration edge" to scramble if we never built one). |
| **4. Glass-box feasibility** | MEDIUM-LOW, category-dependent. The "event ordering" subcategory (~1/5 of 13k, ~2.6k tuples) is a clean reuse of the same adjacency/precedence mechanism as TORQUE/MCScript2.0-temporal. The other four subcategories (duration, frequency, typical-time, stationarity) would need a NEW knowledge source (a magnitude/duration commonsense KB) that does not exist in the substrate today -- CSKG's 1.24M edges are causal-relation edges (ConceptNet/ATOMIC/etc-style), not durational-magnitude facts, so the "SOLVED store" the E4 design leans on does not transfer to 80% of this benchmark. |
| **5. Fit with validated machinery** | WEAKEST. Only the ordering slice maps onto an owned, validated mechanism. The rest would be a NEW capability-build (duration KB acquisition), not a demonstration of what is already HARD_PASS-certified -- this is a different kind of project (build a new organ) disguised as a benchmark pick, which is the wrong sequencing per the standing "select by brain-foundational-right, not by cheap" discipline: MC-TACO's easy scorer format is cheap, but most of its content-ceiling story routes to a component we have not built. |

### 1d. Alternatives considered (per prompt instruction to name a better-fit candidate if found)

- **ROPES** (Lin, Tafjord, Clark, Gardner 2019, AI2): 14k QA pairs (10k train / 1.6k dev / 1.7k hidden
  test) over 1.7k background+situation passage pairs. Format: given a BACKGROUND passage stating a
  general causal relation (e.g., "more pollinators increases fertilization efficiency") plus a NOVEL
  SITUATION instantiating it, answer a question by applying the background relation to the situation
  -- typically a 2-way pick between named entities/values drawn from the situation. Baselines reported
  as near-random (same order-of-magnitude headroom as WIQA/TORQUE). Good secondary fit for the causal
  organ (relation application rather than chain propagation), smaller (14k vs WIQA's 39.7k), and its
  two-passage structure (BACKGROUND + SITUATION) is an extra layer of indirection our extraction
  pipeline has not exercised. Worth a follow-on look; not ranked above WIQA because it is smaller and
  the general-relation-to-new-situation transfer is a different (harder, less-tested) capability than
  straight multi-hop chain propagation.
- **QuaRTz** (Tafjord et al. 2019, AI2): smaller qualitative-relationship dataset (order of ~3.9k
  questions from memory of the family -- NOT independently verified this cycle, would need a pull),
  single-hop qualitative relation + situation -> 2-way answer. Essentially a simpler, single-hop cousin
  of WIQA. Could serve as a cheap WARM-UP/smoke-test for the polarity-extraction mechanism before the
  full multi-hop WIQA build, but does not exercise the VALIDATE-arrests-multiplicative-error advantage
  (that specifically requires multi-hop chains) -- not recommended as the flagship, plausible as a
  1-day smoke precursor.
- **aNLI/ART** (abductive commonsense, named in the E4 note for the "advance/recombination" step): not
  rescored here -- it targets a different loop stage (ADVANCE, not RETRIEVE/VALIDATE) and the E4 note
  already correctly scoped it as a later-stage target, not a flagship-comprehension benchmark in this
  round.

---

## 2. Ranked recommendation

**1. WIQA (recommended flagship).** Reasoning, stated plainly: it is the only candidate whose task
shape is a near-literal match for the SPECIFIC mechanism we have HARD_PASS-certified (Stage-2A
retrieve-VALIDATE-advance multi-hop causal chaining, where VALIDATE demonstrably arrests multiplicative
error) -- and that organ has never been properly exercised, because MCScript2.0 gave it almost no
target (0.7% causal). The needed extension (a polarity bit on `CausalLinkRegister`'s existing CAUSE/
EFFECT role pair) is small, additive, and consistent with how that class already generalizes (it is
already the third instantiation of the same accumulate-register pattern after the base
`AccumulateRegister` and `RelationRegister`). Data is available now, sized well, and the SOTA/human gap
is large. The one honest gap -- no published lexical/content baseline to anchor the ceiling claim -- is
cheap to close ourselves (Section 4, first arm) and is the correct first empirical step regardless of
which benchmark is chosen.

I VETTED my own prior (stated in the dispatch prompt) rather than assuming it: the prior holds up. The
main thing that could have overturned it -- WIQA not being glass-box-feasible, or not actually being
content-ceilinged -- did not materialize in this scan; instead the scan surfaced a MORE PRECISE version
of the content-ceiling risk (polarity-echo, not BoW-overlap) that sharpens rather than undermines the
pick, and confirmed the mechanism fit is closer than a generic "causal benchmark" label would suggest
(WIQA's influence-graph, sign-propagating structure is essentially isomorphic to
`CausalLinkRegister.query_effect_of` chained with a sign multiply).

**2. TORQUE (strong second / near-term follow-on).** The structurally cleanest content ceiling of the
three (candidates are literally passage tokens, so lexical overlap is vacuous by construction) makes it
an excellent benchmark to hold in reserve, particularly if WIQA's polarity-echo baseline turns out to be
uncomfortably strong (a real risk worth pre-empting). The cost is real new scorer engineering (set-
valued F1/EM, not best-of-N) and an unproven extension from adjacency-retrieval to full pairwise
temporal-relation judgment. Recommend as the SECOND benchmark to scope in detail once WIQA's first
experiment lands (whichever way it lands).

**3. MC-TACO (not recommended as flagship).** Simplest scorer shape but the content-ceiling story is
entangled with a capability we do not have (duration/magnitude world knowledge) for 4 of 5 subcategories.
Revisit only if a dedicated durational-KB build is independently justified; do not adopt MC-TACO as a
way to avoid building that KB, because doing so would mean claiming a content-ceiling win on categories
our mechanism cannot actually reach.

---

## 3. Fit map: benchmark question form -> loop step

| Benchmark | Question form | Loop step exercised | Owned organ |
|---|---|---|---|
| WIQA | "if perturbation P (signed), what happens to outcome O?" | RETRIEVE anchor steps for P and O via pull-in; VALIDATE by propagating signed CAUSE/EFFECT edges hop-by-hop along the retrieved path | `CausalLinkRegister` (+ polarity extension) + `cleanup_family.iterative_attractor`/pull-in + `extract_events`/`mcscript_extraction` |
| TORQUE | "which pre-tagged events precede/follow/overlap event E?" | RETRIEVE E's position in the accumulated sequence; VALIDATE each candidate event's relation to E (adjacency today, needs pairwise-relation extension) | `situation_model_accumulate` accumulated sequence + `cleanup_family` retrieval; NEW: pairwise Allen-relation judgment |
| MC-TACO (ordering slice only) | "did event A happen before/after event B?" | Same adjacency mechanism as TORQUE, single-pair, no set-valued scoring needed | `situation_model_accumulate` adjacency (ordering slice only; other 4 slices need an unbuilt duration KB) |

---

## 4. First-experiment design for the top pick (WIQA)

**Name (proposed anchor):** `exp_wiqa_causal_chain_loop_v1`.

**Precondition (verify before build, cheap, ~1 hour):** pull `allenai/wiqa` (Hugging Face `datasets`
or the AI2 direct release), confirm dev-split size/format matches the 6,894 figure found this cycle,
and confirm the influence graph is NOT given as solver input at inference time (only used to generate
the QA pairs) -- this last point was inferred from how the paper frames the task ("systems must read the
paragraph and reason about the chain of effects") but was not independently confirmed from the raw data
schema this cycle; if the graph IS exposed as input, the task is far easier than assumed and the whole
scorecard needs re-grading before building anything further.

**Claim under test:** a glass-box causal-chain-propagation system, built by extending
`CausalLinkRegister` with a signed polarity bit and reusing owned event-extraction/retrieval organs,
beats BOTH the majority-class baseline AND a polarity-echo lexical-shortcut baseline on WIQA dev, with
an edge-scramble ablation collapsing the gain, and with the advantage concentrated on multi-hop
questions (where naive polarity-echo should fail and VALIDATE's arrest-multiplicative-error property
should show up most clearly).

**Arms:**
- **MAJORITY** (real baseline, recompute on our own dev pull; expect near 30.66% per the paper).
- **POLARITY-ECHO** (the WIQA-analog of BoW/content-matching, and the REAL baseline to beat): predict
  the polarity word literally stated in the perturbation clause (predict "more" if the perturbation
  says "more X" / "less" if it says "less X"), predict "no_effect" if the outcome entity/step is not
  mentioned in the paragraph at all. Zero causal reasoning, pure surface echo.
- **BoW-OVERLAP** (secondary, weaker-expected arm, included for completeness/comparability with the
  MCScript2.0 arc's baseline family): simple lexical-overlap-derived classifier between
  perturbation+outcome text and paragraph text.
- **CAUSAL-CHAIN-LOOP** (our system): per-step event extraction -> signed CAUSE/EFFECT edges between
  connective-linked/adjacent steps -> anchor both perturbation and outcome via pull-in -> propagate the
  perturbation's stated sign along the retrieved path, VALIDATING each hop -> answer more/less if a
  validated signed path is found, no_effect if no path is found or the anchor cannot be located (abstain
  -> fall back to best baseline, same anti-regression guarantee pattern as E4).
- **ABLATION-1 (scramble the extracted causal edges)** before propagation -- gain must collapse.
- **ABLATION-2 (no-validate)** -- accept the first retrieved path without hop-consistency checking, to
  replicate (not just assume) Stage-2A's already-certified VALIDATE-matters finding on this new corpus.

**Pre-registered bands (>=3 seeds, report per-seed):**
- **HARD-PASS (all four must hold):**
  1. LOOP - max(MAJORITY, POLARITY-ECHO, BoW-OVERLAP) >= **+0.05** absolute (median over seeds).
  2. Scramble collapse: LOOP - ABLATION-1 >= **+0.05** AND ABLATION-1 <= best-baseline + 0.02.
  3. Validate-matters: ABLATION-2 < LOOP (replicates Stage-2A on real WIQA prose, not assumed).
  4. Multi-hop-specific advantage: on the subset of questions whose gold influence-graph path length is
     >=2 hops (derivable from the released graph annotations even though the SOLVER never sees the
     graph -- this is an evaluation-only oracle label, same pattern as MCScript2.0's question-type
     subsetting), LOOP - POLARITY-ECHO >= **+0.08** (this is the mechanism-distinctive claim: single-hop
     questions are exactly where polarity-echo does fine, so the multi-hop subset isolates the loop's
     actual advantage).
- **HARD-FAIL:** no lift over the best baseline OR scramble does not collapse (gain survives scrambling
  -> it was extraction/content, not the chain) OR the multi-hop subset shows NO differential advantage
  over the aggregate (meaning the mechanism is not doing genuine chain work, matching content by luck).
- **MIDDLE_BAND:** partial lift (+0.02 to +0.05 aggregate) with partial scramble-collapse -> mechanism
  contributes but is not yet clean; narrow the flagship claim to the multi-hop subset specifically
  (same designed-exit pattern E4 used for MCScript2.0's temporal subset) rather than re-running a third
  full-aggregate push.

**Why this is fair and can-fail:** majority-class is a real, already-published baseline; polarity-echo
is a real, cheap, likely-competitive surface shortcut that the mechanism must beat, not a strawman;
the multi-hop-vs-single-hop split is computed from evaluation-only oracle metadata (the released
influence graph), never fed to the solver, so it cannot leak; the scramble and no-validate ablations
force the gain to be attributable to the causal-chain mechanism specifically, replicating (not
assuming) the E4/Stage-2A pattern on a new corpus. Cheap: reuses `extract_events`,
`mcscript_extraction.extract_args`, `cleanup_family.iterative_attractor`, and `CausalLinkRegister`
(one small polarity extension); no GPU; short paragraphs (379 process texts).

---

## Cheap decisive test

Does the WIQA-adapted causal-chain-loop (signed `CausalLinkRegister` propagation over pull-in-retrieved
process steps, VALIDATE at each hop) beat both the majority-class baseline (30.66%) and a polarity-echo
lexical-shortcut baseline on WIQA dev (6,894 questions) by >=0.05 absolute, with an edge-scramble
ablation collapsing the gain to baseline level AND the advantage concentrated on multi-hop
(oracle-labeled, evaluation-only) questions where naive polarity-echo cannot work? Cheap (reuses owned
organs, no GPU, short paragraphs), can-fail (two real baselines, one of them a genuine surface-shortcut
risk not previously considered), one-lever (the chain mechanism, isolated by scramble/no-validate
controls and the multi-hop-subset split), glass-box (every propagated sign traces back through the
retrieved path).

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **HARD-PASS:** LOOP beats best-of-{majority, polarity-echo, BoW-overlap} by >=+0.05 (>=3 seeds) AND
  scramble collapses (LOOP - ABLATION-1 >= +0.05, ABLATION-1 <= best-baseline+0.02) AND
  ABLATION-2 < LOOP (validate replicates) AND multi-hop-subset lift over polarity-echo >= +0.08.
  Predicted P ~ 0.32 (deflated; open risks: no published lexical-baseline anchor, unbuilt polarity
  extension, and whether polarity-echo turns out unexpectedly strong on real WIQA prose).
- **HARD-FAIL:** no lift over the best baseline OR scramble does not collapse OR the multi-hop subset
  shows no differential advantage. Any of these falsifies WIQA as the flagship mechanism demonstration
  and triggers a fall-back look at TORQUE (Section 1b) or ROPES (Section 1d).
- **MIDDLE_BAND (pre-committed exit):** partial aggregate lift, partial collapse -> narrow the flagship
  claim to the multi-hop subset specifically (mirrors E4's temporal-subset exit on MCScript2.0), keep
  the polarity extension (it is small and reusable regardless).
- **Independent, benchmark-selection prediction (not gated on the WIQA experiment):** MC-TACO's
  non-ordering categories (80% of the dataset) will NOT be reachable by the current organ set without a
  new durational-knowledge acquisition project. Predicted with high confidence (P ~ 0.75) from the
  category analysis in Section 1c; this is a scoping conclusion, not a mechanism claim, so it is not
  subject to the same deflation.

## Cross-thread synthesis

- Directly vets and extends `notes/research_e4_inference_augmented_comprehension_design_2026-08-10.md`
  Section 1d, which named these three candidates plus ROPES/QuaRTz/aNLI-ART but did not score them --
  this drill supplies the scorecard, confirms the E4 note's directional recommendation (WIQA for
  causal, TORQUE/MCTACO for temporal) holds up under a real literature pull, and SHARPENS the WIQA
  content-ceiling risk from a generic "is it content-ceilinged" question into the specific,
  testable polarity-echo shortcut the E4-style scramble/ablation design must now guard against.
- Reuses the SAME experiment-design grammar E4 established for MCScript2.0 (real baseline + surface-
  shortcut baseline + scramble ablation + no-validate ablation + a mechanism-distinctive subset split)
  rather than inventing a new design pattern -- continuity with the augment-not-replace architecture
  the gate-test already validated (no-regression via abstain-on-no-path is the same anti-regression
  guarantee, restated for WIQA's 3-way label space instead of MCScript2.0's 2-way MC).
- Extends the barrier-map's organ inventory: confirms `CausalLinkRegister` (barrier-map B8, "owned,
  HARD_PASS toy") is reusable with a small polarity extension rather than needing a new organ, keeping
  the wire-don't-island discipline intact (this drill does not recommend building anything not already
  a small extension of a registered/certifiable class).
- Corrects a potential mis-scoping in the E4 note's brief benchmark list: TORQUE's task format (set-
  valued span selection, event triggers pre-tagged) is meaningfully different in scorer shape from
  WIQA's and MC-TACO's classification format -- the E4 note grouped all three as "temporal/causal
  benchmarks" without flagging this scorer-shape divergence; this drill makes it explicit so exp_dev
  does not assume a shared harness across all three.

## Substrate-product implications

The defensible product claim, if the WIQA experiment lands, is sharper than the MCScript2.0 story: a
glass-box system that reads a process paragraph, builds an auditable signed causal-chain representation
of it (no LLM), and answers "what happens if X changes" questions with a trace showing exactly which
steps were pulled in and how the sign propagated -- on a benchmark where the alternative (an opaque
neural net) cannot show its work at all, and where the naive shortcut (echo the perturbation's stated
direction) is a NAMED, TESTED failure mode we explicitly out-perform rather than an assumption we wave
away. This is a stronger differentiation story than MCScript2.0's "never regress below BoW" framing,
because WIQA's headroom (43 points above majority, 22.5 above SOTA) is large enough that a genuine,
traced multi-hop win is a headline result, not a thin residual. Do not market or measure on MC-TACO's
non-ordering categories without first building (and disclosing) a durational-knowledge source; doing
otherwise would silently claim credit for reasoning the substrate cannot yet perform.

## Honest deflated grade + data-access blockers

**Deflated grade: MEDIUM on the WIQA pick, MEDIUM-LOW on the first-experiment win.**

- The RANKING (WIQA > TORQUE > MC-TACO) is HIGH confidence (~0.60, benchmark-fit judgment, lower risk
  class than a mechanism claim) -- it survives the "don't dismiss adjacent methods" discipline (all
  three were scored on all 5 axes, not pre-judged) and TORQUE in particular was taken seriously as the
  structurally-cleanest ceiling story before being ranked second on engineering-cost grounds, not
  dismissed.
- The WIQA first-experiment HARD-PASS is P ~ 0.32 (deflated per calibration; novel-synthesis cap 0.50).
  Deflators: no published lexical/content baseline to anchor the ceiling claim (must be measured fresh);
  the polarity extension to `CausalLinkRegister` and the paragraph-to-chain extraction are new
  engineering, not yet built or smoke-tested; whether WIQA's real prose yields clean signed edges at the
  rate MCScript2.0's causal (0.7%) scarcity would predict is unknown until tried.
- **Data-access blockers for the USER to clear: none identified that require USER action.** All three
  datasets are public with no paywall or login found in this scan (Hugging Face for WIQA and MC-TACO,
  GitHub for TORQUE). The one open item is MECHANICAL, not a blocker: none of the three were actually
  downloaded and parsed to disk this cycle (facts here are literature-sourced, not disk-verified) --
  the correct next step is exp_dev's first action (pull WIQA dev, confirm schema/counts, confirm the
  influence graph is not solver-visible) before any code is written, exactly the precondition already
  stated in Section 4.

## Citations (verified count)

Four generic-term web scans this cycle (public dataset names used directly, consistent with the E4
note's own precedent that public benchmark names are not substrate-novel terms under the query-privacy
rule): (1) WIQA -- Tandon, Dalvi, Niket et al. 2019, EMNLP-IJCNLP D19-1629 / arXiv:1909.04739; size
39,705 (29,808/6,894/3,003), majority baseline 30.66%, SOTA 73.8%, human 96.3%, `allenai/wiqa` on
Hugging Face -- verified via ACL Anthology, arXiv abstract, Hugging Face dataset card, and a follow-up
scan for the majority-baseline breakdown. Per-category no-effect majority figure (0.55%) surfaced in
one scan snippet but not independently cross-checked -- flagged, not load-bearing to this drill's
conclusions. (2) TORQUE -- Ning, Wu, Han, Peng, Roth 2020, EMNLP 2020.emnlp-main.88 / arXiv:2005.00242;
3.2k passages, RoBERTa-large 51% EM, human 84.5% EM / 95.3 F1 (measured by one author against crowd
annotations on 100 test items, per Table 4 of the paper as summarized in-scan) -- verified via ACL
Anthology + a dedicated human-performance scan; the exact question-count (21k vs 30.4k across two
scan summaries) is UNRESOLVED and flagged for direct verification, not treated as settled. (3) MC-TACO
-- Zhou, Khashabi, Ning, Roth 2019, EMNLP D19-1332 / arXiv:1909.03065; 13k tuples, 5 subcategories,
baseline table (Random F1=36.2/EM=8.1, Always-Positive F1=49.8/EM=12.1, Always-Negative F1=17.4/EM
value UNVERIFIED possible-duplicate artifact, ESIM+GloVe F1=50.3/EM=20.9, ESIM+ELMo F1=54.9/EM=26.4,
BERT F1=66.1/EM=39.6), human performance "~20 points ahead of best model" (exact ceiling number not
found this cycle, flagged) -- verified via ACL Anthology, GitHub `CogComp/MCTACO`, Hugging Face
`CogComp/mc_taco`. (4) ROPES/QuaRTz -- Lin, Tafjord, Clark, Gardner 2019 (ROPES), arXiv:1908.05852,
AllenAI data page; 14k QA pairs (10k/1.6k/1.7k), near-random baselines confirmed via ACL Anthology
D19-5808 and the AllenAI ROPES data page; QuaRTz facts NOT independently re-verified this cycle (carried
from general knowledge of the AI2 qualitative-reasoning dataset family, flagged as such in Section 1d,
not asserted as a verified number).

Carried (not re-derived) from the E4 note's own verified base, credited there: Stage-2A HARD_PASS
result (VALIDATE arrests multiplicative error, 013f1481e); `CausalLinkRegister` class definition and
docstring (`hdlab/situation_model_accumulate.py` lines 161-234, read directly this cycle); the E4 note's
own benchmark-naming (Section 1d) and its P~0.80 prediction that the causal loop's win must be shown on
WIQA rather than MCScript2.0. No citation fabricated or re-asserted from memory without a live scan this
cycle; every number in the scorecard tables traces to a specific search result quoted or paraphrased
above, and every unresolved/unverified figure is explicitly flagged as such rather than presented as
settled.
