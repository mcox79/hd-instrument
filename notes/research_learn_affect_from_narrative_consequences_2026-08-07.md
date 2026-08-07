# Research: learning evaluative/affective word-meaning from narrative consequences (2026-08-07)

Research role, literature-scan cycle, dispatched parallel to a running experiment (read-only, no
production edits). 4 parallel Sonnet lit-scan sub-agents dispatched (biology; weak-supervision
sparse-agreement rescue; narrative/event-based implicit sentiment; sparse-reward credit-assignment
adjacency), synthesized here by the research role.

---

## 0. KB-check (dedup) — this maps DIRECTLY onto an in-flight Stage-4 build, not abstract territory

`bash tools/substrate_query.sh` against this topic surfaced, at cosine 0.31-0.35, our own
`experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1` (**HARD_FAIL**, 2026-08-06)
and its companion `exp_goal_congruence_outcome_valence_v1` (**HARD_PASS**). This is not adjacent
prior art — it IS the Stage-4 build the task description refers to. I read the full design note
(`notes/research_consequence_learning_loop_oov_outcome_verb_valence_2026-08-06.md`) and the failed
run's `data/exp_consequence_learning_loop_oov_outcome_verb_valence_v1/metrics.json` directly.

**The measured failure, precisely:** the design's anti-drift gate requires two independently-computed
signals — `congruence_decision` (Signal A: class-relation + referent-linking) and `lexicon_predict`
(Signal B: flat lexicon membership) — to **agree** before a window's teacher verdict is trusted. On
the real 4-novel corpus scan (22,197 sentences, 1,434 goal-clear windows), this AND-gate produced
`bootstrap_curve[0].n_windows_with_teacher = 3` — three windows, out of 1,431, drew a trusted joint
label across the whole corpus. `n_registered = 0`: zero words were ever grounded. `learnable_subset_size
= 0`. This is a coverage-collapse failure, not a precision failure — the design's own scramble-control
and light-verb-canary machinery never even got the chance to be exercised because almost nothing ever
cleared the entry gate.

This reframes the research question precisely: not just "how does the field learn valence from
consequence" in the abstract, but specifically **"how does the field rescue a near-zero-coverage
two-weak-signal-AND-gate without abandoning the anti-drift precision goal."** That sparsity-rescue
question turned out to have the single most decisive, actionable answer of the whole scan (Section 2).

The three 2026-08-06 prior-art scans already on disk (`prior_art_classical_symbolic_story_
understanding`, `prior_art_modern_neurosymbolic_narrative`, `prior_art_vsa_hdc_for_language`) cover
the goal/outcome **REPRESENTATION** question (Plot Units, Trabasso Goal->Attempt->Outcome, TALE-SPIN,
AESOP, narrative event chains, VSA-for-narrative gap). None of them address word-level valence
**ACQUISITION** from weak/distant consequence supervision — that is genuinely new territory this
session, confirmed by a live re-check (no overlapping hits above cosine 0.35 on the acquisition-
specific query terms).

---

## HEADLINE

**The measured coverage-collapse (3/1431 windows, 0 words grounded) is the textbook failure mode of
a strict two-source AND-gate in weak supervision — a problem the field solved decades ago (Dawid &
Skene 1979 latent-rater EM; modernized as Snorkel/"data programming," Ratner et al. 2016/2017) and
did NOT need a new mechanism to fix, only a different combination rule for two signals the design
already computes.** Swap the hard "Signal A == Signal B" requirement for a probabilistic/soft
combination (each signal treated as an independently-accuracy-weighted labeling function, combined via
EM into a posterior confidence per window) and add one cheap third weak view for identifiability
(Dawid-Skene-style joint accuracy/label inference is only weakly identified with exactly two raters).
This is a genuinely different verdict from "another facet of the grounding wall" — it is a **fixable
combination-rule bug in an otherwise well-precedented cross-situational bootstrap design**, not a
restatement of the field's unsolved raw-prose-to-representation problem. Separately and honestly: a
FULLY zero-seed narrative-affect learner (no hand lexicon anywhere in the pipeline) remains genuinely
unsolved in the literature (Section 4) — but our design never needed that; it already has a ~90-word
seed lexicon (`CLASS_REGISTRY`/`V2_OUTCOME_MET`/`_UNMET`) and is doing well-precedented cross-
situational bootstrap from a seed, not zero-seed induction. Don't let this negative result get
misfiled as "grounding is impossible" — it's specifically "the label-combination rule was wrong."

