# Research: brain learning efficiency + language acquisition + substrate lever-map

**Date:** 2026-07-17. Director drill (biology-led, safe generic-term internet research, USER-requested deep drill).
**Method:** 4 parallel Sonnet lit-scan sub-agents (efficiency levers / active-curiosity+replay / compositional-reuse
+ continual-learning / language-acquisition), synthesized by the director against existing internal findings
(`research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md`, `research_surprise_decomposition_...
2026-07-16.md`, `research_importance_correct_function_retrieval_vs_active_learning_2026-07-16.md`,
`research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md`,
`research_vsa_hdc_state_of_mind_prior_art_scour_2026-07-17.md`, the 07-17 broad-parser arc). Generic neuroscience/ML
terms only in external queries per query-privacy discipline; no substrate-novel names or numbers went off-platform.
Lit-scan calibration penalty applied throughout (deflate 0.15-0.25; novel-synthesis P capped at 0.50).

---

## HEADLINE

**None of the four brain-efficiency levers researched here are foreign to this project — three of the four
(predictive-error scoring, schema-fit gating, statistical/entrenchment recurrence) are ALREADY BUILT, VET-confirmed,
glass-box primitives on the substrate (`additive_map.score_all`, `reachability_audit.schema_fit`, a recurrence-count
floor), independently converged on by this project's own 07-15/07-16 drills before this literature scan even ran —
meaning the substrate's design instinct already tracks real neuroscience without having been told to. The fourth
lever, active/curious data-selection (Gottlieb-Oudeyer "learning progress" / Schmidhuber "compression progress"),
was ALSO already tried on this substrate as an ingest-ORDER signal and HARD_FAILED — and the literature explains
the failure exactly: naive centrality-greedy active selection without a diversity/redundancy correction is a
textbook anti-pattern in active learning, not evidence the signal is inert. The single cheapest, most decisive
un-run test this drill surfaces is re-running the FALSIFIED prioritized-replay cell (R7, wave14c) with the NOW-
available closed-loop surprise signal instead of the collapsed static Hebbian tag it originally used — this
directly mirrors the literature's own controlled demonstration (Schaul et al.'s Prioritized Experience Replay
beating uniform replay on 41/49 Atari games specifically because it re-weights by a closed-loop TD-error, not a
static tag) and is a near-zero-new-code experiment. P_deflated(the substrate-mapping synthesis in Part 3 is a valid,
actionable next-build program) = 0.45 (capped under novel-synthesis ceiling).**

---

# PART 1 — Why biological learning is so much more data/energy-efficient than brute-force LLM training

*(Full lit-scan detail from 4 sub-agents condensed; confidence tags per claim: ESTABLISHED / WELL-SUPPORTED /
CONTESTED / SPECULATIVE, as returned by the sub-agents.)*

### 1.1 Sparse coding (ESTABLISHED mechanism, WELL-SUPPORTED efficiency claim)
Barlow's 1961 efficient-coding hypothesis (redundancy reduction, metabolically-cheap spikes) → Olshausen & Field
1996 (*Nature* 381:607-609): an overcomplete dictionary + sparsity penalty on natural image patches reproduces
V1-like oriented receptive fields with NO hand-coded edge prior. Sparse, near-independent codes need fewer examples
per learned association than dense/entangled codes (WELL-SUPPORTED analogy to compressed sensing: Candès/Donoho-era
results that sparse signals need far fewer measurements than ambient dimensionality) and are more robust to
interference (standard associative-memory theory).

### 1.2 Predictive coding (ESTABLISHED landmark models, CONTESTED as literal brain-wide mechanism)
Rao & Ballard 1999 (*Nat. Neurosci.* 2:79-87): each cortical level predicts the level below; feedforward carries
only the RESIDUAL (prediction error), not raw signal — reproduces V1 simple cells AND real extra-classical
receptive-field effects (end-stopping). Friston 2010 (*Nat. Rev. Neurosci.* 11:127-138) generalizes to active
inference / free-energy minimization — influential but explicitly debated in the same literature (WELL-SUPPORTED
as unifying framework, CONTESTED as sharply falsifiable theory). Computationally: only the unexplained residual
needs to propagate and drive learning — the intuitive core of why the brain doesn't "reprocess everything."

