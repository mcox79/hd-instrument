# Research: E4 -- Inference-Augmented Comprehension Design (AUGMENT not replace) (2026-08-10)

Filed by: research (Opus, USER-authorized program-pivotal strategic synthesis). Foreground, no nested
sub-agents, no background waits. This drill designs the next comprehension attack AND -- gating
everything -- makes the honest call on whether MCScript2.0 is even the right benchmark to demonstrate
inference, after TWO arcs (scenario-discrimination + MCQA) in which static/structured approaches failed
to beat bag-of-words content matching.

KB-CHECK DONE FIRST (mandatory dedup): `substrate_query.sh` on the exact E4 prompt (top hits were the
existing situation-model / relation-inference design notes and the 07-14 cold-start decisions log --
confirmed this is a new synthesis, not a rediscovery, and it EXTENDS rather than re-derives). Read in
full this cycle, disk-verified, credited throughout:
- `notes/research_comprehension_barrier_map_brain_foundational_2026-08-10.md` (the 11-barrier map; the
  binding constraint = prose->structured-encode; store closure)
- `notes/research_e3_realprose_extraction_feasibility_scope_2026-08-10.md` (the three sub-breaks:
  situation_reader-needs-gold-CoNLL, present-tense 67% zero-recall, ungrounded symbol layer worse-than-
  BoW; the E3 grounded-symbol gate)
- `data/exp_mcscript2_mcqa_droptense_properscramble_v1/metrics.json` (the HARD_FAIL cell: BoW 0.629,
  structured 0.401 BELOW CHANCE, scramble 0.476; examples.structure_helps=112, structure_hurts=359;
  extract_diag n_cand_zero=1591/4040; n_ties=404) -- read cell-level this cycle, numbers below are
  off-disk, not from the verdict string
- `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` TOP block (night arc + store closure at 1.2M)
- The prior MCScript2.0 arc (`hdlab/mcscript_extraction.py`, `preregs/2026-08-09_mcscript2_real_
  benchmark_validation_v1.md`) that capped content-matching ~0.61 and found chain_predict a practical null
- Fresh corpus scan this cycle: `data/corpora/mcscript2/extracted/{dev,test,train}-data.xml`, 19,821
  real questions, question-type distribution measured live (Section 1)
- Two targeted modern web scans (MCScript2.0 benchmark facts; dual-route reading neural evidence 2018-2025)

---

## HEADLINE

**The right move is to STOP competing structure-against-content and COMPOSE them: keep BoW as the
always-on fast route, and let a glass-box retrieve-validate-advance loop speak ONLY on the questions BoW
provably cannot answer, ABSTAINING (never voting below chance) everywhere else. That reframe is forced by
the data -- the current static structured scorer is not merely weaker than BoW, it is ANTI-INFORMATIVE on
the very residual it was meant to win: on the 402 questions BoW gets wrong, structure recovers only 112
(27.9%), FAR below the 50% a coin flip would get, because 39% of answer-candidates extract to zero events
and 404/1084 questions are structural ties, so a below-chance guess gets forced onto questions structure
cannot actually read.** The augment design fixes this by construction (abstain-on-empty + a confidence
gate that keeps BoW where the loop is silent), which mathematically cannot regress below BoW on the full
set.

**On the benchmark question the honest verdict is SPLIT, and it is load-bearing.** MCScript2.0 is
BoW-FAVORABLE in AGGREGATE -- it is content-saturable, which is exactly why two content-matching arcs
plateaued near 0.61-0.63 -- so chasing aggregate accuracy is the wrong game. BUT it is NOT uniformly
BoW-favorable: a fresh scan shows **32.7% of all 19,821 questions are TEMPORAL ("when" 27.9% + order-words
5.7%)**, a large, clean, brain-motivated subset where BoW's order-invariance is a PROVABLE ceiling (a
bag of words cannot represent "hail THEN get-in" vs "get-in THEN hail"). That is the right in-corpus
target for the TEMPORAL inference loop. The mirror-image finding is the sharpest benchmark limitation:
**causal-"why" questions are only 0.7% (135/19,821)** -- so the substrate's single strongest validated
inference mechanism (the Stage-2A retrieve-VALIDATE loop, whose HARD_PASS is a CAUSAL-chaining result)
has almost NO direct target on MCScript2.0 and is mistargeted here. The causal loop's demonstration home
is a causal benchmark (WIQA), not MCScript2.0.

**Recommendation (non-forced, honest):** build the augment machinery (it is needed regardless of
benchmark and it fixes the catastrophe), gate-test it CHEAPLY on the MCScript2.0 temporal ("when")
subset -- but SELECT the flagship inference demonstration on purpose-built order/causal benchmarks
(TORQUE / MCTACO for temporal, WIQA for causal) where BoW's order-invariance and causal-blindness are
HARD ceilings, not a thin swamped residual. If E4 does not clear +0.05 on the MCScript2.0 temporal
subset, do NOT keep pushing MCScript2.0 -- pivot the flagship, which the pre-registered MIDDLE_BAND
routes to automatically.