---

## 1. Brain mechanism: how consequence becomes earned value, developmentally

**Appraisal theory has a real, convergent goal-status -> discrete-emotion mapping**, not just a loose
metaphor. Four independent traditions — Lazarus's core relational themes (*Emotion and Adaptation*,
1991), the OCC model (Ortony, Clore & Collins, *The Cognitive Structure of Emotions*, 1988), Scherer's
Component Process Model (2001), and Roseman's appraisal model (1991/1996) — converge on: goal
attained/progressing -> joy; goal blocked by another agent -> anger; goal blocked by self -> guilt/
regret; valued goal-object irrevocably lost -> sadness; goal threatened, outcome uncertain -> fear;
threat removed -> relief. **HIGH confidence**, well-established across independent theoretical
lineages, not a single author's idiosyncratic scheme.

**Dopaminergic reward-prediction-error (RPE) is a domain-general teaching signal, not a food/money-
specific one.** Schultz, Dayan & Montague (*Science*, 1997) established RPE as a TD-error broadcast
signal; subsequent work shows this generalizes to money, social approval/rejection, and abstract
outcomes — i.e. RPE is a general-purpose "was I right about how good/bad that was going to be" signal.
**HIGH confidence** on the core finding, **MEDIUM-HIGH** on the generalization-to-social/abstract-value
literature specifically (well-supported by many converging studies, no single canonical review pinned).

**OFC/vmPFC compute a "common currency" value code** that heterogeneous outcomes (food, money, social
approval, a narrative event) get re-coded into for comparison (Padoa-Schioppa & Assad 2006; Levy &
Glimcher 2012; Bartra/McGuire/Kable meta-analysis 2013). **HIGH confidence.** Amygdala/insula perform
salience-tagging (does this matter, roughly how good/bad) feeding forward into OFC/vmPFC valuation and
back into memory consolidation. ACC signals expectancy-violation/outcome-monitoring (Alexander & Brown
2011 PRO model), complementing dopaminergic RPE. **HIGH** on the general division of labor, **MEDIUM**
on some finer circuit-level claims (still an active research area).

**Developmental account, directly on point for "how a child learns good/bad from lived/observed
outcome":**
- **Eisenberger** (*Science* 2003; *Nat Rev Neurosci* 2012): social pain (e.g. rejection) recruits the
  same dACC/insula circuitry as physical pain — the brain reuses an ancient threat-distress circuit to
  register social consequences as bad, rather than building a separate social-value module. **HIGH.**
- **Hamlin & Wynn** (*Nature*, 2007): 6- and 10-month-old infants preferentially reach for a "Helper"
  puppet over a "Hinderer" after purely OBSERVING the consequences of each puppet's actions on a third
  party's goal — pre-verbal good/bad agent evaluation from observed consequence, no label required.
  **Honest caveat:** a large 2025 multi-lab replication (Lucca et al., ~1000 infants, 37 labs) found
  more inconsistent results than the original, especially at 6 months — the paradigm and general
  finding are foundational to the field, but the original effect size/robustness is less secure than
  it was ten years ago. **HIGH** on the paradigm's existence and field influence, **MEDIUM** on the
  original effect's robustness given documented replication difficulty.

