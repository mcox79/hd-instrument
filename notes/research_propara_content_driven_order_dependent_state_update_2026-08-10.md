# Research drill: content-driven, order-dependent entity-state update for ARM-1 (ProPara)

Filed by: research (Sonnet). Trigger: task input drill on ARM-1 ProPara result
(`data/exp_propara_decisive_inference_arm1_oracle_v1/metrics.json`, DISK-VET'd) -- reasoning arm
wins the official metric (+0.306 F1) and the FOCUS proxy (natural_focus_margin=0.1365 fixed across
seeds) but scramble control shows the win is MOSTLY order-invariant structural prior (oracle
event-count multiset + index monotonicity), not content-based comprehension: only seed7 collapses
cleanly (retained_frac=0.401, HARD_PASS); seed17 (1.056) and seed29 (0.897) barely move at all.

Kept scope narrow per task: brain mechanism -> fidelity-divergence diagnosis of the loop as it
literally exists in `experiments/exp_focus_pullin_causal_stage2a_multihop_loop_v1.py` (organ) /
`exp_propara_decisive_inference_arm1_oracle_v1.py` (caller) -> one concrete testable improvement
-> complementary control. 3 parallel Sonnet lit-scan sub-agents dispatched (event segmentation /
situation-model incremental update / procedural-text NLP precedent); findings integrated below.

## HEADLINE

**The ARM-1 loop's VALIDATE step is content-blind by construction** -- it enforces
CREATE-index < MOVE-window < DESTROY-index as a pure arithmetic constraint on step POSITIONS,
identical regardless of what text sits at each position, while the RETRIEVE step is a single-step,
memoryless BoW/mention classifier with zero dependency on the entity's own history. The brain's
homologous mechanisms (SEM event-segmentation, Kintsch C-I, Zwaan Event-Indexing) are all
literally `state_t = f(state_{t-1}, content_t)` -- sequential, content-driven, and therefore
naturally order-dependent because state_{t-1} depends on which content was integrated when.
ProPara's own literature independently discovered and validated exactly this fix already:
ProGlobal's `c_i = softmax(W[mu_i; c_{i-1}])` (Dalvi et al. 2018) is the direct computational
analogue of Kintsch's cycle-carryover, and it is reported to beat ProLocal's context-blind
per-step classification -- which is structurally what our current RETRIEVE signal is. The
concrete fix: make RETRIEVE gate on the entity's currently-DECODED state (from the
AccumulateRegister, built only from steps already committed) using a VerbNet/FrameNet event-type
lexicon (create/destroy/motion verb classes) instead of raw BoW, and let VALIDATE reject
candidates that are state-INCONSISTENT (not just index-out-of-window). Honest deflator: even the
strongest published content signal (Gupta & Durrett 2019 transformer, verb-ablation -5.5pts) caps
around ~51% on exactly ProPara's "unmentioned/implicit" subset (near baseline) and MOVE-class
events at 56.27 vs 79.82 for CREATE/DESTROY -- so this fix should be expected to make the win
robustly *order-dependent*, not to produce a large *magnitude* jump. The focus-margin headroom on
this specific hard subset is real but small, confirmed independently by outside literature, not
just by our own two data points.

## 1. Brain mechanism: structure -> process -> shape/position/metric