P_deflated = **0.30** for "the inference-augmented loop HARD-PASSes E4 (beats BoW by >=0.05 on the
MCScript2.0 temporal subset with a scramble-collapse control)" -- deflated hard (novel-synthesis cap 0.50,
minus: two content-matching arcs already capped, the current structured scorer is BELOW coin-flip on the
residual, and a HARD-PASS requires a long conjunction of not-yet-built E3 fixes all landing). The REFRAME
itself (augment-not-replace fixes the regression and is the right architecture) is much higher confidence,
**~0.72**, because the abstain+gate guarantee is near-tautological and the two-route shape is strongly
brain-supported (Section 5).

---

## 1. HONEST BENCHMARK ASSESSMENT (this gates everything)

**Is MCScript2.0 the right benchmark to demonstrate INFERENCE's value? Answer: NO in aggregate, YES for
temporal on a defined subset, NO for causal.** Evidence, off-disk and freshly measured:

### 1a. The content residual (0.63 -> ~0.72 -> 0.97) is mostly NOT inference-attributable for a glass-box system

- MCScript2.0 is 2-way MCQA (chance = 0.50). Off-disk: BoW = **0.629** (682/1084 scorable), i.e. +0.129
  over chance. The current structured scorer = **0.401** (BELOW chance) and scramble = 0.476.
- The dataset was DESIGNED with ~half the questions requiring commonsense/script knowledge not in the
  text (Ostermann et al. 2019, verified via web scan). So there IS an inference-requiring population by
  construction. BUT -- and this is the honest crux -- BoW still scores **0.594 on the commonsense split**
  (535 Qs) and 0.685 on the text split (435 Qs). The commonsense questions are harder for BoW (a real
  0.09 inference signal) but BoW is still well above chance on them, because MCScript2.0's crowd-authored
  answer candidates make the correct answer more script-plausible-VOCABULARY-overlapping with the
  scenario than the distractor. Answer-plausibility ranking (content matching over a script prior)
  captures most of the "script knowledge" signal WITHOUT explicit inference.
- The much-cited "SOTA ~0.72 / human ~0.97" gap is real but MISLEADING for THIS program: web scan
  confirms MCScript2.0 is "not challenging to humans" (human near-ceiling) and that opaque PLM systems
  (TriAN and BERT-era successors) close a large fraction of the 0.63->0.97 gap with contextual
  representations -- which are exactly the black-box mechanisms the substrate charter forbids at
  inference. The glass-box-RELEVANT headroom above BoW is therefore NOT the full 0.34; it is the
  inference-attributable slice, which the below-coin-flip structure result shows is currently unrealized.

### 1b. The genuinely-BoW-PROVABLY-CANNOT residual is order-dependent temporal, and it is NOT thin

Fresh scan of all 19,821 MCScript2.0 questions (`{dev,test,train}-data.xml`, this cycle):

| Question opener | Count | Share | BoW-provable ceiling? |
|---|---|---|---|
| what | 7,590 | 38.3% | no (content-answerable) |
| **when (temporal)** | **5,538** | **27.9%** | **YES -- order-invariant BoW cannot represent sequence** |
| where | 2,040 | 10.3% | no (content) |
| who | 1,532 | 7.7% | mostly no (content/coref) |
| **order-words (after/before/next/first/last/then)** | **1,124** | **5.7%** | **YES -- explicit ordering** |
| how | 855 | 4.3% | partial |
| **why (causal)** | **135** | **0.7%** | YES but NEAR-ABSENT |