**The single most directly transferable biological mechanism: evaluative conditioning.** De Houwer
(2007, reviewing Levey & Martin 1975) — mere repeated co-occurrence of an arbitrarily neutral stimulus
(which could just as well be a WORD) with an affectively-loaded unconditioned stimulus is sufficient to
transfer valence to it, via a simple domain-general associative mechanism that doesn't care whether the
paired "outcome" is a picture, a taste, or a narrated event. **HIGH confidence.** This is close to a
direct mechanistic license for our design's cross-situational accumulation shape (a word repeatedly
co-occurring with MET vs UNMET outcomes accrues valence proportional to that co-occurrence pattern) —
it's not just an engineering convenience, it's the brain-analogous mechanism for exactly this problem.

**A documented seam, not a clean identity, between narrated and lived value-learning.** The
description-experience gap (Hertwig & Erev 2009; Hertwig et al. 2004) is a canonical, heavily-
replicated finding that people weight rare outcomes oppositely depending on whether probability
information was described/instructed vs experienced through sampling. Olsson & Phelps (2004; *Nat
Neurosci* 2007) directly compared Pavlovian, observational, and purely instructed/verbal fear
acquisition: all three produce measurable fear, but only Pavlovian and observational transfer to
subliminal presentation — instructed (verbal) fear engages a more cortically-mediated, consciousness-
dependent pathway. **HIGH confidence on both.** **Implication for our design:** learning word valence
from NARRATED consequence (reading, not living, the outcome) is a real, biologically-licensed but
genuinely distinct pathway from direct experiential value learning — not a lesser proxy for it. This
is useful calibration: our design's ambition (ground valence via narrated consequence) is doing
something the brain treats as legitimate but mechanistically distinguishable, which is exactly the
right frame for a text-only glass-box substrate that has no lived experience to draw on.

---

## 2. Field methods — adopt / adapt / not-applicable against our owned organs

