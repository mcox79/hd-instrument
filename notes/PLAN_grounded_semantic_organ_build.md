# PLAN — build the missing semantic organ (grounded affective/goal comprehension)

Status: PROPOSAL (2026-08-05), pending aggressive design-VET before it becomes the recorded plan.
Derived from the brain-foundational audit: `notes/brain_audit_SYNTHESIS_missing_semantic_organ.md`
(+ mechanism `..._affective_comprehension_mechanism.md`, our-components `..._our_components_status.md`).
USER mandate (2026-08-05): "work through EACH component and prove they work as intended, THEN show the
combination works, and stay fully brain-faithful. Design, VET aggressively (RIGHT things not easy ones),
record, implement diligently."

## 0. Invariants (non-negotiable, govern every phase)
- Glass-box; NO external LLM at inference; NO borrowed embedding (GloVe/BERT/transformer vector) as the
  meaning organ, NO bolt-on reader/parser as the comprehension organ. Earn meaning via our own learned
  mechanism. (Borrowed models = DIAGNOSTIC-only, then discarded.)
- Brain = reference standard. Each component judged on ITS OWN brain metric (does it reproduce the
  brain's mechanism for that component), not a downstream task-win. A faithful component that only loses
  a downstream task is KEPT (composition problem, not component problem).
- COMPONENT-FIDELITY-FIRST: nail each component brain-faithful ONE-BY-ONE with a can-fail brain-metric
  gate + adversarial VET, THEN assemble. Assembly is its OWN phase with its own integration proof
  (faithful parts do NOT auto-compose).
- Every gain WIRED into hdlab/ + registry at land-time (no islands). Reuse the faithful assets (coref,
  appraisal-sim) as spokes; do not rebuild them.
- Select by brain-foundational-RIGHT, not by cheap. Do the hard BLOCKING thing first.

## 1. Target architecture (from the audit, brain-mapped)
Two-stage meaning, then situation-model gating, then the downstream phenomena fall out:
```
text -> [C-A ATL hub: learned glass-box concept space, sense-aware] 
             -> [C-B IFG/pMTG control: situation-model-gated sense SELECTION]
                  -> sense-resolved concept
                       -> [C-C valuation spoke: valence rides the sense-resolved concept]  (reuse appraisal-sim)
             ^                                   |
             | top-down bias                     v
        [C-D situation model + AFFECT dim + PREDICTIVE step]  (extend situation_reader; reuse coref)
                  |                         |
                  v                         v
        [C-E incongruity: predicted-vs-surface + mentalizing reattribution]  (reuse ToM)  -> irony falls out
                  |
                  v
        [C-F goal-owner selection]  (Component-5, now fed faithful sense-resolved roles + affect + persistence)
```
Faithful assets to build ON (do not rebuild): coreference (WIRED HARD_PASS), grounded appraisal-sim
(earned valuation spoke, islanded -> WIRE it), ToM (mentalizing, islanded -> WIRE it), situation_reader
skeleton (faithful, needs the affect dim), Component-3 frame-primary roles (faithful mechanism, needs
OOV learning in production), hdlab/learner (rule/estimation engine).

## 2. Component build order (dependency-first = hardest/most-blocking first)
Each component ships with: (i) brain-analog + the exact brain MECHANISM it must reproduce; (ii) a
pre-registered CAN-FAIL brain-metric with HARD-PASS/HARD-FAIL bands and a real baseline; (iii) an
adversarial VET (independent skunkworks recompute + shortcut hunt) BEFORE moving on; (iv) WIRE-or-SHELVE
at land. No component advances on a task-win alone; it advances on its brain-metric.

### C-A. Learned lexical-semantic HUB (ATL analog) — THE blocking foundation
- Brain mechanism: amodal concept space learned by statistical convergence + prediction-error, where a
  surface form activates GRADED, SENSE-STRUCTURED candidate meanings (multiple senses co-active), and
  concepts ground to spokes (valuation/relational). NOT a single vector per form (that IS our current
  failure). NOT count-only (my prior note: count-based content CAPPED; the brain-right answer is
  error-driven differentiation) -> learned by prediction-error over context.
- Build: our own glass-box, earned representation over the corpus. Sense-aware (multi-prototype /
  sense-inventory per form, induced not hand-listed). Grounds to the appraisal-sim (valuation) + coref
  (relational) spokes. Learned via hdlab/learner-style error-driven differentiation (reuse/expand the
  owned learner if it fits; if not, document why and build the minimal earned learner glass-box).
- CAN-FAIL brain-metric: on a held-out sense-labeled probe, the hub must place the two senses of a
  polysemous form (studied-hard vs hit-hard; card-trick vs dirty-trick) in DISTINGUISHABLE regions
  (graded similarity respects sense), AND must NOT collapse to random indexing (control: a hash-random
  baseline must FAIL the sense-distinction the hub passes). HARD-FAIL if the hub cannot separate senses
  better than the random-indexing floor.
- Hardest-thing check (VET target): resist (a) sneaking a borrowed embedding, (b) random indexing, (c) a
  bigger hand lexicon, (d) count-only PPMI if it caps. The RIGHT thing is an earned, sense-structured,
  spoke-grounded, prediction-error-learned space.

### C-B. Semantic CONTROL / word-sense selection (IFG/pMTG analog)
- Brain mechanism: biased competition among C-A's co-active candidate senses, constrained by the running
  situation-model context; controlled retrieval of the non-dominant sense when context licenses it;
  objective = contextual coherence, not frequency.
- Build: a selection step that takes (candidate senses from C-A, situation-model context) -> the
  context-licensed sense, glass-box (inspectable which context cue drove the pick).
- CAN-FAIL brain-metric: on context-minimal-pair items (same word, two contexts forcing different
  senses) it selects correctly ABOVE the dominant-sense-always baseline AND above C-A-without-control;
  must show the SITUATION-MODEL context (not just local window) drives selection. HARD-FAIL if it
  reduces to "pick the frequent sense" or to arm_c-style local-window cues.

### C-C. Sense-resolved VALENCE (replaces resolve_valence_blind)
- Brain mechanism: valence = valuation spoke (OFC/appraisal) applied to the SENSE-RESOLVED concept, not
  the surface token.
- Build: route the C-B-selected sense-resolved concept into the appraisal-sim (reuse Component-2 as the
  valuation spoke); retire resolve_valence_blind from the affect path.
- CAN-FAIL brain-metric: clears the exact failures the audit pinned -- the word-sense FPs (studied hard /
  a trick = non-HARM) AND the INERT-valence hard subset (must now beat the scrambled-valence control,
  which the current reader does NOT). HARD-FAIL if scrambling still leaves accuracy unchanged.

### C-D. Situation model AFFECT dimension + PREDICTIVE step
- Brain mechanism: Zwaan event-indexing with a per-protagonist affect/goal state, maintained across the
  passage (WM in focus + coref/hippocampal persistence out of focus), and PREDICTIVE (forward valence
  expectation generated from the model before the next clause).
- Build: extend situation_reader's SituationModel/EventRecord with an affect dimension (populated by C-C
  on sense-resolved concepts, bound to the coref-resolved protagonist-index); add a forward-prediction
  of expected next-clause valence.
