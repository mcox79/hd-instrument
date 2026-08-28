---
problem: coreference_is_capped_at_065_on_real_narrative
status: SOLVED
bar: "PASSES with EITHER track, ALL of its items. Track A (raise accuracy): a graded cue-based-retrieval resolver beats the incumbent ~0.65 CI-separated on REAL narrative (LitBank gold, held-out), recompute the incumbent floor on the SAME population; an info-free twin (shuffled cue activations / random-antecedent) LOSES CI-separated; report CI half-width + null p95; a positive control that the metric moves. Track B (legible uncertainty): an entropy/margin ABSTAIN flag on the retrieval posterior such that, on the KEPT subset, accuracy is CI-separated-higher than the un-gated resolver on the same items, the abstain rate is < a stated cap (not 'abstain on everything'), and a DOWNSTREAM organ measurably degrades GRACEFULLY when fed the flag vs silently inheriting the wrong link; info-free twin (random abstain) LOSES. A rigorous NEGATIVE is a full pass (Track B alone passes)."
result: "Track A PASSES. LitBank, 100 novels, 50 held-out, competitive pronoun-antecedent subset (>=2 gn-compatible prior gold entities, n=4693 TEST decisions), scorer = link-level argmax==gold: brain-faithful GRADED cue-based retrieval 0.7752 [0.7313,0.8176] vs the INCUMBENT hard-tiered strict-Cb pick recomputed on the SAME population 0.6030 [0.5449,0.6544]; delta +0.1722 [0.1415,0.2032], half-width 0.031, null-p95 0.031, band ABOVE. Positive control: graded fixes 1073 incumbent errors, breaks 265 (net +808). Track B PASSES items a,b,d: posterior entropy (softmax gain=8 tuned on DEV for calibration -- gain-invariant for argmax, so Track A untouched) predicts its own errors AUC 0.806 vs the incumbent's own margin signal 0.617 recomputed on the SAME population (apples-to-apples); deferring the highest-entropy 33.0% lifts kept-subset accuracy 0.7752->0.8935, delta +0.118 CI-sep, random-abstain twin flat 0.7751. Track B item c NOT met on the tested downstream (mapped as an adjacency)."
floor: "Incumbent strict-Cb tiered pick (hdlab _pick_strict_cb) recomputed in-place on LitBank held-out = 0.6030 [0.5449,0.6544] -- the floor the bar names; graded lo 0.7313 > floor hi 0.6544 (CI-separated over the floor's upper bound). Additional floors run same-population: recency 0.7172, ACT-R base-level activation (d=2.0) 0.7824. HONEST: graded TIES ACT-R (delta -0.0072, NOT_SEP) -- graded_competition's MAP-optimality theorem forbids beating the argmax of the same net; the win is over the incumbent's hard TIER, not the best point estimate."
controls: "(1) info-free twin random-antecedent -> 0.0548, LOSES CI-sep (excludes 'any linking helps'). (2) info-free twin shuffled-cue-supports -> 0.0435, LOSES CI-sep (excludes 'the cue geometry not identities carries it'). (3) random-abstain twin at matched rate -> kept 0.7751 = full 0.7752 (excludes 'deferring anything raises kept acc'; the entropy flag is informative). (4) recency 0.7172 and ACT-R 0.7824 floors recomputed same-population (excludes floor cherry-picking; graded's win is over the TIER, ties the strongest arm). (5) DEV/TEST split by document, weights tuned on 50 DEV novels, all headlines on the disjoint 50 TEST novels (excludes tuning-to-gold). (6) parallelism-cue ablation: Smyth-1994 parallelism as a 6th cue -> DEV weight 0.0 (excludes 'a stronger structural cue was left out'). (7) agreement/animacy-filter ablation (exp_coref_agreement_animacy_filter_v1): adding NLTK name-gender gazetteer + animacy pruning to the PINNED agreement filter shrinks the mean candidate pool only 39.9->39.3 and moves graded accuracy 0.7752->0.7774 (null) -- excludes 'a leaky agreement filter is the cap'; the pool TAIL does not bind, the structurally-salient competitors do."
files_changed: "experiments/exp_coref_graded_cue_retrieval_litbank_v1.py, experiments/exp_coref_abstain_downstream_whodidwhat_v1.py, experiments/exp_coref_agreement_animacy_filter_v1.py, verification/test_coref_graded_cue_retrieval.py, notes/problems/coreference_is_capped_at_065_on_real_narrative/SOLVED.md. No hdlab/ write (Q111); proposed hdlab diff below."
reverify: ".venv/Scripts/python.exe verification/test_coref_graded_cue_retrieval.py"
---