| Method | Mechanism | Verdict vs our organs | Confidence |
|---|---|---|---|
| **Snorkel / data programming** (Ratner et al., NeurIPS 2016; VLDB 2017) | Many labeling functions each fire-or-abstain independently over the full pool; an unsupervised generative model estimates each function's accuracy/correlation from agreement STATISTICS across the whole corpus (no ground truth needed), emitting a per-instance posterior confidence instead of a binary trust flag | **ADOPT.** Directly targets the measured failure (Section 0): replaces the AND-requirement (intersection) with a union-plus-weighting scheme; recovers coverage from 3 windows toward however many windows either signal alone fires on | HIGH |
| **Dawid-Skene EM** (1979) | Mathematical ancestor of Snorkel's generative model: jointly infer each rater's accuracy and the latent true label via EM. Caveat found by the lit-scan: **weakly identified with only 2 raters** (label-switching risk, especially if the two sources are correlated by construction) — best practice is 3+ loosely-correlated sources | **ADOPT the mechanism, but MUST add a 3rd weak view** — our design currently has exactly Signal A (`congruence_decision`) + Signal B (`lexicon_predict`), the weak-identifiability regime the literature explicitly warns about | HIGH |
| **Co-training** (Blum & Mitchell, COLT 1998) | Two conditionally-independent views each train on their OWN most-confident subset, not a full-agreement requirement | **ADAPT** as a complementary framing — reinforces "don't require both signals to fire together," could motivate treating Signal A and Signal B as two views that each independently contribute confident exposures rather than jointly gating every window | MEDIUM-HIGH |
| **Yarowsky bootstrapping / propose-but-verify** (Yarowsky 1995; already found in the 08-06 design note via Trueswell/Stevens) | Seed set + iteratively relaxed confidence threshold; one-sense-per-discourse propagation | **ALREADY ADOPTED** (the design's per-window single-credit-target + cross-episode consolidation shape is this pattern) — this scan reinforces it, doesn't add new ground | HIGH |
| **Evaluative conditioning** (De Houwer 2007) | Domain-general co-occurrence-based valence transfer | **ADOPT AS BIOLOGICAL JUSTIFICATION** for the cross-situational accumulation architecture — not a new mechanism, a confirmation that the existing shape is brain-analogous | HIGH |
| **Deng & Wiebe goodFor/badFor propagation** (EACL 2014; EMNLP 2015; Choi & Wiebe +/-EffectWordNet, EMNLP 2014) | Propagates sentiment from a seed expression to an unlabeled entity via a hand-built (seed+WordNet-expanded) lexicon of which event-types are beneficial/harmful, using a factor graph / loopy belief propagation | **ADAPT the RELATION VOCABULARY only, not the mechanism.** Their propagation-from-seed shape is architecturally close to our referent-linked credit-assignment, but their event-effect lexicon is WordNet-expanded — our design deliberately stays WordNet-free (Section 8 of the 08-06 note). Worth a CHEAP audit: does `CLASS_REGISTRY`/`OPPOSED_PAIRS` already cover the goodFor/badFor relation types, or is there a class of outcome verb we're structurally blind to that their RS1-RS4 implicature rules would catch? Not a build, a vocabulary cross-check | MEDIUM |
| **Connotation Frames** (Rashkin, Singh & Choi, ACL 2016) | Crowd-annotated per-verb sentiment-toward-agent/theme, generalized via a factor graph over distributional embeddings | **NOT APPLICABLE.** Teacher signal is crowd-labeled at the type level in a generic templated setting, not derived from any specific narrated consequence — using this would be importing a hand-label pipeline exactly like the WordNet-anchor-propagate alternative our design already chose not to be | HIGH |
| **Event2Mind / StoryCommonsense / GLUCOSE** (Rashkin et al. 2018; Mostafazadeh et al. 2020) | Crowd workers read/imagine a story and hand-annotate intent/reaction/emotion labels | **NOT APPLICABLE, confirmed explicitly by GLUCOSE's own methodology text** ("Workers directly filled these slots — they weren't inferred from story outcomes"). These are commonsense-inference DATASETS built by human judgment, not systems that compute affect from outcome structure | HIGH |
| **Hindsight relabeling / HER** (Andrychowicz et al. 2017; HIGhER, Cideron et al. 2019) | Relabel an episode's target as whatever outcome ACTUALLY occurred, rather than requiring a pre-fixed expected target; an LLM-alignment variant already strips out the RL loop entirely (pure data-relabeling) | **ADAPT.** Maps directly onto the already-in-flight DID-IT-HAPPEN pivot (per MEMORY: read situation-state, not grade words) — credit target should be resolved by "which co-occurring candidate is consistent with the outcome that actually happened," not only by strict pre-specified referent match | MEDIUM-HIGH |
| **RUDDER / return decomposition** (Arjona-Medina et al. 2019); structural credit assignment (Ferret et al.'s SECRET, offline supervised, no RL loop; Schwab et al.'s Granger-causal mixture-of-experts) | Redistribute one delayed/rare outcome credit across co-occurring candidates via marginal/ablation contribution, not a single hard match | **ADAPT.** This is the field's direct answer to the design's own honestly-flagged imprecision ("rare multi-candidate windows credit ALL qualifying lemmas... a known imprecision"): score each candidate's marginal contribution (does removing this candidate change the teacher-verdict confidence) and weight credit proportionally instead of all-or-nothing | MEDIUM-HIGH |
| **Eligibility traces / TD(lambda)** (Sutton & Barto) | Decaying recency-weighted activation tag per state/feature, broadcast credit on outcome in proportion to trace strength | **ADAPT.** Could replace the fixed hard `W=3`-sentence window with a principled decay — a candidate lemma 1 sentence before the outcome gets more credit-weight than one 3 sentences before, instead of a flat cutoff | MEDIUM |
| **Potential-based reward shaping** (Ng, Harada & Russell 1999) | Densify sparse reward via a potential-function difference, provably policy-invariant | **NOT APPLICABLE cleanly** — the policy-invariance theorem has no training-loop analog here; only a loose design metaphor, lowest portability of everything found | LOW |

---

## 3. The single most transferable idea, and exactly how it wires into what we own

**The idea:** replace the hard `Signal_A == Signal_B` AND-gate with a **Dawid-Skene/Snorkel-style
posterior-weighted combination of >=3 weak views**, and feed the resulting REAL-VALUED confidence into
the existing consolidation machinery instead of an unweighted vote increment.

**Why this is minimal-surface-area, not a new mechanism:**

1. **Signal A (`congruence_decision`) and Signal B (`lexicon_predict`) stay exactly as they are.** No
   change to either function. The only change is how their outputs get COMBINED.
2. **Add one cheap third weak view for Dawid-Skene identifiability** (the lit-scan's explicit warning:
   2-rater EM is weakly identified). Cheapest candidate: embedding-cosine similarity between the
   credit-target lemma and known-POS/NEG outcome-verb centroids (already-owned embeddings, no WordNet,
   no external LLM, no new corpus dependency) — genuinely different in KIND from A (structural/referent)
   and B (flat lexicon membership), which is exactly what the co-training/Dawid-Skene literature means
   by "conditionally independent views."
3. **The consolidation rule itself needs almost no change.** `hdlab.self_improving_loop.decide_keep_
   or_revert` is already a pure margin-threshold rule over an `agg_deltas: Dict[str, float]` — a
   REAL-VALUED input, not a boolean. The design's own 3-way POS/NEG/NEUTRAL consolidation (Section 4.4
   of the 08-06 note) is architecturally the same shape: `margin = (pos_votes - neg_votes) / total`.
   The fix is entirely upstream of this: instead of `pos_votes += 1` when Signal A and Signal B both
   fire POS and agree, compute `pos_votes += P(teacher=POS | Signal_A, Signal_B, Signal_C)` from the
   EM-fit posterior, for EVERY window where at least one signal fires (union, not intersection). The
   downstream `MIN_CONFIRM`/`NEUTRAL_BAND` margin-threshold logic is untouched.