- CAN-FAIL brain-metric: IMPLICIT-affect integration -- recover "dread from melancholy+hollow+burden"
  (no explicit polarity word) via cue-integration + forward projection, beating a per-token pooling
  baseline; AND goal-owner PERSISTENCE across a 2-3 sentence span with a distractor character. HARD-FAIL
  if implicit-affect is no better than per-token pooling (would mean the integrate-then-predict step is
  not actually predictive).

### C-E. Incongruity / irony as a BYPRODUCT (reuse ToM)
- Brain mechanism: ACC-style conflict (predicted-vs-surface valence mismatch) triggers mentalizing
  (TPJ/dmPFC) reattribution of intended meaning -- reuse the existing ToM organ, do NOT build a
  standalone irony classifier.
- Build: mismatch signal from C-D's prediction vs the surface reading; on high mismatch, route through
  the ToM organ for intended-meaning reattribution.
- CAN-FAIL brain-metric: recovers the narrative-only irony arm_c MISSED (the 3/5) with 0 sincere
  false-positives, WITHOUT an explicit sarcasm-marker leak -- and does so as a byproduct (no dedicated
  irony features). HARD-FAIL if it needs a standalone surface-cue classifier to work (that would refute
  the "byproduct of a predictive model" hypothesis and re-route).

