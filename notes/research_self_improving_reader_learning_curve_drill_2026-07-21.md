# Research: self-improving reader — the multi-round learning CURVE + confidence-gated rate (Step 3 north star)

Filed by: research (Opus synthesis over 2 parallel Sonnet lit-scan sub-agents + heavy same-day-note dedup).
Trigger: Step 3 north star — does the reader improve on its OWN logged errors over ROUNDS of self-correction,
with the learning-RATE gated by confidence? Biology-first per the full-auto loop's mandatory brain-check.

Per [[feedback-lit-scan-calibration-penalty]]: all P estimates below are DEFLATED 0.15-0.25 from raw
sub-agent reads; P for the specific composed cell (novel-synthesis) is capped at 0.50 and, given this task
composes THREE already-separately-validated pieces into a HARDER multi-round bar than any sibling drill has
attempted, pulled further down (see Cross-thread synthesis).

---

## HEADLINE

**The single most important finding of this drill is a DEDUP correction, not a new mechanism.** Two same-day
notes (`research_brain_confidence_weighted_learning_consolidation_2026-07-20.md`,
`research_brain_active_learning_curiosity_lookup_revision_2026-07-20.md`) and two landed cells (atoms
29386/29389, `exp_active_learning_loop_gap_detect_lookup_revise_v1.py` / `v2.py`) already fully cover: (a) the
brain mechanism for confidence-gated learning (neuromodulator precision-weighting, decision-confidence,
hippocampal salience-gated consolidation — axis 1 below is a condensed recap, not new research); (b) the
three-stage active loop (gap-detect -> internal-retrieve -> external-lookup -> reliability/coherence gate ->
provenance-revise) as WIRING, VET-confirmed load-bearing (ungated revision corrupts the model, per task
context 0.417->0.000); (c) a CONTINUOUS confidence-weighted rate design (not binary accept/reject) — but only
for a single-pass corpus-build (STEP1 codebook), not for iterative self-correction on the reader's own error
log. **What none of the four prior artifacts measure is a genuine multi-ROUND trajectory**: v1/v2's own
"learning_curve" metric (`band10_learning_curve`) is a two-point occ1-vs-occ2 delta (does a cached correction
transfer to a SECOND encounter of the same term within one pass) — not accuracy plotted across successive
rounds of self-correction, and not a rate that continues to compound round-over-round. That gap — the CURVE
itself, plus a must-fail control that targets CROSS-ROUND divergence (compounding confirmation bias) rather
than single-step degradation — is the genuinely novel slice this note targets. Both the ML and the brain
literatures converge on the SAME conditional prediction for what that curve should look like (gated-and-
calibrated iteration climbs; ungated-or-miscalibrated iteration plateaus-then-degrades via compounding error),
which is reassuring for design but does NOT establish that our specific reader/error-log/gate composition will
show it — deflated P for full HARD-PASS = **0.28** (see falsifiable predictions).

---

## (a) BRAIN-FIRST — condensed recap + the genuinely NEW multi-round layer