- **TEMPORAL union = 32.7%.** This is the load-bearing positive: a bag of words is order-invariant, so
  for any "when did X happen" question whose two answers are both content-plausible and differ only in
  RELATIVE ORDER of events present in the passage, BoW has a PROVABLE ceiling and can only win by
  content-correlation luck. This subset is a THIRD of the benchmark -- not thin. It aligns with the
  observed helps set (the 5 structure_helps examples on disk are temporal-dominated: "When did they put
  the letter into the envelope", "When did they get in the taxi", "When did they rinse the dishes").
- **CAUSAL-why = 0.7% (135 questions total across the whole corpus).** The substrate's strongest
  validated inference organ is the Stage-2A retrieve-VALIDATE-advance loop, whose HARD_PASS is a
  multi-hop CAUSAL result (VALIDATE arrests multiplicative error). MCScript2.0 gives that organ almost
  no direct target. Pointing the causal loop at MCScript2.0 is a benchmark-mechanism MISMATCH.
- Provable-core sizing: the truly-BoW-impossible core (temporal questions where both answers are
  content-tied and only order decides) is a fraction of the 32.7%, roughly the observed
  helps-rate 112/1084 = **10.3%** of scorable questions. So: the inference-requiring residual BoW
  provably cannot do is ~10-16% of the benchmark, concentrated in temporal ordering, with a <1% causal
  sliver.

### 1c. Why "helps" cannot be trusted as evidence yet (the honest deflator)

`structure_helps` = 112, `structure_hurts` = 359. On the 402 questions BoW gets wrong, structure recovers
only 112 = **27.9%**, versus the ~50% a coin flip achieves on a 2-way question. So the current structured
approach is BELOW a coin flip even on BoW's failures -- the 112 "helps" are heavily contaminated by the
404 ties (random tie-break alone would produce ~200 apparent helps). **The 112 helps are NOT evidence
that inference is doing work; they are consistent with worse-than-random guessing plus luck.** Any E4
claim of an inference win must therefore come with a scramble-collapse control (Section 4), because the
raw helps count is uninformative.

### 1d. Benchmark verdict

- **Aggregate MCScript2.0: WRONG target.** Content-saturable; inference swamped to ~10-16%; two arcs
  already plateaued here for exactly this reason. Do not chase aggregate accuracy.
- **MCScript2.0 temporal ("when"/order) subset: RIGHT in-corpus gate.** Large (32.7%), clean, BoW has a
  provable ceiling, cheap to isolate with a glass-box question-type rule. Use as the E4 gate.
- **MCScript2.0 for causal: WRONG.** 0.7% causal questions. The causal loop must be demonstrated on WIQA.
- **Better flagship benchmarks to NAME (modern, glass-box-testable, BoW-provably-limited):**
  - TEMPORAL: **TORQUE** (temporal-ordering reading comprehension, Ning et al. 2020) and **MCTACO**
    (multiple-choice temporal commonsense, Zhou et al. 2019) -- ordering/duration are the target, BoW's
    order-invariance is a hard ceiling.
  - CAUSAL / procedural: **WIQA** (what-if QA over process paragraphs with a causal graph, Tandon et al.
    2019) -- questions are "if X does not happen, effect on Y?", almost isomorphic to
    `CausalLinkRegister.query_effect_of`; and **ROPES** / **QuaRTz** (qualitative causal relation reasoning).
  - ABDUCTIVE narrative: **aNLI / ART** (abductive commonsense between two observations) for the
    advance/recombination step.
  The two-track recommendation: keep MCScript2.0-temporal as the CHEAP in-corpus gate (reuses everything),
  but SELECT the flagship on TORQUE+MCTACO (temporal) and WIQA (causal), where the win is not swamped.

---

## 2. THE INFERENCE-AUGMENTED DESIGN (AUGMENT, do not replace)

**Core principle: two brain-faithful routes with a monitoring gate.** A fast content/gist route (always
on) plus a slow inferential-elaboration route (invoked only on the residual), composed so the slow route
can only ADD signal where it has provable advantage and ABSTAINS otherwise. This is the structural fix for
the -0.228 catastrophe: the disaster came from letting structure vote on questions it cannot read.

### 2a. Route 1 -- fast content/gist (ATL-analog, always on)

BoW word-overlap score between each answer candidate span and the passage(+scenario), producing per-
candidate scores and a **confidence = margin between the top-2 candidate scores**. This is the owned
`grounding_acquisition_loop.context_vector` bag-of-content-words bundle (Stage-1c baseline, already
measured; gap 0.153 on discrimination). No change -- it is the base, and the base is respected.

### 2b. The GATE / router (comprehension-monitoring analog)

Decide per question whether to invoke Route 2, from three glass-box signals:
1. **Question type** (rule classifier over wh-word + main verb via owned `pos_tagger`/`arc_parser`):
   is it TEMPORAL (when/after/before/next/first/last) or CAUSAL (why/because) or WHAT-NEXT? Only these
   route to the loop; content-type questions (what/where/who as pure lookup) keep BoW.
2. **BoW confidence**: if BoW margin > tau_conf, ACCEPT BoW (fast route sufficient -- good-enough
   processing). Only low-margin / tie questions escalate. This is the monitoring-on-conflict escalation.
3. **Extractability**: if the answer candidate extracts to ZERO events (the 39% problem), Route 2 CANNOT
   build a structured judgment for it and MUST abstain for that candidate.
Combined rule: invoke Route 2 only when (type in {temporal,causal,what-next}) AND (BoW margin <= tau_conf)
AND (both candidates extract >=1 event). Otherwise keep BoW. This gate is the anti-regression guarantee.

### 2c. Route 2 -- slow retrieve-VALIDATE-advance loop (hippocampal-prefrontal analog, selective)

Turn (passage, question, answer_i) into a query and validate against the passage situation model + store:

1. **Build the passage situation model ONCE per passage** (not per candidate): per-clause events
   {PRED, AGENT, PATIENT, TENSE} via `extract_events` (E3 tense-fix for VBP/VBZ) ->
   `mcscript_extraction.extract_args` positional AGENT/PATIENT -> AGENT/PATIENT coreference-canonicalized
   via `coreference_resolver` + the raw-text mention adapter (E3 Section 3iii) -> grounded symbol vectors
   from `lexical_similarity`/`concept_encoder` wired into `event_bundle._sym_vec` (E3 fix) -> accumulate
   into `situation_focus.ChunkedFocus` (Cowan-4) + `situation_model_accumulate.CausalLinkRegister`
   (temporal-adjacency edges + explicit connectives + CSKG-plausible cause among adjacent pairs).
2. **QUERY from the QUESTION (not the answer)** -- this defeats the shared-stem anchoring bug: parse the
   question to (a) its ANCHOR event (the main verb/object of the "when did X" / "why did X"), and (b) its
   query TYPE. Extract candidate events from the ANSWER SPAN ALONE, never from question+answer
   concatenation (the concatenation is what made both candidates collapse onto the shared stem in the
   failed cell).
3. **RETRIEVE** the anchor's relevant neighborhood: locate the anchor event in the situation model by
   `pull_in` (`cleanup_family.iterative_attractor` / `k_NN_lookup`, salience-gated, GATE_THRESH fixed
   pre-run) and, for script-gap questions, pull the anchor's plausible world-knowledge events from the
   SOLVED store (`kg_traversal`/KGStore shortlist, in_shortlist 0.85 @1.2M; CSKG 1.24M causal edges) via
   `selection_weighted_sharded_typer` routing. For TEMPORAL: retrieve the anchor's predecessor/successor
   events in the accumulated sequence. For CAUSAL: `CausalLinkRegister.query_cause_of(anchor)` /
   `query_effect_of(anchor)`.
4. **VALIDATE** which answer_i is temporally/causally CONSISTENT: score each answer_i's event by whether
   it is reachable via a validated temporal/causal edge from the anchor's retrieved neighborhood (Stage-2A
   VALIDATE -- the step whose HARD_PASS showed it ARRESTS multiplicative error; NO_VALIDATE degrades).
   The answer whose event matches the retrieved predecessor (for "when ... before"), successor (for
   "when ... after / what next"), or cause (for "why") wins Route 2.