### 1.3 Brain vs LLM energy/data numbers (ESTABLISHED order-of-magnitude; WELL-SUPPORTED specific estimates)
Attwell & Laughlin 2001 (*JCBFM* 21:1133-1145): cortical grey-matter signaling energy budget (~47% spikes, ~34%
postsynaptic currents). A more recent estimate (Levy & Calvert, PNAS ~2021) finds cortical *communication*
(wiring) costs ~35x more than raw computation — most of the brain's cognitive energy tax is data movement, not
math, which is itself an interesting point of DISANALOGY with GPUs (GPUs also pay a data-movement tax — the von
Neumann bottleneck — so this may be a shared, not brain-unique, efficiency problem). GPT-3-class training energy
estimates run to ~1,000+ MWh (industry estimates, not first-party disclosures — CONTESTED in precision, not in
order of magnitude) vs ~20W whole-brain. Sample efficiency: Hart & Risley 1995 word-gap estimates (~13-45M words
by age 3) vs the BabyLM Challenge's explicit "developmentally plausible" ceiling of ≤100M words (Warstadt et al.,
2023/2025 findings papers) vs LLM pretraining corpora of hundreds of billions to trillions of tokens — a 3-4
order-of-magnitude gap that is the explicit design premise of the BabyLM benchmark itself.

### 1.4 Active/curious self-directed learning (WELL-SUPPORTED behavioral + theoretical)
Kidd, Piantadosi & Aslin 2012 (PLoS ONE, "Goldilocks Effect"): infants attend most to intermediate-complexity/
intermediate-predictability stimuli relative to their OWN current model — not maximal novelty, not minimal.
Gottlieb, Oudeyer, Lopes & Baranes 2013 (*TiCS*) integrate this into a "learning progress" account: intrinsic
reward = rate of improvement in one's own predictive model, not absolute error or absolute novelty. Schmidhuber's
formal theory of curiosity (~1990-2010, "Driven by Compression Progress") is the direct ML-side formalization:
intrinsic reward = first derivative of compression/prediction quality, which reproduces the Goldilocks zone as a
corollary. Gureckis & Markant 2012 cite active-learning results reaching equivalent accuracy with roughly an order
of magnitude less data than passive/random sampling.

### 1.5 Replay + offline consolidation (ESTABLISHED biology; ESTABLISHED ML analog)
Wilson & McNaughton 1994 (Science): hippocampal place-cell reactivation during sleep. Foster & Wilson 2006
(Nature): REVERSE awake replay, suited to backward credit assignment. Carr, Jadhav & Frank 2011 (*Nat. Neurosci.*
review): awake-state replay as consolidation+retrieval substrate. Multiple lines (PNAS/Nat. Comms-adjacent papers
on reward-prediction-error-biased replay) show replay content is prioritized, not uniform — CONTESTED in exact
mechanistic detail (a 2024 Farooq & Dragoi *Science* paper found intrinsic population-manifold dynamics predict
sleep-replay content even after controlling for novelty/reward — a genuine open tension, not settled). ML analog:
Lin 1992 introduced experience replay; Mnih et al. 2015 (DQN, *Nature*) showed disabling it severely degrades
performance (load-bearing, not cosmetic); Schaul et al. 2015/2016 (Prioritized Experience Replay) showed
TD-error-weighted replay beats uniform replay on 41/49 Atari games — the most directly quantified analog available
for "prioritizing WHAT gets re-trained on by an error/salience signal."

### 1.6 Compositional/factorized representations + reuse (WELL-SUPPORTED research program; CONTESTED strong claim)
Fodor & Pylyshyn 1988 (*Cognition*): systematicity/productivity argument — "infinite use of finite means." Lake,
Ullman, Tenenbaum & Gershman 2017 (*BBS* 40:e253): compositionality + causality + learning-to-learn as what's
missing from standard deep nets; their Bayesian Program Learning demonstration (Lake, Salakhutdinov & Tenenbaum
2015, *Science*) reaches human-level one-shot Omniglot classification via reusable stroke-primitives, vs deep nets
needing hundreds of examples per class. Tse et al. 2007 (*Science* 316:76-82): once a schema exists, a SINGLE new
schema-consistent trial consolidates in ~24-48h instead of weeks. Van Kesteren et al. 2012 (SLIMM model, *TiCS*):
schema-congruent info encoded faster, mediated by mPFC gating hippocampal engagement.