# What was built and measured

The reader resolves a pronoun's antecedent with a **hard, tiered rule** (`hdlab/coreference_resolver._pick_strict_cb`:
pick the candidate holding the most-recent grammatical-subject clause, ties broken by recency) and emits only a coarse
*integer* confidence margin. This SOLVER replaced the tiered pick with the brain's actual computation for reference --
**graded cue-based retrieval** (Lewis & Vasishth 2005; McElree 2003): candidate antecedents compete via a weighted sum
of graded cue activations, read out by a softmax = the Bayesian/FLMP posterior -- reusing the landed
`hdlab.graded_competition` organ verbatim, over the pinned ACT-R base-level activation (recency x frequency x role).

**Population (disk-grounded, real narrative).** LitBank, 100 annotated novels (Bamman et al. 2020), the pre-parsed
cache at `data/litbank/who_did_what_events.json` (spaCy roles/gov-verbs + gold coref). The task is the audit's named
"real open case": **competitive antecedent resolution among 2+ plausible referents** -- every 3rd-person pronoun whose
gold entity was introduced earlier and that has >=2 gender/number-compatible prior gold entities. Split DEV/TEST by
document; weights tuned on DEV, all headlines on the 50 held-out TEST novels. (The brief's "~0.65" is a McGuffey
identity-query figure; on raw LitBank prose the competitive subset is harder and the incumbent's tier is worse -- see
AUDIT UPDATE.)

**Track A result (n=4693 TEST decisions):**

| resolver | accuracy [95% CI] | note |
|---|---|---|
| incumbent hard-tiered strict-Cb (recomputed floor) | 0.603 [0.545, 0.654] | **the measured cap** |
| plain recency | 0.717 [0.661, 0.762] | beats the incumbent tier |
| **graded cue-based retrieval (ours)** | **0.775 [0.731, 0.818]** | +0.172 over incumbent, CI-sep |
| ACT-R base-level activation | 0.782 [0.738, 0.824] | graded ties it (MAP theorem) |
| random-antecedent twin / shuffled-cue twin | 0.055 / 0.044 | info-free, lose by +0.72 |

Graded beats the incumbent **+0.172 [0.142, 0.203]**, half-width 0.031, null-p95 0.031. **The mechanistic cause of the
cap is now measured and surprising: the incumbent's rigid subject-first tier scores BELOW plain recency (-0.114
CI-sep)** -- it over-commits to the last grammatical subject even when the referent is a less salient entity. Replacing
the tier with graded retrieval fixes it.

**Track B result (same cell):** the posterior's normalized entropy predicts the resolver's OWN errors gold-free at
**AUC 0.806** (the landed pronoun confidence signal, `exp_coref_self_confidence_calibration_v2`, reached only 0.627 for
pronouns). Deferring the highest-entropy **33.0%** raises kept-subset accuracy **0.775 -> 0.894**, CI-sep; a
random-abstain twin at the same rate is flat (0.775). So the entropy flag is a calibrated, first-class "defer" signal --
the brain-faithful "when cues conflict the posterior is flat -> defer" (Levy 2008; Swets et al. 2008; Van Dyke & McElree
2006 similarity-based interference), and the brain's own "hold both" signature (the Nref ERP; Nieuwland & Van Berkum
2008). The softmax GAIN is the calibration lever: it is gain-invariant for argmax (Track A untouched), and tuning it on
DEV (gain=8) sharpens the posterior so entropy is a better error predictor (AUC 0.771 -> 0.806, kept 0.866 -> 0.894).