**Structure: Event Segmentation Theory / SEM (Zacks & Swallow 2007; Zacks, Speer, Swallow, Braver
& Reynolds 2007, *Psychol Bull*; Franklin, Norman, Ranganath, Zacks & Gershman 2020, *Psychol Rev*
127(3):327-361).** A "working event model" continuously predicts the next input; large/sustained
PREDICTION-ERROR triggers a boundary. SEM formalizes this as Bayesian model comparison: cluster
scenes into events via a sticky Chinese-Restaurant-Process prior (bias toward continuing the
CURRENT event) vs. the likelihood of the new scene under the current event's learned within-event
dynamics -- a boundary fires when a NEW-event hypothesis beats CONTINUE. The content driving this
is structured scene features (agent/action/role/spatial slots), not raw surface tokens. Kumar,
Goldstein, Michelmann, Zacks, Hasson & Norman (2023, *Cognitive Science* 47:e13343) directly show
human segmentation tracks *Bayesian surprise* (a function of the model's ACCUMULATED belief state)
rather than local word-surprisal alone -- segmentation is provably history-dependent, not a
per-token classifier.

**Structure: cortical hierarchy + hippocampal boundary encoding (Baldassano, Chen, Zadbood, Pillow,
Hasson & Norman 2017, *Neuron* 95(3):709-721).** Data-driven HMM on fMRI finds event granularity
scales an order of magnitude across the cortical hierarchy -- fine/short events in sensory cortex,
coarse/long "narrative-schema" events in angular gyrus/precuneus/mPFC (DMN). Hippocampal activity
spikes at high-order event OFFSETS, and spike strength predicts later recall of that event.
Lositsky et al. (2018, *J Neurosci* 38(45):9689) directly SCRAMBLE event order and find mPFC
schema-pattern similarity is specifically disrupted (posterior sensory regions are not) -- direct
neural evidence that the higher-order situation-model layer, not raw perception, is what content
scrambling breaks.

**Structure: incremental situation-model construction (Kintsch 1988, *Psychol Rev*; van Dijk &
Kintsch 1983; Zwaan, Langston & Graesser 1995, *Psychol Sci* 6:292-297; Zwaan & Radvansky 1998,
*Psychol Bull* 123:162-185).** Construction-Integration: each reading CYCLE (construction) over-
generates propositions/inferences, then (integration) spreading activation settles to a coherent
vector; a subset of the settled activations from cycle t-1 seeds cycle t's construction -- literally
`state_t = f(carryover(state_{t-1}), content_t)`. Zwaan & Radvansky's Event-Indexing Model:
readers monitor 5 dimensions in parallel (time, space, protagonist, causation, intentionality);
the situation model is UPDATED specifically when text signals a DISCONTINUITY on a dimension, with
update cost (reading time) scaling with discontinuity MAGNITUDE (Zwaan 1996, *JEP:LMC*, temporal-
gap-size effect). Time and causation dominate the update-cost effect; space is comparatively weak
(Rinck & Weber 2003, *Mem & Cogn* 31). Trabasso & van den Broek (1985, *JML* 24:612-630) show
causal-network CONNECTIVITY (not proposition count) predicts recall/importance; Xu & Kwok (2019,
*Memory* 27(8)) show readers assume narrated order = chronological order ("temporal-order
iconicity") and out-of-chronological-order material measurably slows reading and degrades memory
accessibility -- order violation is a DETECTABLE, costly event, not a neutral resequencing.
Bounded by Cowan-4 focus (Cowan 2001, *BBS* 24:87-114), extended via Ericsson & Kintsch's (1995,
*Psychol Rev* 102:211-245) Long-Term Working Memory retrieval-structure account of how experts
track more than 4 entities via rapid-cued LTM access from the small active focus.

**SHAPE (what the update computes):** compare NEW content against the CURRENTLY-HELD model state;
accept/reject/reweight based on consistency, not on the input's raw position.
**POSITION (when it fires):** continuously, cycle-by-cycle / at every clause, gated to fire hardest
at discontinuities (PE spikes / dimension-boundary crossings).
**METRIC:** prediction-error magnitude (SEM); reading-time / N400 cost proportional to discontinuity
size (Event-Indexing); causal-connectivity count (Trabasso-van den Broek recall predictor);
hippocampal boundary-response amplitude predicting subsequent memory (Baldassano).

The single unifying computational fact across all three literatures: **the update is a function of
the CARRIED-OVER PRIOR STATE plus the NEW CONTENT, not a function of an entity's raw index
position in the sequence.** Order-dependence is an EMERGENT PROPERTY of this recurrence (permute
the input and state_{t-1} is a different, generally incoherent, thing at every t), not an
explicitly-encoded index rule.

## 2. Fidelity diagnosis: where the loop diverges

Read directly off `_assign_events_for_participant` (`exp_propara_decisive_inference_arm1_oracle_v1.py`
lines 296-330) and `reasoning_label_grids` (lines 333-379):

- **RETRIEVE** (`_bow_step_probs`, called once per participant, independent of any prior
  assignment): a static TF-IDF + mention-boolean classifier scores EVERY step independently.
  There is no notion of "what has already been assigned to this entity so far" feeding the score
  for step t -- structurally identical to ProLocal (Dalvi et al. 2018), the WEAKER of ProPara's own
  two published baselines, which the field's own follow-on work (ProGlobal's
  `c_i = softmax(W[mu_i; c_{i-1}])`, NCET's recurrent-LSTM-plus-CRF) was built specifically to beat
  by adding state-carryover. **Divergence: SHAPE.** The brain's update compares content against
  currently-held state; this classifier has no currently-held state to compare against.

- **VALIDATE** (`lo, hi` window logic, lines 313-329): `lo`/`hi` are pure step-INDEX bounds --
  after CREATE is placed at index i, `lo = i+1`; after DESTROY is placed at index j, `hi = j-1`.
  This constraint is evaluated purely on the numeric position value, structurally identical under
  ANY relabeling of what text occupies each position. **Divergence: POSITION/METRIC.** The brain's
  causal/temporal ordering constraint (Trabasso-van den Broek causal-network necessity; Xu-Kwok
  chronological-order expectation) is itself CONTENT-DERIVED -- "X caused Y" is read off what the
  text says, not assumed from index arithmetic. Our validate step borrows the STRUCTURAL SHAPE of
  an ordering constraint (directionally correct: CREATE-before-DESTROY is real world-knowledge)
  but implements it as index bookkeeping rather than content-verified causal/temporal necessity.
  That is precisely why it survives scramble intact: an index-only constraint is, by construction,
  invariant to whatever content permutation sits behind those indices.

- **Why the content signal is small AND fragile across seeds:** `_bow_step_probs` is a per-step,
  memoryless classifier trained on tiny data (43 dev / ~110 train paragraphs) using
  bag-of-words+mention features that don't discriminate CREATE vs. DESTROY vs. MOVE semantically
  (a sentence mentioning the participant scores similarly whichever event type actually occurred).
  Gupta & Durrett's (2019, EMNLP, arXiv:1909.02635) own input-ablation on this exact task found
  VERB TOKENS SPECIFICALLY are the dominant content signal (removing them costs ~5.5pts, more than
  any other feature category) -- our retrieve signal does not isolate or specially weight verb
  semantics at all, so the little content signal it does carry is diffuse and noisy, which is
  exactly the seed-to-seed instability observed (natural_focus_margin fixed at 0.1365, but
  scramble_retained_frac ranges 0.401 to 1.056 across seeds 7/17/29 -- a weak, non-specific signal
  is expected to behave close to random under permutation, sometimes surviving by chance, sometimes
  not).

## 3. Concrete improvement for the next ARM-1 run (testable, pre-registerable)

**"Sequential state-conditioned retrieve + state-consistency validate"** -- minimal, targeted
change to `reasoning_label_grids` / `_assign_events_for_participant`, reusing owned organs:

1. **Content signal upgrade (verb-class lexicon, not raw BoW).** Extract from each sentence
   whether it contains a CREATE-class predicate (form, appear, produce, generate...), DESTROY-class
   predicate (die, dissolve, evaporate, disappear, decay, absorb, burn up...), or MOVE-class
   predicate (move, flow, travel, carry, fall, transport...) via VerbNet/FrameNet classes -- the
   substrate already has `framenet_cache`/`wordnet_cache` in the KB (confirmed live via
   `substrate_query.sh` this session: FrameNet frame `Objective_influence::Dependent_situation` is
   already indexed) -- REUSE, don't re-source. This directly operationalizes Clark, Dalvi & Tandon
   (arXiv:1804.05435, "What Happened? Leveraging VerbNet...") and ProStruct's (Tandon et al. 2018,
   EMNLP, D18-1006) VerbNet-injection precedent, both reported to beat surface-cue-only baselines
   on this task family, and Kazeminejad & Palmer (2023, *SEM, aclanthology 2023.starsem-1.33)
   explicitly targets the SAME implicit/unmentioned gap this cell's FOCUS metric measures.