### 1.7 Continual learning without catastrophic forgetting (ESTABLISHED problem + theory; WELL-SUPPORTED ML analog)
McCloskey & Cohen 1989: original catastrophic-interference demonstration. McClelland, McNaughton & O'Reilly 1995
(*Psych. Rev.*) — Complementary Learning Systems: hippocampus fast/sparse/pattern-separated one-shot write,
neocortex slow/distributed/interleaved-replay learner; the DUAL architecture (not either system alone) is what
avoids catastrophic interference. Kumaran, Hassabis & McClelland 2016 (*TiCS*) update this and explicitly tie it
to deep-RL experience replay. Kirkpatrick et al. 2017 (Elastic Weight Consolidation, *PNAS*) is the direct
single-network ML analog — WELL-SUPPORTED but honestly only a partial fix (reported forgetting-reduction in the
45-90% range depending on benchmark, not full elimination), suggesting biology's ARCHITECTURAL separation
(two systems) does real work beyond what a same-network regularization penalty can replicate.

### 1.8 Top-5 ranked efficiency principles (sub-agent synthesis, explicitly flagged as own-judgment, not consensus)
1. Architectural/innate priors constraining the hypothesis space before data arrives.
2. Active/curious data curation (effective info-per-sample >> passive i.i.d. sampling).
3. Predictive coding / error-only propagation (spend resources only on the unexplained residual).
4. Sparse, event-driven, in-memory-adjacent computation (partially offset by real communication/wiring costs).
5. Local, biologically-plausible learning rules vs global backprop (SPECULATIVE as a full quantitative account —
   ML's biologically-plausible-backprop alternatives have not yet closed the efficiency gap they're meant to explain).

---

# PART 2 — How language is acquired, and how it reuses the general-purpose machinery from Part 1

### 2.1 Statistical/distributional learning (ESTABLISHED)
Saffran, Aslin & Newport 1996 (*Science* 274:1926-1928): 8-month-olds segment a continuous, cue-free synthetic
speech stream purely via transitional-probability tracking between syllables — no reinforcement, no semantics.
Generalizes across modalities (tones, shapes), suggesting a domain-general sequence-statistics learner that
language acquisition simply recruits — the direct intellectual ancestor of modern distributional semantics
("you shall know a word by the company it keeps," Firth 1957).

### 2.2 Prediction-based learning + surprisal (WELL-SUPPORTED to ESTABLISHED, per-claim)
Hale 2001 + Levy 2008 (*Cognition* 106:1126-1177): word-by-word processing difficulty ∝ −log P(word | context) —
literally a next-word-prediction quantity, decades before GPT-style LMs, extensively validated against reading-time
and eye-tracking data. Kutas & Hillyard 1980 (*Science*): the N400 ERP component — a neural signature of
prediction-violation during comprehension (CONTESTED whether it's "prediction" per se vs generalized semantic
integration — a live debate). Elman 1990 (*Cognitive Science* 14:179-211): a Simple Recurrent Network trained
PURELY to predict the next word spontaneously organizes hidden units by lexical category and captures long-distance
agreement — next-word prediction as a self-supervised structure-inducing signal, proposed and demonstrated in
cognitive science ~30 years before modern LLMs, for the explicit purpose of modeling human processing/acquisition
rather than building a general system. This is the single cleanest "GPT's core training objective predates GPT by
three decades, and was invented to explain children, not to build a product" fact in this whole drill.