**OPTIMIZATION LEVERS TESTED (owner: "is there more to optimize?").** Beyond the pinned ACT-R activation + a light
subjecthood term, every additional STRUCTURAL lever I could build glass-box was tested and is a clean NEGATIVE on
accuracy: (i) parallelism (Smyth 1994) -> DEV weight 0.0; (ii) backward-center / first-mention / frequency cues -> all
weight ~0; (iii) a faithful agreement+animacy pre-filter (NLTK name-gender gazetteer + animacy pruning) -> mean pool
39.9->39.3, accuracy null (the pool TAIL does not bind; the structurally-salient competitors do); (iv) a lexical
implicit-causality cue -> the decisive frame is ~absent in real prose (landed cell, n=0). The ONE lever that paid off
was the Track-B calibration gain (above). Conclusion: the ~0.78 accuracy ceiling for a STRUCTURAL glass-box resolver on
real narrative is real and now DEMONSTRATED (not asserted); the only remaining accuracy lever is the coherence
next-mention PRIOR channel, a separate situation-model build (KEY REALIZATION 5, adjacency 1).

# What was NOT established (and what I would withdraw first)

1. **Graded does NOT beat the best point estimate.** It ties ACT-R base-level activation (-0.007, NOT_SEP) -- by
   `graded_competition`'s MAP-optimality theorem the graded argmax IS the argmax of the same net, so it cannot. **The
   accuracy win is over the incumbent's hard TIER, not over graded activation.** The unique value of the graded FORM is
   the calibrated DISTRIBUTION (Track B), not the point estimate. *If any part of this is wrong, withdraw first any
   implied claim that the graded posterior itself buys accuracy over ACT-R.*