2. **Make RETRIEVE stateful.** Process steps in the ACTUAL order they are presented to the loop
   (natural order for the natural arm, scrambled order for the scramble arm -- the loop must not
   secretly re-sort by true index). At step t, before scoring, DECODE the participant's current
   existence-state from `AccumulateRegister` using ONLY the events committed at steps < t (not the
   oracle multiset's global future knowledge). Gate the verb-class score by consistency with that
   decoded state (near-zero prior for DESTROY/MOVE if not-yet-created; near-zero for further
   MOVE/DESTROY if already destroyed). This is the literal computational form of
   `c_i = softmax(W[mu_i; c_{i-1}])` (ProGlobal) and of Zwaan's "compare new content against
   currently-held model, update on discontinuity."

3. **VALIDATE becomes state-consistency, not index-window.** Reject-and-retry (reusing Stage-2A's
   own retrieve-validate-advance control flow, already the organ's documented reuse pattern) when
   the top-ranked candidate is state-INCONSISTENT, falling back to the next-ranked candidate --
   keep the index-monotonicity bound only as a hard safety floor (never allow DESTROY before
   CREATE), not as the primary discriminator.

**Falsifiable predictions:**
- **HARD-PASS:** natural_focus_margin >= 0.10 (comparable-or-better than the current 0.1365, not
  required to dramatically exceed it per the honest ceiling below) AND scramble collapse on **ALL
  3** full-run seeds this time (scramble_retained_frac <= 0.55 EVERY seed -- tightening the
  existing per-run gate, which only required the aggregate/one seed to collapse) AND the new
  content-lesion control (Section 4) falls to within 0.02 of the true (no-oracle) baseline focus-F1.
- **HARD-FAIL:** scramble still fails to collapse on >=2/3 seeds (the fragility is structural to
  the retrieve signal's weakness, not fixed by this change) OR the content-lesion arm scores
  statistically indistinguishable from the full reasoning arm (proves the added verb-class/state
  gating was decorative, not load-bearing -- same logic as the existing arms-must-differ discipline,
  generalized to a content-ablation instead of a whole-arm ablation).
- **MIDDLE_BAND:** natural margin holds but scramble collapse is still seed-inconsistent (partial
  fix -- the stateful gating helps but the verb-class lexicon's coverage on ProPara's actual
  vocabulary is too sparse to dominate).

## 4. Complementary control: content-lesion / prior-ablation (beyond scramble)

Scramble alone cannot isolate content because BOTH the oracle event-multiset (paragraph-level,
provably invariant to sentence-order permutation by the cell's own design) AND the index-monotonicity
window survive scramble intact -- as the cell's own docstring already states, "some residual
advantage over baselines... is STRUCTURALLY EXPECTED to survive scramble even with zero genuine
temporal composition." A genuinely orthogonal manipulation is needed: **lesion content while
holding order and structure fixed**, the engineering analogue of Lositsky et al.'s scrambling
lesion but targeting the opposite axis.

**Design:** a fourth arm, "prior-only" -- TRUE sentence order (unscrambled), full oracle multiset,
full index-monotonicity window, but the RETRIEVE ranking within each window is replaced by a
UNIFORM-RANDOM draw (deterministic hashlib-seeded, per META_RULE F.5) instead of any content score.
This zeroes the content channel while leaving every structural/order channel exactly as in the
natural arm.

- If prior-only scores close to natural reasoning, that CONFIRMS (independent of scramble) that
  content contributes little -- consistent with the current oracle run's finding.
- If prior-only scores much lower than natural (materially below even the scramble arm, since
  scramble still carries SOME garbled-but-nonzero content, whereas prior-only carries none), that
  is clean evidence content is doing real work that the noisy scramble control under-detected.
- Comparing all three (natural / scramble / prior-only) against the true baseline decomposes the
  win into a structural-prior component (baseline -> prior-only gap), a content component
  (prior-only -> natural gap), and an order-alignment component (natural -> scramble gap, which
  conflates "content garbled" with "content present but misaligned" -- the reason prior-only is
  proposed as an ADDITION to scramble, not a replacement).

No published precedent for either a scramble OR a prior-only ablation was found on ProPara/entity-
tracking systems specifically (clean negative from the NLP lit-scan sub-agent, checked ProLocal/
ProGlobal, NCET, KG-MRC, ProStruct, both Gupta-Durrett papers) -- this decomposition is a genuine
methodological contribution here, not a borrowed number; the HARD-PASS/HARD-FAIL bands above are
therefore set from this session's own dev-calibration discipline (per the cell's existing
calibrate-on-dev/apply-to-test protocol), not from literature magnitudes.

## 5. Cross-thread synthesis with prior entries

- Confirms and sharpens `notes/research_comprehension_barrier_map_brain_foundational_2026-08-10.md`
  B6 (situation-model construction) and B8 (causal/bridging inference + VALIDATION): B8 there is
  marked "toy-validated... on real prose the loop is only as good as B5's extraction feeding it" --
  this drill shows the SAME gap exists one level down, INSIDE the toy-validated loop itself, when
  the loop is asked to do genuine sequential state-tracking rather than compose planted, already-
  structured relations (Stage-2A's HARD_PASS was on planted FHRR-codebook relations with a clean
  content-similarity signal; ARM-1's BoW-mention signal on real ProPara text is much weaker).
- Extends `notes/research_brain_situation_model_simulation_pullin_causal_2026-08-09.md` (retrieve/
  pull-in mechanics) by supplying the missing piece that note flagged as unaddressed: HOW content
  should condition the retrieve step, concretely (verb-class gating + state-consistency), not just
  THAT retrieval should be content-addressable.
- Directly consistent with the MEMORY.md-anchored finding
  `[[project_extraction_is_the_universal_comprehension_wall_9plus_cells_2026-08-10]]`: this fix is
  explicitly scoped to stay WITHIN the oracle-multiset-given regime and does not touch B5
  extraction. It should NOT be read as closing that wall -- the moment the oracle grant is removed,
  the same real-prose extraction ceiling this session's other cells hit 9+ times independently
  should be expected to resurface here too.
- Corroborates (does not merely assert) the ARM-1 cell's own scramble-collapse rationale docstring
  ("some residual advantage... is STRUCTURALLY EXPECTED to survive scramble") with independent,
  disk-external literature: Trabasso-van den Broek causal-connectivity-predicts-recall and
  Xu-Kwok chronological-order-iconicity both predict that REAL comprehension gains should be
  order-sensitive, so a structurally order-invariant win (multiset + index window) SHOULD be
  expected to be brain-INFIDEL by construction, exactly as observed.

## 6. Substrate-product implications

- The fix is a bounded, cheap change (new verb-class lexicon lookup + reordering two existing loop
  stages to be sequential) -- no new organ, reuses `AccumulateRegister`, `_bow_step_probs`'s
  existing sklearn fit, and the Stage-2A retrieve-validate-advance control-flow pattern verbatim.
  Low build cost relative to the diagnostic value (directly tests whether the substrate's toy-
  validated inference organs generalize to real, weakly-signaled content, which is the open
  question the barrier map flags as the single highest-leverage unresolved item).
- If HARD-PASS: gives the substrate a validated, reusable pattern -- "gate retrieve-signal by
  currently-decoded state, not by raw content alone" -- directly transferable to the WIQA causal-
  chain-loop and any future real-prose situation-model consumer (B6/B8 in the barrier map), since
  the mechanism (sequential state-conditioning) is domain-general, not ProPara-specific.
  If HARD-FAIL: cleanly localizes the residual to "the verb-class lexicon's coverage of ProPara's
  actual vocabulary is too sparse" (a data/lexicon-coverage problem, fixable by extending the
  lexicon) vs. "sequential conditioning itself doesn't help" (a mechanism-level negative, would
  argue the loop needs a stronger extraction front end before this class of fix pays off at all --
  routes back to B5, per the barrier map's own sequencing).
- The prior-only / content-lesion control, once built, is directly reusable on ANY future
  oracle-structure-plus-inference cell in this program (WIQA, MCScript2, DesireDB) as a standard
  second control alongside scramble -- worth promoting to a shared harness helper
  (`tools/benchmark_trap_check/`) rather than reimplementing per-cell.

## Cheap decisive test

Before committing to a full `--full` re-run: a `--smoke` (DEV split, 1 seed) run of the modified
cell is the cheap decisive test -- if `scramble_retained_frac` on DEV drops materially versus the
current oracle-run's DEV number (0.507, per the pre-reg's own calibration numbers cited in the
cell) AND the prior-only arm's focus-F1 sits near the true baseline, that is sufficient evidence to
proceed to `--full` (3-seed TEST). If DEV shows no improvement in scramble-consistency, do not
spend the `--full` budget -- iterate the verb-class lexicon coverage first (the most likely single
point of failure per the Gupta-Durrett verb-ablation precedent) or accept a HARD-FAIL diagnosis
localized to lexicon sparsity.

## Bottom line

The brain never implements "monotonicity" as index arithmetic -- every relevant mechanism (SEM
event-boundaries, Kintsch C-I, Zwaan Event-Indexing) computes state_t = f(state_{t-1}, content_t),
making order-dependence an emergent consequence of content-conditioned recurrence rather than an
explicit rule; our ARM-1 loop currently has the ordering RULE (content-blind, index-based) but not
the content-conditioned RECURRENCE that would make it order-dependent for the right reason, and the
field's own ProPara literature (ProGlobal vs. ProLocal; NCET's recurrent CRF; VerbNet-injection
systems) already validates exactly this class of fix, with a realistically modest ceiling on the
FOCUS/implicit subset (the field's strongest system still caps near baseline on unmentioned
entities) -- so the right target for the next run is a scramble-robust (all-seed) but magnitude-
modest win, verified against a new prior-only content-lesion control that isolates content's
contribution independent of scramble's structural confound.

## Citations (verified count)

Verified via 3 independent Sonnet lit-scan sub-agents (WebSearch/WebFetch), each returning a
citation list with per-item confidence flags (HIGH/MEDIUM/LOW). Total distinct citations surfaced:
**23** across the three scans (event-segmentation: 10; situation-model/discontinuity: 13 incl.
overlaps; NLP/ProPara: 10). HIGH-confidence citations (cross-checked or directly quoted numbers,
counted once per unique work): Zacks & Swallow 2007; Zacks, Speer, Swallow, Braver & Reynolds 2007;
Franklin, Norman, Ranganath, Zacks & Gershman 2020 (SEM); Baldassano et al. 2017 (*Neuron*); Speer,
Zacks & Reynolds 2007; Kumar, Goldstein, Michelmann, Zacks, Hasson & Norman 2023; Kintsch 1988;
van Dijk & Kintsch 1983; Zwaan, Langston & Graesser 1995; Zwaan, Magliano & Graesser 1995; Zwaan &
Radvansky 1998; Trabasso & van den Broek 1985; Xu & Kwok 2019; Cowan 2001; Ericsson & Kintsch 1995;
Dalvi et al. 2018 (ProPara/ProLocal/ProGlobal); Gupta & Durrett 2019 (NCET, arXiv:1904.03518);
Gupta & Durrett 2019 (transformer entity-tracking, arXiv:1909.02635, numeric ablations directly
quoted); Tandon et al. 2018 (ProStruct); Clark, Dalvi & Tandon (arXiv:1804.05435). MEDIUM/LOW-
confidence (approach confirmed, exact numbers not extracted, or single-source): Reynolds, Zacks &
Braver 2007; Lositsky et al. 2018; Zwaan 1996; Rinck & Weber 2003; Das et al. 2018 (KG-MRC);
Kazeminejad & Palmer 2023; "Order-Based Pre-training Strategies..." 2024 (arXiv:2404.04676).
No citation was fabricated; every item traces to a specific sub-agent WebSearch/WebFetch result
with an explicit confidence flag preserved above (per lit-scan calibration discipline). Applying
the mandatory calibration penalty (deflate 0.15-0.25, novel-synthesis capped at 0.50):
**P_deflated = 0.35** for "the Section 3 fix clears the tightened all-seed-collapse HARD-PASS band
on the next --smoke/DEV run" (undeflated confidence ~0.55-0.60, given real precedent for the
ProLocal->ProGlobal-style stateful-conditioning direction and the VerbNet-injection direction both
independently beating surface-cue baselines in the literature; deflated for uncharted-combination
risk -- this exact combination, on this exact harness, has not been tested).
