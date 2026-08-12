# Research drill 2: how the brain does gap-driven scaffolded learning that FADES (2026-08-10)

Director task: nail HOW THE BRAIN does gap-driven scaffolded learning that fades, element by
element (SHAPE + POSITION + METRIC), for the "gap-driven CRUTCH" design (fills world-knowledge
gaps only when flagged, consolidates into the substrate, FADES as competence grows). Explicit
2x-drill discipline: go deeper on what the project already found, don't re-run the same scan.
KB-check (`substrate_query.sh`, query = scaffolding/ZPD/CLS/schema-consolidation/predictive-coding/
surprise) returned cosine=0.41 top-5, all pointing at this project's own 2026-08-09 sister notes
(`research_psych_acquisition_consolidation_loop_2026-08-09.md`, word-grain FLAG->LIBRARY->
CONSOLIDATE->GUARD->BANK; `research_brain_script_acquisition_consolidation_2026-08-09.md`,
script-grain version) plus the 2026-07-28 CLS fidelity audit and the 2026-06-22 CLS 5x drill.
Grep-verified (`Vygotsky|zone of proximal|ZPD|automati[sz]ation|power law of practice|scaffold
withdraw|instance theory|ACT-R` and `ACC conflict|anterior cingulate|conflict monitoring|
Botvinick|hippocampal novelty|MMN`) against every file under `notes/`: **zero hits, both
searches** -- confirming the FADE trajectory and the ACC/hippocampal-comparator/metacognitive
specifics of THE FLAG are genuinely new territory this project has not drilled, while the
CONSOLIDATION and GENERALIZATION mechanisms were already drilled in depth 08-09/07-28/06-22 (not
re-run here per 2x discipline -- summarized with pointers, extended only where new).

Method: solo WebSearch/lit-scan (no nested sub-agents this cycle, per dispatch instruction),
10 targeted queries across 4 literatures, cross-checked against the ACTUAL code of every owned
organ named below (`hdlab/grounding_acquisition_loop.py`, `hdlab/predictive_coding.py`,
`hdlab/consequence_learning_loop.py`, `hdlab/verb_lexical_similarity.py`, `hdlab/learner/core.py`)
read fresh this session, not from memory of the 08-09 notes' descriptions of them.

## HEADLINE

Two findings matter more than the rest combined.

**(1) THE FLAG is not one brain system, it's (at least) three, and we own a faithful copy of only
one.** Predictive-coding/event-boundary mismatch (Reynolds/Zacks/Braver 2007 -- already drilled
08-09, and now BUILT as `predictive_coding.py::relative_threshold_gate`) answers "does the model's
own prediction disagree with reality." That is necessary but not sufficient: the brain has two
MORE systems the 08-09 notes never covered -- a hippocampal associative-mismatch comparator
(Kumaran & Maguire; the CA1 match/mismatch literature) that fires on violated *specific*
expectations rather than generic surprise, and an ACC/dACC resource-allocation layer (Shenhav,
Botvinick & Cohen 2013, Expected Value of Control) that decides whether a detected
mismatch is *worth* the effort of resolving right now. Our loop has the first (partially, see
below) and has NEITHER of the other two -- every flagged item is processed identically regardless
of expected payoff, there is no competition for a shared "control budget" across simultaneously-
pending gaps.