2. **Track B item (c) -- a downstream organ degrading gracefully -- did NOT pass on the tested downstream.** Feeding the
   abstain flag to the landed who-did-what FHRR register decode does not move it (ABSTAIN 0.16 ~= COMMIT 0.17, and a
   direct/symbolic version is the same). Diagnosis (exp2): that task is bottlenecked by **name/entity clustering + FHRR
   register capacity (the fan effect: ORACLE coref reaches 0.62, the binder 0.17)**, NOT by the pronoun link -- so
   link-confidence cannot move it. This is a correctly-localized adjacency, not a Track-B failure of the flag itself
   (which works at the resolver's output, item a). Track A alone is a full pass of the bar.
3. **The ~0.78 ceiling is a real semantic gap (see KEY REALIZATION 5), not closed here.**

# KEY REALIZATIONS (the enabling moves)

1. **The incumbent's hard TIER, not "coref" writ large, is the cap -- and it is worse than recency on real prose.**
   Recomputing the incumbent's own pick rule in-place on LitBank (0.603 < recency 0.717) turned a vague "~0.65 cap" into
   a specific mechanism: a rigid most-recent-subject priority mis-ranks exactly when the referent is not a recent
   grammatical subject. Measuring the floor in-place was the move; the quoted 0.65 hid this. **The failure mechanism is
   now quantified:** on the 2012 cases where the tier is wrong and the graded activation is right, the tier picks
   entities a mean 3.42 sentences away vs the correct antecedent at 1.20 -- it grabs a subject 2.2 sentences STALER,
   because strict-Cb ranks by "most-recent-subject-sentence" with NO graded recency decay WITHIN the subject class. The
   graded ACT-R activation demotes stale entities via dt^-d. This is the copy-the-computation lesson made quantitative:
   the hard rule discarded the graded decay, and that decay is exactly what it needed. (Role-WEIGHTING, by contrast, is
   exhausted: uniform 0.783 ~= current 0.792 ~= Lappin-Leass-ish 0.793, within noise -- the decay, not the role weights,
   is the lever.)
2. **Reuse the pinned RETRIEVAL CURRENCY, don't hand-roll cues.** A first version blended separate z-scored Centering
   cues and LOST to ACT-R by -0.025. The fix was to make the graded net the softmax over the pinned Lewis-Vasishth/
   ACT-R base-level activation itself (recency x frequency x role) -- which IS the retrieval currency -- with the
   Centering cues as light additive terms. That recovered the point estimate (ties ACT-R) AND gave the calibrated
   posterior. The lesson: copy the brain's OPERATION (activation-sum -> softmax), sweep only the weights/decay.
3. **The MAP-optimality theorem sets the honest claim.** Knowing graded-argmax == discrete-argmax up front stopped me
   claims graded "beats" ACT-R; the real, defensible win is over the incumbent TIER plus the DISTRIBUTION.
4. **Entropy over the whole candidate set beats a top-2 margin for pronoun confidence.** The landed pronoun confidence
   was a top-2 strict-Cb integer margin (AUC 0.627). Normalized entropy of the full posterior reaches 0.771 -- exactly
   the "entropy/competitor-count, not top-two margin" fix an independent lit-scan on disk recommended.
5. **The residual ~19% is the brain's SECOND Bayesian term, which we do not compute.** Error anatomy: 19.4% of the
   graded arm's errors are STRUCTURALLY DOMINATED -- the gold antecedent is not most-recent, not max-subjecthood, not
   most-frequent, so NO structural cue points to it. The brain resolves these with the **coherence-driven next-mention
   PRIOR** P(referent) (Kehler & Rohde 2013's Bayes: P(referent|pronoun) prop P(pronoun|referent) x P(referent)),
   computed online from verb semantics + discourse-coherence expectations (Van Berkum et al. 2007 P600 at 400-700ms;
   Bott & Solstad 2014: IC bias is epiphenomenal of verb-semantic primitives, R^2=0.75). **Our glass-box resolver
   computes only the Centering LIKELIHOOD term (grammatical role/topichood); it is missing the coherence PRIOR entirely
   -- that is why it plateaus, and the plateau is the two-system boundary, not a tuning failure.**
6. **A lexical implicit-causality cue cannot reach the residual on real narrative.** The landed IC cell
   (`exp_read_discourse_coupling_revival_ic_verb_recency_v1`, MIDDLE_BAND) shows IC perfectly disambiguates constructed
   Garvey-Caramazza frames (ic_acc 1.0 vs recency 0.0) but the IC-decisive "NP1 VERB NP2 because PRON" frame occurs
   **n=0 times** in LitBank's ~200K tokens. So I did NOT rebuild an IC cue (avoiding a landed near-null); the residual
   needs the fuller coherence/situation-model channel, correctly scoped as a deeper build. And even that channel buys
   little in practice: a generalized selectional-preference feature added to a full coref system moved CoNLL F1 only
   +0.3 (Heinzerling, Moosavi & Strube 2017) -- do not over-promise the semantic channel.
7. **Part of the residual is GENUINELY IRREDUCIBLE ambiguity, and the abstain flag is the BRAIN'S OWN response to it.**
   On LitBank itself, ezCoref (Gupta et al. 2022) documents deliberate authorial indeterminacy (the Dickens "[fog]...
   where [it] flows" case) that careful annotators disagree on -- LitBank's gold resolves it by ANNOTATION-SCHEME FIAT
   (only ACE entity types markable), and its high headline agreement is partly that restriction hiding real ambiguity.
   So a slice of my structural residual is not a missing cue at all -- it is items with no unique answer. The brain's
   response to unresolved reference is NOT a silent commit: it is a distinct, sustained "hold both / defer" signature
   (the **Nref** ERP; Nieuwland & Van Berkum 2008, larger for weak context and high-span readers). **That is exactly
   what the Track B entropy flag does** -- so legible uncertainty is not a consolation prize, it is the brain-faithful
   output on the irreducible residual.

# AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

- **COREFERENCE / ENTITY TRACKING entry (~line 1188).** The entry says the organ is "RIGHT-OP-WRONG-METRIC: invented
  arithmetic over a pinned ordering ... competitive antecedent resolution among 2+ plausible referents remains the real
  open case." **MEASURED now on real narrative (LitBank, 100 novels, held-out competitive subset):** the incumbent's
  hard tiered pick = 0.603 (BELOW recency 0.717); brain-faithful graded cue-based retrieval (softmax over ACT-R
  activation, reusing `graded_competition`) = 0.775, **+0.172 CI-sep over the incumbent**, TIES ACT-R (MAP theorem).
- **REVERSES the 08-27 §2b finding** ("the cue-based-activation coref pick HARD_FAILED, -0.1348" and "resolving WHO a
  mention refers to is dominated by simple SALIENCE/RECENCY"). That HARD_FAIL was **population-specific** (QA-SRL /
  McGuffey: short, dense, few entities -- where the hard Centering tier and pure salience excel). On REAL narrative the
  graded ACT-R activation retrieval is the WINNER and the hard tier is the WORST arm. The right mechanism is
  population-dependent; the §2b successor ("entity-BINDING on a MODERN pronoun corpus") is now measured.
- **New PINNED sub-claim:** pronoun reference is a **two-term Bayesian computation** (Kehler & Rohde 2013): a Centering
  LIKELIHOOD (grammatical role/topichood -- what we compute) x a coherence-driven next-mention PRIOR (verb-semantics /
  discourse expectations -- what we do NOT compute). Our resolver is one of two terms; the ~19% structural residual is
  the prior-decisive cases. Entropy over the posterior is the pinned "flat -> defer" uncertainty currency (AUC 0.77).

# PROPOSED hdlab DIFF (strategy session lands it; Q111)

Add an **opt-in graded retrieval pick** to `hdlab/coreference_resolver.py` (default-off; existing behavior byte-identical):
`run_graded_retrieval(stream, gain=2.0, d=3.0, flag_thr=None)` whose PRONOUN branch, over the gn-compatible active
entities, computes the ACT-R base-level activation `A_i = ln(sum_k w_role(k)*dt_k^-d)`, then `graded_pick` (import
`hdlab.graded_competition`) -> argmax pick + normalized-entropy confidence; if `flag_thr` is set, ABSTAIN (assign None)
when entropy > flag_thr. This (a) beats the current `_pick_strict_cb` on real narrative by +0.17, and (b) replaces the
coarse integer strict-Cb margin with the entropy posterior (AUC 0.617 -> 0.806, same population) as the first-class abstain signal the
ToM cue / entity tracking / situation model consume. Keep the name/nominal branch untouched. Wire the entropy as the
same gold-free difficulty currency already used by `graded_competition` (one currency across consumers).

# ADJACENCIES MAPPED (candidate follow-on problems)

1. **The coherence next-mention PRIOR channel** (the residual's real fix) -- and it is SUBSTRATE-NATIVE, not a
   from-scratch build. The full Kehler & Rohde (2013) resolver is `P(referent|pronoun) ~ P(pronoun|referent) x
   P(referent)`: this SOLVER built the LIKELIHOOD term (the graded Centering/ACT-R retrieval). The missing PRIOR
   `P(referent)` is the next-mention expectation -- exactly what the substrate's PREDICTIVE-READER organ already
   computes (forward pre-activation; audit: "PREDICTING what an entity does next uses content-addressable retrieval").
   Concrete proposal: MULTIPLY the graded retrieval posterior by the predictive reader's next-entity expectation before
   argmax, and re-measure on the ~19% structurally-dominated residual. A lexical IC cue alone is insufficient (frame
   ~absent on real prose), and even a generic semantic-fit feature bought only +0.3 F1 in published systems (Heinzerling
   et al. 2017) -- so gate expectations, but this is the ONE remaining accuracy lever. Leverage: the structural residual.
   CAVEAT (raises the true ceiling): part of that residual is LitBank ANNOTATION-FIAT gold (ezCoref/Bleak House) where
   the reference is genuinely ambiguous -- so 0.775 UNDER-states true accuracy, and the movable fraction is smaller than
   19%.
2. **[FLAG TO STRATEGY -- HIGHEST-LEVERAGE ADJACENT TOOL] Name/entity clustering (the landed string-overlap name branch)
   is badly under-performing on real narrative, and it -- not the pronoun link -- is the who-did-what bottleneck.**
   MEASURED on LitBank 100 novels: **65.6% of multi-name gold entities are SHATTERED** (their name mentions split across
   >=2 predicted clusters), and 19.5% of predicted clusters MERGE >=2 gold entities (name-mention purity 0.819). Cause:
   the branch matches on a SINGLE head token, so "Elizabeth" / "Bennet" / "Lizzy" / "Miss Bennet" fragment into separate
   entities. Effect: a correctly-bound pronoun cannot retrieve its referent's events when the referent's identity is
   scattered -> the downstream decode sits at ~0.17 (COMMIT/ABSTAIN/RANDOM alike) vs ORACLE-coref 0.62 (exp2). Fix = a
   name-unification / nominal-alias pass (full-span match + honorific/surname handling). Leverage: caps the entire
   who-did-what + entity-tracking + situation-model stack. Candidate follow-on problem.
3. **[FLAG] The landed pronoun CONFIDENCE signal is weak -- shown APPLES-TO-APPLES.** The incumbent's own pronoun
   confidence (the strict-Cb integer margin) recomputed on THIS LitBank competitive population predicts its errors at
   AUC 0.617 (matching the 0.627 `exp_coref_self_confidence_calibration_v2` reported on its own harness). This SOLVER's
   calibrated posterior entropy reaches AUC 0.806 on the SAME population -- a drop-in replacement that comes FREE with
   the proposed graded resolver (not a separate build). Leverage: any organ that reads coref confidence (refuse gate,
   ToM defer, clarify gate). This flag is FIXED BY the same hdlab diff below, not a new problem.
4. **[FLAG] The LitBank mention cache (`data/litbank/who_did_what_events.json`) stores only a single HEAD TOKEN per
   mention.** This is what forces the name-clustering shatter (flag 2), blocks name-gender inference beyond single-token
   first names (the agreement-filter probe fired rarely for this reason), and blocks any semantic/selectional cue. Fix =
   extend the loader to carry full mention spans + the LitBank entity TYPE (PER/FAC/GPE/...). Leverage: unblocks flags
   2-3 and the coherence channel (adjacency 1).
5. **FHRR register capacity (the fan effect).** who-did-what decode collapses as competing-antecedent fan grows (prior
   cell: 1-3 cands 0.31 -> 17+ 0.16). The addressed-storage problem, orthogonal to coref, reconfirmed with
   coref-specific evidence. Leverage: any register-backed reader.
6. **[SUSPECTED, UNMEASURED] Grammatical-role assignment on archaic literary prose.** Both the incumbent tier and this
   resolver's subjecthood cue read spaCy `nsubj`->SUBJECT off 200-year-old long-sentence prose; parse noise there
   degrades the subjecthood signal for everyone. Not measured here (honest label); a role-accuracy spot-check on LitBank
   vs gold would size it. Leverage: the subjecthood cue + the incumbent tier.
7. **Downstream consumption of the abstain flag.** The ToM observation cue / "where is X" should be re-measured with the
   entropy flag once they are the LINK-bottlenecked consumer (they weren't in the who-did-what test). Leverage: graceful
   degradation across the reading stack.

---

## TLDR (plain language)

To follow a story you must track who each "he / she / they" points back to. The reader's current rule for this is rigid
-- it always reaches for the last person who was the sentence's subject. On 100 real novels, on the genuinely hard cases
(two or more people it could mean), that rigid rule gets about 60 out of 100 right -- worse than just guessing "the most
recently mentioned person" (72). I replaced it with the way the brain actually does this: let all the candidates compete
by how strongly memory brings each to mind, and take the strongest. That gets about 78 out of 100 -- a clear, solidly
measured jump, and scrambled/random versions of it collapse to near zero, so the gain is real. As a bonus, the method
also knows when it is unsure: when the candidates are close, it can say "I'm not confident" and hand back a flag. If it
declines to answer the least-confident third, the answers it DOES give rise to about 87 out of 100 -- and a version that
declines at random gets no such boost, so the "I'm unsure" signal is genuinely meaningful.

Two honest limits. First, this brain-faithful method does not beat a plain memory-strength score -- a theorem says it
can't; the real win is over the reader's OLD rigid rule, plus the new "I'm unsure" signal. Second, the ~22 out of 100 it
still misses are cases where NO structural clue points to the right person -- the brain uses meaning and world knowledge
there (a second, separate reasoning step we have not built), and I show a simple word-meaning shortcut cannot reach it on
real novels. So this fixes the rule and adds the confidence signal; the deeper meaning step is the mapped next problem.

## QUESTIONS
None -- Track A passes the bar cleanly; Track B passes the resolver-output items and I have mapped why the downstream
item did not (it is a different bottleneck). Awaiting your `owner_verdict: DONE`.

## NEXT STEPS
1. (Strategy) Re-verify the witness and land the opt-in `run_graded_retrieval` + entropy-abstain diff into
   `hdlab/coreference_resolver.py` (default-off).
2. (Strategy) Fold the AUDIT UPDATE into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (the coref entry + the §2b reversal).
3. (Follow-on problem) The coherence-driven next-mention PRIOR channel -- the residual's real fix -- as a
   situation-model build, not a resolver tweak.

---
INTEGRATED_BY_STRATEGY: 2026-08-28 (grade EXCELLENT; owner_verdict: DONE). Re-verified FIRST-HAND against the CURRENT
file (test_coref_graded_cue_retrieval.py, ALL 8 checks PASS -- ran it myself; the solver strengthened Track B between
submission and the DONE verdict, so I re-ran fresh rather than trust my earlier read). The ~0.65 coref cap is BROKEN +
DIAGNOSED on real narrative: the reader's rigid hard-tiered pronoun pick (_pick_strict_cb) is replaced by the brain's
graded cue-based retrieval (Lewis-Vasishth 2005 / McElree 2003 -- softmax over the pinned ACT-R base-level activation,
reusing the LANDED graded_competition organ). TRACK A PASSES: graded 0.775 [0.731,0.818] vs the incumbent hard-tier
recomputed on the SAME population 0.603 [0.545,0.654], +0.172 CI-sep (half-width 0.031, null-p95 0.031); info-free twins
collapse (0.055/0.044); positive control fixes 1073 / breaks 265. Cap mechanism MEASURED: the tier scores BELOW plain
recency (0.603<0.717) -- it picks subjects 2.2 sentences staler because strict-Cb lacks the brain's graded dt^-d decay.
TRACK B: entropy predicts its own errors AUC 0.806 vs the incumbent margin 0.617 SAME population (apples-to-apples);
deferring 33% lifts kept acc 0.775->0.894 CI-sep, random twin flat; gain-invariant for argmax (Track A untouched).
HONEST (volunteered): by the MAP-optimality theorem graded TIES ACT-R (0.782, NOT_SEP) -- the win is over the incumbent
TIER + the calibrated distribution, not the point estimate; optimization levers (parallelism, gender/animacy pre-filter
pool 39.9->39.3 null, lexical IC frame n=0, role-weighting) tested + REJECTED with numbers, so the ~0.78 structural
ceiling is demonstrated; the residual ~19% is the brain's 2nd Bayesian term (Kehler-Rohde coherence next-mention PRIOR),
a separate situation-model build. Track B item (c) NOT met on who-did-what -- correctly localized as name-clustering +
register-capacity bottlenecked (oracle-coref 0.62 vs 0.17), not link-bottlenecked; Track A alone is a full pass. Review
+ SOLVER REVIEW block in PROBLEM.md; priority cleared. AUDIT UPDATE folded (BRAIN_FOUNDATIONAL_AUDIT.md 2b, newest +
the coref entry): REVERSES the 08-27 coref cue-based-activation HARD_FAIL as POPULATION-SPECIFIC. hdlab landing QUEUED
(Q111 -- opt-in default-off run_graded_retrieval + entropy-abstain on coreference_resolver.py, existing behavior
byte-identical). NO hdlab written this commit (Q111). Top adjacency now MEASURED for a clean follow-on: name/entity
clustering shatters 65.6% of multi-name gold entities (single-head-token cache root cause) -> caps the whole
who-did-what/entity-tracking stack.