4. **This is the same "two independent teacher signals" primitive the 08-06 note already named as
   worth promoting for reuse** (its own Section 11) — this finding sharpens that recommendation from
   "AND-gate the two signals" to "EM-combine three-or-more signals into a posterior," which is a
   strictly more general, more field-precedented version of the same idea, not a competing one.

**How it maps to the situation-model consequence signal:** `congruence_decision`'s MET/UNMET verdict
(the validated, HARD-PASS `goal_congruence_outcome_valence_v1` baseline) stays the load-bearing
structural signal — it just becomes one of >=3 weighted "labeling functions" feeding an EM-fit
combiner, rather than the mandatory-agreement partner in a 2-of-2 AND-gate. Nothing about the
situation-model's own MET/UNMET semantics changes; only how confidently a given window's verdict is
trusted for TEACHING purposes changes.

---

## 4. Honest verdict: was this solved, or is it another face of the wall?

**Two genuinely different questions, and they get different answers — worth stating precisely because
conflating them would be a mis-calibration in either direction:**

**(a) "Combine 2+ noisy weak-label sources without a coverage-collapsing hard AND-gate" — SOLVED, well
outside our substrate, decades ago.** Dawid-Skene (1979) through Snorkel/data-programming (2016/2017)
is a mature, field-standard, HIGH-confidence-cited engineering pattern. Our measured 3/1431-window
collapse is not a novel problem requiring new theory — it is close to the textbook motivating example
for why this literature exists at all (Ratner et al. explicitly motivate data programming by noting
hand-tuned conjunctions of noisy rules are "brittle and coverage-starved"). This is genuinely good
news: the Stage-4 blocker is very likely a fixable ENGINEERING choice (which combination rule), not a
capability the substrate is missing.