**(2) THE FADE is not merely under-built, it is structurally impossible in the current design,
and this is the actual deliverable of this drill.** `grounding_acquisition_loop.py`'s `GROUNDED_*`
status is explicit, deliberate, and TERMINAL (the 08-09 note names this as an honest deviation
from Ghosh & Gilboa's "adaptable" schema criterion). More importantly, freshly re-read this
session: BANK does not write into any DISTRIBUTED, natively-read associative structure at all --
`register_acquired_outcome` writes into `verb_lexical_similarity.ACQUIRED_OUTCOME_VERB_FEATURES`,
a **plain in-memory Python dict**, consulted by an explicit `in_lexicon()` lookup call that
downstream comprehension code must remember to call. There is no pathway by which a repeatedly-
confirmed, consistently-mapped acquired item ever gets folded into the SAME substrate structure
(the base similarity scorer / codebook / W-matrix) that produces "native," lookup-free predictions
for already-known words. Structurally, the crutch cannot fade -- it is architecturally a permanent
side-table, not a temporary scaffold that gets internalized. **Cross-checked against
`notes/research_crutch_fade_loop_owned_organ_wiring_2026-08-10.md` (DRILL 3, same day, filed after
this drill's code-read): that independent wiring audit names the SAME flat-dict target
(`verb_lexical_similarity`'s Tier-3 overlay) as the current BANK destination and independently
flags it as wrong, and additionally names a concrete, already-CERT-validated candidate FIX this
drill did not have on its radar -- `hdlab/hd_fact_store.py`, a source-trust-vetted fact store where
provenance+trust is natively bound INTO the fact vector, not side metadata. A "crutch-sourced fact
starts low-trust, gets promoted toward full-trust as consistent corroborating evidence accumulates"
design is structurally a TRUST-PROMOTION curve -- which is a real, buildable proxy for the
fade/automaticity curve this drill's Test A measures indirectly via the base similarity scorer.**
The brain's fade (Fitts & Posner 1967
cognitive->associative->autonomous; Logan 1988 instance theory; Shiffrin & Schneider 1977 automatic-
ity requires CONSISTENT mapping) is a literal representational MIGRATION -- effortful,
lookup-dependent retrieval is gradually replaced by fast, direct, automatic retrieval of the SAME
kind of representation used for old material -- not a permanent annotation that a fact "has been
learned." This is the single biggest, cleanest, most actionable fidelity gap this drill found.

## 1. THE FLAG -- how/when the brain seeks help (detects a gap)

| System | Mechanism | Citation | Established? | Owned organ / gap |
|---|---|---|---|---|
| Predictive-coding / event-boundary mismatch | RELATIVE self-referential prediction error (current SSE / running-avg-of-own-recent-SSE), not an absolute magnitude | Reynolds, Zacks & Braver 2007, *Cognitive Science* 31(4) (already drilled 08-09, ROC AUC 0.92-0.94 across thresholds) | ESTABLISHED, cross-validated by independent statistical-learning literature (Baldwin et al. 2008; Stahl et al. 2014) | `hdlab/predictive_coding.py::relative_threshold_gate` + `running_avg_update` -- BUILT this cycle window (literature-pinned to the exact Eq. 8 decay=0.05 form), self-tested, but **confirmed this session: NOT imported/wired into `grounding_acquisition_loop.py` or `consequence_learning_loop.py` at all** (`grep -rl relative_threshold_gate` over the whole repo returns only its own module). The loop's actual live FLAG trigger today is still `consequence_learning_loop.teacher_verdict`'s isolated per-lemma MET/UNMET vote -- an ABSOLUTE, non-relative signal, exactly the "wrong-grain" diagnosis the 08-09 script note already made. Anchor 2 of that note's hand-off (build+A/B `relative_threshold_gate`) targets this precisely and is still un-run. |
| Hippocampal associative-mismatch comparator | Fires on violation of a SPECIFIC associatively-retrieved prediction (e.g. familiar items in unfamiliar temporal order), not generic stimulus novelty; CA1 acts as the match/mismatch detector; a 2025 PNAS finding (already cited in the 08-09 word note, section 1c) shows this mismatch signal tracks *episodic*, not generic-schematic, predictions | Kumaran & Maguire (hippocampal novelty-detection review, *J Neurosci*); match-mismatch fMRI/high-res CA1 studies (Kumaran & Maguire 2007, *J Neurosci* 27(32):8517; Duncan, Sadanand & Davachi, CA1 match/mismatch, *Hippocampus*) | ESTABLISHED, converging fMRI + high-resolution subfield evidence | **New system, NOT previously mapped to any owned organ.** This is distinct from `residual_magnitude` (generic bipolar mismatch fraction against a whole-matrix generative model) -- the hippocampal comparator's SHAPE is "does THIS SPECIFIC episode violate the prediction retrieved from ITS OWN best-matching prior episode," which is closer to `schema_consistency_split_half`'s per-item, per-trace comparison than to a global predictive-coding residual. No owned organ currently computes an associative-mismatch signal AT FLAG TIME (only at CONSOLIDATION time, via the split-half guard, after an item already has >=4 traces) -- there is no mechanism for "this ONE new episode contradicts what I already believed about this specific lemma" to itself act as an elevated-priority flag. |
| ACC / dACC conflict-and-control-allocation | dACC signals response/task conflict and, per the integrative Expected Value of Control (EVC) model, allocates cognitive-control effort as a cost-benefit computation: expected payoff of resolving the conflict, MINUS the effort cost of the control needed -- control is recruited selectively, not uniformly, when its expected benefit justifies the cost | Botvinick, Cohen & Carter 2001/2004 (conflict monitoring, *Trends Cogn Sci* 8(12)); Shenhav, Botvinick & Cohen 2013, *Neuron* 79(2):217-240 (Expected Value of Control) | ESTABLISHED, dominant integrative framework (Botvinick conflict-monitoring itself has an active competing account -- Alexander & Brown 2011 error-likelihood/PRO model -- flagged as CONTESTED at the mechanistic-source level, though the phenomenon of ACC control-signaling itself is not disputed) | **New system, NOT previously mapped, and the cleanest actionable gap in this section.** Every item that clears `Library.flag`'s trace-append gets IDENTICAL downstream treatment (same `MIN_CONFIRM`, same `schema_thresh`, same `patience_max`) regardless of how consequential or how cheap-to-resolve it is. There is no cross-item competition for a shared, finite "control/consolidation budget" the way EVC predicts -- `PATIENCE_MAX` is a per-item ceiling on retries, not a resource ALLOCATED across simultaneously-pending items by expected value. `surprise_order` orders TRACES within an already-admitted item by disagreement, which is a different question (replay priority within a commitment) from EVC's question (is this gap worth investing consolidation effort in AT ALL, relative to the other pending gaps). |
| Metacognitive monitoring (feeling-of-knowing / ease-of-processing) | A distinct, INTROSPECTIVE signal, not the same currency as raw prediction error: judgments of learning are built from CUES (retrieval fluency, partial-recall accessibility), and monitoring/control can DISSOCIATE -- a system can detect it doesn't know something (monitoring) without that automatically triggering corrective action (control) | Nelson & Narens 1990 (meta-level/object-level monitoring-control loop); Koriat 1997, *JEP:General* 126 (cue-utilization account of judgments of learning); accessibility model of feeling-of-knowing | ESTABLISHED, foundational metamemory framework, still the field's dominant model | **New, and the most philosophically-loaded gap**: `decide_keep_or_revert`'s abstain-band and `conformal.py`'s calibrated-abstention machinery are the closest owned analogues (both produce "I don't know, don't commit" as a distinct third state, not forced-binary), but neither is wired as the loop's INTAKE flag -- they gate OUTPUT decisions (whether to keep/revert a vote, whether to emit a calibrated prediction), not "should I go acquire more evidence about this at all." The monitoring/control DISSOCIATION point is itself a useful design lesson: our loop currently conflates "detected a gap" (monitoring) with "will pursue closing it" (control) into one unconditional pipeline -- the brain's own architecture keeps these separable, which is exactly what an EVC-style gate above would restore. |

**Net for FLAG**: the mechanism we own (`residual_magnitude`/`relative_threshold_gate`) is a
faithful copy of the RIGHT SHAPE for one of four converging brain flag-systems (predictive-coding/
event-boundary), still unwired into the loop that actually needs it. Two further systems (ACC/EVC
resource-allocation, metacognitive monitor-control dissociation) are entirely absent as concepts,
not just unwired -- there is nothing in the codebase that decides "is this gap worth resolving" as
opposed to "did the model mispredict."

## 2. THE FILL + CONSOLIDATION (safe) -- how a told fact becomes durable knowledge

This is the piece the 08-09 sister notes already drilled in depth (CLS two-stage McClelland/
McNaughton/O'Reilly 1995; Tse/Langston/Morris schema-consolidation 2007/2011; van Kesteren SLIMM
2012; Ghosh & Gilboa 2014 operational schema criteria; the MDL two-part-code commit gate already
wired as `hdlab.learner.core.per_cluster_gate`; the false-consolidation double-edge, Warren et al.
2014). Not re-drilled here (2x discipline: extend, don't re-scan). One genuinely new angle this
session adds, because it directly touches SAFETY:

| Finding | Citation | Established? | Extension to owned organ |
|---|---|---|---|
| Automaticity itself is graded by TRAINING CONSISTENCY, not exposure count alone: under Consistent Mapping (CM -- the stimulus-response relationship never changes across trials), automatic detection develops and becomes largely independent of load/set-size; under Varied Mapping (VM -- the same stimulus is sometimes a target, sometimes a distractor, across trials), NO automaticity develops no matter how much practice accrues | Schneider & Shiffrin 1977, *Psychol Rev* 84(1); Shiffrin & Schneider 1977, *Psychol Rev* 84(2) | ESTABLISHED, foundational dual-process theory, replicated across decades (some contested detail on exact VM-condition asymptotes, not the CM/VM distinction itself) | **This is the missing SAFETY predictor for consolidation, not just a fade-speed predictor (see section 4).** An item whose traces are CONSISTENT (same polarity, coherent context every time) is exactly the case Schneider/Shiffrin's own paradigm says SHOULD be allowed to automatize/consolidate; an item whose traces are noisy/contradictory (varied mapping) should never be pushed toward consolidation regardless of raw trace COUNT. This maps directly onto `_vote_margin` (already computed, already used for POS/NEG/NEUTRAL labeling) but that margin currently feeds only the LABEL, not the GATE -- `consolidation_pass` gates on `schema_score >= schema_thresh` (context-coherence) and, optionally, the MDL compression gate, but never on vote-margin CONSISTENCY itself as an independent third safety signal. A genuinely inconsistent-polarity item (low `|margin|`) with a coherent CONTEXT could still clear both existing gates and bank as `GROUNDED_NEUTRAL` -- which is arguably fine for polarity-neutral items, but the Schneider/Shiffrin point is sharper: consistency of the STIMULUS-OUTCOME MAPPING, not just of the surrounding context words, is what licenses safe automatization, and that is a check the guard does not currently make explicit. |

## 3. THE GENERALIZATION -- abstracting specific tellings into general schemas

Also already drilled in depth 08-09 (fast-mapping Carey & Bartlett 1978, Carey 2011; SEM's sticky-
CRP schema-clustering Franklin/Norman/Gershman 2020; script-generalization existence-proof Bower/
Black/Turner 1979). One new, directly load-bearing citation this session:

| Finding | Citation | Established? | Extension |
|---|---|---|---|
| Learners generalize from as few as ONE example not by pure similarity but via Bayesian inference over a HYPOTHESIS SPACE of possible word meanings, weighted by a size/specificity prior -- the "suspicious coincidence" effect: if all observed examples happen to fall under an unexpectedly narrow subordinate category, that itself is evidence FOR the narrow reading, but only under STRONG SAMPLING (examples deliberately drawn from the concept's true extension) -- under WEAK SAMPLING (examples drawn incidentally), the same coincidence carries little inferential weight | Xu & Tenenbaum 2007, *Psychol Rev* 114(2) (word learning as Bayesian inference); Tenenbaum & Griffiths (weak vs strong sampling distinction) | ESTABLISHED, influential computational-level account; the sampling-assumption distinction itself is a live methodological point, not universally agreed on for every domain | Directly relevant to the substrate's `MIN_CONFIRM`/patience design: the brain's generalization-from-few-examples is not a flat trace-count threshold, it is SAMPLING-ASSUMPTION-SENSITIVE -- traces drawn from genuinely varied narrative contexts (closer to "strong sampling," deliberately informative) should license faster/more confident generalization than the same count of traces drawn from near-duplicate contexts (closer to incidental "weak sampling," which under Xu/Tenenbaum's own account should generalize LESS confidently despite equal count). `schema_consistency_split_half`'s cosine metric currently rewards near-IDENTICAL context vectors (a coherent-repeat scores near 1.0, per its own self-test) -- which is the right signal for "is this a genuine recurring pattern" but is silent on whether the ACCUMULATED EVIDENCE was informatively diverse (multiple different narrative settings) versus repetitively narrow (same setting restated). This is a real, literature-motivated refinement candidate for `surprise_order`/the eventual generalization check, not a currently-implemented distinction. |

## 4. THE FADE -- the scaffolding-withdrawal trajectory (the drill's core new territory)

| Finding | Citation | Established? | Shape of the trajectory | Owned organ / gap |
|---|---|---|---|---|
| Skill acquisition passes through three qualitatively distinct stages: COGNITIVE (slow, verbally-mediated, error-prone, heavy reliance on explicit instruction/support), ASSOCIATIVE (errors drop, performance consolidates around a stable procedure), AUTONOMOUS (fast, low-effort, resistant to dual-task interference, minimal conscious monitoring needed) | Fitts & Posner 1967, *Human Performance* (Brooks/Cole); modern replications/refinements e.g. Anderson's ACT-R skill-acquisition extension | ESTABLISHED, foundational, still the field's default 3-stage frame (later work, e.g. Anderson, formalizes the SAME three stages as declarative-to-procedural compilation rather than three literal discrete phases -- a continuous-underlying/discrete-labels tension, not a refutation) | Discrete-labeled STAGES over a continuous underlying transfer process; NOT a simple linear ramp -- qualitative shift from externally-scaffolded/effortful to internally-generated/automatic | This is the missing STAGE MODEL for `LibraryItem.status`. Current states are `PENDING -> GROUNDED_* / ESCALATED`, a strict two-stage model (episodic vs banked) with no ASSOCIATIVE middle stage and no notion of retrieval EFFORT changing after `GROUNDED_*` is reached. |
| The power law of practice: response time/effort as a function of practice trials is a power function (T = T1 * N^-b) across an enormous range of skills (typing, mental rotation, lexical decision, fact retrieval) -- LARGE gains early, RAPIDLY DIMINISHING marginal gains, approaching but never fully reaching an asymptote; some later work argues the true within-learner shape is closer to EXPONENTIAL (constant proportional decrement per trial, not a diminishing one) -- the debate is about the EXACT functional form, not the qualitative steep-early/flattening-tail shape, which both candidate functions share | Newell & Rosenbloom 1981 (power law of practice, cross-domain synthesis); Heathcote, Brown & Mewhort 2000 (exponential-law critique, *Psychonomic Bulletin & Review* 7); Rickard 1997 (CMPL: CM/VM strategy-shift account of the apparent power-law shape) | Power-law SHAPE robustly ESTABLISHED as a description; the EXACT generating function (power vs exponential vs strategy-mixture) is ACTIVELY CONTESTED at the mechanistic level | **Answers the drill's explicit question directly: the fade is STEEP-THEN-TAIL, not gradual/linear.** Most of the crutch-dependency reduction happens in the first few resolutions of a given gap; after that, further exposures buy rapidly diminishing additional independence. This has a direct, falsifiable design implication (section "Cheap decisive test" below): if our loop ever builds a fade curve, a LINEAR decay-of-reliance-with-trace-count model would already be the WRONG functional form to assume; a power-law or exponential decay is the brain-faithful null hypothesis to fit against. |
| Automaticity develops via accumulation of INDIVIDUAL MEMORY TRACES ("instances") from each encounter; early performance uses a slow general algorithm, later performance is dominated by fast direct RETRIEVAL of a matching stored instance -- critically, automaticity is a property of a SPECIFIC stimulus-response mapping, not a global "skill level"; and (per Schneider/Shiffrin, section 2) it develops ONLY under consistent mapping | Logan 1988, *Psychol Rev* 95(4) (Instance Theory of Automaticity); Logan 1992 (empirical test, *JEP:LMC*) | ESTABLISHED, one of two dominant automaticity theories (the other being Anderson's ACT-R procedural-compilation account -- broadly complementary, not competing, on the qualitative claim that practice shifts control from slow/general to fast/specific) | **This directly names the PREDICTOR the drill asked for: "what predicts how fast a given piece of knowledge stops needing the crutch."** Per Instance Theory: (a) NUMBER of independent, consistent exposures (more stored instances = faster, more reliable direct retrieval winning the race against the slow algorithm) and (b) CONSISTENCY of the mapping (section 2's Schneider/Shiffrin finding -- inconsistent mapping never automatizes REGARDLESS of exposure count) are the two literature-named predictors. Both map cleanly onto quantities the substrate ALREADY COMPUTES per item (`len(it.traces)`, `_vote_margin`'s consistency) but currently uses ONLY as gate inputs (bank yes/no), never as inputs to a continuous fade/reliance curve. |
| Scaffolding support is CONTINGENT and WITHDRAWN as competence grows, not fixed then dropped: effective tutoring dynamically adjusts assistance level in response to the learner's demonstrated progress (more support when the task is new/hard, progressively less as the learner succeeds unaided) -- withdrawal is COMPETENCE-TRACKED, not a fixed schedule | Wood, Bruner & Ross 1976, *J Child Psychol Psychiatry* 17(2) (coined "scaffolding"; block-pyramid tutoring study, adults reduced support specifically as children succeeded) | ESTABLISHED, foundational (the term's origin), heavily replicated in educational-scaffolding research; NOT literally Vygotsky's own term (Vygotsky defined the Zone of Proximal Development, 1978 translation of 1930s work, but never used "scaffolding" -- the operationalization is Wood/Bruner/Ross's) | **Names the WITHDRAWAL POLICY, distinct from the withdrawal TRAJECTORY (the power-law/instance-theory rows above).** The brain-faithful design is not "fade on a fixed schedule after N exposures" -- it is "fade IN PROPORTION TO DEMONSTRATED, MEASURED COMPETENCE, re-checked continuously, capable of re-escalating support if competence regresses." Our loop has no notion of "demonstrated competence" for a `GROUNDED_*` item at all post-bank -- once banked, `Library.flag` no-ops on it forever (terminal), so there is no channel by which the substrate could even NOTICE a `GROUNDED_*` item's downstream performance degrading and re-open it (contingent RE-scaffolding, which Wood/Bruner/Ross's own study explicitly includes -- support was increased again when a child's performance faltered, not just monotonically withdrawn). |

**Concrete fade-trajectory statement** (synthesizing the four rows above): the brain-faithful FADE
is (a) STAGED (cognitive/effortful-lookup -> associative/consolidating -> autonomous/native,
Fitts & Posner), (b) STEEP-THEN-TAIL in shape (power-law or exponential, not linear, Newell &
Rosenbloom), (c) driven by two measurable predictors already computed by our loop but not yet used
this way -- EXPOSURE COUNT and MAPPING CONSISTENCY (Logan; Schneider & Shiffrin) -- and
(d) CONTINGENT/bidirectional, re-escalating support if downstream performance regresses, not a
one-way terminal bank (Wood, Bruner & Ross). Our loop currently implements NONE of (a)-(d): it has
a single terminal bit (`GROUNDED_*`), no post-bank observation channel, no reliance/effort metric,
and no re-escalation path.

## 5. SHAPE + POSITION + METRIC audit -- owned loop vs brain, per element

| Element | Brain SHAPE | Brain POSITION (where in the pipeline) | Brain METRIC | Owned SHAPE | Owned POSITION | Owned METRIC | Verdict |
|---|---|---|---|---|---|---|---|
| FLAG (pred-coding leg) | relative self-referential mismatch vs own running baseline | continuous, every incoming event, pre-attentive | ratio = SSE_t / running_avg(SSE)_{t-1} | `relative_threshold_gate` exists, literature-pinned | **NOT wired** into the loop's live trigger | ratio vs threshold | FAITHFUL SHAPE, WRONG POSITION (built, unwired) |
| FLAG (live trigger today) | -- | -- | -- | `teacher_verdict(signal_mode="signal_a_only")` | wired, called by `credit_window` | isolated per-lemma MET/UNMET, absolute | DEVIATES (absolute, no "against what schema" baseline -- the 08-09 diagnosis, still true) |
| FLAG (hippocampal comparator leg) | associative mismatch vs THIS item's own specific prior-episode prediction | at first re-encounter of a specific lemma/schema | match/mismatch amplitude, episodic-specific | none | absent | absent | ABSENT -- no owned organ computes this at intake time (only `schema_consistency_split_half`, and only once >=4 traces exist) |
| FLAG (ACC/EVC leg) | expected-value-of-control gate: benefit of resolving minus effort cost, allocated across competing gaps | before committing consolidation resources to a specific pending item | continuous currency (value - cost) | none | absent | absent | ABSENT -- every flagged item gets identical treatment; `PATIENCE_MAX` is a per-item retry ceiling, not a cross-item resource allocation |
| FLAG (metacognitive leg) | monitoring (detect gap) dissociable from control (act on it); fluency/JOL cue-based | continuous, introspective | subjective confidence/fluency cue | `decide_keep_or_revert` abstain-band, `conformal.py` | wired for OUTPUT decisions, not INTAKE | vote-margin abstain-band; calibrated coverage | PARTIAL -- right SHAPE, WRONG POSITION (gates output, not "should I pursue this gap") |
| CONSOLIDATION (safe-commit) | schema-congruency (SLIMM) AND multi-episode structure-compression (MDL) | offline "sleep" pass, batched, separate from reading | context congruency score AND compression-ratio-past-null | `schema_consistency_split_half` AND (optional) `learner.per_cluster_gate` | wired, conjunctive, `consolidation_pass` | cosine margin AND compression ratio >= 1.0 | FAITHFUL (already drilled+built 08-09; MDL leg still un-run per that hand-off's anchor 1) |
| CONSOLIDATION (mapping-consistency safety leg) | automaticity licensed ONLY under consistent stimulus-outcome mapping (Schneider/Shiffrin) | part of the commit decision | vote-margin / polarity consistency across traces | `_vote_margin` computed | feeds the LABEL only, not the GATE | margin value, unused as a gate threshold | PARTIAL DEVIATION -- computed, not consulted as an independent safety gate (new finding this drill, section 2) |
| GENERALIZATION | Bayesian hypothesis-space inference, sampling-assumption-sensitive (informative-diverse evidence generalizes faster/more confidently than repetitive-narrow evidence of equal count) | at/after schema commit | posterior over hypothesis space, weighted by sampling regime | `schema_consistency_split_half` (context coherence), `ruleind_plugin`/MDL (structural compression) | wired at consolidation time | cosine coherence; compression ratio | PARTIAL -- captures "is this a real recurring pattern," silent on evidence-diversity/sampling-assumption distinction (new refinement candidate, section 3) |
| FADE (staged transfer) | 3-stage cognitive->associative->autonomous representational migration | continuous, post-commit, ongoing | qualitative stage + quantitative RT/error curve | none | absent (terminal `GROUNDED_*` bit) | none | ABSENT -- the headline gap |
| FADE (trajectory shape) | power-law/exponential steep-then-tail decline in retrieval effort/latency | tracked per item, per exposure | RT or effort as f(exposure count) | none | absent | none | ABSENT |
| FADE (predictors) | exposure count AND mapping consistency jointly predict fade speed | -- | trace count, vote-margin | both ALREADY COMPUTED (`len(traces)`, `_vote_margin`) | computed for OTHER purposes (gating, labeling) | -- | BUILDING-BLOCKS PRESENT, not wired to any fade output |
| FADE (withdrawal policy) | contingent, competence-tracked, bidirectional (can re-escalate) | continuous, post-commit monitoring | demonstrated task success/failure rate | none (`Library.flag` no-ops on non-PENDING items) | absent | absent | ABSENT -- no re-escalation path exists even in principle; a `GROUNDED_*` item cannot be reopened by later evidence |
| FADE (representational target) | migrates from hippocampal/effortful lookup INTO the same distributed cortical structure used for old/native knowledge | the actual physical relocation of the engram | -- | `register_acquired_outcome` writes to `ACQUIRED_OUTCOME_VERB_FEATURES` (plain dict) | permanent SEPARATE overlay, never merged into base codebook/W | binary dict membership | STRUCTURALLY BLOCKS FADE -- see HEADLINE (2); this is the deepest gap, a POSITION problem more than a missing-metric problem |

## Cheap decisive test

Two tests, cheapest-first, both reusing already-computed quantities (no new corpus, no new
mechanism risk beyond instrumentation):

**Test A (fade-feasibility, primary).** Instrument `verb_lexical_similarity`'s existing base
similarity scorer (the "native," non-overlay pathway already used for lexicon-known words) to
ALSO score every `GROUNDED_*` item from a completed acquisition run, ignoring the
`ACQUIRED_OUTCOME_VERB_FEATURES` overlay entirely. For each `GROUNDED_*` item, record whether the
base scorer, using only its own pre-existing (non-acquired) codebook, ALREADY assigns the correct
polarity via structural/distributional proximity to known verbs -- this is "native coverage,"
i.e. crutch-independence, measured WITHOUT building any new fade mechanism yet. Correlate native-
coverage rate against (i) trace count at grounding time and (ii) `_vote_margin` (consistency) at
grounding time, per Logan/Schneider-Shiffrin's joint prediction.

**Test B (withdrawal-policy feasibility, secondary).** Using the SAME completed run, check whether
any `GROUNDED_*` item's LATER traces (post-bank; currently discarded since `Library.flag` no-ops
on non-PENDING items) would, if not discarded, have contradicted the banked polarity -- i.e.
measure how often the terminal-bank design's inability to re-open an item would have caused it to
retain a stale/wrong polarity, versus a hypothetical contingent-reopening design.

## Falsifiable predictions

**HARD-PASS** (Test A, both required):
- Native-coverage rate (fraction of `GROUNDED_*` items the base similarity scorer independently
  gets right, ignoring the overlay) is significantly higher for items in the top-half of
  `|_vote_margin|` (high consistency) than the bottom-half, on the SAME item set -- replicating
  Schneider/Shiffrin's consistent-mapping-drives-automaticity finding as a substrate-native effect,
  not an assumed one.
- Native-coverage rate is monotonically non-decreasing in trace count across at least 3 count
  buckets (replicating Logan's instance-accumulation prediction), with the STEEPEST gain in the
  lowest buckets and diminishing gains in higher buckets (the power-law/steep-then-tail shape,
  Newell & Rosenbloom) -- a roughly LINEAR native-coverage-vs-count relationship would falsify the
  steep-then-tail shape specifically, even if the overall positive trend holds.

**HARD-FAIL** (Test A, any one triggers, subject to mandatory pre-check):
- Native-coverage rate is ~0% for every `GROUNDED_*` item regardless of consistency/trace count --
  **mandatory pre-check first**: hand-plant a maximally-prototypical synthetic verb (near-identical
  distributionally to an already-known base verb) and confirm the base scorer CAN score it
  correctly in principle; if that sanity check fails, this is a harness/scorer bug, not a negative
  on fade-feasibility, per the standing "flat result = broken experiment" discipline.
- No relationship between consistency/count and native-coverage (flat across all buckets after the
  pre-check passes) -- would falsify Schneider/Shiffrin and Logan's joint prediction as applied to
  this substrate's specific representational geometry, a genuinely informative negative (would mean
  the base codebook's similarity structure does not organize acquired-verb neighborhoods the way
  human lexical-semantic space does, a real finding about the substrate's distributional geometry,
  not about the psychology).

**MIDDLE_BAND**: native-coverage rate is nonzero and correlates with EITHER consistency OR trace
count but not both -- informative (identifies which of the two brain-named predictors actually
carries signal in this substrate's geometry) but underpowered as a full replication; proceed to
build the actual staged/graded fade mechanism using whichever predictor cleared, not both.

## Cross-thread synthesis

Extends (does not duplicate) `notes/research_psych_acquisition_consolidation_loop_2026-08-09.md`
and `notes/research_brain_script_acquisition_consolidation_2026-08-09.md` (FLAG/CONSOLIDATION/
GUARD, word-grain and script-grain, both already thoroughly drilled and cross-checked against
code) by supplying the two things those notes explicitly did not cover: the full multi-system
account of THE FLAG (ACC/EVC resource-allocation, hippocampal associative-comparator, metacognitive
monitor-control dissociation -- all new citations this session) and the entire FADE literature
(Fitts & Posner, Logan instance theory, Newell & Rosenbloom power law, Schneider & Shiffrin
consistent-mapping, Wood/Bruner/Ross scaffolding-withdrawal -- zero prior coverage, grep-confirmed).
Extends `notes/consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md`'s CLS/hippocampal-
replay grounding with the specific consistency-as-safety-signal finding (section 2) that audit did
not separately name. Corrects nothing in the prior notes; confirms the 08-09 script note's
wrong-grain FLAG diagnosis is still live in the current code (freshly re-verified: `teacher_verdict`
is still the wired trigger, `relative_threshold_gate` still unwired) and adds a NEW, higher-priority
finding on top of it: even a correctly-wired relative-threshold FLAG would only fix one of at least
four converging brain flag-systems, and the FADE gap is structurally deeper than any of the
already-identified anchors address (none of the three ranked anchors in the 08-09 script hand-off
touch the BANK-target representational question at all). Also cross-checked against the
same-day, independently-filed `notes/research_crutch_fade_loop_owned_organ_wiring_2026-08-10.md`
(DRILL 3, owned-organ wiring audit rather than brain-fidelity audit) -- that note independently
confirms `grounding_acquisition_loop.py`/`script_grain_acquisition_loop.py` are TOTAL invisible
islands (zero registry rows, zero experiment-cell consumers) as of a fresh
`capability_registry_audit.py` run, and independently flags the flat-dict BANK target as the wrong
destination -- convergent evidence from two different audit methods (brain-fidelity-first here,
registry/wiring-first there) on the same structural gap. DRILL 3's Section "THE STORE" additionally
names `hdlab/hd_fact_store.py` (source-trust-vetted, CERT/chain-grade) as the un-pointed-at correct
destination for BANK output, which this drill's section 4/HEADLINE independently arrives at needing
(a distributed, natively-read structure the crutch can migrate INTO) without knowing that organ
already existed -- the two drills' findings compose directly: DRILL 3 supplies the WHERE (wire BANK
to `hd_fact_store` instead of the flat dict), this drill supplies the WHAT-CURVE (trust/reliance
should follow a power-law/exponential fade keyed on trace-count and mapping-consistency, per
section 4) and the falsifiable test to confirm the substrate's own geometry supports it (Test A).

## Substrate-product implications

If Test A clears HARD-PASS, the substrate gains a genuine, measurable, literature-grounded claim
that would not otherwise be available to a black-box embedding system: not just "the substrate
learned this word" but "the substrate's reliance on the explicit acquisition record for this word
is DECREASING at a rate the human automaticity literature predicts, and here is the exposure-count/
consistency curve that shows it" -- a fully auditable fade trajectory, per-item, rather than a
binary learned/not-learned flag. This is the missing piece that would let "grounding grows and the
crutch becomes unnecessary" become a literal, inspectable, falsifiable substrate property instead
of a design metaphor -- directly extending the "comprehension is a growing library of construction
competencies" framing (each competency's OWN fade curve becomes a first-class observable) and
giving the auditability differentiator (this project's whole positioning) a genuinely new axis: not
just "why did it decide this" but "how much is it still relying on scaffolding for this, and is
that reliance shrinking the way a human learner's would."

## Calibration (per [[feedback-lit-scan-calibration-penalty]])

The FLAG multi-system account (ACC/EVC, hippocampal comparator, metacognitive monitor-control) is
HIGH confidence as neuroscience -- each system individually is well-established, field-consensus
literature (Botvinick/Shenhav, Kumaran/Maguire, Nelson/Narens/Koriat). The FADE literature (Fitts &
Posner, Logan, Newell & Rosenbloom, Schneider & Shiffrin, Wood/Bruner/Ross) is similarly HIGH
confidence as neuroscience/psychology -- these are foundational, heavily-replicated, textbook
results, not fringe or single-study claims. What is NOT established, and where the calibration
penalty applies, is the SUBSTRATE-SPECIFIC synthesis: whether this project's particular
distributional/similarity geometry (the base codebook `verb_lexical_similarity` scorer) actually
organizes acquired-item neighborhoods the way human lexical-semantic memory does, which is exactly
what Test A measures and could genuinely fail. No literature precedent exists for "measure native-
pathway coverage of an acquired item as a proxy for automaticity progress" as a combination --
this is this project's own operationalization of Logan's instance theory, not a literature-
precedented experimental design. P(Test A clears HARD-PASS as specified) is capped at 0.50 per the
novel-synthesis rule and further deflated to **~0.35**: positive factors are that BOTH predictor
quantities (`_vote_margin`, trace count) already exist in the codebase with zero new build required
to compute them, and the base similarity scorer is itself an already-certified organ (no new
mechanism risk); negative factor is genuine uncertainty about whether THIS substrate's specific
codebook geometry places acquired-verb neighborhoods close enough to base-verb neighborhoods for
"native coverage" to ever fire at all, independent of the psychology being right -- a real,
substrate-native failure mode the psychology literature cannot predict.

## Citations (verified count = 11 WebSearch queries this session, 15 distinct NEW citations)

**New this drill:** Botvinick, Cohen & Carter 2001/2004 (*Trends Cogn Sci* 8(12), conflict
monitoring, update); Shenhav, Botvinick & Cohen 2013, *Neuron* 79(2):217-240 (Expected Value of
Control); Kumaran & Maguire 2007, *J Neurosci* 27(32):8517 (hippocampal match-mismatch, associative
novelty); Nelson & Narens 1990 (metacognition monitoring-control framework); Koriat 1997,
*JEP:General* 126:349-370 (cue-utilization judgments of learning); Fitts & Posner 1967, *Human
Performance* (Brooks/Cole, 3-stage skill acquisition); Newell & Rosenbloom 1981 (power law of
practice, cross-domain synthesis); Heathcote, Brown & Mewhort 2000, *Psychonomic Bulletin & Review*
7 (exponential-law critique, cited as the contested-mechanism counterpoint); Rickard 1997 (CMPL
strategy-shift account); Logan 1988, *Psychol Rev* 95(4) (Instance Theory of Automaticity); Logan
1992, *JEP:LMC* (empirical test); Schneider & Shiffrin 1977, *Psychol Rev* 84(1); Shiffrin &
Schneider 1977, *Psychol Rev* 84(2); Wood, Bruner & Ross 1976, *J Child Psychol Psychiatry* 17(2)
(origin of "scaffolding," block-pyramid tutoring study); Xu & Tenenbaum 2007, *Psychol Rev* 114(2)
(Bayesian word learning, suspicious-coincidence / sampling-assumption effect).

**Carried forward** (already verified in the 08-09/07-28/06-22 sister drills, not re-verified this
session): Dumay & Gaskell 2007; Tamminen et al. 2010; Tse et al. 2007/2011; van Kesteren et al.
2012 (SLIMM); McClelland 2013; Warren et al. 2014; Ghosh & Gilboa 2014; Preston & Eichenbaum 2013;
Perfors & Tenenbaum 2009 (MDL, already in-repo); Kumaran, Hassabis & McClelland 2016; Bower, Black
& Turner 1979; Carey & Bartlett 1978; Franklin, Norman, Ranganath, Zacks & Gershman 2020 (SEM);
Reynolds, Zacks & Braver 2007; Baldwin et al. 2008; Stahl et al. 2014; McClelland, McNaughton &
O'Reilly 1995; Marr 1971; Wilson & McNaughton 1994; Buzsaki 1989/2015; Diba & Buzsaki 2007.