5. **ADVANCE** (what-next only): recombine the successor via `sequence_memory.chain_predict` /
   `binding.bind`+`bundle` recombination -- NOT trained forward-regression (falsified 3x on this substrate).
6. Route 2 emits a per-candidate score + its OWN confidence (validation margin). If Route 2 abstains
   (empty candidate, no anchor located, or validation margin below its floor), it contributes NOTHING and
   the gate keeps BoW.

### 2d. Combine (glass-box, auditable)

**Gated hand-off, not blind fusion:** final answer = BoW's pick, OVERRIDDEN by Route 2 only when the gate
fired AND Route 2 is confident (validation margin > tau_val). Every override carries a trace: "BoW
uncertain (margin 0.01); routed to loop; loop chose B because event 'hail-taxi' is the retrieved
predecessor of anchor 'get-in-taxi' via temporal edge e3->e4." This makes the win auditable and is the
product differentiator. (An additive `BoW + lambda*Route2` fusion is the fallback if the hand-off is too
brittle, but the hand-off is preferred for glass-box provenance and because it isolates the loop's
contribution for the ablation.)

### 2e. Handling the 39%-empty-candidate problem explicitly

1591/4040 candidates extract to zero events -- overwhelmingly SHORT answers ("at the end", "a new
laptop", "paint"). The rule is absolute: **NO EVENT -> NO STRUCTURED VOTE -> keep BoW.** This single rule
removes the dominant source of the below-chance -0.228 result. For short NOMINAL answers that carry a
concept but no verb, a graded fallback is allowed WITHOUT full event structure: ground the answer noun via
`concept_encoder`/`lexical_similarity` and score it by concept-similarity to the retrieved event's
expected role filler (e.g. answer "the fridge" vs the retrieved "putting-away" event's LOCATION slot) --
this uses grounding but abstains from the ordering claim it cannot support. If even that is unavailable,
abstain -> BoW.

### 2f. Owned-organ map (every step)

| Step | Owned organ | Status |
|---|---|---|
| Route 1 BoW gist | `grounding_acquisition_loop.context_vector` | measured |
| Question-type router | rule over `pos_tagger`/`arc_parser` | small new glass-box rule |
| Event extraction | `extract_events` (needs E3 present-tense branch) + `mcscript_extraction.extract_args` | owned, patch needed |
| Grounded symbols | `lexical_similarity.concept_similarity`/`concept_encoder`/`ppmi_sparse_encoder` -> `event_bundle._sym_vec` | owned, WIRE needed (E3) |
| Coref canonicalization | `coreference_resolver` + raw-text mention adapter | owned + adapter needed (E3) |
| Situation model / focus | `situation_focus.ChunkedFocus`, `situation_model_accumulate` | owned; focus pull-in SHELVED (Phase-1 wire) |
| Causal/temporal links | `CausalLinkRegister.query_cause_of/effect_of` | owned, HARD_PASS toy |
| Retrieve / pull-in | `cleanup_family.iterative_attractor`/`k_NN_lookup`/`pull_in_multi_exclude` | owned, HARD_PASS toy |
| Store shortlist | `kg_traversal`/KGStore + `selection_weighted_sharded_typer`; `cskg_foundation` (1.24M) | SOLVED @1.2M (in_shortlist 0.85) |
| Validate | Stage-2A loop | HARD_PASS 5/5 toy |
| Advance | `sequence_memory.chain_predict` / recombination | chain-grade certified |

---

## 3. WHERE INFERENCE DEMONSTRABLY WINS (the subset, with concrete examples)

The loop should beat BoW ONLY on questions where content is provably insufficient. Grounded in the 112
helps cases + Section 1's scan, the win subset is:

- **TEMPORAL ORDER ("when", after/before/next):** BoW is order-invariant; the answer depends on relative
  event order both present in the passage. Concrete on-disk helps case (instance 105, "taking a taxi"):
  Q "When did they get in the taxi?" answers ["When they got to the restaurant.", "After they walked to
  the street and hailed one." (correct)]. BoW picks the first (word "restaurant"/"taxi" both overlap the
  passage) and is WRONG. The loop wins because the situation model orders hail -> get-in -> ride ->
  arrive-at-restaurant, so "get-in" follows "hail", not "arrive". This is BoW-PROVABLY-IMPOSSIBLE. Same
  shape: instance 104 (letter into envelope "right before addressing"), instance 107 (rinse dishes "after
  rubbing soap"). This is the loop's home ground and it is 10-16% of the benchmark.
- **WHAT-NEXT / successor:** "what did they do after X" -- `query_effect_of`/successor retrieval + advance.
- **SCRIPT-GAP "what is implied" (subset of commonsense):** the event is not stated but inferable from the
  script via CSKG (e.g. "the store" implies "paid"); pull-in from the store supplies the missing event.
- **CAUSAL "why":** the loop's strongest mechanism -- but only 0.7% of MCScript2.0, so this win must be
  shown on WIQA, not here.

Honest boundary: the loop should NOT be expected to win on pure content lookup ("what was bought" ->
"paint, couch, TV" vs "a new laptop", a BoW slam-dunk and an on-disk structure_hurts case) -- and the gate
must route those to BoW. The design's value is precisely NOT trying to win everywhere.

---

## 4. E4 CAN-FAIL DESIGN (design only, do not run)

**Name (proposed anchor):** `exp_mcscript2_augmented_temporal_loop_v1`.

**Claim under test:** on the pre-registered inference-requiring (temporal) subset, the augmented
(BoW-base + gated loop) system beats the BoW base, AND ablating the loop collapses the gain (proving the
LOOP does the work, not extra content), AND the gate does not regress the full set below BoW.

**Subset (pre-registered, computed from the QUESTION only, before scoring):** questions whose type-rule
labels TEMPORAL (when / after / before / next / first / last / then). Expected N ~ 300-350 of the 1084
scorable (32.7% of corpus; report exact N and its BoW baseline). Secondary subset: causal/what-next
(small; report separately, do not pool).

**Arms:**
- **BoW** (real baseline) -- accuracy on the subset.
- **BoW + random tie-break** -- baseline for the BoW-tie residual within the subset.
- **AUGMENTED** = BoW-base + gated Route-2 temporal loop (grounded events + tense-fix + coref + abstain-
  on-empty; gated hand-off).
- **ABLATION-1 (scramble retrieved knowledge)** = permute the temporal/causal edges / shuffle the pulled-
  in events before VALIDATE. Loop still "runs" but on scrambled structure.
- **ABLATION-2 (no-validate)** = accept first pull-in candidate, skip the VALIDATE step.
- **ABLATION-3 (content-only augment)** = augment BoW with the pulled-in CSKG neighbor WORDS as extra
  bag-of-words (no order, no structure). Controls "more content" vs "the loop".

**Pre-registered bands (>=3 seeds; report per-seed):**
- **HARD-PASS (all four must hold):**
  1. AUGMENTED - BoW on the temporal subset >= **+0.05** absolute (median over seeds).
  2. Scramble collapse: AUGMENTED - ABLATION-1 >= **+0.05** AND ABLATION-1 <= BoW + 0.01 (scramble ties BoW).
  3. Structure-not-content: AUGMENTED - ABLATION-3 >= **+0.03** (the loop's ordering, not extra words, is
     load-bearing) AND ABLATION-2 < AUGMENTED (validate contributes, per Stage-2A).
  4. No full-set regression: AUGMENTED_full >= BoW_full - **0.01** (the gate/abstain preserves BoW where
     the loop is silent -- the anti- -0.228 guarantee, and itself a hard requirement).
- **HARD-FAIL:** AUGMENTED - BoW on the subset <= 0 (no lift) OR scramble does NOT collapse
  (ABLATION-1 >= AUGMENTED - 0.02, i.e. any gain survives scrambling -> it was content, not the loop) OR
  full-set regresses (AUGMENTED_full < BoW_full - 0.02, the gate is leaking below-chance votes).
- **MIDDLE_BAND (+0.02 to +0.05 subset lift, partial scramble-collapse):** inference contributes but is
  swamped/thin on MCScript2.0 -> PIVOT the flagship demonstration to TORQUE+MCTACO (temporal) and WIQA
  (causal) per Section 1d; keep the augment machinery (it validated directionally). This band is the
  designed exit from the BoW-favorable-benchmark risk.

**Why this is a fair, can-fail test:** BoW is a real baseline that already wins the aggregate; the subset
is defined from the question alone (no label leakage); the three ablations force the gain to be
attributable to the LOOP's order/causal structure specifically; and the full-set no-regression clause
makes the gate earn its keep. It is cheap (reuses `CandidateGenerator`, `lexical_similarity`,
`EventBundleCodec`, `CausalLinkRegister`, the CSKG store; no GPU; 1084 short narratives) and glass-box
(every override carries a retrieval+validation trace).

**Precondition (ship before E4):** the E3 fixes E4 depends on -- present-tense `extract_events` branch,
grounded `event_bundle` symbol layer, raw-text mention adapter for coref. E4 is the END-TO-END composition
of E3's pieces plus the gate; if E3's grounded-symbol gate HARD-FAILs, E4 is blocked upstream (correct
place to learn it).

---

## 5. BRAIN-FIDELITY (is augment-not-replace how the brain reads?)

**The two-route shape -- fast semantic gist + slow inferential elaboration invoked only on demand -- is
strongly supported, and the gate is itself brain-motivated.** Modern and classic evidence:

- **Two-stage comprehension (fast construct, slow integrate).** Kintsch Construction-Integration: a fast,
  promiscuous, content-driven construction phase over-generates candidates; a slower settling/integration
  phase resolves them. The BoW route = construction/gist; the loop = integration.
- **Good-enough / shallow processing + escalate-on-monitoring.** Ferreira, Bailey & Ferraro (good-enough
  representations); Sanford & Sturt (shallow processing); Christianson misinterpretation studies: readers
  DEFAULT to a fast, shallow gist and engage deeper compositional/inferential processing only when the
  task demands it or a monitoring signal fires. This is exactly the gate: BoW by default, loop on low
  confidence. The escalation trigger (low content margin) maps to comprehension-monitoring / coherence-
  standards (van den Broek) and inconsistency detection (Albrecht & O'Brien) -- deeper processing is
  recruited on conflict.
- **Inference is selective, not always-on.** McKoon & Ratcliff minimalist hypothesis: only BACKWARD
  bridging inferences are automatic; forward/elaborative inferences are effortful and NOT drawn unless
  needed. This directly licenses "invoke the loop only on the residual" rather than running it everywhere.
- **Neural dissociation (fresh 2018-2025 scan).** Fast semantic gist = the ANTERIOR TEMPORAL LOBE
  semantic hub (Lambon-Ralph hub-and-spoke) + ventral lexical-semantic stream (fast N400-indexed access).
  Slow inferential elaboration = HIPPOCAMPAL relational binding/retrieval (constructive episodic
  simulation; narrative relational integration) + lateral/ventromedial PREFRONTAL controlled retrieval and
  model construction. Web scan (npj Science of Learning 2024 expository-text network; Progress in
  Neurobiology 2022 semantic-cognition; Cerebral Cortex 2025 narrative DMN+semantic connectivity)
  confirms: lexical/semantic retrieval engages ATL + hippocampus + vm/vlPFC together, and building the
  situation model plus integrating new-with-prior knowledge specifically recruits lateral PFC on top of
  the semantic representation regions -- and that "memory representations are multifaceted (gist,
  semantics, schema, episodes), each supported by distinct neural substrates." A fast gist substrate and
  a slow relational-inference substrate operating over it is the documented architecture.
- **Fuzzy-trace theory (Reyna & Brainerd):** parallel gist and verbatim traces, gist dominates default
  judgments -- the same fast-gist-plus-precise-elaboration duality.

**Is it the RIGHT shape? YES, with one disclosed fidelity simplification.** The brain's two routes are
INTERACTIVE and continuous -- the gist route pre-activates and constrains the inference route on every
word (cascaded, not a clean serial hand-off) -- whereas the design uses a DISCRETE gate (BoW-confident ->
skip loop). The discrete gate is a defensible engineering approximation of the good-enough-then-escalate
dynamic, and its escalation trigger (low content margin ~ conflict/low-confidence monitoring) is itself
brain-motivated; but it is a simplification, disclosed, not a claim of exact continuous dynamics. The
shape (compose, don't replace; escalate on monitoring) is right; the discretization is the honest caveat.

---

## 6. HONEST DEFLATED GRADE + BoW-FAVORABLE RISK + CONTINGENCY + WIRE-DEBTS

**Deflated grade: MEDIUM-LOW on the win, HIGH on the reframe.**

- The AUGMENT reframe is correct, brain-faithful, and near-tautologically fixes the -0.228 regression
  (abstain-on-empty + gate-keeps-BoW cannot regress the full set below BoW if band-4 holds). Confidence
  ~0.72. This is real progress independent of the benchmark: it is the right architecture for every future
  comprehension benchmark, not just MCScript2.0.
- The WIN on the MCScript2.0 temporal subset is genuinely uncertain: P_deflated ~ **0.30**. Deflators: two
  content-matching arcs already capped; the current structured scorer is BELOW coin-flip on the residual;
  a HARD-PASS needs a LONG conjunction to all land (E3 tense-fix + grounded symbols + coref adapter +
  correct temporal-edge population + the gate calibrating tau_conf/tau_val on real prose). Any weak link
  drops it to MIDDLE_BAND.

**Explicit BoW-favorable risk + contingency (I am NOT forcing the optimistic path).** MCScript2.0 is
content-saturable in aggregate and PARTIALLY so even on the temporal subset (answer-plausibility catches
some ordering by co-occurrence). The honest read is that MCScript2.0 is the wrong FLAGSHIP for inference.
My recommendation is therefore two-track and self-limiting: (1) build the augment machinery (needed
regardless); (2) gate-test on the MCScript2.0 temporal subset because it is cheap and reuses everything,
with the MIDDLE_BAND pre-wired to PIVOT the flagship to TORQUE+MCTACO (temporal) and WIQA (causal) -- the
benchmarks where BoW's order-invariance and causal-blindness are HARD ceilings, not a thin swamped
residual. If E4 does not clear +0.05 on the subset, do NOT run a 3rd MCScript2.0 content push; the design
already routes to the alternative. I would rate "inference-augmentation beats BoW somewhere it should
(temporal subset OR a purpose-built temporal/causal benchmark)" meaningfully higher (~0.45) than "beats
BoW on MCScript2.0 aggregate" (~0.15, effectively closed) -- which is why the recommendation is to define
success on the SUBSET / the RIGHT benchmark, not the aggregate.

**Wire-don't-island debts (carried from barrier map + E3, all block or weaken E4 until paid):**
1. `event_bundle._sym_vec` grounded-symbol wire (E3) -- E4's discrimination depends on it.
2. Raw-text mention-stream adapter for `coreference_resolver` (E3 3iii) -- AGENT/PATIENT canonicalization
   for temporal-edge linking depends on it.
3. `extract_events` present-tense branch (E3 3ii) -- ~19% of sentences, needed to build the situation model.
4. `situation_focus.py` pull-in un-SHELVE (barrier-map Phase 1) -- the loop queries OUT against the focus.
5. Stage-1.5 context-gate promotion + store readout-fix (barrier-map Phase 0/E1) -- the store shortlist
   the pull-in reads.
6. NEW debts introduced by this design: the question-type ROUTER, the GATE/abstain policy, and the
   Route-1/Route-2 COMBINE rule must each be a registered `hdlab/` organ, not experiment-local functions,
   or E4 becomes another island. `hdlab/mcscript_extraction.py` and `hdlab/outcome_event_extraction.py`
   are still ABSENT from `data/capability_registry.jsonl` (E3 finding) -- register with the E4 anchor.

---

## Cheap decisive test

E4's temporal-subset gate: on the pre-registered MCScript2.0 temporal ("when"/order) subset (~32.7% of
questions, BoW-provably-order-limited), does the augmented BoW-base + gated retrieve-validate-advance loop
(grounded events, coref-canonicalized agents, temporal-edge validation, abstain-on-empty) beat the BoW
baseline by >=0.05, with a knowledge-scramble ablation collapsing the gain to BoW-level AND the full-set
accuracy not regressing below BoW-0.01? Cheap (reuses owned organs + solved store, no GPU, 1084 short
narratives), can-fail (BoW already wins aggregate; three ablations force the gain onto the loop), one-lever
(the loop, isolated by scramble/no-validate/content-only controls), glass-box (every override traced).

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **HARD-PASS:** AUGMENTED - BoW on the temporal subset >= +0.05 (>=3 seeds) AND scramble collapses
  (AUGMENTED - ABLATION-1 >= +0.05, ABLATION-1 <= BoW+0.01) AND AUGMENTED - content-only >= +0.03 AND
  full-set AUGMENTED >= BoW - 0.01. Predicted P ~ 0.30 (deflated; the genuine open risk is the conjunction
  of E3 fixes plus whether temporal order is recoverable on real crowd prose).
- **HARD-FAIL:** no subset lift (AUGMENTED <= BoW) OR scramble does not collapse (gain survives scrambling
  -> it was content) OR full-set regresses below BoW-0.02 (gate leaks below-chance votes). Any of these
  falsifies the augment-loop-on-MCScript2.0 direction and triggers the pivot to TORQUE/MCTACO/WIQA.
- **MIDDLE_BAND (pre-committed exit):** +0.02 to +0.05 subset lift with partial scramble-collapse ->
  inference is real but swamped on MCScript2.0; pivot the flagship to purpose-built temporal/causal
  benchmarks, keep the (directionally-validated) augment machinery.
- **Independent, benchmark-selection prediction (not gated on E4):** the causal retrieve-VALIDATE loop
  (the substrate's HARD_PASS strength) will NOT be demonstrable on MCScript2.0 (0.7% causal questions);
  its win must be shown on WIQA. Predicted with high confidence (P ~ 0.80) from the corpus scan.

## Cross-thread synthesis

- Answers the E4 design request against `notes/research_comprehension_barrier_map_brain_foundational_
  2026-08-10.md` (which sequenced E4 as the end-to-end real-prose loop): this note specifies E4 as an
  AUGMENT (not the replace the map implicitly assumed) and, critically, re-scopes its success criterion
  from aggregate MCScript2.0 to a temporal SUBSET, because the aggregate is BoW-favorable -- a refinement
  the map did not make.
- Builds directly on `notes/research_e3_realprose_extraction_feasibility_scope_2026-08-10.md`: E3's three
  fixes (present-tense, grounded symbols, mention adapter) are E4's preconditions; E4 is the composition
  that turns E3's per-piece gates into an end-to-end MCQA win-or-abstain system.
- Extends the MCScript2.0 arc's own HARD_FAIL (`data/exp_mcscript2_mcqa_droptense_properscramble_v1`):
  reuses its BoW baseline, its structure_helps temporal cluster, and its 39%-empty / 404-tie diagnostics
  as the DESIGN CONSTRAINTS the augment gate is built to satisfy, and re-reads its 112 helps as
  uninformative-until-scramble-controlled (Section 1c) -- a sharper honest reading than the raw count.
- Corrects the standing "static structure loses to BoW twice" narrative: the fix is not a better static
  structure but a COMPOSITION with an abstain gate, which is the brain's own architecture (Section 5).

## Substrate-product implications

The defensible product is a GLASS-BOX comprehension system that (a) never does worse than a transparent
content baseline (the abstain gate guarantees it) and (b) on the questions where content provably fails
(temporal order, causal chains), produces an AUDITABLE inference trace -- which shard routed, which event
pulled in, which temporal/causal edge validated the answer. That trace is the differentiator no opaque PLM
offers, and it is exactly what the augment architecture emits per override. The honest commercial read
mirrors the scientific one: pick the demonstration surface where the glass-box inference edge is not
swamped (temporal/causal benchmarks, or MCScript2.0's temporal subset), show the win-with-trace there,
and use the never-regress guarantee as the reliability story on the content-saturable majority. Do not
market or measure on aggregate MCScript2.0 accuracy -- it rewards content matching and hides the edge.

## Citations (verified count)

Fresh this cycle (2 web scans, generic terms per query-privacy; MCScript2.0 is a public benchmark name):
MCScript2.0 corpus facts (Ostermann, Roth & Pinkal 2019, SemEval S19-1012; ~20k questions / ~3.5k texts,
~half require commonsense/script knowledge, human near-ceiling, TriAN best among early benchmarks) --
verified via ACL Anthology + arXiv 1905.09531 abstract. Dual-route reading neural evidence (verified live):
npj Science of Learning 2024 (expository-text comprehension network: ATL + hippocampus + vm/vlPFC, lateral
PFC for mental-model construction / new-prior integration); Progress in Neurobiology 219 (2022) 102351
(rapid distributed semantic cognition); Cerebral Cortex 2025 bhaf289 (semantic + DMN connectivity in
narrative comprehension); the multifaceted-memory-representations (gist/semantics/schema/episode, distinct
substrates) framing. Corpus scan (this cycle, off-disk): 19,821 MCScript2.0 questions, temporal 32.7% /
causal-why 0.7% -- computed directly, not cited. Cell metrics (off-disk, read this cycle, not from verdict
string): BoW 0.629 / structured 0.401 / scramble 0.476; helps 112 / hurts 359; n_cand_zero 1591/4040;
n_ties 404; by_type text 0.685-vs-0.389, commonsense 0.594-vs-0.400.

CARRIED (not re-derived) from the barrier map's verified base, credited there: Kintsch Construction-
Integration 1988; McKoon & Ratcliff minimalist 1992; van den Broek Landscape / coherence standards;
Albrecht & O'Brien 1993; Ferreira good-enough 2002; Sanford & Sturt shallow processing 2002; Christianson
misinterpretation; Reyna & Brainerd fuzzy-trace; Lambon-Ralph hub-and-spoke; Schacter-Addis constructive
simulation 2007; Trabasso & van den Broek 1985; Singer validation; Stage-2A / Stage-1 HARD_PASS results
(on-disk). Benchmark candidates named (public, not searched-in-depth this cycle, flagged for exp_dev
verification before adoption): TORQUE (Ning et al. 2020), MCTACO (Zhou et al. 2019), WIQA (Tandon et al.
2019), ROPES, QuaRTz, aNLI/ART. No citation fabricated or re-asserted from memory; brain-mechanism claims
carried are each independently verified in the barrier map's own citations section.