**(b) "Ground word valence from raw narrative with ZERO hand-seed anywhere in the pipeline" — still
open, consistent with the grounding-wall finding from the 08-06 prior-art scans.** The narrative/
event-based-sentiment lit-scan (Section 2) found no system that does this: connotation frames and
Event2Mind/StoryCommonsense/GLUCOSE are crowd-labeled; Deng & Wiebe's propagation, the closest genuine
computational-inference precedent, still requires a seed sentiment expression AND a hand-built (or
WordNet-expanded) event-effect lexicon; the connotation-lexicon induction line (Feng et al. 2013)
induces from corpus-distributional co-occurrence, not narrative-outcome structure specifically. **But
our design never claimed zero-seed** — it has a ~90-word hand seed lexicon (`CLASS_REGISTRY`) and
bootstraps cross-situationally from there, which is exactly the well-precedented cross-situational-
learning + propose-but-verify paradigm (Section 1 of the 08-06 note, reinforced this session by
evaluative conditioning). **Conclusion: this specific Stage-4 blocker is not the wall.** The wall (raw-
prose -> grounded representation with no seed at all) is real and separately documented; it is simply
not what's failing here. Misreading (a)'s fix as evidence the wall is closing, or misreading (b)'s
open status as reason to abandon (a)'s fix, would both be calibration errors — they are independent
findings.

---

## Cheap decisive test