**Single-event confidence gating (already covered, not re-derived here):** see
`research_brain_confidence_weighted_learning_consolidation_2026-07-20.md` for the full four-mechanism stack
(Yu & Dayan 2005 neuromodulator precision-weighting; Kepecs/Lak 2008/2014 self-generated decision confidence,
double-dissociation from OFC; Lisman & Grace 2005 hippocampal-VTA salience-gated LTP; Ackerman et al.
metacognitive miscalibration as the load-bearing failure mode). Deflated P for the general principle: 0.80
(that note's number, reused verbatim — not re-derived).

**What is NEW here — multi-ROUND / repeated-exposure dynamics (the layer none of the same-day notes covered):**

1. **Testing effect / retrieval practice across repeated rounds** (Roediger & Karpicke 2006, *Psychological
   Science*, canonical; Karpicke & Roediger 2008, *Science*; Pyc & Rawson 2009 on effortful retrieval) — repeated
   retrieval-and-correct cycles produce genuine long-term gains that CLIMB across sessions, and the size of the
   benefit is larger for items retrieved with initially low confidence and then corrected than for
   already-known items (the "desirable difficulties" framing, Bjork & Bjork 2011) — a direct multi-round analog
   of "gate the update strength by how uncertain the item was."
2. **Spacing effect across multiple sessions** (Cepeda et al. 2006, *Psychological Bulletin*, large
   meta-analysis) — the multi-session (not single-encoding) dynamic is a separate, well-replicated literature
   from single-event consolidation; benefit compounds with session count up to a point, then diminishes —
   evidence that "more rounds" is not automatically monotonic and needs its own curve-shape prediction (rounds
   help, but likely with diminishing returns, not unbounded linear climb).
3. **Reconsolidation-UPDATE FAILURE across repeated retrieval** (Nader, Schafe & LeDoux 2000, *Nature*,
   canonical — retrieval makes a memory transiently labile and re-writable; Hardt, Einarsson & Nader 2010,
   *Annu Rev Psychol*, review) — this is the direct biological mechanism for "self-correction across rounds can
   make things WORSE": each retrieval-and-revise event is a genuine overwrite opportunity, and if the
   correcting signal is wrong or noisy, the ERROR gets written back into long-term storage, entrenching rather
   than fixing it — repeated across rounds, this compounds.
4. **Repetition-strengthened illusory truth / belief entrenchment** (Hasher, Goldstein & Toppino 1977, canonical
   *JVLVB*; Fazio, Brashier, Payne & Marsh 2015, *JEP:General* — repetition increases perceived truth even for
   statements the person KNOWS are false at baseline) — the human failure mode most directly analogous to
   "confirmation bias compounding over self-correction rounds": each additional exposure to a self-generated
   (possibly wrong) revision increases its felt reliability independent of whether it is actually correct. This
   is the biological grounding for why the must-fail control below must specifically test CROSS-ROUND
   divergence, not just a single bad-source injection.
5. **Jointly-adapting confidence + learning-rate across trials** — thin in the literature. Behrens et al. (2007)
   and the Hierarchical Gaussian Filter (Mathys et al. 2011/2014) formalize learning-rate-as-precision-ratio,
   but a live system where the confidence estimate ITSELF is being updated over the same rounds it is gating is
   not a well-trodden experimental paradigm (mostly single-parameter Bayesian filtering theory, not multi-round
   confidence-of-confidence dynamics). Flag as a genuine, small, open corner — not blocking, but do not oversell
   this piece as "brain-proven."

**Bottom line for (a):** the brain shows both directions cleanly — REAL, replicated multi-round improvement
(testing effect, spacing effect) when retrieval-correction is accurate, and REAL, replicated multi-round harm
(reconsolidation-update-failure, repetition-strengthened illusory truth) when the correcting signal is wrong or
overweighted. This is exactly the shape the design below needs: a genuine can-fail axis in BOTH directions, not
just "more rounds = more better."

---

## (b) PRIOR ART — the genuinely new ML layer (multi-round dynamics)

Same dedup principle: single-step confidence-thresholded pseudo-labeling and self-training are well-trodden and
NOT re-derived here (Lee 2013 pseudo-label; Sohn et al. 2020 FixMatch are standard background). The NEW layer
is what happens ACROSS rounds:

- **Confirmation bias / error amplification across rounds** (Arazo et al. 2020, IJCNN, canonical for this
  specific claim): a model overfits to its own wrong pseudo-labels and the bias reinforces round-over-round,
  producing early saturation or reversal rather than a clean climb — the direct ML analog of Hasher/Fazio
  repetition-strengthened error above.
- **Calibration quality gates whether rounds help or hurt** (Rizve et al. 2021, ICLR, "In Defense of
  Pseudo-Labeling"/UPS): high-confidence-but-WRONG predictions from a miscalibrated model are the dominant
  driver of round-over-round noise accumulation — i.e. it is not "gate vs no gate" alone but "well-calibrated
  gate vs poorly-calibrated gate" that determines curve shape. Directly informative for the design: our gate's
  own reliability-score AUC (per the 29376 lineage, must be materially <1.0 and >0.55) should be checked for
  degradation across rounds too, not just at round 0.
- **Zou et al. 2019 (ICCV) confidence-regularized self-training** and **Kumar, Ma & Liang 2020 (ICML) gradual
  domain adaptation**: self-training accuracy climbs monotonically across rounds ONLY under conditions of
  small, well-matched per-round shift/confidence quality; large or noisy per-round updates cause sharp
  divergence — again a conditional, not automatic, prediction.
- **Model collapse / self-consuming loops** (Shumailov et al. 2023/2024, *Nature*, "Curse of Recursion";
  Self-Improving Transformers 2025, arXiv:2502.01612, naming an explicit **"error avalanche"**: errors in
  self-generated training data compound round-over-round toward eventual collapse absent filtering) — the
  clean, citable ML analog of the ungated/inverted-confidence must-fail arm. This literature is usually framed
  for generative models but the underlying mechanism (uncorrected self-consumption erodes distributional tails
  / entrenches the model's own biases across generations) is the correct mental model for what an UNGATED
  multi-round self-correction loop should do if the failure mode is real.
- **Gap explicitly flagged by the lit-scan sub-agent:** no single canonical paper runs the EXACT controlled
  comparison (identical loop, gate on vs off, full accuracy-by-round trajectory reported for both arms) as one
  study. The supporting evidence is triangulated across separate ablations (Kumar et al. "without confidence
  thresholding, all methods do worse"; Rizve et al. UPS ablations; the error-avalanche framing). This is
  honestly the same gap our own substrate has — which is exactly why the cell below is worth running: it would
  be a genuinely novel controlled instance of a comparison the field has only triangulated indirectly.

**Failure modes that justify the must-fail gate (explicit, credited):** confirmation bias / error amplification
(Arazo 2020), calibration-dependence (Rizve 2021 UPS), and error-avalanche/model-collapse (Shumailov 2023,
Self-Improving Transformers 2025) all converge on the same prediction: an UNGATED or miscalibrated multi-round
self-correction loop should show FLAT-then-DEGRADING accuracy with a gap to the gated arm that WIDENS as rounds
accumulate — not just a one-time hit. This is a stronger, round-count-dependent signature than the single-step
"ungated hurts on bad source" result 29386/89 already proved, and is the design's core new must-fail test.

Raw ML sub-agent P-estimate (un-deflated): 0.62 that a well-designed gated-vs-ungated multi-round trajectory
comparison shows the predicted divergence — "literature-consistent-but-not-directly-proven as a single result
type," per the sub-agent's own honest flag above.

---

## (c) DEDUP VERDICT — is the learning curve genuinely novel vs 29386/89?

**Yes, genuinely novel, narrower than the task brief initially framed it.** Specifically:

| Already covered (do NOT re-test) | Genuinely open (this cell's target) |
|---|---|
| Loop wiring: gap-detect -> internal-retrieve -> external-lookup -> gate -> revise (29386/89, VET-confirmed) | Wrapping that SAME wiring in an outer ROUND loop and logging accuracy at each round |
| Binary reliability gate, load-bearing (ungated corrupts model 0.417->0.000 per task context) | A CONTINUOUS confidence-modulated per-item RATE (not accept/reject) that persists and compounds across rounds |
| Continuous confidence-weighted rate for a SINGLE corpus-build pass (STEP1 codebook, `research_brain_confidence_weighted_learning_consolidation_2026-07-20.md`) | The SAME rate concept applied to the reader's OWN logged errors, iterated over 3-5+ rounds |
| Single-step "ungated-lookup-can-hurt" must-fail control (bad-source injection, one pass) | A must-fail control that specifically targets CROSS-ROUND divergence — the gated-vs-ungated GAP must WIDEN with round count, not just appear once |
| `band10_learning_curve` = occ1-vs-occ2 delta (repeated-MENTION transfer within one pass) | A true accuracy-vs-round-number CURVE across independent self-correction rounds |

The task brief's instinct that this MIGHT already be covered by 29386/89 was reasonable but not correct on
inspection of the actual cell code (`exp_active_learning_loop_gap_detect_lookup_revise_v2.py` lines 1056,
1155): `band10_learning_curve` is a two-point within-pass metric, not a multi-round trajectory, and the gate in
both v1 and v2 is binary (`accept = coherent and rel_score >= RELIABILITY_THRESHOLD`), not a continuous rate.
Both fixes are additive to the existing machinery, not replacements — this keeps the cell cheap (see below).

---

## Cheap decisive test

Reuse the ENTIRE `exp_active_learning_loop_gap_detect_lookup_revise_v2.py` machinery (calibration pool, gap
gate, coherence check, provenance-revise) unchanged; wrap it in an outer round loop, 5 rounds, 3 seeds at
smoke / 7 at full (existing SEEDS/FULL_SEEDS convention). Each round: the reader's currently-flagged errors and
abstentions (from the metacog/abstain signal, 29367) form that round's correction batch; internal-retrieve-first
against the round's own accumulating codebook, then external-lookup as needed; the per-item ACCEPT decision
becomes a per-item continuous RATE = reliability_score (already computed, `derive_reliability_scores`) when
coherent, else 0 — replacing the current `>= RELIABILITY_THRESHOLD` binary cutoff with a smooth multiplier on
how strongly that item's revision is written into the codebook. Re-evaluate the SAME held-out eval set after
each round's revisions; log accuracy at rounds 0 (baseline, no revision) through 4.

**Arms** (one variable differs: the per-round rate function):
1. **GATED** — rate = reliability_score (continuous, coherence-gated at 0 if incoherent).
2. **UNGATED** — rate = 1.0 always (accept every revision at full strength, regardless of coherence/reliability).
3. **RANDOM-CONFIDENCE** — rate = reliability_score with per-item scores SHUFFLED before use (construction-
   matched null: same score distribution, decoupled from which item it applies to).
4. **INVERTED-CONFIDENCE** — rate = 1 - reliability_score (deliberately prioritize the least-reliable items —
   the adversarial arm, directly operationalizing the Ackerman/Fazio miscalibration-entrenchment failure mode).
5. **PASSIVE** — no revision at any round, flat reference baseline.

Cheap because: no new model, no new corpus, no new gate math — the only new code is the outer round loop, the
binary-to-continuous rate substitution (a one-line change to the existing accept logic), and per-round
accuracy logging. Design-gate per the standing discipline: confirm at 2-round smoke that (i) the 5 arms
genuinely diverge by round 2 (not identical by construction), (ii) the eval set has enough genuinely-fixable
items (not already-saturated) for a curve to be visible at all, (iii) baseline PASSIVE round-0 accuracy is not
already at ceiling.

---

## Falsifiable predictions

**HARD-PASS** (all of the following, pre-registered, >=3 seeds at full scale):
- GATED arm's accuracy trajectory has a clearly positive slope across rounds 0-4 (recommend >=+0.01
  accuracy/round or round-4 minus round-0 >= 5 percentage points, consistent with the nontrivial single-step
  gain already shown in 29386/89) with monotone-or-near-monotone shape and consistent sign across seeds.
- UNGATED arm's trajectory is flat-or-negative (round-4 <= round-0 within noise) — the load-bearing "gate
  matters across rounds too" signature.
- RANDOM-CONFIDENCE collapses toward UNGATED, not toward GATED (rules out "any nonzero partial rate helps"
  as a confound — mirrors the shuffled-confidence control already validated in the sibling consolidation note).
- INVERTED-CONFIDENCE underperforms both GATED and PASSIVE by round 4 (cleanest evidence the rate's sign, not
  just its existence, is what matters).
- **The GATED-vs-UNGATED gap WIDENS with round number** — this is the genuinely new claim beyond the existing
  single-step result: the divergence should visibly grow round-over-round (a compounding, not one-time,
  signature), matching the confirmation-bias/error-avalanche prediction from (b).

**HARD-FAIL** (any one kills or sharply limits the candidate):
- GATED arm's trajectory is flat within noise across all 5 rounds — the SINGLE MOST LIKELY outcome given the
  task's own framing that the residual may be extraction-bound: if most of the reader's logged errors are
  wrong-span/wrong-argument EXTRACTION misses rather than wrong-role DECISION misses, decision-level
  self-correction has nothing to operate on (it cannot invent extraction the parser never produced). Mandatory
  design mitigation, not an afterthought: partition the round-0 error log into EXTRACTION-class vs
  DECISION-class using the already-existing parser arc-margin (AUC 0.807) and completeness signal BEFORE
  running any rounds, and report the two curves SEPARATELY. A flat EXTRACTION-class curve alongside a real,
  climbing DECISION-class curve is not a failure of this cell — it is the correctly-localized, informative
  result the task brief asked for ("target the drill honestly").
- GATED arm degrades over rounds (real miscalibration-entrenchment, not just in the adversarial control) —
  itself a genuine, useful negative, directly predicted as POSSIBLE (not surprising) by the
  reconsolidation-update-failure and illusory-truth-repetition literature in (a).
- UNGATED trajectory is statistically indistinguishable from GATED's (gate doesn't matter across rounds
  either) — construction/no-signal kill.
- Fewer than ~15-20% of round-0 logged errors are resolvable via internal-retrieve or external-lookup at all
  (most are hard extraction misses with no lookup-recoverable content) — a distributional precondition-gate
  failure; kill before spending compute on the full 5-round run, per the standing design-gate discipline.

---

## Cross-thread synthesis

This drill sits at the convergence point of five same-arc threads and should be read as extending, not
duplicating, each: **metacognition/abstain** (29367, committed-precision 0.882->0.950 @16% abstain — supplies
the per-round error/abstain batch and the reliability score used for the continuous rate); **parser
arc-margin** (AUC 0.807) and **completeness signal** (used here for the mandatory extraction-vs-decision
partition, not previously used this way); **the active-learning loop** (29386/89 — wiring and binary gate
reused verbatim, extended to continuous rate + outer round loop); **confidence-weighted consolidation**
(`research_brain_confidence_weighted_learning_consolidation_2026-07-20.md` — the continuous-rate design
pattern and its must-fail controls, i.e. shuffled/inverted/oracle-ceiling arms, directly reused and extended
from single-pass to multi-round); **the active-loop biology drill**
(`research_brain_active_learning_curiosity_lookup_revision_2026-07-20.md` — the gap-detect/retrieve/lookup
mechanism, reused as the per-round content). It is explicitly NOT the same target as
`exp_dev_handoff_research_compounding_learning_schema_gated_consolidation_2026-07-18.md`'s reconsolidation
thread — that hand-off targets corpus-scale schema-fit reallocation and reactivation-triggered reconsolidation
of the shared STEP1 codebook; this drill targets the READER's own per-item error log across discrete
self-correction rounds. Related in spirit (both are "revisit and possibly overwrite, gated by a fitness
signal"), but different target, different held-out metric, different literature anchor — should stay separate
threads, not be merged, per the same dedup discipline this note itself applied to 29386/89.

Given this composes THREE already-separately-validated pieces (metacog signal + binary gate + loop wiring)
into a strictly HARDER bar (continuous rate, persisting and compounding across multiple rounds, an AND-gate
across 5 falsifiable arms rather than 2-3), and the sibling single-step composition drill
(`research_brain_confidence_weighted_learning_consolidation_2026-07-20.md`) already set P=0.35 for an easier
version of this same kind of claim while flagging the arc's repeated pattern of guardrail-caught over-reads on
hopeful composition claims — this note's P_deflated is set BELOW that sibling's, at 0.28, reflecting genuine
skepticism that the full 5-arm HARD-PASS lands cleanly, not false modesty. The informative-either-way framing
(extraction-vs-decision partition) is what keeps this a good bet despite the low HARD-PASS P: P that the drill
produces a USEFUL, correctly-localized result (whether or not the curve itself passes) is much higher, ~0.75.

---

## Substrate-product implications

If GATED HARD-PASSES with the widening-gap signature: the product gets a genuine, demonstrable "gets better
the more it corrects itself, and knows how hard to lean on each correction" capability — a stronger and more
visible claim than either sibling piece alone (a confidence signal that merely flags uncertainty, or a gate
that merely accepts/rejects once), built entirely from already-existing, already-VET-positive components
recombined, not new research. If it HARD-FAILS via the extraction-bound path: the drill still delivers real
product value by cleanly separating "the reader's residual is unfixable by decision-level self-correction"
(extraction-class, flat) from "the reader's residual IS fixable by decision-level self-correction, and now we
know the rate schedule that works" (decision-class, climbing) — this directly informs whether future product
effort should go toward the parser/extraction layer (a different, larger engineering problem) or toward
scaling this self-correction mechanism (a comparatively cheap win). Either outcome moves the roadmap forward;
this is a genuine can-fail test, not a demonstration, consistent with the design-gate discipline.

---

## Citations (verified count: 21 unique across both lit-scan sub-agents + this note's brain recap; deduped
against the 16 already cited in `research_brain_confidence_weighted_learning_consolidation_2026-07-20.md`)

**Brain / multi-round (new to this note, 8):**
1. Roediger, H.L. & Karpicke, J.D. (2006). Test-enhanced learning. *Psychological Science*. Canonical.
2. Karpicke, J.D. & Roediger, H.L. (2008). The critical importance of retrieval for learning. *Science*.
   Canonical.
3. Pyc, M.A. & Rawson, K.A. (2009). Testing the retrieval effort hypothesis. *J. Memory & Language*.
4. Bjork, R.A. & Bjork, E.L. (2011). Making things hard on yourself, but in a good way: desirable difficulties.
   Standard framework reference.
5. Cepeda, N.J. et al. (2006). Distributed practice in verbal recall tasks: a review and quantitative
   synthesis. *Psychological Bulletin*. Canonical meta-analysis.
6. Nader, K., Schafe, G.E. & LeDoux, J.E. (2000). Fear memories require protein synthesis in the amygdala for
   reconsolidation after retrieval. *Nature*. Canonical (reconsolidation).
7. Hardt, O., Einarsson, E.O. & Nader, K. (2010). A bridge over troubled water: reconsolidation as a link
   between cognitive and neuroscientific memory research traditions. *Annu Rev Psychol*. Review.
8. Hasher, L., Goldstein, D. & Toppino, T. (1977). Frequency and the conference of referential validity.
   *J. Verbal Learning & Verbal Behavior*. Canonical (illusory truth).
9. Fazio, L.K., Brashier, N.M., Payne, B.K. & Marsh, E.J. (2015). Knowledge does not protect against illusory
   truth. *J. Experimental Psychology: General*. Highly cited, repetition-strengthens-even-known-false result.

**ML / multi-round self-training (13, via sub-agent, cross-checked):**
10. Scudder, H. (1965). Probability of error of some adaptive pattern-recognition machines. *IEEE Trans.
    Info Theory*. Historical root.
11. Yarowsky, D. (1995). Unsupervised word sense disambiguation rivaling supervised methods. *ACL*. Historical
    root (bootstrapping/self-training).
12. Lee, D.-H. (2013). Pseudo-label: the simple and efficient semi-supervised learning method. *ICML
    Workshop*. Standard background.
13. Xie, Q. et al. (2020). Self-training with Noisy Student improves ImageNet classification. *CVPR*.
    Canonical, iterative teacher-student.
14. Sohn, K. et al. (2020). FixMatch: simplifying semi-supervised learning with consistency and confidence.
    *NeurIPS*. Standard background.
15. Wei, C., Shen, K., Chen, Y. & Ma, T. (2021). Theoretical analysis of self-training with deep networks on
    unlabeled data. *ICLR*. Convergence theory, assumption-dependent.
16. Kumar, A., Ma, T. & Liang, P. (2020). Understanding self-training for gradual domain adaptation. *ICML*.
    Monotone-climb-under-small-shift result, direct evidence for round-dynamics conditionality.
17. Arazo, E. et al. (2020). Pseudo-labeling and confirmation bias in deep semi-supervised learning. *IJCNN*.
    Canonical for round-over-round bias reinforcement.
18. Zou, Y. et al. (2019). Confidence regularized self-training. *ICCV* (Oral). Canonical for
    continuous/soft-label treatment countering divergence.
19. Rizve, M.N. et al. (2021). In defense of pseudo-labeling: an uncertainty-aware pseudo-label selection
    framework (UPS). *ICLR*. Calibration-quality-gates-round-outcome result.
20. Shumailov, I. et al. (2023/2024). The curse of recursion / AI models collapse when trained on recursively
    generated data. *arXiv:2305.17493* / *Nature* (2024). Model-collapse mechanism, ungated-loop analog.
21. Self-Improving Transformers (2025). *arXiv:2502.01612*. "Error avalanche" — explicit round-over-round
    compounding-error framing for discrete-task self-training, closest direct analog found.

Also consulted, no new citation but explicitly checked: Settles, B. (2009) active-learning survey
(uncertainty sampling background, standard reference, not re-cited above); Behrens et al. (2007) and Mathys et
al. (2011/2014) (already cited in the sibling consolidation note, reused not re-cited here).

Flag: sub-agent explicitly could not find a single canonical paper running the EXACT gated-vs-ungated
multi-round trajectory comparison as one controlled study — the supporting evidence is triangulated across
separate ablations (Kumar et al., Rizve et al., error-avalanche framing). Treat the composite prediction as
literature-consistent, not literature-proven; this is precisely why the cell is worth running.