### 2.3 Usage-based / construction grammar (WELL-SUPPORTED research program; CONTESTED vs nativism)
Tomasello 2003 ("Constructing a Language"): children build grammar bottom-up from concrete exemplars ("verb
islands") via three domain-general mechanisms — ENTRENCHMENT (repeated exposure to a specific pairing strengthens
its expectation, explaining pre-emption of overgeneralization), ANALOGY across surface-similar exemplars, and
gradual SCHEMA ABSTRACTION into slot-and-frame templates. Goldberg's Construction Grammar (1995/2006) is the
grammatical-theory counterpart: form-meaning constructions, not derivations from an abstract innate syntax module,
are the basic unit. Ambridge & Lieven 2011 is the standard synthesis weighing this against nativist accounts.
Marcus et al. 1992 (overregularization monograph, ~11,500 utterances/83 children): overregularization ("goed") is
RARE (~2.5% of opportunities), constant-rate, and preceded by correct irregular usage — diagnostic of a productive
default rule extracted on top of memorized exemplars, exactly the "abstraction atop stored exemplars" signature the
schema-formation story predicts (though Marcus/Pinker themselves argue this for a dual rule+lexicon mechanism, not
a purely usage-based one — CONTESTED interpretation of the same data).

### 2.4 Grounding + social interaction (WELL-SUPPORTED, largely non-contentious)
Baldwin 1991 (*Child Development*): infants map a novel word onto the object the SPEAKER is looking at, not the
object of their own current attention — joint-attention/gaze-following constrains reference beyond pure
co-occurrence statistics. Virtually all theoretical camps accept social-pragmatic cues meaningfully constrain
word-to-referent mapping.

### 2.5 Developmental trajectory (ESTABLISHED as description)
Babbling (~6-10mo) → first words (~12mo) → vocabulary spurt → two-word/telegraphic (~18-24mo) → rapid grammatical
development with overregularization (2-4yr).

### 2.6 Domain-general vs a special language module (CONTESTED — explicit flag, not adjudicated)
Statistical/predictive/social learning mechanisms are each independently domain-general (seen outside language too).
The usage-based program argues NO innate language-specific module is needed. The generative/nativist tradition
(Chomsky, Pinker) argues some innate linguistic structure is still required to explain acquisition speed/uniformity/
poverty-of-the-stimulus. This is a genuinely live, unresolved debate — not something this drill adjudicates.

---

# PART 3 — Substrate lever-map (load-bearing section)

Legend: **HAVE** = a VET-confirmed or at-least-tried substrate primitive exists. **PARTIAL** = tried, mixed/weak
result, or design-only/pending pilot. **MISSING** = no substrate primitive attempts this yet, real gap.