Before committing to a full Dawid-Skene/Snorkel re-architecture, run one cheap, falsifiable
instrumentation pass on the SAME already-scanned 4-novel corpus (methodology already exists per the
08-06 note's Section 7 diagnostic scan, re-runnable with the same `find_desired_state`/`congruence_
decision`/`lexicon_predict` primitives — zero new mechanism, ~1hr):

Count `n_windows_signal_A_fires_alone`, `n_windows_signal_B_fires_alone`, and `n_windows_either_fires`
(OR-coverage), alongside the already-known `n_windows_AND_fires = 3`.

- **HARD-PASS:** OR-coverage >= 15x AND-coverage (i.e. >=45 windows fire at least one signal) —
  confirms the coverage collapse is specifically an artifact of the AND-requirement, validating that a
  Dawid-Skene/Snorkel-style soft-combination re-architecture (Section 3) is the right next build, and
  that most of the design's existing machinery (window generalization, referent-linked credit-target
  scan, 3-way consolidation) can be kept as-is.
- **HARD-FAIL:** OR-coverage stays under 15 windows (5x) even without the AND requirement — this would
  mean the bottleneck is NOT primarily the combination rule but something upstream (e.g. `find_desired_
  state` itself only fires on 6.5% of sentences to begin with, per the 08-06 scan's own 1,434/22,197
  figure, and/or the referent-linked credit-target filter in step 4.3 is over-pruning). In that case the
  Snorkel-style fix from this note would NOT rescue the design, and the next diagnostic must target the
  goal-detection or credit-target stages specifically, not the label-combination rule.
- **Downstream sub-prediction (gated on the above HARD-PASS):** after re-architecting consolidation to
  EM-weighted posteriors with a 3rd weak view, `n_registered` should rise from 0 to >=15 grounded
  lemmas at `MIN_CONFIRM=3`, and `learnable_subset_accuracy` should clear the ORIGINAL pre-reg's 0.75
  HARD-PASS band. If `n_registered` stays at or near 0 even after the fix, that is a HARD-FAIL on the
  whole consequence-learning-loop DIRECTION (not just the AND-gate hypothesis) — pointing to genuine
  corpus sparsity of content-bearing (non-light-verb) outcome signal as the true ceiling, not a fixable
  combination-rule bug.

---

## Cross-thread synthesis

- Directly supersedes nothing in `notes/research_consequence_learning_loop_oov_outcome_verb_valence_
  2026-08-06.md` — that note's architecture (window generalization, referent-linked credit-target scan,
  3-way POS/NEG/NEUTRAL consolidation, multi-pass bootstrap, WordNet-free stance) is unchanged and
  correctly designed; this note diagnoses and fixes ONE specific step (how the two teacher signals get
  combined into a trust decision) using the failed run's own metrics.json as ground truth.
- Consistent with, and does not contradict, the 08-06 prior-art scans' central finding that raw-prose
  -> grounded representation is the field's genuine 45-year open wall (Section 4b above) — this note
  narrows WHERE that wall does and does not apply to the current build.
- Reinforces `exp_goal_congruence_outcome_valence_v1`'s HARD_PASS as the correct, validated situation-
  model consequence-reading baseline; nothing here questions that result, only how its output gets
  combined with a second weak signal for TEACHING purposes.
- The evaluative-conditioning citation (Section 1) is a genuine new biological anchor not present in
  the 08-06 note's own lit-scan (which found Behrend's result-verb-bias and propose-but-verify but not
  evaluative conditioning specifically) — worth folding into future brain-component-map documentation
  as the mechanism license for cross-situational valence accumulation generally, beyond this one build.

---

## Substrate-product implications

- **Immediate next action for Director to hand exp_dev directly (no experiment design prescribed
  here, per [[feedback-no-experiment-design-in-prompts]] — this is a measurement, not a build):**
  instrument the OR-coverage cheap decisive test above on the existing 4-novel corpus scan. It reuses
  existing functions with zero new mechanism and produces a genuinely falsifiable branch (Section
  above) before committing engineering time to a full Snorkel-style re-architecture.
- **If the cheap test HARD-PASSes:** the concrete follow-on build is a Dawid-Skene/Snorkel-style
  posterior-weighted combiner replacing the hard AND-gate, with one added cheap third weak view
  (embedding-cosine-to-known-verb-centroid, no WordNet, no external LLM) — feeding real-valued
  posterior confidence into the EXISTING `decide_keep_or_revert`-family margin-threshold consolidation,
  which needs no changes itself. This keeps the design's WordNet-free stance, its non-circularity
  controls (eval-passage exclusion, label-scramble control, random-credit ablation), and its light-
  verb-neutral-canary intact — only the trust-gate computation changes.
- **Do not read this note as "the grounding wall is closing."** The zero-seed narrative-affect
  induction problem (Section 4b) remains genuinely open in the published literature; this note's fix
  targets a specific, diagnosable engineering choice in a design that already has a seed lexicon, not
  the deeper open problem. Keep these two findings separate in future strategy framing.
- **A reusable substrate-general primitive worth naming:** "EM-combine >=3 independently-computed weak
  structural/lexical signals into a posterior confidence, feed that real-valued confidence into a
  margin-threshold consolidation rule" is a generic pattern applicable to ANY future consequence-driven
  or distant-supervision learning task in this substrate's goal/outcome domain — not just this one
  increment. Worth flagging as a candidate for its own promotion if a second consumer appears, exactly
  as the 08-06 note already flagged the two-signal AND-gate version before this note generalized it.

---

## Citations (verified count)

**Biology (7 mechanisms, agent A, all independently sourced via WebSearch/WebFetch this session):**
Lazarus (*Emotion and Adaptation*, 1991) HIGH; OCC / Ortony, Clore & Collins (1988) HIGH; Scherer
Component Process Model (2001) HIGH; Roseman (1991/1996) HIGH; Schultz, Dayan & Montague (*Science*
1997) HIGH; Padoa-Schioppa & Assad (*Nature* 2006) / Levy & Glimcher (2012) / Bartra et al. (2013)
HIGH; Alexander & Brown PRO model (*Nat Neurosci* 2011) MEDIUM-HIGH; Eisenberger et al. (*Science*
2003; *Nat Rev Neurosci* 2012) HIGH; Hamlin, Wynn & Bloom (*Nature* 2007) HIGH-on-paradigm/MEDIUM-on-
robustness (2025 multi-lab replication, Lucca et al., flagged); De Houwer (2007, evaluative
conditioning) HIGH; Hertwig & Erev (2009) / Hertwig et al. (2004, description-experience gap) HIGH;
Olsson & Phelps (2004; *Nat Neurosci* 2007) HIGH; eLife instructed-aversive-learning study MEDIUM
(citation approximate).

**Weak supervision (agent B, 9 sources):** Ratner, De Sa, Wu, Selsam & Re (data programming, NeurIPS
2016) HIGH; Ratner et al. (Snorkel, VLDB 2017) HIGH; Blum & Mitchell (co-training, COLT 1998) HIGH;
Yarowsky (1995) HIGH; Dawid & Skene (1979) HIGH; Ratner et al. (MeTaL, AAAI 2019) HIGH; Mintz et al.
(distant supervision, ACL-IJCNLP 2009) HIGH; Go, Bhayani & Huang (2009) HIGH; Varma & Re (Snuba, VLDB
2019) MEDIUM.

**Narrative/event sentiment (agent C, 10 sources):** Rashkin, Singh & Choi (Connotation Frames, ACL
2016) HIGH; Rashkin, Bell, Choi & Volkova (2017) HIGH; Sap et al. (Connotation Frames of Power and
Agency, EMNLP 2017) HIGH; Deng & Wiebe (EACL 2014) HIGH; Deng, Wiebe & Choi (COLING 2014) HIGH; Deng &
Wiebe (EMNLP 2015 PSL) MEDIUM (full text not retrieved); Choi & Wiebe (+/-EffectWordNet, EMNLP 2014)
HIGH; Deng, Choi & Wiebe (benefactive/malefactive annotation, ACL 2013) HIGH; Feng, Kang, Kuznetsova &
Choi (Connotation Lexicon, ACL 2013) HIGH; Rashkin et al. (Event2Mind, ACL 2018) HIGH; Rashkin,
Bosselut, Sap, Knight & Choi (StoryCommonsense, ACL 2018) MEDIUM (abstract-only); Mostafazadeh et al.
(GLUCOSE, EMNLP 2020) HIGH.

**Credit assignment (agent D, 9 sources):** Sutton & Barto (2018, eligibility traces) HIGH; Ng, Harada
& Russell (1999, potential-based shaping) HIGH; Andrychowicz et al. (HER, NeurIPS 2017) HIGH; Cideron
et al. (HIGhER, 2019) MEDIUM; Arjona-Medina et al. (RUDDER, NeurIPS 2019) HIGH; RED (2024/2025) MEDIUM;
Minsky (1961) HIGH; Agogino & Tumer (AAMAS 2004) HIGH; Ferret et al. (SECRET, 2019) MEDIUM-HIGH; Schwab,
Miladinovic & Karlen (2019) MEDIUM-HIGH.

**Total distinct verified citations this session: ~40**, spanning 4 independent sub-scans, cross-
checked against 3 already-on-disk 2026-08-06 prior-art notes for non-overlap.

**P_deflated:** raw ~0.65 for "the Snorkel/Dawid-Skene soft-combination fix, applied to the existing
two signals plus one added cheap third view, materially rescues coverage and lets the design clear its
originally pre-registered HARD-PASS bands" (well-precedented general technique with a HIGH-confidence
citation trail, directly diagnosed against this design's own measured failure, not a guess). Deflated
0.20 per the mandatory lit-scan-calibration discipline (no direct precedent for this EXACT combination
applied to goal-outcome-window credit assignment in narrative text; corpus content-verb sparsity,
Section 7 of the 08-06 note, remains a real, independent risk the combination-rule fix does not
address) -> **P_deflated = 0.45** (below the 0.50 novel-synthesis cap). This is the estimate for
"the cheap decisive test HARD-PASSes and the follow-on re-architecture clears its downstream bands" —
Section "Cheap decisive test" above gives the explicit falsifiable branch this estimate should update
against, not a standalone confident prediction.