### C-F. Goal-owner selection (Component-5) on the faithful stack
- Brain mechanism: intentionality dimension bound to protagonist-index, frame-conditioned roles,
  persisted; select the goal-owner from the maintained situation model.
- Build: Component-5 selection fed by C-A/C-B sense-resolved roles + C-D affect/goal persistence +
  coref -- the original frontier target, now on a faithful base.
- CAN-FAIL brain-metric: beat the current real-prose goal-owner ceiling (~0.32 end-to-end / owner-ID
  0.82) on the held-out C3-mined set, with the failure decomposition showing the TYPING_MISS bucket
  (the dominant 14/38) shrinking. HARD-FAIL if no movement on TYPING_MISS.

## 3. Assembly / combination proof (its OWN phase)
After components pass their individual brain-metrics, the integration phase proves the COMBINATION,
using the falsifiable test from the mechanism doc (Section 6):
- Baseline (table valence + positional roles) vs the full situation-model-gated stack, on a held-out set
  spanning: (a) sense-override, (b) implicit affect, (c) irony, (d) goal-owner-across-span-with-distractor.
- HARD-PASS: >=15pts absolute gain on the IMPLICIT-AFFECT and GOAL-OWNER subsets (the two that provably
  require the situation-model layer); improvement on sense/irony expected but smaller.
- HARD-FAIL / diagnostic: <5pts on implicit-affect + goal-owner -> pinpoints which of C-A/C-B vs C-D vs
  persistence is the still-missing piece (a useful failure, not a dead end).
- PLUS the end-to-end goal-owner real-prose number must beat the current ceiling with a clean failure
  decomposition. Integration checkpoints at each wiring seam (faithful parts do not auto-compose).

## 4. Discipline / process (every phase)
- Design-gate before each full run: real baseline, can-fail discriminator (not saturated), difficulty on,
  ONE variable. Pre-register both bands BEFORE running.
- On EVERY negative: brain-fidelity element audit (shape/position/metric vs exact brain mechanism) AND
  ask "is a needed COMPONENT missing -- especially a LEARNING capability?" (route: used-wrong->loop /
  missing-primitive->build / missing-fact->supply / missing-learning->reuse-or-expand hdlab/learner).
- VET positives AS HARD AS negatives, per-axis never aggregate, triple-check load-bearing data, verify
  on disk, READ THE CODE not the label.
- Resumable per-unit; local-only; git-commit after every bank; NO origin push w/o USER auth.
- Docs current every cycle (this plan + backup + charter + registry).

## 5. Open risks the design-VET must attack (RIGHT-not-easy)
1. C-A is the crux and the easiest to cheat. VET must confirm the chosen mechanism is EARNED +
   sense-structured + spoke-grounded, and that the can-fail floor (random-indexing) is a real
   discriminator, not a rigged win.
2. Sequencing: is C-A truly the blocker, or is there a cheaper first step that still does the RIGHT
   thing? (Do-the-hard-blocking-thing says C-A first; VET should confirm nothing faithful is skippable.)
3. Reuse vs island: confirm C-C reuses the appraisal-sim and C-E reuses ToM (spokes), not parallel
   builds. Confirm coref is the persistence substrate for C-D.
4. Brain-faithfulness of "learned distributional hub": is our own error-driven differentiation the ATL
   analog, or a borrowed-embedding shortcut in disguise? VET must draw the line explicitly.
5. Assembly realism: are the per-component metrics chosen so that passing them actually predicts the
   combination passing, or could all components pass while the combination still fails? (Metric-choice
   adversarial check.)