| Brain/ML principle (Part 1-2) | Substrate status | Evidence / file |
|---|---|---|
| Predictive coding / prediction-error-as-learning-signal (§1.2); surprisal (§2.2) | **HAVE — strong** | `hdlab/additive_map.py` `score_all` → `surprise = 1 − reciprocal_rank(true_target)`. VET-confirmed HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE, held-out MRR 0.1282 (284x random ceiling). This is a genuine closed-loop prediction-error metric already recomputed against the CURRENT fitted foundation each cycle — matches the literature's universal finding that closed-loop signals beat static tags. |
| Schema-consistent fast learning (§1.6, Tse/SLIMM) | **HAVE — strong** | `hdlab/reachability_audit.py` `schema_fit` (k-hop reachable mass, hub distance) + `compose_entity` (zero-training mean of support-edge displacement vectors = schema-based slot-filling). Directly maps to Tse 2007/McClelland 2013's "schema changes the RULE for future fast learning," not just what's known. |
| Statistical/distributional recurrence (§2.1, Saffran) + entrenchment (§2.3, Tomasello) | **HAVE — strong, as a gate; entrenchment-for-parsing is a live 07-17 arc** | `recurrence_count` floor in the 3-signal ingest gate; separately, the current broad-parser program explicitly frames construction-inventory growth as ENTRENCHMENT (surprisal uses it) — a direct, already-in-flight Tomasello mapping, not a new idea to build. |
| Sparse/decorrelated coding (§1.1, Olshausen-Field/Barlow) | **HAVE — structural**, not separately re-tested this cycle | BSC/FHRR bipolar/phase codes are inherently high-dimensional and (per the resolved decorrelation fair-test thread) already characterized for interference/crosstalk behavior. This is a pre-existing structural property of the substrate's representation, not a new build — flagged here as a genuine but UNSURPRISING match (the substrate was built VSA-style for other reasons; sparse-coding parallels are real but were not the design motivation). |
| Compositional/structured representations + reuse (§1.6, Lake/BPL; Fodor-Pylyshyn) | **HAVE — partial** | Bind/bundle/resonator + block-local frame-slot decoder (Levelt-style production, HARD_PASS exact-ordered 1.000) is real compositional reuse. TEM content-conditioned relation transform (structure x content factorization) is MIDDLE_BAND — genuine but small (0.05-0.13) transfer to novel combinations, not yet BPL-level one-shot generalization to genuinely NEW primitives (see MISSING row below). |
| CLS fast/slow dual-store, no catastrophic forgetting (§1.7) | **PARTIAL — architecture attempted, HARD_FAILED as literally implemented; a properly-CLS-shaped fix is DESIGNED but not yet piloted** | `exp_two_substrate_fastslow_cls...` HARD_FAILED (both arms below gate, recall 0.689/0.378, seed-robust). But the 07-15 ingest-gate note's full consolidation-loop design (provisional fast tier → offline interleaved-replay-regularized consolidation → foundationalize fast/slow-track by schema-fit) is a properly CLS-shaped redesign, cheap to pilot, not yet run. Per the standing "brain-check every negative" discipline: the HARD_FAIL is the McCloskey-Cohen failure mode (a single shared store), not evidence the CLS *principle* fails here — the fix the biology prescribes (real architectural separation + interleaving, not just a second W matrix) hasn't been tried yet in its full form. |
| Active/curious data-selection, "learning progress" (§1.4, Gottlieb-Oudeyer/Schmidhuber) | **PARTIAL — tried as ingest-ORDER, HARD_FAILED; literature explains the failure; correct locus untested** | `exp_importance_downstream_reach_ingest_prioritization_real_codex_v1` HARD_FAILED (`beats_both: false`) as a foundation-growth-ORDER signal, despite the underlying importance signal being real and popularity-decorrelated (`separability_tier: SEPARABLE`). The 07-16 follow-up note independently found the literature explanation: naive centrality-greedy active selection without a diversity/redundancy correction is a well-documented anti-pattern (matches Gureckis & Markant's active-learning caveats) — this is a brain-check success, not a dead end: same failure shape the ML active-learning literature already catalogs. The recommended correct locus (retrieval/attention-time value-weighting, not acquisition-order) is specified but UNTESTED. |
| Replay + offline consolidation (§1.5) | **PARTIAL — replay exists as an anti-interference/projection regularizer; PRIORITIZED replay by a real closed-loop signal is untested** | wave14c confirmed replay's mechanism on this substrate is projection/subspace-regularization, not literal rehearsal. A STATIC structural-tag priority scheme for replay selection (R7) was FALSIFIED (-0.53 bpc vs random) — but R7's tag was a collapsed rank-1 Hebbian MIR score, structurally different from the now-available closed-loop `score_all` surprise metric. This is the single most literature-mirrored untested lever (see Cheap Decisive Test below — directly parallels Schaul et al.'s PER-vs-uniform-replay ablation). |
| Hippocampal one-shot pattern-separated write, no-interference storage | **HAVE — strong** | Index-protected binding: hub recall 0.261→0.727 (+0.466), independently matching Clarkson-Ubaru-Yang hub-punishment theory. |
| CA3 regenerative/attractor cleanup vs analog accumulation | **HAVE — strong** | Digital-repeater cleanup ≈0.70 vs analog-accumulate ≈0.10 at reasoning depth 5, gap widening with load. |
| Retrieval/attention-time value-weighting (the 4th "importance" axis at its correct locus, §1.4 reframed) | **MISSING — specified, not built** | Recommended by the 07-16 note as the correct hypothesis (mechanistically distinct from acquisition-order): reuse the existing fitted resolvent/importance machinery against the held-out set AS a retrieval-relevance ground truth. Near-zero new compute; simply not yet run. |
| Genuine schema/primitive ABSTRACTION (Lake's BPL: learning NEW reusable primitives, not just recombining existing relation types) | **MISSING — real gap** | `compose_entity` recombines EXISTING relation types via linear mean; nothing yet mines NEW reusable structural motifs from recurring patterns the way BPL's stroke-library grows. Matches the memory-log's own "schema-formation / structural generalization = MISSING / open frontier" line (schema_ablation FULL 12-arm HARD_FAIL, but with a vacuous comparison-axis control — untested, not refuted). |
| Basal-ganglia-style trained Go/NoGo gate driven by a real RPE signal | **MISSING** | PFC-BG goal-gate and BG-analog conflict-op both exist as MIDDLE_BAND/weak (+0.04-0.06 lift); the missing piece per the 07-05 inventory is training them with the substrate's OWN existing cfrpe signal — an existing-primitive-composition task, not a new mechanism, already flagged and not yet done. |
| Grounding via joint attention / shared intentionality (§2.4, Baldwin/Tomasello) | **MISSING — genuinely hard to build without embodiment/exogenous referents** | No current substrate analog of "the speaker's gaze constrains reference." The closest available proxy would be exogenous query-relevance (an external task/user signal) as a stand-in for "what the interlocutor is attending to" — this is speculative and un-piloted; flagged in prior memory as the parked "grounding-needs-exogenous-referent" thread. If the platform expands to a modality with a real external referent (vision, per the 07-17 platform-expansion note), this gap becomes directly addressable; until then it stays MISSING with no clear text-only fix. |
| A unified formal combination rule across schema-fit + surprise + recurrence + importance (4 axes into 1 gate) | **MISSING — but so is the biology's** | Both the 07-15 lit-scan (schema-fit/surprise/recurrence) and independently the two other lit-scans in this cycle confirm NO paper anywhere gives a quantitative combination formula across these signals — three separate anatomical circuits, no single brain algorithm unifies them. Our current gate (a decision tree, not a weighted sum) is therefore a genuine, honestly-labeled NEW proposal informed by, not copied from, biology — it needs its own pilot (07-15 note Section 6), not a literature answer that doesn't exist. |
| Literal energy/joules efficiency (spikes vs matmul, in-memory computing) | **OUT OF SCOPE, flagged not pursued** | The substrate runs on conventional GPU/CPU von Neumann hardware; chasing joule-for-joule parity with biological spiking is not a meaningful lever here (per the project's own Frontier-1-vs-Frontier-2 distinction, this is exactly a case where the brain solves a problem — physical energy scarcity — the substrate doesn't have). The efficiency that DOES transfer and matters is algorithmic/SAMPLE efficiency (fewer examples per generalization) plus transparency (glass-box auditability) — explicitly re-scoped here so this synthesis doesn't chase an irrelevant metric. |

## Buildable program (ranked, cheapest/most-decisive first)

1. **Re-run the falsified prioritized-replay cell (R7) using the closed-loop `score_all` surprise signal** instead
   of the collapsed static Hebbian-MIR tag. Directly mirrors Schaul et al.'s PER-vs-uniform ablation. Near-zero new
   code (both signal and replay infra already exist). **This is the cheap decisive test — see below.**
2. **Pilot the full 3-signal ingest-gate / consolidation-loop** (07-15 note, Sections 3-6) end-to-end on real data —
   closes the CLS "partial, in-design" row with an actual measurement instead of an architecture argument.
3. **Test retrieval/attention-time value-weighting** (07-16 note's recommended hypothesis-a cell) — reuses existing
   resolvent/importance machinery against a held-out set as ground truth; resolves whether "importance" is dead or
   just mis-located.
4. **Continue the in-flight entrenchment+surprisal parser arc** (07-17) — this is already the most directly-mapped
   Tomasello-style rung and needs no new justification from this drill, only continuation.
5. **Build the discourse "state-of-mind" overlay** using the already-scoured VSA prior art (Eliasmith SPA gated
   integrator, Choo OSE item-position accumulation) — frame explicitly as the substrate's analog of the
   developmental jump from single-construction mastery to multi-utterance discourse tracking (situation
   models/Centering Theory), matching the roadmap's own next-rung ordering.
6. **(Bigger lift, stage after 1-3)** A genuine schema/primitive-ABSTRACTION mechanism — mining NEW reusable
   structural motifs from recurring patterns, not just recombining existing relation types via `compose_entity`.
   This is the real BPL-level gap and the honest answer to "what's missing that's hard," not a quick win.
7. **(Speculative, parked)** grounding via an exogenous referent — no concrete plan until/unless the platform
   gains a genuine external-referent modality.

---

## Cheap decisive test

**Re-run the wave14c/R7 prioritized-replay cell, replacing its static Hebbian-MIR priority tag with the existing,
already-VET-confirmed closed-loop surprise score (`additive_map.score_all` → `1 − reciprocal_rank`).** All
components (replay infrastructure, surprise scoring function) already exist and are independently VET-confirmed;
this is a wiring change, not a new mechanism, and directly tests whether R7's failure was signal-specific (a
collapsed/redundant tag) or architecture-general (this substrate's rank-1 Hebbian update rule can't benefit from
ANY replay-priority signal).

**HARD-PASS:** closed-loop-surprise-prioritized replay beats random-replay baseline by a pre-registered margin
(≥0.10 bpc-equivalent improvement, or the cell's native metric) on ≥2/3 seeds. This would validate that R7's
collapse was implementation-specific (wrong signal), matching the literature's own finding that TD-error/prediction-
error-weighted replay outperforms uniform replay (Schaul et al., 41/49 games) — and license building the full
prioritized-consolidation pipeline (buildable-program item 2).

**HARD-FAIL:** closed-loop-surprise-prioritized replay ties or underperforms random replay (delta ≤ 0, or within
noise) on ≥2/3 seeds. Per the standing brain-check discipline, this would NOT be shrugged off — it would mean this
substrate's rank-1 Hebbian delta-rule structurally cannot benefit from ANY priority-tag replay (a real architectural
wall, not a signal-choice bug), and the correct next step would be to check whether biological synaptic plasticity
has a structural feature ours lacks (e.g., eligibility traces / multi-factor three-term plasticity rules — dopamine-
gated STDP is not a simple Hebbian product) that is PRECISELY what makes biological prioritized replay work where a
naive substrate rank-1 rule might not.

---

## Falsifiable predictions (secondary, lower-priority than the cheap decisive test above)

1. **Retrieval-time value-weighting** (buildable item 3): HARD-PASS if reusing existing importance/resolvent
   machinery against a held-out set as a retrieval-relevance ground truth beats a recency/frequency-only baseline
   by a pre-registered margin on ≥2/3 seeds; HARD-FAIL if it does not — in which case the "importance" 4th-axis
   signal should be provisionally deprioritized (not discarded — one more brain-check: is our "value" proxy
   actually analogous to reward/goal-relevance, or just centrality-in-disguise, which would explain a second
   failure the same way the first one was explained).
2. **CLS consolidation-loop pilot** (buildable item 2): HARD-PASS if the fast-provisional/slow-interleaved
   two-track routing (Section 3-4 of the 07-15 note) beats BOTH the single-store baseline AND the already-tried
   naive dual-W (`two_substrate_fastslow_cls`) on recall with no-interference, on ≥2/3 seeds; HARD-FAIL if it does
   not beat the naive dual-W attempt, which would suggest the missing ingredient is genuinely the INTERLEAVED-REPLAY
   half of CLS (not yet tried in combination with the dual-store), not the store-separation half (already tried
   and failed alone).

---

## Cross-thread synthesis

This drill's central finding is convergence, not novelty: the 07-15 ingest-gate note (schema-fit/surprise/
recurrence, built and VET-confirmed BEFORE this literature scan ran) and the 07-16 importance/active-learning notes
(the 4th-axis "learning progress" signal, tried and HARD_FAILED at the wrong locus) independently anticipated
almost exactly the four-lever structure this scan's four sub-agents found in the outside literature, without having
been told what the literature says. That is a meaningful cross-check in the substrate's favor: the project's own
brain-first design instinct is tracking real neuroscience, not inventing brain-flavored language for arbitrary
engineering choices. The one place this drill adds genuinely new information is the DQN/PER precedent (§1.5) — a
concrete, quantified ML demonstration that a closed-loop error-weighted replay signal beats a static one — which
gives the R7-retry (buildable item 1) a specific, literature-grounded reason to expect success where R7 itself
failed, rather than just "try it again with a different score." It also connects the in-flight 07-17 broad-parser
arc (entrenchment grows the construction inventory, surprisal uses it) explicitly to Tomasello's usage-based
acquisition account for the first time in this project's own language — the parser program was already doing this,
now it has an explicit, citable theoretical home.

## Substrate-product implications

The product-relevant framing (per no-papers-product-only discipline): an auditable AI-memory/reasoning substrate's
core value proposition is TRANSPARENT, inspectable learning — a customer can ask "why did this fact get
consolidated / why was this retrieved first" and get a real, glass-box, decision-tree answer (schema-fit, surprise,
recurrence, each independently computed and loggable), not a black-box gradient. This drill's finding that the
brain itself uses three-to-four SEPARATE, non-unified signals rather than one opaque combined score is actually a
point in the substrate's favor for that pitch: an explicit, inspectable decision tree across named criteria is not
a simplification of how intelligent memory works, it is a reasonably faithful (if novel) formalization of it. The
sample-efficiency angle (BabyLM's 100M-word ceiling vs trillion-token LLM training) is a legitimate, literature-
backed reason to expect that composition + schema-reuse + prioritized consolidation, done right, could let a
glass-box substrate reach useful generalization from far less ingested data than a comparably-capable black-box
model — this is a hypothesis this program is actively testing (items 1-3 above), not yet a proven product claim.

## Citations (verified count)

Approximately 49 distinct named papers/reviews cited across the 4 external lit-scan sub-agents plus the 07-15/07-16
internal notes drawn on for cross-synthesis (Barlow 1961; Olshausen & Field 1996; Rao & Ballard 1999; Friston 2010;
Attwell & Laughlin 2001; Levy & Calvert ~2021; Hart & Risley 1995; BabyLM Challenge findings 2023/2025; Lan et al.
poverty-of-stimulus; Kidd/Piantadosi/Aslin 2012; Gottlieb/Oudeyer/Lopes/Baranes 2013; Gureckis & Markant 2012;
Schmidhuber ~1990-2010; Wilson & McNaughton 1994; Foster & Wilson 2006; Carr/Jadhav/Frank 2011; Farooq & Dragoi
2024; Born & Wilhelm ~2012; Lin 1992; Mnih et al. 2015; Schaul et al. 2015/2016; Fodor & Pylyshyn 1988; Lake/Ullman/
Tenenbaum/Gershman 2017; Lake/Salakhutdinov/Tenenbaum 2015; Tse et al. 2007/2011; van Kesteren et al. 2012;
McClelland/McNaughton/O'Reilly 1995; McClelland 2013; Kumaran/Hassabis/McClelland 2016; McCloskey & Cohen 1989;
French 1999; Kirkpatrick et al. 2017; Saffran/Aslin/Newport 1996; Hale 2001; Levy 2008; Kutas & Hillyard 1980;
Federmeier 2007; Elman 1990; Baldwin 1991; Marcus et al. 1992; Tomasello 2003; Goldberg 1995/2006; Ambridge &
Lieven 2011; Lisman & Grace 2005; Duszkiewicz et al. 2019; Schapiro & Turk-Browne 2017; Takeuchi et al. 2016;
Anderson/Laurent/Yantis 2011; Fecteau & Munoz 2006; Klink/Jentgens/Lorteije 2014). These are named/attributed by
the sub-agents with reasonable-confidence author/year/venue; NOT independently cross-checked against publisher
records by the director in this cycle (standard lit-scan caveat — treat exact years/volume numbers as
approximate where a sub-agent hedged with "approximately").

**Confidence discipline applied:** per-claim ESTABLISHED/WELL-SUPPORTED/CONTESTED/SPECULATIVE tags preserved from
the sub-agent reports rather than flattened into one blanket confidence number. Overall P_deflated for the
substrate lever-map (Part 3) = **0.45** (novel-synthesis cap 0.50, further trimmed given several rows depend on
an un-piloted design, not yet a measurement).
